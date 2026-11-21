# -*- coding: utf-8 -*-
"""Supporto di ia23 (modulo, non e' un esperimento): imitatori che riprendono le parole da TUTTA la pagina gia' scritta.

Che cosa c'e' qui, in parole semplici
- Tre imitatori a segni (P1, P2, P3), tutti costruiti sulla GRU 2 x 256 di M1 (come E0-E3 di ia22: niente attenzione, niente vettore di pagina,
  niente posizione nella riga). Cambia l'insieme delle parole da cui si puo' riprendere: non piu' le ultime 28 della riga in corso e di quella
  sopra, ma OGNI tipo di parola gia' scritto nella pagina (una volta sola, in ordine di prima comparsa). Ogni tipo porta tre caratteristiche
  imparate (un peso per classe):
    distanza in righe dell'ultima occorrenza (6 classi: la parola subito prima; stessa riga; 1, 2, 3-5, 6 o piu' righe sopra),
    numero di occorrenze nella pagina (4 classi: 1, 2, 3-4, 5 o piu'),
    frequenza del tipo nel manoscritto di addestramento (7 classi: mai visto, 1, 2-3, 4-7, 8-15, 16-63, 64 o piu').
    P1  come E1: eco come spinta sui logit (prodotto di esperti a livello di segno), con i candidati di tutta la pagina.
    P2  come E2: puntatore "copia e ritocco" a livello di parola, vincolato al contatto (peso x probabilita' GRU dei primi due glifi).
    P3  come E3: puntatore con tre strade in cui l'inizio della parola e' riscritto dalla GRU.
- Per tenere basso il costo: ogni tipo compare una sola volta nella lista dei candidati (non una volta per posizione), il vettore dei tipi si
  codifica una volta per tipo diverso del lotto (non per candidato), le corrispondenze di P1 si raggruppano per classe (con molteplicita').
- L'addestramento e' quello di ia20/ia22 (stesse pieghe, stessi tratti che finiscono a fine riga, stesso arresto anticipato).
- Scrittura segno per segno (`Penna23`) uguale al calcolo a tratti; testi sintetici con tema di pagina, eco locale e contatto piantati
  (`sintetico_tema_eco_contatto`).
Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import random
import time
import bisect
from collections import Counter, OrderedDict, defaultdict

import numpy as np

import gradini_modelli as GM
import echi_modelli as EM

# ---------------------------------------------------------------- costanti (fissate nella preregistrazione)

TIPI = ('P1', 'P2', 'P3')
NT_PUNT = dict(P2=4, P3=7)           # strade del puntatore (come E2 e E3)
NDC, NCC, NFC = 6, 4, 7              # classi: distanza dell'ultima occorrenza, numero di occorrenze nella pagina, frequenza nel manoscritto
NCLS = NDC * NCC * NFC
NTAU, NBK = EM.NTAU, EM.NBK
VERSIONE = 'pagina-1'
REC_INIT = EM.REC_INIT               # softplus(REC_INIT) = 1


def configurazione(tipo, V, piccolo=False):
    c = GM.configurazione(1, V, piccolo)
    c['tipo'] = tipo
    c['versione'] = VERSIONE
    return c


def cfg_completa(tipo, voc, ctx, piccolo=False):
    c = configurazione(tipo, ctx.V, piccolo)
    c.update(nf=ctx.nf, U=ctx.U, SP=ctx.SP, EOL=ctx.EOL, K=ctx.K, S=ctx.S, u0=ctx.u0, nt=NT_PUNT.get(tipo, 0))
    return c


# ---------------------------------------------------------------- le tre caratteristiche di un candidato

def classe_dist(dl, prima):
    """`dl`: righe di distanza fra la parola in corso e l'ultima occorrenza del tipo (>= 0); `prima`: vero se l'ultima occorrenza e' la parola subito prima.
    0 la parola subito prima, 1 stessa riga, 2 una riga sopra, 3 due righe, 4 tre-cinque, 5 sei o piu'."""
    dl = np.asarray(dl)
    c = np.where(dl <= 0, 1, np.where(dl == 1, 2, np.where(dl == 2, 3, np.where(dl <= 5, 4, 5))))
    return np.where(prima, 0, c).astype(np.int8)


def classe_cnt(n):
    """Numero di occorrenze nella pagina: 1 -> 0, 2 -> 1, 3-4 -> 2, 5 o piu' -> 3."""
    n = np.asarray(n)
    return np.where(n <= 1, 0, np.where(n == 2, 1, np.where(n <= 4, 2, 3))).astype(np.int8)


def classe_freq(n):
    """Frequenza nel manoscritto di addestramento: 0 mai visto, 1 una volta, 2 2-3, 3 4-7, 4 8-15, 5 16-63, 6 64 o piu'."""
    return 0 if n <= 0 else 1 if n == 1 else 2 if n <= 3 else 3 if n <= 7 else 4 if n <= 15 else 5 if n <= 63 else 6


def conta_tipi(pagine, ctx):
    """Conteggio dei tipi di parola (tuple di indici di glifo) nelle pagine date (dizionari con `tok`)."""
    c = Counter()
    u0 = ctx.u0
    for d in pagine:
        tok = np.asarray(d['tok'], dtype=np.int64)
        tk = [int(x) for x in tok]
        for s, e in GM.parole_di_tok(tok, ctx):
            c[tuple(x - u0 for x in tk[s:e])] += 1
    return c


def tabella_freq(conti):
    """tipo -> classe di frequenza (solo i tipi visti: gli altri sono la classe 0)."""
    return {t: classe_freq(n) for t, n in conti.items()}


class StatoPagina:
    """I tipi di parola gia' scritti in una pagina, in ordine di prima comparsa, con l'ultima occorrenza e il numero di occorrenze.
    Lo usano allo stesso modo la preparazione delle pagine e la scrittura segno per segno."""

    def __init__(self, cap=64):
        self.slot = {}
        self.tipi = []
        self.ult = np.zeros(cap, np.int64)         # indice (nella pagina) dell'ultima occorrenza
        self.riga = np.zeros(cap, np.int64)        # riga dell'ultima occorrenza
        self.cnt = np.zeros(cap, np.int64)         # occorrenze
        self.j = 0                                 # parole scritte

    @property
    def K(self):
        return len(self.tipi)

    def caratteristiche(self, linea):
        """(classe di distanza, classe di occorrenze) dei tipi gia' scritti, per la parola che sta per essere scritta sulla riga `linea`."""
        K = len(self.tipi)
        return classe_dist(linea - self.riga[:K], self.ult[:K] == self.j - 1), classe_cnt(self.cnt[:K])

    def aggiungi(self, tipo, linea):
        """Registra la parola `tipo` appena scritta sulla riga `linea`. -> (slot, nuovo?)."""
        k = self.slot.get(tipo)
        nuovo = k is None
        if nuovo:
            k = len(self.tipi)
            if k >= len(self.ult):
                for a in ('ult', 'riga', 'cnt'):
                    setattr(self, a, np.concatenate([getattr(self, a), np.zeros(len(self.ult), np.int64)]))
            self.slot[tipo] = k
            self.tipi.append(tipo)
            self.cnt[k] = 0
        self.ult[k] = self.j
        self.riga[k] = linea
        self.cnt[k] += 1
        self.j += 1
        return k, nuovo


# ---------------------------------------------------------------- corrispondenze di P1 (come E1, con memoria locale alla pagina)

def entrate_parola(w, c):
    """Tutte le coppie (l, tau, s) che la parola candidata `c` da' al segno dopo un prefisso di lunghezza `l` della parola `w` (come echi_modelli.spinte_parola,
    ma senza memoria globale e fermandosi quando nessun allineamento e' piu' vivo)."""
    out = []
    st = {(0, 0)}
    for l in range(len(w) + 1):
        if l > 0:
            st = EM.avanza(st, c, w[l - 1])
            if not st:
                break
        for (tau, sg) in EM.spinte(c, l, st):
            out.append((l, tau, sg))
    return tuple(out)


# ---------------------------------------------------------------- pagine preparate

def prepara_pagina(d, ctx, tipo, tid, fc_tipi):
    """Dati fissi di una pagina (`d`: dizionario con almeno tok, linea, nome). `tid`: dizionario tipo -> numero (condiviso, si riempie qui); `fc_tipi`:
    tipo -> classe di frequenza. Per ogni parola j: i tipi gia' scritti (slot 0..nj[j]-1, in ordine di prima comparsa) e le loro classi (DC, CC);
    per P2 e P3 le coppie (candidato, strada); per P1 le corrispondenze raggruppate per classe."""
    tok = np.asarray(d['tok'], dtype=np.int64)
    linea = np.asarray(d['linea'], dtype=np.int64)
    T, Tin = len(tok), len(tok) - 1
    tk = [int(x) for x in tok]
    u0, SP = ctx.u0, ctx.SP
    words = GM.parole_di_tok(tok, ctx)
    nw = len(words)
    units = [tuple(tk[s + j] - u0 for j in range(e - s)) for s, e in words]
    wl = [int(linea[s]) for s, e in words]
    ordine = OrderedDict()
    for u in units:
        if u not in ordine:
            ordine[u] = len(ordine)
    tl = list(ordine)
    ntp = len(tl)
    DC = np.full((nw, ntp), -1, np.int8)
    CC = np.full((nw, ntp), -1, np.int8)
    nj = np.zeros(nw, np.int32)
    st = StatoPagina()
    for j in range(nw):
        K = st.K
        if K:
            dc, cc = st.caratteristiche(wl[j])
            DC[j, :K] = dc
            CC[j, :K] = cc
        nj[j] = K
        st.aggiungi(units[j], wl[j])
    tidp = np.array([tid.setdefault(u, len(tid)) for u in tl], np.int64)
    fcp = np.array([fc_tipi.get(u, 0) for u in tl], np.int8)
    P = dict(nome=d['nome'], tok=tok, linea=linea, T=T, Tin=Tin, words=words, units=units, nw=nw, chunks=GM.tagli_riga(tok, ctx), tl=tl, ntp=ntp,
             DC=DC, CC=CC, nj=nj, tidp=tidp, fcp=fcp,
             ws0=np.array([s - 1 for s, e in words], np.int64), we0=np.array([e - 1 for s, e in words], np.int64),
             wterm=np.array([0 if tk[e] == SP else 1 for s, e in words], np.int64))
    if tipo == 'P1':
        bk = np.full(Tin, NBK, np.int64)
        ft, fcl, ftau, fs, fm = [], [], [], [], []
        memo = {}
        for j, (s, e) in enumerate(words):
            w = units[j]
            for l in range(len(w) + 1):
                t = s - 1 + l
                if t < Tin:
                    bk[t] = min(l, NBK - 1)
            n = int(nj[j])
            if n == 0:
                continue
            clsj = DC[j, :n].astype(np.int64) * (NCC * NFC) + CC[j, :n].astype(np.int64) * NFC + fcp[:n]
            agg = {}
            for k in range(n):
                c = tl[k]
                per = memo.get((c, w))
                if per is None:
                    per = memo[(c, w)] = entrate_parola(w, c)
                cl = int(clsj[k])
                for (l, tau, sg) in per:
                    t = s - 1 + l
                    if t >= Tin:
                        continue
                    key = (t, cl, tau, sg)
                    agg[key] = agg.get(key, 0) + 1
            for (t, cl, tau, sg), mu in agg.items():
                ft.append(t), fcl.append(cl), ftau.append(tau), fs.append(sg), fm.append(mu)
        o = np.argsort(np.array(ft, np.int64), kind='stable') if ft else np.zeros(0, np.int64)
        P.update(bk=bk, ft=np.array(ft, np.int32)[o], fcl=np.array(fcl, np.int16)[o], ftau=np.array(ftau, np.int8)[o], fs=np.array(fs, np.int16)[o],
                 fm=np.array(fm, np.int16)[o])
    else:
        P.update(coppie_pagina(units, tl, nj, ctx, tipo))
        cu0 = np.array([u[0] for u in tl], np.int64)
        cu1 = np.array([u[1] if len(u) > 1 else -2 for u in tl], np.int64)          # -2: parola di un glifo (il secondo "segno" e' la fine parola)
        P.update(cu0p=cu0, cu1p=cu1)
    return P


def coppie_pagina(units, tl, nj, ctx, tipo):
    """Per ogni parola j le coppie (candidato k, strada) con k < nj[j]: strade 0-3 (uguale, cambia, aggiunge, toglie; echi_modelli/gradini_modelli.scripts) e, per P3,
    4-6 (inizio riscritto). Trova i candidati con indici (parola uguale, parola senza un glifo, suffissi) invece di provarli tutti: `coppie_brute` e' il controllo."""
    EX = {u: k for k, u in enumerate(tl)}
    DEL = defaultdict(list)
    SUF1, SUF2 = defaultdict(list), defaultdict(list)
    for k, u in enumerate(tl):
        for i in range(len(u)):
            DEL[(i, u[:i] + u[i + 1:])].append(k)
        if tipo == 'P3':
            SUF1[u[1:]].append(k)
            if len(u) >= 2:
                SUF2[u[2:]].append(k)
    pj, pk, pt, pc, px, pn = [], [], [], [], [], []
    for j, w in enumerate(units):
        n = int(nj[j])
        if n == 0:
            continue
        cand = set()
        k = EX.get(w)
        if k is not None:
            cand.add(k)
        nw_ = len(w)
        for i in range(nw_):
            cand.update(DEL.get((i, w[:i] + w[i + 1:]), ()))              # un glifo cambiato (stessa lunghezza)
        if nw_ >= 2:
            for i in range(nw_):
                k = EX.get(w[:i] + w[i + 1:])                             # un glifo aggiunto (il candidato e' w senza un glifo)
                if k is not None:
                    cand.add(k)
        for i in range(nw_ + 1):
            cand.update(DEL.get((i, w), ()))                              # un glifo tolto (il candidato e' w con un glifo in piu')
        if tipo == 'P3':
            cand.update(SUF1.get(w[1:], ()))
            if nw_ >= 2:
                k = EX.get(w[1:])
                if k is not None:
                    cand.add(k)
                cand.update(SUF2.get(w[2:], ()))
        for k in sorted(cand):
            if k >= n:
                continue
            c = tl[k]
            for (t_, cx, x_, n_) in GM.scripts(c, w, ctx.U):
                pj.append(j), pk.append(k), pt.append(t_), pc.append(cx), px.append(x_), pn.append(n_)
            if tipo == 'P3':
                for t_ in EM.scripts_rigenerati(c, w):
                    pj.append(j), pk.append(k), pt.append(t_), pc.append(0), px.append(0), pn.append(1.0)
    return dict(pj=np.array(pj, np.int64), pk=np.array(pk, np.int64), pt=np.array(pt, np.int64), pc=np.array(pc, np.int64), px=np.array(px, np.int64),
                pn=np.array(pn, np.float32))


def coppie_brute(units, tl, nj, ctx, tipo):
    """Come `coppie_pagina` ma provando tutti i candidati (per le prove)."""
    pj, pk, pt, pc, px, pn = [], [], [], [], [], []
    for j, w in enumerate(units):
        for k in range(int(nj[j])):
            c = tl[k]
            for (t_, cx, x_, n_) in GM.scripts(c, w, ctx.U):
                pj.append(j), pk.append(k), pt.append(t_), pc.append(cx), px.append(x_), pn.append(n_)
            if tipo == 'P3':
                for t_ in EM.scripts_rigenerati(c, w):
                    pj.append(j), pk.append(k), pt.append(t_), pc.append(0), px.append(0), pn.append(1.0)
    return dict(pj=np.array(pj, np.int64), pk=np.array(pk, np.int64), pt=np.array(pt, np.int64), pc=np.array(pc, np.int64), px=np.array(px, np.int64),
                pn=np.array(pn, np.float32))


def prepara_insiemi(insiemi, ctx, tipo, fc_tipi):
    """`insiemi`: liste di liste di pagine (dizionari). Restituisce le liste di pagine preparate; per P2 e P3 costruisce la tabella dei vettori dei tipi di parola
    (una riga per tipo distinto: ctx.FM, indicizzata da P['tidp'])."""
    tid = {}
    out = [[prepara_pagina(d, ctx, tipo, tid, fc_tipi) for d in ins] for ins in insiemi]
    ctx.tid = tid
    if tipo != 'P1':
        righe = [None] * len(tid)
        for u, i in tid.items():
            righe[i] = GM.feat_parola(u, ctx)
        ctx.FM = np.stack(righe) if righe else np.zeros((1, ctx.nf), np.float32)
    return out


# ---------------------------------------------------------------- un lotto: un tratto per ogni pagina ancora attiva

def lotto_tratto(righe, ctx, tipo):
    bt = GM.lotto_tratto(righe, ctx, 1)
    B, L = bt['B'], bt['L']
    cat = lambda l, dt, shp=(): np.concatenate(l) if l else np.zeros((0,) + shp, dt)
    if tipo == 'P1':
        bk = np.full((B, L), NBK, np.int64)
        bi, ti, cl, tau, ss, mu = [], [], [], [], [], []
        for b, (P, (a, c)) in enumerate(righe):
            n = c - a
            bk[b, :n] = P['bk'][a:c]
            lo, hi = np.searchsorted(P['ft'], [a, c], side='left')
            if hi > lo:
                bi.append(np.full(hi - lo, b, np.int64))
                ti.append(P['ft'][lo:hi].astype(np.int64) - a)
                cl.append(P['fcl'][lo:hi].astype(np.int64))
                tau.append(P['ftau'][lo:hi].astype(np.int64))
                ss.append(P['fs'][lo:hi].astype(np.int64))
                mu.append(P['fm'][lo:hi].astype(np.float32))
        bi, ti, cl, tau, ss, mu = cat(bi, np.int64), cat(ti, np.int64), cat(cl, np.int64), cat(tau, np.int64), cat(ss, np.int64), cat(mu, np.float32)
        term = ss < 0                                     # la fine parola e' spazio O fine riga: due segni
        tok = np.where(term, ctx.SP, ctx.u0 + ss)
        bi2, ti2, cl2, tau2, mu2 = bi[term], ti[term], cl[term], tau[term], mu[term]
        bt['eco'] = dict(bk=bk, bi=np.concatenate([bi, bi2]), ti=np.concatenate([ti, ti2]), cls=np.concatenate([cl, cl2]), tau=np.concatenate([tau, tau2]),
                         s=np.concatenate([tok, np.full(len(bi2), ctx.EOL, np.int64)]), mult=np.concatenate([mu, mu2]))
        return bt
    blocchi = []
    J0 = 0
    for b, (P, (a, c)) in enumerate(righe):
        j0 = int(np.searchsorted(P['ws0'], a, side='left'))
        j1 = int(np.searchsorted(P['ws0'], c, side='left'))
        if j1 > j0:
            assert P['we0'][j1 - 1] < c, 'una parola attraversa il confine del tratto'
        Sp = int(P['nj'][j0:j1].max()) if j1 > j0 else 0
        blocchi.append((b, P, j0, j1, Sp, J0))
        J0 += j1 - j0
    S = max([x[4] for x in blocchi] + [1])
    U = ctx.U
    tidg = np.full((J0, S), -1, np.int64)
    dcb = np.full((J0, S), -1, np.int64)
    ccb = np.zeros((J0, S), np.int64)
    fcb = np.zeros((J0, S), np.int64)
    c0b = np.zeros((J0, S), np.int64)
    c1b = np.full((J0, S), -1, np.int64)
    rows, s0, e0, term = [], [], [], []
    pj, pk, pt, pc, px, pn = [], [], [], [], [], []
    for (b, P, j0, j1, Sp, r0) in blocchi:
        nj_ = j1 - j0
        a = righe[b][1][0]
        c = righe[b][1][1]
        rows += [b] * nj_
        s0.append(P['ws0'][j0:j1] - a)
        e0.append(P['we0'][j0:j1] - a)
        term.append(P['wterm'][j0:j1])
        if nj_ and Sp:
            dcs = P['DC'][j0:j1, :Sp]
            ok = dcs >= 0
            dcb[r0:r0 + nj_, :Sp] = dcs
            ccb[r0:r0 + nj_, :Sp] = np.maximum(P['CC'][j0:j1, :Sp], 0)
            tidg[r0:r0 + nj_, :Sp] = np.where(ok, P['tidp'][None, :Sp], -1)
            fcb[r0:r0 + nj_, :Sp] = P['fcp'][None, :Sp]
            c0b[r0:r0 + nj_, :Sp] = P['cu0p'][None, :Sp]
            c1b[r0:r0 + nj_, :Sp] = P['cu1p'][None, :Sp]
        lo = int(np.searchsorted(P['pj'], j0, side='left'))
        hi = int(np.searchsorted(P['pj'], j1, side='left'))
        pj.append(P['pj'][lo:hi] - j0 + r0)
        pk.append(P['pk'][lo:hi]), pt.append(P['pt'][lo:hi]), pc.append(P['pc'][lo:hi]), px.append(P['px'][lo:hi]), pn.append(P['pn'][lo:hi])
    valid = dcb >= 0
    cls = np.where(valid, np.maximum(dcb, 0) * (NCC * NFC) + ccb * NFC + fcb, 0)
    uidx = np.zeros((J0, S), np.int64)
    if valid.any():
        uniq, inv = np.unique(tidg[valid], return_inverse=True)
        uidx[valid] = inv
        Fu = ctx.FM[uniq].astype(np.float32)
    else:
        Fu = np.zeros((1, ctx.nf), np.float32)
    d = dict(rows=np.array(rows, np.int64), s0=cat(s0, np.int64), e0=cat(e0, np.int64), term=cat(term, np.int64), Fu=Fu, uidx=uidx, valid=valid, cls=cls,
             pj=cat(pj, np.int64), pk=cat(pk, np.int64), pt=cat(pt, np.int64), pc=cat(pc, np.int64), px=cat(px, np.int64), pn=cat(pn, np.float32), J=J0,
             c0=c0b, c1=c1b)
    if tipo == 'P2' and J0:
        jj, kk = np.nonzero(valid)
        key = jj * U + d['c0'][jj, kk]
        uk, inv = np.unique(key, return_inverse=True)
        po = np.full((J0, S), -1, np.int64)
        po[jj, kk] = inv
        d.update(pair_j=uk // U, pair_g=uk % U, pair_of=po)
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
            # peso di un candidato = f(distanza) + f(occorrenze) + f(frequenza nel manoscritto): tre vettori imparati
            self.rd = nn.Parameter(torch.full((NDC,), REC_INIT if self.tipo == 'P1' else 0.0))
            self.rc = nn.Parameter(torch.zeros(NCC))
            self.rf = nn.Parameter(torch.zeros(NFC))
            if self.tipo == 'P1':
                self.bet = nn.Parameter(torch.zeros(NTAU, NBK + 1))        # l'ultima colonna (fuori parola) non conta: li' la spinta e' zero
            else:
                U, dk, nt = cfg['U'], cfg['dk'], cfg['nt']
                self.U = U
                self.pq = nn.Linear(H, dk)
                self.pf = nn.Linear(H, 1)
                nn.init.constant_(self.pf.bias, 2.0)
                self.Wc = nn.Parameter(torch.randn(cfg['nf'], dk) * 0.05)
                self.beta = nn.Parameter(torch.tensor([-3.0] + [-4.0] * (nt - 1)))
                self.Tsub = nn.Parameter(torch.zeros(U, U))
                self.Tins = nn.Parameter(torch.zeros(U + 1, U))
                if self.tipo == 'P2':
                    self.gam = nn.Parameter(torch.zeros(1))

        def bias_flat(self):
            """(NCLS,): rd[distanza] + rc[occorrenze] + rf[frequenza], nell'ordine distanza, occorrenze, frequenza."""
            return (self.rd[:, None, None] + self.rc[None, :, None] + self.rf[None, None, :]).reshape(-1)

        # ---- P1: spinta dell'eco sui logit
        def bonus(self, eco, B, L, V):
            w = F_.softplus(self.bias_flat())
            idx = ((eco['bi'] * L + eco['ti']) * NTAU + eco['tau']) * V + eco['s']
            N = torch.zeros(B * L * NTAU * V).index_add_(0, idx, w[eco['cls']] * eco['mult']).view(B, L, NTAU, V)
            b = self.bet[:, eco['bk']].permute(1, 2, 0)[..., None]          # (B, L, NTAU, 1)
            return (b * torch.log1p(N)).sum(2)

        def forward(self, X, bt, h1=None, h2=None):
            y1, _ = self.gru1(self.emb(X), h1)
            u = self.caduta(y1)
            y2, _ = self.gru2(u, h2)
            hd = self.caduta(y2)
            lg = self.out(hd)
            if self.tipo == 'P1' and bt.get('eco') is not None:
                lg = lg + self.bonus(bt['eco'], X.shape[0], X.shape[1], lg.shape[-1])
            return dict(logits=lg, hd=hd, y1=y1, y2=y2)

        # ---- puntatore (P2, P3)
        def tabelle(self):
            U = self.U
            d = torch.full((U, U), 0.0)
            d.fill_diagonal_(float('-inf'))
            return F_.log_softmax(self.Tsub + d, 1), F_.log_softmax(self.Tins, 1)

        def puntatore_enc(self, hs, enc, uidx, valid, cls, logg=None):
            """hs (J, H); enc (Nu, dk) codifica dei tipi del lotto; uidx (J, S) riga di enc di ogni candidato; valid (J, S); cls (J, S) classe (distanza, occorrenze,
            frequenza); logg (J, S) o None (P2). -> (log pi_libero (J,), log pi (J, S, nt))."""
            q = self.pq(hs)
            scu = torch.matmul(q, enc.T) / math.sqrt(self.cfg['dk'])
            sc = scu.gather(1, uidx) + self.bias_flat()[cls]
            if self.tipo == 'P2' and logg is not None:
                sc = sc + self.gam * logg
            lg = (sc[:, :, None] + self.beta[None, None, :]).masked_fill(~valid[:, :, None], float('-inf'))
            tutti = torch.cat([self.pf(hs), lg.reshape(lg.shape[0], -1)], 1)
            lp = F_.log_softmax(tutti, 1)
            return lp[:, 0], lp[:, 1:].reshape(lg.shape)

        def puntatore(self, hs, pw, logg=None):
            enc = torch.matmul(pw['Fu'], self.Wc)
            return self.puntatore_enc(hs, enc, pw['uidx'], pw['valid'], pw['cls'], logg)

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
            if self.tipo == 'P1' or pw is None or pw['J'] == 0:
                return -tl.sum(), ntok
            B = tl.shape[0]
            cs = torch.cat([torch.zeros(B, 1, dtype=torch.float64), torch.cumsum(tl.double(), 1)], 1)
            rows, s0, e0 = pw['rows'], pw['s0'], pw['e0']
            Lfree = (cs[rows, e0 + 1] - cs[rows, s0]).float()
            hs = out['hd'][rows, s0]
            logg = None
            if self.tipo == 'P2':
                logg = self.logg_candidati(lp[rows, s0].detach(), out['y1'][rows, s0].detach(), out['y2'][rows, s0].detach(), pw)
            lpf, lpp = self.puntatore(hs, pw, logg)
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
            if self.tipo == 'P3':
                t0 = tl[rows[pj], s0[pj]]
                t1 = tl[rows[pj], s0[pj] + 1]
                lsp = lsp + torch.where((pt == 4) | (pt == 5), t0, zero) + torch.where(pt == 6, t0 + t1, zero)
            lpi = lpp[pj, pw['pk'], pt]
            cp = torch.exp(lpi + lsp)
            Acopia = torch.zeros(pw['J']).index_add(0, pj, cp)
            lcop = torch.where(Acopia > 0, torch.log(Acopia.clamp(min=1e-38)) + logr, torch.full_like(logr, float('-inf')))
            tot = torch.logaddexp(lpf + Lfree, lcop)
            self.ultimo = dict(tot=tot.detach(), lcop=lcop.detach(), lpf=lpf.detach(), Acopia=Acopia.detach(), lpp=lpp.detach(),
                               logg=None if logg is None else logg.detach())
            return -tot.sum(), ntok

    return Modello(cfg)


def a_torch(bt, tipo):
    import torch
    X, Y, Mk = torch.as_tensor(bt['X']), torch.as_tensor(bt['Y']), torch.as_tensor(bt['Mk'])
    t, pw = {}, None
    if tipo == 'P1':
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
    """Come echi_modelli.addestra_modello (e GM, ia07.addestra): lotti di LOTTO pagine ordinate per lunghezza con un po' di rumore, un passo per tratto, AdamW,
    taglio del gradiente; arresto anticipato sulla validazione (bit per segno), si tiene il migliore. -> (modello, curva_val, curva_add, epoca_scelta)."""
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


def salva_modello(m, percorso, segni, ctx, fc_tipi, extra=None):
    import torch
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    torch.save(dict(stato=m.state_dict(), cfg=m.cfg, segni=list(segni), tipi=ctx.lista_tipi, fc=dict(fc_tipi), extra=extra or {}), percorso + '.tmp')
    os.replace(percorso + '.tmp', percorso)


def carica_modello(percorso, voc):
    """-> (modello in modalita' di prova, ctx, tabella delle frequenze). Il ctx non ha la tabella dei vettori dei tipi (serve solo all'addestramento)."""
    import torch
    d = torch.load(percorso, weights_only=False)
    assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
    cfg = d['cfg']
    ctx = GM.Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
    m = costruisci(cfg)
    m.load_state_dict(d['stato'])
    m.eval()
    return m, ctx, d['fc']


def massa_copia(m, ctx, pagine, lotto=16):
    """Come echi_modelli.massa_copia per P2 e P3."""
    import torch
    assert m.tipo != 'P1'
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
    """Numeri imparati (solo aggregati): peso per classe di distanza, di occorrenze e di frequenza (esponenziale per P2 e P3, softplus del totale per P1);
    P1: beta per tipo e posto; puntatori: beta per strada, gamma di P2."""
    import torch
    import torch.nn.functional as F_
    with torch.no_grad():
        o = OrderedDict()
        o['distanza'] = [round(float(x), 4) for x in m.rd]
        o['occorrenze'] = [round(float(x), 4) for x in m.rc]
        o['frequenza'] = [round(float(x), 4) for x in m.rf]
        if m.tipo == 'P1':
            o['beta'] = [[round(float(x), 4) for x in r] for r in m.bet]
        else:
            o['beta'] = [round(float(x), 4) for x in m.beta]
            if m.tipo == 'P2':
                o['gamma'] = round(float(m.gam), 4)
        return o


# ---------------------------------------------------------------- scrivere segno per segno

class Penna23(EM.Penna22):
    """Come EM.Penna22 (M1 come base) ma con i candidati di tutta la pagina: tiene lo stato della pagina (`StatoPagina`), la codifica dei tipi (P2, P3) e la
    spinta dell'eco di P1 con gli allineamenti aggiornati glifo per glifo."""

    def __init__(self, m, ctx, fc_tipi, capacita=6000):
        super().__init__(m, ctx, capacita)
        self.fc_tipi = fc_tipi
        torch = self.torch
        with torch.no_grad():
            self.bias = m.bias_flat().detach().numpy().astype(np.float64)
            if m.tipo == 'P1':
                self.wtab = torch.nn.functional.softplus(m.bias_flat()).numpy().astype(np.float64)
                self.bet = m.bet.detach().numpy().astype(np.float64)
            else:
                self.Wc = m.Wc.detach().numpy()

    def apri(self):
        super().apri()
        self.stato = StatoPagina()
        cap = 64
        self.fcs = np.zeros(cap, np.int64)
        self.encM = np.zeros((cap, self.m.cfg['dk']), np.float32) if self.tipo != 'P1' else None
        self.c0 = np.zeros(cap, np.int64)
        self.c1 = np.zeros(cap, np.int64)
        self._nfa = None
        self._w = None

    def _aggiorna(self, tok):
        ctx = self.ctx
        if (tok == ctx.SP or tok == ctx.EOL) and self.corrente:
            un = tuple(self.corrente)
            k, nuovo = self.stato.aggiungi(un, self.linea)
            if nuovo:
                if k >= len(self.fcs):
                    for a in ('fcs', 'c0', 'c1'):
                        setattr(self, a, np.concatenate([getattr(self, a), np.zeros(len(self.fcs), np.int64)]))
                    if self.encM is not None:
                        self.encM = np.concatenate([self.encM, np.zeros_like(self.encM)])
                self.fcs[k] = self.fc_tipi.get(un, 0)
                self.c0[k] = un[0]
                self.c1[k] = un[1] if len(un) > 1 else -2
                if self.encM is not None:
                    self.encM[k] = GM.feat_parola(un, ctx) @ self.Wc
            self._nfa = None
            self._w = None
        super()._aggiorna(tok)

    def classi(self):
        """Classe (distanza, occorrenze, frequenza) combinata di ogni tipo gia' scritto, per la parola in corso."""
        st = self.stato
        K = st.K
        dc, cc = st.caratteristiche(self.linea)
        return dc.astype(np.int64) * (NCC * NFC) + cc.astype(np.int64) * NFC + self.fcs[:K]

    def dai(self, tok):
        lg = super().dai(tok)
        if self.tipo == 'P1':
            tok = int(tok)
            ctx = self.ctx
            if tok == ctx.SP or ctx.N0 <= tok < ctx.N0 + ctx.nbins or tok >= ctx.u0:
                for s, v in self.bonus_P1().items():
                    lg[s] += v
        self.lg_ultimo = lg
        return lg

    def bonus_P1(self):
        """{simbolo: spinta} nella parola in corso, con i tipi di tutta la pagina e il prefisso gia' scritto (allineamenti aggiornati a ogni glifo)."""
        ctx, st = self.ctx, self.stato
        K = st.K
        if K == 0:
            return {}
        p = tuple(self.corrente)
        if self._w is None:
            self._w = self.wtab[self.classi()]
        w = self._w
        tl = st.tipi
        if len(p) == 0:
            self._nfa = (p, [(k, {(0, 0)}) for k in range(K)])
        elif self._nfa is not None and self._nfa[0] == p[:-1]:
            nuovi = []
            for k, s_ in self._nfa[1]:
                s2 = EM.avanza(s_, tl[k], p[-1])
                if s2:
                    nuovi.append((k, s2))
            self._nfa = (p, nuovi)
        else:
            vivi = []
            for k in range(K):
                s_ = {(0, 0)}
                for x in p:
                    s_ = EM.avanza(s_, tl[k], x)
                    if not s_:
                        break
                if s_:
                    vivi.append((k, s_))
            self._nfa = (p, vivi)
        N = {}
        for k, s_ in self._nfa[1]:
            for (tau, sg) in EM.spinte(tl[k], len(p), s_):
                if sg < 0:
                    for tk_ in (ctx.SP, ctx.EOL):
                        N[(tau, tk_)] = N.get((tau, tk_), 0.0) + w[k]
                else:
                    N[(tau, ctx.u0 + sg)] = N.get((tau, ctx.u0 + sg), 0.0) + w[k]
        bk = min(len(p), NBK - 1)
        out = {}
        for (tau, s), v in N.items():
            out[s] = out.get(s, 0.0) + self.bet[tau][bk] * math.log1p(v)
        return out

    def logg_pagina(self):
        """(1, K): log della probabilita' dei primi due glifi di ogni tipo gia' scritto (come in addestramento)."""
        torch, ctx = self.torch, self.ctx
        K = self.stato.K
        u0 = ctx.u0
        lg = np.array(self.lg_ultimo, dtype=np.float64)
        lp = lg - (lg.max() + math.log(np.exp(lg - lg.max()).sum()))
        c0, c1 = self.c0[:K], self.c1[:K]
        diff = sorted(set(c0.tolist()))
        L2 = self.avanti(diff).double().numpy()
        L2 = L2 - (L2.max(1, keepdims=True) + np.log(np.exp(L2 - L2.max(1, keepdims=True)).sum(1, keepdims=True)))
        riga = {g: i for i, g in enumerate(diff)}
        ri = np.array([riga[g] for g in c0.tolist()])
        l1 = lp[u0 + c0]
        a, b = L2[ri, ctx.SP], L2[ri, ctx.EOL]
        mx = np.maximum(a, b)
        fine = mx + np.log(np.exp(a - mx) + np.exp(b - mx))
        gl = L2[ri, u0 + np.maximum(c1, 0)]
        l2 = np.where(c1 == -2, fine, gl)
        return torch.from_numpy((l1 + l2).astype(np.float32))[None, :]

    def puntatore_pagina(self):
        """(pi_libero, pi[K, nt]) a inizio parola, con i tipi di tutta la pagina (P2, P3)."""
        torch, m = self.torch, self.m
        K = self.stato.K
        cls = torch.from_numpy(self.classi())[None, :]
        enc = torch.from_numpy(self.encM[:K])
        uidx = torch.arange(K)[None, :]
        valid = torch.ones(1, K, dtype=torch.bool)
        logg = self.logg_pagina() if self.tipo == 'P2' else None
        with torch.inference_mode():
            lpf, lpp = m.puntatore_enc(self.hd[None, :], enc, uidx, valid, cls, logg)
        return float(lpf.exp()), lpp[0].exp().numpy()


# ---------------------------------------------------------------- testi sintetici con tema di pagina, eco locale e contatto piantati

def sintetico_tema_eco_contatto(righe, seme, divisore, unita, eco=0.25, ritocco=0.6, tema=0.3, n_tema=25, contatto=0.7, pref_out=None, temi_out=None):
    """Una copia del libro (`righe`: dizionari come ia07.libro_vero()) con le stesse righe e lunghezze e parole pescate dal vocabolario del libro, con piantati
    insieme:
    - TEMA di pagina (se `tema` > 0): ogni pagina ha `n_tema` parole proprie (tipi diversi scelti con probabilita' uguale fra i tipi del vocabolario: sono rare
      nel manoscritto), usate con probabilita' `tema` in una riga qualunque della pagina;
    - ECO locale (se `eco` > 0): ogni parola, con probabilita' `eco`, e' una parola della riga sopra (a caso); con probabilita' `ritocco` ritoccata (un glifo
      cambiato, aggiunto o tolto, in parti uguali);
    - CONTATTO (se `contatto` > 0): ogni glifo finale ha un glifo iniziale "preferito" (tabella a caso); una parola fresca dopo un'altra comincia con il
      preferito con probabilita' `contatto`.
    L'ordine delle scelte per ogni parola: eco, poi tema, poi parola fresca (dalla frequenza del libro, con il contatto). Restituisce la nuova lista di righe;
    se `pref_out` e' un dizionario ci mette la tabella dei glifi iniziali preferiti, se `temi_out` e' un dizionario ci mette pagina -> insieme delle parole di tema."""
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

    out, pagina_corr, sopra, topici = [], None, None, []
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, sopra = x['pagina'], None
            topici = rng.sample(voc, min(n_tema, len(voc))) if tema else []
            if temi_out is not None:
                temi_out[pagina_corr] = set(topici)
        n = len(x['parole'])
        ps = []
        for k in range(n):
            prima = ps[-1] if ps else None
            g_pref = pref[divisore(prima)[-1]] if prima is not None else None
            if eco and sopra and rng.random() < eco:
                w = rng.choice(sopra)
                if rng.random() < ritocco:
                    w = modifica(w)
            elif tema and topici and rng.random() < tema:
                w = rng.choice(topici)
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
