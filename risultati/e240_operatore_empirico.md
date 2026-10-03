# e240 — Il generatore con l'operatore di variante empirico

Generatore "copia e modifica" migliore (e233/e235: κ 1, χ 0,2, η 1) con le modifiche estratte dalle 675 operazioni osservate fra varianti della stessa pagina nel Voynich; spezzature e prefissi staccati dopo la generazione. AUC del discriminatore dell'e231 sui semi 2–3; riferimento (stesso generatore con l'operatore vecchio, e235) 0.889. Preregistrazione: `preregistrazioni/e240.md`.

| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 | 31.9% | 37.5% | 7.2% | 9.1% | 14.3% |
| seme 2 | 0.899 | 0.664 | 0.411 | 0.126 | 0.214 | 4.283 | 39.7% | 34.9% | 6.0% | 7.1% | 12.3% |
| seme 3 | 0.917 | 0.659 | 0.410 | 0.122 | 0.212 | 4.231 | 40.2% | 34.1% | 5.9% | 7.4% | 12.4% |

AUC media: 0.908. Pagella dell'e224 (seme 2): 16/18, riga riprodotta: sì; mancano: ripetizione, verticale.

Operazioni più frequenti nelle varianti generate (seme 2): +e interna 4.5%, k→t interna 2.6%, −e interna 2.4%, +d iniziale 2.1%, +q iniziale 2.0%, l→r finale 1.7%, −q iniziale 1.7%, ch→sh iniziale 1.7%, t→k interna 1.6%, +d interna 1.6%.

Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 lunghezza media | -1.73 | 4.2913 | 4.1121 |
| G3 fra le 100 piu frequenti | -1.64 | 0.4244 | 0.4113 |
| G3 tipi su parole | -1.34 | 0.7559 | 0.6632 |
| G2 e+ch | +1.25 | 0.0008 | 0.0019 |
| G3 uniche nel testo | -1.20 | 0.1461 | 0.1314 |
| G3 uniche nella pagina | -1.12 | 0.6359 | 0.5222 |
| G3 lunghezza deviazione | +1.11 | 1.5790 | 1.6809 |
| G2 q+e | +1.03 | 0.0003 | 0.0007 |
| G2 p+sh | +1.02 | 0.0006 | 0.0014 |
| G2 l+e | +0.96 | 0.0003 | 0.0008 |

Esito: **non migliore**.
