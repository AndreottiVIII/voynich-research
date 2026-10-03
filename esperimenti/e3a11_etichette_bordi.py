# -*- coding: utf-8 -*-
"""Esperimento e3a11: a parita' del resto della parola, quali ultimi e primi segni crescono o calano nelle etichette
rispetto al mezzo della riga (metodo dell'e389).

Preregistrazione: preregistrazioni/e3a11.md. Scrive risultati/e3a11_etichette_bordi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e389_varianti_bordo as e389

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rng = np.random.RandomState(3111)
    fine, inizio = [], []
    for r in trascrizione.leggi('ZL'):
        t = r.tipo[0]
        if t not in (trascrizione.ETICHETTA, trascrizione.PARAGRAFO):
            continue
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        sez = r.sezione or '?'
        if t == trascrizione.ETICHETTA:
            for w in ws:
                if len(w) >= 2:
                    fine.append(((sez, w[:-1]), True, w[-1]))
                    inizio.append(((sez, w[1:]), True, w[0]))
        else:
            n = len(ws)
            for j, w in enumerate(ws):
                if 0 < j < n - 1 and len(w) >= 2:
                    fine.append(((sez, w[:-1]), False, w[-1]))
                    inizio.append(((sez, w[1:]), False, w[0]))
    ris = OrderedDict([('finali', e389.analizza(fine, rng)), ('iniziali', e389.analizza(inizio, rng))])
    for k in ('finali', 'iniziali'):
        print(k, ris[k]['crescono'], ris[k]['calano'], flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a11_etichette_bordi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a11 — Le etichette, a parità del resto della parola: quali finali e quali iniziali?', '', 'Preregistrazione: `preregistrazioni/e3a11.md`. Δ = quanto il segno è più frequente nelle etichette che in mezzo alla riga, a parità del resto della parola e della sezione.', '']
    for k in ('finali', 'iniziali'):
        x = ris[k]
        md += ['## %s (%d gruppi, %d etichette)' % (k, x['gruppi'], x['parole_al_bordo']), '', '| segno | Δ | z |', '|---|---|---|']
        md += ['| %s | %+.4f | %.1f |' % (s, v['delta'], v['z']) for s, v in x['segni'].items() if abs(v['z']) >= 2]
        md += ['', 'Crescono (z > 3): %s. Calano (z < −3): %s.' % (', '.join(x['crescono']) or 'nessuno', ', '.join(x['calano']) or 'nessuno'), '']
    open(os.path.join(RISULTATI, 'e3a11_etichette_bordi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
