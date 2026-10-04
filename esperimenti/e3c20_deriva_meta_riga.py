# -*- coding: utf-8 -*-
"""Esperimento e3c20: dove avviene la deriva delle scelte lungo la riga (e3c13)? Pendenza della scelta (1 = qo, k, sh,
-ey) sui segni scritti prima, a parità di parola coperta, separata per le parole nella prima metà e nella seconda metà
della riga (posizione relativa del centro della parola); senza prima e ultima parola; righe di almeno 5 parole.
Differenza delle due pendenze con gli stessi ricampionamenti di pagine. ZL e IT.

Preregistrazione: preregistrazioni/e3c20.md. Scrive risultati/e3c20_deriva_meta_riga.json e .md.
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
MIN_PAROLE = 5


def osservazioni(uu, classi):
    """(unità, metà, chiave di strato, x, valore) per le parole interne delle righe di almeno MIN_PAROLE parole."""
    out = []
    for u, righe in enumerate(uu):
        for r in righe:
            if len(r) < MIN_PAROLE:
                continue
            L = sum(len(w) for w in r)
            prima = 0
            for i, w in enumerate(r):
                if 0 < i < len(r) - 1:
                    meta = 0 if (prima + len(w) / 2) / L < 0.5 else 1
                    for k, f in classi.items():
                        x = f(w)
                        if x is not None:
                            out.append((u, meta, (k, x[1]), prima, x[0]))
                prima += len(w)
    return out


def misura(uu, classi, rng):
    obs = osservazioni(uu, classi)
    n_u = len(uu)
    st = {}
    for meta in (0, 1):
        oo = [o for o in obs if o[1] == meta]
        un = np.array([o[0] for o in oo])
        _, strato = np.unique(np.array([hash(o[2]) for o in oo]), return_inverse=True)
        x = np.array([o[3] for o in oo], dtype=float)
        y = np.array([o[4] for o in oo], dtype=float)
        st[meta] = (e3c10.statistiche(strato, x, y, un, n_u, int(strato.max()) + 1), len(oo))
    oss = [float(e3c10.pendenza(st[m][0].sum(0))) for m in (0, 1)]
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n_u, n_u)
        boot.append([e3c10.pendenza(st[m][0][idx].sum(0)) for m in (0, 1)])
    boot = 10 * np.array(boot)
    diff = boot[:, 0] - boot[:, 1]
    ic = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    return OrderedDict([('prima_meta', OrderedDict([('parole', st[0][1]), ('per_10_segni', 10 * oss[0]), ('IC95', ic(boot[:, 0]))])),
                        ('seconda_meta', OrderedDict([('parole', st[1][1]), ('per_10_segni', 10 * oss[1]), ('IC95', ic(boot[:, 1]))])),
                        ('differenza_prima_meno_seconda', OrderedDict([('valore', 10 * (oss[0] - oss[1])), ('IC95', ic(diff))]))])


def main():
    rng = np.random.default_rng(3320)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, _ = e3b62.voynich(pd, mano)
        ris[q] = misura(uu, e3b62.CV, rng)
        print(q, json.dumps(ris[q]), flush=True)
    d = [ris[q]['differenza_prima_meno_seconda']['IC95'] for q in ('ZL', 'IT')]
    if all(x[1] < 0 for x in d):
        esito = "la deriva è più ripida all'inizio della riga"
    elif all(x[0] > 0 for x in d):
        esito = 'la deriva è più ripida verso il margine destro'
    elif all(x[0] <= 0 <= x[1] for x in d):
        esito = 'la deriva è uniforme lungo la riga'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c20_deriva_meta_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c20 — Dove avviene la deriva delle scelte lungo la riga?', '', 'Preregistrazione: `preregistrazioni/e3c20.md`. Pendenza ogni 10 segni (1 = qo, k, sh, -ey), a parità di parola coperta.', '',
          '| trascrizione | prima metà della riga | seconda metà | differenza (prima − seconda) |', '|---|---|---|---|']
    for q, x in ris.items():
        a, b, c = x['prima_meta'], x['seconda_meta'], x['differenza_prima_meno_seconda']
        md.append('| %s | %+.4f (%+.4f – %+.4f), %d parole | %+.4f (%+.4f – %+.4f), %d parole | %+.4f (%+.4f – %+.4f) |' % (
            q, a['per_10_segni'], a['IC95'][0], a['IC95'][1], a['parole'], b['per_10_segni'], b['IC95'][0], b['IC95'][1], b['parole'], c['valore'], c['IC95'][0], c['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c20_deriva_meta_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
