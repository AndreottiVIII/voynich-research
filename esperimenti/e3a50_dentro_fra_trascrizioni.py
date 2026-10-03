# -*- coding: utf-8 -*-
"""Esperimento e3a50: e3a49 (PMI dentro le parole contro PMI fra parole) con le trascrizioni IT e GC.

Preregistrazione: preregistrazioni/e3a50.md. Scrive risultati/e3a50_dentro_fra_trascrizioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e3a49_dentro_fra as e3a49

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MAX_LINGUE = 0.392


def pagine(quale, segni):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi(quale)):
        ws = [segni(w) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per.setdefault(r.pagina, []).append(ws)
    return list(per.values())


def main():
    rnd = random.Random(3150)
    ris = OrderedDict()
    for nome, quale, segni in (('IT (Takahashi)', 'IT', lambda w: tuple(D(w))), ('GC (Glen Claston, v101)', 'GC', lambda w: tuple(w))):
        pp = pagine(quale, segni)
        r_all, n_all = e3a49.rho([r for p in pp for r in p])
        sub = []
        for _ in range(5):
            ordine = rnd.sample(pp, len(pp))
            prese, n = [], 0
            for p in ordine:
                if n >= 10000:
                    break
                prese += p
                n += sum(len(r) for r in p)
            sub.append(e3a49.rho(prese)[0])
        m = statistics.median(sub)
        es = 'regge' if m > MAX_LINGUE else ('come le lingue più alte' if m >= 0.2 else 'non regge')
        ris[nome] = OrderedDict([('rho', r_all), ('celle', n_all), ('rho_10000', sub), ('mediana_10000', m), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a50_dentro_fra_trascrizioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a50 — La giuntura ricalca le sequenze interne anche con Takahashi e Glen Claston?', '', 'Preregistrazione: `preregistrazioni/e3a50.md`. Massimo dei testi sensati nell\'e3a49: 0,392.', '',
          '| trascrizione | ρ (tutto) | celle | ρ a 10.000 parole | mediana | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %.3f | %d | %s | %.3f | %s |' % (k, x['rho'], x['celle'], ', '.join('%.3f' % v for v in x['rho_10000']), x['mediana_10000'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a50_dentro_fra_trascrizioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
