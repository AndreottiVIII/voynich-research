# -*- coding: utf-8 -*-
"""Esperimento 218: risolutore dell'e17 con una chiave che dipende dalla posizione nella parola (ogni segno distinto in
iniziale, interno, finale, parola di un solo segno), sul testo ripulito.

Preregistrazione: preregistrazioni/e218.md. Scrive risultati/e218_chiave_posizionale.json e .md.
"""
import os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import forza_bruta as fb
import e17_ricottura as e17

LINGUE = OrderedDict([('Latin', 'latino'), ('Italian', 'italiano'), ('German', 'tedesco'), ('English', 'inglese'), ('French', 'francese'), ('Spanish', 'spagnolo'),
                      ('Czech', 'ceco'), ('Hungarian', 'ungherese'), ('Hebrew', 'ebraico'), ('Arabic', 'arabo')])


def posizionale(w):
    u = fb.G(w)
    if len(u) == 1:
        return [u[0] + '=']
    return [u[0] + '^'] + list(u[1:-1]) + [u[-1] + '$']


def main():
    righe = fb.righe_ripulite()
    modi = OrderedDict([(fb.RIF, e17.in_unita(righe, fb.G)), ('ripulito, chiave posizionale', e17.in_unita(righe, posizionale))])
    fb.esegui(modi, LINGUE, 'e218_chiave_posizionale', 'e218 — Chiave che dipende dalla posizione nella parola', 'preregistrazioni/e218.md')


if __name__ == '__main__':
    main()
