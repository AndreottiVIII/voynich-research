# Verifica della replica

Riferimento: `origine`. "Identico" = stesso file byte per byte.

| risultato | esito | valori | diversi | scarto rel. max | note |
|---|---|---|---|---|---|
| e01_prevedibilita.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 2351 | 1460 | 4.46e-10 | struttura diversa: 0 valori solo nel vecchio, 21 solo nel nuovo (Chinese-pinyin) |
| e02_impronta.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 10042 | 3090 | 1.14e-10 |  |
| e03_genere.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 521 | 180 | 1.57e-11 |  |
| e04_vicinato.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 1855 | 396 | 1.48e-12 |  |
| e05_righe.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 286 | 91 | 3.65e-13 |  |
| e06_currier.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 600 | 349 | 8.38e-13 |  |
| e07_codifiche.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 313 | 91 | 1.48e-09 |  |
| e07_compromesso_verboso.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 1802 | 432 | 2.14e-14 |  |
| e08_autocitazione.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 920 | 24 | 3.32e-09 |  |
| e09_sintesi.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 226 | 113 | 1.53e-08 |  |
| e10_naibbe.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 234 | 125 | 1.63e-09 |  |
| e11_spazi.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 732 | 435 | 5.42e-13 |  |
| e12_giunture.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 499 | 14 | 6.72e-12 |  |
| e13_profilo.json | diverso: 244 valori oltre 1e-09 | 258 | 244 | 1.84e+00 | `/con_somiglianza/distanza_dal_piu_vicino_fra_lingue/massimo`: 4.059797207385766 → 6.6355759374811445; `/con_somiglianza/distanza_dal_piu_vicino_fra_lingue/mediana`: 1.4203439409133545 → 1.299200083622501; `/con_somiglianza/distanza_voynich_dal_piu_vicino`: 9.869365541095659 → 9.236774796583202; struttura diversa: 0 valori solo nel vecchio, 2 solo nel nuovo (lingue) |
| e14_decifrazione.json | stessi valori | 138 | 0 | 0.00e+00 | struttura diversa: 1433 valori solo nel vecchio, 0 solo nel nuovo (Voynich, glifi, Voynich, glifi e serie di i, controllo Naibbe (Plinio cifrato), controllo negativo) |
| e15_zodiaco.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 300 | 3 | 1.03e-15 |  |
| e16_senza_spazi.json | identico | | 0 | 0 | |
| e17_ricottura.json | identico | | 0 | 0 | |
| e18_anagrammi.json | identico | | 0 | 0 | |
| e19_tutte_le_lingue.json | identico | | 0 | 0 | |
| e20_gradi.json | identico | | 0 | 0 | |
| e21_sondaggi.json | identico | | 0 | 0 | |
| e22_timm_schinner.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 132 | 36 | 1.62e-10 |  |
| e23_giunture.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 555 | 149 | 8.60e-12 |  |
| e24_varieta.json | stessi valori (entro 1e-09 relativo o 1e-12 assoluto) | 364 | 112 | 2.48e-11 |  |
| e25_preghiere.json | identico | | 0 | 0 | |
| e26_decifrazioni_pubblicate.json | identico | | 0 | 0 | |
| e27_cartigli.json | identico | | 0 | 0 | |
| e28_letture.json | identico | | 0 | 0 | |
| e30_elenchi_medievali.json | nuovo | | | | assente nel riferimento |
| e31_naibbe_deriva.json | nuovo | | | | assente nel riferimento |
| e34_spazi_fisici.json | nuovo | | | | assente nel riferimento |
| e35_farmacia_erbario.json | nuovo | | | | assente nel riferimento |
| e36_posizione_pagina.json | nuovo | | | | assente nel riferimento |
| e36_posizione_pagina_esplorativo.json | nuovo | | | | assente nel riferimento |
| e37_posizione_sezione.json | nuovo | | | | assente nel riferimento |
| e37_posizione_sezione_dettaglio.json | nuovo | | | | assente nel riferimento |
| e38_lingua_ignota.json | nuovo | | | | assente nel riferimento |
| e39_h2_arxiv.json | nuovo | | | | assente nel riferimento |
| e40_etichette_tipo.json | nuovo | | | | assente nel riferimento |
| e40_etichette_tipo_lunghezza.json | nuovo | | | | assente nel riferimento |
| e41_gibberish.json | nuovo | | | | assente nel riferimento |
| e42_lotti.json | nuovo | | | | assente nel riferimento |
| e43_ibrido.json | nuovo | | | | assente nel riferimento |
