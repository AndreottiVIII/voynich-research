# -*- coding: utf-8 -*-
"""IA32, modulo di supporto: scrivere un libro con le "manopole" (temperatura per posto, top-p, correzione a conteggi, mescolanza delle istantanee).

In parole semplici
- Gli imitatori di ia20-ia24 scrivono sempre a temperatura 1: ogni segno si pesca con la probabilita' che la rete gli da'. Qui la scrittura ha poche manopole
  continue (tutte a valore "neutro" = come ia20, a meno dell'ordine in cui si pescano le scelte):
    T_primo   temperatura del primo glifo di una parola (non a inizio riga)
    T_int     temperatura dei glifi interni (dal secondo in poi)
    T_fine    temperatura della scelta "la parola finisce qui / continua" (si applica al logit della probabilita' totale di spazio + fine riga)
    T_eol     temperatura della scelta fra spazio e fine riga, quando la parola finisce
    T_riga    temperatura del primo glifo della prima parola della riga
    top_p     si tengono solo i glifi piu' probabili che coprono top_p della probabilita' (1 = niente)
    w_tri     come w_cont ma sui trigrammi (due segni prima), tabelle sui contesti visti nell'addestramento
    w_cont    peso di una correzione a conteggi: una spinta (in logit) verso le frequenze dei bigrammi di segni del libro d'addestramento, calcolata contro
              quelle che il libro scritto ha fin li' (con una memoria di partenza `KAPPA` uguale al libro vero)
    s         miscela delle due istantanee del modello (0 = minimo di validazione, 1 = fine delle epoche in piu')
- Con tutte le manopole neutre la distribuzione dei segni e' esattamente quella della rete (le due scelte "fine parola?" e "quale glifo?" si
  moltiplicano in quella di prima). Le regole di scrittura sono quelle di ia07 (`I7.Penna.ammessi`, importate senza modificarle).
- Il libro si scrive pagina per pagina con la disposizione del libro del mondo attivo, tutto con un solo modello (non c'e' piu' "il modello della piega che non
  ha visto il foglio": la guardia anti-copia sta in `copia_libro`).
- Copia a memoria (come ia20, soglie severe): 5-grammi e 3-grammi di parole, righe intere (>= 4 parole) uguali a righe d'addestramento, e la quota di
  righe uguali a una riga VERA qualunque; ogni numero ha il suo riferimento "naturale" (le righe dei fogli tenuti fuori contro l'addestramento).
"""
import math
import os
import sys
import time
from collections import Counter, OrderedDict

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
import rifare_dati as RD  # noqa: E402

KAPPA = float(os.environ.get('KAPPA32', 300))        # memoria di partenza della correzione (coppie di segni "virtuali" per riga della tabella)
# le manopole: (nome, neutro nel cubo [0,1], come si traduce)
NOMI = ('T_primo', 'T_int', 'T_fine', 'T_eol', 'T_riga', 'top_p', 'w_cont', 'w_tri', 's')
T_LO, T_HI = 0.6, 1.4
NEUTRO = OrderedDict([('T_primo', 1.0), ('T_int', 1.0), ('T_fine', 1.0), ('T_eol', 1.0), ('T_riga', 1.0), ('top_p', 1.0), ('w_cont', 0.0), ('w_tri', 0.0), ('s', 0.0)])
DIM = len(NOMI)


def da_cubo(u):
    """Il vettore u in [0,1]^8 -> le manopole. Temperature: scala logaritmica fra 0,6 e 1,4 (neutro 1: u = 0,6035). top_p: 0,6 + 0,5 u, saturato a 1
    (u >= 0,8 e' "niente top-p"). w_cont e w_tri: 3 (u - 0,2), tagliati a zero sotto 0,2 (massimo 2,4). s: (u - 0,1) / 0,8 tagliato in [0,1]. Il valore neutro sta sempre dentro."""
    u = np.clip(np.asarray(u, float), 0.0, 1.0)
    T = lambda x: float(math.exp(math.log(T_LO) + (math.log(T_HI) - math.log(T_LO)) * x))
    return OrderedDict([('T_primo', T(u[0])), ('T_int', T(u[1])), ('T_fine', T(u[2])), ('T_eol', T(u[3])), ('T_riga', T(u[4])),
                        ('top_p', float(min(1.0, 0.6 + 0.5 * u[5]))), ('w_cont', float(max(0.0, 3.0 * (u[6] - 0.2)))),
                        ('w_tri', float(max(0.0, 3.0 * (u[7] - 0.2)))), ('s', float(min(1.0, max(0.0, (u[8] - 0.1) / 0.8))))])


def neutro_cubo():
    t = lambda x: (math.log(x) - math.log(T_LO)) / (math.log(T_HI) - math.log(T_LO))
    return np.array([t(1.0)] * 5 + [0.9, 0.1, 0.1, 0.05])


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def logsumexp(z):
    m = z.max()
    return float(m + math.log(np.exp(z - m).sum()))


def tabella_bigrammi(f_add):
    """Probabilita' (V+1) x V dei segni di scrittura (spazio, fine riga, glifi) dato il segno prima, dalle pagine d'addestramento. La riga V e' "inizio di riga"."""
    voc = I7.vocabolario()
    primo = voc['primo_contenuto']
    V = len(voc['segni'])
    dp = I16.dati_pagine()
    ins = set(f_add)
    c = np.zeros((V + 1, V))
    for d in dp.values():
        if d['foglio'] not in ins:
            continue
        tok = d['tok']
        for a, b in zip(tok[:-1], tok[1:]):
            b = int(b)
            if b < primo:
                continue
            a = int(a)
            c[a if a >= primo else V, b] += 1
    return c


def tabella_trigrammi(f_add):
    """Probabilita' del segno di scrittura dato i due segni prima, dalle pagine d'addestramento: dizionario (due prima, uno prima) -> vettore (V). Gli stati sono come
    in `tabella_bigrammi` (V = inizio di riga). Solo i contesti visti."""
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
        for t in range(2, len(tok)):
            b = tok[t]
            if b < primo:
                continue
            k = (stato[t - 2] if tok[t - 2] >= primo else V, stato[t - 1])
            v = c.get(k)
            if v is None:
                v = c[k] = np.zeros(V)
            v[b] += 1
    out = {}
    for k, v in c.items():
        l = v + 0.05 * (v > 0)
        out[k] = l / l.sum()
    return out


class Scrittore:
    def __init__(self, cartella):
        self.P = RD.Pieno(cartella)
        self.ctx = self.P.ctx
        self.voc = I7.vocabolario()
        self.D = I7.divisore()
        c = tabella_bigrammi(self.P.f_add)
        V = c.shape[1]
        lisc = c + 0.05 * (c.sum(1, keepdims=True) > 0)
        den = lisc.sum(1, keepdims=True)
        self.T = np.where(den > 0, lisc / np.maximum(den, 1e-12), 1.0 / V)
        self.logT = np.log(np.maximum(self.T, 1e-9))
        self.V = V
        self.T3 = tabella_trigrammi(self.P.f_add)
        self.logT3 = {k: np.log(np.maximum(v, 1e-9)) for k, v in self.T3.items()}
        self.regole = I7.Penna(None, self.voc)
        righe = I7.libro_vero()
        self.pp = I7.per_pagina(righe)
        self.cap = max(4 + sum(3 + self.voc['lmax'] + 2 for _ in rp) for rp in self.pp.values())
        self._pen = {}

    def penna(self, s):
        s = round(float(s), 3)
        if s not in self._pen:
            if len(self._pen) > 4:
                self._pen.clear()
            m = self.P.modello(s)
            self._pen[s] = (m, GM.Penna20(m, self.ctx, self.cap + 8))
        return self._pen[s]

    # ---- una scelta
    def scegli(self, lg, amm, prev, n_gl, prima_riga, k, G, rng, prev2=None, G3=None):
        SP, EOL = self.ctx.SP, self.ctx.EOL
        idx = np.asarray(amm)
        z = np.asarray(lg, float)[idx]
        if k['w_cont'] > 0:
            g = (G[prev] + KAPPA * self.T[prev]) / (G[prev].sum() + KAPPA)
            z = z + k['w_cont'] * (self.logT[prev][idx] - np.log(np.maximum(g[idx], 1e-9)))
        if k.get('w_tri', 0.0) > 0 and G3 is not None and prev2 is not None:
            kk = (prev2, prev)
            t3 = self.T3.get(kk)
            if t3 is not None:
                g3 = G3.get(kk)
                g3 = (np.zeros(self.V) if g3 is None else g3)
                gg = (g3 + KAPPA * t3) / (g3.sum() + KAPPA)
                z = z + k['w_tri'] * (self.logT3[kk][idx] - np.log(np.maximum(gg[idx], 1e-9)))
        dl = (idx == SP) | (idx == EOL)
        if not dl.any():                                                     # primo glifo
            return int(idx[self._glifo(z, k['T_riga'] if prima_riga else k['T_primo'], k['top_p'], rng)])
        if dl.all():                                                         # solo delimitatori
            if len(idx) == 1:
                return int(idx[0])
            return int(idx[self._due(z, k['T_eol'], rng)])
        m = logsumexp(z[dl]) - logsumexp(z[~dl])                             # logit della probabilita' che la parola finisca
        pe = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, m / k['T_fine']))))
        if rng.random() < pe:
            ii = np.nonzero(dl)[0]
            if len(ii) == 1:
                return int(idx[ii[0]])
            return int(idx[ii[self._due(z[ii], k['T_eol'], rng)]])
        ii = np.nonzero(~dl)[0]
        return int(idx[ii[self._glifo(z[ii], k['T_int'], k['top_p'], rng)]])

    @staticmethod
    def _glifo(z, T, top_p, rng):
        p = softmax(z / T)
        if top_p < 1.0:
            o = np.argsort(-p)
            cum = np.cumsum(p[o])
            n = int(np.searchsorted(cum, top_p) + 1)
            q = np.zeros_like(p)
            q[o[:n]] = p[o[:n]]
            p = q / q.sum()
        return I16.campiona(p, rng)

    @staticmethod
    def _due(z, T, rng):
        return I16.campiona(softmax(z / T), rng)

    # ---- una pagina e un libro
    def pagina(self, pen, rp, k, G, rng, G3=None):
        voc, D, regole = self.voc, self.D, self.regole
        SP, EOL = self.ctx.SP, self.ctx.EOL
        pen.apri()
        lg = None
        for t in I7.testa_pagina(rp, voc):
            lg = pen.dai(t)
        out = []
        for j, x in enumerate(rp):
            for t in I7.testa_riga(x, j, voc, D):
                lg = pen.dai(t)
            parole, lung, prima, fine, prev, prev2 = [], 0, 'inizio', False, self.V, self.V
            while not fine:
                parola = []
                while True:
                    amm = regole.ammessi(parola, lung, prima)
                    s = self.scegli(lg, amm, prev, len(parola), (not parole) and (not parola), k, G, rng, prev2, G3)
                    G[prev, s] += 1
                    if G3 is not None and k.get('w_tri', 0.0) > 0:
                        v3 = G3.get((prev2, prev))
                        if v3 is None:
                            v3 = G3[(prev2, prev)] = np.zeros(self.V)
                        v3[s] += 1
                    prev2, prev = prev, s
                    lg = pen.dai(s)
                    if s == EOL:
                        parole.append(''.join(parola))
                        fine = True
                        break
                    lung += 1
                    if s == SP:
                        parole.append(''.join(parola))
                        prima = 'spazio'
                        break
                    parola.append(regole.unita[s])
                    prima = 'segno'
            out.append((x['pagina'], x['ini'], parole))
        return out

    def libro(self, u, seme, fogli=None):
        """Un libro (o solo i fogli `fogli`) con le manopole `u` (cubo [0,1]^8). -> (lista (pagina, inizio, parole), manopole)."""
        k = da_cubo(u)
        m, pen = self.penna(k['s'])
        rng = np.random.default_rng(seme)
        G = np.zeros((self.V + 1, self.V))
        G3 = {}
        ins = None if fogli is None else set(fogli)
        t = []
        for pag, rp in self.pp.items():
            if ins is not None and I7.foglio_di(pag) not in ins:
                continue
            t += self.pagina(pen, rp, k, G, rng, G3)
        return t, k


# ---------------------------------------------------------------- la guardia anti-copia

def righe_di_fogli(fogli):
    ins = set(fogli)
    return [x['parole'] for x in I7.libro_vero() if x['foglio'] in ins]


def conti_naturali(f_add, f_fuori):
    """Il riferimento "naturale": le righe dei fogli tenuti fuori contro quelle d'addestramento (cio' che copia un testo vero mai visto)."""
    add = righe_di_fogli(f_add)
    return I7.conti_copia(righe_di_fogli(f_fuori), add)


def copia_libro(t, f_add):
    """Conti di copia delle pagine `t` contro il testo d'addestramento (5-grammi, 3-grammi, righe intere, parole nuove) e quota di righe (>= 4 parole) uguali a
    una riga VERA qualunque (anche dei fogli tenuti fuori)."""
    add = righe_di_fogli(f_add)
    gen = [ps for _, _, ps in t]
    c = I7.conti_copia(gen, add)
    vere = {tuple(r) for r in (x['parole'] for x in I7.libro_vero()) if len(r) >= 4}
    g = [tuple(r) for r in gen if len(r) >= 4]
    c['righe vere'] = [sum(r in vere for r in g), len(g)]
    return c


if __name__ == '__main__':
    pass
