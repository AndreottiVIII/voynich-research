# -*- coding: utf-8 -*-
"""Strumenti di supporto per ia10 (famiglie di parole): nessun esperimento, solo funzioni, tutte con numpy.

Contenuto
- adatta_famiglie: raggruppamento delle parole in K famiglie secondo i vicini (algoritmo di scambio di Martin, Liermann e
  Ney, 1998, per il modello a classi di Brown et al., 1992: si massimizza l'informazione mutua media fra la classe di una
  parola e la classe della parola dopo; cfr. preregistrazioni/ia10.md; la letteratura va ricontrollata).
- Transizioni: tabella dei passaggi fra famiglie (con lisciatura) e guadagno in bit per coppia di parole vicine.
- misure sulla tabella (entropia, concentrazione), confronto fra raggruppamenti (indice di Rand corretto, informazione
  mutua normalizzata), rimescolamento delle parole dentro la riga.

Convenzione: ogni parola del vocabolario scelto ha un numero 0..NV-1; il numero NV vale "parola rara o mai vista" e
forma da sola la classe K (fissa: non si sposta mai). Le coppie sono (parola, parola dopo) nella stessa riga.
Nessuna parola della trascrizione compare in questo file.
"""
import numpy as np

LOG2 = np.log(2.0)


def xlogx(x):
    """x * log2(x), con 0 al posto di 0*log(0). x e' un array di numeri non negativi."""
    x = np.asarray(x, dtype=np.float64)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(x > 0, x * np.log2(np.where(x > 0, x, 1.0)), 0.0)
    return r


# ---------------------------------------------------------------- raggruppamento per scambio

class Grafo:
    """Coppie (a, b) di una parte del testo, riassunte per parola: seguaci e predecessori con i conteggi."""

    def __init__(self, a, b, NV):
        n = NV + 1
        chiave = a.astype(np.int64) * n + b
        uniche, cont = np.unique(chiave, return_counts=True)
        self.NV = NV
        self.la, self.lb, self.c = uniche // n, uniche % n, cont.astype(np.float64)
        self.ptr_l = np.searchsorted(self.la, np.arange(NV + 2))
        o = np.argsort(self.lb, kind='stable')
        self.ra, self.rb, self.rc = self.la[o], self.lb[o], self.c[o]
        self.ptr_r = np.searchsorted(self.rb, np.arange(NV + 2))
        self.self_ = np.zeros(NV + 1)
        m = self.la == self.lb
        np.add.at(self.self_, self.la[m], self.c[m])
        self.freq = np.zeros(NV + 1)
        np.add.at(self.freq, self.la, self.c)
        np.add.at(self.freq, self.lb, self.c)


def _obiettivo(T):
    """Per un blocco di matrici (..., K+1, K+1) di conteggi: somma di x log x sulle celle meno le somme per riga e per colonna
    (e' N per l'informazione mutua, a meno di costanti)."""
    return xlogx(T).sum((-1, -2)) - xlogx(T.sum(-1)).sum(-1) - xlogx(T.sum(-2)).sum(-1)


def adatta_famiglie(a, b, NV, K, seme, giri=20, grafo=None):
    """Assegna ogni parola 0..NV-1 a una delle K famiglie. a, b: coppie di numeri di parola (NV = rara) delle pagine di
    addestramento. Parte da un'assegnazione a caso (seme) con famiglie di uguale numerosita', poi, in ordine casuale, sposta
    ogni parola nella famiglia che massimizza l'informazione mutua media fra famiglie adiacenti; si ferma quando in un giro si
    spostano meno dello 0,2% delle parole (o dopo `giri` giri). Restituisce (cls, info): cls ha lunghezza NV+1 e cls[NV] = K."""
    g = grafo or Grafo(a, b, NV)
    rng = np.random.default_rng(1000 + seme)
    cls = np.full(NV + 1, K, dtype=np.int64)
    ordine_iniz = rng.permutation(NV)
    cls[ordine_iniz] = np.arange(NV) % K
    M = np.zeros((K + 1, K + 1))
    np.add.at(M, (cls[g.la], cls[g.lb]), g.c)
    idx = np.arange(K)
    spostate_tot, giri_fatti = 0, 0
    for giro in range(giri):
        ordine = rng.permutation(NV)
        spostate = 0
        for u in ordine:
            i0, i1 = g.ptr_l[u], g.ptr_l[u + 1]
            j0, j1 = g.ptr_r[u], g.ptr_r[u + 1]
            if i0 == i1 and j0 == j1:
                continue
            fb, fc = g.lb[i0:i1], g.c[i0:i1]
            pa, pc = g.ra[j0:j1], g.rc[j0:j1]
            mf, mp = fb != u, pa != u
            r = np.bincount(cls[fb[mf]], weights=fc[mf], minlength=K + 1)
            l = np.bincount(cls[pa[mp]], weights=pc[mp], minlength=K + 1)
            nww = g.self_[u]
            a_ = cls[u]
            M0 = M.copy()
            M0[a_, :] -= r
            M0[:, a_] -= l
            M0[a_, a_] -= nww
            T = np.broadcast_to(M0, (K, K + 1, K + 1)).copy()
            T[idx, idx, :] += r
            T[idx, :, idx] += l
            T[idx, idx, idx] += nww
            F = _obiettivo(T)
            b_ = int(np.argmax(F))
            if b_ != a_ and F[b_] > F[a_] + 1e-9:
                cls[u] = b_
                M = T[b_]
                spostate += 1
        spostate_tot += spostate
        giri_fatti += 1
        if spostate < max(1, 0.002 * NV):
            break
    N = M.sum()
    mi = float((_obiettivo(M[None])[0] + xlogx(N)) / N) if N > 0 else 0.0
    return cls, dict(giri=giri_fatti, spostate=spostate_tot, MI_addestramento=mi)


# ---------------------------------------------------------------- tabella dei passaggi

class Transizioni:
    """Tabella dei passaggi fra le classi (K famiglie piu' la classe rara), stimata sulle coppie di addestramento, con
    lisciatura: P(d|c) = (N(c,d) + lam * P(d)) / (N(c) + lam), P(d) = (N(.,d) + 0,5) / (N + 0,5 (K+1)) e lam = 1.
    Il guadagno di una coppia e' log2 P(d|c) - log2 P(d): quanto sapere la classe della parola prima aiuta a prevedere la classe
    della parola dopo, a parita' di tutto il resto (la parola dentro la classe pesa uguale nei due modelli e si semplifica)."""

    LAM = 1.0

    def __init__(self, a, b, cls, K):
        self.K = K
        ca, cb = cls[a], cls[b]
        self.C = np.zeros((K + 1, K + 1))
        np.add.at(self.C, (ca, cb), 1.0)
        self.N = self.C.sum()
        col = self.C.sum(0)
        self.Pd = (col + 0.5) / (self.N + 0.5 * (K + 1))
        riga = self.C.sum(1)
        self.P = (self.C + self.LAM * self.Pd[None, :]) / (riga[:, None] + self.LAM)
        self.logratio = np.log2(self.P) - np.log2(self.Pd)[None, :]

    def guadagno_coppie(self, ca, cb):
        """Guadagno (bit) di ciascuna coppia di classi (array)."""
        return self.logratio[ca, cb]


def misure_tabella(C):
    """Misure di concentrazione della tabella dei passaggi, dai conteggi C (classi x classi, ultima classe = rara).
    - H_cond: entropia condizionata H(d|c), in bit; H_d: entropia di d; MI = H_d - H_cond (plug-in);
    - MI_norm = MI / H_d;
    - celle_meta: quante celle (c,d) servono per mettere insieme meta' della probabilita' congiunta, divise per quante ne
      servirebbero con la tabella di indipendenza P(c)P(d) con le stesse marginali (rapporto <1: probabilita' piu'
      concentrata che a caso);
    - dominante: media (pesata su P(c)) della probabilita' del passaggio piu' frequente, meno la stessa quantita' con
      l'indipendenza (max_d P(d))."""
    C = np.asarray(C, dtype=np.float64)
    N = C.sum()
    if N <= 0:
        return dict(H_cond=float('nan'), H_d=float('nan'), MI=float('nan'), MI_norm=float('nan'), celle_meta=float('nan'),
                    celle_meta_indip=float('nan'), rapporto_celle=float('nan'), dominante=float('nan'))
    P = C / N
    pc, pd = P.sum(1), P.sum(0)
    H_d = float(-(xlogx(pd)).sum())
    H_cond = float(-(xlogx(P).sum() - xlogx(pc).sum()))
    MI = H_d - H_cond

    def celle_meta(Q):
        q = np.sort(Q.ravel())[::-1]
        return int(np.searchsorted(np.cumsum(q), 0.5) + 1)
    cm, ci = celle_meta(P), celle_meta(np.outer(pc, pd))
    with np.errstate(divide='ignore', invalid='ignore'):
        cond = np.where(pc[:, None] > 0, P / np.where(pc[:, None] > 0, pc[:, None], 1.0), 0.0)
    dom = float((pc * cond.max(1)).sum() - pd.max())
    return dict(H_cond=H_cond, H_d=H_d, MI=float(MI), MI_norm=float(MI / H_d) if H_d > 0 else float('nan'), celle_meta=cm,
                celle_meta_indip=ci, rapporto_celle=cm / ci, dominante=dom)


# ---------------------------------------------------------------- confronto fra raggruppamenti

def tabella_contingenza(x, y, peso=None):
    x, y = np.asarray(x), np.asarray(y)
    ux, ix = np.unique(x, return_inverse=True)
    uy, iy = np.unique(y, return_inverse=True)
    T = np.zeros((len(ux), len(uy)))
    np.add.at(T, (ix, iy), 1.0 if peso is None else np.asarray(peso, dtype=float))
    return T


def indice_rand_corretto(x, y):
    """Indice di Rand corretto (Hubert e Arabie, 1985) fra due raggruppamenti degli stessi elementi."""
    T = tabella_contingenza(x, y)
    n = T.sum()
    if n < 2:
        return float('nan')
    c2 = lambda v: v * (v - 1) / 2.0
    somma = c2(T).sum()
    a, b = c2(T.sum(1)).sum(), c2(T.sum(0)).sum()
    atteso = a * b / c2(n)
    massimo = (a + b) / 2.0
    if massimo == atteso:
        return 1.0 if somma == massimo else 0.0
    return float((somma - atteso) / (massimo - atteso))


def info_mutua_tabella(T):
    """Informazione mutua (bit) di una tabella di contingenza, e le due entropie."""
    T = np.asarray(T, dtype=float)
    N = T.sum()
    if N <= 0:
        return 0.0, 0.0, 0.0
    P = T / N
    px, py = P.sum(1), P.sum(0)
    hx, hy = float(-xlogx(px).sum()), float(-xlogx(py).sum())
    hxy = float(-xlogx(P).sum())
    return hx + hy - hxy, hx, hy


def nmi(x, y, peso=None):
    """Informazione mutua normalizzata (divisa per la media delle due entropie, come V-measure) e purezza di x rispetto a y
    (quota degli elementi nella classe di y piu' frequente dentro ogni gruppo di x)."""
    T = tabella_contingenza(x, y, peso)
    mi, hx, hy = info_mutua_tabella(T)
    den = (hx + hy) / 2.0
    pur = float(T.max(1).sum() / T.sum()) if T.sum() > 0 else float('nan')
    return (float(mi / den) if den > 0 else 0.0), pur


# ---------------------------------------------------------------- rimescolamento nella riga

def rimescola_in_riga(tok, linea, rng):
    """Permutazione a caso dei segni di `tok` dentro ogni riga (le righe sono blocchi contigui con numero crescente in
    `linea`); restituisce la sequenza rimescolata."""
    ordine = np.lexsort((rng.random(len(tok)), linea))
    return tok[ordine]


def coppie_di(tok, linea):
    """Indici delle coppie (i, i+1) nella stessa riga."""
    return np.nonzero(linea[1:] == linea[:-1])[0]
