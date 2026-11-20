# -*- coding: utf-8 -*-
"""Supporto di ia16 (modulo, non e' un esperimento): il transformer a segni che "rilegge la pagina".

Che cosa c'e' qui, in parole semplici
- `Imitatore`: un piccolo transformer a segni (stessi simboli e stessa disposizione di ia07: testa di pagina con sezione, mano e
  lingua, testa di riga con tipo, posizione e lunghezza, poi i segni). Ogni segno guarda i segni gia' scritti con una "attenzione"
  che pesa di piu' i segni vicini (ALiBi, Press e altri 2022, da ricontrollare) ma puo' arrivare lontano. Gli strati sono "L" (locali:
  guardano solo gli ultimi segni) e "G" (globali: guardano tutta la pagina scritta fin li'). Tre varianti, che cambiano SOLO che cosa il
  modello puo' guardare (stessi pesi, stesse dimensioni):
    P2 = gli strati globali vedono la pagina scritta fin li' piu' la coda della pagina precedente (contesto pieno);
    P1 = gli strati globali vedono la sola pagina scritta fin li' (senza la precedente);
    R  = tutti gli strati vedono la sola riga corrente (ablazione: senza memoria della pagina, ne' della riga sopra).
  Sezione, mano e lingua entrano anche come somma di tre vettori aggiunta a ogni segno della pagina (cosi' la variante R li vede).
- La coda della pagina precedente (`memoria`) si calcola come pagina a se' (come la memoria di Transformer-XL, Dai e altri 2019, da
  ricontrollare) e senza gradiente: chi scrive e chi si addestra usano lo stesso calcolo.
- `addestra_modello`: addestramento con arresto anticipato sulla validazione (bit per segno), come ia07.
- `Cache` e `Imitatore.passo`: scrittura segno per segno con la memoria delle chiavi e dei valori (nessun ricalcolo).
- `salva_modello` / `carica_modello`: formato ricaricabile per IA17 (pesi, configurazione, elenco dei simboli); mettendo
  `modello.salva_att = True` prima di una chiamata a `modello(...)` le matrici di attenzione (per strato e blocco di query, in
  mezza precisione) restano in `modello.att`.
Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import time

import numpy as np

# ---------------------------------------------------------------- configurazione (fissata nella preregistrazione)

# 'tipi': uno strato "L" (locale: guarda solo gli ultimi FINESTRA_LOC segni della pagina) o "G" (globale: guarda tutta la pagina in
# corso, e per P2 anche la coda della precedente, fino a FINESTRA segni indietro). L-G-L e' il circuito classico del "copiare dalla pagina":
# uno strato locale che dice che cosa precede, uno globale che cerca nella pagina dove e' gia' comparso, uno locale che lo usa.
TAGLIE = {'P': dict(d=96, H=3, tipi='LG', ff=384),
          'S': dict(d=128, H=4, tipi='LGL', ff=512)}
FINESTRA = 2048          # strati globali: al massimo tanti segni indietro (compresa la coda della pagina precedente)
FINESTRA_LOC = 96        # strati locali: circa due righe
PREC = 512               # segni della pagina precedente tenuti in memoria (la coda)
BLOCCO_G, BLOCCO_L = 256, 128   # query per blocco nel calcolo dell'attenzione (solo memoria e velocita', non cambia i numeri)
CADUTA = 0.25
LR = {'P': 2.0e-3, 'S': 1.5e-3}
DECADIMENTO = 0.05
TAGLIO = 1.0
PAGINE_PER_PASSO = 2     # pagine accumulate per ogni passo dell'ottimizzatore
RISCALDAMENTO = 100      # passi di aumento lineare del passo di apprendimento
VARIANTI = ('P2', 'P1', 'R')


def configurazione(taglia, variante, V, finestra_riga=None, piccolo=False):
    """Dizionario di configurazione di un modello. `piccolo`: solo per le prove del codice (mai per una corsa vera)."""
    c = dict(TAGLIE[taglia])
    c.update(taglia=taglia, variante=variante, V=int(V), caduta=CADUTA, finestra=FINESTRA, finestra_loc=FINESTRA_LOC, prec=PREC)
    if piccolo:
        c.update(d=32, H=2, ff=64, finestra=160, finestra_loc=24, prec=64)
    if variante == 'R':
        c['finestra'] = int(finestra_riga)       # basta una riga (piu' qualche segno di margine)
        c['finestra_loc'] = min(c['finestra_loc'], c['finestra'])
    c['strati'] = len(c['tipi'])
    return c


# ---------------------------------------------------------------- il modello

def costruisci(cfg):
    """Il modulo torch (importato qui per non caricare torch da chi legge solo le costanti). Restituisce (modello, classe Cache)."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Blocco(nn.Module):
        def __init__(self, d, ff, caduta):
            super().__init__()
            self.ln1, self.qkv, self.proj = nn.LayerNorm(d), nn.Linear(d, 3 * d), nn.Linear(d, d)
            self.ln2, self.fc1, self.fc2 = nn.LayerNorm(d), nn.Linear(d, ff), nn.Linear(ff, d)
            self.drop = nn.Dropout(caduta)

    class Imitatore(nn.Module):
        def __init__(self, cfg):
            super().__init__()
            self.cfg = dict(cfg)
            d, H, V = cfg['d'], cfg['H'], cfg['V']
            self.d, self.H, self.dh = d, H, d // H
            self.tipi = cfg['tipi']
            self.strati = len(self.tipi)
            self.W_glob, self.W_loc = int(cfg['finestra']), int(cfg['finestra_loc'])
            self.variante = cfg['variante']
            self.ultimo_g = max(i for i, t in enumerate(self.tipi) if t == 'G')
            assert d % H == 0
            self.emb, self.cond = nn.Embedding(V, d), nn.Embedding(V, d)
            self.drop = nn.Dropout(cfg['caduta'])
            self.blocchi = nn.ModuleList([Blocco(d, cfg['ff'], cfg['caduta']) for _ in range(self.strati)])
            self.lnf, self.out = nn.LayerNorm(d), nn.Linear(d, V)
            self.register_buffer('pendenze', torch.tensor([2.0 ** (-8.0 * (h + 1) / H) for h in range(H)]), persistent=False)
            self.salva_att = False
            self.att = []
            self._avvia()

        def _avvia(self):
            for m in self.modules():
                if isinstance(m, (nn.Linear, nn.Embedding)):
                    nn.init.normal_(m.weight, std=0.02)
                    if getattr(m, 'bias', None) is not None:
                        nn.init.zeros_(m.bias)
            for b in self.blocchi:
                nn.init.normal_(b.proj.weight, std=0.02 / math.sqrt(2 * self.strati))
                nn.init.normal_(b.fc2.weight, std=0.02 / math.sqrt(2 * self.strati))

        # ---- calcolo su una pagina intera (addestramento, validazione, memoria)
        def _blocchi(self, T, Tm, W, QB, lin):
            """Blocchi di query: per ognuno (a, b, lo, hi, bias). `bias` = -pendenza * distanza dove il segno e' visibile, -inf altrove.
            `lin`: numeri di riga (solo variante R: si vede solo la riga corrente; allora Tm e' 0)."""
            out = []
            for a in range(0, T, QB):
                b = min(T, a + QB)
                qg = torch.arange(Tm + a, Tm + b)
                lo, hi = max(0, Tm + a - W + 1), Tm + b
                dist = qg[:, None] - torch.arange(lo, hi)[None, :]
                ok = (dist >= 0) & (dist < W)
                if lin is not None:
                    ok &= lin[a:b][:, None] == lin[lo:hi][None, :]
                bias = torch.where(ok, -self.pendenze[:, None, None] * dist.clamp(min=0).to(torch.float32), torch.tensor(float('-inf')))
                out.append((a, b, lo, hi, bias))
            return out

        def forward(self, tok, cond, linea=None, mem=None, solo_kv=False):
            """tok: (T,) interi (gli ingressi); cond: (3,) sezione, mano, lingua; linea: (T,) numero di riga (solo per R);
            mem: lista per strato di (K, V) della pagina precedente (None per gli strati locali), (H, Tm, dh) senza gradiente.
            Restituisce i logit (T, V); con `solo_kv` si ferma all'ultimo strato globale e restituisce le chiavi e i valori."""
            tok = torch.as_tensor(np.asarray(tok), dtype=torch.long)
            cond = torch.as_tensor(np.asarray(cond), dtype=torch.long)
            T = tok.shape[0]
            Tm = next((m[0].shape[1] for m in mem if m is not None), 0) if mem else 0
            H, dh, d = self.H, self.dh, self.d
            x = self.drop(self.emb(tok) + self.cond(cond).sum(0))
            lin = torch.as_tensor(np.asarray(linea), dtype=torch.long) if self.variante == 'R' else None
            piani = {}
            if 'L' in self.tipi:
                piani['L'] = self._blocchi(T, 0, self.W_loc, BLOCCO_L, lin)
            if 'G' in self.tipi:
                piani['G'] = self._blocchi(T, Tm, self.W_glob, BLOCCO_G, lin)
            kvs = []
            if self.salva_att:
                self.att = []
            scala = 1.0 / math.sqrt(dh)
            for l, b in enumerate(self.blocchi):
                h = b.ln1(x)
                qkv = b.qkv(h).view(T, 3, H, dh)
                q, k, v = qkv[:, 0].transpose(0, 1), qkv[:, 1].transpose(0, 1), qkv[:, 2].transpose(0, 1)
                if solo_kv:
                    kvs.append((k.detach(), v.detach()) if self.tipi[l] == 'G' else None)
                if self.tipi[l] == 'G' and mem and mem[l] is not None:
                    k, v = torch.cat([mem[l][0], k], 1), torch.cat([mem[l][1], v], 1)
                o = []
                for a_, b_, lo, hi, bias in piani[self.tipi[l]]:
                    if self.salva_att:
                        p = torch.softmax(torch.matmul(q[:, a_:b_], k[:, lo:hi].transpose(1, 2)) * scala + bias, -1)
                        self.att.append((l, a_, b_, lo, hi, p.detach().to(torch.float16).numpy()))
                        o.append(torch.matmul(p, v[:, lo:hi]))
                    else:
                        o.append(F.scaled_dot_product_attention(q[None, :, a_:b_], k[None, :, lo:hi], v[None, :, lo:hi],
                                                                attn_mask=bias[None])[0])
                o = torch.cat(o, 1).transpose(0, 1).reshape(T, d)
                x = x + b.drop(b.proj(o))
                x = x + b.drop(b.fc2(F.gelu(b.fc1(b.ln2(x)))))
                if solo_kv and l == self.ultimo_g:
                    return kvs
            return self.out(self.lnf(x))

        def memoria(self, tok, cond):
            """Chiavi e valori degli strati globali di una pagina (la coda della precedente) calcolati come pagina a se', senza
            gradiente, in modalita' di prova. Per gli strati locali None."""
            vecchio, sa = self.training, self.salva_att
            self.eval()
            self.salva_att = False
            with torch.no_grad():
                kv = self.forward(tok, cond, None, None, solo_kv=True)
            self.salva_att = sa
            self.train(vecchio)
            return kv + [None] * (self.strati - len(kv))

        # ---- scrittura segno per segno
        def nuova_cache(self, capacita):
            return Cache(self, capacita)

        def passo(self, tok, cond_vec, c, inizio_riga=False):
            """Un segno in ingresso; restituisce i logit del prossimo. `cond_vec`: somma dei tre vettori di condizionamento (d,).
            `c`: la Cache della pagina; `inizio_riga`: il segno e' il primo della testa di riga (serve alla variante R)."""
            H, dh, d = self.H, self.dh, self.d
            t = c.n
            if inizio_riga:
                c.inizio_riga = t
            if self.variante == 'R':
                base = c.inizio_riga
            elif self.variante == 'P1':
                base = c.inizio_pag
            else:
                base = 0
            lo_g = max(base, t + 1 - self.W_glob)
            lo_l = max(c.inizio_riga if self.variante == 'R' else c.inizio_pag, t + 1 - self.W_loc)
            bias = {}
            for tp, lo in (('G', lo_g), ('L', lo_l)):
                if tp in self.tipi:
                    bias[tp] = (lo, -self.pendenze[:, None] * (t - c.indici[lo:t + 1]).to(torch.float32)[None, :])
            x = self.emb(torch.tensor(tok)) + cond_vec
            scala = 1.0 / math.sqrt(dh)
            for l, b in enumerate(self.blocchi):
                h = b.ln1(x)
                qkv = b.qkv(h).view(3, H, dh)
                c.K[l][:, t] = qkv[1]
                c.V[l][:, t] = qkv[2]
                lo, bs = bias[self.tipi[l]]
                Ks, Vs = c.K[l][:, lo:t + 1], c.V[l][:, lo:t + 1]
                p = torch.softmax(torch.matmul(Ks, qkv[0].unsqueeze(-1)).squeeze(-1) * scala + bs, -1)
                o = torch.matmul(p.unsqueeze(1), Vs).reshape(d)
                x = x + b.proj(o)
                x = x + b.fc2(F.gelu(b.fc1(b.ln2(x))))
            c.n = t + 1
            return self.out(self.lnf(x))

        def vettore_cond(self, cond):
            return self.cond(torch.as_tensor(np.asarray(cond), dtype=torch.long)).sum(0)

    class Cache:
        """Chiavi e valori di ogni strato: prima la coda della pagina precedente (solo strati globali, se c'e'), poi la pagina in corso."""

        def __init__(self, m, capacita):
            self.m = m
            self.K = [torch.zeros(m.H, capacita, m.dh) for _ in range(m.strati)]
            self.V = [torch.zeros(m.H, capacita, m.dh) for _ in range(m.strati)]
            self.indici = torch.arange(capacita)
            self.n = self.inizio_pag = self.inizio_riga = 0

        def riparti(self, mem=None):
            self.n = 0
            if mem:
                for l, kv in enumerate(mem):
                    if kv is not None:
                        self.K[l][:, :kv[0].shape[1]] = kv[0]
                        self.V[l][:, :kv[1].shape[1]] = kv[1]
                        self.n = kv[0].shape[1]
            self.inizio_pag = self.inizio_riga = self.n

    return Imitatore(cfg), Cache


# ---------------------------------------------------------------- addestramento

def bpc_pagine(m, pagine, primo, memoria=True):
    """Bit per segno (contenuto, spazi e fine riga) sulle pagine date (dizionari di pagina di ia16); stato dall'inizio della pagina e,
    per P2, la coda della pagina precedente VERA (se la pagina ne ha una)."""
    import torch
    import torch.nn.functional as F
    vecchio = m.training
    m.eval()
    tot = n = 0.0
    with torch.no_grad():
        for p in pagine:
            mem = m.memoria(p['prev_tok'], p['prev_cond']) if (memoria and m.variante == 'P2' and p['prev_tok'] is not None) else None
            logit = m(p['tok'][:-1], p['cond'], p['linea'][:-1], mem)
            y = torch.as_tensor(p['tok'][1:], dtype=torch.long)
            mk = y >= primo
            tot += F.cross_entropy(logit[mk], y[mk], reduction='sum').item()
            n += float(mk.sum())
    m.train(vecchio)
    return tot / max(n, 1.0) / math.log(2)


def addestra_modello(cfg, add, val, primo, seme, epoche_max, pazienza, lr=None, epoche_fisse=None, messaggi=None):
    """Addestra un modello. add, val: liste di dizionari di pagina (vedi ia16). Arresto anticipato sulla validazione: ci si ferma
    quando non migliora da `pazienza` epoche; si tiene il migliore. `epoche_fisse`: numero di epoche senza validazione (modello su
    tutto). Restituisce (modello, curva_validazione, curva_addestramento, epoca_scelta)."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m, _ = costruisci(cfg)
    m.train()
    lr = lr or LR.get(cfg.get('taglia'), 1.0e-3)
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=DECADIMENTO)
    massimo = epoche_fisse or epoche_max
    passi_epoca = math.ceil(len(add) / PAGINE_PER_PASSO)
    totale = massimo * passi_epoca
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / RISCALDAMENTO) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1.0, s / max(totale, 1))))))
    curva_val, curva_add, migliore, stato = [], [], None, None
    inizio = time.time()
    for epoca in range(1, massimo + 1):
        ordine = rng.permutation(len(add))
        perdita = conti = 0.0
        for a in range(0, len(ordine), PAGINE_PER_PASSO):
            lotto = [add[i] for i in ordine[a:a + PAGINE_PER_PASSO]]
            n_lotto = sum(int((np.asarray(p['tok'][1:]) >= primo).sum()) for p in lotto)
            opt.zero_grad()
            for p in lotto:
                mem = m.memoria(p['prev_tok'], p['prev_cond']) if (cfg['variante'] == 'P2' and p['prev_tok'] is not None) else None
                logit = m(p['tok'][:-1], p['cond'], p['linea'][:-1], mem)
                y = torch.as_tensor(p['tok'][1:], dtype=torch.long)
                mk = y >= primo
                loss = F.cross_entropy(logit[mk], y[mk], reduction='sum') / max(n_lotto, 1)
                loss.backward()
                perdita += loss.item() * max(n_lotto, 1)
                conti += float(mk.sum())
            nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
            opt.step()
            sched.step()
        curva_add.append(round(perdita / max(conti, 1) / math.log(2), 5))
        if val and not epoche_fisse:
            v = round(bpc_pagine(m, val, primo), 5)
            curva_val.append(v)
            if migliore is None or v < migliore:
                migliore = v
                stato = {k: t.detach().clone() for k, t in m.state_dict().items()}
            if messaggi:
                messaggi('  epoca %d: addestramento %.4f, validazione %.4f (migliore %.4f), %.0f s' % (epoca, curva_add[-1], v, migliore, time.time() - inizio))
            if len(curva_val) - 1 - curva_val.index(min(curva_val)) >= pazienza:
                break
        elif messaggi:
            messaggi('  epoca %d: addestramento %.4f, %.0f s' % (epoca, curva_add[-1], time.time() - inizio))
    if stato is not None:
        m.load_state_dict(stato)
    scelta = (curva_val.index(min(curva_val)) + 1) if curva_val else massimo
    m.eval()
    return m, curva_val, curva_add, scelta


# ---------------------------------------------------------------- salvare e ricaricare (per IA17)

def salva_modello(m, percorso, segni, extra=None):
    """Salva pesi, configurazione e l'elenco dei simboli (in ordine di indice): `carica_modello` ridà lo stesso modello."""
    import torch
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    torch.save(dict(stato=m.state_dict(), cfg=m.cfg, segni=list(segni), extra=extra or {}), percorso + '.tmp')
    os.replace(percorso + '.tmp', percorso)


def carica_modello(percorso, segni=None):
    """Ricarica un modello salvato con `salva_modello`, in modalita' di prova. Se `segni` e' dato, controlla che i simboli siano gli stessi."""
    import torch
    d = torch.load(percorso, weights_only=False)
    if segni is not None:
        assert list(d['segni']) == list(segni), 'elenco dei simboli diverso da quello del modello'
    m, _ = costruisci(d['cfg'])
    m.load_state_dict(d['stato'])
    m.eval()
    return m
