# -*- coding: utf-8 -*-
"""Ciclo avversario, giri 4 e 5 (semi di ricerca 1 e 2), con lo stesso lavoro della prova_v4b. Le classi di riga di
corpo5 sono scartate (prova_v4b: AUC dell'e266 0,955-0,996, pagella giu'). Qui: parole rare che girano fra le pagine
(corpo5.circola, compagne di riserva, rare fino a 10 occorrenze; e296) = v4; piu' i bordi legati nella riga (corpo6,
e294/e295) e il successore gia' visto omega 0,2 (ricerca dell'e292) = candidati v5.

    PROCESSI=8 python voynichizzatore/prova_v5.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p

C = {'circola': 1.0, 'chiave': 'larga+', 'max_rara': 10}
p.NOME = 'prova_v5'
p.CONF = [('e288', {}), ('ω 0,2', {'omega': 0.2}), ('circola', dict(C)),
          ('bordi fin 1 pre 1', {'lam_fin': 1.0, 'lam_pre': 1.0}), ('bordi fin 0,7 pre 1', {'lam_fin': 0.7, 'lam_pre': 1.0}),
          ('circola + bordi fin 1 pre 1', dict(C, lam_fin=1.0, lam_pre=1.0)), ('circola + bordi fin 0,7 pre 1', dict(C, lam_fin=0.7, lam_pre=1.0)),
          ('circola + bordi fin 1 pre 1 + ω 0,2', dict(C, lam_fin=1.0, lam_pre=1.0, omega=0.2))]

if __name__ == '__main__':
    p.main()
