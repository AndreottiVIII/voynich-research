# IA28 (ia28): l'inferenza per simulazione sui procedimenti (solo numeri)

Tre famiglie di procedimenti con parametri stimati (ABC) su 29 statistiche classiche di quarti di libro; controllo su misure tenute fuori su libri interi. Non e' una decifrazione. Modalita: testo vero. Tabella: 20000 testi per famiglia.

## Controlli

| famiglia | C1 famiglia ritrovata | C2 parametri nell'intervallo | C3 verifica predittiva calibrata |
|---|---|---|---|
| CV | si (1.00) | si | si (1.00) |
| NB | si (1.00) | si | si (1.00) |
| VT | si (1.00) | si | si (1.00) |

Controlli negativi (nessuna famiglia deve vincere): latino in chiaro: si (famiglia CV preferita ma NON compatibile (verifica predittiva fallita)), testo rimescolato: si (famiglia NB preferita ma NON compatibile (verifica predittiva fallita))

## Parametri stimabili e coperture (controlli positivi)

| famiglia | parametro | R2 fuori sacco | stimabile | copertura 90% |
|---|---|---|---|---|
| CV | nu | 0.88 | si | 0.93 |
| CV | tau | 0.93 | si | 0.91 |
| CV | p_lontano | 0.83 | si | 0.93 |
| CV | b_pos | 0.04 | no | 0.92 |
| CV | p_mod | 0.96 | si | 0.91 |
| CV | q_sost | 0.75 | si | 0.90 |
| CV | p_sim | 0.33 | si | 0.91 |
| CV | w_contatto | 0.82 | si | 0.91 |
| NB | conc | 0.88 | si | 0.87 |
| NB | p_eco | 0.98 | si | 0.86 |
| NB | q_tema | 0.91 | si | 0.91 |
| VT | T | 0.96 | si | 0.91 |
| VT | A | 0.97 | si | 0.92 |
| VT | b | 0.92 | si | 0.91 |
| VT | p_eco | 0.98 | si | 0.88 |
| VT | q_tema | 0.88 | si | 0.95 |

## L1 famiglia migliore

Esito: **famiglia NB preferita ma NON compatibile (verifica predittiva fallita)** (leggibile: si). Piu' vicina per scarto medio (rms z): VT.

| famiglia | prob. media | quarti preferita | quarti con verifica passata | rms z medio | statistiche mancate (n. quarti) |
|---|---|---|---|---|---|
| CV | 0.09 | 0 | 0 | 18.66 | H1 (4), H2 (4), H3 (4), H_primo (4), H_ultimo (4), tipi_su_parole (4), quota_una_pagina (4), ripetute_subito (4) |
| NB | 0.86 | 4 | 0 | 32.34 | lung_media (4), lung_sd (4), H_ultimo (4), quota_vicini (4), ripetute_subito (4), contatto (4), bordo_inizio_primo (4), bordo_inizio_ultimo (4) |
| VT | 0.06 | 0 | 0 | 13.95 | lung_sd (4), H0 (4), H1 (4), H2 (4), H_ultimo (4), contatto (4), eco_mod_R247 (4), bordo_inizio_primo (4) |

## L2 parametri (mediana e intervallo al 90%, solo parametri stimabili)

**CV** (leggibile: si; non stimabili: b_pos)

| parametro | mediana | q05 | q95 | R2 | largo | ai bordi |
|---|---|---|---|---|---|---|
| nu | 0.114 | 0.066 | 0.148 | 0.88 | no | no |
| tau | 1.488 | 1.072 | 1.886 | 0.93 | no | no |
| p_lontano | 0.300 | 0.268 | 0.300 | 0.83 | no | si |
| p_mod | 0.497 | 0.444 | 0.557 | 0.96 | no | no |
| q_sost | 0.590 | 0.303 | 0.862 | 0.75 | no | no |
| p_sim | 0.298 | 0.006 | 0.859 | 0.33 | no | no |
| w_contatto | 2.439 | 1.846 | 2.986 | 0.82 | no | no |

**NB** (leggibile: si; non stimabili: nessuno)

| parametro | mediana | q05 | q95 | R2 | largo | ai bordi |
|---|---|---|---|---|---|---|
| conc | 4.014 | 2.168 | 14.101 | 0.88 | no | no |
| p_eco | 0.129 | 0.065 | 0.170 | 0.98 | no | no |
| q_tema | 0.436 | 0.166 | 0.628 | 0.91 | no | no |

**VT** (leggibile: si; non stimabili: nessuno)

| parametro | mediana | q05 | q95 | R2 | largo | ai bordi |
|---|---|---|---|---|---|---|
| T | 3 | 3 | 4 | 0.96 | no | no |
| A | 15 | 14 | 16 | 0.97 | no | no |
| b | 0.718 | 0.574 | 0.868 | 0.92 | no | no |
| p_eco | 0.200 | 0.162 | 0.241 | 0.98 | no | no |
| q_tema | 0.207 | 0.094 | 0.333 | 0.88 | no | no |

## L5 Naibbe vero senza eco

p_eco: mediana 0.129, intervallo 0.065 - 0.170; l'eco e' necessaria (limite basso sopra 0,05): si (leggibile: si)

## L3 misure tenute fuori al vero

| famiglia | quota al vero | misure confrontate | al vero | mancate |
|---|---|---|---|---|
| CV copia e varia | 0.19 | 21 | no | H4, H5, righe_sopra_uguali, righe_2sopra_uguali, in_riga_d1, in_riga_d2, heaps, consecutive_meno_caso, k90, GL, GR, R_rel, Q, copia_netta, lam, rho, D |
| NB Naibbe vero + eco (nomi riallineati) | 0.76 | 21 | si | copia_netta, lam, rho, G9, D |
| NB (nomi nativi) | 0.76 | 21 | si | copia_netta, lam, rho, G9, D |
| VT verboso + eco + bordi | 0.48 | 21 | no | in_riga_d2, in_riga_d3, consecutive_meno_caso, k90, R_rel, Q, copia_netta, lam, rho, G9, D |

## L4 contro il v21 (misura per misura: famiglia piu' vicina / uguale / piu' lontana del v21)

- CV copia e varia: {"piu' lontana": 16, "uguale entro l'errore": 5}
- NB Naibbe vero + eco (nomi riallineati): {"piu' lontana": 8, "uguale entro l'errore": 10, "piu' vicina": 3}
- VT verboso + eco + bordi: {"uguale entro l'errore": 8, "piu' lontana": 12, "piu' vicina": 1}

## L6 giudici (AUC media sui libri; classe: regge <= 0,62, grigia <= 0,65, vede)

Validita dei giudici: OrderedDict({'parole_rimescolate_e231': True, 'parole_rimescolate_e266': True, 'negativo_K_in_banda': False, 'negativo_K': 0.5709244191745908})

| colonna | e231 | e266 | A | K |
|---|---|---|---|---|
| CV copia e varia | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) |
| NB Naibbe vero + eco (nomi riallineati) | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) |
| NB (nomi nativi) | 1.000 (vede) | 1.000 (vede) | 0.998 (vede) | 0.993 (vede) |
| VT verboso + eco + bordi | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) | 1.000 (vede) |
| v21 | 0.552 (regge) | 0.601 (regge) | 0.751 (vede) | 0.767 (vede) |

## Dichiarato

- Le statistiche di sintesi (29) sono classiche e a basso costo; le misure di rete, di struttura e i giudici stanno FUORI dalla stima. Le misure di copia netta, rho e Λ di ia09 sono parenti stretti delle statistiche d'eco di sintesi: sono "fuori" nel senso che non sono usate, non che siano indipendenti.
- L'osservazione e' ognuno dei quattro quarti del testo (pagine a giro), analizzato per conto suo; le simulazioni sono quarti con la stessa impaginazione.
- I testi delle famiglie CV e VT hanno glifi con nomi tirati a caso: per i giudici i libri sono riallineati per rango di frequenza ai glifi del vero (non cambia nessuna struttura). Per NB si riportano anche i nomi nativi (colonna NBn).
- Il v21 non e' una famiglia a parametri liberi (i suoi parametri vengono dal Voynich e il voynichizzatore non si tocca): e' una colonna di riferimento.
- Il Voynich e' eterogeneo (lingue A e B, sezioni, mani); le famiglie scrivono un testo omogeneo. Una verifica predittiva fallita puo' dipendere anche da questo.
