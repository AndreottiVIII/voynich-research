# e288 — Le materie che il generatore manca: ripetizione, verticale, spazio

Copia di e233.genera con penalità rip per le ripetizioni immediate, φ (copia per indice dalla riga sopra) e σ di `dopo`. Validità: sì. Preregistrazione: `preregistrazioni/e288.md`.

| configurazione (seme 1) | pagella | riga | mancano | AUC e266 | ripetizione | verticale | spazio |
|---|---|---|---|---|---|---|---|
| rip 0.5, phi 0.10, sigma 0.04 | 18 | sì | — | 0.937 | 1.16 | 1.019 | 0.617 |
| rip 0.5, phi 0.10, sigma 0.06 | 17 | sì | verticale | 0.941 | 1.15 | 1.012 | 0.603 |
| rip 0.5, phi 0.05, sigma 0.06 | 17 | sì | formule | 0.942 | 1.06 | 1.019 | 0.601 |
| rip 0.5, phi 0.00, sigma 0.09 | 17 | sì | verticale | 0.955 | 1.17 | 1.001 | 0.584 |
| rip 0.3, phi 0.10, sigma 0.06 | 16 | sì | omogeneità, formule | 0.916 | 0.82 | 1.030 | 0.596 |
| rip 0.3, phi 0.10, sigma 0.04 | 16 | sì | ripetizione, formule | 0.924 | 0.80 | 1.029 | 0.608 |
| rip 0.3, phi 0.10, sigma 0.09 | 16 | sì | spazio, omogeneità | 0.936 | 0.84 | 1.026 | 0.577 |
| rip 0.5, phi 0.05, sigma 0.04 | 16 | sì | verticale, formule | 0.944 | 1.14 | 1.005 | 0.616 |
| rip 0.5, phi 0.00, sigma 0.04 | 16 | sì | verticale, formule | 0.947 | 1.16 | 1.004 | 0.618 |
| rip 0.5, phi 0.00, sigma 0.06 | 16 | sì | verticale, formule | 0.949 | 1.19 | 1.002 | 0.602 |
| rip 1.0, phi 0.00, sigma 0.06 | 16 | sì | ripetizione, verticale | 0.952 | 1.43 | 0.996 | 0.599 |
| rip 1.0, phi 0.10, sigma 0.06 | 16 | sì | ripetizione, curva piatta | 0.954 | 1.46 | 1.025 | 0.601 |
| rip 1.0, phi 0.00, sigma 0.04 | 16 | sì | ripetizione, verticale | 0.957 | 1.43 | 1.012 | 0.614 |
| rip 1.0, phi 0.10, sigma 0.04 | 16 | no | ripetizione, curva piatta | 0.958 | 1.47 | 1.034 | 0.615 |
| rip 1.0, phi 0.10, sigma 0.09 | 16 | sì | spazio, ripetizione | 0.962 | 1.47 | 1.027 | 0.583 |
| rip 0.5, phi 0.05, sigma 0.09 | 15 | sì | omogeneità, verticale, formule | 0.946 | 1.11 | 1.010 | 0.584 |
| rip 1.0, phi 0.05, sigma 0.06 | 15 | no | ripetizione, profilo pagina, verticale | 0.956 | 1.46 | 1.009 | 0.597 |
| rip 0.3, phi 0.05, sigma 0.06 | 15 | sì | curva piatta, verticale, formule | 0.957 | 1.01 | 1.006 | 0.587 |
| rip 1.0, phi 0.05, sigma 0.04 | 15 | no | ripetizione, profilo pagina, verticale | 0.957 | 1.43 | 1.009 | 0.610 |
| rip 0.3, phi 0.05, sigma 0.09 | 15 | sì | spazio, omogeneità, verticale | 0.959 | 1.01 | 1.010 | 0.570 |
| rip 0.3, phi 0.05, sigma 0.04 | 15 | sì | curva piatta, verticale, formule | 0.962 | 0.97 | 1.015 | 0.598 |
| rip 0.5, phi 0.10, sigma 0.09 | 15 | sì | spazio, omogeneità, verticale | 0.962 | 1.15 | 1.002 | 0.582 |
| rip 0.3, phi 0.00, sigma 0.06 | 14 | sì | ripetizione, curva piatta, verticale, formule | 0.946 | 0.79 | 1.001 | 0.598 |
| rip 0.3, phi 0.00, sigma 0.04 | 14 | sì | ripetizione, curva piatta, verticale, formule | 0.951 | 0.78 | 0.995 | 0.612 |
| rip 1.0, phi 0.00, sigma 0.09 | 14 | sì | spazio, ripetizione, omogeneità, verticale | 0.956 | 1.40 | 1.003 | 0.581 |
| rip 1.0, phi 0.05, sigma 0.09 | 14 | sì | spazio, ripetizione, profilo pagina, verticale | 0.957 | 1.43 | 1.015 | 0.579 |
| rip 0.3, phi 0.00, sigma 0.09 | 13 | sì | spazio, ripetizione, omogeneità, verticale, formule | 0.956 | 0.78 | 0.993 | 0.579 |

Voynich: ripetizione 1,01, verticale 1,028, spazio 0,664. Scelta: **rip 0.5, phi 0.10, sigma 0.04**.

| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| 7 | rip 1.0, phi 0.00, sigma 0.09 | 15/18 | sì | ripetizione, profilo pagina, verticale | 0.887 | 0.966 |
| 7 | rip 0.5, phi 0.10, sigma 0.04 | 18/18 | sì | — | 0.855 | 0.937 |
| 8 | rip 1.0, phi 0.00, sigma 0.09 | 15/18 | no | spazio, ripetizione, verticale | 0.854 | 0.953 |
| 8 | rip 0.5, phi 0.10, sigma 0.04 | 17/18 | sì | omogeneità | 0.828 | 0.937 |
| 9 | rip 1.0, phi 0.00, sigma 0.09 | 15/18 | sì | spazio, ripetizione, verticale | 0.879 | 0.965 |
| 9 | rip 0.5, phi 0.10, sigma 0.04 | 18/18 | sì | — | 0.816 | 0.926 |

Medie: e241 pagella 45 (somma), riga in 2 semi, AUC 0.873 / 0.961; scelta pagella 53, riga in 3 semi, AUC 0.833 / 0.933.

Esito: **migliore**.
