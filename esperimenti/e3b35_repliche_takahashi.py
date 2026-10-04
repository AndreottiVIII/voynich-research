# -*- coding: utf-8 -*-
"""Esperimento e3b35: replica con la trascrizione IT di e3a64 (compressione a fine riga), e3b10 (a capo e memoria delle
scelte), e3b18 (memoria per classe), e3b20 (memoria e lettere).

Preregistrazione: preregistrazioni/e3b35.md. Scrive risultati/e3b35_repliche_takahashi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a58_spazi_prevedibili as e3a58
import e3a64_spazi_fine_riga as e3a64
import e3b10_scelte_a_capo as e3b10
import e3b18_memoria_incrociata as e3b18
import e3b20_memoria_segni as e3b20

RISULTATI = os.path.join(QUI, '..', 'risultati')


def pagine_par_it():
    """{pagina: [paragrafi di righe di stringhe EVA]} dalla IT."""
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    return [[par for par in pars if par] for pars in per.values() if any(pars)]


def uno(rnd):
    pp = e3a64.punti(e395.righe('IT'))
    reg = e3a58.Regola([(a, b, t == '.') for a, b, t, _ in pp if t != ','])
    strati = defaultdict(list)
    for a, b, t, x in pp:
        if t == ',' or not 0.2 <= reg.p(a, b) <= 0.8:
            continue
        terzo = 1 if x < 1 / 3 else (3 if x > 2 / 3 else 2)
        if terzo != 2:
            strati[a, b].append((terzo, int(t == '.')))
    d = e3a64.differenza(strati)
    nul = []
    for _ in range(2000):
        s2 = {}
        for k, xs in strati.items():
            tt = [t for t, _ in xs]
            rnd.shuffle(tt)
            s2[k] = list(zip(tt, [y for _, y in xs]))
        nul.append(e3a64.differenza(s2))
    p = (1 + sum(1 for v in nul if abs(v) >= abs(d))) / 2001
    return OrderedDict([('differenza', d), ('p', p), ('regge', d < 0 and p < 0.01)])


def due(pagine, rnd):
    cc = []
    for pid, pars in enumerate(pagine):
        cc += e3b10.coppie_pagina(pars, pid)
    e = e3b10.eccessi(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    bd = sorted((lambda eb: eb['stessa riga'][0] - eb['a cavallo'][0])(e3b10.eccessi([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])) for _ in range(2000))
    ic = [bd[50], bd[1949]]
    s, c = e['stessa riga'][0], e['a cavallo'][0]
    return OrderedDict([('stessa_riga', s), ('a_cavallo', c), ('IC95_differenza', ic), ('regge', c < 0.5 * s and ic[0] > 0)])


def tre(pagine_righe, rnd):
    pp = e3b18.prodotti(pagine_righe)
    d, _ = e3b18.medie(pp)
    per = defaultdict(list)
    for x in pp:
        per[x[0]].append(x)
    chiavi = list(per)
    bs, bd = [], []
    for _ in range(1000):
        db, _ = e3b18.medie([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        bs.append(db['stessa'])
        bd.append(db['diverse'])
    bs.sort()
    bd.sort()
    ics, icd = [bs[25], bs[974]], [bd[25], bd[974]]
    return OrderedDict([('stessa', d['stessa']), ('IC_stessa', ics), ('diverse', d['diverse']), ('IC_diverse', icd), ('regge', ics[0] > 0 and icd[0] <= 0 <= icd[1])])


def quattro(pagine_righe, rnd):
    cc = e3b20.coppie(pagine_righe)
    mediane = {d: statistics.median(l for _, dd, l, _, _ in cc if dd == d) for d in (2, 3)}
    dv, _ = e3b20.differenza(cc, mediane)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    b = sorted(e3b20.differenza([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]], mediane)[0] for _ in range(2000))
    ic = [b[50], b[1949]]
    return OrderedDict([('differenza', dv), ('IC95', ic), ('regge', ic[0] > 0)])


def main():
    rnd = random.Random(3235)
    pagine = pagine_par_it()
    pagine_righe = [[r for par in pars for r in par] for pars in pagine]
    ris = OrderedDict()
    ris['1 compressione a fine riga (e3a64)'] = uno(rnd)
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    ris['2 a capo e memoria delle scelte (e3b10)'] = due(pagine, rnd)
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    ris['3 memoria per classe (e3b18)'] = tre(pagine_righe, rnd)
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    ris['4 memoria e lettere (e3b20)'] = quattro(pagine_righe, rnd)
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b35_repliche_takahashi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3b35 — Quattro risultati misurati solo sulla ZL reggono con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b35.md`.', '']
    for k, x in ris.items():
        md.append('- **%s**: %s → **%s**.' % (k, '; '.join('%s %s' % (kk, ('%+.4f' % vv) if isinstance(vv, float) else (('%+.4f – %+.4f' % tuple(vv)) if isinstance(vv, list) else vv)) for kk, vv in x.items() if kk != 'regge'), 'regge' if x['regge'] else 'non regge'))
    open(os.path.join(RISULTATI, 'e3b35_repliche_takahashi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
