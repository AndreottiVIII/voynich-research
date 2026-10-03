# -*- coding: utf-8 -*-
"""Esperimento 265: nel testo circolare (loci Cc) la giuntura fra l'ultima e la prima parola dello stesso anello ha il
legame delle parole vicine (lift dell'e152)?

Preregistrazione: preregistrazioni/e265.md. Scrive risultati/e265_anelli.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e152_righe_in_ordine as e152

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEME, REPLICHE = 265, 1000


def main():
    rnd = random.Random(SEME)
    L = e152.lift()
    anelli = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo == 'Cc':
            ps = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            if len(ps) >= 4:
                anelli.append(ps)
    punt = lambda a, b: math.log(max(L.get((a[-1], b[0]), 0.05), 1e-3))
    chiusura = [punt(a[-1], a[0]) for a in anelli]
    vicine = [punt(x, y) for a in anelli for x, y in zip(a, a[1:])]
    nulli = []
    for _ in range(REPLICHE):
        vs = []
        for i, a in enumerate(anelli):
            j = rnd.choice([k for k in range(len(anelli)) if k != i])
            vs.append(punt(a[-1], anelli[j][0]))
        nulli.append(statistics.mean(vs))
    m, mu, sd = statistics.mean(chiusura), statistics.mean(nulli), statistics.pstdev(nulli)
    z = (m - mu) / sd if sd else None
    mv, sdv = statistics.mean(vicine), statistics.pstdev(vicine)
    esito = ('anello continuo' if (z or 0) > 3 and m >= mv - sdv else 'inizio marcato' if abs(z or 0) <= 2 else 'incerto')
    ris = OrderedDict([('anelli', len(anelli)), ('chiusura_media', m), ('nullo', mu), ('z', z), ('vicine_media', mv), ('vicine_sd', sdv), ('esito', esito)])
    print(dict(ris), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e265_anelli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e265 — Il testo circolare si legge come un anello continuo?', '',
          'Anelli (loci Cc, ≥ 4 parole): %d. Punteggio = log del lift di giuntura (e152). Nullo: ultima parola di un anello → prima di un altro, %d repliche. '
          'Preregistrazione: `preregistrazioni/e265.md`.' % (len(anelli), REPLICHE), '',
          '| giunture | media |', '|---|---|', '| chiusura (ultima → prima) | %.3f |' % m, '| nullo (ultima → prima di un altro anello) | %.3f (z %.1f) |' % (mu, z or 0),
          '| parole vicine negli anelli | %.3f (sd %.3f) |' % (mv, sdv), '', 'Potenza limitata (%d anelli). Esito: **%s**.' % (len(anelli), esito)]
    open(os.path.join(RISULTATI, 'e265_anelli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
