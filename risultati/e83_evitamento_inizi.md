# e83 — L'evitamento fra inizi di riga: verifiche di robustezza

S = quota di coppie di righe (distanza k, stesso paragrafo) con lo stesso primo segno, divisa per l'attesa (500 rimescolamenti delle righe nella pagina). Preregistrazione: `preregistrazioni/e83.md`.

| prova | coppie | osservata | attesa | S | z |
|---|---|---|---|---|---|
| ZL, k=1 | 2622 | 0.085 | 0.164 | 0.52 | -11.8 |
| IT, k=1 | 2580 | 0.085 | 0.164 | 0.52 | -11.4 |
| GC, k=1 (primo carattere) | 2525 | 0.078 | 0.155 | 0.50 | -12.3 |
| ZL lingua A, k=1 | 1076 | 0.055 | 0.151 | 0.36 | -10.0 |
| ZL lingua B, k=1 | 1505 | 0.107 | 0.174 | 0.62 | -7.5 |
| ZL erbario (H), k=1 | 1103 | 0.057 | 0.149 | 0.38 | -9.7 |
| ZL biologia (B), k=1 | 570 | 0.093 | 0.182 | 0.51 | -6.1 |
| ZL ricette (S), k=1 | 569 | 0.130 | 0.182 | 0.71 | -3.3 |
| ZL altre sezioni, k=1 | 380 | 0.084 | 0.151 | 0.56 | -4.1 |
| ZL, k=2 | 1961 | 0.195 | 0.163 | 1.20 | 4.3 |
| ZL, k=3 | 1468 | 0.170 | 0.161 | 1.05 | 0.9 |
| ZL, k=1, senza segno aggiunto | 2622 | 0.103 | 0.144 | 0.71 | -6.7 |
| ZL, k=1, parola intera | 2622 | 0.006 | 0.010 | 0.59 | -2.1 |
