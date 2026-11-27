# -*- coding: utf-8 -*-
"""IA45: i mondi di controllo (SOLO testo latino, mai il Voynich) con la stessa forma delle pagine del manoscritto.

La forma (quante righe, quanti segni, a che righe stanno) e' copiata dai CONTEGGI delle pagine f49v, f66r, f76r e dell'anello di
f57v; il testo e' latino (dati/cache/lingue/Latin.txt), un carattere = una unita'. Le righe hanno un effetto d'inizio riga come
le e72/e73: in meta' delle righe la prima parola riceve davanti un segno scelto a caso con pesi s 4, d 3, y 2, q 1.

Mondi:
  A   colonne = un "alfabeto" di 18 segni recitato a ripetizione (fase a caso), con il 20% di errori e l'8% di buchi; le colonne di
      f49v, f66r, f76r e l'anello recitano lo stesso ciclo;
  B   colonne = i segni d'inizio riga delle righe accanto (copiati), con il 20% di errori;
  Bs  come B, ma i segni sono staccati dalle righe (la riga non li porta piu'): solo descrittivo;
  N1  colonne finte di segni pescati a caso dal testo della stessa pagina;
  N2  colonne finte con le prime unita' di righe qualsiasi (altre righe, in ordine);
  N3  il mondo B con i segni mescolati fra le righe.
In tutti i mondi l'anello e' un ciclo di 18 segni recitato con 20% di errori (nei mondi diversi da A, un ciclo suo).
"""
import os, sys
from collections import Counter
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import colonne_dati as CD

PERCORSO_LATINO = os.path.join(QUI, '..', 'dati', 'cache', 'lingue', 'Latin.txt')
ALFABETO = list('abcdefghilmnopqrstuvx')
INIZI = ('s', 'd', 'y', 'q')
PESI_INIZI = (4, 3, 2, 1)
FORME = {
    'f49v': dict(n_righe=26, n=26, dopo=list(range(26)), prima=[None] + list(range(25))),
    'f66r': dict(n_righe=32, n=33, dopo=[0] * 33, prima=[None] * 33),
    'f76r': dict(n_righe=47, n=9, dopo=[3, 5, 7, 10, 13, 16, 20, 23, 28], prima=[2, 4, 6, 9, 12, 15, 19, 22, 27]),
}
N_ANELLO = 64
LUNGHEZZA_CICLO = 18
ERRORI, BUCHI = 0.20, 0.08
MONDI = ('A', 'B', 'Bs', 'N1', 'N2', 'N3')
_PAROLE = []


def parole_latine():
    if not _PAROLE:
        with open(PERCORSO_LATINO, encoding='utf-8') as f:
            _PAROLE.extend(f.read().split())
    return _PAROLE


def righe_fondo(rng, n, senza_aggiunta=()):
    """n righe di 6-10 parole consecutive; ogni riga e' (lista di parole, segno aggiunto o None). Le righe i in `senza_aggiunta`
    non ricevono mai il segno d'inizio riga."""
    ps = parole_latine()
    righe = []
    for i in range(n):
        a = int(rng.integers(0, len(ps) - 12))
        w = list(ps[a:a + int(rng.integers(6, 11))])
        g = None
        if i not in senza_aggiunta and rng.random() < 0.5:
            g = INIZI[int(rng.choice(len(INIZI), p=np.array(PESI_INIZI) / sum(PESI_INIZI)))]
            w[0] = g + w[0]
        righe.append((w, g))
    return righe


def riferimento_fondo(rng, n=3000):
    righe = righe_fondo(rng, n)
    prime, tutte = Counter(), Counter()
    for w, _ in righe:
        prime[w[0][0]] += 1
        for x in w:
            tutte[x[0]] += 1
    return prime, tutte


def ciclo_recitato(rng, ciclo, n):
    """Recita il ciclo da una fase a caso, con errori (un segno a caso dell'alfabeto) e buchi (un segno del ciclo saltato)."""
    pos = int(rng.integers(0, len(ciclo)))
    out = []
    while len(out) < n:
        s = ciclo[pos % len(ciclo)]
        pos += 1
        if rng.random() < BUCHI:
            continue
        out.append(ALFABETO[int(rng.integers(0, len(ALFABETO)))] if rng.random() < ERRORI else s)
    return out


def _errore(rng, s):
    return ALFABETO[int(rng.integers(0, len(ALFABETO)))] if rng.random() < ERRORI else s


def pagina_controllo(nome, rng, mondo, ciclo, ciclo_anello):
    if nome == 'f57v':
        col = ciclo_recitato(rng, ciclo_anello, N_ANELLO)
        return CD.Pagina(nome, col, [None] * len(col), [None] * len(col), [], [], len(col), 0)
    f = FORME[nome]
    n = f['n']
    dopo, prima = list(f['dopo']), list(f['prima'])
    # nel mondo Bs le righe accanto a un segno non portano il segno d'inizio riga (e' stato staccato)
    stacc = set(r for r in dopo if r is not None) if mondo == 'Bs' else ()
    righe = righe_fondo(rng, f['n_righe'], senza_aggiunta=stacc)
    prime = [w[0][0] for w, _ in righe]
    testo = [c for w, _ in righe for x in w for c in x]
    if mondo == 'A':
        col = ciclo_recitato(rng, ciclo, n)
    elif mondo in ('B', 'N3'):
        if nome == 'f66r':
            idx = sorted(int(i) for i in rng.integers(0, f['n_righe'], n))
            col = [_errore(rng, prime[i]) for i in idx]
        else:
            col = [_errore(rng, prime[r]) for r in dopo]
        if mondo == 'N3':
            col = [col[i] for i in rng.permutation(n)]
    elif mondo == 'Bs':
        p = np.array(PESI_INIZI) / sum(PESI_INIZI)
        col = [_errore(rng, INIZI[int(rng.choice(len(INIZI), p=p))]) for _ in range(n)]
    elif mondo == 'N1':
        col = [testo[int(rng.integers(0, len(testo)))] for _ in range(n)]
    elif mondo == 'N2':
        altre = righe_fondo(rng, 4 * n)
        idx = sorted(int(i) for i in rng.choice(len(altre), n, replace=False))
        col = [altre[i][0][0][0] for i in idx]
    else:
        raise ValueError(mondo)
    return CD.Pagina(nome, col, dopo, prima, prime, testo, n, f['n_righe'])


def mondo(nome_mondo, seme):
    """Un mondo di controllo: (pagine, riferimento)."""
    rng = np.random.default_rng([45, MONDI.index(nome_mondo), seme])
    ciclo = [ALFABETO[i] for i in rng.permutation(len(ALFABETO))[:LUNGHEZZA_CICLO]]
    ciclo_anello = ciclo if nome_mondo == 'A' else [ALFABETO[i] for i in rng.permutation(len(ALFABETO))[:LUNGHEZZA_CICLO]]
    pagine = [pagina_controllo(n, rng, nome_mondo, ciclo, ciclo_anello) for n in ('f49v', 'f66r', 'f76r', 'f57v')]
    return pagine, riferimento_fondo(rng)


# ---------------------------------------------------------------------------------------------------------------------
# Mondi N4: righe VERE di ALTRE pagine del manoscritto (mai le pagine delle colonne), per calibrare i falsi allarmi su un testo
# che ha le sue regolarita'. Si costruiscono solo nella fase V del programma (con il manoscritto), prima di toccare le colonne.
#   N4a colonne finte di unita' pescate a caso dal testo della pagina finta;
#   N4b colonne finte con le prime unita' di righe a caso della pagina finta (in ordine).
# La "pagina finta" e' fatta di righe consecutive di pagine consecutive con la stessa lingua A/B di Currier della pagina vera.
# ---------------------------------------------------------------------------------------------------------------------
MONDI_MS = ('N4a', 'N4b')
LINGUA_PAGINA = {'f49v': 'A', 'f66r': 'B', 'f76r': 'B'}     # scritta nelle intestazioni delle trascrizioni


def indice_pagine(righe, quale, escluse=CD.PAGINE_ESCLUSE_RIFERIMENTO):
    """Lista, nell'ordine del file, delle pagine con righe di paragrafo: dict(pagina, lingua, righe=[(prima unita', unita')])."""
    out = {}
    ordine = []
    for r in righe:
        if r.tipo[0] != 'P' or r.pagina in escluse:
            continue
        ps = CD.pulisci_corpo(r.grezza)
        us = [CD.dividi(w, quale) for w in ps]
        us = [u for u in us if u]
        if not us:
            continue
        if r.pagina not in out:
            out[r.pagina] = dict(pagina=r.pagina, lingua=r.lingua, righe=[])
            ordine.append(r.pagina)
        out[r.pagina]['righe'].append((us[0][0], [x for u in us for x in u]))
    return [out[p] for p in ordine]


def mondo_manoscritto(indice, nome_mondo, seme, riferimento):
    """Un mondo N4: (pagine, riferimento). Senza l'anello (non c'e' un anello finto)."""
    rng = np.random.default_rng([45, 100 + MONDI_MS.index(nome_mondo), seme])
    pagine = []
    for nome, f in FORME.items():
        pool = [i for i, p in enumerate(indice) if p['lingua'] == LINGUA_PAGINA[nome]]
        righe = []
        while len(righe) < f['n_righe']:
            i = pool[int(rng.integers(0, len(pool)))]
            righe = []
            j = i
            while len(righe) < f['n_righe'] and j < len(indice) and indice[j]['lingua'] == LINGUA_PAGINA[nome]:
                righe.extend(indice[j]['righe'])
                j += 1
        righe = righe[:f['n_righe']]
        testo = [x for _, us in righe for x in us]
        prime = [p for p, _ in righe]
        n = f['n']
        if nome_mondo == 'N4a':
            col = [testo[int(rng.integers(0, len(testo)))] for _ in range(n)]
        else:
            col = [prime[i] for i in sorted(int(i) for i in rng.integers(0, len(righe), n))]
        pagine.append(CD.Pagina(nome, col, list(f['dopo']), list(f['prima']), prime, testo, n, f['n_righe']))
    return pagine, riferimento
