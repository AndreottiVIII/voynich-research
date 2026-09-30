# -*- coding: utf-8 -*-
"""Esperimento 31: il Naibbe con preferenze fra le tabelle che derivano lentamente.

A ogni riga nuova (8 parole) i logaritmi dei pesi delle sei tabelle del Naibbe fanno un
passo di una passeggiata casuale che torna verso zero: z <- rho*z + N(0, sigma^2).
Griglia sigma x rho dichiarata; misure dell'e10.

Preregistrazione: preregistrazioni/e31.md. Scrive risultati/e31_naibbe_deriva.json e .md.
"""
import json, math, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
from e10_naibbe import NAIBBE, completa, N, pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SIGMA = (0.1, 0.3, 0.6, 1.0)
RHO = (0.90, 0.98)
PAROLE_RIGA = misure.PAROLE_RIGA


def naibbe_deriva(lettere, glifi, rnd, sigma, rho):
    """Naibbe con pesi delle tabelle che derivano riga per riga (una riga = PAROLE_RIGA parole)."""
    unigrammi = {g for c, g in glifi.items() if c.startswith('unigram_')}
    tabelle = generatori.NAIBBE_TABELLE
    base = [generatori.NAIBBE_PESI[t] for t in tabelle]
    pezzi, i = [], 0
    while i < len(lettere):
        if i == len(lettere) - 1 or rnd.random() < 17 / 36:
            pezzi.append(lettere[i])
            i += 1
        else:
            pezzi.append(lettere[i:i + 2])
            i += 2
    z = [0.0] * len(tabelle)
    pesi = base[:]
    parole = []
    for pezzo in pezzi:
        if len(parole) % PAROLE_RIGA == 0:
            z = [rho * x + rnd.gauss(0, sigma) for x in z]
            pesi = [b * math.exp(x) for b, x in zip(base, z)]
        pesca = lambda: rnd.choices(tabelle, weights=pesi)[0]
        if len(pezzo) == 1:
            parole.append(glifi['unigram_%s_%s' % (pesca(), pezzo)])
        else:
            for _ in range(50):
                w = glifi['prefix_%s_%s' % (pesca(), pezzo[0])] + glifi['suffix_%s_%s' % (pesca(), pezzo[1])]
                if w not in unigrammi:
                    break
            parole.append(w)
    return parole


def main():
    glifi_div = misure.divisore(misure.GLIFI_EVA)
    glifi = generatori.naibbe_tabelle(os.path.join(NAIBBE, 'references', 'naibbe_tables.csv'))
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    ris = OrderedDict()
    ris['Voynich (pagine e righe vere)'] = completa(pagine_voynich(corrente), glifi_div)
    testi = [('Bibbia latina', lingue.parole('Latin')), ('Vitruvio', lingue.genere('Vitruvio, architettura'))]
    for nome, parole in testi:
        lettere = ''.join(generatori.naibbe_pulisci(p) for p in parole[:14000])
        for rho in RHO:
            for sigma in SIGMA:
                cifrato = naibbe_deriva(lettere, glifi, random.Random(31), sigma, rho)[:N]
                chiave = '%s: deriva sigma %.1f, rho %.2f' % (nome, sigma, rho)
                ris[chiave] = completa(misure.pagine_finte(cifrato), glifi_div)
                r = ris[chiave]
                print('%-44s ident x%.2f somigl %.1f%%/%.1f%%/%.1f%% confine %.3f hapax %.2f h2 %.2f' % (
                    chiave, r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'],
                    100 * r['somiglianza_6_righe'], r['im_confine_eccesso'], r['hapax'], r['h2']), flush=True)
    with open(os.path.join(RISULTATI, 'e31_naibbe_deriva.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e31 — Naibbe con preferenze che derivano riga per riga', '',
           'Logaritmi dei pesi delle sei tabelle: z ← ρ·z + N(0, σ²) a ogni riga di 8 parole. Misure dell\'e10. '
           'Preregistrazione: `preregistrazioni/e31.md`.', '',
           '| testo | h2 | hapax | identiche subito | somiglianza: riga | riga sotto | 6 righe | confine |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %.2f | %.2f | ×%.2f | %.1f%% | %.1f%% | %.1f%% | %.3f |' % (
            nome, r['h2'], r['hapax'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'],
            100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe'], r['im_confine_eccesso']))
    with open(os.path.join(RISULTATI, 'e31_naibbe_deriva.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
