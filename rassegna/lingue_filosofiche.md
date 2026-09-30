# Rassegna R1: il Voynich come lingua filosofica (lingua artificiale "a priori")

Scritta il 30/09/2026, prima di qualsiasi esperimento su questa ipotesi. Serve a fissare che
cosa l'ipotesi dice e che cosa prevede, prima di guardare i dati nuovi.

Legenda delle fonti:

- **[letta]**: fonte primaria letta per intero o nella parte citata; copia in
  `dati/cache/letteratura/` con SHA-256 in `dati/FONTI.md`.
- **[di seconda mano]**: nota solo attraverso un'altra fonte, indicata.
- **[non verificata]**: citata da altri, non raggiunta.

## 1. L'ipotesi e la sua storia

**Lingua filosofica, o lingua "a priori".** È una lingua costruita in cui la forma della parola
viene da una classificazione dei concetti, non dall'uso:

- una parte indica il genere (la categoria);
- una parte la differenza e la specie;
- una parte le forme grammaticali.

Gli esempi classici sono del Seicento:

- Dalgarno, *Ars signorum* (1661): venti classi indicate da lettere maiuscole;
- Wilkins, *An Essay towards a Real Character and a Philosophical Language* (1668): quaranta
  generi, con differenze e specie aggiunte alla radice.

Il manoscritto è datato al radiocarbonio 1404–1438. Se l'ipotesi è vera, deve trattarsi di un
precursore di più di due secoli prima.

**William F. Friedman** [di seconda mano, da Tiltman 1967 e D'Imperio 1978].

- **Anni '40.** Riunisce un gruppo di studio, che nel 1944 esamina la lingua di Wilkins.
  D'Imperio riporta che quegli studi trovarono inizi e fini di parola, frequenze delle lettere,
  numero di simboli diversi e lunghezze delle parole «comparabili» a quelle del Voynich
  (D'Imperio 1978, §6.2).
- **La conclusione.** Friedman arrivò a pensare che il testo non fosse un cifrario ma «una forma
  molto primitiva di lingua universale sintetica», del tipo della classificazione filosofica
  di Wilkins.
- **L'anagramma.** Nascose la conclusione in un anagramma, sciolto dopo la sua morte; D'Imperio
  dice che il contenuto era ormai noto (§6.5). Il testo esatto dell'anagramma sciolto è
  **[non verificato]** alla fonte.

**John H. Tiltman**, *The Voynich Manuscript: "The Most Mysterious Manuscript in the World"*,
conferenza del 1967, NSA Technical Journal 12 [letta, DOCID 631091].

- **L'analisi fatta a mano.** È la prima descrizione della struttura interna delle parole:
  - parole divise in "radici" e "suffissi";
  - ogni simbolo ha un suo «ordine di precedenza» dentro la parola;
  - i gruppi finali in A e O hanno frequenze proprie, costanti in tutto il manoscritto.
- **Tre osservazioni che ritroviamo nei nostri dati:**
  - «uno spazio non va necessariamente considerato un segno di divisione fra due parole o
    concetti» (§i): le nostre giunture morbide, e12;
  - parole comuni che compaiono «due volte di seguito, a volte tre» (§k): le nostre ripetizioni
    immediate, e02;
  - niente ripetizioni lunghe di più di 2–3 parole (§o).
- **La sua conclusione.** Il testo non può essere una sostituzione di lettere nell'ordine
  naturale: «le lingue semplicemente non si comportano così» (§o).
- **Le obiezioni a Wilkins e Dalgarno.** Tiltman le giudicò «troppo sistematiche»: una cosa del
  genere si riconoscerebbe «quasi subito». Il Voynich gli pareva piuttosto «una mescolanza
  macchinosa di tipi diversi di sostituzione».
- **Cave Beck.** Trovò un precedente macchinoso di questo tipo, *The Universal Character* (1657):
  - circa 4.000 parole di un dizionario inglese numerate in ordine alfabetico;
  - lettere prefisse per sostantivo (R) e aggettivo (Q);
  - S per il plurale;
  - un separatore obbligatorio dopo ogni parola.
  - Tiltman si chiese se le terminazioni EVA corrispondenti a G e 8G siano "virgola" e
    "virgola plurale".
  - Beck **[di seconda mano]**.

**Mary D'Imperio**, *The Voynich Manuscript: An Elegant Enigma*, NSA 1978 [letta nell'OCR di
archive.org, DTIC ADA070618; §6.5, 6.6, 7, 9.2, 9.3].

- **L'ipotesi che giudica più probabile** (sezione sulle ipotesi, codice PA + E.7):
  - un codice su un piccolo glossario di qualche centinaio di parole latine (piante, medicina,
    astronomia, tempo);
  - la radice scritta con 1–3 simboli, che indicano una pagina o colonna del glossario, oppure
    «una categoria filosofica, come era usuale nelle prime lingue universali»;
  - le forme grammaticali scritte dalle serie finali descritte da Tiltman;
  - varianti di lunghezza diversa per radici e affissi, e nulle.
- **Un'aggiunta che ci interessa molto.** Per riempire le righe fra le parole che portano il
  messaggio, lo scriba «tenderebbe naturalmente a ripetere parti di stringhe vicine con piccoli
  cambiamenti». È, in germe, l'autocitazione di Timm e Schinner, ma messa al servizio di un
  codice.
- **Il precedente d'epoca.** Il sistema di Jakob Silvester (1526; l'OCR legge «1426»), un
  cifrario della corte papale:
  - colonne di un dizionario latino indicate con numeri romani o con digrammi;
  - parole indicate con numeri arabi;
  - desinenze latine scritte con lettere singole o digrammi;
  - nulle sparse.
  - D'Imperio lo ritiene «potenzialmente la base» del testo. Silvester **[di seconda mano]**.
- **Le radici.** Ne cerca le origini nell'*ars memorativa* e nell'arte combinatoria di Ramon
  Llull (XIII secolo), con cerchi rotanti per combinare concetti (§9.3). Llull **[di seconda
  mano]**.
- **Perché il tema conta** (§9.3). Le prime lingue universali hanno questa struttura:
  - radice per la classe;
  - uno o più caratteri per la specie;
  - caratteri per le forme grammaticali.
  - Secondo D'Imperio questa struttura «concorda molto bene con la struttura inizio–centro–fine
    trovata da Tiltman».

**Lingua Ignota** di Ildegarda di Bingen (XII secolo). È l'unica lingua costruita **medievale**
sopravvissuta con un lessico.

- **Il lessico.** È un glossario di 1.011 parole, quasi solo nomi, con glosse latine e a volte
  tedesche. È ordinato per categorie secondo la *scala naturae*:
  - Dio e angeli;
  - persone, parentele, parti del corpo, malattie;
  - ranghi e mestieri;
  - tempo, vestiti, casa;
  - piante, uccelli, insetti.
- **Formazione delle parole.** Ci sono esempi di composizione e derivazione (*peueriz* "padre" →
  *hilz-peueriz* "patrigno") [di seconda mano, Wikipedia].
- **Le fonti.**
  - Edizione Roth (1880) **[non verificata]**.
  - Glossario ricompilato da un amatore a partire da Roth, con il numero d'ordine originale di
    ogni voce (archivio Wayback del 20/08/2012) [letta: la struttura; SHA-256 in `FONTI.md`].
  - Le cautele sono quelle dichiarate dal compilatore stesso.
- **Non è una lingua filosofica in senso stretto:** la forma della parola non si ricava dalla
  classificazione. Ma è **il confronto d'epoca giusto**, perché mostra come una persona colta del
  Medioevo costruiva parole nuove per categorie.

**Lavori recenti rilevanti.**

- **Rozanova e Temerev 2026** (arXiv 2608.17096) [letta].
  - Confrontano le unità imparate con il BPE con la grammatica a slot di Zattera (2022) e con
    quella "crust–mantle–core" di Stolfi (2000). Queste due grammatiche sono **[non verificate]**.
  - Non trattano esplicitamente le lingue filosofiche.
  - Le loro misure sono però le stesse su cui l'ipotesi va messa alla prova: ordine delle parole
    debole, legame forte ai bordi delle parole, vocabolario ricco di parole uniche.
- **Turenne 2026**, «Pastiche hypothesis» (arXiv 2609.20835) [letto il riassunto]. Propone un
  «sistema generativo strutturato» che imita gli erbari. Da leggere prima della stesura finale.
- **Wilkins 1668 e Dalgarno 1661** [non verificati alla fonte]. Descrizioni da D'Imperio §9.3.

## 2. Che cosa prevede l'ipotesi

Serve una distinzione, perché le previsioni si dividono nettamente:

- **(F-prosa)** Una lingua filosofica usata per scrivere **testo corrente** (trattati, istruzioni).
- **(F-elenco)** Una lingua filosofica usata per scrivere **nomi ed elenchi**: etichette, nomi di
  piante e di stelle, elenchi di proprietà.

Il ragionamento centrale viene dall'e07. Un codice che sostituisce ogni parola del testo in
chiaro con una parola in codice, qualunque sia la forma della parola in codice, conserva l'ordine
delle parole del testo in chiaro:

- conserva quindi il fatto che la grammatica evita di ripetere subito una parola;
- tutte le codifiche provate stanno fra ×0,1 e ×0,5 di ripetizioni immediate, contro ×1,0 del
  Voynich.

Una lingua filosofica usata come prosa è, statisticamente, un codice parola per parola con parole
in codice ben strutturate. Il vincolo vale anche per lei.

## 3. Rilettura dei risultati già ottenuti (e01–e28)

| proprietà (esperimento) | Voynich | previsione F-prosa | previsione F-elenco | stato |
|---|---|---|---|---|
| h2 bassa (e01) | 2,22 bit | bassa: pochi pezzi in posizioni fisse | bassa | **compatibile** con entrambe (così anche il gruppo di Friedman, 1944) |
| spazio prevedibile dal segno precedente (e11) | 66% | alto: le desinenze sono un insieme chiuso | alto | **compatibile** |
| struttura a posizioni dei segni (Tiltman; e18: ordine al 78,5%) | c'è | c'è | c'è | **compatibile**, ma non discrimina: anche il generatore e il Naibbe l'hanno |
| parole uniche (e22, e24, e28) | 68% | alte: le combinazioni classe × specie × desinenza sono moltissime | alte | **a favore**: è proprio la proprietà che il generatore di Timm e Schinner (51–54%) e il Naibbe (37–44%) non raggiungono |
| ripetizione immediata (e02, e07) | ×1,0 | ×0,1–0,5, come ogni codice parola per parola | libera: gli elenchi possono ripetere (Tiltman §k) | **contraddice F-prosa**; F-elenco da provare, e i testi a elenco provati nell'e21 ripetevano *meno* della prosa (×0,00–0,07) |
| ordine delle parole: l'identità predice la successiva (arXiv, tab. 3) | 0,79% | 2–10%, come la prosa | catalogo di Linneo: 15,8% | **contraddice F-prosa e contraddice il catalogo di Linneo**; F-elenco resta possibile solo per elenchi senza struttura ripetitiva interna |
| legame fine–inizio (e11) | 0,19 bit | possibile: accordo fra la desinenza di una parola e la classe della successiva | possibile | **compatibile**, da precisare |
| omogeneità di pagina graduata (e04, e05) | 3,8% → 3,4% | pagina con un argomento → parole con le stesse classi → stessi prefissi | idem | **potenzialmente a favore**: un meccanismo nuovo per l'omogeneità, da provare (e36) |
| unioni di parole vicine attestate (e11, e12) | 9,2% | possibile se desinenze e particelle a volte si staccano | idem | **compatibile** |
| etichette dello zodiaco (e15) | quasi tutte diverse; deriva di stile regolare | — | stessa classe ("stella", "grado") → stesso inizio | **da provare**: Tiltman nota che le didascalie astronomiche cominciano spesso con gli stessi simboli (OD/OH nel suo alfabeto) |

**Sintesi della rilettura.**

1. **F-prosa è già in difficoltà** per le stesse ragioni di ogni codice parola per parola:
   ripetizione immediata ×1,0 e ordine delle parole sotto l'1%.
2. **F-elenco non è esclusa.** Spiega bene tre cose che il generatore senza messaggio non spiega:
   - le parole uniche;
   - la struttura a posizioni;
   - forse l'omogeneità di pagina.
   - Ha però due vincoli: gli elenchi veri provati finora non ripetono le parole vicine, e il
     catalogo di Linneo ha un ordine delle parole forte.
3. **L'ibrido di D'Imperio** (codice per categorie + riempitivi copiati dalle parole vicine) è una
   quarta possibilità che mette insieme le ipotesi 1 e 3:
   - le parole del codice darebbero il vocabolario aperto;
   - i riempitivi darebbero le ripetizioni e l'omogeneità.
   - Si può rendere concreta in un generatore e mettere alla prova con la lista di controllo.

## 4. Esperimenti che ne discendono

Numeri dal piano. Le preregistrazioni andranno in `preregistrazioni/`.

- **e36 – Dove sta l'omogeneità di pagina nella parola.**
  - Se F è vera, l'eccesso di somiglianza fra parole della stessa pagina sta nel **primo pezzo**
    della parola, cioè nella classe.
  - Se è vera l'autocitazione, sta dove agiscono le regole di ritocco.
  - Se sono vere le convenzioni di pagina (ipotesi 2), sta su sostituzioni specifiche.
  - Controllo positivo: codice a prefisso semantico sintetico applicato a latino vero.
- **e37 – Prefissi e tipo di illustrazione.**
  - Se F è vera, la distribuzione dei primi pezzi dipende dal soggetto (piante, stelle,
    recipienti, figure) oltre quanto spiegano lingua di Currier, mano e fascicolo.
  - La dipendenza deve essere più forte nelle **etichette**, che sono nomi.
- **e38 – La Lingua Ignota come confronto d'epoca.**
  - Le parole della stessa categoria di Ildegarda condividono inizi o fini più del caso?
  - Se nemmeno una lingua costruita medievale per categorie lo fa, la previsione di e36 ed e37
    va presa come tipica della lingua filosofica "matura" del Seicento e non del Quattrocento.
- **Da aggiungere: e39 – L'ibrido di D'Imperio.**
  - Un generatore che alterna parole di un codice per categorie (da un elenco latino vero) e
    riempitivi per autocitazione.
  - Lo si misura sulla lista di controllo, cercando la regione di parametri che dà insieme parole
    uniche al 68% e ripetizioni ×1,0.

## 5. Riferimenti

- Tiltman, J. H. (1967). *The Voynich Manuscript: "The Most Mysterious Manuscript in the
  World"*. NSA Technical Journal 12(3). Declassificato nel 2002, DOCID 631091. Copia da Wayback
  Machine, perché nsa.gov blocca i download automatici.
- D'Imperio, M. E. (1978). *The Voynich Manuscript: An Elegant Enigma*. NSA/CSS. Copia DTIC
  ADA070618 su archive.org.
- Rozanova, L. e Temerev, A. (2026). *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is
  Not a Space*. arXiv:2608.17096.
- Turenne, N. (2026). *A Generative Grammar Underlying the Voynich Manuscript, the Pastiche
  Hypothesis*. arXiv:2609.20835 (letto il riassunto).
- Wilkins, J. (1668); Dalgarno, G. (1661); Beck, C. (1657); Silvester, J. (1526); Llull, R.:
  **di seconda mano**, attraverso Tiltman 1967 e D'Imperio 1978.
- Ildegarda di Bingen, *Lingua ignota per simplicem hominem Hildegardem prolata*. Edizione Roth
  (1880) **non verificata**. Glossario ricompilato da Roth, archivio Wayback
  `web.archive.org/web/20120820002300/http://www.unmasqued.com/eclecticify/ignota.php`.
