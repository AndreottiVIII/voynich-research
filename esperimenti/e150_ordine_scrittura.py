# -*- coding: utf-8 -*-
"""Esperimento 150: un ordine dei bifogli ricostruito dalla somiglianza di vocabolario (su meta' delle righe) e' piu'
"dolce" dell'ordine di rilegatura sull'altra meta'?

Preregistrazione: preregistrazioni/e150.md. Scrive risultati/e150_ordine_scrittura.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e148_bifogli as e148

RISULTATI = os.path.join(QUI, '..', 'risultati')
DIVISIONI, CASUALI = range(1, 21), 1000


def unita():
    var = e148.variabili_pagine()
    info = {}
    for pag, v in var.items():
        f = e148.foglio(pag)
        if f is not None and 'Q' in v and 'B' in v:
            info.setdefault(f, (v['Q'], v['B'], v.get('I'), v.get('H'), v.get('L')))
    righe = defaultdict(list)
    for r in trascrizione.leggi('ZL'):
        f = e148.foglio(r.pagina)
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if f in info and ps:
            righe[f].append(ps)
    per = defaultdict(list)
    for f in righe:
        per[info[f][:2]].append(f)
    out = OrderedDict()
    for chiave, ff in sorted(per.items(), key=lambda kv: min(kv[1])):
        rr = [ps for f in sorted(ff) for ps in righe[f]]
        if sum(map(len, rr)) >= 100:
            nome = '-'.join('f%d' % f for f in sorted(ff))
            out[nome] = {'righe': rr, 'primo': min(ff), 'sezione': info[min(ff)][2], 'mano': info[min(ff)][3], 'lingua': info[min(ff)][4]}
    return out


def matrice(U, quali, s):
    rnd = random.Random(s)
    vA, vB = {}, {}
    for n, u in U.items():
        a, b = Counter(), Counter()
        for ps in u['righe']:
            (a if rnd.random() < 0.5 else b).update(ps)
        vA[n], vB[n] = a, b
    nomi = list(U)
    SA = [[e148.coseno(vA[x], vA[y]) for y in nomi] for x in nomi]
    SB = [[e148.coseno(vB[x], vB[y]) for y in nomi] for x in nomi]
    return nomi, SA, SB


def valore(ordine, S):
    return statistics.mean(S[a][b] for a, b in zip(ordine, ordine[1:]))


def ricostruisci(S):
    n = len(S)
    migliore = None
    for p in range(n):
        ordine, resto = [p], set(range(n)) - {p}
        while resto:
            u = ordine[-1]
            v = max(resto, key=lambda j: S[u][j])
            ordine.append(v)
            resto.remove(v)
        migliorato = True
        while migliorato:
            migliorato = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    a, b = ordine[i - 1], ordine[i]
                    c = ordine[j]
                    d = ordine[j + 1] if j + 1 < n else None
                    prima = S[a][b] + (S[c][d] if d is not None else 0)
                    dopo = S[a][c] + (S[b][d] if d is not None else 0)
                    if dopo > prima + 1e-12:
                        ordine[i:j + 1] = ordine[i:j + 1][::-1]
                        migliorato = True
        v = valore(ordine, S)
        if migliore is None or v > migliore[0]:
            migliore = (v, ordine)
    return migliore[1]


def main():
    U = unita()
    print('unita\': %d' % len(U), flush=True)
    ris = OrderedDict([('unita', len(U)), ('divisioni', OrderedDict())])
    vittorie = 0
    for s in DIVISIONI:
        nomi, SA, SB = matrice(U, None, s)
        rileg = sorted(range(len(nomi)), key=lambda i: U[nomi[i]]['primo'])
        ric = ricostruisci(SA)
        rnd = random.Random(1000 + s)
        casuali = []
        for _ in range(CASUALI):
            o = list(range(len(nomi)))
            rnd.shuffle(o)
            casuali.append(valore(o, SB))
        r = OrderedDict([('ricostruito_su_B', valore(ric, SB)), ('rilegatura_su_B', valore(rileg, SB)), ('casuali_su_B', statistics.mean(casuali)),
                         ('ricostruito_su_A', valore(ric, SA)), ('rilegatura_su_A', valore(rileg, SA))])
        vittorie += r['ricostruito_su_B'] > r['rilegatura_su_B']
        ris['divisioni'][s] = r
        print('divisione %2d | su B: ricostruito %.4f, rilegatura %.4f, casuali %.4f | su A: ricostruito %.4f, rilegatura %.4f' % (
            s, r['ricostruito_su_B'], r['rilegatura_su_B'], r['casuali_su_B'], r['ricostruito_su_A'], r['rilegatura_su_A']), flush=True)
        if s == 1:
            ris['ordine_ricostruito_divisione_1'] = [(nomi[i], U[nomi[i]]['sezione'], U[nomi[i]]['mano'], U[nomi[i]]['lingua']) for i in ric]
    ris['vittorie'] = vittorie
    ris['ordine_diverso'] = vittorie >= 18
    print('vittorie %d su 20 | ordine di scrittura diverso dalla rilegatura: %s' % (vittorie, vittorie >= 18))
    with open(os.path.join(RISULTATI, 'e150_ordine_scrittura.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e150 — Un ordine di scrittura dei bifogli diverso dalla rilegatura?', '', 'Ordine ricostruito sulla metà A delle righe (somiglianza di vocabolario, avido + 2-opt), '
           'valutato sulla metà B. Preregistrazione: `preregistrazioni/e150.md`.', '',
           '| divisione | ricostruito su B | rilegatura su B | casuali su B |', '|---|---|---|---|']
    for s, r in ris['divisioni'].items():
        out.append('| %d | %.4f | %.4f | %.4f |' % (s, r['ricostruito_su_B'], r['rilegatura_su_B'], r['casuali_su_B']))
    out += ['', 'Vittorie del ricostruito sulla rilegatura: **%d su 20**. Ordine di scrittura diverso: **%s**.' % (vittorie, 'sì' if vittorie >= 18 else 'no'), '',
            '## Ordine ricostruito (divisione 1): unità, sezione, mano, lingua', '', ' → '.join('%s (%s %s %s)' % t for t in ris['ordine_ricostruito_divisione_1'])]
    with open(os.path.join(RISULTATI, 'e150_ordine_scrittura.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
