# -*- coding: utf-8 -*-
"""Moduli di supporto per ia15b (non e' un esperimento): aggiunte a `eco_modelli.py` (di ia15, non modificato).

Che cosa c'e' qui, in parole semplici:
- `vicini_per_tipo`: per ogni parola (tipo) del testo, le parole del testo a una modifica di distanza (serve al generatore "famiglie").
- `genera_argomento_famiglie`: un controllo nuovo, "solo argomento di famiglie di parole": ogni pagina ha un tema fatto di parole; quando
  una parola del tema esce, con probabilita' `phi` esce invece una parola a una modifica da lei (una "parente", presa dal lessico del
  testo). Nessuna copia di una parola scritta poco prima e nessun legame con la distanza: e' il modo in cui anche una lingua flessiva
  ripete parole simili (varianti) senza che nessuno le copi. Serve a sapere se la misura delle varianti si fa ingannare dal lessico.
- `conta_eco_rapida`, `eco_vicina_tutti`: la sola quantita' di eco (eco vicina, pesi comuni) per la taratura dei controlli, senza i
  paragrafi e senza i rimescolamenti dei confini.
Niente risultati scritti qui.
"""
import numpy as np

import eco_modelli as EM


def vicini_per_tipo(A):
    """Per ogni tipo, l'array dei tipi a una modifica (qualunque posto), dal grafo di `EM.grafo_vicini`."""
    S = (A['I'] + A['F'] + A['M']).tocsr()
    return [S.indices[S.indptr[t]:S.indptr[t + 1]] for t in range(S.shape[0])]


def genera_argomento_famiglie(C, A, seme, lam, phi=0.6, k_topic=30):
    """SOLO ARGOMENTO DI FAMIGLIE (nessuna copia di parole vicine, nessun legame con la distanza): ogni pagina ha un tema = k_topic parole
    (scelte con peso frequenza^0,5, ognuna con un peso a scala Zipf, come in `EM.genera_argomento`); ogni parola, con probabilita' `lam`,
    e' pescata dal tema e, con probabilita' `phi`, sostituita da una parola a una modifica da lei (scelta a caso fra quelle del testo; se
    non ne ha resta com'e'); altrimenti e' pescata dalla frequenza generale. Le pagine non si legano fra loro."""
    C.prepara()
    rnd = np.random.RandomState(seme % (2 ** 32 - 1))
    vic = vicini_per_tipo(A)
    cw = np.zeros(C.nt, dtype=np.int64)
    for P in C.pag.values():
        cw += np.bincount(P.tok, minlength=C.nt)
    ok = np.where(cw > 0)[0]
    glob = np.cumsum(cw[ok] / cw[ok].sum())
    sel = cw[ok].astype(float) ** 0.5
    sel_c = np.cumsum(sel / sel.sum())

    def pesca(cum, n=1):
        return np.minimum(np.searchsorted(cum, rnd.random_sample(n)), len(cum) - 1)

    def nuovo():
        idx = set()
        while len(idx) < min(k_topic, len(ok)):
            idx.add(int(pesca(sel_c)[0]))
        idx = np.array(sorted(idx))
        rk = rnd.permutation(len(idx))
        w = 1.0 / (rk + 1.0) ** 0.9
        return [ok[idx], np.cumsum(w / w.sum())]
    out = {}
    nomi = list(C.pag.keys())
    for p in nomi:
        P = C.pag[p]
        topic = nuovo()
        rows = []
        for l in range(len(P.lstart) - 1):
            n = int(P.lstart[l + 1] - P.lstart[l])
            ws = []
            for _ in range(n):
                if rnd.random_sample() < lam:
                    t = int(topic[0][int(pesca(topic[1])[0])])
                    if rnd.random_sample() < phi and len(vic[t]):
                        t = int(vic[t][int(rnd.randint(len(vic[t])))])
                else:
                    t = int(ok[int(pesca(glob)[0])])
                ws.append(C.parole_in_glifi(t))
            rows.append((bool(n and P.ini[P.lstart[l]]), ws))
        out[p] = rows
    from collections import OrderedDict
    return OrderedDict((p, out[p]) for p in nomi)


def conta_eco_rapida(C, A, P, rif_sez):
    """Per una pagina: (n, simile) per banda di distanza, sulle sole parole alla riga 4 o piu' (come il gruppo 'A4' di ia15), per la pagina
    vera e per il riferimento (media delle pagine di riferimento); arrotondati a tre decimali come `EM.stat_pagina`. Restituisce un array
    (2 [vero, riferimento], NB, 5) con colonna 0 = n e colonna 1 = parole simili (le altre a zero): il formato che `eco_comune` di ia15
    si aspetta."""
    pid, prima = EM.paragrafi(P)
    Lq = P.L
    pr = (Lq >= 4).astype(float)
    out = np.zeros((2, EM.NB, 5))
    Mreal = EM.matrici_fonte(A, P, P)
    refs = [EM.matrici_fonte(A, P, R) for R in rif_sez]
    for k, lista in ((0, [Mreal]), (1, refs)):
        acc = np.zeros((EM.NB, 2))
        for M in lista:
            band = EM.bande(Lq, M['n'].shape[1], pid, prima, False)
            s = EM.somme_bande({'n': M['n'], 'h': EM.simile(M)}, band, pr)
            acc[:, 0] += s['n'][:EM.NB] + s['n'][EM.NB:]
            acc[:, 1] += s['h'][:EM.NB] + s['h'][EM.NB:]
        out[k, :, 0:2] = np.round(acc / len(lista), 3)
    return out
