# e307 — Che cosa rende ogni pagina diversa dalle altre

Preregistrazione: `preregistrazioni/e307.md`. Pagine con almeno 60 parole, in strati sezione × lingua con almeno 3 pagine (Voynich: 183 pagine, 9 strati).

## A — Identità oltre sezione e lingua (distanza media pagina-strato)

| testo | rappresentazione | I | nullo | rapporto | z |
|---|---|---|---|---|---|
| Voynich | segni | 0.0263 | 0.0093 | 2.83 | 70.4 |
| Voynich | parole | 0.4641 | 0.4285 | 1.08 | 27.6 |
| Voynich | iniziali e finali | 0.0421 | 0.0179 | 2.35 | 57.4 |
| controllo positivo: Bibbia latina in pagine | segni | 0.0077 | 0.0044 | 1.75 | 49.1 |
| controllo positivo: Bibbia latina in pagine | parole | 0.5360 | 0.4999 | 1.07 | 63.8 |
| controllo positivo: Bibbia latina in pagine | iniziali e finali | 0.0202 | 0.0110 | 1.84 | 46.7 |
| controllo negativo: Voynich rimescolato | segni | 0.0094 | 0.0093 | 1.01 | 0.3 |
| controllo negativo: Voynich rimescolato | parole | 0.4285 | 0.4286 | 1.00 | -0.1 |
| controllo negativo: Voynich rimescolato | iniziali e finali | 0.0181 | 0.0179 | 1.01 | 0.4 |

Esito A: **pagine con identità**.

## B — Le caratteristiche che distinguono le pagine (eccesso di varianza sul nullo)

| caratteristica | eccesso | z |
|---|---|---|
| segno e | 8.99 | 73.2 |
| segno a | 4.90 | 31.9 |
| segno n | 4.68 | 30.8 |
| segno y | 4.61 | 31.3 |
| segno ch | 4.61 | 29.4 |
| iniziale o | 4.46 | 28.2 |
| segno d | 4.43 | 27.2 |
| finale y | 4.39 | 30.6 |
| iniziale ch | 4.31 | 27.6 |
| finale n | 4.28 | 27.5 |
| segno i | 3.99 | 25.2 |
| segno o | 3.95 | 23.6 |
| segno m | 3.63 | 22.0 |
| lunghezza media | 3.51 | 20.4 |
| segno l | 3.47 | 20.2 |

Le meno distintive: segno c (0.98), segno h (0.98), parola al (0.94), segno cfh (0.92), iniziale p (0.74).

## C — Da dove viene l'identità (correlazione fra profili di pagine dello stesso strato)

| coppie | numero | correlazione | nullo | z |
|---|---|---|---|---|
| consecutive | 140 | 0.209 | -0.032 | 10.9 |
| vicine (2-5) | 433 | -0.018 | -0.032 | 1.2 |
| stessa mano (>5) | 3691 | -0.024 | -0.016 | -5.5 |
| stesso fascicolo (>5) | 469 | 0.015 | -0.032 | 4.6 |
| altre (>5) | 250 | -0.074 | -0.033 | -3.8 |

Esito C: **temporale, di fascicolo**.

## D — Tipi di pagina

Silhouette migliore 0.084 con k = 2; nullo 0.048; z 3.2. Esito D: **tipi di pagina**.

- Gruppo 0 (98 pagine, posizione media 104): sezioni {'H': 60, 'A': 1, 'C': 2, 'B': 11, 'T': 2, 'P': 9, 'S': 13}; lingue {'A': 53, 'B': 43, '?': 2}; mani {'1': 53, '2': 24, '4': 2, '3': 19}; tratti segno e -1.67, segno a +1.32, finale y -1.24, segno n +1.21, segno i +1.13, finale n +1.12.
- Gruppo 1 (85 pagine, posizione media 106): sezioni {'H': 56, 'T': 3, 'B': 8, 'C': 1, 'P': 7, 'S': 10}; lingue {'A': 47, 'B': 38}; mani {'1': 47, '2': 21, '5': 7, '3': 9, '?': 1}; tratti segno e +1.93, segno a -1.52, finale y +1.43, segno n -1.40, segno i -1.30, finale n -1.29.
