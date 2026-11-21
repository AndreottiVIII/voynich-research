# IA21 (ia21) — L'allievo e l'esaminatore: testo voynich, percorso vero

Preregistrazione: `preregistrazioni/ia21.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Parametri: giri_max 12, candidate 8, peso_scelte 1.0, epoche_affina 1, lr_affina 0.0005, libri_monitoraggio 3, libri_finali 20, libri_struttura 6, guardie_fermano True.

## Controlli dei giudici (sul testo voynich)

- Giudici del paper, positivo (giudice 2, parole rimescolate): AUC 0,988, soglia ≥ 0,95 → sì.
- Giudici del paper, negativo (etichette a caso): giudice 1 0,506, giudice 2 0,503 → sì.
- K: positivo parole 0,982, e192 0,935 → sì; negativo 0,499 → sì; vede il v21 (AUC 0,766, soglia ≥ 0,65) → sì.
- A: positivo parole 0,986, e192 0,958 → sì; negativo 0,484 → sì.

## I giri (AUC: più basso = più vicino al vero)

| giro | esaminatore prima | esaminatore dopo | giudice 1 | giudice 2 | K | A (amico) | media dei tre | guardie violate |
|---|---|---|---|---|---|---|---|---|
| 0 | — | — | 0,799 | 0,854 | 0,764 | 0,704 | 0,805 | — |
| 1 | 0,934 | 0,730 | 0,791 | 0,881 | 0,738 | 0,623 | 0,803 | — |
| 2 | 0,819 | 0,705 | 0,817 | 0,885 | 0,734 | 0,602 | 0,812 | — |
| 3 | 0,801 | 0,598 | 0,788 | 0,861 | 0,754 | 0,661 | 0,801 | — |

Arresto: **giro 3** (3 giri senza miglioramento (media dei tre giudici)). Ultimo giro valido: 3.

## Libri finali (20 libri nuovi, un giudice per libro)

| | giudice 1 | giudice 2 | K | A (amico) | media dei tre |
|---|---|---|---|---|---|
| partenza (giro 0) | 0,798 ± 0,004 | 0,858 ± 0,004 | 0,760 ± 0,004 | 0,693 ± 0,004 | 0,805 |
| finale (giro 3) | 0,805 ± 0,005 | 0,877 ± 0,005 | 0,769 ± 0,004 | 0,653 ± 0,003 | 0,817 |
| v21 (paper; K e A ricalcolati) | 0,554 ± 0,004 | 0,601 ± 0,005 | 0,766 ± 0,005 | 0,746 ± 0,005 | — |

## Letture preregistrate

- Esaminatore valido (AUC al giro 1 sull'allievo di partenza 0,934, soglia 0,65): sì.
- **L1, finale contro il v21: più lontano dal vero del v21.** e231 più lontano (differenza 0,251 ± 0,007); e266 più lontano (differenza 0,276 ± 0,007); K uguale entro l'errore (differenza 0,003 ± 0,006). A (amico, riportato): più vicino.
- **L1b, finale contro il giro 0: zona grigia.** e231 uguale entro l'errore (differenza 0,007 ± 0,007); e266 più lontano (differenza 0,019 ± 0,006); K uguale entro l'errore (differenza 0,009 ± 0,006). A (amico, riportato): più vicino.
- **L4, giudice amico: impara a ingannare l'esaminatore, non a scrivere il Voynich.** Esaminatore: AUC 0,934 al giro 1 (sull'allievo di partenza) → 0,598 sull'ultimo allievo (calo 0,337); media dei tre giudici: calo -0,012; giudici "più vicino" al giro 0: 0 su 3.
- **L5, esaminatore vero contro cieco: l'esaminatore vero fa meglio di quello cieco.** e231 più vicino; e266 più vicino; K più vicino.
- **Controllo positivo (testo non Voynich): non riuscito o non leggibile.** latino: non leggibile: la partenza e' sopra il soffitto (0,97): i giudici non distinguono i miglioramenti (calo 0,000); sintetico: non riuscito (calo 0,027); locale: non leggibile: la partenza e' sopra il soffitto (0,97): i giudici non distinguono i miglioramenti (calo 0,000)
- **Controllo negativo (esaminatore cieco): riuscito: non migliora.**

## Che cosa resta lontano dal vero a fine percorso

- Struttura che resta lontana (frazione di cammino sotto 0,5): copia_netta, G9. Chiusa almeno a metà: lam, contatto.
- Profilo di sorpresa del giudice A: differenze rimaste almeno a metà di quelle di partenza: inizio_parola, fine_riga.
- Gruppi del giudice 2 ancora riconoscibili (AUC ≥ 0,65): G3 0,78, G9 0,77, G2 0,67.

| misura | vero | partenza | finale | v21 | frazione di cammino | lettura |
|---|---|---|---|---|---|---|
| copia_netta | 0,1099 | 0,0427 | 0,0229 | 0,0531 | -0,29 | resta lontano |
| lam | 0,2014 | 0,0891 | 0,1471 | 0,0650 | 0,52 | chiuso almeno a meta' |
| D | 0,1444 | 0,1491 | 0,1518 | 0,0882 | — | partenza gia' al vero |
| contatto | 0,1884 | 0,1755 | 0,1902 | 0,1850 | 1,14 | chiuso almeno a meta' |
| G9 | 0,0402 | 0,0260 | 0,0224 | 0,0392 | -0,26 | resta lontano |

## Che cosa l'esaminatore sembra usare (associazione, non prova)

- giro 1, pagine dell'allievo di partenza: gruppi del giudice 2 (|ρ| medio): G1 0,05, G2 0,05, G3 0,07, G4 0,05, G5 0,00, G6 0,08, G7 0,04, G8 0,04, G9 0,16. Più associate: G1 r -0,22; G2 e+y 0,21; G3 fra le 100 piu frequenti 0,21; G2 a+r -0,20. Profilo di A (ρ): bit_medi -0,09, bit_sd 0,11, bit_p95 0,05, inizio_parola -0,11, inizio_riga 0,05, dentro_parola -0,09, spazio -0,06, fine_riga 0,18, riga_paragrafo -0,06, riga_altra -0,08, quarto1 -0,10, quarto2 -0,01, quarto3 -0,09, quarto4 -0,07.
- giro 3, pagine dell'ultimo giro valido: gruppi del giudice 2 (|ρ| medio): G1 0,07, G2 0,05, G3 0,13, G4 0,05, G5 0,03, G6 0,11, G7 0,05, G8 0,04, G9 0,19. Più associate: G1 d -0,26; G9 JSD pagina-manoscritto -0,23; G1 l 0,23; G2 e+e 0,18. Profilo di A (ρ): bit_medi -0,16, bit_sd -0,09, bit_p95 -0,15, inizio_parola -0,12, inizio_riga -0,02, dentro_parola -0,15, spazio -0,07, fine_riga 0,01, riga_paragrafo -0,11, riga_altra -0,17, quarto1 -0,17, quarto2 -0,09, quarto3 -0,10, quarto4 -0,10.

## Tempi (minuti per lavoro, macchina condivisa)

- ctrl: 7 lavori, media 0.1, massimo 0.3, totale 0.9.
- D: 10 lavori, media 0.2, massimo 0.3, totale 2.2.
- Kctrl: 5 lavori, media 0.1, massimo 0.1, totale 0.3.
- K: 30 lavori, media 0.1, massimo 0.3, totale 3.7.
- misura: 52 lavori, media 0.5, massimo 0.7, totale 23.7.
- M: 19 lavori, media 0.8, massimo 0.9, totale 14.3.
- naturale: 1 lavori, media 0.0, massimo 0.0, totale 0.0.
- scrivi0: 5 lavori, media 2.4, massimo 2.7, totale 11.9.
- finale: 5 lavori, media 2.0, massimo 2.3, totale 9.9.
- giro: 15 lavori, media 15.8, massimo 18.6, totale 237.1.
