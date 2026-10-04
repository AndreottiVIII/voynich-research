# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): accordo delle scelte fra parole accanto e forma del calo (R) con la misura alla
pari dell'e3c28 (righe senza bordi, coppie dentro la riga, atteso dalla stessa parola; lingue in righe finte della
lunghezza del Voynich) per Voynich, lingue (e3c28) e generatori (e3c29). Scrive risultati/figure/forma_alla_pari.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')
CORTI = {'Conlangs - ': '', 'Historical - ': '', 'Modern - ': '', ' - Literary': '', ' - Technical': '', ' - NT': ' NT', ' (classe generica)': ''}


def corto(k):
    for a, b in CORTI.items():
        k = k.replace(a, b)
    return k[:34]


def main():
    lin = json.load(open(os.path.join(R, 'e3c28_forma_alla_pari.json'), encoding='utf-8'))['testi']
    gen = json.load(open(os.path.join(R, 'e3c29_generatori_alla_pari.json'), encoding='utf-8'))['generatori']
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for k, x in list(lin.items()) + list(gen.items()):
        if x['R'] is None or x['accanto_IC95'][0] is None:
            continue
        if k.startswith('Voynich'):
            col, mk, ms = 'crimson', 'o', 10
        elif k in gen:
            col, mk, ms = 'tab:green', 's', 7
        else:
            col, mk, ms = ('goldenrod' if x.get('conta') else '#ccc'), 'o', 6
        r = max(min(x['R'], 1.4), -0.4)
        ax.plot(x['accanto'], r, mk, color=col, ms=ms)
        if k.startswith('Voynich') or (k not in gen and x.get('conta') and (x['R'] > 0.3 or x['accanto'] > 0.25)):
            ax.annotate(corto(k), (x['accanto'], r), fontsize=7, xytext=(4, 3), textcoords='offset points')
        if k.startswith('Voynich'):
            ax.plot([x['accanto']] * 2, [max(x['R_IC95'][0], -0.4), min(x['R_IC95'][1], 1.4)], color=col, lw=1)
    ax.axhline(0.61, color='crimson', lw=0.6, ls=':')
    ax.set_xlabel('accordo delle scelte fra parole accanto (oltre le coppie a 8–12 parole)')
    ax.set_ylabel('R: quanto ne resta a 3 parole (1 = tutto, 0 = niente; tagliato a −0,4 e 1,4)')
    ax.set_title('Misura alla pari: rosso Voynich, oro lingue con accordo chiaro, grigio lingue senza,\nverde generatori. '
                 'Solo il Voynich ha un accordo che dura (R alto) con forza chiara', fontsize=9)
    fig.tight_layout()
    out = os.path.join(R, 'figure', 'forma_alla_pari.png')
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == '__main__':
    main()
