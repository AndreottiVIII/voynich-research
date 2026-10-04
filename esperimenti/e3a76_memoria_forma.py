# -*- coding: utf-8 -*-
"""Esperimento e3a76: rho frequenza-forma (come e3a55) con quattro modelli di forma (segni indipendenti, caselle, catena
di ordine 1, catena di ordine 2); taratura su lingue riscritte da catene di ordine 1 e 2 (e3a71).

Preregistrazione: preregistrazioni/e3a76.md. Scrive risultati/e3a76_memoria_forma.json e .md.
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
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58
import e3a71_catene_ordini as e3a71

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MODELLI = ('M0', 'MP', 'M1', 'M2')
FINE = '$'


def modelli(tipi):
    segni = sorted({x for w in tipi for x in w}) + [FINE]
    V = len(segni)
    c0 = Counter()
    cP = defaultdict(Counter)
    c1 = defaultdict(Counter)
    c2 = defaultdict(Counter)
    for w in tipi:
        s = list(w) + [FINE]
        prev = ('^', '^')
        for i, x in enumerate(s):
            c0[x] += 1
            cP[min(i, 3)][x] += 1
            c1[prev[1]][x] += 1
            c2[prev][x] += 1
            prev = (prev[1], x)
    n0 = sum(c0.values())

    def p0(x):
        return (c0[x] + 0.5) / (n0 + 0.5 * V)

    def interp(cc, x, base):
        n = sum(cc.values())
        lam = n / (n + 5)
        return lam * (cc[x] / n if n else 0) + (1 - lam) * base

    def lp(w, m):
        s = list(w) + [FINE]
        prev = ('^', '^')
        tot = 0.0
        for i, x in enumerate(s):
            b0 = p0(x)
            if m == 'M0':
                p = b0
            elif m == 'MP':
                p = interp(cP[min(i, 3)], x, b0)
            else:
                b1 = interp(c1[prev[1]], x, b0)
                p = b1 if m == 'M1' else interp(c2[prev], x, b1)
            tot += math.log(p)
            prev = (prev[1], x)
        return tot / len(s)
    return lp


def profilo(parole):
    freq = Counter(tuple(w) for w in parole)
    lp = modelli(list(freq))
    per_l = defaultdict(list)
    for w, n in freq.items():
        if n >= 2:
            per_l[len(w)].append(w)
    out = OrderedDict()
    for m in MODELLI:
        xs, ys = [], []
        for L, ws in per_l.items():
            if len(ws) < 5:
                continue
            a = rankdata([lp(w, m) for w in ws])
            b = rankdata([math.log(freq[w]) for w in ws])
            xs.extend(a - a.mean())
            ys.extend(b - b.mean())
        out[m] = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) >= 20 else None
    return out


def migliore(p):
    vv = {m: v for m, v in p.items() if v is not None}
    return max(vv, key=vv.get) if vv else None


def main():
    rnd = random.Random(3176)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        sub.append(profilo(prese))
    voy = OrderedDict((m, statistics.median(s[m] for s in sub)) for m in MODELLI)
    altri = OrderedDict([('Voynich', OrderedDict([('profilo', voy), ('migliore', migliore(voy)), ('sottoinsiemi', sub)]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [w for l in z.read(nome).decode('utf-8', errors='ignore').splitlines() for w in (e381.parola(p) for p in l.split()) if w]
    p = profilo(gib)
    altri['gibberish umano'] = OrderedDict([('profilo', p), ('migliore', migliore(p))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            p = profilo(e3a55.prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]))
            altri[k] = OrderedDict([('profilo', p), ('migliore', migliore(p))])
    p = profilo(e3a55.prime([[tuple(D(w)) for w in r] for pg in e337.pagine_ts(1) for r in pg]))
    altri['Timm e Schinner, seme 1'] = OrderedDict([('profilo', p), ('migliore', migliore(p))])
    for k, x in altri.items():
        print(k, json.dumps(x['profilo']), x['migliore'], flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe = [[tuple(w) for w in r] for r in e3a58.righe_prime(t) if r]
        x = OrderedDict([('vero', profilo([w for r in righe for w in r]))])
        for ordine_k in (1, 2):
            sint = e3a71.scrivi(e3a71.catena(righe, ordine_k), len(righe), ordine_k, rnd)
            x['catena %d' % ordine_k] = profilo([w for r in sint for w in r])
        sens[k.replace('.txt', '')] = x
    tar = OrderedDict()
    for ordine_k, atteso in ((1, 'M1'), (2, 'M2')):
        mm = [migliore(x['catena %d' % ordine_k]) for x in sens.values()]
        tar['catena %d' % ordine_k] = OrderedDict([('atteso', atteso), ('quota_giusta', mm.count(atteso) / len(mm)), ('conteggi', dict(Counter(mm)))])
    passa = all(x['quota_giusta'] >= 0.7 for x in tar.values())
    mv = altri['Voynich']['migliore']
    nomi = {'M1': 'memoria di un segno', 'M2': 'memoria di due segni', 'MP': 'caselle fisse', 'M0': 'segni indipendenti'}
    esito = nomi.get(mv, 'n.d.') if passa else 'test non informativo (la taratura non passa)'
    medie = OrderedDict((lato, OrderedDict((m, float(np.median([x[lato][m] for x in sens.values() if x[lato][m] is not None]))) for m in MODELLI)) for lato in ('vero', 'catena 1', 'catena 2'))
    out = OrderedDict([('taratura', tar), ('taratura_passa', passa), ('altri', altri), ('mediane_lingue', medie), ('testi_sensati', sens), ('esito', esito)])
    print(json.dumps(tar), json.dumps(medie), esito, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a76_memoria_forma.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%.3f' % v
    md = ['# e3a76 — Quale "memoria" spiega meglio le frequenze delle parole del Voynich?', '', 'Preregistrazione: `preregistrazioni/e3a76.md`. ρ come nell\'e3a55 con quattro modelli di forma.', '',
          '## Taratura', '', '| testi | modello atteso | quota con il modello atteso come migliore | conteggi |', '|---|---|---|---|']
    md += ['| lingue riscritte, %s | %s | %.2f | %s |' % (k, x['atteso'], x['quota_giusta'], ', '.join('%s %d' % kv for kv in sorted(x['conteggi'].items(), key=lambda kv: str(kv[0])))) for k, x in tar.items()]
    md += ['', 'Taratura: **%s**.' % ('passa' if passa else 'non passa'), '', '## Profili', '', '| testo | M0 | MP | M1 | M2 | migliore |', '|---|---|---|---|---|---|']
    md += ['| %s | %s | %s |' % (k, ' | '.join(f(x['profilo'][m]) for m in MODELLI), x['migliore']) for k, x in altri.items()]
    md += ['| lingue vere (mediana) | %s | |' % ' | '.join(f(medie['vero'][m]) for m in MODELLI),
           '| lingue riscritte, ordine 1 (mediana) | %s | |' % ' | '.join(f(medie['catena 1'][m]) for m in MODELLI),
           '| lingue riscritte, ordine 2 (mediana) | %s | |' % ' | '.join(f(medie['catena 2'][m]) for m in MODELLI)]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a76_memoria_forma.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
