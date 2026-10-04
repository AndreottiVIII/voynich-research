# -*- coding: utf-8 -*-
"""Esperimento e3b95 (descrittivo): profilo dell'accordo normalizzato in funzione della distanza in parole (1-7, meno
8-12), Voynich contro lingue con accordo grammaticale. Scrive anche la figura risultati/figure/profilo_distanza.png.

Preregistrazione: preregistrazioni/e3b95.md. Scrive risultati/e3b95_profilo_distanza.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b93_swahili as e3b93

RISULTATI = os.path.join(QUI, '..', 'risultati')
VICINE = range(1, 8)
LONTANE = range(8, 13)


def profilo(unita, classi):
    acc = defaultdict(lambda: [0.0, 0.0, 0])
    for u in unita:
        for c, f in classi.items():
            tot = sum(1 for s in u for w in s if f(w))
            uno = sum(f(w)[0] for s in u for w in s if f(w))
            for s in u:
                xs = [f(w) for w in s]
                for i in range(len(s)):
                    if not xs[i]:
                        continue
                    for d in list(VICINE) + list(LONTANE):
                        j = i + d
                        if j >= len(s) or not xs[j]:
                            continue
                        a, b = xs[i], xs[j]
                        if a[1] == b[1] or e3a86.una_modifica(a[1], b[1]):
                            continue
                        t = tot - 2
                        if t < 5:
                            continue
                        p = (uno - a[0] - b[0]) / t
                        g = d if d in VICINE else 'lontane'
                        acc[g][0] += a[0] == b[0]
                        acc[g][1] += p * p + (1 - p) * (1 - p)
                        acc[g][2] += 1
    def k(g):
        o, a, n = acc[g]
        return (o - a) / (n - a) if n - a > 0 else None
    kl = k('lontane')
    return OrderedDict((d, (k(d) - kl) if k(d) is not None else None) for d in VICINE), {str(g): v[2] for g, v in acc.items()}


def main():
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, _ = e3b62.voynich(e341.pagine(), mano)
    testi = OrderedDict([('Voynich ZL', (uu, e3b62.CV))])
    tt = e381.testi()
    for nome in ('italiano NT (Diodati)', 'spagnolo NT', 'latino NT (Vulgata)'):
        chiave, tipo = e3b91.TESTI[nome]
        righe = [r for r in tt[chiave] if r]
        testi[nome] = ([[b] for b in e3b51.blocchi(righe)], OrderedDict([('x', e3b91.oa if tipo == 'romanzo' else e3b91.usa)]))
    righe = [r for r in tt[e3b93.CHIAVE] if r]
    testi['swahili NT (prefissi)'] = ([[b] for b in e3b51.blocchi(righe)], e3b93.classi(righe))
    ris = OrderedDict()
    for nome, (u, cl) in testi.items():
        pr, n = profilo(u, cl)
        ris[nome] = OrderedDict([('profilo', pr), ('coppie', n)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b95_profilo_distanza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b95 — Forma del calo con la distanza: Voynich contro accordo grammaticale (descrittivo)', '', 'Preregistrazione: `preregistrazioni/e3b95.md`. Valori: K(d) − K(8–12), normalizzati.', '',
          '| testo | ' + ' | '.join('d=%d' % d for d in VICINE) + ' |', '|---|' + '---|' * len(VICINE)]
    for nome, x in ris.items():
        md.append('| %s | ' % nome + ' | '.join('%+.3f' % v if v is not None else 'n.d.' for v in x['profilo'].values()) + ' |')
    open(os.path.join(RISULTATI, 'e3b95_profilo_distanza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    fig, ax = plt.subplots(figsize=(8, 4.5))
    stili = {'Voynich ZL': ('crimson', '-', 2.5)}
    for nome, x in ris.items():
        col, ls, lw = stili.get(nome, ('goldenrod' if 'swahili' not in nome else 'darkorange', '--', 1.5))
        ax.plot(list(x['profilo']), list(x['profilo'].values()), color=col, ls=ls, lw=lw, marker='o', label=nome)
    ax.axhline(0, color='0.3', lw=0.8)
    ax.set_xlabel('distanza in parole')
    ax.set_ylabel('accordo in più (normalizzato)\nrispetto alle parole a 8–12 di distanza')
    ax.set_title('Come cala con la distanza: "memoria" del Voynich e accordo grammaticale delle lingue', fontsize=10)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    os.makedirs(os.path.join(RISULTATI, 'figure'), exist_ok=True)
    fig.savefig(os.path.join(RISULTATI, 'figure', 'profilo_distanza.png'), dpi=150)


if __name__ == '__main__':
    main()
