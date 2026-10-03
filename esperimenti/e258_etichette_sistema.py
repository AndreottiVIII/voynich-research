# -*- coding: utf-8 -*-
"""Esperimento 258: le etichette somigliano alle etichette della stessa pagina e delle pagine vicine (M1), e usano meno il
lessico dei paragrafi di un campione di parole di paragrafo (M2)?

Preregistrazione: preregistrazioni/e258.md. Scrive risultati/e258_etichette_sistema.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237
import e245_etichette_testo as e245

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 258, 200
D = e237.D


def main():
    rnd = random.Random(SEME)
    lab, par, sez = e245.dati()
    ordine = []
    for r in trascrizione.leggi('ZL'):
        if r.pagina not in ordine:
            ordine.append(r.pagina)
    con_lab = [p for p in ordine if lab.get(p)]
    idx = {p: i for i, p in enumerate(ordine)}
    freq_par = Counter(w for rr in par.values() for r in rr for w in r)
    inventario = sorted({x for w in freq_par for x in D(w)} | {x for ws in lab.values() for w in ws for x in D(w)})
    vic = {}

    def V(w):
        if w not in vic:
            vic[w] = e237.vicini(tuple(D(w)), inventario) | {tuple(D(w))}
        return vic[w]

    lab_u = {p: [tuple(D(w)) for w in lab[p]] for p in con_lab}
    per_sez = defaultdict(list)
    for p in con_lab:
        per_sez[sez[p]].append(p)
    vicine = {p: [q for q in con_lab if q != p and abs(idx[q] - idx[p]) <= 2] for p in con_lab}
    # M1
    stessa, vic_v = [], []
    for p in con_lab:
        for i, w in enumerate(lab[p]):
            altre = {u for j, u in enumerate(lab_u[p]) if j != i}
            if altre:
                stessa.append(bool(V(w) & altre))
            if vicine[p]:
                vic_v.append(bool(V(w) & {u for q in vicine[p] for u in lab_u[q]}))
    n_stessa, n_vic = [], []
    for _ in range(REPLICHE):
        a, b = [], []
        for p in con_lab:
            cand = [q for q in per_sez[sez[p]] if q != p and q not in vicine[p]]
            if not cand:
                continue
            q1 = rnd.choice(cand)
            qs = rnd.sample(cand, min(len(vicine[p]), len(cand))) if vicine[p] else []
            u1 = set(lab_u[q1])
            uq = {u for q in qs for u in lab_u[q]}
            for i, w in enumerate(lab[p]):
                if len(lab[p]) > 1:
                    a.append(bool(V(w) & u1))
                if qs:
                    b.append(bool(V(w) & uq))
        n_stessa.append(sum(a) / len(a))
        n_vic.append(sum(b) / len(b))
    z = lambda x, xs: (x - statistics.mean(xs)) / statistics.pstdev(xs) if statistics.pstdev(xs) else None
    q_s, q_v = sum(stessa) / len(stessa), sum(vic_v) / len(vic_v)
    m1 = OrderedDict([('stessa pagina', OrderedDict([('quota', q_s), ('nullo', statistics.mean(n_stessa)), ('z', z(q_s, n_stessa))])),
                      ('pagine vicine (±2)', OrderedDict([('quota', q_v), ('nullo', statistics.mean(n_vic)), ('z', z(q_v, n_vic))]))])
    # M2
    tutte_lab = [(p, w) for p in con_lab for w in lab[p]]
    q_att = sum(freq_par[w] >= 1 for _, w in tutte_lab) / len(tutte_lab)
    per_sez_par = defaultdict(list)
    for p, rr in par.items():
        per_sez_par[sez.get(p)] += [w for r in rr for w in r if len(D(w)) >= 2]
    quante = Counter(sez[p] for p, _ in tutte_lab)
    nulli = []
    for _ in range(REPLICHE):
        xs = []
        for s, n in quante.items():
            pool = per_sez_par.get(s) or [w for v in per_sez_par.values() for w in v]
            xs += [freq_par[w] >= 2 for w in rnd.choices(pool, k=n)]
        nulli.append(sum(xs) / len(xs))
    m2 = OrderedDict([('quota_attestata_nei_paragrafi', q_att), ('nullo_parole_di_paragrafo', statistics.mean(nulli)), ('z', z(q_att, nulli))])
    zv = max(m1['stessa pagina']['z'] or 0, m1['pagine vicine (±2)']['z'] or 0)
    z2 = m2['z'] or 0
    esito = ('sistema a parte' if zv > 3 and z2 < -3 else 'etichette dal lessico comune' if abs(z2) <= 2 else 'misto')
    ris = OrderedDict([('etichette', len(tutte_lab)), ('pagine_con_etichette', len(con_lab)), ('M1', m1), ('M2', m2), ('esito', esito)])
    print(json.dumps(ris, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e258_etichette_sistema.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e258 — Le etichette sono un sistema a parte?', '',
          'Etichette (loci L, ≥ 2 unità): %d su %d pagine. Corrispondenza = ripetizione o variante a distanza 1. Preregistrazione: '
          '`preregistrazioni/e258.md`.' % (len(tutte_lab), len(con_lab)), '', '| misura | vera | nulla | z |', '|---|---|---|---|']
    for k, r in m1.items():
        md.append('| M1, etichette %s | %.3f | %.3f | %.1f |' % (k, r['quota'], r['nullo'], r['z'] or 0))
    md.append('| M2, attestate nei paragrafi (contro parole di paragrafo) | %.3f | %.3f | %.1f |' % (q_att, m2['nullo_parole_di_paragrafo'], z2))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e258_etichette_sistema.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
