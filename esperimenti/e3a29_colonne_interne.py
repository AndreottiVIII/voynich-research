# -*- coding: utf-8 -*-
"""Esperimento e3a29: somiglianza nelle colonne interne (2, 3, 4, penultima) di righe consecutive, con il nullo che
rimescola solo le parole interne (prima e ultima ferme).

Preregistrazione: preregistrazioni/e3a29.md. Scrive risultati/e3a29_colonne_interne.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
COLONNE = [1, 2, 3, -2]


def interne(r, rnd):
    mezzo = r[1:-1]
    return [r[0]] + rnd.sample(mezzo, len(mezzo)) + [r[-1]]


def quote(coppie, chiave):
    return [sum(chiave(a[c]) == chiave(b[c]) for a, b in coppie) / len(coppie) for c in COLONNE]


def main():
    rnd = random.Random(3129)
    coppie = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            for i in range(2, len(rr)):
                if len(rr[i]) >= 5 and len(rr[i - 1]) >= 5:
                    coppie.append((rr[i], rr[i - 1]))
    ris = OrderedDict()
    for nome, chiave in (('stessi primi 2 segni', lambda w: w[:2]), ('parola uguale', lambda w: w)):
        vero = quote(coppie, chiave)
        nul = [quote([(interne(a, rnd), interne(b, rnd)) for a, b in coppie], chiave) for _ in range(1000)]
        x = OrderedDict()
        for k, c in enumerate(COLONNE):
            xs = [n[k] for n in nul]
            m, sd = statistics.mean(xs), statistics.pstdev(xs)
            r = vero[k] / m if m else None
            z = (vero[k] - m) / sd if sd else 0.0
            es = 'ripete nella stessa colonna' if r is not None and r > 1.2 and z > 3 else ('evita' if r is not None and r < 0.8 and z < -3 else 'indifferente')
            x['colonna %s' % ('penultima' if c == -2 else c + 1)] = OrderedDict([('osservata', vero[k]), ('nullo', m), ('rapporto', r), ('z', z), ('esito', es)])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    out = OrderedDict([('coppie_di_righe', len(coppie)), ('misure', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a29_colonne_interne.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a29 — Le colonne interne ripetono davvero? (nullo con i bordi fermi)', '', 'Preregistrazione: `preregistrazioni/e3a29.md`. %d coppie di righe consecutive.' % len(coppie), '']
    for nome, x in ris.items():
        md += ['## %s' % nome, '', '| colonna | osservata | nullo | rapporto | z | esito |', '|---|---|---|---|---|---|']
        md += ['| %s | %.3f | %.3f | %.2f | %.1f | %s |' % (k, v['osservata'], v['nullo'], v['rapporto'], v['z'], v['esito']) for k, v in x.items()]
        md.append('')
    open(os.path.join(RISULTATI, 'e3a29_colonne_interne.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
