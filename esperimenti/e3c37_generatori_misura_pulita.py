# -*- coding: utf-8 -*-
"""Esperimento e3c37: la misura più pulita (e3c34: righe di almeno 6 parole senza bordi; atteso stessa parola + pagina +
deriva) sui generatori, con k/t, sh/ch, -ey/-dy insieme e con qo/o da sola. Pagine = unità di 25 righe.

Preregistrazione: preregistrazioni/e3c37.md. Scrive risultati/e3c37_generatori_misura_pulita.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3b62_memoria_nullo_largo as e3b62
import e3c02_alternanze_generatori as e3c02
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
VOYNICH_K1 = 0.106


def main():
    rng = np.random.default_rng(3337)
    ris = OrderedDict()
    for nome, righe in e3c02.generatori().items():
        pagine = [('g', righe[i:i + 25]) for i in range(0, len(righe), 25)]
        x = OrderedDict()
        x['k/t, sh/ch, -ey/-dy'] = e3c34.misura(pagine, OrderedDict((k, e3b62.CV[k]) for k in TRE), rng)
        x['qo/o'] = e3c34.misura(pagine, OrderedDict([('qo/o', e3b62.CV['qo/o'])]), rng)
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    simili = [k for k, x in ris.items() if x['k/t, sh/ch, -ey/-dy']['K1_IC95'][0] > 0.02 and x['k/t, sh/ch, -ey/-dy']['K'][0] >= VOYNICH_K1 / 2]
    esito = 'nessun generatore ha l\'accordo di k/t, sh/ch, -ey/-dy' if not simili else 'accordo come il Voynich in: ' + ', '.join(simili)
    out = OrderedDict([('generatori', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c37_generatori_misura_pulita.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c37 — I generatori con la misura più pulita', '', 'Preregistrazione: `preregistrazioni/e3c37.md`. Voynich (e3c34–e3c36): K(1) +0,10 – +0,14 con k/t, sh/ch, -ey/-dy; qo/o K(1) ≈ 0, K(3) +0,11.', '',
          '| generatore | classi | K(1) (IC 95%) | K(2) | K(3) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        for c, y in x.items():
            md.append('| %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f |' % (k, c, y['K'][0], y['K1_IC95'][0], y['K1_IC95'][1], y['K'][1], y['K'][2]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c37_generatori_misura_pulita.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
