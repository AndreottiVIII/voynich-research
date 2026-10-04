# e409 — Il messaggio nel sacco

Corpo di partenza: v16. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 82403 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 129 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.564 (0.602, 0.520, 0.554, 0.569, 0.566, 0.568, 0.574, 0.578, 0.516, 0.556, 0.583, 0.577) | 0.598 (0.651, 0.547, 0.596, 0.609, 0.620, 0.596, 0.589, 0.636, 0.544, 0.583, 0.593, 0.606) | 0.545 | 15.3/18 | 6.0/8 | 8/4 | 0.7688 | 0.0402 | 0.50 | 0.53 | 0.61 | 0.58 | 0.53 | 0.52 | 0.56 | 0.66 | 0.50 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.529 | 0.006 | 1.008 | 5.000 | 0.218 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), omogeneità (8), prime righe come registro (6), dispersione delle lunghezze (6).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +2.13 | 0.2219 | 0.2324 |
| G2 r+ch | +1.73 | 0.0009 | 0.0025 |
| G4 unioni attestate | -1.43 | 0.0908 | 0.0866 |
| G3 uniche nel testo | -1.36 | 0.1460 | 0.1518 |
| G2 d+y | -1.12 | 0.0433 | 0.0400 |
| G2 o+k | -1.04 | 0.0402 | 0.0379 |
| G2 r+o | +0.98 | 0.0023 | 0.0039 |
| G2 l+ch | +0.97 | 0.0036 | 0.0057 |

