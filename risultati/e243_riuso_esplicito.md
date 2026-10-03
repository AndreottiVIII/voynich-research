# e243 — Passo 1 del piano 18/18: modulo di riuso esplicito

Quote di classe tarate sull'uscita (seme 1): R 0.337, V 0.230, F 0.128, A 0.147, N 0.158. Verifica sui semi 7–9. Preregistrazione: `preregistrazioni/e243.md`.

| | AUC | pagella | riga | R parole rare | R | V | N | tipi su parole (pagina) | fra le 100 | uniche | vicine | lunghezza |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | | 18/18 | sì | 1,96 | 31.9% | 37.5% | 14.3% | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 |
| seme 7 | 0.975 | 8/18 | sì | 87.5 | 32.3% | 41.4% | 12.3% | 0.721 | 0.326 | 0.150 | 0.230 | 4.934 |
| seme 8 | 0.980 | 8/18 | sì | 80.5 | 31.6% | 41.9% | 12.3% | 0.727 | 0.324 | 0.153 | 0.224 | 4.880 |
| seme 9 | 0.973 | 10/18 | sì | 90.6 | 31.4% | 41.7% | 12.8% | 0.730 | 0.316 | 0.156 | 0.229 | 4.921 |

Media: AUC 0.976, pagella 8.7/18. Proprietà mancanti (quante volte su 3 semi): {'h2': 3, 'spazio': 3, 'uniche': 1, 'tipi': 3, 'ripetizione': 3, 'gradiente': 3, 'unioni': 2, 'deriva': 3, 'Zipf': 3, 'formule': 2, 'profilo pagina': 2}.

Caratteristiche più pesanti del discriminatore (seme 7; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 lunghezza deviazione | +1.58 | 1.5790 | 2.0486 |
| G3 fra le 100 piu frequenti | -1.01 | 0.4244 | 0.3257 |
| G2 y+ch | +0.84 | 0.0024 | 0.0052 |
| G3 uniche nella pagina | -0.81 | 0.6359 | 0.5576 |
| G4 unioni attestate | +0.80 | 0.0916 | 0.0961 |
| G3 lunghezza media | +0.75 | 4.2913 | 4.8043 |
| G1 p | +0.74 | 0.0075 | 0.0138 |
| G3 uniche nel testo | -0.74 | 0.1461 | 0.1546 |
| G2 e+y | -0.67 | 0.0271 | 0.0203 |
| G2 d+ch | +0.64 | 0.0039 | 0.0070 |

Esito: **non superato**.
