# -*- coding: utf-8 -*-
"""Motore dell'inferenza per simulazione (ABC) di ia28 (modulo di supporto, non e' un esperimento).

Che cosa fa, in parole semplici. Si ha una tabella di testi simulati: per ognuno, la famiglia di procedimenti, i parametri con cui e'
stato scritto (riportati a [0, 1] sulla scala dell'a priori) e le statistiche di sintesi misurate. Dato un testo vero (le sue
statistiche), il motore dice:
  1. QUALE FAMIGLIA l'ha scritto con piu' probabilita' (foresta casuale a due livelli, "ABC-RF": una foresta sceglie la famiglia, una
     seconda stima la probabilita' di sbagliare nel punto dove sta il testo vero; Pudlo e altri 2016, da ricontrollare);
  2. CON QUALI PARAMETRI, per ogni famiglia (ABC "semi-automatica" con regressione locale: una foresta predice i parametri dalle
     statistiche, le previsioni diventano le statistiche di sintesi, si tengono le simulazioni piu' vicine al vero in quello spazio e
     si correggono con una regressione lineare pesata; Fearnhead e Prangle 2012, Beaumont e altri 2002, da ricontrollare);
  3. QUANTO sono stimabili i parametri: R^2 "fuori sacco" della foresta (previsione di ogni simulazione fatta senza di essa). Un
     parametro con R^2 sotto SOGLIA_R2 e' "non stimabile" e non si legge.
La verifica predittiva e il controllo di "fuori da tutte le famiglie" sono in `ppc` e `distanza_dal_piu_vicino`. Il modulo non
legge nessun testo: lavora su matrici di numeri.
"""
import math
import os
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

SOGLIA_R2 = 0.25            # un parametro e' "stimabile" se la foresta lo prevede con R^2 fuori sacco >= 0,25 (fissato prima)
FRAZIONE_ACCETTATE = 0.02   # quota di simulazioni tenute nella regressione locale
MIN_ACCETTATE = 150
N_POSTERIORE = 2000
LIVELLO = (0.05, 0.95)      # intervallo al 90%
SOGLIA_PPC = 0.05           # la verifica predittiva "passa" se il valore p e' almeno questo
SOGLIA_Z_MANCATA = 3.0      # una statistica e' "mancata" se il vero sta oltre 3 scarti standard dal predetto


def scala_robusta(S):
    """Mediana e scarto robusto (1,4826 MAD) di ogni colonna; mai zero."""
    med = np.median(S, axis=0)
    sd = 1.4826 * np.median(np.abs(S - med), axis=0)
    sd = np.where(sd < 1e-12, np.maximum(S.std(axis=0), 1e-12), sd)
    return med, sd


class Motore:
    """Foreste addestrate sulla tabella. `S`: (n x p) statistiche; `fam`: (n) indice di famiglia; `U`: lista (una per famiglia) di
    matrici (n_f x d_f) di parametri in [0, 1], nello stesso ordine di `S` ristretto alla famiglia."""

    def __init__(self, nomi_fam, S, fam, U, n_alberi=300, n_alberi_par=200, n_jobs=1, seme=28):
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        self.nomi_fam = list(nomi_fam)
        self.S = np.asarray(S, dtype=float)
        self.fam = np.asarray(fam, dtype=int)
        self.med, self.sd = scala_robusta(self.S)
        Z = self.zeta(self.S)
        self.Z = Z
        self.lda = LinearDiscriminantAnalysis().fit(Z, self.fam)
        X = self._aggiungi_lda(Z)
        self.rfc = RandomForestClassifier(n_estimators=n_alberi, min_samples_leaf=2, max_features='sqrt', oob_score=True, n_jobs=n_jobs,
                                          random_state=seme).fit(X, self.fam)
        oob = self.rfc.oob_decision_function_
        oob = np.where(np.isnan(oob), 1.0 / len(self.nomi_fam), oob)
        self.oob_pred = oob.argmax(axis=1)
        self.errore_oob = float((self.oob_pred != self.fam).mean())
        self.confusione_oob = np.array([[int(((self.fam == i) & (self.oob_pred == j)).sum()) for j in range(len(self.nomi_fam))]
                                        for i in range(len(self.nomi_fam))])
        err = (self.oob_pred != self.fam).astype(float)
        self.rfe = RandomForestRegressor(n_estimators=max(50, n_alberi // 3), min_samples_leaf=5, max_features=0.5, n_jobs=n_jobs,
                                         random_state=seme + 1).fit(X, err)
        self.U, self.zf, self.rfr, self.proj, self.r2, self.proj_sd = [], [], [], [], [], []
        for f in range(len(self.nomi_fam)):
            Zf = Z[self.fam == f]
            Uf = np.asarray(U[f], dtype=float)
            assert len(Zf) == len(Uf), 'tabella: %s ha %d statistiche e %d parametri' % (self.nomi_fam[f], len(Zf), len(Uf))
            rr = RandomForestRegressor(n_estimators=n_alberi_par, min_samples_leaf=5, max_features=0.5, oob_score=True, n_jobs=n_jobs,
                                       random_state=seme + 10 + f).fit(Zf, Uf)
            pr = rr.oob_prediction_.reshape(len(Zf), -1)
            var = Uf.var(axis=0)
            r2 = 1.0 - ((Uf - pr) ** 2).mean(axis=0) / np.maximum(var, 1e-12)
            self.U.append(Uf)
            self.zf.append(Zf)
            self.rfr.append(rr)
            self.proj.append(pr)
            self.r2.append(r2)
            self.proj_sd.append(np.maximum(1.4826 * np.median(np.abs(pr - np.median(pr, axis=0)), axis=0), 1e-6))

    # ---- utilita'
    def zeta(self, S):
        return (np.atleast_2d(np.asarray(S, dtype=float)) - self.med) / self.sd

    def _aggiungi_lda(self, Z):
        return np.hstack([Z, self.lda.transform(Z)])

    # ---- scelta della famiglia
    def scelta_famiglia(self, s):
        """Probabilita' della foresta per ogni famiglia nel punto `s`, la famiglia preferita e la probabilita' a posteriori ABC-RF
        (1 meno l'errore previsto dalla seconda foresta nel punto)."""
        X = self._aggiungi_lda(self.zeta(s))
        p = self.rfc.predict_proba(X)[0]
        k = int(p.argmax())
        err = float(np.clip(self.rfe.predict(X)[0], 0.0, 1.0))
        return OrderedDict(prob=[float(x) for x in p], preferita=k, nome=self.nomi_fam[k], prob_posteriori=1.0 - err)

    # ---- parametri
    def posteriore(self, s, f, n=N_POSTERIORE, seme=1, frazione=FRAZIONE_ACCETTATE):
        """Campioni (n x d) in [0, 1] della distribuzione a posteriori dei parametri della famiglia f dato `s` (ABC con regressione
        locale nello spazio delle previsioni della foresta), e la distanza del vero dalla simulazione piu' vicina in quello spazio."""
        z = self.zeta(s)
        po = self.rfr[f].predict(z).reshape(-1)
        pr, sd, Uf = self.proj[f], self.proj_sd[f], self.U[f]
        d = np.sqrt((((pr - po) / sd) ** 2).sum(axis=1))
        k = int(min(len(d), max(MIN_ACCETTATE, frazione * len(d))))
        idx = np.argpartition(d, k - 1)[:k]
        h = max(float(d[idx].max()), 1e-12)
        w = 1.0 - (d[idx] / h) ** 2
        w = np.maximum(w, 1e-9)
        X = np.hstack([np.ones((k, 1)), pr[idx] - po])
        sw = np.sqrt(w)[:, None]
        # regressione lineare pesata, con una piccola lisciatura (ridge) per non esplodere con poche simulazioni accettate
        A = (X * sw).T @ (X * sw) + 1e-3 * np.eye(X.shape[1])
        B = np.linalg.solve(A, (X * sw).T @ (Uf[idx] * sw))
        adj = Uf[idx] - (pr[idx] - po) @ B[1:]
        adj = np.clip(adj, 0.0, 1.0)
        rng = np.random.default_rng(seme)
        scelta = rng.choice(k, size=n, p=w / w.sum())
        return adj[scelta], float(d.min()), k

    def riassunto(self, camp):
        """Mediana e intervallo al 90% (colonna per colonna) di campioni (n x d)."""
        return [(float(np.quantile(camp[:, j], 0.5)), float(np.quantile(camp[:, j], LIVELLO[0])), float(np.quantile(camp[:, j], LIVELLO[1])))
                for j in range(camp.shape[1])]

    def stimabili(self, f):
        return [bool(r >= SOGLIA_R2) for r in self.r2[f]]

    # ---- fuori dalle famiglie
    def distanza_dal_piu_vicino(self, s, f, n_riferimento=2000, seme=1):
        """Distanza (spazio delle statistiche, scarti robusti) di `s` dalla simulazione piu' vicina della famiglia f, e valore p = quota di
        simulazioni della famiglia che stanno piu' lontano dalle altre del vero dalle sue (distanza al piu' vicino, lasciando fuori se
        stessa). Un valore p vicino a 0 dice che il vero sta fuori dalla nuvola dei simulati."""
        from scipy.spatial import cKDTree
        z = self.zeta(s)[0]
        Zf = self.zf[f]
        albero = cKDTree(Zf)
        d_obs = float(albero.query(z)[0])
        rng = np.random.default_rng(seme)
        idx = rng.choice(len(Zf), size=min(n_riferimento, len(Zf)), replace=False)
        dd = albero.query(Zf[idx], k=2)[0][:, 1]
        return d_obs, float((dd >= d_obs).mean())


def ppc(s_obs, S_pp, nomi):
    """Verifica predittiva. `S_pp`: (m x p) statistiche di testi simulati dalla distribuzione a posteriori. Per ogni statistica lo
    scarto standardizzato del vero dalla media dei simulati; la statistica globale e' la somma dei quadrati; il valore p e' la quota di
    simulati con somma dei quadrati (rispetto agli altri simulati) almeno quanto quella del vero. Restituisce un dizionario di numeri:
    chi2, p, rms_z (radice della media dei quadrati: quanto, in media, il vero sta fuori), z per statistica e l'elenco delle mancate."""
    S_pp = np.asarray(S_pp, dtype=float)
    m, sd = S_pp.mean(axis=0), np.maximum(S_pp.std(axis=0, ddof=1), 1e-12)
    z = (np.asarray(s_obs, dtype=float) - m) / sd
    chi_obs = float((z ** 2).sum())
    chi_pp = (((S_pp - m) / sd) ** 2).sum(axis=1)
    p = float((chi_pp >= chi_obs).mean())
    mancate = [nomi[j] for j in range(len(nomi)) if abs(z[j]) > SOGLIA_Z_MANCATA]
    return OrderedDict(chi2=chi_obs, p=p, rms_z=float(math.sqrt(chi_obs / len(z))), z=[float(x) for x in z], mancate=mancate)


def copertura(veri, intervalli):
    """Quota di valori veri dentro il loro intervallo (liste parallele; intervalli = (lo, hi))."""
    veri = np.asarray(veri, dtype=float)
    lo = np.array([a for a, _ in intervalli])
    hi = np.array([b for _, b in intervalli])
    return float(((veri >= lo) & (veri <= hi)).mean())


def prova_inferenza():
    """Prove interne su un modello giocattolo con parametri noti: due famiglie di numeri (il loro parametro si ritrova con R^2 alto, la
    famiglia si ritrova, un punto lontano da entrambe e' 'fuori')."""
    ris = OrderedDict()
    rng = np.random.default_rng(3)
    n = 2500

    def sim(f, u):
        # famiglia 0: statistiche (a, b) = (u0, u1) + rumore; famiglia 1: (a, b) = (1 + u0, -u1) + rumore; terza statistica = rumore puro
        if f == 0:
            base = np.stack([u[:, 0], u[:, 1]], 1)
        else:
            base = np.stack([1.0 + u[:, 0], -u[:, 1]], 1)
        return np.hstack([base + 0.05 * rng.standard_normal(base.shape), rng.standard_normal((len(u), 1))])
    U0, U1 = rng.random((n, 2)), rng.random((n, 2))
    S = np.vstack([sim(0, U0), sim(1, U1)])
    fam = np.array([0] * n + [1] * n)
    M = Motore(['A', 'B'], S, fam, [U0, U1], n_alberi=60, n_alberi_par=60)
    ris['la famiglia si riconosce (errore fuori sacco sotto il 10%)'] = M.errore_oob < 0.10
    ris['i due parametri sono stimabili (R2 >= 0,25)'] = all(M.stimabili(0)) and all(M.stimabili(1))
    # un testo "vero" della famiglia 0 con parametri (0,3, 0,6)
    u_v = np.array([[0.3, 0.6]])
    s_v = sim(0, u_v)[0]
    sc = M.scelta_famiglia(s_v)
    ris['sceglie la famiglia giusta'] = sc['preferita'] == 0 and sc['prob'][0] > 0.8
    camp, dmin, k = M.posteriore(s_v, 0, n=800)
    ris_ = M.riassunto(camp)
    ris['parametro 0 ritrovato nell\'intervallo'] = ris_[0][1] <= 0.3 <= ris_[0][2]
    ris['parametro 1 ritrovato nell\'intervallo'] = ris_[1][1] <= 0.6 <= ris_[1][2]
    ris['intervallo piu\' stretto dell\'a priori'] = (ris_[0][2] - ris_[0][1]) < 0.5
    # copertura su 80 testi di prova della famiglia 0
    ut = rng.random((80, 2))
    st = sim(0, ut)
    inside = [[], []]
    for i in range(80):
        c, _, _ = M.posteriore(st[i], 0, n=400, seme=i)
        r = M.riassunto(c)
        for j in (0, 1):
            inside[j].append((r[j][1], r[j][2]))
    cop = [copertura(ut[:, j], inside[j]) for j in (0, 1)]
    ris['copertura al 90% fra 0,75 e 1,0 (parametri 0 e 1)'] = all(0.75 <= c <= 1.0 for c in cop)
    # un punto fuori da tutto: lontano dai simulati
    lontano = np.array([8.0, -8.0, 0.0])
    d, p = M.distanza_dal_piu_vicino(lontano, 0)
    d2, p2 = M.distanza_dal_piu_vicino(s_v, 0)
    ris['il punto lontano ha valore p 0 e il punto vero no'] = p == 0.0 and p2 > 0.05
    # verifica predittiva: punto compatibile (p alto) e punto spostato (p basso)
    pp = np.array([sim(0, np.array([[0.3, 0.6]]))[0] for _ in range(300)])
    r1 = ppc(s_v, pp, ['a', 'b', 'c'])
    r2 = ppc(s_v + np.array([1.0, 0.0, 0.0]), pp, ['a', 'b', 'c'])
    ris['ppc: il vero compatibile passa'] = r1['p'] > SOGLIA_PPC
    ris['ppc: il vero spostato fallisce e nomina la statistica mancata'] = r2['p'] == 0.0 and 'a' in r2['mancate']
    return ris


if __name__ == '__main__':
    r = prova_inferenza()
    for k, v in r.items():
        print('%-70s %s' % (k, 'ok' if v else 'FALLITA'))
    sys.exit(0 if all(r.values()) else 1)
