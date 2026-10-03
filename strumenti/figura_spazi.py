# -*- coding: utf-8 -*-
"""Figura di sintesi sugli spazi (misure gia' preregistrate, e3a58 ed e3a60):
A) quanto lo spazio si indovina dai due segni vicini (F1, e3a58) nel Voynich, nelle lingue, nel gibberish e nei generatori;
B) distribuzione della probabilita' della regola di spaziatura negli spazi certi, negli spazi incerti e dove non c'e'
spazio (ZL, come la parte 2 dell'e3a58), con la quota di spazi messi da Takahashi (e3a60).
Scrive risultati/figure/spazi.png.
"""
import json, os, sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(QUI, '..', 'risultati')
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import e386_salto_disegno as e386
import e3a58_spazi_prevedibili as e3a58


def probabilita():
    posiz = []
    for _, _, _, ws, seps in e386.righe():
        blocchi, cur, curs = [], [], []
        for i, w in enumerate(ws):
            sep = seps[i - 1] if i else None
            if w is None or sep == '|':
                if cur:
                    blocchi.append((cur, curs))
                cur, curs = ([], []) if w is None else ([w], [])
                continue
            if cur:
                curs.append(sep)
            cur.append(w)
        if cur:
            blocchi.append((cur, curs))
        for bw, bs in blocchi:
            s, tipo = [], {}
            for j, w in enumerate(bw):
                if s:
                    tipo[len(s)] = bs[j - 1]
                s += list(w)
            posiz += [(s[i - 1], s[i], tipo.get(i, '')) for i in range(1, len(s))]
    reg = e3a58.Regola([(a, b, t == '.') for a, b, t in posiz if t != ','])
    return {t: [reg.p(a, b) for a, b, tt in posiz if tt == t] for t in ('.', ',', '')}


def main():
    f1 = json.load(open(os.path.join(R, 'e3a58_spazi_prevedibili.json'), encoding='utf-8'))['parte1']
    it = json.load(open(os.path.join(R, 'e3a60_spazi_due_trascrittori.json'), encoding='utf-8'))['spazi']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios': [1, 1.4]})
    rnd = np.random.default_rng(0)
    nomi_s = list(f1['testi_sensati'].keys())
    vals = list(f1['testi_sensati'].values())
    jit = rnd.uniform(-0.15, 0.15, len(vals))
    a1.scatter(jit, vals, s=18, c='0.6', label='lingue vere (71 testi)')
    a1.scatter([0], [f1['altri']['Voynich']['f1']], s=200, marker='*', c='crimson', zorder=5, label='Voynich')
    a1.scatter([0.45], [f1['altri']['gibberish umano']['f1']], s=60, marker='s', c='tab:blue', label='gibberish scritto a mano')
    gen = [(k.split(' (')[0].split(',')[0], x['f1']) for k, x in f1['altri'].items() if k not in ('Voynich', 'gibberish umano')]
    for i, (k, v) in enumerate(sorted(gen, key=lambda kv: -kv[1])):
        a1.scatter([0.8], [v], s=45, marker='^', c='tab:green', zorder=4, label='generatori' if i == 0 else None)
        a1.annotate(k, (0.8, v), textcoords='offset points', xytext=(8, (2, -5, 2, -9)[i % 4]), fontsize=7, color='tab:green')
    for k, x, v in zip(nomi_s, jit, vals):
        if 'Pinyin' in k:
            a1.annotate('pinyin (numero del tono a fine parola)', (x, v), textcoords='offset points', xytext=(-8, -4), fontsize=7, color='0.4', ha='right')
            break
    a1.set_xlim(-0.9, 1.4)
    a1.set_xticks([])
    a1.set_ylim(0, 1.02)
    a1.set_ylabel('F1: spazi indovinati dai due segni vicini')
    a1.set_title('A. Dove cade lo spazio si indovina dai segni vicini')
    a1.legend(loc='lower left', fontsize=8, frameon=False)
    pr = probabilita()
    bins = np.linspace(0, 1, 21)
    nomi = {'': 'nessuno spazio', '.': 'spazio certo', ',': 'spazio incerto (virgola della ZL)'}
    colori = {'': '0.7', '.': 'tab:blue', ',': 'darkorange'}
    chiavi = {'': 'ZL nessuno spazio', '.': 'ZL spazio (.)', ',': 'ZL spazio incerto (,)'}
    for t in ('', '.', ','):
        w = np.ones(len(pr[t])) / len(pr[t])
        q = it[chiavi[t]]['P(IT spazio)']
        a2.hist(pr[t], bins=bins, weights=w, histtype='step' if t != ',' else 'stepfilled', alpha=0.85 if t != ',' else 0.45, lw=2,
                color=colori[t], label='%s: media %.2f; Takahashi mette lo spazio %.0f%% delle volte' % (nomi[t], np.mean(pr[t]), 100 * q))
    a2.set_xlabel('probabilità di spazio secondo la regola dei due segni vicini')
    a2.set_ylabel('quota dei punti')
    a2.set_title('B. Gli spazi incerti cadono dove la regola è incerta')
    a2.legend(loc='upper center', fontsize=8, frameon=False)
    a2.set_ylim(0, 1.0)
    fig.tight_layout()
    os.makedirs(os.path.join(R, 'figure'), exist_ok=True)
    out = os.path.join(R, 'figure', 'spazi.png')
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == '__main__':
    main()
