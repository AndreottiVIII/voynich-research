# -*- coding: utf-8 -*-
"""Un risolutore per sostituzioni omofoniche senza spazi, a ricottura simulata.

E' il metodo con cui si risolvono i cifrari omofonici veri (quelli dello
Zodiac, per esempio): si parte da una chiave a caso e la si cambia un simbolo
alla volta; un cambio che migliora si tiene sempre, uno che peggiora si tiene
con una probabilita' che cala man mano che la "temperatura" scende. Cosi' la
ricerca non resta intrappolata nella prima chiave discreta che trova.

Due accorgimenti lo rendono abbastanza veloce da fare centinaia di migliaia di
prove:
- il testo cifrato si riduce una volta per tutte ai conteggi dei suoi gruppi
  di n simboli consecutivi (dentro la stessa riga): il punteggio di una chiave
  dipende solo da quelli;
- cambiando la lettera di un simbolo si ricalcolano solo i gruppi che lo
  contengono.

Il modello della lingua e' a n-grammi di lettere (n = 5 di solito), senza
spazi, con interpolazione alla Witten-Bell fra gli ordini, in una tabella
densa: una lettura per gruppo.
"""
import math
from collections import Counter, namedtuple

import numpy as np


class ModelloLettere:
    """n-grammi di lettere senza spazi, con interpolazione Witten-Bell."""

    def __init__(self, testo, n=5):
        self.n = n
        self.lettere = sorted(set(testo))
        self.indice = {c: i for i, c in enumerate(self.lettere)}
        A = len(self.lettere)
        x = np.array([self.indice[c] for c in testo], dtype=np.int64)
        prob = np.bincount(x, minlength=A).astype(np.float64) + 0.5
        prob /= prob.sum()                                   # ordine 1
        for k in range(2, n + 1):
            # conteggi dei k-grammi come tabella densa A^k
            codice = np.zeros(len(x) - k + 1, dtype=np.int64)
            for j in range(k):
                codice = codice * A + x[j:len(x) - k + 1 + j]
            conti = np.bincount(codice, minlength=A ** k).astype(np.float64).reshape((A ** (k - 1), A))
            N = conti.sum(axis=1, keepdims=True)                # occorrenze del contesto
            T = (conti > 0).sum(axis=1, keepdims=True)          # continuazioni diverse
            # probabilita' dell'ordine inferiore per il contesto accorciato
            inferiore = prob.reshape((A ** (k - 2), A)) if k > 2 else prob.reshape((1, A))
            inferiore = np.tile(inferiore, (A, 1)) if k > 2 else np.tile(inferiore, (A, 1))
            with np.errstate(invalid='ignore', divide='ignore'):
                p = np.where(N > 0, (conti + T * inferiore) / (N + T), inferiore)
            prob = p.reshape(-1)
        self.logp = np.log(prob).astype(np.float32)          # indice: codice del n-gramma
        self.A = A

    def punteggio_testo(self, testo):
        """Log-probabilita' media per lettera di un testo (lettere del modello)."""
        x = np.array([self.indice[c] for c in testo if c in self.indice], dtype=np.int64)
        codice = np.zeros(len(x) - self.n + 1, dtype=np.int64)
        for j in range(self.n):
            codice = codice * self.A + x[j:len(x) - self.n + 1 + j]
        return float(self.logp[codice].mean())


class Grammi:
    """Il testo cifrato ridotto ai conteggi dei suoi n-grammi di simboli, dentro
    le righe. righe: liste di simboli (qualsiasi cosa hashabile)."""

    def __init__(self, righe, n):
        simboli = sorted({s for r in righe for s in r}, key=str)
        self.simboli = simboli
        self.indice = {s: i for i, s in enumerate(simboli)}
        conti = Counter()
        self.frequenza = Counter()
        for r in righe:
            ids = [self.indice[s] for s in r]
            self.frequenza.update(ids)
            for i in range(len(ids) - n + 1):
                conti[tuple(ids[i:i + n])] += 1
        self.G = np.array(list(conti.keys()), dtype=np.int64)
        self.c = np.array(list(conti.values()), dtype=np.float64)
        self.totale = self.c.sum()
        self.contiene = [np.nonzero((self.G == s).any(axis=1))[0] for s in range(len(simboli))]


def _codici(chiave, G, A):
    codice = np.zeros(len(G), dtype=np.int64)
    for j in range(G.shape[1]):
        codice = codice * A + chiave[G[:, j]]
    return codice


def punteggio(chiave, grammi, modello):
    return float((modello.logp[_codici(chiave, grammi.G, modello.A)] * grammi.c).sum() / grammi.totale)


Esito = namedtuple('Esito', 'modello obiettivo chiave')


def _entropia_conti(conti):
    """-sum c log c, per l'entropia delle lettere decifrate (senza la costante)."""
    c = conti[conti > 0]
    return float(-(c * np.log(c)).sum())


def ricottura(grammi, modello, rnd, passi=200000, t0=0.5, t1=0.002, chiave=None, peso_entropia=1.0,
              verboso=False):
    """Ricottura simulata sulla chiave simbolo -> lettera.

    L'obiettivo e' la probabilita' del testo decifrato secondo il modello
    della lingua, piu' l'entropia delle lettere decifrate (moltiplicata per il
    numero di lettere). Il secondo termine non e' un trucco: e' la
    probabilita' di aver scelto quei simboli per quelle lettere, se ogni
    lettera sceglie i suoi simboli con le loro frequenze osservate
    (sum log P(simbolo | lettera) = N H(lettere) - N H(simboli)). Senza, la
    ricerca cade in chiavi degeneri che usano cinque o sei lettere frequenti
    ("etetitis...").

    Restituisce un Esito: punteggio medio per lettera del solo modello,
    obiettivo completo per lettera (per scegliere fra ripartenze), chiave.
    """
    S, A = len(grammi.simboli), modello.A
    if chiave is None:
        chiave = np.array([rnd.randrange(A) for _ in range(S)], dtype=np.int64)
    chiave = chiave.copy()
    freq = np.array([grammi.frequenza[s] for s in range(S)], dtype=np.float64)
    scala = peso_entropia * grammi.totale / freq.sum()       # N H(q), sulla scala dei n-grammi
    conti = np.bincount(chiave, weights=freq, minlength=A).astype(np.float64)
    contributi = modello.logp[_codici(chiave, grammi.G, A)] * grammi.c
    lm = contributi.sum()
    ent = scala * _entropia_conti(conti)
    attuale = lm + ent
    migliore, chiave_migliore, lm_migliore = attuale, chiave.copy(), lm
    # si scelgono i simboli in proporzione alla radice della frequenza
    cumul = np.cumsum(np.sqrt(freq) / np.sqrt(freq).sum())
    fattore = (t1 / t0) ** (1.0 / passi)
    t = t0 * grammi.totale
    accettati = 0
    xlogx = lambda x: x * math.log(x) if x > 0 else 0.0
    for passo in range(passi):
        if verboso and passo % (passi // 20) == 0:
            print('    passo %7d  t %.4f  modello %.4f  migliore %.4f  accettati %.2f' % (
                passo, t / grammi.totale, lm / grammi.totale, lm_migliore / grammi.totale,
                accettati / max(1, passi // 20)), flush=True)
            accettati = 0
        s = min(int(np.searchsorted(cumul, rnd.random())), S - 1)
        nuova = rnd.randrange(A - 1)
        vecchia = int(chiave[s])
        if nuova >= vecchia:
            nuova += 1
        idx = grammi.contiene[s]
        chiave[s] = nuova
        nuovi = modello.logp[_codici(chiave, grammi.G[idx], A)] * grammi.c[idx]
        d_lm = nuovi.sum() - contributi[idx].sum()
        f = freq[s]
        d_ent = scala * (xlogx(conti[vecchia]) + xlogx(conti[nuova])
                         - xlogx(conti[vecchia] - f) - xlogx(conti[nuova] + f))
        delta = d_lm + d_ent
        if delta >= 0 or rnd.random() < math.exp(delta / t):
            accettati += 1
            contributi[idx] = nuovi
            conti[vecchia] -= f
            conti[nuova] += f
            lm += d_lm
            attuale += delta
            if attuale > migliore:
                migliore, chiave_migliore, lm_migliore = attuale, chiave.copy(), lm
        else:
            chiave[s] = vecchia
        t *= fattore
    return Esito(lm_migliore / grammi.totale, migliore / grammi.totale, chiave_migliore)


def risolvi(grammi, modello, rnd, ripartenze=4, passi=None, peso_entropia=1.0):
    """Piu' ricotture da chiavi a caso; tiene quella con l'obiettivo migliore.
    I passi crescono col numero di simboli."""
    passi = passi or 1500 * len(grammi.simboli)
    esiti = [ricottura(grammi, modello, rnd, passi=passi, peso_entropia=peso_entropia)
             for _ in range(ripartenze)]
    return max(esiti, key=lambda e: e.obiettivo), esiti


def punteggio_righe(righe, modello):
    """Log-probabilita' media per lettera di righe di testo, con gli n-grammi
    dentro le righe come nel risolutore (le lettere che il modello non conosce
    spezzano la riga)."""
    codici = []
    for r in righe:
        pezzo = []
        for c in r + '\0':
            i = modello.indice.get(c)
            if i is not None:
                pezzo.append(i)
                continue
            if len(pezzo) >= modello.n:
                x = np.array(pezzo, dtype=np.int64)
                codice = np.zeros(len(x) - modello.n + 1, dtype=np.int64)
                for j in range(modello.n):
                    codice = codice * modello.A + x[j:len(x) - modello.n + 1 + j]
                codici.append(codice)
            pezzo = []
    return float(modello.logp[np.concatenate(codici)].mean()) if codici else float('nan')


def decifra(righe, chiave, grammi, modello):
    """Le righe cifrate tradotte con la chiave (simboli sconosciuti: '?')."""
    return [''.join(modello.lettere[chiave[grammi.indice[s]]] if s in grammi.indice else '?' for s in r)
            for r in righe]
