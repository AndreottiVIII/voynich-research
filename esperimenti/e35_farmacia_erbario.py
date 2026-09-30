# -*- coding: utf-8 -*-
"""Esperimento 35: l'etichetta di un frammento di farmacia richiama la pagina d'erbario
della stessa pianta?

Coppie da dati/corrispondenze_farmacia.json (associazione fatta sulle immagini prima di
questo confronto). Per ogni coppia: distanza di edit normalizzata minima fra l'etichetta e
le parole del testo in paragrafi di ciascuna pagina d'erbario; rango della pagina giusta;
quantile q = (rango - 0,5) / pagine. Statistica: media di q; nulla: medie di quantili
uniformi indipendenti (100.000, seme fisso).

Preregistrazione: preregistrazioni/e35.md. Scrive risultati/e35_farmacia_erbario.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
COPPIE = os.path.join(QUI, '..', 'dati', 'corrispondenze_farmacia.json')
DIVIDI = misure.divisore(misure.GLIFI_EVA)
SIMULAZIONI = 100_000


def pagine_erbario():
    pagine = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione='H'):
        for p in r.parole:
            if trascrizione.pulita(p):
                pagine.setdefault(r.pagina, []).append(p)
    return pagine


def distanza_minima(etichetta, parole):
    e = tuple(DIVIDI(etichetta))
    return min(misure._dist_norm(e, tuple(DIVIDI(p))) for p in parole)


def quantile(etichetta, giusta, pagine):
    d = {pag: distanza_minima(etichetta, ps) for pag, ps in pagine.items()}
    x = d[giusta]
    meglio = sum(1 for v in d.values() if v < x)
    pari = sum(1 for v in d.values() if v == x)
    rango = meglio + (pari + 1) / 2
    return {'distanza': x, 'rango': rango, 'pagine': len(d), 'q': (rango - 0.5) / len(d),
            'pagine_piu_vicine': [p for p, _ in sorted(d.items(), key=lambda kv: kv[1])[:3]]}


def p_media(qs, rnd):
    medie = rnd.random((SIMULAZIONI, len(qs))).mean(axis=1)
    return float((1 + (medie <= np.mean(qs)).sum()) / (1 + SIMULAZIONI))


def main():
    coppie = json.load(open(COPPIE, encoding='utf-8'))['coppie']
    pagine = pagine_erbario()
    tutte_parole = Counter(p for ps in pagine.values() for p in set(ps))
    rnd = np.random.default_rng(35)
    righe_ris = []
    for c in coppie:
        r = quantile(c['etichetta'], c['erbario'], pagine)
        r.update({k: c[k] for k in ('erbario', 'farmacia', 'etichetta', 'incerta')})
        r['identica_nella_pagina'] = c['etichetta'] in pagine[c['erbario']]
        r['pagine_che_la_contengono'] = tutte_parole[c['etichetta']]
        righe_ris.append(r)
        print('%-6s %-12s %-9s dist %.3f rango %5.1f/%d q %.3f identica %s (in %d pagine)  vicine %s' % (
            c['erbario'], c['farmacia'], c['etichetta'], r['distanza'], r['rango'], r['pagine'], r['q'],
            r['identica_nella_pagina'], r['pagine_che_la_contengono'], r['pagine_piu_vicine']))
    tutte = [r['q'] for r in righe_ris]
    certe = [r['q'] for r in righe_ris if not r['incerta']]
    ris = {'coppie': righe_ris, 'pagine_erbario': len(pagine),
           'tutte': {'n': len(tutte), 'media_q': float(np.mean(tutte)), 'p': p_media(tutte, rnd)},
           'senza_punto_interrogativo': {'n': len(certe), 'media_q': float(np.mean(certe)), 'p': p_media(certe, rnd)}}
    print('tutte: media q %.3f p %.4f | senza ?: media q %.3f p %.4f' % (
        ris['tutte']['media_q'], ris['tutte']['p'], ris['senza_punto_interrogativo']['media_q'],
        ris['senza_punto_interrogativo']['p']))
    with open(os.path.join(RISULTATI, 'e35_farmacia_erbario.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ["# e35 — L'etichetta del frammento di farmacia e la pagina d'erbario della stessa pianta", '',
             "Per ogni coppia: distanza di edit minima fra l'etichetta e le parole della pagina d'erbario "
             "(segni composti fusi); rango della pagina giusta fra le %d pagine d'erbario; q = (rango − 0,5) / "
             "pagine. Sotto l'ipotesi nulla q è uniforme. Preregistrazione: `preregistrazioni/e35.md`; "
             "associazione: `dati/corrispondenze_farmacia.json`." % len(pagine), '',
             "| erbario | farmacia | etichetta | incerta | distanza | rango | q | identica nella pagina | pagine che la contengono |",
             '|---|---|---|---|---|---|---|---|---|']
    for r in righe_ris:
        righe.append('| %s | %s | %s | %s | %.3f | %.1f | %.3f | %s | %d |' % (
            r['erbario'], r['farmacia'], r['etichetta'], 'sì' if r['incerta'] else 'no', r['distanza'],
            r['rango'], r['q'], 'sì' if r['identica_nella_pagina'] else 'no', r['pagine_che_la_contengono']))
    righe += ['', 'Media di q: tutte le coppie %.3f (n = %d, p = %.3f); solo senza "?" %.3f (n = %d, p = %.3f).' % (
        ris['tutte']['media_q'], ris['tutte']['n'], ris['tutte']['p'],
        ris['senza_punto_interrogativo']['media_q'], ris['senza_punto_interrogativo']['n'],
        ris['senza_punto_interrogativo']['p'])]
    with open(os.path.join(RISULTATI, 'e35_farmacia_erbario.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
