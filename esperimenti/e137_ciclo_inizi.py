# -*- coding: utf-8 -*-
"""Esperimento 137: gli inizi di riga seguono un ciclo (ordine superiore al primo, periodicita' nel paragrafo)?
Contro una catena del primo ordine stimata sui dati.

Preregistrazione: preregistrazioni/e137.md. Scrive risultati/e137_ciclo_inizi.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e106_procedimento_versi as e106

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SIMULAZIONI, PP = 137, 1000, (2, 3, 4, 5, 6)
CICLO = ['D', 'y', 'o', 'G']


def sequenze_voynich(q):
    seq, cur, pag = [], [], None
    for r in trascrizione.testo_corrente(trascrizione.leggi(q)):
        if not r.parole:
            continue
        if r.inizio_par or r.pagina != pag:
            if len(cur) >= 2:
                seq.append(cur)
            cur = ['P']
            pag = r.pagina
            continue
        w = r.parole[0]
        cur.append(e106.classe(w) if trascrizione.pulita(w) else '?')
    if len(cur) >= 2:
        seq.append(cur)
    return seq


def sequenze_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    seq, cur = [], []
    for i, (ini, ps) in enumerate(rr):
        if ini or i % 29 == 0:
            if len(cur) >= 2:
                seq.append(cur)
            cur = ['P']
            continue
        cur.append(e106.classe(ps[0]) if ps else '?')
    if len(cur) >= 2:
        seq.append(cur)
    return seq


def cmi(seq):
    """I(c_i ; c_{i-2} | c_{i-1})."""
    tri = Counter((s[i - 2], s[i - 1], s[i]) for s in seq for i in range(2, len(s)))
    n = sum(tri.values())
    ab, bc, b = Counter(), Counter(), Counter()
    for (x, y, z), c in tri.items():
        ab[(x, y)] += c
        bc[(y, z)] += c
        b[y] += c
    return sum(c / n * math.log2(c * b[y] / (ab[(x, y)] * bc[(y, z)])) for (x, y, z), c in tri.items())


def mi_periodo(seq, p):
    return misure.informazione_mutua([((i % p), s[i]) for s in seq for i in range(1, len(s))])


def stat(seq):
    out = {'cmi': cmi(seq)}
    for p in PP:
        out['p%d' % p] = mi_periodo(seq, p)
    return out


def markov(seq, rnd):
    tr = defaultdict(Counter)
    for s in seq:
        for a, b in zip(s, s[1:]):
            tr[a][b] += 1
    tab = {a: (list(c), list(c.values())) for a, c in tr.items()}
    out = []
    for s in seq:
        x = ['P']
        for _ in range(len(s) - 1):
            st, w = tab.get(x[-1], tab['P'])
            x.append(rnd.choices(st, w)[0])
        out.append(x)
    return out


def ciclo(seq, rnd):
    classi = sorted({c for s in seq for c in s if c != 'P'})
    out = []
    for s in seq:
        x = ['P']
        for i in range(len(s) - 1):
            x.append(CICLO[i % len(CICLO)] if rnd.random() >= 0.3 else rnd.choice(classi))
        out.append(x)
    return out


def valuta(seq, rnd):
    reale = stat(seq)
    nulli = defaultdict(list)
    for _ in range(SIMULAZIONI):
        for k, v in stat(markov(seq, rnd)).items():
            nulli[k].append(v)
    out = OrderedDict([('paragrafi', len(seq)), ('righe', sum(len(s) - 1 for s in seq))])
    for k, v in reale.items():
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('reale', v), ('nullo', m), ('z', (v - m) / s if s else None)])
    return out


def main():
    rnd = random.Random(SEME)
    t = OrderedDict()
    t['Voynich ZL'] = sequenze_voynich('ZL')
    t['Voynich IT'] = sequenze_voynich('IT')
    t['controllo positivo: ciclo di 4 con 30% di rumore'] = ciclo(t['Voynich ZL'], random.Random(SEME + 1))
    t['Timm e Schinner, seme 19'] = sequenze_ts()
    ris = OrderedDict()
    for nome, seq in t.items():
        ris[nome] = r = valuta(seq, rnd)
        print('%-48s paragrafi %4d righe %5d | CMI %.4f (z %.1f) | %s' % (nome, r['paragrafi'], r['righe'], r['cmi']['reale'], r['cmi']['z'] or 0,
                                                                         ' '.join('p%d z %.1f' % (p, r['p%d' % p]['z'] or 0) for p in PP)), flush=True)
    zmax = lambda n: max([ris[n]['cmi']['z'] or 0] + [ris[n]['p%d' % p]['z'] or 0 for p in PP])
    valido = zmax('controllo positivo: ciclo di 4 con 30% di rumore') > 10
    numerazione = zmax('Voynich ZL') > 4 and zmax('Voynich IT') > 4
    ris['valido'], ris['numerazione'] = valido, numerazione
    print('controllo valido:', valido, '| numerazione:', numerazione)
    with open(os.path.join(RISULTATI, 'e137_ciclo_inizi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e137 — Gli inizi di riga seguono un ciclo?', '', 'Classe d\'inizio di riga (e105), sequenze per paragrafo; nullo: %d catene del primo ordine stimate sui dati. '
           'Preregistrazione: `preregistrazioni/e137.md`.' % SIMULAZIONI, '',
           '| testo | righe | ordine 2: CMI (z) | ' + ' | '.join('periodo %d (z)' % p for p in PP) + ' |', '|---|---|---|' + '---|' * len(PP)]
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.4f (%.1f) | %s |' % (nome, r['righe'], r['cmi']['reale'], r['cmi']['z'] or 0, ' | '.join('%.4f (%.1f)' % (r['p%d' % p]['reale'], r['p%d' % p]['z'] or 0) for p in PP)))
    out += ['', 'Controllo valido: **%s**. Numerazione: **%s**.' % ('sì' if valido else 'no', 'sì' if numerazione else 'no')]
    with open(os.path.join(RISULTATI, 'e137_ciclo_inizi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
