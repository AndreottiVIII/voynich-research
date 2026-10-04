# -*- coding: utf-8 -*-
"""Esperimento e3c11: il consumo con le lettere (pendenza per lettera a parità di parole e classe, e3c10) è uguale nelle
mani 1, 2 e 3? ZL e IT, classi scelte a mano, con i bordi della riga (più coppie), nullo largo, intervalli per pagine;
differenze fra mani con ricampionamenti indipendenti (le mani hanno pagine diverse).

Preregistrazione: preregistrazioni/e3c11.md. Scrive risultati/e3c11_consumo_per_mano.json e .md.
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
import e3c09_regressione_lettere_parole as e3c09
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 500
BOOT = 2000
MANI = ('1', '2', '3')


def pendenza_lettere(uu, ss, rng):
    """Pendenza per lettera dentro gli strati (classe, d): effetto, intervallo e campione bootstrap (già meno il nullo)."""
    cc = OrderedDict((k, e3c09.prepara(uu, ss, f)) for k, f in e3b62.CV.items())
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
    n_u = len(uu)
    un = np.concatenate([c['uni'][c['I']] for c in cc.values()])
    cl = np.concatenate([np.full(len(c['I']), n) for n, c in enumerate(cc.values())])
    d = np.concatenate([c['d'] for c in cc.values()])
    x = np.concatenate([c['L'] for c in cc.values()])
    _, strato = np.unique(cl * 1000 + d.astype(int), return_inverse=True)
    n_s = int(strato.max()) + 1
    y = np.concatenate([e3c09.eccesso(c, c['val']) for c in cc.values()])
    mu = float(np.mean([e3c10.pendenza(e3c10.statistiche(strato, x, np.concatenate([e3c09.eccesso(c, e3b54.rimescola(c, rng)) for c in cc.values()]),
                                                          un, n_u, n_s).sum(0)) for _ in range(PERM)]))
    st = e3c10.statistiche(strato, x, y, un, n_u, n_s)
    oss = float(e3c10.pendenza(st.sum(0)))
    boot = np.array([e3c10.pendenza(st[rng.integers(0, n_u, n_u)].sum(0)) - mu for _ in range(BOOT)])
    return oss - mu, boot, int(len(y))


def main():
    rng = np.random.default_rng(3311)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris, diff = OrderedDict(), OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        boots = {}
        for h in MANI:
            uu, ss = e3b62.voynich(pd, mano, h)
            ef, boot, n = pendenza_lettere(uu, ss, rng)
            boots[h] = boot
            ris['%s, mano %s' % (q, h)] = OrderedDict([('pagine', len(uu)), ('coppie', n), ('effetto', ef),
                                                       ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])])
            print(q, h, json.dumps(ris['%s, mano %s' % (q, h)]), flush=True)
        for a, b in combinations(MANI, 2):
            dd = boots[a] - boots[b]
            diff['%s, mano %s − mano %s' % (q, a, b)] = OrderedDict([('differenza', ris['%s, mano %s' % (q, a)]['effetto'] - ris['%s, mano %s' % (q, b)]['effetto']),
                                                                    ('IC95', [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))])])
    def separate(q):
        return [k for k, v in diff.items() if k.startswith(q) and not v['IC95'][0] <= 0 <= v['IC95'][1]]
    s_zl, s_it = separate('ZL'), separate('IT')
    if not s_zl and not s_it:
        esito = 'uguale fra le mani'
    elif s_zl and s_it and {k[4:] for k in s_zl} & {k[4:] for k in s_it}:
        esito = 'diversa fra le mani'
    else:
        esito = 'incerto'
    out = OrderedDict([('mani', ris), ('differenze', diff), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c11_consumo_per_mano.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c11 — Il consumo con le lettere è uguale nelle tre mani?', '', 'Preregistrazione: `preregistrazioni/e3c11.md`. Pendenza per lettera a parità di parole e classe (e3c10), con i bordi.', '',
          '| trascrizione e mano | pagine | coppie | per lettera (IC 95%) |', '|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %+.4f (%+.4f – %+.4f) |' % (k, x['pagine'], x['coppie'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', '| differenza | valore (IC 95%) |', '|---|---|']
    for k, x in diff.items():
        md.append('| %s | %+.4f (%+.4f – %+.4f) |' % (k, x['differenza'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c11_consumo_per_mano.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
