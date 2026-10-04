# -*- coding: utf-8 -*-
"""Esperimento e3b10: accordo delle scelte di grafia (classi dell'e3b06) fra parole a distanza 2-3, nella stessa riga e a
cavallo dell'a capo, rispetto all'atteso dalla pagina senza le righe coinvolte.

Preregistrazione: preregistrazioni/e3b10.md. Scrive risultati/e3b10_scelte_a_capo.json e .md.
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


def coppie_pagina(pars, pid):
    """[(id paragrafo, tipo, accordo, atteso)] per una pagina (lista di paragrafi di righe di stringhe)."""
    righe = [r for par in pars for r in par]
    out = []
    for c, f in e3b06.CLASSI.items():
        tot = Counter()
        uno = Counter()
        for i, r in enumerate(righe):
            vv = [f(w) for w in r]
            tot[i] = sum(1 for v in vv if v is not None)
            uno[i] = sum(1 for v in vv if v == 1)
        T, U = sum(tot.values()), sum(uno.values())
        k = 0
        for j, par in enumerate(pars):
            seq = [(i, f(w)) for i in range(k, k + len(par)) for w in righe[i]]
            for a in range(len(seq)):
                for d in (2, 3):
                    b = a + d
                    if b >= len(seq):
                        continue
                    (ia, va), (ib, vb) = seq[a], seq[b]
                    if va is None or vb is None:
                        continue
                    ii = {ia, ib}
                    t = T - sum(tot[i] for i in ii)
                    u = U - sum(uno[i] for i in ii)
                    if t < 5:
                        continue
                    p = u / t
                    tipo = 'stessa riga' if ia == ib else 'a cavallo'
                    out.append(((pid, j), tipo, int(va == vb), p * p + (1 - p) * (1 - p)))
            k += len(par)
    return out


def eccessi(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, t, ok, att in cc:
        acc[t][0] += ok - att
        acc[t][1] += 1
    return {t: (s / n, n) for t, (s, n) in acc.items()}


def main():
    rnd = random.Random(3210)
    cc = []
    for pid, pars in enumerate(e341.pagine().values()):
        pp = [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        cc += coppie_pagina([par for par in pp if par], pid)
    e = eccessi(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    bs, bc, bd = [], [], []
    for _ in range(BOOT):
        eb = eccessi([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        bs.append(eb['stessa riga'][0])
        bc.append(eb['a cavallo'][0])
        bd.append(eb['stessa riga'][0] - eb['a cavallo'][0])

    def ic(xs):
        xs = sorted(xs)
        return [xs[int(0.025 * BOOT)], xs[int(0.975 * BOOT) - 1]]
    s, c = e['stessa riga'][0], e['a cavallo'][0]
    d_ic = ic(bd)
    if c < 0.5 * s and d_ic[0] > 0:
        esito = "l'a capo azzera la memoria delle scelte"
    elif c >= 0.75 * s:
        esito = "la memoria passa l'a capo"
    else:
        esito = 'in mezzo'
    out = OrderedDict([('stessa_riga', OrderedDict([('coppie', e['stessa riga'][1]), ('eccesso', s), ('IC95', ic(bs))])),
                       ('a_cavallo', OrderedDict([('coppie', e['a cavallo'][1]), ('eccesso', c), ('IC95', ic(bc))])),
                       ('differenza', s - c), ('IC95_differenza', d_ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b10_scelte_a_capo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b10 — La memoria corta delle scelte di grafia attraversa l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3b10.md`. Coppie a distanza 2–3 parole.', '',
          '| coppie | quante | eccesso di accordo | IC 95% |', '|---|---|---|---|',
          '| stessa riga | %d | %+.4f | %+.4f – %+.4f |' % (out['stessa_riga']['coppie'], s, out['stessa_riga']['IC95'][0], out['stessa_riga']['IC95'][1]),
          '| a cavallo dell\'a capo | %d | %+.4f | %+.4f – %+.4f |' % (out['a_cavallo']['coppie'], c, out['a_cavallo']['IC95'][0], out['a_cavallo']['IC95'][1]),
          '', 'Differenza **%+.4f**, IC 95%% %+.4f – %+.4f.' % (s - c, d_ic[0], d_ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b10_scelte_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
