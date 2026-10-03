# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): per ogni testo, quanto la giuntura ricalca le sequenze dentro le parole
(rho, e3a49/e3a52) e quanto passa l'a capo (Q, e384/e399). Scrive risultati/figure/catena_riga.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')


def carica(nome):
    return json.load(open(os.path.join(R, nome), encoding='utf-8'))


def main():
    capo = carica('e384_giuntura_a_capo.json')['testi']
    rho = carica('e3a49_dentro_fra.json')
    gen_rho = carica('e3a52_dentro_fra_generatori.json')
    gen_q = carica('e399_giuntura_generatori.json')['testi']
    xs, ys = [], []
    for k, x in rho['testi_sensati'].items():
        c = capo.get(k)
        if c and c['capo']['coppie'] >= 1000 and x['celle'] >= 30 and c['Q'] is not None:
            xs.append(x['rho'])
            ys.append(c['Q'])
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.scatter(xs, ys, s=22, c='0.65', label='lingue vere (testi con abbastanza dati)')
    v_rho = rho['Voynich']['mediana_10000']
    v_q = capo['Voynich']['Q']
    ax.scatter([v_rho], [v_q], s=160, marker='*', c='crimson', zorder=5, label='Voynich')
    g_rho = rho['gibberish umano']['rho']
    g_q = capo['gibberish umano']['Q']
    ax.scatter([g_rho], [g_q], s=60, marker='s', c='tab:blue', zorder=4, label='gibberish scritto a mano')
    for k, x in gen_rho.items():
        q = gen_q.get(k, {}).get('Q')
        if q is None or x['mediana_10000'] is None:
            continue
        nome = k.split(' (')[0]
        ax.scatter([x['mediana_10000']], [q], s=50, marker='^', c='tab:green', zorder=4)
        ax.annotate(nome, (x['mediana_10000'], q), textcoords='offset points', xytext=(5, 4), fontsize=8, color='tab:green')
    ax.annotate('Voynich', (v_rho, v_q), textcoords='offset points', xytext=(6, -12), fontsize=9, color='crimson')
    ax.axhline(0, color='0.85', lw=0.8)
    ax.set_xlabel('la giuntura fra parole ricalca le sequenze dentro le parole (ρ)\n← spazio come confine forte          spazio come confine debole →')
    ax.set_ylabel('la giuntura passa a capo (Q)\n← riga chiusa          riga aperta →')
    ax.set_title('Voynich, lingue, gibberish e generatori: catena e chiusura della riga')
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    ax.set_ylim(-0.8, 1.6)
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'catena_riga.png')
    fig.savefig(out, dpi=150)
    print(out, len(xs), 'lingue')


if __name__ == '__main__':
    main()
