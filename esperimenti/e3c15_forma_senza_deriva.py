# -*- coding: utf-8 -*-
"""Esperimento e3c15: la forma del calo (R = [K(3) − K(8–12)] / [K(1) − K(8–12)], e3b96) senza la deriva lungo la riga.

- A, come l'e3b96: atteso dalla quota della pagina, con i bordi della riga;
- B (principale): righe senza la prima e l'ultima parola; atteso di ogni parola corretto per la deriva:
  p_i = quota della pagina + β·(x_i − x̄), con x = segni scritti prima nella riga e β = pendenza della scelta su x a
  parità di parola coperta (e3c13), stimata sul testo intero per ciascuna classe;
- C: righe senza bordi, atteso dalla quota della pagina (per separare l'effetto dei bordi da quello della deriva).

Profilo d = 1…7 descrittivo. ZL e IT, classi scelte a mano, intervalli ricampionando pagine.

Preregistrazione: preregistrazioni/e3c15.md. Scrive risultati/e3c15_forma_senza_deriva.json e .md.
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
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
SOGLIA = 0.45
GRUPPI = ['1', '2', '3', '4', '5', '6', '7', 'lontane']


def gruppo(d):
    return GRUPPI.index('lontane') if d >= 8 else int(d) - 1


def posizioni(uu, f):
    """Segni scritti prima nella riga per ogni parola della classe, nell'ordine in cui la numera prepara."""
    out = []
    for righe in uu:
        for r in righe:
            prima = 0
            for w in r:
                if f(w) is not None:
                    out.append(prima)
                prima += len(w)
    return np.array(out, dtype=float)


def beta(c, x):
    """Pendenza della scelta su x a parità di parola coperta (gruppi di rimescolamento = mano e parola coperta)."""
    st = e3c10.statistiche(c['grp'], x, c['val'], np.zeros(len(x), dtype=int), 1, int(c['grp'].max()) + 1)
    return float(e3c10.pendenza(st.sum(0)))


def somme(cc, n_u, correggi):
    """(unità, gruppo, [accordi, attesi, coppie]); se correggi = {classe: (x, β)} l'atteso tiene conto della deriva."""
    out = np.zeros((n_u, len(GRUPPI), 3))
    for k, c in cc.items():
        val = c['val']
        U = np.bincount(c['uni'], weights=val, minlength=n_u)
        vi, vj = val[c['I']], val[c['J']]
        u = c['uni'][c['I']]
        p0 = (U[u] - vi - vj) / (c['T'][u] - 2)
        if correggi:
            x, b = correggi[k]
            xm = np.bincount(c['uni'], weights=x, minlength=n_u) / np.maximum(np.bincount(c['uni'], minlength=n_u), 1)
            pi = np.clip(p0 + b * (x[c['I']] - xm[u]), 0.01, 0.99)
            pj = np.clip(p0 + b * (x[c['J']] - xm[u]), 0.01, 0.99)
        else:
            pi = pj = p0
        att = pi * pj + (1 - pi) * (1 - pj)
        ok = (vi == vj).astype(float)
        chiave = u * len(GRUPPI) + np.array([gruppo(d) for d in c['d']])
        for col, w in enumerate((ok, att, np.ones_like(ok))):
            out[..., col] += np.bincount(chiave, weights=w, minlength=n_u * len(GRUPPI)).reshape(n_u, len(GRUPPI))
    return out


def kappa(s):
    o, a, n = s[..., 0], s[..., 1], s[..., 2]
    return (o - a) / (n - a)


def erre(k):
    l = k[..., GRUPPI.index('lontane')]
    den = k[..., 0] - l
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(den > 0, (k[..., 2] - l) / den, np.nan)


def una(uu, ss, classi, correggere, rng):
    e3c09.DIST = range(1, 13)
    cc = OrderedDict((k, e3c09.prepara(uu, ss, f)) for k, f in classi.items())
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
    correggi = None
    if correggere:
        correggi = {}
        for k, c in cc.items():
            x = posizioni(uu, classi[k])
            correggi[k] = (x, beta(c, x))
    st = somme(cc, len(uu), correggi)
    k = kappa(st.sum(0))
    boot = np.array([erre(kappa(st[rng.integers(0, len(uu), len(uu))].sum(0))) for _ in range(BOOT)])
    boot = boot[np.isfinite(boot)]
    l = k[GRUPPI.index('lontane')]
    out = OrderedDict([('R', float(erre(k))), ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]),
                       ('profilo', OrderedDict((g, float(k[i] - l)) for i, g in enumerate(GRUPPI[:-1])))])
    if correggi:
        out['beta_per_10_segni'] = OrderedDict((kk, 10 * v[1]) for kk, v in correggi.items())
    return out


def main():
    rng = np.random.default_rng(3315)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        sb = e3c07.senza_bordi(uu)
        ris[q] = OrderedDict([('A: come e3b96 (con i bordi)', una(uu, ss, e3b62.CV, False, rng)),
                              ('B: senza bordi, atteso corretto per la deriva', una(sb, ss, e3b62.CV, True, rng)),
                              ('C: senza bordi, atteso solito', una(sb, ss, e3b62.CV, False, rng))])
        print(q, json.dumps(ris[q]), flush=True)
    b = [ris[q]['B: senza bordi, atteso corretto per la deriva'] for q in ('ZL', 'IT')]
    if all(x['IC95'][0] > SOGLIA for x in b):
        esito = 'la forma piatta regge senza la deriva'
    elif all(x['R'] < SOGLIA for x in b):
        esito = 'senza la deriva la forma non è più piatta'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c15_forma_senza_deriva.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c15 — La forma del calo senza la deriva lungo la riga', '', 'Preregistrazione: `preregistrazioni/e3c15.md`. R = [K(3) − K(8–12)] / [K(1) − K(8–12)]. Lingue (e3b96–e3b98): mediana 0,16, massimo fra le lingue naturali 0,45 (Plinio).', '',
          '| trascrizione | versione | R (IC 95%) | profilo d = 1…7 |', '|---|---|---|---|']
    for q, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s | %.2f (%.2f – %.2f) | %s |' % (q, k, y['R'], y['IC95'][0], y['IC95'][1], ' '.join('%+.3f' % v for v in y['profilo'].values())))
    md += ['', 'Esito (versione B): **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c15_forma_senza_deriva.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
