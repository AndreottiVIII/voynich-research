# -*- coding: utf-8 -*-
"""Esperimento 186b: legame fra iniziali (I1) e finali (F1) di parole consecutive, dentro la riga e attraverso
l'a capo; controllo con latino nascosto nelle iniziali.

Preregistrazione: preregistrazioni/e186b.md. Scrive risultati/e186b_iniziali_a_capo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e74_legame_a_capo as e74
import e186_nulli_acrostici as e186

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 1862
D = e186.D


def coppie(righe, quale, togli=False):
    pulita = trascrizione.pulita
    pos = 0 if quale == 'I1' else -1
    dentro, a_capo = [], []
    for k, (pag, ini, ps) in enumerate(righe):
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro.append((D(a)[pos], D(b)[pos]))
        if k + 1 < len(righe):
            pag2, ini2, ps2 = righe[k + 1]
            if pag2 == pag and not ini2 and ps and ps2 and pulita(ps[-1]) and pulita(ps2[0]):
                u = D(ps2[0])
                if quale == 'I1':
                    secondo = u[1] if (togli and len(u) >= 3 and u[0] in ('y', 'd', 's')) else u[0]
                else:
                    secondo = u[-1]
                a_capo.append((D(ps[-1])[pos], secondo))
    return dentro, a_capo


def misura(righe, quale, rnd, togli=False):
    dentro, a_capo = coppie(righe, quale, togli)
    d, a = e74.eccesso(dentro, rnd), e74.eccesso(a_capo, rnd)
    R = a['eccesso'] / d['eccesso'] if d['eccesso'] > 0 else None
    return OrderedDict([('dentro', d), ('a_capo', a), ('R', R)])


def main():
    rnd = random.Random(SEME)
    rv = e186.righe_voynich()
    ris = OrderedDict()
    ris['Voynich I1'] = misura(rv, 'I1', rnd)
    ris['Voynich I1, tolto y/d/s'] = misura(rv, 'I1', rnd, togli=True)
    ris['Voynich F1'] = misura(rv, 'F1', rnd)
    ris['controllo: latino nelle iniziali, I1'] = misura(e186.nascondi(rv, False), 'I1', rnd)
    for n, r in ris.items():
        print('%-40s dentro %.4f (z %.0f) | a capo %.4f (z %.1f, n %d) | R %s' % (n, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['a_capo']['eccesso'],
              r['a_capo']['z'] or 0, r['a_capo']['n'], '%.2f' % r['R'] if r['R'] is not None else '-'), flush=True)
    c = ris['controllo: latino nelle iniziali, I1']
    valido = (c['R'] or 0) >= 0.5
    esiti = OrderedDict()
    for n in ('Voynich I1', 'Voynich F1'):
        r = ris[n]
        esiti[n] = ('messaggio' if (r['R'] or 0) >= 0.5 and (r['a_capo']['z'] or 0) > 4 else ('composizione di riga' if (r['R'] or 0) < 0.2 else 'misto'))
    ris['valido'], ris['esiti'] = valido, esiti
    print('valido %s | %s' % (valido, dict(esiti)))
    with open(os.path.join(RISULTATI, 'e186b_iniziali_a_capo.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e186b — Il legame fra iniziali (e finali) di parole vicine attraversa l\'a capo?', '',
           'Eccesso d\'informazione mutua dentro la riga e attraverso l\'a capo; R = attraverso / dentro. Preregistrazione: `preregistrazioni/e186b.md`.', '',
           '| | dentro la riga | attraverso l\'a capo | R |', '|---|---|---|---|']
    for n, r in ris.items():
        if isinstance(r, dict) and 'R' in r:
            out.append('| %s | %.4f (z %.0f) | %.4f (z %.1f) | %s |' % (n, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['a_capo']['eccesso'], r['a_capo']['z'] or 0,
                                                                   '%.2f' % r['R'] if r['R'] is not None else '–'))
    out += ['', 'Controllo valido: **%s**. Esiti: %s.' % ('sì' if valido else 'no', '; '.join('%s **%s**' % kv for kv in esiti.items()))]
    with open(os.path.join(RISULTATI, 'e186b_iniziali_a_capo.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
