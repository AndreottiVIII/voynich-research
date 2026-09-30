# -*- coding: utf-8 -*-
"""Stile comune dei grafici, in versione chiara e scura.

Un solo colore d'accento per la cosa di cui parla il grafico (quasi sempre il
Voynich) e il grigio per il contesto: il punto e' vedere dove cade il Voynich
rispetto alle lingue, non distinguere cento lingue fra loro.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TEMI = {
    'chiaro': {
        'sfondo': '#fcfcfb', 'inchiostro': '#0b0b0b', 'secondario': '#52514e',
        'muto': '#898781', 'griglia': '#e1e0d9', 'asse': '#c3c2b7',
        'accento': '#2a78d6', 'contesto': '#898781', 'secondo': '#eb6834',
    },
    'scuro': {
        'sfondo': '#1a1a19', 'inchiostro': '#ffffff', 'secondario': '#c3c2b7',
        'muto': '#898781', 'griglia': '#2c2c2a', 'asse': '#383835',
        'accento': '#3987e5', 'contesto': '#898781', 'secondo': '#d95926',
    },
}


def figura(tema, larghezza=7.2, altezza=4.8):
    t = TEMI[tema]
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 9.5,
        'axes.edgecolor': t['asse'], 'axes.labelcolor': t['secondario'],
        'xtick.color': t['muto'], 'ytick.color': t['muto'],
        'text.color': t['inchiostro'], 'axes.linewidth': 0.8,
    })
    fig, ax = plt.subplots(figsize=(larghezza, altezza), dpi=150)
    fig.patch.set_facecolor(t['sfondo'])
    ax.set_facecolor(t['sfondo'])
    ax.grid(True, color=t['griglia'], linewidth=0.8, linestyle='-')
    ax.set_axisbelow(True)
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)
    ax.tick_params(length=0)
    return fig, ax, t


def titoli(fig, ax, t, titolo, sottotitolo):
    fig.text(0.02, 0.975, titolo, ha='left', va='top', fontsize=12,
             fontweight='bold', color=t['inchiostro'])
    fig.text(0.02, 0.915, sottotitolo, ha='left', va='top', fontsize=9,
             color=t['secondario'], linespacing=1.35)


def salva(fig, cartella, nome, tema):
    os.makedirs(cartella, exist_ok=True)
    percorso = os.path.join(cartella, '%s-%s.png' % (nome, tema))
    fig.savefig(percorso, facecolor=fig.get_facecolor())
    plt.close(fig)
    return percorso
