# e401 — La disposizione delle parole della pagina

Sacco di parole vero e impaginazione vera per ogni pagina; il modello decide i posti. Semi 1–4 (medie). Riferimenti dall'e400: parole rimescolate nella pagina 0,998 (O4), con le prime righe a parte 0,993 (O3), solo righe rimescolate 0,595 (O1). Preregistrazione: `preregistrazioni/e401.md`.

| strato | che cosa | AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | solo prima riga di paragrafo o no | 0.985 | 0.991 (0.987–0.995) | 0.98–0.99 | 11.5/18 | 4.2/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.99 | 0.56 | 0.71 | 0.93 | 0.60 | 0.65 |
| D2 | otto tipi di posto | 0.771 | 0.855 (0.836–0.880) | 0.70–0.85 | 12.5/18 | 4.0/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.79 | 0.51 | 0.68 | 0.55 | 0.60 | 0.67 |
| D3 | otto tipi di posto e legami fra vicine | 0.729 | 0.847 (0.825–0.866) | 0.62–0.75 | 13.8/18 | 4.8/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.70 | 0.51 | 0.73 | 0.58 | 0.64 | 0.64 |

## Pannello: valori grezzi (media delle pagine)

| misura | Voynich | D1 | D2 | D3 |
|---|---|---|---|---|
| G4 inizio p | 0.0769 | 0.0131 | 0.0742 | 0.0749 |
| G4 inizio t | 0.1052 | 0.0321 | 0.1008 | 0.0989 |
| G4 inizio ch | 0.0355 | 0.1723 | 0.0416 | 0.0383 |
| G4 fine m | 0.1392 | 0.0286 | 0.1378 | 0.1456 |
| G7 ultime in m | 0.1392 | 0.0286 | 0.1378 | 0.1456 |
| G7 lunghezza prima parola | 4.8197 | 4.2856 | 4.7805 | 4.7750 |
| G7 lunghezza ultima parola | 4.2931 | 4.2948 | 4.2325 | 4.2694 |
| G4 unioni attestate | 0.0916 | 0.0495 | 0.0534 | 0.1177 |
| G4 somiglianza fra vicine | 0.2181 | 0.2020 | 0.2038 | 0.2317 |
| G6 coppie viste altrove | 0.2213 | 0.1692 | 0.1826 | 0.2693 |
| G6 coppie identiche | 0.0097 | 0.0081 | 0.0088 | 0.0212 |
| G8 p prime righe meno altre | 0.0331 | 0.0302 | 0.0297 | 0.0297 |
| G8 lunghezza parole prime righe | 4.6323 | 4.6596 | 4.6322 | 4.7389 |
| G9 JSD prima-seconda meta | 0.0503 | 0.0366 | 0.0354 | 0.0378 |

## Perché: materie mancate e caratteristiche più pesanti (giudice e266, primo seme)

**D1 — solo prima riga di paragrafo o no.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, formule, legame, lunghezze vicine, omogeneità, prime righe come registro, scelte di riga, unioni, verticale.

| caratteristica | coefficiente | Voynich | disposizione |
|---|---|---|---|
| G4 unioni attestate | -1.34 | 0.0916 | 0.0490 |
| G4 inizio ch | +1.27 | 0.0355 | 0.1642 |
| G4 fine o | +1.21 | 0.0123 | 0.0383 |
| G4 inizio t | -1.19 | 0.1052 | 0.0316 |
| G4 inizio p | -1.17 | 0.0769 | 0.0122 |
| G7 lunghezza prima parola | -0.94 | 4.8197 | 4.2895 |
| G7 ultime in m | -0.77 | 0.1392 | 0.0307 |
| G4 fine m | -0.77 | 0.1392 | 0.0307 |

**D2 — otto tipi di posto.** Materie mancate in almeno un seme: concordanza delle desinenze, coppie viste altrove, formule, legame, lunghezze vicine, omogeneità, prime righe come registro, scelte di riga, unioni, verticale.

| caratteristica | coefficiente | Voynich | disposizione |
|---|---|---|---|
| G4 unioni attestate | -3.99 | 0.0916 | 0.0522 |
| G9 JSD prima-seconda meta | -1.87 | 0.0503 | 0.0352 |
| G3 fra le 100 piu frequenti | +1.67 | 0.4244 | 0.4244 |
| G6 somiglianza a distanza 2 | -1.60 | 0.2198 | 0.2018 |
| G6 coppie viste altrove | -1.45 | 0.2213 | 0.1863 |
| G9 JSD pagina-manoscritto | +1.42 | 0.0402 | 0.0402 |
| G4 somiglianza fra vicine | -1.21 | 0.2181 | 0.2026 |
| G2 d+o | -0.86 | 0.0054 | 0.0054 |

**D3 — otto tipi di posto e legami fra vicine.** Materie mancate in almeno un seme: concordanza delle desinenze, coppie viste altrove, formule, gradiente, legame, prime righe come registro, ripetizione, scelte di riga, unioni, verticale.

| caratteristica | coefficiente | Voynich | disposizione |
|---|---|---|---|
| G6 coppie viste altrove | +2.95 | 0.2213 | 0.2682 |
| G4 unioni attestate | +2.43 | 0.0916 | 0.1166 |
| G9 JSD prima-seconda meta | -1.73 | 0.0503 | 0.0397 |
| G6 coppie identiche | +1.62 | 0.0097 | 0.0215 |
| G3 fra le 100 piu frequenti | -1.27 | 0.4244 | 0.4244 |
| G3 lunghezza media | +1.00 | 4.2913 | 4.2913 |
| G3 uniche nella pagina | +0.97 | 0.6359 | 0.6359 |
| G9 JSD pagina-manoscritto | -0.94 | 0.0402 | 0.0402 |

