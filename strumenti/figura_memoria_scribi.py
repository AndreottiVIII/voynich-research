# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): memoria delle scelte di grafia oltre le parole (effetto = M osservata − media del
nullo largo dell'e3b62), con intervalli al 95% ricampionando pagine o blocchi interi (e3b70): Voynich ZL e IT e per
mano, scriba anglosassone (þ/ð, i/y), altri testi storici (i/y), Codex Marianus (e3b75), generatori. Scrive risultati/figure/memoria_scribi.png.
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
    a = carica('e3b70_memoria_intervalli.json')['intervalli']
    voce = [('Voynich ZL', 'Voynich ZL, tutto', 'crimson'), ('Voynich Takahashi', 'Voynich IT, tutto', 'crimson'),
            ('Voynich ZL, mano 1', 'Voynich ZL, mano 1', '#e88'), ('Voynich ZL, mano 2', 'Voynich ZL, mano 2', '#e88'),
            ('Voynich ZL, mano 3', 'Voynich ZL, mano 3', '#e88'),
            ('scriba anglosassone,\nþ/ð a inizio parola', 'Hatton Gospels, þ/ð a inizio parola', 'tab:blue'),
            ('scriba anglosassone,\ni/y', 'Hatton Gospels, i/y', '#8ac'),
            ('Secreta Alberti\n(inglese), i/y', 'Secreta Alberti, i/y', '#8ac'),
            ('Naibbe', 'Naibbe (Greshko 2025), a capo', 'tab:green'), ('U2', 'U2 (Whitehatnetizen 2026)', 'tab:green'),
            ('U3', 'U3 (Whitehatnetizen 2026)', 'tab:green'), ('Timm e Schinner', 'Timm e Schinner, seme 1', 'tab:green')]
    mar = carica('e3b75_marianus.json')
    a['Codex Marianus, и/ꙇ'] = {'effetto': mar['effetto'], 'IC95': mar['IC95']}
    voce.insert(8, ('Codex Marianus, due\nforme di i a inizio parola', 'Codex Marianus, и/ꙇ', 'tab:purple'))
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    for i, (nome, k, col) in enumerate(voce):
        x = a[k]
        e, (lo, hi) = x['effetto'], x['IC95']
        ns = lo <= 0 <= hi
        ax.bar(i, e, color=col, alpha=0.45 if ns else 1.0, hatch='//' if ns else None, edgecolor='0.4' if ns else col)
        ax.errorbar(i, e, yerr=[[e - lo], [hi - e]], color='0.2', capsize=3)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor='0.85', hatch='//', edgecolor='0.4', label="intervallo che tocca lo zero")], fontsize=8, frameon=False, loc='upper right')
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xticks(np.arange(len(voce)))
    ax.set_xticklabels([v[0] for v in voce], rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('memoria delle scelte oltre le parole\n(normalizzata, vicine − lontane, meno il nullo)')
    ax.set_title('Memoria corta delle scelte: solida nel Voynich (tutte le mani), assente nei generatori, incerta o opposta negli scribi veri', fontsize=10)
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'memoria_scribi.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
