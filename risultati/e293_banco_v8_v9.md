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
| v8 | 7 | esatta | 14/18 | no | 4/8 | 0.640 | 0.753 |
| v8 | 8 | esatta | 13/18 | no | 5/8 | 0.553 | 0.653 |
| v8 | 9 | esatta | 14/18 | no | 6/8 | 0.620 | 0.739 |
| v9 | 7 | esatta | 15/18 | no | 4/8 | 0.654 | 0.733 |
| v9 | 8 | esatta | 14/18 | no | 4/8 | 0.681 | 0.729 |
| v9 | 9 | esatta | 15/18 | no | 4/8 | 0.670 | 0.695 |

| versione | pagella (3 semi) | pagella estesa (3 semi) | riga | AUC e231 | AUC e266 | materie aggiunte mancate |
|---|---|---|---|---|---|---|
| v8 | 41/54 | 56/78 | 0 | 0.604 | 0.715 | dispersione delle lunghezze (1), prime righe come registro (3), scelte di riga (3), concordanza delle desinenze (2) |
| v9 | 44/54 | 56/78 | 0 | 0.668 | 0.719 | dispersione delle lunghezze (2), prime righe come registro (3), scelte di riga (3), concordanza delle desinenze (3), parole rare per pagina (1) |
