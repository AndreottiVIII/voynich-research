# e409 — Il messaggio nel sacco

Corpo di partenza: v17. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83164 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.563 (0.516, 0.537, 0.564, 0.557, 0.593, 0.530, 0.598, 0.598, 0.568, 0.568, 0.530, 0.593) | 0.601 (0.580, 0.577, 0.595, 0.597, 0.617, 0.577, 0.630, 0.629, 0.621, 0.605, 0.568, 0.615) | 0.551 | 15.0/18 | 5.8/8 | 11/4 | 0.7629 | 0.0399 | 0.49 | 0.54 | 0.60 | 0.57 | 0.52 | 0.52 | 0.56 | 0.66 | 0.49 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.521 | -0.004 | 1.009 | 5.000 | 0.223 |

## Materie mancate (su 4 chiavi)

**a.** omogeneità (12), gradiente (12), profilo pagina (12), scelte di riga (12), dispersione delle lunghezze (9), prime righe come registro (5), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.59 | 0.2235 | 0.2328 |
| G3 uniche nel testo | -1.58 | 0.1453 | 0.1540 |
| G1 p | +1.28 | 0.0076 | 0.0078 |
| G8 k prime righe meno altre | +1.19 | -0.0233 | -0.0132 |
| G1 cph | -1.09 | 0.0018 | 0.0014 |
| G2 l+ch | +1.07 | 0.0038 | 0.0058 |
| G8 t prime righe meno altre | +1.06 | -0.0001 | 0.0101 |
| G4 unioni attestate | -1.04 | 0.0919 | 0.0867 |

