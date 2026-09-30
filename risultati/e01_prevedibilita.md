# Esperimento 1: prevedibilita' della lettera successiva

Campioni di 175000 simboli (spazi compresi), media di 5 finestre.
h2 e' l'incertezza sulla lettera successiva sapendo quella prima: piu' e' bassa, piu' il testo e' prevedibile.

| # | testo | scrittura | simboli | h1 | h2 | h3 | h1 - h2 |
|---|---|---|---|---|---|---|---|
| 1 | **Voynich ZL EVA** | ? | 25 | 3.87 | 2.09 | 1.83 | 1.77 |
| 2 | **Voynich IT EVA** | ? | 22 | 3.87 | 2.10 | 1.82 | 1.77 |
| 3 | **Voynich ZL EVA, glifi fusi** | ? | 31 | 3.86 | 2.22 | 1.99 | 1.63 |
| 4 | **Voynich IT EVA, glifi fusi** | ? | 28 | 3.86 | 2.23 | 1.98 | 1.63 |
| 5 | **Voynich ZL EVA, glifi fusi, virgole unite** | ? | 31 | 3.87 | 2.24 | 2.00 | 1.63 |
| 6 | Maori | alfabeto | 15 | 3.45 | 2.51 | 2.17 | 0.94 |
| 7 | **Voynich GC v101** | ? | 70 | 4.03 | 2.52 | 2.28 | 1.50 |
| 8 | Ashaninka-NT | alfabeto | 18 | 3.76 | 2.60 | 2.13 | 1.16 |
| 9 | Malagasy | alfabeto | 29 | 3.75 | 2.68 | 2.21 | 1.06 |
| 10 | Akawaio-NT | alfabeto | 17 | 3.77 | 2.70 | 2.21 | 1.07 |
| 11 | Barasana-NT | alfabeto | 36 | 4.23 | 2.70 | 2.02 | 1.53 |
| 12 | Aukan-NT | alfabeto | 24 | 3.73 | 2.75 | 2.19 | 0.99 |
| 13 | Nahuatl-NT | alfabeto | 31 | 4.04 | 2.78 | 2.14 | 1.26 |
| 14 | Lukpa-NT | alfabeto | 30 | 4.09 | 2.78 | 2.22 | 1.31 |
| 15 | Chinantec-NT | alfabeto | 43 | 4.63 | 2.78 | 1.86 | 1.85 |
| 16 | Tagalog | alfabeto | 26 | 3.66 | 2.79 | 2.26 | 0.87 |
| 17 | Amuzgo-NT | alfabeto | 39 | 4.16 | 2.80 | 2.02 | 1.36 |
| 18 | Quichua-NT | alfabeto | 32 | 3.85 | 2.81 | 2.19 | 1.04 |
| 19 | Zarma | alfabeto | 29 | 3.87 | 2.84 | 2.30 | 1.03 |
| 20 | K'iche'-NT | alfabeto | 29 | 4.13 | 2.85 | 2.16 | 1.28 |
| 21 | Cakchiquel-NT | alfabeto | 33 | 4.15 | 2.85 | 2.12 | 1.30 |
| 22 | Vietnamese | alfabeto | 92 | 4.76 | 2.85 | 2.17 | 1.90 |
| 23 | Vietnamese-tok | alfabeto | 92 | 4.76 | 2.85 | 2.17 | 1.90 |
| 24 | Potawatomi-PART | alfabeto | 18 | 3.65 | 2.86 | 2.52 | 0.80 |
| 25 | Ewe-NT | alfabeto | 44 | 4.22 | 2.86 | 2.37 | 1.36 |
| 26 | Galela-NT | alfabeto | 25 | 3.85 | 2.86 | 2.25 | 0.99 |
| 27 | Cebuano | alfabeto | 26 | 3.74 | 2.86 | 2.26 | 0.88 |
| 28 | Uma-NT | alfabeto | 25 | 3.81 | 2.86 | 2.31 | 0.95 |
| 29 | Camsa-NT | alfabeto | 35 | 4.28 | 2.88 | 2.15 | 1.40 |
| 30 | Creole | alfabeto | 27 | 4.04 | 2.90 | 2.28 | 1.14 |
| 31 | Cabecar-NT | alfabeto | 37 | 4.04 | 2.91 | 2.23 | 1.13 |
| 32 | K'iche'-NT-SIL | alfabeto | 34 | 4.16 | 2.93 | 2.14 | 1.23 |
| 33 | Zulu-NT | alfabeto | 27 | 4.12 | 2.93 | 2.51 | 1.19 |
| 34 | Shona | alfabeto | 24 | 4.08 | 2.94 | 2.44 | 1.14 |
| 35 | Paite | alfabeto | 23 | 3.74 | 2.97 | 2.35 | 0.77 |
| 36 | Indonesian | alfabeto | 25 | 3.95 | 2.97 | 2.37 | 0.98 |
| 37 | Swahili-NT | alfabeto | 26 | 4.00 | 2.99 | 2.52 | 1.01 |
| 38 | Romani-NT | alfabeto | 28 | 3.99 | 2.99 | 2.32 | 1.00 |
| 39 | Achuar-NT | alfabeto | 31 | 3.80 | 3.00 | 2.35 | 0.80 |
| 40 | Xhosa | alfabeto | 27 | 4.13 | 3.01 | 2.56 | 1.12 |
| 41 | Chamorro-PART | alfabeto | 32 | 3.92 | 3.02 | 2.39 | 0.90 |
| 42 | Uspanteco-NT | alfabeto | 32 | 4.16 | 3.02 | 2.19 | 1.15 |
| 43 | Q'eqchi' | alfabeto | 36 | 4.10 | 3.04 | 2.15 | 1.06 |
| 44 | Dinka-NT | alfabeto | 25 | 4.00 | 3.05 | 2.35 | 0.95 |
| 45 | Wolaytta-NT | sillabario | 26 | 3.97 | 3.05 | 2.34 | 0.92 |
| 46 | Jakalteko-NT | alfabeto | 35 | 4.18 | 3.06 | 2.18 | 1.12 |
| 47 | Mam-NT | alfabeto | 34 | 4.14 | 3.07 | 2.24 | 1.07 |
| 48 | Aguaruna-NT | alfabeto | 31 | 3.89 | 3.07 | 2.50 | 0.82 |
| 49 | Afrikaans | alfabeto | 35 | 3.99 | 3.08 | 2.26 | 0.91 |
| 50 | Esperanto | alfabeto | 24 | 4.04 | 3.10 | 2.35 | 0.93 |
| 51 | Somali | alfabeto | 24 | 3.92 | 3.11 | 2.49 | 0.82 |
| 52 | German | alfabeto | 29 | 4.04 | 3.11 | 2.33 | 0.93 |
| 53 | Greek | alfabeto | 25 | 4.01 | 3.11 | 2.44 | 0.89 |
| 54 | Portuguese | alfabeto | 36 | 4.05 | 3.12 | 2.50 | 0.93 |
| 55 | English | alfabeto | 27 | 4.02 | 3.12 | 2.32 | 0.90 |
| 56 | Dutch | alfabeto | 32 | 4.03 | 3.13 | 2.42 | 0.90 |
| 57 | Shuar-NT | alfabeto | 22 | 3.85 | 3.14 | 2.47 | 0.71 |
| 58 | Italian | alfabeto | 28 | 4.01 | 3.16 | 2.56 | 0.86 |
| 59 | Norwegian | alfabeto | 28 | 4.04 | 3.16 | 2.39 | 0.88 |
| 60 | Wolof-NT | alfabeto | 30 | 4.17 | 3.16 | 2.46 | 1.01 |
| 61 | Spanish | alfabeto | 31 | 4.12 | 3.18 | 2.49 | 0.94 |
| 62 | Basque-NT | alfabeto | 32 | 4.03 | 3.18 | 2.55 | 0.85 |
| 63 | English-WEB | alfabeto | 27 | 4.05 | 3.18 | 2.36 | 0.87 |
| 64 | Burmese | abugida | 56 | 4.83 | 3.18 | 2.30 | 1.65 |
| 65 | Tuareg-PART | alfabeto | 41 | 4.05 | 3.19 | 2.61 | 0.86 |
| 66 | Manx-PART | alfabeto | 26 | 3.93 | 3.20 | 2.41 | 0.73 |
| 67 | Estonian-PART | alfabeto | 26 | 4.01 | 3.21 | 2.58 | 0.80 |
| 68 | Danish | alfabeto | 28 | 4.09 | 3.21 | 2.39 | 0.89 |
| 69 | Albanian | alfabeto | 29 | 4.15 | 3.21 | 2.52 | 0.94 |
| 70 | French | alfabeto | 39 | 4.08 | 3.21 | 2.46 | 0.87 |
| 71 | Serbian | alfabeto | 27 | 4.13 | 3.24 | 2.66 | 0.89 |
| 72 | Finnish | alfabeto | 24 | 4.01 | 3.24 | 2.57 | 0.77 |
| 73 | Thai-tok | abugida | 63 | 4.87 | 3.26 | 2.10 | 1.61 |
| 74 | Romanian | alfabeto | 26 | 4.09 | 3.27 | 2.59 | 0.82 |
| 75 | Swedish | alfabeto | 28 | 4.22 | 3.28 | 2.42 | 0.94 |
| 76 | Hindi | abugida | 61 | 4.64 | 3.28 | 2.35 | 1.36 |
| 77 | Gujarati-NT | abugida | 56 | 4.68 | 3.28 | 2.40 | 1.39 |
| 78 | Croatian | alfabeto | 29 | 4.17 | 3.30 | 2.73 | 0.87 |
| 79 | Slovene | alfabeto | 30 | 4.14 | 3.30 | 2.67 | 0.84 |
| 80 | Bulgarian | alfabeto | 33 | 4.17 | 3.30 | 2.61 | 0.87 |
| 81 | Latin | alfabeto | 24 | 3.99 | 3.30 | 2.62 | 0.69 |
| 82 | Malayalam | abugida | 62 | 4.69 | 3.31 | 2.15 | 1.38 |
| 83 | Icelandic | sillabario | 33 | 4.37 | 3.34 | 2.48 | 1.04 |
| 84 | Kabyle-NT | alfabeto | 35 | 4.18 | 3.35 | 2.57 | 0.83 |
| 85 | Marathi | abugida | 60 | 4.68 | 3.36 | 2.40 | 1.32 |
| 86 | Polish | alfabeto | 33 | 4.44 | 3.36 | 2.60 | 1.08 |
| 87 | Tachelhit-NT | abjad | 32 | 4.03 | 3.37 | 2.65 | 0.65 |
| 88 | Latvian-NT | alfabeto | 34 | 4.34 | 3.38 | 2.54 | 0.97 |
| 89 | Japanese-tok | logografica | 1149 | 5.05 | 3.38 | 2.26 | 1.68 |
| 90 | Armenian-PART | alfabeto | 38 | 4.37 | 3.40 | 2.59 | 0.97 |
| 91 | Nepali | abugida | 58 | 4.81 | 3.41 | 2.34 | 1.40 |
| 92 | Turkish | alfabeto | 32 | 4.35 | 3.42 | 2.59 | 0.93 |
| 93 | Coptic-NT | alfabeto | 32 | 4.25 | 3.42 | 2.59 | 0.82 |
| 94 | Syriac-NT | abjad | 23 | 3.94 | 3.43 | 2.71 | 0.51 |
| 95 | Lithuanian | alfabeto | 33 | 4.30 | 3.43 | 2.66 | 0.87 |
| 96 | Kannada | abugida | 60 | 4.74 | 3.44 | 2.34 | 1.30 |
| 97 | Ukranian-NT | alfabeto | 34 | 4.45 | 3.45 | 2.75 | 1.00 |
| 98 | Farsi | abjad | 39 | 4.10 | 3.45 | 2.63 | 0.65 |
| 99 | Russian | alfabeto | 37 | 4.32 | 3.46 | 2.74 | 0.86 |
| 100 | Slovak | alfabeto | 41 | 4.45 | 3.47 | 2.67 | 0.97 |
| 101 | Telugu | abugida | 62 | 4.70 | 3.49 | 2.48 | 1.20 |
| 102 | Hungarian | alfabeto | 33 | 4.39 | 3.49 | 2.59 | 0.90 |
| 103 | Czech | alfabeto | 39 | 4.55 | 3.52 | 2.70 | 1.03 |
| 104 | Hebrew | abjad | 29 | 4.09 | 3.53 | 2.88 | 0.56 |
| 105 | Arabic | abjad | 40 | 4.23 | 3.66 | 2.89 | 0.56 |
| 106 | Cherokee-NT | sillabario | 87 | 5.23 | 3.73 | 2.50 | 1.49 |
| 107 | Ojibwa-NT | sillabario | 116 | 5.40 | 3.81 | 2.47 | 1.60 |
| 108 | Korean | logografica | 905 | 6.28 | 3.84 | 2.69 | 2.44 |
| 109 | Thai | abugida | 63 | 5.24 | 3.88 | 2.44 | 1.36 |
| 110 | Amharic | sillabario | 228 | 5.74 | 4.02 | 2.62 | 1.72 |
| 111 | Chinese-tok | logografica | 2079 | 6.21 | 4.09 | 2.69 | 2.13 |
| 112 | Japanese | logografica | 1279 | 6.81 | 4.20 | 2.38 | 2.61 |
| 113 | Chinese | logografica | 1991 | 5.27 | 4.27 | 2.26 | 1.00 |
