# -*- coding: utf-8 -*-
"""Esperimento e3b28: e3b27 con il confronto fatto sulle righe della pagina (o del paragrafo) precedente che hanno quasi la
stessa lunghezza dell'ultima riga.

Preregistrazione: preregistrazioni/e3b28.md. Scrive risultati/e3b28_ripresa_pagine_lunghezza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3b27_ripresa_pagine as e3b27

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def simili_lunghezza(righe, ultima):
    return [r for r in righe if abs(len(r) - len(ultima)) <= 1]


def main():
    rnd = random.Random(3228)
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append((pg, [par for par in pp if par]))
    coppie = {'stesso foglio': [], 'affiancate': []}
    for (p, pp), (q, qq) in zip(pagine, pagine[1:]):
        fp, fq = e3b27.foglio(p), e3b27.foglio(q)
        if not fp or not fq or lingua.get(p) != lingua.get(q) or lingua.get(p) not in ('A', 'B'):
            continue
        righe_p = [r for par in pp for r in par]
        righe_q = [r for par in qq for r in par]
        if len(righe_p) < 4 or len(righe_q) < 4:
            continue
        if fp[0] == fq[0] and fp[1] == 'r' and fq[1] == 'v':
            tipo = 'stesso foglio'
        elif fq[0] == fp[0] + 1 and fp[1] == 'v' and fq[1] == 'r':
            tipo = 'affiancate'
        else:
            continue
        altre = simili_lunghezza(righe_p[:-1], righe_p[-1])
        e = e3b27.eccesso(righe_q[0], righe_p[-1], altre)
        if e is not None:
            coppie[tipo].append(e)
    dentro = []
    for _, pp in pagine:
        for a, b in zip(pp, pp[1:]):
            altre = simili_lunghezza(a[:-1], a[-1])
            e = e3b27.eccesso(b[0], a[-1], altre)
            if e is not None:
                dentro.append(e)

    def ic(xs):
        b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(BOOT))
        return [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    tutte = coppie['stesso foglio'] + coppie['affiancate']
    ris = OrderedDict()
    for k, xs in (('tutte le coppie di pagine', tutte), ('stesso foglio (r → v)', coppie['stesso foglio']), ('affiancate (v → r)', coppie['affiancate']), ('fra paragrafi della stessa pagina', dentro)):
        ris[k] = OrderedDict([('coppie', len(xs)), ('eccesso', statistics.mean(xs) if xs else None), ('IC95', ic(xs) if len(xs) > 5 else None)])
    esito = 'la ripresa passa la pagina' if ris['tutte le coppie di pagine']['IC95'][0] > 0 else 'la pagina interrompe la ripresa'
    out = OrderedDict([('risultati', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b28_ripresa_pagine_lunghezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b28 — La ripresa passa la pagina? (confronto con righe della stessa lunghezza)', '', 'Preregistrazione: `preregistrazioni/e3b28.md`.', '',
          '| confronto | coppie | eccesso | IC 95% |', '|---|---|---|---|']
    md += ['| %s | %d | %s | %s |' % (k, x['coppie'], '%+.4f' % x['eccesso'] if x['eccesso'] is not None else 'n.d.', '%+.4f – %+.4f' % tuple(x['IC95']) if x['IC95'] else 'n.d.') for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b28_ripresa_pagine_lunghezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
