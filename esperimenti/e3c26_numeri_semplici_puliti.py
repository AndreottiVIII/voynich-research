# -*- coding: utf-8 -*-
"""Esperimento e3c26 (descrittivo): la memoria delle scelte in punti percentuali, senza la parte dovuta alla pagina e alla
deriva lungo la riga. Per ogni coppia (i, j) della stessa classe nella stessa riga (righe senza la prima e l'ultima
parola), r_j = v_j − p_j con p_j = quota attesa per la parola j; Δ = media di r_j se i ha la variante 1 meno media se i ha
l'altra; memoria in punti = Δ(vicine 2–3) − Δ(lontane 6–10). Tre versioni di p_j: quota generale della classe (come e3b82),
quota della pagina, quota della pagina più deriva lungo la riga (β dell'e3c13). ZL e IT, classi scelte a mano.

Preregistrazione: preregistrazioni/e3c26.md. Scrive risultati/e3c26_numeri_semplici_puliti.json e .md.
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
import e3b62_memoria_nullo_largo as e3b62
import e3c07_lettere_parole_bilanciate as e3c07
import e3c09_regressione_lettere_parole as e3c09
import e3c15_forma_senza_deriva as e3c15

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
VERSIONI = ('quota generale', 'quota della pagina', 'pagina e deriva')


def attese(c, x, b):
    """p per ogni parola della classe nelle tre versioni (lasciando fuori la parola stessa)."""
    val, uni = c['val'], c['uni']
    n_u = c['n_unita']
    U = np.bincount(uni, weights=val, minlength=n_u)
    T = np.bincount(uni, minlength=n_u).astype(float)
    tot, n = val.sum(), len(val)
    gen = (tot - val) / (n - 1)
    pag = np.where(T[uni] > 1, (U[uni] - val) / np.maximum(T[uni] - 1, 1), gen)
    xm = np.bincount(uni, weights=x, minlength=n_u) / np.maximum(T, 1)
    der = np.clip(pag + b * (x - xm[uni]), 0.0, 1.0)
    return {'quota generale': gen, 'quota della pagina': pag, 'pagina e deriva': der}


def somme(cc, uu, n_u):
    """(unità, versione, gruppo vicine/lontane, variante di i, [Σ r_j, coppie])."""
    out = np.zeros((n_u, len(VERSIONI), 2, 2, 2))
    for k, c in cc.items():
        f = e3b62.CV[k]
        x = e3c15.posizioni(uu, f)
        b = e3c15.beta(c, x)
        pp = attese(c, x, b)
        vi, vj = c['val'][c['I']], c['val'][c['J']]
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


def punti(s):
    """s (versione, gruppo, variante, 2) -> memoria in punti percentuali per versione."""
    with np.errstate(divide='ignore', invalid='ignore'):
        media = s[..., 0] / s[..., 1]
    delta = media[..., 1] - media[..., 0]
    return 100 * (delta[..., 0] - delta[..., 1]), 100 * delta


def main():
    rng = np.random.default_rng(3326)
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
            mem, delta = punti(st.sum(0))
            y = OrderedDict()
            for iv, ver in enumerate(VERSIONI):
                y[ver] = OrderedDict([('memoria_punti', float(mem[iv])), ('vicine_punti', float(delta[iv, 0])), ('lontane_punti', float(delta[iv, 1]))])
            if nome == 'insieme':
                boot = np.array([punti(st[rng.integers(0, len(uu), len(uu))].sum(0))[0] for _ in range(BOOT)])
                for iv, ver in enumerate(VERSIONI):
                    y[ver]['IC95'] = [float(np.percentile(boot[:, iv], 2.5)), float(np.percentile(boot[:, iv], 97.5))]
            x[nome] = y
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c26_numeri_semplici_puliti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c26 — La memoria delle scelte in punti percentuali, senza pagina e deriva (descrittivo)', '',
          'Preregistrazione: `preregistrazioni/e3c26.md`. Punti = quanto la variante della prima parola sposta la seconda (vicine 2–3) oltre quanto la sposta a 6–10 parole. Righe senza la prima e l\'ultima parola.', '',
          '| trascrizione | classi | quota generale (come e3b82) | quota della pagina | pagina e deriva |', '|---|---|---|---|---|']
    for q, x in ris.items():
        for nome, y in x.items():
            cel = []
            for ver in VERSIONI:
                z = y[ver]
                t = '%.1f (vicine %.1f, lontane %.1f)' % (z['memoria_punti'], z['vicine_punti'], z['lontane_punti'])
                if 'IC95' in z:
                    t += ', IC %.1f – %.1f' % tuple(z['IC95'])
                cel.append(t)
            md.append('| %s | %s | %s |' % (q, nome, ' | '.join(cel)))
    open(os.path.join(RISULTATI, 'e3c26_numeri_semplici_puliti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
