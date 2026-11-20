# -*- coding: utf-8 -*-
"""Testi sintetici con regole d'ordine PIANTATE (e il loro "oracolo") per ia13 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- `genera_piantato`: un testo costruito su un testo qualunque (nel Voynich le "vere", nelle prove il latino) con le stesse righe e le
  stesse lunghezze, dove ogni parola e' pescata dalla frequenza del testo (nessun ordine) tranne tre regole di ordine, di forza nota:
    R1 (contatto, distanza 1): se la parola prima finisce con il glifo X, la parola comincia con il glifo Y (con probabilita' p1);
    R2 (distanza 2):          se la parola di due posti prima finisce con U (e R1 non vale), la parola comincia con W (prob. p2);
    R3 (inizio riga):         la prima parola di ogni riga comincia con Z (prob. p3).
  Con p1 = p2 = p3 = 0 e' un testo SENZA ORDINE (le parole sono indipendenti).
- `Oracolo`: la probabilita' vera di ogni parola dato il suo contesto nella riga, secondo il generatore. Serve a dire quanto
  dovrebbe perdere una rete perfetta se si rimescola la riga (e dove), da confrontare con la rete vera.
Le parole del generatore sono quelle del testo di base; nessun numero e' scritto qui.
"""
import bisect
import math
import random
from collections import OrderedDict

import numpy as np

REGOLE = dict(F=(0.8, 0.6, 0.8), D=(0.3, 0.2, 0.3), Z=(0.0, 0.0, 0.0), R=(0.0, 0.9, 0.0))     # forte, debole, nulla (senza ordine), solo distanza 2: p1, p2, p3
FR_LAST, FR_FIRST = 0.15, 0.10            # quota di parole che finiscono con X (e con U); che cominciano con Y, W, Z (circa)


def scegli_glifi(C, cw):
    """I glifi X, U (finali) e Y, W, Z (iniziali): quelli la cui quota fra le parole e' piu' vicina a FR_LAST e FR_FIRST (distinti)."""
    N = float(cw.sum())
    fr, la = np.zeros(C.q), np.zeros(C.q)
    for t in np.where(cw > 0)[0]:
        fr[C.prima[t]] += cw[t]
        la[C.ultima[t]] += cw[t]
    fr, la = fr / N, la / N

    def vicino(vec, bersaglio, esclusi):
        cand = [(abs(vec[g] - bersaglio), g) for g in range(C.q) if g != C.rar and g not in esclusi and vec[g] > 0]
        return min(cand)[1]
    X = vicino(la, FR_LAST, set())
    U = vicino(la, FR_LAST, {X})
    Y = vicino(fr, FR_FIRST, set())
    W = vicino(fr, FR_FIRST, {Y})
    Z = vicino(fr, FR_FIRST, {Y, W})
    return dict(X=C.glifi[X], U=C.glifi[U], Y=C.glifi[Y], W=C.glifi[W], Z=C.glifi[Z],
                quota_X=round(float(la[X]), 4), quota_U=round(float(la[U]), 4),
                quota_Y=round(float(fr[Y]), 4), quota_W=round(float(fr[W]), 4), quota_Z=round(float(fr[Z]), 4))


class Oracolo:
    """Probabilita' vera di ogni parola dato il contesto nella riga: P = (1-p) Pu(w) + p Pu(w | comincia con G) se una regola vale,
    altrimenti Pu(w). `pu` e' un dizionario parola (tupla di glifi) -> probabilita' nel testo di base."""

    def __init__(self, pu, glifi, p):
        self.pu = pu
        self.g = glifi
        self.p1, self.p2, self.p3 = p
        self.M = {}
        for G in (glifi['Y'], glifi['W'], glifi['Z']):
            self.M[G] = sum(v for w, v in pu.items() if w[0] == G)
        self.t = None

    def prepara(self, C):
        """Tabelle per tipo di parola di un Corpus C (i tipi del testo generato)."""
        self.pu_t = np.array([self.pu.get(C.parole_in_glifi(t), 1e-9) for t in range(C.nt)])
        self.pri = [C.parole_in_glifi(t)[0] for t in range(C.nt)]
        self.ult = [C.parole_in_glifi(t)[-1] for t in range(C.nt)]
        self.t = C

    def costi(self, toks):
        """Bit di ogni parola di una riga (lista di tipi di C) dato il suo contesto nella riga."""
        out = np.zeros(len(toks))
        g = self.g
        for k, t in enumerate(toks):
            pu = self.pu_t[t]
            p = 0.0
            if k == 0:
                p, G = self.p3, g['Z']
            elif self.ult[toks[k - 1]] == g['X']:
                p, G = self.p1, g['Y']
            elif k >= 2 and self.ult[toks[k - 2]] == g['U']:
                p, G = self.p2, g['W']
            if p > 0:
                pr = (1 - p) * pu + (p * pu / self.M[G] if self.pri[t] == G else 0.0)
            else:
                pr = pu
            out[k] = -math.log2(max(pr, 1e-300))
        return out


def genera_piantato(Cb, seme, livello):
    """Il testo con le regole del `livello` ('F', 'D' o 'Z') sul Corpus di base Cb (con `prepara()` fatto). Restituisce
    (pagine, meta, oracolo): pagine come le altre (lista di righe (inizio, parole)), stesse righe e lunghezze di Cb."""
    Cb.prepara()
    p1, p2, p3 = REGOLE[livello]
    cw = np.zeros(Cb.nt)
    for P in Cb.pag.values():
        cw += np.bincount(P.tok, minlength=Cb.nt)
    glifi = scegli_glifi(Cb, cw)
    pu = {Cb.parole_in_glifi(t): float(cw[t] / cw.sum()) for t in np.where(cw > 0)[0]}
    orac = Oracolo(pu, glifi, (p1, p2, p3))
    cum_tutti = np.cumsum(cw)
    liste = {}
    for G in (glifi['Y'], glifi['W'], glifi['Z']):
        ts = [int(t) for t in np.where(cw > 0)[0] if Cb.glifi[Cb.prima[t]] == G]
        liste[G] = (ts, np.cumsum(cw[ts]))
    rnd = random.Random(seme)

    def estrai(G=None):
        if G is None:
            return int(bisect.bisect_right(cum_tutti, rnd.random() * cum_tutti[-1]))
        ts, cum = liste[G]
        return ts[min(bisect.bisect_right(cum, rnd.random() * cum[-1]), len(ts) - 1)]

    def ultimo(t):
        return Cb.glifi[Cb.ultima[t]]
    out = OrderedDict()
    for p, P in Cb.pag.items():
        rows = []
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            toks = []
            for k in range(n):
                if k == 0:
                    pr, G = p3, glifi['Z']
                elif ultimo(toks[k - 1]) == glifi['X']:
                    pr, G = p1, glifi['Y']
                elif k >= 2 and ultimo(toks[k - 2]) == glifi['U']:
                    pr, G = p2, glifi['W']
                else:
                    pr, G = 0.0, None
                toks.append(estrai(G) if (pr > 0 and rnd.random() < pr) else estrai())
            rows.append((bool(P.ini[P.lstart[l]]), [Cb.parole_in_glifi(t) for t in toks]))
        out[p] = rows
    meta = OrderedDict(livello=livello, p1=p1, p2=p2, p3=p3, **glifi)
    return out, meta, orac
