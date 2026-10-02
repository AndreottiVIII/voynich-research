# -*- coding: utf-8 -*-
"""Esperimento 186c: come l'e186b, ma con permutazioni dentro la pagina (separate per coppie dentro la riga e
attraverso l'a capo).

Preregistrazione: preregistrazioni/e186c.md. Scrive risultati/e186c_finali_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e186_nulli_acrostici as e186

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 1863, 500
D = e186.D


def coppie(righe, quale):
    pulita = trascrizione.pulita
    pos = 0 if quale == 'I1' else -1
    dentro, a_capo = [], []
    for k, (pag, ini, ps) in enumerate(righe):
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro.append((pag, D(a)[pos], D(b)[pos]))
        if k + 1 < len(righe):
            pag2, ini2, ps2 = righe[k + 1]
            if pag2 == pag and not ini2 and ps and ps2 and pulita(ps[-1]) and pulita(ps2[0]):
                a_capo.append((pag, D(ps[-1])[pos], D(ps2[0])[pos]))
    return dentro, a_capo


def eccesso(cc, rnd):
    vero = misure.informazione_mutua([(a, b) for _, a, b in cc])
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(cc):
        per[p].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        sec = [b for _, _, b in cc]
        for idx in per.values():
            x = [sec[i] for i in idx]
            rnd.shuffle(x)
            for i, y in zip(idx, x):
                sec[i] = y
        nulli.append(misure.informazione_mutua([(a, s) for (_, a, _), s in zip(cc, sec)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('im', vero), ('nullo', m), ('eccesso', vero - m), ('z', (vero - m) / s if s else None), ('n', len(cc))])


def misura(righe, quale, rnd):
    d, a = coppie(righe, quale)
    d, a = eccesso(d, rnd), eccesso(a, rnd)
    return OrderedDict([('dentro', d), ('a_capo', a), ('R', a['eccesso'] / d['eccesso'] if d['eccesso'] > 0 else None)])


def main():
    rnd = random.Random(SEME)
    rv = e186.righe_voynich()
    ris = OrderedDict()
    ris['Voynich F1'] = misura(rv, 'F1', rnd)
    ris['Voynich I1'] = misura(rv, 'I1', rnd)
    ris['controllo: latino nelle iniziali, I1'] = misura(e186.nascondi(rv, False), 'I1', rnd)
    for n, r in ris.items():
        print('%-40s dentro %.4f (z %.0f) | a capo %.4f (z %.1f) | R %s' % (n, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['a_capo']['eccesso'],
              r['a_capo']['z'] or 0, '%.2f' % r['R'] if r['R'] is not None else '-'), flush=True)
    valido = (ris['controllo: latino nelle iniziali, I1']['R'] or 0) >= 0.5
    f = ris['Voynich F1']
    za = f['a_capo']['z'] or 0
    esito = 'messaggio' if (f['R'] or 0) >= 0.5 and za > 4 else ('abitudini di pagina e riga' if za < 2 else 'misto')
    ris['valido'], ris['esito_F1'] = valido, esito
    print('valido %s | F1: %s' % (valido, esito))
    with open(os.path.join(RISULTATI, 'e186c_finali_pagina.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e186c — Finali di parole vicine attraverso l\'a capo, con nullo dentro la pagina', '', 'Preregistrazione: `preregistrazioni/e186c.md`.', '',
           '| | dentro la riga | attraverso l\'a capo | R |', '|---|---|---|---|']
    for n, r in ris.items():
        if isinstance(r, dict) and 'R' in r:
            out.append('| %s | %.4f (z %.0f) | %.4f (z %.1f) | %s |' % (n, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['a_capo']['eccesso'], r['a_capo']['z'] or 0,
                                                                   '%.2f' % r['R'] if r['R'] is not None else '–'))
    out += ['', 'Controllo valido: **%s**. Finali (F1): **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e186c_finali_pagina.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
