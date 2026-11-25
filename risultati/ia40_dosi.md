# IA40 (ia40) — Tavola a dosi forzate

Preregistrazione: `preregistrazioni/ia40.md`. Mondo `vero`. Solo numeri e aggregati. `sezione` non e' piu' tenuta fuori: e' riportata a parte.

**Esito: ESISTE una riga buona: s100k30, s100k100, s100k100r.** Riga buona = `sezione` entro 2σ, b ≤ 0.65, almeno 7 delle altre 9 misure entro 2σ, guardia anti-copia a posto.

| riga | che cos'e' | N | KN | b | `sezione` z | altre 9 entro 2σ | fuori (delle 9) | div. sezioni bigr / parole | copia | buona |
|---|---|---|---|---|---|---|---|---|---|---|
| t000 | termostato globale a forza 0 | 0.996 | 0.977 | 0.986 (0.026) | 9.9 | 3 su 9 | D, burst, riga_cv, lag23, ttr_pagina, hapax | 0.1166 / 0.3445 | ok | no |
| t025 | termostato globale a forza 0.25 | 0.667 | 0.777 | 0.716 (0.015) | -1.9 | 6 su 9 | burst, lag23, ttr_pagina | 0.0715 / 0.2001 | ok | no |
| t050 | termostato globale a forza 0.5 | 0.457 | 0.676 | 0.624 (0.023) | -4.1 | 7 su 9 | R_rel, ttr_pagina | 0.0554 / 0.1471 | ok | no |
| t075 | termostato globale a forza 0.75 | 0.356 | 0.648 | 0.636 (0.016) | -4.9 | 8 su 9 | ttr_pagina | 0.0492 / 0.1272 | ok | no |
| t100 | termostato globale a forza 1 (punto di IA35) | 0.304 | 0.650 | 0.630 (0.028) | -5.3 | 9 su 9 | - | 0.0430 / 0.1104 | ok | no |
| s50k30 | punto di IA35 con a_sez 0.5, ripiego K 30 | 0.317 | 0.607 | 0.587 (0.025) | -2.8 | 9 su 9 | - | 0.0539 / 0.1594 | ok | no |
| s50k100 | punto di IA35 con a_sez 0.5, ripiego K 100 | 0.318 | 0.618 | 0.556 (0.021) | -3.5 | 9 su 9 | - | 0.0453 / 0.1327 | ok | no |
| s50k300 | punto di IA35 con a_sez 0.5, ripiego K 300 | 0.311 | 0.621 | 0.570 (0.025) | -4.0 | 7 su 9 | burst, hapax | 0.0352 / 0.1033 | ok | no |
| s100k30 | punto di IA35 con a_sez 1, ripiego K 30 | 0.345 | 0.607 | 0.582 (0.029) | -1.2 | 8 su 9 | ini_par | 0.0598 / 0.1825 | ok | SI |
| s100k100 | punto di IA35 con a_sez 1, ripiego K 100 | 0.362 | 0.619 | 0.587 (0.018) | -2.0 | 7 su 9 | burst, ini_par | 0.0485 / 0.1473 | ok | SI |
| s100k300 | punto di IA35 con a_sez 1, ripiego K 300 | 0.374 | 0.642 | 0.561 (0.028) | -2.7 | 6 su 9 | burst, lag23, ini_par | 0.0361 / 0.1068 | ok | no |
| m20 | punto di IA35 con w_sez 0.2 (decadimento neutro) | 0.371 | 0.699 | 0.623 (0.021) | -5.0 | 6 su 9 | R_rel, burst, ini_par | 0.0474 / 0.1261 | ok | no |
| m50 | punto di IA35 con w_sez 0.5 (decadimento neutro) | 0.652 | 0.835 | 0.708 (0.021) | -3.6 | 5 su 9 | D, heaps, ini_par, ttr_pagina | 0.0702 / 0.2019 | ok | no |
| neu | manopole neutre (rete sola) | 0.942 | 0.722 | 0.777 (0.020) | 2.0 | 4 su 9 | burst, riga_cv, lag23, ini_par, ttr_pagina | 0.0632 / 0.1988 | ok | no |
| t100r | ripetizione di t100 con altri semi | 0.297 | 0.650 | 0.616 (0.029) | -5.4 | 8 su 9 | hapax | 0.0441 / 0.1114 | ok | no |
| s100k100r | ripetizione di s100k100 con altri semi | 0.348 | 0.618 | 0.589 (0.022) | -2.0 | 8 su 9 | burst | 0.0486 / 0.1477 | ok | SI |

Divergenza fra sezioni del testo vero: bigrammi 0.0678, parole 0.2077.

**Rumore (righe ripetute con altri semi):** t100: |Δb| 0.015, |Δz `sezione`| 0.1, |Δ altre nove| 1; s100k100: |Δb| 0.001, |Δz `sezione`| 0.0, |Δ altre nove| 1. Le differenze piu' piccole di queste non si leggono.

Misure tenute fuori (z in sigma) per riga:

- `t000`: D 3.9, R_rel 0.6, heaps -1.1, burst -9.1, riga_cv 2.4, sezione 9.9, lag23 25.0, ini_par 1.0, ttr_pagina -20.2, hapax -13.2
- `t025`: D 1.7, R_rel -1.0, heaps -0.1, burst -3.3, riga_cv 1.4, sezione -1.9, lag23 4.2, ini_par 1.2, ttr_pagina -6.5, hapax -1.8
- `t050`: D 1.0, R_rel -2.2, heaps 0.4, burst -1.0, riga_cv 1.0, sezione -4.1, lag23 0.9, ini_par 1.1, ttr_pagina -3.9, hapax 0.3
- `t075`: D 0.7, R_rel -2.0, heaps 1.0, burst 0.6, riga_cv 0.9, sezione -4.9, lag23 -0.5, ini_par 1.3, ttr_pagina -2.5, hapax 1.2
- `t100`: D 0.7, R_rel -1.2, heaps 1.4, burst 1.6, riga_cv 0.8, sezione -5.3, lag23 -1.5, ini_par 1.5, ttr_pagina -1.5, hapax 2.0
- `s50k30`: D 0.8, R_rel -0.8, heaps 0.0, burst 0.5, riga_cv 1.2, sezione -2.8, lag23 -0.7, ini_par 1.6, ttr_pagina -1.7, hapax 1.5
- `s50k100`: D 0.7, R_rel -1.5, heaps 0.1, burst 1.5, riga_cv 1.1, sezione -3.5, lag23 -0.9, ini_par 1.6, ttr_pagina -1.4, hapax 1.8
- `s50k300`: D 0.7, R_rel -1.8, heaps 0.1, burst 2.3, riga_cv 1.1, sezione -4.0, lag23 -1.8, ini_par 1.6, ttr_pagina -0.9, hapax 2.2
- `s100k30`: D 0.1, R_rel -0.7, heaps -0.1, burst 1.0, riga_cv 1.6, sezione -1.2, lag23 -0.9, ini_par 2.4, ttr_pagina -0.9, hapax 1.0
- `s100k100`: D 0.2, R_rel -0.8, heaps -0.2, burst 2.4, riga_cv 1.5, sezione -2.0, lag23 -2.0, ini_par 2.1, ttr_pagina -0.3, hapax 1.5
- `s100k300`: D 0.3, R_rel -1.0, heaps -0.1, burst 4.2, riga_cv 1.4, sezione -2.7, lag23 -3.3, ini_par 2.1, ttr_pagina 0.2, hapax 1.3
- `m20`: D -0.3, R_rel -2.7, heaps 1.6, burst 2.2, riga_cv 0.9, sezione -5.0, lag23 -1.7, ini_par 4.0, ttr_pagina -1.4, hapax 0.9
- `m50`: D -2.9, R_rel -2.0, heaps 2.5, burst -0.2, riga_cv 1.4, sezione -3.6, lag23 -0.3, ini_par 7.1, ttr_pagina -2.4, hapax -1.8
- `neu`: D 1.7, R_rel -1.0, heaps 0.8, burst 5.8, riga_cv 2.1, sezione 2.0, lag23 -4.5, ini_par -2.3, ttr_pagina 2.6, hapax 1.1
- `t100r`: D 0.7, R_rel -1.5, heaps 1.3, burst 1.3, riga_cv 0.8, sezione -5.4, lag23 -1.3, ini_par 1.4, ttr_pagina -1.6, hapax 2.3
- `s100k100r`: D 0.4, R_rel -0.9, heaps -0.1, burst 2.2, riga_cv 1.5, sezione -2.0, lag23 -1.8, ini_par 1.8, ttr_pagina -0.4, hapax 1.1
