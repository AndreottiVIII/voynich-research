# -*- coding: utf-8 -*-
"""Esperimento e3a10: il legame dell'identita' della parola oltre il segno di bordo (e3a08), condizionando a 1, 2, 3
segni di bordo, e senza le parole corte.

Preregistrazione: preregistrazioni/e3a10.md. Scrive risultati/e3a10_resto.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3110)
    voy = e380.voynich()
    coppie = [(st, a, b) for st, par in voy for r in par for a, b in zip(r, r[1:])]
    ris = OrderedDict()
    for lato in ('avanti', 'indietro'):
        x = OrderedDict()
        for k in (1, 2, 3):
            if lato == 'avanti':
                ev = [((st, a[-k:]), a, b[0]) for st, a, b in coppie]
            else:
                ev = [((st, b[:k]), b, a[-1]) for st, a, b in coppie]
            x['k=%d' % k] = e380.prova(ev, rnd, 1000)
        lunghe = [(st, a, b) for st, a, b in coppie if len(a) >= 3 and len(b) >= 3]
        if lato == 'avanti':
            ev = [((st, a[-1:]), a, b[0]) for st, a, b in lunghe]
        else:
            ev = [((st, b[:1]), b, a[-1]) for st, a, b in lunghe]
        x['k=1, senza parole corte'] = e380.prova(ev, rnd, 1000)
        e1 = x['k=1']['E']
        es = []
        if x['k=2']['E'] < 0.5 * e1:
            es.append('il resto sta nei segni subito vicini al bordo')
        if x['k=1, senza parole corte']['E'] < 0.5 * e1:
            es.append('il resto sta nelle parole corte')
        x['esito'] = '; '.join(es) if es else 'il resto è sparso nella parola'
        ris[lato] = x
        print(lato, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a10_resto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a10 — Dove sta il piccolo legame che resta oltre il segno di bordo?', '', 'Preregistrazione: `preregistrazioni/e3a10.md`.', '',
          '| direzione | condizione | coppie | E | z |', '|---|---|---|---|---|']
    for lato, x in ris.items():
        for k, v in x.items():
            if k != 'esito':
                md.append('| %s | %s | %d | %.4f | %.1f |' % (lato, k, v['eventi'], v['E'], v['z']))
    md += ['', 'Esito avanti: **%s**. Esito indietro: **%s**.' % (ris['avanti']['esito'], ris['indietro']['esito'])]
    open(os.path.join(RISULTATI, 'e3a10_resto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
