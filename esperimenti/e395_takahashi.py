# -*- coding: utf-8 -*-
"""Esperimento 395: le prove principali sulla giuntura (e384, e386, e388, e389) con la trascrizione di Takahashi (IT).

Preregistrazione: preregistrazioni/e395.md. Scrive risultati/e395_takahashi.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e380_sandhi as e380
import e386_salto_disegno as e386
import e389_varianti_bordo as e389

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a'}


def righe(quale):
    out, npar = [], 0
    for r in trascrizione.leggi(quale):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        s = re.sub(r'<![^>]*>', '', r.grezza)
        s = s.replace('<%>', '').replace('<$>', '').replace('<->', '|').replace('<~>', '.')
        s = re.sub(r'<@[^>]*>', '', s)
        s = re.sub(r'<[^>]*>', '', s)
        s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
        s = s.replace('{', '').replace('}', '').replace("'", '')
        s = re.sub(r'@\d{3};', '*', s)
        ws, seps, prec = [], [], None
        for p in [p for p in re.split(r'([.,|]+)', s) if p]:
            if re.fullmatch(r'[.,|]+', p):
                prec = '|' if '|' in p else ('.' if '.' in p else ',')
                continue
            ws.append(tuple(D(p)) if trascrizione.pulita(p) else None)
            if len(ws) > 1:
                seps.append(prec or '.')
            prec = None
        if r.inizio_par:
            npar += 1
        if ws:
            out.append(('%s-%s' % (r.sezione or '?', r.lingua or '?'), r.pagina, npar, ws, seps))
    return out


def regola(ev, rnd):
    """ev: [(classe alta, scelta)]; differenza e p a una coda con le classi rimescolate."""
    def diff(e):
        a = [s for c, s in e if c]
        b = [s for c, s in e if not c]
        return sum(a) / len(a) - sum(b) / len(b)
    d = diff(ev)
    cl = [c for c, _ in ev]
    sc = [s for _, s in ev]
    nul = []
    for _ in range(10000):
        rnd.shuffle(cl)
        nul.append(diff(list(zip(cl, sc))))
    return OrderedDict([('eventi', len(ev)), ('differenza', d), ('p', sum(x >= d for x in nul) / len(nul))])


def main():
    rnd = random.Random(395)
    rr = righe('IT')
    tipi = {'|': [], '.': []}
    capo, qo, lr = [], [], []
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        sez = st.split('-')[0]
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] not in tipi:
                continue
            tipi[seps[j]].append((sez, a[-1], b[0]))
            if seps[j] == '.':
                q = e380.ini_qo(b)
                if q and (a[-1] in V or a[-1] in C):
                    qo.append((a[-1] in V, q[1] == 'qo'))
                f = e380.fin_lr(a)
                if f and (b[0] in K or b[0] in A):
                    lr.append((b[0] in K, f[1] == 'l'))
        if k + 1 < len(rr) and rr[k + 1][1] == pag and rr[k + 1][2] == npar and ws[-1] and rr[k + 1][3][0]:
            capo.append((sez, ws[-1][-1], rr[k + 1][3][0][0]))
    ris = OrderedDict()
    ris['1 giuntura nella riga'] = e386.prova(tipi['.'], rnd, 1000)
    ris['2 giuntura a capo'] = e386.prova(capo, rnd, 1000)
    ris['3 giuntura al salto del disegno'] = e386.prova(tipi['|'], rnd, 1000)
    n = len(tipi['|'])
    ris['3 riga a parità di coppie (E mediana)'] = statistics.median(e386.prova(rnd.sample(tipi['.'], n), rnd, 200)['E'] for _ in range(20))
    ris['4 regola di qo-'] = regola(qo, rnd)
    ris['5 regola di -l/-r'] = regola(lr, rnd)
    # 6: fine riga, come l'e389
    fine = []
    for st, pag, npar, ws, seps in rr:
        ww = [w for w in ws if w]
        n_ = len(ww)
        if n_ < 2:
            continue
        for j, w in enumerate(ww):
            if len(w) >= 2 and (0 < j < n_ - 1 or j == n_ - 1):
                fine.append(((st, w[:-1]), j == n_ - 1, w[-1]))
    f6 = e389.analizza(fine, np.random.RandomState(395))
    ris['6 fine riga'] = OrderedDict([('m', f6['segni'].get('m')), ('r', f6['segni'].get('r')), ('l', f6['segni'].get('l')), ('crescono', f6['crescono']), ('calano', f6['calano'])])
    rep = OrderedDict([
        ('1', ris['1 giuntura nella riga']['z'] > 3),
        ('2', ris['2 giuntura a capo']['z'] < 2),
        ('3', ris['3 giuntura al salto del disegno']['z'] < 2 and ris['3 giuntura al salto del disegno']['E'] < ris['3 riga a parità di coppie (E mediana)']),
        ('4', ris['4 regola di qo-']['differenza'] > 0 and ris['4 regola di qo-']['p'] < 0.01),
        ('5', ris['5 regola di -l/-r']['differenza'] > 0 and ris['5 regola di -l/-r']['p'] < 0.01),
        ('6', bool(f6['segni'].get('m') and f6['segni']['m']['z'] > 3 and f6['segni'].get('r') and f6['segni']['r']['z'] < -3)),
    ])
    esito = 'i risultati non dipendono dalla trascrizione' if all(rep.values()) else 'non replicate: %s' % ', '.join(k for k, v in rep.items() if not v)
    out = OrderedDict([('prove', ris), ('replicate', rep), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e395_takahashi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e395 — I risultati sulla giuntura reggono con la trascrizione di Takahashi?', '', 'Preregistrazione: `preregistrazioni/e395.md`.', '',
          '| prova | risultato con IT | replicata |', '|---|---|---|']
    g = ris
    md.append('| 1 giuntura nella riga | E %.4f, z %.1f (%d coppie) | %s |' % (g['1 giuntura nella riga']['E'], g['1 giuntura nella riga']['z'], g['1 giuntura nella riga']['coppie'], 'sì' if rep['1'] else 'no'))
    md.append('| 2 giuntura a capo | E %.4f, z %.1f (%d coppie) | %s |' % (g['2 giuntura a capo']['E'], g['2 giuntura a capo']['z'], g['2 giuntura a capo']['coppie'], 'sì' if rep['2'] else 'no'))
    md.append('| 3 giuntura al salto del disegno | E %.4f, z %.1f (%d coppie); riga a parità %.4f | %s |' % (g['3 giuntura al salto del disegno']['E'], g['3 giuntura al salto del disegno']['z'], g['3 giuntura al salto del disegno']['coppie'], g['3 riga a parità di coppie (E mediana)'], 'sì' if rep['3'] else 'no'))
    for k_, nome in (('4', '4 regola di qo-'), ('5', '5 regola di -l/-r')):
        md.append('| %s | differenza %+.3f, p %.4f (%d eventi) | %s |' % (nome, g[nome]['differenza'], g[nome]['p'], g[nome]['eventi'], 'sì' if rep[k_] else 'no'))
    m6, r6 = g['6 fine riga']['m'], g['6 fine riga']['r']
    md.append('| 6 fine riga | -m Δ %+.3f z %.1f; -r Δ %+.3f z %.1f | %s |' % (m6['delta'] if m6 else 0, m6['z'] if m6 else 0, r6['delta'] if r6 else 0, r6['z'] if r6 else 0, 'sì' if rep['6'] else 'no'))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e395_takahashi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
