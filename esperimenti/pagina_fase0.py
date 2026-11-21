# -*- coding: utf-8 -*-
"""Supporto di ia23 (modulo, non e' un esperimento): la "fase 0" descrittiva, il profilo di distanza dell'eco.

Domanda: per ogni parola che e' uguale, o a una modifica (un glifo cambiato, aggiunto o tolto), da una parola GIA' SCRITTA nella pagina, a che distanza in
righe sta la ripresa piu' vicina? 0 = nella stessa riga, 1 = nella riga sopra, 2, 3-5, 6 o piu' righe sopra. Dice da dove viene l'eco: dalle righe vicine
(eco locale) o da tutta la pagina (tema).

Che cosa c'e' qui, in parole semplici
- `vettore_pagina`: per una pagina (lista di righe (inizio, [parola, ...]), parola = tupla di glifi) un vettore di 23 conti: parole; per classe di distanza
  le riprese piu' vicine uguali e a una modifica; le parole senza ripresa; le riprese ESATTE piu' vicine per classe (e quelle senza); le riprese esatte "di tema"
  (parola presente almeno 3 volte nella pagina e fuori dalle 200 piu' frequenti del testo) per classe.
- `profilo_testo`: i vettori del testo e di due riferimenti a caso (5 ripetizioni ciascuno, medie):
    "righe rimescolate" (le righe di tutto il testo mescolate fra le pagine: nessuna eco, ne' locale ne' di pagina, solo il caso del vocabolario);
    "parole rimescolate" (le parole di ogni pagina rimescolate dentro la pagina, righe delle stesse lunghezze: resta il tema di pagina, sparisce l'eco locale).
- `misure`: dai conti, le quote per classe, la quota locale (classi 0-1, quelle che i modelli di ia22 vedevano), la quota lontana (classi 2 e oltre), il "tasso
  lontano condizionato" (fra le parole senza ripresa esatta nelle classi 0-1, la quota con ripresa esatta a 2 righe o piu': cresce con il tema di pagina) e la quota
  di riprese di tema.
Solo numeri e aggregati: nessuna parola esce da qui.
"""
import math
from collections import Counter, OrderedDict, defaultdict

import numpy as np

CLASSI = ('0', '1', '2', '3-5', '6+')
NV = 23
N_RIM = 5                    # ripetizioni dei riferimenti a caso
TOP_N = 200                  # parole "frequenti" nel manoscritto (come K di ia20/ia22)
TEMA_MIN = 3                 # occorrenze minime in una pagina di una parola "di tema"
# fissate dopo le prove su testi non Voynich (dichiarato): 'assente_quota' (0,01) e' stata aggiunta perche' un testo senza niente di piantato dava un eccesso
# di 0,004 (piccolo ma oltre 2 errori): una differenza sotto un punto percentuale non conta come "presente" ne' come "zona grigia"
SOGLIE = OrderedDict([('presente_errori', 3.0), ('presente_quota', 0.02), ('assente_errori', 2.0), ('assente_quota', 0.01)])


def classe(dl):
    return 0 if dl <= 0 else 1 if dl == 1 else 2 if dl == 2 else 3 if dl <= 5 else 4


def top_tipi(pagine, n=TOP_N):
    """Le `n` parole piu' frequenti del testo (insieme di tipi)."""
    c = Counter(w for rows in pagine.values() for _, ws in rows for w in ws)
    return {w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:n]}


def vettore_pagina(rows, top):
    """Vettore di NV conti per una pagina. Posti: 0 parole; 1-5 riprese piu' vicine UGUALI per classe di distanza; 6-10 riprese piu' vicine a UNA MODIFICA (se la
    piu' vicina e' uguale conta fra le uguali: a pari distanza vince l'uguale); 11 parole senza ripresa; 12-16 riprese ESATTE piu' vicine per classe; 17 parole
    senza ripresa esatta; 18-22 riprese esatte di parole "di tema" per classe."""
    ex = {}                                  # tipo -> ultima riga in cui compare
    dele = defaultdict(set)                  # (posto, parola senza quel glifo) -> tipi
    conti = Counter(w for _, ws in rows for w in ws)
    tema = {w for w, n in conti.items() if n >= TEMA_MIN and w not in top}
    v = np.zeros(NV)
    for r, (_, ws) in enumerate(rows):
        for w in ws:
            v[0] += 1
            n = len(w)
            d_eq = (r - ex[w]) if w in ex else None
            best, kind = d_eq, 'u'
            neigh = set()
            for i in range(n):
                neigh |= dele.get((i, w[:i] + w[i + 1:]), set())          # un glifo cambiato (stessa lunghezza)
            if n >= 2:
                for i in range(n):
                    c = w[:i] + w[i + 1:]
                    if c in ex:
                        neigh.add(c)                                      # un glifo aggiunto (il candidato e' w senza un glifo)
            for i in range(n + 1):
                neigh |= dele.get((i, w), set())                          # un glifo tolto (il candidato e' w con un glifo in piu')
            neigh.discard(w)
            for c in neigh:
                d = r - ex[c]
                if best is None or d < best:
                    best, kind = d, 'v'
            if best is None:
                v[11] += 1
            else:
                v[(1 if kind == 'u' else 6) + classe(best)] += 1
            if d_eq is None:
                v[17] += 1
            else:
                v[12 + classe(d_eq)] += 1
                if w in tema:
                    v[18 + classe(d_eq)] += 1
            if w not in ex:
                for i in range(n):
                    dele[(i, w[:i] + w[i + 1:])].add(w)
            ex[w] = r
    return v


def _nullo_righe(pagine, rng):
    """Le righe di tutto il testo mescolate fra le pagine (ogni pagina ha lo stesso numero di righe)."""
    righe = [ws for rows in pagine.values() for _, ws in rows]
    perm = rng.permutation(len(righe))
    out, k = OrderedDict(), 0
    for p, rows in pagine.items():
        out[p] = [(ini, righe[perm[k + i]]) for i, (ini, _) in enumerate(rows)]
        k += len(rows)
    return out


def _nullo_parole(pagine, rng):
    """Le parole di ogni pagina rimescolate dentro la pagina (stesse lunghezze di riga)."""
    out = OrderedDict()
    for p, rows in pagine.items():
        tutte = [w for _, ws in rows for w in ws]
        perm = rng.permutation(len(tutte))
        k, nuove = 0, []
        for ini, ws in rows:
            nuove.append((ini, [tutte[perm[k + i]] for i in range(len(ws))]))
            k += len(ws)
        out[p] = nuove
    return out


def profilo_testo(pagine, seme, per_pagina=False, nulli=True):
    """`pagine`: pagina -> righe. -> dizionario con la somma dei vettori del testo (`testo`) e, se `nulli`, dei due riferimenti a caso (medie su N_RIM
    ripetizioni): `nullo_righe`, `nullo_parole`; con `per_pagina` anche i vettori pagina per pagina (per l'errore da ricampionamento)."""
    top = top_tipi(pagine)
    rng = np.random.default_rng(seme)
    nomi = list(pagine)
    vt = np.array([vettore_pagina(pagine[p], top) for p in nomi])
    out = OrderedDict(pagine=len(nomi), testo=vt.sum(0).tolist())
    if per_pagina:
        out['per_pagina'] = OrderedDict(testo=vt.tolist())
    if nulli:
        for nome, f in (('nullo_righe', _nullo_righe), ('nullo_parole', _nullo_parole)):
            vs = []
            for _ in range(N_RIM):
                pg = f(pagine, rng)
                vs.append(np.array([vettore_pagina(pg[p], top) for p in nomi]))
            m = np.mean(vs, axis=0)
            out[nome] = m.sum(0).tolist()
            if per_pagina:
                out['per_pagina'][nome] = m.tolist()
    return out


def misure(S):
    """Dai conti S (somma di vettori) i numeri letti."""
    S = np.asarray(S, dtype=np.float64)
    par = S[0]
    anyc = S[1:6] + S[6:11]
    ex, exn, th = S[12:17], S[17], S[18:23]
    out = OrderedDict()
    out['parole'] = par
    for i, c in enumerate(CLASSI):
        out['q_' + c] = anyc[i] / par if par else None
    out['senza_ripresa'] = S[11] / par if par else None
    out['locale'] = anyc[:2].sum() / par if par else None
    out['lontana'] = anyc[2:].sum() / par if par else None
    out['ripresa'] = anyc.sum() / par if par else None
    pool = ex[2:].sum() + exn
    out['tema_cond'] = ex[2:].sum() / pool if pool else None
    out['quota_tema'] = th.sum() / ex.sum() if ex.sum() else None
    out['tema_lontano'] = th[2:].sum() / par if par else None
    return out


MISURE_LETTE = ('locale', 'lontana', 'tema_cond', 'quota_tema', 'tema_lontano')


def riassunto(r, boot=200, seme=1):
    """Da `profilo_testo(..., per_pagina=True)`: le misure del testo e dei due riferimenti, le differenze (testo meno riferimento) con l'errore da ricampionamento
    delle pagine: `eccesso_tema` = tasso lontano condizionato del testo meno quello delle righe rimescolate; `eccesso_locale` = quota locale del testo meno quella
    delle parole rimescolate."""
    pp = {k: np.array(v) for k, v in r['per_pagina'].items()}
    n = len(pp['testo'])
    rng = np.random.default_rng(seme)
    out = OrderedDict()
    for k in ('testo', 'nullo_righe', 'nullo_parole'):
        if k in pp:
            out[k] = misure(pp[k].sum(0))

    def diff(a, b, m):
        x = misure(pp[a].sum(0))[m]
        y = misure(pp[b].sum(0))[m]
        bs = []
        for _ in range(boot):
            ix = rng.integers(0, n, n)
            u, w = misure(pp[a][ix].sum(0))[m], misure(pp[b][ix].sum(0))[m]
            if u is not None and w is not None:
                bs.append(u - w)
        d = (x - y) if x is not None and y is not None else None
        return OrderedDict(differenza=d, errore=float(np.std(bs, ddof=1)) if len(bs) > 1 else None)
    if 'nullo_righe' in pp:
        out['eccesso_tema'] = diff('testo', 'nullo_righe', 'tema_cond')
        out['eccesso_lontana'] = diff('testo', 'nullo_righe', 'lontana')
    if 'nullo_parole' in pp:
        out['eccesso_locale'] = diff('testo', 'nullo_parole', 'locale')
        out['eccesso_tema_su_parole'] = diff('nullo_parole', 'nullo_righe', 'tema_cond') if 'nullo_righe' in pp else None
    return out


def lettura(d):
    """'presente' / 'assente' / 'zona grigia' per un eccesso `d` = dict(differenza, errore). Soglie scritte prima."""
    if d is None or d['differenza'] is None or not d['errore']:
        return 'non calcolabile'
    if d['differenza'] > SOGLIE['presente_errori'] * d['errore'] and d['differenza'] > SOGLIE['presente_quota']:
        return 'presente'
    if d['differenza'] <= max(SOGLIE['assente_errori'] * d['errore'], SOGLIE['assente_quota']):
        return 'assente'
    return 'zona grigia'
