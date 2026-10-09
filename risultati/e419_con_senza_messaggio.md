# e419 — Con messaggio contro senza messaggio, sulla v21

Preregistrazione: `preregistrazioni/e419.md`. Versione v21, chiavi e409-1 … e409-24, testo Isidoro XVII; il libro "senza" ha gli stessi parametri e la stessa chiave, con soli bit di riempimento.

## 1. Contro il Voynich (dai file dell'e409: caso a `v21f1`, caso b `v21`)

| | con messaggio (a) | senza (b) | differenza a − b |
|---|---|---|---|
| giudice e231 | 0,554 | 0,563 | -0,0087 ± 0,0076 |
| giudice e266 | 0,601 | 0,608 | -0,0066 ± 0,0095 |
| pagella | 15,958 | 16,000 | -0,0417 ± 0,0417 |
| cancello della riga | 24 su 24 | 24 su 24 | |

## 2. Diretto: le pagine dei libri con messaggio contro quelle dei libri senza

- Caratteristiche dell'e266, regressione logistica dell'e231, pieghe per chiave; 9420 pagine.
- **AUC 0,506** (0,5 = tira a indovinare).
- Per gruppo: G1 0,506; G2 0,509; G3 0,505; G4 0,501; G5 0,500; G6 0,493; G7 0,502; G8 0,499; G9 0,498.
- Capacità del libro uguale nei due casi: 0 su 24 chiavi.

## 3. Controllo negativo: chiavi dispari contro pari, soli libri senza messaggio

- AUC 0,511; per gruppo: G1 0,446; G2 0,494; G3 0,417; G4 0,486; G5 0,377; G6 0,382; G7 0,434; G8 0,396; G9 0,384.
