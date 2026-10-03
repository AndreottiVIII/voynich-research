# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 7 (semi di ricerca 1 e 2), dalla v5 (bordi legati, scelte di riga per selezione, delta 0,2).
Si provano: piu' lessico globale (delta 0,3 e 0,4), la circolazione leggera delle rare (prova_v6b: con le classi, 38 punti
e AUC 0,821), bordi piu' deboli (0,7), e la riga persa dalla v5 (rip 0,4).

    PROCESSI=6 python voynichizzatore/prova_v7.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p
import versioni

V5 = dict(versioni.V5)
C = {'circola': 0.5, 'chiave': 'larga+', 'max_rara': 10, 'posizione': True}
p.NOME = 'prova_v7'
p.BASE = versioni.V5
p.CONF = [('v5', {}), ('δ 0,3', {'delta': 0.3}), ('δ 0,4', {'delta': 0.4}), ('+ circola pos 0,5', dict(C)),
          ('bordi 0,7/0,7', {'lam_fin': 0.7, 'lam_pre': 0.7}), ('rip 0,4', {'rip': 0.4}), ('δ 0,3 + circola pos 0,5', dict(C, delta=0.3)),
          ('classi 0,4', {'lam_cl': 0.4})]

if __name__ == '__main__':
    p.main()
