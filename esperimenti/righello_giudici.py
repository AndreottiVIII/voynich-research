# -*- coding: utf-8 -*-
"""Giudici nuovi del banco di IA26 (modulo di supporto, non e' un esperimento).

Due giudici che nessun generatore ha mai usato, ne' per regolare qualcosa ne' come bersaglio:
- **N** (conteggi di n-grammi): per ogni riga (la "finestra") i conteggi di n-grammi di glifi (1, 2 e 3) dentro la riga (con i segni
  di inizio e di fine riga e lo spazio fra le parole); un classificatore a regressione logistica impara a dire se una riga e' vera o
  del testo; il punteggio di una pagina e' la media dei punteggi delle sue righe e l'AUC si calcola sulle pagine (pagina vera e gemella
  nella stessa piega, 5 pieghe, 2 ripetizioni). Il vocabolario degli n-grammi viene dalle pagine VERE (i 1.500 piu' frequenti); la forza
  della regolarizzazione e' fissata prima (C = 0,1) e non si tocca guardando i testi. (Una prima versione a livello di pagina, con 1.500
  caratteristiche e 400 esempi, sbagliava il segno dell'AUC: apprendimento "al contrario"; per questo la riga e' l'unita'.)
- **KN** (Markov classico, Kneser-Ney): un modello a n-grammi di glifi con smorzamento di Kneser e Ney (interpolato, sconto di
  Good-Turing per ogni ordine), addestrato sulle pagine vere delle altre pieghe (per foglio, come i giudici K e A); l'ordine (3-6) si
  sceglie sulla validazione fra le pagine VERE (mai sull'esito di un giudice). La sorpresa per glifo diventa un profilo di 14 numeri
  (`ia01.profilo`) e la regressione logistica e' quella di ia01. E' il "giudice a sorpresa" di A e K con un modello che non e' una rete.

Funzioni importate senza modifiche: `ia01_giudice_neurale` (profilo, codifica, auc), `imitatore_misure` (divisione delle pieghe di K).
Una pagina e' una lista di righe (inizio_paragrafo, [parola come tupla di glifi]). Nessun risultato e' scritto qui.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import imitatore_misure as MS  # noqa: E402

VOC_N = 1500                 # n-grammi del vocabolario del giudice N
C_N = 0.1                    # regolarizzazione del giudice N (fissata prima della prova sul Voynich)
PIEGHE_N = 5                 # pieghe per gruppo di pagine del giudice N
RIP_N = 2                    # ripetizioni (suddivisioni diverse) del giudice N
NMAX_N = 3                   # n-grammi di glifi da 1 a 3
ORDINI_KN = (3, 4, 5, 6)     # ordini provati da KN (scelta sulla validazione fra le pagine vere)
SEMI_AUC = (231, 232, 233, 234, 235)
NL_ID = 1                    # a capo nella codifica di ia01


# ---------------------------------------------------------------- AUC con regolarizzazione data

def auc_cv_C(X, y, gruppi, C, pieghe=10, semi=SEMI_AUC):
    """Come ia01.auc_logistico (standardizzazione, regressione logistica, pieghe per gruppo, medie su 5 ripetizioni) ma con C a scelta."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y = np.asarray(X), np.asarray(y)
    aucs = []
    n_gr = len(set(gruppi))
    for s in semi:
        p = np.zeros(len(y))
        for tr, te in StratifiedGroupKFold(n_splits=min(pieghe, n_gr), shuffle=True, random_state=s).split(X, y, gruppi):
            mod = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000)).fit(X[tr], y[tr])
            p[te] = mod.predict_proba(X[te])[:, 1]
        aucs.append(G.auc(y, p))
    return float(np.mean(aucs))


# ---------------------------------------------------------------- giudice N: conteggi di n-grammi dentro la riga

def token_riga(ws):
    """Una riga come sequenza di simboli: inizio riga, glifi con lo spazio fra le parole, fine riga."""
    t = ['^']
    for j, w in enumerate(ws):
        if j:
            t.append(' ')
        t.extend(w)
    t.append('$')
    return t


def conti_ngrammi_riga(ws, nmax=NMAX_N):
    c = Counter()
    t = token_riga(ws)
    for n in range(1, nmax + 1):
        for i in range(len(t) - n + 1):
            c[tuple(t[i:i + n])] += 1
    return c


def vocabolario_N(pagine_vere, k=VOC_N):
    """I k n-grammi piu' frequenti nelle pagine vere (a parita' l'ordine alfabetico: nessun caso)."""
    tot = Counter()
    for rows in pagine_vere.values():
        for _, ws in rows:
            tot.update(conti_ngrammi_riga(ws))
    return [g for g, _ in sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]


def matrice_righe_N(pagine, nomi, voc):
    """Una riga di matrice (conteggi degli n-grammi del vocabolario dentro la riga) per ogni riga delle pagine `nomi`. -> (matrice sparsa, pagina di
    ogni riga come indice in `nomi`)."""
    from scipy.sparse import csr_matrix
    ix = {g: j for j, g in enumerate(voc)}
    dati, col, ptr, prop = [], [], [0], []
    for i, p in enumerate(nomi):
        for _, ws in pagine[p]:
            for g, v in conti_ngrammi_riga(ws).items():
                j = ix.get(g)
                if j is not None:
                    dati.append(float(v))
                    col.append(j)
            ptr.append(len(dati))
            prop.append(i)
    return csr_matrix((dati, col, ptr), shape=(len(prop), len(voc))), np.array(prop, dtype=np.int64)


def _auc_righe(X, y_riga, pag_riga, y_pag, gruppo_pag, C=C_N, pieghe=PIEGHE_N, ripetizioni=RIP_N, seme=700):
    """Nucleo del giudice N: regressione logistica sulle RIGHE (matrice sparsa X, etichetta y_riga), pieghe per gruppo di pagine (una pagina vera
    e la sua gemella stanno nello stesso gruppo), punteggio della pagina = media dei punteggi delle sue righe, AUC sulle pagine (media sulle
    ripetizioni). `pag_riga`: pagina (indice in y_pag) di ogni riga."""
    from sklearn.linear_model import LogisticRegression
    y_pag = np.asarray(y_pag)
    gruppi = sorted(set(gruppo_pag))
    n_pag = len(y_pag)
    n_righe_pag = np.bincount(pag_riga, minlength=n_pag).astype(float)
    aucs = []
    for r in range(ripetizioni):
        ordine = list(gruppi)
        random.Random(seme + r).shuffle(ordine)
        piega_gr = {g: i % pieghe for i, g in enumerate(ordine)}
        piega_pag = np.array([piega_gr[g] for g in gruppo_pag])
        piega_riga = piega_pag[pag_riga]
        punteggio = np.zeros(n_pag)
        for f in range(pieghe):
            tr = piega_riga != f
            te = np.where(~tr)[0]
            if len(te) == 0:
                continue
            mod = LogisticRegression(C=C, max_iter=2000).fit(X[tr], y_riga[tr])
            d = mod.decision_function(X[te])
            punteggio += np.bincount(pag_riga[te], weights=d, minlength=n_pag)
        punteggio = punteggio / np.maximum(n_righe_pag, 1.0)
        aucs.append(G.auc(y_pag, punteggio))
    return float(np.mean(aucs))


def auc_N(Xv, pv, Xt, pt, n_pag):
    """AUC del giudice N fra le pagine vere (Xv, righe di `n_pag` pagine, `pv` = pagina di ogni riga) e le pagine gemelle del testo (Xt, `pt`)."""
    from scipy.sparse import vstack
    X = vstack([Xv, Xt]).tocsr()
    y_riga = np.array([0] * Xv.shape[0] + [1] * Xt.shape[0])
    pag_riga = np.concatenate([pv, pt + n_pag])
    y_pag = np.array([0] * n_pag + [1] * n_pag)
    gruppo = list(range(n_pag)) + list(range(n_pag))
    return _auc_righe(X, y_riga, pag_riga, y_pag, gruppo)


def auc_nullo_N(Xv, pv, n_pag, n_etichette, seme0=3970):
    """Nullo del giudice N: pagine vere con etichette a caso (meta' e meta'), come `auc_nullo_profili`. -> lista di AUC."""
    out = []
    for s in range(1, n_etichette + 1):
        ordine = list(range(n_pag))
        random.Random(seme0 + s).shuffle(ordine)
        classe = np.zeros(n_pag, dtype=np.int64)
        classe[ordine[n_pag // 2:]] = 1
        y_riga = classe[pv]
        out.append(_auc_righe(Xv, y_riga, pv, classe, list(range(n_pag)), seme=800 + s))
    return out


# ---------------------------------------------------------------- giudice KN: n-grammi con smorzamento di Kneser e Ney

class KneserNey:
    """Modello a n-grammi di simboli interi (ids di ia01) con smorzamento di Kneser-Ney interpolato. Ogni pagina comincia da un a capo (come
    `ia01.sorprese`). Sconto per ordine: n1 / (n1 + 2 n2) (stima di Good-Turing); contesto non visto: si passa all'ordine piu' basso;
    ultimo ripiego: probabilita' uniforme."""

    def __init__(self, seqs, ordine, V):
        n = ordine
        self.n, self.V = n, V
        pad = (NL_ID,) * (n - 1)
        raw = Counter()
        for a in seqs:
            s = pad + tuple(int(x) for x in a)
            for i in range(n - 1, len(s)):
                raw[s[i - n + 1:i + 1]] += 1
        self.num = [defaultdict(Counter) for _ in range(n)]       # num[m][contesto di lunghezza m][simbolo]
        for g, v in raw.items():
            self.num[n - 1][g[:-1]][g[-1]] = v
        for m in range(n - 1):
            lung = m + 2
            visti = {g[len(g) - lung:] for g in raw}
            for g in visti:
                self.num[m][g[1:-1]][g[-1]] += 1
        self.tot, self.typ, self.sconto = [], [], []
        for m in range(n):
            self.tot.append({c: sum(d.values()) for c, d in self.num[m].items()})
            self.typ.append({c: len(d) for c, d in self.num[m].items()})
            n1 = sum(1 for d in self.num[m].values() for v in d.values() if v == 1)
            n2 = sum(1 for d in self.num[m].values() for v in d.values() if v == 2)
            self.sconto.append(n1 / (n1 + 2.0 * n2) if n1 + n2 else 0.5)

    def prob(self, h, w):
        """h: tuple degli ultimi n-1 simboli."""
        p = 1.0 / self.V
        for m in range(self.n):
            ctx = h[len(h) - m:] if m else ()
            d = self.num[m].get(ctx)
            if d is None:
                continue
            t = self.tot[m][ctx]
            p = max(d.get(w, 0) - self.sconto[m], 0.0) / t + self.sconto[m] * self.typ[m][ctx] / t * p
        return p

    def sorpresa(self, a):
        """Bit per simbolo di una pagina (array di ids)."""
        n = self.n
        s = (NL_ID,) * (n - 1) + tuple(int(x) for x in a)
        out = np.empty(len(a))
        for i in range(len(a)):
            h = s[i:i + n - 1]
            out[i] = -math.log2(max(self.prob(h, s[i + n - 1]), 1e-12))
        return out

    def bit_medi(self, pagine_ids):
        tot = n = 0
        for a in pagine_ids:
            s = self.sorpresa(a)
            tot += float(s.sum())
            n += len(s)
        return tot / max(n, 1)


def scegli_kn(ids_add, ids_val, V):
    """Ordine di KN scelto sulla validazione (pagine vere tenute da parte): bit per simbolo piu' bassi."""
    scelta = None
    for n in ORDINI_KN:
        m = KneserNey(ids_add, n, V)
        b = m.bit_medi(ids_val)
        if scelta is None or b < scelta[0]:
            scelta = (b, n, m)
    return scelta[2], OrderedDict(ordine=scelta[1], bit_validazione=round(scelta[0], 4))


def lavoro_KN(f, c, libri):
    """Come `imitatore_misure.lavoro_K` per KN: profili di sorpresa (14 numeri) delle pagine di prova della piega f, `vere` e ogni libro di `libri`
    (nome -> pagina -> righe). Il modello e' addestrato sulle pagine vere delle altre pieghe (10% per la validazione, come K)."""
    test, val, add = MS.divisione_K(c, f)
    m, info = scegli_kn([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V'])
    prof = OrderedDict()
    prof['vere'] = OrderedDict((p, G.profilo(c['ids'][p], m.sorpresa(c['ids'][p]))) for p in test)
    for nome, rows in libri.items():
        out = OrderedDict()
        for p in test:
            if p in rows:
                a = G.codifica(rows[p], c['idx'])
                out[p] = G.profilo(a, m.sorpresa(a))
        prof[nome] = out
    return info, prof


# ---------------------------------------------------------------- nullo: pagine vere con etichette a caso

def auc_nullo_profili(profili, n_etichette, auc_fun=None, seme0=3970):
    """AUC di un giudice a profili con etichette a caso fra pagine vere (meta' e meta'), come `imitatore_misure.negativo_K` ma con
    `n_etichette` etichettature diverse. `profili`: pagina -> vettore. -> lista di AUC."""
    auc_fun = auc_fun or (lambda X, y, g: G.auc_logistico(X, y, g)[0])
    out = []
    for s in range(1, n_etichette + 1):
        pag = sorted(profili)
        random.Random(seme0 + s).shuffle(pag)
        y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
        X = np.array([profili[p] for p in pag])
        out.append(float(auc_fun(X, y, pag)))
    return out
