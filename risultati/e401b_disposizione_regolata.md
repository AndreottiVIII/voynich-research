# e401b — La disposizione con la dose dei legami regolata sul pannello

Sacco di parole vero e impaginazione vera; posti (8 tipi) e legami fra vicine con i pesi regolati perché quattro valori tornino quelli del Voynich. Riferimenti: e401 D2 0,855 e D3 0,847 (e231: 0,771 e 0,729); solo righe rimescolate 0,595. Preregistrazione: `preregistrazioni/e401b.md`.

## Regolazione (seme 11, 30 passate)

| giro | bordi | unione | coppia | identica | unioni attestate | coppie viste altrove | coppie identiche | somiglianza fra vicine | scarto massimo |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.500 | 0.500 | 0.500 | 0.000 | 0.0866 | 0.2135 | 0.0156 | 0.2182 | 0.600 |
| 1 | 0.499 | 0.556 | 0.554 | -0.470 | 0.0881 | 0.2150 | 0.0103 | 0.2121 | 0.057 |
| 2 | 0.582 | 0.595 | 0.597 | -0.526 | 0.0942 | 0.2191 | 0.0095 | 0.2147 | 0.029 |
| 3 | 0.629 | 0.566 | 0.612 | -0.499 | 0.0916 | 0.2254 | 0.0094 | 0.2157 | 0.036 |
| 4 | 0.663 | 0.566 | 0.585 | -0.462 | 0.0932 | 0.2241 | 0.0116 | 0.2183 | 0.192 |
| 5 | 0.660 | 0.549 | 0.566 | -0.638 | 0.0922 | 0.2231 | 0.0088 | 0.2164 | 0.098 |
| 6 | 0.683 | 0.542 | 0.553 | -0.535 | 0.0917 | 0.2227 | 0.0103 | 0.2168 | 0.058 |
| 7 | 0.702 | 0.541 | 0.544 | -0.591 | 0.0870 | 0.2250 | 0.0087 | 0.2188 | 0.101 |
| 8 | 0.692 | 0.592 | 0.519 | -0.485 | 0.0920 | 0.2252 | 0.0104 | 0.2166 | 0.069 |
| 9 | 0.712 | 0.587 | 0.493 | -0.552 | 0.0923 | 0.2224 | 0.0096 | 0.2165 | 0.016 |
| Voynich | | | | | 0.0916 | 0.2213 | 0.0097 | 0.2181 | |

Pesi scelti: bordi 0.712, unione 0.587, coppia 0.493, identica -0.552. Scarto massimo 0.016: la regolazione converge.

## Strato D4 (semi 1–4, medie)

| AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.533 | 0.659 (0.638–0.667) | 0.68–0.78 | 14.8/18 | 5.2/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.54 | 0.53 | 0.59 | 0.56 | 0.64 | 0.64 |

Gruppi dell'e231: G1 0.50, G2 0.50, G3 0.50, G4 0.54, G5 0.53.

Materie mancate in almeno un seme: concordanza delle desinenze, formule, gradiente, legame, prime righe come registro, ripetizione, scelte di riga, verticale.

## Pannello (media delle pagine)

| misura | Voynich | D4 |
|---|---|---|
| G4 inizio p | 0.0769 | 0.0729 |
| G4 inizio t | 0.1052 | 0.0993 |
| G4 inizio ch | 0.0355 | 0.0363 |
| G4 fine m | 0.1392 | 0.1446 |
| G7 ultime in m | 0.1392 | 0.1446 |
| G7 lunghezza prima parola | 4.8197 | 4.7674 |
| G7 lunghezza ultima parola | 4.2931 | 4.2514 |
| G4 unioni attestate | 0.0916 | 0.0919 |
| G4 somiglianza fra vicine | 0.2181 | 0.2161 |
| G6 coppie viste altrove | 0.2213 | 0.2247 |
| G6 coppie identiche | 0.0097 | 0.0102 |
| G8 p prime righe meno altre | 0.0331 | 0.0289 |
| G8 lunghezza parole prime righe | 4.6323 | 4.7251 |
| G9 JSD prima-seconda meta | 0.0503 | 0.0378 |

## Caratteristiche più pesanti (giudice e266, seme 1)

| caratteristica | coefficiente | Voynich | disposizione |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.44 | 0.0503 | 0.0373 |
| G6 somiglianza a distanza 2 | -1.30 | 0.2198 | 0.2070 |
| G3 uniche nella pagina | +0.88 | 0.6359 | 0.6359 |
| G4 inizio s | +0.80 | 0.0804 | 0.1053 |
| G2 c+t | -0.78 | 0.0006 | 0.0006 |
| G8 p prime righe meno altre | -0.73 | 0.0331 | 0.0285 |
| G2 a+m | -0.68 | 0.0057 | 0.0057 |
| G1 p | +0.64 | 0.0075 | 0.0075 |
