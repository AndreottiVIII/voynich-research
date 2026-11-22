# ia30 — gli interventi causali dentro un imitatore

Solo numeri e aggregati. Effetti in bit (piu' alto = l'intervento fa perdere piu' previsione). Vale per l'IMITATORE; per il Voynich e' un indizio indiretto.

## Taratura delle regole piantate

| regola | probabilita' | misura ottenuta | bersaglio (vero) |
|---|---|---|---|
| contatto | 0.1297 | 0.1843 | 0.1884 |
| eco | 0.0247 | 0.1220 | 0.1138 |
| bordi inizio | 0.9766 | 0.1966 | 0.2024 |
| bordi fine | 1.0000 | 0.0810 | 0.0911 |

## Modello M1: mappa "intervento -> tratto"

10 modelli, 207 pagine. Per ogni cella: effetto (intervallo al 95%), rapporto con l'ancora, etichetta; "V" = coppia validata dal controllo positivo.

| intervento | punti | kl_primo | eco_sopra | eco_riga | term | pc |
|---|---|---|---|---|---|---|
| fill | 2484 | 2.0249 [1.9439, 2.1300] r=3.74 **causale** | 0.0160 [-0.0715, 0.1154] r=— **non leggibile** | -0.1991 [-0.2839, -0.1044] r=— **non leggibile** | -0.2797 [-0.3035, -0.2626] r=-0.12 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| hN | 1242 | 0.0758 [0.0703, 0.0820] r=1.00 **causale** | -0.1523 [-0.2395, -0.0419] r=— **non leggibile** | 0.0747 [-0.0227, 0.1809] r=— **non leggibile** | 2.3450 [2.0984, 2.6511] r=1.00 **causale** V | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| hR | 1242 | 0.0665 [0.0624, 0.0711] r=0.88 **causale** | -0.0081 [-0.0251, 0.0064] r=— **non leggibile** | -0.0017 [-0.0175, 0.0133] r=— **non leggibile** | 0.0049 [-0.0246, 0.0306] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| hT | 1242 | 0.8807 [0.8128, 0.9507] r=11.62 **causale** | -0.0629 [-0.1245, -0.0108] r=— **non leggibile** | -0.1301 [-0.1716, -0.0889] r=— **non leggibile** | -0.0946 [-0.1323, -0.0667] r=-0.04 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| lfill | 1242 | 2.2866 [2.2051, 2.3788] r=30.18 **causale** | -0.1947 [-0.2617, -0.1288] r=— **non leggibile** | -0.4394 [-0.4781, -0.4057] r=— **non leggibile** | 0.1443 [0.0676, 0.2158] r=0.06 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| lnul | 1242 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| nul | 2484 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| p1 | 2158 | 0.0964 [0.0898, 0.1031] r=0.17 **non causale** V | -0.0013 [-0.0259, 0.0247] r=— **non leggibile** | 0.0112 [-0.0154, 0.0329] r=— **non leggibile** | -0.0034 [-0.0187, 0.0102] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| p2 | 1666 | 0.1551 [0.1479, 0.1640] r=0.27 **non causale** V | 0.0154 [-0.0238, 0.0476] r=— **non leggibile** | 0.0212 [-0.0133, 0.0516] r=— **non leggibile** | -0.0127 [-0.0278, 0.0004] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| p3 | 1182 | 0.0967 [0.0909, 0.1038] r=0.18 **non causale** V | 0.0069 [-0.0289, 0.0444] r=— **non leggibile** | 0.0124 [-0.0202, 0.0434] r=— **non leggibile** | -0.0330 [-0.0487, -0.0168] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| pm | 689 | 0.0730 [0.0666, 0.0795] r=0.15 **non causale** V | -0.0027 [-0.0396, 0.0485] r=— **non leggibile** | 0.0123 [-0.0269, 0.0557] r=— **non leggibile** | -0.0275 [-0.0502, -0.0041] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| pw | 2484 | 0.5413 [0.5176, 0.5669] r=1.00 **causale** V | -0.0157 [-0.0645, 0.0531] r=— **non leggibile** | -0.0014 [-0.0486, 0.0467] r=— **non leggibile** | -0.0300 [-0.0494, -0.0116] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| rc | 1690 | 0.0260 [0.0241, 0.0279] r=0.05 **non causale** V | -0.0156 [-0.0413, 0.0147] r=— **non leggibile** | 0.0163 [-0.0091, 0.0463] r=— **non leggibile** | -0.0348 [-0.0558, -0.0133] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| rl | 1026 | 0.0024 [0.0020, 0.0028] r=0.03 **non causale** | 0.0010 [-0.0092, 0.0106] r=— **non leggibile** x | -0.0048 [-0.0156, 0.0050] r=— **non leggibile** | 0.0044 [-0.0034, 0.0123] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| rs_a | 1242 | 0.1132 [0.1077, 0.1186] r=1.49 **causale** | 0.0218 [-0.0006, 0.0483] r=— **non leggibile** x | -0.0035 [-0.0303, 0.0237] r=— **non leggibile** | 0.0095 [-0.0286, 0.0444] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| rs_m | 1237 | 0.0718 [0.0676, 0.0755] r=0.95 **causale** | -0.0126 [-0.0314, 0.0018] r=— **non leggibile** x | 0.0110 [-0.0036, 0.0261] r=— **non leggibile** | -0.0237 [-0.0409, -0.0097] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| rs_p | 1228 | 0.1025 [0.0969, 0.1086] r=1.35 **causale** | 0.0209 [0.0007, 0.0505] r=— **non leggibile** x | 0.0287 [0.0086, 0.0477] r=— **non leggibile** | -0.0337 [-0.0615, -0.0017] r=-0.01 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| u1 | 1734 | 0.4578 [0.4400, 0.4770] r=0.79 **causale** V | 0.0114 [-0.0328, 0.0679] r=— **non leggibile** | -0.0218 [-0.0729, 0.0225] r=— **non leggibile** | -0.0073 [-0.0215, 0.0096] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| u2 | 2188 | 0.4559 [0.4359, 0.4764] r=0.81 **causale** V | 0.0150 [-0.0296, 0.0674] r=— **non leggibile** | 0.0175 [-0.0303, 0.0594] r=— **non leggibile** | -0.0087 [-0.0233, 0.0086] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| w2 | 1812 | 0.0386 [0.0362, 0.0410] r=0.07 **non causale** V | 0.0207 [-0.0061, 0.0547] r=— **non leggibile** | 0.0303 [0.0028, 0.0615] r=— **non leggibile** | -0.0403 [-0.0605, -0.0191] r=-0.02 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |

Testa di pagina (sezione hS, mano hM, lingua hL): perdita media per fascia di distanza dall'inizio (parole 0-9, 10-39, 40-99, 100+)

- hL: perdita 0.0918, 0.0321, 0.0305, 0.0142; KL del primo glifo 0.0201, 0.0079, 0.0048, 0.0003
- hM: perdita 0.1487, 0.0652, 0.0527, 0.0766; KL del primo glifo 0.0232, 0.0075, 0.0050, 0.0046
- hS: perdita 0.2158, 0.1285, 0.0786, 0.1236; KL del primo glifo 0.0442, 0.0189, 0.0142, 0.0160

Scambio parziale di stati (f0 = quota del cambio del primo glifo che passa; fw = quota del cambio delle parole): media sui modelli

- **pw**: tutto f0 1.000 fw 1.000; solo secondo strato f0 1.000 fw 0.764; solo primo strato f0 0.000 fw 0.215; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.02 (a caso 0.00); 4: 0.03 (a caso 0.01); 8: 0.06 (a caso 0.02); 16: 0.12 (a caso 0.06); 32: 0.24 (a caso 0.11); 64: 0.47 (a caso 0.23); 128: 0.81 (a caso 0.49)
- **rs_a**: tutto f0 1.000 fw 1.000; solo secondo strato f0 1.000 fw 0.797; solo primo strato f0 0.000 fw 0.188; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.00 (a caso 0.00); 2: 0.01 (a caso 0.01); 4: 0.02 (a caso 0.01); 8: 0.05 (a caso 0.03); 16: 0.10 (a caso 0.07); 32: 0.22 (a caso 0.12); 64: 0.43 (a caso 0.26); 128: 0.78 (a caso 0.51)
- **u2**: tutto f0 1.000 fw 1.000; solo secondo strato f0 1.000 fw 0.751; solo primo strato f0 0.000 fw 0.231; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.02 (a caso 0.01); 4: 0.04 (a caso 0.02); 8: 0.06 (a caso 0.03); 16: 0.12 (a caso 0.06); 32: 0.27 (a caso 0.11); 64: 0.48 (a caso 0.25); 128: 0.82 (a caso 0.48)

## Modello E2: mappa "intervento -> tratto"

10 modelli, 207 pagine. Per ogni cella: effetto (intervallo al 95%), rapporto con l'ancora, etichetta; "V" = coppia validata dal controllo positivo.

| intervento | punti | kl_primo | eco_sopra | eco_riga | term | pc |
|---|---|---|---|---|---|---|
| fill | 2484 | 2.4860 [2.3910, 2.5913] r=4.17 **causale** | -0.1958 [-0.2915, -0.0950] r=-0.76 **non causale** | -0.3302 [-0.4097, -0.2431] r=— **non leggibile** | -0.2348 [-0.2701, -0.2089] r=-0.11 **non causale** | 0.0042 [0.0036, 0.0050] r=— **non leggibile** |
| hN | 1242 | 0.0961 [0.0891, 0.1044] r=1.00 **causale** | -0.1890 [-0.2861, -0.0895] r=-0.73 **non causale** | 0.0433 [-0.0722, 0.1651] r=0.70 **zona grigia** | 2.2302 [1.9562, 2.5280] r=1.00 **causale** V | 0.0012 [0.0005, 0.0019] r=— **non leggibile** |
| hR | 1242 | 0.0624 [0.0572, 0.0665] r=0.65 **causale** | -0.0037 [-0.0201, 0.0099] r=-0.01 **non causale** | -0.0050 [-0.0201, 0.0081] r=-0.08 **non causale** | -0.0224 [-0.0467, -0.0022] r=-0.01 **non causale** | 0.0000 [-0.0001, 0.0001] r=— **non leggibile** |
| hT | 1242 | 0.9237 [0.8536, 0.9953] r=9.61 **causale** | -0.0715 [-0.1259, -0.0118] r=-0.28 **non causale** | -0.1830 [-0.2210, -0.1395] r=-2.98 **non causale** | -0.0881 [-0.1189, -0.0587] r=-0.04 **non causale** | 0.0037 [0.0030, 0.0046] r=— **non leggibile** |
| lfill | 1242 | 2.1632 [2.0516, 2.2705] r=22.51 **causale** | -0.1450 [-0.2135, -0.0691] r=-0.56 **non causale** | -0.4205 [-0.4628, -0.3786] r=-6.85 **non causale** | 0.2189 [0.1193, 0.3228] r=0.10 **non causale** | 0.0011 [0.0008, 0.0015] r=— **non leggibile** |
| lnul | 1242 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| nul | 2484 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| p1 | 2120 | 0.1030 [0.0960, 0.1094] r=0.17 **non causale** V | -0.0070 [-0.0357, 0.0176] r=-0.03 **non causale** | 0.0091 [-0.0107, 0.0289] r=— **non leggibile** | -0.0169 [-0.0321, 0.0002] r=-0.01 **non causale** | 0.0009 [0.0006, 0.0012] r=— **non leggibile** |
| p2 | 1636 | 0.1873 [0.1737, 0.2007] r=0.29 **non causale** x | -0.0181 [-0.0613, 0.0242] r=-0.07 **non causale** | 0.0095 [-0.0299, 0.0473] r=— **non leggibile** | -0.0125 [-0.0269, 0.0051] r=-0.01 **non causale** | 0.0008 [0.0004, 0.0012] r=— **non leggibile** |
| p3 | 1176 | 0.0969 [0.0889, 0.1035] r=0.17 **non causale** V | 0.0437 [0.0009, 0.0894] r=0.17 **non causale** | 0.0229 [-0.0107, 0.0560] r=— **non leggibile** | -0.0252 [-0.0430, -0.0067] r=-0.01 **non causale** | 0.0010 [0.0006, 0.0015] r=— **non leggibile** |
| pm | 705 | 0.0770 [0.0701, 0.0843] r=0.16 **non causale** V | 0.0488 [0.0045, 0.1011] r=0.19 **non causale** | 0.0130 [-0.0212, 0.0533] r=— **non leggibile** | -0.0389 [-0.0636, -0.0175] r=-0.02 **non causale** | 0.0014 [0.0007, 0.0021] r=— **non leggibile** |
| pw | 2484 | 0.5964 [0.5698, 0.6184] r=1.00 **causale** V | -0.0031 [-0.0596, 0.0445] r=-0.01 **non causale** | -0.0073 [-0.0609, 0.0356] r=— **non leggibile** | -0.0487 [-0.0712, -0.0269] r=-0.02 **non causale** | 0.0017 [0.0012, 0.0024] r=— **non leggibile** |
| rc | 1736 | 0.0260 [0.0239, 0.0280] r=0.04 **non causale** V | 0.0098 [-0.0160, 0.0330] r=0.04 **non causale** | 0.0096 [-0.0164, 0.0357] r=— **non leggibile** | -0.0237 [-0.0464, -0.0002] r=-0.01 **non causale** | 0.0002 [-0.0000, 0.0005] r=— **non leggibile** |
| rl | 1049 | 0.0028 [0.0023, 0.0033] r=0.03 **non causale** | 0.0064 [-0.0056, 0.0205] r=0.02 **non causale** V | 0.0073 [-0.0023, 0.0170] r=0.12 **zona grigia** | 0.0082 [0.0016, 0.0148] r=0.00 **non causale** | 0.0010 [0.0008, 0.0014] r=— **non leggibile** |
| rs_a | 1242 | 0.1110 [0.1051, 0.1175] r=1.15 **causale** | 0.2581 [0.2206, 0.2997] r=1.00 **causale** V | 0.0614 [0.0242, 0.0965] r=1.00 **causale** | 0.0134 [-0.0203, 0.0395] r=0.01 **non causale** | 0.0019 [0.0002, 0.0043] r=— **non leggibile** |
| rs_m | 1237 | 0.0728 [0.0682, 0.0780] r=0.76 **causale** | -0.0073 [-0.0256, 0.0092] r=-0.03 **non causale** V | -0.0081 [-0.0218, 0.0049] r=-0.13 **non causale** | -0.0246 [-0.0401, -0.0091] r=-0.01 **non causale** | -0.0003 [-0.0005, -0.0001] r=— **non leggibile** |
| rs_p | 1229 | 0.0930 [0.0867, 0.0986] r=0.97 **causale** | 0.1898 [0.1621, 0.2288] r=0.74 **causale** V | 0.0637 [0.0331, 0.0949] r=1.04 **causale** | -0.0377 [-0.0628, -0.0164] r=-0.02 **non causale** | 0.0032 [0.0011, 0.0050] r=— **non leggibile** |
| u1 | 1720 | 0.4883 [0.4642, 0.5134] r=0.74 **causale** V | -0.0222 [-0.0693, 0.0357] r=-0.09 **non causale** | -0.0107 [-0.0580, 0.0269] r=— **non leggibile** | -0.0142 [-0.0320, 0.0015] r=-0.01 **non causale** | 0.0015 [0.0008, 0.0022] r=— **non leggibile** |
| u2 | 2172 | 0.4821 [0.4565, 0.5041] r=0.77 **causale** V | -0.0292 [-0.0799, 0.0215] r=-0.11 **non causale** | -0.0011 [-0.0461, 0.0376] r=— **non leggibile** | -0.0162 [-0.0313, 0.0002] r=-0.01 **non causale** | 0.0014 [0.0008, 0.0021] r=— **non leggibile** |
| w2 | 1826 | 0.0393 [0.0367, 0.0417] r=0.07 **non causale** V | -0.0002 [-0.0262, 0.0300] r=-0.00 **non causale** | 0.0330 [0.0076, 0.0543] r=— **non leggibile** | -0.0242 [-0.0434, -0.0049] r=-0.01 **non causale** | 0.0011 [0.0008, 0.0015] r=— **non leggibile** |

Testa di pagina (sezione hS, mano hM, lingua hL): perdita media per fascia di distanza dall'inizio (parole 0-9, 10-39, 40-99, 100+)

- hL: perdita 0.1353, 0.0380, 0.0306, 0.0186; KL del primo glifo 0.0185, 0.0072, 0.0036, 0.0015
- hM: perdita 0.1486, 0.0546, 0.0404, 0.0397; KL del primo glifo 0.0189, 0.0081, 0.0054, 0.0033
- hS: perdita 0.1445, 0.0750, 0.0434, 0.0928; KL del primo glifo 0.0244, 0.0135, 0.0111, 0.0157

Scambio parziale di stati (f0 = quota del cambio del primo glifo che passa; fw = quota del cambio delle parole): media sui modelli

- **pw**: tutto f0 1.000 fw 1.000; solo secondo strato f0 1.000 fw 0.749; solo primo strato f0 0.000 fw 0.233; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.02 (a caso 0.01); 4: 0.03 (a caso 0.01); 8: 0.06 (a caso 0.02); 16: 0.11 (a caso 0.05); 32: 0.21 (a caso 0.11); 64: 0.42 (a caso 0.21); 128: 0.77 (a caso 0.46)
- **rs_a**: tutto f0 1.000 fw 0.703; solo secondo strato f0 1.000 fw 0.582; solo primo strato f0 0.000 fw 0.117; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.01 (a caso 0.01); 4: 0.02 (a caso 0.02); 8: 0.06 (a caso 0.03); 16: 0.13 (a caso 0.06); 32: 0.26 (a caso 0.13); 64: 0.46 (a caso 0.25); 128: 0.77 (a caso 0.50)
- **u2**: tutto f0 1.000 fw 1.000; solo secondo strato f0 1.000 fw 0.744; solo primo strato f0 0.000 fw 0.236; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.02 (a caso 0.01); 4: 0.03 (a caso 0.02); 8: 0.06 (a caso 0.03); 16: 0.11 (a caso 0.06); 32: 0.22 (a caso 0.12); 64: 0.43 (a caso 0.26); 128: 0.79 (a caso 0.50)

## Modello M5: mappa "intervento -> tratto"

10 modelli, 207 pagine. Per ogni cella: effetto (intervallo al 95%), rapporto con l'ancora, etichetta; "V" = coppia validata dal controllo positivo.

| intervento | punti | kl_primo | eco_sopra | eco_riga | term | pc |
|---|---|---|---|---|---|---|
| fill | 2484 | 2.3272 [2.2466, 2.4152] r=4.36 **causale** | -0.1565 [-0.2611, -0.0440] r=-0.62 **non causale** | -0.3871 [-0.4835, -0.2915] r=— **non leggibile** | -0.0568 [-0.0734, -0.0435] r=-0.02 **non causale** | 0.0004 [0.0000, 0.0008] r=— **non leggibile** |
| hN | 1242 | 0.0609 [0.0575, 0.0657] r=1.00 **causale** | -0.3327 [-0.5062, -0.1565] r=-1.31 **non causale** | 0.4377 [0.2353, 0.6364] r=— **non leggibile** | 3.3926 [3.0704, 3.7191] r=1.00 **causale** | -0.0003 [-0.0013, 0.0008] r=— **non leggibile** |
| hR | 1242 | 0.0777 [0.0723, 0.0833] r=1.28 **causale** | -0.0121 [-0.0257, 0.0023] r=-0.05 **non causale** | -0.0075 [-0.0172, 0.0009] r=— **non leggibile** | -0.0057 [-0.0141, 0.0054] r=-0.00 **non causale** | -0.0000 [-0.0001, 0.0001] r=— **non leggibile** |
| hT | 1242 | 0.9364 [0.8575, 1.0429] r=15.36 **causale** | -0.1141 [-0.1692, -0.0606] r=-0.45 **non causale** | -0.1897 [-0.2285, -0.1449] r=— **non leggibile** | -0.0010 [-0.0247, 0.0223] r=-0.00 **non causale** | 0.0024 [0.0020, 0.0029] r=— **non leggibile** |
| lfill | 1242 | 2.8265 [2.7300, 2.9435] r=46.38 **causale** | -0.1982 [-0.2730, -0.1281] r=-0.78 **non causale** | -0.5209 [-0.5649, -0.4793] r=— **non leggibile** | 0.0023 [-0.0030, 0.0076] r=0.00 **non causale** | 0.0005 [0.0003, 0.0007] r=— **non leggibile** |
| lnul | 1242 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| nul | 2484 | 0.0000 [0.0000, 0.0000] r=0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** | -0.0000 [-0.0000, 0.0000] r=-0.00 **non causale** | -0.0000 [-0.0000, 0.0000] r=— **non leggibile** |
| p1 | 2111 | 0.0864 [0.0804, 0.0913] r=0.16 **non causale** | 0.0040 [-0.0197, 0.0225] r=0.02 **non causale** | 0.0127 [-0.0073, 0.0314] r=— **non leggibile** | 0.0150 [0.0057, 0.0240] r=0.00 **non causale** | 0.0001 [-0.0000, 0.0003] r=— **non leggibile** |
| p2 | 1622 | 0.1725 [0.1617, 0.1846] r=0.30 **zona grigia** | 0.0126 [-0.0285, 0.0556] r=0.05 **non causale** | 0.0011 [-0.0293, 0.0309] r=— **non leggibile** | -0.0006 [-0.0154, 0.0161] r=-0.00 **non causale** | 0.0008 [0.0005, 0.0011] r=— **non leggibile** |
| p3 | 1093 | 0.0835 [0.0774, 0.0905] r=0.15 **non causale** | 0.0433 [0.0113, 0.0779] r=0.17 **non causale** | 0.0486 [0.0203, 0.0857] r=— **non leggibile** | 0.0045 [-0.0106, 0.0224] r=0.00 **non causale** | 0.0005 [0.0003, 0.0008] r=— **non leggibile** |
| pm | 640 | 0.0667 [0.0596, 0.0745] r=0.13 **non causale** | 0.0384 [-0.0129, 0.0919] r=0.15 **non causale** | 0.0379 [0.0058, 0.0700] r=— **non leggibile** | 0.0079 [-0.0097, 0.0336] r=0.00 **non causale** | 0.0011 [0.0007, 0.0014] r=— **non leggibile** |
| pw | 2484 | 0.5342 [0.5091, 0.5527] r=1.00 **causale** | -0.0040 [-0.0582, 0.0558] r=-0.02 **non causale** | 0.0050 [-0.0439, 0.0447] r=— **non leggibile** | -0.0021 [-0.0187, 0.0151] r=-0.00 **non causale** | 0.0008 [0.0004, 0.0012] r=— **non leggibile** |
| rc | 1707 | 0.0185 [0.0166, 0.0203] r=0.03 **non causale** | 0.0054 [-0.0108, 0.0222] r=0.02 **non causale** | -0.0016 [-0.0142, 0.0122] r=— **non leggibile** | -0.0008 [-0.0089, 0.0070] r=-0.00 **non causale** | 0.0001 [-0.0001, 0.0003] r=— **non leggibile** |
| rl | 1037 | 0.0087 [0.0075, 0.0098] r=0.14 **non causale** | -0.0069 [-0.0206, 0.0088] r=-0.03 **non causale** | -0.0003 [-0.0193, 0.0177] r=— **non leggibile** | 0.0284 [0.0176, 0.0409] r=0.01 **non causale** | 0.0008 [0.0006, 0.0010] r=— **non leggibile** |
| rs_a | 1242 | 0.1220 [0.1145, 0.1286] r=2.00 **causale** | 0.2535 [0.1976, 0.3005] r=1.00 **causale** | 0.0359 [-0.0119, 0.0811] r=— **non leggibile** | 0.0422 [0.0128, 0.0725] r=0.01 **non causale** | 0.0015 [-0.0000, 0.0032] r=— **non leggibile** |
| rs_m | 1232 | 0.0453 [0.0419, 0.0487] r=0.74 **causale** | -0.0106 [-0.0294, 0.0045] r=-0.04 **non causale** | 0.0002 [-0.0134, 0.0131] r=— **non leggibile** | -0.0182 [-0.0276, -0.0089] r=-0.01 **non causale** | -0.0001 [-0.0002, 0.0001] r=— **non leggibile** |
| rs_p | 1229 | 0.1107 [0.1038, 0.1184] r=1.82 **causale** | 0.2152 [0.1663, 0.2613] r=0.85 **causale** | 0.0661 [0.0200, 0.1091] r=— **non leggibile** | 0.0796 [0.0485, 0.1125] r=0.02 **non causale** | 0.0019 [0.0006, 0.0034] r=— **non leggibile** |
| u1 | 1730 | 0.4491 [0.4288, 0.4686] r=0.77 **causale** | 0.0325 [-0.0117, 0.0784] r=0.13 **non causale** | -0.0451 [-0.0949, -0.0004] r=— **non leggibile** | -0.0009 [-0.0127, 0.0088] r=-0.00 **non causale** | 0.0003 [-0.0001, 0.0006] r=— **non leggibile** |
| u2 | 2147 | 0.4527 [0.4326, 0.4736] r=0.80 **causale** | 0.0161 [-0.0295, 0.0612] r=0.06 **non causale** | -0.0178 [-0.0628, 0.0236] r=— **non leggibile** | 0.0141 [-0.0016, 0.0286] r=0.00 **non causale** | 0.0006 [0.0003, 0.0009] r=— **non leggibile** |
| w2 | 1815 | 0.0315 [0.0291, 0.0337] r=0.06 **non causale** | -0.0313 [-0.0586, -0.0021] r=-0.12 **non causale** | -0.0044 [-0.0281, 0.0227] r=— **non leggibile** | -0.0023 [-0.0140, 0.0089] r=-0.00 **non causale** | 0.0006 [0.0004, 0.0008] r=— **non leggibile** |

Testa di pagina (sezione hS, mano hM, lingua hL): perdita media per fascia di distanza dall'inizio (parole 0-9, 10-39, 40-99, 100+)

- hL: perdita 0.0578, 0.0071, 0.0007, 0.0037; KL del primo glifo 0.0092, 0.0005, 0.0002, 0.0002
- hM: perdita 0.0374, 0.0002, 0.0025, 0.0042; KL del primo glifo 0.0127, 0.0019, 0.0008, 0.0005
- hS: perdita 0.0463, 0.0065, 0.0014, 0.0064; KL del primo glifo 0.0165, 0.0037, 0.0019, 0.0006

Scambio parziale di stati (f0 = quota del cambio del primo glifo che passa; fw = quota del cambio delle parole): media sui modelli

- **pw**: tutto f0 1.000 fw 0.840; solo secondo strato f0 1.000 fw 0.644; solo primo strato f0 0.000 fw 0.187; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.01); 2: 0.01 (a caso 0.01); 4: 0.03 (a caso 0.02); 8: 0.05 (a caso 0.04); 16: 0.10 (a caso 0.08); 32: 0.21 (a caso 0.13); 64: 0.43 (a caso 0.27); 128: 0.76 (a caso 0.50)
- **rs_a**: tutto f0 1.000 fw 0.241; solo secondo strato f0 1.000 fw 0.121; solo primo strato f0 0.000 fw 0.116; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.01 (a caso 0.01); 4: 0.03 (a caso 0.01); 8: 0.05 (a caso 0.03); 16: 0.11 (a caso 0.06); 32: 0.20 (a caso 0.12); 64: 0.40 (a caso 0.24); 128: 0.76 (a caso 0.48)
- **u2**: tutto f0 1.000 fw 0.884; solo secondo strato f0 1.000 fw 0.673; solo primo strato f0 0.000 fw 0.200; k70 dimensioni 128 (a caso None)
  - k dimensioni (f0): 1: 0.01 (a caso 0.00); 2: 0.02 (a caso 0.01); 4: 0.03 (a caso 0.02); 8: 0.06 (a caso 0.03); 16: 0.13 (a caso 0.06); 32: 0.26 (a caso 0.12); 64: 0.47 (a caso 0.25); 128: 0.79 (a caso 0.50)

## Controlli positivi (testo sintetico a regole note, alla forza del vero) e negativi

### M1 (5 semi)

| coppia | verita' piantata | etichette nei semi | giuste | validata |
|---|---|---|---|---|
| u1|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| u2|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| pw|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| p2|kl_primo | non causale | non causale, non causale, non causale, zona grigia, non causale | 4/5 | si |
| p3|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| pm|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| p1|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| w2|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| rc|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| rs_a|eco_sopra | causale | non leggibile, non leggibile, non leggibile, non leggibile, non leggibile | 0/5 | NO |
| rs_p|eco_sopra | causale | non leggibile, non leggibile, non leggibile, non leggibile, non leggibile | 0/5 | NO |
| rs_m|eco_sopra | non causale | non leggibile, non leggibile, non leggibile, non leggibile, non leggibile | 0/5 | NO |
| rl|eco_sopra | non causale | non leggibile, non leggibile, non leggibile, non leggibile, non leggibile | 0/5 | NO |
| hN|term | causale | causale, causale, causale, causale, causale | 5/5 | si |

Modelli senza regola piantata (le coppie causali per costruzione in `ec` non devono risultare causali): u1|kl_primo: senza regola causale (rapporti ['0.92']), con regola causale, causale, causale, causale, causale: NON riuscito; u2|kl_primo: senza regola zona grigia (rapporti ['0.83']), con regola causale, causale, causale, causale, causale: riuscito; rs_p|eco_sopra: senza regola non leggibile (rapporti ['—']), con regola non leggibile, non leggibile, non leggibile, non leggibile, non leggibile: riuscito

### E2 (5 semi)

| coppia | verita' piantata | etichette nei semi | giuste | validata |
|---|---|---|---|---|
| u1|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| u2|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| pw|kl_primo | causale | causale, causale, causale, causale, causale | 5/5 | si |
| p2|kl_primo | non causale | zona grigia, non causale, non causale, non causale, zona grigia | 3/5 | NO |
| p3|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| pm|kl_primo | non causale | non causale, non causale, non causale, non causale, zona grigia | 4/5 | si |
| p1|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| w2|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| rc|kl_primo | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| rs_a|eco_sopra | causale | causale, causale, causale, causale, causale | 5/5 | si |
| rs_p|eco_sopra | causale | causale, causale, causale, causale, causale | 5/5 | si |
| rs_m|eco_sopra | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| rl|eco_sopra | non causale | non causale, non causale, non causale, non causale, non causale | 5/5 | si |
| hN|term | causale | causale, causale, causale, causale, causale | 5/5 | si |

Modelli senza regola piantata (le coppie causali per costruzione in `ec` non devono risultare causali): u1|kl_primo: senza regola causale (rapporti ['0.90']), con regola causale, causale, causale, causale, causale: NON riuscito; u2|kl_primo: senza regola causale (rapporti ['0.93']), con regola causale, causale, causale, causale, causale: NON riuscito; rs_p|eco_sopra: senza regola non leggibile (rapporti ['—']), con regola causale, causale, causale, causale, causale: riuscito

## Integrita': libro con intervento nullo = libro senza intervento

- reale|M1: identico
- ec|M1: identico
- reale|E2: identico
- ec|E2: identico
- reale|M5: identico

## Libri scritti sotto intervento (ec, E2): quali tratti spariscono e quali restano

| condizione | aderenza_N | bordi_fine | bordi_inizio | contatto | eco_netto | eco_riga | eco_sopra | tasso_eco |
|---|---|---|---|---|---|---|---|---|
| base | 0.4125 | 0.2228 | 0.2883 | 0.1403 | 0.0735 | 0.0925 | 0.1763 | 0.2688 |
| hN | 0.0841 (r=0.20) sparisce | 0.2121 (r=0.95) cala in parte | 0.3002 (r=1.04) cala in parte | 0.1291 (r=0.92) cala in parte | 0.0668 (r=0.91) cala in parte | 0.0946 (r=1.02) resta | 0.1743 (r=0.99) resta | 0.2689 (r=1.00) resta |
| nul | 0.4125 (r=1.00) resta | 0.2228 (r=1.00) cala in parte | 0.2883 (r=1.00) cala in parte | 0.1403 (r=1.00) resta | 0.0735 (r=1.00) resta | 0.0925 (r=1.00) resta | 0.1763 (r=1.00) resta | 0.2688 (r=1.00) resta |
| p1 | 0.3803 (r=0.92) resta | 0.2091 (r=0.94) cala in parte | 0.2864 (r=0.99) cala in parte | 0.1249 (r=0.89) cala in parte | 0.0642 (r=0.87) cala in parte | 0.0886 (r=0.96) resta | 0.1777 (r=1.01) resta | 0.2664 (r=0.99) resta |
| ptr_off | 0.4017 (r=0.97) resta | 0.2281 (r=1.02) cala in parte | 0.3067 (r=1.06) cala in parte | 0.1455 (r=1.04) resta | 0.0464 (r=0.63) cala in parte | 0.0809 (r=0.88) resta | 0.1704 (r=0.97) resta | 0.2514 (r=0.94) resta |
| pw | 0.3795 (r=0.92) cala in parte | 0.2206 (r=0.99) cala in parte | 0.2890 (r=1.00) cala in parte | 0.0081 (r=0.06) sparisce | 0.0595 (r=0.81) cala in parte | 0.0824 (r=0.89) cala in parte | 0.1731 (r=0.98) resta | 0.2556 (r=0.95) resta |
| rs_a | 0.4129 (r=1.00) resta | 0.2143 (r=0.96) cala in parte | 0.3012 (r=1.04) cala in parte | 0.1346 (r=0.96) cala in parte | 0.0607 (r=0.83) cala in parte | 0.0906 (r=0.98) resta | 0.1686 (r=0.96) resta | 0.2592 (r=0.96) resta |
| u2 | 0.3746 (r=0.91) resta | 0.2260 (r=1.01) cala in parte | 0.3035 (r=1.05) cala in parte | 0.0175 (r=0.12) sparisce | 0.0641 (r=0.87) cala in parte | 0.0859 (r=0.93) resta | 0.1776 (r=1.01) resta | 0.2635 (r=0.98) resta |

## Libri scritti sotto intervento (ec, M1): quali tratti spariscono e quali restano

| condizione | aderenza_N | bordi_fine | bordi_inizio | contatto | eco_netto | eco_riga | eco_sopra | tasso_eco |
|---|---|---|---|---|---|---|---|---|
| base | 0.3029 | 0.2114 | 0.2926 | 0.1240 | 0.0477 | 0.0936 | 0.1629 | 0.2565 |
| hN | 0.1059 (r=0.35) sparisce | 0.2073 (r=0.98) cala in parte | 0.3102 (r=1.06) cala in parte | 0.1285 (r=1.04) resta | 0.0391 (r=0.82) cala in parte | 0.0876 (r=0.94) resta | 0.1592 (r=0.98) resta | 0.2468 (r=0.96) resta |
| nul | 0.3029 (r=1.00) cala in parte | 0.2114 (r=1.00) cala in parte | 0.2926 (r=1.00) cala in parte | 0.1240 (r=1.00) resta | 0.0477 (r=1.00) resta | 0.0936 (r=1.00) resta | 0.1629 (r=1.00) resta | 0.2565 (r=1.00) resta |
| p1 | 0.2913 (r=0.96) cala in parte | 0.2033 (r=0.96) cala in parte | 0.3087 (r=1.06) cala in parte | 0.1294 (r=1.04) resta | 0.0498 (r=1.04) cala in parte | 0.0857 (r=0.92) cala in parte | 0.1658 (r=1.02) resta | 0.2515 (r=0.98) resta |
| pw | 0.2797 (r=0.92) cala in parte | 0.2104 (r=1.00) cala in parte | 0.3038 (r=1.04) cala in parte | 0.0076 (r=0.06) sparisce | 0.0529 (r=1.11) cala in parte | 0.0833 (r=0.89) cala in parte | 0.1663 (r=1.02) resta | 0.2496 (r=0.97) resta |
| rs_a | 0.3029 (r=1.00) resta | 0.2039 (r=0.96) cala in parte | 0.3140 (r=1.07) cala in parte | 0.1303 (r=1.05) resta | 0.0522 (r=1.09) cala in parte | 0.0905 (r=0.97) resta | 0.1650 (r=1.01) resta | 0.2554 (r=1.00) resta |
| u2 | 0.2864 (r=0.95) cala in parte | 0.2067 (r=0.98) cala in parte | 0.3073 (r=1.05) cala in parte | 0.0234 (r=0.19) sparisce | 0.0577 (r=1.21) cala in parte | 0.0908 (r=0.97) cala in parte | 0.1650 (r=1.01) resta | 0.2558 (r=1.00) resta |

## Libri scritti sotto intervento (ord, M1): quali tratti spariscono e quali restano

| condizione | D | aderenza_N | bordi_fine | bordi_inizio | contatto | eco_netto | eco_riga | eco_sopra | tasso_eco |
|---|---|---|---|---|---|---|---|---|---|
| base | 0.0075 | 0.4769 | 0.0064 | 0.0155 | 0.0042 | 0.0643 | 0.1030 | 0.1499 | 0.2529 |
| p1 | 0.0035 (r=0.47) cala in parte | 0.4899 (r=1.03) resta | 0.0072 (r=1.12) cala in parte | 0.0117 (r=0.75) cala in parte | 0.0035 (r=0.84) non leggibile | 0.0688 (r=1.07) resta | 0.0981 (r=0.95) resta | 0.1491 (r=0.99) resta | 0.2472 (r=0.98) resta |
| pw | 0.0004 (r=0.05) sparisce | 0.4938 (r=1.04) resta | 0.0065 (r=1.00) resta | 0.0141 (r=0.91) cala in parte | -0.0018 (r=-0.44) non leggibile | 0.0669 (r=1.04) resta | 0.0998 (r=0.97) resta | 0.1523 (r=1.02) resta | 0.2521 (r=1.00) resta |
| u2 | 0.0039 (r=0.52) cala in parte | 0.5107 (r=1.07) resta | 0.0076 (r=1.18) cala in parte | 0.0103 (r=0.66) cala in parte | -0.0020 (r=-0.47) non leggibile | 0.0578 (r=0.90) resta | 0.0976 (r=0.95) resta | 0.1505 (r=1.00) resta | 0.2480 (r=0.98) resta |

## Libri scritti sotto intervento (reale, E2): quali tratti spariscono e quali restano

| condizione | D | aderenza_N | bordi_fine | bordi_inizio | contatto | contatto_pesante | copia_netta | eco_netto | eco_riga | eco_sopra | lam | tasso_eco |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.1406 | 0.4487 | 0.0770 | 0.2000 | 0.1822 | 0.1828 | 0.1106 | 0.1183 | 0.1603 | 0.1880 | 0.3990 | 0.3483 |
| hN | — | 0.0857 (r=0.19) sparisce | 0.0785 (r=1.02) resta | 0.1954 (r=0.98) resta | 0.1763 (r=0.97) cala in parte | 0.1760 (r=0.96) cala in parte | 0.0991 (r=0.90) cala in parte | 0.1183 (r=1.00) resta | 0.1578 (r=0.98) resta | 0.1725 (r=0.92) resta | 0.3944 (r=0.99) resta | 0.3302 (r=0.95) resta |
| nul | — | 0.4375 (r=0.98) resta | 0.0800 (r=1.04) resta | 0.2048 (r=1.02) resta | 0.2061 (r=1.13) cala in parte | — | — | 0.1251 (r=1.06) resta | 0.1720 (r=1.07) resta | 0.1924 (r=1.02) resta | — | 0.3644 (r=1.05) resta |
| p1 | 0.1210 (r=0.86) cala in parte | 0.4438 (r=0.99) resta | 0.0809 (r=1.05) resta | 0.2063 (r=1.03) resta | 0.1776 (r=0.97) resta | 0.1775 (r=0.97) resta | 0.1023 (r=0.92) cala in parte | 0.1114 (r=0.94) resta | 0.1485 (r=0.93) resta | 0.1823 (r=0.97) resta | 0.3826 (r=0.96) cala in parte | 0.3308 (r=0.95) resta |
| ptr_d1 | — | 0.4467 (r=1.00) resta | 0.0835 (r=1.08) resta | 0.2107 (r=1.05) resta | 0.1822 (r=1.00) resta | 0.1823 (r=1.00) resta | 0.0454 (r=0.41) cala in parte | 0.0965 (r=0.82) cala in parte | 0.1468 (r=0.92) resta | 0.1735 (r=0.92) resta | 0.1350 (r=0.34) cala in parte | 0.3203 (r=0.92) resta |
| ptr_off | — | 0.4430 (r=0.99) resta | 0.0842 (r=1.09) resta | 0.2108 (r=1.05) resta | 0.1820 (r=1.00) resta | 0.1826 (r=1.00) resta | 0.0385 (r=0.35) sparisce | 0.0930 (r=0.79) cala in parte | 0.1443 (r=0.90) resta | 0.1748 (r=0.93) resta | 0.0885 (r=0.22) cala in parte | 0.3191 (r=0.92) resta |
| ptr_sopra | — | 0.4408 (r=0.98) resta | 0.0829 (r=1.08) resta | 0.2055 (r=1.03) resta | 0.1793 (r=0.98) resta | 0.1796 (r=0.98) resta | 0.0824 (r=0.74) cala in parte | 0.1080 (r=0.91) resta | 0.1470 (r=0.92) resta | 0.1937 (r=1.03) resta | 0.3228 (r=0.81) cala in parte | 0.3406 (r=0.98) resta |
| pw | 0.0374 (r=0.27) sparisce | 0.4332 (r=0.97) resta | 0.0794 (r=1.03) resta | 0.2152 (r=1.08) resta | 0.0185 (r=0.10) sparisce | 0.0186 (r=0.10) sparisce | 0.0759 (r=0.69) cala in parte | 0.1029 (r=0.87) resta | 0.1323 (r=0.83) cala in parte | 0.1771 (r=0.94) resta | 0.4672 (r=1.17) cala in parte | 0.3094 (r=0.89) resta |
| rs_a | — | 0.4301 (r=0.96) resta | 0.0773 (r=1.00) resta | 0.2117 (r=1.06) resta | 0.1845 (r=1.01) resta | 0.1852 (r=1.01) resta | 0.0576 (r=0.52) cala in parte | 0.1021 (r=0.86) resta | 0.1515 (r=0.95) resta | 0.1614 (r=0.86) resta | 0.4271 (r=1.07) cala in parte | 0.3129 (r=0.90) resta |
| rs_m | — | 0.4469 (r=1.00) resta | 0.0758 (r=0.98) resta | 0.2008 (r=1.00) resta | 0.1786 (r=0.98) resta | 0.1789 (r=0.98) resta | 0.1221 (r=1.10) cala in parte | 0.1206 (r=1.02) resta | 0.1607 (r=1.00) resta | 0.1880 (r=1.00) resta | 0.4138 (r=1.04) resta | 0.3487 (r=1.00) resta |
| u2 | 0.0714 (r=0.51) cala in parte | 0.4485 (r=1.00) resta | 0.0893 (r=1.16) cala in parte | 0.2061 (r=1.03) resta | 0.0414 (r=0.23) sparisce | 0.0412 (r=0.23) sparisce | 0.0792 (r=0.72) cala in parte | 0.1079 (r=0.91) resta | 0.1404 (r=0.88) resta | 0.1801 (r=0.96) resta | 0.3713 (r=0.93) cala in parte | 0.3205 (r=0.92) resta |

## Libri scritti sotto intervento (reale, M1): quali tratti spariscono e quali restano

| condizione | D | aderenza_N | bordi_fine | bordi_inizio | contatto | contatto_pesante | copia_netta | eco_netto | eco_riga | eco_sopra | lam | tasso_eco |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.1487 | 0.4442 | 0.0903 | 0.2094 | 0.1855 | 0.1853 | 0.0362 | 0.0970 | 0.1567 | 0.1809 | 0.0104 | 0.3376 |
| fill | — | 0.2527 (r=0.57) cala in parte | 0.1079 (r=1.20) cala in parte | 0.1493 (r=0.71) cala in parte | 0.0337 (r=0.18) sparisce | — | — | 0.1096 (r=1.13) resta | 0.2845 (r=1.82) cresce | 0.2400 (r=1.33) cresce | — | 0.5245 (r=1.55) cresce |
| hN | — | 0.0912 (r=0.21) sparisce | 0.0931 (r=1.03) resta | 0.2068 (r=0.99) resta | 0.1832 (r=0.99) resta | 0.1829 (r=0.99) resta | 0.0288 (r=0.79) cala in parte | 0.0986 (r=1.02) resta | 0.1553 (r=0.99) resta | 0.1669 (r=0.92) resta | 0.1281 (r=12.29) non leggibile | 0.3222 (r=0.95) resta |
| nul | — | 0.4516 (r=1.02) resta | 0.0898 (r=0.99) resta | 0.1948 (r=0.93) resta | 0.1868 (r=1.01) resta | — | — | 0.1011 (r=1.04) resta | 0.1614 (r=1.03) resta | 0.1848 (r=1.02) resta | — | 0.3462 (r=1.03) resta |
| p1 | 0.1305 (r=0.88) resta | 0.4442 (r=1.00) resta | 0.0949 (r=1.05) resta | 0.2160 (r=1.03) resta | 0.1865 (r=1.00) resta | 0.1861 (r=1.00) resta | 0.0322 (r=0.89) cala in parte | 0.0920 (r=0.95) resta | 0.1479 (r=0.94) resta | 0.1776 (r=0.98) resta | 0.0924 (r=8.86) non leggibile | 0.3255 (r=0.96) resta |
| pw | 0.0520 (r=0.35) sparisce | 0.4395 (r=0.99) resta | 0.0912 (r=1.01) resta | 0.2270 (r=1.08) resta | 0.0233 (r=0.13) sparisce | 0.0233 (r=0.13) sparisce | 0.0129 (r=0.35) sparisce | 0.0815 (r=0.84) resta | 0.1292 (r=0.82) cala in parte | 0.1714 (r=0.95) resta | -0.2714 (r=-26.03) non leggibile | 0.3006 (r=0.89) resta |
| rs_a | — | 0.4381 (r=0.99) resta | 0.0940 (r=1.04) resta | 0.2210 (r=1.06) resta | 0.1915 (r=1.03) resta | 0.1915 (r=1.03) resta | 0.0227 (r=0.63) cala in parte | 0.0923 (r=0.95) resta | 0.1497 (r=0.96) resta | 0.1698 (r=0.94) resta | -0.0802 (r=-7.69) non leggibile | 0.3196 (r=0.95) resta |
| rs_m | — | 0.4444 (r=1.00) resta | 0.0914 (r=1.01) resta | 0.2091 (r=1.00) resta | 0.1879 (r=1.01) resta | 0.1871 (r=1.01) resta | 0.0379 (r=1.05) cala in parte | 0.1019 (r=1.05) resta | 0.1590 (r=1.01) resta | 0.1811 (r=1.00) resta | -0.0597 (r=-5.72) non leggibile | 0.3401 (r=1.01) resta |
| u2 | 0.0768 (r=0.52) cala in parte | 0.4482 (r=1.01) resta | 0.1020 (r=1.13) resta | 0.2216 (r=1.06) resta | 0.0403 (r=0.22) sparisce | 0.0402 (r=0.22) sparisce | 0.0253 (r=0.70) cala in parte | 0.0884 (r=0.91) resta | 0.1401 (r=0.89) resta | 0.1763 (r=0.97) resta | 0.0637 (r=6.11) non leggibile | 0.3165 (r=0.94) resta |

## Libri scritti sotto intervento (reale, M5): quali tratti spariscono e quali restano

| condizione | D | aderenza_N | bordi_fine | bordi_inizio | contatto | contatto_pesante | copia_netta | eco_netto | eco_riga | eco_sopra | lam | tasso_eco |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.1103 | 0.6593 | 0.0870 | 0.1939 | 0.1585 | 0.1587 | 0.1398 | 0.1169 | 0.1509 | 0.1846 | 0.2035 | 0.3355 |
| hN | — | 0.0505 (r=0.08) sparisce | 0.0827 (r=0.95) resta | 0.1833 (r=0.94) resta | 0.1528 (r=0.96) resta | 0.1530 (r=0.96) resta | 0.1152 (r=0.82) cala in parte | 0.1122 (r=0.96) resta | 0.1527 (r=1.01) resta | 0.1682 (r=0.91) resta | 0.3241 (r=1.59) cala in parte | 0.3209 (r=0.96) resta |
| nul | — | 0.6872 (r=1.04) resta | 0.0911 (r=1.05) resta | 0.2094 (r=1.08) resta | 0.1549 (r=0.98) resta | — | — | 0.1223 (r=1.05) resta | 0.1501 (r=0.99) resta | 0.1876 (r=1.02) resta | — | 0.3377 (r=1.01) resta |
| ptr_off | — | 0.6614 (r=1.00) resta | 0.0887 (r=1.02) resta | 0.1931 (r=1.00) resta | 0.1718 (r=1.08) resta | 0.1717 (r=1.08) resta | 0.0820 (r=0.59) cala in parte | 0.0985 (r=0.84) cala in parte | 0.1405 (r=0.93) resta | 0.1729 (r=0.94) resta | 0.1536 (r=0.75) cala in parte | 0.3134 (r=0.93) resta |
| ptr_sopra | — | 0.6588 (r=1.00) resta | 0.0855 (r=0.98) resta | 0.1903 (r=0.98) resta | 0.1577 (r=0.99) resta | 0.1573 (r=0.99) resta | 0.1258 (r=0.90) cala in parte | 0.1105 (r=0.95) resta | 0.1446 (r=0.96) resta | 0.1873 (r=1.01) resta | 0.2719 (r=1.34) cala in parte | 0.3320 (r=0.99) resta |
| pw | 0.0411 (r=0.37) sparisce | 0.6868 (r=1.04) resta | 0.0898 (r=1.03) resta | 0.2210 (r=1.14) cala in parte | 0.0195 (r=0.12) sparisce | 0.0193 (r=0.12) sparisce | 0.0624 (r=0.45) cala in parte | 0.0974 (r=0.83) cala in parte | 0.1271 (r=0.84) resta | 0.1702 (r=0.92) resta | 0.4476 (r=2.20) cresce | 0.2973 (r=0.89) resta |
| rs_a | — | 0.6669 (r=1.01) resta | 0.0813 (r=0.93) cala in parte | 0.2059 (r=1.06) resta | 0.1772 (r=1.12) resta | 0.1776 (r=1.12) resta | 0.0583 (r=0.42) cala in parte | 0.1040 (r=0.89) resta | 0.1449 (r=0.96) resta | 0.1550 (r=0.84) resta | 0.4095 (r=2.01) cresce | 0.2999 (r=0.89) resta |
| u2 | 0.0482 (r=0.44) sparisce | 0.6593 (r=1.00) resta | 0.1026 (r=1.18) cala in parte | 0.1996 (r=1.03) resta | 0.0342 (r=0.22) sparisce | 0.0344 (r=0.22) sparisce | 0.0663 (r=0.47) cala in parte | 0.0935 (r=0.80) cala in parte | 0.1148 (r=0.76) cala in parte | 0.1564 (r=0.85) cala in parte | 0.3356 (r=1.65) cresce | 0.2712 (r=0.81) cala in parte |

## Letture preregistrate

### L1_contatto

- M1: u1|kl_primo = causale; u2|kl_primo = causale; p2|kl_primo = non causale; p1|kl_primo = non causale; pw|kl_primo = causale; w2|kl_primo = non causale; rc|kl_primo = non causale
- E2: u1|kl_primo = causale; u2|kl_primo = causale; p2|kl_primo = lettura non valida; p1|kl_primo = non causale; pw|kl_primo = causale; w2|kl_primo = non causale; rc|kl_primo = non causale
- M5: u1|kl_primo = causale (nessun controllo); u2|kl_primo = causale (nessun controllo); p2|kl_primo = zona grigia (nessun controllo); p1|kl_primo = non causale (nessun controllo); pw|kl_primo = causale (nessun controllo); w2|kl_primo = non causale (nessun controllo); rc|kl_primo = non causale (nessun controllo)

### L2_eco

- M1: rs_m|eco_sopra = lettura non valida; rs_p|eco_sopra = lettura non valida; rs_a|eco_sopra = lettura non valida; rl|eco_sopra = lettura non valida; rs_m|pc = non leggibile (nessun controllo); rs_p|pc = non leggibile (nessun controllo); rs_a|pc = non leggibile (nessun controllo)
- E2: rs_m|eco_sopra = non causale; rs_p|eco_sopra = causale; rs_a|eco_sopra = causale; rl|eco_sopra = non causale; rs_m|pc = non leggibile (nessun controllo); rs_p|pc = non leggibile (nessun controllo); rs_a|pc = non leggibile (nessun controllo)
- M5: rs_m|eco_sopra = non causale (nessun controllo); rs_p|eco_sopra = causale (nessun controllo); rs_a|eco_sopra = causale (nessun controllo); rl|eco_sopra = non causale (nessun controllo); rs_m|pc = non leggibile (nessun controllo); rs_p|pc = non leggibile (nessun controllo); rs_a|pc = non leggibile (nessun controllo)

### L3_bordi

- M1: hN|term = causale; hT|term = non causale (nessun controllo); hR|term = non causale (nessun controllo); hN|kl_primo = causale (nessun controllo); hT|kl_primo = causale (nessun controllo); hR|kl_primo = causale (nessun controllo); rs_a|kl_primo = causale (nessun controllo)
- E2: hN|term = causale; hT|term = non causale (nessun controllo); hR|term = non causale (nessun controllo); hN|kl_primo = causale (nessun controllo); hT|kl_primo = causale (nessun controllo); hR|kl_primo = causale (nessun controllo); rs_a|kl_primo = causale (nessun controllo)
- M5: hN|term = causale (nessun controllo); hT|term = non causale (nessun controllo); hR|term = non causale (nessun controllo); hN|kl_primo = causale (nessun controllo); hT|kl_primo = causale (nessun controllo); hR|kl_primo = causale (nessun controllo); rs_a|kl_primo = causale (nessun controllo)

### L1b_sufficienza_ultime_due

- M1: u2_su_pw = 0.8144793272092172; ic = [0.7711762241293295, 0.8579263392901477]; p1_su_pw = 0.17415471392093107; lettura = zona grigia
- E2: u2_su_pw = 0.7727439304046508; ic = [0.7287083683269737, 0.8125372176343639]; p1_su_pw = 0.16877348490107494; lettura = zona grigia
- M5: u2_su_pw = 0.8030300826215772; ic = [0.7658003068340077, 0.8441373662969096]; p1_su_pw = 0.15527017006567922; lettura = zona grigia

### L4_ordine_famiglie

- reale|E2: hN = None; nul = None; p1 = cala in parte; ptr_d1 = None; ptr_off = None; ptr_sopra = None; pw = sparisce; rs_a = None; rs_m = None; u2 = cala in parte
- reale|M1: fill = None; hN = None; nul = None; p1 = resta; pw = sparisce; rs_a = None; rs_m = None; u2 = cala in parte
- reale|M5: hN = None; nul = None; ptr_off = None; ptr_sopra = None; pw = sparisce; rs_a = None; u2 = sparisce
- controllo ord|M1: p1 = cala in parte; pw = sparisce; u2 = cala in parte

### L5_dove

- M1|pw: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.7643272807021482; y1_fw = 0.2150006738721116; k70_dimensioni = 128; k70_controllo = 128; k70_dimensioni_a_caso = None; lettura = come il controllo
- M1|rs_a: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.7970471325693971; y1_fw = 0.18810513505901416; k70_dimensioni = 128; k70_controllo = 64; k70_dimensioni_a_caso = None; lettura = più sparsa del controllo
- M1|u2: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.7511673799810074; y1_fw = 0.2305732400364166; k70_dimensioni = 128; k70_controllo = 128; k70_dimensioni_a_caso = None; lettura = come il controllo
- E2|pw: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.7486074091835337; y1_fw = 0.2331075176842221; k70_dimensioni = 128; k70_controllo = 128; k70_dimensioni_a_caso = None; lettura = come il controllo
- E2|rs_a: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.5819150405743023; y1_fw = 0.1165542311656395; k70_dimensioni = 128; k70_controllo = 64; k70_dimensioni_a_caso = None; lettura = più sparsa del controllo
- E2|u2: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.7436611989448169; y1_fw = 0.23619087037898176; k70_dimensioni = 128; k70_controllo = 128; k70_dimensioni_a_caso = None; lettura = come il controllo
- M5|pw: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.644044445160098; y1_fw = 0.18677212966685977; k70_dimensioni = 128; k70_controllo = None; k70_dimensioni_a_caso = None; lettura = nessun controllo
- M5|rs_a: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.12103584322630526; y1_fw = 0.11595003269121291; k70_dimensioni = 128; k70_controllo = None; k70_dimensioni_a_caso = None; lettura = nessun controllo
- M5|u2: y2_f0 = 1.0; y1_f0 = 0.0; y2_fw = 0.6726164329275888; y1_fw = 0.1996607099098225; k70_dimensioni = 128; k70_controllo = None; k70_dimensioni_a_caso = None; lettura = nessun controllo

### L6_libri

vedi la tabella dei libri

