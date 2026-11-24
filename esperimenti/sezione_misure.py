# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: le otto misure di struttura tenute fuori = le sei di IA34 (`piano_misure`, importate senza modificarle) + due NUOVE.

In parole semplici
- Le sei di IA34 (heaps, burst, riga_cv, sezione, lag23, ini_par) sono gia' state guardate sul Voynich in IA34: **nessun generatore le ha mai usate come obiettivo** (ne' IA34 ne' IA35), ma
  sono note. Le due nuove sono definite qui, **prima di ogni numero sul Voynich** (e non sono nel banco di IA26 ne' in nessun obiettivo di IA16-IA34):
    ttr_pagina   ricchezza di vocabolario di una pagina: media, sulle pagine, di (tipi di parola / parole) di ciascuna pagina
    hapax        la coda del vocabolario: quota dei tipi di parola che compaiono UNA sola volta in tutto il testo
- Per ogni mondo: valore sul testo vero e sigma vero-contro-vero (scala = sd della differenza fra le due meta' di `S_NM34` divisioni per fogli; sigma = scala / radice di 2), come in IA34.
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

NUOVE = ('ttr_pagina', 'hapax')
NOMI_NM8 = PMS.NOMI_NM + NUOVE


def _ttr_pagina(rows):
    v = []
    for rr in rows.values():
        ws = [w for _, p in rr for w in p]
        if len(ws) >= 20:
            v.append(len(set(ws)) / len(ws))
    return float(np.mean(v)) if len(v) >= 10 else None


def _hapax(rows):
    c = Counter(w for rr in rows.values() for _, ws in rr for w in ws)
    if len(c) < 200:
        return None
    return float(sum(1 for v in c.values() if v == 1) / len(c))


FUNZIONI8 = OrderedDict(list(PMS.FUNZIONI.items()) + [('ttr_pagina', _ttr_pagina), ('hapax', _hapax)])


def misure_testo(rows, pagine=None):
    if pagine is not None:
        rows = OrderedDict((p, rows[p]) for p in pagine if p in rows)
    return OrderedDict((n, f(rows)) for n, f in FUNZIONI8.items())


def riferimento_mondo(vere, dividi, divisioni=None):
    """Come `piano_misure.riferimento_mondo` con le otto misure."""
    divisioni = PMS.S_NM34 if divisioni is None else divisioni
    vero = misure_testo(vere)
    diffs = {n: [] for n in NOMI_NM8}
    for s in range(1, divisioni + 1):
        h1, h2 = dividi(s)
        a, b = misure_testo(vere, h1), misure_testo(vere, h2)
        for n in NOMI_NM8:
            if a[n] is not None and b[n] is not None:
                diffs[n].append(a[n] - b[n])
    scala = OrderedDict((n, float(np.std(d, ddof=1)) if len(d) > 2 else None) for n, d in diffs.items())
    return OrderedDict([('vero', vero), ('scala', scala), ('sigma', OrderedDict((n, (v / math.sqrt(2.0) if v else None)) for n, v in scala.items())), ('divisioni', divisioni)])


if __name__ == '__main__':
    pass
