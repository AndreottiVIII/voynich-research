# IA23 (ia23) — Eco da tutta la pagina, legame fra parole e vocabolario della pagina

Preregistrazione: `preregistrazioni/ia23.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, pagina pagina-1, echi echi-1, gradini gradini-1, sklearn 1.9.1.

## Controlli dei giudici

- Giudici del paper, positivo: AUC 0,988, soglia ≥ 0,95 → sì. Negativo: giudice 1 0,506, giudice 2 0,503 → sì.
- K, positivo: parole 0,982, e192 0,935 → sì. Negativo: 0,499 → sì. K vede il v21 (AUC 0,766) → sì.
- A (riportato, non decide), positivo: parole 0,986, e192 0,958 → sì. Negativo: 0,484 → sì.

## Controlli di sensibilità (testi sintetici)

Testo con tema di pagina, eco locale e contatto piantati insieme (fogli tenuti fuori della piega 0): tasso di eco locale 0,337, quota del glifo iniziale preferito 0,416, contatto 0,628; tasso lontano condizionato 0,161 (con le righe rimescolate 0,059, eccesso di tema piantato 0,102).

| modello | guadagno su M1 (bit/segno) | eco locale scritta / piantata | tema scritto / piantato (eccesso) | glifo preferito scritto / piantato | contatto scritto / piantato | eco ok | tema ok | legame ok | riuscito |
|---|---|---|---|---|---|---|---|---|---|
| M1 | 0,000 | 0,312 | 0,027 | 0,941 | 0,880 | NO | NO | sì | NO |
| E1 | 0,192 | 0,746 | -0,075 | 1,044 | 1,002 | sì | NO | sì | NO |
| E2 | 0,397 | 0,815 | 0,014 | 1,171 | 1,228 | sì | NO | sì | NO |
| E3 | 0,402 | 1,053 | -0,020 | 0,946 | 0,857 | sì | NO | sì | NO |
| P1 | 0,251 | 0,615 | 0,914 | 0,854 | 0,862 | NO | sì | sì | NO |
| P2 | 0,497 | 0,865 | 1,028 | 1,145 | 0,984 | sì | sì | sì | sì |
| P3 | 0,509 | 0,793 | 1,144 | 1,038 | 0,981 | sì | sì | sì | sì |

Il controllo vede la differenza sul tema (P2 impara il tema, E2 di ia22 no): sì.

Testo senza niente di piantato: E2: guadagno su M1 -0,002, massa di copia 0,008 → sì; P1: guadagno su M1 0,015, massa di copia — → sì; P2: guadagno su M1 -0,005, massa di copia 0,037 → sì; P3: guadagno su M1 0,019, massa di copia 0,015 → sì.

## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)

| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa di copia | minuti per modello |
|---|---|---|---|---|---|---|---|
| P1 | 665518 | 1,953 ± 0,030 | 1,916 ± 0,021 | 14,2 | 0 | — | 14.5 |
| P2 | 767361 | 1,966 ± 0,033 | 1,934 ± 0,019 | 12,9 | 0 | 0,168 | 20.2 |
| P3 | 767363 | 1,966 ± 0,031 | 1,938 ± 0,020 | 12,4 | 0 | 0,187 | 16.9 |
| M1 (cache) | — | 1,965 ± 0,031 | 1,940 ± 0,019 | — | — | — | — |
| M5 (cache) | — | 1,960 ± 0,032 | 1,926 ± 0,022 | — | — | — | — |
| E1 (cache) | — | 1,962 ± 0,030 | 1,938 ± 0,020 | — | — | — | — |
| E2 (cache) | — | 1,967 ± 0,031 | 1,951 ± 0,019 | — | — | — | — |
| E3 (cache) | — | 1,966 ± 0,030 | 1,950 ± 0,021 | — | — | — | — |

Numeri imparati (medie): P1 {"distanza": [1.554, 1.81, 1.903, 1.549, 1.009, 0.102], "occorrenze": [0.033, 0.955, 1.112, 1.447], "frequenza": [0.0, 0.328, 0.72, 0.625, 0.478, 0.662, 0.412], "beta": [[0.576, 0.412, 0.361, 0.0], [0.0, 0.247, 0.35, 0.0], [0.066, 0.024, 0.064, 0.0], [0.0, 0.276, 0.17, 0.0], [0.0, 0.059, 0.164, 0.0]]}; P2 {"distanza": [0.291, 0.445, 0.308, 0.24, -0.04, -0.463], "occorrenze": [-0.479, -0.066, 0.194, 0.602], "frequenza": [0.0, -0.557, -0.352, 0.077, 0.434, 0.068, 0.072], "beta": [-2.02, -4.813, -4.948, -4.149], "gamma": [0.15075999999999998, 0.0058037574036136266]}; P3 {"distanza": [0.353, 0.478, 0.35, 0.255, -0.047, -0.495], "occorrenze": [-0.487, -0.047, 0.202, 0.616], "frequenza": [0.0, -0.532, -0.31, 0.109, 0.425, 0.056, 0.059], "beta": [-1.873, -4.823, -4.886, -3.937, -4.532, -4.82, -4.587]}.

## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)

| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |
|---|---|---|---|---|---|
| M1 | 10 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 | 0,675 ± 0,009 |
| E1 | 10 | 0,820 ± 0,015 | 0,870 ± 0,008 | 0,787 ± 0,006 | 0,693 ± 0,014 |
| E2 | 10 | 0,801 ± 0,012 | 0,864 ± 0,004 | 0,797 ± 0,007 | 0,695 ± 0,007 |
| E3 | 10 | 0,798 ± 0,008 | 0,836 ± 0,005 | 0,794 ± 0,008 | 0,724 ± 0,014 |
| M5 | 10 | 0,782 ± 0,008 | 0,799 ± 0,007 | 0,797 ± 0,007 | 0,707 ± 0,006 |
| P1 | 10 | 0,805 ± 0,007 | 0,820 ± 0,006 | 0,811 ± 0,007 | 0,771 ± 0,003 |
| P2 | 10 | 0,791 ± 0,005 | 0,860 ± 0,007 | 0,829 ± 0,006 | 0,769 ± 0,009 |
| P3 | 10 | 0,803 ± 0,008 | 0,837 ± 0,007 | 0,823 ± 0,009 | 0,765 ± 0,009 |
| v21 | 10 | 0,554 ± 0,004 (paper) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | 0,746 ± 0,005 |

Repliche diverse (più di 2 errori): M1: e231 NO, e266 NO; E1: e231 sì, e266 sì; E2: e231 sì, e266 NO; E3: e231 NO, e266 NO; M5: e231 NO, e266 NO; P1: e231 NO, e266 NO; P2: e231 NO, e266 sì; P3: e231 NO, e266 NO.

## Struttura (media ± errore standard sui libri)

| testo | copia netta (bit per parola) | quota locale Λ | contatto ultimo→primo glifo | ordine delle famiglie D | G9 vocabolario della pagina | bordi: inizio riga | bordi: fine riga | quota di parole nuove | costo di forma delle parole nuove (bit per glifo) |
|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1138 | 0,2074 | 0,1884 | 0,1444 | 0,0402 | 0,0790 | 0,0475 | 0,1530 | 3,4786 |
| M1 (10 libri) | 0,0360 ± 0,0016 | 0,0538 ± 0,0368 | 0,1891 ± 0,0025 | 0,1486 ± 0,0017 | 0,0245 ± 0,0006 | 0,0837 ± 0,0015 | 0,0457 ± 0,0007 | 0,1472 ± 0,0015 | 3,7459 ± 0,0062 |
| E1 (10 libri) | 0,1014 ± 0,0045 | 0,3799 ± 0,0250 | 0,1732 ± 0,0033 | 0,1488 ± 0,0015 | 0,0281 ± 0,0002 | 0,0815 ± 0,0017 | 0,0454 ± 0,0019 | 0,1411 ± 0,0008 | 3,7235 ± 0,0061 |
| E2 (10 libri) | 0,1134 ± 0,0079 | 0,3605 ± 0,0150 | 0,1796 ± 0,0083 | 0,1432 ± 0,0081 | 0,0259 ± 0,0007 | 0,0803 ± 0,0012 | 0,0449 ± 0,0006 | 0,1460 ± 0,0023 | 3,8170 ± 0,0136 |
| E3 (10 libri) | 0,1103 ± 0,0034 | 0,4101 ± 0,0183 | 0,1761 ± 0,0016 | 0,1490 ± 0,0029 | 0,0262 ± 0,0006 | 0,0776 ± 0,0012 | 0,0430 ± 0,0008 | 0,1531 ± 0,0026 | 3,7469 ± 0,0042 |
| M5 (10 libri) | 0,1416 ± 0,0059 | 0,2362 ± 0,0111 | 0,1578 ± 0,0015 | 0,1078 ± 0,0014 | 0,0316 ± 0,0002 | 0,0760 ± 0,0017 | 0,0417 ± 0,0006 | 0,1725 ± 0,0030 | 3,6971 ± 0,0097 |
| P1 (10 libri) | 0,1456 ± 0,0082 | 0,1008 ± 0,0106 | 0,1867 ± 0,0046 | 0,1395 ± 0,0029 | 0,0339 ± 0,0006 | 0,0841 ± 0,0013 | 0,0469 ± 0,0005 | 0,1524 ± 0,0012 | 3,7797 ± 0,0104 |
| P2 (10 libri) | 0,1741 ± 0,0082 | 0,2074 ± 0,0106 | 0,1600 ± 0,0038 | 0,1271 ± 0,0052 | 0,0232 ± 0,0008 | 0,0815 ± 0,0007 | 0,0477 ± 0,0010 | 0,1659 ± 0,0006 | 3,8069 ± 0,0267 |
| P3 (10 libri) | 0,2280 ± 0,0075 | 0,2396 ± 0,0060 | 0,1861 ± 0,0053 | 0,1320 ± 0,0017 | 0,0258 ± 0,0002 | 0,0815 ± 0,0016 | 0,0453 ± 0,0014 | 0,1702 ± 0,0018 | 3,7989 ± 0,0425 |
| V21 (10 libri) | 0,0548 ± 0,0016 | 0,0906 ± 0,0177 | 0,1850 ± 0,0011 | 0,0898 ± 0,0017 | 0,0392 ± 0,0005 | 0,0777 ± 0,0009 | 0,0414 ± 0,0007 | 0,1430 ± 0,0012 | 3,6608 ± 0,0053 |

## Letture preregistrate

- Validità: giudici del paper sì, K sì, A sì; sensibilità: P1 NO, P2 sì, P3 sì; il controllo vede la differenza sul tema: sì; controlli della fase 0: NO.
- Scambio visto nel testo sintetico (eco imparata ma legame piantato perso): nessun tipo.

### L1 e L1b: eco, legame e vocabolario della pagina "al vero"?

**L1, imitatori con copia netta, Λ, contatto e D tutti al vero: nessuno.** **L1b, anche G9 al vero: nessuno.**

| tipo | copia netta | Λ | contatto | D | G9 | eco al vero | legame al vero | L1 (4 misure) | L1b (+ G9) |
|---|---|---|---|---|---|---|---|---|---|
| vero | 0,114 | 0,207 | 0,188 | 0,144 | 0,040 | | | | |
| M1 | 0,036 | 0,054 | 0,189 ✓ | 0,149 ✓ | 0,025 | NO | sì | NO | NO |
| E1 | 0,101 | 0,380 | 0,173 | 0,149 ✓ | 0,028 | NO | NO | NO | NO |
| E2 | 0,113 ✓ | 0,360 | 0,180 ✓ | 0,143 ✓ | 0,026 | NO | sì | NO | NO |
| E3 | 0,110 ✓ | 0,410 | 0,176 | 0,149 ✓ | 0,026 | NO | NO | NO | NO |
| M5 | 0,142 | 0,236 | 0,158 | 0,108 | 0,032 | NO | NO | NO | NO |
| P1 | 0,146 | 0,101 | 0,187 ✓ | 0,139 ✓ | 0,034 | NO | sì | NO | NO |
| P2 | 0,174 | 0,207 ✓ | 0,160 | 0,127 | 0,023 | NO | NO | NO | NO |
| P3 | 0,228 | 0,240 | 0,186 ✓ | 0,132 | 0,026 | NO | NO | NO | NO |

### L2: ogni P contro l'E corrispondente di ia22 (bersagli: Λ e G9)

| confronto | lettura | misure corrette | misure rotte | sensibilità |
|---|---|---|---|---|
| P1 contro E1 | **corregge ma rompe** | quota locale Λ, contatto ultimo→primo glifo, G9 vocabolario della pagina, quota di parole nuove, giudice 2 (e266) | copia netta (bit per parola), costo di forma delle parole nuove (bit per glifo), giudice K | NON provata (con riserva) |
| P2 contro E2 | **corregge ma rompe** | quota locale Λ, bordi: fine riga | copia netta (bit per parola), contatto ultimo→primo glifo, G9 vocabolario della pagina, quota di parole nuove, giudice K | provata |
| P3 contro E3 | **corregge ma rompe** | quota locale Λ | copia netta (bit per parola), ordine delle famiglie D, quota di parole nuove, giudice K | provata |

### L3: contro il v21

- **Tipo migliore (AUC media di e231, e266, K): M5.**
  - M1: più lontano dal vero del v21 (e231 più lontano (diff. 0,231 ± 0,010); e266 più lontano (diff. 0,240 ± 0,008); K uguale entro l'errore (diff. 0,007 ± 0,007)).
  - E1: più lontano dal vero del v21 (e231 più lontano (diff. 0,266 ± 0,016); e266 più lontano (diff. 0,269 ± 0,009); K più lontano (diff. 0,020 ± 0,008)).
  - E2: più lontano dal vero del v21 (e231 più lontano (diff. 0,247 ± 0,012); e266 più lontano (diff. 0,263 ± 0,007); K più lontano (diff. 0,031 ± 0,009)).
  - E3: più lontano dal vero del v21 (e231 più lontano (diff. 0,244 ± 0,009); e266 più lontano (diff. 0,235 ± 0,007); K più lontano (diff. 0,028 ± 0,009)).
  - M5: più lontano dal vero del v21 (e231 più lontano (diff. 0,228 ± 0,009); e266 più lontano (diff. 0,198 ± 0,009); K più lontano (diff. 0,031 ± 0,008)).
  - P1: più lontano dal vero del v21 (e231 più lontano (diff. 0,251 ± 0,008); e266 più lontano (diff. 0,219 ± 0,008); K più lontano (diff. 0,045 ± 0,009)).
  - P2: più lontano dal vero del v21 (e231 più lontano (diff. 0,237 ± 0,007); e266 più lontano (diff. 0,259 ± 0,009); K più lontano (diff. 0,063 ± 0,007)).
  - P3: più lontano dal vero del v21 (e231 più lontano (diff. 0,249 ± 0,009); e266 più lontano (diff. 0,236 ± 0,008); K più lontano (diff. 0,057 ± 0,010)).

### L4: profilo di distanza dell'eco (descrittivo)

- Controllo tema_eco (piantato {"eco": 0.25, "tema": 0.3}): eccesso di tema 0,116 ± 0,005 → presente (atteso presente); eccesso locale 0,160 ± 0,003 → presente (atteso presente).
- Controllo solo_eco (piantato {"eco": 0.25, "tema": 0.0}): eccesso di tema 0,001 ± 0,003 → assente (atteso assente); eccesso locale 0,159 ± 0,003 → presente (atteso presente).
- Controllo solo_tema (piantato {"eco": 0.0, "tema": 0.3}): eccesso di tema 0,161 ± 0,006 → presente (atteso presente); eccesso locale 0,002 ± 0,002 → assente (atteso assente).
- Controllo nulla (piantato {"eco": 0.0, "tema": 0.0}): eccesso di tema 0,011 ± 0,003 → zona grigia (atteso assente); eccesso locale -0,003 ± 0,002 → assente (atteso assente).
- **Il vero:** eccesso di tema sul caso 0,068 ± 0,007 → **lettura non valida (controllo della fase 0 fallito)**; eccesso locale sul caso 0,030 ± 0,002 → **lettura non valida (controllo della fase 0 fallito)**.

| testo | distanza 0 | distanza 1 | distanza 2 | distanza 3-5 | distanza 6+ | senza ripresa | profilo: quota di riprese a 0-1 righe | profilo: quota di riprese a 2 righe o piu' | tasso lontano condizionato (tema) | quota di riprese di tema | eccesso di tema sul caso | eccesso locale sul caso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1627 | 0,1991 | 0,0968 | 0,1280 | 0,1052 | 0,3082 | 0,3618 | 0,3300 | 0,2483 | 0,0260 | 0,0679 | 0,0301 |
| V21 (10 libri) | 0,1552 ± 0,0017 | 0,1775 ± 0,0009 | 0,0935 ± 0,0005 | 0,1300 ± 0,0005 | 0,1101 ± 0,0005 | 0,3336 ± 0,0016 | 0,3327 ± 0,0021 | 0,3336 ± 0,0009 | 0,2470 ± 0,0014 | 0,0243 ± 0,0007 | 0,0641 ± 0,0005 | 0,0187 ± 0,0008 |
| M1 (10 libri) | 0,1583 ± 0,0013 | 0,1799 ± 0,0015 | 0,0989 ± 0,0006 | 0,1343 ± 0,0007 | 0,1080 ± 0,0005 | 0,3205 ± 0,0022 | 0,3383 ± 0,0026 | 0,3412 ± 0,0008 | 0,2415 ± 0,0014 | 0,0094 ± 0,0007 | 0,0393 ± 0,0006 | 0,0154 ± 0,0006 |
| M5 (10 libri) | 0,1512 ± 0,0015 | 0,1850 ± 0,0011 | 0,0878 ± 0,0009 | 0,1256 ± 0,0014 | 0,1124 ± 0,0012 | 0,3380 ± 0,0023 | 0,3362 ± 0,0019 | 0,3258 ± 0,0030 | 0,2150 ± 0,0018 | 0,0178 ± 0,0007 | 0,0473 ± 0,0007 | 0,0329 ± 0,0009 |
| E0 (10 libri) | 0,1548 ± 0,0005 | 0,1803 ± 0,0007 | 0,0898 ± 0,0006 | 0,1313 ± 0,0005 | 0,1130 ± 0,0006 | 0,3309 ± 0,0008 | 0,3351 ± 0,0008 | 0,3341 ± 0,0006 | 0,2161 ± 0,0014 | 0,0099 ± 0,0004 | 0,0274 ± 0,0019 | 0,0338 ± 0,0007 |
| E1 (10 libri) | 0,1997 ± 0,0020 | 0,2057 ± 0,0011 | 0,0756 ± 0,0005 | 0,1118 ± 0,0007 | 0,1029 ± 0,0007 | 0,3044 ± 0,0015 | 0,4054 ± 0,0027 | 0,2903 ± 0,0015 | 0,2262 ± 0,0007 | 0,0097 ± 0,0004 | 0,0286 ± 0,0010 | 0,0615 ± 0,0007 |
| E2 (10 libri) | 0,1607 ± 0,0039 | 0,1869 ± 0,0021 | 0,0922 ± 0,0006 | 0,1326 ± 0,0011 | 0,1107 ± 0,0018 | 0,3169 ± 0,0033 | 0,3476 ± 0,0059 | 0,3356 ± 0,0027 | 0,2275 ± 0,0037 | 0,0104 ± 0,0005 | 0,0359 ± 0,0017 | 0,0318 ± 0,0005 |
| E3 (10 libri) | 0,1589 ± 0,0025 | 0,1854 ± 0,0015 | 0,0895 ± 0,0006 | 0,1296 ± 0,0007 | 0,1109 ± 0,0010 | 0,3257 ± 0,0027 | 0,3443 ± 0,0039 | 0,3301 ± 0,0014 | 0,2220 ± 0,0016 | 0,0096 ± 0,0008 | 0,0330 ± 0,0009 | 0,0327 ± 0,0008 |
| P1 (10 libri) | 0,1696 ± 0,0015 | 0,1982 ± 0,0006 | 0,1026 ± 0,0006 | 0,1314 ± 0,0008 | 0,0989 ± 0,0007 | 0,2993 ± 0,0009 | 0,3678 ± 0,0018 | 0,3328 ± 0,0015 | 0,2591 ± 0,0011 | 0,0240 ± 0,0009 | 0,0716 ± 0,0010 | 0,0288 ± 0,0006 |
| P2 (10 libri) | 0,1432 ± 0,0005 | 0,1743 ± 0,0005 | 0,0976 ± 0,0006 | 0,1342 ± 0,0010 | 0,1125 ± 0,0007 | 0,3382 ± 0,0016 | 0,3174 ± 0,0009 | 0,3443 ± 0,0019 | 0,2438 ± 0,0010 | 0,0182 ± 0,0007 | 0,0616 ± 0,0020 | 0,0190 ± 0,0008 |
| P3 (10 libri) | 0,1422 ± 0,0053 | 0,1753 ± 0,0033 | 0,0999 ± 0,0010 | 0,1360 ± 0,0008 | 0,1133 ± 0,0020 | 0,3334 ± 0,0069 | 0,3175 ± 0,0085 | 0,3491 ± 0,0017 | 0,2460 ± 0,0045 | 0,0203 ± 0,0009 | 0,0702 ± 0,0008 | 0,0199 ± 0,0004 |

## Copia a memoria e ripetizioni (soglie severe di ia20)

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| M1 | 0,0000 ± 0,0000 | 0,0077 ± 0,0002 | 0,0000 ± 0,0000 | 0,1508 ± 0,0016 |
| E1 | 0,0000 ± 0,0000 | 0,0084 ± 0,0005 | 0,0000 ± 0,0000 | 0,1447 ± 0,0007 |
| E2 | 0,0000 ± 0,0000 | 0,0077 ± 0,0005 | 0,0000 ± 0,0000 | 0,1500 ± 0,0024 |
| E3 | 0,0000 ± 0,0000 | 0,0085 ± 0,0005 | 0,0000 ± 0,0000 | 0,1565 ± 0,0026 |
| M5 | 0,0000 ± 0,0000 | 0,0059 ± 0,0003 | 0,0000 ± 0,0000 | 0,1768 ± 0,0032 |
| P1 | 0,0000 ± 0,0000 | 0,0067 ± 0,0004 | 0,0000 ± 0,0000 | 0,1563 ± 0,0011 |
| P2 | 0,0000 ± 0,0000 | 0,0059 ± 0,0004 | 0,0000 ± 0,0000 | 0,1701 ± 0,0006 |
| P3 | 0,0000 ± 0,0000 | 0,0058 ± 0,0002 | 0,0000 ± 0,0000 | 0,1741 ± 0,0018 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
- M1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E3: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M5: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- P1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- P2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- P3: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.

Modi di scrittura delle parole (conti sui libri): P2: libero 286919, uguale 46313, copia 57295, toglie 5513, aggiunge 2527, cambia 2942; P3: libero 277206, primo_riscritto 3164, copia 61982, due_riscritti 2876, uguale 43630, cambia 2277, toglie 5530, glifo_davanti 2332, aggiunge 2173.

## Tempi (minuti per lavoro)

- addestra: 30 lavori, media 17.2, massimo 24.7, totale 515.0.
- sens: 12 lavori, media 13.4, massimo 20.5, totale 160.2.
- libro: 30 lavori, media 3.1, massimo 4.1, totale 94.2.
- riflibro: 50 lavori, media 0.3, massimo 0.5, totale 17.4.
- K: 5 lavori, media 0.3, massimo 0.3, totale 1.6.
- M: 91 lavori, media 0.5, massimo 0.6, totale 48.6.
- D: 5 lavori, media 0.3, massimo 0.3, totale 1.4.
- F0: 101 lavori, media 0.0, massimo 0.1, totale 4.8.
- F0c: 4 lavori, media 0.1, massimo 0.1, totale 0.2.
