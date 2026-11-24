# -*- coding: utf-8 -*-
"""IA36, modulo di supporto: lo scrittore di IA35 (14 manopole di IA33 sopra la rete condizionata) con la MEMORIA DI SEZIONE (due manopole nuove: `w_sez`, `t_sez`).

In parole semplici
- `w_pag` (IA33) fa riprendere parole gia' scritte NELLA PAGINA; `w_sez` fa riprendere parole gia' scritte nelle PAGINE PRECEDENTI DELLA STESSA SEZIONE (e lingua) del libro che si sta scrivendo.
  La somiglianza fra pagine nasce dal libro che si scrive: la memoria legge solo parole gia' scritte (in questo libro), mai niente dal Voynich vero ne' dai fogli d'addestramento
  (quelli restano alla rete e alle tabelle, come prima). A fine pagina le sue parole entrano nella memoria della sezione; la pagina in corso non c'e' (c'e' `w_pag`).
- Come `w_pag` (approssimazione dichiarata del puntatore E2 di ia22): le parole scritte formano un albero dei prefissi; a ogni segno la distribuzione e' mescolata con quella delle parole della
  memoria che hanno lo stesso prefisso, con peso `w_sez x n / (n + NU_SEZ)` (n = quanto la memoria passa per quel prefisso, con il decadimento). Si applica PRIMA della ripresa dalla pagina.
- `t_sez`: lunghezza della memoria, in pagine della stessa sezione gia' scritte (2-60, scala logaritmica): una pagina scritta `d` pagine fa pesa exp(-d / t_sez).
- **Con `w_sez` = 0 lo scrittore da' ESATTAMENTE lo stesso libro di IA35** (stesso numero di estrazioni casuali, stesse parole): provato in `prudente_prove`.
- Manopole: le 14 di IA33 (`oracolo_scrittura`) + `w_sez` (0-0,8, zona piatta sotto 0,2 come `w_pag`) + `t_sez`; il cubo e' [0,1]^16. Il punto neutro ha `w_sez` = 0.
Variabili: NU_SEZ36 (2).
Nessun risultato e' scritto qui.
"""
import math
import os
import sys
from collections import Counter, OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import sezione_scrittura as SS  # noqa: E402

NU_SEZ = float(os.environ.get('NU_SEZ36', 2.0))
FINE = OS.FINE
NOMI36 = OS.NOMI33 + ('w_sez', 't_sez')
DIM36 = len(NOMI36)                              # 16
SEZ_MAX = 0.8
T_SEZ_LO, T_SEZ_HI = 2.0, 60.0
NEUTRO36 = OrderedDict(list(OS.NEUTRO33.items()) + [('w_sez', 0.0), ('t_sez', math.sqrt(T_SEZ_LO * T_SEZ_HI))])
U_SEZ_NEUTRO, U_T_NEUTRO = 0.1, 0.5
U_SEZ_PARTENZA = 0.2                              # al bordo della zona piatta: ogni passo verso l'alto accende la memoria


def da_cubo36(u):
    """u in [0,1]^16 (o 14: le ultime due neutre) -> le manopole (le 14 di IA33 piu' `w_sez` = min(0,8, max(0, u - 0,2)) e `t_sez` = 2 .. 60 pagine, scala logaritmica)."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    if len(u) == 14:
        u = np.concatenate([u, [U_SEZ_NEUTRO, U_T_NEUTRO]])
    k = OS.da_cubo33(u[:14])
    k['w_sez'] = float(min(SEZ_MAX, max(0.0, u[14] - 0.2)))
    k['t_sez'] = float(math.exp(math.log(T_SEZ_LO) + (math.log(T_SEZ_HI) - math.log(T_SEZ_LO)) * u[15]))
    return k


def neutro_cubo36():
    return np.concatenate([OS.neutro_cubo33(), [U_SEZ_NEUTRO, U_T_NEUTRO]])


def estendi_cubo(u14, w_sez=0.0, t_sez=None):
    """Un cubo a 14 manopole (IA33/IA35) -> cubo a 16 con la memoria di sezione a `w_sez` (0 = spenta: zona piatta, al bordo `U_SEZ_PARTENZA`) e `t_sez` (None = neutra)."""
    u = np.asarray(u14, float)
    if len(u) >= DIM36:
        return u[:DIM36].copy()
    a = U_SEZ_PARTENZA if not w_sez else min(1.0, 0.2 + float(w_sez))
    b = U_T_NEUTRO if t_sez is None else min(1.0, max(0.0, (math.log(t_sez) - math.log(T_SEZ_LO)) / (math.log(T_SEZ_HI) - math.log(T_SEZ_LO))))
    return np.concatenate([u, [a, b]])


def senza_memoria(u16):
    """Lo stesso punto con la memoria di sezione spenta (`w_sez` = 0): l'ablazione della memoria."""
    u = np.asarray(u16, float).copy()
    u[14] = min(u[14], 0.2)
    return u


def cubo_da_valori36(val):
    u = estendi_cubo(OS.cubo_da_valori(val))
    if val.get('w_sez', 0) > 0:
        u[14] = min(1.0, 0.2 + val['w_sez'])
    if 't_sez' in val:
        u[15] = min(1.0, max(0.0, (math.log(val['t_sez']) - math.log(T_SEZ_LO)) / (math.log(T_SEZ_HI) - math.log(T_SEZ_LO))))
    return u


class StatoLibro36(OS.StatoLibro):
    """Lo stato di un libro che si scrive: quello di IA33 piu' la memoria di sezione (chiave (sezione, lingua) -> albero dei prefissi con pesi, numero di pagine fuse)."""

    def __init__(self, V):
        super().__init__(V)
        self.sez = {}
        self.sez_n = {}
        self.chiave = None
        self.scal = 1.0
        self.gam = 1.0
        self.pagine_lette = []                      # per le prove: (chiave, n pagine della memoria) a ogni lettura


class ScrittoreSez(SS.ScrittoreCond):
    """Lo scrittore di IA35 con la memoria di sezione. `libro33(u, seme, fogli)` accetta 14 o 16 manopole."""

    # ---- la mescolanza con le parole di una memoria (come `w_pag` di IA33, con pesi decimali)
    def _mescola(self, z, idx, c, gam, SP, EOL):
        pos = self.pos
        pm = np.exp(z - z.max())
        pm /= pm.sum()
        q = np.zeros(len(idx))
        for g, cnt in c.items():
            if g == FINE:
                a, b = pos[SP], pos[EOL]
                if a >= 0 and b >= 0:
                    den = pm[a] + pm[b]
                    f = pm[a] / den if den > 0 else 0.5
                    q[a] += cnt * f
                    q[b] += cnt * (1 - f)
                elif a >= 0:
                    q[a] += cnt
                elif b >= 0:
                    q[b] += cnt
            else:
                j = pos[g]
                if j >= 0:
                    q[j] += cnt
        if q.sum() > 0:
            q /= q.sum()
            z = np.log(np.maximum((1 - gam) * pm + gam * q, 1e-300))
        return z

    def _sez_attiva(self, S, k):
        if k.get('w_sez', 0.0) <= 0.0 or S.chiave is None:
            return False
        return bool(S.sez.get(S.chiave))

    def _parole(self, z, idx, S, k, SP, EOL):
        if not self._sez_attiva(S, k):
            return super()._parole(z, idx, S, k, SP, EOL)
        k2 = dict(k)
        k2['w_pag'] = 0.0                                              # la parte di IA33 senza la ripresa dalla pagina (che si fa dopo la memoria di sezione)
        z = super()._parole(z, idx, S, k2, SP, EOL)
        pi = tuple(S.wid)
        c = S.sez[S.chiave].get(pi)
        if c:
            n = float(sum(c.values())) * S.scal
            gam = k['w_sez'] * n / (n + NU_SEZ)
            S.pagine_lette.append((S.chiave, S.sez_n[S.chiave]))
            z = self._mescola(z, idx, c, gam, SP, EOL)
        if k['w_pag'] > 0 and S.pg:
            c = S.pg.get(pi)
            if c:
                n = float(sum(c.values()))
                gam = k['w_pag'] * n / (n + OS.NU_PAG)
                z = self._mescola(z, idx, c, gam, SP, EOL)
        return z

    # ---- una scelta: come `ScrittoreL.scegli33`, con la memoria di sezione fra le cause che accendono la parte "parole" e la registrazione
    def scegli33(self, lg, amm, S, k, rng, prima_riga, n_gl):
        w_sez = k.get('w_sez', 0.0)
        SP, EOL = self.ctx.SP, self.ctx.EOL
        idx = np.asarray(amm)
        z = np.asarray(lg, float)[idx]
        prev, prev2, prev3 = S.prev, S.prev2, S.prev3
        G = S.G
        if k['w_cont'] > 0:
            g = (G[prev] + OS.KAPPA * self.T[prev]) / (G[prev].sum() + OS.KAPPA)
            z = z + k['w_cont'] * (self.logT[prev][idx] - np.log(np.maximum(g[idx], 1e-9)))
        if k['w_tri'] > 0:
            kk = (prev2, prev)
            t3 = self.T3.get(kk)
            if t3 is not None:
                g3 = S.G3.get(kk)
                g3 = np.zeros(self.V) if g3 is None else g3
                gg = (g3 + OS.KAPPA * t3) / (g3.sum() + OS.KAPPA)
                z = z + k['w_tri'] * (self.logT3[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
        if k['w_quad'] > 0:
            kk = (prev3, prev2, prev)
            t4 = self.T4.get(kk)
            if t4 is not None:
                g4 = S.G4.get(kk)
                g4 = np.zeros(self.V) if g4 is None else g4
                gg = (g4 + OS.KAPPA * t4) / (g4.sum() + OS.KAPPA)
                z = z + k['w_quad'] * (self.logT4[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['b_nuove'] != 0.0 or (k['w_pag'] > 0 and S.pg) or self._sez_attiva(S, k)):
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
        if k['w_tri'] > 0:
            v3 = S.G3.get((prev2, prev))
            if v3 is None:
                v3 = S.G3[(prev2, prev)] = np.zeros(self.V)
            v3[s] += 1
        if k['w_quad'] > 0:
            v4 = S.G4.get((prev3, prev2, prev))
            if v4 is None:
                v4 = S.G4[(prev3, prev2, prev)] = np.zeros(self.V)
            v4[s] += 1
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['w_pag'] > 0 or w_sez > 0):
            self._registra(S, s, SP, EOL)
        return s

    def _fonde_pagina(self, S, chiave, tau):
        """A fine pagina: le parole della pagina (albero dei prefissi `S.pg`) entrano nella memoria della sezione, con il peso che compensa il decadimento."""
        n = S.sez_n.get(chiave, 0)
        gamma = math.exp(-1.0 / tau)
        crescita = gamma ** (-n)
        mem = S.sez.setdefault(chiave, {})
        for pi, c in S.pg.items():
            t = mem.get(pi)
            if t is None:
                t = mem[pi] = Counter()
            for g, cnt in c.items():
                t[g] += cnt * crescita
        S.sez_n[chiave] = n + 1

    def _prepara_lettura(self, S, chiave, tau):
        S.chiave = chiave
        n = S.sez_n.get(chiave, 0)
        S.scal = math.exp(-1.0 * n / tau)                                    # gamma ** n
        S.gam = math.exp(-1.0 / tau)

    # ---- una pagina e un libro
    def pagina33(self, pen, rp, k, S, rng):
        voc, D, regole = self.voc, self.D, self.regole
        SP, EOL = self.ctx.SP, self.ctx.EOL
        w_sez = k.get('w_sez', 0.0)
        chiave = (rp[0]['sezione'], rp[0]['lingua'])
        if w_sez > 0:
            self._prepara_lettura(S, chiave, k['t_sez'])
        else:
            S.chiave = None
        pen.apri()
        S.nuova_pagina()
        lg = None
        for t in I7.testa_pagina(rp, voc):
            lg = pen.dai(t)
        out = []
        for j, x in enumerate(rp):
            for t in I7.testa_riga(x, j, voc, D):
                lg = pen.dai(t)
            S.nuova_riga(self.V)
            parole, lung, prima, fine = [], 0, 'inizio', False
            while not fine:
                parola = []
                S.wid = []
                while True:
                    amm = regole.ammessi(parola, lung, prima)
                    s = self.scegli33(lg, amm, S, k, rng, (not parole) and (not parola), len(parola))
                    S.prev3, S.prev2, S.prev = S.prev2, S.prev, s
                    lg = pen.dai(s)
                    if s == EOL:
                        parole.append(''.join(parola))
                        fine = True
                        break
                    lung += 1
                    if s == SP:
                        parole.append(''.join(parola))
                        S.prev_w = tuple(S.wid)
                        prima = 'spazio'
                        break
                    parola.append(regole.unita[s])
                    S.wid.append(s)
                    prima = 'segno'
            out.append((x['pagina'], x['ini'], parole))
        if w_sez > 0:
            self._fonde_pagina(S, chiave, k['t_sez'])
        return out

    def libro33(self, u, seme, fogli=None):
        """Un libro (o solo i fogli `fogli`) con le manopole `u` (cubo [0,1]^16, o ^14 con la memoria spenta). -> (lista (pagina, inizio, parole), manopole)."""
        k = da_cubo36(u)
        m, pen = self.penna(k['s'])
        rng = np.random.default_rng(seme)
        S = StatoLibro36(self.V)
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
