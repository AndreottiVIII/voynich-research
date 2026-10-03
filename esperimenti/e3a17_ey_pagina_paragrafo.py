# -*- coding: utf-8 -*-
"""Esperimento e3a17: la quota di -ey dipende dall'altezza della riga nella pagina (h) o dalla sua posizione nel
paragrafo (p)? Regressione con effetti fissi di pagina x posizione nella riga; bootstrap sulle pagine.

Preregistrazione: preregistrazioni/e3a17.md. Scrive risultati/e3a17_ey_pagina_paragrafo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def stima(blocchi):
    """blocchi: liste di (cella, y, h, p) per pagina -> coefficienti di h e p su variabili tolte della media per cella."""
    per = defaultdict(list)
    for b in blocchi:
        for c, y, h, p in b:
            per[c].append((y, h, p))
    Y, X = [], []
    for xs in per.values():
        if len(xs) < 2:
            continue
        a = np.array(xs, float)
        a -= a.mean(0)
        Y.append(a[:, 0])
        X.append(a[:, 1:])
    Y = np.concatenate(Y)
    X = np.vstack(X)
    coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return coef


def main():
    rnd = random.Random(3117)
    blocchi = []
    for pag, pars in e341.pagine().items():
        n_righe = sum(len(p) for p in pars)
        if len(pars) < 2 or n_righe < 8:
            continue
        b, i = [], 0
        for par in pars:
            m = len(par)
            for k, r in enumerate(par):
                h = i / (n_righe - 1)
                p = k / (m - 1) if m > 1 else 0.0
                ws = [tuple(D(w)) for w in r]
                n = len(ws)
                for j, w in enumerate(ws):
                    if len(w) >= 2 and w[-1] == 'y' and w[-2] in ('d', 'e'):
                        pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                        b.append(((pag, pos), float(w[-2] == 'e'), h, p))
                i += 1
        if b:
            blocchi.append(b)
    coef = stima(blocchi)
    boot = np.array([stima([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi]) for _ in range(2000)])
    ic = np.percentile(boot, [2.5, 97.5], axis=0)
    hs, ps = ic[0, 0] > 0, ic[0, 1] > 0
    h0, p0 = ic[0, 0] <= 0 <= ic[1, 0], ic[0, 1] <= 0 <= ic[1, 1]
    if hs and p0:
        esito = 'altezza nella pagina'
    elif ps and h0:
        esito = 'posizione nel paragrafo'
    elif hs and ps:
        esito = 'tutte e due'
    else:
        esito = 'nessuna delle due separabile'
    out = OrderedDict([('pagine', len(blocchi)), ('parole', sum(len(b) for b in blocchi)), ('coef_h', float(coef[0])), ('IC95_h', ic[:, 0].tolist()),
                       ('coef_p', float(coef[1])), ('IC95_p', ic[:, 1].tolist()), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a17_ey_pagina_paragrafo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a17 — -ey cresce con l\'altezza nella pagina o con la posizione nel paragrafo?', '', 'Preregistrazione: `preregistrazioni/e3a17.md`.', '',
          '%d pagine con più paragrafi, %d parole in -dy/-ey.' % (out['pagine'], out['parole']), '',
          '| fattore | coefficiente (da cima a fondo) | IC 95% |', '|---|---|---|',
          '| altezza nella pagina (h) | %+.3f | %+.3f – %+.3f |' % (coef[0], ic[0, 0], ic[1, 0]),
          '| posizione nel paragrafo (p) | %+.3f | %+.3f – %+.3f |' % (coef[1], ic[0, 1], ic[1, 1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a17_ey_pagina_paragrafo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
