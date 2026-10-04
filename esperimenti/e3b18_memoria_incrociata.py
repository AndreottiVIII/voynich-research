# -*- coding: utf-8 -*-
"""Esperimento e3b18: covarianza dei residui delle scelte di grafia fra parole vicine (d 1-3) e lontane (d 6-10) della
stessa riga, per classi diverse e per la stessa classe.

Preregistrazione: preregistrazioni/e3b18.md. Scrive risultati/e3b18_memoria_incrociata.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')
CLASSI = OrderedDict((k, e3b06.CLASSI[k]) for k in ('qo/o', '-ey/-dy', 'sh/ch', 'ee/e'))
VICINO, LONTANO = (1, 2, 3), tuple(range(6, 11))
ESCLUSA = {'-ey/-dy', 'ee/e'}   # tutte e due sulla fine della parola: legate per costruzione
BOOT = 1000


def prodotti(pagine):
    """[(id riga, tipo 'stessa'|'diverse', gruppo 'vicino'|'lontano', prodotto dei residui)]."""
    out = []
    rid = 0
    for righe in pagine:
        res = [[{} for _ in r] for r in righe]
        for c, f in CLASSI.items():
            val = [[f(w) for w in r] for r in righe]
            tot = [sum(1 for v in vv if v is not None) for vv in val]
            uno = [sum(1 for v in vv if v == 1) for vv in val]
            T, U = sum(tot), sum(uno)
            for i, vv in enumerate(val):
                t, u = T - tot[i], U - uno[i]
                if t < 5:
                    continue
                p = u / t
                for a, v in enumerate(vv):
                    if v is not None:
                        res[i][a][c] = v - p
        for i, rr in enumerate(res):
            for a in range(len(rr)):
                for d in VICINO + LONTANO:
                    b = a + d
                    if b >= len(rr):
                        continue
                    g = 'vicino' if d in VICINO else 'lontano'
                    for ca, xa in rr[a].items():
                        for cb, xb in rr[b].items():
                            if ca != cb and {ca, cb} == ESCLUSA:
                                continue
                            out.append((rid + i, 'stessa' if ca == cb else 'diverse', g, xa * xb))
        rid += len(righe)
    return out


def medie(pp):
    acc = defaultdict(lambda: [0.0, 0])
    for _, t, g, x in pp:
        acc[t, g][0] += x
        acc[t, g][1] += 1
    m = {k: s / n for k, (s, n) in acc.items()}
    return {t: m[t, 'vicino'] - m[t, 'lontano'] for t in ('stessa', 'diverse')}, {k: n for k, (_, n) in acc.items()}


def main():
    rnd = random.Random(3218)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    pp = prodotti(pagine)
    d, n = medie(pp)
    per = defaultdict(list)
    for x in pp:
        per[x[0]].append(x)
    chiavi = list(per)
    bs, bd = [], []
    for _ in range(BOOT):
        db, _ = medie([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
        bs.append(db['stessa'])
        bd.append(db['diverse'])

    def ic(xs):
        xs = sorted(xs)
        return [xs[int(0.025 * BOOT)], xs[int(0.975 * BOOT) - 1]]
    ics, icd = ic(bs), ic(bd)
    if icd[0] <= 0 <= icd[1] and ics[0] > 0:
        esito = 'memoria per classe'
    elif icd[0] > 0:
        esito = 'un modo di scrivere comune'
    else:
        esito = 'incerto'
    out = OrderedDict([('stessa_classe', OrderedDict([('differenza', d['stessa']), ('IC95', ics)])), ('classi_diverse', OrderedDict([('differenza', d['diverse']), ('IC95', icd)])),
                       ('coppie', {'%s %s' % k: v for k, v in n.items()}), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b18_memoria_incrociata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b18 — La memoria è separata per ogni scelta o c\'è un "modo" di scrivere comune?', '', 'Preregistrazione: `preregistrazioni/e3b18.md`. Differenza della covarianza dei residui: vicino (d 1–3) − lontano (d 6–10).', '',
          '| coppie di scelte | differenza vicino − lontano | IC 95% |', '|---|---|---|',
          '| stessa classe | %+.5f | %+.5f – %+.5f |' % (d['stessa'], ics[0], ics[1]),
          '| classi diverse | %+.5f | %+.5f – %+.5f |' % (d['diverse'], icd[0], icd[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b18_memoria_incrociata.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
