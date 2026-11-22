# IA31 (ia31) — l'automa minimo della forma delle parole

Preregistrazione: `preregistrazioni/ia31.md`.

- Versioni: python 3.12.10, numpy 2.5.3, automa automa-1, testi automa-testi-1.
- Controlli: tutti riusciti.

## Controlli

**Positivo (automa noto):** 8 su 8 entro una volta e mezza (soglia 7) -> riuscito.

| testo | K0 | famiglia | K stimato | per piega | dentro |
|---|---|---|---|---|---|
| sint_L4_1 | 4 | libero | 4 | [4, 4, 4, 4, 4] | si |
| sint_L4_2 | 4 | libero | 6 | [6, 6, 6, 6, 4] | si |
| sint_L8_1 | 8 | libero | 8 | [8, 8, 8, 8, 8] | si |
| sint_L8_2 | 8 | libero | 12 | [8, 12, 12, 8, 8] | si |
| sint_L16_1 | 16 | libero | 12 | [12, 12, 12, 12, 12] | si |
| sint_C6_1 | 6 | caselle | 6 | [6, 6, 6, 6, 6] | si |
| sint_L16_2 | 16 | libero | 16 | [16, 16, 16, 16, 16] | si |
| sint_C6_2 | 6 | caselle | 6 | [6, 6, 6, 6, 6] | si |

**Negativo (glifi rimescolati dentro le parole):** riuscito.

| testo | K P | K vero P | guadagno P | guadagno vero P | crolla P | K D | K vero D | guadagno D | guadagno vero D | crolla D |
|---|---|---|---|---|---|---|---|---|---|---|
| neg_N1 | 16 | 24 | 0,034 | 0,272 | True | 8 | 16 | 0,063 | 0,300 | True |
| neg_N2 | 16 | 24 | 0,085 | 0,272 | True | 12 | 16 | 0,097 | 0,300 | True |

**Positivo dello scarto (rumore sul secondo e terzo glifo):** gap True, neutro True -> riuscito.

| testo | scarto 2+3 stimato (automa) | errore | scarto 2+3 esatto | scarto 2+3 trigramma |
|---|---|---|---|---|
| sint_gap | 0,6305 | 0,0031 | 0,6275 | 0,7370 |
| sint_neutro | -0,0039 | 0,0027 | -0,0038 | -0,0037 |

## L1: la taglia minima del vero

| peso e famiglia | K (BIC) | per piega | K (fuori) | K90 | parametri | costo parole nuove automa | trigramma | come il trigramma | K grande |
|---|---|---|---|---|---|---|---|---|---|
| P|libero | 24 | [32, 32, 24, 24, 24] | 96 | 16 | 1319 | 3,455 | 3,479 | si | 3,363 |
| P|caselle | 32 | [32, 32, 32, 32, 32] | 64 | 24 | 1519 | 3,568 | 3,479 | no | 3,474 |
| D|libero | 16 | [16, 16, 24, 16, 16] | 96 | 16 | 751 | 3,282 | 3,479 | si | 3,120 |
| D|caselle | 32 | [32, 32, 32, 24, 24] | 64 | 16 | 1519 | 3,232 | 3,479 | si | 3,170 |

- Peso P: le caselle bastano? K libero 24, K caselle 32, costo parole nuove 3,568 contro 3,455 -> **no**.
- Peso D: le caselle bastano? K libero 16, K caselle 32, costo parole nuove 3,232 contro 3,282 -> **no**.
- P|libero: pianoro della curva fuori (K90 <= K scelto) -> si.
- P|caselle: pianoro della curva fuori (K90 <= K scelto) -> si.
- D|libero: pianoro della curva fuori (K90 <= K scelto) -> si.
- D|caselle: pianoro della curva fuori (K90 <= K scelto) -> si.

## L2: lo scarto del secondo e terzo glifo (parole nuove, bit per glifo; scarto = libri meno vero)

| peso, libri | scarto 2+3 sotto l'automa | errore | scarto 2+3 sotto il trigramma | scarto totale automa | scarto totale trigramma | lettura |
|---|---|---|---|---|---|---|
| P|V21 | 0,1038 | 0,0226 | 0,0427 | 0,3273 | 0,1822 | niente da spiegare (il trigramma non vede scarto nei posti 2+3; per l'automa vale 0,1038) |
| P|M1 | 0,1002 | 0,0335 | 0,1617 | 0,1398 | 0,2674 | in parte (rapporto 0.62) |
| P|E2 | 0,1189 | 0,0234 | 0,2028 | 0,1687 | 0,3384 | in parte (rapporto 0.59) |
| P|W1 | 0,0570 | 0,0326 | 0,1086 | 0,0819 | 0,1926 | niente da spiegare (il trigramma non vede scarto nei posti 2+3; per l'automa vale 0,0570) |
| D|V21 | 0,0616 | 0,0132 | 0,0427 | 0,2230 | 0,1822 | niente da spiegare (il trigramma non vede scarto nei posti 2+3; per l'automa vale 0,0616) |
| D|M1 | 0,0837 | 0,0274 | 0,1617 | 0,1247 | 0,2674 | in parte (rapporto 0.52) |
| D|E2 | 0,1002 | 0,0188 | 0,2028 | 0,1580 | 0,3384 | in parte (rapporto 0.49) |
| D|W1 | 0,0421 | 0,0227 | 0,1086 | 0,0651 | 0,1926 | niente da spiegare (il trigramma non vede scarto nei posti 2+3; per l'automa vale 0,0421) |
| P|sintesi M1 E2 W1 | 0,0920 | 0,0174 | 0,1577 | 0,1301 | 0,2661 | in parte (rapporto 0.58) |
| D|sintesi M1 E2 W1 | 0,0753 | 0,0134 | 0,1577 | 0,1159 | 0,2661 | in parte (rapporto 0.48) |

## L3: il Voynich e' piu' piccolo? (differenza in log2 del numero di stati, gruppo meno Voynich)

| peso, famiglia, gruppo | n | differenza | errore | lettura |
|---|---|---|---|---|
| P|libero|lingue | 8 | 0,415 | 0,307 | simile (entro l'errore) |
| P|libero|cifrari | 21 | -0,549 | 0,392 | simile (entro l'errore) |
| P|libero|Naibbe e Timm-Schinner | 2 | 0,208 | 0,371 | simile (entro l'errore) |
| P|libero|v21 | 2 | 0,000 | 0,307 | simile (entro l'errore) |
| P|libero|M1 | 2 | 0,208 | 0,371 | simile (entro l'errore) |
| P|libero|E2 | 2 | 0,000 | 0,307 | simile (entro l'errore) |
| P|libero|W1 | 2 | 0,000 | 0,307 | simile (entro l'errore) |
| P|libero|cifrario V | 3 | 0,415 | 0,654 | simile (entro l'errore) |
| P|libero|cifrario S | 3 | -0,252 | 0,453 | simile (entro l'errore) |
| P|libero|cifrario N | 3 | 0,415 | 0,307 | simile (entro l'errore) |
| P|libero|cifrario C | 3 | -2,195 | 0,364 | il Voynich e' piu' grande |
| P|libero|cifrario R | 3 | 0,082 | 0,734 | simile (entro l'errore) |
| P|libero|cifrario F | 3 | -0,585 | 0,307 | simile (entro l'errore) |
| P|libero|cifrario P | 3 | -1,723 | 0,337 | il Voynich e' piu' grande |
| D|libero|lingue | 8 | -0,031 | 0,332 | simile (entro l'errore) |
| D|libero|cifrari | 21 | -0,765 | 0,422 | simile (entro l'errore) |
| D|libero|Naibbe e Timm-Schinner | 2 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|v21 | 2 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|M1 | 2 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|E2 | 2 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|W1 | 2 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|cifrario V | 3 | -0,610 | 0,524 | simile (entro l'errore) |
| D|libero|cifrario S | 3 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|cifrario N | 3 | 1,000 | 0,313 | simile (entro l'errore) |
| D|libero|cifrario C | 3 | -1,610 | 0,369 | il Voynich e' piu' grande |
| D|libero|cifrario R | 3 | -3,000 | 0,657 | il Voynich e' piu' grande |
| D|libero|cifrario F | 3 | 0,000 | 0,313 | simile (entro l'errore) |
| D|libero|cifrario P | 3 | -1,138 | 0,342 | il Voynich e' piu' grande |

Riassunto (piu' piccolo solo se P e D concordano):

- libero|lingue: simile (entro l'errore)
- libero|cifrari: simile (entro l'errore)
- libero|Naibbe e Timm-Schinner: simile (entro l'errore)
- libero|v21: simile (entro l'errore)
- libero|M1: simile (entro l'errore)
- libero|E2: simile (entro l'errore)
- libero|W1: simile (entro l'errore)
- libero|cifrario V: simile (entro l'errore)
- libero|cifrario S: simile (entro l'errore)
- libero|cifrario N: simile (entro l'errore)
- libero|cifrario C: il Voynich e' piu' grande
- libero|cifrario R: dipende dal peso (P: simile (entro l'errore); D: il Voynich e' piu' grande)
- libero|cifrario F: simile (entro l'errore)
- libero|cifrario P: il Voynich e' piu' grande

## L4: parole nuove dei libri fuori dalla grammatica del vero

| peso, libri | n | quota sopra il 95-esimo percentile | errore | lettura |
|---|---|---|---|---|
| P|V21 | 10 | 0,072 | 0,001 | zona grigia |
| P|M1 | 10 | 0,073 | 0,001 | zona grigia |
| P|E2 | 10 | 0,078 | 0,002 | zona grigia |
| P|W1 | 10 | 0,064 | 0,001 | zona grigia |
| D|V21 | 10 | 0,061 | 0,001 | zona grigia |
| D|M1 | 10 | 0,073 | 0,001 | zona grigia |
| D|E2 | 10 | 0,080 | 0,002 | zona grigia |
| D|W1 | 10 | 0,065 | 0,001 | zona grigia |

## Taglie di tutti i testi (K scelto con il BIC; per piega fra parentesi; * = K scelto all'ultimo taglio comune a tutte le pieghe: il minimo potrebbe stare oltre)

| testo | P libero | D libero | P caselle | D caselle | trigramma: costo parole nuove |
|---|---|---|---|---|---|
| sint_vero | 8 [8, 8, 8, 8, 8] | — | — | — | 2,897 |
| neg_N1 | 16 [16, 16, 16, 16, 16] | 8 [8, 6, 8, 8, 8] | — | — | 5,022 |
| vero | 24 [32, 32, 24, 24, 24] | 16 [16, 16, 24, 16, 16] | 32 [32, 32, 32, 32, 32] | 32 [32, 32, 32, 24, 24] | 3,479 |
| sint_L4_1 | 4 [4, 4, 4, 4, 4] | — | — | — | 3,086 |
| neg_N2 | 16 [16, 16, 16, 16, 16] | 12 [16, 8, 16, 8, 16] | — | — | 4,341 |
| sint_L4_2 | 6 [6, 6, 6, 6, 4] | — | — | — | 3,109 |
| sint_L8_1 | 8 [8, 8, 8, 8, 8] | — | — | — | 2,780 |
| sint_L8_2 | 12 [8, 12, 12, 8, 8] | — | — | — | 2,631 |
| sint_L16_1 | 12 [12, 12, 12, 12, 12] | — | — | — | 2,974 |
| sint_C6_1 | — | — | 6 [6, 6, 6, 6, 6] | — | 3,362 |
| sint_L16_2 | 16 [16, 16, 16, 16, 16] | — | — | — | 3,376 |
| sint_C6_2 | — | — | 6 [6, 6, 6, 6, 6] | — | 3,453 |
| lingua_latino | 32 [32, 32, 32, 32, 32] | 16 [16, 16, 24, 16, 16] | — | — | 3,535 |
| lingua_latino_nt | 32 [32, 32, 32, 32, 32] | 24 [32, 24, 24, 24, 32] | — | — | 3,451 |
| lingua_inglese | 32 [32, 32, 32, 24, 32] | 12 [12, 12, 12, 16, 8] | — | — | 4,384 |
| lingua_italiano | 32 [32, 32, 32, 32, 24] | 16 [16, 16, 16, 12, 16] | — | — | 3,617 |
| lingua_francese | 32 [32, 32, 32, 32, 32] | 16 [16, 16, 16, 16, 16] | — | — | 3,770 |
| lingua_tedesco | 32 [32, 32, 32, 32, 32] | 16 [16, 16, 16, 16, 16] | — | — | 3,866 |
| lingua_maori | 32 [32, 32, 24, 32, 32] | 12 [12, 12, 12, 12, 12] | — | — | 3,467 |
| lingua_spagnolo | 32 [32, 32, 32, 32, 32] | 16 [16, 16, 12, 12, 16] | — | — | 3,841 |
| nat_ts | 24 [24, 24, 32, 24, 24] | 16 [24, 16, 16, 12, 16] | — | — | 3,400 |
| nat_naibbe | 32 [32, 32, 32, 24, 32] | 16 [16, 16, 12, 16, 16] | — | — | 3,114 |
| cif_V_1_i1 | 64* [48, 48, 48, 64, 64] | 6 [6, 6, 6, 6, 6] | — | — | 5,918 |
| cif_V_3_i1 | 32 [32, 32, 32, 32, 32] | 12 [12, 12, 12, 12, 12] | — | — | 4,609 |
| cif_V_6_i1 | 16 [16, 24, 16, 32, 16] | 16 [16, 16, 16, 16, 16] | — | — | 4,589 |
| cif_S_1_i1 | 32 [32, 32, 32, 32, 32] | 16 [16, 16, 16, 16, 16] | — | — | 3,568 |
| cif_S_2_i1 | 16 [16, 16, 16, 16, 16] | 16 [16, 16, 16, 16, 12] | — | — | 3,677 |
| cif_S_4_i1 | 16 [16, 16, 16, 16, 16] | 16 [16, 12, 16, 12, 16] | — | — | 3,919 |
| cif_N_30_i1 | 32 [32, 32, 32, 32, 32] | 32 [32, 32, 32, 32, 32] | — | — | 3,345 |
| cif_N_150_i1 | 32 [32, 24, 32, 32, 32] | 32* [24, 16, 32, 32, 32] | — | — | 3,451 |
| cif_N_600_i1 | 32 [32, 24, 32, 32, 32] | 32* [32, 32, 32, 16, 32] | — | — | 3,381 |
| cif_C_4_i1 | 4 [4, 4, 6, 4, 4] | 4 [4, 6, 6, 6, 4] | — | — | 4,888 |
| cif_C_16_i1 | 6 [6, 6, 6, 4, 6] | 6 [6, 6, 4, 6, 6] | — | — | 4,977 |
| cif_R_6_i1 | 64* [64, 64, 64, 64, 64] | 1 [1, 1, 1, 1, 1] | — | — | nan |
| cif_R_12_i1 | 16 [16, 32, 32, 32, 16] | 2 [2, 2, 2, 2, 2] | — | — | nan |
| cif_R_24_i1 | 16 [16, 16, 16, 16, 16] | 4 [4, 4, 4, 4, 4] | — | — | nan |
| cif_C_64_i1 | 6 [6, 4, 8, 6, 6] | 6 [6, 6, 6, 6, 6] | — | — | 4,964 |
| cif_F_3p5_i1 | 16 [16, 16, 12, 16, 16] | 16 [12, 12, 12, 16, 16] | — | — | 4,170 |
| cif_F_5p0_i1 | 16 [16, 16, 16, 16, 16] | 16 [16, 16, 16, 16, 16] | — | — | 3,938 |
| cif_P_1_i1 | 8 [8, 8, 12, 6, 8] | 6 [6, 6, 12, 6, 6] | — | — | 4,710 |
| cif_F_7p0_i1 | 16 [16, 16, 16, 16, 24] | 16 [16, 16, 16, 12, 16] | — | — | 3,803 |
| cif_P_5_i1 | 8 [8, 8, 6, 6, 12] | 8 [8, 8, 6, 8, 8] | — | — | 4,724 |
| lib_V21_13 | 24 [24, 32, 32, 24, 32] | 16 [24, 16, 16, 16, 16] | — | — | 3,610 |
| cif_P_25_i1 | 6 [8, 8, 6, 12, 6] | 8 [8, 8, 6, 8, 6] | — | — | 4,661 |
| lib_V21_18 | 24 [32, 32, 24, 24, 24] | 16 [16, 16, 16, 16, 12] | — | — | 3,578 |
| lib_M1_1 | 24 [16, 24, 32, 32, 24] | 16 [16, 16, 16, 16, 16] | — | — | 3,649 |
| lib_M1_6 | 32 [32, 32, 32, 32, 32] | 16 [12, 16, 16, 16, 16] | — | — | 3,608 |
| lib_E2_1 | 24 [16, 24, 24, 24, 24] | 16 [16, 16, 16, 16, 16] | — | — | 3,664 |
| lib_E2_6 | 24 [32, 32, 24, 24, 24] | 16 [16, 16, 16, 16, 16] | — | — | 3,667 |
| lib_W1_1 | 24 [32, 32, 24, 24, 24] | 16 [16, 16, 16, 16, 16] | — | — | 3,578 |
| lib_W1_6 | 24 [24, 24, 24, 24, 24] | 16 [16, 16, 12, 16, 24] | — | — | 3,563 |
