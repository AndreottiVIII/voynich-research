# -*- coding: utf-8 -*-
"""Statistica per ia12 (modulo di supporto, non e' un esperimento): misure per gruppo di pagine, nulli per permutazione delle
etichette di mano, letture.

Che cosa c'e', in parole semplici:
- `Tab`: la tabella "per pagina" di un sotto-testo (numeratori e denominatori dei guadagni di ia09 e ia10 per ogni pagina).
  Ogni misura di un gruppo di pagine e' un rapporto di somme: si calcola in blocco per tanti gruppi insieme (una riga per gruppo).
- `delta_sel`: la differenza fra due mani su un sotto-testo (pagine scelte a parita' di parole per le due mani).
- `nullo_sel`: la stessa differenza quando le etichette di mano si permutano fra le pagine del sotto-testo (tutte insieme, oppure
  dentro la stessa sezione), R volte in blocco.
- `aggrega`: media sui sotto-testi (le diverse scelte di pagine) di una differenza o di un nullo.
- `lettura`: l'esito preregistrato per una misura.
Nessun file e nessuna parola del testo: solo numeri.
"""
import math
from collections import OrderedDict

import numpy as np

SOGLIA_W = 0.03             # bit per parola: guadagno piu' piccolo che si legge (come ia09)
# colonne della tabella: nome -> indice del denominatore. 0 = parole dopo le prime due della riga (ia09); 1 = quelle senza parola simile
# vicina (ia09); 2 = coppie di parole vicine (ia10)
COLONNE = OrderedDict([('gram', 0), ('g', 0), ('n', 0), ('tutto', 0), ('gram_n', 0), ('gp', 0), ('np', 0),
                       ('b', 0), ('c', 0), ('d', 0), ('e', 0), ('i1', 0), ('cd', 0), ('G0', 1), ('G10', 2), ('g10', 2), ('D10', 2)])
IX = {c: i for i, c in enumerate(COLONNE)}
DEN = [d for d in COLONNE.values()]
# misure primarie dei conti (le altre due della domanda, k90 e GR, vengono dalla rete) e descrittive
PRIMARIE = ['netto', 'rho', 'lambda', 'g10', 'D10']
DESCRITTIVE = ['A_gram', 'A_cn', 'G0', 'G10', 'gram', 'g', 'b', 'e', 'i1', 'cd']
TUTTE = PRIMARIE + DESCRITTIVE
# differenza minima che conta (stessa unita' della misura); fissata nella preregistrazione
SOGLIE_MINIME = OrderedDict([('netto', 0.02), ('rho', 0.20), ('lambda', 0.20), ('g10', 0.02), ('D10', 0.05),
                             ('A_gram', 0.02), ('A_cn', 0.02), ('G0', 0.02)])
ALFA_FAM = 0.05 / 7         # sette misure primarie (cinque dei conti e due della rete) con correzione di Bonferroni
MIN_DEFINITI = 0.5          # frazione minima di sotto-testi in cui rho e Lambda devono essere definite


class Tab:
    """Numeratori (bit risparmiati rispetto al modello senza contesto, per pagina) e denominatori di un sotto-testo."""

    def __init__(self, nomi, num, den, parole):
        self.nomi = list(nomi)
        self.P = len(nomi)
        self.N = np.asarray(num, dtype=float)              # (P, K)
        self.D = np.asarray(den, dtype=float)              # (P, 3)
        self.words = np.asarray(parole, dtype=float)       # (P,) parole totali della pagina
        self.ix = {p: i for i, p in enumerate(self.nomi)}

    def misure(self, Mind):
        """Misure di ogni gruppo (righe di Mind, 0/1 sulle pagine): dizionario nome -> array (righe,)."""
        Ns, Ds = Mind @ self.N, Mind @ self.D
        with np.errstate(divide='ignore', invalid='ignore'):
            def G_(c):
                d = Ds[:, DEN[IX[c]]]
                return np.where(d > 0, Ns[:, IX[c]] / np.where(d > 0, d, 1.0), np.nan)
            out = OrderedDict()
            netto = G_('g') - G_('n')
            a_gram = G_('tutto') - G_('g')
            a_cn = G_('tutto') - G_('gram_n')
            pa, pc = np.maximum(a_gram, 0.0), np.maximum(a_cn, 0.0)
            ok = np.maximum(a_gram, a_cn) >= SOGLIA_W
            out['netto'] = netto
            out['rho'] = np.where(ok, pc / np.where(pa + pc > 0, pa + pc, 1.0), np.nan)
            nettop = G_('gp') - G_('np')
            out['lambda'] = np.where(netto >= SOGLIA_W, 1.0 - nettop / np.where(netto != 0, netto, 1.0), np.nan)
            out['g10'] = G_('g10')
            out['D10'] = G_('D10')
            out['A_gram'], out['A_cn'] = a_gram, a_cn
            out['G0'] = G_('G0')
            out['G10'] = G_('G10')
            for c in ('gram', 'g', 'b', 'e', 'i1', 'cd'):
                out[c] = G_(c)
        return out


def valori_gruppi(tab, lab, etichette):
    """Misure di ogni etichetta (gruppo) di un sotto-testo: dict etichetta -> dict misura -> numero."""
    lab = np.asarray(lab)
    M = np.stack([(lab == e).astype(float) for e in etichette])
    m = tab.misure(M)
    return {e: {k: float(v[i]) for k, v in m.items()} for i, e in enumerate(etichette)}


def delta_sel(tab, lab, hA, hB, misure=TUTTE):
    """Differenza (A meno B) di ogni misura su un sotto-testo."""
    v = valori_gruppi(tab, lab, [hA, hB])
    return {k: v[hA][k] - v[hB][k] for k in misure}


def nullo_sel(tab, lab, strati, hA, hB, R, rng, misure=PRIMARIE):
    """R differenze (A meno B) con le etichette permutate dentro gli strati (liste di posizioni); un array (R,) per misura."""
    lab = np.asarray(lab)
    labs = np.tile(lab, (R, 1))
    for ids in strati:
        ids = np.asarray(ids, dtype=np.int64)
        if len(ids) > 1:
            perm = np.argsort(rng.random((R, len(ids))), axis=1)
            labs[:, ids] = lab[ids][perm]
    mA = tab.misure((labs == hA).astype(float))
    mB = tab.misure((labs == hB).astype(float))
    return {k: mA[k] - mB[k] for k in misure}


def aggrega(lista, minfrac=MIN_DEFINITI):
    """Media sui sotto-testi (un numero o un array (R,) ciascuno) dove la misura e' definita; NaN se i definiti sono meno della meta'."""
    x = np.array(lista, dtype=float)
    ok = ~np.isnan(x)
    n = ok.sum(0)
    with np.errstate(invalid='ignore', divide='ignore'):
        m = np.where(n >= max(1, minfrac * len(lista)), np.where(ok, x, 0.0).sum(0) / np.maximum(n, 1), np.nan)
    return m


def p_valore(obs, nulli):
    """p bilaterale per permutazione: (1 + #{|nullo| >= |obs|}) / (1 + R definiti)."""
    if nulli is None or obs is None or (isinstance(obs, float) and math.isnan(obs)):
        return None
    x = np.asarray(nulli, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 20:
        return None
    return float((1 + (np.abs(x) >= abs(obs) - 1e-12).sum()) / (1 + len(x)))


def lettura(obs, p1, p2, minimo):
    """Esito per una misura dei conti. obs = differenza osservata; p1 = p con etichette permutate dentro la lingua; p2 = p con
    etichette permutate dentro lingua e sezione (None se la sezione non si puo' pareggiare); minimo = differenza minima che conta."""
    if obs is None or (isinstance(obs, float) and math.isnan(obs)):
        return 'non definita'
    if abs(obs) < minimo:
        return 'nessuna differenza misurabile'
    if p2 is not None and p2 <= ALFA_FAM:
        return 'differiscono, anche a parita di sezione'
    if p1 is not None and p1 <= ALFA_FAM:
        return 'differiscono oltre la lingua, ma la sezione non si separa'
    return 'zona grigia'
