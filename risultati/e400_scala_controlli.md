# e400 — La scala dei controlli

Testi fatti dal Voynich vero, con l'impaginazione vera e un solo livello rotto; semi 1–4 (medie). Preregistrazione: `preregistrazioni/e400.md`.

Controlli del metro: V AUC 0,5: sì; L4 AUC >= 0,95: sì; N1 decodifica: sì.

| gradino | che cosa | AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V | il Voynich tale e quale | 0.500 | 0.500 (0.500–0.500) | — | 17.0/18 | 8.0/8 | 1/1 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 |
| O1 | righe rimescolate nella pagina | 0.481 | 0.595 (0.588–0.604) | 0.50–0.58 | 17.0/18 | 7.0/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.50 | 0.48 | 0.50 | 0.50 | 0.50 | 0.62 |
| O2 | parole rimescolate dentro la riga | 0.984 | 0.990 (0.984–0.993) | 0.60–0.72 | 11.5/18 | 6.0/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.98 | 0.52 | 0.66 | 0.93 | 0.50 | 0.50 |
| O3 | parole rimescolate nella pagina, prime righe e altre separate | 0.988 | 0.993 (0.990–0.997) | 0.75–0.85 | 12.0/18 | 4.8/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.99 | 0.54 | 0.70 | 0.94 | 0.50 | 0.65 |
| O4 | parole rimescolate in tutta la pagina | 0.989 | 0.998 (0.996–0.999) | 0.80–0.90 | 11.2/18 | 4.0/8 | 0/4 | 0.50 | 0.50 | 0.50 | 0.99 | 0.54 | 0.72 | 0.94 | 0.96 | 0.66 |
| L1 | parole ripescate dalla pagina con reimmissione | 1.000 | 1.000 (1.000–1.000) | 0.88–0.95 | 9.5/18 | 1.0/8 | 0/4 | 0.50 | 0.52 | 1.00 | 0.99 | 0.54 | 0.73 | 0.93 | 0.96 | 0.77 |
| L2 | parole dalle due pagine prima e dalle due dopo | 0.997 | 1.000 (0.999–1.000) | 0.90–0.97 | 7.5/18 | 1.0/8 | 0/4 | 0.41 | 0.32 | 0.98 | 0.99 | 0.54 | 0.78 | 0.94 | 0.96 | 0.67 |
| L3 | parole dalle altre pagine della stessa sezione e lingua | 0.998 | 1.000 (1.000–1.000) | 0.95–0.99 | 6.2/18 | 4.0/8 | 0/4 | 0.40 | 0.31 | 0.98 | 0.99 | 0.54 | 0.82 | 0.94 | 0.96 | 0.75 |
| L4 | parole dalle altre pagine del libro | 1.000 | 1.000 (1.000–1.000) | 0.98–1.00 | 5.0/18 | 1.0/8 | 0/4 | 0.66 | 0.48 | 0.99 | 1.00 | 0.52 | 0.86 | 0.96 | 0.96 | 0.96 |
| N1 | Voynich con Isidoro nascosto nelle cinque scelte di grafia | 0.622 | 0.630 (0.620–0.643) | 0.50–0.60 | 16.0/18 | 7.2/8 | 1/4 | 0.52 | 0.61 | 0.54 | 0.55 | 0.51 | 0.55 | 0.53 | 0.56 | 0.54 |

## Perché: materie perse e caratteristiche più pesanti per gradino (giudice e266, primo seme)

**O1 — righe rimescolate nella pagina.** Materie mancate in almeno un seme: gradiente, prime righe come registro.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G9 JSD prima-seconda meta | -2.33 | 0.0503 | 0.0381 |
| G3 uniche nella pagina | +0.70 | 0.6359 | 0.6359 |
| G3 tipi su parole | +0.56 | 0.7559 | 0.7559 |
| G2 o+y | +0.50 | 0.0017 | 0.0017 |
| G2 s+ch | -0.42 | 0.0009 | 0.0009 |
| G2 t+ch | +0.41 | 0.0119 | 0.0119 |

**O2 — parole rimescolate dentro la riga.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, formule, gradiente, legame, lunghezze vicine, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G4 inizio p | -1.44 | 0.0769 | 0.0086 |
| G4 unioni attestate | -1.30 | 0.0916 | 0.0559 |
| G4 inizio ch | +1.22 | 0.0355 | 0.1673 |
| G7 lunghezza prima parola | -1.05 | 4.8197 | 4.3428 |
| G4 inizio t | -1.01 | 0.1052 | 0.0328 |
| G7 ultime in m | -0.95 | 0.1392 | 0.0293 |

**O3 — parole rimescolate nella pagina, prime righe e altre separate.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, formule, legame, lunghezze vicine, prime righe come registro, scelte di riga, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G4 inizio ch | +1.36 | 0.0355 | 0.1801 |
| G4 unioni attestate | -1.34 | 0.0916 | 0.0514 |
| G7 lunghezza prima parola | -1.08 | 4.8197 | 4.2737 |
| G4 inizio t | -1.06 | 0.1052 | 0.0281 |
| G4 inizio p | -1.04 | 0.0769 | 0.0127 |
| G4 fine o | +1.00 | 0.0123 | 0.0481 |

**O4 — parole rimescolate in tutta la pagina.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, formule, legame, lunghezze vicine, omogeneità, prime righe come registro, scelte di riga, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G4 unioni attestate | -1.19 | 0.0916 | 0.0485 |
| G8 p prime righe meno altre | -1.15 | 0.0331 | 0.0002 |
| G4 inizio ch | +0.97 | 0.0355 | 0.1688 |
| G7 lunghezza prima parola | -0.88 | 4.8197 | 4.2798 |
| G8 f prime righe meno altre | -0.84 | 0.0103 | -0.0002 |
| G4 inizio p | -0.76 | 0.0769 | 0.0110 |

**L1 — parole ripescate dalla pagina con reimmissione.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, formule, legame, lunghezze vicine, omogeneità, parole rare per pagina, prime righe come registro, scelte di riga, tipi, tipi su parole nella pagina, uniche, uniche nella pagina, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G3 uniche nella pagina | -1.15 | 0.6359 | 0.2605 |
| G3 tipi su parole | -1.00 | 0.7559 | 0.5140 |
| G4 unioni attestate | -0.90 | 0.0916 | 0.0378 |
| G3 uniche nel testo | -0.80 | 0.1461 | 0.0628 |
| G8 p prime righe meno altre | -0.75 | 0.0331 | 0.0002 |
| G4 inizio ch | +0.61 | 0.0355 | 0.1704 |

**L2 — parole dalle due pagine prima e dalle due dopo.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, curva piatta, formule, gradiente, legame, lunghezze vicine, omogeneità, parole rare per pagina, prime righe come registro, scelte di riga, tipi, tipi su parole nella pagina, uniche, uniche nella pagina, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G3 uniche nel testo | -1.09 | 0.1461 | 0.0613 |
| G4 unioni attestate | -1.06 | 0.0916 | 0.0371 |
| G8 p prime righe meno altre | -0.99 | 0.0331 | -0.0004 |
| G4 inizio ch | +0.79 | 0.0355 | 0.1697 |
| G6 coppie viste altrove | -0.65 | 0.2213 | 0.1623 |
| G7 lunghezza prima parola | -0.61 | 4.8197 | 4.2640 |

**L3 — parole dalle altre pagine della stessa sezione e lingua.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, curva piatta, formule, gradiente, legame, lunghezze vicine, omogeneità, prime righe come registro, profilo pagina, scelte di riga, tipi, uniche, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G3 uniche nel testo | -1.08 | 0.1461 | 0.0625 |
| G4 unioni attestate | -0.95 | 0.0916 | 0.0375 |
| G8 p prime righe meno altre | -0.93 | 0.0331 | 0.0002 |
| G9 JSD pagina-manoscritto | -0.64 | 0.0402 | 0.0218 |
| G4 inizio t | -0.63 | 0.1052 | 0.0311 |
| G4 inizio ch | +0.56 | 0.0355 | 0.1829 |

**L4 — parole dalle altre pagine del libro.** Materie mancate in almeno un seme: bordo di riga, concordanza delle desinenze, coppie viste altrove, curva piatta, deriva, dispersione delle lunghezze, formule, gradiente, legame, lunghezze vicine, omogeneità, prime righe come registro, profilo pagina, scelte di riga, tipi, tipi su parole nella pagina, uniche, uniche nella pagina, unioni, verticale.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G3 uniche nel testo | -0.70 | 0.1461 | 0.0608 |
| G4 unioni attestate | -0.67 | 0.0916 | 0.0328 |
| G8 p prime righe meno altre | -0.66 | 0.0331 | -0.0004 |
| G6 somiglianza a distanza 2 | -0.61 | 0.2198 | 0.1795 |
| G9 JSD pagina-manoscritto | -0.58 | 0.0402 | 0.0093 |
| G4 inizio p | -0.56 | 0.0769 | 0.0110 |

**N1 — Voynich con Isidoro nascosto nelle cinque scelte di grafia.** Materie mancate in almeno un seme: coppie viste altrove, gradiente, legame, prime righe come registro.

| caratteristica | coefficiente | Voynich | controllo |
|---|---|---|---|
| G6 coppie viste altrove | -1.50 | 0.2213 | 0.2052 |
| G3 lunghezza media | -1.35 | 4.2913 | 4.2989 |
| G2 l+sh | -1.33 | 0.0016 | 0.0010 |
| G1 l | +1.10 | 0.0560 | 0.0574 |
| G9 JSD pagina-manoscritto | -1.05 | 0.0402 | 0.0374 |
| G2 p+sh | +0.94 | 0.0006 | 0.0012 |

N1: decodifica esatta sì; parole cambiate dal nascondiglio 51.7%.
