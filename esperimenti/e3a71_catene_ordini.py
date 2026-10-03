# -*- coding: utf-8 -*-
"""Esperimento e3a71: l'e3a69 con catene di ordine 1 e 3.

Preregistrazione: preregistrazioni/e3a71.md. Scrive risultati/e3a71_catene_ordini.json e .md.
"""
import bisect, json, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e381_parole_intere as e381
import e3a58_spazi_prevedibili as e3a58
import e3a69_catene_sintetiche as e3a69

RISULTATI = os.path.join(QUI, '..', 'risultati')
S, F, I = e3a69.SPAZIO, e3a69.FINE, e3a69.INIZIO
MISURE = e3a69.MISURE


def catena(righe, k):
    c = defaultdict(Counter)
    for r in righe:
        s = [I] * k
        for j, w in enumerate(r):
            if j:
                s.append(S)
            s += list(w)
        s.append(F)
        for i in range(k, len(s)):
            c[tuple(s[i - k:i])][s[i]] += 1
    return {ctx: (list(cc), list(np.cumsum(list(cc.values())))) for ctx, cc in c.items()}


def scrivi(tab, n_righe, k, rnd):
    out = []
    for _ in range(n_righe):
        ctx = (I,) * k
        s = []
        while len(s) < e3a69.MAX_SIMBOLI:
            simboli, cum = tab[ctx]
            x = simboli[bisect.bisect_right(cum, rnd.random() * cum[-1])]
            if x == F:
                break
            s.append(x)
            ctx = ctx[1:] + (x,)
        parole, cur = [], []
        for x in s:
            if x == S:
                if cur:
                    parole.append(tuple(cur))
                cur = []
            else:
                cur.append(x)
        if cur:
            parole.append(tuple(cur))
        if parole:
            out.append(parole)
    return out


def coppia(righe, k, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    sint = scrivi(catena(righe, k), len(righe), k, rnd)
    return OrderedDict([('vero', e3a69.misure(righe, rnd)), ('catena', e3a69.misure(sint, rnd))])


def main():
    rnd = random.Random(3171)
    voy_pag = e375.voynich()
    gib = []
    with zipfile.ZipFile(os.path.join(e3a69.e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    gib = e3a58.righe_prime(gib)
    sens_righe = OrderedDict((k.replace('.txt', ''), e3a58.righe_prime(t)) for k, t in e381.testi().items())
    out = OrderedDict()
    for k in (1, 3):
        sub = []
        for _ in range(5):
            ordine = rnd.sample(voy_pag, len(voy_pag))
            prese, n = [], 0
            for p in ordine:
                if n >= 10000:
                    break
                prese += p
                n += sum(len(r) for r in p)
            sub.append(coppia(prese, k, rnd))
        voy = OrderedDict((lato, OrderedDict((m, statistics.median(s[lato][m] for s in sub)) for m in MISURE)) for lato in ('vero', 'catena'))
        gibb = coppia(gib, k, rnd)
        sens = OrderedDict((nome, coppia(rr, k, rnd)) for nome, rr in sens_righe.items())
        sintesi, passate, cambi = OrderedDict(), 0, []
        for m in MISURE:
            vere = [x['vero'][m] for x in sens.values() if x['vero'][m] is not None]
            cat = [x['catena'][m] for x in sens.values() if x['catena'][m] is not None]
            p90 = float(np.percentile(vere, 90))
            mc = float(np.median(cat))
            passate += mc > p90
            rv = voy['catena'][m] / voy['vero'][m] if voy['vero'][m] else None
            if rv is None or abs(rv - 1) > 0.25:
                cambi.append(m)
            sintesi[m] = OrderedDict([('lingue_vere_mediana', float(np.median(vere))), ('lingue_vere_p90', p90), ('lingue_catena_mediana', mc),
                                      ('voynich_vero', voy['vero'][m]), ('voynich_catena', voy['catena'][m]), ('rapporto_voynich', rv),
                                      ('gibberish_vero', gibb['vero'][m]), ('gibberish_catena', gibb['catena'][m])])
        es_a = 'le catene producono le proprietà del Voynich' if passate == 4 else ('in parte (%d misure su 4)' % passate if passate >= 2 else 'no')
        es_b = 'il Voynich non cambia' if not cambi else 'il Voynich cambia in: ' + ', '.join(cambi)
        out['ordine %d' % k] = OrderedDict([('sintesi', sintesi), ('esito_a', es_a), ('esito_b', es_b), ('passate', passate), ('cambi', cambi), ('testi_sensati', sens)])
        print('ordine', k, json.dumps(sintesi, ensure_ascii=False), es_a, '/', es_b, flush=True)
    regge = all(x['esito_b'] == 'il Voynich non cambia' and x['passate'] >= 2 for x in out.values())
    out['esito'] = 'l\'e3a69 regge' if regge else 'l\'e3a69 non regge con tutti gli ordini'
    json.dump(out, open(os.path.join(RISULTATI, 'e3a71_catene_ordini.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%.3f' % v
    md = ['# e3a71 — L\'e3a69 regge con catene di ordine 1 e di ordine 3?', '', 'Preregistrazione: `preregistrazioni/e3a71.md`. Valori dell\'ordine 2 nell\'e3a69.', '']
    for k, x in out.items():
        if k == 'esito':
            continue
        md += ['## %s' % k, '', '| misura | lingue vere: mediana (90° perc.) | lingue riscritte | Voynich vero | Voynich riscritto | gibberish vero / riscritto |', '|---|---|---|---|---|---|']
        md += ['| %s | %.3f (%.3f) | %.3f | %s | %s | %s / %s |' % (m, y['lingue_vere_mediana'], y['lingue_vere_p90'], y['lingue_catena_mediana'], f(y['voynich_vero']), f(y['voynich_catena']), f(y['gibberish_vero']), f(y['gibberish_catena']))
               for m, y in x['sintesi'].items()]
        md += ['', 'Esito (a): **%s**. Esito (b): **%s**.' % (x['esito_a'], x['esito_b']), '']
    md += ['Esito complessivo: **%s**.' % out['esito']]
    open(os.path.join(RISULTATI, 'e3a71_catene_ordini.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
