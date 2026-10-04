# -*- coding: utf-8 -*-
"""Esperimento e3a96: e3a93 (ripetizione immediata con l'inizio cambiato e raccordo) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3a96.md. Scrive risultati/e3a96_ripetizione_raccordo_it.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e3a50_dentro_fra_trascrizioni as e3a50
import e3a93_ripetizione_raccordo as e3a93

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 10000


def main():
    rnd = random.Random(3196)
    righe = [r for p in e3a50.pagine('IT', lambda w: tuple(D(w))) for r in p]
    c = Counter((a[-1], b[0]) for r in righe for a, b in zip(r, r[1:]))
    n = sum(c.values())
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k

    def J(a, b):
        return math.log((c.get((a, b), 0) + 0.5) * n / ((sa[a] + 0.5) * (sb[b] + 0.5)))
    imm, ctl = [], []
    for r in righe:
        for i in range(len(r) - 1):
            for dist, dest in ((1, imm), (2, ctl)):
                if i + dist >= len(r):
                    continue
                w, v = r[i], r[i + dist]
                if len(w) >= 3 and len(v) >= 3 and e3a93.solo_inizio(w, v):
                    dest.append(J(w[-1], v[0]) - J(w[-1], w[0]))

    def ic(xs):
        b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(BOOT))
        return [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    ici, icc = ic(imm), ic(ctl)
    mi, mc = statistics.mean(imm), statistics.mean(ctl)
    esito = 'si ritrova' if ici[0] > 0 and mc < ici[0] else ('in parte' if ici[0] > 0 else 'non si ritrova')
    out = OrderedDict([('immediate', OrderedDict([('coppie', len(imm)), ('delta_medio', mi), ('IC95', ici)])),
                       ('distanza_2', OrderedDict([('coppie', len(ctl)), ('delta_medio', mc), ('IC95', icc)])), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a96_ripetizione_raccordo_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a96 — La ripetizione che si adatta al raccordo (e3a93) si ritrova con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3a96.md`. ZL (e3a93): immediate +0,167 (IC +0,103 – +0,231); distanza 2 +0,045.', '',
          '| coppie | quante | Δ medio | IC 95% |', '|---|---|---|---|',
          '| immediate | %d | %+.3f | %+.3f – %+.3f |' % (len(imm), mi, ici[0], ici[1]),
          '| a distanza 2 | %d | %+.3f | %+.3f – %+.3f |' % (len(ctl), mc, icc[0], icc[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a96_ripetizione_raccordo_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
