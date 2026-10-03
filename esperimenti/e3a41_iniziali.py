# -*- coding: utf-8 -*-
"""Esperimento e3a41: alternanze di iniziale (a parita' di corpo della parola) legate alla classe dell'ultimo segno della
parola prima; per coppia di iniziali, informazione mutua condizionata al corpo e nullo dentro il corpo.

Preregistrazione: preregistrazioni/e3a41.md. Scrive risultati/e3a41_iniziali.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from statistics import NormalDist

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 2000


def classe(s):
    return 'V' if s in V else ('C' if s in C else ('L' if s == 'l' else 'X'))


def main():
    rnd = random.Random(3141)
    ev = []    # (corpo, iniziale, classe prima)
    for st, pag, npar, ws, seps in e386.righe():
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if a and b and seps[j] == '.' and len(b) >= 2:
                ev.append((b[1:], b[0], classe(a[-1])))
    per_corpo = defaultdict(list)
    for c, x, k in ev:
        per_corpo[c].append((x, k))
    conta = Counter()
    for c, xs in per_corpo.items():
        ini = Counter(x for x, _ in xs)
        for x in ini:
            for y in ini:
                if x < y:
                    conta[(x, y)] += min(ini[x], ini[y])
    coppie = [p for p, n in conta.items() if n >= 10]
    soglia = NormalDist().inv_cdf(1 - 0.01 / max(1, len(coppie)))
    ris = OrderedDict()
    for x, y in sorted(coppie, key=lambda p: -conta[p]):
        gruppi = []
        for c, xs in per_corpo.items():
            g = [(s, k) for s, k in xs if s in (x, y)]
            if len({s for s, _ in g}) == 2:
                gruppi.append(g)
        ev2 = [((i,), s, k) for i, g in enumerate(gruppi) for s, k in g]
        p = e380.prova(ev2, rnd, PERM)
        tab = defaultdict(Counter)
        for g in gruppi:
            for s, k in g:
                tab[k][s] += 1
        dirz = OrderedDict((k, round(tab[k][x] / (tab[k][x] + tab[k][y]), 2)) for k in ('V', 'C', 'L', 'X') if tab[k][x] + tab[k][y] >= 10)
        ris['%s/%s' % (x, y)] = OrderedDict([('corpi', len(gruppi)), ('eventi', p['eventi']), ('E', p['E']), ('z', p['z']), ('quota_di_%s_per_classe' % x, dirz),
                                            ('legata', p['z'] > soglia)])
        print(x, y, json.dumps(ris['%s/%s' % (x, y)], ensure_ascii=False), flush=True)
    legate = [k for k, v in ris.items() if v['legata']]
    esito = 'più alternanze: ' + ', '.join(legate) if legate else 'solo qo-/o-'
    out = OrderedDict([('coppie_provate', len(coppie)), ('soglia_z', soglia), ('alternanze', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a41_iniziali.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a41 — Quali iniziali di parola cambiano secondo la parola prima?', '', 'Preregistrazione: `preregistrazioni/e3a41.md`. Coppie di iniziali provate: %d; soglia z %.2f (Bonferroni).' % (len(coppie), soglia), '',
          '| alternanza x/y | corpi | eventi | E | z | quota di x dopo V / C / L / altro | legata |', '|---|---|---|---|---|---|---|']
    for k, v in ris.items():
        q = list(v.values())[4]
        md.append('| %s | %d | %d | %.4f | %.1f | %s | %s |' % (k, v['corpi'], v['eventi'], v['E'], v['z'], ', '.join('%s %.2f' % kv for kv in q.items()), 'sì' if v['legata'] else ''))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a41_iniziali.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
