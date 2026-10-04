# -*- coding: utf-8 -*-
"""Esperimento e3b61: e3b49 (legame delle scelte con la parola oltre i segni vicini) separatamente per lingua A e B,
ciascuna contro la propria catena di ordine 2.

Preregistrazione: preregistrazioni/e3b61.md. Scrive risultati/e3b61_scelte_parola_ab.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3b49_scelte_parola as e3b49

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rnd = random.Random(3261)
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    per = OrderedDict([('A', []), ('B', [])])
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp and lingua.get(pg) in per:
            per[lingua[pg]].append(pp)
    ris = OrderedDict()
    for L, pagine in per.items():
        v = e3b49.misura(pagine)
        tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
        cat = [e3b49.misura(e3a78.riscrivi(pagine, tab, rnd)) for _ in range(5)]
        x = OrderedDict([('pagine', len(pagine))])
        for c in e3b49.CLASSI:
            cs = [k[c][0] for k in cat if k[c][0] is not None]
            x[c] = OrderedDict([('risparmio', v[c][0]), ('occorrenze', v[c][1]), ('catena_media', sum(cs) / len(cs) if cs else None),
                                ('catena_max', max(cs) if cs else None), ('scarto', v[c][0] - max(cs) if cs and v[c][0] is not None else None)])
        ris[L] = x
        print(L, json.dumps(x), flush=True)
    a_piu = sum(1 for c in e3b49.CLASSI if ris['A'][c]['scarto'] is not None and ris['B'][c]['scarto'] is not None and ris['A'][c]['scarto'] - ris['B'][c]['scarto'] >= 0.005)
    b_piu = sum(1 for c in e3b49.CLASSI if ris['A'][c]['scarto'] is not None and ris['B'][c]['scarto'] is not None and ris['B'][c]['scarto'] - ris['A'][c]['scarto'] >= 0.005)
    esito = 'in A le scelte sono più legate alla parola' if a_piu >= 3 else ('in B più che in A' if b_piu >= 3 else 'nessuna differenza chiara')
    out = OrderedDict([('lingue', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b61_scelte_parola_ab.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b61 — In lingua A le scelte di grafia sono più legate alla parola che in lingua B?', '', 'Preregistrazione: `preregistrazioni/e3b61.md`. Risparmio in bit fuori campione; scarto = risparmio − massimo di 5 catene della stessa lingua.', '',
          '| classe | A: occorrenze | A: risparmio | A: catena max | A: scarto | B: occorrenze | B: risparmio | B: catena max | B: scarto |', '|---|---|---|---|---|---|---|---|---|']
    g = lambda x: 'n.d.' if x is None else '%+.4f' % x
    for c in e3b49.CLASSI:
        a, b = ris['A'][c], ris['B'][c]
        md.append('| %s | %d | %s | %s | %s | %d | %s | %s | %s |' % (c, a['occorrenze'], g(a['risparmio']), g(a['catena_max']), g(a['scarto']), b['occorrenze'], g(b['risparmio']), g(b['catena_max']), g(b['scarto'])))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b61_scelte_parola_ab.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
