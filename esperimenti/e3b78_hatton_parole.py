# -*- coding: utf-8 -*-
"""Esperimento e3b78: memoria di þ/ð a inizio parola nei Hatton Gospels, separando le 10 parole più frequenti (per lo
più grammaticali) dalle altre; metodo finale (e3b62 + e3b70).

Preregistrazione: preregistrazioni/e3b78.md. Scrive risultati/e3b78_hatton_parole.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70

RISULTATI = os.path.join(QUI, '..', 'risultati')
CHIAVE = 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels.txt'


def main():
    rng = np.random.default_rng(3278)
    righe = [r for r in e381.testi()[CHIAVE] if r]
    c = Counter(x[1] for r in righe for w in r for x in [e3b54.v_th_ini(w)] if x)
    prime = {m for m, _ in c.most_common(10)}
    uu = [[b] for b in e3b51.blocchi(righe)]
    gruppi = OrderedDict([('10 parole più frequenti', lambda w: (lambda x: x if x and x[1] in prime else None)(e3b54.v_th_ini(w))),
                          ('altre parole', lambda w: (lambda x: x if x and x[1] not in prime else None)(e3b54.v_th_ini(w)))])
    ris = OrderedDict()
    for nome, f in gruppi.items():
        cc = e3b62.prepara(uu, ['Hatton'] * len(uu), f)
        pr = e3b62.prova(OrderedDict([('x', cc)]), rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(cc)], pr['nullo'], rng)
        ris[nome] = OrderedDict([('occorrenze', int(len(cc['val']))), ('quota_þ', float(cc['val'].mean())), ('coppie_vicine', pr['coppie_vicine']),
                                 ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    a, b = ris['10 parole più frequenti'], ris['altre parole']
    if b['IC95'][0] > 0:
        esito = 'memoria anche nelle parole non grammaticali'
    elif b['IC95'][0] <= 0 <= b['IC95'][1] and a['IC95'][0] > 0:
        esito = 'la stima viene dalle parole grammaticali'
    else:
        esito = 'non dimostrata'
    out = OrderedDict([('parole_frequenti', sorted(''.join(m) for m in prime)), ('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b78_hatton_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b78 — La memoria di þ/ð nello scriba anglosassone viene dalle parole grammaticali?', '', 'Preregistrazione: `preregistrazioni/e3b78.md`. Tutte insieme (e3b70): +0,102 (IC −0,003 – +0,206).', '',
          '| gruppo | occorrenze | quota þ | coppie vicine | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.3f | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (k, x['occorrenze'], x['quota_þ'], x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b78_hatton_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
