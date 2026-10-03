# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 8 (semi di ricerca 1 e 2). La diagnosi della v5 con Isidoro nascosto (AUC 0,810 / 0,915) mette in
cima: G8, le prime righe dei paragrafi (p e f: Voynich +0,0315 e +0,008 rispetto alle altre righe, v5 +0,012 e +0,0015);
G6, le coppie identiche (Voynich 0,0097, v5 0,0205); G3, la dispersione delle lunghezze (1,579 contro 1,662). Ritocchi:
p/f nelle prime righe e k/t nelle altre (corpo5.galli_prime), penalita' per le ripetizioni piu' forte (rip), lunghezza
stabile leggera (beta).

    PROCESSI=8 python voynichizzatore/prova_v8.py [v5|v6]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p
import versioni

BASE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in versioni.VERSIONI else 'v5'
G = {'galli_su': 1.0, 'galli_giu': 0.7}
p.NOME = 'prova_v8'
p.BASE = versioni.VERSIONI[BASE]['corpo']
p.CONF = [(BASE, {}), ('galli 1/0,7', dict(G)), ('galli 1/0', {'galli_su': 1.0}), ('galli 1,3/0,7', dict(G, galli_su=1.3)),
          ('rip 0,3', {'rip': 0.3}), ('galli 1/0,7 + rip 0,3', dict(G, rip=0.3)), ('galli 1/0,7 + β 0,5', dict(G, beta=0.5)),
          ('galli 1/0,7 + rip 0,3 + β 0,5', dict(G, rip=0.3, beta=0.5))]

if __name__ == '__main__':
    p.main()
