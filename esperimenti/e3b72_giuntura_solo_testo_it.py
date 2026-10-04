# -*- coding: utf-8 -*-
"""Esperimento e3b72: e3a06 (giuntura a capo nelle pagine di solo testo) con la IT, e controllo con la riga sopra (ZL e
IT).

Preregistrazione: preregistrazioni/e3b72.md. Scrive risultati/e3b72_giuntura_solo_testo_it.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a06_solo_testo as e3a06

RISULTATI = os.path.join(QUI, '..', 'risultati')


def coppie(rr, sezione, verso):
    """{True/False (pagina T): {pagina: [(ultimo segno riga i, primo segno riga i+verso)]}}."""
    out = defaultdict(lambda: defaultdict(list))
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        j = k + verso
        if j < 0 or j >= len(rr):
            continue
        st2, pag2, npar2, ws2, seps2 = rr[j]
        if pag2 == pag and npar2 == npar and ws and ws[-1] and ws2 and ws2[0]:
            out[sezione.get(pag) == 'T'][pag].append((ws[-1][-1], ws2[0][0]))
    return out


def taratura(T, altre, rnd, nT, E_T, n=2000):
    altre = list(altre.items())
    tar = []
    for _ in range(n):
        rnd.shuffle(altre)
        camp, m = {}, 0
        for pg, xs in altre:
            if m >= nT:
                break
            camp[pg] = xs
            m += len(xs)
        tar.append(e3a06.E_esatto(camp, rnd, 200)[0])
    return sum(x >= E_T for x in tar) / len(tar), statistics.median(tar)


def main():
    rnd = random.Random(3272)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    ris = OrderedDict()
    for q in ('IT', 'ZL'):
        rr = e395.righe(q)
        for nome, verso in (('riga sotto', 1), ('riga sopra', -1)):
            cc = coppie(rr, sezione, verso)
            T = cc[True]
            nT = sum(len(x) for x in T.values())
            E_T, p_T = e3a06.E_esatto(T, rnd, 10000)
            x = OrderedDict([('coppie', nT), ('E', E_T), ('p_esatto', p_T)])
            if q == 'IT' and verso == 1:
                quota, med = taratura(T, cc[False], rnd, nT, E_T)
                x['taratura_quota'] = quota
                x['taratura_mediana'] = med
            ris['%s, %s' % (q, nome)] = x
            print(q, nome, json.dumps(x), flush=True)
    it = ris['IT, riga sotto']
    if it['p_esatto'] < 0.01 and it['taratura_quota'] < 0.01:
        es1 = 'si ritrova con Takahashi'
    elif it['p_esatto'] > 0.05 or it['taratura_quota'] > 0.05:
        es1 = 'non si ritrova'
    else:
        es1 = 'incerto'
    es2 = 'non è somiglianza fra righe vicine' if ris['ZL, riga sopra']['E'] < ris['ZL, riga sotto']['E'] / 2 else 'può essere somiglianza fra righe vicine'
    out = OrderedDict([('misure', ris), ('esito_replica', es1), ('esito_controllo', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b72_giuntura_solo_testo_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3b72 — Giuntura a capo nelle pagine di solo testo: Takahashi e controllo della riga sopra', '', 'Preregistrazione: `preregistrazioni/e3b72.md`. ZL nell\'e3a06: E +0,144, p 0,0006.', '',
          '| trascrizione, abbinamento | coppie | E | p esatto | taratura (quota con E maggiore; mediana) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.4f | %.4f | %s |' % (k, x['coppie'], x['E'], x['p_esatto'], ('%.4f; %+.4f' % (x['taratura_quota'], x['taratura_mediana'])) if 'taratura_quota' in x else '—'))
    md += ['', 'Esito replica: **%s**. Esito controllo: **%s**.' % (es1, es2)]
    open(os.path.join(RISULTATI, 'e3b72_giuntura_solo_testo_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
