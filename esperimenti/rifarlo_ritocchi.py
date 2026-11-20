# -*- coding: utf-8 -*-
"""Strumenti di ia11 (modulo di supporto, non e' un esperimento): i "ritocchi" dei libri generati e le misure per tararli.

Un testo e' un OrderedDict pagina -> righe; una riga e' (inizio_paragrafo, [parola, ...]); una parola e' una tupla di segni
(glifi EVA fusi), come in ia01. I ritocchi sono post-elaborazioni di un testo gia' generato: non toccano il voynichizzatore.

Che cosa c'e' qui, in parole semplici:
- `eco`: l'"eco della pagina" (una parola e' sostituita da una parola, o da una variante a una modifica, scritta prima sulla
  stessa pagina, con un peso che cala con la distanza), e la sua misura (`eco_testo`, tasso di parole uguali o a una modifica
  in sette fasce di distanza, al netto di una pagina di riferimento a caso);
- `riordina`: l'"ordine delle famiglie" (le parole interne di una riga si rimettono in fila in modo che i passaggi fra
  famiglie seguano la tabella delle vere, tenendo ferme la prima e l'ultima parola e il contatto ultimo -> primo glifo);
- `correggi_forma`: la "forma" delle parole nuove (le parole mai viste si avvicinano di una o due modifiche a forme piu' normali);
- `ritocco_casuale`: il controllo negativo (stessa entita' dei ritocchi, nessuna struttura);
- misure: guadagno delle famiglie (D) con un modello di famiglie, informazione mutua del contatto, costo di forma delle parole nuove.
Nessun risultato e' scritto qui e nessuna parola della trascrizione compare in questo file.
"""
import bisect
import math
import os
import random
import sys
import types
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)

RARO = '¤'
NB = 7                                  # fasce di distanza, come ia09: S1, S2, S3, R1, R2, R4, R8
NOMI_FASCE = ['S1', 'S2', 'S3', 'R1', 'R2', 'R4', 'R8']
FINESTRA_MAX = 400                      # al massimo tante parole indietro come fonte dell'eco
FREQ_SOGLIA = 20                        # una parola e' "frequente" se compare almeno tante volte nelle pagine di addestramento


# ---------------------------------------------------------------- struttura delle pagine e fasce di distanza

def struttura(rows):
    """Per ogni parola: riga e posto nella riga; inizio di ogni riga (piu' la fine)."""
    L, J, ls = [], [], [0]
    for l, (_, ws) in enumerate(rows):
        for j in range(len(ws)):
            L.append(l)
            J.append(j)
        ls.append(ls[-1] + len(ws))
    return np.array(L, dtype=np.int64), np.array(J, dtype=np.int64), np.array(ls, dtype=np.int64)


def intervalli_bande(L, J, ls):
    """Intervalli [a, b) di indici di parola delle sette fasce (come ia09, `Finestre.intervalli`): S1 la parola subito prima, S2 la
    seconda prima, S3 le altre della riga; R1 la riga sopra, R2 due-tre righe sopra, R4 quattro-sette, R8 otto o piu'."""
    T = len(L)
    nl = len(ls) - 1
    a = np.zeros((T, NB), dtype=np.int64)
    b = np.zeros((T, NB), dtype=np.int64)

    def riga(x):
        return int(ls[min(max(x, 0), nl)])
    for t in range(T):
        l, j = int(L[t]), int(J[t])
        if j >= 1:
            a[t, 0], b[t, 0] = t - 1, t
        if j >= 2:
            a[t, 1], b[t, 1] = t - 2, t - 1
        if j >= 3:
            a[t, 2], b[t, 2] = t - j, t - 2
        if l >= 1:
            a[t, 3], b[t, 3] = riga(l - 1), riga(l)
        if l >= 2:
            a[t, 4], b[t, 4] = riga(l - 3), riga(l - 1)
        if l >= 4:
            a[t, 5], b[t, 5] = riga(l - 7), riga(l - 3)
        if l >= 8:
            a[t, 6], b[t, 6] = 0, riga(l - 7)
    return a, b


# ---------------------------------------------------------------- parole a una modifica

def vicini_tipi(tipi):
    """dict tipo -> insieme dei tipi (fra quelli dati) a una modifica (sostituzione, inserimento, cancellazione di un segno):
    stessa nozione di `sintassi_modelli.dist1`, ma con chiavi (veloce su migliaia di tipi)."""
    tl = set(tipi)
    jolly = defaultdict(list)
    canc = defaultdict(list)
    for w in tl:
        n = len(w)
        for i in range(n):
            jolly[(i, w[:i], w[i + 1:])].append(w)
            if n >= 2:
                canc[w[:i] + w[i + 1:]].append(w)
    nb = defaultdict(set)
    for ws in jolly.values():
        if len(ws) > 1:
            for x in ws:
                for y in ws:
                    if x != y:
                        nb[x].add(y)
    for k, lunghe in canc.items():
        if k in tl:
            for x in lunghe:
                nb[x].add(k)
                nb[k].add(x)
    return nb


def matrici(ta, tb, nb):
    """Matrici booleane (len(ta), len(tb)): parola uguale, parola a una modifica."""
    u = {}
    ia = np.array([u.setdefault(w, len(u)) for w in ta], dtype=np.int64)
    ib = np.array([u.setdefault(w, len(u)) for w in tb], dtype=np.int64)
    A = np.zeros((len(u), len(u)), dtype=bool)
    for w, i in u.items():
        for n in nb.get(w, ()):
            j = u.get(n)
            if j is not None:
                A[i, j] = True
    return ia[:, None] == ib[None, :], A[ia[:, None], ib[None, :]]


def _presenza(M, a, b):
    cs = np.concatenate([np.zeros((M.shape[0], 1), dtype=np.int64), np.cumsum(M, axis=1)], axis=1)
    righe = np.arange(M.shape[0])[:, None]
    return (cs[righe, b] - cs[righe, a]) > 0


def conti_eco(ta, tb, a, b, nb, rara=None):
    """Per una pagina `ta` (lista di parole) e una pagina di riferimento `tb`: per ogni fascia, quante parole hanno una parola uguale (x)
    o a una modifica (e) nella fascia della propria pagina e nella stessa fascia (stessi indici) della pagina di riferimento; le parole
    con parola UGUALE si contano a parte per le parole frequenti (f) e per quelle rare (r), perche' il guadagno di copia di ia09 pesa molto di piu'
    la ripetizione di parole rare. Righe della matrice (9, NB): x_f propria, x_f riferimento, x_r propria, x_r riferimento, e propria,
    e riferimento, parole frequenti con fascia non vuota, parole rare con fascia non vuota, tutte con fascia non vuota."""
    T = len(ta)
    rara = np.zeros(T, dtype=bool) if rara is None else np.asarray(rara, dtype=bool)
    valido = b > a
    Mx, Me = matrici(ta, ta, nb)
    own_x = _presenza(Mx, a, b) & valido
    own_e = _presenza(Me, a, b) & valido
    Tb = len(tb)
    ar, br = np.minimum(a, Tb), np.minimum(b, Tb)
    Mxr, Mer = matrici(ta, tb, nb)
    ref_x = _presenza(Mxr, ar, br) & valido
    ref_e = _presenza(Mer, ar, br) & valido
    fr = ~rara[:, None]
    rr = rara[:, None]
    return np.stack([(own_x & fr).sum(0), (ref_x & fr).sum(0), (own_x & rr).sum(0), (ref_x & rr).sum(0), own_e.sum(0), ref_e.sum(0),
                     (valido & fr).sum(0), (valido & rr).sum(0), valido.sum(0)]).astype(float)


def derangement(nomi, seme):
    nomi = list(nomi)
    rnd = random.Random(seme)
    for _ in range(1000):
        perm = nomi[:]
        rnd.shuffle(perm)
        if all(x != y for x, y in zip(nomi, perm)):
            return dict(zip(nomi, perm))
    return {x: nomi[(i + 1) % len(nomi)] for i, x in enumerate(nomi)}


def eco_testo(pagine, seme=1, freq=None):
    """Eco di un testo: vettore di 3 x NB numeri, (parole con una parola UGUALE nella fascia, al netto del riferimento) / parole con la fascia
    non vuota, per le parole frequenti, poi per le rare, poi "a UNA MODIFICA" per tutte. Frequente = almeno FREQ_SOGLIA occorrenze in `freq`
    (un Counter di parole; senza `freq` tutte le parole sono frequenti). Il riferimento e' la stessa fascia (stessi indici di parola) di un'altra
    pagina del testo (permutazione senza punti fissi). Restituisce (vettore, somme (9, NB))."""
    nomi = list(pagine)
    perm = derangement(nomi, seme)
    ws = {p: [w for _, r in pagine[p] for w in r] for p in nomi}
    nb = vicini_tipi(w for x in ws.values() for w in x)
    S = np.zeros((9, NB))
    for p in nomi:
        L, J, ls = struttura(pagine[p])
        a, b = intervalli_bande(L, J, ls)
        rara = [(freq.get(w, 0) < FREQ_SOGLIA) for w in ws[p]] if freq is not None else None
        S += conti_eco(ws[p], ws[perm[p]], a, b, nb, rara)
    return vettore_eco(S), S


def vettore_eco(S):
    S = np.asarray(S, dtype=float)
    df, dr, dt = np.maximum(S[6], 1.0), np.maximum(S[7], 1.0), np.maximum(S[8], 1.0)
    return np.concatenate([(S[0] - S[1]) / df, (S[2] - S[3]) / dr, (S[4] - S[5]) / dt])


# ---------------------------------------------------------------- tabelle: contatto ultimo -> primo glifo e forma delle parole

class Contatto:
    """Rapporto P(primo glifo della parola dopo | ultimo glifo) / P(primo glifo), con lisciatura, dalle righe delle pagine date.
    L'indice G (ultimo posto) vale "glifo sconosciuto o assente": rapporto 1."""

    def __init__(self, pagine, lam=5.0, tetto=20.0):
        glifi = sorted({g for rows in pagine.values() for _, ws in rows for w in ws for g in w})
        self.idx = {g: i for i, g in enumerate(glifi)}
        G = self.G = len(glifi)
        c = np.zeros((G, G))
        pf = np.zeros(G)
        for rows in pagine.values():
            for _, ws in rows:
                for w in ws:
                    pf[self.idx[w[0]]] += 1
                for x, y in zip(ws, ws[1:]):
                    c[self.idx[x[-1]], self.idx[y[0]]] += 1
        pf = (pf + 0.5) / (pf.sum() + 0.5 * G)
        P = (c + lam * pf[None, :]) / (c.sum(1, keepdims=True) + lam)
        R = np.clip(P / pf[None, :], 1.0 / tetto, tetto)
        self.R = np.ones((G + 1, G + 1))
        self.R[:G, :G] = R

    def f(self, w):
        return self.idx.get(w[0], self.G)

    def l(self, w):
        return self.idx.get(w[-1], self.G)


class Forma:
    """Forma dei glifi dentro la parola: trigrammi di glifi con fine parola, lisciatura di Witten-Bell (come `sintassi_modelli.Modello`,
    codice copiato e ridotto). Serve a (1) scegliere come si modifica una parola di un segno, (2) misurare il costo di forma delle
    parole nuove, (3) correggerle."""

    def __init__(self, cnt):
        glifi = sorted({g for w in cnt for g in w})
        self.glifi = glifi
        self.idx = {g: i for i, g in enumerate(glifi)}
        q = self.q = len(glifi) + 1                    # l'ultimo indice e' il segno raro; q e' il margine (inizio e fine parola)
        c1 = np.zeros(q + 1)
        c2 = np.zeros((q + 1, q + 1))
        c3 = np.zeros((q + 1, q + 1, q + 1))
        for w, k in cnt.items():
            a = b = q
            for x in [self.idx[g] for g in w] + [q]:
                c3[a, b, x] += k
                c2[b, x] += k
                c1[x] += k
                a, b = b, x
        t1 = float((c1 > 0).sum())
        p1 = (c1 + t1 / (q + 1)) / (c1.sum() + t1)
        n2, t2 = c2.sum(1), (c2 > 0).sum(1)
        d2 = n2 + t2
        p2 = np.where(d2[:, None] == 0, p1[None, :], (c2 + t2[:, None] * p1[None, :]) / np.maximum(d2, 1)[:, None])
        n3, t3 = c3.sum(2), (c3 > 0).sum(2)
        d3 = n3 + t3
        p3 = np.where(d3[..., None] == 0, p2[None, :, :], (c3 + t3[..., None] * p2[None, :, :]) / np.maximum(d3, 1)[..., None])
        self.l3 = np.log2(np.maximum(p3, 1e-12))
        self._vic, self._mod, self._bit = {}, {}, {}

    def bit(self, w):
        v = self._bit.get(w)
        if v is None:
            a = b = self.q
            v = 0.0
            for x in [self.idx.get(g, self.q - 1) for g in w] + [self.q]:
                v -= float(self.l3[a, b, x])
                a, b = b, x
            self._bit[w] = v
        return v

    def vicini(self, w):
        """Tutte le parole a una modifica (non vuote), in ordine fisso."""
        v = self._vic.get(w)
        if v is None:
            n = len(w)
            out = set()
            for i in range(n):
                for g in self.glifi:
                    if g != w[i]:
                        out.add(w[:i] + (g,) + w[i + 1:])
                if n > 1:
                    out.add(w[:i] + w[i + 1:])
            for i in range(n + 1):
                for g in self.glifi:
                    out.add(w[:i] + (g,) + w[i:])
            out.discard(w)
            v = self._vic[w] = sorted(out)
        return v

    def modifica(self, w, rnd):
        """Una parola a una modifica da `w`, scelta con probabilita' proporzionale alla probabilita' di forma."""
        m = self._mod.get(w)
        if m is None:
            vs = self.vicini(w)
            pr = np.array([2.0 ** (-self.bit(x)) for x in vs])
            m = self._mod[w] = (vs, np.cumsum(pr / pr.sum()))
        i = min(int(np.searchsorted(m[1], rnd.random())), len(m[0]) - 1)
        return m[0][i]

    def correggi(self, w, mosse=2):
        """Fino a `mosse` passi greedy verso una forma piu' probabile (di una modifica alla volta)."""
        for _ in range(mosse):
            migliore, bm = w, self.bit(w)
            for x in self.vicini(w):
                bx = self.bit(x)
                if bx < bm - 1e-9:
                    migliore, bm = x, bx
            if migliore == w:
                break
            w = migliore
        return w


# ---------------------------------------------------------------- ritocchi

def eco_pagina(rows, par, forma, ct, rnd, freq=None):
    """ECO: ogni parola (dalla seconda) e' sostituita, con probabilita' `p`, da una parola gia' scritta prima sulla stessa pagina
    (nella versione gia' ritoccata): la fonte e' scelta con peso exp(-distanza in parole / tau) per il contatto ultimo -> primo glifo con
    la parola prima e con la parola dopo e per (frequenza della fonte + 1)^(-gamma) (gamma > 0 favorisce le parole rare); con probabilita'
    `q` la copia e' cambiata di una modifica (scelta secondo la forma)."""
    p, tau, q, gamma = par['p'], par['tau'], par['q'], par.get('gamma', 0.0)
    if p <= 0:
        return rows
    L, J, ls = struttura(rows)
    orig = [w for _, r in rows for w in r]
    n = len(orig)
    out = list(orig)
    fi = np.array([ct.f(w) for w in orig], dtype=np.int64)
    la = np.array([ct.l(w) for w in orig], dtype=np.int64)
    lun_riga = [len(r) for _, r in rows]
    inv = np.array([(freq.get(w, 0) + 1.0) ** (-gamma) for w in orig]) if (gamma and freq is not None) else None
    for t in range(1, n):
        if rnd.random() >= p:
            continue
        j0 = max(0, t - FINESTRA_MAX)
        peso = np.exp(-(t - np.arange(j0, t)) / tau)
        if inv is not None:
            peso = peso * inv[j0:t]
        if J[t] >= 1:
            peso = peso * ct.R[la[t - 1], fi[j0:t]]
        if J[t] + 1 < lun_riga[L[t]]:
            peso = peso * ct.R[la[j0:t], fi[t + 1]]
        cum = np.cumsum(peso)
        j = j0 + min(int(np.searchsorted(cum, rnd.random() * cum[-1])), t - j0 - 1)
        w = out[j]
        if rnd.random() < q:
            w = forma.modifica(w, rnd)
        out[t] = w
        fi[t], la[t] = ct.f(w), ct.l(w)
        if inv is not None:
            inv[t] = (freq.get(w, 0) + 1.0) ** (-gamma)
    return _rimetti(rows, out)


def _rimetti(rows, ws):
    new, k = [], 0
    for ini, r in rows:
        new.append((ini, ws[k:k + len(r)]))
        k += len(r)
    return new


def riordina_riga(ws, fam, lr, ct, lam, mu, rnd):
    """Rimette in fila le parole INTERNE di una riga (la prima e l'ultima restano ferme): ogni posto e' scelto fra le parole che restano
    con peso 2^(lam * guadagno di famiglia del passaggio) * (rapporto di contatto)^mu. Guadagno = log2 P(d|c) - log2 P(d) (bit)."""
    if len(ws) < 4:
        return ws
    out = [ws[0]]
    resto = list(ws[1:-1])
    while resto:
        c, u = fam(out[-1]), ct.l(out[-1])
        peso = np.array([2.0 ** (lam * lr[c, fam(w)]) * ct.R[u, ct.f(w)] ** mu for w in resto])
        cum = np.cumsum(peso)
        i = min(int(np.searchsorted(cum, rnd.random() * cum[-1])), len(resto) - 1)
        out.append(resto.pop(i))
    out.append(ws[-1])
    return out


def riordina_pagina(rows, par, fam, lr, ct, rnd):
    """ORDINE: una frazione `s` delle righe (scelta a caso) e' rimessa in fila con forza `lam`; le altre restano come sono."""
    s, lam, mu = par['s'], par['lam'], par.get('mu', 1.0)
    if s <= 0:
        return rows
    new = []
    for ini, ws in rows:
        if rnd.random() < s:
            ws = riordina_riga(ws, fam, lr, ct, lam, mu, rnd)
        new.append((ini, ws))
    return new


def correggi_pagina(rows, noti, forma, r, rnd):
    """FORMA: ogni parola NUOVA (non fra le `noti`) e' corretta, con probabilita' `r`, di una o due modifiche verso una forma piu' normale."""
    if r <= 0:
        return rows
    new = []
    for ini, ws in rows:
        nw = []
        for w in ws:
            if w not in noti and rnd.random() < r:
                w = forma.correggi(w)
            nw.append(w)
        new.append((ini, nw))
    return new


def ritocco_casuale(pagine, par_eco, par_ord, forma, rnd):
    """CONTROLLO NEGATIVO: stessa entita' di eco e di riordino, nessuna struttura. Una frazione `p` di parole e' sostituita da una parola
    scelta a caso fra tutte quelle del testo (con probabilita' `q` cambiata di una modifica); una frazione `s` di righe ha le parole
    interne rimescolate a caso."""
    tutte = [w for rows in pagine.values() for _, ws in rows for w in ws]
    out = OrderedDict()
    for pg, rows in pagine.items():
        new = []
        for ini, ws in rows:
            ws = list(ws)
            for k in range(len(ws)):
                if rnd.random() < par_eco['p']:
                    w = tutte[rnd.randrange(len(tutte))]
                    if rnd.random() < par_eco['q']:
                        w = forma.modifica(w, rnd)
                    ws[k] = w
            if len(ws) >= 4 and rnd.random() < par_ord['s']:
                mid = ws[1:-1]
                rnd.shuffle(mid)
                ws = [ws[0]] + mid + [ws[-1]]
            new.append((ini, ws))
        out[pg] = new
    return out


# ---------------------------------------------------------------- famiglie (modello di ia10) e misure

def seq_pagine(pagine, ix, NV):
    tok, linea, pag = [], [], []
    k = 0
    for i, rows in enumerate(pagine.values()):
        for _, ws in rows:
            for w in ws:
                tok.append(ix.get(w, NV))
                linea.append(k)
                pag.append(i)
            k += 1
    return np.array(tok, dtype=np.int64), np.array(linea, dtype=np.int64), np.array(pag, dtype=np.int64)


class FamiglieModello:
    """Famiglie di parole e tabella dei passaggi imparate con la procedura di ia10 (importata, non modificata). `K` None: si sceglie
    sulla validazione come ia10; `K` dato: si usa quello."""

    def __init__(self, I10, pagine_add, pagine_val=None, K=None, seme=1):
        FC = I10.FC
        ns = lambda pg: types.SimpleNamespace(pagine=pg, etichette=None)
        sA = I10.Seq(ns(pagine_add), list(pagine_add))
        self.voc, cont = I10.vocabolario(sA)
        self.NV = NV = len(self.voc)
        self.ix = {w: i for i, w in enumerate(self.voc)}
        tA = sA.ids(self.ix, NV)
        if K is None:
            sV = I10.Seq(ns(pagine_val), list(pagine_val))
            tV = sV.ids(self.ix, NV)
            ris, K, (a, b) = I10.adatta_e_scegli(tA, sA.linea, tV, sV.linea, NV, seme)
            self.cls, self.tr = ris[K]['cls'], ris[K]['tr']
        else:
            p = FC.coppie_di(tA, sA.linea)
            a, b = tA[p], tA[p + 1]
            self.cls, _ = FC.adatta_famiglie(a, b, NV, K, seme, giri=I10.GIRI)
            self.tr = FC.Transizioni(a, b, self.cls, K)
        self.K = K
        self.fam_dict = {w: int(self.cls[i]) for i, w in enumerate(self.voc)}
        self.noti = set(w for rows in pagine_add.values() for _, ws in rows for w in ws)
        self.copertura = float(np.mean(tA < NV))

    def fam(self, w):
        return self.fam_dict.get(w, self.K)


def stat_D(I10, M, pagine, rnd_seed, nrim):
    """Per pagina: [somma dei guadagni, coppie] nell'ordine vero e (media di `nrim` rimescolamenti dentro la riga) con le parole rimescolate."""
    FC = I10.FC
    tok, linea, pag = seq_pagine(pagine, M.ix, M.NV)
    n = len(pagine)
    P = I10.punteggi(M.tr, M.cls, tok, linea, pag, n, M.NV)[:, :2]
    rng = np.random.default_rng(rnd_seed)
    R = np.zeros((n, 2))
    for _ in range(nrim):
        R += I10.punteggi(M.tr, M.cls, FC.rimescola_in_riga(tok, linea, rng), linea, pag, n, M.NV)[:, :2]
    return P, R / max(nrim, 1)


def D_da(P, R):
    return float((P[:, 0].sum() - R[:, 0].sum()) / max(P[:, 1].sum(), 1.0))


def mi_contatto(pagine, nrim=5, seme=1):
    """Contatto fra l'ultimo glifo di una parola e il primo della successiva (stessa riga): informazione mutua (bit) meno quella dello
    stesso testo con le parole rimescolate dentro la riga: e' il "g" di ia08 (H1)."""
    def mi(coppie):
        c = Counter(coppie)
        n = sum(c.values())
        pa, pb = Counter(), Counter()
        for (x, y), v in c.items():
            pa[x] += v
            pb[y] += v
        return sum(v / n * math.log2(v * n / (pa[x] * pb[y])) for (x, y), v in c.items())
    righe = [ws for rows in pagine.values() for _, ws in rows]
    base = mi([(a[-1], b[0]) for ws in righe for a, b in zip(ws, ws[1:])])
    rnd = random.Random(seme)
    rim = []
    for _ in range(nrim):
        cp = []
        for ws in righe:
            ws = list(ws)
            rnd.shuffle(ws)
            cp += [(a[-1], b[0]) for a, b in zip(ws, ws[1:])]
        rim.append(mi(cp))
    return base - float(np.mean(rim))


def costo_nuove(forma, pagine, noti):
    """Costo di forma delle parole NUOVE (non fra le `noti`): [bit totali, glifi totali, numero di parole nuove, parole totali]."""
    bit = gl = nn = tot = 0
    for rows in pagine.values():
        for _, ws in rows:
            for w in ws:
                tot += 1
                if w not in noti:
                    bit += forma.bit(w)
                    gl += len(w)
                    nn += 1
    return [float(bit), float(gl), nn, tot]
