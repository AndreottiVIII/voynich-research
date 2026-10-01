# -*- coding: utf-8 -*-
"""Esperimento 81: direzione della giuntura. IM condizionata regressiva (fine di w1 ~ inizio di w2 | radice di w1)
e progressiva (inizio di w2 ~ fine di w1 | corpo di w2), contro permutazioni dentro i gruppi.

Preregistrazione: preregistrazioni/e81.md. Scrive risultati/e81_direzione_giuntura.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e77_versi_sandhi as e77

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 81, 100


def quadruple(righe, dividi):
    """(radice w1, ultimo w1, primo w2, corpo w2) per parole interne vicine."""
    out = []
    for _, ps in righe:
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if trascrizione.pulita(a) and trascrizione.pulita(b):
                u, v = tuple(dividi(a)), tuple(dividi(b))
                if len(u) >= 2 and len(v) >= 2:
                    out.append((u[:-1], u[-1], v[0], v[1:]))
    return out


def im_condizionata(terne):
    """terne: (gruppo, x, y) -> somma_g p(g) IM(x; y | g)."""
    per = defaultdict(list)
    for g, x, y in terne:
        per[g].append((x, y))
    n = len(terne)
    return sum(len(cc) / n * misure.informazione_mutua(cc) for cc in per.values() if len(cc) > 1)


def permuta_nei_gruppi(terne, rnd):
    per = defaultdict(list)
    for i, (g, _, _) in enumerate(terne):
        per[g].append(i)
    ys = [y for _, _, y in terne]
    for idx in per.values():
        valori = [ys[i] for i in idx]
        rnd.shuffle(valori)
        for i, y in zip(idx, valori):
            ys[i] = y
    return [(g, x, y) for (g, x, _), y in zip(terne, ys)]


def eccesso_cond(terne, rnd):
    vera = im_condizionata(terne)
    nulli = [im_condizionata(permuta_nei_gruppi(terne, rnd)) for _ in range(PERMUTAZIONI)]
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('im', vera), ('nullo', m), ('eccesso', vera - m), ('z', (vera - m) / s if s else None)])


def una(args):
    nome, righe, quale = args
    dividi = e71.lettere if quale == 'lettere' else e71.D
    q = quadruple(righe, dividi)
    rnd = random.Random(SEME)
    totale = eccesso_cond([(0, f, i) for _, f, i, _ in q], rnd)
    reg = eccesso_cond([(r, f, i) for r, f, i, _ in q], rnd)
    pro = eccesso_cond([(c, i, f) for _, f, i, c in q], rnd)
    r = OrderedDict([('coppie', len(q)), ('totale', totale), ('regressiva', reg), ('progressiva', pro)])
    t = totale['eccesso']
    r['quota_regressiva'] = reg['eccesso'] / t if t > 0 else None
    r['quota_progressiva'] = pro['eccesso'] / t if t > 0 else None
    r['rapporto_direzione'] = reg['eccesso'] / pro['eccesso'] if pro['eccesso'] > 0 else None
    return nome, r


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = base['Voynich']
    t['Voynich A'] = base['Voynich A']
    t['Voynich B'] = base['Voynich B']
    for nome, (f, sha) in e77.TESTI.items():
        versi = e77.mezzi_versi(f, sha)
        t[nome + ', un mezzo verso per riga'] = ([(False, ps) for ps in versi], 'lettere')
    t['Plinio, a capo'] = base['Plinio, a capo']
    t['+ giunture (e23), seme 19'] = (e71.righe_file(os.path.join(e71.CACHE, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt')), 'eva')
    t['modello e51, seme 19'] = base['modello e51, seme 19']
    t['Timm e Schinner, seme 19'] = base['Timm e Schinner, seme 19']
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in t.items()]):
            ris[nome] = r
            f = lambda x: '%.2f' % x if x is not None else '-'
            print('%-40s coppie %6d | totale %.4f (z %.0f) | regressiva %.4f (z %.1f) quota %s | progressiva %.4f (z %.1f) quota %s | rapporto %s' % (
                nome, r['coppie'], r['totale']['eccesso'], r['totale']['z'] or 0, r['regressiva']['eccesso'],
                r['regressiva']['z'] or 0, f(r['quota_regressiva']), r['progressiva']['eccesso'], r['progressiva']['z'] or 0,
                f(r['quota_progressiva']), f(r['rapporto_direzione'])), flush=True)
    with open(os.path.join(RISULTATI, 'e81_direzione_giuntura.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e81 — Direzione della giuntura', '',
           'Eccesso d\'informazione mutua (bit) fra ultimo segno di w1 e primo di w2: totale; regressiva (a parità di radice '
           'di w1); progressiva (a parità di corpo di w2). Quote = eccesso / totale. Preregistrazione: '
           '`preregistrazioni/e81.md`.', '',
           '| testo | coppie | totale | regressiva (quota) | progressiva (quota) | rapporto reg./prog. |', '|---|---|---|---|---|---|']
    g = lambda x: '%.2f' % x if x is not None else '–'
    for nome, r in ris.items():
        out.append('| %s | %d | %.4f (z %.0f) | %.4f (%s) | %.4f (%s) | %s |' % (
            nome, r['coppie'], r['totale']['eccesso'], r['totale']['z'] or 0, r['regressiva']['eccesso'], g(r['quota_regressiva']),
            r['progressiva']['eccesso'], g(r['quota_progressiva']), g(r['rapporto_direzione'])))
    with open(os.path.join(RISULTATI, 'e81_direzione_giuntura.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
