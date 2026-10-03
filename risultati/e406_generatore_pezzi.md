# e406 — Il generatore intero a pezzi

Semi 1–4 (medie). Riferimenti sugli stessi semi: v5 0,812 / 0,918 (pagella 16,5); C5 dell'e404b 0,711 / 0,813 (14,5); sacco vero ridisposto 0,533 / 0,659 (14,8). Preregistrazione: `preregistrazioni/e406.md`.

Pesi dei legami regolati sul sacco generato (seme 11): bordi 0.767, unione 2.675, coppia 0.000, identica -0.554; scarto massimo 0.138: **non converge**. Pesi dell'e401b: bordi 0.712, unione 0.587, coppia 0.493, identica -0.552.

| strato | che cosa | AUC e231 (prevista) | AUC e266 (min–max; prevista) | solo sacco | pagella | estese | riga | trigrammi dal Voynich | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | posti delle parole nuove veri; pesi della disposizione dell'e401b | 0.667 (0.62–0.70) | 0.747 (0.719–0.787; 0.72–0.80) | 0.542 | 14.2/18 | 4.8/8 | 0/4 | 0.010 | 0.51 | 0.50 | 0.62 | 0.68 | 0.50 | 0.61 | 0.59 | 0.66 | 0.66 |
| P2 | posti dal modello; pesi dell'e401b | 0.670 (0.59–0.73) | 0.744 (0.704–0.773; 0.69–0.83) | 0.523 | 14.2/18 | 4.5/8 | 0/4 | 0.011 | 0.50 | 0.47 | 0.64 | 0.68 | 0.52 | 0.62 | 0.57 | 0.65 | 0.64 |
| P3 | posti dal modello; pesi regolati sul sacco generato | 0.558 (0.58–0.66) | 0.703 (0.674–0.738; 0.68–0.77) | 0.523 | 13.8/18 | 4.0/8 | 0/4 | 0.007 | 0.50 | 0.47 | 0.64 | 0.56 | 0.53 | 0.66 | 0.61 | 0.68 | 0.64 |

Configurazione scelta per la v8 secondo la preregistrazione: **P3**.

## Materie mancate (su 4 semi) e valori grezzi della pagella

**P1.** legame (4), profilo pagina (4), verticale (4), scelte di riga (4), concordanza delle desinenze (4), parole rare per pagina (3), gradiente (2), prime righe come registro (2), ripetizione (1).

**P2.** legame (4), profilo pagina (4), scelte di riga (4), concordanza delle desinenze (4), gradiente (3), verticale (3), prime righe come registro (3), parole rare per pagina (2), ripetizione (1), coppie viste altrove (1).

**P3.** legame (4), profilo pagina (4), verticale (4), scelte di riga (4), concordanza delle desinenze (4), coppie viste altrove (4), formule (3), gradiente (2), parole rare per pagina (2), prime righe come registro (2).

| valore grezzo | Voynich | P1 | P2 | P3 |
|---|---|---|---|---|
| parole | 3.486e+04 | 3.486e+04 | 3.486e+04 | 3.486e+04 |
| h2 | 2.236 | 2.279 | 2.273 | 2.273 |
| lung_media | 4.461 | 4.484 | 4.482 | 4.482 |
| tipi_su_parole | 0.2098 | 0.2028 | 0.2007 | 0.2009 |
| hapax | 0.6795 | 0.7295 | 0.7275 | 0.7281 |
| identiche_immediate | 0.009371 | 0.01022 | 0.01005 | 0.008476 |
| identiche_vs_riga | 1.009 | 1.172 | 1.148 | 1.021 |
| somiglianza_riga | 0.03845 | 0.04183 | 0.03878 | 0.03815 |
| somiglianza_riga_sotto | 0.03987 | 0.03559 | 0.03264 | 0.03219 |
| somiglianza_6_righe | 0.03353 | 0.02918 | 0.02679 | 0.02669 |
| spazio_spiegato | 0.6636 | 0.6459 | 0.6466 | 0.6453 |
| confine | 0.1881 | 0.05647 | 0.05626 | 0.05739 |
| unione_attestata | 0.08766 | 0.0609 | 0.06181 | 0.07828 |
| unione_caso | 0.04464 | 0.03383 | 0.03364 | 0.03484 |
| ordine_rispettato | 0.7847 | 0.7703 | 0.7689 | 0.7689 |
| anagrammi | 0.3535 | 0.2915 | 0.2957 | 0.2957 |
| hapax_1000 | 0.7352 | 0.6996 | 0.6959 | 0.6966 |
| hapax_34000 | 0.6778 | 0.7397 | 0.7391 | 0.739 |
| V2_ricambio_k1_meno_k20 | 0.1058 | 0.09592 | 0.09318 | 0.09209 |
| V3_R | 1.017 | 0.5618 | 0.6102 | 0.591 |
| V3_quota_media | 0.06054 | 0.04299 | 0.04127 | 0.04148 |
| lung_media_segni | 4.461 | 4.484 | 4.482 | 4.482 |
| lung_dev_segni | 1.645 | 1.637 | 1.633 | 1.633 |
| V6_autocorrelazione_lunghezze | 0.1498 | 0.1598 | 0.1646 | 0.2097 |
| V7_zipf | -1.041 | -1.025 | -1.022 | -1.022 |
| V8_forma | 0 | 0.04832 | 0.05145 | 0.05145 |
| verticale | 1.028 | 1.009 | 1.008 | 1.003 |
| formule_terne | 5.195 | 6.307 | 6.488 | 8.663 |

| materia aggiunta | Voynich | P1 | P2 | P3 |
|---|---|---|---|---|
| parole rare per pagina | 1.958 | 6.62 | 5.319 | 5.584 |
| tipi su parole nella pagina | 0.7559 | 0.7459 | 0.7454 | 0.7454 |
| uniche nella pagina | 0.6359 | 0.6177 | 0.6164 | 0.6164 |
| dispersione delle lunghezze | 1.579 | 1.609 | 1.608 | 1.608 |
| prime righe come registro | 4.724 | 2.288 | 2.243 | 3.124 |
| scelte di riga | 12 | 5 | 4.5 | 5.25 |
| concordanza delle desinenze | 0.04335 | 0.0893 | 0.0932 | 0.1059 |
| coppie viste altrove | 0.2213 | 0.2354 | 0.2359 | 0.2511 |

## Pannello (media delle pagine)

| misura | Voynich | P1 | P2 | P3 |
|---|---|---|---|---|
| G4 inizio p | 0.0769 | 0.0801 | 0.0755 | 0.0774 |
| G4 inizio t | 0.1052 | 0.0987 | 0.0945 | 0.0991 |
| G4 inizio ch | 0.0355 | 0.0364 | 0.0387 | 0.0361 |
| G4 fine m | 0.1392 | 0.1401 | 0.1511 | 0.1560 |
| G7 ultime in m | 0.1392 | 0.1401 | 0.1511 | 0.1560 |
| G7 lunghezza prima parola | 4.8197 | 4.8057 | 4.7920 | 4.8240 |
| G7 lunghezza ultima parola | 4.2931 | 4.3957 | 4.3394 | 4.4764 |
| G4 unioni attestate | 0.0916 | 0.0646 | 0.0651 | 0.0841 |
| G4 somiglianza fra vicine | 0.2181 | 0.2156 | 0.2145 | 0.2130 |
| G6 coppie viste altrove | 0.2213 | 0.2354 | 0.2359 | 0.2511 |
| G6 coppie identiche | 0.0097 | 0.0102 | 0.0097 | 0.0086 |
| G8 p prime righe meno altre | 0.0331 | 0.0327 | 0.0311 | 0.0314 |
| G8 lunghezza parole prime righe | 4.6323 | 4.8266 | 4.7778 | 4.8310 |
| G9 JSD prima-seconda meta | 0.0503 | 0.0365 | 0.0372 | 0.0377 |

## Caratteristiche più pesanti (seme 1)

**P1**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G4 unioni attestate | -3.81 | 0.0916 | 0.0654 |
| e266 | G6 coppie viste altrove | +2.08 | 0.2213 | 0.2381 |
| e266 | G9 JSD prima-seconda meta | -2.07 | 0.0503 | 0.0365 |
| e266 | G6 somiglianza a distanza 2 | -1.91 | 0.2198 | 0.2098 |
| e266 | G9 JSD pagina-manoscritto | +1.21 | 0.0402 | 0.0436 |
| e266 | G3 fra le 100 piu frequenti | +1.12 | 0.4244 | 0.4347 |
| e266 | G3 lunghezza deviazione | +0.96 | 1.5790 | 1.6014 |
| e266 | G1 s | -0.88 | 0.0179 | 0.0187 |
| e266 | G8 k prime righe meno altre | +0.85 | -0.0236 | -0.0120 |
| e266 | G7 lunghezza prima parola | -0.79 | 4.8197 | 4.7860 |
| e231 | G4 unioni attestate | -3.33 | 0.0916 | 0.0654 |
| e231 | G3 fra le 100 piu frequenti | +2.40 | 0.4244 | 0.4347 |
| e231 | G3 lunghezza media | -1.41 | 4.2913 | 4.3296 |
| e231 | G1 p | +1.11 | 0.0075 | 0.0084 |
| e231 | G2 sh+o | -0.97 | 0.0129 | 0.0120 |
| e231 | G2 k+a | -0.95 | 0.0175 | 0.0174 |

**P2**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G4 unioni attestate | -3.71 | 0.0916 | 0.0673 |
| e266 | G6 coppie viste altrove | +2.16 | 0.2213 | 0.2350 |
| e266 | G6 somiglianza a distanza 2 | -1.70 | 0.2198 | 0.2081 |
| e266 | G9 JSD prima-seconda meta | -1.45 | 0.0503 | 0.0367 |
| e266 | G3 uniche nel testo | -1.11 | 0.1461 | 0.1462 |
| e266 | G9 JSD pagina-manoscritto | +1.05 | 0.0402 | 0.0403 |
| e266 | G3 lunghezza media | -1.04 | 4.2913 | 4.3343 |
| e266 | G3 lunghezza deviazione | +0.93 | 1.5790 | 1.6043 |
| e266 | G2 q+o | -0.89 | 0.0361 | 0.0339 |
| e266 | G2 ckh+y | -0.86 | 0.0036 | 0.0032 |
| e231 | G4 unioni attestate | -3.69 | 0.0916 | 0.0673 |
| e231 | G3 fra le 100 piu frequenti | +1.87 | 0.4244 | 0.4358 |
| e231 | G3 lunghezza media | -1.86 | 4.2913 | 4.3343 |
| e231 | G3 uniche nella pagina | -1.21 | 0.6359 | 0.6163 |
| e231 | G3 uniche nel testo | -1.09 | 0.1461 | 0.1462 |
| e231 | G2 d+y | -1.04 | 0.0432 | 0.0411 |

**P3**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G6 coppie viste altrove | +3.40 | 0.2213 | 0.2543 |
| e266 | G6 somiglianza a distanza 2 | -1.78 | 0.2198 | 0.2057 |
| e266 | G4 unioni attestate | -1.56 | 0.0916 | 0.0862 |
| e266 | G3 uniche nel testo | -1.25 | 0.1461 | 0.1462 |
| e266 | G7 lunghezza ultima parola | +1.20 | 4.2931 | 4.4684 |
| e266 | G2 d+y | -1.05 | 0.0432 | 0.0411 |
| e266 | G3 tipi su parole | +1.03 | 0.7559 | 0.7457 |
| e266 | G9 JSD prima-seconda meta | -1.00 | 0.0503 | 0.0391 |
| e266 | G1 s | -0.96 | 0.0179 | 0.0185 |
| e266 | G2 d+e | +0.93 | 0.0008 | 0.0012 |
| e231 | G3 fra le 100 piu frequenti | +1.75 | 0.4244 | 0.4358 |
| e231 | G3 uniche nella pagina | -1.43 | 0.6359 | 0.6163 |
| e231 | G3 tipi su parole | +1.31 | 0.7559 | 0.7457 |
| e231 | G2 d+y | -1.27 | 0.0432 | 0.0411 |
| e231 | G3 uniche nel testo | -1.20 | 0.1461 | 0.1462 |
| e231 | G4 inizio y | +1.02 | 0.1476 | 0.1593 |

