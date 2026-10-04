# e409 — Il messaggio nel sacco

Corpo di partenza: v20. Isidoro XVII (38304 bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.

- Andata e ritorno esatta: 12 su 12; chiave sbagliata respinta: 12 su 12.
- Capacità del libro: 83164 bit con il messaggio, nan con soli bit di riempimento (servono 38304); pagine usate dal messaggio 128 su 207.


| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich 0.7559) | JSD (Voynich 0.0402) | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | messaggio nel sacco | 0.554 (0.525, 0.527, 0.578, 0.547, 0.574, 0.517, 0.569, 0.590, 0.544, 0.551, 0.548, 0.579) | 0.599 (0.588, 0.601, 0.595, 0.592, 0.617, 0.570, 0.611, 0.610, 0.620, 0.607, 0.565, 0.611) | 0.551 | 15.6/18 | 5.4/8 | 12/4 | 0.7629 | 0.0399 | 0.49 | 0.54 | 0.60 | 0.56 | 0.51 | 0.53 | 0.56 | 0.62 | 0.49 |

Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):

| caso | S1 | R_riga | A | scelte_per_riga | r_righe_consecutive |
|---|---|---|---|---|---|
| a | 0.509 | 0.006 | 1.034 | 5.000 | 0.226 |

## Materie mancate (su 4 chiavi)

**a.** gradiente (12), profilo pagina (12), scelte di riga (12), dispersione delle lunghezze (9), prime righe come registro (9), omogeneità (4), ripetizione (1), parole rare per pagina (1).

## Caratteristiche più pesanti (giudice e266, prima chiave)

**a**

| caratteristica | coefficiente | Voynich | testo |
|---|---|---|---|
| G6 coppie viste altrove | +1.59 | 0.2235 | 0.2363 |
| G4 unioni attestate | -1.26 | 0.0919 | 0.0844 |
| G2 l+ch | +1.23 | 0.0038 | 0.0058 |
| G2 d+y | -1.17 | 0.0440 | 0.0410 |
| G2 r+ch | +1.12 | 0.0009 | 0.0019 |
| G4 inizio t | -1.10 | 0.1072 | 0.0952 |
| G3 uniche nel testo | -1.08 | 0.1453 | 0.1540 |
| G1 cph | -0.99 | 0.0018 | 0.0014 |

