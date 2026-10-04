# -*- coding: utf-8 -*-
"""Esperimento e3a88: e3a87 (ripresa per distanza, stessa riga contro a cavallo dell'a capo) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3a88.md. Scrive risultati/e3a88_ripresa_distanza_it.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3a80_catena_takahashi as e3a80
import e3a87_ripresa_distanza as e3a87

RISULTATI = os.path.join(QUI, '..', 'risultati')


def media(prof, tipo, dd):
    xs = [(prof[d][tipo]['eccesso'], prof[d][tipo]['coppie']) for d in dd if d in prof and tipo in prof[d] and prof[d][tipo]['eccesso'] is not None]
    w = sum(n for _, n in xs)
    return sum(e * n for e, n in xs) / w if w else None


def main():
    rnd = random.Random(3188)
    pagine = e3a80.pagine_it()
    per_par = [e3a87.conta_par(par) for pars in pagine for par in pars]
    vero = e3a87.somma(per_par)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    base = e3a87.somma([e3a87.conta_par(par) for _ in range(e3a78.RISCRITTURE) for pars in e3a78.riscrivi(pagine, tab, rnd) for par in pars])
    qb, qv = e3a87.quote(base), e3a87.quote(vero)
    diff, e = e3a87.confronto(vero, qb)
    boot = sorted(e3a87.confronto(e3a87.somma([per_par[rnd.randrange(len(per_par))] for _ in per_par]), qb)[0] for _ in range(e3a87.BOOT))
    ic = [boot[int(0.025 * e3a87.BOOT)], boot[int(0.975 * e3a87.BOOT) - 1]]
    prof = OrderedDict()
    for d in range(1, e3a87.DMAX + 1):
        prof[d] = OrderedDict((t, OrderedDict([('coppie', vero[d, t][1]), ('eccesso', qv[d, t] - qb[d, t] if (d, t) in qv and (d, t) in qb else None)]))
                              for t in ('stessa riga', 'a cavallo') if vero[d, t][1])
    s_vic, s_lon = media(prof, 'stessa riga', range(1, 5)), media(prof, 'stessa riga', range(7, 11))
    c_vic, c_lon = media(prof, 'a cavallo', range(3, 7)), media(prof, 'a cavallo', range(10, 21))
    cala = s_lon < 0.5 * s_vic
    piatta = c_lon >= 0.5 * c_vic
    sotto = ic[1] < 0
    esito = 'si ritrova' if sotto and cala and piatta else ('in parte' if (sotto or (cala and piatta)) else 'non si ritrova')
    out = OrderedDict([('eccesso_medio_3_8', e), ('differenza', diff), ('IC95', ic), ('stessa_riga_d1_4', s_vic), ('stessa_riga_d7_10', s_lon),
                       ('a_cavallo_d3_6', c_vic), ('a_cavallo_d10_20', c_lon), ('cala_nella_riga', cala), ('piatta_dalla_riga_sopra', piatta), ('esito', esito), ('profilo', prof)])
    print(json.dumps(OrderedDict((k, v) for k, v in out.items() if k != 'profilo'), ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a88_ripresa_distanza_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a88 — Le due riprese dell\'e3a87 si ritrovano con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3a88.md`.', '',
          'Differenza (stessa riga − a cavallo, d 3–8): **%+.4f**, IC 95%% %+.4f – %+.4f.' % (diff, ic[0], ic[1]),
          'Stessa riga: d 1–4 %+.4f, d 7–10 %+.4f (cala: %s). A cavallo: d 3–6 %+.4f, d 10–20 %+.4f (piatta: %s).' % (s_vic, s_lon, 'sì' if cala else 'no', c_vic, c_lon, 'sì' if piatta else 'no'),
          '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a88_ripresa_distanza_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
