# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): ripetizione di una parola nella stessa riga, eccesso entro 1-4 parole e a 7-10
parole, per Voynich (e3a87), lingue (e3a89), generatori e gibberish (e3a90). Scrive risultati/figure/memoria_corta.png.
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
    v = carica('e3a87_ripresa_distanza.json')['profilo']

    def mv(dd):
        xs = [(v[str(d)]['stessa riga']['eccesso'], v[str(d)]['stessa riga']['coppie']) for d in dd]
        return sum(e * n for e, n in xs) / sum(n for _, n in xs)
    voce = [('Voynich', mv(range(1, 5)), mv(range(7, 11)), 'crimson')]
    l = carica('e3a89_ripresa_lingue.json')['testi_sensati']
    usati = [x for x in l.values() if x['coppie_stessa_d7_10'] >= 500 and x['stessa_d1_4'] is not None]
    voce.append(('lingue (mediana di %d)' % len(usati), float(np.median([x['stessa_d1_4'] for x in usati])), float(np.median([x['stessa_d7_10'] for x in usati])), '0.5'))
    g = carica('e3a90_ripresa_generatori.json')
    nomi = {'Naibbe (Greshko 2025), a capo': 'Naibbe', 'U2 (Whitehatnetizen 2026)': 'U2', 'U3 (Whitehatnetizen 2026)': 'U3',
            'Timm e Schinner, seme 1': 'Timm e Schinner', 'gibberish umano': 'gibberish umano'}
    for k, x in g.items():
        voce.append((nomi.get(k, k), x['stessa_d1_4'], x['stessa_d7_10'], 'tab:blue' if 'gibberish' in k else 'tab:green'))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    xs = np.arange(len(voce))
    ax.bar(xs - 0.18, [x[1] for x in voce], width=0.36, color=[x[3] for x in voce], label='entro 1–4 parole')
    ax.bar(xs + 0.18, [x[2] for x in voce], width=0.36, color=[x[3] for x in voce], alpha=0.4, hatch='//', label='a 7–10 parole')
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([x[0] for x in voce], rotation=20, ha='right', fontsize=9)
    ax.set_ylabel('ripetizioni in più rispetto alla catena di segni\n(quota di parole identiche nella stessa riga)')
    ax.set_title('Ripetizione nella riga: nel Voynich subito e poi si spegne; altrove no')
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'memoria_corta.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
