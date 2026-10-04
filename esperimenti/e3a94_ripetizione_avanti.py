# -*- coding: utf-8 -*-
"""Esperimento e3a94: nelle quasi ripetizioni che cambiano solo la fine, il raccordo con la parola dopo migliora rispetto
alla ripetizione esatta? Coppie immediate e a distanza 2.

Preregistrazione: preregistrazioni/e3a94.md. Scrive risultati/e3a94_ripetizione_avanti.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 10000


def solo_fine(w, v):
    if v == w:
        return False
    if len(v) == len(w):
        return v[:-1] == w[:-1]
    if len(v) == len(w) - 1:
        return v == w[:-1]
    if len(v) == len(w) + 1:
        return v[:-1] == w
    return False


def main():
    rnd = random.Random(3194)
    righe = [r for p in e375.voynich() for r in p]
    c = Counter((a[-1], b[0]) for r in righe for a, b in zip(r, r[1:]))
    n = sum(c.values())
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k

    def J(a, b):
        return math.log((c.get((a, b), 0) + 0.5) * n / ((sa[a] + 0.5) * (sb[b] + 0.5)))
    imm, ctl = [], []
    esempi = Counter()
    for r in righe:
        for i in range(len(r)):
            for dist, dest in ((1, imm), (2, ctl)):
                j = i + dist
                if j + 1 >= len(r):
                    continue
                w, v, u = r[i], r[j], r[j + 1]
                if len(w) >= 3 and len(v) >= 3 and solo_fine(w, v):
                    dest.append(J(v[-1], u[0]) - J(w[-1], u[0]))
                    if dist == 1:
                        esempi[' '.join(''.join(x) for x in (w, v, u))] += 1

    def ic(xs):
        b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(BOOT))
        return [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    ici, icc = ic(imm), ic(ctl)
    esito = 'la ripetizione guarda avanti' if ici[0] > 0 else 'no'
    out = OrderedDict([('immediate', OrderedDict([('coppie', len(imm)), ('delta_medio', statistics.mean(imm)), ('IC95', ici), ('quota_positivi', sum(d > 0 for d in imm) / len(imm))])),
                       ('distanza_2', OrderedDict([('coppie', len(ctl)), ('delta_medio', statistics.mean(ctl)), ('IC95', icc), ('quota_positivi', sum(d > 0 for d in ctl) / len(ctl))])),
                       ('esempi_immediati', esempi.most_common(15)), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a94_ripetizione_avanti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a94 — Quando una parola si ripete subito con la fine cambiata, il cambio si adatta alla parola dopo?', '', 'Preregistrazione: `preregistrazioni/e3a94.md`. Δ = raccordo della fine reale con la parola dopo − raccordo della fine originale (PMI, nat).', '',
          '| coppie | quante | Δ medio | IC 95% | quota con Δ > 0 |', '|---|---|---|---|---|']
    for k, x in (('immediate', out['immediate']), ('a distanza 2', out['distanza_2'])):
        md.append('| %s | %d | %+.3f | %+.3f – %+.3f | %.2f |' % (k, x['coppie'], x['delta_medio'], x['IC95'][0], x['IC95'][1], x['quota_positivi']))
    md += ['', 'Esempi (immediati, con la parola dopo): ' + '; '.join('*%s* (%d)' % kv for kv in esempi.most_common(10)), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a94_ripetizione_avanti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
