# -*- coding: utf-8 -*-
"""Esperimento 247b: le fonti di parole consecutive sono parole consecutive della riga sopra (passo +1)? E la
correlazione degli scarti dell'e247 resta sulle coppie che non sono a passo 0 o +1?

Preregistrazione: preregistrazioni/e247b.md. Scrive risultati/e247b_copia_in_sequenza.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e228_verticale_fisica as e228
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 2471, 200
D = e237.D


def coppie_con_indice():
    pagine = e228.righe_con_riquadri()
    tutte = Counter(w for rr in pagine.values() for r in rr for w, _ in r if trascrizione.pulita(w))
    inventario = sorted({x for w in tutte for x in D(w)})
    per_riga = OrderedDict()               # (pagina, riga) -> [(j, indice fonte, delta)]
    for p, rr in pagine.items():
        passi = [b[1] - a[1] for r in rr for a, b in zip(r, r[1:]) if a[1] is not None and b[1] is not None and b[1] > a[1]]
        if len(passi) < 10:
            continue
        unita = statistics.median(passi)
        for k in range(1, len(rr)):
            sopra = [(w, c) for w, c in rr[k - 1] if c is not None and trascrizione.pulita(w)]
            if len(sopra) < 2:
                continue
            su = [tuple(D(w)) for w, _ in sopra]
            for j in range(1, len(rr[k]) - 1):
                w, c = rr[k][j]
                if c is None or not trascrizione.pulita(w):
                    continue
                vic = e237.vicini(tuple(D(w)), inventario) | {tuple(D(w))}
                fonti = [t for t, ux in enumerate(su) if ux in vic]
                if not fonti:
                    continue
                t = min(fonti, key=lambda t: abs(sopra[t][1] - c))
                per_riga.setdefault((p, k), []).append((j, t, (c - sopra[t][1]) / unita))
    return per_riga


def passi(per_riga):
    out = Counter()
    for v in per_riga.values():
        for (j1, t1, _), (j2, t2, _) in zip(v, v[1:]):
            if j2 == j1 + 1:
                out[t2 - t1] += 1
    return out


def main():
    rnd = random.Random(SEME)
    pr = coppie_con_indice()
    vero = passi(pr)
    n = sum(vero.values())
    nulli = []
    for _ in range(REPLICHE):
        m = OrderedDict()
        for key, v in pr.items():
            ts = [(t, d) for _, t, d in v]
            rnd.shuffle(ts)
            m[key] = [(j, t, d) for (j, _, _), (t, d) in zip(v, ts)]
        nulli.append(passi(m))
    ris = OrderedDict([('coppie_consecutive', n)])
    for s in (0, 1, 2):
        q = vero[s] / n
        qs = [x[s] / max(1, sum(x.values())) for x in nulli]
        ris['passo %+d' % s] = OrderedDict([('quota', q), ('nulla', statistics.mean(qs)), ('z', (q - statistics.mean(qs)) / statistics.pstdev(qs))])

    def corr_resto(prr, tieni):
        a, b = [], []
        for key, v in prr.items():
            for x, y in zip(v, v[1:]):
                if y[0] == x[0] + 1 and tieni(key, x, y):
                    a.append(x[2])
                    b.append(y[2])
        return float(np.corrcoef(a, b)[0, 1]) if len(a) > 10 else None, len(a)

    resto = {(key, x[0]) for key, v in pr.items() for x, y in zip(v, v[1:]) if y[0] == x[0] + 1 and (y[1] - x[1]) not in (0, 1)}
    c_vera, n_resto = corr_resto(pr, lambda key, x, y: (key, x[0]) in resto)
    cn = []
    for _ in range(REPLICHE):
        m = OrderedDict()
        for key, v in pr.items():
            ds = [d for _, _, d in v]
            rnd.shuffle(ds)
            m[key] = [(j, t, d) for (j, t, _), d in zip(v, ds)]
        cn.append(corr_resto(m, lambda key, x, y: (key, x[0]) in resto)[0])
    zb = (c_vera - statistics.mean(cn)) / statistics.pstdev(cn)
    ris['B_correlazione_resto'] = OrderedDict([('coppie', n_resto), ('vera', c_vera), ('nulla', statistics.mean(cn)), ('z', zb)])
    za = ris['passo +1']['z']
    esito = ('copia in sequenza' if za > 3 and abs(zb) <= 2 else 'struttura non spiegata, da esaminare ancora' if abs(zb) > 3 else 'incerto')
    ris['distribuzione_passi'] = {str(k): v for k, v in sorted(vero.items()) if -4 <= k <= 4}
    ris['esito'] = esito
    print(json.dumps(ris, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e247b_copia_in_sequenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e247b — La struttura dell\'e247 è copia "in sequenza" della riga sopra?', '',
          'Coppie di parole consecutive con fonte nella riga sopra: %d. Passo = indice della fonte della seconda − indice della fonte della prima. '
          'Preregistrazione: `preregistrazioni/e247b.md`.' % n, '', '| misura | vera | nulla | z |', '|---|---|---|---|']
    for s in (0, 1, 2):
        r = ris['passo %+d' % s]
        md.append('| quota a passo %+d | %.3f | %.3f | %.1f |' % (s, r['quota'], r['nulla'], r['z']))
    b = ris['B_correlazione_resto']
    md.append('| B: correlazione dei Δ, coppie non a passo 0 o +1 (%d) | %.3f | %.3f | %.1f |' % (b['coppie'], b['vera'], b['nulla'], b['z']))
    md += ['', 'Distribuzione dei passi da −4 a +4: %s.' % ris['distribuzione_passi'], '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e247b_copia_in_sequenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
