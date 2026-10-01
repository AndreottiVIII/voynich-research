# e75 — La riga ha colonne?

Eccesso d'informazione mutua (bit) fra caratteristica delle parole interne e classe di posizione relativa (4 classi), contro 200 rimescolamenti dentro la riga; z fra parentesi. Righe di almeno 6 parole. Preregistrazione: `preregistrazioni/e75.md`.

| testo | righe | primo segno | ultimo segno | lunghezza | tipo |
|---|---|---|---|---|---|
| Voynich | 2671 | 0.0129 (z 31.4) | 0.0020 (z 4.7) | 0.0004 (z 1.9) | 0.0117 (z 12.5) |
| Voynich A | 890 | 0.0229 (z 16.6) | 0.0050 (z 4.0) | -0.0002 (z -0.2) | 0.0136 (z 4.2) |
| Voynich B | 1747 | 0.0101 (z 18.4) | 0.0041 (z 7.6) | 0.0004 (z 1.1) | 0.0115 (z 8.8) |
| Plinio, a capo | 3328 | 0.0010 (z 2.6) | -0.0002 (z -0.5) | -0.0001 (z -0.8) | 0.0009 (z 1.2) |
| Plinio codificato, a capo | 3327 | 0.0001 (z 0.2) | 0.0003 (z 0.8) | 0.0000 (z 0.2) | 0.0009 (z 1.1) |
| Naibbe, a capo | 3281 | 0.0005 (z 1.5) | -0.0000 (z -0.1) | 0.0000 (z 0.0) | -0.0006 (z -0.8) |
| controllo: interne ordinate per lunghezza (metà righe) | 3327 | 0.0288 (z 82.1) | 0.0170 (z 44.7) | 0.1643 (z 904.3) | 0.0657 (z 96.1) |
| Timm e Schinner, seme 19 | 3204 | 0.0007 (z 2.1) | 0.0006 (z 2.4) | 0.0001 (z 0.4) | 0.0000 (z 0.0) |
| Timm e Schinner, seme 1 | 3266 | -0.0001 (z -0.2) | 0.0001 (z 0.6) | 0.0000 (z 0.1) | 0.0005 (z 0.8) |
| Timm e Schinner, seme 2 | 3240 | -0.0005 (z -1.7) | 0.0003 (z 1.4) | 0.0000 (z 0.2) | 0.0003 (z 0.4) |
| + giunture (e23), seme 19 | 3188 | 0.0003 (z 0.9) | 0.0003 (z 1.3) | 0.0002 (z 0.8) | 0.0005 (z 0.6) |
| modello e51, seme 19 | 3162 | 0.0006 (z 1.6) | 0.0006 (z 2.1) | 0.0011 (z 3.2) | 0.0002 (z 0.2) |

Valori più sbilanciati (frequenza nell'ultima classe / nella prima):

- **Voynich**: primo: inizio [('sh', 0.46), ('q', 0.81), ('k', 0.88)], fine [('d', 1.79), ('t', 1.74), ('cth', 1.46)]; ultimo: inizio [('o', 0.75), ('y', 0.9), ('l', 0.92)], fine [('m', 2.47), ('r', 1.21), ('n', 1.15)]; lunghezza: inizio [('7', 0.91), ('6', 0.91), ('3', 0.95)], fine [('4', 1.06), ('5', 1.06), ('1', 1.06)]
- **Voynich A**: primo: inizio [('sh', 0.46), ('k', 0.67), ('q', 0.69)], fine [('d', 2.05), ('s', 1.54), ('cth', 1.42)]; ultimo: inizio [('o', 0.78), ('l', 0.83), ('r', 0.9)], fine [('n', 1.34), ('s', 1.2), ('y', 1.0)]; lunghezza: inizio [('2', 0.92), ('7', 0.93), ('3', 0.96)], fine [('5', 1.13), ('1', 1.04), ('6', 1.03)]
- **Voynich B**: primo: inizio [('sh', 0.47), ('q', 0.82), ('y', 0.89)], fine [('t', 1.7), ('d', 1.58), ('r', 1.49)]; ultimo: inizio [('o', 0.73), ('y', 0.87), ('d', 0.89)], fine [('r', 1.4), ('n', 1.1), ('s', 1.08)]; lunghezza: inizio [('6', 0.88), ('7', 0.88), ('3', 0.95)], fine [('1', 1.17), ('2', 1.1), ('4', 1.09)]
- **Plinio, a capo**: primo: inizio [('d', 0.78), ('p', 0.87), ('i', 0.9)], fine [('h', 1.25), ('o', 1.24), ('u', 1.15)]; ultimo: inizio [('x', 0.87), ('n', 0.88), ('r', 0.9)], fine [('c', 1.19), ('d', 1.15), ('o', 1.14)]; lunghezza: inizio [('1', 0.92), ('6', 0.95), ('7', 0.97)], fine [('5', 1.09), ('2', 1.02), ('4', 1.02)]
- **Plinio codificato, a capo**: primo: inizio [('r', 0.84), ('k', 0.88), ('sh', 0.88)], fine [('f', 1.33), ('s', 1.13), ('ch', 1.06)]; ultimo: inizio [('d', 0.89), ('y', 0.97), ('l', 1.0)], fine [('g', 1.16), ('o', 1.07), ('s', 1.07)]; lunghezza: inizio [('4', 0.96), ('6', 0.97), ('5', 0.99)], fine [('2', 1.1), ('1', 1.07), ('3', 1.07)]
- **Naibbe, a capo**: primo: inizio [('q', 0.91), ('d', 0.93), ('cth', 0.93)], fine [('r', 1.27), ('p', 1.18), ('a', 1.13)]; ultimo: inizio [('d', 0.9), ('y', 0.98), ('o', 0.98)], fine [('m', 1.13), ('s', 1.08), ('n', 1.05)]; lunghezza: inizio [('6', 0.94), ('3', 0.98), ('7', 0.99)], fine [('2', 1.05), ('4', 1.05), ('5', 1.02)]
- **controllo: interne ordinate per lunghezza (metà righe)**: primo: inizio [('cth', 0.38), ('a', 0.45), ('ch', 0.68)], fine [('q', 2.65), ('p', 2.04), ('y', 1.87)]; ultimo: inizio [('o', 0.5), ('l', 0.61), ('d', 0.78)], fine [('n', 1.89), ('y', 1.14), ('m', 0.95)]; lunghezza: inizio [('1', 0.24), ('2', 0.26), ('3', 0.29)], fine [('7', 4.89), ('6', 2.57), ('5', 1.24)]
- **Timm e Schinner, seme 19**: primo: inizio [('e', 0.77), ('k', 0.84), ('t', 0.89)], fine [('s', 1.5), ('p', 1.31), ('ckh', 1.08)]; ultimo: inizio [('s', 0.89), ('l', 0.93), ('r', 0.94)], fine [('m', 1.1), ('n', 1.1), ('y', 1.09)]; lunghezza: inizio [('6', 0.83), ('7', 0.97), ('5', 1.0)], fine [('3', 1.08), ('2', 1.03), ('4', 1.02)]
- **Timm e Schinner, seme 1**: primo: inizio [('e', 0.87), ('ch', 0.9), ('d', 0.96)], fine [('s', 1.39), ('p', 1.36), ('k', 1.16)]; ultimo: inizio [('l', 0.91), ('d', 0.98), ('r', 1.0)], fine [('m', 1.24), ('s', 1.18), ('o', 1.11)]; lunghezza: inizio [('7', 0.89), ('6', 0.92), ('5', 0.96)], fine [('1', 1.29), ('3', 1.05), ('2', 1.04)]
- **Timm e Schinner, seme 2**: primo: inizio [('k', 0.82), ('ch', 0.94), ('t', 0.97)], fine [('e', 1.42), ('q', 1.09), ('p', 1.05)]; ultimo: inizio [('d', 0.94), ('r', 0.94), ('n', 0.96)], fine [('o', 1.21), ('y', 1.06), ('s', 1.02)]; lunghezza: inizio [('4', 0.94), ('6', 0.95), ('7', 0.99)], fine [('1', 1.14), ('2', 1.08), ('3', 1.02)]
- **+ giunture (e23), seme 19**: primo: inizio [('q', 0.76), ('s', 0.77), ('o', 0.95)], fine [('e', 1.51), ('k', 1.1), ('sh', 1.09)]; ultimo: inizio [('s', 0.84), ('l', 0.94), ('d', 0.95)], fine [('o', 1.17), ('y', 1.08), ('n', 1.04)]; lunghezza: inizio [('7', 0.93), ('6', 0.94), ('4', 0.95)], fine [('3', 1.07), ('1', 1.06), ('5', 1.03)]
- **modello e51, seme 19**: primo: inizio [('e', 0.75), ('k', 0.79), ('sh', 0.94)], fine [('cth', 1.57), ('s', 1.15), ('a', 1.11)]; ultimo: inizio [('s', 0.82), ('r', 0.9), ('m', 0.96)], fine [('d', 1.13), ('o', 1.11), ('l', 1.04)]; lunghezza: inizio [('6', 0.84), ('7', 0.86), ('5', 1.0)], fine [('1', 1.48), ('2', 1.11), ('3', 1.11)]
