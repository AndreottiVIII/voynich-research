# -*- coding: utf-8 -*-
"""Esperimento 273: la prima riga di un paragrafo somiglia alle prime righe di altri paragrafi della stessa sezione piu' che
al resto del proprio paragrafo, molto piu' della seconda riga (D1 - D2)?

Preregistrazione: preregistrazioni/e273.md. Scrive risultati/e273_intestazioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, ALTRI, RICAMPIONI = 273, 5, 1000
D = e237.D


def paragrafi():
    out, cur, pag, sez = [], None, None, None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        if not ps:
            continue
        if r.inizio_par or cur is None or r.pagina != pag:
            if cur and len(cur['righe']) >= 3:
                out.append(cur)
            cur = {'pagina': r.pagina, 'sezione': r.sezione, 'righe': []}
            pag = r.pagina
        cur['righe'].append(ps)
    if cur and len(cur['righe']) >= 3:
        out.append(cur)
    return out


def main():
    rnd = random.Random(SEME)
    P = paragrafi()
    tutte = {u for p in P for r in p['righe'] for u in r}
    inventario = sorted({x for u in tutte for x in u})
    vic = {}

    def V(u):
        if u not in vic:
            vic[u] = e237.vicini(u, inventario) | {u}
        return vic[u]

    def S(A, B):
        return sum(1 for u in A if V(u) & B) / len(A) if A else 0.0

    per_sez = defaultdict(list)
    for i, p in enumerate(P):
        per_sez[p['sezione']].append(i)
    diffs = []
    for i, p in enumerate(P):
        altri = [j for j in per_sez[p['sezione']] if P[j]['pagina'] != p['pagina']]
        if len(altri) < ALTRI:
            continue
        prime_altre = {u for j in rnd.sample(altri, ALTRI) for u in P[j]['righe'][0]}
        r1, r2 = p['righe'][0], p['righe'][1]
        resto1 = {u for r in p['righe'][1:] for u in r}
        resto2 = {u for k, r in enumerate(p['righe']) if k != 1 for u in r}
        d1 = S(r1, prime_altre) - S(r1, resto1)
        d2 = S(r2, prime_altre) - S(r2, resto2)
        diffs.append((d1, d2, p['sezione']))
    vals = [a - b for a, b, _ in diffs]
    media = statistics.mean(vals)
    boot = []
    for _ in range(RICAMPIONI):
        boot.append(statistics.mean(rnd.choice(vals) for _ in vals))
    se = statistics.pstdev(boot)
    z = media / se if se else None
    # descrittivo: parole delle prime righe rare nel resto, per sezione
    descr = OrderedDict()
    for s in sorted(per_sez):
        c1 = Counter(''.join(u) for i in per_sez[s] for u in P[i]['righe'][0])
        c2 = Counter(''.join(u) for i in per_sez[s] for r in P[i]['righe'][1:] for u in r)
        n1, n2 = sum(c1.values()) or 1, sum(c2.values()) or 1
        rap = {w: (c / n1) / ((c2[w] + 1) / n2) for w, c in c1.items() if c >= 3}
        descr[s] = [(w, round(x, 1), c1[w]) for w, x in sorted(rap.items(), key=lambda kv: -kv[1])[:5]]
    esito = 'registro di intestazione' if (z or 0) > 3 else ('nessun registro a parte' if abs(z or 0) <= 2 else 'incerto')
    ris = OrderedDict([('paragrafi', len(diffs)), ('D1_medio', statistics.mean(a for a, _, _ in diffs)), ('D2_medio', statistics.mean(b for _, b, _ in diffs)),
                       ('D1_meno_D2', media), ('errore_standard', se), ('z', z), ('parole_tipiche_delle_prime_righe', descr), ('esito', esito)])
    print(json.dumps(ris, ensure_ascii=False, default=float)[:1500], flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e273_intestazioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e273 — Le prime righe dei paragrafi sono un registro a parte?', '',
          'D1 = S(prima riga, prime righe di %d paragrafi della stessa sezione) − S(prima riga, resto del paragrafo); D2 = lo stesso per la seconda riga. '
          'Preregistrazione: `preregistrazioni/e273.md`.' % ALTRI, '', '| paragrafi | D1 medio | D2 medio | D1 − D2 | z |', '|---|---|---|---|---|',
          '| %d | %+.3f | %+.3f | %+.3f | %.1f |' % (len(diffs), ris['D1_medio'], ris['D2_medio'], media, z or 0), '',
          'Parole tipiche delle prime righe (rapporto di frequenza prime righe / resto, occorrenze):', '']
    md += ['- %s: %s' % (s, ', '.join('%s %.1f (%d)' % x for x in v)) for s, v in descr.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e273_intestazioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
