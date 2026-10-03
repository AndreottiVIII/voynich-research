# e408 — Concordanza delle desinenze e scelte di grafia concordi nella riga

Semi 1–4 (medie). Riferimento: U3 dell'e407 (v9) 0,541 / 0,659, pagella 16,5/18, estese 3,2/8. Preregistrazione: `preregistrazioni/e408.md`.

## Regolazione sul pannello (seme 11)

- **R1:** pesi bordi 1.104, unione 0.926, coppia 0.000, identica -0.357, confine 0.683, verticale 0.119, fin_fin 0.072; valori unioni attestate 0.0933, coppie viste altrove 0.2516, coppie identiche 0.0098, somiglianza fra vicine 0.2137, confine 0.1903, verticale 1.0225, concordanza 0.0577; Voynich 0.0916, 0.2213, 0.0097, 0.2181, 0.1881, 1.0278, 0.0416; scarto massimo 0.137: **non converge**.
- **R2:** pesi bordi 1.076, unione 0.914, coppia 0.000, identica -0.660, confine 0.736, verticale 0.098, fin_fin 0.049, classi 0.031; valori unioni attestate 0.0903, coppie viste altrove 0.2498, coppie identiche 0.0085, somiglianza fra vicine 0.2133, confine 0.2031, verticale 1.0283, concordanza 0.0542, accordo classi 0.0227; Voynich 0.0916, 0.2213, 0.0097, 0.2181, 0.1881, 1.0278, 0.0416, 0.0231; scarto massimo 0.129: **non converge**.

| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | riga | scelte di riga per seme | concordanza per seme | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | peso proprio del legame fra finali | 0.554 | 0.673 (0.644–0.714) | 0.559 | 17.0/18 | 2.5/8 | 0/4 | 4, 4, 2, 3 | 0.059, 0.063, 0.059, 0.056 | 0.47 | 0.52 | 0.65 | 0.59 | 0.52 | 0.65 | 0.59 | 0.67 | 0.69 |
| R2 | R1 e scelte di riga | 0.582 | 0.671 (0.596–0.713) | 0.559 | 16.0/18 | 2.8/8 | 0/4 | 8, 11, 10, 8 | 0.057, 0.060, 0.058, 0.058 | 0.47 | 0.52 | 0.65 | 0.62 | 0.50 | 0.62 | 0.60 | 0.68 | 0.67 |

## Materie mancate (su 4 semi) e valori grezzi

**R1.** profilo pagina (4), dispersione delle lunghezze (4), scelte di riga (4), concordanza delle desinenze (4), coppie viste altrove (4), parole rare per pagina (3), prime righe come registro (3).

**R2.** gradiente (4), profilo pagina (4), dispersione delle lunghezze (4), prime righe come registro (4), concordanza delle desinenze (4), coppie viste altrove (4), parole rare per pagina (3), scelte di riga (2).

| valore grezzo | Voynich | R1 | R2 |
|---|---|---|---|
| parole | 3.486e+04 | 3.486e+04 | 3.486e+04 |
| h2 | 2.236 | 2.272 | 2.272 |
| lung_media | 4.461 | 4.476 | 4.476 |
| tipi_su_parole | 0.2098 | 0.1984 | 0.1985 |
| hapax | 0.6795 | 0.7251 | 0.7252 |
| identiche_immediate | 0.009371 | 0.01006 | 0.008403 |
| identiche_vs_riga | 1.009 | 1.163 | 0.8806 |
| somiglianza_riga | 0.03845 | 0.03862 | 0.04248 |
| somiglianza_riga_sotto | 0.03987 | 0.03472 | 0.03457 |
| somiglianza_6_righe | 0.03353 | 0.02816 | 0.02824 |
| spazio_spiegato | 0.6636 | 0.6383 | 0.6381 |
| confine | 0.1881 | 0.1964 | 0.2104 |
| unione_attestata | 0.08766 | 0.08593 | 0.08587 |
| unione_caso | 0.04464 | 0.03901 | 0.03855 |
| ordine_rispettato | 0.7847 | 0.7564 | 0.7564 |
| anagrammi | 0.3535 | 0.2867 | 0.2867 |
| hapax_1000 | 0.7352 | 0.6969 | 0.6978 |
| hapax_34000 | 0.6778 | 0.7371 | 0.7372 |
| V2_ricambio_k1_meno_k20 | 0.1058 | 0.1 | 0.1025 |
| V3_R | 1.017 | 0.6305 | 0.6348 |
| V3_quota_media | 0.06054 | 0.04369 | 0.04365 |
| lung_media_segni | 4.461 | 4.476 | 4.476 |
| lung_dev_segni | 1.645 | 1.645 | 1.645 |
| V6_autocorrelazione_lunghezze | 0.1498 | 0.175 | 0.1788 |
| V7_zipf | -1.041 | -1.027 | -1.027 |
| V8_forma | 0 | 0.03385 | 0.03385 |
| verticale | 1.028 | 1.031 | 1.031 |
| formule_terne | 5.195 | 6.122 | 5.927 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| | R1 | R2 |
|---|---|---|
| S1 | 1.083 | 1.046 |
| R_riga | 0.015 | 0.009 |
| A | 0.977 | 0.980 |
| scelte_per_riga | 1.000 | 1.500 |
| r_righe_consecutive | 0.109 | 0.099 |

| materia aggiunta | Voynich | R1 | R2 |
|---|---|---|---|
| parole rare per pagina | 1.958 | 5.04 | 5.279 |
| tipi su parole nella pagina | 0.7559 | 0.7424 | 0.7424 |
| uniche nella pagina | 0.6359 | 0.6142 | 0.6142 |
| dispersione delle lunghezze | 1.579 | 1.629 | 1.629 |
| prime righe come registro | 4.724 | 2.801 | 2.338 |
| scelte di riga | 12 | 3.25 | 9.25 |
| concordanza delle desinenze | 0.04335 | 0.05928 | 0.05827 |
| coppie viste altrove | 0.2213 | 0.2486 | 0.2494 |

## Caratteristiche più pesanti (seme 1)

**R1**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G6 coppie viste altrove | +2.05 | 0.2213 | 0.2481 |
| e266 | G9 JSD pagina-manoscritto | +2.04 | 0.0402 | 0.0458 |
| e266 | G9 JSD prima-seconda meta | -1.67 | 0.0503 | 0.0352 |
| e266 | G6 somiglianza a distanza 2 | -1.67 | 0.2198 | 0.2079 |
| e266 | G4 unioni attestate | -1.53 | 0.0916 | 0.0912 |
| e266 | G2 cth+y | -1.48 | 0.0042 | 0.0041 |
| e266 | G3 lunghezza deviazione | +1.24 | 1.5790 | 1.6192 |
| e266 | G2 p+ch | -0.96 | 0.0052 | 0.0045 |
| e266 | G2 ch+a | -0.93 | 0.0052 | 0.0046 |
| e266 | G3 tipi su parole | +0.92 | 0.7559 | 0.7400 |
| e231 | G2 cth+y | -1.25 | 0.0042 | 0.0041 |
| e231 | G2 y+o | +1.02 | 0.0004 | 0.0011 |
| e231 | G3 uniche nella pagina | -0.98 | 0.6359 | 0.6120 |
| e231 | G3 lunghezza deviazione | +0.91 | 1.5790 | 1.6192 |
| e231 | G4 inizio p | -0.89 | 0.0769 | 0.0604 |
| e231 | G2 p+ch | -0.89 | 0.0052 | 0.0045 |

**R2**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G6 coppie viste altrove | +2.02 | 0.2213 | 0.2545 |
| e266 | G9 JSD pagina-manoscritto | +1.89 | 0.0402 | 0.0458 |
| e266 | G2 cth+y | -1.64 | 0.0042 | 0.0041 |
| e266 | G9 JSD prima-seconda meta | -1.58 | 0.0503 | 0.0382 |
| e266 | G3 lunghezza deviazione | +1.45 | 1.5790 | 1.6192 |
| e266 | G4 unioni attestate | -1.24 | 0.0916 | 0.0912 |
| e266 | G4 inizio p | -1.14 | 0.0769 | 0.0615 |
| e266 | G8 t prime righe meno altre | +1.07 | 0.0002 | 0.0121 |
| e266 | G6 somiglianza a distanza 2 | -1.02 | 0.2198 | 0.2146 |
| e266 | G2 y+o | +1.01 | 0.0004 | 0.0011 |
| e231 | G2 cth+y | -1.48 | 0.0042 | 0.0041 |
| e231 | G4 inizio p | -1.33 | 0.0769 | 0.0615 |
| e231 | G2 y+o | +1.18 | 0.0004 | 0.0011 |
| e231 | G3 fra le 100 piu frequenti | +1.17 | 0.4244 | 0.4465 |
| e231 | G3 lunghezza deviazione | +1.12 | 1.5790 | 1.6192 |
| e231 | G3 uniche nella pagina | -0.90 | 0.6359 | 0.6120 |

