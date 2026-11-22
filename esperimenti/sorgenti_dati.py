# -*- coding: utf-8 -*-
"""Supporto di ia27 (modulo, non e' un esperimento): i dati del "modello a sorgenti latenti".

Che cosa c'e' qui, in parole semplici
- `Pagina`: una pagina e' una lista di righe; ogni riga ha la fascia di lunghezza (data, come alla GRU di ia07), il segno "inizio di paragrafo" e le
  parole (tuple di glifi EVA fusi, come in ia01). Una pagina porta anche foglio, piega (pieghe per foglio di ia07), sezione, lingua e mano.
- `pagine_vere()`: le pagine del libro vero di ia07 (nelle prove SOLO_CONTROLLI=1: il latino nella disposizione del Voynich).
- `latino_in_disposizione()`: lo stesso, con parole latine (controllo "latino"); dal Voynich si prende solo il numero di parole di ogni riga.
- Rimescolamenti per i controlli negativi (`rimescola`), testi sintetici (usano `sorgenti_genera`), fasce di lunghezza e rischio di fine riga (`Rischio`).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import math
import os
import random
import re
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402

N_FASCE = I7.N_FASCE


class Riga(object):
    __slots__ = ('ini', 'banda', 'lung', 'parole')

    def __init__(self, ini, banda, lung, parole):
        self.ini, self.banda, self.lung, self.parole = bool(ini), int(banda), int(lung), list(parole)


class Pagina(object):
    __slots__ = ('nome', 'foglio', 'piega', 'sezione', 'lingua', 'mano', 'righe')

    def __init__(self, nome, foglio, piega, sezione, lingua, mano, righe):
        self.nome, self.foglio, self.piega = nome, foglio, piega
        self.sezione, self.lingua, self.mano, self.righe = sezione, lingua, mano, righe

    def n_parole(self):
        return sum(len(r.parole) for r in self.righe)

    def copia(self, righe=None):
        return Pagina(self.nome, self.foglio, self.piega, self.sezione, self.lingua, self.mano, righe if righe is not None else
                      [Riga(r.ini, r.banda, r.lung, r.parole) for r in self.righe])


def lunghezza_riga(parole):
    """Segni e spazi di una riga (come ia07.lunghezza): somma dei glifi piu' gli spazi fra le parole."""
    return sum(len(w) for w in parole) + len(parole) - 1


def bordi_fasce(righe_parole):
    """Bordi delle 8 fasce di lunghezza a uguale frequenza (come ia07.vocabolario). `righe_parole`: liste di parole (tuple)."""
    lung = sorted(lunghezza_riga(ws) for ws in righe_parole)
    return [lung[int(len(lung) * i / N_FASCE)] for i in range(1, N_FASCE)]


def fascia_di(lung, bordi):
    return sum(lung >= b for b in bordi)


def da_righe_ia07(righe, D, bordi=None):
    """Da `I7.libro_vero()` (o da una sua copia con altre parole) a una lista di Pagina. Le parole diventano tuple di glifi (divisore D)."""
    pg = I7.pieghe()
    parole = [[tuple(D(w)) for w in x['parole']] for x in righe]
    if bordi is None:
        bordi = bordi_fasce(parole)
    out = OrderedDict()
    for x, ws in zip(righe, parole):
        p = out.get(x['pagina'])
        if p is None:
            p = out[x['pagina']] = Pagina(x['pagina'], x['foglio'], pg[x['foglio']], x['sezione'], x['lingua'], x['mano'], [])
        lu = lunghezza_riga(ws)
        p.righe.append(Riga(x['ini'], fascia_di(lu, bordi), lu, ws))
    return list(out.values()), bordi


_C = {}


def pagine_vere():
    """(pagine, bordi) del libro vero di ia07 (nelle prove: latino con la disposizione del Voynich)."""
    if 'vere' not in _C:
        _C['vere'] = da_righe_ia07(I7.libro_vero(), I7.divisore())
    return _C['vere']


def latino_in_disposizione():
    """(pagine, bordi) con la disposizione vera e parole latine (come ia07 SOLO_CONTROLLI: Macer Floridus nell'erbario di lingua A, Plinio nel resto di A,
    Plinio abbreviato in B). Dal libro vero si usa solo il numero di parole per riga. Le fasce sono ricalcolate sul latino."""
    if 'latino' not in _C:
        righe = I7.libro_vero()
        flussi = I7.latino()
        nuovo = []
        for x in righe:
            f = 'erbario A' if (x['sezione'] == 'H' and x['lingua'] == 'A') else x['lingua'] if x['lingua'] in ('A', 'B') else '?'
            y = dict(x)
            y['parole'] = [next(flussi[f]) for _ in range(len(x['parole']))]
            nuovo.append(y)
        _C['latino'] = da_righe_ia07(nuovo, I7.divisore())
    return _C['latino']


def fogli_piega(piega):
    """(fogli di addestramento, validazione, tenuti fuori) della piega, come ia07."""
    return I7.fogli_della_piega(piega)


def dividi_pagine(pagine, piega):
    """(addestramento, validazione, fuori): liste di Pagina per la piega (pieghe per foglio di ia07). 'tutto': tutte le pagine in addestramento."""
    add, val, fuori = fogli_piega(piega)
    sa, sv, sf = set(add), set(val), set(fuori)
    return ([p for p in pagine if p.foglio in sa], [p for p in pagine if p.foglio in sv], [p for p in pagine if p.foglio in sf])


# ---------------------------------------------------------------- controlli negativi: rimescolamenti

def _gruppo(p):
    return (p.sezione, p.lingua)


def rimescola(pagine, modo, seme):
    """Rimescolamenti che tengono la disposizione (righe, fasce, numero di parole per riga) e cambiano solo quali parole stanno dove.
    - 'fra_pagine': le parole di ogni gruppo (sezione, lingua) si mescolano fra tutte le pagine del gruppo (azzera eco di riga e di pagina);
    - 'dentro_pagina': le parole si mescolano dentro la pagina (azzera l'eco di riga, tiene il tema della pagina);
    - 'righe_fra_pagine': le righe intere (con le loro parole) si mescolano fra le pagine del gruppo (tiene l'eco dentro la riga, azzera quella
      fra righe e il tema della pagina; le fasce restano della disposizione)."""
    rnd = random.Random(seme)
    out = [p.copia() for p in pagine]
    if modo == 'dentro_pagina':
        for p in out:
            ws = [w for r in p.righe for w in r.parole]
            rnd.shuffle(ws)
            k = 0
            for r in p.righe:
                n = len(r.parole)
                r.parole = ws[k:k + n]
                k += n
    elif modo == 'fra_pagine':
        gruppi = OrderedDict()
        for p in out:
            gruppi.setdefault(_gruppo(p), []).append(p)
        for g, ps in gruppi.items():
            ws = [w for p in ps for r in p.righe for w in r.parole]
            rnd.shuffle(ws)
            k = 0
            for p in ps:
                for r in p.righe:
                    n = len(r.parole)
                    r.parole = ws[k:k + n]
                    k += n
    elif modo == 'righe_fra_pagine':
        gruppi = OrderedDict()
        for p in out:
            gruppi.setdefault(_gruppo(p), []).append(p)
        for g, ps in gruppi.items():
            righe = [r.parole for p in ps for r in p.righe]
            rnd.shuffle(righe)
            k = 0
            for p in ps:
                for r in p.righe:
                    r.parole = list(righe[k])
                    k += 1
                    r.lung = lunghezza_riga(r.parole)       # la lunghezza della riga cambia con le parole: la fascia resta quella della disposizione
    else:
        raise ValueError(modo)
    for p in out:
        for r in p.righe:
            r.lung = lunghezza_riga(r.parole)
    return out


# ---------------------------------------------------------------- rischio di fine riga

class Rischio(object):
    """Rischio di fine riga dopo una parola: P(la riga finisce qui | fascia, lunghezza raggiunta). Con la fascia data la lunghezza della riga cade in
    [lo, hi): sotto `lo` la riga non puo' finire, da hi-1 in poi finisce di sicuro. In mezzo si parte dal rischio uniforme 1/(hi - l) e lo si corregge con i
    conteggi (peso 2, come una lisciatura). E' lo stesso per tutte le versioni del modello: i bit dei segni di fine parola (spazio o fine riga) stanno
    qui. Stimato sulle pagine di addestramento."""
    EPS = 1e-6

    def __init__(self, pagine, bordi):
        self.bordi = list(bordi)
        lmax = max(r.lung for p in pagine for r in p.righe)
        self.lo = [0] + list(bordi)
        self.hi = list(bordi) + [lmax + 1]
        self.fine = Counter()
        self.arrivi = Counter()
        for p in pagine:
            for r in p.righe:
                cum = -1
                for k, w in enumerate(r.parole):
                    cum += len(w) + (1 if k else 0)
                    self.arrivi[(r.banda, cum)] += 1
                    if k == len(r.parole) - 1:
                        self.fine[(r.banda, cum)] += 1
        self._t = {}

    def rischio(self, banda, cum):
        k = (banda, cum)
        v = self._t.get(k)
        if v is None:
            lo, hi = self.lo[banda], self.hi[banda]
            if cum < lo:
                v = self.EPS
            elif cum >= hi - 1:
                v = 1.0 - self.EPS
            else:
                h0 = 1.0 / (hi - cum)
                v = (self.fine[k] + 2.0 * h0) / (self.arrivi[k] + 2.0)
                v = min(max(v, self.EPS), 1.0 - self.EPS)
            self._t[k] = v
        return v

    def bit(self, banda, cum, fine):
        """Bit del simbolo "la riga finisce qui" (fine=True) o "continua" (False)."""
        h = self.rischio(banda, cum)
        return -math.log2(h if fine else 1.0 - h)
