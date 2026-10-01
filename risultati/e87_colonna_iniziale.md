# e87 — La colonna delle prime parole è una sequenza con giunture?

R = eccesso di verosimiglianza delle coppie verticali (ultimo segno della parola in posizione p della riga L → primo segno della parola in posizione p della riga L+1) sotto il modello delle giunture dentro la riga, diviso per quello delle coppie dentro la riga. Preregistrazione: `preregistrazioni/e87.md`.

| testo | prima parola: coppie | R (z) | seconda parola: coppie | R (z) |
|---|---|---|---|---|
| Voynich | 2622 | -0.02 (-0.7) | 2609 | -0.00 (-0.0) |
| Voynich A | 1076 | -0.12 (-2.0) | 1078 | -0.12 (-1.7) |
| Voynich B | 1505 | 0.01 (0.3) | 1495 | 0.04 (0.9) |
| controllo positivo: colonna = testo continuo | 1800 | 0.73 (31.2) | 1800 | 0.00 (0.2) |
| controllo negativo: Manusmṛti | 1800 | 0.02 (0.8) | 1800 | 0.00 (0.2) |
| Timm e Schinner, seme 19 | 3210 | 0.27 (3.8) | 3210 | 0.02 (0.2) |
