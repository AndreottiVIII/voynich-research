# -*- coding: utf-8 -*-
"""Esperimento e3c36: la "finestra" di k/t, sh/ch, -ey/-dy (e3c35) c'è sia nelle pagine della lingua A sia in quelle della
lingua B (scribi e pagine diversi)? Misura dell'e3c34 (righe di almeno 6 parole senza bordi; atteso stessa parola + pagina
+ deriva) con le tre classi insieme, separata per A e B. ZL e IT.

Preregistrazione: preregistrazioni/e3c36.md. Scrive risultati/e3c36_finestra_a_b.json e .md.
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
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')


def main():
    rng = np.random.default_rng(3336)
    mano, lingua = {}, {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
        if r.lingua:
            lingua.setdefault(r.pagina, r.lingua)
    classi = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        for lg in ('A', 'B'):
            pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg) and lingua.get(pg) == lg]
            ris['%s, lingua %s' % (q, lg)] = x = e3c34.misura(pagine, classi, rng)
            x['pagine'] = len(pagine)
            print(q, lg, json.dumps(x), flush=True)
    ok = [k for k, x in ris.items() if x['R0'] >= 0.5 and x['R0_IC95'][0] > 0.2]
    if len(ok) == 4:
        esito = 'la finestra c\'è in A e in B, in tutte e due le trascrizioni'
    elif not ok:
        esito = 'la finestra non si ritrova in A e B prese da sole'
    else:
        esito = 'la finestra c\'è in: ' + ', '.join(ok)
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c36_finestra_a_b.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c36 — La finestra di k/t, sh/ch, -ey/-dy in A e in B', '', 'Preregistrazione: `preregistrazioni/e3c36.md`. Misura dell\'e3c34 con le tre classi insieme.', '',
          '| gruppo | pagine | parole | K(1) (IC 95%) | K(2) | K(3) | R0 (IC 95%) |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f (%.2f – %.2f) |' % (k, x['pagine'], x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['R0'], x['R0_IC95'][0], x['R0_IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c36_finestra_a_b.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
