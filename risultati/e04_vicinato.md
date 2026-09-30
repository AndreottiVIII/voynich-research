# Esperimento 4: le parole vicine si copiano?

Coppie di parole adiacenti contro coppie prese a caso **nello stesso blocco**.
"Identiche ×": quante volte più spesso le vicine sono la stessa parola.
"Distanza": distanza di edit fra vicine diverse, diviso quella fra coppie a caso del blocco; sotto 1 le vicine si somigliano di più.
Le ultime due colonne ("grappolo") confrontano invece le coppie a caso nel blocco con le coppie a caso in tutto il testo: dicono quanto il vocabolario di una riga o di una pagina è omogeneo rispetto al resto.

| testo | blocco | vicine: identiche × | vicine: distanza | grappolo: identiche × | grappolo: distanza |
|---|---|---|---|---|---|
| **Voynich ZL** | riga vera | 1.01 | 0.993 | 2.70 | 0.959 |
| **Voynich ZL** | pagina vera | 1.17 | 0.987 | 2.11 | 0.971 |
| **Voynich ZL** | 8 parole | 0.94 | 0.999 | 2.68 | 0.959 |
| **Voynich ZL** | 150 parole | 1.19 | 0.986 | 2.06 | 0.971 |
| **Voynich IT** | riga vera | 1.07 | 0.992 | 2.70 | 0.959 |
| **Voynich IT** | pagina vera | 1.21 | 0.987 | 2.16 | 0.970 |
| **Voynich IT** | 8 parole | 1.00 | 0.999 | 2.60 | 0.958 |
| **Voynich IT** | 150 parole | 1.23 | 0.986 | 2.12 | 0.972 |
| Apicio, ricette di cucina | 8 parole | 0.22 | 1.001 | 1.04 | 0.991 |
| Apicio, ricette di cucina | 150 parole | 0.18 | 0.994 | 1.32 | 0.998 |
| Catone, agricoltura e ricette | 8 parole | 0.06 | 0.998 | 2.87 | 0.991 |
| Catone, agricoltura e ricette | 150 parole | 0.07 | 0.992 | 2.32 | 0.995 |
| Columella XII, conserve e ricette | 8 parole | 0.02 | 0.998 | 0.87 | 0.997 |
| Columella XII, conserve e ricette | 150 parole | 0.02 | 0.998 | 1.24 | 0.999 |
| Varrone, agricoltura | 8 parole | 0.02 | 1.001 | 1.33 | 0.995 |
| Varrone, agricoltura | 150 parole | 0.03 | 0.998 | 1.36 | 0.998 |
| Isidoro XVII, piante | 8 parole | 0.05 | 1.005 | 0.97 | 0.996 |
| Isidoro XVII, piante | 150 parole | 0.04 | 1.003 | 1.24 | 0.998 |
| Isidoro XVI, pietre e metalli | 8 parole | 0.05 | 1.001 | 1.12 | 0.996 |
| Isidoro XVI, pietre e metalli | 150 parole | 0.00 | 0.998 | 1.29 | 0.999 |
| Vegezio, arte militare | 8 parole | 0.04 | 1.002 | 1.63 | 1.000 |
| Vegezio, arte militare | 150 parole | 0.04 | 1.002 | 1.42 | 0.999 |
| Vitruvio, architettura | 8 parole | 0.23 | 1.001 | 1.27 | 0.996 |
| Vitruvio, architettura | 150 parole | 0.19 | 1.000 | 1.49 | 0.997 |
| 87 Bibbie (alfabeto e abjad), intervallo | 8 parole | 0.011 – 1.883 (mediana 0.135) | 0.992 – 1.015 (mediana 1.004) | 0.710 – 2.780 (mediana 1.009) | 0.986 – 1.003 (mediana 0.998) |
| 87 Bibbie (alfabeto e abjad), intervallo | 150 parole | 0.009 – 2.286 (mediana 0.109) | 0.985 – 1.018 (mediana 1.004) | 1.100 – 2.348 (mediana 1.311) | 0.995 – 1.001 (mediana 0.998) |
