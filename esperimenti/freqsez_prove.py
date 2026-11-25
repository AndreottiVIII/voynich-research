# -*- coding: utf-8 -*-
"""IA37, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PICCOLO32=1 EPOCHE32=3 PYTHONIOENCODING=utf-8 USCITA=<cartella nel repo> python esperimenti/freqsez_prove.py [parte ...]
Prove: (1) i cubi a 15 manopole; (2) i conteggi per sezione vengono SOLO da pagine d'addestramento di quella sezione e sommano esattamente ai conteggi globali; le tabelle con ripiego sono normalizzate,
K grande da' la tabella globale; (3) la scelta del ripiego sulla validazione; (4) con `a_sez` = 0 lo scrittore da' ESATTAMENTE il libro di IA36 senza memoria (stessi semi), con `a_sez` > 0 cambia e usa
solo conti delle sezioni scritte; (5) la divergenza fra sezioni (definita; sezioni permutate: cade); (6) la diagnosi sul mondo di sviluppo (`diagnosi`, richiede `RETE37` e `MONDO37`: vedi sotto).
"""
import json
import os
import sys
import tempfile
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

_RETE = {}


def _rete():
    """Una rete condizionata piccola (variante Cb) addestrata una volta, in una cartella dentro il repo (`dati/cache/ia37_prove`), con un ripiego K fissato a mano per le prove di unita'."""
    if 'cart' not in _RETE:
        import sezione_rete as SR
        base = os.path.join(QUI, '..', 'dati', 'cache', 'ia37_prove')
        os.makedirs(base, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix='piccola_', dir=base)
        cart = os.path.join(tmp, 'rete_C')
        SR.addestra_pieno35(cart, True, var=SR.VARIANTI['Cb'])
        json.dump(dict(K=20.0), open(os.path.join(tmp, 'ripiego.json'), 'w'))
        _RETE['cart'] = cart
    return _RETE['cart']


def prova_cubi():
    import oracolo_scrittura as OS
    import prudente_scrittura as PW
    import freqsez_scrittura as FW
    u14 = np.random.default_rng(3).uniform(0, 1, 14)
    k14 = OS.da_cubo33(u14)
    k = FW.da_cubo37(u14)
    assert all(abs(k14[n] - k[n]) < 1e-12 for n in k14) and k['a_sez'] == 0.0 and k['w_sez'] == 0.0
    u15 = FW.da_cubo36(np.concatenate([u14, [0.9, 0.3]]))                          # un cubo di IA36 a 16: la memoria si butta, a_sez al bordo spento
    assert len(u15) == 15 and np.allclose(u15[:14], u14) and FW.da_cubo37(u15)['a_sez'] == 0.0 and FW.da_cubo37(u15)['w_sez'] == 0.0
    v = np.array(u15)
    v[14] = 1.0
    assert abs(FW.da_cubo37(v)['a_sez'] - 1.0) < 1e-12
    v[14] = 0.6
    assert abs(FW.da_cubo37(v)['a_sez'] - 0.5) < 1e-12
    assert FW.da_cubo37(FW.senza_frequenze(v))['a_sez'] == 0.0
    n = FW.neutro_cubo37()
    assert len(n) == 15 and FW.da_cubo37(n)['a_sez'] == 0.0 and abs(FW.da_cubo37(n)['w_cont']) < 1e-12
    p = FW.da_cubo36(u14, a_sez=0.5)
    assert abs(FW.da_cubo37(p)['a_sez'] - 0.5) < 1e-12
    return 'cubi: 15 manopole (le 14 di IA33 invariate, `a_sez` zero sotto 0,2 e uno a 1), conversione dai cubi di IA35/IA36 (memoria di sezione buttata), senza_frequenze'


def prova_conti():
    import rifare_dati as RD
    import rifare_scrittura as RS
    import ia16_imitatore as I16
    import ia07_voynich_neurale as I7
    import freqsez_tabelle as FT
    f_add, f_val, f_fuori = RD.divisione_fogli()
    pg = FT.pagine_di_addestramento(f_add)
    sp = FT.sezione_di_pagina()
    dp = I16.dati_pagine()
    ins, fuori = set(f_add), set(f_val) | set(f_fuori)
    tutte = [p for v in pg.values() for p in v]
    assert tutte and all(dp[p]['foglio'] in ins for p in tutte) and not any(dp[p]['foglio'] in fuori for p in tutte), 'solo pagine d\'addestramento'
    assert all(sp[p] == s for s, v in pg.items() for p in v), 'ogni pagina nella sua sezione'
    assert len(tutte) == len({p for p, d in dp.items() if d['foglio'] in ins}) == len(set(tutte))
    # i conti per sezione sommano ESATTAMENTE a quelli globali
    c2g = RS.tabella_bigrammi(f_add)
    somma2 = sum(FT.conti_segni(v)[0] for v in pg.values())
    assert np.array_equal(somma2, c2g), 'bigrammi: somma delle sezioni diversa dai conti globali'
    T3g = RS.tabella_trigrammi(f_add)
    somma3 = {}
    for v in pg.values():
        for k_, a in FT.conti_segni(v)[1].items():
            somma3[k_] = somma3.get(k_, 0) + a
    assert set(somma3) == set(T3g)
    for k_ in list(T3g)[:300]:
        l = somma3[k_] + 0.05 * (somma3[k_] > 0)
        assert np.allclose(l / l.sum(), T3g[k_]), 'trigrammi: tabella globale ricostruita dalla somma delle sezioni'
    sez = {s: len(v) for s, v in sorted(pg.items())}
    return 'conti per sezione: %d pagine d\'addestramento in %d sezioni %s, nessuna di validazione ne\' tenuta fuori; somma delle sezioni = conti globali (bigrammi esatti, trigrammi ricostruiti)' % (len(tutte), len(pg), sez)


def prova_ripiego():
    import types
    import rifare_dati as RD
    import rifare_scrittura as RS
    import freqsez_tabelle as FT
    f_add, f_val, _ = RD.divisione_fogli()
    sc = types.SimpleNamespace(T3=RS.tabella_trigrammi(f_add))
    r = FT.scegli_ripiego(sc, f_add, f_val)
    assert r['K'] in FT.GRIGLIA_K and r['n_segni'] > 500 and len(r['bit_per_K']) == len(FT.GRIGLIA_K)
    # K enorme = tabella globale: stessi bit
    r2 = FT.scegli_ripiego(sc, f_add, f_val, griglia=(1e12,))
    assert abs(r2['bit_per_K']['1000000000000'] - r2['bit_globale']) < 1e-6, (r2['bit_per_K'], r2['bit_globale'])
    # la regola: se nessun K batte la globale si prende il piu' grande
    assert r['batte_globale'] or r['K'] == max(FT.GRIGLIA_K)
    return 'ripiego sulla validazione: K = %g (batte la globale: %s); bit per segno globale %.4f, per K %s; con K enorme = globale (differenza < 1e-6)' % (
        r['K'], r['batte_globale'], r['bit_globale'], {k: round(v, 4) for k, v in r['bit_per_K'].items()})


def prova_scrittore():
    import oracolo_scrittura as OS
    import prudente_scrittura as PW
    import freqsez_scrittura as FW
    import ia07_voynich_neurale as I7
    cart = _rete()
    A, Z = PW.ScrittoreSez(cart), FW.ScrittoreFreq(cart)
    assert Z.K == 20.0
    fogli = sorted({I7.foglio_di(p) for p in Z.pp})[:14]
    rng = np.random.default_rng(5)
    for caso in range(2):
        u14 = OS.neutro_cubo33().copy() if caso == 0 else np.clip(OS.neutro_cubo33() + rng.uniform(0.0, 0.6, 14), 0, 1)
        if caso == 1:
            u14[[6, 7, 8, 10, 11, 12, 13]] = [0.6, 0.6, 0.6, 0.6, 0.6, 0.3, 0.6]           # w_cont, w_tri, w_quad, w_uni, w_bi, b_nuove, w_pag accese
        u16 = PW.estendi_cubo(u14)                                                             # IA36 con la memoria spenta
        u15 = np.concatenate([u14, [0.2]])
        t36, _ = A.libro33(u16, 300 + caso, fogli)
        t37, man = Z.libro33(u15, 300 + caso, fogli)
        t37b, _ = Z.libro33(u14, 300 + caso, fogli)
        assert t36 == t37 == t37b, 'con a_sez = 0 il libro deve essere quello di IA36 (caso %d)' % caso
        assert man['a_sez'] == 0.0 and man['w_sez'] == 0.0
    # con a_sez > 0 il libro cambia; i conti per sezione usano solo le sezioni scritte e solo le pagine d'addestramento di quella sezione
    u = np.concatenate([u14, [0.8]])
    t_a, man = Z.libro33(u, 301, fogli)
    assert t_a != t36 and abs(man['a_sez'] - 0.75) < 1e-9
    S = Z.ultimo_stato
    sezioni_scritte = {Z.pp[p][0]['sezione'] for p in Z.pp if I7.foglio_di(p) in set(fogli)}
    assert S.G2s and set(S.G2s) <= sezioni_scritte and all(k_[0] in sezioni_scritte for k_ in list(S.G3s) + list(S.G4s))
    assert sum(g.sum() for g in S.G2s.values()) == S.G.sum(), 'i conti per sezione sommano ai conti globali'
    return 'scrittore: con a_sez = 0 il libro e\' identico a quello di IA36 senza memoria (2 casi, con correzioni a segni e parole e w_pag accese; cubo a 14 e a 15); con a_sez 0,75 cambia; i conti per sezione sommano ai conti globali (%d segni) e riguardano solo le sezioni scritte %s' % (
        int(S.G.sum()), sorted(sezioni_scritte))


def prova_tabelle_scrittore():
    import freqsez_scrittura as FW
    import freqsez_tabelle as FT
    cart = _rete()
    Z = FW.ScrittoreFreq(cart)
    # tabelle normalizzate; K enorme = globale
    for s in Z.tab.sezioni():
        T, logT = Z.tab.T2(s)
        assert np.allclose(T.sum(1), 1.0, atol=1e-6) and T.shape == Z.T.shape
    alto = FT.TabelleSezione(Z, Z.P.f_add, 1e12)
    s0 = Z.tab.sezioni()[0]
    assert np.allclose(alto.T2(s0)[0], Z.T, atol=1e-8)
    for kk in list(Z.T3)[:200]:
        r = alto.T3(s0, kk)
        assert np.allclose(r[0], Z.T3[kk], atol=1e-8)
    for kk in list(Z.T4)[:200]:
        r = Z.tab.T4(s0, kk)
        assert r is not None and abs(r[0].sum() - 1.0) < 1e-6
    assert Z.tab.T3(s0, ('x', 'y')) is None
    # lessico di sezione: stessi nodi (stessi prefissi e stessi glifi) di quello globale
    ls = Z.lessico_sez(s0)
    n = 0
    for pi in list(Z.lessico.uni)[:300]:
        a, b = Z.lessico.nodo_u(pi), ls.nodo_u(pi)
        assert np.array_equal(a.ids, b.ids) and len(a.T) == len(b.T) and abs(b.T.sum() - 1.0) < 1e-9
        n += 1
    return 'tabelle con ripiego: righe normalizzate, K enorme = globale (bigrammi, trigrammi, quadrigrammi), contesti sconosciuti -> None; lessico di sezione con gli stessi nodi del globale (%d prefissi)' % n


def prova_divergenza():
    import ia07_voynich_neurale as I7
    import freqsez_tabelle as FT
    import random
    c = I7.contesto_A()
    d = FT.divergenza_sezioni(c['vere'], c['ids'])
    assert d['bigr'] is not None and d['parole'] is not None and d['bigr'] > 0 and d['parole'] > 0 and len(d['sezioni_bigr']) >= 3
    sp = FT.sezione_di_pagina()
    chiavi = list(sp)
    vals = list(sp.values())
    rnd = random.Random(1)
    rnd.shuffle(vals)
    perm = dict(zip(chiavi, vals))
    dp = FT.divergenza_sezioni(c['vere'], c['ids'], sezioni=perm)
    assert dp['bigr'] < d['bigr'] and dp['parole'] < d['parole']
    return 'divergenza fra sezioni (testo latino di prova): bigrammi %.4f, parole %.4f bit (sezioni %s); con le sezioni delle pagine permutate: %.4f e %.4f' % (
        d['bigr'], d['parole'], ','.join(d['sezioni_bigr']), dp['bigr'], dp['parole'])


def prova_diagnosi():
    """La diagnosi sul mondo di sviluppo. Richiede: `MONDO37` (struttura3 o vero), `CACHE37` (cartella del mondo con `rete_C` e `ripiego.json`, preparata da `ia37_frequenze.py` con FASI=P).
    Scrive per ogni punto 2 libri interi con lo scrittore a frequenze: rete sola (manopole neutre), correzioni globali (a_sez = 0) e correzioni di sezione (a_sez = 1), allo stesso punto forte;
    misura la divergenza fra sezioni. Previsione della diagnosi: globali < rete sola ~ vero < ... (le globali la riducono; quelle per sezione no)."""
    import ia37_frequenze as X
    import oracolo_scrittura as OS
    import freqsez_scrittura as FW
    import freqsez_tabelle as FT
    import ia07_voynich_neurale as I7
    mondo = os.environ.get('MONDO37', 'struttura3')
    X.attiva_main(mondo, [])
    cart = X.cart37(mondo, 'rete_C')
    S = FW.ScrittoreFreq(cart)
    c = I7.contesto_A()
    u = OS.neutro_cubo33().copy()
    forti = OrderedDict([('w_cont', 4.0), ('w_tri', 3.0), ('w_quad', 6.0), ('w_uni', 1.0), ('w_bi', 1.0)])
    cubo_forte = OS.cubo_da_valori(forti)
    punti = OrderedDict([('rete_sola', np.concatenate([u, [0.2]])), ('globali', np.concatenate([cubo_forte, [0.2]])), ('di_sezione', np.concatenate([cubo_forte, [1.0]]))])
    out = OrderedDict()
    vero = FT.divergenza_sezioni(c['vere'], c['ids'])
    out['vero'] = OrderedDict([('bigr', vero['bigr']), ('parole', vero['parole'])])
    n = int(os.environ.get('N_DIAG37', 2))
    for nome, uu in punti.items():
        bb, pp = [], []
        for i in range(n):
            t, _ = S.libro33(uu, 700 + i, None)
            d = FT.divergenza_sezioni(I7.libro_A_da_righe(t), c['ids'])
            bb.append(d['bigr'])
            pp.append(d['parole'])
        out[nome] = OrderedDict([('bigr', float(np.mean(bb))), ('parole', float(np.mean(pp))), ('sd_bigr', float(np.std(bb, ddof=1)) if n > 1 else None), ('sd_parole', float(np.std(pp, ddof=1)) if n > 1 else None), ('n', n)])
    print('diagnosi (mondo %s, K = %g): ' % (mondo, S.K) + '; '.join('%s bigrammi %.4f (sd %s) parole %.4f (sd %s)' % (k, v['bigr'], v.get('sd_bigr'), v['parole'], v.get('sd_parole')) for k, v in out.items()), flush=True)
    return json.dumps(out)


def main():
    prove = [prova_cubi, prova_conti, prova_ripiego, prova_scrittore, prova_tabelle_scrittore, prova_divergenza]
    filtro = sys.argv[1:]
    if 'diagnosi' in filtro:
        prove = [prova_diagnosi]
        filtro = []
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
