# -*- coding: utf-8 -*-
"""Esperimento e3c76: lo stato lento che attraversa le righe (e3c75) c'è anche negli scribi veri? (batteria scribi, 7).
Misura dell'e3c74 (K corretto per coppie della stessa scelta: stessa riga a distanza ≥ 5, righe consecutive, righe a due
di distanza) sulle 17 scelte di forma di lettera degli scribi Menota entrate negli e3c50 ed e3c58; Voynich ZL (qo/o,
k/t, sh/ch, -ey/-dy) nella stessa esecuzione.

Preregistrazione: preregistrazioni/e3c76.md. Scrive risultati/e3c76_stato_lento_scribi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b62_memoria_nullo_largo as e3b62
import e3c58_altri_scribi as e3c58
import e3c62_deriva_scribi as e3c62
import e3c74_impostazione_di_riga as e3c74

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')


def main():
    e3c74.PERM = 50
    rng = np.random.default_rng(3376)
    ris = OrderedDict()
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in e341.pagine().items() if mano.get(pg)]
    ris['Voynich ZL'] = x = e3c74.misura(pagine, OrderedDict((k, e3b62.CV[k]) for k in QUATTRO), rng)
    print('Voynich', json.dumps(x, ensure_ascii=False), flush=True)
    soglia = x['righe consecutive']['K_corretto'] / 2
    testi = {}
    for ms, nome, f, tipo in e3c62.scelte():
        if tipo != 'lettera':
            continue
        if ms not in testi:
            testi[ms] = [(h, rr) for _, h, rr in e3c58.leggi(ms)]
        y = e3c74.misura(testi[ms], OrderedDict([(nome, f)]), rng)
        c = y['righe consecutive']
        y['stato_lento'] = c['IC95'][0] > 0
        y['come_voynich'] = y['stato_lento'] and c['K_corretto'] >= soglia
        ris['%s, %s' % (ms, nome)] = y
        print(ms, nome, json.dumps(y, ensure_ascii=False), flush=True)
    come = [k for k, y in ris.items() if k != 'Voynich ZL' and y['come_voynich']]
    lente = [k for k, y in ris.items() if k != 'Voynich ZL' and y['stato_lento']]
    if len(come) >= 3:
        esito = 'gli scribi hanno uno stato lento come il Voynich'
    elif not lente:
        esito = 'nessuno stato lento negli scribi'
    else:
        esito = 'stato lento in poche scelte degli scribi (%d con accordo fra righe, %d grandi come il Voynich)' % (len(lente), len(come))
    out = OrderedDict([('misure', ris), ('soglia', soglia), ('con_stato_lento', lente), ('come_voynich', come), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c76_stato_lento_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c76 — Lo stato lento che attraversa le righe negli scribi veri', '', 'Preregistrazione: `preregistrazioni/e3c76.md`. Soglia (metà del Voynich, righe consecutive): %+.3f.' % soglia, '',
          '| testo, scelta | stessa riga, distanza ≥ 5 | righe consecutive | righe a due di distanza |', '|---|---|---|---|']
    for k, y in ris.items():
        md.append('| %s | %s |' % (k, ' | '.join('%+.3f (%+.3f – %+.3f)' % (y[g]['K_corretto'], y[g]['IC95'][0], y[g]['IC95'][1]) for g in e3c74.GRUPPI)))
    md += ['', 'Esito: **%s**.' % esito, '', 'Con accordo fra righe consecutive: %s.' % (', '.join(lente) or 'nessuna'), 'Grandi come il Voynich: %s.' % (', '.join(come) or 'nessuna'),
           '', 'Fonte dei testi degli scribi: Menota (CC-BY-SA 4.0); file non nel repository.']
    open(os.path.join(RISULTATI, 'e3c76_stato_lento_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
