# Esperimento 7: testi veri codificati

Tre testi (35.000 parole) codificati in quattro modi, misurati come il Voynich. Per i testi artificiali: righe finte da 8 parole, pagine da 20 righe.

- **h2**: incertezza sulla lettera (glifo) successiva, bit.
- **lung.**: lunghezza media delle parole in glifi (lettere per i testi in chiaro).
- **tipi/parole**, **hapax**: varietà del vocabolario sulle prime 30.000 parole.
- **identiche subito**: quota di parole uguali alla precedente; tra parentesi, rispetto a due parole a caso della stessa riga.
- **somiglianza**: quanto due parole diverse si somigliano più del caso, nella stessa riga, fra una riga e quella sotto, a sei righe di distanza.

| testo | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza: stessa riga | riga sotto | 6 righe sotto |
|---|---|---|---|---|---|---|---|---|
| **Voynich (pagine e righe vere)** | 2.24 | 4.46 | 0.210 | 0.68 | 0.94% (×1.01) | 3.8% | 4.0% | 3.4% |
| **Voynich (righe finte da 8 parole)** | 2.24 | 4.46 | 0.210 | 0.68 | 0.87% (×0.94) | 4.1% | 3.6% | 2.6% |
| Vitruvio: testo in chiaro | 3.30 | 6.18 | 0.274 | 0.62 | 0.12% (×0.23) | 0.4% | 0.4% | 0.2% |
| Vitruvio: cifrario verboso | 3.27 | 6.28 | 0.274 | 0.62 | 0.12% (×0.23) | 0.4% | 0.4% | 0.2% |
| Vitruvio: codice parola per parola | 2.36 | 4.72 | 0.274 | 0.62 | 0.12% (×0.23) | 0.1% | 0.0% | 0.0% |
| Vitruvio: codice con varianti | 2.57 | 5.41 | 0.418 | 0.64 | 0.03% (×0.44) | 0.2% | 0.1% | 0.2% |
| Vitruvio: codice con stile di pagina (3 regole, forza 0.7) | 2.64 | 5.03 | 0.436 | 0.74 | 0.20% (×0.46) | 4.9% | 4.9% | 4.9% |
| Vitruvio: codice con stile di pagina (6 regole, forza 0.9) | 2.81 | 5.56 | 0.559 | 0.77 | 0.26% (×0.53) | 13.2% | 13.2% | 13.2% |
| Vitruvio: sillabe come parole | 1.90 | 4.03 | 0.042 | 0.26 | 0.14% (×0.27) | 0.1% | 0.1% | 0.1% |
| Bibbia latina: testo in chiaro | 3.26 | 5.24 | 0.184 | 0.51 | 0.13% (×0.11) | 0.3% | 0.4% | 0.3% |
| Bibbia latina: cifrario verboso | 3.19 | 5.42 | 0.184 | 0.51 | 0.13% (×0.11) | 0.3% | 0.4% | 0.2% |
| Bibbia latina: codice parola per parola | 2.21 | 4.48 | 0.184 | 0.51 | 0.13% (×0.11) | 0.1% | 0.0% | 0.1% |
| Bibbia latina: codice con varianti | 2.50 | 5.07 | 0.321 | 0.54 | 0.05% (×0.29) | 0.2% | 0.2% | 0.2% |
| Bibbia latina: codice con stile di pagina (3 regole, forza 0.7) | 2.50 | 4.76 | 0.338 | 0.69 | 0.16% (×0.19) | 4.3% | 4.4% | 4.4% |
| Bibbia latina: codice con stile di pagina (6 regole, forza 0.9) | 2.72 | 5.30 | 0.472 | 0.73 | 0.36% (×0.34) | 12.7% | 12.8% | 12.8% |
| Bibbia latina: sillabe come parole | 1.90 | 4.07 | 0.039 | 0.22 | 0.11% (×0.19) | -0.3% | -0.1% | -0.0% |
| Bibbia italiana: testo in chiaro | 3.15 | 4.50 | 0.136 | 0.49 | 0.11% (×0.16) | 0.2% | 0.1% | -0.0% |
| Bibbia italiana: cifrario verboso | 3.13 | 4.66 | 0.136 | 0.49 | 0.11% (×0.16) | 0.2% | 0.1% | -0.0% |
| Bibbia italiana: codice parola per parola | 2.12 | 4.29 | 0.136 | 0.49 | 0.11% (×0.16) | -0.2% | -0.0% | -0.1% |
| Bibbia italiana: codice con varianti | 2.48 | 4.90 | 0.256 | 0.50 | 0.05% (×0.46) | -0.2% | -0.2% | -0.2% |
| Bibbia italiana: codice con stile di pagina (3 regole, forza 0.7) | 2.45 | 4.58 | 0.278 | 0.65 | 0.18% (×0.32) | 4.8% | 5.0% | 4.9% |
| Bibbia italiana: codice con stile di pagina (6 regole, forza 0.9) | 2.69 | 5.10 | 0.416 | 0.69 | 0.34% (×0.42) | 14.2% | 14.4% | 14.3% |
| Bibbia italiana: sillabe come parole | 1.80 | 3.93 | 0.032 | 0.23 | 0.24% (×0.30) | 0.1% | 0.0% | -0.0% |
