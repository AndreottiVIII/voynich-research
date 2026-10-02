# -*- coding: utf-8 -*-
"""Esperimento 195: larghezza fisica degli spazi certi fra coppie "spezzate" (a+b esiste come parola) contro le altre,
stratificata per giuntura; controllo con gli spazi dubbi dell'e34.

Preregistrazione: preregistrazioni/e195.md. Scrive risultati/e195_parole_spezzate.json e .md.
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
SEME = 195
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rnd = np.random.default_rng(SEME)
    freq = Counter(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))))
    spazi, fogli = e34.spazi_etichettati()
    certi = []
    controllo = []
    n_spezzate = 0
    for foglio, a, b, sep, larg in spazi:
        if not (trascrizione.pulita(a) and trascrizione.pulita(b)):
            continue
        strato = (D(a)[-1], D(b)[0])
        if sep == '.':
            spezzata = freq.get(a + b, 0) >= 2
            n_spezzate += spezzata
            certi.append((strato, 1 if spezzata else 0, larg))
        controllo.append((strato, 1 if sep == ',' else 0, larg))
    r = e34.differenza_stratificata(certi, rnd)
    c = e34.differenza_stratificata(controllo, rnd)
    valido = c['differenza'] > 0 and c['p_una_coda'] < 0.01
    esito = 'test non valido' if not valido else ('spazi spuri' if r['differenza'] > 0 and r['p_una_coda'] < 0.01 else ('spazi normali' if r['p_una_coda'] > 0.05 else 'incerto'))
    ris = OrderedDict([('fogli', fogli), ('spazi_certi', len(certi)), ('coppie_spezzate', n_spezzate), ('spezzate_contro_normali', r), ('controllo_dubbi_contro_certi', c),
                       ('valido', valido), ('esito', esito)])
    print('spazi certi %d, spezzate %d | normali − spezzate %.3f (z %.1f, p %.4f, strati %d) | controllo dubbi %.3f (z %.1f, p %.4f) | %s' % (
        len(certi), n_spezzate, r['differenza'], r['z'], r['p_una_coda'], r['strati'], c['differenza'], c['z'], c['p_una_coda'], esito), flush=True)
    with open(os.path.join(RISULTATI, 'e195_parole_spezzate.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e195 — Le "parole spezzate" hanno spazi più stretti?', '', 'Larghezza degli spazi certi (normalizzata), stratificata per giuntura. Preregistrazione: `preregistrazioni/e195.md`.', '',
           '| confronto | casi (strati) | differenza | z | p |', '|---|---|---|---|---|',
           '| normali − spezzate (spazi certi; %d spezzate) | %d (%d) | %.3f | %.1f | %.4f |' % (n_spezzate, r['casi'], r['strati'], r['differenza'], r['z'], r['p_una_coda']),
           '| controllo: certi − dubbi | %d (%d) | %.3f | %.1f | %.4f |' % (c['casi'], c['strati'], c['differenza'], c['z'], c['p_una_coda']), '',
           'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e195_parole_spezzate.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
