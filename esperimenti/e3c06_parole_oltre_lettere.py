# -*- coding: utf-8 -*-
"""Esperimento e3c06: a parità di lettere scritte in mezzo, la memoria delle scelte cala anche con il numero di parole?
Coppie nella stessa riga a distanza 2-5 parole; per ogni numero esatto di lettere in mezzo, "poche parole" (distanza
sotto la mediana per quel numero di lettere) contro "molte parole" (sopra). Metodo finale (nullo largo e3b62, intervalli
per pagina e3b70), classi scelte a mano (e3b62.CV). ZL e IT.

Preregistrazione: preregistrazioni/e3c06.md. Scrive risultati/e3c06_parole_oltre_lettere.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70

RISULTATI = os.path.join(QUI, '..', 'risultati')
DIST = (2, 3, 4, 5)
SOGLIA = 0.033


def prepara(unita, strati, f):
    """Come e3b80.prepara, ma G = 0 (meno parole) o 1 (più parole) a parità di lettere in mezzo."""
    val, grp, uni, gruppi = [], [], [], {}
    coppie = []
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
                for d in DIST:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    coppie.append((ids[i], ids[j], d, sum(len(s[k]) for k in range(i + 1, j))))
    per_l = defaultdict(list)
    for c in coppie:
        per_l[c[3]].append(c[2])
    med = {l: statistics.median(ds) for l, ds in per_l.items()}
    I, J, G = [], [], []
    for a, b, d, l in coppie:
        if d == med[l]:
            continue
        I.append(a)
        J.append(b)
        G.append(0 if d < med[l] else 1)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = (T[uni[I]] - 2 >= 5) if len(I) else np.array([], dtype=bool)
    G = np.array(G)
    return dict(val=np.array(val, dtype=float), grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok], G=G[ok] if len(G) else G,
                n_unita=len(unita), rimescolabili=0)


def misura(uu, ss, classi, rng):
    cc = OrderedDict((k, prepara(uu, ss, f)) for k, f in classi.items())
    pr = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
    return OrderedDict([('coppie_poche_parole', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3306)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        ris[q] = misura(uu, ss, e3b62.CV, rng)
        print(q, json.dumps(ris[q], ensure_ascii=False, default=float), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95'][0] > 0 and it['IC95'][0] > 0:
        esito = 'conta anche il numero di parole'
    elif all(x['IC95'][0] <= 0 <= x['IC95'][1] and abs(x['effetto']) < SOGLIA for x in (z, it)):
        esito = 'la memoria si consuma solo con le lettere'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c06_parole_oltre_lettere.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c06 — A parità di lettere in mezzo, la memoria cala anche con il numero di parole?', '',
          'Preregistrazione: `preregistrazioni/e3c06.md`. M = K(meno parole) − K(più parole) a parità di lettere in mezzo, distanze 2–5. Riferimento: lettere a parità di parole (e3b80) +0,066.', '',
          '| trascrizione | coppie con meno parole | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (q, x['coppie_poche_parole'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c06_parole_oltre_lettere.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
