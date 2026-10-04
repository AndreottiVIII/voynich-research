# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo), versione corretta dopo e3b71/e3b72: nelle 6 pagine "solo testo" la giuntura fra
l'ultimo segno di una riga e il primo della seguente resta (e3a06, e3b72), mentre la memoria delle scelte passa l'a capo
come nelle altre pagine (e3b71). Scrive risultati/figure/solo_testo.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')


def carica(nome):
    return json.load(open(os.path.join(R, nome), encoding='utf-8'))


def main():
    g = carica('e3b72_giuntura_solo_testo_it.json')['misure']
    m = carica('e3b71_solo_testo_potenza.json')['trascrizioni']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
    voci = [('solo testo,\nriga sotto (ZL)', g['ZL, riga sotto']['E'], 'crimson'), ('solo testo,\nriga sotto (IT)', g['IT, riga sotto']['E'], 'crimson'),
            ('solo testo,\nriga sopra (ZL)', g['ZL, riga sopra']['E'], '0.6'), ('solo testo,\nriga sopra (IT)', g['IT, riga sopra']['E'], '0.6'),
            ('altre pagine, stessa\nquantità (mediana, IT)', g['IT, riga sotto']['taratura_mediana'], '0.6')]
    a1.bar(range(len(voci)), [v[1] for v in voci], color=[v[2] for v in voci])
    for i, v in enumerate(voci[:4]):
        p = g[['ZL, riga sotto', 'IT, riga sotto', 'ZL, riga sopra', 'IT, riga sopra'][i]]['p_esatto']
        a1.text(i, max(v[1], 0) + 0.004, ('p %.4f' % p).replace('.', ','), ha='center', fontsize=7)
    a1.axhline(0, color='0.3', lw=0.8)
    a1.set_xticks(range(len(voci)))
    a1.set_xticklabels([v[0] for v in voci], fontsize=7)
    a1.set_ylabel("legame fra l'ultimo segno di una riga\ne il primo della seguente (bit in più del caso)", fontsize=8)
    a1.set_title('Giuntura a capo: passa solo nelle pagine di solo testo', fontsize=10)
    xs, vals, los, his, cols, nomi = [], [], [], [], [], []
    for i, (q, k) in enumerate((('ZL', 'T'), ('IT', 'T'), ('ZL', 'N'), ('IT', 'N'))):
        x = m[q]
        if k == 'T':
            v, ic, col, nome = x['D_T'], x['IC95_T'], 'crimson', 'solo testo (%s)' % q
        else:
            v, ic, col, nome = x['D_normali'], None, '0.55', 'altre pagine (%s)' % q
        xs.append(i)
        vals.append(v)
        cols.append(col)
        nomi.append(nome)
        if ic:
            a2.errorbar(i, v, yerr=[[v - ic[0]], [ic[1] - v]], color='0.2', capsize=3)
    a2.bar(xs, vals, color=cols)
    a2.axhline(0, color='0.3', lw=0.8)
    a2.set_xticks(xs)
    a2.set_xticklabels(nomi, fontsize=8)
    a2.set_ylabel("memoria delle scelte a cavallo dell'a capo\n(continuazione − righe vicine)", fontsize=8)
    a2.set_title("Memoria delle scelte: passa l'a capo per metà, dappertutto", fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'solo_testo.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
