# IA36 (ia36) — Scelta prudente e memoria di sezione

Preregistrazione: `preregistrazioni/ia36.md`. Solo numeri e aggregati.

## Oracolo del mondo `struttura2`

**Verdetto: irraggiungibile** (pavimento valido: True; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b. Misure tenute fuori che l'oracolo non rifa: R_rel, ini_par, hapax; il gemello: nessuna.

| giudice | oracolo | errore | riconosciuto | netto (2 errori) |
|---|---|---|---|---|
| N | 0.748 | 0.046 | si | si |
| KN | 0.790 | 0.051 | si | si |
| b | 0.794 | 0.015 | si | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.748 | 0.790 | 0.794 |
| 2 | 0.823 | 0.847 | 0.809 |

## Mondo `struttura2`

Protezione: accesa. Partenza: neutro (il punto di IA35 non e' prudente (penalita' di guardia 2.25 > 0.25): si parte dal migliore per obiettivo prudente). Ciclo di 10 generazioni; scelto **media_finale** (minimo dell'obiettivo prudente fra i 5 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 4.283, penalita' di guardia 0.05 (neutro: obiettivo 5.019).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 4.574 | 4.574 | 0.00 | 7.713 | 0.234 |
| 1 | 4.922 | 4.859 | 0.03 | 7.829 | 0.225 |
| 2 | 5.024 | 4.818 | 0.10 | 6.499 | 0.218 |
| 3 | 4.701 | 4.701 | 0.00 | 6.672 | 0.208 |
| 4 | 4.404 | 4.404 | 0.00 | 5.598 | 0.195 |
| 5 | 4.576 | 4.576 | 0.00 | 6.104 | 0.187 |
| 6 | 4.774 | 4.774 | 0.00 | 5.636 | 0.178 |
| 7 | 4.513 | 4.342 | 0.09 | 6.069 | 0.162 |
| 8 | 4.152 | 4.152 | 0.00 | 6.110 | 0.155 |
| 9 | 4.631 | 4.631 | 0.00 | 6.042 | 0.150 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.019 | 0.00 | 0.00 | 5.019 | 1.6 | 2.4 | -1.2 | 1.7 | -1.2 |
| ia35_C | 4.758 | 2.14 | 2.30 | 9.366 | 1.5 | -1.5 | 11.0 | -4.6 | 3.1 |
| ia33_C | 5.833 | 0.12 | 0.00 | 6.075 | 0.6 | 1.8 | 1.8 | -1.1 | 0.2 |
| media_finale | 4.283 | 0.00 | 0.05 | 4.378 | 0.5 | 0.8 | -2.4 | 0.7 | 1.5 |
| migliore_di_sempre | 4.251 | 0.00 | 0.09 | 4.422 | 1.1 | 2.0 | -1.6 | 3.2 | -0.3 |
| migliore_ultima | 4.687 | 0.00 | 0.05 | 4.784 | 0.5 | 0.2 | -2.4 | -0.8 | 1.4 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.3, g_lung_par 1.8, g_nov_pagine -0.3, g_bigr_rip 0.3, g_zipf -1.0

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -20.2 | 3.1 | -2.6 | 1.6 | -3.9 | 5.5 | -15.1 | 0.6 | -0.1 | 10.0 | 9.8 | 5.1 | -1.9 |
| ia35_C | -5.6 | -1.9 | 4.3 | -1.8 | -1.7 | -1.6 | -17.5 | -2.0 | 2.7 | 6.2 | 8.3 | 4.8 | -12.5 |
| ia33_C | -20.3 | -3.2 | -5.7 | 0.5 | -8.2 | 4.5 | -20.0 | 1.0 | -0.1 | 9.6 | 9.6 | 5.9 | -4.4 |
| media_finale | -20.1 | 0.9 | -5.1 | -0.2 | -3.5 | -2.0 | -18.9 | 0.1 | -0.1 | 9.4 | 9.4 | 1.9 | 0.4 |
| migliore_di_sempre | -19.3 | -0.1 | -3.6 | -0.1 | -3.9 | -1.2 | -18.5 | -0.8 | -0.1 | 9.1 | 9.0 | 3.3 | 0.6 |
| migliore_ultima | -20.3 | -0.2 | -5.6 | -0.0 | -4.7 | -3.4 | -21.5 | 0.6 | -0.1 | 9.7 | 9.7 | 2.1 | 1.1 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 0.962 | 1.000 | 1.000 |
| T_int | 0.893 | 1.000 | 1.000 |
| T_fine | 1.095 | 1.000 | 1.000 |
| T_eol | 0.866 | 1.000 | 1.000 |
| T_riga | 1.075 | 1.000 | 1.000 |
| top_p | 1.000 | 1.000 | 1.000 |
| w_cont | 4.324 | 0.000 | 0.000 |
| w_tri | 0.000 | 0.000 | 0.000 |
| w_quad | 0.000 | 0.000 | 0.000 |
| s | 0.280 | 0.000 | 0.000 |
| w_uni | 0.000 | 0.000 | 0.000 |
| w_bi | 1.050 | 0.000 | 0.000 |
| b_nuove | -0.769 | 0.000 | 0.000 |
| w_pag | 0.096 | 0.000 | 0.000 |
| w_sez | 0.130 | 0.000 | 0.000 |
| t_sez | 12.006 | 10.954 | 10.954 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.761 (0.046) | 0.767 (0.051) | 0.745 (0.020) | 0.50 | burst, sezione, lag23, ttr_pagina, hapax | ok |
| bestN | 8 | 0.754 (0.046) | 0.759 (0.051) | 0.700 (0.019) | 0.50 | burst, sezione, lag23, ttr_pagina, hapax | ok |
| ia35C | 8 | 0.250 (0.046) | 0.623 (0.051) | 0.647 (0.015) | 0.20 | R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| neuC | 4 | 0.947 (0.046) | 0.739 (0.052) | 0.887 (0.039) | 0.40 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| ia33C | 8 | 0.205 (0.046) | 0.742 (0.051) | 0.573 (0.018) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas1 | 4 | 0.824 (0.046) | 0.890 (0.051) | 0.768 (0.016) | 0.33 | burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 1.000 (0.046) | 0.996 (0.051) | 0.999 (0.022) | 0.22 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.974 (0.046) | 0.952 (0.051) | 0.965 (0.022) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| orac | 16 | 0.748 (0.046) | 0.790 (0.051) | 0.794 (0.015) | 0.70 | R_rel, ini_par, hapax | ok |
| orac2 | 8 | 0.823 (0.046) | 0.847 (0.051) | 0.809 (0.027) | 0.67 | heaps, ini_par, ttr_pagina | ok |
| gem | 16 | 0.506 (0.046) | 0.470 (0.053) | 0.455 (0.015) | 1.00 | - | ok |

Misure tenute fuori, `best` (z in sigma): D 0.6, R_rel -0.6, heaps -0.8, burst 10.2, riga_cv -0.5, sezione -3.3, lag23 -4.2, ini_par 0.1, ttr_pagina 11.0, hapax 16.8

Misure tenute fuori, `bestN` (z in sigma): D 0.8, R_rel -0.9, heaps -1.1, burst 10.6, riga_cv -0.6, sezione -3.4, lag23 -4.3, ini_par -0.4, ttr_pagina 11.4, hapax 17.7

Misure tenute fuori, `ia35C` (z in sigma): D -0.5, R_rel -6.2, heaps 4.8, burst -22.5, riga_cv 0.2, sezione -10.1, lag23 19.4, ini_par 2.4, ttr_pagina -9.7, hapax 5.0

Misure tenute fuori, `ia33C` (z in sigma): D 0.7, R_rel -0.6, heaps 3.5, burst 15.3, riga_cv -0.5, sezione -8.8, lag23 -7.5, ini_par -4.6, ttr_pagina 15.6, hapax 23.3

Misure tenute fuori, `neuC` (z in sigma): D -0.6, R_rel 0.7, heaps 2.5, burst 13.0, riga_cv 0.6, sezione 2.4, lag23 -5.7, ini_par -1.2, ttr_pagina 14.0, hapax 23.8

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 0.6, g_lung_par 0.9, g_nov_pagine -2.3, g_bigr_rip 0.6, g_zipf 0.8, riuso_sez -0.3

Guardie e riuso_sez, `bestN` (z in sigma): g_rig_parole 0.6, g_lung_par 0.8, g_nov_pagine -1.7, g_bigr_rip 0.2, g_zipf 0.9, riuso_sez -1.6

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 1.4, g_lung_par -1.3, g_nov_pagine 11.0, g_bigr_rip -5.1, g_zipf 3.0, riuso_sez -14.3

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.6, g_lung_par 2.9, g_nov_pagine -0.7, g_bigr_rip 1.8, g_zipf -1.7, riuso_sez -4.9

Guardie e riuso_sez, `gem` (z in sigma): g_rig_parole 0.0, g_lung_par 0.5, g_nov_pagine 1.2, g_bigr_rip -0.7, g_zipf 0.9, riuso_sez -0.2

Guardie e riuso_sez, `orac` (z in sigma): g_rig_parole 0.0, g_lung_par 1.1, g_nov_pagine 3.1, g_bigr_rip -5.6, g_zipf 1.0, riuso_sez 1.2

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: burst, sezione, lag23, ttr_pagina, hapax; copia superata: False.

## Mondo `vero`

Protezione: accesa. Partenza: ia35 (il punto di IA35 e' prudente (penalita' di guardia 0.25 <= 0.25)). Ciclo di 10 generazioni; scelto **media_finale** (minimo dell'obiettivo prudente fra i 5 finalisti prudenti (penalita' di guardia <= 0.25)): obiettivo 1.921, penalita' di guardia 0.00 (neutro: obiettivo 3.417).

| generazione | valore minimo | obiettivo del minimo | penalita' di guardia | media | passo CMA-ES |
|---|---|---|---|---|---|
| 0 | 2.091 | 2.091 | 0.00 | 5.895 | 0.232 |
| 1 | 1.937 | 1.809 | 0.06 | 3.576 | 0.214 |
| 2 | 2.150 | 2.076 | 0.04 | 3.762 | 0.199 |
| 3 | 2.606 | 2.606 | 0.00 | 3.220 | 0.185 |
| 4 | 2.296 | 2.296 | 0.00 | 3.142 | 0.174 |
| 5 | 2.529 | 2.229 | 0.15 | 3.624 | 0.169 |
| 6 | 2.346 | 2.346 | 0.00 | 3.492 | 0.161 |
| 7 | 2.102 | 2.002 | 0.05 | 2.817 | 0.154 |
| 8 | 2.128 | 1.934 | 0.10 | 2.581 | 0.145 |
| 9 | 1.913 | 1.913 | 0.00 | 2.709 | 0.141 |

| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | g_rig_parole | g_lung_par | g_nov_pagine | g_bigr_rip | g_zipf (z in sigma, libro intero) |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 3.417 | 0.00 | 0.00 | 3.417 | 1.6 | 2.7 | -0.2 | 2.3 | -1.3 |
| ia35_C | 1.695 | 0.27 | 0.14 | 2.234 | 1.0 | 1.8 | 2.7 | 1.2 | -1.0 |
| ia33_C | 1.939 | 0.19 | 0.49 | 2.912 | 0.7 | 1.9 | 3.1 | 4.6 | -1.2 |
| media_finale | 1.921 | 0.00 | 0.00 | 1.921 | 0.7 | 2.1 | 0.9 | 1.2 | -1.1 |
| migliore_di_sempre | 2.178 | 0.06 | 0.00 | 2.295 | 0.7 | 2.0 | 2.0 | -0.8 | -0.7 |
| migliore_grezzo | 2.023 | 0.00 | 0.00 | 2.026 | 1.5 | 2.0 | 1.9 | 2.1 | -1.1 |
| migliore_ultima | 2.160 | 0.02 | 0.00 | 2.199 | 0.6 | 2.1 | 1.9 | -0.9 | -0.9 |

z di guardia delle manopole neutre (fissano il permesso): g_rig_parole 1.0, g_lung_par 1.8, g_nov_pagine -0.5, g_bigr_rip 1.5, g_zipf -0.9

| finalista | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K | riuso_sez |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | -4.7 | 1.6 | -5.8 | 0.8 | 2.3 | -0.2 | -0.9 | 3.2 | -1.1 | 7.6 | 8.3 | 3.5 | 1.1 |
| ia35_C | -0.5 | -0.5 | -3.5 | -1.3 | -0.9 | 0.6 | -0.2 | -0.1 | -1.2 | 3.1 | 4.8 | 1.7 | -1.9 |
| ia33_C | 1.8 | -0.0 | -0.4 | 0.0 | -1.2 | -1.3 | 1.7 | 1.4 | 0.6 | 4.1 | 5.6 | 3.1 | -1.4 |
| media_finale | -1.8 | -0.3 | -4.7 | -0.1 | -1.6 | -0.9 | 0.6 | 0.4 | -1.2 | 3.9 | 5.5 | 2.1 | -0.3 |
| migliore_di_sempre | -1.8 | -1.3 | -5.2 | -0.7 | -0.9 | 0.2 | -0.8 | -0.2 | -1.4 | 3.9 | 6.3 | 2.1 | -1.3 |
| migliore_grezzo | -1.4 | 1.3 | -2.9 | -0.5 | -2.6 | -0.4 | 0.9 | 1.1 | -0.8 | 3.7 | 5.2 | 2.9 | -0.8 |
| migliore_ultima | -1.3 | -1.3 | -5.4 | -0.5 | -0.6 | 0.3 | -0.4 | 0.1 | -1.5 | 4.0 | 6.4 | 2.7 | -1.1 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 0.860 | 1.000 | 0.874 |
| T_int | 0.833 | 1.000 | 0.842 |
| T_fine | 1.018 | 1.000 | 1.088 |
| T_eol | 1.166 | 1.000 | 1.205 |
| T_riga | 0.712 | 1.000 | 0.972 |
| top_p | 1.000 | 1.000 | 0.954 |
| w_cont | 0.000 | 0.000 | 1.506 |
| w_tri | 2.486 | 0.000 | 5.219 |
| w_quad | 6.948 | 0.000 | 6.481 |
| s | 0.703 | 0.000 | 1.000 |
| w_uni | 0.199 | 0.000 | 1.049 |
| w_bi | 0.753 | 0.000 | 0.347 |
| b_nuove | 0.477 | 0.000 | 0.695 |
| w_pag | 0.183 | 0.000 | 0.274 |
| w_sez | 0.032 | 0.000 | 0.000 |
| t_sez | 15.153 | 10.954 | 10.954 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.395 (0.047) | 0.652 (0.056) | 0.647 (0.026) | 0.70 | burst, sezione, lag23 | ok |
| bestN | 8 | 0.396 (0.047) | 0.654 (0.056) | 0.643 (0.023) | 0.70 | burst, sezione, lag23 | ok |
| ia35C | 8 | 0.294 (0.048) | 0.649 (0.056) | 0.600 (0.020) | 0.80 | sezione, hapax | ok |
| neuC | 4 | 0.944 (0.047) | 0.749 (0.056) | 0.749 (0.026) | 0.60 | burst, riga_cv, lag23, ttr_pagina | ok |
| ia33C | 8 | 0.358 (0.047) | 0.724 (0.056) | 0.639 (0.023) | 0.50 | burst, sezione, lag23, ini_par, ttr_pagina | ok |
| cas1 | 4 | 0.784 (0.048) | 0.872 (0.056) | 0.657 (0.029) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.993 (0.047) | 0.993 (0.056) | 0.915 (0.029) | 0.22 | D, heaps, burst, riga_cv, sezione, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.785 (0.047) | 0.870 (0.056) | 0.702 (0.010) | 0.22 | D, burst, riga_cv, sezione, lag23, ini_par, hapax | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.609 (0.021) | | | | |

Misure tenute fuori, `best` (z in sigma): D 1.2, R_rel -1.7, heaps 0.5, burst 4.4, riga_cv 0.7, sezione -4.2, lag23 -3.3, ini_par -1.8, ttr_pagina -0.1, hapax 0.7

Misure tenute fuori, `bestN` (z in sigma): D 1.6, R_rel -1.6, heaps 0.5, burst 4.4, riga_cv 0.7, sezione -4.4, lag23 -3.5, ini_par -1.9, ttr_pagina -0.2, hapax 1.0

Misure tenute fuori, `ia35C` (z in sigma): D 0.6, R_rel -1.9, heaps 1.3, burst 1.7, riga_cv 0.8, sezione -5.2, lag23 -1.4, ini_par 1.4, ttr_pagina -1.5, hapax 2.4

Misure tenute fuori, `ia33C` (z in sigma): D 1.9, R_rel -1.0, heaps 0.7, burst -2.7, riga_cv 0.4, sezione -4.9, lag23 3.0, ini_par -3.7, ttr_pagina -4.3, hapax -1.1

Misure tenute fuori, `neuC` (z in sigma): D 1.6, R_rel -1.2, heaps 0.8, burst 6.2, riga_cv 2.1, sezione 1.4, lag23 -4.3, ini_par -1.9, ttr_pagina 2.7, hapax 0.9

Guardie e riuso_sez, `best` (z in sigma): g_rig_parole 0.7, g_lung_par 2.2, g_nov_pagine 1.0, g_bigr_rip 1.0, g_zipf -1.1, riuso_sez 0.1

Guardie e riuso_sez, `bestN` (z in sigma): g_rig_parole 0.7, g_lung_par 2.1, g_nov_pagine 1.0, g_bigr_rip 1.2, g_zipf -1.2, riuso_sez 0.0

Guardie e riuso_sez, `ia35C` (z in sigma): g_rig_parole 1.0, g_lung_par 1.7, g_nov_pagine 2.8, g_bigr_rip 1.1, g_zipf -1.0, riuso_sez -1.5

Guardie e riuso_sez, `neuC` (z in sigma): g_rig_parole 1.6, g_lung_par 2.7, g_nov_pagine -0.1, g_bigr_rip 2.4, g_zipf -1.5, riuso_sez 1.5

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: burst, sezione, lag23; copia superata: False.

## Che cosa porta la memoria di sezione (stesso punto, con e senza `w_sez`)

Mondo `struttura2`: w_sez 0.130, t_sez 12.0 pagine. Giudici (con / senza memoria): N 0.761 / 0.754, KN 0.767 / 0.759, b 0.745 / 0.700; misure tenute fuori z: D 0.6 / 0.8, R_rel -0.6 / -0.9, burst 10.2 / 10.6, hapax 16.8 / 17.7, heaps -0.8 / -1.1, ini_par 0.1 / -0.4, lag23 -4.2 / -4.3, riga_cv -0.5 / -0.6, sezione -3.3 / -3.4, ttr_pagina 11.0 / 11.4; riuso_sez z: -0.3 / -1.6

Mondo `vero`: w_sez 0.032, t_sez 15.2 pagine. Giudici (con / senza memoria): N 0.395 / 0.396, KN 0.652 / 0.654, b 0.647 / 0.643; misure tenute fuori z: D 1.2 / 1.6, R_rel -1.7 / -1.6, burst 4.4 / 4.4, hapax 0.7 / 1.0, heaps 0.5 / 0.5, ini_par -1.8 / -1.9, lag23 -3.3 / -3.5, riga_cv 0.7 / 0.7, sezione -4.2 / -4.4, ttr_pagina -0.1 / -0.2; riuso_sez z: 0.1 / 0.0

