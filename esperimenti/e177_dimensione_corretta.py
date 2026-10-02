# -*- coding: utf-8 -*-
"""Esperimento 177: dimensione della scrittura per riga corretta per la composizione delle parole (larghezze tipiche
delle unita' EVA stimate con NNLS), e cambio delle scelte di grafia fra righe consecutive.

Preregistrazione: preregistrazioni/e177.md. Scrive risultati/e177_dimensione_corretta.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

import numpy as np
from scipy.optimize import nnls

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146
import e173_dimensione_scrittura as e173
import e173b_dimensione_per_lunghezza as e173b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 177
D = e173.D


def parole_allineate():
    """[(pagina, riga, parola, larghezza/mediana della pagina)]."""
    righe = e146.righe_voynich()
    per = defaultdict(list)
    for k, (pag, _, _) in enumerate(righe):
        per[pag].append(k)
    out = []
    for pag, ks in per.items():
        p = os.path.join(e34.RIQUADRI, pag + '.js')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        voc = [w[0] for w in d[0]]
        vt = [(voc[e[0]], e[3]) for e in d[1]]
        zt = [(k, w) for k in ks for w in righe[k][2]]
        sm = SequenceMatcher(a=[e34.fondi(w) for w, _ in vt], b=[e34.fondi(w) for _, w in zt], autojunk=False)
        loc = []
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                w = zt[j0 + t][1]
                if vt[i0 + t][1] > 0 and trascrizione.pulita(w):
                    loc.append((pag, zt[j0 + t][0], w, vt[i0 + t][1]))
        if loc:
            m = statistics.median(x[3] for x in loc)
            out += [(a, b, c, l / m) for a, b, c, l in loc]
    return righe, out


def main():
    rnd = random.Random(SEME)
    righe, pp = parole_allineate()
    unita = sorted({u for _, _, w, _ in pp for u in D(w)})
    idx = {u: i for i, u in enumerate(unita)}
    A = np.zeros((len(pp), len(unita) + 1))
    b = np.zeros(len(pp))
    for r, (_, _, w, l) in enumerate(pp):
        for u in D(w):
            A[r, idx[u]] += 1
        A[r, -1] = 1
        b[r] = l
    coef, _ = nnls(A, b)
    attesa = A @ coef
    per_riga = defaultdict(list)
    for (pag, k, _, l), a in zip(pp, attesa):
        if a > 0:
            per_riga[(pag, k)].append((l / a, a))
    P, Q = OrderedDict(), OrderedDict()
    for (pag, k), v in per_riga.items():
        if len(v) >= e173.MIN_PAROLE:
            P.setdefault(pag, []).append((k, statistics.median(x for x, _ in v)))
            Q.setdefault(pag, []).append((k, statistics.median(a for _, a in v)))
    for pag in list(P):
        if len(P[pag]) < e173.MIN_RIGHE:
            del P[pag], Q[pag]
            continue
        m = statistics.median(x for _, x in P[pag])
        P[pag] = sorted((k, x / m) for k, x in P[pag])
        Q[pag] = sorted(Q[pag])
    seqs = [[x for _, x in v] for v in P.values()]

    def auto(ss):
        a, b2 = [], []
        for s in ss:
            a += s[:-1]
            b2 += s[1:]
        return e173.pearson(a, b2)
    vero1 = auto(seqs)
    nulli = []
    for _ in range(200):
        mes = []
        for s in seqs:
            s = s[:]
            rnd.shuffle(s)
            mes.append(s)
        nulli.append(auto(mes))
    z1 = (vero1 - statistics.mean(nulli)) / statistics.pstdev(nulli)
    valido = z1 > 5
    res = e146.residui(righe)
    cc, comp = [], []
    for pag, v in P.items():
        q = dict(Q[pag])
        for (k1, s1), (k2, s2) in zip(v, v[1:]):
            if k2 != k1 + 1 or righe[k1][1] != righe[k2][1]:
                continue
            dif = [abs(res[(f, k2)] - res[(f, k1)]) for f in e146.SCELTE if (f, k1) in res and (f, k2) in res]
            if dif:
                c = e173b.classe(min(len(righe[k1][2]), len(righe[k2][2])))
                cc.append({'pagina': pag, 'dim': abs(s2 - s1), 'scelta': statistics.mean(dif), 'classe': c})
                comp.append(abs(q[k2] - q[k1]))
    vero = e173b.statistica(cc, [c['dim'] for c in cc])
    vero_comp = e173b.statistica(cc, comp)
    e173b.RIMESCOLAMENTI = 2000
    n1 = e173b.nullo(cc, lambda c: c['classe'], rnd)
    p = (1 + sum(x >= vero for x in n1)) / 2001
    esito = ('test non valido' if not valido else ('legame non meccanico' if vero > 0 and p < 0.01 else
             ('legame meccanico' if p > 0.05 else 'incerto')))
    ris = OrderedDict([('parole', len(pp)), ('larghezze_unita', {u: float(coef[idx[u]]) for u in unita}), ('costante', float(coef[-1])),
                       ('pagine', len(P)), ('righe', sum(map(len, P.values()))), ('V1', OrderedDict([('r', vero1), ('nullo', statistics.mean(nulli)), ('z', z1)])),
                       ('valido', valido), ('coppie', len(cc)), ('statistica', vero), ('p', p), ('statistica_composizione', vero_comp), ('esito', esito)])
    print('parole %d | pagine %d righe %d | V1 r %.3f z %.1f | coppie %d | statistica %.3f p %.4f | composizione %.3f | %s' % (
        len(pp), len(P), ris['righe'], vero1, z1, len(cc), vero, p, vero_comp, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e177_dimensione_corretta.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e177 — Dimensione della scrittura corretta per la composizione delle parole', '',
           'Larghezza osservata / attesa dalle unità EVA (NNLS su %d parole). Preregistrazione: `preregistrazioni/e177.md`.' % len(pp), '',
           '| verifica | valore |', '|---|---|', '| V1 correlazione fra righe consecutive (z) | %.3f (%.1f) |' % (vero1, z1),
           '| statistica dentro le classi di lunghezza (p) | %.3f (%.4f), coppie %d |' % (vero, p, len(cc)),
           '| controllo: |Δ composizione attesa| contro cambio di scelta | %.3f |' % vero_comp, '',
           'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e177_dimensione_corretta.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
