# e259 — Quanto può dire il Voynich: bit per parola con un modello che copia

Base: bigramma di parole con interpolazione di Witten-Bell e modello di lettere per le parole nuove; mistura: base + cache esatta delle ultime 3 righe + cache di varianti a distanza 1 + solo lettere. Pesi per EM su una parte dell'addestramento; addestramento sulle unità pari, misura sulle dispari. Preregistrazione: `preregistrazioni/e259.md`.

| testo | parole | bit/parola, base | bit/parola, mistura | riduzione | pesi (base, cache, varianti, lettere) | bit totali stimati |
|---|---|---|---|---|---|---|
| Voynich | 34863 | 11.26 | 11.22 | 0.05 | 0.09, 0.06, 0.01, 0.85 | 390994 |
| Plinio XX–XXVII (latino tecnico) | 34863 | 15.73 | 15.65 | 0.08 | 0.79, 0.03, 0.00, 0.19 | 545511 |
| Macer floridus (versi) | 13484 | 14.07 | 14.03 | 0.04 | 0.78, 0.01, 0.00, 0.21 | 189183 |
| Bibbia latina | 34863 | 11.55 | 11.33 | 0.22 | 0.77, 0.07, 0.00, 0.15 | 395048 |
| Bibbia italiana | 34863 | 10.28 | 10.13 | 0.15 | 0.80, 0.05, 0.00, 0.16 | 353105 |

Lettura: **informazione per parola paragonabile a una lingua**. Operativizzazione di "molto piu'" (fissata scrivendo il codice, prima dei risultati): riduzione almeno doppia della massima fra i testi veri.
