# -*- coding: utf-8 -*-
"""Esperimento e3b76: e3b75 (и/ꙇ a inizio parola nel Codex Marianus) separando le parole di almeno 2 segni dalla
congiunzione di un segno. Per la congiunzione (sempre la stessa parola) le coppie simili non si tolgono.

Preregistrazione: preregistrazioni/e3b76.md. Scrive risultati/e3b76_marianus_senza_congiunzione.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b75_marianus as e3b75

RISULTATI = os.path.join(QUI, '..', 'risultati')


def lunghe(w):
    return e3b75.i_iniziale(w) if len(w) >= 2 else None


def brevi(w):
    return e3b75.i_iniziale(w) if len(w) == 1 else None


def prepara(unita, strati, f, escludi):
    """Come e3b62.prepara; con escludi=False le coppie con parole coperte uguali o a una modifica non si tolgono."""
    val, grp, uni, gruppi = [], [], [], {}
    I, J, G = [], [], []
    for u, seqs in enumerate(unita):
        for s in seqs:
            ids, cop = [], []
            for w in s:
                x = f(w)
                if x is None:
                    ids.append(None)
                    cop.append(None)
                    continue
                ids.append(len(val))
                cop.append(x[1])
                val.append(x[0])
                grp.append(gruppi.setdefault((strati[u], x[1]), len(gruppi)))
                uni.append(u)
            for i in range(len(ids)):
                if ids[i] is None:
                    continue
                for d in e3b54.VICINE + e3b54.LONTANE:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if escludi and (cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j])):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if d in e3b54.VICINE else 1)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = T[uni[I]] - 2 >= 5
    v = np.array(val, dtype=float)
    g = np.array(grp, dtype=int)
    gsize = np.bincount(g)
    s1 = np.bincount(g, weights=v)
    misti = int(gsize[(gsize >= 2) & (s1 > 0) & (s1 < gsize)].sum())
    return dict(val=v, grp=g, uni=uni, T=T, I=I[ok], J=J[ok], G=np.array(G)[ok], n_unita=len(unita), rimescolabili=misti)


def main():
    rng = np.random.default_rng(3276)
    righe = [r for r in e381.testi()[e3b75.CHIAVE] if r]
    uu = [[b] for b in e3b51.blocchi(righe)]
    ris = OrderedDict()
    for nome, f, escl in (('parole di almeno 2 segni', lunghe, True), ('congiunzione (un segno)', brevi, False)):
        c = prepara(uu, ['Marianus'] * len(uu), f, escl)
        pr = e3b62.prova(OrderedDict([('x', c)]), rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
        ris[nome] = OrderedDict([('occorrenze', int(len(c['val']))), ('quota_ꙇ', float(c['val'].mean())), ('coppie_vicine', pr['coppie_vicine']),
                                 ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    a, b = ris['parole di almeno 2 segni'], ris['congiunzione (un segno)']
    if a['IC95'][1] < 0:
        esito = 'alternanza anche nelle altre parole'
    elif a['IC95'][0] <= 0 <= a['IC95'][1] and b['IC95'][1] < 0:
        esito = "l'alternanza viene dalla congiunzione"
    else:
        esito = 'incerto'
    out = OrderedDict([('varianti', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b76_marianus_senza_congiunzione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b76 — L\'alternanza и/ꙇ del Codex Marianus viene dalla congiunzione?', '', 'Preregistrazione: `preregistrazioni/e3b76.md`. e3b75 (tutte): −0,090 (IC −0,156 – −0,031).', '',
          '| parole | occorrenze | quota ꙇ | coppie vicine | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.3f | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (k, x['occorrenze'], x['quota_ꙇ'], x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b76_marianus_senza_congiunzione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
