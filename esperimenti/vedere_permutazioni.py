# -*- coding: utf-8 -*-
"""Rimescolamenti, categorie di contesto, pezzi di parola e parole di ricambio per ia13 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- `VARIANTI`: i modi di cambiare l'ordine delle parole dentro una riga (tutte rimescolate, solo coppie vicine scambiate, solo la
  prima o l'ultima spostata, mezze righe, blocchi, ...). Ogni modo e' una permutazione `pi`: la riga nuova e' `[parole[pi[k]] for k]`.
- `categorie`: per ogni parola, che cosa le e' rimasto del suo contesto dopo il rimescolamento (quante parole di fila le stanno
  ancora prima, o se non e' cambiato niente).
- `costi_parola`: i bit di ogni parola divisi nei quattro pezzi (primo glifo, interno, ultimo glifo, spazio o a capo).
- `Ricambi`: per la prova "lasciare alla rete solo un pezzo" si sostituisce una parola con un'altra parola del testo di
  addestramento che ha lo stesso pezzo (stesso ultimo glifo, stessa lunghezza, stessa famiglia, ...).
Nessun risultato e' scritto qui; nessuna parola del Voynich viene stampata.
"""
import bisect
import random
from collections import OrderedDict

import numpy as np


# ---------------------------------------------------------------- rimescolamenti (permutazioni di una riga di n parole)

def p_tutto(n, rnd):
    pi = list(range(n))
    rnd.shuffle(pi)
    return pi


def p_vicine(n, rnd):
    """Scambia coppie di parole adiacenti: da sinistra a destra, con probabilita' 1/2 si scambia la parola con la prossima e si salta."""
    pi = list(range(n))
    i = 0
    while i + 1 < n:
        if rnd.random() < 0.5:
            pi[i], pi[i + 1] = pi[i + 1], pi[i]
            i += 2
        else:
            i += 1
    return pi


def p_finestra3(n, rnd):
    """Rimescola dentro finestre consecutive di 3 parole (la prima finestra e' 0-2, poi 3-5, ...)."""
    pi = list(range(n))
    for s in range(0, n, 3):
        b = pi[s:s + 3]
        rnd.shuffle(b)
        pi[s:s + 3] = b
    return pi


def _blocchi(k):
    def f(n, rnd):
        bl = [list(range(s, min(s + k, n))) for s in range(0, n, k)]
        rnd.shuffle(bl)
        return [i for b in bl for i in b]
    return f


def p_mezze(n, rnd):
    """Rimescola la prima meta' (n // 2 parole) e la seconda meta' ognuna per conto suo."""
    pi = list(range(n))
    h = n // 2
    a, b = pi[:h], pi[h:]
    rnd.shuffle(a)
    rnd.shuffle(b)
    return a + b


def p_bordi_fissi(n, rnd):
    """La prima e l'ultima parola restano dove sono; le altre si rimescolano."""
    pi = list(range(n))
    if n >= 4:
        mid = pi[1:n - 1]
        rnd.shuffle(mid)
        pi[1:n - 1] = mid
    return pi


def p_solo_bordi(n, rnd):
    """Si scambiano solo la prima e l'ultima parola; il resto non si tocca."""
    pi = list(range(n))
    if n >= 2:
        pi[0], pi[n - 1] = pi[n - 1], pi[0]
    return pi


def p_prima_sposta(n, rnd):
    """La prima parola va in un posto a caso diverso dal primo; le altre restano nell'ordine."""
    if n < 2:
        return list(range(n))
    nuova = list(range(1, n))
    nuova.insert(rnd.randrange(1, n), 0)
    return nuova


def p_ultima_sposta(n, rnd):
    """L'ultima parola va in un posto a caso diverso dall'ultimo; le altre restano nell'ordine."""
    if n < 2:
        return list(range(n))
    nuova = list(range(n - 1))
    nuova.insert(rnd.randrange(0, n - 1), n - 1)
    return nuova


def _alterna(resto):
    def f(n, rnd):
        pi = list(range(n))
        idx = list(range(resto, n, 2))
        sh = idx[:]
        rnd.shuffle(sh)
        for a, b in zip(idx, sh):
            pi[a] = b
        return pi
    return f


def p_inversa(n, rnd):
    return list(range(n))[::-1]


# nome -> (funzione, spiegazione breve)
VARIANTI = OrderedDict([
    ('tutto', (p_tutto, 'tutte le parole della riga rimescolate')),
    ('vicine', (p_vicine, 'coppie adiacenti scambiate (probabilita\' 1/2, da sinistra)')),
    ('finestra3', (p_finestra3, 'rimescolate dentro finestre di 3 parole')),
    ('blocchi2', (_blocchi(2), 'blocchi di 2 parole consecutive rimescolati fra loro (le coppie restano)')),
    ('blocchi3', (_blocchi(3), 'blocchi di 3 parole consecutive rimescolati fra loro')),
    ('mezze', (p_mezze, 'rimescolate dentro la prima e dentro la seconda mezza riga')),
    ('bordi_fissi', (p_bordi_fissi, 'prima e ultima ferme, il resto rimescolato')),
    ('solo_bordi', (p_solo_bordi, 'scambiate solo prima e ultima')),
    ('prima_sposta', (p_prima_sposta, 'la prima parola va in un posto a caso')),
    ('ultima_sposta', (p_ultima_sposta, 'l\'ultima parola va in un posto a caso')),
    ('pari_mescolati', (_alterna(0), 'rimescolate solo le parole nei posti 0, 2, 4, ... (a due a due non adiacenti)')),
    ('dispari_mescolati', (_alterna(1), 'rimescolate solo le parole nei posti 1, 3, 5, ...')),
    ('inversa', (p_inversa, 'riga letta al contrario')),
])
NOMI_VARIANTI = list(VARIANTI)


def permutazioni(pagine, variante, seme):
    """Per ogni pagina (nell'ordine dato) e ogni riga, la permutazione `pi` della variante. Un solo flusso casuale su tutto il testo
    (stesse permutazioni in ogni processo)."""
    f = VARIANTI[variante][0]
    rnd = random.Random(seme)
    return OrderedDict((p, [f(len(ws), rnd) for _, ws in rows]) for p, rows in pagine.items())


# ---------------------------------------------------------------- categorie del contesto rimasto

NCAT = 6
NOMI_CAT = ['inizio riga (spostata)', 'parola prima cambiata', 'parola prima uguale (1)', 'prime due uguali (2)',
            'prime tre o piu\' uguali', 'contesto invariato']


def categorie(pi):
    """Per ogni parola (indice VECCHIO i), la categoria del suo contesto nella riga nuova:
    0 = e' in prima posizione ma prima non lo era; 1 = la parola prima e' cambiata; 2, 3, 4 = le ultime 1, 2, 3 o piu' parole prima sono
    le stesse di prima (ma il contesto piu' lontano e' cambiato); 5 = tutto il contesto e' uguale (stessa parola, stesso posto, stessa
    riga prima)."""
    n = len(pi)
    out = [0] * n
    intatto = True            # tutta la riga fino a k e' ancora quella di prima
    for k, i in enumerate(pi):
        if intatto and i == k:
            c = 5
        else:
            intatto = False
            if k == 0:
                c = 0
            else:
                m = 0
                while k - m - 1 >= 0 and i - m - 1 >= 0 and pi[k - m - 1] == i - m - 1:
                    m += 1
                c = 1 + min(m, 3)
        out[i] = c
    return out


# ---------------------------------------------------------------- costi in bit di ogni parola

def posizioni_parole(rows):
    """Per ogni parola di una pagina messa in segni (come G.codifica): (inizio, lunghezza, posto nella riga). Copiata da ia09."""
    pos, out = 0, []
    for ini, ws in rows:
        if ini:
            pos += 1
        for j, w in enumerate(ws):
            if j:
                pos += 1
            out.append((pos, len(w), j))
            pos += len(w)
        pos += 1
    return out


def costi_parola(x, ps):
    """x = sorprese (bit) di ogni segno della pagina; ps = posizioni_parole. Restituisce una matrice (parole, 4): primo glifo, interno,
    ultimo glifo (solo se la parola ha almeno 2 glifi), spazio o a capo dopo la parola. La somma delle 4 colonne e' il costo della parola."""
    a = np.array([p[0] for p in ps], dtype=np.int64)
    ln = np.array([p[1] for p in ps], dtype=np.int64)
    cs = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    tot = cs[a + ln + 1] - cs[a]
    primo = x[a].astype(np.float64)
    fine = x[a + ln].astype(np.float64)
    ultimo = np.where(ln >= 2, x[np.maximum(a + ln - 1, 0)], 0.0)
    inter = tot - primo - ultimo - fine
    return np.stack([primo, inter, ultimo, fine], axis=1)


# ---------------------------------------------------------------- pezzi di parola e parole di ricambio

PEZZI = ['nessuno', 'lunghezza', 'ultimo1', 'ultimi2', 'primo1', 'primo_ultimo', 'classe']
NOMI_PEZZI = OrderedDict([
    ('nessuno', 'nessun pezzo (una parola qualunque, secondo la frequenza)'),
    ('lunghezza', 'solo la lunghezza'),
    ('ultimo1', 'solo l\'ultimo glifo'),
    ('ultimi2', 'solo gli ultimi due glifi'),
    ('primo1', 'solo il primo glifo'),
    ('primo_ultimo', 'primo e ultimo glifo'),
    ('classe', 'solo la famiglia (classe di ia09)'),
])


def chiave_pezzo(nome, w, classe):
    if nome == 'nessuno':
        return 0
    if nome == 'lunghezza':
        return len(w)
    if nome == 'ultimo1':
        return w[-1]
    if nome == 'ultimi2':
        return w[-2:]
    if nome == 'primo1':
        return w[0]
    if nome == 'primo_ultimo':
        return (w[0], w[-1])
    if nome == 'classe':
        return int(classe)
    raise ValueError(nome)


class Ricambi:
    """Parole di ricambio: per ogni pezzo, i tipi di parola dell'addestramento con lo stesso pezzo, pesati per la frequenza.
    `C` e' un Corpus (sintassi_modelli), `cw` i conti per tipo sulle sole pagine di addestramento, `cls` la classe di ogni tipo."""

    def __init__(self, C, cw, cls):
        self.C = C
        self.cls = cls
        self.str = {}
        tipi = np.where(cw > 0)[0]
        self.pool = {}
        for nome in PEZZI:
            d = {}
            for t in tipi:
                t = int(t)
                k = chiave_pezzo(nome, self.parola(t), cls[t])
                d.setdefault(k, []).append(t)
            out = {}
            for k, ts in d.items():
                pesi = np.array([cw[t] for t in ts], dtype=float)
                out[k] = (ts, np.cumsum(pesi))
            self.pool[nome] = out
        self.fallite = 0
        self.richieste = 0

    def parola(self, t):
        s = self.str.get(t)
        if s is None:
            s = self.str[t] = self.C.parole_in_glifi(t)
        return s

    def estrai(self, nome, t, rnd):
        """Una parola (tipo) a caso con lo stesso pezzo di `t`. Se nell'addestramento non ce n'e' nessuna, resta `t`."""
        self.richieste += 1
        e = self.pool[nome].get(chiave_pezzo(nome, self.parola(t), self.cls[t]))
        if e is None:
            self.fallite += 1
            return t
        ts, cum = e
        j = bisect.bisect_right(cum, rnd.random() * cum[-1])
        return ts[min(j, len(ts) - 1)]
