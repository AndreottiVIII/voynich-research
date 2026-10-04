# -*- coding: utf-8 -*-
"""Esperimento e3c17: la deriva delle scelte lungo la riga (e3c13) c'è in ogni mano (1, 2, 3) e in tutte e due le lingue
di Currier (A, B)? Pendenza della scelta sui segni scritti prima nella riga, a parità di parola coperta, senza prima e
ultima parola della riga, quattro classi insieme con il valore 1 = qo, k, sh, -ey. ZL e IT.

Preregistrazione: preregistrazioni/e3c17.md. Scrive risultati/e3c17_deriva_per_mano.json e .md.
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
import e3c13_sh_lungo_la_riga as e3c13

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3317)
    mano, lingua = {}, {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
        if r.lingua:
            lingua.setdefault(r.pagina, r.lingua)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        for nome, scegli in (('mano 1', lambda p: mano.get(p) == '1'), ('mano 2', lambda p: mano.get(p) == '2'), ('mano 3', lambda p: mano.get(p) == '3'),
                             ('lingua A', lambda p: lingua.get(p) == 'A'), ('lingua B', lambda p: lingua.get(p) == 'B')):
            sotto = OrderedDict((p, v) for p, v in pd.items() if scegli(p))
            uu, _ = e3b62.voynich(sotto, mano)
            x = e3c13.pendenza(uu, e3b62.CV, rng)
            x['pagine'] = len(uu)
            ris['%s, %s' % (q, nome)] = x
            print(q, nome, json.dumps(x), flush=True)
    gruppi = ('mano 1', 'mano 2', 'mano 3', 'lingua A', 'lingua B')
    sotto0 = [g for g in gruppi if all(ris['%s, %s' % (q, g)]['IC95'][1] < 0 for q in ('ZL', 'IT'))]
    if len(sotto0) == len(gruppi):
        esito = 'la deriva c\'è in ogni mano e in tutte e due le lingue'
    elif not sotto0:
        esito = 'la deriva non si ritrova nei gruppi presi da soli'
    else:
        esito = 'la deriva c\'è in: ' + ', '.join(sotto0)
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c17_deriva_per_mano.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c17 — La deriva delle scelte lungo la riga, per mano e per lingua di Currier', '', 'Preregistrazione: `preregistrazioni/e3c17.md`. Quattro classi insieme (1 = qo, k, sh, -ey); tutto il testo (e3c13): −0,020 – −0,035 ogni 10 segni per classe.', '',
          '| gruppo | pagine | parole | quota del primo valore | ogni 10 segni (IC 95%) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %.3f | %+.4f (%+.4f – %+.4f) |' % (k, x['pagine'], x['parole'], x['quota_1'], x['per_10_segni'], 10 * x['IC95'][0], 10 * x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c17_deriva_per_mano.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
