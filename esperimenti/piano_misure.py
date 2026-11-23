# -*- coding: utf-8 -*-
"""IA34, modulo di supporto: sei MISURE NUOVE sulla struttura di libro, di pagina e di riga, tenute fuori dal ciclo (si guardano solo all'esame).

In parole semplici
- Nessun generatore e nessun esperimento IA16-IA33 le ha usate come obiettivo, e non sono nel banco di IA26. Si calcolano su un testo nel formato di ia01
  (pagina -> [(inizio paragrafo, [parola come tupla di glifi])]), sulle pagine con almeno 40 parole (quelle dei giudici), e per ogni mondo si danno il valore sul testo vero,
  la scala (deviazione standard della differenza fra le due meta' di una divisione per fogli del testo vero, `S_NM34` divisioni) e quindi sigma = scala / radice di 2, come
  per le misure del banco.
    heaps         crescita del vocabolario lungo il libro: pendenza (in scala logaritmica) dei tipi di parola contro le parole lette, a 8 punti equidistanti
    burst         dispersione delle parole fra pagine: per le 100 parole piu' frequenti, pagine in cui compaiono / pagine attese se le occorrenze cadessero a caso
                  (in proporzione alla lunghezza delle pagine); media sulle parole (sotto 1: le parole stanno raggruppate)
    riga_cv       distribuzione delle lunghezze di riga: coefficiente di variazione (deviazione standard / media) della lunghezza in glifi
    sezione       somiglianza di vocabolario fra pagine: coseno medio fra pagine della stessa sezione (e lingua) meno coseno medio fra pagine di sezioni diverse
                  (2000 + 2000 coppie, seme fisso; vettori sulle 400 parole piu' frequenti del testo)
    lag23         autocorrelazione fra righe a distanza 2 e 3 nella stessa pagina: sovrapposizione media (Jaccard) dei tipi di parola, meno quella media di righe di pagine
                  diverse (3000 coppie, seme fisso)
    ini_par       frequenza dei glifi d'inizio paragrafo: entropia (bit) del primo glifo della prima parola delle righe che aprono un paragrafo
- Non entrano nell'obiettivo del ciclo: `sezione` e `lag23` sono vicine a due manopole (vocabolario di sezione, ripresa dalla riga sopra) ma non le contano come misura.
Nessun risultato e' scritto qui.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402

S_NM34 = int(os.environ.get('S_NM34', 100))
NOMI_NM = ('heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par')
TOP_BURST = 100
TOP_SEZ = 400
COPPIE_SEZ = 2000
COPPIE_LAG = 3000
_K = {}


def chiavi_pagina():
    """pagina -> (sezione, lingua) dal libro del mondo attivo."""
    if 'chiavi' not in _K:
        _K['chiavi'] = {}
        for x in I7.libro_vero():
            _K['chiavi'].setdefault(x['pagina'], (x['sezione'], x['lingua']))
    return _K['chiavi']


def _heaps(rows):
    toks = [w for rr in rows.values() for _, ws in rr for w in ws]
    n = len(toks)
    if n < 800:
        return None
    visti, tipi, pts = set(), [], []
    cp = {int(n * k / 8) for k in range(1, 9)}
    for i, w in enumerate(toks, 1):
        visti.add(w)
        if i in cp:
            pts.append((i, len(visti)))
    a, _ = np.polyfit(np.log([p for p, _ in pts]), np.log([t for _, t in pts]), 1)
    return float(a)


def _burst(rows):
    pag = [Counter(w for _, ws in rr for w in ws) for rr in rows.values()]
    tot = Counter()
    for c in pag:
        tot.update(c)
    N = float(sum(tot.values()))
    if N < 800:
        return None
    np_ = np.array([sum(c.values()) for c in pag], float)
    rap = []
    for w, c in tot.most_common(TOP_BURST):
        oss = sum(1 for p in pag if w in p)
        att = float(np.sum(1.0 - (1.0 - np_ / N) ** c))
        if att > 0:
            rap.append(oss / att)
    return float(np.mean(rap)) if rap else None


def _riga_cv(rows):
    l = [sum(len(w) for w in ws) + len(ws) - 1 for rr in rows.values() for _, ws in rr if ws]
    if len(l) < 30:
        return None
    return float(np.std(l) / np.mean(l))


def _sezione(rows):
    ch = chiavi_pagina()
    nomi = sorted(rows)
    tot = Counter(w for rr in rows.values() for _, ws in rr for w in ws)
    voc = [w for w, _ in tot.most_common(TOP_SEZ)]
    ix = {w: i for i, w in enumerate(voc)}
    M = np.zeros((len(nomi), len(voc)))
    for i, p in enumerate(nomi):
        for _, ws in rows[p]:
            for w in ws:
                j = ix.get(w)
                if j is not None:
                    M[i, j] += 1
    nr = np.linalg.norm(M, axis=1)
    ok = [i for i in range(len(nomi)) if nr[i] > 0 and nomi[i] in ch]
    if len(ok) < 10:
        return None
    M = M[ok] / nr[ok][:, None]
    k = [ch[nomi[i]] for i in ok]
    rnd = random.Random(3434)
    uguali, diverse = [], []
    n = len(ok)
    for _ in range(200000):
        a, b = rnd.randrange(n), rnd.randrange(n)
        if a == b:
            continue
        (uguali if k[a] == k[b] else diverse).append((a, b))
        if len(uguali) >= COPPIE_SEZ and len(diverse) >= COPPIE_SEZ:
            break
    if len(uguali) < 100 or len(diverse) < 100:
        return None
    cs = lambda L: float(np.mean([M[a] @ M[b] for a, b in L[:COPPIE_SEZ]]))
    return cs(uguali) - cs(diverse)


def _lag23(rows):
    righe = {p: [set(ws) for _, ws in rr if len(ws) >= 3] for p, rr in rows.items()}
    jac = lambda a, b: len(a & b) / max(len(a | b), 1)
    v = [jac(r[j], r[j + d]) for r in righe.values() for d in (2, 3) for j in range(len(r) - d)]
    if len(v) < 50:
        return None
    tutte = [(p, r) for p, rr in righe.items() for r in rr]
    rnd = random.Random(3435)
    z = []
    for _ in range(COPPIE_LAG * 3):
        (p1, r1), (p2, r2) = rnd.choice(tutte), rnd.choice(tutte)
        if p1 != p2:
            z.append(jac(r1, r2))
        if len(z) >= COPPIE_LAG:
            break
    return float(np.mean(v) - np.mean(z))


def _ini_par(rows):
    c = Counter(ws[0][0] for rr in rows.values() for ini, ws in rr if ini and ws and ws[0])
    n = sum(c.values())
    if n < 20:
        return None
    return float(-sum((v / n) * math.log2(v / n) for v in c.values()))


FUNZIONI = OrderedDict([('heaps', _heaps), ('burst', _burst), ('riga_cv', _riga_cv), ('sezione', _sezione), ('lag23', _lag23), ('ini_par', _ini_par)])


def misure_testo(rows, pagine=None):
    """Le sei misure su `rows`, solo sulle pagine `pagine` (se date e presenti). -> OrderedDict nome -> valore (None se il testo e' troppo corto)."""
    if pagine is not None:
        rows = OrderedDict((p, rows[p]) for p in pagine if p in rows)
    return OrderedDict((n, f(rows)) for n, f in FUNZIONI.items())


def riferimento_mondo(vere, dividi, divisioni=None):
    """Valore sul testo vero (`vere`: pagina -> righe, le pagine dei giudici) e scala (sd della differenza fra le due meta' di `divisioni` divisioni per fogli).
    `dividi(s)` -> (pagine della meta' 1, pagine della meta' 2) (`righello_banco.dividi_meta`). -> dict(vero, scala, sigma, divisioni)."""
    divisioni = S_NM34 if divisioni is None else divisioni
    vero = misure_testo(vere)
    diffs = {n: [] for n in NOMI_NM}
    for s in range(1, divisioni + 1):
        h1, h2 = dividi(s)
        a, b = misure_testo(vere, h1), misure_testo(vere, h2)
        for n in NOMI_NM:
            if a[n] is not None and b[n] is not None:
                diffs[n].append(a[n] - b[n])
    scala = OrderedDict((n, float(np.std(d, ddof=1)) if len(d) > 2 else None) for n, d in diffs.items())
    return OrderedDict([('vero', vero), ('scala', scala), ('sigma', OrderedDict((n, (v / math.sqrt(2.0) if v else None)) for n, v in scala.items())), ('divisioni', divisioni)])


if __name__ == '__main__':
    pass
