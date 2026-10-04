# -*- coding: utf-8 -*-
"""Esperimento e3b79: crescita di -ey scendendo nella pagina e apertura del paragrafo (e3a81) con ZL e IT, intervalli per
pagina.

Preregistrazione: preregistrazioni/e3b79.md. Scrive risultati/e3b79_verticali_takahashi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3a81_catena_pagina as e3a81
import e3b45_raccordo_a_capo as e3b45

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def a_segni(pagine_str):
    out = []
    for pars in pagine_str:
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp:
            out.append(pp)
    return out


def main():
    rnd = random.Random(3279)
    ris = OrderedDict()
    for q, pagine in (('ZL', a_segni(e341.pagine().values())), ('IT', a_segni(e3b45.pagine_it().values()))):
        vero = e3a81.proprieta(pagine)
        boot = {k: [] for k in vero}
        for _ in range(BOOT):
            b = e3a81.proprieta([pagine[rnd.randrange(len(pagine))] for _ in pagine])
            for k in vero:
                boot[k].append(b[k])
        x = OrderedDict()
        for k in vero:
            bb = sorted(boot[k])
            x[k] = OrderedDict([('valore', vero[k]), ('IC95', [bb[int(0.025 * BOOT)], bb[int(0.975 * BOOT) - 1]])])
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    es = OrderedDict()
    for k in ris['IT']:
        it, zl = ris['IT'][k]['IC95'], ris['ZL'][k]['IC95']
        es[k] = 'si ritrova con Takahashi' if it[0] > 0 and zl[0] > 0 else ('al contrario' if it[1] < 0 else 'non si ritrova')
    out = OrderedDict([('trascrizioni', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b79_verticali_takahashi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b79 — Crescita di -ey scendendo e apertura del paragrafo con Takahashi', '', 'Preregistrazione: `preregistrazioni/e3b79.md`. ZL nell\'e3a81: -ey +0,080; apertura +0,044.', '',
          '| proprietà | ZL (IC 95%) | IT (IC 95%) | esito |', '|---|---|---|---|']
    for k in ris['IT']:
        z, i = ris['ZL'][k], ris['IT'][k]
        md.append('| %s | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) | %s |' % (k, z['valore'], z['IC95'][0], z['IC95'][1], i['valore'], i['IC95'][0], i['IC95'][1], es[k]))
    open(os.path.join(RISULTATI, 'e3b79_verticali_takahashi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
