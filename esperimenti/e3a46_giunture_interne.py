# -*- coding: utf-8 -*-
"""Esperimento e3a46: dentro le forme nuove (e357), una q interna segue i segni di fine parola V (-y, -o, -d) piu' dei
segni C (-n, -r, -s, -m), come fra parole separate?

Preregistrazione: preregistrazioni/e3a46.md. Scrive risultati/e3a46_giunture_interne.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}


def prova(ev, rnd):
    """ev: [(classe V?, b == q)]."""
    def diff(e):
        a = [q for c, q in e if c]
        b = [q for c, q in e if not c]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else 0.0
    d = diff(ev)
    cl = [c for c, _ in ev]
    qq = [q for _, q in ev]
    nul = []
    for _ in range(10000):
        rnd.shuffle(cl)
        nul.append(diff(list(zip(cl, qq))))
    nq = sum(qq)
    return OrderedDict([('eventi', len(ev)), ('q', nq), ('q_dopo_V', sum(q for c, q in ev if c)), ('q_dopo_C', sum(q for c, q in ev if not c)),
                        ('P_q_V', sum(q for c, q in ev if c) / max(1, sum(1 for c, _ in ev if c))), ('P_q_C', sum(q for c, q in ev if not c) / max(1, sum(1 for c, _ in ev if not c))),
                        ('delta', d), ('p', sum(x >= d for x in nul) / len(nul))])


def interni(parole):
    ev = []
    for w in parole:
        for a, b in zip(w[:-1], w[1:]):
            if a in V or a in C:
                ev.append((a in V, b == 'q'))
    return ev


def main():
    rnd = random.Random(3146)
    tok = []
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        tok += ws
        righe.append([tuple(D(w)) for w in ws])
    freq = Counter(tok)
    sim = e350.simili_globali(set(freq))
    nuove = [tuple(D(w)) for w, n in freq.items() if n == 1 and not any(freq[v] >= 20 for v in sim[w] if v != w)]
    comuni = [tuple(D(w)) for w, n in freq.items() if n >= 5]
    ris = OrderedDict()
    ris['dentro le forme nuove'] = prova(interni(nuove), rnd)
    ris['dentro le parole comuni'] = prova(interni(comuni), rnd)
    fra = []
    for r in righe:
        for a, b in zip(r, r[1:]):
            if a and b and (a[-1] in V or a[-1] in C):
                fra.append((a[-1] in V, b[0] == 'q'))
    ris['fra parole separate (riferimento)'] = prova(fra, rnd)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    N = ris['dentro le forme nuove']
    if N['q_dopo_V'] + N['q_dopo_C'] < 15:
        esito = 'non decidibile (meno di 15 q interne dopo V o C)'
    elif N['delta'] > 0 and N['p'] < 0.01:
        esito = 'dentro le forme nuove la giuntura segue il raccordo'
    elif N['p'] > 0.1:
        esito = 'no'
    else:
        esito = 'incerto'
    esempi = Counter()
    for w in nuove:
        for i in range(len(w) - 1):
            if w[i + 1] == 'q' and (w[i] in V or w[i] in C):
                esempi[''.join(w)] += 1
    out = OrderedDict([('forme_nuove', len(nuove)), ('misure', ris), ('esempi', list(esempi)[:20]), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a46_giunture_interne.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a46 — Le giunture dentro le forme nuove seguono il raccordo?', '', 'Preregistrazione: `preregistrazioni/e3a46.md`. Forme nuove: %d.' % len(nuove), '',
          '| dove | eventi | q dopo V | q dopo C | P(q | V) | P(q | C) | Δ | p |', '|---|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %d | %d | %.3f | %.3f | %+.3f | %.4f |' % (k, x['eventi'], x['q_dopo_V'], x['q_dopo_C'], x['P_q_V'], x['P_q_C'], x['delta'], x['p']) for k, x in ris.items()]
    md += ['', 'Esempi di forme nuove con una q interna dopo un segno di fine parola: %s.' % ', '.join(out['esempi']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a46_giunture_interne.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
