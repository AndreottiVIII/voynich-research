# -*- coding: utf-8 -*-
"""Esperimento 90: evitamento fra inizi di riga per mano (scriba).

Preregistrazione: preregistrazioni/e90.md. Scrive risultati/e90_evitamento_mani.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e83_evitamento_inizi as e83

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 90
MANI = ('1', '2', '3')


def pagine_mano(mano):
    per = OrderedDict()
    par = 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), mano=mano):
        if not r.parole:
            continue
        if r.inizio_par:
            par += 1
        w = r.parole[0] if trascrizione.pulita(r.parole[0]) else None
        per.setdefault(r.pagina, []).append((par, bool(r.inizio_par), w))
    return per


def main():
    ris = OrderedDict()
    for m in MANI:
        r = e83.misura(pagine_mano(m), 1, e83.primo_eva, random.Random(SEME))
        ris['mano %s' % m] = r
        e83.riga('mano %s' % m, r)
    tutte = [ris['mano %s' % m] for m in MANI]
    comune = all(r['S'] < 0.8 and r['z'] < -3 for r in tutte)
    scriba = any(r['S'] >= 0.9 and abs(r['z']) < 2 for r in tutte) and any(r['S'] < 0.7 and r['z'] < -3 for r in tutte)
    ris['lettura'] = 'proprietà comune' if comune else 'abitudine di scriba' if scriba else 'misto'
    print('lettura:', ris['lettura'])
    with open(os.path.join(RISULTATI, 'e90_evitamento_mani.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e90 — L\'evitamento fra inizi di riga dipende dallo scriba?', '',
           'S(1) dell\'e83 per mano (variabile $H di ZL). Preregistrazione: `preregistrazioni/e90.md`.', '',
           '| mano | coppie | osservata | attesa | S | z |', '|---|---|---|---|---|---|']
    for m in MANI:
        r = ris['mano %s' % m]
        out.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (m, r['n'], r['osservata'], r['attesa'], r['S'], r['z']))
    out += ['', 'Lettura: **%s**.' % ris['lettura']]
    with open(os.path.join(RISULTATI, 'e90_evitamento_mani.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
