# -*- coding: utf-8 -*-
"""IA33, modulo di supporto: lo scrittore "piu' libero" (parte L): le 9 manopole di IA32 con intervalli piu' larghi, piu' cinque manopole nuove.

In parole semplici
- E' `rifare_scrittura.Scrittore` (importato senza modificarlo) con una scrittura piu' ricca. Tutto il resto (modello pieno con le due istantanee, temperature per posto,
  top-p, correzioni a conteggi sui bigrammi e sui trigrammi di segni, guardia anti-copia) e' come in IA32; con TUTTE le manopole a valore neutro la distribuzione dei segni
  e' esattamente quella della rete (provato in `oracolo_prove`).
- **Intervalli piu' larghi.** `w_cont` e `w_tri` (correzioni a conteggi sui bigrammi e sui trigrammi di segni) arrivano a 7,5 (IA32: 2,4, cioe' 3,1 volte tanto).
  **Nuova `w_quad`**: la stessa correzione sui quadrigrammi di segni (tre segni di contesto), stessa regola della correzione sui trigrammi.
- **Correzione a conteggi di PAROLE** (`w_uni`, `w_bi`, 0-3). Dai fogli d'addestramento si costruisce un albero dei prefissi delle parole (glifi): per ogni prefisso, quante
  parole (unigrammi) o quante parole dopo la parola prima (bigrammi) continuano con ogni glifo, o finiscono li'. La distribuzione di un glifo dato il prefisso e' esattamente
  quella che riscrive le frequenze delle parole intere (il prodotto lungo la parola e' la frequenza della parola; il bigramma e' interpolato con l'unigramma con peso fisso
  `LAMBDA_B33` = 1,5). La correzione e' la stessa di IA32: una spinta in logit `peso x (log tabella - log frequenza gia' scritta dal libro in corso)`, con una memoria
  di partenza `KAPPA_P33` = 40 contro la tabella. **Approssimazione dichiarata:** e' un controllo a retroazione sul libro scritto (spinge le frequenze delle parole verso
  quelle d'addestramento), non una ricampionatura esatta della parola; non cambia niente dove la parola e' ancora fuori dall'albero (parole nuove).
- **`b_nuove`** (-2..+2, neutro 0): un bonus (o una penalita') in logit per ogni segno che porta fuori dal lessico d'addestramento (un glifo che nessuna parola
  d'addestramento con quel prefisso ha, o la fine di una parola che non e' del lessico): alza o abbassa la quota di parole nuove.
- **`w_pag`** (0-0,8, neutro 0), "ripresa dalla pagina" (approssimazione dichiarata del puntatore E2 di ia22): le parole gia' scritte nella pagina formano un albero dei
  prefissi; a ogni segno la distribuzione della rete e' mescolata con quella delle parole della pagina che hanno lo stesso prefisso, con peso `w_pag x n / (n + 2)`
  (n = quante parole della pagina passano per quel prefisso). Serve a copia netta e G9 (il vocabolario della pagina).
- Con 14 manopole il cubo e' [0,1]^14 (`da_cubo33`); il neutro e' `neutro_cubo33()`; il punto di partenza di IA32 (`cubo_da_valori`) e' un modo di ricostruire il cubo da valori.
Variabili: KAPPA33 (memoria della correzione a segni, 300, come IA32), KAPPA_P33 (40), LAMBDA_B33 (1,5), NU_PAG33 (2).
"""
import math
import os
import sys
from collections import Counter, OrderedDict, defaultdict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import rifare_scrittura as RS  # noqa: E402

KAPPA = float(os.environ.get('KAPPA33', 300))
KAPPA_P = float(os.environ.get('KAPPA_P33', 40))
LAMBDA_B = float(os.environ.get('LAMBDA_B33', 1.5))
NU_PAG = float(os.environ.get('NU_PAG33', 2.0))
EPS = 1e-9
FINE = -1                                   # "la parola finisce qui" (spazio o fine riga) nell'albero dei prefissi
LS = ('^',)                                 # "la parola prima" a inizio riga

NOMI33 = ('T_primo', 'T_int', 'T_fine', 'T_eol', 'T_riga', 'top_p', 'w_cont', 'w_tri', 'w_quad', 's', 'w_uni', 'w_bi', 'b_nuove', 'w_pag')
DIM33 = len(NOMI33)
NEUTRO33 = OrderedDict([('T_primo', 1.0), ('T_int', 1.0), ('T_fine', 1.0), ('T_eol', 1.0), ('T_riga', 1.0), ('top_p', 1.0), ('w_cont', 0.0), ('w_tri', 0.0), ('w_quad', 0.0),
                        ('s', 0.0), ('w_uni', 0.0), ('w_bi', 0.0), ('b_nuove', 0.0), ('w_pag', 0.0)])
T_LO, T_HI = RS.T_LO, RS.T_HI
W_MAX = 7.5                                 # massimo di w_cont, w_tri, w_quad (IA32: 2,4)
W_PAROLE_MAX = 3.0
B_MAX = 2.0
PAG_MAX = 0.8


def da_cubo33(u):
    """Il vettore u in [0,1]^14 -> le manopole. Temperature: scala logaritmica 0,6-1,4 (neutro 1); top_p: 0,6 + 0,5 u saturato a 1; w_cont, w_tri, w_quad: 9,375 (u - 0,2) tagliato
    a zero sotto 0,2 (massimo 7,5); s: (u - 0,1) / 0,8 in [0,1]; w_uni e w_bi: 3,75 (u - 0,2) (massimo 3); b_nuove: 4 (u - 0,5) (-2..+2); w_pag: u - 0,2 (massimo 0,8)."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    T = lambda x: float(math.exp(math.log(T_LO) + (math.log(T_HI) - math.log(T_LO)) * x))
    zz = lambda x, c: float(max(0.0, c * (x - 0.2)))
    return OrderedDict([('T_primo', T(u[0])), ('T_int', T(u[1])), ('T_fine', T(u[2])), ('T_eol', T(u[3])), ('T_riga', T(u[4])), ('top_p', float(min(1.0, 0.6 + 0.5 * u[5]))),
                        ('w_cont', zz(u[6], W_MAX / 0.8)), ('w_tri', zz(u[7], W_MAX / 0.8)), ('w_quad', zz(u[8], W_MAX / 0.8)),
                        ('s', float(min(1.0, max(0.0, (u[9] - 0.1) / 0.8)))), ('w_uni', zz(u[10], W_PAROLE_MAX / 0.8)), ('w_bi', zz(u[11], W_PAROLE_MAX / 0.8)),
                        ('b_nuove', float(2 * B_MAX * (u[12] - 0.5))), ('w_pag', float(min(PAG_MAX, max(0.0, u[13] - 0.2))))])


def neutro_cubo33():
    t = lambda x: (math.log(x) - math.log(T_LO)) / (math.log(T_HI) - math.log(T_LO))
    return np.array([t(1.0)] * 5 + [0.9, 0.1, 0.1, 0.1, 0.05, 0.1, 0.1, 0.5, 0.1])


def cubo_da_valori(val):
    """Il cubo che rende i valori `val` (un dizionario di manopole; quelle che mancano restano neutre). Inverso di `da_cubo33` dove e' invertibile (fuori dalle zone piatte)."""
    u = neutro_cubo33().copy()
    t = lambda x: (math.log(min(max(x, T_LO), T_HI)) - math.log(T_LO)) / (math.log(T_HI) - math.log(T_LO))
    for i, n in enumerate(('T_primo', 'T_int', 'T_fine', 'T_eol', 'T_riga')):
        if n in val:
            u[i] = t(val[n])
    if 'top_p' in val:
        u[5] = min(1.0, max(0.0, (val['top_p'] - 0.6) / 0.5))
    for i, n, mx in ((6, 'w_cont', W_MAX), (7, 'w_tri', W_MAX), (8, 'w_quad', W_MAX), (10, 'w_uni', W_PAROLE_MAX), (11, 'w_bi', W_PAROLE_MAX)):
        if n in val and val[n] > 0:
            u[i] = min(1.0, 0.2 + val[n] / (mx / 0.8))
    if 's' in val:
        u[9] = min(1.0, max(0.0, 0.1 + 0.8 * val['s']))
    if 'b_nuove' in val:
        u[12] = min(1.0, max(0.0, 0.5 + val['b_nuove'] / (2 * B_MAX)))
    if 'w_pag' in val and val['w_pag'] > 0:
        u[13] = min(1.0, 0.2 + val['w_pag'])
    return u


# ---------------------------------------------------------------- tabelle di conteggi

def tabella_quadrigrammi(f_add):
    """Come `RS.tabella_trigrammi` ma con tre segni di contesto: (tre prima, due prima, uno prima) -> probabilita' (V) del segno di scrittura. Stati: V = inizio di riga."""
    voc = I7.vocabolario()
    primo = voc['primo_contenuto']
    V = len(voc['segni'])
    dp = I16.dati_pagine()
    ins = set(f_add)
    c = {}
    for d in dp.values():
        if d['foglio'] not in ins:
            continue
        tok = [int(x) for x in d['tok']]
        stato = [x if x >= primo else V for x in tok]
        for t in range(3, len(tok)):
            b = tok[t]
            if b < primo:
                continue
            k = (stato[t - 3], stato[t - 2], stato[t - 1])
            v = c.get(k)
            if v is None:
                v = c[k] = np.zeros(V)
            v[b] += 1
    out = {}
    for k, v in c.items():
        l = v + 0.05 * (v > 0)
        out[k] = l / l.sum()
    return out


class Nodo:
    """Un prefisso dell'albero dei prefissi: i glifi che lo continuano (id dei segni) e la fine; `T` = probabilita' (ultimo posto: la parola finisce)."""
    __slots__ = ('ids', 'T', 'conti', 'fine', 'indice')

    def __init__(self, conti):
        chiavi = sorted(k for k in conti if k != FINE)
        self.ids = np.array(chiavi, dtype=np.int64)
        c = np.array([conti[k] for k in chiavi] + [conti.get(FINE, 0)], float)
        self.conti = c
        self.T = c / c.sum()
        self.fine = conti.get(FINE, 0) > 0
        self.indice = {k: i for i, k in enumerate(chiavi)}


class Lessico:
    """Albero dei prefissi delle parole (glifi) dei fogli d'addestramento: unigrammi, e bigrammi (la parola prima nella stessa riga; `LS` a inizio riga)."""

    def __init__(self, f_add):
        voc = I7.vocabolario()
        primo = voc['primo_contenuto']
        SP, EOL = primo, primo + 1
        dp = I16.dati_pagine()
        ins = set(f_add)
        uni, bi = defaultdict(Counter), defaultdict(Counter)
        self.parole = Counter()
        for d in dp.values():
            if d['foglio'] not in ins:
                continue
            prev, cur = LS, []
            for t in d['tok']:
                t = int(t)
                if t < primo:
                    prev, cur = LS, []
                    continue
                if t == SP or t == EOL:
                    if cur:
                        w = tuple(cur)
                        self.parole[w] += 1
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

    def nodo_u(self, pi):
        n = self._nu.get(pi)
        if n is None and pi in self.uni:
            n = self._nu[pi] = Nodo(self.uni[pi])
        return n

    def nodo_b(self, prev, pi, nodo):
        """Probabilita' (come `Nodo.T`) delle continuazioni dopo `prev`, interpolate con l'unigramma (peso LAMBDA_B). None se `prev` non ha seguito con questo prefisso."""
        k = (prev, pi)
        if k in self._nb:
            return self._nb[k]
        c = self.bi.get(k)
        r = None
        if c is not None:
            cb = np.array([c.get(g, 0) for g in nodo.ids.tolist()] + [c.get(FINE, 0)], float)
            r = (cb + LAMBDA_B * nodo.T) / (cb.sum() + LAMBDA_B)
        self._nb[k] = r
        return r


class StatoLibro:
    """Lo stato di un libro che si scrive: conti correnti delle correzioni (a livello di libro) e della pagina."""

    def __init__(self, V):
        self.G = np.zeros((V + 1, V))
        self.G3, self.G4 = {}, {}
        self.Gu, self.Gb = {}, {}
        self.nuova_pagina()

    def nuova_pagina(self):
        self.pg = {}

    def nuova_riga(self, V):
        self.prev = self.prev2 = self.prev3 = V
        self.wid = []
        self.prev_w = LS


def _retro(T, G, w):
    """La spinta di retroazione: w x (log T - log g), g = (G + KAPPA_P T) / (somma G + KAPPA_P)."""
    g = (G + KAPPA_P * T) / (G.sum() + KAPPA_P)
    return w * (np.log(np.maximum(T, EPS)) - np.log(np.maximum(g, EPS)))


class ScrittoreL(RS.Scrittore):
    """Lo scrittore di IA33 (parte L)."""

    def __init__(self, cartella):
        super().__init__(cartella)
        self._tabelle_l(self.P.f_add)

    def _tabelle_l(self, f_add):
        self.T4 = tabella_quadrigrammi(f_add)
        self.logT4 = {k: np.log(np.maximum(v, 1e-9)) for k, v in self.T4.items()}
        self.lessico = Lessico(f_add)
        self.pos = np.full(self.V, -1, dtype=np.int64)

    # ---- le correzioni di parole
    def _parole(self, z, idx, S, k, SP, EOL):
        lex, pos = self.lessico, self.pos
        pi = tuple(S.wid)
        nodo = lex.nodo_u(pi)
        if nodo is not None:
            p = pos[nodo.ids]
            ok = p >= 0
            pf = (pos[SP], pos[EOL])
            sh = np.zeros(len(nodo.ids) + 1)
            if k['w_uni'] > 0:
                Gu = S.Gu.get(pi)
                if Gu is None:
                    Gu = S.Gu[pi] = np.zeros(len(nodo.T))
                sh += _retro(nodo.T, Gu, k['w_uni'])
            if k['w_bi'] > 0:
                tb = lex.nodo_b(S.prev_w, pi, nodo)
                if tb is not None:
                    kb = (S.prev_w, pi)
                    Gb = S.Gb.get(kb)
                    if Gb is None:
                        Gb = S.Gb[kb] = np.zeros(len(tb))
                    sh += _retro(tb, Gb, k['w_bi'])
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
                gam = k['w_pag'] * n / (n + NU_PAG)
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

    def _registra(self, S, s, SP, EOL):
        """Dopo la scelta del segno `s`: conti correnti dell'albero (retroazione) e della pagina; fine parola."""
        lex = self.lessico
        pi = tuple(S.wid)
        nodo = lex.nodo_u(pi)
        fine = (s == SP or s == EOL)
        if nodo is not None:
            j = len(nodo.T) - 1 if fine else nodo.indice.get(s)
            if j is not None and (not fine or nodo.fine):
                Gu = S.Gu.get(pi)
                if Gu is not None:
                    Gu[j] += 1
                Gb = S.Gb.get((S.prev_w, pi))
                if Gb is not None:
                    Gb[j] += 1
        if fine and S.wid:
            w = tuple(S.wid)
            for i in range(len(w)):
                c = S.pg.get(w[:i])
                if c is None:
                    c = S.pg[w[:i]] = Counter()
                c[w[i]] += 1
            c = S.pg.get(w)
            if c is None:
                c = S.pg[w] = Counter()
            c[FINE] += 1

    # ---- una scelta
    def scegli33(self, lg, amm, S, k, rng, prima_riga, n_gl):
        SP, EOL = self.ctx.SP, self.ctx.EOL
        idx = np.asarray(amm)
        z = np.asarray(lg, float)[idx]
        prev, prev2, prev3 = S.prev, S.prev2, S.prev3
        G = S.G
        if k['w_cont'] > 0:
            g = (G[prev] + KAPPA * self.T[prev]) / (G[prev].sum() + KAPPA)
            z = z + k['w_cont'] * (self.logT[prev][idx] - np.log(np.maximum(g[idx], 1e-9)))
        if k['w_tri'] > 0:
            kk = (prev2, prev)
            t3 = self.T3.get(kk)
            if t3 is not None:
                g3 = S.G3.get(kk)
                g3 = np.zeros(self.V) if g3 is None else g3
                gg = (g3 + KAPPA * t3) / (g3.sum() + KAPPA)
                z = z + k['w_tri'] * (self.logT3[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
        if k['w_quad'] > 0:
            kk = (prev3, prev2, prev)
            t4 = self.T4.get(kk)
            if t4 is not None:
                g4 = S.G4.get(kk)
                g4 = np.zeros(self.V) if g4 is None else g4
                gg = (g4 + KAPPA * t4) / (g4.sum() + KAPPA)
                z = z + k['w_quad'] * (self.logT4[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
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
            m = RS.logsumexp(z[dl]) - RS.logsumexp(z[~dl])                   # logit della probabilita' che la parola finisca
            pe = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, m / k['T_fine']))))
            if rng.random() < pe:
                ii = np.nonzero(dl)[0]
                s = int(idx[ii[0]]) if len(ii) == 1 else int(idx[ii[RS.Scrittore._due(z[ii], k['T_eol'], rng)]])
            else:
                ii = np.nonzero(~dl)[0]
                s = int(idx[ii[RS.Scrittore._glifo(z[ii], k['T_int'], k['top_p'], rng)]])
        # conti correnti
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
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['w_pag'] > 0):
            self._registra(S, s, SP, EOL)
        return s

    # ---- una pagina e un libro
    def pagina33(self, pen, rp, k, S, rng):
        voc, D, regole = self.voc, self.D, self.regole
        SP, EOL = self.ctx.SP, self.ctx.EOL
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
        return out

    def libro33(self, u, seme, fogli=None):
        """Un libro (o solo i fogli `fogli`) con le manopole `u` (cubo [0,1]^14). -> (lista (pagina, inizio, parole), manopole)."""
        k = da_cubo33(u)
        m, pen = self.penna(k['s'])
        rng = np.random.default_rng(seme)
        S = StatoLibro(self.V)
        ins = None if fogli is None else set(fogli)
        t = []
        for pag, rp in self.pp.items():
            if ins is not None and I7.foglio_di(pag) not in ins:
                continue
            t += self.pagina33(pen, rp, k, S, rng)
        return t, k


if __name__ == '__main__':
    pass
