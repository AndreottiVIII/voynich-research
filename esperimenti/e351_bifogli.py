# -*- coding: utf-8 -*-
"""Esperimenti 351 e 352. (e351) coesione dei fascicoli per ripresa fra bifogli, e bifogli piu' vicini a un altro
fascicolo che al proprio; (e352) le etichette ritrovano parole (uguali o a una modifica) nel testo della propria pagina
e del proprio bifoglio piu' che altrove?

Preregistrazione: preregistrazioni/e351.md. Scrive risultati/e351_bifogli.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def carica():
    testo, etich, sez = defaultdict(list), defaultdict(list), {}
    for r in trascrizione.leggi('ZL'):
        if not r.parole:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if not ws:
            continue
        sez.setdefault(r.pagina, r.sezione or '?')
        if r.tipo[0] == trascrizione.PARAGRAFO:
            testo[r.pagina] += ws
        elif r.tipo[0] == 'L':
            etich[r.pagina] += ws
    return testo, etich, sez


def e351(testo, sez, testa, sim, rnd):
    pp = [p for p, ws in testo.items() if len(ws) >= 60 and testa.get(p, {}).get('Q')]
    bif = defaultdict(list)
    for p in pp:
        bif[(testa[p]['Q'], testa[p]['B'])].append(p)
    unita = list(bif)
    ib = {b: k for k, b in enumerate(unita)}
    sez_b = {b: Counter(sez[p] for p in bif[b]).most_common(1)[0][0] for b in unita}
    toks = {b: [w for p in bif[b] for w in testo[p] if len(D(w)) >= 3] for b in unita}
    bif_di = defaultdict(set)
    for b in unita:
        for w in set(toks[b]):
            bif_di[w].add(ib[b])
    n = len(unita)
    S = np.zeros((n, n))
    cache = {}
    for b in unita:
        cnt = Counter()
        for w in toks[b]:
            if w not in cache:
                s = set()
                for v in sim.get(w, (w,)):
                    s |= bif_di.get(v, set())
                cache[w] = s
            for y in cache[w]:
                cnt[y] += 1
        for y, c in cnt.items():
            S[ib[b], y] = c / len(toks[b])
    S = (S + S.T) / 2
    per_sez = defaultdict(list)
    for b in unita:
        per_sez[sez_b[b]].append(ib[b])
    sezioni = {s: idx for s, idx in per_sez.items() if len({unita[i][0] for i in idx}) >= 3}
    quire = np.array([unita[i][0] for i in range(n)], dtype=object)

    def diffs(q):
        out = {}
        for s, idx in sezioni.items():
            for i in idx:
                propri = [j for j in idx if j != i and q[j] == q[i]]
                if not propri:
                    continue
                altri = defaultdict(list)
                for j in idx:
                    if q[j] != q[i]:
                        altri[q[j]].append(S[i, j])
                if not altri:
                    continue
                sp = float(np.mean([S[i, j] for j in propri]))
                medie = {k: float(np.mean(v)) for k, v in altri.items()}
                out[i] = (sp, medie)
        return out
    vero = diffs(quire)
    coes = statistics.mean(sp - statistics.mean(m.values()) for sp, m in vero.values())
    nul, dist_max = [], []
    for _ in range(PERM):
        q = quire.copy()
        for idx in sezioni.values():
            lab = list(q[idx])
            rnd.shuffle(lab)
            q[idx] = lab
        d = diffs(q)
        nul.append(statistics.mean(sp - statistics.mean(m.values()) for sp, m in d.values()))
        dist_max += [max(m.values()) - sp for sp, m in d.values()]
    z = (coes - statistics.mean(nul)) / statistics.pstdev(nul)
    soglia = float(np.percentile(dist_max, 95))
    cand = []
    for i, (sp, m) in vero.items():
        k, v = max(m.items(), key=lambda kv: kv[1])
        if v - sp > soglia:
            cand.append(OrderedDict([('bifoglio', '%s-%s' % unita[i]), ('pagine', bif[unita[i]]), ('sezione', sez_b[unita[i]]), ('ripresa_col_proprio', round(sp, 3)),
                                     ('fascicolo_piu_vicino', k), ('ripresa_con_quello', round(v, 3))]))
    esito = 'fascicoli coesi' if z > 3 else ('no' if z < 2 else 'incerto')
    return OrderedDict([('bifogli', len(vero)), ('coesione', coes), ('nullo', statistics.mean(nul)), ('z', z), ('esito', esito), ('soglia_95', soglia), ('candidati', cand)])


def e352(testo, etich, sez, testa, sim, rnd):
    con_testo = [p for p, ws in testo.items() if len(ws) >= 30]
    per_sez = defaultdict(list)
    for p in con_testo:
        per_sez[sez[p]].append(p)
    bif = defaultdict(list)
    for p in con_testo:
        h = testa.get(p)
        if h and h['Q']:
            bif[(h['Q'], h['B'])].append(p)
    compagne = {p: [x for x in bif.get((testa[p]['Q'], testa[p]['B']), []) if x != p] if testa.get(p, {}).get('Q') else [] for p in con_testo}
    tipi = {p: set(testo[p]) for p in con_testo}
    pagine = [p for p, ws in etich.items() if len(ws) >= 3 and p in tipi and len(per_sez[sez[p]]) >= 3]

    def trova(w, insieme):
        return any(v in insieme for v in sim.get(w, (w,)))

    def misure_(assegna):
        a = b = n = 0
        nb = 0
        for p in pagine:
            q = assegna[p]
            co = set().union(*[tipi[x] for x in compagne[q]]) if compagne[q] else None
            for w in etich[p]:
                n += 1
                a += trova(w, tipi[q])
                if co is not None:
                    nb += 1
                    b += trova(w, co)
        return a / n, (b / nb if nb else 0.0)
    ident = {p: p for p in pagine}
    vero = misure_(ident)
    nul = []
    for _ in range(PERM):
        nul.append(misure_({p: rnd.choice([x for x in per_sez[sez[p]] if x != p]) for p in pagine}))
    z = [(vero[k] - statistics.mean(x[k] for x in nul)) / (statistics.pstdev(x[k] for x in nul) or 1) for k in (0, 1)]
    es = lambda zz: 'le etichette appartengono alla sessione' if zz > 3 else ('no' if zz < 2 else 'incerto')
    return OrderedDict([('pagine', len(pagine)), ('etichette', sum(len(etich[p]) for p in pagine)),
                        ('stessa_pagina', OrderedDict([('quota', vero[0]), ('nullo', statistics.mean(x[0] for x in nul)), ('z', z[0]), ('esito', es(z[0]))])),
                        ('stesso_bifoglio', OrderedDict([('quota', vero[1]), ('nullo', statistics.mean(x[1] for x in nul)), ('z', z[1]), ('esito', es(z[1]))]))])


def main():
    rnd = random.Random(351)
    testa = e308.intestazioni()
    testo, etich, sez = carica()
    tipi = {w for ws in testo.values() for w in ws if len(D(w)) >= 3} | {w for ws in etich.values() for w in ws}
    sim = e350.simili_globali(tipi)
    r351 = e351(testo, sez, testa, sim, rnd)
    print('e351', r351['esito'], round(r351['coesione'], 4), round(r351['z'], 1), len(r351['candidati']), flush=True)
    r352 = e352(testo, etich, sez, testa, sim, random.Random(352))
    print('e352', r352, flush=True)
    json.dump(OrderedDict([('e351', r351), ('e352', r352)]), open(os.path.join(RISULTATI, 'e351_bifogli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e351, e352 — Bifogli forse rilegati altrove; le etichette e la loro sessione', '', 'Preregistrazione: `preregistrazioni/e351.md`.', '',
          '## e351', '', '%d bifogli. Coesione dei fascicoli (ripresa con il proprio fascicolo meno con gli altri): %+.4f contro %+.4f del nullo, z %.1f: **%s**.' % (
              r351['bifogli'], r351['coesione'], r351['nullo'], r351['z'], r351['esito']), '',
          'Bifogli più vicini a un altro fascicolo che al proprio (oltre il 95° percentile del nullo, %.3f):' % r351['soglia_95'], '']
    for c in r351['candidati']:
        md.append('- %s (%s; pagine %s): ripresa col proprio fascicolo %.3f, con il fascicolo %s %.3f.' % (c['bifoglio'], c['sezione'], ', '.join(c['pagine']), c['ripresa_col_proprio'],
                                                                                                         c['fascicolo_piu_vicino'], c['ripresa_con_quello']))
    if not r351['candidati']:
        md.append('- nessuno.')
    md += ['', '## e352 — %d pagine con etichette, %d parole d\'etichetta' % (r352['pagine'], r352['etichette']), '',
           '- Nel testo della stessa pagina: %.3f contro %.3f, z %.1f: **%s**.' % (r352['stessa_pagina']['quota'], r352['stessa_pagina']['nullo'], r352['stessa_pagina']['z'], r352['stessa_pagina']['esito']),
           '- Nel testo delle altre pagine dello stesso bifoglio: %.3f contro %.3f, z %.1f: **%s**.' % (r352['stesso_bifoglio']['quota'], r352['stesso_bifoglio']['nullo'], r352['stesso_bifoglio']['z'], r352['stesso_bifoglio']['esito'])]
    open(os.path.join(RISULTATI, 'e351_bifogli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
