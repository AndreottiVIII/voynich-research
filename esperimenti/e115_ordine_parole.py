# -*- coding: utf-8 -*-
"""Esperimento 115: le parole frequenti hanno un ordine relativo preferito nella riga (oltre la posizione)?

Preregistrazione: preregistrazioni/e115.md. Scrive risultati/e115_ordine_parole.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e114_accordo_terminazioni as e114

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_PAROLE, TIPI, MIN_COPPIE = 115, 200, 8, 40, 10


def interne(righe):
    return [ps[2:-2] for ps in righe if len(ps) >= MIN_PAROLE and all(trascrizione.pulita(w) for w in ps)]


def bowker(rr, frequenti):
    c = Counter()
    for r in rr:
        idx = [(i, w) for i, w in enumerate(r) if w in frequenti]
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                (i, x), (j, y) = idx[a], idx[b]
                if j - i >= 2 and x != y:
                    c[(x, y)] += 1
    stat, n = 0.0, 0
    fatti = set()
    for (x, y), nxy in c.items():
        if (y, x) in fatti or (x, y) in fatti:
            continue
        fatti.add((x, y))
        nyx = c[(y, x)]
        if nxy + nyx >= MIN_COPPIE:
            stat += (nxy - nyx) ** 2 / (nxy + nyx)
            n += 1
    return stat, n


def terzile(i, L):
    return min(2, 3 * i // L)


def una(args):
    nome, righe = args
    rr = interne(righe)
    frequenti = {w for w, _ in Counter(w for r in rr for w in r).most_common(TIPI)}
    reale, coppie = bowker(rr, frequenti)
    rnd = random.Random(SEME)
    n1, n2 = [], []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in rr:
            r = r[:]
            rnd.shuffle(r)
            mes.append(r)
        n1.append(bowker(mes, frequenti)[0])
        mes = []
        for r in rr:
            L = len(r)
            gruppi = {}
            for i, w in enumerate(r):
                gruppi.setdefault(terzile(i, L), []).append(i)
            nuova = r[:]
            for idx in gruppi.values():
                v = [r[i] for i in idx]
                rnd.shuffle(v)
                for i, w in zip(idx, v):
                    nuova[i] = w
            mes.append(nuova)
        n2.append(bowker(mes, frequenti)[0])
    out = OrderedDict([('righe', len(rr)), ('coppie_di_tipi', coppie), ('bowker', reale)])
    for nome_n, nul in (('nullo_riga', n1), ('nullo_terzili', n2)):
        m, s = statistics.mean(nul), statistics.pstdev(nul)
        out[nome_n] = OrderedDict([('media', m), ('z', (reale - m) / s if s else None)])
    out['z_per_coppia'] = (out['nullo_terzili']['z'] or 0) / max(1, coppie) ** 0.5
    return nome, out


def main():
    t = e114.testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, rr) for n, (rr, _) in t.items()]):
            ris[nome] = r
            print('%-26s righe %5d coppie %4d | Bowker %.1f | z (riga) %.1f | z (terzili) %.1f | z/sqrt(coppie) %.2f' % (
                nome, r['righe'], r['coppie_di_tipi'], r['bowker'], r['nullo_riga']['z'] or 0, r['nullo_terzili']['z'] or 0, r['z_per_coppia']), flush=True)
    voy = all((ris[n]['nullo_riga']['z'] or 0) > 4 and (ris[n]['nullo_terzili']['z'] or 0) > 4 for n in ('Voynich ZL', 'Voynich IT'))
    ris['ordine_voynich'] = voy
    print('ordine relativo nel Voynich:', voy)
    with open(os.path.join(RISULTATI, 'e115_ordine_parole.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e115 — Le parole frequenti hanno un ordine preferito?', '', 'Statistica di Bowker sulle coppie ordinate dei %d tipi più '
           'frequenti (parole dalla terza alla terzultima, distanza ≥ 2), contro %d rimescolamenti nella riga e nei terzili. '
           'Preregistrazione: `preregistrazioni/e115.md`.' % (TIPI, RIMESCOLAMENTI), '',
           '| testo | righe | coppie di tipi | Bowker | z (riga) | z (terzili) | z / √coppie |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %d | %.1f | %.1f | %.1f | %.2f |' % (nome, r['righe'], r['coppie_di_tipi'], r['bowker'], r['nullo_riga']['z'] or 0,
                                                                   r['nullo_terzili']['z'] or 0, r['z_per_coppia']))
    out += ['', 'Ordine relativo nel Voynich: **%s**.' % ('sì' if voy else 'no')]
    with open(os.path.join(RISULTATI, 'e115_ordine_parole.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
