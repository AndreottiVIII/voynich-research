# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): accordo delle scelte a 1, 2, 3 parole con la misura pulita (stessa parola +
pagina + deriva, righe senza bordi): Voynich per scelta (e3c35; GC h/k dall'e3c38), lingue (e3c34) e generatori (e3c37).
Scrive risultati/figure/finestra.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')


def carica(n):
    return json.load(open(os.path.join(R, n), encoding='utf-8'))


def main():
    per = carica('e3c35_finestra_per_scelta.json')
    gc = carica('e3c38_finestra_gc.json')['classi']
    lin = carica('e3c34_finestra_tre_parole.json')['testi']
    gen = carica('e3c37_generatori_misura_pulita.json')['generatori']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    d = [1, 2, 3]
    for k, x in lin.items():
        if k.startswith('Voynich') or not x.get('conta'):
            continue
        a1.plot(d, x['K'], '-', color='goldenrod', alpha=0.6, lw=1)
    a1.plot([], [], '-', color='goldenrod', label='lingue con accordo chiaro (classe generica o -o/-a, -us/-a)')
    for k, x in gen.items():
        y = x['k/t, sh/ch, -ey/-dy']['K']
        a1.plot(d, y, '--', color='tab:green', lw=1.2)
    a1.plot([], [], '--', color='tab:green', label='generatori (k/t, sh/ch, -ey/-dy)')
    stili = {'k/t': 'o-', 'sh/ch': 's-', '-ey/-dy': '^-'}
    for c, st in stili.items():
        a2.plot(d, per['ZL, %s' % c]['K'], st, color='crimson', label='Voynich ZL, %s' % c)
        a2.plot(d, per['IT, %s' % c]['K'], st, color='#e88', alpha=0.8)
    a2.plot(d, per['ZL, qo/o']['K'], 'D:', color='purple', label='Voynich ZL, qo/o (accanto decide il raccordo)')
    a2.plot(d, gc['h/k']['K'], 'o--', color='black', label='Glen Claston, gallows h/k')
    a2.plot(d, per['ZL, a/o (automatica)']['K'], 'x:', color='grey', label='Voynich ZL, a/o')
    for a in (a1, a2):
        a.axhline(0, color='grey', lw=0.8)
        a.set_xticks(d)
        a.set_xlabel('distanza in parole nella stessa riga')
        a.legend(fontsize=7)
    a1.set_ylabel('accordo delle scelte oltre l\'atteso (parola, pagina, deriva)')
    a1.set_title('Lingue e generatori: forte fra parole accanto, poi crolla\n(generatori: quasi niente)', fontsize=9)
    a2.set_title('Voynich: k/t, sh/ch, -ey/-dy restano alti fino a 3 parole\n(rosa: Takahashi; nero: terza trascrizione)', fontsize=9)
    fig.tight_layout()
    out = os.path.join(R, 'figure', 'finestra.png')
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == '__main__':
    main()
