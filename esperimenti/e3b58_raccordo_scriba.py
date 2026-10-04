# -*- coding: utf-8 -*-
"""Esperimento e3b58: informazione mutua fra la scelta a inizio parola (þ/ð nei Hatton Gospels, qo/o nel Voynich) e
l'ultima lettera della parola prima, contro un nullo che rimescola la scelta fra le occorrenze dello stesso tipo di
parola nella stessa unità.

Preregistrazione: preregistrazioni/e3b58.md. Scrive risultati/e3b58_raccordo_scriba.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def eventi(unita, f):
    """unita: [ [sequenze di parole] ]; f(w) -> (valore, tipo coperto) o None. Ritorna array (valore, contesto, gruppo)."""
    val, ctx, grp, gruppi, ctxid = [], [], [], {}, {}
    for u, seqs in enumerate(unita):
        for s in seqs:
            for i in range(1, len(s)):
                x = f(s[i])
                if x is None or not s[i - 1]:
                    continue
                val.append(x[0])
                ctx.append(ctxid.setdefault(s[i - 1][-1], len(ctxid)))
                grp.append(gruppi.setdefault((u, x[1]), len(gruppi)))
    return np.array(val), np.array(ctx), np.array(grp), len(ctxid)


def mi(val, ctx, nc):
    n = len(val)
    tab = np.zeros((2, nc))
    np.add.at(tab, (val, ctx), 1)
    pv = tab.sum(1) / n
    pc = tab.sum(0) / n
    p = tab / n
    m = p > 0
    return float((p[m] * np.log2(p[m] / (pv[:, None] * pc[None, :])[m])).sum())


def entropia(val):
    p = val.mean()
    return -sum(x * math.log2(x) for x in (p, 1 - p) if x > 0)


def prova(val, ctx, grp, nc, rng):
    oss = mi(val, ctx, nc)
    pos = np.argsort(grp, kind='stable')
    nul = []
    for _ in range(PERM):
        order = np.lexsort((rng.random(len(val)), grp))
        v = np.empty_like(val)
        v[pos] = val[order]
        nul.append(mi(v, ctx, nc))
    mu = float(np.mean(nul))
    h = entropia(val)
    return OrderedDict([('occorrenze', int(len(val))), ('quota_1', float(val.mean())), ('entropia', h), ('MI', oss), ('MI_nullo', mu),
                        ('effetto', oss - mu), ('effetto_su_entropia', (oss - mu) / h if h else None), ('p', float(np.mean([x >= oss for x in nul]))),
                        ('z', (oss - mu) / float(np.std(nul)) if np.std(nul) > 0 else 0.0)])


def main():
    rng = np.random.default_rng(3258)
    righe = [r for r in e381.testi()[e3b51.TESTI['Hatton Gospels']] if r]
    h = prova(*eventi([[b] for b in e3b51.blocchi(righe)], e3b54.v_th_ini), rng)
    print('Hatton', json.dumps(h), flush=True)
    voy = []
    for pg, pars in e341.pagine().items():
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            voy.append(rr)
    v = prova(*eventi(voy, e3b54.v_qo), rng)
    print('Voynich', json.dumps(v), flush=True)
    esito = 'anche lo scriba anglosassone ha un raccordo' if h['p'] < 0.01 else ('nessun raccordo nello scriba anglosassone' if h['p'] > 0.05 else 'incerto')
    out = OrderedDict([('Hatton Gospels, þ/ð a inizio parola', h), ('Voynich ZL, qo/o', v), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b58_raccordo_scriba.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b58 — Anche lo scriba anglosassone ha un "raccordo"?', '', 'Preregistrazione: `preregistrazioni/e3b58.md`. Informazione mutua fra la scelta a inizio parola e l\'ultima lettera della parola prima; nullo che tiene ferme le parole.', '',
          '| testo, scelta | occorrenze | quota þ / qo | entropia (bit) | MI osservata | MI nullo | effetto | effetto / entropia | z | p |', '|---|---|---|---|---|---|---|---|---|---|']
    for k in ('Hatton Gospels, þ/ð a inizio parola', 'Voynich ZL, qo/o'):
        x = out[k]
        md.append('| %s | %d | %.3f | %.3f | %.4f | %.4f | %+.4f | %+.3f | %+.1f | %.3f |' % (k, x['occorrenze'], x['quota_1'], x['entropia'], x['MI'], x['MI_nullo'], x['effetto'], x['effetto_su_entropia'], x['z'], x['p']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b58_raccordo_scriba.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
