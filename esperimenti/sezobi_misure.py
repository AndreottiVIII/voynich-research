# -*- coding: utf-8 -*-
"""IA38, modulo di supporto: la DIFFERENZA FRA SEZIONI come grandezza dell'obiettivo (due termini: `div_bigr` e `div_par`), con riferimento sui soli fogli d'addestramento.

In parole semplici
- Stessa idea della "divergenza fra sezioni" di IA37 (`freqsez_tabelle.divergenza_sezioni`): media, sulle coppie di sezioni, della divergenza di Jensen-Shannon (bit) fra le distribuzioni (a) dei bigrammi di
  unita' di glifo (con lo spazio fra le parole) e (b) delle 300 parole piu' frequenti. Qui pero' e' una grandezza dell'obiettivo del ciclo, quindi serve che un mezzo libro e il vero degli stessi fogli siano
  confrontabili: per questo (1) si contano **solo le pagine dei fogli d'addestramento** (mai validazione ne' tenuti fuori), sia nel mezzo libro sia nel vero; (2) le sezioni che entrano, il vocabolario dei bigrammi
  (piu' un cestino "altro") e le 300 parole sono quelli del VERO sulle stesse pagine (`Spec`): il candidato e il vero si confrontano sulle stesse coppie di sezioni e sugli stessi vettori, senza che una sezione
  entri o esca per un'occorrenza in piu' o in meno.
- Valore del vero e scala per z: z = (valore del mezzo libro - valore del vero sulle stesse pagine d'addestramento) / scala, con la scala = deviazione standard della differenza fra le due meta' del vero
  (`S_NM34` divisioni per fogli del banco, ognuna ristretta ai fogli d'addestramento), come per le altre misure del banco. Nell'obiettivo: min(|z|, 10), come le altre grandezze.
Nessun risultato e' scritto qui.
"""
import math
import os
import sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import piano_misure as PMS  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402

NOMI_OBI = ('div_bigr', 'div_par')
ALTRO = ('__altro__',)


def _conta(rows, pagine, sp):
    big, par, tot = defaultdict(Counter), defaultdict(Counter), Counter()
    for p in pagine:
        rr = rows.get(p)
        s = sp.get(p)
        if rr is None or s is None:
            continue
        for _, ws in rr:
            seq = []
            for w in ws:
                seq += list(w) + ['_']
                par[s][w] += 1
                tot[w] += 1
            for a, b in zip(seq[:-1], seq[1:]):
                big[s][(a, b)] += 1
    return big, par, tot


class Spec:
    """Le sezioni, il vocabolario dei bigrammi e le parole che definiscono i vettori; si costruisce dal VERO sulle pagine date."""

    def __init__(self, rows, pagine, sp):
        big, par, tot = _conta(rows, pagine, sp)
        self.sez_b = sorted(s for s in big if sum(big[s].values()) >= FT.MIN_SEGNI_DIV)
        self.voc_p = [w for w, _ in tot.most_common(FT.TOP_DIV)]
        ip = set(self.voc_p)
        self.sez_p = sorted(s for s in par if sum(c for w, c in par[s].items() if w in ip) >= FT.MIN_PAROLE_DIV)
        self.voc_b = sorted({k for s in self.sez_b for k in big[s]}, key=str)
        self.ib = {k: i for i, k in enumerate(self.voc_b)}
        self.ip = {k: i for i, k in enumerate(self.voc_p)}


def div_con(rows, pagine, spec, sp):
    """(bigr, parole) del testo `rows` sulle `pagine` con le sezioni e i vocabolari di `spec`. None se meno di due sezioni."""
    big, par, _ = _conta(rows, pagine, sp)
    nb, npv = len(spec.voc_b) + 1, len(spec.voc_p) + 1
    vb, vp = {}, {}
    for s in spec.sez_b:
        v = np.full(nb, 0.5)
        for k, c in big.get(s, {}).items():
            v[spec.ib.get(k, nb - 1)] += c
        vb[s] = v / v.sum()
    for s in spec.sez_p:
        v = np.full(npv, 0.5)
        for w, c in par.get(s, {}).items():
            v[spec.ip.get(w, npv - 1)] += c
        vp[s] = v / v.sum()

    def media(vs):
        ss = sorted(vs)
        d = [FT._js(vs[a], vs[b]) for i, a in enumerate(ss) for b in ss[i + 1:]]
        return float(np.mean(d)) if d else None
    return media(vb), media(vp)


def pagine_addestramento(rows_pagine, f_add):
    """Le pagine (nomi) fra `rows_pagine` che stanno in fogli d'addestramento."""
    import ia07_voynich_neurale as I7
    ins = set(f_add)
    return [p for p in rows_pagine if I7.foglio_di(p) in ins]


def riferimento(vere, ids, dividi, f_add, divisioni=None):
    """Valore del vero sulle pagine d'addestramento e scala (sd della differenza fra le due meta' del vero, ognuna ristretta ai fogli d'addestramento, su `divisioni` divisioni per fogli).
    -> dict(vero, scala, sigma, divisioni, pagine). `dividi(s)` -> (pagine della meta' 1, pagine della meta' 2)."""
    sp = {p: k[0] for p, k in PMS.chiavi_pagina().items()}
    divisioni = PMS.S_NM34 if divisioni is None else divisioni
    tutte = pagine_addestramento(ids, f_add)
    sv = Spec(vere, tutte, sp)
    b, p = div_con(vere, tutte, sv, sp)
    diffs = {'div_bigr': [], 'div_par': []}
    for s in range(1, divisioni + 1):
        h1, h2 = dividi(s)
        r = []
        for h in (h1, h2):
            pg = pagine_addestramento(h, f_add)
            sph = Spec(vere, pg, sp)
            r.append(div_con(vere, pg, sph, sp))
        for j, nome in enumerate(NOMI_OBI):
            if r[0][j] is not None and r[1][j] is not None:
                diffs[nome].append(r[0][j] - r[1][j])
    scala = OrderedDict((n, float(np.std(d, ddof=1)) if len(d) > 2 else None) for n, d in diffs.items())
    return OrderedDict([('vero', OrderedDict([('div_bigr', b), ('div_par', p)])), ('scala', scala), ('sigma', OrderedDict((n, (v / math.sqrt(2.0) if v else None)) for n, v in scala.items())),
                        ('divisioni', divisioni), ('pagine_addestramento', len(tutte)), ('sezioni_bigr', sv.sez_b), ('sezioni_parole', sv.sez_p)])


if __name__ == '__main__':
    pass
