# -*- coding: utf-8 -*-
"""Esperimento e3c14: memoria (e3b62 + e3b70) e pendenza per lettera (e3c10) con un nullo che conserva la posizione nella
riga: il rimescolamento avviene dentro (mano, parola coperta, fascia di posizione), così la deriva delle scelte lungo
la riga (e3c13) resta anche nel nullo. Confronto con il nullo solito nella stessa prova. ZL e IT, classi scelte a mano,
con i bordi (come la misura solita).

Preregistrazione: preregistrazioni/e3c14.md. Scrive risultati/e3c14_nullo_posizione.json e .md.
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
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3c09_regressione_lettere_parole as e3c09
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 500
BOOT = 2000


def fascia(segni_prima):
    """Fascia di posizione nella riga: prima parola, poi fasce di 10 segni fino a 30, poi oltre."""
    if segni_prima == 0:
        return 0
    return min(1 + (segni_prima - 1) // 10, 4)


def con_posizione(c, uu, f):
    """Copia dei dati preparati (e3b62.prepara o e3c09.prepara) con i gruppi del rimescolamento estesi alla fascia di
    posizione. Le parole della classe si ritrovano nello stesso ordine in cui le ha numerate prepara."""
    fasce = []
    for u, righe in enumerate(uu):
        for r in righe:
            prima = 0
            for w in r:
                if f(w) is not None:
                    fasce.append(fascia(prima))
                prima += len(w)
    assert len(fasce) == len(c['val'])
    _, grp = np.unique(np.array(c['grp']) * 10 + np.array(fasce), return_inverse=True)
    d = dict(c)
    d['grp'] = grp
    return d


def pendenza(cc, n_u, rng):
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
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
    return OrderedDict([('nullo', mu), ('effetto', oss - mu), ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])])


def memoria(cc, rng):
    pr = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
    return OrderedDict([('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3314)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        m_cc = OrderedDict((k, e3b62.prepara(uu, ss, f)) for k, f in e3b62.CV.items())
        p_cc = OrderedDict((k, e3c09.prepara(uu, ss, f)) for k, f in e3b62.CV.items())
        x = OrderedDict()
        x['memoria, nullo solito'] = memoria(m_cc, rng)
        x['memoria, nullo con posizione'] = memoria(OrderedDict((k, con_posizione(c, uu, e3b62.CV[k])) for k, c in m_cc.items()), rng)
        x['per lettera, nullo solito'] = pendenza(p_cc, len(uu), rng)
        x['per lettera, nullo con posizione'] = pendenza(OrderedDict((k, con_posizione(c, uu, e3b62.CV[k])) for k, c in p_cc.items()), len(uu), rng)
        x['per lettera sh/ch, nullo con posizione'] = pendenza(OrderedDict([('sh/ch', con_posizione(p_cc['sh/ch'], uu, e3b62.CV['sh/ch']))]), len(uu), rng)
        rob = OrderedDict((k, con_posizione(p_cc[k], uu, e3b62.CV[k])) for k in ('qo/o', 'k/t', '-ey/-dy'))
        x['per lettera robuste, nullo con posizione'] = pendenza(rob, len(uu), rng)
        ris[q] = x
        print(q, json.dumps(x, default=float), flush=True)
    rapp = [ris[q]['memoria, nullo con posizione']['effetto'] / ris[q]['memoria, nullo solito']['effetto'] for q in ('ZL', 'IT')]
    if all(ris[q]['memoria, nullo con posizione']['IC95'][0] > 0 for q in ('ZL', 'IT')) and min(rapp) >= 2 / 3:
        esito = 'la memoria non viene dalla deriva lungo la riga'
    elif max(rapp) < 1 / 2:
        esito = 'la memoria viene in buona parte dalla deriva lungo la riga'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('rapporti_memoria', rapp), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c14_nullo_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c14 — Memoria e consumo con un nullo che conserva la posizione nella riga', '', 'Preregistrazione: `preregistrazioni/e3c14.md`.', '',
          '| trascrizione | misura | nullo | effetto (IC 95%) |', '|---|---|---|---|']
    for q, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s | %+.4f | %+.4f (%+.4f – %+.4f) |' % (q, k, y['nullo'], y['effetto'], y['IC95'][0], y['IC95'][1]))
    md += ['', 'Memoria con il nullo che conserva la posizione, rispetto al nullo solito: ZL %.2f, IT %.2f. Esito: **%s**.' % (rapp[0], rapp[1], esito)]
    open(os.path.join(RISULTATI, 'e3c14_nullo_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
