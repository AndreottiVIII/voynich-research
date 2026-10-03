# e403b — Le parole nuove, secondo tentativo: forma imparata sulle parole uniche

Voynich vero con ogni parola unica nel libro sostituita da una inventata; semi 1–4 (medie). Solo sacco: pavimento 0,50; nell'e403 il migliore era 0,774. Parole uniche del Voynich: lunghezza 5,944 ± 1,570; a una modifica da una nota 0,715; unione di due note 0,678. Preregistrazione: `preregistrazioni/e403b.md`.

| generatore | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD | AUC e231 | AUC e266 | lunghezza | deviazione | a una modifica | unione |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-L | 0.690 (0.678–0.705) | 0.68–0.80 | 0.58 | 0.58 | 0.57 | 0.64 | 0.753 | 0.843 | 5.932 | 1.560 | 0.547 | 0.484 |
| T-LP | 0.688 (0.678–0.700) | 0.62–0.74 | 0.57 | 0.57 | 0.58 | 0.64 | 0.694 | 0.751 | 5.942 | 1.564 | 0.547 | 0.481 |
| T-LPS | 0.644 (0.624–0.662) | 0.55–0.68 | 0.59 | 0.59 | 0.56 | 0.52 | 0.690 | 0.730 | 5.952 | 1.546 | 0.552 | 0.503 |

## Valori di pagina (media delle pagine)

| generatore | G3 lunghezza media | G3 lunghezza deviazione | G1 p | G1 f | G1 m | G1 s | G9 JSD pagina-manoscritto |
|---|---|---|---|---|---|---|---|
| T-L | 4.3160 | 1.6150 | 0.0086 | 0.0031 | 0.0069 | 0.0187 | 0.0297 |
| T-LP | 4.3189 | 1.6178 | 0.0081 | 0.0029 | 0.0069 | 0.0184 | 0.0297 |
| T-LPS | 4.3134 | 1.6080 | 0.0078 | 0.0026 | 0.0070 | 0.0193 | 0.0409 |

## Caratteristiche più pesanti del solo sacco (seme 1)

**T-L**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -3.03 | 0.0402 | 0.0297 |
| G3 uniche nel testo | -1.68 | 0.1461 | 0.1461 |
| G3 fra le 100 piu frequenti | +1.28 | 0.4244 | 0.4244 |
| G2 a+r | -1.23 | 0.0210 | 0.0220 |
| G1 p | +1.16 | 0.0075 | 0.0089 |
| G2 d+y | -1.11 | 0.0432 | 0.0425 |
| G2 o+t | -1.06 | 0.0264 | 0.0260 |
| G2 sh+e | -0.97 | 0.0162 | 0.0164 |
| G1 t | +0.97 | 0.0353 | 0.0350 |
| G3 uniche nella pagina | +0.90 | 0.6359 | 0.6359 |

**T-LP**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -3.02 | 0.0402 | 0.0296 |
| G3 uniche nel testo | -1.82 | 0.1461 | 0.1461 |
| G3 fra le 100 piu frequenti | +1.35 | 0.4244 | 0.4244 |
| G2 e+d | -1.05 | 0.0231 | 0.0243 |
| G1 p | +1.04 | 0.0075 | 0.0083 |
| G2 d+y | -1.03 | 0.0432 | 0.0426 |
| G2 sh+e | -0.97 | 0.0162 | 0.0163 |
| G2 o+l | -0.88 | 0.0473 | 0.0460 |
| G2 a+r | -0.87 | 0.0210 | 0.0214 |
| G2 a+i | -0.85 | 0.0517 | 0.0507 |

**T-LPS**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 uniche nel testo | -1.89 | 0.1461 | 0.1461 |
| G2 d+y | -1.68 | 0.0432 | 0.0417 |
| G3 fra le 100 piu frequenti | +0.89 | 0.4244 | 0.4244 |
| G1 f | -0.79 | 0.0026 | 0.0025 |
| G2 o+l | -0.79 | 0.0473 | 0.0462 |
| G1 p | +0.78 | 0.0075 | 0.0077 |
| G1 d | +0.77 | 0.0766 | 0.0756 |
| G2 l+o | +0.76 | 0.0035 | 0.0045 |
| G2 a+r | -0.75 | 0.0210 | 0.0218 |
| G2 i+s | +0.70 | 0.0002 | 0.0007 |

