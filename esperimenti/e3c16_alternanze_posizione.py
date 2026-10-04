# -*- coding: utf-8 -*-
"""Esperimento e3c16: la memoria nelle alternanze interne scelte dalla regola automatica (e3c01, e3c05) con il nullo che
conserva la posizione nella riga (e3c14). Voynich IT, ZL e GC (v101).

Preregistrazione: preregistrazioni/e3c16.md. Scrive risultati/e3c16_alternanze_posizione.json e .md.
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
import e3c05_terza_trascrizione as e3c05
import e3c14_nullo_posizione as e3c14

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3316)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    testi = OrderedDict()
    for nome, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        testi[nome] = e3b62.voynich(pd, mano)
    testi['Voynich GC (v101)'] = e3c05.unita_gc(mano)
    ris = OrderedDict()
    for nome, (uu, ss) in testi.items():
        scelte, _ = e3c01.alternanze([r for u in uu for r in u])
        classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
        cc = OrderedDict((k, e3b62.prepara(uu, ss, f)) for k, f in classi.items())
        ris[nome] = OrderedDict([('alternanze', list(classi)),
                                 ('nullo solito', e3c14.memoria(cc, rng)),
                                 ('nullo con posizione', e3c14.memoria(OrderedDict((k, e3c14.con_posizione(c, uu, classi[k])) for k, c in cc.items()), rng))])
        print(nome, json.dumps(ris[nome], ensure_ascii=False, default=float), flush=True)
    sopra = [k for k, x in ris.items() if x['nullo con posizione']['IC95'][0] > 0]
    if len(sopra) == 3:
        esito = 'la memoria nelle alternanze automatiche regge senza la posizione in tutte e tre le trascrizioni'
    elif not sopra:
        esito = 'senza la posizione la memoria nelle alternanze automatiche non regge'
    else:
        esito = 'regge in %d trascrizioni su 3' % len(sopra)
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c16_alternanze_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c16 — Memoria nelle alternanze automatiche con il nullo che conserva la posizione', '', 'Preregistrazione: `preregistrazioni/e3c16.md`.', '',
          '| trascrizione | alternanze | nullo solito (IC 95%) | nullo con posizione (IC 95%) |', '|---|---|---|---|']
    for k, x in ris.items():
        a, b = x['nullo solito'], x['nullo con posizione']
        md.append('| %s | %s | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) |' % (k, ', '.join(x['alternanze']), a['effetto'], a['IC95'][0], a['IC95'][1], b['effetto'], b['IC95'][0], b['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c16_alternanze_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
