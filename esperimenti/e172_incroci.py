# -*- coding: utf-8 -*-
"""Esperimento 172: generatore e165 (varianti attestate) con parole nuove per incrocio di due parole attestate in un
segno comune, con probabilita' nu.

Preregistrazione: preregistrazioni/e172.md. Scrive risultati/e172_incroci.json e .md.
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
import e165_varianti_attestate as e165
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e162.D
GRIGLIA = (0.0, 0.1, 0.25)
CANDIDATE_INCROCIO = 20
_NU = 0.0
_VOC = None


def incrocio(w, rnd):
    u = D(w)
    for _ in range(CANDIDATE_INCROCIO):
        v = D(rnd.choice(_VOC))
        comuni = [(i, j) for i, a in enumerate(u) for j, b in enumerate(v) if a == b and (i, j) != (0, 0)]
        if comuni:
            i, j = rnd.choice(comuni)
            return ''.join(u[:i] + v[j:])
    return w


def variante(w, mu, mod, rnd):
    x = e165.variante_attestata(w, mu, mod, rnd)
    if _NU and trascrizione.pulita(x) and rnd.random() < _NU:
        x = incrocio(x, rnd)
    return x


def una(args):
    global _NU, _VOC
    nu, seme, rest = args[0], args[1], args[2:]
    if e165._ATTESTATE is None:
        e165._ATTESTATE = set(rest[4])
    if _VOC is None:
        _VOC = sorted({w for w in rest[4] if trascrizione.pulita(w)})
    _NU = nu
    e153.LAM = 1.0
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
    base = medie['ν 0']['esiti']
    for n, mm in medie.items():
        mm['guadagnate'] = [k for k in base if mm['esiti'][k] and not base[k]]
        mm['perse'] = [k for k in base if base[k] and not mm['esiti'][k]]
        print('%-8s %d/18 | riga %s | completo %s | mancano %s | +%s -%s' % (n, sum(mm['esiti'].values()), mm['riga_riprodotta'], mm['completo'],
              [k for k, x in mm['esiti'].items() if not x], mm['guadagnate'], mm['perse']), flush=True)
    with open(os.path.join(RISULTATI, 'e172_incroci.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'voynich': v}, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e172 — Parole nuove per incrocio di parole attestate', '', 'Generatore e165 (varianti attestate, λ 1, θ 0,3) con incroci di probabilità ν; medie su tre semi. '
           'Preregistrazione: `preregistrazioni/e172.md`.', '', '| ν | pagella | riga | completo | guadagnate rispetto a ν 0 | perse | mancanti |', '|---|---|---|---|---|---|---|']
    for n, mm in medie.items():
        out.append('| %s | %d/18 | %s | %s | %s | %s | %s |' % (n, sum(mm['esiti'].values()), 'sì' if mm['riga_riprodotta'] else 'no', 'sì' if mm['completo'] else 'no',
                   ', '.join(mm['guadagnate']) or '–', ', '.join(mm['perse']) or '–', ', '.join(k for k, x in mm['esiti'].items() if not x) or '–'))
    with open(os.path.join(RISULTATI, 'e172_incroci.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
