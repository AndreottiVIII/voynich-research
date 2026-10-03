# e251 — Passo 2 del piano 18/18 sopra l'e241: lessico di sezione

Generatore dell'e241 con γ (base presa, con questa probabilità, dalle forme non attestate già scritte nelle pagine precedenti della stessa sezione). γ scelto sul seme 1 fra [0.1, 0.2, 0.3, 0.45, 0.6]: **0.10**. Preregistrazione: `preregistrazioni/e251.md` (integrazione del 3/10/2026).

## Validità

| controllo | esito |
|---|---|
| V1 replica dell'e241 sul seme 2 (16/18, ripetizione e verticale, AUC 0,862) | sì (16/18, ripetizione, verticale, AUC 0.8620) |
| V2 γ 0 identico all'e241 (grezzo, dopo) | sì, sì |
| V3 meccanismo attivo (ricircolo γ 0 → γ*) | sì (0.054 → 0.179) |
| V4 coerenza con l'e276 | disponibile: True, seme 7: True, seme 8: True, seme 9: True |
| R delle parole rare del Voynich (atteso 1,96) | 1.958 (C 0.0100, atteso 0.0051, rare 697) |

## Scelta sul seme 1

| γ | pagella | riga | R parole rare | ricircolo |
|---|---|---|---|---|
| 0.00 | 14/18 | sì | 44.4 | 0.054 |
| 0.10 | 11/18 | sì | 43.6 | 0.179 |
| 0.20 | 11/18 | no | 27.3 | 0.302 |
| 0.30 | 7/18 | no | 28.2 | 0.420 |
| 0.45 | 7/18 | no | 22.8 | 0.471 |
| 0.60 | 7/18 | no | 19.4 | 0.551 |

P* 14; ammessi []; scelto γ* 0.10.

## Verifica (semi 7, 8, 9)

| seme | braccio | pagella | riga | mancano | R rare | C | atteso | rare | confinate | AUC e231 | AUC e266 | R | V | F | A | N | ripetizioni |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | e241 | 15/18 | sì | ripetizione, profilo pagina, verticale | 48.5 | 0.2384 | 0.0049 | 881 | 210 | 0.887 | 0.966 | 38.7% | 35.0% | 5.8% | 8.1% | 12.4% | 2.26% |
| 7 | γ 0.10 | 11/18 | sì | h2, spazio, ripetizione, omogeneità, curva piatta, profilo pagina, verticale | 34.1 | 0.1687 | 0.0049 | 996 | 168 | 0.943 | 0.974 | 35.6% | 34.2% | 5.9% | 9.9% | 14.4% | 1.98% |
| 8 | e241 | 15/18 | no | spazio, ripetizione, verticale | 51.5 | 0.2537 | 0.0049 | 875 | 222 | 0.854 | 0.953 | 38.3% | 35.6% | 5.9% | 8.0% | 12.2% | 2.22% |
| 8 | γ 0.10 | 12/18 | no | h2, spazio, ripetizione, curva piatta, profilo pagina, verticale | 33.5 | 0.1720 | 0.0051 | 936 | 161 | 0.926 | 0.978 | 35.9% | 34.1% | 5.9% | 9.9% | 14.2% | 1.99% |
| 9 | e241 | 15/18 | sì | spazio, ripetizione, verticale | 44.8 | 0.2223 | 0.0050 | 877 | 195 | 0.879 | 0.965 | 38.9% | 35.1% | 5.9% | 8.1% | 12.1% | 2.15% |
| 9 | γ 0.10 | 11/18 | sì | h2, spazio, ripetizione, omogeneità, curva piatta, profilo pagina, verticale | 34.7 | 0.1667 | 0.0048 | 930 | 155 | 0.915 | 0.966 | 36.1% | 34.4% | 5.8% | 9.5% | 14.2% | 1.97% |

| seme | proprietà guadagnate | proprietà perse |
|---|---|---|
| 7 | — | curva piatta, h2, omogeneità, spazio |
| 8 | — | curva piatta, h2, profilo pagina |
| 9 | — | curva piatta, h2, omogeneità, profilo pagina |

## Diagnosi (semi 7, 8, 9)

| seme | braccio | ricircolo | dopo | inizio riga | forme nuove | proprie della pagina vera | altre attestate | quota non attestate | nuove > 5 (erbario) | massimo | lessico H occ. | lessico H tipi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | e241 | 0.046 | 2 | 2 | 60 | 76 | 70 | 0.141 | 4 | 7 | 1725 | 1487 |
| 7 | γ 0.10 | 0.203 | 3 | 0 | 60 | 48 | 57 | 0.204 | 15 | 30 | 2318 | 1700 |
| 8 | e241 | 0.048 | 2 | 0 | 87 | 68 | 65 | 0.145 | 4 | 8 | 1727 | 1461 |
| 8 | γ 0.10 | 0.193 | 2 | 0 | 56 | 47 | 56 | 0.202 | 26 | 16 | 2319 | 1670 |
| 9 | e241 | 0.047 | 2 | 0 | 59 | 60 | 74 | 0.143 | 1 | 6 | 1605 | 1417 |
| 9 | γ 0.10 | 0.189 | 3 | 0 | 58 | 46 | 48 | 0.192 | 22 | 17 | 2322 | 1744 |

Medie: e241 pagella 15.00 (somma 45), riga in 2 semi, R rare 48.3, AUC e231 0.873, e266 0.961; γ* pagella 11.33 (somma 34), riga in 2 semi, R rare 34.1, AUC e231 0.928, e266 0.973.

Caratteristiche più pesanti dell'e231 (seme 7, γ*; positivo = più nel generatore):

| caratteristica | coefficiente | Voynich | generatore |
|---|---|---|---|
| G3 lunghezza deviazione | +1.95 | 1.5790 | 1.7556 |
| G3 uniche nel testo | -1.44 | 0.1461 | 0.1353 |
| G3 tipi su parole | -1.16 | 0.7559 | 0.7056 |
| G3 fra le 100 piu frequenti | -0.99 | 0.4244 | 0.3800 |
| G2 a+r | -0.96 | 0.0210 | 0.0157 |
| G3 uniche nella pagina | -0.94 | 0.6359 | 0.5734 |
| G2 p+sh | +0.90 | 0.0006 | 0.0017 |
| G4 somiglianza fra vicine | -0.82 | 0.2181 | 0.1983 |
| G2 a+m | +0.68 | 0.0057 | 0.0098 |
| G2 y+d | +0.66 | 0.0021 | 0.0042 |

Esito: **non superato: R + pagella**.
