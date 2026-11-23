# -*- coding: utf-8 -*-
"""IA33, modulo di supporto: generatori a conteggi senza rete (l'"oracolo" e il baseline classico).

In parole semplici
- **La vera catena** del mondo `markov2` di IA26 (`righello_testi`, `ia01.markov`): una catena di Markov di ordine 2 sui glifi, stimata sul libro intero, che scrive
  ogni riga con lo stesso numero di parole della riga del libro. Qui c'e' una copia fedele del suo procedimento (`conta`, `genera_vere`), provata uguale all'originale
  (`oracolo_prove.py`): serve a fare altri campioni "gemelli" della vera catena (semi nuovi) e a stimare la catena da un testo piu' piccolo.
- **L'oracolo stimato** (parte O): la stessa famiglia (ordine 2 sui glifi), ma stimata dai conteggi dei 78 fogli d'addestramento del mondo, non dal libro intero.
    * `KNCatena` (ufficiale, fissato prima): Kneser-Ney interpolato di ordine 3 (due glifi di contesto), con lo sconto di Good-Turing per ordine (come il giudice KN di IA26,
      `righello_giudici.KneserNey`, importato senza modificarlo); si scrive riga per riga con lo stesso numero di parole del libro.
    * `genera_vere` con i conteggi grezzi (secondario): lo stesso procedimento della vera catena, solo con meno testo (nessun lisciamento oltre il ripiego che la vera catena gia' usa).
    * Con piu' testo (2 e 4 volte): il testo d'addestramento e' quello del mondo piu' campioni della VERA catena sulla disposizione dei fogli d'addestramento.
- **Il baseline classico sul Voynich** (parte V): `KNCatena` con l'ordine scelto sulla validazione (3, 4, 5 o 6 segni, come il giudice KN) su glifi e spazi, stimato sui fogli
  d'addestramento; scrive con lo stesso numero di parole per riga del libro.
Tutto e' deterministico dato il seme. Nessuna rete. Nessun risultato e' scritto qui.
"""
import math
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia01_giudice_neurale as G  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import righello_giudici as RG  # noqa: E402

NL, SP = G.NL, G.SP
ID_NL, ID_SP = 1, 2                      # id dei simboli di KNCatena (0 non usato; i glifi da 3 in poi); NL_ID di righello_giudici e' 1
MAX_PAROLA = 25                          # come ia01.markov: oltre questa lunghezza la parola si chiude
ORDINI_V = (3, 4, 5, 6)                  # ordini provati per il baseline classico (come il giudice KN)


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- testi nel formato "vere": pagina -> [(inizio, [parola come tupla di glifi])]

def vere_di_righe(righe, fogli=None):
    """Le righe (dizionari come `I7.libro_vero()`) -> pagine nel formato di ia01, solo dei fogli `fogli` (None: tutti). Nessun filtro sul numero di parole."""
    D = I7.divisore()
    ins = None if fogli is None else set(fogli)
    out = OrderedDict()
    for x in righe:
        if ins is not None and x['foglio'] not in ins:
            continue
        out.setdefault(x['pagina'], []).append((bool(x['ini']), [tuple(D(w)) for w in x['parole']]))
    return out


def layout_di_righe(righe, fogli=None):
    """La disposizione: pagina -> [(inizio, numero di parole)] (solo i fogli `fogli`)."""
    ins = None if fogli is None else set(fogli)
    out = OrderedDict()
    for x in righe:
        if ins is not None and x['foglio'] not in ins:
            continue
        out.setdefault(x['pagina'], []).append((bool(x['ini']), len(x['parole'])))
    return out


def t_da_vere(vere):
    """pagine nel formato "vere" -> lista (pagina, inizio, [parole come stringhe]) come `I7.leggi_file`."""
    return [(p, bool(ini), [''.join(w) for w in ws]) for p, rows in vere.items() for ini, ws in rows]


# ---------------------------------------------------------------- la vera catena (copia fedele di ia01.markov) e la sua stima da conteggi grezzi

def conta(lista_vere, ordine=2):
    """I conteggi di `ia01.markov`: per ogni lunghezza di contesto 0..ordine, il contesto (da NL a inizio riga) -> Counter dei simboli (glifi e spazio dopo ogni parola).
    `lista_vere`: una lista di dizionari "vere" (si sommano)."""
    cont = defaultdict(Counter)
    for vere in lista_vere:
        for rows in vere.values():
            for _, ws in rows:
                seq = [NL] * ordine
                for w in ws:
                    for s in list(w) + [SP]:
                        for k in range(0, ordine + 1):
                            cont[tuple(seq[len(seq) - k:]) if k else ()][s] += 1
                        seq.append(s)
    return cont


def genera_vere(cont, layout, seme, ordine=2):
    """Come `ia01.markov`, ma con i conteggi `cont` (anche stimati da un testo piu' piccolo) e la disposizione `layout` (pagina -> [(inizio, numero di parole)]).
    Con i conteggi del libro intero e il suo seme riproduce `ia01.markov` identico (provato in `oracolo_prove`). -> pagine nel formato "vere"."""
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in layout.items():
        nuove = []
        for ini, n in rows:
            seq, parole, cur = [NL] * ordine, [], []
            while len(parole) < n:
                s = None
                for k in range(ordine, -1, -1):
                    c = cont.get(tuple(seq[len(seq) - k:]) if k else ())
                    if c:
                        ch = list(c.items())
                        s = rnd.choices([a for a, _ in ch], [b for _, b in ch])[0]
                        if s == SP and not cur:
                            s = None
                            continue
                        break
                if s is None or len(cur) > MAX_PAROLA:
                    s = SP if cur else 'e'
                seq.append(s)
                if s == SP:
                    parole.append(tuple(cur))
                    cur = []
                else:
                    cur.append(s)
            nuove.append((ini, parole))
        out[p] = nuove
    return out


# ---------------------------------------------------------------- Kneser-Ney scritto (oracolo ufficiale e baseline V)

class KNCatena:
    """Un modello a n-grammi con smorzamento di Kneser e Ney (`righello_giudici.KneserNey`), addestrato su RIGHE di glifi e spazi, che scrive righe con un numero
    di parole dato. Simboli: 1 = a capo (contesto di inizio riga), 2 = spazio, 3.. = glifi. `ordine` = numero di simboli del n-gramma (3: due di contesto)."""

    def __init__(self, righe_parole, ordine, glifi):
        """`righe_parole`: lista di righe, ogni riga una lista di parole (tuple di glifi). `glifi`: elenco ordinato di tutti i glifi possibili."""
        self.ordine = int(ordine)
        self.glifi = list(glifi)
        self.id = {g: 3 + i for i, g in enumerate(self.glifi)}
        self.simbolo = {3 + i: g for i, g in enumerate(self.glifi)}
        self.V = 3 + len(self.glifi)
        self.kn = RG.KneserNey(self.sequenze(righe_parole), self.ordine, self.V)
        self._d = {}

    def sequenze(self, righe_parole):
        out = []
        for ws in righe_parole:
            s = []
            for w in ws:
                s.extend(self.id[g] for g in w)
                s.append(ID_SP)
            out.append(np.array(s, dtype=np.int64))
        return out

    def bit(self, righe_parole):
        """Bit per simbolo medi su righe (per scegliere l'ordine sulla validazione)."""
        return self.kn.bit_medi(self.sequenze(righe_parole))

    def distribuzione(self, h, vieta_spazio):
        """(simboli, probabilita') ammessi dopo il contesto `h` (tupla degli ultimi ordine-1 simboli): senza lo 0 e senza l'a capo; senza lo spazio se `vieta_spazio`."""
        k = (h, vieta_spazio)
        r = self._d.get(k)
        if r is None:
            ids = [ID_SP] * (0 if vieta_spazio else 1) + list(range(3, self.V))
            p = np.array([self.kn.prob(h, s) for s in ids], float)
            r = (np.array(ids), np.cumsum(p / p.sum()))
            self._d[k] = r
        return r

    def scrivi_riga(self, n_parole, rnd):
        """Una riga di `n_parole` parole (lista di tuple di glifi)."""
        o = self.ordine
        seq = [ID_NL] * (o - 1)
        parole, cur = [], []
        while len(parole) < n_parole:
            ids, cum = self.distribuzione(tuple(seq[len(seq) - (o - 1):]) if o > 1 else (), not cur)
            s = int(ids[min(int(np.searchsorted(cum, rnd.random() * cum[-1], side='right')), len(ids) - 1)])
            if len(cur) > MAX_PAROLA:
                s = ID_SP
            seq.append(s)
            if s == ID_SP:
                parole.append(tuple(cur))
                cur = []
            else:
                cur.append(self.simbolo[s])
        return parole

    def genera_vere(self, layout, seme):
        rnd = random.Random(seme)
        out = OrderedDict()
        for p, rows in layout.items():
            out[p] = [(ini, self.scrivi_riga(n, rnd)) for ini, n in rows]
        return out


def righe_di_vere(vere):
    """Tutte le righe (liste di parole) di un dizionario "vere"."""
    return [ws for rows in vere.values() for _, ws in rows]


def glifi_del_libro(righe):
    """L'elenco ordinato dei glifi (unita' di `I7.divisore`) di tutto il libro del mondo: solo l'elenco, nessuna frequenza (come `I7.vocabolario`)."""
    D = I7.divisore()
    return sorted({u for x in righe for w in x['parole'] for u in D(w)})


def scegli_ordine(righe_add, righe_val, glifi, ordini=ORDINI_V):
    """L'ordine di KN con meno bit per simbolo sulla validazione (le righe tenute da parte, mai l'esito di un giudice). -> (modello, ordine, bit, tutti i bit)."""
    scelta, tutti = None, OrderedDict()
    for o in ordini:
        m = KNCatena(righe_add, o, glifi)
        b = m.bit(righe_val)
        tutti[o] = round(float(b), 4)
        if scelta is None or b < scelta[0]:
            scelta = (b, o, m)
    return scelta[2], scelta[1], scelta[0], tutti


if __name__ == '__main__':
    pass
