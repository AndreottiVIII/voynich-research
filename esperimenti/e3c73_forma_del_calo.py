# -*- coding: utf-8 -*-
"""Esperimento e3c73: la forma del calo dell'accordo con la distanza. Una chiave (o uno stato) che cambia a intervalli
regolari di B parole, con inizio a caso, dà un calo in linea retta fino a zero, K(d) = A·max(0, 1 − d/B); uno stato che
cambia a caso (senza memoria) dà un calo geometrico, K(d) = A·ρ^(d − 1); una preferenza di tutta la riga aggiunge una
costante, K(d) = c + A·ρ^(d − 1). K corretto (e3c48) a distanza 1 – 7 sulle righe di almeno 10 parole (k/t, sh/ch,
-ey/-dy); modelli adattati con i pesi dei ricampionamenti delle pagine (χ²). Voynich ZL e IT.

Preregistrazione: preregistrazioni/e3c73.md. Scrive risultati/e3c73_forma_del_calo.json e .md.
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
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
DMAX = 7
PERM = 50
BOOT = 1000
GRIGLIA_RHO = np.linspace(0, 1, 201)
GRIGLIA_B = np.linspace(1.2, 30, 289)


def adatta(k, w, forma):
    """Minimi quadrati pesati; ritorna (χ², parametri)."""
    d = np.arange(1, len(k) + 1)
    best = None
    if forma == 'geometrico':
        for rho in GRIGLIA_RHO:
            g = rho ** (d - 1)
            A = float((w * g * k).sum() / (w * g * g).sum())
            c2 = float((w * (k - A * g) ** 2).sum())
            if best is None or c2 < best[0]:
                best = (c2, OrderedDict([('A', A), ('rho', float(rho))]))
    elif forma == 'a blocchi':
        for B in GRIGLIA_B:
            g = np.maximum(0, 1 - d / B)
            A = float((w * g * k).sum() / (w * g * g).sum()) if (g > 0).any() else 0.0
            c2 = float((w * (k - A * g) ** 2).sum())
            if best is None or c2 < best[0]:
                best = (c2, OrderedDict([('A', A), ('B', float(B))]))
    else:
        for rho in GRIGLIA_RHO:
            g = rho ** (d - 1)
            X = np.stack([np.ones_like(g), g], 1)
            W = np.diag(w)
            beta = np.linalg.lstsq(X.T @ W @ X, X.T @ W @ k, rcond=None)[0]
            c2 = float((w * (k - X @ beta) ** 2).sum())
            if best is None or c2 < best[0]:
                best = (c2, OrderedDict([('c', float(beta[0])), ('A', float(beta[1])), ('rho', float(rho))]))
    return best


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 10, DMAX
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    oss = e3c33.somme(tok, n_p)
    nul = np.mean([e3c33.somme(e3c48.rimescola(tok, rng), n_p) for _ in range(PERM)], axis=0)
    k = lambda s, n: s[..., 0].sum(0) / s[..., 1].sum(0) - n[..., 0].sum(0) / n[..., 1].sum(0)
    kc = k(oss, nul)
    boot = np.array([k(oss[i], nul[i]) for i in (rng.integers(0, n_p, n_p) for _ in range(BOOT))])
    w = 1 / boot.var(0)
    modelli = OrderedDict((f, adatta(kc, w, f)) for f in ('geometrico', 'a blocchi', 'costante più geometrico'))
    cc = [adatta(b, w, 'costante più geometrico')[1]['c'] for b in boot[:300]]
    return OrderedDict([('parole', len(tok)), ('K_corretto', [float(z) for z in kc]), ('IC95', [[float(np.percentile(boot[:, i], 2.5)), float(np.percentile(boot[:, i], 97.5))] for i in range(DMAX)]),
                        ('modelli', OrderedDict((f, OrderedDict([('chi2', m[0]), ('parametri', m[1])])) for f, m in modelli.items())),
                        ('c_IC95', [float(np.percentile(cc, 2.5)), float(np.percentile(cc, 97.5))])])


def voci(x):
    g, b, c = (x['modelli'][f]['chi2'] for f in ('geometrico', 'a blocchi', 'costante più geometrico'))
    forma = 'cambi a caso (calo geometrico)' if b - g > 4 else ('cambi a intervalli regolari (calo in linea retta)' if g - b > 4 else 'le due forme non si distinguono')
    riga = 'c\'è anche una preferenza di tutta la riga' if (g - c > 3.84 and x['c_IC95'][0] > 0) else 'nessuna preferenza di riga in più'
    return forma, riga


def main():
    rng = np.random.default_rng(3373)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        x = misura(pagine, cl, rng)
        x['forma'], x['riga'] = voci(x)
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    esito = OrderedDict((t, ris['ZL'][t] if ris['ZL'][t] == ris['IT'][t] else 'ZL: %s; IT: %s' % (ris['ZL'][t], ris['IT'][t])) for t in ('forma', 'riga'))
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c73_forma_del_calo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c73 — La forma del calo: cambi a caso o a intervalli regolari?', '', 'Preregistrazione: `preregistrazioni/e3c73.md`. Righe di almeno 10 parole; k/t, sh/ch, -ey/-dy.', '',
          '| trascrizione | K corretto a 1 … 7 | χ² geometrico (ρ) | χ² a blocchi (B) | χ² costante + geometrico (c, IC) | forma | riga |', '|---|---|---|---|---|---|---|']
    for q, x in ris.items():
        m = x['modelli']
        md.append('| %s | %s | %.1f (%.2f) | %.1f (%.1f) | %.1f (%+.3f, %+.3f – %+.3f) | %s | %s |' % (q, ' / '.join('%+.3f' % z for z in x['K_corretto']), m['geometrico']['chi2'], m['geometrico']['parametri']['rho'],
                                                                                     m['a blocchi']['chi2'], m['a blocchi']['parametri']['B'], m['costante più geometrico']['chi2'],
                                                                                     m['costante più geometrico']['parametri']['c'], x['c_IC95'][0], x['c_IC95'][1], x['forma'], x['riga']))
    md += ['', 'Esito: forma **%s**; riga **%s**.' % (esito['forma'], esito['riga'])]
    open(os.path.join(RISULTATI, 'e3c73_forma_del_calo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
