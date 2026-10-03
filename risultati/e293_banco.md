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
| v2 | 7 | esatta | 17/18 | sì | 0/8 | 0.845 | 0.948 |
| v2 | 8 | esatta | 17/18 | sì | 0/8 | 0.846 | 0.949 |
| v2 | 9 | esatta | 18/18 | no | 0/8 | 0.835 | 0.939 |
| v3 | 7 | esatta | 17/18 | sì | 0/8 | 0.850 | 0.947 |
| v3 | 8 | esatta | 17/18 | sì | 0/8 | 0.804 | 0.933 |
| v3 | 9 | esatta | 18/18 | no | 0/8 | 0.798 | 0.923 |

| versione | pagella (3 semi) | pagella estesa (3 semi) | riga | AUC e231 | AUC e266 | materie aggiunte mancate |
|---|---|---|---|---|---|---|
| v2 | 52/54 | 52/78 | 2 | 0.842 | 0.945 | parole rare per pagina (3), tipi su parole nella pagina (3), uniche nella pagina (3), dispersione delle lunghezze (3), prime righe come registro (3), scelte di riga (3), concordanza delle desinenze (3), coppie viste altrove (3) |
| v3 | 52/54 | 52/78 | 2 | 0.817 | 0.934 | parole rare per pagina (3), tipi su parole nella pagina (3), uniche nella pagina (3), dispersione delle lunghezze (3), prime righe come registro (3), scelte di riga (3), concordanza delle desinenze (3), coppie viste altrove (3) |
