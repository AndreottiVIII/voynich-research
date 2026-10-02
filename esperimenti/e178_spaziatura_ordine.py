# -*- coding: utf-8 -*-
"""Esperimento 178: spaziatura relativa (spazio fra parole / larghezza tipica di un segno, corretta per la
composizione) per bifoglio, nell'ordine ricostruito contro rilegatura e ordini casuali.

Preregistrazione: preregistrazioni/e178.md. Scrive risultati/e178_spaziatura_ordine.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from scipy.optimize import nnls

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154
import e154b_ordine_normalizzato as e154b
import e173_dimensione_scrittura as e173

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, CASUALI = 178, 1000
D = e173.D


def per_foglio():
    fogli = sorted(f[:-3] for f in os.listdir(e34.RIQUADRI) if f.endswith('.js'))
    dati = {}
    righe_A, b = [], []
    for pag in fogli:
        rq = e34.riquadri(pag)
        if not rq:
            continue
        m = statistics.median(t['w'] for t in rq if t['w'] > 0)
        dati[pag] = (rq, m)
        for t in rq:
            if t['w'] > 0 and trascrizione.pulita(t['parola']):
                righe_A.append(Counter(D(t['parola'])))
                b.append(t['w'] / m)
    unita = sorted({u for c in righe_A for u in c})
    idx = {u: i for i, u in enumerate(unita)}
    A = np.zeros((len(righe_A), len(unita) + 1))
    for r, c in enumerate(righe_A):
        for u, n in c.items():
            A[r, idx[u]] = n
        A[r, -1] = 1
    coef, _ = nnls(A, np.array(b))
    media_u = float(np.mean([coef[idx[u]] for u in unita if coef[idx[u]] > 0]))
    out = defaultdict(list)
    for pag, (rq, m) in dati.items():
        f = e148.foglio(pag)
        if f is None:
            continue
        seg, spazi = [], []
        for t in rq:
            if t['w'] > 0 and trascrizione.pulita(t['parola']):
                att = coef[-1] + sum(coef[idx[u]] * n for u, n in Counter(D(t['parola'])).items() if u in idx)
                if att > 0:
                    seg.append(t['w'] / (att / media_u))
        for a, c in zip(rq, rq[1:]):
            if a['riga'] == c['riga']:
                g = c['x'] - (a['x'] + a['w'])
                if g >= 0:
                    spazi.append(g)
        if len(seg) >= 30 and len(spazi) >= 30:
            out[f].append(statistics.median(spazi) / statistics.median(seg))
    return {f: statistics.mean(v) for f, v in out.items()}


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    F = per_foglio()
    C = {}
    for n in U:
        vv = [F[int(x[1:])] for x in n.split('-') if int(x[1:]) in F]
        if vv:
            C[n] = [statistics.mean(vv)]
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
    conferma = bool(r_r < r_l and p < 0.05)
    ris = OrderedDict([('fogli', len(F)), ('unita', len(C)), ('gruppi', {('%s/%s' % k): len(v) for k, v in gruppi.items()}), ('ricostruito', r_r), ('p_ricostruito', p),
                       ('rilegatura', r_l), ('p_rilegatura', p_l), ('casuali_media', statistics.mean(cas)), ('conferma', conferma)])
    print('fogli %d unità %d gruppi %s | ricostruito %.3f (p %.3f) | rilegatura %.3f (p %.3f) | casuali %.3f | conferma %s' % (
        len(F), len(C), ris['gruppi'], r_r, p, r_l, p_l, statistics.mean(cas), conferma), flush=True)
    with open(os.path.join(RISULTATI, 'e178_spaziatura_ordine.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=float)
    out = ['# e178 — La spaziatura della mano nell\'ordine ricostruito dei bifogli', '',
           'Spaziatura relativa = mediana degli spazi fra parole / larghezza tipica di un segno (corretta per la composizione). Preregistrazione: `preregistrazioni/e178.md`.', '',
           '| | ricostruito | rilegatura | casuali (media) |', '|---|---|---|---|',
           '| distanza fra unità consecutive (p) | %.3f (%.3f) | %.3f (%.3f) | %.3f |' % (r_r, p, r_l, p_l, statistics.mean(cas)), '',
           'Gruppi: %s. Conferma: **%s**.' % (', '.join('%s %d' % kv for kv in ris['gruppi'].items()), 'sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e178_spaziatura_ordine.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
