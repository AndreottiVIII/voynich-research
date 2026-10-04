# Dossier per un white paper: il manoscritto Voynich messo alla prova

Questo file riassume tutto il lavoro fatto e quello che se ne è capito, in modo che chi
scrive il white paper non abbia bisogno d'altro. Ogni numero viene da un esperimento
ripetibile. Codice, dati e risultati completi sono nel repository:

- repository: <https://github.com/AndreottiVIII/duri-a-morire>, cartella `voynich/`
- ramo: `claude/voynich-decipherment-mwvrge`
- rapporto completo: `voynich/README.md`; un risultato per esperimento in `voynich/risultati/`
  (`.json` con tutti i numeri, `.md` con la tabella, grafici in versione chiara e scura)
- analisi eseguite con Claude Code (Anthropic), in più sessioni, settembre 2026

## 0. Istruzioni per chi scrive il white paper

- **Non c'è una decifrazione.** Il white paper non deve dichiararne una, né lasciarla
  intendere. Il risultato è una mappa di che cosa il Voynich *non* è, con i controlli, e di
  quale modello gli si avvicina di più.
- **Ogni esito negativo vale solo perché i controlli positivi riescono.** Quando si cita un
  "no", conviene citare anche il controllo che mostra che il metodo avrebbe detto "sì".
- **Tenere le cautele** della sezione 7: un esito negativo esclude un modello preciso per le
  lingue provate, non "ogni decifrazione".
- **Numeri:** qui in formato italiano (virgola decimale). "×1,0" indica un rapporto rispetto al
  caso o a un riferimento; "bit" è un'unità di informazione.
- **Lingua:** il dossier è in italiano; il white paper può essere in italiano o in inglese. Nel
  glossario (sezione 11) ci sono i termini tecnici con l'equivalente inglese.
- **Figure:** l'elenco delle figure già pronte è nella sezione 9.

## 1. Sintesi

Il manoscritto Voynich (Beinecke MS 408, pergamena datata al radiocarbonio 1404–1438) è scritto
in un alfabeto mai letto. In 28 esperimenti ripetibili, con controlli positivi e negativi per
ogni metodo, abbiamo misurato come si comporta il suo testo e messo alla prova le principali
ipotesi: una lingua scritta con un alfabeto normale, un cifrario (semplice, omofonico, verboso,
il Naibbe), un codice parola per parola, anagrammi, abbreviazioni, lettere nulle,
trasposizioni, contenuti non in prosa (elenchi, preghiere), due decifrazioni pubblicate di
recente, e un testo senza messaggio prodotto da una procedura.

In breve:

1. Il testo ha un'impronta che **nessuna lingua naturale** del campione (circa 100 lingue) ha:
   - segni troppo prevedibili;
   - spazi in gran parte prevedibili dal segno che li precede;
   - parole che ripetono la precedente tanto spesso quanto due parole qualsiasi della stessa riga;
   - parole della stessa pagina che si somigliano nella grafia, sempre meno allontanandosi di riga.
2. **Nessun attacco di sostituzione** lo legge: in 14 lingue con gli spazi, in 71 senza,
   contando i segni in molti modi. Lo stesso attacco rompe tutti i controlli positivi.
3. **Nessuna codifica di un testo vero** provata riproduce insieme le sue anomalie: codici
   parola per parola, cifrari verbosi, il Naibbe, abbreviazioni, nulle, trasposizioni, elenchi,
   preghiere e litanie.
4. **Due decifrazioni pubblicate** con codice pubblico (Schechter, latino; Gatta, ebraico)
   "leggono" allo stesso modo un testo senza messaggio.
5. **Il modello che si avvicina di più è senza messaggio:** il generatore ad autocitazione di
   Timm e Schinner (2020), in cui chi scrive copia e ritocca parole già scritte. Con una regola
   in più sulle giunture fra parole, aggiunta qui, riproduce quasi tutta la lista di controllo.
6. **Resta un divario sul vocabolario:** il Voynich ha più parole usate una volta sola (68%
   contro 50–54%). Errori di scrittura o di lettura ne spiegano una parte, e le parole uniche
   del Voynich ne hanno l'aria. Ma aggiunti al generatore lo rendono meno prevedibile del
   Voynich.

Tre possibilità restano aperte e non sono ancora distinte:

- un contenuto che non è prosa, scritto con unità più grandi delle lettere;
- una scrittura con convenzioni che cambiano da pagina a pagina;
- nessun messaggio.

La terza è la più avanti: è l'unica che produce da sola le anomalie principali.

## 2. Il problema e le ipotesi

- **Il manoscritto:** circa 240 pagine con disegni di piante, astronomia e zodiaco, figure
  femminili in vasche, recipienti da farmacia, e una sezione finale di solo testo ("ricette").
  Le pagine si dividono in due varietà di scrittura, le "lingue" A e B di Currier (anni '70).
- **L'alfabeto EVA** trascrive i segni in lettere latine (*qokeedy*, *daiin*, *chol*…). Non dice
  niente sul suono: è un'etichetta. Alcuni segni si scrivono con più lettere EVA (*ch*, *sh*,
  *cth*, *ckh*, *cph*, *cfh*): qui li contiamo come un segno solo.
- **Le ipotesi messe alla prova:**
  1. una lingua naturale in un alfabeto normale;
  2. un testo "tokenizzato": unità più grandi delle lettere, cioè gruppi di segni per una
     lettera (cifrario verboso), sillabe, codici per parola, il Naibbe;
  3. un cifrario classico: sostituzione semplice o omofonica, trasposizione, nulle,
     abbreviazioni, anagrammi;
  4. un contenuto particolare (elenchi, formule, preghiere, litanie);
  5. nessun messaggio: un testo prodotto da una procedura.

## 3. Dati e metodo

### 3.1 Dati (tutti con versione fissata)

**Trascrizioni** (formato IVTFF di René Zandbergen), copiate dal repository
Krymorn/The-Voynich-Transliteration-Tool con le impronte SHA-256 degli originali:

| trascrizione | alfabeto | versione | ruolo |
|---|---|---|---|
| Zandbergen-Landini (ZL) | EVA | 3b del 13/05/2025 | riferimento |
| Takahashi (IT) | EVA di base | 2a, rivista 25/06/2025 | controllo |
| Glen Claston (GC) | v101 | 2a, rivista 25/06/2025 | controllo |

- Si usa il testo in paragrafi: circa 35.000 parole leggibili. Etichette, testi in cerchio e
  raggi restano fuori; le parole con segni illeggibili (0,6%) sono scartate.

**Testi di confronto** (scaricati a commit fisso da `prepara.py`):

- la Bibbia in 100 lingue (christos-c/bible-corpus, CC0);
- la Latin Library (cltk/lat_text_latin_library), per i testi tecnici latini e un modello del
  latino di circa 9 milioni di lettere;
- il cifrario Naibbe di Greshko (greshko/naibbe-cipher, MIT modificata);
- il generatore ad autocitazione di Timm e Schinner (TorstenTimm/SelfCitationTextgenerator,
  MIT, Java);
- il breviario romano in latino (DivinumOfficium/divinum-officium, MIT);
- la decifrazione di Schechter (scott-schechter/voynich-decoded; nessuna licenza dichiarata,
  letta in cache e non ridistribuita);
- il toolkit di Gatta (antenore/voynich-toolkit, MIT).

### 3.2 Principi di metodo

- **Controlli prima di tutto.** Ogni metodo si prova su:
  - un *controllo positivo*: un testo noto, trattato come il Voynich; il metodo deve
    risolverlo;
  - un *controllo negativo*: un testo in un'altra lingua, o senza niente da trovare; dice
    quanto si ottiene per caso.
- **Scala normalizzata** per i risolutori: 0 = controllo negativo, 1 = controllo positivo; il
  Voynich si colloca su questa scala.
- **Confronti alla pari:** campioni della stessa lunghezza e, nei controlli, lo stesso numero
  di simboli del Voynich letto in quel modo.
- **Riproducibilità:** semi del caso fissi, dati a commit fisso; rifacendo, i numeri tornano
  identici.
- **Segni composti fusi:** senza fonderli il testo sembrerebbe più prevedibile di quanto è.

### 3.3 La lista di controllo

È lo strumento centrale: nove proprietà che chiunque proponga una decifrazione, un cifrario o un
meccanismo deve riprodurre tutte insieme (tabella completa in sezione 5.6):

- h2;
- quanto è prevedibile lo spazio;
- varietà del vocabolario e parole uniche;
- ripetizione immediata;
- somiglianza di pagina, vicino e a sei righe;
- legame fra la fine di una parola e l'inizio della successiva;
- parole vicine che unite danno parole esistenti.

## 4. Risultati per tema

I numeri fra parentesi quadre indicano l'esperimento (e01–e28; file in `risultati/`).

### 4.1 L'impronta statistica del Voynich

- **Segni troppo prevedibili [e01].**
  - Con i segni EVA fusi, l'incertezza sul segno successivo (h2) è 2,2 bit. Le lingue con un
    alfabeto di taglia simile stanno fra 2,6 e 3,3 (latino 3,3, italiano 3,2, testi tecnici
    latini 3,2–3,4).
  - Senza spazi: 2,5 contro 2,9–3,5. Fra porzioni diverse del testo i valori cambiano di
    0,01–0,03 bit.
  - Con l'alfabeto v101 di Glen Claston, che conta come un segno solo alcuni gruppi EVA (le
    serie di *i*), il distacco si riduce: 2,5 contro 2,8–3,3 con gli spazi, 2,9 contro 2,8–3,6
    senza, cioè al margine delle lingue.
  - Quindi parte della prevedibilità dipende da come si tagliano i segni (le unità vere sono
    più grandi delle lettere EVA), e parte dai confini di parola.
  - Una sostituzione semplice non cambia questi numeri: per le lingue del campione è esclusa.
- **Il cifrario verboso non ci arriva [e07].** Su 450 cifrari "una lettera = 2–3 segni"
  applicati a latino e italiano, nessuno raggiunge la prevedibilità del Voynich. I più vicini
  (h2 2,4–2,5) hanno parole di 8–10 segni, il doppio delle sue (4,5). Servirebbe un testo in
  chiaro con parole di due lettere in media.
- **Ripetizione immediata [e02, e04, e07].** Nel Voynich una parola è identica alla precedente
  tanto spesso quanto due parole qualsiasi della stessa riga (×1,0). Su 95 testi naturali la
  mediana è ×0,12: la grammatica lo impedisce. Unica eccezione l'indonesiano, che forma il
  plurale raddoppiando la parola. Le ripetute sono parole piene (*chol*, *qokeedy*, *daiin*).
  Qualsiasi codice parola per parola conserva la proprietà della lingua di partenza (tutte le
  codifiche provate stanno fra ×0,1 e ×0,5).
- **Omogeneità di pagina [e04, e05].**
  - Due parole diverse della stessa riga si somigliano nella grafia il 3,8–4,0% più di due
    parole qualsiasi del testo; nei testi naturali da −0,4% a 1,5%. Il massimo viene dalle
    lingue bantu, per la concordanza dei prefissi.
  - Circa quattro quinti dell'effetto vengono dalla pagina intera, il resto dalle righe vicine:
    la somiglianza cala con la distanza fra le righe (3,4% a sei righe).
  - Tiene con due trascrizioni, dentro le lingue A e B di Currier, e fondendo i segni che i
    trascrittori confondono.
  - La "copiatura fra parole adiacenti" di alcuni studi, a guardarla bene, riguarda la riga e
    la pagina, non le parole adiacenti.
- **La "poca sintassi" non è un'anomalia [e03].** Contro la Bibbia il Voynich sembrava avere
  poca sintassi, ma i testi tecnici latini ne hanno altrettanto poca: era la Bibbia, molto
  formulaica, a essere un confronto sbagliato.
- **Le lingue A e B di Currier** si ritrovano con questi strumenti nel 98,5% delle pagine [e06].
- **Gli spazi [e11, e12].**
  - Lo spazio si prevede per due terzi (66%) dal segno che lo precede; nelle lingue la mediana
    è 17%.
  - Unendo due parole vicine si ottiene una parola che il manoscritto usa altrove nel 9,2% dei
    casi (4,8% unendo parole a caso; nelle lingue 0,1–0,7%, pari al caso).
  - Spazi segnati come incerti: l'unione è attestata nel 43,5% dei casi (31% per caso); spazi
    certi: 6,1% (3,4% per caso).
  - Giunture "morbide", prima di *aiin*, *ar*, *al* e dopo *o*: 40–56% (*s aiin* → *saiin*).
    Giunture "dure", prima di *q* e dopo *m*: 0–1%.
  - Le parole sono fatte di pezzi che si attaccano e si staccano. Togliere gli spazi dubbi non
    avvicina il testo a una lingua.
- **Legame fine-inizio [e11].** Come comincia una parola dipende da come è finita la precedente:
  0,19 bit (lingue 0,02–0,40, mediana 0,07). È un legame da lingua con particelle.
- **Isolato da tutte le lingue [e13].** Su nove misure insieme, la distanza del Voynich dalla
  lingua più vicina è 9,9 (5,5 senza l'omogeneità di pagina). La lingua più isolata del
  campione sta a 4,1 dalla sua vicina. Misure più anomale: omogeneità di pagina +10,7
  deviazioni standard, spazio prevedibile +5,8, prevedibilità del segno −3,5. Le lingue "più
  vicine" (potawatomi, chinanteco, ewe, malgascio) non hanno niente in comune fra loro.
- **Le etichette dello zodiaco non sono numeri [e15].** Circa 30 figure per segno, come i gradi
  o i giorni. Ma le etichette sono quasi tutte diverse (264 su 299), e quelle nella stessa
  posizione in segni diversi non si somigliano più del caso (p = 0,46). La loro grafia scivola
  con regolarità dai Pesci al Sagittario (da *-al-* a *-eo-*): la stessa deriva di stile delle
  pagine.

### 4.2 Codifiche di testi veri: nessuna riproduce le anomalie

- **Codice parola per parola [e07, e09].** Sostituire ogni parola di un testo latino con una
  parola del Voynich di pari frequenza dà le lettere e il vocabolario del Voynich, ma non le
  sue anomalie: niente ripetizioni immediate, niente omogeneità di pagina. Il grafico e09 mette
  le due anomalie su due assi: il Voynich sta da solo.
- **Un codice con "stile di pagina"** (lo scriba cambia abitudini a ogni pagina: *ch* per *sh*,
  *q* in testa…) produce omogeneità, anche troppa. Ma è uguale a ogni distanza fra le righe,
  il vocabolario diventa troppo vario e le ripetizioni restano evitate.
- **Il cifrario Naibbe [e10]** (Greshko 2025: il testo si taglia in pezzi di una o due lettere,
  ogni pezzo diventa una "parola" presa da sei tabelle, con un mazzo di carte). Provato sul
  Plinio cifrato dall'autore, su Vitruvio e sulla Bibbia latina e italiana, anche con
  preferenze che cambiano da pagina a pagina.
  - Somiglia al Voynich per h2 (2,2), lunghezza e varietà delle parole.
  - Non somiglia per:
    - parole uniche: 0,37–0,44 contro 0,68;
    - ripetizioni: ×0,33–0,69 contro ×1,0;
    - omogeneità di pagina: al massimo 2,2%, e piatta;
    - legame fine-inizio: 0,002–0,013 bit contro 0,19, meno di qualsiasi lingua.
- **Abbreviazioni [e21]:** il latino con le abbreviazioni dei manoscritti diventa *meno*
  prevedibile (h2 da 3,26 a 3,37), perché si tolgono proprio le parti più prevedibili. È la
  direzione sbagliata.
- **Lettere nulle [e21]:**
  - sparse a caso allontanano (h2 3,54);
  - messe a regola (in testa e in coda alle parole che cominciano o finiscono per vocale)
    avvicinano h2 (2,94) e lo spazio (53%), ma ripetizioni e somiglianze non cambiano.
- **Trasposizioni [e21]:** a colonne o dentro le parole portano h2 a 3,9 e rendono le parole
  casuali. Ordinare le lettere avvicina h2 (2,5), ma è l'ipotesi degli anagrammi, esclusa
  (4.3).
- **Testi a elenco [e21]** (genealogie e censimenti biblici, Notitia Dignitatum, Fasti di
  Idazio):
  - ripetono la parola precedente meno della prosa (×0,00–0,07);
  - somiglianza nella riga al massimo 1,6%;
  - cifrati con un codice prendono la grana del Voynich (h2 1,9–2,2, spazio 69–75%), ma non le
    sue anomalie.
- **Preghiere e litanie [e25]** (breviario romano: litania dei santi, raccomandazione
  dell'anima, salmi con ritornello, preci, un rosario di 15 decine):
  - nessuna ripete subito la parola (×0,00–0,11) e non ci sono pagine omogenee (0,4–1,1%);
  - hanno invece un fortissimo legame fra parole vicine (0,09–1,37 bit, per "ora pro nobis");
  - cifrate con un codice: h2 1,76, spazio 82%, ma ripetizioni e somiglianze restano quelle
    delle preghiere.

### 4.3 Tentativi di decifrazione, con i controlli

- **Sostituzione omofonica con gli spazi, 14 lingue [e14].** Lingue: latino, italiano,
  tedesco, inglese, francese, spagnolo, ceco, ungherese, greco, ebraico, arabo, turco,
  malgascio, chinanteco.
  - Controlli positivi (altra parte della Bibbia, chiave casuale dello stesso tipo): 69–98% di
    parole vere, 629–5.669 parole diverse.
  - Voynich: al massimo 36% di parole vere e 7–93 parole diverse, per lo più sempre le stesse
    tre. Come un testo in un'altra lingua: 4–86 parole diverse.
  - Le coppie di parole decifrate non sono attestate più delle stesse parole rimescolate.
    L'apparente eccezione tedesca è una chiave degenere (*er er*, *seien sie*): uno scarto così
    compare anche in 4 controlli negativi su 14.
  - Nomi di mesi e segni nello zodiaco: un nome giusto in 3 pagine su 144; nomi fuori posto 22
    volte. Puro caso.
  - Il Plinio cifrato col Naibbe (latino vero, altro meccanismo): 9% di parole vere, 53 parole
    diverse. Anche un testo sensato, cifrato in un modo diverso da quello presupposto, sembra
    vuoto.
- **Un risolutore vero senza spazi [e16, e17].**
  - Il metodo: ricottura simulata, modello della lingua a 5-grammi di lettere (per il latino
    circa 9 milioni di lettere), più un termine sulla varietà delle lettere decifrate, senza il
    quale la ricerca finisce in chiavi degeneri.
  - Controlli: ritrova la chiave al 98–100% nelle Bibbie in 14 lingue (26–74 segni) e al 100%
    su Varrone e Isidoro.
  - Unità contate in quattro modi: segni EVA (26), segni v101 (59), gruppi imparati dal testo a
    due gradi (45 e 74 gruppi).
  - Nei 56 controlli positivi il risolutore ritrova almeno il 99,9% della chiave; uno si ferma
    al 98% (il chinanteco, 30 lettere contro 26 segni).
  - Il Voynich sta fra −0,6 e 0,4 sulla scala negativo→positivo, sotto lo 0 in 30 casi su 56.
    Le parole vere di almeno 6 lettere coprono 0,3–10% del testo decifrato, contro 0,5–9% nei
    negativi e 16–61% nei positivi.
  - Il "testo" decifrato è una poltiglia di sillabe (*lusacarutusunummodetdesacsicaresdetta*).
    Il cifrario verboso di prova diventa invece *…ascendissent venerunt in hierusalem et…*.
  - Il punto più alto (ebraico a segni EVA, 0,42) non regge: viene da una sola ripartenza su
    quattro, e il Naibbe, che non è ebraico, arriva allo stesso punto (0,39 contro 0,37).
- **I gruppi di segni a ogni grado [e20].** Nove gradi, da 10 a 150 fusioni (36–173 gruppi), in
  latino e italiano. Il metodo di fusione ritrova tutti i 35 gruppi veri di un cifrario verboso
  di prova, contro 27 su 35 del più diffuso byte-pair encoding.
  - Controlli positivi: 100% della chiave a ogni grado.
  - Il cifrario verboso di prova si legge fra 30 e 60 fusioni (posizione 0,47–0,74).
  - Il Voynich non si legge a nessun grado: fra −0,33 e 0,00.
- **Tutte le lingue del corpus, anche al contrario [e19].** 71 Bibbie in alfabeto o abjad
  (≤32 lettere): lingue europee, semitiche, turche, uraliche, austronesiane, amerindiane,
  africane, il cinese in pinyin.
  - Controlli positivi: 91–100% della chiave in tutte e 71.
  - Voynich: al massimo 0,47 (shona), sotto 0,3 in 66 lingue su 71; letto al contrario al
    massimo 0,39.
  - Il Naibbe, che ha la "grana" del Voynich senza essere una sostituzione di queste lingue,
    arriva poco sotto (mediana 0,09 in meno). Quel poco che sale è grana, non lingua.
  - Le parole vere di almeno 6 lettere: mediana 1,7% contro 47% di un testo vero cifrato.
- **Anagrammi ordinati [e18]** (Hauer e Kondrak 2016: parole con le lettere in un ordine fisso).
  - L'ordine migliore dei segni è rispettato dal 78,5% delle coppie dentro le parole: valore da
    lingua (60–96%, mediana 66%). Con lettere ordinate sarebbe 100%.
  - Il 35% delle parole ha un anagramma nel testo (27% con v101); nelle lingue 1–27%, mediana
    5%. Con le parole ordinate sarebbe 0%.
  - Gli anagrammi sono spesso varianti rare con un pezzo spostato da un capo all'altro (*chol* →
    *lcho*): la stessa mobilità dei pezzi vista negli spazi.

### 4.4 L'ipotesi senza messaggio: il modello più vicino

- **Una nostra autocitazione semplificata [e08]** (copia e ritocca parole delle righe sopra)
  degenerava in parole troppo corte: né prova né smentita.
- **Due varianti veloci [e21]** producono da sole le due anomalie principali: ripetizioni
  ×1,07 e ×1,29; somiglianza che cala dalla riga (12% o 9%) a sei righe (4% o 6%). Tarare tutto
  insieme però non riusciva.
- **L'algoritmo completo di Timm e Schinner [e22]**, fatto girare così com'è con i parametri
  pubblicati: cinque semi, 4.000 righe, circa 36.700 parole ciascuno. Le regole vengono dal
  Voynich stesso, quindi la somiglianza non è una sorpresa. Conta che un procedimento
  eseguibile a mano, senza contenuto, riproduca proprietà che nessuna lingua e nessun cifrario
  hanno.
  - Uguale: h2 2,23–2,26 (2,24); somiglianza nella riga 3,5–3,9% (3,8%); a sei righe 3,2–3,5%
    (3,4%), che cala.
  - Vicino: ripetizioni ×0,72–0,78; spazio 51–57% (66%); anagrammi 42–46% (35%).
  - Lontano: parole uniche 52% (68%); parole diverse 14% (21%); unioni attestate 1,2 volte il
    caso (Voynich 2 volte).
  - Mancante: il legame fine-inizio, 0,01–0,02 bit (Voynich 0,19), come nel Naibbe.
- **La regola delle giunture [e23], aggiunta qui.** Lo scriba tiene la copia ritoccata con
  una probabilità che dipende da come la sua prima lettera si attacca all'ultima della parola
  precedente, secondo le preferenze del Voynich (dopo *-y* volentieri *q-*, dopo *-n* quasi mai
  *k-*).
  - Senza la regola il testo esce identico, byte per byte, a quello del programma pubblicato.
  - Con la regola (forza 3, cinque semi) il legame fine-inizio è 0,175–0,182 bit (Voynich 0,188;
    senza la regola 0,016).
  - Il resto resta: h2 2,23; ripetizioni ×0,81; somiglianza 3,2% e 3,1%; spazio 58%.
  - Resta il vuoto del vocabolario: parole uniche 51%; tra il 50% e il 54% cambiando uno alla
    volta sette parametri.
- **Più parole nuove costano omogeneità [e24].**
  - Il "doppio ritocco" porta le parole uniche fino al 58%, ma la somiglianza scende da 3,4% a
    2,9%.
  - La "copia da lontano" non alza le parole uniche (51–52%) e fa crollare la somiglianza
    (1,0–2,4%).
  - Combinazione migliore (30% di doppi ritocchi, cinque semi): parole uniche 54%, somiglianza
    3,2%, ripetizioni ×0,77, legame 0,19.
  - Nel generatore più parole nuove vogliono dire pagine meno omogenee; il Voynich ha tutte e
    due le cose.
- **Errori di scrittura o di lettura [e28].**
  - Due trascrizioni a confronto (ZL contro Takahashi, 4.118 righe comuni, 34.815 parole):
    uguali 87,5%; lette diversamente 5,1% (a/o, r/s, k/t, y/o, g/m, ch/sh, *i* ed *e* in più o
    in meno); spazi diversi 7,4%.
  - Le parole uniche sono lette diversamente dal 15,5%, le altre dal 4,1%. Prendendo la lettura
    di Takahashi quando dà una parola già nota (208 casi), le parole uniche scendono solo da
    67,9% a 66,1%. Con la trascrizione di Takahashi il Voynich ne ha comunque il 68%.
  - Errori come quelli osservati, aggiunti al generatore con le giunture: parole uniche dal
    50–51% al 60–61% alla stessa dose, al 64–65% alla dose doppia. Le parole diverse arrivano
    al 20–21%, come nel Voynich; la somiglianza cambia poco (3,0–3,2%).
  - Regolarità delle parole uniche, in bit per segno rispetto alle abitudini delle parole
    ripetute dello stesso testo: Voynich 3,38; generatore 3,06–3,10; generatore con errori
    3,35–3,42. Le parole uniche del Voynich hanno l'aria di errori.
  - Ma con gli errori il testo diventa meno prevedibile: h2 2,37–2,45 (Voynich 2,24), spazio
    50–52% (66%). Senza errori di spazio gli spazi reggono meglio (55–57%), ma le parole uniche
    salgono meno (58–62%) e il legame fine-inizio cala (0,150–0,164).

### 4.5 Decifrazioni pubblicate e cartigli

- **Schechter, glossario EVA → latino [e26]** (4.063 voci, 947 significati; dichiara 87,8%
  decifrato contro 2,1% di stringhe EVA casuali). Il suo programma, rifatto in Python, dà gli
  stessi numeri (89,2% sulla sua trascrizione di 37.886 parole, identico per sezione). Però:
  - un "glossario" fatto delle 4.445 parole più frequenti, senza significato, copre il 90,8%;
    2.067 delle 4.445 parole che il suo glossario legge compaiono una volta sola;
  - il confronto con stringhe casuali non misura niente: parole inventate non stanno nel testo;
  - il suo glossario legge il testo senza messaggio di Timm e Schinner al 67–70%;
  - la sua prova sulle pagine lasciate fuori (79–81%) coincide con la quota di parole di una
    metà che compaiono già nell'altra (82–83%); il testo senza messaggio ne ha di più (85–88%);
  - l'ordine delle parole non è latino. Coppie vicine attestate nella Latin Library (1,37 milioni
    di parole): nel latino vero 30% contro 22% rimescolando (×1,34); nel Voynich decifrato 8,8%
    contro 8,8% (×0,99); nel testo senza messaggio decifrato ×0,94–0,98; con i significati
    rimescolati fra le voci ×1,01;
  - le frasi ripetute e Zipf non sono segni di latino. Frasi di tre parole ripetute: testo senza
    messaggio decifrato 77–112, Voynich decifrato 57. Esponente di Zipf circa −1 per il Voynich
    e per il testo senza messaggio non decifrati.
- **Gatta, corrispondenza EVA → consonanti ebraiche, lettura da destra [e26]** (lui stesso:
  "nessuna pagina si legge", ma un segnale nelle parole di 3–4 lettere). Lessico: forme della
  Bibbia in ebraico del corpus (Nuovo Testamento e parte dell'Antico), senza vocali (46.920).
  - Sul Voynich il segnale c'è: 35,4% contro 12,5% ± 5,2% con 200 corrispondenze a caso
    (z = 4,4).
  - Sul testo senza messaggio: 30% (z = 2,7).
  - Una corrispondenza cercata apposta (salita di 3.000 passi) dà il 53% sul Voynich e il 50–61%
    sul testo senza messaggio: più della sua.
  - Le parole lunghe (5+ consonanti) vanno meglio sul Voynich (3,1% contro 1,4–1,6%), ma il 69%
    viene da due parole sole (*okaiin*, *okain*).
- **Altre letture** (Cheshire 2019, "proto-romanzo"; Ardıç, turco antico): non provate, perché
  non abbiamo trovato un programma o un glossario pubblico che le applichi a tutto il testo.
- **I nomi delle piante come cartigli [e27].** Idea: il nome della pianta disegnata sta nella
  prima parola o nella prima riga della pagina, come in molti erbari (Champollion con i
  cartigli).
  - Identificazioni: l'unico elenco raggiungibile da qui, la tabella del toolkit di Gatta (58
    fogli, 15 con confidenza alta, gli altri "moderata", alcuni poco credibili); nomi latini
    aggiunti da noi. Le fonti originali erano bloccate dalla rete dell'ambiente.
  - Metodo: un modello di allineamento (IBM Model 1, come nella traduzione automatica) impara
    quali segni "producono" quali lettere, su tutte le pagine insieme. Si confronta con 1.000
    abbinamenti rimescolati fra i fogli.
  - Controllo positivo: il nome cifrato con un cifrario verboso casuale al posto della prima
    parola si ritrova sempre (p = 0,001), anche con un segno su cinque sbagliato su tutti i
    fogli. Nella prima riga intera la prova è più debole: sui 15 fogli migliori ritrova il nome
    solo in latino e senza errori.
  - Voynich: niente, né in italiano né in latino, né nella prima parola né nella prima riga.
    Il migliore p = 0,053 su otto prove, compatibile col caso.

### 4.6 La lista di controllo (tabella da riportare)

Valori per il testo in paragrafi della ZL, segni composti fusi. Testi naturali: la Bibbia in
circa 90 lingue in alfabeto o abjad, più otto testi tecnici latini. Legenda: ✓ uguale,
≈ vicino, ✗ lontano. "TS" = Timm e Schinner.

| proprietà | Voynich | testi naturali | Naibbe | TS | TS + giunture |
|---|---|---|---|---|---|
| incertezza sul segno successivo (h2) | 2,22 bit | 2,6–3,3 a parità di alfabeto | 2,2 ✓ | 2,24 ✓ | 2,23 ✓ |
| spazio prevedibile dal segno precedente | 66% | 6–100%, mediana 17% | 64% ✓ | 54% ≈ | 58% ≈ |
| parole diverse ogni 30.000 | 21% | 3–33% | 17–18% ✓ | 14% ≈ | 14% ≈ |
| parole usate una volta sola (hapax) | 68% | 12–72% | 37–44% ✗ | 52% ✗ | 51% ✗ |
| parola identica alla precedente, rispetto alla riga | ×1,0 | ×0,01–1,9, mediana ×0,12 | ×0,33–0,69 ✗ | ×0,76 ≈ | ×0,81 ≈ |
| somiglianza fra parole della stessa riga | 3,8% | da −0,4% a 1,5% | 0–2,2% ✗ | 3,8% ✓ | 3,2% ≈ |
| la stessa somiglianza a 6 righe | 3,4% (cala) | vicino a 0 | piatta ✗ | 3,4% (cala) ✓ | 3,1% (cala) ✓ |
| legame fine parola → inizio parola seguente | 0,19 bit | 0,02–0,40, mediana 0,07 | 0,002–0,013 ✗ | 0,016 ✗ | 0,178 ✓ |
| due parole vicine unite danno una parola esistente | 9,2% (caso 4,8%) | 0,1–0,7%, pari al caso | 1,0% (caso 1,3%) ✗ | 13,9% (caso 11,7%) ≈ | 11,8% (caso 9,2%) ≈ |

Aggiunte (e28), sempre sul generatore con le giunture: con errori di lettura alla dose
doppia le parole uniche arrivano al 64–65% e le parole diverse al 20–21%, ma h2 sale a
2,37–2,45 e lo spazio scende al 50–52%.

## 5. Che cosa si può concludere

- **Escluso, con controlli che mostrano che il metodo funziona:**
  - una sostituzione semplice o omofonica di una delle 14 lingue provate con gli spazi, o
    delle 71 provate senza spazi, contando i segni in molti modi, anche leggendo al contrario;
  - un cifrario verboso a gruppi imparati dal testo, a nove gradi fra 36 e 173 gruppi, in
    latino e italiano;
  - un codice parola per parola di un testo in prosa;
  - anagrammi ordinati;
  - il Naibbe come spiegazione completa;
  - abbreviazioni, nulle o trasposizioni come spiegazione principale;
  - elenchi, preghiere e litanie come spiegazione delle anomalie;
  - il nome della pianta scritto lettera per lettera, in italiano o latino, nella prima parola
    delle pagine con le identificazioni disponibili.
- **Non regge ai controlli:** le due decifrazioni pubblicate con codice pubblico (Schechter,
  Gatta).
- **Regge a metà l'idea "tokenizzata".**
  - Regge che i segni non si comportino come lettere: si combinano come pezzi di un sistema, e
    contati a gruppi più grandi il testo si avvicina alle lingue.
  - Non regge che ogni parola stia al posto di una parola di un testo in prosa: tutte le
    codifiche di questo tipo conservano il modo in cui una lingua mette in fila le parole, e il
    Voynich non le mette in fila così.
- **Tre possibilità aperte, non ancora distinte:**
  1. un contenuto che non è prosa (elenchi, tabelle, cataloghi, formule), scritto con unità più
     grandi delle lettere;
  2. una scrittura con convenzioni che cambiano da pagina a pagina, con spazi che non separano
     parole del testo in chiaro;
  3. nessun messaggio: un testo prodotto da una procedura (copiare e variare quanto appena
     scritto).
- **La terza è la più avanti**, perché è l'unica che produce da sola ripetizioni immediate e
  omogeneità di pagina graduata. Con la regola delle giunture ottiene anche il legame
  fine-inizio; manca la varietà del vocabolario, forse in parte spiegabile con errori di
  scrittura o di lettura.
- **Formulazione prudente:** questo non dimostra che il Voynich sia senza messaggio. Dimostra
  che un procedimento eseguibile a mano, senza contenuto, riproduce quasi tutte le sue
  proprietà statistiche, mentre nessuna lingua, nessun cifrario e nessuna decifrazione provata
  lo fa.
- **Letteratura recente convergente:** *A Glyph Is Not a Letter, a Token Is Not a Word, a Space
  Is Not a Space* (arXiv 2608.17096, agosto 2026; letto solo il riassunto) arriva per altra via
  a conclusioni vicine:
  - i segni non si comportano come lettere, le stringhe fra gli spazi non come parole, gli spazi
    non come separatori;
  - l'ordine sta ai bordi delle stringhe e nei confini "graduati";
  - la regolarità dei segni è troppo forte per una sostituzione uno a uno.

## 6. Contributi originali di questo lavoro

Utili da mettere in evidenza nel white paper:

1. **Due anomalie quantificate:** la ripetizione immediata "come a caso" (×1,0 contro ×0,12
   delle lingue) e l'omogeneità di pagina graduata (3,8% che cala a 3,4% a sei righe), su circa
   100 lingue e con testi tecnici latini come controllo di genere.
2. **Una lista di controllo** di nove proprietà, con i valori di riferimento, da usare contro
   qualsiasi proposta.
3. **Un risolutore a ricottura simulata** tarato su 56 + 71 controlli positivi, e il suo esito
   sul Voynich in 71 lingue e con 4 modi di contare i segni (più 9 gradi di gruppi).
4. **La regola delle giunture** aggiunta al generatore di Timm e Schinner, che porta il legame
   fine-inizio da 0,016 a 0,178 bit (Voynich 0,188) senza guastare il resto.
5. **Il controllo "testo senza messaggio"** applicato a decifrazioni pubblicate: un test
   semplice che chiunque annunci una lettura dovrebbe superare.
6. **La prova dei cartigli**, pronta per un elenco affidabile di identificazioni.
7. **Il legame fra parole uniche e letture incerte**: quanto contano, quanto sono irregolari, che
   cosa succede aggiungendo errori al generatore.

## 7. Limiti e cautele

- **Le immagini non ci sono.** Le scansioni della Beinecke non erano raggiungibili; tutto quello
  che dipende dai disegni è fuori, tranne la prova dei cartigli con identificazioni di seconda
  mano.
- **Trascrizioni:** tutto su ZL; IT e GC come controllo. Le trascrizioni divergono sul 12,5%
  delle parole, ma le misure principali restano uguali con Takahashi.
- **Un esito negativo vale solo per il modello provato:** ogni unità vale una lettera, più unità
  la stessa lettera; lingue del corpus. Non copre:
  - unità che valgono zero o più lettere (nulle, sillabe, abbreviazioni) in un vero
    risolutore;
  - codici e trasposizioni complesse;
  - lingue fuori dal corpus.
- **Modelli delle lingue dalla Bibbia**, un genere solo. Per il latino i controlli su Varrone e
  Isidoro mostrano che basta; per le altre lingue non si può verificare.
- **Le identificazioni delle piante** (e27) non sono verificabili alla fonte, e quelle
  "moderate" sono deboli. Sulla prima riga intera la prova ha poca forza con 15 fogli.
- **La decifrazione di Gatta** è misurata con un lessico nostro (la Bibbia in ebraico, senza
  vocali), non con il suo.
- **Il generatore di Timm e Schinner** usa regole tratte dal Voynich: la somiglianza è in parte
  costruita. Il punto è che basta una procedura semplice, non che il generatore "spieghi" il
  Voynich.
- **Siti non raggiungibili dall'ambiente di lavoro:** voynich.nu, Beinecke e Yale, arXiv (testo
  intero), HerbalGram, Kaggle, i blog di botanica voynichiana, stephenbax.net, pure.mpg.de.
- **Un'etichetta sbagliata nel corpus:** l'islandese è segnato come scritto in etiopico; resta
  fuori dai confronti fra alfabeti.

## 8. Cosa resta da fare

1. **Un generatore più regolare in partenza** (segni e spazi più prevedibili), a cui aggiungere
   errori di scrittura o di lettura: è la strada più promettente per chiudere il divario del
   vocabolario.
2. **Testi "a elenco" veri come confronto:** ricettari a lista, cataloghi di stelle, glossari,
   tavole. Se evitano le ripetizioni e non hanno pagine omogenee, la possibilità 1 si
   indebolisce ancora.
3. **Un risolutore in cui un'unità vale zero, una o più lettere** (nulle, sillabe,
   abbreviazioni). I sondaggi dicono che da sole queste strade aiutano poco, ma non è escluso.
4. **Cifrari con "stile di pagina" graduale e giunture morbide**, per esempio varianti del
   Naibbe: sono le due cose che il Naibbe non ha.
5. **Immagini e identificazioni affidabili delle piante:** rifare la prova dei cartigli (pochi
   minuti) e aggiungere le etichette accanto ai disegni.
6. **Leggere per intero lo studio arXiv 2608.17096** e confrontarlo numero per numero.
7. **Studiare a parte la prima e l'ultima parola di ogni riga**, che hanno statistiche proprie.
8. **Mettere alla prova altre decifrazioni annunciate**, appena ne esistono un programma o un
   glossario pubblico: col controllo del testo senza messaggio e con l'ordine delle parole.

## 9. Figure pronte (in `voynich/risultati/`, versione chiara e scura)

| file | che cosa mostra | dove usarla |
|---|---|---|
| `e01_prevedibilita-chiaro.png` | h1 contro h2: il Voynich sotto tutte le ~100 lingue | impronta statistica |
| `e05_righe-chiaro.png` | somiglianza fra parole in funzione della distanza fra righe | omogeneità di pagina |
| `e07_compromesso_verboso-chiaro.png` | 450 cifrari verbosi: prevedibilità contro lunghezza delle parole | cifrari verbosi |
| `e09_sintesi-chiaro.png` | ripetizioni immediate contro somiglianza nella riga: il Voynich da solo | le due anomalie |
| `e13_profilo-chiaro.png` | le lingue su due assi riassuntivi, il Voynich fuori dalla nuvola | isolamento |
| `e14_decifrazione-chiaro.png` | parole vere diverse: controlli positivi, negativi, Voynich | sostituzione con spazi |
| `e17_ricottura-chiaro.png` | posizione del Voynich fra negativo (0) e positivo (1), 14 lingue × 4 modi | risolutore senza spazi |
| `e18_anagrammi-chiaro.png` | ordine dei segni contro anagrammi: lingue, parole ordinate, Voynich | anagrammi |
| `e19_tutte_le_lingue-chiaro.png` | 71 lingue, Voynich dritto e al contrario, Naibbe | tutte le lingue |
| `e20_gradi-chiaro.png` | posizione al variare delle fusioni: il verboso di prova sale, il Voynich no | gruppi di segni |
| `e22_timm_schinner-chiaro.png` | otto proprietà su scala lingua (0) → Voynich (1): generatore e Naibbe | modello senza messaggio |
| `e23_giunture-chiaro.png` | lo stesso con la regola delle giunture | giunture |
| `e24_varieta-chiaro.png` | parole uniche contro somiglianza: il compromesso del generatore | vocabolario |

Per e25–e28 ci sono solo tabelle (`.md`): conviene farne grafici nuovi. Per esempio:

- barre del rapporto "coppie attestate / rimescolate" per latino vero, Voynich decifrato,
  testo senza messaggio e glossario rimescolato (e26);
- parole uniche e h2 contro la dose di errori (e28).

## 10. Scaletta proposta per il white paper

1. **Sommario** (10–12 righe, dalla sezione 1).
2. **Introduzione:** il manoscritto, le ipotesi in campo, perché serve un metodo con controlli.
3. **Dati e metodo:** trascrizioni, corpora, controlli positivi e negativi, scala normalizzata,
   lista di controllo, riproducibilità.
4. **L'impronta del Voynich:** prevedibilità, spazi e giunture, ripetizioni, omogeneità di
   pagina, isolamento dalle lingue (4.1). Figure e01, e05, e09, e13.
5. **Che cosa il Voynich non è:** codifiche di testi veri, Naibbe, sostituzioni con e senza
   spazi, gruppi di segni, 71 lingue, anagrammi (4.2, 4.3). Figure e07, e14, e17, e19, e20, e18.
6. **Le decifrazioni pubblicate alla prova:** Schechter e Gatta, il controllo del testo senza
   messaggio; i cartigli (4.5).
7. **Il modello senza messaggio:** Timm e Schinner, la regola delle giunture, il vocabolario,
   gli errori di lettura (4.4). Figure e22, e23, e24.
8. **Discussione:** la lista di controllo come criterio (4.6), le tre possibilità, che cosa
   servirebbe per distinguerle (5, 8).
9. **Limiti** (7).
10. **Riproducibilità e disponibilità:** repository, comandi, tempi di calcolo (sezione 12).
11. **Appendici:** tabella dei 28 esperimenti (sezione 13), glossario (sezione 11), fonti
    (sezione 14).

## 11. Glossario (italiano / inglese)

- **EVA**: alfabeto convenzionale per trascrivere il Voynich in lettere latine; non indica
  suoni.
- **segno, glifo** (glyph): un carattere del manoscritto; *ch*, *sh*, *cth*… contano come uno.
- **h1, h2** (unigram / conditional entropy): incertezza in bit su un segno preso da solo (h1) e
  sul segno successivo sapendo il precedente (h2). Più bassa = più prevedibile.
- **hapax** (hapax legomenon): parola che compare una volta sola.
- **lingue A e B di Currier** (Currier languages): due varietà di scrittura in cui si dividono le
  pagine (Prescott Currier, anni '70).
- **cifrario omofonico** (homophonic cipher): ogni lettera si può scrivere con più segni.
- **cifrario verboso** (verbose cipher): ogni lettera si scrive con un gruppo di più segni.
- **ricottura simulata** (simulated annealing): ricerca che cambia la chiave un pezzo alla volta
  e accetta ogni tanto un peggioramento, sempre più di rado.
- **modello a 5-grammi** (5-gram model): probabilità di ogni lettera date le quattro precedenti.
- **controllo positivo / negativo** (positive / negative control): testo in cui c'è / non c'è
  la risposta; dice se il metodo funziona e quanto si ottiene per caso.
- **p**: probabilità di ottenere per caso un risultato almeno così forte.
- **z**: di quante deviazioni standard un valore si stacca dalla media dei casi rimescolati.
- **autocitazione** (self-citation): procedura in cui chi scrive copia e ritocca parole già
  scritte (Timm e Schinner).
- **legame fine-inizio** (cross-boundary mutual information): quanta informazione la fine di una
  parola dà sull'inizio della successiva, in bit, oltre il caso.
- **somiglianza di pagina** (page homogeneity): quanto due parole diverse della stessa riga o
  pagina si somigliano nella grafia, oltre il caso (distanza di edit normalizzata).
- **Naibbe**: cifrario quattrocentesco eseguibile a mano proposto da Greshko (2025).
- **cartiglio** (cartouche / crib): parola nota (qui il nome di una pianta) usata come appiglio
  per la decifrazione.
- **IBM Model 1**: modello statistico di allineamento fra due sequenze, nato per la traduzione
  automatica.

## 12. Riproducibilità

```sh
pip install -r voynich/requirements.txt        # numpy, matplotlib, scikit-learn, rapidfuzz, pypinyin
python3 voynich/prepara.py                     # scarica i testi di confronto a commit fisso
python3 voynich/esperimenti/e01_prevedibilita.py
# ... e cosi' via fino a e28
python3 voynich/esperimenti/e14_decifrazione.py --naibbe
```

- **Tempi:** gli esperimenti 17, 19 e 20 richiedono ore con quattro processori (variabile
  `PROCESSI`); gli altri da pochi secondi a qualche decina di minuti.
- **Java:** serve agli esperimenti 22, 23, 24, 26 e 28 (generatore di Timm e Schinner). Dal 23
  in poi il generatore si ricompila dal sorgente con le aggiunte in `analisi/timm_schinner/`
  (`Giunture.java`, `Varieta.java`).
- **Tabelle e grafici:** con `--tabella` e `--grafico` si rifanno dai risultati salvati.
- **Riproducibilità esatta:** semi fissi, quindi numeri identici rifacendo.
- **Fonti:** versioni e impronte in `voynich/dati/FONTI.md`.
- **Codice:**
  - `analisi/` (moduli comuni):
    - `trascrizione.py`: lettura IVTFF;
    - `misure.py`: misure della lista di controllo;
    - `lingue.py`: corpora;
    - `ricottura.py`: risolutore;
    - `generatori.py`: codici e generatori;
    - `decifra.py`, `grafici.py`;
  - `esperimenti/` (e01–e28): uno per esperimento.

## 13. I 28 esperimenti

| # | domanda | risultato |
|---|---|---|
| 1 | La lettera successiva è troppo prevedibile? | Sì a parità di alfabeto; con i segni v101 e senza spazi arriva al margine delle lingue |
| 2 | Come si comportano le parole, rispetto a ~100 lingue? | Vocabolario nella norma; ripetizioni e somiglianze fuori norma |
| 3 | Il genere del testo spiega la "poca sintassi"? | Sì: i testi tecnici latini ne hanno altrettanto poca |
| 4 | Le parole adiacenti si copiano? | No: è la riga (e la pagina) a essere omogenea |
| 5 | Quanto dura la somiglianza fra righe? | Tutta la pagina, un po' di più fra righe vicine |
| 6 | Gli strumenti ritrovano le lingue A e B di Currier? | Sì, 98,5% delle pagine |
| 7 | Un testo vero codificato somiglia al Voynich? | No, con nessuna delle codifiche provate |
| 8 | Un testo che si copia da solo somiglia al Voynich? | La nostra versione semplificata non ci riesce |
| 9 | Le due anomalie in un grafico | Il Voynich sta da solo |
| 10 | Il cifrario Naibbe riproduce il Voynich? | Lettere sì; ripetizioni, pagine, hapax e giunture no |
| 11 | Gli spazi separano parole? | Lo spazio è per due terzi una regola; legame fra parole vicine da lingua con particelle |
| 12 | Quali spazi sono veri? | Giunture morbide e dure; molti spazi incerti non c'erano |
| 13 | A quali lingue somiglia, tutto considerato? | A nessuna: più isolato di qualsiasi lingua |
| 14 | Una sostituzione omofonica lo legge, in 14 lingue? | No; i controlli positivi invece si leggono |
| 15 | Le etichette dello zodiaco sono numeri? | No |
| 16 | E ignorando gli spazi? | Non si sa: il primo metodo non rompeva il controllo positivo (rifatto nel 17) |
| 17 | Senza spazi, risolutore vero, 14 lingue, 4 modi di contare i segni? | Nessuna lettura; i controlli, anche un cifrario verboso, si leggono |
| 18 | Le parole sono anagrammi ordinati? | No: ordine da lingua, più anagrammi di quasi tutte le lingue |
| 19 | In tutte le 71 lingue del corpus, anche al contrario? | No: mai oltre 0,47; il Naibbe arriva poco sotto |
| 20 | Con i gruppi di segni a ogni grado? | No, a nessuno dei nove gradi; il verboso di prova sì, fra 30 e 60 fusioni |
| 21 | Sondaggi: abbreviazioni, nulle, trasposizioni, elenchi, autocitazione | Solo l'autocitazione produce ripetizioni e somiglianza di pagina |
| 22 | L'algoritmo completo di Timm e Schinner? | In gran parte sì; manca il legame fra parole vicine |
| 23 | Con una regola sulle giunture? | Il legame compare (0,178 contro 0,188) senza guastare il resto; vocabolario meno vario |
| 24 | Doppio ritocco o copia da lontano? | Fino al 58% di parole uniche, ma a spese della somiglianza di pagina |
| 25 | Preghiere e litanie? | No: niente ripetizioni immediate né pagine omogenee; forte legame fra parole |
| 26 | Due decifrazioni pubblicate (Schechter, Gatta)? | No: leggono allo stesso modo un testo senza messaggio; ordine delle parole casuale |
| 27 | Il nome della pianta nella prima parola o riga? | Nessuna traccia; il nome cifrato apposta invece si ritrova |
| 28 | Le parole uniche vengono da errori di lettura? | In parte possono: ne hanno l'aria, ma gli errori rendono il testo meno prevedibile del Voynich |

## 14. Fonti e riferimenti

**Dati e software usati**

- Trascrizioni IVTFF di René Zandbergen (ZL, IT, GC), da
  [Krymorn/The-Voynich-Transliteration-Tool](https://github.com/Krymorn/The-Voynich-Transliteration-Tool)
  (commit `cb2d368`); sito originale <https://www.voynich.nu/transcr.html>.
- La Bibbia in 100 lingue:
  [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus) (commit `44e5fca`).
- The Latin Library:
  [cltk/lat_text_latin_library](https://github.com/cltk/lat_text_latin_library) (commit `76229ac`).
- Il cifrario Naibbe:
  [greshko/naibbe-cipher](https://github.com/greshko/naibbe-cipher) (commit `f2675ec`).
- Il generatore di Timm e Schinner:
  [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator)
  (commit `a6ede22`).
- Il breviario romano:
  [DivinumOfficium/divinum-officium](https://github.com/DivinumOfficium/divinum-officium)
  (commit `2dbc3c2`).
- La decifrazione di Schechter:
  [scott-schechter/voynich-decoded](https://github.com/scott-schechter/voynich-decoded)
  (commit `71f2f3c`, 25/03/2026).
- Il toolkit di Gatta:
  [antenore/voynich-toolkit](https://github.com/antenore/voynich-toolkit) (commit `cb13763`).

**Letteratura**

- T. Timm e A. Schinner (2020), *A possible generating algorithm of the Voynich manuscript*,
  Cryptologia 44(1), [doi:10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999).
- M. A. Greshko (2025), *The Naibbe cipher: a substitution cipher that encrypts Latin and Italian
  as Voynich Manuscript-like ciphertext*, Cryptologia,
  [doi:10.1080/01611194.2025.2566408](https://doi.org/10.1080/01611194.2025.2566408).
- B. Hauer e G. Kondrak (2016), sull'ipotesi degli anagrammi (citata; non riletta qui).
- P. Currier (anni '70), le lingue A e B (citato; non riletto qui).
- *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space* (agosto 2026),
  [arXiv:2608.17096](https://arxiv.org/abs/2608.17096) (letto solo il riassunto).
- A. Gatta (2026), articolo del voynich-toolkit su Zenodo,
  [doi:10.5281/zenodo.19226178](https://doi.org/10.5281/zenodo.19226178).
- Letture non provate: G. Cheshire (2019), lingua "proto-romanza"
  ([un resoconto](https://voynichportal.com/2019/05/16/cheshire-reprised/)); A. Ardıç, turco
  antico ([turkicresearch.com](https://www.turkicresearch.com/files/articles/17.pdf)).

Nota per chi scrive: le voci segnate "citata" o "letto solo il riassunto" vanno verificate
sui testi originali prima della pubblicazione.

## 15. Aggiornamento del 3/10/2026 (e212b–e293): proprietà nuove, decifrazioni escluse, generatore e voynichizzatore

Sintesi delle voci del QUADERNO di quel giorno. Tutti gli esperimenti sono preregistrati, con controlli positivi e
negativi; i numeri sono nei file di `risultati/`.

### 15.1 Proprietà del Voynich trovate o confermate

- **Le parole vicine si legano per i bordi, non per il centro** (e285, e285b, e285c). Fra parole vicine nella stessa
  riga, anche escludendo le coppie che sono varianti l'una dell'altra:
  - il finale dipende dal finale della precedente (eccesso di informazione mutua 0,041; generatore 0,007–0,017);
  - il prefisso dal prefisso precedente (0,031; generatore circa 0,010);
  - il finale dal prefisso seguente (0,112; generatore 0,055–0,070);
  - il centro quasi per niente (0,007; il generatore copia i centri, 0,041–0,053).
  - La dipendenza fra finali è fatta di **passaggi fra varianti della stessa desinenza** (*shedy → edy*, *chedy →
    edy*, *edy → chedy*) e di prefissi staccati (*o*, *s*, *l* seguiti da una parola), non di ripetizioni: una
    "concordanza delle desinenze". Non ha l'aspetto delle coppie di lettere di un messaggio.
- **Le prime righe dei paragrafi sono un registro a parte** (e273, confermato): somigliano alle prime righe degli altri
  paragrafi della sezione più che al resto del loro paragrafo (z 4,7), con più *p* e *f* e parole più lunghe (4,63
  segni contro 4,34 del generatore).
- **Le pagine sono varie e omogenee insieme:** tipi su parole nella pagina 0,756, parole uniche nella pagina 0,636, e
  insieme somiglianza alta fra parole della stessa riga. Un generatore "copia e modifica" ottiene l'una o l'altra cosa,
  non tutte e due (e251b, prova cumulativa del ciclo avversario).
- **Le coppie di parole ricompaiono altrove** più che nei generatori: 22,1% delle coppie di parole vicine contro 18%.
- **Inizio riga:** le righe iniziano con *t* nel 10,5% dei casi e con *k* nel 3,2% (il generatore senza questa
  informazione faceva 6,7% e 6,3%).
- **Le scelte di grafia hanno memoria di riga** (modello delle scelte della v1, 56.850 posti): per le cinque scelte
  (ch/sh, k/t, -l/-r, qo-/o-, -dy/-ey) la probabilità della forma lunga cresce con le forme lunghe già scritte nella
  riga e nella riga sopra (coefficienti 0,5–1,4), come già indicavano e135, e146.
- **Capacità delle scelte di grafia come canale:** circa 0,8 bit per posto, cioè circa 46.000 bit per un libro come il
  Voynich (circa 2.000 parole latine compresse): misurata costruendo davvero il canale (voynichizzatore v1).

### 15.2 Decifrazioni escluse (tutte con i controlli)

- **Ricerca guidata dal contenuto in cinque volgari** (e223) e verifica del candidato tedesco (e223b): artefatto; lo z
  del Voynich passa da +4,2 a −4,8 cambiando solo le ripartenze.
- **Tutte le lingue della cache, 85 più le 14 dell'e212** (e212b) e verifica dei tre candidati (e212c): artefatti della
  formula della posizione (positivo che non si decifra; negativo della stessa lingua).
- **Nomenclatore misto** (e222), **16 volgari, lingue storiche e latino abbreviato** (e219), **altri ordini di lettura**
  (e216), **pezzi delle parole come simboli** (e249), **solo le parole non copiate** (e269): nessuna lettura.
- **Canale di Bacone nelle 12 scelte di riga** (e279, e279b, e279c): artefatto delle parole ripetute (z 7,1 contro 4,5
  di un generatore senza messaggio).
- **Etichette come vocabolario:** i quattro anelli a 12 settori non nominano le stesse cose (e280, z 1,2; positivo 14,8).
- **Ruote combinatorie alla Lullo negli anelli** (e286): no, oltre la copia.
- **Lezioni di metodo:** (1) la "posizione fra negativo e positivo" va giudicata solo se il positivo si decifra e
  supera il negativo; (2) nelle prove guidate dal contenuto lo z dipende dalla chiave trovata: serve una distribuzione
  di controlli negativi; (3) un nullo bit per bit gonfia lo z quando le parole si ripetono: serve il nullo a parole
  intere; (4) scegliere fra molte configurazioni su un solo seme produce l'"effetto vincitore".

### 15.3 Il generatore senza messaggio

- **e288: 18/18 su due semi di verifica su tre** (17/18 sul terzo), con tre correzioni guidate dai valori grezzi:
  penalità per le ripetizioni immediate, copia dalla parola alla stessa posizione nella riga sopra, meno spezzature.
  AUC del discriminatore e231 0,833, dell'e266 0,933 (e241: 0,873 e 0,961).
- Non hanno funzionato da soli: lessico di sezione (e251), riuso senza tema e senza reimmissione (e251b), dodici
  interruttori di riga (e252), parametri per sezione (e276), registro delle prime righe (e268, e268b: abbassa il
  discriminatore ma costa pagella), ricerca casuale sui parametri vecchi (e283).

### 15.4 Il voynichizzatore (testo vero → manoscritto con il testo nascosto)

- v0 → v3: il testo (compresso e cifrato con una chiave) si nasconde nelle scelte di grafia; con la chiave torna esatto.
- Con la codifica aritmetica secondo un modello delle scelte imparato dal Voynich (v1 e seguenti), **il testo nascosto
  non rende il manoscritto più riconoscibile** di uno senza messaggio.
- v3 con Isidoro XVII nascosto: AUC 0,812 (e231) e 0,928 (e266); obiettivo 0,6. Banco di prova fisso: e293.

### 15.5 Proprietà trovate nel pomeriggio del 3/10 (e294–e301)

- **Le parole rare sono sparse come errori** (e296, ipotesi di Davide). Due terzi delle parole rare (2–5 occorrenze)
  sono a una lettera da una parola frequente, e compaiono in pagine qualsiasi: R 0,57 (sotto il caso). Anche le rare che
  non sono varianti sono sparse (R 1,16): nel Voynich nessuna parola rara è "della pagina". Nei generatori R 32–87:
  le varianti nascono nella pagina e restano lì. Aggiungere errori sparsi al generatore non basta (e297: R da 52 a 50),
  perché il difetto sta nelle rare che il generatore crea dentro la pagina.
- **La concordanza delle desinenze ha la forma di una lingua, non la forza** (e294). Bordi legati più dei centri
  (indice +0,031), come in 14 testi naturali (giapponese, coreano, nahuatl, lingue amazzoniche, latino tecnico a
  elenchi); ma con eccessi 3–10 volte più piccoli di qualsiasi lingua.
- **La concordanza si ferma all'a capo** (e295): dentro la riga 0,050, attraverso l'a capo 0,007 (z 0,7); nel latino
  continua (r 0,68). È un'abitudine di riga dello scriba, come le scelte di grafia, non grammatica.
- **Famiglie di parole nella pagina** (e298): struttura uguale a quella del generatore; la varietà del Voynich non viene
  da famiglie diverse. **Fine riga** (e299): le righe che finiscono in *m*/*g* sono appena più lunghe (+1,5%, z 2,0):
  indizio debole.
- **L'ordine delle pagine conserva l'ordine di scrittura** (e300, e300b). Pagine consecutive nella rilegatura
  condividono più parole di frequenza media di pagine qualsiasi della stessa sezione (z 8,5), e l'effetto resta dentro
  la stessa sezione e la stessa lingua di Currier (z 5,7). Coerente con uno scriba che riprende parole delle pagine
  appena scritte e con una rilegatura in buona parte fedele (o con un ordine per argomento).
- **Mani 2 e 3 di Davis** (e301): distinguibili per sei abitudini fini (z 3,4), ma hanno scritto sezioni diverse e
  dentro l'erbario non si distinguono (z 1,1): più probabilmente differenze di sezione che di mano.

### 15.6 Proprietà trovate la sera del 3/10 (e302–e306) e il modello del Voynich

- **Le prime righe dei paragrafi sono un registro a parte** (e302): parole più lunghe di 0,42 segni (z 14,7), più *sh*
  e meno *ch* all'inizio, più *p*, *f*, *t*, più finali in -*y*, meno in -*n* (cioè meno -*aiin*).
- **La riga non è un'unità di copia** (e303): le parole della stessa riga si somigliano un po' **meno** di quelle della
  riga sotto (0,965 rispetto alla distanza 1); la somiglianza cala lentamente fino a 8 righe e risale a 12–16.
- **Errori ricorrenti vicini** (e304): le varianti rare di parole frequenti tornano in media tre volte, su pagine più
  vicine del caso (z −5,4): la grafia dello scriba cambia nel tempo.
- **Coppie identiche di parole lunghe** (e305): 0,94% delle coppie vicine, soprattutto *chol chol*, *qokeedy qokeedy*.
- **Che cosa predice una parola** (modello del Voynich, pesi per massima verosimiglianza senza la pagina in esame): la
  sezione e il **segno finale della parola precedente**, non la coppia esatta; la prima parola dei paragrafi è una
  parola nuova quasi una volta su due. (Il peso quasi nullo della riga sopra in quel prototipo **non** va letto come
  "niente copia verticale": la misura diretta dell'e338 trova parole simili nelle righe subito sopra e nella stessa
  colonna più del caso, §15.10.)
- **Ogni pagina ha un'identità forte, lungo un solo asse** (e307). Il profilo dei segni di una pagina si allontana da
  quello della sua sezione e lingua 2,8 volte più del caso (z 70); nella Bibbia, a pagine di argomento diverso, 1,75.
  - L'identità è soprattutto la posizione della pagina fra due estremi, parole in -*edy*/-*eey* contro parole in
    -*aiin*/-*ain*. Varia **dentro** ogni lingua e ogni sezione. Non è l'asse che separa le lingue A e B: quelle
    differiscono nel lessico (e315, §15.8).
  - La pagina condivide l'identità con le pagine dello stesso foglio e dello stesso bifoglio (e308, §15.7), non con
    quelle a 2–5 pagine di distanza.


### 15.7 Il libro fisico e la struttura del paragrafo (e308–e313)

- **L'unità di scrittura è il bifoglio** (e308). L'identità di pagina dell'e307 è condivisa dalle due facce dello
  stesso foglio (correlazione 0,285, z 11,5) e dal foglio coniugato dello stesso bifoglio (0,20, z 8), che
  nell'ordine di lettura sta lontano. Non è condivisa dalla pagina affiancata nell'apertura (0,048, z 2,4) né dagli
  altri fogli del fascicolo. Lo scriba sembra aver scritto un bifoglio alla volta, ognuno in un suo "stato"; per
  somiglianza non si ricostruisce l'ordine del libro (e312).
- **L'asse -edy/-aiin è un continuo** (e309): una sola componente; le lingue A e B si sovrappongono molto su questo
  asse.
- **Il paragrafo comincia con un gallows** (e310): l'83% delle prime parole dei paragrafi inizia con *k*, *t*, *p*,
  *f* o un gallows composto (altrove 9%); metà sono un gallows davanti a una parola comune; due terzi di quelle uniche
  restano forme nuove anche senza il gallows.
- **L'ultima riga del paragrafo ha un registro suo** (e313): meno parole in *qo*- e meno gallows, più *ch*-, *s*-,
  *y*-. È il contrario della prima riga.
- **Le righe non sono regolate sul margine** (e313): sono più irregolari di un testo a capo a larghezza fissa,
  coerente con larghezze variabili intorno ai disegni.
- **Le etichette non ricompaiono nel testo della propria pagina** più che in altre pagine della sezione (e311,
  incerto).

### 15.8 Fascicoli, bifogli, lingue A e B, inizio del paragrafo (e314–e318)

- **Due livelli di "stato"** (e314, e308). La posizione di una pagina sull'asse -edy/-aiin dipende soprattutto dal
  **fascicolo** (η² 0,45, z 8,5). Il resto del profilo è condiviso dal **bifoglio** (le pagine dello stesso bifoglio
  si somigliano, quelle dello stesso fascicolo no). La mano spiega poco (η² 0,14).
- **Le lingue A e B differiscono nel lessico, non sull'asse** (e315). Nell'erbario A e B si separano quasi
  perfettamente (AUC 0,997), anche senza l'asse e senza le parole in -*y*/-*n*:
  - B usa *chedy*, *shedy*, *okedy*, *qokar*, *ar* e parole in *a*-;
  - A ha più *o* e più gallows composti all'inizio delle parole;
  - il punteggio dell'asse da solo non le separa.
- **Il paragrafo comincia con *p*** (e316). Fra i gallows d'inizio paragrafo *p* è il 54% (nel resto del testo
  prevale *k*). Il gallows d'inizio è legato alla parola tre volte meno del solito: è in buona parte un segno della
  posizione.
- **Fogli con le due facce diverse** (e318): f88, f52, f2, f83, f82 hanno recto e verso con profili diversi, nonostante
  la stessa mano e la stessa sezione.

### 15.9 Lingue A e B, prima parola, impaginazione (e319–e323)

- **Le parole tipiche di A e di B sono due famiglie lontane** (e321). Le parole tipiche di B (*chedy*, *qokedy*,
  *shedy*, *okedy*, *qokar*, *ain*…) sono più lontane da quelle tipiche di A (*cthol*, *cthor*, *dchor*, *kchol*,
  *sho*…) di quanto lo sia una parola qualsiasi (2,17 segni contro 1,53, z +8,2). Non sono varianti l'una
  dell'altra: cambiano le terminazioni (A -*ol*/-*or*, B -*edy*/-*dy*/-*ar*/-*ain*).
- **Zona di passaggio fra A e B** (e321): nell'erbario ci sono pagine con un lessico intermedio, concentrate nei
  fascicoli C, F e G.
- **La prima parola del paragrafo non è un titolo** (e320): tolto il gallows, non ricompare nel paragrafo più delle
  altre parole della prima riga.
- **Le righe si accorciano scendendo nella pagina** (e322), in tutte le sezioni, soprattutto dove ci sono i disegni
  grandi.
- **Lo stato dei bifogli di un fascicolo non segue l'annidamento** (e319). Nei fogli con le facce più diverse (f2, f52,
  f83, f88) una sola faccia somiglia al foglio coniugato (e323, incerto).
- **Lo stato cambia anche dentro la pagina, da paragrafo a paragrafo** (e326, e327). Metà alta e metà bassa della pagina
  differiscono (z 7–11), anche togliendo le righe d'inizio e fine paragrafo; il primo e l'ultimo paragrafo della stessa
  pagina differiscono (z 5–11). I livelli sono tre: fascicolo, bifoglio, paragrafo. Resta da separare lo stato dello
  scriba dall'argomento del paragrafo.
- **Le etichette A/B di Currier sono confermate dal lessico** (e325: 107 su 107 nell'erbario). Unico disaccordo f58v
  (S, etichettata A, lessico B). Nelle pagine di passaggio le parole di A e di B si mescolano nelle stesse righe (e324,
  incerto).
- **Dove sta la variazione** (e328): il fascicolo (con la sezione e la lingua che contiene) spiega la parte più grande
  delle differenze fra righe (per il segno *e* il 27%); bifoglio, pagina e paragrafo aggiungono ciascuno qualche punto
  percentuale; circa metà resta fra una riga e l'altra.
- **Paragrafi della stessa pagina** (e329): differiscono sia nel lessico (forme normalizzate, z 6,7) sia nelle scelte di
  grafia (z 6,8): cambiano argomento e abitudine insieme.
- **Girando il foglio** (e330): l'ultimo paragrafo del recto somiglia un po' di più al primo del verso (z 2,5–2,8,
  incerto); fra le pagine affiancate di fogli diversi nessun legame.
- **Scendendo nella pagina cresce -*ey*** (e333): la quota di -*ey* rispetto a -*dy* è più alta nella metà bassa delle
  righe interne, in modo coerente fra le pagine (z 3,2). Le altre scelte di grafia tendono a cambiare anch'esse, sotto
  la soglia. Se la pagina si scriveva dall'alto in basso, è una deriva dell'abitudine durante la scrittura.
- **Le differenze di lessico fra paragrafi non si raccolgono nel tempo** (e332): nell'erbario A i gruppi di paragrafi
  con lessico simile sono sparsi in tutto il libro. Da verificare se siano veri "argomenti".
- **Girando il foglio** (e330, e331): due prove con z intorno a 2 a favore della continuità fra recto e verso, nessuna
  fra fogli diversi. Indizio, non prova.
- **-*ey* è un effetto di posizione, non un orologio** (e335): la crescita di -*ey* scendendo nella pagina si ripete in
  ogni pagina, ma il verso non ne ha più del recto, né il foglio seguente più del precedente.
- **Nessun "argomento" netto** nei paragrafi dell'erbario A (e334): i gruppi trovati dall'LDA non sono più netti che su
  paragrafi fatti a caso con le stesse parole.

### 15.10 Posizione, autocitazione, zodiaco (e337–e339)

- **La posizione nella riga governa le scelte di grafia** (e337): per tutte e cinque le scelte (*ch*/*sh*, *k*/*t*,
  -*l*/-*r*, *qo*-/*o*-, -*dy*/-*ey*) il fattore più forte è la posizione della parola nella riga; poi il tipo di riga e
  l'altezza nella pagina. Paragrafo e faccia del foglio non contano.
- **Le previsioni dell'autocitazione di Timm e Schinner reggono** (e338):
  - una parola ha una parola uguale o a una modifica nelle 2 righe subito sopra più del caso (z 16,6), più che nel loro
    generatore;
  - quando la fonte è nella riga subito sopra, sta nella stessa colonna ±1 più del caso (z 8,7), quanto nel loro
    generatore.

  Cautele: la prima misura include il lessico del paragrafo, la seconda gli effetti di posizione nella riga. La verifica
  è in preparazione (e340).
- **Le etichette dello zodiaco non sono una sequenza di giorni** (e339): la stessa posizione in mesi diversi non porta
  la stessa etichetta; tre etichette su quattro cominciano con *o*.
- **Controllo dell'autocitazione** (e340):
  - a parità di lessico del paragrafo, la ripresa dalle 2 righe subito sopra resta forte (z 17,4), più del doppio
    che nel generatore di Timm e Schinner: **lo scriba riprende parole dalle righe appena scritte**;
  - la ripresa "nella stessa colonna" invece, tolte la prima e l'ultima parola della riga, quasi sparisce (z 2,7):
    l'allineamento veniva dai bordi della riga.

### 15.11 La ripresa dalle righe sopra (e340–e345, notte del 3/10)

- **Lo scriba riprende parole dalle righe appena scritte** (e340: z 17,4 a parità di lessico del paragrafo, più del
  doppio del generatore di Timm e Schinner). Le catene di ripresa sono più lunghe del caso (e343, z 6,2). La ripresa non
  segue la colonna (e340, e345).
- **Il paragrafo riparte da capo** (e343, e344): la ripresa si ferma al confine del paragrafo, e la prima parola del
  paragrafo non riprende le righe sopra (z 0,9), mentre la prima parola di ogni altra riga sì (z 4,6).
- **Le modifiche della ripresa sono quelle del lessico** (e342): nessuna modifica è preferita; le parole vicine
  differiscono per gli stessi cambi che separano le parole in generale. Tendenze verso forme più semplici (*sh*→*ch*,
  togliere *d*, -*y*).
- **Girando il foglio** (e330, e331, e341): tre misure con z fra 1,8 e 2,8, nessuna oltre la soglia. Domanda chiusa
  senza risposta positiva.
- **Il bifoglio è una sessione di scrittura** (e350): le due metà di un bifoglio, lontane nel libro rilegato,
  condividono le parole rare (z 3,2) e si riprendono fra loro (z 13,3) quanto il recto e il verso dello stesso foglio;
  le pagine affiancate di bifogli diversi no (z −0,6 e 0,8). Conferma con le parole l'e308, fatto con i segni.
- **Lo scriba guarda indietro 1–2 righe** (e347): la ripresa viene dalla riga subito sopra (z 12,8 per le copie
  modificate) e da quella prima (z 3,1); dalla terza in su niente. Il generatore di Timm e Schinner pesca fino a 6 righe:
  prima differenza netta con la loro teoria.
- **Le parole uniche non nascono dalla ripresa** (e348): hanno meno delle altre una parola simile nelle righe subito
  sopra (z −9,5). Con l'e296 (errori sparsi) e l'e355 (alcune sessioni ne producono molte di più), sono un processo a
  parte.
- **Sessioni** (e355): le varianti rare tornano sullo stesso foglio (1,8 volte il caso) e un po' nel bifoglio (1,3,
  incerto), non sulle pagine affiancate; la quota di parole nuove varia fra le sessioni il doppio del caso.
- **L'erbario in lingua B riprende più dell'erbario in lingua A** (e349): 0,055 contro 0,025; la mano non conta.
- **Ogni bifoglio ha una sola lingua e quasi sempre una sola mano** (e356): 48 bifogli su 48 tutti A o tutti B (attesi
  65% dentro il fascicolo, z 11,8); 94% con una sola mano di Davis (z 13,9). Il bifoglio è un'unità di scrittura
  completa.
- **La copia non eredita la grafia** (e356): fra parole con la stessa forma in righe vicine le scelte di grafia sono
  scelte di nuovo, salvo una leggera eredità per -*dy*/-*ey*.
- **Errori uniformi, invenzioni per sessione** (e357): le parole uniche che sono varianti di una lettera di parole
  frequenti ("errori") hanno la stessa frequenza in tutte le sessioni, come errori casuali (z 0,2); le forme davvero
  nuove variano fra le sessioni 4 volte più del caso (z 11,8), anche a parità di sezione e lingua.
- **Molte forme nuove sono giunture senza spazio** (e361–e363): le parole uniche non varianti hanno sequenze di segni
  fuori dalle regole del lessico (che nel Voynich è molto più regolare di una lingua: −1,27 contro −2,1 nat per segno),
  e un terzo contiene al suo interno una coppia di segni tipica del confine fra due parole (34,5% contro 7,3% delle
  parole comuni; in latino e italiano quasi nessuna differenza). Non sono due parole intere frequenti attaccate, ma pezzi
  di parole senza spazio. Arrivano a gruppi nella stessa riga (e362).
- **Segni di bordo della riga** (e366–e368): molte parole "uniche" ai bordi della riga sono parole normali con un segno
  in più (*y*, *d*, *s* all'inizio; *y*, *d*, *s*, *g*, *m* alla fine). A inizio riga la parolina *s*, che in mezzo alla
  riga si scrive staccata quasi una volta su due (243 attaccate contro 211 staccate), si attacca quasi sempre alla parola
  seguente (337 contro 16).
- **La ripresa copia pezzi di riga** (e372): due parole vicine riprese vengono da due parole vicine della riga sopra più
  del caso, di solito nello stesso ordine (z 8,0) ma anche invertite (z 4,3), cosa che il generatore di Timm e Schinner
  non fa.
- **Le sessioni variano lungo dimensioni indipendenti** (e373): fra 48 bifogli, otto misure (asse, forme nuove, errori,
  ripresa, -*ey*, *qo*-, lunghezza, coppie identiche) non vanno insieme; la prima componente spiega solo il 28%. L'unico
  legame netto, forme nuove ~ lunghezza, è in buona parte meccanico. La ripresa non è legata all'inventiva.
- **Oltre la giuntura, quasi nessuna preferenza fra parole vicine** (e375). Il nullo scambia le parole con lo stesso
  primo e ultimo segno dentro la pagina, conservando giunture e lessico. Le coppie di parole tornano su più pagine solo
  il 3% oltre il nullo (z 2,0, incerto), contro il 13–38% dei testi sensati a parità di parole (z 13–30). Le coppie in
  eccesso sono soprattutto parolina + parola (*or aiin*, *ol aiin*): forse parole spezzate dallo spazio. Nel Voynich non
  si vedono locuzioni come in una lingua.
- **I segni di bordo della riga non vengono dal gesto di scrivere** (e374). Nel gibberish scritto a mano da volontari
  il primo e l'ultimo segno della riga sono quasi come gli altri (divergenza 0,006, z 3,2); nel Voynich lo sono 24 volte
  di più (0,140; a parità di righe z 172). L'esito preregistrato ("anche nel gibberish") è rispettato alla lettera, ma la
  soglia guardava solo lo z.
- **L'inventiva è della sessione, non dello scriba** (e376): dentro la stessa mano di Davis, sezione e lingua le forme
  nuove variano fra i bifogli 4 volte il caso (z 11,4); la mano non spiega niente. Gli errori restano uniformi.
- **La giuntura fra parole è forte come in una lingua** (e377). L'informazione fra l'ultimo segno di una parola e il
  primo della seguente, oltre il caso, vale nel Voynich 0,18 bit. Su 71 testi in lingue vere (e381, parole intere)
  solo 6 lo superano: arabo del Corano 0,36, sanscrito 0,21–0,24 (con il *sandhi* scritto), tagalog 0,21, greco
  tecnico 0,21. Italiano 0,06–0,12, tedesco 0,04–0,08, latino 0,03–0,06. Nel
  gibberish scritto a mano dai volontari vale 0,014 e nel generatore di Timm e Schinner 0,010. Insieme all'e375: un
  legame forte fra segni di confine, quasi nessuno fra parole intere.
- **Lo spazio a volte spezza le parole** (e379): dopo un elemento corto (*s*, *or*, *ol*, *ar*), la parola seguente
  forma con lui, più del caso, una parola scritta altrove tutta attaccata (*s aiin* / *saiin*, *or aiin* / *oraiin*,
  *ol chedy* / *olchedy*; z 6,9 con un nullo che conserva la giuntura). Con le parole lunghe no.
- **La lingua B non è la lingua A cifrata con un'altra chiave** (e378). Nell'erbario la migliore sostituzione dei
  segni avvicina A a B solo dell'1% del divario fra A e B (la stessa ricerca ritrova al 100% una chiave casuale). I
  segni hanno lo stesso valore nelle due lingue; cambiano lessico e forma delle parole (B più lunghe: 4,37 contro 4,04
  segni).
- **Il gibberish scritto a mano non riprende dalle righe sopra; le lingue e il Voynich sì** (e382, pagine di 25 righe
  per tutti). Eccesso di parole uguali o a una modifica nelle 2 righe sopra: Voynich +0,034, testi sensati +0,029,
  gibberish −0,001 (rapporti 1,09, 1,20, 0,99). L'e346, con il libro intero come unità, gonfiava i testi sensati.
- **La giuntura sta fra parole vere** (e383): resta all'83% fra parole di almeno 3 segni (lingue: mediana 86%); le
  parole spezzate ne spiegano il 18%.
- **La giuntura non passa a capo: la riga è un'unità chiusa** (e384). Fra l'ultima parola di una riga e la prima della
  riga sotto la giuntura è zero (z −0,7 su 3.390 coppie), contro 0,19 dentro la riga. Nella prosa che va a capo dove
  capita il rapporto è circa 0,5–1. Vicino a zero lo hanno solo i testi in cui la riga è un versetto (Corano, Nuovo
  Testamento ebraico, Vulgata abbreviata). L'esito preregistrato, con una soglia mal scelta (minimo e massimo di testi
  piccoli), dice "come nella prosa": dichiarato.
- **Regola di raccordo fra parole** (e380): *qo*-/*o*- davanti alle gallows dipende dall'ultimo segno della parola
  prima (z 19,4): *qo*- dopo -*y*, -*o*, -*d* (59–64%), *o*- dopo -*n*, -*r*, -*s*, -*m* (*qo* 23–27%). -*l*/-*r*
  finale dipende dal primo segno della parola dopo (z 12,7): -*r* davanti ad *a*- (85%), -*l* davanti a *k*-, *t*-,
  *d*-, *l*-, *s*-, *q*- (63–86%). È la forma di una regola come *a*/*an* o la liaison (descrittivo; non dice quali
  suoni). -*dy*/-*ey* e *ch*-/*sh*- non dipendono dal vicino.
- **La ripresa è copia dalla riga subito sopra, non continuità del discorso** (e385): nel Voynich l'eccesso sta tutto a
  distanza 1 (0,032, doppio delle lingue), poco a 2, zero oltre. Nelle lingue è spalmato su 3–4 righe con il massimo a
  distanza 2. Il gibberish umano non ne ha.
- **La giuntura vale solo fra segni scritti di seguito** (e386): si rompe al salto di un disegno dentro la riga (0,026,
  z 1,9, contro 0,167 a parità di coppie) come all'a capo. In una lingua la grammatica passerebbe oltre il disegno. Le
  parole dopo il salto iniziano come quelle di inizio riga (*s*, *d*, *y*).
- **Senza parola prima si scrive *o*-, non *qo*-** (e387, previsione confermata su dati non guardati): nelle etichette, parole isolate, *qo*- davanti a gallows è quasi assente (0–5% contro 30–68% nelle righe, p < 0,0001); dopo il salto di un disegno scende al 7–19%. *qo*- compare solo dopo una parola scritta di seguito che finisce in -*y*, -*o*, -*d* (e380). La previsione simmetrica per -*l* a fine parola non regge.
- **La regola di raccordo è del sistema, non della mano** (e388): le tre mani di Davis con abbastanza testo (1 in lingua A; 2 e 3 in lingua B) seguono tutte le due regole (*qo*-/*o*-: Δ +0,25, +0,48, +0,38; -*l*/-*r*: +0,47, +0,64, +0,57; intervalli tutti sopra zero).
- **-*m* di fine riga è la forma di bordo di -*r*** (e389): a parità del resto della parola, a fine riga -*m* sale di 15 punti e -*r* scende di 12 (z 26,7 e −13,6), -*l* di 5; -*n* non cala (*dar* in mezzo, *dam* a fine riga). A inizio riga *y*- e *s*- (+9 punti ciascuno) prendono il posto di *ch*- e *k*- (−7 ciascuno).
- **Lo stampo della giuntura** (e390): le due regole di raccordo spiegano il 39% della giuntura. Il resto segue lo stesso schema: dopo -*y* viene *q*- (la coppia più forte, +0,087 bit) e si evitano *ch*-, *sh*-, *o*-; dopo -*n*, -*r*, -*l*, -*s* vengono *ch*-, *sh*-, *o*-, *a*- e si evita *q*-.
- **La giuntura c'è in ogni scrittura continua** (e391): nei testi in cerchio e lungo i raggi vale quanto nei paragrafi (E 0,174 contro 0,170, z 24,9). La regola di *qo*- invece lì è debole (+0,04, p 0,03).
- **Il raccordo si applica nel momento in cui si scrive** (e392): una parola *qo*/*o* + gallows ripresa dalla riga sopra ha la forma coordinata con la nuova vicina (effetto +0,49), molto più che con quella della fonte (+0,16); i dati non dicono chi si adatta a chi (e394). Con fonte *qo*- e nuova vicina in -*n*/-*r*/-*s*/-*m* resta *qo*- solo il 29% delle volte; con fonte *o*- e vicina in -*y*/-*o*/-*d* diventa *qo*- il 62%.
- **Inizio riga e lingue** (e393): *qo*- a inizio riga è la forma normale (44–89%) e non dipende dalla riga sopra (p 0,37); la giuntura in lingua B è il doppio che in A (0,217 contro 0,104 a parità di coppie).
- **Anche la fine della parola copiata è coordinata con la parola dopo** (e394): -*l*/-*r* di una parola ripresa dalla riga sopra segue la classe della parola successiva (+0,40) più della fonte (+0,14). Limite: e392 ed e394 mostrano coordinazione con la vicina al momento della scrittura, non chi si adatta a chi.
- **Le scoperte sulla giuntura non dipendono dalla trascrizione** (e395): con la trascrizione di Takahashi si ripetono tutte (giuntura nella riga z 251; a capo z −0,3; al salto del disegno z 1,7; regole di *qo*- e -*l*/-*r*; -*m* al posto di -*r*).
- **Si adatta la parola che si sta scrivendo** (e396): quando due parole copiate dalla riga sopra violerebbero insieme la regola di *qo*-, cambia la seconda (59% contro 18%) e mai la prima (0%). Cautela: cambiare la prima richiederebbe un cambio di finale più grosso.
- **Gli spazi cadono in posti prevedibili** (e397): il 73% dell'incertezza sulla posizione degli spazi si toglie guardando 2 segni prima e 2 dopo, più che in 70 testi sensati su 71 (solo il cinese in pinyin, a sillabe, fa di più: 86%).
- **Nessun generatore pubblicato riproduce la giuntura** (e399): Naibbe 0,002 e U2 0 (nessuna giuntura), Timm e Schinner 0,011, U3 0,076 ma passa l'a capo (Q 0,97); il Voynich 0,191 con Q −0,02.
- **Lo scriba guarda avanti di una parola** (e3a01, e3a02): quando due parole copiate violerebbero la regola -*l*/-*r*, cambia la finale della prima (59% contro 21%, p 0,0002); per *qo*-/*o*- cambia l'inizio della seconda (60% contro 18%). Ogni regola agisce sul pezzo più facile da cambiare: lo scriba conosce la parola successiva mentre finisce quella in corso. Regge con la trascrizione di Takahashi (e3a34: 62% contro 22%; 61% contro 16%).
- **Robustezza** (e3a04, e3a05): giuntura e regole di raccordo reggono in erbario, biologia, ricette e farmacia, e con la terza trascrizione (Glen Claston, alfabeto v101: nella riga 0,233, a capo 0,003; coppia più forte "-9 4-" = -*y* *q*-). Eccezione da verificare: nelle 6 pagine "solo testo" la giuntura sembra passare l'a capo (193 coppie, z 3,6).
- **Nessun legame oltre la parola accanto** (e3a03): a parità della parola in mezzo, l'ultimo segno di una parola non dice niente sul primo segno della parola dopo la successiva (E 0,002 a 10.000 parole, z 1,3 sul libro intero). Nelle lingue il legame c'è: con un nullo dentro la pagina (e3a07), che toglie l'effetto dell'argomento, resta piccolo (mediana 0,013) ma significativo in 34 testi su 42; nel Voynich è zero anche così (0,001, z 0,9). Il Voynich guarda una parola avanti e una indietro, non di più. Attenzione (e3a51): neanche il cifrario Naibbe, che nasconde un vero testo latino, ha questo legame; la proprietà distingue il Voynich dalle lingue in chiaro, non da un cifrario verboso.
- **La -*m* di fine riga è legata al margine** (e3a09): nell'ultima riga del paragrafo, che di solito si ferma prima del margine, la parola finale prende -*m* meno spesso (34% contro 45%, p 0,0006).
- **Il legame con la parola vicina passa quasi tutto dal segno di bordo** (e3a08): a parità di ultimo segno, l'identità della parola prima aggiunge sull'inizio della successiva 0,059 bit (a 10.000 parole) contro una mediana di 0,33 nelle lingue e 0,12 nel gibberish umano; all'indietro 0,024 contro 0,31.
- **Le parole uniche rispettano la giuntura per circa due terzi** (e3a12): forme nuove ed errori seguono il legame con le vicine con Q 0,51–0,67 rispetto alle parole ripetute (z 10–23). Escono dallo stesso processo di scrittura, meno regolari.
- **-*ey* cresce davvero scendendo nella pagina** (e3a15): a parità di pagina, posizione nella riga e lunghezza della riga, la quota di -*ey* fra -*dy*/-*ey* è più alta nella metà bassa (+0,057, z 4,8).
- **La regola di raccordo è uguale in tutte le sessioni** (e3a16): la sua forza varia fra i bifogli solo quanto il caso (rapporto sul nullo 0,72, z −0,8), al contrario dell'inventiva.
- **Un piccolo legame fra parole intere vicine** (e3a14): oltre il segno di bordo e tolto il lessico della pagina, l'identità di una parola dice ancora un poco sull'inizio della successiva: un quarto di quanto succede nelle lingue (0,026 contro 0,111 bit).
- **-*ey* cresce scendendo nella pagina** (e3a17, e3a20): +0,12–0,14 dalla cima al fondo della pagina; l'effetto apparente lungo il paragrafo (e3a17) veniva dalla prima riga del paragrafo e sparisce senza di essa (e3a20). La crescita sta soprattutto nelle pagine delle ricette (+0,108, z 5,7); in erbario e biologia è nella stessa direzione ma sotto soglia (e3a21).
- **La coppia più forte della giuntura ha spazi netti** (esplorativo): fra -*y* e *q*- lo spazio è incerto solo nell'1% dei casi (8% in generale); gli spazi incerti stanno fra -*l* e *k*- (43%), -*r* e *a*- (28%), dove le parole si spezzano.
- **Due famiglie di scelte di grafia** (e3a18, e3a20): *qo*-/*o*- e -*l*/-*r* dipendono dalla parola vicina e non dalla posizione; *ch*/*sh* e *k*/*t* non dipendono dalla vicina e hanno solo un effetto della prima riga del paragrafo (più *sh* e *t*), senza derive graduali; -*dy*/-*ey* cresce con l'altezza nella pagina.
- **La copia dalla riga sopra è costante lungo il paragrafo** (e3a19, e3a20): l'aumento apparente (e3a19) veniva dall'apertura, perché la seconda riga copia poco dalla prima, fatta di parole nuove; dalla terza riga in poi la copia è costante.

### 15.12 Sintesi della notte 3–4/10: il Voynich a confronto con lingue, gibberish umano e generatori

Numeri già registrati nel Quaderno (esperimenti indicati). "Lingue" = 71 testi di Gaskell e Bowern con le parole intere
(e381), di solito 10.000 parole per testo. "Gibberish" = 38 testi scritti a mano da volontari (Gaskell e Bowern 2022).
"Generatori" = Naibbe, U2, U3, Timm e Schinner (e399).

| proprietà | Voynich | lingue | gibberish umano | generatori pubblicati |
|---|---|---|---|---|
| giuntura fra parole vicine, bit (e377, e381) | **0,18–0,19** | 0,03–0,36; solo 6 su 71 sopra il Voynich | 0,014 | 0,00–0,08 (e399) |
| giuntura a capo / nella riga, Q (e384, e399) | **−0,02** | 0,5–1 nella prosa; ~0 solo dove la riga è un versetto | 0,46 (non significativa) | U3 0,97; TS 0,2 |
| giuntura al salto di un disegno (e386) | **0,026** (riga 0,167) | — | — | — |
| legame a distanza 2, a parità della parola in mezzo, nullo nella pagina (e3a07, e3a51) | **0,001** (z 0,9) | mediana 0,013; 34 su 42 significativi | 0,001 | tutti zero, anche il cifrario Naibbe |
| identità della parola oltre il segno di bordo, nullo nella pagina (e3a14) | 0,026 | mediana 0,111 | — | — |
| coppie di parole che tornano oltre la giuntura, R (e375, e381) | **1,03** | 1,16–1,38 | 1,13 | TS 0,99 |
| ripresa dalle 2 righe sopra, eccesso, pagine di 25 righe (e382) | +0,034 | +0,029 | **−0,001** | TS +0,022 |
| forma del calo della ripresa, C (e385) | **−0,07** (solo la riga sopra) | 0,28 (3–4 righe) | nessuna ripresa | — |
| spazi prevedibili dai segni vicini, R (e397) | 0,73 | 0,28–0,86 (sopra il Voynich solo il pinyin) | 0,09 (testi piccoli) | — |
| bordi della riga, divergenza del primo segno (e374) | **0,140** | 0,02 | 0,006 | TS 0,039 |
| alternanza "vocale/consonante" (Sukhotin) al confine, A (e3a30) | **1,086** (z 20,8) | 0,94–1,16, mediana 1,02 | 1,011 | — |
| inizi uguali fra righe consecutive, rapporto (e3a35, e3a95) | **0,51** (z −8,0) | mediana 0,95; solo 3 su 57 sotto | 1,32 | Naibbe 0,93, TS 1,10, U2 1,38, U3 2,05 |
| scriba che guarda avanti di una parola (e3a02, e3a34) | sì (ZL e IT) | — | — | — |
| coppie fra parole che ricalcano le coppie dentro le parole, ρ (e3a49, e3a50) | **0,47** (IT 0,44; GC 0,50) | sotto 0,39 tutte; di solito sotto 0,2 | 0,20 | — |
| spazio prevedibile dai due segni vicini, F1 (e3a58) | **0,86** | mediana 0,64; 90° percentile 0,72 (pinyin 0,97) | 0,28 | 0,80 – 0,88 |
| forme probabili presenti nel vocabolario (e3a61) | **0,43** | mediana 0,04; 90° percentile 0,09 (pinyin 0,54) | 0,09 | 0,41 – 0,45 |
| tagli sbagliati che danno parole vere (e3a67) | **0,50** | mediana 0,065; massimo 0,25 | 0,06 | 0,35 – 0,53 |
| frequenza delle parole che segue la forma, ρ (e3a55) | **0,58** | mediana 0,11; massimo 0,28 | 0,09 | 0,41 (Naibbe) – 0,60 |
| ripetizione nella riga che si spegne con la distanza, calo d 7–10 / d 1–4 (e3a87, e3a89, e3a90) | **0,12** | mediana 2,86; 10° percentile 1,10 | 1,59 | Naibbe nessuna ripetizione; U2 1,28, U3 1,88, TS 0,91 |
| memoria di due segni nella parola, bit per terna (e3a85) | 0,23 | da 0,38 a 1,08 (tutte sopra) | — | Naibbe 0,23, TS 0,30, U2 0,04, U3 0,06 |
| catena per riga: proprietà riprodotte / non riprodotte (e3a78, e3a80, e3a81, e3a92) | 6 orizzontali sì; copia, margine, apertura del paragrafo, -ey no | — | — | — |
| regole di raccordo *qo*-/*o*-, -*l*/-*r* (e380, e388, e395, e3a16) | sì, in tutte le mani, sessioni e trascrizioni | (*sandhi*, liaison in alcune lingue) | — | — |

**In una riga:** il Voynich ha un legame fra parole vicine forte come quello delle lingue più legate, fatto di regole di
raccordo fra segni di confine, chiuso nel tratto scritto di seguito (si rompe all'a capo e al salto di un disegno), e
quasi niente oltre la parola accanto. Ha una ripresa che è copia dalla riga subito sopra, non continuità del discorso.
Nessun testo di confronto ha questa combinazione: le lingue hanno legami anche a distanza e attraverso le righe; il
gibberish umano non ha né giuntura né ripresa; i generatori pubblicati non hanno la giuntura chiusa nella riga.
- **L'apertura del paragrafo pende verso il lato B dell'asse** (e3a22): la prima riga ha più *e* e finali -*y*, meno *a* e -*n* del resto del paragrafo (+0,10, z 6,7), la seconda un po' meno (+0,05, z 3,0): una pendenza che sfuma, più forte in lingua B.
- **Un legame verticale sul margine sinistro** (e3a24–e3a27, e3a33): lo scriba evita di cominciare una riga come la precedente. Con un nullo corretto (ordine delle righe rimescolato; quello di e3a26/e3a27/e3a31 era difettoso, dichiarato), sono evitati *qo*- (z −9,7), *o*- (−7,0), *d*- (−3,8), *ch*- (−3,6), *y*- (−3,5); *s*- no. Se la riga sopra comincia con *qo*-, la riga sotto prende *o*- (Δ −0,52; z da −5,8 a −9,7 in ZL, lingua A, lingua B e con Takahashi). Non conta la riga a distanza 2, né la fine della riga sopra; al margine destro nessun effetto (e3a24); fra paragrafi nessun effetto (e3a40).
- **Al confine fra parole si alternano "vocali" e "consonanti"** (e3a30): con le classi di Sukhotin ricavate dentro le parole, la fine di una parola e l'inizio della seguente sono di classe diversa l'8,6% più del caso (z 20,8), nella parte alta delle lingue (mediana +1,8%; francese +8,9%, inglese +7–16%); il gibberish umano no (+1,1%, z 1,3).
- **L'evitamento sul margine sinistro è proprio del Voynich** (e3a35): rapporto 0,51 (z −8,0) contro 1,32 nel gibberish scritto a mano (nessun evitamento) e una mediana di 0,95 nelle lingue (solo 3 testi su 57 sotto il Voynich).
- **Quanto decidono le regole** (e3a36): il contesto trovato (posto nella riga, segno vicino, riga sopra) toglie il 18% dell'incertezza su *qo*-/*o*- (accuratezza 71% contro 55%) e il 7% su -*l*/-*r* (61% contro 49%). Le regole sono vere ma lasciano libera gran parte della scelta.
- **qo-/o- e -l/-r sono scelte in gran parte libere** (e3a37): parola e contesto insieme tolgono solo il 18,5% (qo-/o-) e il 10,8% (-l/-r) dell'incertezza. Le regole di raccordo spingono, ma la scelta resta per lo più aperta.
- **Le etichette consecutive si copiano con piccole modifiche** (e3a38): due etichette una dopo l'altra nella stessa pagina sono simili (uguali o a una modifica) il doppio del caso (4,0% contro 2,0%, z 4,3): *otol*/*otor*, *oty*/*oky*, *okal*/*okaly*, *otalar*/*otalam*. Lo stesso processo di copia con modifiche del testo.
- **Gli "errori" sono dello scriba, non dei trascrittori** (e3a39): le loro sostituzioni non cadono sui segni su cui ZL e Takahashi non concordano (16% contro 20% della variazione normale), e l'83% è letto identico da Takahashi.
- **Due classi di iniziali** (e3a41): dopo una parola in -*n*/-*r*/-*s*/-*m* la seguente comincia quasi sempre con *ch*-, *sh*-, *o*-, *a*-, *d*-, *cth*- e quasi mai con *k*-, *t*-, *q*-, *l*-, *r*-, *y*- (per esempio *k* contro *sh*: 4% dopo -*n*/-*r*/-*s*/-*m*, 42% dopo -*y*/-*o*/-*d*); dentro le classi (*ch*/*sh*, *k*/*t*) la scelta non dipende dalla parola prima.
- **Robustezza d'insieme** (e3a43): giuntura chiusa nella riga, le due regole di raccordo, l'evitamento sul margine sinistro, l'assenza di legami a distanza 2 e -*m* al posto di -*r* reggono tutte, separatamente, nella prima e nella seconda metà del libro.
- **L'evitamento riguarda l'inizio della riga, non un bordo visivo** (e3a44): dove le righe riprendono a destra di un disegno, una sotto l'altra, gli inizi ripetuti non sono evitati (rapporto 0,92); sul margine vero delle stesse righe sì (0,27, z −4,1).
- **Anche dentro le parole attaccate vale il raccordo** (e3a46, e3a47): nelle parole uniche le *q* interne, che segnano due pezzi attaccati senza spazio, seguono un segno -*y*/-*o*/-*d* in 28 casi su 29 (97%, contro il 56% atteso senza regola): *chedyqokam*, *okeedyqol*, *teyqokedy*.
- **Il raccordo è la regola dei segni dentro la parola, applicata attraverso lo spazio** (e3a48): dentro le parole comuni davanti a *k*/*t*/*d*/*l*/*s*/*q* c'è sempre *l*, mai *r*; fra parole separate la stessa preferenza vale più morbida (71% contro 35%). Lo spazio è un confine debole dentro una catena di segni con regole proprie.
- **Lo spazio è un confine debole, più che in ogni lingua** (e3a49): le preferenze fra l'ultimo segno di una parola e il primo della seguente ricalcano quelle fra due segni dentro la parola (ρ 0,47 a 10.000 parole) più che in tutte le 71 lingue del confronto (al massimo 0,39 in testi piccoli; di solito sotto 0,2) e nel gibberish umano (0,20). Il testo si comporta come una catena di segni con regole di sequenza proprie, in cui gli spazi sono inseriti. Regge con Takahashi (0,44) e con Glen Claston, alfabeto v101 (0,50) (e3a50), con gli spazi incerti uniti (0,44) e senza le parole cortissime (0,42 contro un massimo di 0,33 nelle lingue) (e3a53); vale in lingua A (0,66) e B (0,46) e per i tre scribi principali (0,41–0,63) (e3a54).
- **Catena con spazi deboli e riga chiusa: nessun generatore pubblicato ha tutte e due** (e3a52, e399): U3 riproduce la giuntura che ricalca le sequenze interne (0,50) ma la fa passare all'a capo; Naibbe, U2 e Timm e Schinner non hanno né l'una né l'altra.

**Figura** `risultati/figure/catena_riga.png` (script `strumenti/figura_catena_riga.py`, solo risultati già registrati):
ogni testo è un punto. In orizzontale, quanto la giuntura fra parole ricalca le sequenze dentro le parole (ρ, e3a49,
e3a52); in verticale, quanto la giuntura passa l'a capo (Q, e384, e399). Il Voynich sta da solo in basso a destra:
catena con spazi deboli **e** riga chiusa. Le lingue stanno a sinistra e per lo più in alto (riga aperta), con pochi
testi a versetti vicino a Q = 0; U3 sta in alto a destra (catena ma riga aperta). Per Naibbe e per il gibberish la Q
conta poco, perché la loro giuntura è quasi zero.
- **La frequenza delle parole segue la loro forma** (e3a55): le parole frequenti del Voynich sono le sequenze di segni più probabili per le regole di sequenza (ρ 0,58), più che in tutte le lingue (mediana 0,11, massimo 0,28) e del gibberish umano (0,09); come nei generatori (0,53–0,60) e nel cifrario verboso Naibbe (0,41). Esclude un vocabolario scelto per significato (lingua o cifrario a dizionario), non un procedimento sui segni.
  - Replicato (e3a56) con Takahashi e Glen Claston, in lingua A e B e per le mani 1, 2, 3: ρ sempre 0,57–0,61, sopra il massimo delle lingue alla stessa dimensione.
  - Non è un effetto della bassa entropia dei segni (e3a57): nelle lingue ρ non cresce quando l'entropia cala (r = +0,20); Toki Pona, con la stessa entropia del Voynich (2,25 contro 2,22 bit), ha ρ 0,23 contro 0,59.
- **Lo spazio si indovina dai segni vicini** (e3a58): con la sola coppia di segni attorno al punto, lo spazio si prevede con F1 0,86, sopra il 97% delle lingue (mediana 0,64; più alti solo i due testi in pinyin, che chiudono ogni parola col numero del tono); come nei generatori (0,80–0,88); il gibberish umano è il meno prevedibile (0,28). Gli spazi incerti della ZL cadono proprio dove la regola è incerta: probabilità media di spazio 0,47, contro 0,82 negli spazi certi e 0,04 dove non c'è spazio.
  - Conferma secondaria e debole (e3a59): anche la memoria di due segni passa lo spazio (ρ2 0,35 e 0,23, sopra tutte le lingue), ma con poche terne, valori molto variabili fra sottoinsiemi e il gibberish umano a 0,26 in uno dei due ambiti. Da non usare come prova autonoma.
  - Lo conferma un secondo trascrittore (e3a60): dove la ZL segna lo spazio come incerto, Takahashi (che non usa mai la virgola) lo mette 2 volte su 3, contro il 99,6% negli spazi certi e lo 0,4% altrove; i 320 punti in cui ZL e IT non concordano hanno probabilità media della regola 0,49. L'ambiguità degli spazi è sul foglio, proprio dove la regola lascia la scelta allo scriba.
- **Il vocabolario riempie le forme possibili** (e3a61): fra le sequenze di segni più probabili per le regole di sequenza, il 43% sono parole del Voynich, contro il 4% nelle lingue (mediana; 90° percentile 9%), il 9% nel gibberish umano e il 41–45% nei generatori. Solo il pinyin (sillabe da un inventario chiuso) fa di più (0,54), ma nel pinyin la frequenza non segue la forma (e3a55). Il lessico del Voynich è quasi l'insieme completo delle forme ben fatte, non un campione rado come in una lingua.
  - Nei generatori (e3a62) il legame fra parole intere è zero in Naibbe, U2 e U3, e uguale al Voynich in Timm e Schinner (0,026), dove le parole si copiano a pezzi dalle righe sopra. La piccolezza del legame nel Voynich non esclude quindi un cifrario verboso alla Naibbe.
  - Verso la fine della riga gli spazi facoltativi calano un poco (e3a64: −4 punti su 100 a parità dei segni vicini, p 0,0005) e gli spazi dubbi crescono: lo scriba stringe vicino al margine, come per -m al posto di -r. Effetto piccolo.
  - Il piccolo legame fra parole intere del Voynich non viene dalla copia dalla riga sopra (e3a63): togliendo le parole presenti nella riga sopra resta come togliendo quelle di una riga lontana. Nel generatore di Timm e Schinner, invece, nello stesso test il legame sparisce: stessa grandezza, origine diversa.
- **Figura degli spazi** (`risultati/figure/spazi.png`, da `strumenti/figura_spazi.py`): A) quota di spazi indovinati dai due segni vicini (F1) per Voynich, 71 lingue, gibberish e generatori (e3a58); B) distribuzione della probabilità della regola di spaziatura negli spazi certi, negli spazi incerti della ZL e dove non c'è spazio, con la quota di spazi messi da Takahashi (e3a60). Si vede che gli spazi incerti sono sparsi su tutta la scala (18% vicino a 0, molti fra 0,3 e 0,7), non concentrati come gli altri.
  - Gli spazi facoltativi cambiano un poco da mano a mano (e3a66: mano 1 +7 punti, mano 2 −5, p 0,001, a parità dei segni vicini e della lingua), mentre le regole di raccordo sono uguali per tutti: lo spazio facoltativo è in parte un'abitudine di scrittura. Mano e sezione non sono separabili.
- **Anche i tagli sbagliati danno parole vere** (e3a67): togliendo gli spazi e rimettendoli a caso con la regola dei segni vicini, il 50% dei pezzi sbagliati (almeno 3 segni) sono parole del Voynich; nelle lingue il 6,5% (mediana; massimo 25%, klingon), nel gibberish umano il 6%, nei generatori 35–53%. Le parole del Voynich si comportano come pezzi di una catena tagliata dove la regola lo permette.
  - Spazi prevedibili, forme riempite e tagli sbagliati reggono con Takahashi e con Glen Claston (e3a68: F1 0,85–0,87; riempimento 0,35–0,43; tagli 0,46–0,50), sempre molto sopra il 90° percentile delle lingue.
- **Il Voynich è già un testo da catena di segni** (e3a69): riscritto da una catena di ordine 2 addestrata su sé stesso, il Voynich non cambia in nessuna delle quattro misure (frequenza-forma, riempimento, spazi, tagli). Le lingue riscritte allo stesso modo si spostano verso il Voynich (ρ 0,11 → 0,29; riempimento 0,04 → 0,16; tagli 0,07 → 0,18) ma arrivano a metà strada, e i loro spazi restano imprevedibili (0,67).
  - Non è solo questione di rigidità della catena (e3a70, analisi decisa dopo l'e3a69): anche le lingue con l'entropia più bassa, riscritte, restano lontane dal Voynich per frequenza-forma (z +3,6) e tagli sbagliati (z +3,3). Le parole del Voynich sono più regolari di quelle che una catena di segni ricava da una lingua.
  - Due terzi del piccolo legame fra parole intere stanno nel paragrafo (e3a65: tenendo fermo il paragrafo, E scende da 0,027 a 0,008; la posizione nella riga conta poco). Resta un filo di legame fra vicine (z 5 su tutto il libro). Parte del calo può essere meccanica (gruppi più piccoli).
  - Correzione con l'e3a71: con catene di ordine 1 e 3 l'e3a69 non regge alla lettera (con l'ordine 3 le lingue riscritte tornano quasi come quelle vere). Il fatto solido: il Voynich riscritto con ordine 2 o 3 è identico al vero in tutte e quattro le misure, mentre le lingue cambiano molto con l'ordine. Le parole del Voynich non hanno struttura oltre due segni di memoria, almeno in queste misure; quelle delle lingue sì.
  - Un cifrario verboso alla Naibbe non lascia legami misurabili fra parole vicine, né fra parole intere frequenti (prova esplorativa sui controlli, e3a73 abbandonato: Naibbe z 0,5, inglese z 46) né fra segni di bordo (e3a62): la debolezza dei legami fra parole del Voynich non è un argomento contro un cifrario di quel tipo.
  - **Correzione (e3a72):** il calo del legame col nullo del paragrafo (e3a65) è lo stesso con "paragrafi finti" di uguale grandezza: viene dai gruppi più piccoli (effetto meccanico o lessico delle righe vicine), non dal paragrafo come unità. La frase "due terzi stanno nel paragrafo" va ritirata.
- **La copia porta con sé un poco gli spazi** (e3a74): dove un tratto di 4 segni torna dalla riga subito sopra, lo spazio facoltativo è messo come sopra il 76% delle volte, contro il 74% con lo stesso tratto in una riga lontana (differenza dentro gli strati +0,05, IC +0,01 – +0,09). Lo scriba ricopia almeno in parte parole già scritte, non solo sequenze di segni. Indizio debole.
- **Figura del vocabolario** (`risultati/figure/vocabolario.png`, da `strumenti/figura_vocabolario.py`): quattro pannelli (frequenza-forma, forme riempite, spazi prevedibili, tagli sbagliati) con Voynich, 71 lingue, gibberish scritto a mano e i quattro generatori. In tutti il Voynich sta con i generatori, lontano dalle lingue e dal gibberish.
  - I segni del Voynich sono molto legati al loro posto nella parola (e3a75: entropia di posizione 0,75, 4° percentile delle lingue; pinyin 0,62), ma la rigidità di posizione non spiega perché la frequenza segua la forma (z +4,8) né i tagli sbagliati (z +4,4); spiega solo il riempimento delle forme.
- **Che memoria ha il meccanismo delle parole** (e3a76, metodo tarato su catene di ordine noto): le frequenze del Voynich seguono una catena di segni "quasi di ordine 1, con un po' di ordine 2" (ρ 0,58 con memoria di un segno, 0,69 con due; guadagno +0,10, contro +0,37 nelle catene di ordine 2 e −0,04 in quelle di ordine 1). I generatori non hanno il guadagno di ordine 2 (da −0,02 a +0,01). Le caselle per posto spiegano poco. Rilegge l'e3a70: l'"eccesso" del Voynich veniva in parte dal misurare con un modello di ordine 1.
  - Regge con Takahashi, con Glen Claston (guadagno +0,06) e anche in EVA semplice con i composti spezzati (+0,15, sotto la soglia di 0,185) (e3a77).
- **Sintesi: catena per riga più due meccanismi verticali** (e3a78, previsione scritta prima e confermata): il Voynich riscritto riga per riga dalla propria catena di segni di ordine 2 (con inizio e fine riga) ha la stessa giuntura, la stessa chiusura della riga, le stesse forme di bordo (-m a fine riga, y/s/d a inizio), la stessa catena attraverso lo spazio e la stessa frequenza-forma (R da 0,76 a 1,07). Non ha la copia dalla riga sopra (R 0,06) né l'evitamento degli inizi ripetuti sul margine sinistro (R −0,13): queste due richiedono che lo scriba guardi la riga sopra. Le proprietà riprodotte sono contenute nelle statistiche locali dei segni; nulla qui dice come il testo sia stato prodotto né se abbia un significato.
  - I due meccanismi verticali sono distinti (e3a79): la prima parola della riga si copia dalla riga sopra quanto le altre (eccesso +0,040 contro +0,043); lo scriba evita solo di cominciare come cominciava la riga sopra.
  - Regge identica con la trascrizione di Takahashi (e3a80: le sei proprietà con R da 0,82 a 1,07; copia e margine R 0,02).
  - Servono meccanismi in più anche per l'apertura del paragrafo (p/f nella prima riga, R 0,00) e per -ey che cresce scendendo nella pagina (R −0,13) (e3a81). Quadro: catena per riga per le proprietà orizzontali, più quattro proprietà verticali (copia dalla riga sopra, margine sinistro, apertura del paragrafo, -ey scendendo).
- **Figura della sintesi** (`risultati/figure/catena_spiega.png`, da `strumenti/figura_catena_spiega.py`): per ogni proprietà, R = valore nel Voynich riscritto da una catena di segni per riga / valore nel Voynich vero (e3a78 ZL, e3a80 Takahashi, e3a81). Le sei proprietà orizzontali stanno vicino a 1; copia dalla riga sopra, margine sinistro, apertura del paragrafo e -ey scendendo stanno vicino a 0.
  - La deriva di -ey lungo la pagina non viene dalla copia (e3a82: fra righe consecutive -dy→-ey 118 volte, -ey→-dy 132): è una preferenza di posizione nella pagina, distinta dalla copia.
- **La copia preferisce le parole appena scritte** (e3a83): l'eccesso di parole riprese dalla riga sopra cresce dal primo terzo (+0,016 per parola) all'ultimo (+0,027); posizione media delle fonti +0,009 rispetto al nullo (IC +0,002 – +0,016). Effetto piccolo, coerente con una copia fatta anche a memoria.
  - Si ritrova identica con Takahashi (e3a84: +0,009, IC +0,003 – +0,017).
- **Memoria di due segni misurata direttamente** (e3a85): il Voynich ne ha meno di tutte le 71 lingue (0,23 bit per terna contro 0,38–1,08) e quanto Naibbe (0,23) e Timm e Schinner (0,30); U2/U3 meno (0,04–0,06). Sta a inizio parola e attorno a o, e, i (serie ee, ii). Corregge una frase dell'e3a76: i generatori non hanno il "po' di ordine 2" nella misura frequenza-forma, ma nella struttura delle sequenze Naibbe e Timm e Schinner ne hanno quanto il Voynich.
  - Anche dentro la riga c'è ripresa oltre la catena (e3a86): ripetizioni immediate, quasi ripetizioni e ritorni a distanza 2–4 sono da 2 a 3 volte quelli della catena (R 0,36–0,51). Con l'e3a83: lo scriba riprende materiale appena scritto, nella stessa riga e nella riga sopra.
  - Le due riprese sono distinte (e3a87): nella riga la ripetizione cala con la distanza e si spegne dopo 6–7 parole (memoria recente); dalla riga sopra è piatta da 3 a 20 parole indietro (sguardo alla riga sopra, non memoria). Corregge l'unione proposta dopo l'e3a86.
  - Si ritrova con Takahashi (e3a88: nella riga +0,0066 → +0,0014; dalla riga sopra +0,0058 → +0,0050).
  - **Correzione (e3a89):** che la riga sopra conti un po' di più a parità di distanza succede anche nelle lingue (non distintivo). Distintivo è il calo della ripetizione dentro la riga: nel Voynich forte a breve distanza e spenta in 6–7 parole (rapporto 0,12), nelle lingue l'opposto (mediana 2,86; 10° percentile 1,10): le lingue evitano di ripetere subito, il Voynich ripete subito.
  - Nessun testo di confronto ha questa firma (e3a90): Timm e Schinner ripete a breve distanza ma senza spegnersi (0,91); U2, U3 e il gibberish umano come le lingue (1,3–1,9); Naibbe non ripete affatto (eccesso ±0,0002; la regola preregistrata lo classificava male, difetto dichiarato). La ripresa di memoria corta nella riga è propria del Voynich.
  - Vale in lingua A e B e per le mani 1, 2, 3 (e3a91: eccesso entro 4 parole +0,004/+0,006, zero a 7–10 parole).
  - Con l'alfabeto di Glen Claston reggono sia la sintesi della catena (giuntura, chiusura, catena, frequenza-forma R 0,98–1,11; copia e margine R ≤ 0) sia la ripetizione di memoria corta (calo 0,36) (e3a92): le novità valgono con tutte e tre le trascrizioni.
  - Le ripetizioni immediate con l'inizio cambiato seguono il raccordo (e3a93: Δ +0,17, IC +0,10 – +0,23; a distanza 2 nessun effetto): *okeey qokeey* (dopo -y si aggiunge q), *qokar okar* (dopo -r si toglie). La ripresa di memoria corta e il raccordo lavorano insieme.
  - Anche quando una ripetizione cambia la fine, la fine nuova si accorda con la parola dopo (e3a94: Δ +0,28 immediate, +0,41 a distanza 2; *chor chol daiin*, *dal dar ol*). Qui la direzione non è stabilita (coerente con lo sguardo avanti dell'e3a02).
- **Nessun generatore evita l'inizio uguale sul margine sinistro** (e3a95): Naibbe 0,93, Timm e Schinner 1,10 (non evitano), U2 1,38, U3 2,05 (ripetono), contro 0,51 del Voynich. Tratti che nessun generatore pubblicato ha: giuntura, chiusura della riga, ripresa di memoria corta nella riga, evitamento sul margine.
  - Si ritrova con Takahashi (e3a96: Δ +0,17, IC +0,11 – +0,23; a distanza 2 +0,03).
  - Il salto di un disegno azzera la ripetizione immediata come l'a capo (e3a97: eccesso +0,0047 nelle coppie continue, z 4,3; −0,0048 a cavallo del salto, 665 coppie). Il tratto scritto di seguito è l'unità della scrittura anche per la memoria corta.
  - La catena riproduce la quantità di vocabolario e la legge di Zipf (e3a98: parole diverse R 1,09; pendenza R 1,03) ma fa il 15% di parole uniche in più: il Voynich inventa un po' meno della propria catena, coerente con il riuso (copia e ripetizione).
- **Lo spazio si decide con i segni vicini e la lunghezza, non con la parola** (e3a99, e3b01–e3b03): nei punti facoltativi, nelle lingue lo spazio segue fortissimamente la parola intera (preferenza lessicale da +4 a +7); nel Voynich no. A parità dei 4 segni attorno e della lunghezza dei due pezzi la preferenza lessicale è minima (+0,04 sopra il nullo, z 2,0; latino +4). Lo scriba taglia più spesso quando il pezzo in corso è lungo (5+ segni: +11 punti) ed evita di staccare pezzi di 1–3 segni. Una prima lettura "preferenza contraria" (e3b01, e3b02) era un effetto della lunghezza.
  - Si ritrova con Takahashi (e3b04: scarto lessicale +0,05, z 3,2; stessa dipendenza dalla lunghezza).
  - Nei testi di confronto (e3b05, scarto lessicale con lo stesso nullo): Naibbe +1,58, U2 +0,93, gibberish umano +0,81, U3 +0,45, Timm e Schinner +0,11 (come il Voynich, +0,20); lingue +4. Lo spazio non lessicale distingue il Voynich da lingue, Naibbe, gibberish e U2/U3, non da Timm e Schinner.
- **Figura della memoria corta** (`risultati/figure/memoria_corta.png`, da `strumenti/figura_memoria_corta.py`): eccesso di ripetizione di una parola nella stessa riga entro 1–4 parole e a 7–10 parole (rispetto alla catena di segni), per Voynich (e3a87), lingue (mediana, e3a89), generatori e gibberish (e3a90). Solo nel Voynich la barra vicina è alta e quella lontana quasi nulla.

### Sintesi aggiornata (notte del 4/10, e3a55–e3b05)

Il testo del Voynich si descrive bene con quattro ingredienti; niente di questo è una decifrazione né dice se il testo
abbia un significato.

1. **Una catena di segni scritta riga per riga** (memoria quasi di un segno, un po' di due), che riparte a ogni a capo e
   a ogni salto di disegno. Da sola riproduce giuntura, chiusura della riga, forme di inizio e fine riga, catena
   attraverso lo spazio, frequenza che segue la forma, quantità di vocabolario e legge di Zipf (e3a76–e3a81, e3a92,
   e3a98).
2. **Spazi messi con i segni vicini e la lunghezza della parola in corso**, non con l'identità della parola (e3a58,
   e3a99, e3b03–e3b05): per questo il vocabolario riempie le forme possibili e un taglio diverso dà quasi sempre parole
   che esistono (e3a61, e3a67). Gli spazi dubbi cadono dove la regola lascia la scelta (e3a60).
3. **Ripresa di quello che si è appena scritto**: nella stessa riga a memoria corta (spenta in 6–7 parole), adattata al
   raccordo (e3a86–e3a93); dalla riga sopra, da tutta la riga (e3a83, e3a87).
4. **Regole di pagina e di paragrafo**: evitare di cominciare come la riga sopra, apertura del paragrafo, deriva di
   -*ey* lungo la pagina (e3a25–e3a35, e3a81, e3a82).

Rispetto ai testi di confronto: le lingue hanno spazi lessicali, nessuna catena attraverso lo spazio, ripetizione che
cresce con la distanza; il gibberish scritto a mano non ha giuntura, copia, evitamento sul margine; nessun generatore
pubblicato ha insieme giuntura chiusa nella riga, memoria corta nella riga ed evitamento sul margine (Timm e Schinner ha
la copia e lo spazio non lessicale, ma non il resto).
- **Le "scelte di grafia per riga" sono memoria corta** (e3b06): l'accordo nelle scelte facoltative (qo/o, -ey/-dy, sh/ch, ee/e) c'è fra parole a 2–3 di distanza (+0,031) e sparisce a 6–10 nella stessa riga (−0,001). Le "12 scelte di riga" dell'e206b sono la ripresa di memoria corta, non interruttori di riga. -l/-r non concorda (la decide il raccordo).
  - Regge con Takahashi (e3b07: +0,031 vicino, −0,001 lontano). Senza le coppie di parole simili tutti gli accordi scendono (difetto del confronto con 0, dichiarato), ma il vicino resta +0,027 sopra il lontano: da verificare con l'intervallo della differenza (e3b08).
  - La memoria corta riguarda le scelte di grafia e non solo le parole ripetute (e3b08): tolte le coppie di parole simili, le parole a 2–3 di distanza concordano ancora più di quelle a 6–10 (+0,027, IC +0,014 – +0,039; IT +0,026). Lo scriba rifà per 2–3 parole le stesse scelte anche in parole diverse.
  - Nessun generatore ha la memoria delle scelte di grafia (e3b09: Naibbe 0,000, U2 +0,011, U3 +0,015, Timm e Schinner +0,006, tutti con intervallo che contiene 0; Voynich +0,027).
  - L'a capo azzera anche la memoria delle scelte (e3b10: +0,031 nella stessa riga, +0,002 a cavallo dell'a capo, alla stessa distanza in parole).
  - Obiezione "spazi fra sillabe" (e3b11): nel pinyin (sillabe separate) lo spazio è quasi sempre certo (circa 450 punti facoltativi ogni 10.000 sillabe, contro circa 3.300 ogni 10.000 parole nel Voynich), quindi il test non si può fare; ma lo spazio del Voynich non si comporta come un confine di sillaba di quel tipo. Il maori (scritto a parole) è lessicale (+3,2).
  - Il calo degli spazi facoltativi a fine riga resta a parità di lunghezza dei pezzi (e3b12: −0,039, p 0,001): la compressione verso il margine è reale.
  - Per qo-/o- la memoria resta a parità di raccordo con la parola prima (e3b13: +0,043, IC +0,003 – +0,084): non è un effetto indiretto del raccordo.
  - Quanto dura (e3b14): in lingua A la memoria delle scelte si dimezza dopo 2 parole, in lingua B regge circa 4 parole; in tutte e due sparisce a 6–10.
  - In bit la memoria è piccola (e3b15): per qo/o raccordo 8,2%, raccordo + memoria 8,5%; per -ey/-dy e sh/ch la memoria toglie 2–3%. Le scelte restano libere per più del 90%.
- **Niente pause dentro la riga segnate da -m** (e3b16): dopo una -m in mezzo alla riga la parola comincia come dopo -n (ch, o, sh), non come a inizio riga (d, y, s). La -m è una forma di fine riga; in mezzo alla riga è una finale come le altre.
- **Nota di interpretazione (Quaderno, dopo e3b15):** scelte di grafia libere per più del 90% ma ripetute per abitudine per 2–4 parole è il comportamento di varianti equivalenti scelte mentre si scrive. È compatibile sia con un testo senza significato sia con un cifrario eseguito a mano con omofoni; esclude che quelle varianti portino, così come sono, l'informazione di una lingua parola per parola.
- **Unire le varianti non fa emergere una lingua** (e3b17): con sh → ch, q iniziale tolta ed e ridotte a una, le quattro misure di vocabolario e spazi restano sopra le lingue e anzi salgono un poco (frequenza-forma 0,56 → 0,61). Limite: non dice nulla su codifiche di altro tipo (per esempio cifrari verbosi).
- **Nessuna periodicità lungo la riga** (osservazione dai profili e3a87 ed e3b14): ripetizione e scelte calano regolarmente con la distanza, senza picchi a 2–4 parole; nessun indizio di gruppi di parole di lunghezza fissa (come in un cifrario verboso a gruppi regolari).
  - La memoria è separata per ogni scelta (e3b18): stessa classe +0,023 (vicino − lontano), classi diverse +0,003 (IC che contiene 0). Non c'è un "modo" di scrivere comune.
  - Quali scelte hanno la memoria (e3b19): sì k/t (+0,041), qo/o, sh/ch, ee/e, -ey/-dy; no il numero di i (ain/aiin/aiiin) né -l/-r; ckh/cth e vocale iniziale con troppi pochi dati.
  - La memoria non sembra venire dallo stato della penna (nota dopo e3b18): una penna che si scarica agirebbe su tutte le scelte insieme, mentre ogni scelta ricorda solo sé stessa.
- **Figura dei profili di memoria** (`risultati/figure/memoria_profili.png`, da `strumenti/figura_memoria_profili.py`): A) accordo delle scelte di grafia per distanza nella riga, lingua A e B (e3b14); B) ripetizione di parole per distanza, nella stessa riga e dalla riga sopra (e3a87). Nella riga la memoria si spegne in poche parole; dalla riga sopra la ripresa è piatta.
  - La memoria si consuma con le lettere scritte (e3b20): a parità di parole in mezzo, con poche lettere fra le due parole l'accordo è più alto (+0,059 contro +0,023 a 2 parole; differenza +0,028, IC +0,013 – +0,042). Come una memoria di lavoro di chi scrive.
  - Anche in lettere la memoria di B dura di più (e3b21): mezza vita fra 5 e 9 lettere in A, fra 20 e 29 in B (parole di lunghezza simile).
  - Tutte e tre le mani di B (2, 3, 5) hanno la memoria lunga (mezza vita 10–29 lettere), la mano 1 in A corta (5–9) (e3b22; la mano 3 in A ha solo 2 pagine, test non fattibile): probabilmente una proprietà di B più che di uno scriba, ma A ha una sola mano.
  - Per sezione (e3b23, e3b24): la memoria è più lunga nelle sezioni a testo fitto di B (ricette, biologica, solo testo) che nell'erbario (A e B), anche contando solo coppie dentro lo stesso tratto. Stime per sezione rumorose: quanto dipenda dalla lingua e quanto dal tipo di pagina resta incerto.
- **Ripetizioni grezze** (e3b25): nel Voynich l'1,0% delle coppie di parole vicine è la stessa parola ripetuta e il 4,1% quasi la stessa, contro 0,10% e 0,23% nelle lingue (mediane; massimi 0,71% e 2,2%). **Lacuna:** manca un controllo con uno scriba medievale vero che scelga fra forme equivalenti, per sapere se la memoria corta è un'abitudine generica di chi scrive a mano.
  - Regge anche escludendo le parole cortissime in mezzo (e3b26: parola in mezzo di 3–4 lettere +0,058, di 6+ lettere +0,023; differenza +0,035, IC +0,015 – +0,056).
- **La ripresa non passa né la pagina né il paragrafo** (e3b27, e3b28): a parità di lunghezza delle righe, la prima riga di una pagina non riprende l'ultima della pagina prima (+0,001), né la prima riga di un paragrafo l'ultima del paragrafo prima (+0,007), mentre dentro il paragrafo la ripresa dalla riga sopra vale circa +0,04 per parola. Nessuna differenza fra pagine affiancate e stesso foglio: niente copia dalla pagina accanto.
  - La copia dalla riga sopra è quasi sparsa, parola per parola, non a righe intere (e3b29: righe con metà o più parole riprese 21,0% contro 19,4% con copia sparsa alla stessa media; esito incerto).
  - Dalla riga sopra si riprendono in proporzione di più le parole rare (e3b30: eccesso relativo +31% per le parole che compaiono 2–9 volte, +15% per le frequenti): coerente con una copia a vista delle forme insolite appena scritte.
  - Anche la memoria corta nella riga favorisce le forme rare (e3b31: eccesso relativo +40% per le rare, +8% per le frequenti); le parole uniche hanno una "sorella" a una modifica fra le 4 parole appena prima il 72% più spesso del caso: molte parole uniche nascono come variazione di una parola appena scritta nella stessa riga (non dalla riga sopra, e348).
