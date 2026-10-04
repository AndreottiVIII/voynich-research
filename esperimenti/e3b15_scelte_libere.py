# -*- coding: utf-8 -*-
"""Esperimento e3b15: incertezza tolta sulle scelte di grafia (qo/o, -ey/-dy, sh/ch) da raccordo, memoria corta (ultima
scelta della stessa classe nelle 3 parole precedenti della riga) e da tutti e due; stima e prova su pagine alterne.

Preregistrazione: preregistrazioni/e3b15.md. Scrive risultati/e3b15_scelte_libere.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')
CLASSI = OrderedDict((k, e3b06.CLASSI[k]) for k in ('qo/o', '-ey/-dy', 'sh/ch'))
MODELLI = ('0', 'R', 'M', 'RM')


def eventi(pagine, f):
    """[(pagina, prec, memoria, y)]."""
    out = []
    for pi, righe in enumerate(pagine):
        for r in righe:
            storia = []
            for a, w in enumerate(r):
                y = f(w)
                if y is not None:
                    prec = r[a - 1][-1] if a > 0 else '^'
                    mem = next((v for b, v in reversed(storia) if a - b <= 3), None)
                    out.append((pi, prec, 'n' if mem is None else str(mem), y))
                    storia.append((a, y))
    return out


def chiave(m, prec, mem):
    return {'0': (), 'R': (prec,), 'M': (mem,), 'RM': (prec, mem)}[m]


def entropia_condizionata(train, test, m):
    c = defaultdict(Counter)
    for _, prec, mem, y in train:
        c[chiave(m, prec, mem)][y] += 1
    h = 0.0
    for _, prec, mem, y in test:
        cc = c[chiave(m, prec, mem)]
        p = (cc[y] + 1) / (sum(cc.values()) + 2)
        h -= math.log2(p)
    return h / len(test)


def main():
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    ris = OrderedDict()
    for nome, f in CLASSI.items():
        ev = eventi(pagine, f)
        pari = [e for e in ev if e[0] % 2 == 0]
        dispari = [e for e in ev if e[0] % 2 == 1]
        H = {m: (entropia_condizionata(pari, dispari, m) + entropia_condizionata(dispari, pari, m)) / 2 for m in MODELLI}
        tolta = OrderedDict((m, 1 - H[m] / H['0']) for m in MODELLI)
        ris[nome] = OrderedDict([('eventi', len(ev)), ('entropia', OrderedDict(H.items())), ('incertezza_tolta', tolta)])
        print(nome, json.dumps(ris[nome]), flush=True)
    q = ris['qo/o']['incertezza_tolta']
    esito = 'la memoria rende le scelte meno libere' if q['RM'] - q['R'] >= 0.03 else 'la memoria aggiunge poco'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b15_scelte_libere.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b15 — Con la memoria corta, quanto restano libere le scelte di grafia?', '', 'Preregistrazione: `preregistrazioni/e3b15.md`. Incertezza tolta = 1 − entropia condizionata / entropia senza contesto (stima e prova su pagine alterne).', '',
          '| classe | eventi | entropia senza contesto (bit) | R (raccordo) | M (memoria) | RM (tutti e due) |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.1f%% | %.1f%% | %.1f%% |' % (k, x['eventi'], x['entropia']['0'], 100 * x['incertezza_tolta']['R'], 100 * x['incertezza_tolta']['M'], 100 * x['incertezza_tolta']['RM']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b15_scelte_libere.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
