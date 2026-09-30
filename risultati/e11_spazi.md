# Esperimento 11: gli spazi

- **spazio spiegato**: quanta dell'incertezza su "qui viene uno spazio?" sparisce sapendo il segno precedente (o i due segni precedenti).
- **confine**: quanto l'ultimo segno di una parola dice sul primo della successiva, oltre il caso; solo parole interne alla riga (bit).
- **interno**: lo stesso fra due segni consecutivi dentro una parola (bit).
- **rapporto**: confine diviso interno.

| testo | spazio spiegato (1 segno) | (2 segni) | confine | interno | rapporto |
|---|---|---|---|---|---|
| Voynich (Zandbergen-Landini, glifi) | 66% | 74% | 0.188 | 1.504 | 12.5% |
| Voynich (Takahashi, glifi) | 67% | 76% | 0.169 | 1.493 | 11.3% |
| Voynich (Glen Claston, v101) | 64% | 71% | 0.231 | 1.401 | 16.5% |
| Naibbe (cifrato ufficiale, Plinio XVI) | 64% | 76% | 0.002 | 1.598 | 0.1% |
| 93 testi naturali, intervallo | 6% – 100% (mediana 17%) | 24% – 100% (mediana 43%) | 0.017 – 0.396 (mediana 0.071) | 0.419 – 2.390 (mediana 1.000) | 2% – 28% (mediana 7%) |

## Nel Voynich: fine parola → inizio della parola seguente

Coppie più frequenti del caso (parole interne, rimescolate dentro la riga 20 volte):

| fine | inizio | osservate | attese | × |
|---|---|---|---|---|
| o | r | 76 | 19.3 | 3.94 |
| s | a | 216 | 62.3 | 3.47 |
| o | l | 147 | 45.1 | 3.26 |
| r | a | 586 | 252.8 | 2.32 |
| o | k | 86 | 42.9 | 2.00 |
| o | t | 35 | 17.6 | 1.98 |
| d | y | 33 | 17.6 | 1.88 |
| l | k | 276 | 147.6 | 1.87 |
| y | q | 2820 | 1863.8 | 1.51 |
| o | s | 32 | 22.1 | 1.45 |
| n | cth | 76 | 52.4 | 1.45 |
| d | a | 34 | 23.6 | 1.44 |
| y | p | 82 | 57.8 | 1.42 |
| y | t | 275 | 197.3 | 1.39 |
| l | d | 414 | 297.6 | 1.39 |

Coppie più rare del caso:

| fine | inizio | osservate | attese | × |
|---|---|---|---|---|
| y | a | 73 | 441.2 | 0.17 |
| n | l | 30 | 149.2 | 0.20 |
| r | k | 33 | 115.0 | 0.29 |
| r | l | 36 | 116.8 | 0.31 |
| r | q | 200 | 478.2 | 0.42 |
| o | o | 53 | 121.3 | 0.44 |
| o | ch | 64 | 141.9 | 0.45 |
| r | d | 126 | 230.0 | 0.55 |
| n | q | 310 | 555.8 | 0.56 |
| y | sh | 562 | 988.8 | 0.57 |
| n | s | 43 | 75.5 | 0.57 |
| n | a | 124 | 213.8 | 0.58 |
| l | q | 341 | 581.5 | 0.59 |
| l | a | 114 | 184.7 | 0.62 |
| o | q | 61 | 94.1 | 0.65 |
