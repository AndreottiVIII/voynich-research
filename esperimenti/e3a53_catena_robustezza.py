# -*- coding: utf-8 -*-
"""Esperimento e3a53: e3a49 con gli spazi incerti uniti, e senza le coppie fra parole che coinvolgono parole di al massimo
2 segni (anche nelle lingue).

Preregistrazione: preregistrazioni/e3a53.md. Scrive risultati/e3a53_catena_robustezza.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

from scipy.stats import spearmanr

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e381_parole_intere as e381
import e3a49_dentro_fra as e3a49

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MAX_E3A49 = 0.392


def rho_senza_corte(righe):
    dentro, fra = Counter(), Counter()
    for r in righe:
        for w in r:
            dentro.update(zip(w, w[1:]))
        fra.update((a[-1], b[0]) for a, b in zip(r, r[1:]) if len(a) >= 3 and len(b) >= 3)
    pd, pf = e3a49.pmi(dentro), e3a49.pmi(fra)
    celle = [k for k in pd if dentro[k] >= 5 and fra.get(k, 0) >= 5]
    if len(celle) < 5:
        return None
    return float(spearmanr([pd[k] for k in celle], [pf[k] for k in celle]).correlation)


def pagine_zl(virgola_spazio):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL', virgola_spazio=virgola_spazio)):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per.setdefault(r.pagina, []).append(ws)
    return list(per.values())


def mediana_sub(pp, f, rnd):
    sub = []
    for _ in range(5):
        ordine = rnd.sample(pp, len(pp))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        v = f(prese)
        if v is not None:
            sub.append(v)
    return sub, statistics.median(sub)


def main():
    rnd = random.Random(3153)
    ris = OrderedDict()
    s1, m1 = mediana_sub(pagine_zl(False), lambda rr: e3a49.rho(rr)[0], rnd)
    ris['1 ZL, spazi incerti uniti'] = OrderedDict([('rho_10000', s1), ('mediana', m1), ('soglia', MAX_E3A49), ('esito', 'regge' if m1 > MAX_E3A49 else 'non regge')])
    s2, m2 = mediana_sub(pagine_zl(True), rho_senza_corte, rnd)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        v = rho_senza_corte(righe)
        if v is not None:
            sens[k.replace('.txt', '')] = v
    mx = max(sens.values())
    ris['2 ZL, senza coppie con parole di 1-2 segni'] = OrderedDict([('rho_10000', s2), ('mediana', m2), ('soglia', mx), ('esito', 'regge' if m2 > mx else 'non regge')])
    ris['3 lingue, stessa regola'] = OrderedDict([('max', mx), ('mediana', statistics.median(sens.values())), ('testi', len(sens)), ('primi', sorted(sens.items(), key=lambda kv: -kv[1])[:5])])
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a53_catena_robustezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a53 — La "catena con spazi deboli" regge senza spazi incerti e senza parole corte?', '', 'Preregistrazione: `preregistrazioni/e3a53.md`.', '',
          '| variante | ρ a 10.000 parole | mediana | soglia (massimo delle lingue) | esito |', '|---|---|---|---|---|']
    for k in ('1 ZL, spazi incerti uniti', '2 ZL, senza coppie con parole di 1-2 segni'):
        x = ris[k]
        md.append('| %s | %s | %.3f | %.3f | %s |' % (k, ', '.join('%.3f' % v for v in x['rho_10000']), x['mediana'], x['soglia'], x['esito']))
    l = ris['3 lingue, stessa regola']
    md += ['', 'Lingue con la regola 2 (%d testi): mediana %.3f, massimo %.3f; i più alti: %s.' % (l['testi'], l['mediana'], l['max'], '; '.join('%s %.3f' % kv for kv in l['primi']))]
    open(os.path.join(RISULTATI, 'e3a53_catena_robustezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
