# ia25 - le verifiche rapide

Non e' una decifrazione: si controlla quanto sono solide misure e letture gia' fatte. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia25.md`.

## Parte 1: copia netta con un riferimento di sezione

Domanda: quanta parte della "copia" (copia netta di ia09, rho, Λ) e' vocabolario di sezione, lingua e mano o fascicolo? Riferimenti: 0 = pagina a caso (come ia09); 1 = stessa sezione, lingua e mano; 2 = stessa sezione e fascicolo.

### V21

| rif | libri | copia netta | Λ | rho | contatto | quota di sezione | pagine con ripiego |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 0,055 ± 0,002 | 0,091 ± 0,018 | 0,592 ± 0,013 | 0,185 ± 0,001 | — | 0,00 ± 0,00 |
| 1 | 10 | 0,040 ± 0,001 | 0,126 ± 0,033 | 0,526 ± 0,013 | 0,185 ± 0,001 | 0,262 ± 0,013 | 0,02 ± 0,00 |
| 2 | 10 | 0,045 ± 0,001 | 0,149 ± 0,029 | 0,549 ± 0,013 | 0,185 ± 0,001 | 0,186 ± 0,013 | 0,02 ± 0,00 |

### vere

| rif | libri | copia netta | Λ | rho | contatto | quota di sezione | pagine con ripiego |
|---|---|---|---|---|---|---|---|
| 0 | 1 | 0,114 ± — | 0,207 ± — | 0,730 ± — | 0,188 ± — | — | 0,00 ± — |
| 1 | 1 | 0,097 ± — | 0,261 ± — | 0,697 ± — | 0,188 ± — | 0,151 ± — | 0,02 ± — |
| 2 | 1 | 0,099 ± — | 0,248 ± — | 0,701 ± — | 0,188 ± — | 0,128 ± — | 0,02 ± — |

### M1

| rif | libri | copia netta | Λ | rho | contatto | quota di sezione | pagine con ripiego |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 0,036 ± 0,002 | 0,054 ± 0,037 | 0,515 ± 0,015 | 0,189 ± 0,002 | — | 0,00 ± 0,00 |
| 1 | 10 | 0,026 ± 0,001 | 0,029 ± 0,046 | 0,415 ± 0,017 | 0,189 ± 0,002 | 0,285 ± 0,022 | 0,02 ± 0,00 |
| 2 | 10 | 0,026 ± 0,002 | 0,052 ± 0,071 | 0,412 ± 0,020 | 0,189 ± 0,002 | 0,293 ± 0,026 | 0,02 ± 0,00 |

### M5

| rif | libri | copia netta | Λ | rho | contatto | quota di sezione | pagine con ripiego |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 0,142 ± 0,006 | 0,236 ± 0,011 | 0,905 ± 0,007 | 0,158 ± 0,001 | — | 0,00 ± 0,00 |
| 1 | 10 | 0,132 ± 0,006 | 0,260 ± 0,021 | 0,898 ± 0,008 | 0,158 ± 0,001 | 0,067 ± 0,008 | 0,02 ± 0,00 |
| 2 | 10 | 0,130 ± 0,006 | 0,237 ± 0,018 | 0,896 ± 0,008 | 0,158 ± 0,001 | 0,084 ± 0,010 | 0,02 ± 0,00 |

### E2

| rif | libri | copia netta | Λ | rho | contatto | quota di sezione | pagine con ripiego |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 0,113 ± 0,008 | 0,360 ± 0,015 | 0,808 ± 0,011 | 0,180 ± 0,008 | — | 0,00 ± 0,00 |
| 1 | 10 | 0,097 ± 0,006 | 0,442 ± 0,023 | 0,781 ± 0,013 | 0,180 ± 0,008 | 0,137 ± 0,014 | 0,02 ± 0,00 |
| 2 | 10 | 0,099 ± 0,006 | 0,447 ± 0,022 | 0,786 ± 0,012 | 0,180 ± 0,008 | 0,118 ± 0,012 | 0,02 ± 0,00 |

### Controlli

- positivo_vocabolario_di_sezione_rif1: OrderedDict({'N0': 0.022769944201477904, 'N1': 0.00433117176896396, 'quota': 0.8097855782763472, 'soglie': [0.03, 0.3], 'riuscito': False})
- negativo_copia_di_pagina_vera_rif1: OrderedDict({'N0': 0.08784798672900015, 'N1': 0.07075139496305233, 'quota': 0.19461563551466055, 'soglie': [0.03, 0.25], 'riuscito': True})
- separazione_rif1: OrderedDict({'differenza_fra_le_quote': 0.6151699427616867, 'soglia': 0.2, 'riuscito': True})
- positivo_vocabolario_di_sezione_rif2: OrderedDict({'N0': 0.022769944201477904, 'N1': 0.007575780425275222, 'quota': 0.6672903386041891, 'soglie': [0.03, 0.3], 'riuscito': False})
- negativo_copia_di_pagina_vera_rif2: OrderedDict({'N0': 0.08784798672900015, 'N1': 0.06911061679987936, 'quota': 0.21329310581610927, 'soglie': [0.03, 0.25], 'riuscito': True})
- separazione_rif2: OrderedDict({'differenza_fra_le_quote': 0.4539972327880798, 'soglia': 0.2, 'riuscito': True})
- riproduzione_ia20_ia22: OrderedDict({'dettaglio': OrderedDict({'M1': OrderedDict({'qui': 0.03604932707711207, 'ia20': 0.03604932707711207, 'uguale': True}), 'M5': OrderedDict({'qui': 0.14160789524880663, 'ia20': 0.1416078952488066, 'uguale': True}), 'V21': OrderedDict({'qui': 0.054823252127049804, 'ia20': 0.054823252127049804, 'uguale': True}), 'E2': OrderedDict({'qui': 0.1133756257251108, 'ia22': 0.1133756257251108, 'uguale': True}), 'vere': OrderedDict({'qui': 0.11382446086563112, 'ia20': 0.11382446086563112, 'uguale': True})}), 'riuscito': True})

Letture valide: no

### Letture

- L1_1: OrderedDict({'riferimento': 'stessa sezione, lingua e mano', 'quota_di_sezione': 0.1512613113928747, 'ic': [0.10146784140382875, 0.19976697348397787], 'quota_calibrata': -0.07047536153531005, 'ic_calibrata': [-0.15141798653663532, 0.008373845357579386], 'copia_netta': [0.11382446086563112, 0.09660722364650881], 'lam': [0.20738768101540883, 0.2610823404529329], 'rho': [0.7300442087600032, 0.6970349021442258], 'esito': 'soprattutto copia di pagina'})
- L1_2: OrderedDict({'riferimento': 'stessa sezione e fascicolo', 'quota_di_sezione': 0.12800257031943507, 'ic': [0.07754856093039399, 0.17834651864251694], 'quota_calibrata': -0.18786576070715116, 'ic_calibrata': [-0.298998617352981, -0.07697533079437284], 'copia_netta': [0.11382446086563112, 0.09925463730960639], 'lam': [0.20738768101540883, 0.24819287176701643], 'rho': [0.7300442087600032, 0.7014560075179471], 'esito': 'soprattutto copia di pagina'})
- L2_al_vero_per_riferimento: OrderedDict({'V21': OrderedDict({'0': OrderedDict({'copia_netta': OrderedDict({'media': 0.054823252127049804, 'errore': 0.0015678230950060903, 'vero': 0.11382446086563112, 'al_vero': False, 'distanza_relativa': 0.5183526307955175}), 'lam': OrderedDict({'media': 0.09064644396819724, 'errore': 0.017662220176517814, 'vero': 0.20738768101540883, 'al_vero': False, 'distanza_relativa': 0.5629130740824367}), 'contatto': OrderedDict({'media': 0.18499531172269873, 'errore': 0.0011232005594140613, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.01808670299266179})}), '1': OrderedDict({'copia_netta': OrderedDict({'media': 0.04042228706506303, 'errore': 0.001174010889327292, 'vero': 0.09660722364650881, 'al_vero': False, 'distanza_relativa': 0.5815811122678525}), 'lam': OrderedDict({'media': 0.1256907601028161, 'errore': 0.033210187659804546, 'vero': 0.2610823404529329, 'al_vero': False, 'distanza_relativa': 0.5185780858070895}), 'contatto': OrderedDict({'media': 0.18499531172269873, 'errore': 0.0011232005594140613, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.01808670299266179})}), '2': OrderedDict({'copia_netta': OrderedDict({'media': 0.04461863625160131, 'errore': 0.0013995466196450776, 'vero': 0.09925463730960639, 'al_vero': False, 'distanza_relativa': 0.5504629560791021}), 'lam': OrderedDict({'media': 0.14913458490654025, 'errore': 0.029361766858926407, 'vero': 0.24819287176701643, 'al_vero': False, 'distanza_relativa': 0.39911817835551766}), 'contatto': OrderedDict({'media': 0.18499531172269873, 'errore': 0.0011232005594140613, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.01808670299266179})})}), 'M1': OrderedDict({'0': OrderedDict({'copia_netta': OrderedDict({'media': 0.03604932707711207, 'errore': 0.0015623429076297545, 'vero': 0.11382446086563112, 'al_vero': False, 'distanza_relativa': 0.6832901574674004}), 'lam': OrderedDict({'media': 0.05383330946298408, 'errore': 0.036784837480222515, 'vero': 0.20738768101540883, 'al_vero': False, 'distanza_relativa': 0.7404218553416184}), 'contatto': OrderedDict({'media': 0.18906707372102288, 'errore': 0.002475019779793974, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0035252892852651744})}), '1': OrderedDict({'copia_netta': OrderedDict({'media': 0.025844147728376822, 'errore': 0.001488021677813986, 'vero': 0.09660722364650881, 'al_vero': False, 'distanza_relativa': 0.7324822435334444}), 'lam': OrderedDict({'media': 0.028613224470783415, 'errore': 0.04617149783856241, 'vero': 0.2610823404529329, 'al_vero': False, 'distanza_relativa': 0.8904053624571299}), 'contatto': OrderedDict({'media': 0.18906707372102288, 'errore': 0.002475019779793974, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0035252892852651744})}), '2': OrderedDict({'copia_netta': OrderedDict({'media': 0.02569606272459744, 'errore': 0.0017214539038992198, 'vero': 0.09925463730960639, 'al_vero': False, 'distanza_relativa': 0.7411097010566534}), 'lam': OrderedDict({'media': 0.051887017871621276, 'errore': 0.07109514127457885, 'vero': 0.24819287176701643, 'al_vero': False, 'distanza_relativa': 0.7909407409559746}), 'contatto': OrderedDict({'media': 0.18906707372102288, 'errore': 0.002475019779793974, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0035252892852651744})})}), 'M5': OrderedDict({'0': OrderedDict({'copia_netta': OrderedDict({'media': 0.14160789524880663, 'errore': 0.005903821350086913, 'vero': 0.11382446086563112, 'al_vero': False, 'distanza_relativa': 0.2440901909122471}), 'lam': OrderedDict({'media': 0.2362011254195099, 'errore': 0.011071721890194113, 'vero': 0.20738768101540883, 'al_vero': False, 'distanza_relativa': 0.1389351781312423}), 'contatto': OrderedDict({'media': 0.15779857032805947, 'errore': 0.0014699487562727387, 'vero': 0.18840289899986576, 'al_vero': False, 'distanza_relativa': 0.1624408585763221})}), '1': OrderedDict({'copia_netta': OrderedDict({'media': 0.13218618439786312, 'errore': 0.005862127243282598, 'vero': 0.09660722364650881, 'al_vero': False, 'distanza_relativa': 0.36828468315723156}), 'lam': OrderedDict({'media': 0.2602413008739572, 'errore': 0.020908699239440602, 'vero': 0.2610823404529329, 'al_vero': True, 'distanza_relativa': 0.003221357589780411}), 'contatto': OrderedDict({'media': 0.15779857032805947, 'errore': 0.0014699487562727387, 'vero': 0.18840289899986576, 'al_vero': False, 'distanza_relativa': 0.1624408585763221})}), '2': OrderedDict({'copia_netta': OrderedDict({'media': 0.12991415923571303, 'errore': 0.006173325361498015, 'vero': 0.09925463730960639, 'al_vero': False, 'distanza_relativa': 0.30889762692366673}), 'lam': OrderedDict({'media': 0.2372535144929849, 'errore': 0.018309517077056123, 'vero': 0.24819287176701643, 'al_vero': True, 'distanza_relativa': 0.04407603327262566}), 'contatto': OrderedDict({'media': 0.15779857032805947, 'errore': 0.0014699487562727387, 'vero': 0.18840289899986576, 'al_vero': False, 'distanza_relativa': 0.1624408585763221})})}), 'E2': OrderedDict({'0': OrderedDict({'copia_netta': OrderedDict({'media': 0.1133756257251108, 'errore': 0.00791060325481783, 'vero': 0.11382446086563112, 'al_vero': True, 'distanza_relativa': 0.003943222195887864}), 'lam': OrderedDict({'media': 0.36048555399050375, 'errore': 0.014952541666843615, 'vero': 0.20738768101540883, 'al_vero': False, 'distanza_relativa': 0.7382206707047358}), 'contatto': OrderedDict({'media': 0.1796172567654809, 'errore': 0.008313425850732567, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0466322030129224})}), '1': OrderedDict({'copia_netta': OrderedDict({'media': 0.09712622051723165, 'errore': 0.00573797473116413, 'vero': 0.09660722364650881, 'al_vero': True, 'distanza_relativa': 0.005372236683064956}), 'lam': OrderedDict({'media': 0.4422888321865986, 'errore': 0.023447889956554394, 'vero': 0.2610823404529329, 'al_vero': False, 'distanza_relativa': 0.6940587839809604}), 'contatto': OrderedDict({'media': 0.1796172567654809, 'errore': 0.008313425850732567, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0466322030129224})}), '2': OrderedDict({'copia_netta': OrderedDict({'media': 0.09941073914236162, 'errore': 0.006012648078422922, 'vero': 0.09925463730960639, 'al_vero': True, 'distanza_relativa': 0.0015727409518237515}), 'lam': OrderedDict({'media': 0.4474281770833266, 'errore': 0.021509598484342432, 'vero': 0.24819287176701643, 'al_vero': False, 'distanza_relativa': 0.8027438656793346}), 'contatto': OrderedDict({'media': 0.1796172567654809, 'errore': 0.008313425850732567, 'vero': 0.18840289899986576, 'al_vero': True, 'distanza_relativa': 0.0466322030129224})})})})
- L2_verdetti_cambiati: ['M5 lam: al vero con pagina a caso no, con riferimento 1 sì', 'M5 lam: al vero con pagina a caso no, con riferimento 2 sì']
- L3_quota_di_sezione_degli_altri_testi: OrderedDict({'V21': OrderedDict({'1': OrderedDict({'quota': 0.261620474423317, 'errore': 0.012627254015419748, 'calibrata': 0.10892085950729509, 'vero': 0.1512613113928747, 'differenza': 0.1103591630304423, 'differisce_dal_vero': True}), '2': OrderedDict({'quota': 0.1858556997087452, 'errore': 0.012764443777570035, 'calibrata': -0.06043518357780723, 'vero': 0.12800257031943507, 'differenza': 0.057853129389310115, 'differisce_dal_vero': True})}), 'M1': OrderedDict({'1': OrderedDict({'quota': 0.28493174174426183, 'errore': 0.022011761645813494, 'calibrata': 0.14681488797086634, 'vero': 0.1512613113928747, 'differenza': 0.13367043035138715, 'differisce_dal_vero': True}), '2': OrderedDict({'quota': 0.2926482538902934, 'errore': 0.02611565877234377, 'calibrata': 0.1747921404429047, 'vero': 0.12800257031943507, 'differenza': 0.16464568357085835, 'differisce_dal_vero': True})}), 'M5': OrderedDict({'1': OrderedDict({'quota': 0.06693718346731757, 'errore': 0.008390384558510633, 'calibrata': -0.20754988690467419, 'vero': 0.1512613113928747, 'differenza': -0.08432412792555712, 'differisce_dal_vero': True}), '2': OrderedDict({'quota': 0.08402652663554004, 'errore': 0.010008695279123772, 'calibrata': -0.2847298834548387, 'vero': 0.12800257031943507, 'differenza': -0.04397604368389503, 'differisce_dal_vero': True})}), 'E2': OrderedDict({'1': OrderedDict({'quota': 0.1368419309475677, 'errore': 0.013902220899803103, 'calibrata': -0.09391503152401914, 'vero': 0.1512613113928747, 'differenza': -0.014419380445306995, 'differisce_dal_vero': False}), '2': OrderedDict({'quota': 0.11788268122144507, 'errore': 0.012402876512790957, 'calibrata': -0.21015640119375043, 'vero': 0.12800257031943507, 'differenza': -0.010119889097989998, 'differisce_dal_vero': False})})})

## Parte 2: il v21 e il Naibbe vero con l'eco nella metrica di ia14

Domanda: nella metrica di ia14/ia19 (stessa scala e stesso raggio) dove stanno il v21 e il Naibbe vero con un'eco leggera di pagina? Quanto pesa ogni misura nella distanza, e che cosa cambia senza Λ? Raggio epsilon: 0,461 (senza Λ: 0,457).

| cella | d (9 misure) | classe | peso di Λ | d senza Λ | classe senza Λ | firme | k90 |
|---|---|---|---|---|---|---|---|
| V_1 | 3,52 | lontano | 0,27 | 3,20 | lontano | 1/9 | 3,27 |
| V_3 | 2,72 | lontano | 0,44 | 2,15 | lontano | 1/9 | 3,68 |
| V_6 | 2,36 | lontano | 0,59 | 1,59 | lontano | 1/9 | 3,88 |
| V_3_italiano | 2,88 | lontano | 0,40 | 2,37 | lontano | 1/9 | 3,72 |
| V_3_tedesco | 2,52 | lontano | 0,52 | 1,86 | lontano | 3/9 | 3,76 |
| S_1 | 3,73 | lontano | 0,06 | 3,84 | lontano | 1/9 | 5,91 |
| S_2 | 3,52 | lontano | 0,12 | 3,50 | lontano | 1/9 | 5,19 |
| S_4 | 3,59 | lontano | 0,23 | 3,34 | lontano | 0/9 | 4,23 |
| N_30 | 3,30 | lontano | 0,08 | 3,35 | lontano | 2/9 | 4,47 |
| N_150 | 3,40 | lontano | 0,16 | 3,31 | lontano | 2/9 | 4,79 |
| N_600 | 3,70 | lontano | 0,27 | 3,34 | lontano | 1/9 | 4,35 |
| C_4 | 84,01 | lontano | 0,00 | 89,10 | lontano | 0/9 | 34,70 |
| C_16 | 72,54 | lontano | 0,00 | 76,94 | lontano | 1/9 | 99,70 |
| C_64 | 67,68 | lontano | 0,00 | 71,79 | lontano | 1/9 | 183,46 |
| R_6 | 6,67 | lontano | 0,51 | 5,01 | lontano | 0/9 | 3,41 |
| R_12 | 9,00 | lontano | 0,17 | 8,76 | lontano | 0/9 | 5,91 |
| R_24 | 13,48 | lontano | 0,02 | 14,13 | lontano | 0/9 | 26,27 |
| F_3p5 | 2,48 | lontano | 0,54 | 1,79 | lontano | 3/9 | 3,76 |
| F_5p0 | 3,09 | lontano | 0,35 | 2,65 | lontano | 1/9 | 4,27 |
| F_7p0 | 3,54 | lontano | 0,26 | 3,22 | lontano | 2/9 | 5,20 |
| P_1 | 3,75 | lontano | 0,23 | 3,48 | lontano | 2/9 | 22,86 |
| P_5 | 3,71 | lontano | 0,24 | 3,44 | lontano | 2/9 | 34,65 |
| P_25 | 3,64 | lontano | 0,25 | 3,35 | lontano | 2/9 | 30,03 |
| T0 | 3,57 | lontano | 0,22 | 3,34 | lontano | 4/9 | 4,83 |
| Tneg_i1 | 2,91 | lontano | 0,88 | 1,18 | vicino | 0/9 | — |
| nat_naibbe | 2,05 | lontano | 0,78 | 1,01 | vicino | 3/9 | 1,72 |
| nat_ts | 4,18 | lontano | 0,22 | 3,91 | lontano | 3/9 | 5,52 |
| nat_latino | 3,52 | lontano | 0,14 | 3,46 | lontano | 2/9 | 4,38 |
| VE_0p02 | 2,30 | lontano | 0,56 | 1,63 | lontano | 1/9 | 3,63 |
| VE_0p05 | 1,99 | lontano | 0,59 | 1,36 | vicino | 3/9 | 3,63 |
| VE_0p1 | 2,10 | lontano | 0,44 | 1,67 | lontano | 1/9 | 3,60 |
| VE_0p05_T6 | 1,60 | lontano | 0,18 | 1,54 | lontano | 1/9 | 3,95 |
| VA_8 | 2,95 | lontano | 0,38 | 2,47 | lontano | 0/9 | 4,90 |
| VA_12 | 2,82 | lontano | 0,42 | 2,28 | lontano | 0/9 | 4,87 |
| VA_16 | 2,73 | lontano | 0,44 | 2,16 | lontano | 0/9 | 3,79 |
| NV_30 | 2,97 | lontano | 0,37 | 2,49 | lontano | 1/9 | 3,62 |
| NV_150 | 3,09 | lontano | 0,34 | 2,66 | lontano | 1/9 | 3,72 |
| NV_600 | 3,13 | lontano | 0,34 | 2,70 | lontano | 1/9 | 3,58 |
| VB_0p5 | 2,86 | lontano | 0,40 | 2,35 | lontano | 1/9 | 3,89 |
| VB_0p8 | 2,99 | lontano | 0,37 | 2,53 | lontano | 0/9 | 4,03 |
| VB_1p0 | 3,11 | lontano | 0,34 | 2,69 | lontano | 1/9 | 3,95 |
| VT_2 | 2,21 | lontano | 0,51 | 1,64 | lontano | 1/9 | 4,55 |
| VT_3 | 2,56 | lontano | 0,35 | 2,19 | lontano | 1/9 | 5,14 |
| VT_4 | 2,87 | lontano | 0,39 | 2,38 | lontano | 1/9 | 4,83 |
| V21 | 1,52 | lontano | 0,62 | 1,00 | vicino | 5/9 | 1,69 |
| NE_0p0 | 2,09 | lontano | 0,75 | 1,10 | vicino | 3/9 | 1,72 |
| NE_0p02 | 1,63 | lontano | 0,64 | 1,04 | vicino | 4/9 | 1,73 |
| NE_0p05 | 1,55 | lontano | 0,60 | 1,05 | vicino | 4/9 | 1,73 |
| NE_0p1 | 1,79 | lontano | 0,21 | 1,69 | lontano | 4/9 | 1,75 |

### Controlli

- costruzione_in_impaginazione: OrderedDict({'firme_entro_la_tolleranza': 9, 'misure': ['k90', 'GL', 'GR', 'R_rel', 'Q', 'rho', 'lambda', 'E', 'g'], 'soglia': 7, 'riuscito': True})
- eco_misurabile: OrderedDict({'aumento_E': 0.37220253355451677, 'soglia': 0.03, 'riuscito': True})
- riproduzione_distanze_ia14: OrderedDict({'celle_confrontate': 28, 'scarto_massimo': 0.0, 'riuscito': True})
- negativo_testo_rimescolato: OrderedDict({'distanza': 2.9069234268262254, 'epsilon': 0.46142981489175144, 'distanza_senza_lambda': 1.178194060115352, 'epsilon_senza_lambda': 0.45673074114491496, 'latino_in_chiaro': 3.5720683641345596, 'riuscito': True})

Letture valide: sì

### Letture

- L2_V21: OrderedDict({'distanza': 1.5191314720706526, 'classe': 'lontano', 'distanza_senza_lambda': 0.9984917706688796, 'classe_senza_lambda': 'vicino', 'peso_lambda': 0.6159871696378522, 'firme_raggiunte': 5, 'mancate': ['k90', 'Q', 'lambda', 'E'], 'k90_raggiunto': False, 'k90': 1.6869071936359197})
- L2_NE_0p0: OrderedDict({'distanza': 2.0888592152559484, 'classe': 'lontano', 'distanza_senza_lambda': 1.097360690622394, 'classe_senza_lambda': 'vicino', 'peso_lambda': 0.7546828364300759, 'firme_raggiunte': 3, 'mancate': ['GL', 'GR', 'rho', 'lambda', 'E', 'g'], 'k90_raggiunto': True, 'k90': 1.7190299557243252})
- L2_NE_0p02: OrderedDict({'distanza': 1.6289414209646933, 'classe': 'lontano', 'distanza_senza_lambda': 1.042888109797756, 'classe_senza_lambda': 'vicino', 'peso_lambda': 0.6356557029538875, 'firme_raggiunte': 4, 'mancate': ['GL', 'GR', 'rho', 'lambda', 'E'], 'k90_raggiunto': True, 'k90': 1.7313761569741424})
- L2_NE_0p05: OrderedDict({'distanza': 1.5497761541260122, 'classe': 'lontano', 'distanza_senza_lambda': 1.0456296406621985, 'classe_senza_lambda': 'vicino', 'peso_lambda': 0.5953632716527932, 'firme_raggiunte': 4, 'mancate': ['GL', 'GR', 'rho', 'lambda', 'E'], 'k90_raggiunto': True, 'k90': 1.7336505545334082})
- L2_NE_0p1: OrderedDict({'distanza': 1.7938177275200293, 'classe': 'lontano', 'distanza_senza_lambda': 1.6902075819307045, 'classe_senza_lambda': 'lontano', 'peso_lambda': 0.21082931316887074, 'firme_raggiunte': 4, 'mancate': ['GL', 'GR', 'rho', 'lambda', 'E'], 'k90_raggiunto': True, 'k90': 1.753247287019214})
- L2_nat_naibbe: OrderedDict({'distanza': 2.0515037516507153, 'classe': 'lontano', 'distanza_senza_lambda': 1.0149887486741807, 'classe_senza_lambda': 'vicino', 'peso_lambda': 0.7824168285678831, 'firme_raggiunte': 3, 'mancate': ['GL', 'GR', 'rho', 'lambda', 'E', 'g'], 'k90_raggiunto': True, 'k90': 1.7217148187047984})
- L2_peso_di_lambda: OrderedDict({'celle': 40, 'mediana': 0.3446350257408104, 'dominanti': 8, 'naibbe_nativo': 0.7824168285678831, 'classe_cambia_senza_lambda': ['Tneg_i1', 'VE_0p05'], 'spearman_distanza_con_e_senza_lambda': 0.9626641651031895, 'migliore_con': 'VE_0p05_T6', 'migliore_senza': 'Tneg_i1', 'distanza_migliore_con': 1.6037243322791903, 'distanza_migliore_senza': 1.178194060115352})
- L2_naibbe_eco_contro_le_celle_semplificate: OrderedDict({'migliore_semplificata': 'VE_0p05_T6', 'distanza_migliore_semplificata': 1.6037243322791903, 'naibbe_eco_piu_vicino_del_migliore': ['NE_0p05'], 'naibbe_nativo': 2.0515037516507153})
- L2_k90_raggiunto_da: ['nat_naibbe', 'NE_0p0', 'NE_0p02', 'NE_0p05', 'NE_0p1']

## Parte 3: la temperatura degli imitatori

Domanda: lo scarto di forma delle parole nuove (vero contro imitatori, ia24) e' solo l'effetto della scrittura a temperatura 1? Temperature: 0.8, 0.9, 1.0, 1.1.

Vero (calcolato qui): copia_netta 0,114, lam 0,207, contatto 0,188, G9 0,040, bordi_inizio 0,079, bordi_fine 0,048, D 0,144, costo_forma 3,479, parole_nuove 0,148

| cella | libri | forma | parole nuove | contatto | copia netta | e231 | e266 | K |
|---|---|---|---|---|---|---|---|---|
| M1 T=0.8 | 10 | 3,333 ± 0,008 | 0,066 ± 0,002 | 0,233 ± 0,003 | 0,131 ± 0,002 | 0,986 ± 0,002 | 0,991 ± 0,002 | 0,937 ± 0,003 |
| M1 T=0.9 | 10 | 3,525 ± 0,006 | 0,102 ± 0,002 | 0,209 ± 0,002 | 0,067 ± 0,003 | 0,900 ± 0,006 | 0,928 ± 0,007 | 0,747 ± 0,006 |
| M1 T=1.0 | 10 | 3,746 ± 0,006 | 0,147 ± 0,002 | 0,189 ± 0,002 | 0,035 ± 0,002 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 |
| M1 T=1.1 | 10 | 3,980 ± 0,006 | 0,201 ± 0,001 | 0,168 ± 0,002 | 0,024 ± 0,002 | 0,865 ± 0,007 | 0,920 ± 0,005 | 0,933 ± 0,003 |
| E2 T=0.8 | 10 | 3,583 ± 0,012 | 0,071 ± 0,001 | 0,223 ± 0,012 | 0,246 ± 0,020 | 0,986 ± 0,002 | 0,989 ± 0,002 | 0,929 ± 0,006 |
| E2 T=0.9 | 10 | 3,666 ± 0,015 | 0,103 ± 0,002 | 0,198 ± 0,010 | 0,163 ± 0,010 | 0,919 ± 0,007 | 0,933 ± 0,006 | 0,804 ± 0,009 |
| E2 T=1.0 | 10 | 3,817 ± 0,014 | 0,146 ± 0,002 | 0,180 ± 0,008 | 0,114 ± 0,007 | 0,801 ± 0,012 | 0,864 ± 0,004 | 0,797 ± 0,007 |
| E2 T=1.1 | 10 | 4,006 ± 0,012 | 0,196 ± 0,003 | 0,158 ± 0,007 | 0,090 ± 0,003 | 0,866 ± 0,006 | 0,924 ± 0,005 | 0,923 ± 0,006 |

### Controllo del processo noto (libro v21 nella disposizione del vero)

- 080: OrderedDict({'T': 0.8, 'forma': (3.261601293005145, 0.0057034672963565325), 'scarto': -0.3422051665061563, 'parole_nuove': (0.07830877340028462, 0.0006634594941861487)})
- 090: OrderedDict({'T': 0.9, 'forma': (3.4878812071862293, 0.007334690106981592), 'scarto': -0.11592525232507178, 'parole_nuove': (0.13178698303740216, 0.0010516396190300456)})
- 100: OrderedDict({'T': 1.0, 'forma': (3.7349220544867645, 0.011453383102402456), 'scarto': 0.13111559497546343, 'parole_nuove': (0.19422147128416578, 0.0012550615804027658)})
- 110: OrderedDict({'T': 1.1, 'forma': (4.008086122002779, 0.011175609535335699), 'scarto': 0.40427966249147795, 'parole_nuove': (0.2659948758642517, 0.0013643112383810762)})
- _testo: OrderedDict({'forma': 3.603806459511301, 'parole_nuove': 0.14955318535601037})

### Controlli

- paper_positivo: OrderedDict({'AUC': 0.9880943044799528, 'soglia': 0.95, 'riuscito': True})
- paper_negativo: OrderedDict({'AUC_e231': 0.5060288207038526, 'AUC_e266': 0.5030291147926673, 'banda': (0.45, 0.55), 'riuscito': True})
- identita_a_T1: OrderedDict({'libri': 4, 'uguali': 4, 'riuscito': True})
- K_positivo: OrderedDict({'AUC': OrderedDict({'parole': 0.9820017645328889, 'e192': 0.9349622586020979}), 'soglia': 0.85, 'riuscito': True})
- K_negativo: OrderedDict({'AUC': 0.49913930006862073, 'banda': (0.45, 0.55), 'riuscito': True})
- K_vede_v21: OrderedDict({'AUC': 0.7661552788942261, 'soglia': 0.65, 'riuscito': True})
- negativo_repliche_a_T1: OrderedDict({'dettaglio': OrderedDict({'M1': OrderedDict({'replica0': (3.7454916573809305, 0.011647567504205612), 'replica1': (3.746331389247467, 0.005970538772202198), 'differenza': -0.0008397318665362974, 'errore': 0.013088665401613577, 'uguali': True}), 'E2': OrderedDict({'replica0': (3.778750445201621, 0.008086727542861579), 'replica1': (3.8551995274273407, 0.0061923328532258876), 'differenza': -0.07644908222571978, 'errore': 0.010185290792000822, 'uguali': False})}), 'riuscito': False, 'nota': 'con meno di due libri per replica il controllo non si fa'})
- la_temperatura_agisce: OrderedDict({'dettaglio': OrderedDict({'M1': OrderedDict({'forma': [[0.8, 3.333320590314954, 0.008142344652200196], [0.9, 3.524686495966671, 0.0064956343262348145], [1.0, 3.7459115233141986, 0.006171643139686109], [1.1, 3.9798658958037536, 0.005680425735161341]], 'cresce_con_T': True}), 'E2': OrderedDict({'forma': [[0.8, 3.582690364234783, 0.011764892483414028], [0.9, 3.6659848477322243, 0.014669662849448265], [1.0, 3.8169749863144817, 0.013616149889516328], [1.1, 4.00589098981364, 0.012380041365272201]], 'cresce_con_T': True})}), 'riuscito': True})
- processo_noto_vede_la_temperatura: OrderedDict({'riuscito': True, 'nota': "esito, non condizione di validita': dice se lo scarto di forma a T=1 e' un effetto generico"})

Letture valide: sì

### Letture

- L3_M1: OrderedDict({'per_temperatura': OrderedDict({'080': OrderedDict({'T': 0.8, 'forma': 3.333320590314954, 'scarto': -0.1452313708316395, 'al_vero': True, 'guardia_parole_nuove': False, 'parole_nuove': 0.06648636083585077}), '090': OrderedDict({'T': 0.9, 'forma': 3.524686495966671, 'scarto': 0.046134534820077455, 'al_vero': True, 'guardia_parole_nuove': True, 'parole_nuove': 0.10212554557417683}), '100': OrderedDict({'T': 1.0, 'forma': 3.7459115233141986, 'scarto': 0.26735956216760526, 'al_vero': False, 'guardia_parole_nuove': True, 'parole_nuove': 0.14722778763862202}), '110': OrderedDict({'T': 1.1, 'forma': 3.9798658958037536, 'scarto': 0.5013139346571602, 'al_vero': False, 'guardia_parole_nuove': True, 'parole_nuove': 0.2008469782604087})}), 'scarto_T1': 0.26735956216760526, 'temperatura_migliore': '090', 'frazione_chiusa': 0.8274438570812884, 'esito': 'quasi tutto effetto della temperatura', 'compromessi_persi_contatto_copia': ['contatto'], 'giudici_da_T1_alla_migliore': OrderedDict({'e231': 'peggiora', 'e266': 'peggiora', 'K': 'avvicina'}), 'giudici_validi': True})
- L3_E2: OrderedDict({'per_temperatura': OrderedDict({'080': OrderedDict({'T': 0.8, 'forma': 3.582690364234783, 'scarto': 0.10413840308818978, 'al_vero': True, 'guardia_parole_nuove': False, 'parole_nuove': 0.07120251011375309}), '090': OrderedDict({'T': 0.9, 'forma': 3.6659848477322243, 'scarto': 0.18743288658563095, 'al_vero': False, 'guardia_parole_nuove': True, 'parole_nuove': 0.10305748947287074}), '100': OrderedDict({'T': 1.0, 'forma': 3.8169749863144817, 'scarto': 0.33842302516788836, 'al_vero': False, 'guardia_parole_nuove': True, 'parole_nuove': 0.14599358779738664}), '110': OrderedDict({'T': 1.1, 'forma': 4.00589098981364, 'scarto': 0.5273390286670465, 'al_vero': False, 'guardia_parole_nuove': True, 'parole_nuove': 0.1963207298674861})}), 'scarto_T1': 0.33842302516788836, 'temperatura_migliore': '090', 'frazione_chiusa': 0.4461579956250101, 'esito': 'in parte effetto della temperatura', 'compromessi_persi_contatto_copia': ['copia_netta'], 'giudici_da_T1_alla_migliore': OrderedDict({'e231': 'peggiora', 'e266': 'peggiora', 'K': 'invariata'}), 'giudici_validi': True})
- L3_controllo_processo_noto: OrderedDict({'scarto_T1': 0.13111559497546343, 'temperatura_migliore': '090', 'frazione_chiusa': 1.8841454164683131, 'il_controllo_vede_l_effetto': True})
- L3_sintesi: lo scarto di forma e' in gran parte un effetto della scrittura a temperatura 1 (confermato dal processo noto)

## Parte 4: seconda trascrizione e altro alfabeto

Domanda: k90 (ia03), R_rel (ia02), contatto (ia08) e copia netta (ia09) reggono al cambio di trascrizione e di alfabeto? Tolleranze: {'k90': 0.317, 'R_rel': 0.061, 'copia_netta': 0.015, 'lam': 0.079, 'rho': 0.173, 'contatto': 0.03}.

| variante | parole | tipi | k90 (sd, n) | R_rel | copia netta | Λ | rho | contatto |
|---|---|---|---|---|---|---|---|---|
| ZL | 34690 | 6980 | 2,15 (0,23, 3) | 1,008 | 0,114 | 0,207 | 0,730 | 0,188 |
| ZLn | 34690 | 6980 | 1,90 (0,04, 3) | 1,002 | 0,103 | 0,207 | 0,710 | 0,181 |
| IT | 34235 | 7026 | 2,23 (0,35, 3) | 0,993 | 0,125 | 0,217 | 0,797 | 0,173 |
| GC | 36037 | 8184 | 2,27 (0,37, 3) | 0,982 | 0,091 | -0,014 | 0,681 | 0,227 |
| ZLx | 34690 | 6980 | 2,36 (0,71, 3) | 0,975 | 0,116 | 0,183 | 0,694 | 0,204 |
| ZLc | 32197 | 7932 | 1,97 (0,04, 3) | 1,003 | 0,101 | 0,163 | 0,866 | 0,154 |
| RIN | 34690 | 6980 | 1,95 (0,06, 3) | 1,005 | 0,114 | 0,207 | 0,730 | 0,188 |
| SPO | 34690 | 9469 | 2,47 (0,00, 1) | 1,008 | 0,066 | 0,104 | 0,427 | 0,603 |

Lingue: minimo k90 con le lettere 3,49 (20 lingue), con i 6 digrammi fusi 3,47 (20 lingue).

### Controlli

- ZL_uguale_al_contesto_di_ia07: OrderedDict({'riuscito': True})
- negativo_rinomina: OrderedDict({'differenze': OrderedDict({'copia_netta': 0.0, 'lam': 0.0, 'contatto': 0.0}), 'differenza_k90': 0.19728999457296204, 'soglia_conteggi': 1e-06, 'soglia_k90': 0.317, 'riuscito': True})
- positivo_confini_spostati: OrderedDict({'misure_mosse': ['copia_netta', 'contatto'], 'soglia': 2, 'riuscito': True})
- riproduzione_ia20_conteggi: OrderedDict({'differenze': OrderedDict({'copia_netta': 0.0, 'lam': 0.0, 'contatto': 0.0}), 'soglia': 0.0005, 'riuscito': True})
- riproduzione_k90_di_ia03: OrderedDict({'semi_confrontati': 3, 'riuscito': True})

Letture valide: sì

### Letture

- L4_ZLn: OrderedDict({'descrizione': 'ZL, EVA non fuso', 'k90_sotto_tutte_le_lingue': True, 'k90_di_riferimento_sotto_tutte_le_lingue': True, 'confronto_lingue': 'lettere', 'misure': OrderedDict({'k90': OrderedDict({'variante': 1.9030864702181214, 'riferimento': 2.1511238388415945, 'differenza': -0.24803736862347314, 'regge': True}), 'R_rel': OrderedDict({'variante': 1.001826882807616, 'riferimento': 1.0079574966875626, 'differenza': -0.0061306138799466225, 'regge': True}), 'copia_netta': OrderedDict({'variante': 0.10328758859900468, 'riferimento': 0.11382446086563112, 'differenza': -0.010536872266626446, 'regge': True}), 'lam': OrderedDict({'variante': 0.20739159001314056, 'riferimento': 0.20738768101540883, 'differenza': 3.9089977317274816e-06, 'regge': True}), 'rho': OrderedDict({'variante': 0.7097295162649786, 'riferimento': 0.7300442087600032, 'differenza': -0.0203146924950246, 'regge': True}), 'contatto': OrderedDict({'variante': 0.1808421072280673, 'riferimento': 0.18840289899986576, 'differenza': -0.00756079177179847, 'regge': True})}), 'regge_tutto': True})
- L4_IT: OrderedDict({'descrizione': 'Takahashi, EVA fuso', 'k90_sotto_tutte_le_lingue': True, 'k90_di_riferimento_sotto_tutte_le_lingue': True, 'confronto_lingue': 'lettere', 'misure': OrderedDict({'k90': OrderedDict({'variante': 2.2339142033750172, 'riferimento': 2.1511238388415945, 'differenza': 0.0827903645334227, 'regge': True}), 'R_rel': OrderedDict({'variante': 0.992612207302813, 'riferimento': 1.0079574966875626, 'differenza': -0.01534528938474966, 'regge': True}), 'copia_netta': OrderedDict({'variante': 0.12486100993060081, 'riferimento': 0.11382446086563112, 'differenza': 0.011036549064969689, 'regge': True}), 'lam': OrderedDict({'variante': 0.21711346537693854, 'riferimento': 0.20738768101540883, 'differenza': 0.00972578436152971, 'regge': True}), 'rho': OrderedDict({'variante': 0.7969340134723275, 'riferimento': 0.7300442087600032, 'differenza': 0.06688980471232431, 'regge': True}), 'contatto': OrderedDict({'variante': 0.17260398408008681, 'riferimento': 0.18840289899986576, 'differenza': -0.015798914919778945, 'regge': True})}), 'regge_tutto': True})
- L4_GC: OrderedDict({'descrizione': 'Claston, alfabeto v101', 'k90_sotto_tutte_le_lingue': True, 'k90_di_riferimento_sotto_tutte_le_lingue': True, 'confronto_lingue': 'lettere', 'misure': OrderedDict({'k90': OrderedDict({'variante': 2.268845463192374, 'riferimento': 2.1511238388415945, 'differenza': 0.11772162435077949, 'regge': True}), 'R_rel': OrderedDict({'variante': 0.9822152427292166, 'riferimento': 1.0079574966875626, 'differenza': -0.025742253958346062, 'regge': True}), 'copia_netta': OrderedDict({'variante': 0.09099670038017357, 'riferimento': 0.11382446086563112, 'differenza': -0.02282776048545755, 'regge': False}), 'lam': OrderedDict({'variante': -0.01354658931013697, 'riferimento': 0.20738768101540883, 'differenza': -0.2209342703255458, 'regge': False}), 'rho': OrderedDict({'variante': 0.6811083467428285, 'riferimento': 0.7300442087600032, 'differenza': -0.0489358620171747, 'regge': True}), 'contatto': OrderedDict({'variante': 0.22666517818473847, 'riferimento': 0.18840289899986576, 'differenza': 0.03826227918487271, 'regge': False})}), 'regge_tutto': False})
- L4_ZLx: OrderedDict({'descrizione': 'ZL fuso + 6 digrammi fusi', 'k90_sotto_tutte_le_lingue': True, 'k90_di_riferimento_sotto_tutte_le_lingue': True, 'confronto_lingue': 'fuse', 'misure': OrderedDict({'k90': OrderedDict({'variante': 2.355268149090269, 'riferimento': 2.1511238388415945, 'differenza': 0.20414431024867463, 'regge': True}), 'R_rel': OrderedDict({'variante': 0.9745198621054346, 'riferimento': 1.0079574966875626, 'differenza': -0.033437634582128006, 'regge': True}), 'copia_netta': OrderedDict({'variante': 0.11599419393756596, 'riferimento': 0.11382446086563112, 'differenza': 0.00216973307193484, 'regge': True}), 'lam': OrderedDict({'variante': 0.18311919210304783, 'riferimento': 0.20738768101540883, 'differenza': -0.024268488912360997, 'regge': True}), 'rho': OrderedDict({'variante': 0.693811398900303, 'riferimento': 0.7300442087600032, 'differenza': -0.03623280985970023, 'regge': True}), 'contatto': OrderedDict({'variante': 0.2039705902809908, 'riferimento': 0.18840289899986576, 'differenza': 0.015567691281125035, 'regge': True})}), 'regge_tutto': True})
- L4_ZLc: OrderedDict({'descrizione': 'ZL, virgola non spazio', 'k90_sotto_tutte_le_lingue': True, 'k90_di_riferimento_sotto_tutte_le_lingue': True, 'confronto_lingue': 'lettere', 'misure': OrderedDict({'k90': OrderedDict({'variante': 1.9703791409966227, 'riferimento': 2.1511238388415945, 'differenza': -0.18074469784497182, 'regge': True}), 'R_rel': OrderedDict({'variante': 1.0033480642261268, 'riferimento': 1.0079574966875626, 'differenza': -0.004609432461435858, 'regge': True}), 'copia_netta': OrderedDict({'variante': 0.1012345576307142, 'riferimento': 0.11382446086563112, 'differenza': -0.012589903234916919, 'regge': True}), 'lam': OrderedDict({'variante': 0.16317826590735396, 'riferimento': 0.20738768101540883, 'differenza': -0.04420941510805487, 'regge': True}), 'rho': OrderedDict({'variante': 0.8664967751358748, 'riferimento': 0.7300442087600032, 'differenza': 0.13645256637587155, 'regge': True}), 'contatto': OrderedDict({'variante': 0.15411051182361082, 'riferimento': 0.18840289899986576, 'differenza': -0.034292387176254935, 'regge': False})}), 'regge_tutto': False})
- L4_sintesi: OrderedDict({'L4_ZLn': True, 'L4_IT': True, 'L4_GC': False, 'L4_ZLx': True, 'L4_ZLc': False})

## Parte 5: il metro "vero contro vero"

Domanda: quanto varia il vero da se' stesso, misura per misura, e quali verdetti "al vero" di ia20-ia24 cambiano leggendoli con questo intervallo? (200 divisioni dei fogli in due meta', 1000 ricampionamenti di pagine e di fogli.)

| misura | vero | sigma (divisioni) | sigma (pagine) | sigma (fogli) | sigma del vero | vero ± 2 sigma | meta' contro meta' (95%) | coppie entro il 5% |
|---|---|---|---|---|---|---|---|---|
| copia_netta | 0,1138 | 0,0087 | 0,0081 | 0,0098 | 0,0098 | 0,0942 – 0,1334 | -0,0344 – 0,0315 | 0,31 |
| lam | 0,2074 | 0,0393 | 0,0388 | 0,0387 | 0,0393 | 0,1287 – 0,2860 | -0,1687 – 0,1253 | 0,10 |
| contatto | 0,1885 | 0,0071 | 0,0076 | 0,0097 | 0,0097 | 0,1690 – 0,2079 | -0,0267 – 0,0302 | 0,51 |
| D | 0,1444 | 0,0112 | 0,0090 | 0,0122 | 0,0122 | 0,1201 – 0,1688 | -0,0447 – 0,0432 | 0,23 |
| G9 | 0,0402 | 0,0014 | 0,0016 | 0,0019 | 0,0019 | 0,0364 – 0,0440 | -0,0050 – 0,0054 | 0,54 |
| bordi_inizio | 0,0790 | 0,0038 | 0,0040 | 0,0048 | 0,0048 | 0,0693 – 0,0887 | -0,0148 – 0,0150 | 0,43 |
| bordi_fine | 0,0475 | 0,0019 | 0,0023 | 0,0025 | 0,0025 | 0,0426 – 0,0525 | -0,0072 – 0,0066 | 0,50 |
| parole_nuove | 0,1484 | 0,0040 | 0,0041 | 0,0051 | 0,0051 | 0,1382 – 0,1586 | -0,0158 – 0,0143 | 0,64 |
| costo_forma | 3,4786 | 0,0246 | 0,0310 | 0,0339 | 0,0339 | 3,4107 – 3,5464 | -0,0877 – 0,0926 | 1,00 |

Coppie di meta' "al vero" fra loro su tutte e nove le misure insieme (regola del 5%): 0,000

### Controlli

- negativo_media_zero: OrderedDict({'dettaglio': {'copia_netta': 0.037823239563537864, 'lam': 0.0959337357050616, 'contatto': 0.013873175545700337, 'D': 0.07357127274454796, 'G9': 0.0621972499172, 'bordi_inizio': 0.03119297903091889, 'bordi_fine': 0.10364705735908539, 'parole_nuove': 0.03898524360160881, 'costo_forma': 0.05438222234856465}, 'soglia': 0.25, 'riuscito': True})
- accordo_ricampionamento_divisioni: OrderedDict({'rapporti': {'copia_netta': 1.1319907114128567, 'lam': 0.9852481674516881, 'contatto': 1.370852269254236, 'D': 1.0902511855302575, 'G9': 1.3923129714021665, 'bordi_inizio': 1.2797936627745796, 'bordi_fine': 1.32028953020805, 'parole_nuove': 1.2843835666895727, 'costo_forma': 1.378274779150894}, 'banda': (0.5, 2.0), 'riuscito': True})
- positivo_lingua_A_contro_B: OrderedDict({'dettaglio': OrderedDict({'copia_netta': OrderedDict({'A': 0.12078532742491384, 'B': 0.11141935127978816, 'differenza': 0.009365976145125673, 'in_sigma': 0.5409841184607278}), 'lam': OrderedDict({'A': 0.19320057884760433, 'B': 0.21420331615349952, 'differenza': -0.02100273730589519, 'in_sigma': 0.2670814965039467}), 'contatto': OrderedDict({'A': 0.1320024262799422, 'B': 0.24099798165034675, 'differenza': -0.10899555537040456, 'in_sigma': 7.68230553749583}), 'D': OrderedDict({'A': 0.07240476995766254, 'B': 0.1806020048087545, 'differenza': -0.10819723485109195, 'in_sigma': 4.851630045668699}), 'G9': OrderedDict({'A': 0.05097445803856144, 'B': 0.024234395609582845, 'differenza': 0.026740062428978594, 'in_sigma': 9.883525502762838}), 'bordi_inizio': OrderedDict({'A': 0.06318836691518294, 'B': 0.10089882493683959, 'differenza': -0.03771045802165665, 'in_sigma': 4.982026913555}), 'bordi_fine': OrderedDict({'A': 0.049175517549509835, 'B': 0.053249833070283505, 'differenza': -0.004074315520773669, 'in_sigma': 1.087706991809911}), 'parole_nuove': OrderedDict({'A': 0.17389368711601816, 'B': 0.13502842018483968, 'differenza': 0.03886526693117848, 'in_sigma': 4.8850608937364575}), 'costo_forma': OrderedDict({'A': 3.6940725978624878, 'B': 3.338586626346008, 'differenza': 0.35548597151648, 'in_sigma': 7.225375715512272})}), 'misure_viste': 6, 'soglia': [3, 3.0], 'riuscito': True})
- coerenza_numeri_per_pagina: OrderedDict({'copia_netta': [0.11382446086563112, 0.11382446086563112], 'lam': [0.2073876810154085, 0.20738768101540883], 'contatto': [0.18847533924362891, 0.18840289899986576], 'riuscito': True})

### Verdetti rielaborati (ia20-ia24)

Totali: {'celle': 225, 'con_salvato': 133, 'riprodotte': 133, 'cambia_nuovo': 34, 'cambia_nuovo_o_vecchio': 34, 'diventa_vero_nuovo': 34, 'smette_vero_nuovo': 0}

- ia20: 45 celle, 5 cambiano con la regola nuova: M1 bordi_inizio (no -> sì); M3 D (no -> sì); M3 bordi_fine (no -> sì); M4 bordi_fine (no -> sì); M5 lam (no -> sì)
- ia22: 54 celle, 8 cambiano con la regola nuova: M1 bordi_inizio (no -> sì); E0 contatto (no -> sì); E1 copia_netta (no -> sì); E1 contatto (no -> sì); E2 bordi_fine (no -> sì); E3 contatto (no -> sì); E3 bordi_fine (no -> sì); M5 lam (no -> sì)
- ia23: 72 celle, 11 cambiano con la regola nuova: M1 bordi_inizio (no -> sì); E1 copia_netta (no -> sì); E1 contatto (no -> sì); E2 bordi_fine (no -> sì); E3 contatto (no -> sì); E3 bordi_fine (no -> sì); M5 lam (no -> sì); P1 bordi_inizio (no -> sì); P2 D (no -> sì); P3 lam (no -> sì); P3 D (no -> sì)
- ia24: 54 celle, 10 cambiano con la regola nuova: M1 bordi_inizio (no -> sì); E2 bordi_fine (no -> sì); M5 lam (no -> sì); W1 D (no -> sì); W1 bordi_fine (no -> sì); W2 copia_netta (no -> sì); W2 bordi_inizio (no -> sì); W3 contatto (no -> sì); W3 D (no -> sì); W3 bordi_inizio (no -> sì)

