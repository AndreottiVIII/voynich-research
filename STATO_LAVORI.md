# Stato dei lavori

Fotografia aggiornata a mano a ogni cambio importante. I dettagli e i numeri sono nel `QUADERNO.md`.

## 3/10/2026 — trasloco su un PC più potente

Il vecchio PC (i5-7200U, 2 core, 8 GB) era saturo.

**Decisione di Davide (3/10, 15:00): il vecchio PC non si usa più.** Tutto il lavoro si fa sul nuovo PC. Il vecchio ha chiuso e committato e269, e270 ed e275. Le corse doppie fatte qui (e269 ed e275 complete; e270 interrotta) sono in `esecuzioni/repliche/`, non committate, e vanno solo confrontate.

**Coordinamento fra i due PC (superato):**
- **Vecchio PC:** finisce gli esperimenti già avviati e ne committa i risultati. Non avvia altro.
- **Nuovo PC:** prende tutto ciò che non è ancora partito.
- **Prima di ogni commit sul nuovo PC:** `git pull --rebase`. Il QUADERNO riceve aggiunte da entrambi
  finché il vecchio non ha finito.

**Ancora in corso sul vecchio PC al momento del trasloco:**

| esperimento | che cosa | note |
|---|---|---|
| e243 | piano 18/18, passo 1: riuso esplicito autoreferenziale | già fallito al seme 7 (8/18, AUC 0,975); finisce i semi |
| e249 | pezzi delle parole come simboli | — |
| e269 | decifrazione sulle sole parole non copiate | — |
| e270 | parole nuove delle piante (e190 con profili di bigrammi) | — |
| e275 | generatore appreso dalla mistura dell'e259b | — |

**Verifica del trasloco: fatta.** e277 ed e278 rieseguiti sul nuovo PC danno risultati identici byte per byte
(QUADERNO, voce "Trasloco sul nuovo PC").

**Decisione di Davide (3/10):** anche e249, e269, e270 ed e275 si rilanciano sul nuovo PC, a costo di ripeterli.
- Chi finisce per primo committa i risultati.
- La seconda corsa **non sovrascrive**: si confronta con quella committata (come in `verifica_replica.py`) e
  l'esito va nel QUADERNO come replica.

## In esecuzione sul nuovo PC (code staccate, avviate il 3/10 alle 12:51)

| coda | esperimenti | note |
|---|---|---|
| gemelle | e257 | |
| sezioni | e276 | base e241 (e243b chiuso, AUC e266 0,947) |
| decifra1 | e222 → e219 | `PROCESSI=4` |
| decifra2 | e223 → e216 → e212b | `PROCESSI=4`; e212b con `RIPARTENZE=2`, come preregistrato |
| vecchio1 | e249 → e270 | ripetuti dal vecchio PC; e249 con `PROCESSI=2` |
| vecchio2 | e269 → e275 | ripetuti dal vecchio PC; e269 con `PROCESSI=2` |

La catena di decifrazione è divisa in due code: gli esperimenti non dipendono dai risultati l'uno dell'altro
(e223 usa solo i corpora dell'e219).

- **Numerali nelle ricette (strada nuova 4): tolta per ora** (3/10, 17:10). Manca un controllo positivo valido: serve un
  ricettario vero con le dosi scritte (tipo *Antidotarium Nicolai*), che nella cache non c'è; i numeri nello zodiaco sono
  già esclusi dall'e262. Si riprende se si trova il testo.

## Indicazione permanente di Davide (3/10, 17:15): migliorare in automatico, senza fermarsi

- Il voynichizzatore si migliora **a giri successivi** (v3, v4, …) con il ciclo avversario: diagnosi di che cosa usano i
  discriminatori → correzione → prova sui semi di ricerca (1, 2) → verifica preregistrata sui semi 7, 8, 9 → nuova
  versione. **Non serve il permesso di Davide a ogni passo**: si va avanti finché l'AUC non scende a 0,6, avvisandolo
  dei risultati importanti.
- Restano le regole del progetto: preregistrazione prima di ogni esperimento con un esito, semi di verifica mai usati per
  scegliere, QUADERNO aggiornato, niente squadre di agenti (costano troppo).
- **Regola dei giri (dal 3/10, dopo l'e292):** sui semi 1–2 un ritocco conta solo se dà almeno +4 di pagella estesa
  (18 materie + 8 aggiunte, somma dei due semi) oppure −0,02 di AUC a pagella estesa non peggiore. Differenze più
  piccole sono rumore fra semi.
- **Dove siamo (3/10, 18:50):** registro delle versioni in `voynichizzatore/versioni.py`, strumento unico
  `voynichizzatore/voynichizzatore.py`. v4 = bordi legati nella riga + scelte di riga per selezione (corpo6);
  v5 = v4 + δ 0,2 (parole di base dal lessico globale). Sui semi 1–2: v3 34 punti, AUC 0,857/0,931; v4 39; v5 39,
  AUC 0,816/0,923. Banco sui semi 7–9 in corso; giro 7 (prova_v7) in corso.

## Obiettivo finale chiarito da Davide (3/10, 15:50)

- Il **voynichizzatore**: si dà in mano un testo normale e restituisce un manoscritto indistinguibile dal Voynich
  (pagella 18/18 e discriminatori ad AUC ≤ 0,6), da cui con la chiave il testo torna esatto. Due pezzi: il
  generatore (il corpo, il lavoro in corso) e la codifica (`rassegna/voynichizzatore_progetto.md`, §7 e §11).
- **Quando funziona**, Davide vuole pubblicarlo: su GitHub o come sito (si incolla il testo, esce il manoscritto).
  - Va fatto in un **repo pubblico separato**, con solo il programma e le statistiche necessarie: questo repo resta
    privato e i dati di `dati/cache` non si ridistribuiscono. Prima si controllano le licenze della trascrizione.

## Diagnosi del generatore (3/10, 15:30): perché il discriminatore lo riconosce ancora

Sintesi della lettura di tutti i risultati e231–e266 (agenti, solo lettura; dettagli nell'uscita del workflow).

- **Il "muro" a 0,86 è il gruppo G3 dell'e231**, sei misure di parola: tipi su parole nella pagina (e241 0,68,
  Voynich 0,76), occorrenze uniche nella pagina (0,54 contro 0,64), deviazione della lunghezza (1,66 contro 1,58),
  lunghezza media, hapax, quota fra le 100 più frequenti. G3 da solo non è mai sceso sotto 0,868 in circa 35
  configurazioni; da solo vale 0,896 sull'e241, più dell'AUC complessiva.
- **Cause nel codice di `e233.genera`:** basi pescate dalla pagina vera **con reimmissione** e da un **tema di 3
  parole** che copre il 30% dei posti (costanti mai regolate); `dopo` spezza le parole (+9% di parole, più
  corte); la prima parola di riga viene da un elenco globale e non si varia; χ copia la parola precedente
  (coppie identiche 2,3% contro 1,0%); `e145.riscrivi` sceglie ch/sh senza guardare il segno prima.
- **Per arrivare a 0,6 devono scendere anche:** G8 prime righe (0,87), G6 coppie (0,80), G4 bordi di riga (0,69),
  G7 (0,68), G9 (0,66), G2 coppie di segni (0,65), G1 (0,63).
- **Tabella di marcia proposta** (stime, non misure):
  - A, riuso di pagina senza tema concentrato e senza reimmissione → **e251b** (in corso);
  - H, serbatoio per posizione (prime righe, inizio e fine riga) → **e268** (in corso) e seguenti;
  - C, spazi decisi nella scelta invece che dopo; E1, ch/sh con il segno precedente; D, lunghezza stazionaria
    nelle varianti; F, finestra di riga al posto di χ;
  - B, controllo del "prestito" (quanto l'AUC scende solo perché si copia dalla pagina vera) → e284, da fare.
- Riferimento vero dell'e241 sui semi di verifica: 15/18, AUC 0,873 (e231) e 0,961 (e266).

## Decisione di Davide del 3/10, 15:25 (sostituisce quella delle 15:20): priorità al generatore

- **Generatore al primo posto:** catena e251 → e252 → e267/e268 → e253 → e254, sempre almeno un esperimento
  in corso. Dopo ogni passo due numeri sui semi 7–9: pagella e AUC e231/e266 (riferimento e241: 15/18,
  0,873 / 0,961).
- **Decifrazione:** niente più prove lingua per lingua con il risolutore (troppo calcolo, rendimento
  basso). Solo strade nuove, pratiche e leggere (test statistici, abbinamenti, generatori ibridi).
  - e281 (prime righe, risolutore in sei lingue): **sospeso** dopo due minuti, nessun risultato.
  - e212c (verifica dei tre candidati dell'e212b) si lascia finire: chiude i falsi candidati.

## (superata) Decisione di Davide del 3/10, 15:20: metà generatore, metà decifrazione

- Sempre almeno un esperimento in corso per ciascuna delle due strade.
- **Generatore:** una catena sola, e251 → e252 → e267/e268 → e253 → e254. Dopo ogni passo si riportano due
  numeri sui semi 7–9: proprietà della pagella e AUC dei discriminatori e231/e266. Riferimento e241: 15/18,
  0,873 / 0,961 (e276).
- **Decifrazione:** solo prove strutturalmente diverse dal risolutore di sostituzione (e279 scelte di
  grafia, e280 etichette, e282 codice per categorie; e281 prime righe in corso). Niente altre varianti
  dello stesso attacco, salvo idee nuove.
- Niente squadre di agenti per progettare: costano troppo. Claude scrive direttamente.

## Decisioni di Davide del 3/10 pomeriggio

- **Generatore:** "facciamo di tutto perché scenda sotto il 60%". L'obiettivo è AUC del discriminatore
  ≤ 0,6 (passo 5 del piano). Appena ci si arriva, se ne fa una **prima versione** con Davide
  (voynichizzatore, e225). Le regole del piano restano: preregistrazioni e semi di verifica 7, 8, 9 mai
  usati per regolare.
- **Quattro strade nuove di decifrazione**, tutte da tentare con i controlli:
  1. **e279, il messaggio nelle scelte.** Le scelte di grafia di ogni riga (forme lunghe e corte, e206b)
     come canale nascosto, sul modello del cifrario di Bacone. L'altra metà della strada sono le sole
     parole non copiate (e269, in corso).
  2. **e280, le etichette come vocabolario.** Abbinare le etichette agli oggetti identificati (piante,
     stelle, recipienti), come in un dizionario illustrato; metodo dell'e27.
  3. **e281, le prime righe da sole.** Decifrare solo le prime righe dei paragrafi, che sono un registro
     a parte (e273).
  4. **e282, codice per categorie con riempitivi.** L'ibrido di D'Imperio (`rassegna/lingue_filosofiche.md`,
     e39 mai fatto): parole di un codice per categorie alternate a copie.
- **e194:** Davide non può annotare a mano. Va riprogettato in modo automatico: controllo positivo con le
  etichette *ch*/*sh* della trascrizione, controllo a vista fatto da Claude sulle immagini.
- **Velocità:** Claude ottimizza il risolutore dell'e17 e il generatore nel worktree
  `C:\Users\davide\voynich_veloce` (ramo `velocita`). Le modifiche entrano in `main` solo se i risultati
  restano identici byte per byte e quando le code non hanno esperimenti in attesa.

## Da fare (in ordine)

1. ~~**e257** (righe gemelle).~~ In esecuzione.
2. ~~**Catena di decifrazione:** e222 → e219 → e223 → e216 → e212b.~~ In esecuzione.
3. ~~**e276** (κ e χ per sezione).~~ In esecuzione.
4. **Piano 18/18, passo 2 (e251).**
   - Il passo 1 è chiuso con la lacuna dichiarata (e243 ed e243b non superati).
   - Il codice attuale è costruito sul generatore dell'e243, che ha fallito.
   - Va rifatto sopra l'e241, con un'**integrazione alla preregistrazione**
     committata prima.
   - Poi **e252** (12 interruttori di riga).
5. **Da scrivere:**
   - **e267**, modulo etichette: le etichette sono un sistema a parte che copia le etichette vicine;
   - **e268**, registro delle prime righe: lessico d'apertura per sezione, *opch-*, *qopch-*, *pch-*
     (e273, e278).
6. **Poi:** e253 (taratura congiunta), e254 (ciclo avversario, obiettivo AUC ≤ 0,6), e225
   (voynichizzatore).
   - Da decidere fra la strada costruita a mano e quella appresa (e275).
7. **Piccoli:**
   - e278b: la stessa misura con gruppi di uguale grandezza;
   - semi in parallelo negli esperimenti sui generatori.
8. **Più avanti:** e194, ridisegno ch/sh ad alta risoluzione, insieme a Davide.

## Dove siamo, in breve

- **Generatore migliore:** e241 (pagella 16/18, AUC e231 0,874, AUC e266 0,937).
  - Mancano ancora: verticale, formule, R delle parole rare (Voynich 1,96, generatore ~50), registro delle
    prime righe, varietà di pagina, etichette.
  - Il discriminatore (e243b, e231) vede nel generatore:
    - lunghezze delle parole più disperse;
    - meno parole frequenti e meno parole diverse nella pagina;
    - parole vicine meno simili.
- **Decifrazione:** tutti gli attacchi danno "nessuna lettura". I candidati dell'e217 erano artefatti.
- **Procedimento accertato:**
  - copia "a vista" dalla riga sopra;
  - 12 scelte di grafia per riga;
  - parole spezzate e prefissi staccati;
  - registro d'apertura dei paragrafi, ma senza formule fisse (e278);
  - nessuna isola di testo diverso (e274);
  - ~11 bit per parola non spiegati dalla copia.
