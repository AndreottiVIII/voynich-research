# -*- coding: utf-8 -*-
"""Esperimento e3a19: eccesso di ripresa dalla riga subito sopra per terzo del paragrafo (inizio, mezzo, fine), con
l'atteso esatto sulle altre righe del paragrafo; bootstrap sui paragrafi.

Preregistrazione: preregistrazioni/e3a19.md. Scrive risultati/e3a19_copia_paragrafo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def paragrafo(righe):
    """[(terzo, osservati, attesi, bersagli)] per le righe i >= 1."""
    n = len(righe)
    sim = e385.simili_unita(righe)
    insiemi = [set(r) for r in righe]
    bers = [[w for w in r if len(w) >= 3] for r in righe]
    colpi = [[sum(1 for w in bers[i] if sim[w] & insiemi[j]) if i != j else 0 for j in range(n)] for i in range(n)]
    out = []
    for i in range(1, n):
        if not bers[i]:
            continue
        t = min(2, int(3 * i / (n - 1))) if n > 1 else 0
        if i == n - 1:
            t = 2
        out.append((t, colpi[i][i - 1], sum(colpi[i][j] for j in range(n) if j != i) / (n - 1), len(bers[i])))
    return out


def eccessi(pars):
    s = [[0.0, 0.0, 0.0] for _ in range(3)]
    for p in pars:
        for t, o, a, b in p:
            s[t][0] += o
            s[t][1] += a
            s[t][2] += b
    return [(x[0] - x[1]) / x[2] if x[2] else 0.0 for x in s]


def main():
    rnd = random.Random(3119)
    pars = []
    for pars_p in e341.pagine().values():
        for par in pars_p:
            if len(par) >= 4:
                rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
                pars.append(paragrafo(rr))
    e = eccessi(pars)
    boot = sorted((lambda x: x[2] - x[0])(eccessi([pars[rnd.randrange(len(pars))] for _ in pars])) for _ in range(2000))
    ic = [boot[50], boot[1949]]
    d = e[2] - e[0]
    esito = 'la copia cresce lungo il paragrafo' if ic[0] > 0 else ('cala' if ic[1] < 0 else 'costante')
    out = OrderedDict([('paragrafi', len(pars)), ('eccesso_inizio_mezzo_fine', e), ('differenza_fine_inizio', d), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a19_copia_paragrafo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a19 — La copia dalla riga sopra cambia lungo il paragrafo?', '', 'Preregistrazione: `preregistrazioni/e3a19.md`.', '',
          '%d paragrafi con almeno 4 righe. Eccesso di ripresa dalla riga sopra: inizio %+.4f, mezzo %+.4f, fine %+.4f. Fine − inizio %+.4f (IC 95%% %+.4f – %+.4f).' % (len(pars), e[0], e[1], e[2], d, ic[0], ic[1]), '',
          'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a19_copia_paragrafo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
