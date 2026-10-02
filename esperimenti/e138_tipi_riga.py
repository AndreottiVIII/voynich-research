# -*- coding: utf-8 -*-
"""Esperimento 138: tipi di riga (k-medie sui profili di segni delle parole interne) e posizione della riga nel
paragrafo, contro il rimescolamento dell'ordine delle righe nel paragrafo.

Preregistrazione: preregistrazioni/e138.md. Scrive risultati/e138_tipi_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, KK = 138, 1000, (4, 3, 6)
D = misure.divisore(misure.GLIFI_EVA)
CLASSI = ['B', 'G', 'q', 'e', 'o', 'a', 'y', 'd', 'l', 'r', 's', 'in', 'altro']
MAPPA = {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'cph': 'B', 'cfh': 'B', 'k': 'G', 't': 'G', 'p': 'G', 'f': 'G',
         'i': 'in', 'n': 'in'}


def paragrafi_voynich():
    out, cur, pag = [], [], None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        if r.inizio_par or r.pagina != pag:
            if cur:
                out.append(cur)
            cur, pag = [], r.pagina
        cur.append(list(r.parole))
    if cur:
        out.append(cur)
    return out


def paragrafi_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    out, cur = [], []
    for i, (ini, ps) in enumerate(rr):
        if ini or i % 29 == 0:
            if cur:
                out.append(cur)
            cur = []
        cur.append(ps)
    if cur:
        out.append(cur)
    return out


def profilo(ps):
    c = Counter()
    for w in ps[1:-1]:
        for g in D(w):
            c[MAPPA.get(g, g if g in CLASSI else 'altro')] += 1
    n = sum(c.values())
    return [c[k] / n for k in CLASSI] if n else None


def righe_utili(pars):
    """-> lista di paragrafi, ciascuno lista di (posizione, profilo) dalla 2a riga; solo paragrafi di almeno 4 righe."""
    out = []
    for p in pars:
        if len(p) < 4:
            continue
        rr = []
        for j, ps in enumerate(p[1:], start=1):
            if len(ps) >= 4 and all(trascrizione.pulita(w) for w in ps):
                pos = '2a' if j == 1 else '3a' if j == 2 else 'ultima' if j == len(p) - 1 else 'centrale'
                pr = profilo(ps)
                if pr:
                    rr.append((pos, pr))
        if len(rr) >= 2:
            out.append(rr)
    return out


def kmedie(X, k):
    migliore = None
    for s in range(1, 11):
        rng = np.random.default_rng(s)
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(100):
            d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)
            e = d.argmin(1)
            nuovo = np.array([X[e == j].mean(0) if (e == j).any() else C[j] for j in range(k)])
            if np.allclose(nuovo, C):
                break
            C = nuovo
        sse = ((X - C[e]) ** 2).sum()
        if migliore is None or sse < migliore[0]:
            migliore = (sse, e)
    return migliore[1]


def valuta(pars, rnd):
    rr = righe_utili(pars)
    X = np.array([pr for p in rr for _, pr in p])
    X = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1)
    out = OrderedDict([('paragrafi', len(rr)), ('righe', len(X))])
    for k in KK:
        tipi = kmedie(X, k)
        it = iter(tipi.tolist())
        seq = [[(pos, next(it)) for pos, _ in p] for p in rr]

        def mi_pos(sq):
            return misure.informazione_mutua([(pos, t) for p in sq for pos, t in p])

        def mi_seg(sq):
            return misure.informazione_mutua([(a[1], b[1]) for p in sq for a, b in zip(p, p[1:])])
        reale_p, reale_s = mi_pos(seq), mi_seg(seq)
        np_, ns = [], []
        for _ in range(RIMESCOLAMENTI):
            mes = []
            for p in seq:
                pos = [x for x, _ in p]
                t = [y for _, y in p]
                rnd.shuffle(t)
                mes.append(list(zip(pos, t)))
            np_.append(mi_pos(mes))
            ns.append(mi_seg(mes))
        out['k%d' % k] = OrderedDict([
            ('tipi', dict(Counter(tipi.tolist()))),
            ('posizione', OrderedDict([('im', reale_p), ('nullo', statistics.mean(np_)), ('z', (reale_p - statistics.mean(np_)) / statistics.pstdev(np_) if statistics.pstdev(np_) else None)])),
            ('seguente', OrderedDict([('im', reale_s), ('nullo', statistics.mean(ns)), ('z', (reale_s - statistics.mean(ns)) / statistics.pstdev(ns) if statistics.pstdev(ns) else None)]))])
    return out


def controllo(pars, rnd):
    interne = [w for p in pars for ps in p for w in ps[1:-1] if 'q' in w and trascrizione.pulita(w)]
    out = []
    for p in pars:
        p = [list(ps) for ps in p]
        if len(p) >= 2 and len(p[1]) >= 4:
            p[1] = [p[1][0]] + [rnd.choice(interne) for _ in p[1][1:-1]] + [p[1][-1]]
        out.append(p)
    return out


def main():
    rnd = random.Random(SEME)
    voy = paragrafi_voynich()
    t = OrderedDict([('Voynich ZL', voy), ('controllo positivo: 2a riga con parole in q', controllo(voy, random.Random(SEME + 1))),
                     ('Timm e Schinner, seme 19', paragrafi_ts())])
    ris = OrderedDict()
    for nome, pars in t.items():
        ris[nome] = r = valuta(pars, rnd)
        print('%-46s paragrafi %4d righe %5d | %s' % (nome, r['paragrafi'], r['righe'], ' | '.join(
            'k%d posizione z %.1f, seguente z %.1f' % (k, r['k%d' % k]['posizione']['z'] or 0, r['k%d' % k]['seguente']['z'] or 0) for k in KK)), flush=True)
    z = lambda n, k: ris[n]['k%d' % k]['posizione']['z'] or 0
    valido = z('controllo positivo: 2a riga con parole in q', 4) > 10
    voce = z('Voynich ZL', 4) > 4 and z('Voynich ZL', 3) > 3 and z('Voynich ZL', 6) > 3 and z('Voynich ZL', 4) > z('Timm e Schinner, seme 19', 4)
    ris['valido'], ris['voce_strutturata'] = valido, voce
    print('controllo valido:', valido, '| voce strutturata:', voce)
    with open(os.path.join(RISULTATI, 'e138_tipi_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e138 — Tipi di riga e posizione nel paragrafo', '', 'Profili di segni delle parole interne, k-medie; righe dalla 2a; nullo: %d rimescolamenti dell\'ordine delle '
           'righe nel paragrafo. Preregistrazione: `preregistrazioni/e138.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | ' + ' | '.join('k = %d: posizione (z) / seguente (z)' % k for k in KK) + ' |', '|---|---|' + '---|' * len(KK)]
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %s |' % (nome, r['righe'], ' | '.join('%.4f (%.1f) / %.4f (%.1f)' % (
                r['k%d' % k]['posizione']['im'], r['k%d' % k]['posizione']['z'] or 0, r['k%d' % k]['seguente']['im'], r['k%d' % k]['seguente']['z'] or 0) for k in KK)))
    out += ['', 'Controllo valido: **%s**. Voce strutturata: **%s**.' % ('sì' if valido else 'no', 'sì' if voce else 'no')]
    with open(os.path.join(RISULTATI, 'e138_tipi_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
