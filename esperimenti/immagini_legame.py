# -*- coding: utf-8 -*-
"""Statistica di ia29: somiglianza visiva fra pagine, somiglianza di vocabolario fra pagine, loro legame a parita' di sezione, lingua, mano,
fascicolo, bifoglio, distanza nel manoscritto e lunghezza della pagina. Solo numpy: nessuna immagine, nessun modello.

Disegno (spiegato in preregistrazioni/ia29.md):
- distanza di vocabolario fra due pagine: radice della divergenza di Jensen-Shannon (in bit) fra le due distribuzioni delle parole, ognuna
  "tirata" verso la distribuzione di tutte le pagine con `alfa` conteggi fittizi (cosi' le pagine corte non sembrano diverse solo perche' corte);
  parole con meno di `minimo` occorrenze in tutto il campione finiscono in un solo contenitore;
- distanza visiva: 1 - coseno fra i vettori delle pagine (centrati sulla media del campione);
- legame = correlazione PARZIALE fra le due distanze sulle coppie di pagine, dopo aver tolto da entrambe una regressione sulle covariate
  (categorie delle coppie di sezione, lingua e mano; stesso fascicolo; stesso bifoglio; distanza di posizione con quattro termini; lunghezze);
- significativita': NON la formula (le coppie non sono indipendenti) ma una prova di permutazione. Nulla principale = scorrimento ciclico dei
  vettori visivi dentro ogni gruppo (sezione, lingua, mano) ordinato per posizione: spezza l'abbinamento pagina-disegno ma conserva
  l'andamento lento lungo il manoscritto, dove stanno colore, pergamena e sessione di scrittura. Nulla secondario = permutazione libera dentro
  il gruppo (come e184), piu' potente ma troppo ottimista se c'e' andamento lento.
"""
import math

import numpy as np

LN2 = math.log(2.0)
ALFA, MINIMO = 20.0, 3
K_PIANTA, BETA_PIANTA, TOP_PIANTA = 8, 2.5, 3000


# ---------------------------------------------------------------- distanze
def matrice_conteggi(pagine, minimo=MINIMO):
    """pagine: lista di liste di parole. Restituisce (matrice N x (V+1) di conteggi, vocabolario)."""
    tot = {}
    for ps in pagine:
        for w in ps:
            tot[w] = tot.get(w, 0) + 1
    voc = sorted(w for w, c in tot.items() if c >= minimo)
    ix = {w: i for i, w in enumerate(voc)}
    C = np.zeros((len(pagine), len(voc) + 1))
    for i, ps in enumerate(pagine):
        for w in ps:
            C[i, ix.get(w, len(voc))] += 1
    return C, voc


def bigrammi_pagine(pagine):
    """Versione a "pezzi di parola": ogni pagina diventa la lista dei bigrammi di lettere (con i bordi di parola) delle sue parole."""
    out = []
    for ps in pagine:
        b = []
        for w in ps:
            u = '^' + w + '$'
            b.extend(u[i:i + 2] for i in range(len(u) - 1))
        out.append(b)
    return out


def distanza_testo(C, alfa=ALFA):
    """Radice della JSD (in bit) fra le distribuzioni lisciate delle righe di C."""
    C = np.asarray(C, dtype=np.float64)
    n = C.sum(1)
    m = C.sum(0) / C.sum()
    P = ((C + alfa * m) / (n[:, None] + alfa)).astype(np.float32)

    def H(M):
        L = np.zeros_like(M)
        np.log(M, out=L, where=M > 0)
        return -(M * L).sum(-1)
    HP = H(P)
    N = len(P)
    D = np.zeros((N, N), dtype=np.float64)
    for i in range(N - 1):
        M = (P[i] + P[i + 1:]) * 0.5
        j = (H(M) - 0.5 * (HP[i] + HP[i + 1:])) / LN2
        D[i, i + 1:] = D[i + 1:, i] = np.sqrt(np.maximum(j, 0.0))
    return D


def distanza_vocabolario(C, minimo_pagine=3, massimo_quota=0.5):
    """Distanza di vocabolario PRINCIPALE: 1 - coseno fra i vettori tf-idf (log(1 + conteggio) per log(N / numero di pagine con la parola)); si tengono le
    parole presenti in almeno `minimo_pagine` pagine e in non piu' della meta' delle pagine. Scelta dopo una prova sul controllo Fuchs (non sul Voynich):
    riconosce meglio la pagina di appartenenza di due meta' casuali della stessa pagina (AUC 0,84 contro 0,71 della JSD)."""
    C = np.asarray(C, dtype=np.float64)
    df = (C > 0).sum(0)
    tieni = (df >= minimo_pagine) & (df <= massimo_quota * len(C))
    tieni[-1] = False                       # il contenitore delle parole rare non e' una parola
    X = np.log1p(C[:, tieni]) * np.log(len(C) / np.maximum(df[tieni], 1))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    D = 1.0 - X @ X.T
    np.fill_diagonal(D, 0.0)
    return np.maximum(D, 0.0)


def distanza_visiva(E):
    E = np.asarray(E, dtype=np.float64)
    E = E - E.mean(0)
    E = E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    D = 1.0 - E @ E.T
    np.fill_diagonal(D, 0.0)
    return np.maximum(D, 0.0)


# ---------------------------------------------------------------- covariate
def _categorie_coppie(valori, iu):
    v = np.asarray(valori)
    chiavi = np.array(['|'.join(sorted((a, b))) for a, b in zip(v[iu[0]], v[iu[1]])])
    u = np.unique(chiavi)
    return [(chiavi == k).astype(np.float64) for k in u[1:]]


def covariate(meta, iu):
    """Matrice (coppie x k) delle covariate. meta: lista di dict con sezione, lingua, mano, fascicolo, bifoglio, pos, n."""
    cols = [np.ones(len(iu[0]))]
    for campo in ('sezione', 'lingua', 'mano', 'fascicolo'):     # una colonna per ogni coppia (non ordinata) di valori: effetti fissi di coppia
        cols += _categorie_coppie([m[campo] for m in meta], iu)
    fa = np.array([m['fascicolo'] for m in meta])
    ba = np.array([m['bifoglio'] for m in meta])
    cols.append((fa[iu[0]] == fa[iu[1]]).astype(np.float64))
    cols.append((ba[iu[0]] == ba[iu[1]]).astype(np.float64))
    pos = np.array([m['pos'] for m in meta], dtype=np.float64)
    d = np.abs(pos[iu[0]] - pos[iu[1]])
    d = d / max(d.max(), 1.0)
    cols += [d, d ** 2, d ** 3, np.sqrt(d)]
    ln = np.log(np.array([m['n'] for m in meta], dtype=np.float64))
    cols += [ln[iu[0]] + ln[iu[1]], np.abs(ln[iu[0]] - ln[iu[1]])]
    return np.stack(cols, axis=1)


class Residuo:
    """Toglie da un vettore (o da una matrice di vettori) la sua proiezione sullo spazio delle covariate."""

    def __init__(self, Z):
        U, s, _ = np.linalg.svd(Z, full_matrices=False)
        self.Q = U[:, s > s[0] * 1e-9]
        self.rango = int(self.Q.shape[1])

    def __call__(self, v):
        return v - self.Q @ (self.Q.T @ v)


def vettore_coppie(D, iu):
    return D[iu]


# ---------------------------------------------------------------- permutazioni
CAMPI_GRUPPO = ('fascicolo', 'sezione', 'lingua', 'mano')


def gruppi(meta, campi=CAMPI_GRUPPO):
    """Indici delle pagine per gruppo (fascicolo, sezione, lingua, mano), in ordine di posizione."""
    g = {}
    for i, m in enumerate(meta):
        g.setdefault(tuple(m[c] for c in campi), []).append(i)
    return [np.array(sorted(ix, key=lambda i: meta[i]['pos'])) for ix in g.values()]


def perm_ciclica(gr, N, rng):
    p = np.arange(N)
    for ix in gr:
        if len(ix) >= 2:
            k = int(rng.integers(1, len(ix)))
            p[ix] = ix[(np.arange(len(ix)) + k) % len(ix)]
    return p


def perm_libera(gr, N, rng):
    p = np.arange(N)
    for ix in gr:
        if len(ix) >= 2:
            p[ix] = rng.permutation(ix)
    return p


def prova(Dy, Dx, meta, rng, B=999, nulla='ciclica', lotto=50, gr=None, iu=None, Res=None):
    """Legame fra Dy (vocabolario) e Dx (visivo). Restituisce dict(r, p_ciclica o p_libera, media_nulla, sd_nulla, coppie, rango)."""
    N = len(meta)
    iu = iu if iu is not None else np.triu_indices(N, 1)
    if Res is None:
        Res = Residuo(covariate(meta, iu))
    gr = gr if gr is not None else gruppi(meta)
    ry = Res(Dy[iu])
    ry = ry / np.linalg.norm(ry)
    rx = Res(Dx[iu])
    r = float(rx @ ry / np.linalg.norm(rx))
    nulli = []
    fp = perm_ciclica if nulla == 'ciclica' else perm_libera
    while len(nulli) < B:
        b = min(lotto, B - len(nulli))
        X = np.empty((len(iu[0]), b))
        for k in range(b):
            p = fp(gr, N, rng)
            X[:, k] = Dx[np.ix_(p, p)][iu]
        RX = Res(X)
        nulli.extend((ry @ RX / np.linalg.norm(RX, axis=0)).tolist())
    nulli = np.array(nulli)
    return {'r': r, 'p': float((1 + np.sum(nulli >= r)) / (1 + B)), 'nulla': nulla, 'media_nulla': float(nulli.mean()), 'sd_nulla': float(nulli.std()),
            'coppie': int(len(iu[0])), 'rango_covariate': Res.rango}


def r_osservato(Dy, Dx, meta):
    """Solo la correlazione parziale (senza permutazioni), per sottoinsiemi di pagine."""
    N = len(meta)
    iu = np.triu_indices(N, 1)
    Res = Residuo(covariate(meta, iu))
    ry = Res(Dy[iu])
    rx = Res(Dx[iu])
    return float(rx @ ry / (np.linalg.norm(rx) * np.linalg.norm(ry)))


def sottoinsieme(D, ix):
    ix = np.asarray(ix)
    return D[np.ix_(ix, ix)]


# ---------------------------------------------------------------- legami piantati e degradazioni
def coordinate_pca(E, K=K_PIANTA):
    E = np.asarray(E, dtype=np.float64)
    E = E - E.mean(0)
    U, s, _ = np.linalg.svd(E, full_matrices=False)
    k = min(K, len(s))
    Z = U[:, :k] * s[:k]
    return Z / np.maximum(Z.std(0), 1e-12)


def pianta(pagine, E, q, rng, beta=BETA_PIANTA, top=TOP_PIANTA, K=K_PIANTA):
    """Pagine con un legame piantato di forza q: ogni parola e' sostituita con probabilita' q da una parola pescata da una distribuzione
    che dipende dalla posizione della pagina nello spazio visivo (K coordinate principali): p_i(w) ~ m(w) exp(beta * (W z_i)_w / sqrt(K)),
    W gaussiana casuale. q = 0 lascia il testo com'e'. Il resto del testo e' intatto (la sezione, la mano e la posizione restano)."""
    if q <= 0:
        return [list(p) for p in pagine]
    tot = {}
    for ps in pagine:
        for w in ps:
            tot[w] = tot.get(w, 0) + 1
    voc = sorted(tot, key=lambda w: (-tot[w], w))[:top]
    m = np.array([tot[w] for w in voc], dtype=np.float64)
    m /= m.sum()
    Z = coordinate_pca(E, K)
    W = rng.standard_normal((len(voc), Z.shape[1]))
    out = []
    for i, ps in enumerate(pagine):
        lg = np.log(m) + beta * (W @ Z[i]) / math.sqrt(Z.shape[1])
        p = np.exp(lg - lg.max())
        c = np.cumsum(p / p.sum())
        ps2 = list(ps)
        sost = np.nonzero(rng.random(len(ps2)) < q)[0]
        if len(sost):
            nuove = np.searchsorted(c, rng.random(len(sost)))
            for j, a in zip(sost, nuove):
                ps2[j] = voc[min(int(a), len(voc) - 1)]
        out.append(ps2)
    return out


def diluisci(pagine, f, rng):
    """Ogni parola e' sostituita con probabilita' f da una parola a caso del testo intero (il legame si diluisce, non cambia altro)."""
    pool = [w for ps in pagine for w in ps]
    return [[pool[int(rng.integers(len(pool)))] if rng.random() < f else w for w in ps] for ps in pagine]


def omofoni(pagine, k, rng):
    """Cifrario verboso a omofoni: ogni occorrenza di una parola e' scritta con uno di k "omofoni" scelto a caso."""
    return [[w + '#%d' % int(rng.integers(k)) for w in ps] for ps in pagine]


# ---------------------------------------------------------------- lavori per i processi (devono stare al livello del modulo)
def lavoro_potenza(arg):
    """arg = (nome, pagine, E, meta, Dx, q, seme, B). Una replica: pianta il legame q, calcola r e p (nulla ciclica)."""
    nome, pagine, E, meta, Dx, q, seme, B = arg
    rng = np.random.default_rng(seme)
    pg = pianta(pagine, E, q, rng)
    C, _ = matrice_conteggi(pg)
    Dy = distanza_vocabolario(C)
    r = prova(Dy, Dx, meta, rng, B=B, nulla='ciclica')
    return {'nome': nome, 'q': q, 'seme': seme, 'r': r['r'], 'p': r['p']}


def lavoro_negativo_libero(arg):
    """arg = (nome, Dy, Dx, meta, seme, B). Una replica del controllo negativo: i vettori visivi rimescolati dentro la sezione (libero)
    e poi la prova principale (nulla ciclica) e quella libera."""
    nome, Dy, Dx, meta, seme, B = arg
    rng = np.random.default_rng(seme)
    N = len(meta)
    per_sez = {}
    for i, m in enumerate(meta):
        per_sez.setdefault(m['sezione'], []).append(i)
    p = np.arange(N)
    for ix in per_sez.values():
        ix = np.array(ix)
        p[ix] = rng.permutation(ix)
    Dx2 = Dx[np.ix_(p, p)]
    a = prova(Dy, Dx2, meta, rng, B=B, nulla='ciclica')
    b = prova(Dy, Dx2, meta, rng, B=B, nulla='libera')
    return {'nome': nome, 'seme': seme, 'r': a['r'], 'p_ciclica': a['p'], 'p_libera': b['p']}


def lavoro_testo(arg):
    """arg = (nome, pagine, Dx, meta, seme, B): una replica con un testo dato (per esempio latino nella disposizione del Voynich)."""
    nome, pagine, Dx, meta, seme, B = arg
    rng = np.random.default_rng(seme)
    C, _ = matrice_conteggi(pagine)
    Dy = distanza_vocabolario(C)
    a = prova(Dy, Dx, meta, rng, B=B, nulla='ciclica')
    return {'nome': nome, 'seme': seme, 'r': a['r'], 'p': a['p']}
