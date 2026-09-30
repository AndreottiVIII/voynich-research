# Esperimento 17: il Voynich senza spazi, con un risolutore vero

Ipotesi: ogni unità del Voynich vale una lettera (più unità possono valere la stessa lettera), gli spazi non contano. Risolutore: ricottura simulata su 5-grammi di lettere (analisi/ricottura.py), 4 ripartenze. Per ogni modo di contare le unità, il controllo positivo (la lingua stessa, testo non visto in addestramento) e il negativo (un'altra lingua) sono cifrati con lo stesso numero di simboli e hanno la stessa lunghezza del Voynich letto in quel modo.

- **punteggio**: log-probabilità media per lettera del testo decifrato secondo il modello della lingua (più alto è meglio).
- **posizione**: dove cade il punteggio del Voynich fra il controllo negativo (0) e il positivo (1).
- **copertura 6+**: quota delle lettere coperte da parole vere di almeno 6 lettere.
- **coppie**: fra le parole vere (di almeno 4 lettere) trovate una accanto all'altra, quota delle coppie che compaiono nel testo di addestramento.
- **chiave**: nel controllo positivo, quota del testo cifrato con il simbolo attribuito alla lettera giusta.

Ogni cella con tre numeri: controllo positivo / Voynich / controllo negativo.

| lingua | unità | simboli | chiave (positivo) | punteggio | posizione | copertura 6+ | coppie |
|---|---|---|---|---|---|---|---|
| latino | segni EVA | 26 | 100% | -1.79 / -2.94 / -2.90 | -0.03 | 57% / 9% / 8% | 21% / 0% / 0% |
| latino | segni v101 | 59 | 100% | -1.79 / -2.92 / -2.91 | -0.01 | 57% / 9% / 7% | 22% / 0% / 0% |
| latino | gruppi (20 fusioni) | 45 | 100% | -1.79 / -3.20 / -2.93 | -0.23 | 58% / 4% / 8% | 22% / 1% / 0% |
| latino | gruppi (50 fusioni) | 74 | 100% | -1.78 / -3.20 / -2.97 | -0.19 | 58% / 5% / 7% | 22% / 0% / 0% |
| italiano | segni EVA | 26 | 100% | -1.57 / -3.12 / -3.42 | 0.16 | 49% / 2% / 1% | 38% / 0% / 1% |
| italiano | segni v101 | 59 | 100% | -1.57 / -3.15 / -3.38 | 0.13 | 49% / 2% / 2% | 39% / 0% / 0% |
| italiano | gruppi (20 fusioni) | 45 | 100% | -1.58 / -3.55 / -3.39 | -0.09 | 49% / 1% / 2% | 40% / 0% / 1% |
| italiano | gruppi (50 fusioni) | 74 | 100% | -1.56 / -3.68 / -3.42 | -0.14 | 51% / 1% / 2% | 41% / 1% / 0% |
| tedesco | segni EVA | 26 | 100% | -1.56 / -3.35 / -3.52 | 0.09 | 44% / 3% / 3% | 37% / 4% / 1% |
| tedesco | segni v101 | 59 | 100% | -1.56 / -3.40 / -3.49 | 0.05 | 44% / 3% / 3% | 36% / 3% / 0% |
| tedesco | gruppi (20 fusioni) | 45 | 100% | -1.54 / -3.85 / -3.53 | -0.16 | 45% / 3% / 3% | 37% / 12% / 0% |
| tedesco | gruppi (50 fusioni) | 74 | 100% | -1.51 / -3.69 / -3.46 | -0.11 | 45% / 2% / 3% | 38% / 4% / 0% |
| inglese | segni EVA | 26 | 100% | -1.42 / -3.58 / -3.83 | 0.10 | 33% / 0% / 1% | 51% / 0% / 0% |
| inglese | segni v101 | 59 | 100% | -1.42 / -3.35 / -3.92 | 0.23 | 32% / 1% / 1% | 50% / 2% / 0% |
| inglese | gruppi (20 fusioni) | 45 | 100% | -1.43 / -4.10 / -3.88 | -0.09 | 31% / 0% / 0% | 51% / 1% / 0% |
| inglese | gruppi (50 fusioni) | 74 | 100% | -1.42 / -4.05 / -3.95 | -0.04 | 32% / 0% / 0% | 50% / 0% / 1% |
| francese | segni EVA | 26 | 100% | -1.57 / -3.06 / -2.88 | -0.14 | 46% / 2% / 2% | 38% / 1% / 3% |
| francese | segni v101 | 59 | 100% | -1.56 / -3.02 / -2.87 | -0.12 | 46% / 2% / 2% | 39% / 1% / 2% |
| francese | gruppi (20 fusioni) | 45 | 100% | -1.55 / -3.54 / -2.89 | -0.48 | 46% / 2% / 2% | 41% / 1% / 1% |
| francese | gruppi (50 fusioni) | 74 | 100% | -1.56 / -3.38 / -2.92 | -0.33 | 46% / 1% / 2% | 40% / 0% / 1% |
| spagnolo | segni EVA | 26 | 100% | -1.55 / -3.14 / -3.21 | 0.04 | 50% / 3% / 1% | 41% / 1% / 1% |
| spagnolo | segni v101 | 59 | 100% | -1.54 / -3.04 / -3.25 | 0.13 | 51% / 3% / 1% | 42% / 1% / 0% |
| spagnolo | gruppi (20 fusioni) | 45 | 100% | -1.51 / -3.80 / -3.18 | -0.37 | 51% / 1% / 1% | 41% / 0% / 1% |
| spagnolo | gruppi (50 fusioni) | 74 | 100% | -1.49 / -3.71 / -3.29 | -0.24 | 51% / 1% / 1% | 42% / 0% / 1% |
| ceco | segni EVA | 26 | 100% | -1.80 / -3.39 / -3.70 | 0.17 | 48% / 1% / 1% | 36% / 0% / 0% |
| ceco | segni v101 | 59 | 100% | -1.79 / -3.25 / -3.63 | 0.21 | 49% / 3% / 1% | 37% / 0% / 0% |
| ceco | gruppi (20 fusioni) | 45 | 100% | -1.75 / -3.64 / -3.64 | 0.00 | 50% / 1% / 1% | 38% / 0% / 0% |
| ceco | gruppi (50 fusioni) | 74 | 100% | -1.74 / -3.79 / -3.67 | -0.06 | 50% / 1% / 1% | 38% / 0% / 0% |
| ungherese | segni EVA | 26 | 100% | -1.71 / -3.16 / -3.13 | -0.02 | 55% / 6% / 6% | 24% / 1% / 0% |
| ungherese | segni v101 | 59 | 100% | -1.70 / -3.12 / -3.10 | -0.01 | 55% / 4% / 6% | 24% / 0% / 0% |
| ungherese | gruppi (20 fusioni) | 45 | 100% | -1.69 / -3.23 / -3.07 | -0.11 | 55% / 4% / 8% | 24% / 0% / 0% |
| ungherese | gruppi (50 fusioni) | 74 | 100% | -1.63 / -3.49 / -3.08 | -0.28 | 56% / 4% / 7% | 24% / 0% / 0% |
| greco | segni EVA | 26 | 100% | -1.48 / -3.40 / -3.54 | 0.07 | 47% / 1% / 1% | 46% / 8% / 0% |
| greco | segni v101 | 59 | 100% | -1.48 / -3.35 / -3.64 | 0.14 | 47% / 1% / 1% | 47% / 9% / 0% |
| greco | gruppi (20 fusioni) | 45 | 100% | -1.47 / -3.85 / -3.59 | -0.12 | 47% / 1% / 1% | 48% / 0% / 2% |
| greco | gruppi (50 fusioni) | 74 | 100% | -1.44 / -3.87 / -3.58 | -0.14 | 47% / 1% / 1% | 49% / 0% / 1% |
| ebraico | segni EVA | 26 | 100% | -2.28 / -3.00 / -3.52 | 0.42 | 18% / 3% / 1% | 22% / 0% / 0% |
| ebraico | segni v101 | 59 | 100% | -2.18 / -3.25 / -3.56 | 0.23 | 18% / 2% / 1% | 23% / 0% / 0% |
| ebraico | gruppi (20 fusioni) | 45 | 100% | -2.19 / -3.33 / -3.49 | 0.12 | 17% / 1% / 1% | 24% / 0% / 0% |
| ebraico | gruppi (50 fusioni) | 74 | 100% | -2.23 / -3.37 / -3.57 | 0.15 | 16% / 1% / 1% | 22% / 0% / 0% |
| arabo | segni EVA | 26 | 100% | -2.30 / -2.94 / -2.96 | 0.04 | 25% / 1% / 2% | 28% / 3% / 1% |
| arabo | segni v101 | 59 | 100% | -2.13 / -2.79 / -3.10 | 0.32 | 27% / 3% / 2% | 28% / 1% / 1% |
| arabo | gruppi (20 fusioni) | 45 | 100% | -2.18 / -2.99 / -3.05 | 0.07 | 26% / 2% / 2% | 24% / 5% / 1% |
| arabo | gruppi (50 fusioni) | 74 | 100% | -2.19 / -3.12 / -3.09 | -0.03 | 24% / 2% / 2% | 21% / 1% / 1% |
| turco | segni EVA | 26 | 100% | -1.68 / -3.26 / -3.33 | 0.04 | 59% / 9% / 7% | 25% / 0% / 0% |
| turco | segni v101 | 59 | 100% | -1.68 / -3.27 / -3.37 | 0.06 | 59% / 6% / 5% | 25% / 0% / 0% |
| turco | gruppi (20 fusioni) | 45 | 100% | -1.65 / -4.24 / -3.28 | -0.59 | 61% / 1% / 6% | 25% / 0% / 0% |
| turco | gruppi (50 fusioni) | 74 | 100% | -1.62 / -3.85 / -3.26 | -0.36 | 61% / 3% / 5% | 25% / 0% / 0% |
| malgascio | segni EVA | 26 | 100% | -1.34 / -3.29 / -3.71 | 0.18 | 53% / 9% / 7% | 49% / 1% / 0% |
| malgascio | segni v101 | 59 | 100% | -1.34 / -3.12 / -3.52 | 0.18 | 54% / 10% / 9% | 49% / 0% / 1% |
| malgascio | gruppi (20 fusioni) | 45 | 100% | -1.35 / -3.58 / -3.52 | -0.03 | 54% / 6% / 7% | 49% / 0% / 1% |
| malgascio | gruppi (50 fusioni) | 74 | 100% | -1.32 / -3.65 / -3.48 | -0.08 | 56% / 7% / 8% | 51% / 1% / 0% |
| chinanteco | segni EVA | 26 | 98% | -1.36 / -3.32 / -3.08 | -0.14 | 49% / 3% / 7% | 75% / 0% / 0% |
| chinanteco | segni v101 | 59 | 100% | -1.13 / -3.27 / -3.26 | -0.00 | 52% / 4% / 5% | 74% / 0% / 0% |
| chinanteco | gruppi (20 fusioni) | 45 | 100% | -1.14 / -2.95 / -3.14 | 0.10 | 53% / 3% / 5% | 74% / 0% / 0% |
| chinanteco | gruppi (50 fusioni) | 74 | 100% | -1.15 / -3.10 / -3.20 | 0.05 | 52% / 3% / 7% | 74% / 0% / 0% |

Il testo in chiaro (tetto), per confronto:

| lingua | lettere | punteggio | copertura 6+ | coppie | controllo negativo |
|---|---|---|---|---|---|
| latino | 23 | -1.79 | 57% | 21% | Finnish |
| italiano | 21 | -1.57 | 49% | 38% | Finnish |
| tedesco | 23 | -1.56 | 44% | 37% | Finnish |
| inglese | 24 | -1.42 | 33% | 51% | Finnish |
| francese | 24 | -1.57 | 46% | 38% | Finnish |
| spagnolo | 24 | -1.55 | 50% | 41% | Finnish |
| ceco | 23 | -1.80 | 48% | 36% | Finnish |
| ungherese | 23 | -1.71 | 55% | 24% | Latin |
| greco | 24 | -1.48 | 47% | 46% | Finnish |
| ebraico | 27 | -2.25 | 18% | 22% | Finnish |
| arabo | 31 | -2.13 | 27% | 28% | Finnish |
| turco | 23 | -1.68 | 59% | 25% | Finnish |
| malgascio | 21 | -1.34 | 53% | 49% | Finnish |
| chinanteco | 30 | -1.12 | 53% | 74% | Finnish |

## Controlli in più, in latino

| testo | punteggio | copertura 6+ | coppie | chiave | simboli |
|---|---|---|---|---|---|
| Varrone, agricoltura, tetto (testo in chiaro) | -1.94 | 59% | 10% | – | – |
| Varrone, agricoltura, controllo positivo | -1.94 | 59% | 10% | 100% | 32 |
| Isidoro XVII, piante, tetto (testo in chiaro) | -2.01 | 59% | 9% | – | – |
| Isidoro XVII, piante, controllo positivo | -2.01 | 59% | 9% | 100% | 35 |
| cifrario verboso, tetto (testo in chiaro) | -1.80 | 61% | 24% | – | – |
| cifrario verboso, segni | -3.04 | 7% | 0% | – | 16 |
| cifrario verboso, gruppi (20 fusioni) | -3.24 | 3% | 0% | – | 28 |
| cifrario verboso, gruppi (50 fusioni) | -2.05 | 49% | 15% | – | 45 |
| Naibbe (Plinio), segni | -2.88 | 10% | 0% | – | 22 |
| Naibbe (Plinio), gruppi (20 fusioni) | -3.31 | 4% | 0% | – | 40 |
| Naibbe (Plinio), gruppi (50 fusioni) | -3.21 | 5% | 0% | – | 70 |

## Come "legge" il Voynich la chiave migliore

**latino, segni EVA** (le parole vere più frequenti: aper, sita, erum, mosi, etsi, aperi, periit, siet):

```
lusacarutusunummodetdesacsicaresdetta
cesacusesarumssnummodusucicuscustuo
caummsdiraesarummodetceusacictusummoca
cemmoeniiaeniecsetenacmustummoerummoeseruo
```

**latino, gruppi (50 fusioni)** (le parole vere più frequenti: rere, tete, site, idet, etia, side, sere, titi):

```
peenadiieleniniatrinadiniu
niatiiadeslenienititito
naosdaiadenattaiatinsena
nutetianritataiuteito
```

**italiano, segni EVA** (le parole vere più frequenti: dica, agio, anca, aran, medi, rara, dara, arca):

```
taoisitanaramaggioanoaridresitaroandi
sarilararitagromaggioarasedardardai
siaggroetiaritaggioaddaaridesdaraggisi
saggiameeiameasranamidgardaggiataggiaratai
```

**italiano, gruppi (50 fusioni)** (le parole vere più frequenti: aria, edar, asia, rara, data, resi, ieri, adar):

```
leeledaeesireroenviledorea
loemeoedeisireelinenene
leordeoedirannaeenillile
limomialvemenrersiose
```

**tedesco, segni EVA** (le parole vere più frequenti: alle, eder, erste, leer, aber, ebal, halle, isst):

```
saieheranabaralleieniebegbsherebiente
hebenabeberalbiralleiabahsgabgabtae
heallbisreeberalleietgeabegshtaballehe
helleersseersehbenereglabtalleeralleeberae
```

**tedesco, gruppi (50 fusioni)** (le parole vere più frequenti: eder, eden, ende, erde, nein, aner, sein, derer):

```
elsesennlerananseeresenand
ensennselieranlerenenen
eszuesnserageegnsereeres
elenergeenesebnternen
```

**ebraico, segni EVA** (le parole vere più frequenti: ואתה, ללאת, ללאה, ובוא, ובבא, אוכל, באתה, ובבוא):

```
ןכתאמאוכיכיכוכללאשהישהיאניבמאוהישהיוא
מהיארכיהיאוכליתוכללאשכיכמבנכינכיוכא
מאכללישבואהיאוכללאשהונהכיאנבמוכיכללאמא
מהללאהובבאהובהמיהיהואנלכיוכללאהוכללאהיהוכא
```

**ebraico, gruppi (50 fusioni)** (le parole vere più frequenti: לאלה, ואתו, והוא, האלה, והוה, ואתה, הואל, והלא):

```
בםלמלאשתםכתהוהילעמבמלאיהוב
מילאתילארהכתהתםמבעתעתיש
מלבהאלילאתהויעותלעבמיתמל
מראלאבוממואלעפתבאתיאש
```

**controllo: cifrario verboso, gruppi (50 fusioni)**:

```
tharthanetrabsarisetrabsacendelachis
adregemezechiamcamanuvalidahierusalem
ticiascendissentveneruntinhierusalemet
steteruntiuxtaataeductipiscinaesutearioristaeest
```

**controllo: Varrone, agricoltura, controllo positivo**:

```
varrodeagriculturaimterenti
varronisrerumrusticarumdeagriculturaliber
primusiotiumsiessemconsecutusfundania
commodiustibihaecscriberemquaenuncut
```

