# -*- coding: utf-8 -*-
"""Esperimento e3c27: la memoria in punti percentuali (e3c26) con l'atteso dalla stessa parola coperta. Versioni:
(1) quota generale della classe (come e3c26); (4) quota della stessa parola coperta nella stessa mano (lasciando fuori
la parola stessa); (5) come (4) più la deriva lungo la riga; (N) punti della versione (1) meno la media dei punti con le
scelte rimescolate dentro (mano, parola coperta), come il nullo largo dell'e3b62. Righe senza la prima e l'ultima
parola; ZL e IT, classi scelte a mano.

Preregistrazione: preregistrazioni/e3c27.md. Scrive risultati/e3c27_punti_per_parola.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3c07_lettere_parole_bilanciate as e3c07
import e3c09_regressione_lettere_parole as e3c09
import e3c15_forma_senza_deriva as e3c15
import e3c26_numeri_semplici_puliti as e3c26

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
PERM = 300
VERSIONI = ('quota generale', 'stessa parola', 'stessa parola e deriva')


def attese(c, val, x, b):
    uni, grp = c['uni'], c['grp']
    n_u = c['n_unita']
    tot, n = val.sum(), len(val)
    gen = (tot - val) / (n - 1)
    G = np.bincount(grp, weights=val)
    N = np.bincount(grp).astype(float)
    par = np.where(N[grp] > 1, (G[grp] - val) / np.maximum(N[grp] - 1, 1), gen)
    T = np.bincount(uni, minlength=n_u).astype(float)
    xm = np.bincount(uni, weights=x, minlength=n_u) / np.maximum(T, 1)
    der = np.clip(par + b * (x - xm[uni]), 0.0, 1.0)
    return {'quota generale': gen, 'stessa parola': par, 'stessa parola e deriva': der}


def somme(cc, uu, n_u, valori=None):
    out = np.zeros((n_u, len(VERSIONI), 2, 2, 2))
    for k, c in cc.items():
        f = e3b62.CV[k]
        val = c['val'] if valori is None else valori[k]
        x = e3c15.posizioni(uu, f)
        b = e3c15.beta(c, x)
        pp = attese(c, val, x, b)
        vi, vj = val[c['I']], val[c['J']]
        u = c['uni'][c['I']]
        g = np.where(c['d'] <= 3, 0, 1)
        for iv, ver in enumerate(VERSIONI):
            r = vj - pp[ver][c['J']]
            for gg in (0, 1):
                for a in (0, 1):
                    m = (g == gg) & (vi == a)
                    out[:, iv, gg, a, 0] += np.bincount(u[m], weights=r[m], minlength=n_u)
                    out[:, iv, gg, a, 1] += np.bincount(u[m], minlength=n_u)
    return out


def main():
    rng = np.random.default_rng(3327)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    e3c09.DIST = (2, 3, 6, 7, 8, 9, 10)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        uu = e3c07.senza_bordi(uu)
        x = OrderedDict()
        for nome, chiavi in [('insieme', list(e3b62.CV))] + [(k, [k]) for k in e3b62.CV]:
            cc = OrderedDict((k, e3c09.prepara(uu, ss, e3b62.CV[k])) for k in chiavi)
            st = somme(cc, uu, len(uu))
            mem, delta = e3c26.punti(st.sum(0))
            nul = np.mean([e3c26.punti(somme(cc, uu, len(uu), {k: e3b54.rimescola(c, rng) for k, c in cc.items()}).sum(0))[0][0] for _ in range(PERM)])
            y = OrderedDict()
            for iv, ver in enumerate(VERSIONI):
                y[ver] = OrderedDict([('memoria_punti', float(mem[iv])), ('vicine_punti', float(delta[iv, 0])), ('lontane_punti', float(delta[iv, 1]))])
            y['nullo largo'] = OrderedDict([('memoria_punti', float(mem[0] - nul)), ('nullo_punti', float(nul))])
            if nome == 'insieme':
                boot = np.array([e3c26.punti(st[rng.integers(0, len(uu), len(uu))].sum(0))[0] for _ in range(BOOT)])
                for iv, ver in enumerate(VERSIONI):
                    y[ver]['IC95'] = [float(np.percentile(boot[:, iv], 2.5)), float(np.percentile(boot[:, iv], 97.5))]
                y['nullo largo']['IC95'] = [float(np.percentile(boot[:, 0], 2.5) - nul), float(np.percentile(boot[:, 0], 97.5) - nul)]
            x[nome] = y
            print(q, nome, json.dumps(y, ensure_ascii=False), flush=True)
        ris[q] = x
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c27_punti_per_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c27 — La memoria in punti percentuali con l\'atteso dalla stessa parola', '',
          'Preregistrazione: `preregistrazioni/e3c27.md`. Righe senza la prima e l\'ultima parola. Punti = Δ(vicine 2–3) − Δ(lontane 6–10).', '',
          '| trascrizione | classi | quota generale | stessa parola | stessa parola e deriva | nullo largo (punti − nullo) |', '|---|---|---|---|---|---|']
    for q, x in ris.items():
        for nome, y in x.items():
            cel = []
            for ver in VERSIONI + ('nullo largo',):
                z = y[ver]
                t = '%.1f' % z['memoria_punti']
                if 'IC95' in z:
                    t += ' (%.1f – %.1f)' % tuple(z['IC95'])
                cel.append(t)
            md.append('| %s | %s | %s |' % (q, nome, ' | '.join(cel)))
    open(os.path.join(RISULTATI, 'e3c27_punti_per_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
