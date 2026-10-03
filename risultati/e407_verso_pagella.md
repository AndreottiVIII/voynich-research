# e407 — Verso la pagella: unioni, legame fra ultimo e primo segno, verticale

Semi 1–4 (medie). Riferimento: P3 dell'e406 (v8) 0,558 / 0,703, pagella 13,8/18, estese 4,0/8. Preregistrazione: `preregistrazioni/e407.md`.

## Regolazione sul pannello (seme 11)

- **U1:** pesi bordi 0.776, unione 1.200, coppia 0.000, identica -0.598; valori unioni attestate 0.0880, coppie viste altrove 0.2366, coppie identiche 0.0093, somiglianza fra vicine 0.2154 (Voynich 0.0916, 0.2213, 0.0097, 0.2181); scarto massimo 0.069: converge.
- **U2:** pesi bordi 0.715, unione 0.675, coppia 0.336, identica -0.660, confine 0.609; valori unioni attestate 0.0852, coppie viste altrove 0.2428, coppie identiche 0.0095, somiglianza fra vicine 0.2136, confine 0.1738 (Voynich 0.0916, 0.2213, 0.0097, 0.2181, 0.1881); scarto massimo 0.097: converge.
- **U3:** pesi bordi 0.843, unione 0.859, coppia 0.000, identica -0.553, confine 0.710, verticale 0.117; valori unioni attestate 0.0893, coppie viste altrove 0.2434, coppie identiche 0.0094, somiglianza fra vicine 0.2160, confine 0.1838, verticale 1.0310 (Voynich 0.0916, 0.2213, 0.0097, 0.2181, 0.1881, 1.0278); scarto massimo 0.100: converge.

| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | riga | unione = parola unica (Voynich 0,027) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U1 | parole nuove come unioni | 0.548 | 0.659 (0.635–0.707) | 0.561 | 15.2/18 | 4.0/8 | 0/4 | 0.0342 | 0.50 | 0.51 | 0.66 | 0.54 | 0.50 | 0.61 | 0.56 | 0.67 | 0.70 |
| U2 | U1 e legame fra ultimo e primo segno | 0.559 | 0.673 (0.668–0.679) | 0.561 | 16.0/18 | 3.0/8 | 0/4 | 0.0267 | 0.50 | 0.51 | 0.66 | 0.58 | 0.52 | 0.62 | 0.58 | 0.67 | 0.69 |
| U3 | U2 e verticale | 0.541 | 0.659 (0.643–0.676) | 0.561 | 16.5/18 | 3.2/8 | 0/4 | 0.0298 | 0.50 | 0.51 | 0.66 | 0.55 | 0.48 | 0.62 | 0.57 | 0.67 | 0.70 |

## Materie mancate (su 4 semi) e valori grezzi

**U1.** legame (4), profilo pagina (4), scelte di riga (4), concordanza delle desinenze (4), verticale (3), dispersione delle lunghezze (3), prime righe come registro (3), parole rare per pagina (2).

**U2.** profilo pagina (4), prime righe come registro (4), scelte di riga (4), concordanza delle desinenze (4), verticale (3), parole rare per pagina (3), dispersione delle lunghezze (3), coppie viste altrove (2), gradiente (1).

**U3.** profilo pagina (4), prime righe come registro (4), scelte di riga (4), concordanza delle desinenze (4), dispersione delle lunghezze (3), gradiente (2), parole rare per pagina (2), coppie viste altrove (2).

| valore grezzo | Voynich | U1 | U2 | U3 |
|---|---|---|---|---|
| parole | 3.486e+04 | 3.486e+04 | 3.486e+04 | 3.486e+04 |
| h2 | 2.236 | 2.277 | 2.277 | 2.277 |
| lung_media | 4.461 | 4.49 | 4.49 | 4.49 |
| tipi_su_parole | 0.2098 | 0.2045 | 0.2043 | 0.2045 |
| hapax | 0.6795 | 0.7342 | 0.7341 | 0.7342 |
| identiche_immediate | 0.009371 | 0.008582 | 0.008639 | 0.009119 |
| identiche_vs_riga | 1.009 | 1.046 | 1.047 | 1.082 |
| somiglianza_riga | 0.03845 | 0.0403 | 0.04037 | 0.04064 |
| somiglianza_riga_sotto | 0.03987 | 0.03456 | 0.03455 | 0.03489 |
| somiglianza_6_righe | 0.03353 | 0.02912 | 0.02866 | 0.0286 |
| spazio_spiegato | 0.6636 | 0.6352 | 0.6361 | 0.6355 |
| confine | 0.1881 | 0.03913 | 0.1772 | 0.1925 |
| unione_attestata | 0.08766 | 0.08552 | 0.08244 | 0.08479 |
| unione_caso | 0.04464 | 0.03951 | 0.0391 | 0.03966 |
| ordine_rispettato | 0.7847 | 0.7545 | 0.7545 | 0.7545 |
| anagrammi | 0.3535 | 0.2912 | 0.2912 | 0.2912 |
| hapax_1000 | 0.7352 | 0.699 | 0.7002 | 0.7006 |
| hapax_34000 | 0.6778 | 0.7448 | 0.745 | 0.7449 |
| V2_ricambio_k1_meno_k20 | 0.1058 | 0.09518 | 0.09572 | 0.09623 |
| V3_R | 1.017 | 0.61 | 0.6112 | 0.618 |
| V3_quota_media | 0.06054 | 0.04362 | 0.04335 | 0.04328 |
| lung_media_segni | 4.461 | 4.49 | 4.49 | 4.49 |
| lung_dev_segni | 1.645 | 1.647 | 1.647 | 1.647 |
| V6_autocorrelazione_lunghezze | 0.1498 | 0.1683 | 0.1621 | 0.1814 |
| V7_zipf | -1.041 | -1.028 | -1.028 | -1.028 |
| V8_forma | 0 | 0.03797 | 0.03797 | 0.03797 |
| verticale | 1.028 | 1.01 | 1.005 | 1.029 |
| formule_terne | 5.195 | 4.259 | 6.24 | 6.074 |

| materia aggiunta | Voynich | U1 | U2 | U3 |
|---|---|---|---|---|
| parole rare per pagina | 1.958 | 4.994 | 5.206 | 4.927 |
| tipi su parole nella pagina | 0.7559 | 0.7454 | 0.7454 | 0.7454 |
| uniche nella pagina | 0.6359 | 0.6162 | 0.6162 | 0.6162 |
| dispersione delle lunghezze | 1.579 | 1.626 | 1.626 | 1.626 |
| prime righe come registro | 4.724 | 1.543 | 1.853 | 2.317 |
| scelte di riga | 12 | 3.25 | 2.5 | 3.5 |
| concordanza delle desinenze | 0.04335 | 0.0916 | 0.1041 | 0.1195 |
| coppie viste altrove | 0.2213 | 0.2329 | 0.2399 | 0.2427 |

## Pannello (media delle pagine)

| misura | Voynich | U1 | U2 | U3 |
|---|---|---|---|---|
| G4 inizio p | 0.0769 | 0.0699 | 0.0713 | 0.0714 |
| G4 inizio t | 0.1052 | 0.0988 | 0.1008 | 0.1018 |
| G4 inizio ch | 0.0355 | 0.0370 | 0.0368 | 0.0381 |
| G4 fine m | 0.1392 | 0.1465 | 0.1461 | 0.1458 |
| G7 ultime in m | 0.1392 | 0.1465 | 0.1461 | 0.1458 |
| G7 lunghezza prima parola | 4.8197 | 4.8283 | 4.8398 | 4.8215 |
| G7 lunghezza ultima parola | 4.2931 | 4.3919 | 4.3631 | 4.3878 |
| G4 unioni attestate | 0.0916 | 0.0924 | 0.0883 | 0.0915 |
| G4 somiglianza fra vicine | 0.2181 | 0.2160 | 0.2131 | 0.2160 |
| G6 coppie viste altrove | 0.2213 | 0.2329 | 0.2399 | 0.2427 |
| G6 coppie identiche | 0.0097 | 0.0085 | 0.0087 | 0.0094 |
| G8 p prime righe meno altre | 0.0331 | 0.0286 | 0.0298 | 0.0291 |
| G8 lunghezza parole prime righe | 4.6323 | 4.8112 | 4.7871 | 4.7906 |
| G9 JSD prima-seconda meta | 0.0503 | 0.0352 | 0.0355 | 0.0355 |

## Caratteristiche più pesanti (seme 1)

**U1**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD prima-seconda meta | -2.16 | 0.0503 | 0.0369 |
| e266 | G9 JSD pagina-manoscritto | +2.08 | 0.0402 | 0.0458 |
| e266 | G3 fra le 100 piu frequenti | +1.41 | 0.4244 | 0.4374 |
| e266 | G6 somiglianza a distanza 2 | -1.33 | 0.2198 | 0.2104 |
| e266 | G2 d+a | -1.13 | 0.0373 | 0.0365 |
| e266 | G2 e+p | -1.13 | 0.0008 | 0.0003 |
| e266 | G2 y+k | -0.99 | 0.0070 | 0.0054 |
| e266 | G2 ch+k | +0.98 | 0.0017 | 0.0022 |
| e266 | G2 o+d | -0.90 | 0.0216 | 0.0186 |
| e266 | G2 ch+ckh | -0.88 | 0.0020 | 0.0018 |
| e231 | G1 cph | -1.41 | 0.0018 | 0.0017 |
| e231 | G2 d+a | -1.38 | 0.0373 | 0.0365 |
| e231 | G3 tipi su parole | +1.31 | 0.7559 | 0.7437 |
| e231 | G3 fra le 100 piu frequenti | +1.24 | 0.4244 | 0.4374 |
| e231 | G2 o+t | -1.22 | 0.0264 | 0.0247 |
| e231 | G1 p | +1.16 | 0.0075 | 0.0071 |

**U2**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD pagina-manoscritto | +2.36 | 0.0402 | 0.0458 |
| e266 | G6 coppie viste altrove | +2.11 | 0.2213 | 0.2443 |
| e266 | G9 JSD prima-seconda meta | -1.99 | 0.0503 | 0.0355 |
| e266 | G6 somiglianza a distanza 2 | -1.79 | 0.2198 | 0.2078 |
| e266 | G4 unioni attestate | -1.39 | 0.0916 | 0.0882 |
| e266 | G3 tipi su parole | +1.08 | 0.7559 | 0.7437 |
| e266 | G2 o+t | -1.04 | 0.0264 | 0.0247 |
| e266 | G7 lunghezza ultima parola | +1.04 | 4.2931 | 4.3698 |
| e266 | G2 a+s | +0.95 | 0.0007 | 0.0008 |
| e266 | G1 t | +0.91 | 0.0353 | 0.0337 |
| e231 | G3 fra le 100 piu frequenti | +1.53 | 0.4244 | 0.4374 |
| e231 | G2 o+t | -1.53 | 0.0264 | 0.0247 |
| e231 | G1 cph | -1.48 | 0.0018 | 0.0017 |
| e231 | G3 tipi su parole | +1.43 | 0.7559 | 0.7437 |
| e231 | G2 d+a | -1.23 | 0.0373 | 0.0365 |
| e231 | G2 p+ch | -1.08 | 0.0052 | 0.0042 |

**U3**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD pagina-manoscritto | +2.56 | 0.0402 | 0.0458 |
| e266 | G9 JSD prima-seconda meta | -2.07 | 0.0503 | 0.0367 |
| e266 | G6 coppie viste altrove | +1.95 | 0.2213 | 0.2449 |
| e266 | G6 somiglianza a distanza 2 | -1.78 | 0.2198 | 0.2080 |
| e266 | G2 ch+k | +1.11 | 0.0017 | 0.0022 |
| e266 | G3 fra le 100 piu frequenti | +1.02 | 0.4244 | 0.4374 |
| e266 | G2 p+ch | -0.92 | 0.0052 | 0.0042 |
| e266 | G2 o+m | -0.92 | 0.0021 | 0.0018 |
| e266 | G3 tipi su parole | +0.90 | 0.7559 | 0.7437 |
| e266 | G2 d+a | -0.85 | 0.0373 | 0.0365 |
| e231 | G3 tipi su parole | +1.31 | 0.7559 | 0.7437 |
| e231 | G2 d+a | -1.31 | 0.0373 | 0.0365 |
| e231 | G3 fra le 100 piu frequenti | +1.27 | 0.4244 | 0.4374 |
| e231 | G3 uniche nella pagina | -1.24 | 0.6359 | 0.6138 |
| e231 | G2 p+ch | -1.19 | 0.0052 | 0.0042 |
| e231 | G1 cph | -1.15 | 0.0018 | 0.0017 |

