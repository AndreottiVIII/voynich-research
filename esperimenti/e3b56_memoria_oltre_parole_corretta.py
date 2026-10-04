# -*- coding: utf-8 -*-
"""Esperimento e3b56: e3b54 con l'esclusione delle coppie simili decisa sulle parole con la variante coperta; Voynich ZL
e IT, varianti naturali.

Preregistrazione: preregistrazioni/e3b56.md. Scrive risultati/e3b56_memoria_oltre_parole_corretta.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def prepara(unita, f):
    """Come e3b54.prepara, ma le coppie simili si decidono sulle parole con la variante coperta."""
    val, grp, gruppi = [], [], {}
    I, J, G, Tp, Up = [], [], [], [], []
    for u, seqs in enumerate(unita):
        idx_unit, segn = [], []
        for s in seqs:
            ids, cop = [], []
            for w in s:
                x = f(w)
                if x is None:
                    ids.append(None)
                    cop.append(None)
                    continue
                k = len(val)
                val.append(x[0])
                grp.append(gruppi.setdefault((u, x[1]), len(gruppi)))
                ids.append(k)
                cop.append(x[1])
                idx_unit.append(k)
            segn.append((ids, cop))
        T = len(idx_unit)
        U = sum(val[k] for k in idx_unit)
        if T - 2 < 5:
            continue
        for ids, cop in segn:
            for i in range(len(ids)):
                if ids[i] is None:
                    continue
                for d in e3b54.VICINE + e3b54.LONTANE:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if d in e3b54.VICINE else 1)
                    Tp.append(T)
                    Up.append(U)
    return dict(val=np.array(val, dtype=float), grp=np.array(grp), I=np.array(I, dtype=int), J=np.array(J, dtype=int),
                G=np.array(G), T=np.array(Tp, dtype=float), U=np.array(Up, dtype=float))


def righe_pagine(pagine_str):
    out = []
    for pars in pagine_str:
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            out.append(rr)
    return out


def main():
    rng = np.random.default_rng(3256)
    cv = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])
    ris = OrderedDict()
    for nome, pagine in (('Voynich ZL', righe_pagine(e341.pagine().values())), ('Voynich IT', righe_pagine(e3b45.pagine_it().values()))):
        ris[nome] = e3b54.prova(OrderedDict((k, prepara(pagine, f)) for k, f in cv.items()), rng)
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    tt = e381.testi()
    cn = OrderedDict()
    for nome, chiave in e3b54.STORICI.items():
        righe = [r for r in tt[chiave] if r]
        unita = [[b] for b in e3b51.blocchi(righe)]
        cn['%s, i/y' % nome] = prepara(unita, e3b54.classe_iy(righe))
        if nome == 'Hatton Gospels':
            cn['Hatton Gospels, þ/ð a inizio parola'] = prepara(unita, e3b54.v_th_ini)
            cn['Hatton Gospels, þ/ð dentro la parola'] = prepara(unita, e3b54.v_th_int)
    ris['naturali'] = e3b54.prova(cn, rng)
    print('naturali', json.dumps(ris['naturali'], ensure_ascii=False), flush=True)
    es = OrderedDict()
    for nome in ('Voynich ZL', 'Voynich IT'):
        es[nome] = e3b54.esito(ris[nome]['insieme']['p'], 'memoria oltre le preferenze delle parole', 'non oltre')
    es['naturali'] = e3b54.esito(ris['naturali']['insieme']['p'], 'memoria anche negli scribi veri', 'non si vede negli scribi veri')
    out = OrderedDict([('gruppi', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b56_memoria_oltre_parole_corretta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b56 — Memoria corta oltre le preferenze delle parole (esclusione corretta)', '', 'Preregistrazione: `preregistrazioni/e3b56.md`. M = K(vicine) − K(lontane); coppie simili decise sulle parole con la variante coperta.', '',
          '| gruppo, classe | coppie vicine | M osservata | M nullo | effetto | z | p |', '|---|---|---|---|---|---|---|']
    for g, r in ris.items():
        for k, x in r.items():
            if x['M'] is None:
                md.append('| %s, %s | %d | n.d. | | | | |' % (g, k, x['coppie_vicine']))
                continue
            md.append('| %s, %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (g, k, x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['z'], x['p']))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b56_memoria_oltre_parole_corretta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
