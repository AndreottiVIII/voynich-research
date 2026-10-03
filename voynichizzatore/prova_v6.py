# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 6 (semi di ricerca 1 e 2), con il lavoro della prova_v4b. Correzioni dopo la prova_v5:
- bordi legati (corpo6) senza fattore per la ripetizione della parola precedente (la prova_v5 perdeva "ripetizione");
- classi concordi nella riga per selezione fra le candidate (corpo6, lam_cl), senza contare le parole uguali alla candidata;
- le parole rare che girano per scambio (corpo5.circola) sono scartate: anche solo fra pagine vicine e nella stessa
  posizione della riga perdono omogeneita' e legame (prove veloci sul seme 1). Al loro posto, perche' le rare siano meno
  "della pagina": parole di base dal lessico globale (delta) o pesi piu' forti per le parole frequenti della pagina (alfa).
Regola (QUADERNO, e292): un ritocco conta solo se migliora di almeno 4 punti di pagella estesa sui due semi, o di 0,02
di AUC a pagella non peggiore; poi verifica sui semi 7-9 con il banco e293.

    PROCESSI=14 python voynichizzatore/prova_v6.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prova_v4b as p

B = {'lam_fin': 1.0, 'lam_pre': 1.0}
B7 = {'lam_fin': 0.7, 'lam_pre': 0.7}
p.NOME = 'prova_v6'
p.CONF = [('e288', {}), ('bordi 1/1', dict(B)), ('bordi 0,7/0,7', dict(B7)), ('bordi 1/1 + classi 0,3', dict(B, lam_cl=0.3)),
          ('bordi 0,7/0,7 + classi 0,3', dict(B7, lam_cl=0.3)), ('bordi 1/1 + classi 0,5', dict(B, lam_cl=0.5)),
          ('bordi 1/1 + classi 0,3 + δ 0,2', dict(B, lam_cl=0.3, delta=0.2)), ('bordi 1/1 + classi 0,3 + α 1,3', dict(B, lam_cl=0.3, alfa=1.3))]

if __name__ == '__main__':
    p.main()
