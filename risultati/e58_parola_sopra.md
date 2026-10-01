# e58 — La parola "di sopra": prova del meccanismo di copia verticale

Rapporto fra la somiglianza di una parola con quella nella stessa posizione della riga precedente e la somiglianza media con le altre parole di quella riga (rapporto dei totali). Nulla: 1000 rimescolamenti dell'ordine della riga precedente. Posizione assoluta (i) e relativa (i / lunghezza). Preregistrazione: `preregistrazioni/e58.md`.

| testo | righe | assoluta | z | p | identiche sopra | relativa | z | p |
|---|---|---|---|---|---|---|---|---|
| Voynich | 3886 | 1.059 | 9.9 | 0.001 | 0.010 | 1.061 | 11.0 | 0.001 |
| Voynich, Currier A | 1431 | 1.052 | 4.8 | 0.001 | 0.010 | 1.069 | 6.7 | 0.001 |
| Voynich, Currier B | 2377 | 1.062 | 9.0 | 0.001 | 0.010 | 1.057 | 8.9 | 0.001 |
| Timm e Schinner, seme 19 (controllo positivo) | 3862 | 1.062 | 10.2 | 0.001 | 0.016 | 1.071 | 12.0 | 0.001 |
| Timm e Schinner, seme 1 (controllo positivo) | 3862 | 1.045 | 7.6 | 0.001 | 0.024 | 1.051 | 9.5 | 0.001 |
| Timm e Schinner, seme 2 (controllo positivo) | 3862 | 1.046 | 7.8 | 0.001 | 0.026 | 1.053 | 9.0 | 0.001 |
| modello e51 (seme 19) | 3862 | 1.036 | 6.0 | 0.001 | 0.013 | 1.052 | 9.4 | 0.001 |
| Bibbia latina (controllo negativo) | 4156 | 1.011 | 1.8 | 0.034 | 0.018 | 1.011 | 1.8 | 0.034 |
| Plinio (controllo negativo) | 4180 | 1.007 | 1.3 | 0.093 | 0.006 | 1.007 | 1.3 | 0.093 |
| codice parola per parola (controllo negativo) | 4180 | 1.005 | 0.8 | 0.188 | 0.006 | 1.005 | 0.8 | 0.188 |
| Naibbe (controllo negativo) | 4127 | 1.000 | -0.0 | 0.505 | 0.004 | 1.000 | -0.0 | 0.505 |
