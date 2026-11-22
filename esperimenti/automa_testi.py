# -*- coding: utf-8 -*-
"""Testi, generatori sintetici e misure di costo per ia31 (modulo di supporto, non e' un esperimento).

Un testo e' un dict(pagine=OrderedDict pagina -> righe [(inizio_paragrafo, [parola, ...])], fold=dict pagina -> piega 0-4), con la parola come
tupla di segni (glifi EVA fusi per il Voynich, lettere per le lingue, segni per i cifrari). Le pieghe sono quelle di ia07 (per foglio) per tutti
i testi messi nell'impaginazione del Voynich (lingue, cifrari, libri degli imitatori, controlli); per Naibbe e Timm e Schinner (pagine proprie) sono
quelle di ia01 (`sintassi_testi.pieghe`, ricopiate qui).

Nomi dei testi:
  vero                      il libro vero (nelle prove: il latino messo nella disposizione del Voynich)
  lingua_<k>                un testo di Gaskell e Bowern (le otto lingue di ia14) nell'impaginazione del Voynich
  cif_<cod>_<val>_i<n>      un procedimento di ia14 (cifrari_procedimenti.genera), istanza n
  nat_naibbe, nat_ts        Naibbe e Timm e Schinner (generatori esterni gia' in cache)
  lib_V21_<k>               libro v21 senza messaggio (chiave k di ia01);  lib_M1_<i>, lib_E2_<i>, lib_W1_<i>: libri di ia20, ia22, ia24 (dalla cache)
  neg_N1, neg_N2            controllo negativo: i glifi di ogni parola rimescolati (N1: una volta per parola-tipo; N2: a ogni occorrenza)
  sint_L<K0>_<s>            controllo positivo: lessico generato da un automa libero noto con K0 stati
  sint_C<K0>_<s>            controllo positivo: lessico generato da una grammatica a K0 caselle nota
  sint_vero, sint_gap, sint_neutro   controllo dello scarto: parole di un automa noto; le stesse con rumore sul secondo e terzo glifo; un campione fresco senza rumore

In SOLO_CONTROLLI i libri v21, M1, E2, W1 non esistono: al loro posto catene di Markov di caratteri (ordine 2, 1, 3, 2) del libro di prova, solo per far girare il percorso.
Nessun file letto qui contiene il Voynich, tranne `vero` e i libri quando non si e' in SOLO_CONTROLLI. Solo numeri escono dai lavori.
"""
import math
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import automa_hmm as H  # noqa: E402
import cifrari_procedimenti as CP  # noqa: E402

VERSIONE = 'automa-testi-1'
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
CACHE = os.path.join(QUI, '..', 'dati', 'cache')
NF = 5

# le otto lingue di ia14 (testi di Gaskell e Bowern, scelti prima in ia14)
LINGUE_CHIAVI = OrderedDict([
    ('latino', "Historical - Latin - Technical - Pliny's Natural History.txt"),
    ('latino_nt', 'Historical - Latin - Literary - NT (Vulgate).txt'),
    ('italiano', 'Historical - Italian - Literary - NT - Diodati.txt'),
    ('inglese', 'Historical - English - Literary - NT (KJV).txt'),
    ('francese', 'Historical - French - Literary - NT - Martin.txt'),
    ('tedesco', 'Historical - German - Literary - NT - Luther.txt'),
    ('spagnolo', 'Historical - Spanish - Literary - NT - Sagradas Escrituras.txt'),
    ('maori', 'Modern - Maori - Literary - NT.txt'),
])
CHIAVI_V21 = tuple(range(13, 23))
# cache dei libri degli imitatori (come ia20.percorso_libro, ia22.percorso_libro, ia24.percorso_libro; si verifica nella prova di unita')
PERCORSI_LIBRI = OrderedDict([('M1', ('ia20', 'ia20_libro_M1_%d.txt')), ('E2', ('ia22', 'ia22_libro_E2_%d.txt')), ('W1', ('ia24', 'ia24_libro_W1_%d.txt'))])

_C = {}


def seme_di(*parti):
    return zlib.crc32('|'.join(str(p) for p in ('ia31',) + parti).encode('utf-8')) % (1 << 31)


def contesto():
    import ia07_voynich_neurale as I7
    return I7.contesto_A()


def pieghe_proprie(nomi, seme=3961):
    """Come sintassi_testi.pieghe (ia01): i nomi ordinati, mescolati con random.Random(3961), a giro in 5 pieghe."""
    ordine = sorted(nomi)
    random.Random(seme).shuffle(ordine)
    return {p: i % NF for i, p in enumerate(ordine)}


def layout():
    if 'layout' not in _C:
        _C['layout'] = CP.layout_da_pagine(contesto()['vere'])
    return _C['layout']


def solo_pagine_vere(pag):
    c = contesto()
    return OrderedDict((p, pag[p]) for p in c['vere'] if p in pag)


# ---------------------------------------------------------------- generatori sintetici

def generatore(tipo, K0, seme, V=24):
    """Un automa noto per i controlli. tipo 'L' (libero) o 'C' (caselle). Glifi sintetici 'g0'...'g(V-1)'. Parole di 3-7 glifi circa."""
    rng = np.random.default_rng(seme_di('gen', tipo, K0, seme))
    al = H.Alfabeto(['g%d' % i for i in range(V)])
    NS = al.NS
    B = np.zeros((K0, NS))
    A = np.zeros((K0, K0))
    pi = np.zeros(K0)
    if tipo == 'L':
        ordine = [int(x) for x in rng.permutation(K0)]
        iniziali = set(ordine[:max(1, K0 // 2)])                                 # stati di partenza: non possono finire la parola (niente parole vuote, la distribuzione resta esatta)
        finali = set(ordine[max(1, K0 // 2):][:max(1, K0 // 3)])                 # un terzo degli stati (almeno uno) finisce la parola con probabilita' alta
        for k in range(K0):
            glifi = rng.choice(V, size=3, replace=False)
            w = rng.dirichlet([0.7] * 3)
            pend = 0.0 if k in iniziali else (0.5 if k in finali else 0.10)
            B[k, glifi] = (1 - pend) * w
            B[k, al.FINE] = pend
            succ = rng.choice(K0, size=min(3, K0), replace=False)
            A[k, succ] = rng.dirichlet([0.8] * len(succ))
        pi[sorted(iniziali)] = rng.dirichlet([0.8] * len(iniziali))
    else:
        per = max(2, V // K0)
        for k in range(K0):
            base = (k * per) % V
            glifi = [(base + j) % V for j in range(min(per, 4))]
            w = rng.dirichlet([1.0] * len(glifi))
            pend = 0.0 if k < K0 - 2 else 0.45
            B[k, glifi] = (1 - pend) * w
            B[k, al.FINE] = pend
            A[k, k] += 0.25
            if k + 1 < K0:
                A[k, k + 1] += 0.55
            if k + 2 < K0:
                A[k, k + 2] += 0.20
            if A[k].sum() == 0:
                A[k, k] = 1.0
        pi[0], pi[min(1, K0 - 1)] = 0.8, 0.2
        pi = pi / pi.sum()
    # un po' di probabilita' su tutto (2% sulle emissioni, 1% sulle transizioni libere): nessuna parola e' impossibile, cosi' il costo esatto di una parola con rumore e' finito
    B[:, :V] += 0.02 / V
    B[:, al.RARO] = 0.0
    B = H._normalizza(B)
    if tipo == 'L':
        A = H._normalizza(A + 0.01 / K0)
    else:
        A = H._normalizza(A)
    return H.Automa(K0, al, 'libero' if tipo == 'L' else 'caselle', pi / pi.sum(), A, B)


def campiona_parole(a, n, seme, massimo=30):
    """n parole (tuple di nomi di glifo) dall'automa `a`, con cumulate precalcolate."""
    rng = np.random.default_rng(seme)
    cpi = np.cumsum(a.pi)
    cA = np.cumsum(a.A, axis=1)
    pb = a.B.copy()
    pb[:, a.al.RARO] = 0.0
    cB = np.cumsum(pb / pb.sum(1, keepdims=True), axis=1)
    out = []
    while len(out) < n:
        s = min(int(np.searchsorted(cpi, rng.random() * cpi[-1])), a.K - 1)
        w = []
        while len(w) <= massimo:
            x = min(int(np.searchsorted(cB[s], rng.random() * cB[s][-1])), a.al.NS - 1)
            if x == a.al.FINE:
                break
            w.append(x)
            s = min(int(np.searchsorted(cA[s], rng.random() * cA[s][-1])), a.K - 1)
        else:
            continue
        if w:
            out.append(tuple(a.al.glifi[x] for x in w))
    return out


def rumore_secondo_terzo(parole, p, seme, glifi):
    """Con probabilita' p (parole di almeno 3 glifi) il secondo e il terzo glifo si sostituiscono con glifi a caso (uniformi sull'alfabeto)."""
    rng = random.Random(seme)
    out = []
    for w in parole:
        if len(w) >= 3 and rng.random() < p:
            w = (w[0], rng.choice(glifi), rng.choice(glifi)) + tuple(w[3:])
        out.append(w)
    return out


# ---------------------------------------------------------------- catalogo

def descrizione_testi(istanze=2, n_lib=10):
    """Tutti i nomi dei testi in ordine di presentazione, con la classe."""
    T = OrderedDict()
    T['vero'] = 'vero'
    for k in LINGUE_CHIAVI:
        T['lingua_' + k] = 'lingua'
    for cod, p in CP.PROCEDIMENTI.items():
        for v in p['valori']:
            for i in range(1, istanze + 1):
                T['cif_' + CP.nome_istanza(cod, v, i)] = 'cifrario'
    T['nat_naibbe'] = 'nativo'
    T['nat_ts'] = 'nativo'
    for k in CHIAVI_V21:
        T['lib_V21_%d' % k] = 'v21'
    for s in PERCORSI_LIBRI:
        for i in range(1, n_lib + 1):
            T['lib_%s_%d' % (s, i)] = 'imit_' + s
    return T


def testo(nome):
    """Un testo (vedi l'inizio del file). Solo `vero` si tiene in memoria; gli altri si rifanno a ogni chiamata (un solo testo alla volta)."""
    if nome == 'vero' and 'vero' in _C:
        return _C['vero']
    c = contesto()
    if nome == 'vero':
        t = dict(pagine=c['vere'], fold=dict(c['fold']))
        _C['vero'] = t
        return t
    if nome.startswith('lingua_'):
        t = dict(pagine=CP.testo_lingua_in_layout(LINGUE_CHIAVI[nome[7:]], layout(), 0), fold=c['fold'])
    elif nome.startswith('cif_'):
        cod, val = nome[4:].split('_')[0], nome[4:].split('_')[1]
        ist = int(nome.rsplit('_i', 1)[1])
        valore = [x for x in CP.PROCEDIMENTI[cod]['valori'] if str(x).replace('.', 'p') == val][0]
        t = dict(pagine=CP.genera(cod, valore, ist, layout())[0], fold=c['fold'])
    elif nome in ('nat_naibbe', 'nat_ts'):
        import e3c95_imparabilita as e95
        import famiglie_testi as FT
        pag = FT._da_blocchi(e95.naibbe(), 'N') if nome == 'nat_naibbe' else FT._da_blocchi(e95.timm_schinner(), 'T')
        t = dict(pagine=pag, fold=pieghe_proprie(pag))
    elif nome.startswith('lib_'):
        t = dict(pagine=solo_pagine_vere(_libro(nome)), fold=c['fold'])
    elif nome in ('neg_N1', 'neg_N2'):
        t = dict(pagine=_rimescola(c['vere'], nome), fold=dict(c['fold']))
    elif nome.startswith('sint_'):
        t = _sintetico(nome)
    else:
        raise KeyError(nome)
    return t


def _libro(nome):
    import ia07_voynich_neurale as I7
    _, sigla, k = nome.split('_')
    k = int(k)
    if SOLO_CONTROLLI:
        import ia01_giudice_neurale as G
        ordine = dict(V21=2, M1=1, E2=3, W1=2)[sigla]
        return G.markov(contesto()['vere'], ordine, seme_di('prova', sigla, k))
    if sigla == 'V21':
        return I7.libro_riferimento_A('b', k)
    cartella, modello = PERCORSI_LIBRI[sigla]
    p = os.path.join(CACHE, cartella, 'libri', modello % k)
    if not os.path.exists(p):
        raise RuntimeError('manca il libro %s: va fatto con %s' % (p, cartella))
    return I7.libro_A_da_righe(I7.leggi_file(p))


def _rimescola(pagine, nome):
    out = OrderedDict()
    perm = {}
    rnd = random.Random(seme_di(nome))
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            nw = []
            for w in ws:
                if nome == 'neg_N1':
                    if w not in perm:
                        x = list(w)
                        random.Random(seme_di('N1', ''.join(w))).shuffle(x)
                        perm[w] = tuple(x)
                    nw.append(perm[w])
                else:
                    x = list(w)
                    rnd.shuffle(x)
                    nw.append(tuple(x))
            nr.append((ini, nw))
        out[p] = nr
    return out


def _sintetico(nome):
    c = contesto()
    lay = layout()
    N = sum(n for _, rows in lay for _, n in rows)
    parti = nome.split('_')
    if parti[1] in ('vero', 'gap', 'neutro'):
        a = generatore('L', 8, 3)
        seme = dict(vero=1, gap=2, neutro=3)[parti[1]]
        parole = campiona_parole(a, N, seme_di('camp', nome, seme))
        if parti[1] == 'gap':
            parole = rumore_secondo_terzo(parole, 0.5, seme_di('rumore'), a.al.glifi)
    else:
        tipo, K0, s = parti[1][0], int(parti[1][1:]), int(parti[2])
        a = generatore(tipo, K0, s)
        parole = campiona_parole(a, N, seme_di('camp', nome))
    return dict(pagine=CP.impagina(lay, parole), fold=dict(c['fold']))


def automa_sintetico(nome):
    """L'automa che ha generato un testo sintetico (per misurare il costo esatto)."""
    parti = nome.split('_')
    if parti[1] in ('vero', 'gap', 'neutro'):
        return generatore('L', 8, 3)
    return generatore(parti[1][0], int(parti[1][1:]), int(parti[2]))


# ---------------------------------------------------------------- insiemi di parole di una piega

def conti_piega(pagine, fold, f):
    """(Counter dell'addestramento = pagine delle altre pieghe, Counter delle pagine della piega f)."""
    tr, te = Counter(), Counter()
    for p, rows in pagine.items():
        if p not in fold:
            continue
        dest = te if fold[p] == f else tr
        for _, ws in rows:
            for w in ws:
                dest[w] += 1
    return tr, te


def alfabeto_di(pagine):
    return H.Alfabeto(sorted({g for rows in pagine.values() for _, ws in rows for w in ws for g in w}))


def forma_trigrammi(tr):
    import rifarlo_ritocchi as R
    return R.Forma(tr)


def parti_trigrammi(forma, conti):
    """Come parti_gruppi ma con il modello a trigrammi di ia20 (Forma): ([primo, secondo, terzo, dal quarto, fine] in bit, glifi, parole)."""
    out = np.zeros(5)
    gl = n = 0
    for w, k in conti.items():
        a = b = forma.q
        bp = []
        for x in [forma.idx.get(g, forma.q - 1) for g in w] + [forma.q]:
            bp.append(-float(forma.l3[a, b, x]))
            a, b = b, x
        L = len(w)
        for l, v in enumerate(bp):
            out[4 if l == L else min(l, 3)] += k * v
        gl += k * L
        n += k
    return out, gl, n


def parti_gruppi(a, gruppi):
    """([primo, secondo, terzo, dal quarto, fine] in bit sommati con i pesi, glifi pesati, parole pesate) sotto l'automa `a`."""
    parti = np.zeros(5)
    gl = n = 0.0
    for L, (S, w, ix) in gruppi.items():
        b = a.costi_posizione(S)
        m = L - 1
        parti[0] += float((w * b[:, 0]).sum())
        if m >= 2:
            parti[1] += float((w * b[:, 1]).sum())
        if m >= 3:
            parti[2] += float((w * b[:, 2]).sum())
        if m >= 4:
            parti[3] += float((w * b[:, 3:m].sum(1)).sum())
        parti[4] += float((w * b[:, m]).sum())
        gl += m * float(w.sum())
        n += float(w.sum())
    return parti, gl, n


def costi_per_parola(a, conti, alfabeto):
    """Bit totali per glifo di ogni parola distinta di `conti`: lista di (costo per glifo, peso)."""
    parole = list(conti)
    gr = H.gruppi_da_parole(parole, [conti[w] for w in parole], alfabeto)
    out = []
    for L, (S, w, ix) in gr.items():
        b = a.costi_posizione(S).sum(1) / (L - 1)
        out += list(zip(b.tolist(), w.tolist()))
    return out
