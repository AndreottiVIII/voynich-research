# -*- coding: utf-8 -*-
"""IA37, modulo di supporto: i conteggi PER SEZIONE (tabelle di segni e lessico di parole), la scelta del ripiego sulla validazione e la divergenza fra sezioni.

In parole semplici
- Lo scrittore di IA33 corregge la rete con conteggi dell'INTERO libro d'addestramento (bigrammi, trigrammi e quadrigrammi di segni; alberi di parole). Qui gli stessi conteggi si costruiscono
  per ogni sezione, dalle sole PAGINE d'addestramento di quella sezione (una pagina appartiene a una sezione: ci sono sette fogli a cavallo di due; mai pagine di validazione ne' di fogli tenuti fuori).
- **Ripiego bayesiano.** Dove i dati di una sezione sono pochi si mescola con la tabella globale: per ogni contesto, tabella di sezione = (conti della sezione + K x tabella globale) / (somma dei conti + K).
  K e' il numero di "osservazioni virtuali" della tabella globale (K = 0 sarebbe la tabella di sezione pura, K grande la tabella globale). Lo stesso per l'albero delle parole (conti di sezione + K x conti globali
  normalizzati sul nodo). Una sezione senza pagine d'addestramento ha la tabella globale.
- **K si sceglie sulla perplessita' dei fogli di VALIDAZIONE** (mai i tenuti fuori): fra K in {1, 3, 10, 30, 100, 300} e la tabella globale, quello che da' meno bit per segno al predittore a trigrammi
  sui segni delle pagine di validazione (stessi contesti per tutti; sezione della pagina). Se vince la globale si usa K = 300 e lo si dice. `scegli_ripiego`.
- **Divergenza fra sezioni** (controllo diretto della diagnosi, descrittivo): media, sulle coppie di sezioni con abbastanza testo, della divergenza di Jensen-Shannon (in bit) fra le distribuzioni
  (a) dei bigrammi di unita' di glifo (con il segno di spazio fra le parole) e (b) delle 300 parole piu' frequenti del testo, calcolate sulle pagine dei giudici di un libro. Un libro che non distingue le
  sezioni ha divergenza vicina a zero; il testo vero ha il valore del libro vero. `divergenza_sezioni`.
Nessun risultato e' scritto qui.
"""
import math
import os
import sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import piano_misure as PMS  # noqa: E402

GRIGLIA_K = (1.0, 3.0, 10.0, 30.0, 100.0, 300.0)
K_DEFAULT = 20.0
FINE = OS.FINE
LS = OS.LS
MIN_SEGNI_DIV = 2000                  # bigrammi minimi di una sezione per entrare nella divergenza
MIN_PAROLE_DIV = 600                 # occorrenze di parola minime di una sezione per entrare nella divergenza
TOP_DIV = 300


def sezione_di_pagina():
    """pagina -> sezione (la lettera della testa `S:`), dal libro del mondo attivo."""
    return {p: k[0] for p, k in PMS.chiavi_pagina().items()}


def pagine_di_addestramento(f_add):
    """sezione -> lista dei nomi delle pagine d'addestramento (foglio in `f_add`) di quella sezione."""
    sp = sezione_di_pagina()
    ins = set(f_add)
    out = defaultdict(list)
    for p, d in I16.dati_pagine().items():
        if d['foglio'] in ins and p in sp:
            out[sp[p]].append(p)
    return out


def conti_segni(pagine):
    """Conti grezzi dei segni di scrittura sulle `pagine` (nomi): (bigrammi (V+1) x V, trigrammi dict, quadrigrammi dict), con le stesse definizioni di contesto di
    `rifare_scrittura.tabella_bigrammi`, `tabella_trigrammi` e `oracolo_scrittura.tabella_quadrigrammi` (stato V = inizio di riga)."""
    voc = I7.vocabolario()
    primo = voc['primo_contenuto']
    V = len(voc['segni'])
    dp = I16.dati_pagine()
    c2 = np.zeros((V + 1, V))
    c3, c4 = {}, {}
    for p in pagine:
        tok = [int(x) for x in dp[p]['tok']]
        stato = [x if x >= primo else V for x in tok]
        for t in range(1, len(tok)):
            b = tok[t]
            if b < primo:
                continue
            c2[stato[t - 1], b] += 1
            if t >= 2:
                v = c3.get((stato[t - 2], stato[t - 1]))
                if v is None:
                    v = c3[(stato[t - 2], stato[t - 1])] = np.zeros(V)
                v[b] += 1
            if t >= 3:
                kk = (stato[t - 3], stato[t - 2], stato[t - 1])
                v = c4.get(kk)
                if v is None:
                    v = c4[kk] = np.zeros(V)
                v[b] += 1
    return c2, c3, c4


class TabelleSezione:
    """Le tabelle di segni per sezione con ripiego sulle tabelle globali dello scrittore (`scrittore.T`, `T3`, `T4`, `logT`...). Costruzione pigra, in cache."""

    def __init__(self, scrittore, f_add, K):
        self.w, self.K = scrittore, float(K)
        self.pagine = pagine_di_addestramento(f_add)
        self._conti, self._t2, self._t3, self._t4 = {}, {}, {}, {}

    def sezioni(self):
        return sorted(self.pagine)

    def conti(self, sez):
        if sez not in self._conti:
            self._conti[sez] = conti_segni(self.pagine.get(sez, []))
        return self._conti[sez]

    def T2(self, sez):
        """(probabilita', logaritmo) bigrammi (V+1) x V della sezione con ripiego sulla globale."""
        if sez not in self._t2:
            c2 = self.conti(sez)[0]
            Tg = self.w.T
            T = (c2 + self.K * Tg) / (c2.sum(1, keepdims=True) + self.K)
            self._t2[sez] = (T, np.log(np.maximum(T, 1e-9)))
        return self._t2[sez]

    def _backoff(self, cache, sez, kk, conti, Tg, logTg):
        """Voce (kk) di una tabella sparsa: None se il contesto non e' nella globale; la globale se la sezione non l'ha mai visto; altrimenti il ripiego."""
        t = Tg.get(kk)
        if t is None:
            return None
        c = conti.get(kk)
        if c is None:
            return t, logTg[kk]
        key = (sez, kk)
        r = cache.get(key)
        if r is None:
            p = (c + self.K * t) / (c.sum() + self.K)
            r = cache[key] = (p, np.log(np.maximum(p, 1e-9)))
        return r

    def T3(self, sez, kk):
        return self._backoff(self._t3, sez, kk, self.conti(sez)[1], self.w.T3, self.w.logT3)

    def T4(self, sez, kk):
        return self._backoff(self._t4, sez, kk, self.conti(sez)[2], self.w.T4, self.w.logT4)


class LessicoSezione:
    """L'albero delle parole di una sezione (conti dalle sole pagine d'addestramento di quella sezione) con ripiego sul lessico globale `lex` (un `oracolo_scrittura.Lessico`):
    stessi prefissi e stesso ordine dei glifi del nodo globale, cosi' le spinte della sezione e quelle globali hanno la stessa forma."""

    def __init__(self, lex, pagine, K):
        voc = I7.vocabolario()
        primo = voc['primo_contenuto']
        SP, EOL = primo, primo + 1
        dp = I16.dati_pagine()
        self.lex, self.K = lex, float(K)
        uni, bi = defaultdict(Counter), defaultdict(Counter)
        for p in pagine:
            prev, cur = LS, []
            for t in dp[p]['tok']:
                t = int(t)
                if t < primo:
                    prev, cur = LS, []
                    continue
                if t == SP or t == EOL:
                    if cur:
                        w = tuple(cur)
                        for k in range(len(w)):
                            uni[w[:k]][w[k]] += 1
                            bi[(prev, w[:k])][w[k]] += 1
                        uni[w][FINE] += 1
                        bi[(prev, w)][FINE] += 1
                        prev = w
                        cur = []
                    if t == EOL:
                        prev = LS
                else:
                    cur.append(t)
        self.uni, self.bi = dict(uni), dict(bi)
        self._nu, self._nb = {}, {}

    @staticmethod
    def _fondi(sez_c, glob_c, K):
        tot = float(sum(glob_c.values()))
        out = {k: K * v / tot for k, v in glob_c.items()}
        for k, v in (sez_c or {}).items():
            out[k] = out.get(k, 0.0) + v
        return out

    def nodo_u(self, pi):
        n = self._nu.get(pi)
        if n is None:
            g = self.lex.uni.get(pi)
            if g is None:
                return None
            n = self._nu[pi] = OS.Nodo(self._fondi(self.uni.get(pi), g, self.K))
        return n

    def nodo_b(self, prev, pi, nodo):
        k = (prev, pi)
        if k in self._nb:
            return self._nb[k]
        g = self.lex.bi.get(k)
        r = None
        if g is not None:
            c = self._fondi(self.bi.get(k), g, self.K)
            cb = np.array([c.get(x, 0) for x in nodo.ids.tolist()] + [c.get(FINE, 0)], float)
            r = (cb + OS.LAMBDA_B * nodo.T) / (cb.sum() + OS.LAMBDA_B)
        self._nb[k] = r
        return r


def scegli_ripiego(scrittore, f_add, f_val, griglia=GRIGLIA_K):
    """K fra `griglia` (e la tabella globale) con meno bit per segno sulle pagine di VALIDAZIONE (predittore a trigrammi, solo i contesti presenti nella tabella globale, sezione della pagina).
    -> dict(K, bit_globale, bit_per_K, n_segni, batte_globale, per_sezione)."""
    voc = I7.vocabolario()
    primo = voc['primo_contenuto']
    V = len(voc['segni'])
    dp = I16.dati_pagine()
    sp = sezione_di_pagina()
    tab = TabelleSezione(scrittore, f_add, 1.0)
    inv = set(f_val)
    bit = OrderedDict((K, 0.0) for K in griglia)
    bit_g, n = 0.0, 0
    per_sez = defaultdict(lambda: [0, 0.0, 0.0])
    for p, d in dp.items():
        if d['foglio'] not in inv or p not in sp:
            continue
        sez = sp[p]
        c3 = tab.conti(sez)[1]
        tok = [int(x) for x in d['tok']]
        stato = [x if x >= primo else V for x in tok]
        for t in range(2, len(tok)):
            b = tok[t]
            if b < primo:
                continue
            kk = (stato[t - 2], stato[t - 1])
            tg = scrittore.T3.get(kk)
            if tg is None:
                continue
            n += 1
            lg = -math.log2(max(tg[b], 1e-9))
            bit_g += lg
            c = c3.get(kk)
            for K in griglia:
                if c is None:
                    bit[K] += lg
                else:
                    bit[K] += -math.log2(max((c[b] + K * tg[b]) / (c.sum() + K), 1e-9))
            ps = per_sez[sez]
            ps[0] += 1
            ps[1] += lg
    migliore = min(bit, key=lambda K: bit[K])
    batte = bool(bit[migliore] < bit_g - 1e-9)
    out = OrderedDict([('K', float(migliore if batte else max(griglia))), ('batte_globale', batte), ('n_segni', n), ('bit_globale', bit_g / max(n, 1)),
                       ('bit_per_K', OrderedDict((str(int(K)), v / max(n, 1)) for K, v in bit.items())),
                       ('pagine_addestramento_per_sezione', OrderedDict((s, len(v)) for s, v in sorted(tab.pagine.items())))])
    return out


# ---------------------------------------------------------------- divergenza fra sezioni

def _js(p, q):
    m = 0.5 * (p + q)
    def kl(a):
        ok = a > 0
        return float(np.sum(a[ok] * np.log2(a[ok] / m[ok])))
    return 0.5 * kl(p) + 0.5 * kl(q)


def divergenza_sezioni(rows, pagine=None, top=TOP_DIV, sezioni=None):
    """Divergenza fra sezioni di un testo `rows` (pagina -> [(inizio, [parole come tuple di unita'])]), sulle `pagine` date. -> dict(bigr, parole, sezioni): media delle divergenze di Jensen-Shannon (bit)
    fra le coppie di sezioni con abbastanza testo, sui bigrammi di unita' (spazio fra le parole) e sulle `top` parole piu' frequenti del testo."""
    sp = sezione_di_pagina() if sezioni is None else sezioni
    if pagine is not None:
        rows = OrderedDict((p, rows[p]) for p in pagine if p in rows)
    big, par, tot = defaultdict(Counter), defaultdict(Counter), Counter()
    for p, rr in rows.items():
        s = sp.get(p)
        if s is None:
            continue
        for _, ws in rr:
            seq = []
            for w in ws:
                seq += list(w) + ['_']
                par[s][w] += 1
                tot[w] += 1
            for a, b in zip(seq[:-1], seq[1:]):
                big[s][(a, b)] += 1
    voc_b = sorted({k for c in big.values() for k in c}, key=str)
    voc_p = [w for w, _ in tot.most_common(top)]
    ib = {k: i for i, k in enumerate(voc_b)}
    ip = {k: i for i, k in enumerate(voc_p)}
    vb, vp = {}, {}
    for s in big:
        if sum(big[s].values()) >= MIN_SEGNI_DIV:
            v = np.full(len(voc_b), 0.5)
            for k, c in big[s].items():
                v[ib[k]] += c
            vb[s] = v / v.sum()
    for s in par:
        n = sum(c for w, c in par[s].items() if w in ip)
        if n >= MIN_PAROLE_DIV:
            v = np.full(len(voc_p), 0.5)
            for w, c in par[s].items():
                if w in ip:
                    v[ip[w]] += c
            vp[s] = v / v.sum()

    def media(vs):
        ss = sorted(vs)
        d = [_js(vs[a], vs[b]) for i, a in enumerate(ss) for b in ss[i + 1:]]
        return float(np.mean(d)) if d else None
    return OrderedDict([('bigr', media(vb)), ('parole', media(vp)), ('sezioni_bigr', sorted(vb)), ('sezioni_parole', sorted(vp))])


if __name__ == '__main__':
    pass
