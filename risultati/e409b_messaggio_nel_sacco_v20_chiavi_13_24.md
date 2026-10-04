# e409 — Il messaggio nel sacco

Corpo di partenza: v20. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83715 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.567 (0.545, 0.566, 0.551, 0.554, 0.554, 0.600, 0.554, 0.561, 0.566, 0.614, 0.579, 0.556) | 0.615 (0.607, 0.612, 0.598, 0.593, 0.577, 0.627, 0.613, 0.600, 0.622, 0.689, 0.634, 0.603) | 0.543 | 15.8/18 | 5.6/8 | 12/4 | 0.7622 | 0.0392 | 0.52 | 0.53 | 0.61 | 0.58 | 0.51 | 0.52 | 0.57 | 0.62 | 0.49 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.522 | 0.003 | 1.032 | 5.000 | 0.224 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), dispersione delle lunghezze (11), prime righe come registro (6), omogeneità (2).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.43 | 0.2238 | 0.2377 |
| G3 uniche nel testo | -1.27 | 0.1459 | 0.1516 |
| G3 tipi su parole | +1.13 | 0.7532 | 0.7593 |
| G8 p prime righe meno altre | -1.11 | 0.0334 | 0.0245 |
| G8 lunghezza parole prime righe | -1.10 | 4.6492 | 4.5948 |
| G2 d+y | -1.08 | 0.0435 | 0.0414 |
| G6 somiglianza a distanza 2 | +1.05 | 0.2201 | 0.2263 |
| G4 unioni attestate | -1.03 | 0.0921 | 0.0874 |

