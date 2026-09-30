# Esperimento 24: un vocabolario più vario per l'autocitazione

Il generatore di Timm e Schinner con la regola delle giunture a forza 3 e due regole in più: doppio ritocco (la copia si ritocca una seconda volta) e copia da lontano (la parola si copia dalle pagine già finite). **Distanza**: media degli scarti dal Voynich, sulla scala da lingua tipica (0) a Voynich (1) per le proprietà anomale e in proporzione per parole diverse e hapax; 0 = uguale al Voynich.

## Sondaggio su un seme (19)

| doppio ritocco | copia da lontano | distanza | diverse | hapax | ripetute | somiglianza riga / 6 righe | legame | spazio | h2 |
|---|---|---|---|---|---|---|---|---|---|
| 0% | 0% | 0.195 | 13% | 50% | ×0,88 | 3,4% / 3,5% | 0,179 | 60% | 2,21 |
| 0% | 10% | 0.298 | 13% | 52% | ×0,72 | 1,9% / 1,8% | 0,182 | 59% | 2,18 |
| 0% | 25% | 0.339 | 12% | 51% | ×0,80 | 1,0% / 1,0% | 0,182 | 60% | 2,18 |
| 30% | 0% | 0.192 | 14% | 54% | ×0,83 | 3,6% / 3,2% | 0,178 | 60% | 2,20 |
| 30% | 10% | 0.279 | 13% | 52% | ×0,83 | 2,4% / 2,0% | 0,199 | 60% | 2,19 |
| 30% | 25% | 0.311 | 13% | 55% | ×0,78 | 1,7% / 1,3% | 0,214 | 62% | 2,14 |
| 60% | 0% | 0.264 | 14% | 57% | ×0,60 | 2,9% / 2,4% | 0,192 | 56% | 2,23 |
| 60% | 10% | 0.286 | 16% | 56% | ×0,85 | 2,1% / 1,5% | 0,183 | 58% | 2,29 |
| 60% | 25% | 0.290 | 14% | 55% | ×1,01 | 1,5% / 1,0% | 0,186 | 59% | 2,24 |
| 90% | 0% | 0.234 | 16% | 58% | ×0,91 | 2,9% / 2,1% | 0,188 | 56% | 2,23 |
| 90% | 10% | 0.283 | 15% | 59% | ×0,87 | 2,0% / 1,3% | 0,201 | 59% | 2,25 |
| 90% | 25% | 0.313 | 15% | 57% | ×0,88 | 1,6% / 0,9% | 0,181 | 58% | 2,19 |

## La combinazione più vicina (doppio ritocco 30%, copia da lontano 0%), su 5 semi

| proprietà | Voynich | generatore (media e intervallo) | testi naturali |
|---|---|---|---|
| incertezza sul segno successivo (h2, bit) | 2,24 | 2,22 (2,19 – 2,25) | 2,6–3,3 a parità di alfabeto |
| spazio prevedibile dal segno precedente | 66% | 58% (57% – 60%) | 6–100%, mediana 17% |
| parole diverse ogni 30.000 | 21% | 14% (14% – 14%) | 3–33% |
| parole usate una volta sola (hapax) | 68% | 54% (53% – 55%) | 12–72% |
| parola identica alla precedente, rispetto alla riga | ×1,01 | ×0,77 (×0,73 – ×0,83) | ×0,01–1,9, mediana ×0,12 |
| somiglianza fra parole della stessa riga | 3,8% | 3,2% (2,6% – 3,6%) | da −0,4% a 1,5% |
| la stessa somiglianza a 6 righe di distanza | 3,4% | 2,9% (2,4% – 3,2%) | vicino a 0 |
| legame fine parola → inizio parola seguente (bit) | 0,188 | 0,190 (0,178 – 0,202) | 0,02–0,40, mediana 0,07 |
| due parole vicine unite danno una parola esistente | 8,8% | 13,1% (11,7% – 14,3%) | 0,1–0,7%, pari al caso |
| lunghezza delle parole (segni) | 4,46 | 4,08 (4,00 – 4,13) |  |
| coppie di segni nell'ordine migliore | 78,5% | 75,2% (74,6% – 75,5%) | 60–96%, mediana 66% |
| parole con un anagramma nel testo | 35,4% | 45,0% (43,8% – 46,5%) | 1–27%, mediana 5% |

Parole vicine unite che esistono, rispetto al caso: Voynich 1,96, generatore 1,23.

## Un pezzo di testo generato (seme 19, pagina 11)

```
kain cheor chedyody cheedyod octhal chedyod oshomychar
chedyod edyody chedyod edyod octhal cheedyod ykchal eom
chedyod edyody chedyod chedyod octhar cheedyod okchal od
ycthar cheedyod kcham
```
