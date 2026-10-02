# -*- coding: utf-8 -*-
"""Esperimento 190: come l'e184, con una maschera del disegno per distanza di colore dalla pergamena locale e
caratteristiche di forma (profili, proporzioni, radici, foglie, colore dei fiori).

Preregistrazione: preregistrazioni/e190.md. Scrive risultati/e190_piante_vocabolario_bis.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e148_bifogli as e148
import e154b_ordine_normalizzato as e154b
import e166_intinte as e166
import e173_dimensione_scrittura as e173

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, MIN_PAROLE = 190, 1000, 50
NOMI = ['area', 'verde'] + ['fascia orizz. %d' % i for i in range(6)] + ['fascia vert. %d' % i for i in range(4)] + ['proporzioni', 'radici', 'foglie', 'colore cos', 'colore sin']


def caratteristiche(pag):
    d = json.load(open(os.path.join(e34.RIQUADRI, pag + '.js'), encoding='utf-8'))
    im = Image.open(os.path.join(e166.IMMAGINI, pag + '.jpg')).convert('RGB')
    A = np.asarray(im).astype(float)
    F = np.stack([np.asarray(c.filter(ImageFilter.MedianFilter(61))).astype(float) for c in im.split()], axis=-1)
    dist = np.sqrt(((A - F) ** 2).sum(axis=-1))
    H = np.asarray(im.convert('HSV').split()[0]).astype(float)
    h, w = dist.shape
    fuori = np.ones((h, w), bool)
    for e in d[1]:
        fuori[max(0, e[2] - 4):min(h, e[2] + e[4] + 4), max(0, e[1] - 4):min(w, e[1] + e[3] + 4)] = False
    dis = fuori & (dist > 35)
    lab, n = ndimage.label(dis)
    if n:
        dim = ndimage.sum(dis, lab, range(1, n + 1))
        dis = np.isin(lab, 1 + np.nonzero(dim >= 50)[0])
    verde = dis & (H >= 50) & (H <= 150) & ((A[..., 1] + A[..., 2]) / 2 > A[..., 0])
    tot = max(1, int(dis.sum()))
    f = [tot / (h * w), verde.sum() / tot]
    for i in range(6):
        f.append(dis[i * h // 6:(i + 1) * h // 6].sum() / tot)
    for j in range(4):
        f.append(dis[:, j * w // 4:(j + 1) * w // 4].sum() / tot)
    ys, xs = np.nonzero(dis)
    if len(ys) > 10:
        f.append((np.percentile(ys, 95) - np.percentile(ys, 5) + 1) / (np.percentile(xs, 95) - np.percentile(xs, 5) + 1))
    else:
        f.append(1.0)
    basso = dis[2 * h // 3:] & ~verde[2 * h // 3:]
    f.append(basso.sum() / tot)
    lv, nv = ndimage.label(verde)
    nfoglie = int((ndimage.sum(verde, lv, range(1, nv + 1)) >= 30).sum()) if nv else 0
    f.append(math.log1p(nfoglie))
    nv_mask = dis & ~verde
    ang = H[nv_mask] / 255 * 2 * math.pi
    f += [float(np.cos(ang).mean()) if ang.size else 0.0, float(np.sin(ang).mean()) if ang.size else 0.0]
    return [float(x) for x in f]


def main():
    rnd = random.Random(SEME)
    var = e148.variabili_pagine()
    parole = defaultdict(Counter)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.sezione == 'H':
            parole[r.pagina].update(e154b.normalizza(w) for w in r.parole if trascrizione.pulita(w))
    pagine = [p for p, c in parole.items() if sum(c.values()) >= MIN_PAROLE and os.path.exists(os.path.join(e34.RIQUADRI, p + '.js'))
              and os.path.exists(os.path.join(e166.IMMAGINI, p + '.jpg')) and p in var and 'Q' in var[p] and 'H' in var[p] and 'L' in var[p]]
    grezze = {p: caratteristiche(p) for p in pagine}
    M = np.array([grezze[p] for p in pagine])
    M = (M - M.mean(axis=0)) / np.where(M.std(axis=0) > 0, M.std(axis=0), 1)
    F = {p: M[i] for i, p in enumerate(pagine)}
    gruppo = {p: (var[p]['H'], var[p]['L']) for p in pagine}
    coppie = [(a, b) for i, a in enumerate(pagine) for b in pagine[i + 1:] if gruppo[a] == gruppo[b] and var[a]['Q'] != var[b]['Q']]
    dv = [1 - e148.coseno(parole[a], parole[b]) for a, b in coppie]
    per_g = defaultdict(list)
    for p in pagine:
        per_g[gruppo[p]].append(p)

    def stat(ass, j=None):
        if j is None:
            di = [float(np.linalg.norm(F[ass[a]] - F[ass[b]])) for a, b in coppie]
        else:
            di = [abs(float(F[ass[a]][j] - F[ass[b]][j])) for a, b in coppie]
        return e173.spearman(di, dv)
    ident = {p: p for p in pagine}
    vero = stat(ident)
    nulli = []
    for _ in range(PERMUTAZIONI):
        ass = {}
        for g, pp in per_g.items():
            q = pp[:]
            rnd.shuffle(q)
            ass.update(zip(pp, q))
        nulli.append(stat(ass))
    p = (1 + sum(n >= vero for n in nulli)) / (1 + PERMUTAZIONI)
    esito = 'il vocabolario segue la pianta' if vero > 0 and p < 0.01 else ('nessun legame' if p > 0.05 else 'incerto')
    singole = OrderedDict((NOMI[j], stat(ident, j)) for j in range(len(NOMI)))
    ris = OrderedDict([('pagine', len(pagine)), ('coppie', len(coppie)), ('spearman', vero), ('nullo_media', statistics.mean(nulli)), ('p', p),
                       ('per_caratteristica', singole), ('esito', esito)])
    print('pagine %d coppie %d | Spearman %.3f (nullo %.3f) p %.4f | %s | singole %s' % (len(pagine), len(coppie), vero, statistics.mean(nulli), p, esito,
          {k: round(v, 3) for k, v in singole.items()}), flush=True)
    with open(os.path.join(RISULTATI, 'e190_piante_vocabolario_bis.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e190 — Piante simili, vocabolario simile? (misura del disegno migliore)', '', 'Preregistrazione: `preregistrazioni/e190.md`.', '',
           '| pagine | coppie | Spearman | nullo | p |', '|---|---|---|---|---|', '| %d | %d | %.3f | %.3f | %.4f |' % (len(pagine), len(coppie), vero, statistics.mean(nulli), p), '',
           'Per caratteristica (Spearman, descrittivo): ' + ', '.join('%s %.3f' % kv for kv in singole.items()) + '.', '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e190_piante_vocabolario_bis.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
