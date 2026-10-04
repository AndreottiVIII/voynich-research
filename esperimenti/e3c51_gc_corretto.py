# -*- coding: utf-8 -*-
"""Esperimento e3c51: la trascrizione di Glen Claston (v101) con la misura corretta dell'e3c48. Domanda principale: le scelte
di sola forma che GC distingue e EVA no (due forme di d: 7/8; due forme di e: c/C) hanno la finestra? Riferimento: h/k,
a/o, 2/1 (sh/ch), -c9/-89 (-ey/-dy), 4o/o (qo/o).

Preregistrazione: preregistrazioni/e3c51.md. Scrive risultati/e3c51_gc_corretto.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3c01_alternanze_interne as e3c01
import e3c05_terza_trascrizione as e3c05
import e3c44_finestra_gc_classi as e3c44
import e3c48_finestra_corretta as e3c48
import e3c50_scribi_menota as e3c50

RISULTATI = os.path.join(QUI, '..', 'risultati')
MINIMO = 300
CLASSI = OrderedDict([
    ('7/8 (due forme di d)', ('forma', e3c01.classe('7', '8'))),
    ('c/C (due forme di e)', ('forma', e3c01.classe('c', 'C'))),
    ('h/k (gallows)', ('riferimento', e3c01.classe('h', 'k'))),
    ('2/1 (sh/ch)', ('riferimento', e3c44.v_shch)),
    ('-c9/-89 (-ey/-dy)', ('riferimento', e3c44.v_eydy)),
    ('a/o', ('altro', e3c01.classe('a', 'o'))),
    ('4o/o (qo/o)', ('altro', e3c44.v_qo)),
])


def minoritarie(pagine, f):
    xs = [f(w) for _, rr in pagine for r in rr if len(r) >= 6 for w in r[1:-1]]
    xs = [x for x in xs if x]
    per = defaultdict(set)
    for v, t in xs:
        per[t].add(v)
    mi = [v for v, t in xs if len(per[t]) == 2]
    return len(xs), min(sum(mi), len(mi) - sum(mi))


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3351)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, ss = e3c05.unita_gc(mano)
    pagine = list(zip(ss, uu))
    ris = OrderedDict()
    for k, (tipo, f) in CLASSI.items():
        n, mino = minoritarie(pagine, f)
        if mino < MINIMO:
            ris[k] = OrderedDict([('tipo', tipo), ('eleggibili', n), ('minoritarie_nei_misti', mino), ('misurabile', False)])
            print(k, 'non misurabile', n, mino, flush=True)
            continue
        x = e3c48.misura(pagine, OrderedDict([(k, f)]), rng)
        x['vicine'], x['finestra'] = e3c50.giudizio(x)
        x['tipo'], x['eleggibili'], x['minoritarie_nei_misti'], x['misurabile'] = tipo, n, mino, True
        ris[k] = x
        print(k, json.dumps(x, ensure_ascii=False), flush=True)

    def esito(x):
        if not x['misurabile']:
            return 'non misurabile'
        return 'ha la finestra' if x['finestra'] else ('accordo fra vicine senza finestra' if x['vicine'] else 'nessun accordo chiaro')
    esiti = OrderedDict((k, esito(x)) for k, x in ris.items())
    rif = [k for k, x in ris.items() if x['tipo'] == 'riferimento' and x['misurabile'] and x['finestra']]
    out = OrderedDict([('classi', ris), ('esiti', esiti), ('riferimento_con_finestra', rif),
                       ('esito_riferimento', '%d su 3 (h/k, 2/1, -c9/-89) con la finestra' % len(rif))])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c51_gc_corretto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c51 — Glen Claston con la misura corretta: le scelte di sola forma', '',
          'Preregistrazione: `preregistrazioni/e3c51.md`. EVA (e3c48, ZL): k/t + sh/ch + -ey/-dy insieme, K corretto +0,131 / +0,093 / +0,086, r 0,68.', '',
          '| classe (GC) | tipo | parole | minoritarie nei tipi misti | K osservato 1/2/3 | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) | esito |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if not x['misurabile']:
            md.append('| %s | %s | %d | %d | | | | | | non misurabile |' % (k, x['tipo'], x['eleggibili'], x['minoritarie_nei_misti']))
            continue
        md.append('| %s | %s | %d | %d | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s |' % (
            k, x['tipo'], x['parole'], x['minoritarie_nei_misti'], ' '.join('%+.3f' % z for z in x['K_osservato']), ' '.join('%+.3f' % z for z in x['K_nullo']),
            x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1],
            x['r'], x['r_IC95'][0], x['r_IC95'][1], esiti[k]))
    md += ['', 'Esito sola forma: 7/8 **%s**; c/C **%s**.' % (esiti['7/8 (due forme di d)'], esiti['c/C (due forme di e)']),
           'Esito riferimento: **%s**.' % out['esito_riferimento']]
    open(os.path.join(RISULTATI, 'e3c51_gc_corretto.json'.replace('.json', '.md')), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
