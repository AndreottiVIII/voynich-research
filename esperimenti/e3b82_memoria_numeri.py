# -*- coding: utf-8 -*-
"""Esperimento e3b82 (descrittivo): probabilità che la scelta di grafia si ripeta a 2-3 parole e a 6-10 parole nella
stessa riga, coppie simili tolte sulle parole coperte. ZL e IT.

Preregistrazione: preregistrazioni/e3b82.md. Scrive risultati/e3b82_memoria_numeri.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
VICINE, LONTANE = (2, 3), tuple(range(6, 11))
NOMI_1 = {'qo/o': 'qo', 'k/t': 'k', 'sh/ch': 'sh', '-ey/-dy': '-ey'}


def conteggi(pagine, f):
    c = Counter()
    tot = Counter()
    for righe in pagine:
        for s in righe:
            xs = [f(w) for w in s]
            for x in xs:
                if x:
                    tot[x[0]] += 1
            for i in range(len(s)):
                if not xs[i]:
                    continue
                for d in VICINE + LONTANE:
                    j = i + d
                    if j >= len(s) or not xs[j]:
                        continue
                    a, b = xs[i], xs[j]
                    if a[1] == b[1] or e3a86.una_modifica(a[1], b[1]):
                        continue
                    c[('vicine' if d in VICINE else 'lontane', a[0], b[0])] += 1
    return c, tot


def main():
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, _ = e3b62.voynich(pd, mano)
        x = OrderedDict()
        for k, f in e3b62.CV.items():
            c, tot = conteggi(uu, f)
            y = OrderedDict([('quota_1', tot[1] / (tot[0] + tot[1]))])
            for g in ('vicine', 'lontane'):
                d1 = c[(g, 1, 1)] + c[(g, 1, 0)]
                d0 = c[(g, 0, 1)] + c[(g, 0, 0)]
                y['P(1|1) %s' % g] = c[(g, 1, 1)] / d1 if d1 else None
                y['P(1|0) %s' % g] = c[(g, 0, 1)] / d0 if d0 else None
                y['coppie %s' % g] = d1 + d0
            x[k] = y
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b82_memoria_numeri.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b82 — La memoria delle scelte in numeri semplici (descrittivo)', '', 'Preregistrazione: `preregistrazioni/e3b82.md`. P(1|1) = probabilità che la seconda parola abbia la variante 1 se la prima la ha; P(1|0) = se la prima ha l\'altra.', '',
          '| trascrizione | scelta (variante 1) | quota generale | vicine 2–3: P(1 dopo 1) / P(1 dopo 0) | lontane 6–10: P(1 dopo 1) / P(1 dopo 0) |', '|---|---|---|---|---|']
    for q, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s (%s) | %.2f | %.2f / %.2f | %.2f / %.2f |' % (q, k, NOMI_1[k], y['quota_1'], y['P(1|1) vicine'], y['P(1|0) vicine'], y['P(1|1) lontane'], y['P(1|0) lontane']))
    open(os.path.join(RISULTATI, 'e3b82_memoria_numeri.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
