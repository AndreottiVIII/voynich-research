# -*- coding: utf-8 -*-
"""Esperimento e3a66: eterogeneita' fra le mani di Davis della quota di spazi nei punti facoltativi (regola dell'e3a58 fra
0,2 e 0,8), dentro gli strati della coppia di segni; nullo che rimescola le mani fra le pagine della stessa lingua.

Preregistrazione: preregistrazioni/e3a66.md. Scrive risultati/e3a66_spazi_mani.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
MIN_PUNTI = 300


def eterogeneita(punti, mano_di):
    """punti: [(strato, pagina, y)]; mano_di: {pagina: mano}."""
    per = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for st, pg, y in punti:
        c = per[st][mano_di[pg]]
        c[0] += y
        c[1] += 1
    tot = 0.0
    for st, mm in per.items():
        n = sum(c[1] for c in mm.values())
        q = sum(c[0] for c in mm.values()) / n
        if len(mm) < 2 or q in (0, 1):
            continue
        tot += sum(c[1] * (c[0] / c[1] - q) ** 2 for c in mm.values()) / (q * (1 - q))
    return tot


def main():
    rnd = random.Random(3166)
    info = {}
    for r in trascrizione.leggi('ZL'):
        info.setdefault(r.pagina, (r.mano, r.lingua))
    righe = e3a60.righe('ZL')
    pos = []
    for (pg, _), (segni, sep) in righe.items():
        pos += [(segni[i - 1], segni[i], sep.get(i, ''), pg) for i in range(1, len(segni)) if sep.get(i, '') != '|']
    reg = e3a58.Regola([(a, b, t == '.') for a, b, t, _ in pos if t != ','])
    fac = [((a, b), pg, int(t == '.')) for a, b, t, pg in pos if t != ',' and 0.2 <= reg.p(a, b) <= 0.8]
    conta = Counter(info[pg][0] for _, pg, _ in fac)
    mani = sorted(m for m, n in conta.items() if m and n >= MIN_PUNTI)
    fac = [x for x in fac if info[x[1]][0] in mani]
    pagine = sorted({pg for _, pg, _ in fac})
    mano_di = {pg: info[pg][0] for pg in pagine}
    oss = eterogeneita(fac, mano_di)
    per_lingua = defaultdict(list)
    for pg in pagine:
        per_lingua[info[pg][1]].append(pg)
    nul = []
    for _ in range(PERM):
        m2 = {}
        for lg, pp in per_lingua.items():
            mm = [mano_di[p] for p in pp]
            rnd.shuffle(mm)
            m2.update(zip(pp, mm))
        nul.append(eterogeneita(fac, m2))
    p = (1 + sum(1 for v in nul if v >= oss)) / (1 + PERM)
    esito = 'gli spazi facoltativi sono uguali per tutte le mani' if p >= 0.05 else ('ogni mano spazia a modo suo' if p < 0.01 else 'incerto')
    # descrittivo: scarto pesato di ogni mano dalla quota dello strato
    per = defaultdict(list)
    for st, pg, y in fac:
        per[st].append((mano_di[pg], y))
    desc = OrderedDict()
    for m in mani:
        num = den = 0.0
        npunti = 0
        for st, xs in per.items():
            q = sum(y for _, y in xs) / len(xs)
            ym = [y for mm, y in xs if mm == m]
            if ym:
                num += len(ym) * (sum(ym) / len(ym) - q)
                den += len(ym)
                npunti += len(ym)
        sv = [t for a, b, t, pg in pos if mano_di.get(pg) == m and t in ('.', ',')]
        desc[m] = OrderedDict([('lingue', sorted({info[pg][1] for pg in pagine if mano_di[pg] == m})), ('punti_facoltativi', npunti),
                               ('scarto_quota_spazi', num / den), ('quota_virgole', sv.count(',') / len(sv) if sv else None)])
    out = OrderedDict([('mani', mani), ('punti', len(fac)), ('pagine', len(pagine)), ('eterogeneita', oss), ('nullo_media', sum(nul) / len(nul)),
                       ('nullo_p95', sorted(nul)[int(0.95 * PERM)]), ('p', p), ('per_mano', desc), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a66_spazi_mani.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a66 — Gli spazi facoltativi si mettono allo stesso modo in tutte le mani?', '', 'Preregistrazione: `preregistrazioni/e3a66.md`.', '',
          'Punti facoltativi: %d in %d pagine; mani con almeno %d punti: %s.' % (len(fac), len(pagine), MIN_PUNTI, ', '.join(mani)), '',
          'Eterogeneità osservata %.1f; nullo (mani rimescolate fra pagine della stessa lingua) media %.1f, 95° percentile %.1f; p = %.4f.' % (oss, out['nullo_media'], out['nullo_p95'], p), '',
          '| mano | lingue | punti facoltativi | scarto della quota di spazi dalla media dello strato | quota di virgole |', '|---|---|---|---|---|']
    md += ['| %s | %s | %d | %+.3f | %s |' % (m, '/'.join(x['lingue']), x['punti_facoltativi'], x['scarto_quota_spazi'], '%.3f' % x['quota_virgole'] if x['quota_virgole'] is not None else 'n.d.') for m, x in desc.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a66_spazi_mani.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
