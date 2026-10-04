# -*- coding: utf-8 -*-
"""Esperimento e3c59: la finestra trovata in uno scriba vero (AM 302 fol, ſ/s; e3c58) e quella al limite (Holm A 10, ꝛ/r)
messe alle stesse prove superate dal Voynich: unità di 5 righe (toglie le preferenze di tratti brevi, e3c47 – e3c48) e
nullo che conserva la posizione nella riga con il suo placebo (e3c57). Riferimento nella stessa esecuzione: Voynich ZL
(k/t, sh/ch, -ey/-dy).

Preregistrazione: preregistrazioni/e3c59.md. Scrive risultati/e3c59_finestra_scriba_prove.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b62_memoria_nullo_largo as e3b62
import e3c57_finestra_posizione as e3c57
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
SCRIBI = [('AM-302-fol', 'ſ/s'), ('Holm-A-10', 'ꝛ/r')]


def blocchi(pagine, n=5):
    return [(h, rr[i:i + n]) for h, rr in pagine for i in range(0, len(rr), n)]


def regge(y):
    return y['K1_IC95'][0] > 0.02 and y['K23_IC95'][0] > 0.02


def main():
    e3c57.PERM = 50
    rng = np.random.default_rng(3359)
    testi = OrderedDict()
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    testi['Voynich ZL (k/t, sh/ch, -ey/-dy)'] = ([(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in e341.pagine().items() if mano.get(pg)],
                                                 OrderedDict((k, e3b62.CV[k]) for k in TRE))
    fn = {nome: e3c58.scelta(aa, bb) for nome, aa, bb in e3c58.COPPIE}
    for ms, nome in SCRIBI:
        testi['%s, %s' % (ms, nome)] = ([(h, rr) for _, h, rr in e3c58.leggi(ms)], OrderedDict([(nome, fn[nome])]))
    ris = OrderedDict()
    for k, (pagine, cl) in testi.items():
        for unita, pp in (('pagine', pagine), ('blocchi di 5 righe', blocchi(pagine))):
            x = e3c57.misura(pp, cl, rng)
            ris['%s | %s' % (k, unita)] = x
            print(k, unita, json.dumps(x, ensure_ascii=False), flush=True)
    esiti = OrderedDict()
    for k in testi:
        b = ris['%s | blocchi di 5 righe' % k]
        if regge(b['nullo P']):
            esiti[k] = 'la finestra regge alle due prove'
        elif b['nullo A']['K23_IC95'][0] <= 0 <= b['nullo A']['K23_IC95'][1] or b['nullo P']['K23_IC95'][0] <= 0 <= b['nullo P']['K23_IC95'][1]:
            esiti[k] = 'la finestra non regge (viene da tratti brevi o dalla posizione)'
        else:
            esiti[k] = 'incerto'
    out = OrderedDict([('misure', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c59_finestra_scriba_prove.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c59 — La finestra dello scriba di AM 302 fol alle prove superate dal Voynich', '',
          'Preregistrazione: `preregistrazioni/e3c59.md`. Nulli: A = e3c48; P = con la fascia di posizione; R = placebo (e3c57).', '',
          '| testo | unità | nullo | K corretto 1 (IC 95%) | K corretto 2–3 (IC 95%) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        t, u = k.split(' | ')
        for n in ('A', 'P', 'R'):
            y = x['nullo ' + n]
            md.append('| %s | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) |' % (t, u, n, y['K_corretto'][0], y['K1_IC95'][0], y['K1_IC95'][1], y['K23'], y['K23_IC95'][0], y['K23_IC95'][1]))
    md += [''] + ['- %s: **%s**' % kv for kv in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c59_finestra_scriba_prove.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
