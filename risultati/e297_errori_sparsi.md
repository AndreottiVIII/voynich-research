# e297 — Errori sparsi nel generatore

Corpo dell'e288 più errori sparsi con probabilità p sulle parole frequenti. Validità (p 0 = e288): sì. Preregistrazione: `preregistrazioni/e297.md`.

| p (semi 1–2) | pagella | riga | R parole rare | AUC e266 |
|---|---|---|---|---|
| 0.00 | 34 | no | 52.5 | 0.931 |
| 0.01 | 33 | no | 52.2 | 0.934 |
| 0.02 | 34 | no | 52.9 | 0.930 |
| 0.04 | 34 | no | 51.1 | 0.932 |
| 0.08 | 32 | no | 50.2 | 0.936 |

Scelto p 0.04.

| seme | braccio | pagella | riga | mancano | R rare | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|---|
| 7 | e288 | 18/18 | sì | — | 52.9 | 0.855 | 0.937 |
| 7 | p 0.04 | 17/18 | sì | profilo pagina | 51.3 | 0.860 | 0.946 |
| 8 | e288 | 17/18 | sì | omogeneità | 50.3 | 0.828 | 0.937 |
| 8 | p 0.04 | 17/18 | sì | omogeneità | 50.7 | 0.828 | 0.940 |
| 9 | e288 | 18/18 | sì | — | 48.0 | 0.816 | 0.926 |
| 9 | p 0.04 | 17/18 | sì | curva piatta | 46.3 | 0.816 | 0.926 |

Medie: e288 pagella 53, riga in 3 semi, R 50.4, AUC 0.833 / 0.933; scelta pagella 51, riga in 3 semi, R 49.4, AUC 0.835 / 0.937.

Esito: **non utili**.
