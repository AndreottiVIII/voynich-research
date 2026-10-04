# e409 — Il messaggio nel sacco

Corpo di partenza: v15. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 82491 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 129 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.570 (0.604, 0.554, 0.574, 0.558, 0.546, 0.562, 0.563, 0.583, 0.560, 0.551, 0.596, 0.588) | 0.601 (0.644, 0.601, 0.599, 0.597, 0.585, 0.589, 0.585, 0.590, 0.586, 0.619, 0.610, 0.605) | 0.555 | 15.2/18 | 5.9/8 | 9/4 | 0.7704 | 0.0403 | 0.50 | 0.53 | 0.62 | 0.59 | 0.53 | 0.52 | 0.56 | 0.65 | 0.51 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.520 | 0.016 | 1.003 | 5.000 | 0.215 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), omogeneità (9), prime righe come registro (8), dispersione delle lunghezze (5).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +2.30 | 0.2213 | 0.2351 |
| G2 i+k | +1.37 | 0.0003 | 0.0003 |
| G3 uniche nel testo | -1.36 | 0.1461 | 0.1481 |
| G2 k+h | -1.14 | 0.0005 | 0.0003 |
| G2 r+ch | +1.14 | 0.0009 | 0.0022 |
| G2 l+ch | +1.14 | 0.0037 | 0.0058 |
| G2 d+y | -1.06 | 0.0432 | 0.0405 |
| G8 t prime righe meno altre | +1.04 | 0.0002 | 0.0104 |

