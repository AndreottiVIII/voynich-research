# Piano per il 18/18 e oltre: il modello del voynichizzatore

Scritto il 3/10/2026 mattina, su richiesta di Davide ("fammi tu un piano e lo seguiamo"). Ogni passo è
un esperimento preregistrato (a partire da e243) con criteri di superamento fissati prima. Si va al
passo successivo solo quando il precedente ha un esito.

## Dove siamo

Il miglior generatore è l'e241: pagella 16/18 (un seme), AUC del discriminatore 0,874.

- **Mancano:** ripetizione e verticale.
- **Il discriminatore usa ancora:**
  - il riuso della pagina (R 38% contro 32%);
  - la varietà della pagina;
  - la lunghezza (4,07 contro 4,29);
  - la concentrazione sulle frequenti.
- **Fuori pagella:** le parole rare sono troppo "della pagina" (R 40–57 contro 1,96).

## Metro unico per tutti i passi

Su 3 semi di verifica che non si usano mai per regolare i parametri (7, 8, 9):

1. **pagella dell'e224:** 18 proprietà più la riga;
2. **discriminatore dell'e231:** AUC, sempre con lo stesso codice;
3. **profilo di riuso dell'e237:** R, V, F, A, N;
4. **parole rare per pagina dell'e211:** R.

## Passi

### Passo 1 (e243): il modulo di riuso esplicito

- **Ogni parola** si genera come:
  - ripetizione di una parola della pagina;
  - variante di una parola della pagina, con l'operatore condizionato dell'e241;
  - parola frequente esatta;
  - parola attestata altrove;
  - forma nuova.
- **La fonte** si sceglie con la distribuzione di distanza in righe osservata nel Voynich e, dentro la
  riga sopra, per **posizione fisica** (e228): è il meccanismo comune di ripetizione e verticale.
- **Le quote di classe** si correggono per la distorsione introdotta dalla scelta per giuntura (e238 l'ha
  mostrata). Si regolano in modo che l'**uscita** abbia il profilo del Voynich, non le candidate.
- Base: e241, più spezzature, prefissi staccati e ℓr.
- **Superato se:** pagella ≥ 17/18 sui semi di verifica e AUC ≤ 0,85.

### Passo 2 (e251): lessico che circola fra le pagine

- Le forme nuove entrano in un lessico di sezione; le classi A e N pescano anche da lì.
- **Superato se:** R delle parole rare ≤ 5 senza perdere proprietà della pagella.

### Passo 3 (e252): stato di riga con dodici interruttori

- Le 12 classi dell'e206b diventano interruttori di riga con memoria e ripartenza a pagina, come le
  cinque scelte. Si applicano a tutte le parole della riga.
- **Superato se:** l'e206b sull'uscita ritrova almeno 10 delle 12 classi con z > 3 e la pagella non
  scende.

### Passo 3b (e267, e268): etichette e prime righe (aggiunti il 3/10)

- **e267, modulo etichette** (da e245, e258, e263): le etichette si generano a parte, con un lessico
  proprio (circa il 43% delle loro parole non compare nei paragrafi). Ogni etichetta copia o varia
  un'altra etichetta della stessa pagina o di quelle vicine. Si verifica con le misure dell'e258 e
  dell'e263 sulle etichette generate.
- **e268, prime righe di paragrafo** (da e255): l'intera prima riga ha un lessico proprio, ricco di
  gallows, non solo la prima parola. Si verifica con il gruppo G8 del discriminatore dell'e266.
- L'ortografia di pagina (idea 5) **non serve**: l'e261 mostra che i generatori l'hanno già.

### Passo 4 (e253): regolazione congiunta per momenti

- Tutti i parametri (circa 12) si regolano insieme per far coincidere un vettore di circa 30 statistiche:
  - pagella;
  - misure di riga;
  - profilo R/V/N;
  - le caratteristiche principali del discriminatore.
- Metodo: ricerca casuale più affinamento locale, sul seme di ricerca; mai sui semi di verifica.
- **Superato se:** 18/18 sui semi di verifica.

### Passo 5 (e254 e seguenti): ciclo avversario

- Si riaddestra il discriminatore (anche con caratteristiche nuove: coppie di parole, posizioni nella
  riga, etichette).
- Si guarda che cosa usa e si aggiunge il meccanismo mancante, con un esperimento per ogni aggiunta.
- **Obiettivo:** AUC ≤ 0,6. Ogni caratteristica che resiste è una proprietà nuova del Voynich, da
  scrivere nel QUADERNO.

### Passo 6 (e225): il voynichizzatore

- Lo stesso modello come distribuzioni esplicite, con codifica aritmetica (vedi
  `voynichizzatore_progetto.md`).
- Verifica con i criteri del punto 8 di quel documento.

## Regole

- Ogni passo ha la sua preregistrazione, con la soglia di superamento.
- Se un passo non è superato, se ne capisce il motivo con il discriminatore e lo si rifà una volta. Se
  fallisce ancora, si passa avanti e si dichiara la lacuna.
- I semi di verifica (7, 8, 9) non si guardano mai durante le regolazioni.
