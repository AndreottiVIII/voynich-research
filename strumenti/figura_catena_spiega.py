# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): per ogni proprieta', quanto la catena di segni per riga (ordine 2) la riproduce
(R = riscritto / vero), dagli esperimenti e3a78 (ZL), e3a80 (Takahashi) ed e3a81 (ZL).
Scrive risultati/figure/catena_spiega.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')


def carica(nome):
    return json.load(open(os.path.join(R, nome), encoding='utf-8'))['sintesi']


def main():
    zl = carica('e3a78_cosa_spiega_la_catena.json')
    it = carica('e3a80_catena_takahashi.json')
    pg = carica('e3a81_catena_pagina.json')
    voci = [(n, zl[n]['R'], it[n]['R']) for n in zl] + [(n, x['R'], None) for n, x in pg.items()]
    ordine = sorted(voci, key=lambda v: -v[1])
    fig, ax = plt.subplots(figsize=(9, 5.2))
    y = np.arange(len(ordine))[::-1]
    for yy, (n, rz, ri) in zip(y, ordine):
        col = 'tab:green' if rz >= 0.75 else ('tab:orange' if rz >= 0.25 else 'tab:red')
        ax.barh(yy + 0.18, rz, height=0.34, color=col)
        if ri is not None:
            ax.barh(yy - 0.18, ri, height=0.34, color=col, alpha=0.45)
    ax.set_yticks(y)
    ax.set_yticklabels([v[0] for v in ordine], fontsize=9)
    ax.axvline(1, color='0.4', lw=0.8, ls='--')
    ax.axvline(0.75, color='0.8', lw=0.8)
    ax.axvline(0.25, color='0.8', lw=0.8)
    ax.axvline(0, color='0.4', lw=0.8)
    ax.set_xlim(-0.3, 1.45)
    ax.set_xlabel('R = proprietà nel Voynich riscritto da una catena di segni per riga / nel Voynich vero\n(barra piena: ZL; barra chiara: Takahashi)')
    ax.set_title('Che cosa spiega da sola una catena di segni scritta riga per riga')
    ax.text(1.13, y[0] + 0.4, 'orizzontali:\nspiegate', fontsize=8, color='tab:green', va='top')
    ax.text(0.27, y[-1] - 0.3, 'verticali: serve altro\n(lo scriba guarda la riga sopra,\nil paragrafo, la pagina)', fontsize=8, color='tab:red', va='bottom')
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'catena_spiega.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
