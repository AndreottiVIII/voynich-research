# -*- coding: utf-8 -*-
"""Procedimenti COMBINATI per ia19 (modulo di supporto, non e' un esperimento).

Mette insieme "ingredienti" dei sette procedimenti semplici di ia14 (`cifrari_procedimenti.py`, che qui si importa senza
modificarlo): il verboso omofonico a bigrammi (V), il nomenclatore (N), l'eco di pagina dell'auto-citazione (C, qui leggera),
piu' due ingredienti nuovi (alfabeto ridotto, regole di bordo riga). Ogni combinazione ha un solo parametro con tre valori
fissati prima di qualsiasi misura (nessuna taratura sul Voynich).

REGOLA (come in ia14): questo modulo non legge il Voynich, non importa i suoi caricatori e non usa nessuna statistica del
Voynich oltre a quelle che gia' usa ia14: i nomi dei 20 segni, la lunghezza media di una parola (circa 5 segni), l'impaginazione
passata dal chiamante come lunghezze (`layout`). Il testo in chiaro e' il latino di Plinio (Gaskell e Bowern).

Combinazioni (codice: parametro, valori):
  VE  verboso (T = 3 tavole) + eco leggera di pagina: p = probabilita' che una parola sia un'"eco" (0,02 / 0,05 / 0,10).
      Le parole d'eco sono NULLE (non portano lettere): meta' riprese dal tema della pagina (10 parole scelte a caso fra le
      parole cifrate di quella pagina), meta' varianti a una modifica di una parola della riga corrente o di quella sopra.
  VA  verboso (T = 3) con alfabeto ridotto: A = segni usati per scrivere le parole (8 / 12 / 16 invece di 20).
  NV  nomenclatore + verboso (T = 3): n = parole nel libro dei codici (30 / 150 / 600); le parole fuori libro non si scrivono
      lettera per lettera ma a gruppi di una o due lettere con le tavole del verboso.
  VB  verboso (T = 3) con regole di bordo riga: b = probabilita' che la prima e l'ultima parola di una riga siano scritte con
      due tavole speciali, una solo per gli inizi di riga e una solo per le fini (0,5 / 0,8 / 1,0).
  VT  tutto insieme, a gradini: k = numero di ingredienti (2: alfabeto A = 12 + eco p = 0,05; 3: + bordo b = 0,8;
      4: + nomenclatore n = 150). I valori sono i centrali delle griglie sopra, non scelti guardando misure.
Prova di sensibilita': VE con p = 0,05 e T = 6 tavole (accoppiata al V_6 di ia14).
"""
import itertools
import random
import zlib
from collections import Counter, OrderedDict

import cifrari_procedimenti as CP

ALFABETO = CP.ALFABETO
LETTERE = CP.LETTERE
FATTORE_PREFISSI = 3.0      # il prefisso del verboso e' lungo il minimo lp con A^lp >= 3 * 20 lettere * tavole (cosi' resta libero almeno 2/3)
K_TEMA = 10                 # parole del tema di pagina
Q_TEMA = 0.5                # fra le parole d'eco: meta' tema di pagina, meta' variante locale

COMBINATI = OrderedDict([
    ('VE', dict(nome='verboso + eco leggera di pagina', par='p', valori=(0.02, 0.05, 0.10), chiaro='latino')),
    ('VA', dict(nome='verboso con alfabeto ridotto', par='A', valori=(8, 12, 16), chiaro='latino')),
    ('NV', dict(nome='nomenclatore + verboso', par='n', valori=(30, 150, 600), chiaro='latino')),
    ('VB', dict(nome='verboso con regole di bordo riga', par='b', valori=(0.5, 0.8, 1.0), chiaro='latino')),
    ('VT', dict(nome='tutto insieme (ingredienti a gradini)', par='k', valori=(2, 3, 4), chiaro='latino')),
])
VARIANTI = (('VE', 0.05, 'T6'),)       # prove di sensibilita': (codice, valore, variante)


def configurazione(cod, valore, variante=None):
    """Gli ingredienti di una cella: T tavole, A segni, b bordo, n parole nel libro (0 = niente nomenclatore), p eco."""
    c = dict(T=3, A=20, b=0.0, n=0, p=0.0)
    if cod == 'VE':
        c['p'] = float(valore)
    elif cod == 'VA':
        c['A'] = int(valore)
    elif cod == 'NV':
        c['n'] = int(valore)
    elif cod == 'VB':
        c['b'] = float(valore)
    elif cod == 'VT':
        k = int(valore)
        c.update(A=12, p=0.05)
        if k >= 3:
            c['b'] = 0.8
        if k >= 4:
            c['n'] = 150
    else:
        raise ValueError(cod)
    if variante == 'T6':
        c['T'] = 6
    elif variante:
        raise ValueError(variante)
    return c


def nome_cella(cod, valore, variante=None):
    base = '%s_%s' % (cod, str(valore).replace('.', 'p'))
    return base + ('_' + variante if variante else '')


def nome_istanza(cod, valore, istanza, variante=None):
    """Nome del testo: solo lettere, cifre e trattino basso (serve anche come nome di file)."""
    return '%s_i%d' % (nome_cella(cod, valore, variante), istanza)


def seme19(*parti):
    return zlib.crc32('|'.join(str(p) for p in ('ia19',) + parti).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- segni

class SegniRidotti(CP.Segni):
    """Come Segni (stessi pesi di Zipf tirati a caso), ma solo i primi A segni per peso restano in uso. Con A = 20 e' identico a Segni."""

    def __init__(self, rnd, A):
        super().__init__(rnd)
        rango = sorted(range(len(self.pesi)), key=lambda i: -self.pesi[i])
        for i in rango[A:]:
            self.pesi[i] = 0.0


class SegniDaTesto:
    """Segni per le varianti dell'eco: estratti con le frequenze dei segni del testo cifrato di base (nessuna statistica esterna)."""

    def __init__(self, rnd, parole):
        self.rnd = rnd
        c = Counter(s for w in parole for s in w)
        self.segni = sorted(c)
        self.pesi = [c[s] for s in self.segni]

    def uno(self):
        return self.rnd.choices(self.segni, weights=self.pesi, k=1)[0]

    def stringa(self, n):
        return tuple(self.rnd.choices(self.segni, weights=self.pesi, k=n))


# ---------------------------------------------------------------- verboso esteso

def lunghezza_prefisso(A, Ttot):
    lp = 2
    while A ** lp < FATTORE_PREFISSI * len(LETTERE) * Ttot:
        lp += 1
    return lp


def stringa_esatta(sg, usate, lp):
    """Stringa di ESATTAMENTE lp segni non ancora usata. Con spazio largo consuma il caso come `Segni.nuova` con [(lp, 1.0)] (cosi' con
    A = 20 il verboso e' identico a quello di ia14); se dopo 40 tentativi non trova posto, sceglie a caso fra quelle libere (non allunga)."""
    for _ in range(40):
        sg.rnd.choices((lp,), weights=(1.0,), k=1)
        s = sg.stringa(lp)
        if s not in usate:
            usate.add(s)
            return s
    attivi = [a for a, w in zip(ALFABETO, sg.pesi) if w > 0]
    liberi = [s for s in itertools.product(attivi, repeat=lp) if s not in usate]
    if not liberi:
        raise RuntimeError('nessun prefisso libero')
    s = sg.rnd.choice(liberi)
    usate.add(s)
    return s


def tavole_x(sg, Ttot, lp):
    """Ttot tavole: per ognuna, per ogni lettera, una stringa 'unigramma' (3-5 segni), un prefisso di lp segni esatti e un suffisso
    (1-3 segni). Prefissi tutti diversi fra tutte le tavole, unigrammi tutti diversi, suffissi tutti diversi: il testo si decifra."""
    usate_u, usate_p, usate_s = set(), set(), set()
    tav = []
    for _ in range(Ttot):
        uni = {l: sg.nuova(usate_u, [(3, 0.4), (4, 0.4), (5, 0.2)]) for l in LETTERE}
        pre = {l: stringa_esatta(sg, usate_p, lp) for l in LETTERE}
        suf = {l: sg.nuova(usate_s, [(1, 0.4), (2, 0.4), (3, 0.2)]) for l in LETTERE}
        tav.append((uni, pre, suf))
    return tav, usate_u


def parole_possibili(tav):
    """Tutte le parole che il verboso puo' scrivere: gli unigrammi e le coppie prefisso + suffisso di qualunque tavola."""
    poss = set()
    for uni, _, _ in tav:
        poss.update(uni.values())
    pres = [v for _, pre, _ in tav for v in pre.values()]
    sufs = [v for _, _, suf in tav for v in suf.values()]
    for p in pres:
        for s in sufs:
            poss.add(p + s)
    return poss


def genera_base(rnd, n_base, attrs, cfg, lettere=None, parole_chiaro=None):
    """Il testo cifrato di base (senza eco): n_base parole. `attrs[i]` e' 'i' (prima parola di una riga), 'f' (ultima) o 'n' (altra)
    per la i-esima parola di base. Con T tavole, A = 20, nessun bordo e nessun libro e' IDENTICO a `CP.genera_verboso` (stesso caso).

    - verboso: `lettere` e' il flusso in chiaro; una parola cifrata per ogni gruppo di una (17/36) o due (19/36) lettere;
    - nomenclatore + verboso (cfg['n'] > 0): `parole_chiaro` sono le parole in chiaro; le n piu' frequenti hanno una parola-codice
      (2-4 segni, mai uguale a una parola possibile del verboso), le altre si scrivono con gruppi di una o due lettere.
    Restituisce (parole, info) con info di soli numeri piu' le tavole e il libro (per la prova di decifrazione)."""
    T, A, b, n_libro = cfg['T'], cfg['A'], cfg['b'], cfg['n']
    Ttot = T + (2 if b > 0 else 0)
    lp = lunghezza_prefisso(A, Ttot)
    sg = SegniRidotti(rnd, A)
    tav, uni_set = tavole_x(sg, Ttot, lp)
    pesi = CP.PESI_TAVOLE[:T]

    def scegli(attr):
        if b > 0 and attr in ('i', 'f') and rnd.random() < b:
            return T if attr == 'i' else T + 1          # tavola di inizio riga / di fine riga
        return rnd.choices(range(T), weights=pesi, k=1)[0]

    def gruppo(due, l1, l2, attr):
        """Una parola cifrata per una (due = False) o due lettere."""
        if not due:
            return tav[scegli(attr)][0][l1]
        t = 0
        while True:
            t += 1
            # dopo 10 collisioni con un'altra parola possibile si torna alle tavole normali (con una tavola di bordo fissa sarebbe un ciclo senza fine)
            ta = scegli(attr) if t <= 10 else rnd.choices(range(T), weights=pesi, k=1)[0]
            tb = ta if ta >= T else rnd.choices(range(T), weights=pesi, k=1)[0]
            w = tav[ta][1][l1] + tav[tb][2][l2]
            if w not in uni_set:
                return w

    out = []
    info = dict(T=T, A=A, lp=lp, tavole_totali=Ttot, tav=tav)
    if n_libro <= 0:
        i, L = 0, len(lettere)
        while len(out) < n_base:
            due = rnd.random() < CP.Q_BIGRAMMA
            attr = attrs[len(out)]
            if not due:
                out.append(gruppo(False, lettere[i % L], None, attr))
                i += 1
            else:
                out.append(gruppo(True, lettere[i % L], lettere[(i + 1) % L], attr))
                i += 2
        info['lettere_usate'] = i
        return out, info
    # nomenclatore + verboso
    cont = Counter(parole_chiaro)
    libro = [w for w, _ in sorted(cont.items(), key=lambda x: (-x[1], x[0]))[:n_libro]]
    usate = set(parole_possibili(tav))
    codice = {w: sg.nuova(usate, [(2, 0.3), (3, 0.5), (4, 0.2)]) for w in libro}
    usate_parole = 0
    for w in parole_chiaro:
        if len(out) >= n_base:
            break
        usate_parole += 1
        if w in codice:
            out.append(codice[w])
            continue
        i = 0
        while i < len(w) and len(out) < n_base:
            due = i + 1 < len(w) and rnd.random() < CP.Q_BIGRAMMA
            attr = attrs[len(out)]
            if due:
                out.append(gruppo(True, w[i], w[i + 1], attr))
                i += 2
            else:
                out.append(gruppo(False, w[i], None, attr))
                i += 1
    if len(out) < n_base:
        raise ValueError('parole in chiaro insufficienti')
    info.update(libro=len(libro), parole_in_chiaro_usate=usate_parole,
                copertura=sum(cont[w] for w in libro) / max(len(parole_chiaro), 1), codice_inv={v: k for k, v in codice.items()},
                libro_insieme=set(libro))
    return out, info


def decifra_base(parole, info):
    """Inversione del testo di base (prova che e' un cifrario vero): lettere in chiaro; le parole del libro sono '[parola]'."""
    out = []
    ci = info.get('codice_inv', {})
    for w in parole:
        if w in ci:
            out.append('[%s]' % ci[w])
        else:
            out.append(CP.decifra_verboso([w], info['tav']))
    return ''.join(out)


# ---------------------------------------------------------------- impaginazione, bordi, eco

def attributi_posizione(layout):
    """Per ogni posizione del testo: 'i' prima parola di riga, 'f' ultima, 'n' altra (riga di una parola sola: 'i')."""
    att = []
    for _, rows in layout:
        for _, n in rows:
            for j in range(n):
                att.append('i' if j == 0 else 'f' if j == n - 1 else 'n')
    return att


def tessi_eco(rnd_eco, base, layout, eco_flag, k_tema=K_TEMA):
    """Mette le parole di base e le parole d'eco nell'impaginazione. Una posizione con eco_flag e' una parola NULLA: meta' ripresa dal
    tema della pagina (k_tema parole distinte scelte a caso fra le parole di base di quella pagina), meta' variante a una modifica di
    una parola della riga corrente (fin qui) o della riga sopra (modifica come in ia14: uguale 20%, un segno cambiato 40%, uno in
    piu' 20%, uno in meno 20%). Restituisce (pagine, tipi) con tipi per posizione: 'b' base, 't' tema, 'l' locale."""
    sgt = SegniDaTesto(rnd_eco, base)
    out, tipi = OrderedDict(), []
    pos = ib = 0
    for p, rows in layout:
        npos = sum(n for _, n in rows)
        flags = eco_flag[pos:pos + npos]
        nb = npos - sum(flags)
        pagina_base = base[ib:ib + nb]
        distinte = sorted(set(pagina_base))
        tema = rnd_eco.sample(distinte, min(k_tema, len(distinte))) if distinte else []
        prev, nr, j, kb = [], [], 0, 0
        for ini, n in rows:
            cur = []
            for _ in range(n):
                if flags[j]:
                    cand = prev + cur
                    if tema and (rnd_eco.random() < Q_TEMA or not cand):
                        w, t = rnd_eco.choice(tema), 't'
                    elif cand:
                        w, t = CP.modifica(sgt, rnd_eco.choice(cand)), 'l'
                    else:
                        w, t = sgt.stringa(4), 'l'
                else:
                    w, t = pagina_base[kb], 'b'
                    kb += 1
                cur.append(w)
                tipi.append(t)
                j += 1
            nr.append((ini, cur))
            prev = cur
        out[p] = nr
        pos += npos
        ib += nb
    return out, tipi


# ---------------------------------------------------------------- tutto insieme

def genera_combinato(cod, valore, istanza, layout, variante=None):
    """Il testo di una combinazione, per l'istanza `istanza` (1, 2, 3...), nell'impaginazione `layout` (solo lunghezze).
    Restituisce (pagine, meta) con meta di soli numeri (e, per la prova di decifrazione, `_info` con le tavole: non si scrive)."""
    cfg = configurazione(cod, valore, variante)
    N = sum(CP.parole_per_pagina(layout))
    chiaro = COMBINATI[cod]['chiaro']
    puro = cfg['A'] == 20 and cfg['b'] == 0 and cfg['n'] == 0
    # VE e' accoppiato al verboso di ia14 (stesse tavole, stesso testo in chiaro, stesso punto di partenza): cosi' la differenza e' l'eco
    seme = CP.seme_di('V', cfg['T'], chiaro, istanza) if puro else seme19(cod, valore, variante or '', istanza)
    rnd = random.Random(seme)
    pc = CP.parole_chiaro(chiaro)
    inizio = rnd.randrange(0, max(1, len(pc) - 3 * N // 2))
    # eco: quali posizioni sono nulle (caso separato, cosi' la base non dipende da p)
    rnd_eco = random.Random(seme19('eco', cod, valore, variante or '', istanza))
    p = cfg['p']
    eco_flag = [rnd_eco.random() < p for _ in range(N)] if p > 0 else [False] * N
    n_eco = sum(eco_flag)
    n_base = N - n_eco
    att = attributi_posizione(layout)
    attrs = [a for a, f in zip(att, eco_flag) if not f]
    if cfg['n'] > 0:
        sub = pc[inizio:inizio + N]
        giri = 0
        while len(sub) < N:
            sub = sub + pc[:N - len(sub)]
            giri += 1
        base, info = genera_base(rnd, n_base, attrs, cfg, parole_chiaro=sub)
    else:
        lettere, giri = CP.lettere_da(pc, inizio, int(1.62 * N) + 50)
        base, info = genera_base(rnd, n_base, attrs, cfg, lettere=lettere)
    pagine, tipi = tessi_eco(rnd_eco, base, layout, eco_flag)
    tutte = [w for rows in pagine.values() for _, ws in rows for w in ws]
    meta = dict(codice=cod, valore=valore, variante=variante, istanza=istanza, parole=N, parole_base=n_base, quota_eco=n_eco / N,
                quota_eco_tema=tipi.count('t') / N, quota_eco_locale=tipi.count('l') / N, lunghezza_media=sum(len(w) for w in tutte) / N,
                tipi_distinti=len(set(tutte)), lunghezza_prefisso=info['lp'], tavole_totali=info['tavole_totali'], giri_testo=giri,
                config=dict(cfg))
    meta['_info'] = info
    meta['_tipi'] = tipi
    return pagine, meta
