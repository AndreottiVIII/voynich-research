# -*- coding: utf-8 -*-
"""Esperimento e3b36: replica con la trascrizione IT di e3b13 (memoria di qo/o a parita' di raccordo), e3a66 (spazi
facoltativi per mano) ed e3b28 (ripresa fra pagine contro righe di lunghezza simile).

Preregistrazione: preregistrazioni/e3b36.md. Scrive risultati/e3b36_repliche_takahashi_2.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60
import e3a66_spazi_mani as e3a66
import e3b13_qo_raccordo as e3b13
import e3b27_ripresa_pagine as e3b27
import e3b28_ripresa_pagine_lunghezza as e3b28
import e3b35_repliche_takahashi as e3b35

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def uno(pagine_righe, rnd):
    cc = e3b13.coppie(pagine_righe)
    e = e3b13.eccessi(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    bd = []
    for _ in range(2000):
        eb = e3b13.eccessi([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        bd.append(eb['vicino'][0] - eb['lontano'][0])
    bd.sort()
    ic = [bd[50], bd[1949]]
    return OrderedDict([('differenza', e['vicino'][0] - e['lontano'][0]), ('IC95', ic), ('regge', ic[0] > 0)])


def due(rnd):
    info = {}
    for r in trascrizione.leggi('ZL'):
        info.setdefault(r.pagina, (r.mano, r.lingua))
    righe = e3a60.righe('IT')
    pos = []
    for (pg, _), (segni, sep) in righe.items():
        pos += [(segni[i - 1], segni[i], sep.get(i, ''), pg) for i in range(1, len(segni)) if sep.get(i, '') != '|']
    reg = e3a58.Regola([(a, b, t == '.') for a, b, t, _ in pos if t != ','])
    fac = [((a, b), pg, int(t == '.')) for a, b, t, pg in pos if t != ',' and pg in info and 0.2 <= reg.p(a, b) <= 0.8]
    conta = Counter(info[pg][0] for _, pg, _ in fac)
    mani = sorted(m for m, n in conta.items() if m and n >= e3a66.MIN_PUNTI)
    fac = [x for x in fac if info[x[1]][0] in mani]
    pagine = sorted({pg for _, pg, _ in fac})
    mano_di = {pg: info[pg][0] for pg in pagine}
    oss = e3a66.eterogeneita(fac, mano_di)
    per_lingua = defaultdict(list)
    for pg in pagine:
        per_lingua[info[pg][1]].append(pg)
    nul = []
    for _ in range(1000):
        m2 = {}
        for pp in per_lingua.values():
            mm = [mano_di[p] for p in pp]
            rnd.shuffle(mm)
            m2.update(zip(pp, mm))
        nul.append(e3a66.eterogeneita(fac, m2))
    p = (1 + sum(1 for v in nul if v >= oss)) / 1001
    return OrderedDict([('mani', mani), ('eterogeneita', oss), ('nullo_media', statistics.mean(nul)), ('p', p), ('regge', p < 0.01)])


def tre(pagine_par, rnd):
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    xs = []
    for (p, pp), (q, qq) in zip(pagine_par, pagine_par[1:]):
        fp, fq = e3b27.foglio(p), e3b27.foglio(q)
        if not fp or not fq or lingua.get(p) != lingua.get(q) or lingua.get(p) not in ('A', 'B'):
            continue
        rp = [r for par in pp for r in par]
        rq = [r for par in qq for r in par]
        if len(rp) < 4 or len(rq) < 4:
            continue
        if not ((fp[0] == fq[0] and fp[1] == 'r' and fq[1] == 'v') or (fq[0] == fp[0] + 1 and fp[1] == 'v' and fq[1] == 'r')):
            continue
        e = e3b27.eccesso(rq[0], rp[-1], e3b28.simili_lunghezza(rp[:-1], rp[-1]))
        if e is not None:
            xs.append(e)
    b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(2000))
    ic = [b[50], b[1949]]
    return OrderedDict([('coppie', len(xs)), ('eccesso', statistics.mean(xs)), ('IC95', ic), ('regge', ic[0] <= 0)])


def main():
    rnd = random.Random(3236)
    pagine = e3b35.pagine_par_it()
    pagine_righe = [[r for par in pars for r in par] for pars in pagine]
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    pagine_par = [(pg, [par for par in pars if par]) for pg, pars in per.items() if any(pars)]
    ris = OrderedDict()
    ris['1 memoria di qo/o a parità di raccordo (e3b13)'] = uno(pagine_righe, rnd)
    ris['2 spazi facoltativi per mano (e3a66)'] = due(rnd)
    ris['3 la ripresa non passa la pagina (e3b28)'] = tre(pagine_par, rnd)
    print(json.dumps(ris, ensure_ascii=False, indent=1, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b36_repliche_takahashi_2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3b36 — Altri tre risultati misurati solo sulla ZL reggono con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b36.md`.', '']
    for k, x in ris.items():
        md.append('- **%s**: %s → **%s**.' % (k, '; '.join('%s %s' % (kk, ('%+.4f' % vv) if isinstance(vv, float) else (('%+.4f – %+.4f' % tuple(vv)) if isinstance(vv, list) and vv and isinstance(vv[0], float) else vv)) for kk, vv in x.items() if kk != 'regge'), 'regge' if x['regge'] else 'non regge'))
    open(os.path.join(RISULTATI, 'e3b36_repliche_takahashi_2.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
