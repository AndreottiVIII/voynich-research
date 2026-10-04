# -*- coding: utf-8 -*-
"""Esperimento e3b59: memoria delle scelte oltre le parole (metodo dell'e3b56) mano per mano, con prova di eterogeneità.

Preregistrazione: preregistrazioni/e3b59.md. Scrive risultati/e3b59_memoria_mani.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np
from scipy.stats import chi2

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3b54_memoria_oltre_parole as e3b54
import e3b56_memoria_oltre_parole_corretta as e3b56

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_COPPIE = 2000


def main():
    rng = np.random.default_rng(3259)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    per = OrderedDict()
    for pg, pars in e341.pagine().items():
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr and mano.get(pg):
            per.setdefault(mano[pg], []).append(rr)
    cv = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])
    ris = OrderedDict()
    for h in sorted(per):
        r = e3b54.prova(OrderedDict((k, e3b56.prepara(per[h], f)) for k, f in cv.items()), rng)
        x = r['insieme']
        x['pagine'] = len(per[h])
        x['dev_nullo'] = abs(x['effetto'] / x['z']) if x['z'] else None
        ris[h] = x
        print('mano', h, json.dumps(x), flush=True)
    valide = [h for h, x in ris.items() if x['coppie_vicine'] >= MIN_COPPIE and x['dev_nullo']]
    if all(ris[h]['p'] < 0.05 for h in valide):
        es1 = 'in tutte le mani'
    elif any(ris[h]['p'] > 0.20 for h in valide):
        es1 = 'solo in alcune mani'
    else:
        es1 = 'incerto'
    w = np.array([1 / ris[h]['dev_nullo'] ** 2 for h in valide])
    e = np.array([ris[h]['effetto'] for h in valide])
    media = float((w * e).sum() / w.sum())
    Q = float((w * (e - media) ** 2).sum())
    pq = float(chi2.sf(Q, len(valide) - 1)) if len(valide) > 1 else None
    es2 = 'le mani differiscono' if pq is not None and pq < 0.01 else 'differenze non dimostrate'
    out = OrderedDict([('mani', ris), ('valide', valide), ('media_pesata', media), ('Q', Q), ('p_eterogeneita', pq), ('esito_1', es1), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b59_memoria_mani.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b59 — La memoria corta delle scelte varia da scriba a scriba?', '', 'Preregistrazione: `preregistrazioni/e3b59.md`. Metodo dell\'e3b56; Voynich intero: +0,054.', '',
          '| mano | pagine | coppie vicine | M osservata | M nullo | effetto | z | p |', '|---|---|---|---|---|---|---|---|']
    for h, x in ris.items():
        md.append('| %s | %d | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (h, x['pagine'], x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['z'], x['p']))
    md += ['', 'Mani valide (almeno %d coppie vicine): %s. Media pesata %+.4f; Q = %.2f, p = %s.' % (MIN_COPPIE, ', '.join(valide), media, Q, '%.4f' % pq if pq is not None else 'n.d.'), '',
           'Esito 1: **%s**. Esito 2: **%s**.' % (es1, es2)]
    open(os.path.join(RISULTATI, 'e3b59_memoria_mani.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
