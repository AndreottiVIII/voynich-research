# e3c95 — imparabilità per un modello minuscolo

Modello a caratteri GRU (128 unità nascoste), 40000 segni di addestramento, 5000 di validazione, 10000 di prova, al massimo 2000 passi, semi 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
Corse arrivate al massimo dei passi: 0.
Valori: media dei semi (deviazione standard fra i semi).

## Controlli

- positivo: differenza_bpc -0.0016, soglia 0.0200, superato True
- negativo: G_rimescolato 0.0479, G_voynich 0.4979, G_min_lingue 0.2262, superato True

## Misure per testo

| testo | ruolo | segni | H1 | BPC | G | E90 | D | scarto | epoche | s/corsa |
|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | voynich | 25 | 3.947 | 1.982 | 0.498 (0.021) | 3.789 (0.495) | 0.104 (0.015) | 0.013 | 29.286 | 64 |
| Voynich A | voynich | 25 | 3.968 | 2.138 | 0.461 (0.005) | 4.096 (0.000) | 0.099 (0.012) | 0.065 | 31.539 | 82 |
| Voynich B | voynich | 25 | 3.923 | 1.867 | 0.524 (0.011) | 3.174 (0.324) | 0.117 (0.018) | 0.038 | 30.925 | 79 |
| Voynich, segni rimescolati (controllo negativo) | controllo | 25 | 3.948 | 3.759 | 0.048 (0.002) | 3.891 (0.808) | – (–) | -0.004 | 14.438 | 40 |
| Voynich in lettere EVA non fuse (sensibilità) | sensibilita | 21 | 3.965 | 1.861 | 0.531 (0.021) | 3.379 (0.495) | – (–) | 0.061 | 30.310 | 63 |
| Timm e Schinner (seme 1) | generatore | 24 | 3.807 | 2.191 | 0.425 (0.026) | 3.789 (0.691) | 0.029 (0.015) | 0.178 | 28.672 | 63 |
| Voynichizzatore v21 (libro d'esempio) | generatore | 25 | 3.963 | 2.141 | 0.460 (0.023) | 3.072 (0.000) | 0.074 (0.011) | 0.060 | 28.467 | 60 |
| Naibbe | generatore | 23 | 3.957 | 1.998 | 0.495 (0.004) | 3.174 (0.324) | 0.006 (0.007) | 0.051 | 32.461 | 67 |
| Gibberish (Gaskell e Bowern) | generatore | 30 | 4.453 | 3.992 | 0.104 (0.014) | 7.373 (1.793) | -0.009 (0.014) | 0.232 | 17.203 | 42 |
| Anglo-Saxon | lingua | 27 | 4.227 | 2.491 | 0.411 (0.013) | 12.902 (0.716) | 0.055 (0.018) | 0.255 | 31.027 | 64 |
| Arabic | lingua | 54 | 4.502 | 3.010 | 0.331 (0.016) | 16.998 (0.716) | 0.052 (0.019) | 0.246 | 36.045 | 91 |
| Arabic, letterario | trasferimento | 54 | 3.430 | 2.067 | 0.397 (0.017) | 15.974 (1.542) | – (–) | 0.070 | 48.333 | 116 |
| English | lingua | 26 | 4.139 | 2.319 | 0.440 (0.019) | 13.619 (1.085) | 0.099 (0.035) | 0.302 | 35.021 | 89 |
| English, letterario | trasferimento | 26 | 4.129 | 2.221 | 0.462 (0.016) | 14.131 (0.941) | – (–) | 0.237 | 33.792 | 85 |
| Flemish | lingua | 28 | 4.118 | 2.148 | 0.478 (0.018) | 15.155 (1.163) | 0.051 (0.023) | 0.318 | 40.653 | 102 |
| Flemish, letterario | trasferimento | 28 | 4.033 | 2.194 | 0.456 (0.014) | 13.005 (0.495) | – (–) | 0.268 | 36.147 | 92 |
| French | lingua | 32 | 4.237 | 2.320 | 0.452 (0.010) | 15.258 (0.756) | 0.084 (0.012) | 0.305 | 38.605 | 76 |
| German | lingua | 33 | 4.307 | 2.219 | 0.485 (0.015) | 14.438 (0.897) | 0.075 (0.024) | 0.297 | 36.352 | 92 |
| German, letterario | trasferimento | 33 | 4.170 | 2.224 | 0.467 (0.010) | 13.926 (0.864) | – (–) | 0.218 | 36.352 | 89 |
| Greek | lingua | 28 | 4.201 | 2.535 | 0.397 (0.007) | 13.517 (0.648) | 0.028 (0.013) | 0.284 | 33.075 | 68 |
| Italian | lingua | 30 | 4.141 | 2.304 | 0.444 (0.015) | 14.746 (0.529) | 0.038 (0.009) | 0.240 | 34.918 | 87 |
| Italian, letterario | trasferimento | 30 | 4.144 | 2.372 | 0.428 (0.014) | 15.258 (1.318) | – (–) | 0.277 | 36.864 | 91 |
| Latin (Abbreviated) | lingua | 25 | 4.136 | 3.126 | 0.244 (0.011) | 12.800 (1.106) | 0.000 (0.014) | 0.209 | 28.979 | 76 |
| Latin (Abbreviated), letterario | trasferimento | 25 | 4.087 | 2.995 | 0.267 (0.011) | 15.462 (1.018) | – (–) | 0.258 | 30.822 | 79 |
| Latin | lingua | 25 | 4.131 | 2.829 | 0.315 (0.013) | 13.414 (0.897) | -0.002 (0.011) | 0.221 | 31.130 | 80 |
| Latin, letterario | trasferimento | 25 | 4.078 | 2.514 | 0.383 (0.008) | 14.438 (0.756) | – (–) | 0.244 | 33.690 | 85 |
| Mayan (Kaqchikel) | lingua | 26 | 4.061 | 2.354 | 0.420 (0.010) | 14.336 (0.965) | 0.085 (0.017) | 0.330 | 34.918 | 71 |
| Russian | lingua | 43 | 4.639 | 2.716 | 0.415 (0.015) | 15.155 (0.648) | 0.072 (0.015) | 0.302 | 36.250 | 75 |
| Sanskrit | lingua | 160 | 6.203 | 4.800 | 0.226 (0.021) | 17.715 (0.971) | 0.043 (0.023) | 0.645 | 33.792 | 91 |
| Sanskrit, letterario | trasferimento | 160 | 6.050 | 4.573 | 0.244 (0.009) | 17.613 (1.348) | – (–) | 0.479 | 33.485 | 92 |
| Spanish | lingua | 32 | 4.202 | 2.361 | 0.438 (0.017) | 14.950 (0.716) | 0.076 (0.019) | 0.315 | 38.912 | 77 |
| Chinese (Pinyin) | lingua | 47 | 4.664 | 2.029 | 0.565 (0.010) | 8.704 (0.540) | 0.205 (0.030) | 0.199 | 37.990 | 78 |
| Hebrew | lingua | 30 | 4.182 | 2.926 | 0.300 (0.008) | 13.722 (0.989) | 0.057 (0.010) | 0.211 | 29.491 | 62 |
| Maori | lingua | 17 | 3.554 | 1.829 | 0.485 (0.012) | 12.390 (1.018) | 0.209 (0.021) | 0.139 | 33.485 | 66 |
| Swahili | lingua | 27 | 4.085 | 2.321 | 0.432 (0.010) | 15.667 (0.971) | 0.045 (0.013) | 0.287 | 36.352 | 57 |
| Tagalog | lingua | 25 | 3.810 | 1.920 | 0.496 (0.013) | 14.438 (0.324) | 0.157 (0.018) | 0.205 | 35.635 | 54 |
| Turkish | lingua | 33 | 4.459 | 2.488 | 0.442 (0.010) | 14.950 (0.529) | 0.033 (0.020) | 0.340 | 38.502 | 57 |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | 25 | 4.131 | 2.827 | 0.316 (0.012) | 13.619 (0.971) | – (–) | 0.232 | 31.846 | 50 |
| Latin, cifrato con Vigenère (periodo 7) | cifrato | 25 | 4.456 | 3.443 | 0.227 (0.009) | 18.432 (0.683) | 0.463 (0.024) | 0.151 | 31.334 | 49 |

## Trasferimento (T, bit per segno)

| da -> a | T |
|---|---|
| Voynich A -> Voynich B | 0.447 (0.058) |
| Voynich B -> Voynich A | 0.402 (0.040) |
| Arabic -> Arabic, letterario | 6.628 (0.428) |
| Arabic, letterario -> Arabic | 8.454 (0.594) |
| English -> English, letterario | 0.715 (0.105) |
| English, letterario -> English | 0.792 (0.105) |
| Flemish -> Flemish, letterario | 1.018 (0.092) |
| Flemish, letterario -> Flemish | 0.926 (0.113) |
| German -> German, letterario | 1.362 (0.096) |
| German, letterario -> German | 1.562 (0.104) |
| Italian -> Italian, letterario | 0.798 (0.073) |
| Italian, letterario -> Italian | 0.697 (0.046) |
| Latin (Abbreviated) -> Latin (Abbreviated), letterario | 0.388 (0.052) |
| Latin (Abbreviated), letterario -> Latin (Abbreviated) | 0.377 (0.060) |
| Latin -> Latin, letterario | 0.434 (0.033) |
| Latin, letterario -> Latin | 0.427 (0.036) |
| Sanskrit -> Sanskrit, letterario | 0.946 (0.075) |
| Sanskrit, letterario -> Sanskrit | 0.952 (0.122) |

## Posizione rispetto alle lingue

- G, Voynich: 0.498, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 95%
- G, Voynich A: 0.461, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 75%
- G, Voynich B: 0.524, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 95%
- G, Voynich, segni rimescolati (controllo negativo): 0.048, sotto l'intervallo delle lingue [0.226, 0.565], lingue sotto: 0%
- G, Voynich in lettere EVA non fuse (sensibilità): 0.531, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 95%
- G, Timm e Schinner (seme 1): 0.425, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 45%
- G, Voynichizzatore v21 (libro d'esempio): 0.460, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 75%
- G, Naibbe: 0.495, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 90%
- G, Gibberish (Gaskell e Bowern): 0.104, sotto l'intervallo delle lingue [0.226, 0.565], lingue sotto: 0%
- G, Latin, cifrato con una sostituzione (controllo positivo): 0.316, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 20%
- G, Latin, cifrato con Vigenère (periodo 7): 0.227, dentro l'intervallo delle lingue [0.226, 0.565], lingue sotto: 5%
- E90, Voynich: 3.789, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Voynich A: 4.096, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Voynich B: 3.174, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Voynich, segni rimescolati (controllo negativo): 3.891, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Voynich in lettere EVA non fuse (sensibilità): 3.379, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Timm e Schinner (seme 1): 3.789, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Voynichizzatore v21 (libro d'esempio): 3.072, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Naibbe: 3.174, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Gibberish (Gaskell e Bowern): 7.373, sotto l'intervallo delle lingue [8.704, 17.715], lingue sotto: 0%
- E90, Latin, cifrato con una sostituzione (controllo positivo): 13.619, dentro l'intervallo delle lingue [8.704, 17.715], lingue sotto: 30%
- E90, Latin, cifrato con Vigenère (periodo 7): 18.432, sopra l'intervallo delle lingue [8.704, 17.715], lingue sotto: 100%
- D, Voynich: 0.104, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 85%
- D, Voynich A: 0.099, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 80%
- D, Voynich B: 0.117, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 85%
- D, Timm e Schinner (seme 1): 0.029, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 15%
- D, Voynichizzatore v21 (libro d'esempio): 0.074, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 60%
- D, Naibbe: 0.006, dentro l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 10%
- D, Gibberish (Gaskell e Bowern): -0.009, sotto l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 0%
- D, Latin, cifrato con Vigenère (periodo 7): 0.463, sopra l'intervallo delle lingue [-0.002, 0.209], lingue sotto: 100%
- D_relativo, Voynich: 0.053, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 85%
- D_relativo, Voynich A: 0.046, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 85%
- D_relativo, Voynich B: 0.063, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 85%
- D_relativo, Timm e Schinner (seme 1): 0.013, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 25%
- D_relativo, Voynichizzatore v21 (libro d'esempio): 0.035, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 70%
- D_relativo, Naibbe: 0.003, dentro l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 10%
- D_relativo, Gibberish (Gaskell e Bowern): -0.002, sotto l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 0%
- D_relativo, Latin, cifrato con Vigenère (periodo 7): 0.134, sopra l'intervallo delle lingue [-0.001, 0.115], lingue sotto: 100%
- bpc, Voynich: 1.982, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 10%
- bpc, Voynich A: 2.138, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 15%
- bpc, Voynich B: 1.867, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 5%
- bpc, Voynich, segni rimescolati (controllo negativo): 3.759, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 95%
- bpc, Voynich in lettere EVA non fuse (sensibilità): 1.861, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 5%
- bpc, Timm e Schinner (seme 1): 2.191, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 20%
- bpc, Voynichizzatore v21 (libro d'esempio): 2.141, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 15%
- bpc, Naibbe: 1.998, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 10%
- bpc, Gibberish (Gaskell e Bowern): 3.992, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 95%
- bpc, Latin, cifrato con una sostituzione (controllo positivo): 2.827, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 75%
- bpc, Latin, cifrato con Vigenère (periodo 7): 3.443, dentro l'intervallo delle lingue [1.829, 4.800], lingue sotto: 95%
- h1, Voynich: 3.947, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Voynich A: 3.968, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Voynich B: 3.923, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Voynich, segni rimescolati (controllo negativo): 3.948, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Voynich in lettere EVA non fuse (sensibilità): 3.965, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Timm e Schinner (seme 1): 3.807, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 5%
- h1, Voynichizzatore v21 (libro d'esempio): 3.963, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Naibbe: 3.957, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 10%
- h1, Gibberish (Gaskell e Bowern): 4.453, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 75%
- h1, Latin, cifrato con una sostituzione (controllo positivo): 4.131, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 25%
- h1, Latin, cifrato con Vigenère (periodo 7): 4.456, dentro l'intervallo delle lingue [3.554, 6.203], lingue sotto: 75%
- scarto, Voynich: 0.013, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Voynich A: 0.065, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Voynich B: 0.038, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Voynich, segni rimescolati (controllo negativo): -0.004, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Voynich in lettere EVA non fuse (sensibilità): 0.061, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Timm e Schinner (seme 1): 0.178, dentro l'intervallo delle lingue [0.139, 0.645], lingue sotto: 5%
- scarto, Voynichizzatore v21 (libro d'esempio): 0.060, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Naibbe: 0.051, sotto l'intervallo delle lingue [0.139, 0.645], lingue sotto: 0%
- scarto, Gibberish (Gaskell e Bowern): 0.232, dentro l'intervallo delle lingue [0.139, 0.645], lingue sotto: 30%
- scarto, Latin, cifrato con una sostituzione (controllo positivo): 0.232, dentro l'intervallo delle lingue [0.139, 0.645], lingue sotto: 30%
- scarto, Latin, cifrato con Vigenère (periodo 7): 0.151, dentro l'intervallo delle lingue [0.139, 0.645], lingue sotto: 5%
- T, Voynich A -> Voynich B: 0.447, dentro l'intervallo delle lingue [0.377, 8.454], lingue sotto: 25%
- T, Voynich B -> Voynich A: 0.402, dentro l'intervallo delle lingue [0.377, 8.454], lingue sotto: 12%
- G_e_alfabeto_spearman: -0.057

## Testi più vicini al Voynich sul profilo (G, E90, D)

Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea.

- Voynich: Voynichizzatore v21 (libro d'esempio) (generatore) 0.78; Timm e Schinner (seme 1) (generatore) 1.56; Naibbe (generatore) 1.73; Chinese (Pinyin) (lingua) 3.27; Maori (lingua) 4.98; Anglo-Saxon (lingua) 5.08
- Voynich A: Voynichizzatore v21 (libro d'esempio) (generatore) 0.70; Timm e Schinner (seme 1) (generatore) 1.30; Naibbe (generatore) 1.73; Chinese (Pinyin) (lingua) 3.31; Anglo-Saxon (lingua) 4.84; Maori (lingua) 4.87
- Voynich B: Voynichizzatore v21 (libro d'esempio) (generatore) 1.05; Timm e Schinner (seme 1) (generatore) 1.95; Naibbe (generatore) 1.96; Chinese (Pinyin) (lingua) 3.38; Maori (lingua) 5.23; Anglo-Saxon (lingua) 5.50

## Generatori, cifrati e controlli rispetto al Voynich

"vicino": differenza al massimo un decimo dell'intervallo delle lingue.

- Voynich, segni rimescolati (controllo negativo): G -0.450, E90 +0.102 (vicino)
- Voynich in lettere EVA non fuse (sensibilità): G +0.033 (vicino), E90 -0.410 (vicino)
- Timm e Schinner (seme 1): G -0.073, E90 +0.000 (vicino), D -0.075
- Voynichizzatore v21 (libro d'esempio): G -0.038, E90 -0.717 (vicino), D -0.030
- Naibbe: G -0.003 (vicino), E90 -0.614 (vicino), D -0.098
- Gibberish (Gaskell e Bowern): G -0.394, E90 +3.584, D -0.113
- Latin, cifrato con una sostituzione (controllo positivo): G -0.182, E90 +9.830
- Latin, cifrato con Vigenère (periodo 7): G -0.271, E90 +14.643, D +0.359
