# -*- coding: utf-8 -*-
"""Esperimento e3a07: legame a distanza 2 (e3a03) con il nullo dentro (pagina, parola in mezzo).

Preregistrazione: preregistrazioni/e3a07.md. Scrive risultati/e3a07_distanza_due_pagina.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e380_sandhi as e380
import e381_parole_intere as e381
import misure

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)


def terne(pagine):
    """pagine: [(chiave pagina, [righe])] -> [((pagina, w2), ultimo di w1, primo di w3)]."""
    out = []
    for pg, righe in pagine:
        for r in righe:
            for a, b, c in zip(r, r[1:], r[2:]):
                out.append(((pg, b), a[-1], c[0]))
    return out


def main():
    rnd = random.Random(3107)
    voy = []
    for pg, pars in e341.pagine().items():
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        voy.append((pg, rr))
    ris = OrderedDict()
    ris['Voynich'] = e380.prova(terne(voy), rnd, 1000)
    print('Voynich', json.dumps(ris['Voynich'], default=float), flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib += [((nome, i), righe[i:i + 25]) for i in range(0, len(righe), 25)]
    ris['gibberish umano'] = e380.prova(terne(gib), rnd, 100)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = e380.prova(terne([(i, righe[i:i + 25]) for i in range(0, len(righe), 25)]), rnd, 100)
        print(k, sens[k.replace('.txt', '')]['E'], flush=True)
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]['E']))
    prima = json.load(open(os.path.join(RISULTATI, 'e3a03_distanza_due.json'), encoding='utf-8'))['testi_sensati']
    grandi = [k for k, x in prima.items() if x['eventi'] >= 5000 and k in sens]
    m_prima = statistics.median(prima[k]['E'] for k in grandi)
    m_ora = statistics.median(sens[k]['E'] for k in grandi)
    if m_ora >= 0.5 * m_prima and ris['Voynich']['z'] < 2:
        esito = 'il legame delle lingue è grammatica, non argomento'
    elif m_ora < 0.5 * m_prima:
        esito = 'in buona parte argomento'
    else:
        esito = 'il Voynich ora mostra un legame (z ≥ 2): da rileggere'
    ris['mediana_E_grandi'] = OrderedDict([('e3a03', m_prima), ('e3a07', m_ora), ('testi', len(grandi))])
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a07_distanza_due_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a07 — Il legame a distanza 2 delle lingue è grammatica o argomento della pagina?', '', 'Preregistrazione: `preregistrazioni/e3a07.md`. Nullo dentro (pagina, parola in mezzo).', '',
          'Voynich: E %.4f, z %.1f (%d terne). Gibberish umano: E %.4f, z %.1f. Mediana di E dei %d testi sensati con almeno 5.000 terne: %.4f nell\'e3a03, %.4f qui.' % (
              ris['Voynich']['E'], ris['Voynich']['z'], ris['Voynich']['eventi'], ris['gibberish umano']['E'], ris['gibberish umano']['z'], len(grandi), m_prima, m_ora), '',
          '| testo sensato | terne | E | z |', '|---|---|---|---|']
    md += ['| %s | %d | %.4f | %.1f |' % (k, x['eventi'], x['E'], x['z']) for k, x in ris['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a07_distanza_due_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
