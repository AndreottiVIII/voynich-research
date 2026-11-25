# -*- coding: utf-8 -*-
"""IA37, modulo di supporto: lo scrittore di IA36 (14 manopole di IA33 sopra la rete condizionata) con le FREQUENZE PER SEZIONE (una manopola nuova: `a_sez`).

In parole semplici
- Le correzioni dello scrittore (`w_cont`, `w_tri`, `w_quad` sui segni; `w_uni`, `w_bi` sulle parole) spingono la distribuzione della rete verso conteggi dell'INTERO libro d'addestramento, senza
  sezione. Qui, con `a_sez` > 0, ogni spinta e' la media pesata della spinta di sempre (peso 1 - a_sez: tabella globale e conti globali di quanto si e' scritto) e della spinta "di sezione" (peso a_sez:
  tabella della sezione con ripiego sulla globale, e conti di quanto si e' scritto NELLA SEZIONE in questo libro). `a_sez` = 0: nessuna differenza con lo scrittore di IA36 (stesso numero di estrazioni,
  stesse parole: provato). `a_sez` = 1: solo le tabelle e i conti della sezione.
- La sezione e' quella della pagina che si sta scrivendo (la disposizione del libro, come per le teste di pagina). I conteggi di una sezione vengono SOLO da pagine d'addestramento di quella sezione.
- La memoria di sezione di IA36 (`w_sez`, `t_sez`) resta SPENTA (`w_sez` = 0) e fuori dal ciclo: una sola novita' per volta.
- Cubo di 15 manopole: le 14 di IA33 e `a_sez` = max(0, (u - 0,2) / 0,8) (zona piatta sotto 0,2 come le altre). Il ripiego K e' in `<cartella del mondo>/ripiego.json` (scelto sulla validazione, `freqsez_tabelle`).
Nessun risultato e' scritto qui.
"""
import json
import math
import os
import sys

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402,F401
import rifare_scrittura as RS  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import prudente_scrittura as PW  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402

NOMI37 = OS.NOMI33 + ('a_sez',)
DIM37 = len(NOMI37)                                   # 15
U_A_NEUTRO = 0.1
U_A_PARTENZA = 0.2                                    # al bordo della zona piatta
EPS = OS.EPS


def da_cubo37(u):
    """u in [0,1]^15 (o 14: `a_sez` = 0) -> le manopole (le 14 di IA33, `a_sez`, e `w_sez` = 0 e `t_sez` neutro per la memoria di IA36, spenta)."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    k = OS.da_cubo33(u[:14])
    a = float(max(0.0, (u[14] - 0.2) / 0.8)) if len(u) > 14 else 0.0
    k['w_sez'] = 0.0
    k['t_sez'] = PW.NEUTRO36['t_sez']
    k['a_sez'] = min(1.0, a)
    return k


def neutro_cubo37():
    return np.concatenate([OS.neutro_cubo33(), [U_A_NEUTRO]])


def da_cubo36(u16, a_sez=0.0):
    """Un cubo di IA36 (16 manopole) o di IA35 (14) -> cubo a 15 (la memoria di sezione di IA36 si butta: IA37 la tiene spenta); `a_sez` = 0 mette `a` al bordo spento."""
    u = np.asarray(u16, float)[:14]
    a = U_A_PARTENZA if not a_sez else min(1.0, 0.2 + 0.8 * float(a_sez))
    return np.concatenate([u, [a]])


def senza_frequenze(u15):
    u = np.asarray(u15, float).copy()
    u[14] = min(u[14], 0.2)
    return u


class StatoLibro37(PW.StatoLibro36):
    """Lo stato di un libro: quello di IA36 piu' i conti di quanto si e' scritto in ogni sezione (retroazione delle spinte di sezione)."""

    def __init__(self, V):
        super().__init__(V)
        self.V = V
        self.a = 0.0
        self.sec = None
        self.G2s, self.G3s, self.G4s, self.Gus, self.Gbs = {}, {}, {}, {}, {}

    def g2(self, sec):
        g = self.G2s.get(sec)
        if g is None:
            g = self.G2s[sec] = np.zeros((self.V + 1, self.V))
        return g


class ScrittoreFreq(PW.ScrittoreSez):
    """Lo scrittore di IA36 con le frequenze per sezione. `libro33(u, seme, fogli)` accetta 14 o 15 manopole."""

    def __init__(self, cartella):
        super().__init__(cartella)
        p = os.path.join(os.path.dirname(os.path.abspath(cartella)), 'ripiego.json')
        self.K = float(json.load(open(p, encoding='utf-8'))['K']) if os.path.exists(p) else FT.K_DEFAULT
        self.tab = FT.TabelleSezione(self, self.P.f_add, self.K)
        self._lex_sez = {}

    def lessico_sez(self, sec):
        if sec not in self._lex_sez:
            self._lex_sez[sec] = FT.LessicoSezione(self.lessico, self.tab.pagine.get(sec, []), self.K)
        return self._lex_sez[sec]

    def _sez_attiva(self, S, k):                        # la memoria di IA36 e' spenta
        return False

    # ---- le spinte di parole (come `ScrittoreL._parole`, con la media pesata globale / sezione)
    def _parole(self, z, idx, S, k, SP, EOL):
        lex, pos = self.lessico, self.pos
        a = S.a
        pi = tuple(S.wid)
        nodo = lex.nodo_u(pi)
        if nodo is not None:
            p = pos[nodo.ids]
            ok = p >= 0
            pf = (pos[SP], pos[EOL])
            sh = np.zeros(len(nodo.ids) + 1)
            ls = None
            ns = None
            if a > 0 and (k['w_uni'] > 0 or k['w_bi'] > 0):
                ls = self.lessico_sez(S.sec)
                ns = ls.nodo_u(pi)
                if ns is None or len(ns.T) != len(nodo.T) or not np.array_equal(ns.ids, nodo.ids):
                    ls = ns = None
            if k['w_uni'] > 0:
                Gu = S.Gu.get(pi)
                if Gu is None:
                    Gu = S.Gu[pi] = np.zeros(len(nodo.T))
                s_g = OS._retro(nodo.T, Gu, k['w_uni'])
                if ns is not None:
                    Gus = S.Gus.get((S.sec, pi))
                    if Gus is None:
                        Gus = S.Gus[(S.sec, pi)] = np.zeros(len(ns.T))
                    sh += (1 - a) * s_g + a * OS._retro(ns.T, Gus, k['w_uni'])
                else:
                    sh += s_g
            if k['w_bi'] > 0:
                tb = lex.nodo_b(S.prev_w, pi, nodo)
                if tb is not None:
                    kb = (S.prev_w, pi)
                    Gb = S.Gb.get(kb)
                    if Gb is None:
                        Gb = S.Gb[kb] = np.zeros(len(tb))
                    s_g = OS._retro(tb, Gb, k['w_bi'])
                    tbs = ls.nodo_b(S.prev_w, pi, ns) if ns is not None else None
                    if tbs is not None and len(tbs) == len(tb):
                        Gbs = S.Gbs.get((S.sec, kb))
                        if Gbs is None:
                            Gbs = S.Gbs[(S.sec, kb)] = np.zeros(len(tbs))
                        sh += (1 - a) * s_g + a * OS._retro(tbs, Gbs, k['w_bi'])
                    else:
                        sh += s_g
            if k['w_uni'] > 0 or k['w_bi'] > 0:
                z[p[ok]] += sh[:-1][ok]
                if nodo.fine:
                    for q in pf:
                        if q >= 0:
                            z[q] += sh[-1]
            if k['b_nuove'] != 0.0:
                dentro = np.zeros(len(idx), bool)
                dentro[p[ok]] = True
                if nodo.fine:
                    for q in pf:
                        if q >= 0:
                            dentro[q] = True
                z[~dentro] += k['b_nuove']
        if k['w_pag'] > 0 and S.pg:
            c = S.pg.get(pi)
            if c:
                n = float(sum(c.values()))
                gam = k['w_pag'] * n / (n + OS.NU_PAG)
                z = self._mescola(z, idx, c, gam, SP, EOL)
        return z

    def _registra(self, S, s, SP, EOL):
        if S.a > 0:
            pi = tuple(S.wid)
            nodo = self.lessico.nodo_u(pi)
            fine = (s == SP or s == EOL)
            if nodo is not None:
                j = len(nodo.T) - 1 if fine else nodo.indice.get(s)
                if j is not None and (not fine or nodo.fine):
                    Gus = S.Gus.get((S.sec, pi))
                    if Gus is not None and j < len(Gus):
                        Gus[j] += 1
                    Gbs = S.Gbs.get((S.sec, (S.prev_w, pi)))
                    if Gbs is not None and j < len(Gbs):
                        Gbs[j] += 1
        super()._registra(S, s, SP, EOL)

    # ---- una scelta: come `ScrittoreSez.scegli33`, con le spinte sui segni medie fra globale e sezione
    def scegli33(self, lg, amm, S, k, rng, prima_riga, n_gl):
        SP, EOL = self.ctx.SP, self.ctx.EOL
        a = S.a
        sec = S.sec
        idx = np.asarray(amm)
        z = np.asarray(lg, float)[idx]
        prev, prev2, prev3 = S.prev, S.prev2, S.prev3
        G = S.G
        if k['w_cont'] > 0:
            g = (G[prev] + OS.KAPPA * self.T[prev]) / (G[prev].sum() + OS.KAPPA)
            term = k['w_cont'] * (self.logT[prev][idx] - np.log(np.maximum(g[idx], 1e-9)))
            if a > 0:
                Ts, logTs = self.tab.T2(sec)
                Gs = S.g2(sec)
                gs = (Gs[prev] + OS.KAPPA * Ts[prev]) / (Gs[prev].sum() + OS.KAPPA)
                z = z + ((1 - a) * term + a * (k['w_cont'] * (logTs[prev][idx] - np.log(np.maximum(gs[idx], 1e-9)))))
            else:
                z = z + term
        if k['w_tri'] > 0:
            kk = (prev2, prev)
            t3 = self.T3.get(kk)
            if t3 is not None:
                g3 = S.G3.get(kk)
                g3 = np.zeros(self.V) if g3 is None else g3
                gg = (g3 + OS.KAPPA * t3) / (g3.sum() + OS.KAPPA)
                term = k['w_tri'] * (self.logT3[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
                if a > 0:
                    ts, logts = self.tab.T3(sec, kk)
                    g3s = S.G3s.get((sec, kk))
                    g3s = np.zeros(self.V) if g3s is None else g3s
                    ggs = (g3s + OS.KAPPA * ts) / (g3s.sum() + OS.KAPPA)
                    z = z + ((1 - a) * term + a * (k['w_tri'] * (logts[idx] - np.log(np.maximum(ggs[idx], 1e-9)))))
                else:
                    z = z + term
        if k['w_quad'] > 0:
            kk = (prev3, prev2, prev)
            t4 = self.T4.get(kk)
            if t4 is not None:
                g4 = S.G4.get(kk)
                g4 = np.zeros(self.V) if g4 is None else g4
                gg = (g4 + OS.KAPPA * t4) / (g4.sum() + OS.KAPPA)
                term = k['w_quad'] * (self.logT4[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
                if a > 0:
                    ts, logts = self.tab.T4(sec, kk)
                    g4s = S.G4s.get((sec, kk))
                    g4s = np.zeros(self.V) if g4s is None else g4s
                    ggs = (g4s + OS.KAPPA * ts) / (g4s.sum() + OS.KAPPA)
                    z = z + ((1 - a) * term + a * (k['w_quad'] * (logts[idx] - np.log(np.maximum(ggs[idx], 1e-9)))))
                else:
                    z = z + term
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['b_nuove'] != 0.0 or (k['w_pag'] > 0 and S.pg)):
            self.pos[idx] = np.arange(len(idx))
            try:
                z = self._parole(z, idx, S, k, SP, EOL)
            finally:
                self.pos[idx] = -1
        dl = (idx == SP) | (idx == EOL)
        if not dl.any():                                                     # primo glifo
            s = int(idx[RS.Scrittore._glifo(z, k['T_riga'] if prima_riga else k['T_primo'], k['top_p'], rng)])
        elif dl.all():                                                       # solo delimitatori
            s = int(idx[0]) if len(idx) == 1 else int(idx[RS.Scrittore._due(z, k['T_eol'], rng)])
        else:
            m = RS.logsumexp(z[dl]) - RS.logsumexp(z[~dl])
            pe = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, m / k['T_fine']))))
            if rng.random() < pe:
                ii = np.nonzero(dl)[0]
                s = int(idx[ii[0]]) if len(ii) == 1 else int(idx[ii[RS.Scrittore._due(z[ii], k['T_eol'], rng)]])
            else:
                ii = np.nonzero(~dl)[0]
                s = int(idx[ii[RS.Scrittore._glifo(z[ii], k['T_int'], k['top_p'], rng)]])
        G[prev, s] += 1
        if a > 0:
            S.g2(sec)[prev, s] += 1
        if k['w_tri'] > 0:
            v3 = S.G3.get((prev2, prev))
            if v3 is None:
                v3 = S.G3[(prev2, prev)] = np.zeros(self.V)
            v3[s] += 1
            if a > 0:
                v3s = S.G3s.get((sec, (prev2, prev)))
                if v3s is None:
                    v3s = S.G3s[(sec, (prev2, prev))] = np.zeros(self.V)
                v3s[s] += 1
        if k['w_quad'] > 0:
            v4 = S.G4.get((prev3, prev2, prev))
            if v4 is None:
                v4 = S.G4[(prev3, prev2, prev)] = np.zeros(self.V)
            v4[s] += 1
            if a > 0:
                v4s = S.G4s.get((sec, (prev3, prev2, prev)))
                if v4s is None:
                    v4s = S.G4s[(sec, (prev3, prev2, prev))] = np.zeros(self.V)
                v4s[s] += 1
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['w_pag'] > 0):
            self._registra(S, s, SP, EOL)
        return s

    def pagina33(self, pen, rp, k, S, rng):
        S.sec = rp[0]['sezione']
        return super().pagina33(pen, rp, k, S, rng)

    def libro33(self, u, seme, fogli=None):
        """Un libro (o solo i fogli `fogli`) con le manopole `u` (cubo [0,1]^15, o ^14 con `a_sez` = 0). -> (lista (pagina, inizio, parole), manopole)."""
        k = da_cubo37(u)
        m, pen = self.penna(k['s'])
        rng = np.random.default_rng(seme)
        S = StatoLibro37(self.V)
        S.a = k['a_sez']
        ins = None if fogli is None else set(fogli)
        t = []
        for pag, rp in self.pp.items():
            if ins is not None and I7.foglio_di(pag) not in ins:
                continue
            t += self.pagina33(pen, rp, k, S, rng)
        self.ultimo_stato = S
        return t, k


if __name__ == '__main__':
    pass
