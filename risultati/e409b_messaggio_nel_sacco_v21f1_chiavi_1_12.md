# e409 — Il messaggio nel sacco

Corpo di partenza: v21f1. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83164 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.554 (0.517, 0.553, 0.555, 0.550, 0.579, 0.526, 0.570, 0.580, 0.553, 0.567, 0.531, 0.568) | 0.596 (0.551, 0.630, 0.595, 0.596, 0.614, 0.555, 0.613, 0.627, 0.597, 0.617, 0.557, 0.603) | 0.552 | 16.0/18 | 5.5/8 | 12/4 | 0.7629 | 0.0399 | 0.49 | 0.54 | 0.60 | 0.56 | 0.54 | 0.53 | 0.56 | 0.62 | 0.47 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.505 | 0.007 | 1.025 | 5.000 | 0.192 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (11), dispersione delle lunghezze (9), prime righe come registro (9), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G3 uniche nel testo | -1.54 | 0.1453 | 0.1540 |
| G1 p | +1.47 | 0.0076 | 0.0078 |
| G2 l+ch | +1.22 | 0.0038 | 0.0058 |
| G8 t prime righe meno altre | +1.12 | -0.0001 | 0.0114 |
| G4 unioni attestate | -1.07 | 0.0919 | 0.0824 |
| G3 lunghezza media | +1.02 | 4.3027 | 4.3662 |
| G8 lunghezza parole prime righe | -0.95 | 4.6479 | 4.6034 |
| G2 d+y | -0.94 | 0.0440 | 0.0410 |

