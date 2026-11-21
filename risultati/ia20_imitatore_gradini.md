# IA20 (ia20) — L'imitatore a gradini

Preregistrazione: `preregistrazioni/ia20.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, gradini gradini-1, sklearn 1.9.1.

## Controlli dei giudici

- Giudici del paper, positivo: AUC 0,988, soglia ≥ 0,95 → sì. Negativo: giudice 1 0,506, giudice 2 0,503, banda 0,45–0,55 → sì.
- K, positivo: parole 0,982, e192 0,935, soglia ≥ 0,85 → sì. Negativo (media di 5 etichette): 0,499 → sì. K vede il v21 (AUC 0,766, soglia ≥ 0,65) → sì.
- A (riportato, non decide), positivo: parole 0,986, e192 0,958 → sì. Negativo: 0,484 → sì.

## Controlli di sensibilità degli ingredienti (testi sintetici con un ingrediente piantato)

- M3 (vocabolario della pagina), tema piantato: M3 sotto M2 di 0,002 bit per segno (soglia ≥ 0,030) → NO.
- M4 (posizione nella riga), parole di bordo piantate: M4 sotto M3 di 0,018 (soglia ≥ -0,020: non rovina; il guadagno atteso è piccolo, la GRU sa già contare) → sì.
- M5 (puntatore), copia-e-ritocco piantata dalla riga sopra: M5 sotto M1 di 0,599 (soglia ≥ 0,100), sotto M2 di 0,271; quota a posteriori della copia sulle parole copiabili 0,822 (soglia ≥ 0,500) → sì.
- M5, testo senza niente di piantato: M1 − M5 = 0,012 (≤ 0,020: M5 non guadagna dal nulla) e massa di copia media 0,005 (≤ 0,100) → sì. M2 su eco (descrittivo): guadagno su M1 0,329.

## Modelli (bit per segno; medie sui 10 modelli di ogni gradino)

| gradino | parametri | validazione | fuori piega | epoche scelte | al massimo | minuti per modello |
|---|---|---|---|---|---|---|
| M1 | 665481 | 1,965 ± 0,031 | 1,940 ± 0,019 | 13,5 | 0 | 15.1 |
| M2 | 797193 | 1,950 ± 0,030 | 1,924 ± 0,018 | 15,1 | 0 | 25.0 |
| M3 | 929609 | 1,953 ± 0,031 | 1,929 ± 0,019 | 13,1 | 0 | 29.4 |
| M4 | 938921 | 1,957 ± 0,032 | 1,924 ± 0,021 | 10,9 | 0 | 29.6 |
| M5 | 1040811 | 1,960 ± 0,032 | 1,926 ± 0,022 | 13,0 | 0 | 36.8 |

ia07 (GRU 2 × 256, stesse pieghe e repliche): validazione media 1,964, fuori media 1,948.

## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)

| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |
|---|---|---|---|---|---|
| M1 | 10 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 | 0,675 ± 0,009 |
| M2 | 10 | 0,785 ± 0,005 | 0,838 ± 0,005 | 0,764 ± 0,006 | 0,643 ± 0,008 |
| M3 | 10 | 0,796 ± 0,009 | 0,822 ± 0,012 | 0,785 ± 0,007 | 0,672 ± 0,013 |
| M4 | 10 | 0,801 ± 0,009 | 0,830 ± 0,009 | 0,760 ± 0,006 | 0,644 ± 0,008 |
| M5 | 10 | 0,782 ± 0,008 | 0,799 ± 0,007 | 0,797 ± 0,007 | 0,707 ± 0,006 |
| ia07 (GRU) | 20 | 0,792 ± 0,005 | 0,855 ± 0,004 | 0,762 ± 0,004 | 0,675 ± 0,005 |
| v21 | 10 | 0,554 ± 0,004 (paper) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | 0,746 ± 0,005 |

Repliche diverse (più di 2 errori): M1: e231 NO, e266 NO; M2: e231 NO, e266 NO; M3: e231 sì, e266 sì; M4: e231 sì, e266 sì; M5: e231 NO, e266 NO.

## Struttura (media ± errore standard sui libri)

| testo | copia netta (bit per parola) | quota locale Λ | contatto ultimo→primo glifo | ordine delle famiglie D | G9 vocabolario della pagina | bordi: inizio riga | bordi: fine riga | quota di parole nuove | costo di forma delle parole nuove (bit per glifo) |
|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1138 | 0,2074 | 0,1884 | 0,1444 | 0,0402 | 0,0790 | 0,0475 | 0,1530 | 3,4786 |
| M1 (10 libri) | 0,0360 ± 0,0016 | 0,0538 ± 0,0368 | 0,1891 ± 0,0025 | 0,1486 ± 0,0017 | 0,0245 ± 0,0006 | 0,0837 ± 0,0015 | 0,0457 ± 0,0007 | 0,1472 ± 0,0015 | 3,7459 ± 0,0062 |
| M2 (10 libri) | 0,0515 ± 0,0010 | 0,1787 ± 0,0234 | 0,1624 ± 0,0016 | 0,1180 ± 0,0020 | 0,0269 ± 0,0009 | 0,0751 ± 0,0012 | 0,0478 ± 0,0010 | 0,1568 ± 0,0025 | 3,6675 ± 0,0069 |
| M3 (10 libri) | 0,0783 ± 0,0051 | 0,0453 ± 0,0208 | 0,1859 ± 0,0042 | 0,1306 ± 0,0068 | 0,0296 ± 0,0010 | 0,0842 ± 0,0026 | 0,0439 ± 0,0010 | 0,1555 ± 0,0022 | 3,6801 ± 0,0071 |
| M4 (10 libri) | 0,0656 ± 0,0051 | 0,0932 ± 0,0176 | 0,1507 ± 0,0018 | 0,1078 ± 0,0023 | 0,0297 ± 0,0007 | 0,0810 ± 0,0013 | 0,0440 ± 0,0003 | 0,1507 ± 0,0013 | 3,7367 ± 0,0045 |
| M5 (10 libri) | 0,1416 ± 0,0059 | 0,2362 ± 0,0111 | 0,1578 ± 0,0015 | 0,1078 ± 0,0014 | 0,0316 ± 0,0002 | 0,0760 ± 0,0017 | 0,0417 ± 0,0006 | 0,1725 ± 0,0030 | 3,6971 ± 0,0097 |
| I07 (10 libri) | 0,0504 ± 0,0022 | 0,1019 ± 0,0508 | 0,1816 ± 0,0022 | 0,1541 ± 0,0017 | 0,0243 ± 0,0005 | 0,0796 ± 0,0012 | 0,0439 ± 0,0010 | 0,1428 ± 0,0006 | 3,7093 ± 0,0040 |
| V21 (10 libri) | 0,0548 ± 0,0016 | 0,0906 ± 0,0177 | 0,1850 ± 0,0011 | 0,0898 ± 0,0017 | 0,0392 ± 0,0005 | 0,0777 ± 0,0009 | 0,0414 ± 0,0007 | 0,1430 ± 0,0012 | 3,6608 ± 0,0053 |

## Letture preregistrate

- Validità: giudici del paper sì, K sì, A sì; sensibilità degli ingredienti: M2 sì, M3 NO, M4 sì, M5 sì.
- **Esito finale: il gradino migliore (AUC media di e231, e266, K più bassa) è M5: più lontano dal vero del v21.**
  - M1 contro il v21: più lontano dal vero del v21 (e231 più lontano (diff. 0,231 ± 0,010); e266 più lontano (diff. 0,240 ± 0,008); K uguale entro l'errore (diff. 0,007 ± 0,007)).
  - M2 contro il v21: più lontano dal vero del v21 (e231 più lontano (diff. 0,231 ± 0,006); e266 più lontano (diff. 0,237 ± 0,007); K uguale entro l'errore (diff. -0,002 ± 0,007)).
  - M3 contro il v21: più lontano dal vero del v21 (e231 più lontano (diff. 0,242 ± 0,010); e266 più lontano (diff. 0,221 ± 0,013); K più lontano (diff. 0,019 ± 0,009)).
  - M4 contro il v21: più lontano dal vero del v21 (e231 più lontano (diff. 0,247 ± 0,010); e266 più lontano (diff. 0,229 ± 0,010); K uguale entro l'errore (diff. -0,007 ± 0,007)).
  - M5 contro il v21: più lontano dal vero del v21 (e231 più lontano (diff. 0,228 ± 0,009); e266 più lontano (diff. 0,198 ± 0,009); K più lontano (diff. 0,031 ± 0,008)).
- M1 contro ia07 (stesso modello, tratti allineati alle righe: deve essere "uguale"): e231 uguale entro l'errore; e266 uguale entro l'errore; K uguale entro l'errore.

### Ingrediente → misure corrette / rotte

| gradino | ingrediente | lettura | misure corrette | misure rotte | sensibilità |
|---|---|---|---|---|---|
| M2 | memoria locale (attenzione sulla riga in corso e su quella sopra) | **corregge ma rompe** | copia netta (bit per parola), quota locale Λ, G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo) | contatto ultimo→primo glifo, ordine delle famiglie D | provata |
| M3 | vocabolario della pagina | **corregge ma rompe** | copia netta (bit per parola), contatto ultimo→primo glifo, G9 vocabolario della pagina | quota locale Λ, bordi: fine riga, giudice K | NON provata (con riserva) |
| M4 | posizione nella riga | **rompe** | giudice K | contatto ultimo→primo glifo, ordine delle famiglie D, costo di forma delle parole nuove (bit per glifo) | provata |
| M5 | copia e ritocco (puntatore) | **corregge ma rompe** | copia netta (bit per parola), quota locale Λ, contatto ultimo→primo glifo, G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo), giudice 2 (e266) | bordi: fine riga, quota di parole nuove, giudice K | provata |

### Che cosa nessun gradino porta al vero

| misura | vero | M1 | M2 | M3 | M4 | M5 | al vero in qualche gradino | frazione del cammino del migliore |
|---|---|---|---|---|---|---|---|---|
| copia netta (bit per parola) | 0,1138 | 0,0360 | 0,0515 | 0,0783 | 0,0656 | 0,1416 | no | 0,64 |
| quota locale Λ | 0,2074 | 0,0538 | 0,1787 ✓ | 0,0453 | 0,0932 | 0,2362 | sì | 0,81 |
| contatto ultimo→primo glifo | 0,1884 | 0,1891 ✓ | 0,1624 | 0,1859 ✓ | 0,1507 | 0,1578 | sì | 0,00 |
| ordine delle famiglie D | 0,1444 | 0,1486 ✓ | 0,1180 | 0,1306 | 0,1078 | 0,1078 | sì | 0,00 |
| G9 vocabolario della pagina | 0,0402 | 0,0245 | 0,0269 | 0,0296 | 0,0297 | 0,0316 | no | 0,45 |
| bordi: inizio riga | 0,0790 | 0,0837 | 0,0751 ✓ | 0,0842 ✓ | 0,0810 ✓ | 0,0760 ✓ | sì | 0,56 |
| bordi: fine riga | 0,0475 | 0,0457 ✓ | 0,0478 ✓ | 0,0439 | 0,0440 | 0,0417 | sì | 0,84 |
| quota di parole nuove | 0,1530 | 0,1472 ✓ | 0,1568 ✓ | 0,1555 ✓ | 0,1507 ✓ | 0,1725 | sì | 0,61 |
| costo di forma delle parole nuove (bit per glifo) | 3,4786 | 3,7459 | 3,6675 | 3,6801 | 3,7367 | 3,6971 | no | 0,29 |

**Misure che nessun gradino porta al vero:** copia netta (bit per parola), G9 vocabolario della pagina, costo di forma delle parole nuove (bit per glifo).
- giudice 1 (e231): gradini che battono il v21 (0,554): nessuno.
- giudice 2 (e266): gradini che battono il v21 (0,601): nessuno.
- giudice K: gradini che battono il v21 (0,766): nessuno.

## Copia a memoria e ripetizioni (soglie severe)

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| M1 | 0,0000 ± 0,0000 | 0,0077 ± 0,0002 | 0,0000 ± 0,0000 | 0,1508 ± 0,0016 |
| M2 | 0,0000 ± 0,0000 | 0,0066 ± 0,0002 | 0,0000 ± 0,0000 | 0,1607 ± 0,0027 |
| M3 | 0,0000 ± 0,0000 | 0,0074 ± 0,0005 | 0,0000 ± 0,0000 | 0,1598 ± 0,0022 |
| M4 | 0,0000 ± 0,0000 | 0,0068 ± 0,0002 | 0,0000 ± 0,0000 | 0,1547 ± 0,0013 |
| M5 | 0,0000 ± 0,0000 | 0,0059 ± 0,0003 | 0,0000 ± 0,0000 | 0,1768 ± 0,0032 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
- M1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M3: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M4: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M5: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.

Ripetizioni dentro la pagina (naturale: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000; parole uguali alla parola prima 0,0094):
- M1: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0098 ± 0,0002.
- M2: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0105 ± 0,0003.
- M3: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0108 ± 0,0004.
- M4: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0110 ± 0,0002.
- M5: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0122 ± 0,0005.

M5, modi di scrittura delle parole (conti sui libri): libero 324283, uguale 8229, copia 11706, cambia 1021, toglie 1692, aggiunge 764.

## Tempi (minuti per lavoro)

- addestra: 50 lavori, media 27.2, massimo 45.7, totale 1359.0.
- sens: 9 lavori, media 17.8, massimo 24.9, totale 159.9.
- libro: 50 lavori, media 4.3, massimo 6.1, totale 215.0.
- K: 5 lavori, media 0.4, massimo 0.4, totale 1.9.
- M: 71 lavori, media 0.6, massimo 0.6, totale 39.7.
- D: 5 lavori, media 0.3, massimo 0.3, totale 1.4.
