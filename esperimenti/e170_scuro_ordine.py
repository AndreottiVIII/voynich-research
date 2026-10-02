# -*- coding: utf-8 -*-
"""Esperimento 170: scuro medio, quota di intinte e autocorrelazione dello scuro (e166) per bifoglio, nell'ordine
ricostruito (e154b) contro rilegatura e ordini casuali.

Preregistrazione: preregistrazioni/e170.md. Scrive risultati/e170_scuro_ordine.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154
import e154b_ordine_normalizzato as e154b
import e166_intinte as e166

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, CASUALI = 170, 1000


def per_foglio():
    righe, P = e166.pagine()
    I = e166.intinte(P)
    acc = defaultdict(lambda: {'scuri': [], 'intinte': [], 'coppie': ([], [])})
    for pag, rr in P.items():
        f = e148.foglio(pag)
        if f is None:
            continue
        s = e166.sequenza(rr)
        m = statistics.mean(x for _, _, x in s)
        a = acc[f]
        a['scuri'] += [x for _, _, x in s]
        a['intinte'] += [I[(k, j)] for k, j, _ in s if (k, j) in I]
        a['coppie'][0].extend(x - m for _, _, x in s[:-1])
        a['coppie'][1].extend(x - m for _, _, x in s[1:])
    out = {}
    for f, a in acc.items():
        if len(a['scuri']) >= 30 and a['intinte']:
            out[f] = [statistics.mean(a['scuri']), sum(a['intinte']) / len(a['intinte']), float(np.corrcoef(*a['coppie'])[0, 1])]
    return out


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    F = per_foglio()
    C = {}
    for n in U:
        vv = [F[int(x[1:])] for x in n.split('-') if int(x[1:]) in F]
        if vv:
            C[n] = [statistics.mean(v[i] for v in vv) for i in range(3)]
    gruppi = defaultdict(list)
    for n, u in U.items():
        if n in C:
            gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = {k: v for k, v in gruppi.items() if len(v) >= 6}
    tot_r = tot_l = 0.0
    pesi = 0
    casuali = [0.0] * CASUALI
    for k, nomi in gruppi.items():
        X = e154.standardizza({n: C[n] for n in nomi})
        vett = {n: Counter(e154b.normalizza(w) for ps in U[n]['righe'] for w in ps) for n in nomi}
        S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
        ric = [nomi[i] for i in e150.ricostruisci(S)]
        ril = sorted(nomi, key=lambda n: U[n]['primo'])
        w = len(nomi) - 1
        tot_r += w * e154.distanza(ric, X)
        tot_l += w * e154.distanza(ril, X)
        pesi += w
        for i in range(CASUALI):
            o = nomi[:]
            rnd.shuffle(o)
            casuali[i] += w * e154.distanza(o, X)
    r_r, r_l = tot_r / pesi, tot_l / pesi
    cas = [x / pesi for x in casuali]
    p = sum(x <= r_r for x in cas) / CASUALI
    p_l = sum(x <= r_l for x in cas) / CASUALI
    conferma = r_r < r_l and p < 0.05
    ris = OrderedDict([('fogli', len(F)), ('unita', len(C)), ('gruppi', {('%s/%s' % k): len(v) for k, v in gruppi.items()}), ('ricostruito', r_r), ('p_ricostruito', p),
                       ('rilegatura', r_l), ('p_rilegatura', p_l), ('casuali_media', statistics.mean(cas)), ('conferma_fisica', conferma)])
    print('fogli %d, unità %d, gruppi %s | ricostruito %.3f (p %.3f) | rilegatura %.3f (p %.3f) | casuali %.3f | conferma %s' % (
        len(F), len(C), ris['gruppi'], r_r, p, r_l, p_l, statistics.mean(cas), conferma), flush=True)
    with open(os.path.join(RISULTATI, 'e170_scuro_ordine.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e170 — Lo scuro dell\'inchiostro nell\'ordine ricostruito dei bifogli', '',
           'Misure per unità: scuro medio, quota di intinte, autocorrelazione dello scuro (e166). Preregistrazione: `preregistrazioni/e170.md`.', '',
           '| | ricostruito | rilegatura | casuali (media) |', '|---|---|---|---|',
           '| distanza fra unità consecutive (p) | %.3f (%.3f) | %.3f (%.3f) | %.3f |' % (r_r, p, r_l, p_l, statistics.mean(cas)), '',
           'Gruppi: %s. Conferma fisica: **%s**.' % (', '.join('%s %d' % kv for kv in ris['gruppi'].items()), 'sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e170_scuro_ordine.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
