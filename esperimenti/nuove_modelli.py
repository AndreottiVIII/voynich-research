# -*- coding: utf-8 -*-
"""Supporto di ia24 (modulo, non e' un esperimento): imitatori che costruiscono le parole NUOVE in un altro modo.

Che cosa c'e' qui, in parole semplici
- Tre imitatori a segni (W1, W2, W3), tutti costruiti sulla GRU 2 x 256 di M1 (come E0-E3 di ia22 e P1-P3 di ia23: niente attenzione, niente vettore di pagina).
    W1  "parola nuova = ritocco del lessico": a inizio parola una miscela esatta sceglie fra la scrittura libera della GRU e la copia di una parola del LESSICO
        di addestramento (uguale, con una modifica o con due modifiche). La parola del lessico si sceglie con la sua frequenza (a una potenza imparata) e con la
        probabilita' che la GRU da' ai suoi primi due glifi dopo la parola prima (come E2 di ia22); le modifiche sono un glifo cambiato, aggiunto o tolto, con
        tabelle imparate. Le modifiche doppie partono solo dalle K parole piu' frequenti.
    W2  W1 piu' il puntatore di E2 (candidati = le ultime 28 parole della riga in corso e di quella sopra, copia vincolata al contatto): l'eco locale e il lessico.
    W3  la GRU con un secondo esperto sul segno: un modello di forma "a caselle" (prefisso, nucleo, suffisso come caselle in ordine, imparato dal lessico con
        l'algoritmo EM). Prodotto di esperti: logit della GRU + lambda * log P_caselle(segno | parte di parola gia' scritta); normalizzazione esatta (softmax).
- Per non premiare la copia del testo che si sta imparando, nell'addestramento il lessico di ogni foglio NON contiene il foglio stesso (si toglie il suo
  conteggio): la parola e' nuova per il modello come lo e' nei fogli tenuti fuori. Nella validazione e nei fogli tenuti fuori il lessico e' intero.
- L'addestramento e' quello di ia20/ia22 (stesse pieghe, stessi tratti che finiscono a fine riga, stesso arresto anticipato), copiato qui.
- Scrittura segno per segno (`Penna24`) uguale al calcolo a tratti; testi sintetici con parole nuove piantate (`sintetico_nuove`).
Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import pickle
import random
import time
import bisect
from collections import Counter, OrderedDict
from itertools import combinations

import numpy as np

import gradini_modelli as GM
import echi_modelli as EM

# ---------------------------------------------------------------- costanti (fissate nella preregistrazione)

TIPI = ('W1', 'W2', 'W3')
NT_PUNT = dict(W2=4)                 # strade del puntatore di pagina di W2 (come E2): 0 uguale, 1 cambia, 2 aggiunge, 3 toglie
NSLOT = 8                            # caselle del modello di forma di W3
NBK = 3                              # W3: posto nella parola (primo glifo, secondo, dopo); il 4o (indice 3) = fuori parola
VERSIONE = 'nuove-1'
MIX_INIT = (2.0, -2.0, -3.0, -4.0)   # logit iniziali della miscela: libero, lessico 0, 1, 2 modifiche
LOG_EPS = 1e-9


def configurazione(tipo, V, piccolo=False):
    c = GM.configurazione(1, V, piccolo)
    c['tipo'] = tipo
    c['versione'] = VERSIONE
    c['nslot'] = NSLOT
    return c


def cfg_completa(tipo, voc, ctx, piccolo=False):
    c = configurazione(tipo, ctx.V, piccolo)
    c.update(nf=ctx.nf, U=ctx.U, SP=ctx.SP, EOL=ctx.EOL, K=ctx.K, S=ctx.S, u0=ctx.u0, nt=NT_PUNT.get(tipo, 0))
    return c


# ---------------------------------------------------------------- modifiche di una parola (tuple di indici di glifo)

def n1_stringhe(w, U):
    """Tutte le parole non vuote a UNA modifica da `w` (un glifo cambiato, aggiunto o tolto): insieme di tuple."""
    out = set()
    n = len(w)
    for i in range(n):
        wi = w[i]
        for g in range(U):
            if g != wi:
                out.add(w[:i] + (g,) + w[i + 1:])
        if n > 1:
            out.add(w[:i] + w[i + 1:])
    for i in range(n + 1):
        for g in range(U):
            out.add(w[:i] + (g,) + w[i:])
    out.discard(w)
    return out


def cancellazioni(w, m=2):
    """Le parole ottenute togliendo da `w` fino a `m` glifi (compresa `w`): indice "a cancellazioni" per trovare le parole a distanza <= m."""
    out = {w}
    n = len(w)
    for k in range(1, min(m, n) + 1):
        for pos in combinations(range(n), k):
            s = set(pos)
            out.add(tuple(w[i] for i in range(n) if i not in s))
    return out


def distanza(a, b):
    """Distanza di Levenshtein (glifo cambiato, aggiunto o tolto)."""
    la, lb = len(a), len(b)
    prec = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cur[j] = min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (a[i - 1] != b[j - 1]))
        prec = cur
    return prec[lb]


# ---------------------------------------------------------------- il lessico di addestramento

class Lessico:
    """Il lessico di addestramento di una piega: parole (tuple di indici di glifo) in ordine di frequenza, conteggi, classe (primo glifo, secondo glifo o fine) di
    ogni parola, conteggi per foglio (per toglierli nell'addestramento) e, con memoria, per ogni parola `w` del testo le parole del lessico a una e a due modifiche
    (con le scritture che portano dall'una all'altra). Le modifiche doppie partono solo dalle prime `K2` parole del lessico."""

    def __init__(self, conti, U, K2):
        ordine = sorted(conti.items(), key=lambda kv: (-kv[1], kv[0]))
        self.parole = [w for w, _ in ordine]
        self.n = np.array([c for _, c in ordine], np.float32)
        self.idx = {w: i for i, w in enumerate(self.parole)}
        self.U = int(U)
        self.P = self.U * (self.U + 1)
        self.pair = np.array([w[0] * (self.U + 1) + (w[1] if len(w) > 1 else self.U) for w in self.parole], np.int64)
        self.K2 = min(int(K2), len(self.parole))
        self.foglio = {}
        self.memo = {}
        self._n1 = {}
        self._del2 = None
        self._t = None

    # ---- conteggi per foglio
    def aggiungi_foglio(self, foglio, conti):
        ii = [(self.idx[w], c) for w, c in conti.items() if w in self.idx]
        self.foglio[foglio] = (np.array([i for i, _ in ii], np.int64), np.array([c for _, c in ii], np.float32))

    def conteggi(self, fogli):
        """(len(fogli), L): il conteggio di ogni parola togliendo quello del foglio (se il foglio e' di addestramento); fogli sconosciuti: conteggio intero."""
        NN = np.tile(self.n, (len(fogli), 1))
        for r, f in enumerate(fogli):
            if f in self.foglio:
                i, c = self.foglio[f]
                NN[r, i] -= c
        np.maximum(NN, 0.0, out=NN)
        return NN

    # ---- tensori
    def tensori(self):
        import torch
        if self._t is None:
            self._t = dict(pair=torch.as_tensor(self.pair), n=torch.as_tensor(self.n))
        return self._t

    # ---- parole a una e a due modifiche
    def _indice2(self):
        if self._del2 is None:
            d = {}
            for i in range(self.K2):
                for v in cancellazioni(self.parole[i], 2):
                    d.setdefault(v, []).append(i)
            self._del2 = d
        return self._del2

    def _n1set(self, i):
        s = self._n1.get(i)
        if s is None:
            s = self._n1[i] = frozenset(n1_stringhe(self.parole[i], self.U))
        return s

    def vicini(self, w):
        r = self.memo.get(w)
        if r is None:
            r = self.memo[w] = self._calcola(w)
        return r

    def _calcola(self, w):
        U = self.U
        n1w = n1_stringhe(w, U)
        k0 = np.array([self.idx[w]], np.int64) if w in self.idx else np.zeros(0, np.int64)
        c1, s1 = [], []
        for x in n1w:
            i = self.idx.get(x)
            if i is not None:
                for sc in GM.scripts(x, w, U):
                    c1.append(i)
                    s1.append(sc)
        c2, a2, b2 = [], [], []
        if self.K2:
            cand = set()
            ind = self._indice2()
            for v in cancellazioni(w, 2):
                for i in ind.get(v, ()):
                    cand.add(i)
            for i in sorted(cand):
                c = self.parole[i]
                if c == w or c in n1w:
                    continue                                          # a distanza 0 o 1: la modifica doppia qui non conta (vedi la preregistrazione)
                inter = n1w & self._n1set(i)
                for cp in sorted(inter):
                    for a in GM.scripts(c, cp, U):
                        for b in GM.scripts(cp, w, U):
                            c2.append(i)
                            a2.append(a)
                            b2.append(b)
        f = lambda l, k, dt: np.array([x[k] for x in l], dt)             # tipi piccoli: la memoria dei vicini di una piega puo' essere grande (si convertono nel lotto)
        i8, i16 = np.int8, np.int16
        return (k0,
                (np.array(c1, np.int32), f(s1, 0, i8), f(s1, 1, i16), f(s1, 2, i16), f(s1, 3, i16)),
                (np.array(c2, np.int32), f(a2, 0, i8), f(a2, 1, i16), f(a2, 2, i16), f(a2, 3, i16),
                 f(b2, 0, i8), f(b2, 1, i16), f(b2, 2, i16), f(b2, 3, i16)))

    def riempi(self, tipi):
        for w in tipi:
            self.vicini(w)

    def salva_memo(self, percorso):
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(percorso + '.tmp', 'wb') as f:
            pickle.dump(self.memo, f, protocol=4)
        os.replace(percorso + '.tmp', percorso)

    def carica_memo(self, percorso):
        with open(percorso, 'rb') as f:
            self.memo.update(pickle.load(f))

    # ---- per salvare insieme al modello
    def a_dizionario(self):
        return dict(parole=self.parole, n=self.n, U=self.U, K2=self.K2)

    @classmethod
    def da_dizionario(cls, d):
        conti = {w: float(c) for w, c in zip(d['parole'], d['n'])}
        lex = cls(conti, d['U'], d['K2'])
        return lex


# ---------------------------------------------------------------- il modello di forma "a caselle" (HMM da sinistra a destra)

class Caselle:
    """Caselle in ordine: la parola passa per caselle di numero non decrescente (si puo' restare nella stessa casella, o saltare), a ogni passo emette un glifo
    dalla casella in cui sta, e puo' finire dopo qualunque casella. Parametri: pi0 (casella di partenza), A (S x S, solo casella uguale o seguente), E (S x U, glifo
    emesso), fine (S, probabilita' di finire dopo la casella). Ogni riga di A piu' `fine` somma a 1. Imparato dalle parole DISTINTE del lessico con l'algoritmo EM."""

    def __init__(self, U, S, pi0, A, E, fine):
        self.U, self.S = int(U), int(S)
        self.pi0, self.A, self.E, self.fine = pi0, A, E, fine
        self._memo = {}

    # ---- imparare
    @classmethod
    def adatta(cls, parole, U, S=NSLOT, iterazioni=15, pesi=None):
        parole = [tuple(w) for w in parole]
        N = len(parole)
        Lm = max(len(w) for w in parole)
        G = np.zeros((N, Lm), np.int64)
        lens = np.array([len(w) for w in parole], np.int64)
        for i, w in enumerate(parole):
            G[i, :len(w)] = w
        mask = np.arange(Lm)[None, :] < lens[:, None]
        wt = np.ones(N) if pesi is None else np.asarray(pesi, np.float64)
        # partenza: i glifi si dividono per posizione relativa media in S gruppi (rompe la simmetria)
        somma, cnt = np.zeros(U), np.zeros(U)
        for w in parole:
            n = len(w)
            for t, g in enumerate(w):
                somma[g] += (t / (n - 1)) if n > 1 else 0.5
                cnt[g] += 1
        rel = np.where(cnt > 0, somma / np.maximum(cnt, 1), 0.5)
        rango = np.argsort(np.argsort(rel, kind='stable'), kind='stable')
        casella = np.minimum((rango * S) // max(U, 1), S - 1)
        E = np.full((S, U), 0.02 / U)
        for g in range(U):
            E[casella[g], g] += 1.0
        E /= E.sum(1, keepdims=True)
        pi0 = np.array([1.0 if s <= S // 2 else 0.1 for s in range(S)])
        pi0 /= pi0.sum()
        A = np.zeros((S, S))
        for s in range(S):
            for t in range(s, S):
                A[s, t] = 0.3 if t == s else 1.0 if t == s + 1 else 0.4
        fine = np.full(S, 0.3)
        tot = A.sum(1) + fine
        A /= tot[:, None]
        fine = fine / tot
        ll_prec = None
        for it in range(iterazioni):
            B = E.T[G]                                               # (N, L, S)
            B = np.where(mask[:, :, None], B, 1.0)
            alpha = np.zeros((N, Lm, S))
            alpha[:, 0] = pi0[None, :] * B[:, 0]
            for t in range(1, Lm):
                alpha[:, t] = (alpha[:, t - 1] @ A) * B[:, t]
            ult = np.clip(lens - 1, 0, Lm - 1)
            alpha_fin = alpha[np.arange(N), ult]                     # (N, S)
            Pw = np.maximum((alpha_fin * fine[None, :]).sum(1), 1e-300)
            ll = float((wt * np.log(Pw)).sum() / wt.sum())
            beta = np.zeros((N, Lm, S))
            for t in range(Lm - 1, -1, -1):
                if t < Lm - 1:
                    rec = (B[:, t + 1] * beta[:, t + 1]) @ A.T
                else:
                    rec = np.zeros((N, S))
                beta[:, t] = np.where((ult == t)[:, None], fine[None, :], np.where((t < ult)[:, None], rec, 0.0))
            gam = alpha * beta / Pw[:, None, None]
            gam = gam * mask[:, :, None]
            w3 = wt[:, None, None]
            cpi = (wt[:, None] * gam[:, 0]).sum(0)
            cE = np.zeros((S, U))
            for t in range(Lm):
                m = mask[:, t]
                if m.any():
                    np.add.at(cE.T, G[m, t], (wt[m, None] * gam[m, t]))
            # transizioni: t -> t+1 solo se t+1 < len
            ma = (np.arange(Lm - 1)[None, :] + 1) < lens[:, None]    # (N, L-1)
            aw = alpha[:, :-1] * (wt / Pw)[:, None, None] * ma[:, :, None]
            bb = B[:, 1:] * beta[:, 1:]
            cA = A * np.einsum('nts,ntk->sk', aw, bb)
            cF = (wt[:, None] * (alpha_fin * fine[None, :]) / Pw[:, None]).sum(0)
            pi0 = (cpi + 0.01) / (cpi + 0.01).sum()
            E = (cE + 0.002) / (cE + 0.002).sum(1, keepdims=True)
            mA = np.triu(np.ones((S, S)))
            raw = cA * mA + 0.01 * mA
            rawf = cF + 0.01
            tot = raw.sum(1) + rawf
            A = raw / tot[:, None]
            fine = rawf / tot
            ll_prec = ll
        c = cls(U, S, pi0, A, E, fine)
        c.verosimiglianza = ll_prec
        return c

    # ---- previsione del prossimo simbolo dopo un prefisso
    def predittivo(self, prefisso):
        """log-probabilita' (U + 1,) del prossimo glifo (0..U-1) e della fine parola (indice U) dopo `prefisso` (tupla di glifi). La fine non e' possibile a
        parola vuota (probabilita' ridotta a un valore minimo)."""
        r = self._memo.get(prefisso)
        if r is not None:
            return r
        U = self.U
        if not prefisso:
            p = np.concatenate([self.pi0 @ self.E, [0.0]])
        else:
            a = self.pi0 * self.E[:, prefisso[0]]
            for g in prefisso[1:]:
                a = (a @ self.A) * self.E[:, g]
            s = a.sum()
            a = a / s if s > 0 else np.full(self.S, 1.0 / self.S)
            p = np.concatenate([(a @ self.A) @ self.E, [float(a @ self.fine)]])
        r = np.log(np.maximum(p, LOG_EPS)).astype(np.float64)
        if len(self._memo) > 400000:
            self._memo.clear()
        self._memo[prefisso] = r
        return r

    def tabella(self, w):
        """(len(w) + 1, U + 1): predittivo dopo ogni prefisso di `w`."""
        return np.stack([self.predittivo(tuple(w[:l])) for l in range(len(w) + 1)])

    def bit_parola(self, w):
        """Bit per ogni simbolo di `w` (glifi e poi la fine): lista di len(w) + 1 numeri."""
        t = self.tabella(w)
        return [float(-t[l, w[l] if l < len(w) else self.U] / math.log(2)) for l in range(len(w) + 1)]

    def campiona(self, rng, lmax=14):
        """Una parola dalle caselle (rng: random.Random). Non vuota."""
        s = rng.choices(range(self.S), weights=list(self.pi0))[0]
        out = [rng.choices(range(self.U), weights=list(self.E[s]))[0]]
        while len(out) < lmax:
            pesi = list(self.A[s]) + [self.fine[s]]
            k = rng.choices(range(self.S + 1), weights=pesi)[0]
            if k == self.S:
                break
            s = k
            out.append(rng.choices(range(self.U), weights=list(self.E[s]))[0])
        return tuple(out)

    def a_dizionario(self):
        return dict(U=self.U, S=self.S, pi0=self.pi0, A=self.A, E=self.E, fine=self.fine)

    @classmethod
    def da_dizionario(cls, d):
        return cls(d['U'], d['S'], d['pi0'], d['A'], d['E'], d['fine'])


# ---------------------------------------------------------------- pagine preparate

def parole_pagina(d, ctx):
    tok = np.asarray(d['tok'], dtype=np.int64)
    tk = [int(x) for x in tok]
    u0 = ctx.u0
    words = GM.parole_di_tok(tok, ctx)
    units = [tuple(tk[s + j] - u0 for j in range(e - s)) for s, e in words]
    return tok, tk, words, units


def conti_lessico(pagine_raw, ctx):
    """(conti totali, conti per foglio) delle parole (tuple di indici di glifo) delle pagine grezze `pagine_raw` (dizionari con tok e foglio)."""
    tot, per = Counter(), {}
    for d in pagine_raw:
        _, _, _, units = parole_pagina(d, ctx)
        c = Counter(units)
        tot.update(c)
        per.setdefault(d['foglio'], Counter()).update(c)
    return tot, per


def costruisci_lessico(pagine_add, ctx, K2=None):
    tot, per = conti_lessico(pagine_add, ctx)
    lex = Lessico(tot, ctx.U, ctx.K if K2 is None else K2)
    for f, c in per.items():
        lex.aggiungi_foglio(f, c)
    return lex


def adatta_caselle(lex, ctx, iterazioni=15):
    return Caselle.adatta(lex.parole, ctx.U, NSLOT, iterazioni)


def prepara_pagina(d, ctx, tipo, hmm=None):
    """Dati fissi di una pagina. W2: quelli di E2 (candidati e strade del puntatore) piu' il foglio. W1: parole, tratti e terminatori. W3: in piu' la spinta delle
    caselle (log-probabilita' del prossimo simbolo) e il posto nella parola di ogni posizione."""
    if tipo == 'W2':
        P = EM.prepara_pagina(d, ctx, 'E2')
        P['foglio'] = d.get('foglio')
        return P
    tok, tk, words, units = parole_pagina(d, ctx)
    linea = np.asarray(d['linea'], dtype=np.int64)
    T, Tin = len(tok), len(tok) - 1
    SP = ctx.SP
    P = dict(nome=d['nome'], tok=tok, linea=linea, T=T, Tin=Tin, words=words, units=units, nw=len(words), chunks=GM.tagli_riga(tok, ctx), foglio=d.get('foglio'),
             ws0=np.array([s - 1 for s, e in words], np.int64), we0=np.array([e - 1 for s, e in words], np.int64),
             wterm=np.array([0 if tk[e] == SP else 1 for s, e in words], np.int64))
    if tipo == 'W3':
        U = ctx.U
        sl = np.zeros((Tin, U + 1), np.float32)
        bk = np.full(Tin, NBK, np.int64)
        for (s, e), w in zip(words, units):
            tab = hmm.tabella(w)
            for l in range(len(w) + 1):
                t = s - 1 + l
                if t < Tin:
                    sl[t] = tab[l]
                    bk[t] = min(l, NBK - 1)
        P.update(slot=sl, bk=bk)
    return P


def prepara_insiemi(insiemi, ctx, tipo, lex=None, hmm=None):
    """`insiemi`: liste di liste di pagine grezze. Restituisce le liste di pagine preparate; per W2 costruisce anche la tabella dei vettori delle parole (ctx.FM)."""
    if tipo == 'W2':
        out = EM.prepara_insiemi(insiemi, ctx, 'E2')
        for ins_raw, ins in zip(insiemi, out):
            for d, P in zip(ins_raw, ins):
                P['foglio'] = d.get('foglio')
        return out
    return [[prepara_pagina(d, ctx, tipo, hmm) for d in ins] for ins in insiemi]


def tipi_parole(pagine):
    """Tutte le parole distinte (tuple) delle pagine preparate."""
    s = set()
    for ins in pagine:
        for P in ins:
            s.update(P['units'])
    return s


# ---------------------------------------------------------------- un lotto: un tratto per ogni pagina ancora attiva

def lotto_tratto(righe, ctx, tipo, lex=None):
    U = ctx.U
    if tipo == 'W3':
        bt = GM.lotto_tratto(righe, ctx, 1)
        B, L = bt['B'], bt['L']
        sl = np.zeros((B, L, U + 1), np.float32)
        bk = np.full((B, L), NBK, np.int64)
        for b, (P, (a, c)) in enumerate(righe):
            n = c - a
            sl[b, :n] = P['slot'][a:c]
            bk[b, :n] = P['bk'][a:c]
        bt['slot'], bt['bk'] = sl, bk
        return bt
    if tipo == 'W2':
        bt = EM.lotto_tratto(righe, ctx, 'E2')
        d = bt['parole']
    else:
        bt = GM.lotto_tratto(righe, ctx, 1)
        rows, s0, e0, term = [], [], [], []
        J0 = 0
        for b, (P, (a, c)) in enumerate(righe):
            j0 = int(np.searchsorted(P['ws0'], a, side='left'))
            j1 = int(np.searchsorted(P['ws0'], c, side='left'))
            if j1 > j0:
                assert P['we0'][j1 - 1] < c, 'una parola attraversa il confine del tratto'
            rows += [b] * (j1 - j0)
            s0.append(P['ws0'][j0:j1] - a)
            e0.append(P['we0'][j0:j1] - a)
            term.append(P['wterm'][j0:j1])
            J0 += j1 - j0
        cat = lambda l: np.concatenate(l) if l else np.zeros(0, np.int64)
        d = dict(rows=np.array(rows, np.int64), s0=cat(s0), e0=cat(e0), term=cat(term), J=J0)
        bt['parole'] = d
    # ---- il lessico: per ogni parola del lotto le parole a 0, 1, 2 modifiche
    fogli, frow = [], {}
    lrow, nuova = [], []
    A0j, A0c = [], []
    k1 = [[] for _ in range(6)]          # j, c, t, cx, x, n
    k2 = [[] for _ in range(10)]         # j, c, t1, cx1, x1, n1, t2, cx2, x2, n2
    J0 = 0
    for b, (P, (a, c)) in enumerate(righe):
        j0 = int(np.searchsorted(P['ws0'], a, side='left'))
        j1 = int(np.searchsorted(P['ws0'], c, side='left'))
        f = P['foglio']
        if f not in frow:
            frow[f] = len(fogli)
            fogli.append(f)
        for j in range(j0, j1):
            w = P['units'][j]
            r0, r1, r2 = lex.vicini(w)
            lrow.append(frow[f])
            nuova.append(w not in lex.idx)
            if len(r0):
                A0j.append(np.full(1, J0, np.int64))
                A0c.append(r0)
            if len(r1[0]):
                k1[0].append(np.full(len(r1[0]), J0, np.int64))
                for q in range(5):
                    k1[1 + q].append(r1[q])
            if len(r2[0]):
                k2[0].append(np.full(len(r2[0]), J0, np.int64))
                for q in range(9):
                    k2[1 + q].append(r2[q])
            J0 += 1
    assert J0 == d['J'], 'parole del lotto: %d contro %d' % (J0, d['J'])
    cat = lambda l, dt: np.concatenate(l).astype(dt) if l else np.zeros(0, dt)
    dts1 = [np.int64, np.int64, np.int64, np.int64, np.int64, np.float32]
    dts2 = [np.int64] * 2 + [np.int64, np.int64, np.int64, np.float32] * 2
    d.update(lrow=np.array(lrow, np.int64), nuova=np.array(nuova, bool), NN=lex.conteggi(fogli),
             k0j=cat(A0j, np.int64), k0c=cat(A0c, np.int64),
             k1=[cat(k1[q], dts1[q]) for q in range(6)], k2=[cat(k2[q], dts2[q]) for q in range(10)])
    return bt


def a_torch(bt, tipo):
    import torch
    X, Y, Mk = torch.as_tensor(bt['X']), torch.as_tensor(bt['Y']), torch.as_tensor(bt['Mk'])
    t, pw = {}, None
    if tipo == 'W3':
        t['slot'] = torch.as_tensor(bt['slot'])
        t['bk'] = torch.as_tensor(bt['bk'])
    else:
        p = bt['parole']
        pw = {}
        for k, v in p.items():
            if isinstance(v, np.ndarray):
                pw[k] = torch.as_tensor(v)
            elif isinstance(v, list):
                pw[k] = [torch.as_tensor(x) for x in v]
            else:
                pw[k] = v
    return X, Y, Mk, t, pw


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
            self.passo = 1
            V, H = cfg['V'], cfg['nasc']
            self.H = H
            self.emb = nn.Embedding(V, cfg['emb'])
            self.gru1 = nn.GRU(cfg['emb'], H, 1, batch_first=True)
            self.gru2 = nn.GRU(H, H, 1, batch_first=True)
            self.caduta = nn.Dropout(cfg['caduta'])
            self.out = nn.Linear(H, V)
            self.lessico = None
            self.ultimo = None
            U = cfg['U']
            self.U = U
            if self.tipo == 'W3':
                self.gate = nn.Linear(H, 1)                       # porta imparata: quanto fidarsi delle caselle, dallo stato della GRU
                with torch.no_grad():
                    self.gate.weight.mul_(0.1)
                    self.gate.bias.fill_(-1.0)
                self.gb = nn.Parameter(torch.zeros(NBK))          # e dal posto nella parola (primo glifo, secondo, dopo)
            else:
                self.mix = nn.Linear(H, 4)
                with torch.no_grad():
                    self.mix.bias.copy_(torch.tensor(MIX_INIT))
                self.kap = nn.Parameter(torch.ones(2))            # potenza della frequenza: (0-1 modifiche, 2 modifiche)
                self.gm = nn.Parameter(torch.ones(2))             # esponente della probabilita' GRU dei primi due glifi
                self.tau = nn.Parameter(torch.zeros(3))           # cambia, aggiunge, toglie
                self.Tsub = nn.Parameter(torch.zeros(U, U))
                self.Tins = nn.Parameter(torch.zeros(U + 1, U))
                if self.tipo == 'W2':
                    S, dk, nt = cfg['S'], cfg['dk'], cfg['nt']
                    self.S = S
                    self.pq = nn.Linear(H, dk)
                    self.Wc = nn.Parameter(torch.randn(cfg['nf'], dk) * 0.05)
                    self.rec = nn.Parameter(torch.zeros(S))
                    self.beta = nn.Parameter(torch.tensor([-3.0] + [-4.0] * (nt - 1)))
                    self.gam = nn.Parameter(torch.zeros(1))

        # ---- W3: mistura con le caselle (porta imparata)
        def mistura_slot(self, lg, hd, slot, bk):
            """Probabilita' del segno = (1 - a) * GRU + a * caselle, con a = sigmoide(porta(stato) + bias del posto nella parola) dentro le parole e 0 fuori. Le caselle danno
            la probabilita' di ogni glifo e della fine parola; la fine parola si divide fra spazio e fine riga come fa la GRU. Somma a 1 per costruzione. Restituisce i logit
            (log della mistura dentro le parole, quelli della GRU fuori)."""
            U, SP, EOL = self.U, self.cfg['SP'], self.cfg['EOL']
            pg = F_.softmax(lg, -1)
            ps = slot.exp()
            pt = pg[..., SP] + pg[..., EOL] + 1e-12
            q = torch.cat([torch.zeros(slot.shape[:2] + (SP,)), (ps[..., U] * pg[..., SP] / pt)[..., None], (ps[..., U] * pg[..., EOL] / pt)[..., None], ps[..., :U]], -1)
            dentro = bk < NBK
            a = torch.sigmoid(self.gate(hd)[..., 0] + torch.cat([self.gb, torch.zeros(1)])[bk]) * dentro
            mix = (1.0 - a)[..., None] * pg + a[..., None] * q
            return torch.where(dentro[..., None], torch.log(mix.clamp(min=1e-30)), lg), a

        def forward(self, X, bt, h1=None, h2=None):
            y1, _ = self.gru1(self.emb(X), h1)
            u = self.caduta(y1)
            y2, _ = self.gru2(u, h2)
            hd = self.caduta(y2)
            lg = self.out(hd)
            a = None
            if self.tipo == 'W3' and bt.get('slot') is not None:
                lg, a = self.mistura_slot(lg, hd, bt['slot'], bt['bk'])
            return dict(logits=lg, hd=hd, y1=y1, y2=y2, porta=a)

        # ---- tabelle delle modifiche
        def tabelle(self):
            U = self.U
            d = torch.full((U, U), 0.0)
            d.fill_diagonal_(float('-inf'))
            lsub = F_.log_softmax(self.Tsub + d, 1).clamp(min=-60.0)
            return lsub, F_.log_softmax(self.Tins, 1)

        def avanti_glifi(self, y1, y2, glifi):
            """Un passo in avanti della GRU dallo stato (y1, y2) (N, H) dando il glifo `glifi` (N,): logit (N, V). Senza gradiente."""
            x = self.emb(glifi + self.cfg['u0'])[:, None, :]
            a, _ = self.gru1(x, y1[None])
            b, _ = self.gru2(a, y2[None])
            return self.out(b[:, 0])

        def coppie(self, lp0, y1, y2, blocco=300):
            """(J, U * (U + 1)): log della probabilita' che la GRU da' ai primi due glifi (o a un glifo e poi alla fine parola) dopo lo stato a inizio parola.
            Indice a * (U + 1) + b, b = U per "fine parola". Senza gradiente."""
            U, u0, SP, EOL = self.U, self.cfg['u0'], self.cfg['SP'], self.cfg['EOL']
            J = lp0.shape[0]
            gl = torch.arange(U)
            out = []
            with torch.no_grad():
                for a in range(0, J, blocco):
                    b = min(J, a + blocco)
                    n = b - a
                    lg2 = self.avanti_glifi(y1[a:b].repeat_interleave(U, 0), y2[a:b].repeat_interleave(U, 0), gl.repeat(n))
                    lp2 = F_.log_softmax(lg2, -1).view(n, U, -1)
                    due = torch.cat([lp2[:, :, u0:u0 + U], torch.logaddexp(lp2[:, :, SP], lp2[:, :, EOL])[..., None]], -1)       # (n, U, U + 1)
                    out.append(lp0[a:b, u0:u0 + U][:, :, None] + due)
                return torch.cat(out, 0).reshape(J, U * (U + 1)) if out else torch.zeros(0, U * (U + 1))

        # ---- puntatore di pagina (W2, come E2)
        def logit_candidati(self, hs, Fc, valid, logg):
            q = self.pq(hs)
            enc = torch.matmul(Fc, self.Wc)
            sc = (q[:, None, :] * enc).sum(-1) / math.sqrt(self.cfg['dk']) + self.rec[None, :] + self.gam * logg
            return (sc[:, :, None] + self.beta[None, None, :]).masked_fill(~valid[:, :, None], float('-inf'))

        def pesi_lessico(self, NN, row, lgf, K2, t_pair):
            """Per ogni parola j: (peso normalizzato dei termini del lessico) -> funzioni per le tre famiglie.
            Famiglia A (0 e 1 modifiche): tutto il lessico; famiglia B (2 modifiche): le prime K2 parole. Restituisce (WnA, eA, ZA, WnB, eB, ZB) con
            WnX (righe, parole), eX (J, ...) = exp(gamma * lg - massimo) e ZX (J,) la somma normalizzatrice."""
            kap, gm = self.kap, self.gm
            zero = torch.zeros(())
            WnA = torch.where(NN > 0, NN.clamp(min=1e-6).pow(kap[0]), zero)                   # (righe, L)
            P = lgf.shape[1]
            Mb = torch.zeros(NN.shape[0], P).index_add_(1, t_pair, WnA)                        # (righe, P)
            mA = (gm[0] * lgf).max(1).values.detach()
            eA = torch.exp(gm[0] * lgf - mA[:, None])                                         # (J, P)
            ZA = (Mb[row] * eA).sum(1)
            NB = NN[:, :K2]
            WnB = torch.where(NB > 0, NB.clamp(min=1e-6).pow(kap[1]), zero)
            lgB = lgf[:, t_pair[:K2]]                                                          # (J, K2)
            mB = (gm[1] * lgB).max(1).values.detach() if K2 else torch.zeros(lgf.shape[0])
            eB = torch.exp(gm[1] * lgB - mB[:, None])
            ZB = (WnB[row] * eB).sum(1)
            return WnA, eA, ZA, WnB, eB, ZB

        def nll(self, out, Y, Mk, pw):
            """Somma dei -log P (nat) dei segni da indovinare del tratto e quanti sono. W1 e W2: miscela esatta a livello di parola (libero, lessico a 0, 1 e 2
            modifiche, e per W2 le parole della riga in corso e di quella sopra)."""
            self.ultimo = None
            lp = F_.log_softmax(out['logits'], -1)
            tl = lp.gather(2, Y[..., None])[..., 0] * Mk
            ntok = float(Mk.sum())
            if self.tipo == 'W3' or pw is None or pw['J'] == 0:
                return -tl.sum(), ntok
            B = tl.shape[0]
            U, K2 = self.U, self.lessico.K2
            lex = self.lessico.tensori()
            cs = torch.cat([torch.zeros(B, 1, dtype=torch.float64), torch.cumsum(tl.double(), 1)], 1)
            rows, s0, e0 = pw['rows'], pw['s0'], pw['e0']
            J = pw['J']
            Lfree = (cs[rows, e0 + 1] - cs[rows, s0]).float()
            hs = out['hd'][rows, s0]
            lgf = self.coppie(lp[rows, s0].detach(), out['y1'][rows, s0].detach(), out['y2'][rows, s0].detach())
            row = pw['lrow']
            NN = pw['NN']
            t_pair = lex['pair']
            WnA, eA, ZA, WnB, eB, ZB = self.pesi_lessico(NN, row, lgf, K2, t_pair)
            lsub, lins = self.tabelle()
            lt = F_.log_softmax(self.tau, 0)
            zero = torch.zeros(())

            def log_op(t, cx, x, n):
                tab = torch.where(t == 1, lsub[cx.clamp(max=U - 1), x.clamp(max=U - 1)], torch.where(t == 2, lins[cx.clamp(max=U), x.clamp(max=U - 1)], zero))
                return lt[(t - 1).clamp(min=0)] + tab - torch.log(n)
            # k = 0: la parola e' nel lessico
            j0, c0 = pw['k0j'], pw['k0c']
            q0 = WnA[row[j0], c0] * eA[j0, t_pair[c0]] / ZA[j0]
            A0 = torch.zeros(J).index_add(0, j0, q0)
            # k = 1: una modifica da una parola del lessico
            j1, c1, t1, cx1, x1, n1 = pw['k1']
            q1 = WnA[row[j1], c1] * eA[j1, t_pair[c1]] / ZA[j1] * torch.exp(log_op(t1, cx1, x1, n1))
            A1 = torch.zeros(J).index_add(0, j1, q1)
            # k = 2: due modifiche da una delle prime K2 parole
            j2, c2, ta, cxa, xa, na, tb, cxb, xb, nb = pw['k2']
            if len(j2):
                q2 = WnB[row[j2], c2] * eB[j2, c2] / ZB[j2] * torch.exp(log_op(ta, cxa, xa, na) + log_op(tb, cxb, xb, nb))
            else:
                q2 = torch.zeros(0)
            A2 = torch.zeros(J).index_add(0, j2, q2)
            lm = self.mix(hs)
            logr_all = F_.log_softmax(out['logits'][rows, e0][:, [self.cfg['SP'], self.cfg['EOL']]], -1)
            logr = logr_all.gather(1, pw['term'][:, None])[:, 0]
            ninf = torch.full_like(logr, float('-inf'))
            if self.tipo == 'W2':
                S, nt = self.S, self.cfg['nt']
                valid = pw['valid']
                c0_, c1_ = pw['c0'].clamp(min=0), pw['c1']
                bi = c0_ * (U + 1) + torch.where(c1_ == -2, torch.full_like(c1_, U), c1_.clamp(min=0))
                logg = torch.where(valid, lgf.gather(1, bi), zero)
                lc = self.logit_candidati(hs, pw['Fc'], valid, logg)
                tutti = torch.cat([lm, lc.reshape(J, -1)], 1)
            else:
                tutti = lm
            lpi = F_.log_softmax(tutti, 1)
            lpf, lpk = lpi[:, 0], lpi[:, 1:4]
            lk = [torch.where(A > 0, torch.log(A.clamp(min=1e-38)) + lpk[:, k] + logr, ninf) for k, A in enumerate((A0, A1, A2))]
            termini = [lpf + Lfree] + lk
            lcop = ninf
            if self.tipo == 'W2':
                lpc = lpi[:, 4:].reshape(J, S, nt)
                pj, pt, pc, px, pn = pw['pj'], pw['pt'], pw['pc'], pw['px'], pw['pn']
                m1, m2, m3 = pt == 1, pt == 2, pt == 3
                lsp = torch.zeros(pj.shape[0])
                lsp = lsp + torch.where(m1, lsub[pc.clamp(max=U - 1), px.clamp(max=U - 1)] - torch.log(pn), zero)
                lsp = lsp + torch.where(m2, lins[pc, px.clamp(max=U - 1)] - torch.log(pn), zero)
                lsp = lsp + torch.where(m3, -torch.log(pn), zero)
                cp = torch.exp(lpc[pj, pw['pk'], pt] + lsp)
                Acop = torch.zeros(J).index_add(0, pj, cp)
                lcop = torch.where(Acop > 0, torch.log(Acop.clamp(min=1e-38)) + logr, ninf)
                termini.append(lcop)
            tot = torch.logsumexp(torch.stack(termini, 0), 0)
            lex_tot = torch.logsumexp(torch.stack(lk, 0), 0)
            self.ultimo = dict(tot=tot.detach(), segni=(e0 - s0 + 1).detach(), lpf=lpf.detach(), lex=lex_tot.detach(), cand=lcop.detach(), nuova=pw['nuova'], A=(A0.detach(), A1.detach(), A2.detach()),
                               mix=torch.exp(lpi[:, :4]).detach())
            return -tot.sum(), ntok

    return Modello(cfg)


# ---------------------------------------------------------------- passare da un tratto al successivo, valutare, addestrare

def passa_tratto(m, ctx, righe, stati, addestra=False, opt=None):
    import torch
    import torch.nn as nn
    bt = lotto_tratto(righe, ctx, m.tipo, m.lessico)
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


def addestra_modello(cfg, ctx, lex, add, val, seme, epoche_max, pazienza, epoche_fisse=None, messaggi=None):
    """Come EM.addestra_modello (e ia20): lotti di LOTTO pagine ordinate per lunghezza con un po' di rumore, un passo per tratto, AdamW, taglio del gradiente;
    arresto anticipato sulla validazione (bit per segno), si tiene il migliore. -> (modello, curva_val, curva_add, epoca_scelta)."""
    import torch
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci(cfg)
    m.lessico = lex
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


def salva_modello(m, percorso, segni, ctx, lex, hmm, extra=None):
    import torch
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    torch.save(dict(stato=m.state_dict(), cfg=m.cfg, segni=list(segni), tipi=ctx.lista_tipi, extra=extra or {},
                    lessico=lex.a_dizionario() if lex is not None else None, caselle=hmm.a_dizionario() if hmm is not None else None), percorso + '.tmp')
    os.replace(percorso + '.tmp', percorso)


def carica_modello(percorso, voc):
    """-> (modello in modalita' di prova, ctx, lessico o None, caselle o None)."""
    import torch
    d = torch.load(percorso, weights_only=False)
    assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
    cfg = d['cfg']
    ctx = GM.Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
    m = costruisci(cfg)
    m.load_state_dict(d['stato'])
    m.eval()
    lex = Lessico.da_dizionario(d['lessico']) if d.get('lessico') else None
    hmm = Caselle.da_dizionario(d['caselle']) if d.get('caselle') else None
    m.lessico = lex
    return m, ctx, lex, hmm


def diagnostica(m, ctx, pagine, lotto=16):
    """W1 e W2, su `pagine` (tenute fuori): massa media delle strade del lessico a inizio parola; quota a posteriori della strada del lessico (e della strada di
    pagina) sulle parole NUOVE (non nel lessico) e sulle note; quota di parole nuove; peso delle tre famiglie. Solo numeri."""
    import torch
    vecchio = m.training
    m.eval()
    mass, post_n, post_k, cand_n, cand_k = [], [], [], [], []
    mix = []
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
                pl = torch.exp(u['lex'] - u['tot'])
                pc = torch.exp(u['cand'] - u['tot'])
                nu_ = u['nuova']
                mass += (1.0 - torch.exp(u['lpf'])).tolist()
                post_n += pl[nu_].tolist()
                post_k += pl[~nu_].tolist()
                cand_n += pc[nu_].tolist()
                cand_k += pc[~nu_].tolist()
                mix.append(u['mix'])
            r += 1
    m.train(vecchio)
    f = lambda x: float(np.mean(x)) if x else None
    mx = torch.cat(mix, 0).mean(0).tolist() if mix else None
    tot = len(post_n) + len(post_k)
    return dict(massa_media=f(mass), posteriori_lessico_nuove=f(post_n), posteriori_lessico_note=f(post_k), posteriori_pagina_nuove=f(cand_n), posteriori_pagina_note=f(cand_k),
                quota_nuove=len(post_n) / max(tot, 1), parole=tot, miscela=mx)


def nat_per_parola(m, ctx, pagine, lex, lotto=16, piantate=None):
    """Quanto costa ogni parola (segni e terminatore) delle `pagine` (tenute fuori), divisa fra parole NUOVE (non nel lessico di addestramento `lex`) e note: nat e numero
    di segni di ciascun gruppo. Vale per M1 (modello di ia20), W1, W2 (miscela a livello di parola) e W3 (a segni): le parole sono le stesse per tutti, il conto e' lo stesso."""
    import torch
    vecchio = m.training
    m.eval()
    tot = dict(nat_nuove=0.0, segni_nuove=0, nat_note=0.0, segni_note=0, nat_piantate=0.0, segni_piantate=0, porta_piantate=0.0, porta_piantate_n=0, porta_altre=0.0, porta_altre_n=0)
    tipo = getattr(m, 'tipo', None)
    ordine = sorted(range(len(pagine)), key=lambda i: pagine[i]['Tin'])
    for a0 in range(0, len(ordine), lotto):
        Ps = [pagine[i] for i in ordine[a0:a0 + lotto]]
        stati = [GM.StatoRiga() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            righe = [(Ps[b], Ps[b]['chunks'][r]) for b in att]
            st = [stati[b] for b in att]
            if tipo in ('W1', 'W2'):
                passa_tratto(m, ctx, righe, st)
                u = m.ultimo
                if u is not None and u['tot'].numel():
                    if piantate is not None:
                        fl = []
                        for (P, (a, c)) in righe:
                            j0 = int(np.searchsorted(P['ws0'], a, side='left'))
                            j1 = int(np.searchsorted(P['ws0'], c, side='left'))
                            fl += piantate[P['nome']][j0:j1]
                        fl = torch.tensor(fl, dtype=torch.bool)
                        tot['nat_piantate'] += float(-u['tot'][fl].sum())
                        tot['segni_piantate'] += int(u['segni'][fl].sum())
                    nuova = u['nuova']
                    tot['nat_nuove'] += float(-u['tot'][nuova].sum())
                    tot['segni_nuove'] += int(u['segni'][nuova].sum())
                    tot['nat_note'] += float(-u['tot'][~nuova].sum())
                    tot['segni_note'] += int(u['segni'][~nuova].sum())
            else:
                if tipo == 'W3':
                    bt = lotto_tratto(righe, ctx, 'W3', None)
                    X, Y, Mk, t, pw = a_torch(bt, 'W3')
                else:
                    bt = GM.lotto_tratto(righe, ctx, 1)
                    X, Y, Mk, t, pw = GM.a_torch(bt, 1)
                H = m.H
                h1 = torch.stack([s_.h1 if s_.h1 is not None else torch.zeros(H) for s_ in st])[None]
                h2 = torch.stack([s_.h2 if s_.h2 is not None else torch.zeros(H) for s_ in st])[None]
                with torch.no_grad():
                    out = m(X, t, h1, h2) if tipo == 'W3' else m(X, t, h1, h2, None)
                    lp = torch.log_softmax(out['logits'], -1)
                    tl = -(lp.gather(2, Y[..., None])[..., 0] * Mk)
                    for b, (P, (a, c)) in enumerate(righe):
                        for j, (s, e) in enumerate(P['words']):
                            if a <= s - 1 < c:
                                nat = float(tl[b, s - 1 - a:e - a].sum())
                                if piantate is not None and piantate[P['nome']][j]:
                                    tot['nat_piantate'] += nat
                                    tot['segni_piantate'] += e - s + 1
                                if tipo == 'W3' and piantate is not None:
                                    ap = out['porta'][b, s - 1 - a:e - a]
                                    k_ = 'porta_piantate' if piantate[P['nome']][j] else 'porta_altre'
                                    tot[k_] += float(ap.sum())
                                    tot[k_ + '_n'] += int(ap.numel())
                                if P['units'][j] in lex.idx:
                                    tot['nat_note'] += nat
                                    tot['segni_note'] += e - s + 1
                                else:
                                    tot['nat_nuove'] += nat
                                    tot['segni_nuove'] += e - s + 1
                    for b, s_ in enumerate(st):
                        n = int(bt['lens'][b])
                        s_.h1 = out['y1'][b, n - 1].detach().clone()
                        s_.h2 = out['y2'][b, n - 1].detach().clone()
            r += 1
    m.train(vecchio)
    return tot


def parametri_appresi(m):
    import torch
    import torch.nn.functional as F_
    with torch.no_grad():
        if m.tipo == 'W3':
            return OrderedDict(porta_bias=round(float(m.gate.bias), 4), porta_peso_norma=round(float(m.gate.weight.norm()), 4), porta_posto=[round(float(x), 4) for x in m.gb])
        o = OrderedDict(kappa=[round(float(x), 4) for x in m.kap], gamma=[round(float(x), 4) for x in m.gm], tau=[round(float(x), 4) for x in F_.softmax(m.tau, 0)])
        if m.tipo == 'W2':
            o['beta'] = [round(float(x), 4) for x in m.beta]
            o['gam_pagina'] = round(float(m.gam), 4)
        return o


# ---------------------------------------------------------------- scrivere segno per segno

class Penna24(GM.Penna20):
    """Come GM.Penna20 (M1 come base) piu': W3 la spinta delle caselle sui logit; W1 e W2 le funzioni per scegliere a inizio parola fra libero, lessico e (W2) pagina."""

    def __init__(self, m, ctx, lex, hmm, capacita=6000):
        super().__init__(m, ctx, capacita)
        self.tipo = m.tipo
        self.lex, self.hmm = lex, hmm
        self.lg_ultimo = None
        if self.tipo == 'W3':
            self.gw = m.gate.weight.detach()[0].double().numpy()
            self.gbias = float(m.gate.bias.detach())
            self.gb = [float(x) for x in m.gb.detach()]

    def dai(self, tok):
        lg = super().dai(tok)
        tok = int(tok)
        if self.tipo == 'W3':
            ctx = self.ctx
            if tok == ctx.SP or ctx.N0 <= tok < ctx.N0 + ctx.nbins or tok >= ctx.u0:
                p = tuple(self.corrente)
                q_log = self.hmm.predittivo(p)
                U, u0, SP, EOL = ctx.U, ctx.u0, ctx.SP, ctx.EOL
                z = np.array(lg, dtype=np.float64)
                pg = np.exp(z - z.max())
                pg /= pg.sum()
                a = 1.0 / (1.0 + math.exp(-(float(self.gw @ self.hd.double().numpy()) + self.gbias + self.gb[min(len(p), NBK - 1)])))
                ps = np.exp(q_log)
                pt = pg[SP] + pg[EOL] + 1e-12
                q = np.zeros_like(pg)
                q[u0:u0 + U] = ps[:U]
                q[SP] = ps[U] * pg[SP] / pt
                q[EOL] = ps[U] * pg[EOL] / pt
                mix = (1.0 - a) * pg + a * q
                lg = np.log(np.maximum(mix, 1e-30)).tolist()
        self.lg_ultimo = lg
        return lg

    def avanti(self, glifi):
        """Logit (n, V) dopo aver dato in piu' ciascun glifo di `glifi` (indici di unita') allo stato corrente, senza cambiarlo."""
        torch, m = self.torch, self.m
        n = len(glifi)
        with torch.inference_mode():
            y1 = self.h1[0].expand(n, -1).contiguous()
            y2 = self.h2[0].expand(n, -1).contiguous()
            return m.avanti_glifi(y1, y2, torch.tensor(glifi, dtype=torch.long))

    def tabella_coppie(self):
        """(U, U + 1) numpy: log della probabilita' dei primi due glifi (o glifo e fine) dopo lo stato corrente (come `coppie` del modello)."""
        ctx = self.ctx
        U, u0 = ctx.U, ctx.u0
        lg = np.array(self.lg_ultimo, dtype=np.float64)
        lp = lg - (lg.max() + math.log(np.exp(lg - lg.max()).sum()))
        L2 = self.avanti(list(range(U))).double().numpy()
        L2 = L2 - (L2.max(1, keepdims=True) + np.log(np.exp(L2 - L2.max(1, keepdims=True)).sum(1, keepdims=True)))
        fine = np.logaddexp(L2[:, ctx.SP], L2[:, ctx.EOL])
        due = np.concatenate([L2[:, u0:u0 + U], fine[:, None]], 1)
        return lp[u0:u0 + U][:, None] + due

    def miscela(self, cand, T):
        """Probabilita' a inizio parola: (pi_libero, pi_lessico[3], pi_pagina[S, nt] o None). `T`: tabella_coppie."""
        torch, m, ctx = self.torch, self.m, self.ctx
        U = ctx.U
        with torch.inference_mode():
            lm = m.mix(self.hd[None, :])
            if self.tipo == 'W2' and cand:
                S = ctx.S
                Fc = np.zeros((1, S, ctx.nf), np.float32)
                valid = np.zeros((1, S), bool)
                logg = np.zeros((1, S), np.float32)
                for k, (un, f) in enumerate(cand):
                    Fc[0, k] = f
                    valid[0, k] = True
                    logg[0, k] = T[un[0], un[1] if len(un) > 1 else U]
                lc = m.logit_candidati(self.hd[None, :], torch.from_numpy(Fc), torch.from_numpy(valid), torch.from_numpy(logg))
                tutti = torch.cat([lm, lc.reshape(1, -1)], 1)
            else:
                tutti = lm
            lpi = torch.log_softmax(tutti, 1)[0].exp().numpy()
        pc = lpi[4:].reshape(-1, m.cfg['nt']) if self.tipo == 'W2' and cand else None
        return float(lpi[0]), lpi[1:4], pc

    def pesi_sorgenti(self, T, gruppo):
        """Probabilita' di scegliere ogni parola del lessico come sorgente (gruppo 0: tutto il lessico, per 0 e 1 modifiche; gruppo 1: le prime K2, per 2 modifiche)."""
        m, lex = self.m, self.lex
        kap, gm = float(m.kap[gruppo].detach()), float(m.gm[gruppo].detach())
        K = lex.K2 if gruppo == 1 else len(lex.parole)
        n = lex.n[:K].astype(np.float64)
        lw = kap * np.log(n) + gm * T.reshape(-1)[lex.pair[:K]]
        lw -= lw.max()
        p = np.exp(lw)
        return p / p.sum()

    def tabelle_tipo(self):
        torch, m = self.torch, self.m
        with torch.inference_mode():
            p = torch.softmax(m.tau, 0).double().numpy()
        return p / p.sum()


# ---------------------------------------------------------------- testi sintetici con parole nuove piantate

def sintetico_nuove(righe, seme, divisore, unita, modo='senza', p_nuove=0.3, n_sorgenti=100, n_caselle=6, info_out=None):
    """Una copia del libro (`righe`: dizionari come ia07.libro_vero()) con le stesse righe e lunghezze, parole pescate dalla frequenza del libro e, con probabilita'
    `p_nuove`, una parola NUOVA piantata:
    - modo 'ritocchi': ritocco di una delle `n_sorgenti` parole piu' frequenti del libro (scelta con la sua frequenza); una modifica con probabilita' 0,7, due con 0,3;
      ogni modifica e' un glifo cambiato (0,4), aggiunto (0,3) o tolto (0,3) in un posto a caso, con un glifo a caso fra quelli del libro; la parola ritoccata non e' mai una
      parola del libro;
    - modo 'caselle': una parola della grammatica a caselle piantata: i glifi si dividono a caso in `n_caselle` caselle; la parola passa per le caselle in ordine e per ognuna
      prende (probabilita' 0,9 0,6 0,85 0,6 0,8 0,5, la prima casella e' sempre presente se la parola sarebbe vuota) un glifo a caso della casella; la parola non e' mai una parola
      del libro;
    - modo 'senza': nessuna parola piantata.
    Se `info_out` e' un dizionario ci mette cio' che serve alle misure: le sorgenti, la divisione in caselle, l'insieme delle parole del libro."""
    rng = random.Random(seme)
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    vocset = set(voc)
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    frequenti = sorted(conti, key=lambda w: (-conti[w], w))[:n_sorgenti]
    cum_f, tf = [], 0.0
    for w in frequenti:
        tf += conti[w]
        cum_f.append(tf)
    glifi = list(unita)
    rng_c = random.Random(seme + 17)
    perm = glifi[:]
    rng_c.shuffle(perm)
    caselle = [perm[k::n_caselle] for k in range(n_caselle)]
    p_c = (0.9, 0.6, 0.85, 0.6, 0.8, 0.5, 0.7, 0.5, 0.6, 0.5)

    def una_modifica(u):
        u = list(u)
        tp = rng.choices((1, 2, 3), weights=(0.4, 0.3, 0.3))[0]
        if tp == 1:
            i = rng.randrange(len(u))
            nuovo = rng.choice(glifi)
            if nuovo == u[i]:
                return None
            u[i] = nuovo
        elif tp == 2:
            u.insert(rng.randrange(len(u) + 1), rng.choice(glifi))
        else:
            if len(u) < 2:
                return None
            del u[rng.randrange(len(u))]
        return u

    def ritocco():
        for _ in range(40):
            src = frequenti[min(bisect.bisect_right(cum_f, rng.random() * tf), len(frequenti) - 1)]
            u = list(divisore(src))
            for _k in range(1 if rng.random() < 0.7 else 2):
                u = una_modifica(u)
                if u is None:
                    break
            if u is None:
                continue
            w = ''.join(u)
            if w not in vocset and divisore(w) == u:
                return w
        return fresca()

    def a_caselle():
        for _ in range(40):
            u = []
            for k in range(n_caselle):
                if rng.random() < p_c[k % len(p_c)]:
                    u.append(rng.choice(caselle[k]))
            if not u:
                u = [rng.choice(caselle[0])]
            w = ''.join(u)
            if w not in vocset and divisore(w) == u:
                return w
        return fresca()

    if info_out is not None:
        info_out.update(sorgenti=list(frequenti), caselle=[list(c) for c in caselle], vocabolario=vocset)
    out = []
    piantate = {}
    for x in righe:
        n = len(x['parole'])
        ps = []
        fl = piantate.setdefault(x['pagina'], [])
        for k in range(n):
            if modo == 'ritocchi' and rng.random() < p_nuove:
                w = ritocco()
                fl.append(True)
            elif modo == 'caselle' and rng.random() < p_nuove:
                w = a_caselle()
                fl.append(True)
            else:
                w = fresca()
                fl.append(False)
            ps.append(w)
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    if info_out is not None:
        info_out['piantate'] = piantate                      # pagina -> per ogni parola (in ordine) se e' una parola piantata
    return out


def conforme_caselle(u, caselle):
    """Una parola (lista di glifi) e' "a caselle" se ogni glifo sta in una casella e le caselle crescono strettamente (una sola volta per casella)."""
    casella = {g: k for k, c in enumerate(caselle) for g in c}
    ks = [casella.get(g) for g in u]
    return all(k is not None for k in ks) and all(a < b for a, b in zip(ks, ks[1:]))
