# IA21 (ia21) — L'allievo e l'esaminatore: testo voynich, percorso cieco

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
| 1 | 0,534 | 0,480 | 0,771 | 0,850 | 0,778 | 0,675 | 0,800 | — |
| 2 | 0,512 | 0,502 | 0,773 | 0,879 | 0,782 | 0,649 | 0,811 | — |
| 3 | 0,465 | 0,424 | 0,800 | 0,904 | 0,788 | 0,623 | 0,831 | — |
| 4 | 0,526 | 0,520 | 0,844 | 0,888 | 0,795 | 0,685 | 0,842 | — |

Arresto: **giro 4** (3 giri senza miglioramento (media dei tre giudici)). Ultimo giro valido: 4.

## Libri finali (20 libri nuovi, un giudice per libro)

| | giudice 1 | giudice 2 | K | A (amico) | media dei tre |
|---|---|---|---|---|---|
| partenza (giro 0) | 0,798 ± 0,004 | 0,858 ± 0,004 | 0,760 ± 0,004 | 0,693 ± 0,004 | 0,805 |
| finale (giro 4) | 0,847 ± 0,003 | 0,889 ± 0,003 | 0,786 ± 0,003 | 0,682 ± 0,004 | 0,841 |
| v21 (paper; K e A ricalcolati) | 0,554 ± 0,004 | 0,601 ± 0,005 | 0,766 ± 0,005 | 0,746 ± 0,005 | — |

## Letture preregistrate

- Esaminatore valido (AUC al giro 1 sull'allievo di partenza 0,534, soglia 0,65): NO.
- **L1, finale contro il v21: più lontano dal vero del v21 (ma l'esaminatore era debole al giro 1: non vale come merito dell'esaminatore).** e231 più lontano (differenza 0,293 ± 0,005); e266 più lontano (differenza 0,288 ± 0,006); K più lontano (differenza 0,020 ± 0,005). A (amico, riportato): più vicino.
- **L1b, finale contro il giro 0: peggio del giro 0 (ma l'esaminatore era debole al giro 1).** e231 più lontano (differenza 0,049 ± 0,005); e266 più lontano (differenza 0,031 ± 0,005); K più lontano (differenza 0,027 ± 0,005). A (amico, riportato): uguale entro l'errore.
- **L4, giudice amico: fermo: ne' l'esaminatore ne' i giudici tenuti da parte si muovono.** Esaminatore: AUC 0,534 al giro 1 (sull'allievo di partenza) → 0,520 sull'ultimo allievo (calo 0,013); media dei tre giudici: calo -0,035; giudici "più vicino" al giro 0: 0 su 3.
- **Controllo positivo (testo non Voynich): non riuscito o non leggibile.** latino: non eseguito (calo —); sintetico: non eseguito (calo —); locale: non eseguito (calo —)
- **Controllo negativo (esaminatore cieco): riuscito: non migliora.**

## Che cosa resta lontano dal vero a fine percorso

- Profilo di sorpresa del giudice A: differenze rimaste almeno a metà di quelle di partenza: inizio_parola, inizio_riga, fine_riga.
- Gruppi del giudice 2 ancora riconoscibili (AUC ≥ 0,65): G3 0,77, G2 0,74, G1 0,73, G9 0,72, G8 0,65.

## Che cosa l'esaminatore sembra usare (associazione, non prova)

- giro 1, pagine dell'allievo di partenza: gruppi del giudice 2 (|ρ| medio): G1 0,04, G2 0,04, G3 0,05, G4 0,04, G5 0,01, G6 0,02, G7 0,05, G8 0,02, G9 0,12. Più associate: G9 JSD prima-seconda meta 0,14; G2 h+y -0,13; G2 e+k -0,12; G2 o+i 0,12. Profilo di A (ρ): bit_medi 0,02, bit_sd 0,03, bit_p95 0,00, inizio_parola 0,06, inizio_riga 0,05, dentro_parola -0,03, spazio 0,03, fine_riga 0,03, riga_paragrafo 0,04, riga_altra 0,01, quarto1 0,03, quarto2 0,03, quarto3 0,02, quarto4 -0,03.
- giro 4, pagine dell'ultimo giro valido: gruppi del giudice 2 (|ρ| medio): G1 0,03, G2 0,03, G3 0,02, G4 0,02, G5 0,03, G6 0,02, G7 0,02, G8 0,05, G9 0,03. Più associate: G1 z -0,10; G2 p+o 0,09; G8 k prime righe meno altre -0,08; G2 s+e 0,08. Profilo di A (ρ): bit_medi -0,02, bit_sd -0,03, bit_p95 -0,01, inizio_parola 0,02, inizio_riga -0,06, dentro_parola -0,02, spazio -0,01, fine_riga 0,02, riga_paragrafo 0,01, riga_altra -0,02, quarto1 -0,01, quarto2 -0,00, quarto3 -0,01, quarto4 -0,02.

## Tempi (minuti per lavoro, macchina condivisa)

- ctrl: 7 lavori, media 0.1, massimo 0.3, totale 0.9.
- D: 5 lavori, media 0.2, massimo 0.3, totale 1.2.
- Kctrl: 5 lavori, media 0.1, massimo 0.1, totale 0.3.
- K: 35 lavori, media 0.1, massimo 0.3, totale 3.7.
- misura: 55 lavori, media 0.4, massimo 0.8, totale 23.9.
- M: 13 lavori, media 0.8, massimo 0.9, totale 9.8.
- naturale: 1 lavori, media 0.0, massimo 0.0, totale 0.0.
- scrivi0: 5 lavori, media 2.4, massimo 2.7, totale 11.9.
- finale: 5 lavori, media 1.5, massimo 1.7, totale 7.5.
- giro: 20 lavori, media 38.3, massimo 78.4, totale 765.9.
