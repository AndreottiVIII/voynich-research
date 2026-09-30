# Esperimento 28: le parole uniche e gli errori di lettura

## Due trascrizioni a confronto

Zandbergen-Landini (ZL) contro Takahashi (IT), sulle 4.118 righe in paragrafi che hanno tutte e due (34.815 parole della ZL, senza quelle con segni illeggibili):

- lette allo stesso modo: 87,5%;
- lette diversamente, con lo stesso numero di parole: 5,1% (a un segno di distanza 75% di queste);
- con spazi o parole diversi: 7,4% (701 volte Takahashi unisce due parole della ZL, 344 ne divide una).

Gli scambi più frequenti fra parole a un segno di distanza (ZL → IT): a→o 257, o→a 126, s→r 90, r→s 86, i tolta 73, k→t 42, y→o 41, t→k 39, g→m 35, ch→sh 35, i aggiunta 34, e aggiunta 32.

## Le parole uniche

Sulle prime 30.000 parole della ZL (come nella lista di controllo): 6.293 tipi, di cui 67,9% compaiono una volta sola. Takahashi legge diversamente il 15,5% delle parole uniche e il 4,1% delle altre. Prendendo la sua lettura quando è una parola che il testo usa già (208 casi), le parole uniche scendono al 66,1%.

## Il testo senza messaggio con errori di lettura

Il generatore con la regola delle giunture (esperimento 23, forza 3), più errori come quelli fra le due trascrizioni: per parola, una lettura diversa con probabilità 5,1% (un segno scambiato, aggiunto o tolto, con le frequenze osservate), due parole unite con probabilità 2,0%, una divisa con probabilità 1,0%; moltiplicate per la dose. "Solo segni": niente errori di spazio.

| testo | h2 | spazio | diverse | uniche | ripetute | somiglianza riga | a 6 righe | legame fine-inizio | bit per segno: uniche | ripetute |
|---|---|---|---|---|---|---|---|---|---|---|
| Voynich (ZL) | 2,24 | 66% | 21% | 68% | ×1,01 | 3,8% | 3,4% | 0,188 | 3,38 | 2,15 |
| Voynich (Takahashi) | 2,24 | 67% | 21% | 68% | ×1,07 | 4,0% | 3,5% | 0,169 | 3,38 | 2,13 |
| generatore, seme 19, errori ×0 | 2,21 | 60% | 13% | 50% | ×0,88 | 3,4% | 3,5% | 0,179 | 3,10 | 2,13 |
| generatore, seme 19, errori ×0,5 | 2,25 | 57% | 15% | 56% | ×0,87 | 3,2% | 3,2% | 0,190 | 3,32 | 2,15 |
| generatore, seme 19, errori ×1 | 2,30 | 55% | 17% | 60% | ×0,89 | 3,2% | 3,3% | 0,200 | 3,35 | 2,18 |
| generatore, seme 19, errori ×2 | 2,37 | 52% | 20% | 64% | ×0,97 | 3,1% | 3,2% | 0,214 | 3,38 | 2,23 |
| generatore, seme 19, solo segni ×2 | 2,31 | 57% | 17% | 58% | ×0,86 | 3,2% | 3,3% | 0,164 | 3,53 | 2,17 |
| generatore, seme 19, solo segni ×4 | 2,40 | 55% | 20% | 62% | ×0,83 | 3,2% | 3,2% | 0,150 | 3,57 | 2,22 |
| generatore, seme 1, errori ×0 | 2,29 | 58% | 14% | 51% | ×0,81 | 3,4% | 2,9% | 0,181 | 3,06 | 2,21 |
| generatore, seme 1, errori ×0,5 | 2,33 | 55% | 16% | 57% | ×0,81 | 3,3% | 2,9% | 0,190 | 3,28 | 2,23 |
| generatore, seme 1, errori ×1 | 2,37 | 53% | 18% | 61% | ×0,83 | 3,2% | 2,9% | 0,200 | 3,36 | 2,26 |
| generatore, seme 1, errori ×2 | 2,45 | 50% | 21% | 65% | ×0,89 | 3,0% | 2,7% | 0,205 | 3,42 | 2,31 |

Le ultime due colonne dicono quanto sono regolari le parole: bit per segno secondo un modello a coppie di segni imparato sulle parole ripetute dello stesso testo (prime 30.000 parole). Più alto vuol dire meno regolare: parole uniche che seguono meno le abitudini delle parole ripetute.
