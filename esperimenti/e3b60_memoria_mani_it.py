# -*- coding: utf-8 -*-
"""Esperimento e3b60: memoria delle scelte oltre le parole per mano con la IT (mani della ZL), e per classe (ZL e IT).

Preregistrazione: preregistrazioni/e3b60.md. Scrive risultati/e3b60_memoria_mani_it.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b56_memoria_oltre_parole_corretta as e3b56

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MANI = ('1', '2', '3')


def per_mano(pagine_dict, mano):
    out = OrderedDict((h, []) for h in MANI)
    for pg, pars in pagine_dict.items():
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr and mano.get(pg) in out:
            out[mano[pg]].append(rr)
    return out


def main():
    rng = np.random.default_rng(3260)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cv = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])
    ris = OrderedDict()
    for tr, pagine in (('IT', e3b45.pagine_it()), ('ZL', e341.pagine())):
        pm = per_mano(pagine, mano)
        ris[tr] = OrderedDict()
        for h, pp in pm.items():
            ris[tr][h] = e3b54.prova(OrderedDict((k, e3b56.prepara(pp, f)) for k, f in cv.items()), rng)
            ris[tr][h]['insieme']['pagine'] = len(pp)
            print(tr, 'mano', h, json.dumps(ris[tr][h], ensure_ascii=False), flush=True)
    it = ris['IT']
    p1, p2, p3 = (it[h]['insieme']['p'] for h in MANI)
    if p1 > 0.05 and p2 < 0.05 and p3 < 0.05:
        esito = 'si ritrova con Takahashi'
    elif p1 < 0.01 or p2 > 0.20 or p3 > 0.20:
        esito = 'non si ritrova'
    else:
        esito = 'in parte'
    out = OrderedDict([('risultati', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b60_memoria_mani_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b60 — Memoria delle scelte per mano: Takahashi e classi', '', 'Preregistrazione: `preregistrazioni/e3b60.md`. Effetto = M osservata − M del nullo (metodo dell\'e3b56).', '',
          '| trascrizione | mano | pagine | coppie vicine | effetto insieme (z, p) | qo/o | k/t | sh/ch | -ey/-dy |', '|---|---|---|---|---|---|---|---|---|']
    f = lambda x: 'n.d.' if x['effetto'] is None else '%+.3f (p %.2f)' % (x['effetto'], x['p'])
    for tr in ('IT', 'ZL'):
        for h in MANI:
            r = ris[tr][h]
            x = r['insieme']
            md.append('| %s | %s | %d | %d | %+.4f (%+.1f, %.3f) | %s | %s | %s | %s |' % (tr, h, x['pagine'], x['coppie_vicine'], x['effetto'], x['z'], x['p'],
                                                                                    f(r['qo/o']), f(r['k/t']), f(r['sh/ch']), f(r['-ey/-dy'])))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b60_memoria_mani_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
