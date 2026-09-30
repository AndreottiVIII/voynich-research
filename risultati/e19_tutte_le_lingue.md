# Esperimento 19: il risolutore su tutte le lingue

Il Voynich letto a segni EVA (26 simboli, una riga su due), senza spazi, contro 71 lingue. Per ogni lingua: controllo positivo (la lingua stessa cifrata con 26 simboli e risolta, ritentando una ripartenza alla volta finché la chiave torna, al massimo 4 volte), controllo negativo (un'altra lingua), il Voynich, il Voynich letto da destra a sinistra e il Plinio cifrato col Naibbe, con almeno 2 ripartenze e almeno quante ne sono servite al controllo positivo.

Il risolutore ritrova almeno il 90% della chiave nel controllo positivo in 71 lingue su 71. Dove non ci riesce la posizione non vuol dire niente: quelle lingue sono in fondo alla tabella e fuori dal grafico.

- **posizione**: dove cade il punteggio fra il controllo negativo (0) e il positivo (1), per il Voynich, il Voynich letto al contrario e il Plinio cifrato col Naibbe (che ha la grana del Voynich ma non è una sostituzione di nessuna lingua).

| lingua | famiglia | lettere | chiave (positivo) | punteggio positivo | negativo | Voynich | posizione: Voynich | al contrario | Naibbe | copertura 6+: positivo / Voynich |
|---|---|---|---|---|---|---|---|---|---|---|
| Shona | Niger-Congo | 23 | 100% | -1.52 | -4.90 | -3.32 | 0.47 | 0.31 | 0.33 | 68% / 8.0% |
| Hebrew | Afro-Asiatic | 27 | 100% | -2.26 | -3.60 | -3.11 | 0.37 | 0.39 | 0.39 | 16% / 1.0% |
| Tachelhit | Afro-Asiatic | 22 | 100% | -1.70 | -3.20 | -2.78 | 0.28 | 0.37 | 0.29 | 34% / 1.7% |
| Romanian | Indo-European | 21 | 100% | -1.53 | -3.28 | -2.70 | 0.33 | 0.24 | 0.27 | 53% / 1.2% |
| Paite (Chin) | Sino-Tibetan | 22 | 100% | -1.67 | -2.92 | -2.53 | 0.32 | 0.26 | 0.07 | 54% / 7.4% |
| Farsi (Persian) | Indo-European | 32 | 100% | -2.03 | -3.21 | -2.85 | 0.30 | -0.01 | 0.17 | 29% / 2.3% |
| Croatian | Indo-European | 23 | 100% | -1.98 | -3.77 | -3.25 | 0.29 | 0.17 | 0.21 | 48% / 0.4% |
| Ewe | Niger-Congo | 30 | 100% | -1.74 | -3.71 | -3.33 | 0.20 | 0.27 | 0.09 | 30% / 0.9% |
| Aukan | Creole | 20 | 100% | -1.41 | -3.31 | -3.03 | 0.15 | 0.27 | 0.18 | 23% / 0.2% |
| Galela | West Papuan | 23 | 100% | -1.19 | -4.31 | -3.51 | 0.26 | 0.24 | 0.15 | 55% / 1.1% |
| Russian | Indo-European | 30 | 98% | -1.93 | -3.68 | -3.25 | 0.25 | 0.18 | 0.18 | 50% / 0.9% |
| Serbian | Indo-European | 22 | 100% | -1.81 | -3.73 | -3.26 | 0.24 | 0.22 | 0.16 | 49% / 3.4% |
| Czech | Indo-European | 23 | 100% | -1.74 | -3.61 | -3.57 | 0.02 | 0.22 | 0.12 | 50% / 1.6% |
| Uma | Austronesian | 22 | 100% | -1.42 | -3.79 | -3.28 | 0.22 | 0.22 | 0.17 | 35% / 1.0% |
| Cabécar | Chibchan | 21 | 100% | -1.45 | -3.11 | -2.80 | 0.19 | 0.22 | 0.06 | 40% / 9.1% |
| Lithuanian | Indo-European | 23 | 100% | -1.73 | -3.33 | -3.22 | 0.07 | 0.21 | -0.08 | 58% / 3.5% |
| Malagasy | Austronesian | 21 | 100% | -1.32 | -3.72 | -3.23 | 0.21 | 0.15 | -0.04 | 56% / 9.1% |
| Slovene | Indo-European | 22 | 100% | -1.79 | -3.82 | -3.50 | 0.16 | 0.20 | 0.08 | 48% / 1.6% |
| Bulgarian | Indo-European | 28 | 100% | -1.68 | -3.47 | -3.22 | 0.14 | 0.20 | -0.00 | 52% / 1.0% |
| Cakchiquel | Mayan | 26 | 100% | -1.19 | -4.48 | -3.87 | 0.19 | 0.16 | 0.01 | 52% / 0.5% |
| Amuzgo | Oto-Manguean | 24 | 100% | -1.15 | -3.40 | -3.25 | 0.07 | 0.18 | 0.08 | 69% / 1.7% |
| Estonian | Uralic | 19 | 100% | -1.92 | -2.92 | -2.75 | 0.18 | -0.21 | 0.01 | 39% / 3.0% |
| Chinese (pinyin, una sillaba per parola) | Sino-Tibetan | 30 | 97% | -1.57 | -7.70 | -6.62 | 0.18 | 0.10 | 0.16 | 6% / 0.0% |
| Afrikaans | Indo-European | 22 | 100% | -1.50 | -3.09 | -2.85 | 0.15 | 0.17 | -0.06 | 37% / 1.7% |
| Albanian | Indo-European | 24 | 100% | -1.59 | -3.18 | -3.20 | -0.02 | 0.17 | -0.09 | 43% / 1.2% |
| Swedish | Indo-European | 22 | 100% | -1.61 | -3.24 | -2.98 | 0.16 | 0.12 | 0.00 | 39% / 2.1% |
| Barasana-Eduria | Tucanoan | 20 | 100% | -1.12 | -4.06 | -3.66 | 0.14 | 0.16 | 0.08 | 66% / 6.5% |
| Polish | Indo-European | 24 | 100% | -1.65 | -3.65 | -3.45 | 0.10 | 0.16 | 0.05 | 57% / 0.5% |
| English | Indo-European | 24 | 100% | -1.42 | -3.88 | -3.68 | 0.08 | 0.15 | 0.07 | 31% / 0.8% |
| Haitian Creole | Creole | 24 | 99% | -1.76 | -3.31 | -3.11 | 0.13 | 0.01 | 0.03 | 18% / 0.9% |
| Italian | Indo-European | 21 | 100% | -1.56 | -3.40 | -3.17 | 0.13 | 0.06 | 0.02 | 51% / 1.7% |
| Achuar-Shiwiar | Jivaroan | 21 | 100% | -1.23 | -2.98 | -2.76 | 0.13 | -0.01 | -0.06 | 67% / 14.5% |
| Esperanto | Constructed | 23 | 100% | -1.45 | -3.83 | -3.56 | 0.11 | 0.08 | -0.05 | 45% / 1.1% |
| Camsá | Equatorial (?) | 22 | 100% | -1.13 | -3.49 | -3.22 | 0.11 | -0.04 | -0.04 | 72% / 8.0% |
| Jakalteko | Mayan | 25 | 100% | -1.26 | -3.97 | -3.91 | 0.02 | 0.11 | -0.05 | 48% / 4.0% |
| Norwegian | Indo-European | 23 | 100% | -1.60 | -3.02 | -2.87 | 0.10 | -0.07 | 0.02 | 37% / 7.8% |
| Romani | Indo-European | 25 | 100% | -1.41 | -3.34 | -3.33 | 0.01 | 0.10 | -0.04 | 44% / 0.4% |
| Uspanteco | Mayan | 25 | 100% | -1.13 | -4.15 | -3.91 | 0.08 | 0.02 | -0.01 | 58% / 1.3% |
| Q’eqchi’ | Mayan | 24 | 100% | -1.29 | -3.08 | -2.94 | 0.08 | 0.01 | -0.08 | 38% / 3.9% |
| Indonesian | Austronesian | 24 | 100% | -1.36 | -3.38 | -3.22 | 0.08 | -0.00 | -0.04 | 57% / 3.8% |
| Cebuano | Austronesian | 24 | 100% | -1.38 | -2.65 | -2.55 | 0.08 | -0.22 | -0.28 | 48% / 5.2% |
| German | Indo-European | 23 | 100% | -1.51 | -3.49 | -3.33 | 0.08 | 0.06 | 0.10 | 45% / 3.0% |
| Kabyle | Afro-Asiatic | 25 | 100% | -1.59 | -3.18 | -3.07 | 0.07 | -0.06 | -0.05 | 43% / 0.3% |
| Greek | Indo-European | 24 | 100% | -1.45 | -3.55 | -3.44 | 0.05 | 0.01 | 0.01 | 47% / 3.9% |
| English | Indo-European | 25 | 100% | -1.46 | -3.69 | -3.59 | 0.05 | 0.05 | 0.12 | 33% / 0.1% |
| Spanish | Indo-European | 24 | 100% | -1.49 | -3.23 | -3.40 | -0.10 | 0.04 | 0.01 | 51% / 1.2% |
| Slovak | Indo-European | 23 | 100% | -1.68 | -3.39 | -3.36 | 0.01 | 0.04 | -0.08 | 50% / 1.0% |
| Tagalog | Austronesian | 21 | 100% | -1.45 | -2.60 | -2.56 | 0.04 | -0.27 | -0.39 | 50% / 9.9% |
| Finnish | Uralic | 21 | 100% | -1.53 | -3.03 | -2.99 | 0.03 | 0.04 | 0.06 | 61% / 5.1% |
| K’iche’ | Mayan | 24 | 91% | -1.82 | -4.05 | -4.06 | -0.00 | 0.01 | 0.05 | 38% / 1.0% |
| Vietnamese | Austro-Asiatic | 25 | 100% | -1.65 | -3.45 | -3.69 | -0.13 | 0.01 | -0.10 | 1% / 0.0% |
| Hungarian | Uralic | 23 | 100% | -1.63 | -3.16 | -3.26 | -0.07 | 0.00 | -0.13 | 56% / 2.1% |
| Turkish | Altaic | 23 | 100% | -1.62 | -3.22 | -3.23 | -0.01 | -0.10 | -0.22 | 61% / 11.8% |
| Akawaio | Carib | 16 | 100% | -1.32 | -2.99 | -3.00 | -0.01 | -0.28 | -0.23 | 31% / 1.6% |
| Latin | Indo-European | 23 | 100% | -1.78 | -2.95 | -3.02 | -0.06 | -0.01 | 0.00 | 58% / 8.2% |
| Arabic | Afro-Asiatic | 31 | 98% | -2.34 | -2.88 | -3.00 | -0.21 | -0.02 | -0.24 | 20% / 2.8% |
| Dutch | Indo-European | 23 | 100% | -1.57 | -2.57 | -2.79 | -0.21 | -0.07 | -0.44 | 45% / 5.2% |
| Nahuatl (Tetelcingo) | Uto-Aztecan | 22 | 100% | -1.19 | -3.28 | -3.43 | -0.07 | -0.17 | -0.12 | 64% / 0.8% |
| Chinantec (Quiotepec) | Oto-Manguean | 30 | 98% | -1.34 | -3.24 | -3.39 | -0.08 | -0.10 | -0.14 | 46% / 2.8% |
| Danish | Indo-European | 25 | 100% | -1.65 | -2.93 | -3.10 | -0.13 | -0.15 | -0.15 | 43% / 0.7% |
| Zarma | Nilo-Saharan | 23 | 100% | -1.71 | -2.57 | -2.81 | -0.29 | -0.14 | -0.63 | 25% / 1.4% |
| French | Indo-European | 24 | 100% | -1.56 | -2.89 | -3.14 | -0.19 | -0.15 | -0.35 | 46% / 3.4% |
| K’iche’ | Mayan | 25 | 100% | -1.29 | -3.59 | -3.97 | -0.16 | -0.16 | -0.23 | 41% / 0.2% |
| Xhosa | Niger-Congo | 26 | 100% | -1.65 | -3.27 | -3.60 | -0.21 | -0.22 | -0.43 | 66% / 4.5% |
| Lukpa | Niger-Congo | 24 | 100% | -1.53 | -2.30 | -2.48 | -0.23 | -0.85 | -0.70 | 32% / 0.4% |
| Wolof | Niger-Congo | 23 | 100% | -1.77 | -2.50 | -2.70 | -0.28 | -0.27 | -0.89 | 26% / 4.1% |
| Portuguese | Indo-European | 23 | 100% | -1.52 | -2.56 | -2.87 | -0.30 | -0.35 | -0.45 | 51% / 2.6% |
| Somali | Afro-Asiatic | 23 | 100% | -1.43 | -2.28 | -2.56 | -0.33 | -0.52 | -0.41 | 56% / 11.1% |
| Mam | Mayan | 25 | 100% | -1.32 | -2.95 | -3.69 | -0.45 | -0.42 | -0.40 | 49% / 0.2% |
| Maori | Austronesian | 14 | 100% | -1.53 | -2.32 | -2.71 | -0.49 | -0.64 | -0.57 | 30% / 1.2% |
| Dinka | Nilo-Saharan | 24 | 100% | -1.69 | -1.85 | -3.18 | -8.00 | -6.73 | -9.27 | 25% / 0.5% |

In Dinka il controllo negativo arriva quasi al punteggio del positivo, con una chiave degenere che ripete poche lettere: la scala si schiaccia e le posizioni escono enormi. Non vogliono dire niente.

## Come "legge" il Voynich la chiave migliore, nelle lingue dove arriva più in alto

**Shona** (voynich):

```
mawitikaiamakaiiswaiwamiamatikamwairi
tiaiimwakiamikaiiswaraaamiaatramaiisti
taimiwaamaaiispampaiis
aramoiwaipaiairamwtpaaiiswarami
```

**Hebrew** (voynich al contrario):

```
בנהיתהיאבמוהרבהיתהיתחללואוהוהואבמבתומ
במחללוהונמורבהוירניתחללואבהיבאותהללובמ
חללוטהודחללורהוותבהלומ
בהוניתחללויטמתהונביבידהיתבההוני
```

**Tachelhit** (voynich al contrario):

```
isgantanitstnitanganfllarataganitinam
itfllatastsnitaansanfllanitainsntllait
fllaktabfllantasnitlat
itasanfllaaktntasiaiabganiutasa
```

