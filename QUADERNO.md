# Quaderno di laboratorio

Voci datate, in ordine. Si aggiunge e non si riscrive: se una voce si rivela sbagliata, la
correzione è una voce nuova che la cita. Ogni voce dice che cosa si è fatto, perché, che
cosa si è scartato, com'è andata e con quale commit. Le scelte di metodo più importanti
hanno una voce anche in `DECISIONI.md` (D-nnn). Il lavoro è condotto con Claude Code
(Anthropic, modello Claude Opus 5.5) su indicazione di Davide Caniatti.

---

## 30/09/2026 — Ripartenza in un repository nuovo

**Che cosa.** Nuovo repository in `C:\Users\david\voynich`, fuori da OneDrive, perché la
sincronizzazione di OneDrive e le cartelle `.git` non convivono bene e la cache dei corpora
pesa circa 1 GB. Il primo commit (`ee2a23d`, tag `origine`) importa **così com'è** la cartella
`voynich/` del lavoro precedente: `AndreottiVIII/duri-a-morire`, ramo
`claude/voynich-decipherment-mwvrge`, commit `f57f067`.

**Perché importare invece di riscrivere.** I 28 esperimenti sono la base del white paper.
Riscriverli costerebbe molto e poi bisognerebbe riconciliare i numeri. Importarli e rieseguirli
dà invece una prova di replica: stesso codice, altro sistema operativo, altre versioni delle
librerie.

**Intoppo 1: i fine riga.** Git su questo PC ha `core.autocrlf=true` a livello di sistema. Il
checkout ha convertito LF in CRLF in 66 file su 128, e le impronte SHA-256 delle trascrizioni
non coincidevano più con `dati/FONTI.md`. Corretto riportando tutto a LF. Verifica: i 128 file
coincidono con i blob originali (`git hash-object`) e le tre trascrizioni hanno di nuovo le
impronte pubblicate. Da qui `.gitattributes` con `* -text` e le variabili git in `esegui.py`
(D-001).

**Intoppo 2: il Naibbe su Windows.** Il repository `greshko/naibbe-cipher` contiene file il cui
nome ha il carattere `\`: Windows non li può creare e git va in crash (segmentation fault)
anche solo configurando lo sparse checkout. Soluzione:
- scaricare solo le cartelle usate (`references`, `encrypted`, `decrypted`, `input`,
  `respaced_plaintext`);
- `core.protectNTFS=false` limitato a quel checkout: fuori dalle cartelle scelte non si scrive
  niente.

Il commit resta `f2675ec`.

**Nota a margine, utile più avanti.** I file problematici sono in
`figure_utils/gaskell_bowern_2022/` e contengono i testi "gibberish" scritti a mano da
volontari nello studio di Gaskell e Bowern (2022, *Gibberish after all?*). Sono un confronto
prezioso per l'ipotesi "senza messaggio": testo senza significato prodotto da persone, non da un
algoritmo. Si possono estrarre con `git show` e rinominare.

**Ambiente.** Due scelte:
- Python 3.12.10 in `.venv`, pacchetti alle ultime versioni e fissati (D-004);
- JDK Temurin 21.0.12.1 portabile in `C:\Users\david\tools`, scaricato da Adoptium, SHA-256
  dello zip `f9d6e191…d8b4e`.

Tutti i corpora sono ai commit di `FONTI.md` (109 lingue pronte).

**Esecuzione.**
- `esegui.py` fissa il seme di hash, la codifica e i fine riga, e registra la provenienza di
  ogni esecuzione in `risultati/provenienza/` (D-002, D-003).
- `verifica_replica.py` confronta ogni `.json` con quello del tag `origine`.

## 30/09/2026 — Lettura di arXiv 2608.17096 (Rozanova e Temerev)

Il testo intero questa volta si raggiunge. La sessione precedente aveva letto solo il
riassunto. Il PDF e il testo estratto sono in `dati/cache/letteratura/`; SHA-256 del PDF
`8743a900…8d4d`. Punti rilevanti per noi.

- **Coerenze con il dossier.**
  - Legame fra ultimo segno e primo segno della parola seguente: loro 0,197 bit, noi 0,19.
  - Parole uniche: loro 69,7%, noi 68%.
  - Gli spazi incerti sono giunture interne alle parole: loro indice 0,49 contro 0,03, noi e12.
  - Né il Naibbe né il generatore di Timm e Schinner riproducono il legame fra le parole e le
    parole uniche. È la stessa conclusione del dossier, arrivata per altra via e con implementazioni
    indipendenti.
- **Differenza da capire: h2.** Loro 2,7 bit, noi 2,2. Loro tolgono spazi e a-capo e fondono
  anche `iin`, `in` ed `ee`; noi teniamo lo spazio come simbolo. Da riconciliare in un
  esperimento breve, calcolando h2 con la loro ricetta sul nostro codice.
- **Dati riusabili.**
  - Il loro repository `github.com/lrozanova/voynich-units` (snapshot analizzato `66f8ada`,
    raggiungibile) contiene le coordinate per parola di voynichese.com sulle immagini della
    Beinecke. Con queste l'e34 (larghezza fisica degli spazi) non deve ricavare le coordinate
    dalle immagini da zero.
  - Loro hanno già mostrato che gli spazi incerti sono fisicamente più stretti (AUC 0,905). Il
    nostro contributo nuovo può essere un altro: le giunture **morbide e dure dell'e12, tra gli
    spazi certi**. Se anche fra spazi segnati certi la larghezza dipende dal tipo di giuntura, lo
    spazio è graduato e non binario.
- **Un confronto che ci mancava: il catalogo di Linneo.** Le voci di *Species Plantarum*:
  - hanno parole vicine quasi uguali più spesso del caso (×2,57), come il Voynich (×1,12);
  - hanno un legame fra le parole molto forte (0,32 bit);
  - ma l'identità di una parola predice molto la successiva (15,8% contro 0,79%).
  - Per l'ipotesi 1 (contenuto a elenco) è il tipo di controllo da usare nell'e30. Il catalogo
    somiglia al Voynich nei bordi delle parole ma non nell'ordine delle parole.

## 30/09/2026 — Replica di e01

- **Esito:** tutti i 2.351 valori in comune coincidono entro 1e-9 relativo (scarto assoluto massimo
  1e-11). Le differenze sono nell'ultima cifra dei numeri in virgola mobile: la libreria matematica
  di Windows non è quella di Linux.
- **Due differenze spiegate.**
  - Il `.json` nuovo ha una lingua in più (cinese in pinyin). Nel lavoro precedente il pinyin è
    stato aggiunto al corpus dopo l'ultima esecuzione di e01.
  - Il `.md` nuovo ha gli accenti al posto degli apostrofi. Anche lo script era stato ritoccato
    dopo quell'esecuzione.
  - Quindi i risultati importati non sempre vengono dall'ultima versione del codice. La replica
    serve anche a questo.
- **Errori di procedura miei.**
  - I risultati di e01 sono finiti per sbaglio nel commit `fe096d7` (una modifica a `esegui.py`,
    fatta con `git commit -a`). Da allora i file si aggiungono sempre per nome.
  - Il primo gruppo di repliche (e01–e06) è partito con la versione iniziale di `esegui.py`. In
    quella versione:
    - l'elenco `file_scritti` della provenienza include file di altri esperimenti girati in
      parallelo (e36, e38, e39);
    - il commit registrato è quello della fine dell'esecuzione, non dell'inizio.
    - Gli script di e01–e06 però non sono cambiati dal tag `origine`, come mostra la loro impronta
      nella provenienza, quindi i risultati non ne risentono.

## 30/09/2026 — e39: h2, la ricetta di Rozanova e Temerev

- **Preregistrata** (`preregistrazioni/e39.md`, commit `dc48734`) e confermata.
- **Con la loro ricetta:**
  - si tolgono spazi e a-capo;
  - si fondono cth ckh cph cfh ch sh iin in ee;
  - il nostro codice dà **2,698 bit** (loro 2,7) e il latino 3,47 (loro circa 3,5).
- **Con la nostra ricetta:** 2,24.
- **In ogni ricetta** il Voynich sta almeno 0,73 bit sotto latino, italiano e inglese.
- **Conclusione.** I due numeri non si contraddicono: cambia il modo di contare, non il fenomeno.
  Nel white paper conviene citarli entrambi, dicendo come sono stati calcolati.
- **Nota.** Isidoro XVII e Columella XII sono troppo corti per il confronto alla pari: 190.000
  simboli richiesti.

## 30/09/2026 — Lingue filosofiche: e36, e37, e38, e40

**Prima degli esperimenti:**

- rassegna R1 (`rassegna/lingue_filosofiche.md`), costruita sulle fonti primarie di Tiltman 1967 e
  D'Imperio 1978;
- decisioni D-005 (e29 riformulato) e D-006 (misura per posizione);
- preregistrazione `e36-e38.md`.

**Deviazione D-007.** Una prova del codice ha mostrato che il controllo positivo preregistrato di
e36 aveva un difetto: la numerazione per prima comparsa porta informazione sulla pagina nel
secondo segno. Nella prova avevo visto anche i numeri del Voynich. Ho dichiarato la deviazione
prima della corsa ufficiale e riporto entrambe le versioni; le soglie per il Voynich non sono
cambiate.

**e36 — l'informazione sulla pagina, per posizione.**

- **Controlli validi:** prefisso semantico R = 10,0; codice casuale R = 0,75.
- **Voynich: R = 0,98** (0,90–1,02 togliendo un fascicolo per volta), con informazione forte
  (z = 27) ma uguale in tutte le posizioni. Currier B 1,03; Currier A 0,76 (solo 24 pagine).
- **Per il criterio preregistrato, contro la lingua filosofica a prefisso di classe.**
- **Naibbe:** nessuna informazione di pagina. È un cifrario uniforme, come nell'e10.
- **Generatore di Timm e Schinner:** R = 0,72–0,78, con un picco al penultimo segno.
- **Esplorativo, a parità di stratificazione:** il generatore ha 2–3 volte più informazione di
  pagina del Voynich (quote 0,06–0,11 contro 0,03–0,04). Le sue pagine sono più "chiuse", in
  accordo con le poche parole uniche.

**e38 — Lingua Ignota (esplorativo).**

- 731 voci del glossario. L'informazione sulla categoria sta più **in fondo** alla parola:
  R = 0,55; ultima lettera 0,063, prima 0,033.
- Esempi: gli alberi in *-buz* (*zirumzibuz* pero, *sparinichibuz* pesco), le parti del corpo in
  *-zia*, i libri in *-libiz*. È il modello dei composti germanici, con la testa in fondo.
- **Conseguenza.** Una lingua costruita medievale **non** mette la classe nel prefisso, come
  faranno Wilkins e Dalgarno nel Seicento. Il criterio "R > 2" di e36 ed e37 prende quindi la
  variante seicentesca. La variante medievale (classe in coda) prevederebbe R < 0,5, e il
  Voynich (0,98) non mostra nemmeno quella.
- **Qualità della fonte:** amatoriale. Per esempio #0005 *diabolus* riporta la parola di #0004;
  lasciata com'è per non correggere a mano solo dove fa comodo.

**e37 — l'informazione sulla sezione, per posizione.**

- Scelta dichiarata prima dell'esecuzione: pagine con almeno 10 parole utili.
- **Controlli validi:** 19,5 e 0,55.
- **Paragrafi: R = 1,57**, ma instabile (1,02–2,47). Dipende dal fascicolo T (ricette); senza T
  scende a 1,02.
- **Etichette: R = 3,24.** L'informazione al primo segno (0,044) è il doppio di quella del testo.
- **Rispetto alla preregistrazione:** per il testo né la conferma di F (R > 2) né il criterio
  contro (R ≤ 1,5 **e** etichette con primo ≤ ultimo). Per le etichette, previsione F
  soddisfatta.
- **Analisi secondaria.** L'informazione al primo segno è distribuita su molti segni, non su una
  sola alternanza:
  - Currier A: k-, a-, q-, d-, o-;
  - Currier B: y-, q-, sh-, l-, a-;
  - etichette: s- in farmacia 52% contro 23%.

**e40 — il tipo di oggetto a parità di pagina (preregistrato, `e40.md`).**

- **Farmacia, recipienti contro frammenti:** differiscono nell'**ultimo segno**, p = 0,003,
  potenza stimata 0,74. Supera anche la correzione per 6 test.
  - I recipienti hanno più -d, -n, -g; i frammenti più -r, -l, -m. Le etichette dei recipienti
    sono più lunghe (6,7 segni contro 5,4).
  - **Esplorativo:** l'effetto resta a parità di pagina **e** di lunghezza (p = 0,003–0,004);
    quello sul primo segno no.
- **Biologica e astronomia:** nulle, ma con potenza bassa (0,17–0,54), quindi non informative.
- **Lettura prudente.** Per la preregistrazione l'esito va contro un generatore che non sa che cosa
  etichetta. Resta però un'alternativa non esclusa: se lo scriba ha scritto le etichette **per
  lotti di tipo** (prima tutti i recipienti, poi i frammenti), anche l'autocitazione raggrupperebbe
  le terminazioni per tipo.
  - Per distinguere servirebbe l'ordine di scrittura (dalle immagini: inchiostro, sovrapposizioni)
    oppure una simulazione del generatore con etichette scritte a lotti.
  - Da fare.

**Bilancio sulle lingue filosofiche.**

- **Nel testo corrente:**
  - nessuna concentrazione dell'informazione né all'inizio (stile Wilkins) né alla fine (stile
    Ildegarda);
  - F-prosa era già in difficoltà per le ripetizioni immediate e l'ordine delle parole.
- **Nelle etichette:** ci sono segni di marcatura per tipo di oggetto, in coda nella farmacia,
  che resta la pista aperta (F-elenco o un sistema di nomi). Ma l'alternativa "lotti" va chiusa
  prima di dire di più.

## 30/09/2026 — e41: il gibberish umano (Gaskell e Bowern 2022)

- **Dati.** 38 documenti di testo senza senso scritti a mano da volontari (79–482 parole), estratti
  con `git show` dal repository del Naibbe, perché su Windows non si possono scrivere i loro nomi
  di file. Licenza MIT modificata con obbligo di citazione.
- **Preregistrato** (`e41.md`).
- **M1, ripetizione immediata:** gibberish **0,71** (per documento mediana 0,56, da 0 a 2,61);
  Bibbia inglese 0,05, latina 0,32; Voynich 1,01. Previsione dell'ipotesi 3 soddisfatta: chi
  scrive a caso ripete la parola precedente, come il Voynich.
- **M2, somiglianza graduata fra righe dentro il documento:** gibberish pari al latino e piatto
  (d = 1: 0,003–0,008 al 95%); Voynich 0,008–0,011, che cala con la distanza. Previsione non
  soddisfatta.
- **M3, legame fine–inizio:** gibberish 0,009 bit, **meno** delle lingue (inglese 0,079, latino
  0,031); Voynich 0,188.
- **Lettura.** Una persona che scrive senza senso "come viene" produce la ripetizione immediata ma
  non le altre due anomalie. Per l'ipotesi 3 serve dunque una procedura con regole
  (autocitazione, giunture), non basta la glossolalia.
- **Limiti.** Documenti corti, scrittori moderni, una sola seduta.

## 30/09/2026 — e34: gli spazi certi sono graduati (immagini, via le coordinate di voynichese.com)

- **Preregistrato** (`e34.md`).
- **Dati.** 204 fogli; 23.378 spazi allineati fra i riquadri di voynichese.com e la ZL.
- **Validità.** Gli incerti sono più stretti dei certi di 0,113 (larghezza normalizzata; z = 21).
  Replica Rozanova e Temerev (0,124).
- **Primaria, nuova.** Fra gli spazi **certi**, a parità dei due segni ai lati (36 strati, 12.197
  spazi), lo spazio è più stretto di **0,031** quando le due parole unite danno una parola scritta
  attaccata altrove; z = 3,9, p = 0,0025. È circa un quarto della larghezza media.
- **Secondaria.** Giunture morbide 0,080, intermedie 0,120, dure 0,144 (senza controllo per la
  forma dei segni).
- **Lettura.** Lo spazio è una grandezza graduata anche dove il trascrittore lo vede netto, e
  segue le unità del sistema: i pezzi che formano un'unità nota stanno fisicamente più vicini.
  Questo va con l'ipotesi 2 (gli spazi non separano parole del testo in chiaro), ma è compatibile
  anche con uno scriba che compone pezzi senza messaggio.

## 30/09/2026 — e33 ed e35: immagini, e le piante della farmacia ritrovate nell'erbario

- **e33.** Manifest IIIF di Yale (213 canvas; "Access: Public"). Scaricate 25 immagini a 1.500
  pixel, registrate con impronta in `dati/immagini.json`. Intoppo: due canvas hanno la stessa
  etichetta "102v (part)"; e33 corretto per non sovrascriverli.
- **e35, preregistrato.**
  - La ZL riporta 13 corrispondenze erbario → farmacia (Petersen, Stolfi, FSG, GL).
  - Associazione frammento → etichetta **fatta sulle immagini e registrata con commit prima del
    confronto** (`dati/corrispondenze_farmacia.json`).
  - Tenute 7 coppie; scartate 7, di cui 4 perché il frammento non ha etichetta e 2 perché
    l'etichetta non è chiaramente sua.
  - **Esito nullo:** media dei quantili 0,476 (p = 0,41); per le 2 coppie senza "?" 0,557.
  - Nessuna delle 5 etichette distinte compare in una pagina d'erbario.
- **Lettura.** Con 7 coppie (di cui due doppie) la potenza è bassa, come dichiarato, e il nullo
  non esclude il contenuto. Resta però un dato: le etichette dei frammenti non ricorrono nel testo
  dell'erbario, nemmeno sulla pagina della stessa pianta.
- **Mio giudizio nell'associazione.** Il conteggio [riga, colonna] è ambiguo quando le etichette
  stanno fra un frammento e l'altro. Ho applicato la regola di scarto preregistrata invece di
  scegliere.

## 30/09/2026 — Repository su GitHub

Creato `github.com/AndreottiVIII/voynich`, **privato** (la decisione di pubblicarlo spetta a
Davide), con `gh` (è in `C:\Program Files\GitHub CLI`, non nel PATH della shell Bash). Caricati
il ramo `main` e il tag `origine`.

## 30/09/2026 — Repliche e07, e08, e10, e11, e12, e15

Stessi valori. Quattro valori sembravano diversi con la soglia relativa di 1e-9, ma erano
numeri vicini a zero con scarto assoluto di circa 3e-13. `verifica_replica.py` ora considera
diversi solo i valori che superano **anche** una soglia assoluta di 1e-12.

## 30/09/2026 — e30: glossari medico-botanici medievali e catalogo di stelle

- **Preregistrato** (`e30.md`), con le regole di pulizia degli OCR fissate prima.
- **Testi:**
  - *Alphita* (Mowat 1887): 37.408 parole, inglese residuo 0,38%;
  - *Sinonoma Bartholomei* (Mowat 1882): 7.920 parole, 0,23%;
  - Igino III (catalogo di stelle): 3.872 parole;
  - Igino II (prosa).
- **Misure su pagine finte da 8×20:** nessun testo a elenco ripete la parola precedente
  (0,05–0,15 contro 0,94 del Voynich sulle stesse pagine finte) né ha righe omogenee (≤ 1,3% contro
  4,1%). **Esito contro l'ipotesi 1 per il criterio preregistrato.**
- **Osservazioni:**
  - i glossari hanno **molte parole uniche** (73–77%), come il Voynich (68%) e più del generatore
    senza messaggio (51–54%);
  - il legame fine–inizio è basso in chiaro (0,03–0,10) e il codice parola per parola lo azzera;
  - l'ordine fra parole vicine è alto nei cataloghi (Igino III 0,57 bit), come nel Linneo di
    Rozanova e Temerev.
- **Lettura.**
  - Gli elenchi veri spiegano il vocabolario aperto ma non le ripetizioni né l'omogeneità.
  - Insieme all'e21 (elenchi biblici, *Notitia*, *Fasti*) e all'e25 (litanie), i generi non in
    prosa provati sono ormai molti e nessuno ha le due anomalie.
  - L'ipotesi 1, in forma pura, perde terreno.

## 30/09/2026 — e13 non si replica, per una buona ragione

- **Che cosa.** e13 (il Voynich sul profilo di nove misure, contro le lingue) legge i risultati di
  e01, e02, e09 ed e11. Il nuovo e01 contiene una lingua in più, il cinese in pinyin (84 → 85
  lingue), e i numeri cambiano:
  - distanza del Voynich dalla lingua più vicina: 9,87 → **9,24**; senza l'omogeneità di pagina
    5,51 → **4,39**;
  - distanza massima fra una lingua e la sua vicina: 4,06 → **6,64**; senza omogeneità 4,06 →
    **6,63**.
- **Conseguenza per il white paper.** La frase del dossier "il Voynich è più isolato di qualsiasi
  lingua" regge **solo con l'omogeneità di pagina** (9,2 contro 6,6). Senza, il Voynich (4,4) è
  meno isolato della lingua più isolata del campione allargato.
  - Va verificato quale lingua dà 6,6: con buona probabilità il pinyin, che è una trascrizione di
    una scrittura logografica.
  - Va deciso se tenerlo nel confronto: nel dossier le lingue erano "in alfabeto o abjad".
  - È una decisione da prendere e da registrare (D-008 da scrivere), non da aggiustare in silenzio.

## 30/09/2026 — e31: Naibbe con convenzioni che derivano (ipotesi 2)

- **Preregistrato.** 16 combinazioni (σ × ρ × 2 testi).
- **Somiglianza:** la deriva la fa calare con la distanza, ma arriva al massimo al 2,3% (Voynich
  3,8%).
- **Tutte le combinazioni:**
  - ripetizione 0,37–0,49;
  - legame fine–inizio ≤ 0,005 bit;
  - parole uniche 42–46%.
- **Lettura.** Previsioni (b) e (c) confermate: la variante "cifrario con convenzioni che derivano"
  dell'ipotesi 2 spiega al più una delle anomalie. Resta aperta la variante in cui gli spazi non
  separano parole del testo in chiaro con giunture morbide, e non solo le tabelle che derivano.

## 30/09/2026 — e42: etichette della farmacia, classe o lotti?

- **Preregistrato.** Controlli validi: i lotti sono riconosciuti nel 100% delle simulazioni; per la
  classe i falsi positivi sono il 6%.
- **Voynich.** Il corpo delle etichette (senza l'ultimo segno) **non** si somiglia per tipo dentro
  la pagina (D = −0,009, p = 0,71). Per la preregistrazione l'esito si accorda con la marcatura per
  classe.
- **Ma** il controllo di coerenza sull'ultimo segno, a coppie dentro la pagina, non ritrova
  l'effetto di e40 (p = 0,67).
- **Lettura prudente.**
  - L'e40 rileva una differenza di **distribuzione** delle terminazioni fra recipienti e frammenti,
    sommata su 12 pagine, e 9 pagine su 12 vanno nella stessa direzione.
  - Non c'è però una somiglianza a coppie fra etichette dello stesso tipo sulla stessa pagina.
  - La spiegazione "lotti" è sfavorita; quella "classe marcata" è possibile ma il segnale è debole
    (36 recipienti).
  - Conclusione da tenere nel white paper: indizio, non prova.

## 30/09/2026 — e43: l'ibrido di D'Imperio (codice + riempitivi copiati)

- **Preregistrato.** 12 combinazioni f × λ.
- **Nessuna praticabile.**
  - I riempitivi danno ripetizioni anche troppe (×1,09–1,34) e le parole uniche restano al 51–66%.
  - Ma h2 sale (2,47–3,09; il solo codice ha già 2,40) e la somiglianza è **locale**: fino al 4,8%
    nella riga, ma 0–0,6% a sei righe. Nel Voynich invece la somiglianza sta su tutta la pagina
    (3,8% → 3,4%).
- **Lettura.**
  - Con copie dalle righe vicine l'omogeneità è di riga, non di pagina. Il generatore di Timm e
    Schinner la ottiene di pagina grazie alle sue regole di scelta della fonte.
  - Un ibrido "codice + autocitazione alla Timm e Schinner" non è escluso da questo esperimento, ma
    va costruito con quel generatore (Java), non con l'autocitazione semplificata.
  - Possibile esperimento successivo.
