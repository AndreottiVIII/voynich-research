# -*- coding: utf-8 -*-
"""Esperimento e3a20: e3a18 (derive delle scelte di grafia) senza la prima riga di ogni paragrafo e della pagina; e3a19
(copia per terzo del paragrafo) con le sole righe i >= 2.

Preregistrazione: preregistrazioni/e3a20.md. Scrive risultati/e3a20_senza_apertura.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385
import e3a17_ey_pagina_paragrafo as e3a17
import e3a18_derive as e3a18
import e3a19_copia_paragrafo as e3a19

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NOMI = ['sh fra ch/sh', 't fra k/t', 'qo fra qo/o', '-r fra -l/-r', '-ey fra -dy/-ey']


def parte_a(rnd):
    blocchi = {n: [] for n in NOMI}
    for pag, pars in e341.pagine().items():
        n_righe = sum(len(p) for p in pars)
        if len(pars) < 2 or n_righe < 8:
            continue
        b = {n: [] for n in NOMI}
        i = 0
        for par in pars:
            m = len(par)
            for k, r in enumerate(par):
                h = i / (n_righe - 1)
                p = k / (m - 1) if m > 1 else 0.0
                i += 1
                if k == 0 or i == 1:
                    continue
                ws = [w for w in (tuple(D(x)) for x in r) if w]
                n = len(ws)
                for j, w in enumerate(ws):
                    pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                    for nome, y, cl in e3a18.scelte(w, ws[j - 1] if j > 0 else None, ws[j + 1] if j < n - 1 else None):
                        b[nome].append(((pag, pos, cl), float(y), h, p))
        for nome in NOMI:
            if b[nome]:
                blocchi[nome].append(b[nome])
    ris = OrderedDict()
    for nome in NOMI:
        bl = blocchi[nome]
        coef = e3a17.stima(bl)
        boot = np.array([e3a17.stima([bl[rnd.randrange(len(bl))] for _ in bl]) for _ in range(2000)])
        ic = np.percentile(boot, [0.25, 99.75], axis=0)
        x = OrderedDict([('eventi', sum(len(b) for b in bl))])
        for k, fatt in enumerate(('altezza nella pagina', 'posizione nel paragrafo')):
            lo, hi = ic[0, k], ic[1, k]
            x[fatt] = OrderedDict([('coef', float(coef[k])), ('IC995', [float(lo), float(hi)]),
                                   ('esito', 'deriva (cresce)' if lo > 0 else ('deriva (cala)' if hi < 0 else 'nessuna deriva dimostrata'))])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    return ris


def parte_b(rnd):
    pars = []
    for pars_p in e341.pagine().values():
        for par in pars_p:
            n = len(par)
            if n < 6:
                continue
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            sim = e385.simili_unita(rr)
            insiemi = [set(r) for r in rr]
            bers = [[w for w in r if len(w) >= 3] for r in rr]
            out = []
            for i in range(2, n):
                if not bers[i]:
                    continue
                colpi = [sum(1 for w in bers[i] if sim[w] & insiemi[j]) if j != i else 0 for j in range(n)]
                t = min(2, int(3 * i / (n - 1)))
                out.append((t, colpi[i - 1], sum(colpi) / (n - 1), len(bers[i])))
            pars.append(out)
    e = e3a19.eccessi(pars)
    boot = sorted((lambda x: x[2] - x[0])(e3a19.eccessi([pars[rnd.randrange(len(pars))] for _ in pars])) for _ in range(2000))
    ic = [boot[50], boot[1949]]
    esito = 'la copia cresce lungo il paragrafo anche senza l\'apertura' if ic[0] > 0 else ('cala' if ic[1] < 0 else 'costante')
    return OrderedDict([('paragrafi', len(pars)), ('eccesso_inizio_mezzo_fine', e), ('differenza', e[2] - e[0]), ('IC95', ic), ('esito', esito)])


def main():
    rnd = random.Random(3120)
    A = parte_a(rnd)
    B = parte_b(rnd)
    print('B', json.dumps(B, ensure_ascii=False), flush=True)
    out = OrderedDict([('parte_A', A), ('parte_B', B)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a20_senza_apertura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a20 — Derive e copia lungo il paragrafo senza le righe d\'apertura', '', 'Preregistrazione: `preregistrazioni/e3a20.md`.', '',
          '## Parte A: derive senza la prima riga dei paragrafi e della pagina (IC 99,5%)', '',
          '| scelta | eventi | altezza nella pagina | IC | esito | posizione nel paragrafo | IC | esito |', '|---|---|---|---|---|---|---|---|']
    for nome, x in A.items():
        a, p = x['altezza nella pagina'], x['posizione nel paragrafo']
        md.append('| %s | %d | %+.3f | %+.3f – %+.3f | %s | %+.3f | %+.3f – %+.3f | %s |' % (nome, x['eventi'], a['coef'], a['IC995'][0], a['IC995'][1], a['esito'], p['coef'], p['IC995'][0], p['IC995'][1], p['esito']))
    e = B['eccesso_inizio_mezzo_fine']
    md += ['', '## Parte B: copia dalla riga sopra, righe i ≥ 2', '',
           '%d paragrafi con almeno 6 righe. Inizio %+.4f, mezzo %+.4f, fine %+.4f; fine − inizio %+.4f (IC 95%% %+.4f – %+.4f). Esito: **%s**.' % (B['paragrafi'], e[0], e[1], e[2], B['differenza'], B['IC95'][0], B['IC95'][1], B['esito'])]
    open(os.path.join(RISULTATI, 'e3a20_senza_apertura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
