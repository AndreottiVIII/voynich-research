# -*- coding: utf-8 -*-
"""Esperimento e3b80: memoria delle scelte con poche o molte lettere in mezzo, a parità di distanza in parole (2 e 3),
con il metodo finale (nullo largo dell'e3b62, intervalli per pagina dell'e3b70). ZL e IT.

Preregistrazione: preregistrazioni/e3b80.md. Scrive risultati/e3b80_memoria_lettere.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict

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
DIST = (2, 3)


def prepara(unita, strati, f):
    """Come e3b62.prepara, ma solo coppie a distanza 2-3 con G = 0 (poche lettere in mezzo) o 1 (molte)."""
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
    med = {d: statistics.median([c[3] for c in coppie if c[2] == d]) for d in DIST}
    I, J, G = [], [], []
    for a, b, d, l in coppie:
        if l == med[d]:
            continue
        I.append(a)
        J.append(b)
        G.append(0 if l < med[d] else 1)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = T[uni[I]] - 2 >= 5
    return dict(val=np.array(val, dtype=float), grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok], G=np.array(G)[ok],
                n_unita=len(unita), rimescolabili=0, mediane=med)


def main():
    rng = np.random.default_rng(3280)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        classi = OrderedDict((k, prepara(uu, ss, f)) for k, f in e3b62.CV.items())
        pr = e3b62.prova(classi, rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(c) for c in classi.values()], pr['nullo'], rng)
        ris[q] = OrderedDict([('coppie_poche', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95']),
                              ('mediane', {c: classi[c]['mediane'] for c in classi})])
        print(q, json.dumps(ris[q], ensure_ascii=False, default=float), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95'][0] > 0 and it['effetto'] > 0:
        esito = 'si consuma con le lettere'
    elif z['IC95'][1] < 0:
        esito = 'al contrario'
    else:
        esito = 'non dimostrato'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b80_memoria_lettere.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3b80 — La memoria delle scelte si consuma con le lettere scritte? (metodo finale)', '', 'Preregistrazione: `preregistrazioni/e3b80.md`. M = K(poche lettere in mezzo) − K(molte), a distanza 2–3 parole.', '',
          '| trascrizione | coppie con poche lettere | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (q, x['coppie_poche'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b80_memoria_lettere.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
