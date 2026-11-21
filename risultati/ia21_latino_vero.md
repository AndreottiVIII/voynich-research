# IA21 (ia21) — L'allievo e l'esaminatore: testo latino, percorso vero

Preregistrazione: `preregistrazioni/ia21.md`. **Prova sui soli controlli (non Voynich).**

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Parametri: giri_max 12, candidate 8, peso_scelte 1.0, epoche_affina 1, lr_affina 0.0005, libri_monitoraggio 3, libri_finali 20, libri_struttura 6, guardie_fermano True.

## Controlli dei giudici (sul testo latino)

- Giudici del paper, positivo (giudice 2, parole rimescolate): AUC 0,861, soglia ≥ 0,95 → NO.
- Giudici del paper, negativo (etichette a caso): giudice 1 0,475, giudice 2 0,477 → sì.
- K: positivo parole 0,778, ordine1 1,000 → NO; negativo 0,526 → sì; vede il v21 (AUC 1,000, soglia ≥ 0,65) → sì.
- A: positivo parole 0,737, ordine1 1,000 → NO; negativo 0,528 → sì.

## I giri (AUC: più basso = più vicino al vero)

| giro | esaminatore prima | esaminatore dopo | giudice 1 | giudice 2 | K | A (amico) | media dei tre | guardie violate |
|---|---|---|---|---|---|---|---|---|
| 0 | — | — | 0,983 | 0,987 | 0,991 | 0,767 | 0,987 | — |
| 1 | 0,905 | 0,788 | 0,984 | 0,991 | 0,992 | 0,790 | 0,989 | parole nuove nella fascia del vero |

Arresto: **giro 1** (guardia violata: parole nuove nella fascia del vero). Ultimo giro valido: 0.

## Libri finali (20 libri nuovi, un giudice per libro)

| | giudice 1 | giudice 2 | K | A (amico) | media dei tre |
|---|---|---|---|---|---|
| partenza (giro 0) | 0,978 ± 0,001 | 0,983 ± 0,001 | 0,993 ± 0,000 | 0,780 ± 0,004 | 0,984 |
| finale (giro 0) | 0,978 ± 0,001 | 0,983 ± 0,001 | 0,993 ± 0,000 | 0,780 ± 0,004 | 0,984 |
| v21 (paper; K e A ricalcolati) | 0,554 ± 0,004 | 0,601 ± 0,005 | 1,000 ± 0,000 | — | — |

## Letture preregistrate

- Esaminatore valido (AUC al giro 1 sull'allievo di partenza 0,905, soglia 0,65): sì.
- **L1, finale contro il v21: più lontano dal vero del v21.** e231 più lontano (differenza 0,424 ± 0,004); e266 più lontano (differenza 0,382 ± 0,005); K uguale entro l'errore (differenza sotto 0,01) (differenza -0,007 ± 0,000). A (amico, riportato): non calcolabile.
- **L1b, finale contro il giro 0: nessun progresso sul giro 0 (uguale entro l'errore).** e231 uguale entro l'errore (differenza 0,000 ± 0,002); e266 uguale entro l'errore (differenza 0,000 ± 0,001); K uguale entro l'errore (differenza 0,000 ± 0,001). A (amico, riportato): uguale entro l'errore.
- **Controllo positivo (testo non Voynich): non riuscito o non leggibile.** latino: non leggibile: la partenza e' sopra il soffitto (0,97): i giudici non distinguono i miglioramenti (calo 0,000)
- **Controllo negativo (esaminatore cieco): non eseguito.**

## Che cosa resta lontano dal vero a fine percorso

- Profilo di sorpresa del giudice A: differenze rimaste almeno a metà di quelle di partenza: bit_medi, bit_sd, bit_p95, inizio_parola, inizio_riga, dentro_parola, spazio, fine_riga, riga_paragrafo, riga_altra, quarto1, quarto2, quarto3, quarto4.
- Gruppi del giudice 2 ancora riconoscibili (AUC ≥ 0,65): G3 1,00, G6 0,94, G1 0,75, G2 0,70, G4 0,66.

## Che cosa l'esaminatore sembra usare (associazione, non prova)

- giro 1, pagine dell'allievo di partenza: gruppi del giudice 2 (|ρ| medio): G1 0,08, G2 0,06, G3 0,15, G4 0,04, G5 0,01, G6 0,16, G7 0,03, G8 0,03, G9 0,04. Più associate: G3 uniche nel testo 0,44; G6 coppie viste altrove -0,40; G1 h -0,20; G1 c -0,20. Profilo di A (ρ): bit_medi 0,16, bit_sd 0,20, bit_p95 0,18, inizio_parola -0,08, inizio_riga 0,01, dentro_parola 0,18, spazio 0,10, fine_riga 0,18, riga_paragrafo 0,11, riga_altra 0,16, quarto1 0,17, quarto2 0,10, quarto3 0,15, quarto4 0,15.

## Tempi (minuti per lavoro, macchina condivisa)

- base: 5 lavori, media 23.0, massimo 32.7, totale 115.2.
- ctrl: 7 lavori, media 0.1, massimo 0.2, totale 0.6.
- Kctrl: 5 lavori, media 0.2, massimo 0.2, totale 1.0.
- K: 15 lavori, media 0.1, massimo 0.2, totale 1.2.
- lmA: 10 lavori, media 3.6, massimo 4.5, totale 36.3.
- misura: 26 lavori, media 0.2, massimo 0.3, totale 6.1.
- naturale: 1 lavori, media 0.0, massimo 0.0, totale 0.0.
- scrivi0: 5 lavori, media 1.4, massimo 1.6, totale 6.8.
- giro: 5 lavori, media 6.6, massimo 7.9, totale 33.2.
