# -*- coding: utf-8 -*-
"""Figure del white paper v2, tutte rifatte dai file dei risultati (nessuna misura nuova).

    .venv/Scripts/python white_paper/en/figure/genera_figure.py

Scrive in white_paper/en/figure/: lingue.pdf, scribi.pdf, valutazione.pdf, pagina_f1r.tex.
"""
import json, os, random, sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, '..', '..', '..'))
RIS = os.path.join(RADICE, 'risultati')
sys.path.insert(0, os.path.join(RADICE, 'analisi'))
plt.rcParams.update({'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8, 'font.family': 'DejaVu Sans'})
ROSSO = '#b2182b'
NOMI = {'ꝛ': 'r-rotunda', 'ꝩ': 'vend', 'uͦ': 'u-with-o'}


def etichetta(k):
    k = k.replace('ReF, ', 'German: ')
    for a, b in NOMI.items():
        k = k.replace(a, b)
    return k.replace('abbreviata o no', 'abbreviated or not').replace('senza accento', 'without accent')
GRIGIO = '#4d4d4d'


def carica(nome):
    return json.load(open(os.path.join(RIS, nome), encoding='utf-8'))


def lingue():
    st = carica('e3c84_confronti_per_lingua.json')['statistiche']
    pannelli = [('spazio', 'F1 of spaces from flanking glyphs'), ('riempimento', 'form filling'),
                ('attestazione', 'attested wrong cuts'), ('rispecchiamento', 'mirroring of within-word rules (rho)'),
                ('frequenza_forma', 'frequency follows form (rho)'), ('giuntura', 'junction (bits)')]
    fig, assi = plt.subplots(3, 2, figsize=(6.3, 4.6))
    rnd = random.Random(1)
    for ax, (k, titolo) in zip(assi.flat, pannelli):
        x = st[k]
        nat = list(x['lingua']['valori'].values())
        art = list(x['lingue_artificiali']['valori'].values())
        ax.scatter(nat, [0.6 + rnd.uniform(-0.18, 0.18) for _ in nat], s=12, color=GRIGIO, alpha=0.8, label='natural languages (24)')
        ax.scatter(art, [-0.2 + rnd.uniform(-0.18, 0.18) for _ in art], s=14, facecolors='none', edgecolors=GRIGIO, alpha=0.8,
                   label='constructed-language texts (15)')
        ax.axvline(x['voynich'], color=ROSSO, lw=1.6, label='Voynich')
        ax.set_yticks([])
        ax.set_ylim(-0.6, 1.0)
        ax.set_title(titolo, loc='left')
        for lato in ('top', 'right', 'left'):
            ax.spines[lato].set_visible(False)
    h, l = assi.flat[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(QUI, 'lingue.pdf'))
    plt.close(fig)


def scribi():
    p = carica('e3c90_potenza_scribi.json')
    b = carica('e3c86_intervalli_bifoglio.json')['misure']
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.3, 5.4), gridspec_kw={'width_ratios': [1, 1]})
    # stato a 2-3 parole
    voci = sorted(p['stato'].items(), key=lambda kv: kv[1]['K23'])
    for i, (k, x) in enumerate(voci):
        lo, hi = x['K23_IC95']
        a1.plot([lo, hi], [i, i], color=GRIGIO, lw=1)
        a1.plot(x['K23'], i, 'o', color=GRIGIO, ms=3)
    vk = b['stato breve K2-3']
    a1.axvspan(*vk['bifoglio']['IC95'], color=ROSSO, alpha=0.18, lw=0)
    a1.axvline(vk['valore'], color=ROSSO, lw=1.4)
    a1.axvline(0, color='black', lw=0.6)
    a1.set_yticks(range(len(voci)))
    a1.set_yticklabels([etichetta(k) for k, _ in voci], fontsize=5.6)
    a1.set_xlabel('short state: agreement at 2-3 words')
    a1.set_xlim(-0.2, 0.36)
    # deriva
    vd = sorted(p['deriva'].items(), key=lambda kv: kv[1]['per_10_segni'])
    for i, (k, x) in enumerate(vd):
        lo, hi = x['IC95_per_10_segni']
        a2.plot([lo, hi], [i, i], color=GRIGIO, lw=1)
        a2.plot(x['per_10_segni'], i, 'o', color=GRIGIO, ms=3)
    n = len(vd)
    for j, s in enumerate(('qo/o', 'k/t', 'sh/ch', '-ey/-dy')):
        x = b['deriva %s' % s]
        y = n + 1 + j
        a2.plot(x['bifoglio']['IC95'], [y, y], color=ROSSO, lw=1.4)
        a2.plot(x['valore'], y, 'o', color=ROSSO, ms=3.5)
    a2.axvline(0, color='black', lw=0.6)
    a2.set_yticks(list(range(n)) + [n + 1 + j for j in range(4)])
    a2.set_yticklabels([etichetta(k) for k, _ in vd] + ['Voynich ' + s for s in ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')], fontsize=5.6)
    a2.set_xlabel('drift along the line (per 10 glyphs)')
    for ax in (a1, a2):
        for lato in ('top', 'right'):
            ax.spines[lato].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(QUI, 'scribi.pdf'))
    plt.close(fig)


def valutazione(e419=None):
    v = [carica('e409b_messaggio_nel_sacco_v21f1_chiavi_1_12.json'), carica('e409b_messaggio_nel_sacco_v21f1_chiavi_13_24.json')]
    g1 = [a for x in v for a in x['sintesi']['a']['AUC_e231_per_chiave']]
    g2 = [a for x in v for a in x['sintesi']['a']['AUC_e266_per_chiave']]
    fig, ax = plt.subplots(figsize=(6.3, 2.2))
    rnd = random.Random(2)
    ax.scatter(g1, [1 + rnd.uniform(-0.12, 0.12) for _ in g1], s=14, color=GRIGIO, label='v21, 24 keys')
    ax.scatter(g2, [0 + rnd.uniform(-0.12, 0.12) for _ in g2], s=14, color=GRIGIO)
    for y, val, testo in ((1, 0.481, 'manuscript, lines shuffled'), (0, 0.595, 'manuscript, lines shuffled')):
        ax.plot([val], [y], marker='D', color=ROSSO, ms=5)
        ax.annotate(testo, (val, y), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=6, color=ROSSO)
    for y, val in ((1, 0.984), (0, 0.990)):
        ax.plot([val], [y], marker='s', color=ROSSO, ms=4)
        ax.annotate('words shuffled\nin the line', (val, y), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=6, color=ROSSO)
    ax.axvline(0.5, color='black', lw=0.6)
    ax.axvspan(0.6, 0.7, color='#dddddd', lw=0, zorder=0)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['judge 2 (228 features)', 'judge 1 (209 features)'])
    ax.set_ylim(-0.5, 1.7)
    ax.set_xlim(0.45, 1.02)
    ax.set_xlabel('AUC (0.5 = guessing; grey band: between "hard to tell apart" and "distinguishable")')
    for lato in ('top', 'right'):
        ax.spines[lato].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(QUI, 'valutazione.pdf'))
    plt.close(fig)


def pagina(n=12):
    import trascrizione
    vere = [' '.join(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.pagina == 'f1r'][:n]
    gen = []
    for l in open(os.path.join(QUI, 'libro_esempio_v21.txt'), encoding='utf-8'):
        l = l.strip()
        if l.startswith('#') or not l:
            continue
        loc, parole = l.lstrip('@').split('>', 1)
        if loc.startswith('<f1r.'):
            gen.append(parole.strip().replace('.', ' '))
    gen = gen[:n]
    righe = ['%% generato da genera_figure.py: prime %d righe di f1r (ZL) e del libro d\'esempio v21' % n,
             '\\begin{minipage}{\\linewidth}',
             '\\textbf{f1r, the manuscript} (first %d lines, ZL transliteration)\\par\\medskip' % n,
             '{\\voyfont\\large\\raggedright\\setlength{\\parskip}{2pt}', '\\par\n'.join(vere), '\\par}',
             '\\vspace{8mm}',
             '\\textbf{f1r, a book generated by version 21} (first %d lines)\\par\\medskip' % n,
             '{\\voyfont\\large\\raggedright\\setlength{\\parskip}{2pt}', '\\par\n'.join(gen), '\\par}',
             '\\end{minipage}']
    open(os.path.join(QUI, 'pagina_f1r.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    lingue()
    scribi()
    valutazione()
    pagina()
    print('ok')
