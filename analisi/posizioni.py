# -*- coding: utf-8 -*-
"""In quale posizione della parola sta l'informazione sul gruppo (pagina, sezione, categoria).

Misura di DECISIONI.md, D-006, usata dagli esperimenti 36, 37 e 38.

Si parte da "blocchi": un blocco e' un'unita' che si sposta intera nel rimescolamento
(una parola, se si rimescolano le parole fra le pagine; una pagina, se si rimescolano le
pagine fra le sezioni). Ogni blocco ha un gruppo, uno strato e un grappolo (per la
stabilita'), e contiene delle parole gia' tagliate in segni.

Per ogni posizione p:
    I_p     informazione mutua gruppo / segno in p (stima diretta, bit)
    N_p     media di I_p su n rimescolamenti dei gruppi fra i blocchi dello stesso strato
    quota_p = (I_p - N_p) / H(segno in p)
    z_p     = (I_p - N_p) / deviazione standard dei rimescolamenti
R = quota_primo / media(quota_penultimo, quota_ultimo).
"""
import math
from collections import namedtuple

import numpy as np

POSIZIONI = {'primo': 0, 'secondo': 1, 'penultimo': -2, 'ultimo': -1}

Blocco = namedtuple('Blocco', ['gruppo', 'strato', 'grappolo', 'parole'])


def _mi(etichette, segni, n_etichette, n_segni):
    congiunta = np.bincount(etichette * n_segni + segni, minlength=n_etichette * n_segni)
    congiunta = congiunta.reshape(n_etichette, n_segni).astype(float)
    n = congiunta.sum()
    pg = congiunta.sum(1) / n
    ps = congiunta.sum(0) / n
    pj = congiunta / n
    nz = pj > 0
    return float((pj[nz] * np.log2(pj[nz] / np.outer(pg, ps)[nz])).sum())


def _entropia(segni):
    c = np.bincount(segni).astype(float)
    c = c[c > 0] / c.sum()
    return float(-(c * np.log2(c)).sum())


def profilo(blocchi, posizioni=POSIZIONI, lung_min=4, rimescolamenti=200, seme=0):
    """Profilo di informazione per posizione. Le parole piu' corte di lung_min si scartano."""
    blocchi = [Blocco(b.gruppo, b.strato, b.grappolo,
                      [p for p in b.parole if len(p) >= lung_min]) for b in blocchi]
    blocchi = [b for b in blocchi if b.parole]
    gruppi = {g: i for i, g in enumerate(sorted({b.gruppo for b in blocchi}, key=str))}
    lung = np.array([len(b.parole) for b in blocchi])
    etichette_blocchi = np.array([gruppi[b.gruppo] for b in blocchi])
    # blocchi dello stesso strato: i gruppi si rimescolano solo fra loro
    strati = {}
    for i, b in enumerate(blocchi):
        strati.setdefault(b.strato, []).append(i)
    strati = [np.array(v) for _, v in sorted(strati.items(), key=lambda kv: str(kv[0]))]
    rnd = np.random.default_rng(seme)
    permutazioni = []
    for _ in range(rimescolamenti):
        perm = etichette_blocchi.copy()
        for idx in strati:
            perm[idx] = etichette_blocchi[idx][rnd.permutation(len(idx))]
        permutazioni.append(np.repeat(perm, lung))
    osservate = np.repeat(etichette_blocchi, lung)
    out = {'parole': int(lung.sum()), 'blocchi': len(blocchi), 'gruppi': len(gruppi),
           'strati': len(strati), 'posizioni': {}}
    for nome, pos in posizioni.items():
        simboli = [p[pos] for b in blocchi for p in b.parole]
        inventario = {s: i for i, s in enumerate(sorted(set(simboli)))}
        segni = np.array([inventario[s] for s in simboli])
        ng, ns = len(gruppi), len(inventario)
        i_oss = _mi(osservate, segni, ng, ns)
        nulle = np.array([_mi(p, segni, ng, ns) for p in permutazioni])
        h = _entropia(segni)
        dev = float(nulle.std(ddof=1))
        out['posizioni'][nome] = {
            'I': i_oss, 'nulla': float(nulle.mean()), 'nulla_dev': dev, 'H': h,
            'eccesso': i_oss - float(nulle.mean()),
            'quota': (i_oss - float(nulle.mean())) / h if h else 0.0,
            'z': (i_oss - float(nulle.mean())) / dev if dev else 0.0,
            'p': float((1 + (nulle >= i_oss).sum()) / (1 + len(nulle)))}
    out['R'] = rapporto(out['posizioni'])
    return out


def rapporto(pos):
    """quota al primo segno / media delle quote al penultimo e all'ultimo."""
    tardi = [pos[k]['quota'] for k in ('penultimo', 'ultimo') if k in pos]
    if 'primo' not in pos or not tardi:
        return None
    den = sum(tardi) / len(tardi)
    if den <= 0:
        return math.inf if pos['primo']['quota'] > 0 else None
    return pos['primo']['quota'] / den


def stabilita(blocchi, rimescolamenti=100, **kw):
    """R togliendo un grappolo per volta: (minimo, massimo, valori per grappolo)."""
    valori = {}
    for g in sorted({b.grappolo for b in blocchi}, key=str):
        resto = [b for b in blocchi if b.grappolo != g]
        valori[str(g)] = profilo(resto, rimescolamenti=rimescolamenti, **kw)['R']
    finiti = [v for v in valori.values() if v is not None]
    return {'min': min(finiti) if finiti else None, 'max': max(finiti) if finiti else None,
            'valori': valori}


def righe_utili(righe_di_parole, prima_ultima=True):
    """Toglie la prima e l'ultima parola di ogni riga (D-006)."""
    if not prima_ultima:
        return [p for r in righe_di_parole for p in r]
    return [p for r in righe_di_parole for p in r[1:-1]]
