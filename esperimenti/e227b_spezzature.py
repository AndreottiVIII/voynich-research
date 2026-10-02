# -*- coding: utf-8 -*-
"""Esperimento 227b: una sola quota di parole spezzate riproduce insieme unioni (U/N0, U/N1, U/N2), legame e Q del
Voynich (e227)?

Preregistrazione: preregistrazioni/e227b.md. Scrive risultati/e227b_spezzature.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e227_unioni_e_legame as e227

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRIGLIA = [0.0, 0.06, 0.09, 0.12, 0.15, 0.20, 0.25]
BERSAGLI = OrderedDict([('U/N0', (1.92, 0.15)), ('U/N1', (1.29, 0.07)), ('U/N2', (1.16, 0.05)), ('legame', (0.188, 0.02)), ('Q', (0.67, 0.08))])
RIF_GENERATORE = {'U/N0': 1.29, 'legame': 0.107}     # e227, generatore e192 seme 1


def misura(pagine, rnd):
    a, b = e227.unioni(pagine, rnd), e227.legame(pagine)
    parole = [w for p in pagine for r in p for w in r]
    return OrderedDict([('U/N0', a['N0']['rapporto']), ('U/N1', a['N1']['rapporto']), ('U/N2', a['N2']['rapporto']),
                        ('legame', b['tutte']['eccesso']), ('Q', b['Q']),
                        ('lunghezza_media', sum(len(e227.D(w)) for w in parole) / len(parole)), ('parole', len(parole))])


def fuori(m):
    return [k for k, (v, t) in BERSAGLI.items() if abs(m[k] - v) > t]


def scarto(m):
    return sum(abs(m[k] - v) / t for k, (v, t) in BERSAGLI.items())


def main():
    e227.ESTRAZIONI = 50
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    attestate = set(trascrizione.parole(corrente))
    voy = trascrizione.parole(corrente)
    lung_voy = sum(len(e227.D(w)) for w in voy) / len(voy)
    base = e227.generatore_pagine(1)
    n_base = sum(len(r) for p in base for r in p)
    ris = OrderedDict()
    for i, s in enumerate(GRIGLIA):
        e227.QUOTA_SPEZZATE = s
        testo = e227.spezza(base, attestate, random.Random(227 + i))
        m = misura(testo, random.Random(227))
        m['quota_spezzate'] = (m['parole'] - n_base) / n_base
        m['fuori'] = fuori(m)
        ris['sigma %.2f' % s] = m
        print('sigma %.2f: %s fuori %s' % (s, ' '.join('%s %.3f' % (k, m[k]) for k in list(BERSAGLI) + ['lunghezza_media', 'quota_spezzate']), m['fuori']), flush=True)
    m0 = ris['sigma 0.00']
    valido = abs(m0['U/N0'] - RIF_GENERATORE['U/N0']) <= 0.03 and abs(m0['legame'] - RIF_GENERATORE['legame']) <= 0.005
    candidati = [s for s in GRIGLIA if not ris['sigma %.2f' % s]['fuori']]
    verifica = None
    if candidati:
        s = candidati[0]
        e227.QUOTA_SPEZZATE = s
        base2 = e227.generatore_pagine(2)
        m2 = misura(e227.spezza(base2, attestate, random.Random(2270)), random.Random(227))
        m2['fuori'] = fuori(m2)
        verifica = OrderedDict([('sigma', s), ('misure', m2)])
        print('verifica seme 2, sigma %.2f: fuori %s' % (s, m2['fuori']), flush=True)
    basta = bool(verifica) and not verifica['misure']['fuori']
    vicino = min(GRIGLIA, key=lambda s: (len(ris['sigma %.2f' % s]['fuori']), scarto(ris['sigma %.2f' % s])))
    esito = 'non valido' if not valido else ('un solo meccanismo basta (sigma %.2f)' % verifica['sigma'] if basta else
                                             'non basta (sigma piu\' vicino %.2f, fuori: %s)' % (vicino, ', '.join(ris['sigma %.2f' % vicino]['fuori']) or 'nessuna sul seme 1'))
    ris['lunghezza_media_voynich'] = lung_voy
    ris['verifica'] = verifica
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e227b_spezzature.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e227b — Una sola quota di parole spezzate per unioni, legame e Q?', '',
          'Generatore e192 (seme 1) con parole di almeno 4 unità spezzate in due parti attestate con probabilità σ. '
          'Preregistrazione: `preregistrazioni/e227b.md`.', '',
          '| σ | parole spezzate | U/N0 | U/N1 | U/N2 | legame | Q | lunghezza media | fuori tolleranza |', '|---|---|---|---|---|---|---|---|---|',
          '| **Voynich (bersaglio)** | | 1,92 ± 0,15 | 1,29 ± 0,07 | 1,16 ± 0,05 | 0,188 ± 0,02 | 0,67 ± 0,08 | %.2f | |' % lung_voy]
    for s in GRIGLIA:
        m = ris['sigma %.2f' % s]
        md.append('| %.2f | %.1f%% | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (s, 100 * m['quota_spezzate'], m['U/N0'], m['U/N1'], m['U/N2'],
                                                                                 m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    if verifica:
        m = verifica['misure']
        md.append('| verifica seme 2, σ %.2f | | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (verifica['sigma'], m['U/N0'], m['U/N1'], m['U/N2'],
                                                                                            m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e227b_spezzature.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
