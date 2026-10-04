# -*- coding: utf-8 -*-
"""Esperimento e3c81: lo stato breve delle scelte è uguale in tutte le mani del Voynich (regola del sistema) o cambia da
mano a mano (abitudine di chi scrive)? Misura corretta dell'e3c48 (k/t, sh/ch, -ey/-dy insieme) per ogni mano di Davis
(variabile $H della trascrizione ZL), ZL e IT. Rifà con la correzione l'e3b59 (misura vecchia: "la mano 1 non la ha",
con un dubbio dichiarato subito dopo sul nullo).

Preregistrazione: preregistrazioni/e3c81.md. Scrive risultati/e3c81_stato_per_mano.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48
import e3c52_eva_per_scelta as e3c52

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
MINIMO = 1500


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3381)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        tutte = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        for h in sorted({h for h, _ in tutte}):
            pagine = [(hh, rr) for hh, rr in tutte if hh == h]
            e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
            n = len(e3c33.raccogli(pagine, cl))
            k = '%s, mano %s' % (q, h)
            if n < MINIMO:
                ris[k] = OrderedDict([('pagine', len(pagine)), ('parole', n), ('misurabile', False)])
                continue
            x = e3c48.misura(pagine, cl, rng)
            x['pagine'], x['misurabile'], x['voce'] = len(pagine), True, e3c52.voce(x)
            ris[k] = x
            print(k, json.dumps(x, ensure_ascii=False), flush=True)
    esiti = OrderedDict()
    for q in ('ZL', 'IT'):
        mis = OrderedDict((k, x) for k, x in ris.items() if k.startswith(q) and x['misurabile'])
        k_tutte = json.load(open(os.path.join(RISULTATI, 'e3c48_finestra_corretta.json'), encoding='utf-8'))['varianti']['Voynich %s, pagine intere' % q]['K_corretto'][0]
        manca = [k for k, x in mis.items() if x['K1_IC95'][1] < k_tutte / 2]
        presenti = [k for k, x in mis.items() if x['K1_IC95'][0] > 0.02]
        if manca:
            esiti[q] = 'manca in qualche mano: ' + ', '.join(manca)
        elif len(presenti) == len(mis):
            esiti[q] = 'presente in tutte le mani misurabili'
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('mani', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c81_stato_per_mano.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c81 — Lo stato breve è uguale in tutte le mani?', '', 'Preregistrazione: `preregistrazioni/e3c81.md`.', '',
          '| trascrizione, mano | pagine | parole | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r | voce |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if not x['misurabile']:
            md.append('| %s | %d | %d | | | | non misurabile |' % (k, x['pagine'], x['parole']))
            continue
        md.append('| %s | %d | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f | %s |' % (k, x['pagine'], x['parole'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1],
                                                                                                    x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['voce']))
    md += [''] + ['Esito %s: **%s**.' % kv for kv in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c81_stato_per_mano.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
