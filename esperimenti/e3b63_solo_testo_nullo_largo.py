# -*- coding: utf-8 -*-
"""Esperimento e3b63: e3b55 (memoria nella stessa riga e a cavallo dell'a capo, pagine "solo testo" e altre) con il
nullo largo dell'e3b62 (rimescolamento nello strato, atteso della pagina ricalcolato).

Preregistrazione: preregistrazioni/e3b63.md. Scrive risultati/e3b63_solo_testo_nullo_largo.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000
GRUPPI = ('stessa riga', 'a cavallo')


def prepara(pagine, strati, f):
    val, grp, uni, gruppi = [], [], [], {}
    I, J, G = [], [], []
    for u, pars in enumerate(pagine):
        for par in pars:
            ids, cop, riga = [], [], []
            for nr, r in enumerate(par):
                for w in r:
                    x = f(w)
                    riga.append(nr)
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
                for d in (2, 3):
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if riga[i] == riga[j] else 1)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(pagine)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = T[uni[I]] - 2 >= 5
    return dict(val=np.array(val, dtype=float), grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok], G=np.array(G)[ok], n_unita=len(pagine))


def kappa(ss, g):
    o = sum(s[g][0] for s in ss)
    a = sum(s[g][1] for s in ss)
    n = sum(s[g][2] for s in ss)
    return (o - a) / (n - a) if n - a > 0 else None, int(n)


def prova(classi, rng):
    oss = [e3b62.somme(c, c['val']) for c in classi.values()]
    nul = {g: [] for g in (0, 1)}
    for _ in range(PERM):
        ss = [e3b62.somme(c, e3b54.rimescola(c, rng)) for c in classi.values()]
        for g in (0, 1):
            nul[g].append(kappa(ss, g)[0])
    out = OrderedDict()
    for g in (0, 1):
        k, n = kappa(oss, g)
        nn = [x for x in nul[g] if x is not None]
        mu, sd = float(np.mean(nn)), float(np.std(nn))
        out[GRUPPI[g]] = OrderedDict([('coppie', n), ('K', k), ('nullo', mu), ('effetto', k - mu), ('z', (k - mu) / sd if sd > 0 else 0.0),
                                      ('p', float(np.mean([x >= k for x in nn])))])
    return out


def main():
    rng = np.random.default_rng(3263)
    sezione, mano = {}, {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
        mano.setdefault(r.pagina, r.mano)
    gruppi = OrderedDict([('solo testo (T)', ([], [])), ('altre pagine', ([], []))])
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if not pp:
            continue
        if sezione.get(pg) == 'T':
            gruppi['solo testo (T)'][0].append(pp)
            gruppi['solo testo (T)'][1].append('T')
        else:
            gruppi['altre pagine'][0].append(pp)
            gruppi['altre pagine'][1].append(mano.get(pg) or '?')
    ris = OrderedDict()
    for k, (pagine, strati) in gruppi.items():
        ris[k] = prova(OrderedDict((c, prepara(pagine, strati, f)) for c, f in e3b62.CV.items()), rng)
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    t, a = ris['solo testo (T)']['a cavallo'], ris['altre pagine']['a cavallo']
    esito = 'regge oltre le parole' if t['p'] < 0.05 and a['p'] > 0.05 else ('non regge' if t['p'] > 0.20 else 'incerto')
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b63_solo_testo_nullo_largo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b63 — Pagine "solo testo": la memoria che passa l\'a capo, col nullo largo', '', 'Preregistrazione: `preregistrazioni/e3b63.md`.', '',
          '| pagine | coppie | n | K osservato | K nullo | effetto | z | p |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        for g in GRUPPI:
            y = x[g]
            md.append('| %s | %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (k, g, y['coppie'], y['K'], y['nullo'], y['effetto'], y['z'], y['p']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b63_solo_testo_nullo_largo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
