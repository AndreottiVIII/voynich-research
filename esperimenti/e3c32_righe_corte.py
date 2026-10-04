# -*- coding: utf-8 -*-
"""Esperimento e3c32: perché nelle righe corte l'accordo delle scelte è più alto? Accordo K fra parole a distanza 1, 2, 3
nella stessa riga (righe senza la prima e l'ultima parola), separato per righe corte (4–8 parole) e lunghe (almeno 9), con
due attesi: (a) dalla stessa parola coperta nella mano; (b) come (a) più lo scarto della pagina (quota della classe nella
pagina, lasciando fuori la parola, meno quota della classe nella mano). Differenza corte − lunghe ricampionando pagine.
ZL e IT, classi scelte a mano.

Preregistrazione: preregistrazioni/e3c32.md. Scrive risultati/e3c32_righe_corte.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
VERSIONI = ('stessa parola', 'stessa parola e pagina')
RESTRINGI = 0  # 0 = scarto di pagina pieno (provato anche 20: toglie solo metà dell'effetto di pagina)


def raccogli(pd, mano):
    """Parole delle classi: (pagina, mano, gruppo di riga, id riga, posizione, classe, valore, parola coperta)."""
    tok = []
    nr = 0
    for p, (pg, pars) in enumerate(pd.items()):
        h = mano.get(pg)
        if not h:
            continue
        for par in pars:
            for r in par:
                ws = [tuple(e3b62.D(w)) for w in r]
                ws = [w for w in ws if w]
                nr += 1
                if len(ws) < 4:
                    continue
                g = 0 if len(ws) <= 8 else 1
                for i, w in enumerate(ws[1:-1]):
                    for k, f in e3b62.CV.items():
                        x = f(w)
                        if x is not None:
                            tok.append((p, h, g, nr, i, k, x[0], x[1]))
    return tok


def attese(tok):
    """Atteso dalla stessa parola (lasciando fuori la parola) e somme di pagina e di mano per lo scarto di pagina."""
    v = np.array([t[6] for t in tok], dtype=float)
    def loo(chiavi):
        s, n = defaultdict(float), defaultdict(int)
        for c, x in zip(chiavi, v):
            s[c] += x
            n[c] += 1
        return np.array([(s[c] - x) / (n[c] - 1) if n[c] > 1 else np.nan for c, x in zip(chiavi, v)])
    tipo = loo([(t[1], t[5], t[7]) for t in tok])
    classe_mano = loo([(t[1], t[5]) for t in tok])
    classe_pagina = loo([(t[0], t[5]) for t in tok])
    tipo = np.where(np.isnan(tipo), classe_mano, tipo)
    sp, npag = defaultdict(float), defaultdict(int)
    for t, x in zip(tok, v):
        sp[(t[0], t[5])] += x
        npag[(t[0], t[5])] += 1
    return v, tipo, classe_mano, sp, npag


def somme(tok, n_p):
    """(pagina, gruppo, distanza 1-3, versione, [accordi − attesi, coppie − attesi])."""
    v, tipo, classe_mano, sp, npag = attese(tok)
    per_riga = defaultdict(list)
    for j, t in enumerate(tok):
        per_riga[(t[3], t[5])].append(j)
    out = np.zeros((n_p, 2, 3, len(VERSIONI), 2))
    for (_, _), idx in per_riga.items():
        pos = {tok[j][4]: j for j in idx}
        for a in idx:
            for d in (1, 2, 3):
                b = pos.get(tok[a][4] + d)
                if b is None:
                    continue
                if tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                    continue
                ch = (tok[a][0], tok[a][5])
                if npag[ch] > 2:
                    off = (sp[ch] - v[a] - v[b]) / (npag[ch] - 2)
                    w = (npag[ch] - 2) / (npag[ch] - 2 + RESTRINGI)
                    oa, ob = w * (off - classe_mano[a]), w * (off - classe_mano[b])
                else:
                    oa = ob = 0.0
                pp = {'stessa parola': (tipo[a], tipo[b]), 'stessa parola e pagina': (tipo[a] + oa, tipo[b] + ob)}
                for iv, ver in enumerate(VERSIONI):
                    pi, pj = (min(max(z, 0.01), 0.99) for z in pp[ver])
                    att = pi * pj + (1 - pi) * (1 - pj)
                    out[tok[a][0], tok[a][2], d - 1, iv, 0] += (v[a] == v[b]) - att
                    out[tok[a][0], tok[a][2], d - 1, iv, 1] += 1 - att
    return out


def kappa(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        return s[..., 0] / s[..., 1]


def main():
    rng = np.random.default_rng(3332)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        tok = raccogli(pd, mano)
        n_p = max(t[0] for t in tok) + 1
        st = somme(tok, n_p)
        k = kappa(st.sum(0))
        boot = np.array([kappa(st[rng.integers(0, n_p, n_p)].sum(0)) for _ in range(BOOT)])
        x = OrderedDict()
        for iv, ver in enumerate(VERSIONI):
            y = OrderedDict()
            for d in range(3):
                dif = boot[:, 0, d, iv] - boot[:, 1, d, iv]
                y['d=%d' % (d + 1)] = OrderedDict([('corte', float(k[0, d, iv])), ('lunghe', float(k[1, d, iv])), ('corte − lunghe', float(k[0, d, iv] - k[1, d, iv])),
                                                    ('IC95', [float(np.nanpercentile(dif, 2.5)), float(np.nanpercentile(dif, 97.5))])])
            x[ver] = y
        ris[q] = x
        print(q, json.dumps(x), flush=True)
    esiti = OrderedDict()
    for q in ris:
        a, b = ris[q]['stessa parola']['d=1'], ris[q]['stessa parola e pagina']['d=1']
        if a['IC95'][0] <= 0 <= a['IC95'][1]:
            esiti[q] = 'nessuna differenza fra righe corte e lunghe'
        elif a['IC95'][0] > 0 and b['corte − lunghe'] < a['corte − lunghe'] / 2:
            esiti[q] = 'le righe corte hanno più accordo per le preferenze di pagina'
        elif b['IC95'][0] > 0 and b['corte − lunghe'] >= 2 / 3 * a['corte − lunghe']:
            esiti[q] = "l'accordo in più delle righe corte non viene dalla pagina"
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c32_righe_corte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c32 — Perché nelle righe corte l\'accordo delle scelte è più alto?', '', 'Preregistrazione: `preregistrazioni/e3c32.md`. K a distanza d nella riga (senza bordi), righe corte (4–8 parole) e lunghe (9+).', '',
          '| trascrizione | atteso | d | corte | lunghe | corte − lunghe (IC 95%) |', '|---|---|---|---|---|---|']
    for q, x in ris.items():
        for ver, y in x.items():
            for d, z in y.items():
                md.append('| %s | %s | %s | %+.3f | %+.3f | %+.3f (%+.3f – %+.3f) |' % (q, ver, d, z['corte'], z['lunghe'], z['corte − lunghe'], z['IC95'][0], z['IC95'][1]))
    md += [''] + ['Esito %s (d = 1): **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c32_righe_corte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
