# -*- coding: utf-8 -*-
"""Esperimento e3a52: e3a49 (PMI dentro le parole contro PMI fra parole) nei generatori pubblicati.

Preregistrazione: preregistrazioni/e3a52.md. Scrive risultati/e3a52_dentro_fra_generatori.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3a49_dentro_fra as e3a49

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rnd = random.Random(3152)
    e134.controlla()
    corpi = OrderedDict()
    for k, v in e134.testi().items():
        if k == 'Voynich':
            continue
        rr = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
        rr = [r for r in rr if r]
        corpi[k] = [rr[i:i + 29] for i in range(0, len(rr), 29)]
    for s in (1, 19):
        corpi['Timm e Schinner, seme %d' % s] = [[[tuple(D(w)) for w in r] for r in p] for p in e337.pagine_ts(s)]
    ris = OrderedDict()
    for nome, pp in corpi.items():
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
            v = e3a49.rho(prese)[0]
            if v is not None:
                sub.append(v)
        m = statistics.median(sub) if sub else None
        es = 'n.d.' if m is None else ('lo riproduce' if m >= 0.4 else ('no' if m < 0.3 else 'in parte'))
        ris[nome] = OrderedDict([('rho', r_all), ('celle', n_all), ('rho_10000', sub), ('mediana_10000', m), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a52_dentro_fra_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a52 — I generatori pubblicati hanno la giuntura che ricalca le sequenze interne?', '', 'Preregistrazione: `preregistrazioni/e3a52.md`. Voynich: 0,44–0,50 a 10.000 parole (e3a49, e3a50).', '',
          '| generatore | ρ (tutto) | celle | mediana a 10.000 parole | esito |', '|---|---|---|---|---|']
    md += ['| %s | %s | %d | %s | %s |' % (k, '%.3f' % x['rho'] if x['rho'] is not None else 'n.d.', x['celle'], '%.3f' % x['mediana_10000'] if x['mediana_10000'] is not None else 'n.d.', x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a52_dentro_fra_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
