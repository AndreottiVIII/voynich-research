# -*- coding: utf-8 -*-
"""Esperimento 180: generatore e153 con tema di pagina (c = 1), theta e k variabili; pagella, riga, T1-T4.

Preregistrazione: preregistrazioni/e180.md. Scrive risultati/e180_tema_di_pagina.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
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
GRIGLIA = [(t, k) for t in (0.3, 0.5) for k in (3, 8)]
VOY_T3 = -0.5


def una(args):
    (theta, k), seme, rest = args[0], args[1], args[2:]
    e162.THETA, e162.C, e153.K = theta, 1.0, k
    _, r = e162.una(('x', seme, None) + tuple(rest))
    return (theta, k), r


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
        base = mm['riga_riprodotta'] and sum(esiti.values()) >= 9 and abs(mm.get('grezzo T3', 99) - VOY_T3) <= 2
        mm['pagina_e_T3'] = base
        mm['corregge'] = base and mm.get('ripulito T4', 99) < 0
        medie['θ %g, k %d' % g] = mm
    for n, mm in medie.items():
        print('%-12s %d/18 | riga %s | T3 %.1f T4r %.1f | pagina e T3 %s | corregge %s | mancano %s' % (n, sum(mm['esiti'].values()), mm['riga_riprodotta'],
              mm.get('grezzo T3', 0), mm.get('ripulito T4', 0), mm['pagina_e_T3'], mm['corregge'], [k for k, x in mm['esiti'].items() if not x]), flush=True)
    with open(os.path.join(RISULTATI, 'e180_tema_di_pagina.json'), 'w', encoding='utf-8') as fo:
        json.dump(medie, fo, ensure_ascii=False, indent=1, default=str)
    misure_t = [k for k in medie['θ 0.3, k 3'] if isinstance(k, str) and k.startswith(('grezzo', 'ripulito'))]
    out = ['# e180 — Tema di pagina invece che di riga', '', 'Generatore e153 con tema mantenuto per tutta la pagina (c = 1); medie su tre semi. Voynich: T3 grezzo −0,5, '
           'T4 ripulito −4,0. Preregistrazione: `preregistrazioni/e180.md`.', '',
           '| θ, k | pagella | riga | ' + ' | '.join(misure_t) + ' | pagina e T3 | corregge | mancanti |', '|---|---|---|' + '---|' * len(misure_t) + '---|---|---|']
    for n, mm in medie.items():
        out.append('| %s | %d/18 | %s | %s | %s | %s | %s |' % (n, sum(mm['esiti'].values()), 'sì' if mm['riga_riprodotta'] else 'no',
                   ' | '.join('%.1f' % (mm.get(k) or 0) for k in misure_t), 'sì' if mm['pagina_e_T3'] else 'no', 'sì' if mm['corregge'] else 'no',
                   ', '.join(k for k, x in mm['esiti'].items() if not x) or '–'))
    with open(os.path.join(RISULTATI, 'e180_tema_di_pagina.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
