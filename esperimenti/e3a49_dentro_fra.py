# -*- coding: utf-8 -*-
"""Esperimento e3a49: correlazione fra la PMI delle coppie di segni dentro le parole e la PMI delle coppie (ultimo, primo)
fra parole vicine; Voynich, testi sensati (parole intere), gibberish umano.

Preregistrazione: preregistrazioni/e3a49.md. Scrive risultati/e3a49_dentro_fra.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

from scipy.stats import spearmanr

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')


def pmi(c):
    n = sum(c.values())
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k
    return {(a, b): math.log(k * n / (sa[a] * sb[b])) for (a, b), k in c.items()}


def rho(righe):
    dentro, fra = Counter(), Counter()
    for r in righe:
        for w in r:
            dentro.update(zip(w, w[1:]))
        fra.update((a[-1], b[0]) for a, b in zip(r, r[1:]))
    pd, pf = pmi(dentro), pmi(fra)
    celle = [k for k in pd if dentro[k] >= 5 and fra.get(k, 0) >= 5]
    if len(celle) < 5:
        return None, len(celle)
    return float(spearmanr([pd[k] for k in celle], [pf[k] for k in celle]).correlation), len(celle)


def main():
    rnd = random.Random(3149)
    voy_pag = e375.voynich()
    voy = [r for p in voy_pag for r in p]
    ris = OrderedDict()
    r_all, n_all = rho(voy)
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(rho(prese)[0])
    ris['Voynich'] = OrderedDict([('rho', r_all), ('celle', n_all), ('rho_10000', sub), ('mediana_10000', statistics.median(sub))])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
    rg, ng = rho(gib)
    ris['gibberish umano'] = OrderedDict([('rho', rg), ('celle', ng)])
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        rr, nn = rho(righe)
        if rr is not None:
            sens[k.replace('.txt', '')] = OrderedDict([('rho', rr), ('celle', nn)])
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]['rho']))
    vals = [x['rho'] for x in sens.values()]
    mv = ris['Voynich']['mediana_10000']
    sotto = sum(1 for v in vals if v < mv) / len(vals)
    esito = 'la giuntura ricalca le sequenze interne più che nelle lingue' if sotto > 0.9 else ('meno che nelle lingue' if sotto < 0.1 else 'come nelle lingue')
    ris['percentile_voynich'] = sotto
    ris['esito'] = esito
    print(json.dumps(OrderedDict([('Voynich', ris['Voynich']), ('gibberish', ris['gibberish umano']), ('percentile', sotto), ('esito', esito)]), ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a49_dentro_fra.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a49 — La giuntura fra parole ricalca le sequenze di segni dentro le parole?', '', 'Preregistrazione: `preregistrazioni/e3a49.md`. ρ = Spearman fra PMI dentro le parole e PMI fra parole, sulle celle comuni.', '',
          'Voynich: ρ %.3f (%d celle); a 10.000 parole %s (mediana %.3f), sopra il %.0f%% dei testi sensati. Gibberish umano: ρ %s (%d celle).' % (
              r_all, n_all, ', '.join('%.3f' % x for x in sub), mv, 100 * sotto, '%.3f' % rg if rg is not None else 'n.d.', ng), '',
          '| testo sensato | ρ | celle |', '|---|---|---|']
    md += ['| %s | %.3f | %d |' % (k, x['rho'], x['celle']) for k, x in ris['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a49_dentro_fra.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
