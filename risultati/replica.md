# Verifica della replica

Riferimento: `origine`. "Identico" = stesso file byte per byte.

| risultato | esito | valori | diversi | scarto rel. max | note |
|---|---|---|---|---|---|
| e01_prevedibilita.json | stessi valori (entro 1e-09) | 2351 | 1460 | 4.46e-10 | struttura diversa: 0 valori solo nel vecchio, 21 solo nel nuovo (Chinese-pinyin) |
| e02_impronta.json | stessi valori (entro 1e-09) | 10042 | 3090 | 1.14e-10 |  |
| e03_genere.json | stessi valori (entro 1e-09) | 521 | 180 | 1.57e-11 |  |
| e04_vicinato.json | stessi valori (entro 1e-09) | 1855 | 396 | 1.48e-12 |  |
| e05_righe.json | stessi valori (entro 1e-09) | 286 | 91 | 3.65e-13 |  |
| e06_currier.json | stessi valori (entro 1e-09) | 600 | 349 | 8.38e-13 |  |
