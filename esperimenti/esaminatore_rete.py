# -*- coding: utf-8 -*-
"""Supporto di ia21 (modulo, non e' un esperimento): l'ESAMINATORE, la rete che impara a distinguere pagine vere da pagine scritte
dall'allievo.

Non e' il giudice A di ia01 (una rete che misura la "sorpresa" del testo e poi una regressione sul profilo di 14 numeri): e' un
lettore di pagina che impara direttamente "vera / scritta":
  - segni della pagina (gli stessi di ia01: glifi con frequenza almeno 0,1%, spazio, fine riga, segno di paragrafo, segno raro);
  - tre strati di convoluzione a finestre di 5 segni, dilatate 1, 2, 4 (ogni punto vede circa 29 segni, qualche parola), con somma al
    passo precedente; poi un solo strato di attenzione con due teste (la pagina puo' confrontare un punto con tutti gli altri: serve
    per vedere le parole che tornano); poi media e massimo nel tempo; poi un numero. E' volutamente di un'altra famiglia rispetto
    alla GRU dell'allievo e a quella del giudice A (e va molto piu' veloce sul processore di una GRU nei due versi).
  - circa 85.000 parametri; addestramento su finestre di al massimo 800 segni (a lotti di 8 vere e 8 scritte); valutazione sulla
    pagina intera. Arresto anticipato sull'AUC di validazione (pagine di fogli diversi da quelli dell'addestramento).
`addestra` con `cieco=True` mescola a caso le etichette (controllo negativo di ia21: l'esaminatore non sa niente).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import math
import os
import sys
import time
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import rifarlo_giudici as J  # noqa: E402

EMB, CANALI, TESTE, CADUTA = 32, 64, 2, 0.3
DILATAZIONI = (1, 2, 4)
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
BUDGET_VALUTAZIONE = 2.5e7        # lotti di valutazione: numero di pagine per lunghezza massima al quadrato


def costruisci(V, attenzione=True):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Esaminatore(nn.Module):
        def __init__(self):
            super().__init__()
            self.V = V
            self.emb = nn.Embedding(V + 1, EMB, padding_idx=V)
            self.proj = nn.Conv1d(EMB, CANALI, 1)
            self.convs = nn.ModuleList([nn.Conv1d(CANALI, CANALI, 5, padding=2 * d, dilation=d) for d in DILATAZIONI])
            self.norme = nn.ModuleList([nn.LayerNorm(CANALI) for _ in DILATAZIONI])
            self.att = nn.MultiheadAttention(CANALI, TESTE, batch_first=True) if attenzione else None
            self.ln = nn.LayerNorm(CANALI)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(2 * CANALI, 1)

        def forward(self, x, lung):
            T = x.shape[1]
            pad = torch.arange(T)[None, :] >= lung[:, None]
            vivo = (~pad).float()[:, None, :]
            h = self.proj(self.emb(x).transpose(1, 2)) * vivo
            for conv, ln in zip(self.convs, self.norme):
                h = h + F.gelu(conv(h))
                h = ln(h.transpose(1, 2)).transpose(1, 2) * vivo
            y = h.transpose(1, 2)
            if self.att is not None:
                a, _ = self.att(y, y, y, key_padding_mask=pad, need_weights=False)
                y = self.ln(y + a)
            else:
                y = self.ln(y)
            media = (y * (~pad).float()[:, :, None]).sum(1) / lung[:, None].float()
            massimo = y.masked_fill(pad[:, :, None], -1e9).max(1).values
            return self.out(self.caduta(torch.cat([media, massimo], 1)))[:, 0]

    return Esaminatore()


def _impacchetta(arrs, V):
    import torch
    L = max(len(a) for a in arrs)
    x = np.full((len(arrs), L), V, dtype=np.int64)
    for i, a in enumerate(arrs):
        x[i, :len(a)] = a
    return torch.from_numpy(x), torch.tensor([len(a) for a in arrs], dtype=torch.long)


def _ritaglia(a, lung, rng):
    if len(a) <= lung:
        return a
    s = int(rng.integers(0, len(a) - lung + 1))
    return a[s:s + lung]


def punteggi(m, arrs):
    """Punteggio (logit di 'scritta') di ogni pagina intera, nell'ordine dato."""
    import torch
    vecchio = m.training
    m.eval()
    out = np.zeros(len(arrs))
    ordine = sorted(range(len(arrs)), key=lambda i: len(arrs[i]))
    with torch.no_grad():
        i = 0
        while i < len(ordine):
            n = 1
            while i + n < len(ordine) and n < 16 and (n + 1) * len(arrs[ordine[i + n]]) ** 2 <= BUDGET_VALUTAZIONE:
                n += 1
            gruppo = ordine[i:i + n]
            x, l = _impacchetta([arrs[j] for j in gruppo], m.V)
            s = m(x, l).numpy()
            for j, v in zip(gruppo, s):
                out[j] = v
            i += n
    m.train(vecchio)
    return out


def auc(y, p):
    return J.auc_rango(y, p)


def auc_vere_finte(m, vere, finte):
    """AUC (finta = 1) dell'esaminatore su pagine vere e finte date; None se manca un gruppo."""
    if not vere or not finte:
        return None
    s = punteggi(m, list(vere) + list(finte))
    return float(auc([0] * len(vere) + [1] * len(finte), s))


def addestra(vere, finte_cur, finte_old, vere_val, finte_val, V, seme, cieco=False, epoche_max=25, pazienza=6, lung=800, per_lato=8,
             lr=LR, messaggio=None, attenzione=True):
    """Addestra un esaminatore nuovo. vere, finte_*: liste di vettori di numeri (una pagina ciascuno).
    Lotto: `per_lato` pagine vere e `per_lato` finte (meta' dalle finte del giro in corso `finte_cur`, meta' da quelle dei giri
    precedenti `finte_old`, se ci sono). Un'epoca = abbastanza lotti da passare una volta sulle pagine vere. Arresto: l'AUC sulla
    validazione (vere_val contro finte_val, pagine intere) non migliora da `pazienza` epoche; si tiene il modello migliore.
    cieco: tutte le pagine (vere e finte, anche di validazione) si mescolano e si dividono a caso in due gruppi: l'etichetta non vuol
    dire niente. Restituisce (modello, info)."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    inizio = time.time()
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    if cieco:
        tutte = list(vere) + list(finte_cur) + list(finte_old)
        rng.shuffle(tutte)
        h = len(tutte) // 2
        A, Bc, Bo = tutte[:h], tutte[h:], []
        tv = list(vere_val) + list(finte_val)
        rng.shuffle(tv)
        hv = len(tv) // 2
        VA, VB = tv[:hv], tv[hv:]
    else:
        A, Bc, Bo = list(vere), list(finte_cur), list(finte_old)
        VA, VB = list(vere_val), list(finte_val)
    if not A or not Bc:
        raise ValueError('esaminatore: mancano pagine da una delle due parti')
    m = costruisci(V, attenzione)
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=DECADIMENTO)
    n_lotti = max(4, int(math.ceil(len(A) / per_lato)))
    curva, perdite, migliore, stato = [], [], None, None
    for epoca in range(1, epoche_max + 1):
        tot = 0.0
        for _ in range(n_lotti):
            ia = rng.integers(0, len(A), size=per_lato)
            pagine = [_ritaglia(A[i], lung, rng) for i in ia]
            for _ in range(per_lato):
                src = Bo if (Bo and rng.random() < 0.5) else Bc
                pagine.append(_ritaglia(src[int(rng.integers(0, len(src)))], lung, rng))
            x, l = _impacchetta(pagine, V)
            y = torch.tensor([0.0] * per_lato + [1.0] * per_lato)
            loss = F.binary_cross_entropy_with_logits(m(x, l), y)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
            opt.step()
            tot += loss.item()
        perdite.append(round(tot / n_lotti, 4))
        v = auc_vere_finte(m, VA, VB) if (VA and VB) else None
        curva.append(None if v is None else round(v, 4))
        if v is not None and (migliore is None or v > migliore):
            migliore = v
            stato = {k: t.detach().clone() for k, t in m.state_dict().items()}
        if messaggio:
            messaggio('  esaminatore, epoca %d: perdita %.4f, AUC validazione %s, %.0f s' % (epoca, perdite[-1], curva[-1], time.time() - inizio))
        if v is not None:
            validi = [c for c in curva if c is not None]
            if len(validi) - 1 - validi.index(max(validi)) >= pazienza:
                break
    if stato is not None:
        m.load_state_dict(stato)
    validi = [c for c in curva if c is not None]
    scelta = (validi.index(max(validi)) + 1) if validi else len(perdite)
    m.eval()
    info = OrderedDict([('epoche', len(perdite)), ('epoca_scelta', scelta), ('AUC_validazione', migliore), ('curva_validazione', curva),
                        ('curva_perdita', perdite), ('pagine', [len(A), len(Bc), len(Bo)]), ('pagine_validazione', [len(VA), len(VB)]),
                        ('parametri', sum(p.numel() for p in m.parameters())), ('cieco', bool(cieco)), ('secondi', round(time.time() - inizio, 1))])
    return m, info
