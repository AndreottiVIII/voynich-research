# -*- coding: utf-8 -*-
"""Esperimento e3b67: la memoria delle scelte passa il salto del disegno? Primo tratto con il secondo tratto della stessa
riga contro quelli delle righe con salto precedente e seguente; distanza 2-4; ZL e IT.

Preregistrazione: preregistrazioni/e3b67.md. Scrive risultati/e3b67_salto_potenza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e395_takahashi as e395
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b66_a_capo_potenza as e3b66

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def casi(righe):
    per = defaultdict(list)
    for pg, npar, ws, seps in righe:
        tt = e3b64.tratti(ws, seps)
        if len(tt) >= 2:
            per[pg].append((tt[0], tt[1]))
    out = defaultdict(list)
    for pg, vv in per.items():
        for k, (a, b) in enumerate(vv):
            altri = OrderedDict([('sotto', b), ('precedente', vv[k - 1][1] if k > 0 else None), ('seguente', vv[k + 1][1] if k + 1 < len(vv) else None)])
            out[pg].append((a, altri))
    return out


def analisi(quale, rnd):
    righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(quale)]
    quote = e3b64.quote_pagine(righe, e3b62.CV)
    cc = casi(righe)
    sm = {k: e3b66.somme(cc, quote, k) for k in ('sotto', 'precedente', 'seguente', 'dentro')}
    pagine = [pg for pg in cc if len(cc[pg]) >= 2]

    def dd(pp):
        ks = {k: e3b64.kappa([sm[k][pg] for pg in pp])[0] for k in ('sotto', 'precedente', 'seguente')}
        if None in ks.values():
            return None
        return ks['sotto'] - (ks['precedente'] + ks['seguente']) / 2
    d = dd(pagine)
    boot = sorted(x for x in (dd([rnd.choice(pagine) for _ in pagine]) for _ in range(BOOT)) if x is not None)
    ks = OrderedDict((k, OrderedDict([('K', e3b64.kappa([sm[k][pg] for pg in pagine])[0]), ('coppie', int(sum(sm[k][pg][2] for pg in pagine)))])) for k in sm)
    return OrderedDict([('pagine', len(pagine)), ('K', ks), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])


def main():
    rnd = random.Random(3267)
    ris = OrderedDict((q, analisi(q, rnd)) for q in ('ZL', 'IT'))
    for q, x in ris.items():
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    z, it = ris['ZL'], ris['IT']
    dentro = z['K']['dentro']['K']
    if z['IC95'][0] > 0 and it['D'] > 0:
        esito = 'la memoria passa il salto (almeno in parte)'
    elif z['IC95'][0] <= 0 <= z['IC95'][1] and z['IC95'][1] < dentro / 3:
        esito = 'il salto azzera la memoria'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b67_salto_potenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b67 — La memoria delle scelte passa il salto di un disegno?', '', 'Preregistrazione: `preregistrazioni/e3b67.md`. Coppie a distanza 2–4; D = K(stessa riga) − media di K(riga con salto precedente) e K(seguente).', '',
          '| trascrizione | pagine | K dentro i tratti (coppie) | K stessa riga (coppie) | K precedente (coppie) | K seguente (coppie) | D (IC 95%) |', '|---|---|---|---|---|---|---|']
    for q, x in ris.items():
        k = x['K']
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) |' % (q, x['pagine'], k['dentro']['K'], k['dentro']['coppie'], k['sotto']['K'], k['sotto']['coppie'],
                                                                                              k['precedente']['K'], k['precedente']['coppie'], k['seguente']['K'], k['seguente']['coppie'], x['D'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b67_salto_potenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
