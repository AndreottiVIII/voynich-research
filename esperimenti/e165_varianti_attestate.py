# -*- coding: utf-8 -*-
"""Esperimento 165: generatore e153 (temi a caso) con varianti solo fra parole attestate e/o giunture piu' forti.

Preregistrazione: preregistrazioni/e165.md. Scrive risultati/e165_varianti_attestate.json e .md.
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
GRIGLIA = [('Modifiche', 1.0), ('Modifiche', 2.0), ('attestate', 1.0), ('attestate', 2.0)]
_ATTESTATE = None
_ORIGINALE = e153.variante


def variante_attestata(w, mu, mod, rnd):
    u = tuple(D(w))
    for _ in range(generatori.poisson(rnd, mu)):
        v = mod.modifica(u, rnd)
        if ''.join(v) in _ATTESTATE:
            u = v
    return ''.join(u)


def una(args):
    global _ATTESTATE
    (modo, lam), seme, rest = args[0], args[1], args[2:]
    if _ATTESTATE is None:
        _ATTESTATE = set(rest[4])
    e153.LAM = lam
    e153.variante = variante_attestata if modo == 'attestate' else _ORIGINALE
    _, r = e162.una(('x', seme, None) + tuple(rest))
    return (modo, lam), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    lavori = [(g, s, P, starts, q, L, voy, soglia_ab, v, vb) for g in GRIGLIA for s in e162.SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for g, r in pool.imap(una, lavori):
            per[g].append(r)
    medie = OrderedDict()
    for g in GRIGLIA:
        gruppo = per[g]
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
        medie['%s, λ %g' % g] = mm
    base = medie['Modifiche, λ 1']['esiti']
    for n, mm in medie.items():
        mm['guadagnate'] = [k for k in base if mm['esiti'][k] and not base[k]]
        mm['perse'] = [k for k in base if base[k] and not mm['esiti'][k]]
        print('%-22s %d/18 | riga %s | completo %s | h2 %s tipi %s | +%s -%s' % (n, sum(mm['esiti'].values()), mm['riga_riprodotta'], mm['completo'],
              ('%.3f' % mm['h2']) if 'h2' in mm else '-', ('%.3f' % mm['tipi']) if 'tipi' in mm else '-', mm['guadagnate'], mm['perse']), flush=True)
    with open(os.path.join(RISULTATI, 'e165_varianti_attestate.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'voynich': v}, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e165 — Generatore di righe con varianti attestate e giunture più forti', '',
           'Generatore e153 (θ 0,3, temi a caso), medie su tre semi. Preregistrazione: `preregistrazioni/e165.md`.', '',
           '| varianti, λ | pagella | riga | completo | guadagnate rispetto all\'e153 | perse |', '|---|---|---|---|---|---|']
    for n, mm in medie.items():
        out.append('| %s | %d/18 | %s | %s | %s | %s |' % (n, sum(mm['esiti'].values()), 'sì' if mm['riga_riprodotta'] else 'no', 'sì' if mm['completo'] else 'no',
                                                     ', '.join(mm['guadagnate']) or '–', ', '.join(mm['perse']) or '–'))
    out += ['', 'Proprietà mancanti per combinazione:', '']
    for n, mm in medie.items():
        out.append('- %s: %s' % (n, ', '.join(k for k, x in mm['esiti'].items() if not x) or 'nessuna'))
    with open(os.path.join(RISULTATI, 'e165_varianti_attestate.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
