# IA33 (ia33) — L'oracolo e l'IA piu' libera

Preregistrazione: `preregistrazioni/ia33.md`. Solo numeri e aggregati.

## Parte O — l'oracolo (mondo `markov2`)

**Verdetto: irraggiungibile** (pavimento valido: True; giudice b valido: True). Giudici che lo riconoscono (fuori 0,40-0,60): N, KN, b; oltre 0,60 alla lettera: KN, b.

| giudice | oracolo ufficiale (KN) | errore | riconosciuto (fuori 0,40-0,60) | netto (2 errori) | oltre 0,60 |
|---|---|---|---|---|---|
| N | 0.271 | 0.050 | si | si | no |
| KN | 0.605 | 0.054 | si | no | si |
| b | 0.653 | 0.030 | si | no | si |

| testo (volte) | N | KN | b |
|---|---|---|---|
| 1 | 0.271 | 0.605 | 0.653 |
| 2 | 0.381 | 0.542 | 0.592 |
| 4 | 0.451 | 0.510 | 0.540 |

Stima descrittiva (legge di potenza sui punti sopra, da prendere con cautela): KN: 1.1 volte il testo per 0,60, 1.6 per 0,55; b: 1.6 volte il testo per 0,60, 3.4 per 0,55

## Mondo `markov2`

Ciclo: 24 generazioni, partenza ia32, obiettivo del migliore 1.294 contro 4.793 delle manopole neutre (scelto: media_finale).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 3.751 | 5.217 | 0.217 |
| 1 | 3.059 | 5.441 | 0.211 |
| 2 | 3.056 | 4.176 | 0.211 |
| 3 | 2.782 | 4.247 | 0.205 |
| 4 | 2.192 | 3.692 | 0.204 |
| 5 | 2.680 | 3.366 | 0.207 |
| 6 | 1.807 | 3.434 | 0.212 |
| 7 | 1.860 | 3.023 | 0.208 |
| 8 | 1.828 | 3.354 | 0.198 |
| 9 | 2.216 | 3.805 | 0.185 |
| 10 | 2.156 | 3.576 | 0.175 |
| 11 | 1.887 | 3.781 | 0.170 |
| 12 | 1.894 | 3.357 | 0.165 |
| 13 | 2.171 | 3.368 | 0.159 |
| 14 | 2.124 | 3.135 | 0.147 |
| 15 | 1.833 | 2.937 | 0.142 |
| 16 | 2.020 | 2.930 | 0.137 |
| 17 | 2.086 | 3.068 | 0.129 |
| 18 | 1.902 | 2.809 | 0.118 |
| 19 | 1.719 | 2.472 | 0.112 |
| 20 | 1.247 | 2.486 | 0.107 |
| 21 | 1.361 | 2.228 | 0.101 |
| 22 | 1.314 | 1.929 | 0.096 |
| 23 | 1.486 | 2.120 | 0.087 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 4.793 | 1.2 | 0.1 | 0.3 | -1.3 | 16.8 | 1.2 | 9.3 | 9.9 | 7.6 |
| ia32 | 4.699 | 0.9 | 0.2 | -1.2 | 0.4 | 6.9 | -8.1 | 8.0 | 8.4 | 7.3 |
| media_finale | 1.294 | 0.5 | -0.3 | -1.0 | 0.4 | 0.3 | -2.1 | 1.0 | 3.3 | 1.5 |
| migliore_di_sempre | 1.474 | 0.1 | 0.1 | -0.8 | 0.4 | -0.0 | -0.6 | 1.4 | 4.9 | 1.9 |
| migliore_ultima | 1.627 | 3.6 | -1.1 | 0.4 | 0.3 | 0.8 | -3.4 | -0.5 | 3.0 | 0.8 |

| manopola | valore scelto | neutro |
|---|---|---|
| T_primo | 0.870 | 1.000 |
| T_int | 1.092 | 1.000 |
| T_fine | 0.957 | 1.000 |
| T_eol | 0.820 | 1.000 |
| T_riga | 0.728 | 1.000 |
| top_p | 0.933 | 1.000 |
| w_cont | 1.046 | 0.000 |
| w_tri | 7.348 | 0.000 |
| w_quad | 6.139 | 0.000 |
| s | 0.536 | 0.000 |
| w_uni | 0.000 | 0.000 |
| w_bi | 0.000 | 0.000 |
| b_nuove | 0.046 | 0.000 |
| w_pag | 0.073 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.131 (0.050) | 0.553 (0.054) | 0.650 (0.043) | 1.00 | - | ok |
| neu | 4 | 0.976 (0.050) | 0.927 (0.054) | 0.894 (0.077) | 0.80 | bordi_fine | ok |
| ia32k | 8 | 0.967 (0.050) | 0.865 (0.054) | 0.940 (0.054) | 0.80 | bordi_fine | ok |
| cas1 | 4 | 0.868 (0.050) | 0.908 (0.053) | 0.783 (0.062) | 0.67 | bordi_fine | ok |
| cas2 | 4 | 0.943 (0.050) | 0.907 (0.054) | 0.883 (0.046) | 1.00 | - | ok |
| cas3 | 4 | 0.944 (0.050) | 0.945 (0.054) | 0.859 (0.069) | 0.67 | bordi_fine | ok |
| cas4 | 4 | 1.000 (0.050) | 1.000 (0.053) | 1.000 (0.097) | 0.33 | D, bordi_fine | ok |
| orkn | 16 | 0.271 (0.050) | 0.605 (0.054) | 0.653 (0.030) | 1.00 | - | ok |
| ormle | 8 | 0.276 (0.051) | 0.643 (0.054) | 0.658 (0.031) | 1.00 | - | ok |
| orkn2 | 8 | 0.381 (0.050) | 0.542 (0.054) | 0.592 (0.057) | 1.00 | - | ok |
| orkn4 | 8 | 0.451 (0.050) | 0.510 (0.056) | 0.540 (0.063) | 1.00 | - | ok |
| gem | 16 | 0.514 (0.050) | 0.505 (0.054) | 0.460 (0.036) | 1.00 | - | ok |

**Esito L: al livello dell'oracolo** (giudice b valido: True; controllo negativo riuscito: True).

## Mondo `vero`

Ciclo: 24 generazioni, partenza ia32, obiettivo del migliore 2.206 contro 5.880 delle manopole neutre (scelto: media_finale).

| generazione | obiettivo minimo | media | passo CMA-ES |
|---|---|---|---|
| 0 | 3.559 | 4.736 | 0.228 |
| 1 | 3.092 | 4.216 | 0.221 |
| 2 | 2.441 | 4.106 | 0.212 |
| 3 | 2.341 | 4.041 | 0.207 |
| 4 | 2.552 | 3.848 | 0.194 |
| 5 | 2.559 | 3.896 | 0.181 |
| 6 | 2.551 | 3.217 | 0.176 |
| 7 | 2.348 | 3.801 | 0.179 |
| 8 | 2.302 | 3.340 | 0.169 |
| 9 | 2.936 | 3.449 | 0.165 |
| 10 | 2.431 | 3.369 | 0.155 |
| 11 | 2.691 | 3.159 | 0.152 |
| 12 | 2.473 | 3.028 | 0.150 |
| 13 | 2.746 | 3.551 | 0.147 |
| 14 | 2.755 | 3.162 | 0.145 |
| 15 | 2.719 | 3.268 | 0.139 |
| 16 | 2.562 | 3.157 | 0.126 |
| 17 | 2.457 | 2.859 | 0.121 |
| 18 | 2.406 | 2.826 | 0.113 |
| 19 | 2.490 | 3.121 | 0.111 |
| 20 | 2.344 | 2.727 | 0.107 |
| 21 | 2.038 | 2.426 | 0.105 |
| 22 | 2.226 | 2.555 | 0.105 |
| 23 | 2.145 | 2.551 | 0.103 |

| finalista | obiettivo rivalutato | copia_netta | contatto | G9 | bordi_inizio | costo_forma | parole_nuove | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|---|---|
| neutro | 5.880 | -5.9 | 2.8 | -7.8 | 3.2 | 6.0 | 2.3 | 9.0 | 9.3 | 6.6 |
| ia32 | 3.301 | -4.5 | 0.4 | -4.9 | 0.5 | 0.4 | -4.3 | 4.9 | 5.4 | 3.8 |
| media_finale | 2.206 | 1.3 | -0.7 | -2.3 | 0.6 | -0.6 | -1.2 | 4.1 | 5.5 | 2.9 |
| migliore_di_sempre | 2.211 | -1.1 | -0.6 | -3.6 | 0.6 | -0.3 | -0.6 | 3.7 | 5.5 | 2.7 |
| migliore_ultima | 2.311 | 2.1 | -0.8 | -2.3 | 0.7 | -1.1 | -0.7 | 4.2 | 5.3 | 3.1 |

| manopola | valore scelto | neutro |
|---|---|---|
| T_primo | 1.044 | 1.000 |
| T_int | 0.705 | 1.000 |
| T_fine | 1.051 | 1.000 |
| T_eol | 0.770 | 1.000 |
| T_riga | 0.919 | 1.000 |
| top_p | 0.758 | 1.000 |
| w_cont | 1.905 | 0.000 |
| w_tri | 6.274 | 0.000 |
| w_quad | 7.458 | 0.000 |
| s | 1.000 | 0.000 |
| w_uni | 0.915 | 0.000 |
| w_bi | 0.247 | 0.000 |
| b_nuove | 0.582 | 0.000 |
| w_pag | 0.220 | 0.000 |

| insieme | libri | N | KN | b | quota entro 2 sigma | misure fuori | copia |
|---|---|---|---|---|---|---|---|
| best | 16 | 0.332 (0.047) | 0.750 (0.056) | 0.564 (0.060) | 0.40 | lam, bordi_fine, k90 | ok |
| neu | 4 | 0.983 (0.047) | 0.882 (0.056) | 0.968 (0.056) | 0.60 | lam, bordi_fine | ok |
| ia32k | 8 | 0.606 (0.048) | 0.754 (0.056) | 0.688 (0.061) | 0.60 | lam, D | ok |
| cas1 | 4 | 0.972 (0.047) | 0.983 (0.056) | 0.825 (0.105) | 0.67 | D | ok |
| cas2 | 4 | 0.999 (0.047) | 0.985 (0.056) | 0.969 (0.085) | 0.00 | lam, D, bordi_fine | ok |
| cas3 | 4 | 0.815 (0.047) | 0.840 (0.056) | 0.748 (0.068) | 0.33 | lam, D | ok |
| cas4 | 4 | 1.000 (0.047) | 0.999 (0.056) | 0.999 (0.137) | 0.67 | D | ok |
| ngr | 16 | 0.913 (0.047) | 0.991 (0.056) | 0.726 (0.046) | 0.60 | D, bordi_fine | ok |
| v21 | 10 | 0.599 (0.049) | 0.677 (0.056) | 0.658 (0.045) | | | | |

**Esito L: non riuscito** (giudice b valido: True; controllo negativo riuscito: True).

Resta fuori: giudici oltre 0,60: N, KN; misure fuori 2 sigma: lam, bordi_fine, k90; copia superata: False.

Parte V: baseline N 0.913, KN 0.991, b 0.726; quota del progresso di IA32 fatta dai soli conteggi: N 0.19, KN -0.82, b 16.59

