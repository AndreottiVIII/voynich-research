# e241 — Operatore di variante empirico condizionato ai segni vicini

Come l'e240, con le 2432 operazioni contate insieme al segno prima e dopo; ripiego sull'operatore dell'e240. AUC del discriminatore dell'e231 sui semi 2–3; riferimento (e235) 0.889; e240: 0,908 e pagella 16/18. Preregistrazione: `preregistrazioni/e241.md`.

| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 | 31.9% | 37.5% | 7.2% | 9.1% | 14.3% |
| seme 2 | 0.862 | 0.681 | 0.412 | 0.120 | 0.206 | 4.212 | 38.4% | 35.4% | 5.9% | 8.2% | 12.2% |
| seme 3 | 0.886 | 0.677 | 0.415 | 0.116 | 0.207 | 4.213 | 38.6% | 35.2% | 5.7% | 8.3% | 12.2% |

AUC media: 0.874. Pagella dell'e224 (seme 2): 16/18, riga riprodotta: sì; mancano: ripetizione, verticale.

Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 uniche nella pagina | -1.93 | 0.6359 | 0.5417 |
| G3 lunghezza media | -1.79 | 4.2913 | 4.0653 |
| G3 tipi su parole | -1.70 | 0.7559 | 0.6794 |
| G3 fra le 100 piu frequenti | -1.57 | 0.4244 | 0.4137 |
| G3 lunghezza deviazione | +1.34 | 1.5790 | 1.6626 |
| G2 d+ch | +0.96 | 0.0039 | 0.0056 |
| G1 f | +0.94 | 0.0026 | 0.0027 |
| G2 r+ch | +0.87 | 0.0009 | 0.0010 |
| G2 d+a | -0.87 | 0.0373 | 0.0353 |
| G2 d+y | -0.86 | 0.0432 | 0.0429 |

Esito: **non migliore**.
