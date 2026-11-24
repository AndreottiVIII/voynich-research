# IA35 (ia35) — La rete che sa dove scrive

Preregistrazione: `preregistrazioni/ia35.md`. Solo numeri e aggregati.

## Oracolo del mondo `struttura2`

**Verdetto: irraggiungibile** (pavimento valido: True; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b. Misure tenute fuori che l'oracolo non rifa: R_rel, ini_par, hapax; il gemello: nessuna.

| giudice | oracolo | errore | riconosciuto | netto (2 errori) |
|---|---|---|---|---|
| N | 0.749 | 0.046 | si | si |
| KN | 0.794 | 0.051 | si | si |
| b | 0.788 | 0.015 | si | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.749 | 0.794 | 0.788 |
| 2 | 0.797 | 0.839 | 0.781 |

## Mondo `struttura2`

Ciclo: 10 generazioni, partenza ia33, obiettivo del migliore 4.185 contro 5.414 delle manopole neutre (scelto: migliore_di_sempre).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 5.156 | 6.093 | 0.227 |
| 1 | 5.213 | 5.798 | 0.218 |
| 2 | 4.380 | 5.325 | 0.220 |
| 3 | 4.513 | 5.162 | 0.225 |
| 4 | 4.352 | 5.072 | 0.233 |
| 5 | 4.087 | 5.069 | 0.233 |
| 6 | 4.283 | 5.149 | 0.242 |
| 7 | 4.421 | 5.048 | 0.240 |
| 8 | 4.237 | 4.918 | 0.236 |
| 9 | 4.256 | 4.716 | 0.231 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.414 | -20.2 | 2.9 | -2.7 | 1.9 | -4.0 | 5.7 | -16.0 | 0.0 | -0.3 | 10.0 | 9.9 | 4.7 |
| ia33_C | 5.929 | -20.3 | -3.2 | -5.8 | 0.2 | -8.3 | 4.4 | -24.8 | 1.0 | -0.3 | 9.6 | 9.6 | 5.6 |
| ia33_A | 5.754 | -20.4 | -2.9 | -6.2 | 0.6 | -8.1 | 3.7 | -23.0 | 0.4 | -0.3 | 9.6 | 9.6 | 5.9 |
| media_finale | 4.243 | -10.2 | -1.8 | 1.0 | -2.1 | -0.9 | 0.9 | -16.8 | -1.5 | -0.2 | 7.3 | 8.6 | 4.6 |
| migliore_di_sempre | 4.185 | -5.4 | -1.7 | 4.5 | -1.8 | -1.4 | -1.4 | -17.5 | -1.8 | 1.2 | 6.4 | 8.6 | 4.6 |
| migliore_ultima | 4.371 | -8.7 | -1.5 | 2.1 | -2.1 | -0.2 | 2.8 | -16.9 | -1.9 | -0.0 | 7.4 | 8.8 | 4.3 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.319 | 1.000 | 0.870 |
| T_int | 1.233 | 1.000 | 1.092 |
| T_fine | 1.011 | 1.000 | 0.957 |
| T_eol | 0.632 | 1.000 | 0.820 |
| T_riga | 0.600 | 1.000 | 0.728 |
| top_p | 0.979 | 1.000 | 0.933 |
| w_cont | 5.591 | 0.000 | 1.046 |
| w_tri | 4.765 | 0.000 | 7.348 |
| w_quad | 0.000 | 0.000 | 6.139 |
| s | 1.000 | 0.000 | 0.536 |
| w_uni | 2.227 | 0.000 | 0.000 |
| w_bi | 1.113 | 0.000 | 0.000 |
| b_nuove | -2.000 | 0.000 | 0.046 |
| w_pag | 0.800 | 0.000 | 0.073 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.252 (0.046) | 0.639 (0.051) | 0.644 (0.025) | 0.20 | R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| bestA | 8 | 0.259 (0.046) | 0.658 (0.052) | 0.614 (0.023) | 0.20 | R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| neuC | 4 | 0.951 (0.046) | 0.726 (0.053) | 0.879 (0.031) | 0.40 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| neuA | 4 | 0.927 (0.046) | 0.749 (0.052) | 0.844 (0.026) | 0.50 | heaps, burst, lag23, ttr_pagina, hapax | ok |
| ia33C | 8 | 0.202 (0.046) | 0.744 (0.051) | 0.571 (0.021) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| ia33A | 8 | 0.246 (0.046) | 0.768 (0.052) | 0.538 (0.020) | 0.30 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas1 | 4 | 0.873 (0.046) | 0.897 (0.051) | 0.832 (0.017) | 0.22 | heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.993 (0.046) | 0.995 (0.051) | 0.974 (0.022) | 0.44 | heaps, burst, ini_par, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.999 (0.046) | 0.988 (0.051) | 0.999 (0.024) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| cas4 | 4 | 0.772 (0.046) | 0.885 (0.051) | 0.760 (0.018) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| orac | 16 | 0.749 (0.046) | 0.794 (0.051) | 0.788 (0.015) | 0.70 | R_rel, ini_par, hapax | ok |
| orac2 | 8 | 0.797 (0.046) | 0.839 (0.051) | 0.781 (0.019) | 0.67 | heaps, ini_par, ttr_pagina | ok |
| gem | 16 | 0.506 (0.046) | 0.486 (0.052) | 0.465 (0.018) | 1.00 | - | ok |

Misure tenute fuori, `best` (z in sigma): D -0.4, R_rel -5.9, heaps 4.5, burst -22.1, riga_cv 0.3, sezione -10.0, lag23 19.3, ini_par 2.6, ttr_pagina -9.9, hapax 5.1

Misure tenute fuori, `bestA` (z in sigma): D -0.2, R_rel -6.1, heaps 3.2, burst -21.0, riga_cv 0.2, sezione -10.6, lag23 18.7, ini_par 3.6, ttr_pagina -9.5, hapax 3.9

Misure tenute fuori, `ia33C` (z in sigma): D 0.8, R_rel -0.8, heaps 3.8, burst 15.0, riga_cv -0.5, sezione -8.4, lag23 -7.5, ini_par -4.7, ttr_pagina 15.6, hapax 23.4

Misure tenute fuori, `ia33A` (z in sigma): D 0.6, R_rel -0.5, heaps 3.0, burst 17.4, riga_cv 0.1, sezione -10.0, lag23 -8.4, ini_par -4.1, ttr_pagina 16.0, hapax 22.8

Misure tenute fuori, `neuC` (z in sigma): D -0.1, R_rel 1.0, heaps 2.9, burst 12.4, riga_cv 0.5, sezione 3.0, lag23 -6.3, ini_par -1.2, ttr_pagina 13.9, hapax 24.1

Misure tenute fuori, `neuA` (z in sigma): D 0.2, R_rel 0.5, heaps 3.5, burst 15.7, riga_cv 0.2, sezione -2.0, lag23 -7.7, ini_par -0.3, ttr_pagina 14.5, hapax 24.7

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN, b; misure fuori 2 sigma: R_rel, heaps, burst, sezione, lag23, ini_par, ttr_pagina, hapax; copia superata: False.

## Mondo `vero`

Ciclo: 10 generazioni, partenza ia33, obiettivo del migliore 1.695 contro 3.759 delle manopole neutre (scelto: migliore_di_sempre).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 2.180 | 4.084 | 0.224 |
| 1 | 2.039 | 3.339 | 0.202 |
| 2 | 2.049 | 2.874 | 0.192 |
| 3 | 1.637 | 2.441 | 0.183 |
| 4 | 1.792 | 2.736 | 0.173 |
| 5 | 1.941 | 2.695 | 0.169 |
| 6 | 1.781 | 2.859 | 0.165 |
| 7 | 2.049 | 2.588 | 0.156 |
| 8 | 1.763 | 2.673 | 0.147 |
| 9 | 1.658 | 2.407 | 0.137 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 3.759 | -5.2 | 1.5 | -6.0 | 0.8 | 3.1 | -0.2 | -2.8 | 3.2 | -0.8 | 7.4 | 7.8 | 3.9 |
| ia33_C | 1.913 | 1.4 | 0.1 | 0.0 | 0.2 | -1.2 | -1.4 | 1.5 | 1.6 | 3.3 | 3.4 | 4.6 | 3.4 |
| ia33_A | 2.354 | 1.1 | -0.1 | -2.6 | 0.5 | -1.1 | -1.5 | 2.4 | 1.7 | 2.8 | 4.3 | 5.8 | 3.8 |
| media_finale | 1.818 | -1.6 | 0.4 | -3.2 | -0.2 | 1.3 | -1.0 | 0.2 | 1.1 | -0.4 | 2.9 | 4.7 | 2.9 |
| migliore_di_sempre | 1.695 | -0.3 | -0.4 | -3.5 | -1.3 | -0.7 | 0.6 | -0.3 | -0.1 | -0.8 | 3.3 | 4.9 | 2.1 |
| migliore_ultima | 1.878 | -1.4 | 0.4 | -3.6 | -0.5 | 1.1 | 0.4 | 0.1 | 0.7 | -0.6 | 3.7 | 5.3 | 2.8 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 0.874 | 1.000 | 1.044 |
| T_int | 0.842 | 1.000 | 0.705 |
| T_fine | 1.088 | 1.000 | 1.051 |
| T_eol | 1.205 | 1.000 | 0.770 |
| T_riga | 0.972 | 1.000 | 0.919 |
| top_p | 0.954 | 1.000 | 0.758 |
| w_cont | 1.506 | 0.000 | 1.905 |
| w_tri | 5.219 | 0.000 | 6.274 |
| w_quad | 6.481 | 0.000 | 7.458 |
| s | 1.000 | 0.000 | 1.000 |
| w_uni | 1.049 | 0.000 | 0.915 |
| w_bi | 0.347 | 0.000 | 0.247 |
| b_nuove | 0.695 | 0.000 | 0.582 |
| w_pag | 0.274 | 0.000 | 0.220 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.298 (0.047) | 0.651 (0.056) | 0.632 (0.022) | 0.80 | sezione, hapax | ok |
| bestA | 8 | 0.323 (0.048) | 0.701 (0.057) | 0.621 (0.023) | 0.70 | burst, sezione, lag23 | ok |
| neuC | 4 | 0.943 (0.048) | 0.718 (0.057) | 0.747 (0.022) | 0.50 | burst, riga_cv, lag23, ini_par, ttr_pagina | ok |
| neuA | 4 | 0.962 (0.047) | 0.784 (0.057) | 0.915 (0.044) | 0.50 | burst, lag23, ini_par, ttr_pagina, hapax | ok |
| ia33C | 8 | 0.363 (0.047) | 0.723 (0.056) | 0.631 (0.030) | 0.50 | burst, sezione, lag23, ini_par, ttr_pagina | ok |
| ia33A | 8 | 0.374 (0.047) | 0.775 (0.056) | 0.649 (0.022) | 0.50 | D, sezione, lag23, ini_par, ttr_pagina | ok |
| cas1 | 4 | 0.985 (0.047) | 0.972 (0.056) | 0.878 (0.030) | 0.33 | D, burst, riga_cv, lag23, ttr_pagina, hapax | ok |
| cas2 | 4 | 0.991 (0.047) | 0.891 (0.056) | 0.934 (0.029) | 0.11 | D, burst, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax | ok |
| cas3 | 4 | 0.972 (0.048) | 0.965 (0.056) | 0.782 (0.026) | 0.33 | heaps, burst, sezione, lag23, ttr_pagina, hapax | ok |
| cas4 | 4 | 0.995 (0.047) | 0.989 (0.056) | 0.896 (0.020) | 0.33 | D, heaps, burst, lag23, ini_par, hapax | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.609 (0.021) | | | | |

Misure tenute fuori, `best` (z in sigma): D 0.6, R_rel -1.7, heaps 1.3, burst 1.6, riga_cv 0.8, sezione -5.4, lag23 -1.6, ini_par 1.6, ttr_pagina -1.5, hapax 2.2

Misure tenute fuori, `bestA` (z in sigma): D 1.0, R_rel -1.2, heaps 1.5, burst 2.3, riga_cv -0.3, sezione -5.0, lag23 -2.1, ini_par 1.7, ttr_pagina -1.3, hapax 1.8

Misure tenute fuori, `ia33C` (z in sigma): D 1.7, R_rel -1.4, heaps 0.8, burst -2.8, riga_cv 0.4, sezione -4.8, lag23 3.4, ini_par -3.3, ttr_pagina -4.3, hapax -0.8

Misure tenute fuori, `ia33A` (z in sigma): D 2.5, R_rel -0.9, heaps 0.6, burst -1.2, riga_cv -0.6, sezione -4.5, lag23 2.3, ini_par -2.9, ttr_pagina -3.8, hapax -1.5

Misure tenute fuori, `neuC` (z in sigma): D 1.7, R_rel -0.9, heaps 0.5, burst 5.8, riga_cv 2.1, sezione 1.6, lag23 -4.0, ini_par -2.1, ttr_pagina 2.6, hapax 1.1

Misure tenute fuori, `neuA` (z in sigma): D -1.6, R_rel -1.1, heaps 0.2, burst 12.1, riga_cv 0.1, sezione -0.5, lag23 -9.1, ini_par -2.9, ttr_pagina 3.7, hapax 3.4

**Esito: al livello dell'oracolo** (giudice b valido: True; controllo negativo riuscito: True).

## Che cosa porta il condizionamento (rete condizionata contro ablazione)

Mondo `struttura2`: scelta della rete condizionata sulla validazione (bit per segno, validazione / fuori piega): Ca 2.405 / 2.282; Cb 2.404 / 2.280; Cc 2.407 / 2.293; ablazione 2.396 / 2.290; scelta: Cb; batte l ablazione in validazione: NO

Mondo `struttura2`: perplessita` (bit per segno) C: validazione 2.564, fuori piega 2.412; A: validazione 2.586, fuori piega 2.456

A manopole `best`: giudici (condizionata / ablazione) N 0.252 / 0.259, KN 0.639 / 0.658, b 0.644 / 0.614; misure tenute fuori z: D -0.4 / -0.2, R_rel -5.9 / -6.1, burst -22.1 / -21.0, hapax 5.1 / 3.9, heaps 4.5 / 3.2, ini_par 2.6 / 3.6, lag23 19.3 / 18.7, riga_cv 0.3 / 0.2, sezione -10.0 / -10.6, ttr_pagina -9.9 / -9.5

A manopole `ia33`: giudici (condizionata / ablazione) N 0.202 / 0.246, KN 0.744 / 0.768, b 0.571 / 0.538; misure tenute fuori z: D 0.8 / 0.6, R_rel -0.8 / -0.5, burst 15.0 / 17.4, hapax 23.4 / 22.8, heaps 3.8 / 3.0, ini_par -4.7 / -4.1, lag23 -7.5 / -8.4, riga_cv -0.5 / 0.1, sezione -8.4 / -10.0, ttr_pagina 15.6 / 16.0

A manopole `neutro`: giudici (condizionata / ablazione) N 0.951 / 0.927, KN 0.726 / 0.749, b 0.879 / 0.844; misure tenute fuori z: D -0.1 / 0.2, R_rel 1.0 / 0.5, burst 12.4 / 15.7, hapax 24.1 / 24.7, heaps 2.9 / 3.5, ini_par -1.2 / -0.3, lag23 -6.3 / -7.7, riga_cv 0.5 / 0.2, sezione 3.0 / -2.0, ttr_pagina 13.9 / 14.5

Mondo `vero`: scelta della rete condizionata sulla validazione (bit per segno, validazione / fuori piega): Ca 1.944 / 1.948; Cb 1.927 / 1.934; Cc 1.928 / 1.934; ablazione 1.952 / 1.946; scelta: Cb; batte l ablazione in validazione: si

Mondo `vero`: perplessita` (bit per segno) C: validazione 2.061, fuori piega 2.029; A: validazione 2.109, fuori piega 2.087

A manopole `best`: giudici (condizionata / ablazione) N 0.298 / 0.323, KN 0.651 / 0.701, b 0.632 / 0.621; misure tenute fuori z: D 0.6 / 1.0, R_rel -1.7 / -1.2, burst 1.6 / 2.3, hapax 2.2 / 1.8, heaps 1.3 / 1.5, ini_par 1.6 / 1.7, lag23 -1.6 / -2.1, riga_cv 0.8 / -0.3, sezione -5.4 / -5.0, ttr_pagina -1.5 / -1.3

A manopole `ia33`: giudici (condizionata / ablazione) N 0.363 / 0.374, KN 0.723 / 0.775, b 0.631 / 0.649; misure tenute fuori z: D 1.7 / 2.5, R_rel -1.4 / -0.9, burst -2.8 / -1.2, hapax -0.8 / -1.5, heaps 0.8 / 0.6, ini_par -3.3 / -2.9, lag23 3.4 / 2.3, riga_cv 0.4 / -0.6, sezione -4.8 / -4.5, ttr_pagina -4.3 / -3.8

A manopole `neutro`: giudici (condizionata / ablazione) N 0.943 / 0.962, KN 0.718 / 0.784, b 0.747 / 0.915; misure tenute fuori z: D 1.7 / -1.6, R_rel -0.9 / -1.1, burst 5.8 / 12.1, hapax 1.1 / 3.4, heaps 0.5 / 0.2, ini_par -2.1 / -2.9, lag23 -4.0 / -9.1, riga_cv 2.1 / 0.1, sezione 1.6 / -0.5, ttr_pagina 2.6 / 3.7

