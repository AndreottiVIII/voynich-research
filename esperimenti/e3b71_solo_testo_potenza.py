# -*- coding: utf-8 -*-
"""Esperimento e3b71: D dell'e3b66 (memoria a cavallo dell'a capo contro le righe vicine) nelle pagine di solo testo e
nelle normali, ZL e IT, e contrasto con bootstrap per pagina.

Preregistrazione: preregistrazioni/e3b71.md. Scrive risultati/e3b71_solo_testo_potenza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b65_a_capo_controllo as e3b65
import e3b66_a_capo_potenza as e3b66

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def gruppo(righe, quote):
    casi = e3b65.casi_capo(righe)
    sm = {k: e3b66.somme(casi, quote, k) for k in ('sotto', 'sopra', 'due', 'dentro')}
    return sm, list(casi)


def dd(sm, pp):
    ks = {k: e3b64.kappa([sm[k][pg] for pg in pp])[0] for k in ('sotto', 'sopra', 'due')}
    if None in ks.values():
        return None
    return ks['sotto'] - (ks['sopra'] + ks['due']) / 2


def main():
    rnd = random.Random(3271)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(q)]
        quote = e3b64.quote_pagine(righe, e3b62.CV)
        smT, pT = gruppo([x for x in righe if sezione.get(x[0]) == 'T'], quote)
        smN, pN = gruppo([x for x in righe if sezione.get(x[0]) != 'T'], quote)
        dT, dN = dd(smT, pT), dd(smN, pN)
        boot = []
        for _ in range(BOOT):
            a = dd(smT, [rnd.choice(pT) for _ in pT])
            b = dd(smN, [rnd.choice(pN) for _ in pN])
            if a is not None and b is not None:
                boot.append(a - b)
        boot.sort()
        bT = sorted(x for x in (dd(smT, [rnd.choice(pT) for _ in pT]) for _ in range(BOOT)) if x is not None)
        ris[q] = OrderedDict([('pagine_T', len(pT)), ('D_T', dT), ('IC95_T', [bT[int(0.025 * len(bT))], bT[int(0.975 * len(bT)) - 1]]),
                              ('coppie_T', int(sum(smT['sotto'][pg][2] for pg in pT))), ('pagine_normali', len(pN)), ('D_normali', dN),
                              ('contrasto', dT - dN), ('IC95_contrasto', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])
        print(q, json.dumps(ris[q]), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95_contrasto'][0] > 0 and it['contrasto'] > 0:
        esito = 'nelle pagine di solo testo la memoria passa di più'
    elif z['IC95_contrasto'][1] < 0:
        esito = 'meno che altrove'
    else:
        esito = 'non diverso dalle altre pagine'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b71_solo_testo_potenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b71 — Nelle pagine di solo testo la memoria passa l\'a capo più che altrove?', '', 'Preregistrazione: `preregistrazioni/e3b71.md`. Metodo dell\'e3b66.', '',
          '| trascrizione | D solo testo (IC 95%, coppie) | D pagine normali | contrasto (IC 95%) |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %+.4f (%+.4f – %+.4f, %d) | %+.4f | %+.4f (%+.4f – %+.4f) |' % (q, x['D_T'], x['IC95_T'][0], x['IC95_T'][1], x['coppie_T'], x['D_normali'], x['contrasto'], x['IC95_contrasto'][0], x['IC95_contrasto'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b71_solo_testo_potenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
