# -*- coding: utf-8 -*-
"""Esperimento e3c45: le alternanze dentro la parola scelte dalla regola automatica dell'e3c01, con la misura pulita
(e3c34: righe di almeno 6 parole senza bordi; atteso stessa parola + pagina + deriva) sulle lingue dell'e3c01 tagliate in
righe finte con le lunghezze del Voynich (e3c28); riferimento: Voynich ZL e IT con k/t e sh/ch (scelte interne).

Preregistrazione: preregistrazioni/e3c45.md. Scrive risultati/e3c45_interne_misura_pulita.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c01_alternanze_interne as e3c01
import e3c28_forma_alla_pari as e3c28
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE = 50000


def main():
    rng = np.random.default_rng(3345)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        ris['Voynich %s (k/t, sh/ch)' % q] = e3c34.misura(pagine, OrderedDict((k, e3b62.CV[k]) for k in ('k/t', 'sh/ch')), rng)
        print(q, json.dumps(ris['Voynich %s (k/t, sh/ch)' % q]), flush=True)
    rif = min(ris[k]['K'][0] for k in ris)
    lung = e3c28.lunghezze_voynich()
    for chiave, righe in e381.testi().items():
        righe = [r for r in righe if r]
        if 'Abbreviated' in chiave or sum(len(r) for r in righe) < MIN_PAROLE:
            continue
        parole = [w for r in righe for w in r]
        scelte, _ = e3c01.alternanze([parole])
        classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
        rr = e3c28.righe_finte(parole, lung)
        x = e3c34.misura([('x', rr[i:i + 25]) for i in range(0, len(rr), 25)], classi, rng)
        x['alternanze'] = list(classi)
        x['come_il_voynich'] = bool(x['K1_IC95'][0] > 0.02 and x['K'][0] >= rif / 2)
        nome = chiave.replace('.txt', '')
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    simili = [k for k, x in ris.items() if not k.startswith('Voynich') and x['come_il_voynich']]
    if len(simili) <= 2:
        esito = 'le alternanze interne delle lingue non hanno l\'accordo del Voynich'
    elif len(simili) >= 5:
        esito = 'anche le lingue'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('riferimento_voynich_K1', rif), ('lingue_simili', simili), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c45_interne_misura_pulita.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c45 — Alternanze dentro la parola con la misura pulita: Voynich e lingue', '', 'Preregistrazione: `preregistrazioni/e3c45.md`. Lingue in righe finte con le lunghezze del Voynich; atteso stessa parola + pagina + deriva.', '',
          '| testo | alternanze | K(1) (IC 95%) | K(2) | K(3) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f |' % (k, ', '.join(x.get('alternanze', ['k/t', 'sh/ch'])), x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2]))
    md += ['', 'Riferimento (il più piccolo K(1) del Voynich): %+.3f. Lingue simili: %s.' % (rif, ', '.join(simili) or 'nessuna'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c45_interne_misura_pulita.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
