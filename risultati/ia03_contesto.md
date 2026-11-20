# ia03 (IA3) — quanto contesto serve

Modello a caratteri GRU (128 unità nascoste), finestre di 256 segni da stato vuoto, 8 finestre per passo, 40000 segni di addestramento, 5000 di validazione, 10000 di prova, al massimo 2000 passi, semi 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.
Variante B = GRU più cache neurale (le letture si fanno su questa); variante A = solo GRU (descrittiva). Stessi pesi, stesse corse.
Corse arrivate al massimo dei passi: 0.
Valori: media dei semi (deviazione standard fra i semi). BPC in bit per segno.

# Variante B

## Controlli (B)

- positivo: C3_GR_meno_C1 0.1361, C3_soglia 0.0500, C2_GR_meno_C1 1.3561, C2_soglia 0.5000, C4_GL_meno_C1 1.2857, C4_soglia 0.5000, superato True
- negativo: k90 3, GL 0.0033, GR 0.0003, soglia_k90 4, soglia_GL 0.0200, soglia_GR 0.0300, superato True
- negativo aggiuntivo: Latin, segni rimescolati: GL 0.0471, GR 0.0056, soglia_GL 0.1000, soglia_GR 0.0300, superato True
- negativo aggiuntivo: Voynich, segni rimescolati: GL 0.0066, GR -0.0006, soglia_GL 0.1000, soglia_GR 0.0300, superato True
- verifica B non peggiore di A (max_k BPC_B(k) - BPC_A(k) sulla prova, media dei semi): massimo_controlli 0.0029, massimo_tutti 0.0044, soglia 0.0100, superato True

## Misure per testo (B)

| testo | ruolo | segni | riga (segni) | H1 | BPC(0) | BPC(32) | BPC(255) | k90 | semi k90 non def. | k90 interp. | GL | GR | GR corte | B peggio di A | alfa(255) | theta(255) | s/corsa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | voynich | 25 | 49.4 | 3.939 | 4.018 | 1.955 | 1.905 | 2.3 (0.5) | 0 | 2.0 | 0.049 (0.013) | 0.028 (0.007) | 0.029 | 0.001 | 0.120 | 0.200 | 178 |
| Voynich A | voynich | 27 | 36.1 | 3.958 | 4.036 | 2.136 | 2.103 | 2.4 (0.7) | 0 | 2.1 | 0.033 (0.005) | 0.026 (0.008) | 0.027 | 0.001 | 0.093 | 0.200 | 139 |
| Voynich B | voynich | 24 | 53.5 | 3.916 | 3.981 | 1.852 | 1.810 | 2.0 (0.0) | 0 | 1.8 | 0.042 (0.011) | 0.014 (0.004) | 0.014 | 0.001 | 0.086 | 0.200 | 253 |
| Voynich, segni rimescolati | controllo | 25 | 49.4 | 3.952 | 3.985 | 3.770 | 3.763 | 7.0 (1.4) | 8 | 6.5 | 0.007 (0.004) | -0.001 (0.002) | -0.001 | 0.002 | 0.000 | 0.100 | 179 |
| Timm e Schinner (seme 1) | generatore | 24 | 46.5 | 3.801 | 3.859 | 2.157 | 2.004 | 20.4 (19.4) | 0 | 16.6 | 0.154 (0.042) | 0.071 (0.031) | 0.071 | 0.003 | 0.240 | 0.200 | 180 |
| Voynichizzatore v21 (libro d'esempio) | generatore | 25 | 48.7 | 3.955 | 4.013 | 2.120 | 2.099 | 2.0 (0.0) | 0 | 1.7 | 0.021 (0.006) | 0.010 (0.004) | 0.010 | 0.001 | 0.065 | 0.200 | 172 |
| Naibbe | generatore | 23 | 39.7 | 3.959 | 4.036 | 2.003 | 2.004 | 2.0 (0.0) | 0 | 1.7 | -0.000 (0.001) | 0.003 (0.003) | 0.003 | 0.003 | 0.006 | 0.160 | 160 |
| Gibberish (Gaskell e Bowern) | generatore | 30 | 37.0 | 4.438 | 4.482 | 3.921 | 3.564 | 179.2 (27.0) | 0 | 146.0 | 0.358 (0.067) | 0.172 (0.031) | 0.183 | 0.004 | 0.650 | 0.280 | 134 |
| Anglo-Saxon | lingua | 27 | 35.2 | 4.223 | 4.319 | 2.520 | 2.433 | 6.0 (0.0) | 0 | 5.2 | 0.087 (0.031) | 0.041 (0.014) | 0.041 | 0.001 | 0.370 | 0.220 | 155 |
| Arabic | lingua | 40 | 41.3 | 4.507 | 4.595 | 3.058 | 2.972 | 6.0 (0.0) | 0 | 5.1 | 0.086 (0.015) | 0.018 (0.012) | 0.018 | 0.002 | 0.370 | 0.220 | 168 |
| English | lingua | 26 | 44.9 | 4.140 | 4.207 | 2.346 | 2.277 | 6.2 (0.6) | 0 | 5.5 | 0.069 (0.039) | 0.033 (0.010) | 0.033 | 0.000 | 0.330 | 0.200 | 166 |
| Flemish | lingua | 28 | 42.1 | 4.123 | 4.202 | 2.213 | 2.156 | 6.2 (0.6) | 0 | 5.5 | 0.057 (0.026) | 0.019 (0.009) | 0.019 | 0.002 | 0.580 | 0.200 | 167 |
| French | lingua | 32 | 39.3 | 4.234 | 4.313 | 2.360 | 2.272 | 6.0 (0.0) | 0 | 5.3 | 0.088 (0.031) | 0.035 (0.011) | 0.035 | 0.001 | 0.860 | 0.200 | 173 |
| German | lingua | 34 | 43.4 | 4.343 | 4.427 | 2.295 | 2.228 | 6.0 (0.0) | 0 | 5.3 | 0.067 (0.016) | 0.028 (0.008) | 0.028 | 0.000 | 0.580 | 0.200 | 167 |
| Greek | lingua | 28 | 42.5 | 4.199 | 4.265 | 2.566 | 2.463 | 10.4 (13.2) | 0 | 8.0 | 0.103 (0.039) | 0.038 (0.025) | 0.038 | 0.002 | 0.510 | 0.220 | 164 |
| Italian | lingua | 30 | 46.0 | 4.143 | 4.226 | 2.361 | 2.302 | 6.0 (0.0) | 0 | 4.8 | 0.060 (0.009) | 0.019 (0.010) | 0.019 | 0.001 | 0.370 | 0.220 | 178 |
| Latin (Abbreviated) | lingua | 25 | 38.5 | 4.135 | 4.193 | 3.144 | 3.085 | 8.6 (4.4) | 0 | 7.4 | 0.059 (0.013) | 0.007 (0.010) | 0.007 | 0.001 | 0.240 | 0.220 | 156 |
| Latin | lingua | 25 | 44.7 | 4.131 | 4.200 | 2.862 | 2.813 | 5.6 (0.8) | 0 | 4.5 | 0.049 (0.016) | 0.012 (0.005) | 0.012 | 0.001 | 0.260 | 0.220 | 162 |
| Mayan (Kaqchikel) | lingua | 26 | 54.0 | 4.055 | 4.116 | 2.368 | 2.238 | 8.6 (3.1) | 0 | 7.6 | 0.130 (0.022) | 0.047 (0.009) | 0.047 | 0.001 | 0.720 | 0.200 | 168 |
| Russian | lingua | 43 | 43.0 | 4.637 | 4.729 | 2.747 | 2.652 | 7.8 (5.7) | 0 | 6.1 | 0.095 (0.032) | 0.027 (0.012) | 0.027 | 0.002 | 0.650 | 0.220 | 178 |
| Sanskrit | lingua | 162 | 29.0 | 6.247 | 6.412 | 4.860 | 4.650 | 54.4 (22.6) | 0 | 44.9 | 0.211 (0.044) | 0.101 (0.029) | 0.102 | 0.001 | 0.860 | 0.200 | 161 |
| Spanish | lingua | 32 | 38.5 | 4.204 | 4.287 | 2.402 | 2.299 | 6.2 (0.6) | 0 | 5.7 | 0.103 (0.025) | 0.042 (0.011) | 0.042 | 0.001 | 0.510 | 0.200 | 167 |
| Chinese (Pinyin) | lingua | 47 | 45.6 | 4.666 | 4.779 | 2.032 | 1.958 | 4.0 (0.0) | 0 | 3.4 | 0.074 (0.032) | 0.036 (0.013) | 0.036 | 0.001 | 0.510 | 0.200 | 184 |
| Hebrew | lingua | 30 | 39.8 | 4.184 | 4.248 | 2.963 | 2.878 | 7.6 (5.8) | 0 | 6.4 | 0.085 (0.028) | 0.031 (0.012) | 0.031 | 0.002 | 0.420 | 0.220 | 159 |
| Maori | lingua | 17 | 40.9 | 3.554 | 3.639 | 1.868 | 1.799 | 6.4 (0.8) | 0 | 5.8 | 0.069 (0.036) | 0.051 (0.010) | 0.051 | 0.002 | 0.510 | 0.220 | 172 |
| Swahili | lingua | 27 | 39.8 | 4.084 | 4.161 | 2.364 | 2.276 | 6.2 (0.6) | 0 | 5.9 | 0.088 (0.026) | 0.035 (0.010) | 0.035 | 0.002 | 0.720 | 0.260 | 167 |
| Tagalog | lingua | 25 | 41.0 | 3.811 | 3.900 | 1.962 | 1.883 | 7.2 (1.9) | 0 | 6.6 | 0.079 (0.035) | 0.054 (0.020) | 0.054 | 0.000 | 0.510 | 0.200 | 181 |
| Turkish | lingua | 33 | 42.1 | 4.458 | 4.560 | 2.521 | 2.402 | 6.2 (0.6) | 0 | 5.6 | 0.118 (0.037) | 0.042 (0.016) | 0.042 | 0.001 | 0.930 | 0.240 | 181 |
| Latin, segni rimescolati | controllo | 25 | 44.7 | 4.134 | 4.160 | 4.039 | 3.992 | – (–) | 10 | – | 0.047 (0.021) | 0.006 (0.008) | 0.006 | 0.001 | 0.000 | 0.100 | 148 |
| C1 catena di Markov di ordine 3 (controllo negativo) | controllo | 25 | 43.0 | 4.125 | 4.181 | 2.991 | 2.988 | 3.0 (0.0) | 0 | 2.5 | 0.003 (0.002) | 0.000 (0.003) | 0.000 | 0.002 | 0.037 | 0.200 | 166 |
| C2 latino con ogni riga ripetuta sotto (controllo positivo) | controllo | 25 | 45.0 | 4.150 | 4.237 | 3.047 | 1.773 | 64.0 (0.0) | 0 | 58.3 | 1.275 (0.107) | 1.356 (0.087) | 1.356 | 0.003 | 12.000 | 1.520 | 164 |
| C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni) | controllo | 25 | 45.0 | 4.143 | 4.225 | 3.035 | 1.746 | 255.0 (0.0) | 0 | 241.7 | 1.289 (0.090) | 0.032 (0.061) | 0.032 | 0.001 | 12.000 | 1.440 | 162 |
| C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo) | controllo | 25 | 48.5 | 4.106 | 4.190 | 2.787 | 2.735 | 5.2 (1.0) | 0 | 4.4 | 0.053 (0.017) | 0.136 (0.010) | 0.136 | 0.001 | 0.240 | 0.220 | 175 |

## Curva BPC(k), media dei semi (B)

| testo | 0 | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 16 | 24 | 32 | 48 | 64 | 96 | 128 | 192 | 255 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | 4.018 | 2.369 | 2.104 | 2.050 | 2.026 | 2.006 | 1.993 | 1.980 | 1.972 | 1.963 | 1.955 | 1.943 | 1.936 | 1.927 | 1.921 | 1.912 | 1.905 |
| Voynich A | 4.036 | 2.537 | 2.287 | 2.236 | 2.216 | 2.192 | 2.177 | 2.163 | 2.153 | 2.144 | 2.136 | 2.128 | 2.120 | 2.114 | 2.110 | 2.107 | 2.103 |
| Voynich B | 3.981 | 2.233 | 1.982 | 1.931 | 1.911 | 1.895 | 1.886 | 1.875 | 1.867 | 1.859 | 1.852 | 1.839 | 1.834 | 1.827 | 1.822 | 1.814 | 1.810 |
| Voynich, segni rimescolati | 3.985 | 3.910 | 3.868 | 3.837 | 3.811 | 3.784 | 3.780 | 3.775 | 3.772 | 3.770 | 3.770 | 3.766 | 3.765 | 3.763 | 3.763 | 3.764 | 3.763 |
| Timm e Schinner (seme 1) | 3.859 | 2.501 | 2.350 | 2.296 | 2.251 | 2.225 | 2.215 | 2.202 | 2.192 | 2.172 | 2.157 | 2.132 | 2.111 | 2.087 | 2.063 | 2.031 | 2.004 |
| Voynichizzatore v21 (libro d'esempio) | 4.013 | 2.456 | 2.212 | 2.163 | 2.152 | 2.139 | 2.133 | 2.130 | 2.128 | 2.124 | 2.120 | 2.115 | 2.114 | 2.108 | 2.106 | 2.102 | 2.099 |
| Naibbe | 4.036 | 2.413 | 2.133 | 2.064 | 2.025 | 2.006 | 2.004 | 2.004 | 2.004 | 2.003 | 2.003 | 2.004 | 2.004 | 2.004 | 2.004 | 2.005 | 2.004 |
| Gibberish (Gaskell e Bowern) | 4.482 | 4.193 | 4.126 | 4.106 | 4.088 | 4.065 | 4.049 | 4.018 | 3.992 | 3.951 | 3.921 | 3.859 | 3.804 | 3.734 | 3.677 | 3.606 | 3.564 |
| Anglo-Saxon | 4.319 | 3.690 | 3.130 | 2.850 | 2.695 | 2.571 | 2.544 | 2.536 | 2.533 | 2.526 | 2.520 | 2.506 | 2.492 | 2.473 | 2.462 | 2.443 | 2.433 |
| Arabic | 4.595 | 4.097 | 3.630 | 3.330 | 3.184 | 3.096 | 3.078 | 3.076 | 3.071 | 3.065 | 3.058 | 3.047 | 3.039 | 3.020 | 3.005 | 2.986 | 2.972 |
| English | 4.207 | 3.587 | 3.076 | 2.767 | 2.582 | 2.421 | 2.378 | 2.362 | 2.358 | 2.351 | 2.346 | 2.337 | 2.330 | 2.320 | 2.312 | 2.291 | 2.277 |
| Flemish | 4.202 | 3.535 | 3.005 | 2.695 | 2.497 | 2.311 | 2.249 | 2.223 | 2.220 | 2.215 | 2.213 | 2.207 | 2.205 | 2.199 | 2.187 | 2.170 | 2.156 |
| French | 4.313 | 3.692 | 3.076 | 2.764 | 2.577 | 2.426 | 2.391 | 2.373 | 2.369 | 2.364 | 2.360 | 2.349 | 2.342 | 2.323 | 2.309 | 2.285 | 2.272 |
| German | 4.427 | 3.631 | 3.115 | 2.790 | 2.575 | 2.388 | 2.329 | 2.306 | 2.303 | 2.298 | 2.295 | 2.290 | 2.286 | 2.272 | 2.264 | 2.242 | 2.228 |
| Greek | 4.265 | 3.508 | 3.107 | 2.866 | 2.716 | 2.615 | 2.586 | 2.579 | 2.579 | 2.574 | 2.566 | 2.549 | 2.536 | 2.519 | 2.499 | 2.480 | 2.463 |
| Italian | 4.226 | 3.567 | 3.069 | 2.748 | 2.556 | 2.404 | 2.372 | 2.367 | 2.364 | 2.363 | 2.361 | 2.354 | 2.347 | 2.336 | 2.326 | 2.312 | 2.302 |
| Latin (Abbreviated) | 4.193 | 3.759 | 3.493 | 3.343 | 3.249 | 3.192 | 3.177 | 3.170 | 3.164 | 3.156 | 3.144 | 3.134 | 3.130 | 3.120 | 3.110 | 3.097 | 3.085 |
| Latin | 4.200 | 3.734 | 3.313 | 3.099 | 2.970 | 2.885 | 2.869 | 2.866 | 2.865 | 2.864 | 2.862 | 2.857 | 2.854 | 2.845 | 2.837 | 2.824 | 2.813 |
| Mayan (Kaqchikel) | 4.116 | 3.517 | 3.046 | 2.773 | 2.578 | 2.439 | 2.404 | 2.388 | 2.384 | 2.377 | 2.368 | 2.353 | 2.332 | 2.307 | 2.285 | 2.256 | 2.238 |
| Russian | 4.729 | 3.743 | 3.328 | 3.071 | 2.921 | 2.797 | 2.772 | 2.762 | 2.761 | 2.755 | 2.747 | 2.735 | 2.725 | 2.704 | 2.689 | 2.664 | 2.652 |
| Sanskrit | 6.412 | 5.406 | 5.059 | 4.988 | 4.972 | 4.961 | 4.953 | 4.932 | 4.908 | 4.877 | 4.860 | 4.832 | 4.787 | 4.747 | 4.719 | 4.681 | 4.650 |
| Spanish | 4.287 | 3.491 | 3.107 | 2.813 | 2.625 | 2.470 | 2.432 | 2.419 | 2.415 | 2.407 | 2.402 | 2.387 | 2.376 | 2.357 | 2.338 | 2.311 | 2.299 |
| Chinese (Pinyin) | 4.779 | 3.106 | 2.539 | 2.289 | 2.177 | 2.080 | 2.053 | 2.045 | 2.042 | 2.037 | 2.032 | 2.024 | 2.016 | 1.995 | 1.986 | 1.966 | 1.958 |
| Hebrew | 4.248 | 3.861 | 3.412 | 3.166 | 3.051 | 2.985 | 2.978 | 2.978 | 2.974 | 2.969 | 2.963 | 2.951 | 2.939 | 2.922 | 2.906 | 2.889 | 2.878 |
| Maori | 3.639 | 2.812 | 2.567 | 2.301 | 2.132 | 1.962 | 1.900 | 1.878 | 1.876 | 1.872 | 1.868 | 1.859 | 1.848 | 1.835 | 1.825 | 1.811 | 1.799 |
| Swahili | 4.161 | 3.323 | 3.073 | 2.807 | 2.621 | 2.446 | 2.400 | 2.379 | 2.377 | 2.370 | 2.364 | 2.354 | 2.341 | 2.323 | 2.306 | 2.286 | 2.276 |
| Tagalog | 3.900 | 3.153 | 2.791 | 2.528 | 2.318 | 2.086 | 2.014 | 1.977 | 1.973 | 1.969 | 1.962 | 1.951 | 1.941 | 1.925 | 1.915 | 1.898 | 1.883 |
| Turkish | 4.560 | 3.833 | 3.313 | 2.946 | 2.744 | 2.580 | 2.548 | 2.539 | 2.536 | 2.527 | 2.521 | 2.509 | 2.489 | 2.472 | 2.455 | 2.426 | 2.402 |
| Latin, segni rimescolati | 4.160 | 4.126 | 4.099 | 4.099 | 4.088 | 4.074 | 4.070 | 4.063 | 4.054 | 4.037 | 4.039 | 3.996 | 3.993 | 3.993 | 3.992 | 3.993 | 3.992 |
| C1 catena di Markov di ordine 3 (controllo negativo) | 4.181 | 3.697 | 3.238 | 3.000 | 2.985 | 2.989 | 2.991 | 2.991 | 2.992 | 2.991 | 2.991 | 2.991 | 2.990 | 2.989 | 2.989 | 2.989 | 2.988 |
| C2 latino con ogni riga ripetuta sotto (controllo positivo) | 4.237 | 3.803 | 3.402 | 3.232 | 3.135 | 3.084 | 3.074 | 3.067 | 3.068 | 3.060 | 3.047 | 2.584 | 1.708 | 1.722 | 1.738 | 1.758 | 1.773 |
| C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni) | 4.225 | 3.809 | 3.404 | 3.215 | 3.112 | 3.059 | 3.048 | 3.046 | 3.042 | 3.038 | 3.035 | 3.017 | 3.004 | 2.983 | 2.971 | 2.918 | 1.746 |
| C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo) | 4.190 | 3.724 | 3.337 | 3.117 | 2.893 | 2.818 | 2.798 | 2.793 | 2.792 | 2.790 | 2.787 | 2.782 | 2.778 | 2.770 | 2.761 | 2.745 | 2.735 |

## Posizione rispetto alle lingue (B)

- k90, Voynich: 2.300, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, Voynich A: 2.400, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, Voynich B: 2.000, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, Voynich, segni rimescolati: 7.000, dentro l'intervallo delle lingue [4.000, 54.400], lingue sotto: 65%
- k90, Timm e Schinner (seme 1): 20.400, dentro l'intervallo delle lingue [4.000, 54.400], lingue sotto: 95%
- k90, Voynichizzatore v21 (libro d'esempio): 2.000, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, Naibbe: 2.000, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, Gibberish (Gaskell e Bowern): 179.200, sopra l'intervallo delle lingue [4.000, 54.400], lingue sotto: 100%
- k90, C1 catena di Markov di ordine 3 (controllo negativo): 3.000, sotto l'intervallo delle lingue [4.000, 54.400], lingue sotto: 0%
- k90, C2 latino con ogni riga ripetuta sotto (controllo positivo): 64.000, sopra l'intervallo delle lingue [4.000, 54.400], lingue sotto: 100%
- k90, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 255.000, sopra l'intervallo delle lingue [4.000, 54.400], lingue sotto: 100%
- k90, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 5.200, dentro l'intervallo delle lingue [4.000, 54.400], lingue sotto: 5%
- k90_interpolato, Voynich: 2.005, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, Voynich A: 2.063, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, Voynich B: 1.819, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, Voynich, segni rimescolati: 6.490, dentro l'intervallo delle lingue [3.421, 44.908], lingue sotto: 75%
- k90_interpolato, Timm e Schinner (seme 1): 16.556, dentro l'intervallo delle lingue [3.421, 44.908], lingue sotto: 95%
- k90_interpolato, Voynichizzatore v21 (libro d'esempio): 1.676, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, Naibbe: 1.735, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, Gibberish (Gaskell e Bowern): 145.996, sopra l'intervallo delle lingue [3.421, 44.908], lingue sotto: 100%
- k90_interpolato, C1 catena di Markov di ordine 3 (controllo negativo): 2.549, sotto l'intervallo delle lingue [3.421, 44.908], lingue sotto: 0%
- k90_interpolato, C2 latino con ogni riga ripetuta sotto (controllo positivo): 58.301, sopra l'intervallo delle lingue [3.421, 44.908], lingue sotto: 100%
- k90_interpolato, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 241.655, sopra l'intervallo delle lingue [3.421, 44.908], lingue sotto: 100%
- k90_interpolato, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 4.432, dentro l'intervallo delle lingue [3.421, 44.908], lingue sotto: 5%
- GL, Voynich: 0.049, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Voynich A: 0.033, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Voynich B: 0.042, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Voynich, segni rimescolati: 0.007, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Timm e Schinner (seme 1): 0.154, dentro l'intervallo delle lingue [0.049, 0.211], lingue sotto: 95%
- GL, Voynichizzatore v21 (libro d'esempio): 0.021, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Naibbe: -0.000, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, Gibberish (Gaskell e Bowern): 0.358, sopra l'intervallo delle lingue [0.049, 0.211], lingue sotto: 100%
- GL, Latin, segni rimescolati: 0.047, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, C1 catena di Markov di ordine 3 (controllo negativo): 0.003, sotto l'intervallo delle lingue [0.049, 0.211], lingue sotto: 0%
- GL, C2 latino con ogni riga ripetuta sotto (controllo positivo): 1.275, sopra l'intervallo delle lingue [0.049, 0.211], lingue sotto: 100%
- GL, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 1.289, sopra l'intervallo delle lingue [0.049, 0.211], lingue sotto: 100%
- GL, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.053, dentro l'intervallo delle lingue [0.049, 0.211], lingue sotto: 5%
- GR, Voynich: 0.028, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 35%
- GR, Voynich A: 0.026, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 25%
- GR, Voynich B: 0.014, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 10%
- GR, Voynich, segni rimescolati: -0.001, sotto l'intervallo delle lingue [0.007, 0.101], lingue sotto: 0%
- GR, Timm e Schinner (seme 1): 0.071, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 95%
- GR, Voynichizzatore v21 (libro d'esempio): 0.010, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 5%
- GR, Naibbe: 0.003, sotto l'intervallo delle lingue [0.007, 0.101], lingue sotto: 0%
- GR, Gibberish (Gaskell e Bowern): 0.172, sopra l'intervallo delle lingue [0.007, 0.101], lingue sotto: 100%
- GR, Latin, segni rimescolati: 0.006, sotto l'intervallo delle lingue [0.007, 0.101], lingue sotto: 0%
- GR, C1 catena di Markov di ordine 3 (controllo negativo): 0.000, sotto l'intervallo delle lingue [0.007, 0.101], lingue sotto: 0%
- GR, C2 latino con ogni riga ripetuta sotto (controllo positivo): 1.356, sopra l'intervallo delle lingue [0.007, 0.101], lingue sotto: 100%
- GR, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 0.032, dentro l'intervallo delle lingue [0.007, 0.101], lingue sotto: 40%
- GR, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.136, sopra l'intervallo delle lingue [0.007, 0.101], lingue sotto: 100%
- GR_corte, Voynich: 0.029, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 35%
- GR_corte, Voynich A: 0.027, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 25%
- GR_corte, Voynich B: 0.014, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 10%
- GR_corte, Voynich, segni rimescolati: -0.001, sotto l'intervallo delle lingue [0.007, 0.102], lingue sotto: 0%
- GR_corte, Timm e Schinner (seme 1): 0.071, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 95%
- GR_corte, Voynichizzatore v21 (libro d'esempio): 0.010, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 5%
- GR_corte, Naibbe: 0.003, sotto l'intervallo delle lingue [0.007, 0.102], lingue sotto: 0%
- GR_corte, Gibberish (Gaskell e Bowern): 0.183, sopra l'intervallo delle lingue [0.007, 0.102], lingue sotto: 100%
- GR_corte, Latin, segni rimescolati: 0.006, sotto l'intervallo delle lingue [0.007, 0.102], lingue sotto: 0%
- GR_corte, C1 catena di Markov di ordine 3 (controllo negativo): 0.000, sotto l'intervallo delle lingue [0.007, 0.102], lingue sotto: 0%
- GR_corte, C2 latino con ogni riga ripetuta sotto (controllo positivo): 1.356, sopra l'intervallo delle lingue [0.007, 0.102], lingue sotto: 100%
- GR_corte, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 0.032, dentro l'intervallo delle lingue [0.007, 0.102], lingue sotto: 40%
- GR_corte, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.136, sopra l'intervallo delle lingue [0.007, 0.102], lingue sotto: 100%
- G255, Voynich: 0.516, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 95%
- G255, Voynich A: 0.469, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 75%
- G255, Voynich B: 0.538, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 95%
- G255, Voynich, segni rimescolati: 0.048, sotto l'intervallo delle lingue [0.254, 0.580], lingue sotto: 0%
- G255, Timm e Schinner (seme 1): 0.473, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 75%
- G255, Voynichizzatore v21 (libro d'esempio): 0.469, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 75%
- G255, Naibbe: 0.494, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 90%
- G255, Gibberish (Gaskell e Bowern): 0.197, sotto l'intervallo delle lingue [0.254, 0.580], lingue sotto: 0%
- G255, Latin, segni rimescolati: 0.034, sotto l'intervallo delle lingue [0.254, 0.580], lingue sotto: 0%
- G255, C1 catena di Markov di ordine 3 (controllo negativo): 0.276, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 10%
- G255, C2 latino con ogni riga ripetuta sotto (controllo positivo): 0.573, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 95%
- G255, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 0.579, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 95%
- G255, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.334, dentro l'intervallo delle lingue [0.254, 0.580], lingue sotto: 20%
- bpc255, Voynich: 1.905, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 10%
- bpc255, Voynich A: 2.103, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 15%
- bpc255, Voynich B: 1.810, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 5%
- bpc255, Voynich, segni rimescolati: 3.763, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 95%
- bpc255, Timm e Schinner (seme 1): 2.004, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 15%
- bpc255, Voynichizzatore v21 (libro d'esempio): 2.099, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 15%
- bpc255, Naibbe: 2.004, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 15%
- bpc255, Gibberish (Gaskell e Bowern): 3.564, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 95%
- bpc255, Latin, segni rimescolati: 3.992, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 95%
- bpc255, C1 catena di Markov di ordine 3 (controllo negativo): 2.988, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 90%
- bpc255, C2 latino con ogni riga ripetuta sotto (controllo positivo): 1.773, sotto l'intervallo delle lingue [1.799, 4.650], lingue sotto: 0%
- bpc255, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 1.746, sotto l'intervallo delle lingue [1.799, 4.650], lingue sotto: 0%
- bpc255, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 2.735, dentro l'intervallo delle lingue [1.799, 4.650], lingue sotto: 75%
- guadagno_totale, Voynich: 2.113, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 85%
- guadagno_totale, Voynich A: 1.933, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 60%
- guadagno_totale, Voynich B: 2.171, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 90%
- guadagno_totale, Voynich, segni rimescolati: 0.223, sotto l'intervallo delle lingue [1.108, 2.821], lingue sotto: 0%
- guadagno_totale, Timm e Schinner (seme 1): 1.856, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 35%
- guadagno_totale, Voynichizzatore v21 (libro d'esempio): 1.914, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 50%
- guadagno_totale, Naibbe: 2.032, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 70%
- guadagno_totale, Gibberish (Gaskell e Bowern): 0.919, sotto l'intervallo delle lingue [1.108, 2.821], lingue sotto: 0%
- guadagno_totale, Latin, segni rimescolati: 0.168, sotto l'intervallo delle lingue [1.108, 2.821], lingue sotto: 0%
- guadagno_totale, C1 catena di Markov di ordine 3 (controllo negativo): 1.194, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 5%
- guadagno_totale, C2 latino con ogni riga ripetuta sotto (controllo positivo): 2.464, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 95%
- guadagno_totale, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 2.479, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 95%
- guadagno_totale, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 1.456, dentro l'intervallo delle lingue [1.108, 2.821], lingue sotto: 15%

## Voynich lingua A meno lingua B (differenza di medie) (B)

- k90_interpolato: +0.244 (errore standard 0.112, non appaiato, 10 e 10 semi)
- GL: -0.009 (errore standard 0.004, non appaiato, 10 e 10 semi)
- GR_corte: +0.013 (errore standard 0.003, non appaiato, 10 e 10 semi)

## Pagine di solo testo (GR sui bersagli corti, bit per segno) (B)

- Voynich: GR sulle pagine usabili 0.018 (ds 0.006, 10 semi); GR sulla prova 0.029
  - f66r: 6 semi, 9660 segni, GR 0.012
  - f76r: 8 semi, 22096 segni, GR 0.020
  - f85r1: 5 semi, 9380 segni, GR 0.007
  - f86v6: 8 semi, 20992 segni, GR 0.009
  - f1r: 4 semi, 3832 segni, GR 0.083
  - f86v5: 6 semi, 12102 segni, GR 0.022

## Testi più vicini al Voynich sul profilo (k90 interpolato, GL, GR corte) (B)

Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea.

- Voynich: German (lingua) 0.63; Italian (lingua) 0.64; Flemish (lingua) 0.67; English (lingua) 0.73; Chinese (Pinyin) (lingua) 0.82; Latin (lingua) 0.89
- Voynich A: Flemish (lingua) 0.88; Voynichizzatore v21 (libro d'esempio) (generatore) 0.90; Italian (lingua) 0.90; Latin (lingua) 0.94; German (lingua) 1.03; English (lingua) 1.14
- Voynich B: Latin (lingua) 0.38; Voynichizzatore v21 (libro d'esempio) (generatore) 0.62; Flemish (lingua) 0.63; Italian (lingua) 0.66; Latin (Abbreviated) (lingua) 0.87; German (lingua) 1.06

## Generatori e controlli rispetto al Voynich (B)

"vicino": differenza al massimo un decimo dell'intervallo delle lingue (almeno 0.02 per GL e GR).

- Voynich, segni rimescolati: k90_interpolato +4.486, GL -0.043, GR_corte -0.029
- Timm e Schinner (seme 1): k90_interpolato +14.552, GL +0.104, GR_corte +0.042
- Voynichizzatore v21 (libro d'esempio): k90_interpolato -0.329 (vicino), GL -0.028, GR_corte -0.018 (vicino)
- Naibbe: k90_interpolato -0.270 (vicino), GL -0.050, GR_corte -0.026
- Gibberish (Gaskell e Bowern): k90_interpolato +143.991, GL +0.309, GR_corte +0.154
- Latin, segni rimescolati: GL -0.002 (vicino), GR_corte -0.023
- C1 catena di Markov di ordine 3 (controllo negativo): k90_interpolato +0.544 (vicino), GL -0.046, GR_corte -0.028
- C2 latino con ogni riga ripetuta sotto (controllo positivo): k90_interpolato +56.296, GL +1.225, GR_corte +1.328
- C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): k90_interpolato +239.650, GL +1.240, GR_corte +0.004 (vicino)
- C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): k90_interpolato +2.428 (vicino), GL +0.003 (vicino), GR_corte +0.108

## Letture (criteri della preregistrazione) (B)

- Voynich: {'GL_oltre_zero': True, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- Voynich A: {'GL_oltre_zero': True, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- Voynich B: {'GL_oltre_zero': True, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- A_contro_B: OrderedDict({'k90_interpolato': {'differiscono': False, 'A_meno_B': 0.24359179594085223}, 'GL': {'differiscono': False, 'A_meno_B': -0.009095000000000013}, 'GR_corte': {'differiscono': False, 'A_meno_B': 0.013072156661217865}})
- pagine_di_solo_testo: {'differenza': -0.010566808982165193, 'piu_alta': False}

# Variante A

## Controlli (A)

- positivo: C3_GR_meno_C1 0.1285, C3_soglia 0.0500, superato True
- negativo: k90 3, GL -0.0000, GR -0.0018, soglia_k90 4, soglia_GL 0.0200, soglia_GR 0.0300, superato True
- negativo aggiuntivo: Latin, segni rimescolati: GL 0.0467, GR 0.0055, soglia_GL 0.1000, soglia_GR 0.0300, superato True
- negativo aggiuntivo: Voynich, segni rimescolati: GL 0.0064, GR -0.0006, soglia_GL 0.1000, soglia_GR 0.0300, superato True
- sonda di portata (non decide): C2 latino con ogni riga ripetuta sotto (controllo positivo) {'GR': -0.0015276816155155892, 'GL': 0.00030699999999996843}, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni) {'GR': -0.003024933481156953, 'GL': -2.9999999999752447e-06}

## Misure per testo (A)

| testo | ruolo | segni | riga (segni) | H1 | BPC(0) | BPC(32) | BPC(255) | k90 | semi k90 non def. | k90 interp. | GL | GR | GR corte | B peggio di A | alfa(255) | theta(255) | s/corsa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | voynich | 25 | 49.4 | 3.939 | 4.018 | 1.970 | 1.961 | 2.0 (0.0) | 0 | 1.8 | 0.009 (0.006) | 0.014 (0.007) | 0.014 | – | – | – | 178 |
| Voynich A | voynich | 27 | 36.1 | 3.958 | 4.036 | 2.149 | 2.139 | 2.1 (0.3) | 0 | 1.9 | 0.010 (0.008) | 0.015 (0.009) | 0.016 | – | – | – | 139 |
| Voynich B | voynich | 24 | 53.5 | 3.916 | 3.981 | 1.864 | 1.851 | 2.0 (0.0) | 0 | 1.7 | 0.013 (0.005) | 0.006 (0.003) | 0.006 | – | – | – | 253 |
| Voynich, segni rimescolati | controllo | 25 | 49.4 | 3.952 | 3.985 | 3.769 | 3.763 | 6.0 (0.0) | 8 | 5.8 | 0.006 (0.004) | -0.001 (0.001) | -0.001 | – | – | – | 179 |
| Timm e Schinner (seme 1) | generatore | 24 | 46.5 | 3.801 | 3.859 | 2.208 | 2.196 | 2.3 (0.5) | 0 | 2.0 | 0.012 (0.007) | 0.013 (0.009) | 0.013 | – | – | – | 180 |
| Voynichizzatore v21 (libro d'esempio) | generatore | 25 | 48.7 | 3.955 | 4.013 | 2.125 | 2.122 | 2.0 (0.0) | 0 | 1.6 | 0.003 (0.002) | 0.004 (0.003) | 0.004 | – | – | – | 172 |
| Naibbe | generatore | 23 | 39.7 | 3.959 | 4.036 | 2.003 | 2.003 | 2.0 (0.0) | 0 | 1.7 | 0.000 (0.000) | 0.003 (0.002) | 0.003 | – | – | – | 160 |
| Gibberish (Gaskell e Bowern) | generatore | 30 | 37.0 | 4.438 | 4.482 | 4.013 | 3.996 | 12.3 (9.7) | 0 | 10.8 | 0.017 (0.008) | 0.034 (0.016) | 0.035 | – | – | – | 134 |
| Anglo-Saxon | lingua | 27 | 35.2 | 4.223 | 4.319 | 2.536 | 2.537 | 4.4 (0.8) | 0 | 3.9 | -0.000 (0.000) | 0.002 (0.004) | 0.002 | – | – | – | 155 |
| Arabic | lingua | 40 | 41.3 | 4.507 | 4.595 | 3.077 | 3.077 | 4.0 (0.0) | 0 | 3.7 | 0.000 (0.000) | -0.002 (0.005) | -0.002 | – | – | – | 168 |
| English | lingua | 26 | 44.9 | 4.140 | 4.207 | 2.362 | 2.361 | 5.8 (0.6) | 0 | 4.5 | 0.001 (0.003) | 0.013 (0.009) | 0.013 | – | – | – | 166 |
| Flemish | lingua | 28 | 42.1 | 4.123 | 4.202 | 2.224 | 2.224 | 6.0 (0.0) | 0 | 4.8 | 0.000 (0.000) | 0.005 (0.005) | 0.005 | – | – | – | 167 |
| French | lingua | 32 | 39.3 | 4.234 | 4.313 | 2.370 | 2.370 | 5.6 (0.8) | 0 | 4.2 | 0.000 (0.000) | 0.012 (0.004) | 0.012 | – | – | – | 173 |
| German | lingua | 34 | 43.4 | 4.343 | 4.427 | 2.307 | 2.307 | 5.8 (0.6) | 0 | 4.6 | 0.000 (0.000) | 0.014 (0.007) | 0.014 | – | – | – | 167 |
| Greek | lingua | 28 | 42.5 | 4.199 | 4.265 | 2.581 | 2.580 | 4.0 (0.0) | 0 | 3.8 | 0.001 (0.003) | 0.005 (0.005) | 0.005 | – | – | – | 164 |
| Italian | lingua | 30 | 46.0 | 4.143 | 4.226 | 2.366 | 2.365 | 4.8 (1.0) | 0 | 4.1 | 0.000 (0.001) | 0.005 (0.005) | 0.005 | – | – | – | 178 |
| Latin (Abbreviated) | lingua | 25 | 38.5 | 4.135 | 4.193 | 3.150 | 3.145 | 4.8 (1.0) | 0 | 4.4 | 0.005 (0.008) | -0.005 (0.003) | -0.005 | – | – | – | 156 |
| Latin | lingua | 25 | 44.7 | 4.131 | 4.200 | 2.869 | 2.869 | 4.2 (0.6) | 0 | 3.8 | 0.000 (0.000) | -0.000 (0.003) | -0.000 | – | – | – | 162 |
| Mayan (Kaqchikel) | lingua | 26 | 54.0 | 4.055 | 4.116 | 2.392 | 2.392 | 5.2 (1.0) | 0 | 4.2 | 0.000 (0.000) | 0.007 (0.005) | 0.007 | – | – | – | 168 |
| Russian | lingua | 43 | 43.0 | 4.637 | 4.729 | 2.763 | 2.763 | 4.0 (0.0) | 0 | 3.7 | 0.000 (0.000) | -0.002 (0.003) | -0.002 | – | – | – | 178 |
| Sanskrit | lingua | 162 | 29.0 | 6.247 | 6.412 | 4.944 | 4.945 | 2.1 (0.3) | 0 | 1.9 | -0.001 (0.002) | -0.002 (0.006) | -0.002 | – | – | – | 161 |
| Spanish | lingua | 32 | 38.5 | 4.204 | 4.287 | 2.417 | 2.417 | 5.6 (0.8) | 0 | 4.3 | -0.000 (0.000) | 0.010 (0.005) | 0.010 | – | – | – | 167 |
| Chinese (Pinyin) | lingua | 47 | 45.6 | 4.666 | 4.779 | 2.045 | 2.045 | 3.2 (0.4) | 0 | 2.9 | -0.000 (0.000) | 0.019 (0.008) | 0.019 | – | – | – | 184 |
| Hebrew | lingua | 30 | 39.8 | 4.184 | 4.248 | 2.975 | 2.975 | 4.0 (0.0) | 0 | 3.5 | 0.000 (0.000) | 0.003 (0.002) | 0.003 | – | – | – | 159 |
| Maori | lingua | 17 | 40.9 | 3.554 | 3.639 | 1.876 | 1.876 | 6.0 (0.0) | 0 | 4.9 | 0.000 (0.000) | 0.028 (0.004) | 0.028 | – | – | – | 172 |
| Swahili | lingua | 27 | 39.8 | 4.084 | 4.161 | 2.379 | 2.378 | 6.0 (0.0) | 0 | 4.7 | 0.001 (0.002) | 0.007 (0.003) | 0.007 | – | – | – | 167 |
| Tagalog | lingua | 25 | 41.0 | 3.811 | 3.900 | 1.977 | 1.977 | 6.0 (0.0) | 0 | 5.3 | 0.000 (0.000) | 0.028 (0.005) | 0.028 | – | – | – | 181 |
| Turkish | lingua | 33 | 42.1 | 4.458 | 4.560 | 2.538 | 2.538 | 5.2 (1.0) | 0 | 4.1 | 0.000 (0.000) | 0.002 (0.005) | 0.002 | – | – | – | 181 |
| Latin, segni rimescolati | controllo | 25 | 44.7 | 4.134 | 4.160 | 4.039 | 3.992 | – (–) | 10 | – | 0.047 (0.021) | 0.006 (0.008) | 0.006 | – | – | – | 148 |
| C1 catena di Markov di ordine 3 (controllo negativo) | controllo | 25 | 43.0 | 4.125 | 4.181 | 2.991 | 2.991 | 3.0 (0.0) | 0 | 2.5 | -0.000 (0.000) | -0.001 (0.003) | -0.002 | – | – | – | 166 |
| C2 latino con ogni riga ripetuta sotto (controllo positivo) | controllo | 25 | 45.0 | 4.150 | 4.237 | 3.071 | 3.071 | 4.2 (0.6) | 0 | 3.5 | 0.000 (0.001) | -0.002 (0.003) | -0.002 | – | – | – | 164 |
| C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni) | controllo | 25 | 45.0 | 4.143 | 4.225 | 3.050 | 3.050 | 4.0 (0.0) | 0 | 3.5 | -0.000 (0.000) | -0.003 (0.004) | -0.003 | – | – | – | 162 |
| C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo) | controllo | 25 | 48.5 | 4.106 | 4.190 | 2.794 | 2.793 | 4.0 (0.0) | 0 | 3.8 | 0.002 (0.005) | 0.127 (0.012) | 0.127 | – | – | – | 175 |

## Curva BPC(k), media dei semi (A)

| testo | 0 | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 16 | 24 | 32 | 48 | 64 | 96 | 128 | 192 | 255 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Voynich | 4.018 | 2.369 | 2.104 | 2.050 | 2.025 | 2.006 | 1.994 | 1.984 | 1.979 | 1.975 | 1.970 | 1.963 | 1.961 | 1.961 | 1.961 | 1.961 | 1.961 |
| Voynich A | 4.036 | 2.537 | 2.287 | 2.236 | 2.216 | 2.192 | 2.179 | 2.166 | 2.158 | 2.153 | 2.149 | 2.144 | 2.142 | 2.140 | 2.140 | 2.139 | 2.139 |
| Voynich B | 3.981 | 2.233 | 1.981 | 1.930 | 1.911 | 1.895 | 1.887 | 1.877 | 1.872 | 1.868 | 1.864 | 1.854 | 1.851 | 1.851 | 1.851 | 1.851 | 1.851 |
| Voynich, segni rimescolati | 3.985 | 3.909 | 3.868 | 3.837 | 3.811 | 3.783 | 3.779 | 3.775 | 3.772 | 3.770 | 3.769 | 3.765 | 3.764 | 3.763 | 3.763 | 3.763 | 3.763 |
| Timm e Schinner (seme 1) | 3.859 | 2.500 | 2.349 | 2.296 | 2.252 | 2.227 | 2.224 | 2.220 | 2.217 | 2.212 | 2.208 | 2.201 | 2.200 | 2.198 | 2.197 | 2.196 | 2.196 |
| Voynichizzatore v21 (libro d'esempio) | 4.013 | 2.455 | 2.212 | 2.163 | 2.152 | 2.139 | 2.133 | 2.131 | 2.129 | 2.127 | 2.125 | 2.123 | 2.122 | 2.122 | 2.122 | 2.122 | 2.122 |
| Naibbe | 4.036 | 2.413 | 2.133 | 2.064 | 2.024 | 2.006 | 2.004 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 | 2.003 |
| Gibberish (Gaskell e Bowern) | 4.482 | 4.191 | 4.127 | 4.107 | 4.092 | 4.073 | 4.063 | 4.048 | 4.036 | 4.022 | 4.013 | 4.006 | 4.002 | 3.999 | 3.997 | 3.996 | 3.996 |
| Anglo-Saxon | 4.319 | 3.694 | 3.131 | 2.851 | 2.696 | 2.572 | 2.544 | 2.537 | 2.537 | 2.537 | 2.536 | 2.537 | 2.537 | 2.537 | 2.537 | 2.537 | 2.537 |
| Arabic | 4.595 | 4.097 | 3.630 | 3.330 | 3.185 | 3.096 | 3.079 | 3.077 | 3.077 | 3.077 | 3.077 | 3.076 | 3.077 | 3.077 | 3.077 | 3.077 | 3.077 |
| English | 4.207 | 3.599 | 3.081 | 2.768 | 2.583 | 2.421 | 2.379 | 2.364 | 2.363 | 2.362 | 2.362 | 2.360 | 2.361 | 2.361 | 2.361 | 2.361 | 2.361 |
| Flemish | 4.202 | 3.545 | 3.006 | 2.696 | 2.498 | 2.311 | 2.250 | 2.225 | 2.224 | 2.224 | 2.224 | 2.224 | 2.224 | 2.224 | 2.224 | 2.224 | 2.224 |
| French | 4.313 | 3.693 | 3.076 | 2.765 | 2.577 | 2.426 | 2.391 | 2.374 | 2.371 | 2.370 | 2.370 | 2.370 | 2.370 | 2.370 | 2.370 | 2.370 | 2.370 |
| German | 4.427 | 3.634 | 3.117 | 2.791 | 2.576 | 2.390 | 2.332 | 2.310 | 2.309 | 2.308 | 2.307 | 2.307 | 2.307 | 2.307 | 2.307 | 2.307 | 2.307 |
| Greek | 4.265 | 3.509 | 3.107 | 2.866 | 2.716 | 2.615 | 2.586 | 2.580 | 2.581 | 2.581 | 2.581 | 2.579 | 2.580 | 2.580 | 2.580 | 2.580 | 2.580 |
| Italian | 4.226 | 3.568 | 3.069 | 2.748 | 2.556 | 2.404 | 2.373 | 2.368 | 2.367 | 2.366 | 2.366 | 2.365 | 2.365 | 2.365 | 2.365 | 2.365 | 2.365 |
| Latin (Abbreviated) | 4.193 | 3.762 | 3.493 | 3.343 | 3.249 | 3.192 | 3.177 | 3.170 | 3.165 | 3.160 | 3.150 | 3.145 | 3.145 | 3.145 | 3.145 | 3.145 | 3.145 |
| Latin | 4.200 | 3.736 | 3.317 | 3.101 | 2.972 | 2.887 | 2.872 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 | 2.869 |
| Mayan (Kaqchikel) | 4.116 | 3.519 | 3.046 | 2.772 | 2.578 | 2.439 | 2.405 | 2.393 | 2.391 | 2.392 | 2.392 | 2.392 | 2.392 | 2.392 | 2.392 | 2.392 | 2.392 |
| Russian | 4.729 | 3.742 | 3.327 | 3.071 | 2.921 | 2.797 | 2.772 | 2.764 | 2.764 | 2.763 | 2.763 | 2.763 | 2.763 | 2.763 | 2.763 | 2.763 | 2.763 |
| Sanskrit | 6.412 | 5.406 | 5.059 | 4.988 | 4.974 | 4.968 | 4.966 | 4.960 | 4.951 | 4.942 | 4.944 | 4.944 | 4.944 | 4.944 | 4.945 | 4.945 | 4.945 |
| Spanish | 4.287 | 3.491 | 3.107 | 2.813 | 2.625 | 2.470 | 2.432 | 2.420 | 2.418 | 2.417 | 2.417 | 2.417 | 2.417 | 2.417 | 2.417 | 2.417 | 2.417 |
| Chinese (Pinyin) | 4.779 | 3.106 | 2.539 | 2.289 | 2.177 | 2.080 | 2.053 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 | 2.045 |
| Hebrew | 4.248 | 3.861 | 3.411 | 3.165 | 3.050 | 2.985 | 2.979 | 2.978 | 2.977 | 2.976 | 2.975 | 2.974 | 2.975 | 2.975 | 2.975 | 2.975 | 2.975 |
| Maori | 3.639 | 2.813 | 2.566 | 2.301 | 2.132 | 1.962 | 1.901 | 1.879 | 1.877 | 1.877 | 1.876 | 1.876 | 1.876 | 1.876 | 1.876 | 1.876 | 1.876 |
| Swahili | 4.161 | 3.332 | 3.073 | 2.807 | 2.622 | 2.447 | 2.400 | 2.382 | 2.381 | 2.380 | 2.379 | 2.377 | 2.378 | 2.378 | 2.378 | 2.378 | 2.378 |
| Tagalog | 3.900 | 3.157 | 2.792 | 2.530 | 2.319 | 2.089 | 2.018 | 1.980 | 1.978 | 1.977 | 1.977 | 1.977 | 1.977 | 1.977 | 1.977 | 1.977 | 1.977 |
| Turkish | 4.560 | 3.834 | 3.314 | 2.947 | 2.744 | 2.581 | 2.548 | 2.539 | 2.538 | 2.538 | 2.538 | 2.538 | 2.538 | 2.538 | 2.538 | 2.538 | 2.538 |
| Latin, segni rimescolati | 4.160 | 4.126 | 4.099 | 4.099 | 4.088 | 4.074 | 4.070 | 4.063 | 4.054 | 4.037 | 4.039 | 3.996 | 3.992 | 3.992 | 3.992 | 3.992 | 3.992 |
| C1 catena di Markov di ordine 3 (controllo negativo) | 4.181 | 3.697 | 3.238 | 3.000 | 2.985 | 2.989 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 | 2.991 |
| C2 latino con ogni riga ripetuta sotto (controllo positivo) | 4.237 | 3.805 | 3.404 | 3.236 | 3.138 | 3.084 | 3.075 | 3.073 | 3.073 | 3.072 | 3.071 | 3.071 | 3.071 | 3.071 | 3.071 | 3.071 | 3.071 |
| C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni) | 4.225 | 3.811 | 3.406 | 3.217 | 3.113 | 3.063 | 3.051 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 | 3.050 |
| C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo) | 4.190 | 3.726 | 3.340 | 3.119 | 2.894 | 2.819 | 2.799 | 2.795 | 2.795 | 2.795 | 2.794 | 2.792 | 2.793 | 2.793 | 2.793 | 2.793 | 2.793 |

## Posizione rispetto alle lingue (A)

- k90, Voynich: 2.000, sotto l'intervallo delle lingue [2.100, 6.000], lingue sotto: 0%
- k90, Voynich A: 2.100, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 0%
- k90, Voynich B: 2.000, sotto l'intervallo delle lingue [2.100, 6.000], lingue sotto: 0%
- k90, Voynich, segni rimescolati: 6.000, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 80%
- k90, Timm e Schinner (seme 1): 2.300, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 5%
- k90, Voynichizzatore v21 (libro d'esempio): 2.000, sotto l'intervallo delle lingue [2.100, 6.000], lingue sotto: 0%
- k90, Naibbe: 2.000, sotto l'intervallo delle lingue [2.100, 6.000], lingue sotto: 0%
- k90, Gibberish (Gaskell e Bowern): 12.300, sopra l'intervallo delle lingue [2.100, 6.000], lingue sotto: 100%
- k90, C1 catena di Markov di ordine 3 (controllo negativo): 3.000, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 5%
- k90, C2 latino con ogni riga ripetuta sotto (controllo positivo): 4.200, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 30%
- k90, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 4.000, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 10%
- k90, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 4.000, dentro l'intervallo delle lingue [2.100, 6.000], lingue sotto: 10%
- k90_interpolato, Voynich: 1.761, sotto l'intervallo delle lingue [1.907, 5.303], lingue sotto: 0%
- k90_interpolato, Voynich A: 1.853, sotto l'intervallo delle lingue [1.907, 5.303], lingue sotto: 0%
- k90_interpolato, Voynich B: 1.669, sotto l'intervallo delle lingue [1.907, 5.303], lingue sotto: 0%
- k90_interpolato, Voynich, segni rimescolati: 5.777, sopra l'intervallo delle lingue [1.907, 5.303], lingue sotto: 100%
- k90_interpolato, Timm e Schinner (seme 1): 1.985, dentro l'intervallo delle lingue [1.907, 5.303], lingue sotto: 5%
- k90_interpolato, Voynichizzatore v21 (libro d'esempio): 1.589, sotto l'intervallo delle lingue [1.907, 5.303], lingue sotto: 0%
- k90_interpolato, Naibbe: 1.736, sotto l'intervallo delle lingue [1.907, 5.303], lingue sotto: 0%
- k90_interpolato, Gibberish (Gaskell e Bowern): 10.801, sopra l'intervallo delle lingue [1.907, 5.303], lingue sotto: 100%
- k90_interpolato, C1 catena di Markov di ordine 3 (controllo negativo): 2.537, dentro l'intervallo delle lingue [1.907, 5.303], lingue sotto: 5%
- k90_interpolato, C2 latino con ogni riga ripetuta sotto (controllo positivo): 3.499, dentro l'intervallo delle lingue [1.907, 5.303], lingue sotto: 10%
- k90_interpolato, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 3.467, dentro l'intervallo delle lingue [1.907, 5.303], lingue sotto: 10%
- k90_interpolato, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 3.827, dentro l'intervallo delle lingue [1.907, 5.303], lingue sotto: 35%
- GL, Voynich: 0.009, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Voynich A: 0.010, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Voynich B: 0.013, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Voynich, segni rimescolati: 0.006, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Timm e Schinner (seme 1): 0.012, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Voynichizzatore v21 (libro d'esempio): 0.003, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 95%
- GL, Naibbe: 0.000, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 25%
- GL, Gibberish (Gaskell e Bowern): 0.017, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, Latin, segni rimescolati: 0.047, sopra l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 100%
- GL, C1 catena di Markov di ordine 3 (controllo negativo): -0.000, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 20%
- GL, C2 latino con ogni riga ripetuta sotto (controllo positivo): 0.000, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 80%
- GL, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): -0.000, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 20%
- GL, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.002, dentro l'intervallo delle lingue [-0.001, 0.005], lingue sotto: 95%
- GR, Voynich: 0.014, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 80%
- GR, Voynich A: 0.015, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 85%
- GR, Voynich B: 0.006, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 55%
- GR, Voynich, segni rimescolati: -0.001, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 20%
- GR, Timm e Schinner (seme 1): 0.013, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 75%
- GR, Voynichizzatore v21 (libro d'esempio): 0.004, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 40%
- GR, Naibbe: 0.003, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 40%
- GR, Gibberish (Gaskell e Bowern): 0.034, sopra l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 100%
- GR, Latin, segni rimescolati: 0.006, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 55%
- GR, C1 catena di Markov di ordine 3 (controllo negativo): -0.001, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 20%
- GR, C2 latino con ogni riga ripetuta sotto (controllo positivo): -0.002, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 15%
- GR, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): -0.003, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 5%
- GR, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.127, sopra l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 100%
- GR_corte, Voynich: 0.014, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 80%
- GR_corte, Voynich A: 0.016, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 85%
- GR_corte, Voynich B: 0.006, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 55%
- GR_corte, Voynich, segni rimescolati: -0.001, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 20%
- GR_corte, Timm e Schinner (seme 1): 0.013, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 75%
- GR_corte, Voynichizzatore v21 (libro d'esempio): 0.004, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 40%
- GR_corte, Naibbe: 0.003, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 40%
- GR_corte, Gibberish (Gaskell e Bowern): 0.035, sopra l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 100%
- GR_corte, Latin, segni rimescolati: 0.006, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 55%
- GR_corte, C1 catena di Markov di ordine 3 (controllo negativo): -0.002, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 10%
- GR_corte, C2 latino con ogni riga ripetuta sotto (controllo positivo): -0.002, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 15%
- GR_corte, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): -0.003, dentro l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 5%
- GR_corte, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.127, sopra l'intervallo delle lingue [-0.005, 0.028], lingue sotto: 100%
- G255, Voynich: 0.502, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 95%
- G255, Voynich A: 0.460, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 75%
- G255, Voynich B: 0.527, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 95%
- G255, Voynich, segni rimescolati: 0.048, sotto l'intervallo delle lingue [0.208, 0.562], lingue sotto: 0%
- G255, Timm e Schinner (seme 1): 0.422, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 50%
- G255, Voynichizzatore v21 (libro d'esempio): 0.463, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 80%
- G255, Naibbe: 0.494, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 95%
- G255, Gibberish (Gaskell e Bowern): 0.100, sotto l'intervallo delle lingue [0.208, 0.562], lingue sotto: 0%
- G255, Latin, segni rimescolati: 0.034, sotto l'intervallo delle lingue [0.208, 0.562], lingue sotto: 0%
- G255, C1 catena di Markov di ordine 3 (controllo negativo): 0.275, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 10%
- G255, C2 latino con ogni riga ripetuta sotto (controllo positivo): 0.260, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 10%
- G255, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 0.264, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 10%
- G255, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 0.320, dentro l'intervallo delle lingue [0.208, 0.562], lingue sotto: 25%
- bpc255, Voynich: 1.961, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 5%
- bpc255, Voynich A: 2.139, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 15%
- bpc255, Voynich B: 1.851, sotto l'intervallo delle lingue [1.876, 4.945], lingue sotto: 0%
- bpc255, Voynich, segni rimescolati: 3.763, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 95%
- bpc255, Timm e Schinner (seme 1): 2.196, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 15%
- bpc255, Voynichizzatore v21 (libro d'esempio): 2.122, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 15%
- bpc255, Naibbe: 2.003, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 10%
- bpc255, Gibberish (Gaskell e Bowern): 3.996, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 95%
- bpc255, Latin, segni rimescolati: 3.992, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 95%
- bpc255, C1 catena di Markov di ordine 3 (controllo negativo): 2.991, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 85%
- bpc255, C2 latino con ogni riga ripetuta sotto (controllo positivo): 3.071, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 85%
- bpc255, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 3.050, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 85%
- bpc255, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 2.793, dentro l'intervallo delle lingue [1.876, 4.945], lingue sotto: 75%
- guadagno_totale, Voynich: 2.057, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 90%
- guadagno_totale, Voynich A: 1.897, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 65%
- guadagno_totale, Voynich B: 2.130, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 95%
- guadagno_totale, Voynich, segni rimescolati: 0.223, sotto l'intervallo delle lingue [1.049, 2.734], lingue sotto: 0%
- guadagno_totale, Timm e Schinner (seme 1): 1.663, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 25%
- guadagno_totale, Voynichizzatore v21 (libro d'esempio): 1.891, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 65%
- guadagno_totale, Naibbe: 2.032, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 90%
- guadagno_totale, Gibberish (Gaskell e Bowern): 0.486, sotto l'intervallo delle lingue [1.049, 2.734], lingue sotto: 0%
- guadagno_totale, Latin, segni rimescolati: 0.168, sotto l'intervallo delle lingue [1.049, 2.734], lingue sotto: 0%
- guadagno_totale, C1 catena di Markov di ordine 3 (controllo negativo): 1.190, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 5%
- guadagno_totale, C2 latino con ogni riga ripetuta sotto (controllo positivo): 1.165, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 5%
- guadagno_totale, C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): 1.174, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 5%
- guadagno_totale, C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): 1.398, dentro l'intervallo delle lingue [1.049, 2.734], lingue sotto: 15%

## Voynich lingua A meno lingua B (differenza di medie) (A)

- k90_interpolato: +0.184 (errore standard 0.056, non appaiato, 10 e 10 semi)
- GL: -0.004 (errore standard 0.003, non appaiato, 10 e 10 semi)
- GR_corte: +0.009 (errore standard 0.003, non appaiato, 10 e 10 semi)

## Pagine di solo testo (GR sui bersagli corti, bit per segno) (A)

- Voynich: GR sulle pagine usabili 0.008 (ds 0.005, 10 semi); GR sulla prova 0.014
  - f66r: 6 semi, 9660 segni, GR -0.003
  - f76r: 8 semi, 22096 segni, GR 0.014
  - f85r1: 5 semi, 9380 segni, GR 0.002
  - f86v6: 8 semi, 20992 segni, GR 0.003
  - f1r: 4 semi, 3832 segni, GR 0.043
  - f86v5: 6 semi, 12102 segni, GR 0.006

## Testi più vicini al Voynich sul profilo (k90 interpolato, GL, GR corte) (A)

Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea.

- Voynich: Timm e Schinner (seme 1) (generatore) 2.68; Latin (Abbreviated) (lingua) 5.55; Voynichizzatore v21 (libro d'esempio) (generatore) 5.57; Voynich, segni rimescolati (controllo) 6.17; Greek (lingua) 7.78; English (lingua) 8.15
- Voynich A: Timm e Schinner (seme 1) (generatore) 2.44; Latin (Abbreviated) (lingua) 5.72; Voynichizzatore v21 (libro d'esempio) (generatore) 5.86; Voynich, segni rimescolati (controllo) 6.22; Greek (lingua) 8.00; English (lingua) 8.33
- Voynich B: Timm e Schinner (seme 1) (generatore) 1.19; Voynich, segni rimescolati (controllo) 8.25; Latin (Abbreviated) (lingua) 8.26; Voynichizzatore v21 (libro d'esempio) (generatore) 9.00; Greek (lingua) 11.13; English (lingua) 11.48

## Generatori e controlli rispetto al Voynich (A)

"vicino": differenza al massimo un decimo dell'intervallo delle lingue (almeno 0.02 per GL e GR).

- Voynich, segni rimescolati: k90_interpolato +4.016, GL -0.003 (vicino), GR_corte -0.015 (vicino)
- Timm e Schinner (seme 1): k90_interpolato +0.224 (vicino), GL +0.003 (vicino), GR_corte -0.001 (vicino)
- Voynichizzatore v21 (libro d'esempio): k90_interpolato -0.172 (vicino), GL -0.006 (vicino), GR_corte -0.010 (vicino)
- Naibbe: k90_interpolato -0.024 (vicino), GL -0.009 (vicino), GR_corte -0.011 (vicino)
- Gibberish (Gaskell e Bowern): k90_interpolato +9.040, GL +0.008 (vicino), GR_corte +0.021
- Latin, segni rimescolati: GL +0.037, GR_corte -0.008 (vicino)
- C1 catena di Markov di ordine 3 (controllo negativo): k90_interpolato +0.776, GL -0.009 (vicino), GR_corte -0.016 (vicino)
- C2 latino con ogni riga ripetuta sotto (controllo positivo): k90_interpolato +1.738, GL -0.009 (vicino), GR_corte -0.015 (vicino)
- C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni): k90_interpolato +1.707, GL -0.009 (vicino), GR_corte -0.017 (vicino)
- C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo): k90_interpolato +2.067, GL -0.008 (vicino), GR_corte +0.113

## Letture (criteri della preregistrazione) (A)

- Voynich: {'GL_oltre_zero': False, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- Voynich A: {'GL_oltre_zero': False, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- Voynich B: {'GL_oltre_zero': False, 'GR_azzerata': True, 'k90_definito': True, 'semi_con_k90_non_definito': 0, 'semi': 10}
- A_contro_B: OrderedDict({'k90_interpolato': {'differiscono': True, 'A_meno_B': 0.1842143100381981}, 'GL': {'differiscono': False, 'A_meno_B': -0.0037640000000000104}, 'GR_corte': {'differiscono': False, 'A_meno_B': 0.009499727252720523}})
- pagine_di_solo_testo: {'differenza': -0.0059714539639302965, 'piu_alta': False}
