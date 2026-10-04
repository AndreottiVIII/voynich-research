# -*- coding: utf-8 -*-
"""Esperimento e3c52: in EVA (ZL e IT), la finestra scelta per scelta (qo/o, k/t, sh/ch, -ey/-dy) con la misura corretta
dell'e3c48 (K osservato − K con le scelte rimescolate fra le occorrenze della stessa parola coperta).

Preregistrazione: preregistrazioni/e3c52.md. Scrive risultati/e3c52_eva_per_scelta.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c48_finestra_corretta as e3c48
import e3c50_scribi_menota as e3c50

RISULTATI = os.path.join(QUI, '..', 'risultati')


def voce(x):
    vicine, finestra = e3c50.giudizio(x)
    if finestra:
        return 'finestra'
    if vicine:
        return 'accordo fra vicine senza finestra'
    if x['K23_IC95'][0] > 0.02:
        return 'accordo solo a 2–3 parole'
    return 'nessun accordo chiaro'


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3352)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        for k, f in e3b62.CV.items():
            x = e3c48.misura(pagine, OrderedDict([(k, f)]), rng)
            x['voce'] = voce(x)
            ris['%s %s' % (q, k)] = x
            print(q, k, json.dumps(x, ensure_ascii=False), flush=True)
    esiti = OrderedDict()
    for k in e3b62.CV:
        a, b = ris['ZL ' + k]['voce'], ris['IT ' + k]['voce']
        esiti[k] = ('replicato in ZL e IT: ' + a) if a == b else ('ZL: %s; IT: %s' % (a, b))
    out = OrderedDict([('misure', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c52_eva_per_scelta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c52 — In EVA, scelta per scelta, con la misura corretta', '', 'Preregistrazione: `preregistrazioni/e3c52.md`.', '',
          '| trascrizione e scelta | parole | K osservato 1/2/3 | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) | voce |',
          '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s |' % (
            k, x['parole'], ' '.join('%+.3f' % z for z in x['K_osservato']), ' '.join('%+.3f' % z for z in x['K_nullo']),
            x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1],
            x['r'], x['r_IC95'][0], x['r_IC95'][1], x['voce']))
    md += [''] + ['- %s: **%s**' % kv for kv in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c52_eva_per_scelta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
