# -*- coding: utf-8 -*-
"""Esperimento 64: il soggetto della pagina. La parola d'apertura di una pagina d'erbario ritorna
nella stessa pagina piu' di una parola qualsiasi della pagina di lunghezza simile?

Controllo positivo: Culpeper, Complete Herbal (titolo della voce = nome della pianta).
Preregistrazione: preregistrazioni/e64.md. Scrive risultati/e64_soggetto_pagina.json e .md.
"""
import json, os, random, re, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e22_timm_schinner as e22
from e58_parola_sopra import da_file

RISULTATI = os.path.join(QUI, '..', 'risultati')
CULPEPER = os.path.join(lingue.SORGENTI, 'voynich-units', 'herbal', 'culpeper_en.txt')
D = misure.divisore(misure.GLIFI_EVA)
ESTRAZIONI, PAROLE_PAGINA, VICINO = 200, 170, 0.25


def pagine_voynich_erbario(lingua=None):
    """[(apertura, resto)] per le pagine d'erbario: prima parola del primo paragrafo."""
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione='H', lingua=lingua):
        per.setdefault(r.pagina, []).extend(p for p in r.parole if trascrizione.pulita(p))
    return [(ps[0], ps[1:]) for ps in per.values() if len(ps) > 10]


def voci_culpeper():
    testo = open(CULPEPER, encoding='utf-8', errors='replace').read()
    # le voci dell'erbario: un titolo rientrato in maiuscolo, poi "_Descript._]"
    pezzi = re.split(r'\n {2,}([A-Z][A-Z\' ,-]{2,})\.?\s*\n', testo)
    out = []
    for i in range(1, len(pezzi) - 1, 2):
        titolo, corpo = pezzi[i], pezzi[i + 1]
        if '_Descript._' not in corpo[:400]:
            continue
        testa = lingue.normalizza(titolo).split()
        parole = lingue.normalizza(corpo).split()[:PAROLE_PAGINA]
        if testa and len(parole) > 20:
            out.append((testa[-1], parole))
    return out


def pagine_generatore(seme):
    out = []
    for p in da_file(os.path.join(e22.LAVORO, 'seme_%d' % seme, 'generate', 'generated_text.txt')):
        ps = [w for r in p for w in r][:PAROLE_PAGINA + 1]
        if len(ps) > 10:
            out.append((ps[0], ps[1:]))
    return out


def ritorna(w, resto, dividi, vicino):
    if not vicino:
        return w in resto
    u = tuple(dividi(w)) if dividi else tuple(w)
    return any(misure._dist_norm(u, tuple(dividi(x)) if dividi else tuple(x)) <= VICINO for x in resto)


def prova(pagine, dividi, vicino, seme=64):
    lung = (lambda w: len(dividi(w))) if dividi else len
    oss = np.mean([ritorna(a, resto, dividi, vicino) for a, resto in pagine])
    rnd = random.Random(seme)
    nulle = []
    for _ in range(ESTRAZIONI):
        vals = []
        for a, resto in pagine:
            simili = [i for i, x in enumerate(resto) if abs(lung(x) - lung(a)) <= 1] or list(range(len(resto)))
            i = rnd.choice(simili)
            vals.append(ritorna(resto[i], resto[:i] + resto[i + 1:], dividi, vicino))
        nulle.append(np.mean(vals))
    nulle = np.array(nulle)
    return {'pagine': len(pagine), 'osservata': float(oss), 'caso': float(nulle.mean()),
            'rapporto': float(oss / nulle.mean()) if nulle.mean() else None,
            'p': float((1 + (nulle >= oss).sum()) / (1 + ESTRAZIONI))}


def main():
    testi = OrderedDict([('Voynich, erbario', (pagine_voynich_erbario(), D)),
                         ('Voynich, erbario A', (pagine_voynich_erbario('A'), D)),
                         ('Voynich, erbario B', (pagine_voynich_erbario('B'), D)),
                         ('Culpeper (controllo positivo)', (voci_culpeper(), None))])
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = (pagine_generatore(s), D)
    ris = OrderedDict()
    for nome, (pagine, dividi) in testi.items():
        ris[nome] = {'esatto': prova(pagine, dividi, False), 'vicino': prova(pagine, dividi, True)}
        e, v = ris[nome]['esatto'], ris[nome]['vicino']
        print('%-34s pagine %3d | esatto %.2f vs %.2f (x%s, p %.3f) | vicino %.2f vs %.2f (x%s, p %.3f)' % (
            nome, e['pagine'], e['osservata'], e['caso'], '%.2f' % e['rapporto'] if e['rapporto'] else '—', e['p'],
            v['osservata'], v['caso'], '%.2f' % v['rapporto'] if v['rapporto'] else '—', v['p']), flush=True)
    esempi = [a for a, _ in testi['Voynich, erbario'][0][:20]]
    ris['esempi_aperture_voynich'] = esempi
    ris['esempi_aperture_culpeper'] = [a for a, _ in testi['Culpeper (controllo positivo)'][0][:20]]
    with open(os.path.join(RISULTATI, 'e64_soggetto_pagina.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e64 — Il soggetto della pagina: la parola d\'apertura ritorna nella pagina?', '',
           'Quota di pagine in cui la parola d\'apertura ritorna nel resto della pagina (esatta, o vicina: distanza di '
           'edit ≤ %.2f), contro parole della stessa pagina di lunghezza simile (%d estrazioni). Pagine troncate a %d '
           'parole. Preregistrazione: `preregistrazioni/e64.md`.' % (VICINO, ESTRAZIONI, PAROLE_PAGINA), '',
           '| testo | pagine | esatto: apertura | caso | rapporto | p | vicino: apertura | caso | rapporto | p |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        e, v = r['esatto'], r['vicino']
        f_ = lambda x: '%.2f' % x if x else '—'
        out.append('| %s | %d | %.2f | %.2f | %s | %.3f | %.2f | %.2f | %s | %.3f |' % (
            nome, e['pagine'], e['osservata'], e['caso'], f_(e['rapporto']), e['p'], v['osservata'], v['caso'],
            f_(v['rapporto']), v['p']))
    out += ['', 'Prime aperture del Voynich: %s.' % ', '.join(esempi),
            'Prime aperture di Culpeper: %s.' % ', '.join(ris['esempi_aperture_culpeper'])]
    with open(os.path.join(RISULTATI, 'e64_soggetto_pagina.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
