# -*- coding: utf-8 -*-
"""Esperimento e3b13: accordo della scelta qo-/o- fra parole vicine (d 2-3) e lontane (d 6-10) nella stessa riga, a
parita' della classe di raccordo della parola precedente (V: -y,-o,-d; C: -n,-r,-s,-m,-l).

Preregistrazione: preregistrazioni/e3b13.md. Scrive risultati/e3b13_qo_raccordo.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def classe(prec):
    if prec[-1] in 'yod':
        return 'V'
    if prec[-1] in 'nrsml':
        return 'C'
    return None


def coppie(pagine):
    out = []
    rid = 0
    for righe in pagine:
        val = []
        for r in righe:
            vv = []
            for a, w in enumerate(r):
                q = e3b06.qo(w)
                c = classe(r[a - 1]) if a > 0 else None
                vv.append((q, c) if q is not None and c is not None else None)
            val.append(vv)
        tot, uno = Counter(), Counter()
        for i, vv in enumerate(val):
            for x in vv:
                if x:
                    tot[i, x[1]] += 1
                    uno[i, x[1]] += x[0]
        T = Counter()
        U = Counter()
        for (i, c), n in tot.items():
            T[c] += n
            U[c] += uno[i, c]
        for i, vv in enumerate(val):
            for a in range(len(vv)):
                if not vv[a]:
                    continue
                for d in e3b06.VICINO + e3b06.LONTANO:
                    b = a + d
                    if b >= len(vv) or not vv[b] or vv[b][1] != vv[a][1]:
                        continue
                    c = vv[a][1]
                    t = T[c] - tot[i, c]
                    u = U[c] - uno[i, c]
                    if t < 5:
                        continue
                    p = u / t
                    out.append((rid + i, 'vicino' if d in e3b06.VICINO else 'lontano', int(vv[a][0] == vv[b][0]), p * p + (1 - p) * (1 - p)))
        rid += len(righe)
    return out


def eccessi(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, g, ok, att in cc:
        acc[g][0] += ok - att
        acc[g][1] += 1
    return {g: (s / n, n) for g, (s, n) in acc.items()}


def main():
    rnd = random.Random(3213)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    cc = coppie(pagine)
    e = eccessi(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    bd = []
    for _ in range(BOOT):
        eb = eccessi([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        bd.append(eb['vicino'][0] - eb['lontano'][0])
    bd.sort()
    ic = [bd[int(0.025 * BOOT)], bd[int(0.975 * BOOT) - 1]]
    d = e['vicino'][0] - e['lontano'][0]
    esito = 'la memoria di qo-/o- resta a parità di raccordo' if ic[0] > 0 else 'era il raccordo'
    out = OrderedDict([('vicino', OrderedDict([('coppie', e['vicino'][1]), ('eccesso', e['vicino'][0])])), ('lontano', OrderedDict([('coppie', e['lontano'][1]), ('eccesso', e['lontano'][0])])),
                       ('differenza', d), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b13_qo_raccordo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b13 — La memoria corta di qo-/o- resta a parità di raccordo con la parola prima?', '', 'Preregistrazione: `preregistrazioni/e3b13.md`. Coppie con la stessa classe di raccordo della parola precedente (VV o CC).', '',
          '| coppie | quante | eccesso di accordo |', '|---|---|---|',
          '| vicine (d 2–3) | %d | %+.4f |' % (e['vicino'][1], e['vicino'][0]), '| lontane (d 6–10) | %d | %+.4f |' % (e['lontano'][1], e['lontano'][0]),
          '', 'Differenza **%+.4f**, IC 95%% %+.4f – %+.4f.' % (d, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b13_qo_raccordo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
