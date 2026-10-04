# -*- coding: utf-8 -*-
"""Esperimento e3b77: metodo finale della memoria (e3b62 + e3b70) su due classi che non dovrebbero averla: numero di i
(ain/aiin) e finale -l/-r.

Preregistrazione: preregistrazioni/e3b77.md. Scrive risultati/e3b77_classi_controllo.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70

RISULTATI = os.path.join(QUI, '..', 'risultati')
VOYNICH = 0.086


def numero_i(w):
    run = [k for k, s in enumerate(w) if s == 'i']
    if not run:
        return None
    a, b = run[0], run[-1]
    if b - a + 1 != len(run) or b + 1 >= len(w) or w[b + 1] not in ('n', 'r', 'l'):
        return None
    return (1 if len(run) >= 2 else 0, w[:a] + ('*',) + w[b + 1:])


def lr(w):
    if len(w) >= 2 and w[-1] in ('l', 'r'):
        return (1 if w[-1] == 'l' else 0, w[:-1] + ('*',))
    return None


def main():
    rng = np.random.default_rng(3277)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, ss = e3b62.voynich(e341.pagine(), mano)
    ris = OrderedDict()
    for nome, f in (('numero di i', numero_i), ('-l/-r', lr)):
        c = e3b62.prepara(uu, ss, f)
        pr = e3b62.prova(OrderedDict([(nome, c)]), rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
        ris[nome] = OrderedDict([('occorrenze', int(len(c['val']))), ('quota_1', float(c['val'].mean())), ('coppie_vicine', pr['coppie_vicine']),
                                 ('quota_rimescolabile', pr['quota_rimescolabile']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    vv = list(ris.values())
    if all(x['IC95'][0] <= 0 <= x['IC95'][1] or x['effetto'] < VOYNICH / 3 for x in vv):
        esito = 'il metodo è specifico'
    elif any(x['IC95'][0] > 0 and x['effetto'] >= VOYNICH / 2 for x in vv):
        esito = 'anche le classi di controllo hanno memoria'
    else:
        esito = 'in parte'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b77_classi_controllo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b77 — Il metodo finale è specifico? Classi che non dovrebbero avere memoria', '', 'Preregistrazione: `preregistrazioni/e3b77.md`. Le quattro scelte (e3b70): +0,086 (IC +0,060 – +0,113).', '',
          '| classe | occorrenze | quota del valore 1 | coppie vicine | quota rimescolabile | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.3f | %d | %.2f | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (k, x['occorrenze'], x['quota_1'], x['coppie_vicine'], x['quota_rimescolabile'] or 0, x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b77_classi_controllo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
