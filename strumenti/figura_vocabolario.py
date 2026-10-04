# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): quattro misure di vocabolario e spazi (e3a55, e3a61, e3a58, e3a67) per Voynich,
71 lingue, gibberish scritto a mano e generatori. Scrive risultati/figure/vocabolario.png.
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


def pannelli():
    a = carica('e3a55_frequenza_forma.json')
    b = carica('e3a61_forme_riempite.json')
    c = carica('e3a58_spazi_prevedibili.json')['parte1']
    d = carica('e3a67_spazi_rifatti.json')
    gen = ('Naibbe (Greshko 2025), a capo', 'U2 (Whitehatnetizen 2026)', 'U3 (Whitehatnetizen 2026)', 'Timm e Schinner, seme 1')
    return [
        ('La frequenza segue la forma\n(ρ, e3a55)', list(a['testi_sensati'].values()), a['Voynich']['mediana_10000'], a['gibberish umano']['rho'], [a[g]['rho'] for g in gen]),
        ('Forme probabili presenti\nnel vocabolario (e3a61)', [x['riempimento'] for x in b['testi_sensati'].values()], b['altri']['Voynich']['riempimento'],
         b['altri']['gibberish umano']['riempimento'], [b['altri'][g]['riempimento'] for g in gen]),
        ('Spazi indovinati dai\nsegni vicini (F1, e3a58)', list(c['testi_sensati'].values()), c['altri']['Voynich']['f1'], c['altri']['gibberish umano']['f1'], [c['altri'][g]['f1'] for g in gen]),
        ('Tagli sbagliati che sono\nparole vere (e3a67)', list(d['testi_sensati'].values()), d['altri']['Voynich']['attestazione'], d['altri']['gibberish umano']['attestazione'],
         [d['altri'][g]['attestazione'] for g in gen]),
    ]


def main():
    fig, axes = plt.subplots(1, 4, figsize=(13, 4.6), sharey=False)
    rnd = np.random.default_rng(0)
    for i, (ax, (tit, lingue, v, g, gg)) in enumerate(zip(axes, pannelli())):
        ax.scatter(rnd.uniform(-0.15, 0.15, len(lingue)), lingue, s=14, c='0.6', label='lingue vere (71 testi)' if i == 0 else None)
        ax.scatter([0], [v], s=220, marker='*', c='crimson', zorder=5, label='Voynich' if i == 0 else None)
        ax.scatter([0.5], [g], s=55, marker='s', c='tab:blue', label='gibberish scritto a mano' if i == 0 else None)
        ax.scatter([0.9] * len(gg), gg, s=40, marker='^', c='tab:green', label='generatori (Naibbe, U2, U3, Timm e Schinner)' if i == 0 else None)
        ax.set_xlim(-0.5, 1.2)
        ax.set_xticks([])
        ax.set_ylim(-0.2 if min(lingue) < 0 else 0, 1)
        ax.set_title(tit, fontsize=10)
    fig.legend(loc='lower center', ncol=4, fontsize=8, frameon=False)
    fig.suptitle('Vocabolario e spazi: il Voynich sta con i generatori, non con le lingue', fontsize=11)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'vocabolario.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
