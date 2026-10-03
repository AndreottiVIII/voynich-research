# -*- coding: utf-8 -*-
"""Esperimento 277: dispersione di Juilland (D) delle 100 parole piu' frequenti e delle parole di frequenza 5-20, nel
Voynich (tutto e solo erbario) e in testi veri divisi in unita' di 170 parole.

Preregistrazione: preregistrazioni/e277.md. Scrive risultati/e277_parole_grammaticali.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e99_macer as e99
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
UNITA, PAROLE_MAX = 170, 35000


def juilland(unita, parole):
    n = len(unita)
    tot = [len(u) for u in unita]
    conti = [Counter(u) for u in unita]
    out = {}
    for w in parole:
        f = [c[w] / t for c, t in zip(conti, tot)]
        m = statistics.mean(f)
        out[w] = 1 - (statistics.pstdev(f) / m) / math.sqrt(n - 1) if m else None
    return out


def misura(unita):
    tutte = Counter(w for u in unita for w in u)
    top = [w for w, _ in tutte.most_common(100)]
    medie = [w for w, c in tutte.items() if 5 <= c <= 20]
    d = juilland(unita, top + medie)
    dt = statistics.mean(d[w] for w in top)
    dm = statistics.mean(d[w] for w in medie)
    return OrderedDict([('unita', len(unita)), ('parole', sum(map(len, unita))), ('D_prime_100', dt), ('D_frequenza_5_20', dm), ('rapporto', dt / dm)])


def a_unita(parole):
    parole = parole[:PAROLE_MAX]
    return [parole[i:i + UNITA] for i in range(0, len(parole) - UNITA + 1, UNITA)]


def main():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            per.setdefault(r.pagina, [r.sezione, []])[1].extend(ps)
    testi = OrderedDict([
        ('Voynich, tutte le pagine', [v for _, v in per.values() if len(v) >= 40]),
        ('Voynich, erbario', [v for s, v in per.values() if s == 'H' and len(v) >= 40]),
        ('Bibbia latina', a_unita(lingue.parole('Latin'))),
        ('Bibbia italiana', a_unita(lingue.parole('Italian'))),
        ('Plinio XX–XXVII', a_unita([w for _, ps in plinio() for w in ps])),
        ('Macer floridus, capitoli', [[w for ps in c for w in ps] for c in e99.capitoli()]),
    ])
    ris = OrderedDict((k, misura(v)) for k, v in testi.items())
    for k, r in ris.items():
        print(k, dict(r), flush=True)
    veri = [r['D_prime_100'] for k, r in ris.items() if not k.startswith('Voynich')]
    v = ris['Voynich, erbario']['D_prime_100']
    esito = ('come parole grammaticali' if min(veri) <= v <= max(veri) else 'diverse dalle parole grammaticali' if v < min(veri) - 0.05 else 'al limite')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e277_parole_grammaticali.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e277 — Le parole più frequenti del Voynich si comportano da parole grammaticali?', '',
          'Dispersione di Juilland D (1 = uniforme fra le unità). Testi veri in unità di %d parole. Preregistrazione: `preregistrazioni/e277.md`.' % UNITA, '',
          '| testo | unità | D prime 100 | D frequenza 5–20 | rapporto |', '|---|---|---|---|---|']
    for k, r in list(ris.items())[:len(testi)]:
        md.append('| %s | %d | %.3f | %.3f | %.2f |' % (k, r['unita'], r['D_prime_100'], r['D_frequenza_5_20'], r['rapporto']))
    md += ['', 'Esito (Voynich, erbario, contro l\'intervallo dei testi veri %.3f–%.3f): **%s**.' % (min(veri), max(veri), esito)]
    open(os.path.join(RISULTATI, 'e277_parole_grammaticali.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
