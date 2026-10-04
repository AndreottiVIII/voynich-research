# -*- coding: utf-8 -*-
"""Esperimento e3c09: la memoria delle scelte cala con le parole o con le lettere? Regressione dell'accordo in eccesso
(accordo − atteso) di ogni coppia nella stessa riga (distanza 1-7 parole) sulla distanza in parole d e sulle lettere in
mezzo L insieme, con un termine per classe. Nullo largo (rimescolamento dentro il tipo coperto, e3b62) per togliere gli
effetti di composizione; intervalli ricampionando pagine intere. ZL e IT, classi scelte a mano, con e senza la prima e
l'ultima parola della riga.

Preregistrazione: preregistrazioni/e3c09.md. Scrive risultati/e3c09_regressione_lettere_parole.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3c07_lettere_parole_bilanciate as e3c07

RISULTATI = os.path.join(QUI, '..', 'risultati')
DIST = range(1, 8)
PERM = 500
BOOT = 2000


def prepara(unita, strati, f):
    """Valori, gruppi per il rimescolamento e coppie (i, j, d, L) di una classe."""
    val, grp, uni, gruppi = [], [], [], {}
    I, J, Dd, L = [], [], [], []
    for u, seqs in enumerate(unita):
        for s in seqs:
            ids, cop = [], []
            for w in s:
                x = f(w)
                if x is None:
                    ids.append(None)
                    cop.append(None)
                    continue
                ids.append(len(val))
                cop.append(x[1])
                val.append(x[0])
                grp.append(gruppi.setdefault((strati[u], x[1]), len(gruppi)))
                uni.append(u)
            for i in range(len(ids)):
                if ids[i] is None:
                    continue
                for d in DIST:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    Dd.append(d)
                    L.append(sum(len(s[k]) for k in range(i + 1, j)))
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = T[uni[I]] - 2 >= 5
    return dict(val=np.array(val, dtype=float), grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok],
                d=np.array(Dd, dtype=float)[ok], L=np.array(L, dtype=float)[ok], n_unita=len(unita))


def eccesso(c, val):
    """Accordo − atteso per ogni coppia (atteso dalla quota dell'unità senza la coppia)."""
    U = np.bincount(c['uni'], weights=val, minlength=c['n_unita'])
    vi, vj = val[c['I']], val[c['J']]
    u = c['uni'][c['I']]
    p = (U[u] - vi - vj) / (c['T'][u] - 2)
    return (vi == vj).astype(float) - (p * p + (1 - p) * (1 - p))


def matrici(cc):
    """X (coppie × [classi..., d, L]) e unità di ogni coppia, per tutte le classi insieme."""
    k = len(cc)
    blocchi, unita = [], []
    for n, c in enumerate(cc.values()):
        x = np.zeros((len(c['I']), k + 2))
        x[:, n] = 1.0
        x[:, k] = c['d']
        x[:, k + 1] = c['L']
        blocchi.append(x)
        unita.append(c['uni'][c['I']])
    return np.vstack(blocchi), np.concatenate(unita)


def coeff(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0][-2:]


def misura(uu, ss, classi, rng):
    cc = OrderedDict((k, prepara(uu, ss, f)) for k, f in classi.items())
    X, un = matrici(cc)
    y = np.concatenate([eccesso(c, c['val']) for c in cc.values()])
    oss = coeff(X, y)
    nul = np.array([coeff(X, np.concatenate([eccesso(c, e3b54.rimescola(c, rng)) for c in cc.values()])) for _ in range(PERM)])
    mu = nul.mean(0)
    n_u = int(un.max()) + 1
    k = X.shape[1]
    XtX = np.zeros((n_u, k, k))
    Xty = np.zeros((n_u, k))
    for u in np.unique(un):
        m = un == u
        XtX[u] = X[m].T @ X[m]
        Xty[u] = X[m].T @ y[m]
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n_u, n_u)
        A, b = XtX[idx].sum(0), Xty[idx].sum(0)
        try:
            boot.append(np.linalg.solve(A, b)[-2:] - mu)
        except np.linalg.LinAlgError:
            continue
    boot = np.array(boot)
    out = OrderedDict([('coppie', int(len(y)))])
    for n, nome in enumerate(('per_parola', 'per_lettera')):
        out[nome] = OrderedDict([('osservato', float(oss[n])), ('nullo', float(mu[n])), ('effetto', float(oss[n] - mu[n])),
                                 ('IC95', [float(np.percentile(boot[:, n], 2.5)), float(np.percentile(boot[:, n], 97.5))])])
    return out


def esito(x):
    p, l = x['per_parola']['IC95'], x['per_lettera']['IC95']
    giu_p, giu_l = p[1] < 0, l[1] < 0
    if giu_l and not giu_p and p[0] <= 0 <= p[1]:
        return 'cala con le lettere, non con le parole'
    if giu_p and not giu_l and l[0] <= 0 <= l[1]:
        return 'cala con le parole, non con le lettere'
    if giu_p and giu_l:
        return 'cala con tutte e due'
    return 'incerto'


def main():
    rng = np.random.default_rng(3309)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        for bordi, u in (('senza i bordi', e3c07.senza_bordi(uu)), ('con i bordi', uu)):
            x = misura(u, ss, e3b62.CV, rng)
            x['esito'] = esito(x)
            ris['%s, %s' % (q, bordi)] = x
            print(q, bordi, json.dumps(x, ensure_ascii=False), flush=True)
    e_zl, e_it = ris['ZL, senza i bordi']['esito'], ris['IT, senza i bordi']['esito']
    finale = e_zl if e_zl == e_it else 'incerto (ZL: %s; IT: %s)' % (e_zl, e_it)
    out = OrderedDict([('misure', ris), ('esito', finale)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c09_regressione_lettere_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c09 — La memoria delle scelte cala con le parole o con le lettere? (regressione)', '',
          'Preregistrazione: `preregistrazioni/e3c09.md`. Coefficienti dell\'accordo in eccesso per una parola e per una lettera in più in mezzo, meno il nullo largo; IC 95% per pagine.', '',
          '| misura | coppie | per parola (IC 95%) | per lettera (IC 95%) | per 5 lettere | esito |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        p, l = x['per_parola'], x['per_lettera']
        md.append('| %s | %d | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) | %+.4f | %s |' % (k, x['coppie'], p['effetto'], p['IC95'][0], p['IC95'][1],
                                                                                 l['effetto'], l['IC95'][0], l['IC95'][1], 5 * l['effetto'], x['esito']))
    md += ['', 'Esito (senza i bordi, ZL e IT d\'accordo): **%s**.' % finale]
    open(os.path.join(RISULTATI, 'e3c09_regressione_lettere_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
