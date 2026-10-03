# e409 — Il messaggio nel sacco

Corpo di partenza: v10. Isidoro XVII (38240 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 80216 bit con il messaggio, nan con soli bit di riempimento (servono 38240); pagine usate dal messaggio 131 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.572 (0.582, 0.577, 0.543, 0.578, 0.592, 0.586, 0.585, 0.550, 0.549, 0.536, 0.609, 0.576) | 0.690 (0.711, 0.707, 0.667, 0.712, 0.681, 0.684, 0.687, 0.666, 0.675, 0.663, 0.724, 0.701) | 0.562 | 16.7/18 | 4.1/8 | 0/4 | 0.7586 | 0.0447 | 0.50 | 0.52 | 0.65 | 0.58 | 0.51 | 0.62 | 0.59 | 0.67 | 0.69 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 1.065 | 0.009 | 0.976 | 1.167 | 0.100 |

## Materie mancate (su 4 chiavi)

**a.** profilo pagina (12), scelte di riga (12), concordanza delle desinenze (11), dispersione delle lunghezze (9), prime righe come registro (8), coppie viste altrove (7), gradiente (3), ripetizione (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.58 | 0.0503 | 0.0348 |
| G9 JSD pagina-manoscritto | +2.35 | 0.0402 | 0.0453 |
| G6 coppie viste altrove | +1.67 | 0.2213 | 0.2409 |
| G3 lunghezza media | +1.21 | 4.2913 | 4.3454 |
| G3 fra le 100 piu frequenti | +1.17 | 0.4244 | 0.4356 |
| G1 j | -1.08 | 0.0001 | 0.0000 |
| G2 s+o | -1.08 | 0.0033 | 0.0031 |
| G1 u | -1.06 | 0.0001 | 0.0000 |

