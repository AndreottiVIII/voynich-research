# ia19 - procedimenti combinati e le firme del Voynich

Non e' una decifrazione: si confrontano procedimenti. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia19.md`.

## Controlli

- riproduzione_rete: eseguito True, superato True
- riproduzione_sintassi: eseguito True, superato True
- latino_in_chiaro_corretto: eseguito True, superato True
- separazione_in_lettura: eseguito True, superato True
- negativo_rimescolato: eseguito True, superato True
- eco_misurabile: eseguito True, superato True
- scala_coerente_con_ia14: eseguito True, superato True
- latino in chiaro, misure leggibili: k90, GR, R_rel, Q, rho, lambda, E, g; non leggibili: GL
- codice (ia14): verboso_reversibile True, sostituzione_reversibile True, polialfabetico_reversibile True, modulo_senza_caricatori_del_voynich True, superato True
- codice (ia19): VE_senza_eco_identico_al_verboso_di_ia14 True, deterministico True, istanze_diverse True, decifrabile_tolte_le_nulle True, parole_nulle_e_numero_giusto True, quota_eco_giusta True, scarto_quota_eco_massimo 0.0025666818093322066, modulo_senza_caricatori_del_voynich True, superato True
- letture leggibili: True (riproduzione True, latino_in_chiaro True, separazione True, negativo True, codice True, scala True); controllo dell'eco True

## Riferimenti e misure in lettura (k90, GR, R_rel, Q, rho, lambda, E, g)

| misura | Voynich | A | B | sd Voynich | scala | tolleranza |
|---|---|---|---|---|---|---|
| k90 (segni di contesto, interpolato) | 2.005 | 2.063 | 1.819 | 0.158 | 8.814 | 0.317 |
| GL (guadagno lungo, bit per segno) | 0.049 | 0.033 | 0.042 | 0.013 | 0.035 | 0.025 |
| GR (riga sopra, parole corte, bit) | 0.029 | 0.027 | 0.014 | 0.006 | 0.020 | 0.015 |
| R_rel (mai viste / viste) | 0.997 | 1.000 | 0.972 | 0.031 | 0.166 | 0.061 |
| Q (inventate vere) | 0.081 | 0.081 | 0.078 | 0.009 | 0.009 | 0.017 |
| rho (quota di copia) | 0.700 | 0.872 | 0.622 | 0.019 | 0.145 | 0.173 |
| Lambda (quota locale) | 0.272 | - | - | 0.039 | 0.050 | 0.079 |
| E (eco netta, bit per parola) | 0.105 | 0.117 | 0.100 | 0.007 | 0.067 | 0.015 |
| g (ordine fra famiglie, bit per coppia) | 0.041 | 0.018 | 0.078 | 0.006 | 0.310 | 0.037 |

Raggio epsilon 0.47 (A dal Voynich 0.46, B 0.38, A contro B 0.72, rumore del Voynich da se' 0.47).

## Celle: distanza dal Voynich (unita' di scala) e firme raggiunte (su 8 misure in lettura)

| cella | tipo | d | classe | stabile | firme | larghe | mancate |
|---|---|---|---|---|---|---|---|
| V_1 | verboso omofonico a bigrammi (ia14) | 3.70 | lontano | True | 1/8 | 2/8 | k90,R_rel,Q,rho,lambda,E,g |
| V_3 | verboso omofonico a bigrammi (ia14) | 2.85 | lontano | True | 1/8 | 3/8 | k90,GR,Q,rho,lambda,E,g |
| V_6 | verboso omofonico a bigrammi (ia14) | 2.45 | lontano | True | 1/8 | 5/8 | k90,GR,R_rel,Q,rho,lambda,E |
| V_3_italiano | verboso omofonico a bigrammi (ia14) | 3.02 | lontano | True | 1/8 | 2/8 | k90,GR,Q,rho,lambda,E,g |
| V_3_tedesco | verboso omofonico a bigrammi (ia14) | 2.64 | lontano | True | 3/8 | 3/8 | k90,rho,lambda,E,g |
| S_1 | sillabario con omofoni (ia14) | 3.95 | lontano | True | 1/8 | 2/8 | k90,R_rel,Q,rho,lambda,E,g |
| S_2 | sillabario con omofoni (ia14) | 3.73 | lontano | True | 0/8 | 2/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| S_4 | sillabario con omofoni (ia14) | 3.79 | lontano | True | 0/8 | 2/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| N_30 | nomenclatore (ia14) | 3.49 | lontano | True | 1/8 | 3/8 | k90,GR,R_rel,Q,rho,lambda,E |
| N_150 | nomenclatore (ia14) | 3.60 | lontano | True | 1/8 | 3/8 | k90,GR,R_rel,Q,rho,lambda,E |
| N_600 | nomenclatore (ia14) | 3.92 | lontano | True | 0/8 | 3/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| C_4 | auto-citazione (ia14) | 89.09 | lontano | True | 0/8 | 4/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| C_16 | auto-citazione (ia14) | 76.50 | lontano | True | 1/8 | 4/8 | k90,GR,R_rel,Q,rho,E,g |
| C_64 | auto-citazione (ia14) | 71.39 | lontano | True | 1/8 | 4/8 | k90,GR,R_rel,Q,rho,E,g |
| R_6 | tabella a griglia (ia14) | 7.11 | lontano | True | 0/8 | 1/8 | k90,GR,Q,rho,lambda,E,g |
| R_12 | tabella a griglia (ia14) | 9.61 | lontano | True | 0/8 | 0/8 | k90,GR,Q,rho,lambda,E,g |
| R_24 | tabella a griglia (ia14) | 14.20 | lontano | True | 0/8 | 0/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| F_3p5 | sostituzione con spazi riscritti (ia14) | 2.60 | lontano | True | 3/8 | 4/8 | k90,GR,rho,lambda,E |
| F_5p0 | sostituzione con spazi riscritti (ia14) | 3.26 | lontano | True | 1/8 | 3/8 | k90,R_rel,Q,rho,lambda,E,g |
| F_7p0 | sostituzione con spazi riscritti (ia14) | 3.74 | lontano | True | 1/8 | 3/8 | k90,R_rel,Q,rho,lambda,E,g |
| P_1 | polialfabetico a cambio periodico (ia14) | 3.98 | lontano | True | 1/8 | 3/8 | k90,GR,Q,rho,lambda,E,g |
| P_5 | polialfabetico a cambio periodico (ia14) | 3.94 | lontano | True | 1/8 | 3/8 | k90,GR,Q,rho,lambda,E,g |
| P_25 | polialfabetico a cambio periodico (ia14) | 3.86 | lontano | True | 1/8 | 3/8 | k90,GR,Q,rho,lambda,E,g |
| T0 | latino in chiaro | 3.78 | lontano | True | 3/8 | 3/8 | k90,R_rel,Q,rho,lambda |
| VE_0p02 | combinazione verboso + eco leggera di pagina | 2.41 | lontano | True | 1/8 | 4/8 | k90,GR,Q,rho,lambda,E,g |
| VE_0p05 | combinazione verboso + eco leggera di pagina | 2.07 | lontano | True | 3/8 | 4/8 | k90,Q,lambda,E,g |
| VE_0p1 | combinazione verboso + eco leggera di pagina | 2.21 | lontano | True | 1/8 | 5/8 | k90,GR,Q,rho,lambda,E,g |
| VE_0p05_T6 | combinazione verboso + eco leggera di pagina | 1.66 | lontano | True | 1/8 | 6/8 | k90,GR,R_rel,Q,rho,lambda,E |
| VA_8 | combinazione verboso con alfabeto ridotto | 3.09 | lontano | True | 0/8 | 1/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| VA_12 | combinazione verboso con alfabeto ridotto | 2.95 | lontano | True | 0/8 | 2/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| VA_16 | combinazione verboso con alfabeto ridotto | 2.86 | lontano | True | 0/8 | 3/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| NV_30 | combinazione nomenclatore + verboso | 3.12 | lontano | True | 1/8 | 2/8 | k90,R_rel,Q,rho,lambda,E,g |
| NV_150 | combinazione nomenclatore + verboso | 3.26 | lontano | True | 1/8 | 2/8 | k90,GR,Q,rho,lambda,E,g |
| NV_600 | combinazione nomenclatore + verboso | 3.29 | lontano | True | 1/8 | 2/8 | k90,GR,Q,rho,lambda,E,g |
| VB_0p5 | combinazione verboso con regole di bordo riga | 3.01 | lontano | True | 1/8 | 2/8 | k90,GR,Q,rho,lambda,E,g |
| VB_0p8 | combinazione verboso con regole di bordo riga | 3.15 | lontano | True | 0/8 | 2/8 | k90,GR,R_rel,Q,rho,lambda,E,g |
| VB_1p0 | combinazione verboso con regole di bordo riga | 3.28 | lontano | True | 1/8 | 2/8 | k90,R_rel,Q,rho,lambda,E,g |
| VT_2 | combinazione tutto insieme (ingredienti a gradini) | 2.30 | lontano | True | 1/8 | 3/8 | k90,GR,R_rel,Q,lambda,E,g |
| VT_3 | combinazione tutto insieme (ingredienti a gradini) | 2.70 | lontano | True | 1/8 | 2/8 | k90,GR,R_rel,Q,lambda,E,g |
| VT_4 | combinazione tutto insieme (ingredienti a gradini) | 3.01 | lontano | True | 1/8 | 3/8 | k90,GR,R_rel,Q,rho,lambda,g |

## Profilo medio delle celle (media sulle istanze; sd fra istanze fra parentesi)

| cella | k90 | GL | GR | R_rel | Q | rho | lambda | E | g |
|---|---|---|---|---|---|---|---|---|---|
| V_1 | 3.273 (0.308) | 0.001 (0.001) | 0.022 (0.003) | 0.911 (0.051) | 0.018 (0.006) | 0.000 (0.001) | 0.000 (0.000) | 0.001 (0.000) | 0.372 (0.003) |
| V_3 | 3.679 (0.070) | 0.005 (0.000) | 0.009 (0.000) | 1.048 (0.020) | 0.055 (0.006) | 0.004 (0.006) | 0.000 (0.000) | 0.001 (0.001) | 0.192 (0.009) |
| V_6 | 3.876 (0.057) | 0.003 (0.006) | 0.005 (0.003) | 1.081 (0.018) | 0.050 (0.006) | 0.500 (0.000) | 0.000 (0.000) | 0.004 (0.001) | 0.063 (0.010) |
| V_3_italiano | 3.722 (0.091) | 0.005 (0.003) | 0.011 (0.003) | 1.013 (0.008) | 0.045 (0.009) | 0.019 (0.012) | 0.000 (0.000) | 0.004 (0.002) | 0.244 (0.018) |
| V_3_tedesco | 3.765 (0.090) | 0.006 (0.004) | 0.018 (0.008) | 1.045 (0.025) | 0.075 (0.005) | 0.015 (0.010) | 0.000 (0.000) | 0.003 (0.001) | 0.291 (0.013) |
| S_1 | 5.913 (0.335) | 0.076 (0.023) | 0.023 (0.009) | 1.584 (0.022) | 0.004 (0.001) | 0.192 (0.041) | 0.133 (0.034) | 0.303 (0.040) | 0.589 (0.007) |
| S_2 | 5.192 (0.222) | 0.030 (0.007) | 0.008 (0.003) | 1.291 (0.030) | 0.004 (0.001) | 0.201 (0.032) | 0.089 (0.057) | 0.086 (0.013) | 0.411 (0.028) |
| S_4 | 4.232 (0.194) | 0.018 (0.006) | -0.001 (0.008) | 1.102 (0.025) | 0.003 (0.001) | 0.471 (0.045) | 0.015 (0.058) | 0.028 (0.007) | 0.196 (0.037) |
| N_30 | 4.468 (0.612) | 0.031 (0.023) | 0.001 (0.002) | 1.258 (0.024) | 0.005 (0.000) | 0.320 (0.278) | 0.132 (0.066) | 0.139 (0.017) | 0.055 (0.027) |
| N_150 | 4.790 (0.850) | 0.046 (0.032) | 0.008 (0.007) | 1.225 (0.029) | 0.004 (0.001) | 0.405 (0.121) | 0.069 (0.023) | 0.172 (0.036) | 0.070 (0.012) |
| N_600 | 4.349 (0.099) | 0.027 (0.007) | 0.002 (0.006) | 1.138 (0.021) | 0.005 (0.001) | 0.275 (0.052) | -0.019 (0.096) | 0.123 (0.026) | 0.084 (0.028) |
| C_4 | 34.700 (3.550) | 0.224 (0.056) | 0.583 (0.034) | 0.933 (0.009) | 0.016 (0.007) | 1.000 (0.000) | 0.391 (0.006) | 16.894 (0.339) | 0.003 (0.003) |
| C_16 | 99.703 (14.244) | 0.867 (0.120) | 0.609 (0.048) | 0.936 (0.015) | 0.016 (0.005) | 1.000 (0.000) | 0.326 (0.005) | 14.460 (0.521) | 0.000 (0.004) |
| C_64 | 183.456 (16.043) | 0.802 (0.130) | 0.384 (0.040) | 0.912 (0.007) | 0.013 (0.008) | 1.000 (0.000) | 0.256 (0.002) | 13.515 (0.425) | 0.001 (0.001) |
| R_6 | 3.410 (0.028) | 0.001 (0.000) | 0.045 (0.003) | - (0.000) | 0.000 (0.000) | 0.000 (0.000) | 0.943 (0.003) | 0.627 (0.009) | 0.470 (0.009) |
| R_12 | 5.913 (0.052) | 0.008 (0.002) | 0.096 (0.012) | - (0.000) | 0.000 (0.000) | 0.000 (0.000) | 0.798 (0.004) | 1.469 (0.005) | 0.163 (0.009) |
| R_24 | 26.268 (17.081) | 0.210 (0.074) | 0.130 (0.029) | 2.322 (0.872) | 0.000 (0.000) | 0.009 (0.000) | 0.575 (0.003) | 2.587 (0.005) | -0.227 (0.036) |
| F_3p5 | 3.761 (0.152) | 0.010 (0.003) | 0.046 (0.011) | 1.034 (0.012) | 0.066 (0.009) | 0.077 (0.034) | 0.000 (0.000) | 0.010 (0.003) | 0.011 (0.005) |
| F_5p0 | 4.274 (0.388) | 0.017 (0.006) | 0.032 (0.005) | 1.071 (0.009) | 0.029 (0.002) | 0.098 (0.028) | 0.000 (0.000) | 0.005 (0.001) | 0.005 (0.004) |
| F_7p0 | 5.201 (0.411) | 0.024 (0.007) | 0.037 (0.006) | 1.126 (0.085) | 0.005 (0.001) | 0.500 (0.000) | 0.000 (0.000) | 0.005 (0.001) | -0.000 (0.000) |
| P_1 | 22.859 (0.770) | 0.034 (0.007) | 0.137 (0.017) | 1.005 (0.001) | 0.015 (0.002) | 0.500 (0.000) | 0.000 (0.000) | 0.002 (0.001) | 0.002 (0.002) |
| P_5 | 34.651 (4.001) | 0.056 (0.007) | 0.103 (0.017) | 0.969 (0.024) | 0.013 (0.002) | 0.500 (0.000) | 0.000 (0.000) | 0.001 (0.001) | -0.000 (0.001) |
| P_25 | 30.028 (2.098) | 0.056 (0.010) | 0.108 (0.049) | 0.995 (0.017) | 0.014 (0.001) | 0.500 (0.000) | 0.000 (0.000) | 0.001 (0.001) | -0.002 (0.001) |
| T0 | 4.834 (0.679) | 0.025 (0.009) | 0.017 (0.005) | 1.251 (0.055) | 0.005 (0.001) | 0.277 (0.278) | 0.020 (0.075) | 0.115 (0.052) | 0.059 (0.031) |
| VE_0p02 | 3.626 (0.093) | 0.007 (0.001) | 0.009 (0.004) | 1.049 (0.031) | 0.049 (0.008) | 0.396 (0.029) | 0.530 (0.132) | 0.051 (0.006) | 0.178 (0.003) |
| VE_0p05 | 3.629 (0.091) | 0.007 (0.004) | 0.017 (0.005) | 1.058 (0.007) | 0.051 (0.007) | 0.698 (0.049) | 0.500 (0.021) | 0.142 (0.015) | 0.147 (0.013) |
| VE_0p1 | 3.595 (0.102) | 0.023 (0.010) | 0.011 (0.004) | 1.032 (0.018) | 0.055 (0.003) | 0.877 (0.023) | 0.480 (0.024) | 0.317 (0.014) | 0.109 (0.013) |
| VE_0p05_T6 | 3.949 (0.129) | 0.013 (0.006) | 0.009 (0.002) | 1.082 (0.027) | 0.049 (0.005) | 0.923 (0.024) | 0.373 (0.052) | 0.163 (0.011) | 0.047 (0.013) |
| VA_8 | 4.898 (0.159) | 0.002 (0.004) | 0.004 (0.003) | 1.219 (0.063) | 0.044 (0.013) | 0.009 (0.008) | 0.000 (0.000) | 0.001 (0.001) | 0.192 (0.010) |
| VA_12 | 4.871 (0.148) | 0.005 (0.002) | 0.009 (0.004) | 1.146 (0.023) | 0.049 (0.003) | 0.024 (0.007) | 0.000 (0.000) | 0.002 (0.001) | 0.179 (0.033) |
| VA_16 | 3.786 (0.037) | 0.003 (0.004) | 0.012 (0.006) | 1.068 (0.011) | 0.055 (0.004) | 0.011 (0.005) | 0.000 (0.000) | 0.001 (0.001) | 0.198 (0.008) |
| NV_30 | 3.625 (0.101) | 0.008 (0.005) | 0.019 (0.001) | 1.065 (0.014) | 0.039 (0.004) | 0.034 (0.037) | 0.000 (0.000) | 0.009 (0.012) | 0.249 (0.030) |
| NV_150 | 3.720 (0.120) | 0.011 (0.009) | 0.014 (0.005) | 1.049 (0.024) | 0.033 (0.005) | 0.028 (0.035) | 0.000 (0.000) | 0.011 (0.015) | 0.293 (0.031) |
| NV_600 | 3.580 (0.182) | 0.004 (0.004) | 0.014 (0.004) | 0.995 (0.022) | 0.031 (0.004) | 0.055 (0.055) | 0.000 (0.000) | 0.009 (0.005) | 0.260 (0.046) |
| VB_0p5 | 3.886 (0.033) | 0.007 (0.000) | 0.013 (0.006) | 1.048 (0.017) | 0.046 (0.006) | 0.010 (0.002) | 0.000 (0.000) | 0.001 (0.000) | 0.175 (0.010) |
| VB_0p8 | 4.026 (0.174) | 0.006 (0.003) | 0.007 (0.003) | 1.070 (0.031) | 0.040 (0.005) | 0.005 (0.007) | 0.000 (0.000) | 0.001 (0.001) | 0.168 (0.003) |
| VB_1p0 | 3.953 (0.035) | 0.009 (0.007) | 0.016 (0.000) | 1.070 (0.020) | 0.031 (0.003) | 0.045 (0.024) | 0.000 (0.000) | 0.008 (0.005) | 0.160 (0.007) |
| VT_2 | 4.552 (0.150) | 0.006 (0.001) | 0.008 (0.001) | 1.171 (0.058) | 0.045 (0.011) | 0.636 (0.028) | 0.509 (0.043) | 0.124 (0.003) | 0.147 (0.009) |
| VT_3 | 5.140 (0.130) | 0.015 (0.004) | 0.011 (0.003) | 1.237 (0.017) | 0.031 (0.004) | 0.555 (0.031) | 0.500 (0.030) | 0.137 (0.006) | 0.128 (0.016) |
| VT_4 | 4.834 (0.026) | 0.009 (0.006) | 0.014 (0.009) | 1.244 (0.021) | 0.028 (0.002) | 0.427 (0.027) | 0.540 (0.041) | 0.118 (0.003) | 0.181 (0.023) |

## Nativi, lingue e negativo

| testo | k90 | GL | GR | R_rel | Q | rho | lambda | E | g | d | classe |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Tneg_i1 | - | - | - | - | - | 0.500 | 0.000 | 0.004 | -0.000 | 2.91 | lontano |
| LG_latino | - | - | - | - | - | 0.272 | 0.042 | 0.131 | 0.091 | 2.74 | lontano |
| LG_latino_nt | - | - | - | - | - | 0.534 | 0.130 | 0.273 | 0.197 | 2.00 | lontano |
| LG_italiano | - | - | - | - | - | 0.118 | 0.133 | 0.225 | 0.676 | 2.79 | lontano |
| LG_inglese | - | - | - | - | - | 0.114 | 0.110 | 0.216 | 0.747 | 2.95 | lontano |
| LG_francese | - | - | - | - | - | 0.182 | 0.197 | 0.325 | 0.844 | 2.85 | lontano |
| LG_tedesco | - | - | - | - | - | 0.202 | 0.088 | 0.258 | 0.469 | 2.85 | lontano |
| LG_spagnolo | - | - | - | - | - | 0.193 | 0.116 | 0.294 | 0.775 | 2.97 | lontano |
| LG_maori | - | - | - | - | - | 0.067 | 0.185 | 0.154 | 0.941 | 2.78 | lontano |
| nat_naibbe | 1.722 | -0.000 | 0.003 | 0.993 | 0.087 | 0.500 | 0.000 | 0.002 | 0.088 | 2.12 | lontano |
| nat_ts | 5.515 | 0.115 | 0.046 | 0.999 | 0.068 | 0.979 | -0.025 | 0.814 | 0.006 | 4.39 | lontano |
| nat_latino | 4.379 | 0.042 | 0.010 | 1.166 | 0.005 | 0.387 | 0.075 | 0.337 | 0.020 | 3.73 | lontano |

## Letture

- VE (verboso + eco leggera di pagina): esito no (leggibile True); distanza minima 2.07 (VE_0p05), massima 2.41, classi lontano/lontano/lontano, firme al massimo 3
- VA (verboso con alfabeto ridotto): esito no (leggibile True); distanza minima 2.86 (VA_16), massima 3.09, classi lontano/lontano/lontano, firme al massimo 0
- NV (nomenclatore + verboso): esito no (leggibile True); distanza minima 3.12 (NV_30), massima 3.29, classi lontano/lontano/lontano, firme al massimo 1
- VB (verboso con regole di bordo riga): esito no (leggibile True); distanza minima 3.01 (VB_0p5), massima 3.28, classi lontano/lontano/lontano, firme al massimo 1
- VT (tutto insieme (ingredienti a gradini)): esito no (leggibile True); distanza minima 2.30 (VT_2), massima 3.01, classi lontano/lontano/lontano, firme al massimo 1

- firma k90: combinazioni 0/16 celle (-); semplici 0/23 (-)
- firma GL (fuori lettura): combinazioni 0/16 celle (-); semplici 8/23 (F,N,P,S)
- firma GR: combinazioni 3/16 celle (NV,VB,VE); semplici 5/23 (F,S,V)
- firma R_rel: combinazioni 6/16 celle (NV,VB,VE); semplici 7/23 (F,P,V)
- firma Q: combinazioni 0/16 celle (-); semplici 2/23 (F,V)
- firma rho: combinazioni 3/16 celle (VE,VT); semplici 0/23 (-) NUOVA
- firma lambda: combinazioni 0/16 celle (-); semplici 2/23 (C)
- firma E: combinazioni 1/16 celle (VT); semplici 0/23 (-) NUOVA
- firma g: combinazioni 1/16 celle (VE); semplici 4/23 (F,N,V)

- contro i semplici: combinata piu' vicina VE_0p05_T6 (1.66), semplice piu' vicino V_6 (2.45), migliore True

## Contributo degli ingredienti (differenza di distanza e misure che cambiano oltre 2 deviazioni standard)

- VE_0p02 contro V_3: differenza di distanza -0.45; cambiano: GL,rho,lambda,E
- VE_0p05 contro V_3: differenza di distanza -0.79; cambiano: Q,rho,lambda,E,g
- VE_0p1 contro V_3: differenza di distanza -0.64; cambiano: rho,lambda,E,g
- VE_0p05_T6 contro V_6: differenza di distanza -0.79; cambiano: rho,lambda,E,g
- VA_8 contro V_3: differenza di distanza 0.24; cambiano: k90,GR,R_rel
- VA_12 contro V_3: differenza di distanza 0.10; cambiano: k90,R_rel,rho,E
- VA_16 contro V_3: differenza di distanza 0.00; cambiano: -
- NV_30 contro N_30: differenza di distanza -0.37; cambiano: GR,R_rel,Q,lambda,E,g
- NV_150 contro N_150: differenza di distanza -0.34; cambiano: R_rel,Q,rho,lambda,E,g
- NV_600 contro N_600: differenza di distanza -0.63; cambiano: k90,GL,R_rel,Q,rho,E,g
- VB_0p5 contro V_3: differenza di distanza 0.16; cambiano: k90,GL
- VB_0p8 contro V_3: differenza di distanza 0.29; cambiano: Q,g
- VB_1p0 contro V_3: differenza di distanza 0.43; cambiano: k90,GR,Q,g
- VT_2 contro VE_0p05: differenza di distanza 0.24; cambiano: k90
- VT_3 contro VT_2: differenza di distanza 0.39; cambiano: k90,GL,rho,E
- VT_4 contro VT_3: differenza di distanza 0.32; cambiano: k90,rho,E,g
