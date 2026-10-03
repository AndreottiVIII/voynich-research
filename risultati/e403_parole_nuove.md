# e403 — Il sacco, primo pezzo: le parole nuove

Voynich vero con ogni parola unica nel libro (4.776) sostituita da una parola inventata; semi 1–4 (medie). "Solo sacco" = giudice dell'e266 su G1, G2, G3 e JSD pagina-manoscritto; pavimento 0,50. Preregistrazione: `preregistrazioni/e403.md`.

| generatore | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|---|---|
| variante-libro | 0.795 (0.780–0.807) | 0.60–0.72 | 0.74 | 0.71 | 0.50 | 0.65 | 0.813 | 0.874 |
| variante-pagina | 0.781 (0.772–0.787) | 0.56–0.68 | 0.73 | 0.71 | 0.64 | 0.51 | 0.814 | 0.845 |
| trigrammi | 0.961 (0.953–0.976) | 0.58–0.70 | 0.62 | 0.68 | 0.97 | 0.68 | 0.962 | 0.973 |
| mista | 0.774 (0.752–0.803) | 0.55–0.65 | 0.68 | 0.67 | 0.73 | 0.52 | 0.808 | 0.850 |

## Forma delle parole inventate

| | lunghezza media | lunghezza deviazione | a una modifica da una nota | unione di due note |
|---|---|---|---|---|
| Voynich, parole uniche | 5.944 | 1.570 | 0.715 | 0.678 |
| variante-libro | 5.782 | 1.398 | 1.000 | 0.778 |
| variante-pagina | 5.607 | 1.363 | 1.000 | 0.788 |
| trigrammi | 7.699 | 2.896 | 0.356 | 0.356 |
| mista | 6.318 | 2.101 | 0.785 | 0.758 |

## Valori di pagina (media delle pagine)

| generatore | G3 lunghezza media | G3 lunghezza deviazione | G3 uniche nel testo | G3 tipi su parole | G9 JSD pagina-manoscritto |
|---|---|---|---|---|---|
| variante-libro | 4.2943 | 1.5740 | 0.1461 | 0.7559 | 0.0288 |
| variante-pagina | 4.2456 | 1.5141 | 0.1461 | 0.7559 | 0.0416 |
| trigrammi | 4.5700 | 2.1344 | 0.1461 | 0.7559 | 0.0267 |
| mista | 4.3506 | 1.7169 | 0.1461 | 0.7559 | 0.0390 |

## Caratteristiche più pesanti del solo sacco (seme 1)

**variante-libro**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -2.86 | 0.0402 | 0.0288 |
| G2 i+i | +1.59 | 0.0415 | 0.0420 |
| G2 e+k | +1.40 | 0.0035 | 0.0043 |
| G1 x | -1.40 | 0.0001 | 0.0000 |
| G1 f | -1.37 | 0.0026 | 0.0019 |
| G1 h | -1.23 | 0.0015 | 0.0010 |
| G2 h+y | +1.18 | 0.0011 | 0.0011 |
| G2 cph+y | +1.11 | 0.0006 | 0.0008 |
| G2 s+a | -1.11 | 0.0041 | 0.0037 |
| G1 c | -1.02 | 0.0012 | 0.0004 |

**variante-pagina**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G2 i+i | +1.86 | 0.0415 | 0.0427 |
| G1 c | -1.77 | 0.0012 | 0.0005 |
| G3 lunghezza deviazione | -1.74 | 1.5790 | 1.5152 |
| G2 h+y | +1.74 | 0.0011 | 0.0010 |
| G1 h | -1.46 | 0.0015 | 0.0009 |
| G2 o+d | +1.43 | 0.0216 | 0.0217 |
| G1 f | -1.35 | 0.0026 | 0.0017 |
| G1 x | -1.13 | 0.0001 | 0.0000 |
| G2 a+n | +1.09 | 0.0014 | 0.0017 |
| G2 cph+y | +1.08 | 0.0006 | 0.0007 |

**trigrammi**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 lunghezza deviazione | +4.35 | 1.5790 | 2.1340 |
| G3 uniche nel testo | -1.90 | 0.1461 | 0.1461 |
| G9 JSD pagina-manoscritto | -1.26 | 0.0402 | 0.0266 |
| G3 fra le 100 piu frequenti | +1.03 | 0.4244 | 0.4244 |
| G3 lunghezza media | +0.88 | 4.2913 | 4.5673 |
| G2 d+e | +0.51 | 0.0008 | 0.0015 |
| G2 l+p | +0.51 | 0.0002 | 0.0005 |
| G2 y+p | +0.49 | 0.0009 | 0.0009 |
| G2 l+sh | +0.48 | 0.0016 | 0.0029 |
| G2 d+sh | +0.44 | 0.0017 | 0.0017 |

**mista**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 lunghezza deviazione | +2.84 | 1.5790 | 1.7334 |
| G1 f | -1.86 | 0.0026 | 0.0018 |
| G3 uniche nel testo | -1.48 | 0.1461 | 0.1461 |
| G2 f+ch | +1.41 | 0.0016 | 0.0014 |
| G2 i+i | +1.08 | 0.0415 | 0.0414 |
| G1 c | -1.00 | 0.0012 | 0.0006 |
| G2 o+k | +0.89 | 0.0401 | 0.0412 |
| G1 g | -0.85 | 0.0011 | 0.0008 |
| G2 cth+e | +0.75 | 0.0021 | 0.0025 |
| G2 e+ckh | +0.75 | 0.0007 | 0.0011 |

