# -*- coding: utf-8 -*-
"""Esperimento e3a81: apertura del paragrafo (p/f nella prima riga) e -ey che cresce scendendo nella pagina, nel Voynich
vero e riscritto riga per riga dalla catena di ordine 2 (come e3a78).

Preregistrazione: preregistrazioni/e3a81.md. Scrive risultati/e3a81_catena_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NOMI = ('apertura del paragrafo (p/f)', '-ey scendendo nella pagina')


def proprieta(pagine):
    prima = altre = None
    pf = [0, 0]
    pa = [0, 0]
    for pars in pagine:
        for par in pars:
            for i, r in enumerate(par):
                t = pf if i == 0 else pa
                for w in r:
                    for s in w:
                        t[0] += ('p' in s or 'f' in s)
                        t[1] += 1
    apertura = pf[0] / pf[1] - pa[0] / pa[1]
    alto, basso = [0, 0], [0, 0]
    for pars in pagine:
        righe = [r for par in pars for r in par]
        if len(righe) < 6:
            continue
        meta = len(righe) / 2
        for i, r in enumerate(righe):
            t = alto if i < meta else basso
            for w in r:
                s = ''.join(w)
                if s.endswith('ey') or s.endswith('dy'):
                    t[0] += s.endswith('ey')
                    t[1] += 1
    ey = basso[0] / basso[1] - alto[0] / alto[1]
    return OrderedDict([(NOMI[0], apertura), (NOMI[1], ey)])


def main():
    rnd = random.Random(3181)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append([par for par in pp if par])
    vero = proprieta(pagine)
    print('vero', json.dumps(vero, ensure_ascii=False), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    risc = [proprieta(e3a78.riscrivi(pagine, tab, rnd)) for _ in range(e3a78.RISCRITTURE)]
    sintesi = OrderedDict()
    for n in NOMI:
        rv = statistics.mean(x[n] for x in risc)
        R = rv / vero[n] if vero[n] else None
        es = 'n.d.' if R is None else ('la catena la riproduce' if R >= 0.75 else ('in parte' if R >= 0.25 else 'serve un meccanismo in più'))
        sintesi[n] = OrderedDict([('vero', vero[n]), ('riscritto', [x[n] for x in risc]), ('riscritto_media', rv), ('R', R), ('esito', es)])
    print(json.dumps(sintesi, ensure_ascii=False, indent=1), flush=True)
    json.dump(OrderedDict([('sintesi', sintesi)]), open(os.path.join(RISULTATI, 'e3a81_catena_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a81 — La catena per riga spiega l\'apertura del paragrafo e -ey che cresce scendendo nella pagina?', '', 'Preregistrazione: `preregistrazioni/e3a81.md`.', '',
          '| proprietà | Voynich vero | riscritto (media) | R | esito |', '|---|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %s | %s |' % (n, x['vero'], x['riscritto_media'], '%.2f' % x['R'] if x['R'] is not None else 'n.d.', x['esito']) for n, x in sintesi.items()]
    open(os.path.join(RISULTATI, 'e3a81_catena_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
