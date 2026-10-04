# -*- coding: utf-8 -*-
"""Esperimento e3c47: robustezza della finestra dello scriba anglosassone (e3c46: Hatton, þ/ð a inizio parola) e confronto
con il Voynich alle stesse condizioni. Varianti: unità (pagine) di 25 righe come nell'e3c46 e di 5 righe (lo scarto di
"pagina" toglie anche preferenze che cambiano su tratti brevi, circa 40 parole); per l'Hatton anche senza le 10 parole
con þ/ð iniziale più frequenti. Voynich ZL (k/t, sh/ch, -ey/-dy) con pagine intere e con blocchi di 5 righe.

Preregistrazione: preregistrazioni/e3c47.md. Scrive risultati/e3c47_scriba_robustezza.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3c28_forma_alla_pari as e3c28
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')


def r23(x):
    return (x['K'][1] + x['K'][2]) / 2 / x['K'][0] if x['K'][0] else float('nan')


def main():
    rng = np.random.default_rng(3347)
    parole = [w for r in e381.testi()[e3b54.STORICI['Hatton Gospels']] if r for w in r]
    lung = e3c28.lunghezze_voynich()
    rr = e3c28.righe_finte(parole, lung)
    frequenti = {w for w, _ in Counter(w for w in parole if e3b54.v_th_ini(w)).most_common(10)}
    senza = lambda w: None if w in frequenti else e3b54.v_th_ini(w)
    ris = OrderedDict()
    for nome, f, n in (('Hatton þ/ð, unità di 25 righe', e3b54.v_th_ini, 25), ('Hatton þ/ð, unità di 5 righe', e3b54.v_th_ini, 5),
                       ('Hatton þ/ð senza le 10 parole più frequenti, 25 righe', senza, 25), ('Hatton þ/ð senza le 10 parole più frequenti, 5 righe', senza, 5)):
        x = e3c34.misura([('x', rr[i:i + n]) for i in range(0, len(rr), n)], OrderedDict([('th', f)]), rng)
        x['r23'] = r23(x)
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    pagine, blocchi = [], []
    for pg, pars in e341.pagine().items():
        if not mano.get(pg):
            continue
        righe = [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]
        pagine.append((mano[pg], righe))
        for i in range(0, len(righe), 5):
            blocchi.append((mano[pg], righe[i:i + 5]))
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    for nome, pp in (('Voynich ZL, pagine intere', pagine), ('Voynich ZL, blocchi di 5 righe', blocchi)):
        x = e3c34.misura(pp, cl, rng)
        x['r23'] = r23(x)
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    hatton = [k for k in ris if k.startswith('Hatton')]
    regge = all(ris[k]['K1_IC95'][0] > 0 and ris[k]['r23'] >= 0.5 for k in hatton)
    cade = [k for k in hatton if not (ris[k]['K1_IC95'][0] > 0 and ris[k]['r23'] >= 0.5)]
    esito = 'la finestra dello scriba regge in tutte le varianti' if regge else 'la finestra dello scriba non regge in: ' + '; '.join(cade)
    out = OrderedDict([('varianti', ris), ('parole_tolte', sorted(''.join(w) for w in frequenti)), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c47_scriba_robustezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c47 — Robustezza della finestra dello scriba anglosassone, e il Voynich alle stesse condizioni', '', 'Preregistrazione: `preregistrazioni/e3c47.md`. Misura dell\'e3c34; r = media di K(2) e K(3) divisa per K(1).', '',
          '| variante | parole | K(1) (IC 95%) | K(2) | K(3) | r |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['r23']))
    md += ['', 'Parole tolte: %s.' % ', '.join(out['parole_tolte']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c47_scriba_robustezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
