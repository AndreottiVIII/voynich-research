# -*- coding: utf-8 -*-
"""Misure dell'"eco" per ia15 (modulo di supporto, non e' un esperimento): da dove viene la ripetizione di parole sulla pagina.

Che cosa c'e' qui, in parole semplici:
- `grafo_vicini`: per ogni coppia di parole (tipi) a una modifica di distanza (un glifo cambiato, aggiunto o tolto), dice DOVE sta
  la modifica: inizio, fine o dentro la parola. Si trova con indici di "parola con un buco", senza confrontare tutte le coppie; la
  prova confronta il risultato con `sintassi_modelli.dist1` (la distanza usata in ia09).
- `stat_pagina`: per ogni parola della pagina e per ogni riga sopra (e le parole prima nella stessa riga), quante parole sono
  uguali, a una modifica (divise per posto della modifica), e quante sono in tutto. La stessa conta si fa su una pagina "di
  riferimento" (una pagina a caso della stessa sezione, e una di un'altra sezione), con la stessa geometria di righe: serve a
  togliere la ripetizione "generica". Le righe sopra si raggruppano per distanza (stessa riga, 1, 2-3, 4-7, 8 o piu' righe) e,
  per l'eco fra paragrafi, per "stesso paragrafo / paragrafo diverso".
- `somme_bande`: somme per banda (si rifanno veloci anche con i confini dei paragrafi spostati: serve al controllo "paragrafi
  spostati").
- `relazioni_pagine`: tasso di parole uguali / a una modifica fra coppie di pagine intere, per classe di relazione.
- generatori sintetici (controlli positivi), costruiti su un testo qualunque dato: `genera_argomento` (le parole tornano perche'
  la pagina, il paragrafo o una stretta di pagine "parla" di un tema: nessuna copia) e `genera_copia_eco` (ogni parola copia e
  ritocca una parola scritta poco prima: nessun tema).
Nessun risultato e' scritto qui.
"""
import random
from collections import Counter, OrderedDict, defaultdict

import numpy as np
import scipy.sparse as sps

CLASSI = ('I', 'F', 'M')                       # posto della modifica: inizio, fine, dentro la parola
NB = 5                                         # bande di distanza: stessa riga, 1 riga sopra, 2-3, 4-7, 8 o piu'
NOMI_BANDA = ['D0', 'D1', 'D2', 'D4', 'D8']
QUANT = ['n', 'x', 'vI', 'vF', 'vM']           # quantita' per banda: parole fonte, uguali, a una modifica (per posto)


# ---------------------------------------------------------------- il grafo delle parole a una modifica

def grafo_vicini(C):
    """Tre matrici sparse simmetriche (tipi x tipi), una per posto della modifica (I inizio, F fine, M dentro). Il valore e' il peso
    della coppia in quel posto: una coppia vale 1 in tutto. Una sostituzione al posto k di una parola lunga L vale tutta in I (k = 0),
    F (k = L - 1) o M; se L = 1 (parola di un glifo) mezzo in I e mezzo in F. Un glifo in piu' (o in meno) puo' stare in piu' posti
    se i glifi uguali sono di fila (aa -> a): il peso si divide fra i posti possibili. Niente parola vuota (come ia09)."""
    tipi, tid = C.tipi, C.tid
    nt = len(tipi)
    coppie = {}                                 # (a, b) con a < b -> [wI, wF, wM]

    def aggiungi(a, b, k, L, peso=1.0):
        if a > b:
            a, b = b, a
        v = coppie.setdefault((a, b), [0.0, 0.0, 0.0])
        if L == 1:
            v[0] += peso / 2
            v[1] += peso / 2
        elif k == 0:
            v[0] += peso
        elif k == L - 1:
            v[1] += peso
        else:
            v[2] += peso
    # sostituzioni: parole di uguale lunghezza che differiscono in un solo posto
    gruppi = defaultdict(list)
    for t, w in enumerate(tipi):
        for i in range(len(w)):
            gruppi[(w[:i], w[i + 1:])].append(t)
    for (pre, suf), lst in gruppi.items():
        if len(lst) < 2:
            continue
        i, L = len(pre), len(pre) + 1 + len(suf)
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                aggiungi(lst[x], lst[y], i, L)
    # un glifo in piu' / in meno
    posti = defaultdict(list)                   # (corta, lunga) -> posti k della lunga
    for t, w in enumerate(tipi):
        if len(w) < 2:
            continue
        for k in range(len(w)):
            u = tid.get(w[:k] + w[k + 1:])
            if u is not None:
                posti[(u, t)].append(k)
    for (u, t), ks in posti.items():
        L = len(tipi[t])
        for k in ks:
            aggiungi(u, t, k, L, 1.0 / len(ks))
    r, c = [], []
    pesi = [[], [], []]
    for (a, b), v in coppie.items():
        for (x, y) in ((a, b), (b, a)):
            r.append(x)
            c.append(y)
            for j in range(3):
                pesi[j].append(v[j])
    r, c = np.array(r, dtype=np.int64), np.array(c, dtype=np.int64)
    return {cl: sps.csr_matrix((np.array(pesi[j]), (r, c)), shape=(nt, nt)) for j, cl in enumerate(CLASSI)}


def bucket(d):
    return 0 if d == 0 else 1 if d == 1 else 2 if d <= 3 else 3 if d <= 7 else 4


# ---------------------------------------------------------------- paragrafi

def paragrafi(P):
    """(paragrafo di ogni riga, 'e' la prima riga di un paragrafo). La prima riga della pagina apre sempre un paragrafo."""
    nl = len(P.lstart) - 1
    pid = np.zeros(nl, dtype=np.int64)
    prima = np.zeros(nl, dtype=bool)
    if nl:
        prima[0] = True
    for l in range(1, nl):
        apre = P.lstart[l] < P.lstart[l + 1] and bool(P.ini[P.lstart[l]])
        pid[l] = pid[l - 1] + (1 if apre else 0)
        prima[l] = apre
    return pid, prima


def paragrafi_spostati(pid, rnd):
    """Stesso numero di paragrafi per la pagina, ma con i confini fra righe scelti a caso (senza ripetizioni): i confini cadono altrove."""
    nl = len(pid)
    k = int(pid.max()) + 1 if nl else 0
    nuovo = np.zeros(nl, dtype=np.int64)
    prima = np.zeros(nl, dtype=bool)
    if nl:
        prima[0] = True
    if k >= 2 and nl >= k:
        for b in rnd.sample(range(1, nl), k - 1):
            prima[b] = True
        nuovo = np.cumsum(prima) - 1
    return nuovo, prima


# ---------------------------------------------------------------- le conte di una pagina

def matrici_fonte(A, Pt, Ps):
    """Per ogni parola t della pagina `Pt` e ogni riga l della pagina `Ps` (fonte; puo' essere la stessa pagina) con l <= riga di t:
    n = parole della riga l (le prime J_t se l e' la riga stessa di t, e solo quelle prima di t), x = quante uguali a t, vI/vF/vM =
    quante a una modifica da t (per posto della modifica). Restituisce un dizionario di matrici (parole x righe di Ps)."""
    T, nls = Pt.n, len(Ps.lstart) - 1
    ut, it = np.unique(Pt.tok, return_inverse=True)
    us, is_ = np.unique(Ps.tok, return_inverse=True)
    CT = np.zeros((len(us), nls))
    np.add.at(CT, (is_, Ps.L), 1.0)
    E = (ut[:, None] == us[None, :]).astype(float)
    Av = {c: A[c][ut, :][:, us].toarray() for c in CLASSI}
    LX = E @ CT
    LV = {c: Av[c] @ CT for c in CLASSI}
    Lq = Pt.L
    sopra = (np.arange(nls)[None, :] < Lq[:, None])
    out = {'n': np.tile(np.diff(Ps.lstart).astype(float), (T, 1)) * sopra, 'x': LX[it] * sopra}
    for c in CLASSI:
        out['v' + c] = LV[c][it] * sopra
    # la riga stessa: solo le prime J parole della riga omologa
    for l in range(len(Pt.lstart) - 1):
        if l >= nls:
            break
        a0, a1 = Pt.lstart[l], Pt.lstart[l + 1]
        s0, s1 = Ps.lstart[l], Ps.lstart[l + 1]
        m, nr = a1 - a0, s1 - s0
        if m == 0:
            continue
        mask = (np.arange(nr)[None, :] < np.arange(m)[:, None])
        out['n'][a0:a1, l] = mask.sum(1)
        out['x'][a0:a1, l] = ((Pt.tok[a0:a1][:, None] == Ps.tok[s0:s1][None, :]) & mask).sum(1)
        for c in CLASSI:
            out['v' + c][a0:a1, l] = (Av[c][np.ix_(it[a0:a1], is_[s0:s1])] * mask).sum(1)
    return out


def bande(Lq, ncol, pid, prima, modo_E):
    """Indice di banda di ogni coppia (parola, riga fonte): bucket di distanza + NB se la riga fonte e' di un paragrafo diverso da
    quello della parola; -1 se la riga e' dopo la parola. Con `modo_E` si escludono le prime righe di ogni paragrafo, sia come righe
    della parola sia come fonti."""
    l = np.arange(ncol)[None, :]
    d = Lq[:, None] - l
    valida = d >= 0
    b = np.where(d == 0, 0, np.where(d == 1, 1, np.where(d <= 3, 2, np.where(d <= 7, 3, 4))))
    lc = np.minimum(l, len(pid) - 1)
    fra = pid[Lq][:, None] != pid[lc]
    band = np.where(valida, b + NB * fra, -1)
    if modo_E:
        ok = valida & ~prima[Lq][:, None] & ~prima[lc]
        band = np.where(ok, band, -1)
    return band


def somme_bande(Q, band, peso_riga=None):
    """Somme per banda (2*NB bande) di ogni quantita'. `peso_riga` (T,) filtra le parole (1 = si)."""
    idx = band.ravel()
    ok = idx >= 0
    out = {}
    for q, M in Q.items():
        w = M if peso_riga is None else M * peso_riga[:, None]
        out[q] = np.bincount(idx[ok], weights=w.ravel()[ok], minlength=2 * NB)
    return out


def simile(Q):
    """Parole uguali o a una modifica = x + vI + vF + vM."""
    return Q['x'] + Q['vI'] + Q['vF'] + Q['vM']


def scegli_riferimenti(nomi, meta, nrighe, seme, nrif):
    """Per ogni pagina, `nrif` pagine di riferimento della stessa sezione e `nrif` di un'altra (a caso, mai la pagina stessa;
    si preferiscono pagine con almeno altrettante righe, perche' le bande lontane abbiano fonti)."""
    rnd = random.Random(seme)
    sez, altro = {}, {}
    for p in nomi:
        stessa = [q for q in nomi if q != p and meta[q]['sez'] == meta[p]['sez']] or [q for q in nomi if q != p]
        diversa = [q for q in nomi if meta[q]['sez'] != meta[p]['sez']] or [q for q in nomi if q != p]
        for dest, pool in ((sez, stessa), (altro, diversa)):
            grandi = [q for q in pool if nrighe[q] >= nrighe[p]] or pool
            scelte = rnd.sample(grandi, min(nrif, len(grandi)))
            while len(scelte) < nrif:
                scelte.append(rnd.choice(grandi))
            dest[p] = scelte
    return sez, altro


def stat_pagina(C, A, P, rif_sez, rif_altro, spostamenti=0, seme=0):
    """Tutte le somme di una pagina. Restituisce (dizionario di numeri da salvare, dati per il controllo dei paragrafi spostati).
    - A: bande pooled (dentro + fra paragrafi), tutte le parole, per fonte 'real', 'sez', 'altro' (riferimenti: media)
    - A4: lo stesso per le sole parole alla riga 4 o piu' (stesso gruppo di parole per vicino e lontano)
    - E: bande per paragrafo (dentro / fra) senza le prime righe dei paragrafi, per 'real' e 'sez' (solo n e simile)
    """
    pid, prima = paragrafi(P)
    Lq = P.L
    Mreal = matrici_fonte(A, P, P)
    refs = {'sez': [matrici_fonte(A, P, R) for R in rif_sez], 'altro': [matrici_fonte(A, P, R) for R in rif_altro]}
    pesi_riga = {'tutti': None, 'L4': (Lq >= 4).astype(float)}
    out = {}
    for nome, pr in pesi_riga.items():
        gruppo = {}
        for fonte, lista in (('real', [Mreal]), ('sez', refs['sez']), ('altro', refs['altro'])):
            if fonte == 'altro' and nome != 'tutti':
                continue
            acc = np.zeros((NB, len(QUANT)))
            for M in lista:
                band = bande(Lq, M['n'].shape[1], pid, prima, False)
                s = somme_bande(M, band, pr)
                for j, q in enumerate(QUANT):
                    acc[:, j] += s[q][:NB] + s[q][NB:]
            gruppo[fonte] = np.round(acc / len(lista), 3).tolist()
        out['A' if nome == 'tutti' else 'A4'] = gruppo
    E = {}
    for fonte, lista in (('real', [Mreal]), ('sez', refs['sez'])):
        acc = np.zeros((2, NB, 2))
        for M in lista:
            band = bande(Lq, M['n'].shape[1], pid, prima, True)
            s = somme_bande({'n': M['n'], 'h': simile(M)}, band)
            acc[0, :, 0] += s['n'][:NB]
            acc[0, :, 1] += s['h'][:NB]
            acc[1, :, 0] += s['n'][NB:]
            acc[1, :, 1] += s['h'][NB:]
        E[fonte] = np.round(acc / len(lista), 3).tolist()
    out['E'] = E
    out['npar'] = int(pid.max()) + 1 if len(pid) else 0
    out['nrighe'] = int(len(pid))
    out['nparole'] = int(P.n)
    nulli = dict(Lq=Lq, nl=len(pid), pid=pid, mats=[('real', {'n': Mreal['n'], 'h': simile(Mreal)})] +
                 [('sez', {'n': M['n'], 'h': simile(M)}) for M in refs['sez']])
    return out, nulli


def somme_E_con_paragrafi(nulli, pid, prima):
    """Le somme E (come in stat_pagina) con altri confini di paragrafo."""
    Lq = nulli['Lq']
    res = {'real': np.zeros((2, NB, 2)), 'sez': np.zeros((2, NB, 2))}
    nsez = sum(1 for f, _ in nulli['mats'] if f == 'sez')
    for fonte, M in nulli['mats']:
        band = bande(Lq, M['n'].shape[1], pid, prima, True)
        s = somme_bande(M, band)
        w = 1.0 / nsez if fonte == 'sez' else 1.0
        res[fonte][0, :, 0] += w * s['n'][:NB]
        res[fonte][0, :, 1] += w * s['h'][:NB]
        res[fonte][1, :, 0] += w * s['n'][NB:]
        res[fonte][1, :, 1] += w * s['h'][NB:]
    return res


def relazioni_pagine(C, A, nomi, K):
    """Per ogni pagina e per ogni classe di relazione: [numero di coppie, somma dei tassi di parole uguali, somma dei tassi di
    parole a una modifica]. Il tasso di una coppia di pagine (p, q) = coppie di parole (una per pagina) uguali / a una modifica,
    divise per n_p * n_q."""
    nt = C.nt
    righe, col, val = [], [], []
    for i, p in enumerate(nomi):
        cnt = np.bincount(C.pag[p].tok, minlength=nt)
        nz = np.nonzero(cnt)[0]
        righe += [i] * len(nz)
        col += nz.tolist()
        val += cnt[nz].tolist()
    CM = sps.csr_matrix((np.array(val, dtype=float), (righe, col)), shape=(len(nomi), nt))
    n = np.asarray(CM.sum(1)).ravel()
    Mx = (CM @ CM.T).toarray()
    Mv = (CM @ (A['I'] + A['F'] + A['M']) @ CM.T).toarray()
    den = np.outer(n, n)
    rx, rv = Mx / den, Mv / den
    out = {}
    for i, p in enumerate(nomi):
        v = []
        for k in range(6):
            sel = K[i] == k
            v.append([int(sel.sum()), round(float(rx[i][sel].sum()), 6), round(float(rv[i][sel].sum()), 6)])
        out[p] = v
    return out


# ---------------------------------------------------------------- generatori sintetici

def _conti(C):
    cw = np.zeros(C.nt, dtype=np.int64)
    for P in C.pag.values():
        cw += np.bincount(P.tok, minlength=C.nt)
    return cw


def genera_argomento(C, seme, lam, unita='pagina', ordine=None, k_topic=30, q_riga=0.05, q_pagina=0.25):
    """SOLO ARGOMENTO (nessuna copia di parole vicine): ogni pagina (o paragrafo, o una "stretta" che scorre) ha un tema = un piccolo
    insieme di parole (k_topic, scelte con peso frequenza^0,5, ognuna con un peso a scala Zipf); ogni parola, con probabilita'
    `lam`, e' pescata dal tema, altrimenti dalla frequenza generale. Le parole del tema tornano UGUALI: nessuna modifica.
    unita: 'pagina' (un tema per pagina), 'paragrafo' (un tema nuovo a ogni paragrafo), 'scorre' (un solo tema che cambia piano:
    a ogni riga ogni parola del tema e' sostituita con probabilita' q_riga, a ogni pagina q_pagina; le pagine seguono `ordine`)."""
    C.prepara()
    rnd = np.random.RandomState(seme % (2 ** 32 - 1))
    cw = _conti(C)
    ok = np.where(cw > 0)[0]
    glob = np.cumsum(cw[ok] / cw[ok].sum())
    sel = cw[ok].astype(float) ** 0.5
    sel_c = np.cumsum(sel / sel.sum())

    def pesca(cum, n=1):
        return np.minimum(np.searchsorted(cum, rnd.random_sample(n)), len(cum) - 1)

    def nuovo():
        idx = set()
        while len(idx) < min(k_topic, len(ok)):
            idx.add(int(pesca(sel_c)[0]))
        idx = np.array(sorted(idx))
        rk = rnd.permutation(len(idx))
        w = 1.0 / (rk + 1.0) ** 0.9
        return [ok[idx], np.cumsum(w / w.sum())]

    def sostituisci(topic, q):
        for i in range(len(topic[0])):
            if rnd.random_sample() < q:
                topic[0][i] = ok[int(pesca(sel_c)[0])]
    nomi = list(C.pag.keys())
    seq = [p for p in (ordine or nomi) if p in C.pag]
    topic = nuovo()
    gen = {}
    for p in seq:
        P = C.pag[p]
        if unita == 'pagina':
            topic = nuovo()
        elif unita == 'scorre':
            sostituisci(topic, q_pagina)
        rows = []
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            if unita == 'paragrafo' and (l == 0 or (n and P.ini[P.lstart[l]])):
                topic = nuovo()
            if unita == 'scorre' and l > 0:
                sostituisci(topic, q_riga)
            ws = []
            for _ in range(n):
                if rnd.random_sample() < lam:
                    t = int(topic[0][int(pesca(topic[1])[0])])
                else:
                    t = int(ok[int(pesca(glob)[0])])
                ws.append(C.parole_in_glifi(t))
            rows.append((bool(n and P.ini[P.lstart[l]]), ws))
        gen[p] = rows
    return OrderedDict((p, gen[p]) for p in nomi)


def genera_copia_eco(C, seme, p_copia=0.04, scala=10.0, modo='misto', solo_paragrafo=False):
    """SOLA COPIA (auto-citazione): come `sintassi_modelli.genera_copia` (con probabilita' p_copia si copia una parola scritta prima
    sulla stessa pagina, distanza in parole esponenziale di media `scala`, e la si cambia; altrimenti si pesca dalla frequenza),
    con due varianti: `modo` = 'misto' (uguale 40%, un glifo cambiato 30%, in piu' 15%, in meno 15%, in un posto a caso),
    'fine' (la modifica tocca sempre l'ultimo glifo: cambiato, aggiunto o tolto) o 'inizio' (sempre il primo); `solo_paragrafo`:
    la parola si copia solo dal paragrafo in corso (si riparte a ogni paragrafo)."""
    C.prepara()
    rnd = random.Random(seme)
    cw = _conti(C)
    gl = np.zeros(C.q)
    for t in np.where(cw > 0)[0]:
        for g in C.tipi[t]:
            gl[g] += cw[t]
    gl[C.rar] = 0
    cum_t = np.cumsum(cw / cw.sum())
    cum_g = np.cumsum(gl / gl.sum())
    out = OrderedDict()
    for p, P in C.pag.items():
        toks, rows, inizio_par = [], [], 0
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            if solo_paragrafo and (l == 0 or (n and P.ini[P.lstart[l]])):
                inizio_par = len(toks)
            ws = []
            for _ in range(n):
                t = len(toks) - inizio_par
                if t and rnd.random() < p_copia:
                    d = min(t, int(rnd.expovariate(1.0 / scala)) + 1)
                    w = toks[len(toks) - d]
                    r = rnd.random()
                    g = int(np.searchsorted(cum_g, rnd.random()))
                    if modo == 'misto':
                        if r < 0.40:
                            pass
                        elif r < 0.70 or (r >= 0.85 and len(w) == 1):
                            i = rnd.randrange(len(w))
                            w = w[:i] + (g,) + w[i + 1:]
                        elif r < 0.85:
                            i = rnd.randrange(len(w) + 1)
                            w = w[:i] + (g,) + w[i:]
                        else:
                            i = rnd.randrange(len(w))
                            w = w[:i] + w[i + 1:]
                    else:
                        fine = modo == 'fine'
                        if r < 0.40:
                            pass
                        elif r < 0.70 or (r >= 0.85 and len(w) == 1):
                            w = w[:-1] + (g,) if fine else (g,) + w[1:]
                        elif r < 0.85:
                            w = w + (g,) if fine else (g,) + w
                        else:
                            w = w[:-1] if fine else w[1:]
                else:
                    w = C.tipi[int(np.searchsorted(cum_t, rnd.random()))]
                toks.append(w)
                ws.append(tuple(C.glifi[x] for x in w))
            rows.append((bool(n and P.ini[P.lstart[l]]), ws))
        out[p] = rows
    return out
