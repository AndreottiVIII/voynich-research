# IA32 (ia32) — L'IA che si allena finche' non riesce

Preregistrazione: `preregistrazioni/ia32.md`. Solo numeri e aggregati.

## Mondo `markov2`

Ciclo: 20 generazioni, obiettivo del migliore 4.431 contro 5.254 delle manopole neutre (scelto: media_finale).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 4.710 | 5.919 | 0.222 |
| 1 | 5.111 | 6.131 | 0.205 |
| 2 | 4.487 | 5.974 | 0.187 |
| 3 | 4.190 | 5.703 | 0.173 |
| 4 | 5.027 | 6.075 | 0.147 |
| 5 | 4.414 | 5.620 | 0.141 |
| 6 | 4.428 | 5.376 | 0.137 |
| 7 | 4.640 | 5.348 | 0.133 |
| 8 | 4.454 | 5.687 | 0.121 |
| 9 | 4.465 | 5.589 | 0.124 |
| 10 | 4.157 | 5.172 | 0.118 |
| 11 | 4.225 | 5.165 | 0.106 |
| 12 | 4.426 | 5.011 | 0.101 |
| 13 | 4.164 | 4.933 | 0.093 |
| 14 | 4.414 | 4.726 | 0.091 |
| 15 | 4.449 | 5.163 | 0.090 |
| 16 | 4.132 | 4.691 | 0.088 |
| 17 | 4.498 | 5.082 | 0.085 |
| 18 | 4.381 | 4.900 | 0.086 |
| 19 | 3.837 | 4.534 | 0.090 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.254 | 2.5 | -0.3 | -0.1 | -1.7 | 16.7 | 9.2 | 9.9 | 7.6 |
| media_finale | 4.431 | 1.4 | 0.4 | -0.7 | 0.3 | 7.0 | 8.2 | 8.7 | 7.1 |
| migliore_di_sempre | 4.485 | 2.5 | -0.4 | -0.7 | 0.5 | 9.4 | 7.0 | 7.7 | 7.1 |
| migliore_ultima | 4.590 | 3.0 | -0.2 | -0.9 | -0.1 | 9.9 | 7.3 | 7.9 | 6.7 |

(z delle grandezze di allenamento: misure rispetto al vero degli stessi fogli, giudici rispetto al nullo.)

| manopola | valore scelto | neutro |
|---|---|---|
| T_primo | 0.989 | 1.000 |
| T_int | 0.892 | 1.000 |
| T_fine | 0.941 | 1.000 |
| T_eol | 0.731 | 1.000 |
| T_riga | 0.831 | 1.000 |
| top_p | 1.000 | 1.000 |
| w_cont | 0.460 | 0.000 |
| w_tri | 0.000 | 0.000 |
| s | 0.000 | 0.000 |

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

| giudice mai visto | migliore | neutro | manopole neutre |
|---|---|---|---|
| N | 0.965 | 0.978 | 0.978 |
| KN | 0.869 | 0.911 | 0.911 |
| b | 0.986 | 0.967 | 0.967 |

| misura tenuta fuori | valore | vero | z (sigma = scala / radice 2) | entro 2 sigma |
|---|---|---|---|---|
| lam | 1.8682 | -3.6421 | 0.26 | si |
| D | 0.0421 | 0.0307 | 1.62 | si |
| bordi_fine | 0.0021 | 0.0014 | 2.08 | NO |
| parole_nuove | 0.1397 | 0.1694 | -11.44 | NO |
| k90 | 1.4037 | 1.2992 | 1.90 | si |
| R_rel | 0.9561 | 0.9747 | -1.42 | si |

Quota entro 2 sigma: 0.67; misure fuori: bordi_fine, parole_nuove; copia: ok.

Controllo negativo (manopole a caso): ia32c1: giudici {'N': '1.000', 'KN': '0.999', 'b': '0.998'}, supera False; ia32c2: giudici {'N': '1.000', 'KN': '0.992', 'b': '0.998'}, supera False; ia32c3: giudici {'N': '1.000', 'KN': '1.000', 'b': '1.000'}, supera False; ia32c4: giudici {'N': '0.999', 'KN': '0.974', 'b': '0.999'}, supera False; ia32c5: giudici {'N': '1.000', 'KN': '0.999', 'b': '1.000'}, supera False; ia32c6: giudici {'N': '0.994', 'KN': '0.972', 'b': '0.992'}, supera False; ia32c7: giudici {'N': '1.000', 'KN': '1.000', 'b': '1.000'}, supera False; ia32c8: giudici {'N': '0.994', 'KN': '0.963', 'b': '0.993'}, supera False

## Mondo `vero`

Ciclo: 20 generazioni, obiettivo del migliore 3.078 contro 6.459 delle manopole neutre (scelto: migliore_ultima).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 5.384 | 7.044 | 0.232 |
| 1 | 4.857 | 6.124 | 0.226 |
| 2 | 4.610 | 6.054 | 0.226 |
| 3 | 4.858 | 6.382 | 0.218 |
| 4 | 3.740 | 6.195 | 0.218 |
| 5 | 3.842 | 5.005 | 0.221 |
| 6 | 3.960 | 4.649 | 0.217 |
| 7 | 3.745 | 5.039 | 0.207 |
| 8 | 3.900 | 4.477 | 0.199 |
| 9 | 3.881 | 4.609 | 0.191 |
| 10 | 3.782 | 4.444 | 0.191 |
| 11 | 3.723 | 3.917 | 0.196 |
| 12 | 3.549 | 4.106 | 0.205 |
| 13 | 3.253 | 3.754 | 0.204 |
| 14 | 3.405 | 3.906 | 0.205 |
| 15 | 3.332 | 3.754 | 0.195 |
| 16 | 3.177 | 3.944 | 0.180 |
| 17 | 3.226 | 3.747 | 0.178 |
| 18 | 3.108 | 3.521 | 0.162 |
| 19 | 3.203 | 3.496 | 0.149 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|
| neutro | 6.459 | -5.6 | 3.5 | -8.0 | 3.3 | 6.3 | 9.0 | 9.3 | 6.5 |
| media_finale | 3.178 | -4.5 | -0.4 | -5.6 | 0.7 | 0.6 | 5.0 | 5.6 | 2.9 |
| migliore_di_sempre | 3.180 | -4.2 | 0.1 | -5.3 | 1.0 | 0.3 | 5.3 | 5.7 | 2.8 |
| migliore_ultima | 3.078 | -4.5 | 0.5 | -5.0 | 0.7 | 0.5 | 4.6 | 5.1 | 3.5 |

(z delle grandezze di allenamento: misure rispetto al vero degli stessi fogli, giudici rispetto al nullo.)

| manopola | valore scelto | neutro |
|---|---|---|
| T_primo | 1.097 | 1.000 |
| T_int | 0.804 | 1.000 |
| T_fine | 1.200 | 1.000 |
| T_eol | 0.949 | 1.000 |
| T_riga | 1.335 | 1.000 |
| top_p | 0.984 | 1.000 |
| w_cont | 1.507 | 0.000 |
| w_tri | 2.400 | 0.000 |
| s | 0.978 | 0.000 |

**Esito: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

| giudice mai visto | migliore | neutro | v21 |
|---|---|---|---|
| N | 0.608 | 0.984 | 0.599 |
| KN | 0.754 | 0.884 | 0.677 |
| b | 0.979 | 0.996 | 0.921 |

| misura tenuta fuori | valore | vero | z (sigma = scala / radice 2) | entro 2 sigma |
|---|---|---|---|---|
| lam | 0.3461 | 0.1371 | 3.25 | NO |
| D | 0.1859 | 0.1450 | 2.63 | NO |
| bordi_fine | 0.0524 | 0.0475 | 1.43 | si |
| parole_nuove | 0.1093 | 0.1484 | -6.44 | NO |
| k90 | 2.2019 | 2.1511 | 0.15 | si |
| R_rel | 0.9857 | 1.0080 | -1.03 | si |

Quota entro 2 sigma: 0.50; misure fuori: lam, D, parole_nuove; copia: ok.

Controllo negativo (manopole a caso): ia32c1: giudici {'N': '0.995', 'KN': '0.957', 'b': '1.000'}, supera False; ia32c2: giudici {'N': '0.897', 'KN': '0.844', 'b': '0.921'}, supera False; ia32c3: giudici {'N': '0.867', 'KN': '0.762', 'b': '0.966'}, supera False; ia32c4: giudici {'N': '1.000', 'KN': '0.989', 'b': '1.000'}, supera False; ia32c5: giudici {'N': '0.827', 'KN': '0.829', 'b': '0.956'}, supera False; ia32c6: giudici {'N': '0.983', 'KN': '0.885', 'b': '0.983'}, supera False; ia32c7: giudici {'N': '0.989', 'KN': '0.974', 'b': '0.986'}, supera False; ia32c8: giudici {'N': '1.000', 'KN': '1.000', 'b': '1.000'}, supera False

