# e232 — Meno pagina, più manoscritto, contro il discriminatore

Generatore dell'e230 con la partenza dell'e224, η 1 e σ 0,09; δ = probabilità di prendere la parola di base dalle frequenze del Voynich intero (stessa lingua). AUC del discriminatore dell'e231. Validità (δ 0 = e230): sì. Preregistrazione: `preregistrazioni/e232.md`.

| | AUC | tipi su parole (pagina) | fra le 100 più frequenti | righe in -m |
|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.139 |
| delta 0.0, seme 1 | 0.912 | 0.703 | 0.374 | 0.119 |
| delta 0.2, seme 1 | 0.914 | 0.716 | 0.375 | 0.128 |
| delta 0.4, seme 1 | 0.929 | 0.738 | 0.370 | 0.120 |
| delta 0.0, semi 2–3 | 0.918 | 0.699 | 0.377 | 0.123 |

Caratteristiche più pesanti che restano (δ 0.0, seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 fra le 100 piu frequenti | -2.08 | 0.4244 | 0.3794 |
| G3 uniche nel testo | -1.73 | 0.1461 | 0.1175 |
| G3 lunghezza media | -1.29 | 4.2913 | 4.0780 |
| G4 somiglianza fra vicine | -1.26 | 0.2181 | 0.1877 |
| G4 fine m | -1.16 | 0.1392 | 0.1211 |
| G3 uniche nella pagina | -1.03 | 0.6359 | 0.5622 |
| G3 lunghezza deviazione | +1.01 | 1.5790 | 1.6354 |
| G3 tipi su parole | -1.00 | 0.7559 | 0.6998 |
| G2 t+ch | -0.93 | 0.0119 | 0.0085 |
| G2 a+k | +0.78 | 0.0003 | 0.0008 |

Esito: **delta non aiuta abbastanza**.
