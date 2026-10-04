# -*- coding: utf-8 -*-
"""Esperimento e3a89: misure dell'e3a87 (ripresa per distanza, stessa riga contro a cavallo dell'a capo) sui testi
sensati, confrontate con il Voynich.

Preregistrazione: preregistrazioni/e3a89.md. Scrive risultati/e3a89_ripresa_lingue.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3a58_spazi_prevedibili as e3a58
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3a87_ripresa_distanza as e3a87

RISULTATI = os.path.join(QUI, '..', 'risultati')
RISCR = 2


def misure(pagine, rnd):
    per_par = [e3a87.conta_par(par) for pars in pagine for par in pars]
    vero = e3a87.somma(per_par)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    base = e3a87.somma([e3a87.conta_par(par) for _ in range(RISCR) for pars in e3a78.riscrivi(pagine, tab, rnd) for par in pars])
    qb, qv = e3a87.quote(base), e3a87.quote(vero)

    def media(tipo, dd):
        num = den = 0.0
        for d in dd:
            if (d, tipo) in qv and (d, tipo) in qb:
                n = vero[d, tipo][1]
                num += n * (qv[d, tipo] - qb[d, tipo])
                den += n
        return num / den if den else None
    diff = e3a87.confronto(vero, qb)[0]
    s_vic, s_lon = media('stessa riga', range(1, 5)), media('stessa riga', range(7, 11))
    c_vic, c_lon = media('a cavallo', range(3, 7)), media('a cavallo', range(10, 21))
    n_lon = sum(vero[d, 'stessa riga'][1] for d in range(7, 11))
    return OrderedDict([('differenza', diff), ('stessa_d1_4', s_vic), ('stessa_d7_10', s_lon), ('cavallo_d3_6', c_vic), ('cavallo_d10_20', c_lon),
                        ('calo', s_lon / s_vic if s_vic else None), ('piattezza', c_lon / c_vic if c_vic else None), ('coppie_stessa_d7_10', n_lon)])


def main():
    rnd = random.Random(3189)
    v = json.load(open(os.path.join(RISULTATI, 'e3a87_ripresa_distanza.json'), encoding='utf-8'))
    prof = v['profilo']

    def mv(tipo, dd):
        xs = [(prof[str(d)][tipo]['eccesso'], prof[str(d)][tipo]['coppie']) for d in dd if tipo in prof[str(d)] and prof[str(d)][tipo]['eccesso'] is not None]
        w = sum(n for _, n in xs)
        return sum(e * n for e, n in xs) / w
    voy = OrderedDict([('differenza', v['differenza']), ('calo', mv('stessa riga', range(7, 11)) / mv('stessa riga', range(1, 5))),
                       ('piattezza', mv('a cavallo', range(10, 21)) / mv('a cavallo', range(3, 7)))])
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe = [[tuple(w) for w in r] for r in e3a58.righe_prime(t) if r]
        pagine = [[righe[i:i + 25]] for i in range(0, len(righe), 25)]
        sens[k.replace('.txt', '')] = misure(pagine, rnd)
        print(k, json.dumps(sens[k.replace('.txt', '')]), flush=True)
    usati = {k: x for k, x in sens.items() if x['coppie_stessa_d7_10'] >= 500 and x['calo'] is not None}
    ris = OrderedDict()
    ok = []
    for m in ('differenza', 'calo', 'piattezza'):
        vals = sorted(x[m] for x in usati.values() if x[m] is not None)
        p10, p90 = float(np.percentile(vals, 10)), float(np.percentile(vals, 90))
        q = sum(1 for x in vals if x < voy[m]) / len(vals)
        ris[m] = OrderedDict([('voynich', voy[m]), ('lingue_p10', p10), ('lingue_mediana', float(np.median(vals))), ('lingue_p90', p90), ('quota_sotto_il_voynich', q)])
    sotto = ris['differenza']['voynich'] < ris['differenza']['lingue_p10'] and ris['calo']['voynich'] < ris['calo']['lingue_p10']
    dentro = all(ris[m]['lingue_p10'] <= ris[m]['voynich'] <= ris[m]['lingue_p90'] for m in ('differenza', 'calo'))
    esito = 'l\'a capo organizza la ripresa solo nel Voynich' if sotto else ('come le lingue' if dentro else 'in parte')
    out = OrderedDict([('lingue_usate', len(usati)), ('confronto', ris), ('esito', esito), ('testi_sensati', sens)])
    print(json.dumps(OrderedDict((k, v) for k, v in out.items() if k != 'testi_sensati'), ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a89_ripresa_lingue.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a89 — Nelle lingue l\'a capo cambia il modo in cui le parole si ripetono?', '', 'Preregistrazione: `preregistrazioni/e3a89.md`. Lingue usate (almeno 500 coppie "stessa riga" a d 7–10): %d.' % len(usati), '',
          '| misura | Voynich (e3a87) | lingue: 10° perc. | mediana | 90° perc. | lingue sotto il Voynich |', '|---|---|---|---|---|---|']
    md += ['| %s | %+.4f | %+.4f | %+.4f | %+.4f | %.0f%% |' % (m, x['voynich'], x['lingue_p10'], x['lingue_mediana'], x['lingue_p90'], 100 * x['quota_sotto_il_voynich']) for m, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a89_ripresa_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
