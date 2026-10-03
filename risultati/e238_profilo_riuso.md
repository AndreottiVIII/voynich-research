# e238 — Un generatore che segue il profilo di riuso della pagina

Candidate estratte con le quote dell'e237 (R 0.319, V 0.375, F 0.072, A 0.091, N 0.143), fonti dalle ultime 3 righe; σ 0,09 e prefissi π 0,30 dopo la generazione. AUC del discriminatore dell'e231 sui semi 2–3; riferimento (e235) 0.889. Preregistrazione: `preregistrazioni/e238.md`.

| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 | 31.9% | 37.5% | 7.2% | 9.1% | 14.3% |
| seme 2 | 0.985 | 0.724 | 0.333 | 0.146 | 0.193 | 4.151 | 31.5% | 45.0% | 5.3% | 7.1% | 11.0% |
| seme 3 | 0.988 | 0.723 | 0.322 | 0.146 | 0.196 | 4.180 | 31.5% | 45.2% | 5.3% | 7.1% | 10.9% |

AUC media: 0.987. Pagella dell'e224 (seme 2): 9/18, riga riprodotta: sì; mancano: h2, spazio, tipi, gradiente, deriva, profilo pagina, Zipf, forma parole, verticale.

Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 fra le 100 piu frequenti | -1.40 | 0.4244 | 0.3326 |
| G2 d+a | -0.70 | 0.0373 | 0.0261 |
| G3 uniche nella pagina | -0.63 | 0.6359 | 0.5565 |
| G3 lunghezza media | -0.63 | 4.2913 | 4.0721 |
| G2 o+i | +0.62 | 0.0034 | 0.0090 |
| G3 lunghezza deviazione | +0.60 | 1.5790 | 1.6960 |
| G2 o+o | +0.58 | 0.0007 | 0.0042 |
| G2 e+ch | +0.58 | 0.0008 | 0.0025 |
| G3 uniche nel testo | -0.54 | 0.1461 | 0.1459 |
| G1 c | -0.52 | 0.0012 | 0.0004 |

Esito: **non migliore**.
