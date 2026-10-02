# -*- coding: utf-8 -*-
"""Esperimento 227c: come l'e227b, ma il punto di taglio si sceglie con peso (f(a) f(b))^beta, f = frequenza della parte
nel Voynich. Le parole si spezzano dove le meta' sono frequenti?

Preregistrazione: preregistrazioni/e227c.md. Scrive risultati/e227c_tagli_preferenziali.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e227_unioni_e_legame as e227
import e227b_spezzature as e227b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SIGMA, BETA = [0.06, 0.09, 0.12], [0.0, 0.5, 1.0, 2.0]
RIF_E227B = {'U/N0': 1.868, 'legame': 0.189}       # e227b, sigma 0,09


def spezza(pagine, freq, sigma, beta, rnd):
    out = []
    for p in pagine:
        nuova = []
        for r in p:
            nr = []
            for w in r:
                u = e227.D(w)
                if len(u) >= 4 and rnd.random() < sigma:
                    tagli = [c for c in range(1, len(u)) if freq[''.join(u[:c])] and freq[''.join(u[c:])]]
                    if tagli:
                        pesi = [(freq[''.join(u[:c])] * freq[''.join(u[c:])]) ** beta for c in tagli]
                        c = rnd.choices(tagli, pesi)[0]
                        nr += [''.join(u[:c]), ''.join(u[c:])]
                        continue
                nr.append(w)
            nuova.append(nr)
        out.append(nuova)
    return out


def main():
    e227.ESTRAZIONI = 50
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    freq = Counter(trascrizione.parole(corrente))
    base = e227.generatore_pagine(1)
    n_base = sum(len(r) for p in base for r in p)
    ris, ordine, i = OrderedDict(), [], 0
    for s in SIGMA:
        for b in BETA:
            testo = spezza(base, freq, s, b, random.Random(2270 + i))
            i += 1
            m = e227b.misura(testo, random.Random(227))
            m['quota_spezzate'] = (m['parole'] - n_base) / n_base
            m['fuori'] = e227b.fuori(m)
            nome = 'sigma %.2f, beta %.1f' % (s, b)
            ris[nome] = m
            ordine.append((s, b, nome))
            print('%s: %s fuori %s' % (nome, ' '.join('%s %.3f' % (k, m[k]) for k in list(e227b.BERSAGLI) + ['lunghezza_media']), m['fuori']), flush=True)
    rif = ris['sigma 0.09, beta 0.0']
    valido = abs(rif['U/N0'] - RIF_E227B['U/N0']) <= 0.03 and abs(rif['legame'] - RIF_E227B['legame']) <= 0.01
    candidati = [(s, b, n) for s, b, n in ordine if b > 0 and not ris[n]['fuori']]
    verifica = None
    if candidati:
        s, b, n = candidati[0]
        base2 = e227.generatore_pagine(2)
        m2 = e227b.misura(spezza(base2, freq, s, b, random.Random(2271)), random.Random(227))
        m2['fuori'] = e227b.fuori(m2)
        verifica = OrderedDict([('sigma', s), ('beta', b), ('misure', m2)])
        print('verifica seme 2, %s: fuori %s' % (n, m2['fuori']), flush=True)
    basta = bool(verifica) and not verifica['misure']['fuori']
    vicino = min(ordine, key=lambda x: (len(ris[x[2]]['fuori']), e227b.scarto(ris[x[2]])))[2]
    esito = 'non valido' if not valido else ('tagli preferenziali bastano (sigma %.2f, beta %.1f)' % (verifica['sigma'], verifica['beta']) if basta
                                             else 'non bastano (piu\' vicino %s, fuori: %s)' % (vicino, ', '.join(ris[vicino]['fuori']) or 'nessuna sul seme 1'))
    ris['verifica'] = verifica
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e227c_tagli_preferenziali.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e227c — Tagli preferenziali: le parole si spezzano dove le metà sono frequenti?', '',
          'Generatore e192 (seme 1); taglio con peso (f(a)·f(b))^β fra quelli con le due parti attestate. Preregistrazione: '
          '`preregistrazioni/e227c.md`.', '',
          '| σ | β | parole spezzate | U/N0 | U/N1 | U/N2 | legame | Q | lunghezza media | fuori tolleranza |', '|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich (bersaglio)** | | | 1,92 ± 0,15 | 1,29 ± 0,07 | 1,16 ± 0,05 | 0,188 ± 0,02 | 0,67 ± 0,08 | 4,46 | |']
    for s, b, n in ordine:
        m = ris[n]
        md.append('| %.2f | %.1f | %.1f%% | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (s, b, 100 * m['quota_spezzate'], m['U/N0'], m['U/N1'], m['U/N2'],
                                                                                       m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    if verifica:
        m = verifica['misure']
        md.append('| verifica seme 2 | %.2f / %.1f | | %.2f | %.2f | %.2f | %.3f | %.2f | %.2f | %s |' % (verifica['sigma'], verifica['beta'], m['U/N0'], m['U/N1'],
                                                                                                  m['U/N2'], m['legame'], m['Q'], m['lunghezza_media'], ', '.join(m['fuori']) or '—'))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e227c_tagli_preferenziali.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
