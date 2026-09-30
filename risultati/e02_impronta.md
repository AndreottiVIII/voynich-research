# Esperimento 2: impronta a livello di parola

Campioni di 30.000 parole, media di 3 finestre. Le misure dopo h2 non cambiano se ogni parola è cifrata sempre nello stesso modo.

- **h2**: incertezza sulla lettera successiva (bit); per il Voynich in glifi.
- **lung.**: lunghezza media delle parole, in lettere o glifi.
- **tipi/parole**: parole diverse diviso parole totali.
- **hapax**: quota delle parole diverse che compaiono una volta sola.
- **IM in più**: quanto una parola dice sulla successiva, oltre il caso (bit).
- **ripetute ×**: quante volte una parola si ripete subito, rispetto al caso.
- **somiglianza vicine**: distanza fra parole vicine diviso distanza fra parole a caso, escluse le ripetizioni identiche; sotto 1 le vicine si somigliano più del caso.

> **Attenzione.** "IM in più" dipende molto dal genere del testo: i testi tecnici latini (esperimento 3) scendono quanto il Voynich. La "poca sintassi" che sembra emergere qui è un effetto del confronto con la Bibbia. Anche "somiglianza vicine" va letta insieme agli esperimenti 4 e 5: quasi tutta viene dalla pagina, non dall'essere adiacenti.

| testo | scrittura | h2 | lung. | tipi/parole | hapax | IM in più | ripetute × | somiglianza vicine |
|---|---|---|---|---|---|---|---|---|
| Japanese | logografica | 4.27 | 11.76 | 0.810 | 0.94 | 0.060 | 2.46 | 0.968 |
| Thai | abugida | 3.93 | 34.08 | 0.898 | 0.96 | 0.065 | 2.55 | 0.954 |
| **Voynich ZL virgole unite** |  | 2.24 | 4.81 | 0.250 | 0.72 | 0.130 | 2.72 | 0.957 |
| **Voynich IT** |  | 2.22 | 4.54 | 0.211 | 0.68 | 0.158 | 2.53 | 0.958 |
| **Voynich GC v101** |  | 2.50 | 3.89 | 0.237 | 0.70 | 0.161 | 1.93 | 0.968 |
| Burmese | abugida | 3.19 | 11.73 | 0.537 | 0.78 | 0.169 | 0.40 | 0.999 |
| **Voynich ZL** |  | 2.22 | 4.48 | 0.209 | 0.68 | 0.171 | 2.38 | 0.962 |
| Telugu | abugida | 3.50 | 6.98 | 0.355 | 0.68 | 0.324 | 0.34 | 1.002 |
| Ojibwa-NT | sillabario | 3.82 | 4.46 | 0.307 | 0.75 | 0.421 | 0.05 | 1.001 |
| Ashaninka-NT | alfabeto | 2.60 | 9.95 | 0.277 | 0.69 | 0.432 | 0.30 | 1.003 |
| Cherokee-NT | sillabario | 3.75 | 4.21 | 0.289 | 0.71 | 0.444 | 0.09 | 0.996 |
| Ukranian-NT | alfabeto | 3.46 | 4.42 | 0.204 | 0.59 | 0.469 | 0.10 | 1.004 |
| Zulu-NT | alfabeto | 2.94 | 7.48 | 0.333 | 0.66 | 0.485 | 0.58 | 0.979 |
| Korean | logografica | 3.80 | 2.87 | 0.293 | 0.61 | 0.493 | 0.14 | 1.004 |
| Basque-NT | alfabeto | 3.18 | 6.25 | 0.211 | 0.55 | 0.494 | 0.06 | 1.005 |
| Shuar-NT | alfabeto | 3.15 | 6.88 | 0.253 | 0.65 | 0.522 | 0.24 | 1.004 |
| Quichua-NT | alfabeto | 2.82 | 7.17 | 0.206 | 0.57 | 0.523 | 0.30 | 1.006 |
| Latvian-NT | alfabeto | 3.38 | 4.90 | 0.196 | 0.57 | 0.530 | 0.07 | 0.999 |
| Marathi | abugida | 3.37 | 5.19 | 0.216 | 0.59 | 0.538 | 0.37 | 0.994 |
| Syriac-NT | abjad | 3.44 | 4.22 | 0.229 | 0.57 | 0.538 | 0.57 | 1.000 |
| Kannada | abugida | 3.41 | 6.66 | 0.289 | 0.64 | 0.551 | 0.25 | 1.002 |
| Latin | alfabeto | 3.30 | 5.34 | 0.195 | 0.56 | 0.554 | 0.05 | 1.000 |
| Lithuanian | alfabeto | 3.43 | 5.51 | 0.217 | 0.56 | 0.583 | 0.07 | 0.994 |
| Xhosa | alfabeto | 3.02 | 6.96 | 0.303 | 0.64 | 0.584 | 0.48 | 0.986 |
| Coptic-NT | alfabeto | 3.43 | 5.46 | 0.261 | 0.64 | 0.586 | 0.21 | 1.003 |
| Hungarian | alfabeto | 3.50 | 5.00 | 0.207 | 0.61 | 0.589 | 0.06 | 1.008 |
| Nepali | abugida | 3.40 | 5.38 | 0.201 | 0.58 | 0.594 | 0.37 | 1.002 |
| Malayalam | abugida | 3.32 | 8.00 | 0.298 | 0.66 | 0.605 | 0.14 | 1.003 |
| Amharic | sillabario | 3.99 | 3.99 | 0.321 | 0.65 | 0.605 | 0.42 | 0.997 |
| Aguaruna-NT | alfabeto | 3.08 | 6.96 | 0.261 | 0.63 | 0.612 | 0.13 | 1.002 |
| Chamorro-PART | alfabeto | 3.01 | 4.70 | 0.131 | 0.57 | 0.619 | 0.02 | 1.017 |
| Finnish | alfabeto | 3.23 | 5.93 | 0.209 | 0.56 | 0.633 | 0.05 | 1.000 |
| Polish | alfabeto | 3.38 | 4.85 | 0.176 | 0.53 | 0.636 | 0.04 | 1.000 |
| Arabic | abjad | 3.67 | 4.31 | 0.278 | 0.61 | 0.636 | 0.29 | 0.998 |
| Turkish | alfabeto | 3.41 | 6.18 | 0.255 | 0.55 | 0.642 | 0.56 | 1.000 |
| Estonian-PART | alfabeto | 3.21 | 4.85 | 0.173 | 0.56 | 0.645 | 0.06 | 0.997 |
| Hebrew | abjad | 3.51 | 3.94 | 0.248 | 0.58 | 0.651 | 0.47 | 0.997 |
| Slovene | alfabeto | 3.30 | 4.37 | 0.165 | 0.51 | 0.670 | 0.03 | 0.996 |
| Icelandic | sillabario | 3.33 | 4.33 | 0.143 | 0.51 | 0.671 | 0.08 | 1.004 |
| Croatian | alfabeto | 3.29 | 4.61 | 0.192 | 0.55 | 0.674 | 0.07 | 0.993 |
| Russian | alfabeto | 3.47 | 4.76 | 0.190 | 0.55 | 0.685 | 0.04 | 0.999 |
| Czech | alfabeto | 3.53 | 4.57 | 0.174 | 0.52 | 0.689 | 0.04 | 1.000 |
| Dutch | alfabeto | 3.13 | 4.35 | 0.110 | 0.48 | 0.692 | 0.12 | 1.006 |
| Amuzgo-NT | alfabeto | 2.81 | 6.05 | 0.140 | 0.57 | 0.693 | 0.21 | 1.002 |
| Slovak | alfabeto | 3.47 | 4.52 | 0.170 | 0.52 | 0.696 | 0.04 | 1.000 |
| Chinese-tok | logografica | 3.97 | 1.60 | 0.197 | 0.61 | 0.713 | 0.21 | 1.001 |
| Armenian-PART | alfabeto | 3.39 | 4.83 | 0.176 | 0.54 | 0.715 | 0.16 | 1.000 |
| Bulgarian | alfabeto | 3.31 | 4.30 | 0.147 | 0.51 | 0.716 | 0.05 | 1.002 |
| Serbian | alfabeto | 3.23 | 4.30 | 0.158 | 0.50 | 0.721 | 0.04 | 0.994 |
| Shona | alfabeto | 2.95 | 6.98 | 0.253 | 0.61 | 0.726 | 0.64 | 0.978 |
| Nahuatl-NT | alfabeto | 2.78 | 6.75 | 0.149 | 0.59 | 0.741 | 0.06 | 1.007 |
| Swahili-NT | alfabeto | 3.00 | 5.50 | 0.184 | 0.60 | 0.747 | 0.18 | 0.999 |
| Gujarati-NT | abugida | 3.31 | 4.33 | 0.164 | 0.55 | 0.750 | 0.13 | 0.987 |
| Paite | alfabeto | 2.96 | 3.86 | 0.110 | 0.50 | 0.752 | 0.16 | 1.004 |
| Tuareg-PART | alfabeto | 3.18 | 4.20 | 0.140 | 0.56 | 0.789 | 0.34 | 1.004 |
| German | alfabeto | 3.10 | 4.51 | 0.106 | 0.46 | 0.797 | 0.10 | 1.001 |
| Potawatomi-PART | alfabeto | 2.86 | 4.58 | 0.220 | 0.72 | 0.798 | 0.32 | 1.014 |
| Swedish | alfabeto | 3.26 | 4.26 | 0.109 | 0.46 | 0.817 | 0.09 | 1.003 |
| Albanian | alfabeto | 3.21 | 4.08 | 0.133 | 0.53 | 0.822 | 0.17 | 1.002 |
| Camsa-NT | alfabeto | 2.90 | 7.35 | 0.180 | 0.61 | 0.827 | 0.02 | 0.999 |
| Dinka-NT | alfabeto | 3.07 | 3.45 | 0.081 | 0.42 | 0.834 | 0.45 | 1.011 |
| Portuguese | alfabeto | 3.13 | 4.16 | 0.122 | 0.51 | 0.837 | 0.04 | 0.993 |
| Ewe-NT | alfabeto | 2.88 | 3.69 | 0.113 | 0.50 | 0.846 | 0.16 | 1.011 |
| Danish | alfabeto | 3.20 | 4.10 | 0.107 | 0.47 | 0.849 | 0.05 | 1.002 |
| Wolaytta-NT | sillabario | 3.06 | 6.54 | 0.208 | 0.56 | 0.858 | 1.00 | 0.997 |
| Norwegian | alfabeto | 3.16 | 3.89 | 0.094 | 0.45 | 0.868 | 0.07 | 1.000 |
| K'iche'-NT | alfabeto | 2.85 | 4.56 | 0.103 | 0.55 | 0.869 | 0.04 | 1.004 |
| Achuar-NT | alfabeto | 3.01 | 6.81 | 0.196 | 0.58 | 0.879 | 0.20 | 1.002 |
| Afrikaans | alfabeto | 3.08 | 3.89 | 0.076 | 0.41 | 0.895 | 0.08 | 1.002 |
| Farsi | abjad | 3.46 | 3.58 | 0.133 | 0.51 | 0.903 | 0.05 | 1.004 |
| Somali | alfabeto | 3.11 | 5.26 | 0.158 | 0.50 | 0.905 | 0.06 | 1.013 |
| Italian | alfabeto | 3.16 | 4.40 | 0.130 | 0.52 | 0.907 | 0.12 | 0.997 |
| Wolof-NT | alfabeto | 3.18 | 3.70 | 0.091 | 0.42 | 0.926 | 0.39 | 1.004 |
| Esperanto | alfabeto | 3.09 | 4.32 | 0.110 | 0.50 | 0.933 | 0.03 | 1.014 |
| Cebuano | alfabeto | 2.86 | 4.69 | 0.105 | 0.54 | 0.945 | 0.03 | 1.008 |
| Tachelhit-NT | abjad | 3.38 | 3.71 | 0.102 | 0.43 | 0.948 | 0.08 | 1.006 |
| Spanish | alfabeto | 3.18 | 4.21 | 0.117 | 0.51 | 0.949 | 0.08 | 0.993 |
| Romani-NT | alfabeto | 3.01 | 4.32 | 0.088 | 0.43 | 0.963 | 0.10 | 1.004 |
| Tagalog | alfabeto | 2.78 | 4.62 | 0.101 | 0.52 | 0.981 | 0.03 | 1.014 |
| Kabyle-NT | alfabeto | 3.36 | 4.07 | 0.130 | 0.53 | 0.987 | 0.10 | 1.006 |
| Malagasy | alfabeto | 2.68 | 4.77 | 0.108 | 0.48 | 1.011 | 0.03 | 1.011 |
| Cakchiquel-NT | alfabeto | 2.85 | 4.37 | 0.077 | 0.46 | 1.029 | 0.02 | 0.997 |
| Lukpa-NT | alfabeto | 2.80 | 3.66 | 0.071 | 0.39 | 1.041 | 0.17 | 1.001 |
| Hindi | abugida | 3.28 | 3.47 | 0.095 | 0.44 | 1.048 | 0.39 | 1.008 |
| Greek | alfabeto | 3.11 | 4.68 | 0.140 | 0.53 | 1.054 | 0.06 | 0.987 |
| Galela-NT | alfabeto | 2.87 | 4.48 | 0.100 | 0.53 | 1.069 | 0.29 | 1.001 |
| Mam-NT | alfabeto | 3.09 | 4.66 | 0.113 | 0.51 | 1.070 | 0.13 | 0.997 |
| English | alfabeto | 3.11 | 3.99 | 0.072 | 0.39 | 1.073 | 0.01 | 1.008 |
| Indonesian | alfabeto | 2.97 | 5.56 | 0.091 | 0.41 | 1.080 | 3.08 | 0.995 |
| Romanian | alfabeto | 3.27 | 3.99 | 0.110 | 0.46 | 1.089 | 0.12 | 1.001 |
| French | alfabeto | 3.21 | 4.04 | 0.106 | 0.48 | 1.098 | 0.14 | 1.004 |
| English-WEB | alfabeto | 3.17 | 3.99 | 0.073 | 0.40 | 1.098 | 0.09 | 1.005 |
| Barasana-NT | alfabeto | 2.73 | 6.05 | 0.154 | 0.61 | 1.110 | 0.25 | 1.006 |
| Manx-PART | alfabeto | 3.20 | 3.85 | 0.077 | 0.40 | 1.112 | 0.13 | 1.011 |
| Cabecar-NT | alfabeto | 2.93 | 4.21 | 0.097 | 0.49 | 1.134 | 0.28 | 1.003 |
| Zarma | alfabeto | 2.84 | 3.43 | 0.055 | 0.36 | 1.154 | 0.17 | 1.008 |
| Jakalteko-NT | alfabeto | 3.07 | 5.05 | 0.114 | 0.55 | 1.166 | 0.12 | 1.011 |
| Aukan-NT | alfabeto | 2.76 | 3.28 | 0.029 | 0.23 | 1.170 | 0.16 | 1.000 |
| Maori | alfabeto | 2.51 | 3.35 | 0.049 | 0.38 | 1.173 | 0.05 | 1.016 |
| Chinantec-NT | alfabeto | 2.80 | 4.87 | 0.095 | 0.53 | 1.235 | 0.17 | 1.003 |
| Creole | alfabeto | 2.91 | 3.30 | 0.047 | 0.31 | 1.236 | 0.47 | 0.996 |
| K'iche'-NT-SIL | alfabeto | 2.93 | 4.09 | 0.070 | 0.44 | 1.246 | 0.03 | 1.005 |
| Uma-NT | alfabeto | 2.87 | 3.94 | 0.076 | 0.42 | 1.298 | 0.60 | 0.995 |
| Thai-tok | abugida | 3.23 | 3.93 | 0.068 | 0.37 | 1.484 | 0.18 | 0.997 |
| Uspanteco-NT | alfabeto | 3.03 | 5.05 | 0.095 | 0.48 | 1.489 | 0.12 | 1.004 |
| Chinese-pinyin | alfabeto | 2.20 | 3.86 | 0.026 | 0.12 | 1.536 | 0.30 | 0.994 |
| Vietnamese-tok | alfabeto | 2.86 | 3.13 | 0.054 | 0.26 | 1.566 | 0.31 | 1.003 |
| Vietnamese | alfabeto | 2.86 | 3.13 | 0.054 | 0.26 | 1.567 | 0.31 | 1.003 |
| Q'eqchi' | alfabeto | 3.04 | 4.07 | 0.070 | 0.41 | 1.569 | 0.08 | 1.000 |
| Akawaio-NT | alfabeto | 2.70 | 3.59 | 0.066 | 0.41 | 1.578 | 0.15 | 1.003 |
| Japanese-tok | logografica | 3.32 | 1.40 | 0.060 | 0.41 | 1.681 | 0.01 | 1.002 |
| Chinese | logografica | 4.19 | 1.00 | 0.050 | 0.23 | 1.728 | 0.41 | 1.000 |
