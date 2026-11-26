# -*- coding: utf-8 -*-
"""IA44: prove del codice (solo su dati finti e su libri di controllo; il manoscritto non si legge mai qui).

    PYTHONHASHSEED=0 dati/cache/.venv_lm/Scripts/python esperimenti/schemi_prove.py

Ogni prova stampa OK o ferma il programma con un errore.
"""
import itertools
import os
import random
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
os.environ['SENZA_VOYNICH44'] = '1'
import schemi_dati as D          # noqa: E402
import schemi_erbario as E       # noqa: E402
import schemi_controlli as C     # noqa: E402
import schemi_tavole as TV       # noqa: E402
import schemi_zodiaco as Z       # noqa: E402


def ok(nome):
    print('OK  ' + nome, flush=True)


def lev1(a, b):
    """Distanza di Levenshtein <= 1, a forza bruta (per controllare la costruzione con le chiavi)."""
    la, lb = len(a), len(b)
    n = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        n[i][0] = i
    for j in range(lb + 1):
        n[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            n[i][j] = min(n[i - 1][j] + 1, n[i][j - 1] + 1, n[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return n[la][lb] <= 1


def prova_tavole():
    assert TV.controlla() == [], TV.controlla()
    t = TV.tavole()
    assert len(t) == 6 and all(len(v) == 12 and all(len(x) == 30 for x in v.values()) for v in t.values())
    assert len(TV.tavole(True)) == 7 and list(TV.divisioni()) == ['elemento', 'modalita', 'pianeta']
    d = TV.divisioni()
    for nome, cl in d.items():
        assert len(cl) == 12, nome
    assert [d['elemento'][i] for i in (0, 4, 8)] == [0, 0, 0]          # fuoco: Ariete, Leone, Sagittario
    ok('tavole: genere e luce dividono i 30 gradi; 12 segni per divisione')


def prova_layout():
    for tr in ('ZL', 'IT'):
        lay = D.layout_erbario(tr)
        assert all(p['parole'] is None for u in lay.values() for p in u)
        z = D.layout_zodiaco(tr)
        assert all(v['etichette'] is None and v['altro'] is None for v in z.values())
        assert len(z) == 10
    ok('layout: nessuna parola del manoscritto, 10 segni')


def prova_varianti():
    rnd = random.Random(1)
    parole = {''.join(rnd.choice('aoiedyqk') for _ in range(rnd.randint(2, 6))) for _ in range(250)}
    voc = sorted(parole)
    A = E.adiacenza_varianti(voc)
    for i, j in itertools.combinations(range(len(voc)), 2):
        assert A[i, j] == lev1(voc[i], voc[j]), (voc[i], voc[j])
        assert A[i, j] == A[j, i]
        assert C.una_lettera(voc[i], voc[j]) == A[i, j]
    ok('varianti a una lettera: chiavi = confronto a forza bruta su %d parole' % len(voc))


SCHEMA = ['qazen', 'mubotir', 'zhelvok', 'ydrang']     # parole di schema: non varianti a una lettera l'una dell'altra


def pagine_con_schema(N=60, quote=(0.4, 0.3, 0.2, 0.1), seme=3, extra=0):
    """Pagine finte: parole 'w..' a caso e, in ogni pagina, UNA delle 4 parole di schema."""
    rnd = random.Random(seme)
    voc = ['w%d' % i for i in range(300)]
    pesi = [1 / (i + 1) for i in range(300)]
    pagine, vere = [], []
    for p in range(N):
        ps = rnd.choices(voc, weights=pesi, k=70)
        c = rnd.choices(range(4), weights=quote)[0]
        ps[rnd.randrange(70)] = SCHEMA[c]
        pagine.append(ps)
        vere.append(c)
    return pagine, vere


def prova_ricerca():
    pagine, _ = pagine_con_schema()
    strati = [i // 15 for i in range(len(pagine))]
    U = E.Unita(pagine, strati)
    o1, g1 = U.osservato()
    o2, g2 = U.osservato()
    assert np.array_equal(o1, o2) and g1 == g2                              # deterministica
    j = 4 * E.VARIANTI.index((4, 'una_volta', 'ovunque'))          # modo 'quota': 4 statistiche per variante, le prime due sono (quota, z) del modo 'quota'
    assert o1[j] == 1.0 and sorted(U.voc[i] for i in g1[j // 2]) == sorted(SCHEMA), (o1[j], [U.voc[i] for i in g1[j // 2]])
    assert o1[j + 2] == 1.0 and sorted(U.voc[i] for i in g1[j // 2 + 1]) == sorted(SCHEMA)     # e anche il modo 'esclusione'
    # l'ordine delle pagine non conta
    ordine = list(range(len(pagine)))
    random.Random(5).shuffle(ordine)
    U2 = E.Unita([pagine[i] for i in ordine], [strati[i] for i in ordine])
    assert np.array_equal(U2.osservato()[0], o1)
    ok('ricerca: ritrova le 4 parole di schema (quota 1,00), deterministica, indifferente all\'ordine delle pagine')
    return U


def prova_nulli(U):
    # nullo 'tok': stesse lunghezze, stessi insiemi di parole dentro ogni gruppo
    rnd = np.random.RandomState(0)
    tok = E.rimescola_token(U.token, U.strati, rnd)
    assert [len(a) for a in tok] == [len(a) for a in U.token]
    for s in set(U.strati):
        pp = [p for p, x in enumerate(U.strati) if x == s]
        assert sorted(np.concatenate([U.token[p] for p in pp])) == sorted(np.concatenate([tok[p] for p in pp]))
    # nullo 'col': ogni colonna (parola) ha lo stesso insieme di valori dentro ogni gruppo
    rng = np.random.default_rng(0)
    C2 = E.rimescola_colonne(U.C, U.strati, rng)
    for s in set(U.strati):
        pp = [p for p, x in enumerate(U.strati) if x == s]
        for r in range(3):
            assert np.array_equal(np.sort(U.C[r][pp], axis=0), np.sort(C2[r][pp], axis=0))
    assert not np.array_equal(U.C, C2)
    # i due nulli distruggono lo schema
    nt = U.nullo('tok', 1)
    nc = U.nullo('col', 1)
    j = 4 * E.VARIANTI.index((4, 'una_volta', 'ovunque'))
    assert nt[j] < 0.9 and nc[j] < 0.9, (nt[j], nc[j])
    ok('nulli: lunghezze e insiemi per gruppo conservati; lo schema piantato sparisce (%.2f e %.2f)' % (nt[j], nc[j]))


def prova_nullo_uniforme():
    """Su testo senza schema i p devono essere circa uniformi: con 40 libri finti e K=49 al piu' 6 sotto 0,05."""
    lay = D.layout_erbario('ZL')['A']
    p = []
    for s in range(40):
        pag = C.latino_cifrato(lay, 100 + s, riempitivo=0.5)
        r = C.prova_unita(pag, D.strati(lay), 49, s + 1)
        p.append(r['p'])
    sotto = sum(x <= 0.05 for x in p)
    assert sotto <= 7, sotto
    ok('negativi (latino cifrato, metà riempitivo, unita A): %d su 40 con p <= 0,05 (attesi circa 2)' % sotto)


def prova_piantato():
    lay = D.layout_erbario('ZL')
    for u in ('A', 'B'):
        ctrl = {}
        pag = C.latino_cifrato(lay[u], 5, schema='Q4', controllo=ctrl)
        assert [len(ps) for ps in pag] == [p['n'] for p in lay[u]]                 # impaginato come l'erbario del Voynich
        parole = ctrl['piantate']['qualita']
        assert len(parole) == 4
        for ps in pag:
            assert sum(w in parole for w in ps) == 1                              # una e una sola per pagina
        # le parole riservate non compaiono altrove: gia' garantito dal conto qui sopra (una per pagina)
        # le parole piantate non sono varianti l'una dell'altra
        for a, b in itertools.combinations(parole, 2):
            assert not C.una_lettera(a, b)
    ctrl = {}
    pag = C.latino_cifrato(lay['A'], 5, schema='CS', controllo=ctrl)
    gr = [w for ws in ctrl['piantate'].values() for w in ws]
    for ps in pag:
        n = len(ps)
        for ws in ctrl['piantate'].values():
            pos = [j for j, w in enumerate(ps) if w in ws]
            assert len(pos) == 1 and pos[0] < max(n // 3, 1)                      # nel primo terzo
    assert len(gr) == 4
    ok('piantato: pagine con la lunghezza dell\'erbario, una parola di schema per pagina (anche nel primo terzo per CS)')


def prova_positivo_e_negativo():
    r = C.lavoro(dict(ric='erb', tipo='pos', schema='QG', indice=1, unita='A', K=99))
    assert r['p'] <= 0.02 and r['recupero'], r['p']
    r = C.lavoro(dict(ric='erb', tipo='neg', famiglia='v21', indice=3, unita='A', K=99))
    assert r['p'] > 0.02, r['p']
    ok('un positivo QG visto (p %.3f) e un v21 non visto' % C.lavoro(dict(ric='erb', tipo='pos', schema='QG', indice=1, unita='A', K=99))['p'])


def prova_zodiaco():
    lay = D.layout_zodiaco('ZL')
    et, al = Z.sintetico(lay, 1, 'iid')
    # il finto ha la layout del manoscritto
    for e, a, nome in zip(et, al, D.ORDINE_SEGNI):
        assert len(e) == lay[nome]['n_etichette'] and [len(r) for r in e] == lay[nome]['n_parole_et'] and len(a) == lay[nome]['n_altro']
    # (b): il nullo esatto: p uniforme su sottoinsiemi a caso (enumerazione)
    tab = Z.tabelle_b()
    for nome, mlp in tab.items():
        pop = np.array([bin(m).count('1') for m in range(1024)])
        for s in range(2, 7):
            v = np.unique(np.round(10.0 ** -mlp[pop == s], 12))
            assert v.min() > 0 and abs(np.mean(10.0 ** -mlp[pop == s] <= 0.05) - 0) <= 0.2
    # (c): le classi della tavola, tutte con proporzione fra 0 e 1
    G = Z.Gradi([[['x']] * len(e) for e in et])
    assert G.Mx.shape[0] == len(G.conf) == 6 * 2 * 30
    # (b) planted vs finto
    a1, b1 = [[w for r in e for w in r] for e in et], [[w for r in e for w in r] + x for e, x in zip(et, al)]
    p0 = Z.ricerca_b(a1, b1, k=299, seme=1)['p']
    et2, al2 = Z.pianta_segni(et, al, 2, 'elemento', 20, 0.9)
    p1 = Z.ricerca_b([[w for r in e for w in r] for e in et2], [[w for r in e for w in r] + x for e, x in zip(et2, al2)], k=299, seme=1)['p']
    assert p1 < 0.01 < p0, (p0, p1)
    # (c) planted vs finto, e solo le tavole ammesse contano
    p0c = Z.ricerca_c(et, k=299, seme=1)['p']
    et3, _ = Z.pianta_gradi(et, 3, list(TV.tavole())[0], 0.5)
    p1c = Z.ricerca_c(et3, k=299, seme=1)['p']
    assert p1c < 0.01 < p0c, (p0c, p1c)
    rr = Z.ricerca_c(et3, k=299, seme=1, solo=[list(TV.tavole())[3]])
    assert 'L2' in rr['nome']
    ok('zodiaco: layout rispettata; (b) piantato p=%.3f contro finto p=%.2f; (c) piantato p=%.3f contro finto p=%.2f' % (p1, p0, p1c, p0c))


def prova_porta_chiusa():
    import ia44_schemi as I
    I.TESTO = ''
    try:
        I.testi_di('ZL')
    except SystemExit:
        ok('fase V: con SENZA_VOYNICH44=1 e senza testi di prova il manoscritto non si legge')
        return
    raise AssertionError('il manoscritto e\' stato letto')


def prova_cancello():
    """Il cancello su righe finte: ammette e non ammette come scritto."""
    import ia44_schemi as I
    rows = []
    for u in ('A', 'B'):
        for fam, indici in I.NEG_ERB:
            for i in indici:
                rows.append(dict(ric='erb', tipo='neg', famiglia=fam, indice=i, unita=u, p=0.5))
        for schema, n in I.POS_ERB:
            for i in range(n):
                rows.append(dict(ric='erb', tipo='pos', schema=schema, indice=i, unita=u, p=0.003 if (u == 'A' or i < 10) else 0.5, recupero=True))
    for fam, n in I.NEG_ZOD:
        for i in range(n):
            rows.append(dict(ric='zod', tipo='neg', famiglia=fam, indice=i, p_b=0.5, p_c=0.5))
    for dv, npc, quota, n in I.POS_B:
        for i in range(n):
            rows.append(dict(ric='zodb', tipo='pos', divisione=dv, npc=npc, quota=quota, indice=i, p=0.001 if dv != 'pianeta' else 0.2))
    for tav, f, n, ps in I.POS_C:
        for i in range(n):
            rows.append(dict(ric='zodc', tipo='pos', tavola=tav, f=f, per_segno=ps, indice=i, p=0.001))
    g = I.cancello(rows)
    assert g['erbario']['A']['ammessa'] and not g['erbario']['B']['ammessa']
    assert g['b']['ammesse'] == ['elemento', 'modalita']
    assert len(g['c']['ammesse']) == 6
    # falsi allarmi sopra il 5% chiudono tutto
    for r in rows:
        if r['ric'] == 'zod' and r['indice'] < 10:
            r['p_b'] = 0.001
    g = I.cancello(rows)
    assert g['b']['ammesse'] == [] and len(g['c']['ammesse']) == 6
    ok('cancello: unita\' A ammessa e B no, divisioni (b) senza `pianeta`, falsi allarmi sopra il 5% chiudono (b)')


if __name__ == '__main__':
    prova_tavole()
    prova_layout()
    prova_varianti()
    U = prova_ricerca()
    prova_nulli(U)
    prova_piantato()
    prova_positivo_e_negativo()
    prova_zodiaco()
    prova_porta_chiusa()
    prova_cancello()
    prova_nullo_uniforme()
    print('TUTTE LE PROVE OK')
