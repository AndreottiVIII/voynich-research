# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 10 (semi di ricerca 1 e 2), dalla v6 (v5 + rip 0,4). Nel giro 8 p/f nelle prime righe
(galli 1/0,7) porta l'AUC dell'e266 della v5 da 0,923 a 0,861 a pagella estesa uguale. Qui sopra la v6, con e senza i
ritocchi del giro 9 per il gradiente e il cancello della riga (tema della pagina theta, varianti della parola precedente
chi) e con la lunghezza stabile leggera (beta 0,5, l'unica configurazione del giro 8 con la riga).

    PROCESSI=6 python voynichizzatore/prova_v10.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p
import versioni

G = {'galli_su': 1.0, 'galli_giu': 0.7}
p.NOME = 'prova_v10'
p.BASE = versioni.V6
p.CONF = [('v6', {}), ('+ galli 1/0,7', dict(G)), ('+ galli + β 0,5', dict(G, beta=0.5)), ('+ galli + θ 0,4', dict(G, theta=0.4)),
          ('+ galli + θ 0,5 + χ 0,3', dict(G, theta=0.5, chi=0.3)), ('+ galli + θ 0,4 + χ 0,3', dict(G, theta=0.4, chi=0.3)),
          ('+ galli + θ 0,4 + β 0,5', dict(G, theta=0.4, beta=0.5)), ('+ galli + classi 0,4', dict(G, lam_cl=0.4))]

if __name__ == '__main__':
    p.main()
