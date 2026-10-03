# -*- coding: utf-8 -*-
"""Esperimento 278: le prime due parole dei paragrafi si ripetono come coppia fra paragrafi della stessa sezione piu' delle
prime due parole delle altre righe? Esatte (M1) e con varianti a distanza 1 (M2).

Preregistrazione: preregistrazioni/e278.md. Scrive risultati/e278_formule_apertura.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

from scipy.stats import fisher_exact

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e237.D


def main():
    aperture, altre = defaultdict(list), defaultdict(list)       # sezione -> [(id, (u1, u2))]
    k = 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if len(ps) < 2:
            continue
        coppia = (tuple(D(ps[0])), tuple(D(ps[1])))
        (aperture if r.inizio_par else altre)[r.sezione].append((k, coppia))
        k += 1
    tutte = {u for g in (aperture, altre) for v in g.values() for _, c in v for u in c}
    inventario = sorted({x for u in tutte for x in u})
    vic = {}

    def V(u):
        if u not in vic:
            vic[u] = e237.vicini(u, inventario) | {u}
        return vic[u]

    def quote(gruppo):
        esatte = varianti = n = 0
        for s, v in gruppo.items():
            conta = Counter(c for _, c in v)
            primo = defaultdict(set)
            for _, (a, b) in v:
                primo[a].add(b)
            for _, (a, b) in v:
                n += 1
                esatte += conta[(a, b)] >= 2
                trovata = conta[(a, b)] >= 2
                if not trovata:
                    va, vb = V(a), V(b)
                    trovata = any(x in va and (y in vb) for (x, y), c in conta.items() if (x, y) != (a, b))
                varianti += trovata
        return esatte, varianti, n

    ea, va, na = quote(aperture)
    er, vr, nr = quote(altre)
    ris = OrderedDict()
    for nome, (x1, x2) in (('M1 esatte', (ea, er)), ('M2 con varianti', (va, vr))):
        qa, qr = x1 / na, x2 / nr
        p = float(fisher_exact([[x1, na - x1], [x2, nr - x2]], alternative='greater')[1])
        ris[nome] = OrderedDict([('aperture', qa), ('riferimento', qr), ('rapporto', qa / qr if qr else None), ('p', p)])
        print(nome, dict(ris[nome]), flush=True)
    tipiche = OrderedDict()
    for s, v in aperture.items():
        conta = Counter(c for _, c in v)
        tipiche[s] = [('%s %s' % (''.join(a), ''.join(b)), n) for (a, b), n in conta.most_common(10) if n >= 2]
    ris['coppie_d_apertura_ripetute'] = tipiche
    ris['n'] = {'aperture': na, 'riferimento': nr}
    m1, m2 = ris['M1 esatte'], ris['M2 con varianti']
    forte = any((r['rapporto'] or 0) >= 2 and r['p'] < 0.01 for r in (m1, m2))
    nulla = all((r['rapporto'] or 0) <= 1.2 or r['p'] > 0.05 for r in (m1, m2))
    ris['esito'] = 'formule d\'apertura' if forte else ('nessuna formula' if nulla else 'incerto')
    json.dump(ris, open(os.path.join(RISULTATI, 'e278_formule_apertura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e278 — I paragrafi si aprono con formule fisse?', '',
          'Coppie (prima, seconda parola) delle prime righe di paragrafo (%d) contro le stesse posizioni nelle altre righe (%d). Preregistrazione: '
          '`preregistrazioni/e278.md`.' % (na, nr), '', '| misura | aperture | riferimento | rapporto | p |', '|---|---|---|---|---|']
    for nome in ('M1 esatte', 'M2 con varianti'):
        r = ris[nome]
        md.append('| %s | %.3f | %.3f | %.2f | %.2g |' % (nome, r['aperture'], r['riferimento'], r['rapporto'] or 0, r['p']))
    md += ['', 'Coppie d\'apertura ripetute (almeno 2 volte), per sezione:', '']
    md += ['- %s: %s' % (s, ', '.join('%s (%d)' % x for x in v) or '—') for s, v in tipiche.items()]
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e278_formule_apertura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
