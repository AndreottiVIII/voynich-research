# -*- coding: utf-8 -*-
"""Esperimento 192: generatore con tema di pagina (e180) e varianti attestate, piu' varianti nuove ben formate con
probabilita' nu.

Preregistrazione: preregistrazioni/e192.md. Scrive risultati/e192_generatore_misto.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e162.D
GRIGLIA = (0.2, 0.4, 0.6)
_NU, _ATT = 0.0, None


def variante(w, mu, mod, rnd):
    u = tuple(D(w))
    for _ in range(generatori.poisson(rnd, mu)):
        v = mod.modifica(u, rnd)
        if ''.join(v) in _ATT or (mod.valida(v) and rnd.random() < _NU):
            u = v
    return ''.join(u)


def una(args):
    global _NU, _ATT
    nu, seme, rest = args[0], args[1], args[2:]
    if _ATT is None:
        _ATT = set(rest[4])
    _NU = nu
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e153.variante = variante
    _, r = e162.una(('x', seme, None) + tuple(rest))
    return nu, r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    lavori = [(nu, s, P, starts, q, L, voy, soglia_ab, v, vb) for nu in GRIGLIA for s in e162.SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nu, r in pool.imap(una, lavori):
            per[nu].append(r)
    medie = OrderedDict()
    for nu in GRIGLIA:
        gruppo = per[nu]
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(y.get(k), (int, float)) for y in gruppo)]
        mm = {k: sum(y[k] for y in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(mm, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= mm['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= mm['bordo_fine'] <= 2 * vb[1]
        mm['esiti'] = esiti
        R = mm['R_riga'] if mm.get('R_riga') is not None else 1
        mm['riga_riprodotta'] = (mm['S1'] <= 0.7 and R < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3 and abs(mm['r_righe_consecutive'] - e145.VOY_R1) <= 0.07)
        mm['completo'] = mm['riga_riprodotta'] and sum(esiti.values()) >= 12
        medie['ν %g' % nu] = mm
        print('ν %-4g %d/18 | riga %s | completo %s | T3 %.1f T4r %.1f | mancano %s' % (nu, sum(esiti.values()), mm['riga_riprodotta'], mm['completo'],
              mm.get('grezzo T3', 0), mm.get('ripulito T4', 0), [k for k, x in esiti.items() if not x]), flush=True)
    with open(os.path.join(RISULTATI, 'e192_generatore_misto.json'), 'w', encoding='utf-8') as fo:
        json.dump(medie, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e192 — Tema di pagina e varianti in parte attestate', '', 'Generatore e180 (θ 0,3, k 3, tema di pagina) con varianti attestate più varianti nuove ben formate '
           'con probabilità ν; medie su tre semi. Preregistrazione: `preregistrazioni/e192.md`.', '', '| ν | pagella | riga | completo | T3 grezzo | T4 ripulito | mancanti |',
           '|---|---|---|---|---|---|---|']
    for n, mm in medie.items():
        out.append('| %s | %d/18 | %s | %s | %.1f | %.1f | %s |' % (n, sum(mm['esiti'].values()), 'sì' if mm['riga_riprodotta'] else 'no', 'sì' if mm['completo'] else 'no',
                   mm.get('grezzo T3', 0), mm.get('ripulito T4', 0), ', '.join(k for k, x in mm['esiti'].items() if not x) or '–'))
    with open(os.path.join(RISULTATI, 'e192_generatore_misto.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
