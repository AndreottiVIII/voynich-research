# e404 — Il sacco, secondo pezzo: le parole note della pagina, e il primo generatore intero a pezzi

Impaginazione vera; semi 1–4 (medie). Solo sacco: pavimento 0,50; v5 0,794; modello del Voynich 0,959; parole nuove da sole 0,644 (e403b). Preregistrazione: `preregistrazioni/e404.md`.

Regolazione di θ sul pannello (seme 11): θ = 765.0, tipi su parole 0.7504 (Voynich 0.7559), scarto -0.007: converge.

| strato | che cosa | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|---|
| K1 | lessico di sezione, senza ripetizione | 0.786 (0.764–0.802) | 0.80–0.92 | 0.43 | 0.37 | 0.65 | 0.75 |
| K2 | lessico di sezione con ripetizione | 0.777 (0.743–0.799) | 0.60–0.75 | 0.41 | 0.36 | 0.71 | 0.74 |
| K4 | K2 e parole nuove inventate | 0.756 (0.739–0.795) | 0.68–0.80 | 0.58 | 0.49 | 0.70 | 0.75 |
| K5 | K4 ridisposto (generatore intero a pezzi) | 0.756 (0.739–0.795) | — | 0.58 | 0.49 | 0.70 | 0.75 |

## Valori di pagina (media delle pagine)

| | G3 tipi su parole | G3 uniche nella pagina | G3 uniche nel testo | G3 fra le 100 piu frequenti | G3 lunghezza media | G3 lunghezza deviazione | G9 JSD pagina-manoscritto |
|---|---|---|---|---|---|---|---|
| Voynich | 0.7559 | 0.6359 | 0.1461 | 0.4244 | 4.2913 | 1.5790 | 0.0402 |
| K1 | 0.7850 | 0.6685 | 0.1553 | 0.4290 | 4.2940 | 1.5941 | 0.0224 |
| K2 | 0.7474 | 0.6102 | 0.1559 | 0.4340 | 4.2820 | 1.5901 | 0.0229 |
| K4 | 0.7493 | 0.6131 | 0.1556 | 0.4280 | 4.3108 | 1.6145 | 0.0225 |
| K5 | 0.7493 | 0.6131 | 0.1556 | 0.4280 | 4.3108 | 1.6145 | 0.0225 |

## K5: il generatore intero a pezzi, giudici interi e pagelle

Per confronto, sugli stessi semi: v5 0,812 / 0,918 (pagella 16,5/18); v5 ridisposta 0,797 / 0,842; sacco vero ridisposto 0,533 / 0,659.

| AUC e231 (prevista) | AUC e266 (prevista) | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.716 (0.72–0.84) | 0.857 (0.78–0.90) | 11.5/18 | 4.8/8 | 0/4 | 0.58 | 0.49 | 0.70 | 0.76 | 0.53 | 0.73 | 0.58 | 0.66 | 0.75 |

Materie mancate in almeno un seme: concordanza delle desinenze, formule, gradiente, legame, omogeneità, parole rare per pagina, prime righe come registro, profilo pagina, ripetizione, scelte di riga, verticale.

| giudice | caratteristica | coefficiente | Voynich | K5 |
|---|---|---|---|---|
| e266 | G4 unioni attestate | -2.71 | 0.0916 | 0.0623 |
| e266 | G9 JSD pagina-manoscritto | -2.65 | 0.0402 | 0.0225 |
| e266 | G6 somiglianza a distanza 2 | -2.40 | 0.2198 | 0.1905 |
| e266 | G6 coppie viste altrove | +1.03 | 0.2213 | 0.2290 |
| e266 | G3 lunghezza media | -0.84 | 4.2913 | 4.3081 |
| e266 | G2 d+a | -0.84 | 0.0373 | 0.0347 |
| e266 | G3 uniche nella pagina | -0.81 | 0.6359 | 0.6095 |
| e266 | G8 k prime righe meno altre | +0.77 | -0.0236 | -0.0116 |
| e266 | G8 f prime righe meno altre | -0.76 | 0.0103 | 0.0088 |
| e266 | G2 e+ch | +0.71 | 0.0008 | 0.0011 |
| e231 | G4 unioni attestate | -3.62 | 0.0916 | 0.0623 |
| e231 | G4 somiglianza fra vicine | -1.88 | 0.2181 | 0.2021 |
| e231 | G3 lunghezza media | -1.86 | 4.2913 | 4.3081 |
| e231 | G3 uniche nella pagina | -1.65 | 0.6359 | 0.6095 |
| e231 | G3 fra le 100 piu frequenti | +1.36 | 0.4244 | 0.4291 |
| e231 | G3 lunghezza deviazione | +1.14 | 1.5790 | 1.6120 |

## Caratteristiche più pesanti del solo sacco (seme 1)

**K1 — lessico di sezione, senza ripetizione**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -5.97 | 0.0402 | 0.0222 |
| G3 tipi su parole | +1.48 | 0.7559 | 0.7828 |
| G3 lunghezza media | -1.35 | 4.2913 | 4.3001 |
| G3 uniche nel testo | +1.19 | 0.1461 | 0.1556 |
| G3 fra le 100 piu frequenti | +0.86 | 0.4244 | 0.4275 |
| G2 cth+o | +0.76 | 0.0039 | 0.0041 |
| G2 k+a | +0.64 | 0.0175 | 0.0181 |
| G2 ch+p | +0.63 | 0.0002 | 0.0003 |
| G1 h | +0.60 | 0.0015 | 0.0015 |
| G2 k+ch | -0.55 | 0.0115 | 0.0117 |

**K2 — lessico di sezione con ripetizione**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -5.69 | 0.0402 | 0.0229 |
| G3 uniche nel testo | +1.98 | 0.1461 | 0.1569 |
| G3 uniche nella pagina | -1.77 | 0.6359 | 0.6069 |
| G3 lunghezza media | -1.30 | 4.2913 | 4.2780 |
| G2 ch+a | +0.87 | 0.0052 | 0.0056 |
| G2 p+a | +0.86 | 0.0010 | 0.0011 |
| G2 a+l | -0.72 | 0.0178 | 0.0167 |
| G3 tipi su parole | +0.71 | 0.7559 | 0.7447 |
| G2 r+o | +0.59 | 0.0023 | 0.0025 |
| G1 a | -0.59 | 0.0766 | 0.0771 |

**K4 — K2 e parole nuove inventate**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -5.17 | 0.0402 | 0.0225 |
| G3 uniche nella pagina | -1.24 | 0.6359 | 0.6095 |
| G3 lunghezza media | -1.10 | 4.2913 | 4.3081 |
| G2 ch+a | +1.00 | 0.0052 | 0.0061 |
| G3 tipi su parole | +0.98 | 0.7559 | 0.7475 |
| G3 fra le 100 piu frequenti | +0.87 | 0.4244 | 0.4291 |
| G2 e+y | -0.85 | 0.0271 | 0.0263 |
| G2 d+sh | +0.84 | 0.0017 | 0.0018 |
| G2 o+l | -0.78 | 0.0473 | 0.0475 |
| G2 l+ch | +0.76 | 0.0037 | 0.0048 |

**K5 — K4 ridisposto (generatore intero a pezzi)**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -5.17 | 0.0402 | 0.0225 |
| G3 uniche nella pagina | -1.24 | 0.6359 | 0.6095 |
| G3 lunghezza media | -1.10 | 4.2913 | 4.3081 |
| G2 ch+a | +1.00 | 0.0052 | 0.0061 |
| G3 tipi su parole | +0.98 | 0.7559 | 0.7475 |
| G3 fra le 100 piu frequenti | +0.87 | 0.4244 | 0.4291 |
| G2 e+y | -0.85 | 0.0271 | 0.0263 |
| G2 d+sh | +0.84 | 0.0017 | 0.0018 |
| G2 o+l | -0.78 | 0.0473 | 0.0475 |
| G2 l+ch | +0.76 | 0.0037 | 0.0048 |

