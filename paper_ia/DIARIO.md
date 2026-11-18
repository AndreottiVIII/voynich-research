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
| IA1 (ia01) | Giudice neurale | Una rete neurale separa le pagine del v21 dalle vere meglio dei giudici del paper? Trova il messaggio? | in preparazione |
| IA2 (ia02) | Parole mai viste | Quanto costa alla rete una parola mai vista rispetto a una già vista? Nelle lingue molto; in un testo fatto di regole poco | in preparazione |
| IA3 (ia03) | Quanto contesto serve | Quanti segni indietro deve guardare la rete prima di smettere di migliorare? Guadagna dalla riga sopra? | in preparazione |
| IA4 (ia04) | Il cervello di una lingua | Una rete addestrata su una lingua, a cui si lascia imparare solo l'alfabeto nuovo, riconosce un cifrato lettera per lettera di quella lingua? E sul Voynich, qualche lingua aiuta? | in preparazione |
| IA5 (ia05) | Reti più grandi | Le letture di e3c95 reggono con reti più grandi e con un piccolo transformer? | in preparazione |
| IA6 (ia06) | Le traduzioni dei grandi modelli | Haiku, Sonnet e Opus "traducono" il Voynich e pagine di controllo: le traduzioni dipendono dal testo? | in preparazione (serve l'accesso del programma `claude`) |
| IA7 (ia07) | Il Voynich ricreato da un'IA locale | Una rete addestrata sul Voynich scrive un libro intero: quanto è vicino al vero rispetto al v21? E può nascondere un messaggio? | in preparazione |

## Registro

### 18/11/2026

- Davide decide il nuovo paper e il diario; chiede tutti gli esperimenti e propone l'IA locale che ricrea il Voynich.
- Numeri assegnati: e3c96–e3c99, e3d01–e3d03.
- Il programma `claude` da riga di comando (serve all'e3d02 per interrogare i modelli senza le istruzioni di questo
  progetto) c'è, ma non ha l'accesso fatto: serve un passo di Davide.
- Numerazione cambiata in IA1–IA7 (`ia01`–`ia07`); `esegui.py` e la finestra di stato accettano i codici `ia`.
- Davide: preparare tutto e avvisare, senza lanciare.
