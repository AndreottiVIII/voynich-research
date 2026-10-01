# -*- coding: utf-8 -*-
"""Esperimento 74: il legame fra parole (ultimo segno -> primo segno) attraverso l'a capo, rispetto a
quello dentro la riga. Eccesso d'informazione mutua su 200 permutazioni.

Preregistrazione: preregistrazioni/e74.md. Scrive risultati/e74_legame_a_capo.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERMUTAZIONI, SEME, BLOCCO = 200, 74, 30
AGGIUNTI = {'y', 'd', 's', 'o'}


def righe_voynich(lingua=None):
    """(pagina, inizio paragrafo, parole)."""
    return [(r.pagina, bool(r.inizio_par), list(r.parole))
            for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua) if r.parole]


def coppie(righe, dividi, togli=False):
    pulita = trascrizione.pulita
    dentro, a_capo = [], []
    for k, (pag, inizio, ps) in enumerate(righe):
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro.append((dividi(a)[-1], dividi(b)[0]))
        if k + 1 < len(righe):
            pag2, inizio2, ps2 = righe[k + 1]
            if pag2 == pag and not inizio2 and ps and ps2 and pulita(ps[-1]) and pulita(ps2[0]):
                u = dividi(ps2[0])
                primo = u[1] if (togli and len(u) >= 3 and u[0] in AGGIUNTI) else u[0]
                a_capo.append((dividi(ps[-1])[-1], primo))
    return dentro, a_capo


def eccesso(cc, rnd):
    vera = misure.informazione_mutua(cc)
    primi = [a for a, _ in cc]
    secondi = [b for _, b in cc]
    nulli = []
    for _ in range(PERMUTAZIONI):
        rnd.shuffle(secondi)
        nulli.append(misure.informazione_mutua(list(zip(primi, secondi))))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('im', vera), ('nullo', m), ('eccesso', vera - m), ('z', (vera - m) / s if s else None), ('n', len(cc))])


def una(args):
    nome, righe, quale = args
    dividi = e71.lettere if quale == 'lettere' else e71.D
    rnd = random.Random(SEME)
    ris = OrderedDict()
    dentro, a_capo = coppie(righe, dividi)
    ris['dentro'] = eccesso(dentro, rnd)
    ris['a_capo'] = eccesso(a_capo, rnd)
    ris['R'] = ris['a_capo']['eccesso'] / ris['dentro']['eccesso'] if ris['dentro']['eccesso'] > 0 else None
    if quale != 'lettere':
        _, a_capo2 = coppie(righe, dividi, togli=True)
        ris['a_capo_senza_aggiunto'] = eccesso(a_capo2, rnd)
        ris['R_senza_aggiunto'] = (ris['a_capo_senza_aggiunto']['eccesso'] / ris['dentro']['eccesso']
                                   if ris['dentro']['eccesso'] > 0 else None)
    return nome, ris


def con_pagina(righe):
    return [(None, inizio, ps) for inizio, ps in righe]


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = (righe_voynich(), 'eva')
    t['Voynich A'] = (righe_voynich('A'), 'eva')
    t['Voynich B'] = (righe_voynich('B'), 'eva')
    for nome in ('Plinio, a capo', 'Plinio codificato, a capo', 'Naibbe, a capo'):
        t[nome] = (con_pagina(base[nome][0]), base[nome][1])
    naibbe = base['Naibbe, a capo'][0]
    rnd = random.Random(SEME)
    rimescolato = []
    for i in range(0, len(naibbe), BLOCCO):
        blocco = [ps for _, ps in naibbe[i:i + BLOCCO]]
        rnd.shuffle(blocco)
        rimescolato.extend((None, False, ps) for ps in blocco)
    t['controllo: Naibbe, righe rimescolate'] = (rimescolato, 'eva')
    for s in (19, 1, 2):
        nome = 'Timm e Schinner, seme %d' % s
        t[nome] = (con_pagina(base[nome][0]), 'eva')
    t['+ giunture (e23), seme 19'] = (con_pagina(e71.righe_file(os.path.join(e71.CACHE, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt'))), 'eva')
    t['modello e51, seme 19'] = (con_pagina(base['modello e51, seme 19'][0]), 'eva')
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in t.items()]):
            ris[nome] = r
            sa = r.get('a_capo_senza_aggiunto')
            print('%-40s dentro %.4f (z %.0f, n %d) | a capo %.4f (z %.1f, n %d) | R %s | senza aggiunto %s R %s' % (
                nome, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['dentro']['n'], r['a_capo']['eccesso'],
                r['a_capo']['z'] or 0, r['a_capo']['n'], '%.2f' % r['R'] if r['R'] is not None else '-',
                '%.4f (z %.1f)' % (sa['eccesso'], sa['z'] or 0) if sa else '-',
                '%.2f' % r['R_senza_aggiunto'] if r.get('R_senza_aggiunto') is not None else '-'), flush=True)
    with open(os.path.join(RISULTATI, 'e74_legame_a_capo.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e74 — Il legame attraverso l\'a capo', '',
           'Eccesso d\'informazione mutua (bit) fra ultimo segno di una parola e primo della successiva, rispetto a %d '
           'permutazioni; R = a capo / dentro la riga. Preregistrazione: `preregistrazioni/e74.md`.' % PERMUTAZIONI, '',
           '| testo | dentro la riga | attraverso l\'a capo | R | a capo, tolto y/d/s/o | R senza aggiunto |',
           '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        sa = r.get('a_capo_senza_aggiunto')
        out.append('| %s | %.4f (z %.0f) | %.4f (z %.1f) | %s | %s | %s |' % (
            nome, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['a_capo']['eccesso'], r['a_capo']['z'] or 0,
            '%.2f' % r['R'] if r['R'] is not None else '–', '%.4f (z %.1f)' % (sa['eccesso'], sa['z'] or 0) if sa else '–',
            '%.2f' % r['R_senza_aggiunto'] if r.get('R_senza_aggiunto') is not None else '–'))
    with open(os.path.join(RISULTATI, 'e74_legame_a_capo.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
