# -*- coding: utf-8 -*-
"""Esperimento 187: differenze di forma fra etichette di tipi diversi (e183) a parita' di classe di lunghezza.

Preregistrazione: preregistrazioni/e187.md. Scrive risultati/e187_etichette_lunghezza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e183_etichette_oggetti as e183

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 187, 2000
D = e183.D


def classe(w):
    n = len(D(w))
    return '1-3' if n <= 3 else '4-5' if n <= 5 else '6-7' if n <= 7 else '8+'


def caratt(w):
    u = D(w)
    return (u[0], u[-1], u[0] == 'o')


def statistica(v):
    per = defaultdict(list)
    for _, t, w in v:
        per[classe(w)].append((t, w))
    n = len(v)
    tot = 0.0
    for c, x in per.items():
        if len(x) < 2:
            continue
        for j in range(3):
            tot += len(x) / n * e183.im([(caratt(w)[j], t) for t, w in x])
    return tot


def prova(v, rnd):
    vero = statistica(v)
    gruppi = defaultdict(list)
    for i, (p, _, w) in enumerate(v):
        gruppi[(p, classe(w))].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        tipi = [t for _, t, _ in v]
        for idx in gruppi.values():
            x = [tipi[i] for i in idx]
            rnd.shuffle(x)
            for i, y in zip(idx, x):
                tipi[i] = y
        nulli.append(statistica([(p, t, w) for (p, _, w), t in zip(v, tipi)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(v)), ('im_condizionata', vero), ('nullo', m), ('z', (vero - m) / s if s else None),
                        ('p', (1 + sum(x >= vero for x in nulli)) / (1 + RIMESCOLAMENTI))])


def main():
    rnd = random.Random(SEME)
    tutte = e183.etichette()
    ris = OrderedDict()
    for c, (sez, t1, t2) in e183.CONTRASTI.items():
        v = [(p, t, w) for p, s, t, w in tutte if s == sez and t in (t1, t2)]
        ris[c] = prova(v, rnd)
        print('%-12s n %d | IM condizionata %.3f (nullo %.3f) z %.1f p %.4f' % (c, ris[c]['n'], ris[c]['im_condizionata'], ris[c]['nullo'], ris[c]['z'] or 0, ris[c]['p']), flush=True)
    f = ris['farmacia']
    esito = 'differenza oltre la lunghezza' if (f['z'] or 0) > 3 and f['p'] < 0.01 else ('solo lunghezza' if f['p'] > 0.05 else 'incerto')
    ris['esito_farmacia'] = esito
    print('farmacia: %s' % esito)
    with open(os.path.join(RISULTATI, 'e187_etichette_lunghezza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e187 — Etichette di vasi e frammenti: differenze oltre la lunghezza', '',
           'IM (primo segno, ultimo segno, o-) con il tipo, condizionata alla classe di lunghezza; nullo dentro pagina × classe. Preregistrazione: `preregistrazioni/e187.md`.', '',
           '| contrasto | n | IM condizionata | nullo | z | p |', '|---|---|---|---|---|---|']
    for c in e183.CONTRASTI:
        r = ris[c]
        out.append('| %s | %d | %.3f | %.3f | %.1f | %.4f |' % (c, r['n'], r['im_condizionata'], r['nullo'], r['z'] or 0, r['p']))
    out += ['', 'Farmacia: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e187_etichette_lunghezza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
