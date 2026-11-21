# -*- coding: utf-8 -*-
"""Supporto di ia17 (modulo, non e' un esperimento): parole, relazioni fra parole, testi sintetici con eco piantata, firma dei bordi.

Che cosa c'e' qui, in parole semplici
- `Struttura`: data una pagina come sequenza di segni (eventualmente preceduta dalla coda della pagina precedente), dice per ogni segno a
  quale parola appartiene, a quale riga, in che posto nella parola; e per ogni parola dove comincia e dove finisce, in che riga sta e in che
  posto della riga. Lo spazio o la fine riga dopo una parola appartengono a quella parola.
- `matrice_relazioni`: fra due tipi di parola dice se sono uguali o a una modifica (un glifo cambiato, aggiunto o tolto): e' la
  definizione di "eco" di ia09 (parola uguale o a una modifica da una gia' scritta).
- `genera_sintetico`: testi di controllo costruiti sulla disposizione e sul vocabolario di un libro (nel Voynich: il vero, nelle prove: il
  latino nella disposizione del Voynich), con un'eco piantata a distanza nota (la riga e' la copia di quella due righe sopra) oppure senza
  eco (parole indipendenti).
- `firma_bordi`: i bordi della riga (prima e ultima parola) senza usare una rete: quanto la distribuzione del primo glifo, dell'ultimo glifo
  e della lunghezza delle parole di bordo differisce da quella delle parole interne (distanza di Jensen-Shannon, in bit).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import bisect
import math
import random
from collections import Counter, OrderedDict

import numpy as np

KIND_TESTA, KIND_GLIFO, KIND_SPAZIO, KIND_EOL = 0, 1, 2, 3
LINEA_MEM = -10 ** 6            # numero di riga dei segni della coda della pagina precedente


class Struttura:
    """Struttura in parole di `tokc` = (coda della pagina precedente) + pagina, con `linea` = numero di riga di ogni segno (come ia16:
    -1 per la testa di pagina, 0, 1, ... per le righe; LINEA_MEM per la coda). `Tm` = lunghezza della coda."""

    def __init__(self, tokc, linea, Tm, voc):
        tokc = np.asarray(tokc, dtype=np.int64)
        n = len(tokc)
        primo, SP, EOL = voc['primo_contenuto'], voc['idx'][' '], voc['idx']['\n']
        kind = np.zeros(n, dtype=np.int8)
        kind[tokc >= primo + 2] = KIND_GLIFO
        kind[tokc == SP] = KIND_SPAZIO
        kind[tokc == EOL] = KIND_EOL
        wid = np.full(n, -1, dtype=np.int64)
        jw = np.zeros(n, dtype=np.int64)               # posto nella parola (lo spazio o la fine riga dopo la parola ha il posto = lunghezza)
        inizi, lung = [], []
        w, j, in_parola = -1, 0, False
        for i in range(n):
            k = kind[i]
            if k == KIND_GLIFO:
                if not in_parola:
                    w += 1
                    inizi.append(i)
                    lung.append(0)
                    j = 0
                wid[i], jw[i] = w, j
                j += 1
                lung[w] = j
                in_parola = True
            else:
                if k in (KIND_SPAZIO, KIND_EOL) and in_parola:
                    wid[i], jw[i] = w, j
                in_parola = False
        self.n, self.Tm, self.kind, self.wid, self.jw = n, Tm, kind, wid, jw
        self.tokc = tokc
        self.lin = np.asarray(linea, dtype=np.int64)
        self.w_inizio = np.array(inizi, dtype=np.int64)
        self.w_lung = np.array(lung, dtype=np.int64)
        self.nw = len(inizi)
        self.tipi_parola = [tuple(int(x) for x in tokc[s:s + l]) for s, l in zip(inizi, lung)]
        self.w_linea = self.lin[self.w_inizio] if self.nw else np.zeros(0, dtype=np.int64)
        self.w_mem = self.w_inizio < Tm
        # parole valide per l'eco: non troncate (la prima parola della coda puo' essere tagliata a meta') e non nella testa
        self.valida = np.ones(self.nw, dtype=bool)
        if Tm and self.nw:
            self.valida[0] = False
        # posto nella riga e lunghezza della riga (solo parole della pagina; per la coda -1)
        self.w_J = np.full(self.nw, -1, dtype=np.int64)
        self.w_nl = np.full(self.nw, -1, dtype=np.int64)
        riga_corr, cnt, inizio_riga = None, 0, 0
        for v in range(self.nw):
            if self.w_mem[v]:
                continue
            if self.w_linea[v] != riga_corr:
                if riga_corr is not None:
                    self.w_nl[inizio_riga:v] = cnt
                riga_corr, cnt, inizio_riga = self.w_linea[v], 0, v
            self.w_J[v] = cnt
            cnt += 1
        if riga_corr is not None:
            self.w_nl[inizio_riga:self.nw] = cnt
        self._rel = None

    def relazioni(self, cache_tipi):
        """Matrice (nw + 1) x (nw + 1) di uint8: 1 = parole uguali, 2 = a una modifica, 0 altrimenti (ultima riga e colonna = segnaposto per
        i segni senza parola). Una parola non e' in relazione con se stessa; le parole non valide non entrano."""
        if self._rel is not None:
            return self._rel
        uni = {}
        tid = np.array([uni.setdefault(t, len(uni)) for t in self.tipi_parola], dtype=np.int64)
        tipi = list(uni)
        key = tuple(tipi)
        if cache_tipi is not None and key in cache_tipi:
            R = cache_tipi[key]
        else:
            R = matrice_relazioni(tipi)
            if cache_tipi is not None:
                if len(cache_tipi) > 8:
                    cache_tipi.clear()
                cache_tipi[key] = R
        nw = self.nw
        M = np.zeros((nw + 1, nw + 1), dtype=np.uint8)
        if nw:
            M[:nw, :nw] = R[tid[:, None], tid[None, :]]
            M[np.arange(nw), np.arange(nw)] = 0
            inv = np.nonzero(~self.valida)[0]
            M[inv, :] = 0
            M[:, inv] = 0
        self._rel = M
        return M


def matrice_relazioni(tipi):
    """tipi: lista di tuple di segni. R[a, b] = 1 se uguali, 2 se differiscono di un solo segno (sostituzione, inserimento o cancellazione)."""
    n = len(tipi)
    R = np.zeros((n, n), dtype=np.uint8)
    idx = {t: i for i, t in enumerate(tipi)}
    sost = {}
    for a, t in enumerate(tipi):
        for i in range(len(t)):
            sost.setdefault((len(t), i, t[:i] + t[i + 1:]), []).append(a)
            c = t[:i] + t[i + 1:]
            if c and c in idx:
                b = idx[c]
                R[a, b] = R[b, a] = 2
    for lst in sost.values():
        if len(lst) > 1:
            ii = np.array(lst)
            R[np.ix_(ii, ii)] = 2
    R[np.arange(n), np.arange(n)] = 1
    return R


# ---------------------------------------------------------------- testi sintetici con eco piantata

P_RIGA_ECO = 1.0          # probabilita' che una riga sia la copia di quella a distanza D_ECO
SENZA_CATENE_ECO = False  # se vero, una riga non copia una riga che e' a sua volta una copia (niente catene a distanza 4 e 6)
Q_PAROLA_ECO = 0.5       # (variante per parole) probabilita' che una parola sia presa a caso dalla riga a distanza D_ECO
MOD_ECO = 0.10            # probabilita' che una parola copiata abbia un glifo cambiato
D_ECO = 2


def genera_sintetico(righe, tipo, seme, divisore, unita):
    """`righe`: le righe del libro di base (dizionari come `ia07.libro_vero()`); `tipo`: 'eco_d2' (eco piantata a 2 righe sopra) o
    'senza_eco' (parole indipendenti). Stesse righe e stesse lunghezze della base; le parole sono pescate dalla frequenza del vocabolario
    della base. Restituisce una nuova lista di righe (copie con le parole cambiate)."""
    rng = random.Random(seme)
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    def modifica(w):
        u = divisore(w)
        for _ in range(8):
            i = rng.randrange(len(u))
            nuovo = rng.choice(unita)
            if nuovo == u[i]:
                continue
            u2 = list(u)
            u2[i] = nuovo
            w2 = ''.join(u2)
            if divisore(w2) == u2:
                return w2
        return w

    out, pagina_corr, nuove, copiate = [], None, [], []
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, nuove, copiate = x['pagina'], [], []
        n = len(x['parole'])
        copia = tipo == 'eco_d2' and len(nuove) >= D_ECO and not (SENZA_CATENE_ECO and copiate[-D_ECO]) and rng.random() < P_RIGA_ECO
        if tipo == 'eco_d2_parole':
            src = nuove[-D_ECO] if len(nuove) >= D_ECO else None
            ps = []
            for _ in range(n):
                if src and rng.random() < Q_PAROLA_ECO:
                    w = rng.choice(src)
                    ps.append(modifica(w) if rng.random() < MOD_ECO else w)
                else:
                    ps.append(fresca())
            copia = False
        elif copia:
            src = nuove[-D_ECO]
            ps = [(modifica(w) if rng.random() < MOD_ECO else w) for w in src[:n]]
            ps += [fresca() for _ in range(n - len(ps))]
        else:
            ps = [fresca() for _ in range(n)]
        nuove.append(ps)
        copiate.append(copia)
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out


def parole_in_riga_a_distanza(righe_per_pagina, dmax=6):
    """Quota di parole che compaiono (uguali) nella riga a distanza d (d = 1..dmax) della stessa pagina. righe_per_pagina: pagina -> lista di liste di parole."""
    tot, ok = Counter(), Counter()
    for rr in righe_per_pagina.values():
        for r, ws in enumerate(rr):
            for d in range(1, dmax + 1):
                if r - d < 0:
                    continue
                s = set(rr[r - d])
                for w in ws:
                    tot[d] += 1
                    ok[d] += w in s
    return OrderedDict((d, (ok[d] / tot[d]) if tot[d] else None) for d in range(1, dmax + 1))


def righe_uguali_a_distanza(righe_per_pagina, dmax=6, min_parole=3):
    """Quota di righe (con almeno `min_parole` parole) uguali per almeno meta' dei posti alla riga a distanza d (d = 1..dmax) della stessa
    pagina. Serve a vedere se un libro scritto contiene l'eco piantata. righe_per_pagina: pagina -> lista di liste di parole."""
    tot = Counter()
    ok = Counter()
    for rr in righe_per_pagina.values():
        for r, ws in enumerate(rr):
            if len(ws) < min_parole:
                continue
            for d in range(1, dmax + 1):
                if r - d < 0:
                    continue
                tot[d] += 1
                src = rr[r - d]
                comuni = sum(1 for a, b in zip(ws, src) if a == b)
                if comuni >= 0.5 * min(len(ws), len(src)):
                    ok[d] += 1
    return OrderedDict((d, (ok[d] / tot[d]) if tot[d] else None) for d in range(1, dmax + 1))


# ---------------------------------------------------------------- firma dei bordi della riga (senza rete)

def _jsd(a, b):
    """Distanza di Jensen-Shannon (bit) fra due contatori."""
    chiavi = set(a) | set(b)
    na, nb = sum(a.values()), sum(b.values())
    if na == 0 or nb == 0:
        return None
    s = 0.0
    for k in chiavi:
        p, q = a.get(k, 0) / na, b.get(k, 0) / nb
        m = 0.5 * (p + q)
        if p > 0:
            s += 0.5 * p * math.log2(p / m)
        if q > 0:
            s += 0.5 * q * math.log2(q / m)
    return s


def conti_bordi(pagine):
    """pagine: pagina -> lista di righe (inizio, [parola come tupla di glifi]). Contatori per gruppo (prima, ultima, interna) e tratto
    (primo glifo, ultimo glifo, lunghezza fino a 8), sulle righe di almeno 5 parole; interne = dal terzo posto al terzultimo."""
    c = {g: {f: Counter() for f in ('primo', 'ultimo', 'lung')} for g in ('prima', 'ultima', 'interna')}
    for rows in pagine.values():
        for _, ws in rows:
            if len(ws) < 5:
                continue
            for g, sel in (('prima', ws[:1]), ('ultima', ws[-1:]), ('interna', ws[2:-2])):
                for w in sel:
                    if not w:
                        continue
                    c[g]['primo'][w[0]] += 1
                    c[g]['ultimo'][w[-1]] += 1
                    c[g]['lung'][min(len(w), 8)] += 1
    return c


def firma_da_conti(c):
    """Sei numeri (bit): distanza JS fra le parole prime e le interne, e fra le ultime e le interne, per primo glifo, ultimo glifo e lunghezza."""
    out = OrderedDict()
    for g, nome in (('prima', 'inizio'), ('ultima', 'fine')):
        for f in ('primo', 'ultimo', 'lung'):
            out['%s_%s' % (nome, f)] = _jsd(c[g][f], c['interna'][f])
    return out


def firma_bordi(pagine):
    return firma_da_conti(conti_bordi(pagine))
