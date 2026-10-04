# -*- coding: utf-8 -*-
"""Esperimento e3c19: la memoria delle scelte per mano (1, 2, 3) con il nullo solito e con quello che conserva la
posizione nella riga (e3c14). ZL e IT, classi scelte a mano, con i bordi; differenze fra mani con ricampionamenti
indipendenti.

Preregistrazione: preregistrazioni/e3c19.md. Scrive risultati/e3c19_memoria_mani_posizione.json e .md.
"""
import json, os, sys
from collections import OrderedDict
from itertools import combinations

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3c14_nullo_posizione as e3c14

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANI = ('1', '2', '3')
BOOT = 2000


def con_boot(cc, rng):
    """Memoria (e3b62) con l'intervallo per pagine e il campione bootstrap (meno il nullo)."""
    pr = e3b62.prova(cc, rng)['insieme']
    tot = sum(e3b70.per_unita(c) for c in cc.values())
    n_u = tot.shape[0]
    boot = []
    for _ in range(BOOT):
        x = e3b70.emme(tot[rng.integers(0, n_u, n_u)].sum(0))
        boot.append(np.nan if x is None else x - pr['nullo'])
    boot = np.array(boot)
    m = e3b70.emme(tot.sum(0))
    return m - pr['nullo'], boot


def main():
    rng = np.random.default_rng(3319)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris, diff = OrderedDict(), OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        for nullo in ('nullo solito', 'nullo con posizione'):
            boots = {}
            for h in MANI:
                uu, ss = e3b62.voynich(pd, mano, h)
                cc = OrderedDict((k, e3b62.prepara(uu, ss, f)) for k, f in e3b62.CV.items())
                if nullo == 'nullo con posizione':
                    cc = OrderedDict((k, e3c14.con_posizione(c, uu, e3b62.CV[k])) for k, c in cc.items())
                ef, boot = con_boot(cc, rng)
                boots[h] = boot
                b = boot[np.isfinite(boot)]
                ris['%s, %s, mano %s' % (q, nullo, h)] = OrderedDict([('effetto', float(ef)), ('IC95', [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))])])
                print(q, nullo, h, json.dumps(ris['%s, %s, mano %s' % (q, nullo, h)]), flush=True)
            for a, b in combinations(MANI, 2):
                dd = boots[a] - boots[b]
                dd = dd[np.isfinite(dd)]
                diff['%s, %s, mano %s − mano %s' % (q, nullo, a, b)] = OrderedDict([('differenza', ris['%s, %s, mano %s' % (q, nullo, a)]['effetto'] - ris['%s, %s, mano %s' % (q, nullo, b)]['effetto']),
                                                                                  ('IC95', [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))])])
    pos = [k for k in ris if 'posizione' in k]
    tutte = all(ris[k]['IC95'][0] > 0 for k in pos)
    separate = [k for k, v in diff.items() if 'posizione' in k and not v['IC95'][0] <= 0 <= v['IC95'][1]]
    if tutte and not separate:
        esito = 'senza la posizione la memoria c\'è in ogni mano, senza differenze trovate'
    elif separate:
        esito = 'senza la posizione le mani differiscono: ' + '; '.join(separate)
    else:
        esito = 'senza la posizione la memoria non è dimostrata in ogni mano'
    out = OrderedDict([('mani', ris), ('differenze', diff), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c19_memoria_mani_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c19 — La memoria per mano, con il nullo che conserva la posizione', '', 'Preregistrazione: `preregistrazioni/e3c19.md`.', '',
          '| misura | effetto (IC 95%) |', '|---|---|']
    for k, x in ris.items():
        md.append('| %s | %+.4f (%+.4f – %+.4f) |' % (k, x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', '| differenza | valore (IC 95%) |', '|---|---|']
    for k, x in diff.items():
        md.append('| %s | %+.4f (%+.4f – %+.4f) |' % (k, x['differenza'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c19_memoria_mani_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
