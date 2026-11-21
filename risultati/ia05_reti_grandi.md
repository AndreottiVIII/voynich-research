# IA5 (ia05) — reti più grandi e un piccolo transformer

Stesso disegno di e3c95 (40000 segni di addestramento, 5000 di validazione, 10000 di prova, al massimo 2000 passi, arresto con pazienza 10); semi 1, 2, 3, 4, 5; reti: gru64, gru128, gru256, gru512, gru2x256, transformer.
Valori: media dei semi (deviazione standard fra i semi).

## Controlli

- controllo positivo: gru64, differenza_bpc 0.0004, ds_appaiata 0.0171, errore_standard 0.0076, semi 5, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: gru64, G_rimescolato 0.0478, G_voynich 0.4912, G_min_lingue 0.2189, superato True
- controllo positivo: gru128, differenza_bpc 0.0048, ds_appaiata 0.0136, errore_standard 0.0061, semi 5, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: gru128, G_rimescolato 0.0471, G_voynich 0.4910, G_min_lingue 0.2205, superato True
- controllo positivo: gru256, differenza_bpc 0.0055, ds_appaiata 0.0188, errore_standard 0.0084, semi 5, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: gru256, G_rimescolato 0.0461, G_voynich 0.4927, G_min_lingue 0.2125, superato True
- controllo positivo: gru512, differenza_bpc 0.0049, ds_appaiata 0.0147, errore_standard 0.0085, semi 3, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: gru512, G_rimescolato 0.0442, G_voynich 0.4882, G_min_lingue 0.1975, superato True
- controllo positivo: gru2x256, differenza_bpc -0.0048, ds_appaiata 0.0232, errore_standard 0.0134, semi 3, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: gru2x256, G_rimescolato 0.0452, G_voynich 0.4875, G_min_lingue 0.2022, superato True
- controllo positivo: transformer, differenza_bpc -0.0145, ds_appaiata 0.0365, errore_standard 0.0211, semi 3, soglia 0.0300, superato True, superato_con_soglia_e3c95_0_02 True
- controllo negativo: transformer, G_rimescolato 0.0441, G_voynich 0.4930, G_min_lingue 0.2237, superato True

## Verifica interna: gru128 contro e3c95

- 270 corse confrontate, 270 con curve identiche, differenza massima di BPC nel punto scelto 0.00000 (tolleranza 0.01): superata

## Reti

| rete | parametri (alfabeto del primo testo) | corse | al limite dei passi | riserva (>25%) | s/corsa |
|---|---|---|---|---|---|
| gru64 | 21241 | 270 | 23 | no | 156 |
| gru128 | 66233 | 270 | 0 | no | 169 |
| gru256 | 229945 | 270 | 0 | no | 221 |
| gru512 | 852281 | 162 | 0 | no | 379 |
| gru2x256 | 624697 | 162 | 0 | no | 232 |
| transformer | 411417 | 87 | 2 | no | 734 |

## G per rete

| testo | ruolo | gru64 | gru128 | gru256 | gru512 | gru2x256 | transformer |
|---|---|---|---|---|---|---|---|
| Voynich | voynich | 0.491 (0.022) | 0.491 (0.020) | 0.493 (0.021) | 0.488 (0.026) | 0.487 (0.029) | 0.493 (0.031) |
| Voynich A | voynich | 0.461 (0.002) | 0.462 (0.003) | 0.462 (0.002) | 0.460 (0.004) | 0.459 (0.001) | 0.460 (0.001) |
| Voynich B | voynich | 0.523 (0.007) | 0.527 (0.008) | 0.527 (0.010) | 0.523 (0.004) | 0.524 (0.004) | 0.526 (0.004) |
| Voynich, segni rimescolati (controllo negativo) | controllo | 0.048 (0.001) | 0.047 (0.001) | 0.046 (0.001) | 0.044 (0.002) | 0.045 (0.001) | 0.044 (0.001) |
| Timm e Schinner (seme 1) | generatore | 0.425 (0.031) | 0.428 (0.033) | 0.430 (0.027) | 0.436 (0.029) | 0.436 (0.034) | 0.454 (0.021) |
| Voynichizzatore v21 (libro d'esempio) | generatore | 0.455 (0.021) | 0.457 (0.022) | 0.457 (0.022) | 0.447 (0.024) | 0.445 (0.021) | 0.446 (0.022) |
| Naibbe | generatore | 0.496 (0.006) | 0.496 (0.006) | 0.494 (0.006) | 0.492 (0.008) | 0.492 (0.008) | 0.494 (0.006) |
| Gibberish (Gaskell e Bowern) | generatore | 0.098 (0.013) | 0.097 (0.014) | 0.097 (0.013) | 0.095 (0.012) | 0.096 (0.013) | 0.087 (0.007) |
| Anglo-Saxon | lingua | 0.395 (0.005) | 0.408 (0.004) | 0.411 (0.006) | 0.410 (0.004) | 0.411 (0.004) | 0.413 (0.008) |
| Arabic | lingua | 0.315 (0.012) | 0.329 (0.015) | 0.331 (0.015) | 0.328 (0.021) | 0.337 (0.021) | 0.341 (0.021) |
| English | lingua | 0.422 (0.023) | 0.435 (0.026) | 0.443 (0.025) | 0.440 (0.039) | 0.448 (0.037) | 0.451 (0.036) |
| Flemish | lingua | 0.466 (0.012) | 0.485 (0.015) | 0.491 (0.014) | 0.487 (0.024) | 0.494 (0.019) | 0.494 (0.030) |
| French | lingua | 0.441 (0.004) | 0.457 (0.004) | 0.461 (0.005) | 0.459 (0.003) | 0.466 (0.002) | 0.466 (0.006) |
| German | lingua | 0.459 (0.008) | 0.475 (0.007) | 0.480 (0.004) | 0.478 (0.014) | 0.484 (0.011) | 0.488 (0.013) |
| Greek | lingua | 0.386 (0.004) | 0.399 (0.007) | 0.405 (0.007) | 0.398 (0.008) | 0.407 (0.009) | 0.406 (0.007) |
| Italian | lingua | 0.427 (0.014) | 0.442 (0.015) | 0.445 (0.014) | 0.448 (0.019) | 0.455 (0.020) | 0.467 (0.017) |
| Latin (Abbreviated) | lingua | 0.241 (0.008) | 0.245 (0.010) | 0.247 (0.010) | 0.241 (0.003) | 0.248 (0.002) | 0.258 (0.005) |
| Latin | lingua | 0.308 (0.015) | 0.317 (0.017) | 0.319 (0.020) | 0.316 (0.021) | 0.321 (0.021) | 0.333 (0.023) |
| Mayan (Kaqchikel) | lingua | 0.402 (0.011) | 0.417 (0.009) | 0.419 (0.011) | 0.413 (0.005) | 0.424 (0.007) | 0.426 (0.006) |
| Russian | lingua | 0.392 (0.014) | 0.409 (0.017) | 0.411 (0.019) | 0.416 (0.008) | 0.423 (0.010) | 0.421 (0.007) |
| Sanskrit | lingua | 0.219 (0.024) | 0.220 (0.025) | 0.212 (0.025) | 0.197 (0.041) | 0.202 (0.035) | 0.224 (0.037) |
| Spanish | lingua | 0.427 (0.020) | 0.445 (0.019) | 0.446 (0.017) | 0.445 (0.015) | 0.451 (0.017) | 0.450 (0.016) |
| Chinese (Pinyin) | lingua | 0.561 (0.007) | 0.565 (0.013) | 0.567 (0.012) | 0.558 (0.012) | 0.561 (0.016) | 0.559 (0.009) |
| Hebrew | lingua | 0.297 (0.007) | 0.305 (0.006) | 0.303 (0.007) | 0.294 (0.005) | 0.304 (0.005) | 0.309 (0.011) |
| Maori | lingua | 0.471 (0.009) | 0.485 (0.010) | 0.490 (0.008) | 0.485 (0.008) | 0.485 (0.018) | 0.488 (0.015) |
| Swahili | lingua | 0.418 (0.007) | 0.434 (0.008) | 0.442 (0.009) | 0.433 (0.011) | 0.441 (0.007) | 0.444 (0.009) |
| Tagalog | lingua | 0.473 (0.008) | 0.489 (0.010) | 0.492 (0.013) | 0.492 (0.014) | 0.501 (0.013) | 0.501 (0.017) |
| Turkish | lingua | 0.425 (0.010) | 0.441 (0.010) | 0.441 (0.005) | 0.436 (0.004) | 0.449 (0.007) | 0.456 (0.008) |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | 0.308 (0.014) | 0.316 (0.017) | 0.318 (0.016) | 0.314 (0.022) | 0.322 (0.026) | 0.336 (0.019) |

## E90 (letture) per rete

| testo | ruolo | gru64 | gru128 | gru256 | gru512 | gru2x256 | transformer |
|---|---|---|---|---|---|---|---|
| Voynich | voynich | 5.120 (0.000) | 3.686 (0.561) | 3.072 (0.000) | 2.048 (0.000) | 2.731 (0.591) | 9.899 (0.591) |
| Voynich A | voynich | 5.734 (0.561) | 4.096 (0.000) | 3.072 (0.000) | 2.731 (0.591) | 2.731 (0.591) | 9.557 (0.591) |
| Voynich B | voynich | 4.096 (0.000) | 3.072 (0.000) | 2.253 (0.458) | 2.048 (0.000) | 2.048 (0.000) | 9.557 (0.591) |
| Voynich, segni rimescolati (controllo negativo) | controllo | 4.710 (0.561) | 3.891 (0.857) | 2.867 (0.458) | 3.072 (1.774) | 2.389 (0.591) | 19.797 (2.365) |
| Timm e Schinner (seme 1) | generatore | 5.530 (0.916) | 3.891 (0.458) | 3.072 (0.000) | 2.389 (0.591) | 2.389 (0.591) | 13.312 (2.709) |
| Voynichizzatore v21 (libro d'esempio) | generatore | 4.301 (0.458) | 3.072 (0.000) | 2.458 (0.561) | 2.048 (0.000) | 2.048 (0.000) | 9.216 (0.000) |
| Naibbe | generatore | 4.096 (0.000) | 3.072 (0.000) | 2.048 (0.000) | 2.048 (0.000) | 2.048 (0.000) | 8.533 (0.591) |
| Gibberish (Gaskell e Bowern) | generatore | 11.059 (2.445) | 7.373 (0.857) | 5.530 (1.553) | 4.779 (0.591) | 4.437 (0.591) | 13.312 (3.692) |
| Anglo-Saxon | lingua | 20.070 (0.561) | 12.902 (0.561) | 9.216 (0.000) | 6.485 (0.591) | 6.827 (0.591) | 29.013 (1.564) |
| Arabic | lingua | 25.805 (1.970) | 16.589 (0.458) | 11.264 (0.000) | 8.533 (1.564) | 8.533 (0.591) | 26.965 (1.182) |
| English | lingua | 20.890 (1.860) | 13.517 (1.335) | 9.421 (0.857) | 6.485 (0.591) | 7.509 (0.591) | 28.672 (1.774) |
| Flemish | lingua | 23.962 (2.357) | 15.565 (1.335) | 10.035 (0.458) | 7.168 (1.024) | 7.851 (0.591) | 29.696 (3.072) |
| French | lingua | 25.805 (1.122) | 15.565 (0.857) | 10.035 (0.458) | 7.168 (0.000) | 7.851 (0.591) | 31.061 (1.564) |
| German | lingua | 22.938 (1.168) | 14.131 (0.857) | 9.421 (0.458) | 6.827 (0.591) | 7.509 (0.591) | 27.648 (1.774) |
| Greek | lingua | 21.094 (0.916) | 13.312 (0.724) | 9.421 (0.458) | 6.485 (0.591) | 7.509 (0.591) | 31.403 (2.365) |
| Italian | lingua | 23.552 (2.401) | 14.950 (0.561) | 9.216 (0.000) | 6.485 (0.591) | 7.168 (0.000) | 29.355 (0.591) |
| Latin (Abbreviated) | lingua | 20.685 (1.335) | 12.493 (0.857) | 9.421 (0.857) | 6.485 (0.591) | 7.168 (1.024) | 30.037 (0.591) |
| Latin | lingua | 21.504 (0.724) | 13.517 (0.857) | 9.421 (0.857) | 6.827 (0.591) | 7.168 (0.000) | 29.696 (3.547) |
| Mayan (Kaqchikel) | lingua | 23.142 (1.860) | 14.336 (1.024) | 9.626 (0.561) | 6.827 (0.591) | 7.509 (0.591) | 32.427 (3.128) |
| Russian | lingua | 23.962 (1.374) | 14.950 (0.561) | 9.830 (0.561) | 7.168 (0.000) | 7.851 (0.591) | 29.355 (0.591) |
| Sanskrit | lingua | 26.624 (3.072) | 17.203 (0.857) | 11.059 (0.458) | 8.533 (1.564) | 7.509 (0.591) | 22.187 (2.132) |
| Spanish | lingua | 24.371 (1.335) | 15.360 (0.724) | 10.035 (0.458) | 6.827 (0.591) | 7.168 (0.000) | 33.792 (3.692) |
| Chinese (Pinyin) | lingua | 13.517 (0.857) | 8.806 (0.561) | 6.554 (0.561) | 4.437 (0.591) | 4.779 (0.591) | 14.677 (1.182) |
| Hebrew | lingua | 21.504 (1.448) | 13.722 (1.168) | 9.421 (0.458) | 6.485 (0.591) | 7.509 (0.591) | 25.600 (3.072) |
| Maori | lingua | 18.227 (1.335) | 12.288 (0.724) | 9.011 (0.458) | 6.485 (0.591) | 6.827 (0.591) | 33.109 (1.564) |
| Swahili | lingua | 24.576 (2.172) | 15.565 (1.122) | 10.650 (0.561) | 6.827 (0.591) | 8.192 (0.000) | 34.816 (2.709) |
| Tagalog | lingua | 21.709 (1.832) | 14.336 (0.000) | 9.216 (0.724) | 6.827 (0.591) | 7.509 (0.591) | 33.109 (1.564) |
| Turkish | lingua | 24.166 (1.374) | 14.950 (0.561) | 9.626 (0.561) | 7.168 (0.000) | 8.192 (0.000) | 27.989 (0.591) |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | 21.709 (0.857) | 13.722 (1.374) | 9.626 (0.561) | 6.485 (0.591) | 7.509 (0.591) | 31.744 (2.048) |

## D (bit per segno) per rete

| testo | ruolo | gru64 | gru128 | gru256 | gru512 | gru2x256 | transformer |
|---|---|---|---|---|---|---|---|
| Voynich | voynich | 0.117 (0.017) | 0.095 (0.013) | 0.096 (0.011) | 0.094 (0.004) | 0.106 (0.008) | – |
| Voynich A | voynich | – | – | – | – | – | – |
| Voynich B | voynich | – | – | – | – | – | – |
| Voynich, segni rimescolati (controllo negativo) | controllo | – | – | – | – | – | – |
| Timm e Schinner (seme 1) | generatore | 0.026 (0.020) | 0.027 (0.017) | 0.035 (0.018) | 0.034 (0.014) | 0.040 (0.016) | – |
| Voynichizzatore v21 (libro d'esempio) | generatore | 0.069 (0.006) | 0.075 (0.014) | 0.070 (0.014) | 0.066 (0.014) | 0.071 (0.008) | – |
| Naibbe | generatore | 0.008 (0.004) | 0.005 (0.009) | 0.005 (0.008) | 0.005 (0.005) | 0.004 (0.007) | – |
| Gibberish (Gaskell e Bowern) | generatore | 0.000 (0.008) | -0.006 (0.006) | -0.003 (0.011) | -0.006 (0.015) | 0.003 (0.012) | – |
| Anglo-Saxon | lingua | 0.032 (0.019) | 0.054 (0.019) | 0.077 (0.018) | 0.096 (0.032) | 0.073 (0.021) | – |
| Arabic | lingua | 0.022 (0.027) | 0.051 (0.020) | 0.057 (0.023) | 0.070 (0.040) | 0.078 (0.019) | – |
| English | lingua | 0.063 (0.016) | 0.099 (0.039) | 0.135 (0.035) | 0.150 (0.039) | 0.146 (0.037) | – |
| Flemish | lingua | 0.028 (0.017) | 0.062 (0.027) | 0.091 (0.032) | 0.105 (0.049) | 0.095 (0.028) | – |
| French | lingua | 0.048 (0.008) | 0.082 (0.009) | 0.114 (0.016) | 0.119 (0.013) | 0.125 (0.014) | – |
| German | lingua | 0.030 (0.025) | 0.061 (0.016) | 0.084 (0.024) | 0.101 (0.037) | 0.117 (0.031) | – |
| Greek | lingua | 0.002 (0.006) | 0.027 (0.014) | 0.048 (0.012) | 0.063 (0.009) | 0.055 (0.008) | – |
| Italian | lingua | 0.010 (0.010) | 0.041 (0.012) | 0.047 (0.019) | 0.053 (0.008) | 0.069 (0.028) | – |
| Latin (Abbreviated) | lingua | 0.003 (0.011) | -0.001 (0.010) | 0.008 (0.011) | -0.006 (0.004) | 0.005 (0.006) | – |
| Latin | lingua | 0.002 (0.014) | 0.001 (0.009) | 0.011 (0.021) | 0.009 (0.008) | -0.001 (0.008) | – |
| Mayan (Kaqchikel) | lingua | 0.044 (0.004) | 0.088 (0.011) | 0.102 (0.028) | 0.107 (0.025) | 0.107 (0.015) | – |
| Russian | lingua | 0.025 (0.016) | 0.074 (0.018) | 0.086 (0.018) | 0.105 (0.024) | 0.107 (0.015) | – |
| Sanskrit | lingua | 0.047 (0.045) | 0.035 (0.017) | 0.035 (0.028) | 0.030 (0.055) | 0.019 (0.038) | – |
| Spanish | lingua | 0.032 (0.029) | 0.079 (0.019) | 0.100 (0.017) | 0.129 (0.044) | 0.116 (0.020) | – |
| Chinese (Pinyin) | lingua | 0.185 (0.015) | 0.202 (0.039) | 0.221 (0.036) | 0.211 (0.028) | 0.212 (0.054) | – |
| Hebrew | lingua | 0.044 (0.011) | 0.060 (0.013) | 0.066 (0.013) | 0.069 (0.008) | 0.082 (0.007) | – |
| Maori | lingua | 0.165 (0.015) | 0.203 (0.019) | 0.230 (0.021) | 0.235 (0.018) | 0.229 (0.038) | – |
| Swahili | lingua | 0.022 (0.008) | 0.050 (0.012) | 0.070 (0.025) | 0.087 (0.018) | 0.068 (0.034) | – |
| Tagalog | lingua | 0.116 (0.020) | 0.156 (0.023) | 0.165 (0.030) | 0.190 (0.021) | 0.195 (0.023) | – |
| Turkish | lingua | -0.001 (0.017) | 0.036 (0.025) | 0.031 (0.019) | 0.040 (0.015) | 0.060 (0.018) | – |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | – | – | – | – | – | – |

## BPC per rete

| testo | ruolo | gru64 | gru128 | gru256 | gru512 | gru2x256 | transformer |
|---|---|---|---|---|---|---|---|
| Voynich | voynich | 2.008 (0.088) | 2.009 (0.082) | 2.002 (0.084) | 2.022 (0.103) | 2.025 (0.119) | 2.003 (0.124) |
| Voynich A | voynich | 2.139 (0.014) | 2.138 (0.014) | 2.138 (0.011) | 2.143 (0.009) | 2.147 (0.007) | 2.143 (0.007) |
| Voynich B | voynich | 1.864 (0.038) | 1.849 (0.037) | 1.846 (0.049) | 1.869 (0.011) | 1.869 (0.013) | 1.857 (0.011) |
| Voynich, segni rimescolati (controllo negativo) | controllo | 3.759 (0.008) | 3.761 (0.010) | 3.765 (0.008) | 3.776 (0.020) | 3.772 (0.014) | 3.776 (0.019) |
| Timm e Schinner (seme 1) | generatore | 2.187 (0.125) | 2.173 (0.132) | 2.166 (0.110) | 2.128 (0.106) | 2.129 (0.123) | 2.060 (0.073) |
| Voynichizzatore v21 (libro d'esempio) | generatore | 2.161 (0.087) | 2.153 (0.093) | 2.153 (0.093) | 2.193 (0.102) | 2.201 (0.091) | 2.199 (0.092) |
| Naibbe | generatore | 1.992 (0.025) | 1.996 (0.027) | 2.004 (0.025) | 2.013 (0.032) | 2.014 (0.032) | 2.006 (0.025) |
| Gibberish (Gaskell e Bowern) | generatore | 4.005 (0.087) | 4.009 (0.091) | 4.013 (0.083) | 4.030 (0.090) | 4.027 (0.092) | 4.069 (0.066) |
| Anglo-Saxon | lingua | 2.563 (0.026) | 2.508 (0.021) | 2.493 (0.028) | 2.500 (0.021) | 2.493 (0.023) | 2.487 (0.043) |
| Arabic | lingua | 3.080 (0.049) | 3.015 (0.063) | 3.008 (0.064) | 3.023 (0.092) | 2.983 (0.096) | 2.966 (0.091) |
| English | lingua | 2.394 (0.096) | 2.339 (0.109) | 2.308 (0.107) | 2.318 (0.164) | 2.284 (0.155) | 2.274 (0.151) |
| Flemish | lingua | 2.198 (0.048) | 2.118 (0.059) | 2.094 (0.057) | 2.109 (0.096) | 2.082 (0.075) | 2.080 (0.120) |
| French | lingua | 2.369 (0.017) | 2.303 (0.018) | 2.284 (0.021) | 2.292 (0.013) | 2.263 (0.010) | 2.263 (0.027) |
| German | lingua | 2.329 (0.029) | 2.259 (0.032) | 2.238 (0.024) | 2.242 (0.061) | 2.216 (0.052) | 2.201 (0.058) |
| Greek | lingua | 2.578 (0.016) | 2.526 (0.026) | 2.502 (0.026) | 2.528 (0.021) | 2.490 (0.030) | 2.495 (0.011) |
| Italian | lingua | 2.374 (0.057) | 2.310 (0.059) | 2.300 (0.057) | 2.286 (0.076) | 2.259 (0.080) | 2.209 (0.067) |
| Latin (Abbreviated) | lingua | 3.135 (0.038) | 3.119 (0.047) | 3.110 (0.045) | 3.128 (0.023) | 3.099 (0.009) | 3.058 (0.030) |
| Latin | lingua | 2.860 (0.060) | 2.820 (0.071) | 2.811 (0.081) | 2.821 (0.081) | 2.799 (0.081) | 2.751 (0.091) |
| Mayan (Kaqchikel) | lingua | 2.430 (0.042) | 2.372 (0.034) | 2.363 (0.044) | 2.389 (0.021) | 2.346 (0.031) | 2.338 (0.029) |
| Russian | lingua | 2.820 (0.065) | 2.745 (0.079) | 2.734 (0.085) | 2.712 (0.039) | 2.680 (0.049) | 2.690 (0.035) |
| Sanskrit | lingua | 4.835 (0.156) | 4.826 (0.162) | 4.875 (0.166) | 4.967 (0.258) | 4.938 (0.219) | 4.805 (0.237) |
| Spanish | lingua | 2.405 (0.088) | 2.332 (0.086) | 2.326 (0.079) | 2.328 (0.068) | 2.302 (0.072) | 2.308 (0.065) |
| Chinese (Pinyin) | lingua | 2.045 (0.036) | 2.027 (0.062) | 2.019 (0.058) | 2.060 (0.055) | 2.046 (0.071) | 2.056 (0.040) |
| Hebrew | lingua | 2.944 (0.029) | 2.911 (0.020) | 2.919 (0.023) | 2.952 (0.013) | 2.910 (0.011) | 2.889 (0.040) |
| Maori | lingua | 1.882 (0.033) | 1.833 (0.033) | 1.814 (0.030) | 1.827 (0.031) | 1.828 (0.063) | 1.816 (0.055) |
| Swahili | lingua | 2.378 (0.032) | 2.312 (0.036) | 2.281 (0.045) | 2.318 (0.049) | 2.285 (0.039) | 2.274 (0.048) |
| Tagalog | lingua | 2.006 (0.036) | 1.945 (0.045) | 1.933 (0.056) | 1.930 (0.063) | 1.896 (0.058) | 1.898 (0.075) |
| Turkish | lingua | 2.562 (0.046) | 2.492 (0.045) | 2.491 (0.022) | 2.515 (0.021) | 2.454 (0.029) | 2.422 (0.031) |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | 2.860 (0.059) | 2.825 (0.070) | 2.817 (0.067) | 2.825 (0.085) | 2.795 (0.103) | 2.736 (0.071) |

## scarto per rete

| testo | ruolo | gru64 | gru128 | gru256 | gru512 | gru2x256 | transformer |
|---|---|---|---|---|---|---|---|
| Voynich | voynich | 0.014 (0.087) | 0.040 (0.086) | 0.067 (0.084) | 0.097 (0.131) | 0.088 (0.145) | 0.052 (0.141) |
| Voynich A | voynich | 0.015 (0.017) | 0.070 (0.020) | 0.087 (0.041) | 0.070 (0.016) | 0.075 (0.031) | 0.035 (0.017) |
| Voynich B | voynich | -0.059 (0.056) | 0.011 (0.058) | 0.063 (0.090) | 0.056 (0.051) | 0.057 (0.028) | -0.022 (0.029) |
| Voynich, segni rimescolati (controllo negativo) | controllo | -0.000 (0.016) | -0.001 (0.013) | 0.009 (0.017) | 0.016 (0.041) | 0.005 (0.037) | -0.014 (0.004) |
| Timm e Schinner (seme 1) | generatore | 0.090 (0.119) | 0.167 (0.125) | 0.167 (0.128) | 0.137 (0.087) | 0.088 (0.090) | 0.030 (0.105) |
| Voynichizzatore v21 (libro d'esempio) | generatore | 0.056 (0.096) | 0.076 (0.103) | 0.088 (0.099) | 0.125 (0.101) | 0.132 (0.090) | 0.087 (0.124) |
| Naibbe | generatore | 0.022 (0.024) | 0.056 (0.031) | 0.066 (0.040) | 0.055 (0.036) | 0.045 (0.042) | 0.045 (0.017) |
| Gibberish (Gaskell e Bowern) | generatore | 0.177 (0.098) | 0.214 (0.119) | 0.234 (0.082) | 0.330 (0.174) | 0.295 (0.169) | 0.320 (0.181) |
| Anglo-Saxon | lingua | 0.158 (0.016) | 0.283 (0.061) | 0.320 (0.074) | 0.446 (0.032) | 0.405 (0.109) | 0.306 (0.049) |
| Arabic | lingua | 0.133 (0.073) | 0.268 (0.049) | 0.347 (0.077) | 0.395 (0.129) | 0.444 (0.010) | 0.324 (0.109) |
| English | lingua | 0.170 (0.116) | 0.309 (0.184) | 0.402 (0.118) | 0.544 (0.282) | 0.413 (0.184) | 0.270 (0.226) |
| Flemish | lingua | 0.094 (0.050) | 0.260 (0.077) | 0.319 (0.113) | 0.466 (0.080) | 0.483 (0.107) | 0.196 (0.092) |
| French | lingua | 0.139 (0.030) | 0.255 (0.059) | 0.371 (0.148) | 0.427 (0.028) | 0.409 (0.015) | 0.223 (0.015) |
| German | lingua | 0.155 (0.021) | 0.357 (0.054) | 0.432 (0.072) | 0.535 (0.117) | 0.465 (0.125) | 0.295 (0.055) |
| Greek | lingua | 0.141 (0.046) | 0.270 (0.082) | 0.357 (0.053) | 0.432 (0.052) | 0.406 (0.056) | 0.286 (0.036) |
| Italian | lingua | 0.109 (0.057) | 0.278 (0.090) | 0.399 (0.123) | 0.463 (0.112) | 0.384 (0.086) | 0.209 (0.074) |
| Latin (Abbreviated) | lingua | 0.120 (0.049) | 0.220 (0.069) | 0.279 (0.074) | 0.405 (0.013) | 0.270 (0.125) | 0.215 (0.073) |
| Latin | lingua | 0.121 (0.050) | 0.192 (0.015) | 0.257 (0.060) | 0.358 (0.080) | 0.306 (0.015) | 0.167 (0.077) |
| Mayan (Kaqchikel) | lingua | 0.216 (0.066) | 0.325 (0.035) | 0.415 (0.099) | 0.535 (0.097) | 0.496 (0.086) | 0.382 (0.073) |
| Russian | lingua | 0.145 (0.061) | 0.340 (0.111) | 0.457 (0.131) | 0.458 (0.062) | 0.419 (0.146) | 0.277 (0.075) |
| Sanskrit | lingua | 0.433 (0.227) | 0.661 (0.147) | 0.793 (0.237) | 0.999 (0.254) | 0.819 (0.244) | 0.726 (0.336) |
| Spanish | lingua | 0.148 (0.100) | 0.280 (0.110) | 0.476 (0.111) | 0.460 (0.085) | 0.420 (0.032) | 0.250 (0.081) |
| Chinese (Pinyin) | lingua | 0.111 (0.048) | 0.201 (0.117) | 0.255 (0.072) | 0.325 (0.086) | 0.394 (0.099) | 0.151 (0.036) |
| Hebrew | lingua | 0.070 (0.031) | 0.171 (0.070) | 0.287 (0.086) | 0.246 (0.066) | 0.285 (0.045) | 0.133 (0.044) |
| Maori | lingua | 0.069 (0.031) | 0.149 (0.061) | 0.215 (0.057) | 0.243 (0.077) | 0.327 (0.137) | 0.134 (0.086) |
| Swahili | lingua | 0.140 (0.057) | 0.252 (0.032) | 0.379 (0.132) | 0.370 (0.060) | 0.394 (0.085) | 0.259 (0.110) |
| Tagalog | lingua | 0.153 (0.055) | 0.226 (0.055) | 0.378 (0.090) | 0.403 (0.030) | 0.336 (0.072) | 0.277 (0.040) |
| Turkish | lingua | 0.157 (0.039) | 0.346 (0.045) | 0.466 (0.098) | 0.527 (0.070) | 0.511 (0.067) | 0.240 (0.118) |
| Latin, cifrato con una sostituzione (controllo positivo) | controllo | 0.103 (0.039) | 0.250 (0.049) | 0.282 (0.065) | 0.320 (0.102) | 0.358 (0.047) | 0.240 (0.096) |

## Lettura 1: crescita di G con la grandezza

DG512 = G(gru512) - G(gru64), seme per seme. Le lingue "guadagnano" se la mediana è almeno 0.01 e almeno il 75% ha crescita positiva.

- DG512, lingue: mediana 0.015, da -0.018 a 0.021, 17 su 20 positive: le lingue guadagnano
  - Voynich: -0.001, dentro l'intervallo delle lingue, lingue sotto: 10%, il Voynich cresce meno delle lingue: sì
  - Voynich A: -0.001, dentro l'intervallo delle lingue, lingue sotto: 10%, il Voynich cresce meno delle lingue: sì
  - Voynich B: +0.005, dentro l'intervallo delle lingue, lingue sotto: 20%, il Voynich cresce meno delle lingue: sì
  - Timm e Schinner (seme 1): +0.001, dentro l'intervallo delle lingue, lingue sotto: 20%
  - Voynichizzatore v21 (libro d'esempio): +0.003, dentro l'intervallo delle lingue, lingue sotto: 20%, il Voynich cresce meno delle lingue: sì
  - Naibbe: -0.005, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Gibberish (Gaskell e Bowern): -0.002, dentro l'intervallo delle lingue, lingue sotto: 10%
  - Voynich, segni rimescolati (controllo negativo): -0.004, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Latin, cifrato con una sostituzione (controllo positivo): +0.004, dentro l'intervallo delle lingue, lingue sotto: 20%
- DG256, lingue: mediana 0.018, da -0.006 a 0.025, 19 su 20 positive: le lingue guadagnano
  - Voynich: +0.001, dentro l'intervallo delle lingue, lingue sotto: 5%, il Voynich cresce meno delle lingue: sì
  - Voynich A: +0.000, dentro l'intervallo delle lingue, lingue sotto: 5%, il Voynich cresce meno delle lingue: sì
  - Voynich B: +0.004, dentro l'intervallo delle lingue, lingue sotto: 5%, il Voynich cresce meno delle lingue: sì
  - Timm e Schinner (seme 1): +0.005, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Voynichizzatore v21 (libro d'esempio): +0.002, dentro l'intervallo delle lingue, lingue sotto: 5%, il Voynich cresce meno delle lingue: sì
  - Naibbe: -0.003, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Gibberish (Gaskell e Bowern): -0.002, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Voynich, segni rimescolati (controllo negativo): -0.002, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Latin, cifrato con una sostituzione (controllo positivo): +0.010, dentro l'intervallo delle lingue, lingue sotto: 20%
- DGmax, lingue: mediana 0.022, da 0.003 a 0.028, 20 su 20 positive: le lingue guadagnano
  - Voynich: +0.001, sotto l'intervallo delle lingue, lingue sotto: 0%, il Voynich cresce meno delle lingue: sì
  - Voynich A: +0.000, sotto l'intervallo delle lingue, lingue sotto: 0%, il Voynich cresce meno delle lingue: sì
  - Voynich B: +0.005, dentro l'intervallo delle lingue, lingue sotto: 10%, il Voynich cresce meno delle lingue: sì
  - Timm e Schinner (seme 1): +0.003, dentro l'intervallo delle lingue, lingue sotto: 5%
  - Voynichizzatore v21 (libro d'esempio): +0.003, sotto l'intervallo delle lingue, lingue sotto: 0%, il Voynich cresce meno delle lingue: sì
  - Naibbe: +0.000, sotto l'intervallo delle lingue, lingue sotto: 0%
  - Gibberish (Gaskell e Bowern): +0.000, sotto l'intervallo delle lingue, lingue sotto: 0%
  - Voynich, segni rimescolati (controllo negativo): +0.000, sotto l'intervallo delle lingue, lingue sotto: 0%
  - Latin, cifrato con una sostituzione (controllo positivo): +0.012, dentro l'intervallo delle lingue, lingue sotto: 20%

| testo | DG256 | DG512 | DGmax (rete) | DG2x256 su 256 | DG transformer su gru128 |
|---|---|---|---|---|---|
| Voynich | 0.001 | -0.001 (0.005) | 0.001 (gru256) | -0.003 | 0.003 |
| Voynich A | 0.000 | -0.001 (0.001) | 0.000 (gru256) | -0.003 | -0.002 |
| Voynich B | 0.004 | 0.005 (0.001) | 0.005 (gru2x256) | 0.001 | 0.005 |
| Voynich, segni rimescolati (controllo negativo) | -0.002 | -0.004 (0.003) | 0.000 (gru64) | -0.001 | -0.003 |
| Timm e Schinner (seme 1) | 0.005 | 0.001 (0.003) | 0.003 (gru128) | -0.003 | 0.016 |
| Voynichizzatore v21 (libro d'esempio) | 0.002 | 0.003 (0.003) | 0.003 (gru512) | -0.001 | -0.001 |
| Naibbe | -0.003 | -0.005 (0.001) | 0.000 (gru64) | -0.003 | -0.002 |
| Gibberish (Gaskell e Bowern) | -0.002 | -0.002 (0.002) | 0.000 (gru256) | -0.002 | -0.011 |
| Anglo-Saxon | 0.017 | 0.015 (0.005) | 0.018 (gru256) | -0.001 | 0.004 |
| Arabic | 0.016 | 0.014 (0.007) | 0.022 (gru2x256) | 0.002 | 0.009 |
| English | 0.021 | 0.017 (0.008) | 0.025 (gru2x256) | 0.001 | 0.010 |
| Flemish | 0.025 | 0.021 (0.007) | 0.028 (gru2x256) | 0.002 | 0.011 |
| French | 0.020 | 0.017 (0.004) | 0.024 (gru2x256) | 0.004 | 0.009 |
| German | 0.021 | 0.021 (0.008) | 0.027 (gru2x256) | 0.003 | 0.013 |
| Greek | 0.018 | 0.012 (0.003) | 0.021 (gru2x256) | 0.002 | 0.007 |
| Italian | 0.018 | 0.015 (0.006) | 0.021 (gru2x256) | 0.003 | 0.018 |
| Latin (Abbreviated) | 0.006 | -0.003 (0.001) | 0.006 (gru256) | -0.002 | 0.009 |
| Latin | 0.012 | 0.005 (0.003) | 0.013 (gru256) | -0.003 | 0.010 |
| Mayan (Kaqchikel) | 0.016 | 0.008 (0.002) | 0.019 (gru2x256) | 0.005 | 0.005 |
| Russian | 0.019 | 0.017 (0.002) | 0.024 (gru2x256) | 0.003 | 0.002 |
| Sanskrit | -0.006 | -0.018 (0.008) | 0.003 (gru128) | -0.007 | 0.005 |
| Spanish | 0.019 | 0.019 (0.009) | 0.025 (gru2x256) | 0.004 | 0.003 |
| Chinese (Pinyin) | 0.006 | 0.001 (0.004) | 0.004 (gru256) | -0.000 | -0.001 |
| Hebrew | 0.006 | -0.001 (0.002) | 0.009 (gru2x256) | 0.003 | 0.007 |
| Maori | 0.019 | 0.017 (0.004) | 0.020 (gru256) | -0.003 | 0.006 |
| Swahili | 0.024 | 0.018 (0.004) | 0.026 (gru2x256) | 0.003 | 0.013 |
| Tagalog | 0.019 | 0.019 (0.006) | 0.028 (gru2x256) | 0.007 | 0.010 |
| Turkish | 0.016 | 0.010 (0.002) | 0.023 (gru2x256) | 0.008 | 0.015 |
| Latin, cifrato con una sostituzione (controllo positivo) | 0.010 | 0.004 (0.003) | 0.012 (gru2x256) | 0.001 | 0.017 |

## Lettura 2: testi più vicini al Voynich sul profilo (G, E90, D), per rete

Ogni misura divisa per la sua deviazione standard fra le lingue, a quella rete; distanza euclidea.

- gru64, profilo G, E90, D: Voynichizzatore v21 (libro d'esempio) (generatore) 1.07; Timm e Schinner (seme 1) (generatore) 1.94; Naibbe (generatore) 2.14; Chinese (Pinyin) (lingua) 3.21; Maori (lingua) 4.48; Anglo-Saxon (lingua) 5.38. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.21
- gru64, profilo G, E90: Naibbe (generatore) 0.35; Voynichizzatore v21 (libro d'esempio) (generatore) 0.51; Timm e Schinner (seme 1) (generatore) 0.81; Chinese (Pinyin) (lingua) 2.92; Maori (lingua) 4.38; Gibberish (Gaskell e Bowern) (generatore) 5.09. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 2.92
- gru128, profilo G, E90, D: Voynichizzatore v21 (libro d'esempio) (generatore) 0.64; Timm e Schinner (seme 1) (generatore) 1.42; Naibbe (generatore) 1.64; Chinese (Pinyin) (lingua) 3.50; Maori (lingua) 5.11; Anglo-Saxon (lingua) 5.22. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.50
- gru128, profilo G, E90: Naibbe (generatore) 0.34; Voynichizzatore v21 (libro d'esempio) (generatore) 0.52; Timm e Schinner (seme 1) (generatore) 0.73; Chinese (Pinyin) (lingua) 2.95; Maori (lingua) 4.74; Gibberish (Gaskell e Bowern) (generatore) 4.99. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 2.95
- gru256, profilo G, E90, D: Voynichizzatore v21 (libro d'esempio) (generatore) 0.88; Timm e Schinner (seme 1) (generatore) 1.23; Naibbe (generatore) 1.86; Chinese (Pinyin) (lingua) 4.30; Gibberish (Gaskell e Bowern) (generatore) 5.43; Italian (lingua) 6.59. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 4.30
- gru256, profilo G, E90: Timm e Schinner (seme 1) (generatore) 0.71; Voynichizzatore v21 (libro d'esempio) (generatore) 0.77; Naibbe (generatore) 1.09; Chinese (Pinyin) (lingua) 3.79; Voynich, segni rimescolati (controllo negativo) (controllo) 5.05; Gibberish (Gaskell e Bowern) (generatore) 5.18. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.79
- gru512, profilo G, E90, D: Voynichizzatore v21 (libro d'esempio) (generatore) 0.63; Timm e Schinner (seme 1) (generatore) 1.19; Naibbe (generatore) 1.42; Chinese (Pinyin) (lingua) 3.53; Italian (lingua) 5.46; Anglo-Saxon (lingua) 5.47. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.53
- gru512, profilo G, E90: Naibbe (generatore) 0.04; Voynichizzatore v21 (libro d'esempio) (generatore) 0.46; Timm e Schinner (seme 1) (generatore) 0.71; Chinese (Pinyin) (lingua) 3.01; Voynich, segni rimescolati (controllo negativo) (controllo) 5.07; Maori (lingua) 5.40. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.01
- gru2x256, profilo G, E90, D: Voynichizzatore v21 (libro d'esempio) (generatore) 1.16; Timm e Schinner (seme 1) (generatore) 1.27; Naibbe (generatore) 1.85; Chinese (Pinyin) (lingua) 3.29; Gibberish (Gaskell e Bowern) (generatore) 5.17; Anglo-Saxon (lingua) 5.48. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 3.29
- gru2x256, profilo G, E90: Timm e Schinner (seme 1) (generatore) 0.73; Naibbe (generatore) 0.90; Voynichizzatore v21 (libro d'esempio) (generatore) 1.01; Chinese (Pinyin) (lingua) 2.82; Gibberish (Gaskell e Bowern) (generatore) 4.90; Voynich, segni rimescolati (controllo negativo) (controllo) 4.94. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 2.82
- transformer, profilo G, E90: Naibbe (generatore) 0.30; Voynichizzatore v21 (libro d'esempio) (generatore) 0.57; Timm e Schinner (seme 1) (generatore) 0.88; Chinese (Pinyin) (lingua) 1.31; German (lingua) 3.94; Turkish (lingua) 4.04. Generatori fra i 3 più vicini: 3 (restano i generatori: sì); primo non generatore: Chinese (Pinyin) 1.31

## Lettura 3: E90 e scarto del Voynich rispetto alle lingue, per rete

- gru64, E90, Voynich: 5.120, sotto l'intervallo delle lingue [13.517, 26.624] (sotto tutte le lingue)
- gru64, E90, Voynich A: 5.734, sotto l'intervallo delle lingue [13.517, 26.624] (sotto tutte le lingue)
- gru64, E90, Voynich B: 4.096, sotto l'intervallo delle lingue [13.517, 26.624] (sotto tutte le lingue)
- gru64, scarto, Voynich: 0.014, sotto l'intervallo delle lingue [0.069, 0.433] (sotto tutte le lingue)
- gru64, scarto, Voynich A: 0.015, sotto l'intervallo delle lingue [0.069, 0.433] (sotto tutte le lingue)
- gru64, scarto, Voynich B: -0.059, sotto l'intervallo delle lingue [0.069, 0.433] (sotto tutte le lingue)
- gru128, E90, Voynich: 3.686, sotto l'intervallo delle lingue [8.806, 17.203] (sotto tutte le lingue)
- gru128, E90, Voynich A: 4.096, sotto l'intervallo delle lingue [8.806, 17.203] (sotto tutte le lingue)
- gru128, E90, Voynich B: 3.072, sotto l'intervallo delle lingue [8.806, 17.203] (sotto tutte le lingue)
- gru128, scarto, Voynich: 0.040, sotto l'intervallo delle lingue [0.149, 0.661] (sotto tutte le lingue)
- gru128, scarto, Voynich A: 0.070, sotto l'intervallo delle lingue [0.149, 0.661] (sotto tutte le lingue)
- gru128, scarto, Voynich B: 0.011, sotto l'intervallo delle lingue [0.149, 0.661] (sotto tutte le lingue)
- gru256, E90, Voynich: 3.072, sotto l'intervallo delle lingue [6.554, 11.264] (sotto tutte le lingue)
- gru256, E90, Voynich A: 3.072, sotto l'intervallo delle lingue [6.554, 11.264] (sotto tutte le lingue)
- gru256, E90, Voynich B: 2.253, sotto l'intervallo delle lingue [6.554, 11.264] (sotto tutte le lingue)
- gru256, scarto, Voynich: 0.067, sotto l'intervallo delle lingue [0.215, 0.793] (sotto tutte le lingue)
- gru256, scarto, Voynich A: 0.087, sotto l'intervallo delle lingue [0.215, 0.793] (sotto tutte le lingue)
- gru256, scarto, Voynich B: 0.063, sotto l'intervallo delle lingue [0.215, 0.793] (sotto tutte le lingue)
- gru512, E90, Voynich: 2.048, sotto l'intervallo delle lingue [4.437, 8.533] (sotto tutte le lingue)
- gru512, E90, Voynich A: 2.731, sotto l'intervallo delle lingue [4.437, 8.533] (sotto tutte le lingue)
- gru512, E90, Voynich B: 2.048, sotto l'intervallo delle lingue [4.437, 8.533] (sotto tutte le lingue)
- gru512, scarto, Voynich: 0.097, sotto l'intervallo delle lingue [0.243, 0.999] (sotto tutte le lingue)
- gru512, scarto, Voynich A: 0.070, sotto l'intervallo delle lingue [0.243, 0.999] (sotto tutte le lingue)
- gru512, scarto, Voynich B: 0.056, sotto l'intervallo delle lingue [0.243, 0.999] (sotto tutte le lingue)
- gru2x256, E90, Voynich: 2.731, sotto l'intervallo delle lingue [4.779, 8.533] (sotto tutte le lingue)
- gru2x256, E90, Voynich A: 2.731, sotto l'intervallo delle lingue [4.779, 8.533] (sotto tutte le lingue)
- gru2x256, E90, Voynich B: 2.048, sotto l'intervallo delle lingue [4.779, 8.533] (sotto tutte le lingue)
- gru2x256, scarto, Voynich: 0.088, sotto l'intervallo delle lingue [0.270, 0.819] (sotto tutte le lingue)
- gru2x256, scarto, Voynich A: 0.075, sotto l'intervallo delle lingue [0.270, 0.819] (sotto tutte le lingue)
- gru2x256, scarto, Voynich B: 0.057, sotto l'intervallo delle lingue [0.270, 0.819] (sotto tutte le lingue)
- transformer, E90, Voynich: 9.899, sotto l'intervallo delle lingue [14.677, 34.816] (sotto tutte le lingue)
- transformer, E90, Voynich A: 9.557, sotto l'intervallo delle lingue [14.677, 34.816] (sotto tutte le lingue)
- transformer, E90, Voynich B: 9.557, sotto l'intervallo delle lingue [14.677, 34.816] (sotto tutte le lingue)
- transformer, scarto, Voynich: 0.052, sotto l'intervallo delle lingue [0.133, 0.726] (sotto tutte le lingue)
- transformer, scarto, Voynich A: 0.035, sotto l'intervallo delle lingue [0.133, 0.726] (sotto tutte le lingue)
- transformer, scarto, Voynich B: -0.022, sotto l'intervallo delle lingue [0.133, 0.726] (sotto tutte le lingue)

## Lettura 4: il transformer dice lo stesso?

- a_G_dentro_le_lingue: True
- b_E90_sotto_tutte_le_lingue: True
- c_i_3_piu_vicini_sono_i_generatori: True
- d_controlli_riusciti: True
- frazione_corse_al_limite: 0.023
- riserva_limite_passi: False
- dice_lo_stesso: True

## Posizione rispetto alle lingue (G, D), per rete

- gru64, G, Voynich: 0.491, dentro l'intervallo delle lingue [0.219, 0.561], lingue sotto: 95%
- gru64, G, Voynich A: 0.461, dentro l'intervallo delle lingue [0.219, 0.561], lingue sotto: 80%
- gru64, G, Voynich B: 0.523, dentro l'intervallo delle lingue [0.219, 0.561], lingue sotto: 95%
- gru64, D, Voynich: 0.117, dentro l'intervallo delle lingue [-0.001, 0.185], lingue sotto: 90%
- gru128, G, Voynich: 0.491, dentro l'intervallo delle lingue [0.220, 0.565], lingue sotto: 95%
- gru128, G, Voynich A: 0.462, dentro l'intervallo delle lingue [0.220, 0.565], lingue sotto: 75%
- gru128, G, Voynich B: 0.527, dentro l'intervallo delle lingue [0.220, 0.565], lingue sotto: 95%
- gru128, D, Voynich: 0.095, dentro l'intervallo delle lingue [-0.001, 0.203], lingue sotto: 80%
- gru256, G, Voynich: 0.493, dentro l'intervallo delle lingue [0.212, 0.567], lingue sotto: 95%
- gru256, G, Voynich A: 0.462, dentro l'intervallo delle lingue [0.212, 0.567], lingue sotto: 75%
- gru256, G, Voynich B: 0.527, dentro l'intervallo delle lingue [0.212, 0.567], lingue sotto: 95%
- gru256, D, Voynich: 0.096, dentro l'intervallo delle lingue [0.008, 0.230], lingue sotto: 65%
- gru512, G, Voynich: 0.488, dentro l'intervallo delle lingue [0.197, 0.558], lingue sotto: 90%
- gru512, G, Voynich A: 0.460, dentro l'intervallo delle lingue [0.197, 0.558], lingue sotto: 75%
- gru512, G, Voynich B: 0.523, dentro l'intervallo delle lingue [0.197, 0.558], lingue sotto: 95%
- gru512, D, Voynich: 0.094, dentro l'intervallo delle lingue [-0.006, 0.235], lingue sotto: 45%
- gru2x256, G, Voynich: 0.487, dentro l'intervallo delle lingue [0.202, 0.561], lingue sotto: 85%
- gru2x256, G, Voynich A: 0.459, dentro l'intervallo delle lingue [0.202, 0.561], lingue sotto: 70%
- gru2x256, G, Voynich B: 0.524, dentro l'intervallo delle lingue [0.202, 0.561], lingue sotto: 95%
- gru2x256, D, Voynich: 0.106, dentro l'intervallo delle lingue [-0.001, 0.229], lingue sotto: 55%
- transformer, G, Voynich: 0.493, dentro l'intervallo delle lingue [0.224, 0.559], lingue sotto: 85%
- transformer, G, Voynich A: 0.460, dentro l'intervallo delle lingue [0.224, 0.559], lingue sotto: 65%
- transformer, G, Voynich B: 0.526, dentro l'intervallo delle lingue [0.224, 0.559], lingue sotto: 95%
