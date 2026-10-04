# -*- coding: utf-8 -*-
"""Esperimento e3c69: un ritmo fisso nella riga, come nelle liste di parole a turno dell'"Ave Maria" di Tritemio (ogni
lettera del chiaro diventa una parola presa dalla lista successiva, in ciclo di P liste). Se è così, due parole a
distanza P si somigliano più di quelle a distanza P − 1 e P + 1 ("pettine"). Somiglianza fra parole interne della stessa
riga a distanza 1 – 8: stessa parola, stesso primo segno, stesso ultimo segno, stessa lunghezza. Per P = 2 … 6:
D_P = S(P) − (S(P − 1) + S(P + 1)) / 2, con intervalli ricampionando le pagine. Controlli: un testo finto a liste con
P = 3 (deve dare il pettine) e uno a lista unica (non deve).

Preregistrazione: preregistrazioni/e3c69.md. Scrive risultati/e3c69_ritmo_fisso.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
LMAX = 8
PP = (2, 3, 4, 5, 6)
TRATTI = OrderedDict([('stessa parola', lambda a, b: a == b), ('stesso primo segno', lambda a, b: a[0] == b[0]),
                      ('stesso ultimo segno', lambda a, b: a[-1] == b[-1]), ('stessa lunghezza', lambda a, b: len(a) == len(b))])
BOOT = 2000
Z = 3.5


def somme(pagine):
    """(pagine, LMAX, tratti, 2): coppie simili e coppie totali a ogni distanza, parole interne."""
    out = np.zeros((len(pagine), LMAX, len(TRATTI), 2))
    for p, rr in enumerate(pagine):
        for r in rr:
            w = [x for x in r[1:-1] if x]
            for i in range(len(w)):
                for L in range(1, LMAX + 1):
                    if i + L >= len(w):
                        break
                    for t, f in enumerate(TRATTI.values()):
                        out[p, L - 1, t, 0] += f(w[i], w[i + L])
                        out[p, L - 1, t, 1] += 1
    return out


def pettine(s):
    S = s[..., 0] / s[..., 1]
    return np.stack([S[..., P - 1, :] - (S[..., P - 2, :] + S[..., P, :]) / 2 for P in PP], axis=-2)


def misura(pagine, rng):
    st = somme(pagine)
    d = pettine(st.sum(0))
    boot = np.array([pettine(st[rng.integers(0, len(pagine), len(pagine))].sum(0)) for _ in range(BOOT)])
    sd = boot.std(0)
    z = d / np.where(sd > 0, sd, np.nan)
    S = st.sum(0)[..., 0] / st.sum(0)[..., 1]
    ris = OrderedDict([('profilo', OrderedDict((t, [float(x) for x in S[:, j]]) for j, t in enumerate(TRATTI)))])
    ris['pettine'] = OrderedDict(('P=%d, %s' % (P, t), OrderedDict([('D', float(d[i, j])), ('z', float(z[i, j]))])) for i, P in enumerate(PP) for j, t in enumerate(TRATTI))
    ris['picchi'] = [k for k, x in ris['pettine'].items() if x['z'] > Z]
    return ris


def finto(rng, P, pagine=200, righe=20, liste=200):
    LET = list('abcdefghiklmnopqrstuvy')
    voc = [[tuple(LET[i] for i in rng.integers(0, len(LET), rng.integers(3, 8))) for _ in range(liste)] for _ in range(P)]
    pesi = 1 / np.arange(1, liste + 1)
    pesi /= pesi.sum()
    out, n = [], 0
    for _ in range(pagine):
        rr = []
        for _ in range(righe):
            r = []
            for _ in range(rng.integers(7, 12)):
                r.append(voc[n % P][rng.choice(liste, p=pesi)])
                n += 1
            rr.append(r)
        out.append(rr)
    return out


def main():
    rng = np.random.default_rng(3369)
    ris = OrderedDict()
    ris['controllo: liste a turno, P = 3'] = misura(finto(rng, 3), rng)
    ris['controllo: lista unica'] = misura(finto(rng, 1), rng)
    for q, pd in (('Voynich ZL', e341.pagine()), ('Voynich IT', e3b45.pagine_it())):
        pagine = [[[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par] for pars in pd.values()]
        ris[q] = misura([p for p in pagine if p], rng)
    for k, x in ris.items():
        print(k, x['picchi'], flush=True)
    ok = 'P=3, stessa parola' in ris['controllo: liste a turno, P = 3']['picchi'] and not ris['controllo: lista unica']['picchi']
    comuni = sorted(set(ris['Voynich ZL']['picchi']) & set(ris['Voynich IT']['picchi']))
    if not ok:
        esito = 'prova non valida (i controlli non si comportano come previsto)'
    elif comuni:
        esito = 'ritmo fisso trovato: ' + ', '.join(comuni)
    else:
        esito = 'nessun ritmo fisso nella riga'
    out = OrderedDict([('misure', ris), ('controlli_ok', ok), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c69_ritmo_fisso.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c69 — Un ritmo fisso nella riga (liste a turno alla Tritemio)?', '', 'Preregistrazione: `preregistrazioni/e3c69.md`. D_P = S(P) − media di S(P−1) e S(P+1); z da ricampionamento delle pagine; picco se z > %.1f.' % Z, '']
    for k, x in ris.items():
        md += ['## %s' % k, '', '| tratto | somiglianza a distanza 1 … 8 |', '|---|---|']
        for t, v in x['profilo'].items():
            md.append('| %s | %s |' % (t, ' '.join('%.4f' % z for z in v)))
        md += ['', '| P | ' + ' | '.join(TRATTI) + ' |', '|---|' + '---|' * len(TRATTI)]
        for P in PP:
            md.append('| %d | %s |' % (P, ' | '.join('%+.4f (z %.1f)' % (x['pettine']['P=%d, %s' % (P, t)]['D'], x['pettine']['P=%d, %s' % (P, t)]['z']) for t in TRATTI)))
        md += ['', 'Picchi: %s.' % (', '.join(x['picchi']) or 'nessuno'), '']
    md += ['Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c69_ritmo_fisso.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
