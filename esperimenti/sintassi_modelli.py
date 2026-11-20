# -*- coding: utf-8 -*-
"""Modelli di conteggio per ia09 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- `Corpus`: un testo messo in numeri (parole = tipi, glifi = numeri) con righe e posizioni.
- `Modello`: per una piega, un modello di base delle parole (frequenza + forma dei glifi) e le "bende": modelli che vedono
  solo un pezzo del contesto (parola prima, ultimo glifo della prima, ...), addestrati sulle pagine di addestramento.
- `Finestre`: la "copia": quanto una parola somiglia (uguale o a una modifica) alle parole scritte prima sulla stessa pagina,
  per distanza (stessa riga, righe sopra), oppure alle parole di una pagina a caso (riferimento).
- `em`: pesi di una miscela di modelli, trovati su pagine di validazione.
- generatori sintetici (`genera_grammatica`, `genera_copia`), controlli positivi: costruiti su un testo qualunque dato.

Tutti i modelli danno una vera probabilita' alle parole (e al primo glifo): sommano a 1, cosi' i bit sono confrontabili.
Nessun risultato e' scritto qui.
"""
import bisect
import math
import random
from collections import Counter, OrderedDict, defaultdict

import numpy as np

RARO = '¤'
BANDE = ['S1', 'S2', 'S3', 'R1', 'R2', 'R4', 'R8']      # prima parola, seconda, altre della riga; 1 riga sopra, 2-3, 4-7, 8+
VICINE = ['S1', 'S2', 'S3', 'R1']
LONTANE = ['R2', 'R4', 'R8']
SIMILI_BANDE = 5                                       # per il segno "c'e' una parola simile vicina": bande S1, S2, S3, R1, R2
GRAM = ['b', 'c', 'd', 'e', 'e2', 'cd', 'i1', 'i2']    # bende di grammatica (contesto di parole prima)
BENDE = GRAM + ['f']
BETA = [0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 65536, 1e6, 1e9]   # 1e9 = "come la base"
MIN_CLASSE = 6                                         # parole con almeno tante occorrenze entrano nelle classi
K_CLASSI = 10


# ---------------------------------------------------------------- distanza di modifica

def dist1(a, b):
    """Vero se le tuple a e b sono a una modifica (sostituzione, inserimento, cancellazione) di distanza (come e310)."""
    la, lb = len(a), len(b)
    if la == lb:
        if a == b:
            return False
        d = 0
        for x, y in zip(a, b):
            if x != y:
                d += 1
                if d > 1:
                    return False
        return d == 1
    if abs(la - lb) != 1:
        return False
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def n_modifiche(s, q):
    """Numero di parole diverse a una modifica da s (alfabeto di q glifi, parola non vuota): sostituzioni n(q-1), cancellazioni
    (gruppi di glifi uguali di fila; niente parola vuota), inserimenti n(q-1)+q."""
    n = len(s)
    gruppi = 1 + sum(1 for i in range(1, n) if s[i] != s[i - 1])
    return 2 * n * (q - 1) + q + gruppi - (1 if n == 1 else 0)


# ---------------------------------------------------------------- il testo in numeri

class Pag:
    """Una pagina in numeri: tok (tipo di parola di ogni parola in ordine di lettura), L (riga), J (posto nella riga), ini
    (la riga apre un paragrafo), lstart (indice della prima parola di ogni riga, piu' la fine)."""
    __slots__ = ('tok', 'L', 'J', 'ini', 'lstart', 'n', 'nome')

    def __init__(self, nome, tok, L, J, ini, lstart):
        self.nome = nome
        self.tok = np.array(tok, dtype=np.int64)
        self.L = np.array(L, dtype=np.int64)
        self.J = np.array(J, dtype=np.int64)
        self.ini = np.array(ini, dtype=np.int64)
        self.lstart = np.array(lstart, dtype=np.int64)
        self.n = len(tok)


class Corpus:
    """Un testo in numeri. `glifi`: i segni frequenti (>= 0,1%) piu' il segno raro; i segni sotto la quota diventano il raro."""

    def __init__(self, pagine, glifi=None, quota=0.001):
        conti = Counter(s for rows in pagine.values() for _, ws in rows for w in ws for s in w)
        tot = sum(conti.values())
        if glifi is None:
            glifi = sorted(s for s, c in conti.items() if c / tot >= quota and s != RARO)
        self.glifi = list(glifi) + [RARO]
        self.idx = {s: i for i, s in enumerate(self.glifi)}
        self.q = len(self.glifi)
        self.rar = self.q - 1
        self.tipi, self.tid = [], {}
        self.varianti = {}
        self.pag = self.codifica(pagine)
        self.varianti['reale'] = self.pag
        self._e1 = {}
        self._pronto = False

    def codifica(self, pagine):
        out = OrderedDict()
        for p, rows in pagine.items():
            tok, L, J, ini, lstart = [], [], [], [], [0]
            for l, (i0, ws) in enumerate(rows):
                for j, w in enumerate(ws):
                    wi = tuple(self.idx.get(s, self.rar) for s in w)
                    t = self.tid.get(wi)
                    if t is None:
                        t = self.tid[wi] = len(self.tipi)
                        self.tipi.append(wi)
                    tok.append(t)
                    L.append(l)
                    J.append(j)
                    ini.append(1 if i0 else 0)
                lstart.append(len(tok))
            out[p] = Pag(p, tok, L, J, ini, lstart)
        self._pronto = False
        return out

    def aggiungi(self, nome, pagine):
        self.varianti[nome] = self.codifica(pagine)

    def prepara(self):
        """Tabelle per tipo (dopo aver codificato tutte le varianti)."""
        if self._pronto:
            return
        self.nt = len(self.tipi)
        self.prima = np.array([w[0] for w in self.tipi], dtype=np.int64)
        self.ultima = np.array([w[-1] for w in self.tipi], dtype=np.int64)
        self.Nedit = np.array([n_modifiche(w, self.q) for w in self.tipi], dtype=float)
        self.invN = 1.0 / self.Nedit
        self._pronto = True

    def e1(self, w):
        """Distribuzione del primo glifo di una parola a una modifica da w (formula chiusa, vedi la preregistrazione)."""
        v = self._e1.get(w)
        if v is None:
            s, q = self.tipi[w], self.q
            f = s[0]
            vec = np.full(q, 2.0)
            vec[f] = 0.0
            if len(s) >= 2 and s[1] != f:
                vec[s[1]] += 1.0
            vec[f] = self.Nedit[w] - vec.sum()
            v = vec / self.Nedit[w]
            self._e1[w] = v
        return v

    def parole_in_glifi(self, tipo):
        return tuple(self.glifi[g] for g in self.tipi[tipo])


# ---------------------------------------------------------------- classi di parole

def kmeans(X, K, seme, riavvii=8, giri=40):
    migliore = None
    for r in range(riavvii):
        rs = np.random.RandomState((seme * 100 + r) % (2 ** 32 - 1))
        c = [X[rs.randint(len(X))]]
        for _ in range(1, K):
            d = np.min([((X - ci) ** 2).sum(1) for ci in c], axis=0)
            c.append(X[rs.choice(len(X), p=d / d.sum())] if d.sum() > 0 else X[rs.randint(len(X))])
        c = np.array(c)
        for _ in range(giri):
            lab = ((X[:, None, :] - c[None, :, :]) ** 2).sum(2).argmin(1)
            nuovo = np.array([X[lab == k].mean(0) if (lab == k).any() else c[k] for k in range(K)])
            if np.allclose(nuovo, c):
                break
            c = nuovo
        D = ((X[:, None, :] - c[None, :, :]) ** 2).sum(2)
        lab, ine = D.argmin(1), D.min(1).sum()
        if migliore is None or ine < migliore[0]:
            migliore = (ine, lab)
    return migliore[1]


def classi(C, nomi_pagine, K=K_CLASSI, seme=1, nctx=100, dims=8):
    """Classi di parole per somiglianza dei vicini (a destra e a sinistra, nella stessa riga), dalle pagine date. Le parole
    con meno di MIN_CLASSE occorrenze e quelle mai viste stanno nella classe K (quella dei rari). Restituisce (classe di ogni
    tipo, K effettivo)."""
    pag = [C.pag[p] for p in nomi_pagine]
    cw = np.zeros(C.nt, dtype=np.int64)
    for P in pag:
        cw += np.bincount(P.tok, minlength=C.nt)
    F = np.where(cw >= MIN_CLASSE)[0]
    if len(F) < 3 * 2:
        return np.full(C.nt, 1, dtype=np.int64), 1
    K = max(2, min(K, len(F) // 3))
    top = np.argsort(-cw, kind='stable')[:nctx]
    cidx = {int(t): i for i, t in enumerate(top)}
    nc = len(top) + 3
    riga = {int(t): i for i, t in enumerate(F)}
    X = np.zeros((len(F), 2 * nc))
    for P in pag:
        tok, J = P.tok.tolist(), P.J.tolist()
        n = len(tok)
        for t in range(n):
            r = riga.get(tok[t])
            if r is None:
                continue
            sx = cidx.get(tok[t - 1], nc - 3) if J[t] >= 1 else nc - 2
            dx = cidx.get(tok[t + 1], nc - 3) if (t + 1 < n and J[t + 1] == J[t] + 1) else nc - 1
            X[r, sx] += 1
            X[r, nc + dx] += 1
    X = np.sqrt(X)
    X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    u, s, _ = np.linalg.svd(X, full_matrices=False)
    d = min(dims, len(s))
    E = u[:, :d] * s[:d]
    lab = kmeans(E, K, seme)
    cls = np.full(C.nt, K, dtype=np.int64)
    cls[F] = lab
    return cls, K


# ---------------------------------------------------------------- tabelle di conteggio

class Tab:
    """Conteggi (contesto, esito) e conteggi del contesto, per codici interi."""

    def __init__(self, chiavi, y, NY):
        self.NY = NY
        code = chiavi.astype(np.int64) * NY + y
        self.uc, self.cc = np.unique(code, return_counts=True)
        self.uk, self.ck = np.unique(chiavi, return_counts=True)

    def cerca(self, chiavi, y):
        code = chiavi.astype(np.int64) * self.NY + y
        i = np.minimum(np.searchsorted(self.uc, code), len(self.uc) - 1)
        cnt = np.where(self.uc[i] == code, self.cc[i], 0)
        j = np.minimum(np.searchsorted(self.uk, chiavi), len(self.uk) - 1)
        N = np.where(self.uk[j] == chiavi, self.ck[j], 0)
        return cnt.astype(float), N.astype(float)


BUCKET_RIGA = np.array([0, 1, 2, 3, 3, 4, 4, 4, 4] + [5] * 1000)


def chiavi_pagina(C, P, cls, K):
    """Per ogni parola della pagina, il contesto di ogni benda (numeri interi). Il contesto sta dentro la riga: a inizio riga la
    'parola prima' e' un segno speciale (inizio riga)."""
    t, J, n = P.tok, P.J, P.n
    BOL = C.nt
    q = C.q

    def indietro(k):
        out = np.full(n, BOL, dtype=np.int64)
        if n > k:
            out[k:] = t[:-k]
        return np.where(J >= k, out, BOL)
    p1, p2 = indietro(1), indietro(2)
    ok1, ok2 = p1 != BOL, p2 != BOL
    u1 = np.where(ok1, C.ultima[np.minimum(p1, C.nt - 1)], q)
    f1 = np.where(ok1, C.prima[np.minimum(p1, C.nt - 1)], q)
    u2 = np.where(ok2, C.ultima[np.minimum(p2, C.nt - 1)], q)
    f2 = np.where(ok2, C.prima[np.minimum(p2, C.nt - 1)], q)
    c1 = np.where(ok1, cls[np.minimum(p1, C.nt - 1)], K + 1)
    c2 = np.where(ok2, cls[np.minimum(p2, C.nt - 1)], K + 1)
    return OrderedDict([
        ('b', p1), ('c', u1), ('d', f1), ('e', p2), ('cd', u1 * (q + 1) + f1), ('e2', f2 * (q + 1) + u2),
        ('i1', c1), ('i2', c2 * (K + 2) + c1),
        ('f', (np.minimum(J, 6) * 6 + BUCKET_RIGA[P.L]) * 2 + P.ini)])


# ---------------------------------------------------------------- il modello di una piega

class Modello:
    """Il modello di base e le bende, addestrati sulle pagine `add` (nomi) di un Corpus. Non vede mai le altre pagine."""

    def __init__(self, C, add, seme=1):
        C.prepara()
        self.C = C
        q, nt = C.q, C.nt
        self.add = add
        cw = np.zeros(nt, dtype=np.int64)
        for p in add:
            cw += np.bincount(C.pag[p].tok, minlength=nt)
        self.cw = cw
        # forma dei glifi dentro la parola: trigrammi di glifi (due glifi di contesto) con fine parola, lisciatura di Witten-Bell
        c1 = np.zeros(q + 1)
        c2 = np.zeros((q + 1, q + 1))
        c3 = np.zeros((q + 1, q + 1, q + 1))
        for tipo in np.where(cw > 0)[0]:
            k = float(cw[tipo])
            a = b = q
            for x in C.tipi[tipo] + (q,):
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
        p3[q, q, q] = 0.0                                   # niente parola vuota
        p3[q, q, :] /= p3[q, q, :].sum()
        S = np.zeros(nt)
        for tipo in range(nt):
            a = b = q
            pr = 1.0
            for x in C.tipi[tipo] + (q,):
                pr *= p3[a, b, x]
                a, b = b, x
            S[tipo] = pr
        N = float(cw.sum())
        T = float((cw > 0).sum())
        self.U = (cw + T * S) / (N + T)                     # modello di base (a): frequenza + forma
        cf = np.bincount(C.prima, weights=cw, minlength=q)
        self.U1 = (cf + T * p3[q, q, :q]) / (N + T)         # lo stesso, solo per il primo glifo (marginale esatta)
        # classi di parole (per le bende i1, i2)
        self.cls, self.K = classi(C, add, seme=seme)
        # tabelle
        ch = {p: chiavi_pagina(C, C.pag[p], self.cls, self.K) for p in add}
        self.tab = {'w': {}, 'f': {}}
        yw = np.concatenate([C.pag[p].tok for p in add])
        yf = C.prima[yw]
        for j in BENDE:
            k = np.concatenate([ch[p][j] for p in add])
            self.tab['w'][j] = Tab(k, yw, nt)
            self.tab['f'][j] = Tab(k, yf, q)

    def grezze(self, P, variante_chiavi=None):
        """Per una pagina: per ogni bersaglio (w = parola intera, f = primo glifo) la probabilita' di base e, per ogni benda,
        i conteggi (esito dato il contesto, contesto)."""
        C = self.C
        ch = variante_chiavi or chiavi_pagina(C, P, self.cls, self.K)
        yw = P.tok
        yf = C.prima[yw]
        out = {'w': dict(U=self.U[yw], y=yw), 'f': dict(U=self.U1[yf], y=yf)}
        for tg, y in (('w', yw), ('f', yf)):
            for j in BENDE:
                out[tg][j] = self.tab[tg][j].cerca(ch[j], y)
        return out


def prob_bende(gr, beta):
    """Probabilita' di ogni benda con lisciatura di Dirichlet: (conteggio + beta*U) / (contesto + beta)."""
    out = {'U': gr['U']}
    for j in BENDE:
        cnt, N = gr[j]
        out[j] = (cnt + beta[j] * gr['U']) / (N + beta[j])
    return out


def scegli_beta(gr_val, mask):
    """Per ogni benda, il beta (della griglia) che da' il costo piu' basso sulle pagine di validazione."""
    beta = {}
    for j in BENDE:
        cnt = np.concatenate([g[j][0][m] for g, m in zip(gr_val, mask)])
        N = np.concatenate([g[j][1][m] for g, m in zip(gr_val, mask)])
        U = np.concatenate([g['U'][m] for g, m in zip(gr_val, mask)])
        costi = [-np.log2((cnt + b * U) / (N + b)).sum() for b in BETA]
        beta[j] = BETA[int(np.argmin(costi))]
    return beta


def em(M, giri=300, tol=1e-9):
    """Pesi di una miscela di modelli (colonne di M = probabilita' di ogni modello su ogni parola), per massima verosimiglianza."""
    n, m = M.shape
    pi = np.full(m, 1.0 / m)
    prima = -np.inf
    for _ in range(giri):
        mix = M @ pi
        r = M * pi[None, :] / mix[:, None]
        pi = r.mean(0)
        ll = float(np.log(mix).sum())
        if ll - prima < tol * abs(ll):
            break
        prima = ll
    return pi


# ---------------------------------------------------------------- la copia: finestre sulla pagina

class Finestre:
    """Le parole di una pagina come fonte di confronto. Si interrogano con la posizione di chi cerca (indice di parola, riga,
    posto nella riga): guarda solo le parole PRIMA di quel punto, in sette bande: S1 la parola subito prima, S2 la seconda
    prima, S3 le altre della riga; R1 la riga sopra, R2 due-tre righe sopra, R4 quattro-sette, R8 otto o piu'. Per ogni banda:
    quante parole ci sono, quante sono uguali alla parola cercata, la massa di quelle a una modifica (ognuna pesa 1/numero di
    parole a una modifica da lei), e lo stesso per il primo glifo."""

    def __init__(self, C, P):
        self.C, self.P = C, P
        T = P.n
        self.occ = defaultdict(list)
        for t, w in enumerate(P.tok.tolist()):
            self.occ[w].append(t)
        self.tp = list(self.occ.keys())
        self.nb = {}
        q = C.q
        oh = np.zeros((T, q))
        if T:
            oh[np.arange(T), C.prima[P.tok]] = 1.0
        self.PX = np.vstack([np.zeros((1, q)), np.cumsum(oh, 0)])
        ev = np.array([C.e1(w) for w in P.tok.tolist()]) if T else np.zeros((0, q))
        self.PE = np.vstack([np.zeros((1, q)), np.cumsum(ev, 0)])
        self.ls = P.lstart
        self.nl = len(self.ls) - 1

    def vicini(self, w):
        v = self.nb.get(w)
        if v is None:
            tw = self.C.tipi[w]
            tipi = self.C.tipi
            v = [n for n in self.tp if n != w and dist1(tw, tipi[n])]
            self.nb[w] = v
        return v

    def intervalli(self, tq, Lq, Jq):
        ls, nl = self.ls, self.nl

        def riga(a):
            return int(ls[min(max(a, 0), nl)])
        cur = tq - Jq
        return [(tq - 1, tq) if Jq >= 1 else (0, 0), (tq - 2, tq - 1) if Jq >= 2 else (0, 0),
                (cur, tq - 2) if Jq >= 3 else (0, 0),
                (riga(Lq - 1), riga(Lq)) if Lq >= 1 else (0, 0), (riga(Lq - 3), riga(Lq - 1)) if Lq >= 2 else (0, 0),
                (riga(Lq - 7), riga(Lq - 3)) if Lq >= 4 else (0, 0), (0, riga(Lq - 7)) if Lq >= 8 else (0, 0)]

    def cerca(self, w, g1, tq, Lq, Jq):
        """(n parole, uguali, massa a una modifica, primo glifo uguale, primo glifo a una modifica) per le sette bande."""
        iv = self.intervalli(tq, Lq, Jq)
        inv = self.C.invN
        occ = self.occ
        nb = np.array([b - a for a, b in iv], dtype=float)
        ex = np.zeros(7)
        me = np.zeros(7)
        lw = occ.get(w)
        vic = [(n, occ[n], inv[n]) for n in self.vicini(w)]
        for k, (a, b) in enumerate(iv):
            if b <= a:
                continue
            if lw:
                ex[k] = bisect.bisect_left(lw, b) - bisect.bisect_left(lw, a)
            for n, ln, iN in vic:
                c = bisect.bisect_left(ln, b) - bisect.bisect_left(ln, a)
                if c:
                    me[k] += c * iN
        a_ = np.array([a for a, _ in iv])
        b_ = np.array([b for _, b in iv])
        return nb, ex, me, self.PX[b_, g1] - self.PX[a_, g1], self.PE[b_, g1] - self.PE[a_, g1]


def cache_pagina(C, P, fin_propria, fin_altra):
    """Colonne della copia per tutte le parole di una pagina: dalla pagina stessa (reale) e dalla pagina 'altra' (riferimento:
    le sue parole fino allo stesso punto, vedi la preregistrazione). Matrici (parole, 7) per: n, uguali, a una modifica, primo
    glifo uguale, primo glifo a una modifica; piu' il segno 'simile vicino' (parola uguale o a una modifica nelle bande
    S1-R2)."""
    T = P.n
    out = {}
    for nome in ('r', 'n'):
        out[nome] = {k: np.zeros((T, 7)) for k in ('nb', 'ex', 'me', 'exf', 'mef')}
    PA = fin_altra.P
    for t in range(T):
        w = int(P.tok[t])
        g1 = int(C.prima[w])
        res = fin_propria.cerca(w, g1, t, int(P.L[t]), int(P.J[t]))
        for k, v in zip(('nb', 'ex', 'me', 'exf', 'mef'), res):
            out['r'][k][t] = v
        tn = min(t, PA.n)
        if tn < PA.n:
            Lq, Jq = int(PA.L[tn]), int(PA.J[tn])
        else:
            Lq, Jq = fin_altra.nl, 0
        res = fin_altra.cerca(w, g1, tn, Lq, Jq)
        for k, v in zip(('nb', 'ex', 'me', 'exf', 'mef'), res):
            out['n'][k][t] = v
    r = out['r']
    out['simile'] = ((r['ex'][:, :SIMILI_BANDE] > 0) | (r['me'][:, :SIMILI_BANDE] > 0)).any(1) if T else np.zeros(0, dtype=bool)
    return out


def derangement(nomi, seme):
    """Una pagina 'altra' per ogni pagina, mai se stessa (permutazione senza punti fissi, con semi fissi)."""
    nomi = list(nomi)
    rnd = random.Random(seme)
    for _ in range(1000):
        perm = nomi[:]
        rnd.shuffle(perm)
        if all(a != b for a, b in zip(nomi, perm)):
            return dict(zip(nomi, perm))
    return {a: nomi[(i + 1) % len(nomi)] for i, a in enumerate(nomi)}


def comp_cache(cc, tg, U, tipo):
    """Probabilita' delle componenti della copia (7 bande x uguale / a una modifica); dove la banda e' vuota vale la base U."""
    d = cc[tipo]
    nb = d['nb']
    valida = nb > 0
    den = np.where(valida, nb, 1.0)
    if tg == 'w':
        ex, me = d['ex'] / den, d['me'] / den
    else:
        ex, me = d['exf'] / den, d['mef'] / den
    ex = np.where(valida, ex, U[:, None])
    me = np.where(valida, me, U[:, None])
    pre = 'x_' if tipo == 'r' else 'nx_'
    pm = 'm_' if tipo == 'r' else 'nm_'
    out = {}
    for k, b in enumerate(BANDE):
        out[pre + b] = ex[:, k]
        out[pm + b] = me[:, k]
    return out


# ---------------------------------------------------------------- generatori sintetici (controlli positivi)

def genera_grammatica(C, seme, forza=None, K=K_CLASSI):
    """SOLA GRAMMATICA: le parole del testo `C` in classi (per somiglianza dei vicini); ogni riga e' una sequenza di classi scelta
    da una catena di Markov di primo ordine (l'inizio riga e' uno stato), poi ogni classe e' scritta con una parola della classe
    scelta a caso secondo la frequenza. Nessuna copia: ogni parola e' pescata senza guardare le altre parole, solo la classe
    della precedente.
    - `forza=None` ("naturale"): la catena e' quella stimata sul testo `C`.
    - `forza=s` (da 0 a 1, "piantata"): ogni classe passa alla classe seguente o a quella dopo ancora (meta' e meta') con peso s,
      e a una classe scelta a caso (come nel testo) con peso 1 - s. Serve a avere grammatiche di forza nota.
    Restituisce (pagine, meta); meta ha l'informazione mutua (bit) fra la classe di una parola e quella della successiva."""
    C.prepara()
    nomi = list(C.pag.keys())
    cls, K = classi(C, nomi, K=K, seme=seme)
    cw = np.zeros(C.nt, dtype=np.int64)
    for P in C.pag.values():
        cw += np.bincount(P.tok, minlength=C.nt)
    nc = K + 1
    trans = np.zeros((nc + 1, nc))                         # riga nc = inizio riga
    for P in C.pag.values():
        cp = cls[P.tok]
        for t in range(P.n):
            prev = cp[t - 1] if P.J[t] >= 1 else nc
            trans[prev, cp[t]] += 1
    marg = trans.sum(0) / trans.sum()
    if forza is not None:
        ciclo = np.zeros((nc + 1, nc))
        for c in range(nc):
            ciclo[c, (c + 1) % nc] += 0.5
            ciclo[c, (c + 2) % nc] += 0.5
        ciclo[nc] = marg
        trans = forza * ciclo + (1 - forza) * marg[None, :]
    else:
        trans = trans / np.maximum(trans.sum(1, keepdims=True), 1e-12)
    emis = []
    for c in range(nc):
        tipi = np.where((cls == c) & (cw > 0))[0]
        emis.append((tipi, cw[tipi] / cw[tipi].sum()) if len(tipi) else None)
    rnd = np.random.RandomState(seme % (2 ** 32 - 1))
    out = OrderedDict()
    coppie = Counter()
    for p, P in C.pag.items():
        rows = []
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            prev, ws = nc, []
            for _ in range(n):
                pr = trans[prev]
                c = int(rnd.choice(nc, p=pr / pr.sum())) if pr.sum() > 0 else int(rnd.randint(nc))
                if emis[c] is None:
                    c = int(np.argmax([0 if e is None else len(e[0]) for e in emis]))
                tipi, pe = emis[c]
                ws.append(C.parole_in_glifi(int(tipi[rnd.choice(len(tipi), p=pe)])))
                if prev != nc:
                    coppie[(prev, c)] += 1
                prev = c
            rows.append((bool(P.ini[P.lstart[l]]), ws))
        out[p] = rows
    tot = sum(coppie.values())
    pa, pb = Counter(), Counter()
    for (a, b), v in coppie.items():
        pa[a] += v
        pb[b] += v
    mi = sum(v / tot * math.log2(v * tot / (pa[a] * pb[b])) for (a, b), v in coppie.items())
    return out, dict(mi_classi=round(float(mi), 4), classi=nc)


def genera_copia(C, seme, p_copia=0.5, scala=20.0):
    """SOLA COPIA (auto-citazione): per ogni posto, con probabilita' `p_copia` si copia una parola scritta prima sulla stessa
    pagina (distanza in parole con andamento esponenziale, media `scala`) e la si cambia (uguale 40%, un glifo cambiato 30%,
    un glifo in piu' 15%, un glifo in meno 15%); altrimenti si pesca una parola nuova dalla frequenza del testo. Nessun ordine
    fra classi di parole: la parola pescata non dipende dalla precedente."""
    C.prepara()
    rnd = random.Random(seme)
    cw = np.zeros(C.nt, dtype=np.int64)
    gl = np.zeros(C.q)
    for P in C.pag.values():
        cw += np.bincount(P.tok, minlength=C.nt)
    for t in np.where(cw > 0)[0]:
        for g in C.tipi[t]:
            gl[g] += cw[t]
    gl[C.rar] = 0
    cum_t = np.cumsum(cw / cw.sum())
    cum_g = np.cumsum(gl / gl.sum())
    out = OrderedDict()
    for p, P in C.pag.items():
        toks = []                                          # parole generate, come tuple di numeri di glifo
        rows = []
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            ws = []
            for _ in range(n):
                t = len(toks)
                if t and rnd.random() < p_copia:
                    d = min(t, int(rnd.expovariate(1.0 / scala)) + 1)
                    w = toks[t - d]
                    r = rnd.random()
                    g = int(np.searchsorted(cum_g, rnd.random()))
                    if r < 0.40:
                        pass
                    elif r < 0.70 or (r >= 0.85 and len(w) == 1):
                        i = rnd.randrange(len(w))
                        w = w[:i] + (g,) + w[i + 1:]
                    elif r < 0.85:
                        i = rnd.randrange(len(w) + 1)
                        w = w[:i] + (g,) + w[i:]
                    else:
                        i = rnd.randrange(len(w))
                        w = w[:i] + w[i + 1:]
                else:
                    w = C.tipi[int(np.searchsorted(cum_t, rnd.random()))]
                toks.append(w)
                ws.append(tuple(C.glifi[x] for x in w))
            rows.append((bool(P.ini[P.lstart[l]]), ws))
        out[p] = rows
    return out
