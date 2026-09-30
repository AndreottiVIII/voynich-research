# Esperimento 22: l'algoritmo completo di Timm e Schinner

Il generatore originale (github.com/TorstenTimm/SelfCitationTextgenerator, commit a6ede22) con i parametri pubblicati, 5 semi, 4000 righe ciascuno (circa 36.700 parole). Il Voynich misurato allo stesso modo, sulle righe e pagine vere del testo in paragrafi (trascrizione ZL, segni composti fusi).

| proprietà | Voynich | generatore (media e intervallo sui semi) | Naibbe | testi naturali |
|---|---|---|---|---|
| incertezza sul segno successivo (h2, bit) | 2,24 | 2,24 (2,23 – 2,26) | 2,16 | 2,6–3,3 a parità di alfabeto |
| spazio prevedibile dal segno precedente | 66% | 54% (51% – 57%) | 64% | 6–100%, mediana 17% |
| parole diverse ogni 30.000 | 21% | 14% (13% – 15%) | 18% | 3–33% |
| parole usate una volta sola (hapax) | 68% | 52% (51% – 53%) | 43% | 12–72% |
| parola identica alla precedente, rispetto alla riga | ×1,01 | ×0,76 (×0,72 – ×0,78) | ×0,44 | ×0,01–1,9, mediana ×0,12 |
| somiglianza fra parole della stessa riga | 3,8% | 3,8% (3,5% – 3,9%) | -0,4% | da −0,4% a 1,5% |
| la stessa somiglianza a 6 righe di distanza | 3,4% | 3,4% (3,2% – 3,5%) | -0,2% | vicino a 0 |
| legame fine parola → inizio parola seguente (bit) | 0,188 | 0,016 (0,007 – 0,019) | 0,002 | 0,02–0,40, mediana 0,07 |
| due parole vicine unite danno una parola esistente | 8,8% | 13,9% (12,7% – 15,1%) | 1,0% | 0,1–0,7%, pari al caso |
| lunghezza delle parole (segni) | 4,46 | 4,03 (3,92 – 4,16) | 4,80 |  |
| coppie di segni nell'ordine migliore | 78,5% | 73,0% (72,2% – 74,1%) | 79,2% | 60–96%, mediana 66% |
| parole con un anagramma nel testo | 35,4% | 44,8% (42,2% – 46,2%) | 27,3% | 1–27%, mediana 5% |

Unione attestata per caso (la stessa seconda parola dopo una prima parola qualsiasi): Voynich 4,5%, generatore 11,7%.

## Un pezzo di testo generato (seme 19, pagina 11)

```
par chdain ydyol chedy edy ar aiin ol shol chsair aroram
chdain chdan chdain cheedy sho aiinol chdaiir chdaiin am
aiinol ainol aiinol dain cheedy chdain chdair sair chdam
chdaiiin chdar cheedy chdaiin cheedy cheed chdaiin daim
```
