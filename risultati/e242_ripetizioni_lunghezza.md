# e242 — Meno ripetizioni e parole rare più lunghe, sopra l'e241

Generatore dell'e241 con τ (tema variato) e ℓr (preferenza per le parole lunghe solo fra le non frequenti). AUC del discriminatore dell'e231; riferimento (e241) 0.874. Preregistrazione: `preregistrazioni/e242.md`.

| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | N |
|---|---|---|---|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 | 31.9% | 14.3% |
| tau 0.0, ell_r 0.0, seme 1 | 0.880 | 0.675 | 0.412 | 0.117 | 0.204 | 4.196 | 38.7% | 12.0% |
| tau 0.0, ell_r 1.0, seme 1 | 0.878 | 0.687 | 0.398 | 0.132 | 0.212 | 4.381 | 37.1% | 13.3% |
| tau 0.5, ell_r 0.0, seme 1 | 0.858 | 0.722 | 0.385 | 0.128 | 0.205 | 4.255 | 34.5% | 12.4% |
| tau 0.5, ell_r 1.0, seme 1 | 0.864 | 0.721 | 0.381 | 0.139 | 0.210 | 4.401 | 34.0% | 13.6% |
| tau 0.5, ell_r 0.0, semi 2–3 | 0.879 | 0.715 | 0.396 | 0.125 | 0.204 | 4.223 | 35.2% | 12.3% |

Pagella dell'e224 sulla scelta (seme 2): 13/18, riga riprodotta: no; mancano: spazio, ripetizione, deriva, profilo pagina, verticale.

Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 fra le 100 piu frequenti | -2.11 | 0.4244 | 0.3984 |
| G3 lunghezza media | -1.89 | 4.2913 | 4.1118 |
| G3 lunghezza deviazione | +1.47 | 1.5790 | 1.6759 |
| G3 uniche nella pagina | -1.33 | 0.6359 | 0.5689 |
| G3 uniche nel testo | -1.28 | 0.1461 | 0.1310 |
| G1 s | -1.12 | 0.0179 | 0.0195 |
| G2 i+r | +0.93 | 0.0047 | 0.0059 |
| G1 r | -0.85 | 0.0440 | 0.0409 |
| G2 y+ch | +0.77 | 0.0024 | 0.0032 |
| G2 d+ch | +0.75 | 0.0039 | 0.0050 |

Esito: **non migliore**.
