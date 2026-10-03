# -*- coding: utf-8 -*-
"""Esperimento e3a55: correlazione (dentro le classi di lunghezza) fra la probabilita' di forma di una parola (catena di
segni di ordine 1 stimata sui tipi) e la sua frequenza. Voynich, testi sensati, gibberish, generatori.

Preregistrazione: preregistrazioni/e3a55.md. Scrive risultati/e3a55_frequenza_forma.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from scipy.stats import rankdata

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)


def rho(parole):
    freq = Counter(parole)
    tipi = list(freq)
    trans = defaultdict(Counter)
    for w in tipi:
        s = ('^',) + tuple(w) + ('$',)
        for a, b in zip(s, s[1:]):
            trans[a][b] += 1
    alfabeto = {b for c in trans.values() for b in c}
    V = len(alfabeto)

    def lp(w):
        s = ('^',) + tuple(w) + ('$',)
        tot = 0.0
        for a, b in zip(s, s[1:]):
            c = trans[a]
            tot += math.log((c[b] + 0.5) / (sum(c.values()) + 0.5 * V))
        return tot / (len(w) + 1)
    usati = [w for w in tipi if freq[w] >= 2]
    per_l = defaultdict(list)
    for w in usati:
        per_l[len(w)].append(w)
    xs, ys = [], []
    for L, ws in per_l.items():
        if len(ws) < 5:
            continue
        a = rankdata([lp(w) for w in ws])
        b = rankdata([math.log(freq[w]) for w in ws])
        xs.extend(a - a.mean())
        ys.extend(b - b.mean())
    if len(xs) < 20:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def prime(righe, n=10000):
    out, k = [], 0
    for r in righe:
        if k >= n:
            break
        out += list(r)
        k += len(r)
    return out


def main():
    rnd = random.Random(3155)
    voy_pag = e375.voynich()
    voy = [w for p in voy_pag for r in p for w in r]
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        sub.append(rho(prese))
    ris = OrderedDict([('Voynich', OrderedDict([('rho', rho(voy)), ('rho_10000', sub), ('mediana_10000', statistics.median(sub))]))])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [w for l in z.read(nome).decode('utf-8', errors='ignore').splitlines() for w in (e381.parola(p) for p in l.split()) if w]
    ris['gibberish umano'] = OrderedDict([('rho', rho(gib))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            rr = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
            ris[k] = OrderedDict([('rho', rho(prime(rr)))])
    ris['Timm e Schinner, seme 1'] = OrderedDict([('rho', rho(prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])))])
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        v = rho(prime(t))
        if v is not None:
            sens[k.replace('.txt', '')] = v
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]))
    vals = list(sens.values())
    m = ris['Voynich']['mediana_10000']
    q = sum(1 for v in vals if v < m) / len(vals)
    esito = 'la frequenza segue la forma più che nelle lingue' if q > 0.9 else ('meno' if q < 0.1 else 'come nelle lingue')
    ris['percentile_voynich'] = q
    ris['lingue'] = [min(vals), statistics.median(vals), max(vals)]
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a55_frequenza_forma.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a55 — La frequenza delle parole si spiega con la probabilità della loro sequenza di segni?', '', 'Preregistrazione: `preregistrazioni/e3a55.md`. ρ = Spearman fra probabilità di forma e log della frequenza, dentro le classi di lunghezza.', '',
          'Voynich: ρ %.3f; a 10.000 parole %s (mediana %.3f), sopra il %.0f%% dei testi sensati (che vanno da %.3f a %.3f, mediana %.3f).' % (
              ris['Voynich']['rho'], ', '.join('%.3f' % v for v in sub), m, 100 * q, ris['lingue'][0], ris['lingue'][2], ris['lingue'][1]), '',
          '| testo | ρ |', '|---|---|']
    for k in ris:
        if k not in ('Voynich', 'testi_sensati', 'percentile_voynich', 'lingue', 'esito'):
            md.append('| %s | %s |' % (k, '%.3f' % ris[k]['rho'] if ris[k]['rho'] is not None else 'n.d.'))
    md += ['', '| testo sensato | ρ |', '|---|---|'] + ['| %s | %.3f |' % kv for kv in ris['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a55_frequenza_forma.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
