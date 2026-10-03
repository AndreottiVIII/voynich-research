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
| v3 | 7 | esatta | 17/18 | sì | 0/8 | 0.850 | 0.947 |
| v3 | 8 | esatta | 17/18 | sì | 0/8 | 0.804 | 0.933 |
| v3 | 9 | esatta | 18/18 | no | 0/8 | 0.798 | 0.923 |
| v4 | 7 | esatta | 17/18 | no | 3/8 | 0.839 | 0.927 |
| v4 | 8 | esatta | 17/18 | no | 3/8 | 0.834 | 0.927 |
| v4 | 9 | esatta | 16/18 | no | 3/8 | 0.855 | 0.940 |
| v5 | 7 | esatta | 17/18 | no | 2/8 | 0.830 | 0.935 |
| v5 | 8 | esatta | 15/18 | no | 3/8 | 0.842 | 0.923 |
| v5 | 9 | esatta | 17/18 | no | 3/8 | 0.778 | 0.893 |

| versione | pagella (3 semi) | pagella estesa (3 semi) | riga | AUC e231 | AUC e266 | materie aggiunte mancate |
|---|---|---|---|---|---|---|
| v3 | 52/54 | 52/78 | 2 | 0.817 | 0.934 | parole rare per pagina (3), tipi su parole nella pagina (3), uniche nella pagina (3), dispersione delle lunghezze (3), prime righe come registro (3), scelte di riga (3), concordanza delle desinenze (3), coppie viste altrove (3) |
| v4 | 50/54 | 59/78 | 0 | 0.843 | 0.931 | parole rare per pagina (3), tipi su parole nella pagina (3), uniche nella pagina (3), dispersione delle lunghezze (3), prime righe come registro (3) |
| v5 | 49/54 | 57/78 | 0 | 0.816 | 0.917 | parole rare per pagina (3), tipi su parole nella pagina (3), uniche nella pagina (3), dispersione delle lunghezze (3), prime righe come registro (3), scelte di riga (1) |
