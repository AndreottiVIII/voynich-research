# -*- coding: utf-8 -*-
"""Esperimento 285b: la misura dell'e285 solo sulle coppie di parole vicine che non sono varianti (distanza di modifica
sui segni >= 2), per separare un canale nel finale dalla copia fra vicine.

Preregistrazione: preregistrazioni/e285b.md. Scrive risultati/e285b_finale_non_varianti.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e249_pezzi_simboli as e249
import e251_lessico_sezione as e251
import e285_pezzi_contesto as e285

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, SEMI_GEN, DIST_MIN = 2851, 100, (7, 8, 9), 2
_DIST = {}


def distanza(a, b):
    if (a, b) in _DIST:
        return _DIST[(a, b)]
    x, y = tuple(e237.D(a)), tuple(e237.D(b))
    prec = list(range(len(y) + 1))
    for i in range(1, len(x) + 1):
        cur = [i] + [0] * len(y)
        for j in range(1, len(y) + 1):
            cur[j] = min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (x[i - 1] != y[j - 1]))
        prec = cur
    _DIST[(a, b)] = prec[-1]
    return prec[-1]


def coppie(righe, i, j):
    """righe: liste di (parola, (prefisso, centro, finale)); solo coppie vicine non varianti."""
    return [(a[1][i], b[1][j]) for r in righe for a, b in zip(r, r[1:]) if distanza(a[0], b[0]) >= DIST_MIN]


def eccessi(righe, rnd):
    out = OrderedDict()
    for nome, (i, j) in e285.PEZZI.items():
        vero = e285.mi(coppie(righe, i, j))
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            mes = []
            for r in righe:
                x = list(r)
                rnd.shuffle(x)
                mes.append(x)
            nulli.append(e285.mi(coppie(mes, i, j)))
        out[nome] = OrderedDict([('vero', vero), ('nullo', statistics.mean(nulli)), ('sd', statistics.pstdev(nulli)), ('eccesso', vero - statistics.mean(nulli))])
    return out


def main():
    rnd = random.Random(SEME)
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    taglia = e249.segmentatore([w for r in voy for w in r])
    cache = {}
    tp = lambda w: (w, cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w)))
    testi = OrderedDict([('Voynich', [[tp(w) for w in r] for r in voy])])
    c, c2, freq, _, _, _ = e251.contesto()
    for s in SEMI_GEN:
        rr = e236.dopo(e233.genera(c2, dict(e251.CONF, gamma=0.0), s), freq, 100 + s)
        testi['generatore e241, seme %d' % s] = [[tp(w) for w in ps if trascrizione.pulita(w)] for _, _, ps in rr]
    g7 = testi['generatore e241, seme %d' % SEMI_GEN[0]]
    finali = [f for f, _ in Counter(t[1][2] for r in g7 for t in r if t[1][2]).most_common()]
    lettere = [l for l, _ in Counter(x for _, x in zip(range(200000), e285.latino())).most_common()]
    mappa = {l: finali[i % len(finali)] for i, l in enumerate(lettere)}
    for nome, p in (('controllo positivo (finali = latino, puro)', 1.0), ('controllo positivo (al 50%)', 0.5)):
        it, rr_ = e285.latino(), []
        for r in g7:
            nuova = []
            for w, (a, b, f) in r:
                if f and rnd.random() < p:
                    f2 = mappa[next(it)]
                    nuova.append((w[:len(w) - len(f)] + f2, (a, b, f2)))
                else:
                    nuova.append((w, (a, b, f)))
            rr_.append(nuova)
        testi[nome] = rr_
    ris = OrderedDict()
    for nome, righe in testi.items():
        righe = [r for r in righe if len(r) >= 2]
        tot = sum(len(r) - 1 for r in righe)
        varianti = sum(distanza(a[0], b[0]) < DIST_MIN for r in righe for a, b in zip(r, r[1:]))
        ris[nome] = OrderedDict([('coppie', tot), ('quota_varianti', varianti / tot), ('eccessi', eccessi(righe, rnd))])
        print('%-44s varianti %.3f | ' % (nome, varianti / tot) + ' | '.join('%s %+.4f' % (k, v['eccesso']) for k, v in ris[nome]['eccessi'].items()), flush=True)
    gen = [n for n in testi if n.startswith('generatore')]
    soglia = max(ris[g]['eccessi']['finale']['eccesso'] for g in gen)
    pos = ris['controllo positivo (finali = latino, puro)']['eccessi']['finale']
    valido = pos['eccesso'] > soglia + 3 * pos['sd']
    v = ris['Voynich']['eccessi']['finale']
    regge = v['eccesso'] > soglia + 3 * v['sd']
    esito = 'non valido' if not valido else ('il finale regge come portatore (nessuna lettura)' if regge else 'effetto della copia fra vicine')
    json.dump(OrderedDict([('risultati', ris), ('soglia_generatori_finale', soglia), ('valido', valido), ('esito', esito)]),
              open(os.path.join(RISULTATI, 'e285b_finale_non_varianti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e285b — Il "finale portatore" dell\'e285, sulle sole coppie non varianti', '',
          'Eccesso di informazione mutua fra pezzi omologhi di parole vicine non varianti (distanza di modifica ≥ %d), contro le parole rimescolate '
          'nella riga (%d rimescolamenti). Preregistrazione: `preregistrazioni/e285b.md`.' % (DIST_MIN, RIMESCOLAMENTI), '',
          '| testo | coppie | quota di varianti | ' + ' | '.join(e285.PEZZI) + ' |', '|---|---|---|' + '---|' * len(e285.PEZZI)]
    for n, r in ris.items():
        md.append('| %s | %d | %.3f | %s |' % (n, r['coppie'], r['quota_varianti'], ' | '.join('%+.4f (sd %.4f)' % (x['eccesso'], x['sd']) for x in r['eccessi'].values())))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e285b_finale_non_varianti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
