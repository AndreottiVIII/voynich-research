# e402 — Quanto costa il sacco di pagina dei due generatori esistenti

Corpo della v5 e modello del Voynich, semi 1–4 (medie): testo originale e lo stesso testo con le parole di ogni pagina ridisposte dal modello dell'e401b. "Solo sacco" = giudice dell'e266 sulle sole caratteristiche che non dipendono dall'ordine (G1, G2, G3, JSD pagina-manoscritto). Riferimento: sacco vero ridisposto 0,533 / 0,659 (e401b). Preregistrazione: `preregistrazioni/e402.md`.

| testo | AUC e231 | AUC e266 (min–max) | prevista e266 | solo sacco | previsto | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v5 originale | 0.812 | 0.918 (0.913–0.925) | 0.90–0.94 | 0.794 | 0.80–0.88 | 16.5/18 | 3.0/8 | 0/4 | 0.63 | 0.65 | 0.83 | 0.61 | 0.50 | 0.71 | 0.61 | 0.87 | 0.60 |
| v5 ridisposto | 0.797 | 0.842 (0.825–0.854) | 0.84–0.92 | 0.794 | 0.80–0.88 | 13.5/18 | 1.0/8 | 0/4 | 0.63 | 0.65 | 0.83 | 0.64 | 0.51 | 0.70 | 0.67 | 0.67 | 0.67 |
| modello originale | 0.932 | 0.989 (0.986–0.994) | 0.97–1.00 | 0.959 | 0.88–0.95 | 7.5/18 | 3.0/8 | 0/4 | 0.70 | 0.74 | 0.89 | 0.86 | 0.54 | 0.78 | 0.82 | 0.77 | 0.93 |
| modello ridisposto | 0.894 | 0.968 (0.960–0.974) | 0.90–0.97 | 0.959 | 0.88–0.95 | 9.0/18 | 2.2/8 | 0/4 | 0.70 | 0.74 | 0.89 | 0.75 | 0.50 | 0.77 | 0.73 | 0.73 | 0.92 |

## Pannello (media delle pagine)

| misura | Voynich | v5 originale | v5 ridisposto | modello originale | modello ridisposto |
|---|---|---|---|---|---|
| G4 inizio p | 0.0769 | 0.0849 | 0.0858 | 0.0717 | 0.0918 |
| G4 inizio t | 0.1052 | 0.0968 | 0.1067 | 0.0795 | 0.1074 |
| G4 inizio ch | 0.0355 | 0.0400 | 0.0371 | 0.0739 | 0.0344 |
| G4 fine m | 0.1392 | 0.1390 | 0.1922 | 0.0912 | 0.1552 |
| G7 ultime in m | 0.1392 | 0.1390 | 0.1922 | 0.0912 | 0.1552 |
| G7 lunghezza prima parola | 4.8197 | 4.6858 | 4.7064 | 5.0708 | 5.1000 |
| G7 lunghezza ultima parola | 4.2931 | 4.1418 | 4.1944 | 4.6599 | 4.6419 |
| G4 unioni attestate | 0.0916 | 0.1022 | 0.0949 | 0.0593 | 0.0665 |
| G4 somiglianza fra vicine | 0.2181 | 0.2124 | 0.2093 | 0.2092 | 0.1971 |
| G6 coppie viste altrove | 0.2213 | 0.2239 | 0.2364 | 0.2276 | 0.1957 |
| G6 coppie identiche | 0.0097 | 0.0184 | 0.0163 | 0.0130 | 0.0094 |
| G8 p prime righe meno altre | 0.0331 | 0.0125 | 0.0297 | 0.0190 | 0.0332 |
| G8 lunghezza parole prime righe | 4.6323 | 4.2417 | 4.6417 | 4.8850 | 5.0621 |
| G9 JSD prima-seconda meta | 0.0503 | 0.0407 | 0.0348 | 0.0369 | 0.0342 |

## Perché: materie mancate e caratteristiche più pesanti (primo seme)

**v5 originale.** Materie mancate in almeno un seme: curva piatta, dispersione delle lunghezze, gradiente, parole rare per pagina, prime righe come registro, profilo pagina, tipi su parole nella pagina, uniche nella pagina.

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G8 p prime righe meno altre | -2.12 | 0.0331 | 0.0116 |
| e266 | G8 k prime righe meno altre | +1.13 | -0.0236 | 0.0006 |
| e266 | G3 lunghezza deviazione | +1.12 | 1.5790 | 1.6640 |
| e266 | G3 tipi su parole | -0.99 | 0.7559 | 0.6811 |
| e266 | G3 uniche nel testo | -0.95 | 0.1461 | 0.1281 |
| e266 | G8 f prime righe meno altre | -0.93 | 0.0103 | 0.0025 |
| e266 | G3 uniche nella pagina | -0.91 | 0.6359 | 0.5488 |
| e266 | G2 p+sh | +0.84 | 0.0006 | 0.0015 |
| e266 | G6 coppie identiche | +0.80 | 0.0097 | 0.0167 |
| e266 | G6 coppie viste altrove | -0.74 | 0.2213 | 0.2118 |
| e231 | G3 uniche nel testo | -1.87 | 0.1461 | 0.1281 |
| e231 | G3 lunghezza deviazione | +1.80 | 1.5790 | 1.6640 |
| e231 | G3 tipi su parole | -1.77 | 0.7559 | 0.6811 |
| e231 | G3 fra le 100 piu frequenti | -1.40 | 0.4244 | 0.4218 |
| e231 | G3 lunghezza media | -1.32 | 4.2913 | 4.1571 |
| e231 | G3 uniche nella pagina | -1.26 | 0.6359 | 0.5488 |

**v5 ridisposto.** Materie mancate in almeno un seme: concordanza delle desinenze, curva piatta, dispersione delle lunghezze, formule, gradiente, legame, parole rare per pagina, prime righe come registro, profilo pagina, scelte di riga, tipi su parole nella pagina, uniche nella pagina, verticale.

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G3 uniche nel testo | -1.54 | 0.1461 | 0.1281 |
| e266 | G3 lunghezza deviazione | +1.45 | 1.5790 | 1.6640 |
| e266 | G6 somiglianza a distanza 2 | -1.38 | 0.2198 | 0.2040 |
| e266 | G3 lunghezza media | -1.37 | 4.2913 | 4.1571 |
| e266 | G3 tipi su parole | -1.36 | 0.7559 | 0.6811 |
| e266 | G9 JSD prima-seconda meta | -1.24 | 0.0503 | 0.0355 |
| e266 | G2 p+sh | +1.22 | 0.0006 | 0.0015 |
| e266 | G4 unioni attestate | -1.09 | 0.0916 | 0.0917 |
| e266 | G6 coppie identiche | +1.08 | 0.0097 | 0.0160 |
| e266 | G8 p prime righe meno altre | -1.02 | 0.0331 | 0.0302 |
| e231 | G3 tipi su parole | -1.99 | 0.7559 | 0.6811 |
| e231 | G3 lunghezza deviazione | +1.91 | 1.5790 | 1.6640 |
| e231 | G3 uniche nel testo | -1.63 | 0.1461 | 0.1281 |
| e231 | G3 lunghezza media | -1.58 | 4.2913 | 4.1571 |
| e231 | G3 fra le 100 piu frequenti | -1.40 | 0.4244 | 0.4218 |
| e231 | G3 uniche nella pagina | -1.16 | 0.6359 | 0.5488 |

**modello originale.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, curva piatta, deriva, dispersione delle lunghezze, formule, gradiente, legame, omogeneità, parole rare per pagina, prime righe come registro, profilo pagina, ripetizione, scelte di riga, uniche, verticale.

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD pagina-manoscritto | -1.73 | 0.0402 | 0.0129 |
| e266 | G6 somiglianza a distanza 2 | -1.55 | 0.2198 | 0.1845 |
| e266 | G4 unioni attestate | -1.06 | 0.0916 | 0.0593 |
| e266 | G8 p prime righe meno altre | -0.95 | 0.0331 | 0.0193 |
| e266 | G3 uniche nel testo | -0.79 | 0.1461 | 0.1349 |
| e266 | G3 lunghezza deviazione | +0.73 | 1.5790 | 1.7105 |
| e266 | G6 coppie identiche | +0.62 | 0.0097 | 0.0133 |
| e266 | G6 coppie viste altrove | +0.59 | 0.2213 | 0.2265 |
| e266 | G3 lunghezza media | +0.55 | 4.2913 | 4.5609 |
| e266 | G4 inizio p | -0.51 | 0.0769 | 0.0699 |
| e231 | G4 unioni attestate | -1.72 | 0.0916 | 0.0593 |
| e231 | G3 uniche nel testo | -1.65 | 0.1461 | 0.1349 |
| e231 | G3 lunghezza deviazione | +1.32 | 1.5790 | 1.7105 |
| e231 | G3 lunghezza media | +1.08 | 4.2913 | 4.5609 |
| e231 | G4 inizio d | -0.95 | 0.1585 | 0.1210 |
| e231 | G4 inizio ch | +0.85 | 0.0355 | 0.0718 |

**modello ridisposto.** Materie mancate in almeno un seme: concordanza delle desinenze, coppie viste altrove, curva piatta, deriva, dispersione delle lunghezze, formule, gradiente, legame, omogeneità, parole rare per pagina, prime righe come registro, profilo pagina, ripetizione, scelte di riga, uniche, verticale.

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD pagina-manoscritto | -2.20 | 0.0402 | 0.0129 |
| e266 | G6 somiglianza a distanza 2 | -1.79 | 0.2198 | 0.1848 |
| e266 | G3 lunghezza deviazione | +1.09 | 1.5790 | 1.7105 |
| e266 | G3 uniche nel testo | -1.08 | 0.1461 | 0.1349 |
| e266 | G4 unioni attestate | -0.86 | 0.0916 | 0.0645 |
| e266 | G2 r+y | +0.82 | 0.0019 | 0.0029 |
| e266 | G8 lunghezza parole prime righe | +0.75 | 4.6323 | 5.0707 |
| e266 | G3 tipi su parole | +0.67 | 0.7559 | 0.7634 |
| e266 | G3 lunghezza media | +0.61 | 4.2913 | 4.5609 |
| e266 | G2 k+e | +0.57 | 0.0233 | 0.0296 |
| e231 | G3 uniche nel testo | -1.95 | 0.1461 | 0.1349 |
| e231 | G4 somiglianza fra vicine | -1.56 | 0.2181 | 0.1985 |
| e231 | G3 lunghezza deviazione | +1.50 | 1.5790 | 1.7105 |
| e231 | G3 lunghezza media | +1.45 | 4.2913 | 4.5609 |
| e231 | G4 unioni attestate | -1.36 | 0.0916 | 0.0645 |
| e231 | G2 r+y | +1.12 | 0.0019 | 0.0029 |

