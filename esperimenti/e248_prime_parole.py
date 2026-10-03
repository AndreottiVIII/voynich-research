# -*- coding: utf-8 -*-
"""Esperimento 248: la prima parola della pagina (P) e' piu' spesso unica e ripresa nella pagina delle prime parole degli
altri paragrafi (Q)? Riferimento: prime parole delle altre righe (L).

Preregistrazione: preregistrazioni/e248.md. Scrive risultati/e248_prime_parole.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

from scipy.stats import fisher_exact

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE, GALLOWS = 248, 200, {'p', 't', 'k', 'f'}
D = e237.D


def pagine():
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            d = out.setdefault(r.pagina, {'sezione': r.sezione, 'righe': []})
            d['righe'].append((bool(r.inizio_par), ps))
    return out


def corpo(u):
    return u[1:] if len(u) > 2 and u[0] in GALLOWS else u


def ripresa(u, dopo_u, inventario):
    """u ripetuta o variata (distanza 1) fra le tuple dopo_u."""
    return u in dopo_u or bool(e237.vicini(u, inventario) & dopo_u)


def main():
    rnd = random.Random(SEME)
    P = pagine()
    freq = Counter(w for d in P.values() for _, ps in d['righe'] for w in ps)
    inventario = sorted({x for w in freq for x in D(w)})
    gruppi = {'P': [], 'Q': [], 'L': []}       # (pagina, indice riga, parola)
    for p, d in P.items():
        primo = True
        for k, (ini, ps) in enumerate(d['righe']):
            g = 'P' if (ini and primo) else ('Q' if ini else 'L')
            if ini:
                primo = False
            gruppi[g].append((p, k, ps[0]))
    dopo = {}
    for p, d in P.items():
        for k in range(len(d['righe'])):
            dopo[(p, k)] = {tuple(D(w)) for _, ps in d['righe'][k + 1:] for w in ps}
    tutta = {p: {tuple(D(w)) for _, ps in d['righe'] for w in ps} for p, d in P.items()}
    per_sez = defaultdict(list)
    for p, d in P.items():
        per_sez[d['sezione']].append(p)
    ris = OrderedDict()
    for nome, f in (('parola intera', lambda u: u), ('corpo senza gallows', corpo)):
        r = OrderedDict()
        hap = {g: [freq[w] == 1 for _, _, w in v] for g, v in gruppi.items()}
        rip = {g: [ripresa(f(tuple(D(w))), {f(x) for x in dopo[(p, k)]}, inventario) for p, k, w in v] for g, v in gruppi.items()}
        r['unicita'] = {g: sum(x) / len(x) for g, x in hap.items()}
        tab = [[sum(hap['P']), len(hap['P']) - sum(hap['P'])], [sum(hap['Q']), len(hap['Q']) - sum(hap['Q'])]]
        r['unicita_P_su_Q'] = r['unicita']['P'] / r['unicita']['Q'] if r['unicita']['Q'] else None
        r['unicita_p_fisher'] = float(fisher_exact(tab, alternative='greater')[1])
        r['ripresa'] = {g: sum(x) / len(x) for g, x in rip.items()}
        nulli = []
        for _ in range(REPLICHE):
            xs = []
            for p, k, w in gruppi['P']:
                altre = [q for q in per_sez[P[p]['sezione']] if q != p]
                if not altre:
                    continue
                q = rnd.choice(altre)
                xs.append(ripresa(f(tuple(D(w))), {f(x) for x in tutta[q]}, inventario))
            nulli.append(sum(xs) / len(xs))
        m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        r['ripresa_P_nullo'] = m
        r['ripresa_P_z'] = (r['ripresa']['P'] - m) / sd if sd else None
        ris[nome] = r
        print(nome, json.dumps(r, default=float), flush=True)
    r = ris['parola intera']
    titoli = (r['unicita_P_su_Q'] or 0) >= 1.3 and r['unicita_p_fisher'] < 0.01 and (r['ripresa_P_z'] or 0) > 3 and r['ripresa']['P'] > r['ripresa']['Q']
    ris['n'] = {g: len(v) for g, v in gruppi.items()}
    ris['esito'] = 'indizio di titoli' if titoli else 'nessun indizio'
    json.dump(ris, open(os.path.join(RISULTATI, 'e248_prime_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e248 — La prima parola della pagina è un "titolo"?', '',
          'P = prima parola della pagina (%d), Q = prime parole degli altri paragrafi (%d), L = prime parole delle altre righe (%d). Ripresa = '
          'ripetizione o variante a distanza 1 più avanti nella pagina; nullo: un\'altra pagina della stessa sezione. Preregistrazione: '
          '`preregistrazioni/e248.md`.' % (len(gruppi['P']), len(gruppi['Q']), len(gruppi['L'])), '',
          '| misura | P | Q | L | P/Q | p (Fisher) | ripresa P nullo | z |', '|---|---|---|---|---|---|---|---|']
    for nome, r in list(ris.items())[:2]:
        md.append('| unicità (%s) | %.3f | %.3f | %.3f | %.2f | %.4f | | |' % (nome, r['unicita']['P'], r['unicita']['Q'], r['unicita']['L'], r['unicita_P_su_Q'] or 0, r['unicita_p_fisher']))
        md.append('| ripresa (%s) | %.3f | %.3f | %.3f | | | %.3f | %.1f |' % (nome, r['ripresa']['P'], r['ripresa']['Q'], r['ripresa']['L'], r['ripresa_P_nullo'], r['ripresa_P_z'] or 0))
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e248_prime_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
