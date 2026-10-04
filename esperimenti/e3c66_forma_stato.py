# -*- coding: utf-8 -*-
"""Esperimento e3c66: la forma dello "stato" (e3c55) con la misura corretta dell'e3c48.
(A) Durata: K corretto a distanza 1 – 6 sulle righe di almeno 8 parole (senza prima e ultima), k/t, sh/ch, -ey/-dy
insieme; curva K(d) = A·ρ^(d−1) adattata ai sei punti; mezza vita in parole.
(B) Accoppiamento: K corretto fra parole vicine (1 – 3) della stessa scelta e di scelte diverse (accordo = tutte e due
marcate, qo/k/sh/-ey, o tutte e due semplici), come l'e3c43 ma con la correzione per la distorsione.
Voynich ZL e IT.

Preregistrazione: preregistrazioni/e3c66.md. Scrive risultati/e3c66_forma_stato.json e .md.
"""
import json, math, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
PERM = 50
BOOT = 2000


def adatta(k):
    """K(d) = A·ρ^(d−1) ai minimi quadrati, ρ su una griglia in [0, 1]; ritorna (A, ρ)."""
    d = np.arange(len(k))
    best = None
    for rho in np.linspace(0, 1, 201):
        g = rho ** d
        A = float((g * k).sum() / (g * g).sum())
        e = float(((k - A * g) ** 2).sum())
        if best is None or e < best[0]:
            best = (e, A, float(rho))
    return best[1], best[2]


def mezza_vita(rho):
    return float('inf') if rho >= 1 else (0.0 if rho <= 0 else math.log(0.5) / math.log(rho))


def durata(pagine, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 8, 6
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    tok = e3c33.raccogli(pagine, cl)
    n_p = len(pagine)
    oss = e3c33.somme(tok, n_p)
    nul = np.mean([e3c33.somme(e3c48.rimescola(tok, rng), n_p) for _ in range(PERM)], axis=0)
    k = lambda s, n: s[..., 0].sum(0) / s[..., 1].sum(0) - n[..., 0].sum(0) / n[..., 1].sum(0)
    kc = k(oss, nul)
    boot, fit = [], []
    for _ in range(BOOT):
        idx = rng.integers(0, n_p, n_p)
        b = k(oss[idx], nul[idx])
        boot.append(b)
        fit.append(adatta(b))
    boot = np.array(boot)
    A, rho = adatta(kc)
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    lont = boot[:, 3:].mean(1)
    vic = boot[:, :3].mean(1)
    return OrderedDict([('parole', len(tok)), ('K_corretto', [float(z) for z in kc]), ('IC95', [ic(boot[:, i]) for i in range(6)]),
                        ('K_1_3', float(kc[:3].mean())), ('K_1_3_IC95', ic(vic)), ('K_4_6', float(kc[3:].mean())), ('K_4_6_IC95', ic(lont)),
                        ('A', A), ('rho', rho), ('rho_IC95', ic([f[1] for f in fit])), ('mezza_vita_parole', mezza_vita(rho)),
                        ('mezza_vita_IC95', ic([mezza_vita(f[1]) for f in fit]))])


def somme_incrocio(tok, n_p):
    """(pagine, 2 gruppi [stessa scelta, scelte diverse], 2): accordo nel verso marcato fra parole a distanza 1 – 3."""
    v, x, tipo, mano, sp, npg, sx, beta = e3c33.preparazione(tok)
    per_riga = defaultdict(list)
    for j, t in enumerate(tok):
        per_riga[t[2]].append(j)
    out = np.zeros((n_p, 2, 2))
    for jj in per_riga.values():
        for a in jj:
            for b in jj:
                d = tok[b][3] - tok[a][3]
                if not 1 <= d <= 3:
                    continue
                stessa = tok[a][5] == tok[b][5]
                if stessa and (tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7])):
                    continue
                pa, pb = [], []
                for j, lst in ((a, pa), (b, pb)):
                    ch = (tok[j][0], tok[j][5])
                    if npg[ch] > 1:
                        off = (sp[ch] - v[j]) / (npg[ch] - 1)
                        xm = (sx[ch] - x[j]) / (npg[ch] - 1)
                        lst.append(tipo[j] + off - mano[j] + beta[tok[j][5]] * (x[j] - xm))
                    else:
                        lst.append(tipo[j])
                p1, p2 = min(max(pa[0], 0.01), 0.99), min(max(pb[0], 0.01), 0.99)
                att = p1 * p2 + (1 - p1) * (1 - p2)
                g = 0 if stessa else 1
                out[tok[a][0], g, 0] += (v[a] == v[b]) - att
                out[tok[a][0], g, 1] += 1 - att
    return out


def incrocio(pagine, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    tok = e3c33.raccogli(pagine, cl)
    n_p = len(pagine)
    oss = somme_incrocio(tok, n_p)
    nul = np.mean([somme_incrocio(e3c48.rimescola(tok, rng), n_p) for _ in range(PERM)], axis=0)
    k = lambda s, n: s[..., 0].sum(0) / s[..., 1].sum(0) - n[..., 0].sum(0) / n[..., 1].sum(0)
    kc = k(oss, nul)
    boot = np.array([k(oss[i], nul[i]) for i in (rng.integers(0, n_p, n_p) for _ in range(BOOT))])
    ic = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    ko = oss.sum(0)[:, 0] / oss.sum(0)[:, 1]
    return OrderedDict([('stessa scelta', OrderedDict([('K_osservato', float(ko[0])), ('K_corretto', float(kc[0])), ('IC95', ic(boot[:, 0]))])),
                        ('scelte diverse', OrderedDict([('K_osservato', float(ko[1])), ('K_corretto', float(kc[1])), ('IC95', ic(boot[:, 1]))]))])


def main():
    rng = np.random.default_rng(3366)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        a = durata(pagine, rng)
        print(q, 'durata', json.dumps(a), flush=True)
        b = incrocio(pagine, rng)
        print(q, 'incrocio', json.dumps(b), flush=True)
        if a['K_4_6_IC95'][0] > 0.02:
            ea = 'lo stato dura più di tre parole'
        elif a['K_4_6_IC95'][0] <= 0 <= a['K_4_6_IC95'][1] and a['K_1_3_IC95'][0] > 0.02:
            ea = 'lo stato dura circa tre parole e poi si spegne'
        else:
            ea = 'incerto'
        s, dv = b['stessa scelta'], b['scelte diverse']
        if dv['IC95'][0] > 0 and dv['K_corretto'] >= s['K_corretto'] / 3:
            eb = 'stato comune a scelte diverse'
        elif dv['IC95'][0] <= 0 or dv['K_corretto'] < s['K_corretto'] / 4:
            eb = 'uno stato separato per ogni scelta'
        else:
            eb = 'incerto'
        ris[q] = OrderedDict([('durata', a), ('incrocio', b), ('esito_durata', ea), ('esito_incrocio', eb)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c66_forma_stato.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c66 — La forma dello stato', '', 'Preregistrazione: `preregistrazioni/e3c66.md`.', '', '## A. Durata (righe di almeno 8 parole; k/t, sh/ch, -ey/-dy)', '',
          '| trascrizione | parole | K corretto a 1 / 2 / 3 / 4 / 5 / 6 parole | media 1–3 (IC) | media 4–6 (IC) | ρ (IC) | mezza vita in parole (IC) | esito |', '|---|---|---|---|---|---|---|---|']
    for q, x in ris.items():
        a = x['durata']
        md.append('| %s | %d | %s | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %.1f (%.1f – %.1f) | %s |' % (
            q, a['parole'], ' / '.join('%+.3f' % z for z in a['K_corretto']), a['K_1_3'], a['K_1_3_IC95'][0], a['K_1_3_IC95'][1], a['K_4_6'], a['K_4_6_IC95'][0], a['K_4_6_IC95'][1],
            a['rho'], a['rho_IC95'][0], a['rho_IC95'][1], a['mezza_vita_parole'], a['mezza_vita_IC95'][0], min(a['mezza_vita_IC95'][1], 99), x['esito_durata']))
    md += ['', '## B. Stessa scelta o scelte diverse (distanza 1–3; 1 = qo, k, sh, -ey)', '', '| trascrizione | stessa scelta: K corretto (IC) | scelte diverse: K corretto (IC) | esito |', '|---|---|---|---|']
    for q, x in ris.items():
        s, dv = x['incrocio']['stessa scelta'], x['incrocio']['scelte diverse']
        md.append('| %s | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) | %s |' % (q, s['K_corretto'], s['IC95'][0], s['IC95'][1], dv['K_corretto'], dv['IC95'][0], dv['IC95'][1], x['esito_incrocio']))
    open(os.path.join(RISULTATI, 'e3c66_forma_stato.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
