# -*- coding: utf-8 -*-
"""Esperimento 353: la ripresa dalle 2 righe sopra (misura dell'e346) nei generatori pubblicati (Naibbe, U2, U3, Timm e
Schinner) contro il Voynich.

Preregistrazione: preregistrazioni/e353.md. Scrive risultati/e353_generatori.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e346_gibberish as e346

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
e346.NUL = 100


def a_pagine(righe):
    rr = [ps for _, ps in righe]
    return OrderedDict((str(i), rr[i:i + 29]) for i in range(0, len(rr), 29) if len(rr[i:i + 29]) >= 10)


def main():
    rnd = random.Random(353)
    segni = lambda w: tuple(D(w))
    t = e134.testi()
    unita = OrderedDict([('Voynich', e346.unita_voynich())])
    for k, v in t.items():
        if k != 'Voynich':
            unita[k] = a_pagine(v)
    for s in (1, 19):
        unita['Timm e Schinner, seme %d' % s] = OrderedDict((str(i), p) for i, p in enumerate(e337.pagine_ts(s)))
    ris = OrderedDict()
    for k, u in unita.items():
        ris[k] = e346.gruppo(u, segni, rnd)
        print('%-36s unità %3d E %+.4f R %.2f IC %s' % (k, ris[k]['unita'], ris[k]['E'], ris[k]['R'] or 0, [round(x, 4) for x in ris[k]['IC95']]), flush=True)
    V = ris['Voynich']['IC95']
    for k, r in ris.items():
        if k == 'Voynich':
            continue
        if r['IC95'][1] < V[0]:
            r['confronto'] = 'sotto'
        elif r['IC95'][0] > V[1]:
            r['confronto'] = 'sopra'
        else:
            r['confronto'] = 'pari al Voynich'
    esito = 'nessun generatore la riproduce' if all(r.get('confronto') == 'sotto' for k, r in ris.items() if k != 'Voynich') else \
        'la riproducono: ' + ', '.join(k for k, r in ris.items() if r.get('confronto') in ('pari al Voynich', 'sopra'))
    json.dump(OrderedDict([('testi', ris), ('esito', esito)]), open(os.path.join(RISULTATI, 'e353_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e353 — La ripresa dalle righe sopra nei generatori pubblicati', '', 'Preregistrazione: `preregistrazioni/e353.md`.', '',
          '| testo | pagine | eccesso E | rapporto R | IC 95% | confronto |', '|---|---|---|---|---|---|']
    for k, r in ris.items():
        md.append('| %s | %d | %+.4f | %.2f | %+.4f – %+.4f | %s |' % (k, r['unita'], r['E'], r['R'] or 0, r['IC95'][0], r['IC95'][1], r.get('confronto', '—')))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e353_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
