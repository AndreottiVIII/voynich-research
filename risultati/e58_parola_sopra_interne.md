# e58 — La parola "di sopra": prova del meccanismo di copia verticale (esplorativo: senza la prima e l'ultima parola di ogni riga)

Rapporto fra la somiglianza di una parola con quella nella stessa posizione della riga precedente e la somiglianza media con le altre parole di quella riga (rapporto dei totali). Nulla: 1000 rimescolamenti dell'ordine della riga precedente. Posizione assoluta (i) e relativa (i / lunghezza). Preregistrazione: `preregistrazioni/e58.md`.

| testo | righe | assoluta | z | p | identiche sopra | relativa | z | p |
|---|---|---|---|---|---|---|---|---|
| Voynich | 3589 | 1.028 | 4.3 | 0.001 | 0.012 | 1.023 | 3.6 | 0.001 |
| Voynich, Currier A | 1257 | 1.014 | 1.0 | 0.157 | 0.012 | 1.017 | 1.3 | 0.107 |
| Voynich, Currier B | 2291 | 1.033 | 4.1 | 0.001 | 0.012 | 1.025 | 3.5 | 0.001 |
| Timm e Schinner, seme 19 (controllo positivo) | 3426 | 1.050 | 6.9 | 0.001 | 0.018 | 1.052 | 7.3 | 0.001 |
| Timm e Schinner, seme 1 (controllo positivo) | 3466 | 1.030 | 4.2 | 0.001 | 0.026 | 1.033 | 4.7 | 0.001 |
| Timm e Schinner, seme 2 (controllo positivo) | 3422 | 1.033 | 4.7 | 0.001 | 0.028 | 1.032 | 4.8 | 0.001 |
| modello e51 (seme 19) | 3364 | 1.021 | 3.0 | 0.001 | 0.015 | 1.021 | 3.0 | 0.002 |
| Bibbia latina (controllo negativo) | 4156 | 1.008 | 1.1 | 0.140 | 0.017 | 1.008 | 1.1 | 0.140 |
| Plinio (controllo negativo) | 4180 | 1.004 | 0.6 | 0.268 | 0.006 | 1.004 | 0.6 | 0.268 |
| codice parola per parola (controllo negativo) | 4180 | 1.006 | 0.9 | 0.191 | 0.006 | 1.006 | 0.9 | 0.191 |
| Naibbe (controllo negativo) | 4127 | 0.998 | -0.3 | 0.628 | 0.004 | 0.998 | -0.3 | 0.628 |
| gibberish (righe vere, Gaskell e Bowern) | 1216 | 1.023 | 1.2 | 0.111 | 0.013 | 1.016 | 0.9 | 0.182 |
