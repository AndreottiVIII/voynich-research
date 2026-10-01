# -*- coding: utf-8 -*-
"""Esperimento 97: robustezza della chiusura della riga (e74) su IT, GC e per mano.

Preregistrazione: preregistrazioni/e97.md. Scrive risultati/e97_chiusura_robusta.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 97


def righe(quale='ZL', mano=None):
    return [(r.pagina, bool(r.inizio_par), list(r.parole))
            for r in trascrizione.testo_corrente(trascrizione.leggi(quale), mano=mano) if r.parole]


def main():
    prove = OrderedDict()
    prove['ZL'] = (righe('ZL'), e71.D)
    prove['IT'] = (righe('IT'), e71.D)
    prove['GC (un carattere per segno)'] = (righe('GC'), e71.lettere)
    for m in ('1', '2', '3'):
        prove['ZL, mano %s' % m] = (righe('ZL', m), e71.D)
    ris = OrderedDict()
    for nome, (rr, dv) in prove.items():
        rnd = random.Random(SEME)
        dentro, a_capo = e74.coppie(rr, dv)
        d, a = e74.eccesso(dentro, rnd), e74.eccesso(a_capo, rnd)
        R = a['eccesso'] / d['eccesso'] if d['eccesso'] > 0 else None
        ris[nome] = OrderedDict([('dentro', d), ('a_capo', a), ('R', R)])
        print('%-30s dentro %.4f (z %.0f, n %d) | a capo %.4f (z %.1f, n %d) | R %.3f' % (
            nome, d['eccesso'], d['z'] or 0, d['n'], a['eccesso'], a['z'] or 0, a['n'], R), flush=True)
    robusta = all(r['R'] is not None and r['R'] < 0.2 and (r['dentro']['z'] or 0) > 10 for k, r in ris.items() if k != 'ZL')
    ris['robusta'] = robusta
    print('robusta:', robusta)
    with open(os.path.join(RISULTATI, 'e97_chiusura_robusta.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e97 — La chiusura della riga regge in altre trascrizioni e per mano?', '',
           'R come nell\'e74. Preregistrazione: `preregistrazioni/e97.md`.', '',
           '| prova | dentro la riga (z) | attraverso l\'a capo (z) | R |', '|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %.4f (%.0f) | %.4f (%.1f) | %.3f |' % (k, r['dentro']['eccesso'], r['dentro']['z'] or 0,
                                                              r['a_capo']['eccesso'], r['a_capo']['z'] or 0, r['R']))
    out += ['', 'Robusta: **%s**.' % ('sì' if robusta else 'no')]
    with open(os.path.join(RISULTATI, 'e97_chiusura_robusta.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
