# ia18 — un modello che sa le lingue reimpara il Voynich

controllo positivo, latino cifrato: riuscito (guadagno 0.545 bit per carattere, minimo fra semi 0.545; soglia 0.15)
controllo positivo, latino in chiaro: FALLITO (guadagno 0.559 bit, minimo fra semi 0.559; soglia 0.50; sopra il cifrato di 0.015, soglia 0.10)
controllo negativo: FALLITO (guadagno massimo ammesso 0.05 bit: Latino, lettere rimescolate (controllo negativo) 0.087)

Assegnazione dei segni ai token: letterale. Modello: Qwen2.5-0.5B, vocabolario ridotto a 29 token (29 segni + inizio), fine-tuning completo di tutti i pesi dei due bracci (preaddestrato; pesi casuali dalla configurazione). Finestre di 128 caratteri, 2 finestre per passo, 156 passi (1.0 letture di 40.000 caratteri), passo di apprendimento 5e-05 (preaddestrato) e 0.0002 (casuale), 0.001 per le righe dell'alfabeto. Semi 1, 2.
Valori: media dei semi (deviazione standard). BPC = bit per carattere sulla prova nel punto con la validazione più bassa. G = BPC(pesi casuali) - BPC(preaddestrato): guadagno del preaddestramento; posizione s = (G - G dei negativi) / (G del latino cifrato - G dei negativi).

## Taratura del passo di apprendimento (latino cifrato, seme 0, una lettura; validazione finale in bit)

| braccio | 5e-05 | 0.0001 | 0.0002 | 0.0005 | 0.001 | scelto |
|---|---|---|---|---|---|---|
| preaddestrato | 3.010 | 3.158 | 3.100 | – | – | 5e-05 |
| pesi casuali | – | – | 3.420 | 3.532 | 3.619 | 0.0002 |

## Guadagno del preaddestramento, testo per testo

| testo | ruolo | semi | BPC preaddestrato | BPC casuale | H1 | G (bit) | area fra le curve (bit) | G / BPC casuale | letture a metà strada: preaddestrato | casuale | posizione s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Latino in chiaro | controllo_chiaro | 1 | 2.797 (0.000) | 3.356 (0.000) | 4.117 (0.000) | 0.559 (0.000) | 0.687 (0.000) | 0.167 (0.000) | 0.10 (0.00) | 0.89 (0.00) | 1.03 |
| Latino cifrato (sostituzione semplice) | controllo_cifrato | 1 | 2.860 (0.000) | 3.405 (0.000) | 4.117 (0.000) | 0.545 (0.000) | 0.622 (0.000) | 0.160 (0.000) | 0.18 (0.00) | 0.92 (0.00) | 1.00 |
| Latino, lettere rimescolate (controllo negativo) | controllo_negativo | 1 | 4.009 (0.000) | 4.096 (0.000) | 4.117 (0.000) | 0.087 (0.000) | 0.091 (0.000) | 0.021 (0.000) | 0.60 (0.00) | non raggiunta | 0.00 |

Letture sul Voynich: nessuna (i controlli non sono tutti superati: "non leggibile").

## Token per carattere

| testo | usati | tokenizzazione naturale del modello (descrittivo) |
|---|---|---|
| Latino in chiaro | 1,000 | 0.334 |
| Latino cifrato (sostituzione semplice) | 1,000 | 0.490 |
| Latino, lettere rimescolate (controllo negativo) | 1,000 | 0.452 |
| Gibberish (Gaskell e Bowern) | 1,000 | 0.407 |
| Voynich | 1,000 | 0.418 |
| Voynich, lettere rimescolate (controllo negativo) | 1,000 | 0.470 |
| Timm e Schinner (seme 1) | 1,000 | 0.397 |
| Voynichizzatore v21 (libro d'esempio) | 1,000 | 0.415 |

## Curve di validazione (media dei semi, bit per carattere; colonne = letture del testo di addestramento)

| testo | braccio | 0.00 | 0.10 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---|---|---|---|---|---|---|
| Latino in chiaro | preaddestrato | 13.05 | 3.41 | 3.16 | 2.95 | 2.86 | 2.79 |
| Latino in chiaro | pesi casuali | 5.05 | 4.20 | 3.84 | 3.69 | 3.55 | 3.37 |
| Latino cifrato (sostituzione semplice) | preaddestrato | 11.92 | 3.70 | 3.29 | 3.09 | 2.95 | 2.86 |
| Latino cifrato (sostituzione semplice) | pesi casuali | 5.07 | 4.24 | 3.88 | 3.70 | 3.62 | 3.43 |
| Latino, lettere rimescolate (controllo negativo) | preaddestrato | 13.03 | 4.21 | 4.10 | 4.09 | 4.02 | 4.01 |
| Latino, lettere rimescolate (controllo negativo) | pesi casuali | 5.05 | 4.31 | 4.21 | 4.16 | 4.13 | 4.10 |

