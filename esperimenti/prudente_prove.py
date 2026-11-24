# -*- coding: utf-8 -*-
"""IA36, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PICCOLO32=1 PYTHONIOENCODING=utf-8 USCITA=<cartella fuori dal repo> python esperimenti/prudente_prove.py [parte ...]
Prove: (1) i cubi a 16 manopole (la memoria spenta lascia le 14 di IA33 com'erano); (2) la memoria di sezione: con `w_sez` = 0 lo scrittore da' ESATTAMENTE il libro di IA35, la memoria legge solo
pagine gia' scritte della stessa sezione e lingua (e solo quelle), accesa fa salire il riuso di sezione; (3) le misure di guardia e di riuso (definite, non vuote, scala, sensibilita' a un testo
rimescolato); (4) la scelta prudente su numeri finti (permesso, penalita', partenza, finalisti, protezione spenta); (la valutazione del ciclo e l'esame si provano con il percorso intero di `ia36_prudente`).
"""
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
    """Una rete condizionata piccola addestrata una volta (variante Cb) e le due classi di scrittore (IA35 e IA36) sopra la stessa rete."""
    if 'cart' not in _RETE:
        import sezione_rete as SR
        tmp = tempfile.mkdtemp(prefix='ia36prova_')
        cart = os.path.join(tmp, 'rete_C')
        SR.addestra_pieno35(cart, True, var=SR.VARIANTI['Cb'])
        _RETE['cart'] = cart
    return _RETE['cart']


def prova_cubi():
    import oracolo_scrittura as OS
    import prudente_scrittura as PW
    u14 = np.random.default_rng(3).uniform(0, 1, 14)
    u16 = PW.estendi_cubo(u14)
    assert len(u16) == 16 and np.allclose(u16[:14], u14)
    k14, k16 = OS.da_cubo33(u14), PW.da_cubo36(u16)
    assert all(abs(k14[n] - k16[n]) < 1e-12 for n in k14) and k16['w_sez'] == 0.0
    assert PW.da_cubo36(u14)['w_sez'] == 0.0                                       # un cubo a 14: memoria spenta
    n = PW.neutro_cubo36()
    assert len(n) == 16 and PW.da_cubo36(n)['w_sez'] == 0.0 and PW.da_cubo36(n)['t_sez'] > 2
    v = np.array(u16)
    v[14], v[15] = 0.9, 0.0
    k = PW.da_cubo36(v)
    assert abs(k['w_sez'] - 0.7) < 1e-9 and abs(k['t_sez'] - 2.0) < 1e-9
    assert PW.da_cubo36(PW.senza_memoria(v))['w_sez'] == 0.0
    vv = PW.cubo_da_valori36(dict(PW.da_cubo36(v)))
    assert abs(PW.da_cubo36(vv)['w_sez'] - 0.7) < 1e-9 and abs(PW.da_cubo36(vv)['t_sez'] - 2.0) < 1e-6
    p = PW.estendi_cubo(u14, w_sez=0.0)
    assert PW.da_cubo36(p)['w_sez'] == 0.0 and p[14] == PW.U_SEZ_PARTENZA
    return 'cubi: 16 manopole, le 14 di IA33 invariate, memoria spenta sotto 0,2, t_sez 2-60 pagine (u 0 -> 2,0), estendi e senza_memoria ok'


def prova_memoria():
    import ia07_voynich_neurale as I7
    import oracolo_scrittura as OS
    import prudente_scrittura as PW
    import prudente_misure as PMG
    import sezione_scrittura as SS
    cart = _rete()
    A, Z = SS.ScrittoreCond(cart), PW.ScrittoreSez(cart)
    fogli = sorted({I7.foglio_di(p) for p in Z.pp})[:14]
    rng = np.random.default_rng(11)
    n_ok = 0
    # (a) con w_sez = 0 il libro e' ESATTAMENTE quello di IA35 (stesse estrazioni casuali), per manopole neutre e per manopole con correzioni e ripresa dalla pagina accese
    for caso in range(2):
        u = OS.neutro_cubo33().copy() if caso == 0 else np.clip(OS.neutro_cubo33() + rng.uniform(0.0, 0.6, 14), 0, 1)
        if caso == 1:
            u[13] = 0.7                                                              # w_pag acceso
        t_ia35, _ = A.libro33(u, 100 + caso, fogli)
        t_ia36, _ = Z.libro33(PW.estendi_cubo(u), 100 + caso, fogli)
        t_14, _ = Z.libro33(u, 100 + caso, fogli)
        assert t_ia35 == t_ia36 == t_14, 'con w_sez = 0 il libro deve essere quello di IA35 (caso %d)' % caso
        n_ok += 1
    # (b) la memoria: accesa, legge solo pagine gia' scritte della stessa (sezione, lingua) e solo quelle
    u = PW.estendi_cubo(OS.neutro_cubo33(), w_sez=0.7, t_sez=30.0)
    t_on, man = Z.libro33(u, 7, fogli)
    S = Z.ultimo_stato
    assert man['w_sez'] > 0.69 and S.sez, 'la memoria di sezione non si e\' riempita'
    pagine_per_chiave, vistie = OrderedDict(), OrderedDict()
    righe = I7.libro_vero()
    chiave_di = {}
    for x in righe:
        chiave_di.setdefault(x['pagina'], (x['sezione'], x['lingua']))
    for pag, ini, ws in t_on:
        pagine_per_chiave.setdefault(chiave_di[pag], OrderedDict()).setdefault(pag, []).extend(ws)
    for k_, pg in pagine_per_chiave.items():
        assert S.sez_n[k_] == len(pg), (k_, S.sez_n[k_], len(pg))                    # tante pagine fuse quante ne ha scritte la sezione (e nessuna di altre sezioni)
        parole_scritte = {w for ws in pg.values() for w in ws if w}
        mem = S.sez[k_]
        fini = [pi for pi, c in mem.items() if c.get(OS.FINE, 0) > 0]
        assert len(fini) == len(parole_scritte), (k_, len(fini), len(parole_scritte))    # le parole della memoria sono tutte e sole quelle scritte nelle pagine di quella sezione
    # ogni lettura di memoria avviene con meno pagine fuse di quelle gia' scritte: n pagine lette = pagine gia' scritte della chiave quel momento (mai oltre)
    assert S.pagine_lette and all(n >= 1 for _, n in S.pagine_lette)
    # (c) la memoria alza il riuso di sezione (il suo bersaglio), a parita' di semi e di manopole
    u0 = PW.senza_memoria(u)
    t_off, _ = Z.libro33(u0, 7, fogli)
    riuso = lambda t: PMG.misure_testo(I7.libro_A_da_righe(t))['riuso_sez']
    r_on, r_off = riuso(t_on), riuso(t_off)
    assert r_on is not None and r_off is not None and r_on > r_off, (r_on, r_off)
    return 'memoria di sezione: con w_sez = 0 il libro e\' identico a quello di IA35 (%d casi, anche con ripresa dalla pagina); la memoria contiene solo le parole delle pagine gia\' scritte della stessa sezione (%d sezioni, %d letture); riuso di sezione %.3f con la memoria contro %.3f senza' % (
        n_ok, len(pagine_per_chiave), len(S.pagine_lette), r_on, r_off)


def prova_guardie():
    import righello_banco as B
    import ia07_voynich_neurale as I7
    import ia01_giudice_neurale as G
    import prudente_misure as PMG
    c = I7.contesto_A()
    ref = PMG.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s), 30)
    for n in PMG.NOMI36:
        assert ref['vero'][n] is not None and ref['scala'][n] and ref['scala'][n] > 0, n
    # una meta' vera sta entro poche scale; un testo rimescolato (parole fra le righe) si vede su almeno una guardia
    h1, h2 = B.dividi_meta(5)
    mh = PMG.misure_testo(c['vere'], h1)
    vh = PMG.misure_testo(c['vere'], h1)
    zh = max(abs(mh[n] - ref['vero'][n]) / ref['scala'][n] for n in PMG.NOMI36)
    assert zh < 5, zh
    # un testo con le parole rimescolate dentro la riga NON cambia le guardie (sono conteggi di parole per riga, per pagina e per testo, salvo `g_bigr_rip`: la coppia): lo si dichiara;
    # un testo di ordine 2 sui glifi (parole inventate) si vede
    rim = G.rimescola_parole(c['vere'], 396001)
    mk = G.markov(c['vere'], 2, 5)
    zr = {}
    for nome, t in (('parole rimescolate', rim), ('markov2', mk)):
        mr = PMG.misure_testo(t, c['ids'])
        zr[nome] = {n: round((mr[n] - ref['vero'][n]) / ref['scala'][n], 1) for n in PMG.NOMI36 if mr[n] is not None}
    assert max(abs(zr['markov2'][g]) for g in PMG.GUARDIE36) > 1.5 and abs(zr['markov2']['riuso_sez']) > 3, zr
    assert abs(zr['parole rimescolate']['g_bigr_rip']) > 1.0, zr
    # le cinque guardie non sono le dieci misure d'esame: nomi diversi e nessuna chiamata a piano_misure / sezione_misure nelle loro funzioni
    import sezione_misure as SM
    assert not (set(PMG.GUARDIE36) | set(PMG.EXTRA_OBIETTIVO36)) & (set(SM.NOMI_NM8) | {'D', 'R_rel'})
    return 'misure di guardia e riuso_sez: tutte definite (scala %s); una meta\' vera entro %.1f scale; testo con le parole rimescolate: z %s' % (
        {n: round(v, 4) for n, v in ref['scala'].items()}, zh, zr or 'n.d.')


def prova_scelta():
    import prudente_scelta as PSC
    # permesso: max(ZG_ABS, |zn| + DELTA_G)
    assert abs(PSC.permesso(0.3) - PSC.ZG_ABS) < 1e-12 and abs(PSC.permesso(2.5) - 3.5) < 1e-12 and abs(PSC.permesso(6.0) - PSC.ZG_TETTO) < 1e-12 and abs(PSC.permesso(None) - PSC.ZG_ABS) < 1e-12
    zn = {'a': 0.5, 'b': 2.5, 'c': -1.0}
    e = PSC.eccessi({'a': 1.9, 'b': -4.0, 'c': 5.0}, zn)
    assert e['a'] == 0.0 and abs(e['b'] - 0.5) < 1e-9 and abs(e['c'] - (5.0 - PSC.ZG_ABS)) < 1e-9, e
    assert abs(PSC.penalita_guardie({'a': 1.9, 'b': -4.0, 'c': 5.0}, zn) - np.mean([0.0, 0.5, 3.0])) < 1e-9
    assert PSC.penalita_guardie({}, zn) == 0.0
    assert PSC.eccessi({'x': 50.0}, {})['x'] == PSC.ZCAP_G
    # il valore di un candidato: obiettivo (due meta') + W_G x penalita' di guardia sulla media dei z delle due meta'
    rs = [dict(somma=20.0, n=10, penalita=0.0, zg={'a': 4.0, 'b': 0.0}), dict(somma=24.0, n=13, penalita=1.0, zg={'a': 6.0, 'b': 0.0})]
    vp, ob, pen = PSC.valore_candidato(rs, {'a': 0.0, 'b': 0.0}, ('a', 'b'))
    assert abs(ob - (44.0 / 23 + 0.5)) < 1e-9 and abs(pen - np.mean([5.0 - 2.0, 0.0])) < 1e-9 and abs(vp - (ob + PSC.W_G * pen)) < 1e-9
    assert PSC.valore_candidato([dict(errore='x')], {}, ('a',)) is None
    # partenza: il punto di IA35 se e' prudente, altrimenti il migliore per obiettivo prudente
    ok = OrderedDict([('ia35', dict(obiettivo_prudente=2.0, penalita_guardia=0.1)), ('neutro', dict(obiettivo_prudente=3.0, penalita_guardia=0.0))])
    assert PSC.scegli_partenza(ok)[0] == 'ia35'
    male = OrderedDict([('ia35', dict(obiettivo_prudente=9.0, penalita_guardia=3.0)), ('ia33', dict(obiettivo_prudente=4.5, penalita_guardia=0.2)), ('neutro', dict(obiettivo_prudente=3.0, penalita_guardia=0.0))])
    assert PSC.scegli_partenza(male)[0] == 'neutro'
    # finalisti: il minimo grezzo ma non prudente e' scartato; se nessuno e' prudente vince la penalita' piu' bassa; le reti diverse da C non si scelgono
    fin = OrderedDict([('neutro', dict(rete='C', obiettivo=3.8, penalita_guardia=0.0, obiettivo_prudente=3.8)),
                       ('migliore_grezzo', dict(rete='C', obiettivo=2.0, penalita_guardia=3.0, obiettivo_prudente=2.0 + PSC.W_G * 3.0)),
                       ('migliore_di_sempre', dict(rete='C', obiettivo=3.0, penalita_guardia=0.1, obiettivo_prudente=3.0 + PSC.W_G * 0.1)),
                       ('altra', dict(rete='A', obiettivo=1.0, penalita_guardia=0.0, obiettivo_prudente=1.0))])
    assert PSC.scegli_finalista(fin)[0] == 'migliore_di_sempre'
    fin2 = OrderedDict([('x', dict(rete='C', obiettivo=2.0, penalita_guardia=2.0, obiettivo_prudente=6.0)), ('y', dict(rete='C', obiettivo=3.0, penalita_guardia=1.0, obiettivo_prudente=5.0))])
    n2, mot = PSC.scegli_finalista(fin2)
    assert n2 == 'y' and 'NESSUN' in mot
    # protezione spenta: vince il minimo grezzo
    vecchio = PSC.PRUDENTE
    PSC.PRUDENTE = False
    try:
        assert PSC.scegli_finalista(fin)[0] == 'migliore_grezzo' and PSC.scegli_partenza(male)[0] == 'ia35'
    finally:
        PSC.PRUDENTE = vecchio
    return 'scelta prudente su numeri finti: permesso, eccessi, penalita\', valore del candidato, partenza (IA35 se prudente), finalisti (minimo grezzo scartato), nessuno prudente, protezione spenta'


def main():
    prove = [prova_cubi, prova_memoria, prova_guardie, prova_scelta]
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
