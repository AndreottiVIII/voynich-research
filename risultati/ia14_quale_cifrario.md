# ia14 - quale procedimento produce le firme del Voynich

Non e' una decifrazione: si confrontano procedimenti. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia14.md`.

## Controlli

- riproduzione_rete: eseguito True, superato True
- riproduzione_sintassi: eseguito True, superato True
- latino_in_chiaro_tra_le_lingue: eseguito True, superato False
- separazione: eseguito True, superato True
- negativo_rimescolato: eseguito True, superato True
- codice dei procedimenti: verboso_reversibile True, sostituzione_reversibile True, polialfabetico_reversibile True, modulo_senza_caricatori_del_voynich True, superato True
- letture leggibili: False (riproduzione True, lingue False, separazione True, negativo True, codice True)

## Riferimenti (letti da risultati/ia02, ia03, ia09, ia10)

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

Raggio epsilon 0.46 (A dal Voynich 0.46, B 0.36, A contro B 0.68, rumore del Voynich da se' 0.46).

## Celle: distanza dal Voynich (in unita' di scala) e firme raggiunte

| cella | procedimento | d | classe | stabile | firme | larghe | mancate |
|---|---|---|---|---|---|---|---|
| V_1 | verboso omofonico a bigrammi | 3.52 | lontano | True | 1/9 | 3/9 | k90,GL,R_rel,Q,rho,lambda,E,g |
| V_3 | verboso omofonico a bigrammi | 2.72 | lontano | True | 1/9 | 4/9 | k90,GL,GR,Q,rho,lambda,E,g |
| V_6 | verboso omofonico a bigrammi | 2.36 | lontano | True | 1/9 | 6/9 | k90,GL,GR,R_rel,Q,rho,lambda,E |
| V_3_italiano | verboso omofonico a bigrammi | 2.88 | lontano | True | 1/9 | 3/9 | k90,GL,GR,Q,rho,lambda,E,g |
| V_3_tedesco | verboso omofonico a bigrammi | 2.52 | lontano | True | 3/9 | 4/9 | k90,GL,rho,lambda,E,g |
| S_1 | sillabario con omofoni | 3.73 | lontano | True | 1/9 | 3/9 | k90,GL,R_rel,Q,rho,lambda,E,g |
| S_2 | sillabario con omofoni | 3.52 | lontano | True | 1/9 | 3/9 | k90,GR,R_rel,Q,rho,lambda,E,g |
| S_4 | sillabario con omofoni | 3.59 | lontano | True | 0/9 | 3/9 | k90,GL,GR,R_rel,Q,rho,lambda,E,g |
| N_30 | nomenclatore | 3.30 | lontano | True | 2/9 | 4/9 | k90,GR,R_rel,Q,rho,lambda,E |
| N_150 | nomenclatore | 3.40 | lontano | True | 2/9 | 4/9 | k90,GR,R_rel,Q,rho,lambda,E |
| N_600 | nomenclatore | 3.70 | lontano | True | 1/9 | 4/9 | k90,GR,R_rel,Q,rho,lambda,E,g |
| C_4 | auto-citazione | 84.01 | lontano | True | 0/9 | 4/9 | k90,GL,GR,R_rel,Q,rho,lambda,E,g |
| C_16 | auto-citazione | 72.54 | lontano | True | 1/9 | 4/9 | k90,GL,GR,R_rel,Q,rho,E,g |
| C_64 | auto-citazione | 67.68 | lontano | True | 1/9 | 4/9 | k90,GL,GR,R_rel,Q,rho,E,g |
| R_6 | tabella a griglia | 6.67 | lontano | True | 0/9 | 2/9 | k90,GL,GR,Q,rho,lambda,E,g |
| R_12 | tabella a griglia | 9.00 | lontano | True | 0/9 | 1/9 | k90,GL,GR,Q,rho,lambda,E,g |
| R_24 | tabella a griglia | 13.48 | lontano | True | 0/9 | 0/9 | k90,GL,GR,R_rel,Q,rho,lambda,E,g |
| F_3p5 | sostituzione con spazi riscritti | 2.48 | lontano | True | 3/9 | 5/9 | k90,GL,GR,rho,lambda,E |
| F_5p0 | sostituzione con spazi riscritti | 3.09 | lontano | True | 1/9 | 4/9 | k90,GL,R_rel,Q,rho,lambda,E,g |
| F_7p0 | sostituzione con spazi riscritti | 3.54 | lontano | True | 2/9 | 4/9 | k90,R_rel,Q,rho,lambda,E,g |
| P_1 | polialfabetico a cambio periodico | 3.75 | lontano | True | 2/9 | 4/9 | k90,GR,Q,rho,lambda,E,g |
| P_5 | polialfabetico a cambio periodico | 3.71 | lontano | True | 2/9 | 4/9 | k90,GR,Q,rho,lambda,E,g |
| P_25 | polialfabetico a cambio periodico | 3.64 | lontano | True | 2/9 | 4/9 | k90,GR,Q,rho,lambda,E,g |
| T0 | latino in chiaro | 3.57 | lontano | True | 4/9 | 4/9 | k90,R_rel,Q,rho,lambda |

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
| nat_naibbe | 1.722 | -0.000 | 0.003 | 0.993 | 0.087 | 0.500 | 0.000 | 0.002 | 0.088 | 2.05 | lontano |
| nat_ts | 5.515 | 0.115 | 0.046 | 0.999 | 0.068 | 0.979 | -0.025 | 0.814 | 0.006 | 4.18 | lontano |
| nat_latino | 4.379 | 0.042 | 0.010 | 1.166 | 0.005 | 0.387 | 0.075 | 0.337 | 0.020 | 3.52 | lontano |

## Letture

- V (verboso omofonico a bigrammi): distanza minima 2.36 (V_6), massima 3.52, classi lontano/lontano/lontano, firme al massimo 1/9
- S (sillabario con omofoni): distanza minima 3.52 (S_2), massima 3.73, classi lontano/lontano/lontano, firme al massimo 1/9
- N (nomenclatore): distanza minima 3.30 (N_30), massima 3.70, classi lontano/lontano/lontano, firme al massimo 2/9
- C (auto-citazione): distanza minima 67.68 (C_64), massima 84.01, classi lontano/lontano/lontano, firme al massimo 1/9
- R (tabella a griglia): distanza minima 6.67 (R_6), massima 13.48, classi lontano/lontano/lontano, firme al massimo 0/9
- F (sostituzione con spazi riscritti): distanza minima 2.48 (F_3p5), massima 3.54, classi lontano/lontano/lontano, firme al massimo 3/9
- P (polialfabetico a cambio periodico): distanza minima 3.64 (P_25), massima 3.75, classi lontano/lontano/lontano, firme al massimo 2/9

- firma k90: raggiunta da 0 celle su 23 (nessun procedimento)
- firma GL: raggiunta da 9 celle su 23 (F,N,P,S)
- firma GR: raggiunta da 6 celle su 23 (F,S,V)
- firma R_rel: raggiunta da 7 celle su 23 (F,P,V)
- firma Q: raggiunta da 2 celle su 23 (F,V)
- firma rho: raggiunta da 0 celle su 23 (nessun procedimento)
- firma lambda: raggiunta da 2 celle su 23 (C)
- firma E: raggiunta da 1 celle su 23 (nessun procedimento)
- firma g: raggiunta da 5 celle su 23 (F,N,V)
