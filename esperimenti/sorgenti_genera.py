# -*- coding: utf-8 -*-
"""Supporto di ia27 (modulo, non e' un esperimento): il modello a sorgenti SCRIVE testo.

Stessa storia del modello che stima (`sorgenti_modello`), letta al contrario: per ogni parola si pesca la sorgente (L, S, F, R, P, con le quote della lingua
della pagina; se una sorgente non esiste in quel punto, per esempio R a inizio pagina, si rinormalizza sulle altre), poi la parola da quella sorgente:
L e S dal lessico (primo glifo scelto con il fattore di contatto, poi la parola fra quelle che cominciano cosi'), F glifo per glifo dal modello di forma,
R e P: si sceglie la parola da ricopiare (peso del nucleo, per distanza), il tipo di ritocco, il posto e il glifo nuovo. Dopo ogni parola la riga finisce
con il rischio di fine riga (stesso della stima), dentro la fascia di lunghezza data dalla disposizione.
Usato per: i libri del modello (giudicati come quelli di ia20-ia24) e i testi sintetici con parametri noti dei controlli.
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import sorgenti_dati as SD  # noqa: E402
import sorgenti_modello as SM  # noqa: E402

PROVE_MAX = 8
PAROLE_RIGA_MAX = 60
LUNG_PAROLA_MAX = 18


class Lessico(object):
    """Un lessico da cui si pesca: parole con conteggi, raggruppate per primo glifo."""

    def __init__(self, contatore, voc):
        self.voc = voc
        self.parole = [w for w, c in contatore.items() if c > 0]
        cnt = np.array([contatore[w] for w in self.parole], dtype=float)
        G = voc.G
        self.M = np.zeros(G)
        self.per_f = {}
        primi = np.array([voc.gid[w[0]] for w in self.parole]) if self.parole else np.zeros(0, dtype=int)
        for f in range(G):
            idx = np.where(primi == f)[0]
            if len(idx):
                self.per_f[f] = (idx, np.cumsum(cnt[idx]))
                self.M[f] = cnt[idx].sum()
        self.M = self.M / max(self.M.sum(), 1.0)

    def campiona(self, g_riga, rng):
        p = self.M * g_riga
        s = p.sum()
        if s <= 0:
            return None
        f = int(rng.choice(self.voc.G, p=p / s))
        idx, cum = self.per_f[f]
        i = int(np.searchsorted(cum, rng.random() * cum[-1], side='right'))
        return self.parole[idx[min(i, len(idx) - 1)]]


def campiona_forma(forma, MF, voc, g_riga, rng):
    p = MF * g_riga
    s = p.sum()
    if s <= 0:
        return None
    f = int(rng.choice(voc.G, p=p / s))
    q = forma.q
    a, b = q, forma.idx[voc.unita[f]]
    w = [voc.unita[f]]
    while len(w) < LUNG_PAROLA_MAX:
        pr = 2.0 ** forma.l3[a, b, :]
        pr[q - 1] = 0.0
        x = int(rng.choice(q + 1, p=pr / pr.sum()))
        if x == q:
            break
        w.append(forma.glifi[x])
        a, b = b, x
    return tuple(w)


def ritocca(c, tipo, par, ctx, rng, voc, ritocco_contatto):
    """Un ritocco di tipo 1 (cambia), 2 (aggiunge), 3 (toglie) alla parola c (tupla di glifi). -> parola nuova o None se non e' possibile."""
    n = len(c)
    if tipo == 3 and n < 2:
        return None
    cnt = np.array(SM._cnt_pos(tipo, n))
    om = par.omega[tipo - 1] * cnt
    cl = int(rng.choice(3, p=om / om.sum()))
    if tipo == 2:
        pos = 0 if cl == 0 else n if cl == 2 else int(rng.integers(1, n))
    else:
        pos = 0 if cl == 0 else n - 1 if cl == 2 else int(rng.integers(1, n - 1))
    if tipo == 3:
        return c[:pos] + c[pos + 1:]
    ct = ctx if ritocco_contatto else 0
    pr = par.tau[tipo - 1, 0 if pos == 0 else 1, ct].copy()
    if tipo == 1:
        pr[voc.gid[c[pos]]] = 0.0
    if pr.sum() <= 0:
        return None
    g = voc.unita[int(rng.choice(voc.G, p=pr / pr.sum()))]
    return c[:pos] + (g,) + c[pos + 1:] if tipo == 1 else c[:pos] + (g,) + c[pos:]


class Scrittore(object):
    """Scrive pagine con un modello (parametri `par`, lessici `basi`, rischio `rischio`, versione `var`)."""

    def __init__(self, par, basi, rischio, voc, var, valida=None):
        self.par, self.basi, self.rischio, self.voc, self.var = par, basi, rischio, voc, var
        self.valida = valida or (lambda w: True)
        H = basi.H
        self.LL = Lessico({w: basi.conteggio_L(w, H) for w in basi.cT}, voc)
        self.LS = {s: Lessico(basi.sT[s], voc) for s in range(basi.SG)}
        self.forma = basi.formas[H]
        self.MF = basi.MF[H]
        self.gruppi = basi.gruppi_sl
        self.G = voc.G

    def _parola_fresca(self, sorgente, ctx, sg, rng):
        g = self.par.g[ctx]
        if sorgente == 0:
            return self.LL.campiona(g, rng)
        if sorgente == 1:
            return self.LS[sg].campiona(g, rng)
        return campiona_forma(self.forma, self.MF, self.voc, g, rng)

    def _copia(self, cand, t, rigaini, ri, ctx, src, rng):
        """cand: lista di (indice token, riga, parola); sceglie e ritocca. t: indice della parola da scrivere, rigaini: indice della prima parola della
        riga in corso, ri: riga in corso. src 0 = R, 1 = P."""
        par, voc = self.par, self.voc
        if not cand:
            return None
        if src == 0:
            ks = [SM._classe_R(t, j, rigaini) for j, _, _ in cand]
            kap = par.kR[ks] * par.phiR[[self.basi.bucket(w) for _, _, w in cand]]
            gam = par.gamma_R
        else:
            kap = np.array([par.kP[SM.bin_P(ri - r)] * par.phiP[self.basi.bucket(w)] for _, r, w in cand])
            gam = par.gamma_P
        gg = np.clip(par.g[ctx], *SM.SOGLIA_G) ** gam if gam else 1.0
        fj = np.array([voc.gid[w[0]] for _, _, w in cand])
        p = kap * (gg[fj] if gam else 1.0)
        p = p / p.sum()
        for _ in range(PROVE_MAX):
            j = int(rng.choice(len(cand), p=p))
            c = cand[j][2]
            tipo = int(rng.choice(4, p=par.rho[src]))
            w = c if tipo == 0 else ritocca(c, tipo, par, ctx, rng, voc, self.var['ritocco_contatto'])
            if w is not None and len(w) > 0 and self.valida(w):
                return w
        return None

    def scrivi_pagina(self, pagina, rng):
        """Una pagina con la disposizione di `pagina` (righe, fasce, inizio paragrafo). -> Pagina nuova."""
        par, voc, var = self.par, self.voc, self.var
        sg = self.gruppi.get((pagina.sezione, pagina.lingua), -1)
        gp = SM.lingua_gruppo(pagina.lingua)
        piS = sg >= 0 and self.basi.NS[self.basi.H, sg] >= SM.MIN_S
        righe_nuove, tutte = [], []                     # tutte: (indice token, riga, parola)
        for ri, r in enumerate(pagina.righe):
            parole, cum = [], -1
            rigaini = len(tutte)
            while True:
                k = len(parole)
                ctx = (voc.G + (1 if r.ini else 0)) if k == 0 else voc.gid[parole[-1][-1]]
                t = len(tutte)
                cand_R = [(j, rr, w) for j, rr, w in tutte if rr >= ri - 1]
                cand_P = [(j, rr, w) for j, rr, w in tutte if rr <= ri - 2]
                pi = (par.pi[gp] if var['pi_per_lingua'] else par.pi[0]).copy()
                ok = np.array([1.0, 1.0 if piS else 0.0, 1.0, 1.0 if cand_R else 0.0, 1.0 if cand_P else 0.0])
                pi = pi * ok
                if pi.sum() <= 0:
                    pi = np.array([1.0, 0, 0, 0, 0])
                w = None
                for _ in range(PROVE_MAX):
                    s = int(rng.choice(5, p=pi / pi.sum()))
                    if s <= 2:
                        w = self._parola_fresca(s, ctx, max(sg, 0), rng)
                    elif s == 3:
                        w = self._copia(cand_R, t, rigaini, ri, ctx, 0, rng)
                    else:
                        w = self._copia(cand_P, t, rigaini, ri, ctx, 1, rng)
                    if w is not None and self.valida(w):
                        break
                    w = None
                if w is None:
                    w = self._parola_fresca(0, ctx, max(sg, 0), rng) or ('?',)
                parole.append(w)
                tutte.append((t, ri, w))
                cum += len(w) + (1 if k else 0)
                h = self.rischio.rischio(r.banda, cum)
                if rng.random() < h or len(parole) >= PAROLE_RIGA_MAX or cum > self.rischio.hi[-1] * 1.25:
                    break
            righe_nuove.append(SD.Riga(r.ini, r.banda, SD.lunghezza_riga(parole), parole))
        return pagina.copia(righe_nuove)

    def scrivi(self, pagine, seme):
        rng = np.random.default_rng(seme)
        return [self.scrivi_pagina(p, rng) for p in pagine]
