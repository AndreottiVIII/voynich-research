# e47 — Da dove viene il vocabolario aperto del Voynich

Parole uniche (quota dei tipi che compaiono una volta) in finestre contigue di n parole, media sulle finestre. Ricambio: quota delle parole di un blocco di 1.000 il cui tipo compare in un blocco a distanza k. Preregistrazione: `preregistrazioni/e47.md`.

| testo | n = 1000 | n = 2000 | n = 5000 | n = 10000 | n = 20000 | n = 34000 | in comune k=1 | k=5 | k=20 |
|---|---|---|---|---|---|---|---|---|---|
| Voynich | 0.74 | 0.71 | 0.70 | 0.69 | 0.68 | 0.68 | 0.57 | 0.51 | 0.47 |
| Voynich, Currier A | 0.75 | 0.73 | 0.70 | 0.69 | — | — | 0.57 | 0.49 | — |
| Voynich, Currier B | 0.72 | 0.71 | 0.69 | 0.68 | 0.68 | — | 0.60 | 0.56 | 0.49 |
| Timm e Schinner + giunture, seme 19 | 0.63 | 0.60 | 0.56 | 0.53 | 0.51 | 0.50 | 0.59 | 0.57 | 0.56 |
| Timm e Schinner + giunture, seme 1 | 0.64 | 0.61 | 0.57 | 0.54 | 0.52 | 0.51 | 0.56 | 0.54 | 0.54 |
| Timm e Schinner + giunture, seme 2 | 0.63 | 0.60 | 0.57 | 0.54 | 0.52 | 0.52 | 0.55 | 0.54 | 0.53 |
| Bibbia latina | 0.72 | 0.69 | 0.65 | 0.62 | 0.56 | 0.50 | 0.54 | 0.50 | 0.50 |
| Plinio, libri 20-27 | 0.81 | 0.77 | 0.73 | 0.71 | 0.67 | 0.65 | 0.41 | 0.36 | 0.36 |

Divario di parole uniche, Voynich − generatore (media dei tre semi): n=1000: +0.103, n=2000: +0.110, n=5000: +0.133, n=10000: +0.152, n=20000: +0.165, n=34000: +0.168. Rapporto fra il divario a n = 1000 e quello a n = 34000: 0.61 → esito preregistrato: **misto**.
