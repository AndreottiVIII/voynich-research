# -*- coding: utf-8 -*-
"""Esperimento 397: quota dell'incertezza sulla posizione degli spazi tolta dai segni vicini (2 a sinistra, 2 a destra),
con modello a conteggi e due meta' incrociate. Voynich (5 sottoinsiemi da 10.000 parole), testi sensati (parole intere),
gibberish umano.

Preregistrazione: preregistrazioni/e397.md. Scrive risultati/e397_spazi.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
MIN = 5


def posizioni(righe):
    """[(contesti dal piu' lungo al piu' corto, spazio)] per una lista di righe di parole (tuple di segni)."""
    out = []
    for r in righe:
        segni, spazi = [], []
        for k, w in enumerate(r):
            for i, s in enumerate(w):
                if segni:
                    spazi.append(i == 0)
                segni.append(s)
        n = len(segni)
        for t in range(n - 1):
            l2 = tuple(segni[max(0, t - 1):t + 1])
            r2 = tuple(segni[t + 1:t + 3])
            ctx = [('a', l2, r2), ('b', segni[t], segni[t + 1]), ('c', segni[t])]
            out.append((ctx, spazi[t]))
    return out


def modello(train):
    c = defaultdict(lambda: [0, 0])
    tot = [0, 0]
    for ctx, s in train:
        for k in ctx:
            c[k][s] += 1
        tot[s] += 1
    return c, tot


def entropia(test, m):
    c, tot = m
    base = (tot[1] + 0.5) / (tot[0] + tot[1] + 1)
    hc = hb = 0.0
    for ctx, s in test:
        p = None
        for k in ctx:
            n0, n1 = c.get(k, (0, 0))
            if n0 + n1 >= MIN:
                p = (n1 + 0.5) / (n0 + n1 + 1)
                break
        if p is None:
            p = base
        hc -= math.log2(p if s else 1 - p)
        hb -= math.log2(base if s else 1 - base)
    return hc, hb


def R(blocchi):
    """blocchi: lista di unita' (liste di righe); meta' alterne."""
    a = [r for i, b in enumerate(blocchi) if i % 2 == 0 for r in b]
    b = [r for i, b in enumerate(blocchi) if i % 2 == 1 for r in b]
    pa, pb = posizioni(a), posizioni(b)
    h1 = entropia(pb, modello(pa))
    h2 = entropia(pa, modello(pb))
    return 1 - (h1[0] + h2[0]) / (h1[1] + h2[1])


def main():
    rnd = random.Random(397)
    voy = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy, len(voy))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese.append(p)
            n += sum(len(r) for r in p)
        sub.append(R(prese))
    ris = OrderedDict([('Voynich', OrderedDict([('R_mediana', statistics.median(sub)), ('R', sub)]))])
    print('Voynich', sub, flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib += [righe[i:i + 25] for i in range(0, len(righe), 25)]
    ris['gibberish umano'] = OrderedDict([('R', R(gib))])
    print('gibberish', ris['gibberish umano'], flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = R([righe[i:i + 25] for i in range(0, len(righe), 25)])
    ris['testi sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]))
    Rv = ris['Voynich']['R_mediana']
    sopra = sum(1 for v in sens.values() if v >= Rv)
    esito = 'lo spazio del Voynich si prevede più che in tutte le lingue' if sopra == 0 else 'nella gamma delle lingue (%d testi su %d con R maggiore o uguale)' % (sopra, len(sens))
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e397_spazi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e397 — Lo spazio del Voynich si prevede dai segni intorno più che in una lingua?', '', 'Preregistrazione: `preregistrazioni/e397.md`. R = quota dell\'incertezza sugli spazi tolta da 2 segni a sinistra e 2 a destra.', '',
          'Voynich (5 sottoinsiemi da 10.000 parole): %s; mediana **%.3f**. Gibberish umano: **%.3f**.' % (', '.join('%.3f' % x for x in sub), Rv, ris['gibberish umano']['R']), '',
          '| testo sensato | R |', '|---|---|']
    md += ['| %s | %.3f |' % kv for kv in ris['testi sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e397_spazi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
