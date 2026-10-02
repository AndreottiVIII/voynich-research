# e191 — Un messaggio a codice variabile nelle scelte di grafia? Test di compressione

Lunghezza di codice (bit per occorrenza) con un modello di Markov adattivo (miglior ordine 0–12), contro 50 rimescolamenti dentro riga e scelta. Preregistrazione: `preregistrazioni/e191.md`.

| testo | bit/occ | nullo | guadagno | z |
|---|---|---|---|---|
| Voynich | 0.9425 | 0.9448 | 0.0023 | 13.5 |
| controllo: Huffman puro (π 1) | 0.9774 | 0.9974 | 0.0200 | 5145007048323.4 |
| controllo: Huffman mescolato (π 0,7) | 0.9965 | 0.9965 | 0.0000 | 0.4 |

Controllo valido: **sì**. Esito: **ridondanza da messaggio**.
