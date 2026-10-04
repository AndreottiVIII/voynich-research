# -*- coding: utf-8 -*-
"""Esperimento e3c35 (descrittivo): R0 = K(3)/K(1) dell'e3c34 scelta per scelta: qo/o, k/t, sh/ch, -ey/-dy (a mano) e a/o,
ch/e (automatiche dell'e3c01). Voynich ZL e IT.

Preregistrazione: preregistrazioni/e3c35.md. Scrive risultati/e3c35_finestra_per_scelta.json e .md.
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
import e3c01_alternanze_interne as e3c01
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3335)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    classi = OrderedDict(e3b62.CV)
    classi['a/o (automatica)'] = e3c01.classe('a', 'o')
    classi['ch/e (automatica)'] = e3c01.classe('ch', 'e')
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        for k, f in classi.items():
            ris['%s, %s' % (q, k)] = e3c34.misura(pagine, OrderedDict([(k, f)]), rng)
            print(q, k, json.dumps(ris['%s, %s' % (q, k)]), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c35_finestra_per_scelta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c35 — La finestra di tre parole scelta per scelta (descrittivo)', '', 'Preregistrazione: `preregistrazioni/e3c35.md`. Misura dell\'e3c34 (righe di almeno 6 parole senza bordi; atteso stessa parola + pagina + deriva).', '',
          '| trascrizione, scelta | parole | K(1) (IC 95%) | K(2) | K(3) | R0 (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f (%.2f – %.2f) |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['R0'], x['R0_IC95'][0], x['R0_IC95'][1]))
    open(os.path.join(RISULTATI, 'e3c35_finestra_per_scelta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
