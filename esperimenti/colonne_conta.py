# -*- coding: utf-8 -*-
"""IA45, passo zero: conta i segni delle colonne a margine nelle trascrizioni locali (ZL, IT, GC).

Solo numeri a schermo: niente testo della trascrizione su file. Uso: python esperimenti/colonne_conta.py
"""
import os, sys, itertools
from collections import Counter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import colonne_dati as CD


def main():
    for quale in ('ZL', 'IT', 'GC'):
        pagine, (prime, tutte) = CD.tutto(quale)
        print('=== trascrizione', quale, '| righe P di riferimento (prime unita):', sum(prime.values()))
        for p in pagine:
            c = p.colonna
            allin = len([d for d in p.riga_dopo if d is not None])
            inj = len(set(d for d in p.riga_dopo if d is not None)) == allin and allin > 0
            print('%s voci L0 %d | segni singoli %d (distinti %d, glifi rari %d, illeggibili %d) | righe P %d | segni con riga dopo %d, riga distinta per ogni segno: %s'
                  % (p.nome, p.n_voci, len(c), len(set(c)), sum(1 for x in c if x.startswith('Z')),
                     sum(1 for x in c if x == '?'), p.n_righe, allin, inj))
        for a, b in itertools.combinations(pagine, 2):
            ca = {x for x in a.colonna if x != '?'}
            cb = {x for x in b.colonna if x != '?'}
            print('  segni comuni %s-%s: %d' % (a.nome, b.nome, len(ca & cb)))


if __name__ == '__main__':
    main()
