# Esperimento 21: sondaggi sulle strade rimaste aperte

Campioni di al più 20000 parole, in righe da 8 parole e pagine da 20 righe (il Voynich anche con le sue pagine vere). Misure come nella lista di controllo:

- **h2**: incertezza sul segno successivo, in bit (Voynich 2,2; latino 3,3);
- **lunghezza** media delle parole in segni; **diverse**: parole diverse su parole; **hapax**: parole diverse usate una volta sola;
- **ripetute**: parola identica alla precedente, rispetto a due parole qualsiasi della riga (Voynich ×1,0; lingue ×0,12 in mediana);
- **somiglianza**: quanto si somigliano nella grafia due parole diverse della stessa riga, della riga sotto e di 6 righe sotto, rispetto a due parole qualsiasi (Voynich 3,8%, 3,5%, 3,4%; lingue vicino a 0);
- **spazio**: quota dell'incertezza sullo spazio che il segno precedente toglie (Voynich 66%, lingue 17% in mediana).

| strada | testo | h2 | lunghezza | diverse | hapax | ripetute | somiglianza (riga / sotto / 6 righe) | spazio |
|---|---|---|---|---|---|---|---|---|
| Voynich | Voynich (pagine vere) | 2.24 | 4.46 | 0.21 | 0.68 | ×1.01 | 3.8% / 4.0% / 3.4% | 66% |
| Voynich | Voynich (righe finte da 8 parole) | 2.25 | 4.29 | 0.23 | 0.68 | ×0.92 | 4.3% / 3.9% / 2.8% | 66% |
| riferimento | latino (Vangeli) | 3.26 | 5.25 | 0.22 | 0.56 | ×0.18 | 0.2% / 0.3% / 0.1% | 19% |
| abbreviazioni | latino con abbreviazioni leggere | 3.32 | 4.99 | 0.22 | 0.56 | ×0.18 | 0.2% / 0.3% / 0.1% | 27% |
| abbreviazioni | latino con abbreviazioni pesanti | 3.37 | 4.65 | 0.22 | 0.56 | ×0.18 | 0.2% / 0.4% / 0.1% | 32% |
| nulle | latino con nulle a caso (10%) | 3.54 | 5.78 | 0.46 | 0.82 | ×0.10 | 0.3% / 0.5% / 0.2% | 23% |
| nulle | latino con nulle a regola | 2.94 | 5.93 | 0.22 | 0.56 | ×0.18 | 0.4% / 0.4% / 0.2% | 53% |
| trasposizioni | latino, trasposizione a colonne | 3.91 | 5.25 | 0.79 | 0.94 | ×0.00 | 0.2% / 0.1% / 0.1% | 0% |
| trasposizioni | latino, lettere mescolate dentro le parole | 3.85 | 5.25 | 0.61 | 0.90 | ×0.09 | 0.1% / 0.2% / 0.0% | 0% |
| trasposizioni | latino, lettere capovolte dentro le parole | 3.26 | 5.25 | 0.22 | 0.56 | ×0.18 | 0.2% / 0.3% / 0.1% | 13% |
| trasposizioni | latino, lettere ordinate dentro le parole | 2.50 | 5.25 | 0.21 | 0.55 | ×0.20 | 0.1% / 0.3% / 0.1% | 43% |
| elenchi | elenchi della Bibbia latina, 16908 parole | 3.33 | 5.50 | 0.22 | 0.59 | ×0.06 | 0.4% / 0.6% / 0.3% | 14% |
| elenchi | elenchi della Bibbia latina, con un codice | 2.15 | 4.41 | 0.22 | 0.59 | ×0.06 | 0.1% / 0.1% / 0.1% | 69% |
| elenchi | Notitia Dignitatum (cariche), 9787 parole | 3.21 | 7.51 | 0.22 | 0.54 | ×0.00 | 1.6% / 1.3% / 0.7% | 22% |
| elenchi | Notitia Dignitatum (cariche), con un codice | 2.10 | 4.24 | 0.22 | 0.54 | ×0.00 | -0.3% / 0.1% / 0.4% | 70% |
| elenchi | Fasti di Idazio (consoli), 6485 parole | 3.20 | 5.02 | 0.25 | 0.61 | ×0.07 | 0.8% / 0.7% / 0.4% | 18% |
| elenchi | Fasti di Idazio (consoli), con un codice | 1.93 | 4.29 | 0.25 | 0.61 | ×0.07 | -0.3% / 0.1% / -0.2% | 75% |
| nessun messaggio | autocitazione, modifiche guidate dalla forma delle parole | 1.83 | 1.96 | 0.01 | 0.23 | ×1.07 | 8.9% / 8.2% / 5.9% | 60% |
| nessun messaggio | autocitazione, modifiche guidate dalla lunghezza | 3.34 | 3.54 | 0.32 | 0.55 | ×1.29 | 12.2% / 8.9% / 3.8% | 5% |
