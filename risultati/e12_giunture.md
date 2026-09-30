# Esperimento 12: quali spazi sono veri

Per ogni coppia di parole adiacenti: la loro unione è una parola che il testo usa altrove? Il "caso" è la stessa seconda parola preceduta da una prima parola qualsiasi.

| testo | coppie | unione attestata | caso |
|---|---|---|---|
| **Voynich, tutti gli spazi** | 29872 | 9.2% | 4.8% |
| **Voynich, spazi certi** | 27436 | 6.1% | 3.4% |
| **Voynich, spazi incerti** | 2436 | 43.5% | 31.2% |
| Vitruvio | 30000 | 0.2% | 0.3% |
| Bibbia latina | 30000 | 0.1% | 0.3% |
| Bibbia italiana | 30000 | 0.7% | 0.7% |
| Bibbia tedesca | 30000 | 0.3% | 0.5% |

## Giunture del Voynich (almeno 40 coppie)

Morbida: unione attestata almeno nel 30% dei casi; dura: al massimo nel 2%.

| fine | inizio | coppie | unione attestata | spazi incerti | tipo |
|---|---|---|---|---|---|
| o | r | 106 | 56% | 48% | morbida |
| o | a | 47 | 51% | 55% | morbida |
| d | a | 44 | 50% | 48% | morbida |
| s | a | 280 | 49% | 34% | morbida |
| o | k | 116 | 47% | 51% | morbida |
| l | a | 142 | 46% | 33% | morbida |
| o | l | 196 | 46% | 45% | morbida |
| r | a | 870 | 44% | 28% | morbida |
| o | d | 118 | 44% | 38% | morbida |
| l | k | 339 | 42% | 43% | morbida |
| o | t | 44 | 39% | 45% | morbida |
| o | s | 43 | 35% | 33% | morbida |
| l | s | 131 | 34% | 18% | morbida |
| y | sh | 711 | 2% | 3% | dura |
| y | cth | 144 | 1% | 0% | dura |
| n | o | 1454 | 1% | 2% | dura |
| o | q | 84 | 1% | 7% | dura |
| y | r | 256 | 1% | 4% | dura |
| y | o | 2252 | 1% | 1% | dura |
| n | ch | 1263 | 1% | 0% | dura |
| y | q | 3448 | 0% | 1% | dura |
| n | sh | 645 | 0% | 1% | dura |
| y | ckh | 49 | 0% | 0% | dura |
| r | cth | 77 | 0% | 0% | dura |
| r | k | 51 | 0% | 8% | dura |
| y | y | 298 | 0% | 2% | dura |
| y | cph | 42 | 0% | 0% | dura |
| n | ckh | 45 | 0% | 0% | dura |
| y | p | 99 | 0% | 12% | dura |
| n | cth | 116 | 0% | 0% | dura |
| l | cth | 61 | 0% | 2% | dura |
| r | s | 61 | 0% | 5% | dura |
| n | q | 387 | 0% | 0% | dura |
| l | q | 404 | 0% | 2% | dura |
| m | ch | 71 | 0% | 4% | dura |
| r | q | 241 | 0% | 1% | dura |
| m | o | 64 | 0% | 6% | dura |
| d | q | 94 | 0% | 2% | dura |
| n | l | 40 | 0% | 0% | dura |

## Il Voynich risegmentato

Tolti 4028 spazi (gli incerti e quelli alle giunture morbide: d|a, l|a, l|k, l|s, o|a, o|d, o|k, o|l, o|r, o|s, o|t, r|a, s|a).

| versione | parole | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza nella riga | confine |
|---|---|---|---|---|---|---|---|---|
| originale | 34863 | 2.24 | 4.46 | 0.210 | 0.68 | ×1.01 | 3.8% | 0.188 |
| risegmentato | 30835 | 2.24 | 5.04 | 0.276 | 0.74 | ×1.11 | 4.6% | 0.117 |
