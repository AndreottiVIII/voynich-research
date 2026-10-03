# -*- coding: utf-8 -*-
"""Esperimento 260: misure fisiche della scrittura dai riquadri di voynichese.com (altezza, passo di riga, spazio fra parole,
larghezza per unita', inclinazione, variabilita' dell'altezza) distinguono le mani ($H) dentro lingua x sezione?

Preregistrazione: preregistrazioni/e260.md. Scrive risultati/e260_scribi_tratto.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e237_riuso_pagina as e237
import e244_scribi_procedimento as e244

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_RIQUADRI = 60
D = e237.D


def misure(foglio):
    percorso = os.path.join(e34.RIQUADRI, foglio + '.js')
    if not os.path.exists(percorso):
        return None
    d = json.load(open(percorso, encoding='utf-8'))
    voc = [v[0] for v in d[0]]
    righe, cur, prima = [], [], None
    for e in d[1]:
        if prima is not None and e[1] < prima - 3:
            righe.append(cur)
            cur = []
        cur.append((voc[e[0]], e[1], e[2], e[3], e[4]))
        prima = e[1]
    if cur:
        righe.append(cur)
    tutte = [b for r in righe for b in r]
    if len(tutte) < MIN_RIQUADRI:
        return None
    h = statistics.median(b[4] for b in tutte)
    if h <= 0:
        return None
    ys = [statistics.median(b[2] + b[4] / 2 for b in r) for r in righe if len(r) >= 2]
    passi = [b - a for a, b in zip(ys, ys[1:]) if 0 < b - a < 5 * h]
    spazi = [r[i + 1][1] - (r[i][1] + r[i][3]) for r in righe for i in range(len(r) - 1)]
    spazi = [s for s in spazi if 0 <= s < 5 * h]
    larg = [b[3] / max(1, len(D(b[0]))) for b in tutte if b[0]]
    pend = []
    for r in righe:
        if len(r) >= 4:
            x = np.array([b[1] + b[3] / 2 for b in r])
            y = np.array([b[2] + b[4] / 2 for b in r])
            if x.std() > 0:
                pend.append(float(np.polyfit(x, y, 1)[0]))
    hs = sorted(b[4] for b in tutte)
    iqr = hs[3 * len(hs) // 4] - hs[len(hs) // 4]
    if not (passi and spazi and larg and pend):
        return None
    return OrderedDict([('passo di riga / h', statistics.median(passi) / h), ('spazio fra parole / h', statistics.median(spazi) / h),
                        ('larghezza per unita / h', statistics.median(larg) / h), ('inclinazione', statistics.median(pend)), ('variabilita altezza', iqr / h)])


def main():
    meta = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        meta.setdefault(r.pagina, (r.mano, r.lingua, r.sezione))
    nomi, X, mani, lingue, strati, sezioni = [], [], [], [], [], []
    for p, (m, l, s) in meta.items():
        if not m or not l:
            continue
        f = misure(p)
        if f is None:
            continue
        nomi.append(p)
        X.append(list(f.values()))
        mani.append(m)
        lingue.append(l)
        strati.append('%s|%s' % (l, s))
        sezioni.append(s)
    colonne = list(misure(nomi[0]).keys())
    X, mani, lingue = np.array(X), np.array(mani), np.array(lingue)
    print('pagine %d, mani %s' % (len(nomi), dict(Counter(mani.tolist()))), flush=True)
    ris = OrderedDict([('pagine', len(nomi)), ('mani', dict(Counter(mani.tolist()))), ('caratteristiche', colonne)])
    ris['controllo (lingua dentro la sezione)'] = e244.prova(X, lingue, sezioni, random.Random(2601))
    ris['mani dentro lingua x sezione'] = e244.prova(X, mani, strati, random.Random(2600))
    medie = OrderedDict()
    for m in sorted(set(mani.tolist())):
        sel = mani == m
        medie[m] = OrderedDict((c, float(X[sel, i].mean())) for i, c in enumerate(colonne))
    ris['medie_per_mano'] = medie
    z = ris['mani dentro lingua x sezione']['z'] or 0
    ris['esito'] = 'differenze nel tratto' if z > 3 else ('nessuna differenza oltre lingua e sezione' if z <= 2 else 'incerto')
    print(json.dumps(ris, default=float)[:1500], flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e260_scribi_tratto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e260 — Gli scribi si distinguono dal tratto?', '',
          'Misure fisiche per pagina dai riquadri di voynichese.com; classificatore delle mani contro permutazioni dentro lingua × sezione. '
          'Preregistrazione: `preregistrazioni/e260.md`.', '', '| prova | accuratezza | nullo | z | p |', '|---|---|---|---|---|']
    for k in ('controllo (lingua dentro la sezione)', 'mani dentro lingua x sezione'):
        r = ris[k]
        md.append('| %s | %.3f | %.3f | %.1f | %.4f |' % (k, r['accuratezza'], r['nullo'], r['z'] or 0, r['p']))
    md += ['', '| mano | ' + ' | '.join(colonne) + ' |', '|---|' + '---|' * len(colonne)]
    for m, v in medie.items():
        md.append('| %s | %s |' % (m, ' | '.join('%.3f' % v[c] for c in colonne)))
    md += ['', 'Pagine: %d. Esito: **%s**.' % (len(nomi), ris['esito'])]
    open(os.path.join(RISULTATI, 'e260_scribi_tratto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
