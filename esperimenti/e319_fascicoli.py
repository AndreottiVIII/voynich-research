# -*- coding: utf-8 -*-
"""Esperimenti 319 e 323. (e319) dentro un fascicolo, lo stato dei bifogli cambia in ordine dal piu' esterno al piu'
interno? (e323) in che cosa differiscono le facce dei fogli con recto e verso diversi, e se una faccia sola si
allontana dal suo bifoglio.

Preregistrazione: preregistrazioni/e319.md. Scrive risultati/e319_fascicoli.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e308_libro_fisico as e308
import e314_bifogli as e314

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
FOGLI_E318 = ['f88', 'f52', 'f2', 'f83', 'f82']


def e319(voy, P, s, testa, rnd):
    from scipy.stats import spearmanr
    per = defaultdict(lambda: defaultdict(list))   # fascicolo -> profondita' -> pagine
    for i, p in enumerate(voy.pagine):
        v = testa.get(p['nome'])
        if v and v['Q'] and v['B'] and v['B'].isdigit():
            per[v['Q']][int(v['B'])].append(i)
    fasc = OrderedDict()
    for q, d in per.items():
        if len(d) >= 3:
            prof = sorted(d)
            stati = np.array([P[d[b]].mean(0) for b in prof])
            asse = np.array([s[d[b]].mean() for b in prof])
            fasc[q] = (prof, stati, asse - asse.mean())
    if not fasc:
        return OrderedDict([('fascicoli', 0)])

    def misure(perm):
        rho_num, xs, ys, adj, alt = 0, [], [], [], []
        for q, (prof, stati, asse) in fasc.items():
            pr = [prof[k] for k in perm[q]]
            xs += pr
            ys += list(asse)
            C = np.corrcoef(stati)
            for a in range(len(pr)):
                for b in range(a + 1, len(pr)):
                    (adj if abs(pr[a] - pr[b]) == 1 else alt).append(C[a, b])
        rho = spearmanr(xs, ys).correlation
        return rho, (np.nanmean(adj) - np.nanmean(alt)) if adj and alt else 0.0
    ident = {q: list(range(len(v[0]))) for q, v in fasc.items()}
    vero = misure(ident)
    nulli = []
    for _ in range(PERM):
        pm = {}
        for q, v in fasc.items():
            x = list(range(len(v[0])))
            rnd.shuffle(x)
            pm[q] = x
        nulli.append(misure(pm))
    za = (vero[0] - statistics.mean(n[0] for n in nulli)) / statistics.pstdev(n[0] for n in nulli)
    zb = (vero[1] - statistics.mean(n[1] for n in nulli)) / statistics.pstdev(n[1] for n in nulli)
    if zb > 3 or abs(za) > 3:
        esito = 'scritti in ordine di annidamento'
    elif abs(za) < 2 and abs(zb) < 2:
        esito = 'nessun ordine di annidamento'
    else:
        esito = 'incerto'
    direzione = 'il punteggio sale verso l\'interno (più -edy dentro)' if vero[0] > 0 else 'il punteggio scende verso l\'interno (più -aiin dentro)'
    return OrderedDict([('fascicoli', len(fasc)), ('bifogli', sum(len(v[0]) for v in fasc.values())), ('rho_profondita_asse', vero[0]), ('z_a', za),
                        ('direzione', direzione), ('vicini_meno_altri', vero[1]), ('z_b', zb), ('esito', esito)])


def e323(voy, P, nomi, s, testa, rnd):
    from scipy.stats import spearmanr
    import e307_identita_pagine as e307
    nomi_p = [p['nome'] for p in voy.pagine]
    idx = {p: i for i, p in enumerate(nomi_p)}
    C = np.corrcoef(P)
    fogli = defaultdict(lambda: {'r': [], 'v': []})
    for p in nomi_p:
        v = testa.get(p)
        if v and v['Q'] and v['lato'] in ('r', 'v'):
            fogli[(v['Q'], v['F'])][v['lato']].append(p)
    per_bif = defaultdict(list)
    for p in nomi_p:
        v = testa.get(p)
        if v and v['Q']:
            per_bif[(v['Q'], v['B'])].append(p)

    def compagne(p):
        v = testa[p]
        co = [x for x in per_bif[(v['Q'], v['B'])] if testa[x]['F'] != v['F']]
        if not co:
            co = [x for x in nomi_p if testa.get(x) and testa[x]['Q'] == v['Q'] and testa[x]['F'] != v['F']]
        return co
    righe = []
    for f, d in fogli.items():
        if len(d['r']) == 1 and len(d['v']) == 1:
            r, v = d['r'][0], d['v'][0]
            co = compagne(r)
            if not co:
                continue
            cr = float(np.mean([C[idx[r], idx[x]] for x in co]))
            cv = float(np.mean([C[idx[v], idx[x]] for x in co]))
            righe.append((r, v, float(C[idx[r], idx[v]]), abs(cr - cv), cr, cv, co))
    rv = [x[2] for x in righe]
    asim = [x[3] for x in righe]
    rho = spearmanr(rv, asim).correlation
    nulli = []
    for _ in range(PERM):
        a = list(asim)
        rnd.shuffle(a)
        nulli.append(spearmanr(rv, a).correlation)
    z = (rho - statistics.mean(nulli)) / statistics.pstdev(nulli)
    esito = 'una faccia fuori dal suo bifoglio' if (rho < 0 and z < -3) else ('no' if abs(z) < 2 else 'incerto')
    descr = OrderedDict()
    for x in righe:
        base = x[0][:-1]
        if base in FOGLI_E318:
            diff = P[idx[x[0]]] - P[idx[x[1]]]
            top = [(nomi[j], round(float(diff[j]), 2)) for j in np.argsort(-np.abs(diff))[:5]]
            descr[base] = OrderedDict([('correlazione_recto_verso', round(x[2], 3)), ('asse_recto', round(float(s[idx[x[0]]]), 2)), ('asse_verso', round(float(s[idx[x[1]]]), 2)),
                                       ('recto_con_coniugato', round(x[4], 3)), ('verso_con_coniugato', round(x[5], 3)), ('confronto', x[6]),
                                       ('differenze_recto_meno_verso', top)])
    return OrderedDict([('fogli', len(righe)), ('rho_rv_asimmetria', rho), ('z', z), ('esito', esito), ('descrizione', descr)])


def main():
    testa = e308.intestazioni()
    voy, X, nomi, P = e308.profili()
    s = e314.punteggio(X, nomi)
    r319 = e319(voy, P, s, testa, random.Random(319))
    print('e319', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r319.items()}, flush=True)
    r323 = e323(voy, P, nomi, s, testa, random.Random(323))
    print('e323', r323['esito'], round(r323['rho_rv_asimmetria'], 3), round(r323['z'], 1), flush=True)
    json.dump(OrderedDict([('e319', r319), ('e323', r323)]), open(os.path.join(RISULTATI, 'e319_fascicoli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e319, e323 — I bifogli annidati; i fogli con le facce diverse', '', 'Preregistrazione: `preregistrazioni/e319.md`.', '', '## e319', '']
    if r319.get('fascicoli'):
        md += ['%d fascicoli con almeno 3 bifogli profilati (%d bifogli).' % (r319['fascicoli'], r319['bifogli']), '',
               '- (a) Spearman profondità–asse (scarto dalla media del fascicolo): %.3f, z %.1f; %s.' % (r319['rho_profondita_asse'], r319['z_a'], r319['direzione']),
               '- (b) bifogli a profondità consecutive meno le altre coppie dello stesso fascicolo: %+.3f, z %.1f.' % (r319['vicini_meno_altri'], r319['z_b']), '',
               'Esito e319: **%s**.' % r319['esito']]
    md += ['', '## e323', '', '%d fogli. Spearman fra correlazione recto/verso e asimmetria rispetto al coniugato: %.3f, z %.1f. Esito: **%s**.' % (
        r323['fogli'], r323['rho_rv_asimmetria'], r323['z'], r323['esito']), '']
    for f, d in r323['descrizione'].items():
        md.append('- %s: recto/verso %.2f; asse recto %+.2f, verso %+.2f; con il coniugato: recto %.2f, verso %.2f; differenze più grandi (recto − verso): %s.' % (
            f, d['correlazione_recto_verso'], d['asse_recto'], d['asse_verso'], d['recto_con_coniugato'], d['verso_con_coniugato'],
            ', '.join('%s %+.1f' % t for t in d['differenze_recto_meno_verso'])))
    open(os.path.join(RISULTATI, 'e319_fascicoli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
