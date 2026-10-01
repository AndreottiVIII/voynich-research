# e72 — Al bordo della riga: scelta, aggiunta o sostituzione?

Guadagno in bit per parola di bordo sul modello base S+N (scelta + forma nuova), su dati esclusi (5 parti); pesi della miscela S+N+A+T su tutti i dati. Preregistrazione: `preregistrazioni/e72.md`.

| testo | bordo | parole | +A | +T | +A+T | S | A | T | N | segni aggiunti | segni sostituiti |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | inizio | 3291 | +0.791 | +0.394 | +0.817 | 0.55 | 0.23 | 0.04 | 0.18 | y 0.08, d 0.06, s 0.03, o 0.03 | t 0.01, s 0.01 |
| Voynich | fine | 4006 | +0.196 | +0.148 | +0.321 | 0.39 | 0.08 | 0.07 | 0.46 | y 0.05 | m 0.05, g 0.01 |
| Voynich A | inizio | 1273 | +0.727 | +0.443 | +0.798 | 0.44 | 0.21 | 0.09 | 0.26 | y 0.09, d 0.04, o 0.04, t 0.01 | s 0.03, t 0.03, o 0.01, y 0.01 |
| Voynich A | fine | 1502 | +0.134 | +0.097 | +0.197 | 0.33 | 0.06 | 0.05 | 0.56 | y 0.03, d 0.01 | m 0.03, g 0.01 |
| Voynich B | inizio | 1960 | +0.955 | +0.478 | +0.987 | 0.55 | 0.25 | 0.03 | 0.18 | d 0.07, y 0.07, s 0.04, t 0.03 |  |
| Voynich B | fine | 2423 | +0.235 | +0.214 | +0.435 | 0.35 | 0.10 | 0.09 | 0.47 | y 0.07 | m 0.07 |
| Plinio, a capo | inizio | 4364 | -0.001 | +0.005 | +0.004 | 0.70 | 0.00 | 0.00 | 0.29 |  |  |
| Plinio, a capo | fine | 4365 | +0.169 | +0.215 | +0.321 | 0.76 | 0.02 | 0.02 | 0.19 |  |  |
| Plinio codificato, a capo | inizio | 4344 | +0.036 | +0.042 | +0.052 | 0.54 | 0.03 | 0.04 | 0.39 |  |  |
| Plinio codificato, a capo | fine | 4345 | +0.009 | +0.014 | +0.020 | 0.58 | 0.01 | 0.02 | 0.39 |  |  |
| Naibbe, a capo | inizio | 4270 | +0.034 | +0.037 | +0.051 | 0.84 | 0.02 | 0.02 | 0.12 |  |  |
| Naibbe, a capo | fine | 4271 | +0.010 | +0.047 | +0.052 | 0.87 | 0.01 | 0.03 | 0.10 |  |  |
| controllo: aggiunta "s" all'inizio | inizio | 4344 | +2.531 | +0.956 | +2.600 | 0.22 | 0.35 | 0.04 | 0.38 | s 0.34 | s 0.03 |
| controllo: aggiunta "s" all'inizio | fine | 4345 | +0.009 | +0.014 | +0.020 | 0.58 | 0.01 | 0.02 | 0.39 |  |  |
| controllo: sostituzione con "m" alla fine | inizio | 4344 | +0.036 | +0.042 | +0.052 | 0.54 | 0.03 | 0.04 | 0.39 |  |  |
| controllo: sostituzione con "m" alla fine | fine | 4345 | +0.609 | +2.376 | +2.426 | 0.29 | 0.01 | 0.39 | 0.31 | m 0.01 | m 0.38 |
| Timm e Schinner, seme 19 | inizio | 3602 | +0.147 | +0.068 | +0.161 | 0.74 | 0.09 | 0.02 | 0.15 | k 0.02, o 0.02, p 0.02 |  |
| Timm e Schinner, seme 19 | fine | 3960 | +0.002 | +0.360 | +0.362 | 0.58 | 0.00 | 0.22 | 0.20 |  | m 0.20, g 0.01 |
| Timm e Schinner, seme 1 | inizio | 3647 | +0.195 | +0.081 | +0.195 | 0.77 | 0.10 | 0.00 | 0.13 | k 0.03, p 0.03, t 0.02, y 0.01 |  |
| Timm e Schinner, seme 1 | fine | 3973 | +0.008 | +0.326 | +0.330 | 0.59 | 0.00 | 0.20 | 0.21 |  | m 0.18, g 0.02 |
| Timm e Schinner, seme 2 | inizio | 3624 | +0.157 | +0.063 | +0.161 | 0.78 | 0.08 | 0.01 | 0.12 | k 0.03, p 0.02, t 0.01 |  |
| Timm e Schinner, seme 2 | fine | 3965 | -0.001 | +0.340 | +0.338 | 0.57 | 0.00 | 0.21 | 0.22 |  | m 0.20, g 0.01 |
| modello e51, seme 19 | inizio | 3558 | +0.145 | +0.078 | +0.160 | 0.58 | 0.09 | 0.05 | 0.28 | p 0.02, k 0.01, o 0.01, t 0.01 | p 0.01 |
| modello e51, seme 19 | fine | 3940 | +0.001 | +0.280 | +0.279 | 0.48 | 0.00 | 0.20 | 0.32 |  | m 0.17, g 0.01 |
