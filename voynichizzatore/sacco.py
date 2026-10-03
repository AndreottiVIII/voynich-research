# -*- coding: utf-8 -*-
"""Il sacco di pagina: quali parole stanno in ogni pagina (e404).

Parole note (viste almeno due volte nel libro): pescate dal lessico della sezione e lingua della pagina (occorrenze delle
altre pagine), con ripetizione dentro la pagina: a ogni parola, con probabilita' n/(n+theta) si ripete una parola nota gia'
messa nella pagina (n = quante ce ne sono), altrimenti si pesca dal lessico. theta = None: nessuna ripetizione (K1).
Parole nuove: vere, oppure inventate da parole_nuove.FormeUniche (T-LPS) nei posti delle parole uniche vere.
"""
import os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))


class Sacco:
    """rr: righe (pagina, inizio paragrafo, parole) del Voynich; tipo: pagina -> (sezione, lingua)."""

    def __init__(self, rr, tipo):
        self.rr, self.tipo = rr, tipo
        self.conta = Counter(w for _, _, ps in rr for w in ps)
        note = OrderedDict()
        for p, _, ps in rr:
            note.setdefault(p, []).extend(w for w in ps if self.conta[w] >= 2)
        self.pagine = list(note)
        self.lessico = {}
        for p in self.pagine:
            serb = [w for q in self.pagine if q != p and tipo[q] == tipo[p] for w in note[q]]
            if len(serb) < 500:
                serb = [w for q in self.pagine if q != p and tipo[q][0] == tipo[p][0] for w in note[q]]
            if len(serb) < 500:
                serb = [w for q in self.pagine if q != p for w in note[q]]
            self.lessico[p] = serb
        self._fu = None

    def forme(self):
        if self._fu is None:
            import parole_nuove
            self._fu = parole_nuove.FormeUniche(self.rr)
        self._fu.usate = set()
        return self._fu

    def genera(self, seme, theta=None, nuove='vere'):
        """Il testo con le parole note pescate (e, con nuove='inventate', le uniche sostituite); stessa impaginazione."""
        from disposizione import posizione
        rnd = random.Random(seme)
        fu = self.forme() if nuove == 'inventate' else None
        out, pag, gia, profilo = [], None, [], None
        for p, ini, ps in self.rr:
            if p != pag:
                pag, gia = p, []
                if fu:
                    profilo = fu.profilo([w for q, _, x in self.rr if q == p for w in x])
            serb = self.lessico[p]
            riga = []
            for j, w in enumerate(ps):
                if self.conta[w] >= 2:
                    if theta is not None and gia and rnd.random() < len(gia) / (len(gia) + theta):
                        w = gia[rnd.randrange(len(gia))]
                    else:
                        w = serb[rnd.randrange(len(serb))]
                    gia.append(w)
                elif fu:
                    w = fu.inventa('T-LPS', 4 * bool(ini) + posizione(j, len(ps)), profilo, rnd)
                riga.append(w)
            out.append((p, ini, riga))
        return out
