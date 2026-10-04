# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): profili per distanza nella riga della memoria corta, scelte di grafia in lingua
A e B (e3b14) e ripetizione di parole (e3a87, stessa riga e a cavallo dell'a capo). Scrive
risultati/figure/memoria_profili.png.
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
    s = carica('e3b14_memoria_profilo.json')
    p = carica('e3a87_ripresa_distanza.json')['profilo']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
    for lg, col in (('lingua A', 'tab:orange'), ('lingua B', 'tab:purple')):
        dd = [int(d) for d in s[lg]['profilo'] if s[lg]['profilo'][d]['coppie'] >= 300]
        a1.plot(dd, [s[lg]['profilo'][str(d)]['eccesso'] for d in dd], marker='o', color=col, label=lg)
    a1.axhline(0, color='0.4', lw=0.8)
    a1.set_xlabel('distanza nella riga (parole)')
    a1.set_ylabel('accordo in più rispetto alla pagina')
    a1.set_title('A. Scelte di grafia (-ey/-dy, sh/ch, ee/e); punti con almeno 300 coppie')
    a1.legend(frameon=False, fontsize=9)
    dd = [d for d in range(1, 21)]
    for tipo, col, lab in (('stessa riga', 'crimson', 'nella stessa riga'), ('a cavallo', 'tab:blue', "a cavallo dell'a capo (riga sopra)")):
        xs = [d for d in dd if tipo in p[str(d)] and p[str(d)][tipo]['coppie'] >= 500 and p[str(d)][tipo]['eccesso'] is not None]
        a2.plot(xs, [p[str(d)][tipo]['eccesso'] for d in xs], marker='o', color=col, label=lab)
    a2.axhline(0, color='0.4', lw=0.8)
    a2.set_xlabel('distanza (parole scritte in mezzo)')
    a2.set_ylabel('parole identiche in più rispetto alla catena')
    a2.set_title('B. Ripetizione di parole')
    a2.legend(frameon=False, fontsize=9)
    fig.suptitle('Memoria corta: nella riga si spegne in poche parole; dalla riga sopra è piatta', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(R, 'figure', 'memoria_profili.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
