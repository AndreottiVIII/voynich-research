# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): memoria delle scelte di grafia oltre le parole (effetto = M osservata − M del
nullo che tiene ferme le parole), Voynich ZL e IT, scriba anglosassone (þ/ð, i/y), altri testi storici (i/y), generatori
(e3b56, e3b57). Scrive risultati/figure/memoria_scribi.png.
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
    a = carica('e3b56_memoria_oltre_parole_corretta.json')['gruppi']
    g = carica('e3b57_memoria_generatori.json')['generatori']
    voce = [('Voynich ZL', a['Voynich ZL']['insieme'], 'crimson'), ('Voynich Takahashi', a['Voynich IT']['insieme'], 'crimson'),
            ('Voynich ZL, qo/o', a['Voynich ZL']['qo/o'], '#e88'), ('Voynich ZL, -ey/-dy', a['Voynich ZL']['-ey/-dy'], '#e88'),
            ('scriba anglosassone,\nþ/ð a inizio parola', a['naturali']['Hatton Gospels, þ/ð a inizio parola'], 'tab:blue'),
            ('scriba anglosassone,\ni/y', a['naturali']['Hatton Gospels, i/y'], '#8ac'),
            ('Secreta Alberti\n(inglese), i/y', a['naturali']['Secreta Alberti, i/y'], '#8ac'),
            ('NT fiammingo,\ni/y', a['naturali']['NT fiammingo, i/y'], '#8ac')]
    nomi = {'Naibbe (Greshko 2025), a capo': 'Naibbe', 'U2 (Whitehatnetizen 2026)': 'U2', 'U3 (Whitehatnetizen 2026)': 'U3', 'Timm e Schinner, seme 1': 'Timm e Schinner'}
    for k, x in g.items():
        voce.append((nomi.get(k, k), x['insieme'], 'tab:green'))
    fig, ax = plt.subplots(figsize=(11, 4.8))
    xs = np.arange(len(voce))
    for i, x in enumerate(voce):
        p = x[1]['p']
        ns = p > 0.05
        ax.bar(i, x[1]['effetto'], color=x[2], alpha=0.45 if ns else 1.0, hatch='//' if ns else None, edgecolor='0.4' if ns else x[2])
        testo = ('p %.3f' % p).replace('.', ',') if p >= 0.001 else 'p < 0,001'
        ax.text(i, max(x[1]['effetto'], 0) + 0.003, testo, ha='center', fontsize=7)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor='0.85', hatch='//', edgecolor='0.4', label='non significativo (p > 0,05)')], fontsize=8, frameon=False, loc='upper right')
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([x[0] for x in voce], rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('memoria delle scelte oltre le parole\n(accordo normalizzato, vicine − lontane, meno il nullo)')
    ax.set_title('La memoria corta delle scelte: c\'è nel Voynich e in uno scriba vero, non nei generatori')
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'memoria_scribi.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
