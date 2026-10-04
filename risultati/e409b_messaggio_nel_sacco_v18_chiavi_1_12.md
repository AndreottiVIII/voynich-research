# e409 — Il messaggio nel sacco

Corpo di partenza: v18. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83164 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.559 (0.515, 0.537, 0.558, 0.599, 0.576, 0.531, 0.567, 0.596, 0.573, 0.537, 0.554, 0.558) | 0.597 (0.573, 0.585, 0.599, 0.642, 0.595, 0.552, 0.601, 0.645, 0.601, 0.578, 0.581, 0.612) | 0.551 | 15.6/18 | 5.6/8 | 8/4 | 0.7629 | 0.0399 | 0.49 | 0.54 | 0.60 | 0.56 | 0.52 | 0.53 | 0.55 | 0.62 | 0.48 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.510 | 0.022 | 1.002 | 5.000 | 0.218 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), dispersione delle lunghezze (9), prime righe come registro (7), omogeneità (4), verticale (1), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G4 unioni attestate | -2.20 | 0.0919 | 0.0802 |
| G6 coppie viste altrove | +1.67 | 0.2235 | 0.2289 |
| G3 uniche nel testo | -1.40 | 0.1453 | 0.1540 |
| G8 p prime righe meno altre | -1.35 | 0.0332 | 0.0269 |
| G1 p | +1.28 | 0.0076 | 0.0078 |
| G2 l+ch | +1.21 | 0.0038 | 0.0058 |
| G1 cph | -1.19 | 0.0018 | 0.0014 |
| G3 lunghezza deviazione | +0.97 | 1.5819 | 1.6221 |

