# e404b — Il sacco, terzo pezzo: il carattere della pagina nei segni

Impaginazione vera; semi 1–4 (medie). Riferimenti (e404): K2 0,777, K4 0,756, K5 intero 0,716 / 0,857. Preregistrazione: `preregistrazioni/e404b.md`.

Regolazione di κ e θ insieme sul pannello (seme 11): κ = 0.708, θ = 2280; JSD pagina-manoscritto 0.0406 (Voynich 0.0402), tipi su parole 0.7469 (Voynich 0.7559); scarto massimo 0.012: converge.

| strato | che cosa | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|---|
| C2 | lessico di sezione, ripetizione e carattere; parole nuove vere | 0.482 (0.461–0.518) | 0.58–0.70 | 0.47 | 0.41 | 0.64 | 0.50 |
| C4 | C2 e parole nuove inventate sul profilo generato | 0.645 (0.605–0.678) | 0.64–0.76 | 0.63 | 0.57 | 0.63 | 0.61 |
| C5 | C4 ridisposto (generatore intero a pezzi) | 0.645 (0.605–0.678) | — | 0.63 | 0.57 | 0.63 | 0.61 |

## Valori di pagina (media delle pagine)

| | G3 tipi su parole | G3 uniche nella pagina | G3 uniche nel testo | G3 fra le 100 piu frequenti | G3 lunghezza media | G3 lunghezza deviazione | G9 JSD pagina-manoscritto |
|---|---|---|---|---|---|---|---|
| Voynich | 0.7559 | 0.6359 | 0.1461 | 0.4244 | 4.2913 | 1.5790 | 0.0402 |
| C2 | 0.7437 | 0.6153 | 0.1563 | 0.4390 | 4.3121 | 1.5849 | 0.0418 |
| C4 | 0.7451 | 0.6181 | 0.1559 | 0.4384 | 4.3347 | 1.6180 | 0.0500 |
| C5 | 0.7451 | 0.6181 | 0.1559 | 0.4384 | 4.3347 | 1.6180 | 0.0500 |

## C5: il generatore intero a pezzi, giudici interi e pagelle

Per confronto, sugli stessi semi: K5 (e404) 0,716 / 0,857 (pagella 11,5); v5 0,812 / 0,918 (16,5); sacco vero ridisposto 0,533 / 0,659 (14,8).

| AUC e231 (prevista) | AUC e266 (prevista) | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.711 (0.62–0.74) | 0.813 (0.74–0.85) | 14.5/18 | 4.0/8 | 0/4 | 0.63 | 0.57 | 0.63 | 0.68 | 0.52 | 0.59 | 0.56 | 0.68 | 0.76 |

Materie mancate in almeno un seme: concordanza delle desinenze, coppie viste altrove, dispersione delle lunghezze, gradiente, legame, parole rare per pagina, prime righe come registro, profilo pagina, scelte di riga, verticale.

| misura del pannello | C5 |
|---|---|
| G4 inizio p | 0.0699 |
| G4 inizio t | 0.0979 |
| G4 inizio ch | 0.0367 |
| G4 fine m | 0.1470 |
| G7 ultime in m | 0.1470 |
| G7 lunghezza prima parola | 4.8315 |
| G7 lunghezza ultima parola | 4.3724 |
| G4 unioni attestate | 0.0658 |
| G4 somiglianza fra vicine | 0.2166 |
| G6 coppie viste altrove | 0.2353 |
| G6 coppie identiche | 0.0106 |
| G8 p prime righe meno altre | 0.0288 |
| G8 lunghezza parole prime righe | 4.7777 |
| G9 JSD prima-seconda meta | 0.0327 |

| giudice | caratteristica | coefficiente | Voynich | C5 |
|---|---|---|---|---|
| e266 | G4 unioni attestate | -2.85 | 0.0916 | 0.0678 |
| e266 | G9 JSD pagina-manoscritto | +2.35 | 0.0402 | 0.0505 |
| e266 | G9 JSD prima-seconda meta | -2.26 | 0.0503 | 0.0314 |
| e266 | G6 somiglianza a distanza 2 | -1.41 | 0.2198 | 0.2124 |
| e266 | G6 coppie viste altrove | +1.32 | 0.2213 | 0.2421 |
| e266 | G3 fra le 100 piu frequenti | +1.06 | 0.4244 | 0.4385 |
| e266 | G8 f prime righe meno altre | -0.88 | 0.0103 | 0.0065 |
| e266 | G3 lunghezza deviazione | +0.84 | 1.5790 | 1.6224 |
| e266 | G2 f+ch | +0.79 | 0.0016 | 0.0012 |
| e266 | G2 i+s | +0.78 | 0.0002 | 0.0006 |
| e231 | G4 unioni attestate | -3.00 | 0.0916 | 0.0678 |
| e231 | G3 fra le 100 piu frequenti | +2.10 | 0.4244 | 0.4385 |
| e231 | G1 f | -1.41 | 0.0026 | 0.0018 |
| e231 | G3 lunghezza media | -1.23 | 4.2913 | 4.3569 |
| e231 | G2 f+ch | +1.10 | 0.0016 | 0.0012 |
| e231 | G1 b | -0.99 | 0.0002 | 0.0000 |

## Caratteristiche più pesanti del solo sacco (seme 1)

**C2 — lessico di sezione, ripetizione e carattere; parole nuove vere**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 uniche nella pagina | -2.11 | 0.6359 | 0.6152 |
| G3 tipi su parole | +1.84 | 0.7559 | 0.7435 |
| G3 uniche nel testo | +1.79 | 0.1461 | 0.1557 |
| G1 o | -1.00 | 0.1578 | 0.1537 |
| G2 d+y | +0.85 | 0.0432 | 0.0424 |
| G1 r | +0.80 | 0.0440 | 0.0423 |
| G3 fra le 100 piu frequenti | +0.70 | 0.4244 | 0.4417 |
| G2 p+ch | -0.68 | 0.0052 | 0.0044 |
| G2 cth+y | -0.61 | 0.0042 | 0.0040 |
| G2 e+e | +0.60 | 0.0298 | 0.0308 |

**C4 — C2 e parole nuove inventate sul profilo generato**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | +1.68 | 0.0402 | 0.0505 |
| G1 f | -1.16 | 0.0026 | 0.0018 |
| G1 b | -1.12 | 0.0002 | 0.0000 |
| G3 fra le 100 piu frequenti | +1.12 | 0.4244 | 0.4385 |
| G1 t | +0.99 | 0.0353 | 0.0352 |
| G3 uniche nella pagina | -0.93 | 0.6359 | 0.6218 |
| G2 e+d | -0.85 | 0.0231 | 0.0226 |
| G2 ch+o | -0.82 | 0.0347 | 0.0324 |
| G2 d+y | -0.81 | 0.0432 | 0.0392 |
| G2 f+ch | +0.81 | 0.0016 | 0.0012 |

