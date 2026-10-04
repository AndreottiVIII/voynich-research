# -*- coding: utf-8 -*-
"""Esperimento e3c75: la componente lenta che attraversa le righe (e3c74) è una tendenza dall'alto in basso nella pagina
o uno stato lento? K corretto (e3c48) per coppie della stessa scelta secondo la distanza in righe nella stessa pagina
(0 = stessa riga a distanza ≥ 5 parole; 1; 2; 3; 4 – 6; 7 – 12), con due attesi: A = quello dell'e3c48 (parola coperta +
pagina + deriva lungo la riga); B = A più una deriva verticale (pendenza della scelta sul numero di riga nella pagina,
a parità di parola coperta, stimata come la deriva lungo la riga). Voynich ZL e IT, qo/o, k/t, sh/ch, -ey/-dy.

Preregistrazione: preregistrazioni/e3c75.md. Scrive risultati/e3c75_componente_lenta.json e .md.
"""
import json, os, sys
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
import e3c10_strati_lettere_parole as e3c10
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48
import e3c68_segno_che_azzera as e3c68

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
GRUPPI = ('stessa riga (≥ 5 parole)', '1 riga', '2 righe', '3 righe', '4–6 righe', '7–12 righe')
PERM = 30
BOOT = 2000


def gruppo(dr):
    return {0: 0, 1: 1, 2: 2, 3: 3}.get(dr, 4 if dr <= 6 else (5 if dr <= 12 else None))


def attese_b(tok, v, p):
    """Aggiunge all'atteso la deriva verticale: pendenza sul numero di riga nella pagina, a parità di (mano, parola coperta)."""
    prima = {}
    for t in tok:
        prima[t[0]] = min(prima.get(t[0], t[2]), t[2])
    riga = np.array([t[2] - prima[t[0]] for t in tok], dtype=float)
    pb = p.copy()
    for k in {t[5] for t in tok}:
        idx = np.array([j for j, t in enumerate(tok) if t[5] == k])
        _, strato = np.unique(np.array([hash((tok[j][1], tok[j][7])) for j in idx]), return_inverse=True)
        st = e3c10.statistiche(strato, riga[idx], v[idx], np.zeros(len(idx), dtype=int), 1, int(strato.max()) + 1)
        beta = float(e3c10.pendenza(st.sum(0)))
        s, n = defaultdict(float), defaultdict(int)
        for j in idx:
            s[tok[j][0]] += riga[j]
            n[tok[j][0]] += 1
        for j in idx:
            pg = tok[j][0]
            m = (s[pg] - riga[j]) / (n[pg] - 1) if n[pg] > 1 else riga[j]
            pb[j] = p[j] + beta * (riga[j] - m)
    return np.clip(pb, 0.01, 0.99)


def somme(tok, n_p):
    v, p = e3c68.attese(tok)
    pb = attese_b(tok, v, p)
    per = defaultdict(list)
    for j, t in enumerate(tok):
        per[(t[0], t[5])].append(j)
    out = np.zeros((n_p, 2, len(GRUPPI), 2))
    for (pg, k), jj in per.items():
        for x, a in enumerate(jj):
            for b in jj[x + 1:]:
                dr = abs(tok[b][2] - tok[a][2])
                if dr == 0 and abs(tok[b][3] - tok[a][3]) < 5:
                    continue
                g = gruppo(dr)
                if g is None or tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                    continue
                for e, q in enumerate((p, pb)):
                    att = q[a] * q[b] + (1 - q[a]) * (1 - q[b])
                    out[pg, e, g, 0] += (v[a] == v[b]) - att
                    out[pg, e, g, 1] += 1 - att
    return out


def kappa(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        return s[..., 0] / s[..., 1]


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    oss = somme(tok, n_p)
    nul = np.mean([somme(e3c48.rimescola(tok, rng), n_p) for _ in range(PERM)], axis=0)
    kc = kappa(oss.sum(0)) - kappa(nul.sum(0))
    boot = np.array([kappa(oss[i].sum(0)) - kappa(nul[i].sum(0)) for i in (rng.integers(0, n_p, n_p) for _ in range(BOOT))])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ris = OrderedDict([('parole', len(tok))])
    for e, nome in enumerate(('A (senza deriva verticale)', 'B (con deriva verticale)')):
        ris[nome] = OrderedDict((g, OrderedDict([('K_corretto', float(kc[e, i])), ('IC95', ic(boot[:, e, i]))])) for i, g in enumerate(GRUPPI))
    return ris


def voce(x):
    a, b = x['A (senza deriva verticale)']['1 riga'], x['B (con deriva verticale)']['1 riga']
    if a['K_corretto'] > 0 and b['IC95'][0] <= 0.0 and b['K_corretto'] <= a['K_corretto'] / 3:
        return 'è la tendenza verticale della pagina'
    if b['IC95'][0] > 0 and b['K_corretto'] >= 2 * a['K_corretto'] / 3:
        return 'è uno stato lento (la tendenza verticale non la spiega)'
    if b['IC95'][0] > 0:
        return 'in parte tendenza verticale, in parte stato lento'
    return 'incerto'


def main():
    rng = np.random.default_rng(3375)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        x = misura(pagine, cl, rng)
        x['voce'] = voce(x)
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    a, b = ris['ZL']['voce'], ris['IT']['voce']
    esito = a if a == b else 'ZL: %s; IT: %s' % (a, b)
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c75_componente_lenta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c75 — La componente lenta: tendenza verticale o stato lento?', '', 'Preregistrazione: `preregistrazioni/e3c75.md`.', '',
          '| trascrizione, atteso | ' + ' | '.join(GRUPPI) + ' |', '|---|' + '---|' * len(GRUPPI)]
    for q, x in ris.items():
        for e in ('A (senza deriva verticale)', 'B (con deriva verticale)'):
            md.append('| %s, %s | %s |' % (q, e, ' | '.join('%+.3f (%+.3f – %+.3f)' % (x[e][g]['K_corretto'], x[e][g]['IC95'][0], x[e][g]['IC95'][1]) for g in GRUPPI)))
    md += ['', 'Esito: **%s**.' % esito] + ['- %s: %s' % (q, x['voce']) for q, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3c75_componente_lenta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
