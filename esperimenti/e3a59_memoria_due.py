# -*- coding: utf-8 -*-
"""Esperimento e3a59: PMI condizionata di terne di segni (memoria di due segni) dentro le parole e a cavallo dello
spazio (2+1 e 1+2); correlazione fra gli ambiti; Voynich, testi sensati, gibberish, generatori.

Preregistrazione: preregistrazioni/e3a59.md. Scrive risultati/e3a59_memoria_due.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

import numpy as np
from scipy.stats import spearmanr

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def cpmi(terne):
    """{(a,b,c): log P(c|a,b)/P(c|b)} dai conteggi delle terne di un ambito."""
    ab, bc, b_ = Counter(), Counter(), Counter()
    for (a, b, c), k in terne.items():
        ab[a, b] += k
        bc[b, c] += k
        b_[b] += k
    return {(a, b, c): math.log(k * b_[b] / (ab[a, b] * bc[b, c])) for (a, b, c), k in terne.items()}


def terne(righe):
    dentro, x21, x12 = Counter(), Counter(), Counter()
    for r in righe:
        for w in r:
            dentro.update(zip(w, w[1:], w[2:]))
        for u, v in zip(r, r[1:]):
            if len(u) >= 2:
                x21[u[-2], u[-1], v[0]] += 1
            if len(v) >= 2:
                x12[u[-1], v[0], v[1]] += 1
    return dentro, x21, x12


def rho2(righe):
    dentro, x21, x12 = terne(righe)
    pd = cpmi(dentro)
    out = []
    for x in (x21, x12):
        px = cpmi(x)
        celle = [k for k in pd if dentro[k] >= 5 and x.get(k, 0) >= 5]
        if len(celle) < 10:
            out.append((None, len(celle)))
        else:
            out.append((float(spearmanr([pd[k] for k in celle], [px[k] for k in celle]).correlation), len(celle)))
    return out


def main():
    rnd = random.Random(3159)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(rho2(prese))
    med = [statistics.median([s[i][0] for s in sub if s[i][0] is not None]) for i in (0, 1)]
    ris = OrderedDict([('Voynich', OrderedDict([('2+1', med[0]), ('1+2', med[1]), ('sottoinsiemi', sub)]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    altri = OrderedDict([('gibberish umano', gib)])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            altri[k] = e3a58.righe_prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v])
    altri['Timm e Schinner, seme 1'] = e3a58.righe_prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])
    for k, rr in altri.items():
        x = rho2(rr)
        ris[k] = OrderedDict([('2+1', x[0][0]), ('1+2', x[1][0]), ('celle', [x[0][1], x[1][1]])])
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        x = rho2(e3a58.righe_prime(t))
        sens[k.replace('.txt', '')] = OrderedDict([('2+1', x[0][0]), ('1+2', x[1][0]), ('celle', [x[0][1], x[1][1]])])
    lingue, esiti = OrderedDict(), []
    for amb, m in zip(('2+1', '1+2'), med):
        vals = sorted(s[amb] for s in sens.values() if s[amb] is not None)
        p90 = float(np.percentile(vals, 90))
        lingue[amb] = OrderedDict([('testi', len(vals)), ('minimo', vals[0]), ('mediana', float(np.median(vals))), ('p90', p90), ('massimo', vals[-1]),
                                   ('quota_sotto_il_voynich', sum(1 for v in vals if v < m) / len(vals)), ('voynich_sopra_il_massimo', m > vals[-1])])
        esiti.append(m > p90)
    esito = 'memoria uguale attraverso lo spazio' if all(esiti) else ('come le lingue' if not any(esiti) else 'in parte')
    out = OrderedDict([('altri', ris), ('lingue', lingue), ('testi_sensati', sens), ('esito', esito)])
    print(json.dumps(lingue, ensure_ascii=False), esito, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a59_memoria_due.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%.3f' % v
    md = ['# e3a59 — La catena ha la stessa memoria di due segni attraverso lo spazio?', '', 'Preregistrazione: `preregistrazioni/e3a59.md`.', '',
          '| ambito | testi sensati con valore | minimo | mediana | 90° percentile | massimo | Voynich | lingue sotto il Voynich |', '|---|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.3f | %.3f | %.3f | %.3f | %.0f%% |' % (amb, x['testi'], x['minimo'], x['mediana'], x['p90'], x['massimo'], m, 100 * x['quota_sotto_il_voynich'])
           for (amb, x), m in zip(lingue.items(), med)]
    md += ['', '| testo | ρ2 (2+1) | ρ2 (1+2) |', '|---|---|---|'] + ['| %s | %s | %s |' % (k, f(x['2+1']), f(x['1+2'])) for k, x in ris.items()]
    md += ['', 'Voynich, sottoinsiemi: ' + '; '.join('%s / %s (celle %d / %d)' % (f(s[0][0]), f(s[1][0]), s[0][1], s[1][1]) for s in sub)]
    md += ['', '| testo sensato | ρ2 (2+1) | ρ2 (1+2) | celle |', '|---|---|---|---|']
    md += ['| %s | %s | %s | %d / %d |' % (k, f(x['2+1']), f(x['1+2']), x['celle'][0], x['celle'][1]) for k, x in sens.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a59_memoria_due.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
