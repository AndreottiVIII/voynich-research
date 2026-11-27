# -*- coding: utf-8 -*-
"""IA45: le statistiche e i nulli di permutazione per le colonne di segni singoli. Solo conti, niente modelli.

Ipotesi A: la colonna e' una sequenza convenzionale (un "alfabeto" recitato, forse piu' volte).
  A1  coppie di segni consecutivi (in quest'ordine) che due colonne hanno in comune: sovrapposizione dei conteggi (somma dei minimi).
  A2  periodicita' di una colonna: il massimo, sui ritardi 2..L/2, della quota di posizioni uguali a quella `ritardo` dopo.
Ipotesi B: i segni della colonna sono i segni che aprono le righe accanto.
  B1  numero di segni uguali alla prima unita' della riga accanto (la riga che segue o quella che precede il segno).
  B2  media del logaritmo (frequenza come prima unita' di riga / frequenza come prima unita' di parola) sui segni della colonna.
Nullo: A1 e A2 mescolano l'ordine dei segni dentro ogni colonna (stessi segni, stesse ripetizioni); B1 mescola i segni sulle
stesse righe; B2 pesca segni a caso dal testo della stessa pagina. p = (1 + nulli >= osservato) / (K + 1), a una coda.
"""
import math
import numpy as np


def codifica(liste):
    """Da liste di segni (stringhe) a liste di numeri: stesso segno = stesso numero >= 0; ogni '?' un numero negativo unico."""
    mappa, neg = {}, [0]
    out = []
    for l in liste:
        o = []
        for s in l:
            if s is None or s == '?':
                neg[0] -= 1
                o.append(neg[0])
            else:
                o.append(mappa.setdefault(s, len(mappa)))
        out.append(np.array(o, dtype=np.int64))
    return out, mappa


def _perm(rng, k, n):
    return np.argsort(rng.random((k, n)), axis=1)


def _conteggi(M, X):
    """X: (k, L) numeri. Matrice (k, M*M) di quante volte compare ogni tipo di coppia consecutiva (le coppie con '?' non contano)."""
    k = X.shape[0]
    a, b = X[:, :-1], X[:, 1:]
    cod = np.where((a >= 0) & (b >= 0), a * M + b, M * M) + (np.arange(k)[:, None] * (M * M + 1))
    c = np.bincount(cod.ravel(), minlength=k * (M * M + 1)).reshape(k, M * M + 1)
    return c[:, :M * M].astype(np.int32)


def a1(x, y, M, k, rng, blocco=1000):
    """Sovrapposizione delle coppie consecutive fra due colonne: somma, sui tipi di coppia, del minimo fra quante volte compare
    in una e nell'altra. Ritorna (osservato, p)."""
    obs = int(np.minimum(_conteggi(M, x[None, :])[0], _conteggi(M, y[None, :])[0]).sum())
    ge, tot = 0, 0
    while tot < k:
        n = min(blocco, k - tot)
        cx = _conteggi(M, x[_perm(rng, n, len(x))])
        cy = _conteggi(M, y[_perm(rng, n, len(y))])
        ge += int((np.minimum(cx, cy).sum(1) >= obs).sum())
        tot += n
    return obs, (1 + ge) / (k + 1)


def _periodo(X):
    """(k, L) -> (massimo sui ritardi, ritardo del massimo) per ogni riga."""
    L = X.shape[1]
    ritardi = list(range(2, L // 2 + 1))
    m = np.stack([(X[:, :-p] == X[:, p:]).mean(1) for p in ritardi], axis=1)
    return m.max(1), np.array(ritardi)[m.argmax(1)]


def a2(x, k, rng, blocco=4000):
    """Periodicita' di una colonna. Ritorna (osservato, ritardo, p)."""
    o, r = _periodo(x[None, :])
    ge, tot = 0, 0
    while tot < k:
        n = min(blocco, k - tot)
        nu, _ = _periodo(x[_perm(rng, n, len(x))])
        ge += int((nu >= o[0] - 1e-12).sum())
        tot += n
    return float(o[0]), int(r[0]), (1 + ge) / (k + 1)


def b1(segni, bersagli, k, rng, blocco=4000):
    """Segni uguali alla prima unita' della riga assegnata (bersagli: numeri, un bersaglio per segno). Ritorna (osservato, p)."""
    obs = int((segni == bersagli).sum())
    ge, tot = 0, 0
    while tot < k:
        n = min(blocco, k - tot)
        s = segni[_perm(rng, n, len(segni))]
        ge += int(((s == bersagli[None, :]).sum(1) >= obs).sum())
        tot += n
    return obs, (1 + ge) / (k + 1)


def rapporti_log(prime, tutte, alfa=0.5):
    """Funzione segno -> log(P_prima_unita_di_riga / P_prima_unita_di_parola), lisciata. Segni mai visti in nessuna: 0."""
    segni = set(prime) | set(tutte)
    V = len(segni) + 1
    Np, Nt = sum(prime.values()), sum(tutte.values())

    def f(u):
        if u not in segni:
            return 0.0
        return math.log((prime.get(u, 0) + alfa) / (Np + alfa * V)) - math.log((tutte.get(u, 0) + alfa) / (Nt + alfa * V))
    return f


def b2(colonna, unita_testo, f, k, rng, blocco=4000):
    """Media del rapporto logaritmico sui segni della colonna, contro colonne finte di segni pescati a caso dal testo della
    stessa pagina. Ritorna (osservato, p a una coda alta)."""
    obs = float(np.mean([f(s) for s in colonna]))
    pool = np.array([f(u) for u in unita_testo], dtype=float)
    ge, tot = 0, 0
    while tot < k:
        n = min(blocco, k - tot)
        v = pool[rng.integers(0, len(pool), size=(n, len(colonna)))].mean(1)
        ge += int((v >= obs - 1e-12).sum())
        tot += n
    return obs, (1 + ge) / (k + 1)


# ---------------------------------------------------------------------------------------------------------------------
# La batteria: tutti i test insieme, con i numeri e le soglie scritti nella preregistrazione (ia45)
# ---------------------------------------------------------------------------------------------------------------------
from collections import OrderedDict

COPPIE_A1 = (('f49v', 'f66r'), ('f49v', 'f57v'), ('f66r', 'f57v'))
COLONNE_A2 = ('f49v', 'f66r', 'f57v')
PAGINE_B1 = ('f49v', 'f76r')
PAGINE_B2 = ('f49v', 'f66r', 'f76r')
N_TEST = len(COPPIE_A1) + len(COLONNE_A2) + 2 * len(PAGINE_B1) + len(PAGINE_B2)     # 13
ALFA = 0.01 / N_TEST
MIN_COMUNI = 6          # segni distinti in comune per fare A1 (soglia di Fable: meno di 6 = troppo poco)
MIN_LUNGHEZZA_A2 = 16   # lunghezza minima di una colonna per misurarne il periodo
MIN_SEGNI_B1 = 6


def _bersagli(pagina, quale, codici_righe, neg):
    out = []
    for r in (pagina.riga_dopo if quale == 'dopo' else pagina.riga_prima):
        if r is None or codici_righe[r] < 0:
            neg[0] -= 1
            out.append(neg[0])
        else:
            out.append(int(codici_righe[r]))
    return np.array(out, dtype=np.int64)


def batteria(pagine, riferimento, k, seme):
    """pagine: lista di Pagina (colonne_dati); riferimento: (prime, tutte). Ritorna OrderedDict nome -> dict(osservato, p, ...)."""
    rng = np.random.default_rng(seme)
    per = {p.nome: p for p in pagine}
    liste, indice = [], {}
    for p in pagine:
        indice[('col', p.nome)] = len(liste)
        liste.append(p.colonna)
        indice[('righe', p.nome)] = len(liste)
        liste.append(p.righe_prime)
    cod, mappa = codifica(liste)
    M = max(len(mappa), 1)
    col = {p.nome: cod[indice[('col', p.nome)]] for p in pagine}
    rig = {p.nome: cod[indice[('righe', p.nome)]] for p in pagine}
    f = rapporti_log(*riferimento)
    out = OrderedDict()
    for a, b in COPPIE_A1:
        if a not in col or b not in col:
            out['A1 %s-%s' % (a, b)] = dict(osservato=None, p=None, comuni=0, nota='pagina assente')
            continue
        n_comuni = len(set(col[a][col[a] >= 0].tolist()) & set(col[b][col[b] >= 0].tolist()))
        if n_comuni < MIN_COMUNI:
            out['A1 %s-%s' % (a, b)] = dict(osservato=None, p=None, comuni=n_comuni, nota='troppo poco')
            continue
        o, p = a1(col[a], col[b], M, k, rng)
        out['A1 %s-%s' % (a, b)] = dict(osservato=o, p=p, comuni=n_comuni)
    for n in COLONNE_A2:
        if n not in col or len(col[n]) < MIN_LUNGHEZZA_A2:
            out['A2 %s' % n] = dict(osservato=None, p=None, nota='troppo poco')
            continue
        o, r, p = a2(col[n], k, rng)
        out['A2 %s' % n] = dict(osservato=o, ritardo=r, p=p)
    for n in PAGINE_B1:
        pg = per.get(n)
        dopo = [r for r in pg.riga_dopo if r is not None] if pg else []
        allineata = bool(pg) and len(dopo) == len(set(dopo)) == len(pg.colonna) and len(pg.colonna) >= MIN_SEGNI_B1
        for quale in ('dopo', 'prima'):
            nome = 'B1 %s %s' % (n, quale)
            if not allineata:
                out[nome] = dict(osservato=None, p=None, nota='righe non allineate o troppo pochi segni')
                continue
            neg = [-10 ** 6]
            tgt = _bersagli(pg, quale, rig[n], neg)
            o, p = b1(col[n], tgt, k, rng)
            out[nome] = dict(osservato=o, p=p, segni=len(col[n]))
    for n in PAGINE_B2:
        pg = per.get(n)
        if pg is None or not pg.colonna or not pg.unita_testo:
            out['B2 %s' % n] = dict(osservato=None, p=None, nota='senza testo')
            continue
        o, p = b2(pg.colonna, pg.unita_testo, f, k, rng)
        out['B2 %s' % n] = dict(osservato=o, p=p)
    return out


def significativi(ris, alfa=ALFA):
    return [nome for nome, r in ris.items() if r['p'] is not None and r['p'] <= alfa]


def lettura(ris, alfa=ALFA):
    """Che cosa dice una batteria: (A, B1, B2) vero/falso.
    A  = un test A1 o un A2 sulle colonne dei fogli (l'anello di f57v e' il confronto, non conta da solo);
    B1 = un segno uguale alla prima unita' della riga accanto piu' spesso del caso;
    B2 = i segni della colonna sono del genere che apre le righe (composizione): non dice che siano quelli delle righe accanto.
    Una lettura dice solo quale ipotesi e' compatibile, o nessuna."""
    s = [n for n in significativi(ris, alfa) if n != 'A2 f57v']
    return (any(n.startswith('A') for n in s), any(n.startswith('B1') for n in s), any(n.startswith('B2') for n in s))
