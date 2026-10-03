# -*- coding: utf-8 -*-
"""Esperimento e3a54: e3a49 (PMI dentro le parole contro PMI fra parole) per lingua A, lingua B e mani di Davis 1, 2, 3.

Preregistrazione: preregistrazioni/e3a54.md. Scrive risultati/e3a54_catena_parti.json e .md.
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


def main():
    rnd = random.Random(3154)
    righe = list(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    parti = OrderedDict([('lingua A', lambda r: r.lingua == 'A'), ('lingua B', lambda r: r.lingua == 'B'),
                         ('mano 1', lambda r: r.mano == '1'), ('mano 2', lambda r: r.mano == '2'), ('mano 3', lambda r: r.mano == '3')])
    ris = OrderedDict()
    for nome, f in parti.items():
        per = OrderedDict()
        for r in righe:
            if not f(r):
                continue
            ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            ws = [w for w in ws if w]
            if ws:
                per.setdefault(r.pagina, []).append(ws)
        pp = list(per.values())
        r_all, n_all = e3a49.rho([x for p in pp for x in p])
        sub = []
        for _ in range(5):
            ordine = rnd.sample(pp, len(pp))
            prese, n = [], 0
            for p in ordine:
                if n >= 5000:
                    break
                prese += p
                n += sum(len(x) for x in p)
            v = e3a49.rho(prese)[0]
            if v is not None:
                sub.append(v)
        m = statistics.median(sub) if sub else None
        es = 'n.d.' if m is None else ('regge' if m > 0.3 else ('non regge' if m < 0.2 else 'incerto'))
        ris[nome] = OrderedDict([('parole', sum(len(x) for p in pp for x in p)), ('rho', r_all), ('celle', n_all), ('rho_5000', sub), ('mediana_5000', m), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a54_catena_parti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a54 — La catena con spazi deboli vale in lingua A, in lingua B e per ogni scriba?', '', 'Preregistrazione: `preregistrazioni/e3a54.md`.', '',
          '| parte | parole | ρ (tutto) | celle | mediana a 5.000 parole | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %s | %d | %s | %s |' % (k, x['parole'], '%.3f' % x['rho'] if x['rho'] is not None else 'n.d.', x['celle'], '%.3f' % x['mediana_5000'] if x['mediana_5000'] is not None else 'n.d.', x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a54_catena_parti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
