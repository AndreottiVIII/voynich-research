# -*- coding: utf-8 -*-
"""Procedimenti di cifratura e di generazione di testo per ia14 (modulo di supporto, non e' un esperimento).

Contiene sette "procedimenti" (famiglie di cifrari e di generatori), ciascuno con un solo parametro che si fa variare su
una griglia di tre valori fissata prima, e le funzioni per mettere un testo qualsiasi nell'impaginazione del Voynich
(solo come lunghezze: parole per riga, righe per pagina, paragrafi).

REGOLA: questo modulo non legge il Voynich, non importa i suoi caricatori e non usa nessuna statistica del Voynich. Del
Voynich usa, dichiarate, solo tre cose, tutte generiche:
  1. l'inventario dei 20 segni (glifi EVA fusi) con cui si scrivono le parole cifrate (ALFABETO): i nomi dei segni, non le
     loro frequenze (le frequenze si tirano a caso per ogni istanza, vedi Segni);
  2. la lunghezza media di una parola, circa 5 segni, per scegliere le lunghezze delle stringhe delle tavole (conoscenza
     generale del manoscritto, non un numero misurato qui);
  3. l'impaginazione (parole per riga, righe per pagina), che il chiamante passa come `layout`.
Niente di tutto cio' e' tarato guardando l'esito delle misure.

Una parola cifrata e' una tupla di segni (stringhe); una pagina e' una lista di righe (inizio_paragrafo, [parola, ...]), come
in ia01/ia09/ia10.

Procedimenti (codice: parametro e valori della griglia):
  V  cifrario verboso omofonico a bigrammi (famiglia del cifrario Naibbe; qui con tavole casuali mie, perche' le tavole
     originali non sono nei dati locali): T = numero di tavole alternative, 1 / 3 / 6.
  S  sillabario con omofoni: h = numero di stringhe diverse per la stessa sillaba, 1 / 2 / 4.
  N  nomenclatore (libro dei codici per le parole piu' frequenti, il resto lettera per lettera): n = parole nel libro,
     30 / 150 / 600.
  C  generatore ad auto-citazione (famiglia di Timm e Schinner, mia versione senza testo e senza dati del Voynich):
     W = finestra, in parole, da cui si copia, 4 / 16 / 64.
  R  tabella a griglia (famiglia di Rugg: tre tabelle prefisso / radice / suffisso lette con una griglia che scorre):
     M = lato delle tre tabelle quadrate, 6 / 12 / 24.
  F  sostituzione semplice con spazi riscritti (le parole del testo in chiaro si perdono): L = lunghezza media di una
     parola cifrata, 3,5 / 5 / 7 segni.
  P  polialfabetico a cambio periodico (disco di Alberti / Vigenere): m = ogni quante lettere cambia l'alfabeto, 1 / 5 / 25.
"""
import math
import os
import random
import unicodedata
import zipfile
import zlib
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
GB_ZIP = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data', 'meaningful.zip')

# i 20 segni con cui si scrivono le parole cifrate (inventario, non frequenze)
ALFABETO = ('a', 'o', 'e', 'y', 'i', 'd', 'l', 'r', 's', 'n', 'k', 't', 'p', 'f', 'q', 'm', 'ch', 'sh', 'cth', 'ckh')
# le 20 lettere del testo in chiaro dopo la normalizzazione (stessa idea di Naibbe: j->i, k->c, w->uu, v->u; qui anche y->i, z->s)
LETTERE = tuple('abcdefghilmnopqrstux')
GRIGLIA_ESPONENTE = 0.7           # esponente della legge di Zipf per i pesi dei segni (pesi tirati a caso fra i segni, per istanza)

CHIAVI_CHIARO = OrderedDict([
    ('latino', "Historical - Latin - Technical - Pliny's Natural History.txt"),
    ('italiano', 'Historical - Italian - Literary - NT - Diodati.txt'),
    ('tedesco', 'Historical - German - Technical - German Herbarium.txt'),
])

# i sette procedimenti: codice -> (nome, parametro, valori, testo in chiaro)
PROCEDIMENTI = OrderedDict([
    ('V', dict(nome='verboso omofonico a bigrammi', par='T', valori=(1, 3, 6), chiaro='latino')),
    ('S', dict(nome='sillabario con omofoni', par='h', valori=(1, 2, 4), chiaro='italiano')),
    ('N', dict(nome='nomenclatore', par='n', valori=(30, 150, 600), chiaro='latino')),
    ('C', dict(nome='auto-citazione', par='W', valori=(4, 16, 64), chiaro=None)),
    ('R', dict(nome='tabella a griglia', par='M', valori=(6, 12, 24), chiaro=None)),
    ('F', dict(nome='sostituzione con spazi riscritti', par='L', valori=(3.5, 5.0, 7.0), chiaro='latino')),
    ('P', dict(nome='polialfabetico a cambio periodico', par='m', valori=(1, 5, 25), chiaro='latino')),
])
# prove di sensibilita' al testo in chiaro: stesso procedimento V, valore centrale, altra lingua
VARIANTI_CHIARO = (('V', 3, 'italiano'), ('V', 3, 'tedesco'))
PESI_TAVOLE = (20, 8, 8, 8, 4, 4)       # pesi delle tavole del verboso (come le carte del cifrario Naibbe, dal suo codice pubblico)
Q_BIGRAMMA = 19 / 36                    # quota di gruppi di due lettere nel verboso (17/36 di un'lettera sola, come Naibbe)


# ---------------------------------------------------------------- testi in chiaro

def normalizza(pezzo):
    """Una parola del testo in chiaro -> stringa sulle 20 LETTERE (minuscole, senza segni combinanti)."""
    s = unicodedata.normalize('NFD', pezzo)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    for a, b in (('æ', 'ae'), ('œ', 'oe'), ('ß', 'ss'), ('ð', 'd'), ('þ', 'th'), ('ł', 'l'), ('ø', 'o'),
                 ('w', 'uu'), ('j', 'i'), ('k', 'c'), ('v', 'u'), ('y', 'i'), ('z', 's')):
        s = s.replace(a, b)
    return ''.join(c for c in s if c in LETTERE)


def parola_lingua(pezzo):
    """Segni di una parola intera: lettera + segni combinanti (copiata da e381_parole_intere.parola, per non importarne la catena)."""
    segni = []
    for c in pezzo.lower():
        cat = unicodedata.category(c)
        if cat[0] == 'L':
            segni.append(c)
        elif cat[0] == 'M' and segni:
            segni[-1] += c
        elif c in ("'", '’') and segni:
            segni.append(c)
    return tuple(segni)


_CACHE = {}


def _testo(chiave):
    if chiave not in _CACHE:
        with zipfile.ZipFile(GB_ZIP) as z:
            _CACHE[chiave] = z.read('texts/' + chiave).decode('utf-8', errors='ignore')
    return _CACHE[chiave]


def parole_chiaro(lingua):
    """Parole normalizzate del testo in chiaro (latino, italiano, tedesco), nell'ordine del testo."""
    k = ('chiaro', lingua)
    if k not in _CACHE:
        _CACHE[k] = [w for w in (normalizza(p) for p in _testo(CHIAVI_CHIARO[lingua]).split()) if w]
    return _CACHE[k]


def parole_lingua(chiave):
    """Parole (tuple di segni) di un testo di Gaskell e Bowern, nell'ordine del testo."""
    k = ('lingua', chiave)
    if k not in _CACHE:
        _CACHE[k] = [w for w in (parola_lingua(p) for p in _testo(chiave).split()) if w]
    return _CACHE[k]


def lettere_da(parole, inizio, n):
    """Flusso di almeno n lettere dal testo in chiaro, da `inizio`; ricomincia dall'inizio se finisce (si conta il giro)."""
    out, giri, i, tot = [], 0, inizio, 0
    while tot < n:
        if i >= len(parole):
            i, giri = 0, giri + 1
        out.append(parole[i])
        tot += len(parole[i])
        i += 1
    return ''.join(out), giri


# ---------------------------------------------------------------- impaginazione

def layout_da_pagine(pagine):
    """[(nome pagina, [(inizio_paragrafo, numero di parole), ...]), ...]: solo le lunghezze di un testo gia' in pagine."""
    return [(p, [(bool(ini), len(ws)) for ini, ws in rows]) for p, rows in pagine.items()]


def parole_per_pagina(layout):
    return [sum(n for _, n in rows) for _, rows in layout]


def impagina(layout, parole):
    """Mette le parole, in ordine, nell'impaginazione. Si ferma con un errore se non bastano."""
    out, k = OrderedDict(), 0
    for p, rows in layout:
        nr = []
        for ini, n in rows:
            nr.append((ini, list(parole[k:k + n])))
            k += n
        out[p] = nr
    if k > len(parole):
        raise ValueError('parole insufficienti: servono %d, ce ne sono %d' % (k, len(parole)))
    return out


def rimescola_tutto(pagine, seme):
    """Tutte le parole mescolate fra tutte le pagine (stessa impaginazione): controllo negativo."""
    rnd = random.Random(seme)
    tutte = [w for rows in pagine.values() for _, ws in rows for w in ws]
    rnd.shuffle(tutte)
    out, k = OrderedDict(), 0
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            nr.append((ini, tutte[k:k + len(ws)]))
            k += len(ws)
        out[p] = nr
    return out


# ---------------------------------------------------------------- segni e stringhe

class Segni:
    """Estrae stringhe di segni con pesi di Zipf tirati a caso fra i segni (per istanza): nessuna frequenza del Voynich."""

    def __init__(self, rnd):
        self.rnd = rnd
        ordine = list(range(len(ALFABETO)))
        rnd.shuffle(ordine)
        w = [0.0] * len(ALFABETO)
        for r, i in enumerate(ordine):
            w[i] = 1.0 / (r + 1) ** GRIGLIA_ESPONENTE
        self.pesi = w

    def uno(self):
        return self.rnd.choices(ALFABETO, weights=self.pesi, k=1)[0]

    def stringa(self, n):
        return tuple(self.rnd.choices(ALFABETO, weights=self.pesi, k=n))

    def nuova(self, usate, lunghezze):
        """Stringa non ancora usata; lunghezze = [(lunghezza, probabilita'), ...]. Se dopo molti tentativi non c'e' posto, si allunga."""
        ls, ps = zip(*lunghezze)
        extra = 0
        for t in range(1, 10 ** 6):
            s = self.stringa(self.rnd.choices(ls, weights=ps, k=1)[0] + extra)
            if s not in usate:
                usate.add(s)
                return s
            if t % 40 == 0:
                extra += 1
        raise RuntimeError('nessuna stringa libera')


def parole_da_flusso(rnd, segni_flusso, n_parole, lung_media, lung_max=16):
    """Taglia un flusso di segni in n_parole parole; lunghezza = 1 + binomiale(15, p) con media lung_media (da 1 a 16 segni): i
    confini di parola non hanno niente a che fare con il testo in chiaro."""
    p = (lung_media - 1.0) / (lung_max - 1)
    out, i = [], 0
    for _ in range(n_parole):
        k = 1 + sum(1 for _ in range(lung_max - 1) if rnd.random() < p)
        if i + k > len(segni_flusso):
            raise ValueError('flusso di segni troppo corto')
        out.append(tuple(segni_flusso[i:i + k]))
        i += k
    return out, i


# ---------------------------------------------------------------- V: verboso omofonico a bigrammi

def tavole_verboso(sg, T):
    """T tavole; per ognuna, per ogni lettera, una stringa per 'unigramma' (lettera sola), 'prefisso' e 'suffisso' (lettera in un
    gruppo di due). Stringhe tutte diverse fra loro dentro lo stesso stato; un gruppo di due non coincide mai con una lettera sola."""
    usate_u, usate_p, usate_s = set(), set(), set()
    tav = []
    for _ in range(T):
        uni = {l: sg.nuova(usate_u, [(3, 0.4), (4, 0.4), (5, 0.2)]) for l in LETTERE}
        pre = {l: sg.nuova(usate_p, [(2, 1.0)]) for l in LETTERE}
        suf = {l: sg.nuova(usate_s, [(1, 0.4), (2, 0.4), (3, 0.2)]) for l in LETTERE}
        tav.append((uni, pre, suf))
    return tav, usate_u


def genera_verboso(rnd, n_parole, T, lettere):
    """Una parola cifrata per ogni gruppo di una o due lettere; tavola scelta a caso con i pesi PESI_TAVOLE[:T]. `lettere` e' il
    flusso in chiaro (stringa). Restituisce (parole, lettere usate, tavole)."""
    sg = Segni(rnd)
    tav, uni_set = tavole_verboso(sg, T)
    pesi = PESI_TAVOLE[:T]
    out, i, L = [], 0, len(lettere)
    while len(out) < n_parole:
        due = rnd.random() < Q_BIGRAMMA
        if not due:
            u, _, _ = tav[rnd.choices(range(T), weights=pesi, k=1)[0]]
            out.append(u[lettere[i % L]])
            i += 1
        else:
            while True:
                _, p, _ = tav[rnd.choices(range(T), weights=pesi, k=1)[0]]
                _, _, s = tav[rnd.choices(range(T), weights=pesi, k=1)[0]]
                w = p[lettere[i % L]] + s[lettere[(i + 1) % L]]
                if w not in uni_set:
                    break
            out.append(w)
            i += 2
    return out, i, tav


def decifra_verboso(parole, tav):
    """Inversione del verboso (prova che e' un cifrario vero): parola cifrata -> una o due lettere."""
    um, pm, sm = {}, {}, {}
    for uni, pre, suf in tav:
        um.update({v: l for l, v in uni.items()})
        pm.update({v: l for l, v in pre.items()})
        sm.update({v: l for l, v in suf.items()})
    out = []
    for w in parole:
        if w in um:
            out.append(um[w])
            continue
        for k in range(1, len(w)):
            if w[:k] in pm and w[k:] in sm:
                out.append(pm[w[:k]] + sm[w[k:]])
                break
        else:
            raise ValueError('parola non decifrabile')
    return ''.join(out)


# ---------------------------------------------------------------- S: sillabario con omofoni

VOCALI = set('aeiou')
NESSI = {'pr', 'br', 'tr', 'dr', 'cr', 'gr', 'fr', 'pl', 'bl', 'cl', 'gl', 'fl', 'qu'}


def sillabe(w):
    """Divisione in sillabe, a regole semplici (ogni vocale e' un nucleo; una consonante va con la vocale dopo; fra due consonanti
    si taglia in mezzo, salvo i nessi consonante + l/r). Non e' linguistica fine: serve solo a dare un sillabario."""
    idx = [i for i, c in enumerate(w) if c in VOCALI]
    if len(idx) < 2:
        return [w]
    tagli = []
    for a, b in zip(idx, idx[1:]):
        c = b - a - 1
        if c == 0:
            tagli.append(b)
        elif c == 1:
            tagli.append(a + 1)
        else:
            tagli.append(b - 2 if w[b - 2:b] in NESSI else b - 1)
    parti, s = [], 0
    for t in tagli:
        parti.append(w[s:t])
        s = t
    parti.append(w[s:])
    return parti


def genera_sillabario(rnd, n_parole, h, parole):
    """Ogni parola in chiaro -> una parola cifrata, fatta incollando, senza separatori, una stringa per sillaba; ogni sillaba ha h
    stringhe (omofoni) fra cui si sceglie a caso a ogni occorrenza. Le stringhe si assegnano alla prima volta che si vede la sillaba."""
    sg = Segni(rnd)
    usate = set()
    tabella = {}
    out = []
    for w in parole[:n_parole]:
        cifrata = ()
        for s in sillabe(w):
            if s not in tabella:
                tabella[s] = [sg.nuova(usate, [(2, 0.35), (3, 0.65)]) for _ in range(h)]
            cifrata += rnd.choice(tabella[s])
        out.append(cifrata)
    return out, len(tabella)


# ---------------------------------------------------------------- N: nomenclatore

def tavola_lettere(sg, freq):
    """Lettera -> stringa di 1 o 2 segni, senza prefissi in comune (si puo' decifrare): le 14 lettere piu' frequenti del testo hanno un
    segno solo, le altre due segni che cominciano con uno dei 6 segni non usati dalle prime."""
    ordine = sorted(LETTERE, key=lambda l: (-freq.get(l, 0), l))
    segni = list(ALFABETO)
    sg.rnd.shuffle(segni)
    tab = {l: (s,) for l, s in zip(ordine[:14], segni[:14])}
    liberi, usate = segni[14:], set()
    for l in ordine[14:]:
        while True:
            s = (sg.rnd.choice(liberi), sg.uno())
            if s not in usate:
                usate.add(s)
                tab[l] = s
                break
    return tab


def genera_nomenclatore(rnd, n_parole, n_libro, parole):
    """Le n_libro parole piu' frequenti del testo in chiaro hanno una parola-codice (stringa di 2-4 segni); le altre si scrivono
    lettera per lettera con la tavola. Una parola in chiaro -> una parola cifrata (i confini di parola restano)."""
    sg = Segni(rnd)
    testo = parole[:n_parole]
    cont = Counter(testo)
    libro = [w for w, _ in sorted(cont.items(), key=lambda x: (-x[1], x[0]))[:n_libro]]
    usate = set()
    codice = {w: sg.nuova(usate, [(2, 0.3), (3, 0.5), (4, 0.2)]) for w in libro}
    freq = Counter(c for w in testo for c in w)
    tab = tavola_lettere(sg, freq)
    out = []
    for w in testo:
        out.append(codice[w] if w in codice else tuple(x for c in w for x in tab[c]))
    return out, dict(libro=len(libro), copertura=sum(cont[w] for w in libro) / max(len(testo), 1))


# ---------------------------------------------------------------- C: auto-citazione

def modifica(sg, w):
    """Copia di una parola con una piccola modifica: uguale 20%, un segno cambiato 40%, uno in piu' 20%, uno in meno 20%."""
    r = sg.rnd.random()
    w = list(w)
    if r < 0.2:
        return tuple(w)
    if r < 0.6 or (r >= 0.8 and len(w) == 1):
        w[sg.rnd.randrange(len(w))] = sg.uno()
    elif r < 0.8 and len(w) < 12:
        w.insert(sg.rnd.randrange(len(w) + 1), sg.uno())
    elif len(w) > 1:
        del w[sg.rnd.randrange(len(w))]
    return tuple(w)


def genera_autocitazione(rnd, n_per_pagina, W, nu=0.05):
    """Per ogni pagina: la prima parola e' nuova (da 3 a 7 segni); poi con probabilita' nu una parola nuova, altrimenti la copia
    (con una piccola modifica) di una delle ultime W parole della stessa pagina, scelta a caso. Nessun testo in chiaro."""
    sg = Segni(rnd)
    out = []
    for n in n_per_pagina:
        pag = []
        for _ in range(n):
            if not pag or rnd.random() < nu:
                pag.append(sg.stringa(rnd.randint(3, 7)))
            else:
                fin = pag[-W:]
                pag.append(modifica(sg, fin[rnd.randrange(len(fin))]))
        out.extend(pag)
    return out


# ---------------------------------------------------------------- R: tabella a griglia

def genera_griglia(rnd, n_per_pagina, M):
    """Tre tabelle M x M di frammenti (prefissi di 1-2 segni, radici di 1-3, suffissi di 1-2). Una parola = prefisso + radice +
    suffisso letti in tre punti della stessa 'griglia' (la posizione nella radice e nel suffisso e' spostata di un valore fisso). La
    griglia fa un passo a caso (-1, 0, +1 per riga e per colonna, 25% / 50% / 25%) a ogni parola; a ogni pagina riparte da un punto a caso."""
    sg = Segni(rnd)

    def tab(lunghezze):
        ls, ps = zip(*lunghezze)
        return [[sg.stringa(rnd.choices(ls, weights=ps, k=1)[0]) for _ in range(M)] for _ in range(M)]
    PRE = tab([(1, 0.6), (2, 0.4)])
    MED = tab([(1, 0.3), (2, 0.5), (3, 0.2)])
    SUF = tab([(1, 0.5), (2, 0.5)])
    a, b, c, d = (rnd.randrange(M) for _ in range(4))
    out = []
    for n in n_per_pagina:
        i, j = rnd.randrange(M), rnd.randrange(M)
        for _ in range(n):
            out.append(PRE[i][j] + MED[(i + a) % M][(j + b) % M] + SUF[(i + c) % M][(j + d) % M])
            i = (i + rnd.choices((-1, 0, 1), weights=(1, 2, 1), k=1)[0]) % M
            j = (j + rnd.choices((-1, 0, 1), weights=(1, 2, 1), k=1)[0]) % M
    return out


# ---------------------------------------------------------------- F: sostituzione semplice con spazi riscritti

def segni_necessari(n_parole, lung_media):
    """Segni di flusso che bastano per n_parole parole (media + sei errori standard della somma, con margine)."""
    return int(n_parole * lung_media + 6 * math.sqrt(n_parole) * 2.5) + 200


def genera_sostituzione(rnd, n_parole, lung_media, lettere):
    """Sostituzione semplice (lettera -> 1 o 2 segni, decifrabile); il flusso di segni cifrati si taglia in parole di lunghezza a
    caso, senza rapporto con le parole in chiaro."""
    sg = Segni(rnd)
    tab = tavola_lettere(sg, Counter(lettere))
    need = segni_necessari(n_parole, lung_media)
    flusso, i = [], 0
    while len(flusso) < need:
        flusso.extend(tab[lettere[i % len(lettere)]])
        i += 1
    parole, usati = parole_da_flusso(rnd, flusso, n_parole, lung_media)
    return parole, tab, flusso[:usati]


def decifra_sostituzione(flusso, tab):
    """Inversione della sostituzione (stringhe senza prefissi in comune): flusso di segni -> lettere."""
    inv = {v: l for l, v in tab.items()}
    out, i = [], 0
    while i < len(flusso):
        if (flusso[i],) in inv:
            out.append(inv[(flusso[i],)])
            i += 1
        else:
            out.append(inv[tuple(flusso[i:i + 2])])
            i += 2
    return ''.join(out)


# ---------------------------------------------------------------- P: polialfabetico a cambio periodico

def genera_polialfabetico(rnd, n_parole, m, lettere, lung_media=5.0, periodo=7):
    """Ogni lettera -> un segno (20 lettere, 20 segni); l'alfabeto cambia ogni m lettere seguendo una chiave di `periodo` spostamenti
    (m = 1: Vigenere di periodo 7; m = 25: un alfabeto per volta, a disco di Alberti). Il flusso cifrato si taglia in parole di
    lunghezza a caso."""
    base = list(range(len(LETTERE)))
    rnd.shuffle(base)
    chiave = [rnd.randrange(1, len(LETTERE)) for _ in range(periodo)]
    pos = {l: k for k, l in enumerate(LETTERE)}
    need = segni_necessari(n_parole, lung_media)
    flusso = []
    for k in range(need):
        sh = chiave[(k // m) % periodo]
        flusso.append(ALFABETO[base[(pos[lettere[k % len(lettere)]] + sh) % len(LETTERE)]])
    parole, usati = parole_da_flusso(rnd, flusso, n_parole, lung_media)
    return parole, dict(base=base, chiave=chiave, m=m), flusso[:usati]


def decifra_polialfabetico(flusso, info, inizio=0):
    """Inversione del polialfabetico (prova che e' un cifrario vero): segni -> lettere."""
    base, chiave, m = info['base'], info['chiave'], info['m']
    pos_di_base = {b: k for k, b in enumerate(base)}
    out = []
    for k, s in enumerate(flusso):
        sh = chiave[(k // m) % len(chiave)]
        out.append(LETTERE[(pos_di_base[ALFABETO.index(s)] - sh) % len(LETTERE)])
    return ''.join(out)


# ---------------------------------------------------------------- tutto insieme

def seme_di(*parti):
    return zlib.crc32('|'.join(str(p) for p in ('ia14',) + parti).encode('utf-8')) % (1 << 31)


def genera(codice, valore, istanza, layout, chiaro=None):
    """Il testo di un procedimento (codice), con il valore del suo parametro, per l'istanza `istanza` (1, 2, 3...), nell'impaginazione
    `layout`. `chiaro` e' la lingua del testo in chiaro (per i procedimenti che ne hanno uno; di norma quella di PROCEDIMENTI).
    Restituisce (pagine, meta) con meta di soli numeri."""
    p = PROCEDIMENTI[codice]
    chiaro = chiaro or p['chiaro']
    rnd = random.Random(seme_di(codice, valore, chiaro, istanza))
    npag = parole_per_pagina(layout)
    N = sum(npag)
    meta = dict(codice=codice, valore=valore, istanza=istanza, chiaro=chiaro, parole=N)
    if chiaro:
        pc = parole_chiaro(chiaro)
        inizio = rnd.randrange(0, max(1, len(pc) - 3 * N // 2))
    if codice == 'V':
        # lettere necessarie: al piu' 2 per parola cifrata
        lettere, giri = lettere_da(pc, inizio, int(1.62 * N) + 50)
        parole, usate, _ = genera_verboso(rnd, N, int(valore), lettere)
        meta.update(lettere_usate=usate, giri_testo=giri, lettere_per_parola=usate / N)
    elif codice == 'S':
        sub = pc[inizio:inizio + N]
        giri = 0
        while len(sub) < N:
            sub = sub + pc[:N - len(sub)]
            giri += 1
        parole, nsill = genera_sillabario(rnd, N, int(valore), sub)
        meta.update(sillabe_distinte=nsill, giri_testo=giri)
    elif codice == 'N':
        sub = pc[inizio:inizio + N]
        giri = 0
        while len(sub) < N:
            sub = sub + pc[:N - len(sub)]
            giri += 1
        parole, info = genera_nomenclatore(rnd, N, int(valore), sub)
        meta.update(info, giri_testo=giri)
    elif codice == 'C':
        parole = genera_autocitazione(rnd, npag, int(valore))
    elif codice == 'R':
        parole = genera_griglia(rnd, npag, int(valore))
    elif codice == 'F':
        lettere, giri = lettere_da(pc, inizio, segni_necessari(N, float(valore)))
        parole, _, _ = genera_sostituzione(rnd, N, float(valore), lettere)
        meta.update(giri_testo=giri)
    elif codice == 'P':
        lettere, giri = lettere_da(pc, inizio, segni_necessari(N, 5.0))
        parole, _, _ = genera_polialfabetico(rnd, N, int(valore), lettere)
        meta.update(giri_testo=giri)
    else:
        raise ValueError(codice)
    return impagina(layout, parole), meta


def nome_istanza(codice, valore, istanza, chiaro=None):
    """Nome del testo: solo lettere, cifre e trattino basso (serve anche come nome di file)."""
    base = '%s_%s' % (codice, str(valore).replace('.', 'p'))
    if chiaro and chiaro != PROCEDIMENTI[codice]['chiaro']:
        base += '_' + chiaro
    return '%s_i%d' % (base, istanza)


def testo_lingua_in_layout(chiave, layout, seme):
    """Un testo naturale (una lingua di Gaskell e Bowern) messo nell'impaginazione del Voynich: parole consecutive da un punto a caso."""
    pw = parole_lingua(chiave)
    N = sum(parole_per_pagina(layout))
    rnd = random.Random(seme_di('lingua', chiave, seme))
    inizio = rnd.randrange(0, max(1, len(pw) - N))
    sub = pw[inizio:inizio + N]
    if len(sub) < N:
        raise ValueError('testo troppo corto: %s (%d parole, servono %d)' % (chiave, len(pw), N))
    return impagina(layout, sub)
