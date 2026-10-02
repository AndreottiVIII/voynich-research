# e226 — Dove nascono le parole nuove?

Parola nuova = prima occorrenza di un tipo (≥ 3 unità); genitore = tipo già visto a distanza di edit 1. L = quota con un genitore fra le parole precedenti della stessa unità / quota fra le prime parole di 20 unità precedenti a caso (stessa sezione quando c'è). Intervallo al 95% con 1000 ricampionamenti. Preregistrazione: `preregistrazioni/e226.md`.

| testo | unità | parole nuove | con un genitore | locale | controllo | L | intervallo | Heaps |
|---|---|---|---|---|---|---|---|---|
| Voynich | 207 | 6750 | 81% | 24.6% | 15.8% | 1.56 | 1.50–1.62 | 0.719 |
| generatore e192 (controllo positivo) | 207 | 6949 | 85% | 34.4% | 15.7% | 2.19 | 2.10–2.28 | 0.736 |
| Voynich rimescolato nella sezione (controllo negativo) | 207 | 6740 | 81% | 19.4% | 18.5% | 1.05 | 1.00–1.09 | 0.685 |
| Macer floridus, capitoli | 79 | 3737 | 34% | 5.3% | 3.5% | 1.52 | 1.33–1.78 | 0.708 |
| Isidoro XVII, paragrafi | 326 | 3895 | 27% | 2.9% | 0.4% | 6.75 | 5.21–8.71 | 0.808 |

Esito: **nascita intermedia**. Generatore troppo locale rispetto al Voynich: **no**.
