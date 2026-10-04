# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): memoria delle scelte nella stessa riga e a cavallo dell'a capo, nelle pagine
"solo testo" e nelle altre (e3b38 ZL, e3b39 IT), per sezione (e3b41) e per la mano 2 (e3b42). Scrive
risultati/figure/solo_testo.png.
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
    voce = []
    for f, tr in (('e3b38_solo_testo_a_capo.json', 'ZL'), ('e3b39_solo_testo_it.json', 'Takahashi')):
        g = carica(f)['gruppi']
        voce.append(('solo testo\n(%s)' % tr, g['solo testo (T)'], 'crimson'))
        voce.append(('altre pagine\n(%s)' % tr, g['altre pagine'], '0.55'))
    m = carica('e3b42_a_capo_mano.json')
    voce.append(('mano 2,\nsolo testo', m['mano2_T'], 'crimson'))
    voce.append(('mano 2,\naltre pagine', m['mano2_altre'], '0.55'))
    s = carica('e3b41_a_capo_sezioni.json')['sezioni']
    for k, nome in (('S', 'ricette'), ('B', 'biologia'), ('H', 'erbario')):
        voce.append((nome, s[k], '0.55'))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    xs = np.arange(len(voce))
    st = [x[1]['stessa_riga'] for x in voce]
    ac = [x[1]['a_cavallo'] for x in voce]
    lo = [x[1]['a_cavallo'] - x[1]['IC95_a_cavallo'][0] for x in voce]
    hi = [x[1]['IC95_a_cavallo'][1] - x[1]['a_cavallo'] for x in voce]
    ax.bar(xs - 0.18, st, width=0.36, color=[x[2] for x in voce], alpha=0.45, label='nella stessa riga')
    ax.bar(xs + 0.18, ac, width=0.36, color=[x[2] for x in voce], yerr=[lo, hi], capsize=3, label="a cavallo dell'a capo (con intervallo 95%)")
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([x[0] for x in voce], fontsize=8)
    ax.set_ylabel('accordo delle scelte di grafia\nin più del caso (parole a 2–3 di distanza)')
    ax.set_title("Nelle 6 pagine di solo testo la memoria passa l'a capo; altrove si azzera")
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'solo_testo.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
