# -*- coding: utf-8 -*-
"""Esperimento e3b04: e3b03 (spazio facoltativo, parola intera contro lunghezza) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3b04.md. Scrive risultati/e3b04_lessicale_lunghezza_it.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a60_spazi_due_trascrittori as e3a60
import e3b01_taratura_lessicale as e3b01
import e3b03_lessicale_lunghezza as e3b03

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3204)
    d = e3a60.righe('IT')
    chiavi = list(d)
    righe = [d[k] for k in chiavi]
    punti = e3b01.punti_fissi(righe)
    ys = [p[3] for p in punti]
    lun = e3b03.lunghezze(righe, punti)
    key = [(p[2],) + l for p, l in zip(punti, lun)]
    vero = e3b03.statistica(righe, punti, ys, key)
    m2, s2 = e3b03.nullo(righe, punti, ys, key, [k + (chiavi[p[0]][0],) for k, p in zip(key, punti)], rnd)
    media_st = defaultdict(list)
    for p in punti:
        media_st[p[2]].append(p[3])
    ms = {k: sum(v) / len(v) for k, v in media_st.items()}
    acc = defaultdict(list)
    for p, l in zip(punti, lun):
        acc[l[0]].append(p[3] - ms[p[2]])
    sc = OrderedDict((str(L), sum(acc[L]) / len(acc[L])) for L in sorted(acc))
    ok = abs(vero - m2) <= 0.2 and sc.get('5', 0) > 0 and sc.get('2', 0) < 0
    esito = 'si ritrova' if ok else 'non si ritrova'
    out = OrderedDict([('punti', len(punti)), ('differenza_vera', vero), ('nullo_pagina', OrderedDict([('media', m2), ('sd', s2), ('z', (vero - m2) / s2 if s2 else 0.0)])),
                       ('scarto_per_lunghezza_sinistra', sc), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b04_lessicale_lunghezza_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b04 — Lo spazio dipende dalla lunghezza e non dalla parola anche con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b04.md`. ZL (e3b03): +0,105 contro nullo +0,068 (z +2,0).', '',
          'Punti %d. Differenza vera **%+.3f**; nullo dentro strati × pagina %+.3f (sd %.3f), z %+.1f.' % (len(punti), vero, m2, s2, out['nullo_pagina']['z']), '',
          'Scarto della quota di spazi per lunghezza del pezzo a sinistra: ' + ', '.join('%s: %+.3f' % ('5+' if k == '5' else k, v) for k, v in sc.items()) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b04_lessicale_lunghezza_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
