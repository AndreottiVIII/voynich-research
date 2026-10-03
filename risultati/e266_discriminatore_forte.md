# e266 — Un discriminatore più forte

Caratteristiche dell'e231 più G6 (coppie di parole), G7 (posizione nella riga), G8 (prime righe di paragrafo), G9 (ortografia di pagina). Controlli: A contro B 1.000; etichette a caso 0.519. Preregistrazione: `preregistrazioni/e266.md`.

| confronto | AUC | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|
| generatore e192 (seme 1) | 0.985 | 0.632 | 0.788 | 0.916 | 0.939 | 0.494 | 0.864 | 0.863 | 0.858 | 0.669 |
| generatore e241 (seme 2) | 0.937 | 0.631 | 0.649 | 0.896 | 0.686 | 0.540 | 0.805 | 0.682 | 0.874 | 0.661 |

Caratteristiche più pesanti contro il generatore e241 (coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G8 p prime righe meno altre | -1.77 | 0.0331 | 0.0120 |
| G3 uniche nella pagina | -1.36 | 0.6359 | 0.5417 |
| G6 coppie identiche | +1.34 | 0.0097 | 0.0227 |
| G3 tipi su parole | -1.21 | 0.7559 | 0.6794 |
| G8 f prime righe meno altre | -1.20 | 0.0103 | 0.0021 |
| G3 lunghezza deviazione | +0.95 | 1.5790 | 1.6626 |
| G6 coppie viste altrove | -0.85 | 0.2213 | 0.2079 |
| G2 d+ch | +0.81 | 0.0039 | 0.0056 |
| G3 fra le 100 piu frequenti | -0.77 | 0.4244 | 0.4137 |
| G6 somiglianza a distanza 2 | -0.71 | 0.2198 | 0.2014 |
| G8 k prime righe meno altre | +0.64 | -0.0236 | -0.0022 |
| G8 lunghezza parole prime righe | -0.57 | 4.6323 | 4.1807 |

Esito: **piu' forte** (riferimento e231 sul generatore e241: 0.874).
