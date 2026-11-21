# -*- coding: utf-8 -*-
"""Supporto di ia20 (modulo, non e' un esperimento): la scala di imitatori M1-M5.

Che cosa c'e' qui, in parole semplici
- Cinque modelli a segni, ognuno aggiunge UN ingrediente al precedente (stesse teste di pagina e di riga di ia07, stesso modo di
  imparare):
    M1  GRU 2 x 256 (come ia07: immersione 64, caduta 0,3), scritta qui come due GRU da uno strato con la caduta in mezzo;
    M2  = M1 + memoria locale: fra i due strati un'attenzione sui segni della riga in corso e della riga sopra (e solo quelle);
    M3  = M2 + vocabolario della pagina: un vettore (media dei vettori delle parole gia' scritte nella pagina) dato alla GRU;
    M4  = M3 + posizione nella riga: numero della parola, prima parola, segni che mancano ai due estremi della fascia di lunghezza;
    M5  = M4 + copia e ritocco: a inizio parola un puntatore sceglie fra "scrivi libero" e "copia una parola della riga in corso o
          di quella sopra, uguale o con una modifica (un glifo cambiato, aggiunto o tolto)"; le probabilita' sono imparate.
- L'addestramento e' quello di ia07 (lotti di 8 pagine, AdamW, un passo per tratto) con un solo cambio: i tratti di circa 256 segni
  finiscono alla fine di una riga (cosi' nessuna parola e nessuna riga si spezza fra due tratti: serve al puntatore). Lo stato
  della GRU passa da un tratto al successivo (senza gradiente), come in ia07; anche la memoria dell'attenzione (la riga sopra).
- M5 e' una miscela esatta a livello di parola: P(parola) = pi_libero * P_GRU(parola) + somma sulle parole candidate di
  pi_candidato,tipo * P(ritocco). La perdita e' il -log di questa probabilita', quindi i bit per segno di M5 si confrontano con quelli
  di M1-M4. Per scrivere si pesca prima la scelta (libero / candidato e tipo di ritocco) e poi la parola.
- Salvataggio ricaricabile (`salva_modello` / `carica_modello`), scrittura segno per segno (`Penna20`) uguale al calcolo a tratti.
Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import time
import random
from collections import Counter, OrderedDict

import numpy as np

# ---------------------------------------------------------------- costanti (fissate nella preregistrazione)

PASSI = (1, 2, 3, 4, 5)
NOME_PASSO = {1: 'M1', 2: 'M2', 3: 'M3', 4: 'M4', 5: 'M5'}
EMB, NASCOSTO, CADUTA = 64, 256, 0.3
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
LOTTO = 8
TRONCO = 256                 # segni per tratto (il tratto finisce alla fine della prima riga che arriva a questa lunghezza)
ATT_D, ATT_H = 128, 4        # attenzione di M2: dimensione e teste
PENDENZE = [2.0 ** (-4 - 2 * h) for h in range(ATT_H)]   # distanza -> penalita' (1/16, 1/64, 1/256, 1/1024 per segno)
DP = 64                      # vettore del vocabolario della pagina (M3)
NW, WEMB, N_NUM = 12, 8, 4   # M4: numero della parola (0-11), sua immersione, numeri (r_lo, r_hi, prima parola, in riga)
K_TIPI = 200                 # M3 e M5: le K parole piu' frequenti nell'addestramento hanno un posto proprio nel vettore delle parole
S_CAND = 28                  # M5: parole candidate (le piu' recenti della riga in corso e di quella sopra)
DK = 64                      # M5: dimensione di chiave e domanda del puntatore
LUNG_MAX = 10                # lunghezze di parola distinte nel vettore delle parole
NTIPI = 4                    # M5: tipi di candidato: 0 uguale, 1 un glifo cambiato, 2 un glifo aggiunto, 3 un glifo tolto
VERSIONE = 'gradini-1'


def configurazione(passo, V, piccolo=False):
    """Configurazione di un modello. `piccolo`: solo per le prove del codice (mai in una corsa vera)."""
    c = dict(passo=int(passo), V=int(V), emb=EMB, nasc=NASCOSTO, caduta=CADUTA, att_d=ATT_D, att_h=ATT_H, dp=DP, dk=DK, K=K_TIPI, S=S_CAND, versione=VERSIONE)
    if piccolo:
        c.update(emb=16, nasc=48, att_d=32, dp=16, dk=16, K=40, S=12)
    return c


# ---------------------------------------------------------------- contesto: segni, teste, parole piu' frequenti

class Ctx:
    """Tutto cio' che serve a leggere una pagina per un modello: dove stanno i segni, le teste, le fasce di lunghezza e l'elenco delle
    K parole piu' frequenti (viene dall'addestramento della piega: e' un elenco di parole, non una frequenza)."""

    def __init__(self, voc, tipi, K=K_TIPI, S=S_CAND):
        i = voc['idx']
        self.primo = voc['primo_contenuto']
        self.SP, self.EOL, self.u0 = self.primo, self.primo + 1, self.primo + 2
        self.U = len(voc['unita'])
        self.Tset = frozenset(i['T:' + t] for t in 'PMUS')
        self.N0, self.nbins = i['N:0'], 8
        b = list(voc['bordi'])
        self.lo = np.array([0.0] + b)
        self.hi = np.array(b + [float(voc['lmax'])])
        self.K, self.S = int(K), int(S)
        self.lista_tipi = [tuple(w) for w in tipi[:self.K]]
        self.tipi = {w: j for j, w in enumerate(self.lista_tipi)}
        self.nf = (self.K + 1) + (self.U + 2) ** 2 + LUNG_MAX
        self.V = len(voc['segni'])
        self.lmax = int(voc['lmax'])
        self.bordi = b


def tipi_da_pagine(pagine, ctx_tmp):
    """Le K parole piu' frequenti (tuple di indici di glifo) nelle pagine date (parita': ordine delle tuple)."""
    c = Counter()
    for P in pagine:
        tok = P['tok']
        for s, e in parole_di_tok(tok, ctx_tmp):
            c[tuple(int(x) - ctx_tmp.u0 for x in tok[s:e])] += 1
    return [w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:ctx_tmp.K]]


def parole_di_tok(tok, ctx):
    """[(s, e)]: s = posizione del primo segno, e = posizione del terminatore (spazio o fine riga). Solo parole non vuote."""
    u0 = ctx.u0
    t, T, out = 0, len(tok), []
    tk = [int(x) for x in tok]
    while t < T:
        if tk[t] >= u0 and (t == 0 or tk[t - 1] < u0):
            s = t
            while t < T and tk[t] >= u0:
                t += 1
            out.append((s, t))
        else:
            t += 1
    return out


def feat_parola(units, ctx):
    """Vettore fisso (non imparato) di una parola: [indice fra le K frequenti (o 'altra')] + [coppie di glifi dentro la parola, con
    margini di inizio e fine, normalizzate] + [lunghezza]. `units`: indici di glifo (0..U-1)."""
    f = np.zeros(ctx.nf, np.float32)
    f[ctx.tipi.get(tuple(units), ctx.K)] = 1.0
    U2 = ctx.U + 2
    seq = [0] + [u + 1 for u in units] + [ctx.U + 1]
    n = len(seq) - 1
    base = ctx.K + 1
    for a, b in zip(seq, seq[1:]):
        f[base + a * U2 + b] += 1.0 / n
    f[base + U2 * U2 + min(len(units), LUNG_MAX) - 1] = 1.0
    return f


def scripts(c, w, U):
    """Modi per ottenere la parola `w` dal candidato `c` con al piu' un ritocco (tuple di indici di glifo): lista di
    (tipo, contesto, glifo, n). tipo 0 uguale; 1 un glifo cambiato (contesto = glifo di c cambiato, glifo = nuovo, n = len(c));
    2 un glifo aggiunto (contesto = glifo a sinistra, U = margine; glifo = aggiunto; n = len(c)+1); 3 un glifo tolto (n = len(c)).
    Le scritture che danno parola vuota non ci sono."""
    lc, lw = len(c), len(w)
    if c == w:
        return [(0, 0, 0, 1)]
    out = []
    if lw == lc:
        diff = [i for i in range(lc) if c[i] != w[i]]
        if len(diff) == 1:
            i = diff[0]
            out.append((1, c[i], w[i], lc))
    elif lw == lc + 1:
        for i in range(lc + 1):
            if w[:i] == c[:i] and w[i + 1:] == c[i:]:
                out.append((2, c[i - 1] if i > 0 else U, w[i], lc + 1))
    elif lw == lc - 1 and lw >= 1:
        for i in range(lc):
            if c[:i] + c[i + 1:] == w:
                out.append((3, 0, 0, lc))
    return out


def tagli_riga(tok, ctx, tronco=TRONCO):
    """Tratti (a, c) sulle posizioni d'ingresso (0 .. T-2): il tratto finisce dove comincia la prima riga dopo `tronco` segni."""
    Tin = len(tok) - 1
    starts = [t for t in range(Tin) if int(tok[t]) in ctx.Tset]
    cuts = [0]
    while True:
        target = cuts[-1] + tronco
        if target >= Tin:
            break
        nxt = next((s for s in starts if s >= target), None)
        if nxt is None:
            break
        cuts.append(nxt)
    cuts.append(Tin)
    return [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]


def prepara_pagina(d, ctx, con_puntatore=True):
    """Dati fissi di una pagina (`d`: dizionario di ia16.dati_pagine con almeno `tok`, `linea`, `nome`): parole, vettori, tratti, numeri
    della posizione nella riga, candidati e scritture del puntatore."""
    tok = np.asarray(d['tok'], dtype=np.int64)
    linea = np.asarray(d['linea'], dtype=np.int64)
    T, Tin = len(tok), len(tok) - 1
    tk = [int(x) for x in tok]
    u0, SP, N0 = ctx.u0, ctx.SP, ctx.N0
    widx = np.zeros(Tin, np.int64)
    sof = np.zeros(Tin, np.int64)
    bn = np.full(Tin, -1, np.int64)
    w = sofar = 0
    binv = -1
    for t in range(Tin):
        x = tk[t]
        if x in ctx.Tset:
            w = sofar = 0
            binv = -1
        elif N0 <= x < N0 + ctx.nbins:
            binv = x - N0
        elif x == SP:
            w += 1
            sofar += 1
        elif x >= u0:
            sofar += 1
        widx[t], sof[t], bn[t] = min(w, NW - 1), sofar, binv
    words = parole_di_tok(tok, ctx)
    nw = len(words)
    units = [tuple(tk[s + j] - u0 for j in range(e - s)) for s, e in words]
    Fw = np.zeros((nw, ctx.nf), np.float32)
    for j, un in enumerate(units):
        Fw[j] = feat_parola(un, ctx)
    Cw = np.zeros((nw + 1, ctx.nf), np.float32)
    if nw:
        Cw[1:] = np.cumsum(Fw, axis=0, dtype=np.float64).astype(np.float32)
    ends = np.array([e for s, e in words], dtype=np.int64)
    ncomp = np.searchsorted(ends, np.arange(Tin), side='right').astype(np.int64)
    P = dict(nome=d['nome'], tok=tok, linea=linea, T=T, Tin=Tin, widx=widx, sof=sof, bn=bn, words=words, units=units, nw=nw, Fw=Fw, Cw=Cw,
             ncomp=ncomp, chunks=tagli_riga(tok, ctx))
    if con_puntatore:
        wl = [int(linea[s]) for s, e in words]
        per_riga = {}
        for j, l in enumerate(wl):
            per_riga.setdefault(l, []).append(j)
        cand = np.full((nw, ctx.S), -1, np.int16)
        pj, pk, pt, pc, px, pn = [], [], [], [], [], []
        for j in range(nw):
            l = wl[j]
            lst = ([k for k in per_riga[l] if k < j][::-1] + per_riga.get(l - 1, [])[::-1])[:ctx.S]
            cand[j, :len(lst)] = lst
            for k, c in enumerate(lst):
                for (t_, cx, x_, n_) in scripts(units[c], units[j], ctx.U):
                    pj.append(j), pk.append(k), pt.append(t_), pc.append(cx), px.append(x_), pn.append(n_)
        P.update(cand=cand, pj=np.array(pj, np.int64), pk=np.array(pk, np.int64), pt=np.array(pt, np.int64), pc=np.array(pc, np.int64),
                 px=np.array(px, np.int64), pn=np.array(pn, np.float32),
                 ws0=np.array([s - 1 for s, e in words], np.int64), we0=np.array([e - 1 for s, e in words], np.int64),
                 wterm=np.array([0 if tk[e] == SP else 1 for s, e in words], np.int64))
    return P


# ---------------------------------------------------------------- un lotto: un tratto per ogni pagina ancora attiva

def lotto_tratto(righe, ctx, passo):
    """righe: [(P, (a, c))]. Restituisce i tensori numpy del tratto: ingressi X, bersagli Y, maschera Mk (segni da indovinare), numero
    di riga `lin` e posizione `pos` per l'attenzione, vettore delle parole F (M3), numero della parola e numeri (M4), parole (M5)."""
    B = len(righe)
    L = max(c - a for _, (a, c) in righe)
    X = np.zeros((B, L), np.int64)
    Y = np.zeros((B, L), np.int64)
    Mk = np.zeros((B, L), np.float32)
    lin = np.full((B, L), -99, np.int64)
    pos = np.zeros((B, L), np.int64)
    lens = []
    out = dict(B=B, L=L)
    if passo >= 3:
        F = np.zeros((B, L, ctx.nf + 1), np.float32)
    if passo >= 4:
        W = np.zeros((B, L), np.int64)
        NUM = np.zeros((B, L, N_NUM), np.float32)
    for b, (P, (a, c)) in enumerate(righe):
        n = c - a
        lens.append(n)
        X[b, :n] = P['tok'][a:c]
        Y[b, :n] = P['tok'][a + 1:c + 1]
        Mk[b, :n] = (Y[b, :n] >= ctx.primo)
        lin[b, :n] = P['linea'][a:c]
        pos[b, :n] = np.arange(a, c)
        pos[b, n:] = 10 ** 6 + np.arange(L - n)
        if passo >= 3:
            nc = P['ncomp'][a:c]
            F[b, :n, :ctx.nf] = P['Cw'][nc] / np.maximum(nc, 1)[:, None]
            F[b, :n, ctx.nf] = np.log1p(nc) / 6.0
        if passo >= 4:
            bnn, so = P['bn'][a:c], P['sof'][a:c]
            W[b, :n] = P['widx'][a:c]
            inl = bnn >= 0
            bi = np.maximum(bnn, 0)
            NUM[b, :n, 0] = np.where(inl, np.clip((ctx.lo[bi] - so) / 40.0, -1.0, 2.0), 0.0)
            NUM[b, :n, 1] = np.where(inl, np.clip((ctx.hi[bi] - so) / 40.0, -1.0, 3.0), 0.0)
            NUM[b, :n, 2] = (inl & (P['widx'][a:c] == 0)).astype(np.float32)
            NUM[b, :n, 3] = inl.astype(np.float32)
    out.update(X=X, Y=Y, Mk=Mk, lin=lin, pos=pos, lens=np.array(lens))
    if passo >= 3:
        out['F'] = F
    if passo >= 4:
        out.update(W=W, NUM=NUM)
    if passo >= 5:
        rows, s0, e0, term, Fc, valid = [], [], [], [], [], []
        pj, pk, pt, pc, px, pn = [], [], [], [], [], []
        J0 = 0
        for b, (P, (a, c)) in enumerate(righe):
            j0 = int(np.searchsorted(P['ws0'], a, side='left'))
            j1 = int(np.searchsorted(P['ws0'], c, side='left'))
            if j1 > j0:
                assert P['we0'][j1 - 1] < c, 'una parola attraversa il confine del tratto'
            nj = j1 - j0
            rows += [b] * nj
            s0.append(P['ws0'][j0:j1] - a)
            e0.append(P['we0'][j0:j1] - a)
            term.append(P['wterm'][j0:j1])
            cd = P['cand'][j0:j1].astype(np.int64)
            valid.append(cd >= 0)
            Fc.append(P['Fw'][np.maximum(cd, 0)] * (cd >= 0)[..., None])
            lo = int(np.searchsorted(P['pj'], j0, side='left'))
            hi = int(np.searchsorted(P['pj'], j1, side='left'))
            pj.append(P['pj'][lo:hi] - j0 + J0)
            pk.append(P['pk'][lo:hi]), pt.append(P['pt'][lo:hi]), pc.append(P['pc'][lo:hi]), px.append(P['px'][lo:hi]), pn.append(P['pn'][lo:hi])
            J0 += nj
        cat = lambda l, dt, shp=(): np.concatenate(l) if l else np.zeros((0,) + shp, dt)
        out['parole'] = dict(rows=np.array(rows, np.int64), s0=cat(s0, np.int64), e0=cat(e0, np.int64), term=cat(term, np.int64),
                             Fc=cat(Fc, np.float32, (ctx.S, ctx.nf)), valid=cat(valid, bool, (ctx.S,)), pj=cat(pj, np.int64), pk=cat(pk, np.int64),
                             pt=cat(pt, np.int64), pc=cat(pc, np.int64), px=cat(px, np.int64), pn=cat(pn, np.float32), J=J0)
    return out


# ---------------------------------------------------------------- il modello

def costruisci(cfg, ctx=None):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F_

    class Modello(nn.Module):
        def __init__(self, cfg):
            super().__init__()
            self.cfg = dict(cfg)
            self.passo = cfg['passo']
            V, H = cfg['V'], cfg['nasc']
            self.H = H
            self.emb = nn.Embedding(V, cfg['emb'])
            din = cfg['emb']
            if self.passo >= 3:
                self.nf = cfg['nf']
                self.Wp = nn.Parameter(torch.randn(self.nf + 1, cfg['dp']))
                din += cfg['dp']
            if self.passo >= 4:
                self.wemb = nn.Embedding(NW, WEMB)
                din += WEMB + N_NUM
            self.gru1 = nn.GRU(din, H, 1, batch_first=True)
            self.gru2 = nn.GRU(H, H, 1, batch_first=True)
            self.caduta = nn.Dropout(cfg['caduta'])
            self.out = nn.Linear(H, V)
            if self.passo >= 2:
                d, h = cfg['att_d'], cfg['att_h']
                self.aq, self.ak, self.av = nn.Linear(H, d), nn.Linear(H, d), nn.Linear(H, d)
                self.ao = nn.Linear(d, H)
                nn.init.normal_(self.ao.weight, std=0.02)
                nn.init.zeros_(self.ao.bias)
                self.register_buffer('pend', torch.tensor(PENDENZE[:h], dtype=torch.float32), persistent=False)
            if self.passo >= 5:
                U, S, dk = cfg['U'], cfg['S'], cfg['dk']
                self.U, self.S = U, S
                self.pq = nn.Linear(H, dk)
                self.pf = nn.Linear(H, 1)
                nn.init.constant_(self.pf.bias, 2.0)
                self.Wc = nn.Parameter(torch.randn(self.nf, dk) * 0.05)
                self.rec = nn.Parameter(torch.zeros(S))
                self.beta = nn.Parameter(torch.tensor([-3.0, -4.0, -4.0, -4.0]))
                self.Tsub = nn.Parameter(torch.zeros(U, U))
                self.Tins = nn.Parameter(torch.zeros(U + 1, U))

        # ---- ingressi della GRU
        def ingresso(self, X, bt):
            parti = [self.emb(X)]
            if self.passo >= 3:
                parti.append(torch.matmul(bt['F'], self.Wp))
            if self.passo >= 4:
                parti += [self.wemb(bt['W']), bt['NUM']]
            return torch.cat(parti, -1)

        # ---- attenzione locale (M2): righe in corso e sopra, con memoria del tratto precedente
        def attenzione(self, u, lin, pos, mem):
            B, L, _ = u.shape
            h = self.cfg['att_h']
            dh = self.cfg['att_d'] // h
            if mem is not None:
                src = torch.cat([mem[0], u], 1)
                kl, kp = torch.cat([mem[1], lin], 1), torch.cat([mem[2], pos], 1)
            else:
                src, kl, kp = u, lin, pos
            Kt = src.shape[1]
            q = self.aq(u).view(B, L, h, dh).transpose(1, 2)
            k = self.ak(src).view(B, Kt, h, dh).transpose(1, 2)
            v = self.av(src).view(B, Kt, h, dh).transpose(1, 2)
            dist = pos[:, :, None] - kp[:, None, :]
            ok = (dist >= 0) & (kl[:, None, :] >= lin[:, :, None] - 1)
            ok = ok & (kl[:, None, :] > -90) | (dist == 0)
            bias = -self.pend[None, :, None, None] * dist.clamp(min=0)[:, None].to(torch.float32)
            bias = bias.masked_fill(~ok[:, None], float('-inf'))
            o = F_.scaled_dot_product_attention(q, k, v, attn_mask=bias)
            return self.ao(o.transpose(1, 2).reshape(B, L, h * dh))

        def forward(self, X, bt, h1=None, h2=None, mem=None):
            """X (B, L) segni in ingresso. Restituisce un dizionario: logits (B, L, V), hd (B, L, H) (stato d'uscita con la caduta),
            y1 (stati del primo strato = quel che si porta al tratto dopo), u (ingresso dell'attenzione = memoria), y2."""
            y1, _ = self.gru1(self.ingresso(X, bt), h1)
            u = self.caduta(y1)
            u2 = u + self.attenzione(u, bt['lin'], bt['pos'], mem) if self.passo >= 2 else u
            y2, _ = self.gru2(u2, h2)
            hd = self.caduta(y2)
            return dict(logits=self.out(hd), hd=hd, y1=y1, y2=y2, u=u)

        # ---- puntatore (M5)
        def tabelle(self):
            U = self.U
            d = torch.full((U, U), 0.0)
            d.fill_diagonal_(float('-inf'))
            return F_.log_softmax(self.Tsub + d, 1), F_.log_softmax(self.Tins, 1)

        def puntatore(self, hs, Fc, valid):
            """hs (J, H) stati a inizio parola; Fc (J, S, nf) vettori dei candidati; valid (J, S). -> (log pi_libero (J,), log pi (J, S, 4))."""
            q = self.pq(hs)
            enc = torch.matmul(Fc, self.Wc)
            sc = (q[:, None, :] * enc).sum(-1) / math.sqrt(self.cfg['dk']) + self.rec[None, :]
            lg = (sc[:, :, None] + self.beta[None, None, :]).masked_fill(~valid[:, :, None], float('-inf'))
            tutti = torch.cat([self.pf(hs), lg.reshape(lg.shape[0], -1)], 1)
            lp = F_.log_softmax(tutti, 1)
            return lp[:, 0], lp[:, 1:].reshape(lg.shape)

        def nll(self, out, Y, Mk, pw):
            """Somma dei -log P (in nat) dei segni da indovinare del tratto, e quanti sono. Con M5 e' la miscela a livello di parola."""
            self.ultimo = None
            lp = F_.log_softmax(out['logits'], -1)
            tl = lp.gather(2, Y[..., None])[..., 0] * Mk
            ntok = float(Mk.sum())
            if pw is None or pw['J'] == 0:
                return -tl.sum(), ntok
            B = tl.shape[0]
            cs = torch.cat([torch.zeros(B, 1, dtype=torch.float64), torch.cumsum(tl.double(), 1)], 1)     # somma cumulata in doppia precisione: i bit di una parola sono la differenza di due numeri grandi
            rows, s0, e0 = pw['rows'], pw['s0'], pw['e0']
            Lfree = (cs[rows, e0 + 1] - cs[rows, s0]).float()
            hs = out['hd'][rows, s0]
            lpf, lpp = self.puntatore(hs, pw['Fc'], pw['valid'])
            lg2 = out['logits'][rows, e0][:, [self.cfg['SP'], self.cfg['EOL']]]
            logr = F_.log_softmax(lg2, -1).gather(1, pw['term'][:, None])[:, 0]
            lsub, lins = self.tabelle()
            pj, pt, pc, px, pn = pw['pj'], pw['pt'], pw['pc'], pw['px'], pw['pn']
            lsp = torch.zeros(pj.shape[0])
            m1, m2, m3 = pt == 1, pt == 2, pt == 3
            lsp = lsp + torch.where(m1, lsub[pc.clamp(max=self.U - 1), px.clamp(max=self.U - 1)] - torch.log(pn), torch.zeros(()))
            lsp = lsp + torch.where(m2, lins[pc, px.clamp(max=self.U - 1)] - torch.log(pn), torch.zeros(()))
            lsp = lsp + torch.where(m3, -torch.log(pn), torch.zeros(()))
            lpi = lpp[pj, pw['pk'], pt]
            cp = torch.exp(lpi + lsp)
            Acopia = torch.zeros(pw['J']).index_add(0, pj, cp)
            lcop = torch.where(Acopia > 0, torch.log(Acopia.clamp(min=1e-38)) + logr, torch.full_like(logr, float('-inf')))
            tot = torch.logaddexp(lpf + Lfree, lcop)
            self.ultimo = dict(tot=tot.detach(), lcop=lcop.detach(), lpf=lpf.detach(), Acopia=Acopia.detach())    # per le prove e per `massa_copia`
            return -tot.sum(), ntok

    m = Modello(cfg)
    return m


def a_torch(bt, passo):
    """Dai numpy ai tensori."""
    import torch
    t = dict(lin=torch.as_tensor(bt['lin']), pos=torch.as_tensor(bt['pos']))
    if passo >= 3:
        t['F'] = torch.as_tensor(bt['F'])
    if passo >= 4:
        t['W'] = torch.as_tensor(bt['W'])
        t['NUM'] = torch.as_tensor(bt['NUM'])
    X, Y, Mk = torch.as_tensor(bt['X']), torch.as_tensor(bt['Y']), torch.as_tensor(bt['Mk'])
    pw = None
    if 'parole' in bt:
        p = bt['parole']
        pw = dict(J=p['J'], rows=torch.as_tensor(p['rows']), s0=torch.as_tensor(p['s0']), e0=torch.as_tensor(p['e0']), term=torch.as_tensor(p['term']),
                  Fc=torch.as_tensor(p['Fc']), valid=torch.as_tensor(p['valid']), pj=torch.as_tensor(p['pj']), pk=torch.as_tensor(p['pk']),
                  pt=torch.as_tensor(p['pt']), pc=torch.as_tensor(p['pc']), px=torch.as_tensor(p['px']), pn=torch.as_tensor(p['pn']))
    return X, Y, Mk, t, pw


# ---------------------------------------------------------------- passare da un tratto al successivo e valutare

class StatoRiga:
    """Quel che una pagina porta da un tratto al successivo (senza gradiente): stati dei due strati e memoria dell'attenzione."""
    __slots__ = ('h1', 'h2', 'mem')

    def __init__(self):
        self.h1 = self.h2 = self.mem = None


def passa_tratto(m, ctx, righe, stati, addestra=False, opt=None, scala=None):
    """Un tratto per ogni pagina di `righe` ([(P, (a, c))]); `stati`: lista di StatoRiga (una per pagina, aggiornata qui). Restituisce
    (somma -log P in nat, numero di segni). Con `addestra` fa il passo dell'ottimizzatore."""
    import torch
    import torch.nn as nn
    bt = lotto_tratto(righe, ctx, m.passo)
    X, Y, Mk, t, pw = a_torch(bt, m.passo)
    B, L = X.shape
    H = m.H
    h1 = torch.stack([s.h1 if s.h1 is not None else torch.zeros(H) for s in stati])[None]
    h2 = torch.stack([s.h2 if s.h2 is not None else torch.zeros(H) for s in stati])[None]
    mem = None
    if m.passo >= 2 and any(s.mem is not None for s in stati):
        Pm = max(s.mem[0].shape[0] for s in stati if s.mem is not None)
        mu = torch.zeros(B, Pm, H)
        ml = torch.full((B, Pm), -99, dtype=torch.long)
        mp = torch.full((B, Pm), -10 ** 6, dtype=torch.long)
        for b, s in enumerate(stati):
            if s.mem is not None:
                n = s.mem[0].shape[0]
                mu[b, :n], ml[b, :n], mp[b, :n] = s.mem[0], s.mem[1], s.mem[2]
        mem = (mu, ml, mp)
    if addestra:
        out = m(X, t, h1, h2, mem)
        nll, ntok = m.nll(out, Y, Mk, pw)
        if ntok > 0:
            loss = nll / ntok
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
            opt.step()
    else:
        with torch.no_grad():
            out = m(X, t, h1, h2, mem)
            nll, ntok = m.nll(out, Y, Mk, pw)
    with torch.no_grad():
        lens = bt['lens']
        for b, s in enumerate(stati):
            n = int(lens[b])
            s.h1 = out['y1'][b, n - 1].detach().clone()
            s.h2 = out['y2'][b, n - 1].detach().clone()
            if m.passo >= 2:
                s.mem = (out['u'][b, :n].detach().clone(), t['lin'][b, :n].clone(), t['pos'][b, :n].clone())
    return float(nll.detach()), ntok


def bpc_pagine(m, ctx, pagine, lotto=16):
    """Bit per segno (segni, spazi e fine riga) sulle pagine date: pagine intere a tratti con lo stato che passa (equivale alla pagina intera)."""
    vecchio = m.training
    m.eval()
    tot = n = 0.0
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a:a + lotto]]
        stati = [StatoRiga() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            nl, nt = passa_tratto(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att])
            tot += nl
            n += nt
            r += 1
    m.train(vecchio)
    return tot / max(n, 1.0) / math.log(2)


def addestra_modello(cfg, ctx, add, val, seme, epoche_max, pazienza, epoche_fisse=None, messaggi=None):
    """Come ia07.addestra: lotti di LOTTO pagine ordinate per lunghezza con un po' di rumore, un passo per tratto, AdamW, taglio del
    gradiente; arresto anticipato sulla validazione (bit per segno), si tiene il migliore. Restituisce (modello, curva_val, curva_add,
    epoca_scelta)."""
    import torch
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci(cfg)
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    massimo = epoche_fisse or epoche_max
    curva_val, curva_add, migliore, stato_migliore = [], [], None, None
    inizio = time.time()
    for epoca in range(1, massimo + 1):
        chiavi = [P['Tin'] * (1 + 0.3 * u) for P, u in zip(add, rng.uniform(size=len(add)))]
        ordine = sorted(range(len(add)), key=lambda i: chiavi[i])
        lotti = [ordine[a:a + LOTTO] for a in range(0, len(ordine), LOTTO)]
        rng.shuffle(lotti)
        perdita = conti = 0.0
        for lotto in lotti:
            Ps = [add[i] for i in lotto]
            stati = [StatoRiga() for _ in Ps]
            r = 0
            while True:
                att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
                if not att:
                    break
                nl, nt = passa_tratto(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att], addestra=True, opt=opt)
                perdita += nl
                conti += nt
                r += 1
        curva_add.append(round(perdita / max(conti, 1) / math.log(2), 5))
        if val and not epoche_fisse:
            v = round(bpc_pagine(m, ctx, val), 5)
            curva_val.append(v)
            if migliore is None or v < migliore:
                migliore = v
                stato_migliore = {k: t.detach().clone() for k, t in m.state_dict().items()}
            if messaggi:
                messaggi('  epoca %d: addestramento %.4f, validazione %.4f (migliore %.4f), %.0f s' % (epoca, curva_add[-1], v, migliore, time.time() - inizio))
            if len(curva_val) - 1 - curva_val.index(min(curva_val)) >= pazienza:
                break
        elif messaggi:
            messaggi('  epoca %d: addestramento %.4f, %.0f s' % (epoca, curva_add[-1], time.time() - inizio))
    if stato_migliore is not None:
        m.load_state_dict(stato_migliore)
    scelta = (curva_val.index(min(curva_val)) + 1) if curva_val else massimo
    m.eval()
    return m, curva_val, curva_add, scelta


# ---------------------------------------------------------------- salvare e ricaricare

def salva_modello(m, percorso, segni, ctx, extra=None):
    import torch
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    torch.save(dict(stato=m.state_dict(), cfg=m.cfg, segni=list(segni), tipi=ctx.lista_tipi, extra=extra or {}), percorso + '.tmp')
    os.replace(percorso + '.tmp', percorso)


def carica_modello(percorso, voc):
    """-> (modello in modalita' di prova, ctx). Controlla che i simboli siano gli stessi."""
    import torch
    d = torch.load(percorso, weights_only=False)
    assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
    cfg = d['cfg']
    ctx = Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
    m = costruisci(cfg)
    m.load_state_dict(d['stato'])
    m.eval()
    return m, ctx


def cfg_completa(passo, voc, ctx, piccolo=False):
    c = configurazione(passo, ctx.V, piccolo)
    c.update(nf=ctx.nf, U=ctx.U, SP=ctx.SP, EOL=ctx.EOL, K=ctx.K, S=ctx.S)
    return c


# ---------------------------------------------------------------- scrivere segno per segno

class Penna20:
    """Il modello passo per passo (una pagina alla volta): tiene lo stato delle GRU, la memoria dell'attenzione, il vettore delle parole,
    i numeri della riga e le parole candidate. Il calcolo e' lo stesso del calcolo a tratti (stessi numeri a meno degli arrotondamenti)."""

    def __init__(self, m, ctx, capacita=6000):
        import torch
        self.m, self.ctx, self.torch = m, ctx, torch
        self.passo = m.passo
        self.cap = capacita
        h, d = m.cfg['att_h'], m.cfg['att_d']
        if self.passo >= 2:
            self.K = torch.zeros(capacita, h, d // h)
            self.Vv = torch.zeros(capacita, h, d // h)

    def apri(self):
        torch, ctx = self.torch, self.ctx
        self.h1 = self.h2 = None
        self.n = 0                       # posizione (segni dati alla pagina)
        self.linea = -1
        self.inizi = {}                  # numero di riga -> posizione del primo segno
        self.lin = []                    # numero di riga di ogni posizione
        self.somma = np.zeros(ctx.nf, np.float32)
        self.ncomp = 0
        self.w = self.sofar = 0
        self.bin = -1
        self.corrente = []               # glifi della parola in corso
        self.righe_parole = {}           # numero di riga -> lista di (unita, vettore)
        self.hd = None

    # ---- stato della riga dopo aver letto `tok` (come in prepara_pagina)
    def _aggiorna(self, tok):
        ctx = self.ctx
        if tok in ctx.Tset:
            self.linea += 1
            self.w = self.sofar = 0
            self.bin = -1
            self.corrente = []
            self.inizi[self.linea] = self.n
            self.righe_parole[self.linea] = []
        elif ctx.N0 <= tok < ctx.N0 + ctx.nbins:
            self.bin = tok - ctx.N0
        elif tok == ctx.SP or tok == ctx.EOL:
            if self.corrente:
                un = tuple(self.corrente)
                f = feat_parola(un, ctx)
                self.somma += f
                self.ncomp += 1
                self.righe_parole.setdefault(self.linea, []).append((un, f))
                self.corrente = []
            if tok == ctx.SP:
                self.w += 1
                self.sofar += 1
        elif tok >= ctx.u0:
            self.sofar += 1
            self.corrente.append(tok - ctx.u0)

    def dai(self, tok):
        """Un segno in ingresso; restituisce i logit (V) del prossimo e tiene lo stato d'uscita in self.hd."""
        torch, m, ctx = self.torch, self.m, self.ctx
        tok = int(tok)
        self._aggiorna(tok)
        with torch.inference_mode():
            parti = [m.emb(torch.tensor(tok))]
            if self.passo >= 3:
                f = np.zeros(ctx.nf + 1, np.float32)
                f[:ctx.nf] = self.somma / max(self.ncomp, 1)
                f[ctx.nf] = math.log1p(self.ncomp) / 6.0
                parti.append(torch.from_numpy(f) @ m.Wp)
            if self.passo >= 4:
                inl = self.bin >= 0
                bi = max(self.bin, 0)
                num = np.array([np.clip((ctx.lo[bi] - self.sofar) / 40.0, -1.0, 2.0) if inl else 0.0,
                                np.clip((ctx.hi[bi] - self.sofar) / 40.0, -1.0, 3.0) if inl else 0.0,
                                1.0 if (inl and self.w == 0) else 0.0, 1.0 if inl else 0.0], np.float32)
                parti += [m.wemb(torch.tensor(min(self.w, NW - 1))), torch.from_numpy(num)]
            x = torch.cat(parti)[None, None, :]
            y1, h1 = m.gru1(x, self.h1)
            self.h1 = h1
            u = y1[0, 0]
            if self.passo >= 2:
                hh, d = m.cfg['att_h'], m.cfg['att_d']
                dh = d // hh
                t = self.n
                self.K[t] = m.ak(u).view(hh, dh)
                self.Vv[t] = m.av(u).view(hh, dh)
                self.lin.append(self.linea)
                lo = self.inizi.get(self.linea - 1, 0) if self.linea >= 1 else 0
                q = m.aq(u).view(hh, dh)
                Ks, Vs = self.K[lo:t + 1], self.Vv[lo:t + 1]
                dist = (t - torch.arange(lo, t + 1)).to(torch.float32)
                sc = torch.einsum('hd,nhd->hn', q, Ks) / math.sqrt(dh) - m.pend[:, None] * dist[None, :]
                p = torch.softmax(sc, -1)
                o = torch.einsum('hn,nhd->hd', p, Vs).reshape(d)
                u2 = u + m.ao(o)
            else:
                u2 = u
            y2, h2 = m.gru2(u2[None, None, :], self.h2)
            self.h2 = h2
            self.hd = y2[0, 0]
            self.n += 1
            return m.out(self.hd).tolist()

    # ---- puntatore (M5): scelta a inizio parola
    def candidati(self):
        """Parole candidate (le piu' recenti della riga in corso, poi quelle della riga sopra): lista di (unita, vettore)."""
        cur = self.righe_parole.get(self.linea, [])[::-1]
        sopra = self.righe_parole.get(self.linea - 1, [])[::-1]
        return (cur + sopra)[:self.ctx.S]

    def puntatore(self, cand):
        """Probabilita' (pi_libero, pi[s, tipo]) a inizio parola con i candidati `cand` (numpy)."""
        torch, m, ctx = self.torch, self.m, self.ctx
        S = ctx.S
        Fc = np.zeros((1, S, ctx.nf), np.float32)
        valid = np.zeros((1, S), bool)
        for k, (un, f) in enumerate(cand):
            Fc[0, k] = f
            valid[0, k] = True
        with torch.inference_mode():
            lpf, lpp = m.puntatore(self.hd[None, :], torch.from_numpy(Fc), torch.from_numpy(valid))
        return float(lpf.exp()), lpp[0].exp().numpy()

    def tabelle_ritocco(self):
        with self.torch.inference_mode():
            lsub, lins = self.m.tabelle()
        return lsub.exp().numpy(), lins.exp().numpy()


def campiona_ritocco(un, tipo, psub, pins, rng):
    """Una parola (tuple di glifi) ottenuta da `un` con il ritocco `tipo` (0 uguale, 1 cambia, 2 aggiunge, 3 toglie); posizione a caso,
    glifo dalle tabelle imparate. None se il ritocco non e' possibile (toglie da una parola di un glifo)."""
    n = len(un)
    if tipo == 0:
        return tuple(un)
    if tipo == 1:
        i = int(rng.integers(0, n))
        p = psub[un[i]]
        x = int(rng.choice(len(p), p=p / p.sum()))
        return tuple(un[:i]) + (x,) + tuple(un[i + 1:])
    if tipo == 2:
        i = int(rng.integers(0, n + 1))
        ctxg = un[i - 1] if i > 0 else len(psub)
        p = pins[ctxg]
        x = int(rng.choice(len(p), p=p / p.sum()))
        return tuple(un[:i]) + (x,) + tuple(un[i:])
    if n < 2:
        return None
    i = int(rng.integers(0, n))
    return tuple(un[:i]) + tuple(un[i + 1:])


# ---------------------------------------------------------------- testi sintetici (controlli: solo disposizione e frequenze del libro dato)

def sintetico(righe, seme, divisore, unita, eco=0.0, ritocco=0.5, tema=0.0, n_tema=25, bordi=0.0):
    """Una copia del libro (`righe`: dizionari come ia07.libro_vero()) con le stesse righe e lunghezze, parole pescate dalla frequenza del
    vocabolario del libro, e ingredienti piantati:
    - `eco`: ogni parola, con questa probabilita', e' una parola della riga sopra (a caso), con un ritocco (un glifo cambiato, aggiunto o tolto, in parti uguali) con
      probabilita' `ritocco`;
    - `tema`: ogni pagina ha `n_tema` parole sue; con questa probabilita' la parola e' una di queste;
    - `bordi`: con questa probabilita' la prima parola della riga e' una di 6 parole d'inizio riga fisse e l'ultima una di 6 d'ultima riga fisse.
    Restituisce la nuova lista di righe."""
    rng = random.Random(seme)
    import bisect
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    def modifica(w):
        u = divisore(w)
        for _ in range(12):
            tp = rng.choice((1, 2, 3))
            if tp == 1:
                i = rng.randrange(len(u))
                nuovo = rng.choice(unita)
                if nuovo == u[i]:
                    continue
                u2 = list(u)
                u2[i] = nuovo
            elif tp == 2:
                i = rng.randrange(len(u) + 1)
                u2 = list(u[:i]) + [rng.choice(unita)] + list(u[i:])
            else:
                if len(u) < 2:
                    continue
                i = rng.randrange(len(u))
                u2 = list(u[:i]) + list(u[i + 1:])
            w2 = ''.join(u2)
            if w2 != w and divisore(w2) == u2:
                return w2
        return w

    prime = [fresca() for _ in range(6)]
    ultime = [fresca() for _ in range(6)]
    out, pagina_corr, sopra, topici = [], None, None, []
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, sopra, topici = x['pagina'], None, [fresca() for _ in range(n_tema)]
        n = len(x['parole'])
        ps = []
        for k in range(n):
            if bordi and k == 0 and rng.random() < bordi:
                w = rng.choice(prime)
            elif bordi and k == n - 1 and n > 1 and rng.random() < bordi:
                w = rng.choice(ultime)
            elif eco and sopra and rng.random() < eco:
                w = rng.choice(sopra)
                if rng.random() < ritocco:
                    w = modifica(w)
            elif tema and rng.random() < tema:
                w = rng.choice(topici)
            else:
                w = fresca()
            ps.append(w)
        sopra = ps
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out


def massa_copia(m, ctx, pagine, lotto=16):
    """Solo M5. Su `pagine` (tenute fuori): (a) massa di copia media a inizio parola, 1 - pi_libero, su tutte le parole; (b) quota a posteriori della
    strada "copia" (P(copia e parola) / P(parola)) sulle parole che hanno almeno un candidato compatibile ("copiabili") e sulle altre; (c) quota di
    parole copiabili. Restituisce un dizionario di numeri."""
    import torch
    assert m.passo >= 5
    vecchio = m.training
    m.eval()
    mass, post_c, post_n, ncop, n = [], [], [], 0, 0
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a:a + lotto]]
        stati = [StatoRiga() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            righe = [(Ps[b], Ps[b]['chunks'][r]) for b in att]
            passa_tratto(m, ctx, righe, [stati[b] for b in att])
            u = m.ultimo
            if u is not None and u['tot'].numel():
                post = torch.exp(u['lcop'] - u['tot'])
                copiabile = u['Acopia'] > 0
                mass += (1.0 - torch.exp(u['lpf'])).tolist()
                post_c += post[copiabile].tolist()
                post_n += post[~copiabile].tolist()
            r += 1
    m.train(vecchio)
    tot = len(post_c) + len(post_n)
    f = lambda x: float(np.mean(x)) if x else None
    return dict(massa_media=f(mass), posteriori_copiabili=f(post_c), posteriori_altre=f(post_n), quota_copiabili=len(post_c) / max(tot, 1), parole=tot)
