# -*- coding: utf-8 -*-
"""Esperimento 184: distanza fra disegni delle piante (caratteristiche grezze dalle immagini di voynichese.com, fuori
dai riquadri delle parole) contro distanza di vocabolario, fra pagine d'erbario dello stesso gruppo e di fascicoli
diversi (Mantel per strati).

Preregistrazione: preregistrazioni/e184.md. Scrive risultati/e184_piante_vocabolario.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from PIL import Image

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
SEME, PERMUTAZIONI, MIN_PAROLE, MARGINE = 184, 1000, 50, 4


def caratteristiche(pag):
    d = json.load(open(os.path.join(e34.RIQUADRI, pag + '.js'), encoding='utf-8'))
    im = Image.open(os.path.join(e166.IMMAGINI, pag + '.jpg')).convert('RGB')
    hsv = np.asarray(im.convert('HSV')).astype(float)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h, w = V.shape
    fuori = np.ones((h, w), bool)
    for e in d[1]:
        fuori[max(0, e[2] - MARGINE):min(h, e[2] + e[4] + MARGINE), max(0, e[1] - MARGINE):min(w, e[1] + e[3] + MARGINE)] = False
    med = float(np.median(V))
    colorato = (S > 60) & fuori
    disegno = (colorato | ((V < 0.7 * med) & fuori))
    n_col = max(1, int(colorato.sum()))
    verde = colorato & (H >= 40) & (H <= 110)
    rosso = colorato & ((H < 25) | (H > 230))
    blu = colorato & (H > 130) & (H <= 190)
    f = [verde.sum() / n_col, rosso.sum() / n_col, blu.sum() / n_col]
    ist, _ = np.histogram(H[colorato], bins=12, range=(0, 256))
    f += list(ist / n_col)
    tot = max(1, int(disegno.sum()))
    for i in range(4):
        for j in range(4):
            f.append(disegno[i * h // 4:(i + 1) * h // 4, j * w // 4:(j + 1) * w // 4].sum() / tot)
    ys = np.nonzero(verde)[0]
    f += [float(ys.mean() / h) if len(ys) else 0.5, float(ys.std() / h) if len(ys) else 0.0]
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
    F = {p: caratteristiche(p) for p in pagine}
    M = np.array([F[p] for p in pagine])
    M = (M - M.mean(axis=0)) / np.where(M.std(axis=0) > 0, M.std(axis=0), 1)
    F = {p: M[i] for i, p in enumerate(pagine)}
    gruppo = {p: (var[p]['H'], var[p]['L']) for p in pagine}
    coppie = [(a, b) for i, a in enumerate(pagine) for b in pagine[i + 1:] if gruppo[a] == gruppo[b] and var[a]['Q'] != var[b]['Q']]
    dv = [1 - e148.coseno(parole[a], parole[b]) for a, b in coppie]

    def stat(assegna):
        di = [float(np.linalg.norm(F[assegna[a]] - F[assegna[b]])) for a, b in coppie]
        return e173.spearman(di, dv)
    ident = {p: p for p in pagine}
    vero = stat(ident)
    per_g = defaultdict(list)
    for p in pagine:
        per_g[gruppo[p]].append(p)
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
    ris = OrderedDict([('pagine', len(pagine)), ('gruppi', {('%s/%s' % g): len(v) for g, v in per_g.items()}), ('coppie', len(coppie)),
                       ('spearman', vero), ('nullo_media', statistics.mean(nulli)), ('p', p), ('esito', esito)])
    print('pagine %d gruppi %s coppie %d | Spearman %.3f (nullo %.3f) p %.4f | %s' % (len(pagine), ris['gruppi'], len(coppie), vero, statistics.mean(nulli), p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e184_piante_vocabolario.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e184 — Piante simili, vocabolario simile?', '',
           'Spearman fra distanza dei disegni (colori e forma, fuori dai riquadri) e distanza di vocabolario, per coppie di pagine d\'erbario dello stesso gruppo '
           'e di fascicoli diversi; nullo: permutazione dei disegni dentro il gruppo. Preregistrazione: `preregistrazioni/e184.md`.', '',
           '| pagine | coppie | Spearman | nullo | p |', '|---|---|---|---|---|', '| %d | %d | %.3f | %.3f | %.4f |' % (len(pagine), len(coppie), vero, statistics.mean(nulli), p),
           '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e184_piante_vocabolario.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
