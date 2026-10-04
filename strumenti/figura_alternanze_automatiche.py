# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): a sinistra la memoria nelle alternanze dentro la parola scelte da una regola
uguale per tutti (e3c01 testi grandi, e3c04 testi piccoli, e3c02 generatori), con intervalli al 95% per unità; a destra
il profilo con la distanza per i testi che hanno memoria (e3c03). Scrive risultati/figure/alternanze_automatiche.png.
"""
import json, os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')
CORTI = {'Conlangs - ': '', 'Historical - ': '', 'Modern - ': '', ' - Literary': '', ' - Technical': '', ' - NT': ' NT'}


def carica(nome):
    p = os.path.join(R, nome)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def corto(k):
    for a, b in CORTI.items():
        k = k.replace(a, b)
    return k[:38]


def main():
    c1, c2, c3, c4 = (carica(n) for n in ('e3c01_alternanze_interne.json', 'e3c02_alternanze_generatori.json', 'e3c03_tre_tratti.json',
                                           'e3c04_alternanze_testi_piccoli.json'))
    righe = []
    for k in ('Voynich IT', 'Voynich ZL'):
        righe.append((k.replace('IT', 'Takahashi') + '  (' + ', '.join(c1['testi'][k]['alternanze']) + ')', c1['testi'][k], 'crimson'))
    lingue = sorted(((k, x) for k, x in c1['testi'].items() if not k.startswith('Voynich')), key=lambda kx: kx[1]['effetto'])
    for k, x in reversed(lingue):
        righe.append((corto(k), x, 'goldenrod'))
    if c4:
        for k, x in sorted(c4['testi'].items(), key=lambda kx: -kx[1]['effetto']):
            alt = x['alternanze'][0]
            righe.append((corto(k) + ('  (' + alt + ')' if all(ord(ch) < 0x370 for ch in alt) else ''), x, '#c9a'))
    for k, x in c2['testi'].items():
        righe.append((corto(k), x, 'tab:green'))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 0.26 * len(righe) + 2), gridspec_kw={'width_ratios': [1.15, 1]})
    for i, (et, x, col) in enumerate(righe):
        y = len(righe) - i
        a1.plot(x['IC95'], [y, y], color=col, lw=2)
        a1.plot(x['effetto'], y, 'o', color=col, ms=5)
    a1.set_yticks(range(len(righe), 0, -1))
    a1.set_yticklabels([r[0] for r in righe], fontsize=7)
    a1.axvline(0, color='grey', lw=0.8)
    a1.set_xlim(-0.14, 0.14)  # il Charaka Samhita (230 coppie) ha un intervallo fuori scala, tagliato
    a1.set_xlabel('memoria nelle alternanze dentro la parola (effetto, IC 95%)')
    a1.set_title('Regola uguale per tutti: rosso Voynich, oro testi grandi,\nrosa testi piccoli (erbari, tecnici), verde generatori\n(intervalli tagliati a ±0,14)', fontsize=9)
    stili = {'Voynich IT': ('crimson', '-', 'Voynich Takahashi'), 'Voynich ZL': ('crimson', '--', 'Voynich ZL'),
             'Historical - Arabic - Literary - Quran': ('goldenrod', '-', 'Corano (persona del discorso)'),
             'Naibbe (Greshko 2025), a capo': ('tab:green', '-', 'Naibbe (cifrario)')}
    for k, x in c3['testi'].items():
        col, ls, et = stili.get(k, ('grey', ':', corto(k)))
        ds = sorted(int(d) for d in x['profilo'])
        a2.plot(ds, [x['profilo'][str(d)] for d in ds], ls, color=col, marker='o', label=et)
    a2.axhline(0, color='grey', lw=0.8)
    a2.set_xlabel('distanza in parole')
    a2.set_ylabel('accordo delle scelte oltre quello lontano, K(d) − K(8–12)')
    a2.set_title('Forma: il Voynich ha il massimo fra parole accanto e cala piano;\nCorano e Naibbe no', fontsize=9)
    a2.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(R, 'figure', 'alternanze_automatiche.png')
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == '__main__':
    main()
