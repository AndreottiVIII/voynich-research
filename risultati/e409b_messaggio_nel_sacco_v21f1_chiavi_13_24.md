# e409 — Il messaggio nel sacco

Corpo di partenza: v21f1. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83715 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.554 (0.526, 0.577, 0.563, 0.549, 0.525, 0.559, 0.564, 0.569, 0.539, 0.551, 0.571, 0.561) | 0.606 (0.574, 0.604, 0.609, 0.607, 0.574, 0.609, 0.629, 0.627, 0.591, 0.588, 0.630, 0.632) | 0.543 | 15.9/18 | 5.2/8 | 12/4 | 0.7622 | 0.0392 | 0.52 | 0.53 | 0.61 | 0.59 | 0.48 | 0.54 | 0.57 | 0.60 | 0.49 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.525 | 0.008 | 1.032 | 4.750 | 0.188 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), dispersione delle lunghezze (11), prime righe come registro (9), omogeneità (1), coppie viste altrove (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.54 | 0.2238 | 0.2359 |
| G3 uniche nel testo | -1.36 | 0.1459 | 0.1516 |
| G3 tipi su parole | +1.26 | 0.7532 | 0.7593 |
| G2 d+y | -1.03 | 0.0435 | 0.0414 |
| G8 p prime righe meno altre | -0.91 | 0.0334 | 0.0255 |
| G1 t | +0.91 | 0.0352 | 0.0345 |
| G7 lunghezza ultima parola | +0.86 | 4.2981 | 4.4321 |
| G1 y | -0.84 | 0.1046 | 0.0976 |

