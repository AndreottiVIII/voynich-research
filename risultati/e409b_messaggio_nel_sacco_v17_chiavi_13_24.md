# e409 — Il messaggio nel sacco

Corpo di partenza: v17. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83715 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.556 (0.527, 0.575, 0.537, 0.561, 0.545, 0.571, 0.551, 0.559, 0.567, 0.549, 0.550, 0.578) | 0.593 (0.560, 0.601, 0.555, 0.590, 0.588, 0.598, 0.594, 0.604, 0.613, 0.602, 0.576, 0.632) | 0.543 | 15.1/18 | 5.2/8 | 7/4 | 0.7622 | 0.0392 | 0.52 | 0.53 | 0.61 | 0.57 | 0.52 | 0.52 | 0.56 | 0.65 | 0.49 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.503 | 0.013 | 1.006 | 5.000 | 0.223 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), omogeneità (11), dispersione delle lunghezze (11), scelte di riga (11), prime righe come registro (10), parole rare per pagina (1), coppie viste altrove (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 uniche nel testo | -1.56 | 0.1459 | 0.1516 |
| G2 r+ch | +1.21 | 0.0010 | 0.0017 |
| G2 d+y | -1.17 | 0.0435 | 0.0414 |
| G2 e+y | -1.15 | 0.0270 | 0.0249 |
| G8 p prime righe meno altre | -1.08 | 0.0334 | 0.0251 |
| G2 l+a | +1.05 | 0.0018 | 0.0028 |
| G1 t | +0.99 | 0.0352 | 0.0345 |
| G2 l+d | +0.98 | 0.0044 | 0.0046 |

