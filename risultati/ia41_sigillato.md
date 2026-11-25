# IA41 (ia41) — Esame sigillato su divisioni nuove dei fogli

Preregistrazione: `preregistrazioni/ia41.md`. Mondo `vero`. Solo numeri e aggregati.

**Esito: IA40 legata alla prima divisione: il risultato non regge su pagine mai viste (criterio 1 o 3 caduto); il compromesso torna.** (media sulle divisioni nuove: 1 (seme 4101), 2 (seme 4102), 3 (seme 4103), 4 (seme 4104); giudice b valido: True, `neu` b 0.891)

## Criteri (scritti prima)

| criterio | esito | numeri |
|---|---|---|
| 1. b di `s100k30` sotto `t100` in almeno 3 divisioni su 4 e di almeno 0,02 in media | no | sotto in 2 su 4; differenza media -0.011; b `s100k30` 0.682, 0.718, 0.576, 0.677; b `t100` 0.624, 0.740, 0.597, 0.648 |
| 2. b medio fra 0,40 e 0,60 (0,60-0,65 = pari col v21) | no | b medio 0.663; pari col v21: False; b v21 0.555 |
| 3. `sezione` entro 2σ (σ = rumore di campionamento) | SI | z medio -1.5 (strumento valido: True) |
| 4. almeno 5 delle altre 7 misure vecchie entro 2σ | SI | dentro: heaps, burst, riga_cv, lag23, ini_par, ttr_pagina, hapax; fuori: - |
| 5. sorprese fra 0,40 e 0,60 e indovina-sezione entro 2 errori | no | avanti 0.462 (FUORI), indietro 0.584 (FUORI), indovina-sezione finto 0.899 contro vero 0.809 (differenza 0.090, errore 0.063, valido) |
| 6. almeno 2/3 delle misure nuove valide entro 2σ | no | dentro: lunghezza, doppie, testa; fuori: dispersione, vicine; usciti dal verdetto: lingua; `lingua` z 1.4 (previsione scritta: fallisce) |

## Strumenti e difetti piantati

Strumenti che vedono il loro difetto (gli altri escono dal verdetto): sezione si, lingua NO, vicine si, indovina si, b si, avanti NO, indietro NO.

Pagine rimescolate (z medio, in unita' di rumore): heaps 0.5, burst 1.3, riga_cv 2.3, sezione -3.6, lag23 -1.5, ini_par 1.4, ttr_pagina 0.3, hapax 0.2, lingua -2.4, dispersione -2.4, vicine -4.8, lunghezza 0.0, doppie 0.5, testa 0.0; indovina-sezione vero 0.809, pagine rimescolate 0.393.
Meta' righe di `neu` (riga `dif`): b 0.745, sorpresa in avanti 0.518, sorpresa al contrario 0.541.

## Per divisione

| divisione | riga | b | avanti | indietro | indovina | `sezione` z | pagine tenute fuori |
|---|---|---|---|---|---|---|---|
| 0 | s100k30 | 0.532 (0.020) | 0.392 | 0.643 | 0.792 | -0.9 | 30 |
| 0 | t100 | 0.588 (0.021) | 0.233 | 0.790 | 0.517 | -3.8 | 30 |
| 0 | neu | 0.808 (0.019) | 0.433 | 0.662 | 0.796 | 0.5 | 30 |
| 0 | dif | 0.639 (0.015) | 0.425 | 0.643 | 0.829 | 0.1 | 30 |
| 0 | v21 | 0.641 (0.021) | 0.523 | 0.448 | 0.923 | -0.0 | 30 |
| 1 | s100k30 | 0.682 (0.031) | 0.607 | 0.413 | 0.951 | -4.2 | 28 |
| 1 | t100 | 0.624 (0.019) | 0.473 | 0.536 | 0.661 | -7.5 | 28 |
| 1 | neu | 0.953 (0.031) | 0.652 | 0.679 | 0.951 | -3.6 | 28 |
| 1 | dif | 0.828 (0.021) | 0.638 | 0.423 | 0.951 | -4.0 | 28 |
| 1 | v21 | 0.560 (0.022) | 0.589 | 0.397 | 1.000 | -1.2 | 28 |
| 2 | s100k30 | 0.718 (0.015) | 0.479 | 0.624 | 0.954 | -2.2 | 30 |
| 2 | t100 | 0.740 (0.031) | 0.171 | 0.843 | 0.537 | -4.7 | 30 |
| 2 | neu | 0.922 (0.025) | 0.758 | 0.571 | 0.958 | -0.7 | 30 |
| 2 | dif | 0.774 (0.017) | 0.650 | 0.452 | 0.958 | -1.3 | 30 |
| 2 | v21 | 0.600 (0.028) | 0.527 | 0.437 | 0.993 | 0.3 | 30 |
| 3 | s100k30 | 0.576 (0.024) | 0.392 | 0.635 | 0.810 | -1.4 | 29 |
| 3 | t100 | 0.597 (0.022) | 0.233 | 0.764 | 0.539 | -4.3 | 29 |
| 3 | neu | 0.821 (0.019) | 0.405 | 0.695 | 0.746 | -0.7 | 29 |
| 3 | dif | 0.625 (0.024) | 0.397 | 0.606 | 0.784 | -0.9 | 29 |
| 3 | v21 | 0.477 (0.020) | 0.510 | 0.467 | 0.945 | -0.1 | 29 |
| 4 | s100k30 | 0.677 (0.015) | 0.371 | 0.665 | 0.879 | 1.6 | 32 |
| 4 | t100 | 0.648 (0.019) | 0.191 | 0.808 | 0.722 | -0.7 | 32 |
| 4 | neu | 0.866 (0.016) | 0.383 | 0.759 | 0.883 | -0.2 | 32 |
| 4 | dif | 0.755 (0.020) | 0.387 | 0.683 | 0.907 | 0.8 | 32 |
| 4 | v21 | 0.585 (0.014) | 0.509 | 0.479 | 0.935 | 1.3 | 32 |

Misure (z medio sulle divisioni nuove, in unita' di rumore di campionamento) per `s100k30`, `t100` e v21:

| misura | s100k30 | t100 | v21 |
|---|---|---|---|
| heaps | 0.7 | 0.9 | 0.6 |
| burst | 0.9 | 1.0 | 1.9 |
| riga_cv | 1.7 | 1.1 | 1.8 |
| sezione | -1.5 | -4.3 | 0.1 |
| lag23 | -1.5 | -1.3 | -2.3 |
| ini_par | 1.6 | 0.6 | 2.3 |
| ttr_pagina | 0.5 | 0.0 | 0.9 |
| hapax | 0.6 | -0.4 | -1.9 |
| lingua (nuova) | 1.4 | 0.1 | 1.1 |
| dispersione (nuova) | -2.2 | -2.8 | -0.6 |
| vicine (nuova) | -2.2 | -1.5 | -1.9 |
| lunghezza (nuova) | -0.4 | -1.5 | -0.9 |
| doppie (nuova) | 0.5 | 0.8 | -1.3 |
| testa (nuova) | -1.0 | 0.5 | -0.7 |

Informazione sulla divisione originale (N e KN usano anche pagine studiate: non vanno nel verdetto): s100k30 N 0.351, KN 0.600, D 0.148; t100 N 0.295, KN 0.653, D 0.154; neu N 0.941, KN 0.714, D 0.171.
