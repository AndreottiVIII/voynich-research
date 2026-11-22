# -*- coding: utf-8 -*-
"""Supporto di ia27 (modulo, non e' un esperimento): il modello esplicito "a sorgenti latenti", senza reti, stimato a massima verosimiglianza (EM).

Che cosa fa il modello, in parole semplici
A ogni parola il modello sceglie in segreto una "sorgente" fra cinque, e la parola viene da li':
  L  lessico generale: una parola gia' vista altrove (frequenza), con il fattore di contatto;
  S  lessico di sezione: una parola vista nello stesso gruppo (sezione, lingua), con il fattore di contatto;
  F  forma: una parola inventata da un modello di forma (trigrammi di glifi), con il fattore di contatto;
  R  riga: una parola della riga in corso o di quella sopra (uguale, o con un ritocco di un glifo);
  P  pagina: una parola del resto della pagina (righe piu' su di una), uguale o con un ritocco.
Il "contatto" e' un fattore che premia un primo glifo adatto all'ultimo glifo della parola prima (come ia08). Per R e P, la scelta della parola da
ricopiare dipende dalla distanza (il "nucleo": un peso per ogni classe di distanza) e dalla frequenza della parola (un peso per classe di frequenza) e il ritocco ha un tipo (uguale, glifo cambiato, aggiunto, tolto),
un posto (primo, interno, ultimo glifo) e un glifo nuovo. Lo spazio fra parole (e la fine riga) sta in un rischio a parte, uguale per tutte le versioni.
Tutti i parametri si stimano con l'algoritmo EM sulle pagine di addestramento. Per non far vincere per forza il lessico delle pagine stesse, i
lessici L, S e F delle pagine di addestramento sono "a incrocio": calcolati sugli altri gruppi di fogli (`n_inner`), mai sul gruppo della pagina.
Su pagine nuove si usano i lessici di tutte le pagine di addestramento.
Le versioni (`VARIANTI`) tolgono un pezzo per volta. Nessuna parola del manoscritto compare in questo file e nessun risultato e' scritto qui.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import sorgenti_dati as SD  # noqa: E402
import rifarlo_ritocchi as RR  # noqa: E402

SORGENTI = ('L', 'S', 'F', 'R', 'P')
NOMI_SORGENTI = OrderedDict([('L', 'lessico generale'), ('S', 'lessico di sezione'), ('F', 'forma (parola inventata)'),
                             ('R', 'riga (in corso o sopra)'), ('P', 'resto della pagina')])
TIPI = ('uguale', 'cambia', 'aggiunge', 'toglie')
EDGES_D = np.array([1, 2, 3, 4, 5, 6, 8, 10, 13, 17, 23, 31])      # classi di distanza in parole (R)
NB = len(EDGES_D)
KR = 2 * NB                                                         # classi di R: (stessa riga / riga sopra) x distanza
KP = 5                                                              # classi di P: righe piu' su 2, 3, 4, 5-6, 7 o piu'
NF = 3                                                              # classi di frequenza della parola ricopiata: 20 piu' frequenti, fino alla 200-esima, altre
FREQ_TOP = (20, 200)
MIN_S = 200                                                         # parole minime del gruppo (sezione, lingua) perche' S esista
SOGLIA_G = (0.02, 50.0)                                             # il fattore di contatto sta fra questi due valori
EPS_P = 1e-300


def etichetta_classe_R(k):
    rel, b = divmod(k, NB)
    lo = int(EDGES_D[b])
    hi = int(EDGES_D[b + 1]) - 1 if b + 1 < NB else None
    return '%s, %s' % ('riga in corso' if rel == 0 else 'riga sopra', ('%d' % lo if hi == lo else '%d-%d' % (lo, hi)) if hi else '%d o piu\'' % lo) + ' parole prima'


ETICHETTE_P = ['2 righe sopra', '3 righe sopra', '4 righe sopra', '5-6 righe sopra', '7 o piu\' righe sopra']


def bin_P(rr):
    return 0 if rr == 2 else 1 if rr == 3 else 2 if rr == 4 else 3 if rr <= 6 else 4


class Voc(object):
    """I glifi (unita' del libro) e il contesto del contatto: 0..G-1 ultimo glifo della parola prima, G inizio riga, G+1 inizio paragrafo."""

    def __init__(self, unita):
        self.unita = list(unita)
        self.gid = {u: i for i, u in enumerate(self.unita)}
        self.G = len(self.unita)
        self.Cx = self.G + 2


def lingua_gruppo(l):
    return 0 if l == 'A' else 1 if l == 'B' else 2


# ---------------------------------------------------------------- il testo come tabelle di numeri

class Corpus(object):
    """Un insieme di pagine come vettori per parola: glifi, contesto, fascia, lunghezza raggiunta, gruppi. `rischio` (SD.Rischio) da' i bit di fine parola."""

    def __init__(self, pagine, voc, rischio, gruppi_sl, hid_di_foglio=None, hid_default=0):
        self.pagine, self.voc = pagine, voc
        P = voc
        par_s, ids, ctx, fi, la, ln, band, lg, sg, hid, riga, riga_loc, pag = [], [], [], [], [], [], [], [], [], [], [], [], []
        stop_bit, self.pag_ini, self.riga_ini, nrow = 0.0, [], [], 0
        self.bits_stop = []
        for pi, p in enumerate(pagine):
            self.pag_ini.append(len(par_s))
            for ri, r in enumerate(p.righe):
                self.riga_ini.append(len(par_s))
                cum = -1
                for k, w in enumerate(r.parole):
                    par_s.append(tuple(w))
                    ids.append(tuple(P.gid[g] for g in w))
                    ctx.append(P.G + (1 if r.ini else 0) if k == 0 else P.gid[r.parole[k - 1][-1]])
                    fi.append(P.gid[w[0]])
                    la.append(P.gid[w[-1]])
                    ln.append(len(w))
                    band.append(r.banda)
                    cum += len(w) + (1 if k else 0)
                    self.bits_stop.append(rischio.bit(r.banda, cum, k == len(r.parole) - 1))
                    lg.append(lingua_gruppo(p.lingua))
                    sg.append(gruppi_sl.get((p.sezione, p.lingua), -1))
                    hid.append(hid_di_foglio.get(p.foglio, hid_default) if hid_di_foglio else hid_default)
                    riga.append(nrow)
                    riga_loc.append(ri)
                    pag.append(pi)
                nrow += 1
        self.parole, self.ids = par_s, ids
        self.T, self.NR = len(par_s), nrow
        a = np.array
        self.ctx, self.fi, self.la, self.ln, self.band = a(ctx, dtype=np.int64), a(fi, dtype=np.int64), a(la, dtype=np.int64), a(ln, dtype=np.int64), a(band)
        self.lg, self.sg, self.hid, self.riga, self.riga_loc, self.pag = a(lg), a(sg), a(hid), a(riga), a(riga_loc), a(pag)
        self.bits_stop = np.array(self.bits_stop)
        self.n_segni = float((self.ln + 1).sum())
        self.pag_ini.append(self.T)
        self.riga_ini.append(self.T)


# ---------------------------------------------------------------- i lessici L, S, F (a incrocio sulle pagine di addestramento)

class Basi(object):
    """Lessici di L, S, F. h in 0..n_inner-1: lessico senza il gruppo h di fogli (per le pagine di addestramento di quel gruppo); h = n_inner: lessico
    pieno (per le pagine nuove). Le parole sono tuple di glifi (stringhe)."""

    def __init__(self, pagine_add, voc, n_inner=10, seme=1, forma_su='tipi'):
        self.voc, self.H = voc, n_inner
        fogli = sorted({p.foglio for p in pagine_add})
        rnd = random.Random(seme)
        rnd.shuffle(fogli)
        self.hid_di_foglio = {f: i % n_inner for i, f in enumerate(fogli)}
        self.gruppi_sl = OrderedDict()
        for p in pagine_add:
            self.gruppi_sl.setdefault((p.sezione, p.lingua), len(self.gruppi_sl))
        SG, G, H = max(len(self.gruppi_sl), 1), voc.G, n_inner
        self.SG = SG
        cT, cG = Counter(), [Counter() for _ in range(H)]
        sT, sG = [Counter() for _ in range(SG)], [[Counter() for _ in range(SG)] for _ in range(H)]
        fT, fG = np.zeros(G), np.zeros((H, G))
        fsT, fsG = np.zeros((SG, G)), np.zeros((H, SG, G))
        for p in pagine_add:
            h, s = self.hid_di_foglio[p.foglio], self.gruppi_sl[(p.sezione, p.lingua)]
            for r in p.righe:
                for w in r.parole:
                    cT[w] += 1
                    cG[h][w] += 1
                    sT[s][w] += 1
                    sG[h][s][w] += 1
                    g = voc.gid[w[0]]
                    fT[g] += 1
                    fG[h, g] += 1
                    fsT[s, g] += 1
                    fsG[h, s, g] += 1
        self.cT, self.cG, self.sT, self.sG = cT, cG, sT, sG
        self.rango = {w: i for i, (w, _) in enumerate(sorted(cT.items(), key=lambda x: (-x[1], x[0])))}
        self.NL = np.array([sum(cT.values()) - sum(cG[h].values()) for h in range(H)] + [sum(cT.values())], dtype=float)
        self.NS = np.zeros((H + 1, SG))
        for s in range(SG):
            tot = sum(sT[s].values())
            for h in range(H):
                self.NS[h, s] = tot - sum(sG[h][s].values())
            self.NS[H, s] = tot
        self.ML = np.zeros((H + 1, G))                     # marginale del primo glifo nel lessico L
        self.MS = np.zeros((H + 1, SG, G))
        for h in range(H):
            self.ML[h] = (fT - fG[h]) / max(self.NL[h], 1.0)
            for s in range(SG):
                self.MS[h, s] = (fsT[s] - fsG[h, s]) / max(self.NS[h, s], 1.0)
        self.ML[H] = fT / max(self.NL[H], 1.0)
        for s in range(SG):
            self.MS[H, s] = fsT[s] / max(self.NS[H, s], 1.0)
        # forma: trigrammi di glifi sui tipi (default) o sulle occorrenze, senza il gruppo h
        self.formas, self.MF = [], np.zeros((H + 1, G))
        for h in range(H + 1):
            if forma_su == 'tipi':
                tipi = [w for w, c in cT.items() if (c - (cG[h][w] if h < H else 0)) > 0]
                cnt = Counter({w: 1 for w in tipi})
            else:
                cnt = Counter({w: c - (cG[h][w] if h < H else 0) for w, c in cT.items() if c - (cG[h][w] if h < H else 0) > 0})
            fm = RR.Forma(cnt)
            self.formas.append(fm)
            for g, u in enumerate(voc.unita):
                j = fm.idx.get(u)
                self.MF[h, g] = 2.0 ** float(fm.l3[fm.q, fm.q, j]) if j is not None else 0.0

    def bucket(self, w):
        """Classe di frequenza di una parola (nel lessico di addestramento): 0 fra le 20 piu' frequenti, 1 fino alla 200-esima, 2 le altre (e le mai viste)."""
        r = self.rango.get(w)
        return 0 if r is not None and r < FREQ_TOP[0] else 1 if r is not None and r < FREQ_TOP[1] else 2

    def conteggio_L(self, w, h):
        return self.cT.get(w, 0) - (self.cG[h].get(w, 0) if h < self.H else 0)

    def conteggio_S(self, w, h, s):
        return self.sT[s].get(w, 0) - (self.sG[h][s].get(w, 0) if h < self.H else 0)

    def riempi(self, c):
        """Probabilita' di base (senza contatto) per ogni parola di un Corpus: baseL, baseS, baseF; vS = il gruppo ha abbastanza parole."""
        T = c.T
        c.baseL, c.baseS, c.baseF = np.zeros(T), np.zeros(T), np.zeros(T)
        c.vS = np.zeros(T, dtype=bool)
        for t in range(T):
            h, s, w = int(c.hid[t]), int(c.sg[t]), c.parole[t]
            c.baseL[t] = self.conteggio_L(w, h) / self.NL[h]
            if s >= 0 and self.NS[h, s] >= MIN_S:
                c.vS[t] = True
                c.baseS[t] = self.conteggio_S(w, h, s) / self.NS[h, s]
            c.baseF[t] = 2.0 ** (-self.formas[h].bit(w))


# ---------------------------------------------------------------- parametri

class Par(object):
    """Tutti i parametri del modello (numeri; nessuna parola)."""

    def __init__(self, voc, variante):
        G, Cx = voc.G, voc.Cx
        self.G, self.Cx = G, Cx
        self.pi = np.tile(np.array([0.35, 0.20, 0.15, 0.20, 0.10]), (3, 1))
        for s, nome in enumerate(SORGENTI):
            if not variante['usa'][nome]:
                self.pi[:, s] = 0.0
        self.pi /= self.pi.sum(1, keepdims=True)
        self.kR, self.kP = np.ones(KR), np.ones(KP)
        self.phiR, self.phiP = np.ones(NF), np.ones(NF)       # peso della classe di frequenza della parola ricopiata
        self.rho = np.tile(np.array([0.55, 0.25, 0.10, 0.10]), (2, 1))
        if not variante['ritocco']:
            self.rho = np.tile(np.array([1.0, 0.0, 0.0, 0.0]), (2, 1))
        self.omega = np.ones((3, 3))                         # (cambia, aggiunge, toglie) x (primo, interno, ultimo)
        self.tau = np.full((2, 2, Cx, G), 1.0 / G)           # (cambia, aggiunge) x (primo posto, altri) x contesto x glifo nuovo
        self.ref = np.full(G, 1.0 / G)                       # primo glifo, frequenza di tutte le parole
        self.pc = np.full((Cx, G), 1.0 / G)                  # P(primo glifo | contesto) delle parole fresche (L, S, F)
        self.g = np.ones((Cx, G))                            # fattore di contatto pc / ref
        self.gamma_R = float(variante['gamma'])
        self.gamma_P = float(variante['gamma'])
        self.ll = []

    def copia(self):
        import copy
        return copy.deepcopy(self)


def variante(nome=None, **kw):
    """Una versione del modello: quali sorgenti, contatto, ritocco, nucleo, frequenza (peso della classe di frequenza della parola ricopiata: di norma spenta,
    vedi `con_frequenza`), contatto sulla copia, lingue separate."""
    v = dict(nome=nome or 'pieno', usa={s: True for s in SORGENTI}, contatto=True, ritocco=True, nucleo_piatto=False, gamma=0.0,
             ritocco_contatto=False, pi_per_lingua=True, frequenza=False)
    v.update(kw)
    return v


def varianti():
    V = OrderedDict()
    V['pieno'] = variante('pieno')
    V['senza_R'] = variante('senza_R', usa=dict(L=1, S=1, F=1, R=0, P=1))
    V['senza_P'] = variante('senza_P', usa=dict(L=1, S=1, F=1, R=1, P=0))
    V['senza_S'] = variante('senza_S', usa=dict(L=1, S=0, F=1, R=1, P=1))
    V['senza_copia'] = variante('senza_copia', usa=dict(L=1, S=1, F=1, R=0, P=0))
    V['nucleo_piatto'] = variante('nucleo_piatto', nucleo_piatto=True)
    V['senza_contatto'] = variante('senza_contatto', contatto=False)
    V['senza_ritocco'] = variante('senza_ritocco', ritocco=False)
    V['con_frequenza'] = variante('con_frequenza', frequenza=True)
    V['solo_lessico'] = variante('solo_lessico', usa=dict(L=1, S=0, F=1, R=0, P=0), contatto=False)
    V['copia_con_contatto'] = variante('copia_con_contatto', gamma=1.0)
    V['ritocco_con_contatto'] = variante('ritocco_con_contatto', ritocco_contatto=True)
    return V


# ---------------------------------------------------------------- il calcolo su un Corpus

def _classe_R(t, j, riga_ini_t):
    rel = 0 if j >= riga_ini_t else 1
    return rel * NB + int(np.searchsorted(EDGES_D, t - j, side='right')) - 1


def _cnt_pos(tipo, n):
    """Quante posizioni per classe (primo, interno, ultimo) per un ritocco di tipo 1 (cambia), 2 (aggiunge), 3 (toglie) su una parola di n glifi."""
    if tipo == 2:
        return (1.0, float(n - 1), 1.0)
    return (1.0, 0.0, 0.0) if n == 1 else (1.0, float(n - 2), 1.0)


def _mm_fattore(S, E, old, cnt):
    """Passo MM di un fattore di scelta (nucleo o frequenza): S = scelte attese, E = esposizione, `cnt` = quante parole candidate in ogni classe. Media
    pesata in scala logaritmica con il valore medio delle classi con dati (3 scelte di peso), poi la media dei candidati e' riportata a 1."""
    raw = np.where(E > 0, S / np.maximum(E, EPS_P), old)
    lam = S / (S + 3.0)
    valid = S > 0
    logmed = float((np.log(np.maximum(raw[valid], 1e-12)) * S[valid]).sum() / max(S[valid].sum(), 1e-9)) if valid.any() else 0.0
    nk = np.exp(lam * np.log(np.maximum(raw, 1e-12)) + (1 - lam) * logmed)
    return nk / max(float((cnt * nk).sum() / max(cnt.sum(), 1.0)), 1e-12)


class Calcolo(object):
    """Probabilita' e statistiche EM di un Corpus, dati i parametri. Costruito una volta (eventi e candidati sono senza parametri)."""

    def __init__(self, corpus, basi, var, peso=None):
        self.c, self.basi, self.var = corpus, basi, var
        self.voc = corpus.voc
        basi.riempi(corpus)
        c = corpus
        self.peso = np.ones(c.T) if peso is None else peso
        self.sgz = np.clip(c.sg, 0, None)
        self.bk = np.array([basi.bucket(w) for w in c.parole], dtype=np.int64)
        self._copia()

    def _copia(self):
        c, G = self.c, self.voc.G
        ev = defaultdict(list)
        cand_t, cand_k, cand_f, cand_b = [], [], [], []
        CP = np.zeros((c.NR, KP, NF, G))
        nR, nP = np.zeros(c.T), np.zeros(c.T)
        for p in range(len(c.pagine)):
            a, b = c.pag_ini[p], c.pag_ini[p + 1]
            if a == b:
                continue
            r0 = c.riga[a]
            r1 = c.riga[b - 1]
            hist = {}
            for r in range(r0, r1 + 1):
                h = np.zeros((NF, G))
                lo, hi = c.riga_ini[r], c.riga_ini[r + 1]
                for j in range(lo, hi):
                    h[self.bk[j], c.fi[j]] += 1
                hist[r] = h
            for r in range(r0 + 2, r1 + 1):
                for r2 in range(r0, r - 1):
                    CP[r, bin_P(r - r2)] += hist[r2]
            d_eq, d_sub, d_del = defaultdict(list), defaultdict(list), defaultdict(list)
            for t in range(a, b):
                w = c.ids[t]
                n = len(w)
                r = c.riga[t]
                rini = c.riga_ini[r]
                lo = c.riga_ini[r - 1] if r > r0 else rini
                if t > lo:
                    j = np.arange(lo, t)
                    rel = (j < rini).astype(np.int64)
                    k = rel * NB + np.searchsorted(EDGES_D, t - j, side='right') - 1
                    cand_t.append(np.full(len(j), t, dtype=np.int64))
                    cand_k.append(k)
                    cand_f.append(c.fi[j])
                    cand_b.append(self.bk[j])
                    nR[t] = len(j)
                nP[t] = CP[r].sum()

                def aggiungi(j, tipo, pos, n_c, g, ci):
                    if j >= lo:
                        src, k = 0, _classe_R(t, j, rini)
                    else:
                        src, k = 1, bin_P(r - int(c.riga[j]))
                    if tipo == 0:
                        pc = 1
                    elif tipo == 2:
                        pc = 0 if pos == 0 else 2 if pos == n_c else 1
                    else:
                        pc = 0 if pos == 0 else 2 if pos == n_c - 1 else 1
                    e = ev
                    e['t'].append(t); e['src'].append(src); e['k'].append(k); e['tipo'].append(tipo); e['pc'].append(pc)
                    e['n'].append(n_c); e['g'].append(g); e['ci'].append(ci); e['fj'].append(int(c.fi[j])); e['b'].append(int(self.bk[j]))
                for j in d_eq.get(w, ()):
                    aggiungi(j, 0, 0, n, -1, -1)
                for i in range(n):
                    for j in d_sub.get((i, w[:i], w[i + 1:]), ()):
                        cj = c.ids[j]
                        if cj[i] != w[i]:
                            aggiungi(j, 1, i, n, w[i], cj[i])
                if n >= 2:
                    for i in range(n):
                        for j in d_eq.get(w[:i] + w[i + 1:], ()):
                            aggiungi(j, 2, i, n - 1, w[i], -1)
                for j, i in d_del.get(w, ()):
                    aggiungi(j, 3, i, len(c.ids[j]), -1, -1)
                d_eq[w].append(t)
                for i in range(n):
                    d_sub[(i, w[:i], w[i + 1:])].append(t)
                if n >= 2:
                    for i in range(n):
                        d_del[w[:i] + w[i + 1:]].append((t, i))
        E = {k: np.array(v, dtype=np.int64) for k, v in ev.items()}
        for k in ('t', 'src', 'k', 'tipo', 'pc', 'n', 'g', 'ci', 'fj', 'b'):
            E.setdefault(k, np.zeros(0, dtype=np.int64))
        self.E = E
        self.ev_cnt = np.array([_cnt_pos(int(tp), int(n)) if tp else (0.0, 0.0, 0.0) for tp, n in zip(E['tipo'], E['n'])]).reshape(-1, 3)
        self.cand_t = np.concatenate(cand_t) if cand_t else np.zeros(0, dtype=np.int64)
        self.cand_k = np.concatenate(cand_k) if cand_k else np.zeros(0, dtype=np.int64)
        self.cand_f = np.concatenate(cand_f) if cand_f else np.zeros(0, dtype=np.int64)
        self.cand_b = np.concatenate(cand_b) if cand_b else np.zeros(0, dtype=np.int64)
        self.CP, self.vR, self.vP = CP, nR > 0, nP > 0

    # ---- probabilita' delle sorgenti
    def _componenti(self, par, vincoli=None):
        c, b, H = self.c, self.basi, self.basi.H
        T = c.T
        g = par.g
        f, ctx, hid, sg = c.fi, c.ctx, c.hid, self.sgz
        gv = g[ctx, f]
        ZL = b.ML @ g.T                                   # (H+1, Cx)
        ZS = np.einsum('hsg,cg->hsc', b.MS, g)           # (H+1, SG, Cx)
        ZF = b.MF @ g.T
        PL = c.baseL * gv / np.maximum(ZL[hid, ctx], EPS_P)
        PS = np.where(c.vS, c.baseS * gv / np.maximum(ZS[hid, sg, ctx], EPS_P), 0.0)
        PF = c.baseF * gv / np.maximum(ZF[hid, ctx], EPS_P)
        # copia: R e P
        ggR = np.clip(g, *SOGLIA_G) ** par.gamma_R
        ggP = np.clip(g, *SOGLIA_G) ** par.gamma_P
        E = self.E
        wR = par.kR[self.cand_k] * par.phiR[self.cand_b] * ggR[ctx[self.cand_t], self.cand_f]
        DR = np.bincount(self.cand_t, weights=wR, minlength=T)
        W = np.tensordot(par.phiP, np.tensordot(par.kP, self.CP, axes=(0, 1)), axes=(0, 1))     # (NR, G)
        DP = (W[c.riga] * ggP[ctx]).sum(1)
        DRs, DPs = np.where(DR > 0, DR, 1.0), np.where(DP > 0, DP, 1.0)
        src, k, tp, pc, n, gl, ci, fj, et, bb = E['src'], E['k'], E['tipo'], E['pc'], E['n'], E['g'], E['ci'], E['fj'], E['t'], E['b']
        isR = src == 0
        kap = np.where(isR, par.kR[np.minimum(k, KR - 1)] * par.phiR[bb], par.kP[np.minimum(k, KP - 1)] * par.phiP[bb])
        gg_e = np.where(isR, ggR[ctx[et], fj], ggP[ctx[et], fj])
        q = kap * gg_e / np.where(isR, DRs[et], DPs[et])
        rho = par.rho[src, tp]
        om_e = par.omega[np.maximum(tp - 1, 0), pc]
        Om = (par.omega[np.maximum(tp - 1, 0)] * self.ev_cnt).sum(1)
        pos = np.where(tp == 0, 1.0, om_e / np.maximum(Om, EPS_P))
        ct = ctx[et] if self.var['ritocco_contatto'] else np.zeros(len(et), dtype=np.int64)
        cl2 = (pc != 0).astype(np.int64)
        ti = np.clip(tp - 1, 0, 1)
        tg = par.tau[ti, cl2, ct, np.clip(gl, 0, None)]
        tx = par.tau[ti, cl2, ct, np.clip(ci, 0, None)]
        glyph = np.where(tp == 1, tg / np.maximum(1.0 - tx, 1e-9), np.where(tp == 2, tg, 1.0))
        evp = q * rho * pos * glyph
        PR = np.bincount(et[isR], weights=evp[isR], minlength=T)
        PP = np.bincount(et[~isR], weights=evp[~isR], minlength=T)
        comp = np.stack([PL, PS, PF, PR, PP], axis=1)
        val = np.stack([np.ones(T, bool), c.vS, np.ones(T, bool), self.vR, self.vP], axis=1)
        pis = par.pi[c.lg] * val if self.var['pi_per_lingua'] else par.pi[0][None, :] * val
        sm = pis.sum(1, keepdims=True)
        pis = pis / np.where(sm > 0, sm, 1.0)
        return dict(comp=comp, pis=pis, evp=evp, q=q, DR=DRs, DP=DPs, ggR=ggR, ggP=ggP, wR=wR)

    def verosimiglianza(self, par):
        """(bit delle parole, bit di fine parola, numero di segni (glifi + un separatore per parola)) del Corpus; senza pesi."""
        x = self._componenti(par)
        P = np.maximum((x['comp'] * x['pis']).sum(1), EPS_P)
        return float(-np.log2(P).sum()), float(self.c.bits_stop.sum()), self.c.n_segni, -np.log2(P)

    # ---- un passo EM
    def passo(self, par, aggiorna=True):
        c, var, E = self.c, self.var, self.E
        T, G, Cx = c.T, self.voc.G, self.voc.Cx
        x = self._componenti(par)
        comp, pis = x['comp'], x['pis']
        P = np.maximum((comp * pis).sum(1), EPS_P)
        w = self.peso
        ll = float((w * np.log(P)).sum())
        if not aggiorna:
            return ll
        r = comp * pis / P[:, None]                                   # responsabilita' (T, 5)
        wr = r * w[:, None]
        # ---- quote
        new = par.copia()
        if var['pi_per_lingua']:
            for gp in range(3):
                m = c.lg == gp
                if m.sum() > 30:
                    s = wr[m].sum(0) + 0.5 * (par.pi[gp] > 0)
                    new.pi[gp] = s / s.sum()
        else:
            s = wr.sum(0) + 0.5 * (par.pi[0] > 0)
            new.pi[:] = s / s.sum()
        for si, nome in enumerate(SORGENTI):
            if not var['usa'][nome]:
                new.pi[:, si] = 0.0
        # ---- contatto: parole fresche (L, S, F) con il loro primo glifo
        if var['contatto']:
            fr = wr[:, 0] + wr[:, 1] + wr[:, 2]
            n = np.zeros((Cx, G))
            np.add.at(n, (c.ctx, c.fi), fr)
            beta = 20.0
            ref = np.bincount(c.fi, weights=w, minlength=G) + 0.5
            ref = ref / ref.sum()
            new.ref = ref
            new.pc = (n + beta * ref[None, :]) / (n.sum(1, keepdims=True) + beta)
            new.g = np.clip(new.pc / ref[None, :], *SOGLIA_G)
        # ---- copia: nucleo, ritocco, posto, glifo
        src, k, tp, pc, nn, gl, ci, et, bb = E['src'], E['k'], E['tipo'], E['pc'], E['n'], E['g'], E['ci'], E['t'], E['b']
        isR = src == 0
        evp = x['evp']
        post = np.zeros(len(et))
        rs = np.where(isR, wr[et, 3], wr[et, 4])
        den = np.where(isR, np.maximum(comp[et, 3], EPS_P), np.maximum(comp[et, 4], EPS_P))
        post = rs * evp / den                                        # massa a posteriori di ogni evento (con peso)
        if len(et):
            if var['ritocco']:
                for sidx in (0, 1):
                    m = (src == sidx)
                    cnt = np.bincount(tp[m], weights=post[m], minlength=4)
                    new.rho[sidx] = (cnt + 1.0) / (cnt.sum() + 4.0)
                for ti in (1, 2, 3):
                    m = tp == ti
                    if m.sum() < 5:
                        continue
                    N = np.bincount(pc[m], weights=post[m], minlength=3)
                    Om = (par.omega[ti - 1] * self.ev_cnt[m]).sum(1)
                    Ex = (self.ev_cnt[m] * (post[m] / np.maximum(Om, EPS_P))[:, None]).sum(0)
                    om = (N + 1.0) / (Ex + 1.0)
                    new.omega[ti - 1] = om / om.mean()
                ctxu = c.ctx[et] if var['ritocco_contatto'] else np.zeros(len(et), dtype=np.int64)
                for ti in (1, 2):
                    for cl2 in (0, 1):
                        m = (tp == ti) & ((pc != 0).astype(int) == cl2)
                        if not m.any():
                            continue
                        tab = np.zeros((Cx, G))
                        np.add.at(tab, (ctxu[m], gl[m]), post[m])
                        tot = tab.sum(0)
                        glob = (tot + 0.5) / (tot.sum() + 0.5 * G)
                        if var['ritocco_contatto'] and cl2 == 0:
                            new.tau[ti - 1, cl2] = (tab + 5.0 * glob[None, :]) / (tab.sum(1, keepdims=True) + 5.0)
                        else:
                            new.tau[ti - 1, cl2] = glob[None, :]
            if (not var['nucleo_piatto']) or var['frequenza']:
                gg_s = (x['ggR'], x['ggP'])
                for sidx in (0, 1):
                    m = src == sidx
                    kk, ph = (par.kR, par.phiR) if sidx == 0 else (par.kP, par.phiP)
                    K = KR if sidx == 0 else KP
                    DD = x['DR'] if sidx == 0 else x['DP']
                    gg_ = gg_s[sidx]
                    Sk = np.bincount(k[m], weights=post[m], minlength=K)
                    Sb = np.bincount(bb[m], weights=post[m], minlength=NF)
                    if sidx == 0:
                        ct = self.cand_t
                        base = wr[ct, 3] * gg_[c.ctx[ct], self.cand_f] / DD[ct]
                        ek = np.bincount(self.cand_k, weights=base * ph[self.cand_b], minlength=K)
                        eb = np.bincount(self.cand_b, weights=base * kk[self.cand_k], minlength=NF)
                        cnt_k = np.bincount(self.cand_k, minlength=K).astype(float)
                        cnt_b = np.bincount(self.cand_b, minlength=NF).astype(float)
                    else:
                        ek, eb = np.zeros(K), np.zeros(NF)
                        wt = wr[:, 4] / DD
                        for kcl in range(KP):
                            for b in range(NF):
                                ex = float((wt * (self.CP[:, kcl, b, :][c.riga] * gg_[c.ctx]).sum(1)).sum())
                                ek[kcl] += ex * ph[b]
                                eb[b] += ex * kk[kcl]
                        cnt_k = self.CP.sum(axis=(2, 3)).sum(0)
                        cnt_b = self.CP.sum(axis=(1, 3)).sum(0)
                    nk = kk if var['nucleo_piatto'] else _mm_fattore(Sk, ek, kk, cnt_k)
                    nb = ph if not var['frequenza'] else _mm_fattore(Sb, eb, ph, cnt_b)
                    if sidx == 0:
                        new.kR, new.phiR = nk, nb
                    else:
                        new.kP, new.phiP = nk, nb
        new.ll = par.ll + [ll]
        self._stat = dict(r=wr.sum(0), post=post)
        return ll, new

    def adatta(self, par, max_iter=60, tol=1e-6, verbose=None):
        """EM: alterna passi finche' la verosimiglianza (media per parola) non migliora meno di `tol`. -> parametri."""
        ultimo = None
        for it in range(max_iter):
            ll, par = self.passo(par)
            m = ll / max(self.peso.sum(), 1.0)
            if verbose:
                verbose('  EM %d: log-verosimiglianza media %.5f' % (it, m))
            if ultimo is not None and m - ultimo < tol:
                break
            ultimo = m
        return par


# ---------------------------------------------------------------- stima completa di una versione

def stima(pagine_add, voc, rischio, var, n_inner=10, seme=1, basi=None, max_iter=60, tol=1e-6, verbose=None, peso_pagine=None):
    """Stima i parametri della versione `var` sulle pagine di addestramento. -> (par, basi, calcolo)."""
    basi = basi or Basi(pagine_add, voc, n_inner=n_inner, seme=seme)
    corpus = Corpus(pagine_add, voc, rischio, basi.gruppi_sl, basi.hid_di_foglio)
    peso = None
    if peso_pagine is not None:
        peso = np.array([peso_pagine[p] for p in corpus.pag], dtype=float)
    calc = Calcolo(corpus, basi, var, peso)
    par = Par(voc, var)
    par = iniziale(par, corpus, var)
    par = calc.adatta(par, max_iter=max_iter, tol=tol, verbose=verbose)
    return par, basi, calc


def iniziale(par, c, var):
    """Contatto di partenza: frequenze del primo glifo dato il contesto sulle parole di addestramento."""
    G, Cx = c.voc.G, c.voc.Cx
    ref = np.bincount(c.fi, minlength=G) + 0.5
    ref = ref / ref.sum()
    n = np.zeros((Cx, G))
    np.add.at(n, (c.ctx, c.fi), 1.0)
    par.ref = ref
    par.pc = (n + 20.0 * ref[None, :]) / (n.sum(1, keepdims=True) + 20.0)
    if var['contatto']:
        par.g = np.clip(par.pc / ref[None, :], *SOGLIA_G)
    return par


def valuta(par, pagine, voc, rischio, basi, var):
    """Bit per segno e per parola di pagine nuove (lessici pieni). -> dict."""
    c = Corpus(pagine, voc, rischio, basi.gruppi_sl, None, hid_default=basi.H)
    calc = Calcolo(c, basi, var)
    bw, bs, ns, per = calc.verosimiglianza(par)
    return OrderedDict(bit_parole=bw, bit_fine=bs, segni=ns, parole=c.T, bit_per_segno=(bw + bs) / ns, bit_per_parola=bw / c.T,
                       bit_per_segno_solo_parole=bw / ns), per, calc


def riassunto_parametri(par, calc=None, var=None):
    """Numeri leggibili dei parametri: quote per lingua, nucleo (quota di scelte per classe), ritocco, posto, contatto."""
    out = OrderedDict()
    out['quote'] = OrderedDict((lab, [float(x) for x in par.pi[i]]) for i, lab in enumerate(('A', 'B', 'altra')))
    out['rho'] = OrderedDict((nm, [float(x) for x in par.rho[i]]) for i, nm in enumerate(('R', 'P')))
    out['omega'] = [[float(x) for x in row] for row in par.omega]
    out['kR'] = [float(x) for x in par.kR]
    out['kP'] = [float(x) for x in par.kP]
    out['phiR'] = [float(x) for x in par.phiR]
    out['phiP'] = [float(x) for x in par.phiP]
    return out
