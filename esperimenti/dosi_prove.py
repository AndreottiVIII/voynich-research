# -*- coding: utf-8 -*-
"""IA40, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PICCOLO32=1 EPOCHE32=3 PYTHONIOENCODING=utf-8 USCITA=<cartella nel repo> python esperimenti/dosi_prove.py [parte ...]
Prove: (1) `dosi`: il termostato a forza f moltiplica ESATTAMENTE le cinque manopole di conteggio e lascia ferme le altre; f = 1 e' il punto di IA35; (2) `righe`: le righe della tavola; (3) `verdetto`: gli esiti scritti
prima su numeri finti; (4) `scrittori` (rete piccola): la riga t100 (scrittore di IA37) e il libro di IA36 con la memoria spenta sono identici; K cambia le tabelle di sezione; la memoria accesa cambia il libro.
"""
import json
import os
import sys
import tempfile

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

CONTI = ('w_cont', 'w_tri', 'w_quad', 'w_uni', 'w_bi')


def _base():
    """Il punto di IA35 per `vero` (solo i 14 numeri delle manopole, da `ciclo_esito.json`: niente testo ne' dati del Voynich)."""
    p = os.path.join(QUI, '..', 'dati', 'cache', 'ia35', 'vero', 'ciclo_esito.json')
    return np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float)[:14]


def prova_dosi():
    import oracolo_scrittura as OS
    import ia40_dosi as X
    u = _base()
    k1 = OS.da_cubo33(u)
    assert np.allclose(X.u_dose(u, 1.0), u)
    k0 = OS.da_cubo33(X.u_dose(u, 0.0))
    for n in CONTI:
        assert k0[n] == 0.0, n
    for f in (0.25, 0.5, 0.75):
        kf = OS.da_cubo33(X.u_dose(u, f))
        for n in CONTI:
            assert abs(kf[n] - f * k1[n]) < 1e-9, (f, n, kf[n], f * k1[n])
        for n in k1:
            if n not in CONTI:
                assert kf[n] == k1[n], n
    return 'termostato: forza 0, 0,25, 0,5, 0,75, 1 moltiplicano esattamente w_cont %.3f, w_tri %.3f, w_quad %.3f, w_uni %.3f, w_bi %.3f del punto di IA35 e lasciano ferme temperature, top_p, s, b_nuove, w_pag' % (
        k1['w_cont'], k1['w_tri'], k1['w_quad'], k1['w_uni'], k1['w_bi'])


def prova_righe():
    import prudente_scrittura as PW
    import freqsez_scrittura as FW
    import ia40_dosi as X
    u = _base()
    R = X.righe(u)
    assert list(R) == ['t000', 't025', 't050', 't075', 't100', 's50k30', 's50k100', 's50k300', 's100k30', 's100k100', 's100k300', 'm20', 'm50', 'neu', 't100r', 's100k100r'], list(R)
    assert all(len(r['spec'][1]) == (16 if r['spec'][0] == 'M' else 15) for r in R.values())
    assert np.allclose(R['t100']['spec'][1][:14], u) and FW.da_cubo37(R['t100']['spec'][1])['a_sez'] == 0.0
    for nome, a, K in (('s50k30', 0.5, 30), ('s50k100', 0.5, 100), ('s50k300', 0.5, 300), ('s100k30', 1.0, 30), ('s100k100', 1.0, 100), ('s100k300', 1.0, 300)):
        k = FW.da_cubo37(R[nome]['spec'][1])
        assert abs(k['a_sez'] - a) < 1e-9 and R[nome]['spec'][2] == K and np.allclose(R[nome]['spec'][1][:14], u)
    for nome, w in (('m20', 0.2), ('m50', 0.5)):
        k = PW.da_cubo36(R[nome]['spec'][1])
        assert abs(k['w_sez'] - w) < 1e-9 and abs(k['t_sez'] - PW.NEUTRO36['t_sez']) < 1e-6 and np.allclose(R[nome]['spec'][1][:14], u)
    assert FW.da_cubo37(R['neu']['spec'][1])['w_cont'] == 0.0 and FW.da_cubo37(R['neu']['spec'][1])['a_sez'] == 0.0
    assert R['t100r']['spec'] == R['t100']['spec']
    return 'tavola: %d righe (%s), 8 libri ciascuna; a_sez 0,5 e 1 con K 30, 100, 300; w_sez 0,2 e 0,5 con decadimento neutro; neutro e due ripetizioni' % (len(R), ' '.join(R))


def prova_verdetto():
    import ia40_dosi as X

    def riga(z_sez, b, fuori, copia=True):
        mis = {m: dict(z=0.0, entro_2sigma=(m not in fuori)) for m in ('D', 'R_rel', 'heaps', 'burst', 'riga_cv', 'lag23', 'ini_par', 'ttr_pagina', 'hapax')}
        mis['sezione'] = dict(z=z_sez, entro_2sigma=abs(z_sez) <= 2)
        return dict(misure_tenute_fuori=mis, giudici_mai_visti=dict(b=dict(media=b)), copia_ok=copia)
    assert X.verdetto(riga(-1.5, 0.64, []))['buona']
    assert not X.verdetto(riga(-2.5, 0.64, []))['buona']
    assert not X.verdetto(riga(-1.5, 0.66, []))['buona']
    assert not X.verdetto(riga(-1.5, 0.64, ['D', 'burst', 'lag23']))['buona']
    assert X.verdetto(riga(-1.5, 0.64, ['D', 'burst']))['buona']
    assert not X.verdetto(riga(-1.5, 0.64, [], copia=False))['buona']
    return 'esiti scritti prima su numeri finti: sezione entro 2 sigma, b <= 0,65, almeno 7 delle altre 9 entro 2 sigma, copia a posto'


def prova_scrittori():
    import sezione_rete as SR
    import prudente_scrittura as PW
    import freqsez_scrittura as FW
    import freqsez_tabelle as FT
    import ia07_voynich_neurale as I7
    import oracolo_scrittura as OS
    import ia40_dosi as X
    base = os.path.join(QUI, '..', 'dati', 'cache', 'ia40_prove')
    os.makedirs(base, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='piccola_', dir=base)
    cart = os.path.join(tmp, 'rete_C')
    SR.addestra_pieno35(cart, True, var=SR.VARIANTI['Cb'])
    u14 = np.clip(OS.neutro_cubo33() + np.random.default_rng(4).uniform(0.0, 0.6, 14), 0, 1)
    u14[[6, 7, 8, 10, 11, 13]] = [0.6, 0.6, 0.6, 0.6, 0.6, 0.5]
    R = X.righe(u14)
    S36, S37 = PW.ScrittoreSez(cart), FW.ScrittoreFreq(cart)
    fogli = sorted({I7.foglio_di(p) for p in S37.pp})[:12]
    t100, _ = S37.libro33(np.asarray(R['t100']['spec'][1]), 21, fogli)
    t36, _ = S36.libro33(np.concatenate([u14, [0.2, 0.5]]), 21, fogli)
    assert t100 == t36, 't100 (scrittore di IA37) deve essere il libro di IA36 con la memoria spenta'
    t0, _ = S37.libro33(np.asarray(R['t000']['spec'][1]), 21, fogli)
    assert t0 != t100
    sa = FT.TabelleSezione(S37, S37.P.f_add, 30.0)
    sb = FT.TabelleSezione(S37, S37.P.f_add, 300.0)
    sez = sa.sezioni()[0]
    assert not np.allclose(sa.T2(sez)[0], sb.T2(sez)[0]) and np.allclose(sa.T2(sez)[0].sum(1), 1.0, atol=1e-6)
    X.RM._W['cart'] = tmp
    S30 = X.scrittore40(R['s100k30']['spec'])
    S300 = X.scrittore40(R['s100k300']['spec'])
    assert S30.K == 30.0 and S300.K == 300.0 and S30 is not S300
    t_a, man = S30.libro33(np.asarray(R['s100k30']['spec'][1]), 21, fogli)
    assert abs(man['a_sez'] - 1.0) < 1e-9 and t_a != t100
    SMEM = X.scrittore40(R['m50']['spec'])
    t_m, man_m = SMEM.libro33(np.asarray(R['m50']['spec'][1]), 21, fogli)
    assert abs(man_m['w_sez'] - 0.5) < 1e-9 and t_m != t100 and SMEM.ultimo_stato.sez
    return ('scrittori (rete piccola): la riga t100 (scrittore di IA37) e\' IDENTICA al libro di IA36 con la memoria spenta; t000 diverso; K 30 e 300 danno tabelle di sezione diverse e righe normalizzate; '
            'scrittore40 costruisce uno scrittore per ogni K; a_sez 1 cambia il libro; w_sez 0,5 cambia il libro e riempie la memoria')


def main():
    prove = [prova_dosi, prova_righe, prova_verdetto, prova_scrittori]
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
