# Esperimento 26: due decifrazioni pubblicate, alla prova dei controlli

Il testo senza messaggio è quello del generatore ad autocitazione di Timm e Schinner (esperimenti 22 e 23): parole copiate e ritoccate, nessun significato.

## Schechter: un glossario EVA → latino

Glossario di 4.063 voci con 947 significati diversi; la sua trascrizione (Takahashi) e il suo modo di leggerla, rifatti in Python: 37.886 parole, copertura 89,2% come dà il suo programma.

| testo | parole decifrate |
|---|---|
| Voynich, col suo glossario | 89,2% |
| Voynich, con un glossario qualunque: le 4.445 parole più frequenti, senza significato | 90,8% |
| testo senza messaggio (Timm e Schinner, programma pubblicato), col suo glossario | 66,8% |
| testo senza messaggio (Timm e Schinner, con le giunture), col suo glossario | 70,5% |

Le parole diverse che il glossario decifra sono 4.445; 2.067 compaiono una volta sola nel manoscritto.

**Pagine lasciate fuori.** Il glossario ridotto alle parole viste nei fogli dispari, provato sui pari (e viceversa), come fa lui; accanto, la quota di parole dei fogli di prova che compaiono già nell'altra metà, qualunque significato abbiano:

| testo | glossario ridotto, sui pari | già viste, sui pari | glossario ridotto, sui dispari | già viste, sui dispari |
|---|---|---|---|---|
| Voynich | 80,9% | 82,1% | 81,2% | 82,7% |
| Timm e Schinner, programma pubblicato | 64,9% | 86,7% | 64,9% | 85,4% |
| Timm e Schinner, con le giunture | 68,8% | 87,9% | 68,4% | 88,1% |

**L'ordine delle parole.** Fra le coppie di parole vicine che il latino conosce, quante compaiono una accanto all'altra nella Latin Library (1.367.764 parole, esclusi i testi di prova); poi le stesse parole rimescolate dentro la riga. Se l'ordine è latino, le coppie vere sono attestate più di quelle rimescolate.

| testo | coppie | attestate | rimescolate | rapporto |
|---|---|---|---|---|
| Voynich decifrato | 16.040 | 8,8% | 8,8% | ×0,99 |
| Timm e Schinner, programma pubblicato, decifrato | 10.153 | 9,7% | 10,0% | ×0,98 |
| Timm e Schinner, con le giunture, decifrato | 10.889 | 7,9% | 8,4% | ×0,94 |
| latino vero (Apicio, Isidoro XVII) | 9.593 | 29,9% | 22,4% | ×1,34 |
| Voynich, significati rimescolati fra le voci | 11.179 | 7,9% | 7,8% | ×1,01 (al massimo 1,10) |

Per i significati rimescolati: media di 20 glossari con gli stessi valori spostati a caso fra le voci.

**Frasi ripetute e legge di Zipf.** Frasi di tre parole (tutte decifrate, dove c'è la traduzione) che ricorrono almeno tre volte in più di un foglio, nel testo e rimescolando tutte le parole (media di 5); pendenza di log(frequenza) su log(rango) sui primi 1.000 ranghi.

| testo | parole | frasi ripetute | rimescolato | Zipf |
|---|---|---|---|---|
| Voynich decifrato | 33.785 | 57 | 4,0 | -1,51 |
| Voynich non decifrato | 37.886 | 13 | 0,0 | -1,00 |
| Timm e Schinner, programma pubblicato, decifrato | 24.107 | 77 | 21,2 | -1,70 |
| Timm e Schinner, programma pubblicato, non decifrato | 36.087 | 21 | 2,2 | -0,99 |
| Timm e Schinner, con le giunture, decifrato | 24.930 | 112 | 24,4 | -1,81 |
| Timm e Schinner, con le giunture, non decifrato | 35.372 | 23 | 1,4 | -1,02 |
| latino vero (Apicio, Isidoro XVII) | 17.696 | 114 | 0,4 | -0,88 |

## Gatta: una corrispondenza EVA → consonanti ebraiche

Quota delle parole decifrate che sono forme della Bibbia in ebraico (46.920 forme senza vocali, dal Nuovo Testamento e da buona parte dell'Antico), contate con la loro frequenza: con la sua corrispondenza, con 200 corrispondenze a caso (media e z), e con una corrispondenza cercata apposta per quel testo (3.000 passi di salita).

| testo | consonanti | sua | a caso | z | cercata apposta | z |
|---|---|---|---|---|---|---|
| Voynich | 3-4 | 35,4% | 12,5% ± 5,2% | 4,4 | 53,0% | 7,8 |
| Voynich | 5+ | 3,1% | 0,2% ± 0,3% | 8,6 | 5,6% | 16,1 |
| Timm e Schinner, programma pubblicato | 3-4 | 29,7% | 13,5% ± 6,0% | 2,7 | 49,5% | 6,0 |
| Timm e Schinner, programma pubblicato | 5+ | 1,4% | 0,2% ± 0,3% | 4,6 | 0,9% | 2,7 |
| Timm e Schinner, con le giunture | 3-4 | 30,7% | 13,7% ± 6,3% | 2,7 | 60,6% | 7,4 |
| Timm e Schinner, con le giunture | 5+ | 1,6% | 0,2% ± 0,3% | 5,0 | 1,3% | 4,1 |

Sul Voynich, con la sua corrispondenza, le parole di 5 o più consonanti trovate sono 28 forme diverse, e le due più frequenti (okaiin → bhytw, 212 volte, okain → brytw, 144 volte) fanno il 69% dei casi. Con la corrispondenza cercata apposta, la più frequente è shedy → bbStm, 428 volte.
