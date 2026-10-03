# -*- coding: utf-8 -*-
"""Esperimento e3a61: fra le K sequenze di segni piu' probabili per la catena di ordine 1 (stimata sui tipi), quante
sono parole attestate? Per lunghezze 3..7; Voynich, testi sensati, gibberish, generatori.

Preregistrazione: preregistrazioni/e3a61.md. Scrive risultati/e3a61_forme_riempite.json e .md.
"""
import heapq, json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
LUNGHEZZE = range(3, 8)


def modello(tipi):
    trans = defaultdict(Counter)
    for w in tipi:
        s = ('^',) + tuple(w) + ('$',)
        for a, b in zip(s, s[1:]):
            trans[a][b] += 1
    segni = sorted({x for w in tipi for x in w})
    V = len(segni) + 1
    lp = {}
    for a in ['^'] + segni:
        c = trans[a]
        n = sum(c.values())
        for b in segni + ['$']:
            lp[a, b] = math.log((c[b] + 0.5) / (n + 0.5 * V))
    return segni, lp


def migliori(segni, lp, L, K):
    """Le K sequenze di lunghezza L piu' probabili (ricerca A* esatta)."""
    # best[r][c]: massimo log-prob per aggiungere r segni dopo c e poi la fine
    best = [{c: lp[c, '$'] for c in segni}]
    for r in range(1, L):
        best.append({c: max(lp[c, d] + best[r - 1][d] for d in segni) for c in segni})
    coda = [(-(lp['^', c] + best[L - 1][c]), lp['^', c], (c,)) for c in segni]
    heapq.heapify(coda)
    out = []
    while coda and len(out) < K:
        _, g, pref = heapq.heappop(coda)
        if len(pref) == L:
            out.append(pref)
            continue
        if len(pref) == L - 1:
            # completamento: un segno e poi la fine
            pass
        rim = L - len(pref)
        c = pref[-1]
        for d in segni:
            g2 = g + lp[c, d]
            if len(pref) + 1 == L:
                heapq.heappush(coda, (-(g2 + lp[d, '$']), g2 + lp[d, '$'], pref + (d,)))
            else:
                heapq.heappush(coda, (-(g2 + best[rim - 1][d]), g2, pref + (d,)))
    return out


def riempimento(parole):
    tipi = set(tuple(w) for w in parole)
    segni, lp = modello(tipi)
    per_L = OrderedDict()
    hit = tot = 0
    for L in LUNGHEZZE:
        att = {w for w in tipi if len(w) == L}
        K = len(att)
        if K == 0:
            continue
        top = migliori(segni, lp, L, K)
        h = sum(1 for w in top if w in att)
        per_L[L] = OrderedDict([('K', K), ('presenti', h), ('quota', h / K)])
        hit += h
        tot += K
    return hit / tot, per_L


def main():
    rnd = random.Random(3161)
    voy_pag = e375.voynich()
    sub, dett = [], []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        q, pl = riempimento(prese)
        sub.append(q)
        dett.append(pl)
    ris = OrderedDict([('Voynich', OrderedDict([('riempimento', statistics.median(sub)), ('sottoinsiemi', sub), ('per_lunghezza_primo', dett[0])]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [w for l in z.read(nome).decode('utf-8', errors='ignore').splitlines() for w in (e381.parola(p) for p in l.split()) if w]
    q, pl = riempimento(gib)
    ris['gibberish umano'] = OrderedDict([('riempimento', q), ('per_lunghezza', pl)])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            q, pl = riempimento(e3a55.prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]))
            ris[k] = OrderedDict([('riempimento', q), ('per_lunghezza', pl)])
    q, pl = riempimento(e3a55.prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]))
    ris['Timm e Schinner, seme 1'] = OrderedDict([('riempimento', q), ('per_lunghezza', pl)])
    for k, x in ris.items():
        print(k, '%.3f' % x['riempimento'], flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        q, pl = riempimento(e3a55.prime(t))
        sens[k.replace('.txt', '')] = OrderedDict([('riempimento', q), ('per_lunghezza', pl)])
    vals = sorted(x['riempimento'] for x in sens.values())
    m = ris['Voynich']['riempimento']
    p10, p90 = float(np.percentile(vals, 10)), float(np.percentile(vals, 90))
    sotto = sum(1 for v in vals if v < m) / len(vals)
    esito = 'il vocabolario riempie le forme probabili più che nelle lingue' if m > p90 else ('come le lingue' if m >= p10 else 'meno')
    lingue = OrderedDict([('minimo', vals[0]), ('p10', p10), ('mediana', float(np.median(vals))), ('p90', p90), ('massimo', vals[-1]), ('quota_sotto_il_voynich', sotto)])
    out = OrderedDict([('altri', ris), ('lingue', lingue), ('testi_sensati', OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]['riempimento']))), ('esito', esito)])
    print(json.dumps(lingue), esito, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a61_forme_riempite.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a61 — Il vocabolario riempie le forme più probabili?', '', 'Preregistrazione: `preregistrazioni/e3a61.md`. Riempimento = quota delle K sequenze più probabili (K = tipi attestati di quella lunghezza, 3–7 segni) che sono parole attestate.', '',
          'Testi sensati: minimo %.3f, 10° percentile %.3f, mediana %.3f, 90° percentile %.3f, massimo %.3f. Il Voynich supera il %.0f%% dei testi sensati.' % (vals[0], p10, float(np.median(vals)), p90, vals[-1], 100 * sotto), '',
          '| testo | riempimento | per lunghezza (3, 4, 5, 6, 7) |', '|---|---|---|']
    for k, x in ris.items():
        pl = x.get('per_lunghezza', x.get('per_lunghezza_primo'))
        extra = ' (sottoinsiemi: %s)' % ', '.join('%.3f' % v for v in x['sottoinsiemi']) if 'sottoinsiemi' in x else ''
        md.append('| %s | %.3f%s | %s |' % (k, x['riempimento'], extra, ', '.join('%.2f' % pl[L]['quota'] if L in pl else '–' for L in LUNGHEZZE)))
    md += ['', '| testo sensato | riempimento | per lunghezza (3, 4, 5, 6, 7) |', '|---|---|---|']
    md += ['| %s | %.3f | %s |' % (k, x['riempimento'], ', '.join('%.2f' % x['per_lunghezza'][L]['quota'] if L in x['per_lunghezza'] else '–' for L in LUNGHEZZE)) for k, x in out['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a61_forme_riempite.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
