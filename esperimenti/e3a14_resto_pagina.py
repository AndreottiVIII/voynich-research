# -*- coding: utf-8 -*-
"""Esperimento e3a14: e3a08 con il nullo dentro la pagina: l'identita' della parola prima (dopo) dice ancora qualcosa sul
primo (ultimo) segno della vicina, a parita' di segno di bordo e di pagina?

Preregistrazione: preregistrazioni/e3a14.md. Scrive risultati/e3a14_resto_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def eventi(pagine):
    av, ind = [], []
    for pg, righe in pagine:
        for r in righe:
            for a, b in zip(r, r[1:]):
                av.append(((pg, a[-1]), a, b[0]))
                ind.append(((pg, b[0]), b, a[-1]))
    return av, ind


def due(pagine, rnd, perm):
    av, ind = eventi(pagine)
    return OrderedDict([('avanti', e380.prova(av, rnd, perm)), ('indietro', e380.prova(ind, rnd, perm))])


def main():
    rnd = random.Random(3114)
    voy = []
    for pg, pars in e341.pagine().items():
        voy.append((pg, [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]))
    ris = OrderedDict([('Voynich', due(voy, rnd, 1000))])
    print('Voynich', json.dumps(ris['Voynich'], default=float), flush=True)
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy, len(voy))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese.append(p)
            n += sum(len(r) for r in p[1])
        x = due(prese, rnd, 100)
        sub.append((x['avanti']['E'], x['indietro']['E']))
    ris['Voynich a 10.000 parole'] = OrderedDict([('avanti', [a for a, _ in sub]), ('indietro', [b for _, b in sub])])
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = due([(i, righe[i:i + 25]) for i in range(0, len(righe), 25)], rnd, 100)
    ris['testi_sensati'] = sens
    esiti = OrderedDict()
    for lato in ('avanti', 'indietro'):
        z = ris['Voynich'][lato]['z']
        grandi = [x[lato]['E'] for x in sens.values() if x[lato]['eventi'] >= 5000]
        m = statistics.median(grandi)
        ev = statistics.median(ris['Voynich a 10.000 parole'][lato])
        if z < 2:
            es = 'il resto era lessico della pagina'
        elif z > 3:
            es = 'resta un piccolo legame fra vicine (Voynich %.4f contro mediana delle lingue %.4f)' % (ev, m)
        else:
            es = 'incerto'
        esiti[lato] = OrderedDict([('z', z), ('E_voynich_10000', ev), ('mediana_lingue', m), ('esito', es)])
    ris['esiti'] = esiti
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a14_resto_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    V = ris['Voynich']
    md = ['# e3a14 — Il resto oltre il segno di bordo viene dal lessico della pagina?', '', 'Preregistrazione: `preregistrazioni/e3a14.md`. Nullo dentro (pagina, segno di bordo).', '',
          '| | avanti E | z | indietro E | z |', '|---|---|---|---|---|',
          '| Voynich (tutto) | %.4f | %.1f | %.4f | %.1f |' % (V['avanti']['E'], V['avanti']['z'], V['indietro']['E'], V['indietro']['z']),
          '| Voynich a 10.000 parole (mediana) | %.4f | | %.4f | |' % (esiti['avanti']['E_voynich_10000'], esiti['indietro']['E_voynich_10000']),
          '| testi sensati con almeno 5.000 coppie (mediana) | %.4f | | %.4f | |' % (esiti['avanti']['mediana_lingue'], esiti['indietro']['mediana_lingue']),
          '', 'Esito avanti: **%s**. Esito indietro: **%s**.' % (esiti['avanti']['esito'], esiti['indietro']['esito'])]
    open(os.path.join(RISULTATI, 'e3a14_resto_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
