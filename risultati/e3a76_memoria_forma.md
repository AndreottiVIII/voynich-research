# e3a76 — Quale "memoria" spiega meglio le frequenze delle parole del Voynich?

Preregistrazione: `preregistrazioni/e3a76.md`. ρ come nell'e3a55 con quattro modelli di forma.

## Taratura

| testi | modello atteso | quota con il modello atteso come migliore | conteggi |
|---|---|---|---|
| lingue riscritte, catena 1 | M1 | 0.96 | M1 68, M2 3 |
| lingue riscritte, catena 2 | M2 | 1.00 | M2 71 |

Taratura: **passa**.

## Profili

| testo | M0 | MP | M1 | M2 | migliore |
|---|---|---|---|---|---|
| Voynich | 0.077 | 0.231 | 0.581 | 0.686 | M2 |
| gibberish umano | 0.036 | 0.041 | 0.085 | 0.127 | M2 |
| Naibbe (Greshko 2025), a capo | 0.026 | 0.102 | 0.408 | 0.411 | M2 |
| U2 (Whitehatnetizen 2026) | 0.052 | 0.212 | 0.575 | 0.578 | M2 |
| U3 (Whitehatnetizen 2026) | 0.053 | 0.232 | 0.601 | 0.584 | M1 |
| Timm e Schinner, seme 1 | 0.134 | 0.164 | 0.525 | 0.534 | M2 |
| lingue vere (mediana) | 0.034 | 0.044 | 0.114 | 0.134 | |
| lingue riscritte, ordine 1 (mediana) | 0.152 | 0.320 | 0.699 | 0.656 | |
| lingue riscritte, ordine 2 (mediana) | 0.061 | 0.125 | 0.282 | 0.651 | |

Esito: **memoria di due segni**.
