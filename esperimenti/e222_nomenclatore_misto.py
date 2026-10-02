# -*- coding: utf-8 -*-
"""Esperimento 222: nomenclatore misto. Le parole piu' frequenti (50 o 150 tipi, testo ripulito) si trattano come codici
interi e si tolgono (spezzano la riga); il resto si attacca lettera per lettera con il risolutore dell'e17.

Preregistrazione: preregistrazioni/e222.md. Scrive risultati/e222_nomenclatore_misto.json e .md.
"""
import os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import forza_bruta as fb
import e17_ricottura as e17


def main():
    righe = fb.righe_ripulite()
    freq = Counter(w for r in righe for w in r if w)
    modi = OrderedDict([(fb.RIF, e17.in_unita(righe, fb.G))])
    for n in (50, 150):
        codici = {w for w, _ in freq.most_common(n)}
        modi['ripulito, senza le %d parole più frequenti' % n] = e17.in_unita([[None if w in codici else w for w in r] for r in righe], fb.G)
    fb.esegui(modi, e17.LINGUE, 'e222_nomenclatore_misto', 'e222 — Nomenclatore misto: parole frequenti come codici, il resto lettera per lettera', 'preregistrazioni/e222.md')


if __name__ == '__main__':
    main()
