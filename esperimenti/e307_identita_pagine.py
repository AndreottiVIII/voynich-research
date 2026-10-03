# -*- coding: utf-8 -*-
"""Esperimento 307: che cosa rende ogni pagina diversa dalle altre. (A) identita' della pagina oltre sezione e lingua;
(B) caratteristiche che la portano; (C) se viene dal tempo (pagine consecutive), dalla mano o dal fascicolo; (D) se ci
sono tipi di pagina.

Preregistrazione: preregistrazioni/e307.md. Scrive risultati/e307_identita_pagine.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_PAROLE, NULLI, PERM, NULLI_D = 60, 200, 1000, 50
INIZIALI_V = ['q', 'o', 'ch', 'sh', 'd', 's', 'y', 'a', 'k', 't', 'p', 'f', 'l', ('ckh', 'cth', 'cph', 'cfh')]
FINALI_V = ['y', 'n', 'l', 'r', 'm', 's', 'o']


class Testo:
    """Pagine (nome, strato, mano, fascicolo, posizione nel libro, parole) e le caratteristiche per tipo di parola."""

    def __init__(self, pagine, dividi, iniziali=None, finali=None):
        conta = defaultdict(int)
        for p in pagine:
            conta[p['strato']] += 1
        self.pagine = [p for p in pagine if conta[p['strato']] >= 3 and len(p['parole']) >= MIN_PAROLE]
        tok = [(i, w) for i, p in enumerate(self.pagine) for w in p['parole']]
        tipi = sorted({w for _, w in tok})
        idx = {w: k for k, w in enumerate(tipi)}
        self.pag = np.array([i for i, _ in tok])
        self.parola = np.array([idx[w] for _, w in tok])
        freq = Counter(w for _, w in tok)
        u = {w: dividi(w) for w in tipi}
        gl = Counter(g for w, n in freq.items() for g in u[w] for _ in range(n))
        self.glifi = [g for g, _ in gl.most_common(25)]
        if iniziali is None:
            iniziali = [g for g, _ in Counter(u[w][0] for w in freq.elements()).most_common(12)]
        if finali is None:
            finali = [g for g, _ in Counter(u[w][-1] for w in freq.elements()).most_common(8)]
        self.parole30 = [w for w, _ in freq.most_common(30)]
        voc5 = [w for w, n in freq.items() if n >= 5]
        self.v5 = {w: k for k, w in enumerate(voc5)}
        ini_n = ['%s' % (x if isinstance(x, str) else 'gallows composti') for x in iniziali] + ['altra']
        fin_n = list(finali) + ['altra']
        self.nomi = (['segno %s' % g for g in self.glifi] + ['segni altri'] + ['iniziale %s' % x for x in ini_n] + ['finale %s' % x for x in fin_n]
                     + ['lunghezza', 'lunghezza2'] + ['parola %s' % w for w in self.parole30])
        G, I, F = len(self.glifi) + 1, len(ini_n), len(fin_n)
        self.G, self.I, self.F = G, I, F
        M = np.zeros((len(tipi), len(self.nomi)))
        gi = {g: k for k, g in enumerate(self.glifi)}
        p30 = {w: k for k, w in enumerate(self.parole30)}
        for w, k in idx.items():
            x = u[w]
            for g in x:
                M[k, gi.get(g, G - 1)] += 1
            a = next((t for t, c in enumerate(iniziali) if (x[0] == c if isinstance(c, str) else x[0] in c)), I - 1)
            M[k, G + a] = 1
            b = finali.index(x[-1]) if x[-1] in finali else F - 1
            M[k, G + I + b] = 1
            M[k, G + I + F] = len(x)
            M[k, G + I + F + 1] = len(x) ** 2
            if w in p30:
                M[k, G + I + F + 2 + p30[w]] = 1
        self.M = M
        self.v5_di = np.array([self.v5.get(w, -1) for w in tipi])
        self.strati = defaultdict(list)
        for i, p in enumerate(self.pagine):
            self.strati[p['strato']].append(i)
        self.tok_strato = defaultdict(list)
        for t, i in enumerate(self.pag):
            self.tok_strato[self.pagine[i]['strato']].append(t)
        self.tok_strato = {s: np.array(v) for s, v in self.tok_strato.items()}

    def rimescola(self, rnd):
        out = self.parola.copy()
        for s, t in self.tok_strato.items():
            x = out[t].copy()
            rnd.shuffle(x)
            out[t] = x
        return out

    def somme(self, parola):
        n = len(self.pagine)
        S = np.zeros((n, self.M.shape[1]))
        np.add.at(S, self.pag, self.M[parola])
        W = np.zeros((n, len(self.v5)))
        v = self.v5_di[parola]
        ok = v >= 0
        np.add.at(W, (self.pag[ok], v[ok]), 1)
        N = np.bincount(self.pag, minlength=n).astype(float)
        return S, W, N

    def caratteristiche(self, S, N):
        G, I, F = self.G, self.I, self.F
        tot_g = S[:, :G].sum(1, keepdims=True)
        X = np.hstack([S[:, :G] / tot_g, S[:, G:G + I] / N[:, None], S[:, G + I:G + I + F] / N[:, None],
                       (S[:, G + I + F] / N)[:, None], np.sqrt(np.maximum(S[:, G + I + F + 1] / N - (S[:, G + I + F] / N) ** 2, 0))[:, None],
                       S[:, G + I + F + 2:] / N[:, None]])
        nomi = self.nomi[:G + I + F] + ['lunghezza media', 'lunghezza deviazione'] + self.nomi[G + I + F + 2:]
        return X, nomi

    def scarti(self, X):
        R = X.copy()
        for s, idx in self.strati.items():
            R[idx] = X[idx] - X[idx].mean(0)
        return R


def jsd(P, Q):
    P = P / np.maximum(P.sum(1, keepdims=True), 1e-12)
    Q = Q / np.maximum(Q.sum(1, keepdims=True), 1e-12)
    Mx = (P + Q) / 2

    def kl(a, b):
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(a > 0, a * np.log2(a / np.maximum(b, 1e-300)), 0).sum(1)
    return (kl(P, Mx) + kl(Q, Mx)) / 2


def identita(t, S, W):
    """I per le tre rappresentazioni: distanza media pagina-strato."""
    G, I, F = t.G, t.I, t.F
    out = OrderedDict()
    for nome, A in (('segni', S[:, :G]), ('parole', W), ('iniziali e finali', None)):
        if A is None:
            a1, a2 = S[:, G:G + I], S[:, G + I:G + I + F]
            v = []
            for B in (a1, a2):
                ref = np.zeros_like(B)
                for s, idx in t.strati.items():
                    ref[idx] = B[idx].sum(0)
                v.append(jsd(B, ref))
            out[nome] = float(np.mean((v[0] + v[1]) / 2))
        else:
            ref = np.zeros_like(A)
            for s, idx in t.strati.items():
                ref[idx] = A[idx].sum(0)
            out[nome] = float(np.mean(jsd(A, ref)))
    return out


def domanda_A(t, parola, rnd):
    S, W, N = t.somme(parola)
    vero = identita(t, S, W)
    nulli = defaultdict(list)
    for _ in range(NULLI):
        S2, W2, _ = t.somme(t.rimescola(rnd))
        for k, v in identita(t, S2, W2).items():
            nulli[k].append(v)
    out = OrderedDict()
    for k, v in vero.items():
        m, sd = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('I', v), ('nullo', m), ('rapporto', v / m if m else None), ('z', (v - m) / sd if sd else 0.0)])
    return out


def main():
    rnd = random.Random(307)
    pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            x = pag.setdefault(r.pagina, {'nome': r.pagina, 'strato': (r.sezione or '?', r.lingua or '?'), 'mano': r.mano or '?', 'fascicolo': r.quire or '?', 'parole': []})
            x['parole'] += [w for w in r.parole if trascrizione.pulita(w)]
    for k, x in enumerate(pag.values()):
        x['posizione'] = k
    voy = Testo(list(pag.values()), D, INIZIALI_V, FINALI_V)
    print('Voynich: %d pagine in %d strati, %d parole' % (len(voy.pagine), len(voy.strati), len(voy.parola)), flush=True)
    lat = [w.lower() for w in lingue.parole('Latin', max_caratteri=400000) if w.isalpha()]
    bib = Testo([{'nome': 'b%d' % i, 'strato': 'Bibbia', 'mano': '-', 'fascicolo': '-', 'posizione': i, 'parole': lat[i * 170:(i + 1) * 170]}
                 for i in range(len(lat) // 170)], list)
    A = OrderedDict()
    A['Voynich'] = domanda_A(voy, voy.parola, rnd)
    A['controllo positivo: Bibbia latina in pagine'] = domanda_A(bib, bib.parola, rnd)
    A['controllo negativo: Voynich rimescolato'] = domanda_A(voy, voy.rimescola(random.Random(3070)), rnd)
    for n, x in A.items():
        print('A %-46s %s' % (n, {k: (round(v['rapporto'], 3), round(v['z'], 1)) for k, v in x.items()}), flush=True)
    zp = [v['z'] for v in A['controllo positivo: Bibbia latina in pagine'].values()]
    zn = [v['z'] for v in A['controllo negativo: Voynich rimescolato'].values()]
    zv = [v['z'] for v in A['Voynich'].values()]
    valido = all(z > 3 for z in zp) and all(abs(z) < 2 for z in zn)
    esitoA = 'non valido' if not valido else ('pagine con identità' if sum(z > 3 for z in zv) >= 2 else ('nessuna identità oltre lo strato' if all(z < 2 for z in zv) else 'incerto'))

    # B
    S, W, N = voy.somme(voy.parola)
    X, nomi = voy.caratteristiche(S, N)
    R = voy.scarti(X)
    var_vero = R.var(0)
    var_nulli, R_nulli = [], []
    for k in range(NULLI):
        S2, _, N2 = voy.somme(voy.rimescola(rnd))
        R2 = voy.scarti(voy.caratteristiche(S2, N2)[0])
        var_nulli.append(R2.var(0))
        if k < NULLI_D:
            R_nulli.append(R2)
    var_nulli = np.array(var_nulli)
    sd_null = np.sqrt(var_nulli.mean(0))
    ecc = var_vero / np.maximum(var_nulli.mean(0), 1e-15)
    zB = (var_vero - var_nulli.mean(0)) / np.maximum(var_nulli.std(0), 1e-15)
    B = [OrderedDict([('caratteristica', nomi[j]), ('eccesso', float(ecc[j])), ('z', float(zB[j]))]) for j in np.argsort(-ecc)]
    print('B prime 15:', [(b['caratteristica'], round(b['eccesso'], 2)) for b in B[:15]], flush=True)

    # C
    P = R / np.maximum(sd_null, 1e-12)
    C = np.corrcoef(P)
    n = len(voy.pagine)
    classi = defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = voy.pagine[i], voy.pagine[j]
            if a['strato'] != b['strato']:
                continue
            d = abs(a['posizione'] - b['posizione'])
            if d == 1:
                classi['consecutive'].append((i, j))
            elif d <= 5:
                classi['vicine (2-5)'].append((i, j))
            else:
                if a['mano'] == b['mano'] and a['mano'] != '?':
                    classi['stessa mano (>5)'].append((i, j))
                if a['fascicolo'] == b['fascicolo'] and a['fascicolo'] != '?':
                    classi['stesso fascicolo (>5)'].append((i, j))
                if a['mano'] != b['mano'] and a['fascicolo'] != b['fascicolo']:
                    classi['altre (>5)'].append((i, j))
    rndC = random.Random(3071)
    perm_null = defaultdict(list)
    coppie = {k: (np.array([x for x, _ in v]), np.array([y for _, y in v])) for k, v in classi.items() if v}
    for _ in range(PERM):
        pi = np.arange(n)
        for s, idx in voy.strati.items():
            x = list(idx)
            rndC.shuffle(x)
            pi[idx] = x
        for k, (I_, J_) in coppie.items():
            perm_null[k].append(C[pi[I_], pi[J_]].mean())
    Cres = OrderedDict()
    for k, (I_, J_) in coppie.items():
        v = float(C[I_, J_].mean())
        m, sd = statistics.mean(perm_null[k]), statistics.pstdev(perm_null[k])
        Cres[k] = OrderedDict([('coppie', len(I_)), ('correlazione', v), ('nullo', m), ('z', (v - m) / sd if sd else 0.0)])
    print('C', {k: (round(v['correlazione'], 3), round(v['z'], 1)) for k, v in Cres.items()}, flush=True)
    comp = [nome for nome, k in (('temporale', 'consecutive'), ('di mano', 'stessa mano (>5)'), ('di fascicolo', 'stesso fascicolo (>5)')) if k in Cres and Cres[k]['z'] > 3]
    esitoC = ', '.join(comp) if comp else 'individuale'

    # D
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    def migliore(Pm):
        best = (-1, None, None)
        for k in range(2, 7):
            km = KMeans(n_clusters=k, n_init=10, random_state=307).fit(Pm)
            s = silhouette_score(Pm, km.labels_)
            if s > best[0]:
                best = (s, k, km.labels_)
        return best
    s_vero, k_vero, lab = migliore(P)
    s_null = [migliore(Rn / np.maximum(sd_null, 1e-12))[0] for Rn in R_nulli]
    zD = (s_vero - statistics.mean(s_null)) / statistics.pstdev(s_null) if statistics.pstdev(s_null) else 0.0
    esitoD = 'tipi di pagina' if zD > 3 else ('nessun tipo' if zD < 2 else 'incerto')
    gruppi = OrderedDict()
    for g in range(k_vero):
        idx = [i for i in range(n) if lab[i] == g]
        pp = [voy.pagine[i] for i in idx]
        media = P[idx].mean(0)
        gruppi[g] = OrderedDict([('pagine', len(idx)), ('sezione', dict(Counter(p['strato'][0] for p in pp))), ('lingua', dict(Counter(p['strato'][1] for p in pp))),
                                 ('mano', dict(Counter(p['mano'] for p in pp))), ('fascicolo', dict(Counter(p['fascicolo'] for p in pp))),
                                 ('posizione_media', statistics.mean(p['posizione'] for p in pp)),
                                 ('tratti', [(nomi[j], round(float(media[j]), 2)) for j in np.argsort(-np.abs(media))[:6]])])
    print('D silhouette %.3f (k %d) nullo %.3f z %.1f -> %s' % (s_vero, k_vero, statistics.mean(s_null), zD, esitoD), flush=True)

    out = OrderedDict([('A', A), ('A_esito', esitoA), ('B', B), ('C', Cres), ('C_esito', esitoC),
                       ('D', OrderedDict([('silhouette', s_vero), ('k', k_vero), ('nullo', statistics.mean(s_null)), ('z', zD), ('gruppi', gruppi)])), ('D_esito', esitoD)])
    json.dump(out, open(os.path.join(RISULTATI, 'e307_identita_pagine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e307 — Che cosa rende ogni pagina diversa dalle altre', '', 'Preregistrazione: `preregistrazioni/e307.md`. Pagine con almeno %d parole, in strati sezione × lingua con almeno 3 pagine (Voynich: %d pagine, %d strati).' % (
        MIN_PAROLE, len(voy.pagine), len(voy.strati)), '', '## A — Identità oltre sezione e lingua (distanza media pagina-strato)', '',
          '| testo | rappresentazione | I | nullo | rapporto | z |', '|---|---|---|---|---|---|']
    for t_, x in A.items():
        for k, v in x.items():
            md.append('| %s | %s | %.4f | %.4f | %.2f | %.1f |' % (t_, k, v['I'], v['nullo'], v['rapporto'], v['z']))
    md += ['', 'Esito A: **%s**.' % esitoA, '', '## B — Le caratteristiche che distinguono le pagine (eccesso di varianza sul nullo)', '',
           '| caratteristica | eccesso | z |', '|---|---|---|']
    for b in B[:15]:
        md.append('| %s | %.2f | %.1f |' % (b['caratteristica'], b['eccesso'], b['z']))
    md += ['', 'Le meno distintive: %s.' % ', '.join('%s (%.2f)' % (b['caratteristica'], b['eccesso']) for b in B[-5:]), '',
           '## C — Da dove viene l\'identità (correlazione fra profili di pagine dello stesso strato)', '', '| coppie | numero | correlazione | nullo | z |', '|---|---|---|---|---|']
    for k, v in Cres.items():
        md.append('| %s | %d | %.3f | %.3f | %.1f |' % (k, v['coppie'], v['correlazione'], v['nullo'], v['z']))
    md += ['', 'Esito C: **%s**.' % esitoC, '', '## D — Tipi di pagina', '',
           'Silhouette migliore %.3f con k = %d; nullo %.3f; z %.1f. Esito D: **%s**.' % (s_vero, k_vero, statistics.mean(s_null), zD, esitoD), '']
    for g, x in gruppi.items():
        md.append('- Gruppo %d (%d pagine, posizione media %.0f): sezioni %s; lingue %s; mani %s; tratti %s.' % (
            g, x['pagine'], x['posizione_media'], x['sezione'], x['lingua'], x['mano'], ', '.join('%s %+.2f' % t_ for t_ in x['tratti'])))
    open(os.path.join(RISULTATI, 'e307_identita_pagine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esitoA, '|', esitoC, '|', esitoD)


if __name__ == '__main__':
    main()
