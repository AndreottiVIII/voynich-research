# -*- coding: utf-8 -*-
"""Parole nuove: modi di inventare parole che non sono nel Voynich, con la forma delle sue parole uniche (e403).

- variante: una modifica (operatore empirico dell'e241) di una parola di partenza;
- trigrammi: modello a trigrammi di segni imparato sulle parole uniche;
- unione: due parole scritte attaccate.
Ogni parola restituita e' ben formata per l'operatore (o campionata dal modello), non attestata e non gia' usata.
"""
import os, random, sys
from collections import Counter, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure

D = misure.divisore(misure.GLIFI_EVA)
QUOTE_MISTA = (0.72, 0.14, 0.14)      # variante, unione, trigrammi: descrizione delle parole uniche (preregistrazione e403)


class Trigrammi:
    def __init__(self, parole):
        self.t = defaultdict(Counter)
        for w in parole:
            u = ('^', '^') + tuple(D(w)) + ('$',)
            for a, b, c in zip(u, u[1:], u[2:]):
                self.t[(a, b)][c] += 1
        self.t = {k: (list(v), list(v.values())) for k, v in self.t.items()}

    def campiona(self, rnd):
        a, b, out = '^', '^', []
        while len(out) < 14:
            segni, pesi = self.t[(a, b)]
            c = rnd.choices(segni, pesi)[0]
            if c == '$':
                break
            out.append(c)
            a, b = b, c
        return ''.join(out)


class ParoleNuove:
    """conta: Counter delle parole del testo da cui si impara; mod: operatore di variante (c2['mod'] di e251._prepara)."""

    def __init__(self, conta, mod):
        self.att = set(conta)
        self.mod = mod
        self.tipi_libro = sorted(w for w, n in conta.items() if n >= 2)
        self.tri = Trigrammi(sorted(w for w, n in conta.items() if n == 1))
        self.usate = set()

    def _nuova(self, w):
        if w and len(w) >= 2 and w not in self.att and w not in self.usate:
            self.usate.add(w)
            return True
        return False

    def trigrammi(self, rnd):
        for _ in range(200):
            w = self.tri.campiona(rnd)
            if self._nuova(w):
                return w
        raise RuntimeError('trigrammi: nessuna parola nuova')

    def variante(self, basi, rnd):
        for _ in range(60):
            u = tuple(D(basi[rnd.randrange(len(basi))]))
            x = self.mod.modifica(u, rnd)
            if self.mod.valida(x) and self._nuova(''.join(x)):
                return ''.join(x)
        return self.trigrammi(rnd)

    def unione(self, basi, rnd):
        for _ in range(60):
            w = basi[rnd.randrange(len(basi))] + basi[rnd.randrange(len(basi))]
            if len(D(w)) <= 12 and self._nuova(w):
                return w
        return self.trigrammi(rnd)

    def inventa(self, modo, tipi_pagina, rnd):
        """modo: 'variante-libro', 'variante-pagina', 'trigrammi', 'mista'. tipi_pagina: tipi non unici della pagina."""
        pagina = tipi_pagina or self.tipi_libro
        if modo == 'variante-libro':
            return self.variante(self.tipi_libro, rnd)
        if modo == 'variante-pagina':
            return self.variante(pagina, rnd)
        if modo == 'trigrammi':
            return self.trigrammi(rnd)
        x = rnd.random()
        if x < QUOTE_MISTA[0]:
            return self.variante(pagina, rnd)
        if x < QUOTE_MISTA[0] + QUOTE_MISTA[1]:
            return self.unione(pagina, rnd)
        return self.trigrammi(rnd)
