# Diario del paper "Voynich e IA"

Secondo diario, solo per il nuovo paper. Il `QUADERNO.md` resta il quaderno di laboratorio con tutti i numeri; qui
vanno le decisioni, il piano, lo stato degli esperimenti spiegato in modo semplice e le idee per il testo. Il registro
in fondo si allunga solo in coda; il piano e lo stato si aggiornano.

## Decisioni

- **18/11/2026 — Nuovo paper su Voynich e IA** (Davide). Il tema preciso resta aperto: IA come strumento di misura,
  "traduzioni" fatte dall'IA, ricerca condotta da un'IA, o tutti e tre. Intanto si fanno tutti gli esperimenti
  proposti, ognuno preregistrato e con i suoi controlli, spiegati in modo semplice.
- **18/11/2026 — Diario a parte** (Davide): questo file.
- **18/11/2026 — Idea di Davide: un'IA locale che ricrea il Voynich**, come alternativa al voynichizzatore v21
  ("ovviamente non la avevano loro ma esce figo come output"). Diventa l'esperimento IA7, con e senza messaggio
  nascosto.
- **18/11/2026 — Numerazione da 1** (Davide: "è un nuovo lavoro alla fine"): gli esperimenti del paper sono IA1,
  IA2, … (codici `ia01`, `ia02`, … nei file); i numeri e3c96–e3d03 assegnati prima non si usano.
- **18/11/2026 — Preparare, non lanciare** (Davide): preregistrazioni e codice pronti e provati sui controlli, poi
  si decide insieme quando e dove farli partire. Se serve, il lavoro passa a una chat nuova nella cartella
  ClaudeTower.
- Il paper si scrive solo quando lo dice Davide.

## Punto di partenza

- **e3c95 (17/11):** una rete neurale minuscola (67.000 parametri, indovina il segno successivo) addestrata da zero su
  67 testi. Il Voynich ha tanta regola quanta le lingue più regolari, ma la impara in meno di 4 letture (le lingue con
  la stessa regola in 12–15) e senza quasi niente da memorizzare. Si comporta come i generatori che lo imitano (v21,
  Timm e Schinner, Naibbe), non come le 20 lingue né come i cifrati. Non dice se c'è un significato.
- **Paper v2:** i due giudici (classificatori) separano le pagine del v21 dalle vere appena sopra il caso (AUC 0,55 e
  0,60) e non distinguono i libri con messaggio da quelli senza (0,506). Il paper scrive che un giudice più forte
  potrebbe fare meglio.

## Esperimenti

| codice | nome semplice | domanda | stato |
|---|---|---|---|
| IA1 (ia01) | Giudice neurale | Una rete neurale separa le pagine del v21 dalle vere meglio dei giudici del paper? Trova il messaggio? | pronto, rivisto e corretto |
| IA2 (ia02) | Parole mai viste | Quanto costa alla rete una parola mai vista rispetto a una già vista? Nelle lingue molto; in un testo fatto di regole poco | pronto, rivisto e corretto |
| IA3 (ia03) | Quanto contesto serve | Quanti segni indietro deve guardare la rete prima di smettere di migliorare? Guadagna dalla riga sopra? | pronto, rivisto e corretto |
| IA4 (ia04) | Il cervello di una lingua | Una rete addestrata su una lingua, a cui si lascia imparare solo l'alfabeto nuovo, riconosce un cifrato lettera per lettera di quella lingua? E sul Voynich, qualche lingua aiuta? | pronto, rivisto e corretto |
| IA5 (ia05) | Reti più grandi | Le letture di e3c95 reggono con reti più grandi e con un piccolo transformer? | pronto, rivisto e corretto |
| IA6 (ia06) | Le traduzioni dei grandi modelli | Haiku, Sonnet e Opus "traducono" il Voynich e pagine di controllo: le traduzioni dipendono dal testo? | pronto, rivisto e corretto (serve l'accesso del programma `claude` e una prova vera di 48 chiamate per le soglie) |
| IA7 (ia07) | Il Voynich ricreato da un'IA locale | Una rete addestrata sul Voynich scrive un libro intero: quanto è vicino al vero rispetto al v21? E può nascondere un messaggio? | pronto, rivisto e corretto |

## Registro

### 18/11/2026

- Davide decide il nuovo paper e il diario; chiede tutti gli esperimenti e propone l'IA locale che ricrea il Voynich.
- Numeri assegnati: e3c96–e3c99, e3d01–e3d03.
- Il programma `claude` da riga di comando (serve all'e3d02 per interrogare i modelli senza le istruzioni di questo
  progetto) c'è, ma non ha l'accesso fatto: serve un passo di Davide.
- Numerazione cambiata in IA1–IA7 (`ia01`–`ia07`); `esegui.py` e la finestra di stato accettano i codici `ia`.
- Davide: preparare tutto e avvisare, senza lanciare.
- Tutti e sette preparati (preregistrazione e codice, prove solo su controlli e testi non Voynich), non committati né
  lanciati. Cambi rispetto al piano, decisi dagli agenti o dal coordinatore e dichiarati nelle preregistrazioni:
  - IA2: misura principale R_rel = R / R_tri (rapporto con un modello a trigrammi che non può imparare parole
    intere), perché anche il controllo "solo regole" ha R 1,3; 20.000 parole inventate invece di 2.000.
  - IA3: la sola GRU non usa il contesto oltre 12–24 segni e non copia nemmeno una riga ripetuta, quindi la misura
    non distingueva niente. Aggiunta la cache neurale (Grave e altri 2017, forma a normalizzazione globale): ora copia
    la riga ripetuta (GR 1,38) e le ripetizioni a 170 segni (GL 1,30). Letture sulla variante con cache; 10 semi.
  - IA4: avvio per frequenza (ogni segno nuovo parte dal segno della lingua con lo stesso rango); 18 cifrati invece
    di 20 (maya e cinese in pinyin senza testo nuovo sufficiente).
  - IA5: semi 1–5 per le reti piccole, 1–3 per le grandi; soglia del controllo positivo 0,03 invece di 0,02.
  - IA6: 3 ripetizioni invece di 4 (tetto di 1.000 chiamate); avvio dei modelli in modalità senza istruzioni
    personali (`--safe-mode`).
  - IA7: GRU 2×256 condizionata da sezione, mano, lingua, tipo e lunghezza di riga; capacità del messaggio circa
    591.000 bit per libro sul latino (v21 circa 83.000).
- Revisione indipendente in corso (tre revisori, solo lettura).
- Revisione indipendente (tre revisori, solo lettura) e correzioni degli autori, tutte dichiarate nelle
  preregistrazioni:
  - IA1: l'AUC del giudice "lettore" metteva insieme i punteggi di 5 reti diverse e si gonfiava (0,649 complessiva
    contro 0,560 per piega sul libro di prova): ora media per piega; controllo negativo del messaggio riparato; semi
    distinti per insieme; si ferma se manca un libro.
  - IA2: secondo controllo "solo regole" più duro (prefisso + corpo + suffisso): R_rel 0,99, riuscito.
  - IA3: α e θ della cache scelti per ogni k sulla validazione; GR sulle sole posizioni tagliate.
  - IA4: controllo positivo solo sui 14 cifrati dello stesso testo; cancello contro i generatori ("il metodo non
    distingue" se anche un generatore sembra una lingua); eco delle frequenze misurata a parte; famiglie di lingue
    fissate; sonda con omofoni e digrafi: il metodo non li tollera (TG 0,30), quindi vale solo per la sostituzione
    semplice segno per segno.
  - IA5: confronti sui semi comuni; soglia C+ 0,03 motivata e senza modifiche da ambiente.
  - IA6: riservatezza rafforzata (sempre senza personalizzazioni, cartella pubblica vuota, verifica di nove voci,
    nessun percorso personale nei risultati); soglie da fissare con una prova vera di 48 chiamate prima del commit;
    riferimento del messaggio dallo stesso libro di Isidoro; attesa automatica se finisce il limite d'uso.
  - IA7: libro vetrina e immagini solo in `dati/cache/ia07_vetrina/` con controllo di copia nei risultati; due serie
    di modelli; difetto trovato nella prova (il classificatore riconosceva la serie) corretto togliendo la media per
    serie; letture "non valide" se cade il controllo da cui dipendono.
- Nota per il quaderno: la griglia di E90 in e3c95 è di 1,024 letture, non 0,9 come scritto nella voce del 17/11
  (non cambia le conclusioni); da dichiarare nella prossima voce.
