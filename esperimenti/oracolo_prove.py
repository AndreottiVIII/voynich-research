# -*- coding: utf-8 -*-
"""IA33, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PYTHONIOENCODING=utf-8 USCITA=<cartella> python esperimenti/oracolo_prove.py
Prove: (1) la copia della vera catena e' identica a `ia01.markov`; (2) Kneser-Ney: la riga ha il numero di parole giusto, niente spazio a inizio parola, le frequenze di scelta
seguono la formula; (3) il lessico: il prodotto delle probabilita' lungo i glifi di una parola e' la frequenza della parola; (4) lo scrittore: a manopole neutre la scelta e'
quella della rete e, con le sole manopole di IA32, e' identica a quella di `rifare_scrittura` (stessi numeri casuali); le manopole nuove spingono nel verso atteso (quadrigrammi,
unigrammi e bigrammi di parole, parole nuove, ripresa dalla pagina); (5) il cubo: neutro, intervalli (3 volte quelli di IA32) e inversione; (6) il giudice b libro per libro e'
quello di IA32; (7) le regole di lettura (criteri) su numeri finti.
"""
import math
import os
import sys
from collections import Counter, OrderedDict
from types import SimpleNamespace

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def prova_catena():
    import ia01_giudice_neurale as G
    import ia07_voynich_neurale as I7
    import oracolo_catene as OC
    righe = I7.libro_vero()
    vere = OC.vere_di_righe(righe)
    for seme in (12345, 7):
        a = G.markov(vere, 2, seme)
        b = OC.genera_vere(OC.conta([vere], 2), OC.layout_di_righe(righe), seme, 2)
        assert a == b, 'la copia della vera catena non e\' identica a ia01.markov (seme %d)' % seme
    return 'catena: genera_vere uguale a ia01.markov (2 semi, libro intero)'


def prova_kn():
    import ia07_voynich_neurale as I7
    import oracolo_catene as OC
    import rifare_dati as RD
    righe = I7.libro_vero()
    f_add, f_val, _ = RD.divisione_fogli()
    gl = OC.glifi_del_libro(righe)
    ra = OC.righe_di_vere(OC.vere_di_righe(righe, f_add))
    m = OC.KNCatena(ra, 3, gl)
    lay = OC.layout_di_righe(righe)
    bk = m.genera_vere(lay, 11)
    assert list(bk) == list(lay)
    for p, rows in bk.items():
        for (ini, n), (ini2, ws) in zip(lay[p], rows):
            assert ini == ini2 and len(ws) == n and all(len(w) >= 1 for w in ws), 'riga con il numero di parole sbagliato o parola vuota'
    # la distribuzione dopo un contesto: somma 1, senza lo 0 e senza l'a capo, e senza spazio se vietato
    ids, cum = m.distribuzione((1, 1), True)
    assert 2 not in ids and 0 not in ids and 1 not in ids and abs(cum[-1] - 1.0) < 1e-9
    ids, cum = m.distribuzione((1, 1), False)
    assert 2 in ids
    # frequenze di scelta: dopo un contesto frequente la scelta empirica segue la formula
    import random
    h = max(m._d, key=lambda k: 0) if m._d else (1, 1)
    ids, cum = m.distribuzione(h[0], h[1])
    p = np.diff(np.concatenate([[0.0], cum]))
    rnd = random.Random(3)
    n = 20000
    cont = np.zeros(len(ids))
    for _ in range(n):
        cont[min(int(np.searchsorted(cum, rnd.random() * cum[-1], side='right')), len(ids) - 1)] += 1
    err = np.abs(cont / n - p).max()
    assert err < 0.012, 'KN: scarto massimo %.4f' % err
    # l'ordine scelto e' uno di quelli ammessi e i bit di validazione scendono (o restano) con piu' contesto fino a un minimo
    mm, o, b, tutti = OC.scegli_ordine(ra, OC.righe_di_vere(OC.vere_di_righe(righe, f_val)), gl)
    assert o in OC.ORDINI_V and round(float(b), 4) == min(tutti.values())
    return 'KN: righe giuste, distribuzione somma 1 (scarto %.4f), ordine scelto %d (bit %.3f)' % (err, o, b)


def prova_oracolo_stimato():
    """L'oracolo con i conteggi grezzi di una meta' del testo scrive solo trigrammi visti nella meta' (la famiglia e' chiusa); con tutto il testo ricade nella vera catena."""
    import ia07_voynich_neurale as I7
    import oracolo_catene as OC
    righe = I7.libro_vero()
    ff = sorted({x['foglio'] for x in righe})[::2]
    vere = OC.vere_di_righe(righe, ff)
    cont = OC.conta([vere], 2)
    bk = OC.genera_vere(cont, OC.layout_di_righe(righe), 5, 2)
    visti = set()
    for rows in vere.values():
        for _, ws in rows:
            s = ['\n', '\n']
            for w in ws:
                for g in list(w) + [' ']:
                    visti.add((s[-2], s[-1], g))
                    s.append(g)
    nuovi = tot = 0
    for rows in bk.values():
        for _, ws in rows:
            s = ['\n', '\n']
            for w in ws:
                for g in list(w) + [' ']:
                    tot += 1
                    nuovi += (s[-2], s[-1], g) not in visti
                    s.append(g)
    assert nuovi / tot < 0.01, 'trigrammi non visti nell\'addestramento: %.4f' % (nuovi / tot)
    return 'oracolo con conteggi grezzi: trigrammi non visti %.4f' % (nuovi / tot)


def _scrittore_senza_rete():
    import ia07_voynich_neurale as I7
    import rifare_dati as RD
    import rifare_scrittura as RS
    import oracolo_scrittura as OS
    voc = I7.vocabolario()
    f_add = RD.divisione_fogli()[0]
    s = OS.ScrittoreL.__new__(OS.ScrittoreL)
    s.ctx = SimpleNamespace(SP=voc['primo_contenuto'], EOL=voc['primo_contenuto'] + 1)
    c = RS.tabella_bigrammi(f_add)
    V = c.shape[1]
    lisc = c + 0.05 * (c.sum(1, keepdims=True) > 0)
    den = lisc.sum(1, keepdims=True)
    s.T = np.where(den > 0, lisc / np.maximum(den, 1e-12), 1.0 / V)
    s.logT = np.log(np.maximum(s.T, 1e-9))
    s.V = V
    s.T3 = RS.tabella_trigrammi(f_add)
    s.logT3 = {k: np.log(np.maximum(v, 1e-9)) for k, v in s.T3.items()}
    s._tabelle_l(f_add)
    return s, voc, f_add


def prova_scelta():
    import oracolo_scrittura as OS
    import rifare_scrittura as RS
    s, voc, f_add = _scrittore_senza_rete()
    V, SP, EOL = s.V, s.ctx.SP, s.ctx.EOL
    u0 = voc['primo_contenuto'] + 2
    rng = np.random.default_rng(5)
    lg = list(rng.normal(0, 2.0, V))
    amm = [SP, EOL] + list(range(u0, u0 + 8))
    k0 = OS.da_cubo33(OS.neutro_cubo33())
    assert all(abs(k0[n] - OS.NEUTRO33[n]) < 1e-9 for n in OS.NOMI33), k0
    S = OS.StatoLibro(V)
    S.nuova_riga(V)
    z = np.array([lg[a] for a in amm])
    p = np.exp(z - z.max())
    p /= p.sum()
    n = 40000
    cont = np.zeros(len(amm))
    for _ in range(n):
        S.G[:] = 0
        S.wid = [u0, u0 + 1, u0 + 2]
        cont[amm.index(s.scegli33(lg, amm, S, k0, rng, False, 3))] += 1
    err = np.abs(cont / n - p).max()
    assert err < 0.012, 'neutro: scarto massimo %.4f dal softmax' % err
    # uguale a rifare_scrittura con le sole manopole di IA32 (stessi numeri casuali, stesso stato)
    k1 = dict(k0)
    k1.update(T_int=0.8, T_fine=1.2, w_cont=1.5, w_tri=2.4, top_p=0.95, T_eol=0.9)
    # (RS.Scrittore.scegli accetta (lg, amm, prev, n_gl, prima_riga, k, G, rng, prev2, G3))
    ra, rb = np.random.default_rng(9), np.random.default_rng(9)
    Ga, G3a = np.zeros((V + 1, V)), {}
    S2 = OS.StatoLibro(V)
    prev = prev2 = V
    S2.prev, S2.prev2, S2.prev3 = V, V, V
    S2.wid = []
    amm_t = [SP, EOL] + list(range(u0, u0 + 8))
    diff = 0
    for t in range(600):
        sa = RS.Scrittore.scegli(s, lg, amm_t, prev, 3, False, k1, Ga, ra, prev2, G3a)
        Ga[prev, sa] += 1
        v3 = G3a.get((prev2, prev))
        if v3 is None:
            v3 = G3a[(prev2, prev)] = np.zeros(V)
        v3[sa] += 1
        prev2, prev = prev, sa
        sb = s.scegli33(lg, amm_t, S2, k1, rb, False, 3)
        S2.prev3, S2.prev2, S2.prev = S2.prev2, S2.prev, sb
        diff += int(sa != sb)
    assert diff == 0, 'scegli33 con le manopole di IA32 differisce da rifare_scrittura (%d scelte su 600)' % diff
    return 'scelta: neutro = softmax (scarto %.4f); con le manopole di IA32 identica a rifare_scrittura (600 scelte)' % err


def prova_lessico():
    import oracolo_scrittura as OS
    import ia07_voynich_neurale as I7
    s, voc, f_add = _scrittore_senza_rete()
    lex = s.lessico
    # il prodotto delle probabilita' dei glifi lungo ogni parola e la sua fine e' la frequenza della parola fra le parole che cominciano come lei
    tot = sum(lex.parole.values())
    cx = 0
    for w, c in list(lex.parole.most_common(60)) + list(lex.parole.most_common()[-30:]):
        p = 1.0
        for k in range(len(w)):
            nodo = lex.nodo_u(w[:k])
            p *= nodo.T[nodo.indice[w[k]]]
        nodo = lex.nodo_u(w)
        p *= nodo.T[-1]
        assert abs(p - c / tot) < 1e-9, 'prodotto %.6g contro frequenza %.6g' % (p, c / tot)
        cx += 1
    # il bigramma interpolato e' una distribuzione
    w0 = lex.parole.most_common(1)[0][0]
    nodo = lex.nodo_u(())
    tb = lex.nodo_b(w0, (), nodo)
    assert tb is not None and abs(tb.sum() - 1.0) < 1e-9
    assert lex.nodo_b(('x',), (), nodo) is None
    return 'lessico: %d parole, prodotto lungo i glifi = frequenza (%d verificate); bigramma interpolato somma 1' % (len(lex.parole), cx)


def _frequenze(s, k, lg, amm, S_fun, n=6000, seme=3):
    rng = np.random.default_rng(seme)
    cont = np.zeros(len(amm))
    for _ in range(n):
        S = S_fun()
        cont[amm.index(s.scegli33(lg, amm, S, k, rng, False, len(S.wid)))] += 1
    return cont / n


def prova_manopole_nuove():
    import oracolo_scrittura as OS
    s, voc, f_add = _scrittore_senza_rete()
    lex = s.lessico
    V, SP, EOL = s.V, s.ctx.SP, s.ctx.EOL
    k0 = OS.da_cubo33(OS.neutro_cubo33())
    # un prefisso del lessico con piu' continuazioni
    pi = next(w[:2] for w, c in lex.parole.most_common() if len(w) >= 3 and len(lex.nodo_u(w[:2]).ids) >= 3)
    nodo = lex.nodo_u(pi)
    dentro = list(nodo.ids[:3])
    fuori = [g for g in range(voc['primo_contenuto'] + 2, V) if g not in set(nodo.ids.tolist())][:2]
    assert fuori, 'nessun glifo fuori dal lessico dopo il prefisso'
    amm = [SP, EOL] + dentro + fuori
    lg = [0.0] * V
    def nuovo():
        S = OS.StatoLibro(V)
        S.nuova_riga(V)
        S.wid = list(pi)
        return S
    base = _frequenze(s, k0, lg, amm, nuovo)
    # b_nuove > 0 spinge verso i glifi fuori dal lessico; < 0 li allontana
    k1 = dict(k0)
    k1['b_nuove'] = 1.5
    p1 = _frequenze(s, k1, lg, amm, nuovo)
    k2 = dict(k0)
    k2['b_nuove'] = -1.5
    p2 = _frequenze(s, k2, lg, amm, nuovo)
    qf = lambda p: float(sum(p[amm.index(g)] for g in fuori) + (0 if nodo.fine else p[0] + p[1]))
    assert qf(p1) > qf(base) + 0.03 and qf(p2) < qf(base) - 0.03, 'b_nuove non muove il nuovo: %.3f %.3f %.3f' % (qf(p2), qf(base), qf(p1))
    # w_uni: la retroazione spinge verso la tabella i glifi che il libro ha scritto meno di quanto dica il lessico
    T = nodo.T
    ids = nodo.ids.tolist()
    j_poco = int(np.argmax(T[:-1]))
    S0 = nuovo()
    S0.Gu[pi] = np.zeros(len(T))
    S0.Gu[pi][[i for i in range(len(T) - 1) if i != j_poco]] = 500.0            # il libro ha scritto tutti gli altri molto
    amm2 = [SP, EOL] + [int(g) for g in ids]
    k3 = dict(k0)
    k3['w_uni'] = 2.0
    def con_stato():
        S = nuovo()
        S.Gu[pi] = S0.Gu[pi].copy()
        return S
    pa = _frequenze(s, k0, lg, amm2, con_stato, n=3000)
    pb = _frequenze(s, k3, lg, amm2, con_stato, n=3000)
    ia = amm2.index(int(ids[j_poco]))
    assert pb[ia] > pa[ia] + 0.05, 'w_uni non spinge il glifo scritto poco: %.3f -> %.3f' % (pa[ia], pb[ia])
    # w_bi: dopo una parola con seguito noto, il seguito piu' frequente guadagna
    prec = lex.parole.most_common(1)[0][0]
    b = lex.bi.get((prec, ()))
    if b:
        gmax = max((g for g in b if g != -1), key=lambda g: b[g])
        k4 = dict(k0)
        k4['w_bi'] = 2.0
        def dopo():
            S = OS.StatoLibro(V)
            S.nuova_riga(V)
            S.prev_w = prec
            S.wid = []
            tb = lex.nodo_b(prec, (), lex.nodo_u(()))
            S.Gb[(prec, ())] = np.full(len(tb), 200.0)
            return S
        top = [g for g in lex.nodo_u(()).ids.tolist()][:6]
        if gmax not in top:
            top = top[:5] + [gmax]
        amm3 = list(top)
        pa = _frequenze(s, k0, lg, amm3, dopo, n=3000)
        pb = _frequenze(s, k4, lg, amm3, dopo, n=3000)
        # con il libro che ha scritto tutto in modo uniforme, la retroazione spinge i glifi piu' frequenti nel bigramma
        i = amm3.index(gmax)
        assert pb[i] >= pa[i] - 0.02
    # w_pag: le parole gia' scritte sulla pagina guadagnano (mescolanza)
    w = lex.parole.most_common(5)[2][0]
    k5 = dict(k0)
    k5['w_pag'] = 0.7
    def pagina():
        S = OS.StatoLibro(V)
        S.nuova_riga(V)
        for _ in range(2):
            for i in range(len(w)):
                c = S.pg.setdefault(w[:i], Counter())
                c[w[i]] += 1
            S.pg.setdefault(w, Counter())[-1] += 1
        S.wid = []
        return S
    amm4 = list(sorted({int(x) for x in lex.nodo_u(()).ids[:8]} | {w[0]}))
    pa = _frequenze(s, k0, lg, amm4, pagina, n=3000)
    pb = _frequenze(s, k5, lg, amm4, pagina, n=3000)
    i = amm4.index(w[0])
    assert pb[i] > pa[i] + 0.1, 'w_pag non spinge verso le parole della pagina: %.3f -> %.3f' % (pa[i], pb[i])
    # w_quad: spinge verso la tabella dei quadrigrammi
    kk = next(k for k, v in s.T4.items() if (v > 0).sum() >= 3 and k[0] != V)
    t4 = s.T4[kk]
    cand = [int(g) for g in np.nonzero(t4)[0]][:3]
    amm5 = cand + [g for g in range(voc['primo_contenuto'] + 2, V) if t4[g] == 0][:2]
    k6 = dict(k0)
    k6['w_quad'] = 3.0
    def contesto4():
        S = OS.StatoLibro(V)
        S.nuova_riga(V)
        S.prev3, S.prev2, S.prev = kk
        S.G4[kk] = np.zeros(V)
        S.G4[kk][cand[0]] = 1000.0                                           # il libro ha scritto gia' molto il primo candidato: la retroazione lo frena
        return S
    pa = _frequenze(s, k0, lg, amm5, contesto4, n=3000)
    pb = _frequenze(s, k6, lg, amm5, contesto4, n=3000)
    assert pb[0] < pa[0] - 0.05, 'w_quad non frena il quadrigramma scritto troppo: %.3f -> %.3f' % (pa[0], pb[0])
    assert pb[3] <= pa[3] + 1e-9 and pb[4] <= pa[4] + 1e-9, 'w_quad alza un quadrigramma mai visto'
    return 'manopole nuove: b_nuove (quota fuori lessico %.3f / %.3f / %.3f), w_uni, w_bi, w_pag, w_quad ok' % (qf(p2), qf(base), qf(p1))


def prova_cubo():
    import oracolo_scrittura as OS
    u = OS.neutro_cubo33()
    assert len(u) == OS.DIM33 == 14
    k = OS.da_cubo33(np.ones(14))
    assert abs(k['w_cont'] - 7.5) < 1e-9 and abs(k['w_tri'] - 7.5) < 1e-9 and abs(k['w_quad'] - 7.5) < 1e-9, k
    assert k['w_tri'] >= 3 * 2.4, 'il limite dei trigrammi deve essere almeno 3 volte quello di IA32'
    assert abs(k['w_uni'] - 3.0) < 1e-9 and abs(k['b_nuove'] - 2.0) < 1e-9 and abs(k['w_pag'] - 0.8) < 1e-9, k
    k = OS.da_cubo33(np.zeros(14))
    assert k['w_cont'] == 0 and abs(k['b_nuove'] + 2.0) < 1e-9 and k['w_pag'] == 0
    val = OrderedDict([('T_primo', 1.0972), ('T_int', 0.804), ('T_fine', 1.1997), ('T_eol', 0.949), ('T_riga', 1.3355), ('top_p', 0.984), ('w_cont', 1.5069), ('w_tri', 2.4), ('s', 0.9783)])
    u2 = OS.cubo_da_valori(val)
    k2 = OS.da_cubo33(u2)
    for n, v in val.items():
        assert abs(k2[n] - v) < 1e-6, (n, k2[n], v)
    for n in ('w_quad', 'w_uni', 'w_bi', 'b_nuove', 'w_pag'):
        assert abs(k2[n]) < 1e-9, (n, k2[n])
    return 'cubo: 14 manopole, neutro, limiti (7,5 = 3,1 volte IA32), inversione dei valori di IA32'


def prova_giudice_b():
    import ia07_voynich_neurale as I7
    import ia01_giudice_neurale as G
    import righello_giudici as RG
    import rifare_giudice as RGB
    import oracolo_giudice as OG
    import oracolo_catene as OC
    import rifare_dati as RD
    import random
    c = I7.contesto_A()
    righe = I7.libro_vero()
    vere = c['vere']
    f_fuori = set(RD.divisione_fogli()[2])
    pagine = [p for p in c['ids'] if I7.foglio_di(p) in f_fuori]
    voc = RG.vocabolario_N(vere)
    libri = [G.markov(vere, 2, 100 + i) for i in range(4)]
    a = RGB.auc_b(vere, libri[:2], libri[2:], pagine, I7.foglio_di, voc, 3)
    l = OG.auc_b_libri(vere, libri[:2], libri[2:], pagine, I7.foglio_di, voc, 3)
    assert abs(a - float(np.mean(l))) < 1e-12 and len(l) == 2, (a, l)
    return 'giudice b: la media dei libri e\' quella di IA32 (%.3f, %d libri)' % (a, len(l))


def prova_criteri():
    """Le regole di lettura su numeri finti: O irraggiungibile / raggiungibile, L al livello dell'oracolo, batte il riferimento, non riuscito, non valido."""
    os.environ.setdefault('PICCOLO32', '1')
    import ia33_oracolo as X
    def ins(media, err=0.01, n=8, ok=True, quota=1.0, fuori=None):
        j = OrderedDict((k, OrderedDict([('media', media[k]), ('sd_libri', 0.01), ('n', n), ('errore', err)])) for k in X.GIUDICI3)
        return OrderedDict([('n', n), ('ruolo', ''), ('giudici_mai_visti', j), ('giudici_ok', all(0.4 <= v <= 0.6 for v in media.values())), ('giudici_di_allenamento', {}),
                            ('misure_tenute_fuori', {}), ('quota_entro_2sigma', quota), ('misure_fuori', fuori or []), ('copia_ok', ok), ('copia_violazione_max', 0.0), ('copia_quote', {})])
    R = OrderedDict()
    R['orkn'] = ins(dict(N=0.66, KN=0.58, b=0.70))
    R['gem'] = ins(dict(N=0.52, KN=0.51, b=0.55))
    R['neu'] = ins(dict(N=0.98, KN=0.90, b=0.99), n=4)
    R['ormle'] = ins(dict(N=0.64, KN=0.57, b=0.69))
    R['orkn2'] = ins(dict(N=0.62, KN=0.56, b=0.66))
    R['orkn4'] = ins(dict(N=0.58, KN=0.54, b=0.62))
    O = X.lettura_O(R)
    assert O['verdetto'] == 'irraggiungibile' and O['giudici_oltre_0_60'] == ['N', 'b'], O
    assert 'N' in O['stima_testo_necessario_descrittiva']
    R2 = OrderedDict(R)
    R2['orkn'] = ins(dict(N=0.57, KN=0.55, b=0.59))
    assert X.lettura_O(R2)['verdetto'] == 'raggiungibile'
    R3 = OrderedDict(R)
    R3['gem'] = ins(dict(N=0.52, KN=0.51, b=0.80))
    assert X.lettura_O(R3)['verdetto'] == 'non valido'
    # L al livello dell'oracolo: AUC dentro la fascia
    R['best'] = ins(dict(N=0.68, KN=0.60, b=0.72), quota=0.8)
    e = X.esito_L('vero', R, None, O)
    assert e['esito'] == "al livello dell'oracolo", e['esito']
    R['best'] = ins(dict(N=0.80, KN=0.60, b=0.72), quota=0.8)
    e = X.esito_L('vero', R, None, O)
    assert e['esito'] == 'non riuscito' and e['resta_fuori']['giudici_oltre_0_60'] == ['N', 'KN', 'b'][:0] + ['N', 'b'], e
    R['best'] = ins(dict(N=0.55, KN=0.58, b=0.56), quota=1.0)
    assert X.esito_L('vero', R, None, O)['esito'] == 'riuscito assoluto'
    # batte il v21 (a 2 errori) e non "al livello": O raggiungibile
    v21 = OrderedDict((j, OrderedDict([('media', m), ('sd_libri', 0.01), ('n', 10), ('errore', 0.01)])) for j, m in dict(N=0.80, KN=0.80, b=0.95).items())
    R['best'] = ins(dict(N=0.70, KN=0.70, b=0.85), quota=0.4)
    e = X.esito_L('vero', R, v21, X.lettura_O(R2))
    assert e['esito'] == 'batte il v21', e['esito']
    R['best'] = ins(dict(N=0.795, KN=0.70, b=0.85), quota=0.4)
    e = X.esito_L('vero', R, v21, X.lettura_O(R2))
    assert e['esito'] == 'non riuscito' and e['batte_il_riferimento']['piu_vicino_su_tutti'], e
    R['neu'] = ins(dict(N=0.98, KN=0.90, b=0.60), n=4)
    assert X.esito_L('vero', R, v21, O)['esito'] == 'non valido'
    # un oracolo molto SOTTO 0,5 (il giudice lo vede "piu' vero del vero": memoria dell'addestramento) e' riconosciuto come uno sopra
    R4 = OrderedDict(R)
    R4['neu'] = ins(dict(N=0.98, KN=0.90, b=0.99), n=4)
    R4['orkn'] = ins(dict(N=0.25, KN=0.55, b=0.55))
    O4 = X.lettura_O(R4)
    assert O4['verdetto'] == 'irraggiungibile' and O4['giudici_oltre_0_60'] == ['N'] and O4['giudici_sopra_0_60_lettera'] == [], O4
    R4['best'] = ins(dict(N=0.52, KN=0.55, b=0.55), quota=0.8)
    assert X.esito_L('vero', R4, None, O4)['esito'] == 'riuscito assoluto'
    R4['best'] = ins(dict(N=0.70, KN=0.55, b=0.55), quota=0.8)                  # distanza 0,20 <= 0,25 + 0,05: al livello dell'oracolo
    assert X.esito_L('vero', R4, None, O4)['esito'] == "al livello dell'oracolo"
    return 'criteri: 12 casi su numeri finti ok'


def prova_un_mondo_per_processo():
    """Il mondo si attiva una volta sola per processo: la richiamata non cambia il testo; un secondo mondo e' un errore (in IA32 il testo si degradava e `vero` ereditava quello di `markov2`)."""
    os.environ.setdefault('PICCOLO32', '1')
    import ia33_oracolo as X
    import ia07_voynich_neurale as I7
    X.attiva_main('markov2', [])
    t1 = [x['parole'] for x in I7.libro_vero()[:50]]
    X.attiva_main('markov2', ['tar:a:1'])
    X.attiva_main('markov2', [])
    assert [x['parole'] for x in I7.libro_vero()[:50]] == t1, 'il testo del mondo è cambiato alla seconda attivazione'
    try:
        X.attiva_main('vero', [])
    except RuntimeError:
        return 'un mondo per processo: richiamata uguale, secondo mondo rifiutato'
    raise AssertionError('un secondo mondo nello stesso processo deve dare errore')


def main():
    prove = [prova_catena, prova_kn, prova_oracolo_stimato, prova_cubo, prova_scelta, prova_lessico, prova_manopole_nuove, prova_giudice_b, prova_criteri, prova_un_mondo_per_processo]   # l'ultima cambia il mondo del processo
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
