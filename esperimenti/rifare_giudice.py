# -*- coding: utf-8 -*-
"""IA32, modulo di supporto: il giudice nuovo "b" dell'esame finale.

In parole semplici
- E' un classificatore fresco, addestrato DOPO il ciclo, a distinguere le righe VERE dei fogli tenuti fuori (che l'imitatore non ha mai visto) dalle righe gemelle
  scritte dall'imitatore con le manopole migliori. Le righe gemelle sono quelle dei libri scritti con la stessa disposizione (stesse pagine, stesse righe).
- Caratteristiche: conteggi dei n-grammi di glifi (1-3) dentro la riga, come il giudice N di IA26, con il vocabolario preso dalle pagine vere (solo conteggi, nessuna
  etichetta); NIENTE identita' delle parole (un classificatore con le parole potrebbe imparare "queste parole sono dei fogli d'addestramento" e
  sbagliare il segno dell'AUC). Regressione logistica L2 (C = `C_B32`, fissata prima, 0,05), pesi di classe bilanciati.
- Addestramento e prova sono separati due volte: i LIBRI dell'imitatore si dividono in libri d'addestramento e libri di prova (semi diversi), e le PAGINE
  vere in 5 gruppi di fogli (un gruppo di fogli tenuti fuori e' la prova, gli altri l'addestramento). Il punteggio di una pagina e' la media dei punteggi delle sue righe.
  AUC = pagine vere del gruppo contro le loro gemelle nei libri di prova, messe insieme nei 5 gruppi; si fa la media sui libri di prova.
- Il nullo: stesso procedimento con le etichette scambiate a caso (per ogni coppia pagina vera / gemella, con probabilita' 1/2) dentro i libri d'addestramento e di prova.
- Condizione di validita' (scritta prima): lo stesso giudice, applicato a un imitatore a manopole neutre (i libri a temperatura 1), deve dare almeno
  `AUC_NEUTRO_MIN32` (0,70); altrimenti e' troppo debole per questa prova e l'esame non si legge.
"""
import os
import random
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import righello_giudici as RG  # noqa: E402

C_B = float(os.environ.get('C_B32', 0.05))
GRUPPI_B = 5
AUC_NEUTRO_MIN = float(os.environ.get('AUC_NEUTRO_MIN32', 0.70))


def _righe(rows, pagine, voc):
    """Matrice delle righe e indice di pagina (nell'elenco `pagine`) di ogni riga."""
    return RG.matrice_righe_N(OrderedDict((p, rows[p]) for p in pagine), pagine, voc)


def auc_b(vere, libri_train, libri_test, pagine, foglio_di, voc, seme=0, permuta=False):
    """`vere`: pagina -> righe (pagine vere dei fogli tenuti fuori); `libri_*`: liste di dizionari pagina -> righe (stesse pagine). `pagine`: elenco delle pagine
    (le vere dei fogli tenuti fuori presenti in tutti i libri). `foglio_di`: pagina -> foglio. -> AUC media sui libri di prova (o None).
    Con `permuta` le etichette si scambiano per pagina (a caso, stessa scelta per tutti i libri): il nullo."""
    from sklearn.linear_model import LogisticRegression
    from scipy.sparse import vstack
    pagine = [p for p in pagine if p in vere and all(p in L for L in libri_train + libri_test)]
    if len(pagine) < 6 or not libri_train or not libri_test:
        return None
    rnd = random.Random(7000 + seme)
    fogli = sorted({foglio_di(p) for p in pagine})
    rnd.shuffle(fogli)
    gruppo = {f: i % GRUPPI_B for i, f in enumerate(fogli)}
    gp = np.array([gruppo[foglio_di(p)] for p in pagine])
    sw = np.array([rnd.random() < 0.5 for _ in pagine]) if permuta else np.zeros(len(pagine), bool)   # True: la pagina vera fa da "positiva"
    Xv, pv = _righe(vere, pagine, voc)
    Xl_tr = [_righe(L, pagine, voc) for L in libri_train]
    Xl_te = [_righe(L, pagine, voc) for L in libri_test]
    n = len(pagine)
    sv = np.zeros(n)                                       # punteggio medio di ogni pagina vera (dal modello del gruppo che non la ha vista)
    sg = [np.zeros(n) for _ in libri_test]                 # idem per le gemelle di ogni libro di prova
    for f in range(GRUPPI_B):
        tr_pag = gp != f
        te_pag = ~tr_pag
        if not te_pag.any() or not tr_pag.any():
            continue
        mv = tr_pag[pv]
        Xs, ys = [Xv[mv]], [sw[pv[mv]].astype(float)]
        for X, pg in Xl_tr:
            m = tr_pag[pg]
            Xs.append(X[m])
            ys.append((~sw[pg[m]]).astype(float))
        ytr = np.concatenate(ys)
        if ytr.min() == ytr.max():
            continue
        mod = LogisticRegression(C=C_B, max_iter=2000, class_weight='balanced').fit(vstack(Xs).tocsr(), ytr)
        mvv = te_pag[pv]
        sv += np.bincount(pv[mvv], weights=mod.decision_function(Xv[mvv]), minlength=n)
        for b, (X, pg) in enumerate(Xl_te):
            m = te_pag[pg]
            sg[b] += np.bincount(pg[m], weights=mod.decision_function(X[m]), minlength=n)
    nr_v = np.maximum(np.bincount(pv, minlength=n).astype(float), 1.0)
    aucs = []
    for b, (X, pg) in enumerate(Xl_te):
        nr_g = np.maximum(np.bincount(pg, minlength=n).astype(float), 1.0)
        a, c = sv / nr_v, sg[b] / nr_g
        pos, neg = np.where(sw, a, c), np.where(sw, c, a)
        aucs.append(G.auc(np.array([0] * n + [1] * n), np.concatenate([neg, pos])))
    return float(np.mean(aucs))


def esame_b(vere, libri, pagine, foglio_di, voc, n_train, permutazioni=20, seme=0):
    """AUC del giudice b con i primi `n_train` libri come addestramento e gli altri come prova, e il nullo (`permutazioni` scambi). -> dict."""
    tr, te = libri[:n_train], libri[n_train:]
    a = auc_b(vere, tr, te, pagine, foglio_di, voc, seme)
    nul = [auc_b(vere, tr, te, pagine, foglio_di, voc, seme + 1 + k, permuta=True) for k in range(permutazioni)]
    nul = [x for x in nul if x is not None]
    return OrderedDict([('auc', a), ('nullo_media', float(np.mean(nul)) if nul else None), ('nullo_sd', float(np.std(nul, ddof=1)) if len(nul) > 1 else None),
                        ('n_nullo', len(nul)), ('libri_addestramento', len(tr)), ('libri_prova', len(te)), ('pagine', len([p for p in pagine if p in vere]))])
