# ia45 — le colonne di segni singoli a margine

Preregistrazione: `preregistrazioni/ia45.md`. Solo numeri: i segni e il testo della trascrizione non stanno qui. Soglia di ogni test: p <= 0.00077 (0,01 diviso 13 test). **Non e' una decifrazione**: un esito dice solo quale ipotesi e' compatibile.

## Controlli (testo latino, 200 prove per mondo, 20000 rimescolamenti)

| mondo | prove | A | B1 | B2 |
|---|---|---|---|---|
| A | 200 | 1.000 | 0.000 | 0.000 |
| B | 200 | 0.000 | 1.000 | 1.000 |
| Bs | 200 | 0.005 | 0.005 | 1.000 |
| N1 | 200 | 0.005 | 0.000 | 0.015 |
| N2 | 200 | 0.000 | 0.005 | 1.000 |
| N3 | 200 | 0.000 | 0.000 | 0.990 |
| N4a | 200 | 0.000 | 0.005 | 0.005 |
| N4b | 200 | 0.005 | 0.250 | 1.000 |

| parte | positivo | tasso | falsi allarmi | cancello |
|---|---|---|---|---|
| A | A | 1.000 | N1 0.005, N2 0.000, N3 0.000, B 0.000, N4a 0.000, N4b 0.005 | ammessa |
| B1 | B | 1.000 | N1 0.000, N2 0.005, N3 0.000, A 0.000, N4a 0.005, N4b 0.250 | NON ammessa |
| B2 | Bs | 1.000 | N1 0.015, A 0.000, N4a 0.005 | ammessa |

## Conteggi (ZL)

| pagina | segni | distinti | glifi rari | illeggibili | righe di testo |
|---|---|---|---|---|---|
| f49v | 26 | 12 | 6 | 0 | 26 |
| f66r | 33 | 15 | 3 | 0 | 32 |
| f76r | 9 | 7 | 0 | 0 | 47 |
| f57v | 64 | 17 | 12 | 0 | 0 |

## Test, trascrizione ZL

| test | osservato | p | nota |
|---|---|---|---|
| A1 f49v-f66r | 0.0 | 1.00000 |  |
| A1 f49v-f57v | 0.0 | 1.00000 |  |
| A1 f66r-f57v | 1.0 | 0.99125 |  |
| A2 f49v | 0.368421 | 0.00255 | ritardo 7 |
| A2 f66r | 0.178571 | 0.29159 | ritardo 5 |
| A2 f57v | 0.958333 | 0.00005 | ritardo 16 |
| B1 f49v dopo | 1.0 | 0.65187 |  |
| B1 f49v prima | 1.0 | 0.57287 |  |
| B1 f76r dopo | 1.0 | 0.62372 |  |
| B1 f76r prima | 0.0 | 1.00000 |  |
| B2 f49v | 0.150792 | 0.00005 |  |
| B2 f66r | 0.404201 | 0.00005 |  |
| B2 f76r | 0.055336 | 0.03950 |  |

## Test, trascrizione IT

| test | osservato | p | nota |
|---|---|---|---|
| A1 f49v-f66r | 0.0 | 1.00000 |  |
| A1 f49v-f57v | 0.0 | 1.00000 |  |
| A1 f66r-f57v | 2.0 | 0.97340 |  |
| A2 f49v | 0.263158 | 0.02080 | ritardo 7 |
| A2 f66r | 0.178571 | 0.35448 | ritardo 5 |
| A2 f57v | 0.692308 | 0.00005 | ritardo 17 |
| B1 f49v dopo | 1.0 | 0.65297 |  |
| B1 f49v prima | 1.0 | 0.57582 |  |
| B1 f76r dopo | 1.0 | 0.62757 |  |
| B1 f76r prima | 0.0 | 1.00000 |  |
| B2 f49v | 0.446992 | 0.00005 |  |
| B2 f66r | 0.3042 | 0.00010 |  |
| B2 f76r | 0.097458 | 0.05630 |  |

## Test, trascrizione GC

| test | osservato | p | nota |
|---|---|---|---|
| A1 f49v-f66r | – | – | troppo poco |
| A1 f49v-f57v | 0.0 | 1.00000 |  |
| A1 f66r-f57v | 1.0 | 0.92640 |  |
| A2 f49v | 0.421053 | 0.00150 | ritardo 7 |
| A2 f66r | 0.178571 | 0.10659 | ritardo 5 |
| A2 f57v | 0.571429 | 0.00005 | ritardo 17 |
| B1 f49v dopo | 1.0 | 0.64387 |  |
| B1 f49v prima | 1.0 | 0.56232 |  |
| B1 f76r dopo | 1.0 | 0.57317 |  |
| B1 f76r prima | 0.0 | 1.00000 |  |
| B2 f49v | 0.350416 | 0.00005 |  |
| B2 f66r | 0.077829 | 0.00375 |  |
| B2 f76r | -0.088425 | 0.15269 |  |

## Confermati (p <= soglia in ZL e in IT o GC, parte ammessa)

- A1 f49v-f66r: no
- A1 f49v-f57v: no
- A1 f66r-f57v: no
- A2 f49v: no
- A2 f66r: no
- A2 f57v: confermato
- B1 f49v dopo: no
- B1 f49v prima: no
- B1 f76r dopo: no
- B1 f76r prima: no
- B2 f49v: confermato
- B2 f66r: confermato
- B2 f76r: no

**Lettura:** nessuna delle due; composizione dei segni come quella dei segni che aprono le righe (B2).
