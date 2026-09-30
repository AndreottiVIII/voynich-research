# -*- coding: utf-8 -*-
"""Testi artificiali: come verrebbe il Voynich se fosse fatto cosi'?

Due famiglie.

1. Codifiche di un testo vero ("tokenizzato"): si parte da latino o italiano
   e si cifra. Cifrario verboso (ogni lettera diventa uno o due glifi), codice
   parola per parola (ogni parola diventa una parola del Voynich di pari
   frequenza), sillabe usate come parole, codice con varianti (ogni parola ha
   piu' codici e se ne sceglie uno a caso). Se una di queste desse un testo
   con l'impronta del Voynich, l'ipotesi reggerebbe.

2. Autocitazione, sul modello proposto da Timm e Schinner (2020): chi scrive
   copia una parola gia' scritta poco sopra nella pagina e la modifica un po'.
   Le modifiche possibili (un glifo al posto di un altro, un glifo aggiunto o
   tolto in testa o in coda) e la loro frequenza si ricavano dalle coppie di
   parole del Voynich che differiscono per una sola modifica; non si usa
   nessuna informazione su dove stanno le parole nella pagina.
"""
import math, random
from collections import Counter, defaultdict

import misure

VOCALI = set('aeiouyàèéìíòóùúâêîôûäëïöü')
MUTE, LIQUIDE = set('bcdfgptv'), set('lr')


# --- sillabe ------------------------------------------------------------------

def sillabe(parola):
    """Divisione in sillabe alla buona, valida per latino e italiano: una
    consonante fra due vocali va con la seconda; di due o piu' la prima resta
    con la sillaba prima, salvo muta piu' liquida (pa-tre) che va avanti intera."""
    nuclei, i = [], 0
    while i < len(parola):
        if parola[i] in VOCALI:
            j = i
            while j + 1 < len(parola) and parola[j + 1] in VOCALI:
                j += 1
            nuclei.append((i, j))
            i = j + 1
        else:
            i += 1
    if len(nuclei) < 2:
        return [parola]
    tagli = []
    for (_, fine), (inizio, _) in zip(nuclei, nuclei[1:]):
        cons = parola[fine + 1:inizio]
        if len(cons) <= 1 or (len(cons) == 2 and cons[0] in MUTE and cons[1] in LIQUIDE):
            tagli.append(fine + 1)
        else:
            tagli.append(fine + 2)
    pezzi, prima = [], 0
    for t in tagli:
        pezzi.append(parola[prima:t])
        prima = t
    pezzi.append(parola[prima:])
    return pezzi


def in_sillabe(parole):
    return [s for p in parole for s in sillabe(p)]


# --- un modello dei glifi per inventare parole "alla Voynich" ---------------

class ModelloParole:
    """Trigrammi di glifi, per inventare parole nuove dall'aspetto voynichese
    quando un codice ha bisogno di piu' parole di quante il Voynich ne abbia."""

    def __init__(self, parole, dividi):
        self.dividi = dividi
        self.conti = defaultdict(Counter)
        for p in parole:
            u = ['^', '^'] + dividi(p) + ['$']
            for i in range(2, len(u)):
                self.conti[(u[i - 2], u[i - 1])][u[i]] += 1

    def inventa(self, rnd, massimo=12):
        u = ['^', '^']
        while len(u) < massimo + 2:
            scelte = self.conti[(u[-2], u[-1])]
            g = rnd.choices(list(scelte), weights=list(scelte.values()))[0]
            if g == '$':
                break
            u.append(g)
        return ''.join(u[2:])


def vocabolario_voynich(parole):
    """Le parole del Voynich dalla piu' frequente alla meno frequente."""
    return [w for w, _ in Counter(parole).most_common()]


def codice_per_rango(testo, parole_voynich, modello, rnd, varianti=None):
    """Ogni parola del testo diventa una parola del Voynich di pari rango di
    frequenza. Con varianti=funzione(frequenza) ogni parola riceve piu' codici,
    e a ogni occorrenza se ne sceglie uno a caso (codice omofonico)."""
    ordine = [w for w, _ in Counter(testo).most_common()]
    freq = Counter(testo)
    disponibili = list(vocabolario_voynich(parole_voynich))
    usate = set(disponibili)

    def nuova():
        if disponibili:
            return disponibili.pop(0)
        while True:
            w = modello.inventa(rnd)
            if w and w not in usate:
                usate.add(w)
                return w

    codice = {}
    for w in ordine:
        k = varianti(freq[w]) if varianti else 1
        codice[w] = [nuova() for _ in range(k)]
    return [rnd.choice(codice[w]) for w in testo]


# --- cifrario verboso ---------------------------------------------------------

def cifra_verboso(testo, tabella):
    return [''.join(tabella[c] for c in p) for p in testo]


def cerca_verboso(testo, glifi, rnd, bersaglio_h2, bersaglio_lung, prove=300):
    """Cerca a caso il cifrario verboso che piu' avvicina h2 e lunghezza delle
    parole a quelle del Voynich. Le lettere piu' frequenti ricevono un glifo
    solo, le altre una coppia di glifi; quante e quali cambia a ogni prova.
    Restituisce la tabella migliore e i suoi numeri."""
    lettere = [c for c, _ in Counter(''.join(testo)).most_common()]
    singoli = glifi[:20]
    coppie = [a + b for a in glifi[:12] for b in glifi[:12]]
    dividi = misure.divisore(glifi)
    migliore = None
    for _ in range(prove):
        quante_singole = rnd.randint(0, min(len(lettere), len(singoli)))
        tabella = {}
        s = rnd.sample(singoli, quante_singole)
        c = rnd.sample(coppie, len(lettere) - quante_singole)
        for i, lettera in enumerate(lettere):
            tabella[lettera] = s[i] if i < quante_singole else c[i - quante_singole]
        cifrato = cifra_verboso(testo[:15000], tabella)
        h2 = misure.condizionate(misure.sequenza(cifrato, dividi), k_max=2)['h2']
        lung = sum(len(dividi(p)) for p in cifrato) / len(cifrato)
        punti = abs(h2 - bersaglio_h2) / 0.1 + abs(lung - bersaglio_lung) / 0.3
        if migliore is None or punti < migliore[0]:
            migliore = (punti, tabella, h2, lung, quante_singole)
    return migliore


# --- autocitazione ------------------------------------------------------------

class Modifiche:
    """Le modifiche che trasformano una parola del Voynich in un'altra parola
    del Voynich: sostituzione di un glifo, glifo aggiunto o tolto in testa o
    in coda. Pesi presi dalle coppie di parole (frequenti almeno due volte) che
    differiscono esattamente per una di queste modifiche."""

    def __init__(self, parole, dividi):
        self.dividi = dividi
        freq = Counter(parole)
        tipi = {tuple(dividi(w)): c for w, c in freq.items() if c >= 2}
        self.sostituzioni = defaultdict(Counter)
        for pos_max in range(1, 13):
            gruppi = defaultdict(list)
            for u, c in tipi.items():
                if len(u) == pos_max:
                    for i in range(pos_max):
                        gruppi[(i, u[:i] + u[i + 1:])].append((u[i], c))
            for (_, _), membri in gruppi.items():
                for a, ca in membri:
                    for b, cb in membri:
                        if a != b:
                            self.sostituzioni[a][b] += min(ca, cb)
        self.testa, self.coda = Counter(), Counter()
        for u, c in tipi.items():
            if len(u) > 1:
                if u[1:] in tipi:
                    self.testa[u[0]] += min(c, tipi[u[1:]])
                if u[:-1] in tipi:
                    self.coda[u[-1]] += min(c, tipi[u[:-1]])
        self.n_sost = sum(sum(v.values()) for v in self.sostituzioni.values())
        self.n_testa, self.n_coda = sum(self.testa.values()), sum(self.coda.values())
        # coppie di glifi ammesse dentro una parola (con ^ e $ per inizio e fine)
        self.ammesse = set()
        for u in tipi:
            v = ('^',) + u + ('$',)
            self.ammesse.update(zip(v, v[1:]))

    def valida(self, u):
        v = ('^',) + tuple(u) + ('$',)
        return len(u) > 0 and all(c in self.ammesse for c in zip(v, v[1:]))

    def modifica(self, u, rnd):
        u = list(u)
        tot = self.n_sost + 2 * self.n_testa + 2 * self.n_coda
        x = rnd.random() * tot
        if x < self.n_sost:
            posti = [i for i, g in enumerate(u) if self.sostituzioni[g]]
            if posti:
                i = rnd.choice(posti)
                scelte = self.sostituzioni[u[i]]
                u[i] = rnd.choices(list(scelte), weights=list(scelte.values()))[0]
        elif x < self.n_sost + self.n_testa:
            u.insert(0, rnd.choices(list(self.testa), weights=list(self.testa.values()))[0])
        elif x < self.n_sost + 2 * self.n_testa:
            if len(u) > 1 and u[0] in self.testa:
                u.pop(0)
        elif x < self.n_sost + 2 * self.n_testa + self.n_coda:
            u.append(rnd.choices(list(self.coda), weights=list(self.coda.values()))[0])
        else:
            if len(u) > 1 and u[-1] in self.coda:
                u.pop()
        return tuple(u)


def codice_con_stile(testo, parole_voynich, modello, modifiche, rnd, parole_pagina=160,
                     regole=3, forza=0.7):
    """La versione piu' forte dell'ipotesi "tokenizzata": un codice parola per
    parola (come codice_per_rango) scritto da uno scriba che ogni pagina ha le
    sue abitudini. Per ogni pagina si scelgono alcune regole di scrittura fra
    quelle tipiche del Voynich (ch->sh, k->t, q in testa, y in coda...) e le si
    applicano con probabilita' forza a tutte le parole della pagina che le
    ammettono. Parole diverse della stessa pagina finiscono cosi' per condividere
    gli stessi tratti, come farebbe un'ortografia che cambia da una seduta
    all'altra."""
    base = codice_per_rango(testo, parole_voynich, modello, rnd)
    dividi = modifiche.dividi
    ops = []
    for a, cambi in modifiche.sostituzioni.items():
        for b, c in cambi.most_common(3):
            ops.append((('sost', a, b), c))
    ops += [(('testa', g), c) for g, c in modifiche.testa.most_common(6)]
    ops += [(('coda', g), c) for g, c in modifiche.coda.most_common(6)]
    ops.sort(key=lambda o: -o[1])
    ops = ops[:40]
    out = []
    for inizio in range(0, len(base), parole_pagina):
        scelte = []   # una lista, non un insieme: l'ordine deve essere lo stesso a ogni esecuzione
        while len(scelte) < regole:
            op = rnd.choices([o for o, _ in ops], weights=[c for _, c in ops])[0]
            if op not in scelte:
                scelte.append(op)
        for w in base[inizio:inizio + parole_pagina]:
            u = list(dividi(w))
            for op in scelte:
                if rnd.random() > forza:
                    continue
                prova = list(u)
                if op[0] == 'sost' and op[1] in prova:
                    prova = [op[2] if g == op[1] else g for g in prova]
                elif op[0] == 'testa' and prova[0] != op[1]:
                    prova = [op[1]] + prova
                elif op[0] == 'coda' and prova[-1] != op[1]:
                    prova = prova + [op[1]]
                if modifiche.valida(prova):
                    u = prova
            out.append(''.join(u))
    return out


# --- il cifrario Naibbe (Greshko 2025) ---------------------------------------
#
# Greshko, M. A. (2025). The Naibbe cipher: a substitution cipher that encrypts
# Latin and Italian as Voynich Manuscript-like ciphertext. Cryptologia,
# doi:10.1080/01611194.2025.2566408. Codice e tabelle: github.com/greshko/
# naibbe-cipher (licenza MIT modificata, che chiede questa citazione).
#
# Qui lo stesso algoritmo di naibbe.py, riscritto per avere semi fissi e per
# poter far cambiare da una pagina all'altra le preferenze fra le tabelle.
# Il testo in chiaro, senza spazi, si taglia a caso in pezzi di una o due
# lettere; ogni pezzo diventa una "parola": una lettera sola prende la forma
# 'unigram' di una tabella, una coppia unisce il 'prefix' della prima lettera
# e il 'suffix' della seconda, ciascuno da una tabella pescata a parte. Le
# tabelle si pescano da un mazzo di 52 carte con pesi diversi.

NAIBBE_TABELLE = ['alpha', 'beta1', 'beta2', 'beta3', 'gamma1', 'gamma2']
NAIBBE_PESI = {'alpha': 20, 'beta1': 8, 'beta2': 8, 'beta3': 8, 'gamma1': 4, 'gamma2': 4}


def naibbe_pulisci(testo):
    """Come clean_line di naibbe.py: niente diacritici, solo lettere,
    w -> uu, j -> i, k -> c."""
    import unicodedata
    n = unicodedata.normalize('NFD', testo)
    n = ''.join(c for c in n if unicodedata.category(c) != 'Mn')
    sostituzioni = {'æ': 'ae', 'œ': 'oe', 'ð': 'd', 'þ': 'th', 'ł': 'l', 'ß': 'ss', 'ø': 'o'}
    n = ''.join(sostituzioni.get(c, c) for c in n.lower())
    n = ''.join(c for c in n if c.isalpha()).upper()
    return n.replace('W', 'UU').replace('J', 'I').replace('K', 'C').lower()


def naibbe_tabelle(percorso_csv):
    import csv
    with open(percorso_csv, encoding='utf-8-sig') as f:
        return {r['code']: r['glyphs'] for r in csv.DictReader(f)}


def naibbe(lettere, glifi, rnd, parole_pagina=None, concentrazione=None):
    """Cifra una stringa di lettere. Restituisce la lista delle parole e, per
    controllo, la lista dei pezzi in chiaro (una o due lettere) di ciascuna.

    Senza concentrazione il mazzo e' quello di Greshko. Con concentrazione=k,
    a ogni nuova pagina (ogni parole_pagina parole) le probabilita' delle sei
    tabelle si ripescano da una Dirichlet centrata sui pesi del mazzo: piu' k
    e' piccolo, piu' ogni pagina preferisce poche tabelle, come uno scriba che
    cambia abitudini da una seduta all'altra."""
    unigrammi = {g for c, g in glifi.items() if c.startswith('unigram_')}
    pezzi, i = [], 0
    while i < len(lettere):
        if i == len(lettere) - 1 or rnd.random() < 17 / 36:
            pezzi.append(lettere[i])
            i += 1
        else:
            pezzi.append(lettere[i:i + 2])
            i += 2
    mazzo, pos = [], 0
    probabilita = None

    def pesca(dal_mazzo=False):
        nonlocal mazzo, pos
        if probabilita is not None and not dal_mazzo:
            return rnd.choices(NAIBBE_TABELLE, weights=probabilita)[0]
        if pos >= len(mazzo):
            mazzo = [t for t, n in NAIBBE_PESI.items() for _ in range(n)]
            rnd.shuffle(mazzo)
            pos = 0
        pos += 1
        return mazzo[pos - 1]

    parole = []
    for pezzo in pezzi:
        if concentrazione and parole_pagina and len(parole) % parole_pagina == 0:
            base = [NAIBBE_PESI[t] for t in NAIBBE_TABELLE]
            tot = sum(base)
            g = [rnd.gammavariate(concentrazione * b / tot, 1) for b in base]
            probabilita = [x / sum(g) for x in g]
        if len(pezzo) == 1:
            parole.append(glifi['unigram_%s_%s' % (pesca(), pezzo)])
        else:
            tentativi = 0
            while True:
                # con una pagina tutta su una tabella certe coppie danno sempre
                # una parola gia' usata per una lettera sola: dopo 50 tentativi
                # si torna al mazzo normale, altrimenti non si esce piu'
                dal_mazzo = tentativi >= 50
                w = (glifi['prefix_%s_%s' % (pesca(dal_mazzo), pezzo[0])] +
                     glifi['suffix_%s_%s' % (pesca(dal_mazzo), pezzo[1])])
                if w not in unigrammi:
                    break
                tentativi += 1
            parole.append(w)
    return parole, pezzi


def poisson(rnd, lam):
    soglia, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p < soglia:
            return k
        k += 1


def autocitazione(struttura, semi_righe, modifiche, rnd, lam=1.0, tau=1.5, lontano=0.05,
                  preferenza=0.0):
    """Genera un testo con la stessa struttura del Voynich (quante pagine,
    quante righe per pagina, quante parole per riga).

    Ogni parola nasce da una parola gia' scritta: di solito nella stessa pagina,
    scegliendo la riga con probabilita' che cala con la distanza (tau: quante
    righe sopra si guarda, in media), a volte (lontano) da un punto qualsiasi
    del testo gia' scritto. Dentro la riga scelta, con preferenza > 0 si pesca
    piu' volentieri una parola gia' usata spesso (peso: volte usata ** preferenza).
    La copia subisce un numero di modifiche preso da una distribuzione di
    Poisson di media lam; una modifica che produce una parola impossibile
    (coppie di glifi mai viste) viene scartata."""
    dividi = modifiche.dividi
    scritte = [tuple(dividi(w)) for riga in semi_righe for w in riga]
    usate = Counter(scritte)

    def pesca(parole):
        if not preferenza:
            return rnd.choice(parole)
        return rnd.choices(parole, weights=[usate[p] ** preferenza for p in parole])[0]

    pagine_out = []
    for righe_pagina in struttura:
        pagina = []
        for n_parole in righe_pagina:
            riga = []
            for _ in range(n_parole):
                if pagina or riga:
                    if rnd.random() < lontano:
                        fonte = rnd.choice(scritte)
                    else:
                        candidate = [(0, riga)] if riga else []
                        candidate += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                        pesi = [math.exp(-d / tau) for d, _ in candidate]
                        _, sorgente = rnd.choices(candidate, weights=pesi)[0]
                        fonte = pesca(sorgente)
                else:
                    fonte = pesca(scritte[-200:])   # inizio pagina: dalla pagina prima
                nuova = fonte
                for _ in range(poisson(rnd, lam)):
                    prova = modifiche.modifica(nuova, rnd)
                    if modifiche.valida(prova):
                        nuova = prova
                riga.append(nuova)
                scritte.append(nuova)
                usate[nuova] += 1
            pagina.append(riga)
        pagine_out.append([[''.join(u) for u in riga] for riga in pagina])
    return pagine_out
