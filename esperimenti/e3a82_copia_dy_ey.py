# -*- coding: utf-8 -*-
"""Esperimento e3a82: coppie di parole uguali tranne la finale -dy/-ey in righe della stessa pagina, a distanza 1 e da 3 a
5; quota con -dy sopra e -ey sotto.

Preregistrazione: preregistrazioni/e3a82.md. Scrive risultati/e3a82_copia_dy_ey.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

from scipy.stats import binomtest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')


def conta(righe, distanze):
    """righe: liste di parole (stringhe EVA) di una pagina. Restituisce (A, B)."""
    A = B = 0
    idx = []
    for r in righe:
        d = defaultdict(lambda: [0, 0])
        for w in r:
            if len(w) >= 3 and w[-2:] in ('dy', 'ey'):
                d[w[:-2]][w[-2:] == 'ey'] += 1
        idx.append(d)
    for i in range(len(righe)):
        for k in distanze:
            j = i + k
            if j >= len(righe):
                continue
            for x, (dy_s, ey_s) in idx[i].items():
                if x in idx[j]:
                    dy_g, ey_g = idx[j][x]
                    A += dy_s * ey_g
                    B += ey_s * dy_g
    return A, B


def main():
    tot = OrderedDict([('distanza 1', [0, 0]), ('distanza 3-5', [0, 0])])
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        for nome, dd in (('distanza 1', (1,)), ('distanza 3-5', (3, 4, 5))):
            a, b = conta(righe, dd)
            tot[nome][0] += a
            tot[nome][1] += b
    ris = OrderedDict()
    for nome, (a, b) in tot.items():
        p = binomtest(a, a + b, 0.5).pvalue if a + b else None
        ris[nome] = OrderedDict([('A_dy_sopra_ey_sotto', a), ('B_ey_sopra_dy_sotto', b), ('q', a / (a + b) if a + b else None), ('p', p)])
    q1, ql, p1 = ris['distanza 1']['q'], ris['distanza 3-5']['q'], ris['distanza 1']['p']
    if q1 is not None and p1 < 0.01 and q1 > 0.5 and q1 >= ql:
        esito = 'la copia spinge verso -ey'
    elif q1 is not None and p1 < 0.01 and q1 < 0.5:
        esito = 'la copia spinge verso -dy'
    else:
        esito = 'la copia non ha direzione'
    out = OrderedDict([('conteggi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a82_copia_dy_ey.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a82 — -ey cresce scendendo perché la copia trasforma -dy in -ey?', '', 'Preregistrazione: `preregistrazioni/e3a82.md`.', '',
          '| distanza fra le righe | -dy sopra, -ey sotto (A) | -ey sopra, -dy sotto (B) | q = A/(A+B) | p (binomiale) |', '|---|---|---|---|---|']
    md += ['| %s | %d | %d | %.3f | %.2g |' % (k, x['A_dy_sopra_ey_sotto'], x['B_ey_sopra_dy_sotto'], x['q'], x['p']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a82_copia_dy_ey.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
