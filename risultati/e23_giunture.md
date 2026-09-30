# Esperimento 23: l'autocitazione con la regola delle giunture

Il generatore di Timm e Schinner (parametri pubblicati, 5 semi per forza, 4000 righe) con una regola in più: la parola nuova si accetta con probabilità min(1, R^forza), dove R dice quanto nel Voynich il suo primo segno segue l'ultimo segno della parola precedente. Forza 0 = il programma originale.

| proprietà | Voynich | forza 0 | forza 1 | forza 2 | forza 3 | testi naturali |
|---|---|---|---|---|---|---|
| incertezza sul segno successivo (h2, bit) | 2,24 | 2,24 (2,23 – 2,26) | 2,22 (2,18 – 2,26) | 2,23 (2,18 – 2,28) | 2,23 (2,20 – 2,29) | 2,6–3,3 a parità di alfabeto |
| spazio prevedibile dal segno precedente | 66% | 54% (51% – 57%) | 57% (55% – 60%) | 58% (53% – 61%) | 58% (56% – 60%) | 6–100%, mediana 17% |
| parole diverse ogni 30.000 | 21% | 14% (13% – 15%) | 13% (12% – 14%) | 14% (13% – 15%) | 14% (13% – 14%) | 3–33% |
| parole usate una volta sola (hapax) | 68% | 52% (51% – 53%) | 52% (51% – 53%) | 52% (51% – 53%) | 51% (49% – 52%) | 12–72% |
| parola identica alla precedente, rispetto alla riga | ×1,01 | ×0,76 (×0,72 – ×0,78) | ×0,73 (×0,70 – ×0,78) | ×0,74 (×0,66 – ×0,83) | ×0,81 (×0,72 – ×0,88) | ×0,01–1,9, mediana ×0,12 |
| somiglianza fra parole della stessa riga | 3,8% | 3,8% (3,5% – 3,9%) | 3,5% (3,2% – 4,0%) | 3,5% (3,4% – 3,7%) | 3,2% (2,8% – 3,6%) | da −0,4% a 1,5% |
| la stessa somiglianza a 6 righe di distanza | 3,4% | 3,4% (3,2% – 3,5%) | 3,1% (2,8% – 3,5%) | 3,3% (3,1% – 3,7%) | 3,1% (2,7% – 3,5%) | vicino a 0 |
| legame fine parola → inizio parola seguente (bit) | 0,188 | 0,016 (0,007 – 0,019) | 0,063 (0,060 – 0,069) | 0,127 (0,120 – 0,130) | 0,178 (0,175 – 0,182) | 0,02–0,40, mediana 0,07 |
| due parole vicine unite danno una parola esistente | 8,8% | 13,9% (12,7% – 15,1%) | 12,8% (12,1% – 13,1%) | 11,5% (10,0% – 13,0%) | 11,8% (10,7% – 12,4%) | 0,1–0,7%, pari al caso |
| lunghezza delle parole (segni) | 4,46 | 4,03 (3,92 – 4,16) | 4,05 (3,98 – 4,10) | 4,15 (4,09 – 4,24) | 4,13 (4,10 – 4,18) |  |
| coppie di segni nell'ordine migliore | 78,5% | 73,0% (72,2% – 74,1%) | 74,5% (74,1% – 75,1%) | 74,3% (73,3% – 75,8%) | 74,4% (73,8% – 74,9%) | 60–96%, mediana 66% |
| parole con un anagramma nel testo | 35,4% | 44,8% (42,2% – 46,2%) | 44,4% (43,7% – 45,1%) | 44,5% (43,7% – 45,2%) | 44,1% (43,0% – 46,7%) | 1–27%, mediana 5% |

Parole vicine unite che esistono, rispetto al caso: Voynich 1,96; forza 0: 1,20; forza 1: 1,19; forza 2: 1,27; forza 3: 1,29.

## Il vocabolario: cambia con i parametri del generatore?

Con la regola a forza 3 e il seme 19, cambiando un parametro alla volta. Un sondaggio: un seme solo.

| variante | parole diverse | hapax | h2 | ripetute | somiglianza nella riga | legame fine-inizio |
|---|---|---|---|---|---|---|
| parametri pubblicati | 13% | 50% | 2,21 | ×0,88 | 3,4% | 0,179 |
| suggerimenti al 20% invece del 40% | 12% | 51% | 2,16 | ×0,74 | 2,6% | 0,196 |
| suggerimenti scelti a caso | 15% | 51% | 2,26 | ×0,80 | 2,9% | 0,171 |
| niente suggerimenti | 14% | 51% | 2,25 | ×0,82 | 3,3% | 0,170 |
| aggiungi e togli al 40% invece del 20% | 11% | 50% | 2,16 | ×0,76 | 3,0% | 0,199 |
| unisci e dividi al 50% invece del 30% | 14% | 50% | 2,19 | ×0,84 | 3,3% | 0,154 |
| parole strane ammesse (errori 5) | 15% | 54% | 2,30 | ×0,76 | 3,1% | 0,191 |
| mai la parola appena scritta come fonte | 10% | 50% | 1,83 | ×0,74 | 1,6% | 0,151 |

Nel Voynich: parole diverse 21%, hapax 68%.

## Un pezzo di testo generato con forza 1 (seme 19, pagina 11)

```
kaiiin daiin aiin chpal cheedy daiiin chdysho sain arair
daiin aiin dan ar aiin chky cheedy daiiin chdysho dar am
aiiin dol cheedy sar dain daram ched chdyshy dol dol dam
ydam aiiin an an
```

## Un pezzo di testo generato con forza 2 (seme 19, pagina 11)

```
qokain ytal yd ockhdy ckhdy ofol okan daiis ypor alchom
qotaiin okal ckhdy dais ckhdackhdy daiin dain yckhdy aly
ckhdy taiin otais yekedy taiin ykchdy shaly okol yckhdy
okoly teed aloaly dais dan
```

## Un pezzo di testo generato con forza 3 (seme 19, pagina 11)

```
pchepo ykair shedy chdchd ainol shchdy sheedy eedy daim
chekar shchdy cheky daiin shchdy okeko daim shchd okair
chety dan shchdy cheto daim shchdy qokeko dain cheto dan
todan daiin chekal shchdy okchd shchdy shchdy chdan chdy
```

