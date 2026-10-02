# -*- coding: utf-8 -*-
"""Tabella descrittiva dell'ordine ricostruito dei bifogli (stesso procedimento dell'e154b: vocabolario normalizzato,
greedy + 2-opt, dentro i gruppi di stessa mano e lingua con almeno 6 unita'). Nessun test: le verifiche sono
e148, e150, e150b, e154b, e161.

Scrive risultati/ricostruzione_bifogli.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154
import e154b_ordine_normalizzato as e154b

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    U = e150.unita()
    _, imp = e154.caratteristiche(U)
    gruppi = defaultdict(list)
    for n, u in U.items():
        if imp.get(n) is not None:
            gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = OrderedDict((k, v) for k, v in sorted(gruppi.items(), key=lambda kv: -len(kv[1])) if len(v) >= e154.MINIMO)
    ris = OrderedDict()
    out = ['# Ordine ricostruito dei bifogli (descrittivo)', '',
           'Dentro ogni gruppo di stessa mano e lingua, unità (bifogli o fogli singoli con almeno 100 parole) ordinate per somiglianza '
           'di vocabolario normalizzato (procedimento dell\'e154b). Il verso della sequenza non è determinato. Accanto: sezione e posizione '
           'nella rilegatura attuale (rango del primo foglio nel gruppo).', '']
    for (mano, lingua), nomi in gruppi.items():
        vett = {n: Counter(e154b.normalizza(w) for ps in U[n]['righe'] for w in ps) for n in nomi}
        S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
        ric = [nomi[i] for i in e150.ricostruisci(S)]
        ril = sorted(nomi, key=lambda n: U[n]['primo'])
        rango = {n: i + 1 for i, n in enumerate(ril)}
        sim = [S[nomi.index(a)][nomi.index(b)] for a, b in zip(ric, ric[1:])]
        chiave = 'mano %s, lingua %s' % (mano, lingua)
        ris[chiave] = [OrderedDict([('unita', n), ('sezione', U[n]['sezione']), ('rango_rilegatura', rango[n]),
                                    ('somiglianza_con_la_successiva', sim[i] if i < len(sim) else None)]) for i, n in enumerate(ric)]
        out += ['## %s (%d unità)' % (chiave, len(nomi)), '', '| # | unità | sezione | rango nella rilegatura | somiglianza con la successiva |', '|---|---|---|---|---|']
        for i, r in enumerate(ris[chiave]):
            out.append('| %d | %s | %s | %d | %s |' % (i + 1, r['unita'], r['sezione'] or '–', r['rango_rilegatura'],
                                                    '%.3f' % r['somiglianza_con_la_successiva'] if r['somiglianza_con_la_successiva'] is not None else '–'))
        out.append('')
    with open(os.path.join(RISULTATI, 'ricostruzione_bifogli.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    with open(os.path.join(RISULTATI, 'ricostruzione_bifogli.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
