# -*- coding: utf-8 -*-
"""Esperimento 96: l'evitamento fra inizi di riga sopravvive alla fusione delle famiglie di segni (e95)?

Preregistrazione: preregistrazioni/e96.md. Scrive risultati/e96_evitamento_famiglie.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e83_evitamento_inizi as e83

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 96, 500
FAMIGLIE = {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'k': 'G', 't': 'G', 'p': 'G', 'f': 'G', 'd': 'D', 'r': 'D', 's': 'D'}


def famiglia(w):
    g = e83.primo_eva(w)
    return FAMIGLIE.get(g, g)


def dentro_famiglia(per, rnd):
    """Fra le coppie con la stessa famiglia, quota con lo stesso segno, contro il nullo."""
    def stat(cc):
        sel = [(a, b) for a, b in cc if FAMIGLIE.get(a) and FAMIGLIE.get(a) == FAMIGLIE.get(b)]
        return (sum(a == b for a, b in sel) / len(sel) if sel else None), len(sel)
    reale = [c for rr in per.values() for c in e83.coppie(rr, 1, e83.primo_eva)]
    q, n = stat(reale)
    nulli = []
    for _ in range(PERMUTAZIONI):
        cc = []
        for rr in per.values():
            idx = [i for i, (_, ini, _) in enumerate(rr) if not ini]
            ws = [rr[i][2] for i in idx]
            rnd.shuffle(ws)
            nuova = list(rr)
            for i, w in zip(idx, ws):
                nuova[i] = (rr[i][0], False, w)
            cc.extend(e83.coppie(nuova, 1, e83.primo_eva))
        x, _ = stat(cc)
        nulli.append(x)
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', n), ('osservata', q), ('attesa', m), ('S', q / m), ('z', (q - m) / s if s else None)])


def main():
    e83.PERMUTAZIONI = PERMUTAZIONI
    per = e83.pagine('ZL')
    ris = OrderedDict()
    ris['primo segno'] = e83.misura(per, 1, e83.primo_eva, random.Random(SEME))
    ris['famiglia del primo segno'] = e83.misura(per, 1, famiglia, random.Random(SEME))
    ris['dentro la famiglia'] = dentro_famiglia(per, random.Random(SEME))
    for k, r in ris.items():
        e83.riga(k, r)
    sf, sd = ris['famiglia del primo segno']['S'], ris['dentro la famiglia']['S']
    ris['lettura'] = ('variazione grafica' if sf >= 0.85 and sd < 0.7 else 'unità sottostante' if sf < 0.7 else 'misto')
    print('lettura:', ris['lettura'])
    with open(os.path.join(RISULTATI, 'e96_evitamento_famiglie.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e96 — L\'evitamento fra inizi di riga sopravvive alla fusione delle famiglie?', '',
           'Famiglie: {ch, sh, ckh, cth}, {k, t, p, f}, {d, r, s}. S come nell\'e83. Preregistrazione: '
           '`preregistrazioni/e96.md`.', '', '| misura | coppie | osservata | attesa | S | z |', '|---|---|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (k, r['n'], r['osservata'], r['attesa'], r['S'], r['z'] or 0))
    out += ['', 'Lettura: **%s**.' % ris['lettura']]
    with open(os.path.join(RISULTATI, 'e96_evitamento_famiglie.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
