# Esperimento 1: prevedibilità della lettera successiva

Campioni di 175000 simboli (spazi compresi), media di 5 finestre.
h2 è l'incertezza sulla lettera successiva sapendo quella prima: più è bassa, più il testo è prevedibile.

| # | testo | scrittura | simboli | h1 | h2 | h3 | h1 - h2 |
|---|---|---|---|---|---|---|---|
| 1 | **Voynich ZL EVA** | ? | 25 | 3.87 | 2.09 | 1.83 | 1.77 |
| 2 | **Voynich IT EVA** | ? | 22 | 3.87 | 2.10 | 1.82 | 1.77 |
| 3 | Chinese-pinyin | alfabeto | 32 | 4.25 | 2.19 | 1.78 | 2.06 |
| 4 | **Voynich ZL EVA, glifi fusi** | ? | 31 | 3.86 | 2.22 | 1.99 | 1.63 |
| 5 | **Voynich IT EVA, glifi fusi** | ? | 28 | 3.86 | 2.23 | 1.98 | 1.63 |
| 6 | **Voynich ZL EVA, glifi fusi, virgole unite** | ? | 31 | 3.87 | 2.24 | 2.00 | 1.63 |
| 7 | Maori | alfabeto | 15 | 3.45 | 2.51 | 2.17 | 0.94 |
| 8 | **Voynich GC v101** | ? | 70 | 4.03 | 2.52 | 2.28 | 1.50 |
| 9 | Ashaninka-NT | alfabeto | 18 | 3.76 | 2.60 | 2.13 | 1.16 |
| 10 | Malagasy | alfabeto | 29 | 3.75 | 2.68 | 2.21 | 1.06 |
| 11 | Akawaio-NT | alfabeto | 17 | 3.77 | 2.70 | 2.21 | 1.07 |
| 12 | Barasana-NT | alfabeto | 36 | 4.23 | 2.70 | 2.02 | 1.53 |
| 13 | Aukan-NT | alfabeto | 24 | 3.73 | 2.75 | 2.19 | 0.99 |
| 14 | Nahuatl-NT | alfabeto | 31 | 4.04 | 2.78 | 2.14 | 1.26 |
| 15 | Lukpa-NT | alfabeto | 30 | 4.09 | 2.78 | 2.22 | 1.31 |
| 16 | Chinantec-NT | alfabeto | 43 | 4.63 | 2.78 | 1.86 | 1.85 |
| 17 | Tagalog | alfabeto | 26 | 3.66 | 2.79 | 2.26 | 0.87 |
| 18 | Amuzgo-NT | alfabeto | 39 | 4.16 | 2.80 | 2.02 | 1.36 |
| 19 | Quichua-NT | alfabeto | 32 | 3.85 | 2.81 | 2.19 | 1.04 |
| 20 | Zarma | alfabeto | 29 | 3.87 | 2.84 | 2.30 | 1.03 |
| 21 | K'iche'-NT | alfabeto | 29 | 4.13 | 2.85 | 2.16 | 1.28 |
| 22 | Cakchiquel-NT | alfabeto | 33 | 4.15 | 2.85 | 2.12 | 1.30 |
| 23 | Vietnamese | alfabeto | 92 | 4.76 | 2.85 | 2.17 | 1.90 |
| 24 | Vietnamese-tok | alfabeto | 92 | 4.76 | 2.85 | 2.17 | 1.90 |
| 25 | Potawatomi-PART | alfabeto | 18 | 3.65 | 2.86 | 2.52 | 0.80 |
| 26 | Ewe-NT | alfabeto | 44 | 4.22 | 2.86 | 2.37 | 1.36 |
| 27 | Galela-NT | alfabeto | 25 | 3.85 | 2.86 | 2.25 | 0.99 |
| 28 | Cebuano | alfabeto | 26 | 3.74 | 2.86 | 2.26 | 0.88 |
| 29 | Uma-NT | alfabeto | 25 | 3.81 | 2.86 | 2.31 | 0.95 |
| 30 | Camsa-NT | alfabeto | 35 | 4.28 | 2.88 | 2.15 | 1.40 |
| 31 | Creole | alfabeto | 27 | 4.04 | 2.90 | 2.28 | 1.14 |
| 32 | Cabecar-NT | alfabeto | 37 | 4.04 | 2.91 | 2.23 | 1.13 |
| 33 | K'iche'-NT-SIL | alfabeto | 34 | 4.16 | 2.93 | 2.14 | 1.23 |
| 34 | Zulu-NT | alfabeto | 27 | 4.12 | 2.93 | 2.51 | 1.19 |
| 35 | Shona | alfabeto | 24 | 4.08 | 2.94 | 2.44 | 1.14 |
| 36 | Paite | alfabeto | 23 | 3.74 | 2.97 | 2.35 | 0.77 |
| 37 | Indonesian | alfabeto | 25 | 3.95 | 2.97 | 2.37 | 0.98 |
| 38 | Swahili-NT | alfabeto | 26 | 4.00 | 2.99 | 2.52 | 1.01 |
| 39 | Romani-NT | alfabeto | 28 | 3.99 | 2.99 | 2.32 | 1.00 |
| 40 | Achuar-NT | alfabeto | 31 | 3.80 | 3.00 | 2.35 | 0.80 |
| 41 | Xhosa | alfabeto | 27 | 4.13 | 3.01 | 2.56 | 1.12 |
| 42 | Chamorro-PART | alfabeto | 32 | 3.92 | 3.02 | 2.39 | 0.90 |
| 43 | Uspanteco-NT | alfabeto | 32 | 4.16 | 3.02 | 2.19 | 1.15 |
| 44 | Q'eqchi' | alfabeto | 36 | 4.10 | 3.04 | 2.15 | 1.06 |
| 45 | Dinka-NT | alfabeto | 25 | 4.00 | 3.05 | 2.35 | 0.95 |
| 46 | Wolaytta-NT | sillabario | 26 | 3.97 | 3.05 | 2.34 | 0.92 |
| 47 | Jakalteko-NT | alfabeto | 35 | 4.18 | 3.06 | 2.18 | 1.12 |
| 48 | Mam-NT | alfabeto | 34 | 4.14 | 3.07 | 2.24 | 1.07 |
| 49 | Aguaruna-NT | alfabeto | 31 | 3.89 | 3.07 | 2.50 | 0.82 |
| 50 | Afrikaans | alfabeto | 35 | 3.99 | 3.08 | 2.26 | 0.91 |
| 51 | Esperanto | alfabeto | 24 | 4.04 | 3.10 | 2.35 | 0.93 |
| 52 | Somali | alfabeto | 24 | 3.92 | 3.11 | 2.49 | 0.82 |
| 53 | German | alfabeto | 29 | 4.04 | 3.11 | 2.33 | 0.93 |
| 54 | Greek | alfabeto | 25 | 4.01 | 3.11 | 2.44 | 0.89 |
| 55 | Portuguese | alfabeto | 36 | 4.05 | 3.12 | 2.50 | 0.93 |
| 56 | English | alfabeto | 27 | 4.02 | 3.12 | 2.32 | 0.90 |
| 57 | Dutch | alfabeto | 32 | 4.03 | 3.13 | 2.42 | 0.90 |
| 58 | Shuar-NT | alfabeto | 22 | 3.85 | 3.14 | 2.47 | 0.71 |
| 59 | Italian | alfabeto | 28 | 4.01 | 3.16 | 2.56 | 0.86 |
| 60 | Norwegian | alfabeto | 28 | 4.04 | 3.16 | 2.39 | 0.88 |
| 61 | Wolof-NT | alfabeto | 30 | 4.17 | 3.16 | 2.46 | 1.01 |
| 62 | Spanish | alfabeto | 31 | 4.12 | 3.18 | 2.49 | 0.94 |
| 63 | Basque-NT | alfabeto | 32 | 4.03 | 3.18 | 2.55 | 0.85 |
| 64 | English-WEB | alfabeto | 27 | 4.05 | 3.18 | 2.36 | 0.87 |
| 65 | Burmese | abugida | 56 | 4.83 | 3.18 | 2.30 | 1.65 |
| 66 | Tuareg-PART | alfabeto | 41 | 4.05 | 3.19 | 2.61 | 0.86 |
| 67 | Manx-PART | alfabeto | 26 | 3.93 | 3.20 | 2.41 | 0.73 |
| 68 | Estonian-PART | alfabeto | 26 | 4.01 | 3.21 | 2.58 | 0.80 |
| 69 | Danish | alfabeto | 28 | 4.09 | 3.21 | 2.39 | 0.89 |
| 70 | Albanian | alfabeto | 29 | 4.15 | 3.21 | 2.52 | 0.94 |
| 71 | French | alfabeto | 39 | 4.08 | 3.21 | 2.46 | 0.87 |
| 72 | Serbian | alfabeto | 27 | 4.13 | 3.24 | 2.66 | 0.89 |
| 73 | Finnish | alfabeto | 24 | 4.01 | 3.24 | 2.57 | 0.77 |
| 74 | Thai-tok | abugida | 63 | 4.87 | 3.26 | 2.10 | 1.61 |
| 75 | Romanian | alfabeto | 26 | 4.09 | 3.27 | 2.59 | 0.82 |
| 76 | Swedish | alfabeto | 28 | 4.22 | 3.28 | 2.42 | 0.94 |
| 77 | Hindi | abugida | 61 | 4.64 | 3.28 | 2.35 | 1.36 |
| 78 | Gujarati-NT | abugida | 56 | 4.68 | 3.28 | 2.40 | 1.39 |
| 79 | Croatian | alfabeto | 29 | 4.17 | 3.30 | 2.73 | 0.87 |
| 80 | Slovene | alfabeto | 30 | 4.14 | 3.30 | 2.67 | 0.84 |
| 81 | Bulgarian | alfabeto | 33 | 4.17 | 3.30 | 2.61 | 0.87 |
| 82 | Latin | alfabeto | 24 | 3.99 | 3.30 | 2.62 | 0.69 |
| 83 | Malayalam | abugida | 62 | 4.69 | 3.31 | 2.15 | 1.38 |
| 84 | Icelandic | sillabario | 33 | 4.37 | 3.34 | 2.48 | 1.04 |
| 85 | Kabyle-NT | alfabeto | 35 | 4.18 | 3.35 | 2.57 | 0.83 |
| 86 | Marathi | abugida | 60 | 4.68 | 3.36 | 2.40 | 1.32 |
| 87 | Polish | alfabeto | 33 | 4.44 | 3.36 | 2.60 | 1.08 |
| 88 | Tachelhit-NT | abjad | 32 | 4.03 | 3.37 | 2.65 | 0.65 |
| 89 | Latvian-NT | alfabeto | 34 | 4.34 | 3.38 | 2.54 | 0.97 |
| 90 | Japanese-tok | logografica | 1149 | 5.05 | 3.38 | 2.26 | 1.68 |
| 91 | Armenian-PART | alfabeto | 38 | 4.37 | 3.40 | 2.59 | 0.97 |
| 92 | Nepali | abugida | 58 | 4.81 | 3.41 | 2.34 | 1.40 |
| 93 | Turkish | alfabeto | 32 | 4.35 | 3.42 | 2.59 | 0.93 |
| 94 | Coptic-NT | alfabeto | 32 | 4.25 | 3.42 | 2.59 | 0.82 |
| 95 | Syriac-NT | abjad | 23 | 3.94 | 3.43 | 2.71 | 0.51 |
| 96 | Lithuanian | alfabeto | 33 | 4.30 | 3.43 | 2.66 | 0.87 |
| 97 | Kannada | abugida | 60 | 4.74 | 3.44 | 2.34 | 1.30 |
| 98 | Ukranian-NT | alfabeto | 34 | 4.45 | 3.45 | 2.75 | 1.00 |
| 99 | Farsi | abjad | 39 | 4.10 | 3.45 | 2.63 | 0.65 |
| 100 | Russian | alfabeto | 37 | 4.32 | 3.46 | 2.74 | 0.86 |
| 101 | Slovak | alfabeto | 41 | 4.45 | 3.47 | 2.67 | 0.97 |
| 102 | Telugu | abugida | 62 | 4.70 | 3.49 | 2.48 | 1.20 |
| 103 | Hungarian | alfabeto | 33 | 4.39 | 3.49 | 2.59 | 0.90 |
| 104 | Czech | alfabeto | 39 | 4.55 | 3.52 | 2.70 | 1.03 |
| 105 | Hebrew | abjad | 29 | 4.09 | 3.53 | 2.88 | 0.56 |
| 106 | Arabic | abjad | 40 | 4.23 | 3.66 | 2.89 | 0.56 |
| 107 | Cherokee-NT | sillabario | 87 | 5.23 | 3.73 | 2.50 | 1.49 |
| 108 | Ojibwa-NT | sillabario | 116 | 5.40 | 3.81 | 2.47 | 1.60 |
| 109 | Korean | logografica | 905 | 6.28 | 3.84 | 2.69 | 2.44 |
| 110 | Thai | abugida | 63 | 5.24 | 3.88 | 2.44 | 1.36 |
| 111 | Amharic | sillabario | 228 | 5.74 | 4.02 | 2.62 | 1.72 |
| 112 | Chinese-tok | logografica | 2079 | 6.21 | 4.09 | 2.69 | 2.13 |
| 113 | Japanese | logografica | 1279 | 6.81 | 4.20 | 2.38 | 2.61 |
| 114 | Chinese | logografica | 1991 | 5.27 | 4.27 | 2.26 | 1.00 |
