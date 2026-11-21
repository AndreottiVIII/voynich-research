# -*- coding: utf-8 -*-
"""Supporto di ia17 (modulo, non e' un esperimento): scrivere libri con l'imitatore di ia16 a memoria ridotta.

Che cosa c'e' qui, in parole semplici
- `passo17`: come `Imitatore.passo` di ia16 (un segno alla volta, con la memoria delle chiavi e dei valori) ma con una regola su che cosa
  si puo' guardare: `None` = tutto (come ia16: la pagina in corso e, per P2, la coda della pagina precedente: riscrive i libri di ia16 segno
  per segno); `'SP'` = senza la pagina precedente; un intero k = solo la riga corrente e le k righe sopra (k = 0: solo la riga). La testa di
  pagina si vede solo se la finestra arriva alla testa (cioe' quando ci sono meno di k righe sopra).
  Il file di ia16 non e' modificato: la logica e' copiata da `passo` di `imitatore_modelli.py` (dichiarato).
- `Penna17`: la penna di ia16 (`Penna16`) con questo passo. `scrivi_libro17`: come `scrivi_libro` di ia16 con la regola, i semi e l'ordine
  delle pagine identici (con `None` il libro e' lo stesso di ia16, parola per parola).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import math

import numpy as np
import torch
import torch.nn.functional as F

import ia07_voynich_neurale as I7
import ia16_imitatore as I16


def passo17(m, tok, cond_vec, c, regola, inizio_riga=False):
    """Un segno in ingresso, restituisce i logit del prossimo. `c`: la Cache della pagina, con l'elenco `c.t_righe` (posizione nella cache del
    primo segno della testa di ogni riga). Vedi la descrizione del modulo per `regola`."""
    H, dh, d = m.H, m.dh, m.d
    t = c.n
    if inizio_riga:
        c.inizio_riga = t
        c.t_righe.append(t)
    cur = len(c.t_righe) - 1
    if regola is None:
        base = 0 if m.variante == 'P2' else c.inizio_pag
    elif regola == 'SP':
        base = c.inizio_pag
    else:
        k = int(regola)
        base = c.t_righe[cur - k] if cur - k >= 0 else c.inizio_pag
    lo_g = max(base, t + 1 - m.W_glob)
    lo_l = max(base, c.inizio_pag, t + 1 - m.W_loc)
    bias = {}
    for tp, lo in (('G', lo_g), ('L', lo_l)):
        if tp in m.tipi:
            bias[tp] = (lo, -m.pendenze[:, None] * (t - c.indici[lo:t + 1]).to(torch.float32)[None, :])
    x = m.emb(torch.tensor(tok)) + cond_vec
    scala = 1.0 / math.sqrt(dh)
    for l, b in enumerate(m.blocchi):
        h = b.ln1(x)
        qkv = b.qkv(h).view(3, H, dh)
        c.K[l][:, t] = qkv[1]
        c.V[l][:, t] = qkv[2]
        lo, bs = bias[m.tipi[l]]
        Ks, Vs = c.K[l][:, lo:t + 1], c.V[l][:, lo:t + 1]
        p = torch.softmax(torch.matmul(Ks, qkv[0].unsqueeze(-1)).squeeze(-1) * scala + bs, -1)
        o = torch.matmul(p.unsqueeze(1), Vs).reshape(d)
        x = x + b.proj(o)
        x = x + b.fc2(F.gelu(b.fc1(b.ln2(x))))
    c.n = t + 1
    return m.out(m.lnf(x))


class Penna17(I16.Penna16):
    def __init__(self, m, voc, cache, regola):
        super().__init__(m, voc, cache)
        self.regola = regola

    def apri(self, cond, mem):
        super().apri(cond, mem)
        self.cache.t_righe = []

    def dai(self, tok):
        with torch.inference_mode():
            lg = passo17(self.m, int(tok), self.cv, self.cache, self.regola, tok in self.T)
        self.ultimo = lg.tolist()
        self.storia.append(int(tok))


def scrivi_libro17(regola, modello_di, seme, pagine=None):
    """Come `ia16.scrivi_libro` con la regola di memoria. `pagine`: solo queste pagine (insieme di nomi; per i controlli); la coda della pagina
    precedente (solo per `regola` None e modelli P2) c'e' soltanto se la pagina precedente e' stata scritta subito prima."""
    righe, voc = I7.libro_vero(), I7.vocabolario()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    cap_pagina = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())
    cache, prev, out = None, None, []
    for pag, rp in pp.items():
        if pagine is not None and pag not in pagine:
            prev = None
            continue
        m = modello_di(pag)
        if cache is None:
            cache = m.nuova_cache(cap_pagina + m.cfg['prec'] + 8)
        penna = Penna17(m, voc, cache, regola)
        cond = I7.testa_pagina(rp, voc)[1:4]
        mem = m.memoria(prev[0], prev[1]) if (regola is None and m.variante == 'P2' and prev is not None) else None
        penna.apri(cond, mem)
        out += I7.percorri_pagina(penna, rp, lambda j, amm, pr: amm[I16.campiona(pr, rng)])
        prev = (np.array(penna.storia, dtype=np.int64)[-m.cfg['prec']:], np.array(cond, dtype=np.int64))
    return out


def nll_a_passi(m, p, regola):
    """Bit di ogni segno da indovinare di una pagina calcolati segno per segno con `passo17` (a parole note), senza coda della pagina
    precedente. Serve a controllare che la scrittura con la regola coincida con il calcolo a pagina intera con la maschera."""
    voc = I7.vocabolario()
    T = {voc['idx']['T:' + t] for t in 'PMUS'}
    tok = [int(x) for x in p['tok']]
    c = m.nuova_cache(len(tok) + 8)
    c.riparti(None)
    c.t_righe = []
    cv = m.vettore_cond(p['cond'])
    out = np.full(len(tok) - 1, np.nan)
    with torch.inference_mode():
        for t in range(len(tok) - 1):
            lg = passo17(m, tok[t], cv, c, regola, tok[t] in T)
            if tok[t + 1] >= voc['primo_contenuto']:
                out[t] = float(-torch.log_softmax(lg.float(), -1)[tok[t + 1]] / math.log(2.0))
    return out
