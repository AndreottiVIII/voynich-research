# e210b — Capacità delle scelte di grafia con un modello sequenziale combinato

Regressione logistica per scelta, solo con il contesto precedente nell'ordine di lettura; validazione pagine pari/dispari. Preregistrazione: `preregistrazioni/e210b.md`.

| scelta | M0 | solo parola | combinato |
|---|---|---|---|
| F1 ch/sh | 0.877 | 0.848 | 0.793 |
| F2 k/t | 0.943 | 0.920 | 0.881 |
| F3 -l/-r | 0.998 | 0.967 | 0.939 |
| F5 qo-/o- | 1.000 | 0.988 | 0.924 |
| F7 -dy/-ey | 0.950 | 0.731 | 0.628 |
| **tutte (bit/occorrenza)** | 0.945 | 0.887 | 0.831 |
| **bit totali** | 53749 | 50410 | 47217 |

e182: 49215 bit; e210 (MXL, pseudo-verosimiglianza): 50097 bit. Combinato: 47217 bit (-4.1% su e182). Tre canali: 93177 bit, cioè 3788–7765 parole latine.

Esito: **il limite regge**.
