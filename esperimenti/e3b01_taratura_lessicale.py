# -*- coding: utf-8 -*-
"""Esperimento e3b01: taratura dell'e3a99 con un nullo in cui lo spazio nei punti facoltativi e' rimescolato dentro gli
strati dei 4 segni attorno (spazio deciso solo dai segni vicini); Voynich (ZL) e latino della Vulgata.

Preregistrazione: preregistrazioni/e3b01.md. Scrive risultati/e3b01_taratura_lessicale.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60
import e3a99_spazio_lessicale as e3a99

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 100


def punti_fissi(righe):
    reg = e3a58.Regola([(s[i - 1], s[i], sep.get(i, '') == '.') for s, sep in righe for i in range(1, len(s)) if sep.get(i, '') in ('.', '')])
    out = []
    for k, (s, sep) in enumerate(righe):
        for i in range(2, len(s) - 1):
            t = sep.get(i, '')
            if t in ('.', '') and 0.2 <= reg.p(s[i - 1], s[i]) <= 0.8:
                out.append((k, i, tuple(s[i - 2:i + 2]), int(t == '.')))
    return out


def statistica(righe, punti, ys):
    """righe con i separatori; ys: scelta (1 spazio) per ogni punto fisso."""
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
    for (k, i, st, _), y in zip(punti, ys):
        s = righe[k][0]
        cc = confini[k]
        a = max([c for c in cc if c < i], default=0)
        b = min([c for c in cc if c > i], default=len(s))
        if y:
            lam = lp(tuple(s[a:i]), 1) + lp(tuple(s[i:b]), 1) - lp(tuple(s[a:b]))
        else:
            lam = lp(tuple(s[a:i])) + lp(tuple(s[i:b])) - lp(tuple(s[a:b]), 1)
        per[st][y].append(lam)
    num = den = 0.0
    for l0, l1 in per.values():
        if l0 and l1:
            w = len(l0) * len(l1) / (len(l0) + len(l1))
            num += w * (sum(l1) / len(l1) - sum(l0) / len(l0))
            den += w
    return num / den


def taratura(righe, rnd):
    punti = punti_fissi(righe)
    ys = [p[3] for p in punti]
    vero = statistica(righe, punti, ys)
    strati = defaultdict(list)
    for j, p in enumerate(punti):
        strati[p[2]].append(j)
    nul = []
    for _ in range(PERM):
        y2 = list(ys)
        for idx in strati.values():
            vv = [ys[j] for j in idx]
            rnd.shuffle(vv)
            for j, v in zip(idx, vv):
                y2[j] = v
        nul.append(statistica(righe, punti, y2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('punti', len(punti)), ('differenza_vera', vero), ('nullo_media', m), ('nullo_sd', sd), ('z', (vero - m) / sd if sd else 0.0),
                        ('nullo_min', min(nul)), ('nullo_max', max(nul))])


def main():
    rnd = random.Random(3201)
    lat = taratura(e3a99.righe_testo(e381.testi()['Historical - Latin - Literary - NT (Vulgate).txt']), rnd)
    print('latino', json.dumps(lat), flush=True)
    voy = taratura(list(e3a60.righe('ZL').values()), rnd)
    print('Voynich', json.dumps(voy), flush=True)
    z = voy['z']
    esito = 'nessuna preferenza lessicale: lo spazio dipende solo dai segni vicini' if abs(z) < 2 else ('una preferenza lessicale debole' if z >= 2 else 'una preferenza contraria')
    out = OrderedDict([('latino', lat), ('Voynich', voy), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b01_taratura_lessicale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b01 — Taratura dell\'e3a99: quanto vale la differenza lessicale se lo spazio dipende solo dai segni vicini?', '', 'Preregistrazione: `preregistrazioni/e3b01.md`.', '',
          '| testo | punti | differenza vera | nullo: media (sd) | nullo: min – max | z |', '|---|---|---|---|---|---|']
    for k, x in (('latino, Vulgata', lat), ('Voynich (ZL)', voy)):
        md.append('| %s | %d | %+.3f | %+.3f (%.3f) | %+.3f – %+.3f | %+.1f |' % (k, x['punti'], x['differenza_vera'], x['nullo_media'], x['nullo_sd'], x['nullo_min'], x['nullo_max'], x['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b01_taratura_lessicale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
