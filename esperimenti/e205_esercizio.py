# -*- coding: utf-8 -*-
"""Esperimento 205: l'irregolarita' della larghezza delle parole (rispetto all'attesa dalla composizione) diminuisce
lungo il manoscritto dentro ogni mano?

Preregistrazione: preregistrazioni/e205.md. Scrive risultati/e205_esercizio.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import OrderedDict, defaultdict

import numpy as np
from scipy.optimize import nnls

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e148_bifogli as e148
import e173_dimensione_scrittura as e173
import e177_dimensione_corretta as e177

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 205, 2000
D = e177.D


def main():
    rnd = random.Random(SEME)
    righe, pp = e177.parole_allineate()
    unita = sorted({u for _, _, w, _ in pp for u in D(w)})
    idx = {u: i for i, u in enumerate(unita)}
    A = np.zeros((len(pp), len(unita) + 1))
    b = np.zeros(len(pp))
    for r, (_, _, w, l) in enumerate(pp):
        for u in D(w):
            A[r, idx[u]] += 1
        A[r, -1] = 1
        b[r] = l
    coef, _ = nnls(A, b)
    att = A @ coef
    per_riga = defaultdict(list)
    for (pag, k, _, l), a in zip(pp, att):
        if a > 0 and l > 0:
            per_riga[(pag, k)].append(math.log(l / a))
    per_pag = defaultdict(list)
    for (pag, k), v in per_riga.items():
        if len(v) >= 4:
            m = statistics.median(v)
            per_pag[pag].append(statistics.median(abs(x - m) for x in v))
    ordine = []
    for pag, _, _ in righe:
        if pag not in ordine:
            ordine.append(pag)
    var = e148.variabili_pagine()
    mani = defaultdict(list)
    for i, pag in enumerate(ordine):
        if len(per_pag.get(pag, [])) >= 8 and pag in var and var[pag].get('H'):
            mani[var[pag]['H']].append((i, statistics.mean(per_pag[pag])))
    mani = {h: v for h, v in mani.items() if len(v) >= 10}

    def stat(mm):
        num = den = 0.0
        for v in mm.values():
            num += len(v) * e173.spearman([i for i, _ in v], [x for _, x in v])
            den += len(v)
        return num / den
    vero = stat(mani)
    nulli = []
    for _ in range(PERMUTAZIONI):
        mm = {}
        for h, v in mani.items():
            x = [y for _, y in v]
            rnd.shuffle(x)
            mm[h] = [(i, y) for (i, _), y in zip(v, x)]
        nulli.append(stat(mm))
    p = (1 + sum(n <= vero for n in nulli)) / (1 + PERMUTAZIONI)
    per_mano = {h: OrderedDict([('pagine', len(v)), ('spearman', e173.spearman([i for i, _ in v], [x for _, x in v]))]) for h, v in sorted(mani.items())}
    esito = 'miglioramento (esercizio)' if vero < 0 and p < 0.01 else ('nessun miglioramento' if p > 0.05 else 'incerto')
    ris = OrderedDict([('per_mano', per_mano), ('statistica', vero), ('nullo_media', statistics.mean(nulli)), ('p_una_coda', p), ('esito', esito)])
    print('per mano %s | statistica %.3f (nullo %.3f) p %.4f | %s' % ({h: (x['pagine'], round(x['spearman'], 3)) for h, x in per_mano.items()}, vero, statistics.mean(nulli), p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e205_esercizio.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=float)
    out = ['# e205 — La scrittura diventa più regolare lungo il manoscritto?', '', 'Irregolarità della larghezza delle parole (rispetto alla composizione) contro l\'ordine di rilegatura, '
           'dentro ogni mano. Preregistrazione: `preregistrazioni/e205.md`.', '', '| mano | pagine | Spearman |', '|---|---|---|']
    out += ['| %s | %d | %.3f |' % (h, x['pagine'], x['spearman']) for h, x in per_mano.items()]
    out += ['', 'Statistica pesata %.3f (nullo %.3f), p %.4f. Esito: **%s**.' % (vero, statistics.mean(nulli), p, esito)]
    with open(os.path.join(RISULTATI, 'e205_esercizio.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
