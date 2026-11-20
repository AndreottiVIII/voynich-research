# IA2 (ia02) — parole mai viste

Stesso modello di e3c95: GRU a caratteri (128 unità), 40000 segni di addestramento, 5000 di validazione, 10000 di prova, al massimo 2000 passi, semi 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
Corse arrivate al massimo dei passi: 0.
Valori: media dei semi (deviazione standard fra i semi).

## Controlli

- positivo: R_rel_C+ 1.0060, R_rel_C+2 0.9905, soglia 1.1000, superato True
- negativo: R_rel 1.8553, R_rel_max_lingue 1.5238, R_rel_max_positivi 1.0060, superato True

## Misure per testo

R: costo per segno delle parole mai viste / delle viste, a parità di lunghezza (rete); R_tri: lo stesso per il modello a trigrammi (nessuna memoria di parole intere); R_rel = R / R_tri. quota nuove: parole mai viste nella prova. N: quota di parole inventate non presenti nell'addestramento; Q: fra le nuove, quota che compare in validazione+prova (rete / trigrammi / unigrammi); la Q della rete si legge solo con almeno 100 hit sui semi (altrimenti "–", e il numero di hit è fra parentesi). I costi per segno (costo_visto, costo_nuovo) sommano i bit dei segni e del separatore che chiude la parola, e dividono per i soli segni.

| testo | ruolo | segni | BPC | quota nuove | R | R_tri | R_rel | copertura | N | Q rete (n hit) | Q tri | Q uni |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | voynich | 25 | 1.982 | 0.228 | 1.801 (0.088) | 1.806 | 0.997 (0.031) | 0.902 | 0.231 | 0.081 (3729) | 0.073 | 0.020 |
| Voynich A | voynich | 25 | 2.138 | 0.221 | 1.753 (0.049) | 1.754 | 1.000 (0.006) | 0.937 | 0.212 | 0.081 (3366) | 0.074 | 0.016 |
| Voynich B | voynich | 25 | 1.867 | 0.189 | 1.933 (0.058) | 1.988 | 0.972 (0.017) | 0.865 | 0.207 | 0.078 (3218) | 0.069 | 0.010 |
| Timm e Schinner (seme 1) | generatore | 24 | 2.191 | 0.205 | 1.688 (0.098) | 1.694 | 0.996 (0.016) | 0.956 | 0.187 | 0.070 (2620) | 0.054 | 0.002 |
| Voynichizzatore v21 (libro d'esempio) | generatore | 25 | 2.141 | 0.232 | 1.915 (0.067) | 1.916 | 0.999 (0.019) | 0.896 | 0.271 | 0.059 (3158) | 0.057 | 0.011 |
| Naibbe | generatore | 23 | 1.998 | 0.226 | 1.529 (0.024) | 1.545 | 0.990 (0.010) | 0.975 | 0.277 | 0.091 (5021) | 0.084 | 0.005 |
| Gibberish (Gaskell e Bowern) | generatore | 30 | 3.992 | 0.744 | 1.181 (0.054) | 1.269 | 0.931 (0.034) | 0.720 | 0.816 | 0.019 (3059) | 0.029 | 0.024 |
| Anglo-Saxon | lingua | 27 | 2.491 | 0.209 | 1.729 (0.051) | 1.403 | 1.233 (0.033) | 0.904 | 0.386 | 0.011 (805) | 0.012 | 0.007 |
| Arabic | lingua | 54 | 3.010 | 0.370 | 1.559 (0.045) | 1.478 | 1.055 (0.026) | 0.938 | 0.640 | 0.008 (996) | 0.007 | 0.005 |
| English | lingua | 26 | 2.319 | 0.153 | 1.837 (0.060) | 1.396 | 1.316 (0.028) | 0.917 | 0.350 | 0.006 (441) | 0.009 | 0.003 |
| Flemish | lingua | 28 | 2.148 | 0.176 | 2.153 (0.102) | 1.413 | 1.524 (0.050) | 0.959 | 0.386 | 0.007 (542) | 0.014 | 0.013 |
| French | lingua | 32 | 2.320 | 0.166 | 1.833 (0.056) | 1.360 | 1.348 (0.039) | 0.923 | 0.359 | 0.006 (409) | 0.006 | 0.001 |
| German | lingua | 33 | 2.219 | 0.167 | 2.151 (0.100) | 1.521 | 1.414 (0.041) | 0.919 | 0.365 | 0.009 (582) | 0.011 | 0.002 |
| Greek | lingua | 28 | 2.535 | 0.275 | 1.682 (0.065) | 1.335 | 1.260 (0.041) | 0.840 | 0.453 | 0.004 (394) | 0.004 | 0.000 |
| Italian | lingua | 30 | 2.304 | 0.205 | 1.845 (0.071) | 1.364 | 1.352 (0.033) | 0.910 | 0.414 | 0.007 (586) | 0.011 | 0.003 |
| Latin (Abbreviated) | lingua | 25 | 3.126 | 0.454 | 1.262 (0.031) | 1.158 | 1.089 (0.023) | 0.837 | 0.648 | 0.007 (889) | 0.012 | 0.007 |
| Latin | lingua | 25 | 2.829 | 0.488 | 1.381 (0.036) | 1.181 | 1.170 (0.028) | 0.851 | 0.730 | 0.005 (710) | 0.007 | 0.004 |
| Mayan (Kaqchikel) | lingua | 26 | 2.354 | 0.167 | 2.010 (0.066) | 1.473 | 1.365 (0.030) | 0.946 | 0.351 | 0.012 (814) | 0.022 | 0.014 |
| Russian | lingua | 43 | 2.716 | 0.257 | 1.651 (0.037) | 1.394 | 1.184 (0.031) | 0.911 | 0.448 | 0.009 (774) | 0.008 | 0.010 |
| Sanskrit | lingua | 160 | 4.800 | 0.573 | 1.623 (0.150) | 1.807 | 0.897 (0.039) | 0.496 | 0.739 | 0.004 (302) | 0.005 | 0.001 |
| Spanish | lingua | 32 | 2.361 | 0.175 | 1.890 (0.066) | 1.386 | 1.364 (0.037) | 0.894 | 0.363 | 0.005 (356) | 0.004 | 0.001 |
| Chinese (Pinyin) | lingua | 47 | 2.029 | 0.017 | 2.114 (0.082) | 2.082 | 1.019 (0.061) | 0.993 | 0.073 | 0.034 (494) | 0.044 | 0.002 |
| Hebrew | lingua | 30 | 2.926 | 0.309 | 1.563 (0.041) | 1.440 | 1.085 (0.017) | 0.986 | 0.522 | 0.017 (1726) | 0.019 | 0.004 |
| Maori | lingua | 17 | 1.829 | 0.057 | 2.046 (0.123) | 1.413 | 1.448 (0.077) | 0.881 | 0.190 | 0.011 (411) | 0.017 | 0.009 |
| Swahili | lingua | 27 | 2.321 | 0.256 | 1.716 (0.063) | 1.274 | 1.347 (0.047) | 0.795 | 0.530 | 0.004 (471) | 0.007 | 0.001 |
| Tagalog | lingua | 25 | 1.920 | 0.162 | 1.993 (0.102) | 1.369 | 1.455 (0.059) | 0.850 | 0.361 | 0.003 (237) | 0.004 | 0.000 |
| Turkish | lingua | 33 | 2.488 | 0.416 | 1.652 (0.045) | 1.291 | 1.280 (0.027) | 0.859 | 0.636 | 0.008 (1000) | 0.006 | 0.001 |
| C+ solo regole (catena di Markov di ordine 2 sul latino) | controllo | 25 | 3.177 | 0.614 | 1.296 (0.025) | 1.288 | 1.006 (0.014) | 0.331 | 0.642 | 0.024 (3109) | 0.028 | 0.013 |
| C- solo memoria (lessico casuale di 3.000 parole) | controllo | 25 | 2.049 | 0.165 | 3.649 (0.223) | 1.967 | 1.855 (0.104) | 0.986 | 0.513 | – (3) | 0.000 | 0.000 |
| C+2 solo regole di posizione (prefisso, corpo, suffisso) | controllo | 16 | 2.480 | 0.544 | 1.325 (0.011) | 1.338 | 0.990 (0.010) | 0.824 | 0.543 | 0.070 (7524) | 0.068 | 0.014 |

## Posizione rispetto alle lingue

- R, Voynich: 1.801, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 50%
- R, Voynich A: 1.753, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 50%
- R, Voynich B: 1.933, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 70%
- R, Timm e Schinner (seme 1): 1.688, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 40%
- R, Voynichizzatore v21 (libro d'esempio): 1.915, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 70%
- R, Naibbe: 1.529, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 10%
- R, Gibberish (Gaskell e Bowern): 1.181, sotto l'intervallo delle lingue [1.262, 2.153], lingue sotto: 0%
- R, C+ solo regole (catena di Markov di ordine 2 sul latino): 1.296, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 5%
- R, C- solo memoria (lessico casuale di 3.000 parole): 3.649, sopra l'intervallo delle lingue [1.262, 2.153], lingue sotto: 100%
- R, C+2 solo regole di posizione (prefisso, corpo, suffisso): 1.325, dentro l'intervallo delle lingue [1.262, 2.153], lingue sotto: 5%
- R_rel, Voynich: 0.997, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Voynich A: 1.000, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Voynich B: 0.972, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Timm e Schinner (seme 1): 0.996, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Voynichizzatore v21 (libro d'esempio): 0.999, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Naibbe: 0.990, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, Gibberish (Gaskell e Bowern): 0.931, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, C+ solo regole (catena di Markov di ordine 2 sul latino): 1.006, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_rel, C- solo memoria (lessico casuale di 3.000 parole): 1.855, sopra l'intervallo delle lingue [0.897, 1.524], lingue sotto: 100%
- R_rel, C+2 solo regole di posizione (prefisso, corpo, suffisso): 0.990, dentro l'intervallo delle lingue [0.897, 1.524], lingue sotto: 5%
- R_tri, Voynich: 1.806, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 90%
- R_tri, Voynich A: 1.754, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 90%
- R_tri, Voynich B: 1.988, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 95%
- R_tri, Timm e Schinner (seme 1): 1.694, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 90%
- R_tri, Voynichizzatore v21 (libro d'esempio): 1.916, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 95%
- R_tri, Naibbe: 1.545, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 90%
- R_tri, Gibberish (Gaskell e Bowern): 1.269, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 10%
- R_tri, C+ solo regole (catena di Markov di ordine 2 sul latino): 1.288, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 15%
- R_tri, C- solo memoria (lessico casuale di 3.000 parole): 1.967, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 95%
- R_tri, C+2 solo regole di posizione (prefisso, corpo, suffisso): 1.338, dentro l'intervallo delle lingue [1.158, 2.082], lingue sotto: 25%
- quota_nuove, Voynich: 0.228, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 55%
- quota_nuove, Voynich A: 0.221, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 55%
- quota_nuove, Voynich B: 0.189, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 45%
- quota_nuove, Timm e Schinner (seme 1): 0.205, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 45%
- quota_nuove, Voynichizzatore v21 (libro d'esempio): 0.232, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 55%
- quota_nuove, Naibbe: 0.226, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 55%
- quota_nuove, Gibberish (Gaskell e Bowern): 0.744, sopra l'intervallo delle lingue [0.017, 0.573], lingue sotto: 100%
- quota_nuove, C+ solo regole (catena di Markov di ordine 2 sul latino): 0.614, sopra l'intervallo delle lingue [0.017, 0.573], lingue sotto: 100%
- quota_nuove, C- solo memoria (lessico casuale di 3.000 parole): 0.165, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 20%
- quota_nuove, C+2 solo regole di posizione (prefisso, corpo, suffisso): 0.544, dentro l'intervallo delle lingue [0.017, 0.573], lingue sotto: 95%
- N_rete, Voynich: 0.231, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 10%
- N_rete, Voynich A: 0.212, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 10%
- N_rete, Voynich B: 0.207, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 10%
- N_rete, Timm e Schinner (seme 1): 0.187, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 5%
- N_rete, Voynichizzatore v21 (libro d'esempio): 0.271, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 10%
- N_rete, Naibbe: 0.277, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 10%
- N_rete, Gibberish (Gaskell e Bowern): 0.816, sopra l'intervallo delle lingue [0.073, 0.739], lingue sotto: 100%
- N_rete, C+ solo regole (catena di Markov di ordine 2 sul latino): 0.642, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 85%
- N_rete, C- solo memoria (lessico casuale di 3.000 parole): 0.513, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 65%
- N_rete, C+2 solo regole di posizione (prefisso, corpo, suffisso): 0.543, dentro l'intervallo delle lingue [0.073, 0.739], lingue sotto: 75%
- Q_rete, Voynich: 0.081, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Voynich A: 0.081, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Voynich B: 0.078, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Timm e Schinner (seme 1): 0.070, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Voynichizzatore v21 (libro d'esempio): 0.059, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Naibbe: 0.091, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rete, Gibberish (Gaskell e Bowern): 0.019, dentro l'intervallo delle lingue [0.003, 0.034], lingue sotto: 95%
- Q_rete, C+ solo regole (catena di Markov di ordine 2 sul latino): 0.024, dentro l'intervallo delle lingue [0.003, 0.034], lingue sotto: 95%
- Q_rete, C+2 solo regole di posizione (prefisso, corpo, suffisso): 0.070, sopra l'intervallo delle lingue [0.003, 0.034], lingue sotto: 100%
- Q_rel, Voynich: 1.112, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 90%
- Q_rel, Voynich A: 1.087, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 85%
- Q_rel, Voynich B: 1.138, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 90%
- Q_rel, Timm e Schinner (seme 1): 1.302, sopra l'intervallo delle lingue [0.516, 1.218], lingue sotto: 100%
- Q_rel, Voynichizzatore v21 (libro d'esempio): 1.039, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 75%
- Q_rel, Naibbe: 1.083, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 80%
- Q_rel, Gibberish (Gaskell e Bowern): 0.651, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 25%
- Q_rel, C+ solo regole (catena di Markov di ordine 2 sul latino): 0.877, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 60%
- Q_rel, C+2 solo regole di posizione (prefisso, corpo, suffisso): 1.025, dentro l'intervallo delle lingue [0.516, 1.218], lingue sotto: 70%
- costo_visto, Voynich: 2.141, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 15%
- costo_visto, Voynich A: 2.364, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 20%
- costo_visto, Voynich B: 2.011, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 5%
- costo_visto, Timm e Schinner (seme 1): 2.490, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 45%
- costo_visto, Voynichizzatore v21 (libro d'esempio): 2.253, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 20%
- costo_visto, Naibbe: 2.215, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 15%
- costo_visto, Gibberish (Gaskell e Bowern): 4.905, sopra l'intervallo delle lingue [1.948, 4.603], lingue sotto: 100%
- costo_visto, C+ solo regole (catena di Markov di ordine 2 sul latino): 3.843, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 90%
- costo_visto, C- solo memoria (lessico casuale di 3.000 parole): 1.574, sotto l'intervallo delle lingue [1.948, 4.603], lingue sotto: 0%
- costo_visto, C+2 solo regole di posizione (prefisso, corpo, suffisso): 2.958, dentro l'intervallo delle lingue [1.948, 4.603], lingue sotto: 80%
- costo_nuovo, Voynich: 3.062, sotto l'intervallo delle lingue [3.212, 5.969], lingue sotto: 0%
- costo_nuovo, Voynich A: 3.250, dentro l'intervallo delle lingue [3.212, 5.969], lingue sotto: 5%
- costo_nuovo, Voynich B: 3.085, sotto l'intervallo delle lingue [3.212, 5.969], lingue sotto: 0%
- costo_nuovo, Timm e Schinner (seme 1): 3.412, dentro l'intervallo delle lingue [3.212, 5.969], lingue sotto: 20%
- costo_nuovo, Voynichizzatore v21 (libro d'esempio): 3.415, dentro l'intervallo delle lingue [3.212, 5.969], lingue sotto: 20%
- costo_nuovo, Naibbe: 2.963, sotto l'intervallo delle lingue [3.212, 5.969], lingue sotto: 0%
- costo_nuovo, Gibberish (Gaskell e Bowern): 4.761, dentro l'intervallo delle lingue [3.212, 5.969], lingue sotto: 90%
- costo_nuovo, C+ solo regole (catena di Markov di ordine 2 sul latino): 3.683, dentro l'intervallo delle lingue [3.212, 5.969], lingue sotto: 40%
- costo_nuovo, C- solo memoria (lessico casuale di 3.000 parole): 6.032, sopra l'intervallo delle lingue [3.212, 5.969], lingue sotto: 100%
- costo_nuovo, C+2 solo regole di posizione (prefisso, corpo, suffisso): 2.972, sotto l'intervallo delle lingue [3.212, 5.969], lingue sotto: 0%
- R_rel_e_quota_nuove_spearman: -0.582
- R_rel_e_alfabeto_spearman: -0.434

## Letture 1, 6 e 7

- Voynich: R_rel 0.997, dentro l'intervallo delle lingue (lingue sotto 5%); scala 0 (solo regole) - 1 (solo memoria): -0.01; lettura: solo regole (R_rel sotto la soglia, controlli "solo regole" riusciti); AVVERTENZA: R_rel dipende dal vocabolario (|rho| > 0,5 fra le lingue)
- Voynich A: R_rel 1.000, dentro l'intervallo delle lingue (lingue sotto 5%); scala 0 (solo regole) - 1 (solo memoria): -0.01; lettura: solo regole (R_rel sotto la soglia, controlli "solo regole" riusciti); AVVERTENZA: R_rel dipende dal vocabolario (|rho| > 0,5 fra le lingue)
- Voynich B: R_rel 0.972, dentro l'intervallo delle lingue (lingue sotto 5%); scala 0 (solo regole) - 1 (solo memoria): -0.04; lettura: solo regole (R_rel sotto la soglia, controlli "solo regole" riusciti); AVVERTENZA: R_rel dipende dal vocabolario (|rho| > 0,5 fra le lingue)
- A contro B: R_rel 1.000 e 0.972, differenza 0.028, soglia (3 deviazioni standard) 0.051: non distinguibili

## Testi più vicini al Voynich sul profilo (R_rel, N, Q_rel)

Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea; Q_rel = Q_rete / Q_tri, solo con almeno 100 hit (altrimenti la misura manca e il profilo usa le altre).

- Voynich (misure: R_rel, N_rete, Q_rel): Naibbe (generatore) 0.30; Voynichizzatore v21 (libro d'esempio) (generatore) 0.40; Timm e Schinner (seme 1) (generatore) 0.89; Russian (lingua) 1.70; Chinese (Pinyin) (lingua) 1.76; C+2 solo regole di posizione (prefisso, corpo, suffisso) (controllo) 1.87
- Voynich A (misure: R_rel, N_rete, Q_rel): Naibbe (generatore) 0.39; Voynichizzatore v21 (libro d'esempio) (generatore) 0.41; Timm e Schinner (seme 1) (generatore) 0.97; Chinese (Pinyin) (lingua) 1.60; Russian (lingua) 1.78; Anglo-Saxon (lingua) 1.91
- Voynich B (misure: R_rel, N_rete, Q_rel): Naibbe (generatore) 0.49; Voynichizzatore v21 (libro d'esempio) (generatore) 0.60; Timm e Schinner (seme 1) (generatore) 0.76; Chinese (Pinyin) (lingua) 1.81; Russian (lingua) 1.92; C+2 solo regole di posizione (prefisso, corpo, suffisso) (controllo) 2.03

## Generatori e controlli rispetto al Voynich

"vicino": differenza al massimo un decimo dell'intervallo delle lingue.

- Timm e Schinner (seme 1): R -0.113, R_rel -0.001 (vicino), quota_nuove -0.023 (vicino), N_rete -0.044 (vicino), Q_rel +0.190
- Voynichizzatore v21 (libro d'esempio): R +0.114, R_rel +0.002 (vicino), quota_nuove +0.005 (vicino), N_rete +0.040 (vicino), Q_rel -0.073
- Naibbe: R -0.273, R_rel -0.008 (vicino), quota_nuove -0.001 (vicino), N_rete +0.046 (vicino), Q_rel -0.029 (vicino)
- Gibberish (Gaskell e Bowern): R -0.621, R_rel -0.067, quota_nuove +0.516, N_rete +0.584, Q_rel -0.461
- C+ solo regole (catena di Markov di ordine 2 sul latino): R -0.505, R_rel +0.009 (vicino), quota_nuove +0.387, N_rete +0.410, Q_rel -0.235
- C- solo memoria (lessico casuale di 3.000 parole): R +1.847, R_rel +0.858, quota_nuove -0.063, N_rete +0.281
- C+2 solo regole di posizione (prefisso, corpo, suffisso): R -0.476, R_rel -0.007 (vicino), quota_nuove +0.316, N_rete +0.312, Q_rel -0.087
