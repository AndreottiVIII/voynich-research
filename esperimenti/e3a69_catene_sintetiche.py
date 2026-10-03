# -*- coding: utf-8 -*-
"""Esperimento e3a69: catena di segni di ordine 2 (spazio e fine riga compresi) addestrata su ogni testo e lasciata
scrivere; quattro misure della notte (e3a55, e3a61, e3a58, e3a67) sul testo vero e sulla copia scritta dalla catena.

Preregistrazione: preregistrazioni/e3a69.md. Scrive risultati/e3a69_catene_sintetiche.json e .md.
"""
import bisect, json, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58
import e3a61_forme_riempite as e3a61
import e3a67_spazi_rifatti as e3a67

RISULTATI = os.path.join(QUI, '..', 'risultati')
SPAZIO, FINE, INIZIO = ' ', '$', '^'
MAX_SIMBOLI = 200
MISURE = ('rho frequenza-forma (e3a55)', 'riempimento (e3a61)', 'F1 degli spazi (e3a58)', 'tagli sbagliati che sono parole (e3a67)')


def catena(righe):
    c = defaultdict(Counter)
    for r in righe:
        s = [INIZIO, INIZIO]
        for j, w in enumerate(r):
            if j:
                s.append(SPAZIO)
            s += list(w)
        s.append(FINE)
        for a, b, x in zip(s, s[1:], s[2:]):
            c[a, b][x] += 1
    tab = {}
    for k, cc in c.items():
        simboli = list(cc)
        cum = list(np.cumsum([cc[x] for x in simboli]))
        tab[k] = (simboli, cum)
    return tab


def scrivi(tab, n_righe, rnd):
    out = []
    for _ in range(n_righe):
        a, b = INIZIO, INIZIO
        s = []
        while len(s) < MAX_SIMBOLI:
            simboli, cum = tab[a, b]
            x = simboli[bisect.bisect_right(cum, rnd.random() * cum[-1])]
            if x == FINE:
                break
            s.append(x)
            a, b = b, x
        parole, cur = [], []
        for x in s:
            if x == SPAZIO:
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


def misure(righe, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    parole = [w for r in righe for w in r]
    return OrderedDict([(MISURE[0], e3a55.rho(parole)), (MISURE[1], e3a61.riempimento(parole)[0]),
                        (MISURE[2], e3a58.f1(righe)), (MISURE[3], e3a67.attestazione(righe, rnd)[0])])


def coppia(righe, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    sint = scrivi(catena(righe), len(righe), rnd)
    return OrderedDict([('vero', misure(righe, rnd)), ('catena', misure(sint, rnd)), ('parole_catena', sum(len(r) for r in sint))])


def main():
    rnd = random.Random(3169)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(coppia(prese, rnd))
    voy = OrderedDict((lato, OrderedDict((m, statistics.median(s[lato][m] for s in sub)) for m in MISURE)) for lato in ('vero', 'catena'))
    print('Voynich', json.dumps(voy, ensure_ascii=False), flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    gibb = coppia(e3a58.righe_prime(gib), rnd)
    print('gibberish', json.dumps(gibb, ensure_ascii=False), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        sens[k.replace('.txt', '')] = coppia(e3a58.righe_prime(t), rnd)
    sintesi = OrderedDict()
    passate = 0
    cambi = []
    for m in MISURE:
        vere = [x['vero'][m] for x in sens.values() if x['vero'][m] is not None]
        cat = [x['catena'][m] for x in sens.values() if x['catena'][m] is not None]
        p90 = float(np.percentile(vere, 90))
        mc = float(np.median(cat))
        ok = mc > p90
        passate += ok
        rv = voy['catena'][m] / voy['vero'][m] if voy['vero'][m] else None
        if rv is None or abs(rv - 1) > 0.25:
            cambi.append(m)
        sintesi[m] = OrderedDict([('lingue_vere_mediana', float(np.median(vere))), ('lingue_vere_p90', p90), ('lingue_catena_mediana', mc),
                                  ('lingue_catena_sopra_p90', ok), ('voynich_vero', voy['vero'][m]), ('voynich_catena', voy['catena'][m]), ('rapporto_voynich', rv),
                                  ('gibberish_vero', gibb['vero'][m]), ('gibberish_catena', gibb['catena'][m])])
    es_a = 'le catene producono le proprietà del Voynich' if passate == 4 else ('in parte (%d misure su 4)' % passate if passate >= 2 else 'no')
    es_b = 'il Voynich non cambia' if not cambi else 'il Voynich cambia in: ' + ', '.join(cambi)
    out = OrderedDict([('sintesi', sintesi), ('Voynich_sottoinsiemi', sub), ('gibberish', gibb), ('testi_sensati', sens), ('esito_a', es_a), ('esito_b', es_b)])
    print(json.dumps(sintesi, ensure_ascii=False, indent=1), es_a, '/', es_b, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a69_catene_sintetiche.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%.3f' % v
    md = ['# e3a69 — Una catena di segni addestrata su una lingua produce le proprietà del Voynich?', '', 'Preregistrazione: `preregistrazioni/e3a69.md`. Catena di ordine 2 su segni, spazio e fine riga.', '',
          '| misura | lingue vere: mediana (90° perc.) | lingue riscritte dalla catena: mediana | Voynich vero | Voynich riscritto | gibberish vero | gibberish riscritto |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %.3f (%.3f) | %.3f | %s | %s | %s | %s |' % (m, x['lingue_vere_mediana'], x['lingue_vere_p90'], x['lingue_catena_mediana'], f(x['voynich_vero']), f(x['voynich_catena']), f(x['gibberish_vero']), f(x['gibberish_catena']))
           for m, x in sintesi.items()]
    md += ['', '| testo sensato | ' + ' | '.join('%s vero / catena' % m.split(' (')[0] for m in MISURE) + ' |', '|---|' + '---|' * len(MISURE)]
    md += ['| %s | %s |' % (k, ' | '.join('%s / %s' % (f(x['vero'][m]), f(x['catena'][m])) for m in MISURE)) for k, x in sens.items()]
    md += ['', 'Esito (a): **%s**. Esito (b): **%s**.' % (es_a, es_b)]
    open(os.path.join(RISULTATI, 'e3a69_catene_sintetiche.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
