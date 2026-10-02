# -*- coding: utf-8 -*-
"""Esperimento 227d: spezzatura a caso (sigma) piu' distacco dei "prefissi" a -l/-r (parole attestate di al piu' 3 unita'
che finiscono in l o r: ol, or, ar, dar, qol...) con probabilita' pi. Riproducono insieme le cinque misure dell'e227?

Preregistrazione: preregistrazioni/e227d.md. Scrive risultati/e227d_prefissi_staccati.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e227_unioni_e_legame as e227
import e227b_spezzature as e227b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SIGMA, PI = [0.03, 0.06, 0.09], [0.05, 0.10, 0.20, 0.30]
D = e227.D


def trasforma(pagine, freq, sigma, pi, rnd):
    prefissi = {w for w in freq if len(D(w)) <= 3 and D(w)[-1] in ('l', 'r')}
    out = []
    for p in pagine:
        nuova = []
        for r in p:
            nr = []
            for w in r:
                u = D(w)
                if len(u) >= 3:
                    taglio = next((c for c in (2, 3) if c < len(u) and ''.join(u[:c]) in prefissi and freq[''.join(u[c:])]), None)
                    if taglio and rnd.random() < pi:
                        nr += [''.join(u[:taglio]), ''.join(u[taglio:])]
                        continue
                if len(u) >= 4 and rnd.random() < sigma:
                    tagli = [c for c in range(1, len(u)) if freq[''.join(u[:c])] and freq[''.join(u[c:])]]
                    if tagli:
                        c = rnd.choice(tagli)
                        nr += [''.join(u[:c]), ''.join(u[c:])]
                        continue
                nr.append(w)
            nuova.append(nr)
        out.append(nuova)
    return out


def eccesso_per_prima(pagine, rnd, n=10):
    righe = [r for p in pagine for r in p]
    voc = Counter(w for r in righe for w in r)
    cp = [(a, b) for r in righe for a, b in zip(r, r[1:])]
    fine = {a: tuple(D(a)) for a, _ in cp}
    g2 = defaultdict(list)
    for a, _ in cp:
        g2[fine[a][-2:]].append(a)
    oss, att = Counter(), Counter()
    for a, b in cp:
        oss[a] += voc[a + b] > 0
        att[a] += sum(voc[rnd.choice(g2[fine[a][-2:]]) + b] > 0 for _ in range(20)) / 20
    return [(w, round(oss[w] - att[w], 1)) for w in sorted(oss, key=lambda w: -(oss[w] - att[w]))[:n]]


def main():
    e227.ESTRAZIONI = 50
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    freq = Counter(trascrizione.parole(corrente))
    base = e227.generatore_pagine(1)
    n_base = sum(len(r) for p in base for r in p)
    ris, ordine, i = OrderedDict(), [], 0
    for s in SIGMA:
        for pi in PI:
            testo = trasforma(base, freq, s, pi, random.Random(2272 + i))
            i += 1
            m = e227b.misura(testo, random.Random(227))
            m['quota_spezzate'] = (m['parole'] - n_base) / n_base
            m['fuori'] = e227b.fuori(m)
            nome = 'sigma %.2f, pi %.2f' % (s, pi)
            ris[nome] = m
            ordine.append((s, pi, nome))
            print('%s: %s fuori %s' % (nome, ' '.join('%s %.3f' % (k, m[k]) for k in list(e227b.BERSAGLI) + ['lunghezza_media', 'quota_spezzate']), m['fuori']), flush=True)
    candidati = [x for x in ordine if not ris[x[2]]['fuori']]
    verifica = None
    if candidati:
        s, pi, n = candidati[0]
        base2 = e227.generatore_pagine(2)
        m2 = e227b.misura(trasforma(base2, freq, s, pi, random.Random(2299)), random.Random(227))
        m2['fuori'] = e227b.fuori(m2)
        verifica = OrderedDict([('sigma', s), ('pi', pi), ('misure', m2)])
        print('verifica seme 2, %s: fuori %s' % (n, m2['fuori']), flush=True)
    basta = bool(verifica) and not verifica['misure']['fuori']
    vs, vp, vicino = min(ordine, key=lambda x: (len(ris[x[2]]['fuori']), e227b.scarto(ris[x[2]])))
    migliore = (verifica['sigma'], verifica['pi']) if verifica else (vs, vp)
    idx = [k for k, (s, p, _) in enumerate(ordine) if (s, p) == migliore][0]
    ris['eccesso_per_prima_parola'] = eccesso_per_prima(trasforma(base, freq, migliore[0], migliore[1], random.Random(2272 + idx)), random.Random(5))
    esito = ('prefissi staccati bastano (sigma %.2f, pi %.2f)' % migliore if basta
             else "non bastano (piu' vicino %s, fuori: %s)" % (vicino, ', '.join(ris[vicino]['fuori']) or 'nessuna sul seme 1'))
    ris['verifica'] = verifica
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e227d_prefissi_staccati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e227d — Prefissi a -l/-r staccati più spezzatura a caso', '',
          'Generatore e192 (seme 1); distacco di un prefisso attestato (≤ 3 unità, finale l o r) con probabilità π, poi spezzatura a caso '
          'con probabilità σ. Preregistrazione: `preregistrazioni/e227d.md`.', '',
          '| σ | π | parole in più | U/N0 | U/N1 | U/N2 | legame | Q | lunghezza media | fuori tolleranza |', '|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich (bersaglio)** | | | 1,92 ± 0,15 | 1,29 ± 0,07 | 1,16 ± 0,05 | 0,188 ± 0,02 | 0,67 ± 0,08 | 4,46 | |']
    for s, pi, n in ordine:
        m = ris[n]
        md.append('| %.2f | %.2f | %.1f%% | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (s, pi, 100 * m['quota_spezzate'], m['U/N0'], m['U/N1'], m['U/N2'],
                                                                                        m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    if verifica:
        m = verifica['misure']
        md.append('| verifica seme 2 | %.2f / %.2f | | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (verifica['sigma'], verifica['pi'], m['U/N0'], m['U/N1'],
                                                                                                   m['U/N2'], m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    md += ['', 'Prime parole con l\'eccesso maggiore nel testo generato (σ %.2f, π %.2f): %s. Nel Voynich: ol +195, or +116, ar +68, chol +42, '
           'al +42, dar +42, qol +41, dal +31.' % (migliore[0], migliore[1], ', '.join('%s %+.0f' % x for x in ris['eccesso_per_prima_parola'])),
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e227d_prefissi_staccati.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
