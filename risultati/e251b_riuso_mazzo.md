# e251b — Passo 2, secondo tentativo: riuso di pagina senza tema concentrato e senza reimmissione

Copia di e233.genera con θ (quota del tema), K (parole del tema) e mazzo (estrazione senza reimmissione dalla pagina, frequenti escluse). Validità (valori di controllo = e241): sì. Preregistrazione: `preregistrazioni/e251b.md`.

| configurazione (seme 1) | pagella | riga | R parole rare |
|---|---|---|---|
| e241 | 14 | sì | 44.4 |
| θ 0,3 K 12 | 14 | sì | 47.0 |
| θ 0,15 K 3 | 13 | sì | 45.4 |
| θ 0 | 14 | sì | 38.2 |
| mazzo, θ 0,3 K 3 | 12 | sì | 45.3 |
| mazzo, θ 0,15 K 3 | 10 | sì | 23.3 |
| mazzo, θ 0 | 10 | no | 10.2 |
| mazzo, θ 0,3 K 12 | 11 | sì | 33.2 |

P* 14; ammesse: θ 0,3 K 12, θ 0,15 K 3, θ 0; scelta: **θ 0**.

| seme | configurazione | pagella | riga | mancano | R rare | AUC e231 | G3 | AUC e266 | tipi/parole pagina |
|---|---|---|---|---|---|---|---|---|---|
| 7 | e241 | 15/18 | sì | ripetizione, profilo pagina, verticale | 48.5 | 0.887 | 0.914 | 0.966 | 0.681 |
| 7 | θ 0 | 14/18 | sì | spazio, ripetizione, omogeneità, verticale | 39.6 | 0.882 | 0.885 | 0.960 | 0.730 |
| 8 | e241 | 15/18 | no | spazio, ripetizione, verticale | 51.5 | 0.854 | 0.904 | 0.953 | 0.679 |
| 8 | θ 0 | 14/18 | sì | spazio, ripetizione, omogeneità, verticale | 43.1 | 0.864 | 0.875 | 0.948 | 0.733 |
| 9 | e241 | 15/18 | sì | spazio, ripetizione, verticale | 44.8 | 0.879 | 0.929 | 0.965 | 0.674 |
| 9 | θ 0 | 14/18 | sì | spazio, ripetizione, omogeneità, verticale | 42.4 | 0.856 | 0.881 | 0.961 | 0.730 |

Medie: e241: pagella 45 (somma), riga in 2 semi, R rare 48.3, AUC e231 0.873 (G3 0.916), e266 0.961, tipi/parole 0.678; θ 0: pagella 42 (somma), riga in 3 semi, R rare 41.7, AUC e231 0.867 (G3 0.880), e266 0.956, tipi/parole 0.731. Voynich: tipi su parole nella pagina 0,756.

Esito: **non superato: R + pagella**. Utile per il generatore (AUC e266 almeno 0,03 sotto a pagella non inferiore): **no**. Prosegue: **e241**.
