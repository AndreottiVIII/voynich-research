# -*- coding: utf-8 -*-
"""Esperimento e3a78: il Voynich riscritto riga per riga dalla propria catena di segni di ordine 2 (stessa struttura di
pagine, paragrafi e righe); otto proprieta' nel vero e nel riscritto.

Preregistrazione: preregistrazioni/e3a78.md. Scrive risultati/e3a78_cosa_spiega_la_catena.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e377_giuntura_gibberish as e377
import e385_calo as e385
import e3a25_inizi_evitati as e3a25
import e3a49_dentro_fra as e3a49
import e3a55_frequenza_forma as e3a55
import e3a71_catene_ordini as e3a71

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
RISCRITTURE = 5
ORDINE = 2
NOMI = ('giuntura', 'chiusura della riga', 'ripresa dalla riga sopra', 'margine sinistro', '-m a fine riga', 'y/s/d a inizio riga',
        'catena dentro/fra le parole', 'frequenza-forma')


def giuntura(righe, rnd, perm=20):
    def mi(rr):
        return e377.mi(Counter((a[-1], b[0]) for r in rr for a, b in zip(r, r[1:])))
    o = mi(righe)
    nul = [mi([rnd.sample(r, len(r)) for r in righe]) for _ in range(perm)]
    return o - statistics.mean(nul)


def a_capo(pagine, rnd, perm=20):
    coppie = []
    for i, pars in enumerate(pagine):
        for par in pars:
            for r1, r2 in zip(par, par[1:]):
                if r1 and r2:
                    coppie.append((i, r1[-1][-1], r2[0][0]))
    o = e377.mi(Counter((a, b) for _, a, b in coppie))
    per = {}
    for i, a, b in coppie:
        per.setdefault(i, []).append((a, b))
    nul = []
    for _ in range(perm):
        c = Counter()
        for xs in per.values():
            bs = [b for _, b in xs]
            rnd.shuffle(bs)
            c.update(zip([a for a, _ in xs], bs))
        nul.append(e377.mi(c))
    return o - statistics.mean(nul)


def proprieta(pagine, rnd):
    righe = [r for pars in pagine for par in pars for r in par if r]
    parole = [w for r in righe for w in r]
    e_riga = giuntura(righe, rnd)
    e_capo = a_capo(pagine, rnd)
    us = [e385.unita(par) for pars in pagine for par in pars if len(par) >= 2]
    e1 = e385.profilo(us)[0][1]
    blocchi = [e3a25.inizi(par[1:], 2) for pars in pagine for par in pars if len(par[1:]) >= 3]
    marg = e3a25.prova(blocchi, rnd, 200)
    fin = [r[-1] for r in righe]
    alt = [w for r in righe for w in r[:-1]]
    m_fine = sum(w[-1] == 'm' for w in fin) / len(fin) - sum(w[-1] == 'm' for w in alt) / len(alt)
    ini = [r[0] for r in righe]
    alt2 = [w for r in righe for w in r[1:]]
    ysd = sum(w[0] in ('y', 's', 'd') for w in ini) / len(ini) - sum(w[0] in ('y', 's', 'd') for w in alt2) / len(alt2)
    return OrderedDict([(NOMI[0], e_riga), (NOMI[1], e_riga - e_capo), (NOMI[2], e1), (NOMI[3], 1 - marg['rapporto']),
                        (NOMI[4], m_fine), (NOMI[5], ysd), (NOMI[6], e3a49.rho(righe)[0]), (NOMI[7], e3a55.rho(parole))])


def riscrivi(pagine, tab, rnd):
    out = []
    for pars in pagine:
        pp = []
        for par in pars:
            nuovo = []
            for _ in par:
                r = []
                while not r:
                    r = e3a71.scrivi(tab, 1, ORDINE, rnd)
                    r = r[0] if r else []
                nuovo.append(r)
            pp.append(nuovo)
        out.append(pp)
    return out


def main():
    rnd = random.Random(3178)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append([par for par in pp if par])
    vero = proprieta(pagine, rnd)
    print('vero', json.dumps(vero, ensure_ascii=False), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], ORDINE)
    risc = []
    for v in range(RISCRITTURE):
        risc.append(proprieta(riscrivi(pagine, tab, rnd), rnd))
        print('riscritto', v, json.dumps(risc[-1], ensure_ascii=False), flush=True)
    sintesi = OrderedDict()
    for n in NOMI:
        rv = statistics.mean(x[n] for x in risc)
        R = rv / vero[n] if vero[n] else None
        es = 'n.d.' if R is None else ('la catena la riproduce' if R >= 0.75 else ('in parte' if R >= 0.25 else 'la catena non la riproduce: serve un meccanismo in più'))
        sintesi[n] = OrderedDict([('vero', vero[n]), ('riscritto_media', rv), ('riscritto', [x[n] for x in risc]), ('R', R), ('esito', es)])
    out = OrderedDict([('sintesi', sintesi)])
    print(json.dumps(sintesi, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a78_cosa_spiega_la_catena.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a78 — Che cosa spiega da sola una catena di segni per riga, e che cosa no?', '', 'Preregistrazione: `preregistrazioni/e3a78.md`. Catena di ordine 2 addestrata sul Voynich; 5 riscritture con la stessa struttura di pagine, paragrafi e righe.', '',
          '| proprietà | Voynich vero | riscritto (media) | R | esito |', '|---|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %s | %s |' % (n, x['vero'], x['riscritto_media'], '%.2f' % x['R'] if x['R'] is not None else 'n.d.', x['esito']) for n, x in sintesi.items()]
    open(os.path.join(RISULTATI, 'e3a78_cosa_spiega_la_catena.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
