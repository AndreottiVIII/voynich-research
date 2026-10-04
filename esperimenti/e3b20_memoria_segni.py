# -*- coding: utf-8 -*-
"""Esperimento e3b20: a parita' di distanza in parole (2 e 3), l'accordo delle scelte di grafia e' maggiore quando fra le
due parole ci sono poche lettere?

Preregistrazione: preregistrazioni/e3b20.md. Scrive risultati/e3b20_memoria_segni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06
import e3b19_altre_scelte as e3b19

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
CLASSI = OrderedDict([(k, e3b06.CLASSI[k]) for k in ('qo/o', '-ey/-dy', 'sh/ch', 'ee/e')] + [('k/t', e3b19.kt)])


def coppie(pagine):
    """[(id riga, d, lettere in mezzo, accordo, atteso)]."""
    out = []
    rid = 0
    for righe in pagine:
        for c, f in CLASSI.items():
            val = [[f(w) for w in r] for r in righe]
            tot = [sum(1 for v in vv if v is not None) for vv in val]
            uno = [sum(1 for v in vv if v == 1) for vv in val]
            T, U = sum(tot), sum(uno)
            for i, vv in enumerate(val):
                t, u = T - tot[i], U - uno[i]
                if t < 5:
                    continue
                p = u / t
                att = p * p + (1 - p) * (1 - p)
                r = righe[i]
                for a in range(len(vv)):
                    if vv[a] is None:
                        continue
                    for d in (2, 3):
                        b = a + d
                        if b < len(vv) and vv[b] is not None:
                            out.append((rid + i, d, sum(len(w) for w in r[a + 1:b]), int(vv[a] == vv[b]), att))
        rid += len(righe)
    return out


def differenza(cc, mediane):
    acc = defaultdict(lambda: [0.0, 0])
    for _, d, l, ok, att in cc:
        g = 'poche' if l < mediane[d] else ('molte' if l > mediane[d] else None)
        if g:
            acc[d, g][0] += ok - att
            acc[d, g][1] += 1
    num = den = 0.0
    for d in (2, 3):
        if acc[d, 'poche'][1] and acc[d, 'molte'][1]:
            w = acc[d, 'poche'][1] + acc[d, 'molte'][1]
            num += w * (acc[d, 'poche'][0] / acc[d, 'poche'][1] - acc[d, 'molte'][0] / acc[d, 'molte'][1])
            den += w
    return num / den, {('%d %s' % k): (s / n if n else None, n) for k, (s, n) in acc.items()}


def main():
    rnd = random.Random(3220)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    cc = coppie(pagine)
    mediane = {d: statistics.median(l for _, dd, l, _, _ in cc if dd == d) for d in (2, 3)}
    dv, dett = differenza(cc, mediane)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    b = sorted(differenza([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]], mediane)[0] for _ in range(BOOT))
    ic = [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    esito = 'la memoria si misura (anche) in segni' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'la memoria si misura in parole')
    out = OrderedDict([('mediane_lettere', mediane), ('dettaglio', dett), ('differenza', dv), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b20_memoria_segni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b20 — La memoria corta si misura in parole o in segni scritti?', '', 'Preregistrazione: `preregistrazioni/e3b20.md`. Mediana delle lettere in mezzo: d 2 → %s, d 3 → %s.' % (mediane[2], mediane[3]), '',
          '| distanza e lettere in mezzo | eccesso di accordo | coppie |', '|---|---|---|']
    md += ['| %s | %s | %d |' % (k, '%+.4f' % v[0] if v[0] is not None else 'n.d.', v[1]) for k, v in sorted(dett.items())]
    md += ['', 'Differenza "poche" − "molte": **%+.4f**, IC 95%% %+.4f – %+.4f.' % (dv, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b20_memoria_segni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
