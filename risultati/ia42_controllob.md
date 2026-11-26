# IA42 (ia42) — Controllo B: un libro v21 come "vero"

Preregistrazione: `preregistrazioni/ia42.md`. Il "vero" e' il libro v21 n. 13 (con parole e impaginazione del Voynich: limite dichiarato); gemelli = gli altri nove. Solo numeri e aggregati.

**Esito: STESSO VOTO: sul libro v21 (regola nota) l'imitatore prende lo stesso b che sul Voynich (0,66): limite del metodo con cosi' poco testo, niente di proprio del Voynich.**

## Validita'

- Gemelli (b medio sulle divisioni 1, 2, 3, 4): 0.499, in fascia 0,40-0,60: True; per divisione 0.566, 0.521, 0.391, 0.519.
- Pagine rimescolate (difetto piantato): `sezione` z -3.9 (vista: True), `vicine` z -2.7 (vista: False); indovina-sezione vero 0.940, rimescolate 0.383 (vista: True).
- Controllo valido: True.

## b dell'imitatore sul libro v21

| riga | b medio | per divisione |
|---|---|---|
| s100k30 | 0.661 | 0.686, 0.695, 0.629, 0.634 |
| t100 | 0.606 | 0.581, 0.659, 0.634, 0.550 |
| neu | 0.968 | |
| gemelli (altri libri v21) | 0.499 | 0.566, 0.521, 0.391, 0.519 |

b medio di `t100` e `s100k30`: **0.633** (sul Voynich in IA41: 0,66). Previsione scritta (stesso voto, 0,61-0,68): confermata.

## Le tre misure di riferimento (z medio di `s100k30`, in unita' di rumore di campionamento)

| misura | qui | Voynich (IA41) | gemelli | lettura |
|---|---|---|---|---|
| dispersione | -1.3 | -2.2 | 0.0 | dentro qui e fuori sul Voynich: proprio del Voynich |
| vicine | -0.8 | -2.2 | -0.2 | fuori dal verdetto (non vede il suo difetto) |
| sezione | -1.3 | -1.5 | -0.5 | dentro qui e dentro sul Voynich |

Previsione scritta: `dispersione` fuori anche qui: False; `vicine` dentro: None.

Altre misure fuori da 2σ per `s100k30`: burst, ini_par, hapax, doppie.

## Tutte le misure (z medio)

| misura | s100k30 | t100 | gemelli |
|---|---|---|---|
| heaps | 0.7 | 1.1 | 0.4 |
| burst | -2.4 | -0.8 | -0.6 |
| riga_cv | -0.3 | -0.3 | 0.1 |
| sezione | -1.3 | -4.4 | -0.5 |
| lag23 | 0.7 | -0.5 | -0.5 |
| ini_par | 2.2 | 1.5 | -0.4 |
| ttr_pagina | -0.3 | -0.3 | 0.3 |
| hapax | 3.3 | 2.7 | 0.7 |
| dispersione (nuova) | -1.3 | -2.2 | 0.0 |
| vicine (nuova) | -0.8 | -0.4 | -0.2 |
| lunghezza (nuova) | -0.2 | -1.1 | 0.1 |
| doppie (nuova) | 2.5 | 2.2 | -0.8 |
| testa (nuova) | -0.5 | 0.6 | -0.1 |

## Per divisione

| divisione | riga | b | indovina-sezione | `sezione` z | pagine tenute fuori |
|---|---|---|---|---|---|
| 1 | s100k30 | 0.686 (0.025) | 0.947 | -1.2 | 26 |
| 1 | t100 | 0.581 (0.025) | 0.692 | -5.0 | 26 |
| 1 | neu | 0.970 (0.023) | 0.909 | 0.3 | 26 |
| 1 | gem | 0.566 (0.022) | 1.000 | 0.1 | 26 |
| 2 | s100k30 | 0.695 (0.019) | 0.963 | -2.2 | 30 |
| 2 | t100 | 0.659 (0.021) | 0.608 | -5.2 | 30 |
| 2 | neu | 0.971 (0.017) | 0.921 | -1.6 | 30 |
| 2 | gem | 0.521 (0.021) | 0.989 | -0.4 | 30 |
| 3 | s100k30 | 0.629 (0.029) | 0.871 | -1.0 | 28 |
| 3 | t100 | 0.634 (0.020) | 0.594 | -5.0 | 28 |
| 3 | neu | 0.977 (0.035) | 0.839 | 1.6 | 28 |
| 3 | gem | 0.391 (0.027) | 0.944 | -1.7 | 28 |
| 4 | s100k30 | 0.634 (0.016) | 0.902 | -0.8 | 33 |
| 4 | t100 | 0.550 (0.019) | 0.738 | -2.2 | 33 |
| 4 | neu | 0.953 (0.041) | 0.871 | -0.7 | 33 |
| 4 | gem | 0.519 (0.014) | 0.962 | 0.1 | 33 |
