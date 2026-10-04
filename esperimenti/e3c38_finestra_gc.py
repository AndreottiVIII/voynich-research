# -*- coding: utf-8 -*-
"""Esperimento e3c38: la finestra (e3c34/e3c35) classe per classe nella trascrizione di Glen Claston (v101), con le tre
alternanze scelte dalla regola automatica (h/k, a/o, 7/8). Confronto descrittivo con k/t di ZL e IT.

Preregistrazione: preregistrazioni/e3c38.md. Scrive risultati/e3c38_finestra_gc.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3c01_alternanze_interne as e3c01
import e3c05_terza_trascrizione as e3c05
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3338)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, ss = e3c05.unita_gc(mano)
    pagine = list(zip(ss, uu))
    scelte, _ = e3c01.alternanze([r for u in uu for r in u])
    ris = OrderedDict()
    for c in scelte:
        k = '%s/%s' % c
        ris[k] = e3c34.misura(pagine, OrderedDict([(k, e3c01.classe(*c))]), rng)
        print(k, json.dumps(ris[k]), flush=True)
    gall = ris.get('h/k')
    if gall is None:
        esito = 'la regola non ha scelto h/k'
    elif gall['R0'] >= 0.5 and gall['K1_IC95'][0] > 0:
        esito = 'le gallows di GC hanno la finestra come k/t in EVA'
    elif gall['R0'] < 0.3:
        esito = 'le gallows di GC non hanno la finestra'
    else:
        esito = 'incerto'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c38_finestra_gc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c38 — La finestra nella trascrizione di Glen Claston, classe per classe', '', 'Preregistrazione: `preregistrazioni/e3c38.md`. k/t in EVA (e3c35): K(1) +0,125 / +0,129, R0 0,56 / 0,57 (ZL / IT).', '',
          '| classe (GC) | parole | K(1) (IC 95%) | K(2) | K(3) | R0 (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f (%.2f – %.2f) |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['R0'], x['R0_IC95'][0], x['R0_IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c38_finestra_gc.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
