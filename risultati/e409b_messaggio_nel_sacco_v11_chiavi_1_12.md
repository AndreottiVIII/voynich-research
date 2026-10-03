# e409 — Il messaggio nel sacco

Corpo di partenza: v11. Isidoro XVII (38240 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 80216 bit con il messaggio, nan con soli bit di riempimento (servono 38240); pagine usate dal messaggio 131 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.579 (0.590, 0.561, 0.566, 0.585, 0.571, 0.571, 0.584, 0.553, 0.598, 0.557, 0.618, 0.591) | 0.634 (0.640, 0.615, 0.620, 0.628, 0.596, 0.625, 0.631, 0.612, 0.655, 0.650, 0.687, 0.653) | 0.562 | 14.9/18 | 4.5/8 | 9/4 | 0.7586 | 0.0447 | 0.50 | 0.52 | 0.65 | 0.58 | 0.51 | 0.57 | 0.57 | 0.66 | 0.62 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.576 | 0.015 | 1.008 | 5.000 | 0.219 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), omogeneità (11), coppie viste altrove (11), dispersione delle lunghezze (9), prime righe come registro (5), concordanza delle desinenze (5), formule (2).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.71 | 0.2213 | 0.2427 |
| G2 s+o | -1.54 | 0.0033 | 0.0031 |
| G9 JSD pagina-manoscritto | +1.46 | 0.0402 | 0.0453 |
| G3 lunghezza media | +1.35 | 4.2913 | 4.3454 |
| G1 p | +1.28 | 0.0075 | 0.0073 |
| G1 j | -1.13 | 0.0001 | 0.0000 |
| G3 tipi su parole | +1.13 | 0.7559 | 0.7591 |
| G4 inizio ch | +1.12 | 0.0355 | 0.0517 |

