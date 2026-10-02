# -*- coding: utf-8 -*-
"""Esperimento 173b: come l'e173, ma correlazione dentro classi di lunghezza della riga e nullo che rimescola
dentro le classi (e, secondario, dentro pagina x classe).

Preregistrazione: preregistrazioni/e173b.md. Scrive risultati/e173b_dimensione_per_lunghezza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e146_deriva_preferenze as e146
import e173_dimensione_scrittura as e173

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 1732, 2000
CLASSI = ((0, 7), (7, 9), (9, 11), (11, 10 ** 6))


def classe(n):
    for i, (lo, hi) in enumerate(CLASSI):
        if lo <= n < hi:
            return i


def statistica(cc, dd):
    per = defaultdict(list)
    for c, d in zip(cc, dd):
        per[c['classe']].append((d, c['scelta']))
    num = den = 0.0
    for v in per.values():
        if len(v) >= 10:
            num += len(v) * e173.spearman([a for a, _ in v], [b for _, b in v])
            den += len(v)
    return num / den if den else 0.0


def nullo(cc, chiave, rnd):
    gruppi = defaultdict(list)
    for i, c in enumerate(cc):
        gruppi[chiave(c)].append(i)
    out = []
    for _ in range(RIMESCOLAMENTI):
        dd = [c['dim'] for c in cc]
        for idx in gruppi.values():
            v = [dd[i] for i in idx]
            rnd.shuffle(v)
            for i, x in zip(idx, v):
                dd[i] = x
        out.append(statistica(cc, dd))
    return out


def main():
    rnd = random.Random(SEME)
    righe, P = e173.dimensioni()
    res = e146.residui(righe)
    cc = []
    for pag, v in P.items():
        for (k1, s1), (k2, s2) in zip(v, v[1:]):
            if k2 != k1 + 1 or righe[k1][1] != righe[k2][1]:
                continue
            dif = [abs(res[(f, k2)] - res[(f, k1)]) for f in e146.SCELTE if (f, k1) in res and (f, k2) in res]
            if dif:
                cc.append({'pagina': pag, 'dim': abs(s2 - s1), 'scelta': statistics.mean(dif), 'classe': classe(min(len(righe[k1][2]), len(righe[k2][2])))})
    vero = statistica(cc, [c['dim'] for c in cc])
    n1 = nullo(cc, lambda c: c['classe'], rnd)
    n2 = nullo(cc, lambda c: (c['pagina'], c['classe']), rnd)
    p1 = (1 + sum(x >= vero for x in n1)) / (1 + RIMESCOLAMENTI)
    p2 = (1 + sum(x >= vero for x in n2)) / (1 + RIMESCOLAMENTI)
    esito = 'le scelte seguono la dimensione' if vero > 0 and p1 < 0.01 else ('nessun legame' if p1 > 0.05 else 'incerto')
    per_classe = OrderedDict()
    for i, (lo, hi) in enumerate(CLASSI):
        v = [c for c in cc if c['classe'] == i]
        per_classe['%d-%s' % (lo, hi - 1 if hi < 10 ** 6 else '')] = OrderedDict([('coppie', len(v)), ('spearman', e173.spearman([c['dim'] for c in v], [c['scelta'] for c in v]))])
    ris = OrderedDict([('coppie', len(cc)), ('statistica', vero), ('p_classi', p1), ('nullo_classi_media', statistics.mean(n1)),
                       ('p_pagina_per_classe', p2), ('nullo_pagina_per_classe_media', statistics.mean(n2)), ('per_classe', per_classe), ('esito', esito)])
    print('coppie %d | statistica %.3f | p classi %.4f (nullo %.3f) | p pagina×classe %.4f (nullo %.3f) | %s | %s' % (
        len(cc), vero, p1, statistics.mean(n1), p2, statistics.mean(n2), esito, {k: round(x['spearman'], 3) for k, x in per_classe.items()}), flush=True)
    with open(os.path.join(RISULTATI, 'e173b_dimensione_per_lunghezza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e173b — Dimensione della scrittura e scelte di grafia, a parità di lunghezza della riga', '',
           'Spearman fra |Δ dimensione| e cambio di scelta, dentro classi di lunghezza della riga più corta. Preregistrazione: `preregistrazioni/e173b.md`.', '',
           '| classe (parole) | coppie | Spearman |', '|---|---|---|'] + ['| %s | %d | %.3f |' % (k, x['coppie'], x['spearman']) for k, x in per_classe.items()] + [
           '', 'Statistica pesata %.3f; p (nullo dentro le classi) %.4f; p (dentro pagina × classe) %.4f.' % (vero, p1, p2), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e173b_dimensione_per_lunghezza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
