# e416 — La larghezza delle righe in caratteri

Preregistrazione: `preregistrazioni/e416.md`. Larghezza di una riga: caratteri EVA delle sue parole più uno spazio per parola. Pagine con almeno 5 righe.

## Sul Voynich

- Pendenza β di log(larghezza) su log(parole), entrambe rispetto alla mediana della pagina: **0,871**.
- Righe oltre 1,25 volte la mediana: 6,0%; oltre 1,5: 2,9%; deviazione dei residui: 0,1241.

## Regolazione del peso (manoscritti senza messaggio, chiavi e416-reg-1 e e416-reg-2)

| peso | oltre 1,25 | oltre 1,5 | residui | pendenza propria |
|---|---|---|---|---|
| 0,0 | 16,7% | 4,9% | 0,1554 | 1,003 |
| 0,01 **(scelto)** | 14,3% | 3,5% | 0,1281 | 0,974 |
| 0,02 | 12,6% | 3,0% | 0,1085 | 0,943 |
| 0,05 | 11,1% | 2,6% | 0,0831 | 0,921 |
| 0,1 | 10,4% | 2,5% | 0,0631 | 0,897 |
| 0,2 | 10,2% | 2,4% | 0,0492 | 0,887 |
| 0,5 | 9,9% | 2,4% | 0,0326 | 0,883 |

Scelto il peso con la deviazione dei residui più vicina a quella del Voynich (0,1241).

## Misura: Isidoro nascosto, 12 chiavi (e409-1 … e409-12)

| | oltre 1,25 | oltre 1,5 | parole oltre 1,5 | residui |
|---|---|---|---|---|
| Voynich | 6,0% | 2,9% | 3,2% | 0,1241 |
| v17 | 16,7% | 5,0% | 3,3% | 0,1543 |
| v18 | 13,8% | 3,7% | 3,3% | 0,1252 |

- Sacchi di pagina identici fra v17 e v18: 12 su 12; gabbia identica: 12 su 12; rilettura esatta della v18: 12 su 12.
- I giudici, la pagella e il cancello della v18 si misurano con l'e409 (`VERSIONE=v18`), stesse chiavi.
