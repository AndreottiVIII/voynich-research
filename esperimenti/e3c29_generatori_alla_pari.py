# -*- coding: utf-8 -*-
"""Esperimento e3c29: la misura alla pari dell'e3c28 (righe senza bordi, coppie dentro la riga, atteso dalla stessa parola
coperta) sui generatori: Naibbe, U2, U3, Timm e Schinner, classi scelte a mano, unità di 25 righe.

Preregistrazione: preregistrazioni/e3c29.md. Scrive risultati/e3c29_generatori_alla_pari.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3b62_memoria_nullo_largo as e3b62
import e3c02_alternanze_generatori as e3c02
import e3c07_lettere_parole_bilanciate as e3c07
import e3c28_forma_alla_pari as e3c28

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3329)
    prima = json.load(open(os.path.join(RISULTATI, 'e3c28_forma_alla_pari.json'), encoding='utf-8'))['testi']
    rif = min(prima[q]['accanto'] for q in ('Voynich IT', 'Voynich ZL'))
    ris = OrderedDict()
    for nome, righe in e3c02.generatori().items():
        uu = e3c07.senza_bordi([righe[i:i + 25] for i in range(0, len(righe), 25)])
        x = e3c28.misura(uu, [nome] * len(uu), e3b62.CV, rng)
        x['come_il_voynich'] = bool(x['accanto_IC95'][0] is not None and x['accanto_IC95'][0] > 0.02 and x['accanto'] >= rif / 2)
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    simili = [k for k, x in ris.items() if x['come_il_voynich']]
    esito = 'nessun generatore ha l\'accordo delle scelte del Voynich' if not simili else 'accordo come il Voynich in: ' + ', '.join(simili)
    out = OrderedDict([('generatori', ris), ('riferimento_voynich_accanto', rif), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c29_generatori_alla_pari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def due(a):
        return '—' if a is None else '%.2f' % a
    md = ['# e3c29 — I generatori con la misura alla pari', '', 'Preregistrazione: `preregistrazioni/e3c29.md`. Voynich (e3c28): accordo accanto +0,170 (IT), +0,184 (ZL); R 0,85 / 0,82.', '',
          '| generatore | accordo accanto (IC 95%) | R (IC 95%) |', '|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %+.3f (%s – %s) | %s (%s – %s) |' % (k, x['accanto'], due(x['accanto_IC95'][0]), due(x['accanto_IC95'][1]), due(x['R']), due(x['R_IC95'][0]), due(x['R_IC95'][1])))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c29_generatori_alla_pari.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
