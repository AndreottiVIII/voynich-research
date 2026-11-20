# IA7 (ia07) — Il Voynich ricreato da una rete neurale locale

Preregistrazione: `preregistrazioni/ia07.md`.

- Rete: GRU 2 strati x 256, immersione 64, caduta 0.30. Addestramento: AdamW lr 0.002, decadimento 0.01, taglio 1, lotti di 8 pagine, tratti di 256 segni, al massimo 150 epoche, pazienza 10.
- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.

## Controlli

- **Positivo** (giudice 2 sul libro vero con le parole rimescolate nella riga (O2, semi [1, 2])): AUC 0,988, soglia ≥ 0,95 → sì.
- **Negativo** (pagine vere con etichette a caso (pieghe per foglio, semi [1, 2, 3, 4, 5])): giudice 1 0,506, giudice 2 0,503, intervallo 0,45–0,55 → sì.
- **Recupero del messaggio**: esatto 21 su 21, chiave sbagliata respinta 21 su 21 → sì.
- **Negativo con/senza** (libri senza messaggio, semi dispari contro pari (giudice 2, pieghe per libro)): AUC 0,511 → sì.
- **Positivo, giudice A** (giudice A: libro vero con le parole rimescolate nella riga (seme 396001) e generatore e192 (se manca, vale il primo, dichiarato)): AUC parole 0,986, e192 0,958, soglia ≥ 0,85 → sì.
- **Negativo, giudice A** (giudice A: pagine vere con etichette a caso (media di 5 etichette)): AUC 0,484 (0,494, 0,510, 0,464, 0,499, 0,450), intervallo 0,45–0,55 → sì.

## Modelli (pieghe per foglio, due repliche con semi di addestramento diversi)

| piega | replica | fogli add./val./fuori | parametri | epoca scelta (su) | BPC add. | BPC val. | BPC fuori | scarto | minuti |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 70/10/20 | 665481 | 15 (25) | 1,773 | 1,878 | 1,938 | 0,165 | 33.0 |
| 1 | 0 | 70/10/20 | 665481 | 12 (22) | 1,811 | 1,960 | 2,024 | 0,213 | 31.6 |
| 2 | 0 | 70/10/20 | 665481 | 14 (24) | 1,792 | 1,941 | 1,944 | 0,152 | 35.0 |
| 3 | 0 | 70/10/20 | 665481 | 15 (25) | 1,790 | 1,913 | 1,956 | 0,166 | 35.3 |
| 4 | 0 | 70/10/20 | 665481 | 12 (22) | 1,877 | 2,145 | 1,849 | -0,028 | 27.3 |
| 0 | 1 | 70/10/20 | 665481 | 19 (29) | 1,728 | 1,884 | 1,964 | 0,236 | 37.2 |
| 1 | 1 | 70/10/20 | 665481 | 18 (28) | 1,728 | 1,934 | 2,030 | 0,302 | 39.0 |
| 2 | 1 | 70/10/20 | 665481 | 11 (21) | 1,861 | 1,943 | 1,971 | 0,110 | 29.0 |
| 3 | 1 | 70/10/20 | 665481 | 13 (23) | 1,812 | 1,911 | 1,966 | 0,153 | 22.2 |
| 4 | 1 | 70/10/20 | 665481 | 12 (22) | 1,847 | 2,132 | 1,837 | -0,009 | 20.2 |
| tutto | — | 100/0/0 | 665481 | 13 (13) | 1,863 | — | — | — | 24.4 |

## Giudici: libri generati contro libro vero (un giudice per libro)

| libri | n | giudice 1 (e231) | lettura | giudice 2 (e266) | lettura | pagine giudicate | pagella | cancello | estese |
|---|---|---|---|---|---|---|---|---|---|
| senza messaggio | 20 | 0,792 ± 0,005 (0,740–0,834) | più lontano dal vero del v21 | 0,855 ± 0,004 (0,827–0,892) | più lontano dal vero del v21 | 200 | 13,0 | 0 | 5,7 |
| con messaggio | 20 | 0,795 ± 0,005 (0,730–0,829) | più lontano dal vero del v21 (le due repliche dei modelli differiscono più di 2 errori) | 0,864 ± 0,004 (0,808–0,894) | più lontano dal vero del v21 | 201 | 12,8 | 0 | 5,7 |

Riferimenti del paper v2: v21 giudice 1 0,554 ± 0,004, giudice 2 0,601 ± 0,005 (24 chiavi, pagella 16,0/17). Scala (e400): O1 righe rimescolate nella pagina: 0,481 e 0,595; O2 parole rimescolate nella riga: 0,984 e 0,990.
Scala ricalcolata qui sul libro vero: O1: 0,488 e 0,601; O2: 0,981 e 0,988.

**Per replica dei modelli (senza messaggio):** giudice 1: replica 0 0,795 ± 0,006, replica 1 0,789 ± 0,009; giudice 2: replica 0 0,849 ± 0,006, replica 1 0,860 ± 0,005.

**Gruppi del giudice 2 (senza messaggio):** G1 0,70; G2 0,73; G3 0,73; G4 0,60; G5 0,48; G6 0,65; G7 0,57; G8 0,62; G9 0,73.
Materie mancate (somma sui libri): gradiente (20), deriva (20), coppie viste altrove (20), profilo pagina (19), ripetizione (16), omogeneità (16), prime righe come registro (16), scelte di riga (10), verticale (9).

| caratteristica (primo libro) | coefficiente | vero | generato |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -1.77 | 0.0399 | 0.0258 |
| G3 lunghezza media | -1.58 | 4.2931 | 4.2546 |
| G3 uniche nella pagina | +1.53 | 0.6341 | 0.6616 |
| G3 fra le 100 piu frequenti | +1.42 | 0.4250 | 0.4634 |
| G4 unioni attestate | -1.22 | 0.0912 | 0.0910 |
| G6 coppie viste altrove | +1.21 | 0.2215 | 0.2547 |
| G8 lunghezza parole prime righe | -1.15 | 4.6305 | 4.6085 |
| G3 tipi su parole | +1.07 | 0.7546 | 0.7744 |

**Per replica dei modelli (con messaggio):** giudice 1: replica 0 0,806 ± 0,004, replica 1 0,784 ± 0,008; giudice 2: replica 0 0,867 ± 0,004, replica 1 0,862 ± 0,008.

**Gruppi del giudice 2 (con messaggio):** G1 0,70; G2 0,73; G3 0,74; G4 0,60; G5 0,48; G6 0,65; G7 0,58; G8 0,62; G9 0,73.
Materie mancate (somma sui libri): gradiente (20), deriva (20), profilo pagina (20), coppie viste altrove (20), prime righe come registro (18), ripetizione (17), omogeneità (17), verticale (9), scelte di riga (8), dispersione delle lunghezze (1).

| caratteristica (primo libro) | coefficiente | vero | generato |
|---|---|---|---|
| G9 JSD pagina-manoscritto | -1.91 | 0.0402 | 0.0255 |
| G3 fra le 100 piu frequenti | +1.49 | 0.4244 | 0.4695 |
| G3 uniche nella pagina | +1.40 | 0.6359 | 0.6580 |
| G3 tipi su parole | +1.30 | 0.7559 | 0.7727 |
| G4 unioni attestate | -1.15 | 0.0916 | 0.0928 |
| G3 uniche nel testo | +1.11 | 0.1461 | 0.1451 |
| G2 a+r | -1.09 | 0.0210 | 0.0146 |
| G6 somiglianza a distanza 2 | -1.07 | 0.2198 | 0.2097 |

## Giudice A "sorpresa" (di IA1): libri generati contro libro vero

Modello del testo per piega (le pieghe dei generatori) e seme addestrato sulle pagine vere delle altre pieghe; profilo di sorpresa di 14 numeri per pagina; regressione logistica come e231. **Limite di circolarità:** il generatore e il giudice sono reti addestrate sullo stesso testo; vedi la preregistrazione.

| libri | n | AUC A | v21 ricalcolato (stesse pieghe) | lettura | lettura assoluta | nota |
|---|---|---|---|---|---|---|
| senza messaggio | 20 | 0,675 ± 0,005 (0,629–0,724) | 0,746 ± 0,005 (10 libri) | più vicino al vero del v21 | giudice A vede la differenza (sopra 0,65) | NON conclusivo: un giudice che è una rete addestrata sullo stesso testo vede il testo della rete come atteso; si legge solo insieme ai giudici 1 e 2 |
| con messaggio | 20 | 0,668 ± 0,006 (0,621–0,708) | 0,751 ± 0,006 (10 libri) | più vicino al vero del v21 | giudice A vede la differenza (sopra 0,65) | NON conclusivo: un giudice che è una rete addestrata sullo stesso testo vede il testo della rete come atteso; si legge solo insieme ai giudici 1 e 2 |

Per replica dei modelli (senza messaggio): replica 0 0,694 ± 0,005, replica 1 0,657 ± 0,004.

Per replica dei modelli (con messaggio): replica 0 0,686 ± 0,006, replica 1 0,649 ± 0,005.

v21 con messaggio (chiavi 13–22) ricalcolato qui: 0,751 ± 0,006; ia01 (pieghe per pagina): 0,751 → scarto 0,000 (coerente). v21 senza messaggio: 0,746 ± 0,005. Righe rimescolate nella pagina: 0,589. Controlli di ia01 (pieghe diverse): parole rimescolate 0,985; e192 0,957; negativo 0,483; righe rimescolate 0,576.
Coerenza del contesto con ia01.contesto(): pagine [202, 202]; stesse_pagine True; stessi_segni True; sequenze_uguali 202.

Modelli del testo di A: seme 1 piega 0: 1440 passi, 1,950 bit/segno in validazione, 2,063 fuori; seme 1 piega 1: 1240 passi, 1,850 bit/segno in validazione, 2,099 fuori; seme 1 piega 2: 1620 passi, 1,895 bit/segno in validazione, 2,072 fuori; seme 1 piega 3: 1720 passi, 1,993 bit/segno in validazione, 2,029 fuori; seme 1 piega 4: 1480 passi, 1,865 bit/segno in validazione, 1,946 fuori; seme 2 piega 0: 1240 passi, 2,007 bit/segno in validazione, 2,052 fuori; seme 2 piega 1: 1420 passi, 1,959 bit/segno in validazione, 2,096 fuori; seme 2 piega 2: 1880 passi, 2,033 bit/segno in validazione, 2,076 fuori; seme 2 piega 3: 1740 passi, 1,979 bit/segno in validazione, 2,036 fuori; seme 2 piega 4: 1740 passi, 1,967 bit/segno in validazione, 1,951 fuori.

Differenza di profilo, generato meno vero, bit per segno (senza messaggio): bit_medi -0.006, bit_sd +0.049, bit_p95 +0.117, inizio_parola -0.049, inizio_riga +0.093, dentro_parola +0.000, spazio -0.024, fine_riga +0.140, riga_paragrafo -0.009, riga_altra -0.002, quarto1 -0.006, quarto2 +0.015, quarto3 -0.010, quarto4 -0.025.

Differenza di profilo, generato meno vero, bit per segno (con messaggio): bit_medi -0.005, bit_sd +0.049, bit_p95 +0.120, inizio_parola -0.043, inizio_riga +0.077, dentro_parola +0.002, spazio -0.020, fine_riga +0.132, riga_paragrafo -0.008, riga_altra -0.001, quarto1 -0.003, quarto2 +0.014, quarto3 -0.007, quarto4 -0.022.

Lo stesso per il v21 senza messaggio: bit_medi +0.132, bit_sd +0.105, bit_p95 +0.406, inizio_parola +0.180, inizio_riga +0.172, dentro_parola +0.128, spazio +0.040, fine_riga +0.225, riga_paragrafo +0.139, riga_altra +0.125, quarto1 +0.120, quarto2 +0.155, quarto3 +0.125, quarto4 +0.128.

Con meno senza messaggio (differenza delle medie, libri non appaiati): AUC_e231 0,0031 ± 0,0073; AUC_e266 0,0097 ± 0,0057; pagella -0,1500 ± 0,2436.

## Copia a memoria

Quote rispetto al testo d'addestramento del modello che ha scritto la pagina (riferimento naturale: le pagine vere tenute fuori, stesse pieghe).

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| senza messaggio | 0,0000 ± 0,0000 | 0,0081 ± 0,0001 | 0,0000 ± 0,0000 | 0,1461 ± 0,0005 |
| con messaggio | 0,0000 ± 0,0000 | 0,0081 ± 0,0001 | 0,0000 ± 0,0000 | 0,1468 ± 0,0005 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
| v21 (libro d'esempio) | 0,0000 | 0,0040 | 0,0000 | 0,1530 |
- 5-grammi: generato 0,0000 ± 0,0000, naturale 0,0000 → **copia come il testo vero**.
- righe intere: generato 0,0000 ± 0,0000, naturale 0,0000 → **copia come il testo vero**.

## Messaggio

- Capacità (bit determinati dal libro): con messaggio 349075 ± 334, senza 348610 ± 459; il messaggio ne usa 38304; v21 81100–85900 → **più del v21**.
- Con contro senza messaggio (giudice 2, pieghe per libro, 8127 pagine): AUC 0,496 → **nessuna traccia**. Per gruppo: G1 0,499; G2 0,499; G3 0,500; G4 0,486; G5 0,487; G6 0,496; G7 0,482; G8 0,483; G9 0,496.

## Libro vetrina (modello addestrato su tutto: non è una prova onesta)

- Giudice 1 0,997, giudice 2 0,998; recupero esatto sì; capacità 280066 bit; pagella 13.
- Copia rispetto al libro intero: 5-grammi 0,0000; 3-grammi 0,0099; righe intere 0,0000; parole nuove 0,1442.

**Controllo di copia della vetrina** (il testo e le immagini restano in `dati/cache/ia07_vetrina/`, non nel repo; la pubblicazione di qualche pagina la decide Davide guardando questo controllo):

- righe di almeno 3 parole identiche a una riga del libro vero: **0 su 3997** (nello stesso posto: 0);
- 5-grammi di parole presenti nel libro vero: **0 su 13371** (0,0000);
- pagine intere identiche alla pagina vera: **0 su 207**;
- pagine senza nessuna riga e nessun 5-gramma copiato: 207 su 207.

Nessuna pagina con copia.

- Pagine in immagine (solo fra le pagine senza copia, in `dati/cache/ia07_vetrina/pagine/`): `ia07_vetrina_f1v.png` (89 kB), `ia07_vetrina_f75r.png` (124 kB), `ia07_vetrina_f58r.png` (142 kB), `ia07_vetrina_f88r.png` (126 kB).
