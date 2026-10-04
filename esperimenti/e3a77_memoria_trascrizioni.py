# -*- coding: utf-8 -*-
"""Esperimento e3a77: profilo di memoria dell'e3a76 con IT (EVA fuso), GC (v101) e ZL in EVA semplice.

Preregistrazione: preregistrazioni/e3a77.md. Scrive risultati/e3a77_memoria_trascrizioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e3a50_dentro_fra_trascrizioni as e3a50
import e3a76_memoria_forma as e3a76

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SOGLIA = 0.369 / 2


def main():
    rnd = random.Random(3177)
    ris = OrderedDict()
    for nome, quale, segni, decide in (('IT (Takahashi), EVA fuso', 'IT', lambda w: tuple(D(w)), True),
                                       ('GC (Glen Claston, v101)', 'GC', lambda w: tuple(w), True),
                                       ('ZL, EVA semplice (descrittivo)', 'ZL', lambda w: tuple(w), False)):
        pp = e3a50.pagine(quale, segni)
        sub = []
        for _ in range(5):
            ordine = rnd.sample(pp, len(pp))
            prese = []
            for p in ordine:
                if len(prese) >= 10000:
                    break
                prese += [w for r in p for w in r]
            sub.append(e3a76.profilo(prese))
        prof = OrderedDict((m, statistics.median(s[m] for s in sub)) for m in e3a76.MODELLI)
        best = e3a76.migliore(prof)
        gain = prof['M2'] - prof['M1']
        es = ('regge' if best in ('M1', 'M2') and gain < SOGLIA else 'non regge') if decide else 'descrittivo'
        ris[nome] = OrderedDict([('profilo', prof), ('migliore', best), ('guadagno_M2_M1', gain), ('sottoinsiemi', sub), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a77_memoria_trascrizioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a77 — "Quasi ordine 1" regge con altri alfabeti di trascrizione?', '', 'Preregistrazione: `preregistrazioni/e3a77.md`. Riferimento e3a76 (ZL, EVA fuso): M1 0,581, M2 0,686, guadagno +0,105; soglia del guadagno %.3f.' % SOGLIA, '',
          '| trascrizione | M0 | MP | M1 | M2 | migliore | guadagno M2 − M1 | esito |', '|---|---|---|---|---|---|---|---|']
    md += ['| %s | %s | %s | %+.3f | %s |' % (k, ' | '.join('%.3f' % x['profilo'][m] for m in e3a76.MODELLI), x['migliore'], x['guadagno_M2_M1'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a77_memoria_trascrizioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
