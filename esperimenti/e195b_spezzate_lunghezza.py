# -*- coding: utf-8 -*-
"""Esperimento 195b: come l'e195, stratificando anche per lunghezza delle due parole.

Preregistrazione: preregistrazioni/e195b.md. Scrive risultati/e195b_spezzate_lunghezza.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e34_spazi_fisici as e34

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 1952
D = misure.divisore(misure.GLIFI_EVA)


def strato(a, b):
    return (D(a)[-1], D(b)[0], min(len(D(a)), 5), min(len(D(b)), 5))


def main():
    rnd = np.random.default_rng(SEME)
    freq = Counter(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))))
    spazi, _ = e34.spazi_etichettati()
    certi, controllo = [], []
    for foglio, a, b, sep, larg in spazi:
        if not (trascrizione.pulita(a) and trascrizione.pulita(b)):
            continue
        if sep == '.':
            certi.append((strato(a, b), 1 if freq.get(a + b, 0) >= 2 else 0, larg))
        controllo.append((strato(a, b), 1 if sep == ',' else 0, larg))
    r = e34.differenza_stratificata(certi, rnd)
    c = e34.differenza_stratificata(controllo, rnd)
    valido = c['differenza'] > 0 and c['p_una_coda'] < 0.01
    esito = 'test non valido' if not valido else ('spazi spuri' if r['differenza'] > 0 and r['p_una_coda'] < 0.01 else ('effetto della lunghezza' if r['p_una_coda'] > 0.05 else 'incerto'))
    ris = OrderedDict([('spezzate_contro_normali', r), ('controllo_dubbi_contro_certi', c), ('valido', valido), ('esito', esito)])
    print('normali − spezzate %.4f (z %.1f, p %.4f, casi %d, strati %d) | controllo %.4f (z %.1f, p %.4f, casi %d) | %s' % (
        r['differenza'], r['z'], r['p_una_coda'], r['casi'], r['strati'], c['differenza'], c['z'], c['p_una_coda'], c['casi'], esito), flush=True)
    with open(os.path.join(RISULTATI, 'e195b_spezzate_lunghezza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e195b — Parole spezzate a parità di lunghezza delle parole', '', 'Preregistrazione: `preregistrazioni/e195b.md`.', '',
           '| confronto | casi (strati) | differenza | z | p |', '|---|---|---|---|---|',
           '| normali − spezzate | %d (%d) | %.4f | %.1f | %.4f |' % (r['casi'], r['strati'], r['differenza'], r['z'], r['p_una_coda']),
           '| controllo: certi − dubbi | %d (%d) | %.4f | %.1f | %.4f |' % (c['casi'], c['strati'], c['differenza'], c['z'], c['p_una_coda']), '',
           'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e195b_spezzate_lunghezza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
