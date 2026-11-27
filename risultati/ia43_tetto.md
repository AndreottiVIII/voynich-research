# IA43 — Il tetto al messaggio

Preregistrazione: `preregistrazioni/ia43.md`. Solo numeri. Messaggio in chiaro piantato nel v21; la batteria vede un libro se almeno k misure valide superano la soglia dei libri senza messaggio; il tetto di una cella e' la dose piu' bassa da cui in su almeno 11 libri su 12 sono visti.

## Controlli

- Controllo positivo (forma a, 1 alternativa, 100%): batteria vede **12** libri su 12: **passato**.
- Recupero con la chiave (forma a, 100%): chiave giusta 0,992, chiave sbagliata 0,000.
- k (misure valide da superare): forma a: tutte 4, solo M 4; forma b: tutte 4, solo M 4; forma c: tutte 4, solo M 4; forma z: tutte 4, solo M 4.
- Falsi allarmi dei libri senza messaggio (uno fuori): forma a: 0,000; forma b: 0,000; forma c: 0,000; forma z: 0,000.
- Misure valide per forma: a: 25; b: 23; c: 20; z: 25.

## Per cella: libri visti su 12, per dose

| cella | 1% | 2% | 5% | 10% | 20% | 40% | 70% | 100% | tetto | lettura | tetto con le sole misure M |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a1 | 1 | 9 | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| a3 | · | · | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| a10 | · | · | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| b1 | 0 | 5 | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| b3 | · | · | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,10 |
| b6 | · | · | 11 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,10 |
| c1 | 2 | 7 | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| c3 | · | · | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |
| c10 | · | · | 12 | 12 | 12 | 12 | 12 | 12 | 0,05 | tetto basso (5%) | 0,05 |

`·` = dose non provata per quella cella (le dosi 1 e 2% si provano solo con 1 alternativa).

## Controllo di sostituzione (come a, ma parole del messaggio rimescolate su tutto il libro)

| dose | libri visti (batteria) | solo M |
|---|---|---|
| 2% | 7 | 4 |
| 5% | 12 | 12 |
| 10% | 12 | 12 |
| 20% | 12 | 12 |
| 40% | 12 | 12 |
| 100% | 12 | 12 |

## Voynich

- forma a: 5 misure M oltre la soglia (heaps, sezione, hapax, T4g, T4r), k_M 4: **visto**.
- forma b: 7 misure M oltre la soglia (heaps, sezione, ttr_pagina, hapax, doppie, T4g, T4r), k_M 4: **visto**.
- forma c: 5 misure M oltre la soglia (heaps, sezione, hapax, T4g, T4r), k_M 4: **visto**.
- forma z: 5 misure M oltre la soglia (heaps, sezione, hapax, T4g, T4r), k_M 4: **visto**.

Trascrizione di Takahashi (stesse misure M): forma a: 4 oltre la soglia (visto); forma b: 6 oltre la soglia (visto); forma c: 4 oltre la soglia (visto); forma z: 4 oltre la soglia (visto).

