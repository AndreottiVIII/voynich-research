# -*- coding: utf-8 -*-
"""IA36, modulo di supporto: le misure di GUARDIA della scelta prudente e la misura di riuso di sezione (obiettivo).

In parole semplici
- **Cinque misure di guardia**, nuove, pensate per accorgersi quando il ciclo "compra" obiettivo rovinando la struttura che non vede. NON sono sinonimi delle dieci misure d'esame
  (D, R_rel, heaps, burst, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax: quelle restano tenute fuori da obiettivo, scelta dei finalisti e taratura); non sono nel banco di IA26 e in
  nessun obiettivo di IA16-IA35. Si usano SOLO come guardia (mai nell'obiettivo): se una guardia esce dal permesso, il candidato paga una penalita'.
    g_rig_parole   forma di riga in PAROLE: coefficiente di variazione (deviazione standard / media) del numero di parole per riga (riga_cv dell'esame e' in glifi)
    g_lung_par     lunghezza media delle parole (in unita' di glifo), pesata sulle occorrenze
    g_nov_pagine   novita' rispetto alle pagine vicine: media, sulle pagine di almeno 20 parole, della quota di occorrenze il cui tipo non compare nelle 3 pagine precedenti (nell'ordine del testo)
    g_bigr_rip     ripetizione di coppie di parole: quota delle coppie di parole adiacenti (nella stessa riga) il cui tipo di coppia compare almeno due volte nel testo
    g_zipf         pendenza della legge di Zipf: retta (log10 frequenza contro log10 rango) sui 200 tipi di parola piu' frequenti
- **Una misura nuova nell'OBIETTIVO del ciclo (non e' una guardia, non e' una delle dieci):** `riuso_sez`, il bersaglio proprio della memoria di sezione: quota delle occorrenze di parola
  (pagine di almeno 20 parole) il cui tipo compare gia' in una pagina precedente della STESSA sezione e lingua (nell'ordine del testo; sezione e lingua come in `piano_misure`). Senza un
  termine come questo la manopola `w_sez` sarebbe cieca per il ciclo (l'obiettivo di IA35 non contiene niente che la memoria di sezione sposti). `sezione` dell'esame (coseno medio fra pagine
  della stessa sezione meno fra sezioni diverse, su 400 parole) resta TENUTA FUORI: dice se un riuso della giusta quantita' dia anche la giusta somiglianza fra pagine.
- Come per le misure di IA34/IA35: valore sul testo vero e scala (deviazione standard della differenza fra le due meta' di `S_NM34` divisioni per fogli); z di un mezzo libro = (valore - vero degli
  stessi fogli) / scala.
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
import piano_misure as PMS  # noqa: E402

GUARDIE36 = ('g_rig_parole', 'g_lung_par', 'g_nov_pagine', 'g_bigr_rip', 'g_zipf')
EXTRA_OBIETTIVO36 = ('riuso_sez',)
NOMI36 = GUARDIE36 + EXTRA_OBIETTIVO36
MIN_PAROLE_PAG = 20
FINESTRA_NOV = 3
TOP_ZIPF = 200


def _parole_di(rr):
    return [w for _, ps in rr for w in ps]


def _g_rig_parole(rows):
    n = [len(ws) for rr in rows.values() for _, ws in rr if ws]
    if len(n) < 30:
        return None
    return float(np.std(n) / np.mean(n))


def _g_lung_par(rows):
    L = [len(w) for rr in rows.values() for _, ws in rr for w in ws]
    if len(L) < 800:
        return None
    return float(np.mean(L))


def _g_nov_pagine(rows):
    tipi = [set(_parole_di(rr)) for rr in rows.values()]
    ws = [_parole_di(rr) for rr in rows.values()]
    v = []
    for i in range(FINESTRA_NOV, len(ws)):
        if len(ws[i]) < MIN_PAROLE_PAG:
            continue
        prima = set().union(*tipi[i - FINESTRA_NOV:i])
        v.append(sum(1 for w in ws[i] if w not in prima) / len(ws[i]))
    return float(np.mean(v)) if len(v) >= 10 else None


def _g_bigr_rip(rows):
    c = Counter()
    for rr in rows.values():
        for _, ws in rr:
            for a, b in zip(ws[:-1], ws[1:]):
                c[(a, b)] += 1
    n = sum(c.values())
    if n < 800:
        return None
    return float(sum(v for v in c.values() if v >= 2) / n)


def _g_zipf(rows):
    c = Counter(w for rr in rows.values() for _, ws in rr for w in ws)
    if len(c) < TOP_ZIPF:
        return None
    f = np.array([v for _, v in c.most_common(TOP_ZIPF)], float)
    a, _ = np.polyfit(np.log10(np.arange(1, TOP_ZIPF + 1)), np.log10(f), 1)
    return float(a)


def _riuso_sez(rows):
    ch = PMS.chiavi_pagina()
    visti, tot, riuso = {}, 0, 0
    for p, rr in rows.items():
        ws = _parole_di(rr)
        k = ch.get(p)
        if k is None:
            continue
        s = visti.get(k)
        if s is not None and len(ws) >= MIN_PAROLE_PAG:
            riuso += sum(1 for w in ws if w in s)
            tot += len(ws)
        visti.setdefault(k, set()).update(ws)
    return float(riuso / tot) if tot >= 500 else None


FUNZIONI36 = OrderedDict([('g_rig_parole', _g_rig_parole), ('g_lung_par', _g_lung_par), ('g_nov_pagine', _g_nov_pagine), ('g_bigr_rip', _g_bigr_rip), ('g_zipf', _g_zipf),
                          ('riuso_sez', _riuso_sez)])


def misure_testo(rows, pagine=None):
    """Le sei misure (cinque guardie e `riuso_sez`) su `rows` (pagina -> [(inizio, [parole])]), solo sulle pagine `pagine` (se date e presenti). -> OrderedDict nome -> valore (None se troppo corto)."""
    if pagine is not None:
        rows = OrderedDict((p, rows[p]) for p in pagine if p in rows)
    return OrderedDict((n, f(rows)) for n, f in FUNZIONI36.items())


def riferimento_mondo(vere, dividi, divisioni=None):
    """Valore sul testo vero e scala (sd della differenza fra le due meta' di `divisioni` divisioni per fogli), come `sezione_misure.riferimento_mondo`."""
    divisioni = PMS.S_NM34 if divisioni is None else divisioni
    vero = misure_testo(vere)
    diffs = {n: [] for n in NOMI36}
    for s in range(1, divisioni + 1):
        h1, h2 = dividi(s)
        a, b = misure_testo(vere, h1), misure_testo(vere, h2)
        for n in NOMI36:
            if a[n] is not None and b[n] is not None:
                diffs[n].append(a[n] - b[n])
    scala = OrderedDict((n, float(np.std(d, ddof=1)) if len(d) > 2 else None) for n, d in diffs.items())
    return OrderedDict([('vero', vero), ('scala', scala), ('sigma', OrderedDict((n, (v / math.sqrt(2.0) if v else None)) for n, v in scala.items())), ('divisioni', divisioni)])


def z_misure(v, vh, scala, nomi=NOMI36):
    """z (in scale) di un mezzo libro: (valore - vero degli stessi fogli) / scala, per le misure presenti e con scala."""
    out = OrderedDict()
    for n in nomi:
        if v.get(n) is not None and vh.get(n) is not None and scala.get(n):
            out[n] = (v[n] - vh[n]) / scala[n]
    return out


if __name__ == '__main__':
    pass
