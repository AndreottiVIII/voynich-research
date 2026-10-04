# -*- coding: utf-8 -*-
"""Esperimento e3b02: e3b01 con il nullo dentro (strato dei 4 segni x pagina) e dentro (strato x mano).

Preregistrazione: preregistrazioni/e3b02.md. Scrive risultati/e3b02_lessicale_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e381_parole_intere as e381
import e3a60_spazi_due_trascrittori as e3a60
import e3a99_spazio_lessicale as e3a99
import e3b01_taratura_lessicale as e3b01

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 100


def taratura(righe, gruppo_di_riga, rnd):
    punti = e3b01.punti_fissi(righe)
    ys = [p[3] for p in punti]
    vero = e3b01.statistica(righe, punti, ys)
    strati = defaultdict(list)
    for j, p in enumerate(punti):
        strati[p[2], gruppo_di_riga[p[0]]].append(j)
    nul = []
    for _ in range(PERM):
        y2 = list(ys)
        for idx in strati.values():
            vv = [ys[j] for j in idx]
            rnd.shuffle(vv)
            for j, v in zip(idx, vv):
                y2[j] = v
        nul.append(e3b01.statistica(righe, punti, y2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('differenza_vera', vero), ('nullo_media', m), ('nullo_sd', sd), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3202)
    lat = e3a99.righe_testo(e381.testi()['Historical - Latin - Literary - NT (Vulgate).txt'])
    r_lat = taratura(lat, [k // 25 for k in range(len(lat))], rnd)
    print('latino', json.dumps(r_lat), flush=True)
    d = e3a60.righe('ZL')
    chiavi = list(d)
    righe = [d[k] for k in chiavi]
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    rP = taratura(righe, [k[0] for k in chiavi], rnd)
    print('Voynich, pagina', json.dumps(rP), flush=True)
    rM = taratura(righe, [mano.get(k[0]) for k in chiavi], rnd)
    print('Voynich, mano', json.dumps(rM), flush=True)
    z = rP['z']
    esito = 'nessuna preferenza lessicale' if abs(z) < 2 else ('preferenza contraria' if z <= -2 else 'preferenza lessicale debole')
    out = OrderedDict([('latino_pagine', r_lat), ('Voynich_nullo_pagina', rP), ('Voynich_nullo_mano', rM), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b02_lessicale_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b02 — La "preferenza contraria" dell\'e3b01 resta con il nullo dentro la pagina?', '', 'Preregistrazione: `preregistrazioni/e3b02.md`. e3b01: Voynich −0,861, nullo senza pagina −0,010 (z −12,8).', '',
          '| testo e nullo | differenza vera | nullo: media (sd) | z |', '|---|---|---|---|']
    for k, x in (('latino, dentro "pagine" di 25 righe', r_lat), ('Voynich, dentro la pagina', rP), ('Voynich, dentro la mano', rM)):
        md.append('| %s | %+.3f | %+.3f (%.3f) | %+.1f |' % (k, x['differenza_vera'], x['nullo_media'], x['nullo_sd'], x['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b02_lessicale_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
