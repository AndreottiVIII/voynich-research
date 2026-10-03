# -*- coding: utf-8 -*-
"""Esperimento e3a18: deriva delle cinque scelte di grafia con l'altezza nella pagina (h) e la posizione nel paragrafo
(p); effetti fissi di pagina x posizione nella riga (x classe della vicina per qo-/o- e -l/-r); bootstrap sulle pagine.

Preregistrazione: preregistrazioni/e3a18.md. Scrive risultati/e3a18_derive.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380
import e3a17_ey_pagina_paragrafo as e3a17

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a', 'o', 'y'}


def scelte(w, prima, dopo):
    """[(nome, esito, classe della vicina)] per una parola."""
    out = []
    if w[0] in ('ch', 'sh') and len(w) >= 2:
        out.append(('sh fra ch/sh', w[0] == 'sh', None))
    for s in w:
        if s in ('k', 't'):
            out.append(('t fra k/t', s == 't', None))
    q = e380.ini_qo(w)
    if q:
        cl = None if not prima else ('V' if prima[-1] in V else ('C' if prima[-1] in C else 'X'))
        out.append(('qo fra qo/o', q[1] == 'qo', cl))
    f = e380.fin_lr(w)
    if f:
        cl = None if not dopo else ('K' if dopo[0] in K else ('A' if dopo[0] in A else 'X'))
        out.append(('-r fra -l/-r', f[1] == 'r', cl))
    if len(w) >= 3 and w[-1] == 'y' and w[-2] in ('d', 'e'):
        out.append(('-ey fra -dy/-ey', w[-2] == 'e', None))
    return out


def main():
    rnd = random.Random(3118)
    nomi = ['sh fra ch/sh', 't fra k/t', 'qo fra qo/o', '-r fra -l/-r', '-ey fra -dy/-ey']
    blocchi = {n: [] for n in nomi}
    for pag, pars in e341.pagine().items():
        n_righe = sum(len(p) for p in pars)
        if len(pars) < 2 or n_righe < 8:
            continue
        b = {n: [] for n in nomi}
        i = 0
        for par in pars:
            m = len(par)
            for k, r in enumerate(par):
                h = i / (n_righe - 1)
                p = k / (m - 1) if m > 1 else 0.0
                ws = [w for w in (tuple(D(x)) for x in r) if w]
                n = len(ws)
                for j, w in enumerate(ws):
                    pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                    for nome, y, cl in scelte(w, ws[j - 1] if j > 0 else None, ws[j + 1] if j < n - 1 else None):
                        b[nome].append(((pag, pos, cl), float(y), h, p))
                i += 1
        for nome in nomi:
            if b[nome]:
                blocchi[nome].append(b[nome])
    ris = OrderedDict()
    for nome in nomi:
        bl = blocchi[nome]
        coef = e3a17.stima(bl)
        boot = np.array([e3a17.stima([bl[rnd.randrange(len(bl))] for _ in bl]) for _ in range(2000)])
        ic = np.percentile(boot, [0.25, 99.75], axis=0)
        x = OrderedDict([('pagine', len(bl)), ('eventi', sum(len(b) for b in bl))])
        for k, fatt in enumerate(('altezza nella pagina', 'posizione nel paragrafo')):
            lo, hi = ic[0, k], ic[1, k]
            es = ('deriva (cresce)' if lo > 0 else ('deriva (cala)' if hi < 0 else 'nessuna deriva dimostrata'))
            x[fatt] = OrderedDict([('coef', float(coef[k])), ('IC995', [float(lo), float(hi)]), ('esito', es)])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a18_derive.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a18 — Le cinque scelte di grafia derivano scendendo nella pagina e nel paragrafo?', '', 'Preregistrazione: `preregistrazioni/e3a18.md`. Coefficienti da cima a fondo; intervalli al 99,5%.', '',
          '| scelta | eventi | altezza nella pagina | IC 99,5% | esito | posizione nel paragrafo | IC 99,5% | esito |', '|---|---|---|---|---|---|---|---|']
    for nome, x in ris.items():
        a, p = x['altezza nella pagina'], x['posizione nel paragrafo']
        md.append('| %s | %d | %+.3f | %+.3f – %+.3f | %s | %+.3f | %+.3f – %+.3f | %s |' % (nome, x['eventi'], a['coef'], a['IC995'][0], a['IC995'][1], a['esito'], p['coef'], p['IC995'][0], p['IC995'][1], p['esito']))
    open(os.path.join(RISULTATI, 'e3a18_derive.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
