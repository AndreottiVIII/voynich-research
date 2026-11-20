# ia01 — giudice neurale

controllo positivo, giudice A: ctrl:parole 0.985, ctrl:e192 0.957 (soglia 0.85): SUPERATO
controllo positivo, giudice B: ctrl:parole 0.819, ctrl:e192 0.884 (soglia 0.85): NON superato
controllo negativo, giudice A: vere contro vere, etichette a caso, AUC media 0.483 (0.519, 0.386, 0.437, 0.459, 0.613), banda 0.45-0.55: SUPERATO
controllo negativo, giudice B: vere contro vere, etichette a caso, AUC media 0.520 (0.495, 0.522, 0.470, 0.538, 0.574), banda 0.45-0.55: SUPERATO

Lettura sul giudizio: giudice migliore fra i validi: A, AUC media 0.751: la rete vede qualcosa che i giudici del paper non vedono (AUC > 0.65): vedi il descrittivo; intervallo al 95% sulle pagine 0.716-0.792: il limite basso supera 0.62.

Lettura sul messaggio, giudice A -> A: AUC 0.518; negativo 0.524; frazione 30% -> 0.900: nessuna traccia con questa sensibilita'; scala: si vede dal 10% di parole sostituite
Lettura sul messaggio, giudice B -> B: AUC 0.501; negativo 0.500; frazione 30% -> 0.642: nessuna traccia con questa sensibilita'; scala: si vede dal 30% di parole sostituite

Semi dei modelli del testo: 2. Valori: AUC media sui libri (errore standard sui libri).

## Libri v21 (con messaggio) contro il Voynich, chiavi 13, 14, 15, 16, 17, 18, 19, 20, 21, 22

AUC di B e B unico = media delle AUC dentro ogni piega; AUC di A = previsioni delle pieghe messe insieme (come e231).

| giudice | AUC media (se) | min-max | IC 95% pagine | limite basso > 0,62 | AUC complessiva (B) | AUC appaiata | meno giudice 2 del paper (se) |
|---|---|---|---|---|---|---|---|
| sorpresa | 0.751 (0.007) | 0.721-0.775 | 0.716-0.792 | si | - | 0.761 | +0.150 (0.006) |
| lettore | 0.510 (0.012) | 0.467-0.590 | 0.487-0.534 | no | 0.513 | 0.514 | -0.092 (0.013) |
| lettore unico | 0.606 (0.003) | 0.594-0.621 | 0.574-0.640 | no | 0.619 | 0.610 | +0.005 (0.007) |

Paper v2, stesse chiavi: giudice 1 e giudice 2 per chiave in `risultati/e409b_*_v21f1_*.json` (media sulle 24 chiavi: 0.554 e 0.601).

| libro | A | B | B unico | giudice 2 del paper |
|---|---|---|---|---|
| a13 | 0.721 | 0.476 | 0.605 | 0.574 |
| a14 | 0.769 | 0.532 | 0.598 | 0.604 |
| a15 | 0.768 | 0.531 | 0.616 | 0.609 |
| a16 | 0.729 | 0.544 | 0.605 | 0.607 |
| a17 | 0.741 | 0.510 | 0.612 | 0.574 |
| a18 | 0.739 | 0.590 | 0.621 | 0.609 |
| a19 | 0.774 | 0.488 | 0.611 | 0.629 |
| a20 | 0.773 | 0.467 | 0.594 | 0.627 |
| a21 | 0.775 | 0.468 | 0.595 | 0.591 |
| a22 | 0.725 | 0.491 | 0.605 | 0.588 |

## Controlli

| insieme | A | B |
|---|---|---|
| ctrl:parole | 0.985 | 0.819 |
| ctrl:e192 | 0.957 | 0.884 |
| ctrl:righe | 0.576 | 0.513 |
| negativo (media di 5 etichette) | 0.483 | 0.520 |

Riferimenti del paper per il giudice 2: parole rimescolate nella riga 0,99; righe rimescolate nella pagina 0,595; e192 0,97 (con il giudice vecchio).

## Messaggio: libri con contro libri senza (chiavi 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24); AUC = media delle AUC per piega, IC 95% col bootstrap sulle chiavi

| insieme | A | B |
|---|---|---|
| msg:ab | 0.518 (0.507-0.530) | 0.501 (0.492-0.510) |
| msg:neg | 0.524 (0.506-0.543) | 0.500 (0.462-0.530) |
| msg:f0.03 | 0.554 (0.552-0.557) | 0.497 (0.491-0.503) |
| msg:f0.1 | 0.680 (0.674-0.686) | 0.512 (0.502-0.521) |
| msg:f0.3 | 0.900 (0.892-0.910) | 0.642 (0.632-0.651) |
| msg:f1.0 | 0.997 (0.996-0.998) | 1.000 (1.000-1.000) |
Paper: AUC 0,506 con le caratteristiche del giudice 2.

## Dove il giudice A trova la differenza (generata meno vera, bit per segno; media sui libri)

| misura | differenza (se) | AUC della sola misura |
|---|---|---|
| bit_medi | +0.1320 (0.0040) | 0.666 |
| bit_sd | +0.1034 (0.0026) | 0.732 |
| bit_p95 | +0.3946 (0.0119) | 0.733 |
| inizio_parola | +0.1889 (0.0060) | 0.704 |
| inizio_riga | +0.1538 (0.0084) | 0.610 |
| dentro_parola | +0.1274 (0.0054) | 0.634 |
| spazio | +0.0402 (0.0040) | 0.574 |
| fine_riga | +0.2103 (0.0114) | 0.578 |
| riga_paragrafo | +0.1433 (0.0063) | 0.636 |
| riga_altra | +0.1232 (0.0039) | 0.653 |
| quarto1 | +0.1256 (0.0054) | 0.620 |
| quarto2 | +0.1433 (0.0053) | 0.656 |
| quarto3 | +0.1226 (0.0049) | 0.623 |
| quarto4 | +0.1367 (0.0066) | 0.642 |

Per sezione (differenza in bit per segno; pagine):

| sezione | pagine | media | inizio parola | inizio riga | dentro parola | spazio | a capo |
|---|---|---|---|---|---|---|---|
| A | 3 | +0.304 | +0.153 | +0.266 | +0.241 | +0.009 | +0.987 |
| B | 19 | +0.124 | +0.247 | +0.066 | +0.110 | +0.068 | +0.176 |
| C | 5 | +0.256 | +0.215 | +0.214 | +0.198 | +0.062 | +0.929 |
| H | 128 | +0.120 | +0.173 | +0.129 | +0.122 | +0.017 | +0.154 |
| P | 16 | +0.116 | +0.174 | +0.105 | +0.100 | +0.094 | +0.334 |
| S | 25 | +0.187 | +0.266 | +0.376 | +0.180 | +0.112 | +0.209 |
| T | 6 | +0.027 | +0.050 | +0.059 | +0.028 | -0.004 | +0.201 |

Per lingua (differenza in bit per segno; pagine):

| lingua | pagine | media | inizio parola | inizio riga | dentro parola | spazio | a capo |
|---|---|---|---|---|---|---|---|
| ? | 6 | +0.175 | +0.114 | +0.174 | +0.127 | -0.064 | +0.663 |
| A | 114 | +0.117 | +0.154 | +0.176 | +0.118 | +0.022 | +0.223 |
| B | 82 | +0.150 | +0.243 | +0.121 | +0.141 | +0.073 | +0.160 |

Coefficienti medi della regressione (misure standardizzate; positivo = piu alto nella generata):

riga_altra -0.82, inizio_parola +0.65, bit_p95 +0.57, bit_sd +0.28, inizio_riga +0.28, quarto2 +0.25, dentro_parola +0.17, fine_riga +0.17, quarto1 -0.16, quarto4 +0.14, bit_medi +0.05, quarto3 -0.05, spazio +0.03, riga_paragrafo -0.01

Modelli del testo (giudice A): bit per segno sulla validazione 1.956; passi 1510.
