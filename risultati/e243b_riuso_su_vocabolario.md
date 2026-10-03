# e243b — Passo 1 del piano 18/18, rifatto: riuso sopra un vocabolario vero

Generatore dell'e242 (e241 + ℓr 1) con copia verticale fisica a distanza (φ 0.10, scelto sul seme 1 con l'AUC dell'e266) e penalità 0.3 per la ripetizione immediata. Validità (φ 0, senza penalità = e242): sì. Preregistrazione: `preregistrazioni/e243b.md`.

| seme | pagella | riga | mancano | AUC e231 | AUC e266 | R | V | N | R parole rare | ripetizioni immediate |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 16/18 | sì | verticale, formule | 0.876 | 0.941 | 37.0% | 35.3% | 13.5% | 49.5 | 0.92% |
| 8 | 16/18 | no | spazio, omogeneità | 0.888 | 0.969 | 36.4% | 35.7% | 13.8% | 55.2 | 0.94% |
| 9 | 15/18 | sì | omogeneità, verticale, formule | 0.871 | 0.931 | 36.8% | 35.6% | 13.5% | 56.5 | 0.99% |

Medie: pagella 15.7/18, AUC e231 0.878, AUC e266 0.947. Riferimenti: e241 16/18 (un seme), AUC e231 0,874, AUC e266 0,937; Voynich: R 31.9%, V 37.5%, N 14.3%, parole rare 1,96, ripetizioni immediate 0,97%.

Caratteristiche più pesanti del discriminatore dell'e231 (seme 7; positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 lunghezza deviazione | +1.99 | 1.5790 | 1.7540 |
| G3 fra le 100 piu frequenti | -1.76 | 0.4244 | 0.3974 |
| G3 uniche nella pagina | -1.43 | 0.6359 | 0.5526 |
| G3 tipi su parole | -1.42 | 0.7559 | 0.6888 |
| G4 somiglianza fra vicine | -1.29 | 0.2181 | 0.1930 |
| G2 i+i | +1.23 | 0.0415 | 0.0441 |
| G2 a+m | +1.01 | 0.0057 | 0.0099 |
| G1 m | +0.98 | 0.0065 | 0.0110 |
| G3 uniche nel testo | -0.94 | 0.1461 | 0.1422 |
| G2 d+a | -0.90 | 0.0373 | 0.0331 |

Esito: **non superato**.
