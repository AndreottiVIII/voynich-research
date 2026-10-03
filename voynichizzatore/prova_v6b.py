# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 6, prova gemella (semi 1 e 2): nella prova_v5 "circola + bordi 1/1" ha dato l'AUC dell'e231 piu'
bassa sui semi di ricerca (0,804; e288 0,857) perdendo 3 punti di pagella (ripetizione, curva piatta, gradiente). Qui la
stessa strada con le correzioni del giro 6 (bordi senza premio alla ripetizione; classi di riga per selezione) e la
circolazione con e senza il vincolo della posizione nella riga.

    PROCESSI=8 python voynichizzatore/prova_v6b.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p

B = {'lam_fin': 1.0, 'lam_pre': 1.0}
C = {'circola': 1.0, 'chiave': 'larga+', 'max_rara': 10}
p.NOME = 'prova_v6b'
p.CONF = [('bordi 1/1 + circola pos', dict(B, posizione=True, **C)), ('bordi 1/1 + classi 0,3 + circola pos', dict(B, lam_cl=0.3, posizione=True, **C)),
          ('bordi 1/1 + classi 0,3 + circola pos 0,5', dict(B, lam_cl=0.3, posizione=True, **dict(C, circola=0.5))),
          ('bordi 1/1 + classi 0,3 + circola', dict(B, lam_cl=0.3, **C))]

if __name__ == '__main__':
    p.main()
