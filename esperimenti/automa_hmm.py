# -*- coding: utf-8 -*-
"""Automi probabilistici della forma delle parole per ia31 (modulo di supporto, non e' un esperimento).

Un "automa" qui e' un modello di Markov nascosto (HMM) a K stati, con emissione dallo stato: ogni parola e' una sequenza di glifi
seguita da un segno di fine parola (FINE). Lo stato iniziale si sceglie con la probabilita' pi; a ogni passo lo stato emette un segno
(un glifo oppure FINE) e, se non e' FINE, passa a un altro stato con la matrice A. La parola finisce quando viene emesso FINE:
la distribuzione sulle parole e' quindi esatta (somma a 1, salvo le parole di lunghezza infinita, di probabilita' nulla).

Due famiglie (stessa macchina, vincoli diversi sulla matrice A):
  libero    A piena: un automa qualunque con K stati.
  caselle   A triangolare (si resta nella casella o si va a una successiva, mai indietro): una grammatica a caselle imparata dai dati.

Stima: Baum-Welch (EM) con le parole distinte e i loro pesi (pesi = frequenza nel testo, oppure 1 per ogni parola distinta), con
propagazione "scalata" (stabile). Il criterio di taglia e' la lunghezza di descrizione (BIC): -log2 verosimiglianza + (parametri/2) log2 n.
Il costo per posizione e' esatto: le costanti di scala della propagazione in avanti sono le probabilita' condizionate P(segno | prefisso).

Questo modulo non legge nessun dato e non importa altro che numpy. Versione: AUTOMA-1.
"""
import math
import numpy as np

VERSIONE = 'automa-1'
PSEUDO = 0.01                  # pseudo-conteggio (peso assoluto) sulle probabilita' di emissione, transizione e inizio: evita i veri zeri


class Alfabeto:
    """Segni di un testo: i glifi (in ordine fisso), il segno raro (glifo mai visto) e FINE. Indici: glifi 0..V-1, RARO = V, FINE = V+1."""

    def __init__(self, glifi):
        self.glifi = list(glifi)
        self.V = len(self.glifi)
        self.idx = {g: i for i, g in enumerate(self.glifi)}
        self.RARO = self.V
        self.FINE = self.V + 1
        self.NS = self.V + 2

    def codifica(self, parola):
        """Parola (sequenza di glifi) -> lista di indici con FINE in coda."""
        return [self.idx.get(g, self.RARO) for g in parola] + [self.FINE]


def gruppi_da_parole(parole, pesi, alfabeto):
    """Le parole (lista di sequenze di glifi) con i loro pesi -> {lunghezza con FINE: (S matrice interi N x L, pesi N, indici delle parole)}.
    Parole vuote escluse."""
    per_lung = {}
    for k, (w, p) in enumerate(zip(parole, pesi)):
        if len(w) == 0:
            continue
        per_lung.setdefault(len(w) + 1, []).append((k, alfabeto.codifica(w), p))
    out = {}
    for L, el in per_lung.items():
        S = np.array([e[1] for e in el], dtype=np.int64)
        out[L] = (S, np.array([e[2] for e in el], dtype=np.float64), np.array([e[0] for e in el], dtype=np.int64))
    return out


def parametri_liberi(K, V, famiglia):
    """Numero di parametri liberi: inizio (K-1) + transizioni + emissioni (K righe da V+1 segni: V liberi per riga)."""
    if famiglia == 'libero':
        trans = K * (K - 1)
    elif famiglia == 'caselle':
        trans = K * (K - 1) // 2
    else:
        raise ValueError(famiglia)
    return (K - 1) + trans + K * V


class Automa:
    def __init__(self, K, alfabeto, famiglia, pi, A, B):
        self.K, self.al, self.famiglia = K, alfabeto, famiglia
        self.pi, self.A, self.B = pi, A, B

    # ------------------------------------------------------------ propagazione
    def _avanti(self, S):
        """alpha scalato (N, L, K) e costanti di scala c (N, L): c[:, t] = P(segno t | segni prima). Verosimiglianza = prodotto di c."""
        N, L = S.shape
        E = self.B.T[S]                                         # (N, L, K): probabilita' di emettere il segno osservato da ogni stato
        alpha = np.empty((N, L, self.K))
        c = np.empty((N, L))
        a = self.pi[None, :] * E[:, 0, :]
        c[:, 0] = a.sum(1)
        alpha[:, 0] = a / np.maximum(c[:, 0:1], 1e-300)
        for t in range(1, L):
            a = (alpha[:, t - 1] @ self.A) * E[:, t, :]
            c[:, t] = a.sum(1)
            alpha[:, t] = a / np.maximum(c[:, t:t + 1], 1e-300)
        return E, alpha, c

    def costi_posizione(self, S):
        """Bit per posizione (N, L): -log2 P(segno t | prefisso). L'ultima colonna e' il costo di FINE."""
        c = self._avanti(S)[2]
        return -np.log2(np.maximum(c, 1e-300))

    def costo_gruppi(self, gruppi):
        """{indice parola: vettore dei bit per posizione}."""
        out = {}
        for L, (S, w, ix) in gruppi.items():
            b = self.costi_posizione(S)
            for r, k in enumerate(ix):
                out[int(k)] = b[r]
        return out

    def ll_bit(self, gruppi):
        """Somma pesata dei bit (= -log2 verosimiglianza)."""
        tot = 0.0
        for L, (S, w, ix) in gruppi.items():
            tot += float((self.costi_posizione(S).sum(1) * w).sum())
        return tot

    def parametri(self):
        return parametri_liberi(self.K, self.al.V, self.famiglia)

    # ------------------------------------------------------------ campionamento (controlli sintetici)
    def campiona(self, rng, massimo=40):
        """Una parola (sequenza di indici di glifi). Riparte se supera `massimo` segni."""
        while True:
            s = rng.choice(self.K, p=self.pi)
            w = []
            while len(w) <= massimo:
                pb = self.B[s].copy()
                pb[self.al.RARO] = 0.0
                x = rng.choice(self.al.NS, p=pb / pb.sum())
                if x == self.al.FINE:
                    return tuple(w) if w else self.campiona(rng, massimo)
                w.append(int(x))
                s = rng.choice(self.K, p=self.A[s])
            # troppo lunga: si scarta


def _normalizza(M, maschera=None):
    if maschera is not None:
        M = M * maschera
    s = M.sum(-1, keepdims=True)
    s = np.where(s <= 0, 1.0, s)
    return M / s


def _maschera(K, famiglia):
    if famiglia == 'libero':
        return np.ones((K, K))
    return np.triu(np.ones((K, K)))


def inizializza(K, alfabeto, famiglia, rng, unigramma, pos_media):
    """Partenza casuale, ma deterministica per seme. `unigramma`: frequenze dei segni (NS); `pos_media`: posizione relativa media (0-1) di ogni segno."""
    NS = alfabeto.NS
    base = np.maximum(unigramma, 1e-3)
    maschera = _maschera(K, famiglia)
    if famiglia == 'libero':
        pi = _normalizza(1.0 + rng.random(K))
        A = _normalizza(1.0 + rng.random((K, K)))
        B = _normalizza(base[None, :] * (0.3 + rng.random((K, NS))))
    else:
        pi = _normalizza(np.exp(-np.arange(K) / max(1.0, K / 3.0)) * (0.5 + rng.random(K)))
        stay = 1.0 + rng.random((K, K)) * np.eye(K) * 2
        A = _normalizza((np.triu(rng.random((K, K)) + stay)), maschera)
        centro = (np.arange(K) + 0.5) / K
        d = (pos_media[None, :] - centro[:, None]) / max(0.15, 1.0 / K)
        B = _normalizza(base[None, :] * np.exp(-0.5 * d * d) * (0.5 + rng.random((K, NS))))
    return pi, A, B


def statistiche(gruppi, alfabeto):
    """Frequenze pesate dei segni (NS) e posizione relativa media di ciascuno: servono solo a inizializzare."""
    NS = alfabeto.NS
    f = np.zeros(NS)
    pos = np.zeros(NS)
    for L, (S, w, ix) in gruppi.items():
        rel = np.arange(L)[None, :] / max(1, L - 1)
        for x in range(NS):
            m = (S == x)
            f[x] += float((m * w[:, None]).sum())
            pos[x] += float((m * w[:, None] * rel).sum())
    pos = np.where(f > 0, pos / np.maximum(f, 1e-12), 0.5)
    return f / max(f.sum(), 1e-12), pos


def stima(gruppi, alfabeto, K, famiglia, seme, giri=25, tol=1e-5, riavvii=1, unigramma=None, pos_media=None):
    """Baum-Welch con `riavvii` partenze casuali: si tiene la migliore per verosimiglianza. Restituisce (Automa, dict di informazioni).
    K = 1: un solo stato (le lettere sono indipendenti, la lunghezza e' geometrica); non serve EM (conteggi diretti)."""
    if unigramma is None:
        unigramma, pos_media = statistiche(gruppi, alfabeto)
    NS = alfabeto.NS
    maschera = _maschera(K, famiglia)
    migliore, info_m = None, None
    for r in range(riavvii if K > 1 else 1):
        rng = np.random.default_rng(seme * 1000 + r)
        pi, A, B = inizializza(K, alfabeto, famiglia, rng, unigramma, pos_media)
        a = Automa(K, alfabeto, famiglia, pi, A, B)
        prec, giri_fatti = None, 0
        for g in range(giri if K > 1 else 1):
            Epi = np.zeros(K)
            EA = np.zeros((K, K))
            EB = np.zeros((NS, K))
            ll = 0.0
            peso_tot = 0.0
            for L, (S, w, ix) in gruppi.items():
                N = S.shape[0]
                E, alpha, c = a._avanti(S)
                beta = np.empty_like(alpha)
                beta[:, L - 1] = 1.0
                for t in range(L - 2, -1, -1):
                    beta[:, t] = ((E[:, t + 1] * beta[:, t + 1]) @ a.A.T) / np.maximum(c[:, t + 1:t + 2], 1e-300)
                gamma = alpha * beta
                ll += float((np.log(np.maximum(c, 1e-300)).sum(1) * w).sum())
                peso_tot += float(w.sum())
                Epi += (w[:, None] * gamma[:, 0]).sum(0)
                for t in range(L - 1):
                    X = (E[:, t + 1] * beta[:, t + 1]) * (w / np.maximum(c[:, t + 1], 1e-300))[:, None]
                    EA += alpha[:, t].T @ X
                for t in range(L):
                    oh = (S[:, t:t + 1] == np.arange(NS)[None, :])
                    EB += oh.T @ (w[:, None] * gamma[:, t])
            EA = np.where(maschera > 0, EA * a.A, 0.0)
            a.pi = _normalizza(Epi + PSEUDO)
            a.A = _normalizza(EA + PSEUDO * maschera, maschera)
            B2 = EB.T + PSEUDO
            B2[:, alfabeto.RARO] = PSEUDO
            a.B = _normalizza(B2)
            giri_fatti = g + 1
            if prec is not None and abs(ll - prec) <= tol * max(1.0, abs(prec)):
                break
            prec = ll
        info = dict(ll_nat=ll, giri=giri_fatti, riavvio=r)
        if migliore is None or ll > info_m['ll_nat']:
            migliore, info_m = a, info
    return migliore, info_m


def stima_k1(gruppi, alfabeto):
    """K = 1 in forma chiusa: i segni sono indipendenti (conteggio dei segni, FINE compresa)."""
    NS = alfabeto.NS
    cnt = np.zeros(NS)
    for L, (S, w, ix) in gruppi.items():
        for x in range(NS):
            cnt[x] += float(((S == x) * w[:, None]).sum())
    cnt[alfabeto.RARO] = 0.0
    B = _normalizza((cnt + PSEUDO)[None, :])
    B[0, alfabeto.RARO] = PSEUDO / (cnt.sum() + PSEUDO * NS)
    B = _normalizza(B)
    return Automa(1, alfabeto, 'libero', np.ones(1), np.ones((1, 1)), B)


def fit(gruppi, alfabeto, K, famiglia, seme, giri=25, riavvii=1, unigramma=None, pos_media=None):
    """Interfaccia unica: (Automa, informazioni). Per K = 1 le due famiglie coincidono."""
    if K == 1:
        a = stima_k1(gruppi, alfabeto)
        a.famiglia = famiglia
        return a, dict(ll_nat=-a.ll_bit(gruppi) * math.log(2), giri=0, riavvio=0)
    return stima(gruppi, alfabeto, K, famiglia, seme, giri=giri, riavvii=riavvii, unigramma=unigramma, pos_media=pos_media)


def bic_bit(ll_bit_neg, K, V, famiglia, n_eff):
    """Lunghezza di descrizione in bit: -log2 L + (p/2) log2 n."""
    p = parametri_liberi(K, V, famiglia)
    return ll_bit_neg + 0.5 * p * math.log2(max(n_eff, 2.0))


def posizioni_cumulate(bit_per_pos, lunghezza_glifi):
    """Scompone i bit di una parola (lunghezza_glifi + 1 posizioni, l'ultima e' FINE) in cinque parti: primo, secondo, terzo, dal quarto, fine.
    Come in ia24 (nuove_fase0): le parti si dividono per i glifi totali e sommano al costo di forma. Parole di 1 o 2 glifi: le posizioni mancanti valgono 0."""
    n = lunghezza_glifi
    b = np.asarray(bit_per_pos, dtype=float)[:n + 1]
    out = np.zeros(5)
    for i in range(n):
        out[min(i, 3)] += b[i]
    out[4] = b[n]
    return out
