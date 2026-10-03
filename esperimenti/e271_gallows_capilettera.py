# -*- coding: utf-8 -*-
"""Esperimento 271: togliendo il gallows iniziale (p, f; t, k) si ottiene una parola attestata piu' spesso che togliendo il
primo segno di parole che cominciano con un segno non gallows, a parita' di lunghezza del corpo?

Preregistrazione: preregistrazioni/e271.md. Scrive risultati/e271_gallows_capilettera.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'p', 'f', 't', 'k', 'cph', 'cfh', 'cth', 'ckh'}


def main():
    righe = [(bool(r.inizio_par), [w for w in r.parole if trascrizione.pulita(w)]) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))]
    voc = Counter(w for _, ps in righe for w in ps)
    gruppi = defaultdict(list)          # gruppo -> [(lunghezza corpo, attestato)]
    for ini, ps in righe:
        for w in ps:
            u = D(w)
            if len(u) < 3:
                continue
            corpo = ''.join(u[1:])
            x = (len(u) - 1, voc[corpo] > 0)
            g = u[0]
            if g in ('p', 'f'):
                gruppi['a: p/f nelle prime righe' if ini else 'b: p/f nelle altre righe'].append(x)
            elif g in ('t', 'k'):
                gruppi['c: t/k'].append(x)
            elif g not in GALLOWS:
                gruppi['r: riferimento (non gallows)'].append(x)
    rif = defaultdict(lambda: [0, 0])
    for L, a in gruppi['r: riferimento (non gallows)']:
        rif[L][0] += a
        rif[L][1] += 1
    quota = {L: (v[0] / v[1]) for L, v in rif.items() if v[1] >= 20}
    ris = OrderedDict()
    for nome in ('a: p/f nelle prime righe', 'b: p/f nelle altre righe', 'c: t/k'):
        xs = [(L, a) for L, a in gruppi[nome] if L in quota]
        O = sum(a for _, a in xs)
        A = sum(quota[L] for L, _ in xs)
        var = sum(quota[L] * (1 - quota[L]) for L, _ in xs)
        ris[nome] = OrderedDict([('parole', len(xs)), ('osservate', O / len(xs)), ('attese', A / len(xs)), ('O_su_A', O / A if A else None),
                                 ('z', (O - A) / math.sqrt(var) if var else None)])
        print(nome, dict(ris[nome]), flush=True)
    ris['riferimento_parole'] = len(gruppi['r: riferimento (non gallows)'])
    a, c = ris['a: p/f nelle prime righe'], ris['c: t/k']
    esito = ('iniziali decorate' if (a['O_su_A'] or 0) >= 1.5 and (a['z'] or 0) > 3 and a['O_su_A'] > (c['O_su_A'] or 0)
             else 'nessun indizio' if (a['O_su_A'] or 0) <= 1.1 or (a['z'] or 0) <= 2 else 'incerto')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e271_gallows_capilettera.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e271 — I gallows iniziali sono capilettera aggiunti a parole normali?', '',
          'Corpo = parola senza la prima unità; O = quota di corpi attestati; A = attesa dal riferimento (parole che cominciano con un segno non gallows) '
          'a parità di lunghezza del corpo. Preregistrazione: `preregistrazioni/e271.md`.', '', '| gruppo | parole | O | A | O/A | z |', '|---|---|---|---|---|---|']
    for nome in ('a: p/f nelle prime righe', 'b: p/f nelle altre righe', 'c: t/k'):
        r = ris[nome]
        md.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (nome, r['parole'], r['osservate'], r['attese'], r['O_su_A'] or 0, r['z'] or 0))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e271_gallows_capilettera.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
