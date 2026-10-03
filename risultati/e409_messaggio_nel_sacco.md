# e409 — Il messaggio nel sacco

Corpo di partenza: v9. Isidoro XVII (38240 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 4 su 4; chiave sbagliata respinta: 4 su 4.
- Capacità del libro: 80333 bit con il messaggio, 80516 con soli bit di riempimento (servono 38240); pagine usate dal messaggio 131 su 207.
- Nascondiglio vecchio (c): decodifica esatta 4 su 4.

| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.560 (0.578, 0.559, 0.551, 0.552) | 0.697 (0.730, 0.702, 0.684, 0.671) | 0.566 | 16.2/18 | 4.0/8 | 0/4 | 0.7585 | 0.0445 | 0.50 | 0.52 | 0.64 | 0.58 | 0.51 | 0.61 | 0.58 | 0.65 | 0.69 |
| b | stesso canale, soli bit di riempimento | 0.523 (0.478, 0.527, 0.528, 0.560) | 0.655 (0.606, 0.654, 0.657, 0.704) | 0.529 | 16.0/18 | 3.8/8 | 0/4 | 0.7573 | 0.0445 | 0.47 | 0.49 | 0.63 | 0.56 | 0.45 | 0.63 | 0.56 | 0.67 | 0.67 |
| c | nascondiglio vecchio sul corpo della versione di partenza | 0.677 (0.658, 0.696, 0.671, 0.680) | 0.737 (0.740, 0.729, 0.725, 0.755) | 0.641 | 15.0/18 | 3.8/8 | 0/4 | 0.7651 | 0.0421 | 0.52 | 0.64 | 0.64 | 0.60 | 0.49 | 0.58 | 0.57 | 0.69 | 0.62 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 1.101 | 0.008 | 0.966 | 0.750 | 0.093 |
| b | 1.086 | 0.014 | 0.957 | 1.750 | 0.101 |
| c | 1.037 | -0.009 | 0.974 | 5.000 | 0.166 |

## Materie mancate (su 4 chiavi)

**a.** profilo pagina (4), scelte di riga (4), concordanza delle desinenze (4), gradiente (3), coppie viste altrove (3), prime righe come registro (3), dispersione delle lunghezze (2).

**b.** gradiente (4), profilo pagina (4), scelte di riga (4), concordanza delle desinenze (4), prime righe come registro (3), dispersione delle lunghezze (3), coppie viste altrove (3).

**c.** gradiente (4), legame (4), profilo pagina (4), prime righe come registro (4), scelte di riga (4), concordanza delle desinenze (4), dispersione delle lunghezze (3), parole rare per pagina (2).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +2.45 | 0.2213 | 0.2434 |
| G9 JSD prima-seconda meta | -2.42 | 0.0503 | 0.0353 |
| G9 JSD pagina-manoscritto | +2.17 | 0.0402 | 0.0453 |
| G6 somiglianza a distanza 2 | -1.47 | 0.2198 | 0.2106 |
| G2 s+o | -1.44 | 0.0033 | 0.0031 |
| G1 j | -1.34 | 0.0001 | 0.0000 |
| G4 inizio s | +1.07 | 0.0804 | 0.1101 |
| G3 lunghezza media | +1.00 | 4.2913 | 4.3454 |

**b**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.33 | 0.0503 | 0.0355 |
| G6 somiglianza a distanza 2 | -2.16 | 0.2198 | 0.2107 |
| G9 JSD pagina-manoscritto | +2.01 | 0.0402 | 0.0456 |
| G6 coppie viste altrove | +1.73 | 0.2213 | 0.2401 |
| G3 tipi su parole | +1.27 | 0.7559 | 0.7536 |
| G3 fra le 100 piu frequenti | +1.10 | 0.4244 | 0.4390 |
| G3 lunghezza media | +1.06 | 4.2913 | 4.3547 |
| G2 y+t | -0.98 | 0.0061 | 0.0052 |

**c**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.39 | 0.0503 | 0.0367 |
| G6 somiglianza a distanza 2 | -1.81 | 0.2198 | 0.2028 |
| G4 unioni attestate | -1.26 | 0.0916 | 0.0838 |
| G2 p+sh | +1.20 | 0.0006 | 0.0009 |
| G2 sh+d | +1.16 | 0.0011 | 0.0017 |
| G2 y+o | +1.16 | 0.0004 | 0.0009 |
| G1 l | +1.10 | 0.0560 | 0.0613 |
| G8 k prime righe meno altre | +1.09 | -0.0236 | -0.0073 |

