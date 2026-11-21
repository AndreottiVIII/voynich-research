# -*- coding: utf-8 -*-
"""Supporto di ia21 (modulo, non e' un esperimento): un testo SINTETICO per i controlli.

Perche': nel latino messo nella disposizione del Voynich (il controllo di ia07, ia16) i giudici vedono quasi sempre la differenza
(AUC vicino a 1): un imitatore che migliora non si nota (effetto soffitto). Qui un testo fatto a macchina, con regole semplici e
note, che una rete a segni impara solo in parte:
  - parole costruite da sillabe (lettere latine senza c e h, cosi' nessun glifo fuso e nessuna parola del Voynich);
  - ogni "tema" (circa una pagina) ha un suo piccolo vocabolario, che cambia a poco a poco (il vocabolario della pagina);
  - una parola su sei e' una variante (una lettera cambiata) di una delle ultime 30 parole (l'eco di varianti);
  - fra una parola e la successiva c'e' un legame fra l'ultima lettera e la prima (il contatto);
  - quattro flussi con alfabeti di sillabe un poco diversi, come le "lingue" A e B.
Non e' il Voynich e non contiene parole del Voynich. Si usa solo con SOLO_CONTROLLI=1 (TESTO_PROVA=sintetico), sostituendo
`ia07_voynich_neurale.latino`. Deterministico (semi fissi).
"""
import random
from collections import OrderedDict

CONSONANTI = ['b', 'd', 'f', 'g', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z', 'pl', 'tr', 'st', 'kr', 'br', 'gl']
VOCALI = ['a', 'e', 'i', 'o', 'u']
FINALI = ['', '', 'n', 's', 'r', 'l', 'm']
LETTERE = sorted(set(''.join(CONSONANTI + VOCALI + FINALI)))


def _parola(rnd, cons, voc, fin):
    n = rnd.choice([1, 2, 2, 3])
    return ''.join(rnd.choice(cons) + rnd.choice(voc) for _ in range(n)) + rnd.choice(fin)


def _variante(rnd, w):
    """Una lettera cambiata (sempre una lettera dell'alfabeto di prova)."""
    i = rnd.randrange(len(w))
    nuova = rnd.choice([x for x in LETTERE if x != w[i]])
    return (w[:i] + nuova + w[i + 1:]) or w


def _flusso(seme, ritaglio, strati=True):
    """Flusso infinito di parole. `ritaglio`: quante consonanti/vocali dell'alfabeto di sillabe si usano (flussi un po' diversi).
    `strati=False` (testo "locale"): niente vocabolario di pagina e niente varianti: solo parole a sillabe con frequenze alla Zipf e il
    legame fra ultima e prima lettera di parole vicine; una rete a segni lo puo' imparare quasi tutto."""
    rnd = random.Random(seme)
    cons = CONSONANTI[ritaglio[0]:] + CONSONANTI[:ritaglio[0]]
    cons = cons[:16]
    voc = VOCALI[ritaglio[1]:] + VOCALI[:ritaglio[1]]
    voc = voc[:4]
    fin = FINALI
    globale = []
    while len(globale) < 500:
        w = _parola(rnd, cons, voc, fin)
        if w not in globale:
            globale.append(w)
    peso_g = [1.0 / (i + 1) for i in range(len(globale))]
    # legame fra l'ultima lettera di una parola e la prima della successiva: per ogni ultima lettera un sottoinsieme di prime lettere
    prime = sorted({w[0] for w in globale})
    ammesse = {u: set(rnd.sample(prime, max(3, len(prime) // 2))) for u in sorted({w[-1] for w in globale})}
    tema, da_cambiare, recenti = [], 0, []
    prec = None
    while True:
        if da_cambiare <= 0 or not tema:
            # nuovo tema: meta' delle parole del tema vecchio resta, il resto e' nuovo
            resto = rnd.sample(tema, len(tema) // 2) if tema else []
            nuove = rnd.choices(globale, weights=peso_g, k=40 - len(resto))
            tema = list(dict.fromkeys(resto + nuove))
            da_cambiare = rnd.randint(120, 220)
        x = rnd.random()
        for _ in range(8):
            if strati and x < 0.17 and recenti:
                w = _variante(rnd, rnd.choice(recenti[-30:]))
            elif strati and x < 0.85:
                w = rnd.choices(tema, weights=[1.0 / (i + 1) for i in range(len(tema))])[0]
            else:
                w = rnd.choices(globale, weights=peso_g)[0]
            if prec is None or w[0] in ammesse.get(prec[-1], prime):
                break
            x = rnd.random()                      # ritenta con un'altra scelta
        recenti.append(w)
        if len(recenti) > 60:
            del recenti[:30]
        prec = w
        da_cambiare -= 1
        yield w


def sintetico():
    """Come `ia07_voynich_neurale.latino()`: chiavi 'erbario A', 'A', 'B', '?' con un flusso di parole ciascuna."""
    return OrderedDict([('erbario A', _flusso(910001, (0, 0))), ('A', _flusso(910002, (3, 1))),
                        ('B', _flusso(910003, (6, 2))), ('?', _flusso(910004, (9, 3)))])


def locale():
    """Come `sintetico()` ma senza vocabolario di pagina e senza varianti: solo regole locali (sillabe, Zipf, contatto)."""
    return OrderedDict([('erbario A', _flusso(910001, (0, 0), False)), ('A', _flusso(910002, (3, 1), False)),
                        ('B', _flusso(910003, (6, 2), False)), ('?', _flusso(910004, (9, 3), False))])
