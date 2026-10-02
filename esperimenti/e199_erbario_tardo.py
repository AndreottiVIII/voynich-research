# -*- coding: utf-8 -*-
"""Esperimento 199: le pagine d'erbario tarde (f87-f96, mano 1 / lingua A) somigliano di piu' alla farmacia o
all'erbario iniziale?

Preregistrazione: preregistrazioni/e199.md. Scrive risultati/e199_erbario_tardo.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e148_bifogli as e148
import e154b_ordine_normalizzato as e154b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 199, 2000


def main():
    rnd = random.Random(SEME)
    var = e148.variabili_pagine()
    voc = defaultdict(Counter)
    sez = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        voc[r.pagina].update(e154b.normalizza(w) for w in r.parole if trascrizione.pulita(w))
        sez[r.pagina] = r.sezione
    ok = lambda p: p in var and var[p].get('H') == '1' and var[p].get('L') == 'A' and sum(voc[p].values()) >= 30
    gruppi = {'iniziale': [], 'tardo': [], 'farmacia': []}
    for p in voc:
        f = e148.foglio(p)
        if f is None or not ok(p):
            continue
        if sez[p] == 'H' and f <= 57:
            gruppi['iniziale'].append(p)
        elif sez[p] == 'H' and 87 <= f <= 96:
            gruppi['tardo'].append(p)
        elif sez[p] == 'P':
            gruppi['farmacia'].append(p)
    rif = gruppi['iniziale'] + gruppi['farmacia']
    S = {t: {r: e148.coseno(voc[t], voc[r]) for r in rif} for t in gruppi['tardo']}

    def stat(farm):
        ds = []
        for t in gruppi['tardo']:
            a = [S[t][r] for r in rif if r in farm]
            b = [S[t][r] for r in rif if r not in farm]
            ds.append(statistics.mean(a) - statistics.mean(b))
        return statistics.mean(ds), ds
    vero, ds = stat(set(gruppi['farmacia']))
    nulli = []
    for _ in range(PERMUTAZIONI):
        x = rif[:]
        rnd.shuffle(x)
        nulli.append(stat(set(x[:len(gruppi['farmacia'])]))[0])
    p = (1 + sum(abs(n) >= abs(vero) for n in nulli)) / (1 + PERMUTAZIONI)
    esito = 'vocabolario del tempo' if vero > 0 and p < 0.01 else ('vocabolario dell\'illustrazione' if vero < 0 and p < 0.01 else 'nessuna preferenza')
    ris = OrderedDict([('pagine', {k: len(v) for k, v in gruppi.items()}), ('statistica', vero), ('pagine_tarde_piu_vicine_alla_farmacia', sum(d > 0 for d in ds)),
                       ('nullo_media', statistics.mean(nulli)), ('p_due_code', p), ('esito', esito)])
    print('pagine %s | farmacia − iniziale %.4f (nullo %.4f) p %.4f | tarde più vicine alla farmacia %d/%d | %s' % (
        ris['pagine'], vero, statistics.mean(nulli), p, ris['pagine_tarde_piu_vicine_alla_farmacia'], len(ds), esito), flush=True)
    with open(os.path.join(RISULTATI, 'e199_erbario_tardo.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e199 — L\'erbario tardo parla come l\'erbario o come la farmacia?', '', 'Mano 1, lingua A. Preregistrazione: `preregistrazioni/e199.md`.', '',
           '| pagine (iniziale / tarde / farmacia) | farmacia − iniziale | nullo | p | tarde più vicine alla farmacia |', '|---|---|---|---|---|',
           '| %d / %d / %d | %.4f | %.4f | %.4f | %d/%d |' % (len(gruppi['iniziale']), len(gruppi['tardo']), len(gruppi['farmacia']), vero, statistics.mean(nulli), p,
                                                           ris['pagine_tarde_piu_vicine_alla_farmacia'], len(ds)), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e199_erbario_tardo.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
