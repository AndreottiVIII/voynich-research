# -*- coding: utf-8 -*-
"""Esperimento e3c40: la misura pulita (e3c34) sul Voynich ZL e su 5 riscritture con la sua catena di segni di ordine 2
(e3b69: forme di bordo e raccordo sì, memoria no). L'accordo fra parole accanto viene dalla catena?

Preregistrazione: preregistrazioni/e3c40.md. Scrive risultati/e3c40_finestra_catena.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3b62_memoria_nullo_largo as e3b62
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')
RISCRITTURE = 5
TRE = ('k/t', 'sh/ch', '-ey/-dy')


def main():
    rnd = random.Random(3340)
    rng = np.random.default_rng(3340)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    pagine, strati = [], []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(e3b62.D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp and mano.get(pg):
            pagine.append(pp)
            strati.append(mano[pg])

    def misura(pp):
        unita = [(h, [r for par in pars for r in par]) for h, pars in zip(strati, pp)]
        return OrderedDict([('k/t, sh/ch, -ey/-dy', e3c34.misura(unita, OrderedDict((k, e3b62.CV[k]) for k in TRE), rng)),
                            ('qo/o', e3c34.misura(unita, OrderedDict([('qo/o', e3b62.CV['qo/o'])]), rng))])
    ris = OrderedDict()
    ris['Voynich ZL'] = misura(pagine)
    print('Voynich', json.dumps(ris['Voynich ZL']), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    for k in range(RISCRITTURE):
        ris['catena %d' % (k + 1)] = misura(e3a78.riscrivi(pagine, tab, rnd))
        print('catena', k + 1, json.dumps(ris['catena %d' % (k + 1)]), flush=True)
    v = ris['Voynich ZL']['k/t, sh/ch, -ey/-dy']['K'][0]
    c = float(np.mean([ris['catena %d' % (k + 1)]['k/t, sh/ch, -ey/-dy']['K'][0] for k in range(RISCRITTURE)]))
    if c < v / 4:
        esito = 'l\'accordo fra parole accanto non viene dalla catena di segni'
    elif c >= v / 2:
        esito = 'l\'accordo fra parole accanto viene in buona parte dalla catena di segni'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('K1_voynich', v), ('K1_catene_media', c), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c40_finestra_catena.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c40 — L\'accordo delle scelte con la misura pulita viene dalla catena di segni?', '', 'Preregistrazione: `preregistrazioni/e3c40.md`. Misura dell\'e3c34 su Voynich ZL e su 5 riscritture con la sua catena di ordine 2.', '',
          '| testo | k/t, sh/ch, -ey/-dy: K(1) (IC 95%) / K(2) / K(3) | qo/o: K(1) / K(2) / K(3) |', '|---|---|---|']
    for k, x in ris.items():
        a, b = x['k/t, sh/ch, -ey/-dy'], x['qo/o']
        md.append('| %s | %+.3f (%+.3f – %+.3f) / %+.3f / %+.3f | %+.3f / %+.3f / %+.3f |' % (k, a['K'][0], a['K1_IC95'][0], a['K1_IC95'][1], a['K'][1], a['K'][2], b['K'][0], b['K'][1], b['K'][2]))
    md += ['', 'K(1) Voynich %+.3f; media delle riscritture %+.3f. Esito: **%s**.' % (v, c, esito)]
    open(os.path.join(RISULTATI, 'e3c40_finestra_catena.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
