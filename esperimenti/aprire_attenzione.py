# -*- coding: utf-8 -*-
"""Supporto di ia17 (modulo, non e' un esperimento): leggere dentro l'imitatore di ia16 (mappe di attenzione e maschere).

Che cosa c'e' qui, in parole semplici
- `installa_maschera(m, primo)`: dice al modello (senza modificare il file di ia16) di nascondere alcune coppie (segno che guarda, segno guardato):
  la maschera si passa con `stato['G']` e `stato['L']` (vero = nascosto) e vale per quella sola chiamata. Il segno stesso non si nasconde mai.
- Maschere: `maschera_righe(S, T, k)` (si vedono solo la riga corrente e le k righe sopra: k = 0 e' "solo la riga"; la testa di pagina e la coda
  della pagina precedente si nascondono) e `maschera_eco(...)` (si nascondono le parole che sono "eco" della parola che si sta per scrivere,
  cioe' uguali o a una modifica; il controllo nasconde altrettante parole non-eco della stessa riga e della stessa lunghezza).
- `nll_pagina`: bit di ogni segno da indovinare di una pagina (come ia16, a parole note: "teacher forcing") con o senza maschera.
- `costi_parole`: i bit divisi per parola e per pezzo (primo glifo, glifi interni, ultimo glifo, spazio o a capo), come ia13.
- `aggrega_attenzione`: dove guardano gli strati globali: quota di attenzione per distanza in righe e per tipo di bersaglio, e "sollevamento"
  sulle parole eco (attenzione sui segni delle parole eco / attenzione attesa su segni di parole non-eco alla stessa distanza in righe e alla
  stessa distanza in segni), con l'etichetta della parola da scrivere sbagliata a caso come controllo dello strumento.
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import math
import random
from collections import OrderedDict

import numpy as np
import torch

import aprire_parole as AP

NCAT = 14                 # categorie di bersaglio (vedi NOMI_CAT)
NOMI_CAT = ['coda pagina precedente', 'testa di pagina', 'testa di riga', 'stessa riga: parola da scrivere (segni gia\' scritti)',
            'stessa riga: parola prima', 'stessa riga: seconda prima', 'stessa riga: altre',
            '1 riga sopra', '2 righe sopra', '3 righe sopra', '4-5 righe sopra', '6-9 righe sopra', '10-19 righe sopra', '20+ righe sopra']
NDL = 9                   # classi di distanza in righe per l'eco: 0, 1, 2, 3, 4-5, 6-9, 10-19, 20+, coda della pagina precedente
NOMI_DL = ['stessa riga', '1', '2', '3', '4-5', '6-9', '10-19', '20+', 'pagina precedente']
NREL = 3                  # eco: 1 = uguale (segno allineato), 2 = uguale (altro segno), 3 = a una modifica
NOMI_REL = ['uguale, segno allineato', 'uguale, altri segni', 'a una modifica']
BORDI_DL = [1, 2, 3, 4, 6, 10, 20]
BORDI_DIST = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
NB = 10
NCELLA = NDL * 4 * NB
NOMI_QC = ['inizio parola (si indovina il primo glifo)', 'dentro la parola', 'fine parola (spazio o a capo)']
LN2 = math.log(2.0)


# ---------------------------------------------------------------- la maschera

def installa_maschera(m, primo):
    """Sostituisce, sull'istanza, il calcolo dei blocchi di attenzione con uno che applica anche la maschera aggiuntiva `stato`.
    Il file di ia16 resta com'e'. Restituisce `stato` (dizionario con 'G' e 'L': tensori booleani (T, Tm + T) e (T, T), o None)."""
    stato = {'G': None, 'L': None}
    orig = m._blocchi

    def nuovo(T, Tm, W, QB, lin):
        blocchi = orig(T, Tm, W, QB, lin)
        ex = stato['G'] if (Tm > 0 or W == m.W_glob) else stato['L']
        if ex is None:
            return blocchi
        out = []
        for a, b, lo, hi, bias in blocchi:
            out.append((a, b, lo, hi, bias.masked_fill(ex[a:b, lo:hi][None], float('-inf'))))
        return out
    m._blocchi = nuovo
    m._stato17 = stato
    m._primo17 = int(primo)
    return stato


def _imposta(stato, exG, Tm):
    if exG is None:
        stato['G'] = stato['L'] = None
        return
    t = torch.from_numpy(np.ascontiguousarray(exG))
    stato['G'] = t
    stato['L'] = t[:, Tm:] if Tm else t


def maschera_righe(S, T, k, con_mem=True):
    """Nasconde i segni a piu' di k righe sopra la riga del segno che guarda (la testa di pagina conta come riga -1; la coda della pagina
    precedente sempre). Con `con_mem` l'array e' (T, Tm + T) (per un calcolo con la coda in memoria), altrimenti (T, T)."""
    Tm = S.Tm
    lq = S.lin[Tm:Tm + T]
    lk, off = (S.lin[:Tm + T], Tm) if con_mem else (S.lin[Tm:Tm + T], 0)
    ex = (lq[:, None] - lk[None, :]) > k
    ex[np.arange(T), off + np.arange(T)] = False
    return ex


def info_query(S, T, voc):
    """Per ogni segno che guarda (posizione t della pagina, cioe' posizione combinata Tm + t; indovina il segno t + 1):
    classe (0 inizio parola, 1 dentro la parola, 2 fine parola, -1 non si indovina), parola da scrivere, posto del segno da scrivere nella parola."""
    Tm = S.Tm
    kt = S.kind[Tm + 1:Tm + 1 + T]
    kq = S.kind[Tm:Tm + T]
    qc = np.full(T, -1, dtype=np.int64)
    qc[(kt == AP.KIND_GLIFO) & (kq != AP.KIND_GLIFO)] = 0
    qc[(kt == AP.KIND_GLIFO) & (kq == AP.KIND_GLIFO)] = 1
    qc[kt >= AP.KIND_SPAZIO] = 2
    wq = np.where(kt == AP.KIND_GLIFO, S.wid[Tm + 1:Tm + 1 + T], S.wid[Tm:Tm + T])
    wq = np.where(qc >= 0, wq, S.nw)
    wq = np.where(wq < 0, S.nw, wq)
    jq = S.jw[Tm + 1:Tm + 1 + T]
    return qc, wq.astype(np.int64), jq


def _wk(S, n_chiavi):
    w = S.wid[:n_chiavi]
    return np.where(w < 0, S.nw, w)


def matrice_controllo(S, Mb, seme):
    """Per ogni parola da scrivere: al posto di ogni parola eco (di `Mb`) una parola non-eco, piu' vecchia della parola da scrivere, della
    stessa riga della parola eco e, in ordine di preferenza, della stessa lunghezza e della stessa classe di frequenza nella pagina (classe =
    parte intera del logaritmo in base 2 del numero di volte che il tipo di parola compare nella pagina e nella coda: le parole eco sono per
    costruzione parole che si ripetono, e togliere parole che si ripetono costa di piu' che togliere parole rare); scelta a caso (seme fisso)."""
    nw = S.nw
    Mc = np.zeros_like(Mb)
    rng = random.Random(seme)
    freq = {}
    for v in range(nw):
        if S.valida[v]:
            freq[S.tipi_parola[v]] = freq.get(S.tipi_parola[v], 0) + 1
    fcl = np.array([int(math.log2(freq[S.tipi_parola[v]])) if S.valida[v] else -1 for v in range(nw)], dtype=np.int64)
    per_riga = {}
    for v in range(nw):
        if S.valida[v]:
            per_riga.setdefault(int(S.w_linea[v]), []).append(v)
    for wq in range(nw):
        if S.w_mem[wq]:
            continue
        E = np.nonzero(Mb[wq, :wq])[0]
        if len(E) == 0:
            continue
        Eset = set(int(x) for x in E)
        for e in E:
            lst = [c for c in per_riga.get(int(S.w_linea[e]), []) if c < wq and c not in Eset]
            if not lst:
                continue
            scelta = None
            for criteri in (('l', 'f'), ('f',), ('l',), ()):
                cand = [c for c in lst if all((S.w_lung[c] == S.w_lung[e]) if k == 'l' else (fcl[c] == fcl[e]) for k in criteri)]
                if cand:
                    scelta = rng.choice(cand)
                    break
            Mc[wq, scelta] = 1
    return Mc


def maschera_eco(S, T, qinfo, solo_uguali, controllo, seme, cache_tipi):
    """Nasconde, per ogni segno che guarda, le parole eco (uguali, oppure uguali o a una modifica) della parola da scrivere. Con
    `controllo` nasconde invece altrettante parole non-eco (vedi `matrice_controllo`)."""
    Tm = S.Tm
    M = S.relazioni(cache_tipi)
    Mb = (M == 1) if solo_uguali else (M > 0)
    if controllo:
        Mb = matrice_controllo(S, Mb.astype(np.uint8), seme).astype(bool)
    qc, wq, jq = qinfo
    wk = _wk(S, Tm + T)
    ex = Mb[wq[:, None], wk[None, :]]
    ex[np.arange(T), Tm + np.arange(T)] = False
    return ex


def conta_nascosti(ex, qc):
    """Numero medio di segni nascosti per segno che guarda (descrittivo)."""
    return float(ex[qc >= 0].sum(1).mean()) if (qc >= 0).any() else 0.0


# ---------------------------------------------------------------- bit di una pagina

def nll_pagina(m, p, mem, stato, ex, Tm=0):
    """Bit di ogni segno da indovinare (array di lunghezza T = segni - 1; nan dove il segno non si indovina) con la maschera `ex` (o senza)."""
    _imposta(stato, ex, Tm)
    try:
        with torch.no_grad():
            logit = m(p['tok'][:-1], p['cond'], p['linea'][:-1], mem)
    finally:
        _imposta(stato, None, 0)
    lp = torch.log_softmax(logit.float(), -1)
    y = torch.as_tensor(np.asarray(p['tok'][1:]), dtype=torch.long)
    nll = (-lp[torch.arange(len(y)), y] / LN2).numpy().astype(np.float64)
    nll[y.numpy() < m._primo17] = np.nan                  # i segni di testa non si indovinano (ia16 non li conta)
    return nll


def costi_parole(nll, S):
    """Bit per parola della pagina (solo parole della pagina, nell'ordine di lettura): matrice (parole, 4) con il primo glifo, i glifi interni,
    l'ultimo glifo (solo se la parola ha almeno due glifi), lo spazio o a capo dopo la parola. La somma delle 4 colonne e' il costo della parola.
    `nll[t]` e' il costo del segno t + 1 della pagina."""
    Tm = S.Tm
    v = np.nonzero(~S.w_mem)[0]
    s = S.w_inizio[v] - Tm - 1
    l = S.w_lung[v]
    x = np.where(np.isnan(nll), 0.0, nll)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    tot = cs[s + l + 1] - cs[s]
    primo = x[s]
    fine = x[s + l]
    ultimo = np.where(l >= 2, x[np.maximum(s + l - 1, 0)], 0.0)
    inter = tot - primo - ultimo - fine
    return np.stack([primo, inter, ultimo, fine], axis=1)


def etichetta_posto(S):
    """Per le parole della pagina: 0 prima della riga, 1 interna, 2 ultima della riga (le righe di una parola contano come prime)."""
    v = np.nonzero(~S.w_mem)[0]
    J, nl = S.w_J[v], S.w_nl[v]
    c = np.ones(len(v), dtype=np.int64)
    c[J == 0] = 0
    c[(J == nl - 1) & (nl >= 2)] = 2
    return c


def info_eco_parole(S):
    """Per ogni parola della pagina: distanza in righe dalla parola uguale piu' vicina gia' scritta (0 = stessa riga, -1 = nessuna nella pagina)
    e dalla parola a una modifica piu' vicina; e se c'e' un'uguale / a una modifica nella coda della pagina precedente."""
    M = S.relazioni(None)
    v = np.nonzero(~S.w_mem)[0]
    dl_eq = np.full(len(v), -1, dtype=np.int64)
    dl_mod = np.full(len(v), -1, dtype=np.int64)
    mem_eq = np.zeros(len(v), dtype=bool)
    mem_mod = np.zeros(len(v), dtype=bool)
    for i, w in enumerate(v):
        r = M[w, :w]
        for rel, dl, mm in ((1, dl_eq, mem_eq), (2, dl_mod, mem_mod)):
            u = np.nonzero(r == rel)[0]
            if len(u) == 0:
                continue
            um = S.w_mem[u]
            mm[i] = bool(um.any())
            up = u[~um]
            if len(up):
                dl[i] = int((S.w_linea[w] - S.w_linea[up]).min())
    return dl_eq, dl_mod, mem_eq, mem_mod


# ---------------------------------------------------------------- attenzione

def _classi_cella(S, tq, kk, ok, wq_b, jq_b, qc_b, Mrel, valida_ext, Tm, W):
    """Indici di cella (distanza in righe x tipo di relazione x distanza in segni) di ogni coppia (segno che guarda, segno guardato), -1 se
    non conta; e le classi di distanza in righe."""
    dist = tq[:, None] - kk[None, :]
    ismem = kk < Tm
    wk_raw = S.wid[kk]
    isw = wk_raw >= 0
    wk = np.where(isw, wk_raw, S.nw)
    dl = S.lin[tq][:, None] - S.lin[kk][None, :]
    dlc = np.digitize(np.clip(dl, 0, None), BORDI_DL)
    dl8 = np.where(ismem[None, :], 8, dlc)
    rel = Mrel[wq_b[:, None], wk[None, :]]
    al = S.jw[kk][None, :] == jq_b[:, None]
    rc = np.where(rel == 1, np.where(al, 1, 2), np.where(rel == 2, 3, 0))
    esclusa = (~isw)[None, :] | (wk[None, :] == wq_b[:, None]) | (~valida_ext[wk])[None, :] | (~ok) | (qc_b < 0)[:, None]
    tdb = np.digitize(dist, BORDI_DIST)
    cella = ((dl8 * 4 + rc) * NB + tdb)
    return np.where(esclusa, -1, cella), dist


def _somma_cella(cella, pa, qb):
    """Conti e masse per (segno che guarda, cella): N (qb, NDL, 4, NB), M (H, qb, NDL, 4, NB)."""
    valido = cella >= 0
    flat = (np.arange(qb)[:, None] * NCELLA + cella)[valido]
    N = np.bincount(flat, minlength=qb * NCELLA).reshape(qb, NDL, 4, NB).astype(np.float64)
    Ms = np.stack([np.bincount(flat, weights=pa[h][valido], minlength=qb * NCELLA).reshape(qb, NDL, 4, NB) for h in range(pa.shape[0])])
    return N, Ms


def _eco_da_celle(N, Ms, qc_b):
    """Attenzione osservata e attesa sulle parole eco, per classe di segno che guarda: (3, NDL, NREL, H) e conteggi (3, NDL, NREL)."""
    H = Ms.shape[0]
    obs = np.zeros((3, NDL, NREL, H))
    att = np.zeros((3, NDL, NREL, H))
    nq = np.zeros((3, NDL, NREL))
    N0 = N[:, :, 0, :]
    for r in range(1, 4):
        Nr = N[:, :, r, :]
        cond = (Nr > 0) & (N0 > 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            e = np.where(cond[None], Nr[None] * Ms[:, :, :, 0, :] / np.where(N0 > 0, N0, 1.0)[None], 0.0)
        o = np.where(cond[None], Ms[:, :, :, r, :], 0.0)
        for c in range(3):
            sel = qc_b == c
            if not sel.any():
                continue
            obs[c, :, r - 1, :] += o[:, sel].sum(axis=(1, 3)).T
            att[c, :, r - 1, :] += e[:, sel].sum(axis=(1, 3)).T
            nq[c, :, r - 1] += cond[sel].any(-1).sum(0)
    return obs, att, nq


def aggrega_attenzione(m, p, mem, S, T, qinfo, cache_tipi, seme_falso):
    """Mappe di attenzione degli strati globali di una pagina. Restituisce un dizionario di array (per la media sulle pagine, si sommano):
    cat_massa (3, NCAT, H), cat_chiavi (3, NCAT), nq (3), eco_obs / eco_att (3, NDL, NREL, H), eco_nq (3, NDL, NREL) e gli stessi con
    la parola da scrivere sbagliata a caso (falso_*). Chiamarla con il modello in modalita' di prova."""
    Tm = S.Tm
    m.salva_att = True
    try:
        with torch.no_grad():
            m(p['tok'][:-1], p['cond'], p['linea'][:-1], mem)
        att = [x for x in m.att if m.tipi[x[0]] == 'G']
    finally:
        m.salva_att = False
        m.att = []
    H = m.H
    qc, wq, jq = qinfo
    Mrel = S.relazioni(cache_tipi)
    valida_ext = np.append(S.valida, False)
    nw = S.nw
    # parola da scrivere sbagliata: una parola a caso della pagina (stesso posto nella parola)
    rng = np.random.default_rng(seme_falso)
    pag_w = np.nonzero((~S.w_mem) & S.valida)[0]
    falso = np.full(nw + 1, nw, dtype=np.int64)
    if len(pag_w):
        falso[pag_w] = rng.choice(pag_w, size=len(pag_w))
    out = dict(cat_massa=np.zeros((3, NCAT, H)), cat_chiavi=np.zeros((3, NCAT)), nq=np.zeros(3),
               ini_massa=np.zeros((3, H)), ini_chiavi=np.zeros(3), ini_nq=np.zeros(3),
               eco_obs=np.zeros((3, NDL, NREL, H)), eco_att=np.zeros((3, NDL, NREL, H)), eco_nq=np.zeros((3, NDL, NREL)),
               falso_obs=np.zeros((3, NDL, NREL, H)), falso_att=np.zeros((3, NDL, NREL, H)), falso_nq=np.zeros((3, NDL, NREL)))
    W = m.W_glob
    for l, a, b, lo, hi, pa in att:
        qb = b - a
        pa = pa.astype(np.float32)
        qi = np.arange(a, b)
        tq = Tm + qi
        kk = np.arange(lo, hi)
        dist = tq[:, None] - kk[None, :]
        ok = (dist >= 0) & (dist < W)
        qc_b, wq_b, jq_b = qc[a:b], wq[a:b], jq[a:b]
        if not (qc_b >= 0).any():
            continue
        # --- dove guarda: quota per categoria di bersaglio
        ismem = kk < Tm
        kind_k = S.kind[kk]
        lin_k = S.lin[kk]
        wk_raw = S.wid[kk]
        isw = wk_raw >= 0
        dl = S.lin[tq][:, None] - lin_k[None, :]
        dlc = np.digitize(np.clip(dl, 0, None), BORDI_DL)
        ro = wq_b[:, None] - np.where(isw, wk_raw, 0)[None, :]
        catw = np.where(dlc == 0, np.where(ro <= 0, 3, np.where(ro == 1, 4, np.where(ro == 2, 5, 6))), 7 + (dlc - 1))
        cat = np.where(isw[None, :], catw, -1)
        cat = np.where(ismem[None, :], 0, cat)
        cat = np.where(((~ismem) & (kind_k == 0) & (lin_k == -1))[None, :], 1, cat)
        cat = np.where(((~ismem) & (kind_k == 0) & (lin_k >= 0))[None, :], 2, cat)
        cat = np.where(ok & (qc_b >= 0)[:, None], cat, -1)
        val = cat >= 0
        flat = (np.arange(qb)[:, None] * NCAT + cat)[val]
        cnt = np.bincount(flat, minlength=qb * NCAT).reshape(qb, NCAT).astype(np.float64)
        n_all = cnt.sum(1)
        ksh = cnt / np.where(n_all > 0, n_all, 1.0)[:, None]
        for h in range(H):
            mass = np.bincount(flat, weights=pa[h][val], minlength=qb * NCAT).reshape(qb, NCAT)
            for c in range(3):
                sel = qc_b == c
                if sel.any():
                    out['cat_massa'][c, :, h] += mass[sel].sum(0)
        for c in range(3):
            sel = qc_b == c
            if sel.any():
                out['cat_chiavi'][c] += ksh[sel].sum(0)
                out['nq'][c] += sel.sum()
        # --- prime due righe della pagina (solo per i segni che guardano da riga 4 in poi)
        ini_k = (lin_k >= 0) & (lin_k <= 1) & (~ismem) & isw
        qok = (S.lin[tq] >= 4) & (qc_b >= 0)
        v2 = ok & qok[:, None]
        sel_ini = v2 & ini_k[None, :]
        n_t = v2.sum(1).astype(np.float64)
        n_i = sel_ini.sum(1).astype(np.float64)
        for c in range(3):
            selq = qok & (qc_b == c)
            if selq.any():
                out['ini_chiavi'][c] += (n_i[selq] / np.where(n_t[selq] > 0, n_t[selq], 1.0)).sum()
                out['ini_nq'][c] += selq.sum()
                for h in range(H):
                    out['ini_massa'][c, h] += (pa[h] * sel_ini)[selq].sum()
        # --- eco: parola vera e sbagliata
        for nome, wqx in (('eco', wq_b), ('falso', falso[wq_b])):
            cella, _ = _classi_cella(S, tq, kk, ok, wqx, jq_b, qc_b, Mrel, valida_ext, Tm, W)
            N, Ms = _somma_cella(cella, pa, qb)
            o, e, n = _eco_da_celle(N, Ms, qc_b)
            out[nome + '_obs'] += o
            out[nome + '_att'] += e
            out[nome + '_nq'] += n
    return out


def somma_dizionari(lista):
    out = None
    for d in lista:
        if out is None:
            out = {k: v.copy() for k, v in d.items()}
        else:
            for k, v in d.items():
                out[k] = out[k] + v
    return out
