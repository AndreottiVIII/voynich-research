# -*- coding: utf-8 -*-
"""Esperimento e3b03: differenza lessicale dell'e3b01 dentro strati (4 segni attorno, lunghezza del pezzo sinistro e
destro); nulli dentro gli strati e dentro strati x pagina; descrittivo della quota di spazi per lunghezza dei pezzi.

Preregistrazione: preregistrazioni/e3b03.md. Scrive risultati/e3b03_lessicale_lunghezza.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a60_spazi_due_trascrittori as e3a60
import e3a99_spazio_lessicale as e3a99
import e3b01_taratura_lessicale as e3b01

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 100


def lunghezze(righe, punti):
    out = []
    for k, i, st, y in punti:
        s, sep = righe[k]
        cc = sorted(j for j, t in sep.items() if t in ('.', ',', '|') and j != i)
        a = max([c for c in cc if c < i], default=0)
        b = min([c for c in cc if c > i], default=len(s))
        out.append((min(i - a, 5), min(b - i, 5)))
    return out


def statistica(righe, punti, ys, strati_key):
    """Come e3b01.statistica ma con strati dati da strati_key[j]."""
    seps = [dict(sep) for _, sep in righe]
    for (k, i, _, _), y in zip(punti, ys):
        if y:
            seps[k][i] = '.'
        else:
            seps[k].pop(i, None)
    f = Counter()
    confini = []
    for (s, _), sep in zip(righe, seps):
        c = sorted(i for i, t in sep.items() if t in ('.', ',', '|'))
        confini.append(c)
        f.update(e3a99.parole_di(s, c))
    N, V = sum(f.values()), len(f)

    def lp(x, togli=0):
        return math.log((f[x] - togli + 0.5) / (N + 0.5 * V))
    per = defaultdict(lambda: ([], []))
    for j, ((k, i, _, _), y) in enumerate(zip(punti, ys)):
        s = righe[k][0]
        cc = confini[k]
        a = max([c for c in cc if c < i], default=0)
        b = min([c for c in cc if c > i], default=len(s))
        if y:
            lam = lp(tuple(s[a:i]), 1) + lp(tuple(s[i:b]), 1) - lp(tuple(s[a:b]))
        else:
            lam = lp(tuple(s[a:i])) + lp(tuple(s[i:b])) - lp(tuple(s[a:b]), 1)
        per[strati_key[j]][y].append(lam)
    num = den = 0.0
    for l0, l1 in per.values():
        if l0 and l1:
            w = len(l0) * len(l1) / (len(l0) + len(l1))
            num += w * (sum(l1) / len(l1) - sum(l0) / len(l0))
            den += w
    return num / den


def nullo(righe, punti, ys, strati_key, gruppi, rnd):
    idx = defaultdict(list)
    for j, g in enumerate(gruppi):
        idx[g].append(j)
    out = []
    for _ in range(PERM):
        y2 = list(ys)
        for jj in idx.values():
            vv = [ys[j] for j in jj]
            rnd.shuffle(vv)
            for j, v in zip(jj, vv):
                y2[j] = v
        out.append(statistica(righe, punti, y2, strati_key))
    return statistics.mean(out), statistics.pstdev(out)


def main():
    rnd = random.Random(3203)
    d = e3a60.righe('ZL')
    chiavi = list(d)
    righe = [d[k] for k in chiavi]
    punti = e3b01.punti_fissi(righe)
    ys = [p[3] for p in punti]
    lun = lunghezze(righe, punti)
    key = [(p[2],) + l for p, l in zip(punti, lun)]
    vero = statistica(righe, punti, ys, key)
    m1, s1 = nullo(righe, punti, ys, key, key, rnd)
    m2, s2 = nullo(righe, punti, ys, key, [k + (chiavi[p[0]][0],) for k, p in zip(key, punti)], rnd)
    z1, z2 = (vero - m1) / s1, (vero - m2) / s2
    esito = 'la preferenza contraria era la lunghezza: sparisce' if abs(z2) < 2 else ('resta anche a parità di lunghezza' if z2 <= -2 else 'a parità di lunghezza appare una preferenza lessicale')
    # descrittivo: scarto della quota di spazi per lunghezza, dentro lo strato dei 4 segni
    media_st = defaultdict(list)
    for p in punti:
        media_st[p[2]].append(p[3])
    ms = {k: sum(v) / len(v) for k, v in media_st.items()}
    desc = OrderedDict()
    for lato, pos in (('sinistra', 0), ('destra', 1)):
        acc = defaultdict(list)
        for p, l in zip(punti, lun):
            acc[l[pos]].append(p[3] - ms[p[2]])
        desc[lato] = OrderedDict((str(L), OrderedDict([('punti', len(acc[L])), ('scarto', sum(acc[L]) / len(acc[L]))])) for L in sorted(acc))
    out = OrderedDict([('punti', len(punti)), ('differenza_vera', vero), ('N1', OrderedDict([('media', m1), ('sd', s1), ('z', z1)])),
                       ('N2_pagina', OrderedDict([('media', m2), ('sd', s2), ('z', z2)])), ('per_lunghezza', desc), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b03_lessicale_lunghezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b03 — La "preferenza contraria" sparisce se si tiene ferma la lunghezza dei pezzi?', '', 'Preregistrazione: `preregistrazioni/e3b03.md`. Strati: 4 segni attorno × lunghezza del pezzo sinistro × destro (fino a 5+).', '',
          'Differenza vera **%+.3f**. Nullo dentro gli strati: %+.3f (sd %.3f), z %+.1f. Nullo dentro strati × pagina: %+.3f (sd %.3f), z **%+.1f**.' % (vero, m1, s1, z1, m2, s2, z2), '',
          '| lunghezza del pezzo | punti (sinistra) | scarto della quota di spazi (sinistra) | punti (destra) | scarto (destra) |', '|---|---|---|---|---|']
    for L in sorted(set(desc['sinistra']) | set(desc['destra'])):
        a, b = desc['sinistra'].get(L, {}), desc['destra'].get(L, {})
        md.append('| %s | %s | %s | %s | %s |' % ('5+' if L == '5' else L, a.get('punti', 0), '%+.3f' % a['scarto'] if a else '–', b.get('punti', 0), '%+.3f' % b['scarto'] if b else '–'))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b03_lessicale_lunghezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
