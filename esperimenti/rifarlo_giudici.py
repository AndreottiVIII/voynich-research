# -*- coding: utf-8 -*-
"""Giudici di ia11 (modulo di supporto, non e' un esperimento).

- `GiudiceK`: il giudice INDIPENDENTE. Un modello a caratteri non neurale (n-grammi con lisciatura di Witten-Bell interpolata, piu'
  una "memoria di pagina": le sequenze gia' scritte sulla stessa pagina pesano di piu'; idea delle cache dei modelli di lingua,
  Kuhn e De Mori 1990, da ricontrollare). Non e' stato usato per progettare i ritocchi e non ha niente in comune con la rete GRU del
  giudice A, salvo il passaggio finale (il profilo di sorpresa di ia01 e la regressione logistica). Si addestra solo sulle pagine
  vere di addestramento della piega.
- `giudici_paper`: i due giudici del paper (e231 e e266), con i loro riferimenti presi dalle pagine vere di ia01.
- aiuti per l'AUC e per gli intervalli appaiati.
Nessun risultato e' scritto qui.
"""
import math
import os
import sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)


# ---------------------------------------------------------------- giudice K

class GiudiceK:
    """Modello a caratteri: ordine `N` (contesto di N-1 segni), lisciatura di Witten-Bell interpolata, memoria di pagina con peso
    `lam` * n / (n + kap) (n = quante volte il contesto di `KC` segni e' gia' comparso nella pagina)."""
    KC = 3

    def __init__(self, pagine_ids, V, N=5, lam=0.0, kap=2.0):
        self.V, self.N, self.lam, self.kap = V, N, lam, kap
        self.tab = [dict() for _ in range(N)]
        for a in pagine_ids:
            seq = [1] + a.tolist()
            for i in range(1, len(seq)):
                x = seq[i]
                for k in range(0, N):
                    if k > i:
                        break
                    ctx = tuple(seq[i - k:i]) if k else ()
                    nd = self.tab[k].get(ctx)
                    if nd is None:
                        nd = self.tab[k][ctx] = [0, 0, {}]
                    if x not in nd[2]:
                        nd[1] += 1
                        nd[2][x] = 0
                    nd[0] += 1
                    nd[2][x] += 1

    def imposta(self, N=None, lam=None, kap=None):
        if N is not None:
            assert N <= len(self.tab)
            self.N = N
        if lam is not None:
            self.lam = lam
        if kap is not None:
            self.kap = kap

    def sorpresa(self, a):
        """Bit di ogni segno di una pagina (array di numeri, come ia01); il contesto parte dall'a capo (numero 1)."""
        V, N, lam, kap, KC = self.V, self.N, self.lam, self.kap, self.KC
        tab = self.tab
        seq = [1] + a.tolist()
        cache = {}
        out = np.zeros(len(a))
        for i in range(1, len(seq)):
            x = seq[i]
            p = 1.0 / V
            for k in range(0, N):
                if k > i:
                    break
                ctx = tuple(seq[i - k:i]) if k else ()
                nd = tab[k].get(ctx)
                if nd is None:
                    break
                p = (nd[2].get(x, 0) + nd[1] * p) / (nd[0] + nd[1])
            if lam > 0 and i >= KC:
                cc = tuple(seq[i - KC:i])
                e = cache.get(cc)
                if e is not None:
                    n = e[0]
                    w = lam * n / (n + kap)
                    p = (1 - w) * p + w * e[1].get(x, 0) / n
                    e[0] += 1
                    e[1][x] = e[1].get(x, 0) + 1
                else:
                    cache[cc] = [1, {x: 1}]
            elif lam > 0:
                pass
            out[i - 1] = -math.log2(max(p, 1e-12))
        return out


def costo_medio(giudice, pagine_ids):
    tot = n = 0.0
    for a in pagine_ids:
        s = giudice.sorpresa(a)
        tot += s.sum()
        n += len(s)
    return tot / max(n, 1)


def scegli_giudice_k(add_ids, val_ids, V, ordini=(4, 5, 6), lams=(0.0, 0.1, 0.2, 0.35, 0.5), kaps=(1.0, 3.0)):
    """Addestra il giudice sulle pagine di addestramento e sceglie ordine e memoria di pagina sulle pagine di validazione vere (costo minimo:
    nessuna pagina generata e nessuna pagina di prova interviene)."""
    N0 = max(ordini)
    g = GiudiceK(add_ids, V, N=N0)
    scelta = None
    for N in ordini:
        g.imposta(N=N, lam=0.0)
        c = costo_medio(g, val_ids)
        if scelta is None or c < scelta[0]:
            scelta = (c, N, 0.0, 2.0)
    g.imposta(N=scelta[1])
    base = scelta
    for lam in lams:
        for kap in kaps:
            if lam == 0:
                continue
            g.imposta(lam=lam, kap=kap)
            c = costo_medio(g, val_ids)
            if c < scelta[0]:
                scelta = (c, scelta[1], lam, kap)
    g.imposta(N=scelta[1], lam=scelta[2], kap=scelta[3])
    return g, dict(N=scelta[1], lam=scelta[2], kap=scelta[3], bit_validazione=round(scelta[0], 4), bit_senza_memoria=round(base[0], 4))


# ---------------------------------------------------------------- giudici del paper

_RIF = {}


def prepara_paper(vere):
    """`vere`: pagina -> righe (inizio, [parola come tupla di glifi]) di ia01. Costruisce nel formato dei giudici del paper le pagine vere
    e i riferimenti (come ia07.riferimenti, ma sulle stesse pagine vere di ia01)."""
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    vpag, vi = OrderedDict(), OrderedDict()
    for p, rows in vere.items():
        vpag[p] = ['?', [[''.join(w) for w in ws] for _, ws in rows]]
        vi[p] = ['?', [(bool(ini), [''.join(w) for w in ws]) for ini, ws in rows]]
    rif = e231.riferimenti(vpag)
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    nv, Xv, nf = e231.caratteristiche(OrderedDict((p, rr) for p, (_, rr) in vpag.items()), rif)
    _RIF.update(vpag=vpag, rif=rif, rif266=rif266, vt266=vt266, v231=(nv, Xv, nf))
    return _RIF


def _auc_tabelle(vt, gt):
    import e231_discriminatore as e231
    nv, Xv, _ = vt
    ng, Xg, _ = gt
    comuni = [p for p in nv if p in set(ng)]
    iv, ig = {p: i for i, p in enumerate(nv)}, {p: i for i, p in enumerate(ng)}
    X = np.vstack([Xv[[iv[p] for p in comuni]], Xg[[ig[p] for p in comuni]]])
    y = np.array([0] * len(comuni) + [1] * len(comuni))
    return e231.auc_cv(X, y, np.array(comuni + comuni)), len(comuni)


def giudici_paper(libro, vere):
    """AUC dei due giudici del paper per un libro (pagina -> righe di ia01), con il loro protocollo (pagina vera e gemella insieme,
    10 pieghe, 5 ripetizioni). Il libro e' ridotto alle pagine che esistono fra le vere."""
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    if not _RIF:
        prepara_paper(vere)
    gp = OrderedDict((p, [[''.join(w) for w in ws] for _, ws in rows]) for p, rows in libro.items() if p in vere)
    gi = OrderedDict((p, [(bool(ini), [''.join(w) for w in ws]) for ini, ws in rows]) for p, rows in libro.items() if p in vere)
    n231, X231, nf = e231.caratteristiche(gp, _RIF['rif'])
    a231, n1 = _auc_tabelle(_RIF['v231'], (n231, X231, nf))
    tab = e266.tabella(gi, _RIF['rif266'])
    a266, n2 = _auc_tabelle(_RIF['vt266'], tab)
    return dict(AUC_e231=float(a231), AUC_e266=float(a266), pagine=int(min(n1, n2)))


# ---------------------------------------------------------------- AUC e intervalli appaiati

def auc_rango(y, p):
    from scipy.stats import rankdata
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float('nan')
    r = rankdata(p)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def auc_coppie(r, g):
    return auc_rango([0] * len(r) + [1] * len(g), np.concatenate([r, g]))


def bootstrap_auc(insiemi, n=1000, seme=1):
    """`insiemi`: nome -> lista di (reali, generate) (una coppia per libro, stesse pagine nello stesso ordine). Per ogni ricampionamento
    delle pagine (lo stesso per tutti i nomi) calcola la media sui libri delle AUC. Restituisce nome -> array di n medie."""
    rng = np.random.default_rng(seme)
    nomi = list(insiemi)
    m = len(insiemi[nomi[0]][0][0])
    out = {k: np.zeros(n) for k in nomi}
    for i in range(n):
        I = rng.integers(0, m, m)
        for k in nomi:
            out[k][i] = np.mean([auc_coppie(r[I], g[I]) for r, g in insiemi[k]])
    return out
