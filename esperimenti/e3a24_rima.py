# -*- coding: utf-8 -*-
"""Esperimento e3a24: rima (ultimi 2 segni uguali fra le parole finali di righe consecutive) e allitterazione (primi 2
segni delle prime parole), contro l'ordine delle righe rimescolato e contro la somiglianza con una parola in mezzo.

Preregistrazione: preregistrazioni/e3a24.md. Scrive risultati/e3a24_rima.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def quota(pars, prendi_a, prendi_b, chiave, rnd):
    si = tot = 0
    for par in pars:
        for i in range(1, len(par)):
            a = prendi_a(par[i], rnd)
            b = prendi_b(par[i - 1], rnd)
            if a is None or b is None:
                continue
            tot += 1
            si += chiave(a) == chiave(b)
    return si / tot if tot else 0.0


def prova(pars, prendi_a, prendi_b, chiave, rnd):
    vero = quota(pars, prendi_a, prendi_b, chiave, rnd)
    nul = [quota([rnd.sample(p, len(p)) for p in pars], prendi_a, prendi_b, chiave, rnd) for _ in range(1000)]
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('osservata', vero), ('nullo', m), ('rapporto', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3124)
    pars = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            rr = [r for r in rr if r]
            if sum(len(r) >= 3 for r in rr) >= 3:
                pars.append(rr)
    fin = lambda r, rnd: r[-1] if len(r) >= 3 and len(r[-1]) >= 2 else None
    ini = lambda r, rnd: r[0] if len(r) >= 3 and len(r[0]) >= 2 else None
    mezzo = lambda r, rnd: (lambda w: w if len(w) >= 2 else None)(r[rnd.randrange(1, len(r) - 1)]) if len(r) >= 3 else None
    coda, testa = (lambda w: w[-2:]), (lambda w: w[:2])
    ris = OrderedDict()
    ris['rima: finale contro finale'] = prova(pars, fin, fin, coda, rnd)
    ris['finale contro una parola in mezzo della riga sopra'] = prova(pars, fin, mezzo, coda, rnd)
    ris['allitterazione: prima contro prima'] = prova(pars, ini, ini, testa, rnd)
    ris['prima contro una parola in mezzo della riga sopra'] = prova(pars, ini, mezzo, testa, rnd)
    esiti = OrderedDict()
    for nome, a, b in (('rima', 'rima: finale contro finale', 'finale contro una parola in mezzo della riga sopra'),
                       ('allitterazione', 'allitterazione: prima contro prima', 'prima contro una parola in mezzo della riga sopra')):
        z1 = ris[a]['z']
        R = ris[a]['rapporto'] / ris[b]['rapporto'] if ris[b]['rapporto'] else None
        if z1 > 3 and R is not None and R > 1.2:
            es = 'le righe %s' % ('rimano' if nome == 'rima' else 'allitterano')
        elif z1 > 3:
            es = 'somiglianza solo da copia'
        elif z1 < 2:
            es = 'nessuna %s' % nome
        else:
            es = 'incerto'
        esiti[nome] = OrderedDict([('R', R), ('esito', es)])
    out = OrderedDict([('paragrafi', len(pars)), ('misure', ris), ('esiti', esiti)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a24_rima.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a24 — Le righe "rimano"?', '', 'Preregistrazione: `preregistrazioni/e3a24.md`. %d paragrafi con almeno 3 righe di almeno 3 parole.' % len(pars), '',
          '| confronto | osservata | nullo (righe rimescolate) | rapporto | z |', '|---|---|---|---|---|']
    md += ['| %s | %.3f | %.3f | %.2f | %.1f |' % (k, x['osservata'], x['nullo'], x['rapporto'], x['z']) for k, x in ris.items()]
    md += ['', 'Rima: R = %.2f, esito **%s**. Allitterazione: R = %.2f, esito **%s**.' % (esiti['rima']['R'], esiti['rima']['esito'], esiti['allitterazione']['R'], esiti['allitterazione']['esito'])]
    open(os.path.join(RISULTATI, 'e3a24_rima.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
