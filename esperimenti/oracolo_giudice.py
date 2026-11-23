# -*- coding: utf-8 -*-
"""IA33, modulo di supporto: il giudice "b" di IA32 (`rifare_giudice`, importato senza modificarlo) con l'AUC di ogni libro di prova (serve all'errore).

In parole semplici
- E' lo stesso giudice di IA32 (stessa regressione logistica, stessi gruppi di fogli, stesso nullo con le etichette scambiate): `rifare_giudice.auc_b` restituisce solo la
  media sui libri di prova; qui si restituisce anche la lista, libro per libro, per dare un errore (deviazione standard fra libri / radice del numero di libri).
- Nessuna formula nuova: `auc_b_libri` e' `rifare_giudice.auc_b` con in uscita la lista invece della media.
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
import rifare_giudice as RGB  # noqa: E402

C_B = RGB.C_B
GRUPPI_B = RGB.GRUPPI_B


def auc_b_libri(vere, libri_train, libri_test, pagine, foglio_di, voc, seme=0, permuta=False):
    """Come `rifare_giudice.auc_b` ma -> lista delle AUC, una per libro di prova (None se non si puo' calcolare)."""
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
    sw = np.array([rnd.random() < 0.5 for _ in pagine]) if permuta else np.zeros(len(pagine), bool)
    Xv, pv = RGB._righe(vere, pagine, voc)
    Xl_tr = [RGB._righe(L, pagine, voc) for L in libri_train]
    Xl_te = [RGB._righe(L, pagine, voc) for L in libri_test]
    n = len(pagine)
    sv = np.zeros(n)
    sg = [np.zeros(n) for _ in libri_test]
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
        aucs.append(float(G.auc(np.array([0] * n + [1] * n), np.concatenate([neg, pos]))))
    return aucs


def esame_b_libri(vere, libri, pagine, foglio_di, voc, n_train, permutazioni=12, seme=0):
    """AUC del giudice b: i primi `n_train` libri addestrano, gli altri provano; nullo con `permutazioni` scambi di etichette. -> dict con `per_libro` (lista), `auc` (media),
    `sd_libri`, `nullo_media`, `nullo_sd` (deviazione standard della media sui libri di prova sotto il nullo)."""
    tr, te = libri[:n_train], libri[n_train:]
    lst = auc_b_libri(vere, tr, te, pagine, foglio_di, voc, seme)
    nul = []
    for k in range(permutazioni):
        x = auc_b_libri(vere, tr, te, pagine, foglio_di, voc, seme + 1 + k, permuta=True)
        if x is not None:
            nul.append(float(np.mean(x)))
    return OrderedDict([('auc', float(np.mean(lst)) if lst else None), ('per_libro', lst), ('sd_libri', float(np.std(lst, ddof=1)) if lst and len(lst) > 1 else None),
                        ('nullo_media', float(np.mean(nul)) if nul else None), ('nullo_sd', float(np.std(nul, ddof=1)) if len(nul) > 1 else None),
                        ('n_nullo', len(nul)), ('libri_addestramento', len(tr)), ('libri_prova', len(te)), ('pagine', len([p for p in pagine if p in vere]))])
