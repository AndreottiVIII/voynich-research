# -*- coding: utf-8 -*-
"""Esperimento 103: le etichette dello zodiaco si corrispondono per posizione fra i segni?

Preregistrazione: preregistrazioni/e103.md. Scrive risultati/e103_zodiaco_posizioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, LONTANI = 103, 500, 3
D = misure.divisore(misure.GLIFI_EVA)
SEGNI = [['f70v2'], ['f70v1', 'f71r'], ['f71v', 'f72r1'], ['f72r2'], ['f72r3'], ['f72v3'], ['f72v2'], ['f72v1'], ['f73r'], ['f73v']]


def etichette():
    per = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo == 'Lz':
            ps = [w for w in r.parole if trascrizione.pulita(w)]
            per.setdefault(r.pagina, []).append(tuple(D(ps[0])) if ps else None)
    return [[x for p in pagine for x in per.get(p, [])] for pagine in SEGNI]


def sim(a, b):
    return 1 - misure._dist_norm(a, b)


def delta(segni, f):
    stesso, diverso = [], []
    for s in range(len(segni)):
        for t in range(s + 1, len(segni)):
            A, B = segni[s], segni[t]
            for i, a in enumerate(A):
                if a is None:
                    continue
                for j, b in enumerate(B):
                    if b is None:
                        continue
                    if i == j:
                        stesso.append(f(a, b))
                    elif abs(i - j) >= LONTANI:
                        diverso.append(f(a, b))
    return statistics.mean(stesso) - statistics.mean(diverso)


def allinea(segni, f):
    """Spostamento ciclico che massimizza la somiglianza allo stesso indice con i segni gia' allineati."""
    out = [segni[0]]
    for S in segni[1:]:
        n = len(S)
        migliore, valore = S, None
        for k in range(n):
            R = S[k:] + S[:k]
            v = sum(f(a, b) for T in out for a, b in zip(R, T) if a is not None and b is not None)
            if valore is None or v > valore:
                migliore, valore = R, v
        out.append(migliore)
    return out


def prova(segni, f, rnd, libero=False):
    calcola = (lambda ss: delta(allinea(ss, f), f)) if libero else (lambda ss: delta(ss, f))
    vero = calcola(segni)
    nulli = []
    for _ in range(PERMUTAZIONI if not libero else PERMUTAZIONI // 5):
        mes = []
        for S in segni:
            S = S[:]
            rnd.shuffle(S)
            mes.append(S)
        nulli.append(calcola(mes))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    p = (1 + sum(x >= vero for x in nulli)) / (1 + len(nulli))
    return OrderedDict([('delta', vero), ('nullo', m), ('z', (vero - m) / s if s else None), ('p', p), ('permutazioni', len(nulli))])


def main():
    segni = etichette()
    primo = lambda a, b: float(a[0] == b[0])
    ris = OrderedDict([('etichette_per_segno', [len(s) for s in segni])])
    rnd = random.Random(SEME)
    ultimi = [g for g, _ in Counter(x[-1] for S in segni for x in S if x).most_common(6)]
    g_i = [rnd.choice(ultimi) for _ in range(30)]
    controllo = [[(x[:-1] + (g_i[i],)) if (x and rnd.random() < 0.5) else x for i, x in enumerate(S)] for S in segni]
    ris['controllo positivo, somiglianza'] = prova(controllo, sim, random.Random(SEME))
    ris['somiglianza, indice fisso'] = prova(segni, sim, random.Random(SEME))
    ris['primo segno, indice fisso'] = prova(segni, primo, random.Random(SEME))
    ris['somiglianza, allineamento libero'] = prova(segni, sim, random.Random(SEME), libero=True)
    ris['primo segno, allineamento libero'] = prova(segni, primo, random.Random(SEME), libero=True)
    for k, r in ris.items():
        if isinstance(r, dict):
            print('%-36s delta %.4f nullo %.4f z %.2f p %.3f (%d)' % (k, r['delta'], r['nullo'], r['z'] or 0, r['p'], r['permutazioni']), flush=True)
    ps = [ris[k]['p'] for k in ris if k.startswith(('somiglianza', 'primo'))]
    ris['valido'] = ris['controllo positivo, somiglianza']['p'] < 0.01
    ris['corrispondenza'] = min(ps) < 0.01 or sum(p < 0.05 for p in ps) >= 2
    print('valido', ris['valido'], '| corrispondenza', ris['corrispondenza'])
    with open(os.path.join(RISULTATI, 'e103_zodiaco_posizioni.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e103 — Le etichette dello zodiaco si corrispondono per posizione?', '',
           '10 segni, etichette %s. Δ = media allo stesso indice − media a indici distanti ≥ %d. Preregistrazione: '
           '`preregistrazioni/e103.md`.' % (ris['etichette_per_segno'], LONTANI), '', '| prova | Δ | nullo | z | p |', '|---|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %.4f | %.4f | %.2f | %.3f |' % (k, r['delta'], r['nullo'], r['z'] or 0, r['p']))
    out += ['', 'Valido: **%s**; corrispondenza per posizione: **%s**.' % ('sì' if ris['valido'] else 'no', 'sì' if ris['corrispondenza'] else 'no')]
    with open(os.path.join(RISULTATI, 'e103_zodiaco_posizioni.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
