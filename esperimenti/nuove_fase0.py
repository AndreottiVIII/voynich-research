# -*- coding: utf-8 -*-
"""Supporto di ia24 (modulo, non e' un esperimento): la "fase 0" descrittiva sulle parole NUOVE.

Domanda: in un testo (il vero, il v21, un libro scritto da un imitatore) le parole che non compaiono nel lessico dei fogli di addestramento ("nuove", stessa definizione del
costo di forma di ia08/ia20: lessico = pagine vere delle ALTRE pieghe) come sono fatte? Sono ritocchi di parole del lessico, o sono costruite a caselle, o sono scritte segno
per segno?

Che cosa si misura (per ogni piega: lessico e modelli di forma delle altre pieghe; poi si somma sulle pieghe):
  (a) distanza di modifica dalla parola nota piu' vicina (1, 2, 3 o piu') e frequenza (nel lessico) di quella parola; quota di parole nuove a una o due modifiche da una
      delle K parole piu' frequenti del lessico;
  (b) lunghezza delle parole nuove e delle note;
  (c) profilo per posizione (primo glifo, glifi interni, ultimo glifo) delle parole nuove e delle note, e la divergenza di Jensen-Shannon (bit) fra i due;
  (d) quota di parole nuove spiegabili come "parola nota + un pezzo noto" (pezzo = uno dei 20 prefissi o suffissi piu' frequenti di 1-3 glifi) e come "parola nota + un
      pezzo qualsiasi di 1-3 glifi";
  (e) il costo di forma (trigrammi di glifi, `rifarlo_ritocchi.Forma`, la stessa misura di ia20) scomposto per posto nella parola: primo glifo, secondo, terzo, dal quarto in poi,
      fine parola; le cinque parti sommano al costo di forma (bit per glifo) di ia20;
  (f) il costo delle parole nuove sotto un modello a caselle (`nuove_modelli.Caselle`, EM sul lessico delle altre pieghe), in bit per glifo.
Ogni testo e' una matrice pagine x numeri: si somma (con l'errore da ricampionamento delle pagine) e se ne ricavano i numeri letti (`derivate`).
Controlli: il testo vero con le parole nuove sostituite da parole PIANTATE (`pianta`): "ritocco" (una o due modifiche di una parola frequente del lessico), "libero" (glifi a
caso della stessa lunghezza) e "caselle" (parola campionata dal modello a caselle).
Solo numeri e aggregati: nessuna parola esce da qui.
"""
import math
import random
from collections import Counter, OrderedDict

import numpy as np

import nuove_modelli as NM
import rifarlo_ritocchi as R

BIN_FREQ = (1, 2, 5, 20)             # conteggio nel lessico: 1 / 2-4 / 5-19 / 20 o piu'
NLEN = 12                            # lunghezze 1..11 e 12 o piu'
N_PEZZI = 20                         # prefissi e suffissi piu' frequenti
KMAX_PEZZO = 3
BOOT = 200


def classe_freq(n):
    return 0 if n < 2 else 1 if n < 5 else 2 if n < 20 else 3


# ---------------------------------------------------------------- lessico di una piega, indici dei vicini

class IndiceVicini:
    """Indice "a cancellazioni" sulle parole di un lessico: trova le parole a distanza <= 2 da una parola data."""

    def __init__(self, conti):
        self.parole = list(conti)
        self.cnt = [conti[w] for w in self.parole]
        self.d = {}
        for i, w in enumerate(self.parole):
            for v in NM.cancellazioni(w, 2):
                self.d.setdefault(v, []).append(i)
        self._memo = {}

    def cerca(self, w):
        """(distanza 1, 2 o 3 = "3 o piu'", conteggio della parola piu' vicina; a pari distanza la piu' frequente). `w` non e' nel lessico."""
        r = self._memo.get(w)
        if r is not None:
            return r
        cand = set()
        for v in NM.cancellazioni(w, 2):
            cand.update(self.d.get(v, ()))
        best = (3, 0)
        lw = len(w)
        for i in cand:
            c = self.parole[i]
            if abs(len(c) - lw) > 2 or c == w:
                continue
            dd = NM.distanza(c, w)
            if dd <= 2 and (dd < best[0] or (dd == best[0] and self.cnt[i] > best[1])):
                best = (dd, self.cnt[i])
        self._memo[w] = best
        return best


class Piega:
    """Tutto cio' che serve a misurare le parole nuove delle pagine della piega `f`: lessico (pagine vere delle altre pieghe), indici dei vicini, forma, caselle, pezzi."""

    def __init__(self, vere, fold, f, glifi, ktop, con_caselle=True):
        self.f = f
        self.glifi = glifi
        self.gi = {g: i for i, g in enumerate(glifi)}
        pv = [rows for p, rows in vere.items() if fold[p] != f]
        self.cnt = Counter(w for rows in pv for _, ws in rows for w in ws)
        self.noti = set(self.cnt)
        self.forma = R.Forma(self.cnt)
        self.indice = IndiceVicini(self.cnt)
        top = sorted(self.cnt, key=lambda w: (-self.cnt[w], w))[:ktop]
        self.top = top
        self.indice_top = IndiceVicini({w: self.cnt[w] for w in top})
        pre, suf = Counter(), Counter()
        for w, k in self.cnt.items():
            for j in range(1, KMAX_PEZZO + 1):
                if len(w) > j:
                    pre[w[:j]] += k
                    suf[w[-j:]] += k
        self.pre = {p for p, _ in sorted(pre.items(), key=lambda kv: (-kv[1], kv[0]))[:N_PEZZI]}
        self.suf = {p for p, _ in sorted(suf.items(), key=lambda kv: (-kv[1], kv[0]))[:N_PEZZI]}
        self.hmm = None
        if con_caselle:
            tipi = [tuple(self.gi[g] for g in w) for w in self.cnt if all(g in self.gi for g in w)]
            self.hmm = NM.Caselle.adatta(tipi, len(glifi), NM.NSLOT, 15)
        self._ben = {}

    def bit_posizioni(self, w):
        """Bit per ogni simbolo di `w` (glifi, poi la fine parola) sotto la forma a trigrammi: lista di len(w) + 1 numeri."""
        fm = self.forma
        a = b = fm.q
        out = []
        for x in [fm.idx.get(g, fm.q - 1) for g in w] + [fm.q]:
            out.append(-float(fm.l3[a, b, x]))
            a, b = b, x
        return out

    def spiegabile(self, w):
        """(con un pezzo frequente, con un pezzo qualsiasi) = w e' una parola nota piu' un pezzo di 1-3 glifi davanti o dietro."""
        n = len(w)
        freq = qual = False
        for j in range(1, min(KMAX_PEZZO, n - 1) + 1):
            if w[j:] in self.noti:
                qual = True
                freq = freq or w[:j] in self.pre
            if w[:n - j] in self.noti:
                qual = True
                freq = freq or w[n - j:] in self.suf
        return freq, qual


# ---------------------------------------------------------------- vettore dei conti di una pagina

def campi(G):
    return OrderedDict([('n_parole', 1), ('n_nuove', 1), ('dist', 3), ('dist_freq', 8), ('s_top', 2), ('len_nuove', NLEN), ('len_note', NLEN),
                        ('primo_nuove', G), ('primo_note', G), ('int_nuove', G), ('int_note', G), ('ult_nuove', G), ('ult_note', G),
                        ('spiega', 2), ('forma_pos', 5), ('glifi_nuovi', 1), ('caselle', 3)])


def fette(G):
    out, a = OrderedDict(), 0
    for k, n in campi(G).items():
        out[k] = slice(a, a + n)
        a += n
    return out, a


def conta_pagine(rows_per_pagina, pieghe_di, oggetti, glifi):
    """Matrice (pagine, numeri) per i testi dati: `rows_per_pagina`: pagina -> righe [(inizio, [parola, ...])]; `pieghe_di`: pagina -> piega; `oggetti`: piega -> Piega."""
    G = len(glifi)
    F, tot = fette(G)
    M = np.zeros((len(rows_per_pagina), tot))
    gi = {g: i for i, g in enumerate(glifi)}
    for r, (p, rows) in enumerate(rows_per_pagina.items()):
        ob = oggetti[pieghe_di[p]]
        v = M[r]
        for _, ws in rows:
            for w in ws:
                v[F['n_parole']] += 1
                L = min(len(w), NLEN) - 1
                nuova = w not in ob.noti
                if not nuova:
                    v[F['len_note'].start + L] += 1
                    v[F['primo_note'].start + gi[w[0]]] += 1
                    v[F['ult_note'].start + gi[w[-1]]] += 1
                    for g in w[1:-1]:
                        v[F['int_note'].start + gi[g]] += 1
                    continue
                v[F['n_nuove']] += 1
                v[F['len_nuove'].start + L] += 1
                v[F['primo_nuove'].start + gi[w[0]]] += 1
                v[F['ult_nuove'].start + gi[w[-1]]] += 1
                for g in w[1:-1]:
                    v[F['int_nuove'].start + gi[g]] += 1
                dd, cn = ob.indice.cerca(w)
                v[F['dist'].start + dd - 1] += 1
                if dd <= 2:
                    v[F['dist_freq'].start + (dd - 1) * 4 + classe_freq(cn)] += 1
                dt = ob.indice_top.cerca(w)[0]
                if dt <= 1:
                    v[F['s_top'].start] += 1
                if dt <= 2:
                    v[F['s_top'].start + 1] += 1
                fr, qu = ob.spiegabile(w)
                v[F['spiega'].start] += fr
                v[F['spiega'].start + 1] += qu
                bp = ob.bit_posizioni(w)
                n = len(w)
                for l, b in enumerate(bp):
                    k = 4 if l == n else min(l, 3)
                    v[F['forma_pos'].start + k] += b
                v[F['glifi_nuovi']] += n
                if ob.hmm is not None and all(g in ob.gi for g in w):
                    bits = ob.hmm.bit_parola(tuple(ob.gi[g] for g in w))
                    v[F['caselle'].start] += sum(bits)
                    v[F['caselle'].start + 1] += n
                    v[F['caselle'].start + 2] += 1
    return M


def js_bit(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    if p.sum() == 0 or q.sum() == 0:
        return None
    p, q = p / p.sum(), q / q.sum()
    m = 0.5 * (p + q)
    kl = lambda a, b: float(sum(x * math.log2(x / y) for x, y in zip(a, b) if x > 0))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def derivate(v, G):
    """I numeri letti da un vettore somma (vedi `campi`)."""
    F, _ = fette(G)
    g = lambda k: v[F[k]]
    nn, npar = float(g('n_nuove')[0]), float(g('n_parole')[0])
    div = lambda a, b: (a / b) if b else None
    out = OrderedDict()
    out['quota_nuove'] = div(nn, npar)
    d = g('dist')
    df = g('dist_freq').reshape(2, 4)
    out['dist1'], out['dist2'], out['dist3'] = (div(float(d[i]), nn) for i in range(3))
    out['dist1_freq5'] = div(float(df[0, 2] + df[0, 3]), nn)
    out['dist1_freq20'] = div(float(df[0, 3]), nn)
    out['dist2_freq5'] = div(float(df[1, 2] + df[1, 3]), nn)
    out['top_1'], out['top_2'] = (div(float(x), nn) for x in g('s_top'))
    ln, lk = g('len_nuove'), g('len_note')
    L = np.arange(1, NLEN + 1)
    out['lung_nuove'] = div(float((ln * L).sum()), float(ln.sum()))
    out['lung_note'] = div(float((lk * L).sum()), float(lk.sum()))
    out['js_lunghezza'] = js_bit(ln, lk)
    out['js_primo'] = js_bit(g('primo_nuove'), g('primo_note'))
    out['js_interno'] = js_bit(g('int_nuove'), g('int_note'))
    out['js_ultimo'] = js_bit(g('ult_nuove'), g('ult_note'))
    out['spiega_frequente'], out['spiega_qualsiasi'] = (div(float(x), nn) for x in g('spiega'))
    gl = float(g('glifi_nuovi')[0])
    fp = g('forma_pos')
    out['costo_forma'] = div(float(fp.sum()), gl)
    for nome, x in zip(('forma_primo', 'forma_secondo', 'forma_terzo', 'forma_dopo', 'forma_fine'), fp):
        out[nome] = div(float(x), gl)
    cs = g('caselle')
    out['costo_caselle'] = div(float(cs[0]), float(cs[1]))
    return out


def riassunto(M, G, boot=BOOT, seme=1):
    """(derivate della somma, errori da ricampionamento delle pagine, somma). Con boot=0 niente errori."""
    S = M.sum(0)
    d = derivate(S, G)
    err = OrderedDict((k, None) for k in d)
    if boot and len(M) > 1:
        rng = np.random.default_rng(seme)
        bs = []
        for _ in range(boot):
            bs.append(derivate(M[rng.integers(0, len(M), len(M))].sum(0), G))
        for k in d:
            xs = [b[k] for b in bs if b[k] is not None]
            err[k] = float(np.std(xs, ddof=1)) if len(xs) > 1 else None
    return d, err, S


# ---------------------------------------------------------------- testi con parole nuove piantate (controlli)

def pianta(vere, fold, oggetti, glifi, modo, seme):
    """Il testo vero con ogni parola NUOVA (non nel lessico della sua piega) sostituita da una parola piantata:
    - 'ritocco': una parola scelta con la sua frequenza fra le piu' frequenti del lessico, con una modifica (probabilita' 0,6) o due (0,4), ognuna un glifo cambiato,
      aggiunto o tolto con la stessa probabilita' (glifo a caso fra quelli del testo);
    - 'libero': glifi a caso (dalla frequenza dei glifi nelle parole distinte del lessico), con la lunghezza della parola sostituita;
    - 'caselle': una parola campionata dal modello a caselle della piega.
    La parola piantata non e' mai nel lessico. Restituisce le pagine nello stesso formato."""
    rng = random.Random(seme)
    out = OrderedDict()
    cache = {}
    for p, rows in vere.items():
        ob = oggetti[fold[p]]
        if ob.f not in cache:
            tot = Counter(g for w in ob.cnt for g in w)
            gl = [g for g in glifi if tot[g] > 0]
            cache[ob.f] = (gl, [tot[g] for g in gl], [ob.cnt[w] for w in ob.top])
        gl, pg, pt = cache[ob.f]

        def ritocca(u):
            u = list(u)
            tp = rng.choice((1, 2, 3))
            if tp == 1:
                i = rng.randrange(len(u))
                g = rng.choice(gl)
                if g == u[i]:
                    return None
                u[i] = g
            elif tp == 2:
                u.insert(rng.randrange(len(u) + 1), rng.choice(gl))
            else:
                if len(u) < 2:
                    return None
                del u[rng.randrange(len(u))]
            return u

        def nuova_parola(lunghezza):
            for _ in range(60):
                if modo == 'ritocco':
                    u = list(rng.choices(ob.top, weights=pt)[0])
                    for _k in range(1 if rng.random() < 0.6 else 2):
                        u = ritocca(u)
                        if u is None:
                            break
                    if u is None:
                        continue
                elif modo == 'libero':
                    u = rng.choices(gl, weights=pg, k=lunghezza)
                else:
                    u = [glifi[i] for i in ob.hmm.campiona(rng)]
                w = tuple(u)
                if w and w not in ob.noti:
                    return w
            return None

        nr = []
        for ini, ws in rows:
            nws = []
            for w in ws:
                if w in ob.noti:
                    nws.append(w)
                else:
                    x = nuova_parola(len(w))
                    nws.append(x if x is not None else w)
            nr.append((ini, nws))
        out[p] = nr
    return out
