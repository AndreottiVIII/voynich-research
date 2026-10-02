# -*- coding: utf-8 -*-
"""Esperimento 171: il legame alle giunture fra una parola e la successiva intinta (e166), contro le coppie senza
intinta a parita' di numero.

Preregistrazione: preregistrazioni/e171.md. Scrive risultati/e171_intinte_giunture.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e166_intinte as e166

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SOTTOCAMPIONI, BOOT = 171, 50, 200


def main():
    rnd = random.Random(SEME)
    righe, P = e166.pagine()
    I = e166.intinte(P)
    con, senza = [], []
    ini_con, ini_senza = [], []
    pulita = trascrizione.pulita
    for rr in P.values():
        for k, vals in rr:
            ps = righe[k][2]
            for j in range(1, len(ps) - 2):
                a, b = ps[j], ps[j + 1]
                if vals[j] is None or vals[j + 1] is None or (k, j + 1) not in I or not (pulita(a) and pulita(b)):
                    continue
                coppia = (e71.D(a)[-1], e71.D(b)[0])
                (con if I[(k, j + 1)] else senza).append(coppia)
                (ini_con if I[(k, j + 1)] else ini_senza).append(e71.D(b)[0] in ('y', 'd', 's'))
    print('coppie con intinta %d, senza %d' % (len(con), len(senza)), flush=True)
    e_con = e74.eccesso(con, rnd)
    sotto = [e74.eccesso(rnd.sample(senza, len(con)), rnd)['eccesso'] for _ in range(SOTTOCAMPIONI)]
    e_senza = statistics.mean(sotto)
    R = e_con['eccesso'] / e_senza if e_senza > 0 else None
    boot = []
    for _ in range(BOOT):
        b = [rnd.choice(con) for _ in con]
        boot.append(e74.eccesso(b, rnd)['eccesso'] / e_senza)
    boot.sort()
    lo, hi = boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]
    if R is not None and R < 0.5 and hi < 0.8:
        esito = 'l\'intinta spezza il legame'
    elif lo <= 1 <= hi:
        esito = 'nessun effetto'
    else:
        esito = 'effetto parziale'
    ris = OrderedDict([('coppie_con_intinta', len(con)), ('coppie_senza', len(senza)), ('eccesso_con', e_con), ('eccesso_senza_sottocampionato', e_senza),
                       ('Rint', R), ('intervallo', [lo, hi]), ('quota_yds_intinte', sum(ini_con) / len(ini_con) if ini_con else None),
                       ('quota_yds_altre', sum(ini_senza) / len(ini_senza) if ini_senza else None), ('esito', esito)])
    print('eccesso con intinta %.4f (z %.0f) | senza %.4f | Rint %.2f [%.2f, %.2f] | y/d/s: intinte %.3f, altre %.3f | %s' % (
        e_con['eccesso'], e_con['z'] or 0, e_senza, R or 0, lo, hi, ris['quota_yds_intinte'] or 0, ris['quota_yds_altre'] or 0, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e171_intinte_giunture.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e171 — Un\'intinta a metà riga spezza il legame fra parole vicine?', '',
           'Eccesso d\'informazione mutua (ultimo segno, primo segno) per coppie di parole interne adiacenti, secondo che la seconda sia '
           'un\'intinta (e166). Preregistrazione: `preregistrazioni/e171.md`.', '',
           '| | coppie | eccesso (bit) |', '|---|---|---|',
           '| con intinta | %d | %.4f (z %.0f) |' % (len(con), e_con['eccesso'], e_con['z'] or 0),
           '| senza (sottocampionate alla stessa numerosità, media di %d) | %d | %.4f |' % (SOTTOCAMPIONI, len(senza), e_senza), '',
           'Rint = %.2f, intervallo al 95%% [%.2f, %.2f]. Parole che iniziano con y/d/s: intinte %.3f, altre %.3f.' % (
               R or 0, lo, hi, ris['quota_yds_intinte'] or 0, ris['quota_yds_altre'] or 0), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e171_intinte_giunture.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
