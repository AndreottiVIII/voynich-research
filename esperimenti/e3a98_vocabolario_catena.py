# -*- coding: utf-8 -*-
"""Esperimento e3a98: parole diverse, parole uniche e pendenza di Zipf nel Voynich vero e riscritto dalla catena di
ordine 2 per riga (come e3a78).

Preregistrazione: preregistrazioni/e3a98.md. Scrive risultati/e3a98_vocabolario_catena.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NOMI = ('parole diverse per 10.000', 'quota di parole uniche', 'pendenza di Zipf (10-1000)')


def proprieta(pagine):
    parole = [w for pars in pagine for par in pars for r in par for w in r]
    blocchi = [len(set(parole[i:i + 10000])) for i in range(0, len(parole) - 9999, 10000)][:5]
    f = Counter(parole)
    uniche = sum(1 for w in parole if f[w] == 1) / len(parole)
    fr = sorted(f.values(), reverse=True)
    rr = np.arange(10, min(1000, len(fr)) + 1)
    y = np.log([fr[r - 1] for r in rr])
    pend = float(np.polyfit(np.log(rr), y, 1)[0])
    return OrderedDict([(NOMI[0], statistics.mean(blocchi)), (NOMI[1], uniche), (NOMI[2], pend)])


def main():
    rnd = random.Random(3198)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append([par for par in pp if par])
    vero = proprieta(pagine)
    print('vero', json.dumps(vero, ensure_ascii=False), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    risc = [proprieta(e3a78.riscrivi(pagine, tab, rnd)) for _ in range(e3a78.RISCRITTURE)]
    sintesi = OrderedDict()
    for n in NOMI:
        rv = statistics.mean(x[n] for x in risc)
        R = abs(rv) / abs(vero[n]) if vero[n] else None
        es = 'n.d.' if R is None else ('la catena la riproduce' if 0.9 <= R <= 1.1 else ('la catena ne fa di più' if R > 1.1 else 'la catena ne fa di meno'))
        sintesi[n] = OrderedDict([('vero', vero[n]), ('riscritto', [x[n] for x in risc]), ('riscritto_media', rv), ('R', R), ('esito', es)])
    print(json.dumps(sintesi, ensure_ascii=False, indent=1), flush=True)
    json.dump(OrderedDict([('sintesi', sintesi)]), open(os.path.join(RISULTATI, 'e3a98_vocabolario_catena.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a98 — La quantità di vocabolario è quella che la catena di segni produce?', '', 'Preregistrazione: `preregistrazioni/e3a98.md`.', '',
          '| misura | Voynich vero | riscritto (media) | R | esito |', '|---|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %.2f | %s |' % (n, x['vero'], x['riscritto_media'], x['R'], x['esito']) for n, x in sintesi.items()]
    open(os.path.join(RISULTATI, 'e3a98_vocabolario_catena.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
