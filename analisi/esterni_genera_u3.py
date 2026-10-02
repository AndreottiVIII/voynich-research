# -*- coding: utf-8 -*-
"""Genera il testo dei generatori U2 e U3 di Whitehatnetizen/voynich-investigation (commit ccd5db0), riga per riga,
con le stesse impostazioni del loro scripts/u3_generator.py (seme 1492), e lo scrive per l'e134.

Si esegue con l'ambiente del loro repository (numpy, scipy, rapidfuzz), non con quello di questo progetto:
    dati/cache/generatori_esterni/.venv_vi/Scripts/python analisi/esterni_genera_u3.py
Prima vanno costruiti i loro dati: scripts/fetch_voynich.py (dal file ZL3b-n.txt incluso) e la serie voynich_eva.
"""
import os, sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni', 'voynich-investigation')
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import numpy as np
import seriesio as S
import generate_model as GM
import generation_tournament as GT
import u3_generator as U3

OUT = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni')


def main():
    v_lines = U3.voynich_lines(U3.N)
    line_lens = np.array([len(l) for l in v_lines if l])
    mk = GM.fit_markov(S.load_tokens('voynich_eva'))
    cont = GT.fit_cont(mk)
    GT.VOY_LENS = np.array([len(w) for w in S.load_tokens('voynich_eva')])
    u2, _ = GT.gen_u2(mk, cont, np.random.default_rng(U3.SEED), U3.SIZES, U3.W, U3.P_COPY, U3.OVERLAP)
    u2_lines = U3.typeset(u2, line_lens, np.random.default_rng(U3.SEED))
    _, u3_lines = U3.gen_u3(mk, cont, np.random.default_rng(U3.SEED), U3.SIZES, line_lens)
    for nome, righe in (('u2', u2_lines), ('u3', u3_lines)):
        with open(os.path.join(OUT, '%s_righe.txt' % nome), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(' '.join(r) for r in righe if r) + '\n')
        print(nome, len(righe), sum(len(r) for r in righe))


if __name__ == '__main__':
    main()
