# Il manoscritto Voynich come sistema di scrittura

## Misure ripetibili a confronto con lingue, scribi medievali, cifrari e generatori

**Davide Caniatti**
con analisi eseguite con l'assistenza di Claude (Anthropic)

*Bozza in italiano, 4 ottobre 2026. Da rivedere; la versione definitiva sarà in inglese.*

---

## In breve

Il manoscritto Voynich (Yale, Beinecke MS 408; pergamena datata al radiocarbonio fra il 1404 e il 1438) è scritto in
un alfabeto che nessuno ha mai letto. In questo lavoro **non proponiamo una decifrazione**. Proponiamo qualcosa di più
modesto e, crediamo, più utile: una serie di misure ripetibili, ciascuna decisa in anticipo e provata prima su testi in
cui la risposta è nota, che descrivono **come** è scritto il testo del Voynich e lo confrontano con lingue naturali,
lingue artificiali, testi senza senso scritti a mano da volontari, cifrari storici, generatori di testo pubblicati e,
per la prima volta in modo sistematico, con il lavoro di **79 scribi medievali veri** e del copista di un cifrario
settecentesco.

Il quadro che ne esce è netto: il Voynich segue regole di scrittura fra parole vicine e ai bordi della riga molto più
forti di quelle di qualsiasi scriba, lingua o generatore provato. Queste regole non ci dicono che cosa c'è scritto, ma
restringono molto le spiegazioni possibili e danno a chiunque proponga una lettura una lista di proprietà da
riprodurre.

---

## Le dieci scoperte principali

Le prime sette sono, per quanto sappiamo, **nuove**; le altre tre rafforzano con misure nuove idee già discusse.

1. **Il testo è una catena di segni in cui lo spazio è un confine debole.** Le regole che legano l'ultimo segno di una
   parola al primo della seguente ricalcano quelle fra due segni dentro la parola, più che in tutte le 71 lingue di
   confronto. Lo spazio si indovina dai due segni attorno (accuratezza 0,86, sopra il 97% delle lingue), e tagliando il
   testo in un altro punto
   permesso dalle regole si ottengono quasi sempre parole che esistono altrove nel manoscritto (50%, contro il 6,5%
   delle lingue).
2. **Le parole vicine sono legate da regole di "raccordo".** *qo-* compare dopo parole che finiscono in *-y*, *-o*,
   *-d*; *o-* dopo *-n*, *-r*, *-s*, *-m*. La finale *-l* o *-r* dipende dall'inizio della parola dopo. Lo scriba
   **conosce la parola successiva** mentre finisce quella in corso. Il legame è almeno quattro volte più forte che in
   qualsiasi scriba medievale provato.
3. **La riga è un'unità chiusa.** Il legame fra parole si interrompe all'a capo e anche dove un disegno spezza la riga;
   l'inizio e la fine della riga hanno forme proprie (a fine riga *-m* prende il posto di *-r*; a inizio riga compaiono
   *s-* e *y-*).
4. **Lo scriba copia dalla riga subito sopra.** Le parole riprendono, più del caso, parole (o pezzi di riga) della riga
   appena scritta, non di quelle più in alto; la copia si adatta alle regole di raccordo con la nuova vicina.
5. **Ogni riga evita di cominciare come quella sopra.** Se la riga sopra comincia con *qo-*, quella sotto comincia con
   *o-*. Fra 79 scribi medievali nessuno lo fa: nei sei nordici non c'è un solo caso in 72 prove, e solo tre dei 73
   manoscritti tedeschi evitano un singolo inizio, quanto ci si aspetta dal caso.
6. **Le scelte fra varianti hanno uno "stato" che dura qualche parola.** Fra le forme *k*/*t*, *sh*/*ch*, -*ey*/-*dy*,
   lo scriba tende a ripetere per due-tre parole la stessa scelta, **qualunque parola stia scrivendo**. Non è copia di
   parole simili, non è la posizione nella riga, è separato per ogni scelta ed è identico in tutte le mani del
   manoscritto: è una regola del sistema di scrittura. Nei sei scribi nordici e nel copista del cifrario Copiale non
   l'abbiamo trovato (la verifica sui 73 scribi tedeschi è in corso, esperimento e3c77).
7. **Lungo la riga le varianti "marcate" calano** (*qo*, *k*, *sh*, -*ey* diventano più rare andando verso destra):
   da tre a quindici volte più che nei sei scribi nordici (verifica sui tedeschi in corso).
8. **Il Voynich ripete subito la parola precedente** (1% delle coppie vicine) o una quasi uguale (3,9%) più di tutte
   le lingue e di tutti gli 85 testi scritti a mano provati (di solito da 10 a 100 volte di più), pur avendo un
   vocabolario di grandezza normale.
9. **Il libro ha una struttura di scrittura**: la pagina ha un'identità forte, il bifoglio è un'unità di lavoro (una
   sola "lingua" di Currier, quasi sempre una sola mano), il paragrafo si apre con un segno grande (*p*) e ha una prima
   e un'ultima riga con un registro proprio; -*ey* cresce scendendo nella pagina.
10. **Nessuna lettura proposta regge ai controlli**: né le nostre (sostituzioni in decine di lingue, risolutori, cifrari
    verbosi, nomenclatori, ricerche guidate dal contenuto), né quelle pubblicate che abbiamo potuto verificare (Bax,
    Vatne, Cheshire, Schechter, Gatta), né i meccanismi di cifratura storici simulati (omofoni, indice di Alberti,
    biletterale di Bacone, liste di Tritemio, autochiave).

---

## 1. Introduzione

### 1.1 Il manoscritto

Il Voynich è un codice di circa 240 pagine, con disegni di piante, diagrammi astronomici e zodiacali, figure femminili
in vasche e tubature, contenitori da farmacia e una lunga sezione finale di solo testo, divisa in brevi paragrafi
segnati da stelline (di solito chiamata "ricette"). La scrittura è ordinata e sicura: non sembra il lavoro di chi
inventa i segni mentre scrive. Negli anni Settanta Prescott Currier notò che le pagine si dividono in due varietà di
scrittura, oggi chiamate **lingua A** e **lingua B**, e che le mani che hanno scritto il manoscritto sono più d'una.

Il testo si studia attraverso **trascrizioni** che rendono ogni segno con una lettera latina convenzionale. La più
usata è l'alfabeto EVA: una parola come *qokeedy* o *daiin* non dice niente sul suono, è solo un'etichetta per una
sequenza di segni. Alcuni segni si scrivono in EVA con più lettere (*ch*, *sh*, i "gallows" *k*, *t*, *p*, *f* e le loro
forme composte); in tutte le nostre misure li contiamo come un segno solo.

### 1.2 Il problema

In più di un secolo sono state proposte decine di letture: latino abbreviato, lingue romanze, ebraico, turco antico,
lingue asiatiche, cifrari di vario tipo. Nessuna ha convinto la comunità degli studiosi, per una ragione semplice: è
facile trovare in un testo lungo qualche parola che "sembra" qualcosa, ed è difficile dimostrare che una lettura fa
meglio del caso. Dall'altra parte, chi sostiene che il testo non abbia significato deve spiegare perché ha tante
regolarità.

### 1.3 Che cosa offre questo lavoro

Non una nuova lettura, ma un insieme di **misure con controlli**:

- ogni misura è stata **decisa per iscritto prima** di guardare il risultato sul Voynich (preregistrazione);
- ogni metodo è stato **provato prima su testi finti** in cui l'effetto cercato c'era o mancava, per vedere se lo
  ritrovava;
- ogni proprietà del Voynich è stata **confrontata** con le stesse misure su lingue, scribi, cifrari e generatori;
- quando una misura intermedia si è rivelata sbagliata, **lo abbiamo scritto** e l'abbiamo corretta (le verifiche
  interne sono elencate nell'Appendice B).

Il risultato è una descrizione del Voynich come **sistema di scrittura**: che cosa fa chi scrive, parola dopo parola e
riga dopo riga. Questa descrizione è utile in due modi: dice quali spiegazioni sono escluse e fornisce una lista di
proprietà che qualsiasi spiegazione futura dovrà riprodurre.

---

## 2. Dati

### 2.1 Il Voynich

Tre trascrizioni indipendenti, nel formato IVTFF di René Zandbergen:

| trascrizione | alfabeto | ruolo |
|---|---|---|
| Zandbergen-Landini (ZL) | EVA | riferimento |
| Takahashi (IT) | EVA di base | replica |
| Glen Claston (GC) | v101 (un altro modo di tagliare i segni) | replica |

Usiamo il testo in paragrafi, circa 35.000 parole leggibili. Le etichette dei disegni, i testi in cerchio e i raggi
entrano solo in alcune prove, segnalate. Le parole con segni illeggibili (0,6%) sono scartate. Ogni risultato
principale è stato replicato su almeno due trascrizioni, la maggior parte su tutte e tre.

### 2.2 Testi di confronto

- **Lingue naturali:** la Bibbia in circa 100 lingue; 71 testi della raccolta di Gaskell e Bowern (2022) in lingue
  diverse, a parole intere; testi tecnici latini (Plinio, Varrone, Isidoro, Vitruvio) e italiani (il *Della Pittura* di
  Alberti), per controllare l'effetto del genere.
- **Lingue artificiali:** Esperanto, Volapük, Neo-Quenya, Interlingua, Lojban, Klingon, LOLCat, Toki Pona.
- **Testo senza senso scritto a mano:** 38 testi prodotti da volontari a cui era stato chiesto di scrivere a mano un
  testo inventato (Gaskell e Bowern 2022).
- **Generatori e cifrari pubblicati che imitano il Voynich:** il cifrario Naibbe (Greshko 2025), che cifra un vero
  testo latino o italiano con un procedimento eseguibile a mano; il generatore ad "autocitazione" di Timm e Schinner
  (2020), che produce testo senza messaggio copiando e ritoccando parole già scritte; due generatori amatoriali (U2,
  U3).
- **Scribi medievali veri, a livello del facsimile** (cioè con le forme delle lettere come sul manoscritto, le
  abbreviazioni e le righe e le pagine originali):
  - 6 manoscritti dell'archivio **Menota** (Medieval Nordic Text Archive): islandesi, norvegesi e uno svedese, dal 1200
    circa al 1550;
  - 73 manoscritti tedeschi del **Referenzkorpus Frühneuhochdeutsch** (ReF), dal 1350 al 1500, cioè dell'area e del
    secolo del Voynich, con righe di 5–8 parole come le sue;
  - lo scriba anglosassone degli *Hatton Gospels* (da un'edizione, senza righe originali).
- **Un cifrario storico vero:** il **Copiale**, manoscritto cifrato tedesco della metà del Settecento (105 pagine), con la
  trascrizione e la decifrazione di Knight, Megyesi e Schaefer (2011). Usa una cifra omofonica: la stessa lettera si
  può scrivere con simboli diversi, a scelta del copista.
- **Testi tecnici medievali scritti a mano:** dal ReF, un *Libro della natura*, un ricettario di chirurgia, un libro di
  astrologia lunare, una *Naturlehre* e un libro di magia e alchimia.

Tutti i dati sono stati presi a versioni fissate, con le licenze indicate nell'Appendice D. I testi protetti non sono
ridistribuiti.

---

## 3. Metodo

### 3.1 Le regole che ci siamo dati

1. **Preregistrazione.** Per ogni esperimento, prima di eseguirlo sul Voynich, abbiamo scritto in un file datato la
   domanda, la misura, i dati e il **criterio** con cui avremmo letto l'esito ("se il valore supera X diremo Y").
2. **Prova del codice su testi finti.** Ogni misura è stata provata prima su testi costruiti apposta, con l'effetto
   cercato presente e assente. Una misura che non distingueva i due casi non è stata usata: in tre casi l'esperimento
   non è stato eseguito ed è stato dichiarato come lacuna (§11).
3. **Controlli positivi e negativi.** Per le prove di decifrazione: un testo noto cifrato allo stesso modo (che il
   metodo deve risolvere) e un testo in un'altra lingua (che dice quanto si ottiene per caso).
4. **Intervalli onesti.** Gli intervalli di incertezza si calcolano ricampionando pagine intere, perché parole vicine
   non sono indipendenti.
5. **Un passo fallito si rifà una volta**, poi si dichiara la lacuna.
6. **Le correzioni si scrivono.** Il quaderno di laboratorio è stato scritto solo aggiungendo, mai cancellando.

### 3.2 Le misure principali, in parole semplici

- **Giuntura:** quanta informazione l'ultimo segno di una parola dà sul primo segno della parola dopo, oltre quella
  che ci si aspetterebbe dalla frequenza dei segni (in bit).
- **Raccordo:** quanto una scelta all'inizio (o alla fine) di una parola dipende dal segno della parola vicina, a parità
  di parola.
- **Accordo delle scelte (lo "stato"):** per una scelta fra due varianti (per esempio *k* o *t*), quanto due parole
  vicine della stessa riga fanno la stessa scelta più del previsto, dove il "previsto" tiene conto delle preferenze di
  ogni parola, della pagina e della posizione nella riga. Lo esprimiamo come una frazione dell'accordo massimo possibile
  (0 = come il caso, valori positivi = più accordo del caso).
- **Ripresa dalla riga sopra:** quante parole hanno una parola uguale o quasi uguale nella riga sopra, oltre il caso.
- **Margine sinistro:** quanto spesso una riga comincia come la riga sopra, rispetto alle righe rimescolate.

### 3.3 Una correzione di metodo decisiva

A metà del lavoro abbiamo scoperto che la misura dell'accordo delle scelte aveva una **distorsione** che cambiava da
testo a testo: in alcuni testi gonfiava l'accordo fino a +0,37, in altri lo abbassava. La causa è che il "previsto"
viene stimato dagli stessi dati. La correzione consiste nel sottrarre il valore che si ottiene rimescolando le scelte
fra le occorrenze della stessa parola (che ha la stessa distorsione ma nessun accordo vero). Tutte le misure di accordo
riportate qui sono corrette in questo modo. La correzione ha cambiato tre indicazioni provvisorie del lavoro: lo
scriba anglosassone non ha la "finestra" che una prima misura gli attribuiva; il Volapük non somiglia al Voynich; il
Voynich non sta "fuori" dalla gamma delle lingue per la forma del suo accordo, ma in cima.

---

## 4. Il testo come catena di segni: parole, spazi e righe

### 4.1 Un'impronta che nessuna lingua ha

Il primo dato, già noto in parte, è che il testo del Voynich è troppo regolare. L'incertezza sul segno successivo
(una misura classica, chiamata h2) è 2,2 bit, contro 2,6–3,3 nelle lingue con un alfabeto di grandezza simile. Messe
insieme nove misure (prevedibilità dei segni, spazi, vocabolario, ripetizioni, somiglianza fra parole della stessa
pagina, legami fra parole vicine), il Voynich sta più lontano dalla lingua più vicina di quanto la lingua più isolata
del campione stia dalla sua vicina (distanza 9,9 contro 4,1). Le lingue che gli "somigliano di più" (potawatomi,
chinanteco, ewe, malgascio) non hanno niente in comune fra loro: il Voynich non ha una famiglia linguistica naturale.

Alcune cose invece sono normali: la quantità di parole diverse (circa 2.900 ogni 10.000 parole, come nei testi tecnici
medievali), la legge di Zipf, la scarsa "sintassi" apparente (che è la stessa dei testi tecnici latini: era la Bibbia,
molto formulaica, a essere un confronto sbagliato).

### 4.2 Lo spazio è un confine debole dentro una catena di segni

Questa è la prima scoperta nuova, ed è la chiave per capire molte delle altre.

- **Lo spazio si indovina dai segni vicini.** Guardando solo i due segni prima e i due dopo un punto, si prevede se lì
  c'è uno spazio con un'accuratezza di 0,86, più che nel 97% delle lingue (mediana 0,64). Gli spazi che i trascrittori
  segnano come incerti cadono proprio dove la regola è incerta, e dove ZL e Takahashi non concordano.
- **Lo spazio non dipende dalla parola.** Nelle lingue, se uno spazio è "facoltativo" (per esempio in una parola
  composta), la scelta dipende fortemente dalla parola intera. Nel Voynich no: contano solo i segni vicini e la lunghezza
  del pezzo in corso (lo scriba spezza più spesso un pezzo lungo ed evita di staccare pezzi di 1–3 segni).
- **Tagli diversi danno parole vere.** Togliendo gli spazi e rimettendoli a caso con la regola dei segni vicini, la
  metà dei pezzi sbagliati sono comunque parole che esistono nel Voynich (50%), contro il 6,5% nelle lingue (massimo
  25%).
- **Il vocabolario riempie le forme possibili.** Fra le sequenze di segni più probabili per le regole del sistema, il
  43% sono parole del Voynich; nelle lingue il 4%. E le parole frequenti sono proprio le sequenze più probabili
  (correlazione 0,58, contro 0,11 nelle lingue).
- **Le regole fra parole ricalcano quelle dentro le parole.** Le preferenze fra l'ultimo segno di una parola e il primo
  della seguente somigliano a quelle fra due segni consecutivi dentro una parola (correlazione 0,47), più che in tutte
  le 71 lingue (al massimo 0,39, di solito sotto 0,2). Anche dentro parole scritte attaccate vale la stessa regola: le
  *q* interne seguono un segno -*y*, -*o* o -*d* in 28 casi su 29.

In sintesi: il testo si comporta come una **catena di segni** con regole di sequenza proprie, in cui gli spazi sono
inseriti dove la catena lo permette. Le "parole" del Voynich non sono unità scelte una per una come in una lingua; sono
pezzi di una catena. Questo non dice ancora che cosa la catena rappresenti.

### 4.3 La giuntura e il raccordo fra parole vicine

- **Una giuntura forte.** L'ultimo segno di una parola dice molto sul primo segno della seguente: 0,18–0,19 bit oltre
  il caso. Su 71 lingue solo 6 superano il Voynich (fra cui il sanscrito, che scrive le assimilazioni fra parole, e
  l'arabo del Corano). Nel testo senza senso scritto a mano dai volontari vale 0,014; nei generatori pubblicati fra 0 e
  0,08.
- **Due regole precise ("raccordo").**
  - *qo-* oppure *o-* davanti ai segni alti (gallows): *qo-* dopo una parola che finisce in -*y*, -*o*, -*d* (59–64%
    delle volte), *o-* dopo -*n*, -*r*, -*s*, -*m* (*qo-* solo nel 23–27%).
  - -*l* oppure -*r* a fine parola: -*r* davanti a una parola che comincia con *a-* (85%), -*l* davanti a *k-*, *t-*,
    *d-*, *l-*, *s-*, *q-* (63–86%).
  - Hanno la forma di regole come l'inglese *a*/*an* o la *liaison* francese. Non dicono quali suoni ci siano dietro.
- **Lo scriba guarda avanti di una parola.** Quando due parole copiate dalla riga sopra violerebbero insieme una regola,
  lo scriba cambia il pezzo più facile da cambiare: per -*l*/-*r* la fine della prima parola (59% contro 21%), per
  *qo-*/*o-* l'inizio della seconda (60% contro 18%). Quindi mentre finisce una parola conosce già la successiva.
- **E non oltre.** A parità della parola in mezzo, l'ultimo segno di una parola non dice niente sul primo della
  parola dopo la successiva; nelle lingue questo legame c'è in 34 testi su 42. Il Voynich guarda una parola avanti e una
  indietro, non di più.
- **Regola del sistema.** Le regole valgono uguali nelle tre mani principali, in tutte le sezioni, in tutti i bifogli,
  con tutte e tre le trascrizioni.

### 4.4 La riga è un'unità chiusa

- **La giuntura si ferma all'a capo.** Fra l'ultima parola di una riga e la prima della riga sotto il legame è zero,
  contro 0,19 dentro la riga. Nella prosa delle lingue, che va a capo dove capita, il legame passa per metà o per
  intero; è vicino a zero solo nei testi in cui ogni riga è un versetto.
- **E si ferma al salto di un disegno.** Dove una riga è interrotta da una pianta, il legame fra le parole ai due lati
  scende da 0,167 a 0,026. In una lingua la grammatica passerebbe oltre il disegno. Le parole dopo il disegno cominciano
  come quelle di inizio riga.
- **Forme di bordo.** A parità del resto della parola, a fine riga -*m* sale di 15 punti percentuali e -*r* scende di
  12 (*dar* in mezzo alla riga, *dam* a fine riga); a inizio riga *s-* e *y-* salgono di circa 9–10 punti al posto di
  *ch-* e *k-*. Nell'ultima riga del paragrafo, che non arriva al margine, -*m* è più rara: è una forma legata al
  margine.
- **Senza parola prima si scrive *o-*.** Nelle etichette dei disegni, che sono parole isolate, *qo-* davanti ai gallows
  quasi non c'è (0–5% contro 30–68% nelle righe): *qo-* nasce solo dopo una parola scritta di seguito. È una previsione
  fatta prima e confermata su dati non guardati.

Nessun generatore pubblicato ha insieme una catena con spazi deboli e una riga chiusa: il generatore U3 ha la catena ma
la fa passare all'a capo; gli altri non hanno né l'una né l'altra.

---

## 5. La pagina e il libro: copiare dalla riga sopra, evitare di ripetersi

### 5.1 Lo scriba copia dalla riga subito sopra

- **Ripresa.** Una parola ha una parola uguale o quasi uguale nelle due righe subito sopra molto più del caso (z 17,4 a
  parità di lessico del paragrafo), più del doppio che nel generatore di Timm e Schinner, costruito proprio su questa
  idea.
- **Solo la riga subito sopra.** La ripresa viene dalla riga immediatamente sopra (forte) e un poco da quella prima;
  dalla terza in su niente. Nelle lingue la "ripresa" di parole è spalmata su 3–4 righe (è la continuità del discorso,
  con il massimo a due righe); nel Voynich è tutta a distanza 1. Il generatore di Timm e Schinner pesca fino a 6 righe
  sopra: è la prima differenza netta con la loro teoria.
- **Pezzi di riga.** Due parole vicine riprese vengono più del caso da due parole vicine della riga sopra, di solito
  nello stesso ordine ma anche invertite.
- **Non per colonne.** La parola copiata non sta nella stessa colonna della fonte (l'allineamento che sembrava esserci
  veniva dai bordi della riga).
- **Si ferma al paragrafo e alla pagina.** La prima riga di un paragrafo non riprende l'ultima del paragrafo prima, né
  la prima riga di una pagina l'ultima della pagina prima. Dentro il paragrafo, dalla terza riga in poi, la copia è
  costante.
- **La copia si adatta al raccordo.** Una parola ripresa dalla riga sopra prende la forma (*qo-* o *o-*, -*l* o -*r*)
  che va d'accordo con la sua **nuova** vicina più che quella della fonte (effetto +0,49 contro +0,16). Le regole di
  raccordo si applicano nel momento in cui si scrive.
- **Il gibberish non lo fa.** Il testo senza senso scritto a mano dai volontari non riprende dalle righe sopra
  (−0,001); le lingue sì, ma con la ripresa spalmata su più righe (secondo punto).

### 5.2 Ogni riga evita di cominciare come quella sopra

- Rimescolando l'ordine delle righe dentro i paragrafi, si vede che lo scriba **evita** di cominciare una riga con lo
  stesso inizio della riga precedente: *qo-* (z −9,7), *o-* (−7,0), *d-* (−3,8), *ch-* (−3,6), *y-* (−3,5). Se la
  riga sopra comincia con *qo-*, la riga sotto prende *o-* (la probabilità di *qo-* cala di 52 punti).
- Vale per l'inizio della riga, non per un bordo visivo qualsiasi: dove le righe riprendono a destra di un disegno, una
  sotto l'altra, l'effetto non c'è. Non conta la riga a due di distanza, né la fine della riga sopra, né il margine
  destro.
- Rapporto fra inizi uguali osservati e attesi: Voynich 0,51; lingue mediana 0,95 (solo 3 su 57 sotto il Voynich);
  gibberish a mano 1,32; generatori 0,93–2,05.

### 5.3 Paragrafi, pagine, bifogli

- **Il paragrafo si apre con un segno grande.** L'83% delle prime parole dei paragrafi comincia con un gallows (*k*,
  *t*, *p*, *f* o composti), altrove il 9%; fra questi domina *p* (54%), che nel resto del testo è raro. Il gallows di
  apertura è legato alla parola tre volte meno del solito: è in buona parte un segno della posizione.
- **Prima e ultima riga hanno un registro proprio.** La prima riga del paragrafo ha parole più lunghe, più *p*, *f*,
  *sh*, più finali in -*y*; l'ultima ha meno *qo-* e meno gallows, più *ch-*, *s-*, *y-*.
- **-*ey* cresce scendendo nella pagina** (+0,12–0,14 dalla cima al fondo, a parità di posizione nella riga), soprattutto
  nelle pagine delle ricette. Le righe si accorciano scendendo.
- **Ogni pagina ha un'identità forte**, soprattutto lungo un asse che va dalle parole in -*edy*/-*eey* a quelle in
  -*aiin*/-*ain* (la pagina si allontana dal profilo della sua sezione 2,8 volte più del caso).
- **Il bifoglio è un'unità di lavoro.** L'identità della pagina è condivisa dalle due facce dello stesso foglio e dal
  foglio coniugato dello stesso bifoglio (che nel libro rilegato sta lontano), non dalla pagina accanto. Le due metà di
  un bifoglio condividono le parole rare e si riprendono fra loro. Tutti i 48 bifogli con dati sufficienti sono
  interamente in lingua A o interamente in lingua B, e il 94% è di una sola mano.
- **Le lingue A e B differiscono nel lessico**, non nei segni: la migliore sostituzione dei segni avvicina A a B solo
  dell'1% del divario, mentre la stessa ricerca ritrova al 100% una chiave casuale. B non è A cifrata con un'altra
  chiave.
- **L'ordine delle pagine conserva in buona parte l'ordine di scrittura:** pagine consecutive condividono più parole
  di pagine qualsiasi della stessa sezione.

---

## 6. Le scelte fra varianti: ripetere, durare, derivare

Nel testo del Voynich molte parole esistono in coppie di varianti che differiscono per un solo segno: *qo*/*o* a
inizio parola, *k*/*t* (due gallows), *sh*/*ch*, -*ey*/-*dy* in fondo. Studiare **come lo scriba sceglie** fra queste
varianti si è rivelato il modo più fecondo di guardare il testo.

### 6.1 Ripetere subito

- Nel Voynich l'1,0% delle coppie di parole vicine è la stessa parola ripetuta (*chol chol*, *qokeedy qokeedy*) e il
  3,9% è una parola quasi uguale (un segno di differenza). Nelle lingue: 0,10% e 0,23% (mediane; massimi 0,71% e
  2,2%); nei sei scribi nordici 0,01–0,05% e 0,2–0,5%; nei 73 scribi tedeschi mediana 0,05% e 0,46% (massimi 0,54% e
  1,20%); nei testi tecnici medievali scritti a mano (erbari, ricettari, astrologia) 0,03–0,15% e 0,2–0,6%; nel copista
  del Copiale praticamente mai.
- Le ripetizioni sono uguali in tutte le sezioni (erbario 1,0%, biologia 1,2%, farmacia 0,9%, ricette 0,9%): non
  dipendono dal genere del contenuto.
- **La ripetizione si spegne in fretta:** dentro la riga è forte fra parole vicine e sparisce dopo 6–7 parole
  (rapporto lontano/vicino 0,12). Nelle lingue è il contrario (mediana 2,86): le lingue evitano di ripetere subito, il
  Voynich ripete subito. Nessun testo di confronto ha questa firma.
- Quando una parola ripetuta cambia l'inizio o la fine, il cambio segue il raccordo con la vicina (*okeey qokeey*: dopo
  -*y* si aggiunge *q*).

### 6.2 Lo "stato" delle scelte

È la scoperta che ci ha impegnato di più, e la sua descrizione è stata precisata più volte lungo la strada (Appendice B).
Questo è lo stato finale.

- **Lo stato breve.** Fra parole vicine della stessa riga lo scriba tende a fare la stessa scelta. Tolte le preferenze
  di ogni parola, della pagina e della posizione, e corretta la distorsione della misura, l'accordo vale +0,13 fra
  parole accanto e +0,09 a due e tre parole (*k*/*t*, *sh*/*ch*, -*ey*/-*dy* insieme; +0,14 per *k*/*t* e +0,18 per
  -*ey*/-*dy* prese da sole). Si dimezza in circa tre parole.
- **Non è copia.** L'accordo è quasi uguale fra parole molto diverse (quattro o più segni di differenza: +0,09) e fra
  parole simili (+0,13). Il generatore di Timm e Schinner, che copia parole vicine modificandole, fa il contrario:
  accordo solo fra parole simili.
- **Non è la posizione nella riga.** Con un confronto che conserva la posizione (e un "placebo" per separare l'effetto
  della procedura), la parte dovuta alla posizione è circa zero.
- **È separato per ogni scelta.** Fra scelte diverse l'accordo è zero (−0,01): non c'è una "modalità marcata" comune;
  *k*/*t* e -*ey*/-*dy* cambiano ciascuna per conto suo.
- **Non dipende da quante volte la scelta compare in mezzo:** vive lungo la riga, di parola in parola, e viene "letto"
  quando la scelta compare.
- **È uguale in tutte le mani** (mani 1, 2, 3: fra +0,12 e +0,15 fra parole accanto), in lingua A e B, in tutte le
  sezioni dove si può misurare, e nelle tre trascrizioni (in Glen Claston le gallows +0,12, i finali +0,14). È una
  **regola del sistema di scrittura**, non l'abitudine di uno scriba.
- **Le varianti di sola forma non mostrano un accordo chiaro.** Le due forme di *d* e le due forme di *e* che solo
  Glen Claston distingue (differenze di forma del segno, non di parola) hanno un accordo debole e incerto (+0,05 /
  +0,06, intervalli che toccano lo zero). Non ne traiamo una regola generale: uno scriba vero ha una finestra in una
  scelta di sola forma (§7).
- **Uno stato lento, in più.** Oltre allo stato breve c'è una componente lenta che passa l'a capo: parole di righe
  consecutive si accordano (+0,05), a due righe meno (+0,03), a 7–12 righe niente. Non è la tendenza dall'alto in basso
  della pagina. Questa componente lenta, a differenza di quella breve, **è normale negli scribi veri** (§7).

**Che cosa dice e che cosa non dice.** Uno stato che dura qualche parola, separato per ogni scelta, è compatibile con
un'abitudine di scrittura regolata (chi scrive "entra" in una variante e ci resta per un po'), con una regola di un
sistema di cifratura o con un procedimento che produce testo. Non dice che le varianti portino informazione, né quale.

### 6.3 La deriva lungo la riga

- Dentro la riga, a parità di parola e senza la prima e l'ultima parola, le varianti *qo*, *k*, *sh*, -*ey* diventano
  più rare andando verso destra: da −0,020 a −0,034 ogni 10 segni, cioè 8–12 punti percentuali da un capo all'altro di
  una riga tipica. La deriva è più ripida nella prima metà della riga e c'è in ogni mano, circa tre volte più forte in
  lingua B.
- Essendo comune a tutte le scelte, non è un effetto dell'inchiostro su un solo tratto (per esempio il trattino che
  distingue *sh* da *ch*). Nessun generatore pubblicato la ha.
- Accanto ai disegni le forme marcate si fanno più rare; in particolare la *q* cade nella parola che comincia subito
  dopo un disegno (−33 punti), non in quella prima. Senza le immagini non si può dire se sia scrittura (si riparte
  contro il disegno con *o-*) o lettura dei trascrittori.

---

## 7. Il confronto con chi scriveva davvero a mano

Molte delle proprietà descritte sopra potrebbero, in linea di principio, essere abitudini normali di uno scriba: chi
scrive a mano abbrevia di più a fine riga, alterna forme di lettera, cambia abitudini da un giorno all'altro. Finora
mancava un confronto sistematico con scribi veri, perché servono trascrizioni che conservino le forme delle lettere, le
righe e le pagine originali. Le abbiamo trovate in due archivi pubblici: Menota (manoscritti nordici) e il ReF
(manoscritti tedeschi). A questi abbiamo aggiunto il copista del cifrario Copiale, che sceglie fra simboli equivalenti
come potrebbe fare chi scrive in un cifrario.

Per ogni proprietà abbiamo usato **la stessa misura** del Voynich, rifacendo il Voynich nella stessa esecuzione.

### 7.1 La tabella

| proprietà del Voynich | Voynich | 6 scribi nordici (1200–1550) | 73 scribi tedeschi (1350–1500) | copista del Copiale | verdetto |
|---|---|---|---|---|---|
| raccordo fra parole vicine (effetto / incertezza della scelta) | 0,058 | 2 scelte su 11 con 0,013–0,015, le altre zero | 2 scelte su 13 con 0,001–0,005, le altre zero | — | **proprio del Voynich** (da 4 a 12 volte il caso più forte) |
| margine sinistro: righe che evitano l'inizio della riga sopra | 5 inizi evitati | 0 su 72 prove | nessun manoscritto con 3 o più inizi evitati; 3 su 72 con uno solo | — | **proprio del Voynich** |
| forme di bordo della riga (quanto cresce la forma più tipica) | fine -*m* +0,151; inizio *s-* +0,098 | +0,016–0,025 (abbreviazioni a fine riga, *v-* a inizio) | +0,019 (il trattino di a capo); +0,012 | — | stessa natura, **da 4 a 8 volte più forte** nel Voynich |
| ripetizione della parola vicina (identica / quasi) | 1,00% / 3,87% | 0,01–0,05% / 0,2–0,5% | mediana 0,05% / 0,46% | 0,00% / 0,04% | **proprio del Voynich** |
| deriva lungo la riga (ogni 10 segni) | da −0,020 a −0,034 | al massimo 0,0075; abbreviazione +0,005 | *[e3c77 in corso]* | — | **proprio del Voynich** (finora) |
| stato breve delle scelte (fra parole accanto; a 2–3 parole) | +0,13; +0,09, uguale fra parole diverse | 1 scelta su 18 con una finestra simile, ma che viene da parole simili | *[e3c77 in corso]* | **alterna** gli omofoni: −0,18 | **non trovato negli scribi** nella forma del Voynich |
| stato lento fra righe consecutive | +0,050 | 6 scelte su 17 con accordo fra righe, 5 grandi come il Voynich | — | — | **normale per chi scrive a mano** |

### 7.2 Che cosa vuol dire

- **Cinque proprietà su sette non hanno paragone** in 79 scribi di tre secoli e tre tradizioni (islandese, norvegese,
  svedese, tedesca), né nel copista di un cifrario: raccordo, margine sinistro, ripetizioni e, finora, deriva lungo la
  riga; le forme di bordo hanno la stessa natura (lo scriba vero abbrevia di più a fine riga) ma sono da quattro a otto
  volte più deboli.
- **Lo stato breve** del Voynich (accordo che vale anche fra parole molto diverse) non l'abbiamo trovato in nessuno
  scriba. Uno scriba norvegese (AM 302 fol, verso il 1300) ha, nella scelta fra *s* lunga e *s* tonda, una "finestra"
  di grandezza e forma simili, che supera le stesse prove del Voynich (non viene da tratti brevi di pagina né dalla
  posizione); ma la sua finestra viene soprattutto da **parole simili** (+0,29 fra parole simili, +0,065 fra parole
  diverse), cioè dal ripetere forme della stessa parola: un meccanismo diverso.
- **Il copista del Copiale fa l'opposto del Voynich:** se nella parola prima ha usato un simbolo per una lettera, nella
  parola dopo tende a usarne un altro (accordo −0,18 fra parole accanto, fino a −0,48 per la *u*). È la pratica di chi
  cifra con omofoni e li fa girare per non lasciare ripetizioni. Le scelte del Voynich non si comportano come gli omofoni
  di questo cifrario.
- **Lo stato lento** che passa da una riga all'altra è invece **normale** per chi scrive a mano (abitudini che cambiano
  piano, o cambi di mano non segnati nei file). Non distingue il Voynich.
- **Anche le ripetizioni non vengono dal genere:** erbari, ricettari e testi di astrologia tedeschi del Quattrocento
  scritti a mano ripetono la parola vicina da 7 a 30 volte meno del Voynich.

In una frase: **il "modo di scrivere" del Voynich non è quello di uno scriba che copia un testo in una lingua con le
normali varianti di forma.** Le sue regole fra parole vicine e ai bordi della riga sono molto più forti. Questo non dice
che cosa sia il testo; dice che chi l'ha scritto seguiva regole che gli scribi normali non seguivano.

---

## 8. Che cosa il Voynich non è

Ogni "no" di questa sezione vale perché il metodo usato dice "sì" quando la risposta c'è (controllo positivo). Dove un
controllo non funzionava, la prova non è stata usata.

### 8.1 Non una lingua scritta in modo ordinario

- L'impronta statistica (§4.1) non corrisponde a nessuna delle circa 100 lingue del campione, e nemmeno ai testi
  tecnici medievali.
- **Lo spazio non è lessicale** (§4.2): nelle lingue lo spazio dipende dalla parola, qui dai segni vicini.
- **Ripetizione immediata e sua forma** (§6.1): le lingue evitano di ripetere subito, il Voynich ripete subito.
- **Nessun legame oltre la parola accanto** (§4.3), mentre le lingue hanno legami anche a distanza.
- **Una cautela onesta:** con la misura corretta, l'accordo delle scelte del Voynich ha la stessa grandezza
  dell'accordo grammaticale delle lingue (per esempio fra le desinenze -*o*/-*a* in italiano o -*us*/-*a* in latino), e
  la sua forma (quanto dura a due-tre parole) sta in cima alla gamma delle lingue, non fuori: il latino tecnico di
  Plinio gli arriva vicino. Lo stato breve, da solo, non basta a distinguere il Voynich da una lingua con accordi; lo
  distinguono l'insieme delle altre proprietà.

### 8.2 Non un testo vero codificato in modo semplice

Abbiamo codificato testi veri (latino, italiano, Bibbia, testi tecnici) in molti modi e misurato se acquistano le
proprietà del Voynich:

- **codice parola per parola** (ogni parola del testo sostituita da una parola del Voynich): prende le lettere e il
  vocabolario del Voynich, ma non le ripetizioni, l'omogeneità della pagina, il raccordo;
- **cifrari verbosi** (ogni lettera diventa un gruppo di 2–3 segni): su 450 varianti nessuna raggiunge la prevedibilità
  del Voynich con parole della sua lunghezza;
- **il cifrario Naibbe**: somiglia per prevedibilità e lunghezza delle parole, non per ripetizioni, parole uniche,
  omogeneità della pagina, giuntura (quasi zero) e proprietà di riga;
- **abbreviazioni, lettere nulle, trasposizioni**: allontanano o non bastano;
- **elenchi, preghiere, litanie** cifrati: prendono la "grana" del Voynich ma non le sue anomalie.

### 8.3 Non una sostituzione leggibile in una lingua nota

- **Sostituzione omofonica con gli spazi in 14 lingue:** nei controlli (lo stesso tipo di cifra su un altro testo
  biblico) si ritrova il 69–98% di parole vere; sul Voynich al massimo il 36%, con 7–93 parole diverse, per lo più
  sempre le stesse tre, come un testo in un'altra lingua.
- **Un risolutore senza spazi** (ricottura simulata con un modello del latino di 9 milioni di lettere), tarato su 56 +
  71 controlli positivi (ritrova la chiave al 98–100%): sul Voynich, contando i segni in quattro modi diversi e a nove
  gradi di raggruppamento, in 71 lingue, anche leggendo al contrario, il risultato non supera mai quello dei controlli
  negativi in modo affidabile. Il "testo" decifrato è una poltiglia di sillabe.
- **Altre prove:** 85 lingue con gli spazi; 16 volgari, lingue storiche e latino abbreviato; un nomenclatore misto;
  ricerche guidate dal contenuto atteso (nomi di piante, mesi); altri ordini di lettura; pezzi di parola come simboli:
  nessuna lettura. Due esiti "formalmente positivi" (un candidato tedesco e uno sillabico) si sono rivelati artefatti:
  il secondo usciva identico sul Voynich rimescolato.
- **Anagrammi ordinati:** l'ordine dei segni dentro le parole è da lingua, non da anagramma.
- **I nomi delle piante come appiglio:** il nome della pianta, cifrato apposta in un controllo, si ritrova nella prima
  parola della pagina; nel Voynich, con le identificazioni disponibili, nessuna traccia.

### 8.4 Le letture pubblicate che abbiamo potuto verificare

- **Bax (2014):** le parole che ricorrono non si comportano da nomi (la "*shor*" letta come "nero" compare 96 volte su
  67 pagine di tutte le sezioni); fuori dalle pagine da cui è stata ricavata, la chiave non batte il caso (p 0,14) e
  produce "nomi" ovunque.
- **Vatne (2021):** si basa su una trascrizione propria; solo un terzo delle sue voci si ritrova nella trascrizione di
  riferimento.
- **Cheshire (2019, lingua "proto-romanza"):** la sua chiave legge come parole romanze più parole del caso, ma
  **qualsiasi** chiave della stessa forma adattata in pochi minuti al manoscritto fa meglio, anche su pagine non usate
  per adattarla (20 chiavi su 20).
- **Schechter (2026, glossario dall'EVA a latino, occitano ed ebraico;** secondo l'autore un manuale farmaceutico
  bilingue latino-occitano, "decifrato all'87,8%"): il suo programma, rifatto, dà gli stessi numeri; ma un "glossario"
  fatto delle parole più frequenti senza alcun significato copre altrettanto, il suo glossario "legge" al 67–70% anche
  un testo senza messaggio, e l'ordine delle parole decifrate non è latino (coppie attestate come rimescolando).
- **Gatta (2026, corrispondenza fra 19 segni EVA e consonanti ebraiche, lettura da destra):** il segnale che c'è sul
  Voynich c'è anche sul testo senza messaggio, e una corrispondenza cercata apposta fa meglio della sua. Lo stesso
  autore, nella versione attuale del suo lavoro, conclude che il testo non si comporta come ebraico e che nessuna pagina
  si legge.

Il **controllo del testo senza messaggio** (applicare la stessa lettura a un testo generato senza contenuto) è semplice
e lo proponiamo come test minimo per chiunque annunci una decifrazione.

### 8.5 Non uno dei meccanismi di cifratura storici simulati

Abbiamo cercato nel Voynich la firma che lascerebbero alcuni sistemi di cifratura del Quattrocento e del Cinquecento,
dopo aver verificato su testi cifrati apposta che la prova la vede:

- **omofoni scelti dal copista** (come nel Copiale): lascerebbero un accordo **negativo** fra parole vicine (il copista
  alterna i simboli); il Voynich ha un accordo positivo;
- **un segno che cambia l'alfabeto** (le lettere-indice del disco cifrante di Leon Battista Alberti, *De componendis
  cifris*, verso il 1466): nessuna parola o segno frequente dopo cui
  lo stato delle scelte riparte (un indice raro non si può escludere);
- **un messaggio a bit nelle scelte doppie** (come il cifrario biletterale di Francis Bacon, ideato verso il 1576–79 e
  descritto nel 1623, dove la forma della lettera porta un bit): un messaggio che ricominci a ogni pagina o riga si vedrebbe con enorme evidenza nei controlli (z fino a 70);
  nel Voynich nessun segnale. Un messaggio continuo che attraversa le pagine resta fuori dalla portata della prova;
- **liste di parole a turno** (l'"Ave Maria" della *Polygraphia* di Giovanni Tritemio, stampata nel 1518, dove ogni
  lettera diventa una parola latina presa dalla tavola successiva e il testo cifrato sembra una preghiera): nessun ritmo da 2 a 6 parole lungo la riga;
- **un'autochiave che riparte a ogni riga** (ogni lettera cifrata dipende dalla precedente; ogni riga ha un avvio
  nuovo): è l'unico meccanismo provato che **chiude la riga** come il Voynich, ma distrugge tutto il resto: nessuna
  ripetizione, un vocabolario gonfiato (da 4.500 a 6.400 parole diverse ogni 10.000, contro 2.900), inizi di riga
  deboli, nessun evitamento sul margine.

### 8.6 Non una lingua artificiale, non il gibberish, non i generatori pubblicati

- **Lingue artificiali** (Esperanto, Volapük, Neo-Quenya, Interlingua, Lojban, Klingon, LOLCat): nessuna ha lo stato
  delle scelte; nessuna ha nemmeno un accordo fra parole accanto.
- **Testo senza senso scritto a mano dai volontari:** non ha giuntura (0,014), non ha forme di bordo, non riprende dalla
  riga sopra, non evita gli inizi ripetuti (anzi li ripete). Chi inventa un testo a mano non produce spontaneamente le
  regole del Voynich.
- **Generatori pubblicati:** il Naibbe non ha giuntura né proprietà di riga; il generatore di Timm e Schinner ha la
  ripresa dalle righe sopra e lo spazio non lessicale, ma pesca troppo lontano, non ha la giuntura chiusa nella riga, né
  lo stato delle scelte (il suo accordo viene dal copiare parole simili), né l'evitamento sul margine, né la deriva; i
  generatori U2 e U3 non hanno la combinazione di catena e riga chiusa. **Nessuno riproduce insieme** giuntura chiusa
  nella riga, memoria corta delle ripetizioni, stato delle scelte, evitamento sul margine.

---

## 9. Che cosa confermiamo e che cosa smentiamo del lavoro precedente

| idea o risultato precedente | il nostro esito |
|---|---|
| **Lingue A e B di Currier** | **Confermate** (98,5% delle pagine; confermate dal lessico 107 su 107 nell'erbario). Differiscono nel lessico, non nei segni; ogni bifoglio è tutto A o tutto B. |
| **Più mani** (Davis) | **Non le mettiamo in discussione**, ma le abitudini fini che distinguono le mani si confondono in parte con le sezioni (le mani 2 e 3 dentro l'erbario non si distinguono). Soprattutto, **tutte seguono le stesse regole** (raccordo, stato delle scelte, margine). |
| **Autocitazione** (Timm e Schinner 2020): lo scriba copia e ritocca parole già scritte | **Confermata in parte.** Lo scriba riprende davvero dalla riga sopra (più del loro generatore) e ripete subito. Ma il riuso del Voynich è **a corto raggio** (riga subito sopra, memoria nella riga di 6–7 parole), **adattato al raccordo**, con uno stato delle scelte che vale anche fra parole diverse: cose che il loro generatore non fa. |
| **Il Naibbe** (Greshko 2025) come spiegazione | **Non regge come spiegazione completa**: niente giuntura, niente proprietà di riga, ripetizioni e parole uniche lontane. |
| **"Parole-chiave"** per argomento (Montemurro e Zanette 2013) | **Non distintive**: le hanno anche testi generati senza messaggio. |
| **Il gibberish somiglia al Voynich** (Gaskell e Bowern 2022, su misure di basso livello) | **Non per le regole di scrittura**: il gibberish a mano non ha giuntura, forme di bordo, ripresa dalla riga sopra, evitamento sul margine, né le regolarità del vocabolario (le parole frequenti non sono le forme più probabili). |
| **"Un segno non è una lettera, una parola non è una parola, uno spazio non è uno spazio"** (Rozanova e Temerev, arXiv 2608.17096, 2026) | **Convergente**: anche noi troviamo una catena di segni con regole ai bordi delle parole, segni troppo regolari per una sostituzione uno a uno, e spazi incerti che si comportano come giunture interne alle parole. Come loro, troviamo che le "parole" formano un vocabolario plausibile e che l'anomalia sta nel modo in cui si susseguono. |
| **Letture di Bax, Vatne, Cheshire, Schechter, Gatta** | **Non reggono** ai controlli (§8.4). |
| **Le etichette dello zodiaco come numeri o giorni** | **No**: quasi tutte diverse, nessuna corrispondenza di posizione fra mesi. |
| **"Il Voynich ha poca sintassi"** | **Non è un'anomalia**: i testi tecnici latini ne hanno altrettanto poca. |

---

## 10. Discussione

### 10.1 Che cosa sappiamo, in una pagina

Il testo del Voynich è prodotto da un sistema di scrittura con tre livelli di regole:

1. **Dentro la parola e fra parole vicine:** una catena di segni con regole di sequenza proprie, in cui gli spazi sono
   confini deboli messi dove la catena lo permette; regole di raccordo fra la fine di una parola e l'inizio della
   seguente, applicate mentre si scrive, guardando una parola avanti.
2. **Nella riga:** la riga è un'unità chiusa, con forme d'inizio e di fine proprie; le scelte fra varianti seguono uno
   stato breve (2–3 parole) e una deriva verso le forme semplici andando a destra; le parole si ripetono subito e la
   ripetizione si spegne in poche parole.
3. **Fra le righe e nel libro:** la riga sotto copia dalla riga subito sopra, adattando le copie alle regole di
   raccordo, ed evita di cominciare come lei; il paragrafo ha un'apertura e una chiusura proprie; pagina, bifoglio e
   fascicolo hanno un'identità; il bifoglio è un'unità di lavoro.

Molte di queste regole sono **del sistema**, non della persona: valgono uguali nelle mani diverse, nelle due "lingue"
di Currier, in tutte le sezioni, nelle tre trascrizioni.

### 10.2 Che cosa questo esclude e che cosa lascia aperto

**Esclude**, con i controlli descritti:

- una lingua naturale scritta in un alfabeto ordinario, letta con una sostituzione (semplice o omofonica) in una delle
  lingue provate;
- le letture pubblicate che abbiamo potuto verificare;
- i meccanismi di cifratura storici simulati, presi uno per uno;
- un testo inventato a mano senza regole (il gibberish dei volontari non ha le regole del Voynich);
- che le regole del Voynich siano le normali abitudini di uno scriba (79 scribi veri non le hanno).

**Lascia aperti** tre scenari, che i nostri dati non sanno separare:

1. **Una lingua scritta con un sistema di scrittura molto artificiale**: per esempio un sistema in cui le varianti
   (*k*/*t*, -*ey*/-*dy*…) non portano significato ma seguono regole di forma, e in cui gli spazi non separano le
   parole del testo. Una lettura sarebbe possibile solo con un aggancio esterno.
2. **Un codice o un cifrario di un tipo non provato**, per esempio con un repertorio di parole o un libro-chiave
   perduto. In questo caso la statistica non basta.
3. **Nessun messaggio:** un testo prodotto da un procedimento eseguibile a mano. Un procedimento di questo tipo (il
   generatore ad autocitazione di Timm e Schinner, con una regola sulle giunture aggiunta da noi) riproduce già molte
   delle proprietà di base (prevedibilità, somiglianza fra parole della pagina, ripetizioni, legame fra parole vicine),
   ma non le regole di riga e di pagina descritte qui.

I nostri dati spostano un poco il peso verso gli scenari 1 e 3 rispetto a un cifrario storico classico, perché le
regole del Voynich sono "regole di forma" e nessun cifrario provato le riproduce. Ma **non li separano**.

### 10.3 Un'avvertenza: un messaggio può nascondersi nelle scelte

In un lavoro collegato (lo strumento che chiamiamo "voynichizzatore", sviluppato in parallelo) abbiamo verificato che
un testo vero, compresso e cifrato con una chiave, si può nascondere nelle scelte fra varianti (*k*/*t*, *sh*/*ch*,
-*ey*/-*dy*, *qo*/*o*…) di un testo con le proprietà del Voynich, **senza renderlo più riconoscibile** a un
discriminatore statistico. La capacità di questo canale è di circa 0,8 bit per scelta, cioè circa 46.000 bit per un libro
come il Voynich (l'equivalente di circa 2.000 parole latine compresse). Quindi **le proprietà statistiche da sole non
possono dimostrare che il testo non abbia significato**: un testo "senza messaggio" e un testo con un messaggio nascosto
nelle scelte possono avere le stesse statistiche.

### 10.4 Perché la statistica da sola non arriverà a una lettura

Tutti i nostri strumenti misurano **regolarità**. Una lettura richiede di sapere che cosa **rappresentano** i segni, e
questo le regolarità non lo dicono: un sistema di scrittura molto regolare può nascondere una lingua, un codice o niente.
Per arrivare a una lettura servirebbe un elemento esterno: un testo di cui il Voynich sia la copia (un erbario o un
trattato noto), un'identificazione sicura di molte piante da usare come appiglio, una chiave ritrovata in un archivio.

### 10.5 Che cosa ci farebbe cambiare idea

- Un sistema di lettura che superi i controlli usati qui: che funzioni sul testo vero e non su quello rimescolato o
  generato senza messaggio, che produca frasi sensate su pagine mai viste prima, e che spieghi le regole di scrittura
  descritte (raccordo, riga chiusa, stato delle scelte, copia dalla riga sopra, margine).
- Uno scriba medievale, o un cifrario storico, con le stesse regole: cambierebbe la lettura di tutto il lavoro.
- Un procedimento semplice che le riproduca tutte insieme.

---

## 11. Limiti e lacune dichiarate

- **Effetti piccoli.** Molte delle proprietà nuove sono piccole in assoluto (l'accordo delle scelte vale circa 13
  punti percentuali fra parole accanto) e hanno richiesto correzioni di metodo. Le abbiamo riportate con intervalli e
  repliche, ma restano misure sottili.
- **Trascrizioni.** Tutto dipende dalle trascrizioni: le tre usate divergono su circa una parola su otto. Le misure
  principali reggono su tutte e tre, ma senza le immagini non possiamo distinguere ciò che fece lo scriba da ciò che
  leggono i trascrittori (per esempio la *q* che cade dopo un disegno).
- **Scribi di confronto.** 79 scribi nordici e tedeschi; mancano scribi latini o italiani del Quattrocento trascritti
  a livello di facsimile, e scribi inglesi del Medioevo (noti per la grafia molto variabile). I manoscritti nordici e
  tedeschi non segnano i cambi di mano.
- **Cifrari storici.** Un solo cifrario vero (il Copiale, del Settecento). L'archivio DECODE, che raccoglie centinaia di
  cifrari del Quattro-Cinquecento, richiede un account e non ha una licenza di riuso; nessun cifrario del Quattrocento
  vi compare con trascrizione e chiave insieme.
- **Prove che non abbiamo potuto fare,** perché le misure, provate su testi finti, non distinguevano i casi:
  - se lo stato delle scelte dura un certo numero di **parole** o un certo **tempo di scrittura** (segni);
  - se gli stati delle diverse scelte **cambiano negli stessi punti** (che indicherebbe unità nascoste di qualche
    parola);
  - se lo stato **breve** passa l'a capo (quello lento sì).
- **Una prova con pochi dati:** se lo stato sopravvive al salto di un disegno (la stima è positiva ma l'intervallo è
  troppo largo per dirlo).
- **Fonti:** tutti i riferimenti sono stati verificati su pagine dell'editore, del repository o dell'archivio; restano
  due cautele (Appendice D): il PDF di Bax non è stato riletto nella pagina del titolo, e la datazione al radiocarbonio
  è nota da un comunicato dell'università più che da un articolo scientifico.
- **In corso** al momento di questa bozza: lo stato breve e la deriva nei 73 scribi tedeschi (esperimento e3c77); un
  confronto fra manoscritti e libri a stampa dello stesso corpus.

---

## 12. Riproducibilità

Ogni esperimento ha:

- una **preregistrazione** datata (`preregistrazioni/eNN.md`), scritta prima dell'esecuzione;
- un **programma** (`esperimenti/eNN_*.py`) in Python 3.12, con semi del caso fissi;
- un **registro di esecuzione** con la versione del codice e dei dati (`risultati/provenienza/`);
- un **risultato** in tabella (`risultati/eNN_*.md`) e in formato completo (`.json`);
- una voce nel **quaderno di laboratorio**, scritto solo aggiungendo.

Rifacendo un esperimento si ottengono gli stessi numeri. Il repository è al momento privato; i dati protetti da diritto
d'autore non vi sono inclusi e vanno riscaricati dalle fonti (Appendice D).

---

## Appendice A. Gli esperimenti dietro le scoperte principali

| scoperta | esperimenti principali | repliche |
|---|---|---|
| Impronta statistica, isolamento dalle lingue | e01–e06, e13 | IT, GC |
| Spazio debole e prevedibile, tagli che danno parole, vocabolario che riempie le forme | e3a49, e3a55, e3a58, e3a61, e3a67, e3a99–e3b05 | e3a50, e3a56, e3a60, e3a68 |
| Giuntura e regole di raccordo | e377, e380, e390, e3a01–e3a03, e3a41 | e388, e395, e3a04, e3a05, e3a34 |
| Riga chiusa, salto del disegno, forme di bordo | e384, e386, e387, e389, e3a09 | e395, e3a43 |
| Copia dalla riga subito sopra | e340, e343, e347, e372, e385, e392, e394, e396, e3b28 | e3a80, e3a84 |
| Evitamento sul margine sinistro | e3a25–e3a27, e3a33, e3a35, e3a44 | e3a33 (IT, lingua A e B) |
| Paragrafo, pagina, bifoglio, fascicolo, lingue A e B | e302, e307–e316, e321, e350, e356, e378 | e3a15, e3a21 |
| Ripetizione immediata e sua forma | e02, e3a86–e3a90, e3b25 | e3a88, e3a91, e3a92 |
| Stato breve delle scelte | e3c33, e3c48, e3c52, e3c55, e3c57, e3c66, e3c72, e3c81 | IT, GC (e3c51), mani, sezioni (e3c54) |
| Stato lento | e3c73–e3c75 | e3c76 (scribi) |
| Deriva lungo la riga | e3c13, e3c17, e3c20–e3c24 | IT |
| Batteria scribi | e3c50, e3c58–e3c65, e3c76–e3c80 | — |
| Copiale | e3c61 | — |
| Decifrazioni e letture escluse | e14, e16–e20, e26, e27, e133, e163, e163b, e212b, e216, e219, e222, e223, e249, e269 | controlli positivi in ogni prova |
| Meccanismi di cifratura storici | e3c68–e3c71 | controlli finti in ogni prova |
| Lingue artificiali, gibberish, generatori | e346, e374, e377, e382, e399, e3a95, e3c37, e3c49, e3c53 | — |

## Appendice B. Verifiche interne: indicazioni provvisorie corrette dal metodo

Nessuno dei risultati di questo lavoro è stato pubblicato prima. Durante il lavoro, però, alcune misure intermedie hanno
dato indicazioni che le verifiche successive hanno corretto. Le riportiamo perché mostrano quali misure sono fragili e
come i controlli le hanno corrette: chi vorrà rifare il lavoro potrà evitare gli stessi passi falsi, e chi legge può
giudicare quanto le conclusioni finali siano state messe alla prova.

**Correzioni dovute alla distorsione della misura dell'accordo (§3.3)**

1. Una prima misura attribuiva allo scriba anglosassone degli *Hatton Gospels* la stessa "finestra" del Voynich. Per
   quella scelta la misura era gonfiata (+0,25); corretta, lo scriba ha un accordo fra parole accanto ma non a 2–3
   parole.
2. Il Volapük sembrava avere un accordo simile a quello del Voynich; con la misura corretta è a zero.
3. La forma dell'accordo del Voynich (quanto dura a 2–3 parole) sembrava fuori dalla gamma delle lingue; corretta, sta
   in cima alla gamma, non fuori.
4. Un'osservazione sulle parole "neutre" fra due parole che fanno la stessa scelta suggeriva che lo stato viaggiasse
   solo sulle occorrenze della scelta; era un effetto della stessa distorsione.

**Descrizioni rese più precise da misure successive**

5. Lo stato delle scelte sembrava una "finestra" di tre parole che poi scende a zero; si spegne invece poco a poco
   (mezza vita circa tre parole) e c'è in più una componente lenta che passa da una riga all'altra.
6. L'ipotesi che ogni riga avesse una sua "impostazione" delle scelte (come una chiave per riga) non ha retto:
   l'accordo passa da una riga all'altra.
7. Dopo la prova sulle forme di sola lettera di Glen Claston avevamo letto lo stato come legato a "quale parola si
   scrive, non come si traccia la lettera"; uno scriba vero con una finestra in una scelta di sola forma ha mostrato che
   la generalizzazione era troppo ampia (e la sua finestra, a sua volta, viene da parole simili).
8. Una misura senza correzione indicava che la mano 1 non avesse lo stato delle scelte; con la misura corretta tutte le
   mani lo hanno uguale.
9. Una misura indicava che la memoria delle scelte si azzerasse all'a capo; era un effetto del confronto con la media
   della pagina (fine e inizio riga hanno forme proprie).
10. Il primo controllo del margine sinistro usava un confronto difettoso; con il confronto corretto il risultato regge.
11. Una misura attribuiva al paragrafo due terzi del piccolo legame fra parole intere; era un effetto meccanico dei
    gruppi più piccoli.
12. Le forme rare sembravano riprese più delle altre dalla riga sopra; con la seconda trascrizione resta solo una
    tendenza.

**Esiti formalmente positivi che erano artefatti**

13. Un candidato di lettura "una parola = una sillaba" e un candidato tedesco in una ricerca guidata dal contenuto: il
    primo usciva identico sul Voynich rimescolato, il secondo cambiava segno cambiando solo i punti di partenza della
    ricerca.

**Criteri formulati in modo troppo netto**

14. In tre casi il criterio deciso in anticipo chiamava "assente" o "azzerato" un effetto il cui intervallo di
    incertezza toccava lo zero (lo stato nell'erbario, al salto del disegno, in alcune sezioni). In tutti e tre la stima
    era positiva e simile al resto: erano dati insufficienti, non assenza. Da qui la regola, che proponiamo anche ad altri,
    di dire "manca" solo quando l'intervallo sta tutto sotto il valore di riferimento.

## Appendice C. Glossario (italiano / inglese)

- **EVA**: alfabeto convenzionale per trascrivere il Voynich in lettere latine; non indica suoni.
- **segno** (glyph): un carattere del manoscritto; *ch*, *sh*, i gallows e i loro composti contano come uno.
- **gallows**: i segni alti *k*, *t*, *p*, *f* dell'EVA.
- **lingue A e B di Currier** (Currier languages): le due varietà di scrittura in cui si dividono le pagine.
- **giuntura** (cross-boundary information): quanta informazione l'ultimo segno di una parola dà sul primo della
  seguente, oltre il caso.
- **raccordo** (junction rule, sandhi-like rule): regola che lega la forma di una parola a quella della vicina.
- **riga chiusa** (line as closed unit): la giuntura non passa all'a capo.
- **stato delle scelte** (choice state): la tendenza a ripetere la stessa variante per alcune parole.
- **deriva lungo la riga** (in-line drift): il calo delle varianti marcate da sinistra a destra.
- **preregistrazione** (preregistration): descrizione scritta, prima di eseguire, di domanda, misura e criterio.
- **controllo positivo / negativo** (positive / negative control): testo in cui la risposta c'è / non c'è.
- **cifra omofonica** (homophonic cipher): la stessa lettera si può scrivere con più simboli.
- **cifrario verboso** (verbose cipher): ogni lettera diventa un gruppo di più segni.
- **autocitazione** (self-citation): procedura in cui chi scrive copia e ritocca parole già scritte.
- **facsimile** (facsimile-level transcription): trascrizione che conserva le forme delle lettere del manoscritto.
- **intervallo al 95%** (95% confidence interval): l'intervallo in cui cade il valore vero, con buona fiducia.

## Appendice D. Fonti e licenze

### D.1 Dati

**Il Voynich.**

- R. Zandbergen, file di traslitterazione del manoscritto Voynich in formato IVTFF, <https://www.voynich.nu/transcr.html>:
  Zandbergen-Landini (ZL3b, EVA), Takahashi (IT2a), Glen Claston (GC2a, alfabeto v101); formato descritto in R.
  Zandbergen, *IVTFF – Intermediate Voynich MS Transliteration File Format*, v2.0.1 (2025).
- Datazione al radiocarbonio della pergamena (1404–1438, al 95%): laboratorio NSF-Arizona AMS dell'Università
  dell'Arizona, gruppo di G. Hodgins, quattro campioni misurati nel 2009; comunicato dell'Università dell'Arizona, 10
  febbraio 2011; resoconto di R. Zandbergen, <https://www.voynich.nu/extra/carbon.html>.

**Testi di confronto.**

- C. Christodouloupoulos e M. Steedman (2015), "A massively parallel corpus: the Bible in 100 languages", *Language
  Resources and Evaluation* 49(2): 375–395, doi:10.1007/s10579-014-9287-y (dati: christos-c/bible-corpus, CC0).
- The Latin Library (raccolta cltk/lat_text_latin_library); breviario romano (Divinum Officium, MIT).
- D. E. Gaskell e C. L. Bowern (2022), "Gibberish after all? Voynichese is statistically similar to human-produced
  samples of meaningless text", in C. Layfield e J. Abela (a cura di), *Proceedings of the 1st International Conference
  on the Voynich Manuscript 2022 (VOY2022)*, CEUR Workshop Proceedings 3313, paper 4 (2023),
  <https://ceur-ws.org/Vol-3313/paper4.pdf>. I testi senza senso sono stati scritti a mano da volontari (42 nello
  studio; 38 testi nei dati pubblicati); licenza dei dati: MIT modificata.
- M. A. Greshko (2025), "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich
  Manuscript-like ciphertext", *Cryptologia*, pubblicato online il 26 novembre 2025, doi:10.1080/01611194.2025.2566408
  (codice: greshko/naibbe-cipher).
- T. Timm e A. Schinner (2020), "A possible generating algorithm of the Voynich manuscript", *Cryptologia* 44(1): 1–19,
  doi:10.1080/01611194.2019.1596999 (codice: TorstenTimm/SelfCitationTextgenerator, MIT).
- **Menota**, Medieval Nordic Text Archive, <https://www.menota.org> (catalogo su Clarino, Università di Bergen). La
  licenza è indicata testo per testo; per i sei testi usati (AM 519 a 4to, AM 677 4to, AM 60 4to, AM 242 fol, Holm A 10,
  AM 302 fol) è CC-BY-SA 4.0. Ogni testo va citato con i dati della sua intestazione (editore, versione).
- **ReF**: K.-P. Wegera, H.-J. Solms, U. Demske, S. Dipper (2021), *Reference Corpus of Early New High German
  (1350–1650)*, versione 1.0.2, Zenodo, doi:10.5281/zenodo.5793616. Zenodo indica la licenza CC BY 4.0, il file LICENSE
  dentro l'archivio CC BY-SA 4.0: ci atteniamo alla più restrittiva.
- **Copiale**: K. Knight, B. Megyesi, C. Schaefer (2011), "The Copiale Cipher", in *Proceedings of the 4th Workshop on
  Building and Using Comparable Corpora (BUCC)*, ACL, pp. 2–9, <https://aclanthology.org/W11-1202/>; e K. Knight, B.
  Megyesi, C. Schaefer, "The Secrets of the Copiale Cipher", *Journal for Research into Freemasonry and Fraternalism*
  2(2): 314–324 (volume del 2011, pubblicato nel 2012), doi:10.1558/jrff.v2i2.314. Trascrizione e decifrazione dal sito
  del progetto dell'Università di Stoccolma. Datazione: metà del Settecento (la scritta "1866" nel manoscritto è una nota
  di possesso).

### D.2 Letture e decifrazioni verificate

- S. Bax (2014), *A proposed partial decoding of the Voynich script*, PDF pubblicato in proprio, gennaio 2014 (letto
  dall'archivio web).
- S. B. Vatne (2021), *Cracking the Voynich Cipher*, PDF pubblicato in proprio, ottobre 2021.
- G. Cheshire (2019), "The Language and Writing System of MS408 (Voynich) Explained", *Romance Studies* 37(1): 30–67,
  doi:10.1080/02639904.2019.1599566.
- S. Schechter (2026), *voynich-decoded*, repository GitHub, <https://github.com/scott-schechter/voynich-decoded>
  (nessuna licenza dichiarata; usato in copia locale, non ridistribuito).
- A. Gatta (2026), *voynich-toolkit* (software), Zenodo, doi:10.5281/zenodo.19226178 (DOI di tutte le versioni; la
  versione provata è la v0.26.0), licenza MIT.

### D.3 Letteratura

- P. H. Currier (1976), "Papers on the Voynich Manuscript", in M. E. D'Imperio (a cura di), *New Research on the
  Voynich Manuscript: Proceedings of a Seminar*, Washington (dattiloscritto); trascrizione di J. Guy e J. Reeds (1992),
  <https://www.voynich.nu/extra/curr_main.html>.
- L. Fagin Davis (2020), "How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript",
  *Manuscript Studies* 5(1): 164–180, doi:10.1353/mns.2020.0011 (le cinque mani usate qui).
- M. A. Montemurro e D. H. Zanette (2013), "Keywords and co-occurrence patterns in the Voynich manuscript: an
  information-theoretic analysis", *PLoS ONE* 8(6): e66344, doi:10.1371/journal.pone.0066344.
- B. Hauer e G. Kondrak (2016), "Decoding Anagrammed Texts Written in an Unknown Language and Script", *Transactions of
  the Association for Computational Linguistics* 4: 75–86, doi:10.1162/tacl_a_00084.
- L. Rozanova e A. Temerev (2026), "A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space: What the
  Units of Voynichese Are Not", arXiv:2608.17096.
- L. B. Alberti, *De componendis cifris* (verso il 1466); G. Tritemio, *Polygraphiae libri sex* (1518); F. Bacon, *De
  dignitate et augmentis scientiarum* (1623), con la descrizione del cifrario biletterale.

*Tutti i riferimenti sono stati verificati su pagine dell'editore, del repository o dell'archivio (ottobre 2026). Per
Bax non è stato possibile rileggere la pagina del titolo del PDF; per la datazione al radiocarbonio la fonte è un
comunicato dell'università, non un articolo scientifico.*
