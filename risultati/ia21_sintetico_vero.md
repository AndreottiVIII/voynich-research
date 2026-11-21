# IA21 (ia21) — L'allievo e l'esaminatore: testo sintetico, percorso vero

Preregistrazione: `preregistrazioni/ia21.md`. **Prova sui soli controlli (non Voynich).**

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Parametri: giri_max 12, candidate 8, peso_scelte 1.0, epoche_affina 1, lr_affina 0.0005, libri_monitoraggio 3, libri_finali 20, libri_struttura 6, guardie_fermano True.

## Controlli dei giudici (sul testo sintetico)

- Giudici del paper, positivo (giudice 2, parole rimescolate): AUC 0,777, soglia ≥ 0,95 → NO.
- Giudici del paper, negativo (etichette a caso): giudice 1 0,529, giudice 2 0,527 → sì.
- K: positivo parole 0,994, ordine1 1,000 → sì; negativo 0,544 → sì; vede il v21 (AUC 1,000, soglia ≥ 0,65) → sì.
- A: positivo parole 0,985, ordine1 1,000 → sì; negativo 0,500 → sì.

## I giri (AUC: più basso = più vicino al vero)

| giro | esaminatore prima | esaminatore dopo | giudice 1 | giudice 2 | K | A (amico) | media dei tre | guardie violate |
|---|---|---|---|---|---|---|---|---|
| 0 | — | — | 0,981 | 0,995 | 0,795 | 0,796 | 0,924 | — |
| 1 | 0,961 | 0,882 | 0,977 | 0,991 | 0,775 | 0,845 | 0,915 | — |
| 2 | 0,956 | 0,882 | 0,975 | 0,993 | 0,741 | 0,848 | 0,903 | — |
| 3 | 0,892 | 0,863 | 0,975 | 0,991 | 0,747 | 0,853 | 0,904 | — |
| 4 | 0,943 | 0,889 | 0,976 | 0,992 | 0,739 | 0,850 | 0,902 | — |
| 5 | 0,932 | 0,910 | 0,979 | 0,991 | 0,729 | 0,845 | 0,900 | — |

Arresto: **giro 5** (3 giri senza miglioramento (media dei tre giudici)). Ultimo giro valido: 5.

## Libri finali (20 libri nuovi, un giudice per libro)

| | giudice 1 | giudice 2 | K | A (amico) | media dei tre |
|---|---|---|---|---|---|
| partenza (giro 0) | 0,983 ± 0,001 | 0,995 ± 0,000 | 0,797 ± 0,002 | 0,792 ± 0,004 | 0,925 |
| finale (giro 5) | 0,979 ± 0,001 | 0,989 ± 0,001 | 0,724 ± 0,002 | 0,842 ± 0,002 | 0,897 |
| v21 (paper; K e A ricalcolati) | 0,554 ± 0,004 | 0,601 ± 0,005 | 1,000 ± 0,000 | — | — |

## Letture preregistrate

- Esaminatore valido (AUC al giro 1 sull'allievo di partenza 0,961, soglia 0,65): sì.
- **L1, finale contro il v21: solo K scende: possibile giudice amico, non vale come sì (e almeno due giudici su tre sono "più lontano").** e231 più lontano (differenza 0,425 ± 0,004); e266 più lontano (differenza 0,388 ± 0,005); K più vicino (differenza -0,276 ± 0,002). A (amico, riportato): non calcolabile.
- **L1b, finale contro il giro 0: zona grigia.** e231 uguale entro l'errore (differenza sotto 0,01) (differenza -0,004 ± 0,001); e266 uguale entro l'errore (differenza sotto 0,01) (differenza -0,005 ± 0,001); K più vicino (differenza -0,072 ± 0,003). A (amico, riportato): più lontano.
- **L4, giudice amico: fermo: ne' l'esaminatore ne' i giudici tenuti da parte si muovono.** Esaminatore: AUC 0,961 al giro 1 (sull'allievo di partenza) → 0,910 sull'ultimo allievo (calo 0,051); media dei tre giudici: calo 0,027; giudici "più vicino" al giro 0: 1 su 3.
- **Controllo positivo (testo non Voynich): non riuscito o non leggibile.** sintetico: non riuscito (calo 0,027)
- **Controllo negativo (esaminatore cieco): non eseguito.**

## Che cosa resta lontano dal vero a fine percorso

- Profilo di sorpresa del giudice A: differenze rimaste almeno a metà di quelle di partenza: inizio_riga.
- Gruppi del giudice 2 ancora riconoscibili (AUC ≥ 0,65): G3 0,98, G6 0,82, G9 0,74, G2 0,69, G1 0,66.

## Che cosa l'esaminatore sembra usare (associazione, non prova)

- giro 1, pagine dell'allievo di partenza: gruppi del giudice 2 (|ρ| medio): G1 0,18, G2 0,21, G3 0,24, G4 0,10, G5 0,01, G6 0,07, G7 0,16, G8 0,09, G9 0,45. Più associate: G9 JSD pagina-manoscritto -0,52; G2 u+s 0,45; G2 d+i 0,45; G2 b+r 0,45. Profilo di A (ρ): bit_medi -0,30, bit_sd -0,20, bit_p95 -0,12, inizio_parola -0,29, inizio_riga -0,08, dentro_parola -0,29, spazio -0,17, fine_riga 0,22, riga_paragrafo -0,23, riga_altra -0,30, quarto1 -0,24, quarto2 -0,25, quarto3 -0,27, quarto4 -0,29.
- giro 5, pagine dell'ultimo giro valido: gruppi del giudice 2 (|ρ| medio): G1 0,18, G2 0,20, G3 0,21, G4 0,11, G5 0,01, G6 0,19, G7 0,17, G8 0,08, G9 0,53. Più associate: G9 JSD pagina-manoscritto -0,58; G9 JSD prima-seconda meta -0,48; G3 fra le 100 piu frequenti 0,47; G2 i+l 0,41. Profilo di A (ρ): bit_medi -0,44, bit_sd -0,46, bit_p95 -0,38, inizio_parola -0,30, inizio_riga -0,18, dentro_parola -0,45, spazio -0,29, fine_riga 0,09, riga_paragrafo -0,33, riga_altra -0,44, quarto1 -0,39, quarto2 -0,38, quarto3 -0,40, quarto4 -0,38.

## Tempi (minuti per lavoro, macchina condivisa)

- base: 5 lavori, media 10.6, massimo 12.2, totale 53.1.
- ctrl: 7 lavori, media 0.2, massimo 0.3, totale 1.1.
- Kctrl: 5 lavori, media 0.4, massimo 0.4, totale 1.8.
- K: 40 lavori, media 0.1, massimo 0.3, totale 2.9.
- lmA: 10 lavori, media 3.0, massimo 4.2, totale 29.7.
- misura: 58 lavori, media 0.3, massimo 0.6, totale 16.7.
- naturale: 1 lavori, media 0.0, massimo 0.0, totale 0.0.
- scrivi0: 5 lavori, media 3.4, massimo 4.4, totale 16.9.
- finale: 5 lavori, media 0.9, massimo 1.0, totale 4.6.
- giro: 25 lavori, media 7.1, massimo 13.1, totale 176.4.
