# -*- coding: utf-8 -*-
"""Esperimento e3b55: memoria delle scelte nella stessa riga e a cavallo dell'a capo (coppie a distanza 2-3 nel
paragrafo, senza parole simili), contro il nullo dell'e3b54 che tiene ferme le parole; pagine "solo testo" e altre.

Preregistrazione: preregistrazioni/e3b55.md. Scrive risultati/e3b55_solo_testo_oltre_parole.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000
VICINE = (2, 3)
GRUPPI = ('stessa riga', 'a cavallo')


def prepara(pagine, f):
    """pagine: [ [paragrafi di righe di parole] ]. Coppie vicine con etichetta 0 stessa riga, 1 a cavallo.
    Le coppie simili si tolgono confrontando le parole con la variante coperta (così l'esclusione non dipende dalla
    variante e il nullo non è distorto)."""
    val, grp, gruppi = [], [], {}
    I, J, G, Tp, Up = [], [], [], [], []
    for u, pars in enumerate(pagine):
        seq_par = []
        idx_unit = []
        for par in pars:
            s, riga, ids = [], [], []
            for nr, r in enumerate(par):
                for w in r:
                    x = f(w)
                    s.append(x[1] if x else w)
                    riga.append(nr)
                    if x is None:
                        ids.append(None)
                        continue
                    k = len(val)
                    val.append(x[0])
                    grp.append(gruppi.setdefault((u, x[1]), len(gruppi)))
                    ids.append(k)
                    idx_unit.append(k)
            seq_par.append((s, riga, ids))
        T = len(idx_unit)
        U = sum(val[k] for k in idx_unit)
        if T - 2 < 5:
            continue
        for s, riga, ids in seq_par:
            for i in range(len(s)):
                if ids[i] is None:
                    continue
                for d in VICINE:
                    j = i + d
                    if j >= len(s) or ids[j] is None:
                        continue
                    if s[i] == s[j] or e3a86.una_modifica(s[i], s[j]):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if riga[i] == riga[j] else 1)
                    Tp.append(T)
                    Up.append(U)
    return dict(val=np.array(val, dtype=float), grp=np.array(grp), I=np.array(I, dtype=int), J=np.array(J, dtype=int),
                G=np.array(G), T=np.array(Tp, dtype=float), U=np.array(Up, dtype=float))


def kappa(ss, g):
    o = sum(s[g][0] for s in ss)
    a = sum(s[g][1] for s in ss)
    n = sum(s[g][2] for s in ss)
    return (o - a) / (n - a) if n - a > 0 else None, int(n)


def prova(classi, rng):
    oss = [e3b54.somme(c, c['val']) for c in classi.values()]
    nul = {g: [] for g in (0, 1)}
    for _ in range(PERM):
        ss = [e3b54.somme(c, e3b54.rimescola(c, rng)) for c in classi.values()]
        for g in (0, 1):
            nul[g].append(kappa(ss, g)[0])
    out = OrderedDict()
    for g in (0, 1):
        k, n = kappa(oss, g)
        nn = [x for x in nul[g] if x is not None]
        mu = float(np.mean(nn))
        out[GRUPPI[g]] = OrderedDict([('coppie', n), ('K', k), ('nullo', mu), ('effetto', k - mu), ('p', float(np.mean([x >= k for x in nn]))),
                                      ('z', (k - mu) / float(np.std(nn)) if np.std(nn) > 0 else 0.0)])
    return out


def main():
    rng = np.random.default_rng(3255)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    gruppi = OrderedDict([('solo testo (T)', []), ('altre pagine', [])])
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp:
            gruppi['solo testo (T)' if sezione.get(pg) == 'T' else 'altre pagine'].append(pp)
    cl = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])
    ris = OrderedDict()
    for k, pagine in gruppi.items():
        ris[k] = prova(OrderedDict((c, prepara(pagine, f)) for c, f in cl.items()), rng)
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    t, a = ris['solo testo (T)']['a cavallo'], ris['altre pagine']['a cavallo']
    if t['p'] < 0.05 and a['p'] > 0.05:
        esito = 'regge oltre le parole'
    elif t['p'] > 0.20:
        esito = 'non regge'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b55_solo_testo_oltre_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b55 — La memoria che passa l\'a capo nelle pagine "solo testo", col nullo che tiene ferme le parole', '', 'Preregistrazione: `preregistrazioni/e3b55.md`. K normalizzato; coppie a distanza 2–3 senza parole simili.', '',
          '| pagine | coppie | coppie (n) | K osservato | K nullo | effetto | z | p |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        for g in GRUPPI:
            y = x[g]
            md.append('| %s | %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (k, g, y['coppie'], y['K'], y['nullo'], y['effetto'], y['z'], y['p']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b55_solo_testo_oltre_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
