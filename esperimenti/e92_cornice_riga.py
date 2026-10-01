# -*- coding: utf-8 -*-
"""Esperimento 92: apertura e chiusura della riga sono accoppiate (cornice)?

Preregistrazione: preregistrazioni/e92.md. Scrive risultati/e92_cornice_riga.json e .md.
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
SEME, PERMUTAZIONI = 92, 500
D = e71.D


def voci(righe, i_a, i_b):
    """(pagina, primo segno della parola i_a, ultimo segno della parola i_b) per righe utili."""
    out = []
    for pag, ini, ps in righe:
        if ini or len(ps) < 4:
            continue
        a, b = ps[i_a], ps[i_b]
        if trascrizione.pulita(a) and trascrizione.pulita(b):
            out.append((pag, D(a)[0], D(b)[-1]))
    return out


def eccesso(vv, rnd):
    vera = misure.informazione_mutua([(a, b) for _, a, b in vv])
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(vv):
        per[p].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        bs = [b for _, _, b in vv]
        for idx in per.values():
            x = [bs[i] for i in idx]
            rnd.shuffle(x)
            for i, y in zip(idx, x):
                bs[i] = y
        nulli.append(misure.informazione_mutua([(a, b) for (_, a, _), b in zip(vv, bs)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(vv)), ('eccesso', vera - m), ('z', (vera - m) / s if s else None)])


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = e74.righe_voynich()
    t['Voynich A'] = e74.righe_voynich('A')
    t['Voynich B'] = e74.righe_voynich('B')
    ts = base['Timm e Schinner, seme 19'][0]
    t['Timm e Schinner, seme 19'] = [(i // 29, ini, ps) for i, (ini, ps) in enumerate(ts)]
    rc = base['Plinio codificato, a capo'][0]
    t['Plinio codificato, a capo'] = [(i // 20, ini, ps) for i, (ini, ps) in enumerate(rc)]
    rnd = random.Random(SEME)
    cp = []
    for i, (ini, ps) in enumerate(rc):
        a, z = ('y', 'm') if rnd.random() < 0.5 else ('s', 'g')
        ps = [a + ps[0]] + ps[1:-1] + [ps[-1] + z] if len(ps) >= 2 else ps
        cp.append((i // 20, ini, ps))
    t['controllo positivo: cornice y…m / s…g'] = cp
    ris = OrderedDict()
    for nome, righe in t.items():
        r = OrderedDict([('cornice', eccesso(voci(righe, 0, -1), random.Random(SEME))),
                         ('interno', eccesso(voci(righe, 1, -2), random.Random(SEME)))])
        ris[nome] = r
        print('%-40s cornice: n %4d %.4f (z %.1f) | interno (2a/penultima): n %4d %.4f (z %.1f)' % (
            nome, r['cornice']['n'], r['cornice']['eccesso'], r['cornice']['z'] or 0, r['interno']['n'],
            r['interno']['eccesso'], r['interno']['z'] or 0), flush=True)
    with open(os.path.join(RISULTATI, 'e92_cornice_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e92 — La riga ha una cornice?', '',
           'Eccesso d\'informazione mutua fra il primo segno della prima parola e l\'ultimo segno dell\'ultima (cornice), e fra '
           'seconda e penultima parola (interno), contro %d rimescolamenti nella pagina. Preregistrazione: '
           '`preregistrazioni/e92.md`.' % PERMUTAZIONI, '',
           '| testo | cornice: righe | eccesso (z) | interno: righe | eccesso (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        a, b = r['cornice'], r['interno']
        out.append('| %s | %d | %.4f (%.1f) | %d | %.4f (%.1f) |' % (nome, a['n'], a['eccesso'], a['z'] or 0, b['n'], b['eccesso'], b['z'] or 0))
    with open(os.path.join(RISULTATI, 'e92_cornice_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
