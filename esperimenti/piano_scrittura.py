# -*- coding: utf-8 -*-
"""IA34, modulo di supporto: lo scrittore "con il piano del libro" (parte L di IA34).

In parole semplici
- E' lo scrittore di IA33 (`oracolo_scrittura.ScrittoreL`, importato senza modificarlo: modello pieno, temperature, correzioni a conteggi di segni e di parole, parole nuove,
  ripresa dalla pagina) con **tre manopole nuove** che portano nella scrittura la struttura su scala di sezione, di riga e di fine riga, e con i limiti delle correzioni sui
  segni portati da 7,5 a 15. Con tutte le manopole nuove a zero la scelta e' identica a quella di IA33 (provato in `piano_prove`: stessi numeri casuali, stesse scelte).
    m_sez    (0-0,8, neutro 0)  **sorgente di sezione**, come la sorgente S di IA27: all'inizio di ogni parola, con questa probabilita', la parola e' estratta dal vocabolario
                                 della sezione della pagina (sezione e lingua; frequenze dei fogli d'addestramento di quella sezione), glifo per glifo lungo l'albero dei prefissi:
                                 il prodotto delle probabilita' e' la frequenza della parola in quella sezione (estrazione esatta, non una retroazione). La rete non sceglie i glifi di
                                 quella parola, ma li legge (il suo stato avanza); fra spazio e fine riga, a parola finita, decide la rete. Se la sezione non ha fogli d'addestramento
                                 non fa niente. Serve a k90 (quanto contesto serve) e alla somiglianza di vocabolario fra pagine della stessa sezione.
    w_riga   (0-0,8, neutro 0)  **ripresa dalla riga sopra**: a ogni segno la distribuzione della rete e' mescolata con quella delle parole della riga sopra (stessa pagina) che stanno
                                 in posizione vicina (da 2 prima a 2 dopo quella della parola in corso) e hanno lo stesso prefisso, con peso `w_riga x n / (n + 2)`. E' la stessa
                                 mescolanza di `w_pag` ma ristretta alla riga sopra (IA27: eco 6-12 parole prima). Serve a Λ.
    w_fine   (0-3, neutro 0)    **fine riga**: quando una parola puo' finire, la scelta fra spazio e fine riga e' corretta con la retroazione a conteggi degli altri controlli, verso
                                 la frazione di volte in cui quella parola (o, se rara, il suo ultimo glifo) chiude una riga nei fogli d'addestramento. Serve ai bordi di fine riga.
  Il cubo e' [0,1]^17 (`da_cubo34`); il neutro e' `neutro_cubo34()`; `cubo_da_valori34` ricostruisce il cubo da valori (per partire dal punto scelto da IA33).
Variabili: NU_RIGA34 (2).
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
import rifare_scrittura as RS  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import piano_misure as PMS  # noqa: E402

NU_RIGA = float(os.environ.get('NU_RIGA34', 2.0))
FINE = OS.FINE
LS = OS.LS
NOMI34 = OS.NOMI33 + ('m_sez', 'w_riga', 'w_fine')
DIM34 = len(NOMI34)
NEUTRO34 = OrderedDict(list(OS.NEUTRO33.items()) + [('m_sez', 0.0), ('w_riga', 0.0), ('w_fine', 0.0)])
W_MAX34 = 15.0
SEZ_MAX, RIGA_MAX, FINE_MAX = 0.8, 0.8, 3.0
T_LO, T_HI = RS.T_LO, RS.T_HI


def da_cubo34(u):
    """u in [0,1]^17 -> manopole. Come `oracolo_scrittura.da_cubo33` ma w_cont, w_tri, w_quad arrivano a 15 (15 (u - 0,2) / 0,8 sopra 0,2); m_sez e w_riga: u - 0,2 (massimo 0,8);
    w_fine: 3,75 (u - 0,2) (massimo 3)."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    T = lambda x: float(math.exp(math.log(T_LO) + (math.log(T_HI) - math.log(T_LO)) * x))
    zz = lambda x, c: float(max(0.0, c * (x - 0.2)))
    return OrderedDict([('T_primo', T(u[0])), ('T_int', T(u[1])), ('T_fine', T(u[2])), ('T_eol', T(u[3])), ('T_riga', T(u[4])), ('top_p', float(min(1.0, 0.6 + 0.5 * u[5]))),
                        ('w_cont', zz(u[6], W_MAX34 / 0.8)), ('w_tri', zz(u[7], W_MAX34 / 0.8)), ('w_quad', zz(u[8], W_MAX34 / 0.8)),
                        ('s', float(min(1.0, max(0.0, (u[9] - 0.1) / 0.8)))), ('w_uni', zz(u[10], OS.W_PAROLE_MAX / 0.8)), ('w_bi', zz(u[11], OS.W_PAROLE_MAX / 0.8)),
                        ('b_nuove', float(2 * OS.B_MAX * (u[12] - 0.5))), ('w_pag', float(min(OS.PAG_MAX, max(0.0, u[13] - 0.2)))),
                        ('m_sez', float(min(SEZ_MAX, max(0.0, u[14] - 0.2)))), ('w_riga', float(min(RIGA_MAX, max(0.0, u[15] - 0.2)))), ('w_fine', zz(u[16], FINE_MAX / 0.8))])


def neutro_cubo34():
    return np.concatenate([OS.neutro_cubo33(), [0.1, 0.1, 0.1]])


def cubo_da_valori34(val):
    """Il cubo che rende i valori `val` (dizionario; le manopole che mancano restano neutre). Inverso di `da_cubo34` fuori dalle zone piatte."""
    u = neutro_cubo34().copy()
    t = lambda x: (math.log(min(max(x, T_LO), T_HI)) - math.log(T_LO)) / (math.log(T_HI) - math.log(T_LO))
    for i, n in enumerate(('T_primo', 'T_int', 'T_fine', 'T_eol', 'T_riga')):
        if n in val:
            u[i] = t(val[n])
    if 'top_p' in val:
        u[5] = min(1.0, max(0.0, (val['top_p'] - 0.6) / 0.5))
    for i, n, mx in ((6, 'w_cont', W_MAX34), (7, 'w_tri', W_MAX34), (8, 'w_quad', W_MAX34), (10, 'w_uni', OS.W_PAROLE_MAX), (11, 'w_bi', OS.W_PAROLE_MAX), (16, 'w_fine', FINE_MAX)):
        if n in val and val[n] > 0:
            u[i] = min(1.0, 0.2 + val[n] / (mx / 0.8))
    if 's' in val:
        u[9] = min(1.0, max(0.0, 0.1 + 0.8 * val['s']))
    if 'b_nuove' in val:
        u[12] = min(1.0, max(0.0, 0.5 + val['b_nuove'] / (2 * OS.B_MAX)))
    for i, n in ((13, 'w_pag'), (14, 'm_sez'), (15, 'w_riga')):
        if n in val and val[n] > 0:
            u[i] = min(1.0, 0.2 + val[n])
    return u


class LessicoSezione:
    """Alberi dei prefissi delle parole (in id di segni) per sezione (e lingua) dai fogli d'addestramento; e la tabella "questa parola chiude la riga?" (spazio / fine riga)."""

    def __init__(self, f_add):
        voc = I7.vocabolario()
        primo = voc['primo_contenuto']
        SP, EOL = primo, primo + 1
        dp = I16.dati_pagine()
        ch = PMS.chiavi_pagina()
        ins = set(f_add)
        uni = defaultdict(lambda: defaultdict(Counter))
        righe = []
        for d in dp.values():
            if d['foglio'] not in ins:
                continue
            k = ch.get(d['nome'])
            cur, linea = [], []
            for t in d['tok']:
                t = int(t)
                if t < primo:
                    cur, linea = [], []
                    continue
                if t == SP or t == EOL:
                    if cur:
                        w = tuple(cur)
                        linea.append(w)
                        if k is not None:
                            u = uni[k]
                            for i in range(len(w)):
                                u[w[:i]][w[i]] += 1
                            u[w][FINE] += 1
                        cur = []
                    if t == EOL:
                        righe.append(linea)
                        linea = []
                else:
                    cur.append(t)
        self.uni = {k: dict(v) for k, v in uni.items()}
        self.chiavi = set(self.uni)
        self._n = {}
        occ = Counter(w for r in righe for w in r)
        self.occ = occ
        cnt = defaultdict(lambda: [0.0, 0.0])
        for r in righe:
            for i, w in enumerate(r):
                cnt[self.chiave_fine(w)][1 if i == len(r) - 1 else 0] += 1
        self.tab_fine = {kk: np.array([(c[0] + 0.5) / (c[0] + c[1] + 1.0), (c[1] + 0.5) / (c[0] + c[1] + 1.0)]) for kk, c in cnt.items()}
        tot = np.array([sum(c[0] for c in cnt.values()), sum(c[1] for c in cnt.values())]) + 0.5
        self.fine_globale = tot / tot.sum()

    def chiave_fine(self, w):
        """La parola stessa se compare almeno 3 volte nei fogli d'addestramento, altrimenti il suo ultimo glifo."""
        return w if self.occ.get(w, 0) >= 3 else ('g', w[-1])

    def nodo(self, k, pi):
        kk = (k, pi)
        if kk in self._n:
            return self._n[kk]
        c = self.uni.get(k, {}).get(pi)
        n = OS.Nodo(c) if c else None
        self._n[kk] = n
        return n


class ScrittorePiano(OS.ScrittoreL):
    """Lo scrittore di IA34."""

    def __init__(self, cartella):
        super().__init__(cartella)
        self._piano(self.P.f_add)

    def _piano(self, f_add):
        self.sez = LessicoSezione(f_add)
        self.chiavi = PMS.chiavi_pagina()

    # ---- mescolanza con parole date (riga sopra)
    def _mescola(self, z, idx, cnt, gam, SP, EOL):
        pos = self.pos
        pm = np.exp(z - z.max())
        pm /= pm.sum()
        q = np.zeros(len(idx))
        for g, c in cnt.items():
            if g == FINE:
                a, b = pos[SP], pos[EOL]
                if a >= 0 and b >= 0:
                    den = pm[a] + pm[b]
                    f = pm[a] / den if den > 0 else 0.5
                    q[a] += c * f
                    q[b] += c * (1 - f)
                elif a >= 0:
                    q[a] += c
                elif b >= 0:
                    q[b] += c
            else:
                j = pos[g]
                if j >= 0:
                    q[j] += c
        if q.sum() <= 0:
            return z
        q /= q.sum()
        return np.log(np.maximum((1 - gam) * pm + gam * q, 1e-300))

    def _riga(self, z, idx, S, k, SP, EOL):
        j = len(S.riga_cur)
        pi = tuple(S.wid)
        n = len(pi)
        cnt = Counter()
        for c in S.riga_sopra[max(0, j - 2): j + 3]:
            if c[:n] == pi:
                cnt[c[n] if len(c) > n else FINE] += 1
        tot = sum(cnt.values())
        if not tot:
            return z
        return self._mescola(z, idx, cnt, k['w_riga'] * tot / (tot + NU_RIGA), SP, EOL)

    def _fine(self, z, idx, S, k, SP, EOL):
        w = tuple(S.wid)
        key = self.sez.chiave_fine(w)
        T = self.sez.tab_fine.get(key, self.sez.fine_globale)
        G = S.Ge.get(key)
        if G is None:
            G = S.Ge[key] = np.zeros(2)
        sh = OS._retro(T, G, k['w_fine'])
        z = z.copy()
        z[self.pos[SP]] += sh[0]
        z[self.pos[EOL]] += sh[1]
        return z

    def _da_sezione(self, z, idx, S, k, rng, SP, EOL):
        """Il segno scelto dalla sorgente di sezione, o None se non si puo' (la parola torna alla rete)."""
        nodo = self.sez.nodo(S.chiave, tuple(S.wid))
        if nodo is None:
            S.flag = False
            return None
        pos = self.pos
        p = pos[nodo.ids]
        ok = p >= 0
        pesi = np.where(ok, nodo.conti[:-1], 0.0)
        fine_ok = nodo.fine and (pos[SP] >= 0 or pos[EOL] >= 0)
        pf = nodo.conti[-1] if fine_ok else 0.0
        tot = float(pesi.sum() + pf)
        if tot <= 0:
            S.flag = False
            return None
        x = rng.random() * tot
        if x < pf:
            ii = [q for q in (pos[SP], pos[EOL]) if q >= 0]
            if len(ii) == 1:
                return int(idx[ii[0]])
            return int(idx[ii[RS.Scrittore._due(z[ii], k['T_eol'], rng)]])
        x -= pf
        cum = np.cumsum(pesi)
        i = min(int(np.searchsorted(cum, x, side='right')), len(cum) - 1)
        return int(nodo.ids[i])

    # ---- una scelta
    def scegli34(self, lg, amm, S, k, rng, prima_riga, n_gl):
        idx = np.asarray(amm)
        self.pos[idx] = np.arange(len(idx))
        try:
            return self._scegli34(lg, idx, S, k, rng, prima_riga)
        finally:
            self.pos[idx] = -1

    def _scegli34(self, lg, idx, S, k, rng, prima_riga):
        SP, EOL = self.ctx.SP, self.ctx.EOL
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
        if self.lessico is not None and (k['w_uni'] > 0 or k['w_bi'] > 0 or k['b_nuove'] != 0.0 or (k['w_pag'] > 0 and S.pg)):
            z = self._parole(z, idx, S, k, SP, EOL)
        if k['w_riga'] > 0 and S.riga_sopra:
            z = self._riga(z, idx, S, k, SP, EOL)
        e_fine = bool(S.wid) and self.pos[SP] >= 0 and self.pos[EOL] >= 0
        if k['w_fine'] > 0 and e_fine:
            z = self._fine(z, idx, S, k, SP, EOL)
        s = None
        if S.flag:
            s = self._da_sezione(z, idx, S, k, rng, SP, EOL)
        if s is None:
            dl = (idx == SP) | (idx == EOL)
            if not dl.any():
                s = int(idx[RS.Scrittore._glifo(z, k['T_riga'] if prima_riga else k['T_primo'], k['top_p'], rng)])
            elif dl.all():
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
        if k['w_fine'] > 0 and e_fine and (s == SP or s == EOL):
            key = self.sez.chiave_fine(tuple(S.wid))
            g = S.Ge.get(key)
            if g is None:
                g = S.Ge[key] = np.zeros(2)
            g[0 if s == SP else 1] += 1
        return s

    # ---- una pagina e un libro
    def pagina34(self, pen, rp, k, S, rng):
        voc, D, regole = self.voc, self.D, self.regole
        SP, EOL = self.ctx.SP, self.ctx.EOL
        pen.apri()
        S.nuova_pagina()
        S.riga_sopra = []
        S.chiave = self.chiavi.get(rp[0]['pagina'])
        sezione_attiva = k['m_sez'] > 0 and S.chiave in self.sez.chiavi
        lg = None
        for t in I7.testa_pagina(rp, voc):
            lg = pen.dai(t)
        out = []
        for j, x in enumerate(rp):
            for t in I7.testa_riga(x, j, voc, D):
                lg = pen.dai(t)
            S.nuova_riga(self.V)
            S.riga_cur = []
            parole, lung, prima, fine = [], 0, 'inizio', False
            while not fine:
                parola = []
                S.wid = []
                S.flag = bool(sezione_attiva and rng.random() < k['m_sez'])
                while True:
                    amm = regole.ammessi(parola, lung, prima)
                    s = self.scegli34(lg, amm, S, k, rng, (not parole) and (not parola), len(parola))
                    S.prev3, S.prev2, S.prev = S.prev2, S.prev, s
                    lg = pen.dai(s)
                    if s == EOL:
                        parole.append(''.join(parola))
                        S.riga_cur.append(tuple(S.wid))
                        fine = True
                        break
                    lung += 1
                    if s == SP:
                        parole.append(''.join(parola))
                        S.prev_w = tuple(S.wid)
                        S.riga_cur.append(S.prev_w)
                        prima = 'spazio'
                        break
                    parola.append(regole.unita[s])
                    S.wid.append(s)
                    prima = 'segno'
            S.riga_sopra = S.riga_cur
            out.append((x['pagina'], x['ini'], parole))
        return out

    def libro34(self, u, seme, fogli=None):
        """Un libro (o solo i fogli `fogli`) con le manopole `u` (cubo [0,1]^17). -> (lista (pagina, inizio, parole), manopole)."""
        k = da_cubo34(u)
        m, pen = self.penna(k['s'])
        rng = np.random.default_rng(seme)
        S = OS.StatoLibro(self.V)
        S.Ge = {}
        ins = None if fogli is None else set(fogli)
        t = []
        for pag, rp in self.pp.items():
            if ins is not None and I7.foglio_di(pag) not in ins:
                continue
            t += self.pagina34(pen, rp, k, S, rng)
        return t, k


if __name__ == '__main__':
    pass
