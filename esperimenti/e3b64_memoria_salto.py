# -*- coding: utf-8 -*-
"""Esperimento e3b64: la memoria delle scelte passa il salto di un disegno o l'a capo? Nullo che tiene interi i tratti:
le parti dopo il confine si rimescolano fra i confini della stessa pagina.

Preregistrazione: preregistrazioni/e3b64.md. Scrive risultati/e3b64_memoria_salto.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e386_salto_disegno as e386
import e3a86_ripetizioni_riga as e3a86
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
MIN_SALTO = 150


def tratti(ws, seps):
    """Divide una riga nei tratti separati dai salti del disegno."""
    out, cur = [], [ws[0]]
    for k, s in enumerate(seps):
        if s == '|':
            out.append(cur)
            cur = []
        cur.append(ws[k + 1])
    out.append(cur)
    return out


def confini(righe, tipo):
    """righe: [(pagina, paragrafo, parole, separatori)] in ordine. Ritorna {pagina: [(prima, dopo)]}."""
    out = defaultdict(list)
    if tipo == 'salto':
        for pg, npar, ws, seps in righe:
            tt = tratti(ws, seps)
            if len(tt) >= 2:
                out[pg].append((tt[0], tt[1]))
    else:
        for (pg, npar, ws, seps), (pg2, npar2, ws2, seps2) in zip(righe, righe[1:]):
            if pg == pg2 and npar == npar2:
                out[pg].append((tratti(ws, seps)[-1], tratti(ws2, seps2)[0]))
    return out


def valori(seg, f):
    return [f(w) if w else None for w in seg]


def coppie_cavallo(a, b):
    """a, b: liste di (valore, coperta) o None. Coppie a cavallo a distanza 2-3, senza illeggibili in mezzo."""
    seq = a + b
    n = len(a)
    out = []
    for i in range(n):
        for d in (2, 3):
            j = i + d
            if j < n or j >= len(seq) or seq[i] is None or seq[j] is None:
                continue
            if any(seq[k] is None for k in range(i + 1, j)):
                continue
            ci, cj = seq[i][1], seq[j][1]
            if ci == cj or e3a86.una_modifica(ci, cj):
                continue
            out.append((seq[i][0], seq[j][0]))
    return out


def coppie_dentro(seg):
    out = []
    for i in range(len(seg)):
        for d in (2, 3):
            j = i + d
            if j >= len(seg) or seg[i] is None or seg[j] is None or any(seg[k] is None for k in range(i + 1, j)):
                continue
            if seg[i][1] == seg[j][1] or e3a86.una_modifica(seg[i][1], seg[j][1]):
                continue
            out.append((seg[i][0], seg[j][0]))
    return out


def kappa(somme):
    o = sum(s[0] for s in somme)
    a = sum(s[1] for s in somme)
    n = sum(s[2] for s in somme)
    return (o - a) / (n - a) if n - a > 0 else None, int(n)


def somma_pagina(pairs, p):
    att = p * p + (1 - p) * (1 - p)
    return (sum(1 for x, y in pairs if x == y), att * len(pairs), len(pairs))


def prova(per_pagina, quote, classi, rng):
    """per_pagina: {pagina: [(prima, dopo)]}; quote: {(classe, pagina): p}."""
    dati = []
    for pg, cc in per_pagina.items():
        for c, f in classi.items():
            if (c, pg) not in quote:
                continue
            prime = [valori(a, f) for a, _ in cc]
            dopo = [valori(b, f) for _, b in cc]
            dati.append((quote[(c, pg)], prime, dopo))
    oss = [somma_pagina([x for a, b in zip(pr, do) for x in coppie_cavallo(a, b)], p) for p, pr, do in dati]
    dentro = [somma_pagina([x for a, b in zip(pr, do) for s in (a, b) for x in coppie_dentro(s)], p) for p, pr, do in dati]
    k_oss, n = kappa(oss)
    nul = []
    for _ in range(PERM):
        ss = []
        for p, pr, do in dati:
            perm = rng.permutation(len(do))
            ss.append(somma_pagina([x for i, a in enumerate(pr) for x in coppie_cavallo(a, do[perm[i]])], p))
        nul.append(kappa(ss)[0])
    nul = [x for x in nul if x is not None]
    mu, sd = float(np.mean(nul)), float(np.std(nul))
    kd, nd = kappa(dentro)
    return OrderedDict([('coppie_a_cavallo', n), ('K', k_oss), ('nullo', mu), ('effetto', k_oss - mu), ('z', (k_oss - mu) / sd if sd > 0 else 0.0),
                        ('p', float(np.mean([x >= k_oss for x in nul]))), ('K_dentro_i_tratti', kd), ('coppie_dentro', nd)])


def quote_pagine(righe, classi):
    tot = defaultdict(lambda: [0, 0])
    for pg, npar, ws, seps in righe:
        for c, f in classi.items():
            for w in ws:
                x = f(w) if w else None
                if x:
                    tot[(c, pg)][0] += x[0]
                    tot[(c, pg)][1] += 1
    return {k: u / t for k, (u, t) in tot.items() if t >= 5}


def main():
    rng = np.random.default_rng(3264)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e386.righe()]
    quote = quote_pagine(righe, e3b62.CV)
    ris = OrderedDict()
    ris['salto del disegno'] = prova(confini(righe, 'salto'), quote, e3b62.CV, rng)
    print('salto', json.dumps(ris['salto del disegno']), flush=True)
    capo = confini(righe, 'capo')
    ris['a capo, pagine normali'] = prova({pg: v for pg, v in capo.items() if sezione.get(pg) != 'T'}, quote, e3b62.CV, rng)
    print('a capo normali', json.dumps(ris['a capo, pagine normali']), flush=True)
    ris['a capo, pagine di solo testo'] = prova({pg: v for pg, v in capo.items() if sezione.get(pg) == 'T'}, quote, e3b62.CV, rng)
    print('a capo T', json.dumps(ris['a capo, pagine di solo testo']), flush=True)
    s = ris['salto del disegno']
    es = OrderedDict()
    es['salto'] = 'dati insufficienti' if s['coppie_a_cavallo'] < MIN_SALTO else ('il salto del disegno azzera la memoria' if s['p'] > 0.05 else 'la memoria passa il salto')
    es['a capo, pagine normali'] = "l'a capo azzera la memoria" if ris['a capo, pagine normali']['p'] > 0.05 else "la memoria passa l'a capo"
    es['a capo, pagine di solo testo'] = "la memoria passa l'a capo" if ris['a capo, pagine di solo testo']['p'] < 0.05 else 'non dimostrato'
    out = OrderedDict([('confini', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b64_memoria_salto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b64 — La memoria delle scelte passa il salto di un disegno o l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3b64.md`. Nullo: le parti dopo il confine rimescolate fra i confini della stessa pagina.', '',
          '| confine | coppie a cavallo | K osservato | K nullo | effetto | z | p | K dentro i tratti (coppie) |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f | %+.4f (%d) |' % (k, x['coppie_a_cavallo'], x['K'], x['nullo'], x['effetto'], x['z'], x['p'], x['K_dentro_i_tratti'], x['coppie_dentro']))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b64_memoria_salto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
