# -*- coding: utf-8 -*-
"""Esperimento 156: quanta parte della differenza di vocabolario fra le "lingue" A e B di Currier sparisce unificando le
scelte di grafia decise per riga?

Preregistrazione: preregistrazioni/e156.md. Scrive risultati/e156_lingue_ab.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e135_stato_riga as e135
import e145_abitudini as e145
import e154b_ordine_normalizzato as e154b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, ESTRAZIONI, CAMPIONE = 156, 50, 8000
D = misure.divisore(misure.GLIFI_EVA)


def n2(w):
    u = D(e154b.normalizza(w))
    out = []
    for i, g in enumerate(u):
        if g == 'e' and out and out[-1] == 'e':
            continue
        out.append(g)
    s = ''.join(out)
    return s[:-4] + 'ain' if s.endswith('aiin') else s


LIVELLI = OrderedDict([('N0 grezzo', lambda w: w), ('N1 cinque scelte', e154b.normalizza), ('N2 piu e/ee e ain/aiin', n2)])


def pagine(filtro):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole and filtro(r):
            per.setdefault(r.pagina, []).append([w for w in r.parole if trascrizione.pulita(w)])
    return per


def campione(per, n, rnd):
    chiavi = list(per)
    rnd.shuffle(chiavi)
    out = []
    for k in chiavi:
        out.extend(w for r in per[k] for w in r)
        if len(out) >= n:
            break
    return out[:n]


def due_meta(per, n, rnd):
    chiavi = list(per)
    rnd.shuffle(chiavi)
    a = {k: per[k] for k in chiavi[0::2]}
    b = {k: per[k] for k in chiavi[1::2]}
    return campione(a, n, rnd), campione(b, n, rnd)


def jsd(xs, ys):
    p, q = Counter(xs), Counter(ys)
    n, m = sum(p.values()), sum(q.values())
    out = 0.0
    for w in set(p) | set(q):
        a, b = p[w] / n, q[w] / m
        mm = (a + b) / 2
        if a:
            out += 0.5 * a * math.log2(a / mm)
        if b:
            out += 0.5 * b * math.log2(b / mm)
    return out


def eccesso(P1, P2, f, rnd):
    n = min(CAMPIONE, sum(len(r) for p in P1.values() for r in p) // 2, sum(len(r) for p in P2.values() for r in p) // 2)
    tra, dentro = [], []
    for _ in range(ESTRAZIONI):
        x, y = campione(P1, n, rnd), campione(P2, n, rnd)
        tra.append(jsd([f(w) for w in x], [f(w) for w in y]))
        for P in (P1, P2):
            a, b = due_meta(P, n, rnd)
            dentro.append(jsd([f(w) for w in a], [f(w) for w in b]))
    return statistics.mean(tra) - statistics.mean(dentro), statistics.mean(tra), statistics.mean(dentro), n


def riscritto_con(Pa, Pb):
    """A riscritto con le quote di B, h = 0 (controllo positivo)."""
    righe_b = [('x', r) for p in Pb.values() for r in p if r]
    acc = defaultdict(lambda: [0, 0])
    for f, _, st, v in e135.occorrenze(righe_b):
        if f in e145.SCELTE:
            acc[(f, st[1:])][0] += v
            acc[(f, st[1:])][1] += 1
    q = {k: (a + 0.5) / (n + 1) for k, (a, n) in acc.items()}
    h = {f: 0.0 for f in e145.SCELTE}
    rnd = random.Random(SEME + 1)
    out = OrderedDict()
    for k, p in Pa.items():
        rr = []
        for r in p:
            r = e145.riscrivi(r, h, q, rnd) if r else r
            # e/ee e ain/aiin con le quote di B, a livello di parola
            nuove = []
            for w in r:
                u = D(w)
                s = ''.join(u)
                nuove.append(s)
            rr.append(nuove)
        out[k] = rr
    return out


def main():
    rnd = random.Random(SEME)
    A = pagine(lambda r: r.lingua == 'A')
    B = pagine(lambda r: r.lingua == 'B')
    M2 = pagine(lambda r: r.mano == '2')
    M3 = pagine(lambda r: r.mano == '3')
    Ar = riscritto_con(A, B)
    ris = OrderedDict()
    for nome, (P1, P2) in (('A contro B', (A, B)), ('controllo positivo: A contro A riscritto con le quote di B', (A, Ar)),
                           ('mano 2 contro mano 3 (entrambe B)', (M2, M3))):
        r = OrderedDict()
        for liv, f in LIVELLI.items():
            ex, tra, dentro, n = eccesso(P1, P2, f, rnd)
            r[liv] = OrderedDict([('jsd_tra', tra), ('jsd_dentro', dentro), ('eccesso', ex), ('campione', n)])
        e0 = r['N0 grezzo']['eccesso']
        for liv in ('N1 cinque scelte', 'N2 piu e/ee e ain/aiin'):
            r[liv]['quota_spiegata'] = 1 - r[liv]['eccesso'] / e0 if e0 > 0 else None
        ris[nome] = r
        print('%-58s %s' % (nome, ' | '.join('%s: eccesso %.4f%s' % (liv.split()[0], x['eccesso'], (' (spiegata %.2f)' % x['quota_spiegata']) if x.get('quota_spiegata') is not None else '')
                                            for liv, x in r.items())), flush=True)
    qa = ris['A contro B']['N2 piu e/ee e ain/aiin']['quota_spiegata']
    qc = ris['controllo positivo: A contro A riscritto con le quote di B']['N2 piu e/ee e ain/aiin']['quota_spiegata']
    valido = (qc or 0) >= 0.8
    esito = 'A e B sono abitudini di grafia' if qa >= 0.7 else 'A e B differiscono nel vocabolario' if qa < 0.3 else 'in parte'
    ris['valido'], ris['esito'] = valido, esito
    print('controllo valido %s | quota spiegata A/B %.2f | esito: %s' % (valido, qa, esito))
    with open(os.path.join(RISULTATI, 'e156_lingue_ab.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e156 — Le "lingue" A e B sono solo abitudini di grafia?', '', 'JSD fra distribuzioni dei tipi (campioni per pagine, %d estrazioni); eccesso = fra − dentro. '
           'Preregistrazione: `preregistrazioni/e156.md`.' % ESTRAZIONI, '',
           '| confronto | livello | JSD fra | JSD dentro | eccesso | quota spiegata dalla grafia |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            for liv, x in r.items():
                out.append('| %s | %s | %.4f | %.4f | %.4f | %s |' % (nome, liv, x['jsd_tra'], x['jsd_dentro'], x['eccesso'],
                                                                   '%.2f' % x['quota_spiegata'] if x.get('quota_spiegata') is not None else '–'))
    out += ['', 'Controllo valido: **%s**. Esito: **%s** (quota spiegata a N2: %.2f).' % ('sì' if valido else 'no', esito, qa)]
    with open(os.path.join(RISULTATI, 'e156_lingue_ab.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
