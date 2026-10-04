# e409 — Il messaggio nel sacco

Corpo di partenza: v19. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83164 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.551 (0.513, 0.551, 0.556, 0.545, 0.575, 0.524, 0.551, 0.553, 0.562, 0.568, 0.556, 0.562) | 0.596 (0.596, 0.606, 0.597, 0.601, 0.607, 0.541, 0.634, 0.614, 0.606, 0.598, 0.576, 0.581) | 0.552 | 15.8/18 | 5.5/8 | 4/4 | 0.7629 | 0.0399 | 0.49 | 0.54 | 0.60 | 0.55 | 0.52 | 0.55 | 0.57 | 0.62 | 0.47 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.524 | -0.004 | 0.999 | 5.000 | 0.221 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (11), dispersione delle lunghezze (9), prime righe come registro (9), omogeneità (2), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.84 | 0.2235 | 0.2341 |
| G8 p prime righe meno altre | -1.74 | 0.0332 | 0.0264 |
| G3 uniche nel testo | -1.41 | 0.1453 | 0.1540 |
| G2 l+ch | +1.38 | 0.0038 | 0.0058 |
| G4 unioni attestate | -1.35 | 0.0919 | 0.0876 |
| G1 p | +1.30 | 0.0076 | 0.0078 |
| G4 inizio ch | +1.13 | 0.0318 | 0.0424 |
| G8 k prime righe meno altre | +1.10 | -0.0233 | -0.0127 |

