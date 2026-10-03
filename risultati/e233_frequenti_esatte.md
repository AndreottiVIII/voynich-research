# e233 — Parole frequenti esatte, rare variate, e copia della parola precedente

Generatore dell'e232 (η 1, δ 0) con κ (modifiche medie MU·(2r)^κ) e χ (seconda candidata variante della parola precedente); dopo la generazione σ 0,09 e prefissi staccati π 0,30 (e227d). AUC del discriminatore dell'e231. Validità (κ 0, χ 0 = e232): sì. Preregistrazione: `preregistrazioni/e233.md`.

| | AUC | fra le 100 | uniche nel testo | somiglianza vicine | tipi su parole (pagina) |
|---|---|---|---|---|---|
| **Voynich** | | 0.424 | 0.137 | 0.223 | 0.756 |
| kappa 0.0, chi 0.0, seme 1 | 0.938 | 0.392 | 0.108 | 0.192 | 0.683 |
| kappa 0.0, chi 0.1, seme 1 | 0.945 | 0.400 | 0.109 | 0.198 | 0.681 |
| kappa 0.0, chi 0.2, seme 1 | 0.957 | 0.388 | 0.106 | 0.203 | 0.690 |
| kappa 0.5, chi 0.0, seme 1 | 0.929 | 0.412 | 0.108 | 0.192 | 0.674 |
| kappa 0.5, chi 0.1, seme 1 | 0.891 | 0.412 | 0.109 | 0.201 | 0.666 |
| kappa 0.5, chi 0.2, seme 1 | 0.900 | 0.413 | 0.108 | 0.204 | 0.670 |
| kappa 1.0, chi 0.0, seme 1 | 0.863 | 0.425 | 0.116 | 0.196 | 0.669 |
| kappa 1.0, chi 0.1, seme 1 | 0.901 | 0.435 | 0.116 | 0.202 | 0.661 |
| kappa 1.0, chi 0.2, seme 1 | 0.860 | 0.419 | 0.113 | 0.209 | 0.669 |
| kappa 0.0, chi 0.0, semi 2–3 | 0.931 | 0.390 | 0.107 | 0.192 | 0.686 |
| kappa 1.0, chi 0.2, semi 2–3 | 0.889 | 0.428 | 0.111 | 0.206 | 0.666 |

Caratteristiche più pesanti che restano (kappa 1.0, chi 0.2, seme 2; coefficiente positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 lunghezza media | -2.03 | 4.2913 | 4.0136 |
| G3 fra le 100 piu frequenti | -1.65 | 0.4244 | 0.4272 |
| G3 uniche nella pagina | -1.60 | 0.6359 | 0.5200 |
| G3 lunghezza deviazione | +1.56 | 1.5790 | 1.6457 |
| G2 ch+d | +1.31 | 0.0053 | 0.0065 |
| G3 tipi su parole | -1.22 | 0.7559 | 0.6639 |
| G1 s | -1.18 | 0.0179 | 0.0184 |
| G3 uniche nel testo | -0.99 | 0.1461 | 0.1173 |
| G2 t+ch | -0.93 | 0.0119 | 0.0090 |
| G5 verticale | -0.86 | 0.0051 | -0.0024 |

Esito: **non aiuta abbastanza**.
