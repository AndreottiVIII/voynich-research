# -*- coding: utf-8 -*-
"""Esperimento e3b29: distribuzione, fra le righe, della quota di parole riprese dalla riga sopra; righe "quasi copiate"
e varianza, contro un nullo che usa un'altra riga del paragrafo come "riga sopra".

Preregistrazione: preregistrazioni/e3b29.md. Scrive risultati/e3b29_copia_raffiche.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 200


def quota(riga, rif, sim):
    bers = [w for w in riga if len(w) >= 3]
    s = set(rif)
    return sum(1 for w in bers if sim[w] & s) / len(bers)


def main():
    rnd = random.Random(3229)
    unita = []   # (paragrafo, sim, indice riga)
    for pars in e341.pagine().values():
        for par in pars:
            pp = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            pp = [r for r in pp if r]
            if len(pp) < 3:
                continue
            sim = e385.simili_unita(pp)
            for i in range(1, len(pp)):
                if sum(1 for w in pp[i] if len(w) >= 3) >= 6:
                    unita.append((pp, sim, i))
    oss = [quota(pp[i], pp[i - 1], sim) for pp, sim, i in unita]
    coda = lambda xs: sum(1 for x in xs if x >= 0.5) / len(xs)
    c_o, v_o = coda(oss), float(np.var(oss))
    # media del nullo semplice (un'altra riga del paragrafo), per calcolare la copia in piu' da spargere
    base = []
    for pp, sim, i in unita:
        j = rnd.choice([j for j in range(len(pp)) if j != i])
        base.append(quota(pp[i], pp[j], sim))
    e = max(0.0, (statistics.mean(oss) - statistics.mean(base)) / (1 - statistics.mean(base)))
    c_n, v_n = [], []
    for _ in range(PERM):
        xs = []
        for pp, sim, i in unita:
            j = rnd.choice([j for j in range(len(pp)) if j != i])
            x = quota(pp[i], pp[j], sim)
            n = sum(1 for w in pp[i] if len(w) >= 3)
            libere = round(n * (1 - x))
            xs.append(x + sum(1 for _ in range(libere) if rnd.random() < e) / n)
        c_n.append(coda(xs))
        v_n.append(float(np.var(xs)))
    p99c, p95c, p99v = float(np.percentile(c_n, 99)), float(np.percentile(c_n, 95)), float(np.percentile(v_n, 99))
    if c_o > p99c and v_o > p99v:
        esito = 'a raffiche'
    elif c_o < p95c:
        esito = 'sparsa'
    else:
        esito = 'incerto'
    out = OrderedDict([('righe', len(unita)), ('media_osservata', statistics.mean(oss)), ('media_nullo_semplice', statistics.mean(base)), ('copia_sparsa_aggiunta', e), ('quota_quasi_copiate', c_o), ('nullo_quota_media', statistics.mean(c_n)), ('nullo_quota_p99', p99c),
                       ('varianza', v_o), ('nullo_varianza_media', statistics.mean(v_n)), ('nullo_varianza_p99', p99v),
                       ('distribuzione', OrderedDict((str(b), sum(1 for x in oss if b <= x < b + 0.1) / len(oss)) for b in np.round(np.arange(0, 1.0, 0.1), 1))), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b29_copia_raffiche.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b29 — La copia dalla riga sopra è sparsa o a raffiche?', '', 'Preregistrazione: `preregistrazioni/e3b29.md`.', '',
          'Righe: %d. Quota media di parole con una simile nella riga sopra: %.3f.' % (len(unita), out['media_osservata']), '',
          '| misura | osservata | nullo (media) | nullo (99° percentile) |', '|---|---|---|---|',
          '| righe con metà o più parole riprese | %.4f | %.4f | %.4f |' % (c_o, out['nullo_quota_media'], p99c),
          '| varianza della quota fra le righe | %.4f | %.4f | %.4f |' % (v_o, out['nullo_varianza_media'], p99v), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b29_copia_raffiche.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
