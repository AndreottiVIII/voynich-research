# -*- coding: utf-8 -*-
"""Esperimento 87: la colonna delle prime parole segue la regola delle giunture in verticale?

Preregistrazione: preregistrazioni/e87.md. Scrive risultati/e87_colonna_iniziale.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e77_versi_sandhi as e77
import e80_verso_o_elastica_2 as e80

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 87, 500


def righe_voynich(lingua=None):
    """(pagina, paragrafo, inizio, parole)."""
    out, par = [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        if not r.parole:
            continue
        par += bool(r.inizio_par)
        out.append((r.pagina, par, bool(r.inizio_par), list(r.parole)))
    return out


def coppie(righe, dividi, pos):
    pulita = trascrizione.pulita
    dentro = {0: [], 1: []}
    vert = {0: [], 1: []}
    for k, (pag, par, ini, ps) in enumerate(righe):
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro[k % 2].append((dividi(a)[-1], dividi(b)[0]))
        if k + 1 < len(righe):
            pag2, par2, ini2, ps2 = righe[k + 1]
            if pag2 == pag and par2 == par and not ini and not ini2 and len(ps) > pos and len(ps2) > pos \
                    and pulita(ps[pos]) and pulita(ps2[pos]):
                vert[k % 2].append((pag, dividi(ps[pos])[-1], dividi(ps2[pos])[0]))
    return dentro, vert


def eccesso_pagina(cc, modello, rnd):
    if len(cc) < 10:
        return None
    vera = e80.statistica([(a, b) for _, a, b in cc], modello)
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(cc):
        per[p].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        bs = [b for _, _, b in cc]
        for idx in per.values():
            v = [bs[i] for i in idx]
            rnd.shuffle(v)
            for i, x in zip(idx, v):
                bs[i] = x
        nulli.append(e80.statistica([(a, b) for (_, a, _), b in zip(cc, bs)], modello))
    return vera - statistics.mean(nulli), statistics.pstdev(nulli)


def misura(nome, righe, dividi):
    rnd = random.Random(SEME)
    ris = OrderedDict()
    for etichetta, pos in (('prima', 0), ('seconda', 1)):
        dentro, vert = coppie(righe, dividi, pos)
        rif, vv = [], []
        for meta in (0, 1):
            modello = e80.Giunture(dentro[meta])
            altra = 1 - meta
            rif.append(e80.eccesso(dentro[altra], modello, rnd)[0])
            vv.append(eccesso_pagina(vert[altra], modello, rnd))
        e_rif = statistics.mean(rif)
        e_v = statistics.mean(x[0] for x in vv)
        se = (sum(x[1] ** 2 for x in vv) ** 0.5) / len(vv)
        ris[etichetta] = OrderedDict([('n', len(vert[0]) + len(vert[1])), ('riferimento', e_rif), ('eccesso', e_v),
                                      ('z', e_v / se if se else None), ('R', e_v / e_rif)])
    print('%-46s prima: n %4d R %.2f (z %.1f) | seconda: n %4d R %.2f (z %.1f)' % (
        nome, ris['prima']['n'], ris['prima']['R'], ris['prima']['z'] or 0, ris['seconda']['n'], ris['seconda']['R'],
        ris['seconda']['z'] or 0), flush=True)
    return ris


def main():
    e80.PERMUTAZIONI = PERMUTAZIONI
    t = OrderedDict()
    t['Voynich'] = (righe_voynich(), e71.D)
    t['Voynich A'] = (righe_voynich('A'), e71.D)
    t['Voynich B'] = (righe_voynich('B'), e71.D)
    versi = e77.mezzi_versi(*e77.TESTI['Manusmṛti'])
    neg = [(i // 20, i // 20, i % 20 == 0, list(ps)) for i, ps in enumerate(versi[:2000])]
    flusso = [w for ps in versi[2000:] for w in ps]
    pos = [(p, q, ini, [flusso[i]] + ps[1:]) for i, (p, q, ini, ps) in enumerate(neg)]
    t['controllo positivo: colonna = testo continuo'] = (pos, e71.lettere)
    t['controllo negativo: Manusmṛti'] = (neg, e71.lettere)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    rts, par = [], 0
    for i, (ini, ps) in enumerate(ts):
        par += ini
        rts.append((i // 29, par, ini, ps))
    t['Timm e Schinner, seme 19'] = (rts, e71.D)
    ris = OrderedDict((nome, misura(nome, rr, dv)) for nome, (rr, dv) in t.items())
    with open(os.path.join(RISULTATI, 'e87_colonna_iniziale.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e87 — La colonna delle prime parole è una sequenza con giunture?', '',
           'R = eccesso di verosimiglianza delle coppie verticali (ultimo segno della parola in posizione p della riga L → '
           'primo segno della parola in posizione p della riga L+1) sotto il modello delle giunture dentro la riga, diviso per '
           'quello delle coppie dentro la riga. Preregistrazione: `preregistrazioni/e87.md`.', '',
           '| testo | prima parola: coppie | R (z) | seconda parola: coppie | R (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        a, b = r['prima'], r['seconda']
        out.append('| %s | %d | %.2f (%.1f) | %d | %.2f (%.1f) |' % (nome, a['n'], a['R'], a['z'] or 0, b['n'], b['R'], b['z'] or 0))
    with open(os.path.join(RISULTATI, 'e87_colonna_iniziale.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
