# -*- coding: utf-8 -*-
"""IA41, modulo di supporto: i tre giudici NUOVI dell'esame sigillato (sorpresa in avanti, sorpresa al contrario, indovina-sezione), tutti con "vero" = solo pagine TENUTE FUORI della divisione.

In parole semplici
- **Sorpresa in avanti:** modello a n-grammi (`righello_giudici.KneserNey`, ordine scelto fra 3-6 sulle pagine di VALIDAZIONE vere) addestrato sulle pagine vere STUDIATE (fogli d'addestramento); bit per
  segno di ogni pagina tenuta fuori; per ogni libro finto, frazione di pagine tenute fuori in cui la gemella finta ha sorpresa piu' alta della vera (0,5 = non si distinguono; sotto 0,5: il finto e' piu'
  prevedibile del vero: il sospetto dietro N a 0,35).
- **Sorpresa al contrario:** lo stesso modello (stesso ordine) addestrato sul PRIMO libro finto dell'insieme (tutte le sue pagine); frazione di pagine tenute fuori in cui la pagina VERA ha sorpresa piu' alta
  della gemella finta di ognuno degli altri libri (0,5 = non si distinguono; sopra 0,5: il vero ha cose che il finto non scrive).
- **Indovina-sezione:** classificatore (naive Bayes multinomiale sulle 600 parole piu' frequenti delle pagine studiate, lisciatura 0,5) addestrato sulle pagine vere studiate a dire la sezione; quota di
  pagine tenute fuori (di sezioni che il classificatore conosce) indovinate, per il vero e per ogni libro finto. Il finto troppo facile da attribuire = profilo di sezione copiato; troppo difficile = sezioni deboli.
Nessun risultato e' scritto qui.
"""
import math
import os
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import piano_misure as PMS  # noqa: E402
import righello_giudici as RG  # noqa: E402

N_PAROLE_IND = 600


def _auc_appaiata(a, b):
    """Frazione di pagine in cui `a` > `b` (parita' = 1/2)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.mean((a > b) + 0.5 * (a == b))) if len(a) else None


class Giudici:
    """I tre giudici di una divisione. `c` = `ia07.contesto_A()`, `f_add`, `f_val`, `f_fuori` = i fogli della divisione."""

    def __init__(self, c, f_add, f_val, f_fuori):
        self.c = c
        ins_a, ins_v, ins_f = set(f_add), set(f_val), set(f_fuori)
        fog = I7.foglio_di
        self.pag_add = [p for p in c['ids'] if fog(p) in ins_a]
        self.pag_val = [p for p in c['ids'] if fog(p) in ins_v]
        self.pag_ho = [p for p in c['ids'] if fog(p) in ins_f]
        assert not (set(self.pag_add) & set(self.pag_ho)) and not (set(self.pag_val) & set(self.pag_ho)), 'le pagine tenute fuori non devono essere ne\' studiate ne\' di validazione'
        self.m_fwd, self.info = RG.scegli_kn([c['ids'][p] for p in self.pag_add], [c['ids'][p] for p in self.pag_val], c['V'])
        self.ordine = self.info['ordine']
        self.s_vero = {p: float(self.m_fwd.sorpresa(c['ids'][p]).mean()) for p in self.pag_ho}
        self.sez = {p: k[0] for p, k in PMS.chiavi_pagina().items()}
        self._addestra_indovina()

    # ---- indovina-sezione
    def _addestra_indovina(self):
        c = self.c
        cont = Counter(w for p in self.pag_add for _, ws in c['vere'][p] for w in ws)
        self.voc = [w for w, _ in cont.most_common(N_PAROLE_IND)]
        self.ix = {w: i for i, w in enumerate(self.voc)}
        per = {}
        for p in self.pag_add:
            s = self.sez.get(p)
            if s is None:
                continue
            v = per.setdefault(s, np.full(len(self.voc), 0.5))
            for _, ws in c['vere'][p]:
                for w in ws:
                    j = self.ix.get(w)
                    if j is not None:
                        v[j] += 1
        npag = Counter(self.sez[p] for p in self.pag_add if p in self.sez)
        self.classi = sorted(s for s in per if npag[s] >= 3)
        self.logp = {s: np.log(per[s] / per[s].sum()) for s in self.classi}
        tot = float(sum(npag[s] for s in self.classi))
        self.prior = {s: math.log(npag[s] / tot) for s in self.classi}

    def _classifica(self, rr):
        v = np.zeros(len(self.voc))
        for _, ws in rr:
            for w in ws:
                j = self.ix.get(w)
                if j is not None:
                    v[j] += 1
        return max(self.classi, key=lambda s: self.prior[s] + float(v @ self.logp[s]))

    def pagine_indovinabili(self):
        return [p for p in self.pag_ho if self.sez.get(p) in self.classi]

    def acc_indovina(self, rows):
        pg = [p for p in self.pagine_indovinabili() if p in rows]
        if not pg:
            return None
        return float(np.mean([self._classifica(rows[p]) == self.sez[p] for p in pg]))

    # ---- sorprese
    def _score(self, model, rows, pagine):
        out = {}
        for p in pagine:
            if p in rows:
                a = G.codifica(rows[p], self.c['idx'])
                if len(a) > 3:
                    out[p] = float(model.sorpresa(a).mean())
        return out

    def auc_avanti(self, rows):
        s = self._score(self.m_fwd, rows, self.pag_ho)
        pg = [p for p in self.pag_ho if p in s]
        return _auc_appaiata([s[p] for p in pg], [self.s_vero[p] for p in pg])

    def modello_finto(self, rows):
        """Il KneserNey addestrato su tutte le pagine di un libro finto (stesso ordine della sorpresa in avanti)."""
        ids = [G.codifica(rr, self.c['idx']) for rr in rows.values()]
        return RG.KneserNey(ids, self.ordine, self.c['V'])

    def auc_indietro(self, modello, rows_finti):
        """Per ogni libro finto in `rows_finti` (diverso da quello che ha addestrato il modello): frazione di pagine tenute fuori in cui la VERA ha sorpresa piu' alta della finta."""
        sv = self._score(modello, self.c['vere'], self.pag_ho)
        out = []
        for rows in rows_finti:
            sf = self._score(modello, rows, self.pag_ho)
            pg = [p for p in self.pag_ho if p in sv and p in sf]
            out.append(_auc_appaiata([sv[p] for p in pg], [sf[p] for p in pg]))
        return out


if __name__ == '__main__':
    pass
