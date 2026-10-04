# -*- coding: utf-8 -*-
"""Esperimento e3b38: e3b10 (memoria delle scelte nella stessa riga e a cavallo dell'a capo) nelle pagine "solo testo"
(sezione T) e nelle altre.

Preregistrazione: preregistrazioni/e3b38.md. Scrive risultati/e3b38_solo_testo_a_capo.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b10_scelte_a_capo as e3b10

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def analizza(pagine, rnd):
    cc = []
    for pid, pars in enumerate(pagine):
        cc += e3b10.coppie_pagina(pars, pid)
    e = e3b10.eccessi(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    bc = []
    for _ in range(BOOT):
        eb = e3b10.eccessi([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        if 'a cavallo' in eb:
            bc.append(eb['a cavallo'][0])
    bc.sort()
    ic = [bc[int(0.025 * len(bc))], bc[int(0.975 * len(bc)) - 1]]
    return OrderedDict([('pagine', len(pagine)), ('stessa_riga', e['stessa riga'][0]), ('coppie_stessa', e['stessa riga'][1]),
                        ('a_cavallo', e['a cavallo'][0]), ('coppie_a_cavallo', e['a cavallo'][1]), ('IC95_a_cavallo', ic)])


def main():
    rnd = random.Random(3238)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    gruppi = {'solo testo (T)': [], 'altre pagine': []}
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        gruppi['solo testo (T)' if sezione.get(pg) == 'T' else 'altre pagine'].append(pp)
    ris = OrderedDict((k, analizza(v, rnd)) for k, v in gruppi.items())
    t = ris['solo testo (T)']
    if t['coppie_a_cavallo'] < 150:
        esito = 'dati insufficienti'
    elif t['IC95_a_cavallo'][0] > 0 and t['a_cavallo'] >= 0.5 * t['stessa_riga']:
        esito = "nelle pagine solo testo la memoria passa l'a capo"
    elif t['IC95_a_cavallo'][0] <= 0 <= t['IC95_a_cavallo'][1]:
        esito = "anche lì l'a capo azzera la memoria"
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b38_solo_testo_a_capo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b38 — Nelle pagine "solo testo" la memoria delle scelte attraversa l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3b38.md`.', '',
          '| pagine | quante | stessa riga: eccesso (coppie) | a cavallo dell\'a capo: eccesso (coppie) | IC 95% a cavallo |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f – %+.4f |' % (k, x['pagine'], x['stessa_riga'], x['coppie_stessa'], x['a_cavallo'], x['coppie_a_cavallo'], x['IC95_a_cavallo'][0], x['IC95_a_cavallo'][1]) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b38_solo_testo_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
