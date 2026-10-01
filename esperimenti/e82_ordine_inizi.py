# -*- coding: utf-8 -*-
"""Esperimento 82: i primi segni delle righe consecutive dipendono l'uno dall'altro (ordine, numerazione)?

Preregistrazione: preregistrazioni/e82.md. Scrive risultati/e82_ordine_inizi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 82, 500
D = e71.D


def coppie(righe, posizione):
    out = []
    for k in range(len(righe) - 1):
        pag, _, ps = righe[k]
        pag2, inizio2, ps2 = righe[k + 1]
        if pag2 != pag or inizio2 or len(ps) <= posizione or len(ps2) <= posizione:
            continue
        a, b = ps[posizione], ps2[posizione]
        if trascrizione.pulita(a) and trascrizione.pulita(b):
            out.append((pag, D(a)[0], D(b)[0]))
    return out


def eccesso(cc, rnd):
    vera = misure.informazione_mutua([(x, y) for _, x, y in cc])
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(cc):
        per[p].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        ys = [y for _, _, y in cc]
        for idx in per.values():
            v = [ys[i] for i in idx]
            rnd.shuffle(v)
            for i, y in zip(idx, v):
                ys[i] = y
        nulli.append(misure.informazione_mutua([(x, y) for (_, x, _), y in zip(cc, ys)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(cc)), ('eccesso', vera - m), ('z', (vera - m) / s if s else None)])


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = e74.righe_voynich()
    t['Voynich A'] = e74.righe_voynich('A')
    t['Voynich B'] = e74.righe_voynich('B')
    for s in (19, 1, 2):
        rr = base['Timm e Schinner, seme %d' % s][0]
        t['Timm e Schinner, seme %d' % s] = [(i // 29, inizio, ps) for i, (inizio, ps) in enumerate(rr)]
    rc = base['Plinio codificato, a capo'][0]
    marcatori = ('s', 'y', 'd')
    t['controllo positivo: marcatore a ciclo'] = [(i // 20, False, [marcatori[(i % 20) % 3] + ps[0]] + ps[1:]) for i, (_, ps) in enumerate(rc)]
    t['controllo negativo: senza marcatore'] = [(i // 20, False, ps) for i, (_, ps) in enumerate(rc)]
    ris = OrderedDict()
    for nome, righe in t.items():
        rnd = random.Random(SEME)
        prima = eccesso(coppie(righe, 0), rnd)
        seconda = eccesso(coppie(righe, 1), rnd)
        ris[nome] = OrderedDict([('prima_parola', prima), ('seconda_parola', seconda)])
        print('%-40s prima: n %5d eccesso %.4f (z %.1f) | seconda: n %5d eccesso %.4f (z %.1f)' % (
            nome, prima['n'], prima['eccesso'], prima['z'] or 0, seconda['n'], seconda['eccesso'], seconda['z'] or 0), flush=True)
    with open(os.path.join(RISULTATI, 'e82_ordine_inizi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e82 — I segni d\'inizio riga seguono un ordine?', '',
           'Eccesso d\'informazione mutua fra il primo segno della prima (o seconda) parola di righe consecutive, contro %d '
           'permutazioni dentro la pagina. Preregistrazione: `preregistrazioni/e82.md`.' % PERMUTAZIONI, '',
           '| testo | prima parola: n | eccesso (z) | seconda parola: n | eccesso (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        a, b = r['prima_parola'], r['seconda_parola']
        out.append('| %s | %d | %.4f (%.1f) | %d | %.4f (%.1f) |' % (nome, a['n'], a['eccesso'], a['z'] or 0, b['n'], b['eccesso'], b['z'] or 0))
    with open(os.path.join(RISULTATI, 'e82_ordine_inizi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
