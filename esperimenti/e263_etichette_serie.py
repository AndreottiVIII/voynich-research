# -*- coding: utf-8 -*-
"""Esperimento 263: etichette consecutive sulla stessa pagina sono varianti a una modifica (M1)? E la modifica si ripete
lungo la serie (M2)?

Preregistrazione: preregistrazioni/e263.md. Scrive risultati/e263_etichette_serie.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237
import e239_operatore_variante as e239
import e259_bit_per_parola as e259

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, MINIMO = 263, 1000, 5
D = e237.D


def pagine():
    per = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo and r.tipo.startswith('L'):
            w = ''.join(x for x in r.parole if trascrizione.pulita(x))
            if w:
                per.setdefault(r.pagina, []).append(tuple(D(w)))
    return OrderedDict((p, v) for p, v in per.items() if len(v) >= MINIMO)


def misure_serie(seqs):
    n1 = d1 = n2 = d2 = 0
    for v in seqs:
        ops = []
        for a, b in zip(v, v[1:]):
            n1 += 1
            if e259.dist1(a, b):
                d1 += 1
                ops.append(e239.operazione(a, b)[1])
            else:
                ops.append(None)
        for o1, o2 in zip(ops, ops[1:]):
            if o1 is not None and o2 is not None:
                n2 += 1
                d2 += o1 == o2
    return d1 / n1, (d2 / n2 if n2 else 0.0), n2


def main():
    rnd = random.Random(SEME)
    P = pagine()
    seqs = list(P.values())
    m1, m2, n2 = misure_serie(seqs)
    nulli1, nulli2 = [], []
    for _ in range(PERMUTAZIONI):
        mesc = [rnd.sample(v, len(v)) for v in seqs]
        a, b, _ = misure_serie(mesc)
        nulli1.append(a)
        nulli2.append(b)
    z = lambda x, xs: (x - statistics.mean(xs)) / statistics.pstdev(xs) if statistics.pstdev(xs) else None
    z1, z2 = z(m1, nulli1), z(m2, nulli2)
    esito = ('etichette in serie' if (z1 or 0) > 3 and (z2 or 0) > 3 else 'etichette vicine simili ma senza serie' if (z1 or 0) > 3 else 'nessun ordine')
    ris = OrderedDict([('pagine', len(P)), ('etichette', sum(map(len, seqs))), ('M1', OrderedDict([('quota', m1), ('nullo', statistics.mean(nulli1)), ('z', z1)])),
                       ('M2', OrderedDict([('coppie_di_coppie', n2), ('quota', m2), ('nullo', statistics.mean(nulli2)), ('z', z2)])), ('esito', esito)])
    print(json.dumps(ris, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e263_etichette_serie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e263 — Le etichette di una pagina formano una serie?', '',
          'Etichette (loci L) nell\'ordine della ZL: %d su %d pagine. Nullo: %d rimescolamenti dell\'ordine nella pagina. Preregistrazione: '
          '`preregistrazioni/e263.md`.' % (ris['etichette'], len(P), PERMUTAZIONI), '', '| misura | vera | nulla | z |', '|---|---|---|---|',
          '| M1: consecutive a distanza 1 | %.3f | %.3f | %.1f |' % (m1, statistics.mean(nulli1), z1 or 0),
          '| M2: stessa modifica lungo la serie (%d casi) | %.3f | %.3f | %.1f |' % (n2, m2, statistics.mean(nulli2), z2 or 0), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e263_etichette_serie.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
