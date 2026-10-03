# -*- coding: utf-8 -*-
"""Esperimento e3a26: la scelta qo-/o- della prima parola della riga dipende da come comincia la riga a distanza L sopra
(L = 1, 2, 3), e dalla fine della riga subito sopra? Righe dalla seconda del paragrafo in poi.

Preregistrazione: preregistrazioni/e3a26.md. Scrive risultati/e3a26_margine_sinistro.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 10000


def prova(ev, rnd):
    """ev: [(paragrafo, condizione, qo)]; Delta e z con le condizioni rimescolate dentro il paragrafo."""
    def delta(e):
        a = [q for _, c, q in e if c]
        b = [q for _, c, q in e if not c]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else 0.0
    d = delta(ev)
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(ev):
        per[p].append(i)
    nul = []
    for _ in range(PERM):
        e2 = list(ev)
        for idx in per.values():
            cs = [ev[i][1] for i in idx]
            rnd.shuffle(cs)
            for i, c in zip(idx, cs):
                e2[i] = (ev[i][0], c, ev[i][2])
        nul.append(delta(e2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    na = sum(1 for _, c, _ in ev if c)
    return OrderedDict([('eventi', [na, len(ev) - na]), ('delta', d), ('z', (d - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3126)
    ris = OrderedDict()
    ev = {1: [], 2: [], 3: [], 'fine': []}
    k = 0
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            k += 1
            for i in range(1, len(rr)):
                if not rr[i]:
                    continue
                q = e380.ini_qo(rr[i][0])
                if not q:
                    continue
                for L in (1, 2, 3):
                    j = i - L
                    if j >= 1 and rr[j]:
                        ev[L].append((k, rr[j][0][:2] == ('q', 'o'), q[1] == 'qo'))
                if rr[i - 1] and (rr[i - 1][-1][-1] in V or rr[i - 1][-1][-1] in C):
                    ev['fine'].append((k, rr[i - 1][-1][-1] in V, q[1] == 'qo'))
    for L in (1, 2, 3):
        ris['inizio della riga a distanza %d' % L] = prova(ev[L], rnd)
    ris['fine della riga subito sopra (V contro C)'] = prova(ev['fine'], rnd)
    for k_, x in ris.items():
        print(k_, json.dumps(x), flush=True)
    d1, z1 = ris['inizio della riga a distanza 1']['delta'], ris['inizio della riga a distanza 1']['z']
    d2, z2 = ris['inizio della riga a distanza 2']['delta'], ris['inizio della riga a distanza 2']['z']
    if d1 < 0 and z1 < -3:
        esito = 'qo- a inizio riga evita il qo- subito sopra' + ('; alternanza' if d2 > 0 and z2 > 3 else '')
    elif abs(z1) < 2:
        esito = 'nessuna dipendenza dall\'inizio sopra'
    else:
        esito = 'incerto'
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a26_margine_sinistro.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a26 — qo- a inizio riga dipende dall\'inizio della riga sopra?', '', 'Preregistrazione: `preregistrazioni/e3a26.md`. Righe dalla seconda del paragrafo in poi.', '',
          '| condizione | eventi (sì / no) | Δ P(qo) | z |', '|---|---|---|---|']
    md += ['| %s | %d / %d | %+.3f | %.1f |' % (k_, x['eventi'][0], x['eventi'][1], x['delta'], x['z']) for k_, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a26_margine_sinistro.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
