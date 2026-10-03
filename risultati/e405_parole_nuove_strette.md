# e405 — Le parole nuove, terzo passo

Semi 1–4 (medie). Riferimenti: prova isolata T-LPS 0,644 (e403b); sacco intero C4 0,645, con le parole nuove vere C2 0,482 (e404b). Parole uniche del Voynich: lunghezza 5,944 ± 1,570; a una modifica da una nota 0,715. Preregistrazione: `preregistrazioni/e405.md`.

Forza della scelta per profilo (N3), regolata sul pannello: 0.370 (JSD pagina-manoscritto 0.0382, Voynich 0.0402); punti provati: 0.00 → 0.0357, 1.00 → 0.0478, 0.37 → 0.0382, 0.68 → 0.0444, 0.47 → 0.0433.

| generatore | misura | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|---|
| N1 | isolata | 0.622 (0.608–0.643) | 0.60–0.66 | 0.58 | 0.57 | 0.56 | 0.51 |
| N1 | intero | 0.582 (0.576–0.592) | 0.58–0.65 | 0.52 | 0.51 | 0.64 | 0.59 |
| N2 | isolata | 0.615 (0.604–0.628) | 0.56–0.64 | 0.54 | 0.56 | 0.56 | 0.51 |
| N2 | intero | 0.563 (0.554–0.570) | 0.55–0.63 | 0.50 | 0.49 | 0.64 | 0.59 |
| N3 | intero | 0.495 (0.476–0.520) | 0.53–0.62 | 0.50 | 0.48 | 0.64 | 0.47 |

## Forma delle inventate (prova isolata)

| generatore | lunghezza | deviazione | a una modifica da una nota | unione di due note | campioni attestati scartati |
|---|---|---|---|---|---|
| N1 | 5.932 | 1.551 | 0.548 | 0.486 | 0.479 |
| N2 | 5.950 | 1.534 | 0.548 | 0.484 | 0.467 |

## Valori di pagina del sacco intero (media delle pagine)

| generatore | G3 tipi su parole | G3 uniche nella pagina | G3 uniche nel testo | G3 fra le 100 piu frequenti | G3 lunghezza media | G3 lunghezza deviazione | G9 JSD pagina-manoscritto | G1 f | G1 p | G1 m |
|---|---|---|---|---|---|---|---|---|---|---|
| N1 | 0.7457 | 0.6163 | 0.1561 | 0.4366 | 4.3367 | 1.6071 | 0.0487 | 0.0028 | 0.0081 | 0.0066 |
| N2 | 0.7457 | 0.6172 | 0.1559 | 0.4366 | 4.3439 | 1.6140 | 0.0489 | 0.0028 | 0.0081 | 0.0066 |
| N3 | 0.7461 | 0.6172 | 0.1565 | 0.4387 | 4.3358 | 1.6179 | 0.0399 | 0.0027 | 0.0079 | 0.0066 |

## Caratteristiche più pesanti del sacco intero (seme 1)

**N1**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 uniche nella pagina | -1.56 | 0.6359 | 0.6139 |
| G9 JSD pagina-manoscritto | +1.38 | 0.0402 | 0.0497 |
| G3 tipi su parole | +1.17 | 0.7559 | 0.7447 |
| G1 f | +1.11 | 0.0026 | 0.0028 |
| G1 s | -0.99 | 0.0179 | 0.0179 |
| G2 a+r | -0.94 | 0.0210 | 0.0215 |
| G2 ch+e | -0.94 | 0.0319 | 0.0298 |
| G3 fra le 100 piu frequenti | +0.91 | 0.4244 | 0.4365 |
| G2 y+ch | +0.72 | 0.0024 | 0.0026 |
| G2 e+s | +0.68 | 0.0031 | 0.0032 |

**N2**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 fra le 100 piu frequenti | +1.73 | 0.4244 | 0.4330 |
| G3 tipi su parole | +1.58 | 0.7559 | 0.7504 |
| G9 JSD pagina-manoscritto | +1.24 | 0.0402 | 0.0477 |
| G3 uniche nella pagina | -1.06 | 0.6359 | 0.6231 |
| G1 k | +1.06 | 0.0544 | 0.0542 |
| G1 h | +1.03 | 0.0015 | 0.0018 |
| G2 o+k | -0.91 | 0.0401 | 0.0390 |
| G2 k+h | -0.91 | 0.0005 | 0.0004 |
| G1 y | -0.88 | 0.1046 | 0.0999 |
| G2 d+y | -0.87 | 0.0432 | 0.0418 |

**N3**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 tipi su parole | +1.70 | 0.7559 | 0.7421 |
| G3 uniche nella pagina | -1.57 | 0.6359 | 0.6132 |
| G3 fra le 100 piu frequenti | +1.17 | 0.4244 | 0.4435 |
| G2 i+n | -0.98 | 0.0483 | 0.0544 |
| G1 d | +0.86 | 0.0766 | 0.0772 |
| G2 d+y | -0.80 | 0.0432 | 0.0410 |
| G1 r | -0.69 | 0.0440 | 0.0449 |
| G2 r+a | +0.66 | 0.0033 | 0.0046 |
| G1 y | -0.62 | 0.1046 | 0.0963 |
| G2 o+l | -0.62 | 0.0473 | 0.0475 |

