# -*- coding: utf-8 -*-
"""Esperimento e3c07: le due misure del consumo con una divisione bilanciata dentro ogni strato.

- "lettere a parità di parole" (come l'e3b80): strato = distanza in parole (2, 3); dentro lo strato le coppie si ordinano
  per lettere in mezzo (spareggio casuale con seme) e la prima metà va a "poche lettere", la seconda a "molte";
- "parole a parità di lettere" (come l'e3c06): strato = numero esatto di lettere in mezzo; ordinamento per distanza in
  parole (2-5), prima metà "meno parole", seconda "più parole".

Così ogni strato pesa uguale nei due gruppi (nell'e3b80 e nell'e3c06 la divisione alla mediana, con i pareggi tolti, li
sbilanciava). Ognuna con e senza la prima e l'ultima parola della riga. ZL e IT, classi scelte a mano, metodo finale.

Preregistrazione: preregistrazioni/e3c07.md. Scrive risultati/e3c07_lettere_parole_bilanciate.json e .md.
"""
import json, os, random, sys
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
MODI = OrderedDict([('lettere a parità di parole', ((2, 3), 'd', 'l')), ('parole a parità di lettere', ((2, 3, 4, 5), 'l', 'd'))])


def senza_bordi(uu):
    """Ogni riga senza la prima e l'ultima parola: distanze e lettere in mezzo delle coppie restanti non cambiano."""
    return [[r[1:-1] for r in u if len(r) > 2] for u in uu]


def prepara(unita, strati, f, modo, seme):
    """Come e3b80.prepara, ma G = 0/1 dalla divisione bilanciata dentro ogni strato."""
    dist, chiave_strato, chiave_ordine = MODI[modo]
    rnd = random.Random(seme)
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
                for d in dist:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    coppie.append({'i': ids[i], 'j': ids[j], 'd': d, 'l': sum(len(s[k]) for k in range(i + 1, j))})
    per_strato = defaultdict(list)
    for c in coppie:
        per_strato[c[chiave_strato]].append(c)
    I, J, G = [], [], []
    for k in sorted(per_strato):
        cc = per_strato[k]
        cc = sorted(cc, key=lambda c: (c[chiave_ordine], rnd.random()))
        h = len(cc) // 2
        for g, parte in ((0, cc[:h]), (1, cc[len(cc) - h:])):
            for c in parte:
                I.append(c['i'])
                J.append(c['j'])
                G.append(g)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J, G = np.array(I, dtype=int), np.array(J, dtype=int), np.array(G, dtype=int)
    ok = (T[uni[I]] - 2 >= 5) if len(I) else np.array([], dtype=bool)
    return dict(val=np.array(val, dtype=float), grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok], G=G[ok] if len(G) else G,
                n_unita=len(unita), rimescolabili=0)


def misura(uu, ss, classi, modo, rng, seme):
    cc = OrderedDict((k, prepara(uu, ss, f, modo, seme + n)) for n, (k, f) in enumerate(classi.items()))
    pr = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
    return OrderedDict([('coppie_gruppo_0', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3307)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        ris[q] = OrderedDict()
        for bordi, u in (('con i bordi', uu), ('senza i bordi', senza_bordi(uu))):
            for modo in MODI:
                ris[q]['%s, %s' % (modo, bordi)] = misura(u, ss, e3b62.CV, modo, rng, 3307)
                print(q, modo, bordi, json.dumps(ris[q]['%s, %s' % (modo, bordi)], default=float), flush=True)
    l = [ris[q]['lettere a parità di parole, senza i bordi'] for q in ('ZL', 'IT')]
    esito_l = 'il consumo con le lettere regge' if l[0]['IC95'][0] > 0 and l[1]['IC95'][0] > 0 else (
        'il consumo con le lettere non regge' if all(x['IC95'][0] <= 0 for x in l) else 'consumo con le lettere incerto')
    p = [ris[q]['parole a parità di lettere, con i bordi'] for q in ('ZL', 'IT')]
    if all(x['IC95'][0] <= 0 <= x['IC95'][1] for x in p):
        esito_p = "l'effetto negativo dell'e3c06 era un errore di metodo"
    elif all(x['IC95'][1] < 0 for x in p):
        esito_p = "l'effetto negativo dell'e3c06 resta"
    else:
        esito_p = 'parole incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito_lettere', esito_l), ('esito_parole', esito_p)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c07_lettere_parole_bilanciate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c07 — Consumo con le lettere e con le parole, divisione bilanciata, con e senza i bordi della riga', '',
          'Preregistrazione: `preregistrazioni/e3c07.md`. Prima: lettere a parità di parole +0,066 (e3b80); parole a parità di lettere −0,057 ZL, −0,060 IT (e3c06).', '',
          '| trascrizione | misura | coppie per gruppo | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|']
    for q, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (q, k, y['coppie_gruppo_0'], y['M'], y['nullo'], y['effetto'], y['IC95'][0], y['IC95'][1]))
    md += ['', "Esito principale (lettere, divisione bilanciata, senza i bordi): **%s**. Controllo dell'e3c06 (parole, con i bordi, descrittivo): **%s**." % (esito_l, esito_p)]
    open(os.path.join(RISULTATI, 'e3c07_lettere_parole_bilanciate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
