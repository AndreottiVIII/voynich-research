# e411 — Profilo di pagina e gradiente

Semi 1–4 (medie), corpo senza messaggio. Riferimento: G2 dell'e410 (corpo della v11) 0,552 / 0,616, pagella 15,8/18, cancello 3/4. Preregistrazione: `preregistrazioni/e411.md`.

- Carattere per posizione: κ = 0.606, θ = 7824; JSD pagina-manoscritto 0.0400 (Voynich 0.0402), tipi su parole 0.7470; scarto massimo 0.012: converge.
- Vicinato: peso 4.00; gradiente 0.219 (Voynich 0.683); giri: 4.0 → 0.219, 11.0 → -0.001, 21.2 → -0.028, 31.9 → -0.038, 40.0 → -0.033, 40.0 → -0.033, 40.0 → -0.033.

| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | semi con il cancello | JSD fra le due metà (Voynich 0,0503) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | carattere di pagina per posizione nella parola | 0.591 | 0.644 (0.640–0.650) | 0.562 | 16.2/18 | 4.2/8 | 3/4 | 0.0409 | 0.52 | 0.53 | 0.67 | 0.59 | 0.53 | 0.60 | 0.57 | 0.64 | 0.60 |
| H2 | H1 e vicinato fra righe | 0.689 | 0.780 (0.732–0.812) | 0.562 | 14.2/18 | 5.8/8 | 0/4 | 0.0751 | 0.52 | 0.53 | 0.67 | 0.70 | 0.55 | 0.66 | 0.60 | 0.62 | 0.68 |

Valori per seme (profilo pagina: R fra 0,8 e 1,25; gradiente fra 0,70 e 0,97; cancello: S1 ≤ 0,7, A ≥ 1,0, scelte ≥ 3, r 0,207 ± 0,07):

| | H1 | H2 |
|---|---|---|
| gradiente | 0.556, 0.584, 0.557, 0.601 | 0.200, 0.201, 0.214, 0.198 |
| V3_R | 0.787, 0.732, 0.834, 0.828 | 0.752, 0.730, 0.789, 0.843 |
| V3_quota_media | 0.044, 0.043, 0.042, 0.045 | 0.051, 0.048, 0.048, 0.051 |
| somiglianza_riga | 0.047, 0.046, 0.044, 0.042 | 0.094, 0.090, 0.091, 0.087 |
| somiglianza_riga_sotto | 0.039, 0.039, 0.037, 0.036 | 0.094, 0.089, 0.092, 0.087 |
| somiglianza_6_righe | 0.026, 0.027, 0.024, 0.025 | 0.019, 0.018, 0.020, 0.017 |
| verticale | 1.029, 1.042, 1.038, 1.028 | 1.032, 1.020, 1.034, 1.028 |
| confine | 0.198, 0.207, 0.180, 0.201 | 0.169, 0.178, 0.163, 0.168 |
| S1 | 0.585, 0.634, 0.532, 0.525 | 0.755, 0.727, 0.768, 0.640 |
| R_riga | 0.015, 0.002, 0.022, 0.020 | 0.056, -0.005, 0.047, 0.034 |
| A | 1.007, 1.013, 1.014, 1.000 | 1.020, 1.030, 1.027, 1.018 |
| scelte_per_riga | 5.000, 5.000, 5.000, 5.000 | 5.000, 5.000, 5.000, 5.000 |
| r_righe_consecutive | 0.174, 0.176, 0.171, 0.174 | 0.304, 0.296, 0.279, 0.302 |

## Materie mancate (su 4 semi)

**H1.** gradiente (4), scelte di riga (4), coppie viste altrove (4), concordanza delle desinenze (3), dispersione delle lunghezze (3), profilo pagina (2), omogeneità (1), parole rare per pagina (1).

**H2.** omogeneità (4), gradiente (4), formule (4), coppie viste altrove (4), profilo pagina (3), dispersione delle lunghezze (3), parole rare per pagina (2).

| materia aggiunta | Voynich | H1 | H2 |
|---|---|---|---|
| parole rare per pagina | 1.958 | 4.821 | 4.91 |
| tipi su parole nella pagina | 0.7559 | 0.7477 | 0.7477 |
| uniche nella pagina | 0.6359 | 0.6222 | 0.6222 |
| dispersione delle lunghezze | 1.579 | 1.621 | 1.621 |
| prime righe come registro | 4.724 | 3.378 | 5.567 |
| scelte di riga | 12 | 7.25 | 10 |
| concordanza delle desinenze | 0.04335 | 0.05878 | 0.04807 |
| coppie viste altrove | 0.2213 | 0.2535 | 0.255 |

## Caratteristiche più pesanti (giudice e266, seme 1)

**H1**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +2.39 | 0.2213 | 0.2471 |
| G9 JSD prima-seconda meta | -1.80 | 0.0503 | 0.0415 |
| G2 y+o | +1.57 | 0.0004 | 0.0010 |
| G3 fra le 100 piu frequenti | +1.43 | 0.4244 | 0.4433 |
| G2 o+k | -1.32 | 0.0401 | 0.0385 |
| G2 ch+e | -1.26 | 0.0319 | 0.0315 |
| G3 lunghezza media | +1.14 | 4.2913 | 4.3306 |
| G2 ch+d | +1.07 | 0.0053 | 0.0067 |
| G4 inizio ch | +1.05 | 0.0355 | 0.0464 |
| G4 inizio s | +1.03 | 0.0804 | 0.0975 |

**H2**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 somiglianza a distanza 2 | +2.04 | 0.2198 | 0.2549 |
| G4 somiglianza fra vicine | +1.92 | 0.2181 | 0.2455 |
| G9 JSD prima-seconda meta | +1.56 | 0.0503 | 0.0748 |
| G3 fra le 100 piu frequenti | +1.36 | 0.4244 | 0.4433 |
| G6 coppie viste altrove | +1.30 | 0.2213 | 0.2519 |
| G2 y+o | +1.24 | 0.0004 | 0.0010 |
| G8 k prime righe meno altre | +1.03 | -0.0236 | -0.0149 |
| G9 JSD pagina-manoscritto | -1.02 | 0.0402 | 0.0420 |
| G2 s+o | -0.99 | 0.0033 | 0.0029 |
| G3 tipi su parole | +0.93 | 0.7559 | 0.7477 |

