# e410 — Il cancello della riga

Semi 1–4 (medie). Riferimento: R1 dell'e408 (corpo della v10) 0,554 / 0,673, pagella 17,0/18, cancello perso in 4 semi. Preregistrazione: `preregistrazioni/e410.md`.

## Regolazione sul pannello (seme 11)

- **G1:** pesi bordi 1.253, unione 0.900, coppia 0.000, identica -0.501, confine 0.636, verticale 0.091, fin_fin 0.000, prima_lettera -0.886, distanza2 0.264; scarto massimo 0.141: **non converge**.
  - valori (Voynich): unioni attestate 0.0907 (0.0916); coppie viste altrove 0.2525 (0.2213); coppie identiche 0.0103 (0.0097); somiglianza fra vicine 0.2152 (0.2181); confine 0.1935 (0.1881); verticale 1.0306 (1.0278); concordanza 0.0563 (0.0416); S1 0.4659 (0.5312); somiglianza a distanza 2 0.2250 (0.2198); A 1.0189 (1.0465).
- **G2:** pesi bordi 1.131, unione 0.909, coppia 0.000, identica -0.561, confine 0.685, verticale 0.127, fin_fin 0.007, prima_lettera -0.804, distanza2 0.153, scelte 0.049, scelte_sopra 0.047; scarto massimo 0.131: **non converge**.
  - valori (Voynich): unioni attestate 0.0903 (0.0916); coppie viste altrove 0.2482 (0.2213); coppie identiche 0.0089 (0.0097); somiglianza fra vicine 0.2143 (0.2181); confine 0.1915 (0.1881); verticale 1.0242 (1.0278); concordanza 0.0574 (0.0416); S1 0.5762 (0.5312); somiglianza a distanza 2 0.2231 (0.2198); A 1.0107 (1.0465); varianza per riga 1.1293 (1.1027); r righe consecutive 0.1695 (0.2070).

| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | semi con il cancello | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | prima lettera della riga e somiglianza a distanza 2 | 0.555 | 0.639 (0.619–0.657) | 0.539 | 16.0/18 | 3.8/8 | 0/4 | 0.52 | 0.51 | 0.63 | 0.60 | 0.48 | 0.59 | 0.58 | 0.67 | 0.65 |
| G2 | G1 e cinque scelte di grafia nella riga e fra righe | 0.552 | 0.616 (0.600–0.629) | 0.539 | 15.8/18 | 4.5/8 | 3/4 | 0.52 | 0.51 | 0.63 | 0.61 | 0.51 | 0.57 | 0.59 | 0.64 | 0.64 |

Cancello della riga per seme (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| | G1 | G2 |
|---|---|---|
| S1 | 0.524, 0.546, 0.487, 0.502 | 0.531, 0.610, 0.590, 0.550 |
| R_riga | -0.022, 0.008, -0.008, 0.042 | -0.011, 0.037, 0.010, 0.013 |
| A | 1.022, 1.036, 1.024, 1.007 | 1.004, 0.997, 1.022, 1.003 |
| scelte_per_riga | 2.000, 3.000, 0.000, 2.000 | 5.000, 5.000, 5.000, 5.000 |
| r_righe_consecutive | 0.085, 0.089, 0.092, 0.080 | 0.195, 0.167, 0.180, 0.174 |

## Materie mancate (su 4 semi)

**G1.** gradiente (4), profilo pagina (4), scelte di riga (4), coppie viste altrove (4), parole rare per pagina (3), concordanza delle desinenze (3), prime righe come registro (2), dispersione delle lunghezze (1).

**G2.** gradiente (4), profilo pagina (4), scelte di riga (4), coppie viste altrove (3), parole rare per pagina (3), concordanza delle desinenze (2), omogeneità (1), dispersione delle lunghezze (1), prime righe come registro (1).

| materia aggiunta | Voynich | G1 | G2 |
|---|---|---|---|
| parole rare per pagina | 1.958 | 7.153 | 6.855 |
| tipi su parole nella pagina | 0.7559 | 0.7459 | 0.7459 |
| uniche nella pagina | 0.6359 | 0.6196 | 0.6196 |
| dispersione delle lunghezze | 1.579 | 1.621 | 1.621 |
| prime righe come registro | 4.724 | 2.525 | 3.248 |
| scelte di riga | 12 | 4.25 | 6.75 |
| concordanza delle desinenze | 0.04335 | 0.059 | 0.05645 |
| coppie viste altrove | 0.2213 | 0.2506 | 0.2462 |

## Caratteristiche più pesanti (seme 1)

**G1**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD prima-seconda meta | -1.80 | 0.0503 | 0.0374 |
| e266 | G6 coppie viste altrove | +1.52 | 0.2213 | 0.2564 |
| e266 | G3 tipi su parole | +1.52 | 0.7559 | 0.7421 |
| e266 | G9 JSD pagina-manoscritto | +1.39 | 0.0402 | 0.0427 |
| e266 | G2 y+o | +1.07 | 0.0004 | 0.0009 |
| e266 | G2 o+r | -1.01 | 0.0284 | 0.0264 |
| e266 | G1 s | -0.99 | 0.0179 | 0.0192 |
| e266 | G2 cth+e | +0.96 | 0.0021 | 0.0020 |
| e266 | G2 r+sh | +0.94 | 0.0003 | 0.0007 |
| e266 | G2 ckh+e | +0.93 | 0.0020 | 0.0021 |
| e231 | G2 y+o | +1.33 | 0.0004 | 0.0009 |
| e231 | G3 uniche nella pagina | -1.21 | 0.6359 | 0.6167 |
| e231 | G2 r+sh | +1.16 | 0.0003 | 0.0007 |
| e231 | G4 inizio s | +1.10 | 0.0804 | 0.1226 |
| e231 | G3 tipi su parole | +1.08 | 0.7559 | 0.7421 |
| e231 | G2 e+sh | +1.04 | 0.0003 | 0.0006 |

**G2**

| giudice | caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|---|
| e266 | G9 JSD prima-seconda meta | -1.98 | 0.0503 | 0.0380 |
| e266 | G6 coppie viste altrove | +1.68 | 0.2213 | 0.2534 |
| e266 | G2 y+ch | +1.28 | 0.0024 | 0.0028 |
| e266 | G2 cth+e | +1.20 | 0.0021 | 0.0020 |
| e266 | G3 tipi su parole | +1.16 | 0.7559 | 0.7421 |
| e266 | G2 l+e | +1.03 | 0.0003 | 0.0007 |
| e266 | G2 y+o | +1.01 | 0.0004 | 0.0009 |
| e266 | G2 r+sh | +0.98 | 0.0003 | 0.0007 |
| e266 | G4 inizio ch | +0.97 | 0.0355 | 0.0411 |
| e266 | G9 JSD pagina-manoscritto | +0.95 | 0.0402 | 0.0427 |
| e231 | G3 fra le 100 piu frequenti | +1.17 | 0.4244 | 0.4436 |
| e231 | G2 y+o | +1.17 | 0.0004 | 0.0009 |
| e231 | G3 uniche nella pagina | -1.10 | 0.6359 | 0.6167 |
| e231 | G2 r+sh | +1.10 | 0.0003 | 0.0007 |
| e231 | G2 y+ch | +1.09 | 0.0024 | 0.0028 |
| e231 | G2 a+l | -1.05 | 0.0178 | 0.0191 |

