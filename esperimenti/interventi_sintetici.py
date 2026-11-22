# -*- coding: utf-8 -*-
"""Supporto di ia30 (modulo, non e' un esperimento): il testo sintetico "a regole note" dei controlli positivi, e la sua taratura.

Che cosa c'e' qui, in parole semplici
- `sintetico_regole`: una copia del libro (stesse righe e stesse lunghezze, parole pescate dalla frequenza del libro) con regole piantate, ognuna con
  UNA sola fonte d'informazione nota:
    CONTATTO  una parola fresca dopo un'altra comincia con il glifo "preferito" dall'ULTIMO glifo della parola prima (solo da questo);
    ECO       con una certa probabilita' la parola e' una parola della riga SOPRA presa a caso, con un ritocco (un glifo cambiato, aggiunto o tolto);
    BORDI     la prima (e l'ultima) parola della riga viene da un elenco di 6 parole fisse;
    ORDINE    ogni parola ha una famiglia (a caso, fissa); con una certa probabilita' la famiglia della parola dopo e' quella successiva (in giro) a
              quella della parola prima: dipende dalla parola prima INTERA (non dalle sue ultime lettere).
- `calibra_contatto`, `calibra_eco`, `calibra_bordi`: la forza di ogni regola si sceglie in modo che la misura sul testo piantato dia il valore VERO
  del manoscritto (contatto 0,188; copia netta 0,114; firme dei bordi), cosi' il controllo e' "alla forza del vero". Le misure sono quelle di ia08/ia09/ia17.
Nessuna parola del manoscritto compare in questo file; i valori veri sono numeri gia' pubblicati in `risultati/ia20_imitatore_gradini.json`.
"""
import bisect
import math
import os
import random
import sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

# valori veri (ia20, `risultati/ia20_imitatore_gradini.json`, chiave "vero"): bersagli della taratura
VERO_CONTATTO = 0.18840289899986576
VERO_COPIA_NETTA = 0.11382446086563112
VERO_BORDI_INIZIO_PRIMO = 0.2024      # punto medio dell'intervallo [0,1803; 0,2246] di ia20
VERO_BORDI_FINE_ULTIMO = 0.0911       # punto medio dell'intervallo [0,0795; 0,1028] di ia20


def sintetico_regole(righe, seme, divisore, unita, contatto=0.0, eco=0.0, ritocco=0.5, bordi_in=0.0, bordi_fi=0.0, ordine=0.0, n_fam=8, info=None):
    """`righe`: dizionari come ia07.libro_vero() (pagina, ini, parole, ...). Restituisce la nuova lista di righe. `info` (dict) riceve la tabella dei glifi
    preferiti e le famiglie."""
    rng = random.Random(seme)
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)
    pref = {a: rng.choice(unita) for a in unita}
    fam = {w: rng.randrange(n_fam) for w in voc}
    per_fam = []
    for f in range(n_fam):
        ws = [w for w in voc if fam[w] == f]
        c, tt = [], 0.0
        for w in ws:
            tt += conti[w]
            c.append(tt)
        per_fam.append((ws, c, tt))
    if info is not None:
        info.update(pref=pref, fam=fam)

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    def da_famiglia(f):
        ws, c, tt = per_fam[f]
        if not ws:
            return fresca()
        return ws[min(bisect.bisect_right(c, rng.random() * tt), len(ws) - 1)]

    def con_primo(w, g):
        u = divisore(w)
        u2 = [g] + list(u[1:])
        w2 = ''.join(u2)
        return w2 if divisore(w2) == u2 else w

    def modifica(w):
        u = divisore(w)
        for _ in range(12):
            tp = rng.choice((1, 2, 3))
            if tp == 1:
                i = rng.randrange(len(u))
                nuovo = rng.choice(unita)
                if nuovo == u[i]:
                    continue
                u2 = list(u)
                u2[i] = nuovo
            elif tp == 2:
                i = rng.randrange(len(u) + 1)
                u2 = list(u[:i]) + [rng.choice(unita)] + list(u[i:])
            else:
                if len(u) < 2:
                    continue
                i = rng.randrange(len(u))
                u2 = list(u[:i]) + list(u[i + 1:])
            w2 = ''.join(u2)
            if w2 != w and divisore(w2) == u2:
                return w2
        return w

    prime = [fresca() for _ in range(6)]
    ultime = [fresca() for _ in range(6)]
    out, pagina_corr, sopra = [], None, None
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, sopra = x['pagina'], None
        n = len(x['parole'])
        ps = []
        for k in range(n):
            prima = ps[-1] if ps else None
            if bordi_in and k == 0 and rng.random() < bordi_in:
                w = rng.choice(prime)
            elif bordi_fi and k == n - 1 and n > 1 and rng.random() < bordi_fi:
                w = rng.choice(ultime)
            elif eco and sopra and rng.random() < eco:
                w = rng.choice(sopra)
                if rng.random() < ritocco:
                    w = modifica(w)
            elif ordine and prima is not None and prima in fam and rng.random() < ordine:
                w = da_famiglia((fam[prima] + 1) % n_fam)
            else:
                w = fresca()
                if contatto and prima is not None and rng.random() < contatto:
                    w = con_primo(w, pref[divisore(prima)[-1]])
            ps.append(w)
        sopra = ps
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out


# ---------------------------------------------------------------- taratura (bisezione su una probabilita')

def bisezione(f, bersaglio, lo=0.0, hi=1.0, passi=7, tol=0.03):
    """Trova x in [lo, hi] con f(x) ~ bersaglio (f crescente). Restituisce (x, f(x), cronologia)."""
    cron = []
    f_hi = f(hi)
    cron.append((hi, f_hi))
    if f_hi < bersaglio:
        return hi, f_hi, cron
    best = (hi, f_hi)
    for _ in range(passi):
        mid = (lo + hi) / 2
        v = f(mid)
        cron.append((mid, v))
        if abs(v - bersaglio) < abs(best[1] - bersaglio):
            best = (mid, v)
        if abs(v - bersaglio) <= tol * bersaglio:
            return mid, v, cron
        if v < bersaglio:
            lo = mid
        else:
            hi = mid
    return best[0], best[1], cron


def righe_a_rows(righe, D):
    """Formato dei giudici: pagina -> [(inizio paragrafo, [parola come tupla di glifi])]."""
    out = OrderedDict()
    for x in righe:
        out.setdefault(x['pagina'], []).append((bool(x['ini']), [tuple(D(w)) for w in x['parole']]))
    return out


def proporzionale(f, bersaglio, p0, passi=5, tol=0.05, massimo=1.0):
    """Taratura per aggiustamenti proporzionali: p <- p * bersaglio / f(p) (f cresce con p). Restituisce (p migliore, f(p), cronologia)."""
    cron, p, best = [], p0, None
    for _ in range(passi):
        v = f(p)
        cron.append((p, v))
        if best is None or abs(v - bersaglio) < abs(best[1] - bersaglio):
            best = (p, v)
        if abs(v - bersaglio) <= tol * bersaglio:
            break
        p = min(massimo, p * 2 if v <= 0 else p * bersaglio / v)
    return best[0], best[1], cron
