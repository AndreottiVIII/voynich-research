# -*- coding: utf-8 -*-
"""IA44, ricerca (a): nell'erbario, gruppi di 2-4 parole "una e una sola per pagina" (schema delle qualita' e dei gradi).

Il motore e' lo stesso per i controlli e per il Voynich: prende liste di parole per pagina (stringhe opache) e i gruppi di
rimescolamento (fascicolo e mano), e ritorna numeri. Nessun testo viene scritto.

Una RICERCA su un'unita' (erbario A o erbario B):
  per ogni variante (taglia m del gruppo 2, 3, 4; conteggio 'presenza' o 'una_volta'; regione 'ovunque', 'inizio' = primo terzo
  delle parole della pagina, 'fine' = ultimo terzo) si cerca, con una ricerca a fascio (larghezza FASCIO), il gruppo di m parole
  che rende massima la quota di pagine in cui il gruppo e' presente "esattamente una volta" (una sola delle m parole, per
  'presenza'; una sola occorrenza totale del gruppo, per 'una_volta').
  Vincoli: ogni parola del gruppo "prende" almeno il 5% delle pagine (pagine dove e' l'unica del gruppo); nessuna coppia di parole
  del gruppo e' una variante a una lettera dell'altra (distanza di Levenshtein 1: sostituzione, inserzione o cancellazione);
  parole candidate: presenti in non piu' del 70% delle pagine della regione.
Due nulli (rimescolamenti, sempre dentro lo stesso gruppo di fascicolo e mano):
  'tok'  le parole si rimescolano fra le pagine (le lunghezze delle pagine restano);
  'col'  per ogni parola, i suoi conteggi per pagina si rimescolano fra le pagine (frequenza e "a ciuffi" di ogni parola restano).
Statistica: punteggio per variante = quota di pagine "esatte" del miglior gruppo; z di ogni variante contro il nullo (media e
scarto del nullo stesso); statistica della ricerca = massimo di z su tutte le varianti; p = (1 + n nulli >= osservato)/(1 + n);
p finale = il piu' grande dei due nulli.
"""
import os
import sys
from collections import defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

FASCIO = 12
QUOTA_MIN = 0.05                  # quota minima di pagine "prese" da ogni parola del gruppo
TOLLERANZA = 0.05                 # pagine in cui due parole dello stesso gruppo possono comparire insieme: 5% delle pagine della meno frequente
FREQ_MAX = 0.70                   # una parola candidata sta al massimo nel 70% delle pagine (della regione)
MAX_CANDIDATE = 400
TAGLIE = (2, 3, 4)
CONTEGGI = ('presenza', 'una_volta')
REGIONI = ('ovunque', 'inizio', 'fine')
VARIANTI = tuple((m, c, r) for c in CONTEGGI for r in REGIONI for m in TAGLIE)     # 18 varianti
MODI = ('quota', 'esclusione')          # i due modi di ricerca del gruppo (vedi `cerca`)
STATISTICHE = tuple((v, mo, k) for v in VARIANTI for mo in MODI for k in ('quota', 'z'))   # 72: per variante e modo la quota di pagine esatte e lo z
NULLI = ('tok', 'col')


# ---------------------------------------------------------------- vocabolario e varianti a una lettera

def vocabolario(pagine):
    """pagine: lista di liste di parole. Ritorna (lista dei tipi in ordine alfabetico, lista di array di id per pagina). L'ordine
    alfabetico fa si' che gli spareggi della ricerca non dipendano dall'ordine delle pagine."""
    voc = sorted({w for ps in pagine for w in ps})
    ids = {w: i for i, w in enumerate(voc)}
    out = [np.array([ids[w] for w in ps], dtype=np.int32) for ps in pagine]
    return voc, out


def adiacenza_varianti(voc):
    """Matrice booleana V x V: True se le due parole sono uguali o differiscono per UNA lettera (sostituzione, inserzione,
    cancellazione). Costruita con chiavi (schema con un buco; parola uguale a una cancellazione dell'altra), senza confronti a coppie."""
    V = len(voc)
    sost = defaultdict(list)
    parola = defaultdict(list)
    canc = defaultdict(list)
    for i, w in enumerate(voc):
        parola[w].append(i)
        for j in range(len(w)):
            sost[w[:j] + '*' + w[j + 1:]].append(i)
            canc[w[:j] + w[j + 1:]].append(i)
    A = np.eye(V, dtype=bool)
    for ids in sost.values():
        if len(ids) > 1:
            ii = np.array(ids)
            A[np.ix_(ii, ii)] = True
    for x, corte in canc.items():
        lunghe = parola.get(x)
        if lunghe:
            A[np.ix_(np.array(lunghe), np.array(corte))] = True
            A[np.ix_(np.array(corte), np.array(lunghe))] = True
    return A


# ---------------------------------------------------------------- conteggi

def conteggi_regioni(token, V):
    """token: lista di array di id (uno per pagina, in ordine di scrittura). Ritorna int16 [3, N, V]: conteggi in ovunque, inizio
    (primo terzo), fine (ultimo terzo)."""
    N = len(token)
    C = np.zeros((3, N, V), dtype=np.int16)
    for p, a in enumerate(token):
        L = len(a)
        if L == 0:
            continue
        pos = np.arange(L) / L
        C[0, p] = np.bincount(a, minlength=V)
        C[1, p] = np.bincount(a[pos < 1 / 3], minlength=V)
        C[2, p] = np.bincount(a[pos >= 2 / 3], minlength=V)
    return C


def rimescola_token(token, strati, rnd):
    """Nullo 'tok': dentro ogni gruppo le parole si rimescolano fra le pagine (stesse lunghezze)."""
    out = [None] * len(token)
    gruppi = defaultdict(list)
    for p, s in enumerate(strati):
        gruppi[s].append(p)
    for pp in gruppi.values():
        tutte = np.concatenate([token[p] for p in pp])
        rnd.shuffle(tutte)
        i = 0
        for p in pp:
            L = len(token[p])
            out[p] = tutte[i:i + L]
            i += L
    return out


def rimescola_colonne(C, strati, rng):
    """Nullo 'col': per ogni parola, i suoi conteggi (nelle tre regioni insieme) si permutano fra le pagine dello stesso gruppo."""
    out = C.copy()
    gruppi = defaultdict(list)
    for p, s in enumerate(strati):
        gruppi[s].append(p)
    for pp in gruppi.values():
        if len(pp) < 2:
            continue
        pp = np.array(pp)
        idx = rng.random((len(pp), C.shape[2])).argsort(axis=0)          # per colonna una permutazione delle pagine del gruppo
        for r in range(3):
            sotto = C[r][pp]
            out[r][pp] = np.take_along_axis(sotto, idx, axis=0)
    return out


# ---------------------------------------------------------------- la ricerca a fascio

def _z(esatte, N, b):
    """Eccesso di pagine "esatte" sul caso (parole indipendenti con le frequenze osservate): (osservate - N b)/radice(N b (1-b))."""
    b = np.clip(b, 1e-6, 1 - 1e-6)
    return (esatte - N * b) / np.sqrt(N * b * (1 - b))


def cerca(C, adj, conteggio, regione, esclusione, taglie=TAGLIE):
    """Per ogni taglia m il miglior gruppo: dict m -> (quota di pagine esatte, z di eccesso sul caso, tuple di id). C: [3, N, V].
    Due modi di ricerca (due ricerche diverse, tutte e due contate): `esclusione=False`: fascio ordinato per pagine esatte, con il solo
    vincolo di non-variante; `esclusione=True`: il gruppo e' una "cricca di esclusione", due parole stanno insieme solo se sono
    presenti insieme (nella stessa pagina) al piu' TOLLERANZA (5%) delle pagine della meno frequente (per difetto; per le parole rare,
    mai): le parole molto frequenti, che a caso hanno quote alte, non coprono il fascio e si trovano anche schemi con classi rare.
    Tra i gruppi ammessi si tiene quello con piu' pagine esatte. Lo z e' l'eccesso di pagine esatte sul caso (parole indipendenti
    con le frequenze osservate), calcolato sul gruppo scelto."""
    r = REGIONI.index(regione)
    X = C[r].astype(np.int16)
    N, V = X.shape
    if conteggio == 'presenza':
        X = (X > 0).astype(np.int16)
        presenti = X.sum(0)
        prese = presenti
    else:
        presenti = (X > 0).sum(0)
        prese = (X == 1).sum(0)
    vuoto = {m: (0.0, 0.0, ()) for m in taglie}
    minclaim = max(2, int(np.ceil(QUOTA_MIN * N)))
    ok = (prese >= minclaim) & (presenti <= FREQ_MAX * N)
    cand = np.nonzero(ok)[0]
    if len(cand) > MAX_CANDIDATE:
        ordine = np.argsort(-prese[cand], kind='stable')[:MAX_CANDIDATE]
        cand = np.sort(cand[ordine])
    if len(cand) < max(taglie):
        return vuoto
    Xc = X[:, cand]
    A = adj[np.ix_(cand, cand)]
    W = len(cand)
    P = (Xc > 0)
    E1 = (Xc == 1)
    Z0 = (Xc == 0)
    p1 = E1.mean(0)
    p0 = Z0.mean(0)
    pres = P.sum(0)
    OV = P.astype(np.float32).T @ P.astype(np.float32)                 # pagine in cui le due parole sono presenti insieme
    TOL = np.floor(TOLLERANZA * np.minimum(pres[:, None], pres[None, :]))
    compat = ((OV <= TOL) if esclusione else np.ones_like(A)) & ~A     # esclusione (solo nel modo 'esclusione') e non varianti a una lettera
    # passo 2: TUTTE le coppie compatibili (prodotto di matrici), poi si tengono le FASCIO migliori
    EZ = E1.astype(np.float32).T @ Z0.astype(np.float32)               # [i, j]: pagine dove i e' esattamente una e j assente
    esatte2 = EZ + EZ.T
    valida = compat & (np.minimum(EZ, EZ.T) >= minclaim)
    np.fill_diagonal(valida, False)
    s2 = np.where(np.triu(valida, 1), esatte2, -1.0).ravel()
    ordine = np.argsort(-s2, kind='stable')[:FASCIO]
    stati = []
    for k in ordine:
        if s2[k] < 0:
            break
        i, j = int(k // W), int(k % W)
        stati.append((int(s2[k]), (i, j), Xc[:, i] + Xc[:, j], float(p0[i] * p0[j]), float(p1[i] * p0[j] + p1[j] * p0[i])))
    risultati = {}
    if not stati:
        return vuoto
    if 2 in taglie:
        es, mem, _, _, b = stati[0]
        risultati[2] = (es / N, float(_z(es, N, b)), tuple(int(cand[i]) for i in mem))
    for m in range(3, max(taglie) + 1):
        nuovi = {}
        for es0, mem, c, a0, b0 in stati:
            somma = c[:, None] + Xc                                    # N x W
            esatte = (somma == 1).sum(0)
            presa = ((c[:, None] == 0) & E1).sum(0)
            vietate = ~compat[list(mem)].all(0) | (presa < minclaim)
            esatte = np.where(vietate, -1, esatte)
            top = np.argsort(-esatte, kind='stable')[:FASCIO]
            for w in top:
                if esatte[w] < 0:
                    break
                chiave = tuple(sorted(mem + (int(w),)))
                if chiave not in nuovi or nuovi[chiave][0] < esatte[w]:
                    nuovi[chiave] = (int(esatte[w]), chiave, somma[:, w].copy(), float(a0 * p0[w]), float(b0 * p0[w] + a0 * p1[w]))
        if not nuovi:
            break
        stati = sorted(nuovi.values(), key=lambda t: (-t[0], t[1]))[:FASCIO]
        if m in taglie:
            es, mem, _, _, b = stati[0]
            risultati[m] = (es / N, float(_z(es, N, b)), tuple(int(cand[i]) for i in mem))
    return {m: risultati.get(m, (0.0, 0.0, ())) for m in taglie}


def punteggi(C, adj):
    """Vettore delle statistiche (nell'ordine di STATISTICHE) e i gruppi trovati (uno per variante e modo: indice = statistica // 2)."""
    punti, gruppi = [], []
    cache = {}
    for (m, c, r) in VARIANTI:
        for mo in MODI:
            if (c, r, mo) not in cache:
                cache[(c, r, mo)] = cerca(C, adj, c, r, mo == 'esclusione')
            q, z, g = cache[(c, r, mo)][m]
            punti += [q, z]
            gruppi.append(g)
    return np.array(punti), gruppi


# ---------------------------------------------------------------- una ricerca completa su un'unita'

class Unita:
    """Una unita' (erbario A o B): pagine come liste di parole, gruppi di rimescolamento, vocabolario e adiacenza."""

    def __init__(self, pagine, strati):
        self.pagine = pagine
        self.strati = list(strati)
        self.voc, self.token = vocabolario(pagine)
        self.V = len(self.voc)
        self.adj = adiacenza_varianti(self.voc)
        self.C = conteggi_regioni(self.token, self.V)
        self.N = len(pagine)

    def osservato(self):
        return punteggi(self.C, self.adj)

    def nullo(self, tipo, seme):
        """Un campione del nullo `tipo` ('tok' o 'col'): vettore di punteggi."""
        if tipo == 'tok':
            rnd = np.random.RandomState(seme)
            tok = rimescola_token(self.token, self.strati, rnd)
            C = conteggi_regioni(tok, self.V)
        else:
            rng = np.random.default_rng(seme)
            C = rimescola_colonne(self.C, self.strati, rng)
        return punteggi(C, self.adj)[0]


def lavoro_nullo(args):
    """Per i processi in parallelo: (unita', tipo, [semi]) -> lista di vettori. L'unita' arriva gia' costruita (picklata)."""
    unita, tipo, semi = args
    return [unita.nullo(tipo, s) for s in semi]


def valuta(oss, nulli_per_tipo):
    """oss: vettore osservato di un'unita'; nulli_per_tipo: dict tipo -> matrice [K, n_varianti]. Ritorna per ogni tipo:
    z osservati e, per ogni campione del nullo, il suo z (con media e scarto del nullo stesso)."""
    out = {}
    for tipo, M in nulli_per_tipo.items():
        M = np.asarray(M, dtype=float)
        mu = M.mean(0)
        sd = np.maximum(M.std(0, ddof=1) if len(M) > 1 else np.ones(M.shape[1]), 1e-9)
        out[tipo] = dict(z_oss=(np.asarray(oss, dtype=float) - mu) / sd, z_nulli=(M - mu) / sd, mu=mu, sd=sd)
    return out


def p_finale(valutazioni_unita):
    """valutazioni_unita: lista (una per unita') di dict tipo -> risultato di `valuta`. Il massimo si prende su tutte le unita' e
    varianti; ritorna dict(p, p_per_tipo, stat, variante, unita)."""
    per_tipo = {}
    migliore = None
    for tipo in NULLI:
        K = len(valutazioni_unita[0][tipo]['z_nulli'])
        oss = -np.inf
        nul = np.full(K, -np.inf)
        for u, ev in enumerate(valutazioni_unita):
            e = ev[tipo]
            zo = e['z_oss']
            j = int(np.argmax(zo))
            if zo[j] > oss:
                oss, jmax, umax = float(zo[j]), j, u
            nul = np.maximum(nul, e['z_nulli'].max(1))
        p = (1 + int((nul >= oss).sum())) / (K + 1)
        per_tipo[tipo] = dict(p=p, stat=oss, variante=STATISTICHE[jmax][0] + (STATISTICHE[jmax][1], STATISTICHE[jmax][2]), indice=jmax, unita=umax, nullo_medio=float(nul.mean()), nullo_p95=float(np.quantile(nul, 0.95)))
    pf = max(v['p'] for v in per_tipo.values())
    return dict(p=pf, per_tipo=per_tipo)
