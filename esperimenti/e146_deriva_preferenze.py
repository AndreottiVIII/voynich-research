# -*- coding: utf-8 -*-
"""Esperimento 146: correlazione delle preferenze di grafia fra righe a distanza d (dentro pagina, a cavallo di pagina e
di paragrafo), per stimare la deriva delle "abitudini" e le eventuali ripartenze.

Preregistrazione: preregistrazioni/e146.md. Scrive risultati/e146_deriva_preferenze.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e135_stato_riga as e135

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, BOOT = 146, 1000, 1000
SCELTE = (0, 1, 2, 4, 6)
DD = (1, 2, 3, 5, 10)


def righe_voynich():
    out, par = [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            par += bool(r.inizio_par)
            out.append((r.pagina, par, list(r.parole)))
    return out


def righe_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    out, par = [], 0
    for i, (ini, ps) in enumerate(rr):
        par += bool(ini or i % 29 == 0)
        out.append((i // 29, par, ps))
    return out


def residui(righe):
    occ = [o for o in e135.occorrenze([('x', ps) for _, _, ps in righe]) if o[0] in SCELTE]
    occ = [(f, r, st[1:]) + (v,) for f, r, st, v in occ]  # toglie la pagina dagli strati
    quota = defaultdict(lambda: [0, 0])
    for f, r, st, v in occ:
        quota[(f, st)][0] += v
        quota[(f, st)][1] += 1
    acc = defaultdict(list)
    for f, r, st, v in occ:
        a, n = quota[(f, st)]
        acc[(f, r)].append(v - a / n)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def corr(coppie_righe, res):
    x, y = [], []
    for i, j in coppie_righe:
        for f in SCELTE:
            if (f, i) in res and (f, j) in res:
                x.append(res[(f, i)])
                y.append(res[(f, j)])
    if len(x) < 30:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else None


def gruppi_coppie(righe):
    g = defaultdict(list)
    for i in range(len(righe)):
        for d in DD:
            j = i + d
            if j < len(righe) and righe[j][0] == righe[i][0]:
                g['dentro la pagina, d=%d' % d].append((i, j))
        j = i + 1
        if j < len(righe):
            if righe[j][0] != righe[i][0]:
                g['a cavallo di pagina'].append((i, j))
            elif righe[j][1] != righe[i][1]:
                g['a cavallo di paragrafo'].append((i, j))
            else:
                g['dentro il paragrafo, d=1'].append((i, j))
    return g


def per_pagina(coppie, righe):
    p = defaultdict(list)
    for i, j in coppie:
        p[righe[i][0]].append((i, j))
    return p


def valuta(righe, rnd):
    res = residui(righe)
    g = gruppi_coppie(righe)
    out = OrderedDict()
    for nome, cc in g.items():
        out[nome] = OrderedDict([('coppie', len(cc)), ('r', corr(cc, res))])
    # nullo per dentro la pagina: righe rimescolate dentro ogni pagina
    idx_pag = defaultdict(list)
    for i, (pag, _, _) in enumerate(righe):
        idx_pag[pag].append(i)
    nulli = defaultdict(list)
    for _ in range(RIMESCOLAMENTI):
        perm = list(range(len(righe)))
        for ii in idx_pag.values():
            v = ii[:]
            rnd.shuffle(v)
            for a, b in zip(ii, v):
                perm[a] = b
        res2 = {(f, i): res[(f, perm[i])] for (f, i) in res if (f, perm[i]) in res}
        for d in DD:
            nulli[d].append(corr(g['dentro la pagina, d=%d' % d], res2) or 0)
    for d in DD:
        k = 'dentro la pagina, d=%d' % d
        m, s = statistics.mean(nulli[d]), statistics.pstdev(nulli[d])
        out[k]['nullo'] = m
        out[k]['z'] = ((out[k]['r'] or 0) - m) / s if s else None
    # bootstrap per pagine
    for k in ('dentro la pagina, d=1', 'dentro la pagina, d=10', 'a cavallo di pagina', 'a cavallo di paragrafo', 'dentro il paragrafo, d=1'):
        pp = per_pagina(g[k], righe)
        chiavi = list(pp)
        vv = []
        for _ in range(BOOT):
            cc = [c for p in (rnd.choice(chiavi) for _ in chiavi) for c in pp[p]]
            r = corr(cc, res)
            if r is not None:
                vv.append(r)
        vv.sort()
        out[k]['iv'] = [vv[int(0.05 * len(vv))], vv[int(0.95 * len(vv)) - 1]] if vv else None
    return out


def main():
    rnd = random.Random(SEME)
    ris = OrderedDict()
    for nome, rr in (('Voynich ZL', righe_voynich()), ('Timm e Schinner, seme 19', righe_ts())):
        ris[nome] = r = valuta(rr, rnd)
        for k, x in r.items():
            print('%-26s %-28s coppie %5d r %+.3f %s %s' % (nome, k, x['coppie'], x['r'] or 0,
                                                         '(z %.1f)' % x['z'] if x.get('z') is not None else '', '[%.3f, %.3f]' % tuple(x['iv']) if x.get('iv') else ''), flush=True)
    v = ris['Voynich ZL']
    sovrap = lambda a, b: a and b and a[0] <= b[1] and b[0] <= a[1]
    d1, d10 = v['dentro la pagina, d=1'], v['dentro la pagina, d=10']
    deriva = (d1['z'] or 0) > 4 and (d1['r'] or 0) > (d10['r'] or 0) and not sovrap(d1['iv'], d10['iv'])
    cp = v['a cavallo di pagina']
    rip_pag = (cp['r'] or 0) < (d1['r'] or 0) / 2 and not sovrap(cp['iv'], d1['iv'])
    cpar, dpar = v['a cavallo di paragrafo'], v['dentro il paragrafo, d=1']
    rip_par = (cpar['r'] or 0) < (dpar['r'] or 0) / 2 and not sovrap(cpar['iv'], dpar['iv'])
    ris['deriva_locale'], ris['ripartenza_pagina'], ris['ripartenza_paragrafo'] = deriva, rip_pag, rip_par
    print('deriva locale %s | ripartenza a pagina %s | ripartenza a paragrafo %s' % (deriva, rip_pag, rip_par))
    with open(os.path.join(RISULTATI, 'e146_deriva_preferenze.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e146 — Deriva delle preferenze di riga', '', 'Correlazione dei residui di riga (5 scelte, strati senza pagina) fra righe a distanza d. '
           'Nullo dentro pagina: %d rimescolamenti delle righe nella pagina; intervalli: bootstrap per pagine. Preregistrazione: `preregistrazioni/e146.md`.' % RIMESCOLAMENTI, '',
           '| testo | gruppo | coppie | r | z | intervallo 90% |', '|---|---|---|---|---|---|']
    for nome in ('Voynich ZL', 'Timm e Schinner, seme 19'):
        for k, x in ris[nome].items():
            out.append('| %s | %s | %d | %+.3f | %s | %s |' % (nome, k, x['coppie'], x['r'] or 0, '%.1f' % x['z'] if x.get('z') is not None else '',
                                                           '%.3f – %.3f' % tuple(x['iv']) if x.get('iv') else ''))
    out += ['', 'Deriva locale: **%s**. Ripartenza a pagina: **%s**. Ripartenza a paragrafo: **%s**.' % tuple('sì' if x else 'no' for x in (deriva, rip_pag, rip_par))]
    with open(os.path.join(RISULTATI, 'e146_deriva_preferenze.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
