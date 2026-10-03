# -*- coding: utf-8 -*-
"""Esperimento e3a68: e3a58 (F1 degli spazi), e3a61 (riempimento) ed e3a67 (tagli sbagliati) con le trascrizioni IT e GC.

Preregistrazione: preregistrazioni/e3a68.md. Scrive risultati/e3a68_spazi_forme_trascrizioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e3a50_dentro_fra_trascrizioni as e3a50
import e3a58_spazi_prevedibili as e3a58
import e3a61_forme_riempite as e3a61
import e3a67_spazi_rifatti as e3a67

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SOGLIE = OrderedDict([('F1 degli spazi (e3a58)', 0.718), ('riempimento (e3a61)', 0.086), ('tagli sbagliati che sono parole (e3a67)', 0.119)])
ORIGINALE = {'F1 degli spazi (e3a58)': 0.862, 'riempimento (e3a61)': 0.434, 'tagli sbagliati che sono parole (e3a67)': 0.499}


def main():
    rnd = random.Random(3168)
    ris = OrderedDict()
    for nome, quale, segni in (('IT (Takahashi)', 'IT', lambda w: tuple(D(w))), ('GC (Glen Claston, v101)', 'GC', lambda w: tuple(w))):
        pp = e3a50.pagine(quale, segni)
        vals = OrderedDict((k, []) for k in SOGLIE)
        for _ in range(5):
            ordine = rnd.sample(pp, len(pp))
            prese, n = [], 0
            for p in ordine:
                if n >= 10000:
                    break
                prese += p
                n += sum(len(r) for r in p)
            vals['F1 degli spazi (e3a58)'].append(e3a58.f1(prese))
            vals['riempimento (e3a61)'].append(e3a61.riempimento([w for r in prese for w in r])[0])
            vals['tagli sbagliati che sono parole (e3a67)'].append(e3a67.attestazione(prese, rnd)[0])
        ris[nome] = OrderedDict()
        for k, v in vals.items():
            m = statistics.median(v)
            ris[nome][k] = OrderedDict([('sottoinsiemi', v), ('mediana', m), ('soglia', SOGLIE[k]), ('esito', 'regge' if m > SOGLIE[k] else 'non regge')])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a68_spazi_forme_trascrizioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a68 — Spazi prevedibili, forme riempite e tagli sbagliati reggono con Takahashi e Glen Claston?', '', 'Preregistrazione: `preregistrazioni/e3a68.md`. Soglia = 90° percentile dei testi sensati nell\'esperimento originale.', '',
          '| trascrizione | misura | ZL (originale) | sottoinsiemi | mediana | soglia | esito |', '|---|---|---|---|---|---|---|']
    for nome, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s | %.3f | %s | %.3f | %.3f | %s |' % (nome, k, ORIGINALE[k], ', '.join('%.3f' % v for v in y['sottoinsiemi']), y['mediana'], y['soglia'], y['esito']))
    open(os.path.join(RISULTATI, 'e3a68_spazi_forme_trascrizioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
