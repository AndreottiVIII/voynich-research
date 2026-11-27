# -*- coding: utf-8 -*-
"""IA45: estrae dalle trascrizioni le colonne di segni singoli a margine e le righe accanto.

Una colonna e' la lista dei suoi segni, nell'ordine del file. Un segno e' una stringa:
- una unita' EVA (ch, sh, cth... contano come una; per GC ogni carattere e' una unita');
- un glifo raro scritto `Z140z` (nel file `@140;`): identita' propria, mai confuso con altro;
- `?` (illeggibile): ogni `?` e' un segno a se', che non e' uguale a nessun altro (si codifica poi con un numero unico).

Le voci di una colonna con piu' di una unita' (parole) non sono segni: si saltano (la sequenza si considera continua).
Niente di quello che si legge qui va scritto in risultati/: solo numeri.
"""
import os, re, sys
from collections import Counter, namedtuple

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import trascrizione, misure

D_EVA = misure.divisore(misure.GLIFI_EVA)
RARO = re.compile(r'@(\d{3});')
RARO_P = re.compile(r'Z\d{3}z')
PAGINE_COLONNE = ('f49v', 'f66r', 'f76r')
PAGINA_ANELLO = 'f57v'
PAGINE_ESCLUSE_RIFERIMENTO = ('f49v', 'f66r', 'f76r', 'f57v')

# colonna: segni (lista di str); riga_dopo / riga_prima: indice nella lista delle righe P (o None)
Pagina = namedtuple('Pagina', ['nome', 'colonna', 'riga_dopo', 'riga_prima', 'righe_prime', 'unita_testo', 'n_voci', 'n_righe'])


def pulisci_corpo(grezza):
    """Parole di un locus tenendo l'identita' dei glifi rari."""
    corpo = RARO.sub(lambda m: 'Z%sz' % m.group(1), grezza)
    return trascrizione.pulisci(corpo)[0]


def dividi(parola, quale):
    out = []
    for pezzo in re.split(r'(Z\d{3}z)', parola):
        if not pezzo:
            continue
        if RARO_P.fullmatch(pezzo):
            out.append(pezzo)
        elif quale == 'GC':
            out.extend(pezzo)
        else:
            out.extend(D_EVA(pezzo))
    return out


def _righe_pagina(righe, nome):
    return [r for r in righe if r.pagina == nome]


def pagina_colonna(righe, nome, quale):
    """Colonna di segni singoli (loci L0), con la riga P che segue e quella che precede ogni segno."""
    rp = _righe_pagina(righe, nome)
    P = [r for r in rp if r.tipo[0] == 'P']
    righe_prime = []
    for r in P:
        ps = pulisci_corpo(r.grezza)
        righe_prime.append(dividi(ps[0], quale)[0] if ps else None)
    unita_testo = [u for r in P for w in pulisci_corpo(r.grezza) for u in dividi(w, quale)]
    colonna, dopo, prima = [], [], []
    voci = 0
    for r in rp:
        if r.tipo != 'L0':
            continue
        voci += 1
        ps = pulisci_corpo(r.grezza)
        us = [u for w in ps for u in dividi(w, quale)]
        if len(ps) != 1 or len(us) != 1:
            continue
        colonna.append(us[0])
        d = [i for i, p in enumerate(P) if p.numero > r.numero]
        a = [i for i, p in enumerate(P) if p.numero < r.numero]
        dopo.append(d[0] if d else None)
        prima.append(a[-1] if a else None)
    return Pagina(nome, colonna, dopo, prima, righe_prime, unita_testo, voci, len(P))


def anello(righe, quale, nome=PAGINA_ANELLO):
    """Anello: la riga circolare con piu' segni singoli, tutti i suoi segni singoli in ordine."""
    migliore, mig_n = [], -1
    for r in _righe_pagina(righe, nome):
        if r.tipo[0] != 'C':
            continue
        ps = pulisci_corpo(r.grezza)
        sing = [dividi(w, quale) for w in ps]
        sing = [u[0] for u in sing if len(u) == 1]
        if len(sing) > mig_n:
            migliore, mig_n = sing, len(sing)
    return Pagina(nome, migliore, [None] * len(migliore), [None] * len(migliore), [], [], mig_n, 0)


def riferimento(righe, quale, escluse=PAGINE_ESCLUSE_RIFERIMENTO):
    """Frequenze del libro (senza le pagine delle colonne): prima unita' della prima parola di ogni riga P,
    e prima unita' di ogni parola dei paragrafi."""
    prime, tutte = Counter(), Counter()
    for r in righe:
        if r.tipo[0] != 'P' or r.pagina in escluse:
            continue
        ps = pulisci_corpo(r.grezza)
        us = [dividi(w, quale) for w in ps]
        us = [u for u in us if u]
        if not us:
            continue
        prime[us[0][0]] += 1
        for u in us:
            tutte[u[0]] += 1
    return prime, tutte


def tutto(quale):
    righe = trascrizione.leggi(quale)
    pagine = [pagina_colonna(righe, n, quale) for n in PAGINE_COLONNE]
    pagine.append(anello(righe, quale))
    return pagine, riferimento(righe, quale)


def da_righe(righe, quale):
    """Come `tutto`, ma da una lista di Riga gia' costruita (per le prove su testi finti)."""
    pagine = [pagina_colonna(righe, n, quale) for n in PAGINE_COLONNE]
    pagine.append(anello(righe, quale))
    return pagine, riferimento(righe, quale)
