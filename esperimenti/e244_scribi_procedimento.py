# -*- coding: utf-8 -*-
"""Esperimento 244: le misure del procedimento (riuso, operatore di variante, scelte di riga) distinguono le mani ($H della
ZL, scribi di Davis) oltre lingua di Currier e sezione? Classificatore contro permutazioni dentro gli strati.

Preregistrazione: preregistrazioni/e244.md. Scrive risultati/e244_scribi_procedimento.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e206_segni_facoltativi as e206
import e237_riuso_pagina as e237
import e239_operatore_variante as e239

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE, PERMUTAZIONI, SEMI = 60, 200, (244, 245, 246, 247, 248)
D = e237.D


def pagine():
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            d = out.setdefault(r.pagina, {'lingua': r.lingua, 'sezione': r.sezione, 'mano': r.mano, 'righe': []})
            d['righe'].append(ps)
    return OrderedDict((p, d) for p, d in out.items() if sum(map(len, d['righe'])) >= MIN_PAROLE and d['mano'] and d['lingua'])


def caratteristiche(pag, inventario, top_ops, classi, cl, medie_classi):
    rr = pag['righe']
    sulla = OrderedDict()
    conta, ops = Counter(), Counter()
    for k, r in enumerate(rr):
        for w in r:
            u = tuple(D(w))
            if sulla:
                if u in sulla:
                    conta['R'] += 1
                else:
                    vic = e237.vicini(u, inventario)
                    fonti = [x for x in sulla if x in vic]
                    if fonti:
                        conta['V'] += 1
                        m = max(sulla[x] for x in fonti)
                        s = next(x for x in fonti if sulla[x] == m)
                        t, o = e239.operazione(s, u)
                        ops[t] += 1
                        ops[o] += 1
                    else:
                        conta['altro'] += 1
            sulla[u] = k
            sulla.move_to_end(u)
    n = sum(conta.values()) or 1
    nv = conta['V'] or 1
    f = OrderedDict([('R', conta['R'] / n), ('V', conta['V'] / n)])
    for t in ('sostituzione', 'inserzione', 'cancellazione'):
        f['op ' + t] = ops[t] / nv
    for o in top_ops:
        f['op ' + o] = ops[o] / nv
    occ = defaultdict(list)
    for r in rr:
        for w in r:
            for c, v in cl.get(w, {}).items():
                nome = '%s %s' % c
                if nome in classi:
                    occ[nome].append(v)
    for c in classi:
        f['scelta ' + c] = sum(occ[c]) / len(occ[c]) if len(occ[c]) >= 5 else medie_classi[c]
    return f


def accuratezza(X, y, semi=SEMI):
    acc = []
    for s in semi:
        k = min(5, min(Counter(y).values()))
        pieghe = StratifiedKFold(n_splits=max(2, k), shuffle=True, random_state=s)
        giuste = 0
        for tr, te in pieghe.split(X, y):
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X[tr], y[tr])
            giuste += (m.predict(X[te]) == y[te]).sum()
        acc.append(giuste / len(y))
    return float(np.mean(acc))


def prova(X, y, strati, rnd, semi=SEMI):
    vera = accuratezza(X, y, semi)
    nulli = []
    for _ in range(PERMUTAZIONI):
        yp = y.copy()
        for s in set(strati):
            idx = [i for i, x in enumerate(strati) if x == s]
            vals = list(yp[idx])
            rnd.shuffle(vals)
            yp[idx] = vals
        nulli.append(accuratezza(X, yp, semi[:1]))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    p = (1 + sum(x >= vera for x in nulli)) / (PERMUTAZIONI + 1)
    return OrderedDict([('accuratezza', vera), ('nullo', m), ('z', (vera - m) / sd if sd else None), ('p', p)])


def main():
    P = pagine()
    tutte = Counter(w for d in P.values() for r in d['righe'] for w in r)
    inventario = sorted({x for w in tutte for x in D(w)})
    top_ops = [o for o, _ in json.load(open(os.path.join(RISULTATI, 'e239_operatore_variante.json'), encoding='utf-8'))['Voynich']['prime_25'][:10]]
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    freq = Counter(w for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) for w in r.parole if trascrizione.pulita(w))
    cl = e206.classi_di(freq)
    occ = defaultdict(list)
    for w, n in freq.items():
        for c, v in cl.get(w, {}).items():
            occ['%s %s' % c] += [v] * n
    medie = {c: (sum(occ[c]) / len(occ[c]) if occ[c] else 0.5) for c in classi}
    nomi = list(P)
    feats = [caratteristiche(P[p], inventario, top_ops, classi, cl, medie) for p in nomi]
    colonne = list(feats[0])
    X = np.array([[f[c] for c in colonne] for f in feats])
    mani = np.array([P[p]['mano'] for p in nomi])
    lingue = np.array([P[p]['lingua'] for p in nomi])
    strati = ['%s|%s' % (P[p]['lingua'], P[p]['sezione']) for p in nomi]
    sezioni = [P[p]['sezione'] for p in nomi]
    piu_mani = {s: dict(Counter(m for m, t in zip(mani, strati) if t == s)) for s in sorted(set(strati)) if len(set(m for m, t in zip(mani, strati) if t == s)) > 1}
    print('pagine %d, caratteristiche %d, mani %s; strati con piu\' mani: %s' % (len(nomi), len(colonne), dict(Counter(mani)), piu_mani), flush=True)
    ris = OrderedDict([('pagine', len(nomi)), ('caratteristiche', colonne), ('mani', dict(Counter(mani))), ('strati_con_piu_mani', piu_mani)])
    ris['controllo positivo (lingua dentro la sezione)'] = prova(X, lingue, sezioni, random.Random(2441))
    print('controllo positivo', dict(ris['controllo positivo (lingua dentro la sezione)']), flush=True)
    ris['mani dentro lingua x sezione'] = prova(X, mani, strati, random.Random(2440))
    print('mani', dict(ris['mani dentro lingua x sezione']), flush=True)
    m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X, mani)
    peso = np.abs(m[-1].coef_).mean(0)
    ris['caratteristiche_piu_pesanti'] = [(colonne[i], float(peso[i])) for i in np.argsort(-peso)[:10]]
    cp, mn = ris['controllo positivo (lingua dentro la sezione)'], ris['mani dentro lingua x sezione']
    valido = (cp['z'] or 0) > 3
    esito = ('non valido' if not valido else 'procedimenti personali' if (mn['z'] or 0) > 3
             else 'nessuna differenza oltre lingua e sezione' if (mn['z'] or 0) <= 2 else 'incerto')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e244_scribi_procedimento.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e244 — Gli scribi hanno procedimenti diversi?', '',
          "Caratteristiche del procedimento per pagina (riuso, operatore di variante, 12 scelte di riga); accuratezza di una regressione logistica "
          "contro %d permutazioni dentro gli strati. Preregistrazione: `preregistrazioni/e244.md`." % PERMUTAZIONI, '',
          '| prova | pagine | accuratezza | nullo | z | p |', '|---|---|---|---|---|---|']
    for k in ('controllo positivo (lingua dentro la sezione)', 'mani dentro lingua x sezione'):
        r = ris[k]
        md.append('| %s | %d | %.3f | %.3f | %.1f | %.4f |' % (k, len(nomi), r['accuratezza'], r['nullo'], r['z'] or 0, r['p']))
    md += ['', 'Mani: %s. Strati (lingua|sezione) con più di una mano: %s.' % (dict(Counter(mani)), piu_mani), '',
           'Caratteristiche più pesanti per le mani: %s.' % ', '.join('%s (%.2f)' % x for x in ris['caratteristiche_piu_pesanti']), '',
           'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e244_scribi_procedimento.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
