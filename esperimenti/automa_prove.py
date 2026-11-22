# -*- coding: utf-8 -*-
"""Prove di unita' di ia31 (modulo di supporto: non e' un esperimento). Solo testi sintetici e il latino di prova (SOLO_CONTROLLI=1):

    SOLO_CONTROLLI=1 python esperimenti/automa_prove.py

Controlla: la distribuzione sulle parole e' esatta (somma a 1); la verosimiglianza della propagazione coincide con la somma su tutti i percorsi; l'EM non peggiora la
verosimiglianza; le caselle restano triangolari; i costi per posizione sommano al totale e coincidono con le probabilita' condizionate; il costo a trigrammi coincide con
`rifarlo_ritocchi.costo_nuove`; il generatore sintetico e' ritrovato; i conteggi per piega sono una partizione.
"""
import itertools
import math
import os
import sys
from collections import Counter

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import automa_hmm as H  # noqa: E402
import automa_testi as AT  # noqa: E402


def automa_casuale(K, V, famiglia, seme):
    rng = np.random.default_rng(seme)
    al = H.Alfabeto(['a%d' % i for i in range(V)])
    pi = H._normalizza(1 + rng.random(K))
    A = H._normalizza(rng.random((K, K)), H._maschera(K, famiglia))
    B = rng.random((K, al.NS))
    B[:, al.RARO] = 0
    B[:, al.FINE] += 1.5
    B = H._normalizza(B)
    return H.Automa(K, al, famiglia, pi, A, B)


def prova_normalizzazione():
    """Parole di 1-7 glifi + parola vuota + massa delle parole con almeno 8 glifi (calcolata a parte) = 1."""
    for fam in ('libero', 'caselle'):
        a = automa_casuale(3, 3, fam, 1)
        al = a.al
        tot = 0.0
        for n in range(1, 8):
            for w in itertools.product(range(al.V), repeat=n):
                S = np.array([list(w) + [al.FINE]])
                tot += float(2.0 ** (-a.costi_posizione(S).sum()))
        vuote = float((a.pi * a.B[:, al.FINE]).sum())
        em = a.B[:, :al.V].sum(1)
        v = a.pi.copy()
        for t in range(8):
            v = (v * em) @ a.A
        sopra = float(v.sum())
        assert abs(tot + vuote + sopra - 1.0) < 1e-9, (fam, tot, vuote, sopra)
    print('normalizzazione: la distribuzione sulle parole somma a 1 (liberi e a caselle)')


def prova_percorsi():
    """La verosimiglianza della propagazione scalata = somma su tutti i percorsi di stato (enumerati)."""
    a = automa_casuale(3, 4, 'libero', 2)
    al = a.al
    for w in [(0,), (1, 2), (3, 0, 1), (2, 2, 3, 1)]:
        s = list(w) + [al.FINE]
        exact = 0.0
        for cam in itertools.product(range(a.K), repeat=len(s)):
            p = a.pi[cam[0]] * a.B[cam[0], s[0]]
            for t in range(1, len(s)):
                p *= a.A[cam[t - 1], cam[t]] * a.B[cam[t], s[t]]
            exact += p
        got = 2.0 ** (-a.costi_posizione(np.array([s])).sum())
        assert abs(got - exact) < 1e-12 * max(1, exact) + 1e-15, (w, got, exact)
    print('percorsi: la propagazione coincide con la somma su tutti i percorsi (4 parole, 3 stati)')


def prova_condizionali():
    """I costi per posizione sono probabilita' condizionate: per ogni prefisso la somma sui segni successivi e' 1."""
    a = automa_casuale(4, 3, 'libero', 3)
    al = a.al
    for prefisso in [[], [0], [1, 2], [2, 0, 1]]:
        tot = 0.0
        for x in range(al.NS):
            S = np.array([prefisso + [x]])
            tot += 2.0 ** (-a.costi_posizione(S)[0, -1])
        assert abs(tot - 1.0) < 1e-12, (prefisso, tot)
    print('condizionali: le probabilita\' del segno dopo un prefisso sommano a 1')


def parole_di_prova(seme=5, n=400, K0=4):
    a = AT.generatore('L', K0, seme)
    parole = AT.campiona_parole(a, n, seme)
    return a, parole


def prova_em():
    """L'EM non peggiora la verosimiglianza; le caselle restano triangolari; i costi per posizione sommano al totale."""
    a0, parole = parole_di_prova()
    c = Counter(parole)
    p = sorted(c)
    al = H.Alfabeto(sorted({g for w in p for g in w}))
    gr = H.gruppi_da_parole(p, [float(c[w]) for w in p], al)
    un, pm = H.statistiche(gr, al)
    for fam in ('libero', 'caselle'):
        prec = None
        for giri in (1, 3, 6, 12, 24):
            a, info = H.stima(gr, al, 4, fam, 7, giri=giri, riavvii=1, unigramma=un, pos_media=pm)
            ll = -a.ll_bit(gr)
            if prec is not None:
                assert ll >= prec - 1e-6 * abs(prec), (fam, giri, ll, prec)
            prec = ll
        if fam == 'caselle':
            assert np.allclose(np.tril(a.A, -1), 0.0)
        # somma dei bit per posizione = bit totali
        tot = a.ll_bit(gr)
        parti, gl, n = AT.parti_gruppi(a, gr)
        assert abs(parti.sum() - tot) < 1e-6, (parti.sum(), tot)
        assert abs(n - sum(c.values())) < 1e-9
        assert abs(gl - sum(len(w) * k for w, k in c.items())) < 1e-9
    # determinismo
    a1, _ = H.stima(gr, al, 4, 'libero', 9, giri=5, unigramma=un, pos_media=pm)
    a2, _ = H.stima(gr, al, 4, 'libero', 9, giri=5, unigramma=un, pos_media=pm)
    assert np.array_equal(a1.A, a2.A) and np.array_equal(a1.B, a2.B)
    print('EM: verosimiglianza non decrescente, caselle triangolari, parti per posizione = totale, determinismo')


def prova_k1():
    """K = 1 in forma chiusa: il costo e' l'entropia dei segni (con la lunghezza geometrica)."""
    a0, parole = parole_di_prova(seme=6)
    c = Counter(parole)
    p = sorted(c)
    al = H.Alfabeto(sorted({g for w in p for g in w}))
    gr = H.gruppi_da_parole(p, [float(c[w]) for w in p], al)
    a = H.stima_k1(gr, al)
    cnt = Counter()
    for w, k in c.items():
        for g in w:
            cnt[g] += k
        cnt['#'] += k
    N = sum(cnt.values())
    atteso = -sum(k * math.log2(k / N) for k in cnt.values())
    assert abs(a.ll_bit(gr) - atteso) < 0.01 * atteso, (a.ll_bit(gr), atteso)
    print('K = 1: costo %.1f bit contro entropia dei segni %.1f' % (a.ll_bit(gr), atteso))


def prova_recupero():
    """Un automa noto con 4 stati: l'EM a 4 stati arriva vicino al costo dell'automa vero sulle parole di prova."""
    a0, parole = parole_di_prova(seme=8, n=6000, K0=4)
    c = Counter(parole)
    p = sorted(c)
    al = a0.al
    gr = H.gruppi_da_parole(p, [float(c[w]) for w in p], al)
    esatto = a0.ll_bit(gr)
    un, pm = H.statistiche(gr, al)
    a, _ = H.stima(gr, al, 4, 'libero', 11, giri=60, riavvii=4, unigramma=un, pos_media=pm)
    a1 = H.stima_k1(gr, al)
    n = sum(c.values())
    print('recupero: costo per parola, automa vero %.3f, EM a 4 stati %.3f, un solo stato %.3f' % (esatto / n, a.ll_bit(gr) / n, a1.ll_bit(gr) / n))
    assert a.ll_bit(gr) < 1.03 * esatto, 'l\'EM a 4 stati non raggiunge l\'automa vero'


def prova_generatore():
    """I due campionatori (veloce e per parola) producono la stessa distribuzione e nessuna parola vuota: il costo medio per parola sotto l'automa che ha generato i dati e' lo stesso."""
    for nome in ('sint_L4_1', 'sint_L8_1', 'sint_C6_1'):
        a0 = AT.automa_sintetico(nome)
        rng = np.random.default_rng(5)
        w1 = AT.campiona_parole(a0, 6000, 11)
        w2 = [tuple(a0.al.glifi[x] for x in a0.campiona(rng, massimo=30)) for _ in range(6000)]      # stesso limite di 30 glifi del campionatore veloce
        assert all(len(w) > 0 for w in w1 + w2)
        medie = []
        for ws in (w1, w2):
            c = Counter(ws)
            p = list(c)
            gr = H.gruppi_da_parole(p, [float(c[w]) for w in p], a0.al)
            medie.append(a0.ll_bit(gr) / sum(c.values()))
        assert abs(medie[0] - medie[1]) < 0.04 * medie[0], (nome, medie)
        print('  generatore %-9s bit per parola sotto automa vero: %.3f (veloce) e %.3f (per parola); lunghezza media %.2f' % (nome, medie[0], medie[1], sum(len(w) for w in w1) / len(w1)))
    print('generatore: i due campionatori coincidono, nessuna parola vuota')


def prova_pieghe():
    """I conteggi per piega sono una partizione: addestramento + fuori = tutto; nessuna parola in due pieghe."""
    T = AT.testo('vero')
    tot = Counter(w for rows in T['pagine'].values() for _, ws in rows for w in ws)
    for f in range(5):
        tr, te = AT.conti_piega(T['pagine'], T['fold'], f)
        assert tr + te == tot
    print('pieghe: addestramento + fuori = testo intero, per tutte e cinque le pieghe')


def prova_trigrammi():
    """Le parti del costo a trigrammi sommano a `rifarlo_ritocchi.costo_nuove` (stessa definizione di ia20 e ia24)."""
    import rifarlo_ritocchi as R
    T = AT.testo('vero')
    f = 2
    tr, te = AT.conti_piega(T['pagine'], T['fold'], f)
    forma = R.Forma(tr)
    noti = set(tr)
    nu = Counter({w: k for w, k in te.items() if w not in noti})
    pg = {p: rows for p, rows in T['pagine'].items() if T['fold'][p] == f}
    bit, gl, nn, tot_ = R.costo_nuove(forma, pg, noti)
    parti, gl2, n2 = AT.parti_trigrammi(forma, nu)
    assert abs(parti.sum() - bit) < 1e-6 and gl == gl2 and nn == n2, (parti.sum(), bit, gl, gl2, nn, n2)
    print('trigrammi: parti per posto = costo_nuove di ia20 (%.3f bit per glifo sulle parole nuove)' % (bit / gl))


def prova_catalogo():
    """I testi del catalogo si costruiscono, hanno le stesse pagine del vero e le parole sono tuple."""
    base = AT.testo('vero')
    nomi = ['lingua_latino', 'cif_V_3_i1', 'cif_F_3p5_i1', 'neg_N1', 'neg_N2', 'sint_L4_1', 'sint_C6_1', 'sint_vero', 'sint_gap', 'sint_neutro', 'lib_V21_13', 'lib_M1_1']
    for nome in nomi:
        t = AT.testo(nome)
        assert set(t['pagine']) <= set(base['pagine']), nome
        w0 = t['pagine'][next(iter(t['pagine']))][0][1][0]
        assert isinstance(w0, tuple), nome
        n = sum(len(ws) for rows in t['pagine'].values() for _, ws in rows)
        print('  catalogo %-14s pagine %d parole %d' % (nome, len(t['pagine']), n))
    # il rimescolamento di N1 conserva lunghezze e conteggi dei glifi, e un tipo dà sempre la stessa forma
    n1 = AT.testo('neg_N1')
    for p in list(base['pagine'])[:3]:
        for (_, ws0), (_, ws1) in zip(base['pagine'][p], n1['pagine'][p]):
            for a, b in zip(ws0, ws1):
                assert sorted(a) == sorted(b)
    print('catalogo: i testi si costruiscono; N1 conserva i glifi di ogni parola')


def prova_incroci_percorsi():
    """I percorsi dei libri degli imitatori coincidono con quelli di ia20, ia22, ia24 (solo se i moduli si importano; fuori da SOLO_CONTROLLI)."""
    if AT.SOLO_CONTROLLI:
        print('percorsi dei libri: non verificati (SOLO_CONTROLLI)')
        return
    import ia20_imitatore_gradini as I20
    import ia22_eco_e_legame as I22
    assert os.path.normpath(I20.percorso_libro(1, 3)) == os.path.normpath(os.path.join(AT.CACHE, 'ia20', 'libri', AT.PERCORSI_LIBRI['M1'][1] % 3))
    assert os.path.normpath(I22.percorso_libro('E2', 3)) == os.path.normpath(os.path.join(AT.CACHE, 'ia22', 'libri', AT.PERCORSI_LIBRI['E2'][1] % 3))
    print('percorsi dei libri: coincidono con ia20 e ia22')


if __name__ == '__main__':
    prova_normalizzazione()
    prova_percorsi()
    prova_condizionali()
    prova_em()
    prova_k1()
    prova_recupero()
    prova_generatore()
    prova_pieghe()
    prova_trigrammi()
    prova_catalogo()
    prova_incroci_percorsi()
    print('TUTTE LE PROVE SONO RIUSCITE')
