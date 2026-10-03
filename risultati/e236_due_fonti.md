# e236 — Generatore a due fonti: parole frequenti esatte e varianti nuove

Candidate esatte dalle frequenze del manoscritto con probabilità g, altrimenti varianti con almeno una modifica di parole delle righe recenti (probabilità ρ) o del manoscritto; niente serbatoio di pagina; σ 0,09 e prefissi π 0,30 dopo la generazione. AUC del discriminatore dell'e231. Riferimento (e235): 0.889. Preregistrazione: `preregistrazioni/e236.md`.

| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media |
|---|---|---|---|---|---|---|
| **Voynich** | | 0.756 | 0.424 | 0.137 | 0.223 | 4.461 |
| g 0.60, rho 0.5, seme 1 | 0.992 | 0.836 | 0.375 | 0.142 | 0.172 | 4.132 |
| g 0.60, rho 0.9, seme 1 | 0.990 | 0.830 | 0.374 | 0.148 | 0.176 | 4.145 |
| g 0.75, rho 0.5, seme 1 | 0.976 | 0.819 | 0.402 | 0.119 | 0.170 | 4.116 |
| g 0.75, rho 0.9, seme 1 | 0.963 | 0.817 | 0.400 | 0.123 | 0.173 | 4.154 |
| g 0.90, rho 0.5, seme 1 | 0.967 | 0.803 | 0.431 | 0.101 | 0.174 | 4.143 |
| g 0.90, rho 0.9, seme 1 | 0.958 | 0.802 | 0.432 | 0.102 | 0.173 | 4.139 |
| g 0.90, rho 0.9, semi 2–3 | 0.946 | 0.801 | 0.429 | 0.102 | 0.174 | 4.140 |

Pagella dell'e224 sulla scelta (seme 2): 10/18, riga riprodotta: sì; mancano: uniche, omogeneità, gradiente, curva piatta, deriva, profilo pagina, lunghezze vicine, verticale.

Caratteristiche più pesanti che restano (seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G4 somiglianza fra vicine | -2.45 | 0.2181 | 0.1723 |
| G3 uniche nel testo | -1.98 | 0.1461 | 0.1043 |
| G3 lunghezza deviazione | +1.35 | 1.5790 | 1.6816 |
| G3 lunghezza media | -1.31 | 4.2913 | 4.0387 |
| G3 tipi su parole | +0.80 | 0.7559 | 0.7987 |
| G1 s | -0.79 | 0.0179 | 0.0177 |
| G2 p+sh | +0.74 | 0.0006 | 0.0014 |
| G3 fra le 100 piu frequenti | -0.65 | 0.4244 | 0.4294 |
| G3 uniche nella pagina | +0.62 | 0.6359 | 0.6826 |
| G2 t+ch | -0.60 | 0.0119 | 0.0085 |

Esito: **non migliore**.
