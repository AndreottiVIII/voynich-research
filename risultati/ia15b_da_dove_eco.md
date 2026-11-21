# ia15b — da dove viene l'eco della pagina (seconda versione)

Soglie nella preregistrazione `preregistrazioni/ia15b.md`. "Eco" = eccesso di parole uguali o a una modifica da parole gia' scritte (stessa riga prima, righe sopra), per parola fonte, rispetto a una pagina di riferimento della stessa sezione con la stessa geometria di righe. Intervalli al 95% col bootstrap sulle pagine. Nessuna parola nei risultati. Nuovo rispetto a ia15: controlli separati per lettura, generatori tarati sull'eco vicina del Voynich, varianti sulla sola parte locale dell'eco.

## Taratura dei generatori (solo la quantita' di eco vicina)

Bersaglio: eco vicina 0.01159 (eco vicina del testo vere). Tolleranza 8%. Livelli: {"V": 1.0, "M": 0.5, "D": 0.25}.

| famiglia | livello | quota del bersaglio | livello numerico (quota tema o prob. di copia) | eco vicina ottenuta | raggiunto | valutazioni |
|---|---|---|---|---|---|---|
| argP | V | 1.0 | 0.3624 | 0.01173 | si | 3 |
| argP | M | 0.5 | 0.2542 | 0.00585 | si | 1 |
| argP | D | 0.25 | 0.1875 | 0.00273 | si | 2 |
| argR | V | 1.0 | 0.4356 | 0.01156 | si | 3 |
| argR | M | 0.5 | 0.3056 | 0.00506 | NO | 8 |
| argS | V | 1.0 | 0.3931 | 0.01221 | si | 2 |
| argF | V | 1.0 | 0.4341 | 0.01243 | si | 2 |
| argF | M | 0.5 | 0.2898 | 0.00562 | si | 1 |
| tecM | V | 1.0 | 0.2786 | 0.01111 | si | 3 |
| tecM | M | 0.5 | 0.1650 | 0.00610 | si | 1 |
| tecM | D | 0.25 | 0.0950 | 0.00298 | si | 1 |
| tecP | V | 1.0 | 0.2548 | 0.01121 | si | 3 |
| tecP | M | 0.5 | 0.1533 | 0.00605 | si | 1 |
| tecP | D | 0.25 | 0.0940 | 0.00314 | NO | 8 |

## Letture

- vere: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a13: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a14: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a15: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a16: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a17: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a18: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a19: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- ts1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **zona grigia**; sintesi **argomento di pagina (senza il paragrafo)**
- ts2: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **zona grigia**; sintesi **argomento di pagina (senza il paragrafo)**
- a21: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a20: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- a22: eco misurabile; profilo **intermedio**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **mista (senza il paragrafo)**
- latino: eco misurabile; profilo **intermedio**; varianti **medie**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **si**; sintesi **argomento che scorre (senza il paragrafo)**
- italiano: eco misurabile; profilo **intermedio**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **zona grigia**; sintesi **argomento che scorre (senza il paragrafo)**
- inglese: eco misurabile; profilo **intermedio**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento che scorre (senza il paragrafo)**
- latGeom: eco misurabile; profilo **intermedio**; varianti **medie**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **si**; sintesi **argomento che scorre (senza il paragrafo)**
- ingGeom: eco misurabile; profilo **intermedio**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **zona grigia**; sintesi **argomento che scorre (senza il paragrafo)**
- argP1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- argP2: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- argP3: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- argR1: eco misurabile; profilo **ripido**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **zona grigia (senza il paragrafo)**
- argR2: eco misurabile; profilo **ripido**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **zona grigia (senza il paragrafo)**
- argR3: eco misurabile; profilo **ripido**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **zona grigia (senza il paragrafo)**
- argS1: eco misurabile; profilo **intermedio**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **si**; sintesi **argomento che scorre (senza il paragrafo)**
- argF1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- argF2: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- tecM1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecM2: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecM3: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecP1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecCoda1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **fine**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecTesta1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **inizio**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- argPm1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- argRm1: eco misurabile; profilo **ripido**; varianti **basse**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **zona grigia (senza il paragrafo)**
- argFm1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- tecMm1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecPm1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- argPd1: eco misurabile; profilo **piatto**; varianti **nessuna parte locale**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **non leggibile (varianti in eccesso non misurabili)**; pagine vicine **no**; sintesi **argomento di pagina (senza il paragrafo)**
- tecMd1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **dentro la parola**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**
- tecPd1: eco misurabile; profilo **ripido**; varianti **alte**; paragrafo **non leggibile (i controlli di questa lettura non sono superati)**; modifiche **nessun posto prevale**; pagine vicine **no**; sintesi **tecnica (senza il paragrafo)**

## Controlli

- negativo_rimescolato_fra_pagine: SUPERATO (eco debole (nessuna ripetizione sopra il caso)); letture profilo, varianti, paragrafo, direzione, pagine_vicine, sintesi, sintesi_senza_paragrafo; testi vere~t1, vere~t2, vere~t3, vere~t4, vere~t5, tecM1~t, argP1~t, argF1~t
- negativo_nella_pagina_profilo: SUPERATO (profilo piatto (l'eco di pagina resta, perde la distanza)); letture profilo; testi vere~p, tecM1~p, argP1~p, argF1~p
- negativo_nella_pagina_varianti: SUPERATO (varianti non alte (nessuna parte locale da leggere)); letture varianti; testi vere~p, tecM1~p, argP1~p, argF1~p
- negativo_nella_pagina_paragrafo: SUPERATO (il paragrafo non conta); letture paragrafo; testi vere~p, tecM1~p, argP1~p, argF1~p
- positivo_tecnica_profilo: SUPERATO (profilo ripido); letture profilo; testi tecM1, tecM2, tecM3
- positivo_tecnica_varianti: SUPERATO (varianti alte); letture varianti; testi tecM1, tecM2, tecM3
- positivo_tecnica_paragrafo: NON SUPERATO (il paragrafo non conta (zona grigia ammessa: la copia e' per parole, non per paragrafi)); letture paragrafo; testi tecM1, tecM2, tecM3
- positivo_argomento_pagina_profilo: SUPERATO (profilo piatto); letture profilo; testi argP1, argP2, argP3
- positivo_argomento_pagina_varianti: SUPERATO (varianti basse o nessuna parte locale); letture varianti; testi argP1, argP2, argP3
- positivo_argomento_pagina_paragrafo: SUPERATO (il paragrafo non conta); letture paragrafo; testi argP1, argP2, argP3
- positivo_famiglie_profilo: SUPERATO (profilo piatto); letture profilo; testi argF1, argF2
- positivo_famiglie_varianti: SUPERATO (varianti non alte (tante varianti nella pagina, nessuna copia: la parte locale non c'e')); letture varianti; testi argF1, argF2
- positivo_famiglie_paragrafo: SUPERATO (il paragrafo non conta); letture paragrafo; testi argF1, argF2
- positivo_argomento_paragrafo_paragrafo: SUPERATO (il paragrafo conta); letture paragrafo; testi argR1, argR2, argR3
- positivo_argomento_paragrafo_varianti: SUPERATO (varianti basse (le parole del tema tornano uguali)); letture varianti; testi argR1, argR2, argR3
- positivo_tecnica_riparte_paragrafo: SUPERATO (il paragrafo conta); letture paragrafo; testi tecP1
- positivo_tecnica_riparte_varianti: SUPERATO (varianti alte); letture varianti; testi tecP1
- positivo_argomento_che_scorre_pagine: SUPERATO (pagine vicine "si"); letture pagine_vicine; testi argS1
- negativo_pagine_vicine: SUPERATO (pagine vicine non "si" (temi e copie indipendenti da una pagina alla successiva)); letture pagine_vicine; testi argP1, argP2, argP3, argF1, argF2, tecM1, tecM2, tecM3
- positivo_direzione_fine: SUPERATO (direzione "fine"); letture direzione; testi tecCoda1
- positivo_direzione_inizio: SUPERATO (direzione "inizio"); letture direzione; testi tecTesta1
- negativo_direzione: SUPERATO (direzione ne' "inizio" ne' "fine" (modifiche a caso nella parola)); letture direzione; testi tecM1
- sintesi_tecnica: NON SUPERATO (sintesi "tecnica"); letture sintesi; testi tecM1, tecM2, tecM3
- sintesi_argomento_pagina: SUPERATO (sintesi "argomento di pagina"); letture sintesi; testi argP1, argP2, argP3
- sintesi_famiglie: SUPERATO (sintesi "argomento di pagina"); letture sintesi; testi argF1, argF2
- sintesi_argomento_paragrafo: SUPERATO (sintesi "argomento di paragrafo"); letture sintesi; testi argR1, argR2, argR3
- sintesi_tecnica_riparte: SUPERATO (sintesi "tecnica che riparte a ogni paragrafo"); letture sintesi; testi tecP1
- sintesi_argomento_che_scorre: SUPERATO (sintesi "argomento che scorre"); letture sintesi; testi argS1
- sintesi_senza_paragrafo_tecnica: SUPERATO (sintesi senza il paragrafo "tecnica"); letture sintesi_senza_paragrafo; testi tecM1, tecM2, tecM3
- sintesi_senza_paragrafo_argomento_pagina: SUPERATO (sintesi senza il paragrafo "argomento di pagina"); letture sintesi_senza_paragrafo; testi argP1, argP2, argP3, argF1, argF2
- sintesi_senza_paragrafo_argomento_che_scorre: SUPERATO (sintesi senza il paragrafo "argomento che scorre"); letture sintesi_senza_paragrafo; testi argS1
- **lettura valida (i suoi controlli sono superati)**: profilo SI; varianti SI; paragrafo NO; direzione SI; pagine_vicine SI; sintesi NO; sintesi_senza_paragrafo SI
- livelli M (meta') e D (un quarto) dell'eco del Voynich, descrittivi: {"argPm1": {"eco": "misurabile", "profilo": "piatto", "varianti": "nessuna parte locale", "paragrafo": "non conta", "pagine_vicine": "no", "sintesi": "argomento di pagina", "potenza": 0.505}, "argRm1": {"eco": "misurabile", "profilo": "ripido", "varianti": "basse", "paragrafo": "conta", "pagine_vicine": "no", "sintesi": "argomento di paragrafo", "potenza": 0.437}, "argFm1": {"eco": "misurabile", "profilo": "piatto", "varianti": "nessuna parte locale", "paragrafo": "non conta", "pagine_vicine": "no", "sintesi": "argomento di pagina", "potenza": 0.485}, "tecMm1": {"eco": "misurabile", "profilo": "ripido", "varianti": "alte", "paragrafo": "zona grigia", "pagine_vicine": "no", "sintesi": "tecnica", "potenza": 0.527}, "tecPm1": {"eco": "misurabile", "profilo": "ripido", "varianti": "alte", "paragrafo": "zona grigia", "pagine_vicine": "no", "sintesi": "tecnica", "potenza": 0.522}, "argPd1": {"eco": "misurabile", "profilo": "piatto", "varianti": "nessuna parte locale", "paragrafo": "non conta", "pagine_vicine": "no", "sintesi": "argomento di pagina", "potenza": 0.235}, "tecMd1": {"eco": "misurabile", "profilo": "ripido", "varianti": "alte", "paragrafo": "zona grigia", "pagine_vicine": "no", "sintesi": "tecnica", "potenza": 0.257}, "tecPd1": {"eco": "misurabile", "profilo": "ripido", "varianti": "alte", "paragrafo": "non leggibile", "pagine_vicine": "no", "sintesi": "tecnica", "potenza": 0.271}}

## Eco per testo (eccesso di parole simili per parola fonte)

| testo | pagine | eco tutta (rif. sezione) | eco tutta (rif. altra sezione) | eco vicina 0-3 righe (pesi comuni) | eco lontana 4+ (pesi comuni) | H = lontana / vicina | parte locale / eco vicina | quota varianti vicina (grezza) | quota varianti nella parte locale |
|---|---|---|---|---|---|---|---|---|---|
| vere | 202 | +0.0062 (+0.0047; +0.0079) | +0.0098 (+0.0076; +0.0122) | +0.0116 (+0.0099; +0.0134) | +0.0057 (+0.0044; +0.0072) | +0.49 (+0.41; +0.58) | +0.51 (+0.42; +0.59) | +0.74 (+0.72; +0.76) | +0.76 (+0.72; +0.81) |
| a13 | 202 | +0.0063 (+0.0048; +0.0078) | +0.0091 (+0.0070; +0.0115) | +0.0121 (+0.0100; +0.0142) | +0.0062 (+0.0047; +0.0077) | +0.52 (+0.42; +0.62) | +0.48 (+0.38; +0.58) | +0.74 (+0.71; +0.78) | +0.73 (+0.69; +0.78) |
| a14 | 202 | +0.0054 (+0.0037; +0.0071) | +0.0094 (+0.0072; +0.0121) | +0.0093 (+0.0072; +0.0113) | +0.0044 (+0.0028; +0.0059) | +0.47 (+0.32; +0.63) | +0.53 (+0.37; +0.68) | +0.73 (+0.69; +0.76) | +0.72 (+0.66; +0.78) |
| a15 | 202 | +0.0046 (+0.0035; +0.0057) | +0.0084 (+0.0062; +0.0106) | +0.0091 (+0.0076; +0.0107) | +0.0042 (+0.0030; +0.0055) | +0.46 (+0.36; +0.57) | +0.54 (+0.43; +0.64) | +0.75 (+0.71; +0.79) | +0.72 (+0.66; +0.78) |
| a16 | 202 | +0.0053 (+0.0041; +0.0064) | +0.0095 (+0.0076; +0.0117) | +0.0082 (+0.0069; +0.0097) | +0.0043 (+0.0030; +0.0055) | +0.52 (+0.39; +0.64) | +0.48 (+0.36; +0.61) | +0.78 (+0.74; +0.81) | +0.78 (+0.71; +0.85) |
| a17 | 202 | +0.0045 (+0.0034; +0.0056) | +0.0071 (+0.0050; +0.0098) | +0.0098 (+0.0081; +0.0117) | +0.0049 (+0.0038; +0.0063) | +0.50 (+0.40; +0.62) | +0.50 (+0.38; +0.60) | +0.72 (+0.69; +0.75) | +0.69 (+0.62; +0.75) |
| a18 | 202 | +0.0051 (+0.0036; +0.0065) | +0.0092 (+0.0068; +0.0119) | +0.0099 (+0.0075; +0.0122) | +0.0050 (+0.0035; +0.0064) | +0.50 (+0.40; +0.61) | +0.50 (+0.39; +0.60) | +0.72 (+0.69; +0.76) | +0.71 (+0.63; +0.78) |
| a19 | 202 | +0.0057 (+0.0043; +0.0073) | +0.0101 (+0.0077; +0.0126) | +0.0099 (+0.0079; +0.0118) | +0.0044 (+0.0030; +0.0058) | +0.44 (+0.31; +0.59) | +0.56 (+0.41; +0.69) | +0.78 (+0.75; +0.80) | +0.77 (+0.71; +0.82) |
| ts1 | 138 | +0.0425 (+0.0290; +0.0562) | +0.0409 (+0.0283; +0.0541) | +0.0471 (+0.0324; +0.0623) | +0.0419 (+0.0283; +0.0562) | +0.89 (+0.84; +0.93) | +0.11 (+0.07; +0.16) | +0.62 (+0.60; +0.66) | +0.57 (+0.49; +0.67) |
| ts2 | 138 | +0.0425 (+0.0328; +0.0523) | +0.0460 (+0.0352; +0.0572) | +0.0458 (+0.0358; +0.0559) | +0.0407 (+0.0312; +0.0503) | +0.89 (+0.84; +0.93) | +0.11 (+0.07; +0.16) | +0.62 (+0.60; +0.66) | +0.56 (+0.47; +0.66) |
| a21 | 202 | +0.0063 (+0.0045; +0.0081) | +0.0098 (+0.0077; +0.0121) | +0.0111 (+0.0088; +0.0135) | +0.0055 (+0.0037; +0.0075) | +0.50 (+0.38; +0.61) | +0.50 (+0.39; +0.62) | +0.75 (+0.71; +0.79) | +0.79 (+0.74; +0.83) |
| a20 | 202 | +0.0054 (+0.0038; +0.0070) | +0.0093 (+0.0069; +0.0119) | +0.0090 (+0.0070; +0.0112) | +0.0050 (+0.0036; +0.0065) | +0.55 (+0.44; +0.66) | +0.45 (+0.34; +0.56) | +0.75 (+0.72; +0.79) | +0.74 (+0.67; +0.82) |
| a22 | 202 | +0.0049 (+0.0037; +0.0061) | +0.0085 (+0.0063; +0.0112) | +0.0086 (+0.0069; +0.0104) | +0.0044 (+0.0031; +0.0059) | +0.51 (+0.40; +0.63) | +0.49 (+0.37; +0.60) | +0.76 (+0.73; +0.78) | +0.72 (+0.65; +0.78) |
| latino | 196 | +0.0092 (+0.0063; +0.0126) | +0.0108 (+0.0078; +0.0142) | +0.0135 (+0.0102; +0.0171) | +0.0073 (+0.0049; +0.0104) | +0.54 (+0.43; +0.64) | +0.46 (+0.36; +0.57) | +0.32 (+0.24; +0.37) | +0.27 (+0.17; +0.36) |
| italiano | 196 | +0.0046 (+0.0033; +0.0059) | +0.0046 (+0.0033; +0.0059) | +0.0055 (+0.0041; +0.0070) | +0.0036 (+0.0021; +0.0051) | +0.65 (+0.43; +0.92) | +0.35 (+0.08; +0.57) | +0.14 (-0.02; +0.27) | -0.16 (-2.21; +0.28) |
| inglese | 196 | +0.0027 (+0.0018; +0.0037) | +0.0039 (+0.0030; +0.0047) | +0.0046 (+0.0035; +0.0057) | +0.0014 (+0.0005; +0.0025) | +0.31 (+0.11; +0.49) | +0.69 (+0.51; +0.89) | -0.04 (-0.18; +0.07) | +0.00 (-0.23; +0.16) |
| latGeom | 202 | +0.0044 (+0.0030; +0.0060) | +0.0046 (+0.0032; +0.0063) | +0.0084 (+0.0062; +0.0109) | +0.0039 (+0.0027; +0.0052) | +0.46 (+0.39; +0.54) | +0.54 (+0.46; +0.61) | +0.30 (+0.24; +0.34) | +0.27 (+0.18; +0.33) |
| ingGeom | 202 | +0.0023 (+0.0014; +0.0035) | +0.0019 (+0.0011; +0.0026) | +0.0045 (+0.0035; +0.0057) | +0.0022 (+0.0012; +0.0033) | +0.48 (+0.29; +0.65) | +0.52 (+0.35; +0.71) | -0.07 (-0.23; +0.06) | -0.21 (-0.63; +0.00) |
| argP1 | 202 | +0.0116 (+0.0111; +0.0121) | +0.0116 (+0.0109; +0.0122) | +0.0117 (+0.0111; +0.0124) | +0.0117 (+0.0112; +0.0123) | +1.00 (+0.96; +1.04) | -0.00 (-0.04; +0.04) | +0.01 (-0.03; +0.05) | -25.03 (-8.15; +12.72) |
| argP2 | 202 | +0.0108 (+0.0102; +0.0115) | +0.0107 (+0.0102; +0.0112) | +0.0108 (+0.0102; +0.0116) | +0.0111 (+0.0105; +0.0117) | +1.02 (+0.98; +1.08) | -0.02 (-0.08; +0.02) | +0.02 (-0.03; +0.06) | +0.43 (-3.95; +4.25) |
| argP3 | 202 | +0.0109 (+0.0102; +0.0116) | +0.0103 (+0.0094; +0.0112) | +0.0108 (+0.0100; +0.0116) | +0.0111 (+0.0104; +0.0118) | +1.03 (+0.99; +1.07) | -0.03 (-0.07; +0.01) | -0.02 (-0.07; +0.02) | +0.46 (-2.89; +3.48) |
| argR1 | 202 | +0.0041 (+0.0033; +0.0049) | +0.0041 (+0.0033; +0.0049) | +0.0116 (+0.0106; +0.0125) | +0.0024 (+0.0018; +0.0031) | +0.21 (+0.16; +0.26) | +0.79 (+0.74; +0.84) | +0.00 (-0.03; +0.03) | +0.01 (-0.04; +0.05) |
| argR2 | 202 | +0.0040 (+0.0033; +0.0049) | +0.0042 (+0.0035; +0.0050) | +0.0114 (+0.0104; +0.0125) | +0.0026 (+0.0019; +0.0033) | +0.23 (+0.18; +0.28) | +0.77 (+0.72; +0.82) | -0.02 (-0.06; +0.03) | -0.03 (-0.09; +0.03) |
| argR3 | 202 | +0.0036 (+0.0030; +0.0043) | +0.0039 (+0.0032; +0.0046) | +0.0108 (+0.0101; +0.0116) | +0.0021 (+0.0016; +0.0028) | +0.20 (+0.15; +0.25) | +0.80 (+0.75; +0.85) | -0.04 (-0.07; -0.00) | -0.02 (-0.07; +0.03) |
| argS1 | 202 | +0.0069 (+0.0062; +0.0076) | +0.0069 (+0.0062; +0.0078) | +0.0122 (+0.0115; +0.0129) | +0.0063 (+0.0056; +0.0070) | +0.51 (+0.47; +0.56) | +0.49 (+0.44; +0.53) | +0.04 (+0.01; +0.08) | +0.12 (+0.07; +0.18) |
| argF1 | 202 | +0.0120 (+0.0114; +0.0128) | +0.0120 (+0.0113; +0.0127) | +0.0120 (+0.0113; +0.0127) | +0.0120 (+0.0113; +0.0126) | +1.00 (+0.96; +1.04) | +0.00 (-0.04; +0.04) | +0.66 (+0.62; +0.70) | +7.54 (-6.56; +6.93) |
| argF2 | 202 | +0.0122 (+0.0115; +0.0129) | +0.0122 (+0.0116; +0.0128) | +0.0124 (+0.0117; +0.0130) | +0.0122 (+0.0116; +0.0128) | +0.99 (+0.95; +1.02) | +0.01 (-0.02; +0.05) | +0.67 (+0.63; +0.70) | +0.72 (-2.78; +4.45) |
| tecM1 | 202 | +0.0028 (+0.0022; +0.0036) | +0.0025 (+0.0019; +0.0032) | +0.0111 (+0.0105; +0.0118) | +0.0005 (-0.0001; +0.0012) | +0.05 (-0.01; +0.10) | +0.95 (+0.90; +1.01) | +0.62 (+0.59; +0.64) | +0.61 (+0.58; +0.63) |
| tecM2 | 202 | +0.0029 (+0.0022; +0.0038) | +0.0031 (+0.0025; +0.0038) | +0.0112 (+0.0104; +0.0122) | +0.0008 (+0.0001; +0.0014) | +0.07 (+0.01; +0.12) | +0.93 (+0.88; +0.99) | +0.63 (+0.61; +0.65) | +0.63 (+0.61; +0.65) |
| tecM3 | 202 | +0.0026 (+0.0022; +0.0032) | +0.0021 (+0.0016; +0.0027) | +0.0105 (+0.0098; +0.0112) | +0.0005 (+0.0000; +0.0010) | +0.05 (+0.00; +0.10) | +0.95 (+0.90; +1.00) | +0.62 (+0.60; +0.64) | +0.62 (+0.58; +0.64) |
| tecP1 | 202 | +0.0031 (+0.0025; +0.0036) | +0.0027 (+0.0022; +0.0034) | +0.0112 (+0.0103; +0.0122) | +0.0007 (+0.0002; +0.0012) | +0.06 (+0.02; +0.11) | +0.94 (+0.89; +0.98) | +0.64 (+0.62; +0.67) | +0.64 (+0.61; +0.66) |
| tecCoda1 | 202 | +0.0031 (+0.0025; +0.0038) | +0.0029 (+0.0023; +0.0036) | +0.0128 (+0.0121; +0.0135) | +0.0007 (+0.0002; +0.0012) | +0.05 (+0.01; +0.09) | +0.95 (+0.91; +0.99) | +0.66 (+0.64; +0.68) | +0.66 (+0.63; +0.67) |
| tecTesta1 | 202 | +0.0031 (+0.0025; +0.0038) | +0.0027 (+0.0019; +0.0035) | +0.0118 (+0.0110; +0.0128) | +0.0006 (+0.0000; +0.0012) | +0.05 (+0.00; +0.10) | +0.95 (+0.90; +1.00) | +0.65 (+0.62; +0.67) | +0.64 (+0.61; +0.67) |
| argPm1 | 202 | +0.0055 (+0.0050; +0.0060) | +0.0051 (+0.0047; +0.0055) | +0.0059 (+0.0052; +0.0065) | +0.0055 (+0.0049; +0.0060) | +0.93 (+0.86; +1.03) | +0.07 (-0.03; +0.14) | +0.06 (-0.03; +0.14) | +0.69 (-1.37; +2.35) |
| argRm1 | 202 | +0.0018 (+0.0014; +0.0022) | +0.0021 (+0.0018; +0.0026) | +0.0051 (+0.0045; +0.0057) | +0.0011 (+0.0007; +0.0016) | +0.22 (+0.15; +0.31) | +0.78 (+0.69; +0.85) | -0.07 (-0.16; +0.00) | -0.07 (-0.20; +0.03) |
| argFm1 | 202 | +0.0057 (+0.0052; +0.0062) | +0.0053 (+0.0048; +0.0059) | +0.0056 (+0.0050; +0.0062) | +0.0056 (+0.0051; +0.0061) | +0.99 (+0.91; +1.08) | +0.01 (-0.08; +0.09) | +0.64 (+0.60; +0.69) | -0.52 (-4.33; +6.50) |
| tecMm1 | 202 | +0.0014 (+0.0010; +0.0019) | +0.0014 (+0.0009; +0.0020) | +0.0061 (+0.0055; +0.0068) | +0.0003 (-0.0001; +0.0008) | +0.05 (-0.02; +0.13) | +0.95 (+0.87; +1.02) | +0.60 (+0.57; +0.64) | +0.60 (+0.56; +0.64) |
| tecPm1 | 202 | +0.0013 (+0.0009; +0.0019) | +0.0013 (+0.0009; +0.0017) | +0.0060 (+0.0055; +0.0067) | -0.0001 (-0.0006; +0.0004) | -0.01 (-0.10; +0.07) | +1.01 (+0.93; +1.10) | +0.60 (+0.56; +0.64) | +0.59 (+0.55; +0.63) |
| argPd1 | 202 | +0.0027 (+0.0023; +0.0032) | +0.0023 (+0.0019; +0.0027) | +0.0027 (+0.0022; +0.0032) | +0.0025 (+0.0020; +0.0030) | +0.90 (+0.73; +1.11) | +0.10 (-0.11; +0.27) | -0.02 (-0.19; +0.10) | +1.07 (-1.55; +5.38) |
| tecMd1 | 202 | +0.0003 (-0.0001; +0.0009) | +0.0007 (+0.0004; +0.0012) | +0.0030 (+0.0024; +0.0037) | -0.0003 (-0.0009; +0.0002) | -0.11 (-0.32; +0.06) | +1.11 (+0.94; +1.32) | +0.56 (+0.48; +0.63) | +0.59 (+0.51; +0.66) |
| tecPd1 | 202 | +0.0006 (+0.0002; +0.0010) | +0.0010 (+0.0006; +0.0014) | +0.0031 (+0.0026; +0.0037) | -0.0002 (-0.0006; +0.0002) | -0.06 (-0.19; +0.07) | +1.06 (+0.93; +1.19) | +0.59 (+0.52; +0.66) | +0.59 (+0.51; +0.67) |
| vere~t1 | 202 | +0.0002 (-0.0003; +0.0006) | -0.0002 (-0.0007; +0.0002) | +0.0001 (-0.0004; +0.0006) | +0.0001 (-0.0003; +0.0006) | +1.48 (-10.05; +8.21) | -0.48 (-7.21; +11.05) | +1.35 (-3.88; +6.91) | -0.67 (-3.79; +7.02) |
| vere~t2 | 202 | -0.0002 (-0.0005; +0.0002) | +0.0001 (-0.0004; +0.0006) | +0.0001 (-0.0004; +0.0007) | +0.0001 (-0.0003; +0.0005) | +0.74 (-8.85; +8.07) | +0.26 (-7.07; +9.85) | +0.62 (-3.00; +5.20) | +2.26 (-4.46; +4.11) |
| vere~t3 | 202 | -0.0003 (-0.0006; +0.0000) | -0.0000 (-0.0004; +0.0003) | -0.0003 (-0.0007; +0.0001) | -0.0004 (-0.0008; +0.0000) | +1.06 (-4.71; +7.16) | -0.06 (-6.16; +5.71) | +0.66 (-1.06; +2.08) | +2.49 (-3.02; +5.82) |
| ts1~t | 138 | +0.0002 (-0.0004; +0.0008) | +0.0004 (-0.0001; +0.0010) | +0.0003 (-0.0004; +0.0009) | +0.0002 (-0.0004; +0.0008) | +0.63 (-8.98; +12.23) | +0.37 (-11.23; +9.98) | +0.77 (-1.63; +3.82) | +0.38 (-3.40; +4.26) |
| vere~t4 | 202 | -0.0001 (-0.0006; +0.0004) | -0.0002 (-0.0007; +0.0002) | -0.0001 (-0.0006; +0.0004) | -0.0002 (-0.0007; +0.0003) | +2.41 (-14.52; +12.57) | -1.41 (-11.57; +15.52) | +1.49 (-1.86; +5.73) | +0.74 (-3.20; +5.05) |
| vere~t5 | 202 | +0.0003 (-0.0001; +0.0007) | -0.0000 (-0.0005; +0.0005) | +0.0004 (-0.0002; +0.0009) | +0.0002 (-0.0003; +0.0006) | +0.45 (-2.70; +4.31) | +0.55 (-3.31; +3.70) | +0.83 (-0.52; +2.94) | +0.77 (-2.34; +3.53) |
| a13~t | 202 | +0.0003 (-0.0001; +0.0007) | +0.0004 (+0.0000; +0.0008) | +0.0004 (-0.0001; +0.0009) | +0.0004 (-0.0001; +0.0008) | +0.96 (-2.93; +5.90) | +0.04 (-4.90; +3.93) | +0.38 (-2.60; +4.45) | -12.31 (-13.01; +11.87) |
| argP1~t | 202 | -0.0001 (-0.0004; +0.0002) | -0.0001 (-0.0004; +0.0002) | -0.0001 (-0.0004; +0.0002) | -0.0000 (-0.0004; +0.0003) | +0.40 (-8.39; +14.57) | +0.60 (-13.57; +9.39) | +1.08 (-1.80; +3.72) | +1.06 (-3.78; +4.46) |
| tecM1~t | 202 | +0.0001 (-0.0004; +0.0005) | -0.0006 (-0.0011; -0.0000) | +0.0004 (-0.0001; +0.0009) | -0.0001 (-0.0005; +0.0003) | -0.25 (-6.10; +5.10) | +1.25 (-4.10; +7.10) | +0.99 (+0.05; +2.06) | +1.10 (+0.63; +2.51) |
| argF1~t | 202 | +0.0002 (-0.0000; +0.0004) | -0.0000 (-0.0003; +0.0002) | +0.0003 (-0.0000; +0.0007) | +0.0001 (-0.0002; +0.0004) | +0.41 (-1.68; +3.13) | +0.59 (-2.13; +2.68) | +0.98 (+0.16; +2.29) | +1.21 (-1.75; +4.76) |
| latino~t | 196 | +0.0002 (-0.0001; +0.0005) | +0.0000 (-0.0003; +0.0004) | +0.0000 (-0.0003; +0.0004) | +0.0003 (-0.0001; +0.0006) | +17.22 (-21.01; +25.75) | -16.22 (-24.75; +22.01) | +3.58 (-6.06; +6.70) | +0.43 (-3.42; +4.19) |
| inglese~t | 196 | +0.0000 (-0.0006; +0.0007) | -0.0000 (-0.0007; +0.0007) | -0.0002 (-0.0009; +0.0005) | +0.0004 (-0.0003; +0.0012) | -1.79 (-16.93; +20.96) | +2.79 (-19.96; +17.93) | +0.88 (-3.51; +6.63) | +0.67 (-0.67; +2.88) |
| ts1~p | 138 | +0.0425 (+0.0292; +0.0560) | +0.0409 (+0.0283; +0.0542) | +0.0426 (+0.0290; +0.0565) | +0.0435 (+0.0298; +0.0576) | +1.02 (+0.99; +1.04) | -0.02 (-0.04; +0.01) | +0.63 (+0.60; +0.67) | +0.38 (-2.16; +2.38) |
| italiano~t | 196 | -0.0003 (-0.0013; +0.0006) | +0.0001 (-0.0009; +0.0010) | -0.0001 (-0.0011; +0.0010) | -0.0004 (-0.0016; +0.0007) | +8.40 (-19.64; +19.59) | -7.40 (-18.59; +20.64) | +2.11 (-6.50; +6.33) | +0.41 (-2.82; +4.10) |
| vere~p | 202 | +0.0064 (+0.0050; +0.0081) | +0.0097 (+0.0075; +0.0120) | +0.0075 (+0.0059; +0.0091) | +0.0073 (+0.0059; +0.0088) | +0.97 (+0.90; +1.06) | +0.03 (-0.06; +0.10) | +0.75 (+0.72; +0.78) | +1.30 (-3.44; +4.62) |
| a13~p | 202 | +0.0060 (+0.0046; +0.0074) | +0.0090 (+0.0069; +0.0114) | +0.0069 (+0.0054; +0.0083) | +0.0073 (+0.0058; +0.0089) | +1.06 (+0.96; +1.17) | -0.06 (-0.17; +0.04) | +0.77 (+0.72; +0.82) | +0.23 (-3.57; +3.69) |
| argP1~p | 202 | +0.0117 (+0.0112; +0.0122) | +0.0116 (+0.0110; +0.0123) | +0.0116 (+0.0110; +0.0123) | +0.0117 (+0.0111; +0.0123) | +1.00 (+0.96; +1.04) | -0.00 (-0.04; +0.04) | -0.01 (-0.05; +0.02) | +3.66 (-8.09; +13.74) |
| tecM1~p | 202 | +0.0028 (+0.0022; +0.0034) | +0.0025 (+0.0018; +0.0031) | +0.0036 (+0.0030; +0.0044) | +0.0036 (+0.0029; +0.0043) | +0.98 (+0.85; +1.14) | +0.02 (-0.14; +0.15) | +0.62 (+0.57; +0.67) | +0.56 (-3.58; +4.64) |
| argF1~p | 202 | +0.0119 (+0.0112; +0.0126) | +0.0118 (+0.0111; +0.0124) | +0.0120 (+0.0113; +0.0127) | +0.0119 (+0.0112; +0.0125) | +0.99 (+0.95; +1.04) | +0.01 (-0.04; +0.05) | +0.64 (+0.60; +0.68) | -1.47 (-7.03; +8.73) |
| italiano~p | 196 | +0.0043 (+0.0030; +0.0057) | +0.0048 (+0.0035; +0.0062) | +0.0046 (+0.0031; +0.0060) | +0.0040 (+0.0027; +0.0055) | +0.88 (+0.65; +1.20) | +0.12 (-0.20; +0.35) | +0.23 (-0.01; +0.37) | +0.72 (-3.34; +2.97) |
| inglese~p | 196 | +0.0028 (+0.0020; +0.0037) | +0.0036 (+0.0027; +0.0044) | +0.0028 (+0.0019; +0.0039) | +0.0030 (+0.0021; +0.0040) | +1.06 (+0.80; +1.43) | -0.06 (-0.43; +0.20) | -0.06 (-0.31; +0.13) | -0.39 (-5.35; +7.57) |
| latino~p | 196 | +0.0092 (+0.0063; +0.0126) | +0.0109 (+0.0079; +0.0143) | +0.0092 (+0.0065; +0.0123) | +0.0092 (+0.0065; +0.0126) | +1.00 (+0.94; +1.07) | -0.00 (-0.07; +0.06) | +0.33 (+0.24; +0.40) | +6.24 (-9.44; +7.70) |

## Parte locale dell'eco: uguali e varianti (vicino meno lontano, pesi comuni)

| testo | parte locale | di cui uguali | di cui varianti |
|---|---|---|---|
| vere | +0.0059 (+0.0047; +0.0069) | +0.0014 (+0.0010; +0.0017) | +0.0045 (+0.0035; +0.0053) |
| a13 | +0.0058 (+0.0042; +0.0075) | +0.0016 (+0.0011; +0.0021) | +0.0043 (+0.0031; +0.0055) |
| a14 | +0.0049 (+0.0031; +0.0068) | +0.0013 (+0.0008; +0.0019) | +0.0035 (+0.0022; +0.0051) |
| a15 | +0.0049 (+0.0037; +0.0061) | +0.0014 (+0.0009; +0.0018) | +0.0035 (+0.0026; +0.0044) |
| a16 | +0.0039 (+0.0028; +0.0052) | +0.0009 (+0.0005; +0.0012) | +0.0031 (+0.0021; +0.0041) |
| a17 | +0.0049 (+0.0034; +0.0065) | +0.0015 (+0.0010; +0.0021) | +0.0034 (+0.0023; +0.0045) |
| a18 | +0.0050 (+0.0032; +0.0066) | +0.0015 (+0.0009; +0.0021) | +0.0035 (+0.0022; +0.0048) |
| a19 | +0.0055 (+0.0036; +0.0076) | +0.0013 (+0.0008; +0.0017) | +0.0043 (+0.0027; +0.0059) |
| ts1 | +0.0052 (+0.0030; +0.0074) | +0.0022 (+0.0011; +0.0034) | +0.0029 (+0.0017; +0.0042) |
| ts2 | +0.0050 (+0.0028; +0.0078) | +0.0022 (+0.0011; +0.0035) | +0.0028 (+0.0016; +0.0043) |
| a21 | +0.0056 (+0.0040; +0.0073) | +0.0012 (+0.0008; +0.0016) | +0.0044 (+0.0032; +0.0058) |
| a20 | +0.0040 (+0.0027; +0.0055) | +0.0010 (+0.0006; +0.0016) | +0.0030 (+0.0020; +0.0040) |
| a22 | +0.0042 (+0.0031; +0.0053) | +0.0012 (+0.0008; +0.0015) | +0.0030 (+0.0021; +0.0039) |
| latino | +0.0061 (+0.0047; +0.0078) | +0.0045 (+0.0034; +0.0056) | +0.0017 (+0.0009; +0.0025) |
| italiano | +0.0019 (+0.0004; +0.0033) | +0.0022 (+0.0013; +0.0032) | -0.0003 (-0.0014; +0.0007) |
| inglese | +0.0031 (+0.0022; +0.0041) | +0.0031 (+0.0024; +0.0039) | +0.0000 (-0.0005; +0.0006) |
| latGeom | +0.0045 (+0.0031; +0.0061) | +0.0033 (+0.0024; +0.0043) | +0.0012 (+0.0006; +0.0019) |
| ingGeom | +0.0024 (+0.0015; +0.0033) | +0.0029 (+0.0021; +0.0037) | -0.0005 (-0.0010; +0.0000) |
| argP1 | -0.0000 (-0.0004; +0.0005) | -0.0002 (-0.0005; +0.0002) | +0.0002 (-0.0002; +0.0005) |
| argP2 | -0.0003 (-0.0008; +0.0002) | -0.0002 (-0.0005; +0.0002) | -0.0001 (-0.0005; +0.0003) |
| argP3 | -0.0003 (-0.0008; +0.0001) | -0.0002 (-0.0005; +0.0002) | -0.0001 (-0.0005; +0.0002) |
| argR1 | +0.0091 (+0.0085; +0.0098) | +0.0091 (+0.0085; +0.0096) | +0.0001 (-0.0003; +0.0005) |
| argR2 | +0.0088 (+0.0080; +0.0097) | +0.0091 (+0.0085; +0.0096) | -0.0002 (-0.0007; +0.0003) |
| argR3 | +0.0086 (+0.0080; +0.0093) | +0.0088 (+0.0082; +0.0093) | -0.0001 (-0.0006; +0.0003) |
| argS1 | +0.0059 (+0.0053; +0.0066) | +0.0052 (+0.0046; +0.0058) | +0.0007 (+0.0004; +0.0011) |
| argF1 | +0.0000 (-0.0004; +0.0005) | -0.0001 (-0.0003; +0.0001) | +0.0001 (-0.0003; +0.0005) |
| argF2 | +0.0002 (-0.0003; +0.0007) | +0.0000 (-0.0002; +0.0003) | +0.0001 (-0.0003; +0.0006) |
| tecM1 | +0.0106 (+0.0099; +0.0113) | +0.0041 (+0.0039; +0.0044) | +0.0065 (+0.0059; +0.0071) |
| tecM2 | +0.0105 (+0.0097; +0.0112) | +0.0039 (+0.0037; +0.0041) | +0.0066 (+0.0060; +0.0072) |
| tecM3 | +0.0100 (+0.0092; +0.0108) | +0.0038 (+0.0035; +0.0042) | +0.0061 (+0.0054; +0.0068) |
| tecP1 | +0.0105 (+0.0096; +0.0115) | +0.0038 (+0.0035; +0.0042) | +0.0067 (+0.0060; +0.0074) |
| tecCoda1 | +0.0121 (+0.0113; +0.0129) | +0.0042 (+0.0039; +0.0044) | +0.0079 (+0.0073; +0.0086) |
| tecTesta1 | +0.0112 (+0.0103; +0.0121) | +0.0041 (+0.0037; +0.0044) | +0.0072 (+0.0064; +0.0079) |
| argPm1 | +0.0004 (-0.0001; +0.0009) | +0.0001 (-0.0001; +0.0004) | +0.0003 (-0.0001; +0.0007) |
| argRm1 | +0.0039 (+0.0034; +0.0045) | +0.0042 (+0.0038; +0.0046) | -0.0003 (-0.0007; +0.0001) |
| argFm1 | +0.0001 (-0.0004; +0.0006) | +0.0001 (-0.0001; +0.0003) | -0.0000 (-0.0005; +0.0004) |
| tecMm1 | +0.0058 (+0.0052; +0.0065) | +0.0023 (+0.0021; +0.0025) | +0.0035 (+0.0029; +0.0041) |
| tecPm1 | +0.0061 (+0.0055; +0.0068) | +0.0025 (+0.0023; +0.0027) | +0.0036 (+0.0031; +0.0042) |
| argPd1 | +0.0003 (-0.0003; +0.0008) | -0.0000 (-0.0002; +0.0002) | +0.0003 (-0.0002; +0.0007) |
| tecMd1 | +0.0033 (+0.0027; +0.0040) | +0.0014 (+0.0012; +0.0016) | +0.0020 (+0.0014; +0.0025) |
| tecPd1 | +0.0033 (+0.0026; +0.0040) | +0.0013 (+0.0011; +0.0016) | +0.0020 (+0.0014; +0.0025) |
| vere~t1 | -0.0000 (-0.0006; +0.0005) | -0.0001 (-0.0003; +0.0001) | +0.0000 (-0.0004; +0.0005) |
| vere~t2 | +0.0000 (-0.0005; +0.0005) | -0.0000 (-0.0002; +0.0002) | +0.0001 (-0.0004; +0.0005) |
| vere~t3 | +0.0000 (-0.0004; +0.0005) | -0.0000 (-0.0002; +0.0002) | +0.0001 (-0.0003; +0.0005) |
| ts1~t | +0.0001 (-0.0005; +0.0008) | +0.0001 (-0.0002; +0.0003) | +0.0000 (-0.0005; +0.0006) |
| vere~t4 | +0.0001 (-0.0004; +0.0007) | +0.0000 (-0.0002; +0.0002) | +0.0001 (-0.0004; +0.0006) |
| vere~t5 | +0.0002 (-0.0003; +0.0008) | +0.0000 (-0.0001; +0.0002) | +0.0002 (-0.0003; +0.0007) |
| a13~t | +0.0000 (-0.0005; +0.0005) | +0.0002 (+0.0001; +0.0004) | -0.0002 (-0.0007; +0.0002) |
| argP1~t | -0.0001 (-0.0005; +0.0003) | +0.0000 (-0.0001; +0.0001) | -0.0001 (-0.0005; +0.0003) |
| tecM1~t | +0.0004 (+0.0000; +0.0009) | -0.0000 (-0.0002; +0.0001) | +0.0005 (+0.0001; +0.0009) |
| argF1~t | +0.0002 (-0.0002; +0.0006) | -0.0000 (-0.0001; +0.0001) | +0.0002 (-0.0001; +0.0006) |
| latino~t | -0.0002 (-0.0007; +0.0002) | -0.0001 (-0.0004; +0.0001) | -0.0001 (-0.0004; +0.0002) |
| inglese~t | -0.0007 (-0.0015; +0.0001) | -0.0002 (-0.0008; +0.0003) | -0.0005 (-0.0010; +0.0001) |
| ts1~p | -0.0008 (-0.0018; +0.0002) | -0.0005 (-0.0010; +0.0000) | -0.0003 (-0.0010; +0.0004) |
| italiano~t | +0.0004 (-0.0009; +0.0018) | +0.0002 (-0.0003; +0.0008) | +0.0002 (-0.0009; +0.0013) |
| vere~p | +0.0002 (-0.0004; +0.0008) | -0.0001 (-0.0003; +0.0002) | +0.0003 (-0.0003; +0.0008) |
| a13~p | -0.0004 (-0.0011; +0.0003) | -0.0003 (-0.0006; -0.0000) | -0.0001 (-0.0007; +0.0005) |
| argP1~p | -0.0001 (-0.0005; +0.0005) | +0.0001 (-0.0002; +0.0004) | -0.0002 (-0.0006; +0.0002) |
| tecM1~p | +0.0001 (-0.0005; +0.0006) | +0.0000 (-0.0002; +0.0002) | +0.0000 (-0.0005; +0.0006) |
| argF1~p | +0.0001 (-0.0005; +0.0006) | +0.0002 (-0.0000; +0.0004) | -0.0001 (-0.0005; +0.0004) |
| italiano~p | +0.0005 (-0.0007; +0.0017) | +0.0001 (-0.0004; +0.0007) | +0.0004 (-0.0006; +0.0014) |
| inglese~p | -0.0002 (-0.0010; +0.0006) | -0.0002 (-0.0008; +0.0003) | +0.0001 (-0.0006; +0.0006) |
| latino~p | -0.0000 (-0.0006; +0.0006) | +0.0001 (-0.0003; +0.0006) | -0.0002 (-0.0006; +0.0003) |

## Eco per banda di distanza (rif. sezione): tutti i simili / uguali / varianti

| testo | D0 | D1 | D2 | D4 | D8 |
|---|---|---|---|---|---|
| vere | +0.0176 / +0.0046 / +0.0131 | +0.0131 / +0.0032 / +0.0099 | +0.0097 / +0.0026 / +0.0071 | +0.0071 / +0.0021 / +0.0050 | +0.0041 / +0.0012 / +0.0028 |
| a13 | +0.0241 / +0.0065 / +0.0176 | +0.0120 / +0.0033 / +0.0087 | +0.0088 / +0.0022 / +0.0066 | +0.0072 / +0.0018 / +0.0055 | +0.0042 / +0.0008 / +0.0034 |
| a14 | +0.0192 / +0.0049 / +0.0143 | +0.0104 / +0.0029 / +0.0075 | +0.0067 / +0.0019 / +0.0047 | +0.0050 / +0.0012 / +0.0038 | +0.0041 / +0.0009 / +0.0032 |
| a15 | +0.0190 / +0.0044 / +0.0146 | +0.0100 / +0.0025 / +0.0075 | +0.0059 / +0.0016 / +0.0043 | +0.0049 / +0.0011 / +0.0038 | +0.0030 / +0.0005 / +0.0024 |
| a16 | +0.0155 / +0.0036 / +0.0118 | +0.0101 / +0.0025 / +0.0076 | +0.0062 / +0.0013 / +0.0049 | +0.0047 / +0.0010 / +0.0037 | +0.0044 / +0.0008 / +0.0036 |
| a17 | +0.0227 / +0.0066 / +0.0161 | +0.0105 / +0.0027 / +0.0078 | +0.0065 / +0.0018 / +0.0047 | +0.0047 / +0.0014 / +0.0033 | +0.0024 / +0.0004 / +0.0020 |
| a18 | +0.0180 / +0.0048 / +0.0132 | +0.0108 / +0.0030 / +0.0078 | +0.0070 / +0.0020 / +0.0050 | +0.0054 / +0.0014 / +0.0041 | +0.0033 / +0.0008 / +0.0026 |
| a19 | +0.0244 / +0.0058 / +0.0186 | +0.0106 / +0.0026 / +0.0080 | +0.0065 / +0.0013 / +0.0051 | +0.0050 / +0.0012 / +0.0038 | +0.0044 / +0.0008 / +0.0036 |
| ts1 | +0.0523 / +0.0187 / +0.0336 | +0.0514 / +0.0187 / +0.0328 | +0.0451 / +0.0173 / +0.0278 | +0.0451 / +0.0170 / +0.0281 | +0.0392 / +0.0143 / +0.0249 |
| ts2 | +0.0525 / +0.0182 / +0.0343 | +0.0509 / +0.0188 / +0.0322 | +0.0455 / +0.0172 / +0.0283 | +0.0436 / +0.0163 / +0.0273 | +0.0398 / +0.0145 / +0.0253 |
| a21 | +0.0225 / +0.0056 / +0.0170 | +0.0129 / +0.0035 / +0.0093 | +0.0081 / +0.0019 / +0.0062 | +0.0059 / +0.0016 / +0.0043 | +0.0046 / +0.0011 / +0.0036 |
| a20 | +0.0181 / +0.0049 / +0.0132 | +0.0100 / +0.0025 / +0.0075 | +0.0065 / +0.0015 / +0.0050 | +0.0051 / +0.0013 / +0.0038 | +0.0043 / +0.0010 / +0.0033 |
| a22 | +0.0173 / +0.0039 / +0.0134 | +0.0103 / +0.0024 / +0.0079 | +0.0060 / +0.0016 / +0.0044 | +0.0051 / +0.0011 / +0.0040 | +0.0035 / +0.0006 / +0.0028 |
| latino | +0.0141 / +0.0096 / +0.0046 | +0.0160 / +0.0111 / +0.0049 | +0.0127 / +0.0087 / +0.0040 | +0.0095 / +0.0060 / +0.0035 | +0.0060 / +0.0038 / +0.0022 |
| italiano | +0.0030 / +0.0023 / +0.0007 | +0.0065 / +0.0062 / +0.0004 | +0.0060 / +0.0047 / +0.0013 | +0.0046 / +0.0032 / +0.0014 | +0.0023 / +0.0015 / +0.0008 |
| inglese | +0.0017 / +0.0030 / -0.0014 | +0.0055 / +0.0059 / -0.0004 | +0.0047 / +0.0047 / +0.0000 | +0.0019 / +0.0022 / -0.0003 | +0.0004 / +0.0007 / -0.0003 |
| latGeom | +0.0101 / +0.0069 / +0.0032 | +0.0109 / +0.0077 / +0.0032 | +0.0077 / +0.0054 / +0.0023 | +0.0058 / +0.0038 / +0.0020 | +0.0024 / +0.0018 / +0.0006 |
| ingGeom | -0.0015 / +0.0005 / -0.0020 | +0.0064 / +0.0066 / -0.0002 | +0.0051 / +0.0051 / +0.0000 | +0.0034 / +0.0032 / +0.0002 | +0.0013 / +0.0010 / +0.0003 |
| argP1 | +0.0122 / +0.0117 / +0.0005 | +0.0117 / +0.0115 / +0.0002 | +0.0116 / +0.0116 / +0.0000 | +0.0115 / +0.0116 / -0.0000 | +0.0116 / +0.0116 / +0.0001 |
| argP2 | +0.0117 / +0.0115 / +0.0002 | +0.0108 / +0.0106 / +0.0002 | +0.0107 / +0.0106 / +0.0001 | +0.0112 / +0.0108 / +0.0003 | +0.0107 / +0.0106 / +0.0002 |
| argP3 | +0.0097 / +0.0110 / -0.0012 | +0.0108 / +0.0110 / -0.0002 | +0.0110 / +0.0110 / -0.0001 | +0.0114 / +0.0111 / +0.0003 | +0.0108 / +0.0109 / -0.0002 |
| argR1 | +0.0163 / +0.0164 / -0.0001 | +0.0137 / +0.0137 / -0.0001 | +0.0096 / +0.0096 / +0.0000 | +0.0047 / +0.0047 / +0.0001 | +0.0014 / +0.0012 / +0.0002 |
| argR2 | +0.0156 / +0.0163 / -0.0008 | +0.0138 / +0.0139 / -0.0001 | +0.0100 / +0.0099 / +0.0001 | +0.0051 / +0.0048 / +0.0003 | +0.0011 / +0.0012 / -0.0001 |
| argR3 | +0.0165 / +0.0163 / +0.0002 | +0.0139 / +0.0141 / -0.0002 | +0.0085 / +0.0092 / -0.0006 | +0.0045 / +0.0046 / -0.0002 | +0.0009 / +0.0010 / -0.0001 |
| argS1 | +0.0135 / +0.0130 / +0.0006 | +0.0127 / +0.0123 / +0.0004 | +0.0118 / +0.0115 / +0.0004 | +0.0096 / +0.0097 / -0.0000 | +0.0043 / +0.0045 / -0.0002 |
| argF1 | +0.0112 / +0.0038 / +0.0073 | +0.0120 / +0.0041 / +0.0079 | +0.0122 / +0.0041 / +0.0081 | +0.0121 / +0.0042 / +0.0079 | +0.0121 / +0.0044 / +0.0077 |
| argF2 | +0.0117 / +0.0039 / +0.0077 | +0.0128 / +0.0041 / +0.0087 | +0.0122 / +0.0041 / +0.0081 | +0.0123 / +0.0041 / +0.0083 | +0.0121 / +0.0039 / +0.0082 |
| tecM1 | +0.0274 / +0.0114 / +0.0160 | +0.0174 / +0.0066 / +0.0108 | +0.0067 / +0.0023 / +0.0044 | +0.0010 / +0.0003 / +0.0007 | +0.0001 / -0.0000 / +0.0001 |
| tecM2 | +0.0282 / +0.0110 / +0.0172 | +0.0175 / +0.0064 / +0.0111 | +0.0062 / +0.0020 / +0.0041 | +0.0014 / +0.0006 / +0.0009 | +0.0002 / +0.0001 / +0.0001 |
| tecM3 | +0.0267 / +0.0103 / +0.0164 | +0.0164 / +0.0061 / +0.0104 | +0.0060 / +0.0021 / +0.0039 | +0.0008 / +0.0003 / +0.0005 | +0.0001 / -0.0000 / +0.0001 |
| tecP1 | +0.0323 / +0.0122 / +0.0201 | +0.0165 / +0.0060 / +0.0105 | +0.0047 / +0.0015 / +0.0032 | +0.0012 / +0.0003 / +0.0009 | +0.0006 / +0.0001 / +0.0005 |
| tecCoda1 | +0.0286 / +0.0109 / +0.0177 | +0.0190 / +0.0066 / +0.0124 | +0.0081 / +0.0022 / +0.0059 | +0.0017 / +0.0004 / +0.0013 | -0.0002 / -0.0001 / -0.0002 |
| tecTesta1 | +0.0294 / +0.0107 / +0.0187 | +0.0184 / +0.0066 / +0.0118 | +0.0074 / +0.0023 / +0.0051 | +0.0016 / +0.0004 / +0.0012 | -0.0000 / -0.0000 / +0.0000 |
| argPm1 | +0.0064 / +0.0058 / +0.0005 | +0.0060 / +0.0057 / +0.0003 | +0.0058 / +0.0054 / +0.0004 | +0.0055 / +0.0053 / +0.0002 | +0.0054 / +0.0054 / -0.0001 |
| argRm1 | +0.0067 / +0.0073 / -0.0007 | +0.0065 / +0.0067 / -0.0002 | +0.0042 / +0.0046 / -0.0003 | +0.0022 / +0.0023 / -0.0001 | +0.0005 / +0.0005 / +0.0000 |
| argFm1 | +0.0054 / +0.0020 / +0.0034 | +0.0058 / +0.0019 / +0.0039 | +0.0057 / +0.0019 / +0.0038 | +0.0057 / +0.0019 / +0.0037 | +0.0057 / +0.0020 / +0.0038 |
| tecMm1 | +0.0145 / +0.0060 / +0.0085 | +0.0092 / +0.0035 / +0.0057 | +0.0033 / +0.0013 / +0.0020 | +0.0006 / +0.0002 / +0.0003 | -0.0000 / -0.0000 / +0.0000 |
| tecPm1 | +0.0176 / +0.0073 / +0.0103 | +0.0092 / +0.0037 / +0.0054 | +0.0022 / +0.0008 / +0.0014 | +0.0003 / +0.0000 / +0.0003 | -0.0001 / -0.0000 / -0.0000 |
| argPd1 | +0.0025 / +0.0028 / -0.0003 | +0.0028 / +0.0029 / -0.0001 | +0.0027 / +0.0027 / +0.0000 | +0.0025 / +0.0029 / -0.0004 | +0.0028 / +0.0029 / -0.0001 |
| tecMd1 | +0.0070 / +0.0034 / +0.0036 | +0.0046 / +0.0019 / +0.0027 | +0.0017 / +0.0006 / +0.0010 | -0.0004 / -0.0001 / -0.0004 | -0.0004 / -0.0000 / -0.0004 |
| tecPd1 | +0.0098 / +0.0041 / +0.0057 | +0.0047 / +0.0020 / +0.0027 | +0.0011 / +0.0004 / +0.0007 | -0.0004 / -0.0001 / -0.0004 | -0.0001 / -0.0000 / -0.0000 |
| vere~t1 | +0.0002 / -0.0001 / +0.0003 | +0.0003 / -0.0000 / +0.0003 | -0.0002 / -0.0001 / -0.0001 | +0.0004 / +0.0000 / +0.0004 | +0.0001 / +0.0000 / +0.0001 |
| vere~t2 | -0.0001 / -0.0006 / +0.0005 | +0.0003 / +0.0001 / +0.0002 | +0.0002 / +0.0002 / +0.0001 | +0.0004 / +0.0001 / +0.0002 | -0.0004 / -0.0000 / -0.0004 |
| vere~t3 | -0.0004 / -0.0004 / +0.0000 | -0.0009 / -0.0002 / -0.0007 | -0.0002 / -0.0000 / -0.0001 | -0.0002 / -0.0001 / -0.0001 | -0.0003 / -0.0001 / -0.0002 |
| ts1~t | +0.0003 / +0.0004 / -0.0001 | +0.0000 / -0.0001 / +0.0001 | +0.0003 / +0.0001 / +0.0002 | +0.0003 / -0.0001 / +0.0003 | +0.0002 / +0.0000 / +0.0001 |
| vere~t4 | +0.0003 / +0.0000 / +0.0003 | +0.0001 / +0.0003 / -0.0002 | -0.0005 / -0.0001 / -0.0003 | -0.0003 / +0.0000 / -0.0003 | -0.0000 / +0.0001 / -0.0001 |
| vere~t5 | -0.0003 / -0.0000 / -0.0003 | +0.0003 / -0.0002 / +0.0005 | +0.0004 / +0.0001 / +0.0003 | +0.0001 / -0.0000 / +0.0002 | +0.0004 / +0.0001 / +0.0003 |
| a13~t | -0.0001 / +0.0001 / -0.0002 | +0.0005 / +0.0003 / +0.0002 | +0.0004 / +0.0002 / +0.0002 | +0.0004 / +0.0001 / +0.0003 | +0.0003 / +0.0000 / +0.0003 |
| argP1~t | +0.0002 / -0.0001 / +0.0003 | +0.0001 / +0.0000 / +0.0001 | -0.0004 / -0.0000 / -0.0004 | -0.0001 / -0.0000 / -0.0001 | -0.0001 / +0.0000 / -0.0001 |
| tecM1~t | -0.0001 / -0.0001 / +0.0001 | +0.0001 / -0.0000 / +0.0001 | +0.0004 / +0.0000 / +0.0004 | +0.0002 / +0.0001 / +0.0001 | -0.0000 / +0.0000 / -0.0001 |
| argF1~t | +0.0005 / -0.0000 / +0.0005 | +0.0002 / -0.0001 / +0.0003 | +0.0002 / +0.0000 / +0.0001 | +0.0002 / +0.0001 / +0.0001 | +0.0002 / +0.0000 / +0.0002 |
| latino~t | +0.0002 / +0.0002 / +0.0000 | -0.0000 / -0.0001 / +0.0001 | +0.0002 / +0.0000 / +0.0002 | +0.0001 / +0.0000 / +0.0001 | +0.0003 / +0.0001 / +0.0002 |
| inglese~t | -0.0013 / -0.0007 / -0.0006 | -0.0007 / -0.0003 / -0.0005 | -0.0002 / +0.0000 / -0.0002 | +0.0006 / +0.0003 / +0.0003 | +0.0001 / -0.0001 / +0.0002 |
| ts1~p | +0.0431 / +0.0158 / +0.0272 | +0.0431 / +0.0158 / +0.0274 | +0.0420 / +0.0155 / +0.0265 | +0.0426 / +0.0159 / +0.0267 | +0.0424 / +0.0157 / +0.0267 |
| italiano~t | +0.0016 / +0.0011 / +0.0004 | +0.0001 / +0.0001 / +0.0001 | -0.0011 / -0.0001 / -0.0009 | -0.0003 / +0.0001 / -0.0004 | -0.0003 / -0.0002 / -0.0001 |
| vere~p | +0.0077 / +0.0020 / +0.0057 | +0.0081 / +0.0019 / +0.0061 | +0.0079 / +0.0020 / +0.0059 | +0.0073 / +0.0021 / +0.0052 | +0.0057 / +0.0016 / +0.0041 |
| a13~p | +0.0068 / +0.0017 / +0.0051 | +0.0071 / +0.0016 / +0.0054 | +0.0072 / +0.0018 / +0.0054 | +0.0069 / +0.0018 / +0.0050 | +0.0053 / +0.0011 / +0.0042 |
| argP1~p | +0.0122 / +0.0118 / +0.0004 | +0.0115 / +0.0115 / -0.0000 | +0.0116 / +0.0119 / -0.0003 | +0.0117 / +0.0116 / +0.0001 | +0.0117 / +0.0115 / +0.0002 |
| tecM1~p | +0.0033 / +0.0015 / +0.0018 | +0.0046 / +0.0018 / +0.0028 | +0.0039 / +0.0014 / +0.0025 | +0.0031 / +0.0012 / +0.0019 | +0.0022 / +0.0008 / +0.0014 |
| argF1~p | +0.0120 / +0.0041 / +0.0079 | +0.0118 / +0.0041 / +0.0077 | +0.0121 / +0.0044 / +0.0078 | +0.0119 / +0.0042 / +0.0078 | +0.0118 / +0.0043 / +0.0075 |
| italiano~p | +0.0059 / +0.0036 / +0.0023 | +0.0042 / +0.0037 / +0.0005 | +0.0046 / +0.0037 / +0.0009 | +0.0041 / +0.0032 / +0.0009 | +0.0039 / +0.0036 / +0.0003 |
| inglese~p | +0.0024 / +0.0027 / -0.0003 | +0.0029 / +0.0030 / -0.0001 | +0.0026 / +0.0029 / -0.0002 | +0.0033 / +0.0034 / -0.0001 | +0.0024 / +0.0030 / -0.0006 |
| latino~p | +0.0092 / +0.0061 / +0.0032 | +0.0096 / +0.0064 / +0.0032 | +0.0093 / +0.0062 / +0.0031 | +0.0090 / +0.0058 / +0.0032 | +0.0092 / +0.0059 / +0.0033 |

Bande: D0 stessa riga (parole prima), D1 una riga sopra, D2 due-tre righe sopra, D4 quattro-sette, D8 otto o piu'.

## Il paragrafo: eco dentro e fra paragrafi a 2-3 righe di distanza (senza le prime righe dei paragrafi; pagine con pesi comuni)

| testo | Q a 2-3 righe (D2) = eco fra / eco dentro | confini spostati: 2,5% - 97,5% | eco dentro D2 | eco fra D2 | pagine usate | Q a 4-7 righe (D4) | pagine D4 | paragrafo |
|---|---|---|---|---|---|---|---|---|
| vere | +0.88 (+0.69; +1.11) | 0.72 - 1.40 | +0.0127 (+0.0102; +0.0153) | +0.0112 (+0.0089; +0.0136) | 154 | +0.80 (+0.51; +1.15) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| a13 | +0.77 (+0.54; +1.03) | 0.66 - 1.43 | +0.0121 (+0.0092; +0.0150) | +0.0093 (+0.0062; +0.0124) | 169 | +1.09 (+0.71; +1.88) | 127 | non leggibile (i controlli di questa lettura non sono superati) |
| a14 | +0.76 (+0.56; +1.09) | 0.65 - 1.64 | +0.0119 (+0.0087; +0.0147) | +0.0090 (+0.0066; +0.0117) | 182 | +0.57 (+0.36; +0.88) | 133 | non leggibile (i controlli di questa lettura non sono superati) |
| a15 | +0.90 (+0.62; +1.23) | 0.53 - 1.66 | +0.0081 (+0.0060; +0.0103) | +0.0073 (+0.0050; +0.0097) | 185 | +0.97 (+0.50; +1.83) | 147 | non leggibile (i controlli di questa lettura non sono superati) |
| a16 | +0.67 (+0.45; +0.93) | 0.59 - 1.46 | +0.0088 (+0.0064; +0.0113) | +0.0059 (+0.0037; +0.0079) | 183 | +1.07 (+0.62; +2.12) | 139 | non leggibile (i controlli di questa lettura non sono superati) |
| a17 | +0.59 (+0.38; +0.85) | 0.55 - 1.46 | +0.0111 (+0.0085; +0.0137) | +0.0065 (+0.0039; +0.0096) | 171 | +0.94 (+0.64; +1.48) | 130 | non leggibile (i controlli di questa lettura non sono superati) |
| a18 | +0.98 (+0.70; +1.30) | 0.65 - 1.61 | +0.0102 (+0.0075; +0.0130) | +0.0099 (+0.0069; +0.0133) | 171 | +0.79 (+0.49; +1.27) | 123 | non leggibile (i controlli di questa lettura non sono superati) |
| a19 | +0.72 (+0.39; +1.08) | 0.54 - 1.53 | +0.0102 (+0.0071; +0.0129) | +0.0073 (+0.0037; +0.0106) | 177 | +0.90 (+0.49; +1.89) | 142 | non leggibile (i controlli di questa lettura non sono superati) |
| ts1 | - (-; -) | - | - (-; -) | - (-; -) | 0 | - (-; -) | 0 | non leggibile (i controlli di questa lettura non sono superati) |
| ts2 | - (-; -) | - | - (-; -) | - (-; -) | 0 | - (-; -) | 0 | non leggibile (i controlli di questa lettura non sono superati) |
| a21 | +0.77 (+0.47; +1.06) | 0.60 - 1.58 | +0.0127 (+0.0096; +0.0158) | +0.0097 (+0.0058; +0.0135) | 179 | +0.65 (+0.38; +0.94) | 145 | non leggibile (i controlli di questa lettura non sono superati) |
| a20 | +0.77 (+0.50; +1.11) | 0.66 - 1.55 | +0.0092 (+0.0070; +0.0117) | +0.0071 (+0.0046; +0.0095) | 184 | +0.86 (+0.51; +1.31) | 131 | non leggibile (i controlli di questa lettura non sono superati) |
| a22 | +0.84 (+0.53; +1.23) | 0.61 - 1.76 | +0.0094 (+0.0069; +0.0122) | +0.0079 (+0.0047; +0.0114) | 181 | +0.76 (+0.25; +1.59) | 136 | non leggibile (i controlli di questa lettura non sono superati) |
| latino | +1.03 (+0.80; +1.24) | 0.79 - 1.28 | +0.0127 (+0.0093; +0.0164) | +0.0132 (+0.0085; +0.0186) | 196 | +0.95 (+0.78; +1.16) | 196 | non leggibile (i controlli di questa lettura non sono superati) |
| italiano | +1.07 (+0.49; +1.76) | 0.30 - 1.88 | +0.0064 (+0.0045; +0.0082) | +0.0068 (+0.0032; +0.0107) | 196 | +0.69 (+0.40; +1.22) | 196 | non leggibile (i controlli di questa lettura non sono superati) |
| inglese | +0.65 (+0.25; +1.15) | 0.45 - 1.55 | +0.0053 (+0.0038; +0.0068) | +0.0034 (+0.0012; +0.0056) | 196 | +1.26 (+0.46; +5.12) | 196 | non leggibile (i controlli di questa lettura non sono superati) |
| latGeom | +0.94 (+0.70; +1.31) | 0.71 - 1.38 | +0.0068 (+0.0044; +0.0097) | +0.0064 (+0.0040; +0.0091) | 154 | +0.78 (+0.47; +1.21) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| ingGeom | +1.03 (+0.50; +1.87) | 0.56 - 1.55 | +0.0047 (+0.0029; +0.0067) | +0.0049 (+0.0024; +0.0076) | 154 | +0.86 (+0.24; +1.77) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argP1 | +0.94 (+0.79; +1.11) | 0.83 - 1.19 | +0.0125 (+0.0111; +0.0140) | +0.0118 (+0.0102; +0.0133) | 154 | +1.11 (+0.97; +1.29) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argP2 | +1.02 (+0.88; +1.19) | 0.79 - 1.21 | +0.0114 (+0.0100; +0.0128) | +0.0117 (+0.0103; +0.0132) | 154 | +0.93 (+0.80; +1.07) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argP3 | +1.13 (+0.90; +1.37) | 0.85 - 1.19 | +0.0100 (+0.0084; +0.0115) | +0.0113 (+0.0096; +0.0129) | 154 | +1.00 (+0.88; +1.13) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argR1 | -0.02 (-0.09; +0.05) | 0.71 - 1.19 | +0.0167 (+0.0151; +0.0183) | -0.0003 (-0.0015; +0.0009) | 154 | -0.01 (-0.11; +0.07) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argR2 | +0.03 (-0.04; +0.11) | 0.65 - 1.15 | +0.0155 (+0.0142; +0.0168) | +0.0005 (-0.0006; +0.0018) | 154 | -0.00 (-0.08; +0.09) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argR3 | +0.03 (-0.06; +0.13) | 0.67 - 1.18 | +0.0135 (+0.0121; +0.0147) | +0.0005 (-0.0007; +0.0017) | 154 | -0.01 (-0.09; +0.06) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argS1 | +0.88 (+0.75; +1.02) | 0.82 - 1.19 | +0.0124 (+0.0110; +0.0137) | +0.0109 (+0.0096; +0.0123) | 154 | +1.05 (+0.87; +1.29) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argF1 | +1.01 (+0.86; +1.17) | 0.86 - 1.17 | +0.0111 (+0.0098; +0.0125) | +0.0112 (+0.0098; +0.0125) | 154 | +0.91 (+0.82; +1.02) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argF2 | +0.94 (+0.80; +1.10) | 0.82 - 1.16 | +0.0131 (+0.0117; +0.0145) | +0.0124 (+0.0106; +0.0141) | 154 | +0.90 (+0.77; +1.05) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecM1 | +0.48 (+0.21; +0.81) | 0.56 - 1.29 | +0.0067 (+0.0053; +0.0083) | +0.0033 (+0.0014; +0.0051) | 154 | -0.23 (-3.28; +0.51) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecM2 | +0.97 (+0.66; +1.49) | 0.50 - 1.24 | +0.0058 (+0.0040; +0.0076) | +0.0056 (+0.0041; +0.0072) | 154 | +2.40 (+0.54; +22.96) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecM3 | +1.00 (+0.61; +1.60) | 0.53 - 1.29 | +0.0047 (+0.0031; +0.0061) | +0.0047 (+0.0030; +0.0063) | 154 | -0.03 (-0.79; +1.35) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecP1 | +0.12 (-0.14; +0.39) | 0.41 - 1.44 | +0.0062 (+0.0046; +0.0081) | +0.0007 (-0.0009; +0.0022) | 154 | +0.07 (-0.71; +1.42) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecCoda1 | +0.98 (+0.71; +1.33) | 0.61 - 1.16 | +0.0072 (+0.0057; +0.0088) | +0.0070 (+0.0055; +0.0086) | 154 | +1.79 (+0.67; +11.63) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecTesta1 | +0.83 (+0.60; +1.16) | 0.59 - 1.25 | +0.0073 (+0.0056; +0.0091) | +0.0061 (+0.0046; +0.0077) | 154 | +1.17 (+0.39; +4.58) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argPm1 | +0.82 (+0.57; +1.13) | 0.74 - 1.44 | +0.0064 (+0.0049; +0.0078) | +0.0052 (+0.0037; +0.0066) | 154 | +0.98 (+0.68; +1.38) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argRm1 | -0.05 (-0.20; +0.09) | 0.45 - 1.37 | +0.0078 (+0.0064; +0.0090) | -0.0004 (-0.0015; +0.0007) | 154 | -0.08 (-0.19; +0.03) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argFm1 | +1.03 (+0.76; +1.39) | 0.68 - 1.42 | +0.0057 (+0.0045; +0.0068) | +0.0059 (+0.0046; +0.0072) | 154 | +0.99 (+0.77; +1.29) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecMm1 | +0.94 (+0.40; +1.80) | 0.35 - 1.63 | +0.0034 (+0.0018; +0.0050) | +0.0032 (+0.0014; +0.0051) | 154 | +0.81 (-0.33; +10.23) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecPm1 | +0.09 (-0.59; +0.68) | -0.08 - 3.31 | +0.0026 (+0.0012; +0.0040) | +0.0002 (-0.0011; +0.0017) | 154 | -0.46 (-3.27; +0.72) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| argPd1 | +1.03 (+0.51; +1.83) | 0.42 - 1.65 | +0.0035 (+0.0024; +0.0046) | +0.0036 (+0.0020; +0.0054) | 154 | +0.91 (+0.39; +1.83) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecMd1 | +0.57 (-0.27; +2.61) | -0.09 - 5.20 | +0.0021 (+0.0007; +0.0035) | +0.0012 (-0.0006; +0.0032) | 154 | - (-6.43; +20.76) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| tecPd1 | -0.35 (-4.38; +1.40) | -0.60 - 2.75 | +0.0013 (-0.0001; +0.0026) | -0.0004 (-0.0021; +0.0013) | 154 | - (-18.85; +3.58) | 116 | non leggibile (i controlli di questa lettura non sono superati) |
| vere~t1 | - (+1.46; +97.51) | -10.01 - 8.61 | -0.0004 (-0.0016; +0.0006) | +0.0022 (+0.0006; +0.0037) | 154 | -0.08 (-8.31; +5.41) | 116 |  |
| vere~t2 | - (-5.83; +31.62) | -7.75 - 8.13 | -0.0005 (-0.0017; +0.0010) | +0.0008 (-0.0008; +0.0023) | 154 | - (-55.26; +9.82) | 116 |  |
| vere~t3 | - (-69.85; +3.78) | -64.02 - 30.31 | -0.0007 (-0.0021; +0.0006) | -0.0004 (-0.0018; +0.0009) | 154 | -28.57 (-69.46; +1.51) | 116 |  |
| ts1~t | - (-; -) | - | - (-; -) | - (-; -) | 0 | - (-; -) | 0 |  |
| vere~t4 | - (-29.02; +26.61) | -50.54 - 20.70 | -0.0003 (-0.0016; +0.0010) | +0.0001 (-0.0014; +0.0014) | 154 | -3.26 (-43.41; +2.42) | 116 |  |
| vere~t5 | - (-2.38; +54.22) | -2.25 - 9.34 | -0.0001 (-0.0015; +0.0013) | +0.0008 (-0.0005; +0.0022) | 154 | -7.16 (-19.71; +8.18) | 116 |  |
| a13~t | - (-1.26; +39.67) | -3.33 - 10.60 | -0.0000 (-0.0011; +0.0011) | +0.0009 (-0.0004; +0.0023) | 169 | +0.89 (-0.82; +11.79) | 127 |  |
| argP1~t | - (-17.33; +0.54) | -339.52 - 8.49 | -0.0009 (-0.0018; +0.0001) | -0.0002 (-0.0013; +0.0010) | 154 | +1.98 (-1.41; +18.71) | 116 |  |
| tecM1~t | +1.72 (-1.35; +13.00) | -4.90 - 16.56 | +0.0004 (-0.0009; +0.0017) | +0.0006 (-0.0005; +0.0018) | 154 | +1.08 (-3.32; +11.63) | 116 |  |
| argF1~t | +0.12 (-2.99; +5.33) | -2.23 - 10.84 | +0.0007 (-0.0003; +0.0017) | +0.0001 (-0.0010; +0.0013) | 154 | -0.60 (-9.88; +2.88) | 116 |  |
| latino~t | +4.82 (-1.12; +58.23) | -7.26 - 32.45 | +0.0001 (-0.0004; +0.0007) | +0.0007 (-0.0002; +0.0017) | 196 | +0.03 (-4.14; +3.77) | 196 |  |
| inglese~t | - (-24.34; +86.21) | -34.03 - 22.08 | -0.0003 (-0.0012; +0.0006) | +0.0005 (-0.0017; +0.0025) | 196 | - (-1.90; +21.72) | 196 |  |
| ts1~p | - (-; -) | - | - (-; -) | - (-; -) | 0 | - (-; -) | 0 |  |
| italiano~t | - (-77.39; +5.54) | -200.62 - 7.60 | -0.0002 (-0.0015; +0.0012) | -0.0017 (-0.0044; +0.0010) | 196 | -1.19 (-16.33; +0.20) | 196 |  |
| vere~p | +1.21 (+0.92; +1.61) | 0.71 - 1.46 | +0.0071 (+0.0051; +0.0091) | +0.0086 (+0.0059; +0.0115) | 154 | +0.96 (+0.72; +1.30) | 116 |  |
| a13~p | +0.95 (+0.65; +1.35) | 0.76 - 1.40 | +0.0067 (+0.0045; +0.0088) | +0.0064 (+0.0042; +0.0087) | 169 | +0.67 (+0.41; +1.04) | 127 |  |
| argP1~p | +0.91 (+0.77; +1.07) | 0.80 - 1.14 | +0.0122 (+0.0110; +0.0137) | +0.0112 (+0.0096; +0.0129) | 154 | +0.97 (+0.80; +1.12) | 116 |  |
| tecM1~p | +1.46 (+0.92; +2.47) | 0.55 - 1.69 | +0.0034 (+0.0020; +0.0048) | +0.0050 (+0.0033; +0.0067) | 154 | +1.50 (+0.82; +4.57) | 116 |  |
| argF1~p | +0.94 (+0.79; +1.13) | 0.85 - 1.13 | +0.0123 (+0.0110; +0.0136) | +0.0116 (+0.0099; +0.0133) | 154 | +1.02 (+0.89; +1.19) | 116 |  |
| italiano~p | +1.20 (+0.36; +2.43) | 0.40 - 2.17 | +0.0043 (+0.0025; +0.0060) | +0.0052 (+0.0017; +0.0088) | 196 | +1.05 (+0.52; +3.09) | 196 |  |
| inglese~p | +1.75 (+0.80; +3.30) | 0.18 - 2.28 | +0.0024 (+0.0013; +0.0036) | +0.0042 (+0.0020; +0.0064) | 196 | +1.12 (+0.66; +2.46) | 196 |  |
| latino~p | +0.98 (+0.80; +1.22) | 0.78 - 1.22 | +0.0095 (+0.0063; +0.0132) | +0.0092 (+0.0064; +0.0128) | 196 | +1.06 (+0.90; +1.28) | 196 |  |

## Dove cadono le modifiche delle varianti vicine (quota dell'eccesso di varianti: inizio / fine / dentro; fra parentesi la quota nel riferimento)

| testo | inizio | fine | dentro la parola | lettura |
|---|---|---|---|---|
| vere | 0.47 (0.48) | 0.17 (0.14) | 0.36 (0.38) | nessun posto prevale |
| a13 | 0.48 (0.48) | 0.11 (0.15) | 0.41 (0.37) | nessun posto prevale |
| a14 | 0.48 (0.51) | 0.13 (0.14) | 0.39 (0.35) | nessun posto prevale |
| a15 | 0.46 (0.52) | 0.10 (0.15) | 0.44 (0.34) | nessun posto prevale |
| a16 | 0.49 (0.49) | 0.13 (0.14) | 0.37 (0.36) | nessun posto prevale |
| a17 | 0.54 (0.49) | 0.13 (0.16) | 0.33 (0.35) | nessun posto prevale |
| a18 | 0.49 (0.50) | 0.11 (0.14) | 0.40 (0.35) | nessun posto prevale |
| a19 | 0.50 (0.50) | 0.10 (0.15) | 0.39 (0.34) | nessun posto prevale |
| ts1 | 0.54 (0.49) | 0.25 (0.26) | 0.22 (0.24) | nessun posto prevale |
| ts2 | 0.50 (0.52) | 0.25 (0.27) | 0.25 (0.22) | nessun posto prevale |
| a21 | 0.53 (0.50) | 0.13 (0.15) | 0.34 (0.36) | nessun posto prevale |
| a20 | 0.45 (0.52) | 0.11 (0.14) | 0.44 (0.34) | nessun posto prevale |
| a22 | 0.48 (0.51) | 0.14 (0.15) | 0.38 (0.34) | nessun posto prevale |
| latino | 0.35 (0.39) | 0.54 (0.46) | 0.11 (0.15) | nessun posto prevale |
| italiano | 0.25 (0.54) | 0.58 (0.44) | 0.17 (0.02) | non leggibile (varianti in eccesso non misurabili) |
| inglese | 0.50 (0.40) | -0.05 (0.55) | 0.55 (0.04) | non leggibile (varianti in eccesso non misurabili) |
| latGeom | 0.41 (0.27) | 0.47 (0.56) | 0.11 (0.17) | nessun posto prevale |
| ingGeom | 0.76 (0.41) | -0.34 (0.54) | 0.58 (0.04) | non leggibile (varianti in eccesso non misurabili) |
| argP1 | 1.58 (0.49) | 0.05 (0.16) | -0.64 (0.36) | non leggibile (varianti in eccesso non misurabili) |
| argP2 | 1.12 (0.49) | -0.26 (0.16) | 0.14 (0.34) | non leggibile (varianti in eccesso non misurabili) |
| argP3 | -0.04 (0.48) | 0.44 (0.17) | 0.61 (0.35) | non leggibile (varianti in eccesso non misurabili) |
| argR1 | 2.04 (0.48) | -3.48 (0.17) | 2.44 (0.35) | non leggibile (varianti in eccesso non misurabili) |
| argR2 | 0.29 (0.49) | 0.49 (0.16) | 0.22 (0.35) | non leggibile (varianti in eccesso non misurabili) |
| argR3 | 0.83 (0.50) | -0.12 (0.14) | 0.29 (0.36) | non leggibile (varianti in eccesso non misurabili) |
| argS1 | 0.47 (0.49) | 0.13 (0.15) | 0.40 (0.36) | nessun posto prevale |
| argF1 | 0.33 (0.49) | 0.15 (0.16) | 0.52 (0.34) | dentro la parola |
| argF2 | 0.33 (0.49) | 0.18 (0.15) | 0.49 (0.37) | nessun posto prevale |
| tecM1 | 0.24 (0.51) | 0.25 (0.17) | 0.51 (0.32) | dentro la parola |
| tecM2 | 0.24 (0.49) | 0.22 (0.19) | 0.54 (0.32) | dentro la parola |
| tecM3 | 0.21 (0.51) | 0.23 (0.18) | 0.55 (0.31) | dentro la parola |
| tecP1 | 0.25 (0.50) | 0.23 (0.18) | 0.52 (0.32) | dentro la parola |
| tecCoda1 | 0.03 (0.46) | 0.94 (0.26) | 0.02 (0.28) | fine |
| tecTesta1 | 0.97 (0.57) | 0.03 (0.15) | 0.00 (0.28) | inizio |
| argPm1 | 0.59 (0.51) | 0.45 (0.15) | -0.03 (0.35) | non leggibile (varianti in eccesso non misurabili) |
| argRm1 | 0.29 (0.50) | 0.26 (0.16) | 0.45 (0.34) | non leggibile (varianti in eccesso non misurabili) |
| argFm1 | 0.30 (0.50) | 0.13 (0.16) | 0.57 (0.34) | dentro la parola |
| tecMm1 | 0.29 (0.51) | 0.21 (0.16) | 0.49 (0.33) | nessun posto prevale |
| tecPm1 | 0.24 (0.52) | 0.24 (0.16) | 0.52 (0.33) | dentro la parola |
| argPd1 | 2.57 (0.51) | 0.88 (0.15) | -2.45 (0.33) | non leggibile (varianti in eccesso non misurabili) |
| tecMd1 | 0.21 (0.50) | 0.25 (0.16) | 0.53 (0.34) | dentro la parola |
| tecPd1 | 0.33 (0.51) | 0.23 (0.16) | 0.45 (0.33) | nessun posto prevale |
| vere~t1 | 0.99 (0.51) | 0.34 (0.15) | -0.33 (0.33) |  |
| vere~t2 | 0.21 (0.51) | 0.67 (0.15) | 0.12 (0.33) |  |
| vere~t3 | 0.24 (0.52) | 0.21 (0.15) | 0.55 (0.33) |  |
| ts1~t | 0.22 (0.49) | 0.86 (0.26) | -0.08 (0.25) |  |
| vere~t4 | 1.92 (0.51) | -2.12 (0.15) | 1.21 (0.34) |  |
| vere~t5 | 0.71 (0.51) | 0.25 (0.15) | 0.04 (0.34) |  |
| a13~t | -0.55 (0.52) | 0.69 (0.14) | 0.86 (0.33) |  |
| argP1~t | 1.12 (0.50) | 0.05 (0.15) | -0.17 (0.34) |  |
| tecM1~t | 0.67 (0.50) | -0.08 (0.18) | 0.40 (0.32) |  |
| argF1~t | 0.35 (0.49) | 0.41 (0.15) | 0.24 (0.36) |  |
| latino~t | 0.61 (0.31) | 0.09 (0.56) | 0.30 (0.13) |  |
| inglese~t | -0.36 (0.41) | 1.47 (0.55) | -0.11 (0.04) |  |
| ts1~p | 0.52 (0.49) | 0.25 (0.26) | 0.23 (0.25) |  |
| italiano~t | 1.08 (0.54) | 0.20 (0.44) | -0.28 (0.02) |  |
| vere~p | 0.46 (0.48) | 0.18 (0.15) | 0.36 (0.38) |  |
| a13~p | 0.52 (0.48) | 0.09 (0.15) | 0.39 (0.37) |  |
| argP1~p | -1.00 (0.48) | 1.21 (0.16) | 0.79 (0.35) |  |
| tecM1~p | 0.16 (0.51) | 0.26 (0.17) | 0.58 (0.32) |  |
| argF1~p | 0.32 (0.49) | 0.16 (0.16) | 0.52 (0.35) |  |
| italiano~p | 0.40 (0.53) | 0.52 (0.45) | 0.08 (0.02) |  |
| inglese~p | 0.68 (0.40) | -0.42 (0.56) | 0.73 (0.04) |  |
| latino~p | 0.38 (0.38) | 0.51 (0.47) | 0.11 (0.15) |  |

## Pagine vicine contro lontane (tasso di parole simili fra pagine intere, in rapporto alla stessa sezione, quaderno diverso, stessa mano)

| testo | stesso foglio | stesso bifoglio | consecutive | stesso quaderno | altra sezione | gradiente (consecutive / quaderno) | coppie foglio / bifoglio / consecutive | solo uguali, consecutive | solo varianti, consecutive |
|---|---|---|---|---|---|---|---|---|---|
| vere | +1.00 (+0.96; +1.04) | +1.01 (+0.97; +1.05) | +0.89 (+0.83; +0.94) | +0.91 (+0.87; +0.95) | +0.64 (+0.62; +0.66) | +0.98 (+0.93; +1.02) | 238 / 412 / 160 | +0.86 (+0.78; +0.94) | +0.89 (+0.84; +0.94) |
| a13 | +0.88 (+0.84; +0.92) | +0.91 (+0.87; +0.94) | +0.84 (+0.79; +0.88) | +0.85 (+0.82; +0.88) | +0.61 (+0.59; +0.64) | +0.99 (+0.93; +1.04) | 238 / 412 / 160 | +0.78 (+0.69; +0.87) | +0.85 (+0.81; +0.89) |
| a14 | +0.91 (+0.87; +0.95) | +0.92 (+0.89; +0.95) | +0.91 (+0.86; +0.96) | +0.87 (+0.84; +0.91) | +0.65 (+0.63; +0.67) | +1.04 (+1.00; +1.09) | 238 / 412 / 160 | +0.90 (+0.81; +1.00) | +0.91 (+0.87; +0.95) |
| a15 | +0.91 (+0.87; +0.95) | +0.91 (+0.87; +0.94) | +0.84 (+0.80; +0.89) | +0.88 (+0.85; +0.91) | +0.65 (+0.63; +0.67) | +0.96 (+0.92; +1.00) | 238 / 412 / 160 | +0.79 (+0.71; +0.88) | +0.85 (+0.81; +0.89) |
| a16 | +0.91 (+0.88; +0.94) | +0.92 (+0.89; +0.95) | +0.85 (+0.81; +0.90) | +0.87 (+0.84; +0.90) | +0.63 (+0.61; +0.65) | +0.98 (+0.93; +1.04) | 238 / 412 / 160 | +0.86 (+0.77; +0.96) | +0.85 (+0.81; +0.89) |
| a17 | +0.89 (+0.85; +0.93) | +0.87 (+0.84; +0.90) | +0.84 (+0.79; +0.89) | +0.82 (+0.79; +0.86) | +0.59 (+0.57; +0.61) | +1.03 (+0.97; +1.08) | 238 / 412 / 160 | +0.79 (+0.71; +0.86) | +0.85 (+0.81; +0.90) |
| a18 | +0.92 (+0.87; +0.96) | +0.88 (+0.85; +0.92) | +0.84 (+0.79; +0.89) | +0.84 (+0.80; +0.88) | +0.61 (+0.59; +0.64) | +1.00 (+0.95; +1.07) | 238 / 412 / 160 | +0.75 (+0.66; +0.85) | +0.86 (+0.81; +0.91) |
| a19 | +0.92 (+0.89; +0.96) | +0.90 (+0.87; +0.93) | +0.84 (+0.80; +0.89) | +0.84 (+0.81; +0.87) | +0.64 (+0.62; +0.66) | +1.01 (+0.96; +1.05) | 238 / 412 / 160 | +0.79 (+0.73; +0.87) | +0.85 (+0.81; +0.90) |
| ts1 | +1.17 (+1.06; +1.30) | - (-; -) | +1.05 (+1.01; +1.10) | +1.02 (+0.99; +1.05) | +1.01 (+1.00; +1.03) | +1.03 (+0.99; +1.08) | 138 / 0 / 136 | +1.08 (+1.00; +1.17) | +1.05 (+1.01; +1.09) |
| ts2 | +1.06 (+0.95; +1.19) | - (-; -) | +1.13 (+1.03; +1.24) | +0.98 (+0.95; +1.00) | +0.98 (+0.95; +1.00) | +1.16 (+1.07; +1.26) | 138 / 0 / 136 | +1.31 (+1.07; +1.58) | +1.10 (+1.02; +1.17) |
| a21 | +0.91 (+0.86; +0.97) | +0.90 (+0.86; +0.95) | +0.81 (+0.75; +0.86) | +0.84 (+0.80; +0.88) | +0.60 (+0.58; +0.63) | +0.96 (+0.91; +1.01) | 238 / 412 / 160 | +0.70 (+0.61; +0.80) | +0.83 (+0.79; +0.87) |
| a20 | +0.92 (+0.88; +0.97) | +0.90 (+0.87; +0.94) | +0.82 (+0.78; +0.87) | +0.86 (+0.83; +0.90) | +0.66 (+0.64; +0.68) | +0.95 (+0.91; +0.99) | 238 / 412 / 160 | +0.78 (+0.71; +0.86) | +0.83 (+0.79; +0.88) |
| a22 | +0.90 (+0.86; +0.93) | +0.93 (+0.89; +0.96) | +0.87 (+0.82; +0.93) | +0.85 (+0.82; +0.89) | +0.65 (+0.63; +0.67) | +1.02 (+0.96; +1.09) | 238 / 412 / 160 | +0.87 (+0.77; +0.97) | +0.87 (+0.83; +0.93) |
| latino | +1.50 (+1.36; +1.65) | - (-; -) | +1.46 (+1.33; +1.61) | +1.26 (+1.19; +1.33) | +0.78 (+0.73; +0.82) | +1.16 (+1.05; +1.28) | 196 / 0 / 194 | +1.80 (+1.59; +2.02) | +1.19 (+1.08; +1.33) |
| italiano | +1.08 (+1.05; +1.12) | - (-; -) | +1.07 (+1.04; +1.10) | +1.01 (+1.00; +1.02) | +1.00 (+0.99; +1.00) | +1.06 (+1.03; +1.09) | 196 / 0 / 194 | +1.24 (+1.18; +1.30) | +1.01 (+0.98; +1.04) |
| inglese | +1.07 (+1.04; +1.09) | - (-; -) | +1.04 (+1.02; +1.06) | +1.01 (+1.00; +1.02) | +0.99 (+0.98; +1.00) | +1.03 (+1.01; +1.05) | 196 / 0 / 194 | +1.08 (+1.06; +1.11) | +1.00 (+0.98; +1.02) |
| latGeom | +2.00 (+1.71; +2.34) | +1.80 (+1.48; +2.19) | +2.13 (+1.82; +2.49) | +1.50 (+1.35; +1.66) | +1.05 (+0.97; +1.16) | +1.42 (+1.26; +1.61) | 238 / 412 / 160 | +2.49 (+2.15; +2.89) | +1.78 (+1.43; +2.15) |
| ingGeom | +1.11 (+1.08; +1.14) | +1.07 (+1.04; +1.10) | +1.11 (+1.08; +1.14) | +1.07 (+1.05; +1.09) | +1.07 (+1.04; +1.09) | +1.04 (+1.01; +1.07) | 238 / 412 / 160 | +1.22 (+1.17; +1.27) | +1.02 (+0.99; +1.06) |
| argP1 | +1.02 (+0.99; +1.05) | +1.00 (+0.98; +1.02) | +1.00 (+0.96; +1.03) | +1.00 (+0.98; +1.01) | +0.99 (+0.96; +1.01) | +1.00 (+0.97; +1.03) | 238 / 412 / 160 | +1.04 (+0.97; +1.12) | +0.99 (+0.96; +1.02) |
| argP2 | +0.99 (+0.97; +1.02) | +1.01 (+0.99; +1.03) | +0.99 (+0.96; +1.02) | +1.00 (+0.99; +1.02) | +1.01 (+0.99; +1.03) | +0.99 (+0.96; +1.01) | 238 / 412 / 160 | +1.02 (+0.95; +1.09) | +0.99 (+0.96; +1.02) |
| argP3 | +1.04 (+1.01; +1.07) | +1.01 (+0.99; +1.04) | +1.02 (+0.99; +1.05) | +1.02 (+1.00; +1.04) | +1.03 (+1.01; +1.05) | +1.00 (+0.98; +1.03) | 238 / 412 / 160 | +1.04 (+0.97; +1.11) | +1.02 (+0.99; +1.05) |
| argR1 | +1.01 (+0.98; +1.04) | +1.00 (+0.98; +1.03) | +0.98 (+0.95; +1.01) | +1.00 (+0.98; +1.02) | +1.00 (+0.98; +1.02) | +0.98 (+0.96; +1.01) | 238 / 412 / 160 | +1.03 (+0.97; +1.09) | +0.98 (+0.95; +1.01) |
| argR2 | +1.02 (+0.99; +1.05) | +1.01 (+0.98; +1.03) | +1.03 (+1.00; +1.06) | +1.02 (+1.00; +1.04) | +1.02 (+1.00; +1.05) | +1.00 (+0.98; +1.04) | 238 / 412 / 160 | +1.01 (+0.94; +1.09) | +1.03 (+1.00; +1.06) |
| argR3 | +1.03 (+1.00; +1.07) | +1.04 (+1.01; +1.06) | +0.99 (+0.96; +1.02) | +1.02 (+1.01; +1.04) | +1.04 (+1.02; +1.06) | +0.97 (+0.95; +1.00) | 238 / 412 / 160 | +1.01 (+0.96; +1.07) | +0.99 (+0.96; +1.02) |
| argS1 | +1.33 (+1.28; +1.39) | +1.09 (+1.06; +1.12) | +1.33 (+1.28; +1.38) | +1.05 (+1.03; +1.07) | +1.04 (+1.02; +1.06) | +1.27 (+1.22; +1.31) | 238 / 412 / 160 | +3.66 (+3.28; +4.05) | +1.01 (+0.98; +1.05) |
| argF1 | +0.99 (+0.96; +1.02) | +0.99 (+0.97; +1.01) | +1.01 (+0.98; +1.04) | +1.00 (+0.98; +1.02) | +0.99 (+0.97; +1.02) | +1.01 (+0.98; +1.05) | 238 / 412 / 160 | +1.03 (+0.97; +1.10) | +1.01 (+0.98; +1.04) |
| argF2 | +1.00 (+0.97; +1.03) | +1.00 (+0.97; +1.02) | +0.99 (+0.96; +1.02) | +0.99 (+0.97; +1.01) | +0.99 (+0.97; +1.01) | +1.00 (+0.98; +1.03) | 238 / 412 / 160 | +0.93 (+0.87; +0.99) | +1.00 (+0.97; +1.03) |
| tecM1 | +1.02 (+0.99; +1.04) | +1.00 (+0.98; +1.03) | +1.00 (+0.96; +1.03) | +1.01 (+0.99; +1.03) | +1.01 (+0.99; +1.03) | +0.98 (+0.96; +1.01) | 238 / 412 / 160 | +1.01 (+0.95; +1.06) | +0.99 (+0.96; +1.03) |
| tecM2 | +1.00 (+0.97; +1.03) | +0.99 (+0.97; +1.02) | +0.99 (+0.96; +1.03) | +0.99 (+0.97; +1.01) | +0.99 (+0.97; +1.02) | +1.00 (+0.98; +1.03) | 238 / 412 / 160 | +1.04 (+0.99; +1.09) | +0.99 (+0.96; +1.02) |
| tecM3 | +0.99 (+0.96; +1.02) | +1.00 (+0.97; +1.02) | +0.98 (+0.95; +1.02) | +1.00 (+0.98; +1.02) | +1.01 (+0.99; +1.04) | +0.98 (+0.96; +1.01) | 238 / 412 / 160 | +0.98 (+0.92; +1.04) | +0.98 (+0.95; +1.02) |
| tecP1 | +1.02 (+1.00; +1.05) | +1.04 (+1.02; +1.06) | +1.01 (+0.98; +1.04) | +1.02 (+1.00; +1.03) | +1.03 (+1.01; +1.05) | +0.99 (+0.97; +1.02) | 238 / 412 / 160 | +1.03 (+0.97; +1.08) | +1.01 (+0.98; +1.04) |
| tecCoda1 | +0.97 (+0.95; +1.00) | +1.00 (+0.98; +1.02) | +0.98 (+0.95; +1.01) | +1.00 (+0.98; +1.01) | +0.99 (+0.97; +1.02) | +0.98 (+0.95; +1.01) | 238 / 412 / 160 | +0.99 (+0.94; +1.04) | +0.97 (+0.95; +1.00) |
| tecTesta1 | +0.99 (+0.97; +1.02) | +0.97 (+0.95; +0.99) | +1.00 (+0.97; +1.04) | +0.98 (+0.96; +1.00) | +0.96 (+0.94; +0.98) | +1.02 (+0.99; +1.06) | 238 / 412 / 160 | +1.00 (+0.95; +1.05) | +1.00 (+0.97; +1.04) |
| argPm1 | +0.97 (+0.95; +1.00) | +1.02 (+1.00; +1.04) | +1.02 (+0.99; +1.05) | +1.01 (+0.99; +1.03) | +1.00 (+0.98; +1.02) | +1.01 (+0.99; +1.03) | 238 / 412 / 160 | +1.02 (+0.98; +1.07) | +1.02 (+0.99; +1.05) |
| argRm1 | +0.98 (+0.96; +1.01) | +0.99 (+0.97; +1.02) | +1.01 (+0.99; +1.04) | +0.99 (+0.98; +1.01) | +0.98 (+0.97; +1.00) | +1.02 (+1.00; +1.05) | 238 / 412 / 160 | +1.04 (+0.99; +1.08) | +1.01 (+0.99; +1.04) |
| argFm1 | +0.99 (+0.97; +1.01) | +1.00 (+0.98; +1.02) | +0.99 (+0.97; +1.01) | +1.01 (+0.99; +1.02) | +1.00 (+0.99; +1.02) | +0.98 (+0.96; +1.00) | 238 / 412 / 160 | +0.99 (+0.94; +1.04) | +0.99 (+0.96; +1.01) |
| tecMm1 | +1.02 (+1.00; +1.04) | +1.01 (+0.99; +1.03) | +1.02 (+0.99; +1.04) | +1.02 (+1.00; +1.03) | +1.02 (+1.00; +1.04) | +1.00 (+0.98; +1.02) | 238 / 412 / 160 | +1.06 (+1.01; +1.11) | +1.01 (+0.99; +1.03) |
| tecPm1 | +0.98 (+0.96; +1.01) | +0.99 (+0.97; +1.01) | +0.99 (+0.96; +1.01) | +0.98 (+0.97; +0.99) | +0.98 (+0.96; +1.00) | +1.01 (+0.98; +1.03) | 238 / 412 / 160 | +0.99 (+0.95; +1.03) | +0.99 (+0.96; +1.01) |
| argPd1 | +0.99 (+0.97; +1.01) | +0.98 (+0.96; +1.00) | +0.98 (+0.96; +1.01) | +0.98 (+0.96; +0.99) | +0.98 (+0.96; +1.00) | +1.00 (+0.98; +1.02) | 238 / 412 / 160 | +0.95 (+0.91; +1.00) | +0.99 (+0.96; +1.01) |
| tecMd1 | +0.99 (+0.97; +1.01) | +1.02 (+1.00; +1.03) | +1.01 (+0.99; +1.03) | +1.00 (+0.99; +1.01) | +1.00 (+0.99; +1.02) | +1.01 (+0.99; +1.03) | 238 / 412 / 160 | +1.01 (+0.96; +1.05) | +1.01 (+0.99; +1.04) |
| tecPd1 | +0.99 (+0.97; +1.01) | +0.99 (+0.98; +1.01) | +0.99 (+0.97; +1.01) | +0.99 (+0.98; +1.01) | +0.99 (+0.97; +1.01) | +1.00 (+0.98; +1.02) | 238 / 412 / 160 | +0.99 (+0.95; +1.04) | +0.99 (+0.97; +1.01) |
| vere~t1 | +0.99 (+0.97; +1.01) | +1.01 (+0.99; +1.03) | +1.00 (+0.98; +1.02) | +0.99 (+0.98; +1.01) | +1.01 (+1.00; +1.03) | +1.01 (+0.99; +1.03) | 238 / 412 / 160 | +1.01 (+0.98; +1.05) | +1.00 (+0.98; +1.02) |
| vere~t2 | +1.02 (+0.99; +1.04) | +1.01 (+0.99; +1.03) | +1.00 (+0.99; +1.02) | +1.00 (+0.99; +1.01) | +1.00 (+0.99; +1.02) | +1.00 (+0.99; +1.02) | 238 / 412 / 160 | +0.99 (+0.95; +1.03) | +1.01 (+0.99; +1.03) |
| vere~t3 | +1.01 (+1.00; +1.03) | +1.02 (+1.00; +1.04) | +1.02 (+1.00; +1.04) | +1.01 (+1.00; +1.02) | +1.02 (+1.00; +1.03) | +1.01 (+0.99; +1.03) | 238 / 412 / 160 | +1.07 (+1.03; +1.11) | +1.01 (+0.99; +1.03) |
| ts1~t | +1.00 (+0.99; +1.01) | - (-; -) | +1.00 (+0.99; +1.01) | +1.00 (+0.99; +1.00) | +1.00 (+1.00; +1.00) | +1.00 (+0.99; +1.01) | 138 / 0 / 136 | +1.00 (+0.98; +1.02) | +1.00 (+0.99; +1.01) |
| vere~t4 | +1.00 (+0.98; +1.01) | +1.00 (+0.99; +1.02) | +1.00 (+0.98; +1.02) | +1.00 (+0.99; +1.01) | +1.00 (+0.99; +1.02) | +1.00 (+0.98; +1.02) | 238 / 412 / 160 | +1.02 (+0.98; +1.05) | +1.00 (+0.98; +1.02) |
| vere~t5 | +1.00 (+0.98; +1.02) | +1.00 (+0.98; +1.01) | +1.01 (+0.99; +1.02) | +1.00 (+0.99; +1.01) | +1.00 (+0.99; +1.02) | +1.01 (+0.99; +1.03) | 238 / 412 / 160 | +1.01 (+0.97; +1.05) | +1.00 (+0.98; +1.02) |
| a13~t | +0.99 (+0.97; +1.01) | +0.99 (+0.98; +1.01) | +0.99 (+0.97; +1.01) | +0.99 (+0.97; +1.00) | +0.99 (+0.97; +1.01) | +1.01 (+0.99; +1.02) | 238 / 412 / 160 | +0.97 (+0.93; +1.01) | +1.00 (+0.98; +1.02) |
| argP1~t | +0.99 (+0.96; +1.01) | +0.97 (+0.95; +0.99) | +0.98 (+0.95; +1.00) | +0.99 (+0.98; +1.01) | +0.97 (+0.95; +0.99) | +0.98 (+0.96; +1.00) | 238 / 412 / 160 | +0.97 (+0.93; +1.03) | +0.98 (+0.95; +1.00) |
| tecM1~t | +1.00 (+0.98; +1.02) | +1.01 (+1.00; +1.03) | +1.01 (+0.99; +1.03) | +1.01 (+1.00; +1.03) | +1.01 (+1.00; +1.03) | +1.00 (+0.97; +1.01) | 238 / 412 / 160 | +1.02 (+0.99; +1.06) | +1.01 (+0.98; +1.03) |
| argF1~t | +1.01 (+0.98; +1.04) | +1.01 (+0.99; +1.03) | +1.01 (+0.99; +1.04) | +1.00 (+0.99; +1.01) | +1.00 (+0.98; +1.01) | +1.01 (+0.99; +1.04) | 238 / 412 / 160 | +1.03 (+0.97; +1.08) | +1.01 (+0.99; +1.04) |
| latino~t | +0.99 (+0.96; +1.02) | - (-; -) | +0.99 (+0.96; +1.01) | +0.99 (+0.98; +1.00) | +0.99 (+0.99; +1.00) | +1.00 (+0.97; +1.03) | 196 / 0 / 194 | +0.99 (+0.95; +1.02) | +0.99 (+0.95; +1.02) |
| inglese~t | +1.00 (+0.99; +1.02) | - (-; -) | +1.01 (+0.99; +1.03) | +1.00 (+0.99; +1.01) | +1.00 (+1.00; +1.00) | +1.01 (+0.99; +1.03) | 196 / 0 / 194 | +1.01 (+0.99; +1.03) | +1.01 (+0.99; +1.03) |
| ts1~p | +1.17 (+1.06; +1.30) | - (-; -) | +1.05 (+1.01; +1.10) | +1.02 (+0.99; +1.05) | +1.01 (+1.00; +1.03) | +1.03 (+0.99; +1.08) | 138 / 0 / 136 | +1.08 (+1.00; +1.17) | +1.05 (+1.01; +1.09) |
| italiano~t | +0.99 (+0.97; +1.02) | - (-; -) | +1.01 (+0.99; +1.03) | +1.01 (+1.00; +1.02) | +1.00 (+1.00; +1.01) | +1.00 (+0.98; +1.03) | 196 / 0 / 194 | +0.98 (+0.95; +1.01) | +1.02 (+0.99; +1.05) |
| vere~p | +1.00 (+0.96; +1.04) | +1.01 (+0.97; +1.05) | +0.89 (+0.83; +0.94) | +0.91 (+0.87; +0.95) | +0.64 (+0.62; +0.66) | +0.98 (+0.93; +1.02) | 238 / 412 / 160 | +0.86 (+0.78; +0.94) | +0.89 (+0.84; +0.94) |
| a13~p | +0.88 (+0.84; +0.92) | +0.91 (+0.87; +0.94) | +0.84 (+0.79; +0.88) | +0.85 (+0.82; +0.88) | +0.61 (+0.59; +0.64) | +0.99 (+0.93; +1.04) | 238 / 412 / 160 | +0.78 (+0.69; +0.87) | +0.85 (+0.81; +0.89) |
| argP1~p | +1.02 (+0.99; +1.05) | +1.00 (+0.98; +1.02) | +1.00 (+0.96; +1.03) | +1.00 (+0.98; +1.01) | +0.99 (+0.96; +1.01) | +1.00 (+0.97; +1.03) | 238 / 412 / 160 | +1.04 (+0.97; +1.12) | +0.99 (+0.96; +1.02) |
| tecM1~p | +1.02 (+0.99; +1.04) | +1.00 (+0.98; +1.03) | +1.00 (+0.96; +1.03) | +1.01 (+0.99; +1.03) | +1.01 (+0.99; +1.03) | +0.98 (+0.96; +1.01) | 238 / 412 / 160 | +1.01 (+0.95; +1.06) | +0.99 (+0.96; +1.03) |
| argF1~p | +0.99 (+0.96; +1.02) | +0.99 (+0.97; +1.01) | +1.01 (+0.98; +1.04) | +1.00 (+0.98; +1.02) | +0.99 (+0.97; +1.02) | +1.01 (+0.98; +1.05) | 238 / 412 / 160 | +1.03 (+0.97; +1.10) | +1.01 (+0.98; +1.04) |
| italiano~p | +1.08 (+1.05; +1.12) | - (-; -) | +1.07 (+1.04; +1.10) | +1.01 (+1.00; +1.02) | +1.00 (+0.99; +1.00) | +1.06 (+1.03; +1.09) | 196 / 0 / 194 | +1.24 (+1.18; +1.30) | +1.01 (+0.98; +1.04) |
| inglese~p | +1.07 (+1.04; +1.09) | - (-; -) | +1.04 (+1.02; +1.06) | +1.01 (+1.00; +1.02) | +0.99 (+0.98; +1.00) | +1.03 (+1.01; +1.05) | 196 / 0 / 194 | +1.08 (+1.06; +1.11) | +1.00 (+0.98; +1.02) |
| latino~p | +1.50 (+1.36; +1.65) | - (-; -) | +1.46 (+1.33; +1.61) | +1.26 (+1.19; +1.33) | +0.78 (+0.73; +0.82) | +1.16 (+1.05; +1.28) | 196 / 0 / 194 | +1.80 (+1.59; +2.02) | +1.19 (+1.08; +1.33) |

## Descrittivo: quota di varianti grezza contro lo stesso testo con le parole mescolate dentro la pagina (tiene il lessico e il tema, rompe la distanza)

| testo | quota varianti vicina | quota con le parole mescolate nella pagina | differenza | H testo | H rimescolato |
|---|---|---|---|---|---|
| vere | +0.74 (+0.72; +0.76) | +0.75 (+0.72; +0.78) | -0.01 (-0.04; +0.02) | +0.49 (+0.41; +0.58) | +0.97 (+0.90; +1.06) |
| a13 | +0.74 (+0.71; +0.78) | +0.77 (+0.72; +0.82) | -0.02 (-0.06; +0.01) | +0.52 (+0.42; +0.62) | +1.06 (+0.96; +1.17) |
| ts1 | +0.62 (+0.60; +0.66) | +0.63 (+0.60; +0.67) | -0.01 (-0.02; +0.00) | +0.89 (+0.84; +0.93) | +1.02 (+0.99; +1.04) |
| latino | +0.32 (+0.24; +0.37) | +0.33 (+0.24; +0.40) | -0.02 (-0.05; +0.02) | +0.54 (+0.43; +0.64) | +1.00 (+0.94; +1.07) |
| italiano | +0.14 (-0.02; +0.27) | +0.23 (-0.01; +0.37) | -0.08 (-0.20; +0.07) | +0.65 (+0.43; +0.92) | +0.88 (+0.65; +1.20) |
| inglese | -0.04 (-0.18; +0.07) | -0.06 (-0.31; +0.13) | +0.01 (-0.14; +0.23) | +0.31 (+0.11; +0.49) | +1.06 (+0.80; +1.43) |
| argP1 | +0.01 (-0.03; +0.05) | -0.01 (-0.05; +0.02) | +0.03 (-0.01; +0.06) | +1.00 (+0.96; +1.04) | +1.00 (+0.96; +1.04) |
| argF1 | +0.66 (+0.62; +0.70) | +0.64 (+0.60; +0.68) | +0.02 (+0.00; +0.04) | +1.00 (+0.96; +1.04) | +0.99 (+0.95; +1.04) |
| tecM1 | +0.62 (+0.59; +0.64) | +0.62 (+0.57; +0.67) | -0.00 (-0.05; +0.05) | +0.05 (-0.01; +0.10) | +0.98 (+0.85; +1.14) |

## Le pagine vere per sezione

| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina (grezza) | quota varianti parte locale | profilo | varianti |
|---|---|---|---|---|---|---|---|---|---|
| A | 3 | - | - | - | - | - | - | - | - |
| B | 19 | 6240 | +0.0133 (+0.0105; +0.0159) | +0.0055 (+0.0032; +0.0082) | +0.42 (+0.27; +0.57) | +0.68 (+0.61; +0.73) | +0.72 (+0.62; +0.81) | intermedio | alte |
| C | 5 | 589 | +0.0159 (-0.0048; +0.0398) | +0.0072 (-0.0041; +0.0238) | +0.45 (-0.22; +0.74) | +0.75 (+0.12; +0.84) | +0.84 (+0.68; +0.98) | intermedio | nessuna parte locale |
| H | 128 | 11474 | +0.0173 (+0.0147; +0.0203) | +0.0107 (+0.0083; +0.0133) | +0.62 (+0.49; +0.76) | +0.78 (+0.74; +0.82) | +0.81 (+0.72; +0.93) | intermedio | alte |
| P | 16 | 2306 | +0.0099 (+0.0077; +0.0125) | +0.0058 (+0.0023; +0.0085) | +0.59 (+0.27; +0.79) | +0.74 (+0.67; +0.81) | +0.74 (+0.50; +0.99) | intermedio | alte |
| S | 25 | 11586 | +0.0076 (+0.0054; +0.0100) | +0.0029 (+0.0010; +0.0048) | +0.38 (+0.15; +0.57) | +0.75 (+0.69; +0.79) | +0.76 (+0.68; +0.82) | intermedio | alte |
| T | 6 | 2284 | +0.0149 (+0.0054; +0.0243) | +0.0081 (+0.0001; +0.0158) | +0.54 (+0.01; +0.68) | +0.75 (+0.69; +0.82) | +0.78 (+0.67; +0.95) | intermedio | alte |

Eterogeneita' dell'eco vicina fra i gruppi: {"gruppo_minimo": "S", "gruppo_massimo": "H", "rapporto": 2.2825621800784637, "intervalli_separati": true, "esito": "varia", "rapporto_massimo_dei_riferimenti": 5.910331851365559, "esito_relativo": "come i riferimenti"}

## Le pagine vere per tipo di pagina

| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina (grezza) | quota varianti parte locale | profilo | varianti |
|---|---|---|---|---|---|---|---|---|---|
| H erbario | 128 | 11474 | +0.0173 (+0.0147; +0.0203) | +0.0107 (+0.0083; +0.0133) | +0.62 (+0.49; +0.76) | +0.78 (+0.74; +0.82) | +0.81 (+0.72; +0.93) | intermedio | alte |
| S ricette | 25 | 11586 | +0.0076 (+0.0054; +0.0100) | +0.0029 (+0.0010; +0.0048) | +0.38 (+0.15; +0.57) | +0.75 (+0.69; +0.79) | +0.76 (+0.68; +0.82) | intermedio | alte |
| T solo testo | 6 | 2284 | +0.0149 (+0.0054; +0.0243) | +0.0081 (+0.0001; +0.0158) | +0.54 (+0.01; +0.68) | +0.75 (+0.69; +0.82) | +0.78 (+0.67; +0.95) | intermedio | alte |
| altro | 10 | 3276 | +0.0132 (+0.0094; +0.0166) | +0.0054 (+0.0026; +0.0083) | +0.41 (+0.22; +0.61) | +0.72 (+0.60; +0.82) | +0.76 (+0.62; +0.96) | intermedio | alte |
| circolare o raggi | 6 | 396 | +0.0270 (-0.0075; +0.0397) | +0.0094 (-0.0053; +0.0237) | +0.35 (-0.32; +0.85) | +0.79 (-0.55; +1.38) | +0.91 (-0.43; +3.90) | non leggibile | non leggibile |
| etichette | 27 | 5674 | +0.0115 (+0.0090; +0.0141) | +0.0057 (+0.0033; +0.0084) | +0.50 (+0.31; +0.67) | +0.66 (+0.61; +0.71) | +0.70 (+0.55; +0.78) | intermedio | alte |

Eterogeneita' dell'eco vicina fra i gruppi: {"gruppo_minimo": "S ricette", "gruppo_massimo": "H erbario", "rapporto": 2.2825621800784637, "intervalli_separati": true, "esito": "varia", "rapporto_massimo_dei_riferimenti": 3.5880804173558816, "esito_relativo": "come i riferimenti"}

## Le pagine vere per lingua A/B

| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina (grezza) | quota varianti parte locale | profilo | varianti |
|---|---|---|---|---|---|---|---|---|---|
| ? | 6 | 412 | +0.0130 (-0.0112; +0.0382) | +0.0131 (-0.0070; +0.0226) | +1.01 (-0.90; +3.73) | +0.85 (-0.84; +1.77) | -50.31 (-38.21; +28.49) | non leggibile | non leggibile |
| A | 114 | 11231 | +0.0144 (+0.0120; +0.0175) | +0.0096 (+0.0078; +0.0119) | +0.67 (+0.56; +0.79) | +0.78 (+0.74; +0.81) | +0.84 (+0.73; +1.00) | intermedio | alte |
| B | 82 | 23047 | +0.0107 (+0.0087; +0.0127) | +0.0045 (+0.0029; +0.0064) | +0.42 (+0.30; +0.53) | +0.73 (+0.69; +0.75) | +0.74 (+0.69; +0.79) | intermedio | alte |

## Le pagine vere per mano

| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina (grezza) | quota varianti parte locale | profilo | varianti |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 112 | 10481 | +0.0150 (+0.0123; +0.0180) | +0.0096 (+0.0076; +0.0122) | +0.64 (+0.52; +0.78) | +0.77 (+0.73; +0.81) | +0.82 (+0.72; +0.98) | intermedio | alte |
| 2 | 46 | 10806 | +0.0147 (+0.0117; +0.0175) | +0.0068 (+0.0043; +0.0095) | +0.47 (+0.33; +0.59) | +0.71 (+0.67; +0.75) | +0.74 (+0.67; +0.81) | intermedio | alte |
| 3 | 31 | 11703 | +0.0076 (+0.0054; +0.0101) | +0.0029 (+0.0009; +0.0050) | +0.38 (+0.15; +0.57) | +0.75 (+0.70; +0.79) | +0.76 (+0.68; +0.82) | intermedio | alte |
| 4 | 5 | 367 | +0.0128 (-0.0114; +0.0399) | +0.0131 (-0.0081; +0.0236) | +1.02 (-0.53; +5.28) | +0.83 (-0.23; +1.39) | -10.22 (-29.80; +1.44) | non leggibile | non leggibile |
| 5 | 7 | 873 | +0.0101 (+0.0007; +0.0147) | +0.0051 (-0.0011; +0.0151) | +0.50 (-0.14; +1.76) | +0.77 (+0.69; +1.06) | +0.69 (-0.57; +1.87) | intermedio | nessuna parte locale |
| ? | 1 | - | - | - | - | - | - | - | - |

## Erbario: disegno piccolo, medio, grande (terzili dell'area del disegno, e190)

- disegno piccolo (35 pagine): eco vicina +0.0203 (+0.0138; +0.0271); lontana +0.0125 (+0.0087; +0.0175); H +0.61 (+0.44; +0.87)
- disegno medio (34 pagine): eco vicina +0.0157 (+0.0114; +0.0204); lontana +0.0128 (+0.0080; +0.0182); H +0.82 (+0.57; +1.10)
- disegno grande (35 pagine): eco vicina +0.0201 (+0.0157; +0.0251); lontana +0.0091 (+0.0050; +0.0133); H +0.45 (+0.26; +0.68)

## Eterogeneita' dell'eco vicina per sezione nei generatori (nessuna sezione nel testo) e nelle lingue nella disposizione del Voynich: il Voynich si legge contro questi

- per sezione, latGeom: {"gruppo_minimo": "P", "gruppo_massimo": "H", "rapporto": 5.910331851365559, "intervalli_separati": true, "esito": "varia"}
- per sezione, ingGeom: {"gruppo_minimo": "P", "gruppo_massimo": "H", "rapporto": 3.0340672039070804, "intervalli_separati": false, "esito": "uniforme"}
- per sezione, argP1: {"gruppo_minimo": "P", "gruppo_massimo": "H", "rapporto": 1.1349473035116209, "intervalli_separati": false, "esito": "uniforme"}
- per sezione, argR1: {"gruppo_minimo": "S", "gruppo_massimo": "B", "rapporto": 1.4450000341632163, "intervalli_separati": true, "esito": "zona grigia"}
- per sezione, argS1: {"gruppo_minimo": "H", "gruppo_massimo": "P", "rapporto": 1.1516762971528294, "intervalli_separati": false, "esito": "uniforme"}
- per sezione, argF1: {"gruppo_minimo": "B", "gruppo_massimo": "H", "rapporto": 1.099568999024644, "intervalli_separati": false, "esito": "uniforme"}
- per sezione, tecM1: {"gruppo_minimo": "P", "gruppo_massimo": "H", "rapporto": 1.4340629240917686, "intervalli_separati": false, "esito": "uniforme"}
- per sezione, tecP1: {"gruppo_minimo": "P", "gruppo_massimo": "H", "rapporto": 1.8668371552822374, "intervalli_separati": true, "esito": "varia"}
- per tipo di pagina, latGeom: {"gruppo_minimo": "S ricette", "gruppo_massimo": "H erbario", "rapporto": 3.5880804173558816, "intervalli_separati": true, "esito": "varia"}
- per tipo di pagina, ingGeom: {"gruppo_minimo": "etichette", "gruppo_massimo": "H erbario", "rapporto": 1.9586044088023051, "intervalli_separati": false, "esito": "uniforme"}
- per tipo di pagina, argP1: {"gruppo_minimo": "etichette", "gruppo_massimo": "H erbario", "rapporto": 1.1798537089057106, "intervalli_separati": false, "esito": "uniforme"}
- per tipo di pagina, argR1: {"gruppo_minimo": "S ricette", "gruppo_massimo": "H erbario", "rapporto": 1.4229606829576742, "intervalli_separati": true, "esito": "zona grigia"}
- per tipo di pagina, argS1: {"gruppo_minimo": "altro", "gruppo_massimo": "S ricette", "rapporto": 1.216013248781121, "intervalli_separati": false, "esito": "uniforme"}
- per tipo di pagina, argF1: {"gruppo_minimo": "altro", "gruppo_massimo": "H erbario", "rapporto": 1.0753495217608078, "intervalli_separati": false, "esito": "uniforme"}
- per tipo di pagina, tecM1: {"gruppo_minimo": "S ricette", "gruppo_massimo": "H erbario", "rapporto": 1.2388693854347135, "intervalli_separati": false, "esito": "uniforme"}
- per tipo di pagina, tecP1: {"gruppo_minimo": "etichette", "gruppo_massimo": "H erbario", "rapporto": 1.3863249132721154, "intervalli_separati": false, "esito": "uniforme"}

## v21 contro vere (media dei libri meno vere)

| misura | vere | v21 | differenza | rapporto |
|---|---|---|---|---|
| E_vic_c | +0.0116 (+0.0099; +0.0134) | +0.0097 (+0.0090; +0.0104) | -0.0019 (-0.0037; -0.0001) | 0.84 |
| E_lon_c | +0.0057 (+0.0044; +0.0072) | +0.0048 (+0.0043; +0.0054) | -0.0009 (-0.0025; +0.0005) | 0.84 |
| H | +0.4950 (+0.4064; +0.5800) | +0.4980 (+0.4536; +0.5456) | +0.0031 (-0.0849; +0.0981) | 1.01 |
| QV_vic | +0.7428 (+0.7184; +0.7642) | +0.7482 (+0.7354; +0.7606) | +0.0055 (-0.0211; +0.0331) | 1.01 |
| QL | +0.7648 (+0.7191; +0.8086) | +0.7360 (+0.7166; +0.7559) | -0.0288 (-0.0761; +0.0209) | 0.96 |
| loc_rel | +0.5050 (+0.4200; +0.5936) | +0.5020 (+0.4544; +0.5464) | -0.0031 (-0.0981; +0.0849) | 0.99 |
| Q | +0.8815 (+0.6895; +1.1061) | +0.7751 (+0.7029; +0.8639) | -0.1064 (-0.3333; +0.0946) | 0.88 |

## Ponte con ia09: copia netta in bit per parola (modelli di ia09) per sezione e tipo di pagina

| gruppo | pagine | copia netta (bit) | guadagno g (bit) | quota di copia rho |
|---|---|---|---|---|
| tutte | - | +0.105 (+0.091; +0.120) | - | - |
| sezione B | 19 | +0.164 (+0.143; +0.183) | +0.165 (+0.141; +0.185) | +0.64 (+0.60; +0.68) |
| sezione C | 5 | +0.068 (-0.078; +0.128) | +0.088 (-0.013; +0.132) | +0.67 (+0.00; +0.95) |
| sezione H | 128 | +0.091 (+0.070; +0.115) | +0.099 (+0.077; +0.123) | +0.79 (+0.71; +0.85) |
| sezione P | 16 | +0.098 (+0.044; +0.153) | +0.114 (+0.074; +0.163) | +0.84 (+0.70; +0.91) |
| sezione S | 25 | +0.094 (+0.064; +0.123) | +0.097 (+0.067; +0.127) | +0.66 (+0.56; +0.73) |
| sezione T | 6 | +0.089 (-0.002; +0.170) | +0.086 (-0.004; +0.165) | +0.69 (+0.09; +0.86) |
| tipo_di_pagina H erbario | 128 | +0.091 (+0.070; +0.115) | +0.099 (+0.077; +0.123) | +0.79 (+0.71; +0.85) |
| tipo_di_pagina S ricette | 25 | +0.094 (+0.064; +0.123) | +0.097 (+0.067; +0.127) | +0.66 (+0.56; +0.73) |
| tipo_di_pagina T solo testo | 6 | +0.089 (-0.002; +0.170) | +0.086 (-0.004; +0.165) | +0.69 (+0.09; +0.86) |
| tipo_di_pagina altro | 10 | +0.143 (+0.116; +0.169) | +0.141 (+0.109; +0.170) | +0.63 (+0.56; +0.72) |
| tipo_di_pagina circolare o raggi | 6 | -0.001 (-0.090; +0.071) | +0.034 (-0.034; +0.104) | +0.00 (+0.00; +0.85) |
| tipo_di_pagina etichette | 27 | +0.148 (+0.113; +0.175) | +0.156 (+0.128; +0.180) | +0.71 (+0.66; +0.77) |
