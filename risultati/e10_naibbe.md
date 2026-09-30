# Esperimento 10: il cifrario Naibbe

Greshko, M. A. (2025). *The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext.* Cryptologia. doi:10.1080/01611194.2025.2566408. Codice: github.com/greshko/naibbe-cipher.

Stesse misure dell'esperimento 7, più **confine**: quanto l'ultimo segno di una parola dice sul primo della successiva, oltre il caso (bit). "Deriva di pagina": a ogni pagina le preferenze fra le sei tabelle si ripescano; concentrazione più bassa = pagine più "di parte".

| testo | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza: riga | riga sotto | 6 righe | confine |
|---|---|---|---|---|---|---|---|---|---|
| **Voynich (pagine e righe vere)** | 2.24 | 4.46 | 0.210 | 0.68 | ×1.01 | 3.8% | 4.0% | 3.4% | 0.188 |
| **Voynich (righe finte da 8 parole)** | 2.24 | 4.46 | 0.210 | 0.68 | ×0.94 | 4.1% | 3.6% | 2.6% | 0.165 |
| Naibbe, cifrato ufficiale di Greshko (Plinio XVI) | 2.16 | 4.80 | 0.175 | 0.43 | ×0.44 | -0.4% | -0.1% | -0.2% | 0.002 |
| Vitruvio: testo in chiaro | 3.30 | 6.18 | 0.274 | 0.62 | ×0.23 | 0.4% | 0.4% | 0.2% | 0.028 |
| Vitruvio: Naibbe | 2.17 | 4.82 | 0.174 | 0.43 | ×0.40 | -0.1% | -0.1% | -0.1% | 0.004 |
| Vitruvio: Naibbe con deriva di pagina (concentrazione 3.0) | 2.17 | 4.82 | 0.165 | 0.44 | ×0.42 | 0.5% | 0.6% | 0.7% | 0.002 |
| Vitruvio: Naibbe con deriva di pagina (concentrazione 1.0) | 2.19 | 4.82 | 0.154 | 0.44 | ×0.33 | 1.4% | 1.4% | 1.5% | 0.004 |
| Vitruvio: Naibbe con deriva di pagina (concentrazione 0.3) | 2.17 | 4.82 | 0.117 | 0.41 | ×0.37 | 2.0% | 2.0% | 2.0% | 0.006 |
| Bibbia latina: testo in chiaro | 3.26 | 5.24 | 0.184 | 0.51 | ×0.11 | 0.3% | 0.4% | 0.3% | 0.034 |
| Bibbia latina: Naibbe | 2.16 | 4.82 | 0.177 | 0.43 | ×0.52 | -0.1% | 0.0% | 0.1% | 0.003 |
| Bibbia latina: Naibbe con deriva di pagina (concentrazione 3.0) | 2.16 | 4.81 | 0.167 | 0.44 | ×0.50 | 0.7% | 0.7% | 0.8% | 0.003 |
| Bibbia latina: Naibbe con deriva di pagina (concentrazione 1.0) | 2.16 | 4.82 | 0.149 | 0.43 | ×0.45 | 1.2% | 1.3% | 1.3% | 0.002 |
| Bibbia latina: Naibbe con deriva di pagina (concentrazione 0.3) | 2.17 | 4.83 | 0.116 | 0.42 | ×0.46 | 2.1% | 2.2% | 2.2% | 0.005 |
| Bibbia italiana: testo in chiaro | 3.15 | 4.50 | 0.136 | 0.49 | ×0.16 | 0.2% | 0.1% | -0.0% | 0.075 |
| Bibbia italiana: Naibbe | 2.20 | 4.74 | 0.166 | 0.37 | ×0.59 | -0.1% | -0.1% | -0.1% | 0.005 |
| Bibbia italiana: Naibbe con deriva di pagina (concentrazione 3.0) | 2.20 | 4.75 | 0.162 | 0.39 | ×0.69 | 0.6% | 0.6% | 0.6% | 0.007 |
| Bibbia italiana: Naibbe con deriva di pagina (concentrazione 1.0) | 2.19 | 4.73 | 0.140 | 0.41 | ×0.66 | 1.2% | 1.3% | 1.1% | 0.006 |
| Bibbia italiana: Naibbe con deriva di pagina (concentrazione 0.3) | 2.21 | 4.72 | 0.113 | 0.43 | ×0.67 | 1.6% | 1.6% | 1.6% | 0.013 |
