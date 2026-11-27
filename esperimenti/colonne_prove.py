# -*- coding: utf-8 -*-
"""IA45: prove del codice, SOLO su testi non Voynich (latino) e su numeri finti. Mai sulle trascrizioni del manoscritto.

    PYTHONHASHSEED=0 dati/cache/.venv_lm/Scripts/python esperimenti/colonne_prove.py [tempi]
"""
import os, sys, time
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import colonne_test as T
import colonne_controlli as C
import colonne_dati as CD

PROVE = []


def prova(f):
    PROVE.append(f)
    return f


@prova
def codifica_unica():
    cod, mappa = T.codifica([['a', 'b', '?', 'a'], ['?', 'b', None]])
    assert cod[0][0] == cod[0][3] and cod[0][1] == cod[1][1]
    neg = [x for c in cod for x in c if x < 0]
    assert len(neg) == 3 and len(set(neg)) == 3          # ogni '?' o None e' un numero negativo unico
    assert len(mappa) == 2


@prova
def a1_coppie_note():
    rng = np.random.default_rng(1)
    x = np.array(list(range(10)) * 3)
    y = np.array((list(range(4, 10)) + list(range(4))) * 2 + list(range(10)))
    obs, p = T.a1(x, y, 10, 2000, rng)
    assert obs >= 20                                      # il ciclo di 10 coppie, ripetuto, e' in comune
    assert p < 0.001
    z = rng.permutation(x)
    obs2, p2 = T.a1(x, z, 10, 500, rng)
    assert obs2 < obs and p2 > 0.01
    # le coppie con segni illeggibili non contano
    w = np.array([0, -1, 2, 3])
    assert T.a1(w, w, 10, 200, rng)[0] == 1                # solo la coppia 2-3


@prova
def a2_periodo():
    rng = np.random.default_rng(2)
    x = np.array(([0, 1, 2, 3, 4, 5] * 6)[:30])
    o, r, p = T.a2(x, 2000, rng)
    assert o == 1.0 and r in (6, 12) and p < 0.001
    y = rng.permutation(x)
    o2, _, p2 = T.a2(y, 2000, rng)
    assert p2 > 0.01


@prova
def b1_uguali():
    rng = np.random.default_rng(3)
    segni = np.arange(12) % 6
    tgt = segni.copy()
    obs, p = T.b1(segni, tgt, 2000, rng)
    assert obs == 12 and p < 0.01
    tgt2 = -np.arange(1, 13)
    assert T.b1(segni, tgt2, 200, rng)[0] == 0


@prova
def b2_rapporto():
    rng = np.random.default_rng(4)
    from collections import Counter
    prime = Counter({'s': 400, 'd': 300, 'a': 100})
    tutte = Counter({'s': 100, 'd': 100, 'a': 800, 'n': 1000})
    f = T.rapporti_log(prime, tutte)
    assert f('s') > 0 > f('a') and f('zz') == 0.0
    testo = list('a' * 30 + 'nn' + 'sd')
    obs, p = T.b2(list('ssdsdsds'), testo, f, 2000, rng)
    assert p < 0.01
    obs, p = T.b2(list('aaaa'), testo, f, 2000, rng)
    assert p > 0.2


@prova
def estrazione_su_righe_finte():
    """Una pagina finta nel formato delle trascrizioni: colonna di segni, righe P e glifi rari."""
    from collections import namedtuple
    import trascrizione as TR
    R = TR.Riga
    def r(pag, n, tipo, corpo):
        return R(pag, n, tipo, None, None, None, None, False, False, [], corpo)
    righe = [r('f49v', 1, 'L0', 'f'), r('f49v', 2, 'P0', 'kshor.shol.cphokchol'), r('f49v', 3, 'L0', '@140;'),
             r('f49v', 4, 'P0', 'qokchy.qokchod'), r('f49v', 5, 'L0', 'sh'), r('f49v', 6, 'P0', 'chotchy.cthey'),
             r('f49v', 7, 'L0', 'air'), r('f49v', 8, 'P0', 'sho.daiin'), r('f49v', 9, 'Lx', 'ab'),
             r('f57v', 1, 'Cc', 'o.l.d.r.@169;v.t.daiin.o.l'), r('f57v', 2, 'Cc', 'otaiin.chedy')]
    pagine, (prime, tutte) = CD.da_righe(righe, 'ZL')
    p = pagine[0]
    assert p.colonna == ['f', 'Z140z', 'sh']             # 'air' e' una parola: saltata; Lx non e' colonna
    assert p.riga_dopo == [0, 1, 2] and p.riga_prima == [None, 0, 1]
    assert p.righe_prime == ['k', 'q', 'ch', 'sh']
    assert p.n_voci == 4 and p.n_righe == 4
    assert pagine[3].colonna == ['o', 'l', 'd', 'r', 't', 'o', 'l']      # '@169;v' ha due unita': saltata
    assert prime['k'] == 0                                # le pagine delle colonne non stanno nel riferimento


@prova
def mondi_di_controllo_forma():
    for m in C.MONDI:
        pagine, (prime, tutte) = C.mondo(m, 1)
        assert [p.nome for p in pagine] == ['f49v', 'f66r', 'f76r', 'f57v']
        assert [len(p.colonna) for p in pagine] == [26, 33, 9, 64]
        assert sum(prime.values()) == 3000
        pagine2, _ = C.mondo(m, 1)
        assert [p.colonna for p in pagine] == [p.colonna for p in pagine2]      # deterministico


@prova
def batteria_gira():
    pagine, rif = C.mondo('A', 7)
    ris = T.batteria(pagine, rif, 500, 1)
    assert len(ris) == T.N_TEST
    assert ris['A2 f57v']['p'] is not None


@prova
def mondi_n4_su_righe_finte():
    """I mondi N4 su un "manoscritto" finto fatto di latino (nessuna riga vera): forma giusta e deterministici."""
    import trascrizione as TR
    rng = np.random.default_rng(9)
    R = TR.Riga
    righe = []
    for k in range(40):
        pag = 'f%dr' % (100 + k)
        lingua = 'A' if k < 20 else 'B'
        for n in range(30):
            a = int(rng.integers(0, 1000))
            corpo = '.'.join(C.parole_latine()[a:a + 7])
            righe.append(R(pag, n + 1, 'P0', 'H', lingua, '1', 'A', False, False, [], corpo))
    indice = C.indice_pagine(righe, 'GC')
    assert len(indice) == 40 and indice[0]['lingua'] == 'A' and len(indice[0]['righe']) == 30
    rif = C.riferimento_fondo(rng, 200)
    for m in C.MONDI_MS:
        pagine, _ = C.mondo_manoscritto(indice, m, 3, rif)
        assert [p.nome for p in pagine] == ['f49v', 'f66r', 'f76r']
        assert [len(p.colonna) for p in pagine] == [26, 33, 9]
        assert [len(p.righe_prime) for p in pagine] == [26, 32, 47]
        pagine2, _ = C.mondo_manoscritto(indice, m, 3, rif)
        assert [p.colonna for p in pagine] == [p.colonna for p in pagine2]
        ris = T.batteria(pagine, rif, 300, 1)                       # senza anello: i test dell'anello sono "troppo poco"
        assert ris['A2 f57v']['p'] is None and ris['A1 f49v-f57v']['p'] is None


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'tempi':
        for m in C.MONDI:
            t = time.time()
            pagine, rif = C.mondo(m, 1)
            ris = T.batteria(pagine, rif, 10000, 1)
            print(m, '%.1f s' % (time.time() - t), T.lettura(ris), {k: (None if v['p'] is None else round(v['p'], 4)) for k, v in ris.items()})
        return
    for f in PROVE:
        t = time.time()
        f()
        print('ok  %s (%.1f s)' % (f.__name__, time.time() - t), flush=True)
    print('%d prove riuscite' % len(PROVE))


if __name__ == '__main__':
    main()
