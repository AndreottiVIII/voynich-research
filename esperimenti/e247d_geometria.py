# -*- coding: utf-8 -*-
"""Esperimento 247d: la correlazione fra scarti consecutivi (coppie non a passo 0 o +1) supera un nullo che conserva le
posizioni e la riga sopra e cambia solo le parole della riga (prese da altre righe della stessa pagina)?

Preregistrazione: preregistrazioni/e247d.md. Scrive risultati/e247d_geometria.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e228_verticale_fisica as e228
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 2473, 200
D = e237.D
_VIC = {}


def vicini(u, inventario):
    if u not in _VIC:
        _VIC[u] = e237.vicini(u, inventario) | {u}
    return _VIC[u]


def correlazione(pagine, inventario):
    a, b = [], []
    for p, rr in pagine.items():
        passi = [y[1] - x[1] for r in rr for x, y in zip(r, r[1:]) if x[1] is not None and y[1] is not None and y[1] > x[1]]
        if len(passi) < 10:
            continue
        unita = statistics.median(passi)
        for k in range(1, len(rr)):
            sopra = [(w, c) for w, c in rr[k - 1] if c is not None and trascrizione.pulita(w)]
            if len(sopra) < 2:
                continue
            su = [tuple(D(w)) for w, _ in sopra]
            v = []
            for j in range(1, len(rr[k]) - 1):
                w, c = rr[k][j]
                if c is None or not trascrizione.pulita(w):
                    continue
                vic = vicini(tuple(D(w)), inventario)
                fonti = [t for t, ux in enumerate(su) if ux in vic]
                if fonti:
                    t = min(fonti, key=lambda t: abs(sopra[t][1] - c))
                    v.append((j, t, (c - sopra[t][1]) / unita))
            for x, y in zip(v, v[1:]):
                if y[0] == x[0] + 1 and (y[1] - x[1]) not in (0, 1):
                    a.append(x[2])
                    b.append(y[2])
    return (float(np.corrcoef(a, b)[0, 1]) if len(a) > 10 else None), len(a)


def main():
    rnd = random.Random(SEME)
    pagine = e228.righe_con_riquadri()
    tutte = Counter(w for rr in pagine.values() for r in rr for w, _ in r if trascrizione.pulita(w))
    inventario = sorted({x for w in tutte for x in D(w)})
    vera, n = correlazione(pagine, inventario)
    nulli = []
    for i in range(REPLICHE):
        nuove = OrderedDict()
        for p, rr in pagine.items():
            nr = [list(rr[0])]
            for k in range(1, len(rr)):
                altre = [w for kk, r in enumerate(rr) if kk not in (k, k - 1) for w, _ in r if trascrizione.pulita(w)]
                if not altre:
                    nr.append(list(rr[k]))
                    continue
                nr.append([(rnd.choice(altre) if trascrizione.pulita(w) else w, c) for w, c in rr[k]])
            nuove[p] = nr
        nulli.append(correlazione(nuove, inventario)[0])
        if i % 50 == 49:
            print('repliche %d' % (i + 1), flush=True)
    mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    z = (vera - mu) / sd if sd else None
    esito = 'geometria' if abs(z) <= 2 else ('struttura nella scelta, da esaminare' if z > 3 else 'incerto')
    ris = OrderedDict([('coppie', n), ('correlazione', vera), ('nullo_geometrico', mu), ('sd', sd), ('z', z), ('esito', esito)])
    print(dict(ris), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e247d_geometria.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e247d — La correlazione degli scarti viene dalla geometria della riga sopra?', '',
          'Coppie consecutive non a passo 0 o +1: %d. Nullo geometrico: le parole di ogni riga sostituite con parole di altre righe della stessa '
          'pagina, posizioni e riga sopra invariate; %d repliche. Preregistrazione: `preregistrazioni/e247d.md`.' % (n, REPLICHE), '',
          '| correlazione | nullo geometrico | z |', '|---|---|---|', '| %.3f | %.3f | %.1f |' % (vera, mu, z or 0), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e247d_geometria.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
