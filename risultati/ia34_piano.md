# IA34 (ia34) — Il piano del libro

Preregistrazione: `preregistrazioni/ia34.md`. Solo numeri e aggregati.

## Oracolo del mondo `struttura`

**Verdetto: non valido** (pavimento valido: False; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b. Misure tenute fuori che l'oracolo non rifa: R_rel, ini_par; il gemello: R_rel.

| giudice | oracolo | errore | riconosciuto | netto (2 errori) |
|---|---|---|---|---|
| N | 0.746 | 0.051 | si | si |
| KN | 0.791 | 0.054 | si | si |
| b | 0.728 | 0.039 | si | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.746 | 0.791 | 0.728 |
| 2 | 0.827 | 0.849 | 0.685 |

## Mondo `struttura`

Ciclo: 12 generazioni, partenza ia33, obiettivo del migliore 3.390 contro 5.752 delle manopole neutre (scelto: migliore_ultima).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 5.212 | 6.052 | 0.226 |
| 1 | 4.729 | 5.456 | 0.211 |
| 2 | 4.635 | 5.377 | 0.201 |
| 3 | 4.417 | 5.086 | 0.197 |
| 4 | 4.296 | 5.034 | 0.193 |
| 5 | 4.435 | 4.831 | 0.195 |
| 6 | 4.239 | 4.828 | 0.195 |
| 7 | 3.683 | 4.411 | 0.202 |
| 8 | 3.637 | 4.302 | 0.210 |
| 9 | 3.258 | 4.510 | 0.222 |
| 10 | 3.546 | 4.566 | 0.221 |
| 11 | 3.548 | 4.430 | 0.214 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.752 | -22.6 | 3.4 | -4.4 | -0.1 | -4.3 | 9.0 | -12.1 | -0.8 | -0.1 | 10.3 | 10.1 | 5.1 |
| ia33 | 5.922 | -22.6 | -3.9 | -5.8 | 0.2 | -7.7 | 4.8 | -20.0 | -0.2 | -0.1 | 9.8 | 9.8 | 5.3 |
| media_finale | 3.629 | -16.4 | -2.7 | -1.0 | -0.2 | -3.2 | -3.0 | 2.4 | -0.4 | -0.0 | 6.1 | 7.7 | 4.5 |
| migliore_di_sempre | 3.433 | -12.6 | -2.5 | 0.0 | -1.1 | -1.4 | 1.0 | -5.4 | -1.2 | 0.3 | 4.8 | 7.0 | 4.3 |
| migliore_ultima | 3.390 | -13.1 | -1.9 | 1.3 | -0.1 | -3.4 | -3.0 | -0.4 | -0.4 | 0.2 | 5.1 | 7.2 | 4.9 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 0.882 | 1.000 | 0.870 |
| T_int | 0.699 | 1.000 | 1.092 |
| T_fine | 0.674 | 1.000 | 0.957 |
| T_eol | 0.661 | 1.000 | 0.820 |
| T_riga | 0.814 | 1.000 | 0.728 |
| top_p | 1.000 | 1.000 | 0.933 |
| w_cont | 7.828 | 0.000 | 1.046 |
| w_tri | 2.435 | 0.000 | 7.348 |
| w_quad | 5.770 | 0.000 | 6.139 |
| s | 0.943 | 0.000 | 0.536 |
| w_uni | 0.451 | 0.000 | 0.000 |
| w_bi | 1.384 | 0.000 | 0.000 |
| b_nuove | -0.726 | 0.000 | 0.046 |
| w_pag | 0.184 | 0.000 | 0.073 |
| m_sez | 0.000 | 0.000 | 0.000 |
| w_riga | 0.800 | 0.000 | 0.000 |
| w_fine | 1.297 | 0.000 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.231 (0.051) | 0.736 (0.054) | 0.509 (0.029) | 0.38 | R_rel, burst, sezione, lag23, ini_par | ok |
| neu | 4 | 0.992 (0.051) | 0.699 (0.055) | 0.997 (0.106) | 0.62 | burst, sezione, lag23 | ok |
| ia33k | 8 | 0.195 (0.051) | 0.758 (0.054) | 0.463 (0.061) | 0.50 | burst, sezione, lag23, ini_par | ok |
| cas1 | 4 | 0.547 (0.051) | 0.809 (0.054) | 0.527 (0.070) | 0.43 | heaps, burst, sezione, lag23 | ok |
| cas2 | 4 | 0.480 (0.051) | 0.790 (0.054) | 0.476 (0.059) | 0.29 | heaps, burst, sezione, lag23, ini_par | ok |
| cas3 | 4 | 0.255 (0.051) | 0.828 (0.054) | 0.492 (0.077) | 0.29 | heaps, burst, riga_cv, sezione, lag23 | ok |
| cas4 | 4 | 0.461 (0.051) | 0.772 (0.054) | 0.520 (0.092) | 0.29 | heaps, burst, sezione, lag23, ini_par | ok |
| orac | 16 | 0.746 (0.051) | 0.791 (0.054) | 0.728 (0.039) | 0.75 | R_rel, ini_par | ok |
| orac2 | 8 | 0.827 (0.051) | 0.849 (0.054) | 0.685 (0.042) | 0.86 | ini_par | ok |
| gem | 16 | 0.514 (0.051) | 0.514 (0.054) | 0.392 (0.040) | 0.88 | R_rel | ok |

Misure tenute fuori, `best` (z in sigma): D 1.9, R_rel -3.4, heaps -1.1, burst -8.5, riga_cv 0.4, sezione -11.4, lag23 9.3, ini_par 2.5

Misure tenute fuori, `ia33k` (z in sigma): D 0.3, R_rel -0.6, heaps 2.0, burst 20.6, riga_cv 0.2, sezione -11.7, lag23 -11.6, ini_par -5.2

Misure tenute fuori, `neu` (z in sigma): D 0.5, R_rel -0.3, heaps 1.9, burst 20.4, riga_cv 1.4, sezione -2.9, lag23 -11.8, ini_par -0.1

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN; misure fuori 2 sigma: R_rel, burst, sezione, lag23, ini_par; copia superata: False.

## Mondo `vero`

Ciclo: 12 generazioni, partenza ia33, obiettivo del migliore 2.038 contro 5.438 delle manopole neutre (scelto: ia33).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 2.556 | 3.835 | 0.228 |
| 1 | 2.381 | 3.839 | 0.209 |
| 2 | 2.685 | 4.144 | 0.194 |
| 3 | 2.279 | 3.661 | 0.183 |
| 4 | 2.026 | 3.383 | 0.173 |
| 5 | 2.776 | 3.390 | 0.163 |
| 6 | 2.304 | 3.105 | 0.159 |
| 7 | 2.556 | 2.903 | 0.151 |
| 8 | 2.474 | 3.196 | 0.151 |
| 9 | 2.665 | 3.223 | 0.147 |
| 10 | 2.694 | 3.151 | 0.142 |
| 11 | 2.510 | 3.486 | 0.134 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | lam | bordi_fine | k90 | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.438 | -6.0 | 2.9 | -8.0 | 3.7 | 6.1 | 2.2 | -8.5 | -1.8 | -1.5 | 9.0 | 9.3 | 6.6 |
| ia33 | 2.038 | 1.2 | -0.8 | -1.7 | 0.7 | -0.9 | -1.2 | 1.4 | 2.0 | 1.7 | 4.4 | 5.4 | 2.7 |
| media_finale | 2.404 | 0.1 | -2.1 | -3.1 | -1.4 | 3.1 | -0.3 | 0.6 | 0.2 | 0.5 | 4.7 | 6.1 | 4.2 |
| migliore_di_sempre | 2.257 | 1.1 | -0.5 | -2.4 | 0.5 | -0.8 | -1.9 | 1.6 | 2.8 | 2.0 | 4.4 | 5.9 | 2.6 |
| migliore_ultima | 2.476 | 1.4 | -1.7 | -2.8 | -1.7 | 3.5 | 0.8 | -0.4 | 0.2 | -0.1 | 4.7 | 5.7 | 4.7 |

| manopola | valore scelto | neutro | partenza |
|---|---|---|---|
| T_primo | 1.044 | 1.000 | 1.044 |
| T_int | 0.705 | 1.000 | 0.705 |
| T_fine | 1.051 | 1.000 | 1.051 |
| T_eol | 0.770 | 1.000 | 0.770 |
| T_riga | 0.919 | 1.000 | 0.919 |
| top_p | 0.758 | 1.000 | 0.758 |
| w_cont | 1.905 | 0.000 | 1.905 |
| w_tri | 6.274 | 0.000 | 6.274 |
| w_quad | 7.458 | 0.000 | 7.458 |
| s | 1.000 | 0.000 | 1.000 |
| w_uni | 0.915 | 0.000 | 0.915 |
| w_bi | 0.247 | 0.000 | 0.247 |
| b_nuove | 0.582 | 0.000 | 0.582 |
| w_pag | 0.220 | 0.000 | 0.220 |
| m_sez | 0.000 | 0.000 | 0.000 |
| w_riga | 0.000 | 0.000 | 0.000 |
| w_fine | 0.000 | 0.000 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.325 (0.047) | 0.751 (0.056) | 0.572 (0.043) | 0.62 | sezione, lag23, ini_par | ok |
| neu | 4 | 0.981 (0.047) | 0.880 (0.056) | 0.946 (0.079) | 0.50 | burst, riga_cv, sezione, lag23 | ok |
| ia33k | 8 | 0.324 (0.047) | 0.750 (0.056) | 0.722 (0.068) | 0.62 | sezione, lag23, ini_par | ok |
| cas1 | 4 | 0.994 (0.047) | 0.977 (0.056) | 0.989 (0.085) | 0.14 | heaps, burst, riga_cv, sezione, lag23, ini_par | ok |
| cas2 | 4 | 0.709 (0.048) | 0.834 (0.056) | 0.662 (0.083) | 0.29 | burst, riga_cv, sezione, lag23, ini_par | ok |
| cas3 | 4 | 0.320 (0.048) | 0.710 (0.057) | 0.640 (0.037) | 0.43 | burst, sezione, lag23, ini_par | ok |
| cas4 | 4 | 0.318 (0.047) | 0.707 (0.056) | 0.592 (0.112) | 0.57 | burst, sezione, lag23 | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.658 (0.045) | | | | |

Misure tenute fuori, `best` (z in sigma): D 1.7, R_rel 0.2, heaps 1.2, burst -1.7, riga_cv 0.3, sezione -5.0, lag23 2.1, ini_par -3.1

Misure tenute fuori, `ia33k` (z in sigma): D 1.7, R_rel -0.7, heaps 1.2, burst -1.9, riga_cv 0.3, sezione -5.0, lag23 2.6, ini_par -3.2

Misure tenute fuori, `neu` (z in sigma): D 0.4, R_rel -1.8, heaps 1.3, burst 13.0, riga_cv 2.6, sezione -4.6, lag23 -9.0, ini_par 0.8

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN; misure fuori 2 sigma: sezione, lag23, ini_par; copia superata: False.

