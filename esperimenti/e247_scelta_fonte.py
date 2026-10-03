# -*- coding: utf-8 -*-
"""Esperimento 247: scarto orizzontale fra una parola e la sua fonte (ripetizione o variante a distanza 1) nella riga
sopra, con i riquadri di voynichese.com: concentrazione (M1) e struttura sequenziale (M2).

Preregistrazione: preregistrazioni/e247.md. Scrive risultati/e247_scelta_fonte.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e228_verticale_fisica as e228
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 247, 200
D = e237.D


def main():
    rnd = random.Random(SEME)
    pagine = e228.righe_con_riquadri()
    tutte = Counter(w for rr in pagine.values() for r in rr for w, _ in r if trascrizione.pulita(w))
    inventario = sorted({x for w in tutte for x in D(w)})
    coppie = []                       # (pagina, riga, j, delta, centri della riga sopra in unita' di pagina, centro parola)
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
                u = tuple(D(w))
                vic = e237.vicini(u, inventario) | {u}
                fonti = [cs for (x, cs), ux in zip(sopra, su) if ux in vic]
                if not fonti:
                    continue
                s = min(fonti, key=lambda cs: abs(cs - c))
                coppie.append((p, k, j, (c - s) / unita, [cs / unita for _, cs in sopra], c / unita))
    deltas = np.array([x[3] for x in coppie])
    med = float(np.median(np.abs(deltas)))
    nulli = []
    for _ in range(REPLICHE):
        nulli.append(float(np.median([abs(cw - rnd.choice(cs)) for _, _, _, _, cs, cw in coppie])))
    z1 = (med - statistics.mean(nulli)) / statistics.pstdev(nulli)

    def corr_consecutive(ds):
        a, b = [], []
        for (p1, k1, j1, d1, _, _), (p2, k2, j2, d2, _, _) in zip(ds, ds[1:]):
            if (p1, k1) == (p2, k2):
                a.append(d1)
                b.append(d2)
        return float(np.corrcoef(a, b)[0, 1]) if len(a) > 10 else None

    vero2 = corr_consecutive(coppie)
    per_riga = OrderedDict()
    for x in coppie:
        per_riga.setdefault((x[0], x[1]), []).append(x)
    nulli2 = []
    for _ in range(REPLICHE):
        mesc = []
        for v in per_riga.values():
            ds = [x[3] for x in v]
            rnd.shuffle(ds)
            mesc += [(x[0], x[1], x[2], d, x[4], x[5]) for x, d in zip(v, ds)]
        nulli2.append(corr_consecutive(mesc))
    z2 = (vero2 - statistics.mean(nulli2)) / statistics.pstdev(nulli2)
    bins = Counter(round(d * 2) / 2 for d in deltas)
    n = sum(bins.values())
    h = -sum(c / n * math.log2(c / n) for c in bins.values())
    esito = ('struttura nella scelta, da esaminare' if abs(z2) > 3 else 'scelta meccanica' if z1 < -3 and abs(z2) <= 2 else 'incerto')
    ris = OrderedDict([('coppie', len(coppie)), ('mediana_abs_delta', med), ('nullo_M1', statistics.mean(nulli)), ('z_M1', z1),
                       ('quota_entro_mezza_parola', float(np.mean(np.abs(deltas) <= 0.5))), ('M2_correlazione', vero2),
                       ('nullo_M2', statistics.mean(nulli2)), ('z_M2', z2), ('entropia_bit', h), ('bit_totali', h * n), ('esito', esito)])
    print(dict(ris), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e247_scelta_fonte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e247 — Un messaggio nella scelta di quale parola copiare?', '',
          'Scarto Δ (in passi di parola) fra una parola interna e la sua fonte più vicina (ripetizione o variante a distanza 1) nella riga sopra; '
          'riquadri di voynichese.com. Preregistrazione: `preregistrazioni/e247.md`.', '',
          '| misura | vera | nulla | z |', '|---|---|---|---|',
          '| M1: mediana di \\|Δ\\| | %.2f | %.2f | %.1f |' % (med, statistics.mean(nulli), z1),
          '| M2: correlazione fra Δ consecutivi nella riga | %.3f | %.3f | %.1f |' % (vero2, statistics.mean(nulli2), z2), '',
          'Coppie: %d; entro mezza parola: %.0f%%; entropia di Δ (a mezze parole): %.2f bit per coppia, %.0f bit in tutto.' % (
              len(coppie), 100 * ris['quota_entro_mezza_parola'], h, h * n), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e247_scelta_fonte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
