# -*- coding: utf-8 -*-
"""Testi di supporto per ia10: inglese (Brown, con le categorie grammaticali), latino (UD Latin-PROIEL, con le categorie),
testi sintetici con grammatica nota, pieghe per pagina. Nessuna parola e' scritta nei risultati: qui si caricano e basta.

Un testo e' un oggetto Testo: pagine (pagina -> righe; riga = (inizio_paragrafo, [parola, ...]); parola = tupla di segni),
piega (pagina -> 0..4, stessa ricetta di ia01: pagine in ordine, mescolate con random.Random(3961), piega = posto % 5),
tipo (pagina -> (sezione, lingua A/B) per il Voynich, altrimenti vuoto), etichette (pagina -> lista, per riga, delle categorie
di ogni parola; solo per i testi con categorie note).

Fonti scaricate (dati/cache/ia10/fonti, protette dal diritto d'autore, non si ridistribuiscono):
- Brown Corpus (Francis e Kucera, 1964/1979), dai dati di NLTK: "redistribution permitted" (README del corpus);
- Universal Dependencies, UD Latin-PROIEL (treebank del PROIEL: Vulgata, Cesare, Cicerone, ...): licenza CC BY-NC-SA 4.0.
"""
import math
import os
import random
import zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
FONTI = os.path.join(QUI, '..', 'dati', 'cache', 'ia10', 'fonti')
BROWN_ZIP = os.path.join(FONTI, 'brown', 'brown.zip')
UD_LATINO = os.path.join(FONTI, 'ud_latin_proiel', 'la_proiel-ud-train.conllu')
NF = 5
PAGINE_POS = 196          # le stesse dimensioni del Voynich: 196 pagine di 23 righe
RIGHE_POS = 23
PAROLE_RIGA_POS = 8       # circa le parole per riga del Voynich (35.000 parole in 196 x 23 righe)


class Testo:
    def __init__(self, nome, pagine, tipo=None, etichette=None, descrizione='', piega=None):
        self.nome = nome
        self.pagine = pagine
        self.tipo = tipo or {}
        self.etichette = etichette
        self.descrizione = descrizione
        self.piega = piega or piegatura(list(pagine))

    def n_parole(self):
        return sum(len(ws) for rows in self.pagine.values() for _, ws in rows)


def piegatura(nomi, seme=3961):
    """Stessa ricetta di ia01.contesto: nomi in ordine, mescolati con random.Random(3961), piega = posto % 5."""
    ordine = sorted(nomi)
    random.Random(seme).shuffle(ordine)
    return {p: i % NF for i, p in enumerate(ordine)}


def righe_a_pagine(parole, etichette=None, prefisso='P', per_riga=PAROLE_RIGA_POS, righe=RIGHE_POS, pagine=PAGINE_POS):
    """Flusso di parole (tuple) -> pagine di `righe` righe di `per_riga` parole. Le pagine sono `pagine` (si ferma a quel
    numero). Le etichette (lista parallela) seguono la stessa divisione."""
    out, et = OrderedDict(), OrderedDict()
    n = per_riga * righe
    for i in range(pagine):
        blocco = parole[i * n:(i + 1) * n]
        if len(blocco) < n:
            break
        nome = '%s%03d' % (prefisso, i)
        out[nome] = [(j % 8 == 0, list(blocco[j * per_riga:(j + 1) * per_riga])) for j in range(righe)]
        if etichette is not None:
            eb = etichette[i * n:(i + 1) * n]
            et[nome] = [list(eb[j * per_riga:(j + 1) * per_riga]) for j in range(righe)]
    return out, (et if etichette is not None else None)


# ---------------------------------------------------------------- inglese: Brown

def categoria_brown(tag):
    """Categoria grossolana (11) da un'etichetta del Brown Corpus. Mia semplificazione, vicina a quella "universale" di NLTK
    (da ricontrollare): NOME, VERBO, AUSILIARE, AGGETTIVO, AVVERBIO, ARTICOLO/DETERMINANTE, PRONOME, PREPOSIZIONE,
    CONGIUNZIONE, NUMERO, PARTICELLA; None per punteggiatura e simboli."""
    t = tag.lower().split('+')[0]
    t = t.replace('*', '')
    if not any(c.isalpha() for c in t):
        return None
    for suf in ('-hl', '-tl', '-nc'):
        t = t.replace(suf, '')
    if t.startswith('fw-'):
        t = t[3:]
    if t in ('pp$', 'pp$$', 'wp$', 'dt$'):
        return 'DET'
    t = t.rstrip('$')
    if t in ('nn', 'nns', 'np', 'nps', 'nr', 'nrs'):
        return 'NOME'
    if t in ('vb', 'vbd', 'vbg', 'vbn', 'vbz'):
        return 'VERBO'
    if t == 'md' or t.startswith('be') or t.startswith('hv') or t.startswith('do'):
        return 'AUS'
    if t.startswith('jj'):
        return 'AGG'
    if t in ('rb', 'rbr', 'rbt', 'rn', 'ql', 'qlp', 'wql', 'wrb', ''):
        return 'AVV'
    if t in ('at', 'dt', 'dti', 'dts', 'dtx', 'abn', 'abx', 'ap', 'wdt'):
        return 'DET'
    if t in ('pn', 'ppl', 'ppls', 'ppo', 'pps', 'ppss', 'wps', 'wpo', 'pp', 'ppa'):
        return 'PRON'
    if t == 'in':
        return 'PREP'
    if t in ('cc', 'cs'):
        return 'CONG'
    if t in ('cd', 'od'):
        return 'NUM'
    if t in ('to', 'rp'):
        return 'PART'
    return 'ALTRO'


def carica_brown(seme=1010, n_parole=PAGINE_POS * RIGHE_POS * PAROLE_RIGA_POS):
    """Brown: file scelti a caso (seme) fino ad avere n_parole parole (minuscole, senza punteggiatura), poi pagine di 23
    righe da 8 parole. Le righe non seguono le frasi: come in un manoscritto, l'a capo e' indipendente dalla sintassi."""
    z = zipfile.ZipFile(BROWN_ZIP)
    nomi = sorted(n for n in z.namelist() if n.startswith('brown/c') and not n.endswith('/'))
    random.Random(seme).shuffle(nomi)
    parole, cat = [], []
    for n in nomi:
        if len(parole) >= n_parole:
            break
        for tok in z.read(n).decode('latin-1').split():
            if '/' not in tok:
                continue
            w, t = tok.rsplit('/', 1)
            c = categoria_brown(t)
            if c is None or not w:
                continue
            parole.append(tuple(w.lower()))
            cat.append(c)
    parole, cat = parole[:n_parole], cat[:n_parole]
    pagine, et = righe_a_pagine(parole, cat, prefisso='E')
    return Testo('inglese', pagine, etichette=et, descrizione='Brown Corpus (NLTK), %d parole, categorie grossolane' % len(parole))


# ---------------------------------------------------------------- latino: UD Latin-PROIEL

def carica_latino_ud(seme=1011, n_parole=PAGINE_POS * RIGHE_POS * PAROLE_RIGA_POS, blocco=1000):
    """UD Latin-PROIEL (categorie UPOS): le frasi, in blocchi consecutivi di circa `blocco` parole; i blocchi, mescolati, si
    mettono in fila fino ad avere n_parole parole; poi pagine di 23 righe da 8 parole. Minuscolo, senza i trattini di unione."""
    frasi, cur = [], []
    for l in open(UD_LATINO, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l:
            if cur:
                frasi.append(cur)
                cur = []
            continue
        if l.startswith('#'):
            continue
        c = l.split('\t')
        if '-' in c[0] or '.' in c[0]:
            continue
        if c[3] == 'PUNCT':
            continue
        cur.append((c[1].lower(), c[3]))
    if cur:
        frasi.append(cur)
    blocchi, b, n = [], [], 0
    for f in frasi:
        b.extend(f)
        n += len(f)
        if n >= blocco:
            blocchi.append(b)
            b, n = [], 0
    random.Random(seme).shuffle(blocchi)
    parole, cat = [], []
    for b in blocchi:
        if len(parole) >= n_parole:
            break
        for w, t in b:
            parole.append(tuple(w))
            cat.append(t)
    parole, cat = parole[:n_parole], cat[:n_parole]
    pagine, et = righe_a_pagine(parole, cat, prefisso='U')
    return Testo('latino_ud', pagine, etichette=et, descrizione='UD Latin-PROIEL, %d parole, categorie UPOS' % len(parole))


# ---------------------------------------------------------------- sintetici con grammatica nota

ALFABETO = list('abcdefghijkl')


def _dirichlet(rnd, n, alfa):
    x = [rnd.gammavariate(alfa, 1.0) for _ in range(n)]
    s = sum(x)
    return [v / s for v in x]


def _stazionaria(P, giri=200):
    n = len(P)
    pi = [1.0 / n] * n
    for _ in range(giri):
        pi = [sum(pi[i] * P[i][j] for i in range(n)) for j in range(n)]
    return pi


def sintetico(tipo, seme=2024, K0=8, per_classe=400, mescolanza=0.08, alfa=0.25):
    """Testo sintetico con K0 classi vere e una catena di Markov fra classi (righe di Dirichlet(alfa), mescolate con una
    quota `mescolanza` di scelta a caso). Le parole di una classe seguono Zipf (1/rango). Tre tipi:
      'forma'   : la classe dipende dalla forma (ogni classe ha 3 finali di 2 segni suoi) e dall'ordine;
      'noforma' : la classe dipende solo dall'ordine: parole = stringhe a caso, senza legame fra forma e classe;
      'caso'    : stesso lessico di 'forma' ma le classi si susseguono a caso (niente grammatica, solo forma).
    Costruito da zero: non usa nessun testo vero."""
    rnd = random.Random(seme)
    T = [[(1 - mescolanza) * p + mescolanza / K0 for p in _dirichlet(rnd, K0, alfa)] for _ in range(K0)]
    pi = _stazionaria(T)
    finali = {}
    tutti = [(a, b) for a in ALFABETO for b in ALFABETO]
    rnd.shuffle(tutti)
    for c in range(K0):
        finali[c] = tutti[3 * c:3 * c + 3]
    visti = set()
    lessico = []
    for c in range(K0):
        parole = []
        while len(parole) < per_classe:
            if tipo == 'noforma':
                w = tuple(rnd.choice(ALFABETO) for _ in range(rnd.randint(2, 6)))
            else:
                stelo = tuple(rnd.choice(ALFABETO) for _ in range(rnd.randint(1, 4)))
                w = stelo + rnd.choice(finali[c])
            if w in visti:
                continue
            visti.add(w)
            parole.append(w)
        lessico.append(parole)
    zipf = [1.0 / (i + 1) for i in range(per_classe)]
    cum = []
    t = 0.0
    for x in zipf:
        t += x
        cum.append(t)
    n = PAGINE_POS * RIGHE_POS
    parole, cat = [], []
    for _ in range(n):
        c = rnd.choices(range(K0), weights=pi)[0]
        for j in range(PAROLE_RIGA_POS):
            if j:
                c = rnd.choices(range(K0), weights=pi)[0] if tipo == 'caso' else rnd.choices(range(K0), weights=T[c])[0]
            parole.append(rnd.choices(lessico[c], cum_weights=cum)[0])
            cat.append('C%d' % c)
    pagine, et = righe_a_pagine(parole, cat, prefisso='S')
    return Testo('sint_' + tipo, pagine, etichette=et,
                 descrizione='sintetico %s: %d classi vere, %d parole per classe, catena di Markov di Dirichlet(%.2f)' % (tipo, K0, per_classe, alfa))


# ---------------------------------------------------------------- Timm e Schinner, Naibbe (generatori pubblicati)

def _da_blocchi(blocchi, prefisso):
    """Blocchi di righe (come in e3c95_imparabilita) -> pagine; solo quelle con almeno 40 parole."""
    out = OrderedDict()
    for i, b in enumerate(blocchi):
        rows = [(False, [tuple(w) for w in r]) for r in b if r]
        if sum(len(ws) for _, ws in rows) >= 40:
            out['%s%03d' % (prefisso, i)] = rows
    return out
