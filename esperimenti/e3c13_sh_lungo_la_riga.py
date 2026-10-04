# -*- coding: utf-8 -*-
"""Esperimento e3c13: la quota di sh (contro ch) cala lungo la riga, a parità di parola coperta? Previsione
dell'ipotesi "inchiostro" (il trattino di sh svanisce man mano che la penna si scarica, e si intinge a inizio riga).
Pendenza della scelta sui segni scritti prima nella riga, dentro strati (classe, parola coperta), senza la prima e
l'ultima parola della riga; intervalli ricampionando pagine. ZL e IT; per confronto le scelte robuste.

Preregistrazione: preregistrazioni/e3c13.md. Scrive risultati/e3c13_sh_lungo_la_riga.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def osservazioni(uu, f):
    """(unità, parola coperta, segni prima nella riga, valore) per le parole della classe, senza prima e ultima della riga."""
    out = []
    for u, righe in enumerate(uu):
        for r in righe:
            prima = 0
            for i, w in enumerate(r):
                x = f(w)
                if x is not None and 0 < i < len(r) - 1:
                    out.append((u, x[1], prima, x[0]))
                prima += len(w)
    return out


def pendenza(uu, classi, rng):
    obs = [(u, (k, cop), x, v) for k, f in classi.items() for (u, cop, x, v) in osservazioni(uu, f)]
    un = np.array([o[0] for o in obs])
    _, strato = np.unique(np.array([hash(o[1]) for o in obs]), return_inverse=True)
    x = np.array([o[2] for o in obs], dtype=float)
    y = np.array([o[3] for o in obs], dtype=float)
    n_u, n_s = len(uu), int(strato.max()) + 1
    st = e3c10.statistiche(strato, x, y, un, n_u, n_s)
    oss = float(e3c10.pendenza(st.sum(0)))
    boot = np.array([e3c10.pendenza(st[rng.integers(0, n_u, n_u)].sum(0)) for _ in range(BOOT)])
    return OrderedDict([('parole', len(obs)), ('quota_1', float(y.mean())), ('per_segno', oss), ('per_10_segni', 10 * oss),
                        ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])])


def main():
    rng = np.random.default_rng(3313)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, _ = e3b62.voynich(pd, mano)
        for k in e3b62.CV:
            ris['%s, %s' % (q, k)] = pendenza(uu, OrderedDict([(k, e3b62.CV[k])]), rng)
            print(q, k, json.dumps(ris['%s, %s' % (q, k)]), flush=True)
    sh = [ris['%s, sh/ch' % q]['IC95'] for q in ('ZL', 'IT')]
    if all(x[1] < 0 for x in sh):
        esito = "compatibile con l'inchiostro: sh cala lungo la riga"
    elif all(x[1] >= 0 for x in sh):
        esito = "non compatibile con l'inchiostro: sh non cala lungo la riga"
    else:
        esito = 'incerto'
    out = OrderedDict([('pendenze', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c13_sh_lungo_la_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c13 — La quota di sh cala lungo la riga?', '', 'Preregistrazione: `preregistrazioni/e3c13.md`. Pendenza della scelta (1 = qo, k, sh, -ey) sui segni scritti prima nella riga, a parità di parola coperta, senza prima e ultima parola.', '',
          '| trascrizione, classe | parole | quota del primo valore | per 10 segni (IC 95%) |', '|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.3f | %+.4f (%+.4f – %+.4f) |' % (k, x['parole'], x['quota_1'], x['per_10_segni'], 10 * x['IC95'][0], 10 * x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c13_sh_lungo_la_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
