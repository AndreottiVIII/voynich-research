# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: il giudice b di IA32 (`rifare_giudice`, via `oracolo_giudice`) con il rumore ridotto.

In parole semplici
- In IA34 lo stesso punto di manopole dava b 0,572 e 0,722 in due insiemi di libri: il giudice b ha un rumore di circa 0,15 (poche pagine vere, gruppi di fogli, libri che
  addestrano o provano). Qui l'AUC di un insieme di libri e' la **media di `RIP_B35` ripetizioni** (8) di `oracolo_giudice.auc_b_libri`, ognuna con una divisione diversa dei fogli in
  gruppi E una divisione diversa dei libri in addestramento e prova (meta' e meta', a caso con seme fisso); l'AUC di ogni libro e' la media sulle ripetizioni in cui era libro di prova.
- Errore onesto: il **nullo** e' la stessa procedura intera (le stesse `RIP_B35` ripetizioni, con le etichette vero/gemella scambiate a caso per pagina) ripetuta `PERM_B35` (8) volte; la sua
  deviazione standard e' il rumore che resta dopo la media. L'errore dell'insieme (come in IA33) e' la radice di (sd fra libri² / numero di libri + sd del nullo²).
Nessun risultato e' scritto qui.
"""
import os
import random
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import oracolo_giudice as OG  # noqa: E402

RIP_B = int(os.environ.get('RIP_B35', 8))
PERM_B = int(os.environ.get('PERM_B35', 8))


def _ripetizioni(vere, libri, pagine, foglio_di, voc, seme, permuta, rip):
    n = len(libri)
    somma, cont, medie = np.zeros(n), np.zeros(n), []
    for r in range(rip):
        rnd = random.Random(910000 + 1000 * seme + 17 * r + (500 if permuta else 0))
        idx = list(range(n))
        rnd.shuffle(idx)
        tr, te = idx[:n // 2], idx[n // 2:]
        lst = OG.auc_b_libri(vere, [libri[i] for i in tr], [libri[i] for i in te], pagine, foglio_di, voc, seme=100 * seme + r + (50 if permuta else 0), permuta=permuta)
        if lst is None:
            continue
        for i, a in zip(te, lst):
            somma[i] += a
            cont[i] += 1
        medie.append(float(np.mean(lst)))
    return somma, cont, medie


def esame_b_medio(vere, libri, pagine, foglio_di, voc, ripetizioni=None, permutazioni=None, seme=0):
    """AUC del giudice b su un insieme di libri (lista di pagine -> righe), mediata su piu' divisioni, con nullo. -> dict (`auc`, `per_libro`, `sd_libri`, `nullo_media`, `nullo_sd`, ...)."""
    rip = RIP_B if ripetizioni is None else ripetizioni
    per = PERM_B if permutazioni is None else permutazioni
    somma, cont, medie = _ripetizioni(vere, libri, pagine, foglio_di, voc, seme, False, rip)
    per_libro = [float(s / c) for s, c in zip(somma, cont) if c > 0]
    nul = []
    for k in range(per):
        _, _, m = _ripetizioni(vere, libri, pagine, foglio_di, voc, seme + 1 + k, True, rip)
        if m:
            nul.append(float(np.mean(m)))
    return OrderedDict([('auc', float(np.mean(medie)) if medie else None), ('per_libro', per_libro), ('sd_ripetizioni', float(np.std(medie, ddof=1)) if len(medie) > 1 else None),
                        ('sd_libri', float(np.std(per_libro, ddof=1)) if len(per_libro) > 1 else None), ('nullo_media', float(np.mean(nul)) if nul else None),
                        ('nullo_sd', float(np.std(nul, ddof=1)) if len(nul) > 1 else None), ('n_nullo', len(nul)), ('ripetizioni', rip), ('libri', len(libri)),
                        ('pagine', len([p for p in pagine if p in vere]))])


if __name__ == '__main__':
    pass
