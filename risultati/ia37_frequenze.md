# IA37 (ia37) — Frequenze per sezione

Preregistrazione: `preregistrazioni/ia37.md`. Solo numeri e aggregati.

## Oracolo del mondo `struttura2`

**Verdetto: irraggiungibile** (pavimento valido: True; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b. Misure tenute fuori che l'oracolo non rifa: ini_par, hapax; il gemello: nessuna.

| giudice | oracolo | errore | riconosciuto | netto (2 errori) |
|---|---|---|---|---|
| N | 0.751 | 0.046 | si | si |
| KN | 0.796 | 0.051 | si | si |
| b | 0.786 | 0.012 | si | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.751 | 0.796 | 0.786 |
| 2 | 0.807 | 0.837 | 0.803 |

## Mondo `struttura2`

Protezione: accesa. Partenza: ia36 (il punto di IA35 e' prudente (penalita' di guardia 0.00 <= 0.25)). Ciclo di 10 generazioni; scelto **media_finale** (minimo dell'obiettivo prudente fra i 6 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 4.044, penalita' di guardia 0.00 (neutro: obiettivo 5.170).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 5.266 | 4.679 | 0.29 | 7.271 | 0.229 |
| 1 | 4.569 | 4.569 | 0.00 | 6.138 | 0.210 |
| 2 | 4.792 | 4.792 | 0.00 | 5.902 | 0.200 |
| 3 | 4.916 | 4.809 | 0.05 | 6.342 | 0.188 |
| 4 | 4.800 | 4.800 | 0.00 | 5.475 | 0.178 |
| 5 | 4.430 | 4.324 | 0.05 | 5.739 | 0.177 |
| 6 | 4.411 | 4.411 | 0.00 | 5.649 | 0.167 |
| 7 | 4.232 | 4.227 | 0.00 | 5.537 | 0.153 |
| 8 | 4.249 | 3.978 | 0.14 | 5.294 | 0.142 |
| 9 | 4.188 | 4.129 | 0.03 | 4.905 | 0.139 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.170 | 0.00 | 0.00 | 5.170 | 1.7 | 1.8 | -1.1 | 2.6 | -1.7 |
| ia36_C | 4.319 | 0.00 | 0.00 | 4.319 | 0.7 | 1.1 | -1.4 | -0.4 | 1.1 |
| ia35_C | 4.667 | 2.04 | 2.20 | 9.074 | 1.4 | -1.3 | 11.2 | -5.2 | 2.9 |
| ia33_C | 5.736 | 0.14 | 0.00 | 6.007 | 0.4 | 1.4 | 1.8 | -1.5 | 0.6 |
| media_finale | 4.044 | 0.00 | 0.00 | 4.044 | 0.3 | 0.4 | -1.0 | 0.5 | 2.1 |
| migliore_di_sempre | 3.965 | 0.00 | 0.14 | 4.250 | 0.2 | 0.8 | -1.1 | 0.3 | 3.4 |
| migliore_grezzo | 4.046 | 0.72 | 1.18 | 6.399 | 0.3 | 1.3 | -1.2 | 9.5 | -1.4 |
| migliore_ultima | 4.108 | 0.02 | 0.22 | 4.538 | 0.2 | 0.9 | -0.8 | -0.5 | 3.8 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.3, g_lung_par 1.9, g_nov_pagine -0.8, g_bigr_rip 0.3, g_zipf -0.7

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -20.1 | 2.3 | -3.0 | 1.6 | -4.3 | 5.7 | -22.5 | 0.0 | -0.1 | 10.0 | 9.8 | 5.1 | -2.2 |
| ia36_C | -19.9 | 0.6 | -5.3 | 0.2 | -3.6 | -1.8 | -13.6 | 0.8 | -0.1 | 9.5 | 9.5 | 2.6 | -0.8 |
| ia35_C | -5.2 | -2.0 | 4.2 | -1.7 | -1.3 | -1.5 | -17.3 | -1.9 | 3.4 | 5.9 | 8.4 | 4.4 | -12.9 |
| ia33_C | -20.1 | -3.6 | -5.7 | 0.5 | -8.2 | 4.4 | -19.4 | 1.0 | -0.1 | 9.6 | 9.6 | 6.0 | -4.6 |
| media_finale | -18.6 | 0.7 | -2.7 | -0.0 | -2.1 | -5.1 | -16.6 | 0.4 | -0.0 | 6.6 | 7.5 | 3.9 | 0.4 |
| migliore_di_sempre | -18.3 | 1.1 | -2.2 | 0.1 | -0.8 | -6.7 | -13.5 | 1.0 | -0.0 | 5.7 | 7.1 | 4.0 | 0.9 |
| migliore_grezzo | -14.2 | 0.4 | 1.3 | -0.5 | -2.5 | -3.7 | -17.3 | 0.2 | -0.0 | 6.4 | 6.7 | 6.5 | 1.1 |
| migliore_ultima | -18.5 | 1.1 | -2.1 | 0.1 | -0.7 | -6.9 | -18.0 | 1.0 | -0.0 | 5.9 | 7.3 | 4.0 | 1.0 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.031 | 1.000 | 0.962 |
| T_int | 0.878 | 1.000 | 0.893 |
| T_fine | 1.175 | 1.000 | 1.095 |
| T_eol | 0.703 | 1.000 | 0.866 |
| T_riga | 1.087 | 1.000 | 1.075 |
| top_p | 0.887 | 1.000 | 1.000 |
| w_cont | 6.298 | 0.000 | 4.324 |
| w_tri | 0.000 | 0.000 | 0.000 |
| w_quad | 0.000 | 0.000 | 0.000 |
| s | 0.246 | 0.000 | 0.280 |
| w_uni | 0.000 | 0.000 | 0.000 |
| w_bi | 2.394 | 0.000 | 1.050 |
| b_nuove | -0.806 | 0.000 | -0.769 |
| w_pag | 0.283 | 0.000 | 0.096 |
| w_sez | 0.000 | 0.000 | 0.000 |
| t_sez | 10.954 | 10.954 | 10.954 |
| a_sez | 0.544 | 0.000 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.888 (0.046) | 0.808 (0.051) | 0.796 (0.008) | 0.50 | heaps, sezione, lag23, ttr_pagina, hapax | ok |
| bestG | 8 | 0.891 (0.046) | 0.830 (0.051) | 0.785 (0.031) | 0.60 | sezione, lag23, ttr_pagina, hapax | ok |
| ia36C | 8 | 0.750 (0.046) | 0.763 (0.051) | 0.711 (0.019) | 0.50 | burst, sezione, lag23, ttr_pagina, hapax | ok |
| ia35C | 8 | 0.249 (0.046) | 0.649 (0.052) | 0.585 (0.022) | 0.20 | R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| neuC | 4 | 0.946 (0.046) | 0.730 (0.051) | 0.906 (0.031) | 0.40 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| ia33C | 8 | 0.211 (0.046) | 0.739 (0.051) | 0.597 (0.020) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas1 | 4 | 0.421 (0.046) | 0.799 (0.051) | 0.649 (0.021) | 0.22 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.711 (0.046) | 0.842 (0.051) | 0.725 (0.017) | 0.56 | burst, lag23, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.999 (0.046) | 0.994 (0.051) | 0.997 (0.028) | 0.33 | heaps, burst, lag23, ini_par, ttr_pagina, hapax | ok |
| orac | 16 | 0.751 (0.046) | 0.796 (0.051) | 0.786 (0.012) | 0.80 | ini_par, hapax | ok |
| orac2 | 8 | 0.807 (0.046) | 0.837 (0.051) | 0.803 (0.013) | 0.67 | heaps, ini_par, ttr_pagina | ok |
| gem | 16 | 0.502 (0.046) | 0.462 (0.052) | 0.466 (0.012) | 1.00 | - | ok |

Misure tenute fuori, `best` (z in sigma): D -0.1, R_rel 0.3, heaps -4.2, burst -1.3, riga_cv -0.8, sezione -2.2, lag23 2.8, ini_par -1.3, ttr_pagina 3.1, hapax 13.1

Misure tenute fuori, `bestG` (z in sigma): D -0.4, R_rel -1.1, heaps -1.0, burst -0.2, riga_cv -1.0, sezione -5.0, lag23 2.3, ini_par -1.2, ttr_pagina 3.2, hapax 12.5

Misure tenute fuori, `ia36C` (z in sigma): D 0.8, R_rel -0.2, heaps -0.9, burst 10.9, riga_cv -0.6, sezione -3.8, lag23 -4.5, ini_par -0.6, ttr_pagina 11.6, hapax 17.6

Misure tenute fuori, `ia35C` (z in sigma): D -0.2, R_rel -6.1, heaps 4.6, burst -22.6, riga_cv 0.3, sezione -10.0, lag23 19.5, ini_par 2.7, ttr_pagina -9.9, hapax 5.2

Misure tenute fuori, `ia33C` (z in sigma): D 0.2, R_rel -0.9, heaps 4.1, burst 14.7, riga_cv -0.5, sezione -8.4, lag23 -7.4, ini_par -4.9, ttr_pagina 15.3, hapax 23.4

Misure tenute fuori, `neuC` (z in sigma): D 0.3, R_rel 0.3, heaps 2.8, burst 12.8, riga_cv 0.6, sezione 2.9, lag23 -5.0, ini_par -1.4, ttr_pagina 13.8, hapax 24.1

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 0.2, g_lung_par 0.5, g_nov_pagine -1.2, g_bigr_rip 0.2, g_zipf 2.3, riuso_sez 0.5

Guardie e riuso_sez, `bestG` (z in sigma): g_rig_parole 0.2, g_lung_par 1.0, g_nov_pagine -1.3, g_bigr_rip -1.1, g_zipf 2.7, riuso_sez 0.2

Guardie e riuso_sez, `ia36C` (z in sigma): g_rig_parole 0.5, g_lung_par 0.7, g_nov_pagine -1.6, g_bigr_rip -0.1, g_zipf 1.2, riuso_sez -1.6

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 1.5, g_lung_par -1.3, g_nov_pagine 11.2, g_bigr_rip -4.9, g_zipf 3.2, riuso_sez -14.3

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.7, g_lung_par 2.1, g_nov_pagine -0.9, g_bigr_rip 1.8, g_zipf -0.8, riuso_sez -4.9

Guardie e riuso_sez, `gem` (z in sigma): g_rig_parole 0.0, g_lung_par 0.3, g_nov_pagine 1.3, g_bigr_rip -0.4, g_zipf 0.9, riuso_sez -0.2

Guardie e riuso_sez, `orac` (z in sigma): g_rig_parole 0.0, g_lung_par 0.9, g_nov_pagine 3.2, g_bigr_rip -5.9, g_zipf 1.1, riuso_sez 1.1

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: heaps, sezione, lag23, ttr_pagina, hapax; copia superata: False.

## Mondo `vero`

Protezione: accesa. Partenza: ia36 (il punto di IA35 e' prudente (penalita' di guardia 0.00 <= 0.25)). Ciclo di 10 generazioni; scelto **migliore_di_sempre** (minimo dell'obiettivo prudente fra i 6 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 1.821, penalita' di guardia 0.00 (neutro: obiettivo 3.328).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 2.519 | 2.338 | 0.09 | 3.851 | 0.225 |
| 1 | 2.204 | 2.163 | 0.02 | 4.035 | 0.214 |
| 2 | 2.000 | 2.000 | 0.00 | 3.291 | 0.204 |
| 3 | 2.286 | 1.945 | 0.17 | 3.023 | 0.189 |
| 4 | 1.933 | 1.683 | 0.13 | 3.052 | 0.171 |
| 5 | 1.625 | 1.625 | 0.00 | 2.394 | 0.159 |
| 6 | 1.792 | 1.792 | 0.00 | 2.595 | 0.149 |
| 7 | 2.072 | 2.072 | 0.00 | 2.448 | 0.145 |
| 8 | 1.745 | 1.745 | 0.00 | 2.234 | 0.141 |
| 9 | 1.982 | 1.982 | 0.00 | 2.675 | 0.126 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 3.328 | 0.00 | 0.00 | 3.328 | 1.7 | 2.4 | -0.2 | 2.9 | -1.4 |
| ia36_C | 1.923 | 0.00 | 0.00 | 1.923 | 0.7 | 2.3 | 1.1 | 1.0 | -0.9 |
| ia35_C | 1.733 | 0.23 | 0.21 | 2.201 | 0.9 | 1.8 | 3.0 | 0.9 | -1.0 |
| ia33_C | 1.982 | 0.22 | 0.34 | 2.654 | 0.8 | 1.8 | 2.9 | 4.6 | -1.3 |
| media_finale | 1.848 | 0.00 | 0.00 | 1.848 | 0.8 | 2.0 | 0.6 | 1.1 | -0.6 |
| migliore_di_sempre | 1.821 | 0.00 | 0.00 | 1.821 | 0.9 | 2.0 | 1.1 | 0.9 | -1.1 |
| migliore_ultima | 1.990 | 0.00 | 0.00 | 1.990 | 0.9 | 1.9 | 1.2 | 0.7 | -0.8 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.1, g_lung_par 1.9, g_nov_pagine -0.0, g_bigr_rip 1.5, g_zipf -1.1

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -4.9 | 1.4 | -5.8 | 0.8 | 3.0 | -0.1 | 0.1 | 3.3 | 0.1 | 7.8 | 8.2 | 4.0 | 0.9 |
| ia36_C | -2.2 | -0.0 | -4.3 | 0.1 | -1.9 | -1.0 | -0.4 | 1.2 | -0.1 | 3.1 | 4.9 | 1.7 | -0.4 |
| ia35_C | -0.2 | -0.5 | -3.3 | -1.3 | -0.7 | 0.6 | -0.3 | -0.1 | -0.1 | 3.0 | 4.7 | 2.2 | -2.0 |
| ia33_C | 1.9 | 0.1 | 0.0 | 0.2 | -1.1 | -1.4 | 1.4 | 1.7 | 2.2 | 3.7 | 5.4 | 3.0 | -1.2 |
| media_finale | -2.9 | -0.1 | -3.4 | 0.0 | 0.3 | -1.2 | 0.3 | 0.4 | 0.1 | 3.1 | 5.1 | 2.7 | -0.4 |
| migliore_di_sempre | -2.1 | -0.6 | -3.5 | -0.3 | -0.3 | -0.0 | 0.4 | -0.0 | 0.3 | 3.4 | 5.1 | 3.3 | -0.6 |
| migliore_ultima | -1.9 | -0.7 | -4.1 | -0.0 | 1.1 | -0.9 | -0.1 | 0.3 | 0.2 | 3.6 | 5.4 | 3.2 | -0.9 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.005 | 1.000 | 0.860 |
| T_int | 0.672 | 1.000 | 0.833 |
| T_fine | 1.103 | 1.000 | 1.018 |
| T_eol | 1.254 | 1.000 | 1.166 |
| T_riga | 0.744 | 1.000 | 0.712 |
| top_p | 1.000 | 1.000 | 1.000 |
| w_cont | 1.525 | 0.000 | 0.000 |
| w_tri | 4.470 | 0.000 | 2.486 |
| w_quad | 4.651 | 0.000 | 6.948 |
| s | 0.798 | 0.000 | 0.703 |
| w_uni | 0.000 | 0.000 | 0.199 |
| w_bi | 1.441 | 0.000 | 0.753 |
| b_nuove | 0.719 | 0.000 | 0.477 |
| w_pag | 0.162 | 0.000 | 0.183 |
| w_sez | 0.000 | 0.000 | 0.000 |
| t_sez | 10.954 | 10.954 | 10.954 |
| a_sez | 0.000 | 0.000 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.390 (0.047) | 0.663 (0.056) | 0.666 (0.020) | 0.60 | burst, sezione, lag23, hapax | ok |
| bestG | 8 | 0.387 (0.048) | 0.664 (0.056) | 0.652 (0.026) | 0.70 | burst, sezione, lag23 | ok |
| ia36C | 8 | 0.397 (0.047) | 0.653 (0.056) | 0.620 (0.017) | 0.60 | burst, sezione, lag23, ini_par | ok |
| ia35C | 8 | 0.297 (0.047) | 0.653 (0.056) | 0.635 (0.028) | 0.80 | sezione, hapax | ok |
| neuC | 4 | 0.944 (0.047) | 0.724 (0.057) | 0.769 (0.025) | 0.60 | burst, riga_cv, lag23, ttr_pagina | ok |
| ia33C | 8 | 0.359 (0.047) | 0.731 (0.056) | 0.634 (0.026) | 0.50 | burst, sezione, lag23, ini_par, ttr_pagina | ok |
| cas1 | 4 | 0.993 (0.047) | 0.976 (0.056) | 0.937 (0.030) | 0.22 | D, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.828 (0.048) | 0.798 (0.056) | 0.748 (0.029) | 0.44 | D, burst, sezione, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.997 (0.047) | 0.989 (0.056) | 0.885 (0.024) | 0.33 | D, heaps, riga_cv, sezione, ttr_pagina, hapax | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.609 (0.021) | | | | |

Misure tenute fuori, `best` (z in sigma): D 1.3, R_rel -1.6, heaps 0.8, burst 3.6, riga_cv 0.7, sezione -4.6, lag23 -2.5, ini_par -1.7, ttr_pagina -0.8, hapax 2.1

Misure tenute fuori, `bestG` (z in sigma): D 1.0, R_rel -1.1, heaps 0.7, burst 3.4, riga_cv 0.7, sezione -4.5, lag23 -2.6, ini_par -2.0, ttr_pagina -0.8, hapax 1.9

Misure tenute fuori, `ia36C` (z in sigma): D 1.5, R_rel -1.6, heaps 0.7, burst 4.4, riga_cv 0.6, sezione -4.2, lag23 -3.3, ini_par -2.3, ttr_pagina -0.1, hapax 0.9

Misure tenute fuori, `ia35C` (z in sigma): D 0.7, R_rel -2.0, heaps 1.4, burst 2.0, riga_cv 0.8, sezione -5.4, lag23 -1.7, ini_par 1.4, ttr_pagina -1.6, hapax 2.1

Misure tenute fuori, `ia33C` (z in sigma): D 1.9, R_rel -1.8, heaps 0.6, burst -2.8, riga_cv 0.4, sezione -4.9, lag23 3.0, ini_par -3.7, ttr_pagina -4.3, hapax -0.9

Misure tenute fuori, `neuC` (z in sigma): D 1.3, R_rel -0.9, heaps 0.8, burst 6.2, riga_cv 2.1, sezione 1.3, lag23 -4.6, ini_par -1.9, ttr_pagina 3.1, hapax 0.6

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 0.8, g_lung_par 1.9, g_nov_pagine 1.0, g_bigr_rip 1.0, g_zipf -1.2, riuso_sez -0.1

Guardie e riuso_sez, `bestG` (z in sigma): g_rig_parole 0.9, g_lung_par 2.0, g_nov_pagine 1.0, g_bigr_rip 1.1, g_zipf -1.1, riuso_sez 0.0

Guardie e riuso_sez, `ia36C` (z in sigma): g_rig_parole 0.6, g_lung_par 2.2, g_nov_pagine 1.2, g_bigr_rip 1.1, g_zipf -1.0, riuso_sez 0.0

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 1.1, g_lung_par 1.8, g_nov_pagine 2.8, g_bigr_rip 1.2, g_zipf -1.1, riuso_sez -1.6

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.6, g_lung_par 2.7, g_nov_pagine 0.1, g_bigr_rip 2.2, g_zipf -1.3, riuso_sez 1.3

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: burst, sezione, lag23, hapax; copia superata: False.

## Che cosa portano le frequenze per sezione (stesso punto, con e senza `a_sez`) e la diagnosi

Mondo `struttura2`: a_sez 0.544, ripiego K 300 (la tabella di sezione batte la globale in validazione: True). Giudici (con / senza): N 0.888 / 0.891, KN 0.808 / 0.830, b 0.796 / 0.785; misure tenute fuori z: D -0.1 / -0.4, R_rel 0.3 / -1.1, burst -1.3 / -0.2, hapax 13.1 / 12.5, heaps -4.2 / -1.0, ini_par -1.3 / -1.2, lag23 2.8 / 2.3, riga_cv -0.8 / -1.0, sezione -2.2 / -5.0, ttr_pagina 3.1 / 3.2

Divergenza fra sezioni (bit; bigrammi di glifi / parole): best 0.0469 / 0.1698; bestG 0.0505 / 0.1577; ia36C 0.0485 / 0.1523; ia35C 0.0513 / 0.1422; neuC 0.0596 / 0.1770; ia33C 0.0368 / 0.0964; orac 0.0811 / 0.2558; orac2 0.0777 / 0.2357; gem 0.0759 / 0.2291; vero 0.0735 / 0.2291

Mondo `vero`: a_sez 0.000, ripiego K 300 (la tabella di sezione batte la globale in validazione: True). Giudici (con / senza): N 0.390 / 0.387, KN 0.663 / 0.664, b 0.666 / 0.652; misure tenute fuori z: D 1.3 / 1.0, R_rel -1.6 / -1.1, burst 3.6 / 3.4, hapax 2.1 / 1.9, heaps 0.8 / 0.7, ini_par -1.7 / -2.0, lag23 -2.5 / -2.6, riga_cv 0.7 / 0.7, sezione -4.6 / -4.5, ttr_pagina -0.8 / -0.8

Divergenza fra sezioni (bit; bigrammi di glifi / parole): best 0.0485 / 0.1241; bestG 0.0496 / 0.1256; ia36C 0.0474 / 0.1255; ia35C 0.0433 / 0.1117; neuC 0.0628 / 0.2005; ia33C 0.0517 / 0.1253; vero 0.0678 / 0.2077

