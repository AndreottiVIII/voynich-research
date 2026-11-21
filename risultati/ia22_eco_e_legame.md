# IA22 (ia22) — Eco e legame fra parole, insieme

Preregistrazione: `preregistrazioni/ia22.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, echi echi-1, gradini gradini-1, sklearn 1.9.1.

## Controlli dei giudici

- Giudici del paper, positivo: AUC 0,988, soglia ≥ 0,95 → sì. Negativo: giudice 1 0,506, giudice 2 0,503 → sì.
- K, positivo: parole 0,982, e192 0,935 → sì. Negativo: 0,499 → sì. K vede il v21 (AUC 0,766) → sì.
- A (riportato, non decide), positivo: parole 0,986, e192 0,958 → sì. Negativo: 0,484 → sì.

## Controlli di sensibilità (testi sintetici)

Testo con eco e contatto piantati insieme (fogli tenuti fuori della piega 0): tasso di eco 0,546, quota del glifo iniziale preferito 0,519, contatto 0,743.

| modello | guadagno su M1 (bit/segno) | eco scritta / piantata | glifo preferito scritto / piantato | contatto scritto / piantato | eco ok | legame ok | riuscito |
|---|---|---|---|---|---|---|---|
| M1 | 0,000 | 0,249 | 0,977 | 0,970 | NO | sì | NO |
| E0 | 0,611 | 0,941 | 0,885 | 0,796 | sì | NO | NO |
| E1 | 0,337 | 0,891 | 0,988 | 0,851 | sì | sì | sì |
| E2 | 0,596 | 0,924 | 0,920 | 0,842 | sì | sì | sì |
| E3 | 0,649 | 1,052 | 1,015 | 0,875 | sì | sì | sì |
| M5 | 0,617 | 0,951 | 0,883 | 0,793 | sì | NO | NO |

Testo senza niente di piantato: E0: guadagno su M1 -0,003, massa di copia 0,004 → sì; E1: guadagno su M1 -0,026, massa di copia — → sì; E2: guadagno su M1 -0,007, massa di copia 0,004 → sì; E3: guadagno su M1 0,004, massa di copia 0,004 → sì.

## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)

| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa di copia | minuti per modello |
|---|---|---|---|---|---|---|---|
| E0 | 767371 | 1,974 ± 0,030 | 1,942 ± 0,020 | 14,2 | 0 | 0,050 | 19.8 |
| E1 | 665529 | 1,962 ± 0,030 | 1,938 ± 0,020 | 13,6 | 0 | — | 16.8 |
| E2 | 767372 | 1,967 ± 0,031 | 1,951 ± 0,019 | 13,3 | 0 | 0,052 | 22.0 |
| E3 | 767374 | 1,966 ± 0,030 | 1,950 ± 0,021 | 15,0 | 0 | 0,053 | 20.5 |
| M1 (ia20) | — | 1,965 ± 0,031 | 1,940 ± 0,019 | — | — | — | — |
| M5 (ia20) | — | 1,960 ± 0,032 | 1,926 ± 0,022 | — | — | — | — |

Numeri imparati (medie): E0 {"beta": [-2.345, -4.564, -4.859, -3.902]}; E1 {"beta": [[0.4177, 0.3791, 0.421, 0.0], [0.0, 0.251, 0.3383, 0.0], [0.0682, 0.0742, 0.1084, 0.0], [0.0, 0.365, 0.0711, 0.0], [0.0, 0.0673, 0.0971, 0.0]], "peso_distanza": [1.572, 1.607, 1.568, 1.608, 1.484, 1.536, 1.414, 1.313, 1.259, 1.466, 1.169, 1.315, 1.312, 1.127, 1.141, 1.13, 1.179, 1.031, 1.229, 1.027, 0.879, 0.85, 0.888, 0.875, 1.11, 0.891, 0.749, 0.906]}; E2 {"beta": [-2.365, -4.527, -4.832, -3.895], "gamma": [0.06625, 0.007375322968446119]}; E3 {"beta": [-2.067, -4.635, -4.892, -3.726, -4.251, -4.639, -4.38]}.

## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)

| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |
|---|---|---|---|---|---|
| M1 | 10 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 | 0,675 ± 0,009 |
| E0 | 10 | 0,790 ± 0,014 | 0,863 ± 0,013 | 0,777 ± 0,006 | 0,704 ± 0,009 |
| E1 | 10 | 0,820 ± 0,015 | 0,870 ± 0,008 | 0,787 ± 0,006 | 0,693 ± 0,014 |
| E2 | 10 | 0,801 ± 0,012 | 0,864 ± 0,004 | 0,797 ± 0,007 | 0,695 ± 0,007 |
| E3 | 10 | 0,798 ± 0,008 | 0,836 ± 0,005 | 0,794 ± 0,008 | 0,724 ± 0,014 |
| M5 | 10 | 0,782 ± 0,008 | 0,799 ± 0,007 | 0,797 ± 0,007 | 0,707 ± 0,006 |
| v21 | 10 | 0,554 ± 0,004 (paper) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | 0,746 ± 0,005 |

Repliche diverse (più di 2 errori): M1: e231 NO, e266 NO; E0: e231 sì, e266 sì; E1: e231 sì, e266 sì; E2: e231 sì, e266 NO; E3: e231 NO, e266 NO; M5: e231 NO, e266 NO.

## Struttura (media ± errore standard sui libri)

| testo | copia netta (bit per parola) | quota locale Λ | contatto ultimo→primo glifo | ordine delle famiglie D | G9 vocabolario della pagina | bordi: inizio riga | bordi: fine riga | quota di parole nuove | costo di forma delle parole nuove (bit per glifo) |
|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1138 | 0,2074 | 0,1884 | 0,1444 | 0,0402 | 0,0790 | 0,0475 | 0,1530 | 3,4786 |
| M1 (10 libri) | 0,0360 ± 0,0016 | 0,0538 ± 0,0368 | 0,1891 ± 0,0025 | 0,1486 ± 0,0017 | 0,0245 ± 0,0006 | 0,0837 ± 0,0015 | 0,0457 ± 0,0007 | 0,1472 ± 0,0015 | 3,7459 ± 0,0062 |
| E0 (10 libri) | 0,0922 ± 0,0024 | 0,3947 ± 0,0203 | 0,1782 ± 0,0028 | 0,1373 ± 0,0025 | 0,0231 ± 0,0005 | 0,0817 ± 0,0004 | 0,0466 ± 0,0011 | 0,1539 ± 0,0011 | 3,7184 ± 0,0127 |
| E1 (10 libri) | 0,1014 ± 0,0045 | 0,3799 ± 0,0250 | 0,1732 ± 0,0033 | 0,1488 ± 0,0015 | 0,0281 ± 0,0002 | 0,0815 ± 0,0017 | 0,0454 ± 0,0019 | 0,1411 ± 0,0008 | 3,7235 ± 0,0061 |
| E2 (10 libri) | 0,1134 ± 0,0079 | 0,3605 ± 0,0150 | 0,1796 ± 0,0083 | 0,1432 ± 0,0081 | 0,0259 ± 0,0007 | 0,0803 ± 0,0012 | 0,0449 ± 0,0006 | 0,1460 ± 0,0023 | 3,8170 ± 0,0136 |
| E3 (10 libri) | 0,1103 ± 0,0034 | 0,4101 ± 0,0183 | 0,1761 ± 0,0016 | 0,1490 ± 0,0029 | 0,0262 ± 0,0006 | 0,0776 ± 0,0012 | 0,0430 ± 0,0008 | 0,1531 ± 0,0026 | 3,7469 ± 0,0042 |
| M5 (10 libri) | 0,1416 ± 0,0059 | 0,2362 ± 0,0111 | 0,1578 ± 0,0015 | 0,1078 ± 0,0014 | 0,0316 ± 0,0002 | 0,0760 ± 0,0017 | 0,0417 ± 0,0006 | 0,1725 ± 0,0030 | 3,6971 ± 0,0097 |
| V21 (10 libri) | 0,0548 ± 0,0016 | 0,0906 ± 0,0177 | 0,1850 ± 0,0011 | 0,0898 ± 0,0017 | 0,0392 ± 0,0005 | 0,0777 ± 0,0009 | 0,0414 ± 0,0007 | 0,1430 ± 0,0012 | 3,6608 ± 0,0053 |

## Letture preregistrate

- Validità: giudici del paper sì, K sì, A sì; sensibilità: E0 sì, E1 sì, E2 sì, E3 sì; controlli della fase 0 sì.
- Scambio visto nel testo sintetico (eco imparata ma legame piantato perso): E0.

### L1: eco e legame insieme "al vero"?

**Imitatori con copia netta, Λ, contatto e D tutti al vero: nessuno.**

| tipo | copia netta | Λ | contatto | D | eco al vero | legame al vero | tutti |
|---|---|---|---|---|---|---|---|
| vero | 0,114 | 0,207 | 0,188 | 0,144 | | | |
| M1 | 0,036 | 0,054 | 0,189 ✓ | 0,149 ✓ | NO | sì | NO |
| E0 | 0,092 | 0,395 | 0,178 | 0,137 ✓ | NO | NO | NO |
| E1 | 0,101 | 0,380 | 0,173 | 0,149 ✓ | NO | NO | NO |
| E2 | 0,113 ✓ | 0,360 | 0,180 ✓ | 0,143 ✓ | NO | sì | NO |
| E3 | 0,110 ✓ | 0,410 | 0,176 | 0,149 ✓ | NO | NO | NO |
| M5 | 0,142 | 0,236 | 0,158 | 0,108 | NO | NO | NO |

### L2: ogni imitatore contro M1 (eco aggiunta?) e contro M5 (legame tenuto?)

| confronto | lettura | misure corrette | misure rotte | sensibilità |
|---|---|---|---|---|
| E0 contro M1 | **corregge ma rompe** | copia netta (bit per parola), quota di parole nuove | contatto ultimo→primo glifo | provata |
| E0 contro M5 | **corregge ma rompe** | contatto ultimo→primo glifo, ordine delle famiglie D, bordi: fine riga, quota di parole nuove, giudice K | quota locale Λ, G9 vocabolario della pagina, giudice 2 (e266) | provata |
| E1 contro M1 | **corregge ma rompe** | copia netta (bit per parola), G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo) | contatto ultimo→primo glifo, quota di parole nuove, giudice 2 (e266) | provata |
| E1 contro M5 | **corregge ma rompe** | copia netta (bit per parola), contatto ultimo→primo glifo, ordine delle famiglie D, quota di parole nuove | quota locale Λ, G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo), giudice 1 (e231), giudice 2 (e266) | provata |
| E2 contro M1 | **corregge ma rompe** | copia netta (bit per parola) | costo di forma delle parole nuove (bit per glifo), giudice 2 (e266), giudice K | provata |
| E2 contro M5 | **corregge ma rompe** | copia netta (bit per parola), contatto ultimo→primo glifo, ordine delle famiglie D, bordi: fine riga, quota di parole nuove | quota locale Λ, G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo), giudice 2 (e266) | provata |
| E3 contro M1 | **corregge ma rompe** | copia netta (bit per parola) | contatto ultimo→primo glifo, bordi: fine riga, giudice K | provata |
| E3 contro M5 | **corregge ma rompe** | copia netta (bit per parola), contatto ultimo→primo glifo, ordine delle famiglie D, quota di parole nuove | quota locale Λ, G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo), giudice 2 (e266) | provata |

### L3: contro il v21

- **Tipo migliore (AUC media di e231, e266, K): M5.**
  - M1: più lontano dal vero del v21 (e231 più lontano (diff. 0,231 ± 0,010); e266 più lontano (diff. 0,240 ± 0,008); K uguale entro l'errore (diff. 0,007 ± 0,007)).
  - E0: più lontano dal vero del v21 (e231 più lontano (diff. 0,236 ± 0,015); e266 più lontano (diff. 0,262 ± 0,014); K uguale entro l'errore (diff. 0,011 ± 0,008)).
  - E1: più lontano dal vero del v21 (e231 più lontano (diff. 0,266 ± 0,016); e266 più lontano (diff. 0,269 ± 0,009); K più lontano (diff. 0,020 ± 0,008)).
  - E2: più lontano dal vero del v21 (e231 più lontano (diff. 0,247 ± 0,012); e266 più lontano (diff. 0,263 ± 0,007); K più lontano (diff. 0,031 ± 0,009)).
  - E3: più lontano dal vero del v21 (e231 più lontano (diff. 0,244 ± 0,009); e266 più lontano (diff. 0,235 ± 0,007); K più lontano (diff. 0,028 ± 0,009)).
  - M5: più lontano dal vero del v21 (e231 più lontano (diff. 0,228 ± 0,009); e266 più lontano (diff. 0,198 ± 0,009); K più lontano (diff. 0,031 ± 0,008)).

### L4: fase 0 — dove cade la modifica delle varianti d'eco e se si accorda col contatto

- Controllo pos (regola piantata = 0,8): a un glifo vicini 2,749, lontani 1,654, differenza 1,094 ± 0,070 → lettura **presente**.
- Controllo neg (regola piantata = 0,0): a un glifo vicini 0,501, lontani 0,824, differenza -0,323 ± 0,054 → lettura **assente**.

| testo | varianti | quota sul primo glifo (attesa a posto uniforme; lontani) | un glifo: vicini − rimescolata | lontani | vicini − lontani ± errore | regola |
|---|---|---|---|---|---|---|
| vere | 9314 | 0,488 (0,287; 0,498) | 0,567 | 0,579 | -0,012 ± 0,048 | **assente** |
| v21 | 89101 | 0,491 (0,288; 0,511) | 0,503 | 0,480 | 0,023 ± 0,013 | **assente** |
| M1 | 92887 | 0,505 (0,299; 0,511) | 0,623 | 0,628 | -0,004 ± 0,014 | **assente** |
| M5 | 80983 | 0,500 (0,282; 0,507) | 0,533 | 0,526 | 0,007 ± 0,014 | **assente** |
| E0 | 83507 | 0,477 (0,285; 0,491) | 0,580 | 0,584 | -0,004 ± 0,013 | **assente** |
| E1 | 98741 | 0,464 (0,272; 0,479) | 0,525 | 0,511 | 0,014 ± 0,013 | **assente** |
| E2 | 83480 | 0,498 (0,282; 0,511) | 0,550 | 0,549 | 0,001 ± 0,014 | **assente** |
| E3 | 81514 | 0,481 (0,280; 0,483) | 0,531 | 0,533 | -0,002 ± 0,014 | **assente** |

## Copia a memoria e ripetizioni (soglie severe di ia20)

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| M1 | 0,0000 ± 0,0000 | 0,0077 ± 0,0002 | 0,0000 ± 0,0000 | 0,1508 ± 0,0016 |
| E0 | 0,0000 ± 0,0000 | 0,0071 ± 0,0002 | 0,0000 ± 0,0000 | 0,1576 ± 0,0011 |
| E1 | 0,0000 ± 0,0000 | 0,0084 ± 0,0005 | 0,0000 ± 0,0000 | 0,1447 ± 0,0007 |
| E2 | 0,0000 ± 0,0000 | 0,0077 ± 0,0005 | 0,0000 ± 0,0000 | 0,1500 ± 0,0024 |
| E3 | 0,0000 ± 0,0000 | 0,0085 ± 0,0005 | 0,0000 ± 0,0000 | 0,1565 ± 0,0026 |
| M5 | 0,0000 ± 0,0000 | 0,0059 ± 0,0003 | 0,0000 ± 0,0000 | 0,1768 ± 0,0032 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
- M1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E0: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E3: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M5: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.

Modi di scrittura delle parole (conti sui libri): E0: libero 331766, uguale 12932, copia 18172, toglie 2737, cambia 1400, aggiunge 1103; E2: libero 321723, uguale 12769, copia 17915, toglie 2679, cambia 1422, aggiunge 1045; E3: libero 316966, uguale 11587, copia 18764, toglie 2142, cambia 965, glifo_davanti 863, aggiunge 695, primo_riscritto 1323, due_riscritti 1189.

## Tempi (minuti per lavoro)

- addestra: 40 lavori, media 19.7, massimo 28.3, totale 789.8.
- sens: 11 lavori, media 13.3, massimo 18.0, totale 146.2.
- libro: 40 lavori, media 1.8, massimo 2.3, totale 72.6.
- riflibro: 20 lavori, media 0.3, massimo 0.5, totale 6.7.
- K: 5 lavori, media 0.2, massimo 0.2, totale 1.2.
- M: 71 lavori, media 0.4, massimo 0.5, totale 29.1.
- D: 5 lavori, media 0.2, massimo 0.2, totale 1.1.
- F0: 71 lavori, media 0.0, massimo 0.0, totale 0.9.
