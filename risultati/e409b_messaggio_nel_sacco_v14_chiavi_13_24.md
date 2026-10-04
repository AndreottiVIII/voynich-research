# e409 — Il messaggio nel sacco

Corpo di partenza: v14. Isidoro XVII (38240 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 82283 bit con il messaggio, nan con soli bit di riempimento (servono 38240); pagine usate dal messaggio 129 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.584 (0.622, 0.593, 0.594, 0.596, 0.614, 0.556, 0.572, 0.552, 0.555, 0.601, 0.572, 0.577) | 0.609 (0.628, 0.631, 0.607, 0.595, 0.630, 0.591, 0.616, 0.589, 0.597, 0.624, 0.602, 0.596) | 0.565 | 15.2/18 | 5.8/8 | 10/4 | 0.7700 | 0.0400 | 0.50 | 0.55 | 0.62 | 0.59 | 0.52 | 0.52 | 0.57 | 0.65 | 0.51 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.513 | 0.006 | 1.008 | 5.000 | 0.217 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), omogeneità (10), prime righe come registro (7), dispersione delle lunghezze (7).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G2 l+ch | +1.56 | 0.0037 | 0.0056 |
| G4 inizio s | +1.35 | 0.0804 | 0.1139 |
| G2 l+sh | +1.16 | 0.0016 | 0.0028 |
| G2 ch+e | -1.14 | 0.0319 | 0.0295 |
| G2 s+o | -1.14 | 0.0033 | 0.0030 |
| G6 coppie viste altrove | +1.13 | 0.2213 | 0.2311 |
| G2 e+ckh | +1.04 | 0.0007 | 0.0010 |
| G3 tipi su parole | +1.03 | 0.7559 | 0.7673 |

