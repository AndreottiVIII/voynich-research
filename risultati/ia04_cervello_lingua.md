# ia04 — il cervello di una lingua

controllo positivo: riuscito (13 cifrati su 13 con il cervello giusto migliore, TG >= 0.80 e scarto dal miglior cervello di un'altra famiglia >= 0.10; ammessi 1 falliti; non valutabili 1; TG giusto minimo 1.009; massimo-fra-gli-sbagliati: massimo 0.451, 95° percentile 0.441)
controllo negativo: riuscito (guadagno massimo di un cervello sul testo rimescolato, soglia 0.030 bit: Voynich, segni rimescolati (controllo negativo) -0.0077 (Latin (Abbreviated)); Latin, segni rimescolati (controllo negativo) -0.0001 (Latin (Abbreviated)))

Cervelli: GRU a caratteri (128 unità), addestrati come in e3c95 (40000 segni, arresto sulla validazione), semi 1, 2, 3. Adattamento: immersione e uscita nuove, nucleo bloccato, avvio frequenza, passo 0.01, al massimo 3000 passi, pazienza 15.
Valori: media dei semi (deviazione standard). BPC in bit per segno; g = BPC_casuale - BPC_cervello; TG = g / (BPC_casuale - BPC_zero).

Corse arrivate al massimo dei passi: 347 su 2394.

## Cervelli (BPC sulla prova; i segni sono il numero V dell'alfabeto)

| lingua | famiglia | segni | BPC | passi |
|---|---|---|---|---|
| Anglo-Saxon | germaniche | 27 | 2.502 | 813 |
| Arabic | semitiche | 40 | 3.020 | 800 |
| English | germaniche | 26 | 2.316 | 773 |
| Flemish | germaniche | 28 | 2.127 | 980 |
| French | romanze | 32 | 2.300 | 893 |
| German | germaniche | 34 | 2.257 | 867 |
| Greek | Greek | 28 | 2.526 | 873 |
| Italian | romanze | 30 | 2.282 | 900 |
| Latin (Abbreviated) | romanze | 25 | 3.095 | 767 |
| Latin | romanze | 25 | 2.792 | 813 |
| Mayan (Kaqchikel) | Mayan (Kaqchikel) | 26 | 2.359 | 833 |
| Russian | Russian | 43 | 2.699 | 873 |
| Sanskrit | Sanskrit | 162 | 4.853 | 847 |
| Spanish | romanze | 32 | 2.322 | 947 |
| Chinese (Pinyin) | Chinese (Pinyin) | 47 | 2.052 | 987 |
| Hebrew | semitiche | 30 | 2.919 | 747 |
| Maori | austronesiane | 17 | 1.839 | 873 |
| Swahili | Swahili | 27 | 2.327 | 847 |
| Tagalog | austronesiane | 25 | 1.937 | 907 |
| Turkish | Turkish | 33 | 2.490 | 973 |

## Bersagli: riferimenti e cervelli migliori (per BPC)

| bersaglio | ruolo | segni | casuale | zero | den. min. | 1° (TG) | 2° (TG) | scarto TG | g del 1° |
|---|---|---|---|---|---|---|---|---|---|
| Cifrato: Anglo-Saxon | cifrato | 27 | 3.100 | 2.528 | 0.514 | Anglo-Saxon (1.051) | Russian (0.451) | 0.601 | 0.600 |
| Cifrato: Arabic | cifrato | 40 | 3.510 | 3.063 | 0.416 | Arabic (1.075) | Latin (Abbreviated) (0.436) | 0.638 | 0.479 |
| Cifrato: English | cifrato_altro | 26 | 2.889 | 2.179 | 0.652 | English (0.539) | Latin (Abbreviated) (0.408) | 0.131 | 0.384 |
| Cifrato: Flemish | cifrato_altro | 27 | 2.798 | 2.194 | 0.589 | Flemish (0.522) | Swahili (0.435) | 0.087 | 0.315 |
| Cifrato: French | cifrato | 32 | 3.046 | 2.340 | 0.638 | French (1.045) | Sanskrit (0.435) | 0.610 | 0.735 |
| Cifrato: German | cifrato_altro | 30 | 2.827 | 2.203 | 0.598 | German (0.466) | Greek (0.450) | 0.016 | 0.290 |
| Cifrato: Greek | cifrato | 28 | 3.099 | 2.575 | 0.518 | Greek (1.036) | Latin (0.417) | 0.619 | 0.543 |
| Cifrato: Italian | cifrato_altro | 29 | 3.052 | 2.340 | 0.687 | Italian (0.532) | Turkish (0.433) | 0.099 | 0.379 |
| Cifrato: Latin (Abbreviated) | cifrato | 25 | 3.480 | 3.086 | 0.368 | Latin (Abbreviated) (1.021) | Latin (0.788) | 0.232 | 0.401 |
| Cifrato: Latin | cifrato | 25 | 3.300 | 2.843 | 0.408 | Latin (1.009) | Latin (Abbreviated) (0.735) | 0.274 | 0.459 |
| Cifrato: Russian | cifrato | 43 | 3.332 | 2.769 | 0.543 | Russian (1.066) | German (0.434) | 0.632 | 0.599 |
| Cifrato: Sanskrit | cifrato | 162 | 5.069 | 4.777 | 0.259 | Sanskrit (0.482) | Hebrew (0.252) | 0.231 | 0.139 |
| Cifrato: Spanish | cifrato | 32 | 2.993 | 2.358 | 0.604 | Spanish (1.048) | Latin (Abbreviated) (0.433) | 0.615 | 0.664 |
| Cifrato: Hebrew | cifrato | 30 | 3.359 | 2.926 | 0.400 | Hebrew (1.029) | Arabic (0.441) | 0.589 | 0.445 |
| Cifrato: Maori | cifrato | 17 | 2.384 | 1.825 | 0.546 | Maori (1.031) | Arabic (0.427) | 0.604 | 0.576 |
| Cifrato: Swahili | cifrato | 27 | 2.924 | 2.376 | 0.542 | Swahili (1.009) | Hebrew (0.344) | 0.665 | 0.553 |
| Cifrato: Tagalog | cifrato | 25 | 2.562 | 1.863 | 0.664 | Tagalog (1.032) | Swahili (0.397) | 0.636 | 0.722 |
| Cifrato: Turkish | cifrato | 33 | 3.069 | 2.476 | 0.568 | Turkish (1.050) | Latin (0.378) | 0.672 | 0.621 |
| Voynich | voynich | 25 | 2.117 | 2.016 | 0.090 | Latin (Abbreviated) (0.479) | Hebrew (0.436) | 0.043 | 0.049 |
| Voynich A | voynich | 27 | 2.225 | 2.136 | 0.071 | Latin (Abbreviated) (–) | Hebrew (–) | – | 0.036 |
| Voynich B | voynich | 24 | 1.942 | 1.864 | 0.066 | Hebrew (–) | Latin (Abbreviated) (–) | – | 0.032 |
| Voynich in lettere EVA non fuse (sensibilità) | voynich | 21 | 1.993 | 1.887 | 0.099 | Sanskrit (0.383) | Latin (0.350) | 0.033 | 0.040 |
| Timm e Schinner (seme 1) | generatore | 24 | 2.235 | 2.119 | 0.103 | Latin (Abbreviated) (0.619) | Hebrew (0.600) | 0.019 | 0.074 |
| Voynichizzatore v21 (libro d'esempio) | generatore | 25 | 2.260 | 2.196 | 0.053 | Hebrew (–) | Latin (Abbreviated) (–) | – | 0.026 |
| Naibbe | generatore | 23 | 2.105 | 1.999 | 0.099 | Latin (Abbreviated) (0.598) | Arabic (0.562) | 0.036 | 0.064 |
| Gibberish (Gaskell e Bowern) | generatore | 30 | 4.140 | 4.022 | 0.088 | Latin (Abbreviated) (0.126) | Latin (0.071) | 0.055 | 0.016 |
| Voynich, segni rimescolati (controllo negativo) | negativo | 25 | 3.786 | 3.765 | 0.015 | Latin (Abbreviated) (–) | Hebrew (–) | – | -0.008 |
| Latin, cifrato degradato: omofoni e digrafi (sonda) | sonda | 30 | 3.640 | 3.093 | 0.505 | Sanskrit (0.344) | Latin (Abbreviated) (0.316) | 0.027 | 0.190 |
| Latin, segni rimescolati (controllo negativo) | negativo | 25 | 4.048 | 4.004 | 0.039 | Latin (Abbreviated) (–) | Tagalog (–) | – | -0.000 |

## Controllo positivo, cifrato per cifrato (stesso testo)

| cifrato | riuscito | migliore | TG giusto (ds) | TG miglior sbagliato | scarto qualsiasi | scarto altra famiglia |
|---|---|---|---|---|---|---|
| Cifrato: Anglo-Saxon | sì | Anglo-Saxon | 1.051 (0.055) | 0.451 | 0.601 | 0.601 |
| Cifrato: Arabic | sì | Arabic | 1.075 (0.049) | 0.436 | 0.638 | 0.638 |
| Cifrato: French | sì | French | 1.045 (0.055) | 0.435 | 0.610 | 0.610 |
| Cifrato: Greek | sì | Greek | 1.036 (0.039) | 0.417 | 0.619 | 0.619 |
| Cifrato: Latin (Abbreviated) | sì | Latin (Abbreviated) | 1.021 (0.035) | 0.437 | 0.583 | 0.583 |
| Cifrato: Latin | sì | Latin | 1.009 (0.052) | 0.427 | 0.582 | 0.582 |
| Cifrato: Russian | sì | Russian | 1.066 (0.043) | 0.435 | 0.631 | 0.631 |
| Cifrato: Sanskrit | non valutabile | – | – (–) | – | – | – |
| Cifrato: Spanish | sì | Spanish | 1.048 (0.037) | 0.433 | 0.615 | 0.624 |
| Cifrato: Hebrew | sì | Hebrew | 1.029 (0.030) | 0.441 | 0.589 | 0.602 |
| Cifrato: Maori | sì | Maori | 1.031 (0.004) | 0.427 | 0.604 | 0.604 |
| Cifrato: Swahili | sì | Swahili | 1.009 (0.082) | 0.344 | 0.665 | 0.665 |
| Cifrato: Tagalog | sì | Tagalog | 1.032 (0.009) | 0.397 | 0.636 | 0.636 |
| Cifrato: Turkish | sì | Turkish | 1.050 (0.052) | 0.378 | 0.672 | 0.672 |

## Cifrati descrittivi (altro testo della lingua) e sonda degradata: non contano nel controllo

| bersaglio | tipo | migliore per BPC | TG giusto (ds) | TG miglior sbagliato | scarto qualsiasi | scarto altra famiglia |
|---|---|---|---|---|---|---|
| Cifrato: English | cifrato_altro | English | 0.539 (0.086) | 0.408 | 0.131 | 0.131 |
| Cifrato: Flemish | cifrato_altro | Flemish | 0.522 (0.061) | 0.435 | 0.087 | 0.087 |
| Cifrato: German | cifrato_altro | German | 0.466 (0.031) | 0.450 | 0.016 | 0.016 |
| Cifrato: Italian | cifrato_altro | Italian | 0.532 (0.027) | 0.433 | 0.099 | 0.099 |
| Latin, cifrato degradato: omofoni e digrafi (sonda) | sonda | Sanskrit | 0.316 (0.067) | 0.344 | -0.027 | -0.027 |

## Letture preregistrate (Voynich, generatori, gibberish)

- Voynich: non leggibile: la differenza fra rete casuale e rete da zero è sotto 0.30 bit in un seme (TG instabile). Migliore Latin (Abbreviated) (TG 0.479, ds 0.127), secondo Hebrew (0.436); scarto da qualsiasi altro 0.043, dal miglior cervello di un'altra famiglia 0.043; TG mediano 0.234, minimo 0.088; criterio non raggiunto; con i soli cervelli con almeno tanti segni (19): migliore Latin (Abbreviated), TG 0.479, scarto altra famiglia 0.043, criterio non raggiunto
- Voynich in lettere EVA non fuse (sensibilità): non leggibile: la differenza fra rete casuale e rete da zero è sotto 0.30 bit in un seme (TG instabile). Migliore Sanskrit (TG 0.383, ds 0.153), secondo Latin (0.350); scarto da qualsiasi altro 0.033, dal miglior cervello di un'altra famiglia 0.033; TG mediano 0.165, minimo -0.015; criterio non raggiunto; con i soli cervelli con almeno tanti segni (19): migliore Sanskrit, TG 0.383, scarto altra famiglia 0.033, criterio non raggiunto
- Timm e Schinner (seme 1): non leggibile: la differenza fra rete casuale e rete da zero è sotto 0.30 bit in un seme (TG instabile). Migliore Latin (Abbreviated) (TG 0.619, ds 0.265), secondo Hebrew (0.600); scarto da qualsiasi altro 0.019, dal miglior cervello di un'altra famiglia 0.019; TG mediano 0.414, minimo 0.294; criterio non raggiunto; con i soli cervelli con almeno tanti segni (19): migliore Latin (Abbreviated), TG 0.619, scarto altra famiglia 0.019, criterio non raggiunto
- Naibbe: non leggibile: la differenza fra rete casuale e rete da zero è sotto 0.30 bit in un seme (TG instabile). Migliore Latin (Abbreviated) (TG 0.598, ds 0.039), secondo Arabic (0.562); scarto da qualsiasi altro 0.036, dal miglior cervello di un'altra famiglia 0.036; TG mediano 0.453, minimo 0.377; criterio non raggiunto; con i soli cervelli con almeno tanti segni (19): migliore Latin (Abbreviated), TG 0.598, scarto altra famiglia 0.036, criterio non raggiunto
- Gibberish (Gaskell e Bowern): non leggibile: la differenza fra rete casuale e rete da zero è sotto 0.30 bit in un seme (TG instabile). Migliore Latin (Abbreviated) (TG 0.126, ds 0.063), secondo Latin (0.071); scarto da qualsiasi altro 0.055, dal miglior cervello di un'altra famiglia 0.082; TG mediano -0.166, minimo -0.376; criterio non raggiunto; con i soli cervelli con almeno tanti segni (10): migliore Hebrew, TG -0.091, scarto altra famiglia 0.078, criterio non raggiunto

## Eco delle frequenze e contributo del nucleo (nucleo casuale con lo stesso avvio per frequenza)

| bersaglio | cervelli | eco medio (bit) | nucleo medio (bit) | casuale - zero (bit) | quota eco | cervello migliore: eco / nucleo |
|---|---|---|---|---|---|---|
| Cifrato: Latin | 20 | 0.010 | 0.184 | 0.457 | 0.023 | Latin: 0.014 / 0.445 |
| Cifrato: Spanish | 20 | 0.011 | 0.249 | 0.635 | 0.018 | Spanish: 0.016 / 0.648 |
| Voynich | 20 | 0.003 | 0.023 | 0.101 | 0.029 | Latin (Abbreviated): 0.011 / 0.038 |
| Timm e Schinner (seme 1) | 20 | 0.001 | 0.051 | 0.117 | 0.005 | Latin (Abbreviated): -0.003 / 0.077 |
| Voynichizzatore v21 (libro d'esempio) | 20 | 0.000 | 0.010 | 0.064 | 0.005 | Hebrew: 0.002 / 0.024 |
| Gibberish (Gaskell e Bowern) | 20 | -0.007 | -0.003 | 0.118 | -0.063 | Latin (Abbreviated): -0.005 / 0.020 |
| Voynich, segni rimescolati (controllo negativo) | 20 | -0.001 | -0.018 | 0.021 | -0.036 | Latin (Abbreviated): -0.002 / -0.006 |

## Correlazione dei TG sui cervelli: Voynich contro gli altri bersagli (Spearman)

- Voynich ~ Cifrato: Anglo-Saxon: 0.693
- Voynich ~ Cifrato: Arabic: 0.523
- Voynich ~ Cifrato: English: 0.687
- Voynich ~ Cifrato: Flemish: -0.048
- Voynich ~ Cifrato: French: 0.514
- Voynich ~ Cifrato: German: 0.426
- Voynich ~ Cifrato: Greek: 0.466
- Voynich ~ Cifrato: Italian: 0.242
- Voynich ~ Cifrato: Latin (Abbreviated): 0.589
- Voynich ~ Cifrato: Latin: 0.400
- Voynich ~ Cifrato: Russian: 0.426
- Voynich ~ Cifrato: Sanskrit: 0.662
- Voynich ~ Cifrato: Spanish: 0.495
- Voynich ~ Cifrato: Hebrew: 0.639
- Voynich ~ Cifrato: Maori: 0.260
- Voynich ~ Cifrato: Swahili: 0.352
- Voynich ~ Cifrato: Tagalog: -0.319
- Voynich ~ Cifrato: Turkish: 0.520
- Voynich ~ Voynich in lettere EVA non fuse (sensibilità): 0.481
- Voynich ~ Timm e Schinner (seme 1): 0.441
- Voynich ~ Naibbe: 0.654
- Voynich ~ Gibberish (Gaskell e Bowern): 0.233
- Voynich ~ Latin, cifrato degradato: omofoni e digrafi (sonda): 0.674

## TG per cervello (righe: bersagli; colonne: cervelli)

| bersaglio | Anglo-Sa | Arabic | English | Flemish | French | German | Greek | Italian | Latin (A | Latin | Mayan (K | Russian | Sanskrit | Spanish | Chinese  | Hebrew | Maori | Swahili | Tagalog | Turkish |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cifrato: Anglo-Saxon | 1.05 | 0.41 | 0.41 | 0.35 | 0.41 | 0.43 | 0.42 | 0.41 | 0.44 | 0.43 | 0.40 | 0.45 | 0.43 | 0.41 | 0.36 | 0.42 | 0.36 | 0.35 | 0.34 | 0.41 |
| Cifrato: Arabic | 0.40 | 1.07 | 0.42 | 0.31 | 0.39 | 0.35 | 0.41 | 0.39 | 0.44 | 0.41 | 0.36 | 0.43 | 0.43 | 0.35 | 0.36 | 0.42 | 0.34 | 0.34 | 0.32 | 0.41 |
| Cifrato: English | 0.40 | 0.36 | 0.54 | 0.31 | 0.39 | 0.39 | 0.39 | 0.37 | 0.41 | 0.39 | 0.35 | 0.41 | 0.40 | 0.38 | 0.35 | 0.39 | 0.32 | 0.32 | 0.34 | 0.36 |
| Cifrato: Flemish | 0.39 | 0.42 | 0.38 | 0.52 | 0.40 | 0.40 | 0.38 | 0.40 | 0.40 | 0.39 | 0.37 | 0.43 | 0.43 | 0.42 | 0.41 | 0.40 | 0.34 | 0.43 | 0.43 | 0.42 |
| Cifrato: French | 0.42 | 0.42 | 0.39 | 0.31 | 1.04 | 0.42 | 0.40 | 0.38 | 0.42 | 0.39 | 0.37 | 0.41 | 0.44 | 0.41 | 0.35 | 0.41 | 0.34 | 0.35 | 0.34 | 0.40 |
| Cifrato: German | 0.43 | 0.41 | 0.40 | 0.34 | 0.41 | 0.47 | 0.45 | 0.39 | 0.43 | 0.41 | 0.37 | 0.41 | 0.44 | 0.41 | 0.37 | 0.38 | 0.36 | 0.36 | 0.32 | 0.44 |
| Cifrato: Greek | 0.37 | 0.39 | 0.36 | 0.30 | 0.39 | 0.38 | 1.04 | 0.34 | 0.38 | 0.42 | 0.35 | 0.41 | 0.39 | 0.37 | 0.34 | 0.39 | 0.34 | 0.33 | 0.30 | 0.36 |
| Cifrato: Italian | 0.40 | 0.42 | 0.38 | 0.34 | 0.41 | 0.41 | 0.40 | 0.53 | 0.41 | 0.41 | 0.38 | 0.42 | 0.43 | 0.41 | 0.38 | 0.40 | 0.35 | 0.35 | 0.32 | 0.43 |
| Cifrato: Latin (Abbreviated) | 0.38 | 0.40 | 0.36 | 0.27 | 0.36 | 0.39 | 0.38 | 0.38 | 1.02 | 0.79 | 0.30 | 0.40 | 0.44 | 0.39 | 0.31 | 0.36 | 0.30 | 0.31 | 0.29 | 0.38 |
| Cifrato: Latin | 0.36 | 0.40 | 0.37 | 0.31 | 0.40 | 0.39 | 0.40 | 0.40 | 0.73 | 1.01 | 0.34 | 0.41 | 0.43 | 0.39 | 0.38 | 0.40 | 0.31 | 0.32 | 0.31 | 0.43 |
| Cifrato: Russian | 0.40 | 0.42 | 0.39 | 0.32 | 0.43 | 0.43 | 0.43 | 0.38 | 0.41 | 0.41 | 0.34 | 1.07 | 0.43 | 0.37 | 0.33 | 0.41 | 0.34 | 0.34 | 0.34 | 0.42 |
| Cifrato: Sanskrit | 0.08 | 0.22 | 0.12 | -0.03 | 0.03 | 0.04 | 0.15 | 0.07 | 0.23 | 0.24 | 0.02 | 0.20 | 0.48 | 0.05 | 0.05 | 0.25 | -0.00 | 0.04 | 0.04 | 0.12 |
| Cifrato: Spanish | 0.39 | 0.40 | 0.38 | 0.31 | 0.37 | 0.38 | 0.40 | 0.40 | 0.43 | 0.41 | 0.36 | 0.42 | 0.38 | 1.05 | 0.36 | 0.38 | 0.33 | 0.34 | 0.33 | 0.38 |
| Cifrato: Hebrew | 0.39 | 0.44 | 0.37 | 0.32 | 0.39 | 0.39 | 0.37 | 0.34 | 0.43 | 0.37 | 0.35 | 0.40 | 0.38 | 0.38 | 0.37 | 1.03 | 0.31 | 0.33 | 0.32 | 0.37 |
| Cifrato: Maori | 0.37 | 0.43 | 0.39 | 0.33 | 0.41 | 0.40 | 0.39 | 0.38 | 0.41 | 0.40 | 0.38 | 0.41 | 0.41 | 0.40 | 0.36 | 0.40 | 1.03 | 0.34 | 0.36 | 0.38 |
| Cifrato: Swahili | 0.32 | 0.31 | 0.30 | 0.33 | 0.27 | 0.28 | 0.29 | 0.29 | 0.32 | 0.31 | 0.27 | 0.31 | 0.32 | 0.30 | 0.31 | 0.34 | 0.25 | 1.01 | 0.34 | 0.32 |
| Cifrato: Tagalog | 0.36 | 0.38 | 0.36 | 0.38 | 0.36 | 0.35 | 0.36 | 0.37 | 0.35 | 0.35 | 0.33 | 0.36 | 0.37 | 0.38 | 0.37 | 0.36 | 0.33 | 0.40 | 1.03 | 0.37 |
| Cifrato: Turkish | 0.34 | 0.32 | 0.34 | 0.24 | 0.34 | 0.30 | 0.30 | 0.34 | 0.36 | 0.38 | 0.25 | 0.36 | 0.34 | 0.32 | 0.28 | 0.34 | 0.31 | 0.25 | 0.26 | 1.05 |
| Voynich | 0.35 | 0.23 | 0.26 | 0.19 | 0.13 | 0.32 | 0.20 | 0.09 | 0.48 | 0.31 | 0.23 | 0.30 | 0.39 | 0.27 | 0.19 | 0.44 | 0.18 | 0.19 | 0.23 | 0.21 |
| Voynich A | 0.00 | 0.01 | 0.01 | -0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.04 | 0.03 | 0.02 | 0.01 | 0.02 | 0.00 | 0.02 | 0.03 | -0.00 | 0.01 | 0.00 | 0.01 |
| Voynich B | 0.03 | 0.02 | 0.01 | -0.00 | 0.01 | 0.01 | 0.00 | 0.00 | 0.03 | 0.02 | 0.01 | 0.01 | 0.02 | 0.01 | 0.01 | 0.03 | 0.00 | 0.02 | 0.01 | 0.01 |
| Voynich in lettere EVA non fuse (sensibilità) | 0.29 | 0.13 | 0.28 | 0.17 | 0.16 | -0.01 | 0.00 | 0.16 | 0.28 | 0.35 | 0.28 | 0.34 | 0.38 | 0.14 | 0.26 | 0.35 | 0.12 | 0.15 | 0.10 | 0.15 |
| Timm e Schinner (seme 1) | 0.36 | 0.44 | 0.44 | 0.48 | 0.44 | 0.46 | 0.41 | 0.37 | 0.62 | 0.51 | 0.41 | 0.35 | 0.57 | 0.38 | 0.30 | 0.60 | 0.42 | 0.29 | 0.30 | 0.32 |
| Voynichizzatore v21 (libro d'esempio) | 0.02 | 0.02 | 0.01 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.03 | 0.01 | 0.00 | 0.00 | 0.02 | 0.00 | 0.01 | 0.03 | 0.01 | 0.02 | 0.00 | 0.01 |
| Naibbe | 0.47 | 0.56 | 0.48 | 0.38 | 0.42 | 0.48 | 0.41 | 0.44 | 0.60 | 0.49 | 0.41 | 0.50 | 0.50 | 0.43 | 0.43 | 0.53 | 0.38 | 0.41 | 0.40 | 0.53 |
| Gibberish (Gaskell e Bowern) | -0.10 | -0.12 | -0.19 | -0.31 | -0.18 | -0.22 | -0.16 | -0.24 | 0.13 | 0.07 | -0.06 | -0.23 | -0.22 | -0.38 | -0.17 | -0.09 | 0.04 | -0.15 | 0.02 | -0.17 |
| Voynich, segni rimescolati (controllo negativo) | -0.02 | -0.02 | -0.02 | -0.02 | -0.02 | -0.02 | -0.02 | -0.02 | -0.01 | -0.02 | -0.02 | -0.01 | -0.01 | -0.03 | -0.02 | -0.01 | -0.01 | -0.01 | -0.02 | -0.02 |
| Latin, cifrato degradato: omofoni e digrafi (sonda) | 0.24 | 0.30 | 0.23 | 0.19 | 0.20 | 0.23 | 0.21 | 0.22 | 0.32 | 0.27 | 0.20 | 0.22 | 0.34 | 0.22 | 0.23 | 0.29 | 0.15 | 0.26 | 0.20 | 0.23 |
| Latin, segni rimescolati (controllo negativo) | -0.02 | -0.02 | -0.02 | -0.02 | -0.02 | -0.03 | -0.02 | -0.03 | -0.00 | -0.01 | -0.02 | -0.02 | -0.02 | -0.03 | -0.02 | -0.01 | -0.02 | -0.01 | -0.00 | -0.02 |

(Dove il denominatore è sotto 0.10 bit la cella mostra g, in bit, non TG.)
