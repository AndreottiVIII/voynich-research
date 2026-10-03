# e244 — Gli scribi hanno procedimenti diversi?

Caratteristiche del procedimento per pagina (riuso, operatore di variante, 12 scelte di riga); accuratezza di una regressione logistica contro 200 permutazioni dentro gli strati. Preregistrazione: `preregistrazioni/e244.md`.

| prova | pagine | accuratezza | nullo | z | p |
|---|---|---|---|---|---|
| controllo positivo (lingua dentro la sezione) | 183 | 0.990 | 0.712 | 10.3 | 0.0050 |
| mani dentro lingua x sezione | 183 | 0.789 | 0.806 | -0.8 | 0.8060 |

Mani: {np.str_('1'): 101, np.str_('2'): 45, np.str_('5'): 7, np.str_('3'): 30}. Strati (lingua|sezione) con più di una mano: {'B|H': {np.str_('2'): 20, np.str_('5'): 6, np.str_('3'): 6}, 'B|T': {np.str_('5'): 1, np.str_('2'): 4}}.

Caratteristiche più pesanti per le mani: scelta d interna (0.90), scelta d iniziale (0.72), scelta ch iniziale (0.63), R (0.58), scelta t interna (0.41), scelta e interna (0.41), op +i interna (0.40), scelta cth iniziale (0.39), op −i interna (0.38), scelta y finale (0.34).

Esito: **nessuna differenza oltre lingua e sezione**.
