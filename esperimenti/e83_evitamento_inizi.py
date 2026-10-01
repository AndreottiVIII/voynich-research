# -*- coding: utf-8 -*-
"""Esperimento 83: robustezza dell'evitamento fra inizi di riga (trascrizioni, lingue, sezioni, distanze,
segno aggiunto tolto, parola intera).

Preregistrazione: preregistrazioni/e83.md. Scrive risultati/e83_evitamento_inizi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 83, 500
D = misure.divisore(misure.GLIFI_EVA)
AGGIUNTI = {'y', 'd', 's', 'o'}


def primo_eva(w):
    return D(w)[0]


def primo_car(w):
    return w[0]


def senza_aggiunto(w):
    u = D(w)
    return u[1] if len(u) >= 3 and u[0] in AGGIUNTI else u[0]


def parola(w):
    return w


def pagine(quale='ZL', lingua=None, sezioni=None, esclusa=False):
    """Per pagina: lista di (paragrafo, inizio paragrafo, prima parola o None)."""
    per = OrderedDict()
    par = 0
    for r in trascrizione.testo_corrente(trascrizione.leggi(quale), lingua=lingua):
        if sezioni is not None and ((r.sezione in sezioni) == esclusa):
            continue
        if not r.parole:
            continue
        if r.inizio_par:
            par += 1
        w = r.parole[0] if trascrizione.pulita(r.parole[0]) else None
        per.setdefault(r.pagina, []).append((par, bool(r.inizio_par), w))
    return per


def coppie(seq, k, chiave):
    out = []
    for i in range(len(seq) - k):
        (p1, i1, a), (p2, i2, b) = seq[i], seq[i + k]
        if p1 == p2 and not i1 and not i2 and a is not None and b is not None:
            out.append((chiave(a), chiave(b)))
    return out


def quota_stessa(cc):
    return sum(a == b for a, b in cc) / len(cc) if cc else None


def misura(per, k, chiave, rnd):
    reale = [c for rr in per.values() for c in coppie(rr, k, chiave)]
    q = quota_stessa(reale)
    nulli = []
    for _ in range(PERMUTAZIONI):
        cc = []
        for rr in per.values():
            # rimescola l'ordine delle righe non d'inizio paragrafo; ogni riga tiene il suo paragrafo
            # nella posizione in cui cade (le coppie restano dentro lo stesso paragrafo come nel reale)
            idx = [i for i, (_, ini, _) in enumerate(rr) if not ini]
            parole = [rr[i][2] for i in idx]
            rnd.shuffle(parole)
            nuova = list(rr)
            for i, w in zip(idx, parole):
                nuova[i] = (rr[i][0], False, w)
            cc.extend(coppie(nuova, k, chiave))
        nulli.append(quota_stessa(cc))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(reale)), ('osservata', q), ('attesa', m), ('S', q / m if m else None),
                        ('z', (q - m) / s if s else None)])


def riga(nome, r):
    print('%-44s n %5d | osservata %.3f attesa %.3f | S %.2f (z %.1f)' % (nome, r['n'], r['osservata'], r['attesa'], r['S'], r['z'] or 0), flush=True)


def main():
    ris = OrderedDict()
    prove = OrderedDict()
    prove['ZL, k=1'] = (pagine('ZL'), 1, primo_eva)
    prove['IT, k=1'] = (pagine('IT'), 1, primo_eva)
    prove['GC, k=1 (primo carattere)'] = (pagine('GC'), 1, primo_car)
    prove['ZL lingua A, k=1'] = (pagine('ZL', lingua='A'), 1, primo_eva)
    prove['ZL lingua B, k=1'] = (pagine('ZL', lingua='B'), 1, primo_eva)
    prove['ZL erbario (H), k=1'] = (pagine('ZL', sezioni={'H'}), 1, primo_eva)
    prove['ZL biologia (B), k=1'] = (pagine('ZL', sezioni={'B'}), 1, primo_eva)
    prove['ZL ricette (S), k=1'] = (pagine('ZL', sezioni={'S'}), 1, primo_eva)
    prove['ZL altre sezioni, k=1'] = (pagine('ZL', sezioni={'H', 'B', 'S'}, esclusa=True), 1, primo_eva)
    prove['ZL, k=2'] = (pagine('ZL'), 2, primo_eva)
    prove['ZL, k=3'] = (pagine('ZL'), 3, primo_eva)
    prove['ZL, k=1, senza segno aggiunto'] = (pagine('ZL'), 1, senza_aggiunto)
    prove['ZL, k=1, parola intera'] = (pagine('ZL'), 1, parola)
    for nome, (per, k, chiave) in prove.items():
        r = misura(per, k, chiave, random.Random(SEME))
        ris[nome] = r
        riga(nome, r)
    with open(os.path.join(RISULTATI, 'e83_evitamento_inizi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e83 — L\'evitamento fra inizi di riga: verifiche di robustezza', '',
           'S = quota di coppie di righe (distanza k, stesso paragrafo) con lo stesso primo segno, divisa per l\'attesa '
           '(%d rimescolamenti delle righe nella pagina). Preregistrazione: `preregistrazioni/e83.md`.' % PERMUTAZIONI, '',
           '| prova | coppie | osservata | attesa | S | z |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (nome, r['n'], r['osservata'], r['attesa'], r['S'], r['z'] or 0))
    with open(os.path.join(RISULTATI, 'e83_evitamento_inizi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
