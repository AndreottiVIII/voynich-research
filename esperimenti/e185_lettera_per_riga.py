# -*- coding: utf-8 -*-
"""Esperimento 185: correlazione totale fra le cinque scelte di grafia della stessa riga (valore di maggioranza),
contro permutazioni indipendenti dentro la pagina; controllo con una lettera di Bacon per riga.

Preregistrazione: preregistrazioni/e185.md. Scrive risultati/e185_lettera_per_riga.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e181_bacone as e181

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 185, 2000
SCELTE = (0, 1, 2, 4, 6)


def entropia(c):
    n = sum(c.values())
    return -sum(x / n * math.log2(x / n) for x in c.values() if x)


def tc(simboli):
    return sum(entropia(Counter(s[i] for s in simboli)) for i in range(5)) - entropia(Counter(simboli))


def righe_simboli():
    pagina = {k: r.pagina for k, r in enumerate(r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole)}
    per = defaultdict(lambda: defaultdict(list))
    for f, k, v in e181.occorrenze():
        per[k][f].append(v)
    out = []
    for k in sorted(per):
        s = []
        for f in SCELTE:
            x = per[k].get(f)
            m = sum(x) / len(x) if x else 0.5
            s.append(None if m == 0.5 else int(m > 0.5))
        if all(b is not None for b in s):
            out.append((pagina[k], tuple(s)))
    return out


def prova(dati, rnd):
    vero = tc([s for _, s in dati])
    per = defaultdict(list)
    for i, (p, _) in enumerate(dati):
        per[p].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        col = [[s[i] for _, s in dati] for i in range(5)]
        for i in range(5):
            for idx in per.values():
                x = [col[i][j] for j in idx]
                rnd.shuffle(x)
                for j, y in zip(idx, x):
                    col[i][j] = y
        nulli.append(tc(list(zip(*col))))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('tc', vero), ('nullo', m), ('z', (vero - m) / s if s else None), ('p', (1 + sum(n >= vero for n in nulli)) / (1 + PERMUTAZIONI))])


def main():
    rnd = random.Random(SEME)
    dati = righe_simboli()
    bit = e181.bacone(5 * len(dati))
    lettere = [tuple(bit[5 * i:5 * i + 5]) for i in range(len(dati))]
    testi = OrderedDict([('Voynich', dati), ('controllo: Bacone, una lettera per riga', [(p, l) for (p, _), l in zip(dati, lettere)]),
                         ('controllo: Bacone mescolato (0,7)', [(p, l if rnd.random() < 0.7 else s) for (p, s), l in zip(dati, lettere)])])
    ris = OrderedDict([('righe', len(dati))])
    for nome, d in testi.items():
        ris[nome] = prova(d, rnd)
        print('%-42s TC %.4f (nullo %.4f) z %.1f p %.4f' % (nome, ris[nome]['tc'], ris[nome]['nullo'], ris[nome]['z'] or 0, ris[nome]['p']), flush=True)
    z = lambda n: ris[n]['z'] or 0
    valido = z('controllo: Bacone, una lettera per riga') > 4
    esito = 'test non valido' if not valido else ('lettere per riga presenti' if z('Voynich') > 4 else ('assenti' if z('Voynich') < 2 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    ris['simboli_piu_frequenti'] = [[''.join(map(str, s)), n] for s, n in Counter(s for _, s in dati).most_common(8)]
    print('valido %s | esito: %s' % (valido, esito))
    with open(os.path.join(RISULTATI, 'e185_lettera_per_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e185 — Una lettera per riga? Dipendenza fra le cinque scelte della stessa riga', '',
           'Correlazione totale (bit) fra i valori di maggioranza delle cinque scelte, su %d righe con tutte e cinque definite; nullo: permutazioni indipendenti '
           'dentro la pagina. Preregistrazione: `preregistrazioni/e185.md`.' % len(dati), '', '| testo | TC | nullo | z | p |', '|---|---|---|---|---|']
    for nome in testi:
        r = ris[nome]
        out.append('| %s | %.4f | %.4f | %.1f | %.4f |' % (nome, r['tc'], r['nullo'], r['z'] or 0, r['p']))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e185_lettera_per_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
