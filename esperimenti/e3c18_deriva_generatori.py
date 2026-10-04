# -*- coding: utf-8 -*-
"""Esperimento e3c18: la deriva delle scelte lungo la riga (e3c13) c'è nei generatori? Naibbe, U2, U3, Timm e Schinner,
classi scelte a mano, pendenza a parità di parola coperta senza prima e ultima parola della riga, quattro classi
insieme (1 = qo, k, sh, -ey) e separate; unità di 25 righe.

Preregistrazione: preregistrazioni/e3c18.md. Scrive risultati/e3c18_deriva_generatori.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3b62_memoria_nullo_largo as e3b62
import e3c02_alternanze_generatori as e3c02
import e3c13_sh_lungo_la_riga as e3c13

RISULTATI = os.path.join(QUI, '..', 'risultati')
VOYNICH_B = -0.035


def main():
    rng = np.random.default_rng(3318)
    ris = OrderedDict()
    for nome, righe in e3c02.generatori().items():
        uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
        x = OrderedDict([('insieme', e3c13.pendenza(uu, e3b62.CV, rng))])
        for k, f in e3b62.CV.items():
            x[k] = e3c13.pendenza(uu, OrderedDict([(k, f)]), rng)
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    sotto = [k for k, x in ris.items() if x['insieme']['IC95'][1] < 0 and x['insieme']['per_10_segni'] <= VOYNICH_B / 3]
    if not sotto:
        esito = 'i generatori non hanno la deriva lungo la riga'
    elif len(sotto) == len(ris):
        esito = 'tutti i generatori hanno la deriva'
    else:
        esito = 'deriva in: ' + ', '.join(sotto)
    out = OrderedDict([('generatori', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c18_deriva_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c18 — La deriva delle scelte lungo la riga nei generatori', '', 'Preregistrazione: `preregistrazioni/e3c18.md`. Voynich (e3c17, classi insieme): A −0,011, B −0,035 ogni 10 segni.', '',
          '| generatore | classi | parole | ogni 10 segni (IC 95%) |', '|---|---|---|---|']
    for k, x in ris.items():
        for c, y in x.items():
            md.append('| %s | %s | %d | %+.4f (%+.4f – %+.4f) |' % (k, c, y['parole'], y['per_10_segni'], 10 * y['IC95'][0], 10 * y['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c18_deriva_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
