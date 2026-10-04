# -*- coding: utf-8 -*-
"""Esperimento e3b14: profilo dell'eccesso di accordo delle scelte di grafia (-ey/-dy, sh/ch, ee/e) per distanza d = 1..10
nella stessa riga, lingua A e B; mezza vita.

Preregistrazione: preregistrazioni/e3b14.md. Scrive risultati/e3b14_memoria_profilo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 1000
DD = range(1, 11)
CLASSI = OrderedDict((k, e3b06.CLASSI[k]) for k in ('-ey/-dy', 'sh/ch', 'ee/e'))


def coppie(pagine):
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
                for a in range(len(vv)):
                    if vv[a] is None:
                        continue
                    for d in DD:
                        b = a + d
                        if b < len(vv) and vv[b] is not None:
                            out.append((rid + i, d, int(vv[a] == vv[b]), att))
        rid += len(righe)
    return out


def profilo(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, d, ok, att in cc:
        acc[d][0] += ok - att
        acc[d][1] += 1
        if d >= 6:
            acc['6-10'][0] += ok - att
            acc['6-10'][1] += 1
    return {k: (s / n, n) for k, (s, n) in acc.items()}


def analizza(pagine, rnd):
    cc = coppie(pagine)
    pr = profilo(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    b1, bl = [], []
    for _ in range(BOOT):
        pb = profilo([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        b1.append(pb[1][0])
        bl.append(pb['6-10'][0])
    ic = lambda xs: [sorted(xs)[int(0.025 * BOOT)], sorted(xs)[int(0.975 * BOOT) - 1]]
    e1 = pr[1][0]
    mezza = next((d for d in DD if pr[d][0] < 0.5 * e1), None)
    i1 = ic(b1)
    if i1[0] > 0 and mezza is not None and mezza <= 4:
        es = 'memoria di breve durata'
    elif mezza is None or mezza > 6:
        es = 'memoria lunga'
    else:
        es = 'in mezzo'
    return OrderedDict([('profilo', OrderedDict((str(d), OrderedDict([('eccesso', pr[d][0]), ('coppie', pr[d][1])])) for d in DD)),
                        ('IC_d1', i1), ('eccesso_6_10', pr['6-10'][0]), ('IC_6_10', ic(bl)), ('mezza_vita', mezza), ('esito', es)])


def main():
    rnd = random.Random(3214)
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    per_l = defaultdict(list)
    for pg, pars in e341.pagine().items():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        per_l[lingua.get(pg)].append([r for r in righe if r])
    ris = OrderedDict()
    for lg in ('A', 'B'):
        ris['lingua ' + lg] = analizza(per_l[lg], rnd)
        print(lg, json.dumps(ris['lingua ' + lg], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b14_memoria_profilo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b14 — Quanto dura la memoria delle scelte di grafia?', '', 'Preregistrazione: `preregistrazioni/e3b14.md`. Classi -ey/-dy, sh/ch, ee/e; eccesso di accordo nella stessa riga.', '',
          '| d | ' + ' | '.join('%s: eccesso (coppie)' % k for k in ris) + ' |', '|---|' + '---|' * len(ris)]
    for d in DD:
        md.append('| %d | %s |' % (d, ' | '.join('%+.4f (%d)' % (x['profilo'][str(d)]['eccesso'], x['profilo'][str(d)]['coppie']) for x in ris.values())))
    md += ['']
    for k, x in ris.items():
        md.append('- %s: d = 1 IC %+.4f – %+.4f; d 6–10 %+.4f (IC %+.4f – %+.4f); mezza vita %s parole. Esito: **%s**.' % (k, x['IC_d1'][0], x['IC_d1'][1], x['eccesso_6_10'], x['IC_6_10'][0], x['IC_6_10'][1], x['mezza_vita'], x['esito']))
    open(os.path.join(RISULTATI, 'e3b14_memoria_profilo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
