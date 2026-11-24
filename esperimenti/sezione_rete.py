# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: la rete condizionata ("la rete che sa dove scrive") e la sua ablazione.

In parole semplici
- Il modello pieno di IA32/IA33 (GRU 2 x 256 di `gradini_modelli`, passo M1) legge gia' nel flusso dei segni le teste di pagina (`<pag>`, sezione, mano, lingua: quattro segni all'inizio
  della pagina) e le teste di riga (tipo di riga: inizio di paragrafo / meta' / fine / sola, posizione nella pagina, fascia di lunghezza: tre segni a ogni riga). Ma la sezione si legge
  UNA volta per pagina e la GRU la "dimentica" lungo la pagina; l'inizio di paragrafo si legge una volta per riga.
- Qui la stessa rete con il condizionamento **persistente**: a OGNI passo si danno in ingresso, concatenati al segno, gli indici (immersioni di 8 numeri) di sezione, mano, lingua, tipo di riga,
  posizione della riga, fascia di lunghezza e di una "posizione nella riga" a quattro valori (0 = si sta per scrivere il primo glifo della riga, 1 = altra testa, 2 = dentro la prima parola,
  3 = dopo); e all'uscita si aggiungono due **bias** appresi, uno per (sezione, lingua) e uno per (tipo di riga, posizione nella riga), sulla distribuzione dei segni (partono da zero).
  Niente di tutto questo e' un'informazione nuova: viene dagli stessi segni di testa, ricordati; e' un modo di fare in modo che la rete non li dimentichi.
- **Ablazione** (`cond=False`): la stessa classe, lo stesso seme, la stessa taglia, lo stesso addestramento, ma senza immersioni di condizionamento ne' bias: e' M1 con le sole teste nel flusso (come
  IA32). Serve a isolare l'effetto del condizionamento dal riaddestramento.
- L'addestramento e' quello di `rifare_dati.addestra_pieno` (copiato qui con la rete nuova): stesse pagine, stessa divisione dei fogli, lotti, AdamW, arresto sul minimo di validazione con pazienza
  `PAZIENZA32`, due istantanee (A = minimo di validazione, C = fine delle epoche in piu'), perplessita' (bit per segno) di validazione e **sui fogli tenuti fuori** riportate nel `pieno.json`.
- `PennaCond` scrive un segno alla volta con lo stesso calcolo della rete a tratti (provato in `sezione_prove`); `PienoCond` e' `rifare_dati.Pieno` per la rete nuova (istantanee mescolabili).
Nessun risultato e' scritto qui.
"""
import json
import math
import os
import sys
import time
from collections import OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import rifare_dati as RD  # noqa: E402

DC = 8
FAM = ('S:', 'M:', 'L:', 'T:', 'R:', 'N:')
SEME_RETE = int(os.environ.get('SEME_RETE35', 35001))
# la griglia (fissata prima di guardare qualunque numero del Voynich; decisa dopo una prova sul latino in cui la rete condizionata sovra-adattava):
# 'Ca' = quella originale (immersioni da 8, nessuna caduta); 'Cb' = immersioni da 4 e caduta 0,3 sull'ingresso di condizionamento;
# 'Cc' = immersioni da 8, caduta 0,5 e penalita' L2 (1e-3 x somma dei quadrati) sui due bias in uscita. Si sceglie sulla validazione.
VARIANTI = OrderedDict([('Ca', dict(dc=8, cond_drop=0.0, l2_bias=0.0)), ('Cb', dict(dc=4, cond_drop=0.3, l2_bias=0.0)), ('Cc', dict(dc=8, cond_drop=0.5, l2_bias=1e-3))])


class Info:
    """Le famiglie di segni di testa (sezione, mano, lingua, tipo di riga, posizione, fascia) nel vocabolario."""

    def __init__(self, voc):
        self.pag = voc['idx']['<pag>']
        self.SP = voc['primo_contenuto']
        self.EOL = self.SP + 1
        self.fam = {}
        self.n = [0] * len(FAM)
        for tid, s in enumerate(voc['segni']):
            for f, pre in enumerate(FAM):
                if s.startswith(pre):
                    self.fam[tid] = (f, self.n[f])
                    self.n[f] += 1
                    break


class StatoCond:
    """Gli indici di condizionamento a ogni passo, dallo stesso flusso di segni (per i dati e per la scrittura: una sola funzione)."""

    def __init__(self, info):
        self.info = info
        self.cur = list(info.n)                 # "nessuno" = n
        self.in1 = False

    def passo(self, tok):
        f = self.info.fam.get(tok)
        if f is not None:
            self.cur[f[0]] = f[1]
            if f[0] == len(FAM) - 1:
                self.in1 = True
                p = 0
            else:
                p = 1
        elif tok == self.info.pag:
            self.in1 = False
            p = 1
        elif tok == self.info.SP or tok == self.info.EOL:
            self.in1 = False
            p = 3
        else:
            p = 2 if self.in1 else 3
        return self.cur + [p]


def cond_da_tok(tok, info):
    """Gli indici (T, 7) di condizionamento di ogni posizione di una pagina (segni `tok`)."""
    sc = StatoCond(info)
    return np.array([sc.passo(int(t)) for t in tok], dtype=np.int64)


def costruisci_rete(cfg):
    import torch
    import torch.nn as nn

    class Rete(nn.Module):
        def __init__(self, cfg):
            super().__init__()
            self.cfg = dict(cfg)
            self.cond = bool(cfg['cond'])
            V, H = cfg['V'], cfg['nasc']
            self.H = H
            self.emb = nn.Embedding(V, cfg['emb'])
            din = cfg['emb']
            if self.cond:
                sz = cfg['sizes']
                dc = int(cfg.get('dc', DC))
                self.ce = nn.ModuleList([nn.Embedding(n + 1, dc) for n in sz] + [nn.Embedding(4, dc)])
                self.cdrop = nn.Dropout(float(cfg.get('cond_drop', 0.0)))
                self.l2_bias = float(cfg.get('l2_bias', 0.0))
                din += dc * (len(sz) + 1)
                self.b_sl = nn.Embedding((sz[0] + 1) * (sz[2] + 1), V)
                self.b_tp = nn.Embedding((sz[3] + 1) * 4, V)
                nn.init.zeros_(self.b_sl.weight)
                nn.init.zeros_(self.b_tp.weight)
            self.gru1 = nn.GRU(din, H, 1, batch_first=True)
            self.gru2 = nn.GRU(H, H, 1, batch_first=True)
            self.caduta = nn.Dropout(cfg['caduta'])
            self.out = nn.Linear(H, V)

        def ingresso(self, X, C):
            parti = [self.emb(X)]
            if self.cond:
                parti.append(self.cdrop(torch.cat([self.ce[i](C[..., i]) for i in range(len(self.ce))], -1)))
            return torch.cat(parti, -1)

        def bias(self, C):
            if not self.cond:
                return 0.0
            sz = self.cfg['sizes']
            return self.b_sl(C[..., 0] * (sz[2] + 1) + C[..., 2]) + self.b_tp(C[..., 3] * 4 + C[..., 6])

        def penalita(self):
            if not self.cond or self.l2_bias <= 0:
                return 0.0
            return self.l2_bias * (self.b_sl.weight.pow(2).sum() + self.b_tp.weight.pow(2).sum())

        def forward(self, X, C, h1=None, h2=None):
            y1, _ = self.gru1(self.ingresso(X, C), h1)
            u = self.caduta(y1)
            y2, _ = self.gru2(u, h2)
            hd = self.caduta(y2)
            return dict(logits=self.out(hd) + self.bias(C), y1=y1, y2=y2)

    return Rete(cfg)


def _stato_nuovo():
    return dict(h1=None, h2=None)


def passa_tratto35(m, ctx, righe, stati, addestra=False, opt=None):
    """Come `gradini_modelli.passa_tratto` per M1, con gli indici di condizionamento. `stati`: lista di dict(h1, h2). -> (somma -log P in nat, segni)."""
    import torch
    import torch.nn as nn
    bt = GM.lotto_tratto(righe, ctx, 1)
    X, Y, Mk = torch.as_tensor(bt['X']), torch.as_tensor(bt['Y']), torch.as_tensor(bt['Mk'])
    B, L = X.shape
    C = np.zeros((B, L, 7), np.int64)
    for b, (P, (a, c)) in enumerate(righe):
        C[b, :c - a] = P['C'][a:c]
    C = torch.as_tensor(C)
    H = m.H
    h1 = torch.stack([s['h1'] if s['h1'] is not None else torch.zeros(H) for s in stati])[None]
    h2 = torch.stack([s['h2'] if s['h2'] is not None else torch.zeros(H) for s in stati])[None]

    def nll(out):
        lp = torch.nn.functional.log_softmax(out['logits'], -1)
        tl = lp.gather(2, Y[..., None])[..., 0] * Mk
        return -tl.sum(), float(Mk.sum())
    if addestra:
        out = m(X, C, h1, h2)
        n_, ntok = nll(out)
        if ntok > 0:
            loss = n_ / ntok + m.penalita()
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), GM.TAGLIO)
            opt.step()
    else:
        with torch.no_grad():
            out = m(X, C, h1, h2)
            n_, ntok = nll(out)
    with torch.no_grad():
        for b, s in enumerate(stati):
            n = int(bt['lens'][b])
            s['h1'] = out['y1'][b, n - 1].detach().clone()
            s['h2'] = out['y2'][b, n - 1].detach().clone()
    return float(n_.detach()), ntok


def bpc35(m, ctx, pagine, lotto=16):
    """Bit per segno sulle pagine date (pagine intere a tratti con lo stato che passa)."""
    vecchio = m.training
    m.eval()
    tot = n = 0.0
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a:a + lotto]]
        stati = [_stato_nuovo() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            nl, nt = passa_tratto35(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att])
            tot += nl
            n += nt
            r += 1
    m.train(vecchio)
    return tot / max(n, 1.0) / math.log(2)


def _epoca35(m, ctx, add, opt, rng):
    perdita = conti = 0.0
    chiavi = [P['Tin'] * (1 + 0.3 * u) for P, u in zip(add, rng.uniform(size=len(add)))]
    ordine = sorted(range(len(add)), key=lambda i: chiavi[i])
    lotti = [ordine[a:a + GM.LOTTO] for a in range(0, len(ordine), GM.LOTTO)]
    rng.shuffle(lotti)
    for lotto in lotti:
        Ps = [add[i] for i in lotto]
        stati = [_stato_nuovo() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            nl, nt = passa_tratto35(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att], addestra=True, opt=opt)
            perdita += nl
            conti += nt
            r += 1
    return round(perdita / max(conti, 1) / math.log(2), 5)


def _pagine(fogli, ctx, info):
    pp = RD.pagine_per_modello(fogli, ctx)
    for P in pp:
        P['C'] = cond_da_tok(P['tok'], info)
    return pp


def addestra_pieno35(cartella, cond, seme=None, nasc=None, messaggi=None, var=None):
    """Addestra la rete (condizionata se `cond`, ablazione altrimenti) e salva `pieno.pt` (istantanee A e C) e `pieno.json` in `cartella`. Riprendibile: se `pieno.pt` c'e' non rifa niente.
    Stessi fogli, stesse epoche, stessa pazienza di `rifare_dati.addestra_pieno`."""
    import torch
    seme = SEME_RETE if seme is None else seme
    nasc = RD.NASC32 if nasc is None else nasc
    os.makedirs(cartella, exist_ok=True)
    pt, pj = os.path.join(cartella, 'pieno.pt'), os.path.join(cartella, 'pieno.json')
    if os.path.exists(pt) and os.path.exists(pj):
        return json.load(open(pj, encoding='utf-8'))
    inizio = time.time()
    f_add, f_val, f_fuori = RD.divisione_fogli()
    voc, ctx = RD.contesto(f_add)
    info = Info(voc)
    add, val, fuori = (_pagine(f, ctx, info) for f in (f_add, f_val, f_fuori))
    cfg = GM.cfg_completa(1, voc, ctx, RD.PICCOLO32)
    if not RD.PICCOLO32:
        cfg['nasc'] = int(nasc)
    cfg.update(cond=bool(cond), sizes=list(info.n))
    if cond and var:
        cfg.update(var)
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci_rete(cfg)
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=GM.LR, weight_decay=GM.DECADIMENTO)

    def say(s):
        if messaggi:
            try:
                messaggi(s)
            except OSError:
                pass
    curva_val, curva_add = [], []
    migliore, stato_A, ep_A = None, None, 0
    epoca = 0
    for epoca in range(1, RD.EPOCHE32 + 1):
        curva_add.append(_epoca35(m, ctx, add, opt, rng))
        v = round(bpc35(m, ctx, val), 5)
        curva_val.append(v)
        if migliore is None or v < migliore:
            migliore, ep_A = v, epoca
            stato_A = {k: t.detach().clone() for k, t in m.state_dict().items()}
        say('epoca %d: addestramento %.4f, validazione %.4f (migliore %.4f all\'epoca %d), %.0f s' % (epoca, curva_add[-1], v, migliore, ep_A, time.time() - inizio))
        if epoca - ep_A >= RD.PAZIENZA32:
            break
    extra = max(RD.EXTRA_MIN32, int(math.ceil(RD.EXTRA32 * ep_A)))
    for e in range(extra):
        epoca += 1
        curva_add.append(_epoca35(m, ctx, add, opt, rng))
        curva_val.append(round(bpc35(m, ctx, val), 5))
        say('epoca %d (extra %d/%d): addestramento %.4f, validazione %.4f, %.0f s' % (epoca, e + 1, extra, curva_add[-1], curva_val[-1], time.time() - inizio))
    stato_C = {k: t.detach().clone() for k, t in m.state_dict().items()}
    ris = OrderedDict([('condizionata', bool(cond)), ('variante', dict(var) if (cond and var) else None), ('parametri', sum(p.numel() for p in m.parameters())), ('nascosto', cfg['nasc']), ('fogli', [len(f_add), len(f_val), len(f_fuori)]),
                       ('epoca_A', ep_A), ('epoche_totali', epoca), ('extra', extra), ('bpc_val_A', curva_val[ep_A - 1]), ('bpc_val_C', curva_val[-1]),
                       ('bpc_add_A', curva_add[ep_A - 1]), ('bpc_add_C', curva_add[-1]), ('piccolo', RD.PICCOLO32), ('seme', seme)])
    for nome, st in (('A', stato_A), ('C', stato_C)):
        m.load_state_dict(st)
        m.eval()
        ris['bpc_fuori_' + nome] = round(bpc35(m, ctx, fuori), 5) if fuori else None
    m.load_state_dict(stato_C)
    ris['secondi'] = round(time.time() - inizio, 1)
    torch.save(dict(stato_A=stato_A, stato_C=stato_C, cfg=cfg, segni=list(voc['segni']), tipi=ctx.lista_tipi, f_add=f_add, f_val=f_val, f_fuori=f_fuori), pt + '.tmp')
    os.replace(pt + '.tmp', pt)
    json.dump(dict(ris, curva_validazione=curva_val, curva_addestramento=curva_add), open(pj, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def scegli_variante(cartella_mondo):
    """Sceglie la variante della rete condizionata con la perplessita' di VALIDAZIONE piu' bassa (istantanea A: il minimo di validazione; mai i fogli tenuti fuori) fra `rete_Ca`, `rete_Cb`,
    `rete_Cc` e la copia in `rete_C`. Scrive `scelta_rete.json` con la perplessita' di validazione e fuori piega di tutte (e dell'ablazione `rete_A`). -> dict."""
    import shutil
    campi = ('epoca_A', 'epoche_totali', 'parametri', 'bpc_val_A', 'bpc_val_C', 'bpc_fuori_A', 'bpc_fuori_C', 'bpc_add_C')
    out = OrderedDict()
    for nome in VARIANTI:
        pj = os.path.join(cartella_mondo, 'rete_' + nome, 'pieno.json')
        if os.path.exists(pj):
            d = json.load(open(pj, encoding='utf-8'))
            out[nome] = OrderedDict([('variante', d.get('variante'))] + [(k, d.get(k)) for k in campi])
    abl = None
    pj = os.path.join(cartella_mondo, 'rete_A', 'pieno.json')
    if os.path.exists(pj):
        d = json.load(open(pj, encoding='utf-8'))
        abl = OrderedDict((k, d.get(k)) for k in campi)
    scelta = min(out, key=lambda n: out[n]['bpc_val_A']) if out else None
    ris = OrderedDict([('varianti', out), ('ablazione', abl), ('scelta', scelta),
                       ('batte_ablazione_in_validazione', bool(scelta and abl and out[scelta]['bpc_val_A'] < abl['bpc_val_A']))])
    if scelta:
        dest = os.path.join(cartella_mondo, 'rete_C')
        if not os.path.exists(os.path.join(dest, 'pieno.pt')):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(os.path.join(cartella_mondo, 'rete_' + scelta), dest)
        json.dump(ris, open(os.path.join(cartella_mondo, 'scelta_rete.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


class PienoCond:
    """Come `rifare_dati.Pieno` per la rete nuova: `modello(s)` mescola le istantanee A (s = 0) e C (s = 1)."""

    def __init__(self, cartella):
        import torch
        d = torch.load(os.path.join(cartella, 'pieno.pt'), weights_only=False)
        voc = I7.vocabolario()
        assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
        cfg = d['cfg']
        self.ctx = GM.Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
        self.cfg, self.A, self.C = cfg, d['stato_A'], d['stato_C']
        self.f_add, self.f_val, self.f_fuori = d['f_add'], d['f_val'], d['f_fuori']
        self.info = Info(voc)
        self._m = {}

    def modello(self, s):
        s = round(float(min(1.0, max(0.0, s))), 3)
        if s not in self._m:
            m = costruisci_rete(self.cfg)
            st = {}
            for k, a in self.A.items():
                c = self.C[k]
                st[k] = ((1 - s) * a + s * c) if a.is_floating_point() else a.clone()
            m.load_state_dict(st)
            m.eval()
            m.info = self.info
            if len(self._m) > 6:
                self._m.clear()
            self._m[s] = m
        return self._m[s]


class PennaCond:
    """La rete passo per passo (una pagina alla volta): stesso calcolo del calcolo a tratti."""

    def __init__(self, m, ctx, capacita=None):
        import torch
        self.m, self.ctx, self.torch = m, ctx, torch

    def apri(self):
        self.h1 = self.h2 = None
        self.sc = StatoCond(self.m.info)

    def dai(self, tok):
        torch, m = self.torch, self.m
        tok = int(tok)
        c = self.sc.passo(tok)
        with torch.inference_mode():
            out = m(torch.tensor([[tok]]), torch.tensor([[c]]), self.h1, self.h2)
            self.h1 = out['y1'][:, -1][None]
            self.h2 = out['y2'][:, -1][None]
            return out['logits'][0, 0].tolist()


if __name__ == '__main__':
    pass
