# -*- coding: utf-8 -*-
"""IA32, modulo di supporto: CMA-ES minimale (senza gradiente), riprendibile.

In parole semplici
- Un ottimizzatore "a popolazioni": a ogni generazione si propongono `lam` insiemi di manopole attorno a una media, si misura quanto vanno bene, e media e
  larghezza si aggiornano verso i migliori (Hansen, "The CMA Evolution Strategy: A Tutorial", 2016; scritto qui da zero, senza la libreria `cma`, che non c'e').
- Le manopole vivono nel cubo [0,1]^d (le traduzioni in temperature ecc. sono in `rifare_scrittura.da_cubo`); i punti proposti fuori dal cubo si riportano dentro
  (taglio) e l'aggiornamento usa i punti riportati.
- Tutto lo stato (media, larghezza, matrici) e' un dizionario JSON: si salva a ogni generazione e si riprende (`RIPRENDI=1`). I punti di una generazione
  dipendono solo dal seme e dal numero di generazione, quindi una generazione interrotta si rifa uguale.
"""
import math

import numpy as np


class CMA:
    def __init__(self, x0, sigma0=0.25, lam=None, seme=0, limiti=(0.0, 1.0)):
        n = len(x0)
        self.n = n
        self.lam = int(lam or (4 + int(3 * math.log(n))))
        self.mu = self.lam // 2
        w = np.log(self.mu + 0.5) - np.log(np.arange(1, self.mu + 1))
        self.w = w / w.sum()
        self.mueff = 1.0 / float((self.w ** 2).sum())
        self.cc = (4 + self.mueff / n) / (n + 4 + 2 * self.mueff / n)
        self.cs = (self.mueff + 2) / (n + self.mueff + 5)
        self.c1 = 2 / ((n + 1.3) ** 2 + self.mueff)
        self.cmu = min(1 - self.c1, 2 * (self.mueff - 2 + 1 / self.mueff) / ((n + 2) ** 2 + self.mueff))
        self.damps = 1 + 2 * max(0.0, math.sqrt((self.mueff - 1) / (n + 1)) - 1) + self.cs
        self.chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
        self.mean = np.array(x0, float)
        self.sigma = float(sigma0)
        self.C = np.eye(n)
        self.pc = np.zeros(n)
        self.ps = np.zeros(n)
        self.gen = 0
        self.seme = int(seme)
        self.lo, self.hi = limiti

    def _eig(self):
        C = (self.C + self.C.T) / 2
        d, B = np.linalg.eigh(C)
        d = np.maximum(d, 1e-20)
        return B, np.sqrt(d)

    def ask(self):
        """I `lam` punti della generazione corrente (deterministici dato seme e numero di generazione). -> (punti riportati nel cubo, punti grezzi)."""
        rng = np.random.default_rng(self.seme * 100003 + self.gen)
        B, D = self._eig()
        zs = rng.standard_normal((self.lam, self.n))
        ys = (zs * D) @ B.T
        xs = self.mean + self.sigma * ys
        return np.clip(xs, self.lo, self.hi), xs

    def tell(self, xs_riportati, valori):
        """Aggiorna con i punti (riportati nel cubo) e i loro valori (da minimizzare)."""
        xs = np.asarray(xs_riportati, float)
        ordine = np.argsort(valori, kind='stable')
        xs = xs[ordine]
        vecchia = self.mean.copy()
        self.mean = self.w @ xs[:self.mu]
        y = (self.mean - vecchia) / self.sigma
        B, D = self._eig()
        invsqrtC = B @ np.diag(1 / D) @ B.T
        self.ps = (1 - self.cs) * self.ps + math.sqrt(self.cs * (2 - self.cs) * self.mueff) * (invsqrtC @ y)
        hsig = float(np.linalg.norm(self.ps) / math.sqrt(1 - (1 - self.cs) ** (2 * (self.gen + 1))) / self.chiN < 1.4 + 2 / (self.n + 1))
        self.pc = (1 - self.cc) * self.pc + hsig * math.sqrt(self.cc * (2 - self.cc) * self.mueff) * y
        artmp = (xs[:self.mu] - vecchia) / self.sigma
        self.C = ((1 - self.c1 - self.cmu) * self.C + self.c1 * (np.outer(self.pc, self.pc) + (1 - hsig) * self.cc * (2 - self.cc) * self.C)
                  + self.cmu * (artmp.T * self.w) @ artmp)
        self.sigma *= math.exp((self.cs / self.damps) * (np.linalg.norm(self.ps) / self.chiN - 1))
        self.sigma = float(min(self.sigma, 0.6))
        self.gen += 1

    def stato(self):
        return dict(n=self.n, lam=self.lam, mean=self.mean.tolist(), sigma=self.sigma, C=self.C.tolist(), pc=self.pc.tolist(), ps=self.ps.tolist(),
                    gen=self.gen, seme=self.seme, lo=self.lo, hi=self.hi)

    @classmethod
    def da_stato(cls, s):
        c = cls(s['mean'], s['sigma'], s['lam'], s['seme'], (s['lo'], s['hi']))
        c.C, c.pc, c.ps, c.gen = np.array(s['C']), np.array(s['pc']), np.array(s['ps']), int(s['gen'])
        return c


def prova():
    """Controllo dello strumento: sfera e ellissoide mal condizionato in 8 dimensioni, con rumore. -> (valore finale sfera, distanza della media dall'ottimo)."""
    centro = np.array([0.3, 0.7, 0.5, 0.2, 0.8, 0.4, 0.6, 0.1])
    scala = np.array([1, 3, 1, 5, 1, 2, 1, 4], float)
    c = CMA(np.full(8, 0.5), 0.25, 10, seme=3)
    rng = np.random.default_rng(0)
    for _ in range(40):
        xs, _ = c.ask()
        f = [float((((x - centro) * scala) ** 2).sum()) + 0.01 * rng.standard_normal() for x in xs]
        c.tell(xs, f)
    return float((((c.mean - centro) * scala) ** 2).sum()), float(np.linalg.norm(c.mean - centro))


if __name__ == '__main__':
    print(prova())
