# -*- coding: utf-8 -*-
"""Supporto di ia22 (modulo, non e' un esperimento): la "fase 0" descrittiva sulle varianti d'eco.

Domanda (ia22, fase 0): nelle parole che sono VARIANTI A UNA MODIFICA (un glifo cambiato, aggiunto o tolto, come in ia09, ia15b e ia17) di una parola della
riga in corso o di quella sopra, (a) dove cade la modifica (primo glifo, interno, ultimo glifo) e (b) la variante si accorda con il contatto della parola
prima (ultimo glifo della parola prima -> primo glifo, o primi due glifi, della parola) meglio della parola d'origine?

Che cosa c'e' qui, in parole semplici
- `una_modifica`: dice se una parola e' una variante a una modifica di un'altra, di che tipo e dove cade la modifica.
- `Contatto1` e `Contatto2`: tabelle P(primo glifo | ultimo glifo della parola prima) / P(primo glifo) e lo stesso per i primi due glifi, stimate sulle pagine
  di riferimento (nel lavoro vero: le pagine vere delle ALTRE pieghe, cioe' fuori piega), con la stessa lisciatura di `rifarlo_ritocchi.Contatto`.
- `conta_testo`: per un testo (pagina -> righe) conta le varianti per tipo e posto, quante modifiche cadono sul primo glifo rispetto a quante ne
  cadrebbero se il posto fosse a caso, e per le varianti che cambiano il primo glifo la differenza (in bit, scala del rapporto) fra l'accordo col contatto
  della variante e quello della parola d'origine. Controllo negativo: la stessa cosa con l'ultimo glifo della parola prima rimescolato (estratto a caso dalle
  parole del testo: le posizioni delle varianti non cambiano ma il contatto non c'e' piu').
Solo numeri e aggregati: nessuna parola esce da qui.
"""
import math
import random
from collections import Counter, OrderedDict

import numpy as np

S_CAND = 28            # candidati come nei modelli: ultime S parole della riga in corso e poi quelle della riga sopra
N_RIM = 5              # estrazioni del controllo negativo per pagina
LAM, TETTO = 5.0, 20.0


def una_modifica(c, w):
    """None se `w` non e' a una modifica da `c` (o e' uguale). Altrimenti (tipo, classe): tipo 'c' (un glifo cambiato), 'a' (aggiunto), 't' (tolto);
    classe 'primo' (la modifica tocca il primo glifo), 'ultimo' (l'ultimo) o 'interno'. In caso di piu' posti equivalenti si prende il primo."""
    n, m = len(c), len(w)
    if c == w:
        return None
    if m == n:
        d = [i for i in range(n) if c[i] != w[i]]
        if len(d) != 1:
            return None
        i = d[0]
        return 'c', ('primo' if i == 0 else 'ultimo' if i == n - 1 else 'interno')
    if m == n + 1:
        for i in range(n + 1):
            if w[:i] == c[:i] and w[i + 1:] == c[i:]:
                return 'a', ('primo' if i == 0 else 'ultimo' if i == n else 'interno')
        return None
    if m == n - 1 and m >= 1:
        for i in range(n):
            if c[:i] + c[i + 1:] == w:
                return 't', ('primo' if i == 0 else 'ultimo' if i == n - 1 else 'interno')
    return None


def posti_attesi(c, w, tipo):
    """Quanti posti ha la modifica del tipo dato (per l'attesa a posto uniforme): cambia e toglie n, aggiunge n + 1."""
    n = len(c)
    return n + 1 if tipo == 'a' else n


class Contatto1:
    """R(ultimo glifo, primo glifo) = P(primo | ultimo) / P(primo), con lisciatura (come rifarlo_ritocchi.Contatto). Indice G = glifo sconosciuto: rapporto 1."""

    def __init__(self, pagine):
        glifi = sorted({g for rows in pagine.values() for _, ws in rows for w in ws for g in w})
        self.idx = {g: i for i, g in enumerate(glifi)}
        G = self.G = len(glifi)
        c = np.zeros((G, G))
        pf = np.zeros(G)
        for rows in pagine.values():
            for _, ws in rows:
                for w in ws:
                    pf[self.idx[w[0]]] += 1
                for x, y in zip(ws, ws[1:]):
                    c[self.idx[x[-1]], self.idx[y[0]]] += 1
        pf = (pf + 0.5) / (pf.sum() + 0.5 * G)
        P = (c + LAM * pf[None, :]) / (c.sum(1, keepdims=True) + LAM)
        R = np.clip(P / pf[None, :], 1.0 / TETTO, TETTO)
        self.L = np.zeros((G + 1, G + 1))
        self.L[:G, :G] = np.log2(R)

    def log2r(self, ultimo, w):
        return float(self.L[self.idx.get(ultimo, self.G), self.idx.get(w[0], self.G)])


class Contatto2:
    """Lo stesso per i primi due glifi (o il solo glifo, se la parola ne ha uno)."""

    def __init__(self, pagine):
        glifi = sorted({g for rows in pagine.values() for _, ws in rows for w in ws for g in w})
        self.idx = {g: i for i, g in enumerate(glifi)}
        G = self.G = len(glifi)
        sim = Counter()
        for rows in pagine.values():
            for _, ws in rows:
                for w in ws:
                    sim[tuple(w[:2])] += 1
        self.sim = {s: i for i, s in enumerate(sorted(sim))}
        n = len(self.sim)
        c = np.zeros((G, n))
        pf = np.array([sim[s] for s in sorted(sim)], dtype=np.float64)
        for rows in pagine.values():
            for _, ws in rows:
                for x, y in zip(ws, ws[1:]):
                    c[self.idx[x[-1]], self.sim[tuple(y[:2])]] += 1
        pf = (pf + 0.5) / (pf.sum() + 0.5 * n)
        P = (c + LAM * pf[None, :]) / (c.sum(1, keepdims=True) + LAM)
        self.L = np.log2(np.clip(P / pf[None, :], 1.0 / TETTO, TETTO))

    def log2r(self, ultimo, w):
        a, s = self.idx.get(ultimo), self.sim.get(tuple(w[:2]))
        return 0.0 if a is None or s is None else float(self.L[a, s])


def tabelle_fuori_piega(vere, fold, pieghe=5):
    """piega -> (Contatto1, Contatto2) stimate sulle pagine `vere` (pagina -> righe) delle ALTRE pieghe."""
    out = {}
    for f in range(pieghe):
        ref = OrderedDict((p, r) for p, r in vere.items() if fold[p] != f)
        out[f] = (Contatto1(ref), Contatto2(ref))
    return out


def varianti_pagina(rows, S=S_CAND, modo='vicini', rng=None):
    """Per le parole di una pagina (righe [(inizio, [parola, ...])], parole = tuple di glifi): lista di (indice di riga, indice nella riga, categoria, dettaglio)
    con categoria 'copia' (uguale a un candidato), 'variante' (a una modifica da un candidato: dettaglio = (candidato, tipo, classe)) o 'altra'.
    I candidati ('vicini') sono le parole della riga in corso prima della parola (dalla piu' vicina) e poi quelle della riga sopra (dall'ultima), al massimo S.
    Controllo 'lontani': i candidati sono le parole (dall'ultima, al massimo S) di una riga della stessa pagina scelta a caso a distanza di almeno 3 righe: le
    varianti che saltano fuori sono varianti per caso (nessuna eco), con la stessa lunghezza di lista; se la pagina non ha una riga cosi' lontana, nessuna parola."""
    out = []
    righe = [list(ws) for _, ws in rows]
    for r, ws in enumerate(righe):
        if modo == 'lontani':
            lont = [q for q in range(len(righe)) if abs(q - r) >= 3]
            if not lont:
                continue
            fisso = righe[rng.choice(lont)][::-1][:S]
        else:
            sopra = righe[r - 1][::-1] if r > 0 else []
        for i, w in enumerate(ws):
            cand = fisso if modo == 'lontani' else (ws[:i][::-1] + sopra)[:S]
            if any(c == w for c in cand):
                out.append((r, i, 'copia', next(c for c in cand if c == w)))
                continue
            trovata = None
            for rango, c in enumerate(cand):
                m = una_modifica(c, w)
                if m is not None:
                    trovata = (c,) + m + (modo == 'vicini' and rango == 0 and i > 0,)          # ultimo: l'origine e' la parola prima stessa
                    break
            out.append((r, i, 'variante' if trovata else 'altra', trovata))
    return out


def conta_testo(pagine, fold, tab, seme, S=S_CAND):
    """Come `_conta_modo` con i candidati veri ('vicini') e con il controllo dei candidati lontani ('lontani', varianti per caso)."""
    return OrderedDict((modo, _conta_modo(pagine, fold, tab, seme, S, modo)) for modo in ('vicini', 'lontani'))


def _conta_modo(pagine, fold, tab, seme, S, modo):
    """Conti per un testo. `pagine`: pagina -> righe; `fold`: pagina -> piega; `tab`: tabelle_fuori_piega. Restituisce un dizionario di numeri (nessuna parola):
    - parole, copie (uguali a un candidato), varianti, altre; varianti che hanno come origine la parola prima (escluse dalle differenze di contatto: l'origine
      sarebbe la parola con cui si confronta); varianti per (tipo, classe) e le attese a posto uniforme (somma di 1/posti) per primo/ultimo;
    - per le varianti che cambiano il primo glifo (n1): somma delle differenze in bit (variante meno origine) con il contatto vero, e con l'ultimo glifo della
      parola prima rimescolato (media di N_RIM estrazioni); lo stesso per i primi due glifi (n2: varianti che cambiano uno dei primi due glifi);
    - accordo medio col contatto (bit, scala del rapporto) delle copie esatte e delle altre parole che hanno una parola prima;
    - per pagina: [n1, somma vera, somma rimescolata, n2, somma vera 2, somma rimescolata 2] (per gli errori)."""
    rng = random.Random(seme)
    pool = {f: [w[-1] for p, rows in pagine.items() if fold[p] == f for _, ws in rows for w in ws[:-1]] for f in set(fold.values())}
    tot = Counter()
    per_tc = Counter()
    att = dict(primo=0.0, ultimo=0.0, interno=0.0)
    s1 = s1r = s2 = s2r = 0.0
    n1 = n2 = 0
    acc = dict(copia=[0, 0.0], altra=[0, 0.0], variante=[0, 0.0])
    per_pag = OrderedDict()
    for p, rows in pagine.items():
        f = fold[p]
        c1, c2 = tab[f]
        righe = [list(ws) for _, ws in rows]
        pp = [0, 0.0, 0.0, 0, 0.0, 0.0]
        for (r, i, cat, det) in varianti_pagina(rows, S, modo, rng):
            w = righe[r][i]
            tot['parole'] += 1
            tot[cat] += 1
            prev = righe[r][i - 1] if i > 0 else None
            if prev is not None and cat in acc:
                acc[cat][0] += 1
                acc[cat][1] += c1.log2r(prev[-1], w)
            if cat != 'variante':
                continue
            c, tipo, classe, e_prima = det
            per_tc[(tipo, classe)] += 1
            k = posti_attesi(c, w, tipo)
            att['primo'] += 1.0 / k
            att['ultimo'] += 1.0 / k if len(c) > 1 or tipo == 'a' else 0.0
            if prev is None:
                continue
            if e_prima:                      # l'origine e' la parola prima: il suo "contatto" con se' stessa non e' un contatto fra due parole
                tot['varianti_da_parola_prima'] += 1
                continue
            ult = prev[-1]
            if w[0] != c[0]:
                d = c1.log2r(ult, w) - c1.log2r(ult, c)
                dr = 0.0
                for _ in range(N_RIM):
                    u = rng.choice(pool[f]) if pool[f] else ult
                    dr += c1.log2r(u, w) - c1.log2r(u, c)
                dr /= N_RIM
                n1 += 1
                s1 += d
                s1r += dr
                pp[0] += 1
                pp[1] += d
                pp[2] += dr
            if tuple(w[:2]) != tuple(c[:2]):
                d = c2.log2r(ult, w) - c2.log2r(ult, c)
                dr = 0.0
                for _ in range(N_RIM):
                    u = rng.choice(pool[f]) if pool[f] else ult
                    dr += c2.log2r(u, w) - c2.log2r(u, c)
                dr /= N_RIM
                n2 += 1
                s2 += d
                s2r += dr
                pp[3] += 1
                pp[4] += d
                pp[5] += dr
        per_pag[p] = pp
    att['interno'] = max(tot['variante'] - att['primo'] - att['ultimo'], 0.0)
    return OrderedDict([('parole', tot['parole']), ('copie', tot['copia']), ('varianti', tot['variante']), ('altre', tot['altra']),
                        ('varianti_da_parola_prima', tot['varianti_da_parola_prima']),
                        ('per_tipo_classe', OrderedDict(('%s_%s' % k, v) for k, v in sorted(per_tc.items()))),
                        ('attese_posto_uniforme', att), ('n1', n1), ('somma1_vera', s1), ('somma1_rimescolata', s1r),
                        ('n2', n2), ('somma2_vera', s2), ('somma2_rimescolata', s2r),
                        ('accordo', OrderedDict((k, v) for k, v in acc.items())),
                        ('pagine', list(per_pag)), ('per_pagina', list(per_pag.values()))])


def riassunto(r, boot=200, seme=1):
    """Dal risultato di `conta_testo` (o dalla somma di piu' risultati sullo stesso formato) i numeri letti:
    quota di modifiche sul primo glifo osservata e attesa a posto uniforme, e le differenze medie (vera - rimescolata) a uno e a due glifi con errore da
    ricampionamento delle pagine."""
    v = r['varianti']
    pt = r['per_tipo_classe']
    primo = sum(x for k, x in pt.items() if k.endswith('_primo'))
    ultimo = sum(x for k, x in pt.items() if k.endswith('_ultimo'))
    interno = sum(x for k, x in pt.items() if k.endswith('_interno'))
    out = OrderedDict([('varianti', v), ('quota_primo', primo / v if v else None), ('quota_interno', interno / v if v else None), ('quota_ultimo', ultimo / v if v else None),
                       ('attesa_primo', r['attese_posto_uniforme']['primo'] / v if v else None), ('attesa_ultimo', r['attese_posto_uniforme']['ultimo'] / v if v else None)])
    pp = np.array(r['per_pagina'], dtype=np.float64) if r['per_pagina'] else np.zeros((0, 6))
    rng = np.random.default_rng(seme)
    for nome, (a, b, c) in (('uno', (0, 1, 2)), ('due', (3, 4, 5))):
        n = pp[:, a].sum()
        d = (pp[:, b].sum() - pp[:, c].sum()) / n if n else None
        bs = []
        if len(pp) and n:
            for _ in range(boot):
                x = pp[rng.integers(0, len(pp), len(pp))]
                nn = x[:, a].sum()
                if nn:
                    bs.append((x[:, b].sum() - x[:, c].sum()) / nn)
        out['n_' + nome] = int(n)
        out['differenza_' + nome] = d
        out['vera_' + nome] = pp[:, b].sum() / n if n else None
        out['rimescolata_' + nome] = pp[:, c].sum() / n if n else None
        out['errore_' + nome] = float(np.std(bs, ddof=1)) if len(bs) > 1 else None
    out['accordo_medio'] = OrderedDict((k, (x[1] / x[0]) if x[0] else None) for k, x in r['accordo'].items())
    return out


def somma_risultati(lista):
    """Somma piu' risultati di `conta_testo` (libri dello stesso tipo) in uno solo, modo per modo."""
    return OrderedDict((modo, _somma_modo([r[modo] for r in lista])) for modo in lista[0])


def _somma_modo(lista):
    out = None
    for r in lista:
        if out is None:
            out = OrderedDict((k, (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)) for k, v in r.items())
            out['per_tipo_classe'] = Counter(r['per_tipo_classe'])
            out['attese_posto_uniforme'] = dict(r['attese_posto_uniforme'])
            out['accordo'] = {k: list(v) for k, v in r['accordo'].items()}
            out['per_pagina'] = [list(x) for x in r['per_pagina']]
            continue
        for k in ('parole', 'copie', 'varianti', 'altre', 'varianti_da_parola_prima', 'n1', 'somma1_vera', 'somma1_rimescolata', 'n2', 'somma2_vera', 'somma2_rimescolata'):
            out[k] += r[k]
        out['per_tipo_classe'].update(r['per_tipo_classe'])
        for k in out['attese_posto_uniforme']:
            out['attese_posto_uniforme'][k] += r['attese_posto_uniforme'][k]
        for k in out['accordo']:
            out['accordo'][k][0] += r['accordo'][k][0]
            out['accordo'][k][1] += r['accordo'][k][1]
        out['per_pagina'] += [list(x) for x in r['per_pagina']]
    return out
