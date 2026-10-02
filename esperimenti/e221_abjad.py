# -*- coding: utf-8 -*-
"""Esperimento 221: risolutore dell'e17 sullo "scheletro consonantico" del testo ripulito (tolti i segni a, o, e, y, i)
contro lingue scritte senza vocali (abjad) e, per confronto, alcune con vocali.

Preregistrazione: preregistrazioni/e221.md. Scrive risultati/e221_abjad.json e .md.
"""
import os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import forza_bruta as fb
import e17_ricottura as e17

VOCALI = {'a', 'o', 'e', 'y', 'i'}
LINGUE = OrderedDict([('Hebrew', 'ebraico'), ('Arabic', 'arabo'), ('Syriac-NT', 'siriaco'), ('Farsi', 'persiano'), ('Latin', 'latino'), ('Italian', 'italiano')])


def scheletro(w):
    u = [x for x in fb.G(w) if x not in VOCALI]
    return u


def main():
    righe = fb.righe_ripulite()
    modi = OrderedDict([(fb.RIF, e17.in_unita(righe, fb.G)), ('ripulito, senza segni vocalici', e17.in_unita(righe, scheletro))])
    fb.esegui(modi, LINGUE, 'e221_abjad', 'e221 — Scheletro consonantico contro lingue senza vocali', 'preregistrazioni/e221.md')


if __name__ == '__main__':
    main()
