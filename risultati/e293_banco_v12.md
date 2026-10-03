# e293 — Pagella estesa e banco di prova del voynichizzatore

Testo nascosto: Isidoro XVII (inizio), chiave "banco"; corpi con i semi 7, 8, 9. Pagella estesa = 18 materie dell'e224 + 8 (su 8) con il metro valido. Preregistrazione: `preregistrazioni/e293.md`.

| materia aggiunta | Voynich | fascia | metro valido |
|---|---|---|---|
| parole rare per pagina | 1.9580 | R ≤ 5 | sì |
| tipi su parole nella pagina | 0.7559 | ±0.03 | sì |
| uniche nella pagina | 0.6359 | ±0.04 | sì |
| dispersione delle lunghezze | 1.5790 | ±0.04 | sì |
| prime righe come registro | 4.7243 | z > 3 | sì |
| scelte di riga | 12 | ≥ 10 su 12 | sì |
| concordanza delle desinenze | 0.0433 | ±0.012 | sì |
| coppie viste altrove | 0.2213 | ±0.02 | sì |

| versione | seme | decodifica | pagella | riga | materie aggiunte passate | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|---|
| v12 | 7 | esatta | 15/18 | no | 5/8 | 0.567 | 0.626 |
| v12 | 8 | esatta | 15/18 | sì | 6/8 | 0.552 | 0.601 |
| v12 | 9 | esatta | 15/18 | sì | 6/8 | 0.518 | 0.572 |

| versione | pagella (3 semi) | pagella estesa (3 semi) | riga | AUC e231 | AUC e266 | materie aggiunte mancate |
|---|---|---|---|---|---|---|
| v12 | 45/54 | 62/78 | 2 | 0.546 | 0.600 | prime righe come registro (2), scelte di riga (3), coppie viste altrove (1), dispersione delle lunghezze (1) |
