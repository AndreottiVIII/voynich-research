# -*- coding: utf-8 -*-
"""Esperimento e3b69: misura della memoria delle scelte (e3b62) sul Voynich riscritto dalla propria catena di ordine 2
(forme di bordo e raccordo sì, memoria no): controllo di distorsione.

Preregistrazione: preregistrazioni/e3b69.md. Scrive risultati/e3b69_memoria_catena.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
RISCRITTURE = 5


def main():
    rnd = random.Random(3269)
    rng = np.random.default_rng(3269)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    pagine, strati = [], []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp and mano.get(pg):
            pagine.append(pp)
            strati.append(mano[pg])

    def misura(pp):
        unita = [[r for par in pars for r in par] for pars in pp]
        return e3b62.prova(OrderedDict((k, e3b62.prepara(unita, strati, f)) for k, f in e3b62.CV.items()), rng)
    ris = OrderedDict()
    ris['Voynich ZL'] = misura(pagine)
    print('Voynich', json.dumps(ris['Voynich ZL']['insieme']), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    for k in range(RISCRITTURE):
        ris['catena %d' % (k + 1)] = misura(e3a78.riscrivi(pagine, tab, rnd))
        print('catena', k + 1, json.dumps(ris['catena %d' % (k + 1)]['insieme']), flush=True)
    ev = ris['Voynich ZL']['insieme']['effetto']
    ec = [ris['catena %d' % (k + 1)]['insieme']['effetto'] for k in range(RISCRITTURE)]
    pc = [ris['catena %d' % (k + 1)]['insieme']['p'] for k in range(RISCRITTURE)]
    media = float(np.mean(ec))
    if media < ev / 5 and all(p >= 0.01 for p in pc):
        esito = 'la misura non è distorta'
    elif media >= ev / 2:
        esito = 'la misura è distorta'
    else:
        esito = 'in parte'
    out = OrderedDict([('gruppi', ris), ('effetto_Voynich', ev), ('effetto_catene_media', media), ('quota_oltre_la_catena', (ev - media) / ev if ev else None), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b69_memoria_catena.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b69 — La misura della memoria è distorta dalle forme di bordo e dal raccordo? Controllo con la catena', '', 'Preregistrazione: `preregistrazioni/e3b69.md`. Metodo dell\'e3b62.', '',
          '| testo | coppie vicine | M | M nullo | effetto | z | p | qo/o | k/t | sh/ch | -ey/-dy |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for k, r in ris.items():
        x = r['insieme']
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f | %s |' % (k, x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['z'], x['p'],
                                                                      ' | '.join('%+.3f' % r[c]['effetto'] if r[c]['effetto'] is not None else 'n.d.' for c in e3b62.CV)))
    md += ['', 'Effetto Voynich %+.4f; media delle catene %+.4f; quota oltre la catena %.2f.' % (ev, media, out['quota_oltre_la_catena']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b69_memoria_catena.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
