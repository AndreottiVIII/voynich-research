# -*- coding: utf-8 -*-
"""Esperimento 262: le etichette dello zodiaco nella stessa posizione di segni diversi si somigliano piu' di quelle in
posizioni diverse? (a) allineamento per indice, (b) al miglior spostamento ciclico per coppia di segni.

Preregistrazione: preregistrazioni/e262.md. Scrive risultati/e262_zodiaco_ordinale.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from itertools import combinations

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEME, PERMUTAZIONI, LUNGHEZZA = 262, 1000, 30
UNIONI = [('f70v1', 'f71r'), ('f71v', 'f72r1')]


def sequenze():
    per = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo == 'Lz':
            w = ''.join(r.parole)
            if w:
                per.setdefault(r.pagina, []).append(w)
    out = OrderedDict()
    usate = set()
    for a, b in UNIONI:
        if a in per and b in per:
            out[a + '+' + b] = per[a] + per[b]
            usate |= {a, b}
    for p, v in per.items():
        if p not in usate:
            out[p] = v
    return OrderedDict((k, v[:LUNGHEZZA]) for k, v in out.items() if len(v) >= 25)


def matrice(a, b):
    return np.array([[1 - misure._dist_norm(tuple(D(x)), tuple(D(y))) for y in b] for x in a])


def delta(mats, ciclico):
    s_same, s_diff = [], []
    for M in mats:
        n = min(M.shape)
        M = M[:n, :n]
        if ciclico:
            best = max(range(n), key=lambda s: np.mean([M[i, (i + s) % n] for i in range(n)]))
            idx = [(i, (i + best) % n) for i in range(n)]
        else:
            idx = [(i, i) for i in range(n)]
        same = np.mean([M[i, j] for i, j in idx])
        diff = (M.sum() - sum(M[i, j] for i, j in idx)) / (n * n - n)
        s_same.append(same)
        s_diff.append(diff)
    return float(np.mean(s_same) - np.mean(s_diff))


def main():
    rnd = random.Random(SEME)
    seq = sequenze()
    nomi = list(seq)
    coppie = list(combinations(nomi, 2))
    base = {(a, b): matrice(seq[a], seq[b]) for a, b in coppie}
    ris = OrderedDict([('sequenze', {k: len(v) for k, v in seq.items()})])
    for nome, cic in (('indice', False), ('spostamento ciclico', True)):
        vero = delta([base[c] for c in coppie], cic)
        nulli = []
        for _ in range(PERMUTAZIONI):
            perm = {k: rnd.sample(range(len(v)), len(v)) for k, v in seq.items()}
            mats = [base[(a, b)][np.ix_(perm[a], perm[b])] for a, b in coppie]
            nulli.append(delta(mats, cic))
        mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        ris[nome] = OrderedDict([('delta', vero), ('nullo', mu), ('z', (vero - mu) / sd if sd else None)])
        print(nome, dict(ris[nome]), flush=True)
    za, zb = ris['indice']['z'] or 0, ris['spostamento ciclico']['z'] or 0
    ris['esito'] = 'etichette ordinali' if max(za, zb) > 3 else ('nessun ordine comune' if max(za, zb) <= 2 else 'incerto')
    json.dump(ris, open(os.path.join(RISULTATI, 'e262_zodiaco_ordinale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e262 — Le etichette dello zodiaco sono ordinali?', '',
          'Sequenze di etichette Lz (Ariete e Toro uniti dalle due metà): %s. Δ = somiglianza fra etichette della stessa posizione in segni diversi '
          'meno quella fra posizioni diverse; nullo: %d permutazioni dentro ogni sequenza. Preregistrazione: `preregistrazioni/e262.md`.' % (
              ', '.join('%s (%d)' % kv for kv in ris['sequenze'].items()), PERMUTAZIONI), '',
          '| allineamento | Δ | nullo | z |', '|---|---|---|---|']
    for nome in ('indice', 'spostamento ciclico'):
        r = ris[nome]
        md.append('| %s | %+.4f | %+.4f | %.1f |' % (nome, r['delta'], r['nullo'], r['z'] or 0))
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e262_zodiaco_ordinale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
