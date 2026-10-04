# -*- coding: utf-8 -*-
"""Esperimento e3b53: memoria corta normalizzata (e3b52) delle varianti grafiche naturali i/y (Hatton Gospels, Secreta
Alberti, Nuovo Testamento fiammingo) e þ/ð (Hatton), da sole e insieme, contro il Voynich.

Preregistrazione: preregistrazioni/e3b53.md. Scrive risultati/e3b53_varianti_naturali.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b20_memoria_segni as e3b20
import e3b51_thorn_eth as e3b51
import e3b52_memoria_normalizzata as e3b52

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
TESTI = OrderedDict([('Hatton Gospels', 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels.txt'),
                     ('Secreta Alberti', 'Historical - English - Technical - Secreta Alberti.txt'),
                     ('NT fiammingo', 'Historical - Flemish - Literary - NT.txt')])
MIN_OCC = 3


def classe_iy(righe):
    """Funzione parola -> 1 (forma con y), 0 (forma con i), None, dalle coppie i/y del testo."""
    c = Counter(w for r in righe for w in r)
    val = {}
    conflitti = set()
    for w, f in c.items():
        if f < MIN_OCC:
            continue
        for i, s in enumerate(w):
            if s != 'i':
                continue
            w2 = w[:i] + ('y',) + w[i + 1:]
            if c.get(w2, 0) >= MIN_OCC:
                for x, v in ((w, 0), (w2, 1)):
                    if x in val and val[x] != v:
                        conflitti.add(x)
                    val[x] = v
    for x in conflitti:
        del val[x]
    return (lambda w: val.get(w)), len(val)


def main():
    rnd = random.Random(3253)
    tt = e381.testi()
    ris = OrderedDict()
    insieme = []
    base = 0
    for nome, chiave in TESTI.items():
        righe = [r for r in tt[chiave] if r]
        unita = [[b] for b in e3b51.blocchi(righe)]
        f, n_tipi = classe_iy(righe)
        classi = OrderedDict([('i/y', f)])
        if nome == 'Hatton Gospels':
            classi.update(e3b51.CLASSI)
        ev = e3b52.eventi(unita, classi, lambda w: w)
        for c in classi:
            evc = [x for x in ev if x[1] == c]
            m, dett = e3b52.memoria(evc)
            b = e3b52.boot(evc, rnd)
            ris['%s, %s' % (nome, c)] = OrderedDict([('memoria', m), ('dettaglio', dett), ('IC95', e3b52.ic(b) if b else None),
                                                      ('tipi_iy', n_tipi if c == 'i/y' else None)])
            print(nome, c, json.dumps(ris['%s, %s' % (nome, c)], ensure_ascii=False), flush=True)
        insieme += [(base + u, c, g, ok, att) for u, c, g, ok, att in ev]
        base += len(unita)
    mn, dn = e3b52.memoria(insieme)
    bn = e3b52.boot(insieme, rnd)
    ris['insieme naturale'] = OrderedDict([('memoria', mn), ('dettaglio', dn), ('IC95', e3b52.ic(bn))])
    voy = []
    for pg, pars in e341.pagine().items():
        rr = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            voy.append(rr)
    ev_v = e3b52.eventi(voy, e3b20.CLASSI, lambda w: tuple(D(w)))
    mv, dv = e3b52.memoria(ev_v)
    bv = e3b52.boot(ev_v, rnd)
    ris['Voynich (ZL)'] = OrderedDict([('memoria', mv), ('dettaglio', dv), ('IC95', e3b52.ic(bv))])
    n = min(len(bv), len(bn))
    ci = e3b52.ic([bv[i] - bn[i] for i in range(n)])
    in_ic = ris['insieme naturale']['IC95']
    es1 = 'memoria corta nelle varianti naturali' if in_ic[0] > 0 else 'non si vede'
    es2 = 'il Voynich ha più memoria' if ci[0] > 0 else ('il Voynich ne ha meno' if ci[1] < 0 else 'comparabile')
    out = OrderedDict([('testi', ris), ('contrasto', mv - mn), ('IC95_contrasto', ci), ('esito_1', es1), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b53_varianti_naturali.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b53 — Memoria corta delle varianti grafiche naturali contro il Voynich', '', 'Preregistrazione: `preregistrazioni/e3b53.md`. Memoria = K(vicine) − K(lontane), normalizzata, senza parole simili.', '',
          '| testo, variante | coppie vicine | coppie lontane | memoria (IC 95%) |', '|---|---|---|---|']
    for k, x in ris.items():
        d = x['dettaglio']
        if x['memoria'] is None or not d or not x['IC95']:
            md.append('| %s | — | — | n.d. |' % k)
            continue
        md.append('| %s | %d | %d | %+.4f (%+.4f – %+.4f) |' % (k, d['vicine'][1], d['lontane'][1], x['memoria'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Contrasto Voynich − insieme naturale: **%+.4f** (IC 95%% %+.4f – %+.4f).' % (mv - mn, ci[0], ci[1]), '',
           'Esito 1: **%s**. Esito 2: **%s**.' % (es1, es2)]
    open(os.path.join(RISULTATI, 'e3b53_varianti_naturali.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
