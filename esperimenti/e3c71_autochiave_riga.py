# -*- coding: utf-8 -*-
"""Esperimento e3c71: un'autochiave che riparte a ogni riga riproduce i tratti di riga del Voynich? Simulazione su due
testi in chiaro (Plinio in latino, Della Pittura di Alberti in italiano) in righe finte con le lunghezze del Voynich:
(a) sostituzione semplice; (b) autochiave per riga (ogni lettera cifrata = lettera + lettera in chiaro precedente nella
riga, la prima con un avvio casuale nuovo a ogni riga; gli spazi restano); (c) autochiave continua (l'avvio solo
all'inizio del testo). Misure del Voynich: giuntura nella riga e a capo (e384, Q), inizi di riga speciali (e389),
margine sinistro (e3a33), ripetizioni di parole vicine (e3b25), tipi di parola ogni 10.000.

Preregistrazione: preregistrazioni/e3c71.md. Scrive risultati/e3c71_autochiave_riga.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e384_giuntura_a_capo as e384
import e389_varianti_bordo as e389
import e399_giuntura_generatori as e399
import e3a27_margine_robustezza as e3a27
import e3a33_margine_corretto as e3a33
import e3b25_ripetizioni_grezze as e3b25
import e3c28_forma_alla_pari as e3c28
import e3c63_margine_scribi as e3c63
import e3c64_bordi_scribi as e3c64

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTI = OrderedDict([('latino (Plinio)', "Historical - Latin - Technical - Pliny's Natural History.txt"),
                     ('italiano (Alberti, Della Pittura)', 'Historical - Italian - Technical - Della Pittura.txt')])
PAROLE = 30000


def cifra(righe, modo, rnd):
    alfa = sorted({c for r in righe for w in r for c in w})
    idx = {c: i for i, c in enumerate(alfa)}
    N = len(alfa)
    out = []
    k = rnd.randrange(N)
    for r in righe:
        if modo == 'autochiave per riga':
            k = rnd.randrange(N)
        nr = []
        for w in r:
            nw = []
            for c in w:
                p = idx[c]
                if modo == 'sostituzione':
                    nw.append(alfa[p])
                else:
                    nw.append(alfa[(p + k) % N])
                    k = p
            nr.append(tuple(nw))
        out.append(nr)
    return out


def tratti(righe, rnd, rng):
    blocchi = [[righe[i:i + 29]] for i in range(0, len(righe), 29)]
    g, _ = e384.misura(blocchi, rnd)
    fine, inizio = [], []
    for r in righe:
        n = len(r)
        for j, w in enumerate(r):
            if len(w) < 2:
                continue
            if 0 < j < n - 1 or j == 0:
                inizio.append(((0, w[1:]), j == 0, w[0]))
    ini = e389.analizza(inizio, np.random.RandomState(rng.integers(1 << 30)))
    m = e3c64.massimo(ini)
    pars = [[(r[0][0], None) for r in righe[i:i + 29] if r and r[0]] for i in range(0, len(righe), 29)]
    marg = e3c63.misura([p for p in pars if len(p) >= 2], rnd)
    rip = e3b25.quote(righe)
    tok = [w for r in righe for w in r][:10000]
    return OrderedDict([('E_riga', g['riga']['E']), ('E_capo', g['capo']['E']), ('Q', g['Q']),
                        ('inizio_max', OrderedDict([('segno', ''.join(m[1]) if m else None), ('delta', m[0] if m else 0.0), ('z', m[2] if m else 0.0)])),
                        ('inizi_evitati', [s for s, x in marg.items() if x['esito'] == 'evitato']),
                        ('ripetizione', rip['ripetizione']), ('quasi', rip['quasi']), ('tipi_su_10000', len(set(tok)))])


def main():
    rnd = random.Random(3371)
    rng = np.random.default_rng(3371)
    e384.PERM = 100
    e3c63.e3a33.PERM = 1000
    e389.PERM = 300
    ris = OrderedDict()
    voy = [r for b in e399.blocchi_voynich() for par in b for r in par if r]
    ris['Voynich ZL'] = tratti(voy, rnd, rng)
    print('Voynich', json.dumps(ris['Voynich ZL'], ensure_ascii=False, default=float), flush=True)
    lung = e3c28.lunghezze_voynich()
    tt = e381.testi()
    for nome, chiave in TESTI.items():
        parole = [tuple(w) for r in tt[chiave] if r for w in r][:PAROLE]
        righe = e3c28.righe_finte(parole, lung)
        for modo in ('sostituzione', 'autochiave per riga', 'autochiave continua'):
            x = tratti(cifra(righe, modo, rnd), rnd, rng)
            ris['%s, %s' % (nome, modo)] = x
            print(nome, modo, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    v = ris['Voynich ZL']
    chiude = all(ris['%s, autochiave per riga' % n]['E_riga'] >= 0.5 * v['E_riga'] and (ris['%s, autochiave per riga' % n]['Q'] or 0) < 0.3
                 and (ris['%s, autochiave continua' % n]['Q'] or 0) >= 0.5 for n in TESTI)
    altri = OrderedDict()
    for n in TESTI:
        x = ris['%s, autochiave per riga' % n]
        altri[n] = OrderedDict([('inizi speciali', x['inizio_max']['delta'] >= v['inizio_max']['delta'] / 2 and x['inizio_max']['z'] > 3),
                                ('margine sinistro', len(x['inizi_evitati']) >= 3),
                                ('ripetizioni', x['ripetizione'] >= v['ripetizione'] / 2 and x['quasi'] >= v['quasi'] / 2),
                                ('vocabolario', abs(x['tipi_su_10000'] - v['tipi_su_10000']) <= 0.3 * v['tipi_su_10000'])])
    esito = ('l\'autochiave per riga chiude la riga come il Voynich' if chiude else 'l\'autochiave per riga non chiude la riga come il Voynich')
    out = OrderedDict([('misure', ris), ('chiude_la_riga', chiude), ('altri_tratti_autochiave_per_riga', altri), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c71_autochiave_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c71 — Un\'autochiave che riparte a ogni riga riproduce i tratti di riga del Voynich?', '', 'Preregistrazione: `preregistrazioni/e3c71.md`.', '',
          '| testo | E nella riga | E a capo | Q | inizio di riga: segno che cresce di più (Δ, z) | inizi evitati sul margine | identiche / a una modifica | tipi su 10.000 |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %.4f | %.4f | %s | %s %+.3f (%.1f) | %s | %.4f / %.4f | %d |' % (k, x['E_riga'], x['E_capo'], '%.2f' % x['Q'] if x['Q'] is not None else '—', x['inizio_max']['segno'],
                                                                                       x['inizio_max']['delta'], x['inizio_max']['z'], ', '.join(x['inizi_evitati']) or 'nessuno', x['ripetizione'], x['quasi'], x['tipi_su_10000']))
    md += ['', 'Esito: **%s**.' % esito, ''] + ['- %s, autochiave per riga: %s' % (n, '; '.join('%s %s' % (t, 'sì' if b else 'no') for t, b in a.items())) for n, a in altri.items()]
    open(os.path.join(RISULTATI, 'e3c71_autochiave_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
