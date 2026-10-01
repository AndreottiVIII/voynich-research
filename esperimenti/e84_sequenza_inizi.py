# -*- coding: utf-8 -*-
"""Esperimento 84: oltre all'evitamento, gli inizi di riga consecutivi hanno passaggi preferiti (fuori diagonale)
o asimmetrici (sequenza)?

Preregistrazione: preregistrazioni/e84.md. Scrive risultati/e84_sequenza_inizi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e83_evitamento_inizi as e83

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 84, 500


def statistiche(cc):
    fuori = [(a, b) for a, b in cc if a != b]
    t = Counter(cc)
    segni = sorted({a for a, _ in cc} | {b for _, b in cc})
    bowker = 0.0
    for i, x in enumerate(segni):
        for y in segni[i + 1:]:
            s = t[(x, y)] + t[(y, x)]
            if s:
                bowker += (t[(x, y)] - t[(y, x)]) ** 2 / s
    return {'fuori': misure.informazione_mutua(fuori), 'bowker': bowker,
            'stessa': sum(a == b for a, b in cc) / len(cc)}


def misura(per, rnd):
    reale = [c for rr in per.values() for c in e83.coppie(rr, 1, e83.primo_eva)]
    v = statistiche(reale)
    nulli = {k: [] for k in v}
    for _ in range(PERMUTAZIONI):
        cc = []
        for rr in per.values():
            idx = [i for i, (_, ini, _) in enumerate(rr) if not ini]
            parole = [rr[i][2] for i in idx]
            rnd.shuffle(parole)
            nuova = list(rr)
            for i, w in zip(idx, parole):
                nuova[i] = (rr[i][0], False, w)
            cc.extend(e83.coppie(nuova, 1, e83.primo_eva))
        for k, x in statistiche(cc).items():
            nulli[k].append(x)
    out = OrderedDict([('n', len(reale))])
    for k in v:
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('reale', v[k]), ('nullo', m), ('z', (v[k] - m) / s if s else None)])
    out['S'] = v['stessa'] / out['stessa']['nullo']
    return out


def da_righe(righe, righe_pagina):
    """righe: liste di parole -> formato di e83.pagine (un paragrafo per pagina, prima riga = inizio)."""
    per = OrderedDict()
    for i, ps in enumerate(righe):
        p = i // righe_pagina
        per.setdefault(p, []).append((p, i % righe_pagina == 0, ps[0] if ps else None))
    return per


def main():
    import e73_bordo_interno as e73
    import e71_bordo_riga as e71
    base = e73.testi()
    rc = [ps for _, ps in base['Plinio codificato, a capo'][0]]
    t = OrderedDict()
    t['Voynich'] = e83.pagine('ZL')
    t['Voynich A'] = e83.pagine('ZL', lingua='A')
    t['Voynich B'] = e83.pagine('ZL', lingua='B')
    marcatori = ('s', 'y', 'd')
    t['controllo: sequenza (marcatore a ciclo)'] = da_righe([[marcatori[(i % 20) % 3] + ps[0]] + ps[1:] for i, ps in enumerate(rc)], 20)
    rnd = random.Random(SEME)
    prime = [ps[0] for ps in rc]
    evit = []
    for i, ps in enumerate(rc):
        ps = list(ps)
        if i % 20 and evit and e83.primo_eva(ps[0]) == e83.primo_eva(evit[-1][0]):
            while True:
                w = prime[rnd.randrange(len(prime))]
                if e83.primo_eva(w) != e83.primo_eva(evit[-1][0]):
                    break
            ps[0] = w
        evit.append(ps)
    t['controllo: solo evitamento'] = da_righe(evit, 20)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    per = OrderedDict()
    par = 0
    for i, (ini, ps) in enumerate(ts):
        par += ini
        per.setdefault(i // 29, []).append((par, ini, ps[0]))
    t['Timm e Schinner, seme 19'] = per
    ris = OrderedDict()
    for nome, p in t.items():
        r = misura(p, random.Random(SEME))
        ris[nome] = r
        print('%-42s n %5d | S %.2f | fuori diagonale %.4f (nullo %.4f, z %.1f) | asimmetria %.1f (nullo %.1f, z %.1f)' % (
            nome, r['n'], r['S'], r['fuori']['reale'], r['fuori']['nullo'], r['fuori']['z'] or 0,
            r['bowker']['reale'], r['bowker']['nullo'], r['bowker']['z'] or 0), flush=True)
    with open(os.path.join(RISULTATI, 'e84_sequenza_inizi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e84 — Sequenza o solo evitamento fra inizi di riga?', '',
           'IM fuori dalla diagonale (coppie con segni diversi) e statistica di simmetria di Bowker, contro %d rimescolamenti. '
           'Preregistrazione: `preregistrazioni/e84.md`.' % PERMUTAZIONI, '',
           '| testo | coppie | S | fuori diagonale (z) | asimmetria (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %d | %.2f | %.4f (%.1f) | %.1f (%.1f) |' % (nome, r['n'], r['S'], r['fuori']['reale'], r['fuori']['z'] or 0,
                                                              r['bowker']['reale'], r['bowker']['z'] or 0))
    with open(os.path.join(RISULTATI, 'e84_sequenza_inizi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
