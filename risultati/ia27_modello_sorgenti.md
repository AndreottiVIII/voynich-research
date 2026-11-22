# IA27 (ia27) — Il modello a sorgenti latenti

Preregistrazione: `preregistrazioni/ia27.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.

## Bit per segno fuori piega (media ± errore sulle 5 pieghe)

| versione | fuori (bit/segno) | fuori (bit/parola) | validazione (bit/segno) | EM: passi, verosimiglianza sale |
|---|---|---|---|---|
| pieno | 2,078 ± 0,034 | 10,86 ± 0,10 | 2,157 ± 0,071 | 42,8, sì |
| senza_R | 2,082 ± 0,034 | 10,88 ± 0,10 | 2,161 ± 0,071 | 42,0, sì |
| senza_P | 2,086 ± 0,034 | 10,90 ± 0,10 | 2,163 ± 0,071 | 40,4, sì |
| senza_S | 2,106 ± 0,036 | 11,01 ± 0,10 | 2,205 ± 0,075 | 31,2, sì |
| senza_copia | 2,091 ± 0,034 | 10,93 ± 0,10 | 2,168 ± 0,071 | 39,6, sì |
| nucleo_piatto | 2,079 ± 0,034 | 10,87 ± 0,10 | 2,157 ± 0,071 | 42,6, sì |
| senza_contatto | 2,125 ± 0,032 | 11,12 ± 0,10 | 2,192 ± 0,067 | 42,6, sì |
| senza_ritocco | 2,083 ± 0,034 | 10,89 ± 0,10 | 2,162 ± 0,071 | 41,6, sì |
| con_frequenza | 2,074 ± 0,035 | 10,84 ± 0,10 | 2,153 ± 0,071 | 42,4, sì |
| solo_lessico | 2,176 ± 0,033 | 11,39 ± 0,09 | 2,266 ± 0,071 | 10,0, sì |
| copia_con_contatto | 2,076 ± 0,035 | 10,85 ± 0,10 | 2,155 ± 0,071 | 42,4, sì |
| ritocco_con_contatto | 2,078 ± 0,034 | 10,86 ± 0,10 | 2,156 ± 0,071 | 42,6, sì |
| bigramma di parole (conteggi) | 2,231 ± 0,036 | 11,70 ± 0,11 | 2,320 ± 0,075 | — |

### Contro le reti (stesse pieghe: differenza per piega, modello pieno meno rete)

| rete | bit/segno fuori | pieno - rete | entro 0,10 | sotto la rete |
|---|---|---|---|---|
| ia07 (GRU) | 1,948 ± 0,030 | 0,130 ± 0,009 | NO | NO |
| M1 (ia20) | 1,940 ± 0,029 | 0,138 ± 0,008 | NO | NO |
| M2 (ia20) | 1,924 ± 0,027 | 0,154 ± 0,011 | NO | NO |
| M3 (ia20) | 1,929 ± 0,027 | 0,149 ± 0,012 | NO | NO |
| M4 (ia20) | 1,924 ± 0,030 | 0,154 ± 0,005 | NO | NO |
| M5 (ia20) | 1,926 ± 0,033 | 0,152 ± 0,005 | NO | NO |
| E0 (ia22) | 1,942 ± 0,030 | 0,136 ± 0,007 | NO | NO |
| E1 (ia22) | 1,938 ± 0,029 | 0,140 ± 0,005 | NO | NO |
| E2 (ia22) | 1,951 ± 0,029 | 0,127 ± 0,010 | NO | NO |
| E3 (ia22) | 1,950 ± 0,031 | 0,128 ± 0,007 | NO | NO |

### Ablazioni (versione meno pieno, stesse pieghe)

| versione | bit/segno in piu' | bit/parola in piu' |
|---|---|---|
| senza_R | 0,004 ± 0,000 | 0,022 ± 0,001 |
| senza_P | 0,007 ± 0,000 | 0,041 ± 0,002 |
| senza_S | 0,028 ± 0,004 | 0,151 ± 0,019 |
| senza_copia | 0,012 ± 0,001 | 0,068 ± 0,003 |
| nucleo_piatto | 0,001 ± 0,000 | 0,003 ± 0,000 |
| senza_contatto | 0,047 ± 0,003 | 0,258 ± 0,020 |
| senza_ritocco | 0,005 ± 0,000 | 0,026 ± 0,002 |
| con_frequenza | -0,004 ± 0,000 | -0,020 ± 0,002 |
| solo_lessico | 0,098 ± 0,003 | 0,532 ± 0,017 |
| copia_con_contatto | -0,002 ± 0,000 | -0,011 ± 0,002 |
| ritocco_con_contatto | -0,000 ± 0,000 | -0,001 ± 0,000 |
| bigramma di parole (conteggi) | 0,153 ± 0,003 | — |

## Quote delle sorgenti (stima sul testo intero; intervalli al 95% sui ricampionamenti delle pagine)

| sorgente | quota (tutte le lingue) | intervallo | A | B |
|---|---|---|---|---|
| L lessico generale | 0,2216 | [0,1859; 0,2631] | 0,1349 | 0,2577 |
| S lessico di sezione | 0,4024 | [0,3515; 0,4613] | 0,4285 | 0,3992 |
| F forma (parola inventata) | 0,2800 | [0,2613; 0,2939] | 0,3439 | 0,2444 |
| R riga (in corso o sopra) | 0,0341 | [0,0297; 0,0386] | 0,0450 | 0,0288 |
| P resto della pagina | 0,0619 | [0,0535; 0,0713] | 0,0477 | 0,0699 |

R + P (ricopiatura): intervallo [0,0839; 0,1088]. Ritocchi di R (uguale, cambia, aggiunge, toglie): stima 0,636, 0,108, 0,069, 0,186; intervalli [0,577; 0,682] [0,082; 0,155] [0,047; 0,090] [0,149; 0,219].

Nucleo di R (quota delle scelte di ricopiatura per classe di distanza):
- riga in corso, 1 parole prima: 0,139 [0,112; 0,167]
- riga in corso, 2 parole prima: 0,117 [0,092; 0,142]
- riga in corso, 3 parole prima: 0,066 [0,045; 0,092]
- riga in corso, 4 parole prima: 0,057 [0,040; 0,079]
- riga in corso, 5 parole prima: 0,025 [0,016; 0,039]
- riga in corso, 6-7 parole prima: 0,035 [0,021; 0,048]
- riga in corso, 8-9 parole prima: 0,006 [0,004; 0,010]
- riga in corso, 10-12 parole prima: 0,003 [0,002; 0,006]
- riga in corso, 13-16 parole prima: 0,001 [0,000; 0,003]
- riga in corso, 17-22 parole prima: 0,000 [0,000; 0,000]
- riga in corso, 23-30 parole prima: 0,000 [0,000; 0,000]
- riga in corso, 31 o piu' parole prima: 0,000 [0,000; 0,000]
- riga sopra, 1 parole prima: 0,002 [0,001; 0,004]
- riga sopra, 2 parole prima: 0,010 [0,006; 0,016]
- riga sopra, 3 parole prima: 0,027 [0,016; 0,039]
- riga sopra, 4 parole prima: 0,033 [0,020; 0,047]
- riga sopra, 5 parole prima: 0,058 [0,038; 0,088]
- riga sopra, 6-7 parole prima: 0,128 [0,102; 0,157]
- riga sopra, 8-9 parole prima: 0,096 [0,067; 0,125]
- riga sopra, 10-12 parole prima: 0,129 [0,095; 0,160]
- riga sopra, 13-16 parole prima: 0,049 [0,034; 0,062]
- riga sopra, 17-22 parole prima: 0,015 [0,008; 0,025]
- riga sopra, 23-30 parole prima: 0,003 [0,001; 0,006]
- riga sopra, 31 o piu' parole prima: 0,002 [0,000; 0,005]

Nucleo di P: 2 righe sopra 0,200; 3 righe sopra 0,128; 4 righe sopra 0,078; 5-6 righe sopra 0,154; 7 o piu' righe sopra 0,439.

Informazione del contatto (bit), stima sul testo intero: 0,3265. L'intervallo dei ricampionamenti ([0,3108; 0,3574]) e' spostato in alto dalle pagine ripetute e non si legge: il contatto si legge dai bit in piu' della versione senza contatto.

Con o senza la sorgente di sezione S: la quota R+P cambia di 0,0372 [0,0275; 0,0474] (stesse estrazioni; 200).

Versione con_frequenza: peso della classe di frequenza della parola ricopiata (20 piu frequenti, fino alla 200-esima, altre), stima sul testo intero: R 2,00 1,30 0,27, P 1,78 1,46 0,23; rapporto rare/frequenti di R nelle 5 pieghe e nel testo intero: 0,14 0,14 0,14 0,12 0,14 0,14.
Rapporto fra il peso di una parola vicina (riga in corso, 1-3 parole prima) e di una lontana (riga sopra, 13 parole o piu): [2,16; 3,09].

## Letture del modello

- strumento_valido: negativo_fra_pagine True, positivo_forza_media True, positivo_forza_debole True, autocoerenza False, nota le quote si leggono come misure solo se il negativo e il positivo di forza media riescono; se la prova di autocoerenza fallisce sono limiti alti
- R_riga: presente
- P_pagina: presente
- nucleo_cala_con_la_distanza: si
- eco_e_vocabolario_di_sezione: in parte era vocabolario di sezione
- si_ricopiano: soprattutto parole frequenti
- contatto: il contatto serve (senza, piu bit)
- contro_le_reti: ia07 (GRU) oltre 0,10 bit dalla rete, M1 (ia20) oltre 0,10 bit dalla rete, M2 (ia20) oltre 0,10 bit dalla rete, M3 (ia20) oltre 0,10 bit dalla rete, M4 (ia20) oltre 0,10 bit dalla rete, M5 (ia20) oltre 0,10 bit dalla rete, E0 (ia22) oltre 0,10 bit dalla rete, E1 (ia22) oltre 0,10 bit dalla rete, E2 (ia22) oltre 0,10 bit dalla rete, E3 (ia22) oltre 0,10 bit dalla rete

## Controlli del modello

- Positivo, forza debole (R 0,006, P 0,004 veri): R stimata 0,0094 0,0072 0,0088 0,0086 0,0086, P stimata 0,0110 0,0110 0,0091 0,0106 0,0095; ritrovato in 4 semi su 5 (soglia 4): sì. Per criterio: quota_R 5, quota_P 5, ritocchi 4, nucleo 5, contatto 5, guadagno_visto 5. Guadagno di copia 0,039 0,046 0,046 0,043 0,040 bit per parola.
- Positivo, forza media (R 0,012, P 0,008 veri): R stimata 0,0156 0,0157 0,0158 0,0159 0,0169, P stimata 0,0152 0,0121 0,0127 0,0146 0,0128; ritrovato in 5 semi su 5 (soglia 4): sì. Per criterio: quota_R 5, quota_P 5, ritocchi 5, nucleo 5, contatto 5, guadagno_visto 5. Guadagno di copia 0,092 0,113 0,095 0,105 0,088 bit per parola.
- Positivo, forza forte (R 0,030, P 0,020 veri): R stimata 0,0346 0,0337 0,0340 0,0332 0,0348, P stimata 0,0294 0,0259 0,0273 0,0269 0,0261; ritrovato in 5 semi su 5 (soglia 4): sì. Per criterio: quota_R 5, quota_P 5, ritocchi 5, nucleo 5, contatto 5, guadagno_visto 5. Guadagno di copia 0,239 0,238 0,255 0,236 0,238 bit per parola.
- Negativo fra_pagine: quota R 0,0078 0,0035 0,0077, quota P 0,0241 0,0217 0,0272, guadagno di copia 0,011 0,016 0,020 bit per parola; riuscito: sì (soglie R 0.02, P 0.05, guadagno 0.08).
- Negativo dentro_pagina: quota R 0,0237 0,0208 0,0207, quota P 0,1093 0,1127 0,1126, guadagno di copia 0,060 0,068 0,060 bit per parola (descrittivo).
- Negativo righe_fra_pagine: quota R 0,0195 0,0212 0,0185, quota P 0,0176 0,0169 0,0210, guadagno di copia 0,021 0,018 0,022 bit per parola (descrittivo).
- Autocoerenza (il modello scrive, lo stesso metodo rilegge): quote vere R 0,0391 P 0,0711; sul testo scritto R 0,0469 0,0462 P 0,0812 0,0792; guadagno di copia sul vero 0,058 e sullo scritto 0,480 0,391 bit per parola (rapporto 8,23 6,72, soglia 1.5) → NO.
- Latino nella disposizione: quota R 0,0122, P 0,0550, guadagno di copia 0,179 bit per parola, ritocchi di R 0,814, 0,105, 0,037, 0,045 → sì.

## Dove spende i bit (fuori piega, tutte le pieghe)

- pieno: parole nuove: 27,1% dei bit (20,05 bit per parola, 5334 parole); note con una parola uguale o a un ritocco gia scritta in pagina: 50,2% dei bit (8,64 bit per parola, 22889 parole); note senza: 18,7% dei bit (11,12 bit per parola, 6640 parole); fine parola (spazio o fine riga): 3,9% dei bit (0,44 bit per parola, 34863 parole).
- senza_copia: parole nuove: 27,2% dei bit (20,19 bit per parola, 5334 parole); note con una parola uguale o a un ritocco gia scritta in pagina: 50,5% dei bit (8,75 bit per parola, 22889 parole); note senza: 18,4% dei bit (10,98 bit per parola, 6640 parole); fine parola (spazio o fine riga): 3,9% dei bit (0,44 bit per parola, 34863 parole).
- solo_lessico: parole nuove: 26,6% dei bit (20,58 bit per parola, 5334 parole); note con una parola uguale o a un ritocco gia scritta in pagina: 51,4% dei bit (9,26 bit per parola, 22889 parole); note senza: 18,3% dei bit (11,34 bit per parola, 6640 parole); fine parola (spazio o fine riga): 3,8% dei bit (0,44 bit per parola, 34863 parole).

## Controlli dei giudici

- Giudici del paper, positivo: AUC 0,988 → sì. Negativo: 0,506 e 0,503 → sì.
- K: positivo parole 0,982, e192 0,935 → sì; negativo 0,499 → sì; vede il v21 0,766 → sì.

## Libri scritti dal modello: giudici (AUC, piu' basso = piu' vicino al vero)

| libri | n | e231 | e266 | K | A (riportato) |
|---|---|---|---|---|---|
| pieno | 10 | 0,996 ± 0,000 | 1,000 ± 0,000 | 0,945 ± 0,001 | 0,985 ± 0,000 |
| copia_con_contatto | 5 | 0,994 ± 0,001 | 0,999 ± 0,000 | 0,947 ± 0,002 | 0,985 ± 0,001 |
| ritocco_con_contatto | 5 | 0,995 ± 0,001 | 1,000 ± 0,000 | 0,945 ± 0,003 | 0,986 ± 0,000 |
| senza_copia | 5 | 0,997 ± 0,001 | 1,000 ± 0,000 | 0,952 ± 0,001 | 0,981 ± 0,001 |
| nucleo_piatto | 5 | 0,995 ± 0,001 | 0,999 ± 0,000 | 0,947 ± 0,002 | 0,984 ± 0,001 |
| M1 | 10 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 | 0,675 ± 0,009 |
| M5 | 10 | 0,782 ± 0,008 | 0,799 ± 0,007 | 0,797 ± 0,007 | 0,707 ± 0,006 |
| v21 | 10 | 0,554 ± 0,004 (paper) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | — |

## Struttura (media ± errore sui libri)

| testo | copia netta (bit per parola) | quota locale Λ | contatto ultimo→primo glifo | ordine delle famiglie D | G9 vocabolario della pagina | bordi: inizio riga | bordi: fine riga | quota di parole nuove | costo di forma delle parole nuove (bit per glifo) |
|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1138 | 0,2074 | 0,1884 | 0,1444 | 0,0402 | 0,0790 | 0,0475 | 0,1530 | 3,4786 |
| pieno (10 libri) | 0,4143 ± 0,0064 | 0,1679 ± 0,0096 | 0,1729 ± 0,0012 | 0,0478 ± 0,0008 | 0,0132 ± 0,0001 | 0,0639 ± 0,0003 | 0,0114 ± 0,0004 | 0,1826 ± 0,0005 | 3,4881 ± 0,0028 |
| copia_con_contatto (5 libri) | 0,5003 ± 0,0054 | 0,1193 ± 0,0137 | 0,1894 ± 0,0017 | 0,0460 ± 0,0013 | 0,0132 ± 0,0001 | 0,0717 ± 0,0005 | 0,0113 ± 0,0004 | 0,1864 ± 0,0007 | 3,4876 ± 0,0075 |
| ritocco_con_contatto (5 libri) | 0,4199 ± 0,0078 | 0,1524 ± 0,0100 | 0,1730 ± 0,0004 | 0,0481 ± 0,0017 | 0,0132 ± 0,0002 | 0,0657 ± 0,0008 | 0,0104 ± 0,0003 | 0,1862 ± 0,0014 | 3,4869 ± 0,0056 |
| senza_copia (5 libri) | 0,0040 ± 0,0005 | 0,0094 ± 0,1933 | 0,1920 ± 0,0021 | 0,0503 ± 0,0014 | 0,0115 ± 0,0001 | 0,0713 ± 0,0006 | 0,0109 ± 0,0001 | 0,1650 ± 0,0006 | 3,3822 ± 0,0037 |
| nucleo_piatto (5 libri) | 0,4177 ± 0,0103 | 0,1227 ± 0,0236 | 0,1734 ± 0,0032 | 0,0463 ± 0,0015 | 0,0132 ± 0,0001 | 0,0635 ± 0,0005 | 0,0110 ± 0,0005 | 0,1836 ± 0,0002 | 3,4826 ± 0,0048 |
| M1 (10 libri) | 0,0360 ± 0,0016 | 0,0538 ± 0,0368 | 0,1891 ± 0,0025 | 0,1486 ± 0,0017 | 0,0245 ± 0,0006 | 0,0837 ± 0,0015 | 0,0457 ± 0,0007 | 0,1472 ± 0,0015 | 3,7459 ± 0,0062 |
| M5 (10 libri) | 0,1416 ± 0,0059 | 0,2362 ± 0,0111 | 0,1578 ± 0,0015 | 0,1078 ± 0,0014 | 0,0316 ± 0,0002 | 0,0760 ± 0,0017 | 0,0417 ± 0,0006 | 0,1725 ± 0,0030 | 3,6971 ± 0,0097 |
| V21 (10 libri) | 0,0548 ± 0,0016 | 0,0906 ± 0,0177 | 0,1850 ± 0,0011 | 0,0898 ± 0,0017 | 0,0392 ± 0,0005 | 0,0777 ± 0,0009 | 0,0414 ± 0,0007 | 0,1430 ± 0,0012 | 3,6608 ± 0,0053 |

## Letture preregistrate

- Validita' dei giudici: paper sì, K sì.
  - pieno contro il v21: più lontano dal vero del v21 (e231 più lontano; e266 più lontano; K più lontano).
  - copia_con_contatto contro il v21: più lontano dal vero del v21 (e231 più lontano; e266 più lontano; K più lontano).
  - ritocco_con_contatto contro il v21: più lontano dal vero del v21 (e231 più lontano; e266 più lontano; K più lontano).
  - senza_copia contro il v21: più lontano dal vero del v21 (e231 più lontano; e266 più lontano; K più lontano).
  - nucleo_piatto contro il v21: più lontano dal vero del v21 (e231 più lontano; e266 più lontano; K più lontano).
- **Eco e legame insieme (copia netta, Λ, contatto, D tutti "al vero"):** nessuna versione.
  - pieno: eco al vero NO, legame al vero NO (copia_netta NO, lam NO, contatto NO, D NO).
  - copia_con_contatto: eco al vero NO, legame al vero NO (copia_netta NO, lam NO, contatto sì, D NO).
  - ritocco_con_contatto: eco al vero NO, legame al vero NO (copia_netta NO, lam NO, contatto NO, D NO).
  - senza_copia: eco al vero NO, legame al vero NO (copia_netta NO, lam sì, contatto sì, D NO).
  - nucleo_piatto: eco al vero NO, legame al vero NO (copia_netta NO, lam NO, contatto NO, D NO).
  - M1: eco al vero NO, legame al vero sì (copia_netta NO, lam NO, contatto sì, D sì).
  - M5: eco al vero NO, legame al vero NO (copia_netta NO, lam NO, contatto NO, D NO).
- **Che cosa nessuna versione porta al vero:** copia netta (bit per parola), ordine delle famiglie D, G9 vocabolario della pagina, bordi: inizio riga, bordi: fine riga, quota di parole nuove.

## Copia a memoria (soglie severe di ia20)

| | 5-grammi | 3-grammi | righe intere | parole nuove |
|---|---|---|---|---|
| pieno | 0,0000 ± 0,0000 | 0,0011 ± 0,0001 | 0,0000 ± 0,0000 | 0,1846 ± 0,0005 |
| copia_con_contatto | 0,0000 ± 0,0000 | 0,0012 ± 0,0001 | 0,0000 ± 0,0000 | 0,1884 ± 0,0007 |
| ritocco_con_contatto | 0,0000 ± 0,0000 | 0,0011 ± 0,0001 | 0,0000 ± 0,0000 | 0,1882 ± 0,0014 |
| senza_copia | 0,0000 ± 0,0000 | 0,0012 ± 0,0001 | 0,0000 ± 0,0000 | 0,1668 ± 0,0006 |
| nucleo_piatto | 0,0000 ± 0,0000 | 0,0012 ± 0,0001 | 0,0000 ± 0,0000 | 0,1856 ± 0,0003 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
- pieno: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO.
- copia_con_contatto: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO.
- ritocco_con_contatto: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO.
- senza_copia: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO.
- nucleo_piatto: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO.

## Tempi (minuti per lavoro)

- stima: 72 lavori, media 0.68, massimo 1.04, totale 48.8.
- bigramma: 5 lavori, media 0.24, massimo 0.29, totale 1.2.
- boot: 20 lavori, media 4.53, massimo 5.17, totale 90.7.
- ctrl: 27 lavori, media 1.14, massimo 1.83, totale 30.8.
- libro: 30 lavori, media 0.69, massimo 0.84, totale 20.7.
- K: 5 lavori, media 0.51, massimo 0.62, totale 2.5.
- M: 61 lavori, media 0.79, massimo 0.99, totale 48.3.
- D: 5 lavori, media 0.42, massimo 0.47, totale 2.1.
