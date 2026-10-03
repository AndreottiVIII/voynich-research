# Progetto del voynichizzatore finale

Scritto il 3/10/2026, la notte prima di costruirlo con Davide. È un documento di progetto, non un risultato:
le cifre del Voynich vengono dalla pagella (e61, e78) e dagli esperimenti citati; quelle del generatore
andranno aggiornate con l'esito dell'e224.

## 1. Che cosa deve fare

Prende un testo qualsiasi e una parola chiave e restituisce un manoscritto in voynichese che:

- per tutte le proprietà che abbiamo identificato non si distingue dal Voynich;
- con la parola chiave si ritrasforma nel testo esatto;
- senza la parola chiave non lascia capire nemmeno **se** contiene un messaggio.

Scelte di Davide (3/10/2026, prima di dormire):

| domanda | scelta |
|---|---|
| che cosa imita | **tutto il manoscritto**: pagine in ordine, con sezioni, mani e lingue A/B |
| che cosa produce | **EVA, immagine delle pagine, etichette e testo circolare** oltre ai paragrafi |
| chiave | **parola chiave** |
| se indistinguibilità e compattezza confliggono | **prevale l'indistinguibilità** |

## 2. Il principio: tutto il lavoro sta nel modello

La versione attuale (`analisi/voynichizzatore.py`, v2) usa la steganografia per codifica aritmetica
(Ziegler, Deng e Rush 2019):

- il messaggio si comprime e si cifra con un flusso derivato dalla chiave, quindi diventa una sequenza di
  bit indistinguibile da bit casuali;
- quei bit fanno da "dado" per ogni scelta del modello generativo.

Ne segue un fatto semplice, che regge tutto il progetto: **se i bit sono uniformi, il testo prodotto è un
campione del modello**, a meno dell'errore di quantizzazione delle probabilità (frequenze intere su
2^16: trascurabile). È la sicurezza "perfetta" di Cachin (1998) rispetto al modello.

Quindi:

1. **indistinguibile dal Voynich** = il *modello* è indistinguibile dal Voynich;
2. il livello di codifica non aggiunge né toglie proprietà: va solo reso robusto (punto 7);
3. il generatore senza messaggio (e192, e224) e il voynichizzatore devono essere **lo stesso programma**.
   Oggi non lo sono: la v2 ha pesi provvisori suoi.

Conseguenza sulla capacità: l'indistinguibilità fissa quanti bit porta ogni parola, cioè l'entropia del
modello. Non si può far portare più bit a una parola senza cambiarne la statistica. È lo stesso limite
dell'e182/e189 visto dall'altra parte, e la scelta "prevale l'indistinguibilità" lo accetta.

## 3. Architettura: un solo modello, due motori

Un modulo nuovo, `analisi/modello_voynich.py`, descrive il manoscritto come una sequenza di **passi
osservabili**. Per ogni passo restituisce una distribuzione esplicita sulle forme visibili. Due motori lo
usano:

- `campiona(seme)`: il generatore, che usa la pagella e gli esperimenti;
- `codifica(bit)` / `decodifica(testo)`: il voynichizzatore.

Regole che rendono possibile la decodifica:

- **R1 – Ogni scelta visibile è un simbolo codificato:** la parola, il tipo di spazio, la forma di
  un'etichetta. La sua distribuzione è sulle **forme di superficie**: se due percorsi interni danno la
  stessa parola (variante nuova che coincide con una attestata, riscrittura per abitudine, copia dalla
  riga sopra), i pesi si sommano. La v2 lo fa già per le abitudini.
- **R2 – Ogni variabile nascosta viene dalla chiave, non dal messaggio:** tema di pagina, abitudini di
  grafia, dizionario delle varianti, deriva. Chi decodifica la rigenera; chi non ha la chiave vede una
  variabile casuale come nel generatore.
- **R3 – Determinismo:**
  - le distribuzioni si calcolano in ordine fisso (liste ordinate, mai iterazione su `set`);
  - si prova con `PYTHONHASHSEED` diversi;
  - la versione del modello entra nell'intestazione.
- **R4 – I meccanismi "procedurali" dell'e224 vanno riscritti come pesi sulla parola successiva:**
  - parole spezzate (σ): la seconda metà riceve un peso in più quando la parola prima è una prima metà
    possibile;
  - formule (ψ): un modello a "cache" che alza la probabilità della parola che continua una sequenza già
    scritta;
  - copia verticale (φ): un peso sulla parola nella stessa posizione della riga sopra.

  Così ogni passo resta una sola distribuzione su parole e la decodifica non è ambigua. Una copia di tre
  parole in un colpo, come la fa oggi l'e224, darebbe testi uguali per percorsi diversi.

## 4. Il piano del manoscritto

L'uscita segue la struttura vera, pagina per pagina, presa dalla trascrizione ZL:

- per ogni pagina:
  - sezione ($I), lingua di Currier ($L), mano ($H) e fascicolo ($Q);
  - i *loci* con il loro tipo: paragrafo, etichetta, testo circolare, radiale;
  - il numero di righe e la lunghezza di ogni riga;
- se le immagini servono, anche la posizione delle righe e delle parole sulla pagina (i riquadri di
  voynichese.com già registrati sulle immagini IIIF, `analisi/piena_risoluzione.py`).

Lunghezza dell'uscita:

- **predefinita:** si scrivono pagine nell'ordine del manoscritto finché il messaggio non finisce, poi si
  completa la pagina con bit casuali derivati dalla chiave;
- **`--intero`:** si scrive sempre l'intero manoscritto (circa 37.000 parole) e il resto si riempie allo
  stesso modo;
- **messaggio più lungo della capacità:** si apre un "secondo volume", con lo stesso piano e il numero di
  volume nella derivazione della chiave.

Ordine di scrittura e di rilegatura. La deriva del vocabolario segue **quando** una pagina è stata
scritta, non dove è rilegata (e199). Il modello genera quindi nell'ordine ricostruito dei bifogli
(`risultati/ricostruzione_bifogli.md`) e presenta le pagine nell'ordine di rilegatura. Chi decodifica
conosce entrambi gli ordini, che sono pubblici.

## 5. Il modello, livello per livello

Per ogni componente: la proprietà che deve dare, da dove viene e lo stato attuale.

### Manoscritto
- **Lingue A e B e sezioni:** ogni pagina estrae dal serbatoio della propria lingua e sezione, come le
  parole d'inizio della v2. Prova: un classificatore deve separare A da B nell'uscita quanto nel Voynich.
- **Deriva nel tempo:** il serbatoio scivola lungo l'ordine di scrittura. Proprietà: pagella "deriva" ed
  e199, le ultime pagine d'erbario vicine alla farmacia.

### Pagina
- **Tema di pagina** (e180): tiene la pagina e porta T3 al livello del Voynich.
- **Abitudini di grafia** con ripartenza a ogni pagina (e145).
- **Parole rare poco "della pagina"** (e211): R 1,96 nel Voynich contro 50 nel generatore e192.
  - **Difetto noto da correggere:** oggi le varianti nuove nascono dalle parole della pagina e restano
    lì, così si raggruppano 25 volte troppo.
  - Correzione: la variante nuova parte da una parola del serbatoio della sezione, non della pagina.
    L'e226 di stanotte misura da dove nascono le parole nuove nel Voynich.

### Riga, cioè l'unità di composizione
- **Chiusura** (e74, e97) e coppie ripetute chiuse nella riga (e196).
- **Inizio:**
  - evitamento del primo segno della riga sopra (e83–e84, e96);
  - segni y/d/s d'inizio riga (e139);
  - le prime righe dei paragrafi con le proprie parole d'inizio.
- **Cinque scelte di grafia per riga**, indipendenti fra loro (e135, e185), con memoria AR(1) (e145).
  qo-/o- e -l/-r valgono un bit pieno (e210).
- **Segni facoltativi concordi nella riga** (e206, da confermare con gli strati nell'e206b).
- **Legame fra parole vicine** (pagella 0,188; e152, e164).
- **Fine riga** (bordo 55,5; e78).
  - **Difetto visto stanotte nella v2:** 15 righe su 28 della pagina di prova finiscono con *daim* (8) o
    *koeam* (7). Nel Voynich la parola finale più comune, *daiin*, chiude 131 righe su 4.130.
  - Il peso moltiplicativo (rapporto)^η sul segno finale concentra troppo.
  - Correzione: stimare direttamente la distribuzione delle parole finali dato il serbatoio, oppure
    calibrare η sulla distribuzione intera e non sul solo rapporto. L'e229 dice che cosa distingue
    davvero la parola finale.

### Parola
- **Serbatoio di forme attestate più varianti nuove ben formate** (ν; e192).
- **Proprietà da tenere:**
  - h2, tipi, uniche e curva piatta;
  - Zipf (pagella −1,04);
  - forma delle parole (V8);
  - lunghezze vicine;
  - radice k/t lessicalizzata (e201).
- **Unioni** (rapporto 1,97): l'e227 verifica se vengono dal legame o da un meccanismo a sé.
- **Copia verticale** (1,028) e **formule** (5,2): vedi R4.
- **Difetti visti nella v2:**
  - troppe ripetizioni: nella pagina di prova *chol* compare 24 volte su 215 parole (11%) contro l'1,1%
    del Voynich, e *shol* 13 volte. È probabilmente l'effetto combinato della massa del tema e del
    peso di giuntura;
  - parole di un segno solo.

  Vanno misurati sull'uscita intera prima di correggerli.

### Etichette, testo circolare e radiale
- Un sottomodello per tipo di *locus*, stimato sulle etichette vere della stessa sezione.
- **Proprietà:**
  - le etichette della farmacia differiscono fra vasi e frammenti solo per la lunghezza (e183, e187);
  - testo circolare e rosette somigliano alle etichette (e193);
  - l'anello di f57v non è ordinato per frequenza (e193).
- Le etichette portano poche parole: contano poco per la capacità, ma molto per l'aspetto.

### Spazi
- Spazi certi e incerti (`.` e `,` dell'EVA) con le frequenze per tipo di giuntura (e12, pagella
  "spazio"). Gli spazi delle "parole spezzate" sono normali a parità di lunghezza (e195b).

### Aggiornamento della notte (e226–e228b)

- **Parole spezzate:**
  - spezzare il 6% delle parole in due parti attestate dà **insieme** il legame (0,189 contro 0,188), la
    sua quota nelle coppie uniche (Q 0,65 contro 0,67) e le unioni grezze (1,87 contro 1,92) (e227b);
  - la regola dei segni alle giunture non va rafforzata;
  - le parole di base vanno allungate, perché la spezzatura le accorcia (4,46 → 4,20);
  - resta fuori l'eccesso di unioni a parità di segni finali (U/N1, U/N2), che i tagli a caso non
    riproducono. L'e227c, ancora in corso, prova i tagli dove le metà sono frequenti: i primi punti
    dicono di no.
- **Copia verticale per posizione fisica** (e228, e228b, z 3,9): la parola copiata è quella
  materialmente sopra, non quella di pari indice. Senza immagini, la posizione si stima dal conteggio
  cumulato dei segni. Nel voynichizzatore, che ha la disposizione delle pagine vere, la si può prendere
  dai riquadri.
- **Lessico:**
  - le parole nuove nascono un po' dalla pagina (L 1,56), meno che nel generatore (2,19) (e226);
  - il grosso divario sulle parole rare (e211) viene dal fatto che nel generatore la variante resta sulla
    sua pagina. Serve un lessico di parole nuove che cresce per sezione e si riusa altrove: lo prova
    l'e230.
- **Prefissi staccati** (e227d): con spezzature a caso (σ 0,09) più i prefissi *ol, or, ar, al, dar,
  dal, qol* scritti staccati (π 0,30), tutte e cinque le misure di giuntura e unione stanno in
  tolleranza, anche su un seme nuovo.
- **Scelte di riga** (e206b, e206c): oltre alle cinque note ci sono una dozzina di segni facoltativi
  decisi per riga (*e* doppia, *y* finale, *ch/sh* iniziale, *d* iniziale, *l* finale, *t* interna…).
  Sono quasi indipendenti fra loro: lo stato di riga è una dozzina di interruttori.
- **Discriminatore** (e231–e236):
  - generatore e192: AUC 0,97;
  - con fine riga, spezzature, prefissi, κ (frequenti esatte, rare variate) e χ (copia della parola
    precedente): 0,86–0,89;
  - nessuna variante provata scende oltre.
- **Bersaglio per il riuso nella pagina** (e237): R ≈ 32% ripetizioni esatte di parole della pagina, V
  ≈ 37% varianti a una modifica, N ≈ 14% forme nuove, con fonti a 2–3 righe sopra. È il modulo da
  costruire per primo domani, perché i generatori finora sbagliano proprio il rapporto R/V/N.
- **Capacità** (e210b): le scelte di grafia portano al massimo circa 47.000 bit; i tre canali circa
  93.000 bit.
- **Partenza consigliata per il modello** (e241, pagella 16/18 e AUC 0,874, i migliori della notte):
  - giunture λ 1, k 8; fine riga η 1;
  - κ 1 (frequenti esatte, rare variate) e χ 0,2 (copia della parola precedente);
  - operatore di variante empirico condizionato ai segni vicini (e241);
  - dopo la generazione, spezzature σ 0,09 e prefissi a -l/-r staccati π 0,30 (e227d);
  - in più ℓr 1 (e242), che corregge lunghezza e forme nuove senza costi.

  Non usare le giunture rinforzate dell'e224 (λ 1,5) insieme alle spezzature: il legame supera la
  banda (e230).
- **Lacune note da dichiarare se non si chiudono:**
  - il riuso della pagina (R 38% contro 32%);
  - il raggruppamento delle parole rare (e211, R 40–57 contro 1,96);
  - la "verticale" della pagella;
  - l'eccesso di unioni a giuntura conservata, chiuso solo in parte dall'e227d.

## 6. L'immagine

Due stadi.

1. **Font:** l'EVA si rende con un font del Voynich, sulla disposizione del piano (posizioni delle righe
   dalle pagine vere). Le licenze dei font disponibili vanno verificate prima di usarne uno.
2. **"Collage", facoltativo e più ambizioso:**
   - **Parole attestate:** ogni parola attestata si disegna con un ritaglio reale di quella parola, preso
     dalle immagini a piena risoluzione. Abbiamo già riquadri e registrazioni.
   - **Parole nuove:** si compongono da ritagli di segni.
   - **Proprietà fisiche:** si possono imitare anche quelle misurate: intinte e scuro graduale (e166,
     e170), spaziatura (e178), passo di riga (e161).
   - **Licenze:**
     - le immagini della Beinecke sono di pubblico dominio secondo la politica di Yale per le opere di
       pubblico dominio, da ricontrollare e scrivere in `dati/FONTI.md`;
     - per i file dei riquadri di voynichese.com la licenza non è dichiarata, mentre lo zip v1 è
       Apache 2.0.

Il decodificatore legge sempre l'EVA. L'immagine è un'uscita, non un ingresso.

## 7. Il livello di codifica (dalla v2, da irrobustire)

- **Chiave:** parola chiave → `hashlib.scrypt` (con sale fisso di versione) → semi separati per:
  - flusso di cifratura;
  - variabili nascoste;
  - completamento.

  scrypt rende costosi i tentativi a forza bruta sulla parola chiave.
- **Intestazione:** versione del modello, compressione sì/no e lunghezza, più un'**etichetta di
  autenticazione** (HMAC-SHA256 troncato a 32 bit). Con una chiave sbagliata si ottiene un "chiave
  errata" sicuro, non un errore casuale.
- **Compressione:**
  - zlib per cominciare;
  - un compressore a modello di lettere (come `ricottura.ModelloLettere`, pubblico e deterministico)
    guadagnerebbe circa un terzo sui testi italiani.
- **Aritmetica:**
  - la v2 usa frazioni esatte; per l'intero manoscritto (decine di migliaia di simboli) diventano lente,
    con costo quadratico;
  - si passa a un *range coder* a 32 bit con rinormalizzazione, standard e deterministico, con le stesse
    frequenze intere.
- **Completamento dopo la fine del messaggio:**
  - nella v2 le scelte successive dipendono dal punto medio fisso dell'intervallo, cioè sono funzione del
    messaggio e non casuali;
  - nella pagina di prova non si vede una degenerazione, ma la garanzia manca;
  - si estendono i bit con bit casuali derivati dalla chiave, che il decodificatore ignora grazie alla
    lunghezza nell'intestazione.

## 8. Criteri di accettazione (proposta per la preregistrazione e225)

Uscite da misurare:

- 5 manoscritti interi;
- 3 con messaggio: un testo italiano lungo, uno inglese e byte casuali;
- 2 senza messaggio, dal generatore con la stessa configurazione.

| gruppo | proprietà | criterio |
|---|---|---|
| pagella | le 18 dell'e61 + bordo (e78) | tutte nelle bande, media sui 5 |
| riga | chiusura R (e74), evitamento (e83), y/d/s (e139), scelte indipendenti e abitudini (e135, e145, e185), coppie chiuse (e196), segni facoltativi (e206b) | stesso esito del Voynich in ogni test |
| pagina | parole rare R (e211), T3 grezzo e T4 ripulito (e160: Voynich −0,5 e −4,0) | R fra 1 e 4; T3 e T4 dello stesso segno del Voynich |
| manoscritto | A contro B, sezioni, deriva, e199 | stessi esiti |
| etichette | e183/e187, e193 | stessi esiti |
| test di messaggio | e181, e185, e186–e186c, e191b, e162b, e209 | **nessuno scatta** (come nel Voynich) |
| discriminatore | classificatore pagina vera contro generata, per sezione, a validazione incrociata | AUC ≤ 0,6, con controllo positivo (lo stesso classificatore separa A da B) |
| non copia | quota di sequenze di 4 parole copiate dal Voynich | non oltre quella fra le due metà del Voynich (altrimenti è un collage, non un'imitazione) |
| sicurezza | uscite con messaggio contro uscite senza | stesse distribuzioni, AUC ≈ 0,5; controllo positivo: la v1 (bit solo in qo-/o- e -l/-r, testo non compresso) si deve vedere |
| decodifica | 100 testi di lunghezza varia; chiave sbagliata | ritorno identico 100/100; rifiuto 100/100 |

Il discriminatore è il criterio più severo e il più nuovo: misura anche le proprietà che non abbiamo
ancora identificato. Se fallisce, le caratteristiche che usa dicono dove guardare.

## 9. Ordine di lavoro per domani

1. Leggere l'esito dell'e224 e degli esperimenti della notte; fissare la configurazione.
2. Scrivere `modello_voynich.py` (regole R1–R4). Verificare che `campiona` riproduca la pagella
   dell'e224 (stessa configurazione, stessi semi, stesse proprietà).
3. Voynichizzatore v3 sopra il modello:
   - range coder, scrypt, HMAC, completamento casuale;
   - prove di andata e ritorno.
4. Sottomodelli per etichette e testo circolare.
5. Preregistrazione e225, poi esecuzione dei criteri del punto 8.
6. Immagine: prima il font, poi, se c'è tempo, il collage.
7. Voce nel QUADERNO, poi i paragrafi per il white paper (solo quando Davide lo dice).

## 10. Rischi e domande aperte

- **Le 18/18 potrebbero non arrivare dall'e224.** Il voynichizzatore erediterebbe la stessa lacuna. Il
  documento finale deve dire con precisione quali proprietà mancano: "indistinguibile per tutto ciò che
  sappiamo misurare tranne X".
- **Il discriminatore potrebbe trovare differenze** che la pagella non vede. È un risultato utile anche
  per la ricerca: proprietà nuove.
- **Una pagella superata a forza di parametri** rischia di essere adattata, non spiegata. Per questo
  servono i test sui meccanismi (e226–e229) e la verifica su semi nuovi.
- **La capacità dipende dall'entropia del modello**, che non conosciamo finché il modello non è fissato.
  Ordine di grandezza dalla v2: qualche bit per parola, quindi l'intero manoscritto porterebbe forse
  100–150 mila bit, cioè qualche migliaio di parole italiane compresse. Va misurata nell'e225.

## 11. Idea di Davide del 3/10/2026: il messaggio va dimensionato sul libro intero

- **L'osservazione.** Molte proprietà del Voynich esistono solo sul libro intero: omogeneità di pagina,
  vocabolario di sezione, deriva, circolazione delle parole rare. Tradurre "una frase" in voynichese non ha senso:
  il voynichizzatore va provato su un libro intero, con un messaggio coerente.
- **Capacità misurata:** canali liberi noti circa 93.000 bit (e210b), cioè 3.800–7.800 parole latine; limite largo
  circa 380.000 bit (e259b).
- **Conseguenze per la preregistrazione dell'e225:**
  - il testo d'ingresso è un testo vero e coerente, lungo quanto la capacità (per esempio un erbario latino di
    circa 5.000 parole), diviso per sezioni come il manoscritto: capitoli delle piante sulle pagine dell'erbario,
    ricette sulle pagine delle ricette, e così via;
  - criteri: (a) il libro prodotto supera pagella e discriminatori come il generatore senza messaggio; (b) con la
    chiave il testo torna esatto; (c) senza la chiave i nostri attacchi (risolutore, e279, e285) non lo trovano;
  - un messaggio troppo corto, diluito nel riempitivo, non dimostra niente; uno troppo lungo rompe le proprietà.
    La lunghezza giusta è essa stessa una misura da riportare.
- **Conseguenza per la decifrazione:** se il Voynich porta un messaggio, è probabilmente piccolo rispetto al testo
  e nascosto nelle scelte, non nelle parole. Le prove leggere a bassa densità (e279, e285) vanno in questa
  direzione.
