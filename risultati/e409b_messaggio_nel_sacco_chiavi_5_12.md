# e409 — Il messaggio nel sacco

Corpo di partenza: v9. Isidoro XVII (38240 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 8 su 8; chiave sbagliata respinta: 8 su 8.
- Capacità del libro: 80157 bit con il messaggio, 79989 con soli bit di riempimento (servono 38240); pagine usate dal messaggio 131 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.560 (0.575, 0.547, 0.556, 0.521, 0.558, 0.550, 0.617, 0.557) | 0.675 (0.688, 0.694, 0.665, 0.653, 0.652, 0.655, 0.719, 0.674) | 0.560 | 16.6/18 | 3.9/8 | 0/4 | 0.7586 | 0.0448 | 0.49 | 0.52 | 0.65 | 0.56 | 0.47 | 0.62 | 0.58 | 0.66 | 0.69 |
| b | stesso canale, soli bit di riempimento | 0.559 (0.569, 0.558, 0.547, 0.551, 0.570, 0.550, 0.567, 0.562) | 0.680 (0.684, 0.684, 0.678, 0.643, 0.656, 0.663, 0.700, 0.729) | 0.545 | 16.5/18 | 4.0/8 | 0/4 | 0.7573 | 0.0455 | 0.49 | 0.50 | 0.65 | 0.59 | 0.50 | 0.62 | 0.60 | 0.67 | 0.68 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 1.072 | 0.016 | 0.964 | 1.375 | 0.099 |
| b | 1.069 | 0.025 | 0.963 | 1.500 | 0.095 |

## Materie mancate (su 4 chiavi)

**a.** profilo pagina (8), scelte di riga (8), concordanza delle desinenze (8), dispersione delle lunghezze (7), prime righe come registro (7), gradiente (3), coppie viste altrove (3).

**b.** profilo pagina (8), scelte di riga (8), concordanza delle desinenze (8), dispersione delle lunghezze (6), prime righe come registro (5), gradiente (4), coppie viste altrove (4), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.26 | 0.0503 | 0.0365 |
| G9 JSD pagina-manoscritto | +1.84 | 0.0402 | 0.0446 |
| G6 coppie viste altrove | +1.60 | 0.2213 | 0.2420 |
| G6 somiglianza a distanza 2 | -1.51 | 0.2198 | 0.2093 |
| G2 y+o | +1.29 | 0.0004 | 0.0010 |
| G8 k prime righe meno altre | +1.27 | -0.0236 | -0.0087 |
| G3 tipi su parole | +1.27 | 0.7559 | 0.7596 |
| G3 fra le 100 piu frequenti | +1.15 | 0.4244 | 0.4376 |

**b**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.31 | 0.0503 | 0.0367 |
| G6 coppie viste altrove | +2.09 | 0.2213 | 0.2408 |
| G9 JSD pagina-manoscritto | +1.61 | 0.0402 | 0.0445 |
| G6 somiglianza a distanza 2 | -1.51 | 0.2198 | 0.2100 |
| G3 fra le 100 piu frequenti | +1.49 | 0.4244 | 0.4365 |
| G2 cth+o | -1.30 | 0.0039 | 0.0030 |
| G3 tipi su parole | +1.23 | 0.7559 | 0.7590 |
| G2 o+t | -1.20 | 0.0264 | 0.0263 |

