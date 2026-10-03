# e412 — Il giudice forte: coppie viste altrove e differenza fra le due metà della pagina

Semi 1–4 (medie), corpo senza messaggio. Riferimento: G2 dell'e410 (corpo della v11) 0,552 / 0,616, pagella 15,8/18, cancello 3/4. Preregistrazione: `preregistrazioni/e412.md`.

## Regolazione sul pannello (seme 11)

- **M1:** pesi bordi 1.157, unione 0.910, coppia -0.164, identica -0.562, confine 0.685, verticale 0.132, fin_fin 0.000, prima_lettera -1.019, distanza2 0.035, scelte 0.046, scelte_sopra 0.048; scarto massimo 0.136: **non converge**.
  - valori (Voynich): unioni attestate 0.0878 (0.0916); coppie viste altrove 0.2513 (0.2213); coppie identiche 0.0088 (0.0097); somiglianza fra vicine 0.2137 (0.2181); confine 0.1945 (0.1881); verticale 1.0280 (1.0278); concordanza 0.0566 (0.0416); S1 0.4907 (0.5312); somiglianza a distanza 2 0.2202 (0.2198); A 1.0156 (1.0465); varianza per riga 1.1787 (1.1027); r righe consecutive 0.2042 (0.2070); JSD fra le meta 0.0383 (0.0503).
- **M2:** pesi bordi 1.003, unione 0.979, coppia -0.366, identica -0.417, confine 0.742, verticale 0.152, fin_fin 0.000, prima_lettera -0.948, distanza2 0.132, scelte 0.044, scelte_sopra 0.048, meta 1.103; scarto massimo 0.118: **non converge**.
  - valori (Voynich): unioni attestate 0.0874 (0.0916); coppie viste altrove 0.2473 (0.2213); coppie identiche 0.0105 (0.0097); somiglianza fra vicine 0.2188 (0.2181); confine 0.1790 (0.1881); verticale 1.0221 (1.0278); concordanza 0.0471 (0.0416); S1 0.4837 (0.5312); somiglianza a distanza 2 0.2232 (0.2198); A 1.0079 (1.0465); varianza per riga 1.1667 (1.1027); r righe consecutive 0.2232 (0.2070); JSD fra le meta 0.0523 (0.0503).

| strato | che cosa | AUC e231 | AUC e266 (per seme) | solo sacco | pagella | estese | semi con il cancello | trigrammi dal Voynich | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | peso della coppia esatta anche negativo | 0.563 | 0.625 (0.611, 0.597, 0.660, 0.634) | 0.557 | 15.0/18 | 4.2/8 | 1/4 | 0.007 | 0.50 | 0.51 | 0.64 | 0.60 | 0.48 | 0.58 | 0.57 | 0.65 | 0.64 |
| M2 | M1 e differenza fra le due meta' della pagina | 0.566 | 0.604 (0.606, 0.595, 0.608, 0.607) | 0.557 | 15.0/18 | 3.5/8 | 3/4 | 0.005 | 0.50 | 0.51 | 0.64 | 0.60 | 0.55 | 0.56 | 0.56 | 0.65 | 0.54 |

| per seme | M1 | M2 |
|---|---|---|
| coppie viste altrove (Voynich 0,221 ± 0,02) | 0.245, 0.244, 0.246, 0.246 | 0.239, 0.245, 0.244, 0.248 |
| JSD fra le due metà (Voynich 0,0503) | 0.0413, 0.0387, 0.0399, 0.0421 | 0.0516, 0.0520, 0.0538, 0.0553 |
| S1 | 0.535, 0.403, 0.486, 0.485 | 0.538, 0.536, 0.494, 0.493 |
| R_riga | -0.007, 0.017, 0.002, 0.010 | 0.012, -0.013, -0.008, 0.040 |
| A | 0.979, 1.004, 0.995, 0.999 | 1.008, 1.015, 0.997, 1.015 |
| scelte_per_riga | 5.000, 5.000, 5.000, 5.000 | 5.000, 5.000, 5.000, 5.000 |
| r_righe_consecutive | 0.220, 0.220, 0.219, 0.210 | 0.231, 0.230, 0.243, 0.224 |

## Materie mancate (su 4 semi)

**M1.** omogeneità (4), gradiente (4), profilo pagina (4), scelte di riga (4), coppie viste altrove (4), parole rare per pagina (3), dispersione delle lunghezze (3), prime righe come registro (1).

**M2.** omogeneità (4), gradiente (4), profilo pagina (4), parole rare per pagina (4), prime righe come registro (4), scelte di riga (4), dispersione delle lunghezze (3), coppie viste altrove (3).

## Caratteristiche più pesanti (giudice e266, seme 1)

**M1**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +2.68 | 0.2213 | 0.2451 |
| G9 JSD pagina-manoscritto | +1.63 | 0.0402 | 0.0445 |
| G6 somiglianza a distanza 2 | -1.49 | 0.2198 | 0.2151 |
| G4 inizio ch | +1.36 | 0.0355 | 0.0479 |
| G3 lunghezza media | +1.31 | 4.2913 | 4.3633 |
| G2 ch+o | -1.13 | 0.0347 | 0.0318 |
| G4 unioni attestate | -1.12 | 0.0916 | 0.0900 |
| G3 tipi su parole | +1.03 | 0.7559 | 0.7451 |
| G2 d+y | -0.94 | 0.0432 | 0.0435 |
| G1 f | +0.93 | 0.0026 | 0.0024 |

**M2**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.69 | 0.2213 | 0.2392 |
| G3 uniche nella pagina | -1.49 | 0.6359 | 0.6161 |
| G2 d+y | -1.40 | 0.0432 | 0.0435 |
| G2 o+p | -1.12 | 0.0036 | 0.0037 |
| G4 inizio ch | +1.07 | 0.0355 | 0.0436 |
| G2 e+p | -1.05 | 0.0008 | 0.0005 |
| G4 unioni attestate | -1.03 | 0.0916 | 0.0874 |
| G9 JSD pagina-manoscritto | +1.03 | 0.0402 | 0.0445 |
| G2 o+t | -1.02 | 0.0264 | 0.0242 |
| G1 p | +1.01 | 0.0075 | 0.0078 |

