# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 9 (semi di ricerca 1 e 2). Il banco (semi 7-9) mostra che v4 e v5 perdono il cancello della riga
in tutti i semi e la materia "gradiente". Sul seme 1: gradiente = somiglianza a 6 righe / somiglianza nella riga, Voynich
0,89, v3 0,71, v5 0,56 (il lessico globale toglie parole comuni alla pagina; i bordi alzano la somiglianza nella riga);
nel cancello cade A (somiglianza fra parole vicine, >= 1): v5 0,983. Ritocchi: piu' tema di pagina (theta, e251b; nell'e253
theta era il parametro che piu' abbassava l'AUC) e piu' varianti della parola precedente (chi).

    PROCESSI=8 python voynichizzatore/prova_v9.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p
import versioni

p.NOME = 'prova_v9'
p.BASE = versioni.V5
p.CONF = [('v5', {}), ('θ 0,4', {'theta': 0.4}), ('θ 0,5', {'theta': 0.5}), ('χ 0,3', {'chi': 0.3}), ('θ 0,4 + χ 0,3', {'theta': 0.4, 'chi': 0.3}),
          ('θ 0,5 + χ 0,3', {'theta': 0.5, 'chi': 0.3}), ('θ 0,4 + δ 0,1', {'theta': 0.4, 'delta': 0.1}), ('θ 0,5 + χ 0,3 + bordi 0,7', {'theta': 0.5, 'chi': 0.3, 'lam_fin': 0.7, 'lam_pre': 0.7})]

if __name__ == '__main__':
    p.main()
