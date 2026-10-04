# -*- coding: utf-8 -*-
"""Esperimento e3c23: la semplificazione accanto al disegno (e3c21, e3c22) riguarda solo qo/o (l'unica scelta che cambia
la larghezza della parola: un segno in più) o anche k/t, sh/ch, -ey/-dy? Regressione dentro strati (classe, parola
coperta) su x, F, L e A (= parola che tocca un disegno, prima o dopo), separata per qo/o e per le altre tre classi
insieme. ZL. Più la figura del profilo della scelta lungo la riga (A e B), descrittiva.

Preregistrazione: preregistrazioni/e3c23.md. Scrive risultati/e3c23_spazio_stretto.json e .md e
risultati/figure/deriva_riga.png.
"""
import json, os, sys
from collections import OrderedDict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e386_salto_disegno as e386
import e3b62_memoria_nullo_largo as e3b62
import e3c22_bordi_e_disegno as e3c22

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
FASCE = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 35), (36, 40), (41, 50)]


def osservazioni(righe, classi):
    out = []
    for _, pag, _, ws, seps in righe:
        if any(w is None for w in ws) or len(ws) < 3:
            continue
        prima = 0
        for i, w in enumerate(ws):
            vicino = (i > 0 and seps[i - 1] == '|') or (i < len(ws) - 1 and seps[i] == '|')
            v = [float(prima), float(i == 0), float(i == len(ws) - 1), float(vicino)]
            for k, f in classi.items():
                x = f(w)
                if x is not None:
                    out.append((pag, (k, x[1]), v, float(x[0])))
            prima += len(w)
    return out


def misura(righe, classi, rng):
    obs = osservazioni(righe, classi)
    k = 4
    n, sz, szz = e3c22.statistiche(obs, k)
    oss = e3c22.coefficienti(n.sum(0), sz.sum(0), szz.sum(0), k)
    boot = np.array([e3c22.coefficienti(*(a[idx].sum(0) for a in (n, sz, szz)), k) for idx in (rng.integers(0, n.shape[0], n.shape[0]) for _ in range(BOOT))])
    nomi = ('x', 'F', 'L', 'accanto al disegno')
    return OrderedDict((nm, OrderedDict([('coefficiente', float(oss[i]) * (10 if nm == 'x' else 1)),
                                         ('IC95', [float(np.percentile(boot[:, i], q)) * (10 if nm == 'x' else 1) for q in (2.5, 97.5)])])) for i, nm in enumerate(nomi))


def profilo(righe, lingua_di):
    """Quota della scelta marcata, scarto dalla media della propria parola coperta, per fascia di segni prima (parole
    interne), separata per lingua A e B; più gli scarti di prima parola, ultima e parole accanto al disegno."""
    obs = osservazioni(righe, e3b62.CV)
    medie = {}
    for o in obs:
        medie.setdefault(o[1], []).append(o[3])
    medie = {k: np.mean(v) for k, v in medie.items()}
    out = {}
    for lg in ('A', 'B'):
        oo = [o for o in obs if lingua_di.get(o[0]) == lg]
        scarti = lambda sel: [o[3] - medie[o[1]] for o in oo if sel(o)]
        fasce = []
        for a, b in FASCE:
            s = scarti(lambda o: o[2][1] == 0 and o[2][2] == 0 and o[2][3] == 0 and a <= o[2][0] <= b)
            fasce.append((float(np.mean(s)) if s else None, len(s)))
        out[lg] = OrderedDict([('fasce', fasce), ('prima', float(np.mean(scarti(lambda o: o[2][1] == 1)))),
                               ('ultima', float(np.mean(scarti(lambda o: o[2][2] == 1)))), ('accanto al disegno', float(np.mean(scarti(lambda o: o[2][3] == 1))))])
    return out


def figura(prof, ris):
    fig, ax = plt.subplots(figsize=(9, 5))
    centri = [(a + b) / 2 for a, b in FASCE]
    for lg, col in (('A', 'tab:blue'), ('B', 'crimson')):
        p = prof[lg]
        ax.plot(centri, [v for v, _ in p['fasce']], 'o-', color=col, label='lingua %s, parole interne' % lg)
        ax.plot([0], [p['prima']], 's', color=col, ms=9, mfc='white', label='%s: prima parola della riga' % lg)
        ax.plot([centri[-1] + 6], [p['ultima']], 'D', color=col, ms=8, mfc='white', label='%s: ultima parola della riga' % lg)
        ax.plot([centri[-1] + 10], [p['accanto al disegno']], '^', color=col, ms=9, label='%s: accanto a un disegno' % lg)
    ax.axhline(0, color='grey', lw=0.8)
    ax.set_xlabel('segni scritti prima nella riga')
    ax.set_ylabel('quota di qo, k, sh, -ey rispetto alla media della stessa parola')
    ax.set_title('Le varianti marcate calano lungo la riga (soprattutto all\'inizio)\ne sono più rare contro il margine e contro i disegni', fontsize=10)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(RISULTATI, 'figure', 'deriva_riga.png'), dpi=130)


def main():
    rng = np.random.default_rng(3323)
    righe = e386.righe()
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        if r.lingua:
            lingua.setdefault(r.pagina, r.lingua)
    ris = OrderedDict()
    ris['qo/o'] = misura(righe, OrderedDict([('qo/o', e3b62.CV['qo/o'])]), rng)
    ris['k/t, sh/ch, -ey/-dy'] = misura(righe, OrderedDict((k, e3b62.CV[k]) for k in ('k/t', 'sh/ch', '-ey/-dy')), rng)
    for k in ('k/t', 'sh/ch', '-ey/-dy'):
        ris[k] = misura(righe, OrderedDict([(k, e3b62.CV[k])]), rng)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    q, alt = ris['qo/o']['accanto al disegno']['IC95'], ris['k/t, sh/ch, -ey/-dy']['accanto al disegno']['IC95']
    if alt[1] < 0:
        esito = 'la semplificazione accanto al disegno c\'è anche nelle scelte che non cambiano la larghezza'
    elif q[1] < 0 and alt[0] <= 0 <= alt[1]:
        esito = 'la semplificazione accanto al disegno sta in qo/o (larghezza)'
    else:
        esito = 'incerto'
    prof = profilo(righe, lingua)
    figura(prof, ris)
    out = OrderedDict([('regressioni', ris), ('profilo', prof), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c23_spazio_stretto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c23 — La semplificazione accanto al disegno: solo qo/o o tutte le scelte?', '', 'Preregistrazione: `preregistrazioni/e3c23.md`. ZL; regressione dentro strati (classe, parola coperta); x per 10 segni.', '',
          '| classi | x | F (prima della riga) | L (ultima) | accanto al disegno |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %s |' % (k, ' | '.join('%+.4f (%+.4f – %+.4f)' % (x[n]['coefficiente'], x[n]['IC95'][0], x[n]['IC95'][1]) for n in ('x', 'F', 'L', 'accanto al disegno'))))
    md += ['', 'Figura: `risultati/figure/deriva_riga.png` (descrittiva).', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c23_spazio_stretto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
