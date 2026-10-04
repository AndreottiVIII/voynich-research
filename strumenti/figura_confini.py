# -*- coding: utf-8 -*-
"""Figura di sintesi (nessun dato nuovo): che cosa passa i confini della scrittura (salto del disegno, a capo).
Memoria delle scelte (e3b66, e3b67), ripetizione di parole (e3b68), raccordo qo/o (e3b45). Scrive
risultati/figure/confini.png.
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


def pannello(ax, titolo, voci, ylab):
    xs = np.arange(len(voci))
    for i, (nome, v, ic, col) in enumerate(voci):
        ax.bar(i, v, color=col)
        if ic:
            ax.errorbar(i, v, yerr=[[v - ic[0]], [ic[1] - v]], color='0.2', capsize=3)
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([v[0] for v in voci], fontsize=8)
    ax.set_title(titolo, fontsize=10)
    ax.set_ylabel(ylab, fontsize=8)


def main():
    a = carica('e3b66_a_capo_potenza.json')['trascrizioni']
    s = carica('e3b67_salto_potenza.json')['trascrizioni']
    r = carica('e3b68_ripetizione_confini.json')['confini']
    q = carica('e3b45_raccordo_a_capo.json')['gruppi']
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
    pannello(axs[0], 'Memoria delle scelte (ZL)', [
        ('nella riga', a['ZL']['K']['dentro']['K'], None, 'crimson'),
        ('oltre il salto\ndel disegno', s['ZL']['D'], s['ZL']['IC95'], '#e88'),
        ("oltre l'a capo", a['ZL']['D'], a['ZL']['IC95'], '#e88')], 'accordo in più (normalizzato)')
    pannello(axs[1], 'Ripetizione di parole (ZL)', [
        ('nella riga', r["a capo, ZL"]['eccesso_dentro'], None, 'tab:blue'),
        ('oltre il salto\ndel disegno', r['salto, ZL']['D'], r['salto, ZL']['IC95'], '#8ac'),
        ("oltre l'a capo", r['a capo, ZL']['D'], r['a capo, ZL']['IC95'], '#8ac')], 'quota di parole ripetute in più')
    z = q['ZL, tutte le non T']
    pannello(axs[2], 'Raccordo qo/o (ZL)', [
        ('nella riga', z['stessa_riga_differenza'], None, 'tab:green'),
        ("oltre l'a capo", z['a_cavallo']['differenza'], z['a_cavallo']['IC95'], '#9c9')], 'P(qo | -y,-o,-d) − P(qo | -n,-r,-s,-m,-l)')
    fig.suptitle("All'a capo riparte la catena di segni (raccordo); memoria delle scelte e ripetizioni proseguono attenuate", fontsize=10)
    fig.text(0.5, 0.005, "Oltre i confini: rispetto agli abbinamenti con le righe vicine (barre: intervallo 95%). Nella riga: rispetto alla media della pagina (scelte) o agli stessi controlli (ripetizioni). Confronto indicativo.", ha='center', fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'confini.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
