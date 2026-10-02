# -*- coding: utf-8 -*-
"""Esperimento 203: etichette zodiacali adiacenti nel cerchio (ordinate per ora, dentro l'anello) sono piu' simili del
caso?

Preregistrazione: preregistrazioni/e203.md. Scrive risultati/e203_ninfe_in_sequenza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e144_ruote_zodiaco as e144

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, MINIMO = 203, 2000, 6
D = misure.divisore(misure.GLIFI_EVA)


def distanza_modifica(a, b):
    a, b = D(a), D(b)
    prec = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (x != y)))
        prec = cur
    return prec[-1]


_CACHE = {}


def somiglianza(a, b):
    k = (a, b)
    if k not in _CACHE:
        _CACHE[k] = 1 - distanza_modifica(a, b) / max(len(D(a)), len(D(b)))
    return _CACHE[k]


def adiacenti(anelli):
    tot, n = 0.0, 0
    for v in anelli:
        for i in range(len(v)):
            tot += somiglianza(v[i], v[(i + 1) % len(v)])
            n += 1
    return tot / n


def main():
    rnd = random.Random(SEME)
    per = defaultdict(list)
    for e in e144.etichette():
        per[(e['pagina'], e['anello'])].append((e['ora'], e['parole'][0]))
    anelli = [[w for _, w in sorted(v)] for v in per.values() if len(v) >= MINIMO]
    tutte = statistics.mean(somiglianza(v[i], v[j]) for v in anelli for i in range(len(v)) for j in range(i + 1, len(v)))
    vero = adiacenti(anelli) - tutte
    nulli = []
    for _ in range(PERMUTAZIONI):
        mes = []
        for v in anelli:
            v = v[:]
            rnd.shuffle(v)
            mes.append(v)
        nulli.append(adiacenti(mes) - tutte)
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    z = (vero - m) / s if s else None
    p = (1 + sum(n >= vero for n in nulli)) / (1 + PERMUTAZIONI)
    per_dist = defaultdict(list)
    for v in anelli:
        L = len(v)
        for i in range(L):
            for j in range(i + 1, L):
                d = min(j - i, L - (j - i))
                per_dist[min(d, 4)].append(somiglianza(v[i], v[j]))
    esito = 'sequenza ordinata' if (z or 0) > 3 and p < 0.01 else ('nessun ordine' if p > 0.05 else 'incerto')
    ris = OrderedDict([('anelli', len(anelli)), ('etichette', sum(map(len, anelli))), ('eccesso_adiacenti', vero), ('nullo', m), ('z', z), ('p', p),
                       ('per_distanza', {('%d' % k if k < 4 else '4+'): statistics.mean(v) for k, v in sorted(per_dist.items())}), ('esito', esito)])
    print('anelli %d, etichette %d | eccesso adiacenti %.4f (nullo %.4f) z %.1f p %.4f | per distanza %s | %s' % (
        len(anelli), ris['etichette'], vero, m, z or 0, p, {k: round(x, 3) for k, x in ris['per_distanza'].items()}, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e203_ninfe_in_sequenza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e203 — Le etichette delle ninfe contano?', '', 'Preregistrazione: `preregistrazioni/e203.md`.', '',
           '| anelli | etichette | eccesso di somiglianza fra adiacenti | nullo | z | p |', '|---|---|---|---|---|---|',
           '| %d | %d | %.4f | %.4f | %.1f | %.4f |' % (len(anelli), ris['etichette'], vero, m, z or 0, p), '',
           'Somiglianza per distanza nel cerchio: %s.' % ', '.join('%s: %.3f' % kv for kv in ris['per_distanza'].items()), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e203_ninfe_in_sequenza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
