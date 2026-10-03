# -*- coding: utf-8 -*-
"""Esperimento 270: come l'e190 (disegno della pianta contro vocabolario), ma con la distanza calcolata sulla forma (coppie di
segni) delle sole parole nuove (classe N dell'e237) di ogni pagina d'erbario. Le caratteristiche del disegno si salvano in
dati/cache/disegni_e190.json.

Preregistrazione: preregistrazioni/e270.md. Scrive risultati/e270_parole_nuove_piante.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e148_bifogli as e148
import e166_intinte as e166
import e173_dimensione_scrittura as e173
import e190_piante_vocabolario_bis as e190
import e237_riuso_pagina as e237
import e269_parole_non_copiate as e269

RISULTATI = os.path.join(QUI, '..', 'risultati')
CACHE = os.path.join(QUI, '..', 'dati', 'cache', 'disegni_e190.json')
MIN_NUOVE = 8
D = e237.D


def coppie_segni(ws):
    c = Counter()
    for w in ws:
        u = ('^',) + tuple(D(w)) + ('$',)
        c.update(zip(u, u[1:]))
    return c


def coseno(a, b):
    num = sum(a[k] * b[k] for k in a if k in b)
    den = (sum(v * v for v in a.values()) ** 0.5) * (sum(v * v for v in b.values()) ** 0.5)
    return num / den if den else 0.0


def main():
    rnd = random.Random(e190.SEME)
    var = e148.variabili_pagine()
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            per.setdefault(r.pagina, [r.sezione, []])[1].append(ps)
    nomi = list(per)
    classi = e269.classi_per_parola([per[p][1] for p in nomi])
    nuove = {p: [w for r in cp for w, c in r if c == 'N'] for p, cp in zip(nomi, classi)}
    pagine = [p for p in nomi if per[p][0] == 'H' and len(nuove[p]) >= MIN_NUOVE and os.path.exists(os.path.join(e34.RIQUADRI, p + '.js'))
              and os.path.exists(os.path.join(e166.IMMAGINI, p + '.jpg')) and p in var and 'Q' in var[p] and 'H' in var[p] and 'L' in var[p]]
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    for p in pagine:
        if p not in cache:
            cache[p] = [float(x) for x in e190.caratteristiche(p)]
            json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
    M = np.array([cache[p] for p in pagine])
    M = (M - M.mean(axis=0)) / np.where(M.std(axis=0) > 0, M.std(axis=0), 1)
    F = {p: M[i] for i, p in enumerate(pagine)}
    prof = {p: coppie_segni(nuove[p]) for p in pagine}
    gruppo = {p: (var[p]['H'], var[p]['L']) for p in pagine}
    coppie = [(a, b) for i, a in enumerate(pagine) for b in pagine[i + 1:] if gruppo[a] == gruppo[b] and var[a]['Q'] != var[b]['Q']]
    dv = [1 - coseno(prof[a], prof[b]) for a, b in coppie]
    per_g = defaultdict(list)
    for p in pagine:
        per_g[gruppo[p]].append(p)

    def stat(ass):
        return e173.spearman([float(np.linalg.norm(F[ass[a]] - F[ass[b]])) for a, b in coppie], dv)

    vero = stat({p: p for p in pagine})
    nulli = []
    for _ in range(e190.PERMUTAZIONI):
        ass = {}
        for g, pp in per_g.items():
            q = pp[:]
            rnd.shuffle(q)
            ass.update(zip(pp, q))
        nulli.append(stat(ass))
    p = (1 + sum(n >= vero for n in nulli)) / (1 + e190.PERMUTAZIONI)
    esito = 'le parole nuove seguono la pianta' if vero > 0 and p < 0.01 else ('nessun legame' if p > 0.05 else 'incerto')
    ris = OrderedDict([('pagine', len(pagine)), ('coppie', len(coppie)), ('parole_nuove_medie', statistics.mean(len(nuove[q]) for q in pagine)),
                       ('spearman', vero), ('nullo_media', statistics.mean(nulli)), ('p', p), ('esito', esito)])
    print(dict(ris), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e270_parole_nuove_piante.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e270 — Le parole nuove di una pagina d\'erbario seguono la pianta?', '',
          "Come l'e190, con la distanza sulla forma (coppie di segni) delle parole nuove (classe N) di ogni pagina. Preregistrazione: "
          '`preregistrazioni/e270.md`.', '', '| pagine | coppie | parole nuove per pagina | Spearman | nullo | p |', '|---|---|---|---|---|---|',
          '| %d | %d | %.1f | %.3f | %.3f | %.4f |' % (len(pagine), len(coppie), ris['parole_nuove_medie'], vero, statistics.mean(nulli), p), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e270_parole_nuove_piante.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
