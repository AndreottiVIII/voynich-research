# -*- coding: utf-8 -*-
"""Esperimento e3b17: le quattro misure di vocabolario e spazi (e3a69) sul Voynich vero e con le varianti unite
(sh -> ch, q iniziale tolta, serie di e ridotte a una).

Preregistrazione: preregistrazioni/e3b17.md. Scrive risultati/e3b17_varianti_unite.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a69_catene_sintetiche as e3a69

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
P90 = OrderedDict(zip(e3a69.MISURE, (0.202, 0.086, 0.718, 0.122)))


def unisci(w):
    w = w.replace('sh', 'ch')
    if w.startswith('q') and len(w) > 1:
        w = w[1:]
    return re.sub('e+', 'e', w)


def pagine(f):
    out = []
    for pars in e341.pagine().values():
        righe = [[w for w in (tuple(D(f(x))) for x in r if trascrizione.pulita(x)) if w] for par in pars for r in par]
        righe = [r for r in righe if r]
        if righe:
            out.append(righe)
    return out


def mediana(pp, rnd):
    sub = []
    for _ in range(5):
        ordine = rnd.sample(pp, len(pp))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(e3a69.misure(prese, rnd))
    return OrderedDict((m, statistics.median(s[m] for s in sub)) for m in e3a69.MISURE)


def main():
    rnd = random.Random(3217)
    vero = mediana(pagine(lambda w: w), rnd)
    unito = mediana(pagine(unisci), rnd)
    sopra = sum(1 for m in e3a69.MISURE if unito[m] is not None and unito[m] > P90[m])
    esito = 'le varianti non nascondono una lingua' if sopra >= 3 else 'unire le varianti avvicina il Voynich alle lingue'
    out = OrderedDict([('vero', vero), ('unito', unito), ('p90_lingue', P90), ('misure_sopra_p90', sopra), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b17_varianti_unite.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b17 — Unendo le varianti di grafia, il Voynich somiglia di più a una lingua?', '', 'Preregistrazione: `preregistrazioni/e3b17.md`. Varianti unite: sh → ch, q iniziale tolta, serie di e ridotte a una.', '',
          '| misura | Voynich vero | varianti unite | 90° percentile delle lingue |', '|---|---|---|---|']
    md += ['| %s | %.3f | %.3f | %.3f |' % (m, vero[m], unito[m], P90[m]) for m in e3a69.MISURE]
    md += ['', 'Misure sopra il 90° percentile delle lingue col testo unito: %d su 4.' % sopra, '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b17_varianti_unite.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
