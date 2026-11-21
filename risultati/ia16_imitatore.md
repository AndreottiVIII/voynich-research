# IA16 (ia16) — Un imitatore che rilegge la pagina

Preregistrazione: `preregistrazioni/ia16.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Taglia scelta: **P** (validazione media P2: P 1,961, S 1,966). Regola: validazione media piu' bassa; se le taglie differiscono meno di 0,02 bit per segno, la piu' piccola.

## Controlli dei giudici

- Giudici del paper, positivo (giudice 2, parole rimescolate nella riga): AUC 0,988, soglia ≥ 0,95 → sì.
- Giudici del paper, negativo (etichette a caso): giudice 1 0,506, giudice 2 0,503, banda 0,45–0,55 → sì.
- K, positivo: parole 0,982, e192 0,935, soglia ≥ 0,85 → sì. Negativo (media di 5 etichette): 0,499 → sì. K vede il v21 (AUC 0,766, soglia ≥ 0,65) → sì.
- A (riportato), positivo: parole 0,986, e192 0,958, soglia ≥ 0,85 → sì. Negativo: 0,484 → sì.

## Modelli (pieghe per foglio; bit per segno)

| modello | parametri | epoca scelta (su) | BPC add. | BPC val. | BPC fuori | scarto | minuti |
|---|---|---|---|---|---|---|---|
| P1 P piega 0 r0 | 244969 | 36 (46) | 1,859 | 1,889 | 1,970 | 0,112 | 44.8 |
| P1 P piega 1 r0 | 244969 | 33 (43) | 1,844 | 1,945 | 2,009 | 0,165 | 46.8 |
| P1 P piega 2 r0 | 244969 | 27 (37) | 1,871 | 1,913 | 1,928 | 0,057 | 36.9 |
| P1 P piega 3 r0 | 244969 | 37 (47) | 1,854 | 1,906 | 1,960 | 0,106 | 45.4 |
| P1 P piega 4 r0 | 244969 | 27 (37) | 1,889 | 2,128 | 1,827 | -0,062 | 34.9 |
| P2 P piega 0 r0 | 244969 | 37 (47) | 1,846 | 1,877 | 1,958 | 0,112 | 115.5 |
| P2 P piega 0 r1 | 244969 | 32 (42) | 1,855 | 1,882 | 1,965 | 0,110 | 60.5 |
| P2 P piega 1 r0 | 244969 | 24 (34) | 1,883 | 1,963 | 2,029 | 0,146 | 64.5 |
| P2 P piega 1 r1 | 244969 | 20 (30) | 1,885 | 1,961 | 2,039 | 0,154 | 42.0 |
| P2 P piega 2 r0 | 244969 | 27 (37) | 1,870 | 1,920 | 1,933 | 0,063 | 63.2 |
| P2 P piega 2 r1 | 244969 | 32 (42) | 1,881 | 1,935 | 1,949 | 0,068 | 55.4 |
| P2 P piega 3 r0 | 244969 | 33 (43) | 1,876 | 1,921 | 1,975 | 0,099 | 60.2 |
| P2 P piega 3 r1 | 244969 | 39 (49) | 1,846 | 1,906 | 1,951 | 0,105 | 57.7 |
| P2 P piega 4 r0 | 244969 | 34 (44) | 1,892 | 2,122 | 1,843 | -0,049 | 52.3 |
| P2 P piega 4 r1 | 244969 | 20 (30) | 1,959 | 2,168 | 1,893 | -0,066 | 39.1 |
| P2 S piega 0 r0 | 623177 | 24 (34) | 1,876 | 1,893 | 1,970 | 0,095 | 130.3 |
| P2 S piega 1 r0 | 623177 | 25 (35) | 1,884 | 1,985 | 2,043 | 0,159 | 152.9 |
| P2 S piega 2 r0 | 623177 | 22 (32) | 1,900 | 1,941 | 1,960 | 0,059 | 145.9 |
| P2 S piega 3 r0 | 623177 | 22 (32) | 1,880 | 1,893 | 1,969 | 0,089 | 121.2 |
| P2 S piega 4 r0 | 623177 | 30 (40) | 1,873 | 2,114 | 1,849 | -0,025 | 151.4 |
| R P piega 0 r0 | 244969 | 27 (37) | 1,913 | 1,912 | 1,998 | 0,085 | 20.8 |
| R P piega 1 r0 | 244969 | 11 (21) | 1,948 | 1,998 | 2,084 | 0,136 | 12.9 |
| R P piega 2 r0 | 244969 | 13 (23) | 1,984 | 1,986 | 2,015 | 0,032 | 12.3 |
| R P piega 3 r0 | 244969 | 17 (27) | 1,944 | 1,945 | 2,015 | 0,071 | 12.4 |
| R P piega 4 r0 | 244969 | 24 (34) | 1,924 | 2,159 | 1,863 | -0,061 | 13.7 |

Medie per variante e taglia (bit per segno; epoche scelte in media; modelli arrivati al massimo di epoche): P1 P: 5 modelli, validazione 1,956, fuori 1,939, epoche 32,0, al massimo 0; P2 P: 10 modelli, validazione 1,965, fuori 1,954, epoche 29,8, al massimo 0; P2 S: 5 modelli, validazione 1,966, fuori 1,958, epoche 24,6, al massimo 0; R P: 5 modelli, validazione 2,000, fuori 1,995, epoche 18,4, al massimo 0.

ia07 (GRU 2 x 256, 665.481 parametri, stesse pieghe e repliche): validazione media 1,964, fuori media 1,948 bit per segno.

## Giudici: libri contro libro vero (un giudice per libro; AUC, più basso = più vicino al vero)

| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |
|---|---|---|---|---|---|
| imitatore P2 | 20 | 0,858 ± 0,006 | 0,878 ± 0,006 | 0,803 ± 0,004 | 0,777 ± 0,005 |
| imitatore P1 | 10 | 0,810 ± 0,006 | 0,833 ± 0,007 | 0,755 ± 0,006 | 0,713 ± 0,006 |
| imitatore R | 10 | 0,895 ± 0,006 | 0,927 ± 0,004 | 0,719 ± 0,004 | 0,670 ± 0,006 |
| ia07 (GRU) | 20 | 0,792 ± 0,005 | 0,855 ± 0,004 | 0,762 ± 0,004 | 0,675 ± 0,005 |
| v21 | 10 | 0,554 ± 0,004 (paper, 24 chiavi) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | 0,746 ± 0,005 |

P2 per replica dei modelli: e231: replica 0 0,841 ± 0,007, replica 1 0,876 ± 0,008; e266: replica 0 0,863 ± 0,008, replica 1 0,892 ± 0,008.
Le due repliche P2 differiscono di più di 2 errori? e231: sì; e266: sì.
Gruppi del giudice 2 (P2): G1 0,82; G2 0,82; G3 0,76; G4 0,70; G5 0,47; G6 0,68; G7 0,73; G8 0,63; G9 0,58.

## Letture preregistrate

- Validità: giudici del paper sì, K sì, A sì, copia di P2 senza soglia di "copia" superata sì.
- **L1, contro il v21: più lontano dal vero del v21.** e231 più lontano (differenza 0,304 ± 0,008); e266 più lontano (differenza 0,277 ± 0,008); K più lontano (differenza 0,037 ± 0,006). A (riportato, valido): più lontano.
- **L2, contro ia07: peggio di ia07.** e231 più lontano (differenza 0,067 ± 0,008); e266 più lontano (differenza 0,023 ± 0,007); K più lontano (differenza 0,041 ± 0,006). A (riportato, valido): più lontano.
- L3, giudici, P2 contro P1: e231 più lontano; e266 più lontano; K più lontano; più vicino su 0 giudici, più lontano su 3.
- L3, giudici, P2 contro R: e231 più vicino; e266 più vicino; K più lontano; più vicino su 2 giudici, più lontano su 1.
- **L3, struttura, P2 contro R: la memoria della pagina avvicina al vero.** copia_netta: P2 più vicino al vero di R; lam: P2 più vicino al vero di R; D: P2 più vicino al vero di R; contatto: P2 più vicino al vero di R; G9: P2 più vicino al vero di R; copia netta di R 0,034 contro 0,114 del vero.
- **L4, struttura contro ia07: zona grigia** (più vicino su 2 misure, più lontano su 2).

## Struttura (media ± errore standard sui libri; vero con intervallo al 95% sulle pagine)

| testo | copia netta (bit per parola) | quota locale Λ | D (ia10) | contatto g (ia08) | G9 JSD pagina-manoscritto |
|---|---|---|---|---|---|
| vero | 0,114 [0.099, 0.13] | 0,207 [0.129, 0.288] | 0,144 | 0,188 | 0,0402 |
| P2 (10 libri) | 0,087 ± 0,001 | 0,100 ± 0,014 | 0,118 ± 0,003 | 0,142 ± 0,002 | 0,0371 ± 0,0008 |
| I07 (10 libri) | 0,050 ± 0,002 | 0,102 ± 0,051 | 0,154 ± 0,002 | 0,182 ± 0,002 | 0,0243 ± 0,0005 |
| P1 (10 libri) | 0,092 ± 0,001 | 0,087 ± 0,010 | 0,139 ± 0,001 | 0,153 ± 0,001 | 0,0430 ± 0,0005 |
| R (10 libri) | 0,034 ± 0,001 | 0,004 ± 0,030 | 0,091 ± 0,002 | 0,120 ± 0,001 | 0,0246 ± 0,0001 |
| V21 (10 libri) | 0,055 ± 0,002 | 0,091 ± 0,018 | 0,090 ± 0,002 | 0,185 ± 0,001 | 0,0392 ± 0,0005 |

| misura | vero | imitatore P2 | ia07 | frazione di cammino da ia07 al vero | lettura |
|---|---|---|---|---|---|
| copia_netta | 0,1138 | 0,0870 | 0,0504 | 0,58 | più vicino al vero di ia07 |
| lam | 0,2074 | 0,1001 | 0,1019 | -0,02 | come ia07 |
| D | 0,1444 | 0,1179 | 0,1541 | 3,75 | più lontano dal vero di ia07 |
| contatto | 0,1884 | 0,1418 | 0,1816 | — | più lontano dal vero di ia07 |
| G9 | 0,0402 | 0,0371 | 0,0243 | 0,81 | più vicino al vero di ia07 |

## Copia a memoria e ripetizioni

Quote rispetto al testo d'addestramento del modello che ha scritto la pagina (naturale: pagine vere tenute fuori).

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| imitatore P2 | 0,0000 ± 0,0000 | 0,0085 ± 0,0001 | 0,0000 ± 0,0000 | 0,1603 ± 0,0050 |
| imitatore P1 | 0,0000 ± 0,0000 | 0,0088 ± 0,0002 | 0,0000 ± 0,0000 | 0,1351 ± 0,0002 |
| imitatore R | 0,0000 ± 0,0000 | 0,0052 ± 0,0002 | 0,0000 ± 0,0000 | 0,1597 ± 0,0005 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
| v21 (libro d'esempio) | 0,0000 | 0,0040 | 0,0000 | 0,1530 |
- P2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; parole nuove nella fascia; scrittura che si avvita: NO.
- P1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; parole nuove nella fascia; scrittura che si avvita: NO.
- R: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; parole nuove nella fascia; scrittura che si avvita: NO.

Ripetizioni dentro la pagina (naturale: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000; parole uguali alla parola prima 0,0094):
- P2: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0137 ± 0,0002.
- P1: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0141 ± 0,0002.
- R: righe uguali a una precedente nella pagina (>= 4 parole) 0,0000 ± 0,0000; righe uguali alla riga sopra (>= 2 parole) 0,0000 ± 0,0000; parole uguali alla parola prima 0,0087 ± 0,0001.

## Libro vetrina (modello su tutto: non è una prova onesta; testo e immagini solo in `dati/cache/ia16/vetrina`)

- righe di almeno 3 parole identiche a una riga vera: 0 su 4051; 5-grammi presenti nel libro vero: 0 su 28496; pagine identiche: 0 su 207; pagine senza copia: 207.

## Tempi (minuti per lavoro, macchina condivisa)

- addestra: 25 lavori, media 63.7, massimo 152.9, totale 1593.1.
- libro: 40 lavori, media 6.1, massimo 12.4, totale 245.0.
- K: 5 lavori, media 0.4, massimo 0.4, totale 2.1.
- M: 51 lavori, media 0.7, massimo 0.9, totale 37.0.
- D: 5 lavori, media 0.3, massimo 0.3, totale 1.3.
