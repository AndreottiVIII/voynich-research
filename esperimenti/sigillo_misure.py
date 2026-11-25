# -*- coding: utf-8 -*-
"""IA41, modulo di supporto: le MISURE dell'esame sigillato (otto di struttura di IA35 + sei nuove), il rumore di campionamento e i DIFETTI PIANTATI.

In parole semplici
- Qui il "vero" e' solo l'insieme delle pagine TENUTE FUORI della divisione (circa 30 pagine, mai viste da rete, tabelle e scelte). Ogni misura si calcola sulle pagine tenute fuori del libro finto
  (le stesse pagine del vero) e sulle pagine tenute fuori vere. Come unita' di scarto si usa il **rumore di campionamento**: la deviazione standard della misura su 60 estrazioni a caso di fogli
  (stesso numero di fogli dei tenuti fuori, stessa scelta regolare per sezione di `rifare_dati.divisione_fogli`) del testo vero; z = (media dei libri finti - vero tenuto fuori) / rumore.
- **Otto misure vecchie** (`sezione_misure.misure_testo`: heaps, burst, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax; IA34-IA35) e **sei nuove**, definite qui:
    lingua      nell'erbario (sezione H): coseno medio fra pagine della stessa lingua (A o B) meno coseno medio fra pagine di lingue diverse (300 parole piu' frequenti). Previsione scritta: FALLISCE
                (le tabelle sono per sezione, non per lingua)
    dispersione indice di dispersione dei 50 bigrammi di unita' di glifo piu' comuni fra le pagine (con almeno 150 bigrammi): somma su pagine di (conti - attesi)^2 / (attesi (1 - f)), diviso (pagine - 1), media
                sui 50 bigrammi; vale circa 1 se le pagine sono estrazioni a caso della media, piu' di 1 se ogni pagina ha un suo profilo
    vicine      pagine consecutive del libro (ordine di `contesto_A`) della stessa sezione: coseno medio (400 parole piu' frequenti) meno quello di pagine della stessa sezione non consecutive (distanza almeno 3)
    lunghezza   coefficiente di variazione (sd / media) della lunghezza delle parole in unita' di glifo
    doppie      quota delle parole uguali alla parola prima nella stessa riga
    testa       quota delle occorrenze di parola che sono una delle 10 parole piu' frequenti
- **Controllo di coincidenza** con tutto quello gia' usato in IA32-IA40 (obiettivo: copia netta, contatto, G9, bordi, costo di forma, parole nuove, Λ, k90, e231, e266, K, `riuso_sez`, `div_bigr`, `div_par`; guardie:
  `g_rig_parole`, `g_lung_par`, `g_nov_pagine`, `g_bigr_rip`, `g_zipf`; esame: D, R_rel e le otto): nessuna coincide; `lingua` e `vicine` toccano la stessa materia di `sezione` (pagine fra le sezioni) ma sono altri
  confronti (lingua dentro una sezione; pagine adiacenti), `testa` e `lunghezza` sono parenti di `g_zipf` e `g_lung_par` (media della lunghezza) ma sono altre grandezze. Dichiarato.
- **Difetti piantati** (conti sul testo, niente generazione): `pagine_rimescolate` = ogni pagina porta le righe di un'altra pagina (permutazione fissa): `sezione`, `lingua`, `vicine` e l'indovina-sezione devono crollare;
  `meta_righe` = una riga su due sostituita dalla riga corrispondente di un altro libro (per i giudici: le righe di `neu`).
Nessun risultato e' scritto qui.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import piano_misure as PMS  # noqa: E402
import sezione_misure as SM  # noqa: E402
import rifare_dati as RD  # noqa: E402

VECCHIE = ('heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par', 'ttr_pagina', 'hapax')
NUOVE = ('lingua', 'dispersione', 'vicine', 'lunghezza', 'doppie', 'testa')
TUTTE = VECCHIE + NUOVE
ESTRAZIONI = int(os.environ.get('ESTRAZIONI41', 60))
SOGLIA_DIFETTO = 3.0                       # |z| del difetto piantato oltre il quale la misura "vede" il suo difetto (in unita' di rumore)


def _parole(rr):
    return [w for _, ps in rr for w in ps]


def _cos_pagine(rows, pagine, top):
    tot = Counter(w for p in pagine for w in _parole(rows[p]))
    voc = [w for w, _ in tot.most_common(top)]
    ix = {w: i for i, w in enumerate(voc)}
    M = np.zeros((len(pagine), len(voc)))
    for i, p in enumerate(pagine):
        for w in _parole(rows[p]):
            j = ix.get(w)
            if j is not None:
                M[i, j] += 1
    nr = np.linalg.norm(M, axis=1)
    ok = nr > 0
    M[ok] = M[ok] / nr[ok][:, None]
    return M @ M.T, ok


def m_lingua(rows):
    ch = PMS.chiavi_pagina()
    pg = [p for p in rows if p in ch and ch[p][0] == 'H' and ch[p][1] in ('A', 'B')]
    la = [p for p in pg if ch[p][1] == 'A']
    lb = [p for p in pg if ch[p][1] == 'B']
    if len(la) < 4 or len(lb) < 4:
        return None
    S, ok = _cos_pagine(rows, pg, 300)
    lang = np.array([ch[p][1] for p in pg])
    n = len(pg)
    uguali, diverse = [], []
    for i in range(n):
        for j in range(i + 1, n):
            if ok[i] and ok[j]:
                (uguali if lang[i] == lang[j] else diverse).append(S[i, j])
    if len(uguali) < 5 or len(diverse) < 5:
        return None
    return float(np.mean(uguali) - np.mean(diverse))


def m_dispersione(rows):
    from itertools import chain
    pag = []
    for p, rr in rows.items():
        c = Counter()
        for _, ws in rr:
            for w in ws:
                for a, b in zip(w[:-1], w[1:]):
                    c[(a, b)] += 1
        n = sum(c.values())
        if n >= 150:
            pag.append((c, n))
    if len(pag) < 8:
        return None
    tot = Counter()
    for c, _ in pag:
        tot.update(c)
    N = float(sum(n for _, n in pag))
    top = [k for k, _ in tot.most_common(50)]
    ds = []
    for k in top:
        f = tot[k] / N
        if not 0 < f < 1:
            continue
        s = sum((c.get(k, 0) - n * f) ** 2 / (n * f * (1 - f)) for c, n in pag)
        ds.append(s / (len(pag) - 1))
    return float(np.mean(ds)) if ds else None


def m_vicine(rows):
    ch = PMS.chiavi_pagina()
    ordine = list(I7.contesto_A()['ids'])                          # ordine del libro (pagine dei giudici)
    pos = {p: i for i, p in enumerate(ordine)}
    pg = [p for p in rows if p in ch and p in pos]
    if len(pg) < 10:
        return None
    pg.sort(key=lambda p: pos[p])
    S, ok = _cos_pagine(rows, pg, 400)
    cons, non = [], []
    for i in range(len(pg)):
        for j in range(i + 1, len(pg)):
            if not (ok[i] and ok[j]) or ch[pg[i]][0] != ch[pg[j]][0]:
                continue
            d = pos[pg[j]] - pos[pg[i]]
            if d == 1:
                cons.append(S[i, j])
            elif d >= 3:
                non.append(S[i, j])
    if len(cons) < 3 or len(non) < 10:
        return None
    return float(np.mean(cons) - np.mean(non))


def m_lunghezza(rows):
    L = [len(w) for rr in rows.values() for _, ws in rr for w in ws]
    if len(L) < 800:
        return None
    return float(np.std(L) / np.mean(L))


def m_doppie(rows):
    n = d = 0
    for rr in rows.values():
        for _, ws in rr:
            for a, b in zip(ws[:-1], ws[1:]):
                n += 1
                d += (a == b)
    return float(d / n) if n >= 800 else None


def m_testa(rows):
    c = Counter(w for rr in rows.values() for _, ws in rr for w in ws)
    n = sum(c.values())
    if n < 800:
        return None
    return float(sum(v for _, v in c.most_common(10)) / n)


FUNZIONI_NUOVE = OrderedDict([('lingua', m_lingua), ('dispersione', m_dispersione), ('vicine', m_vicine), ('lunghezza', m_lunghezza), ('doppie', m_doppie), ('testa', m_testa)])


def misure(rows, pagine):
    """Le quattordici misure di un testo `rows` (pagina -> righe) sulle `pagine` date (solo quelle presenti). -> OrderedDict nome -> valore (None se troppo corto)."""
    sub = OrderedDict((p, rows[p]) for p in pagine if p in rows)
    out = OrderedDict(SM.misure_testo(sub))
    for n, f in FUNZIONI_NUOVE.items():
        try:
            out[n] = f(sub)
        except (ValueError, ZeroDivisionError):
            out[n] = None
    return out


# ---------------------------------------------------------------- rumore di campionamento

def estrazione_fogli(seme, n_fuori=None):
    """Una scelta a caso di fogli con lo stesso criterio di `rifare_dati.divisione_fogli` (ordine casuale dentro ogni sezione, poi scelta regolare) e la stessa quota di tenuti fuori."""
    rnd = random.Random(seme)
    per_sez = OrderedDict()
    for f, s in RD.fogli_del_libro():
        per_sez.setdefault(s, []).append(f)
    ordine = []
    for s in sorted(per_sez):
        l = list(per_sez[s])
        rnd.shuffle(l)
        ordine += l
    scelti, _ = RD._scegli_ogni(ordine, RD.FUORI32)
    return sorted(scelti)


def rumore(vere, ids, estrazioni=None, seme0=41000):
    """Deviazione standard di ogni misura sul testo vero su `estrazioni` insiemi a caso di fogli. -> dict(sd, n)."""
    estrazioni = ESTRAZIONI if estrazioni is None else estrazioni
    val = {n: [] for n in TUTTE}
    for k in range(estrazioni):
        ins = set(estrazione_fogli(seme0 + k))
        pg = [p for p in ids if I7.foglio_di(p) in ins]
        m = misure(vere, pg)
        for n in TUTTE:
            if m.get(n) is not None:
                val[n].append(m[n])
    return OrderedDict((n, OrderedDict([('sd', float(np.std(v, ddof=1)) if len(v) > 5 else None), ('media', float(np.mean(v)) if v else None), ('n', len(v))])) for n, v in val.items())


# ---------------------------------------------------------------- difetti piantati

def pagine_rimescolate(rows, seme=4141):
    """Ogni pagina porta le righe di un'altra pagina (permutazione fissa di tutte le pagine): le etichette di sezione restano, il contenuto no."""
    nomi = list(rows)
    perm = list(nomi)
    random.Random(seme).shuffle(perm)
    return OrderedDict((p, rows[q]) for p, q in zip(nomi, perm))


def meta_righe(rows, altro):
    """Una riga su due (le dispari di ogni pagina) sostituita dalla riga di `altro` nella stessa posizione (se c'e'): il resto resta. Per i giudici `altro` e' un libro di `neu`."""
    out = OrderedDict()
    for p, rr in rows.items():
        ar = altro.get(p) or []
        out[p] = [((r[0], ar[j][1]) if (j % 2 == 1 and j < len(ar)) else r) for j, r in enumerate(rr)]
    return out


if __name__ == '__main__':
    pass
