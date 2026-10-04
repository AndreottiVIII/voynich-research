# -*- coding: utf-8 -*-
"""Esperimento e3b47: residui di spaziatura (spazio osservato − probabilità della regola) per riga, centrati per pagina;
legame fra righe a distanza 1..6 contro l'ordine delle righe rimescolato nella pagina.

Preregistrazione: preregistrazioni/e3b47.md. Scrive risultati/e3b47_deriva_spazi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
DIST = range(1, 7)
MIN_PUNTI = 3


def residui(quale):
    """{pagina: [residuo medio per riga, nell'ordine]} centrati per pagina."""
    pulite = e3a60.righe(quale)
    pos = []
    for segni, sep in pulite.values():
        pos += [(segni[i - 1], segni[i], sep.get(i, '') == '.') for i in range(1, len(segni)) if sep.get(i, '') in ('.', '')]
    reg = e3a58.Regola(pos)
    per = OrderedDict()
    for r in trascrizione.leggi(quale):
        if r.tipo[0] != trascrizione.PARAGRAFO or (r.pagina, r.numero) not in pulite:
            continue
        segni, sep = pulite[(r.pagina, r.numero)]
        xs = []
        for i in range(1, len(segni)):
            t = sep.get(i, '')
            if t not in ('.', ''):
                continue
            p = reg.p(segni[i - 1], segni[i])
            if 0.2 <= p <= 0.8:
                xs.append((t == '.') - p)
        if len(xs) >= MIN_PUNTI:
            per.setdefault(r.pagina, []).append(sum(xs) / len(xs))
    out = OrderedDict()
    for pg, v in per.items():
        if len(v) >= 4:
            m = sum(v) / len(v)
            out[pg] = [x - m for x in v]
    return out


def legami(pagine):
    acc = defaultdict(lambda: [0.0, 0])
    for v in pagine:
        for d in DIST:
            for i in range(len(v) - d):
                acc[d][0] += v[i] * v[i + d]
                acc[d][1] += 1
    return {d: acc[d][0] / acc[d][1] for d in DIST if acc[d][1]}


def gruppi(s):
    return sum(s[d] for d in (1, 2, 3)) / 3, sum(s[d] for d in (4, 5, 6)) / 3


def prova(per, rnd):
    pagine = list(per.values())
    oss = legami(pagine)
    nv, nl, nd = [], [], defaultdict(list)
    for _ in range(PERM):
        s = legami([rnd.sample(v, len(v)) for v in pagine])
        a, b = gruppi(s)
        nv.append(a)
        nl.append(b)
        for d in DIST:
            nd[d].append(s[d])
    v, l = gruppi(oss)
    z = lambda x, n: (x - statistics.mean(n)) / statistics.pstdev(n)
    return OrderedDict([('pagine', len(pagine)), ('righe', sum(len(x) for x in pagine)),
                        ('S', OrderedDict((d, oss[d]) for d in DIST)), ('S_nullo', OrderedDict((d, statistics.mean(nd[d])) for d in DIST)),
                        ('z_d', OrderedDict((d, z(oss[d], nd[d])) for d in DIST)), ('z_vicine', z(v, nv)), ('z_lontane', z(l, nl))])


def main():
    rnd = random.Random(3247)
    ris = OrderedDict()
    for quale in ('ZL', 'IT'):
        ris[quale] = prova(residui(quale), rnd)
        print(quale, json.dumps(ris[quale], ensure_ascii=False), flush=True)
    zz = [ris[q]['z_vicine'] for q in ris]
    esito = 'la spaziatura deriva lungo la pagina' if all(z > 2 for z in zz) else ('nessuna deriva' if all(abs(z) < 2 for z in zz) else 'incerto')
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b47_deriva_spazi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b47 — La propensione allo spazio cambia lentamente lungo la pagina?', '', 'Preregistrazione: `preregistrazioni/e3b47.md`. z rispetto all\'ordine delle righe rimescolato nella pagina.', '',
          '| trascrizione | pagine | righe | ' + ' | '.join('z(d=%d)' % d for d in DIST) + ' | z vicine (1–3) | z lontane (4–6) |', '|---|---|---|' + '---|' * len(DIST) + '---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %d | ' % (q, x['pagine'], x['righe']) + ' | '.join('%+.1f' % x['z_d'][d] for d in DIST) + ' | %+.1f | %+.1f |' % (x['z_vicine'], x['z_lontane']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b47_deriva_spazi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
