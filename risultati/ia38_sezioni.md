# IA38 (ia38) — Giudici e sezioni insieme

Preregistrazione: `preregistrazioni/ia38.md`. Solo numeri e aggregati.

## Oracolo del mondo `struttura2`

**Verdetto: irraggiungibile** (pavimento valido: True; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b. Misure tenute fuori che l'oracolo non rifa: R_rel, ini_par, hapax; il gemello: nessuna.

| giudice | oracolo | errore | riconosciuto | netto (2 errori) |
|---|---|---|---|---|
| N | 0.750 | 0.046 | si | si |
| KN | 0.792 | 0.051 | si | si |
| b | 0.805 | 0.013 | si | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.750 | 0.792 | 0.805 |
| 2 | 0.803 | 0.837 | 0.802 |

## Mondo `struttura2`

Protezione: accesa. Partenza: ia37 (punto di IA37: prudente (penalita' di guardia 0.00 <= 0.25) e con il migliore obiettivo prudente fra i punti di IA37 e IA35 prudenti). Ciclo di 10 generazioni; scelto **migliore_ultima** (minimo dell'obiettivo prudente fra i 7 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 3.421, penalita' di guardia 0.00 (neutro: obiettivo 4.655).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 4.444 | 3.877 | 0.28 | 8.345 | 0.228 |
| 1 | 4.047 | 4.047 | 0.00 | 6.775 | 0.212 |
| 2 | 4.038 | 4.038 | 0.00 | 6.481 | 0.202 |
| 3 | 3.635 | 3.635 | 0.00 | 5.392 | 0.188 |
| 4 | 3.569 | 3.569 | 0.00 | 5.146 | 0.174 |
| 5 | 4.202 | 4.125 | 0.04 | 5.146 | 0.162 |
| 6 | 3.558 | 3.558 | 0.00 | 4.465 | 0.151 |
| 7 | 3.518 | 3.518 | 0.00 | 4.976 | 0.145 |
| 8 | 3.660 | 3.660 | 0.00 | 4.481 | 0.142 |
| 9 | 3.578 | 3.462 | 0.06 | 4.378 | 0.143 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 4.655 | 0.00 | 0.00 | 4.655 | 1.6 | 2.3 | -0.3 | 1.9 | -0.9 |
| ia37_C | 3.842 | 0.00 | 0.00 | 3.842 | 0.4 | 0.3 | -1.4 | -0.1 | 1.6 |
| ia35_C | 4.411 | 2.01 | 2.68 | 9.767 | 1.5 | -0.8 | 11.4 | -5.6 | 3.2 |
| ia33_C | 5.518 | 0.05 | 0.00 | 5.616 | 0.4 | 1.6 | 1.9 | -0.7 | 0.8 |
| media_finale | 3.402 | 0.00 | 0.18 | 3.754 | 0.8 | -0.0 | -0.1 | 3.8 | -1.1 |
| migliore_di_sempre | 3.466 | 0.00 | 0.00 | 3.466 | 1.3 | -0.3 | 1.0 | 2.6 | -0.7 |
| migliore_grezzo | 3.516 | 0.00 | 0.05 | 3.609 | 1.4 | -1.3 | 2.2 | 2.2 | -0.6 |
| migliore_ultima | 3.421 | 0.00 | 0.00 | 3.421 | 1.4 | -1.2 | 2.0 | 2.5 | -0.0 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.3, g_lung_par 1.6, g_nov_pagine -0.4, g_bigr_rip 0.4, g_zipf -1.3

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez | div_bigr | div_par |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -20.3 | 3.0 | -2.8 | 1.5 | -4.4 | 5.5 | -21.1 | 0.3 | -0.5 | 10.0 | 9.8 | 4.6 | -1.9 | -1.6 | -1.4 |
| ia37_C | -18.9 | 0.7 | -2.3 | 0.0 | -2.4 | -5.2 | -14.9 | 0.7 | -0.5 | 6.9 | 8.0 | 3.9 | 0.5 | -3.1 | -1.3 |
| ia35_C | -5.8 | -1.9 | 4.0 | -1.9 | -1.1 | -1.4 | -17.9 | -2.2 | 0.5 | 6.8 | 8.5 | 4.3 | -12.5 | -2.0 | -3.1 |
| ia33_C | -20.4 | -3.5 | -5.7 | -0.0 | -8.2 | 4.7 | -22.5 | 1.1 | -0.5 | 9.5 | 9.5 | 5.7 | -4.3 | -4.1 | -4.3 |
| media_finale | -16.8 | -0.1 | -0.6 | -0.8 | -0.3 | -0.3 | -15.7 | -0.7 | -0.5 | 7.6 | 7.9 | 5.0 | -0.9 | -2.7 | -0.4 |
| migliore_di_sempre | -16.2 | 0.6 | 0.1 | -0.4 | -1.4 | -0.5 | -16.0 | -1.0 | -0.5 | 7.0 | 7.5 | 5.1 | -1.6 | -2.7 | -0.7 |
| migliore_grezzo | -14.9 | 0.1 | 0.4 | -0.9 | -0.9 | 0.7 | -15.7 | -1.4 | -0.5 | 6.9 | 7.7 | 5.1 | -2.7 | -2.5 | -0.7 |
| migliore_ultima | -15.2 | -0.2 | 0.2 | -1.0 | -0.5 | 0.4 | -17.0 | -1.1 | -0.5 | 6.9 | 7.6 | 4.7 | -2.4 | -2.6 | -0.6 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.043 | 1.000 | 1.031 |
| T_int | 0.740 | 1.000 | 0.878 |
| T_fine | 1.254 | 1.000 | 1.175 |
| T_eol | 1.041 | 1.000 | 0.703 |
| T_riga | 1.120 | 1.000 | 1.087 |
| top_p | 1.000 | 1.000 | 0.887 |
| w_cont | 7.500 | 0.000 | 6.298 |
| w_tri | 0.382 | 0.000 | 0.000 |
| w_quad | 0.000 | 0.000 | 0.000 |
| s | 0.721 | 0.000 | 0.246 |
| w_uni | 0.000 | 0.000 | 0.000 |
| w_bi | 2.335 | 0.000 | 2.394 |
| b_nuove | -0.403 | 0.000 | -0.806 |
| w_pag | 0.495 | 0.000 | 0.283 |
| w_sez | 0.000 | 0.000 | 0.000 |
| t_sez | 10.954 | 10.954 | 10.954 |
| a_sez | 0.729 | 0.000 | 0.544 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.782 (0.046) | 0.760 (0.051) | 0.806 (0.017) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| ia37C | 8 | 0.886 (0.046) | 0.808 (0.051) | 0.774 (0.013) | 0.50 | heaps, sezione, lag23, ttr_pagina, hapax | ok |
| ia35C | 8 | 0.249 (0.046) | 0.637 (0.052) | 0.616 (0.028) | 0.20 | R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| neuC | 4 | 0.949 (0.046) | 0.726 (0.052) | 0.890 (0.031) | 0.40 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| ia33C | 8 | 0.209 (0.046) | 0.738 (0.051) | 0.592 (0.018) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas1 | 4 | 0.703 (0.047) | 0.756 (0.051) | 0.713 (0.016) | 0.33 | burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.999 (0.046) | 0.987 (0.051) | 0.986 (0.019) | 0.33 | heaps, burst, sezione, ini_par, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.887 (0.046) | 0.905 (0.051) | 0.895 (0.034) | 0.33 | burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| orac | 16 | 0.750 (0.046) | 0.792 (0.051) | 0.805 (0.013) | 0.70 | R_rel, ini_par, hapax | ok |
| orac2 | 8 | 0.803 (0.046) | 0.837 (0.051) | 0.802 (0.021) | 0.67 | heaps, ini_par, ttr_pagina | ok |
| gem | 16 | 0.491 (0.046) | 0.484 (0.052) | 0.456 (0.014) | 1.00 | - | ok |

Misure tenute fuori, `best` (z in sigma): D 0.4, R_rel -0.6, heaps 2.7, burst -14.9, riga_cv 0.5, sezione -3.2, lag23 14.0, ini_par 2.8, ttr_pagina -5.9, hapax 17.5

Misure tenute fuori, `ia37C` (z in sigma): D -0.1, R_rel -0.2, heaps -4.0, burst -0.9, riga_cv -0.8, sezione -2.2, lag23 3.2, ini_par -1.0, ttr_pagina 2.8, hapax 13.1

Misure tenute fuori, `ia35C` (z in sigma): D -0.5, R_rel -6.8, heaps 4.8, burst -22.2, riga_cv 0.4, sezione -10.1, lag23 19.6, ini_par 2.8, ttr_pagina -9.9, hapax 5.0

Misure tenute fuori, `ia33C` (z in sigma): D 0.7, R_rel -0.3, heaps 3.9, burst 15.0, riga_cv -0.5, sezione -8.5, lag23 -7.4, ini_par -4.5, ttr_pagina 15.5, hapax 23.4

Misure tenute fuori, `neuC` (z in sigma): D 0.2, R_rel 0.0, heaps 2.7, burst 12.3, riga_cv 0.6, sezione 2.9, lag23 -6.0, ini_par -1.9, ttr_pagina 13.9, hapax 24.2

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 1.4, g_lung_par -1.3, g_nov_pagine 2.1, g_bigr_rip 2.2, g_zipf -0.3, riuso_sez -3.5

Guardie e riuso_sez, `ia37C` (z in sigma): g_rig_parole 0.2, g_lung_par 0.4, g_nov_pagine -1.3, g_bigr_rip 0.3, g_zipf 2.1, riuso_sez 0.5

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 1.5, g_lung_par -1.1, g_nov_pagine 11.2, g_bigr_rip -5.1, g_zipf 3.4, riuso_sez -14.4

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.5, g_lung_par 2.5, g_nov_pagine -0.8, g_bigr_rip 2.0, g_zipf -1.6, riuso_sez -4.7

Guardie e riuso_sez, `gem` (z in sigma): g_rig_parole 0.0, g_lung_par 0.6, g_nov_pagine 1.4, g_bigr_rip -0.5, g_zipf 1.0, riuso_sez -0.2

Guardie e riuso_sez, `orac` (z in sigma): g_rig_parole 0.0, g_lung_par 0.8, g_nov_pagine 3.1, g_bigr_rip -5.7, g_zipf 1.2, riuso_sez 1.0

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax; copia superata: False.

## Mondo `vero`

Protezione: accesa. Partenza: ia37 (punto di IA37: prudente (penalita' di guardia 0.00 <= 0.25) e con il migliore obiettivo prudente fra i punti di IA37 e IA35 prudenti). Ciclo di 10 generazioni; scelto **ia37_C** (minimo dell'obiettivo prudente fra i 6 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 1.847, penalita' di guardia 0.00 (neutro: obiettivo 3.067).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 2.453 | 2.453 | 0.00 | 3.648 | 0.227 |
| 1 | 2.353 | 2.353 | 0.00 | 3.711 | 0.211 |
| 2 | 2.434 | 2.434 | 0.00 | 3.117 | 0.199 |
| 3 | 2.509 | 2.509 | 0.00 | 2.874 | 0.182 |
| 4 | 2.033 | 2.033 | 0.00 | 2.774 | 0.172 |
| 5 | 2.175 | 2.144 | 0.02 | 2.793 | 0.165 |
| 6 | 2.303 | 2.145 | 0.08 | 2.632 | 0.154 |
| 7 | 1.912 | 1.912 | 0.00 | 2.650 | 0.141 |
| 8 | 1.897 | 1.897 | 0.00 | 2.437 | 0.136 |
| 9 | 2.070 | 1.959 | 0.06 | 2.590 | 0.135 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 3.067 | 0.00 | 0.00 | 3.067 | 1.6 | 2.5 | -0.4 | 2.3 | -1.4 |
| ia37_C | 1.847 | 0.00 | 0.00 | 1.847 | 0.8 | 1.9 | 0.7 | 1.1 | -1.0 |
| ia35_C | 1.872 | 0.22 | 0.17 | 2.305 | 0.9 | 1.8 | 2.9 | 1.2 | -1.2 |
| ia33_C | 1.864 | 0.31 | 0.44 | 2.743 | 0.6 | 1.8 | 2.8 | 4.7 | -1.4 |
| media_finale | 1.852 | 0.00 | 0.00 | 1.852 | 0.7 | 2.2 | 1.4 | 2.2 | -0.9 |
| migliore_di_sempre | 1.952 | 0.00 | 0.00 | 1.952 | 1.2 | 1.8 | 1.4 | 0.4 | -0.6 |
| migliore_ultima | 1.845 | 0.03 | 0.00 | 1.902 | 0.9 | 2.6 | 1.7 | 2.6 | -1.7 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.4, g_lung_par 1.9, g_nov_pagine -0.0, g_bigr_rip 1.2, g_zipf -0.8

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez | div_bigr | div_par |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -4.7 | 1.9 | -5.9 | 0.5 | 2.5 | -0.3 | -2.9 | 3.1 | 0.2 | 7.5 | 8.1 | 3.5 | 1.1 | -0.8 | -0.7 |
| ia37_C | -2.0 | -0.7 | -3.5 | -0.2 | -0.4 | 0.0 | 0.8 | 0.3 | 0.0 | 3.6 | 5.3 | 3.0 | -0.5 | -1.8 | -2.8 |
| ia35_C | -0.4 | -0.3 | -3.5 | -1.2 | -0.8 | 0.4 | -1.4 | 0.1 | 0.2 | 3.1 | 5.0 | 2.1 | -1.9 | -2.1 | -3.0 |
| ia33_C | 1.8 | 0.2 | 0.1 | 0.2 | -1.3 | -1.2 | 1.2 | 1.4 | 1.4 | 3.6 | 5.0 | 3.3 | -1.2 | -1.7 | -2.9 |
| media_finale | -2.3 | -0.9 | -3.1 | 0.2 | -0.5 | -0.2 | 0.1 | 0.3 | 0.0 | 3.8 | 4.9 | 2.9 | -0.7 | -1.8 | -2.5 |
| migliore_di_sempre | -3.5 | -0.7 | -3.0 | 0.1 | -0.5 | -0.8 | 1.2 | 0.6 | 0.7 | 3.6 | 5.2 | 2.3 | -0.8 | -2.0 | -2.5 |
| migliore_ultima | 0.3 | -0.6 | -2.5 | 0.1 | -0.7 | 1.4 | -0.1 | 0.4 | 0.9 | 4.2 | 4.9 | 2.7 | -1.2 | -1.8 | -2.3 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.005 | 1.000 | 1.005 |
| T_int | 0.672 | 1.000 | 0.672 |
| T_fine | 1.103 | 1.000 | 1.103 |
| T_eol | 1.254 | 1.000 | 1.254 |
| T_riga | 0.744 | 1.000 | 0.744 |
| top_p | 1.000 | 1.000 | 1.000 |
| w_cont | 1.525 | 0.000 | 1.525 |
| w_tri | 4.470 | 0.000 | 4.470 |
| w_quad | 4.651 | 0.000 | 4.651 |
| s | 0.798 | 0.000 | 0.798 |
| w_uni | 0.000 | 0.000 | 0.000 |
| w_bi | 1.441 | 0.000 | 1.441 |
| b_nuove | 0.719 | 0.000 | 0.719 |
| w_pag | 0.162 | 0.000 | 0.162 |
| w_sez | 0.000 | 0.000 | 0.000 |
| t_sez | 10.954 | 10.954 | 10.954 |
| a_sez | 0.000 | 0.000 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.387 (0.047) | 0.668 (0.056) | 0.656 (0.018) | 0.50 | burst, sezione, lag23, ini_par, hapax | ok |
| ia37C | 8 | 0.389 (0.048) | 0.666 (0.056) | 0.638 (0.019) | 0.50 | burst, sezione, lag23, ini_par, hapax | ok |
| ia35C | 8 | 0.294 (0.048) | 0.649 (0.056) | 0.610 (0.021) | 0.80 | sezione, hapax | ok |
| neuC | 4 | 0.947 (0.048) | 0.737 (0.057) | 0.753 (0.017) | 0.50 | burst, riga_cv, lag23, ini_par, ttr_pagina | ok |
| ia33C | 8 | 0.361 (0.047) | 0.719 (0.056) | 0.631 (0.018) | 0.50 | burst, sezione, lag23, ini_par, ttr_pagina | ok |
| cas1 | 4 | 1.000 (0.047) | 0.999 (0.056) | 0.997 (0.031) | 0.00 | D, heaps, burst, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.666 (0.048) | 0.744 (0.056) | 0.683 (0.029) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.932 (0.047) | 0.963 (0.056) | 0.757 (0.025) | 0.33 | D, heaps, burst, lag23, ini_par, hapax | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.609 (0.021) | | | | |

Misure tenute fuori, `best` (z in sigma): D 1.2, R_rel -1.6, heaps 0.9, burst 3.5, riga_cv 0.7, sezione -4.6, lag23 -2.5, ini_par -2.0, ttr_pagina -0.8, hapax 2.3

Misure tenute fuori, `ia37C` (z in sigma): D 1.1, R_rel -1.6, heaps 0.9, burst 3.5, riga_cv 0.8, sezione -4.6, lag23 -2.5, ini_par -2.0, ttr_pagina -0.8, hapax 2.1

Misure tenute fuori, `ia35C` (z in sigma): D 0.8, R_rel -1.8, heaps 1.4, burst 1.4, riga_cv 0.7, sezione -5.4, lag23 -1.1, ini_par 1.7, ttr_pagina -1.7, hapax 2.5

Misure tenute fuori, `ia33C` (z in sigma): D 1.8, R_rel -1.1, heaps 0.7, burst -2.7, riga_cv 0.5, sezione -4.8, lag23 3.0, ini_par -3.5, ttr_pagina -4.4, hapax -1.0

Misure tenute fuori, `neuC` (z in sigma): D 1.2, R_rel -0.9, heaps 0.6, burst 6.1, riga_cv 2.1, sezione 1.5, lag23 -4.2, ini_par -2.0, ttr_pagina 3.0, hapax 1.2

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 0.8, g_lung_par 1.9, g_nov_pagine 1.1, g_bigr_rip 0.9, g_zipf -1.1, riuso_sez -0.1

Guardie e riuso_sez, `ia37C` (z in sigma): g_rig_parole 0.9, g_lung_par 1.9, g_nov_pagine 1.2, g_bigr_rip 0.9, g_zipf -1.1, riuso_sez -0.1

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 0.9, g_lung_par 1.8, g_nov_pagine 3.0, g_bigr_rip 1.3, g_zipf -1.1, riuso_sez -1.6

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.6, g_lung_par 2.9, g_nov_pagine 0.1, g_bigr_rip 2.1, g_zipf -1.4, riuso_sez 1.3

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: burst, sezione, lag23, ini_par, hapax; copia superata: False.

## Che cosa cambia vedendo le sezioni nell'obiettivo (`best` contro `ia37C`) e la diagnosi

Mondo `struttura2`: a_sez 0.729. Giudici (IA38 / IA37): N 0.782 / 0.886, KN 0.760 / 0.808, b 0.806 / 0.774; misure tenute fuori z (IA38 / IA37; **`sezione` in parte insegnata**): D 0.4 / -0.1, R_rel -0.6 / -0.2, burst -14.9 / -0.9, hapax 17.5 / 13.1, heaps 2.7 / -4.0, ini_par 2.8 / -1.0, lag23 14.0 / 3.2, riga_cv 0.5 / -0.8, sezione -3.2 / -2.2 (insegnata), ttr_pagina -5.9 / 2.8

Le altre nove misure entro 2 sigma (senza `sezione`): best 3 su 9; ia37C 5 su 9; ia35C 2 su 9; neuC 4 su 9; ia33C 3 su 9; orac 6 su 9; orac2 5 su 8; gem 9 su 9. `sezione` z: best -3.2, ia37C -2.2, ia35C -10.1, neuC 2.9, ia33C -8.5, orac -0.1, orac2 -1.4, gem -1.1

Divergenza fra sezioni (bit; bigrammi di glifi / parole): best 0.0499 / 0.1933; ia37C 0.0464 / 0.1683; ia35C 0.0499 / 0.1402; neuC 0.0603 / 0.1788; ia33C 0.0368 / 0.0964; orac 0.0810 / 0.2571; orac2 0.0771 / 0.2370; gem 0.0761 / 0.2310; vero 0.0735 / 0.2291

Mondo `vero`: a_sez 0.000. Giudici (IA38 / IA37): N 0.387 / 0.389, KN 0.668 / 0.666, b 0.656 / 0.638; misure tenute fuori z (IA38 / IA37; **`sezione` in parte insegnata**): D 1.2 / 1.1, R_rel -1.6 / -1.6, burst 3.5 / 3.5, hapax 2.3 / 2.1, heaps 0.9 / 0.9, ini_par -2.0 / -2.0, lag23 -2.5 / -2.5, riga_cv 0.7 / 0.8, sezione -4.6 / -4.6 (insegnata), ttr_pagina -0.8 / -0.8

Le altre nove misure entro 2 sigma (senza `sezione`): best 5 su 9; ia37C 5 su 9; ia35C 8 su 9; neuC 4 su 9; ia33C 5 su 9. `sezione` z: best -4.6, ia37C -4.6, ia35C -5.4, neuC 1.5, ia33C -4.8

Divergenza fra sezioni (bit; bigrammi di glifi / parole): best 0.0492 / 0.1252; ia37C 0.0493 / 0.1249; ia35C 0.0437 / 0.1102; neuC 0.0633 / 0.2001; ia33C 0.0525 / 0.1256; vero 0.0678 / 0.2077

## La curva del compromesso (frontiera fra la parte giudici e la parte sezioni dell'obiettivo)

Mondo `struttura2`: 152 candidati; frontiera (nessun altro candidato e' migliore su entrambe):

| blocco | gen | i | nome | J (giudici) | S (sezioni) | obiettivo | a_sez |
|---|---|---|---|---|---|---|---|
| ciclo | 7 | 10 | - | 5.47 | 2.23 | 3.73 | 0.51 |
| ciclo | 6 | 8 | - | 5.74 | 1.96 | 3.89 | 0.44 |
| ciclo | 6 | 2 | - | 5.82 | 1.80 | 3.56 | 0.44 |
| ciclo | 7 | 4 | - | 5.88 | 1.49 | 4.00 | 0.16 |
| ciclo | 7 | 9 | - | 6.22 | 1.10 | 3.93 | 0.21 |
| ciclo | 8 | 0 | - | 6.66 | 0.91 | 4.10 | 0.08 |
| ciclo | 5 | 8 | - | 7.31 | 0.70 | 4.68 | 0.17 |

Mondo `vero`: 149 candidati; frontiera (nessun altro candidato e' migliore su entrambe):

| blocco | gen | i | nome | J (giudici) | S (sezioni) | obiettivo | a_sez |
|---|---|---|---|---|---|---|---|
| finalisti | 901 | 5 | migliore_di_sempre | 3.35 | 2.29 | 1.94 | 0.34 |
| finalisti | 901 | 1 | ia37_C | 3.45 | 2.19 | 1.76 | 0.00 |
| finalisti | 902 | 4 | media_finale | 3.63 | 2.17 | 1.91 | 0.17 |
| finalisti | 902 | 5 | migliore_di_sempre | 3.65 | 2.07 | 1.94 | 0.34 |
| finalisti | 901 | 6 | migliore_ultima | 3.67 | 2.00 | 1.81 | 0.15 |
| ciclo | 7 | 3 | - | 3.83 | 1.73 | 2.22 | 0.32 |
| ciclo | 4 | 5 | - | 4.57 | 1.47 | 2.09 | 0.00 |
| ciclo | 5 | 9 | - | 5.05 | 1.21 | 2.36 | 0.00 |
| ciclo | 5 | 0 | - | 5.17 | 1.05 | 2.57 | 0.00 |
| ciclo | 6 | 10 | - | 6.14 | 0.46 | 2.43 | 0.26 |

