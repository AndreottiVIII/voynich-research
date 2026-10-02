# e231 — Discriminatore: pagine vere contro pagine del generatore

Regressione logistica su caratteristiche di pagina, validazione incrociata a 10 pieghe ripetuta 5 volte; per il generatore la pagina vera e la gemella generata stanno nella stessa piega. Preregistrazione: `preregistrazioni/e231.md`.

| confronto | pagine | AUC | G1 segni | G2 coppie | G3 parole | G4 riga | G5 verticale |
|---|---|---|---|---|---|---|---|
| controllo positivo (A contro B) | 196 | 1.000 | 0.988 | 1.000 | 0.930 | 0.893 | 0.430 |
| generatore e192 contro Voynich | 202 | 0.970 | 0.632 | 0.788 | 0.916 | 0.939 | 0.494 |
| controllo negativo (etichette a caso) | 202 | 0.527 | | | | | |

Caratteristiche più pesanti (coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G4 fine m | -2.01 | 0.1392 | 0.0230 |
| G4 unioni attestate | -1.55 | 0.0916 | 0.0484 |
| G3 fra le 100 piu frequenti | -1.46 | 0.4244 | 0.3558 |
| G3 uniche nel testo | -1.14 | 0.1461 | 0.1270 |
| G3 uniche nella pagina | -1.09 | 0.6359 | 0.5552 |
| G3 tipi su parole | -0.91 | 0.7559 | 0.6922 |
| G4 fine l | +0.79 | 0.0915 | 0.1519 |
| G4 fine o | +0.73 | 0.0123 | 0.0497 |
| G2 p+sh | +0.71 | 0.0006 | 0.0017 |
| G2 t+e | +0.62 | 0.0090 | 0.0107 |

Esito: **distinguibile**.
