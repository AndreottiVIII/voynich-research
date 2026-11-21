# -*- coding: utf-8 -*-
"""Supporto di ia22 (modulo, non e' un esperimento): imitatori con l'eco della pagina e il legame fra parole.

Che cosa c'e' qui, in parole semplici
- Quattro imitatori a segni (E0-E3), tutti costruiti sulla GRU 2 x 256 di M1 (ia20: niente attenzione, niente vettore di pagina, niente posizione
  nella riga) perche' M1 e' l'unico gradino di ia20 che ha il contatto fra parole e l'ordine delle famiglie (D) al vero. Ognuno aggiunge l'eco
  della pagina in un modo che NON tocca la GRU:
    E1  prodotto di esperti a livello di segno: logit della GRU + beta * log(1 + somma delle parole d'eco che continuano il prefisso, anche
        con un ritocco gia' fatto o da fare). Normalizzazione esatta per segno (softmax su tutti i simboli). La GRU decide il primo glifo
        (contatto); l'eco spinge soltanto, con pesi imparati per tipo di corrispondenza e per posto nella parola.
    E0  riferimento: il puntatore "copia e ritocco" di M5 (miscela esatta a livello di parola) ma sulla base M1 (senza il resto di M2-M4).
    E2  E0 con il puntatore vincolato al contatto: il peso di copiare la parola j e' moltiplicato (in scala logaritmica, con un esponente
        imparato) per la probabilita' che la GRU da' ai primi due glifi di j dopo la parola prima (secondo glifo con un passo in avanti della GRU).
    E3  E0 piu' tre strade di "copia con inizio rigenerato": si copia la parola d'eco ma il primo glifo, o i primi due, li riscrive la GRU
        (quindi col contatto); oppure si mette davanti un glifo nuovo scritto dalla GRU. La quota di ogni strada e' imparata.
- L'addestramento e' quello di ia20 (stesse pieghe, stessi tratti che finiscono a fine riga, stesso arresto anticipato), copiato qui senza
  l'attenzione e la memoria dei tratti.
- Scrittura segno per segno (`Penna22`) uguale al calcolo a tratti; testi sintetici con eco E contatto piantati (`sintetico_eco_contatto`).
Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import random
import time
import bisect
from collections import Counter, OrderedDict

import numpy as np

import gradini_modelli as GM

# ---------------------------------------------------------------- costanti (fissate nella preregistrazione)

TIPI = ('E0', 'E1', 'E2', 'E3')
NT_PUNT = dict(E0=4, E2=4, E3=7)     # strade del puntatore per candidato: 0 uguale, 1 cambia, 2 aggiunge, 3 toglie (+ E3: 4 primo glifo riscritto, 5 glifo nuovo davanti, 6 primi due riscritti)
NTAU = 5                             # E1: tipi di corrispondenza (0 uguale fin qui, 1 dopo un ritocco, 2 salta un glifo, 3 fine parola uguale, 4 fine dopo un ritocco)
NBK = 3                              # E1: posto nella parola (primo glifo, secondo, dopo)
VERSIONE = 'echi-1'
REC_INIT = math.log(math.e - 1.0)    # softplus(REC_INIT) = 1


def configurazione(tipo, V, piccolo=False):
    c = GM.configurazione(1, V, piccolo)
    c['tipo'] = tipo
    c['versione'] = VERSIONE
    return c


def cfg_completa(tipo, voc, ctx, piccolo=False):
    c = configurazione(tipo, ctx.V, piccolo)
    c.update(nf=ctx.nf, U=ctx.U, SP=ctx.SP, EOL=ctx.EOL, K=ctx.K, S=ctx.S, u0=ctx.u0, nt=NT_PUNT.get(tipo, 0))
    return c


# ---------------------------------------------------------------- corrispondenza di una parola d'eco con il prefisso (E1)

def avanza(st, c, x):
    """Stati (i, e) dell'allineamento del prefisso con la parola d'eco `c` dopo il glifo `x`: i = glifi di `c` consumati, e = ritocchi usati (0 o 1)."""
    n = len(c)
    nuovo = set()
    for (i, e) in st:
        if i < n and c[i] == x:
            nuovo.add((i + 1, e))
        if e == 0:
            if i < n and c[i] != x:
                nuovo.add((i + 1, 1))            # un glifo cambiato
            nuovo.add((i, 1))                    # un glifo aggiunto (x)
            if i + 1 < n and c[i + 1] == x:
                nuovo.add((i + 2, 1))            # un glifo tolto (c[i]) e poi x
    return nuovo


def spinte(c, l, st):
    """(tipo, s) che gli stati `st` danno al segno dopo un prefisso di lunghezza `l`: s = indice di glifo oppure -1 (= fine parola, spazio o fine riga)."""
    n = len(c)
    out = set()
    for (i, e) in st:
        if i < n:
            out.add((0 if e == 0 else 1, c[i]))
        if e == 0 and i + 1 < n:
            out.add((2, c[i + 1]))
        if l >= 1:
            if i == n:
                out.add((3 if e == 0 else 4, -1))
            elif e == 0 and i == n - 1:
                out.add((4, -1))
    return out


def spinte_prefisso(c, p):
    """Come sopra ma per un prefisso `p` dato per intero (usato dalla scrittura)."""
    st = {(0, 0)}
    for x in p:
        st = avanza(st, c, x)
        if not st:
            return set()
    return spinte(c, len(p), st)


_MEMO = {}


def spinte_parola(w, c):
    """Per ogni lunghezza di prefisso l = 0..len(w) di `w`, la lista (tipo, s) che la parola d'eco `c` da' al segno dopo. Con memoria."""
    k = (c, w)
    r = _MEMO.get(k)
    if r is None:
        r = []
        st = {(0, 0)}
        for l in range(len(w) + 1):
            if l > 0:
                st = avanza(st, c, w[l - 1]) if st else st
            r.append(sorted(spinte(c, l, st)) if st else [])
        if len(_MEMO) > 300000:
            _MEMO.clear()
        _MEMO[k] = r
    return r


def scripts_rigenerati(c, w):
    """Strade di E3 che portano da `c` a `w`: 4 = primo glifo riscritto (stessa lunghezza, resto uguale), 5 = glifo nuovo davanti (w = x + c),
    6 = primi due glifi riscritti (stessa lunghezza, almeno 2, resto uguale)."""
    out = []
    lc, lw = len(c), len(w)
    if lw == lc and lc >= 1 and w[1:] == c[1:]:
        out.append(4)
    if lw == lc + 1 and w[1:] == c:
        out.append(5)
    if lw == lc and lc >= 2 and w[2:] == c[2:]:
        out.append(6)
    return out


# ---------------------------------------------------------------- pagine preparate per i tipi E

def prepara_pagina(d, ctx, tipo):
    """Dati fissi di una pagina (`d`: dizionario con almeno tok, linea, nome). Come GM.prepara_pagina per M1/M5 ma senza i vettori per segno; per E1 le
    corrispondenze d'eco, per gli altri candidati e strade del puntatore."""
    tok = np.asarray(d['tok'], dtype=np.int64)
    linea = np.asarray(d['linea'], dtype=np.int64)
    T, Tin = len(tok), len(tok) - 1
    tk = [int(x) for x in tok]
    u0, SP = ctx.u0, ctx.SP
    words = GM.parole_di_tok(tok, ctx)
    nw = len(words)
    units = [tuple(tk[s + j] - u0 for j in range(e - s)) for s, e in words]
    wl = [int(linea[s]) for s, e in words]
    per_riga = {}
    for j, l in enumerate(wl):
        per_riga.setdefault(l, []).append(j)
    cand = np.full((nw, ctx.S), -1, np.int16)
    for j in range(nw):
        l = wl[j]
        lst = ([k for k in per_riga[l] if k < j][::-1] + per_riga.get(l - 1, [])[::-1])[:ctx.S]
        cand[j, :len(lst)] = lst
    P = dict(nome=d['nome'], tok=tok, linea=linea, T=T, Tin=Tin, words=words, units=units, nw=nw, cand=cand, chunks=GM.tagli_riga(tok, ctx),
             ws0=np.array([s - 1 for s, e in words], np.int64), we0=np.array([e - 1 for s, e in words], np.int64),
             wterm=np.array([0 if tk[e] == SP else 1 for s, e in words], np.int64))
    if tipo == 'E1':
        bk = np.full(Tin, NBK, np.int64)
        ft, fk, ftau, fs = [], [], [], []
        for j, (s, e) in enumerate(words):
            w = units[j]
            cj = [units[k] for k in cand[j] if k >= 0]
            for l in range(len(w) + 1):
                t = s - 1 + l
                if t < Tin:
                    bk[t] = min(l, NBK - 1)
            for k, c in enumerate(cj):
                per = spinte_parola(w, c)
                for l in range(len(w) + 1):
                    t = s - 1 + l
                    if t >= Tin:
                        continue
                    for (tau, sg) in per[l]:
                        ft.append(t)
                        fk.append(k)
                        ftau.append(tau)
                        fs.append(sg)
        o = np.argsort(np.array(ft, np.int64), kind='stable') if ft else np.zeros(0, np.int64)
        P.update(bk=bk, ft=np.array(ft, np.int32)[o], fk=np.array(fk, np.int8)[o], ftau=np.array(ftau, np.int8)[o], fs=np.array(fs, np.int16)[o])
    else:
        pj, pk, pt, pc, px, pn = [], [], [], [], [], []
        for j in range(nw):
            for k in range(ctx.S):
                cj = int(cand[j, k])
                if cj < 0:
                    break
                for (t_, cx, x_, n_) in GM.scripts(units[cj], units[j], ctx.U):
                    pj.append(j), pk.append(k), pt.append(t_), pc.append(cx), px.append(x_), pn.append(n_)
                if tipo == 'E3':
                    for t_ in scripts_rigenerati(units[cj], units[j]):
                        pj.append(j), pk.append(k), pt.append(t_), pc.append(0), px.append(0), pn.append(1.0)
        cu0 = np.full((nw, ctx.S), -1, np.int16)
        cu1 = np.full((nw, ctx.S), -1, np.int16)
        for j in range(nw):
            for k in range(ctx.S):
                cj = int(cand[j, k])
                if cj < 0:
                    break
                u = units[cj]
                cu0[j, k] = u[0]
                cu1[j, k] = u[1] if len(u) > 1 else -2        # -2: parola di un glifo (il secondo "segno" e' la fine parola)
        P.update(pj=np.array(pj, np.int64), pk=np.array(pk, np.int64), pt=np.array(pt, np.int64), pc=np.array(pc, np.int64), px=np.array(px, np.int64),
                 pn=np.array(pn, np.float32), cu0=cu0, cu1=cu1)
    return P


def prepara_insiemi(insiemi, ctx, tipo):
    """`insiemi`: liste di liste di pagine (dizionari). Restituisce le liste di pagine preparate; per i tipi con puntatore costruisce la tabella dei
    vettori delle parole (una riga per parola distinta: ctx.FM) e il vettore `wt` (riga di ogni parola) di ogni pagina."""
    out = [[prepara_pagina(d, ctx, tipo) for d in ins] for ins in insiemi]
    if tipo != 'E1':
        tid, righe = {}, []
        for ins in out:
            for P in ins:
                wt = np.zeros(P['nw'], np.int64)
                for j, u in enumerate(P['units']):
                    i = tid.get(u)
                    if i is None:
                        i = tid[u] = len(righe)
                        righe.append(GM.feat_parola(u, ctx))
                    wt[j] = i
                P['wt'] = wt
        ctx.FM = np.stack(righe) if righe else np.zeros((1, ctx.nf), np.float32)
    return out


# ---------------------------------------------------------------- un lotto: un tratto per ogni pagina ancora attiva

def lotto_tratto(righe, ctx, tipo):
    bt = GM.lotto_tratto(righe, ctx, 1)
    B, L = bt['B'], bt['L']
    if tipo == 'E1':
        bk = np.full((B, L), NBK, np.int64)
        bi, ti, kk, tau, ss = [], [], [], [], []
        for b, (P, (a, c)) in enumerate(righe):
            n = c - a
            bk[b, :n] = P['bk'][a:c]
            lo, hi = np.searchsorted(P['ft'], [a, c], side='left')
            if hi > lo:
                bi.append(np.full(hi - lo, b, np.int64))
                ti.append(P['ft'][lo:hi].astype(np.int64) - a)
                kk.append(P['fk'][lo:hi].astype(np.int64))
                tau.append(P['ftau'][lo:hi].astype(np.int64))
                ss.append(P['fs'][lo:hi].astype(np.int64))
        cat = lambda l: np.concatenate(l) if l else np.zeros(0, np.int64)
        bi, ti, kk, tau, ss = cat(bi), cat(ti), cat(kk), cat(tau), cat(ss)
        term = ss < 0                                     # la fine parola e' spazio O fine riga: due segni
        tok = np.where(term, ctx.SP, ctx.u0 + ss)
        bi2, ti2, kk2, tau2 = bi[term], ti[term], kk[term], tau[term]
        bt['eco'] = dict(bk=bk, bi=np.concatenate([bi, bi2]), ti=np.concatenate([ti, ti2]), k=np.concatenate([kk, kk2]), tau=np.concatenate([tau, tau2]),
                         s=np.concatenate([tok, np.full(len(bi2), ctx.EOL, np.int64)]))
        return bt
    rows, s0, e0, term, Fc, valid, c0, c1, wtc = [], [], [], [], [], [], [], [], []
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
        wtc.append(P['wt'][np.maximum(cd, 0)])
        c0.append(P['cu0'][j0:j1].astype(np.int64))
        c1.append(P['cu1'][j0:j1].astype(np.int64))
        lo = int(np.searchsorted(P['pj'], j0, side='left'))
        hi = int(np.searchsorted(P['pj'], j1, side='left'))
        pj.append(P['pj'][lo:hi] - j0 + J0)
        pk.append(P['pk'][lo:hi]), pt.append(P['pt'][lo:hi]), pc.append(P['pc'][lo:hi]), px.append(P['px'][lo:hi]), pn.append(P['pn'][lo:hi])
        J0 += nj
    cat = lambda l, dt, shp=(): np.concatenate(l) if l else np.zeros((0,) + shp, dt)
    S = ctx.S
    validc = cat(valid, bool, (S,))
    wt = cat(wtc, np.int64, (S,))
    d = dict(rows=np.array(rows, np.int64), s0=cat(s0, np.int64), e0=cat(e0, np.int64), term=cat(term, np.int64),
             Fc=(ctx.FM[wt] * validc[..., None]).astype(np.float32) if J0 else np.zeros((0, S, ctx.nf), np.float32), valid=validc,
             pj=cat(pj, np.int64), pk=cat(pk, np.int64), pt=cat(pt, np.int64), pc=cat(pc, np.int64), px=cat(px, np.int64), pn=cat(pn, np.float32), J=J0,
             c0=cat(c0, np.int64, (S,)), c1=cat(c1, np.int64, (S,)))
    if tipo == 'E2' and J0:
        jj, kk = np.nonzero(validc)
        key = jj * ctx.U + d['c0'][jj, kk]
        uk, inv = np.unique(key, return_inverse=True)
        po = np.full((J0, S), -1, np.int64)
        po[jj, kk] = inv
        d.update(pair_j=uk // ctx.U, pair_g=uk % ctx.U, pair_of=po)
    bt['parole'] = d
    return bt


# ---------------------------------------------------------------- il modello

def costruisci(cfg):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F_

    class Modello(nn.Module):
        def __init__(self, cfg):
            super().__init__()
            self.cfg = dict(cfg)
            self.tipo = cfg['tipo']
            self.passo = 1                         # per `Penna20` e per le funzioni di ia20: base M1
            V, H = cfg['V'], cfg['nasc']
            self.H = H
            self.emb = nn.Embedding(V, cfg['emb'])
            self.gru1 = nn.GRU(cfg['emb'], H, 1, batch_first=True)
            self.gru2 = nn.GRU(H, H, 1, batch_first=True)
            self.caduta = nn.Dropout(cfg['caduta'])
            self.out = nn.Linear(H, V)
            S = cfg['S']
            self.S = S
            if self.tipo == 'E1':
                self.rec1 = nn.Parameter(torch.full((S,), REC_INIT))
                self.bet = nn.Parameter(torch.zeros(NTAU, NBK + 1))        # l'ultima colonna (fuori parola) non conta: li' la spinta e' zero
            else:
                U, dk, nt = cfg['U'], cfg['dk'], cfg['nt']
                self.U = U
                self.pq = nn.Linear(H, dk)
                self.pf = nn.Linear(H, 1)
                nn.init.constant_(self.pf.bias, 2.0)
                self.Wc = nn.Parameter(torch.randn(cfg['nf'], dk) * 0.05)
                self.rec = nn.Parameter(torch.zeros(S))
                self.beta = nn.Parameter(torch.tensor([-3.0] + [-4.0] * (nt - 1)))
                self.Tsub = nn.Parameter(torch.zeros(U, U))
                self.Tins = nn.Parameter(torch.zeros(U + 1, U))
                if self.tipo == 'E2':
                    self.gam = nn.Parameter(torch.zeros(1))

        # ---- E1: spinta dell'eco sui logit
        def bonus(self, eco, B, L, V):
            w = F_.softplus(self.rec1)
            idx = ((eco['bi'] * L + eco['ti']) * NTAU + eco['tau']) * V + eco['s']
            N = torch.zeros(B * L * NTAU * V).index_add_(0, idx, w[eco['k']]).view(B, L, NTAU, V)
            b = self.bet[:, eco['bk']].permute(1, 2, 0)[..., None]          # (B, L, NTAU, 1)
            return (b * torch.log1p(N)).sum(2)

        def forward(self, X, bt, h1=None, h2=None):
            y1, _ = self.gru1(self.emb(X), h1)
            u = self.caduta(y1)
            y2, _ = self.gru2(u, h2)
            hd = self.caduta(y2)
            lg = self.out(hd)
            if self.tipo == 'E1' and bt.get('eco') is not None:
                lg = lg + self.bonus(bt['eco'], X.shape[0], X.shape[1], lg.shape[-1])
            return dict(logits=lg, hd=hd, y1=y1, y2=y2)

        # ---- puntatore (E0, E2, E3)
        def tabelle(self):
            U = self.U
            d = torch.full((U, U), 0.0)
            d.fill_diagonal_(float('-inf'))
            return F_.log_softmax(self.Tsub + d, 1), F_.log_softmax(self.Tins, 1)

        def puntatore(self, hs, Fc, valid, logg=None):
            """hs (J, H); Fc (J, S, nf); valid (J, S); logg (J, S) o None (E2). -> (log pi_libero (J,), log pi (J, S, nt))."""
            q = self.pq(hs)
            enc = torch.matmul(Fc, self.Wc)
            sc = (q[:, None, :] * enc).sum(-1) / math.sqrt(self.cfg['dk']) + self.rec[None, :]
            if self.tipo == 'E2' and logg is not None:
                sc = sc + self.gam * logg
            lg = (sc[:, :, None] + self.beta[None, None, :]).masked_fill(~valid[:, :, None], float('-inf'))
            tutti = torch.cat([self.pf(hs), lg.reshape(lg.shape[0], -1)], 1)
            lp = F_.log_softmax(tutti, 1)
            return lp[:, 0], lp[:, 1:].reshape(lg.shape)

        def avanti_glifi(self, y1, y2, glifi):
            """Un passo in avanti della GRU dallo stato (y1, y2) (N, H) dando il glifo `glifi` (N,) (indici di unita'): logit (N, V). Senza gradiente."""
            u0 = self.cfg['u0']
            x = self.emb(glifi + u0)[:, None, :]
            a, _ = self.gru1(x, y1[None])
            b, _ = self.gru2(a, y2[None])
            return self.out(b[:, 0])

        def logg_candidati(self, lp_first, y1, y2, pw):
            """log della probabilita' che la GRU da' ai primi due glifi di ogni candidato (J, S): primo dal logit gia' calcolato, secondo (o la fine parola
            se la parola ha un solo glifo) da un passo in avanti. Senza gradiente."""
            u0, SP, EOL = self.cfg['u0'], self.cfg['SP'], self.cfg['EOL']
            valid = pw['valid']
            c0 = pw['c0'].clamp(min=0)
            l1 = lp_first.gather(1, c0 + u0)
            with torch.no_grad():
                pj, pg = pw['pair_j'], pw['pair_g']
                lg2 = self.avanti_glifi(y1[pj], y2[pj], pg)
                lp2 = F_.log_softmax(lg2, -1)                                         # (Np, V)
                po = pw['pair_of'].clamp(min=0)
                c1 = pw['c1']
                gl = lp2[po, (c1.clamp(min=0) + u0)]
                fine = torch.logaddexp(lp2[po, SP], lp2[po, EOL])
                l2 = torch.where(c1 == -2, fine, gl)
            return torch.where(valid, l1 + l2, torch.zeros(()))

        def nll(self, out, Y, Mk, pw):
            """Somma dei -log P (nat) dei segni da indovinare del tratto e quanti sono. Con il puntatore e' la miscela a livello di parola."""
            self.ultimo = None
            lp = F_.log_softmax(out['logits'], -1)
            tl = lp.gather(2, Y[..., None])[..., 0] * Mk
            ntok = float(Mk.sum())
            if self.tipo == 'E1' or pw is None or pw['J'] == 0:
                return -tl.sum(), ntok
            B = tl.shape[0]
            cs = torch.cat([torch.zeros(B, 1, dtype=torch.float64), torch.cumsum(tl.double(), 1)], 1)
            rows, s0, e0 = pw['rows'], pw['s0'], pw['e0']
            Lfree = (cs[rows, e0 + 1] - cs[rows, s0]).float()
            hs = out['hd'][rows, s0]
            logg = None
            if self.tipo == 'E2':
                logg = self.logg_candidati(lp[rows, s0].detach(), out['y1'][rows, s0].detach(), out['y2'][rows, s0].detach(), pw)
            lpf, lpp = self.puntatore(hs, pw['Fc'], pw['valid'], logg)
            lg2 = out['logits'][rows, e0][:, [self.cfg['SP'], self.cfg['EOL']]]
            logr = F_.log_softmax(lg2, -1).gather(1, pw['term'][:, None])[:, 0]
            lsub, lins = self.tabelle()
            pj, pt, pc, px, pn = pw['pj'], pw['pt'], pw['pc'], pw['px'], pw['pn']
            zero = torch.zeros(())
            lsp = torch.zeros(pj.shape[0])
            m1, m2, m3 = pt == 1, pt == 2, pt == 3
            lsp = lsp + torch.where(m1, lsub[pc.clamp(max=self.U - 1), px.clamp(max=self.U - 1)] - torch.log(pn), zero)
            lsp = lsp + torch.where(m2, lins[pc, px.clamp(max=self.U - 1)] - torch.log(pn), zero)
            lsp = lsp + torch.where(m3, -torch.log(pn), zero)
            if self.tipo == 'E3':
                t0 = tl[rows[pj], s0[pj]]
                t1 = tl[rows[pj], s0[pj] + 1]
                lsp = lsp + torch.where((pt == 4) | (pt == 5), t0, zero) + torch.where(pt == 6, t0 + t1, zero)
            lpi = lpp[pj, pw['pk'], pt]
            cp = torch.exp(lpi + lsp)
            Acopia = torch.zeros(pw['J']).index_add(0, pj, cp)
            lcop = torch.where(Acopia > 0, torch.log(Acopia.clamp(min=1e-38)) + logr, torch.full_like(logr, float('-inf')))
            tot = torch.logaddexp(lpf + Lfree, lcop)
            self.ultimo = dict(tot=tot.detach(), lcop=lcop.detach(), lpf=lpf.detach(), Acopia=Acopia.detach())
            return -tot.sum(), ntok

    return Modello(cfg)


def a_torch(bt, tipo):
    import torch
    X, Y, Mk = torch.as_tensor(bt['X']), torch.as_tensor(bt['Y']), torch.as_tensor(bt['Mk'])
    t, pw = {}, None
    if tipo == 'E1':
        t['eco'] = {k: torch.as_tensor(v) for k, v in bt['eco'].items()}
    else:
        p = bt['parole']
        pw = {k: (torch.as_tensor(v) if isinstance(v, np.ndarray) else v) for k, v in p.items()}
    return X, Y, Mk, t, pw


# ---------------------------------------------------------------- passare da un tratto al successivo e valutare

def passa_tratto(m, ctx, righe, stati, addestra=False, opt=None):
    """Un tratto per ogni pagina di `righe` ([(P, (a, c))]); `stati`: lista di GM.StatoRiga (h1, h2). -> (somma -log P in nat, numero di segni)."""
    import torch
    import torch.nn as nn
    bt = lotto_tratto(righe, ctx, m.tipo)
    X, Y, Mk, t, pw = a_torch(bt, m.tipo)
    H = m.H
    h1 = torch.stack([s.h1 if s.h1 is not None else torch.zeros(H) for s in stati])[None]
    h2 = torch.stack([s.h2 if s.h2 is not None else torch.zeros(H) for s in stati])[None]
    if addestra:
        out = m(X, t, h1, h2)
        nll, ntok = m.nll(out, Y, Mk, pw)
        if ntok > 0:
            loss = nll / ntok
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(m.parameters(), GM.TAGLIO)
            opt.step()
    else:
        with torch.no_grad():
            out = m(X, t, h1, h2)
            nll, ntok = m.nll(out, Y, Mk, pw)
    with torch.no_grad():
        lens = bt['lens']
        for b, s in enumerate(stati):
            n = int(lens[b])
            s.h1 = out['y1'][b, n - 1].detach().clone()
            s.h2 = out['y2'][b, n - 1].detach().clone()
    return float(nll.detach()), ntok


def bpc_pagine(m, ctx, pagine, lotto=16):
    vecchio = m.training
    m.eval()
    tot = n = 0.0
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a:a + lotto]]
        stati = [GM.StatoRiga() for _ in Ps]
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
    """Come GM.addestra_modello (e ia07.addestra): lotti di LOTTO pagine ordinate per lunghezza con un po' di rumore, un passo per tratto, AdamW, taglio del
    gradiente; arresto anticipato sulla validazione (bit per segno), si tiene il migliore. -> (modello, curva_val, curva_add, epoca_scelta)."""
    import torch
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci(cfg)
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=GM.LR, weight_decay=GM.DECADIMENTO)
    massimo = epoche_fisse or epoche_max
    curva_val, curva_add, migliore, stato_migliore = [], [], None, None
    inizio = time.time()
    for epoca in range(1, massimo + 1):
        chiavi = [P['Tin'] * (1 + 0.3 * u) for P, u in zip(add, rng.uniform(size=len(add)))]
        ordine = sorted(range(len(add)), key=lambda i: chiavi[i])
        lotti = [ordine[a:a + GM.LOTTO] for a in range(0, len(ordine), GM.LOTTO)]
        rng.shuffle(lotti)
        perdita = conti = 0.0
        for lotto in lotti:
            Ps = [add[i] for i in lotto]
            stati = [GM.StatoRiga() for _ in Ps]
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


def salva_modello(m, percorso, segni, ctx, extra=None):
    import torch
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    torch.save(dict(stato=m.state_dict(), cfg=m.cfg, segni=list(segni), tipi=ctx.lista_tipi, extra=extra or {}), percorso + '.tmp')
    os.replace(percorso + '.tmp', percorso)


def carica_modello(percorso, voc):
    """-> (modello in modalita' di prova, ctx). Il ctx non ha la tabella dei vettori delle parole (serve solo all'addestramento)."""
    import torch
    d = torch.load(percorso, weights_only=False)
    assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
    cfg = d['cfg']
    ctx = GM.Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
    m = costruisci(cfg)
    m.load_state_dict(d['stato'])
    m.eval()
    return m, ctx


def massa_copia(m, ctx, pagine, lotto=16):
    """Come GM.massa_copia ma per i tipi E con puntatore."""
    import torch
    assert m.tipo != 'E1'
    vecchio = m.training
    m.eval()
    mass, post_c, post_n = [], [], []
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a:a + lotto]]
        stati = [GM.StatoRiga() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            passa_tratto(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att])
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


def parametri_appresi(m):
    """Numeri imparati (solo aggregati, per capire che cosa fa l'eco): E1: beta per tipo e posto, pesi per distanza; puntatore: beta per strada, gamma di E2."""
    import torch
    import torch.nn.functional as F_
    with torch.no_grad():
        if m.tipo == 'E1':
            return OrderedDict(beta=[[round(float(x), 4) for x in r] for r in m.bet], peso_distanza=[round(float(x), 4) for x in F_.softplus(m.rec1)])
        o = OrderedDict(beta=[round(float(x), 4) for x in m.beta], recenza=[round(float(x), 4) for x in m.rec])
        if m.tipo == 'E2':
            o['gamma'] = round(float(m.gam), 4)
        return o


# ---------------------------------------------------------------- scrivere segno per segno

class Penna22(GM.Penna20):
    """Come GM.Penna20 (M1 come base) piu' la spinta dell'eco di E1 e le funzioni di E2/E3 (passo in avanti della GRU)."""

    def __init__(self, m, ctx, capacita=6000):
        super().__init__(m, ctx, capacita)
        self.tipo = m.tipo
        self.lg_ultimo = None

    def dai(self, tok):
        lg = super().dai(tok)
        tok = int(tok)
        if self.tipo == 'E1':
            ctx = self.ctx
            if tok == ctx.SP or ctx.N0 <= tok < ctx.N0 + ctx.nbins or tok >= ctx.u0:
                b = self.bonus_E1()
                for s, v in b.items():
                    lg[s] += v
        self.lg_ultimo = lg
        return lg

    def bonus_E1(self):
        """{simbolo: spinta} nella parola in corso, con i candidati della riga in corso e di quella sopra e il prefisso gia' scritto."""
        import torch
        m, ctx = self.m, self.ctx
        p = tuple(self.corrente)
        cand = self.candidati()
        with torch.no_grad():
            w = torch.nn.functional.softplus(m.rec1).tolist()
            bet = m.bet.tolist()
        N = {}
        for k, (un, f) in enumerate(cand):
            for (tau, sg) in spinte_prefisso(un, p):
                if sg < 0:
                    for tk_ in (ctx.SP, ctx.EOL):
                        N[(tau, tk_)] = N.get((tau, tk_), 0.0) + w[k]
                else:
                    N[(tau, ctx.u0 + sg)] = N.get((tau, ctx.u0 + sg), 0.0) + w[k]
        bk = min(len(p), NBK - 1)
        out = {}
        for (tau, s), v in N.items():
            out[s] = out.get(s, 0.0) + bet[tau][bk] * math.log1p(v)
        return out

    def avanti(self, glifi):
        """Logit (n, V) dopo aver dato in piu' ciascun glifo di `glifi` (indici di unita') allo stato corrente, senza cambiarlo."""
        torch, m = self.torch, self.m
        n = len(glifi)
        with torch.inference_mode():
            y1 = self.h1[0].expand(n, -1).contiguous()
            y2 = self.h2[0].expand(n, -1).contiguous()
            return m.avanti_glifi(y1, y2, torch.tensor(glifi, dtype=torch.long))

    def logg_candidati(self, cand):
        """(1, S): log della probabilita' dei primi due glifi di ogni candidato (come in training)."""
        torch, ctx = self.torch, self.ctx
        S, u0 = ctx.S, ctx.u0
        lg = np.array(self.lg_ultimo, dtype=np.float64)
        lp = lg - (lg.max() + math.log(np.exp(lg - lg.max()).sum()))
        diff = sorted({c[0] for c, f in cand})
        lp2 = {}
        if diff:
            L2 = self.avanti(diff).double().numpy()
            L2 = L2 - (L2.max(1, keepdims=True) + np.log(np.exp(L2 - L2.max(1, keepdims=True)).sum(1, keepdims=True)))
            lp2 = {g: L2[i] for i, g in enumerate(diff)}
        out = np.zeros((1, S), np.float32)
        for k, (c, f) in enumerate(cand):
            l1 = lp[u0 + c[0]]
            if len(c) == 1:
                a, b = lp2[c[0]][ctx.SP], lp2[c[0]][ctx.EOL]
                l2 = max(a, b) + math.log(math.exp(a - max(a, b)) + math.exp(b - max(a, b)))
            else:
                l2 = lp2[c[0]][u0 + c[1]]
            out[0, k] = l1 + l2
        return torch.from_numpy(out)

    def puntatore(self, cand):
        torch, m, ctx = self.torch, self.m, self.ctx
        S = ctx.S
        Fc = np.zeros((1, S, ctx.nf), np.float32)
        valid = np.zeros((1, S), bool)
        for k, (un, f) in enumerate(cand):
            Fc[0, k] = f
            valid[0, k] = True
        logg = self.logg_candidati(cand) if self.tipo == 'E2' else None
        with torch.inference_mode():
            lpf, lpp = m.puntatore(self.hd[None, :], torch.from_numpy(Fc), torch.from_numpy(valid), logg)
        return float(lpf.exp()), lpp[0].exp().numpy()


# ---------------------------------------------------------------- testi sintetici con eco e contatto piantati

def sintetico_eco_contatto(righe, seme, divisore, unita, eco=0.5, ritocco=0.6, inizio=0.5, contatto=0.0, pref_out=None):
    """Una copia del libro (`righe`: dizionari come ia07.libro_vero()) con le stesse righe e lunghezze e parole pescate dalla frequenza del libro, con
    piantati insieme:
    - CONTATTO (se `contatto` > 0): ogni glifo finale ha un glifo iniziale "preferito" (tabella a caso); una parola dopo un'altra comincia con il
      preferito con probabilita' `contatto`;
    - ECO (se `eco` > 0): ogni parola, con probabilita' `eco`, e' una parola della riga sopra (a caso); con probabilita' `ritocco` e' ritoccata: con
      probabilita' `inizio` il ritocco e' proprio "il primo glifo diventa il preferito dal contatto" (la regola da mettere alla prova), altrimenti un glifo
      cambiato, aggiunto o tolto a caso (in parti uguali).
    Restituisce la nuova lista di righe; se `pref_out` e' un dizionario ci mette la tabella dei glifi iniziali preferiti."""
    rng = random.Random(seme)
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)
    pref = {a: rng.choice(unita) for a in unita}
    if pref_out is not None:
        pref_out.update(pref)

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    def con_primo(w, g):
        u = divisore(w)
        u2 = [g] + list(u[1:])
        w2 = ''.join(u2)
        return w2 if divisore(w2) == u2 else w

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

    out, pagina_corr, sopra = [], None, None
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, sopra = x['pagina'], None
        n = len(x['parole'])
        ps = []
        for k in range(n):
            prima = ps[-1] if ps else None
            g_pref = pref[divisore(prima)[-1]] if prima is not None else None
            if eco and sopra and rng.random() < eco:
                w = rng.choice(sopra)
                if rng.random() < ritocco:
                    if g_pref is not None and rng.random() < inizio:
                        w = con_primo(w, g_pref)
                    else:
                        w = modifica(w)
            else:
                w = fresca()
                if contatto and g_pref is not None and rng.random() < contatto:
                    w = con_primo(w, g_pref)
            ps.append(w)
        sopra = ps
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out
