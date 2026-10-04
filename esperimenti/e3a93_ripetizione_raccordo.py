# -*- coding: utf-8 -*-
"""Esperimento e3a93: nelle quasi ripetizioni immediate che cambiano solo l'inizio, il raccordo con la fine della parola
precedente (la parola ripetuta) migliora rispetto alla ripetizione esatta? Controllo a distanza 2.

Preregistrazione: preregistrazioni/e3a93.md. Scrive risultati/e3a93_ripetizione_raccordo.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 10000


def solo_inizio(w, v):
    """True se v differisce da w solo all'inizio (primo segno sostituito, tolto o aggiunto)."""
    if v == w:
        return False
    if len(v) == len(w):
        return v[1:] == w[1:]
    if len(v) == len(w) - 1:
        return v == w[1:]
    if len(v) == len(w) + 1:
        return v[1:] == w
    return False


def main():
    rnd = random.Random(3193)
    righe = [r for p in e375.voynich() for r in p]
    c = Counter((a[-1], b[0]) for r in righe for a, b in zip(r, r[1:]))
    n = sum(c.values())
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k

    def J(a, b):
        k = c.get((a, b), 0)
        return math.log((k + 0.5) * n / ((sa[a] + 0.5) * (sb[b] + 0.5)))
    imm, ctl = [], []
    esempi = Counter()
    for r in righe:
        for i in range(len(r) - 1):
            for dist, dest in ((1, imm), (2, ctl)):
                if i + dist >= len(r):
                    continue
                w, v = r[i], r[i + dist]
                if len(w) >= 3 and len(v) >= 3 and solo_inizio(w, v):
                    dest.append(J(w[-1], v[0]) - J(w[-1], w[0]))
                    if dist == 1:
                        esempi[''.join(w) + ' ' + ''.join(v)] += 1

    def ic(xs):
        b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(BOOT))
        return [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    mi, mc = statistics.mean(imm), statistics.mean(ctl)
    ici, icc = ic(imm), ic(ctl)
    if ici[0] > 0 and mc < ici[0]:
        esito = 'la ripetizione rispetta il raccordo'
    elif ici[0] <= 0 <= ici[1]:
        esito = 'no'
    else:
        esito = 'incerto'
    out = OrderedDict([('immediate', OrderedDict([('coppie', len(imm)), ('delta_medio', mi), ('IC95', ici), ('quota_positivi', sum(d > 0 for d in imm) / len(imm))])),
                       ('controllo_distanza_2', OrderedDict([('coppie', len(ctl)), ('delta_medio', mc), ('IC95', icc), ('quota_positivi', sum(d > 0 for d in ctl) / len(ctl))])),
                       ('esempi_immediati', esempi.most_common(15)), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a93_ripetizione_raccordo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a93 — Quando una parola si ripete subito con l\'inizio cambiato, il cambio rispetta il raccordo?', '', 'Preregistrazione: `preregistrazioni/e3a93.md`. Δ = raccordo reale − raccordo della ripetizione esatta (PMI, nat).', '',
          '| coppie | quante | Δ medio | IC 95% | quota con Δ > 0 |', '|---|---|---|---|---|']
    for k, x in (('immediate', out['immediate']), ('distanza 2 (controllo)', out['controllo_distanza_2'])):
        md.append('| %s | %d | %+.3f | %+.3f – %+.3f | %.2f |' % (k, x['coppie'], x['delta_medio'], x['IC95'][0], x['IC95'][1], x['quota_positivi']))
    md += ['', 'Esempi più frequenti (immediati): ' + '; '.join('*%s* (%d)' % kv for kv in esempi.most_common(10)), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a93_ripetizione_raccordo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
