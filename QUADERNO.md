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

## 30/09/2026 — e44: un messaggio diluito nel generatore di Timm e Schinner

- **Preregistrato** (`e44.md`).
- **Il modello.** Nuova aggiunta al sorgente Java, `analisi/timm_schinner/Messaggio.java`: a ogni
  posto di parola, con probabilità m, si scrive la parola successiva di un messaggio vero (Plinio
  codificato parola per parola). Il resto è il generatore con le giunture a forza 3.
- **Validità.** Con m = 0 il testo è identico byte per byte a quello dell'e23, per i semi 19, 1 e 2.
- **Risultati (media su tre semi):**

| m | parole di messaggio | parole uniche | ripetizione | somigl. riga → 6 righe | legame | h2 |
|---|---|---|---|---|---|---|
| 0 | 0% | 0,51 | 0,81 | 3,5% → 3,3% | 0,179 | 2,25 |
| 0,05 | 4% | 0,55 | 0,71 | 2,7% → 2,5% | 0,164 | 2,33 |
| 0,10 | 9% | 0,57 | 0,68 | 2,4% → 2,1% | 0,156 | 2,39 |
| 0,20 | 17% | 0,60 | 0,75 | 1,6% → 1,3% | 0,132 | 2,43 |
| 0,50 | 44% | 0,65 | 0,63 | 0,7% → 0,6% | 0,060 | 2,47 |
| Voynich | | 0,68 | 1,01 | 3,8% → 3,4% | 0,188 | 2,24 |

- **Esito:** nessuna quota compatibile (m\* = 0).
  - Il messaggio porta le parole uniche verso il Voynich, ma già al 4% di parole rompe
    l'omogeneità di pagina.
  - Le parole del messaggio, una volta scritte, diventano anche fonti di copia e portano nella
    pagina vocabolario estraneo.
- **Per la preregistrazione:** l'ipotesi "nessun messaggio" esce rafforzata rispetto alla variante
  "messaggio diluito fra riempitivi".
- **Cautela importante.** Il codice usato assegna le parole del Voynich per rango di frequenza
  latina, senza badare allo stile della pagina. Un codificatore più accorto, che scegliesse fra
  sinonimi la forma più simile alle parole vicine, potrebbe non rompere l'omogeneità. Questo
  esperimento esclude la diluizione "ingenua", non ogni diluizione.

## 30/09/2026 — Immagini: download completo e vicolo cieco dell'allineamento (e33, e45, D-010)

- **e33.** Scaricate 211 immagini su 213: rifiutate con 403 le foto del dorso e del taglio, che non
  servono. Registro con impronte in `dati/immagini.json`. e33 ora annota le immagini rifiutate
  invece di fermarsi.
- **e45 e D-010.** L'idea era misurare l'inchiostro delle etichette della farmacia, per capire se
  recipienti e frammenti furono scritti in sedute diverse.
  - I riquadri di voynichese.com non si portano sulle immagini IIIF: le scale trovate variano da
    1,60 (bordo della griglia) a 2,04 fra pagine uguali, e nei paragrafi i riquadri si
    sovrappongono fra righe.
  - Sulle etichette, con affinamento locale, circa metà cade nel posto giusto (controllo a vista
    su f99r).
  - Misura rinviata. Per farla serve segnare a mano i riquadri delle etichette, con un protocollo
    cieco.

## 30/09/2026 — e47: il vocabolario aperto è costante e strutturale

- **Preregistrato.** Esito "misto" per la soglia dichiarata: il divario di parole uniche fra Voynich
  e generatore è 0,10 già a 1.000 parole e sale a 0,17 a 34.000.
- **Il dato più importante, non previsto:** nel Voynich la quota di parole uniche quasi non cala
  con la dimensione del campione.

| parole | 1.000 | 5.000 | 34.000 |
|---|---|---|---|
| Voynich | 0,74 | 0,70 | 0,68 |
| generatore | 0,63 | 0,56 | 0,51 |
| Bibbia latina | 0,72 | 0,65 | 0,50 |
| Plinio | 0,81 | 0,73 | 0,65 |

  - Succede anche dentro Currier A o B da soli, con la trascrizione di Takahashi, e fondendo i
    segni confondibili (0,69 → 0,64). Nel generatore la fusione accentua la saturazione
    (0,53 → 0,42).
  - Il Voynich produce forme nuove a ritmo quasi costante, e non per minuzie grafiche o errori di
    lettura.
- **Ricambio.** La quota di vocabolario in comune fra blocchi di 1.000 parole cala con la distanza
  nel Voynich (0,57 → 0,47 da k = 1 a k = 20). Nel generatore quasi no (0,56 → 0,54).

## 30/09/2026 — e48: il generatore che compone parole nuove

- **Preregistrato.**
- **Il modello.** Nuova aggiunta Java (`Composizione.java`): con probabilità q una parola si compone
  segno per segno con trigrammi di segni, λ · pagina corrente + (1 − λ) · tutto il Voynich.
- **Validità.** Con q = 0 il testo è identico all'e23.
- **Esito:** nessuna combinazione compatibile.
  - Con λ = 0,9 omogeneità (3,4–3,8%), ripetizione (fino a 0,95) e h2 (2,23–2,28) reggono.
  - Le parole uniche arrivano al massimo a 0,58, e il legame fine–inizio crolla (0,08–0,11),
    perché le parole composte saltano la regola delle giunture.
- **Incidente.** La prima corsa di e48 è fallita: l'analisi esplorativa di e47, lanciata in
  parallelo, ha ricompilato la cartella delle classi dell'e23 mentre e48 la usava per il
  controllo di validità. Rilanciata da sola. Regola nuova: gli esperimenti che compilano il
  generatore non girano in parallelo fra loro; e49 usa una cartella propria.

## 30/09/2026 — Metodo: il rischio di adattare il modello ai dati

Con e48 ed e49 sto costruendo un modello per tentativi successivi, ciascuno preregistrato. Ma la
sequenza dei tentativi è guidata dai risultati precedenti (un "giardino dei sentieri che si
biforcano"). Per questo l'e49 introduce una **validazione fuori campione**: tre proprietà del
Voynich non usate per costruire il modello, con soglie fissate prima:

- la curva piatta delle parole uniche;
- il ricambio del vocabolario;
- il profilo di informazione di pagina dell'e36.

Nel white paper un modello "che funziona" va presentato con queste prove, non con la sola lista di
controllo su cui è stato tarato.

## 1/10/2026 — Davide: "continua con tentativi successivi; il white paper solo quando lo dico io"

Lavoro in autonomia durante la notte. Stessa procedura: preregistrazione, commit, esecuzione,
commit dei risultati, quaderno, push sul repository privato.

## 30/09–1/10/2026 — e49 ed e50: il generatore che compone, verso il Voynich

**e49 (giunture anche per le parole composte).**

- Il legame fine–inizio torna a 0,18–0,24.
- Nessuna combinazione compatibile, per il solito compromesso: con la composizione dalla pagina
  (λ = 0,9) l'omogeneità regge ma le parole uniche restano 0,56–0,57; con λ = 0,6 le uniche
  arrivano a 0,58–0,62 ma l'omogeneità scende all'1,4–2,3%.
- Validazione fuori campione: V1 (curva piatta) sempre superata; V3 solo con λ bassa; V2 (deriva
  del vocabolario) **mai** (0,00–0,04 contro 0,10).

**Lettura del sorgente.** Il generatore, nelle righe iniziali di paragrafo, il 70% delle volte
copia da una riga iniziale di paragrafo presa a caso in **tutto** il testo già scritto. Questo
rimescola vocabolario da ogni parte del testo e spiega la mancanza di deriva.

**e50, due aggiunte spegnibili.**

- **Recenza:** fonti di inizio paragrafo solo dalle ultime K.
- **Novità:** la parola composta dev'essere una forma mai scritta.
- **Validità:** spente, il testo è identico all'e23 e all'e49.
- **Esiti:**
  - la novità rompe il compromesso: parole uniche 0,70–0,79 con omogeneità 3,8–7,2%;
  - la recenza K = 5 dà la deriva (V2 = 0,057–0,071 con λ = 0,9);
  - nessuna combinazione è compatibile: h2 sale a 2,45–2,62 (limite 2,40), e parole uniche e
    omogeneità superano il Voynich.
- **e51** prova q più piccoli. Aggiunge due validazioni fuori campione nuove (V4 lunghezza delle
  parole, V5 unioni attestate), perché V2, diventata un bersaglio della recenza, non è più fuori
  campione.

## 1/10/2026 — Repliche: un difetto di esecuzione

- Il gruppo e09…e27 si è fermato dopo e14. Il processo di `esegui.py`, con l'output rediretto su
  file, è andato in errore scrivendo una lettera ebraica, perché su Windows la codifica
  predefinita dell'output non è UTF-8.
- Corretto (`sys.stdout.reconfigure`) e rilanciato e18–e27.
- **e14** si replica (stessi valori). Il controllo Naibbe si aggiunge con `--naibbe`, come nel
  lavoro originale.

## 1/10/2026 — e51 ed e53: il modello senza messaggio si avvicina

**e51** (meno composizione).

- Prime combinazioni **compatibili**: K = 0, q = 0,10, λ = 0,75 e 0,90.
  - Ripetizione 0,76; somiglianza 3,4% → 3,2%; h2 2,38; legame 0,19; parole uniche 0,64.
  - Lunghezza delle parole 4,41 ± 1,63 (Voynich 4,46 ± 1,64).
- **Fuori campione:** V1 e V4 superate; V3 (profilo di pagina: R 0,74, quota 0,086–0,091) e V5
  (unioni attestate 1,4 contro 2,0) no.
- Per la preregistrazione: compatibile ma validazione a metà.

**Nuove prove fuori campione, calibrate solo su Voynich e lingue prima di guardare i modelli.**

- **V6, autocorrelazione delle lunghezze di parole vicine:** Voynich **+0,15**; Bibbia latina
  −0,16, italiana −0,23, Plinio 0,00. È una firma forte: parole lunghe vicino a parole lunghe, come
  nel gibberish di Gaskell e Bowern.
- **V7, Zipf:** Voynich −1,04, lingue da −0,82 a −1,04. Prova debole.

**e53** (scissione alle giunture morbide; sostituzioni di fine parola).

- La scissione porta le unioni attestate a 1,70–1,83.
- **V6 superata** (0,084–0,094) con sostituzioni finali spente e d ≥ 0,06: il modello riproduce
  fuori campione una proprietà che nessuna lingua ha.
- V7 fallisce di poco (−0,91).
- Ipotesi (b) smentita: senza sostituzioni finali R resta 0,72–0,74.
- **Autocritica sul criterio.** Le soglie a senso unico lasciano passare eccessi: con la scissione
  il legame fine–inizio arriva a 0,30–0,36 (Voynich 0,19). Da qui in poi i criteri saranno bande
  a due lati.

**Stato del modello senza messaggio.** "Autocitazione (Timm e Schinner) + composizione di forme
nuove nello stile della pagina + regola delle giunture + scissione alle giunture morbide."

- **Riproduce:** h2, spazio, parole uniche e curva piatta, lunghezza delle parole, ripetizione
  (0,75–0,8, un po' bassa), omogeneità graduata, legame (troppo con la scissione), unioni
  attestate, autocorrelazione delle lunghezze.
- **Non riproduce:**
  - il **profilo di pagina** (nel Voynich l'informazione di pagina è uniforme lungo la parola, nel
    modello si concentra in fondo ed è più forte);
  - la **deriva** del vocabolario, senza la recenza;
  - Zipf (di poco).

## 1/10/2026 — e46 ed e52: il codice accorto

- **e46** (12 varianti casuali per parola, scelta per stile). Nessuna combinazione compatibile.
  h2 2,76–2,88, tipi il doppio del Voynich; l'omogeneità resta locale; con γ = 3 il legame supera
  il Voynich (0,47–0,55).
- **e52** (varianti vere del Voynich a distanza 1).
  - Molto più vicino: h2 2,12–2,30, tipi 0,17–0,20 (Voynich 0,21), ripetizione fino a 0,91.
  - Somiglianza di pagina locale (fino al 3,4% nella riga, 1,2–1,8% a sei righe) e legame ≤ 0,11:
    stile e giunture si contendono la stessa scelta.
  - **L'86–88% delle posizioni è ambiguo.**
- **Lettura del messaggio conoscendo la chiave** (esplorativo):
  - parola per parola: 31–38%;
  - con il contesto addestrato sullo stesso testo: 91–95%, ma è memoria;
  - con il contesto addestrato su altri libri di Plinio: **32–37%**.
- **Lettura.** Un codice che ottiene le ripetizioni del Voynich facendo condividere le forme a
  parole diverse perde circa due terzi del messaggio anche per chi ha la chiave. È un argomento
  forte contro la variante "codice accorto" dell'ipotesi con contenuto, almeno nella forma provata.

## 1/10/2026 — e54 ed e55: la forma delle parole (V8)

- **e54 (diagnosi esplorativa).** Nel generatore la firma di pagina sta sui segni della seconda e
  penultima posizione (*e*, *d*, *i*), nel Voynich è distribuita. Ma soprattutto le **forme** sono
  diverse:
  - *q-* iniziale: generatore 3%, Voynich 10–18%;
  - *a-* iniziale: generatore 20%;
  - *-y* finale: generatore 18%, Voynich 33–46%.
- **e55, preregistrato.** Distanza di Jensen–Shannon fra le distribuzioni del segno per posizione.
  - Riferimenti: rumore (pagine pari/dispari) 0,000–0,001; Currier A/B 0,021–0,087.
  - **Tutti i generatori ad autocitazione, tutti i semi, falliscono V8.**
  - Naibbe e codice parola per parola la superano, per costruzione.
- **Lettura.** La somiglianza del generatore alla lista di controllo non si estende alla forma
  delle parole: scrive parole più lontane dal Voynich di quanto le sue due lingue lo siano fra
  loro. V8 entra nella lista di controllo per qualunque generatore futuro.

## 1/10/2026 — Replica di e17 sul sottoinsieme dichiarato (D-009)

- e17 (risolutore a ricottura simulata) rieseguito su latino, italiano ed ebraico: 3.710 valori
  confrontati, **nessuna differenza** a parte i tempi di esecuzione. Il log è in
  `risultati/provenienza/e17.*`; la corsa ha usato `LINGUE_SOLO=Latin,Italian,Hebrew` e
  `PROCESSI=2`.
  - Quella corsa è partita prima che `esegui.py` registrasse le variabili d'ambiente, quindi le
    annoto qui.
- Il file rieseguito conteneva solo le tre lingue. Ho ripristinato `e17_ricottura.json` e `.md`
  originali, con gli stessi valori, per non perdere le altre lingue.
- `verifica_replica.py` ora ignora i campi di durata.
- **Stato della replica:** tutti gli esperimenti e01–e28 si replicano, tranne e19 ed e20, non
  rieseguiti (D-009), ed e13, che cambia per una ragione spiegata (D-008). e16 era superato già
  nel lavoro originale e non è stato rieseguito.

## 1/10/2026 — e56 ed e57: "copia o componi", un modello più semplice

- **e56.** Due gesti: copiare una parola vicina o comporne una nuova con i trigrammi della pagina
  recente.
  - Nessuna combinazione compatibile (bande a due lati): la composizione libera satura, con parole
    uniche 0,30–0,54 e tipi 0,02–0,16.
  - Deriva (V2) e autocorrelazione delle lunghezze (V6) però compaiono.
- **e57** (forme composte sempre nuove). Eccesso opposto: tipi 0,50–0,80, h2 2,5–2,8, legame
  0,34–0,40.
- **Il numero chiave.** Nel Voynich circa il **14% delle parole** è una forma che compare una sola
  volta (0,21 tipi per parola × 0,68 di quota unica). Un modello deve inventare circa una parola su
  sette e riusare le altre con piccole variazioni. Il modello e51 (q = 0,10) sta in quella zona.
- **Il paradosso da spiegare.** Il Voynich ripete la parola precedente quanto il caso (×1,0), ma
  inventa forme nuove a ritmo costante. Nei modelli le due cose si ottengono solo con una spinta
  esplicita alla novità.

## 1/10/2026 — e58: la parola "di sopra" (prova del meccanismo di copia)

- **Preregistrato.** Una parola somiglia a quella nella stessa posizione della riga sopra più che
  alle altre parole di quella riga?
- **Risultati:**
  - Voynich **1,059** (z = 9,9); Currier A 1,052, B 1,062;
  - generatore di Timm e Schinner 1,045–1,062 (controllo positivo);
  - controlli negativi 1,000–1,011. Ma la Bibbia latina ha p = 0,034, sotto la soglia di 0,05:
    validità non piena per la lettera della preregistrazione.
- **Esplorativo, senza la prima e l'ultima parola di ogni riga.** Le parole ai bordi hanno forme
  proprie e gonfiano il confronto.
  - Voynich **1,028** (z = 4,3, p = 0,001); B 1,033; A 1,014 (non significativo, meno pagine).
  - Generatore 1,030–1,050.
  - Controlli negativi tutti p > 0,1. Gibberish a righe vere 1,023 (p = 0,11, campioni piccoli).
- **Lettura.** C'è una traccia di somiglianza "in verticale" della grandezza di quella del
  generatore che copia la parola di sopra. È un indizio a favore di un meccanismo di copia
  (ipotesi 3). Ma lo produrrebbe anche un contenuto **a colonne**, con righe parallele (ipotesi 1
  nella forma "tabella"). Distinguere le due cose richiede di sapere se le "colonne" del Voynich
  hanno un senso proprio: per esempio, se la somiglianza verticale si concentra in certe posizioni
  della riga.

## 1/10/2026 — e60: formule a distanza

- **Preregistrato.** Sequenze di 2–3 parole che ritornano ad almeno 10 pagine di distanza,
  rispetto alle parole rimescolate dentro la pagina.
- **Risultati:**
  - coppie: generatori ×1,13–1,31; **Voynich ×1,51**; testi con contenuto ×2,0–3,1;
  - terne: generatori ×1,5–3,3; **Voynich ×5,2**; testi con contenuto ×11–58;
  - i codici conservano esattamente le formule del testo in chiaro.
- **Per la soglia preregistrata** (coppie ≥ 1,5) il Voynich "si accorda con un contenuto a formule",
  ma proprio sul limite.
- **Descrizione (esplorativa) delle terne lontane del Voynich.**
  - Sono quasi tutte **nella stessa sezione**, a 10–20 pagine di distanza (biologica f75–f84,
    ricette f103–f112), e fatte di parole frequenti di Currier B (*ol shedy qokedy*,
    *chey qol chedy*).
  - Spesso includono pezzi staccati alle giunture morbide (*ol s aiin*, *or aiin*).
- **Lettura prudente.** Il forte legame fine–inizio del Voynich (-y → q-) rende certe sequenze più
  probabili del rimescolamento. Lo mostra il generatore: con le giunture (e51) le terne lontane
  passano da ×1,5–2 a ×3,3.
  - L'eccesso del Voynich è quindi in parte un effetto delle giunture e della concentrazione del
    vocabolario per sezione, non necessariamente di formule di contenuto.
  - Resta però più alto di tutti i generatori: ×5,2 contro ×3,3 al massimo.

## 1/10/2026 — e59: la traccia verticale con la distanza

- **Preregistrato.** Voynich: eccesso 0,028 a d = 1, 0,018 a d = 2, 0,021 a d = 3, 0,015 a d = 5.
  Il rapporto d=2/d=1 è 0,64.
- **Lettura.** Non è "copia dalla sola riga sopra". Il profilo è simile al generatore ai semi 1 e 2,
  che sceglie la riga fonte fra tutte le precedenti della pagina.
- **Limite.** Oltre d = 1 il controllo negativo è inaffidabile (Bibbia a pagine finte: z = 3,9 a
  d = 3). Il test non separa una tabella da una copia "da tutta la pagina".

## 1/10/2026 — e61: la pagella (riepilogo descrittivo)

- **Che cos'è.** 17 proprietà del Voynich, con bande di tolleranza scelte dopo aver visto i
  risultati, per 10 testi o modelli.
- **Punteggi:**
  - lingue ed elenchi 1–2;
  - codice parola per parola 3; Naibbe 5; codice accorto 6;
  - generatore puro 5; con giunture 8; **modello e51 9**; modello e53 8.
- **Complementarità.**
  - I codici prendono forma delle parole, h2, spazio, tipi, e hanno un profilo di pagina piatto
    come il Voynich (codice di Plinio R = 1,06).
  - I generatori prendono omogeneità, legame, traccia verticale, formule; il loro profilo di
    pagina è concentrato in fondo alla parola (R 0,64–0,72).
- **Nessuno** riproduce la deriva del vocabolario (a parte la recenza aggiunta apposta in e50),
  il profilo di pagina e l'autocorrelazione delle lunghezze (Voynich 0,15; massimo 0,07–0,09).
- **Prossimo passo.** e62 prova a unire le due famiglie: messaggio vero, omofoni veri, scelta
  secondo uno stile di pagina che deriva.

## 1/10/2026 — e62 e una diagnosi sulle lunghezze

- **e62** (omofoni veri scelti secondo uno stile di pagina che deriva). Nessuna combinazione
  compatibile: omogeneità al massimo 0,9%. La deriva compare (0,06–0,07 con σ = 2, ρ = 0,95).
- **Bilancio della famiglia "codice"** (e46, e52, e62).
  - Per avere omogeneità di pagina con la sola scelta fra forme equivalenti servono molte forme
    per parola, e molte forme gonfiano vocabolario e h2.
  - Per avere le ripetizioni bisogna che parole diverse condividano le forme, e allora il messaggio
    si perde per due terzi.
  - Nella forma provata, l'ipotesi "codice + stile" non riproduce il Voynich.
- **Diagnosi esplorativa dell'autocorrelazione delle lunghezze.**
  - Voynich: 0,15 / 0,087 / 0,064 a distanza 1 / 2 / 3. Generatore: 0,015 / 0,027 / 0,022.
    Bibbia: −0,16 / 0,00 / 0,03.
  - Centrando le lunghezze sulla media della riga, nel Voynich resta un vantaggio della posizione
    contigua (−0,074 contro −0,17 a distanza 2).
  - Sono quindi due componenti: **righe con un loro stile di lunghezza** e **somiglianza fra parole
    contigue**. Il generatore non ha né l'una né l'altra.
- **Ipotesi di meccanismo, da provare in e63: la riga modello.** Lo scriba prende una riga sopra
  come modello e la ripercorre parola per parola, ritoccando.

## 1/10/2026 — e63: la riga modello

- **Preregistrato.** Ogni riga ripercorre una riga sopra, ritoccandone le parole.
- **Esito: in eccesso su tutto.**
  - Autocorrelazione delle lunghezze 0,09–0,38 (Voynich 0,15) e traccia verticale 1,9–3,0
    (Voynich 1,03).
  - h2 3,0–3,4; ripetizione circa 2; forma delle parole lontanissima.
- **Lettura.** Le modifiche applicate riga dopo riga accumulano forme sempre più strane. Nella forma
  provata il meccanismo non regge. Una variante molto più leggera (a ≤ 0,3) potrebbe dare solo
  la componente di riga, ma non l'ho provata.

## 1/10/2026 — e64: il soggetto della pagina

- **Preregistrato.** La parola d'apertura delle pagine d'erbario ritorna nella pagina più di una
  parola qualsiasi di lunghezza simile?
- **Controllo positivo (Culpeper).** Il nome della pianta ritorna 1,77 volte più del caso
  (p = 0,005). La soglia preregistrata era 2: **validità non piena**.
- **Voynich.**
  - L'apertura ritorna **molto meno** del caso: 2% contro 21% (×0,07); in forma simile 27% contro
    55% (×0,50).
  - Vale in Currier A e B.
- **Generatore:** ×0,12–0,18. Le prime parole di paragrafo hanno regole proprie.
- **Lettura prudente.**
  - La prima parola delle pagine d'erbario non si comporta come il nome del soggetto di un
    erbario: non ritorna, nemmeno in grafia vicina.
  - Se fosse il nome della pianta, nel testo il nome dovrebbe comparire in un'altra forma, per
    esempio abbreviato, oppure non comparire affatto.
  - È la stessa direzione del procedimento senza messaggio. Il test però ha validità non piena.

## 1/10/2026 — e65: formule d'apertura nelle ricette (test non valido)

- **Preregistrato.** Le aperture dei paragrafi sono più concentrate delle parole interne?
- **Il controllo positivo fallisce.** Apicio ha rapporto 0,95 (p = 0,71): le aperture variano
  (*accipies*, *piper*, *adicies*) e le parole interne sono già concentrate. Solo la Bibbia (*et*,
  *dixitque*) supera la soglia (1,78).
- **Il valore del Voynich** (0,84; aperture più frequenti *tchedy*, *pol*, *polaiin*) **non è
  informativo.**
- **Lezione di metodo.** L'idea "i ricettari aprono con formule" era vera per l'italiano o il latino
  tardo (*recipe*, *item*), non per Apicio. Il controllo positivo l'ha mostrato prima che il
  risultato sul Voynich potesse essere sovrainterpretato.

## 1/10/2026 — Pilota abbandonato: riquadri delle etichette segnati "a vista"

- **Tentativo.** Segnare a mano i riquadri delle etichette di f99r su un ritaglio con griglia di
  coordinate, per misurare l'inchiostro (chiudere e40/e42).
- **Esito.** Leggendo le coordinate dall'immagine sbaglio la posizione di decine di pixel, quanto
  un'etichetta intera. Inoltre i contorni dei disegni hanno lo stesso inchiostro bruno del testo,
  quindi un affinamento automatico non basta.
- **Decisione.** Non procedere. Serve un annotatore umano con uno strumento grafico: è un lavoro
  che Davide potrebbe fare, circa 190 riquadri su 12 pagine.

## 1/10/2026 — e66: parole chiave e argomenti (nello spirito di Montemurro e Zanette 2013)

- **Preregistrato.** La misura è ricostruita dalla descrizione generale, non dal loro codice;
  l'articolo è da verificare alla fonte.
- **Risultati** (I* in bit per parola):
  - Plinio 0,105 (in chiaro e codificato identici: la misura non dipende dalla grafia);
  - Bibbia 0,177;
  - **Voynich 0,296**;
  - generatore di Timm e Schinner 0,39–0,50;
  - modello e51 0,36;
  - modello con recenza 0,435;
  - Naibbe 0.
- **Lettura.**
  1. La "struttura per parole chiave" **non** è un indizio di contenuto: un procedimento di copia
     locale ne produce più dei testi veri.
  2. Ciò che distingue il Voynich è la **persistenza a grande scala**: 0,25 a 4.000 parole, contro
     0,16 del generatore puro. Solo il modello con recenza ci arriva (0,244).
  - È la stessa conclusione della deriva (V2): il vocabolario del Voynich cambia lungo il testo
    come se lo scriba attingesse a ciò che ha scritto di recente, non a tutto il testo.
  - Un testo con argomenti che cambiano lo farebbe allo stesso modo: questa proprietà non
    distingue fra contenuto e procedimento con recenza.

## 1/10/2026 — e67 ed e68: consolidamento e filtro di forma

**e67** (consolidato a parametri fissi: forme nuove + giunture + recenza + scissione).

- 6–9 proprietà su 17, non meglio dell'e51: i meccanismi interferiscono. Recenza e scissione
  insieme alzano h2 (2,43–2,46) e abbassano lo spazio (0,47–0,50).

**e68** (filtro di forma sul primo e l'ultimo segno, sopra l'e51).

- **Deviazione D-011.** Con η = 1 il generatore si bloccava, perché rifiutava le parole d'inizio
  paragrafo con i gallows. Il filtro è stato escluso per le parole d'inizio riga e tutto è stato
  rieseguito.
- **Validità:** con η = 0 il testo è identico all'e51.
- **η = 1: 12/17,** il punteggio più alto finora. Fuori campione 5/7: **deriva 0,081 e Zipf −1,08**
  compaiono senza essere bersagli. Ripetizione 1,21 e legame 0,14 al limite delle bande.
- **Restano fuori:**
  - la forma delle parole (2,02: il filtro tocca solo primo e ultimo segno);
  - lo spazio (0,575);
  - l'omogeneità, ora in eccesso (8,1%);
  - il profilo di pagina (R 1,31);
  - l'autocorrelazione delle lunghezze (0,072).
- **Lettura.**
  - Parte dei difetti del generatore dipende davvero dalla forma delle parole: correggerla sistema
    deriva e Zipf.
  - Ma il compromesso si sposta (omogeneità troppo alta), e la forma resta lontana nelle posizioni
    interne della parola.
  - Il procedimento senza messaggio arriva a 12/17 proprietà; le altre 5 non le ho ottenute in
    nessuna combinazione provata.

## 1/10/2026 — e69: filtro di forma su quattro posizioni

- **Griglia preregistrata:** posizioni {2; 4} × η {0,5; 1} × λ {0,6; 0,75}, semi 19, 1 e 2.
  Nessuna combinazione si è bloccata.
- **Migliore:** ancora 12/17 (2 posizioni, η 1, λ 0,6), con deriva 0,121, Zipf −1,04 e lunghezze
  vicine 0,085 dentro le bande.
- **La forma delle parole non rientra mai:** 1,84–2,54 volte la distanza A–B. Con 4 posizioni
  e η 1 va **peggio** (5–6/17): il legame fra parole crolla (0,007–0,009) e i tipi scendono.
- **Previsione smentita.** Avevo previsto che con 4 posizioni la forma scendesse verso 1; non è
  successo.
- **Lettura.** Il filtro può solo rifiutare ciò che il generatore propone. Se le regole di ritocco
  di Timm e Schinner propongono poche forme buone, rifiutare le cattive impoverisce il vocabolario
  invece di correggerlo.

## 1/10/2026 — e70: copia esatta frequente o forma nuova

- **Modello.** In Python e senza le regole di ritocco: ogni parola è una copia di una vicina (c
  0,80–0,90, con ritocco leggero facoltativo μ) oppure una forma nuova dai trigrammi del Voynich.
- **Esito:** 4–6/17, molto peggio dell'e68.
- **Previsioni smentite:**
  - parole uniche 0,40–0,50 (Voynich 0,68): copiare così spesso riusa troppo;
  - tipi a 0,10–0,30, a seconda di μ;
  - la forma delle parole, che doveva tornare "per costruzione", è a 2,7–4,5.
- **Probabile spiegazione (non verificata).** La forma si misura sulle occorrenze, non sui tipi.
  Con molte copie esatte, poche forme composte presto si moltiplicano e la distribuzione dei segni
  per posizione segue quelle poche forme. Il Voynich invece ha le stesse distribuzioni in tutte
  le parti del testo.
- **Lettura.**
  - "Copiare e basta" non basta: serve un meccanismo che ritocchi molto, cioè proprio le regole di
    Timm e Schinner, che però hanno la forma sbagliata.
  - È lo stesso compromesso di e56 ed e57, visto dall'altra parte.
  - **Chiudo qui la linea dei generatori senza messaggio.** Il migliore resta 12/17 (e68 ed e69).

## 1/10/2026 — e71: anatomia del bordo di riga

- **Preregistrato.** È la voce 7 del dossier. Prima di eseguire ho letto nel codice del generatore
  di Timm e Schinner che ha già regole per il bordo: aggiunge un segno a inizio riga e sostituisce
  l'ultimo segno. L'ho annotato nella preregistrazione.
- **La prova del segno aggiunto non vale.** Il controllo positivo ("s" aggiunta a metà delle righe)
  dà 1,09 contro la soglia di 1,5. La misura è troppo debole: la forma senza il primo segno è
  spesso rara, e la soglia di 2 attestazioni la esclude. Il Voynich dà 1,17 (z 16), ma con un
  controllo fallito non si legge.
- **Distinzione del bordo** (rapporto con il nullo, cioè con le parole rimescolate dentro la
  riga):

  | testo | inizio | fine |
  |---|---|---|
  | Voynich | 23 | 55 |
  | lingua A | 15 | 22 |
  | lingua B | 32 | 43 |
  | Plinio mandato a capo | 4,6 | 1,1 |
  | Plinio codificato | 2,3 | 0,8 |
  | Naibbe | 4,8 | 0,7 |
  | Timm e Schinner | 10–13 | 129–188 |
  | e51 | 10 | 130 |

  - Nella prosa mandata a capo l'effetto all'inizio è solo di lunghezza: la parola che non entra
    va alla riga dopo, quindi le parole iniziali sono più lunghe.
- **Segni arricchiti** (righe che non aprono un paragrafo):

  | testo | inizio riga | fine riga |
  |---|---|---|
  | Voynich | s ×5,3, y ×4,8, t ×3,5, d ×2,5 | g ×25, m ×16 |
  | generatore | p ×4–5, f ×4–5, k ×2–3 | m ×8–11, g ×8–15 |

  - Il generatore mette i gallow anche a inizio riga, mentre il Voynich no (p ×2,6 su 44 casi).
  - A fine riga usa la "m" il doppio del Voynich (circa 1.200 occorrenze contro 626).
- **Esclusività** (tipi che compaiono solo al bordo):
  - Voynich 1,7 e 1,8;
  - generatori 1,3–1,5 e 1,3–2,3;
  - prosa mandata a capo 1,2–1,3 e circa 1.
  - Non distingue "riga = voce" dai ritocchi di bordo, perché anche il generatore la produce.
- **Lettura.**
  - Il bordo di riga del Voynich è fortissimo e di **forma diversa** da quella del generatore:
    all'inizio s/y/d e non i gallow, alla fine meno m.
  - Le regole di bordo di Timm e Schinner sono una caricatura: all'inizio troppo deboli e con i
    segni sbagliati, alla fine troppo forti.
  - La proprietà entra nella pagella come diciottesima (D-012).
- **Prossimo passo (e72).** Una prova meglio costruita fra **aggiunta** di un segno, **scelta** di
  parole diverse e **sostituzione** dell'ultimo segno, con un modello di verosimiglianza invece
  della soglia di attestazione.

## 1/10/2026 — e72: scelta, aggiunta o sostituzione al bordo

- **Metodo.** Preregistrato. Miscela con EM di scelta (S), aggiunta di un segno (A),
  sostituzione (T) e forma nuova (N). Confronto con la verosimiglianza su dati esclusi.
- **Nota di trasparenza.** Prima di eseguire ho fatto una prova di funzionamento sulle prime 600
  righe della lingua A, e ho visto un numero, il guadagno di A, prima del commit della
  preregistrazione. Il disegno non è stato cambiato dopo.
- **Validità:**
  - **controllo d'aggiunta:** guadagno +2,53 bit (✓). Il peso π_A,s è però 0,342, appena sotto il
    minimo dichiarato di 0,35 (✗): i pesi **sottostimano** la quota aggiunta di circa un terzo
    (0,34 contro 0,5 vero), quindi vanno letti come limiti inferiori;
  - **controllo di sostituzione:** T +2,38 contro A +0,61 (✓);
  - **testi mandati a capo:** all'inizio i guadagni stanno sotto 0,05 bit. **Alla fine Plinio in
    chiaro guadagna 0,17–0,32 (✗).** Il motivo sono le desinenze latine: una parola mai vista a metà
    riga si spiega bene come "stessa radice con un'altra desinenza", in **qualsiasi** posizione. È
    un difetto di disegno: mancava il confronto con una posizione interna. **Il lato fine non si
    legge.**
- **Inizio riga** (unico lato valido), guadagno in bit e peso:

  | testo | A | T | peso A | segni |
  |---|---|---|---|---|
  | Voynich | **+0,79** | +0,39 | 0,23 | y, d, s, o |
  | lingua A | +0,73 | | | |
  | lingua B | +0,96 | | | |
  | controlli mandati a capo | ≤ +0,04 | | | |
  | Timm e Schinner ed e51 | +0,15–0,20 | | 0,08–0,10 | gallow k, p, t |

  - Secondo il criterio preregistrato il meccanismo all'inizio è l'**aggiunta**: molte parole
    d'inizio riga sono parole normali precedute da y, d, s oppure o.
  - Il generatore fa la stessa cosa, ma con forza un quarto più bassa e con i segni sbagliati.
- **Riserva.** Resta da escludere che sia la morfologia generale del Voynich, dove le parole con e
  senza un o-, y-, d- iniziale coesistono. Il testo codificato per rango (parole del Voynich
  messe a caso) dà +0,04, il che lo rende poco probabile. La prova giusta è però la stessa misura
  su una posizione interna: la faccio nell'e73.

## 1/10/2026 — e73: il bordo contro la posizione accanto

- **Metodo.** Preregistrato. Stesso modello dell'e72, con riferimento le parole dalla terza alla
  terzultima, su righe di almeno 6 parole. Effetto proprio = bordo meno posizione accanto.
- **Validità:**
  - **inizio:** i controlli mandati a capo stanno a ≤ 0,026 (✓). Il controllo d'aggiunta dà
    +2,38 (✓);
  - **fine:** il controllo di sostituzione dà T +2,13, più di A +0,51 (✓). **Plinio però dà T
    +0,064, sopra la soglia di 0,05 (✗).** L'effetto è piccolo e viene dall'a capo: le parole
    finali sono quelle corte che ci stanno. Per regola il lato fine non si legge.
- **Inizio riga (valido).** Effetto proprio dell'aggiunta, in bit:

  | testo | A | T |
  |---|---|---|
  | Voynich | **+0,79** | +0,40 |
  | lingua A | +0,59 | |
  | lingua B | +0,94 | |
  | Timm e Schinner | +0,14–0,21 | |
  | e51 | +0,13 | |

  - Nel Voynich la seconda parola dà solo +0,02, quindi l'effetto è proprio della prima parola.
  - **È confermato:** a inizio riga lo scriba aggiunge un segno (y, d, s, o) a una parola normale.
    Questo spiega una parte importante della particolarità delle parole d'inizio riga.
- **Fine riga (esplorativo, non valido per regola):**
  - Voynich: A +0,165 e T +0,161, cioè indistinguibili;
  - generatore: solo sostituzione (T +0,28–0,37, A ≈ 0).
  - Il meccanismo del generatore ("ol" → "om") è dunque probabilmente diverso da quello del
    Voynich, ma la prova non è valida.
- **Lettura per le ipotesi.**
  - Un segno aggiunto a inizio riga è compatibile con una convenzione di scrittura (un segno di
    riga o un riempitivo) e con un procedimento di generazione con una regola di bordo.
  - Non è compatibile con un testo vero mandato a capo senza convenzioni: i controlli danno circa
    0.
  - Per chi cerca di decifrare, il primo segno delle parole d'inizio riga in y, d, s, o è
    probabilmente da togliere.

## 1/10/2026 — e74: il legame fra parole non attraversa l'a capo

- **Metodo.** Preregistrato. Eccesso d'informazione mutua fra l'ultimo segno di una parola e il
  primo della successiva: dentro la riga (fra parole interne) e attraverso l'a capo (ultima
  parola di una riga, prima della riga dopo, stesso paragrafo).
- **Validità:**
  - Naibbe a capo: R 1,02 (✓). Il suo legame però è debolissimo (0,0014 bit, z 2), quindi è un
    controllo di poca forza;
  - Plinio a capo: R 0,67, ed è il controllo che conta, perché il legame è forte sia dentro (z 46)
    sia attraverso l'a capo (z 8);
  - righe rimescolate: R < 0 (✓).
- **Voynich:**

  | testo | dentro la riga | attraverso l'a capo | R |
  |---|---|---|---|
  | Voynich | 0,200 bit (z 248) | 0,001 (z 0,3) | **0,01** |
  | lingua A | | | 0,02 |
  | lingua B | | | 0,01 |
  | Voynich, tolto y/d/s/o | | | 0,04 |

- **Controllo esplorativo, non preregistrato.**
  - Escludendo le fini di riga in m, g, d, s (forse sostituite), R resta 0,009–0,018.
  - Dentro la riga, con lo stesso numero di coppie (3.337), lo z è 45: la potenza c'è.
- **Generatori:**
  - Timm e Schinner: R 0,15–0,26, ma su un legame debole (0,02);
  - con le giunture (e23): R 0,00;
  - e51: R 0,03.
  - La regola delle giunture di questi modelli vale solo dentro la riga, per costruzione.
- **Lettura.** Questo è uno dei risultati più netti finora: **la riga del Voynich è un'unità
  chiusa.** Il forte legame fra parole vicine, che è la ragione della regola delle giunture,
  sparisce del tutto all'a capo.
  - **Contro un testo continuo cifrato e mandato a capo**, dove le parole sono pezzi di una
    sequenza continua: lì il legame continuerebbe, come in Plinio (R 0,67). Anche la sequenza dei
    segni del Voynich, che è molto prevedibile (h2 bassa), non continua da una riga all'altra.
  - **Compatibile con:**
    - righe come voci indipendenti (ipotesi 1);
    - una scrittura o generazione riga per riga (ipotesi 3, come il generatore);
    - un cifrario che riparte a ogni riga (ipotesi 2 con una convenzione di riga).
  - Insieme all'e73 (segno aggiunto a inizio riga) e all'e71 (fine riga in m/g), la riga ha
    un'**apertura**, una **chiusura** e nessun legame con la riga dopo.

## 1/10/2026 — e75: struttura interna della riga

- **Metodo.** Preregistrato. Informazione mutua fra caratteristiche delle parole interne e classe
  di posizione relativa (4 classi), contro i rimescolamenti dentro la riga.
- **Validità:**
  - testi mandati a capo con |z| < 3 per tutte le caratteristiche (il massimo è Plinio, primo
    segno, z 2,6) (✓);
  - controllo positivo (parole ordinate per lunghezza): z 904 (✓).
- **Voynich:**

  | caratteristica | eccesso (bit) | z | lettura preregistrata |
  |---|---|---|---|
  | primo segno | 0,0129 | **31** | struttura |
  | tipo | 0,0117 | **12,5** | struttura |
  | ultimo segno | | 4,7 | sotto soglia |
  | lunghezza | | 1,9 | nulla |

  - **Verso l'inizio della riga:** *sh* (×0,46 nell'ultima classe rispetto alla prima), q, k.
  - **Verso la fine della riga:** *d* ×1,8, *t* ×1,7, *cth* ×1,5.
  - Le lingue A e B lo mostrano entrambe.
- **Generatori:** tutti con eccesso ≈ 0 (|z| ≤ 2,4, con le giunture o senza). È un'altra proprietà
  che non hanno.
- **Controllo esplorativo, non preregistrato.** Togliendo anche la seconda e la penultima parola
  (righe di almeno 8 parole), il primo segno scende a z 9,5. Togliendone due per lato (righe di
  almeno 10 parole) scende a z 2,2, con meno righe. Quindi:
  - **non sono colonne di una tabella**, ma un **gradiente dai bordi** verso l'interno, che si
    estende per una o due parole;
  - la seconda parola è ricca di *sh*, mentre sul segno aggiunto (e73) era quasi normale; le
    parole verso la fine sono ricche di *d* e *t*.
- **Lettura.**
  - La riga del Voynich ha un "profilo" dall'inizio alla fine, non solo i bordi.
  - Il fatto che nella prosa mandata a capo non ci sia niente conferma che la riga è un'unità
    di composizione.
  - Un procedimento senza messaggio dovrebbe scrivere riga per riga con preferenze che cambiano
    lungo la riga; il generatore non lo fa.
  - Una voce d'elenco con una formula d'apertura e una di chiusura lo farebbe naturalmente.

## 1/10/2026 — e76: righe piene e chiuse (sezione delle ricette)

- **Metodo.** Preregistrato.
- **Errore di codice.** Nella prima esecuzione le etichette "dentro" e "a capo" erano scambiate
  (R invertiti). Corretto in un commit a parte e rieseguito; la prima esecuzione è scartata.
- **Validità:**
  - Apicio, una ricetta per paragrafo: CV 0,035, R 1,16 (✓);
  - voci indipendenti: CV 0,44, R 0,13 (✓).
- **Risultati:**

  | testo | CV | righe corte | R |
  |---|---|---|---|
  | **Voynich S** | **0,049** | **0,1%** | **−0,00** (dentro la riga 0,256 bit, z 145) |
  | Voynich H (descrittivo) | 0,19 | | 0,08 |
  | generatore | 0,12 | 6–7% | 0,16–0,25 |

  - Nell'erbario i disegni cambiano lo spazio disponibile, da qui il CV più alto.
- **Lettura.** Nella sezione S le righe sono **piene come una prosa mandata a capo e chiuse come
  voci indipendenti**.
  - Nessuno dei due modelli semplici dell'ipotesi 1 lo spiega.
  - Il contenuto di ogni riga si adatta alla larghezza, e ogni riga ricomincia da capo.
  - Sono compatibili:
    - un procedimento che riempie la riga (il generatore lo fa, ma meno pieno e meno chiuso);
    - un cifrario o una convenzione riga per riga, con riempitivi;
    - **un testo in versi con giunture fonetiche scritte**, come il sandhi del sanscrito, che si
      applica dentro il verso e non attraverso la fine del verso, dove valgono forme di pausa.
- **Prossimo passo.** Questa ultima possibilità non era stata considerata ed è verificabile:
  e77.

## 1/10/2026 — e77: versi con sandhi riproducono la riga chiusa

- **Metodo.** Preregistrato. *Manusmṛti* e *Raghuvaṃśa* (GRETIL tramite ambuda-org, commit
  fisso, SHA-256 in FONTI.md) in due impaginazioni: un mezzo verso per riga, oppure lo stesso
  testo di seguito mandato a capo.
- **Risultati** (criterio di conferma: R < 0,3 con z > 10 nell'impaginazione per versi, R > 0,6
  in quella di seguito):

  | testo | impaginazione | dentro la riga | a capo | R | CV | bordo ini / fin |
  |---|---|---|---|---|---|---|
  | Manusmṛti | per versi | 0,849 bit (z 449) | 0,006 | **0,01** | 0,096 | 22 / 148 |
  | Manusmṛti | di seguito | 0,595 | 0,455 (z 83) | 0,76 | 0,082 | 5 / 2 |
  | Raghuvaṃśa | per versi | 0,871 (z 375) | 0,006 | **0,01** | 0,172 | 9 / 97 |
  | Raghuvaṃśa | di seguito | 0,624 | 0,533 | 0,86 | 0,097 | 3 / 2 |
  | *Voynich* | | *0,20 (z 248)* | *0,001* | ***0,01*** | *0,049 (S)* | *23 / 55* |

  **Meccanismo confermato per entrambi i testi.**
- **Forme di pausa.** Alla fine del verso sono arricchite ḥ (×5), t (×3,7), **m** (×3,3).
  All'inizio, nella Manusmṛti, a ×1,9 e y ×1,9.
- **Lettura. Risultato importante.**
  - Il "legame forte fra parole vicine", che nel dossier era fra gli argomenti principali
    **contro** una lingua naturale (nelle lingue europee è debole: Plinio 0,04 bit), esiste in una
    lingua naturale con giunture fonetiche scritte. Lì è anche **più forte** che nel Voynich.
  - Se il testo è impaginato **un verso per riga**, il legame si ferma all'a capo esattamente come
    nel Voynich (R 0,01 in tutti e tre).
  - Il bordo di riga diventa fortissimo, con una forma di pausa in -m alla fine.
  - Quindi le proprietà di riga del Voynich (e71, e74–e76) hanno **due** spiegazioni possibili:
    - un procedimento riga per riga senza messaggio;
    - **un testo in versi, una riga per verso, in una lingua o in una grafia con giunture
      scritte (tipo sandhi)**.
  - Non dico che il Voynich sia sanscrito. Dico che la combinazione "giunture forti + riga chiusa
    + bordo forte" non è più una prova contro il contenuto.
- **Prossimo passo (e78).** Misurare i versi con sandhi su tutta l'impronta: ripetizioni,
  somiglianza fra righe, omogeneità di pagina, h2, parole uniche, unioni. Così si vede dove
  questa possibilità regge e dove cade.

## 1/10/2026 — e78: i versi con sandhi sulla pagella

- **Metodo.** Preregistrato. Deviazione tecnica D-013: la deriva è misurata alla distanza
  massima disponibile, perché i testi sono corti.
- **Risultati:**

  | testo | proprietà riprodotte |
  |---|---|
  | Manusmṛti | 4/17 (unioni, curva piatta, deriva, verticale) |
  | Raghuvaṃśa | 1/17 |
  | Plinio (controllo) | 1/17 |

  - **Dove falliscono:**
    - h2 3,40–3,47 (Voynich 2,24);
    - tipi su parole 0,50–0,67 (0,21);
    - omogeneità di pagina 0,003–0,015 (0,038);
    - legame in eccesso (0,78–0,83 contro 0,19);
    - bordo finale troppo forte nella Manusmṛti (148 contro 55).
  - **Ripetizione:** 0,42 e 0,75, più alta di Plinio (0,12) ma sotto il Voynich (1,01).
- **Lettura** (come previsto). Il verso con sandhi spiega le proprietà di riga ma non il resto
  dell'impronta, che resta lontana come per ogni lingua naturale scritta in alfabeto. Restano:
  - un testo in versi molto ripetitivo e codificato (abbreviazioni, sillabe) che abbassi h2 e i
    tipi;
  - oppure il procedimento senza messaggio.
- **Prossima prova (e79).** Distinguere fra "verso" e "riga elastica".
  - Un verso ha lunghezza fissa: dove lo spazio è ridotto dai disegni deve andare a capo a metà,
    e la riga dopo continua il verso, quindi il legame attraversa l'a capo.
  - Una riga elastica si accorcia e resta chiusa.

## 1/10/2026 — e79: verso fisso o riga elastica? (non valido)

- **Metodo.** Preregistrato. Legame attraverso l'a capo dopo righe corte (< 0,75 della mediana di
  pagina) e dopo righe piene.
- **Validità fallita.** Il controllo "verso con spazio limitato" dà Δ = −0,09, contro il ≥ 0,3
  richiesto. **L'esperimento non si legge.**
- **Causa (difetto di disegno).**
  - Ho classificato le righe per larghezza **scritta**. Nei versi impaginati in uno spazio
    stretto, la riga tagliata è piena rispetto al suo spazio e finisce fra le "piene". Le "corte"
    sono soprattutto i resti dei versi, che sono chiusi.
  - Inoltre nel Voynich H ci sono solo 101 coppie dopo righe corte. Con l'informazione mutua su
    tutto l'alfabeto la potenza è troppo bassa: un R di 0,3 non si distinguerebbe da 0.
- **Numeri solo descrittivi:**
  - Voynich H: R_corte 0,12 (n 101, z 0,3), R_piene 0,07;
  - tutto il testo: 0,01 e 0,01.
- **Se lo si riprende,** servono:
  - la classificazione per spazio **disponibile**, uguale nel controllo e nel Voynich;
  - una statistica più potente, come il log-rapporto di verosimiglianza della coppia sotto la
    tabella delle giunture dentro la riga.

## 1/10/2026 — e80: verso fisso o riga elastica? (seconda prova)

- **Metodo.** Preregistrato. Righe corte per spazio disponibile, ereditate dal Voynich nel
  controllo. Statistica di verosimiglianza sotto il modello delle giunture, con validazione a
  metà.
- **Validità:**
  - verso con spazio limitato: R_corte 0,51 contro R_piene 0,08, Δ 0,43 (✓);
  - verso senza limiti: R 0,00 (✓).
- **Voynich, tutto il testo:** **R_corte 0,19** (limite superiore 0,40, n 217) e R_piene 0,05
  (limite superiore 0,12).
  - **Lettura preregistrata: indeciso.** R_corte è sotto 0,2, ma il limite superiore tocca 0,40,
    e il criterio chiedeva < 0,4.
  - Il valore centrale è lontano da quello del verso spezzato (0,51), ma con 217 coppie non si
    esclude un piccolo effetto.
- **Voynich H:** R_corte 0,10 (limite 0,51, n 101), poca potenza.
- **Generatore:** R_piene 0,33 (z 3,9). Con questa statistica il generatore mostra un piccolo
  legame residuo attraverso l'a capo; il Voynich quasi nessuno (0,05).
- **Lettura.** Prova debole a favore della riga elastica: dopo una riga accorciata dai disegni,
  la riga dopo non sembra continuarla come farebbe un verso spezzato. Il verso a lunghezza fissa
  come spiegazione della chiusura perde un po' di plausibilità, ma non è escluso.

## 1/10/2026 — e81: direzione della giuntura (non valido), e un controllo esplorativo sulla chiave per riga

**e81** (preregistrato).

- **Misure:** IM condizionata regressiva (fine di w1 ~ inizio di w2, a parità di radice di w1) e
  progressiva (a parità di corpo di w2).
- **Validità fallita.**
  - Il criterio chiedeva un rapporto regressiva / progressiva > 2 nei versi sanscriti: la
    Manusmṛti dà 2,26, il **Raghuvaṃśa 1,36**.
  - Anche Plinio, che non ha sandhi, dà 2,16, quindi la misura non isola il sandhi.
  - **Non si legge.**
- **Descrittivo:** Voynich 0,87 (A 0,59, B 1,08); generatore con le giunture 0,76; e51 0,55;
  generatore senza giunture 0,22.

**Esplorativo, non preregistrato: una chiave diversa per ogni riga?**

- Un cifrario che cambia chiave (o alfabeto) a ogni riga spiegherebbe la riga chiusa. Darebbe
  però un **salto** di somiglianza fra parole della stessa riga e parole della riga adiacente.
- Con `misure.decadimento`:

  | distanza fra righe | distanza normalizzata | parole identiche |
  |---|---|---|
  | 0 (stessa riga) | 0,9615 | ×2,83 |
  | 1 | 0,9601 | ×2,50 |
  | 2 | 0,9636 | ×2,38 |
  | 6 | 0,9665 | ×2,13 |

  - Le parole della riga adiacente sono **altrettanto simili** di quelle della stessa riga.
    Nessun salto.
- **Lettura.** Una chiave per riga è poco probabile: la riga è chiusa per le giunture e per i
  bordi, non per il vocabolario. Lo stile cambia piano lungo la pagina, non a ogni riga.

## 1/10/2026 — e82: gli inizi di riga consecutivi si evitano

- **Metodo.** Preregistrato. **Deviazione D-014:** il primo nullo accoppiava una riga con se
  stessa e il controllo negativo era fallito (z −3,2). L'esecuzione è conservata in
  `risultati/scartati/`. Corretto il nullo (rimescolamento dell'ordine delle righe nella pagina) e
  rieseguito con gli stessi criteri.
- **Validità:** controllo positivo (marcatore a ciclo) z 918; controllo negativo z 0,6 (✓).
- **Risultato.** IM fra il primo segno di righe consecutive:

  | testo | prima parola | seconda parola |
  |---|---|---|
  | Voynich | **0,126 bit (z 24)** | 0,031 (z 4,7) |
  | lingua A | 0,179 (z 17) | |
  | lingua B | 0,109 (z 14) | |
  | Timm e Schinner | 0,027–0,029 (z 5–6) | |

  **Lettura preregistrata:** il segno d'inizio riga dipende da quello della riga prima, ben oltre
  la vicinanza fra righe.
- **Esplorativo, non preregistrato: che forma ha.** È soprattutto **evitamento**: due righe
  consecutive cominciano con lo stesso segno **meno della metà delle volte** attese.

  | coppia di inizi | rapporto osservato / atteso |
  |---|---|
  | stesso segno, in generale | 222 contro 520 (0,43) |
  | q → q | 0,20 |
  | d → d | 0,46 |
  | y → y | 0,51 |
  | q → ch | 2,5 |
  | o → q | 1,7 |
  | d → q | 1,5 |

  | posizione | rapporto stesso segno |
  |---|---|
  | seconda parola | 0,91 |
  | terza parola | 0,88 |
  | ultima parola | 0,92 |
  | prima parola, generatore | 0,94–0,97 |

  - L'effetto è **proprio della prima parola** di riga, e il generatore non lo ha.
- **Perché conta.** Una regola d'alternanza fra inizi di riga consecutivi è tipica di un elenco
  numerato o marcato (segni che cambiano da una voce all'altra) o di una convenzione di
  impaginazione. Un'abitudine casuale non la produce, e nessun generatore provato la ha. È stata
  trovata esplorando: prima di darle peso servono verifiche preregistrate (e83).

## 1/10/2026 — e83: l'evitamento fra inizi di riga è confermato

- **Metodo.** Preregistrato. S(k) = quota di righe a distanza k (stesso paragrafo) con lo stesso
  primo segno, divisa per l'attesa con 500 rimescolamenti.
  - Con questo nullo S(1) del ZL è 0,52, contro lo 0,43 esplorativo dell'e82, che usava un
    insieme di coppie un po' diverso.
- **Criterio di conferma** (S(1) < 0,7 con z < −4 nelle tre trascrizioni e nelle due lingue):
  **confermato.**

  | prova | S(1) | z |
  |---|---|---|
  | ZL | 0,52 | −11,8 |
  | IT | 0,52 | −11,4 |
  | GC (altro alfabeto) | 0,50 | −12,3 |
  | lingua A | **0,36** | −10,0 |
  | lingua B | 0,62 | −7,5 |

- **Sezioni** (descrittivo):

  | sezione | S(1) |
  |---|---|
  | erbario | **0,38** |
  | biologia | 0,51 |
  | altre | 0,56 |
  | ricette | 0,71 (z −3,3) |

- **Forma:**
  - S(2) = 1,196 (z +4,3), proprio al confine di 1,2 tra "alternanza" e "solo evitamento". Per la
    regola dichiarata è solo evitamento della ripetizione immediata, con una tendenza
    all'alternanza ABAB;
  - S(3) = 1,05: a distanza 3 l'effetto sparisce.
- **Senza il segno aggiunto:** S(1) = 0,71 (z −6,7). L'evitamento sta in gran parte nel segno
  aggiunto, ma non tutto.
- **Parola intera:** S(1) = 0,59 (z −2,1, poche coppie).
- **Lettura.**
  - **Due righe consecutive evitano di cominciare con lo stesso segno.** L'effetto riguarda solo la
    prima parola, non dipende dalla trascrizione, è più forte nella lingua A e nell'erbario, e
    nessun generatore provato lo produce.
  - Ipotesi in campo:
    1. **segni di voce o di numerazione** (ipotesi 1): un elenco con marcatori che cambiano da una
       riga all'altra;
    2. **scelta visiva dello scriba**, che evita di incolonnare lo stesso segno sul margine
       sinistro. Vale sia per un testo vero sia per uno inventato;
    3. **regola di un procedimento** che deriva l'inizio di riga da quello sopra, cambiandolo.
  - **Prossima prova (e84):** la struttura fuori dalla diagonale. Se, a parte l'evitare lo stesso
    segno, certi passaggi sono preferiti e in modo asimmetrico (X → Y sì, Y → X no), è una
    sequenza (numerazione, ordine). Se resta solo l'evitamento, simmetrico, è più probabilmente
    una scelta visiva.

## 1/10/2026 — e84: sequenza oltre l'evitamento; e85: niente distici (effetto di posizione)

**e84** (preregistrato).

- **Validità:**
  - controllo "sequenza": z > 1.000 in entrambe le misure;
  - controllo "solo evitamento": z 0,2 e −1,8 (✓).
- **Voynich:** struttura fuori dalla diagonale z **12,4**, asimmetria z **11,4**. Vale nelle lingue
  A (5,8 e 6,7) e B (10,0 e 7,6). Generatore: 2,1 e −0,9.
- **Lettura preregistrata:** oltre a evitare lo stesso segno, gli inizi di righe consecutive
  hanno passaggi preferiti e asimmetrici.
- **Esplorativo, matrice osservato / atteso:**

  | passaggio | rapporto |
  |---|---|
  | q → q | 0,23 |
  | o → o | 0,19 |
  | ch → ch | 0 |
  | ch ↔ sh (due segni simili) | 0,24 |
  | q → ch | 2,8 |
  | q → sh | 2,1 |
  | ch → t | 2,4 |
  | o → q | 1,9 |
  | d → q | 1,7 |

  - Asimmetrie: d → q 125 contro q → d 67; q → ch 57 contro 25; o → s 49 contro 19.

**e85** (preregistrato): la parità della riga nel paragrafo.

- **Validità:** controllo positivo (Manusmṛti) z 18,4; controllo negativo |z| < 3 (✓).
- **Voynich:** primo segno z 6,7, numero di parole z 10,5. Per la regola preregistrata sarebbe
  "righe a coppie in fase".
- **Confondimento non previsto (difetto di disegno).**
  - La seconda riga del paragrafo è sempre dispari, e l'ultima, che è corta, cade su una parità
    che dipende dalla lunghezza del paragrafo.
  - Controllo esplorativo: togliendo la seconda e l'ultima riga, l'effetto sparisce (primo segno
    z −0,5; numero di parole z 0,8).
  - **La lettura "distici" è ritirata:** è un effetto di posizione. La seconda riga comincia
    raramente per q (6% contro 15–21% delle altre) e spesso per o o d (23% e 26%).
- **Lo stesso confondimento sull'e83–e84?** Controllo esplorativo che tiene solo le coppie di
  righe con j ≥ 2, e poi j ≥ 3:

  | righe tenute | S(1) | z | sequenza (z) | asimmetria (z) |
  |---|---|---|---|---|
  | j ≥ 2 | 0,50 | −11,0 | 9,4 | 9,2 |
  | j ≥ 3 | 0,51 | −8,6 | 8,3 | 7,4 |

  - Lingua A, j ≥ 3: S(1) 0,38. **L'evitamento e la sequenza restano:** non dipendono dalla
    seconda riga.
- **Lettura complessiva della serie e82–e85.**
  - Gli inizi di righe consecutive si evitano e preferiscono certi passaggi.
  - Non c'è una fase a coppie legata all'inizio del paragrafo, quindi non sono distici: è una
    regola che lega ogni inizio di riga a quello della riga sopra.
  - Fra i segni simili d'aspetto (ch e sh) l'evitamento vale anche incrociato, il che fa pensare
    a una componente **visiva**: non incolonnare segni uguali o simili sul margine sinistro.

## 1/10/2026 — Esplorativo: i versi veri non evitano; e86: nemmeno il gibberish umano

- **Esplorativo, non preregistrato.** S(1) sulla prima lettera delle righe consecutive:
  - *Eneide*, un verso per riga: **1,01**;
  - Manusmṛti, mezzo verso per riga: **1,18** (attrazione);
  - nel Voynich, fra gli inizi che non sono y/d/s/o, l'evitamento è più forte (0,31) che fra gli
    inizi in y/d/s/o (0,74): non sta tutto nel segno aggiunto.
- **e86** (preregistrato): gibberish scritto a mano (Gaskell e Bowern, 38 documenti).
  - **Validità:** Bibbia inglese 0,99, Bibbia latina 1,22, entro 0,8–1,25 (✓).
  - **Gibberish:** S(1) **1,05** (z 0,7); seconda parola 1,00.
  - **Lettura:** chi inventa un testo **non** evita di cominciare due righe con la stessa lettera.
    L'evitamento non è una firma generale della composizione libera.
- **Stato.** L'evitamento fra inizi di riga (S ≈ 0,5) non c'è in nessun testo provato: prosa,
  versi latini e sanscriti, gibberish umano, generatore. È una proprietà nuova da spiegare.
- **Prossima prova (e87).** La colonna delle prime parole è scritta come una sequenza a sé? Se sì,
  la regola delle giunture dovrebbe valere **in verticale**: la fine della prima parola di una
  riga decide l'inizio della prima parola della riga sotto, con la stessa tabella delle giunture
  dentro la riga.

## 1/10/2026 — e87: niente giunture verticali nella colonna delle prime parole

- **Metodo.** Preregistrato. Le coppie verticali (ultimo segno della prima parola di L → primo
  segno della prima parola di L+1) sono valutate sotto il modello delle giunture dentro la riga.
- **Validità:**
  - controllo positivo (colonna = testo continuo): R 0,73 (z 31) (✓);
  - controllo negativo: R 0,02 (✓).
- **Voynich:** R **−0,02** (z −0,7); A −0,12; B 0,01. Seconda parola ≈ 0.
- **Generatore:** R 0,27 (z 3,8), un legame verticale debole che il Voynich non ha.
- **Lettura.** La colonna delle prime parole **non** è una sequenza con giunture. L'evitamento fra
  inizi di riga non viene dalla regola delle giunture applicata in verticale.
- **Prossima prova (e88).** "Copia e cambia l'inizio": la prima parola di una riga è una copia
  della prima parola sopra con l'inizio cambiato? Allora i corpi (la parola senza il primo segno)
  dovrebbero somigliarsi più del caso.

## 1/10/2026 — e88: la prima parola di riga non è copiata da quella sopra

- **Metodo.** Preregistrato. Somiglianza verticale dei corpi (parola senza il primo segno) per
  la colonna delle prime parole e per quella delle seconde.
- **Validità:** controllo positivo (copia e cambio su metà delle righe): corpi identici ×5,27
  (z 52) (✓).
- **Risultati** (rapporto con l'atteso):

  | testo | colonna | corpi identici | somiglianza | parole identiche |
  |---|---|---|---|---|
  | Voynich | prime parole | **1,03** (z 0,2) | 1,08 (z 4,3) | **0,58** (z −2,4) |
  | Voynich | seconde parole | **1,47** (z 4,1) | 1,12 (z 6,2) | 1,27 |
  | lingua A | prime parole | 0,57 | 1,01 | 0,28 |
  | lingua A | seconde parole | 1,00 | 1,10 | |
  | lingua B | prime parole | 1,19 | 1,14 | 0,73 |
  | lingua B | seconde parole | 1,86 (z 5,1) | | |
  | Timm e Schinner | prime parole | 1,33 (z 2,7) | | 1,19 |
  | Timm e Schinner | seconde parole | 1,33 (z 2,9) | | 1,34 |

- **Lettura** (criterio preregistrato non raggiunto: nessun "copia e cambio").
  - Nel Voynich la prima parola di riga **non deriva** dalla prima parola sopra; anzi la evita
    (parole identiche 0,58).
  - Le parole in seconda posizione mostrano la solita traccia di copia verticale (e58), le prime
    no.
  - Il generatore copia allo stesso modo in tutte le colonne.
- **Quadro della riga** (e71–e88): la prima parola è **speciale**.
  - Porta spesso un segno aggiunto (y, d, s, o: e73).
  - È scelta per essere diversa da quella sopra: nel segno iniziale (e83, e84) e nella parola
    intera (e88).
  - Non viene copiata, mentre il resto della riga sì.
  - Questo è il comportamento di una **intestazione di voce**: voci consecutive con nomi diversi
    e descrizioni simili.
  - Non è il comportamento di una prosa mandata a capo, di versi o di un generatore ad
    autocitazione.

## 1/10/2026 — e89: le etichette non somigliano alle prime parole di riga

- **Metodo.** Preregistrato. JSD del primo e dell'ultimo segno fra le 1.164 etichette e le parole
  iniziali, interne e finali dei paragrafi; bootstrap.
- **Risultati:**

  | misura | iniziali | interne | finali |
  |---|---|---|---|
  | D_ini (primo segno) | 0,231 | 0,186 | **0,126** |
  | D_fin (ultimo segno) | 0,078 | **0,047** | 0,056 |

  - Nessuno dei tre ordini preregistrati (0% dei ricampionamenti): **esito misto**.
  - **Primo segno:**
    - etichette: o 54%, d, y, ch, a;
    - prime parole di riga: d, y, o, q, s, t;
    - parole interne: o, q, ch, sh.
- **Lettura.**
  - Le etichette, che sono con ogni probabilità nomi, sono **più lontane proprio dalle prime parole
    di riga**.
  - L'interpretazione "intestazione di voce = nome" si **indebolisce**: se le prime parole di riga
    sono speciali, non lo sono perché sono nomi come le etichette.
  - Il fatto che il primo segno delle etichette somigli a quello delle parole finali è inatteso.
    Lo annoto senza leggerlo.

## 1/10/2026 — Esplorativi sulla prima parola; e90: l'evitamento è comune a tutte le mani

**Esplorativi, non preregistrati.**

- **Etichette consecutive** sulla stessa pagina: S 0,99. Nessun evitamento: è proprio degli
  inizi di riga del testo.
- **Prima parola di L+1 e ultima parola di L:** corpi identici 1,04, nessuna relazione. La prima
  parola non deriva nemmeno dall'ultima parola sopra.
- Nello stesso controllo, le righe "stessa colonna" usavano un nullo con lo stesso difetto della
  D-014 (coppie di una parola con se stessa) e i loro rapporti **non valgono**. Lo scrivo per
  non riusarli.

**e90** (preregistrato). S(1) per mano (variabile $H, attribuzioni di Davis):

| mano | S(1) | z |
|---|---|---|
| 1 (lingua A) | **0,36** | −9,8 |
| 2 (B) | 0,54 | −6,7 |
| 3 (B, più un po' di A) | 0,70 | −3,8 |

- **Lettura preregistrata: proprietà comune.** Tutte e tre le mani evitano, con intensità
  decrescente.
- Non è l'abitudine di un solo scriba: è una regola condivisa del modo di scrivere questo testo
  (o del procedimento), applicata con più o meno rigore da mani diverse.

## 1/10/2026 — e91: le giunture del Voynich sono nella norma delle lingue del mondo

- **Metodo.** Preregistrato. Misura "confine" (parole interne) su 110 Bibbie (prime 35.000
  parole, righe di 8), sui versi sanscriti e sul Voynich.
- **Risultato.** Il Voynich (**0,188 bit**) è al **17° posto su 110**.

  | lingua | eccesso (bit) |
  |---|---|
  | q'eqchi' | 0,40 |
  | barasana | 0,24 |
  | ojibwa | 0,24 |
  | tagalog | 0,22 |
  | hindi | 0,21 |
  | cabilo | 0,19 |
  | amarico | 0,19 |
  | k'iche' | 0,17 |
  | malgascio | 0,16 |
  | gaelico | 0,16 |
  | ungherese | 0,14 |
  | esperanto | 0,13 |
  | francese | 0,12 |
  | inglese | 0,10 |
  | italiano | 0,07 |
  | **latino** | **0,033** (fra i più bassi) |
  | finlandese | 0,019 (il più basso) |

  - **Previsione sbagliata:** avevo previsto le lingue europee sotto 0,06, ma francese e
    ungherese stanno sopra 0,12.
  - **Non confrontabili:** le scritture in cui una parola è uno o due caratteri (cinese 1,25,
    giapponese, coreano). Lì la misura coglie la dipendenza fra parole intere.
- **Lettura. Correzione importante rispetto al dossier.** Il dossier presentava il legame forte
  fra parole come un indizio contro una lingua naturale, ma il confronto era soprattutto con il
  latino, che è una delle lingue con il legame più debole. Rispetto alle lingue del mondo, il
  legame del Voynich è **normale**. Spesso nelle lingue lo producono le parole grammaticali brevi
  e frequenti (tagalog *ng*, *sa*, *ang*) o le mutazioni (gaelico).
  - **Resta anomalo** che il legame si fermi alla fine della riga (e74): in nessuna prosa lo fa.
  - Lo spostamento va ricordato nel white paper: **la forza delle giunture non distingue; la
    loro chiusura alla riga sì.**
- **Nota all'e91.** L'e13 del dossier, standardizzato su 85 Bibbie, metteva già il "legame
  attraverso lo spazio" a +1,7 deviazioni standard, cioè dentro la gamma. L'e91 conferma quel
  numero; la correzione riguarda il modo in cui il dossier lo raccontava (spesso contro il solo
  latino).
- **Le anomalie davvero estreme restano:**

  | misura (e13) | deviazioni standard |
  |---|---|
  | somiglianza nella riga | +10,7 |
  | spazio prevedibile | +3,9 |
  | h2 | −3,3 |
  | ripetizioni immediate | +2,5 |

  - A queste si aggiungono le proprietà di riga di questa sessione: chiusura, segno aggiunto,
    evitamento fra inizi, prima parola non copiata.

## 1/10/2026 — e92: nessuna cornice di riga

- **Metodo.** Preregistrato. IM fra il primo segno della prima parola e l'ultimo segno
  dell'ultima, nella stessa riga, contro i rimescolamenti delle ultime parole nella pagina.
  - Prima del commit il minimo è passato da 3 a 4 parole, perché con 3 la seconda e la penultima
    coincidono.
- **Validità:** controllo positivo (cornici y…m / s…g) z 747; Plinio codificato z −0,3 (✓).
- **Voynich:** cornice z −0,5 (A −1,5; B 0,2); interno z 1,1. Generatore: 2,2.
- **Lettura.** Apertura e chiusura della riga sono **indipendenti**: la riga ha bordi propri, ma
  non una cornice accoppiata.

## 1/10/2026 (notte) — Punto della situazione: la riga (e70–e92)

**Che cosa è stabilito** (preregistrato, con controlli validi):

1. **La riga è un'unità chiusa** (e74, e76).
   - Il legame fra parole vicine (0,20 bit dentro la riga) sparisce all'a capo (R 0,01). Nella
     prosa mandata a capo resta (Plinio 0,67).
   - Nella sezione delle ricette le righe sono anche **piene** (CV 0,049).
2. **Bordi forti e diversi da quelli del generatore** (e71).
   - All'inizio della riga sono arricchiti s, y, t, d; alla fine g e m.
   - Il generatore mette all'inizio i gallow e alla fine troppe m.
3. **All'inizio della riga si aggiunge un segno** (y, d, s, o) a una parola normale (e73). È
   proprio della prima parola: sulla seconda è quasi nullo.
4. **Profilo interno** (e75). *sh* è più frequente verso l'inizio, *d* e *t* verso la fine. È un
   gradiente dai bordi, non colonne.
5. **Inizi di righe consecutive** (e82–e84, e90).
   - Si evitano: S(1) ≈ 0,5. Il risultato regge in tre trascrizioni, in due lingue, in tre mani
     e togliendo la seconda riga del paragrafo.
   - Hanno passaggi preferiti e asimmetrici.
   - Non c'è alternanza in fase con il paragrafo (e85, distici ritirati).
6. **La prima parola non è copiata** dalla riga sopra (e88), mentre la seconda sì. Non deriva
   nemmeno dall'ultima parola sopra (esplorativo).
7. **Fatti negativi:**
   - niente giunture verticali fra prime parole (e87);
   - nessuna cornice apertura–chiusura (e92);
   - le etichette non somigliano alle prime parole (e89).

**Confronti:**

- **Versi sanscriti con sandhi** (e77): riproducono 1 e 2, cioè la riga chiusa, i bordi forti e
  la -m finale. Falliscono però il resto dell'impronta (e78: 1–4/17) e non evitano gli inizi
  (Manusmṛti 1,18).
- **Eneide e gibberish umano** (e86): nessun evitamento.
- **Generatori di Timm e Schinner e varianti:** nessuno ha le proprietà 3, 4, 5 e 6 nella forma
  giusta.
- **La forza delle giunture è nella norma** delle lingue del mondo (e91, 17ª su 110). Non è un
  argomento contro una lingua; lo è la loro chiusura alla riga.

**Che cosa significa per le tre ipotesi:**

- **Ipotesi 1 (contenuto non in prosa):** una riga per voce spiegherebbe la chiusura e la prima
  parola "nuova", ma non le righe piene (e76), e le prime parole non somigliano ai nomi delle
  etichette (e89). Una tabella o un elenco a righe di lunghezza fissa resta possibile.
- **Ipotesi 2 (convenzioni di scrittura o cifratura):** servirebbe una cifratura che riparte a ogni
  riga, con una prima parola trattata a parte. Una chiave per riga è sfavorita, perché il
  vocabolario non salta fra le righe (esplorativo, e81).
- **Ipotesi 3 (nessun messaggio):** servirebbe un procedimento riga per riga in cui la prima
  parola è scelta a parte e diversa da quella sopra, mentre il resto è copiato. Il generatore
  noto non lo fa; un procedimento umano potrebbe, ma il gibberish dei volontari non lo mostra.
- In tutti e tre i casi **la riga è l'unità di composizione**, e la prima parola ha un ruolo suo.
  È la principale novità di questa fase.

**Esperimenti non validi o ritirati:** e79, e81, e85 (lettura distici); D-013, D-014.

**In corso:** replica dell'e20 (D-009), in sottofondo.

## 1/10/2026 — e93: la prima parola viene dal vocabolario della pagina (quasi come le altre)

- **Metodo.** Preregistrato. Quota di occorrenze il cui tipo compare in un'altra riga della stessa
  pagina, contro il rimescolamento delle righe fra le pagine.
- **Validità:** parole interne del Voynich 1,37 (z 38) (✓).
- **Risultati** (legame):

  | testo | prima | seconda | interne | ultima |
  |---|---|---|---|---|
  | Voynich | 1,27 | 1,29 | 1,37 | 1,24 |
  | lingua A | 1,25 | | 1,35 | |
  | lingua B | 1,13 | | 1,15 | |
  | Timm e Schinner | 1,72 | | 1,50 | |

- **Lettura preregistrata.** Per il Voynich nel suo insieme vale per un soffio "meno legata"
  (1,27 contro la soglia di 1,296); per la lingua B è indeciso.
  - L'ultima parola ha lo stesso calo (1,24), quindi è un effetto delle **forme di bordo** (segni
    aggiunti o sostituiti, che danno varianti più rare), non una fonte diversa per la prima
    parola.
  - **Conclusione pratica:** la prima parola viene dal vocabolario della pagina; è "nuova" solo
    rispetto alla riga sopra (e88).

## 1/10/2026 — Letteratura sulla riga: che cosa era già noto

- **D'Imperio 1978** (OCR in cache, SHA in FONTI.md), §4.4:
  - "elementi simili a prefissi" (o e y in EVA) aggiunti davanti a parole che compaiono anche
    senza. È il segno aggiunto dell'e73, che però lì non è legato alla riga;
  - le etichette cominciano spesso con *o* e quasi mai con i gallow. L'e89 lo ritrova (o 54%);
  - la prima riga del primo paragrafo comincia con pochi segni (i gallow). È noto, e l'abbiamo
    escluso dalle misure.
- **Currier, la riga come "unità funzionale"** ("Line As A Functional Unit", spesso abbreviato
  LAAFU). È citato in letteratura, ma **non verificato alla fonte**: i suoi articoli del 1976 non
  sono nella cache. Nel white paper le proprietà di riga (bordi distinti) vanno attribuite a lui
  come osservazione qualitativa, con questa riserva.
- **Che cosa sembra nuovo in questa fase** (da verificare con una ricerca bibliografica prima del
  white paper):
  - la chiusura misurata delle giunture all'a capo e il confronto con i versi con sandhi;
  - l'evitamento e la sequenza fra inizi di righe consecutive;
  - la prima parola non copiata dalla riga sopra;
  - il fatto che il legame fra parole sia nella norma delle lingue del mondo.

## 1/10/2026 — Ricerca bibliografica sulla riga

Ricerca web dell'1/10. Letto per intero solo Feaster 2021 (SHA in FONTI.md).

- **Feaster 2021**, *Rightward and Downward in the Voynich Manuscript* (blog Griffonage).
  - Le parole in *Sh* stanno più a sinistra nella riga delle corrispondenti in *ch*, con un
    picco sulla **seconda parola**.
  - Ci sono effetti analoghi lungo il paragrafo ("downwardness").
  - Cita Currier sulla rarità delle parole in ch/Sh a inizio riga, e Smith e Ponzi sulle parole
    in seconda posizione nel fascicolo 20.
  - **Il gradiente dell'e75 è quindi già noto** (Feaster, Smith e Ponzi): l'e75 lo conferma con un
    test a permutazione e mostra che i generatori non lo hanno.
  - Feaster lo trova "rilevabile ovunque" lungo la riga; il nostro controllo esplorativo dava un
    effetto che cala fino a z 2,2 togliendo due parole per lato. È una differenza da guardare nel
    white paper.
- **Altri lavori trovati, da leggere prima del white paper:**
  - Vogt, *The Line as a Functional Unit in the Voynich Manuscript*
    (voynichthoughts.files.wordpress.com/2012/11/the_voynich_line.pdf);
  - Smith e Ponzi 2019, *Glyph combinations across word breaks in the Voynich manuscript*, sulle
    giunture **dentro** la riga, dichiaratamente escluse quelle all'a capo;
  - arXiv 2608.17096 (già in cache), con una divergenza del primo segno d'inizio riga di 0,528
    per le prime righe di paragrafo contro 0,179 per le altre.
- **Che cosa resta, per ora, senza precedenti trovati:**
  - la chiusura misurata delle giunture all'a capo (e74) e il confronto con i versi con sandhi
    (e77);
  - l'evitamento e la sequenza fra inizi di righe consecutive (e82–e84, e90);
  - la prima parola non copiata dalla riga sopra (e88).
  - Va verificato su Vogt e su Smith e Ponzi prima di dirlo nel white paper.
- **Letti anche** Vogt 2012 e Smith e Ponzi 2019 (SHA in FONTI.md).
  - **Vogt** studia la lunghezza delle parole lungo la riga: la prima parola è più lunga, la
    seconda ha un calo, la lunghezza scende verso la fine (spiegata dalla composizione per righe).
    Non tratta il legame attraverso l'a capo né la relazione fra righe consecutive.
  - **Smith e Ponzi** studiano le giunture dentro la riga ed escludono esplicitamente gli spazi
    all'a capo.
  - Né loro né Feaster misurano la **chiusura delle giunture all'a capo** (e74) o la **dipendenza
    fra inizi di righe consecutive** (e82–e84, e88). Per quanto trovato finora sono contributi
    nuovi; la ricerca non è esaustiva, e va detto.
- **Esplorativo, non preregistrato: l'"effetto prima parola" di Vogt.**
  - La prima parola di riga è più lunga: 4,74 segni contro 4,43 delle interne e 4,28 della
    seconda (righe di almeno 4 parole).
  - Togliendo il segno iniziale alle prime parole che cominciano per y, d, s, o e il cui resto è
    una parola attestata a metà riga, la media scende a **4,25**.
  - Il criterio è largo (tocca 1.548 prime parole su 3.162, alcune senza segno aggiunto, come
    *daiin* → *aiin*), quindi spiega anche più del necessario.
  - **Lettura:** il segno aggiunto dell'e73 basta a spiegare l'effetto che Vogt non sapeva
    spiegare.
  - Il calo della seconda parola (4,28), che Vogt nota anch'esso, resta senza spiegazione.
- **Esplorativo, non preregistrato: il "calo della seconda parola" di Vogt.**
  - La seconda parola è lunga in media 4,29 segni, le interne 4,43 (righe di almeno 5 parole).
  - Se la seconda parola avesse, per ogni primo segno, le lunghezze delle interne, l'attesa
    sarebbe **4,32**: il calo è quasi tutto **composizione**.
  - In seconda posizione ci sono più parole in *sh* (17% contro 9%) e in *ch* (22% contro 18%),
    che sono corte (circa 4 segni), e meno parole in *q* (14% contro 18%), che sono lunghe (5,8).
  - Il calo di Vogt è quindi lo stesso fenomeno della preferenza di sh/ch per la seconda posizione
    (Feaster; Smith e Ponzi).
  - **Le due "anomalie di lunghezza" di Vogt hanno così una spiegazione semplice:** il segno
    aggiunto (prima parola) e la scelta del tipo di parola (seconda). Resta da spiegare perché la
    seconda posizione preferisca sh/ch.
- **Esplorativo, non preregistrato: le giunture spiegano la preferenza per sh/ch in seconda
  posizione?** **No.**
  - Dalla fine della prima parola (y 971, n 627, r 558, l 403…) la tabella delle giunture interne
    prevede per la seconda parola la stessa quota delle interne: ch 0,179, sh 0,093.
  - Si osservano invece ch **0,235** e sh **0,161**, e meno parole in o (0,173 contro 0,232
    previste).
  - **Lettura:** la seconda posizione ha una preferenza **propria** per le parole in ch/sh, non
    ereditata dalla giuntura con la prima parola. La riga ha quindi uno schema dei primi due posti:
    una prima parola con un segno aggiunto, poi una parola in ch/sh. Anche questo manca ai
    generatori (e75).

## 1/10/2026 — e94: preferenza per ch/sh vicino all'inizio della riga, a gradiente

- **Metodo.** Preregistrato. Quota di parole in ch/sh osservata contro quella prevista dalla
  tabella delle giunture, a partire dalla fine della parola precedente.
- **Risultati** (rapporto e intervallo al 95%):

  | testo | posizione 2 | posizione 3 |
  |---|---|---|
  | ZL | **1,43** (1,37–1,49) | 1,18 (1,12–1,24) |
  | IT | 1,37 | 1,15 |
  | lingua A | 1,48 | 1,21 |
  | lingua B | 1,37 | 1,14 |
  | Timm e Schinner | 1,05 | 1,02 |

- **Criterio preregistrato non soddisfatto.** La posizione 3 doveva essere normale (intervallo
  con 1 o sotto 1,1), ma è anch'essa in eccesso. Non si tratta di una regola della sola seconda
  posizione.
- **Lettura.** La preferenza per le parole in ch/sh oltre le giunture è reale (in entrambe le
  trascrizioni e le lingue) e **decresce dall'inizio della riga**: 1,43, poi 1,18, poi le interne.
  È il gradiente di Feaster misurato a parità di giunture. Il generatore non lo ha.

## 1/10/2026 — e95: famiglie di segni intercambiabili, con scelta legata alla posizione

- **Metodo.** Preregistrato. Indice A = JSD fra i "corpi" (resto della parola) delle parole che
  cominciano con X e con Y, diviso per la JSD di divisioni casuali. A ≈ 1 vuol dire stessa
  continuazione.
- **Coppie con A ≤ 1,5 nel Voynich** (10):

  | coppia | A |
  |---|---|
  | ckh/cth | 1,06 |
  | r/s | 1,09 |
  | k/t | 1,18 |
  | ch/ckh | 1,20 |
  | **ch/sh** | **1,26** |
  | d/r | 1,37 |
  | ckh/sh | 1,44 |
  | d/s | 1,45 |
  | p/t | 1,46 |
  | r/t | 1,48 |

  - Si formano tre famiglie: {ch, sh, ckh, cth}, {k, t, p}, {d, r, s}.
- **La scelta dipende dalla posizione** (nullo: permutazione fra parole con lo stesso corpo):

  | coppia | dipendenza | dettaglio |
  |---|---|---|
  | ch/sh | riga z 17; prima riga del paragrafo molto forte | sh 51% nella prima riga del paragrafo contro 32%; sh 58% a inizio riga, 23% a fine riga |
  | k/t | riga z 20 | t 79% a inizio riga, 35% all'interno |
  | p/t | prima riga del paragrafo z 15 | p nella prima riga: t solo 40% contro 89% |
  | r/s | riga z 32 | s 97% a inizio riga |
  | d/s | riga z 23 | |

- **Criterio preregistrato per ch/sh: soddisfatto** (A ≤ 1,5 e z > 4).
- **Tarature, esplorative, dopo l'esecuzione:**
  - lingue vere (latino, italiano, inglese, tedesco; prime 35.000 parole): **nessuna** coppia di
    iniziali con A ≤ 1,5; il minimo è 2,2–4,3;
  - generatore di Timm e Schinner: 6 coppie, **solo fra i gallow** (f/p/k/t, A 0,97–1,20), che
    il generatore scambia per costruzione. Non ha ch/sh né d/r/s;
  - Naibbe: 1 coppia.
- **Lettura.**
  - Il Voynich ha **famiglie di segni intercambiabili all'inizio della parola**: stesse
    continuazioni, e la scelta dentro la famiglia dipende dalla posizione nella riga e nel
    paragrafo. Nelle lingue in alfabeto non succede.
  - **Due interpretazioni:**
    1. **allografi:** forme dello stesso segno scelte per posizione, come la s lunga e la s tonda,
       o le iniziali ornate della prima riga. È una convenzione grafica che non porta significato;
    2. **uno "slot" combinatorio:** l'iniziale e il resto della parola si scelgono in modo
       indipendente, come in un sistema a tabelle o in un procedimento.
  - Le due non si separano con questa misura. In ogni caso, per una decifrazione questi segni non
    vanno trattati come lettere indipendenti di un alfabeto.
  - La dipendenza dalla posizione (sh, p e t vicino all'inizio della riga o del paragrafo) è una
    proprietà di **impaginazione**, come le lettere ornate. Contribuisce alle "anomalie di riga"
    viste in e71–e94.

## 1/10/2026 — e96: l'evitamento riguarda le classi, non le forme

- **Metodo.** Preregistrato. S(1) sul primo segno, sulla famiglia del primo segno (famiglie
  dell'e95) e dentro la famiglia.
- **Risultati:**

  | livello | S(1) | z |
  |---|---|---|
  | primo segno | 0,52 | −12,0 |
  | **famiglia** | **0,61** | **−12,4** |
  | dentro la famiglia (261 coppie) | 0,90 | −2,1 |

- **Lettura preregistrata: unità sottostante.**
  - Due righe consecutive evitano di cominciare con la stessa **classe** (q, o, y, {d, r, s},
    {ch, sh…}, {k, t, p, f}).
  - Dentro una classe non c'è variazione grafica: lo scriba non alterna d e s, o ch e sh, per non
    ripetersi.
  - Non è quindi un fatto di forme o di estetica fine. È una regola su che tipo di parola apre la
    riga rispetto alla riga sopra.
- **Esplorativo, non preregistrato: sensibilità dell'impronta alla fusione delle famiglie.**
  - Si usano come rappresentanti ch, cth, t e d.

  | misura | originale | fuso all'inizio della parola | fuso ovunque |
  |---|---|---|---|
  | h2 | 2,24 | 2,14 | **2,03** |
  | tipi | 0,210 | 0,187 | 0,143 |
  | parole uniche | 0,68 | 0,67 | 0,63 |
  | spazio | 0,66 | 0,67 | 0,59 |
  | ripetizione | 1,01 | 0,97 | 1,03 |
  | somiglianza nella riga | 0,038 | 0,036 | 0,034 |
  | legame | 0,188 | 0,178 | 0,174 |

  - **Lettura:** se le famiglie sono allografi, il testo "vero" è ancora più prevedibile (h2 più
    bassa, meno tipi), cioè ancora più lontano da una lingua in alfabeto. Le anomalie di
    ripetizione e di somiglianza non dipendono dal distinguere o no i segni delle famiglie.

## 1/10/2026 — Decifrazioni annunciate di recente (punto 8 del dossier)

- **Ricerca web dell'1/10.** Le proposte recenti trovate, per esempio "Deciphering the Voynich
  Manuscript Complete 2025" (ResearchGate e Academia) e il "metodo dell'àncora dai", **non hanno
  una chiave algoritmica pubblica**: le letture si appoggiano a "indizi visivi" scelti caso per
  caso. Non si possono mettere alla prova con i nostri controlli (testo senza messaggio, ordine
  delle parole) e non le provo.
- **Il Naibbe** di Greshko (*Cryptologia*, 2025) è già nel corpus (e31, e43, e71–e74). Non
  riproduce la chiusura della riga: legame debole (0,0014 bit), R ≈ 1 una volta mandato a capo.

## 1/10/2026 — e97: la chiusura della riga è robusta

- **Metodo.** Preregistrato. R dell'e74 su altre trascrizioni e per mano.

  | prova | R | legame dentro la riga |
  |---|---|---|
  | ZL | 0,006 | |
  | IT | 0,010 | |
  | GC (altro alfabeto, un carattere per segno) | 0,040 | |
  | mano 1 | −0,020 | |
  | mano 2 | 0,060 | |
  | mano 3 | −0,002 | |
  | tutte | | da 0,14 a 0,26 bit, z da 57 a 273 |

- **Criterio preregistrato soddisfatto: robusta.** La riga chiusa non dipende dalla trascrizione,
  dall'alfabeto di trascrizione né dallo scriba.

## 1/10/2026 — e98: il verso chiude la riga anche senza sandhi. Svolta nella lettura della riga

- **Metodo.** Preregistrato. R dell'e74 per i poeti latini, un verso per riga e di seguito.
- **Criterio preregistrato soddisfatto:** 4 testi conformi su 5 validi.

  | testo | R per versi | R di seguito | legame dentro la riga | CV |
  |---|---|---|---|---|
  | Ovidio, *Metamorfosi* | **0,03** | 0,89 | 0,121 bit | 0,078 |
  | Lucrezio | **0,04** | 0,89 | 0,112 bit | 0,080 |
  | Orazio | **0,15** | 0,89 | | 0,082 |
  | Giovenale | **0,19** | 0,91 | | 0,091 |
  | *Eneide* | 0,12 | 0,87 | | 0,087 |

  - Marbodo è troppo breve: 196 versi tenuti dal filtro, R per versi −1,12, non interpretabile.
- **Esplorativo, non preregistrato: bordi del verso latino** (rapporto con il nullo, come
  nell'e71):

  | testo | bordo inizio | bordo fine |
  |---|---|---|
  | Ovidio | 25 | 115 |
  | Lucrezio | 35 | 68 |
  | *Voynich* | *23* | *55* |
  | prosa mandata a capo | 4,6 | 1,1 |

  - Alla fine del verso latino sono arricchite o, u, s, i, m: sono le chiuse dell'esametro.
- **Che cosa i versi NON hanno:**
  - evitamento fra inizi (S(1) da 0,92 a 1,13; Voynich 0,52);
  - segno aggiunto all'inizio (0,71–0,92).
- **Lettura.**
  1. La chiusura della riga, i bordi forti e le righe di lunghezza regolare del Voynich sono
     **esattamente ciò che fa un testo in versi impaginato un verso per riga**, in latino come in
     sanscrito, con sandhi o senza.
  2. Il metro **aumenta** anche il legame fra parole dentro il verso: Ovidio 0,12 contro Plinio
     0,03. Il Voynich (0,19) sta fra il verso latino e il verso sanscrito.
  3. Le proprietà di riga che nei giorni scorsi sembravano chiedere un procedimento riga per riga
     hanno quindi una spiegazione naturale semplice: **il testo è in versi**.
  - L'ipotesi 1 prende la forma concreta di "testo in versi, un verso per riga". Esistono erbari
    medievali in versi: il *Macer floridus*, in esametri, fu molto diffuso nel Quattrocento. È un
    genere plausibile per un erbario.
  - **Restano fuori dal verso:**
    - l'evitamento fra inizi di righe consecutive e il segno aggiunto;
    - le anomalie di vocabolario: h2 bassa, ripetizioni ×1,0, somiglianza nella riga +10,7
      deviazioni standard.
  - Una possibilità da provare: un testo in versi scritto in un sistema che rende le sillabe con
    gruppi di segni (h2 bassa), con formule ripetute.
- **Prossimo passo (e99).** Il verso latino sulla pagella intera, come l'e78 per il sanscrito.

## 1/10/2026 — e99: il *Macer floridus* ha la riga del Voynich, non il suo vocabolario

- **Metodo.** Preregistrato. Erbario in esametri (XI secolo), edizione Choulant 1832 (OCR):
  2.177 versi, 79 capitoli, uno per pianta, 13.484 parole.
- **Proprietà di riga:**

  | misura | *Macer* | Voynich |
  |---|---|---|
  | R, un verso per riga | **−0,004** | 0,006 |
  | R, di seguito | 0,657 | |
  | legame dentro la riga | 0,145 bit | 0,20 |
  | CV | 0,088 | 0,049 (S) |
  | bordo inizio | **22,0** | 23 |
  | bordo fine | 17,8 | 55 |
  | S(1) inizi consecutivi | 0,95 | **0,52** |
  | prima parola, corpi identici con la riga sopra | 0,79 | 1,03 |

  - Fine riga: m ×1,86, r, s. Inizio riga: u, h, a, e.
- **Pagella: 0/17**, come ogni lingua naturale: h2 3,31, ripetizione 0,08, omogeneità 0,000,
  tipi 0,29.
  - Anche il bordo di riga fallisce la banda, per la fine: 17,8 è meno della metà di 55.
- **Lettura (previsioni confermate).**
  - Un erbario medievale in versi, impaginato un verso per riga, ha **la stessa chiusura della
    riga** e **lo stesso bordo d'inizio** del Voynich, con la m arricchita alla fine.
  - Non ha l'evitamento fra inizi, né il bordo di fine così forte, né il vocabolario del Voynich
    (h2 bassa, ripetizioni, omogeneità di pagina).
  - **Quadro attuale:** il Voynich ha **righe da poesia** e **parole da procedimento** (o da un
    sistema di scrittura molto diverso da un alfabeto). La riga non è più un argomento contro il
    contenuto; il vocabolario sì.

## 1/10/2026 — e100: l'erbario in versi cifrato non arriva al vocabolario del Voynich

- **Metodo.** Preregistrato. *Macer floridus*, un verso per riga e un capitolo per pagina,
  cifrato in quattro modi; proprietà di riga e pagella completa (18 proprietà).
- **Risultati:**

  | cifratura | pagella | R | bordo ini/fin | S(1) | h2 | tipi | ripetizione | omogeneità |
  |---|---|---|---|---|---|---|---|---|
  | verboso (vedi nota) | 0/18 | **−0,01** | 30 / 21 | 0,95 | 3,30 | 0,29 | 0,08 | 0,000 |
  | codice per parola | 3/18 | (legame ≈ 0) | 3,6 / 2,1 | 1,05 | 2,33 | 0,29 | 0,08 | 0,006 |
  | codice per sillaba | 2/18 | (legame 0,015) | 18 / 3,7 | 1,03 | 1,92 | 0,041 | **1,10** | 0,000 |
  | Naibbe | 5/18 | (legame ≈ 0) | 7 / 13 | 1,08 | 2,16 | 0,17 | 0,41 | 0,000 |
  | *Voynich* | | *0,006* | *23 / 55* | *0,52* | *2,24* | *0,21* | *1,01* | *0,038* |

  - **Nota sul verboso.** La ricerca preregistrata (`cerca_verboso`, 300 prove) ha scelto 20
    lettere con un segno solo, cioè una **sostituzione semplice**: h2 resta quella del latino. Le
    parole latine sono lunghe (5,9 lettere) e ogni lettera resa con due segni le allunga ancora,
    quindi la ricerca non allunga. È il compromesso già documentato nell'e07: non lo correggo,
    perché è l'esito della procedura dichiarata.
- **Previsioni:** confermate.
  - Nessuna cifratura supera 5/18.
  - Solo la sostituzione conserva la chiusura della riga; il codice per parola e il Naibbe
    distruggono il legame dentro la riga.
- **Due cose da notare.**
  1. **Il codice per sillaba dà ripetizione ×1,10**, cioè le ripetizioni immediate del Voynich.
     Con una parola per sillaba, sillabe uguali vicine diventano parole uguali vicine. Ha però
     troppi pochi tipi (0,04) e h2 troppo bassa (1,92).
  2. **L'omogeneità di pagina resta a zero in tutte le cifrature**, anche se ogni capitolo parla di
     una sola pianta.
- **Lettura.**
  - Un contenuto ordinato per argomento (una pianta per pagina) non produce, attraverso nessuna
    cifratura provata, la somiglianza fra parole vicine e di pagina del Voynich (+10,7 deviazioni
    standard nell'e13).
  - Questa resta l'anomalia che solo la copia locale (procedimento ad autocitazione, ipotesi 3)
    produce.
  - **La riga** si spiega con il verso; **la pagina** e **le parole** con la copia. Un'ipotesi che
    tenga tutto dovrebbe combinarli: per esempio un testo composto in versi, verso per verso,
    copiando e variando parole delle righe vicine. Sarebbe una composizione poetica "ad
    autocitazione": un'ipotesi nuova da precisare.

## 1/10/2026 — e101: sillabe con convenzioni di pagina, fallimento istruttivo

- **Metodo.** Preregistrato. *Macer* in versi, una parola per sillaba, 1 + ⌊f/c⌋ codici per
  sillaba (c = 40, 20, 10, 5), scelti a caso o fissati per pagina; tre semi.
- **Risultati: massimo 5/18.**
  - Ripetizione 0,88–1,24: sempre vicina al Voynich.
  - **Omogeneità ≈ 0 in tutti i casi**, anche con i codici fissati per pagina.
  - Parole uniche 0,09–0,22 (Voynich 0,68).
  - Tipi 0,06–0,23.
  - h2 2,30–2,76.
- **Previsioni smentite:** "per pagina" non dà omogeneità, e nessuna combinazione supera 10/18.
- **Lettura (importante per capire che cosa misura l'omogeneità).**
  - La "somiglianza nella riga" (+10,7 deviazioni standard, e13) misura quanto si **somigliano
    nella forma** parole **diverse** vicine, cioè quante poche modifiche le separano. Non misura il
    riuso delle stesse parole.
  - Fissare un codice per pagina aumenta il riuso, non la somiglianza fra parole diverse: per questo
    non serve.
  - Nel Voynich parole vicine e diverse sono **varianti** l'una dell'altra (*qokeedy*, *qokedy*,
    *okeedy*…). È la firma di una scrittura che produce le parole **modificando parole vicine**.
    Nessuna cifratura di un testo vero provata finora (e07, e43, e46, e52, e62, e100, e101) lo fa.
  - Lo fa il procedimento ad autocitazione, ipotesi 3, e potrebbe farlo un cifrario in cui i codici
    di una pagina nascono come varianti gli uni degli altri (D'Imperio ipotizzava riempitivi
    "costruiti ripetendo parti di stringhe vicine con piccole modifiche"). Quest'ultima variante
    però fallisce l'omogeneità nell'e43, se le copie sono solo locali.

## 1/10/2026 — Esplorativi: la grammatica delle varianti; inizi di paragrafo

**Esplorativo, non preregistrato.**

- **Varianti a una sola modifica fra parole vicine nella riga:**
  - Voynich: 4,3% delle coppie;
  - generatore di Timm e Schinner: 6,7%.
- **Voynich, per tipo di modifica:**
  - sostituzione del segno iniziale 28%, aggiunta in testa 25%, aggiunta interna 19%;
  - modifiche più frequenti: +e interna (107), +q in testa (92), l↔r in coda (86), k↔t interna
    (59), +d interna (52), +ch in testa (47), +o in testa (42), ch↔sh in testa (38), l↔o, ch↔cth,
    a↔o.
- **Generatore:** aggiunta in testa 54%, dominata da **+ch** (466), poi +d, +e, +i, +o, +sh.
- **Lettura.**
  - Le varianti del Voynich seguono le famiglie dell'e95 (ch/sh, k/t, l/r, a/o) e l'aggiunta di
    q-.
  - Il generatore invece aggiunge prefissi, soprattutto ch-. Questo spiega in parte perché la
    forma delle parole del generatore è sbagliata (e54: troppo poche q-, troppe a- e ch-).
  - I modelli Python (e56, e57, e70) usavano già modifiche stimate sul vocabolario del Voynich
    (`generatori.Modifiche`) e fallivano per altre ragioni (quota di copia).
- **Inizi di paragrafi consecutivi** sulla stessa pagina: S = 1,04 (z 1,0), nessun evitamento. Sono
  quasi tutti gallow (p 331, t 171, k 78, f 32). **L'evitamento riguarda solo le righe dentro il
  paragrafo.**

## 1/10/2026 — Esplorativo: il Voynich non rima

**Esplorativo, non preregistrato.** Coincidenza delle ultime due lettere o segni, rispetto al
rimescolamento delle righe:

| testo | fra fini di righe consecutive | metà riga – fine riga (rima interna) |
|---|---|---|
| Voynich | **1,00** (z 0,1) | 1,35 (z 6,4) |
| Ovidio | 1,04 | 2,15 |
| *Macer* | 1,27 | 3,72 |
| Marbodo (esametri leonini) | 3,28 | 6,59 |

- Il Voynich non ha rima fra righe.
- Il suo 1,35 interno può venire dalla semplice somiglianza fra parole della stessa riga: manca
  un confronto fra posizioni qualsiasi.
- Nei testi latini anche l'accordo grammaticale (aggettivo e nome lontani con la stessa
  desinenza) produce la "rima interna".
- **Lettura:** nessun indizio di rima. Non esclude il verso (la poesia classica e il *Macer* non
  rimano), ma toglie una prova possibile a favore.

## 1/10/2026 — e103: le etichette dello zodiaco non si corrispondono per posizione

- **Metodo.** Preregistrato. 10 segni con circa 30 etichette (Ariete e Toro ricomposti dalle
  due metà). Somiglianza delle etichette con lo stesso indice in segni diversi, contro indici
  distanti; anche con allineamento ciclico libero.
- **Validità:** controllo positivo (segno finale fisso per indice su metà delle etichette): p 0,002
  (✓).
- **Risultati:**

  | misura | p |
  |---|---|
  | somiglianza a indice fisso | 0,14 |
  | primo segno a indice fisso | 0,71 |
  | somiglianza con allineamento libero | 0,74 |
  | primo segno con allineamento libero | 0,27 |

- **Lettura.** Nessuna corrispondenza rilevabile fra le etichette nella stessa posizione di segni
  diversi. Se le etichette fossero i numeri dei giorni scritti con un sistema regolare, ci si
  aspetterebbe una corrispondenza. Non c'è, almeno con l'ordine della trascrizione e con
  spostamenti ciclici. Non esclude nomi propri diversi per ogni segno (stelle, per esempio).

## 1/10/2026 — e102: le scritture sillabiche non si avvicinano al Voynich

- **Metodo.** Preregistrato. 14 Bibbie in abugida e sillabari (escluse dall'e13), con
  l'impaginazione del Voynich, contro 17 alfabetiche di riferimento.
- **Risultati.**
  - **h2 più alta, non più bassa:** abugida e sillabari 3,06–4,02; mediana alfabetica 3,18;
    Voynich 2,24.
  - Somiglianza nella riga ≤ 0,009, salvo il thai non segmentato (0,028), dove una "parola" è una
    frase intera; Voynich 0,038.
  - Ripetizione: wolaytta 0,43, thai 0,53; Voynich 1,01.
  - **Anomalie condivise:** 0 su 4 per tutte, tranne l'ojibwa (1: spazio prevedibile 0,48) e il
    thai (1).
- **Previsione confermata.** Nessuna scrittura arriva a 3 anomalie su 4. L'ipotesi "lingua
  naturale in una scrittura sillabica" non spiega l'impronta: in queste scritture l'incertezza sul
  segno successivo è anzi più alta.

## 1/10/2026 — e105: l'inizio di riga dipende solo dall'inizio della riga sopra

- **Metodo.** Preregistrato (tentativo 4 concordato con Davide). Otto candidati per la classe
  d'inizio di riga (famiglie fuse), senza condizioni e condizionati all'inizio della riga sopra.
- **Risultati** (eccesso d'informazione mutua, z):

  | candidato | z | z condizionato all'inizio della riga sopra |
  |---|---|---|
  | inizio della riga sopra | **26,1** | |
  | posizione nel paragrafo | 9,0 | −0,4 |
  | classi presenti nella riga sopra | 5,4 | 0,6 |
  | inizio di due righe sopra | 5,1 | −2,1 |
  | numero di parole della riga sopra | 3,0 | 2,5 |
  | fine della riga sopra | −0,6 | −1,5 |
  | numero di parole della riga | | 1,2 |
  | seconda parola della riga | | 1,0 |

  - Per le ultime due il nullo non condizionato non è informativo (le caratteristiche si spostano
    con la riga ed eccesso e varianza nulli sono 0): vale solo la versione condizionata. È un
    difetto di disegno che riguarda solo quelle due.
- **Lettura** (nessun candidato rilevante oltre la riga sopra, come previsto; il candidato 3 è
  spiegato anch'esso).
  - La regola d'inizio riga è **del primo ordine**: la riga nuova "guarda" solo come comincia la
    riga immediatamente sopra, per evitarla e per preferire certi passaggi.
  - Non guarda come finisce la riga sopra, né quali parole contiene, né quanto è lunga.
  - La dipendenza dalla posizione nel paragrafo è un riflesso di questa catena, che parte dai
    gallow d'inizio paragrafo.
  - È il comportamento di chi, cominciando una riga, guarda l'inizio di quella sopra (la colonna
    sinistra) e sceglie diverso: un'abitudine di impaginazione o una regola di procedimento, non
    una dipendenza di contenuto.

## 1/10/2026 — e104: sillabe con grafia variabile, la prima cifratura vicina sul vocabolario

- **Metodo.** Preregistrato. *Macer* in versi; ogni sillaba ha una parola di base del Voynich e
  ogni occorrenza riceve k ~ Poisson(μ) varianti (`Modifiche` stimate sul Voynich).
- **Risultati** (medie su tre semi):

  | μ | pagella | h2 | tipi | uniche | ripetizione | omogeneità | legame |
  |---|---|---|---|---|---|---|---|
  | 0,3 | 5/18 | 2,13 | 0,111 | 0,56 | 1,02 | −0,001 | 0,008 |
  | **0,6** | **7/18** | **2,28** | 0,156 | **0,60** | **0,94** | −0,001 | 0,005 |
  | 1,0 | 5/18 | 2,44 | **0,209** | **0,64** | **0,99** | −0,000 | 0,004 |
  | 1,5 | 2/18 | 2,60 | 0,264 | 0,67 | 1,00 | −0,000 | 0,003 |
  | *Voynich* | | *2,24* | *0,210* | *0,68* | *1,01* | *0,038* | *0,19* |

  - Con μ = 0,6 riproduce in banda: h2, spazio, parole uniche, ripetizione, curva piatta, Zipf,
    forma delle parole.
- **Criterio preregistrato non raggiunto:** la somiglianza nella riga resta a 0 per ogni μ.
- **Lettura.**
  1. È la **prima cifratura di un testo vero** che riproduce insieme tre delle quattro anomalie
     forti dell'e13 (h2 bassa, spazio prevedibile, ripetizione ×1), più la quantità e la
     distribuzione delle parole. Un **sistema sillabico con grafia variabile** spiega molto del
     vocabolario del Voynich.
  2. **Mancano:**
     - la somiglianza fra parole vicine. Le sillabe si ripetono uniformemente nel testo, non per
       argomento, quindi le varianti della stessa sillaba non si addensano nella riga e nella
       pagina;
     - il legame fra parole e la chiusura della riga (legame quasi nullo).
  3. **Che cosa servirebbe per chiudere:**
     - una grafia che varia **localmente**: lo scriba riprende la grafia usata poco prima per la
       stessa sillaba, o per sillabe simili, cioè copia dalla memoria recente come nel procedimento
       ad autocitazione;
     - giunture fra sillabe consecutive (sandhi o fonotassi scritte).
  - È un'ipotesi ibrida concreta: testo vero in sillabe, scritto con varianti che lo scriba
    riprende da ciò che ha appena scritto. Da provare (e108).

## 1/10/2026 — Replica dell'e20 completata

- L'e20 (risolutore a nove gradi di fusione, latino e italiano) è stato rieseguito per intero, in
  sottofondo: 7.011 secondi con 3 processi.
- **Confronto con il tag `origine`:** 7.126 valori; i soli 63 diversi sono i tempi di esecuzione
  (campi "secondi"). **Replica identica.**
- **Stato della replica:** e01–e28 tutti replicati (e13 cambia per la ragione della D-008; e17 su un
  sottoinsieme, D-009), tranne e19, ancora da rieseguire, ed e16, superato già in origine.

## 1/10/2026 — e109: il primo segno di riga non è un indicatore di chiave

- **Metodo.** Preregistrato (proposta discussa con Davide). Il resto della riga (dalla seconda
  parola) dipende dalla classe d'inizio? Nullo: classi d'inizio rimescolate fra le righe della
  stessa pagina.
- **Validità:** controllo positivo debole (tavole che scambiano 2 coppie di segni) z 92,6; forte
  z 56,3 (✓).
  - Il controllo "debole" è risultato più marcato del "forte", perché scambia segni molto
    frequenti.
- **Risultati** (eccesso, z):

  | testo | fuori diagonale (indicatore) | diagonale (stessa classe) | seconda parola |
  |---|---|---|---|
  | **Voynich** | **+0,0002 (z 0,4)** | +0,0003 (z 0,4) | +0,020 (z 5,6) |
  | Timm e Schinner | 0,0005 (z 1,1) | | 0,019 (z 5,4) |
  | *Macer* | +0,0025 (z 6,6) | | 0,12 (z 13,6) |

- **Lettura preregistrata: indicatore escluso**, alla sensibilità del controllo.
  - La distribuzione dei segni nel resto della riga **non dipende** dal primo segno: eccesso
    +0,0002 contro 0,0425 del controllo, cioè meno dell'1%.
  - Con la variabilità del nullo (deviazione standard di circa 0,0005), un effetto di circa 0,002
    (z ≈ 4, il 5% del controllo) sarebbe stato visto.
  - Resta possibile solo una tavola che lasci invariate le frequenze dei segni (per esempio un
    cambio fra omofoni di pari frequenza), che questa misura non vede.
  - La dipendenza della seconda parola (z 5,6) c'è anche nel generatore (5,4): è la regola delle
    giunture fra prima e seconda parola, non un indicatore.
- **Conseguenza.** La riga "riparte" (giunture chiuse, inizio speciale), ma **il primo segno non
  governa il resto della riga**. L'idea "cifrario con indicatore di riga" cade, e con essa il
  tentativo di decifrazione per indicatore (e110) previsto in caso contrario.
- **Nota tecnica sull'e107.** È stato lanciato per errore con `LINGUE_SOLO=x` nell'ambiente. L'e107
  non usa quella variabile (le sue tre lingue sono fisse), ma il valore compare nella provenienza.

## 1/10/2026 — e108: la grafia che deriva non dà somiglianza; esplorativi sull'alternanza

**e108** (preregistrato): sillabe con grafia che riparte dall'ultima usata.

- **Esito: fallimento.** Massimo 4/18. La somiglianza nella riga resta ≤ 0,004 (Voynich 0,038).
- Peggiorano: h2 3,0–3,3, forma delle parole 1,1–10,4, deriva troppo forte (0,22–0,49).
- **Lettura.** La somiglianza del Voynich lega parole **diverse** vicine. In un codice vorrebbe dire
  che la grafia di una parola dipende dalle parole vicine e non solo dall'unità che codifica.

**Esplorativo, non preregistrato: un codice "differenziale a catena"?** Prima parola della riga
come seme, ogni parola successiva = la precedente modificata, con il messaggio nella modifica.

- Somiglianza fra parole della stessa riga per distanza (rapporto con coppie a caso):

  | testo | distanza 1 | distanza 2 | distanza 3 |
  |---|---|---|---|
  | Voynich | 1,18 | **1,22** | 1,18 |
  | Voynich, solo interne | 1,20 | **1,26** | 1,21 |
  | Timm e Schinner | 1,29 | 1,15 | 1,13 |
  | con giunture (e23) | 1,23 | 1,09 | 1,10 |
  | e51 | 1,27 | 1,14 | 1,14 |
  | Bibbia latina | 0,92 | 0,955 | 0,946 |
  | Ovidio | 0,946 | 0,959 | 0,959 |
  | *Macer* | 0,989 | 0,958 | 0,949 |

- **Nessuna catena:** nel Voynich le parole vicine non sono le più simili. L'ipotesi differenziale
  non è sostenuta.
- **Scoperta: alternanza.** Nel Voynich le parole a distanza 2 sono **più** simili di quelle
  vicine, come nella Bibbia latina e in Ovidio; nei generatori ad autocitazione è il contrario,
  perché copiano dalla parola appena scritta.
  - La parità della posizione nella riga ha un effetto minimo (0,001 bit sul primo segno): non
    sono due flussi in fase fissa.
  - Le giunture non spiegano l'alternanza: il generatore con le giunture ha 1,23 contro 1,09.
- Da confermare con una prova preregistrata (e110).

## 1/10/2026 — e106: il procedimento "a versi" non basta

- **Metodo.** Preregistrato (tentativo 3). Base e69 contro base con regole di riga stimate sul
  Voynich; medie su tre semi.

  | modello | pagella | R | S(1) | copia 1ª / 2ª colonna | e94 posizione 2 |
  |---|---|---|---|---|---|
  | base | 13/18 | 0,02 | 1,06 | 1,31 / 1,19 | 1,04 |
  | con regole di riga | 10/18 | 0,01 | 0,63 | 0,41 / 1,19 | 1,11 |

- **Sufficienza non raggiunta.** La pagella scende a 10/18 (perde unioni, lunghezze vicine,
  bordo) e la preferenza della seconda posizione resta sotto 1,2.
- Nota: la base rigenerata arriva a 13/18 con il bordo di riga, e la chiusura della riga ce l'ha
  già (R 0,02).
- **Lettura.** Aggiungere le regole di riga al generatore migliore costa altre proprietà. In più
  il generatore copia a catena, cosa che il Voynich non fa (alternanza, quaderno sopra).
  L'ipotesi senza messaggio, nella forma "autocitazione", non tiene tutto insieme.
- **Ancora da fare:** e110 (conferma preregistrata dell'alternanza); e107 (trascrizione ripulita
  nei risolutori), che stava girando in sottofondo e va registrato quando finisce.

## 1/10/2026 — e107: la trascrizione ripulita non si lascia leggere

- **Metodo.** Preregistrato (tentativo 2). Tolti 609 gallow d'inizio paragrafo e 1.671 segni aggiunti
  a inizio riga; fusione leggera (sh→ch, p→t, f→k) o forte. Risolutore dell'e17 con latino,
  italiano ed ebraico.
- **Risultati** (posizione del Voynich fra controllo negativo 0 e positivo 1):

  | lingua | ripulita, fusione leggera | ripulita, fusione forte | gruppi | e17 originale (EVA / gruppi) |
  |---|---|---|---|---|
  | latino | −0,06 | −0,04 | −0,22 | −0,03 / −0,19 |
  | italiano | 0,18 | 0,20 | −0,06 | 0,16 / −0,14 |
  | ebraico | 0,42 | 0,28 | 0,05 | 0,42 / 0,15 |

  - Copertura con parole di almeno 6 lettere ≤ 9,7%; nel controllo positivo è 17–57%.
- **Previsione confermata: nessun miglioramento rilevante.** Togliere le convenzioni grafiche non
  avvicina una sostituzione omofonica di latino, italiano o ebraico. L'ipotesi "ogni segno vale una
  lettera, più segni la stessa lettera" resta esclusa anche sul testo ripulito.
- **Nota.** L'esecuzione aveva per errore `LINGUE_SOLO=x` nell'ambiente; l'e107 non la usa.

## 1/10/2026 — e110: niente copia a catena nel Voynich, sempre nei generatori

- **Metodo.** Preregistrato. A = somiglianza fra parole interne a distanza 2 / a distanza 1;
  nullo: parole rimescolate dentro la riga.
- **Risultati:**

  | testo | A | z |
  |---|---|---|
  | Voynich ZL | 1,044 | 5,3 |
  | Voynich IT | 1,052 | 5,5 |
  | lingua B | 1,052 | 5,0 |
  | **lingua A** | **1,020** | **0,9** |
  | mano 1 | 1,025 | 1,2 |
  | mano 2 | 1,093 | 5,8 |
  | mano 3 | 1,023 | 1,7 |
  | Timm e Schinner (3 semi) | 0,87–0,89 | da −11 a −13 |
  | con giunture | 0,889 | −11 |
  | e51 | 0,900 | −10 |
  | base dell'e106 (3 semi) | 0,81–0,86 | da −14 a −20 |
  | Bibbie (latina, italiana, inglese, tedesca) | 1,035 / 0,986 / 1,046 / 1,017 | |
  | Ovidio | 1,014 | |
  | *Macer* | 0,969 | |
  | Plinio | 1,002 | |

- **Criteri preregistrati:**
  - "alternanza confermata": **no**, perché nella lingua A non è significativa;
  - "tutti i generatori sotto 1": **sì**, nettamente.
- **Lettura.**
  - Il Voynich, in ogni sottoinsieme (trascrizioni, lingue, mani), sta fra 1,02 e 1,09, cioè
    **nella gamma delle lingue vere** (0,97–1,05).
  - Tutti i generatori ad autocitazione, incluso il migliore (13/18), stanno fra 0,80 e 0,90: la
    loro parola più simile è quella appena scritta, perché copiano a catena.
  - L'alternanza vera e propria (sopra 1) è solida solo nella lingua B. Il fatto più importante è
    però un altro: **il Voynich non ha la firma della copia a catena**, che tutti i procedimenti ad
    autocitazione provati hanno.
  - È la seconda proprietà, dopo l'evitamento fra inizi di riga, che va **contro** l'ipotesi senza
    messaggio nella forma "autocitazione", e verso una sequenza di parole organizzata come in una
    lingua.

## 1/10/2026 — e111: parole come sillabe? Il modello alla lettera non regge (passi 1–2)

- **Metodo.** Preregistrato. Normalizzazioni N0–N4 (famiglie, serie di e/i, q iniziale, famiglie
  forti). Confronto del flusso di classi con flussi di sillabe veri (prime 30.000 unità).
- **Risultati:**

  | flusso | classi | classi uniche | h1 | h2 | Zipf | ripetizioni |
  |---|---|---|---|---|---|---|
  | sillabe vere (*Macer*, Ovidio, Bibbia latina e italiana) | 953–1.446 | 22–27% | 7,7–8,5 | 4,1–4,7 | da −1,28 a −1,61 | 0,1–0,5% |
  | Voynich N0 | 6.293 | 68% | 10,1 | 4,28 | −1,04 | 1,0% |
  | Voynich N4 | 3.430 | 62% | 8,5 | 5,05 | −1,27 | 2,6% |
  | controllo (*Macer* cifrato come nell'e104) N0 | 4.696 | 59% | 9,85 | 4,25 | −1,08 | 0,3% |
  | controllo N4 | 2.354 (sillabe vere 1.238) | | | | | |

  - Purezza del controllo: H(sillaba | classe) da 0,97 a 2,32 bit; H(classe | sillaba) da 2,45 a
    2,15 bit.
- **Criterio preregistrato non soddisfatto a nessun livello.** Al livello più vicino (N4) restano
  fuori classi, classi uniche, h2 e ripetizioni.
- **Ma il criterio non distingue.**
  - Fallisce anche per il controllo, che è un vero cifrario a sillabe con varianti: le
    normalizzazioni semplici non annullano le varianti generali.
  - Senza normalizzazione il controllo assomiglia molto al Voynich: classi, classi uniche, h1, h2,
    Zipf.
  - Il Voynich ha però più ripetizioni immediate di qualunque flusso di sillabe (1,0–2,6% contro
    0,1–0,5%).
- **Metro** (sezione S, righe non finali):

  | testo | CV unità per riga | CV larghezza | rapporto |
  |---|---|---|---|
  | Voynich S (parole) | 0,141 | 0,105 | 1,34 |
  | Ovidio (sillabe) | 0,082 | 0,078 | 1,05 |
  | *Macer* (sillabe) | 0,092 | 0,088 | 1,05 |
  | Plinio a capo (parole) | 0,43 | 0,42 | 1,03 |

  - La lettura preregistrata ("CV unità < CV segni") era mal posta: neppure i versi veri la
    soddisfano.
  - Il confronto dei rapporti dice che nel Voynich il numero di parole varia **più** della
    larghezza: le righe sembrano riempite fino al margine, non contate in sillabe.
- **Decisione** (come da preregistrazione, discussa con Davide prima del passo 3). Il passo 3 si
  imposta come **prova di fattibilità**: il risolutore a sillabe si prova prima sul controllo
  cifrato. Se non lo legge, nemmeno un Voynich di quel tipo sarebbe decifrabile per via statistica
  con questa quantità di testo.

## 1/10/2026 — e113: non è una lingua monosillabica (vietnamita, cinese)

- **Metodo.** Preregistrato (strada 1). Misure "a sillabe" dell'e111 su vietnamita, cinese (pinyin
  con e senza toni, caratteri), sillabe latine e italiane, contro il Voynich a N0, N1, N2.
- **Risultati:**

  | flusso | classi | classi uniche | ripetizione rispetto alla riga | compatibilità |
  |---|---|---|---|---|
  | vietnamita | 1.555 | 0,24 | 0,23 | 3/6 (h1, h2, Zipf) |
  | pinyin con toni | 783 | | 0,32 | 2/6 |
  | pinyin senza toni | 357 | | 0,42 | 2/6 |
  | cinese in caratteri | 1.443 | | 0,29 | 3/6 |
  | sillabe latine | 1.157 | | 0,16 | 2/6 |
  | sillabe italiane | 953 | | 0,28 | 2/6 |
  | **Voynich** | **4.782–6.293** | **0,65–0,68** | **≈ 1,00** | |

- **Previsione in parte smentita:** le monosillabiche non sono più vicine delle sillabe latine.
  Nessun flusso è "vicino" (≥ 5/6).
- **Lettura.**
  - Il Voynich ha **3–4 volte più forme distinte** di qualunque inventario di sillabe, anche con i
    toni.
  - Ha **ripetizioni immediate da 2,5 a 6 volte** più frequenti, anche rispetto a lingue con
    reduplicazione.
  - L'ipotesi "lingua monosillabica" (Stolfi), nella forma "una parola = una sillaba di una lingua
    nota", non regge.
  - Resta solo la variante con grafia variabile (e104), che però ha i limiti dell'e111.

## 1/10/2026 — e114: nessun accordo delle terminazioni a distanza (contro la grammatica)

- **Metodo.** Preregistrato (strada 2). IM fra gli ultimi 2 segni (o lettere) di parole a distanza k
  nella riga, contro il rimescolamento dentro la riga (che conserva l'omogeneità di riga).
- **Risultati** (eccesso in bit, z):

  | testo | k = 1 | k = 2 | k = 3 |
  |---|---|---|---|
  | Voynich ZL | 0,048 (16) | **0,000 (0,1)** | −0,002 |
  | Voynich IT | 0,029 (10) | 0,005 (1,5) | −0,001 |
  | lingue A e B | 0,03 / 0,05 | ≤ 0 | ≤ 0 |
  | generatori (5) | 0,039–0,042 | da −0,015 a −0,005 | negativi |
  | Bibbia latina | 0,34 | **0,065 (19)** | 0,017 (4,4) |
  | Bibbia italiana | 0,60 | 0,13 (35) | |
  | Bibbia tedesca | 0,36 | 0,10 (30) | |
  | Bibbia ungherese | 0,52 | 0,14 (29) | |
  | Bibbia turca | 0,40 | 0,13 (33) | |
  | Ovidio | 0,16 | 0,03 (7) | |

- **Criteri preregistrati:** accordo nel Voynich **no**; generatori senza accordo **sì**.
- **Lettura. Risultato forte.**
  - In tutte le lingue provate, flessive e agglutinanti, in prosa e in versi, la terminazione di una
    parola predice quella delle parole successive, a distanza 1 con 0,16–0,60 bit e ancora a
    distanza 2. È la sintassi: accordi e parole grammaticali.
  - **Nel Voynich questa struttura manca.** Il poco che c'è a distanza 1 (0,03–0,05) è della stessa
    misura dei generatori e si spiega con la regola delle giunture. A distanza 2 è zero.
  - Le terminazioni delle parole del Voynich (-dy, -y, -in, -ol…) non portano informazione
    sintattica sequenziale come le desinenze o le parole grammaticali di una lingua.
- **Riserve.**
  - Se le parole fossero sillabe, la sintassi starebbe su più parole e la misura andrebbe fatta su
    un flusso di sillabe vere. Non l'ho fatto: è un controllo da aggiungere.
  - Combinato con l'e110 (nessuna copia a catena), il Voynich non è né una lingua scritta parola
    per parola, né la copia a catena dei generatori noti.
- **Controllo esplorativo, dopo l'esecuzione, che cambia la lettura dell'e114:**

  | flusso | k = 1 | k = 2 | k = 3 |
  |---|---|---|---|
  | sillabe latine in chiaro (Bibbia) | 1,00 bit | 0,29 | 0,11 |
  | sillabe del *Macer* in chiaro | 1,11 | 0,38 | |
  | **le stesse sillabe cifrate come nell'e104** | **0,035** | **0,013 (z 4,1)** | 0,003 |
  | Voynich | 0,048 | 0,000 | |

  - In un **codice** le terminazioni delle parole sono etichette arbitrarie rispetto a ciò che
    codificano, quindi la misura sulle terminazioni non vede più la sintassi.
  - **Lettura corretta:** l'e114 esclude una lingua **scritta in alfabeto** (dove le terminazioni
    sono desinenze o parole grammaticali). Non esclude un **codice** che renda unità linguistiche con
    parole del Voynich: un codice di questo tipo dà valori dello stesso ordine del Voynich.

## 1/10/2026 — e115: le parole frequenti del Voynich non hanno un ordine preferito

- **Metodo.** Preregistrato (strada 3). Asimmetria di Bowker sulle coppie ordinate dei 40 tipi più
  frequenti (parole dalla terza alla terzultima, distanza ≥ 2), contro due nulli.
- **Risultati** (z contro il rimescolamento nella riga; z contro i terzili):

  | testo | z (riga) | z (terzili) |
  |---|---|---|
  | Voynich ZL | **0,6** | 0,7 |
  | Voynich IT | 0,4 | 0,0 |
  | lingue A e B | ≈ 0 | |
  | generatori | da −1,7 a 0,3 (un seme 4,1) | |
  | Bibbie (latina, italiana, tedesca, ungherese, turca) | **6,1–18,4** | da −5,4 a 2,1 |
  | Ovidio (solo 1 coppia, non informativo) | | |

- **Validità del secondo nullo.** Quello per terzili fa sparire l'ordine anche nelle lingue: per la
  regola preregistrata **quella parte della misura non vale**. Conta il confronto con il primo
  nullo, dove le lingue sono chiaramente positive.
- **Controllo esplorativo, dopo l'esecuzione:**

  | testo | z (riga) | z (terzili) |
  |---|---|---|
  | *Macer* sillabe in chiaro | 44,7 | 11,1 |
  | *Macer* cifrato e104, μ 0 | 44,7 | 11,1 |
  | *Macer* cifrato e104, **μ 0,6** | **21,7** | 4,9 |

  - A differenza delle terminazioni (e114), l'ordine delle parole frequenti **si conserva in un
    codice**, anche con varianti di grafia.
- **Lettura. Risultato forte.**
  - Nel Voynich le parole frequenti (*daiin*, *chedy*, *ol*, *qokeedy*…) non hanno alcun ordine
    relativo preferito. Nelle lingue sì (z 6–18) e nei codici di una lingua pure (z 22–45).
  - Questo va contro un testo linguistico **cifrato parola per parola o sillaba per sillaba**,
    anche con grafia variabile: la sintassi lascerebbe un ordine fra le unità frequenti.
  - Il Voynich si comporta come i generatori senza messaggio.
  - **Resta aperto:**
    - un sistema in cui le parole frequenti sono nulle o riempitivi mescolati al testo vero;
    - un sistema in cui il messaggio non sta nell'ordine delle parole (per esempio nelle iniziali
      di riga, idea dell'acrostico).

## 1/10/2026 — e116: le ripetizioni non sono numeri; e117: misura satura

**e116** (preregistrato, strada B: ripetizioni come quantità).

- **Concentrazione:** 3,74 (≥ 3, come previsto). Il generatore però ha 3,27, quasi lo stesso.
- **Tipi più ripetuti:** chol (24), qokeedy (18), qokedy (16), qokeey (12), daiin (11), ol, shedy,
  chedy, dy, chor. Sono parole comuni, non un piccolo gruppo di "numerali".
- **Sezioni:**

  | sezione | ripetizione rispetto all'attesa | IC 95% |
  |---|---|---|
  | erbario | 1,02 | 0,84–1,20 |
  | ricette | 1,13 | 0,87–1,34 |
  | biologia | 0,85 | |
  | farmacia | 0,77 | |
  | altre | 1,00 | |

  - Nessuna differenza: ricette e farmacia **non** sono sopra le altre.
- **Serie:**

  | lunghezza | osservate | attese |
  |---|---|---|
  | 2 | 267 | 321 |
  | 3 | 9 | 3,0 |
  | 4 | 1 | 0,03 |

  - Il generatore ha lo stesso schema: 11 serie di 3 contro 3,1 attese.
- **Posizione:** le ripetizioni stanno al centro della riga (z 11,3), raramente all'inizio.
- **Lettura preregistrata: misto.**
  - L'ipotesi "numeri e quantità" **non è sostenuta**: manca la differenza fra sezioni, che era la
    previsione chiave.
  - Il quadro delle ripetizioni (concentrazione, serie di 3 in eccesso, posizione centrale)
    coincide con quello del generatore ad autocitazione.

**e117** (preregistrato, strada C: combinatoria inizio × fine).

- Il **riempimento** delle 12 × 20 combinazioni è saturo (0,92–1,00) in tutti i testi, lingue
  comprese: con migliaia di tipi tutte le combinazioni compaiono. **La misura non è informativa**
  (difetto di disegno); "più combinatorio di ogni lingua": no.
- **Dipendenza** (descrittivo, osservata contro attesa):

  | testo | osservata | attesa |
  |---|---|---|
  | Voynich | 0,011 | 0,009 |
  | latino | 0,016 | 0,011 |
  | italiano | 0,019 | 0,017 |
  | inglese | 0,053 | 0,046 |
  | turco | 0,077 | 0,013 |
  | ungherese | 0,051 | 0,016 |
  | Naibbe | 0,006 | 0,011 |
  | generatore | 0,016 | 0,012 |

  - Nel Voynich inizio e fine della parola sono quasi indipendenti, come in latino e italiano su
    queste parti. Non distingue.

## 1/10/2026 — e118: nessuna sezione fa eccezione

- **Metodo.** Preregistrato (strada D). Proprietà di riga per sezione; testi del genere.
- **Risultati:**

  | testo | righe | R | S(1) (z) | A (z) | bordo ini/fin | ripetizione |
  |---|---|---|---|---|---|---|
  | Voynich, tutto | 4.130 | 0,01 | 0,52 (−12) | 1,044 (5,1) | 23 / 55 | 0,99 |
  | erbario | 1.608 | 0,08 | **0,38** (−9,7) | 1,008 (0,6) | 15 / 23 | 1,02 |
  | biologia | 745 | 0,05 | 0,51 (−6,2) | **1,157 (7,2)** | 27 / 10 | 0,85 |
  | farmacia | 224 | −0,13 | **0,33** (−3,6) | 1,047 (1,5) | 9 / 7 | 0,77 |
  | ricette | 1.164 | 0,00 | 0,72 (−3,6) | 1,022 (1,6) | 21 / 33 | 1,13 |
  | altre | 389 | 0,18 | 0,70 (−2,2) | 1,012 (0,4) | 11 / 11 | 1,00 |
  | *Macer* (erbario in versi) | | 0,00 | 0,95 | 0,969 | 23 / 17 | 0,07 |
  | Plinio (erbario in prosa) | | 0,66 | 1,04 | 1,002 | 4 / 1 | 0,11 |
  | Apicio (ricette) | | 0,46 | 1,08 | 1,011 | 3 / 3 | 0,03 |

- **Sezioni che "si discostano"** (criterio preregistrato): erbario e altre, solo per A (z < 1).
  - È l'alternanza, già nota come non significativa nella lingua A (e110). In nessuna sezione A
    scende sotto 1, cioè in nessuna c'è copia a catena.
- **Lettura.**
  - La riga chiusa, l'evitamento fra inizi e l'assenza di copia a catena valgono **in tutte le
    sezioni**. Non c'è una sezione "diversa" da attaccare per prima.
  - L'evitamento è più forte in erbario e farmacia (S 0,33–0,38), più debole in ricette (0,72).
  - L'alternanza (A > 1) è netta solo in biologia.
  - Rispetto ai testi del genere, il Voynich ha la riga chiusa come il *Macer* (in versi), non come
    Plinio e Apicio (in prosa), ma ha anche evitamento e ripetizioni che nessun testo del genere ha.

## 1/10/2026 — e119: niente acrostico nelle iniziali di riga

- **Metodo.** Preregistrato (idea discussa con Davide). Sequenza dei primi segni delle righe non
  d'inizio paragrafo, pagina per pagina: 3.210 simboli, 11 tipi.
- **Parte 1, statistica:**

  | sequenza | h2/h1 | IM a distanza 1 (z) | IM a distanza 2 | S(1) | S(2) |
  |---|---|---|---|---|---|
  | iniziali del Voynich | **0,96** | **0,077** (14,6) | 0,021 | 0,62 | 1,14 |
  | lettere latine | 0,84 | 0,53 (79) | 0,30 | 0,40 | 0,88 |
  | lettere italiane | 0,83 | 0,58 (83) | 0,20 | 0,59 | 1,17 |
  | acrostico latino cifrato con 11 simboli (controllo) | 0,88 | 0,37 (105) | 0,17 | 0,46 | 0,96 |
  | iniziali del generatore | 0,97 | 0,021 | 0,013 | 1,05 | 1,02 |

- **Parte 2, decifrazione** con il risolutore dell'e17:

  | lingua | controllo positivo | posizione del Voynich | copertura 6+ del Voynich |
  |---|---|---|---|
  | latino | chiave giusta 79% | **−0,28** | 1,4% |
  | italiano | chiave giusta 80% | **−3,23** | 1,4% |

  - Il Voynich decifrato è peggiore del controllo negativo ("iiiissiieuiiu…").
- **Criteri:** controllo valido **sì**; acrostico non escluso **no**.
- **Lettura.**
  - Le iniziali di riga hanno la forma qualitativa delle lettere: doppie evitate, ritorno a
    distanza 2.
  - Ma la loro dipendenza è **sette volte più debole** di quella delle lettere di una lingua
    (0,077 contro 0,53–0,58 bit), e cinque volte più debole di un acrostico cifrato con lo stesso
    numero di simboli (0,37).
  - Il risolutore, che legge l'acrostico di prova all'80%, non ricava nulla dalle iniziali.
  - **Un acrostico in latino o in italiano è escluso.** L'evitamento fra inizi di riga è una regola
    debole e locale, non la traccia di un messaggio scritto lettera per lettera.

## 1/10/2026 — e120: riga per riga, le righe del Voynich non hanno formule ricorrenti

- **Metodo.** Preregistrato (proposta di Davide). Coppie di righe simili (Needleman–Wunsch sulle
  parole), parti fisse e caselle, legame delle caselle con la pagina.
  - Prima del commit: bootstrap ridotto a 50 ricampionamenti, per il tempo; Apicio a capo a 40
    lettere.
- **Risultati:**

  | testo | righe | con una riga simile | caselle / fisse | indice (IC) |
  |---|---|---|---|---|
  | **Voynich** | 3.481 | **0,6%** | 57 / 76 | 0,89 (0,70–1,11) |
  | Apicio (ricette) | 992 | **18,4%** | 262 / 752 | 1,15 (0,92–1,44) |
  | *Macer* (erbario in versi) | 2.154 | **18,3%** | 815 / 1.551 | 1,18 (1,05–1,25) |
  | Timm e Schinner | 3.643 | 0,8% | 83 / 119 | 0,72 (0,46–0,87) |

- **Validità fallita:** l'indice dei testi veri resta sotto 1,2. Le caselle sono più legate alla
  pagina, ma di poco. La lettura delle caselle del Voynich **non si fa** (e comunque sono pochissime:
  57 parole).
- **Il dato descrittivo è però netto.**
  - Nei testi veri del genere (ricette, erbario in versi) quasi **una riga su cinque riprende lo
    scheletro di un'altra** (formule: "piper, ligusticum…"; "si…, cum vino…").
  - Nel Voynich, con lo stesso criterio (almeno 3 posizioni fisse, varianti comprese), succede a
    **6 righe su mille**, come nel generatore.
  - Esempi trovati: righe vicine come "sar shedy qol … okal …" (f81r).
- **Lettura.** "Estrapolare riga per riga" cercando formule con caselle non è possibile.
  - Le righe del Voynich non sono costruite su scheletri ricorrenti come le voci di un ricettario o
    i versi di un erbario.
  - La somiglianza fra righe è diffusa (parole varianti sparse), non a formula.
  - È un altro punto in cui il Voynich si comporta come un procedimento di copia locale e non come
    un testo di genere.

## 1/10/2026 — e112: il primo risolutore a sillabe degenera (non valido)

- **Metodo.** Preregistrato (passo 3, prova di fattibilità sul controllo).
- **Risultati:**

  | prova | accuratezza | copertura 6+ |
  |---|---|---|
  | μ 0 | 0,033 | 0,38 |
  | μ 0,3 | 0,022 | 0,39 |
  | μ 0,6 | 0,022 | 0,45 |
  | negativo: rimescolato | | 0,44 |
  | negativo: generatore | | 0,41 |
  | tetto (*Macer* in chiaro) | | 0,535 |

- **Risolutore valido: no.** La chiave degenera: quasi tutti i simboli finiscono su "re" e "de"
  ("re de re re de…"). Ripetere sillabe frequenti alza la probabilità del modello, e la copertura
  sale per artefatto ("rede", "dere" sembrano pezzi di parole latine): i controlli negativi arrivano
  al 41–44%.
- **Lettura** (come da regola): nessuna conclusione sulla fattibilità. Corretto nell'e112b con il
  termine di entropia dell'e17, più una diagnosi a modello barato. È in corso.

## 2/10/2026 — e123: un messaggio nelle scelte ch/sh? Criteri passati, ma con la forma sbagliata

- **Metodo.** Preregistrato (strada A).
  - Dati: le 14.391 scelte ch/sh in ordine di lettura.
  - Nullo: rimescolamento dentro gli strati (pagina, prima riga, posizione nella riga e nella parola,
    segno seguente).
  - Controllo positivo: latino in codice di Bacone a 5 bit, scritto nelle scelte.
- **Risultati** (z):

  | testo | dist. 1 | 2 | 3 | 4 | 5 | deficit blocchi di 5 |
  |---|---|---|---|---|---|---|
  | Voynich | 11,4 | 6,0 | 2,8 | 1,8 | 2,2 | 9,6 |
  | controllo | 19,2 | 48,8 | 36,2 | 29,2 | 9,1 | 156 |
  | Timm e Schinner | 1,8 | 2,8 | 1,3 | 1,1 | 3,1 | 1,7 |

- **Esito per regola: "canale non escluso".** Il deficit del Voynich vale però il 6% di quello del
  controllo, e la dipendenza cala con la distanza senza l'impronta di blocco. Prima di trarne
  conclusioni ho preregistrato l'e123b.

## 2/10/2026 — e123b: la dipendenza ch/sh è una preferenza per riga, non un canale

- **Metodo.** Preregistrato.
  - Prima di scrivere il codice ho corretto lo strato riga, guardando solo i conteggi (3,6 scelte per
    riga): con tutto il contesto solo 3.789 occorrenze erano permutabili, quindi lo strato riga tiene
    del contesto solo "iniziale di parola o no".
  - Controllo di (P): le scelte vere rimescolate una volta dentro (riga + contesto).
- **Risultati:**
  - **con il nullo per riga** la dipendenza del Voynich sparisce: z dei blocchi di 5 da 10,0 a 1,0.
    Il controllo positivo resta a 121,6.
  - **il controllo di (P) si comporta esattamente come il Voynich**: z 9,1 col nullo dell'e123, 0,9
    con quello per riga.
  - **scomposizione:** l'eccesso di scelte uguali c'è in parole adiacenti (z 5,6), più lontane nella
    riga (3,7) e fra righe (3,2). Col nullo per riga resta solo un piccolo eccesso fra parole adiacenti
    (z 3,0).
- **Esito: (M) non in piedi.** La dipendenza dell'e123 nasce perché la quota di sh cambia da riga a
  riga, più un lieve effetto di innesco fra parole adiacenti. Il canale alla Bacone nelle scelte ch/sh
  è escluso, alla sensibilità del controllo.
- **Nota di metodo.** L'indice di fase è instabile quando il deficit medio è vicino a zero: dà 1,26
  sia al Voynich sia al controllo di (P), col nullo per riga. Il criterio richiedeva entrambe le
  condizioni, quindi l'esito non cambia, ma l'indice va normalizzato in modo diverso se riusato.
- **Nuova proprietà del Voynich:** la preferenza ch/sh è propria di ogni riga. Va con la riga come
  unità chiusa: chi scriveva sceglieva la grafia riga per riga.

## 2/10/2026 — e121: togliere la copia a catena non basta (nessun procedimento completo)

- **Metodo.** Preregistrato. Generatore di Timm e Schinner (e69):
  - con riuso della parola appena scritta al 10% (base) o allo 0% (senza catena);
  - con e senza le regole di riga dell'e106.
  - Medie su tre semi.
- **Risultati** (Voynich: R 0,006, S(1) 0,52, copia 1,03/1,47, e94 1,43, A 1,044):

  | modello | pagella | S(1) | copia 1ª / 2ª | e94 | A |
  |---|---|---|---|---|---|
  | base | 13/18 | 1,06 | 1,31 / 1,19 | 1,04 | 0,837 |
  | senza catena | 13/18 | 1,02 | 1,27 / 1,08 | 1,01 | 0,893 |
  | base + regole | 10/18 | 0,66 | 0,39 / 1,19 | 1,10 | 0,837 |
  | senza catena + regole | 12/18 | 0,66 | 0,39 / 1,08 | 1,11 | 0,892 |

- **Esito: nessun modello completo.**
  - Senza catena A sale solo a 0,89, ancora lontano da 1,04: la somiglianza a distanza 1 non viene
    solo dalla copia della parola precedente, ma dalla copia locale in generale.
  - Le regole di riga correggono S(1), ma fanno crollare la copia della prima colonna (0,39 contro
    1,03).
  - La copia della seconda colonna (1,47 nel Voynich) non viene mai riprodotta.
  - Mancano sempre ripetizione, profilo di pagina, forma delle parole e formule.
- **Lettura.** La famiglia "copia locale + regole" non arriva al Voynich con modifiche piccole. Le
  proprietà di riga del Voynich non sono un ritocco di un generatore a copia: vanno cercate in un
  procedimento diverso (e124, Rugg) o in un'origine diversa (e126–e128).

## 2/10/2026 — e112b: il risolutore a sillabe funziona solo col modello "barato"; il passo 3 si chiude

- **Metodo.** Preregistrato.
  - È l'e112 con il termine di entropia dell'e17.
  - In più, una diagnosi "a modello barato": il modello delle sillabe addestrato sul *Macer* stesso,
    cioè sul testo cifrato.
- **Risultati** (accuratezza della chiave; copertura 6+):

  | prova | modello onesto | modello barato |
  |---|---|---|
  | μ 0 (1.245 simboli) | 0,017 (0,23) | **0,956** (0,51) |
  | μ 0,3 | 0,019 (0,21) | – |
  | μ 0,6 (4.732 simboli) | 0,024 (0,24) | 0,082 (0,16) |
  | negativi | – (0,21) | – |
  | tetto (chiaro) | (0,535) | |

- **Esito per regola: risolutore non valido.** Il passo 3 si chiude con "risolutore a sillabe non
  realizzato".
- **Diagnosi.**
  - La ricerca funziona: col modello barato ritrova il 96% della chiave a μ = 0.
  - Il limite è il modello della lingua: addestrato su altri testi latini, non basta a fissare 1.245
    simboli.
  - Con le varianti di grafia (μ = 0,6, 4.732 simboli, ognuno raro) la chiave non si ritrova nemmeno
    col modello barato (8%).
- **Lettura.** Un codice per sillabe con grafia variabile, cioè il modello di contenuto migliore
  finora (e104), non sarebbe decifrabile per sola statistica, neanche conoscendo il testo esatto della
  lingua. Non dice nulla sul fatto che il Voynich lo sia. Dice che questa strada di decifrazione,
  anche se l'ipotesi fosse vera, richiederebbe un appiglio esterno: etichette con referente noto
  (e122), nomi propri, una parola certa.

## 2/10/2026 — e124: tavola e griglia (Rugg, ricostruzione semplificata). Lontana nel complesso, utile in due punti

- **Metodo.** Preregistrato (strada B).
  - Tavola di 40 righe con prefisso, nucleo e suffisso estratti dalle parti delle parole del Voynich.
  - Griglia a tre fori, cella vuota con probabilità b, ripartenza o continuazione a ogni riga, tavola
    nuova ogni T pagine.
  - Medie su tre semi.
- **Risultati:**
  - pagella **da 1 a 5 su 18** in tutte le combinazioni;
  - **difetti:** h2 2,84–2,88 (troppo alta), parole uniche 0–0,14 (Voynich 0,66), tipi/parole
    0,03–0,12 (troppo pochi);
  - **due cose che il generatore di Timm e Schinner non ottiene:**
    - **A ≈ 1,0** (0,985–1,025; Voynich 1,044): senza copia a catena l'alternanza viene da sé;
    - **con la griglia che riparte a ogni riga, la riga si chiude:** R 0,01–0,14 contro 0,56–0,72
      quando continua.
  - S(1) però resta a 0,97–1,11 (Voynich 0,52).
  - La copia della prima e della seconda colonna è simile (Voynich: 1,03 / 1,47).
- **Esito: nessuna combinazione completa.**
- **Lettura.**
  - La mia ricostruzione è troppo povera: 40 righe di parti indipendenti danno poche parole, tutte
    ricorrenti, e niente struttura interna.
  - L'idea di fondo, cioè un procedimento posizionale che riparte a ogni riga, dà gratis due proprietà
    che la copia non dà (chiusura e A ≈ 1).
  - Una griglia più ricca, con parti dipendenti come le colonne di Rugg e tavole più grandi, potrebbe
    avvicinarsi. Il metodo esatto di Rugg non è stato verificato alla fonte.

## 2/10/2026 — e125: un messaggio nelle lunghezze delle parole? Decifrazione non valida, statistica contraria

- **Metodo.** Preregistrato (strada C).
  - Dati: la sequenza delle lunghezze delle parole (1–8+) come testo di 8 simboli.
  - Statistica come l'e119; poi il risolutore dell'e17 in latino e italiano.
- **Risultati della statistica** (eccesso d'IM a distanza 1, contro il rimescolamento nella riga):

  | sequenza | IM1 | S(1) |
  |---|---|---|
  | Voynich | 0,014 | 1,04 |
  | lunghezze delle parole latine | 0,032 | 0,80 |
  | latino cifrato con 8 simboli (testo vero nelle lunghezze) | **0,180** | 0,70 |
  | Timm e Schinner | 0,003 | 0,96 |

- **Decifrazione: controllo non valido.** Con soli 8 simboli il risolutore non ritrova la chiave
  (0%) nemmeno sul controllo. Per regola, nessuna conclusione dalla parte 2.
- **Lettura** (descrittiva, fuori dai criteri):
  - Un testo nascosto nelle lunghezze lascerebbe una dipendenza fra simboli vicini 13 volte più forte
    di quella del Voynich.
  - La sequenza delle lunghezze del Voynich è anzi *meno* strutturata di quella di un normale testo
    latino, e non evita la ripetizione della stessa lunghezza.
  - La correlazione fra lunghezze vicine (V6) è reale ma debole, più del generatore e meno di una
    lingua.
  - Non c'è segno di un canale nelle lunghezze.

## 2/10/2026 — e126: nessuna grammatica nemmeno nella composizione della riga; trasposizione esclusa

- **Metodo.** Preregistrato (ipotesi 1).
  - Misura: accordo fra terminazioni *diverse* (ultimi 2 segni) in coppie a distanza ≥ 2 nella stessa
    riga. Non dipende dall'ordine dentro la riga.
  - Nullo: scambio di parole fra righe della stessa pagina, per classe di posizione.
- **Risultati** (eccesso d'IM, z):
  - Voynich: ZL −0,0008 (−0,5), IT +0,0004 (0,3);
  - Timm e Schinner: z 3,2, 7,3, 5,7;
  - lingue: latino 22,5, italiano 29,4, ungherese 32,5, turco 25,7, Ovidio 8,5.
  - Terminazioni identiche: Voynich ×1,07, lingue ×1,15–1,36, Timm e Schinner ×1,0.
- **Esito: trasposizione esclusa**, alla sensibilità del controllo (controllo valido, cinque lingue su
  cinque). L'eccesso del Voynich vale −3% di quello latino.
- **Lettura.**
  - Le parole di una riga del Voynich non portano coppie grammaticali di terminazioni, nemmeno
    ignorando l'ordine. Persino Timm e Schinner ne ha un po' di più, per la copia da parole vicine.
  - Insieme a e114 ed e115: nessuna traccia di sintassi né nell'ordine né nella composizione della
    riga, per qualunque cifratura che conservi le terminazioni.
  - Resta coperta solo da codici che sostituiscono parole intere, o da un contenuto che non ha
    grammatica (elenchi, nomi).

## 2/10/2026 — e128: la scrittura inventata da persone non ha l'inizio di riga del Voynich

- **Metodo.** Preregistrato (ipotesi 3).
  - 38 testi senza senso scritti a mano da volontari (Gaskell e Bowern 2022; 1.617 righe, 10.032
    parole).
  - Confrontati con 10 sottoinsiemi della stessa dimensione di Voynich, Timm e Schinner e Bibbie latina
    e italiana.
- **Risultati** (media dei sottoinsiemi):

  | proprietà | Voynich | lingue | Timm e Schinner | testi senza senso |
  |---|---|---|---|---|
  | bordo d'inizio | 15,1 | 0,88 | 5,2 | **1,4** |
  | S(1) | 0,52 | 1,04 | 1,02 | **1,11** |
  | lunghezze vicine | 0,062 | −0,123 | −0,001 | −0,007 |
  | ripetizione immediata | 1,02 | 0,06 | 0,74 | 0,69 |
  | accordo a distanza 2 | −0,009 | 0,055 | −0,003 | 0,009 |
  | A | 1,047 | 1,019 | 0,897 | 1,047 |
  | chiusura R | 0,004 | 1,05 | 0,34 | 0,81 |

  (Accordo, A e chiusura non sono discriminanti a questa dimensione.)
- **Esito: "in parte"** (2 proprietà discriminanti su 4; Timm e Schinner 2 su 4).
  - I testi senza senso stanno dalla parte del Voynich nelle proprietà di parola: ripetizioni
    frequenti e lunghezze. Conferma Gaskell e Bowern.
  - Stanno invece dalla parte delle lingue nelle due proprietà d'inizio riga.
- **Lettura.**
  - Le due firme d'inizio riga del Voynich, cioè il bordo forte (15 volte il nullo) e l'evitamento
    dell'inizio della riga precedente (0,52), non si trovano:
    - nelle lingue;
    - nel generatore di Timm e Schinner;
    - nella scrittura inventata spontaneamente da persone.
  - Non nascono "da sole" scrivendo a caso. Sono una regola, applicata in modo sistematico.
  - Limiti: testi brevi, moderni, scritti da persone che sapevano di dover inventare.

## 2/10/2026 — e132: la prima parola della riga è un lemma? Controllo non valido; descrittivamente no

- **Metodo.** Preregistrato.
  - Gruppi: prime parole delle righe (segno y/d/s/o tolto), seconde parole come placebo, prime dei
    paragrafi (gamba tolta).
  - Riferimento: parole interne appaiate per sezione e lunghezza.
  - Misure: unicità (M1a), concentrazione nella pagina (M1b), presenza fra le etichette (M2), titoli
    d'erbario fra le etichette della farmaceutica (M3).
- **Validità: no.** Il controllo negativo (Timm e Schinner senza nomi) dà z 5,8 in M1a e 4,0 in M1b
  sulle prime parole: anche il generatore ha inizi di riga un po' speciali. Per regola nessuna
  conclusione formale.
- **Risultati** (z):

  | gruppo | M1a unica | M1b stessa pagina | M2 etichette | M3 |
  |---|---|---|---|---|
  | prime delle righe, segno tolto | 1,5 | **−5,0** | **−14,5** | −6,5 |
  | seconde (placebo) | −1,5 | −1,4 | −4,0 | 1,6 |
  | prime dei paragrafi, gamba tolta | **14,7** (31% contro 14%) | −1,7 | −4,9 | −0,2 |
  | controllo positivo, prime | −14,3 | 79,4 | | |

- **Lettura** (descrittiva).
  - Le prime parole delle righe sono l'**opposto** dei nomi: meno legate alla pagina e molto meno
    presenti fra le etichette delle parole interne. Il difetto del controllo negativo riguarda i falsi
    positivi, mentre qui l'effetto è negativo, quindi la lettura regge. La prima parola della riga non
    è un lemma.
  - Le prime parole dei paragrafi sono invece spesso uniche (31% contro 14%), ma non ricorrono sulla
    pagina, né fra le etichette, né fra le etichette della farmaceutica. Sono forme singolari, non nomi
    riusati. È la premessa di Vatne (2021) ("la prima parola della pagina d'erbario è il nome della
    pianta"): unicità sì, ma nessuna delle altre tracce di un nome.
  - La strada "lemma come appiglio" si chiude per le righe, e resta debole per i paragrafi.

## 2/10/2026 — e129: griglia più ricca. Riga chiusa e A ≈ 1 sì; la somiglianza locale no

- **Metodo.** Preregistrato.
  - Tre terne di colonne riempite con parti di parole vere del Voynich.
  - Griglia che riparte a ogni riga, spostamento di colonna con probabilità m.
  - R ∈ {36, 72}, m ∈ {0,2; 0,5}, T ∈ {1, 4}; tre semi.
- **Risultati:**
  - pagella 2–5/18, proprietà di riga e di pagina 2–4/12. Migliore: R 36, m 0,5, T 4.
  - **Ottenute:** riga chiusa (R da −0,04 a 0,11 in 6 combinazioni su 8), A ≈ 1 (0,98–1,03),
    ripetizione e tipi.
  - Rispetto all'e124 la ricchezza è migliorata (uniche 0,42–0,59, tipi 0,13–0,25).
  - **Mai ottenute:** omogeneità (0,006–0,009, Voynich ~0,04), gradiente, formule, bordo di riga,
    legame, S(1), copia ed e94. h2 resta alta (2,47–2,62).
- **Esito: nessun avvicinamento.**
- **Lettura.**
  - La griglia dà la riga chiusa e l'assenza di catena, ma non la **somiglianza locale**: le parole di
    una riga del Voynich si somigliano fra loro (omogeneità), mentre quelle della griglia no.
  - Timm e Schinner fa l'opposto: ha la somiglianza, ma per copia a catena (A 0,84).
  - Il Voynich ha somiglianza dentro la riga **senza** catena (A 1,04): come se ogni riga avesse un suo
    "tema" (preferenze di segni scelte per la riga) da cui escono tutte le sue parole. È coerente con
    la grafia ch/sh decisa per riga (e123b).
  - Idea per un modello successivo: parametri di riga, non copia.

## 2/10/2026 — e127: l'anagramma stretto è escluso; l'ordine dei segni è rigido come in Timm e Schinner

- **Metodo.** Preregistrato (ipotesi 2).
  - Prima esecuzione fallita nella parte 2: caratteri rari dell'OCR del *Macer*. Corretto, commit
    e3ea77d.
  - Seconda esecuzione fallita: deriva su testo corto. Corretto come nell'e104 (D-013), commit
    1c9e699.
  - La parte 1 è identica in tutte le esecuzioni; i log dei primi tentativi sono conservati nella
    cartella di lavoro.
- **Parte 1:**

  | testo | coerenza d'ordine | tipi con anagramma |
  |---|---|---|
  | Voynich ZL / IT | 0,878 / 0,876 | 35% / 37% |
  | Timm e Schinner | 0,83–0,84 | 45–47% |
  | lingue | 0,65–0,68 | 5–7% |
  | latino ordinato, 3% guastato | 0,998 | 16% |

- **Parte 2:** pagella 0–1/18 sia ordinato sia no (latino in segni del Voynich per corrispondenza di
  frequenza). Nessuna versione promettente.
- **Esito:**
  - ordine stretto escluso: un terzo dei tipi ha un anagramma;
  - ordine più rigido di una lingua, come quello del generatore che copia parole del Voynich.
  - Ordinare le lettere non avvicina il latino al Voynich.

## 2/10/2026 — e133: le letture di Bax e Vatne non reggono alla verifica sistematica

- **Metodo.** Preregistrato.
  - Fonti: Bax (2014), dall'archivio web, perché il sito risponde 403; Vatne (2021), con la sua
    tabella di lavoro.
  - Nota di trasparenza: in una prova d'accesso a Wikidata, poi abbandonata, ho messo per errore
    l'email di Davide nell'intestazione User-Agent. La richiesta non ha avuto risposta e non è stata
    ripetuta; il test non usa Wikidata.
- **Parte 1, le parole di Bax su tutte le occorrenze.**
  - Per regola "reggono" (7 coerenti su 10), ma **la regola era mal posta**: 6 delle 7 "coerenti" sono
    parole che compaiono una volta sola (kydainy, kydain, koaiin, keedey, ksor, keeredal), quindi
    stanno per forza sulla loro pagina e il confronto non è informativo (z 0).
  - Le tre parole che ricorrono falliscono tutte:
    - **shaiin** (Chiron): 20 occorrenze su 18 pagine, erbario, astronomia, ricette;
    - **shor** (char, "nero"): 96 occorrenze su 67 pagine, in tutte le sezioni;
    - **oror** (arar, ginepro): 8 occorrenze, **nessuna** su f15v o f16r né nell'erbario (sezioni B,
      C, P, S, T). Nella ZL la parola delle pagine del ginepro è "poror", oppure un pezzo di parola.
  - Lettura corretta: dove la verifica è possibile, cioè per le parole ricorrenti, le letture di Bax
    non si comportano da nomi.
- **Parte 2, la chiave di Bax contro 10.000 chiavi casuali.**
  - Sulle 128 pagine d'erbario: S = 7 contro 1,6 (p 0,015). È atteso, perché la chiave è stata
    ricavata da quelle pagine.
  - **Fuori campione**, senza le 7 pagine di Bax: S = 2 contro 0,70 (99° percentile 4; p 0,14).
    **Non batte il caso.**
  - In più, il 12% delle parole interne (3.737 su 30.777) decifra in un "nome" del suo lessico:
    TR ("toro") 1.358 volte, KTN ("cotone") 1.051, KR ("elleboro") 1.042. La chiave produce nomi
    dappertutto, quindi non è specifica.
- **Parte 3, le parole di Vatne.**
  - Delle 84 voci della tabella, 28 si ritrovano identiche nella ZL sulla pagina indicata: Vatne usa
    una trascrizione propria.
  - Di queste, **12 (43%) compaiono anche su altre pagine** (shody in 6 pagine di ricette, chaiin e dol
    in decine di pagine). Le prime parole di confronto fanno il 47%. p = 0,43.
  - L'affermazione "these names are not found at any place in the texts" è **smentita**, e le sue
    parole non si comportano diversamente da qualsiasi prima parola di paragrafo.
- **Esito complessivo.**
  - Nessuna delle due proposte fornisce un appiglio verificato.
  - La chiave di Bax non batte il caso fuori campione, e i suoi nomi ricorrenti stanno dappertutto.
  - Le parole di Vatne non sono diverse dalle altre prime parole.
- **Da fare:** Sherwood (anagrammi, serve il suo alfabeto completo) e Tucker-Talbert (fonti parziali).

## 2/10/2026 — e130: tutte le mani seguono le stesse regole di riga, con intensità diversa

- **Metodo.** Preregistrato.
  - Le proprietà dell'e128 più la quota di sh per riga, per le mani di Davis (variabile $H della ZL).
  - Intervalli bootstrap per pagine.
- **Risultati** (mani 1, 2, 3; lingue in e128: bordo 0,88, S(1) 1,04):
  - **bordo d'inizio:** 13,6 / 30,8 / 21,0;
  - **S(1):** 0,36 / 0,54 / 0,70;
  - **quota di sh per riga:** 1,15 / 1,13 / 1,14, tutte con intervallo sopra 1;
  - **lunghezze vicine:** 0,05 / 0,07 / 0,09;
  - **A:** 1,01 / 1,09 / 1,03;
  - **chiusura R:** −0,03 / 0,06 / 0,00.
  - Mani 4 e 5 (descrittive): bordo 3,5 / 3,7, S(1) 0,55 / 0,69.
- **Esito per regola: "in parte".** Tutte le mani stanno dalla parte del Voynich in tutte le
  proprietà discriminanti, ma gli intervalli del bordo e di S(1) non si sovrappongono fra mani: la
  forza della regola cambia, con la mano 2 al massimo per il bordo e la mano 1 per l'evitamento.
- **Difetto di metodo** (da non riusare così): il bootstrap per pagine duplica righe identiche, e
  questo distorce le misure basate sull'informazione mutua. Gli intervalli dell'accordo e della
  chiusura non contengono nemmeno la stima puntuale e vanno ignorati. Il bordo (JSD) e S(1)
  (rapporto di quote), usati nei criteri, ne risentono poco o niente.
- **Lettura.**
  - Le stesse regole di riga in tutte e cinque le mani, mentre l'invenzione spontanea non le produce
    (e128): è un **sistema condiviso**, non un'abitudine personale.
  - L'intensità diversa può dipendere dalla mano o dalla lingua A/B, che qui coincidono.

## 2/10/2026 — e131: il procedimento per riga riproduce la riga, non il resto

- **Metodo.** Preregistrato.
  - Griglia dell'e129 (R 36, m 0,5, T 4) con colonna d'inizio, evitamento (a 0,5 o 0,9) e grafia
    ch/sh per riga.
- **Risultati:**
  - pagella 4–5/18, proprietà di riga 4–5/12;
  - S(1) da 0,14 a 0,59 (raggiunto con a = 0,5);
  - R ≈ 0;
  - A ≈ 1,0;
  - ma bordo d'inizio 44–46 (troppo forte), copia della prima colonna 0,37–0,78, e94 ≈ 1,0.
  - Mai ottenute: h2, parole uniche, omogeneità, legame, lunghezze vicine, Zipf, forma, verticale,
    formule, bordo di riga, copia, e94.
- **Esito: nessun procedimento completo.**
- **Lettura.**
  - Le regole di riga si mettono facilmente in un procedimento e danno riga chiusa, evitamento e
    assenza di catena.
  - Il resto (forma delle parole, somiglianza locale, preferenza ch/sh in seconda posizione, copia
    della seconda colonna) richiede un meccanismo di produzione delle parole che né la griglia né la
    copia alla Timm e Schinner danno da sole.
  - Il prossimo modello dovrebbe unire la copia locale **dentro la riga** (somiglianza senza catena
    fra righe) con le regole di riga.

## 2/10/2026 — Sherwood e Tucker-Talbert: non verificabili con le fonti raggiungibili

- **Sherwood** (anagrammi italiani, alfabeto "AVA"):
  - il sito non è più online e l'archivio web conserva solo le pagine 1, 2 e 14 dell'appendice di 14,
    cioè 13 piante;
  - la tabella dell'alfabeto è fatta di immagini di circa 50 pixel in cui diversi segni si
    confondono: ricostruirla sarebbe una mia interpretazione, non la sua;
  - il metodo ammette per sua dichiarazione molti gradi di libertà (anagrammi, parole spezzate in due
    o tre, articoli e preposizioni aggiunti, segni "decorativi" ignorati, a/g e d/t intercambiabili).
    L'autrice stessa scrive che gli anagrammi "may produce spurious results".
  - Nessun test riproducibile possibile.
- **Tucker e Talbert** (HerbalGram 100, 2013; nomi nahuatl):
  - l'articolo online ha perso le parole voynichiane, scritte in un font speciale che l'HTML non
    conserva, e il PDF citato non esiste più (404, anche in archivio);
  - restano solo le loro traslitterazioni delle etichette di f100r (nashtli, maguoey, macanol,
    namaepi, acamaaya…), senza la parola EVA né la chiave.
  - Non verificabile senza la versione a stampa.
- Fonti in `dati/cache/letture_proposte/`, non ridistribuite.

## 2/10/2026 — Spoglio di r/voynich

- **Metodo.**
  - Reddit blocca l'accesso automatico (403) e il browser integrato non lo apre.
  - Elenco dei post preso dall'archivio PullPush (api.pullpush.io): 1.800 post da 11/2016 a 9/2026,
    poi il servizio ha limitato le richieste (429). Tenuto in cartella di lavoro, non nel repository.
  - Letti i post con più voti e quelli con affermazioni testabili (parole chiave: decipher, line,
    first word, statistic, cipher, label…).
- **Esito.** Quasi tutto è interpretazione di disegni o traduzione non verificabile (irlandese,
  stenografia ceca, nahuatl, ebraico, "procedural grammar"…). Le cose verificabili:
  1. **Generatore U2/U3** (Whitehatnetizen, 2026), che dichiara di riprodurre "essentially the
     whole 17-metric fingerprint". Codice MIT: messo alla prova nell'e134.
  2. **Naibbe** (Greshko 2025, *Cryptologia*), già in parte nelle e71–e75: completato nell'e134.
  3. **"tolor" = fecondazione** (2025): 3 occorrenze (tolor f38r; otolor f67r2, f77v), con l'idea
     che "o-" sia un articolo. È verificabile in parte: le e72 ed e73 mostrano che o- (con y-, d-,
     s-) è un segno aggiunto a inizio riga per regola di posizione. Da controllare se l'alternanza
     X/oX dipende dalla posizione nella riga. Annotata come idea.
  4. **"Parole uniche non a caso; la prima parola della pagina spesso unica"** (2026): coincide con
     quanto misurato nell'e132 (prime parole dei paragrafi uniche al 31% contro 14%).
  5. **"Margine destro perfetto anche dopo le illustrazioni"** (2025): richiede misure sulle
     immagini. È coerente con la riga chiusa, perché il testo si adatta alla riga. Annotata.

## 2/10/2026 — e136: le righe non rimano

- **Metodo.** Preregistrato (idea 2).
  - Fine di riga = ultimi 2 segni.
  - Si confrontano le fini della riga i e della riga i + k (k = 1–4) nello stesso paragrafo, contro
    1.000 rimescolamenti dell'ordine delle righe nel paragrafo.
  - Il file della *Commedia* contiene il poema due volte: i canti duplicati sono stati tolti prima di
    eseguire, e la preregistrazione è stata aggiornata nello stesso commit.
- **Risultati** (z a k = 1 / 2 / 3 / 4):
  - Voynich ZL: 0,3 / 0,6 / 0,7 / −1,1;
  - Voynich IT: 0,8 / 1,0 / 0,3 / −0,7;
  - Dante (terza rima): 27 / **617** (fini identiche ×15,6) / 66 / 217;
  - Ovidio, *Macer*, Timm e Schinner: tutti sotto 2,5.
- **Esito: nessuna rima**, con un controllo enormemente sensibile.
- **Lettura.**
  - Le fini di righe vicine sono indipendenti fra loro come in versi senza rima, o anche di più.
  - Insieme alla chiusura (e74) e alla catena d'inizio (e105), che guarda solo l'inizio della riga
    sopra: la riga si lega alla precedente **soltanto** con l'evitamento dell'inizio.

## 2/10/2026 — e134: Naibbe e i generatori U2/U3 di Reddit non hanno le proprietà di riga

- **Metodo.** Preregistrato.
  - Naibbe: testo cifrato pubblicato da Greshko (Plinio XVI), mandato a capo sulle larghezze del
    Voynich.
  - U2/U3: rigenerati con il loro codice (commit ccd5db0, seme 1492) in un ambiente separato.
  - Prima esecuzione fermata da un errore di formattazione della tabella dopo il calcolo, corretto in
    ef24971; risultati identici.
- **Risultati** (Voynich: S(1) 0,53, bordo 23/56, R 0,01, sh per riga 1,14, A 1,04):

  | testo | riga e pagina | S(1) | bordo inizio / fine | R | sh per riga | A |
  |---|---|---|---|---|---|---|
  | Naibbe | 3/12 | 0,97 | 2,9 / 1,7 | 0,08 | 0,98 | 1,01 |
  | U2 | 1/12 | 1,25 | 1,2 / 1,0 | 0,00 | 1,04 | 1,04 |
  | U3 | 2/12 | 1,51 | 1,3 / 0,7 | 0,99 | 1,05 | 1,03 |

- **Esito:** nessuno riproduce la struttura di riga. Nessuno ha l'evitamento dell'inizio, il bordo
  forte o la grafia decisa per riga.
  - U3, che copia dalla riga sopra, apre la riga invece di chiuderla (R 0,99), e la copia di colonna
    è 3,5 volte il caso.
  - Il "17-metric fingerprint" di U2/U3 riguarda le parole, non la riga.
- **Nota sul criterio dell'accordo nella riga:** qui le pagine sono blocchi di 29 righe, non le pagine
  vere. Il Voynich stesso dà z 3,0, mentre con le pagine vere (e126) dava −0,5: scambiare parole fra
  righe di pagine vere diverse porta dentro l'omogeneità di pagina. Il criterio dell'accordo non
  discrimina in questo formato; l'esito non cambia, perché i generatori falliscono già le altre
  condizioni.

## 2/10/2026 — e135: cinque scelte di grafia su sette sono decise per riga, ma indipendenti fra loro

- **Metodo.** Preregistrato (idea 1).
  - Sette scelte binarie, ciascuna con il suo contesto più la pagina negli strati: ch/sh, k/t, -l/-r
    finale, e/ee, qo-/o-, ain/aiin, -dy/-ey.
  - Misure: varianza per riga contro i rimescolamenti negli strati; accoppiamento fra scelte (media
    delle 21 correlazioni dei residui di riga).
- **Risultati.**
  - **Scelte decise per riga** (rapporto, z):
    - k/t 1,13 (10,1), -dy/-ey 1,12 (8,3), ch/sh 1,14 (7,8), -l/-r 1,07 (4,0), qo-/o- 1,06 (3,7);
    - sotto soglia: e/ee 1,05 (2,8), ain/aiin 1,04 (2,3).
    - Timm e Schinner: solo -l/-r (6,2).
  - **Accoppiamento:** C = 0,005 (z 1,1). Il controllo positivo (stato imposto al 30%) dà z 35,9.
  - Coppie notevoli:
    - e/ee ~ -dy/-ey r −0,19 (z −8,9): probabilmente meccanica, perché le due scelte cadono negli
      stessi segni della stessa parola (-ey);
    - -dy/-ey con ch/sh, k/t e qo-: r ≈ +0,07 (z 3,7–3,9);
    - -l/-r ~ qo-: −0,06 (z −3,1).
- **Esito per regola: nessuno stato di riga comune** (5 scelte per riga sì, accoppiamento no).
- **Lettura.**
  - È una proprietà nuova e forte: **la riga è l'unità in cui si fissano molte scelte di grafia**, non
    solo ch/sh. Ogni riga ha le sue preferenze, oltre a quelle della pagina e del contesto.
  - Le preferenze però variano **in modo indipendente** l'una dall'altra, con al più un debole legame
    attorno a -dy. Non c'è una "chiave di riga" unica da stimare e togliere: la strada "normalizzare
    la riga" come passo di decifrazione non è aperta.
  - È compatibile con un procedimento che per ogni riga sceglie separatamente più parametri (colonne
    di una tavola, varianti), o con una scrittura che riga per riga riprende abitudini diverse.

## 2/10/2026 — e137 ed e137b: nessuna numerazione degli inizi di riga

- **e137** (preregistrato): ordine 2 delle classi d'inizio, cioè I(c_i ; c_{i−2} | c_{i−1}), con
  z 5,6 (ZL) e 6,1 (IT) contro una catena unica del primo ordine.
  - Nessun periodo da 2 a 6 (z da −1,2 a 0,3). Il controllo con un ciclo di 4 dà z 26–45.
  - Per regola "numerazione: sì". Ma Timm e Schinner, che non ha numerazione, dà 6,2: il nullo a
    catena unica non controllava le differenze fra sezioni e mani. È un difetto di disegno.
- **e137b** (preregistrato dopo l'e137): catene del primo ordine stimate per sezione + mano (N1) e
  per fascicolo (N2).
  - Il Voynich scende a z 2,9 / 2,4 (ZL) e 3,3 / 3,1 (IT). Il controllo resta a 20,7. Timm e Schinner,
    a blocchi, resta a 5,3.
  - Esito per regola: **indeciso**.
- **Lettura complessiva.**
  - Nessuna periodicità, quindi nessun contatore o ciclo.
  - Un residuo debole di ordine 2 (z ≈ 3) che una catena unica non spiega, ma che anche un generatore
    senza regole di riga mostra più forte.
  - L'inizio di riga resta descritto come regola di evitamento della riga sopra, non come
    numerazione.

## 2/10/2026 — e139: y-, d- e s- sono segni d'inizio riga; o- no

- **Metodo.** Preregistrato (idea 5, dal post di r/voynich su "tolor"/"otolor").
  - Coppie X/PX (P = o, y, d, s), con la quota di PX per posizione nella riga.
  - Rapporto prima/interna contro 1.000 rimescolamenti dentro la riga.
- **Risultati** (quota di PX; prima / interna; rapporto, z):

  | prefisso | prima | interna | rapporto (z) |
  |---|---|---|---|
  | s- | 0,53 | 0,04 | **14,8** (99,9) |
  | y- | 0,35 | 0,07 | **5,3** (42,3) |
  | d- | 0,58 | 0,16 | **3,6** (42,0) |
  | o- | 0,27 | 0,29 | 0,91 (−2,2) |

- **Esito:**
  - y-, d- e s- sono **posizionali**: compaiono quasi solo a inizio riga e raramente fuori posizione;
  - o- **non** è posizionale: l'alternanza X/oX vale circa 29% ovunque, ed è più rara come prima
    parola di paragrafo (6%).
- **Correzione di una lettura precedente.** Nelle e72/e73 avevo scritto "segno aggiunto y, d, s o o".
  I dati dicono che il segno d'inizio riga è y, d o s, mentre o- è un fenomeno diverso, presente in
  tutta la riga.
- **Su "tolor":** tolor (f38r, prima di paragrafo), otolor (f67r2 e f77v, entrambe fuori dal testo in
  paragrafi). L'idea che o- sia un elemento che si aggiunge alle parole ovunque, non legato alla
  posizione, è **compatibile** con i dati. Che significhi "il/la" non è verificabile con questo test.

## 2/10/2026 — e138: nessuna struttura di voce stabile nelle righe dei paragrafi

- **Metodo.** Preregistrato (idea 4).
  - Profili di segni delle parole interne, k-medie, righe dalla seconda di ogni paragrafo.
  - Statistica: informazione mutua fra tipo e posizione nel paragrafo, contro il rimescolamento
    dell'ordine delle righe.
- **Risultati** (z posizione / z riga seguente):
  - Voynich: k 4: 2,9 / 6,0; k 3: 6,4 / 4,7; k 6: 0,9 / 3,9;
  - controllo positivo: 146–157;
  - Timm e Schinner: tutti sotto 1.
- **Esito: voce strutturata no.** L'effetto della posizione è instabile: forte con 3 tipi, debole con
  4, assente con 6.
- **Lettura.**
  - Non c'è un ordine ripetuto di tipi di riga dentro il paragrafo (tipo "nome, descrizione, uso"),
    oltre agli effetti noti di prima riga e di bordo.
  - È invece costante una somiglianza fra righe consecutive (z 4–6), che il generatore non ha: è il
    gradiente locale già noto, ora visto anche nel profilo dei segni delle parole interne.

## 2/10/2026 — e141: il testo è composto nelle righe della pagina, non copiato da un modello con altri a capo

- **Metodo.** Preregistrato.
  - Si confrontano le righe che seguono una riga accorciata (< 60% della mediana della pagina, non
    ultima di paragrafo: di solito accorciata da un disegno) con quelle che seguono una riga piena.
  - Controllo positivo: il 10% delle righe piene spezzate artificialmente al 40%.
- **Risultati:**

  | gruppo | coppie | inizio y/d/s [90%] | stesso primo segno | R giuntura |
  |---|---|---|---|---|
  | Voynich, dopo riga corta | 65 | **0,554** [0,46–0,65] | 0,09 | 0,16 |
  | Voynich, dopo riga piena | 2.667 | 0,477 [0,46–0,49] | 0,07 | −0,02 |
  | controllo, dopo riga corta | 404 | 0,287 [0,25–0,32] | 0,11 | 0,50 (z 4,9) |

- **Esito: composto sul posto.** Rapporto corta/piena 1,16 nel Voynich contro 0,60 nel controllo.
- **Lettura.**
  - Dopo una riga accorciata da un disegno, la riga seguente ricomincia con il segno d'inizio come
    tutte le altre, e la giuntura resta chiusa.
  - Le righe non sono pezzi di righe di un modello con un'altra impaginazione: chi scriveva componeva
    ogni riga nello spazio che aveva sulla pagina.
  - Questo indebolisce l'idea, emersa su Reddit, di un testo prodotto altrove e poi ricopiato in bella
    dagli scribi. Se c'era un modello, aveva già le stesse righe, oppure le regole si applicavano al
    momento della scrittura in pagina.

## 2/10/2026 — e142: le etichette dei due Ariete e dei due Toro non si somigliano più del caso

- **Metodo.** Preregistrato.
  - Le 11 coppie di pagine zodiacali consecutive, di cui 2 dello stesso segno (f70v1–f71r Ariete,
    f71v–f72r1 Toro).
  - Somiglianza delle etichette: coseno dei bigrammi di segni, Jaccard dei tipi, e coseno su etichette
    più cerchi.
  - Nullo esatto sulle 55 scelte di 2 coppie.
- **Risultati:**
  - coseno etichette: 0,869 stesso segno contro 0,833 (p 0,31);
  - Jaccard: 0,038 contro 0,032 (p 0,42);
  - etichette più cerchi: 0,940 contro 0,928 (p 0,27).
  - La coppia più simile è f70v2–f70v1 (Pesci–Ariete). Ariete–Ariete ha 0 parole in comune.
- **Esito: nessuna prova** che le etichette dipendano dal segno disegnato. Potenza bassa (11 coppie).
- **Lettura.** È coerente con l'osservazione di r/voynich: il vocabolario segue la posizione nel
  manoscritto (e le mani), non il soggetto dei disegni. Le due pagine dello stesso segno sono vicine
  nel libro, ma non più simili fra loro di due pagine vicine di segni diversi.

## 2/10/2026 — e143: inizio e fine della stessa riga non sono legati (controllo non valido)

- **Metodo.** Preregistrato.
  - Informazione mutua fra la classe del primo segno e l'ultimo segno della stessa riga, contro il
    rimescolamento delle fini fra righe della stessa pagina e della stessa classe di lunghezza.
- **Risultati:**
  - Voynich: IM 0,0287 contro 0,0299 (z −0,4);
  - Timm e Schinner: z 1,3;
  - controllo positivo (in un terzo delle righe che cominciano con s, l'ultimo segno diventa m):
    z 6,4.
- **Validità: no**, perché il controllo positivo non arriva a z 10. L'effetto imposto era piccolo:
  riguarda solo le righe in s.
- **Lettura** (descrittiva): nel Voynich l'informazione mutua osservata è persino sotto il nullo.
  Nessuna traccia di una cornice inizio–fine, con una sensibilità inferiore a un legame che tocca il
  30% delle righe in s. Le celle più lontane da 1 (G…m ×1,39, y…m ×1,26, G…n ×0,72) restano entro la
  variazione del nullo complessivo.

## 2/10/2026 — e140: le varianti lunghe non servono a riempire la riga

- **Metodo.** Preregistrato.
  - Correlazione di Spearman, entro pagina, fra il surplus di varianti lunghe (ee, aiin, qo-) di una
    riga e la sua "base" (lunghezza con le varianti portate alla forma corta).
  - Nullo: 1.000 rimescolamenti delle scelte negli strati.
- **Risultati** (rho, z):
  - Voynich, righe interne −0,125 (−6,0);
  - Voynich, ultime righe di paragrafo (non allineate) −0,139 (−2,8);
  - controllo positivo −0,58 (−28,3);
  - Timm e Schinner −0,22 (−12,4).
- **Esito per regola: no.** La correlazione negativa c'è, ma:
  - ha la stessa forza nelle ultime righe di paragrafo, che non vanno a margine;
  - è ancora più forte nel generatore, che non allinea nulla.
  È un effetto generico della misura (righe fatte di parole corte e scelte con varianti lunghe vanno
  insieme anche senza intenzione), non un allineamento.
- **Lettura.** Le scelte di grafia decise per riga (e135) non si spiegano con il riempimento della
  riga. L'osservazione di r/voynich sul margine destro regolare resta da misurare sulle immagini.

## 2/10/2026 — e144: le etichette dello zodiaco non hanno un posto fisso nella ruota

- **Metodo.** Preregistrato. Spunto da r/voynich (Ockanacken 2025).
  - 293 etichette delle 12 ruote, con l'ora d'orologio e l'anello ricavati dalla trascrizione ZL
    (commenti `<!hh:mm>`, testi circolari Cc).
- **Risultati:**
  - **(A) settore:** le coppie con la stessa radice in ruote diverse distano in media 3,02 ore,
    contro 2,98 del caso (z 1,2; con radici di 4 segni z −0,1). Il controllo positivo dà z −7,3.
  - **(B) anello:** nessuna preferenza (z −1,7).
  - **(C) famiglia yke-:** 8 etichette su 10 in Scorpione e Sagittario (p = 6·10⁻⁵); le altre 2 sono
    in Vergine e Bilancia. Sono le ultime quattro ruote, consecutive nel manoscritto.
- **Esito:** settore no, anello no, yke confinata sì.
- **Lettura.**
  - Le osservazioni del post ("otar" alla stessa ora nei due Toro, okal/otal per anello) sono casi
    singoli che, presi tutti insieme, non superano il caso. Le etichette non seguono lo schema della
    ruota (posizione, anello), quindi niente che faccia pensare a giorni o gradi.
  - La famiglia yke- è reale, ma si spiega con la deriva del vocabolario lungo il manoscritto (e142,
    e il post sul vocabolario che segue la posizione): compare alla fine dello zodiaco, non in un
    punto preciso delle ruote.

## 2/10/2026 — e147: il testo non si adatta allo spazio, e il margine destro non è "perfetto"

- **Metodo.** Preregistrato. Riquadri delle parole di voynichese.com (come nell'e34), 178 pagine di
  testo in paragrafi. Spunti da r/voynich.
- **Risultati:**
  - **(1)** nelle righe che cominciano dopo un disegno le parole non sono più corte: +0,05 segni,
    z 0,4 (124 righe spostate su 31 pagine);
  - **(2)** i segni non sono più stretti: +0,003 segni/pixel, intervallo da −0,001 a 0,007;
  - **(3)** il margine destro è **meno** regolare di un semplice "vado a capo quando la parola non
    entra": dispersione delle fini 0,084 contro 0,043 simulata (rapporto 1,95 [1,77–2,15]).
- **Esito: no su tutte e tre.**
- **Lettura.**
  - Nessun adattamento delle parole allo spazio, nessuna compressione, nessun allineamento attivo.
  - L'impressione su Reddit di righe che "finiscono esattamente allo stesso margine" non regge alla
    misura. Le righe finiscono in modo più irregolare di un riempimento meccanico, come è normale se
    chi scrive va a capo anche prima del margine, per esempio alla fine di una riga composta come
    unità (e74, e141).

## 2/10/2026 — e148: le due metà di un bifoglio si somigliano molto più dei vicini — scrittura per bifoglio

- **Metodo.** Preregistrato.
  - Coppie di fogli coniugati (stesso fascicolo $Q e bifoglio $B della ZL) contro coppie non coniugate
    dello stesso fascicolo, alla stessa distanza, con la stessa mano e la stessa lingua.
  - Quantile di ogni coppia coniugata fra le sue coppie di confronto; nullo uniforme.
- **Risultati** (23 coppie utilizzabili):
  - coseno dei tipi di parola: media dei quantili **0,827**, p < 0,0001;
  - coseno dei bigrammi di segni: **0,844**, p < 0,0001;
  - profili delle preferenze di grafia: 0,536, p 0,27.
  - Coppie coniugate più simili di tutte le loro coppie di confronto: 16 su 23 nella misura (1)
    (per esempio f3–f6, f19–f22, f76–f83, f78–f81, f108–f111).
- **Esito: bifogli scritti come unità.**
- **Lettura.**
  - Anche a parità di mano, lingua, fascicolo e distanza, le due metà dello stesso foglio piegato
    condividono vocabolario e combinazioni di segni più dei fogli vicini nell'ordine attuale. Il
    testo, o almeno il suo vocabolario, è stato prodotto **bifoglio per bifoglio**, prima che i fogli
    fossero piegati e messi nell'ordine attuale.
  - Va con la deriva del vocabolario (e142, e144): una sessione di scrittura corrisponde a un foglio
    aperto, non a pagine consecutive del libro rilegato. L'ordine di rilegatura non è l'ordine di
    scrittura.
  - Le preferenze di grafia per riga non seguono il bifoglio: variano più in fretta (e135, e146).
  - **Limiti:** molti quantili si basano su 2 sole coppie di confronto; i fascicoli balneologici (f75–f84)
    sono molto omogenei al loro interno. Il risultato regge però su 23 coppie e due misure.
  - **Prossimo passo** (da preregistrare): ricostruire l'ordine di scrittura dei bifogli dalla
    somiglianza, e controllare se la deriva del vocabolario diventa più regolare in quell'ordine che
    in quello attuale.

## 2/10/2026 — e150 ed e150b: i bifogli hanno un ordine di somiglianza che la rilegatura non segue

- **e150** (preregistrato).
  - Unità: 52 bifogli (o fogli singoli).
  - Si ricostruisce un ordine che massimizza la somiglianza di vocabolario fra unità consecutive,
    calcolata su metà delle righe (avido + 2-opt), e lo si valuta sull'altra metà, per 20 divisioni.
  - Ricostruito 0,50–0,54 contro rilegatura 0,42–0,45 e ordini casuali 0,31–0,34: vince **20 su 20**.
  - Ma l'ordine ricostruito separa nettamente mani e lingue: prima tutti i bifogli B, poi tutti gli A.
    Il guadagno poteva venire solo da questo, già noto.
- **e150b** (preregistrato dopo l'e150): la stessa prova **dentro** i gruppi di stessa mano e lingua
  (mano 1/A: 27 unità; 2/B: 11; 3/B: 7).
  - Ricostruito 0,53–0,57 contro rilegatura 0,50–0,52: vince **20 su 20** in totale e 20 su 20 nel
    gruppo più grande da solo.
- **Esito per regola:** ordine diverso dalla rilegatura sì, anche dentro le mani.
- **Lettura, con cautela.**
  - Fra i bifogli c'è una struttura di somiglianza di vocabolario stabile: la si ritrova uguale in due
    metà indipendenti delle righe. L'ordine di rilegatura non la segue, nemmeno dentro la stessa mano.
  - Insieme all'e148 (le due metà di un bifoglio si somigliano molto), è compatibile con una
    produzione per bifogli in un ordine diverso da quello attuale, con il vocabolario che deriva da un
    bifoglio al successivo.
  - **Non lo dimostra.** La stessa struttura potrebbe venire da somiglianze di contenuto (piante
    simili scritte con parole simili) o da gruppi non lineari. Che sia una sequenza, e non una
    raccolta di gruppi, andrebbe provato a parte (per esempio con la continuità di mano, inchiostro o
    impaginazione nell'ordine ricostruito).
  - Interessa il white paper: la rilegatura attuale non è l'ordine di produzione, in accordo con
    quanto si sa dalla codicologia (bifogli rimescolati).

## 2/10/2026 — e149: le etichette sono un lessico a sé, segnato da o-

- **Metodo.** Preregistrato. Spunto da r/voynich.
  - 996 etichette (prima parola). Attestazione nel testo dei paragrafi, così come sono e togliendo il
    primo segno, contro parole del testo della stessa lunghezza.
  - Il confronto è solo per lunghezza, non per sezione: lo zodiaco non ha testo in paragrafi. La
    preregistrazione è stata aggiornata prima di eseguire.
- **Risultati** (tutte le etichette):
  - **(a)** attestate nel testo: 57% contro 79% (z −19);
  - **(b)** fra le non attestate, attestate togliendo il primo segno: 22% contro 36% (z −4);
  - **iniziali:** o- 59% (zodiaco 76%) contro 21% nel testo. Gallow 3% (zodiaco 0%) contro 8%.
- **Esito: lessico a sé** (non "testo + prefisso").
- **Lettura.**
  - Le etichette non sono parole del testo con un segno davanti: togliendo il primo segno si
    ritrovano nel testo **meno** spesso delle parole del testo.
  - Sono forme proprie, spesso uniche, con una marca iniziale forte: **o-**, che nel testo è un
    elemento qualunque (e139) e nelle etichette è la norma.
  - È come la regola d'inizio riga (y/d/s): una posizione o un tipo di testo ha la sua marca
    d'inizio. Per le etichette è o-.
  - Per un contenuto, sarebbero il posto giusto per cercare nomi. Ma le prove sui nomi (e35, e122 in
    standby, e133, e144) non hanno finora trovato legami fra etichette e disegni.

## 2/10/2026 — e146: le preferenze di riga derivano in 3–5 righe e ripartono a ogni pagina

- **Metodo.** Preregistrato.
  - Correlazione dei residui di riga delle cinque scelte decise per riga (e135; strati senza pagina)
    fra righe a distanza d.
  - Nullo dentro pagina: righe rimescolate nella pagina. Intervalli bootstrap per pagine.
- **Risultati, Voynich** (r, z):
  - dentro la pagina: d = 1: 0,207 (9,4); d = 2: 0,195 (7,5); d = 3: 0,169 (4,5); d = 5: 0,147 (2,0);
    d = 10: 0,126 (0,2), cioè il livello di pagina;
  - a cavallo di paragrafo: 0,147 contro 0,222 dentro il paragrafo (si attenua, non riparte);
  - a cavallo di pagina: **0,095** [0,03–0,16] contro 0,207 [0,19–0,23] (riparte).
- **Timm e Schinner:** eccesso solo a d = 1 (z 4,3) e poi piatto (copia della parola appena scritta).
  Nessun calo fra le sue "pagine" di 29 righe (0,277), che non sono pagine vere.
- **Esito:** deriva locale sì, ripartenza a pagina sì, ripartenza a paragrafo no.
- **Lettura.**
  - Le preferenze di grafia hanno una memoria di 3–5 righe, oltre al livello comune della pagina, e
    cambiano in modo netto al cambio di pagina.
  - Ha la forma delle abitudini di una persona che scrive in sessioni, con la pagina come unità di
    lavoro: una deriva lenta, non una copia della parola precedente.
  - Va con l'e148 (bifogli scritti come unità) e l'e141 (righe composte sul posto).
  - Questi valori fissano i parametri del generatore e145.

## 2/10/2026 — e151: le ricette non sono in ordine da glossario

- **Metodo.** Preregistrato. Spunto da r/voynich ("Quire 20 might be a glossary").
  - Prefissi condivisi fra le prime parole di paragrafi consecutivi (gallow iniziale tolto), contro il
    rimescolamento dei paragrafi nella pagina.
  - Controllo positivo: i lemmi dell'*Alphita*, glossario alfabetico.
- **Risultati** (primi 2 segni):
  - ricette (S): 0,146 contro 0,132 (×1,10, z 0,8);
  - erbario: ×0,88 (z −0,8);
  - *Alphita*: 0,458 contro 0,312 (×1,47, z 20,6).
- **Esito: nessun ordine alfabetico** né di altro tipo per prefisso nei paragrafi delle ricette, con un
  controllo molto sensibile.
- **Lettura.** I paragrafi stellati non sono le voci di un elenco ordinato. È coerente con l'e132:
  le prime parole dei paragrafi sono spesso uniche ma non si comportano da lemmi.

## 2/10/2026 — e145: le abitudini che derivano riproducono le scelte per riga, non la chiusura

- **Metodo.** Preregistrato.
  - Modello minimo: parole vere di ogni pagina rimescolate fra le righe, regola d'inizio (e131,
    a = 0,5), cinque preferenze di grafia AR(1) per riga con ripartenza parziale a ogni pagina.
  - Griglia ρ ∈ {0,6; 0,85} × σ ∈ {0,4; 0,8}, più due riferimenti (solo regola; niente).
- **Risultati** (Voynich: S(1) 0,52, R 0,006, A 1,044, 5 scelte per riga, r consecutive 0,207):
  - **con abitudini:**
    - scelte decise per riga 3,3–5,0;
    - r consecutive 0,16–0,17 con (0,6; 0,8) e (0,85; 0,4), cioè vicino al Voynich;
    - S(1) 0,62–0,66.
  - **ma:** R 0,53–0,71 (nessuna chiusura; −0,23 con (0,85; 0,8), instabile), A 0,99, pagella
    10–11/18.
  - **riferimenti:** solo regola S(1) 0,58; senza nulla S(1) 1,02.
- **Esito: nessuna combinazione basta per la riga.**
- **Lettura.**
  - Le abitudini AR(1) riproducono le scelte decise per riga e la loro memoria fra righe (e135,
    e146). La regola d'inizio riproduce l'evitamento.
  - La **chiusura della riga** e l'alternanza A ≥ 1 non vengono da questi due meccanismi. Dipendono
    dall'ordine delle parole dentro la riga e dalle giunture, che il modello rimescola: R qui è
    instabile perché, senza ordine, le giunture interne hanno eccesso quasi nullo.
  - Il prossimo modello deve produrre la riga **in ordine**, con giunture e somiglianza locale, non
    rimescolare parole vere.

## 2/10/2026 — e152: un generatore che scrive le righe in ordine riproduce la firma di riga del Voynich

- **Metodo.** Preregistrato.
  - Ogni riga: inizio con regola (y/d/s, evitamento della riga sopra); tema di k parole della pagina;
    parole successive come varianti del tema (Poisson μ), scelte in base alla giuntura con la parola
    precedente; abitudini di grafia AR(1) (ρ 0,6, σ 0,8).
  - k ∈ {2, 4} × μ ∈ {0,5; 1,0}, più un'ablazione senza giunture.
- **Risultati** (Voynich: S(1) 0,52, R 0,006, A 1,044, 5 scelte per riga, r 0,207):
  - **tutte e 4 le combinazioni con giunture riproducono la riga:** S(1) 0,61–0,66, R da −0,02 a
    0,03, A 1,009–1,028, 5 scelte decise per riga su 5, r fra righe consecutive 0,17;
  - **senza giunture:** A 0,996 (sotto 1), quindi la riga non è riprodotta. La scelta per giuntura
    contribuisce all'alternanza;
  - **pagella 6–10/18; "completo" no.** Il modello esagera la somiglianza dentro la riga (omogeneità
    0,10–0,20 contro circa 0,04; formule 37–169 volte il caso). Mancano anche e94 (≈1,05 contro 1,43),
    verticale, gradiente, bordo di riga, Zipf, e h2 è un po' alta (2,43–2,58).
- **Esito per regola:** riga riprodotta sì (4 combinazioni), completo no.
- **Lettura.**
  - È il primo modello del progetto che riproduce **insieme** tutte le proprietà di riga misurate:
    - riga chiusa;
    - evitamento dell'inizio sopra;
    - alternanza A ≥ 1 senza copia a catena;
    - cinque scelte di grafia decise per riga;
    - memoria delle preferenze fra righe.
  - La ricetta è: comporre la riga come unità a sé, con una regola d'inizio; scrivere le parole come
    varianti di un piccolo tema della riga, attaccandole per giuntura; lasciare che le abitudini di
    grafia derivino da una riga all'altra.
  - Ciò che resta fuori riguarda la pagina e la parola:
    - il tema è troppo forte, perché le righe diventano formulaiche;
    - la preferenza ch/sh in seconda posizione (e94);
    - il gradiente verticale.
  - Mostra che un procedimento senza messaggio di questo tipo **basta** per la riga. Non mostra che
    il Voynich sia stato fatto così, né esclude un contenuto codificato nelle parole del tema.

## 2/10/2026 — e154 ed e154b: l'ordine ricostruito dei bifogli è confermato dalle abitudini di grafia

- **e154** (preregistrato).
  - Dentro i gruppi di stessa mano e lingua, l'ordine dei bifogli ricostruito dal vocabolario rende
    più graduali due cose:
    - **(I) grafia** (preferenze delle cinque scelte per riga): 2,61 contro 2,94 della rilegatura e
      3,14 del caso, p < 0,001;
    - **(II) impaginazione** (parole e segni per riga, righe per paragrafo, gallow p/f): 2,34 contro
      2,32 della rilegatura, cioè nessun guadagno sulla rilegatura (p 0,04 sul caso).
  - Esito per regola: confermato.
  - **Difetto riconosciuto subito:** le scelte di grafia cambiano l'identità delle parole, quindi la
    misura (I) non era indipendente dal vocabolario.
- **e154b** (preregistrato dopo l'e154): l'ordine si ricostruisce su un vocabolario con le cinque
  scelte unificate (ch=sh, k=t, -l=-r, qo-=o-, -dy=-ey), poi si misura la grafia.
  - Ricostruito 2,55, rilegatura 2,94, caso 3,13, p < 0,001.
  - Per gruppo: mano 1/A 2,48 contro 3,10; mano 3/B 2,70 contro 3,01; mano 2/B 2,65 contro 2,46 (qui
    no).
- **Esito: ordine confermato dalla grafia.**
- **Lettura.**
  - Un ordine dei bifogli ricostruito solo dal vocabolario, senza le scelte di grafia, mette vicini
    anche bifogli con abitudini di grafia simili. Due tracce indipendenti della scrittura concordano
    su un ordine diverso dalla rilegatura, soprattutto per la mano 1 (erbario A, 27 unità).
  - È l'indizio più forte finora di un **ordine di produzione** diverso da quello di rilegatura,
    ricostruibile dai dati. L'impaginazione non lo conferma né lo smentisce.
  - **Limiti:**
    - le abitudini di grafia potrebbero seguire anche il contenuto (piante simili), non solo il
      tempo;
    - la mano 2 non lo conferma;
    - un controllo materiale (inchiostro, rigatura, pigmenti) resta il passo decisivo e non è
      statistico.

## 2/10/2026 — e122b: le pagine della farmacia non condividono parole con l'erbario della stessa pianta

- **Metodo.** Preregistrato. Misura dell'e122 (Davide non riesce ad abbinare a mano).
  - **(A)** le 14 corrispondenze pubblicate nei commenti della ZL (Petersen, Stolfi, FSG, GL), anche
    quelle senza un'etichetta propria, perché qui conta la pagina intera.
  - **(B)** abbinamenti visivi fatti da me sulle immagini. **Esito: nessuno affidabile.** I frammenti
    della farmacia sono quasi tutti radici e foglioline senza tratti distintivi; le somiglianze con le
    piante dell'erbario erano vaghe e non le ho registrate. Lo dichiara `dati/abbinamenti_visivi.json`,
    committato prima dell'analisi.
- **Risultati (A)**, 14 coppie su 8 pagine della farmacia:
  - quota dei tipi della farmacia presenti nella pagina d'erbario abbinata: 0,099 contro 0,101 del
    caso (p 0,54);
  - con le varianti: 0,278 contro 0,278 (p 0,50);
  - normalizzata: 0,97 (p 0,60).
- **Esito:** nessun segnale di nominazione. La validità minima di 15 coppie non è raggiunta (14).
- **Lettura.**
  - Le pagine abbinate condividono **esattamente** quanto il caso: nessuna traccia che le parole
    della farmacia nominino la pianta disegnata.
  - Con l'e35 (etichette della farmacia assenti dall'erbario) e l'e142 (segni zodiacali doppi) è la
    terza prova sul legame fra parole e disegni, e la terza senza legame.
  - Il numero di coppie è piccolo: un effetto debole non si escluderebbe. Ma la media è anzi sotto il
    caso.

## 2/10/2026 — e156: le "lingue" A e B non sono solo abitudini di grafia (controllo non valido)

- **Metodo.** Preregistrato.
  - Eccesso di divergenza fra le distribuzioni delle parole di A e B (oltre la variabilità interna).
  - Prima e dopo l'unificazione delle cinque scelte di grafia (N1) e delle varianti ee/aiin (N2).
- **Risultati:**
  - eccesso A/B: 0,246 (grezzo) → 0,234 (N1) → 0,225 (N2). La grafia ne spiega solo il **5–8%**;
  - fra le mani 2 e 3 (entrambe B): eccesso 0,061 → 0,052, cioè 15% spiegato.
- **Validità: no.**
  - Il controllo positivo (A riscritto con le quote di B) era mal costruito: confronta A con sé stesso
    riscritto, quindi le stesse pagine, contro due metà di A fatte di pagine diverse. L'eccesso
    risulta negativo già sul grezzo e la quota non si può calcolare.
  - Errore di disegno mio: il controllo andava fatto su metà diverse di A.
- **Lettura** (descrittiva, ma netta): unificare le varianti di grafia riduce di pochissimo la
  differenza fra A e B. Le due "lingue" di Currier differiscono nel vocabolario (quali parole e con
  che frequenza), non solo nelle abitudini di grafia decise per riga.

## 2/10/2026 — e158: il "riconoscimento" dell'ebraico di Hauer e Kondrak lo dà anche un testo senza messaggio

- **Metodo.** Preregistrato. Ricostruzione dei due metodi di Hauer e Kondrak indipendenti dalla chiave
  (profilo di frequenza F; schemi di ripetizione nella parola P; versione per anagrammi A) su 109
  lingue.
- **Validità:** lingua giusta prima nel **100%** di 20 lingue cifrate, con tutti e tre i metodi.
- **Risultati** (prime lingue, sicurezza, posizione dell'ebraico):
  - **Voynich:** F Latin… (1,37; ebraico 22°); P Danish, Arabic, **Hebrew** (1,08; 3°); A Arabic,
    Syriac… (0,94; 8°);
  - **Timm e Schinner:** P **Hebrew** primo, sicurezza 1,17, più del Voynich; A Syriac, Arabic,
    Hebrew;
  - **generatore e152:** P Danish, Arabic, Syriac, Hebrew; A Arabic, Syriac;
  - **testi inventati a mano:** Albanian, Telugu… (ebraico 39°–75°).
- **Esito:** l'indicazione sul Voynich **non è informativa**. Un generatore senza messaggio (Timm e
  Schinner) ottiene l'ebraico per primo con più sicurezza del Voynich.
- **Lettura.**
  - L'affinità con le lingue semitiche viene dalla **forma delle parole** del Voynich (pochi schemi di
    ripetizione delle lettere), che ogni testo costruito con le sue regole di parola condivide, non
    da una lingua sottostante.
  - Sono i controlli che mancavano nel lavoro originale.

## 2/10/2026 — e159: le "parole-chiave" di Montemurro e Zanette le hanno anche i testi senza messaggio

- **Metodo.** Preregistrato.
  - Indice d'informazione delle parole sulla posizione nel testo, I = Σ (n/N)(H̃ − H), su Voynich,
    Bibbia latina, Timm e Schinner, generatore e152 e testi inventati a mano.
- **Risultati** (bit per parola):
  - **N 35.000, P 32:** Voynich 0,29; latino 0,16; Timm e Schinner **0,31**; e152 0,34;
  - **N 10.000, P 10:** Voynich 0,08; latino 0,09; Timm e Schinner **0,23**; testi inventati **0,24**;
    e152 0,16.
- **Esito: le parole-chiave non distinguono un contenuto.** Un generatore senza messaggio e i testi
  inventati da persone hanno tanta o più "struttura per argomenti" del Voynich.
- **Lettura.** L'organizzazione delle parole per posizione nel libro, presentata come segno di un
  contenuto organizzato per temi, nasce anche da una deriva del vocabolario senza significato (copia
  locale, abitudini che cambiano, invenzione spontanea). Le parole-chiave del Voynich (shedy,
  qokeedy, qokain…) sono le stesse che separano le lingue A e B (e156).

## 2/10/2026 — e153: il generatore di righe rifinito riproduce anche copia di colonna, e94, omogeneità e formule

- **Metodo.** Preregistrato.
  - Generatore e152 (k 3, μ 0,5) con tre aggiunte:
    - tema più debole: candidate dal tema con probabilità θ, altrimenti dalla pagina;
    - tema che passa alla riga dopo con probabilità c;
    - ch/sh favoriti ×2 in seconda posizione.
  - θ ∈ {0,3; 0,6} × c ∈ {0; 0,5}.
- **Risultati.** Con θ = 0,3, la riga è riprodotta in tutte le combinazioni, e in più:
  - pagella 10/18 e riga e pagina **9/12** (e152: 5–6);
  - copia della prima e della seconda colonna 0,93 / 1,48 (Voynich 1,03 / 1,47);
  - e94 1,44 (Voynich 1,43);
  - omogeneità 0,036 (circa 0,04);
  - formule 2,7 nella banda.
  - **Mancano:** h2, tipi/parole (0,27 contro 0,19), Zipf, unioni, legame (giunture), gradiente,
    verticale, bordo di riga. "Completo" no: serve una pagella ≥ 12.
  - Con θ = 0,6 il tema è troppo forte (formule 12,5).
- **Esito per regola:** riga riprodotta sì, completo no, quindi nessun modello di riferimento.
- **Lettura.**
  - È il modello senza messaggio più vicino al Voynich prodotto finora: riproduce tutte le proprietà
    di riga e quasi tutte quelle di pagina che riguardano la composizione della riga.
  - Ciò che manca riguarda la **forma delle parole e delle giunture**: le varianti generate
    (generatori.Modifiche) creano troppi tipi nuovi e alzano h2, e le giunture non hanno la forza del
    Voynich.
  - Il passo successivo, se lo si vuole completo, è un generatore di parole migliore, non un altro
    meccanismo di riga.

## 2/10/2026 — e160: sotto l'involucro di riga non riemerge un codice a parole (solo un debole ordine)

- **Metodo.** Preregistrato. Primo tentativo di decifrazione a parole.
  - L'involucro tolto: segno d'inizio y/d/s; cinque scelte di grafia; ee/aiin.
  - Misure: T1 ordine delle parole frequenti, T2 accordo a distanza, T3 accordo nella riga, T4
    informazione fra parole adiacenti.
  - Controllo positivo: latino cifrato parola per parola, a cui si aggiunge lo stesso involucro.
- **Risultati** (z, nell'ordine T1, T2, T3, T4):

  | testo | T1 | T2 | T3 | T4 |
  |---|---|---|---|---|
  | controllo, tetto (senza involucro) | 6,1 | 5,6 | 3,1 | 48,8 |
  | controllo con involucro | 3,9 | 3,1 | 4,2 | −4,3 |
  | controllo ripulito | 4,3 | 4,3 | 2,1 | **27,9** |
  | Voynich grezzo | 0,6 | 0,1 | −0,5 | −18,6 |
  | Voynich ripulito | 3,6 | −0,2 | −2,8 | −4,0 |

- **Validità: sì.** L'involucro cancella la struttura del controllo (T4 da 48,8 a −4,3), e la pulizia la
  fa riemergere (27,9).
- **Esito: struttura riemersa nel Voynich no.** T4 resta negativo, nessun accordo.
- **Lettura.**
  - Se sotto il Voynich ci fosse un testo cifrato parola per parola, nascosto dall'involucro di riga
    che conosciamo, la pulizia lo farebbe riemergere, come succede con il latino. Non succede.
  - Un debole ordine delle parole frequenti compare dopo la pulizia (T1 da 0,6 a 3,6). È sotto la
    soglia e senza legami fra parole vicine: probabilmente un effetto delle giunture, non della
    sintassi.
  - Nel Voynich le parole adiacenti sono **meno** legate del caso (T4 −18,6), in accordo con A > 1
    (e110): due parole vicine si evitano più di due parole a distanza 2.

## 2/10/2026 — e155: le righe hanno un tema debole ma reale (sotto la soglia preregistrata)

- **Metodo.** Preregistrato.
  - Copertura delle 1–2 famiglie di varianti più grandi nella riga (distanza ≤ 0,25), contro il
    rimescolamento delle parole fra righe della stessa pagina.
- **Risultati:**
  - **Voynich:** C1 0,230 contro 0,217 (×1,06, z 10,9); C2 ×1,05 (z 13,0);
  - **generatore e152:** ×2,39 (z 236), controllo valido;
  - **Timm e Schinner:** ×0,99 (z −1,8);
  - **latino:** ×0,96 (z −8,8).
- **Esito per regola: righe a tema no** (z alto, ma rapporto sotto 1,1).
- **Lettura.**
  - Le parole di una riga del Voynich si raccolgono in famiglie di varianti un po' più del vocabolario
    della pagina. L'effetto è piccolo ma netto, e non c'è né in Timm e Schinner né nel latino.
  - È molto più debole del generatore e152 (tema forte), coerente con l'e153 (θ = 0,3 va meglio di
    θ = 0,6).
  - Un tema di riga debole non regge l'estrazione di un "tema dominante" per riga: la strada 5
    (sequenza dei temi come voci) non si apre, per ora.

## 2/10/2026 — Hannig, Ardıç, Cheshire: chiavi non verificabili come chiavi fisse

- **Hannig (2020, ebraico)**, PDF dal suo sito (`dati/cache/letture_proposte/hannig_2020.pdf`, SHA-256
  86fa8e75…; tabella a p. 15 letta come immagine):
  - **22 corrispondenze su 34 segni ebraici.** I quattro segni a gamba del Voynich, con e senza
    panca, coprono 12 consonanti (B/b, G/g, D/d, P/p, K/k, T/t). Nella tabella le righe B, G e D
    hanno lo stesso segno, come b, g e d: lo stesso segno vale fino a tre lettere.
  - Mancano ancora 12 lettere (w, z, ḥ, m, n, s, ṣ, ś, š e quattro finali).
  - **Una chiave così non è fissa:** ogni parola ha molte letture, e in un ebraico senza vocali
    quasi tutte trovano una parola. Il test con chiavi casuali non discriminerebbe.
  - L'e158 mostra inoltre che l'affinità del Voynich con le lingue semitiche nasce dalla forma delle
    parole, anche in un testo senza messaggio.
  - **Non verificabile come chiave, e l'argomento linguistico che la motiva è smentito dall'e158.**
- **Ardıç (antico turco)**, articolo (`ardic_turkic.pdf`, SHA-256 5ead8ec5…): i segni del Voynich sono
  in un font proprio, che il testo estratto non conserva, e l'alfabeto dichiarato ha "24 lettere e
  90+ lettere composte". Da verificare con la tabella resa come immagine. Rimandato.
- **Cheshire (2019, "proto-romanzo")**: il PDF dell'articolo (Romance Studies 37:1) non è
  raggiungibile da qui (403, non in archivio). Rimandato.

## 2/10/2026 — Ardıç e Cheshire: esito della verifica delle chiavi

- **Ardıç**: la fig. 1b (p. 10), resa come immagine, dà l'alfabeto.
  - Diversi segni hanno **più suoni**, e ci sono 90 e più "lettere composte".
  - La corrispondenza fra i segni disegnati e l'EVA è incerta già a vista, per i segni piccoli e
    simili fra loro.
  - **Non è una chiave fissa verificabile:** come per Hannig, ogni parola ha molte letture. Chiuso.
- **Cheshire**: il PDF dell'accettato (Bristol) si è trovato nell'archivio web (istantanea
  20230531091812; SHA-256 7cffdecd…, in FONTI).
  - **Una chiave fissa c'è:** la tabella "Symbol-Italic key" (fig. 12).
  - **Traduzione in EVA:** dai disegni, confermata allineando le sue letture di f53r (righe 1–6) con la
    ZL. Per esempio `kodam chocthody oty` → "la nasa éo eme ona o'ma" e `qokod` → "dolon".
  - **Il resto del metodo è libero:** risegmenta le parole a piacere e cerca ogni pezzo in nove lingue
    romanze più il basco, con abbreviazioni (o'ma = "o'mater").
  - Quindi: **e163**, chiave contro chiavi casuali della stessa forma.
- **Errore di esecuzione nell'e163, corretto:** la pagina `fRos` (le rosette) non ha numero di foglio e
  faceva fallire il filtro delle pagine. È esclusa, come già detto nella preregistrazione (f67–f86).
  Commit a parte.

## 2/10/2026 — e163: la chiave di Cheshire batte le chiavi casuali, ma solo in parte

- **Metodo.** Preregistrato.
  - **Lessico:** l'unione dei vocabolari biblici di latino, italiano, portoghese, rumeno, spagnolo,
    francese e basco.
  - **Testo:** il Voynich fuori campione, cioè senza le pagine che lui traduce; 24.894 parole.
  - **Nullo:** chiavi casuali con la stessa forma, uscite rimescolate fra vocali e fra consonanti.
  - **Misure:** M1 per le parole intere, M2 per le parole risegmentabili.
- **Risultati:**

  | testo | M1 Cheshire | M1 casuali (mediana / 99°) | M2 Cheshire | M2 casuali (mediana / 99°) |
  |---|---|---|---|---|
  | controllo: italiano vero, scritto con l'inverso della chiave | 0,684 | 0,253 / 0,358 | 0,765 | 0,488 / 0,684 |
  | Voynich fuori campione | **0,234** | 0,113 / 0,197 (p 0,0015) | **0,594** | 0,429 / 0,627 (p 0,03) |

- **Controllo valido.** **Esito per regola: incerto.** M1 è sopra il 99° percentile, M2 fra il 95° e il
  99°.
- **Analisi esplorativa, non preregistrata.**
  - Il vantaggio viene da poche parole frequenti: le prime 15 fanno il 54% dei riscontri. Per esempio
    `daiin`→"naus", `ol`→"or", `ar`→"as", `or`→"os", `dar`→"nas", `chor`→"eos", `qokol`→"dolor".
  - Sulle parole lette di 3–4 lettere la chiave resta sopra tutte le chiavi casuali (≥ 4 lettere:
    0,102 contro 0,017 di mediana). Da 5 lettere in su il vantaggio sparisce (0,017 contro un 99°
    percentile di 0,030).
- **Lettura.**
  - Una chiave **scelta guardando il manoscritto** fa leggere come parole le parole frequenti e corte:
    è ciò che ci si aspetta da una chiave adattata, non necessariamente da una chiave giusta.
  - Il nullo preregistrato (chiavi casuali) non tiene conto dell'adattamento. Anche la scelta "fuori
    campione" non basta, perché Cheshire conosceva tutto il manoscritto.
  - Il confronto giusto è con chiavi **ottimizzate** allo stesso modo: e163b.
  - Sul controllo italiano la chiave vera arriva a 0,68. Sul Voynich Cheshire arriva a 0,23, e le
    parole lunghe non tornano.

## 2/10/2026 — e162: un messaggio nei temi di riga è invisibile ai test di struttura, ma rompe la pagina

- **Metodo.** Preregistrato.
  - Generatore e153 con i temi di riga presi da un flusso di latino codificato parola per parola (3
    parole per riga), contro temi a caso dalla pagina.
  - Tre semi.
- **Risultati:**

  | generatore | pagella | S(1) | A | scelte | r | T3 grezzo | T4 grezzo | T3 ripulito | T4 ripulito |
  |---|---|---|---|---|---|---|---|---|---|
  | temi dal messaggio | 4/18 | 0,60 | 1,009 | 5 | 0,158 | 6,9 | −4,0 | 4,9 | 8,4 |
  | temi a caso (e153) | 10/18 | 0,66 | 1,011 | 5 | 0,169 | 5,0 | −8,5 | 3,0 | 6,3 |

- **Esito per regola:**
  - **(a) Riga riprodotta col messaggio: sì.**
  - **(b) Messaggio visibile ai test di struttura: no.** Nessuna misura supera di 3 il riferimento; la
    più vicina è T4 ripulito, +2,1.
- **Lettura.**
  - **Le regole di riga e i test di struttura dell'e160** non escludono un messaggio nascosto così:
    l'involucro di riga e la scelta a caso fra tema e pagina (θ 0,3) lo diluiscono troppo.
  - **Però, non preregistrato:** col messaggio la pagella scende da 10 a 4 su 18. Cadono omogeneità,
    curva piatta, deriva, profilo di pagina, lunghezze vicine e formule. Un flusso di testo che corre
    da una pagina all'altra toglie alle pagine il loro vocabolario proprio, che invece il Voynich ha.
  - Un messaggio nei temi sarebbe compatibile solo se **il testo in chiaro cambiasse argomento
    pagina per pagina**, come un erbario con una pianta per pagina.
  - **Prossimo test (e162b):** temi da un testo latino a voci, una voce per pagina. Si guarda se
    torna la pagella e se il messaggio resta invisibile.

## 2/10/2026 — e157: le abitudini di grafia non riconoscono un cambio di scriba (metodo non valido)

- **Metodo.** Preregistrato.
  - Salto massimo delle cinque preferenze di grafia fra due blocchi di righe della pagina, contro 500
    rimescolamenti delle righe.
  - Taratura su pagine cucite (7 + 7 righe).
- **Taratura:** cuciture fra **mani diverse** rilevate nell'**8%** dei casi, fra **stessa mano** nel 10%.
  - **Metodo valido: no.** Servivano almeno il 50%, e il doppio della stessa mano.
- **Lettura.**
  - Le preferenze di grafia riga per riga sono quasi tutte variazione **dentro** la mano: il salto
    fra due pagine della stessa mano è grande quanto quello fra due mani.
  - Concorda con l'e130 (gli andamenti di riga sono condivisi dalle mani) e con l'e146 (ripartenza a
    ogni pagina).
  - Le 7 pagine vere con p < 0,01 (f1r, f3r, f31r, f36v, f83r, f107v, f114v; f115r no, p 0,23) **non si
    interpretano** come cambi di scriba.
  - Tre hanno il taglio a 4 righe dalla fine di pagine lunghe (f83r, f107v, f114v): forse un effetto
    di fine pagina, da non leggere oltre.
- **Strada 3 (cambi di scriba): chiusa** con questi strumenti. Per le mani resta la paleografia (Davis).

## 2/10/2026 — e161: il passo di riga conferma debolmente l'ordine ricostruito; il colore dell'inchiostro segue la rilegatura

- **Metodo.** Preregistrato.
  - **(III) Inchiostro:** tinta, saturazione e scuro dalle immagini IIIF.
  - **(IV) Passo di riga:** distanza fra righe divisa per l'altezza delle parole, dai riquadri di
    voynichese.com.
  - Per ciascuno, distanza fra bifogli consecutivi nell'ordine ricostruito dal vocabolario (e154b)
    e in quello di rilegatura, contro 1.000 ordini casuali.
  - Gruppi di stessa mano e lingua: 1/A con 27 unità, 2/B con 11, 3/B con 7.
- **Risultati:**

  | caratteristiche | ricostruito (p) | rilegatura (p) | casuali |
  |---|---|---|---|
  | (III) inchiostro | 2,299 (0,618) | **1,955 (0,006)** | 2,263 |
  | (IV) passo di riga | **1,034 (0,039)** | 1,247 (0,664) | 1,202 |

- **Esito per regola: conferma fisica sì**, dal passo di riga.
- **Cautele.**
  - **Due misure provate:** con la correzione per due confronti (soglia 0,025) il passo di riga **non**
    passerebbe. È una conferma debole.
  - **Il colore dell'inchiostro è graduale nell'ordine di rilegatura,** non in quello ricostruito. È
    il confondimento dichiarato nella preregistrazione: le fotografie fatte in ordine di rilegatura
    cambiano luce e colore gradualmente. Il colore misurato dalle fotografie dunque non serve a datare
    la scrittura.
  - Il passo di riga è un rapporto (distanza fra righe su altezza delle parole), quindi non dipende
    dalla scala né dalla luce. È una proprietà della scrittura: rigatura e mano.
- **Lettura.**
  - L'unica misura fisica non viziata dalle fotografie va nella direzione dell'ordine ricostruito, e
    non va in quella della rilegatura.
  - Insieme all'e154b (abitudini di grafia), l'ordine ricostruito ha **due conferme indipendenti dal
    vocabolario**: una forte (grafia) e una debole (passo di riga).
  - Non basta a proporre l'ordine come certo. Basta a riportarlo nel white paper come ipotesi
    sostenuta.

## 2/10/2026 — e164: il legame alle giunture non è un effetto di posizione (contro l'obiezione di Feaster)

- **Perché.** Feaster (Malta 2022, paper12 §5) propone che le combinazioni anomale alle giunture di
  Smith e Ponzi nascano dalla posizione delle parole nella riga e nel paragrafo. L'e74 non aveva un
  nullo per strati di posizione.
- **Metodo.** Preregistrato.
  - Eccesso d'informazione mutua fra ultimo e primo segno di parole interne adiacenti.
  - Tre nulli:
    - **N0**, fra tutte le coppie;
    - **N1**, nello stesso strato di posizione nella riga;
    - **N2**, che aggiunge la riga nel paragrafo e la sezione.
- **Risultati:**

  | testo | N0 | N2 | ritenzione N2 |
  |---|---|---|---|
  | Voynich | 0,1997 (z 252) | 0,1970 (z 216) | **0,99** |
  | Plinio a capo (controllo lingua) | 0,0412 | 0,0413 | 1,00 |
  | solo posizione (Voynich rimescolato negli strati) | 0,0026 | 0,0001 | 0,05 |

- **Validità: sì. Esito: legame alle giunture vero.** La sola posizione produce l'1% del legame del
  Voynich.
- **Lettura.**
  - Le preferenze di posizione esistono (Feaster), ma non spiegano il legame fra parole adiacenti: è
    un legame fra parola e parola.
  - **Il punto 1 della rassegna regge:** il legame è vero dentro la riga e sparisce all'a capo (e74).
  - Feaster può avere ragione su combinazioni singole come y.q e n.q. Sul legame complessivo no.
- **Rassegna.** Nello stesso thread di Voynich Day (4343) Feaster aveva provato informalmente le
  combinazioni all'a capo e trovato due anomalie singole (m→q 58%, n→Sh 140%), che poi attribuiva a
  differenze di sezione. La misura complessiva (R ≈ 0) e il confronto con Plinio restano nostri.

## 2/10/2026 — e162b: un messaggio a voci, una per pagina, non rende la pagina e si vede (T3)

- **Metodo.** Preregistrato.
  - Come l'e162, ma i temi di riga vengono dal paragrafo di Isidoro, *Etymologiae* XVII (326
    paragrafi, codificati parola per parola) assegnato alla pagina.
  - Le parole del paragrafo si usano in ordine e ciclicamente.
- **Risultati:**

  | generatore | pagella | T3 grezzo | T3 ripulito | T4 ripulito |
  |---|---|---|---|---|
  | temi da voci, una per pagina | 5/18 | **8,0** | **6,5** | 8,2 |
  | flusso continuo (e162) | 4/18 | 6,9 | 4,9 | 8,4 |
  | temi a caso (e153) | 10/18 | 5,0 | 3,0 | 6,3 |
  | Voynich (e160) | – | −0,5 | −2,8 | −4,0 |

- **Esito per regola:**
  - **(a) Pagina recuperata: no.** La pagella è 5/18. Cadono omogeneità, profilo di pagina, curva
    piatta, lunghezze vicine e formule.
  - **(b) Messaggio visibile: sì,** al limite. T3 grezzo supera il riferimento di 3,0, T3 ripulito di
    3,5.
- **Lettura.**
  - Un messaggio nascosto nei temi non riproduce le proprietà di pagina del Voynich, nemmeno con un
    testo a voci. Quando è organizzato per pagina, alza l'accordo nella composizione della riga (T3),
    che nel Voynich è nullo o negativo.
  - **L'ipotesi "messaggio nei temi" si indebolisce** (lettura preregistrata (a) no).
- **Nota sul generatore, non preregistrata.**
  - Anche l'e153 con temi a caso ha T3 5,0 contro il −0,5 del Voynich, e T4 ripulito 6,3 contro −4,0.
    Il tema di riga, pur debole, crea più accordo nella riga di quanto ne abbia il Voynich.
  - Sono due proprietà da aggiungere alla lista di ciò che il generatore non riproduce. Vanno
    guardate insieme al tema di riga debole misurato nell'e155 (×1,06).

## 2/10/2026 — e163b: qualsiasi chiave adattata legge "romanzo" meglio di quella di Cheshire

- **Metodo.** Preregistrato.
  - 20 chiavi della stessa forma di quella di Cheshire, ottimizzate con 3.000 scambi sui fogli
    dispari e misurate sui pari.
  - Controllo: italiano scritto con l'inverso della chiave.
- **Risultati** (M1 = quota di parole lette come parole del lessico, in verifica):

  | testo | Cheshire | ottimizzate (mediana / max) | Cheshire ≥ 4 lettere | ottimizzate ≥ 4 (mediana / max) |
  |---|---|---|---|---|
  | controllo italiano (chiave vera) | 0,686 | 0,503 / 0,690 | 0,503 | 0,187 / 0,509 |
  | Voynich | **0,233** | **0,345 / 0,374** | 0,100 | 0,137 / 0,175 |

- **Validità: sì.** Nel controllo l'ottimizzazione ritrova chiavi buone quanto quella vera.
- **Esito per regola: vantaggio spiegato dall'adattamento.** Tutte le 20 chiavi ottimizzate, la
  peggiore a 0,292, battono quella di Cheshire, anche sulle parole lunghe.
- **Lettura.**
  - La chiave di Cheshire legge come parole romanze più parole del caso perché è adattata alle parole
    frequenti del manoscritto. Una qualsiasi chiave adattata in pochi minuti fa meglio, anche su
    pagine non usate per adattarla.
  - Nel controllo la chiave vera è il massimo e l'ottimizzazione la raggiunge appena (0,69). Sul
    Voynich nessuna chiave si avvicina a quel livello.
  - **Cheshire chiuso:** stessa conclusione di Bax (e133). Una chiave che lascia libera la ricerca
    in nove lingue produce "letture" per costruzione.

## 2/10/2026 — Ordine ricostruito dei bifogli: tabella descrittiva, e perché non aggiungo un test "a lunga distanza"

- **Fatto.** `analisi/ricostruzione_bifogli.py` scrive `risultati/ricostruzione_bifogli.md`: l'ordine
  ricostruito (procedimento dell'e154b) per i tre gruppi di mano e lingua, con sezione, rango nella
  rilegatura e somiglianza con l'unità successiva. È descrittivo e il verso non è determinato.
- **Prove che sostengono l'ordine:**
  - e148: i fogli coniugati si somigliano;
  - e150 ed e150b: l'ordine si ricostruisce su dati non usati;
  - e154b: le abitudini di grafia confermano l'ordine (forte, p < 0,001);
  - e161: lo conferma anche il passo di riga (debole, p 0,039, non regge la correzione per due misure).
- **Scartato:** un test di "deriva a lunga distanza" nell'ordine ricostruito. Un percorso costruito
  cercando vicini simili produce comunque differenze che crescono con la distanza, anche senza una
  vera cronologia, perché vocabolario e grafia sono correlati. Il test non distinguerebbe niente.
  Servono conferme indipendenti dal vocabolario, come la grafia e la fisica.
- **Lettura della tabella** (descrittiva):
  - nel gruppo 1/A le unità farmaceutiche (f88–f102) finiscono vicine fra loro e accanto a f87–f90 e
    f93–f96, erbario di fascicoli tardi;
  - nel gruppo 2/B le unità balneologiche (f75–f84) formano un blocco compatto, con somiglianze
    0,85–0,95.

## 2/10/2026 — e165: varianti solo fra parole attestate correggono h2 e tipi, ma perdono altro

- **Metodo.** Preregistrato. Generatore e153 con varianti {Modifiche, attestate} × λ {1, 2}, tre semi.
- **Risultati:**

  | varianti, λ | pagella | riga | guadagnate | perse |
  |---|---|---|---|---|
  | Modifiche, λ 1 (e153) | 10/18 | sì | – | – |
  | Modifiche, λ 2 | 10/18 | sì | – | – |
  | attestate, λ 1 | 9/18 | sì | h2, tipi | uniche, curva piatta, formule |
  | attestate, λ 2 | 10/18 | sì | h2, tipi | uniche, curva piatta |

- **Esito per regola: completo no** (serviva ≥ 12/18).
- **Lettura.**
  - Le varianti fra parole già attestate portano h2 (2,32) e tipi/parole nella banda del Voynich: la
    diagnosi dell'e153 era giusta.
  - Però riducono le parole uniche, che il Voynich ha in abbondanza (68%): il Voynich **crea** parole
    nuove, ma senza alzare h2.
  - Giunture più forti (λ 2) non cambiano la pagella.
  - **Il compromesso da trovare:** parole nuove che restino "dentro le regole di formazione" del
    Voynich. Serve un generatore di parole basato sulla struttura a posizioni (Zattera 2022, 12
    "slot"; Stolfi), non sulle modifiche casuali.

## 2/10/2026 — e166: l'inchiostro mostra le intinte, ma le scelte di grafia non cambiano con l'inchiostro

- **Dati.** Immagini "large" di voynichese.com, già nella cornice dei riquadri delle parole (FONTI).
  Allineamento perfetto, verificato a vista su f103r. 177 pagine e 23.680 parole misurate.
- **Validità: sì.**
  - **V1:** lo scuro delle parole consecutive è correlato (r 0,33 contro −0,01 rimescolato, z 44,5).
  - **V2:** gli scurimenti sono bruschi e gli schiarimenti graduali, la firma delle intinte (skewness
    +0,23, p 0,0005).
- **H1, descrittivo:** le intinte cadono più spesso sulla prima parola della riga (19,6%) che sulle
  altre (14,4%). Lo scriba tende a intingere all'inizio della riga, ma non sempre.
- **H2, test principale:** il cambio delle scelte di grafia fra righe consecutive non è maggiore
  quando la seconda riga comincia con un'intinta. Differenza −0,0003, p 0,67, su 3.028 coppie di cui
  968 con intinta.
- **Esito: nessun legame.**
- **Lettura.** Le scelte di grafia riga per riga non sono un effetto della carica di penna: restano
  una convenzione legata alla riga in quanto tale. La misura dell'inchiostro funziona, quindi è uno
  strumento nuovo per altre domande, per esempio la velocità di scrittura o l'ordine delle pagine.

## 2/10/2026 — e167: *Polygraphia III* (Hermes) non ha il legame fra parole vicine

- **Metodo.** Preregistrato. I tre cifrati pubblicati da Hermes, mandati a capo con le larghezze del
  Voynich, a lettere singole.
- **Risultati:**

  | testo | (a) legame alle giunture (z) | (b) A | (c) ripetizione immediata / attesa |
  |---|---|---|---|
  | Voynich (lettere EVA) | 0,192 (309) | 1,054 | 1,01 |
  | Plinio a capo | 0,041 (52) | 1,002 | 0,12 |
  | PIII 10 colonne | 0,0002 (1) | 1,012 | 0,56 |
  | PIII 24 colonne | −0,0001 (0) | 1,017 | 0,51 |
  | PIII tutte le colonne | 0,0004 (1) | 1,005 | 0,35 |

- **Esito per regola: compatibile no.** Nessuna variante riproduce (a) né (b).
- **Lettura.**
  - Come previsto dalla costruzione, nel cifrario di Tritemio la fine di una parola (che codifica la
    lettera) e l'inizio della seguente (radice scelta a caso) sono indipendenti. Il Voynich ha invece
    il legame più forte fra tutti i testi misurati: cinque volte Plinio.
  - Anche l'alternanza A (parole adiacenti più diverse di quelle a distanza 2) manca.
  - *Polygraphia III* imita le statistiche dentro la parola, non quelle fra parole. Come Naibbe ed
    e134, non produce il Voynich senza un meccanismo in più.

## 2/10/2026 — Nota d'ordine sui commit dell'e169

Due comandi git partiti insieme si sono bloccati a vicenda (index.lock). Il codice
`esperimenti/e169_tema_e_vicini.py` è così entrato nel commit 50b235d, insieme ai risultati di e165–e167,
invece che in un commit a parte. L'ordine resta valido: la preregistrazione e169 è nel commit
precedente fdd73dc, e l'e169 è partito solo dopo 50b235d. D'ora in poi i comandi git vanno sempre in
sequenza.

## 2/10/2026 — e170: lo scuro dell'inchiostro è graduale in entrambi gli ordini (nessuna conferma)

- **Metodo.** Preregistrato.
  - Per unità: scuro medio, quota di intinte e autocorrelazione dello scuro (e166).
  - Ordine ricostruito (e154b) contro rilegatura e 1.000 ordini casuali; 49 unità in tre gruppi.
- **Risultati** (distanza fra unità consecutive):

  | ordine | distanza | p |
  |---|---|---|
  | ricostruito | 2,080 | 0,015 |
  | rilegatura | 2,035 | 0,004 |
  | casuali (media) | 2,318 | – |

- **Esito per regola: conferma fisica no.** L'ordine ricostruito è più graduale del caso, ma non della
  rilegatura.
- **Lettura.**
  - Entrambi gli ordini sono più graduali del caso, quindi lo scuro dell'inchiostro porta un segnale
    di vicinanza.
  - Per la rilegatura può essere il confondimento dichiarato, cioè le riprese fotografiche in ordine
    di rilegatura, anche se la misura è normalizzata sulla pergamena locale. Oppure la rilegatura
    conserva in parte l'ordine di scrittura: i fascicoli tengono insieme bifogli scritti vicini.
  - I due ordini condividono molte adiacenze dentro i fascicoli, quindi il test non li separa bene.
  - Le conferme dell'ordine ricostruito restano la grafia (e154b, forte) e il passo di riga (e161,
    debole).

## 2/10/2026 — e171: un'intinta a metà riga non spezza il legame fra parole vicine

- **Metodo.** Preregistrato.
  - Eccesso d'informazione mutua alle giunture per le coppie di parole interne in cui la seconda è
    un'intinta (e166), contro le coppie senza intinta sottocampionate alla stessa numerosità.
  - 1.799 coppie con intinta, 11.194 senza.
- **Risultati:**
  - eccesso con intinta 0,158 bit (z 25), senza 0,210, quindi Rint 0,75;
  - intervallo bootstrap [0,80; 1,10];
  - parole che iniziano con y, d o s: 13,0% fra le intinte, 12,1% fra le altre.
- **Esito per regola: nessun effetto** (l'intervallo contiene 1).
- **Cautela di metodo, non preregistrata:** la stima centrale (0,75) cade fuori dall'intervallo. Il
  bootstrap con ripetizione gonfia l'informazione mutua (coppie duplicate), quindi l'intervallo è
  spostato verso l'alto. Una lettura prudente è "al più un indebolimento parziale, intorno al 25%".
- **Lettura.**
  - Dopo un'intinta il legame con la parola precedente resta forte (z 25), molto lontano dallo zero
    dell'a capo (R 0,01, e74). Anche i segni d'inizio riga non compaiono più spesso.
  - **La chiusura della riga non è un effetto delle pause di scrittura:** riguarda la riga in quanto
    tale.
  - Insieme all'e166 (scelte di grafia indipendenti dalle intinte), la riga del Voynich risulta
    un'unità **di composizione**, non del gesto fisico.

## 2/10/2026 — e173: dimensione della scrittura e scelte di grafia, correlazione piccola ma confusa

- **Metodo.** Preregistrato.
  - Dimensione della riga: larghezza dei riquadri per unità EVA, mediana per riga, normalizzata sulla
    pagina.
  - Correlazione fra |Δ dimensione| e cambio di scelta fra righe consecutive.
- **Validità: sì.** La dimensione ha struttura fra righe consecutive (r 0,27 contro −0,01, z 11,4).
- **Risultato:** Spearman 0,083, p 0,001 su 3.045 coppie. Esito per regola: "le scelte seguono la
  dimensione".
- **Controllo esplorativo, non preregistrato:** c'è un confondimento.
  - Entrambi i cambi diminuiscono con il numero di parole della riga più corta (Spearman −0,17 e −0,16),
    perché le righe corte danno misure rumorose.
  - Dentro le classi di lunghezza le correlazioni sono 0,11, −0,04, 0,095 e 0,061.
- **Lettura sospesa:** l'esito per regola non si accetta finché non lo conferma l'e173b, preregistrato
  con il nullo dentro le classi di lunghezza.

## 2/10/2026 — e173b: le scelte di grafia cambiano un po' di più dove cambia la dimensione della scrittura

- **Metodo.** Preregistrato.
  - Come l'e173, ma correlazione dentro classi di lunghezza della riga più corta (< 7, 7–8, 9–10,
    ≥ 11 parole).
  - Due nulli: rimescolamento dentro la classe, e dentro pagina × classe.
- **Risultati:**
  - statistica pesata 0,062;
  - p 0,001 dentro le classi (nullo −0,001), p 0,0005 dentro pagina × classe (nullo 0,008);
  - per classe: 0,11, −0,04, 0,095 e 0,061.
- **Esito per regola: le scelte seguono la dimensione.**
- **Lettura.**
  - Fra righe consecutive, quando la scrittura cambia dimensione le scelte di grafia (ch/sh, k/t,
    -l/-r, qo-/o-, -dy/-ey) cambiano un po' di più. L'effetto è **piccolo** (ρ ≈ 0,06) ma regge al
    confondimento della lunghezza e al nullo per pagina.
  - Le scelte non seguono le intinte (e166) ma seguono, debolmente, la dimensione della scrittura:
    qualcosa che cambia lo "stato" della mano (penna rifatta, ripresa dopo una pausa, cambio di
    postura) cambia anche le preferenze.
  - **Cautela:** una classe (7–8 parole) va nel verso opposto, e altri confondimenti non sono
    esclusi, per esempio errori di allineamento dei riquadri sulle righe difficili. Da replicare
    con un'altra misura di dimensione, come l'altezza dei segni senza aste.
- **Possibile seguito:** le "sessioni" di scrittura riconosciute da salti di dimensione spiegano le
  scelte meglio della riga?

## 2/10/2026 — e169: tema più debole ed evitamento abbassano T3, ma T4 resta positivo e la pagina si perde

- **Metodo.** Preregistrato. Generatore e153 con θ {0; 0,15; 0,3} × β {1; 0,5}, tre semi.
- **Risultati** (Voynich: T3 grezzo −0,5, T4 ripulito −4,0):

  | θ, β | pagella | A | T3 grezzo | T4 ripulito | perse rispetto a θ 0,3 β 1 |
  |---|---|---|---|---|---|
  | 0, 1 | 8/18 | 1,013 | 1,7 | 7,7 | omogeneità, lunghezze vicine |
  | 0, 0,5 | 6/18 | 1,043 | 0,9 | 4,8 | ripetizione, omogeneità, curva piatta, lunghezze vicine |
  | 0,15, 1 | 7/18 | 1,009 | 3,2 | 6,4 | omogeneità, lunghezze vicine |
  | 0,15, 0,5 | 6/18 | 1,051 | 0,6 | 5,6 | ripetizione, omogeneità, lunghezze vicine |
  | 0,3, 1 | 9/18 | 1,012 | 5,0 | 6,5 | – |
  | 0,3, 0,5 | 7/18 | 1,061 | 5,4 | 5,0 | ripetizione, lunghezze vicine |

- **Esito per regola: nessuna combinazione corregge l'accordo.** T4 ripulito resta positivo ovunque.
- **Lettura.**
  - **Il tema di riga è un compromesso.** Serve alle proprietà di pagina (omogeneità, lunghezze
    vicine): senza tema si perdono. Ma alza l'accordo nella riga (T3), che nel Voynich è nullo. Con
    θ 0 o con l'evitamento (β 0,5) T3 scende vicino al Voynich, a prezzo della pagina.
  - Quindi nel Voynich l'omogeneità di pagina **non** viene da parole ripetute dentro la riga. Viene
    da qualcosa a livello di pagina che non si concentra nelle singole righe, per esempio un
    vocabolario di pagina usato in modo uniforme. È un'indicazione su come rifare il generatore: il
    tema deve essere di pagina, non di riga.
  - **T4 ripulito positivo** (adiacenti più legati del rimescolamento) resta in tutte le versioni,
    mentre il Voynich è negativo. Probabilmente viene dalla scelta per giunture (L^λ) a livello di
    parola intera. È da capire prima di un nuovo tentativo.
  - **Nota tecnica:** θ 0,3 β 1 dà 9/18 contro i 10/18 dell'e153, per un diverso consumo dei numeri
    casuali nel codice (il rinnovo del tema). È nella variabilità fra semi.

## 2/10/2026 — e174: replica con l'altezza della scrittura, non valida per scarsità di dati

- **Metodo.** Preregistrato. L'altezza dei riquadri delle parole fatte solo di segni bassi (a, e, i, n,
  o, r, s, ch, sh, ee), almeno 2 per riga.
- **Risultato:**
  - restano solo 32 pagine e 385 righe;
  - V1 r 0,138, z 3,0 (serviva > 5): **test non valido**;
  - per completezza, la statistica è 0,045 (p 0,28) su 120 coppie.
- **Lettura.** Le parole "tutte basse" sono troppo rare per misurare l'altezza riga per riga. La
  replica dell'e173b resta aperta. Serve un'altezza del corpo della scrittura misurata
  direttamente sulle immagini (profilo d'inchiostro della riga dentro i riquadri), non dai riquadri,
  che includono aste e code.

## 2/10/2026 — e175: replica con il corpo della scrittura, non valida; e un confondimento serio per l'e173b

- **Metodo.** Preregistrato. Altezza della fascia densa del profilo d'inchiostro nei riquadri.
- **Risultato:**
  - 150 pagine, 3.160 righe;
  - V1 r 0,087, z 3,2 (serviva > 5): **non valido**;
  - la statistica è comunque 0,067, p 0,0005, come nell'e173b.
- **Riflessione, non preregistrata.** Una misura con poca struttura fra righe che correla come l'altra
  con il cambio di scelta fa pensare a un **legame meccanico**: le scelte stesse cambiano la geometria
  dei segni.
  - sh ha il pennacchio, t è più largo di k, -dy e -ey differiscono, qo- aggiunge un segno.
  - Se una riga passa a più sh o più t, la sua "dimensione" misurata cambia per questo, non per
    lo stato della mano.
  - L'e173b non escludeva questo confondimento: **la sua lettura va sospesa.**
- **Test giusto (e176):** dimensione misurata solo su parole senza nessuno dei segni coinvolti nelle
  cinque scelte.

## 2/10/2026 — e176: dimensione sulle parole neutre, non valida per scarsità

- **Metodo.** Preregistrato. Larghezza per segno solo sulle parole senza occorrenze delle cinque
  scelte.
- **Risultato:**
  - 44 pagine, 601 righe;
  - V1 r 0,033, z 1,6: **non valido**;
  - per completezza, la statistica è −0,093 (p 0,92).
- **Lettura.** Le parole neutre (daiin, aiin, s…) sono troppo poche. Si passa all'e177, che corregge la
  dimensione di ogni parola per la sua composizione.

## 2/10/2026 — e177: corretta per la composizione, la dimensione della scrittura lega poco con le scelte

- **Metodo.** Preregistrato.
  - Larghezza tipica di ogni unità EVA stimata con NNLS su 30.011 parole allineate.
  - Dimensione di riga = mediana di osservata / attesa.
  - Stesso test dell'e173b.
- **Primo tentativo fermato al salvataggio** (valori numpy nel JSON). Corretto in un commit a parte e
  rieseguito: è deterministico, con valori identici.
- **Risultati:**
  - **V1:** la dimensione corretta ha molta struttura fra righe consecutive (r 0,506, z 11,8, contro
    0,27 della misura grezza);
  - **legame con il cambio di scelta:** 0,032, p 0,036;
  - **la sola composizione** (|Δ larghezza attesa|) dà 0,027.
- **Esito per regola: incerto.**
- **Lettura.**
  - Togliendo l'effetto della composizione delle parole, il legame dell'e173b (0,062) si dimezza e
    non supera più la soglia. **L'effetto dell'e173b era in buona parte meccanico:** le scelte cambiano
    i segni, e i segni la larghezza.
  - **Le scelte di grafia non hanno, per ora, una causa fisica misurabile**: non intinte (e166), non
    dimensione (e177, al più un residuo debole).
  - **Risultato a margine, non preregistrato come ipotesi:** la dimensione della scrittura corretta
    varia **lentamente** lungo la pagina (r 0,51 fra righe consecutive). È un "orologio" della mano
    che si potrebbe usare per l'ordine delle pagine (come il passo di riga nell'e161) e per le mani.

## 2/10/2026 — e178: anche la spaziatura della mano è graduale in entrambi gli ordini

- **Metodo.** Preregistrato. Spaziatura relativa (spazio fra parole / larghezza tipica di un segno,
  corretta per la composizione), che non dipende né dalla scala né dalla luce delle immagini. 52
  unità in tre gruppi.
- **Risultati:**

  | ordine | distanza | p |
  |---|---|---|
  | ricostruito | 0,893 | 0,006 |
  | rilegatura | 0,864 | 0,003 |
  | casuali (media) | 1,143 | – |

- **Esito per regola: conferma no.**
- **Lettura.**
  - Come per lo scuro (e170), entrambi gli ordini sono molto più graduali del caso. Qui non c'è il
    confondimento della ripresa fotografica, quindi **anche la rilegatura conserva vicinanze reali di
    scrittura**: i fascicoli tengono insieme bifogli scritti vicini.
  - Il confronto fra i due ordini ha poca forza perché condividono molte adiacenze.
  - **Test giusto (e179):** solo le adiacenze in cui i due ordini differiscono.

## 2/10/2026 — e179: sulle adiacenze in disaccordo le misure fisiche non scelgono fra i due ordini

- **Metodo.** Preregistrato.
  - Solo le coppie consecutive in uno dei due ordini ma non nell'altro: 31 solo nel ricostruito (R),
    31 solo nella rilegatura (B).
  - Distanza fisica su spaziatura, passo di riga e scuro, standardizzati nel gruppo.
  - 5.000 rimescolamenti delle etichette dentro i gruppi.
- **Risultati:**
  - media B − media R = +0,201, nel verso del ricostruito;
  - p 0,21 per il ricostruito, p 0,80 per la rilegatura;
  - per misura: spaziatura −0,04, passo di riga +0,29, scuro +0,05.
- **Esito per regola: nessuna preferenza.**
- **Lettura.**
  - Con 31 coppie per parte il test ha poca forza. Il verso è quello dell'ordine ricostruito, e viene
    quasi tutto dal passo di riga, come già nell'e161.
  - Le misure fisiche dalle immagini (scuro, spaziatura, passo) dicono che **entrambi** gli ordini
    conservano vicinanze di scrittura (e170, e178), ma non sanno scegliere fra i due.
  - **Stato della ricostruzione per il white paper:**
    - confermata dalla grafia (e154b, forte);
    - debolmente dal passo di riga (e161);
    - non dalle altre misure fisiche (e170, e178, e179).
    
    Va presentata come ipotesi sostenuta dal testo, non dalla fisica.

## 2/10/2026 — e182: il canale delle scelte di grafia potrebbe portare fino a ~49.000 bit

- **Metodo.** Preregistrato, descrittivo.
  - Perdita logaritmica in validazione incrociata (pagine pari/dispari) delle cinque scelte (56.800
    occorrenze circa in 4.118 righe), sotto tre modelli:
    - M0, quota per scelta;
    - M1, più lo strato;
    - M2, più l'abitudine della riga precedente.
- **Risultati:**

  | testo | M0 | M1 | M2 (bit/occorrenza) | bit/riga | bit totali | lettere di latino (compresso / grezzo) |
  |---|---|---|---|---|---|---|
  | Voynich | 0,945 | 0,874 | 0,866 | 11,95 | 49.215 | 24.608 / 12.004 |
  | canale pieno (Bacone) | 0,934 | 0,940 | 0,946 | 12,89 | 53.089 | 26.544 / 12.949 |

- **Lettura.**
  - I modelli di abitudine (posizione, contesto, riga precedente) spiegano poco: restano 0,87 bit per
    scelta, quasi quanto un canale pieno.
  - **Limite superiore:** se un messaggio stesse nelle varianti di grafia, potrebbe essere lungo fino a
    12.000–25.000 lettere, cioè 2.000–5.000 parole latine. Non è poco: un trattatello.
  - Il limite dice solo che lo spazio c'è, non che c'è un messaggio. Se quei bit hanno la struttura di
    un testo, lo dice l'e181 (indice di coincidenza dei gruppi).
  - Un modello delle abitudini migliore abbasserebbe il limite.

## 2/10/2026 — e181: nessun messaggio "baconiano" nelle scelte di grafia

- **Metodo.** Preregistrato.
  - Indice di coincidenza dei gruppi di 5 scelte consecutive (F1, F2, F3, F5, F7, 56.850 occorrenze
    nell'ordine di lettura), massimo sugli sfasamenti.
  - Nullo: rimescolamento dentro riga e scelta, che conserva le abitudini.
  - Controllo: latino nell'alfabeto di Bacon scritto sulle stesse occorrenze.
- **Risultati** (z):

  | testo | L 5 | L 4 | L 6 | L 7 |
  |---|---|---|---|---|
  | Voynich | **0,5** | 1,1 | 1,7 | 2,8 |
  | Bacone puro | 250 | 6,9 | 28 | 41 |
  | Bacone mescolato (70%) | 55 | −3,4 | 3,8 | 3,9 |

- **Validità: sì. Esito per regola: assente.**
- **Lettura.**
  - Le scelte di grafia del Voynich non hanno la firma di un alfabeto a gruppi di 5, nemmeno se il
    messaggio occupasse solo il 70% delle scelte: il test lo vedrebbe con z 55.
  - Insieme all'e182, il canale **avrebbe spazio** per un trattatello, ma la struttura di un testo
    cifrato alla Bacon **non c'è**.
  - Restano fuori codifiche non a blocchi fissi (gruppi di lunghezza variabile, o un bit per riga
    invece che per occorrenza). Da provare solo se c'è un motivo.

## 2/10/2026 — e183: le etichette della farmacia differiscono fra vasi e frammenti, soprattutto in lunghezza

- **Metodo.** Preregistrato.
  - Informazione mutua fra forma dell'etichetta (primo e ultimo segno, lunghezza, o-) e tipo di
    oggetto (codici di locus ZL), dentro la sezione.
  - Nullo: rimescolamento dei tipi dentro la pagina.
  - Contrasti: farmacia Lf 189 / Lc 36; biologica Ln 62 / Lt 47; astronomica Ls 74 / L0 39.
- **Risultati:**
  - **complessivo:** IM 0,810 contro 0,611, z 3,0, p 0,0025;
  - **controllo di potenza:** z 9,1;
  - **per contrasto:** farmacia z 5,9, biologica 1,2, astronomica 0,1;
  - **etichette identiche:** 37 coppie, stesso tipo nel 70% contro 65% atteso.
- **Esito per regola: le etichette dipendono dall'oggetto.** L'effetto viene però solo dalla farmacia.
- **Esplorativo, non preregistrato:**
  - le etichette dei vasi sono più lunghe (81% di 6+ unità contro 43%) e finiscono più spesso in -y;
  - la quota di o- è uguale (53%).
- **Lettura.**
  - In farmacia vasi e frammenti di pianta hanno etichette di forma diversa. Può essere contenuto
    (nomi di preparati più lunghi dei nomi di parti di pianta) o formato (più spazio sui vasi).
    Questo test non distingue le due cose.
  - Ninfe e tubi, stelle e altre etichette: nessuna differenza.
  - Le etichette identiche non si ripetono sullo stesso tipo di oggetto più del caso, cosa che un
    nomenclatore invece farebbe.
  - Va controllato lo spazio disponibile: larghezza dei riquadri delle etichette e lunghezza a parità
    di spazio.

## 2/10/2026 — e184: con misure grezze del disegno, piante simili non hanno vocabolario simile

- **Metodo.** Preregistrato.
  - 122 pagine d'erbario; 3.682 coppie dello stesso gruppo di mano e lingua e di fascicoli diversi.
  - Spearman fra distanza dei disegni (colori e forma fuori dai riquadri delle parole) e distanza di
    vocabolario.
  - Mantel per strati.
- **Risultato:** Spearman −0,010 (nullo −0,001), p 0,53. **Esito per regola: nessun legame.**
- **Limite, non preregistrato.** Un controllo a vista dei numeri (f3r: 81% dei pixel "colorati"
  rosso-bruni) fa pensare che la maschera del colore prenda anche macchie e toni della pergamena, non
  solo il disegno. L'esito vale quindi solo come "non con queste misure".
- **Da migliorare:** misura del disegno con la pergamena tolta localmente (come per l'inchiostro
  nell'e166) e caratteristiche di forma (foglie, radici).

## 2/10/2026 — e172: gli incroci ridanno le parole uniche, ma a prezzo della pagina

- **Metodo.** Preregistrato. Generatore e165 (varianti attestate, λ 1, θ 0,3) con incroci di due
  parole attestate in un segno comune, con probabilità ν ∈ {0; 0,1; 0,25}. Tre semi.
- **Risultati:**

  | ν | pagella | guadagnate rispetto a ν 0 | perse |
  |---|---|---|---|
  | 0 | 9/18 | – | – |
  | 0,1 | 8/18 | formule | profilo pagina, lunghezze vicine |
  | 0,25 | 6/18 | uniche | tipi, omogeneità, profilo pagina, lunghezze vicine |

- **Esito per regola: completo no.**
- **Lettura.**
  - Creare parole nuove per incrocio ridà le parole uniche, ma il vocabolario si allarga troppo: si
    perdono tipi/parole e omogeneità di pagina.
  - Nel Voynich parole nuove e omogeneità convivono. Le parole nuove sono quindi **vicine alle parole
    della stessa pagina** (varianti locali), non incroci qualsiasi del vocabolario.
  - La prossima versione del generatore dovrebbe incrociare solo con parole **della stessa pagina**.

## 2/10/2026 — e180: un tema di pagina tiene la pagina e porta l'accordo nella riga al livello del Voynich

- **Metodo.** Preregistrato. Generatore e153 con tema estratto a inizio pagina e mantenuto per tutta
  la pagina (c = 1), θ {0,3; 0,5} × k {3; 8}. Tre semi.
- **Risultati** (Voynich: T3 grezzo −0,5, T4 ripulito −4,0):

  | θ, k | pagella | T3 grezzo | T4 ripulito | pagina e T3 |
  |---|---|---|---|---|
  | 0,3, 3 | **10/18** | **1,1** | 6,1 | sì |
  | 0,3, 8 | 8/18 | 1,4 | 4,7 | no |
  | 0,5, 3 | 9/18 | 0,8 | 6,5 | sì |
  | 0,5, 8 | **10/18** | **0,9** | 7,0 | sì |

- **Esito per regola:** "corregge l'accordo" no, perché T4 ripulito resta positivo. "Pagina e T3" sì per
  tre combinazioni su quattro.
- **Lettura.**
  - La previsione dell'e169 è confermata: **il tema è di pagina, non di riga.** Con un tema fisso per
    la pagina, la pagella resta a 10/18 come nell'e153 e l'accordo dentro la riga scende da 5,0 a
    circa 1, vicino al Voynich.
  - Un argomento di pagina è compatibile con il Voynich. Un argomento di riga no.
  - **Resta T4 ripulito** (parole adiacenti più legate del caso), da capire.
  - Mancano ancora h2, tipi, legame, unioni, Zipf, verticale, formule e bordo di riga.
- **Nuovo riferimento per il generatore:** e153 con tema di pagina (θ 0,3, k 3).

## 2/10/2026 — e185: le cinque scelte di una riga sono quasi indipendenti, troppo per una "lettera per riga"

- **Metodo.** Preregistrato.
  - Correlazione totale fra i valori di maggioranza delle cinque scelte nella stessa riga (1.088
    righe con tutte e cinque definite).
  - Nullo: permutazioni indipendenti dentro la pagina.
  - Controlli: una lettera di Bacon per riga.
- **Risultati:**

  | testo | TC (bit) | nullo | z |
  |---|---|---|---|
  | Voynich | 0,057 | 0,033 | 3,7 |
  | Bacone, una lettera per riga | 0,710 | 0,024 | 112 |
  | Bacone mescolato (70% delle righe) | 0,306 | 0,022 | 50 |

- **Validità: sì. Esito per regola: incerto** (z fra 2 e 4).
- **Lettura.**
  - C'è una dipendenza piccola fra le scelte della stessa riga, ma l'eccesso è di 0,025 bit:
    - quasi 30 volte meno di un messaggio "una lettera per riga" (0,69);
    - 11 volte meno di un messaggio presente solo nel 70% delle righe.
  - A occhio, una mescolanza di circa il 20% al massimo.
  - È spiegabile con legami meccanici fra scelte nelle stesse parole, per esempio qo- con k/t.
  - **Una lettera per riga, scritta con le cinque scelte, è esclusa** come codifica principale.

## 2/10/2026 — e186: legami fra iniziali e finali di parole vicine, molto più deboli di un messaggio nascosto

- **Metodo.** Preregistrato.
  - 12 regole di estrazione (iniziali o finali di parola con passo 1–4, iniziali o finali di riga,
    seconda parola, iniziale di paragrafo).
  - Legame fra simboli estratti consecutivi contro rimescolamento nella pagina.
  - Confronto con il generatore e180; controlli con latino nascosto.
- **Risultati** (z; eccesso in bit fra parentesi per le regole principali):

  | regola | Voynich | generatore |
  |---|---|---|
  | I1, iniziale di ogni parola | 43,8 (0,048) | 3,8 (0,005) |
  | I2 | 5,8 (0,011) | 0,0 |
  | I3, I4 | 3,1, 2,4 | 1,3, −0,6 |
  | F1, finale di ogni parola | 12,3 (0,009) | 1,6 |
  | F2 | 5,7 (0,007) | 1,4 |
  | F3, F4 | −0,1, −0,4 | – |
  | R1, iniziale di riga | 22,3 (0,110) | 5,5 (0,020) |
  | R2, R3, P1 | 0,8, 1,3, −0,2 | – |
  | controllo latino in I1 | 770 (0,481) | |
  | controllo latino in R1 | 89 (0,501) | |

- **Validità: sì. Candidate per regola:** I1, I2, F1, F2, R1.
- **Lettura, prima di qualsiasi conclusione.**
  - **R1** è l'evitamento dell'inizio fra righe consecutive già noto (e83): le righe evitano di
    cominciare come quella sopra. Il generatore lo imita in forma più debole (z 5,5).
  - **I1, I2, F1, F2:** legami fra parole vicine che decadono con la distanza (passo 1 > passo 2 >
    nulla a passo 3–4), come le regole locali di composizione. In grandezza sono **dieci volte** più
    deboli di un messaggio latino nascosto nelle iniziali (0,048 contro 0,48).
  - **Test decisivo (e186b):** un messaggio nelle iniziali continua attraverso l'a capo. I legami di
    composizione del Voynich si chiudono con la riga (e74).

## 2/10/2026 — e186b: le iniziali si chiudono con la riga; le finali sembrano attraversarla (da verificare)

- **Metodo.** Preregistrato. Legame fra iniziali (I1) e finali (F1) di parole consecutive, dentro la
  riga e attraverso l'a capo. Nullo globale come nell'e74.
- **Risultati:**

  | | dentro la riga | attraverso l'a capo | R |
  |---|---|---|---|
  | Voynich I1 | 0,0785 (z 94) | 0,0130 (z 2,8) | 0,17 |
  | Voynich I1, tolto y/d/s | 0,0785 (z 91) | 0,0132 (z 3,0) | 0,17 |
  | Voynich F1 | 0,0163 (z 23) | 0,0134 (z 4,3) | 0,82 |
  | latino nelle iniziali | 0,481 (z 496) | 0,458 (z 80) | 0,95 |

- **Esito per regola:**
  - **I1: composizione di riga.** Il legame fra iniziali si chiude con la riga. Nessun messaggio
    nelle iniziali.
  - **F1: "messaggio".** Il legame fra finali attraversa l'a capo.
- **Controllo esplorativo, non preregistrato.**
  - Le finali portano due scelte di grafia con abitudini di pagina (-l/-r, -dy/-ey, e146), e il
    nullo dell'e186b è globale.
  - Rimescolando dentro la pagina, l'eccesso attraverso l'a capo scende a 0,007 bit (z 1,8).
- **L'esito "messaggio" per F1 non si accetta prima dell'e186c,** preregistrato con il nullo dentro la
  pagina. In ogni caso la grandezza (0,013 bit) è 35 volte sotto il latino nascosto (0,46).

## 2/10/2026 — e186c: anche le finali si spiegano con le abitudini di pagina; nessun cifrario a nulli

- **Metodo.** Preregistrato. Come l'e186b, con 500 permutazioni dentro la pagina.
- **Risultati:**

  | | dentro la riga | attraverso l'a capo | R |
  |---|---|---|---|
  | Voynich F1 | 0,0089 (z 7) | 0,0066 (z 1,7) | 0,74 |
  | Voynich I1 | 0,0577 (z 33) | 0,0019 (z 0,4) | 0,03 |
  | latino nelle iniziali | 0,480 (z 475) | 0,456 (z 74) | 0,95 |

- **Validità: sì. Esito per regola, F1: abitudini di pagina e riga** (z attraverso l'a capo < 2).
- **Lettura.**
  - A parità di pagina il legame fra finali attraverso l'a capo non è significativo: viene dalle
    abitudini di grafia della pagina (-l/-r, -dy/-ey).
  - Le iniziali si chiudono con la riga (R 0,03).
  - **Conclusione della strada 4:** nessuna delle dodici regole di estrazione (iniziali, finali,
    passi, acrostici di riga e di paragrafo) dà una sequenza con la struttura di un testo. Il latino
    nascosto allo stesso modo darebbe legami 10–50 volte più forti, che attraversano l'a capo.

## 2/10/2026 — e187: vasi e frammenti differiscono solo nella lunghezza dell'etichetta

- **Metodo.** Preregistrato. Informazione mutua fra tipo di oggetto e forma dell'etichetta (primo
  segno, ultimo segno, o-), condizionata alla classe di lunghezza. Nullo dentro pagina × classe.
- **Risultati:**

  | contrasto | n | IM condizionata | nullo | z | p |
  |---|---|---|---|---|---|
  | farmacia | 225 | 0,209 | 0,194 | 0,5 | 0,29 |
  | biologica | 109 | 0,297 | 0,284 | 0,4 | 0,35 |
  | astronomica | 113 | 0,610 | 0,563 | 0,9 | 0,19 |

- **Esito per regola: solo lunghezza.**
- **Lettura.**
  - A parità di lunghezza le etichette dei vasi e quelle dei frammenti hanno le stesse iniziali, le
    stesse finali e la stessa quota di o-. La differenza dell'e183 è solo di lunghezza, spiegabile con
    lo spazio sui vasi.
  - **Nessun indizio di nomenclatore:** le etichette non distinguono che cosa nominano, salvo la
    lunghezza.

## 2/10/2026 — e188: l'enochiano di Dee e Kelley non ha le regole di riga del Voynich

- **Metodo.** Preregistrato. Trascrizione di Boxer di Sloane MS 3188 (541 righe), a lettere, contro il
  Voynich (lettere EVA) e Plinio a capo.
- **Risultati:**

  | testo | giunture dentro (z) | attraverso l'a capo (z) | R | S (p) | A | ripetizione |
  |---|---|---|---|---|---|---|
  | enochiano | 0,099 (12,4) | 0,070 (2,4) | 0,70 | 1,03 (0,63) | 1,253 | 0,50 |
  | Voynich | 0,192 (281) | 0,003 (0,9) | **0,02** | **0,66 (0,002)** | 1,054 | 1,01 |
  | Plinio a capo | 0,041 (49) | 0,027 (7,3) | 0,66 | 1,04 (0,78) | 1,002 | 0,12 |

- **Esito per regola: non ha le regole di riga del Voynich.**
- **Lettura.**
  - Per le righe l'enochiano si comporta come il latino: il legame fra parole vicine continua
    attraverso l'a capo (R 0,70, come Plinio 0,66) e le righe non evitano di cominciare come quella
    sopra.
  - Ha però un'alternanza fortissima (A 1,25: parole vicine molto diverse) e ripetizioni immediate a
    metà strada (0,50).
  - **La glossolalia scritta di Dee e Kelley non produce la riga chiusa del Voynich.** La riga del
    Voynich resta un tratto senza analoghi, nemmeno fra i testi "inventati" storici: e128 (Gaskell e
    Bowern), Naibbe, Polygraphia III e ora l'enochiano.

## 2/10/2026 — e193: testo circolare e rosette somigliano alle etichette; l'anello di f57v non è ordinato per frequenza

- **Metodo.** Preregistrato, descrittivo.
  - Blocchi non di paragrafo contro 1.000 campioni di paragrafi della stessa dimensione.
  - "Diverso" se almeno due misure hanno |z| > 3.
- **Due correzioni d'esecuzione, in commit a parte:**
  - `testo_corrente` contiene solo i paragrafi: i blocchi si prendono da tutti i loci della ZL;
  - la sequenza di f57v va presa dalla riga dell'anello con più segni singoli, per un periodo, come
    dice la preregistrazione.
- **Risultati** (z delle misure più distanti):

  | blocco | parole | o- | nel vocabolario dei paragrafi | altro | diverso |
  |---|---|---|---|---|---|
  | circolare | 1.831 | 0,38 (z 4,7) | 0,76 (z −3,1) | – | sì |
  | radiale | 350 | 0,35 (z 2,3) | 0,73 (z −3,4) | – | no |
  | rosette | 528 | 0,61 (z 7,1) | 0,73 (z −3,3) | – | sì |
  | anello di f57v | 169 | – | – | segni singoli 64% (z 31), lunghezza 2,2 (z −6,3) | sì |
  | etichette | 1.014 | 0,52 (z 7,0) | 0,60 (z −7,7) | segni singoli z 4,1 | sì |

- **Anello di f57v.**
  - Il periodo estratto è o l d r v x k m f t r y I (con r ripetuto).
  - Non è ordinato per frequenza dei segni nel testo: Spearman 0,27, p 0,39.
  - La ripetizione di r dice che non è un semplice alfabeto.
- **Lettura.**
  - Il testo circolare e quello delle rosette usano più o- e più parole assenti dai paragrafi: si
    comportano come le etichette, cioè come un "etichettese" (e149).
  - Il radiale è a metà strada.
  - L'anello di f57v resta un oggetto a sé (segni singoli ripetuti 4 volte). Non ha la forma di una
    tabella ordinata per frequenza.

## 2/10/2026 — e191: compressione delle scelte, guadagno minuscolo e test di poca potenza

- **Metodo.** Preregistrato.
  - Modello di Markov adattivo sulla sequenza delle scelte, contro il rimescolamento dentro riga e
    scelta.
  - Controlli: latino in codice di Huffman.
- **Risultati** (bit per occorrenza):

  | testo | valore | nullo | guadagno | z |
  |---|---|---|---|---|
  | Voynich | 0,9425 | 0,9448 | 0,0023 | 13,5 |
  | Huffman puro | 0,9774 | 0,9974 | 0,0200 | (enorme) |
  | Huffman mescolato (70%) | 0,9965 | 0,9965 | 0,0000 | 0,4 |

- **Esito per regola: "ridondanza da messaggio".** Non si accetta, per due ragioni.
  - **Potenza:** il test non vede un messaggio Huffman presente nel 70% delle scelte. Il codice di
    Huffman toglie quasi tutta la ridondanza: anche puro guadagna solo 0,02 bit.
  - **Specificità:** il guadagno del Voynich (0,0023 bit) è nove volte più piccolo di un messaggio
    puro. Si spiega con legami meccanici fra scelte della stessa parola (e185: qo- con k/t), che il
    nullo spezza.
- **Verifica (e191b):** un nullo che rimescola parole intere dentro la riga e conserva i legami interni
  alla parola.
- **Nota di metodo per il white paper:** i codici a lunghezza variabile ben fatti sono quasi
  incomprimibili, quindi questo tipo di test non li può escludere. Resta solo il limite di capacità
  (e182).

## 2/10/2026 — e191b: il guadagno di compressione dell'e191 è tutto interno alle parole

- **Metodo.** Preregistrato. Stesso compressore dell'e191, con un nullo che permuta le parole intere
  dentro la riga, ciascuna con le sue scelte.
- **Risultato:** 0,9425 bit per occorrenza contro 0,9425 del nullo; guadagno −0,0001, z −0,4.
- **Esito per regola: il guadagno dell'e191 è interno alle parole.**
- **Lettura.**
  - Una volta conservati i legami fra scelte della stessa parola, l'ordine delle parole non aggiunge
    nessuna ridondanza alla sequenza delle scelte.
  - Nessuna traccia di un messaggio che corre lungo il testo nelle scelte di grafia: né a blocchi
    (e181), né per riga (e185), né sequenziale (e191, e191b). Resta il limite di potenza per i codici
    di Huffman ben fatti.

## 2/10/2026 — e189: i tre canali "liberi" potrebbero portare al massimo ~95.000 bit

- **Metodo.** Preregistrato, descrittivo. Informazione non spiegata dalle regole note, in tre canali:
  - (a) scelte di grafia (e182);
  - (b) segno d'inizio riga dato quello della riga sopra;
  - (c) ordine delle parole nella riga, dato il modello delle giunture. Calcolo esatto su tutte le
    permutazioni per le righe di 3–7 parole (prima parola fissa), estrapolato per parola alle righe
    più lunghe.
- **Risultati:**

  | canale | bit |
  |---|---|
  | (a) scelte di grafia | 49.215 |
  | (b) segno d'inizio riga | 5.823 (1,75 per riga) |
  | (c) ordine delle parole | 40.137 (7.066 esatti su 1.387 righe; 1,34 bit per parola, il resto estrapolato) |
  | **totale** | **95.175** |

- **Equivalente:** 23.000–48.000 lettere di latino, cioè circa 3.900–7.900 parole.
- **Lettura.**
  - È un **limite superiore**. Se il Voynich nascondesse un messaggio solo nella forma (varianti,
    ordine, segni d'inizio) lasciando il vocabolario a un procedimento senza messaggio, il messaggio
    non potrebbe superare qualche migliaio di parole latine, l'equivalente di un breve trattato.
  - Per le scelte di grafia i test di struttura sono negativi (e181, e185, e191b).
  - **Cautela:** la parte (c) è per l'80% estrapolata dalle righe di 6–7 parole. I modelli delle
    abitudini sono semplici, e un modello migliore abbasserebbe il limite.

## 2/10/2026 — e195: le "parole spezzate" sembrano avere spazi più stretti (forse è la lunghezza)

- **Origine.** Ipotesi implicita nella sovrapposizione "split words" di voynichese.com: alcuni spazi
  fra coppie che esistono anche unite (ol daiin / oldaiin) non sarebbero veri separatori.
- **Metodo.** Preregistrato.
  - Larghezza fisica degli spazi certi della ZL (e34), coppie spezzate (a+b presente ≥ 2 volte)
    contro le altre.
  - Stratificazione per giuntura.
- **Risultati:**
  - 22.158 spazi certi, di cui 764 fra coppie spezzate;
  - normali − spezzate = 0,030, z 4,5, p 0,0015;
  - controllo (certi − dubbi): 0,114, z 19,9.
- **Esito per regola: spazi spuri.**
- **Controllo esplorativo, non preregistrato.** Stratificando anche per lunghezza delle due parole,
  la differenza sparisce (0,001, z 0,1, 969 casi utilizzabili). Le coppie spezzate sono fatte spesso
  di parole corte, e accanto a parole corte gli spazi sono più stretti.
- **L'esito non si accetta prima dell'e195b,** preregistrato con la stratificazione per lunghezza e
  con il controllo di potenza.

## 2/10/2026 — e195b: gli spazi delle "parole spezzate" sono normali, a parità di lunghezza

- **Metodo.** Preregistrato. Come l'e195, con strato = (giuntura, lunghezza di a, lunghezza di b).
- **Risultati:**
  - normali − spezzate 0,001, z 0,1, p 0,45 (969 casi, 22 strati);
  - controllo certi − dubbi 0,098, z 7,2, p 0,0005: il test stratificato vede ancora l'effetto noto.
- **Esito per regola: effetto della lunghezza.**
- **Lettura.** Le coppie che esistono anche unite non hanno spazi più stretti degli altri spazi fra
  parole di pari lunghezza. L'ipotesi implicita della sovrapposizione "split words" (spazi spuri) non
  regge. Le parole spezzate sono coincidenze di un vocabolario fatto di pezzi combinabili.

## 2/10/2026 — e192: generatore con tema di pagina e varianti in parte nuove, record di 11/18

- **Metodo.** Preregistrato.
  - Tema di pagina (e180).
  - Varianti attestate, più varianti nuove ben formate con probabilità ν ∈ {0,2; 0,4; 0,6}.
- **Risultati:**

  | ν | pagella | T3 grezzo | T4 ripulito | mancanti |
  |---|---|---|---|---|
  | 0,2 | 10/18 | 1,1 | 2,3 | uniche, legame, unioni, curva piatta, Zipf, verticale, formule, bordo |
  | **0,4** | **11/18** | 0,7 | 3,5 | legame, unioni, curva piatta, Zipf, verticale, formule, bordo |
  | 0,6 | 10/18 | 1,6 | 3,6 | h2, legame, unioni, curva piatta, Zipf, verticale, formule, bordo |

- **Esito per regola: completo no**, ma è il miglior generatore senza messaggio finora.
- **Lettura.** h2, tipi e parole uniche tornano insieme con ν 0,4. Restano fuori le proprietà delle
  giunture (legame, unioni), la forma della distribuzione delle frequenze (Zipf, curva piatta), la
  verticale, le formule e il bordo di riga.

## 2/10/2026 — e196–e201: ipotesi da voynichese.com e da r/voynich

- **e196, coppie ripetute attraverso l'a capo** (voynichese, "word-pairs").
  - Eccesso di coppie ripetute dentro la riga 0,060 (z 29); attraverso l'a capo −0,003 (z −0,6).
  - Rrip −0,05, contro 0,86 di Plinio.
  - **Esito: ripetizioni chiuse nella riga.** È la chiusura della riga, ora anche a livello di parole
    intere.
- **e197, parole uniche** (r/voynich 1qavl2o).
  - Quota di hapax per posizione: prima parola della pagina 0,53; prima di paragrafo 0,46; prima di
    riga 0,18; seconda 0,11; interna 0,11; **ultima di riga 0,23**.
  - Scala verticale: 1.161 coppie contro 1.196 attese (z −1,4). **Esito: assente.**
  - Lettura: gli hapax stanno dove ce lo si aspetta, cioè a inizio paragrafo (gallow) e a fine riga
    (-m, -g). Nessuna "scala".
- **e198, cifrario a ordinamento** (r/voynich 1tcr6pt, Edwards; "Firth's sorting cipher").
  - Insiemi di segni realizzati in più ordini: Voynich 15,3%, latino 2,0%, italiano 2,4%, latino
    ordinato 0%, generatore e180 17,6%.
  - **Esito: non compatibile.** Il Voynich ha molti più "anagrammi" delle lingue, come il generatore
    senza messaggio (alky/kaly/ykal, or/ro): l'ordine dei segni dentro la parola non è fisso.
- **e199, erbario tardo** (r/voynich 1v4hiiz).
  - Mano 1, lingua A: le 10 pagine d'erbario tarde (f87–f96) somigliano alla farmacia più che
    all'erbario iniziale (+0,089, p 0,0005; 9 pagine su 10).
  - **Esito: vocabolario del tempo.** Il vocabolario segue il momento di scrittura, non il soggetto
    disegnato. Conferma l'intuizione del post e la vicinanza nell'ordine ricostruito.
- **e200, anelli dello zodiaco** (r/voynich 1pfv59a). Replica con un disegno diverso dell'e144 B: IM
  prefisso–anello 0,237 contro 0,225, z 0,5. **Esito: assenti**, come nell'e144.
  - okal sta più spesso all'esterno (12/17), ma anche otal (14/25).
- **e201, k o t: radice o riga?** (r/voynich 1sj3vlq).
  - Bit per occorrenza: M0 0,943, radice 0,906, riga 0,930, entrambi 0,898. Risparmio: radice 0,037,
    riga 0,012.
  - **Esito per regola: "classificatore di radice".**
  - Lettura prudente: la "radice" qui è il resto della parola, quindi il risultato dice che molte
    parole sono **lessicalizzate** con k o con t (qokeedy più di qoteedy). L'abitudine di riga aggiunge
    un terzo in più (0,045 insieme).
  - Non dimostra che i gallow siano "classificatori di dominio"; per questo servirebbe un legame con il
    soggetto, che finora manca (e184, e190). Rende però più stretto il limite di capacità: e210.

## 2/10/2026 — e202–e205: intuizioni qualitative da r/voynich, messe alla prova

- **e202, "balbettii" come auto-correzioni** (nyzkc9, cxfm2w).
  - Nelle 1.072 coppie adiacenti quasi uguali (distanza 1) la seconda parola è la più frequente nel
    51,1% dei casi (p 0,5).
  - Generatore e180: 49,0%. Timm e Schinner: 55,3% (p 2·10⁻⁵).
  - **Esito: nessun verso.** Le coppie quasi uguali non sono correzioni (che andrebbero verso la forma
    comune) né copie modificate a senso unico. Il testo di Timm e Schinner ha invece un verso:
    differisce dal Voynich anche qui.
- **e203, ninfe in sequenza come giorni o gradi** (itwqgx).
  - Etichette adiacenti nel cerchio: eccesso di somiglianza 0,008, z 1,7, p 0,044.
  - La somiglianza per distanza è piatta (0,339 / 0,330 / 0,318 / 0,333).
  - **Esito: incerto.** Nessun andamento da conteggio.
- **e204, ricette che rimandano alle piante** (1pz77va).
  - **Esito per regola: nessun rimando**, ma il test non ha forza: solo 7 parole d'erbario hanno 2 o
    più occorrenze tutte sulla stessa pagina.
  - Questo dato è in sé notevole e porta all'e211.
- **e205, esercizio di calligrafia** (1bg4s4m).
  - Irregolarità della larghezza delle parole contro l'ordine di rilegatura dentro le mani: mano 1
    +0,09, mano 2 −0,22, mano 3 +0,14; statistica +0,016, p 0,58.
  - **Esito: nessun miglioramento** (nell'ordine di rilegatura).

## 2/10/2026 — e210: con la parola il limite non scende (combinazione ingenua); qo-/o- e -l/-r sono del tutto imprevedibili

- **Metodo.** Preregistrato.
  - Bit per scelta in validazione incrociata con: la parola neutralizzata (MX); la parola più le
    altre scelte della riga (MXL); più la riga precedente (MXLP).
  - Combinazione dei modelli per rapporti di probabilità.
- **Risultati** (bit per occorrenza):

  | scelta | M0 | MX | MXL | MXLP |
  |---|---|---|---|---|
  | F1 ch/sh | 0,877 | 0,860 | 0,850 | 0,912 |
  | F2 k/t | 0,943 | 0,922 | 0,917 | 0,978 |
  | F3 -l/-r | 0,998 | 0,977 | 1,000 | 1,045 |
  | F5 qo-/o- | 1,000 | 1,000 | 1,000 | 1,041 |
  | F7 -dy/-ey | 0,950 | 0,709 | 0,657 | 0,679 |
  | tutte | 0,946 | 0,890 | 0,881 | 0,930 |

- **Esito:**
  - il modello migliore (MXL) dà 50.097 bit, contro i 49.215 dell'e182 (M2, con gli strati di
    posizione e contesto);
  - **il limite non scende**;
  - totale dei tre canali: 96.057 bit, cioè circa 3.900–8.000 parole latine.
- **Lettura.**
  - La combinazione a rapporti di probabilità conta due volte le stesse informazioni (MXLP peggiora).
    Per stringere il limite serve un modello combinato vero, una regressione con tutti i contesti:
    e210b.
  - **Fatto nuovo:** qo-/o- e -l/-r valgono 1 bit pieno per occorrenza. Né la parola, né la posizione,
    né la riga li prevedono. -dy/-ey invece è in gran parte lessicale (0,66).
  - Se un canale libero esiste, è soprattutto in qo-/o- e -l/-r.

## 2/10/2026 — e211: le parole rare dell'erbario sono poco "della pagina", meno di qualsiasi erbario vero

- **Metodo.** Preregistrato. Quota di parole rare (frequenza 2–5) confinate in una sola unità,
  rispetto alla ridistribuzione casuale (R).
- **Risultati:**

  | testo | unità | parole rare | C | atteso | R |
  |---|---|---|---|---|---|
  | Voynich, erbario | 116 pagine | 697 | 0,010 | 0,005 | **1,96** |
  | *Macer floridus* | 79 capitoli | 1.238 | 0,051 | 0,010 | 5,13 |
  | Isidoro XVII | 326 paragrafi | 874 | 0,106 | 0,003 | 41,6 |
  | generatore e192 | 116 pagine | 879 | 0,230 | 0,005 | 50,2 |

- **Esito per regola: intermedio** (fra 1,5 e 3).
- **Lettura.**
  - Le parole rare del Voynich sono appena più raggruppate del caso. In due erbari latini veri lo sono
    da 2,5 a 20 volte di più.
  - Il nome della pianta e le parole proprie della voce, che in un erbario si ripetono dentro la voce,
    nel Voynich praticamente non ci sono. È un argomento contro "il testo descrive la pianta della
    pagina", indipendente dai test sulle immagini (e184, e190).
  - **Il generatore e192 sbaglia in senso opposto** (R 50): le varianti nuove nascono e si ripetono
    sulla stessa pagina. Nel Voynich le parole nuove nate su una pagina non vi si ripetono. Va
    corretto: per esempio, le varianti nuove non devono entrare nel serbatoio della pagina.

## 2/10/2026 — e206: molti segni "facoltativi" concordano dentro la riga (da verificare con gli strati)

- **Origine.** Sovrapposizione "superfluous characters" di voynichese.com.
- **Metodo.** Preregistrato.
  - Ogni classe (segno, posizione) di coppie di parole che differiscono per un segno tolto.
  - Accordo fra forme lunghe e corte dentro la riga, contro il rimescolamento dentro la pagina.
- **Risultati.** Controllo qo-/o- (q iniziale): z 4,6, valido. Classi con z > 3 (16):
  - d interna 11,8; e interna 8,9; p iniziale 7,0; t interna 6,5; y finale 5,9; sh iniziale 5,3;
  - d iniziale 4,5; l finale 4,5; q iniziale 4,6; o iniziale 3,6; ch interna 3,5; y iniziale 3,3;
  - ch iniziale 3,0; cth iniziale, sh interna, p interna.
  - Nessun effetto per k interna, k e t iniziali, i interna, m finale.
- **Cautela, non preregistrata.** Il nullo conserva la pagina ma non il tipo di riga né la posizione
  della parola. Le classi con p e alcune altre risentono certamente delle prime righe dei paragrafi
  (dove p e f abbondano) e della posizione nella riga.
  - Le classi nuove (d, e, y, o) non si accettano come "scelte di riga" prima dell'e206b, con il nullo
    dentro pagina × prima riga del paragrafo × posizione della parola.

## 2/10/2026 — e207: il paragrafo come unità di contenuto, test non valido

- **Metodo.** Preregistrato. Somiglianza di vocabolario fra righe consecutive dello stesso paragrafo
  e a cavallo di un inizio di paragrafo.
- **Risultati:**
  - **Voynich:** stesso − a cavallo 0,053 (nullo 0,005), p 0,0005; 533 coppie a cavallo;
  - **controllo *Macer floridus*:** 0,007, p 0,18. Solo 74 coppie a cavallo, e i versi sono brevi e
    poco simili fra loro.
- **Esito per regola: test non valido** (il controllo non passa).
- **Lettura.**
  - Nel Voynich la riga che apre un paragrafo condivide molto meno vocabolario con quella sopra.
  - Può essere contenuto, oppure l'effetto noto della prima riga di paragrafo (gallow p/f, parole
    lunghe, "top row" di Tavie), che ha un vocabolario suo.
  - Da rifare escludendo la prima riga di paragrafo, cioè confrontando la seconda riga del paragrafo
    nuovo con l'ultima del precedente, e con un controllo più adatto.

## 2/10/2026 — e214: i nomi dei mesi e dei segni non si trovano nello zodiaco

- **Metodo.** Preregistrato.
  - Una sola chiave che fa leggere, sulle 12 pagine dello zodiaco, il nome del segno o del mese
    (latino, come scritto sul foglio, italiano, tedesco).
  - Confronto con 200 assegnazioni permutate dei nomi alle pagine.
  - Chiavi omofoniche e biunivoche.
- **Risultati** (pagine con il nome su 12):

  | testo, chiave | vero | nullo (media / max) | p |
  |---|---|---|---|
  | Voynich, omofonica | 5 | 4,9 / 6 | 0,82 |
  | Voynich, biunivoca | 4 | 3,9 / 5 | 0,90 |
  | controllo con nomi cifrati inseriti, omofonica | 12 | 5,0 / 6 | 0,005 |
  | controllo, biunivoca | 12 | 3,9 / 5 | 0,005 |

- **Validità: sì. Esito per regola: nessun nome.**
- **Lettura.**
  - Con una sostituzione semplice, anche omofonica, non c'è una chiave che faccia comparire il nome del
    proprio segno o mese sulla propria pagina più che su una pagina qualsiasi. Il controllo mostra che
    se il nome ci fosse, scritto parola per parola con una sostituzione, emergerebbe chiarissimo.
  - Restano escluse da questo test le codifiche non per lettera (codici a parole, sillabe) e i nomi
    abbreviati o in altre lingue.

## 3/10/2026 — Prova di fattibilità scartata: decifrazione a parole per allineamento dei contesti

- **Idea.** Allineare lo spazio delle parole del Voynich ripulito a quello di latino, italiano e
  tedesco, senza dizionario (Artetxe e altri 2018: PPMI + SVD, inizio da profili di somiglianza,
  Procrustes iterato con CSLS). Se il Voynich è un codice a parole, le parole usate negli stessi
  contesti si dovrebbero allineare.
- **Prova di fattibilità, solo sul controllo positivo, prima della preregistrazione.** Latino cifrato
  parola per parola dell'e160: 35.000 parole, la stessa lunghezza del Voynich. Riferimento: altre
  300.000 parole della stessa Bibbia.
  - Inizio da profili: accuratezza @1 = 0,000.
  - Inizio per rango di frequenza: 0,026 col solo rango, 0,004 dopo l'affinamento con i contesti.
- **Decisione:** l'esperimento non si lancia. Con un testo lungo quanto il Voynich, l'allineamento
  per contesti non ritrova nemmeno un codice a parole vero, nella lingua giusta e con un testo di
  riferimento dello stesso genere.
- **Lettura, utile per il white paper.** Un codice a parole (nomenclatore) di questa lunghezza non si
  può rompere per sola statistica dei contesti. Come per le sillabe (e112b), servirebbe una chiave
  esterna, cioè parole note. I tentativi con parole note dove dovevano esserci (e214, nomi dello
  zodiaco) non hanno trovato nulla, per le sostituzioni lettera per lettera.
- Il codice resta in `analisi/scartati/e215_allineamento_parole.py`.

## 3/10/2026 — Strumento: il "voynichizzatore" (testo qualsiasi → voynichese → testo, con chiave)

- **Idea di Davide:** come chiusura, uno strumento che rende "intraducibile" un testo qualsiasi e che
  segue le proprietà e i modi del Voynich per quanto li conosciamo.
- **Prima versione, scartata e non committata:** il generatore produceva il testo e il messaggio stava
  solo in qo-/o- e -l/-r. Davide l'ha giustamente rifiutata: il messaggio deve **essere** il testo, non
  stare in un angolo.
- **Versione adottata** (`analisi/voynichizzatore.py`): codifica aritmetica sul modello generativo
  (steganografia per codifica aritmetica; Ziegler, Deng e Rush 2019).
  - **Modello esplicito**, parola per parola:
    - pagine, paragrafi e lunghezze di riga dalle pagine vere;
    - prima parola dalle parole d'inizio del Voynich (riga o paragrafo, lingua A/B), con l'evitamento
      del primo segno della riga sopra;
    - poi serbatoio della pagina, tema di pagina, varianti attestate o nuove ben formate, copia dalla
      riga sopra, peso di giuntura, ch/sh in seconda posizione, regola di fine riga;
    - le cinque scelte di grafia con le abitudini di riga (memoria, ripartenza a pagina).
  - **Codifica:** il messaggio si comprime (se conviene), si cifra con un flusso derivato dalla chiave
    (quindi è indistinguibile da bit casuali) e fa da "dado" a ogni scelta, con aritmetica esatta su
    frazioni. Chi ha la chiave rifà il modello e ricostruisce i bit; con una chiave sbagliata si
    ottiene un errore.
- **Prove:**
  - "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura." (592 bit) sta in una pagina
    di 28 righe e torna identica;
  - un testo di 249 caratteri (784 bit compresso) sta in una pagina e torna identico;
  - circa 4 bit per parola.
- **Limiti noti:** con i pesi provvisori si vedono ripetizioni troppo frequenti (chol, os) e parole di
  un segno. I parametri vanno presi dall'e224.
- **Da fare (e225, dopo l'e224):** un testo voynichizzato lungo quanto il manoscritto, misurato con la
  pagella, le regole di riga e i test di messaggio. Per costruzione è un campione del modello: deve
  avere le proprietà del generatore.

## 3/10/2026 — Notte: progetto del voynichizzatore finale

- Davide ha scelto (prima di dormire):
  - imitare **tutto il manoscritto** (sezioni, mani, lingue A/B);
  - uscita in **EVA, immagine delle pagine, etichette e testo circolare**;
  - **parola chiave**;
  - **l'indistinguibilità prevale sulla compattezza**.
- Il progetto è in `rassegna/voynichizzatore_progetto.md`.
  - **Principio:** con bit cifrati uniformi, l'uscita è un campione del modello. Tutto il lavoro sta nel
    modello, che deve essere lo stesso del generatore.
  - **Architettura:** un modello, due motori; ogni scelta visibile è un simbolo codificato, ogni
    variabile nascosta viene dalla chiave.
  - **Criteri di accettazione** per l'e225: pagella, regole di riga, test di messaggio silenziosi, un
    discriminatore con AUC ≤ 0,6, nessuna copia e sicurezza.
- **Difetti della v2 visti su una pagina di prova:**
  - *chol* 24 volte su 215 parole (11%, contro l'1,1% del Voynich);
  - 15 righe su 28 finiscono con *daim* o *koeam* (nel Voynich la finale più comune, *daiin*, chiude
    131 righe su 4.130).

## 3/10/2026 — e227: le unioni contro la giuntura (non valido); il legame vale per due terzi anche nelle coppie uniche

- **Preregistrato.** Fa parte dei test notturni sui meccanismi delle proprietà mancanti al generatore.
- **Deviazione da annotare.** Una prova rapida del codice ha calcolato i valori del Voynich (con 3
  estrazioni) prima del commit della preregistrazione. Il testo della preregistrazione era già scritto
  e non è stato toccato; lo dice anche il messaggio di commit.
  - Regola per il futuro: le prove rapide si fanno solo sui controlli.
- **A, unioni.** U/N0 (nullo della pagella), U/N1 (stesso ultimo segno), U/N2 (stessi ultimi due segni):
  - Voynich 1,92 / 1,29 / 1,16 (z 12,6);
  - generatore e192 1,29 / 1,05 / 1,04;
  - generatore con il 6% di parole spezzate 1,71 / 1,17 / 1,06.
  - **Non valido:** il controllo positivo non arriva a U/N2 ≥ 1,3, perché il nullo che conserva due
    segni finali assorbe quasi tutto l'effetto delle spezzature.
  - Descrittivamente, il Voynich supera le spezzature al 6% sotto tutti e tre i nulli.
- **B, legame.**
  - Voynich: 0,188 su tutte le coppie interne, 0,125 sulle coppie che compaiono una volta (Q 0,67).
  - Generatore: Q 0,94 (valido).
  - **Esito misto.** Il legame del Voynich solo sulle coppie uniche (0,125) supera già quello del
    generatore su tutte (0,107): la regola dei segni del generatore è troppo debole.
- **Osservazione non preregistrata, ma decisiva per il passo dopo.** Spezzare il 6% delle parole lunghe
  sposta *tre* misure insieme verso il Voynich: legame da 0,107 a 0,161, unioni da 1,29 a 1,71, Q da
  0,94 a 0,74. Uno spazio dentro una parola eredita la dipendenza fra segni interni e crea coppie
  ripetute.
  - Ipotesi messa alla prova subito nell'e227b: una sola quota di spezzature riproduce tutte e cinque le
    misure?

## 3/10/2026 — e226: le parole nuove nascono un po' "dalla pagina", meno che nel generatore ma non la metà

- **Preregistrato.** Una parola alla prima occorrenza ha un "genitore" (tipo già visto a distanza di edit
  1) fra le parole precedenti della stessa pagina più spesso che fra le prime parole di altre pagine
  della stessa sezione? Il rapporto è L.
- **Risultati:**

  | testo | con un genitore | L | intervallo |
  |---|---|---|---|
  | Voynich | 81% | **1,56** | 1,50–1,62 |
  | generatore e192 (controllo positivo) | 85% | 2,19 | 2,10–2,28 |
  | Voynich rimescolato nella sezione (controllo negativo) | 81% | 1,05 | 1,00–1,09 |
  | *Macer floridus* | 34% | 1,52 | 1,33–1,78 |
  | Isidoro XVII | 27% | 6,75 | 5,21–8,71 |

  - Gli esponenti di Heaps sono simili: Voynich 0,72, generatore 0,74, Macer 0,71, Isidoro 0,81.
- **Esito preregistrato:**
  - test valido;
  - nel Voynich la **nascita è intermedia** (1,3 < L < 2);
  - il generatore **non** è "troppo locale" per la soglia preregistrata (il doppio): 2,19 contro 1,56,
    con intervalli separati.
- **Lettura.**
  - Quattro parole nuove su cinque sono a una modifica da una parola già scritta. Nei testi latini, in
    lettere, sono una su tre; il confronto fra unità diverse è solo indicativo.
  - La pagina conta, ma meno che nel generatore.
  - Il divario enorme dell'e211 sulle parole rare (R 50 contro 1,96) non si spiega con dove nascono le
    parole, che è solo un po' più locale. Il motivo probabile è che nel generatore la variante nata su
    una pagina resta lì: il serbatoio è della pagina. Nel Voynich, invece, le parole rare tornano in
    altre pagine.
  - **Indicazione per il generatore:** un lessico che cresce per tutto il manoscritto, con le varianti
    nuove riusabili altrove, più che una nascita meno locale. Da provare.

## 3/10/2026 — e227b: il 6% di parole spezzate dà insieme legame, Q e unioni del Voynich, ma non l'eccesso a giuntura conservata

- **Preregistrato.** Una sola quota di spezzature σ riproduce le cinque misure dell'e227 sul Voynich
  (U/N0 1,92, U/N1 1,29, U/N2 1,16, legame 0,188, Q 0,67)?
- **Risultati** (generatore e192, seme 1):
  - **σ 0,09, cioè il 6,1% di parole spezzate:**
    - U/N0 **1,87**, legame **0,189**, Q **0,65**: tutti e tre in tolleranza;
    - U/N1 1,20 e U/N2 1,08: fuori.
  - **σ più alti:** U/N1 e U/N2 restano fermi (1,19–1,20 e 1,06–1,07), mentre legame e Q superano il
    bersaglio. Con σ 0,25 il legame arriva a 0,308.
  - **Lunghezza media delle parole:** scende da 4,46 a 4,20.
- **Esito preregistrato: non basta.** Il più vicino è σ 0,09, con fuori U/N1 e U/N2; non si fa la
  verifica sul seme 2 perché nessun σ passa.
- **Lettura.**
  - **Legame.** Il "legame" del Voynich (0,188), che nessun generatore raggiungeva, si ottiene quasi
    esattamente spezzando il 6% delle parole. Si ottengono insieme anche la sua quota nelle coppie uniche
    e le unioni grezze. La regola delle giunture fra segni non va rafforzata: il di più viene da spazi
    messi dentro parole.
  - **Ciò che manca.** Resta l'eccesso di unioni a parità di segni finali. I tagli a caso fra i punti
    possibili non lo danno. Ipotesi successiva (e227c): i tagli cadono di preferenza dove le due metà
    sono parole frequenti.
  - **Conseguenza per il generatore.** Le parole di base devono essere più lunghe, altrimenti la
    spezzatura accorcia troppo le parole.

## 3/10/2026 — e228 ed e228b: la copia verticale segue la parola che sta fisicamente sopra (copia a vista)

- **Domanda** (aperta dall'e58): la somiglianza "in verticale" viene dalla parola **materialmente sopra**
  (copia a vista) o da quella con lo **stesso numero d'ordine** nella riga sopra (colonne logiche)?
  - Si usano i riquadri di voynichese.com allineati alla ZL (204 pagine, 30.011 parole su 34.612).
  - Si tengono i casi in cui le due parole differiscono: 4.341.
- **e228, preregistrato.** Δ = sim(parola fisicamente sopra) − sim(parola di pari indice).
  - Voynich: Δ **+0,019**, z 3,9, p 0,0002.
  - Controlli su una base neutra (righe sopra prese da altre pagine): nullo +0,002 (p 0,58), fisico
    +0,029, indice −0,024.
  - Esito: **copia a vista (fisica)**.
- **e228b, preregistrato dopo un difetto di disegno visto sui soli controlli.** Una prova rapida con un
  altro seme aveva dato Δ +0,009 nella base neutra: la parola fisicamente sopra tende a essere più lunga
  e la somiglianza normalizzata favorisce lunghezze simili. Il nullo dell'e228b è fatto di 200 basi
  neutre:
  - Δ nullo medio +0,0046;
  - Voynich **z_Δ 3,9**;
  - eccesso verso la parola fisicamente sopra **z_P 3,4**, verso quella di pari indice **z_I −1,2**;
  - controlli: neutro −1,2, fisico 6,3, indice −8,0, tutti validi.
  - Esito: **copia a vista (fisica)**.
- **Lettura.**
  - È la prima indicazione di **come** chi scriveva riprendeva le parole: guardando quella appena sopra
    sulla pagina, non contando le posizioni. La traccia verticale non è una struttura a colonne logiche
    (tabella); è un'abitudine visiva di copia.
  - Si accorda con l'"autocitazione" di Timm e Schinner nella forma "copia ciò che vedi vicino". Si
    accorda anche con l'e59, dove la traccia si estende a più righe sopra.
- **Conseguenza per il generatore e il voynichizzatore.** La copia verticale va fatta per posizione
  fisica. Senza immagini, la posizione si stima dal conteggio cumulato dei segni.

## 3/10/2026 — e231: un discriminatore distingue il generatore e192 dal Voynich (AUC 0,97) e dice dove sbaglia

- **Preregistrato.**
  - Regressione logistica su caratteristiche di pagina in cinque gruppi: segni, coppie di segni,
    parole, riga, verticale.
  - Validazione incrociata a 10 pieghe ripetuta 5 volte; pagina vera e gemella generata nella stessa
    piega.
  - Nessuna caratteristica di appartenenza al vocabolario del Voynich.
- **Controlli:** A contro B 1,000 (valido); etichette a caso 0,527 (valido).
- **Generatore e192 contro Voynich: AUC 0,970, distinguibile.** AUC per gruppo:
  - segni 0,63; coppie 0,79; parole 0,92; riga 0,94;
  - verticale 0,49, che non distingue.
- **Caratteristiche più pesanti** (Voynich contro generatore):
  - righe che finiscono in **-m**: 13,9% contro 2,3%. Manca la regola di fine riga (η, e224);
  - **unioni attestate** nella pagina: 9,2% contro 4,8%. Mancano le parole spezzate (e227b);
  - parole fra le **100 più frequenti**: 42% contro 36%. Il generatore ha frequenze meno concentrate
    (Zipf);
  - parole **uniche nel testo**: 14,6% contro 12,7% (curva piatta, e226);
  - **parole uniche nella pagina** (0,64 contro 0,56) e **tipi su parole nella pagina** (0,76 contro
    0,69).
    - **Proprietà nuova**, che la pagella non misura (lì "tipi" è sull'intero testo): le pagine vere
      ripetono meno le proprie parole.
    - Il generatore pesca troppo dal serbatoio della pagina; le pagine vere usano più le parole
      frequenti di tutto il manoscritto e più forme uniche.
  - righe che finiscono in -l e -o più frequenti nel generatore.
- **Lettura.**
  - Le proprietà che la pagella segnava come mancanti (bordo, unioni, Zipf, curva piatta) sono proprio
    quelle che il discriminatore usa. Le due misure si confermano a vicenda.
  - In più c'è la varietà dentro la pagina: un generatore buono deve pescare meno dalla pagina e più dal
    manoscritto intero.
  - Il discriminatore si rieseguirà sulla configurazione finale dell'e224/e230.

## 3/10/2026 — e227c: neanche i tagli dove le metà sono frequenti danno l'eccesso di unioni a giuntura conservata

- **Preregistrato.** Il punto di taglio si sceglie con peso (f(a)·f(b))^β, con β ∈ {0; 0,5; 1; 2} e
  σ ∈ {0,06; 0,09; 0,12}.
- **Validità:** σ 0,09 e β 0 ripete l'e227b (U/N0 1,84, legame 0,187, Q 0,67): valido.
- **Risultati.**
  - Con β > 0, U/N1 e U/N2 restano a 1,19–1,22 e 1,06–1,08 (bersagli 1,29 e 1,16).
  - Il legame cala, perché le metà frequenti sono corte e la giuntura dipende meno dai segni interni.
- **Esito: non bastano.** Il punto più vicino resta σ 0,09 con β 0, fuori U/N1 e U/N2.
- **Lettura.**
  - L'eccesso di unioni che resta a parità di segni finali è una proprietà a sé. Coppie di parole
    vicine **specifiche** si uniscono in parole attestate più di quanto dica la loro fine.
  - Né spezzare a caso né spezzare dove le metà sono frequenti lo produce.
  - Resta aperta: per il voynichizzatore è una proprietà di second'ordine da segnalare come mancante,
    se non si trova il meccanismo.

## 3/10/2026 — e206b: con il nullo stratificato restano 12 classi di segni facoltativi decise per riga

- **Preregistrato.** Come l'e206, ma i valori si rimescolano dentro pagina × prima riga di paragrafo ×
  posizione della parola nella riga.
- **Controllo** (q iniziale = qo-/o-): z 4,3, valido.
- **Restano (z > 3):**
  - *d* interna 10,9: corrisponde a -dy/-ey, F7;
  - *e* interna 9,0;
  - *t* interna 6,3;
  - *y* finale 5,2;
  - *ch* iniziale 5,1;
  - *sh* iniziale 4,8;
  - *q* iniziale 4,3: F5;
  - *d* iniziale 4,1;
  - *l* finale 4,1;
  - *cth* iniziale 3,6;
  - *o* iniziale 3,5;
  - *sh* interna 3,2.
- **Cadono rispetto all'e206:** *p* iniziale (da 7,0 a 1,7), *p* interna (da 4,6 a 1,0), *y* iniziale e
  *ch* interna. Per *p* la cautela era giusta: l'effetto veniva dalle prime righe dei paragrafi.
- **Lettura.**
  - Oltre alle cinque scelte note, la riga "decide" se usare la forma lunga o corta per diversi segni
    facoltativi:
    - *e* doppia o semplice;
    - *y* finale presente o no;
    - *ch*/*sh* iniziale presente o no (per esempio *chol*/*ol*);
    - *d* iniziale (*dal*/*al*);
    - *l* finale;
    - *t* interna.
  - Con 46 classi provate, a z > 3 ci si aspetta meno di un falso positivo.
  - **Per il voynichizzatore:** lo stato di riga deve includere anche queste scelte, oltre alle cinque
    (o un'unica "abitudine di lunghezza" per riga, se si dimostra che sono correlate: da verificare).

## 3/10/2026 — e206c: le scelte di riga dell'e206b sono quasi indipendenti (legame parziale, debolissimo)

- **Preregistrato.**
  - Correlazioni fra righe dei residui di strato per le 66 coppie delle 12 classi, senza parole in
    comune fra le due classi di una coppia.
  - Nullo: le righe si permutano dentro la pagina, indipendentemente per classe (200 volte).
- **Risultati:**
  - media delle correlazioni 0,014 contro 0,001 del nullo (z 3,2, p 0,01);
  - prima componente 10,9% contro 10,3% (z 2,1).
  - Coppie più correlate, tutte ≤ 0,09: *y* finale / *d* interna, *e* interna / *y* finale, *d*
    interna / *l* finale, *d* interna / *t* interna.
- **Esito preregistrato: legame parziale.**
- **Lettura.**
  - Come le cinque scelte note (e185), anche queste sono in gran parte **indipendenti**. Non c'è
    un'unica "abitudine di lunghezza" della riga.
  - Il piccolo legame comune riguarda le terminazioni (famiglie -edy/-eey/-dy).
  - **Per il voynichizzatore:** uno stato di riga con una dozzina di interruttori quasi indipendenti, con
    un debole legame fra quelli delle terminazioni, invece di un unico parametro.

## 3/10/2026 — e227d: spezzature a caso più prefissi a -l/-r staccati riproducono tutte e cinque le misure di giuntura

- **Origine, dichiarata.** Dopo l'e227c ho esplorato, fuori preregistrazione, quali coppie portano
  l'eccesso di unioni a giuntura conservata.
  - Quasi tutto viene da prime parole corte in -l/-r: *ol* +195, *or* +116, *ar* +68, *chol*, *al*,
    *dar* +42, *qol* +41, *dal* +31.
  - Da lì l'ipotesi preregistrata: prefissi staccati.
- **Preregistrato.** Generatore e192 con:
  - distacco del prefisso (parola attestata di al più 3 unità in l/r all'inizio di una parola il cui
    resto è attestato) con probabilità π;
  - spezzatura a caso σ.
- **Risultati:**
  - σ 0,09 con π 0,30 è l'unica combinazione con tutte e cinque le misure in tolleranza sul seme 1:
    U/N0 1,87, U/N1 1,23, U/N2 1,11, legame 0,197, Q 0,63;
  - **verifica sul seme 2:** U/N0 1,84, U/N1 1,25, U/N2 1,14, legame 0,180, Q 0,67, ancora tutte in
    tolleranza;
  - **profilo dell'eccesso** nel testo generato: *ol* +246, *or* +69, *al* +61, *ar* +52, *dal* +32,
    *qol* +20, *dar* +16. Somiglia a quello del Voynich, con *ol* troppo forte e *or*, *chol* troppo
    deboli.
- **Esito preregistrato: prefissi staccati bastano (σ 0,09, π 0,30).**
- **Cautele.**
  - Due parametri per cinque bersagli, e l'ipotesi è nata da un'esplorazione degli stessi dati: è una
    prova di **sufficienza**, non che sia andata così.
  - U/N1 e U/N2 stanno appena dentro il limite inferiore.
  - La lunghezza media scende a 4,1 contro 4,46: le parole di base dovrebbero essere più lunghe.
- **Lettura.** Si ottengono così cinque proprietà di giuntura e d'unione che nessun generatore aveva:
  - il legame fra parole vicine;
  - la sua quota nelle coppie uniche;
  - le unioni grezze;
  - le unioni a parità di uno e due segni finali.

  Bastano due abitudini di scrittura semplici:
  - uno spazio messo a volte dentro una parola;
  - i prefissi corti *ol*, *or*, *ar*, *al*, *dal*, *qol*… scritti spesso staccati.

  È coerente con le "terne lontane" dell'e60 fatte di pezzi staccati (*ol s aiin*, *or aiin*) e con le
  giunture "morbide" dell'e12.
- **Per il generatore e il voynichizzatore:** due meccanismi espliciti, con le parole di base
  allungate.

## 3/10/2026 — e232: pescare dal manoscritto invece che dalla pagina non inganna il discriminatore

- **Preregistrato.**
  - Generatore dell'e230 (partenza dell'e224, η 1, σ 0,09).
  - δ è la probabilità di prendere la parola di base dalle frequenze del Voynich intero.
  - Metrica: l'AUC del discriminatore dell'e231.
- **Validità:** con δ 0 il testo è identico all'e230.
- **Risultati:**
  - η 1 e σ 0,09 abbassano l'AUC da 0,97 (e192) a **0,91–0,92**;
  - δ 0,2 dà 0,914 e δ 0,4 dà 0,929: δ non aiuta, e la verifica si fa solo per δ 0 (0,918).
  - La varietà dentro la pagina sale con δ (0,70 → 0,74), ma la quota di parole frequenti no (0,37).
- **Esito: δ non aiuta abbastanza.**
- **Che cosa usa ancora il discriminatore** (Voynich contro generatore):
  - parole fra le 100 più frequenti: 0,42 contro 0,38;
  - parole uniche nel testo: 0,15 contro 0,12;
  - lunghezza media: 4,29 contro 4,08 (le spezzature accorciano);
  - **somiglianza fra parole vicine: 0,22 contro 0,19**;
  - righe in -m: 0,14 contro 0,12;
  - deviazione della lunghezza più alta nel generatore.
- **Lettura e ipotesi successiva (e233).**
  - Il generatore modifica allo stesso modo parole frequenti e rare: disperde le frequenti, che restano
    meno concentrate, e crea meno forme uniche.
  - Non copia mai la parola appena scritta, quindi le parole vicine sono meno simili.
  - Ipotesi: le parole frequenti si scrivono esatte e quelle rare si variano; a volte si riprende la
    parola precedente con una variante.

## 3/10/2026 — e210b: con un modello sequenziale vero il canale delle scelte scende del 4% (il limite regge)

- **Correzione di metodo rispetto all'e210, preregistrata.** L'MXL dell'e210 condizionava ogni scelta
  sulle altre occorrenze della riga, prima e dopo. È una pseudo-verosimiglianza, non un limite
  superiore. L'e210b usa solo ciò che precede nell'ordine di lettura.
- **Metodo.**
  - Regressione logistica per scelta. Caratteristiche:
    - la parola;
    - la stessa scelta prima nella riga, nella riga precedente e prima nella pagina;
    - le altre scelte prima nella riga;
    - la posizione nella riga, la prima riga di paragrafo, la lingua e la sezione.
  - Validazione su pagine pari e dispari.
- **Risultati** (bit per occorrenza: tasso di base / solo parola / combinato):

  | scelta | tasso di base | solo parola | combinato |
  |---|---|---|---|
  | F1 ch/sh | 0,877 | 0,848 | 0,793 |
  | F2 k/t | 0,943 | 0,920 | 0,881 |
  | F3 -l/-r | 0,998 | 0,967 | 0,939 |
  | F5 qo-/o- | 1,000 | 0,988 | 0,924 |
  | F7 -dy/-ey | 0,950 | 0,731 | 0,628 |

  - **Totale: 47.217 bit**, contro 49.215 dell'e182: −4,1%.
  - Tre canali: **93.177 bit**, cioè circa 3.800–7.800 parole latine.
- **Esito preregistrato: il limite regge**, perché la soglia era −5%.
- **Lettura.**
  - Il tetto di capacità è robusto. Un messaggio nascosto nelle scelte, nel segno d'inizio e nell'ordine
    non può superare qualche migliaio di parole.
  - qo-/o- e -l/-r non sono del tutto imprevedibili come sembrava nell'e210: con lingua, sezione e
    posizione perdono il 6–8%.
  - Per il voynichizzatore è anche una stima della capacità di questi canali in un testo indistinguibile.

## 3/10/2026 — e233: variare le parole rare e tenere esatte le frequenti aiuta, ma non abbastanza (AUC 0,93 → 0,89)

- **Preregistrato.**
  - κ: modifiche medie MU·(2r)^κ, con r rango percentile della parola.
  - χ: la seconda candidata è una variante della parola precedente.
  - Dopo la generazione, spezzature e prefissi staccati dell'e227d.
  - Metrica: l'AUC del discriminatore.
- **Validità:** con κ 0 e χ 0 il testo è identico all'e232.
- **Risultati:**
  - seme 1: da 0,938 (κ 0, χ 0) a 0,860 (κ 1, χ 0,2) e 0,863 (κ 1, χ 0);
  - verifica (semi 2–3): **0,931 contro 0,889**, −0,042.
- **Esito: non aiuta abbastanza**, perché la soglia era −0,05.
- **Che cosa cambia:**
  - con κ 1 la quota fra le 100 più frequenti arriva a quella del Voynich (0,428 contro 0,424);
  - con χ sale la somiglianza fra parole vicine (0,206 contro 0,223 del Voynich).
- **Che cosa resta** (caratteristiche più pesanti):
  - lunghezza media (4,01 contro 4,29), accorciata dalle spezzature;
  - **varietà dentro la pagina** (uniche nella pagina 0,52 contro 0,64; tipi su parole 0,66 contro
    0,76), che con κ peggiora;
  - parole uniche nel testo (0,12 contro 0,15);
  - deviazione della lunghezza più alta.
- **Lettura.**
  - Il generatore ottiene l'omogeneità della pagina ripetendo **identiche** le parole del tema e del
    serbatoio. Il Voynich la ottiene con **varianti simili ma diverse**: le pagine vere sono omogenee e
    insieme varie.
  - È l'ipotesi successiva, e234: le parole del tema si scrivono sempre con almeno una modifica.

## 3/10/2026 — e190: anche con una misura del disegno migliore, piante simili non hanno vocabolario simile

- **Preregistrato.** È il rifacimento dell'e184.
  - Una maschera del disegno che esclude le macchie della pergamena, sviluppata su f3r e f9v senza
    guardare il testo.
  - Otto caratteristiche: area, verde, profili, proporzioni, radici, foglie, colore.
  - Coppie di pagine d'erbario dello stesso gruppo di mano e lingua, di fascicoli diversi.
- **Risultati:** 122 pagine, 3.682 coppie, Spearman −0,062 (nullo 0,003), p 0,84. Nessuna
  caratteristica presa da sola supera |0,09|.
- **Esito: nessun legame.**
- **Lettura.** Conferma l'e184 con un disegno misurato meglio. Si accorda con l'e211 (parole rare poco
  "della pagina") e con l'e122b (la farmacia non condivide parole con l'erbario della stessa pianta).
  Nell'erbario il vocabolario non segue la pianta disegnata.

## 3/10/2026 — e234: il tema variato dà la varietà della pagina, ma i parametri si fanno concorrenza

- **Preregistrato.**
  - τ: una candidata dal tema rimasta uguale si modifica una volta.
  - ℓ: preferenza per le candidate lunghe.
  - Parte dall'e233 con κ 1 e χ 0,2.
- **Validità:** con τ 0 e ℓ 0 il testo è identico all'e233.
- **Risultati** (seme 1):
  - la combinazione migliore resta τ 0 e ℓ 0 (AUC 0,863);
  - **τ 1** porta la varietà della pagina al livello del Voynich (tipi su parole 0,747 contro 0,756;
    uniche 0,134 contro 0,137), ma l'AUC sale a 0,951;
  - **ℓ 1,5** allunga troppo le parole (4,60 contro 4,46) e abbassa la quota fra le 100 più frequenti
    (0,36 contro 0,42).
  - Verifica: τ 0 e ℓ 0 dà 0,889 sui semi 2–3.
- **Esito: non aiuta abbastanza**, perché la scelta coincide con la partenza.
- **Lettura.**
  - Ogni meccanismo da solo porta una caratteristica al valore del Voynich: κ la concentrazione delle
    frequenti, χ la somiglianza fra vicine, τ la varietà della pagina, ℓ la lunghezza.
  - Ma si fanno concorrenza: τ e ℓ tolgono peso alle parole frequenti, che sono corte e ripetute.
  - Una salita per coordinate su un parametro alla volta, a partire da una combinazione fissa, non basta.
    Serve una ricerca congiunta con il discriminatore come obiettivo: e235.

## 3/10/2026 — Registrazione dei riquadri di voynichese.com sulle immagini IIIF a piena risoluzione: completata

- **Strumento:** `analisi/piena_risoluzione.py` (committato il 2/10). Correlazione incrociata FFT della
  maschera d'inchiostro, scala 1,5–2,3.
- **Esito:** 169 pagine registrate (cache `dati/cache/registrazioni_iiif.json`, non nel repository).
  - Correlazione mediana 0,21 (minimo 0,02, massimo 0,37).
  - 24 pagine sotto 0,1, da considerare dubbie.
- **Per l'e194** (discretezza di ch/sh sui ritagli a piena risoluzione) e per gli altri test sulle
  immagini, da preregistrare:
  - una soglia di qualità (per esempio correlazione ≥ 0,15);
  - un controllo a vista su un campione di pagine, scelto prima di guardare i risultati.

## 3/10/2026 — Prova di fattibilità per l'e194 (ch/sh sulle immagini piene): misura ingenua non adatta

- **Non è un esperimento.** È una prova di disegno su due pagine di sviluppo, f9v e f76r, da escludere
  poi dal test.
- **Si vede che:**
  - i ritagli a piena risoluzione sono ben allineati alle parole;
  - il pennacchio di *sh* è visibile a occhio.
- **Misura provata.** Inchiostro sopra la fascia del corpo, nella zona del primo segno, normalizzato
  sull'altezza del corpo.
  - Su f76r non separa *ch* e *sh*: AUC 0,22, addirittura rovesciata.
- **Cause, viste sulle immagini:**
  - nel ritaglio allargato verso l'alto entrano le code della riga sopra, che spesso vengono prese per
    il corpo della parola;
  - i pennacchi sono tratti sottili e chiari, sotto la soglia fissa d'inchiostro.
- **Da riprogettare con Davide:**
  - fascia del corpo cercata solo dentro il riquadro;
  - soglia adattiva (Otsu sul ritaglio);
  - esclusione dei tratti connessi che escono dal bordo superiore;
  - controllo positivo, cioè AUC fra *ch* e *sh* annotati ≥ 0,8, prima di chiedersi se la
    distinzione sia discreta o graduale.

## 3/10/2026 — e235: la ricerca congiunta non scende sotto AUC 0,86 (ottimo locale); la famiglia "copia e modifica" ha un limite

- **Preregistrato.**
  - Salita per coordinate (2 passate) su α, τ, ℓ, κ e χ.
  - Obiettivo: l'AUC del discriminatore sul seme 1; verifica sui semi 2–3.
- **Risultati.**
  - Nessun cambio di un solo parametro migliora la partenza (κ 1, χ 0,2, τ 0, ℓ 0, α 1: AUC 0,863).
  - α 1,3–1,6 concentra troppo: fra le 100 0,46–0,50, tipi su parole nella pagina 0,60–0,64.
  - τ alza la varietà, ma abbassa la concentrazione e la somiglianza fra vicine.
  - ℓ 1 dà la lunghezza giusta (4,48), ma toglie concentrazione.
  - Verifica: partenza = finale = **0,889**.
- **Esito: nessun miglioramento netto.**
- **Lettura.**
  - Con i meccanismi provati stanotte, il discriminatore scende da 0,97 (e192) a circa 0,86–0,89, non
    oltre.
  - Le caratteristiche che restano riguardano la **struttura del vocabolario di pagina**. Le pagine vere
    sono insieme molto varie (tipi su parole 0,76, molte forme uniche) e molto concentrate sulle parole
    frequenti del manoscritto (0,42).
  - Nei generatori le due cose si escludono: più varietà significa meno concentrazione, e viceversa. Le
    pagine vere sembrano fatte di **parole frequenti esatte più varianti uniche**, con poche parole
    "della pagina" ripetute. Il generatore invece ripete il serbatoio della pagina.
  - Proposta per domani: un generatore di architettura diversa, con due fonti (parole frequenti globali,
    esatte; varianti nuove quasi tutte uniche, ma simili alle vicine) e niente serbatoio di pagina
    ripetuto. L'omogeneità verrebbe dalla somiglianza delle varianti, non dalla ripetizione.
  - Per il paper: un discriminatore semplice distingue ancora le pagine vere da ogni generatore senza
    messaggio provato. La pagella a 18 proprietà non basta come criterio di indistinguibilità.

## 3/10/2026 — e236: senza serbatoio di pagina il discriminatore vince di più e la pagina si perde

- **Preregistrato.**
  - Candidate esatte dalle frequenze del manoscritto (probabilità g), altrimenti varianti con almeno una
    modifica di parole delle due righe precedenti (ρ) o del manoscritto.
  - Nessun serbatoio di pagina; spezzature e prefissi staccati dopo la generazione.
- **Risultati:**
  - AUC 0,96–0,99 sul seme 1; la scelta (g 0,9, ρ 0,9) dà **0,946** sui semi 2–3, contro il riferimento
    0,889;
  - la varietà della pagina supera il Voynich (tipi su parole 0,80 contro 0,76);
  - somiglianza fra vicine 0,17 contro 0,22; parole uniche 0,10 contro 0,14;
  - pagella (seme 2): **10/18**. Mancano omogeneità, gradiente, deriva, profilo di pagina, uniche, curva
    piatta, lunghezze vicine e verticale.
- **Esito: non migliore.**
- **Lettura.**
  - Togliere il serbatoio di pagina fa perdere proprio le proprietà di pagina: omogeneità, gradiente,
    profilo, deriva.
  - Le pagine vere hanno una base di parole propria, ma la usano in modo diverso dai nostri generatori:
    - più varietà del generatore "copia e modifica";
    - meno del generatore a due fonti;
    - parole vicine più simili di entrambi.
- **Bilancio della notte sui generatori** (e230 e e224 ancora in corso):
  - il discriminatore è passato da 0,97 (e192) a 0,86–0,89 con fine riga, spezzature, prefissi staccati,
    κ e χ;
  - tre architetture e una ricerca congiunta non scendono oltre;
  - la proprietà ancora non capita è il modo in cui una pagina riusa e varia le proprie parole.

## 3/10/2026 — e237: come una pagina del Voynich riusa le proprie parole (un terzo ripetute, più di un terzo varianti)

- **Preregistrato come descrittivo.** Ogni parola, tranne la prima della pagina, si classifica come:
  - R, ripetizione di una parola già sulla pagina;
  - V, variante a distanza 1 di una parola della pagina;
  - F, fra le 200 più frequenti;
  - A, già scritta in pagine precedenti;
  - N, nuova.
- **Risultati:**

  | testo | R | V | F | A | N | distanza R / V (righe) |
  |---|---|---|---|---|---|---|
  | **Voynich** | **31,9%** | **37,5%** | 7,2% | 9,1% | **14,3%** | 3 / 2 |
  | copia e modifica (e233/e235) | 40,0% | 35,7% | 5,9% | 7,2% | 11,2% | 3 / 2 |
  | due fonti (e236) | 27,3% | 41,8% | 7,2% | 11,4% | 12,3% | 4 / 2 |
  | e192 | 36,3% | 36,1% | 6,1% | 8,8% | 12,7% | 3 / 2 |

  - Scarti oltre il 20% relativo:
    - copia e modifica: R (troppe ripetizioni), A e N (troppo poche);
    - due fonti: A.
- **Lettura.**
  - **Fatto descrittivo nuovo e semplice.** Nel Voynich più di due parole su tre sono la ripetizione
    esatta (un terzo) o una variante a una modifica (più di un terzo) di una parola **già scritta sulla
    stessa pagina**, di solito 2–3 righe sopra.
  - Solo una parola su sette è una forma mai vista.
  - È la descrizione quantitativa più diretta del procedimento di scrittura: guardare indietro di poche
    righe e riscrivere la parola identica o cambiata di un segno.
  - Il generatore "copia e modifica" migliore del discriminatore ripete troppo, perché κ = 1 tiene esatte
    le parole frequenti della pagina, e inventa troppo poco. Il bersaglio per il generatore e per il
    voynichizzatore ora è esplicito: R ≈ 32%, V ≈ 37%, N ≈ 14%, con fonti a 2–3 righe.

## 3/10/2026 — e238: seguire il profilo di riuso con varianti forzate rompe la forma delle parole (AUC 0,99)

- **Preregistrato.** Candidate estratte con le quote dell'e237 (R, V, F, A, N), fonti dalle ultime 3
  righe. Le varianti (V, N) sono modifiche forzate (`e234.forza_variante`).
- **Risultati** (semi 2–3):
  - **AUC 0,987**, peggio del riferimento 0,889;
  - profilo: R 31,5% (giusto), ma V 45% (troppe) e N 11%. La selezione per giuntura favorisce le
    varianti;
  - pagella (seme 2): **9/18**. Mancano h2, spazio, tipi, gradiente, deriva, profilo di pagina, Zipf,
    forma delle parole, verticale;
  - il discriminatore usa coppie di segni innaturali (*o+i*, *o+o*, *e+ch* molto più frequenti) e la
    quota fra le 100 più frequenti (0,33 contro 0,42).
- **Esito: non migliore.**
- **Lettura.**
  - Imporre il profilo di riuso con modifiche **qualsiasi** produce forme non-Voynich e fa perdere le
    proprietà dei segni.
  - Nel Voynich una "variante" non è una modifica a caso: è per lo più uno scambio entro le famiglie
    note (ch/sh, k/t, e/ee, -dy/-ey, ain/aiin, …) o un'altra parola attestata.
  - **Per il voynichizzatore:** l'operatore di variante va costruito sulle sostituzioni osservate fra
    parole vicine della stessa pagina, non sulle modifiche generiche di `generatori.Modifiche`.

## 3/10/2026 — e239: l'operatore di variante del Voynich è diffuso; al generatore mancano proprio le operazioni delle scelte di riga

- **Preregistrato come descrittivo.** Per le 12.990 varianti (classe V dell'e237) si guarda
  l'operazione dalla fonte più recente sulla pagina.
- **Risultati:**
  - Voynich: sostituzioni 53%, inserzioni 29%, cancellazioni 18%. Le prime 10 operazioni coprono il
    20%, le prime 25 il 38%: **operatore diffuso**.
  - Le più frequenti: ±*e* interna (3,9% e 2,8%), ±*q* iniziale, *k*↔*t* interna, +*d* iniziale, ±*o*
    iniziale, *l*↔*r* finale, ±*i* interna, *ch*↔*sh* iniziale.
  - Il generatore "copia e modifica" ha quote simili (57/27/16) e le stesse operazioni principali. Ma
    **non produce mai** sei operazioni frequenti nel Voynich:
    - −*d* interna 1,4%;
    - +*ch* interna 1,2%;
    - +*y* finale 1,2%;
    - −*d* iniziale 1,1%;
    - +*d* interna 1,0%;
    - +*o* interna 1,0%.
  - Sottostima +*e* interna (2,4% contro 3,9%).
- **Lettura.**
  - Le operazioni che mancano al generatore sono proprio i segni facoltativi decisi per riga trovati
    nell'e206b (*d* interna e iniziale, *y* finale, *ch*). È una convergenza fra due esperimenti
    indipendenti.
  - L'operatore `generatori.Modifiche` non sa togliere o aggiungere *d*, *ch*, *y* finale e *o* interna.
  - **Per il voynichizzatore:** l'operatore di variante va preso dalla distribuzione empirica delle
    operazioni (e239), tutte, perché è diffuso. Le operazioni legate alle scelte di riga vanno guidate
    dallo stato della riga (e206b).
  - Spiega anche perché nell'e238 le varianti forzate producevano coppie di segni innaturali.

## 3/10/2026 — e240: con l'operatore di variante empirico la pagella sale a 16/18; il discriminatore resta a 0,91

- **Preregistrato.** Il generatore "copia e modifica" migliore (κ 1, χ 0,2, η 1, spezzature e prefissi)
  con le modifiche estratte dalle 675 operazioni osservate fra varianti della stessa pagina (e239), al
  posto di `generatori.Modifiche`. Quest'ultimo sa solo sostituire e aggiungere o togliere in testa e
  in coda, mai all'interno.
- **Risultati** (semi 2–3):
  - **AUC 0,908**, contro il riferimento 0,889: **non migliore**;
  - **pagella (seme 2): 16/18**, mancano solo ripetizione e verticale. È il punteggio più alto di un
    generatore senza messaggio finora (l'e224 nella ricerca si ferma a 14/18). Riga riprodotta;
  - le operazioni delle varianti generate ora includono +*d* interna, che prima non c'era;
  - profilo di riuso ancora con troppe ripetizioni (R 40%) e poche nuove (N 12%);
  - il discriminatore usa lunghezza, quota delle frequenti, varietà della pagina e alcune coppie di
    segni innaturali create da inserzioni di *e* (*e+ch*, *q+e*, *l+e*).
- **Lettura.**
  - L'operatore empirico avvicina il testo al Voynich sulle proprietà della pagella, ma non sul
    discriminatore.
  - Le inserzioni vanno condizionate al contesto: un *e* si aggiunge accanto a un altro *e*, non dopo
    *q* o *l*. L'operatore empirico usa solo la classe di posizione.
  - Insieme a e237 ed e206b, è la base più promettente per il voynichizzatore:
    - operatore empirico condizionato ai segni vicini;
    - profilo di riuso R/V/N;
    - scelte di riga;
    - spezzature e prefissi staccati.

## 3/10/2026 — e224: la salita per coordinate si ferma a 14/18 in ricerca e 12/18 in verifica

- **Preregistrato.** Salita per coordinate (2 passate) su η, σ, (λ, k), φ, ψ, α, ν, con la pagella
  sul seme 1; verifica sui semi 2–4.
- **Configurazione finale:** η 1, σ 0, λ 1,5 con k 16, φ 0, ψ 0, α 1, ν 0,4.
  - Durante la ricerca:
    - η 1 porta la fine riga (bordo);
    - (1,5, 16) il legame;
    - σ 0,06 dava legame e unioni ma perdeva altro, a parità di punteggio (13/18);
    - ψ e φ 0,2 peggiorano.
- **Verifica: 12/18, riga riprodotta, completo: no.**
  - Mancano h2, uniche, unioni, curva piatta, Zipf, verticale.
  - Fuori pagella: R delle parole rare **51,5** (Voynich 1,96); T4 −14,2 (Voynich −4,0), T3 1,0.
- **Esito: non completo.** La pagella non arriva a 18/18 con questi meccanismi, e la ricerca sul seme 1
  sovrastima: 14 contro 12.
- **Confronto con la notte:**
  - l'e240 (operatore di variante empirico, spezzature e prefissi staccati, κ, χ) dà **16/18** sul seme
    2, una sola misura;
  - gli esperimenti successivi della notte hanno trovato i meccanismi mancanti per unioni e legame
    (e227d), per la verticale (fisica, e228b) e per la forma delle varianti (e239, e240).
  - L'e230 parte ora dalla configurazione dell'e224.

## 3/10/2026 — e241: con l'operatore condizionato ai segni vicini, AUC 0,874 e pagella 16/18 (il miglior generatore della notte)

- **Preregistrato.** Come l'e240, con le 2.432 operazioni di variante contate insieme al segno prima e
  dopo; ripiego sull'operatore dell'e240.
- **Risultati** (semi 2–3):
  - **AUC 0,874** (e240 0,908; riferimento e235 0,889);
  - **pagella 16/18** sul seme 2 (mancano ripetizione e verticale), riga riprodotta;
  - le coppie di segni innaturali (*e+ch*, *q+e*, *l+e*) non sono più fra le caratteristiche
    pesanti.
- **Esito preregistrato: non migliore**, perché la soglia era ≤ 0,839.
- **Che cosa resta:** solo caratteristiche lessicali:
  - varietà della pagina (uniche nella pagina 0,54 contro 0,64; tipi su parole 0,68 contro 0,76);
  - lunghezza media (4,07 contro 4,29) e sua deviazione;
  - concentrazione sulle frequenti (0,41 contro 0,42);
  - profilo di riuso: R 38% contro 32%, N 12% contro 14%.
- **Lettura e programma per il voynichizzatore.** La forma dei segni e delle varianti è a posto (e241).
  Restano due problemi precisi:
  1. **troppe ripetizioni esatte nella pagina** (R): la pagina deve ripetere un terzo, non quasi due
     quinti;
  2. **parole troppo corte**: le spezzature accorciano. Le parole di base non frequenti vanno allungate
     per compensare, senza toccare le frequenti, che sono corte.

## 3/10/2026 — e242: meno ripetizioni e parole rare più lunghe non abbassano l'AUC (compromesso lessicale)

- **Preregistrato.** Sopra l'e241: τ (tema variato) e ℓr (preferenza per le parole lunghe solo fra le
  non frequenti), griglia 2 × 2 sul seme 1.
- **Risultati:**
  - seme 1: 0,880 (partenza), 0,878 (ℓr 1), **0,858** (τ 0,5), 0,864 (τ 0,5 + ℓr 1);
  - verifica della scelta (τ 0,5) sui semi 2–3: **0,879**, contro il riferimento 0,874;
  - τ 0,5 porta le ripetizioni a R 35% (Voynich 32%), ma abbassa la quota delle frequenti (0,40 contro
    0,42) e fa perdere la riga nella pagella (13/18, riga non riprodotta);
  - ℓr 1 da sola corregge lunghezza (4,38), parole uniche (0,13) e forme nuove (N 13,3%), con AUC
    invariata.
- **Esito: non migliore.**
- **Lettura.** Il compromesso fra caratteristiche lessicali resta: ogni correzione locale ne sposta
  un'altra e il discriminatore resta attorno a 0,86–0,88. Per il voynichizzatore conviene comunque:
  - tenere ℓr (corregge lunghezza e forme nuove senza costi);
  - cercare un meccanismo diverso per le ripetizioni, che non tolga peso alle parole frequenti: per
    esempio ripetere meno le parole *di pagina* e non quelle frequenti.

## 3/10/2026 — Bilancio della notte sui generatori (e224–e242)

| generatore | AUC del discriminatore | pagella |
|---|---|---|
| e192 (partenza) | 0,970 | 11/18 |
| e224 finale (η 1, giunture) | — | 12/18 in verifica |
| + spezzature (e232) | 0,918 | — |
| + κ, χ, prefissi (e233/e235) | 0,889 | — |
| + operatore empirico (e240) | 0,908 | 16/18 (1 seme) |
| + operatore condizionato (e241) | **0,874** | **16/18** (1 seme) |
| due fonti (e236) | 0,946 | 10/18 |
| profilo forzato (e238) | 0,987 | 9/18 |

- **Meccanismi acquisiti, ciascuno con un esperimento:**
  - fine riga (η);
  - parole spezzate e prefissi a -l/-r staccati (legame, unioni);
  - copia verticale per posizione fisica;
  - parole frequenti esatte e rare variate (concentrazione);
  - copia della parola precedente (somiglianza fra vicine);
  - operatore di variante empirico condizionato ai segni vicini (forma delle varianti);
  - dodici scelte di riga quasi indipendenti.
- **Ancora non capito:** il modo in cui la pagina riusa le proprie parole. Il bersaglio quantitativo è
  R 32%, V 37%, N 14% (e237), insieme a varietà della pagina e concentrazione sulle frequenti.

## 3/10/2026 — e230: aggiungere i meccanismi alla configurazione dell'e224 non migliora (le giunture erano già rinforzate)

- **Preregistrato.** Varianti sulla configurazione finale dell'e224 (η 1, λ 1,5, k 16), medie sui
  semi 2–4.
- **Validità:** con i meccanismi spenti il testo è identico all'e224.
- **Risultati:**

  | variante | pagella | R parole rare | U/N1 | Q |
  |---|---|---|---|---|
  | V0 e224 | 12/18 | 51,5 | 1,06 | 0,91 |
  | V1 + spezzature σ 0,09 | 10/18 | 57,5 | 1,16 | 0,78 |
  | V2 + lessico per sezione γ 0,05 | 10/18 | 41,3 | 1,18 | 0,79 |
  | V3 + copia verticale fisica | 11/18 | 39,6 | 1,18 | 0,79 |

  - In V1 manca "legame": il legame va **oltre** la banda.
  - Il lessico per sezione abbassa R da 51 a 40, molto lontano da 1,96.
  - La copia fisica recupera l'omogeneità ma non la "verticale".
- **Esito: nessun miglioramento netto.**
- **Lettura.**
  - La configurazione dell'e224 aveva già rafforzato le giunture (λ 1,5, k 16) per compensare il legame
    mancante.
  - Con le spezzature, che danno da sole il legame (e227b), il rinforzo è di troppo e il legame supera
    la banda. I meccanismi vanno combinati con la base adatta: giunture λ 1, come nell'e227d e
    nell'e241, che infatti arriva a 16/18.
  - Il lessico per sezione riduce il raggruppamento delle parole rare, ma di poco: il problema dell'e211
    resta aperto.

## 3/10/2026 — e212: la forza bruta sul testo ripulito non trova letture in 14 lingue

- **Preregistrato.**
  - Ricottura omofonica con 4 ripartenze, 14 lingue, quattro modi: grezzo; ripulito; ripulito con
    gruppi di 20 o 50 fusioni.
  - Posizione del Voynich fra il controllo negativo (generatore, 0) e il positivo (testo vero cifrato,
    1), per il punteggio e per la copertura di parole di almeno 6 lettere.
- **Risultati.**
  - La copertura delle parole lunghe non supera mai 0,14 della distanza fra i controlli.
  - Il punteggio arriva a 0,62 in ebraico e 0,42 in arabo (ripulito, segni EVA), ma con copertura
    0,12–0,13. Il modello di lettere si adatta meglio al Voynich che al generatore, senza che compaiano
    parole vere.
  - I gruppi di fusioni peggiorano quasi ovunque.
- **Esito: nessuna lettura.** Nessuna combinazione raggiunge 0,5 su entrambe le misure.
- **Lettura.**
  - Gli esempi decifrati, nel risultato, sono sequenze senza senso in ogni lingua.
  - Il punteggio relativamente alto in ebraico e arabo, senza parole, ricorda l'e158 ("riconoscimento"
    dell'ebraico anche in testi senza messaggio). Sono lingue con alfabeti senza vocali brevi, in cui un
    modello di lettere si adatta più facilmente.
  - Ora parte da sola la catena e213 → e217 → e218 → e221 → e222 → e219 → e223 → e216 → e212b.

## 3/10/2026 — e213: decifrazione guidata dal contenuto atteso, test non valido

- **Preregistrato.** Una chiave per tutto il testo ripulito; modelli latini per sezione (piante, ricette,
  astronomia); discriminazione fuori campione Δ e z contro il rimescolamento delle sezioni.
- **Risultati:**

  | testo | Δ | z |
  |---|---|---|
  | controllo positivo (latino cifrato) | 0,107 | **1,4** |
  | Voynich ripulito | 0,005 | 6,1 |
  | controllo negativo (generatore) | 0,007 | −0,3 |

- **Esito: test non valido**, perché la validità chiedeva z del positivo > 4.
  - Il controllo positivo si decifra bene ("quamminimumutaturneuedomum…"), ma le sue sezioni non si
    distinguono abbastanza fuori campione.
  - La preregistrazione aveva segnalato il rischio: il testo di ricette usato come controllo è corto e
    ciclico.
- **Lettura, da non sovrainterpretare.**
  - Lo z 6,1 del Voynich, in un test non valido, non vale come segnale.
  - È plausibile che rifletta le differenze di grafia fra sezioni (erbario per lo più in lingua A,
    ricette e biologica in lingua B) più che un contenuto. Gli esempi decifrati sono sequenze senza senso
    (*tumauatinaesesturauis…*).
  - Un e213b con un controllo positivo più lungo e non ciclico, e con le sezioni dentro la stessa lingua
    di Currier, separerebbe le due cose. È da proporre a Davide.

## 3/10/2026 — e217: "una parola = una sillaba" segnala un candidato, con un sospetto di difetto di disegno

- **Preregistrato.** Le parole del Voynich ripulito (le 300 più frequenti) come simboli, le sillabe di
  cinque lingue come lettere (150 unità più "altro"), risolutore omofonico con 3 ripartenze.
- **Risultati** (posizione del Voynich fra negativo 0 e positivo 1):
  - cinese con toni **5,55**;
  - vietnamita **4,19**;
  - giapponese **1,73**;
  - cinese senza toni −18;
  - tailandese −65.
  - Valide 4 lingue su 5 (chiave giusta del positivo ≥ 20%).
- **Esito preregistrato: candidato, da esaminare.**
- **Prima di ogni lettura, il sospetto (scritto prima della verifica).**
  - Una posizione **oltre 1** vuol dire che il Voynich decifrato è "più probabile" del testo vero
    decifrato con la chiave giusta. Una decifrazione vera non lo fa.
  - Il punteggio confrontato è solo quello del modello di lingua, ma i testi hanno distribuzioni dei
    simboli diverse:
    - i controlli sono omofonici, con simboli piatti;
    - il Voynich ha poche parole frequentissime, che il risolutore può mettere sulle unità più
      frequenti, compresa la classe "altro" (i "·" negli esempi: *· shang4 dou1 ye3 ·*).
  - Il Voynich è anche spezzato in segmenti più corti dei controlli.
- **Protocollo:** nessuna lettura. Verifica preregistrata nell'e217b, con 8 ripartenze, il Voynich
  rimescolato, il generatore trattato come il Voynich e metà del testo.

## 3/10/2026 — e217b: il "candidato" sillabico dell'e217 è un artefatto (lo dà anche il Voynich rimescolato)

- **Preregistrato**, secondo il protocollo per i candidati: 8 ripartenze, Voynich rimescolato, generatore
  trattato come il Voynich, chiave su metà delle righe.
- **Risultati** (punteggi; positivo e negativo dall'e217):

  | lingua | positivo | Voynich (8 ripartenze) | Voynich rimescolato | generatore come il Voynich |
  |---|---|---|---|---|
  | cinese con toni | −4,44 | −3,27 | −3,37 | −3,75 |
  | vietnamita | −4,07 | −3,01 | −3,03 | −3,43 |
  | giapponese | −3,76 | −3,46 | **−3,35** | −3,69 |

  - La posizione regge con 8 ripartenze (5,58; 4,37; 1,80).
  - Il calo fuori campione è minore di quello del positivo.
- **Esito preregistrato: artefatto in tutte e tre le lingue**, perché il Voynich non supera il proprio
  rimescolamento.
- **Lettura.**
  - Il punteggio alto viene dalla distribuzione delle frequenze delle parole, non dal loro ordine:
    - rimescolando le parole il punteggio resta lo stesso;
    - anche il generatore senza messaggio, trattato allo stesso modo, batte di molto il testo vero
      cifrato.
  - Una distribuzione molto concentrata si mette sulle unità più frequenti della lingua e "sembra"
    lingua a un modello di trigrammi.
  - Il Voynich supera il generatore di 0,3–0,5: è la sua maggiore concentrazione sulle parole frequenti,
    la stessa vista dal discriminatore (e231–e242).
  - Che il calo fuori campione sia piccolo è coerente: anche le frequenze delle parole generalizzano.
- **Lezione di metodo.** Un confronto di punteggi del modello di lingua fra testi con distribuzioni dei
  simboli diverse non è valido. I test di decifrazione a parole devono avere sempre il controllo "testo
  rimescolato" (e il generatore trattato allo stesso modo) **dentro** il criterio, non solo dopo.

## 3/10/2026 — e218: una chiave che dipende dalla posizione nella parola non dà letture

- **Preregistrato.** Ogni segno cifra in modo diverso a inizio, interno, fine e parola di un segno solo.
  Dieci lingue, testo ripulito.
- **Risultati.**
  - Posizione del modo posizionale (punteggio / copertura delle parole di almeno 6 lettere): in tutte
    le lingue europee la copertura sta fra −0,07 e 0,07.
  - Ebraico 0,66 / 0,46 e arabo 0,52 / 0,11.
- **Esito: nessuna lettura.** Nessuna lingua raggiunge 0,5 su entrambe le misure.
- **Lettura.**
  - L'ebraico è di nuovo il più alto (come nell'e212), ma sotto soglia. Gli esempi decifrati sono
    sequenze senza senso (*תשהחכלישארא…*).
  - Le scritture senza vocali brevi si adattano più facilmente (e158). L'e221 (abjad: il Voynich senza
    i segni "vocalici" a, o, e, y, i) lo mette alla prova direttamente.

## 3/10/2026 — e221: togliere i segni "vocalici" non avvicina il Voynich alle lingue senza vocali

- **Preregistrato.** Il testo ripulito senza a, o, e, y, i (scheletro consonantico) contro ebraico,
  arabo, siriaco e persiano, più latino e italiano.
- **Risultati** (punteggio / copertura): con lo scheletro le posizioni **scendono**:
  - ebraico da 0,70 / 0,25 a 0,28 / 0,00;
  - arabo da 0,52 / 0,29 a −1,14 / −0,10;
  - siriaco 0,05; persiano −0,04; latino −0,39; italiano −0,25.
- **Esito: nessuna lettura.**
- **Lettura.**
  - Il vantaggio relativo dell'ebraico e dell'arabo sul testo intero (e212, e218) non viene da un
    Voynich scritto "come un abjad": togliendo i segni vocalici sparisce.
  - Resta il segno che un modello di lettere per quelle lingue si adatta più facilmente a testi a bassa
    entropia (e158).

## 3/10/2026 — e244: dentro la stessa lingua e sezione, gli scribi non hanno procedimenti distinguibili

- **Preregistrato.** Strada 1 della lista di decifrazione.
  - Caratteristiche del procedimento per pagina: riuso R/V (e237), operatore di variante (e239), le 12
    scelte di riga (e206b).
  - Classificatore delle mani ($H della ZL, scribi di Davis) contro permutazioni dentro gli strati
    lingua × sezione.
- **Risultati** (183 pagine):
  - controllo positivo (lingua A/B dentro la sezione): accuratezza 0,99 contro 0,71, **z 10,3**,
    valido;
  - **mani:** accuratezza 0,789 contro 0,806 del nullo, **z −0,8**.
  - Solo due strati hanno più di una mano: erbario B (scribi 2, 3, 5; 32 pagine) e testo stellare B
    (2, 5).
- **Esito: nessuna differenza oltre lingua e sezione.**
- **Lettura.**
  - Le misure del procedimento distinguono benissimo la lingua A dalla B. Dove si possono confrontare
    mani diverse a parità di lingua e sezione (erbario B), non le distinguono.
  - O gli scribi seguono lo stesso procedimento, o le differenze fra scribi stanno nel tratto (forma dei
    segni, Davis) e non nel modo di comporre.
  - La potenza è limitata (32 pagine in un solo strato utile).
  - Nota tecnica: nel .md le etichette delle mani compaiono come *np.str_*; è solo un difetto di stampa,
    i numeri sono giusti.

## 3/10/2026 — e245: le etichette non richiamano il testo della loro pagina (meno legate di una riga qualsiasi)

- **Preregistrato.** Strada 2 della lista di decifrazione.
  - 696 etichette (loci L, ≥ 2 unità), di cui 199 rare.
  - Legame con i paragrafi della stessa pagina contro quelli di un'altra pagina della stessa sezione.
  - Confronto con il legame di una riga di testo con la sua pagina.
- **Risultati** (R = quota vera / nulla):

  | legame | R etichette | z | R righe di testo |
  |---|---|---|---|
  | esatto | 1,09 | 1,0 | 1,30 |
  | variante | 1,10 | 3,1 | 1,12 |
  | **raro esatto** | **1,24** | **0,6** | **1,82** |

- **Esito: nessun legame.**
- **Lettura.**
  - Un'etichetta non ripete le parole rare del testo della sua pagina più di quelle di un'altra pagina.
    Non c'è il comportamento di un nome che il testo richiama.
  - Le etichette sono anche **meno** legate alla loro pagina di quanto lo sia una riga di testo: la
    loro pagina non fa loro da "serbatoio" come fa con le righe.
  - Si accorda con l'e183, l'e187 (le etichette differiscono solo in lunghezza) e l'e193 (etichette e
    testo circolare simili fra loro). Le etichette sembrano un sistema a parte, scritto con lo stesso
    lessico generale ma non con la pagina sotto gli occhi.

## 3/10/2026 — e248: la prima parola della pagina non si comporta da "titolo"

- **Preregistrato.** Strada 5 della lista di decifrazione.
  - P: prima parola della pagina (207); Q: prime parole degli altri paragrafi (533); L: prime parole
    delle altre righe.
- **Risultati:**
  - **unicità:** P 0,527, Q 0,458 (P/Q 1,15, p 0,055); L 0,175;
  - **ripresa** (ripetizione o variante più avanti nella stessa pagina): P 0,353, Q 0,336. Per P,
    contro un'altra pagina della stessa sezione, 0,285 (z 3,3), cioè il normale legame di pagina;
  - sul corpo senza il gallows iniziale, la ripresa è 0,599 per P e 0,602 per Q.
- **Esito: nessun indizio** (serviva P/Q ≥ 1,3 con p < 0,01 e P più ripresa di Q).
- **Difetto dichiarato.** Nella riga "corpo senza gallows" l'unicità è calcolata sulla parola intera,
  perché il codice non ricalcola le frequenze dei corpi. La ripresa invece usa il corpo. L'esito
  dipende dalla parola intera e non cambia.
- **Lettura.** La prima parola di pagina è un po' più spesso unica delle altre prime di paragrafo, ma è
  ripresa nella pagina allo stesso modo. Non si comporta come il nome di una voce. Si accorda con l'e190
  e l'e211.

## 3/10/2026 — e250: le righe che non copiano e non sono copiate non sono fisicamente diverse

- **Preregistrato.** Strada 7 della lista di decifrazione.
  - Affinità di copia di ogni riga con le 3 righe sopra e sotto: ripetizioni e varianti a distanza 1.
  - Isolate = il 10% più basso per sezione.
  - Scuro dell'inchiostro (e166) e altezza dei riquadri (e34) come z dentro la pagina, contro scelte
    casuali nelle stesse pagine.
- **Risultati** (2.991 righe, 297 isolate):
  - scuro: media |z| 0,825 contro 0,786, **z 1,3**;
  - altezza: 0,661 contro 0,676, **z −0,6**.
- **Esito: nessuna differenza fisica.**
- **Lettura.** Le righe meno legate alle vicine sono scritte con lo stesso inchiostro e la stessa
  grandezza. Non ci sono tracce di aggiunte successive riconoscibili così: la scarsa affinità è
  variazione normale del procedimento, non un altro momento di scrittura.

## 3/10/2026 — e246: nessun messaggio nella sequenza delle modifiche delle varianti

- **Preregistrato.** Strada 3 della lista di decifrazione.
  - Sequenza delle operazioni di variante (25 più frequenti più "altro").
  - S1: informazione mutua fra operazioni consecutive nella riga.
  - S2: informazione mutua fra l'ultima operazione di una riga e la prima della successiva.
- **Risultati:**
  - Voynich: S1 z 0,7, S2 z −1,3;
  - generatore senza messaggio: z −0,2 e 0,5;
  - **controllo positivo** (testo latino nelle stesse posizioni): z 122,6 e 86,9, valido.
  - Il canale porta 2,70 bit per variante, cioè **circa 35.000 bit** al massimo su tutto il
    manoscritto.
- **Esito: nessuna struttura.** La scelta della modifica è indistinguibile da quella di un generatore
  senza messaggio. Un messaggio scritto così si vedrebbe subito.

## 3/10/2026 — e247, e247b, e247c: la scelta della fonte è "a vista", con una correlazione residua fra parole vicine ancora da spiegare

- **e247, preregistrato.** Strada 4: scarto orizzontale Δ fra parola e fonte nella riga sopra, sui
  riquadri.
  - **M1:** mediana |Δ| 1,88 passi di parola contro 2,60 a caso (z −20). La fonte è molto vicina:
    copia a vista.
  - **M2:** Δ consecutivi correlati, 0,335 contro 0,091 (z 21).
  - Esito: struttura da esaminare.
- **e247b, preregistrato.**
  - Parole consecutive copiano parole consecutive della riga sopra (passo +1) più del caso: 13,1%
    contro 10,7%, z 4,2.
  - La correlazione resta anche fuori da quelle coppie: 0,196 contro 0,069, z 5,7.
- **e247c, preregistrato.** Togliendo lo slittamento della riga (mediana dei Δ delle altre coppie) la
  correlazione resta: 0,420 contro 0,288, z 4,2. Esito: struttura non spiegata, da esaminare.
- **Lettura provvisoria.** Prima di pensare a una scelta intenzionale c'è un'altra spiegazione
  meccanica da escludere: la **geometria locale**. Due parole vicine stanno sotto lo stesso tratto della
  riga sopra; la fonte più vicina dipende da come sono spaziate lì le parole, qualunque sia il loro
  contenuto. Il rimescolamento dei Δ dentro la riga rompe questa dipendenza e quindi non è il nullo
  giusto. L'e247d usa un nullo che conserva la geometria e cambia solo le parole.

## 3/10/2026 — e258: le etichette sono un sistema a parte (si copiano fra loro, lessico in buona parte proprio)

- **Preregistrato.** 1.078 parole-etichetta (loci L, ≥ 2 unità) su 55 pagine.
- **Risultati:**
  - **M1:** un'etichetta ha una ripetizione o variante fra le **altre etichette della stessa pagina** nel
    34,5% dei casi, contro il 13,4% con una pagina a caso della stessa sezione (**z 10,6**). Con le
    etichette delle **pagine vicine** (±2) 38,1% contro 29,6% (**z 6,3**);
  - **M2:** solo il **57%** delle parole-etichetta compare nei paragrafi, contro l'**85%** di un campione
    di parole di paragrafo della stessa sezione (**z −25,9**).
- **Esito: sistema a parte.**
- **Lettura.**
  - Le etichette non prendono dal testo della loro pagina (e245), ma si copiano fra loro, sulla stessa
    pagina e su quelle vicine, e usano un lessico in buona parte proprio.
  - È lo stesso procedimento di copia e variante applicato a un secondo "flusso" di parole: le etichette
    di una pagina sono scritte guardando le altre etichette, non i paragrafi.
  - Per il voynichizzatore: le etichette vanno generate con un modulo a parte, con un proprio lessico e
    la copia dalle etichette vicine.

## 3/10/2026 — e255: nessuna copia attraverso il cambio di pagina; ogni pagina riparte da capo

- **Preregistrato.** D = somiglianza delle prime 3 righe di p con le **ultime** 3 di q, meno quella con le
  **prime** 3 di q.
- **Risultati** (z contro pagine a caso della stessa sezione e mano):
  - precedente nella rilegatura D −0,026 (z 1,7);
  - successiva −0,061 (z −1,5);
  - a fronte, per i versi, −0,039 (z 0,4);
  - recto dello stesso foglio −0,017 (z 1,6).
- **Esito: nessuna copia attraverso la pagina.**
- **Lettura.**
  - L'inizio di una pagina non riprende la fine della pagina precedente né quella a fronte. Anzi, tutte
    le D sono negative: le prime righe di una pagina somigliano di più alle prime righe delle altre
    pagine, perché gli inizi di paragrafo hanno un lessico proprio.
  - La copia a vista lavora dentro la pagina. A ogni pagina nuova si riparte, come ripartono le
    abitudini di grafia (e145).
  - Per la ricostruzione dell'ordine dei bifogli il passaggio di pagina non dà informazione.

## 3/10/2026 — e260: neanche misure fisiche grossolane della scrittura distinguono gli scribi a parità di lingua e sezione

- **Preregistrato.** Misure per pagina dai riquadri: passo di riga, spazio fra parole, larghezza per unità
  (tutte divise per l'altezza), inclinazione delle righe, variabilità dell'altezza. Classificatore delle
  mani contro permutazioni dentro lingua × sezione, come l'e244.
- **Risultati** (181 pagine):
  - controllo (lingua A/B dentro la sezione): 0,737 contro 0,576, **z 4,8**;
  - **mani:** 0,634 contro 0,622, **z 0,7**.
  - Medie per mano simili. La mano 2 ha un'inclinazione media più alta (0,116), probabilmente per poche
    pagine con righe mal riconosciute.
- **Esito: nessuna differenza oltre lingua e sezione.**
- **Lettura.**
  - Insieme all'e244: dove si possono confrontare (erbario B), gli scribi di Davis non si distinguono né
    per come compongono né per spaziatura, altezza e passo di riga.
  - Le differenze che Davis vede sono nella forma fine dei segni, che qui non misuriamo.
  - Le lingue A e B differiscono anche fisicamente, a parità di sezione.

## 3/10/2026 — e259: con questo modello il Voynich porta ~11 bit per parola, come una Bibbia; ma il suo modello migliore è quasi solo "di lettere"

- **Preregistrato.**
  - Mistura di quattro componenti: bigramma di parole con modello di lettere per le parole nuove; cache
    esatta delle ultime 3 righe; cache di varianti a distanza 1 (uniforme sui vicini, approssimazione
    dichiarata); modello di lettere da solo.
  - Pesi per EM; addestramento sulle unità pari, misura sulle dispari.
- **Risultati** (bit per parola, base → mistura; pesi base / cache / varianti / lettere):
  - **Voynich 11,26 → 11,22**; pesi 0,09 / 0,06 / 0,01 / **0,85**;
  - Bibbia latina 11,55 → 11,33 (0,77 / 0,07 / 0 / 0,15);
  - Bibbia italiana 10,28 → 10,13;
  - Plinio 15,73 → 15,65;
  - *Macer* 14,07 → 14,03.
- **Esito preregistrato: informazione per parola paragonabile a una lingua.**
  - Il Voynich non sta sotto i due terzi del minimo, e la cache non gli toglie più che alle lingue.
  - L'operativizzazione di "molto più", cioè una riduzione almeno doppia, è stata fissata scrivendo il
    codice, prima dei risultati.
- **Lettura, con due fatti da non perdere.**
  1. **Per il Voynich il modello migliore è quasi solo il modello di lettere** (peso 0,85; nelle lingue
     il bigramma di parole pesa circa 0,8). Le parole del Voynich si prevedono bene dalle loro lettere e
     poco dalla parola precedente: è di nuovo l'assenza di sintassi (e114, e115) vista da un'altra parte.
     Gli 11 bit per parola vengono soprattutto dall'incertezza sulle lettere, non da un vocabolario
     ricco.
  2. **La cache aiuta pochissimo (0,05 bit)**, anche se due parole su tre sono copie o varianti
     (e237). Le ripetizioni riguardano parole già facili, e la cache di varianti uniforme su centinaia di
     vicini è troppo debole per costruzione. Il numero è quindi un limite superiore largo.
  - L'e259b userà una cache di varianti pesata con il modello di lettere, per misurare quanto il
    procedimento riduce davvero l'informazione.

## 3/10/2026 — e259b: anche con una cache di varianti realistica il Voynich porta ~11 bit per parola; la pagina conta nei segni

- **Preregistrato.** Come l'e259, con la cache di varianti pesata dal modello di lettere e un modello di
  lettere della pagina, interpolato al 50% con quello generale.
- **Risultati** (bit per parola: base → + cache → + lettere della pagina; pesi della mistura completa):
  - **Voynich 11,26 → 11,16 → 10,99** (riduzione 0,27); pesi base 0,05, cache 0,01, **varianti 0,06**,
    lettere 0,08, **lettere della pagina 0,79**;
  - Bibbia latina 11,55 → 11,25 (0,30); Bibbia italiana 10,28 → 10,09 (0,19); Plinio 15,73 → 15,58;
    *Macer* 14,07 → 13,92;
  - nelle lingue il peso delle varianti è 0,00 e quello delle lettere della pagina circa 0,07.
- **Esito preregistrato: informazione per parola paragonabile a una lingua.**
- **Lettura.**
  - Copiare e variare non rende il testo povero di informazione. Se scegliere quale parola copiare e
    quale modifica fare fosse libero, costerebbe circa quanto scrivere una parola nuova: circa 11 bit per
    parola, per un totale di circa 380.000 bit.
  - È un limite superiore molto più largo del tetto dei soli canali "liberi" noti (circa 93.000 bit,
    e210b). Dice che, misurato così, il Voynich non è troppo prevedibile per portare un testo; non dice
    che lo porti.
  - È proprio del Voynich, rispetto alle lingue, che:
    - le parole si prevedano dalle **lettere della pagina** (peso 0,79 contro circa 0,07);
    - si usi la **cache di varianti**.

    L'omogeneità di pagina sta nei segni, ed è la firma del procedimento di copia e variante.

## 3/10/2026 — e247d: la correlazione degli scarti è geometria; la scelta della fonte è a vista, senza canale nascosto

- **Preregistrato.**
  - Nullo che conserva posizioni e riga sopra e sostituisce le parole di ogni riga con parole di altre
    righe della stessa pagina.
  - Coppie consecutive non a passo 0 o +1: 1.294.
- **Risultato:** correlazione dei Δ 0,196 contro **0,198** del nullo geometrico (z −0,1).
- **Esito: geometria.**
- **Bilancio della strada 4 (e247–e247d).**
  - La fonte di una ripetizione o variante è la parola fisicamente vicina sopra (copia a vista, e228).
  - Parole consecutive copiano un po' più spesso parole consecutive della riga sopra (passo +1, z 4,2).
  - Tutta la correlazione restante fra gli scarti viene dalla disposizione delle parole sulla riga
    sopra, non da una scelta.
  - Nessuno spazio per un messaggio nella scelta della fonte oltre quello di un procedimento meccanico.
  - Lezione di metodo: il rimescolamento dentro la riga non era il nullo giusto, perché rompe la
    geometria. Lo era il nullo geometrico.

## 3/10/2026 — Interruzione: il computer si è spento; esperimenti rilanciati da capo

- Lo spegnimento ha interrotto e243 (dopo la taratura, prima della verifica), e249, e256, e257 ed e222.
  Nessun commit è stato rovinato.
- Sono rilanciati da capo con gli stessi semi, in tre file parallele:
  - e243, poi e257;
  - e256;
  - e249, poi la catena e222 → e219 → e223 → e216 → e212b.

  Il codice non è cambiato. Le prove sono deterministiche, quindi i risultati sono quelli che si
  sarebbero avuti senza interruzione.
- I log parziali dei tentativi interrotti sono sovrascritti dai nuovi. Le righe già stampate prima
  dello spegnimento (taratura dell'e243, parte Voynich dell'e256) devono ricomparire identiche: è un
  controllo di riproducibilità.

## 3/10/2026 — e256: nessuna deriva direzionale nelle genealogie (un indizio sotto soglia sulla *d* interna)

- **Preregistrato.** Squilibrio fra operazioni inverse lungo la scrittura (fonte più in alto, variante
  più in basso), contro righe rimescolate nella pagina; 66 coppie con almeno 50 occorrenze.
- **Risultati:**
  - solo 2 coppie con |z| > 3:
    - +*d* / −*d* interna: squilibrio −0,170 contro −0,005, z −3,4;
    - *d*→*e* / *e*→*d* interna: +0,341 contro +0,129, z 3,2;
  - il generatore, che usa la stessa misura, non ha nessuna coppia oltre |z| 2.
- **Esito preregistrato: nessuna deriva direzionale** (servivano almeno 3 coppie).
- **Indizio sotto soglia.** Le due coppie vanno nella stessa direzione: scendendo nella pagina le varianti
  **perdono la *d* interna** o la cambiano in *e* (*chedy* → *chey*) più del contrario. È coerente con la
  scelta -dy/-ey (F7), ma con 66 coppie provate non basta.
- **Difetto dichiarato.** L'oscillazione (w3 = w1) vale 0 per costruzione nel Voynich e nel generatore.
  Un ritorno alla forma di partenza è già presente sulla pagina e viene classificato come ripetizione,
  non come variante. La misura non è informativa.

## 3/10/2026 — e261: i generatori hanno già l'"ortografia di pagina" del Voynich

- **Preregistrato.** La mistura dell'e259b applicata ai generatori.
- **Risultati** (peso delle lettere della pagina; bit per parola):
  - Voynich 0,79 (10,99);
  - **generatore e241 0,73 (10,81)**;
  - generatore e192 0,64 (11,21).
- **Esito: presente** per entrambi, almeno la metà del peso del Voynich.
- **Lettura.**
  - Il serbatoio di pagina dei generatori produce già la preferenza di segni per pagina. Non serve un
    meccanismo nuovo: l'idea 5 della lista di oggi cade.
  - Il generatore "copia e modifica" ha quasi lo stesso contenuto d'informazione per parola del Voynich.

## 3/10/2026 — e262, e263, e265: zodiaco non ordinale, etichette copiate dalla vicina, anelli con un inizio

- **e262, preregistrato.** Le etichette dello zodiaco (Lz) nella stessa posizione di segni diversi.
  - 10 sequenze da 30: Ariete e Toro uniti dalle due metà.
  - Δ (stessa posizione − posizioni diverse): per indice +0,004 (z 1,3); con spostamento ciclico
    +0,050 contro +0,050 (z −0,4).
  - **Esito: nessun ordine comune.** Le etichette non si comportano da ordinali (giorni o gradi).
- **e263, preregistrato.** Etichette consecutive sulla stessa pagina (971 su 45 pagine).
  - **M1:** a distanza 1 il 9,4% delle coppie, contro il 6,0% (z 7,5).
  - **M2:** stessa modifica lungo la serie in 0 casi su 56. Anche il nullo è 0, quindi la misura non è
    informativa.
  - **Esito: etichette vicine simili ma senza serie.** È la copia dall'etichetta accanto, come nell'e258,
    non un'enumerazione.
- **e265, preregistrato.** 81 anelli di testo circolare (Cc).
  - Giuntura di chiusura (ultima → prima) −0,230 contro −0,236 del nullo (z 0,1). Le giunture fra
    parole vicine valgono +0,018.
  - **Esito: inizio marcato.** La chiusura dell'anello ha il legame di due parole a caso: gli anelli hanno
    un inizio e una fine, come una riga scritta in cerchio. Potenza limitata.
- **Lettura comune.** Nelle aree "illustrate" (zodiaco, etichette, anelli) vale lo stesso procedimento
  del testo:
  - copia dalla parola vicina;
  - un inizio e una fine come una riga.

  Non compaiono strutture da contenuto (ordinali, serie numeriche, testo circolare continuo).

## 3/10/2026 — e264: nessuna chiave che cambia a ogni pagina

- **Preregistrato.** Per ogni pagina la migliore delle 64 combinazioni di scambi (ch↔sh, k↔t, p↔f,
  ckh↔cth, cph↔cfh, l↔r). Guadagno = aumento della quota di parole attestate nel resto del testo.
- **Risultati** (guadagno medio):
  - Voynich **0,0103**;
  - generatore senza chiave (e241) 0,0117;
  - generatore con chiave di pagina a caso **0,0255**.
  - Mann-Whitney: positivo > negativo p = 1,9·10⁻¹⁵ (valido); Voynich > negativo **p = 0,56**.
- **Esito: nessuna chiave di pagina.**
- **Lettura.** Una chiave diversa per pagina, fatta di scambi fra segni simili, si vedrebbe chiaramente.
  Il Voynich si comporta come un testo con sole abitudini di pagina. Le differenze di grafia fra pagine
  sono abitudini, non chiavi.

## 3/10/2026 — e266: un discriminatore più forte (AUC 0,937 sul miglior generatore) e due proprietà nuove

- **Preregistrato.** Le caratteristiche dell'e231 più quattro gruppi:
  - G6: coppie di parole;
  - G7: posizione nella riga;
  - G8: prime righe di paragrafo;
  - G9: ortografia di pagina.
- **Controlli:** A contro B 1,000; etichette a caso 0,519 (valido).
- **Risultati:**
  - generatore e192: **0,985**;
  - generatore "copia e modifica" e241: **0,937**, contro 0,874 dell'e231.
  - AUC per gruppo contro l'e241: G8 **0,874**, G6 0,805, G7 0,682, G9 0,661.
- **Esito: più forte.**
- **Proprietà nuove che il generatore non ha** (caratteristiche più pesanti):
  - **prime righe di paragrafo:** nel Voynich la prima riga ha molti più *p* e *f* delle altre righe
    (+3,3% e +1,0% contro +1,2% e +0,2% nel generatore) e parole più lunghe (4,63 contro 4,18). Il
    generatore tratta in modo speciale solo la prima parola;
  - **parole ripetute subito:** il generatore scrive due volte di fila la stessa parola nel 2,3% delle
    coppie, il Voynich nell'1,0%. Il modulo di riuso copia troppo spesso la parola appena scritta;
  - restano la varietà della pagina e la deviazione della lunghezza.
- **Per il piano:**
  - e268 (prime righe) diventa prioritario;
  - nel modulo di riuso la fonte "stessa riga" deve escludere, o rendere rara, la parola immediatamente
    precedente.

## 3/10/2026 — Limite dei processi in background; e243 fallisce già al primo seme

- **Infrastruttura.** Dopo il riavvio i processi in background dell'ambiente vengono fermati dopo circa
  30 minuti. Così si sono interrotti e243 (dopo il primo seme di verifica) ed e249.
  - D'ora in poi le code lunghe girano **staccate** (`scratchpad/coda.sh`, file di stato
    `stato_code.txt`).
  - Un monitor, riarmato ogni 30 minuti, segnala gli esperimenti conclusi.
  - Rilanciati da capo:
    - coda A: e243, e257;
    - coda B: e249, e222, e219, e223, e216, e212b;
    - coda C: e270.
- **e243 (passo 1 del piano), seme 7, prima dell'interruzione:**
  - pagella **8/18**, AUC **0,975**, R delle parole rare **87,5**;
  - profilo di riuso giusto (R 32%, V 41%, N 12%);
  - mancano h2, spazio, uniche, tipi, ripetizione, gradiente, unioni, deriva, Zipf, formule.
  - Con una media richiesta di 17/18 il passo **non può** essere superato. Lo si completa comunque per
    avere tutti i numeri.
- **Diagnosi.**
  - Il generatore dell'e243 copia e varia soprattutto **le proprie righe** generate, con varianti
    sempre forzate, e si allontana dal vocabolario del Voynich.
  - Il generatore "copia e modifica" (e241, 16/18) pesca invece dal vocabolario vero della pagina e lo
    varia.
  - Il profilo di riuso giusto non basta: le copie devono poggiare su parole vere.
- **Come previsto dal piano**, il passo 1 si rifà una volta (e243b), partendo dall'e241 e aggiungendo
  solo ciò che manca:
  - copia dalle righe sopra per posizione fisica, con le distanze del Voynich;
  - niente ripetizione immediata;
  - parole rare più lunghe.

## 3/10/2026 — e271, e272: i gallows iniziali non sono capilettera, e la -m a fine riga non è un'abbreviazione

- **e271, preregistrato.** Togliendo il primo segno si ottiene una parola attestata (corpo attestato),
  contro l'atteso a parità di lunghezza del corpo per le parole che cominciano con un segno non gallows:
  - *p*/*f* nelle prime righe: 0,757 contro 0,751 (**O/A 1,01**, z 0,3);
  - *p*/*f* nelle altre righe: 1,11 (z 2,6);
  - *t*/*k*: 0,95 (z −4,4).
  - **Esito: nessun indizio.** I gallows delle prime righe non sono decorazioni aggiunte a parole normali.
  - Fatto generale: tre parole su quattro, tolto il primo segno, sono ancora parole attestate.
    È la struttura "a incastro" del lessico.
- **e272, preregistrato.** Parole in *-m*: quota di tronchi "completabili" (inizio di una parola
  frequente più lunga):
  - **a fine riga 0,637 contro 0,698 all'interno**, rapporto **0,91** (p 0,97);
  - controllo *-y*: 0,98.
  - **Esito: nessun indizio.** La *-m* finale di riga non si comporta come un segno di abbreviazione
    del copista: è una regola di fine riga del procedimento (e71, e78), non una troncatura per stare nel
    margine.

## 3/10/2026 — e273: le prime righe dei paragrafi sono un registro a parte ("intestazioni")

- **Preregistrato.** 659 paragrafi con almeno 3 righe.
  - D1 = somiglianza della prima riga con le prime righe di 5 paragrafi della stessa sezione, meno
    quella con il resto del proprio paragrafo.
  - D2 = lo stesso per la seconda riga.
- **Risultati:**
  - D1 −0,015; D2 −0,062;
  - **D1 − D2 = +0,047** (errore standard 0,010, **z 4,7**).
- **Esito: registro di intestazione.**
- **Parole tipiche delle prime righe** (rapporto di frequenza rispetto al resto):
  - erbario: *opchy, pchor, opchey, opchol, qopchy*;
  - ricette e stelle: *pchedy, qopchedy, opal, qopchey*;
  - biologica: *opchedy, qopshedy, ofchedy*.
- **Lettura.**
  - Le prime righe hanno un lessico comune fra paragrafi della stessa sezione, fatto soprattutto di forme
    con *p*/*f* e prefissi *o-*/*qo-* (*opch-*, *qopch-*).
  - È un "registro di apertura", come le formule d'inizio delle voci di un erbario o di un ricettario,
    oppure un'abitudine grafica d'inizio paragrafo.
  - L'e271 dice che il gallows non è una decorazione aggiunta a parole normali: sono parole proprie
    dell'apertura.
  - **Per il generatore (e268):** le prime righe vanno generate da un lessico d'apertura per sezione, non
    solo con la prima parola speciale.

## 3/10/2026 — e277: le parole più frequenti del Voynich sono sparse fra le pagine come le parole grammaticali delle lingue

- **Preregistrato.** Dispersione di Juilland D (1 = uniforme) delle 100 parole più frequenti e delle parole
  di frequenza 5–20.
- **Risultati** (D prime 100 / D frequenza 5–20 / rapporto):
  - Voynich, tutte le pagine: 0,852 / 0,570 / 1,49;
  - **Voynich, erbario: 0,801** / 0,614 / 1,30;
  - Bibbia latina 0,867 / 0,596 / 1,46; Bibbia italiana 0,888 / 0,594 / 1,49;
  - Plinio 0,868 / 0,627 / 1,38; *Macer* 0,769 / 0,563 / 1,37.
- **Esito: come parole grammaticali.** L'erbario sta dentro l'intervallo dei testi veri, 0,769–0,888.
- **Lettura, con una cautela.**
  - Le parole frequenti del Voynich sono distribuite uniformemente fra le pagine, e le parole medie a
    grappoli, nella stessa proporzione delle lingue. È compatibile con un sistema "parole funzione + parole
    di contenuto".
  - La prova però **non distingue** una lingua da un procedimento: qualunque testo fatto da un fondo di
    parole comuni del libro più varianti locali ha questa proprietà, e i nostri generatori la costruiscono
    per costruzione (serbatoi globali più pagine).
  - Il dato utile è un altro: le frequenti del Voynich **non** sono legate alla sezione più di quanto
    accada nelle lingue, almeno nell'erbario.

## 3/10/2026 — e278: le aperture dei paragrafi non sono formule fisse (sono quasi sempre uniche)

- **Preregistrato.** Coppie (prima, seconda parola) delle prime righe di paragrafo (740) contro le stesse
  posizioni nelle altre righe (3.363), ripetute in un altro paragrafo o riga della stessa sezione.
- **Risultati:**
  - esatte: aperture **0,5%**, riferimento **5,5%** (rapporto 0,10);
  - con varianti: **10,8%** contro **47,1%** (rapporto 0,23);
  - solo due coppie d'apertura ripetute: *tshor shey* (erbario) e *polor sheedy* (stelle).
- **Esito: nessuna formula.** Anzi, le aperture si ripetono molto meno delle altre righe.
- **Difetto dichiarato.**
  - Il gruppo di riferimento è 4,5 volte più grande. In un gruppo più grande è più facile trovare una
    coppia ripetuta, quindi il confronto non è a parità di dimensione.
  - Lo scarto osservato (10 volte) è molto più grande di quanto questo spieghi plausibilmente, ma una
    conferma con sottocampioni della stessa dimensione (e278b) sarebbe pulita.
- **Lettura.**
  - Il "registro d'apertura" dell'e273 è fatto di **forme simili** (*opch-*, *qopch-*, *pch-*), non di
    frasi ripetute.
  - Ogni paragrafo si apre con una parola propria, quasi sempre unica (e248: 53% di parole d'apertura
    uniche), costruita con il repertorio d'apertura.
  - Non c'è l'appiglio di una formula fissa su cui tentare una lettura.

## 3/10/2026 — e274: i punti imprevedibili del testo non formano gruppi

- **Preregistrato.** La sorpresa di ogni parola è calcolata con la mistura dell'e259b, fuori campione
  (pagine pari contro dispari). Il residuo toglie l'effetto di lunghezza e posizione. G è la quota di
  coppie vicine entrambe nel 10% più sorprendente; il nullo sono 500 rimescolamenti nella riga.
- **Risultati:**
  - Voynich: sorpresa media 11,04 bit, G 0,0140 contro un nullo di 0,0134, **z 1,2**;
  - generatore e241 (controllo negativo): 10,82 bit, z 3,0;
  - Voynich con frammenti di Plinio (controllo positivo): 12,44 bit, **z 9,8**.
- **Validità:** il positivo supera z 3.
- **Esito: nessun raggruppamento.** Il Voynich è anzi meno raggruppato del generatore senza messaggio.
- **Lettura.**
  - Non ci sono "isole" di testo diverso dentro le righe, come lascerebbe un messaggio inserito in poche
    parole (per esempio parole in chiaro in mezzo a riempitivo).
  - Il modello di copia lascia ~11 bit per parola, e questa sorpresa è sparsa in modo uniforme.
  - Il generatore e241 raggruppa un poco le sue sorprese, il Voynich no: è una piccola differenza in più
    da chiudere per il generatore (le varianti difficili del generatore arrivano a coppie).

## 3/10/2026 — e243b: passo 1 del piano 18/18 rifatto, non superato. Lacuna dichiarata

- **Preregistrato.** Generatore dell'e242 (e241 + ℓr 1) con:
  - copia verticale fisica a distanza d, presa dalle distanze del Voynich;
  - penalità 0,3 per la ripetizione immediata;
  - φ scelto sul seme 1 con l'AUC dell'e266: 0,10, contro 0,946 / 0,959 per φ 0,25.
- **Validità:** con φ 0 e senza penalità coincide con l'e242.
- **Verifica sui semi 7, 8, 9:**
  - pagella 16, 16 e 15 su 18, media **15,7**; la riga non è riprodotta nel seme 8;
  - AUC dell'e231 0,876 / 0,888 / 0,871, media **0,878**;
  - AUC dell'e266 media **0,947**.
  - Riferimento e241: 16/18, AUC 0,874 e 0,937.
- **Esito: non superato.**
  - Il criterio chiedeva pagella ≥ 17, riga in tutti i semi e AUC dell'e231 ≤ 0,85.
  - È il secondo tentativo (dopo l'e243), quindi per la regola del piano si **dichiara la lacuna** del
    passo 1 e si prosegue con la configurazione migliore, cioè **e241**.
- **Che cosa ha fatto la copia a distanza:**
  - il profilo di riuso si sposta un poco verso il Voynich (R 36,7% contro 31,9%, V 35,5% contro
    37,5%, N 13,6% contro 14,3%);
  - le ripetizioni immediate vanno a posto (0,92–0,99% contro 0,97%);
  - ma le **parole rare** restano riusate troppo: R 49–57 contro 1,96 del Voynich. È il difetto più
    grande rimasto.
- **Che cosa usa il discriminatore** (seme 7). Nel generatore rispetto al Voynich:
  - lunghezze delle parole più disperse (deviazione 1,75 contro 1,58);
  - meno parole fra le 100 più frequenti (0,397 contro 0,424);
  - meno parole uniche nella pagina (0,553 contro 0,636);
  - meno tipi per parola (0,689 contro 0,756);
  - meno somiglianza fra parole vicine (0,193 contro 0,218).
- **Lettura.**
  - Il generatore ripete le stesse parole rare nella pagina, mentre il Voynich, nella pagina, usa
    **più parole diverse e più frequenti**, e le vicine si somigliano di più.
  - È la direzione per il passo 2 (e251, lessico che circola) e per il ciclo avversario: varianti nuove
    invece di copie esatte delle rare, e lunghezze meno disperse.

## 3/10/2026 — e243: passo 1 del piano 18/18, primo tentativo, non superato

- **Preregistrato.** Generatore con riuso esplicito autoreferenziale. Le quote di classe sono tarate
  sull'uscita (seme 1): R 0,337, V 0,230, F 0,128, A 0,147, N 0,158.
- **Verifica sui semi 7, 8, 9:**
  - pagella 8, 8 e 10 su 18;
  - AUC del discriminatore 0,975 / 0,980 / 0,973;
  - R delle parole rare 80–91, contro 1,96 del Voynich.
- **Esito: non superato.** Il profilo di riuso è giusto (R 31–32%, contro 31,9%), ma il testo si allontana
  dal vocabolario del Voynich:
  - parole più lunghe (4,9 contro 4,5) e più disperse in lunghezza;
  - meno parole frequenti;
  - h2, Zipf, deriva e gradiente persi.
- **Lettura.** Copiare dal proprio testo già generato fa deriva. Per questo il passo è stato rifatto
  sopra il vocabolario vero (e243b, anch'esso non superato, vedi sopra): da qui la lacuna dichiarata del
  passo 1.
- Registrato dopo l'e243b perché finito dopo: la coda è stata fermata per il trasloco e l'e257 passa al
  nuovo PC.

## 3/10/2026 — Trasloco sul nuovo PC: e277 ed e278 rieseguiti, risultati identici

- **Nuovo PC:**
  - Intel Core i5-12600K (10 core, 16 thread), 32 GB, Windows 11 (10.0.26200);
  - Python 3.12.10 e i 25 pacchetti di `requirements.txt` alle versioni fissate (numpy 2.5.3, scipy
    1.18.1, scikit-learn 1.9.1), controllati uno per uno con `pip freeze`;
  - JDK non ancora installato: serve solo per e22–e24.
- **Dati.** `dati/cache` è **copiato dal vecchio PC** (`voynich_cache.zip`), non riscaricato con
  `prepara.py`:
  - 19.705 file, 2,14 GB;
  - CRC dello zip verificati;
  - file estratti confrontati uno per uno con lo zip: nessuno manca, nessuna dimensione diversa.
- **Verifica:** e277 ed e278 rieseguiti con `esegui.py` al commit 96a7c86.
  - I `.json` e i `.md` dei risultati sono **identici byte per byte** a quelli committati.
  - Nella provenienza coincidono le impronte dei dati, l'impronta dello script, Python e le versioni dei
    pacchetti.
  - Cambiano solo:
    - piattaforma: Windows 11 invece di Windows 10;
    - commit;
    - JDK assente;
    - durata: 1,2 s contro 13,5 s per e277, 2,5 s contro 43,2 s per e278.
- La provenienza di e277 ed e278 in `risultati/provenienza/` è ora quella della corsa sul nuovo PC.
  Quella del vecchio PC resta nei commit 5b52165 e 703cec1.
- **Esito: trasloco verificato.** Il nuovo PC prende gli esperimenti non ancora partiti (vedi
  `STATO_LAVORI.md`).

## 3/10/2026 — e257: le righe gemelle ci sono, ma il generatore e241 ne fa altrettante

- **Preregistrato.**
  - G è la catena più lunga di corrispondenze (uguali o a distanza 1) nello stesso ordine fra una riga e
    quella sopra, divisa per le parole della riga. La riga è gemella se G ≥ 0,5.
  - Nullo: la riga sopra presa da un'altra pagina della stessa sezione, 200 repliche.
  - Riferimento: generatore e241, seme 2.
- **Risultati:**
  - Voynich: 3.589 coppie di righe, G medio 0,193, righe gemelle **2,7%** contro 1,3% del nullo (z 8,0);
  - generatore e241: G medio 0,215, righe gemelle **3,1%** contro 1,2% (z 11,0);
  - nel Voynich G sta quasi sempre fra 0 e 0,4 (il valore più comune è 0,2).
- **Esito: nessun eccesso.** L'eccesso sul nullo c'è, ma il criterio chiedeva anche almeno 1,5 volte il
  generatore: il Voynich ne ha 0,86 volte.
- **Lettura.**
  - Non serve un meccanismo in più di copia "in ordine" della riga sopra. La copia "a vista" con
    modifiche, già nel generatore, basta a produrre le righe gemelle che si vedono, anzi un poco di più.
  - È coerente con e247b–e247d.
- Prima esecuzione completata sul nuovo PC: 316 s.

## 3/10/2026 — e223: decifrazione guidata dal contenuto in cinque volgari; il tedesco segnala un candidato debole

- **Preregistrato.** Come l'e213 (una chiave, modelli di lingua per sezione, stima sulle pagine pari e
  verifica sulle dispari), con corpora di dominio in italiano, tedesco, francese, spagnolo e catalano.
- **Risultati** (z della discriminazione fra sezioni fuori campione):

  | lingua | positivo | Voynich | generatore |
  |---|---|---|---|
  | italiano | 8,8 | 1,6 | −2,0 |
  | tedesco | 8,2 | **4,2** | −1,8 |
  | francese | 9,5 | −0,7 | −1,0 |
  | spagnolo | 7,0 | 3,5 | **4,4** |
  | catalano | 10,1 | −4,2 | −3,4 |

  - Il test è valido in tutte e cinque le lingue (positivo > 4).
- **Esito preregistrato:**
  - tedesco: **lettura di dominio, da esaminare** (Voynich z > 4 e almeno 3 sopra il generatore);
  - le altre quattro lingue: nessuna lettura.
- **Prima di ogni lettura, i sospetti (scritti prima della verifica).**
  - Il **controllo negativo spagnolo**, cioè il generatore, che non contiene alcun messaggio, arriva a
    z 4,4. Quindi z > 4 si raggiunge anche senza contenuto, e la soglia non protegge abbastanza.
  - Nel tedesco il Δ del Voynich è −0,0008: lo z è positivo solo perché il nullo è più basso (−0,0058).
    Il positivo ha Δ 0,12, cioè un effetto 150 volte più grande.
  - Gli esempi decifrati non contengono parole tedesche (*nsdisimacherernstisarjaral*).
  - Le lingue provate sono cinque: con cinque prove un superamento isolato della soglia è più
    probabile.
- **Protocollo:** nessuna lettura. Si fa la verifica per i candidati, come nell'e217b, da preregistrare
  nell'e223b:
  - 8 ripartenze;
  - Voynich rimescolato;
  - generatore trattato come il Voynich, con più semi;
  - chiave su metà delle righe.
- Prima esecuzione sul nuovo PC: 500 s.

## 3/10/2026 — e269: decifrazione sulle sole parole non copiate, nessuna lettura

- **Preregistrato.** Se il messaggio sta nelle parole "nuove" (classi N e A del profilo di riuso dell'e237),
  togliendo le copie e le varianti il risolutore dovrebbe leggere meglio.
  - Si tengono 4.761 parole: N 3.022 e A 1.739.
  - Classi sul testo ripulito: R 16.980, V 10.655, F 2.260, N 3.022, A 1.739.
  - Risolutore di forza bruta (e212) in 5 lingue: latino, italiano, tedesco, ebraico, arabo.
  - Il rimescolato sta dentro il criterio.
- **Risultati.** La posizione è fra controllo negativo (0) e positivo (1), nella forma punteggio /
  copertura delle parole di almeno 6 lettere:

  | lingua | solo non copiate | rimescolato |
  |---|---|---|
  | latino | 0,06 / −0,04 | −0,22 / −0,07 |
  | italiano | −0,05 / −0,02 | 0,05 / −0,02 |
  | tedesco | 0,24 / 0,04 | 0,13 / 0,03 |
  | ebraico | 0,27 / 0,09 | 0,25 / 0,00 |
  | arabo | 0,28 / −0,01 | 0,37 / 0,02 |

- **Esito: nessuna lettura.**
  - Nessuna lingua arriva a 0,5.
  - Le parole non copiate non sono più leggibili del loro rimescolato.
  - Ebraico e arabo restano alti nel punteggio come in tutte le prove precedenti: è un effetto dei
    loro alfabeti senza vocali, non del testo.

## 3/10/2026 — e275: generatore "appreso" dalla mistura dell'e259b, non promettente

- **Preregistrato.** Si campiona parola per parola dal modello a mistura dell'e259b, stimato sul Voynich.
  - Pesi stimati delle componenti: base 0,05, cache 0,01, varianti 0,06, lettere 0,08,
    **lettere della pagina 0,79**.
  - Due varianti:
    - (a) campionamento puro;
    - (b) con le scelte di grafia di riga e la fine riga dell'e145.
  - Verifica sui semi 7, 8, 9.
- **Risultati:**
  - (a): pagella 8,3/18, AUC dell'e231 0,997, AUC dell'e266 1,000;
  - (b): pagella 8,3/18, AUC 0,991 e 0,998.
  - In entrambe la riga non è riprodotta. Mancano omogeneità, gradiente, legame, unioni, deriva, profilo
    di pagina, lunghezze vicine, formule e bordo di riga.
  - Il profilo di riuso invece è vicino: R 30–34%, V 36–37%, N 15–17%.
  - Le parole rare sono riusate meno che nei generatori a mano: R 18–29 contro ~50, ma ancora lontano
    dall'1,96 del Voynich.
- **Esito: non promettente.** Il criterio chiedeva pagella ≥ 16 o AUC dell'e266 sotto 0,937.
- **Lettura.**
  - Il modello a mistura spiega bene **quanto** si copia (il profilo di riuso), ma non **come** è fatta
    la pagina.
  - La componente dominante, "lettere della pagina", genera parole plausibili lettera per lettera, ma
    perde tutto ciò che il generatore a mano ottiene con le regole esplicite (copia verticale, giunture,
    spezzature, scelte di riga).
  - **Decisione per il piano:** si resta sulla strada costruita a mano (e241). Dalla strada appresa si
    può prendere un'idea: generare le parole nuove con il modello di lettere della pagina, per abbassare
    il riuso delle parole rare.

## 3/10/2026 — e270: le parole nuove delle pagine d'erbario non seguono la pianta

- **Preregistrato.** Come l'e190 (somiglianza fra disegni contro somiglianza fra testi), ma il testo di
  ogni pagina è ridotto alle sue parole nuove (classe N dell'e237), confrontate per coppie di segni.
- **Risultati:** 121 pagine, 3.684 coppie, 18,3 parole nuove per pagina in media. Spearman 0,023 contro
  un nullo di 0,017, **p 0,46**.
- **Esito: nessun legame.** Anche le parole "nuove", cioè non copiate, non somigliano di più fra pagine
  con piante simili. Non c'è il segno di un nome o di una descrizione della pianta nel lessico nuovo.
- Eseguito sul vecchio PC. Il nuovo PC lo ripete come replica.

## 3/10/2026 — e223b: il candidato tedesco dell'e223 è un artefatto (z da +4,2 a −4,8 cambiando solo le ripartenze)

- **Preregistrato**, secondo il protocollo per i candidati. Sul solo tedesco, con modelli, controllo
  positivo e misura dell'e223:
  - 8 ripartenze;
  - metà invertite;
  - Voynich rimescolato dentro la riga;
  - generatore con cinque semi;
  - controllo positivo nelle stesse forme.
- **Risultati** (z della discriminazione fra sezioni fuori campione):

  | prova | z positivo | z Voynich |
  |---|---|---|
  | e223, una corsa, 4 ripartenze | 8,2 | 4,2 |
  | e223b, positivo 4 ripartenze, Voynich 8 | 7,8 | **−4,8** |
  | metà invertite, 4 ripartenze | 9,0 | 3,1 |
  | rimescolato nella riga, 4 ripartenze | 3,9 | 1,6 |

  - Generatore, semi 1–5: −1,4; −2,0; −4,0; −3,6; 0,2 (massimo 0,2). Nell'e223 lo spagnolo era arrivato a
    4,4.
- **Validità: sì.** Il positivo regge nelle due direzioni, e il rimescolamento nella riga ne dimezza lo z.
- **Esito preregistrato: artefatto.** Nessuna delle quattro prove è superata.
- **Lettura.**
  - Lo z del Voynich dipende dalla chiave che la ricottura trova. Con 8 ripartenze la chiave migliore
    secondo l'obiettivo dà uno z di segno opposto. Il 4,2 dell'e223 era un caso fortunato di una sola
    corsa.
  - **Lezione di metodo per le prove guidate dal contenuto (e213, e223).** Lo z del nullo permuta le
    etichette a chiave fissa, quindi non tiene conto della variabilità fra chiavi. Per un testo senza
    messaggio questa variabilità porta lo z fra circa −5 e +4,5 (generatore e Voynich). Una soglia
    z > 4 su una corsa sola non basta. Le prossime prove di questo tipo vanno tarate su una
    distribuzione di controlli negativi (più semi del generatore, più ripartenze), non su un solo z.
  - Gli esempi decifrati con 8 ripartenze restano senza parole tedesche (*rsdesehaufenenrstesancanal*).
- **Bilancio della strada "guidata dal contenuto":** latino (e213, non valido), cinque volgari (e223) e
  verifica del tedesco (e223b). Nessuna lettura.
- Durata sul nuovo PC: 14 minuti con `PROCESSI=3`.

## 3/10/2026 — Repliche sul nuovo PC: e269 ed e275 identiche a quelle del vecchio PC

- **Perché.** e269 ed e275 sono stati eseguiti su entrambi i PC (decisione di Davide). Il vecchio li ha
  finiti per primo e li ha committati. Le corse del nuovo PC sono in `esecuzioni/repliche/`, non
  committate.
- **Risultati:**
  - **e275:** `.json` identico byte per byte;
  - **e269:** 2.664 valori confrontati; ne differiscono 44, tutti tempi di esecuzione (campi `secondi`). Il
    `.md` è uguale a parte i tempi. La corsa del nuovo PC aveva `PROCESSI=2`, quella del vecchio 1:
    conferma che `PROCESSI` cambia solo il parallelismo;
  - le impronte dei dati coincidono in tutte e due.
- **Durate:** e269 124 min sul vecchio PC, 51 sul nuovo (con il doppio dei processi); e275 87 contro 28.
- **e270** sul nuovo PC è stato fermato a metà, perché il vecchio l'aveva già finito: nessun confronto.
- Da qui in poi si lavora solo sul nuovo PC (STATO_LAVORI.md).

## 3/10/2026 — e276: regolare κ e χ per sezione non aiuta

- **Preregistrato.** Base e241 (l'e243b era peggiore: AUC e266 0,947 contro 0,937). κ e χ scelti per
  gruppo di sezione sul seme 1, con l'AUC dell'e231 sulle sole pagine del gruppo; verifica sui semi 7–9
  contro lo stesso generatore con parametri globali (κ 1, χ 0,2).
- **Scelte:** erbario κ 1,5 χ 0,3; biologica κ 0,5 χ 0,3; ricette e stelle κ 1 χ 0,3; altre κ 0,5 χ 0,1.
- **Risultati** (semi 7, 8, 9; globale → per sezione):
  - AUC dell'e266: 0,966 → 0,955; 0,953 → 0,918; 0,965 → 0,954. Differenza media **0,019**;
  - AUC dell'e231: 0,887 → 0,863; 0,854 → 0,830; 0,879 → 0,838;
  - pagella: 15 → 14; 15 → 15; 15 → 17.
- **Esito preregistrato: non aiuta.** Serviva un calo dell'AUC dell'e266 di almeno 0,03.
- **Lettura.**
  - Regolare per sezione abbassa un poco tutte e due le AUC, ma non abbastanza: le differenze fra
    sezioni non sono il problema principale del generatore.
  - Il generatore e241 sui semi di verifica 7–9 fa **15/18** in tutti e tre, non 16 come sul seme 2,
    con AUC dell'e231 media 0,873 e dell'e266 0,961. È il riferimento vero per i passi seguenti.
  - I parametri per sezione restano un candidato per la regolazione congiunta (e253).
- Durata sul nuovo PC: 48 min.

## 3/10/2026 — e222: il nomenclatore misto non dà letture

- **Preregistrato.** Le 50 o 150 parole più frequenti trattate come codici interi e tolte; il resto
  attaccato lettera per lettera con il risolutore dell'e17, in 14 lingue.
- **Risultati** (posizione punteggio / copertura): togliendo le parole frequenti le posizioni in
  genere **scendono**. Ebraico da 0,70 / 0,25 a 0,27 / 0,08 (50) e 0,32 / 0,04 (150); arabo da 0,52 / 0,29
  a 0,50 / 0,07 e 0,32 / −0,02. Le europee restano fra −0,4 e 0,3 nel punteggio, sotto 0,06 nella
  copertura.
- **Esito preregistrato: nessuna lettura.**
- **Lettura.** Se le parole frequenti fossero codici e il resto un cifrario di lettere, togliendole il
  resto dovrebbe leggersi meglio: succede il contrario. Il vantaggio di ebraico e arabo viene in parte
  proprio dalle parole frequenti (e158, e217b).
- Durata sul nuovo PC: 70 min con `PROCESSI=4`.

## 3/10/2026 — e219: volgari, lingue storiche e latino abbreviato non danno letture

- **Preregistrato.** Risolutore dell'e17 sul testo ripulito, contro 16 corpora: latino abbreviato,
  lombardo, veneto, napoletano, siciliano, friulano, ladino, catalano, occitano, franco-provenzale,
  piccardo, alemanno, bavarese, gotico, anglosassone, slavo ecclesiastico.
- **Risultati.** Il controllo positivo ritrova la chiave al 98–100% (slavo ecclesiastico 89%). Il Voynich
  sta fra 0,01 e 0,40 nel punteggio e fra −0,02 e 0,15 nella copertura delle parole di almeno 6 lettere.
- **Esito preregistrato: nessuna lettura.** Nessun corpus arriva a 0,5.
- **Lettura.** Le varietà vicine all'ambiente probabile del manoscritto (Italia del nord, area alpina,
  1404–1438) si comportano come le lingue nazionali. Gli esempi decifrati sono sequenze senza parole
  (*litrmrsisisisinatestes…* per il latino abbreviato).
- Durata sul nuovo PC: 25 min con `PROCESSI=4`.

## 3/10/2026 — e216: altri ordini di lettura non danno letture

- **Preregistrato.** Risolutore dell'e17 su cinque modi: riferimento; righe al contrario; parole al
  contrario; per colonne; senza i segni facoltativi. Sei lingue.
- **Risultati.** Nessun modo nuovo supera 0,5 in tutte e due le misure. Il più alto è l'ebraico senza
  segni facoltativi, 0,54 / 0,20, sotto il riferimento ebraico (0,70 / 0,25). Tedesco "per colonne"
  0,29 / 0,19.
- **Esito preregistrato: nessuna lettura.**
- **Lettura.** Leggere il testo in un altro ordine non lo avvicina a una lingua. Insieme all'e210
  (qo-/o- e -l/-r imprevedibili) dice che l'ordine di lettura normale non nasconde un cifrario di
  trasposizione semplice.
- Durata sul nuovo PC: 87 min con `PROCESSI=4`.

## 3/10/2026 — e249: i pezzi delle parole come simboli non danno letture

- **Preregistrato.** I pezzi ricorrenti delle parole come simboli del cifrario, con il rimescolato dei
  pezzi dentro il criterio; cinque lingue.
- **Risultati** (pezzi / pezzi rimescolati, punteggio e copertura):
  - latino, italiano e tedesco sotto zero (−0,36 … −0,27 nel punteggio);
  - ebraico −0,16 / 1,30 contro 0,13 / 6,89 del rimescolato;
  - arabo 0,49 / 4,63 contro 1,19 / 2,82.
- **Esito preregistrato: nessuna lettura.** Nessuna lingua supera il proprio rimescolato.
- **Lettura.**
  - Le coperture sopra 1 (fino a 6,89) non sono letture: in ebraico e arabo il controllo positivo
    stesso non trova quasi parole lunghe, quindi la differenza fra positivo e negativo è quasi zero e la
    posizione esplode. È lo stesso difetto dei "candidati" dell'e212b (vedi sotto).
  - Il testo prodotto dal codice riporta anche un "candidato" calcolato senza il rimescolato (arabo,
    pezzi rimescolati); l'esito vale solo per il criterio preregistrato, con il rimescolato.
- Prima esecuzione completa (il vecchio PC non l'aveva finita): 97 min con `PROCESSI=2`.

## 3/10/2026 — e212b: tre "candidati" su 85 lingue, ma la posizione è un artefatto aritmetico

- **Preregistrato.** Come l'e212 (testo ripulito, segni EVA, 2 ripartenze) su tutte le lingue della
  cache non fatte nell'e212: 85 lingue.
- **Risultati.** Candidati secondo il criterio (posizione ≥ 0,5 nelle due misure): **hindi** (6,12 /
  3.133), **finlandese** (6,28 / 9,17), **birmano** (3,10 / 4,01). Le altre 82 lingue no.
- **Esito preregistrato: tre candidati, da riprovare con 8 ripartenze (e212c).**
- **Il difetto, visto sui valori grezzi prima della verifica.** La posizione è (Voynich − negativo) /
  (positivo − negativo):
  - hindi e birmano: il controllo positivo non si decifra (copertura 0,00 e 0,02). Il denominatore è
    quasi zero e la posizione esplode;
  - finlandese: il controllo negativo dell'e17 è finlandese cifrato, cioè la lingua stessa. Il
    denominatore è negativo: il Voynich (−2,70 / 0,07) sta molto sotto i due controlli (−1,58 / 0,63 e
    −1,37 / 0,70), ma la formula dà 6,3.
- **Lezione di metodo.** La posizione va giudicata solo dove il controllo positivo si decifra e il
  positivo supera il negativo. L'e212c lo mette nel criterio, con il latino come negativo del finlandese.
- Durata sul nuovo PC: 33 min con `PROCESSI=4`, `RIPARTENZE=2`.

## 3/10/2026 — e281 sospeso prima di avere risultati

- L'e281 (risolutore dell'e17 sulle sole prime righe dei paragrafi, sei lingue; preregistrazione e codice
  committati) è stato fermato due minuti dopo l'avvio, senza risultati. È una decisione di Davide: niente
  più prove lingua per lingua con il risolutore, troppo costose per quello che rendono, e priorità al
  generatore.
- La preregistrazione resta valida: se si riprende, si esegue così com'è.

## 3/10/2026 — e212c fermato a metà: i candidati dell'e212b non reggono già sui valori parziali

- Fermato a metà per decisione di Davide (niente prove lingua per lingua). Valori parziali dal log, con 8
  ripartenze (punteggio / copertura delle parole di almeno 6 lettere):
  - **finlandese**, con il latino come negativo: positivo −1,58 / 62,8%, negativo −3,05 / 5,4%, Voynich
    −2,73 / 5,5%. Posizione **0,22 / 0,00**: nessun segnale. Con un negativo giusto il "6,3" dell'e212b sparisce;
  - **hindi:** controllo positivo −2,75 / **5,3%**, sotto la soglia di validità (30%): il risolutore non legge
    l'hindi nemmeno quando il messaggio c'è. Test **non valido**;
  - **birmano:** non arrivato. Nell'e212b il positivo aveva copertura 1,7%: test non valido per lo stesso motivo.
- **Conclusione:** i tre candidati dell'e212b erano artefatti della formula della posizione. Nessuna lettura.
- Non si committano risultati parziali: il json si scrive solo a lingua finita.

## 3/10/2026 — e251: il lessico di sezione sopra l'e241 non supera il passo 2

- **Preregistrato** (integrazione del 3/10): il γ di `e233.genera` (base presa dalle forme non attestate già
  scritte nelle pagine precedenti della stessa sezione) sopra l'e241, con braccio di controllo e241 sugli stessi
  semi.
- **Validità:** replica dell'e241 sul seme 2 esatta (16/18, AUC 0,862); γ 0 identico all'e241; meccanismo attivo
  (ricircolo da 0,05 a 0,19–0,20); R delle parole rare del Voynich 1,958 come atteso.
- **Scelta sul seme 1:** la pagella scende subito (e241 14; γ 0,1 → 11; 0,2 → 11 senza riga; da 0,3 in su → 7);
  R delle parole rare da 44 a 19 con γ 0,6. Nessun γ ammesso: verifica con il ripiego γ 0,1.
- **Verifica (semi 7, 8, 9; e241 → γ 0,1):** pagella 15, 15, 15 → 11, 12, 11; R delle parole rare 48,3 → 34,1;
  AUC dell'e231 0,873 → 0,928, dell'e266 0,961 → 0,973. Si perdono h2, curva piatta e omogeneità o profilo.
- **Esito preregistrato: non superato** (R e pagella).
- **Diagnosi delle rare confinate** (e241, semi 7–9): circa un terzo forme nuove, un terzo parole attestate proprie
  di una sola pagina vera del Voynich, un terzo altre attestate. Il lessico toglie soprattutto le "proprie della
  pagina vera" (76 → 48 sul seme 7), non le forme nuove.
- **Lettura.**
  - Far circolare le forme nuove abbassa R ma rompe la pagella: le forme nuove ricopiate in altre pagine
    gonfiano la quota di non attestate (0,14 → 0,20) e cambiano h2 e la curva delle uniche.
  - La diagnosi del generatore fatta oggi (sintesi in STATO_LAVORI.md) indica la causa principale altrove: il
    generatore pesca dalla pagina vera **con reimmissione** e da un **tema di 3 parole** che copre il 30% dei posti.
    Sono costanti scritte nel codice e mai regolate. Da qui le parole che si ripetono troppo nella pagina (tipi
    su parole 0,68 contro 0,76, uniche nella pagina 0,54 contro 0,64) e le rare confinate.
  - Secondo il piano il passo si rifà una volta: e251b con questo meccanismo (riuso di pagina senza tema
    concentrato e senza reimmissione).
- Durata sul nuovo PC: 21 min con `PROCESSI=6`.

## 3/10/2026 — e279, e285, e286: tre prove leggere di decifrazione; due esiti formalmente positivi, da verificare

- **e279, Bacone nelle 12 scelte di riga dell'e206b.** 105.799 bit (una parola dà un bit per ogni classe che ha).
  - Indice di coincidenza dei gruppi di 5 bit: Voynich 0,0445, **z 17,5** (L4 14,9; L6 18,9; L7 17,2) contro il nullo
    dentro classe × riga. Controlli: Bacone puro z 341, al 70% z 51, al 30% z 5,1 (indice 0,0437).
  - **Esito preregistrato: canale baconiano presente.**
  - **Sospetto, scritto prima della verifica.** Molte classi sono di forma della parola (*o* iniziale, *y* finale,
    *ch* iniziale…): una parola porta più bit insieme, e due parole su tre sono copie o varianti (e237). Il nullo
    rimescola i bit uno per uno e spezza questi blocchi, quindi il caso a cui confrontiamo il Voynich è troppo
    "piatto". È lo stesso tranello dell'e191 (z 13,5 → −0,4 con il nullo a parole intere, e191b). Con le 5 scelte
    dell'e181, che per lo più non sono di forma, lo stesso nullo dava z 0,5.
  - **Protocollo:** nessuna lettura; verifica e279b con il nullo a parole intere e il generatore con gli
    interruttori come controllo negativo.
- **e285, pezzi della parola nel contesto (tabelle e griglie).** Eccesso di informazione mutua fra pezzi omologhi
  di parole vicine, rispetto al rimescolamento nella riga:
  - Voynich: prefisso 0,037; centro 0,010; **finale 0,050**; finale → prefisso 0,117;
  - generatore e241 (semi 7–9): prefisso 0,027–0,031; centro 0,053–0,062; finale 0,024–0,034; finale → prefisso
    0,061–0,074;
  - positivo puro: finale 0,253; al 50% 0,029 (il test vede solo un messaggio denso).
  - **Esito preregistrato: pezzo portatore candidato, il finale** (0,050 contro una soglia di 0,041).
  - **Sospetto.** Nel Voynich le parole vicine si somigliano più che nel generatore (0,218 contro 0,207,
    e241), e due vicine che sono varianti l'una dell'altra hanno spesso lo stesso finale. Il centro, al contrario,
    dipende meno che nel generatore. Il quadro è quello di una copia fra vicine fatta "per finali", non per forza un
    messaggio. Anche il legame finale → prefisso è quasi il doppio del generatore.
  - **Protocollo:** nessuna lettura; verifica e285b sulle sole coppie vicine che non sono varianti.
- **e286, ruote combinatorie negli anelli (Cc).** Quota di coppie consecutive che cambiano un solo pezzo: anelli
  0,135 (eccesso 0,023, z 4,8); paragrafi in tratti uguali 0,111 (eccesso 0,014, z 2,6); positivo z 11,4.
  - **Esito preregistrato: nessuna struttura combinatoria oltre la copia** (eccesso 1,6 volte il riferimento,
    serviva il doppio).
  - Gli anelli sono un po' più "sistematici" del testo corrente, coerente con l'e263 (etichette e aree illustrate
    copiate dalla vicina).

## 3/10/2026 — e280: i quattro anelli a 12 settori non nominano le stesse 12 cose

- **Preregistrato** (strada nuova 2, versione leggera e senza lingue). Quattro anelli di 12 settori nei
  diagrammi astronomici (f67r1 Ri; f67r2 Ls e L0; f67v1 L0). Se fossero un vocabolario (12 mesi o 12 segni), il
  settore corrispondente dovrebbe avere un'etichetta simile da un anello all'altro, una volta allineati inizio e
  verso.
- **Misura:** per ogni coppia di anelli la migliore delle 24 disposizioni della somiglianza media dei settori
  (1 − distanza di modifica normalizzata, segni EVA); S = media sulle 6 coppie; z contro 1.000 rimescolamenti
  nell'anello.
- **Risultati:**
  - anelli: S 0,286 contro 0,278 del nullo, **z 1,2**;
  - positivo (mesi latini con un cifrario verboso, disposizioni a caso, 20% di errori): **z 14,8**;
  - negativi (6 gruppi di finestre di 12 etichette astronomiche e dello zodiaco): z da −1,9 a 1,2.
- **Esito preregistrato: nessun vocabolario comune.**
- **Lettura.**
  - Se i quattro anelli nominano le stesse 12 cose, non lo fanno con parole che si somigliano: il test vede
    benissimo un nome cifrato anche con errori. Oppure nominano cose diverse.
  - È coerente con l'e263: nelle aree illustrate le etichette si copiano dalla vicina, non da un elenco di nomi
    fisso.
- Durata: un minuto.

## 3/10/2026 — e279b: verifica non valida per un mio errore nel controllo positivo

- **Preregistrato:** nullo che rimescola parole intere (con i loro bit) dentro la riga; generatore e241 con gli
  interruttori dell'e252 come negativo; positivi di Bacone al 70% e al 30%.
- **Risultati** (z del gruppo di 5 bit, nullo a parole intere / nullo bit per bit):
  - Voynich **6,2** / 23,6;
  - generatore senza messaggio **4,2** / 37,4;
  - positivi al 70%: −0,7 / −7,6; al 30%: 1,2 / 7,9.
- **Esito preregistrato: non valido** (il positivo al 70% non supera z 4).
- **L'errore (mio).** Nei positivi il messaggio è stato inserito consumandolo solo nei posti sostituiti, quindi
  sfasato rispetto alla griglia dei gruppi di 5: non è un cifrario di Bacone, e il test per costruzione non poteva
  vederlo. Nell'e279 il positivo era allineato, ed era visto (z 341 puro, 51 al 70%).
- **Che cosa si vede comunque, non come esito:** con il nullo giusto lo z del Voynich crolla da 23,6 a 6,2, e il
  generatore senza messaggio arriva a 4,2: gran parte del segnale dell'e279 viene dalle parole ripetute. La
  differenza Voynich − generatore è 2,0, sotto la soglia preregistrata di 3.
- Si rifà con i positivi corretti (e279c), stesso criterio.

## 3/10/2026 — e285b: la dipendenza fra finali di parole vicine regge anche senza le coppie di varianti

- **Preregistrato:** la misura dell'e285 sulle sole coppie di parole vicine non varianti (distanza di modifica ≥ 2).
  Le coppie varianti sono il 5,3% nel Voynich e il 6,7–6,9% nel generatore.
- **Risultati** (eccesso di informazione mutua sul rimescolamento nella riga):
  - **finale:** Voynich **0,041**; generatore e241 0,017 / 0,007 / 0,011 (semi 7, 8, 9); soglia 0,024;
  - **prefisso:** Voynich 0,031; generatore 0,009–0,011;
  - **centro:** Voynich 0,007; generatore 0,041–0,053 (il generatore copia i centri, il Voynich no);
  - **finale → prefisso:** Voynich 0,112; generatore 0,055–0,070;
  - positivo puro 0,255 sul finale; al 50% 0,021.
- **Esito preregistrato: il finale regge come portatore.** Nessuna lettura.
- **Lettura, con le alternative da distinguere (scritte prima della prova successiva).**
  1. **Inerzia della mano:** dopo un finale, lo scriba tende a riscriverlo (l'e123b aveva già visto un "innesco"
     fra parole adiacenti per ch/sh, z 3,0).
  2. **Concordanza di una lingua:** desinenze vicine che si accordano, come aggettivo e nome.
  3. **Un messaggio** portato dai finali.
  - Le prime due producono soprattutto **ripetizioni dello stesso finale**; un messaggio produce **passaggi
    sistematici fra finali diversi**, come le coppie di lettere di una lingua. Si separano nell'e285c.
  - Vale anche il contrario per il generatore: le parole del Voynich si legano alle vicine per i bordi (prefisso,
    finale) e non per il centro, il generatore fa il contrario. È una proprietà nuova da dare al generatore.

## 3/10/2026 — e279c: il canale "alla Bacone" dell'e279 è un artefatto delle parole ripetute

- **Preregistrato:** come l'e279b, con i positivi allineati.
- **Risultati** (z con il nullo a parole intere): Voynich **7,1**; generatore e241 con gli interruttori, senza
  messaggio, **4,5**; positivo puro 357,9; al 70% 103,7.
- **Esito preregistrato: artefatto delle parole ripetute.** Il test è valido, ma il Voynich supera il generatore di
  2,6 (serviva 3).
- **Lettura.** Il segnale dell'e279 (z 17,5) viene quasi tutto dal fatto che le parole si ripetono con i loro
  segni facoltativi: rimescolando parole intere scende a 7,1, e un generatore senza messaggio arriva a 4,5. Strada
  nuova 1 chiusa: nessun canale di Bacone nelle 12 scelte di riga (e nelle 5 scelte, e181).

## 3/10/2026 — e268: il registro delle prime righe abbassa il discriminatore, ma ρ 0,6 è troppo e rompe la pagella

- **Preregistrato** (passo 3b): nelle prime righe dei paragrafi, con probabilità ρ, la base viene dalle prime righe
  vere delle altre pagine della stessa sezione. ρ scelto sul seme 1 con l'AUC del gruppo G8 dell'e266.
- **Scelta sul seme 1** (pagella / AUC e266 / G8): ρ 0: 14 / 0,956 / 0,885; 0,2: 15 / 0,934 / 0,837; 0,4: 14 / 0,943 /
  0,796; 0,6: 13 / 0,928 / 0,748; 0,8: 12 / 0,919 / 0,703. Scelto **ρ 0,6** (G8 minima fra gli ammessi).
- **Verifica** (semi 7, 8, 9; e241 → ρ 0,6):
  - G8: 0,890 → **0,754**; AUC dell'e266: 0,961 → **0,915**; dell'e231: 0,873 → 0,864;
  - misura dell'e273 sul seme 7: e241 +0,002 (z 0,2) → ρ +0,083 (**z 8,4**; Voynich +0,047, z 4,7);
  - pagella: 45 → **38** (si perdono omogeneità, gradiente, curva piatta, in un seme h2); riga in 3 semi su 3
    (e241: 2).
- **Esito preregistrato: non superato** (pagella).
- **Lettura.**
  - È il primo meccanismo che abbassa in modo netto il discriminatore forte (−0,046) e il suo gruppo G8 (−0,136):
    il registro d'apertura è una delle cose che tradivano il generatore.
  - ρ 0,6 è troppo: l'effetto dell'e273 esce quasi doppio di quello del Voynich, e le prime righe "importate"
    rompono omogeneità e gradiente della pagina. La regola di scelta (G8 minima) spingeva verso l'eccesso.
  - Secondo tentativo (e268b): ρ scelto perché la misura dell'e273 sul seme 1 sia la più vicina a quella del
    Voynich, a pagella non inferiore all'e241.

## 3/10/2026 — e251b: senza tema concentrato il "muro" si muove, ma il passo 2 non passa; lacuna dichiarata

- **Preregistrato:** copia di `e233.genera` con θ (quota del tema), K (parole del tema) e mazzo (estrazione senza
  reimmissione); scelta sul seme 1 con la regola dell'e251.
- **Seme 1** (pagella, R delle parole rare): e241 14, 44; θ 0 14, 38; mazzo θ 0 10 (senza riga), 10,2; mazzo θ 0,15
  10, 23. Scelta: **θ 0** (senza tema).
- **Verifica** (semi 7–9; e241 → θ 0): pagella 45 → 42; riga in 2 → 3 semi; R delle parole rare 48,3 → 41,7; AUC
  dell'e231 0,873 → 0,867, gruppo **G3 0,916 → 0,880**; dell'e266 0,961 → 0,956; tipi su parole nella pagina 0,678 →
  **0,731** (Voynich 0,756).
- **Esito preregistrato: non superato** (R e pagella). Non "utile" per la regola (AUC dell'e266 −0,005). È il
  secondo tentativo del passo 2: **si dichiara la lacuna del passo 2** e il generatore prosegue con l'e241.
- **Lettura.** Il tema concentrato spiega una parte del "muro" di G3 (varietà di parole nella pagina): toglierlo
  porta la varietà quasi al Voynich e abbassa G3 di 0,036, la prima mossa vera di quel gruppo. Il mazzo senza
  reimmissione abbassa molto R delle parole rare (fino a 10) ma rompe la pagella. θ resta un parametro per la
  regolazione congiunta (e253).

## 3/10/2026 — e285c: fra finali vicini ci sono passaggi sistematici, ma sembrano concordanza di desinenze e prefissi staccati

- **Preregistrato:** la dipendenza dell'e285b divisa in ripetizione dello stesso finale e passaggi fra finali diversi.
- **Risultati:**
  - ripetizione: Voynich +0,016 (z 12,9); generatore +0,017–0,021: il generatore ripete **di più**;
  - passaggi fra finali diversi: Voynich **+0,043 (z 17,8)**; generatore +0,010–0,019; positivo +0,245;
  - la ripetizione vale solo a distanza 1 (a distanza 2 e 3 è nulla), come nel generatore.
- **Esito preregistrato: passaggi sistematici** (compatibile con un messaggio, da verificare oltre).
- **I passaggi più frequenti del caso, prima di ogni lettura:** *shedy → edy* (3,8 volte l'atteso), *eedy → edy*,
  *chedy → edy*, *edy → chedy*, *edy → l*, e da parole finite in *o*, *s*, *l* a parole senza finale (i prefissi
  staccati dell'e227).
  - Sono la stessa famiglia di desinenza (*-edy*) divisa diversamente dal segmentatore, cioè una **concordanza delle
    desinenze** fra parole vicine, e i **prefissi staccati** già noti. Non hanno l'aspetto delle coppie di lettere di
    un messaggio.
  - Verifica e285d: desinenze raggruppate per famiglia e coppie con prefisso staccato escluse.
- **Per il generatore:** le parole vicine del Voynich "rimano" nella desinenza più che nel generatore, che invece
  ripete di più le parole. È un meccanismo da aggiungere.

## 3/10/2026 — Voynichizzatore v0: funziona, ma il messaggio nelle scelte di grafia si vede

- **Che cosa fa:** testo normale → manoscritto intero in EVA (corpo e241 con il seme dalla chiave); il testo
  compresso e cifrato con la chiave va nelle 5 scelte di grafia, in posti sparsi scelti dalla chiave. Con la chiave
  il testo torna esatto; con una chiave sbagliata non si legge niente (`voynichizzatore/v0.py`).
- **Prova:** Isidoro, *Etymologiae* XVII (inizio, 1.668 parole latine) → 207 pagine, 4.130 righe; il messaggio
  occupa il 66% dei 57.696 posti di scelta. Decodifica identica byte per byte.
- **Rilevabilità (descrittiva, stesso corpo):** senza messaggio pagella 14, riga sì, AUC e231 0,893, e266 0,951; con
  il messaggio pagella 13, **riga no**, AUC **0,958** e **0,980**. Le scelte forzate a metà e metà rompono le
  abitudini di riga.
- **Prossimo passo (v1):** codifica aritmetica con un modello delle scelte imparato dal Voynich (contesto e scelte
  già fatte nella riga), così le scelte escono distribuite come nel modello; corpo migliorato con θ 0 e le prime
  righe.

## 3/10/2026 — e268b: prime righe, secondo tentativo; non superato, lacuna del passo 3b (prime righe)

- **Preregistrato:** come l'e268, con ρ scelto sul seme 1 per avvicinare la misura dell'e273 a quella del Voynich
  (+0,047), a pagella non inferiore. Scelto **ρ 0,25** (+0,026 sul seme 1; ρ 0,3 dava +0,047 ma pagella 13).
- **Verifica** (semi 7–9; e241 → ρ 0,25): G8 0,890 → **0,824**; AUC dell'e266 0,961 → **0,931**; dell'e231 0,873 →
  0,866; misura dell'e273 sul seme 7 +0,028 (z **2,9**); pagella 45 → **42** (seme 7: 16/18, seme 8 e 9: 13/18);
  riga in 3 semi su 3.
- **Esito preregistrato: non superato** (e273 di un soffio, pagella). Secondo tentativo: si dichiara la **lacuna del
  passo 3b per le prime righe**.
- **Lettura.** Il registro d'apertura abbassa il discriminatore forte di 0,03 anche a dose moderata, ma le prime
  righe "prese" da altre pagine costano proprietà di pagina (omogeneità, gradiente, formule) a seconda del seme. ρ
  resta un parametro per la regolazione congiunta, dove si può compensare con gli altri.

## 3/10/2026 — e252: i dodici interruttori di riga, così come progettati, peggiorano il generatore

- **Preregistrato** (integrazione del 3/10): base e241 (il passo 2 ha una lacuna); per ognuna delle 12 classi
  dell'e206b uno stato AR(1) di riga; `e251.applica_interruttori` riscrive le parole dopo le cinque scelte.
- **Validità:** interruttori spenti identici a `e233.genera`; base identica all'e251 sui semi 7–9.
- **Risultati** (semi 7–9; base → interruttori): pagella 15, 15, 15 → 11, 11, 13; riga in 2 semi → **0**; AUC
  dell'e231 0,873 → **0,935**, dell'e266 0,961 → **0,983**. Si perdono h2, Zipf, a volte legame e omogeneità.
- **e206b sull'uscita del seme 7:** classi con z > 3 **3 su 12** (base: 4). Le classi di prefisso (*sh* iniziale,
  *cth* iniziale) salgono un poco, quelle di fine e di interno scendono.
- **Esito preregistrato: non superato** (classi, pagella, riga).
- **Lettura.**
  - Il meccanismo sceglie a caso una classe per parola e sostituisce la parola con "la forma lunga più frequente"
    (o la corta): cambia il vocabolario invece di cambiare un segno, e rompe Zipf e h2. Inoltre le 12 classi
    insieme toccano quasi ogni parola, e il loro stato di riga si diluisce.
  - Un secondo tentativo dovrebbe cambiare solo il segno della classe (come fa `e145.riscrivi` per le cinque
    scelte), non la parola. Intanto il modello delle scelte della v1 del voynichizzatore (imparato dal Voynich,
    con lo stato di riga) fa qualcosa di simile per le cinque scelte.

## 3/10/2026 — Voynichizzatore v1: con la codifica aritmetica il messaggio non si vede più

- **Che cosa cambia dalla v0:** un modello delle 5 scelte di grafia, imparato dal Voynich (regressione logistica per
  tipo di scelta; contesto della parola con le famiglie dei segni, posizione nella riga, scelte già fatte nella riga e
  nella riga sopra), dà per ogni posto la probabilità della forma lunga. Il messaggio cifrato sceglie con quella
  probabilità attraverso la codifica aritmetica binaria (Witten, Neal, Cleary, 32 bit): il decodificatore aritmetico
  nasconde, il codificatore rilegge. Tutte le scelte del libro escono distribuite come nel modello
  (`voynichizzatore/v1.py`, modello in `voynichizzatore/modello_scelte_v1.json`).
- **Il modello** (56.850 posti, come l'e182): quote di forme lunghe CH 0,30, KT 0,36, LR 0,47, DE 0,63, QO 0,51; i
  coefficienti dello stato di riga sono tutti positivi (0,5–1,4): le abitudini di riga sono nel modello.
- **Prova:** Isidoro XVII (11.207 byte, 4.776 compressi, 38.240 bit) nello stesso corpo della v0. Decodifica identica
  byte per byte; chiave sbagliata respinta. Capacità con questo metodo circa 0,8 bit per posto (circa 46.000 bit).
- **Rilevabilità (stesso corpo):** senza messaggio 14/18, riga sì, AUC e231 0,893, e266 0,951; **v1 con il messaggio
  15/18, riga sì, 0,889 e 0,957** (v0: 13/18, riga no, 0,958 e 0,980).
- **Lettura.** Il canale non aggiunge rilevabilità oltre la variabilità fra semi; il modello delle scelte migliora
  perfino la pagella di un punto. Da qui la rilevabilità del voynichizzatore dipende solo dal corpo (generatore).

## 3/10/2026 — e288: il generatore arriva a 18/18 su due semi di verifica su tre

- **Preregistrato:** copia di `e233.genera` con la penalità **rip** per le candidate uguali alla parola precedente,
  **φ** con copia per indice dalla riga sopra e **σ** di `dopo`; griglia di 27 configurazioni sul seme 1.
- **Seme 1:** la migliore è **rip 0,5, φ 0,10, σ 0,04**: 18/18 con la riga (ripetizione ×1,16, verticale 1,019,
  spazio 0,617; Voynich 1,01, 1,028, 0,664). Con rip 0,3 la ripetizione scende troppo (×0,80) e si perdono le formule.
- **Verifica** (semi 7, 8, 9; e241 → scelta):
  - pagella **15 → 18**, **15 → 17** (manca solo l'omogeneità), **15 → 18**; riga in 2 → **3** semi;
  - AUC dell'e231 0,887 / 0,854 / 0,879 → **0,855 / 0,828 / 0,816** (media 0,873 → **0,833**);
  - AUC dell'e266 0,966 / 0,953 / 0,965 → **0,937 / 0,937 / 0,926** (media 0,961 → **0,933**).
- **Esito preregistrato: migliore** (non "18/18" per il seme 8).
- **Lettura.**
  - Tre correzioni piccole e mirate, guidate dai valori grezzi, fanno quello che e243 ed e243b (passo 1) non avevano
    fatto: la ripetizione va a posto con una penalità moderata, la verticale con la copia **per indice** (non per
    posizione fisica), lo spazio con meno spezzature.
  - Il discriminatore scende anche lui (−0,04 / −0,03): le materie della pagella e i suoi indizi in parte coincidono.
  - È il nuovo riferimento per il corpo del voynichizzatore (v2) e per la regolazione congiunta.

## 3/10/2026 — e283: la ricerca casuale congiunta sui parametri vecchi non migliora; lezione sull'"effetto vincitore"

- **Preregistrato:** 96 configurazioni casuali di 13 parametri dell'e241, più 24 di affinamento, sul seme 1;
  obiettivo AUC dell'e266 con la pagella non oltre 1 sotto l'e241; verifica sui semi 7–9.
- **Seme 1:** la scelta (a017: α 1,23, κ 1,81, χ 0,00, ν 0,35, λ 1,38, η 0,19, δ 0,34, ψ 0,03, σ 0,04, π 0,34) ha AUC
  dell'e266 0,910 contro 0,956 dell'e241, pagella 15 contro 14.
- **Verifica** (semi 7–9; e241 → scelta): pagella 45 → **40** (perde omogeneità, verticale, formule, bordo di riga,
  a volte deriva); riga in 2 → 3 semi; AUC dell'e231 0,873 → 0,890, dell'e266 0,961 → 0,948.
- **Esito preregistrato: non migliore.**
- **Lettura.**
  - **Effetto vincitore.** Fra 121 configurazioni valutate su un solo seme, la migliore lo è in parte per caso:
    l'AUC oscilla di circa ±0,03 da un seme all'altro. Sui semi di verifica il vantaggio si dimezza, e il vincolo
    largo sulla pagella (meno 1) lascia perdere proprietà. L'e288, che sceglie prima per pagella su una griglia
    piccola, regge invece benissimo alla verifica. Da qui l'integrazione dell'e289: due semi di ricerca, scelta per
    pagella poi AUC. L'e253, in corso, ha lo stesso disegno dell'e283 e va letto con questa cautela.
  - **Correlazioni con l'AUC dell'e266 sul seme 1** (positiva = alzarlo peggiora): γ +0,72, χ +0,50, ν +0,51, φ fisica
    +0,46, η +0,36, σ +0,30; δ −0,41, κ −0,29, α −0,24, π −0,22. Il lessico di sezione, la copia della parola
    precedente e le varianti facili tradiscono il generatore; prendere basi dal Voynich intero e variare le rare aiuta.

## 3/10/2026 — Voynichizzatore v2: il nascondiglio della v1 nel corpo dell'e288

- **Che cosa fa:** come la v1 (scelte di grafia con la codifica aritmetica secondo il modello imparato dal Voynich), ma
  il corpo è la configurazione dell'e288 (rip 0,5, φ 0,10 per indice, σ 0,04) con `corpo2.genera_v2`
  (`voynichizzatore/v2.py`; accetta anche i parametri della regolazione congiunta).
- **Prova:** Isidoro XVII, chiave "mandragora" (corpo con il seme ricavato dalla chiave, non un seme di verifica).
  Decodifica identica byte per byte. 57.311 posti di scelta.
- **Rilevabilità:**
  - stesso corpo senza messaggio: **17/18** (manca il gradiente), riga sì, AUC e231 **0,812**, e266 **0,928**;
  - con il messaggio: **16/18** (mancano verticale e formule), riga sì, AUC e231 **0,831**, e266 **0,933**;
  - confronto con le versioni precedenti, stesso testo e stessa chiave: v0 0,958 / 0,980; v1 0,889 / 0,957.
- **Lettura.** Il corpo nuovo abbassa i due discriminatori di 0,06 e 0,02 rispetto alla v1. Il messaggio costa qui
  un punto di pagella e 0,02 / 0,005 di AUC: su un solo seme è dentro la variabilità (circa ±0,03), da misurare su più
  chiavi. Prossimi giri: e253 ed e289 per il corpo, poi il ciclo avversario.

## 3/10/2026 — e296: le parole rare del Voynich sono in gran parte varianti di parole frequenti, sparse come errori

- **Preregistrato** (ipotesi di Davide): rare = 2–5 occorrenze; "varianti" = a una modifica (sui segni) da una parola con
  almeno 20 occorrenze; R dell'e211 sulle pagine dell'erbario per i due gruppi.
- **Risultati:**

  | testo | rare | quota varianti | R varianti | R non varianti |
  |---|---|---|---|---|
  | Voynich | 1.487 | **0,656** | **0,57** | 1,16 |
  | generatore e288 (semi 7, 8, 9) | 1.882–1.937 | 0,56–0,57 | 32–39 | 77–87 |

  - Anche fra gli hapax, il 29% è a una modifica da una parola frequente (generatore 27%).
- **Esito preregistrato: errori sparsi sostenuti.**
- **Lettura.**
  - Due terzi delle parole rare del Voynich sono varianti di una lettera di parole frequenti, e compaiono in pagine
    qualsiasi, come errori di scrittura o di lettura capitati a caso (R sotto 1: perfino meno raggruppate del caso).
  - Nel generatore le varianti nascono dalle parole della pagina e restano lì: è la causa del difetto più grande
    rimasto (R delle parole rare). Le rare del Voynich che non sono varianti sono anch'esse sparse (R 1,16): nel Voynich
    nessuna parola rara è "della pagina".
  - L'e297 aggiunge al generatore gli errori sparsi.

## 3/10/2026 — e294: il profilo dei bordi del Voynich ha la forma di una lingua con concordanza, non la forza

- **Preregistrato:** indice dei bordi = (eccesso del prefisso + eccesso del finale)/2 − eccesso del centro (informazione
  mutua fra pezzi di parole vicine oltre il rimescolamento nella riga), su 20.000 parole per testo.
- **Risultati** (110 testi validi): Voynich **+0,031** (prefisso 0,037, centro 0,012, finale 0,049, finale → prefisso 0,116);
  generatore e288 −0,010. **14 testi naturali** hanno indice ≥ Voynich: giapponese +0,198, coreano +0,167, Catone +0,106,
  nahuatl +0,085, ashaninka +0,081, achuar, Varrone, aguaruna, quichua, lituano, Columella XII, shuar, basco, Vegezio.
  Latino della Bibbia +0,001, finlandese +0,007, ebraico −0,009.
- **Esito preregistrato: profilo da lingua.**
- **Lettura, con una cautela forte.**
  - La **forma** (bordi legati più dei centri) si trova nelle lingue agglutinanti o con concordanza e nei testi
    tecnici latini a elenchi (ricette, agricoltura): non è un'impronta esclusiva del procedimento.
  - Ma la **forza** è diversa: nelle lingue gli eccessi sono 0,1–0,5 bit, nel Voynich 0,01–0,05. Le parole vicine del
    Voynich si legano 3–10 volte meno che in qualsiasi lingua: è di nuovo l'assenza di sintassi (e114, e115, e259).
  - Il generatore ha la forma opposta (centri copiati): per imitare il Voynich deve legare i bordi, non copiare i centri.

## 3/10/2026 — e253: la regolazione congiunta su 19 parametri non migliora l'e288; e289 fermato

- **e253, preregistrato:** 128 configurazioni casuali più 32 di affinamento sul seme 1, obiettivo AUC dell'e266.
  - Scelta (a031) sul seme 1: AUC 0,916 (e241 0,956). Verifica sui semi 7–9: pagella 48 (e241 45), riga in 2 semi, AUC
    dell'e231 0,878 (e241 0,873), dell'e266 0,943 (0,961). **Esito: non migliore** (serviva −0,05).
  - Peggiore dell'e288 (53, 0,833, 0,933): di nuovo l'effetto vincitore della scelta su un solo seme (e283).
  - Correlazioni con l'AUC dell'e266 sul seme 1: θ −0,59 (un tema più presente aiuta), ψ −0,39 (copiare pezzi di riga
    aiuta), α −0,36, η −0,31; γ +0,60, interruttori +0,44, ρ +0,41, K del tema +0,31, φ +0,25, σ +0,24 fanno male.
- **e289 fermato** dopo l'avvio, senza risultati: era centrato sulla scelta dell'e253, peggiore dell'e288. Il prossimo
  giro di regolazione si centra sul corpo migliore (e288 con gli errori sparsi dell'e297, se utili).

## 3/10/2026 — e295: la concordanza delle desinenze si ferma all'a capo (abitudine di riga, non grammatica)

- **Preregistrato:** eccesso di informazione mutua fra i finali di parole vicine dentro la riga e fra l'ultima parola di
  una riga e la prima della seguente (stesso paragrafo); controllo positivo: Bibbia latina in righe.
- **Risultati:** Voynich dentro 0,050, attraverso l'a capo **0,007 (z 0,7), r 0,14**; generatore 0,021 e 0,012 (r 0,57);
  latino 0,192 e 0,131 (z 9,9, **r 0,68**).
- **Esito preregistrato: si ferma all'a capo (abitudine di riga).**
- **Lettura.** Con l'e294: la concordanza delle desinenze del Voynich ha la forma di quella delle lingue agglutinanti,
  ma è molto più debole e non supera l'a capo, mentre in una lingua la frase continua nella riga seguente. È
  un'abitudine dello scriba legata alla riga, come le scelte di grafia (e135, e206b). Per il generatore: la "rima" delle
  desinenze va fatta dentro la riga.

## 3/10/2026 — e293: banco di prova e pagella estesa; la v3 migliora la v2, ma le 8 materie aggiunte mancano tutte

- **Preregistrato:** pagella estesa = 18 materie dell'e224 + 8 (parole rare per pagina, tipi e uniche nella pagina,
  dispersione delle lunghezze, prime righe come registro, scelte di riga dell'e206b, concordanza delle desinenze, coppie
  viste altrove); banco fisso: Isidoro XVII nascosto con la chiave "banco" in corpi con i semi 7, 8, 9.
- **Controllo del metro:** il Voynich passa tutte e otto le materie aggiunte (R 1,96; tipi 0,756; uniche 0,636;
  dispersione 1,579; e273 z 4,7; 12 classi su 12; concordanza 0,043; coppie 0,221).
- **Risultati** (3 semi): decodifica esatta in tutti e 6 i casi.

  | versione | pagella | pagella estesa | riga | AUC e231 | AUC e266 |
  |---|---|---|---|---|---|
  | v2 | 52/54 | 52/78 | 2 | 0,842 | 0,945 |
  | v3 | 52/54 | 52/78 | 2 | **0,817** | **0,934** |

- **Esito:** la v3 **migliora** la v2 (AUC dell'e266 −0,011, pagella estesa uguale).
- **Lettura.** Le 18 materie originali sono quasi tutte prese, ma nessuna delle 8 materie aggiunte: la pagella a 18
  sopravvalutava il generatore. Ognuna delle otto ha un meccanismo candidato (errori sparsi, lunghezza stabile, rima delle
  desinenze nella riga, successore già visto, prime righe): sono la v4.

## 3/10/2026 — e298, e299: le famiglie di parole nella pagina non distinguono; la fine riga dipende appena dalla lunghezza

- **e298 (famiglie):** tipi legati da una modifica, componenti per pagina. Voynich: 117 tipi, 36,4 famiglie, 3,09 tipi per
  famiglia, 75% delle occorrenze in famiglie di 2+ tipi; generatore e288 (semi 7–9): 112 tipi, 34–35 famiglie, 3,02–3,08,
  78–79%. **Nessuna misura diversa.** La maggiore varietà del Voynich nella pagina non viene da una diversa struttura per
  famiglie ma, secondo l'e296, dalle parole rare sparse (errori).
- **e299 (fine riga):** le righe che finiscono in *m* o *g* sono più lunghe dell'1,5% rispetto alla media della pagina
  (z 2,0); generatore −1,9…+0,3% (z −1,8…0,3). **Esito: incerto.** Un indizio debole di uso dei finali di riga per
  chiudere righe lunghe; non una prova di giustificazione.

## 3/10/2026 — e300, e301: le pagine consecutive si somigliano; le mani 2 e 3 si distinguono, ma forse per la sezione

- **e300 (ordine delle pagine):** somiglianza (coseno sulle parole di frequenza media) fra pagine consecutive nella
  rilegatura, contro permutazioni dentro la sezione. Voynich: 0,129 contro 0,097, **z 8,5**; Spearman distanza-somiglianza
  −0,13. Positivo (Bibbia in pagine): z 23,1. **Esito preregistrato: ordine di rilegatura vicino a quello di scrittura.**
  - **Cautela, scritta prima della verifica:** dentro una sezione le pagine in lingua A e in lingua B stanno in blocchi
    contigui (fascicoli omogenei), e due pagine della stessa lingua si somigliano comunque. La permutazione dentro la
    sezione non toglie questo effetto. Verifica: e300b, permutazione dentro sezione × lingua.
- **e301 (scribi):** mani 2 e 3 di Davis (lingua B, 74 pagine), sei abitudini fini per pagina (t/k a inizio riga, concordanza
  -dy/-ey, rima, qo-, finali m/g, lunghezza). Accuratezza 0,770 contro 0,507, **z 3,4: esito preregistrato "mani
  distinguibili"**. Ma le mani hanno scritto sezioni diverse (mano 2: B 19, H 20, T 4, C 3; mano 3: S 22, H 6) e dentro
  l'erbario, l'unica sezione comune, z 1,1. La differenza è più probabilmente di sezione che di mano, come negli e244 ed e260.

## 3/10/2026 — e300b: l'ordine delle pagine resta anche dentro la stessa lingua

- **Preregistrato:** la misura dell'e300 con le permutazioni dentro **sezione × lingua di Currier** (seme 300).
- **Risultato:** coppie consecutive 0,136 contro 0,113 del nullo, **z 5,7**; Spearman distanza-somiglianza −0,14.
  **Esito preregistrato: traccia d'ordine oltre la lingua.**
- **Lettura.** La cautela dell'e300 (blocchi di lingua contigui) spiega una parte dell'effetto (z da 8,5 a 5,7), non
  tutto: anche fra pagine della stessa sezione e della stessa lingua, quelle vicine nella rilegatura condividono più
  parole di frequenza media. È coerente con un testo scritto pagina dopo pagina, riprendendo parole delle pagine appena
  scritte, e con una rilegatura che in buona parte conserva quell'ordine. Resta possibile un ordine per argomento.

## 3/10/2026 — e297: gli errori sparsi da soli non spargono le parole rare del generatore

- **Preregistrato:** corpo dell'e288 più errori sparsi (una parola frequente diventa, con probabilità p, una sua variante
  di una modifica, in un punto qualsiasi del libro); p ∈ {0; 0,01; 0,02; 0,04; 0,08} sui semi 1–2, verifica sui 7–9.
- **Risultati:** R delle parole rare 52,5 → 50,2 al massimo (Voynich 1,96); scelta p 0,04: pagella 53 → 51, AUC
  0,833 / 0,933 → 0,835 / 0,937. **Esito preregistrato: non utili.**
- **Lettura.** Gli errori nuovi diventano quasi tutti hapax (una occorrenza) e non contano fra le rare (2–5); le rare del
  generatore restano confinate nella pagina dove nascono, perché il generatore prende le parole di base dalle parole della
  stessa pagina del Voynich. L'ipotesi di Davide (e296) resta sostenuta sul Voynich, ma nel generatore serve far
  **girare** le rare fra le pagine, non solo aggiungere errori: è il primo ritocco della v5 (`corpo5.circola`).

## 3/10/2026 — e291: il tema variato non migliora l'e288

- **Preregistrato:** τ (copie del tema sempre variate, e234) × rip × φ sopra l'e288; scelta sui semi 1–2 per pagella
  con la riga, verifica sui 7–9.
- **Risultati:** scelta τ 0, rip 0,4, φ 0,15 (cioè **senza** tema variato). Verifica: pagella 53 → 50, AUC 0,833 /
  0,933 → 0,841 / 0,939. Con τ > 0 l'AUC dell'e266 sale (0,94–0,97) e il gruppo G6 peggiora (0,72 → 0,78–0,85).
  **Esito preregistrato: non migliore.**
- **Lettura.** Variare sempre le copie del tema alza la varietà ma rompe le coppie ripetute (G6). La varietà del Voynich
  nella pagina va cercata altrove: parole rare che girano (e296) e scelte di grafia concordi nella riga (e206b).

## 3/10/2026 — Ciclo avversario, giro 4: i ritocchi previsti non migliorano; le classi di riga fatte per parola sono dannose

Prove di ricerca sui semi 1–2 (`voynichizzatore/prova_v4.py`, `prova_v4b.py`; i registri stanno in
`esecuzioni/voynichizzatore/`, fuori dal repo). Regola: prima la pagella (18 materie + 8 aggiunte, somma sui due semi),
poi l'AUC.

- **prova_v4** (cumulativa sopra l'e288):

  | passo | pagella | estese | riga | AUC e231 | AUC e266 |
  |---|---|---|---|---|---|
  | e288 | 34 | 0 | 1 | 0,857 | 0,931 |
  | + errori sparsi 0,02 | 34 | 0 | 1 | 0,855 | 0,930 |
  | + lunghezza stabile β 1 | 31 | 2 | 2 | 0,863 | 0,947 |
  | + rima delle desinenze ε 2 | 30 | 2 | 0 | 0,839 | 0,937 |
  | + successore già visto ω 0,1 | 29 | 1 | 0 | 0,822 | 0,936 |
  | + prime righe ρ 0,15 | 29 | 1 | 0 | 0,830 | 0,925 |

  Nessun passo migliora l'e288: ognuno prende al massimo una materia aggiunta e ne perde una o due delle 18.
- **prova_v4b, classi di riga per parola** (`corpo5.classi_riga`: per ogni riga e ognuna delle 12 classi dell'e206b
  una forma bersaglio; le parole in disaccordo passano alla compagna della coppia minima). Prende tipi e uniche nella
  pagina e, a f 1, le 12 scelte di riga, ma la pagella scende a 12–15 (si perdono gradiente, legame, Zipf, formule, h2)
  e l'AUC sale a 0,91–0,98 (e231) e 0,955–0,996 (e266): G2, G4, G6 salgono a 0,8–0,93. **Scartate.** Fermata la prova
  dopo 8 lavori su 16 (le configurazioni restanti contenevano tutte le classi). Come nell'e252: cambiare parola per
  imitare le scelte di riga si vede; la concordanza di riga del Voynich non nasce da sostituzioni di parole intere.
- **Prove veloci sul seme 1** (solo misure aggiunte, per progettare la v5):
  - parole rare che girano (`corpo5.circola`, scambi fra pagine della stessa sezione con gli stessi bordi): R delle
    rare 56 → 24 (chiave stretta), 19,5 (larga), 11,3 (rare fino a 10 occorrenze), **6,7** (con compagne di riserva);
    tipi su parole nella pagina 0,680 → 0,709, uniche 0,539 → 0,586; coppie viste altrove invariate;
  - bordi legati nella riga (`corpo6`, tabelle dei passaggi finale→finale e prefisso→prefisso imparate dal Voynich;
    identico a `corpo4` a manopole spente, verificato): λ_fin 1 → concordanza delle desinenze 0,016 → **0,053**
    (Voynich 0,043), scelte di riga 3 → 5; λ_fin 2 + λ_pre 1 → concordanza 0,097 (troppa), scelte di riga 8, coppie
    viste altrove **0,226** (Voynich 0,221).
- Da qui la prova_v5: circolazione delle rare (v4), più bordi legati e ω 0,2 dalla ricerca dell'e292 (v5).

## 3/10/2026 — e292: le coppie ripetute (ω) non migliorano l'e288 sui semi di verifica

- **Preregistrato:** ω (la prima candidata riprende una parola che seguiva già la parola precedente altrove nel testo) ×
  τ (tema variato) sopra l'e288; scelta sui semi 1–2 per pagella con la riga, verifica sui 7–9.
- **Ricerca:** scelta ω 0,2, τ 0 (pagella 36 sui semi 1–2 con la riga in tutti e due; e288 34). Con τ 1 la pagella
  crolla (12–16) come nell'e291.
- **Verifica** (semi 7–9): pagella 53 → **47** (perde curva piatta, profilo pagina, formule), riga in 3 semi; AUC
  0,833 / 0,933 → 0,851 / 0,934; G3 0,870 → 0,857, G6 0,721 → 0,696. **Esito preregistrato: non migliore.**
- **Lettura.** Il +2 di pagella sui semi di ricerca era rumore (effetto vincitore, terza volta oggi): con due semi, una
  differenza di 2 punti di pagella non dice niente. Per il ciclo avversario: un ritocco si adotta solo se migliora di
  più del rumore fra semi (almeno 4 punti di pagella estesa, o 0,02 di AUC), e si verifica sempre sui semi 7–9.

## 3/10/2026 — Ciclo avversario, giro 5: bordi legati e parole rare che girano abbassano l'AUC, ma costano pagella

`voynichizzatore/prova_v5.py`, semi di ricerca 1–2 (somme sui due semi; e288 = corpo della v3):

| configurazione | pagella | estese | riga | AUC e231 | AUC e266 |
|---|---|---|---|---|---|
| e288 | 34 | 0 | 1 | 0,857 | 0,931 |
| ω 0,2 | 36 | 0 | 2 | 0,859 | 0,938 |
| circola (rare fino a 10, compagne di riserva) | 29 | 2 | 0 | 0,863 | 0,950 |
| bordi λ_fin 1, λ_pre 1 | 32 | 4 | 0 | 0,832 | 0,934 |
| bordi 0,7 / 1 | 31 | 2 | 0 | 0,851 | 0,943 |
| circola + bordi 1 / 1 | 31 | 2 | 0 | **0,804** | **0,928** |
| circola + bordi 0,7 / 1 | 29 | 2 | 0 | 0,836 | 0,952 |
| circola + bordi 1 / 1 + ω 0,2 | 29 | 3 | 0 | 0,847 | 0,950 |

- I **bordi** prendono concordanza delle desinenze e coppie viste altrove e abbassano G4 (inizio riga, 0,63 → 0,52) ma
  alzano G6 (0,72 → 0,81) e perdono sempre "ripetizione": premiavano anche la ripetizione della parola precedente
  (stesso prefisso e stesso finale). Corretto nel giro 6.
- La **circolazione** porta R delle rare a 6,5–6,7 e abbassa G3 (0,866 → 0,81: il primo vero passo sul "muro" della
  varietà nella pagina dopo l'e251b), ma perde omogeneità, legame e curva piatta e alza G4 (0,63 → 0,73). Prove veloci
  sul seme 1: anche scambiando solo fra parole nella stessa posizione della riga, o solo fra pagine vicine (2 o 6
  pagine), omogeneità e legame si perdono. Le rare del generatore portano il "legame" con le parole vicine; spostarle
  lo rompe.
- **Insieme** (circola + bordi 1/1): l'AUC dell'e231 più bassa mai vista sui semi di ricerca (0,804 e 0,791/0,817 per
  seme), con G3 0,78–0,79 e G4 0,57.
- Le classi di riga **per selezione** fra le candidate (`corpo6`, λ_cl), invece che per sostituzione: sul seme 1, con i
  bordi, λ_cl 0,3 porta le scelte di riga a **11 su 12** (Voynich 12, generatore 2–3) con concordanza 0,045 e coppie
  0,236 (Voynich 0,043 e 0,221); λ_cl 1 esagera (tipi su parole 0,55: premia le parole già nella riga, corretto).
- ω 0,2 non entra: l'e292 mostra che il +2 era rumore.

## 3/10/2026 — Ciclo avversario, giro 6: nascono la v4 (bordi + scelte di riga) e la v5 (+ lessico globale)

`voynichizzatore/prova_v6.py` e `prova_v6b.py`, semi di ricerca 1–2 (somme; regola: almeno +4 di pagella estesa, oppure
−0,02 di AUC a pagella estesa non peggiore):

| configurazione | pagella | estese | totale | riga | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| e288 (corpo della v3) | 34 | 0 | 34 | 1 | 0,857 | 0,931 |
| bordi 1/1 (senza premio alla ripetizione) | 31 | 2 | 33 | 0 | 0,838 | 0,936 |
| bordi 0,7/0,7 | 35 | 2 | 37 | 0 | 0,836 | 0,940 |
| **bordi 1/1 + classi 0,3 → v4** | 33 | 6 | **39** | 1 | 0,863 | 0,944 |
| bordi 0,7/0,7 + classi 0,3 | 33 | 5 | 38 | 1 | 0,856 | 0,932 |
| bordi 1/1 + classi 0,5 | 29 | 4 | 33 | 0 | 0,867 | 0,931 |
| **bordi 1/1 + classi 0,3 + δ 0,2 → v5** | 33 | 6 | **39** | 0 | **0,816** | **0,923** |
| bordi 1/1 + classi 0,3 + α 1,3 | 29 | 5 | 34 | 1 | 0,859 | 0,926 |
| bordi 1/1 + circola pos | 29 | 3 | 32 | 0 | 0,820 | 0,942 |
| bordi 1/1 + classi 0,3 + circola pos | 29 | 6 | 35 | 0 | 0,821 | 0,936 |
| bordi 1/1 + classi 0,3 + circola pos 0,5 | 32 | 6 | 38 | 1 | 0,821 | 0,934 |
| bordi 1/1 + classi 0,3 + circola | 29 | 6 | 35 | 0 | 0,839 | 0,944 |

- **v4** = corpo dell'e288 + bordi legati nella riga (λ_fin 1, λ_pre 1) + scelte di riga per selezione (λ_cl 0,3):
  +5 di pagella estesa. Le materie nuove prese su ogni seme: **scelte di riga** (12 classi concordi nella riga),
  **concordanza delle desinenze**, **coppie viste altrove**. È la prima volta che il generatore prende materie della
  pagella estesa senza perderne altrettante.
- **v5** = v4 + δ 0,2 (una parola di base su cinque dal lessico di tutto il libro invece che dalla pagina, e232): stessa
  pagella estesa, AUC −0,047 (e231) e −0,021 (e266). G3 0,875 → 0,84: le parole "della pagina" erano una parte del muro.
- Verifica in corso: banco e293 con v3, v4, v5 sui semi 7–9, con Isidoro XVII nascosto e la decodifica controllata.

## 3/10/2026 — e293, banco della v4 e della v5: più materie aggiunte, ma il cancello della riga si perde

Banco preregistrato dell'e293 (`esegui.py e293 -- --v3 --v4 --v5`): Isidoro XVII nascosto con la chiave "banco", corpi
con i semi di verifica 7, 8, 9. **Decodifica esatta in tutti e nove i manoscritti.**

| versione | pagella (3 semi) | pagella estesa | riga | AUC e231 | AUC e266 | mancate fra le 18 |
|---|---|---|---|---|---|---|
| v3 | 52/54 | 52/78 | 2 semi | 0,817 | 0,934 | profilo pagina, omogeneità |
| v4 | 50/54 | **59/78** | 0 | 0,843 | 0,931 | gradiente (3), omogeneità |
| v5 | 49/54 | 57/78 | 0 | **0,816** | **0,917** | gradiente (3), deriva, profilo pagina |

- **Prese su tutti i semi** dalla v4: scelte di riga, concordanza delle desinenze, coppie viste altrove (la v5 manca le
  scelte di riga su un seme). Mancano ancora: parole rare per pagina, tipi e uniche nella pagina, dispersione delle
  lunghezze, prime righe come registro.
- **Esito**, con il criterio usato per la v3 (AUC dell'e266 almeno −0,01 a pagella estesa non inferiore): la **v5
  migliora la v3** (−0,017, pagella estesa +5); la v4 no (AUC dell'e266 −0,003). **Ma** v4 e v5 perdono il cancello
  della riga in tutti i semi e la materia "gradiente": è un costo vero, da riparare prima di dire che la v5 è migliore
  in tutto.
- **Causa** (seme 1, valori grezzi): gradiente = somiglianza fra righe a distanza 6 / somiglianza nella riga: Voynich
  0,034/0,038 = 0,89; v3 0,022/0,031 = 0,71; v4 0,027/0,046 = 0,59; v5 0,020/0,036 = 0,56. I bordi e le classi alzano la
  somiglianza dentro la riga, il lessico globale abbassa quella fra righe lontane della stessa pagina. Nel cancello cade
  A (somiglianza fra parole vicine oltre il caso, soglia 1,0): v3 1,026, v4 1,012, v5 0,983, solo bordi 0,974.
- **Diagnosi della v5** con lo strumento unico (Isidoro, chiave "giardino"; AUC 0,810 / 0,915): pesano di più le prime
  righe dei paragrafi (G8: *p* +0,0315 nel Voynich, +0,012 nella v5; *f* +0,008 contro +0,0015), la varietà nella
  pagina (G3) e le coppie identiche (G6: 0,0205 contro 0,0097).
- Giri in corso: 7 (più lessico globale, circolazione leggera), 8 (*p*/*f* nelle prime righe, ripetizioni, lunghezze),
  9 (tema della pagina θ e varianti della parola precedente χ, contro il gradiente e A).

## 3/10/2026 — Ciclo avversario, giro 7: nasce la v6 (v5 + penalità per le ripetizioni più forte)

`voynichizzatore/prova_v7.py`, dalla v5, semi di ricerca 1–2 (somme):

| configurazione | pagella | estese | totale | riga | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| v5 | 33 | 6 | 39 | 0 | 0,816 | 0,923 |
| δ 0,3 | 31 | 6 | 37 | 0 | 0,811 | 0,921 |
| δ 0,4 | 32 | 5 | 37 | 0 | 0,794 | 0,919 |
| + circola pos 0,5 | 32 | 5 | 37 | 0 | 0,821 | 0,924 |
| bordi 0,7/0,7 | 31 | 4 | 35 | 0 | 0,813 | 0,930 |
| **rip 0,4 → v6** | 33 | 6 | **39** | 0 | **0,782** | **0,903** |
| δ 0,3 + circola pos 0,5 | 29 | 7 | 36 | 0 | 0,817 | 0,934 |
| classi 0,4 | 33 | 5 | 38 | 0 | 0,783 | 0,904 |

- **v6** = v5 con la penalità per la ripetizione immediata della stessa parola da 0,5 a 0,4: pagella estesa uguale,
  AUC −0,034 / −0,020. Coerente con la diagnosi della v5 (coppie identiche il doppio del Voynich).
- Il cancello della riga resta perso in tutte le configurazioni (giro 9). Banco della v6 sui semi 7–9 in corso.

## 3/10/2026 — Ciclo avversario, giro 8: p e f nelle prime righe abbassano molto il discriminatore forte

`voynichizzatore/prova_v8.py`, dalla v5, semi 1–2 (somme). `corpo5.galli_prime`: nelle prime righe dei paragrafi un
gallows *k*/*t* (anche *ckh*/*cth*) diventa *p*/*f* con probabilità su × (0,27 per *k*, 0,14 per *t*); nelle altre righe
*p*/*f* diventa *k*/*t* con probabilità giù. Le quote vengono dai conteggi: nel Voynich *p* è il 3,3% dei segni nelle
prime righe e lo 0,17% nelle altre (venti volte), nella v5 1,7% e 0,56%.

| configurazione | pagella | estese | totale | riga | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| v5 | 33 | 6 | 39 | 0 | 0,816 | 0,923 |
| galli 1/0,7 | 33 | 6 | 39 | 0 | 0,826 | **0,861** |
| galli 1/0 | 33 | 6 | 39 | 0 | 0,836 | 0,884 |
| galli 1,3/0,7 | 33 | 6 | 39 | 0 | 0,826 | 0,862 |
| rip 0,3 | 31 | 6 | 37 | 0 | 0,806 | 0,923 |
| galli 1/0,7 + rip 0,3 | 32 | 6 | 38 | 0 | 0,826 | 0,862 |
| galli 1/0,7 + β 0,5 | 33 | 6 | 39 | 1 | 0,839 | 0,873 |
| galli 1/0,7 + rip 0,3 + β 0,5 | 32 | 5 | 37 | 0 | 0,829 | 0,841 |

- Il gruppo G8 dell'e266 (prime righe) scende da 0,87 a 0,66–0,69; l'AUC dell'e266 −0,062, il passo più grande del
  giorno su quel discriminatore. L'e231 (che non guarda le prime righe) +0,010.
- La misura "prime righe come registro" (e273) sale da −2,3/+0,2 a −0,7/+1,3 (Voynich 4,7): i gallows sono una parte
  del registro delle prime righe, non tutto.
- Giro 10: lo stesso ritocco sopra la v6.

## 3/10/2026 — e293, banco della v6: non confermata (effetto vincitore, quarta volta)

| versione | pagella (3 semi) | pagella estesa | riga | AUC e231 | AUC e266 |
|---|---|---|---|---|---|
| v5 | 49/54 | 57/78 | 0 | 0,816 | 0,917 |
| v6 (v5 + rip 0,4) | 46/54 | 55/78 | 0 | 0,827 | 0,936 |

- Decodifica esatta nei tre manoscritti. Sui semi 1–2 la v6 abbassava l'AUC di 0,034/0,020; sui semi 7–9 la alza di
  0,011/0,019. **La v6 non è confermata; la versione migliore verificata resta la v5.**
- **Lezione di metodo.** L'AUC di un solo seme varia di circa 0,03 (v3 sui semi 7–9: 0,850, 0,804, 0,798): la media
  di due semi ha un errore di circa 0,02, quindi la soglia di 0,02 della regola dei giri è dentro il rumore. Da ora i
  giri scelgono su **quattro semi di ricerca (1–4)** e un ritocco conta solo se abbassa l'AUC di almeno 0,03, oppure
  è mirato a un gruppo del discriminatore e lo abbassa nettamente (come le prime righe: G8 da 0,87 a 0,67).

## 3/10/2026 — e302–e306: cinque misure che mostrano che cosa il generatore vecchio non aveva capito

Preregistrato (`preregistrazioni/e302.md`); Voynich contro il corpo della v5 sui semi di ricerca 1–3.

- **e302, registro delle prime righe** (prime righe dei paragrafi − altre righe, z con permutazioni dentro la pagina).
  Nel Voynich: lunghezza delle parole **+0,42 segni (z 14,7)**; parole che iniziano con *ch* −0,067 (z −12,7), con *sh*
  +0,033 (z 9,2), con *p* +0,062 (z 31,6), con *f* +0,011, con *t* +0,018; finali in *y* +0,031, in *n* −0,039 (z −8,7),
  in *r* +0,020; segni *p* +0,035, *f* +0,009, *k* −0,020. Il generatore (v5) manca 11 di queste 16 differenze: le
  prime righe sono un **registro intero** (parole più lunghe, *sh* invece di *ch*, -*y* invece di -*aiin*), non solo i
  gallows *p*/*f*.
- **e303, somiglianza fra righe e distanza** (rispetto alla distanza 1). Voynich: **dentro la riga 0,965** (le parole
  della stessa riga si somigliano un po' meno di quelle della riga sotto), poi 0,91 a 2 righe, 0,82 a 8, 0,91 a 12–16:
  non scende mai sotto metà. Generatore: dentro la riga **1,30**, poi piatta e perfino in salita (1,09 a 16).
  **Lettura:** nel Voynich la riga non è un'unità di copia; il generatore vecchio costruiva la riga copiando e variando
  le parole vicine (χ, ripetizioni, bordi), un'ipotesi sbagliata alla base.
- **e304, errori ricorrenti.** Le 975 varianti rare (a una modifica da una parola frequente) tornano in media ogni 2,96
  occorrenze, su pagine **più vicine del caso** (56,1 pagine contro 61,4 del nullo nella stessa sezione, **z −5,4**;
  il 20% ha due occorrenze entro 3 pagine). **Esito preregistrato: errori ricorrenti vicini.** Nel generatore z −0,2…
  +2,0 (14% entro 3 pagine). Con l'e300: la grafia dello scriba cambia nel tempo; una variante resta in uso per qualche
  pagina.
- **e305, coppie identiche.** Voynich 0,94% delle coppie vicine (generatore 1,8%); in fine riga l'8% (generatore 15%).
  Il Voynich ripete parole **lunghe** (*chol* 24, *qokeedy* 18, *qokedy* 16, *qokeey* 12, *daiin* 11); il generatore
  parole corte (*ol* 49–61, *ar*, *daiin*, *or*, *al*).
- **e306, lunghezze per posizione.** Il generatore è più corto ovunque: parole di 1 segno 4,6% (Voynich 3,3%), di 2 segni
  11,3% (8,4%), di 6 segni 13,8% (15,6%); prime righe, parola mediana 4,22 contro 4,82. Le spezzature e i prefissi
  staccati del generatore (e236) fanno troppi frammenti corti.
- **Uso.** Queste proprietà non si aggiungono come toppe: il **modello del Voynich** (`voynichizzatore/modello.py`, voce
  seguente) le prende dal testo condizionando sul tipo di riga e sulla posizione, senza copia dentro la riga e con le
  pagine vicine.

## 3/10/2026 — Cambio d'impianto: dal generatore "copia e modifica" a un modello del Voynich

- **Perché** (discusso con Davide alle 19:15). In un giorno di ciclo avversario il generatore vecchio è rimasto fra 0,82
  e 0,92 di AUC: ogni meccanismo nuovo ne rompeva un altro (bordi contro gradiente, lessico globale contro
  omogeneità), quattro scelte su due semi non hanno retto la verifica (e283, e253, e292, v6), e l'e303 mostra che una
  delle sue basi (la riga costruita copiando i vicini) è sbagliata. Fermati i giri 9 e 10 senza risultati.
- **Il modello:** ogni parola viene da una mescolanza di componenti, ognuna legata a una proprietà trovata: lessico della
  pagina, coppia con la parola precedente nella riga (e285, e295), parole che seguono lo stesso segno finale (e294),
  memoria della pagina, pagine precedenti (e300, e304), lessico per sezione × tipo di riga × posizione (e273, e302),
  lessico del libro, riga sopra (verticale), parola nuova come variante di una parola frequente (e296). I pesi per
  gruppo (tipo di riga × posizione) si stimano per **massima verosimiglianza sul Voynich, con ogni componente calcolata
  senza la pagina in esame** (il modello non impara a copiare la pagina che scrive).
- **Prima cosa che il modello insegna** (pesi stimati):
  - righe normali, parole in mezzo: sezione 0,31, **segno finale della parola precedente 0,20**, pagina 0,16, libro
    0,13, parola nuova 0,09, coppia esatta 0,03, memoria 0,004, **riga sopra 0,004**;
  - prima parola dei paragrafi: **parola nuova 0,47**;
  - ultima parola della riga: segno finale precedente 0,15, parola nuova 0,21.
  - **Lettura:** la parola si prevede dalla sezione e dal **bordo** della parola precedente, quasi per niente dalla
    coppia esatta; la riga sopra e la memoria non aggiungono nulla al lessico della pagina (la "verticalità" del Voynich
    è lessico di pagina, non copia). Il generatore vecchio aveva meccanismi di copia verticale e di riga che il testo non
    sostiene.
- Prova in corso: pagella, pagella estesa, AUC sui semi 1–4, contro la v5.

## 3/10/2026 — Modello del Voynich: il primo prototipo fallisce e insegna due cose

- **Prototipo 1** (lessico della pagina vera come componente; legame col segno finale come fonte di parole), semi 1–4:
  pagella 6–7/18, AUC **0,988 / 0,998** (v5 sugli stessi semi: 66/72 di pagella, 0,812 / 0,918). Pagine troppo varie
  (tipi su parole 0,836 contro 0,756), troppo pochi hapax (0,091 contro 0,137), legame fra finali vicini 0,009 contro
  0,024, coppie riviste altrove 0,15 contro 0,24. Copia di trigrammi dal Voynich 0,2% (nessuna copia).
- **Errore di costruzione:** la componente "pagina vera" (con la sola parola tolta) vede anche le parole che vengono dopo
  nella pagina e prende il posto della memoria; in generazione restano solo fonti indipendenti. Corretto togliendola: la
  ripetizione nella pagina deve venire dalla memoria di ciò che è già scritto.
- **Seconda forma:** fonti (memoria, pagine vicine, coppia, sezione, posizione, libro, nuova; pesi per verosimiglianza) e
  scelta fra 16 candidate con i legami ai bordi del Voynich (finale→finale, finale→prefisso, prefisso→prefisso).
- **Prima cosa capita** dalla taratura sul seme 1: alzando la memoria la varietà nella pagina va a posto, ma le coppie
  identiche vicine raddoppiano (0,02–0,03 contro 0,0094). Il Voynich **ripete le parole nella pagina ma le evita nella
  stessa riga** (lo diceva l'e303: nella riga le parole si somigliano meno che con la riga sotto). Con la memoria fatta
  delle **righe precedenti** della pagina le coppie identiche scendono a 0,009–0,014.
- **Taratura** (metodo dei momenti sul seme 1, memoria ×2, coppia ×3, legami 1,5): varietà nella pagina 0,763 (Voynich
  0,756), hapax 0,130 (0,137), coppie riviste altrove 0,240 (0,241), legame fra finali 0,0240 (0,0237), coppie
  identiche 0,0138 (0,0094); lunghezza delle parole 4,62 (4,46: ancora lunghe). Prova con i discriminatori sui semi 1–4
  in corso.

## 3/10/2026 — e307: ogni pagina ha un'identità forte, lungo un solo asse (-edy contro -aiin), condivisa con la pagina accanto

Preregistrato (`preregistrazioni/e307.md`). 183 pagine con almeno 60 parole, 9 strati sezione × lingua; nullo = parole
rimescolate fra le pagine dello stesso strato.

- **A, identità oltre sezione e lingua** (distanza media pagina-strato, rapporto sul nullo e z):
  - **Voynich:** segni **2,83 (z 70)**, parole 1,08 (z 28), iniziali e finali **2,35 (z 57)**;
  - controllo positivo, Bibbia latina in pagine: 1,75 (z 49), 1,07 (z 64), 1,84 (z 47);
  - controllo negativo, Voynich rimescolato: 1,01, 1,00, 1,01 (|z| < 0,5).
  - **Esito preregistrato: pagine con identità.** Per i segni il Voynich ha più identità di pagina della Bibbia, dove
    le pagine cambiano libro e argomento.
- **B, in che cosa consiste:** le caratteristiche con più varianza in eccesso sono i segni ***e*** (9,0 volte il
  nullo), *a* (4,9), *n* (4,7), *y* (4,6), *ch* (4,6), l'iniziale *o* (4,5), *d* (4,4), la finale *y* (4,4),
  l'iniziale *ch*, la finale *n*, *i*, *o*, *m*, la lunghezza. Non distinguono le pagine: *c*, *h*, la parola *al*,
  *cfh*, l'iniziale *p*.
- **C, da dove viene** (correlazione fra profili di pagine dello stesso strato):

  | coppie | correlazione | z |
  |---|---|---|
  | **consecutive** | **0,209** | **10,9** |
  | vicine (2–5) | −0,018 | 1,2 |
  | stessa mano (> 5) | −0,024 | −5,5 |
  | stesso fascicolo (> 5) | 0,015 | 4,6 |
  | altre (> 5) | −0,074 | −3,8 |

  **Esito preregistrato: temporale e di fascicolo.**
- **D, tipi di pagina:** silhouette 0,084 con k = 2, contro 0,048 del nullo, z 3,2. **Esito preregistrato: tipi di
  pagina.** I due gruppi sono i due estremi dello stesso asse:
  - gruppo 0: meno *e* e -*y*, più *a*, *i*, *n*, -*n*, cioè parole in -*aiin*/-*ain*;
  - gruppo 1: l'opposto, parole in -*edy*/-*eey*.

  Tutti e due i gruppi sono distribuiti in tutte le sezioni, in tutte e due le lingue e in tutte le mani.
- **Lettura** (scritta dopo i risultati):
  1. L'identità di una pagina è soprattutto la sua **posizione su un asse "-edy/-eey contro -aiin/-ain"**. È lo stesso
     asse che separa le lingue A e B di Currier, ma qui vale **dentro** ogni lingua e ogni sezione. A e B sembrano più
     gli estremi di un continuo che due sistemi separati.
  2. Il silhouette basso (0,08) dice che i "tipi" sono deboli: più che due tipi, un continuo con due estremi.
  3. **Le pagine consecutive** condividono l'identità (z 10,9), quelle a 2–5 pagine di distanza **no** (z 1,2). Questo
     fa pensare a un'unità fisica di due pagine: le due facce dello stesso foglio, o le due pagine affiancate di
     un'apertura. Da verificare con un esperimento apposito.
  4. Le pagine della stessa mano **non** si somigliano di più. Lo z negativo viene dal confronto con tutte le coppie,
     che comprendono le consecutive: fra le coppie lontane, stessa mano −0,024 contro −0,074 delle "altre". Il
     fascicolo conta un poco.
- **Per il voynichizzatore** (da segnalare all'altra chat): una pagina generata deve stare in un punto preciso
  dell'asse *e* contro *a*/*i*/*n* e condividerlo con la pagina accanto. È probabilmente il G9 che il modello del
  Voynich non riproduce.

## 3/10/2026 — e308, e309, e312: l'unità di scrittura è il bifoglio, non la pagina che segue

Preregistrato (`preregistrazioni/e308.md`). Profili di pagina dell'e307, 183 pagine; struttura fisica dalle intestazioni
della ZL (`$Q` fascicolo, `$F` foglio, `$B` bifoglio).

- **e308, quale unità condivide l'identità** (correlazione media fra profili, z con permutazioni dentro lo strato):

  | coppie | numero | correlazione | z |
  |---|---|---|---|
  | **stesso foglio** (recto e verso) | 91 | **0,285** | **11,5** |
  | **bifoglio, stessa faccia** | 80 | **0,197** | **8,1** |
  | **bifoglio, facce opposte** | 84 | **0,206** | **7,9** |
  | pannelli dello stesso lato (pieghevoli) | 11 | 0,212 | 3,8 |
  | apertura (verso + recto seguente, affiancate) | 80 | 0,048 | 2,4 |
  | stesso fascicolo, altro | 930 | −0,034 | −1,9 |

  Stesso foglio contro apertura: +0,237, z 6,2. **Esito preregistrato: unità fisiche = stesso foglio, bifoglio
  (tutte e due le facce), pannelli; non l'apertura.**
- **e309, l'asse -edy/-aiin:**
  - BIC: 1 componente 1005, 2 componenti 1013. Media A −0,58, B +0,80. Sovrapposizione: 67% delle pagine A sopra il
    25° percentile delle B, 48% delle B sotto il 75° delle A. **Esito: continuo.**
  - Autocorrelazione nell'ordine del libro, dentro lo strato: passo 1 **0,336 (z 4,7)**, passo 2 0,151 (2,1), passo 3
    0,06, passo 5 0,06, passo 10 −0,11. **Esito: coppie di pagine** (non deriva lenta).
- **e312, l'ordine dalle somiglianze:** in nessuno strato l'ordinamento spettrale ritrova l'ordine del libro (z da
  −0,2 a 1,6; complessivo 1,6). **Esito: no.**
  - 9 pagine sono più simili a pagine lontane che alle vicine: f1v, f2r, f2v, f4r, f7r, f52v, f53r, f90r1, f88r. Le
    elenco senza dichiararle spostate.
- **Lettura** (scritta dopo i risultati):
  1. L'identità di una pagina è condivisa dalle **pagine dello stesso pezzo di pergamena**: le due facce del foglio e
     il foglio coniugato del bifoglio, che nell'ordine di lettura sta lontano (per esempio f1 e f8). Non è condivisa
     dalla pagina affiancata nell'apertura, né dagli altri fogli dello stesso fascicolo.
  2. È quello che ci si aspetta se lo scriba ha scritto **un bifoglio alla volta**, ognuno in un suo "stato" (punto
     sull'asse -edy/-aiin, abitudini), e i bifogli sono stati poi piegati e cuciti.
  3. Spiega anche l'e300 (pagine consecutive simili: sono soprattutto recto e verso dello stesso foglio) e perché
     l'ordine del libro non si ricostruisce per somiglianza: l'ordine di lettura alterna bifogli diversi.
  4. È coerente con l'idea, nella codicologia recente, che il manoscritto sia stato scritto su bifogli sciolti e
     rilegato dopo, forse non nell'ordine di scrittura.
  5. A e B, su questo asse, si sovrappongono molto: la differenza fra le due "lingue" non sta tutta qui.
- **Per il voynichizzatore** (da segnalare all'altra chat): lo "stato" va scelto per bifoglio, non per pagina, ed è lo
  stesso sulle quattro pagine del bifoglio.

## 3/10/2026 — e310, e311: le parole d'inizio paragrafo sono quasi tutte "gallows + parola"; le etichette non tornano nel testo

Preregistrato (`preregistrazioni/e310.md`, con la correzione del controllo prima dell'esecuzione).

- **e310:**

  | misura | prime parole dei paragrafi | prime parole delle altre righe | parole in mezzo |
  |---|---|---|---|
  | parole uniche | 47,7% | 17,5% | 10,8% |
  | iniziano con un gallows | **83,4%** | 9,0% | 8,8% |
  | gallows + parola nota (≥ 2 occorrenze) | **53,8%** | 7,3% | 6,3% |
  | fra le uniche: gallows + parola nota | 33,4% | 5,1% | 5,7% |
  | fra le uniche con gallows: resto noto | 37,9% | 44,1% | 44,1% |
  | fra le uniche: togliendo il 1°/2°/ultimo segno resta una parola nota | 35% / 14% / 3% | 44% / 17% / 8% | 32% / 20% / 10% |

  - Fra le uniche, "gallows + parola nota" vale 33,4% contro 4,4% delle parole in mezzo a pari lunghezza, z 26,8.
    **Esito preregistrato: prefisso meccanico.**
  - Il 65% delle parole uniche d'inizio paragrafo resta nuovo anche togliendo il primo segno.
  - **Lettura, con una cautela:** il paragrafo comincia quasi sempre con una parola che inizia con un gallows (83%
    contro 9%), e metà delle prime parole è un gallows davanti a una parola comune. Però, fra le parole uniche che
    iniziano con un gallows, il resto è una parola nota tanto spesso quanto altrove (38% contro 44%): il "gallows +
    parola" è una proprietà di tutte le parole con il gallows iniziale, e l'inizio del paragrafo sceglie soprattutto
    quelle. Due terzi delle parole d'inizio uniche restano forme nuove: il prefisso spiega una parte, non tutto.
- **e311, etichette e testo:** 35 pagine, 770 parole d'etichetta. Nel testo della propria pagina: esatte 12,1%
  contro 11,1% del nullo (z 1,1); a una modifica 44,2% contro 40,6% (z 2,3). Controllo positivo z 4,4 (potenza
  limitata: poche pagine). **Esito preregistrato: incerto.** Le etichette non ricompaiono nel testo della propria
  pagina più che in quello di un'altra pagina della stessa sezione.

## 3/10/2026 — e313: l'ultima riga del paragrafo ha un registro suo; le righe non sono regolate sul margine

Preregistrato (`preregistrazioni/e313.md`, con la correzione della parte B prima dell'esecuzione).

- **A, ultime righe contro righe interne** (|z| > 3):
  - parole che iniziano con ***q*** −4,8 punti (z −8,2), con *ch* +3,5 (z 4,8), con *s* +0,5 (z 3,9), con *y* +1,3
    (z 4,0);
  - segni *t* −1,0 (z −6,5) e *k* −0,6 (z −3,8);
  - 2,9 parole in meno.
  - **Esito: registro dell'ultima riga** (6 caratteristiche oltre al numero di parole). Le ultime righe hanno meno
    parole in *qo*- e meno gallows: il contrario delle prime righe, che hanno più gallows (e302).
- **B, margine destro:**
  - log del rapporto di varianza dei segni per riga: Voynich −1,10; stesse parole a capo a larghezza fissa −1,63;
    latino a 40 lettere −2,76;
  - differenza appaiata +0,54, z 4,95. **Esito: righe meno regolate di un normale a capo.**
  - Le righe del Voynich hanno lunghezze più irregolari di un testo che va a capo a larghezza fissa. È coerente con
    righe la cui larghezza cambia (testo intorno ai disegni), non con parole adattate allo spazio.
  - Misura complementare: l'ultima parola della riga è più corta delle altre della stessa riga di 0,17 segni oltre il
    caso (z −3,6). Un piccolo segno di parole accorciate o scelte corte in fine riga.

## 3/10/2026 — vz: e400, la scala dei controlli: per i giudici contano i bordi della riga, non l'ordine delle righe; il nascondiglio da solo vale 0,63

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e400.md`): testi fatti dal Voynich vero con l'impaginazione
vera e un solo livello rotto, passati ai giudici e231 ed e266; semi 1–4. Risultati in `risultati/e400_scala_controlli.md`.

- **Controlli del metro: validi.** Voynich tale e quale AUC 0,500; parole da tutto il libro 1,000; decodifica esatta.

| gradino | AUC e231 | AUC e266 | prevista (e266) | gruppi che si accendono |
|---|---|---|---|---|
| O1, righe rimescolate nella pagina | 0,481 | 0,595 | 0,50–0,58 | G9 0,62 |
| O2, parole rimescolate dentro la riga | 0,984 | **0,990** | 0,60–0,72 | G4 0,98, G7 0,93, G6 0,66 |
| O3, parole rimescolate nella pagina (prime righe a parte) | 0,988 | 0,993 | 0,75–0,85 | G4 0,99, G7 0,94, G6 0,70, G9 0,65 |
| O4, parole rimescolate in tutta la pagina | 0,989 | 0,998 | 0,80–0,90 | in più G8 0,96 |
| L1, ripescate dalla pagina con reimmissione | 1,000 | 1,000 | 0,88–0,95 | in più G3 1,00 |
| L2, dalle pagine vicine (±2) | 0,997 | 1,000 | 0,90–0,97 | G3 0,98, G9 0,67 |
| L3, da sezione × lingua | 0,998 | 1,000 | 0,95–0,99 | G3 0,98, G9 0,75 |
| L4, da tutto il libro | 1,000 | 1,000 | ≥ 0,98 | G3 0,99, G9 0,96 |
| N1, Voynich con Isidoro nascosto | 0,622 | **0,630** | 0,50–0,60 | G2 0,61 |

- **Previsioni sbagliate, e perché.** Avevo previsto O2 a 0,60–0,72: è 0,99. Rimescolare le parole dentro la riga
  basta a farsi riconoscere quasi sempre. Il motivo sta nei **bordi della riga**, non nell'ordine in mezzo:
  - righe che iniziano con *p* 7,7% → 0,9%; con *t* 10,5% → 3,3%; con *ch* 3,6% → 16,7%;
  - prima parola della riga 4,82 segni → 4,34;
  - righe che finiscono in *m* 13,9% → 2,9%; in *o* 1,2% → 4,8%;
  - coppie vicine che unite danno una parola attestata 9,2% → 5,6%.
  L'ordine delle parole **in mezzo** alla riga pesa molto meno (G6 0,66; G5 0,52).
- **L'ordine delle righe nella pagina non conta quasi niente** (O1 0,48 / 0,60). L'unica traccia: le due metà della
  pagina sono più diverse fra loro del caso (JSD 0,050 contro 0,038): il profilo dei segni scivola lungo la pagina.
- **Le prime righe dei paragrafi** contano quanto i bordi (G8 0,96 appena le loro parole si mescolano alle altre).
- **Le parole della pagina:** ripescarle con reimmissione rompe da solo la varietà (G3 1,00: tipi su parole 0,756 →
  0,514). Prendendo le parole dalle pagine vicine o dalla sezione, il profilo di pagina (G9) sale solo a 0,67–0,75;
  con tutto il libro a 0,96. L'identità della pagina è in buona parte identità di **sezione e lingua**.
- **Il nascondiglio da solo si vede un poco: 0,62 / 0,63** (soglia preregistrata 0,60). Riscrive il 51,7% delle
  parole. Lo tradiscono le coppie di parole viste altrove (0,221 → 0,205: due occorrenze della stessa coppia ricevono
  scelte diverse) e alcune coppie di segni (*l*+*sh*, *p*+*sh*). Con questo canale l'obiettivo 0,6 non si raggiunge
  nemmeno con un corpo perfetto: il canale va migliorato (meno posti toccati, o scelte legate alla parola intera).
- **Esito secondo la preregistrazione:** O4 ≥ 0,75, quindi il primo pezzo da costruire è **la disposizione** delle
  parole (quali parole nelle prime righe, quali a inizio e fine riga, poi le coppie), tenendo le parole vere della
  pagina; e N1 > 0,60, quindi il nascondiglio è da rifare.
- **Lettura per la ricerca sul Voynich.** La riga è un'unità con un inizio e una fine propri (parola iniziale lunga,
  con *p*/*t*; parola finale in *m*), mentre l'ordine delle righe nella pagina è quasi libero. Coerente con e74, e78,
  e139, e273; qui la misura dice che i bordi pesano molto più dell'ordine interno.
- **Rilettura del lavoro precedente.** Il generatore vecchio (0,82 / 0,92) era già molto meglio di un rimescolamento
  delle parole vere (0,99): i suoi meccanismi di riga funzionavano. Il "modello del Voynich" (0,93 / 0,99) non aveva
  modello dei bordi di riga oltre la posizione: per questo stava al livello dei rimescolamenti.

## 3/10/2026 — e314, e315, e318: lo stato è di fascicolo e di bifoglio; A e B differiscono nel lessico, non sull'asse

Preregistrato (`preregistrazioni/e314.md`, con la correzione dell'e315 prima dell'esecuzione).

- **e314 (a), quanto pesa il bifoglio** (η² del punteggio dell'asse -edy/-aiin dentro lo strato):

  | raggruppamento | η² | nullo | z |
  |---|---|---|---|
  | bifoglio | 0,587 | 0,257 | 6,6 |
  | fascicolo | 0,451 | 0,118 | 8,5 |
  | mano | 0,138 | 0,033 | 5,2 |

  **Esito preregistrato: stato di bifoglio; spiegano qualcosa anche la mano e il fascicolo.**
  - **Osservazione non preregistrata:** per il solo punteggio dell'asse, il bifoglio non aggiunge molto al fascicolo
    (0,587 − 0,451 = 0,136, contro 0,139 attesi solo perché i gruppi sono più piccoli). L'asse è uno stato **di
    fascicolo**. Con il profilo intero (e308) invece il bifoglio conta da solo (pagine dello stesso bifoglio 0,20,
    altre dello stesso fascicolo −0,03). Si legge così: il fascicolo dà la posizione sull'asse, il bifoglio dà il resto
    del profilo.
- **e314 (b), che cosa porta il bifoglio:** segni *e* (η² 0,68, z 9,3), *i*, iniziale *y*, *a*, iniziale *d*, iniziale
  *ch*, *n*, finale *n*, *m*, iniziale *o*, finale *m*, *ch*, *d*, finale *y*, *s*.
- **e314 (c), un ordine dei bifogli** (erbario, 32 bifogli): l'ordine spettrale non segue il libro (|ρ| 0,31, z 1,6) e
  la mano non lo segue (cambi 11 contro 13 attesi, z −1,3). **La mano segue lo stato: in nessuna sezione.** L'ordine
  trovato è nel file dei risultati, come descrizione.
- **e315, lingue A e B nell'erbario** (84 pagine A, 32 B; validazione per bifoglio):

  | caratteristiche | AUC |
  |---|---|
  | (i) solo il punteggio dell'asse | **0,331** |
  | (ii) tutte | 1,000 |
  | (iii) tutte tranne l'asse e le parole in -*y*/-*n* | **0,997** (nullo 0,50, z alto) |
  | (iv) solo parole non in -*y*/-*n* | 0,966 |

  - Le differenze più forti (d di Cohen, B − A): parola *chedy* +2,8; iniziale *a* +2,4; segno *o* −2,0; *okedy*
    +1,8; *ar* +1,7; *shedy* +1,7; *chckhy* +1,5; *chdy* +1,5; *qokar* +1,5; segni *d* +1,4 e *k* +1,4; iniziale
    gallows composto −1,4; *okeedy* +1,4.
  - **Esito preregistrato: A e B differiscono oltre l'asse.**
  - **Correzione della mia lettura dell'e307.** Avevo scritto che l'asse -edy/-aiin "è lo stesso che separa A e B".
    Nell'erbario il punteggio dell'asse da solo **non** separa A e B. A e B differiscono per un lessico preciso:
    - B: *chedy*, *shedy*, *okedy*, *qokar*, *ar*, parole in *a*-;
    - A: più *o*, più gallows composti all'inizio.

    L'asse dell'e307 è un'altra dimensione, che varia dentro ogni lingua per fascicolo e bifoglio.
- **e318 (a), le 9 pagine candidate dell'e312:** con almeno un'irregolarità fisica il 22%, contro il 51% delle altre
  pagine (p 0,98). **Esito: no.** Non stanno su fogli irregolari.
- **e318 (b), fogli con recto e verso diversi:** 77 fogli; solo 3 hanno un cambio di mano, lingua o sezione fra le facce
  (differenza +0,03, z 0,2). **Esito: no** (poca potenza).
  - Fogli con le facce più diverse: f88r/v (−0,40), f52r/v (−0,21), f2r/v (−0,09), f83r/v, f82r/v.
  - Sono quasi le stesse "candidate" dell'e312: quelle pagine non sembrano fuori posto, sono **fogli le cui due facce
    sono diverse**, forse scritte in momenti diversi.

## 3/10/2026 — e316, e317: il paragrafo comincia con *p*, il gallows è meno legato alla parola del solito; l'arco del paragrafo è debole

Preregistrato (`preregistrazioni/e316.md`).

- **e316, gallows d'inizio paragrafo** (617 paragrafi che iniziano con un gallows):
  - quali: ***p* 331**, *t* 171, *k* 78, *f* 32, *cph* 4, *cth* 1. Nel resto del testo il gallows più frequente è *k*;
    all'inizio del paragrafo è *p* (54%). Lingua B *p* 256 su 413; lingua A *p* 75 su 194.
  - **(a)** informazione mutua fra il gallows e il segno che segue: prime parole 0,108 (z 8,5); parole in mezzo con
    gallows iniziale 0,321 (z 82,6). **Esito preregistrato: il gallows segue la parola.** Ma il legame è **tre volte
    più debole** che nelle parole normali: all'inizio del paragrafo il gallows è in buona parte scelto per la posizione
    (soprattutto *p*), non per la parola.
  - **(b)** stesso gallows fra paragrafi della stessa pagina 0,456 (z 0,9), dello stesso bifoglio 0,449 (z 2,5).
    **Esito: né per pagina né per bifoglio.**
  - **(c)** *p*/*f* nel primo paragrafo della pagina rispetto agli altri −0,05 (z 1,1). **Esito: no.**
- **e317, arco del paragrafo** (355 paragrafi con almeno 5 righe, 2.181 righe interne):
  - pendenza dalla seconda alla penultima riga: numero di parole −0,089 (z −8,2), finale *y* −0,064 (z −3,8); le altre
    sotto 3. **Esito preregistrato: debole.**
  - La seconda riga ha più parole (+0,82, z 5,6) e meno finali in *n* (z −3,0). La penultima ha meno parole in *qo*-
    (z −4,7) e meno parole (z −5,8).
  - **Lettura:** il registro dell'ultima riga (meno *qo*-, e313) comincia già nella penultima. Le righe si accorciano
    verso la fine del paragrafo; può dipendere anche dall'impaginazione intorno ai disegni.

## 3/10/2026 — e319, e323: nessun ordine di annidamento; nei fogli con le facce diverse una faccia sola esce dal bifoglio (incerto)

Preregistrato (`preregistrazioni/e319.md`).

- **e319** (9 fascicoli con almeno 3 bifogli profilati, 39 bifogli):
  - (a) profondità contro punteggio dell'asse: Spearman −0,155, z −0,9;
  - (b) bifogli a profondità consecutive contro le altre coppie: +0,199, z 1,9.
  - **Esito preregistrato: nessun ordine di annidamento.** Lo stato non cambia in modo ordinato dal bifoglio esterno a
    quello interno. Il "+0,199" dei bifogli vicini è appena sotto la soglia: da non dimenticare se un esperimento
    futuro avrà più potenza.
- **e323** (77 fogli): correlazione recto/verso contro asimmetria rispetto al foglio coniugato, Spearman −0,242, z −2,0.
  **Esito preregistrato: incerto.**
  - Nei cinque fogli con le facce più diverse, in quattro una faccia somiglia al foglio coniugato e l'altra no:

    | foglio | recto col coniugato | verso col coniugato | differenze più grandi |
    |---|---|---|---|
    | f2 | −0,05 | 0,18 | il recto ha molto meno *ch*- iniziale e *chor*, più *y*- |
    | f52 | 0,28 | −0,15 | il verso ha più gallows composti iniziali, meno -*m* |
    | f83 | 0,49 | 0,02 | il verso ha molto più *qokal* |
    | f88 | −0,11 | 0,17 | il recto ha più *cheol* e -*l*, parole più corte |
    | f82 | 0,41 | 0,26 | entrambe vicine al coniugato |

  - È coerente con facce scritte in un altro momento rispetto al resto del bifoglio, ma la prova su tutti i fogli non
    supera la soglia.

## 3/10/2026 — e320, e321, e322: la prima parola non annuncia il paragrafo; A e B hanno parole tipiche lontane fra loro, con una zona di passaggio; le righe si accorciano scendendo nella pagina

Preregistrato (`preregistrazioni/e320.md`).

- **e320** (702 paragrafi con almeno 15 parole):

  | voci | nel proprio paragrafo | in un altro della sezione | R |
  |---|---|---|---|
  | nucleo della prima parola (senza gallows) | 0,111 | 0,082 | 1,36 |
  | altre parole della prima riga (controllo) | 0,161 | 0,120 | 1,35 |

  - Differenza dei R +0,01, z 0,1. **Esito preregistrato: no.** La prima parola, tolto il gallows, non ricompare nel
    paragrafo più di qualsiasi altra parola della prima riga: non fa da "titolo".
  - **Errore mio nella misura "a una modifica" dei nuclei** (0,919 nel proprio paragrafo). Il nucleo dista una sola
    modifica dalla prima parola stessa, che sta nel paragrafo, quindi si ritrova sempre. Quella misura non vale; la
    decisione preregistrata usa la misura esatta, che è pulita.
- **e321** (erbario):
  - parole tipiche di B: *chedy*, *qokedy*, *shedy*, *okedy*, *otedy*, *qokchdy*, *kedy*, *ytedy*, *qokeedy*, *qotedy*,
    *air*, *qokar*, *otain*, *ain*…;
  - parole tipiche di A: *cthol*, *cthor*, *sho*, *otchol*, *dchy*, *dchor*, *kchol*, *kchor*, *qo*, *ctho*, *cho*,
    *shodaiin*, *dchol*, *sheor*…
  - **(a)** distanza media di ogni parola-B dalla parola-A più vicina: 2,17 segni, contro 1,53 se al posto delle
    parole-A si mettono parole qualsiasi di A (z **+8,2**). **Esito preregistrato: incerto**, perché il criterio
    prevedeva solo il caso opposto. Le parole tipiche di B sono **più lontane** dalle parole tipiche di A di quanto lo
    sia una parola qualsiasi: non sono varianti, sono due famiglie con terminazioni diverse (A: -*ol*, -*or*,
    gallows composti; B: -*edy*, -*dy*, -*ar*, -*ain*).
  - **(b)** indice-A di 181 pagine (parole scelte su metà dei bifogli, applicate all'altra metà): per decimi da tutto B
    a tutto A [36, 27, 14, 11, 10, 16, 11, 35, 17, 4]; pagine fra 0,25 e 0,75: **39%**. **Esito preregistrato:
    passaggio graduale.**
    - Cautela: l'indice di una pagina A pura non arriva a 1, perché alcune parole-B brevi (*ain*, *ar*) compaiono anche
      in A; la soglia 0,75 conta come "miste" molte pagine A normali (0,70–0,75).
    - Restano però pagine davvero intermedie, concentrate in alcuni fascicoli: C (f17–f24, 0,47–0,60), F (f43–f48: A a
      0,48–0,75 e B a 0,32–0,42) e G (f51–f55: 0,27–0,64). Sembra una **zona di passaggio nei fascicoli C, F, G**.
- **e322**, pendenza del numero di parole delle righe interne lungo il paragrafo:

  | sezione | pendenza (z) |
  |---|---|
  | erbario H | −0,146 (−8,6) |
  | T | −0,204 (−3,7) |
  | C | −0,195 (−2,9) |
  | stelle S | −0,081 (−1,9); in segni −0,095 (−3,1) |
  | B | −0,02 |
  | P | +0,01 |

  - **Esito preregistrato: effetto dell'impaginazione** (forte nell'erbario, non sotto −2 nelle stelle, misurata in
    parole).
  - Cautela: misurata in segni la pendenza nelle stelle è −3,1. Rispetto alla posizione nella pagina le righe si
    accorciano scendendo in **tutte** le sezioni (B −0,33, z −9,8; H −0,24, z −12,3; S −0,10, z −3,6). Si legge come
    un effetto dell'impaginazione (disegni in basso, pagine che si stringono), più forte dove ci sono i disegni grandi,
    con forse una piccola abitudine dello scriba dappertutto.

## 3/10/2026 — e324, e325, e326: nelle pagine di passaggio A e B si mescolano nella riga (incerto); Currier confermato; metà alta e metà bassa della pagina differiscono

Preregistrato (`preregistrazioni/e324.md`; la soglia delle pagine miste, 0,30–0,65, scelta dopo aver visto
l'istogramma dell'e321, come dichiarato).

- **e324, varianza fra le righe dell'indice-A:**

  | pagine | numero | V | nullo | z |
  |---|---|---|---|---|
  | miste (indice 0,30–0,65) | 32 | 0,0812 | 0,0692 | 2,2 |
  | pure | 44 | 0,0412 | 0,0399 | 0,5 |
  | controllo positivo, righe alternate | 20 | 0,1532 | 0,0590 | 20,3 |

  **Esito preregistrato: incerto** (fra 2 e 3). Nelle pagine di passaggio le righe sono appena più omogenee del caso;
  il controllo positivo mostra che un'alternanza vera di righe A e righe B si vedrebbe benissimo. Quindi le parole di A
  e di B si mescolano soprattutto **dentro le stesse righe**: un passaggio graduale, non due modi di scrivere alternati
  a tratti.
- **e325, riclassificare le pagine** (classificatore sul lessico addestrato sull'erbario):
  - accordo con Currier fra le previsioni sicure: erbario 107 su 107, B 17/17, P 14/14, T 6/6, C 2/2, S 18/19.
    **Esito preregistrato: etichette confermate.**
  - Unico disaccordo: **f58v** (sezione S, etichettata A, P(B) 0,81). Con la cautela del lessico di sezione: la
    sezione S è quasi tutta B.
  - Pagine senza etichetta: f67r2 P(B) 0,28 (più A); f70r2 P(B) 0,20 (A).
- **e326, metà alta contro metà bassa della pagina** (84 pagine con almeno 16 righe):
  - differenza del punteggio dell'asse 2,85 contro 1,79 del nullo, **z 7,3**;
  - distanza fra le distribuzioni dei segni 0,0302 contro 0,0209, **z 10,3**.
  - **Esito preregistrato: lo stato cambia dentro la pagina.**
  - Pagine con la differenza maggiore: f87v, f35v, f39r, f81v, f76v, f40v, f107v, f106r, f82v, f86v3.
  - **Cautela, scritta dopo i risultati:** la metà alta contiene più prime righe di paragrafo, che hanno un registro
    loro (e302: più -*y*, meno -*n*, più *p*/*f*); e le righe si accorciano scendendo (e322). Parte della differenza può
    venire da qui e non da un cambio di "stato". Va verificato togliendo prime e ultime righe dei paragrafi (e327).

## 3/10/2026 — e327: lo stato cambia davvero dentro la pagina, da un paragrafo all'altro

Preregistrato (`preregistrazioni/e327.md`), controllo dell'e326.

| versione | coppie | D1 (asse) | nullo | z | D2 (segni) | nullo | z |
|---|---|---|---|---|---|---|---|
| 1. solo righe interne | 80 | 2,89 | 2,18 | 3,9 | 0,0354 | 0,0254 | 8,7 |
| 2. nullo a pari tipo di riga | 84 | 2,85 | 1,79 | 7,1 | 0,0302 | 0,0206 | 11,3 |
| 3. primo contro ultimo paragrafo | 57 | 5,02 | 3,25 | 5,3 | 0,0781 | 0,0489 | 11,2 |

- **Esito preregistrato: lo stato cambia davvero dentro la pagina; cambio fra paragrafi.** La differenza fra metà alta
  e metà bassa resta togliendo le prime e ultime righe dei paragrafi, e resta con un nullo che conserva il tipo di
  riga. Il primo e l'ultimo paragrafo della stessa pagina differiscono più di due gruppi di righe presi a caso dagli
  stessi due paragrafi.
- **Lettura, con una cautela:** lo "stato" ha almeno tre livelli: fascicolo (posizione sull'asse, e314), bifoglio
  (profilo, e308), paragrafo (e327). Due paragrafi possono differire anche perché parlano di cose diverse
  (argomento): questa prova non separa "stato dello scriba" da "argomento del paragrafo".

## 3/10/2026 — e328, e329, e330: la variazione sta a tutti i livelli, soprattutto nel fascicolo; i paragrafi cambiano sia argomento sia abitudine; continuità girando il foglio incerta

Preregistrato (`preregistrazioni/e328.md`).

- **e328** (2.482 righe interne): quota della varianza fra le righe spiegata da ogni livello, oltre il caso (eccesso;
  tutti i livelli con z > 3 salvo dove detto):

  | variabile | fascicolo | bifoglio | pagina | paragrafo | resto (riga) |
  |---|---|---|---|---|---|
  | finale -*y* | +0,155 | +0,077 | +0,049 | +0,056 | 0,51 |
  | finale -*n* | +0,070 | +0,068 | +0,045 | +0,051 | 0,59 |
  | segno *e* | **+0,266** | +0,107 | +0,074 | +0,054 | 0,37 |
  | iniziale *qo*- | +0,181 | +0,033 | +0,043 | +0,041 | 0,55 |
  | lunghezza media | +0,138 | +0,044 | +0,041 | +0,019 (z 2,6) | 0,59 |

  **Esito: il livello con l'eccesso maggiore è sempre il fascicolo**, che qui comprende anche sezione e lingua; poi
  bifoglio, pagina e paragrafo aggiungono ciascuno qualche punto percentuale. Metà circa della variazione resta fra una
  riga e l'altra.
- **e329** (82 coppie primo/ultimo paragrafo della stessa pagina):
  - lessico normalizzato (tolte le 5 scelte di grafia): JSD 0,707 contro 0,673, **z 6,7**;
  - grafia (le 5 scelte): 5,11 contro 4,04, **z 6,8**.
  - **Esito preregistrato: argomento e abitudine.** Due paragrafi della stessa pagina differiscono sia per le parole
    (forme normalizzate) sia per come si scelgono le varianti di grafia.
- **e330:**
  - fogli, ultimo paragrafo del recto e primo del verso più vicini dei due lontani: asse +1,27 (z 2,5), segni +0,016
    (z 2,8). **Esito: incerto.**
  - aperture (verso e recto seguente): z 0,9 e 0,0. **Esito: no.**
  - **Lettura:** c'è un indizio di scrittura continua girando il foglio (mai fra fogli diversi), ma con 59 fogli non
    supera la soglia.

## 3/10/2026 — vz: e401, la disposizione: i posti della riga spiegano quasi tutto il salto; i legami fra vicine, così come sono, esagerano

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e401.md`): per ogni pagina il sacco delle parole vere e
l'impaginazione vera; un modello decide i posti. Semi 1–4. Risultati in `risultati/e401_disposizione.md`.
Riferimenti dall'e400: parole a caso nella pagina 0,998; solo righe rimescolate 0,595.

| strato | AUC e231 | AUC e266 | prevista (e266) | G4 | G6 | G7 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|
| D1, solo "prima riga di paragrafo o no" | 0,985 | 0,991 | 0,985–0,995 | 0,99 | 0,71 | 0,93 | 0,60 | 0,65 |
| D2, otto tipi di posto | 0,771 | **0,855** | 0,70–0,85 | 0,79 | 0,68 | 0,55 | 0,60 | 0,67 |
| D3, D2 + legami fra vicine | 0,729 | 0,847 | 0,62–0,75 | 0,70 | 0,73 | 0,58 | 0,64 | 0,64 |

- **D1 come previsto:** basta sapere quali parole stanno bene in una prima riga (tratti della parola, non la sua
  identità) per riportare G8 da 0,96 a 0,60 (*p* nelle prime righe meno le altre 0,030; Voynich 0,033).
- **D2, il passo grande:** con gli otto tipi di posto i bordi della riga tornano quelli del Voynich: inizio riga
  con *p* 7,4% (Voynich 7,7%), con *t* 10,1% (10,5%), con *ch* 4,2% (3,6%), fine in *m* 13,8% (13,9%), prima parola
  4,78 segni (4,82). G7 scende da 0,93 a 0,55; l'AUC da 0,99 a 0,855 (e231: 0,771). **I bordi della riga si
  spiegano con i tratti della parola e il tipo di posto**, senza altro.
- **D3 non è la previsione** (0,847 contro 0,62–0,75; guadagno su D2 sotto la soglia di 0,03 per l'e266). Il
  pannello dice perché: i legami **esagerano**. Unioni attestate 11,8% (Voynich 9,2%; senza legami 5,3%), coppie
  viste altrove 26,9% (22,1%; 18,3%), coppie identiche 2,1% (0,97%; 0,88%), somiglianza fra vicine 0,232 (0,218;
  0,204). Il giudice usa le stesse caratteristiche di prima, con il segno rovesciato. I tre termini (bordi, unione,
  coppia esatta) dicono in parte la stessa cosa e sommati contano doppio. Il verso è giusto, la dose no.
- **Resta fuori da tutti gli strati** la differenza fra le due metà della pagina (JSD 0,050 nel Voynich, 0,035–0,038
  qui): è l'ordine delle righe (O1 dell'e400), che questo modello non tocca.
- **Esito secondo la preregistrazione:** D3 > 0,70 e uno strato non ha dato il guadagno previsto: ci si ferma a
  capire. Capito dal pannello (dose dei legami); secondo tentativo e401b: i pesi dei termini di legame, più un termine
  per le coppie identiche, regolati **sul pannello** (non sui giudici) finché unioni, coppie viste altrove, coppie
  identiche e somiglianza fra vicine tornano quelle del Voynich.
- **Nota di esecuzione.** Il primo lancio (20:08) non è finito: dieci processi addestravano ciascuno la regressione
  su una matrice densa e si bloccavano a vicenda; interrotto alle 21:30 senza risultati. Corretto con una matrice
  sparsa (stesso modello) e rilanciato: 7 minuti.
- **Lettura per la ricerca sul Voynich.** Dove sta una parola nella riga si prevede bene dalla sua forma (primo e
  ultimo segno, lunghezza, *p*/*f*): l'inizio e la fine della riga hanno una "grammatica" di forme, non di parole.

## 3/10/2026 — vz: e401b, la disposizione con i legami alla dose giusta: giudici a 0,53 e 0,66 (con le parole vere di ogni pagina)

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e401b.md`): stesso modello dell'e401 più un termine per la
coppia identica; i quattro pesi dei legami regolati **sul pannello** (seme 11), non sui giudici. Risultati in
`risultati/e401b_disposizione_regolata.md`.

- **Regolazione: converge in 10 giri** (scarto massimo 1,6%). Pesi: bordi 0,71, unione 0,59, coppia esatta 0,49,
  coppia identica −0,55 (evitata). Valori: unioni attestate 9,2% (Voynich 9,2%), coppie viste altrove 22,2% (22,1%),
  coppie identiche 0,96% (0,97%), somiglianza fra vicine 0,217 (0,218). I pesi sono circa la metà di quelli dell'e401:
  era una questione di dose.
- **Strato D4, semi 1–4:**

  | | AUC e231 | AUC e266 (min–max) | prevista e266 | G4 | G5 | G6 | G7 | G8 | G9 |
  |---|---|---|---|---|---|---|---|---|---|
  | D4 | **0,533** | **0,659** (0,638–0,667) | 0,68–0,78 | 0,54 | 0,53 | 0,59 | 0,56 | 0,64 | 0,64 |
  | per confronto: D2 (e401) | 0,771 | 0,855 | | 0,79 | 0,51 | 0,68 | 0,55 | 0,60 | 0,67 |
  | per confronto: solo righe rimescolate (e400, O1) | 0,481 | 0,595 | | 0,50 | 0,48 | 0,50 | 0,50 | 0,50 | 0,62 |

- **Meglio della previsione.** Con le parole vere di ogni pagina, un modello di pochi pezzi (tratti della parola →
  tipo di posto; tre legami fra vicine più l'evitamento della parola identica) dispone le parole in modo che il
  giudice dell'e231 non le distingua quasi dal Voynich (0,53) e quello dell'e266 poco (0,66; il pavimento di questa
  strada è 0,60).
- **Che cosa resta, dalle caratteristiche pesanti:**
  - G9: le due metà della pagina sono più diverse nel Voynich (JSD 0,050 contro 0,038): è l'ordine delle righe, che il
    modello non tocca (lo stesso scarto di O1);
  - G8: nelle prime righe le parole escono un po' troppo lunghe (4,73 contro 4,63) e con un po' meno *p* (0,029
    contro 0,033);
  - G6: somiglianza a distanza 2 nella riga 0,207 contro 0,220: il legame del Voynich va un poco oltre la parola
    accanto;
  - inizio riga con *s* 10,5% contro 8,0%.
- **Che cosa NON è a posto: la pagella.** 14,8/18 e 5,2/8, cancello della riga perso in 4 semi su 4. Mancano in
  almeno un seme: concordanza delle desinenze, formule, gradiente, legame, prime righe come registro, ripetizione,
  scelte di riga, verticale. I giudici guardano medie di pagina; la pagella guarda anche strutture fini (scelte di
  grafia concordi nella riga, copia dalla riga sopra, sequenze ripetute) che questo modello non ha.
- **Limite dichiarato nella preregistrazione, da ricordare:** i quattro valori regolati sono anche caratteristiche dei
  giudici. Il risultato dice che queste statistiche **bastano** per quei giudici, non che il modello sia giusto per
  altre vie: la pagella lo conferma.
- **Esito secondo la preregistrazione:** D4 ≤ 0,78 con G4 e G6 ≤ 0,65: la disposizione dentro la riga è capita per
  quanto riguarda i giudici. Passi seguenti: l'ordine delle righe nella pagina (G9), le materie di pagella perse, poi
  il sacco di pagina (quali parole), che è la parte ancora tutta da fare.
- **Lettura per la ricerca sul Voynich.** L'ordine delle parole nella riga del Voynich, visto da questi giudici, è
  descritto da: una "grammatica" di forme per i posti della riga, un legame debole fra bordi di parole vicine, una
  tendenza a scrivere vicine due parole che unite ne danno una terza, e l'evitamento della parola identica accanto.

## 3/10/2026 — e331, e332, e333: girando il foglio ancora incerto; gli argomenti non sono locali; -ey cresce scendendo nella pagina

Preregistrato (`preregistrazioni/e331.md`).

- **e331** (lontana − vicina; z con inversione del segno):

  | prova | coppie | segni (z) | asse (z) | lessico (z) |
  |---|---|---|---|---|
  | fogli, blocchi di 4 righe | 82 | +0,015 (2,2) | +0,95 (1,7) | +0,032 (2,2) |
  | aperture, blocchi di 4 | 80 | −0,005 (−0,8) | +0,54 (0,7) | −0,008 (−0,6) |
  | fogli, blocchi di 8 | 30 | +0,011 (1,8) | +0,34 (0,4) | +0,023 (1,0) |
  | aperture, blocchi di 8 | 23 | +0,013 (1,4) | +1,52 (1,4) | +0,014 (0,7) |

  **Esito preregistrato: incerto.** Con l'e330 è la seconda volta che i fogli danno z intorno a 2 nella direzione della
  continuità, e le aperture intorno a 0. Le due prove usano quasi gli stessi fogli, quindi non si sommano. L'indizio
  resta, la prova no.
- **e332** (erbario in lingua A, 178 paragrafi, 182 forme normalizzate, LDA con 6 argomenti):
  - distanza media nel libro fra paragrafi con lo stesso argomento 47,4 pagine contro 47,8 del nullo, z −0,6;
  - ogni argomento è dominante in 6–8 fascicoli.
  - **Esito preregistrato: argomenti che tornano lontano.**
  - **Cautela scritta dopo il risultato:** la prova non controlla se questi "argomenti" siano reali o rumore. Con 178
    paragrafi e 182 forme l'LDA trova sempre 6 gruppi, e gruppi casuali sarebbero anch'essi sparsi nel libro. L'e329
    dice che i paragrafi differiscono davvero nel lessico; qui si vede che quelle differenze non si raccolgono in un
    periodo del libro. Per dire che ci sono argomenti ricorrenti serve un confronto con l'LDA su paragrafi rimescolati.
- **e333** (metà bassa − metà alta delle righe interne della pagina):

  | misura | pagine | differenza | z |
  |---|---|---|---|
  | **-*dy*/-*ey*** (quota di -*ey*) | 65 | **+0,090** | **3,2** |
  | -*l*/-*r* | 77 | −0,061 | −2,7 |
  | *k*/*t* | 80 | −0,046 | −2,3 |
  | *ch*/*sh* | 80 | +0,025 | 1,7 |
  | punteggio dell'asse | 80 | −0,62 | −1,5 |
  | *o*-/*qo*- | 68 | −0,004 | −0,1 |

  **Esito preregistrato: direzione costante per -*dy*/-*ey*.** Scendendo nella pagina la quota di -*ey* rispetto a
  -*dy* cresce in modo coerente da pagina a pagina. Le altre scelte tendono a cambiare anche loro (−*r* e *t* in calo)
  ma sotto la soglia. Se la pagina si scriveva dall'alto in basso, -*ey* aumenta con il tempo dentro la pagina.

## 3/10/2026 — e334, e335, e336: niente argomenti netti; -ey non è un orologio ma un effetto di posizione nella pagina

Preregistrato (`preregistrazioni/e334.md`).

- **e334** (erbario A, 178 paragrafi): concentrazione dell'argomento dominante 0,789 contro 0,822 su paragrafi
  rimescolati (z −2,3). **Esito preregistrato: rumore.**
  - I gruppi dell'e332 non sono argomenti reali: l'LDA sui paragrafi veri non trova gruppi più netti che su paragrafi
    fatti a caso con le stesse parole.
  - Le differenze di lessico fra paragrafi dell'e329 sono quindi una continuità locale (le righe dello stesso
    paragrafo condividono parole), non argomenti che tornano.
  - Correlazioni fra argomenti e quota di -*ey*: da −0,16 a +0,08.
- **e335, -*ey* come orologio:**
  - verso − recto dello stesso foglio +0,007 (78 fogli, z 0,2);
  - recto seguente − verso, aperture, −0,000 (z 0,0).
  - **Esito preregistrato: la crescita è solo di posizione nella pagina; per le aperture no.** Una pagina scritta dopo
    non ha più -*ey*: la crescita dell'e333 si ripete in ogni pagina, dall'alto in basso. Non misura il tempo.
- **e336** (quota di -*ey*):
  - dentro il paragrafo, seconda metà − prima: z 2,6;
  - fra paragrafi consecutivi: z 1,6.
  - **Esito preregistrato: incerto.** Per -*l*/-*r* e *k*/*t*: nulla (|z| < 2).
- **Lettura:** -*ey* cresce scendendo nella pagina ma non si accumula da una pagina all'altra: è legato alla posizione
  verticale, come l'accorciarsi delle righe (e322), forse all'impaginazione. La strada "orologio" per ricostruire
  l'ordine di scrittura si chiude qui.

## 3/10/2026 — vz: e402, il sacco di pagina è il muro: v5 0,79 e modello del Voynich 0,96 guardando solo quali parole stanno nella pagina

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e402.md`): corpo della v5 e modello del Voynich (seconda
forma tarata), semi 1–4; testo originale e testo con le parole di ogni pagina ridisposte dal modello dell'e401b; in
più l'AUC del **solo sacco** (giudice dell'e266 sulle caratteristiche che non dipendono dall'ordine: G1, G2, G3, JSD
pagina-manoscritto). Risultati in `risultati/e402_sacco_generatori.md`.

| testo | AUC e231 | AUC e266 | prevista (e266) | solo sacco | pagella | G3 | G8 | G9 |
|---|---|---|---|---|---|---|---|---|
| v5 originale | 0,812 | 0,918 | 0,90–0,94 | **0,794** | 16,5/18 | 0,83 | 0,87 | 0,60 |
| v5 ridisposta | 0,797 | **0,842** | 0,84–0,92 | 0,794 | 13,5/18 | 0,83 | 0,67 | 0,67 |
| modello originale | 0,932 | 0,989 | 0,97–1,00 | **0,959** | 7,5/18 | 0,89 | 0,77 | 0,93 |
| modello ridisposto | 0,894 | 0,968 | 0,90–0,97 | 0,959 | 9,0/18 | 0,89 | 0,73 | 0,92 |
| per confronto: sacco vero ridisposto (e401b) | 0,533 | 0,659 | | 0,500 | 14,8/18 | 0,50 | 0,64 | 0,64 |

- **Le previsioni tornano** (solo sacco della v5 0,794 contro 0,80–0,88 previsto; del modello 0,959, un filo sopra
  0,88–0,95).
- **Il muro è il sacco.** Con il sacco vero la disposizione dà 0,53 / 0,66; con il sacco della v5 0,80 / 0,84; con
  quello del modello 0,89 / 0,97. Il solo sacco della v5 vale 0,794: quasi tutto il suo 0,81 dell'e231.
- **Ridisporre la v5** abbassa il giudice forte di 0,076 (G8, prime righe: da 0,87 a 0,67) e quasi niente l'altro; ma
  costa pagella (16,5 → 13,5: la disposizione nuova non ha concordanza delle desinenze, formule, verticale, scelte
  di riga, che la v5 aveva).
- **Che cosa tradisce il sacco della v5** (caratteristiche pesanti): pagine troppo ripetitive (tipi su parole 0,681
  contro 0,756; uniche nella pagina 0,549 contro 0,636), lunghezze troppo disperse (1,664 contro 1,579) e parole in
  media troppo corte (4,16 contro 4,29), meno parole uniche nel libro (12,8% contro 14,6%).
- **Che cosa tradisce il sacco del modello:** pagine troppo "medie" (JSD pagina-manoscritto 0,013 contro 0,040: G9
  0,93), parole troppo lunghe (4,56) e disperse (1,71).
- **Esito secondo la preregistrazione:** la base migliore per il sacco è quella della v5 (0,794), ma è a 0,79 ≈ 0,80:
  "il sacco è il muro e si lavora lì". La disposizione dell'e401b migliora il giudice forte di almeno 0,03 su entrambi
  i generatori: resta come ultimo stadio, sapendo che per la pagella va completata.
- **Prossimo passo:** costruire il sacco un pezzo alla volta, come per la disposizione, misurando ogni pezzo con il
  "solo sacco" e il resto preso dal vero. Primo pezzo (e403): le **parole nuove** (il 14,6% delle parole di una pagina
  compare una volta sola in tutto il libro): si sostituiscono solo quelle con parole inventate da più generatori di
  forme, e si vede quale non si fa riconoscere.

## 3/10/2026 — vz: e403, le parole nuove: nessuno dei quattro modi di inventarle passa (0,77–0,96); le parole uniche del Voynich portano i segni rari

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e403.md`): nel Voynich vero si sostituisce solo ogni parola
unica nel libro (4.776, il 13,7% delle occorrenze) con una parola inventata; "solo sacco" = giudice dell'e266 su G1, G2,
G3, JSD pagina-manoscritto (pavimento 0,50). Semi 1–4. Risultati in `risultati/e403_parole_nuove.md`.

| generatore | solo sacco | previsto | G1 | G2 | G3 | JSD | lunghezza delle inventate (Voynich 5,94 ± 1,57) |
|---|---|---|---|---|---|---|---|
| variante-libro (operatore dell'e241 su un tipo del libro) | 0,795 | 0,60–0,72 | 0,74 | 0,71 | 0,50 | 0,65 | 5,78 ± 1,40 |
| variante-pagina (su un tipo della stessa pagina) | 0,781 | 0,56–0,68 | 0,73 | 0,71 | 0,64 | 0,51 | 5,61 ± 1,36 |
| trigrammi di segni imparati sulle parole uniche | 0,961 | 0,58–0,70 | 0,62 | 0,68 | 0,97 | 0,68 | 7,70 ± 2,90 |
| mista (72% variante-pagina, 14% unione, 14% trigrammi) | 0,774 | 0,55–0,65 | 0,68 | 0,67 | 0,73 | 0,52 | 6,32 ± 2,10 |

- **Esito preregistrato: tutti sopra 0,60.** Previsioni sbagliate di 0,1–0,3. **Da sole, le parole nuove fatte così
  costano quanto tutto il sacco della v5 (0,794):** una parte grande del "muro" dei generatori vecchi era qui.
- **Perché (caratteristiche pesanti e conteggi sul Voynich fatti dopo):**
  - le varianti hanno la lunghezza quasi giusta e, se partono dalla pagina, tengono il profilo della pagina (JSD
    0,51); ma **mancano i segni rari**: *c*, *h*, *x*, *f*, *g* pesano fra le prime caratteristiche;
  - i trigrammi hanno i segni più giusti (G1 0,62) ma lunghezze sbagliate (7,7 ± 2,9: nessun controllo della
    lunghezza), e non seguono la pagina (JSD 0,68).
- **Conteggio sul Voynich (proprietà del testo).** Le parole uniche contengono il 18,3% dei segni del libro, ma:
  il 100% delle *x*, l'81% delle *c* isolate, l'80% delle *b*, il 68% delle *g*, il 66% delle *h* isolate, il 64% delle
  *f*, il 61% dei *cfh*, il 42% delle *p*, il 37% dei *cph*, il 31% delle *s*, il 29% delle *m*; e solo il 10% delle
  *q*, l'11% delle *n*, il 14% delle *i*. Il 9,3% delle parole uniche ha almeno un segno raro (3,8% dei tipi non unici);
  il 17,8% ha *p* o *f* (10,6%). **Le parole uniche non sono "una parola frequente con un errore qualsiasi": sono il
  posto dove stanno i segni rari e i segni di posizione** (*p*/*f* delle prime righe, *m*/*g* di fine riga, *s*
  d'inizio riga). Va con il fatto che stanno ai bordi (47,7% delle prime parole di paragrafo, 21% delle ultime di
  riga, 8,8% in mezzo).
- **Secondo tentativo (e403b):** un modello della forma imparato sulle parole uniche (trigrammi), con la lunghezza
  controllata, distinto per tipo di posto nella riga e scelto in modo da seguire il profilo della pagina.

## 3/10/2026 — e337, e338, e339: la posizione nella riga governa le scelte di grafia; le previsioni dell'autocitazione reggono (con due cautele); le etichette dello zodiaco non sono giorni

Preregistrato (`preregistrazioni/e337.md`).

- **e337** (perdita di log-verosimiglianza togliendo il fattore, in millesimi di bit per posto; base: strato e
  fascicolo):

  | scelta | posti | posizione nella riga | tipo di riga | altezza nella pagina | paragrafo | faccia |
  |---|---|---|---|---|---|---|
  | *ch*/*sh* | 14.391 | **10,1** | 4,8 | 0,2 | 0,0 | 0,0 |
  | *k*/*t* | 17.986 | **4,0** | 0,4 | 1,2 | 0,1 | 0,0 |
  | -*l*/-*r* | 9.523 | **4,8** | 0,4 | 0,4 | 0,1 | 0,1 |
  | *o*-/*qo*- | 8.818 | **10,1** | 1,4 | 1,9 | 0,1 | 1,0 |
  | -*dy*/-*ey* | 9.968 | **18,1** | 5,0 | 4,5 | 0,1 | 0,2 |

  - Significativi dopo Bonferroni:
    - *ch*/*sh*: posizione, tipo di riga;
    - *k*/*t*: posizione, altezza;
    - -*l*/-*r*: posizione;
    - *o*-/*qo*-: posizione, altezza;
    - -*dy*/-*ey*: posizione, tipo di riga, altezza.
  - **Il paragrafo (primo o no) e la faccia del foglio non contano mai.**
  - **Esito:** il fattore più forte, per tutte e cinque le scelte, è la **posizione della parola nella riga**; poi il
    tipo di riga e l'altezza nella pagina.
- **e338, l'autocitazione di Timm e Schinner:**

  | testo | fonte nelle 2 righe sopra | nullo | E1 (z) | stessa colonna | nullo | E2 (z) |
  |---|---|---|---|---|---|---|
  | Voynich (167 pagine) | 0,433 | 0,395 | **+0,037 (16,6)** | 0,406 | 0,369 | **+0,037 (8,7)** |
  | Timm e Schinner, seme 1 | 0,569 | 0,546 | +0,023 (11,8) | 0,439 | 0,409 | +0,030 (8,2) |
  | Timm e Schinner, seme 19 | 0,534 | 0,511 | +0,023 (10,8) | 0,421 | 0,377 | +0,044 (10,8) |

  **Esito preregistrato: valido; autocitazione sostenuta per tutte e due le previsioni** (E1 del Voynich 1,62 volte
  quello del generatore, E2 0,99 volte).
  - **Correzione di una mia lettura.** Dal primo prototipo del modello del Voynich avevo scritto che "la riga sopra
    non aggiunge nulla, la verticalità è lessico di pagina, non copia". Era una conclusione debole: in quel prototipo
    la componente "riga sopra" competeva con il lessico della pagina vera, che vedeva anche le parole venute dopo. La
    misura diretta dice che le parole hanno una fonte nelle righe subito sopra, e nella stessa colonna, più del caso,
    almeno quanto nel generatore che si basa proprio su questo. Correzioni fatte nel dossier e nel passaggio di
    consegne del voynichizzatore.
  - **Due cautele, scritte dopo il risultato:**
    1. E1 confronta con le righe della pagina in ordine casuale: include anche il lessico del paragrafo, che le righe
       vicine condividono (e329). Il generatore di Timm e Schinner non ha paragrafi.
    2. E2 confronta con l'ordine casuale della riga sopra: include anche l'effetto di posizione (e337: la prima e
       l'ultima parola della riga hanno forme loro), che rende simili le parole nella stessa colonna anche senza
       copia.

    Per separare la copia da questi due effetti servono E1 dentro e fuori dal paragrafo ed E2 senza la prima e
    l'ultima parola (e340).
- **e339** (12 pagine dello zodiaco, 294 etichette):
  - stessa posizione in mesi diversi: +0,001, z 0,4. **Esito preregistrato: no.** Le etichette non sono una sequenza
    di giorni ripetuta mese per mese.
  - Etichette consecutive nella stessa pagina: z 1,1 (non più simili del caso).
  - Il 76% delle etichette dello zodiaco comincia con *o* (21% nel testo).

## 3/10/2026 — vz: e403b, parole nuove con la forma imparata sulle parole uniche: da 0,77 a 0,64 (pezzo provvisorio)

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e403b.md`): stessa prova dell'e403, con un modello a
trigrammi di segni imparato sulle parole uniche, più un pezzo alla volta. Risultati in
`risultati/e403b_parole_nuove_forma.md`.

| generatore | solo sacco | previsto | G1 | G2 | G3 | JSD | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|---|---|
| T-L, trigrammi con la lunghezza controllata | 0,690 | 0,68–0,80 | 0,58 | 0,58 | 0,57 | 0,64 | 0,753 | 0,843 |
| T-LP, anche per tipo di posto nella riga | 0,688 | 0,62–0,74 | 0,57 | 0,57 | 0,58 | 0,64 | 0,694 | 0,751 |
| T-LPS, anche scelte secondo il profilo della pagina | **0,644** | 0,55–0,68 | 0,59 | 0,59 | 0,56 | 0,52 | 0,690 | 0,730 |
| per confronto: il migliore dell'e403 (mista) | 0,774 | | 0,68 | 0,67 | 0,73 | 0,52 | 0,808 | 0,850 |

- **Previsioni rispettate.** Controllare la lunghezza porta da 0,961 (trigrammi dell'e403) a 0,690: la lunghezza delle
  inventate è ora 5,93 ± 1,56 (Voynich 5,94 ± 1,57).
- **Il tipo di posto non cambia il solo sacco** (0,688 contro 0,690: sotto la soglia di 0,03), come è giusto, perché il
  solo sacco non guarda i posti; ma abbassa molto i giudici interi (e231 da 0,753 a 0,694, e266 da 0,843 a 0,751): i
  segni di posizione (*p*/*f* nelle prime righe, *m* a fine riga, *s* a inizio) finiscono nei posti giusti. Si tiene
  per questo motivo, dichiarandolo.
- **Seguire il profilo della pagina** guadagna 0,044 (JSD da 0,64 a 0,52: 0,0409 contro 0,0402 del Voynich).
- **Che cosa resta** (0,64 contro il pavimento 0,50): le inventate somigliano a parole note meno delle vere (a una
  modifica da una nota 0,55 contro 0,715); alcune coppie di segni (*d*+*y* 0,0417 contro 0,0432; *l*+*o* 0,0045 contro
  0,0035); la dispersione delle lunghezze nella pagina (1,61 contro 1,58).
- **Esito secondo la preregistrazione:** migliore fra 0,62 e 0,70 → **pezzo provvisorio**. Le parole nuove costano
  0,64 di solo sacco da sole; il costo si rimisura nel sacco intero. Leva nota se servirà: un modello dei segni più
  stretto (quattro segni di contesto, o varianti di parole della pagina filtrate dal modello).
- **Anche con tutto il resto vero**, sostituire le sole parole uniche porta i giudici interi a 0,69 / 0,73: le parole
  nuove sono una parte del testo che i giudici guardano molto.

## 3/10/2026 — vz: e404, le parole note: il lessico di sezione dà la varietà giusta ma pagine troppo "medie"; primo generatore intero a pezzi a 0,716 / 0,857

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e404.md`): impaginazione vera; parole note pescate dal
lessico della sezione e lingua (altre pagine), con ripetizione θ regolata sul pannello; semi 1–4. Risultati in
`risultati/e404_parole_note.md`.

- **Regolazione:** θ = 765 (tipi su parole 0,750 contro 0,756): converge. Serve pochissima ripetizione: già senza, il
  lessico di sezione dà 0,785.

| strato | solo sacco | previsto | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|
| K1, lessico di sezione senza ripetizione (parole nuove vere) | 0,786 | 0,80–0,92 | 0,43 | 0,37 | 0,65 | 0,75 |
| K2, con ripetizione | 0,777 | 0,60–0,75 | 0,41 | 0,36 | 0,71 | 0,74 |
| K4, K2 + parole nuove inventate (T-LPS) | 0,756 | 0,68–0,80 | 0,58 | 0,49 | 0,70 | 0,75 |

- **K2 non è la previsione** (0,777 contro 0,60–0,75). La caratteristica che pesa, di gran lunga, è una sola: la
  **JSD pagina-manoscritto**, 0,023 contro 0,040 del Voynich (coefficiente −5,7; la seconda vale 2). Le pagine fatte
  col lessico di sezione hanno frequenze dei segni giuste in media (G1 e G2 sotto 0,5) e la varietà giusta, ma si
  scostano dal libro la metà di quanto fanno le pagine vere: **manca il carattere proprio della pagina**. La
  ripetizione di parole intere non lo dà (θ è quasi spenta).
- **Lettura per la ricerca sul Voynich.** Una pagina del Voynich non è più ripetitiva di un campione del lessico della
  sua sezione e lingua (0,756 contro 0,785 di tipi su parole), ma il suo profilo dei segni è due volte più lontano dal
  libro. L'identità della pagina sta nei **segni** (abitudini di grafia della pagina, e145, e261), non nella
  ripetizione di parole.
- **K5, il primo generatore intero costruito a pezzi** (parole note dal lessico di sezione con ripetizione, parole
  nuove inventate, disposizione dell'e401b; di vero restano l'impaginazione e quali posti hanno una parola nuova; il
  profilo usato per le parole nuove è ancora quello della pagina vera):

  | | AUC e231 | AUC e266 | pagella | estese | G3 | G4 | G6 | G8 | G9 |
  |---|---|---|---|---|---|---|---|---|---|
  | K5 | **0,716** | **0,857** | 11,5/18 | 4,8/8 | 0,70 | 0,76 | 0,73 | 0,66 | 0,75 |
  | previsto | 0,72–0,84 | 0,78–0,90 | 11–14 | | | | | | |
  | v5, stessi semi (e402) | 0,812 | 0,918 | 16,5/18 | 3,0/8 | 0,83 | 0,61 | 0,71 | 0,87 | 0,60 |
  | sacco vero ridisposto (e401b) | 0,533 | 0,659 | 14,8/18 | 5,2/8 | 0,50 | 0,54 | 0,59 | 0,64 | 0,64 |

  Meglio della v5 su entrambi i giudici (−0,10 e −0,06), **peggio sulla pagella** (11,5 contro 16,5; cancello della
  riga perso; mancano concordanza delle desinenze, formule, gradiente, legame, omogeneità, profilo pagina,
  ripetizione, scelte di riga, verticale, parole rare per pagina, prime righe come registro). Semi di ricerca, non
  ancora il banco.
  - Con questo sacco la disposizione dà meno unioni attestate (6,2% contro 9,2%) e meno somiglianza a distanza 2
    (0,19 contro 0,22): i pesi dei legami erano regolati sul sacco vero; con un sacco diverso vanno regolati di
    nuovo, a sacco finito.
- **Esito secondo la preregistrazione:** K2 > 0,65 → secondo tentativo (e404b) con il solo pezzo che manca: il
  carattere della pagina nei segni.

## 3/10/2026 — e340: la ripresa dalle righe subito sopra regge anche dentro il paragrafo; la "stessa colonna" no

Preregistrato (`preregistrazioni/e340.md`), controllo dell'e338.

| testo | fonte nelle 2 righe sopra | nullo (righe rimescolate dentro il paragrafo) | E1p (z) | stessa colonna, parole in mezzo | nullo | E2m (z) |
|---|---|---|---|---|---|---|
| Voynich (167 pagine) | 0,480 | 0,428 | **+0,051 (17,4)** | 0,435 | 0,420 | +0,015 (2,7) |
| Timm e Schinner, seme 1 | 0,569 | 0,545 | +0,024 (11,0) | 0,475 | 0,456 | +0,019 (4,3) |
| Timm e Schinner, seme 19 | 0,534 | 0,510 | +0,023 (10,9) | 0,464 | 0,428 | +0,036 (7,6) |

- **Esito preregistrato: valido; parziale (regge E1p).**
- **Lettura:**
  - Anche a parità di lessico del paragrafo, una parola trova una parola uguale o a una modifica nelle 2 righe subito
    sopra più che in righe dello stesso paragrafo prese a caso. L'effetto è più del doppio di quello del generatore di
    Timm e Schinner. La **ripresa dalle righe appena scritte** è una proprietà vera del Voynich: è la parte centrale
    della loro ipotesi.
  - La "stessa colonna" invece, tolte la prima e l'ultima parola della riga, quasi sparisce (z 2,7). L'allineamento
    verticale dell'e338 veniva soprattutto dai bordi della riga, che hanno forme loro (e337). Lo scriba riprende parole
    dalle righe sopra, ma non dalla stessa posizione.

## 3/10/2026 — vz: e404b, il carattere della pagina nei segni: le parole note non si distinguono più (solo sacco 0,48); generatore a pezzi a 0,711 / 0,813, pagella 14,5

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e404b.md`, con un'integrazione prima dell'esecuzione: θ e κ
regolati insieme). Ogni pagina riceve gli scostamenti dei segni di **un'altra** pagina vera, a caso, della stessa
sezione e lingua; le parole note si pescano dal lessico di sezione con peso exp(κ · scostamenti). Semi 1–4. Risultati
in `risultati/e404b_carattere_pagina.md`.

- **Regolazione sul pannello:** κ = 0,708, θ = 2280 (ripetizione quasi spenta); JSD pagina-manoscritto 0,0406 (Voynich
  0,0402), tipi su parole 0,747 (0,756): converge (scarto massimo 1,2%).

| strato | solo sacco | previsto | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|
| C2, parole note con il carattere, parole nuove vere | **0,482** | 0,58–0,70 | 0,47 | 0,41 | 0,64 | 0,50 |
| C4, anche le parole nuove inventate | 0,645 | 0,64–0,76 | 0,63 | 0,57 | 0,63 | 0,61 |
| per confronto: K2 e K4 dell'e404 (senza carattere) | 0,777 e 0,756 | | | | | |

- **C2 meglio della previsione: 0,48, cioè al pavimento.** Con il carattere di pagina le parole note di una pagina
  generata non si distinguono da quelle di una pagina vera, per quanto vedono questi giudici. Tre ingredienti: il
  lessico della sezione e lingua, un carattere nei segni preso da un'altra pagina, quasi nessuna ripetizione di parole.
- **Lettura per la ricerca sul Voynich.** L'identità di una pagina, vista da questi giudici, è: sezione e lingua, più
  un profilo dei segni proprio (quanto *sh* contro *ch*, quanto *k* contro *t*, e così via), che un'altra pagina della
  stessa sezione può prestare senza che si veda. Non serve nessuna parola "propria" della pagina, a parte le parole
  nuove. È coerente con le abitudini di grafia di pagina (e145, e261) e con l'e296 (nessuna parola rara è "della
  pagina").
- **Il costo che resta nel sacco sono le parole nuove:** C4 − C2 = 0,16 (soglia preregistrata 0,08). In C4 la JSD
  sale troppo (0,050 contro 0,040) e mancano i segni rari (*f* 0,0018 contro 0,0026, *b*). **Capito il motivo:** la
  scelta delle parole nuove "secondo il profilo della pagina" penalizza ogni segno che la pagina non ha fra le parole
  note (peso lisciato −2,7 per segno assente), cioè proprio i segni rari che le parole nuove devono portare, e spinge
  troppo sui segni comuni. È un difetto di costruzione mio, non una proprietà del testo.
- **C5, generatore intero a pezzi** (di vero: impaginazione e posti delle parole nuove):

  | | AUC e231 | AUC e266 | pagella | estese | G3 | G4 | G6 | G8 | G9 |
  |---|---|---|---|---|---|---|---|---|---|
  | C5 | **0,711** | **0,813** | **14,5/18** | 4,0/8 | 0,63 | 0,68 | 0,59 | 0,68 | 0,76 |
  | previsto | 0,62–0,74 | 0,74–0,85 | | | | | | | |
  | K5 (e404) | 0,716 | 0,857 | 11,5/18 | 4,8/8 | 0,70 | 0,76 | 0,73 | 0,66 | 0,75 |
  | v5 | 0,812 | 0,918 | 16,5/18 | 3,0/8 | 0,83 | 0,61 | 0,71 | 0,87 | 0,60 |

  Il carattere recupera tre materie di pagella (da 11,5 a 14,5) e abbassa il giudice forte di 0,044. Restano, dalle
  caratteristiche pesanti: unioni attestate 6,8% contro 9,2% (pesi della disposizione regolati sul sacco vero), JSD
  pagina-manoscritto troppo alta per le parole nuove, differenza fra le due metà della pagina (0,031 contro 0,050:
  ordine delle righe), coppie viste altrove 24% contro 22%.
- **Esito secondo la preregistrazione:** C2 ≤ 0,65 → il carattere era il pezzo mancante delle parole note; C4 − C2 >
  0,08 → passo seguente: le parole nuove (modello dei segni più stretto e correzione della scelta per profilo).

## 3/10/2026 (notte) — e341, e344, e345: girando il foglio no; il paragrafo riparte da capo; nessuna colonna dei bordi

Preregistrato (`preregistrazioni/e341.md`). Lavoro autonomo notturno chiesto da Davide.

- **e341** (ripresa fra blocchi di 3 righe: fine recto + inizio verso contro inizio recto + fine verso):
  - fogli +0,036 su 91, z 1,8;
  - aperture −0,015, z −0,7.
  - **Esito preregistrato: no.** È la terza misura (e330, e331, e341) che sui fogli dà z fra 1,8 e 2,8 nella stessa
    direzione, ma nessuna supera la soglia, e le tre usano gli stessi fogli. La domanda "lo scriba girava il foglio e
    continuava?" si chiude senza una risposta positiva.
- **e344** (fonte nelle 2 righe sopra, contro 2 righe a caso della pagina):

  | gruppo | parole | quota | nullo | z |
  |---|---|---|---|---|
  | prime parole dei paragrafi, parola intera | 533 | 0,141 | 0,131 | 0,9 |
  | prime parole dei paragrafi, nucleo senza gallows | 533 | 0,287 | 0,286 | 0,1 |
  | prime parole delle altre righe, parola intera | 3.183 | 0,359 | 0,327 | 4,6 |
  | prime parole delle altre righe, nucleo | 3.183 | 0,378 | 0,347 | 5,0 |

  **Esito preregistrato: parole nuove anche rispetto alle righe sopra.** La prima parola di un paragrafo non riprende
  le righe appena scritte (nemmeno senza il gallows), mentre la prima parola di ogni altra riga sì. Con e310 ed e320:
  l'inizio del paragrafo è un vero "ripartire da capo".
- **e345** (stessa posizione nella riga sopra, contro un'altra riga del paragrafo):

  | parola | quota | nullo | z |
  |---|---|---|---|
  | prima parola | 0,039 | 0,046 | −2,2 |
  | ultima parola | 0,048 | 0,039 | 2,5 |
  | parole in mezzo, stessa posizione | 0,062 | 0,058 | 2,2 |

  **Esito preregistrato: nessuna colonna dei bordi.** Con l'e340: la ripresa dalle righe sopra non segue la colonna,
  né al centro né ai bordi. L'E2 dell'e338 (z 8,7) era un effetto più debole e diffuso (posizioni ±1 vicino ai bordi),
  non una copia in colonna.

## 3/10/2026 (notte) — e342, e343: le modifiche della ripresa sono quelle del lessico; le catene di ripresa sono lunghe e si fermano al paragrafo

Preregistrato (`preregistrazioni/e342.md`).

- **e342** (10.488 coppie parola/fonte vicina, 23.712 coppie di riferimento a 6+ righe di distanza):
  - nessuna modifica è **preferita** (rapporto > 1,5 e z > 3) né **evitata** (< 0,67 e z < −3) nella ripresa;
  - i rapporti vanno da 0,78 a 1,41. Tendenze sotto soglia:
    - *sh*→*ch* 1,41 (z 5,7);
    - −*d* interno 1,27 (z 3,8);
    - −*d* iniziale 1,24 (z 3,2);
    - −*y* finale 1,32 (z 2,9);
    - *k*→*t* 0,78 (z −3,6).
  - Lo stesso per il generatore di Timm e Schinner: nessuna preferita.
  - **Esito preregistrato: nessuna modifica preferita o evitata.**
  - **Lettura:** quando lo scriba riprende una parola dalle righe sopra la cambia con le **stesse** modifiche che
    separano le parole del lessico in generale. È coerente con un lessico prodotto in buona parte dalla ripresa stessa.
    Le leggere tendenze (*sh*→*ch*, togliere *d* e *y*, poco *k*→*t*) vanno verso forme più semplici.
- **e343:**
  - **(a)** lunghezza media delle catene di ripresa (quante volte si risale di fonte in fonte) 0,696 contro 0,625 con le
    righe rimescolate nel paragrafo, z 6,2. **Esito: catene più lunghe del caso.** Distribuzione: 0 23.202, 1 6.213,
    2 2.665, 3 1.260, 4 647, 5 325, 6+ 551.
  - **(b)** prima riga del paragrafo: dall'ultima riga del paragrafo precedente −0,050 rispetto a una sua riga
    qualsiasi (z −7,4); righe interne: dalla riga sopra +0,090 rispetto a una riga lontana; differenza z −14,9.
    **Esito preregistrato: il paragrafo è un confine per la ripresa.**
  - **Cautela:** che la prima riga riprenda **meno** dall'ultima riga precedente che da una riga qualsiasi può venire
    anche dai registri opposti di ultima riga (meno *qo*-, più *ch*-) e prima riga (gallows, *sh*, parole lunghe).
    Resta che la ripresa non attraversa il confine.

## 3/10/2026 — vz: e405, parole nuove, terzo passo: il sacco intero generato è al pavimento (solo sacco 0,495)

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e405.md`). Risultati in
`risultati/e405_parole_nuove_strette.md`. Semi 1–4.

| generatore di parole nuove | prova isolata | sacco intero | previsto (intero) | G1 | G2 | G3 | JSD |
|---|---|---|---|---|---|---|---|
| T-LPS (e403b, e404b) | 0,644 | 0,645 | | 0,63 | 0,57 | 0,63 | 0,61 |
| N1, profilo solo sui segni comuni | 0,622 | 0,582 | 0,58–0,65 | 0,52 | 0,51 | 0,64 | 0,59 |
| N2, anche modello a quattro segni | 0,615 | 0,563 | 0,55–0,63 | 0,50 | 0,49 | 0,64 | 0,59 |
| N3, anche forza della scelta regolata sul pannello (0,37) | — | **0,495** | 0,53–0,62 | 0,50 | 0,48 | 0,64 | 0,47 |

- **Il difetto capito nell'e404b era quello giusto.** Non penalizzare i segni rari porta il sacco intero da 0,645 a
  0,582 (*f* da 0,0018 a 0,0028; Voynich 0,0026). Regolare la forza della scelta sul pannello (JSD 0,0399 contro
  0,0402) lo porta a **0,495: al pavimento**, meglio della previsione.
- **Il modello a quattro segni** guadagna poco (0,019, sotto la soglia di 0,03) e non rende le inventate più vicine a
  parole note (0,548 contro 0,715 del Voynich). Si tiene N3 che lo include perché è quello misurato; la differenza con
  un N3 a trigrammi non è stata misurata. Quasi metà dei campioni del modello dei segni sono parole attestate (47%,
  scartate): soglia di allarme del 60% non superata.
- **Che cosa resta nel sacco** (G3 0,64): le pagine generate sono un filo meno varie (tipi su parole 0,746 contro
  0,756; uniche nella pagina 0,617 contro 0,636) e usano un po' più le parole frequenti (0,439 contro 0,424).
- **La prova isolata resta a 0,62:** le parole inventate, messe al posto esatto delle uniche vere in un testo per il
  resto vero, si vedono ancora un poco; nel sacco generato questo scarto non emerge.
- **Esito secondo la preregistrazione:** sacco intero ≤ 0,58 → **il sacco è chiuso per quanto serve ora**. Passi
  seguenti: i posti delle parole nuove e la disposizione regolata sul sacco generato, poi il banco.
- **Il sacco di pagina, in sintesi (e403–e405):** parole note dal lessico di sezione e lingua, con un carattere nei
  segni prestato da un'altra pagina (κ 0,708) e quasi nessuna ripetizione (θ 2280); parole nuove da un modello dei
  segni imparato sulle parole uniche, con la lunghezza delle uniche, distinto per tipo di posto nella riga, scelte fra
  sei candidate secondo il profilo dei segni comuni della pagina (forza 0,37).

## 3/10/2026 (notte) — e350: il bifoglio è una sessione di scrittura (parole rare e ripresa)

Preregistrato (`preregistrazioni/e350.md`). 176 pagine; coppie della stessa sezione; z con permutazioni delle pagine
dentro la sezione.

| classe di coppie | coppie | rare condivise (Jaccard) | nullo | z | ripresa | nullo | z |
|---|---|---|---|---|---|---|---|
| stesso foglio (recto/verso) | 97 | 0,0205 | 0,0088 | 7,9 | 0,705 | 0,629 | 10,4 |
| **stesso bifoglio, fogli diversi** | 165 | **0,0125** | 0,0087 | **3,2** | **0,705** | 0,630 | **13,3** |
| apertura (pagine affiancate, bifogli diversi) | 64 | 0,0072 | 0,0083 | −0,6 | 0,629 | 0,621 | 0,8 |
| stesso fascicolo, altro | 887 | 0,0098 | 0,0100 | −0,5 | 0,668 | 0,656 | 3,8 |
| altro fascicolo | 6.048 | 0,0041 | 0,0044 | −3,8 | 0,537 | 0,542 | −10,3 |

- **Esito preregistrato: il bifoglio è una sessione**, per le parole rare e per la ripresa.
- **Lettura:**
  - Le due metà di un bifoglio, che nel libro rilegato stanno lontane (per esempio f1 e f8), condividono le parole rare
    e si "riprendono" fra loro **quanto il recto e il verso dello stesso foglio** (ripresa 0,705 in tutti e due i casi).
  - Le pagine affiancate di bifogli diversi, che chi legge vede insieme, no.
  - È la conferma, con una misura sulle parole, dell'e308 (fatto con i profili dei segni): lo scriba ha scritto un
    bifoglio alla volta, con il lessico e le parole del momento, prima che i bifogli fossero piegati e cuciti.
- **Per il voynichizzatore** (da segnalare all'altra chat): il "momento di scrittura" va simulato per bifoglio. Lessico
  rare e ripresa sono condivisi dalle quattro pagine del bifoglio, non dalle pagine affiancate.

## 3/10/2026 (notte) — e351, e352: fascicoli non più coesi del caso (poca potenza); un bifoglio "B" in un fascicolo "A"; etichette senza legame con la sessione

Preregistrato (`preregistrazioni/e351.md`).

- **e351** (30 bifogli dell'erbario, l'unica sezione con almeno 3 fascicoli e abbastanza bifogli):
  - coesione dei fascicoli (ripresa con il proprio fascicolo meno con gli altri) +0,017 contro −0,000 del nullo,
    z 1,7. **Esito preregistrato: no** (con poca potenza: 30 bifogli).
  - Un solo bifoglio oltre la soglia: **D-2** (f26r, f26v, f31r, f31v). Ripresa col proprio fascicolo D 0,623, con il
    fascicolo H 0,825.
  - **Lettura:** f26 e f31 sono in lingua B, in un fascicolo D quasi tutto A, e H è un fascicolo dell'erbario in lingua
    B. Il bifoglio D-2 è una sessione "B" cucita in un fascicolo "A": coerente con bifogli scritti come sessioni e poi
    rilegati.
- **e352** (35 pagine, 770 parole d'etichetta; parola uguale o a una modifica):
  - nel testo della stessa pagina 0,431 contro 0,404, z 1,1;
  - nel testo delle altre pagine dello stesso bifoglio 0,619 contro 0,596, z 0,6.
  - **Esito preregistrato: no** per tutte e due. Le etichette non si legano al testo né della loro pagina né della loro
    sessione (con l'e311).

## 3/10/2026 — vz: e406, il generatore intero a pezzi: 0,558 / 0,703 sui semi di ricerca (v5: 0,812 / 0,918), pagella 13,8

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e406.md`). Del Voynich vero il generatore usa
l'impaginazione e le statistiche. Risultati in `risultati/e406_generatore_pezzi.md`. Semi 1–4.

| strato | AUC e231 | AUC e266 | previste | solo sacco | pagella | estese | trigrammi dal Voynich |
|---|---|---|---|---|---|---|---|
| P1, posti delle parole nuove veri, pesi della disposizione dell'e401b | 0,667 | 0,747 | 0,62–0,70 / 0,72–0,80 | 0,542 | 14,2/18 | 4,8/8 | 1,0% |
| P2, posti dal modello | 0,670 | 0,744 | ±0,03 da P1 | 0,523 | 14,2/18 | 4,5/8 | 1,1% |
| P3, anche i pesi dei legami regolati sul sacco generato | **0,558** | **0,703** | 0,58–0,66 / 0,68–0,77 | 0,523 | 13,8/18 | 4,0/8 | 0,7% |
| v5, stessi semi (e402) | 0,812 | 0,918 | | 0,794 | 16,5/18 | 3,0/8 | |

- **I posti delle parole nuove dal modello non costano niente** (P2 = P1), come previsto: quota per tipo di posto ×
  moltiplicatore della pagina tipo.
- **P3: il giudice dell'e231 scende sotto 0,6 (0,558)**; quello dell'e266 a 0,703. Sono i numeri più bassi mai visti
  nel progetto per un generatore intero, su quattro semi di ricerca; il banco sui semi 7–9 è la verifica.
- **La regolazione dei legami sul sacco generato NON converge** (scarto massimo 14%): il peso dell'unione sale a 2,7,
  quello della coppia esatta va a 0, e le unioni attestate restano a 8,4% (Voynich 9,2%) mentre le coppie viste
  altrove salgono a 25% (22%). **Ipotesi sul perché:** nel Voynich il 68% delle parole uniche si legge come due parole
  note unite, e sono loro a rendere "attestata" l'unione di due parole vicine; le parole inventate lo sono solo nel
  48% dei casi. Il difetto è nel sacco (come nascono le parole nuove), non nella disposizione. Da verificare.
- **La pagella è il punto debole** (13,8 contro 16,5 della v5; cancello della riga perso). Materie mancate in 4 semi
  su 4, con i valori grezzi (Voynich → P3):
  - **legame** (confine): 0,188 → 0,057;
  - **profilo pagina** (V3_R): 1,02 → 0,59; quota media 0,061 → 0,041;
  - **verticale:** 1,028 → 1,003;
  - **scelte di riga:** 12 classi → 5;
  - **concordanza delle desinenze:** 0,043 → 0,106 (troppa);
  - **coppie viste altrove:** 0,221 → 0,251 (troppe, solo in P3);
  - in 2–3 semi: formule (5,2 → 8,7 in P3), gradiente, parole rare per pagina (R 1,96 → 5,6), prime righe come
    registro (z 4,7 → 3,1).
- **Esito secondo la preregistrazione:** P3 migliore di P2 di oltre 0,02 sul giudice forte → **P3 è la v8**
  (`voynichizzatore/pezzi_parametri.json`, versione `v8` nel registro). Va al banco e293.
- **Lettura.** I due giudici, che guardano medie di pagina, sono quasi soddisfatti da un modello fatto di pochi pezzi
  capiti uno per uno. La pagella, che guarda strutture fini fra parole e fra righe (legame, verticale, scelte di grafia
  concordi nella riga), no: è il lavoro che resta, insieme al nascondiglio.

## 3/10/2026 (notte) — e353: la ripresa dalle righe sopra nei generatori pubblicati; un cifrario di testo vero non ce l'ha

Preregistrato (`preregistrazioni/e353.md`). Misura dell'e346 (parole di almeno 3 segni, fonte uguale o a una modifica
nelle 2 righe sopra, nullo con le righe della pagina rimescolate).

| testo | pagine | eccesso E | rapporto R | IC 95% | confronto |
|---|---|---|---|---|---|
| Voynich | 167 | +0,034 | 1,09 | +0,029 – +0,040 | — |
| Naibbe (Greshko 2025), testo vero cifrato | 171 | −0,001 | 1,00 | −0,005 – +0,003 | sotto |
| U2 (Whitehatnetizen 2026) | 123 | +0,061 | 1,39 | +0,055 – +0,067 | sopra |
| U3 (Whitehatnetizen 2026) | 122 | +0,041 | 1,29 | +0,036 – +0,047 | pari |
| Timm e Schinner, seme 1 | 138 | +0,022 | 1,05 | +0,017 – +0,028 | sotto |
| Timm e Schinner, seme 19 | 138 | +0,023 | 1,05 | +0,018 – +0,028 | sotto |

- **Esito preregistrato: la riproducono U2 e U3.**
- **Lettura:**
  - Il cifrario Naibbe, che cifra un testo vero (Plinio) parola per parola, **non ha ripresa**. Un testo vero cifrato
    con un sistema di quel tipo non produce la ripresa dalle righe sopra del Voynich.
  - Il generatore di Timm e Schinner, costruito sull'autocitazione, ne ha meno del Voynich.
  - U2 e U3 ne hanno quanto il Voynich o di più, ma non hanno le proprietà di riga (e134).
  - Nessun metodo pubblicato ha insieme la ripresa e il resto. È un vincolo utile: un'ipotesi sul Voynich deve
    produrre la ripresa (che un cifrario parola per parola non dà) e le proprietà di riga.

## 3/10/2026 (notte) — e354: la direzione della ripresa non si vede, ma la misura ha poca potenza

Preregistrato (`preregistrazioni/e354.md`). Coppie a una modifica fra righe interne consecutive dello stesso paragrafo;
quota in cui la parola sopra è la più frequente; nullo con le righe interne rimescolate.

| testo | coppie | quota con la forma più frequente sopra | nullo | z |
|---|---|---|---|---|
| Voynich | 6.723 | 0,5029 | 0,4998 | 0,5 |
| Timm e Schinner, seme 1 | 19.722 | 0,5082 | 0,5000 | 1,8 |
| Timm e Schinner, seme 19 | 13.899 | 0,5103 | 0,5000 | 2,4 |

- **Esito preregistrato: senza direzione.**
- **Cautela, scritta dopo il risultato:** nel generatore di Timm e Schinner, dove la copia va dall'alto in basso per
  costruzione, la misura arriva appena a z 1,8–2,4. La frequenza delle parole non dice bene quale sia la fonte e quale
  la copia. Il risultato del Voynich non esclude una direzione: dice solo che questa misura non la vede. (La
  preregistrazione non aveva un criterio di validità sul controllo; lo aggiungo qui come lettura.)

## 3/10/2026 — vz: e293, banco della v8 (generatore a pezzi): 0,604 / 0,715 con Isidoro nascosto, decodifica esatta; pagella 41/54



Banco preregistrato dell'e293 (`esegui.py e293 -- --v8`): Isidoro XVII nascosto con la chiave "banco" nelle cinque scelte di grafia (modello v3), corpi con i semi di verifica 7, 8, 9. **Decodifica esatta nei tre manoscritti.**



| versione | pagella (3 semi) | pagella estesa | riga | AUC e231 | AUC e266 |

|---|---|---|---|---|---|

| v5 (copia e modifica) | 49/54 | 57/78 | 0 | 0,816 | 0,917 |

| **v8 (a pezzi, e400–e406)** | 41/54 | 56/78 | 0 | **0,604** | **0,715** |



- Per seme (e231 / e266): seme 7 0,640 / 0,753; seme 8 0,553 / 0,653; seme 9 0,620 / 0,739. Pagella 14, 13, 14.

- **Esito con il criterio dell'e293** (AUC dell'e266 almeno −0,01 a pagella estesa non inferiore): l'AUC scende di 0,20 ma la pagella estesa è 56 contro 57: **formalmente "non migliora"** per un punto di pagella estesa. Lo dichiaro così com'è: la v8 è molto meno riconoscibile dai giudici e prende meno materie delle 18 (41 contro 49).

- I semi di verifica confermano i semi di ricerca (0,558 / 0,703 senza messaggio): niente effetto vincitore questa volta. Il messaggio nascosto costa circa 0,05 / 0,01, in linea con il costo del nascondiglio misurato nell'e400 (0,63 da solo sul Voynich vero).

- Del Voynich vero la v8 usa l'impaginazione e le statistiche (lessico per sezione e lingua, caratteri di pagina, forme delle parole uniche, affinità ai posti, legami); trigrammi di parole in comune con il Voynich 0,7–1% (e406).

- Lavoro che resta: le materie di pagella perse (legame, verticale, scelte di riga, concordanza delle desinenze, profilo pagina), il cancello della riga, il nascondiglio.

## 3/10/2026 (notte) — e347, e348, e349: lo scriba guarda indietro 1–2 righe; le parole uniche non nascono dalla ripresa; l'erbario B riprende più dell'erbario A

Preregistrato (`preregistrazioni/e347.md`).

- **e347**, eccesso di ripresa dalla riga a distanza L (z):

  | L | Voynich esatta | Voynich modificata | Timm e Schinner 1, esatta / modificata | Timm e Schinner 19, esatta / modificata |
  |---|---|---|---|---|
  | 1 | +0,009 (6,5) | +0,031 (12,8) | +0,016 (9,5) / +0,031 (11,5) | +0,014 (8,4) / +0,027 (11,1) |
  | 2 | +0,005 (3,1) | +0,009 (3,1) | +0,009 (5,1) / +0,009 (3,2) | +0,006 (4,7) / +0,009 (3,5) |
  | 3 | +0,001 (0,3) | +0,001 (0,3) | +0,007 (3,9) / +0,011 (3,9) | +0,004 (2,2) / +0,009 (3,3) |
  | 4 | −0,000 | −0,000 | +0,010 (5,4) / +0,014 (5,2) | +0,006 (3,5) / +0,017 (6,9) |
  | 5–6 | ~0 | ~0 | z 2–4 | z 2–4 |

  - **Esito preregistrato** (ultima distanza con z > 3): Voynich 2 righe (esatte e modificate); Timm e Schinner 4–6
    righe.
  - **Lettura:** lo scriba riprende soltanto dalla riga subito sopra e da quella prima ancora; dalla terza in su niente.
    Il generatore di Timm e Schinner pesca fino a 6 righe sopra. È la prima differenza netta fra il Voynich e la loro
    teoria.
- **e348:** 3.099 parole uniche. Eccesso di fonte modificata nelle 2 righe sopra: uniche +0,018, altre della stessa
  lunghezza +0,062; differenza z −9,5. **Esito preregistrato: no.**
  - Le parole uniche hanno **meno** delle altre una parola a una modifica nelle righe subito sopra.
  - Quando ce l'hanno, la fonte è meno frequente (mediana 43 occorrenze contro 136).
  - Non nascono copiando con modifica le righe appena scritte: vengono da un altro processo (invenzioni o errori
    sparsi, con l'e296).
- **e349** (E1p complessivo +0,036):
  - erbario in lingua A +0,025 (IC 0,013–0,036) ed erbario in lingua B +0,055 (0,041–0,071) diversi dalla media;
  - B-B +0,041, S-B +0,037, mani 1, 2, 3 da +0,031 a +0,042, tutti nella media.
  - **Esito preregistrato: gruppi diversi dalla media: erbario A (meno ripresa) ed erbario B (più ripresa).** La mano
    non conta.

## 3/10/2026 (notte) — e355: gli "errori" restano sul foglio; le sessioni differiscono in inventiva

Preregistrato (`preregistrazioni/e355.md`).

- **(a)** 975 varianti rare (2–5 occorrenze a una modifica da una parola con almeno 20): coppie di occorrenze su
  pagine diverse della stessa sezione, osservate / attese:

  | classe | rapporto | z |
  |---|---|---|
  | stesso foglio | 1,78 | 5,1 |
  | stesso bifoglio, fogli diversi | 1,33 | 2,9 |
  | apertura | 1,04 | 0,2 |
  | stesso fascicolo, altro | 0,94 | −2,2 |
  | altro fascicolo | 0,90 | −4,8 |

  **Esito preregistrato: incerto** (il bifoglio a z 2,9). L'andamento è quello della sessione: le varianti tornano sul
  foglio e un po' nel bifoglio, non sulle pagine affiancate.
- **(b)** 48 bifogli con almeno 150 parole:
  - varianza della quota di parole uniche fra bifogli 2,04 volte il nullo, **z 13,7**;
  - correlazione con la ripresa −0,155 (z −1,1).
  - **Esito preregistrato: sessioni più o meno inventive.** Alcune sessioni producono molte più parole nuove di altre,
    indipendentemente da quanto riprendono.

## 3/10/2026 (notte) — e356: ogni bifoglio ha una sola lingua e quasi sempre una sola mano; la copia eredita solo -dy/-ey

Preregistrato (`preregistrazioni/e356.md`).

- **(a)** Bifogli con almeno 2 pagine etichettate (intestazioni della ZL; nullo con le etichette rimescolate dentro il
  fascicolo):

  | etichetta | bifogli | omogenei | atteso | z |
  |---|---|---|---|---|
  | lingua A/B | 48 | **100%** | 65% | 11,8 |
  | mano di Davis | 52 | **94%** | 63% | 13,9 |

  - **Esito preregistrato: lingua di sessione; mano di sessione.**
  - Nessun bifoglio mescola A e B. Tre bifogli mescolano le mani: H-1 (f57: mani 5 e 1; f66: mano 5), N-1 (il
    pieghevole f85/f86) e T-2 (f104, f115).
  - Con l'e350: il bifoglio è un'unità di scrittura completa, con una lingua, di solito uno scriba, un lessico e una
    ripresa sue.
- **(b)** ripresa dalle 2 righe sopra per posizione della parola nella riga (eccesso, z):
  - prima +0,056 (8,9);
  - seconda +0,051 (6,0);
  - **in mezzo +0,059 (15,1)**;
  - penultima +0,044 (6,0);
  - **ultima +0,027 (3,6)**.

  Si riprende ovunque, meno nell'ultima parola, che ha forme sue (e337).
- **(c)** stessa scelta di grafia fra parole con la stessa forma normalizzata, righe vicine (1–2) contro lontane (3+):
  - *ch*/*sh* 0,560 contro 0,541 (z 2,0);
  - *k*/*t* 0,615 contro 0,617;
  - -*l*/-*r* 0,595 contro 0,610;
  - *o*-/*qo*- 0,585 contro 0,587;
  - **-*dy*/-*ey* 0,795 contro 0,766 (z 4,1)**.
  - **Esito preregistrato: in parte (-*dy*/-*ey*).** Quando lo scriba riprende una parola dalle righe sopra non ne
    copia la grafia: la sceglie di nuovo, salvo una leggera eredità per -*dy*/-*ey*.

## 3/10/2026 (notte) — e357: gli "errori" sono uniformi come errori casuali; l'inventiva delle sessioni sta nelle forme nuove

Preregistrato (`preregistrazioni/e357.md`). 48 bifogli con almeno 150 parole. Varianza fra i bifogli, come scarto dalla
media del proprio strato sezione × lingua, contro le parole rimescolate fra i bifogli dello stesso strato:

| quota | rapporto sul nullo | z |
|---|---|---|
| parole uniche | 3,80 | 11,2 |
| "errori" (uniche a una modifica da una parola con almeno 20 occorrenze) | **1,05** | **0,2** |
| forme nuove (le altre uniche) | **4,04** | **11,8** |

- **Esiti preregistrati: inventiva oltre la sezione; fatta di forme nuove.**
- Nessun legame con la lunghezza media delle parole (Spearman 0,02) né con la posizione nel libro (−0,03).
- I più inventivi: O-1, Q-1 (erbario A), I-1, H-2 (S-A), H-1 (T-B), G-4: 20–25% di parole uniche. I meno: M-1, M-3,
  M-4 (biologica B), E-1 (erbario B), B-2, E-3 (erbario A): 7–9%.
- **Lettura** (con l'ipotesi di Davide dell'e296):
  - Le parole uniche che sono varianti di una lettera di parole frequenti hanno **la stessa frequenza in tutte le
    sessioni**, come ci si aspetta da veri errori di scrittura o di lettura, che capitano a caso.
  - Le forme davvero nuove dipendono dalla sessione: alcune sessioni inventano molto, altre quasi niente. Sono due
    processi diversi.
  - Con l'e348: né gli uni né le altre nascono dalla ripresa delle righe sopra.

## 3/10/2026 (notte) — e358: dentro il bifoglio, un indizio di scrittura a foglio piegato (incerto)

Preregistrato (`preregistrazioni/e358.md`). 44 bifogli completi (quattro pagine di almeno 6 righe). Passaggio da P a Q
= ripresa fra la fine di P e l'inizio di Q, meno il contrario; z con inversione del segno.

| passaggio | media | z |
|---|---|---|
| Xr→Xv (stesso foglio) | +0,037 | 1,3 |
| Yr→Yv (stesso foglio) | +0,056 | 2,3 |
| Xv→Yr (faccia interna aperta) | −0,007 | −0,2 |
| Yv→Xr (faccia esterna aperta) | −0,044 | −1,6 |

- Piegato, i due passaggi insieme: z 2,5. Aperto: z −1,3. **Esito preregistrato: incerto.**
- L'indizio va nella direzione di una scrittura foglio per foglio (recto e poi verso), non sulla pergamena aperta,
  come le e330, e331, e341 (z intorno a 2). Usano però gli stessi fogli, quindi non si sommano.

## 3/10/2026 (notte) — e359: le forme nuove usano i pezzi della loro sessione, ma non più delle parole comuni

Preregistrato (`preregistrazioni/e359.md`). Una parola è "composta" in un insieme di parole se si taglia in un inizio e
una fine (almeno 2 segni ciascuno) presenti come inizio e fine di altre parole dell'insieme.

| parole | numero | composte nel proprio bifoglio | in un altro della sezione | eccesso | z |
|---|---|---|---|---|---|
| forme nuove | 3.243 | 0,633 | 0,523 | +0,111 | 20,6 |
| errori | 1.202 | 0,697 | 0,613 | +0,084 | 8,6 |
| parole comuni | 694 | 0,918 | 0,790 | +0,128 | 10,5 |

- **Esito preregistrato: incerto** (le forme nuove superano il caso, ma non le parole comuni).
- **Lettura:** ogni parola è più "componibile" con i pezzi della propria sessione che con quelli di un'altra: è la
  coerenza del lessico di sessione (e350). Le forme nuove non lo sono più delle altre. Non c'è un processo speciale di
  invenzione per ricombinazione oltre questa coerenza.

## 3/10/2026 (notte) — e360: l'inventiva delle sessioni non è un effetto dei paragrafi

Preregistrato (`preregistrazioni/e360.md`), controllo dell'e357.

| righe usate | dispersione delle forme nuove, rapporto sul nullo | z |
|---|---|---|
| tutte | 4,03 | 12,3 |
| senza le prime righe dei paragrafi | 3,76 | 10,8 |
| solo righe interne | 3,28 | 9,0 |

- Densità di paragrafi contro quota di forme nuove: Spearman 0,216, z 1,5.
- **Esito preregistrato: l'inventiva non è un effetto dei paragrafi.** Le sessioni differiscono nella quota di forme
  nuove anche nelle righe interne dei paragrafi.

## 3/10/2026 (notte) — e361: le forme nuove non sono due parole attaccate

Preregistrato (`preregistrazioni/e361.md`).

- Forme nuove di almeno 5 segni: 3.090; si tagliano in due parole esistenti (parti con almeno 3 occorrenze) il **48,7%**.
- Gli errori il 44,3%; le parole comuni della stessa lunghezza il **76,2%**; differenza z −39,3.
- **Esito preregistrato: no.** Le forme nuove si spiegano come due parole attaccate **meno** delle parole comuni.
- Fra quelle che si tagliano, la coppia compare altrove come due parole vicine il 16% (fondo 9%). In fine riga 22%
  contro 18%.
- **Lettura:** le forme nuove non sono spazi mancati o non visti. Sono forme insolite, fatte di pezzi meno comuni
  (con l'e359: pezzi presi più spesso dalla propria sessione, come per tutte le parole).

## 3/10/2026 (notte) — e362: le forme nuove hanno sequenze di segni insolite, tipiche di una fine e un inizio di parola; arrivano a gruppi nella riga

Preregistrato (`preregistrazioni/e362.md`).

- **(a)** catena di Markov di ordine 2 sui segni, stimata sulle parole non uniche (per le parole comuni, senza la parola
  stessa):

  | parole | numero | log-verosimiglianza per segno | comuni a pari lunghezza | z |
  |---|---|---|---|---|
  | forme nuove | 3.373 | −2,355 | −1,276 | −256,6 |
  | errori | 1.403 | −2,471 | −1,578 | −102,1 |

  - **Esito preregistrato: forme nuove fuori dalle regole dei segni.**
  - Passaggi più tipici delle forme nuove rispetto alle comuni: *ee*→*a* 15×, *ir*→*o* 13×, *al*→*sh* 11×,
    *or*→*ch* 11×, *ar*→*ch* 9×, *od*→*e* 9×, *lo*→*d* 8×, *ik*→*h* 8×, *fch*→*o* 8×, *ep*→*ch* 7×.
  - **Due cautele, scritte dopo il risultato:**
    1. in qualunque lingua le parole uniche hanno sequenze più rare delle comuni: serve un riferimento in una lingua
       vera per dire se le forme nuove del Voynich sono più "fuori regola" degli hapax di un testo normale;
    2. molti passaggi tipici sono una **fine di parola** (-*al*, -*or*, -*ar*, -*od*) seguita da un **inizio di parola**
       (*ch*-, *sh*-, *e*, *d*): sembrano pezzi di parole incollati, anche se non due parole intere frequenti (e361).

    Verifica: e363.
- **(b)** coppie di forme nuove nella stessa riga 1.702 contro 1.530 del nullo (forme nuove rimescolate nel paragrafo),
  z 5,2; nello stesso paragrafo 11.141 contro 11.641 (rimescolate nella pagina), z −3,0.
  - **Esito preregistrato: momenti inventivi** nella riga: le forme nuove arrivano a gruppi dentro la stessa riga, mentre
    fra i paragrafi della pagina sono anzi più sparse del caso.

## 3/10/2026 (notte) — e363: un terzo delle forme nuove contiene una "giuntura" fra due parole; le parole comuni del Voynich sono molto più regolari di quelle di una lingua

Preregistrato (`preregistrazioni/e363.md`). Voynich, latino e italiano, circa 32.000 parole ciascuno.

| testo | forme nuove | ll per segno, forme nuove | comuni a pari lunghezza | Δ | con giuntura: forme nuove | comuni | z |
|---|---|---|---|---|---|---|---|
| Voynich | 3.371 | −2,354 | −1,271 | **−1,083** | **0,345** | 0,073 | 63,1 |
| latino | 2.799 | −2,350 | −2,062 | −0,288 | 0,197 | 0,171 | 4,0 |
| italiano | 1.936 | −2,367 | −2,185 | −0,181 | 0,214 | 0,171 | 5,1 |

- **Esiti preregistrati:** (a) le forme nuove del Voynich sono più fuori regola degli hapax di una lingua; (b) le forme
  nuove contengono giunture di parola.
- **Lettura:**
  - **(a)** In assoluto le forme nuove del Voynich sono "irregolari" quanto gli hapax di latino e italiano (−2,35 nat
    per segno in tutti e tre). È il resto del lessico del Voynich a essere molto più regolare (−1,27 contro −2,06 e
    −2,19): le parole comuni seguono regole di formazione strette (e43, e115), e le forme nuove ne escono.
  - **(b)** Il 34,5% delle forme nuove contiene, all'interno, una coppia di segni tipica del **confine fra due parole**
    (per esempio *l*|*ch*, *l*|*d*, *l*|*q*, *m*|*ch*, *d*|*q*), contro il 7,3% delle parole comuni. In latino e
    italiano la differenza è minima.
  - Molte forme nuove sembrano quindi pezzi di due parole scritti senza uno spazio visibile. Non due parole intere
    frequenti (e361), ma una fine e un inizio di parola.
  - È coerente con l'incertezza nota sugli spazi del Voynich. Una parte delle "parole uniche" sarebbe un fatto di
    spaziatura, non di lessico.
- **Verifica:** e364, se l'"inventiva" delle sessioni (e357) sia un'abitudine di spaziatura.

## 3/10/2026 (notte) — e364: l'inventiva delle sessioni è soprattutto vera, la spaziatura conta meno

Preregistrato (`preregistrazioni/e364.md`). 48 bifogli; forme nuove divise con le coppie di confine dell'e363.

| forme nuove | dispersione fra bifogli, rapporto sul nullo | z |
|---|---|---|
| con giuntura (spaziatura) | 1,85 | 3,3 |
| senza giuntura | **4,03** | **11,5** |

- Lunghezza media delle parole del bifoglio contro forme nuove con giuntura: Spearman −0,09 (z −0,6).
- **Esito preregistrato: tutte e due.**
- **Lettura:** le sessioni differiscono un poco nel modo di spaziare, ma soprattutto nella quantità di forme davvero
  nuove, senza giunture. L'"inventiva" dell'e357 regge come proprietà della sessione.

## 3/10/2026 (notte) — e365: nessuna prova di due modi di scrittura; le forme nuove stanno ai bordi della riga

Preregistrato (`preregistrazioni/e365.md`).

- 2.457 righe:
  - Spearman fra numero di forme nuove della riga e ripresa delle sue altre parole −0,031 (nullo −0,062), z 2,1;
  - ripresa media delle altre parole 0,512 nelle righe senza forme nuove, 0,483 in quelle con 2 o più.
  - **Esito preregistrato: incerto.** Nessuna prova che lo scriba alterni righe "copiate" e righe "inventate".
- **Descrittiva:** le forme nuove stanno il doppio delle volte ai **bordi della riga**:

  | posizione | forme nuove | altre parole |
  |---|---|---|
  | prima parola | 21,5% | 10,8% |
  | ultima parola | 20,3% | 10,9% |
  | in mezzo | 39,4% | 55,1% |

  I bordi hanno forme loro (e337: prime parole con *t*/*k*/*p*, ultime con -*m*/-*g*), e lì nascono più parole nuove.

## 3/10/2026 (notte) — e366: ai bordi della riga lo scriba attacca un segno a parole normali

Preregistrato (`preregistrazioni/e366.md`). Forme nuove (uniche non varianti) di almeno 3 segni.

| forme nuove | numero | parola nota togliendo il primo segno | togliendo l'ultimo |
|---|---|---|---|
| prime della riga (non di paragrafo) | 419 | **0,356** | 0,053 |
| ultime della riga | 684 | 0,158 | **0,104** |
| in mezzo | 1.963 | 0,228 | 0,052 |

- **Esiti preregistrati:**
  - **segno di inizio riga** (z 5,5); i segni tolti sono *y* 44, *d* 28, *s* 26, *t* 17, *o* 13, *sh* 7;
  - **segno di fine riga** (z 4,7); i segni tolti sono *y* 22, *d* 14, *s* 11, *g* 9, *o* 5, *m* 4.
- **Lettura:** molte "parole uniche" ai bordi della riga sono parole normali con un segno in più:
  - all'inizio, *y*-, *d*-, *s*- (diversi dal gallows dell'inizio di paragrafo);
  - alla fine, -*y*, -*d*, -*s*, -*g*, -*m*.

  Spiega perché le forme nuove stanno il doppio ai bordi (e365) e perché la prima parola della riga è più lunga
  (e306). Come per il paragrafo (e310, e316), i bordi della riga hanno segni loro.

## 3/10/2026 (notte) — e346: prima esecuzione fermata per lentezza; codice ottimizzato senza cambiare il metodo

- La prima esecuzione dell'e346 (avviata alle 22:24) è stata fermata alle 22:56, dopo 33 minuti di CPU, senza
  risultati. Il calcolo delle parole simili confrontava tutte le coppie di tipi di ogni documento, e i testi sensati
  hanno migliaia di tipi.
- **Correzione del codice, stesso metodo:**
  - le somiglianze (uguale o a una modifica) si trovano con un indice per chiavi (jolly e cancellazioni, come
    nell'e350), che dà esattamente le stesse coppie;
  - i valori di ogni documento si calcolano una volta sola e si riusano nei sottogruppi (categorie, autori).
- Si riesegue con lo stesso seme.

## 3/10/2026 (notte) — e367: le prime parole "segno + parola" esistono anche staccate, ma manca il confronto con il centro della riga

Preregistrato (`preregistrazioni/e367.md`).

- 1.760 prime parole di riga (non di paragrafo) della forma p + X, con p ∈ {*s*, *d*, *y*, *o*, *l*, *r*} e X parola
  nota. Nel 45,7% dei casi la coppia "p X" compare staccata in mezzo a un'altra riga, contro il 12,6% del nullo (X
  sostituita da una parola della stessa frequenza): **z 44,0. Esito preregistrato: la parolina staccata si attacca a
  inizio riga.**
- Descrittiva:
  - *d* da sola è rarissima a inizio riga (0,06%), mentre le prime parole "*d* + parola" sono il 16,8% delle prime
    parole;
  - *y* da sola è più frequente a inizio riga (1,8%) che in mezzo (0,6%).
- **Cautela, scritta dopo il risultato:**
  - fra gli esempi ci sono *daiin* (*d* + *aiin*), *saiin*, *otchy*: parole comuni che si trovano dappertutto, e che il
    trascrittore a volte divide ("*d aiin*");
  - il risultato può misurare l'incertezza generale degli spazi, non un fatto dell'inizio riga;
  - manca il confronto con le parole p + X **in mezzo** alla riga.

  Verifica: e368.

## 3/10/2026 (notte) — e368: a inizio riga la parolina *s* (e *l*, *y*) si attacca alla parola seguente

Preregistrato (`preregistrazioni/e368.md`), verifica dell'e367. Indice di attacco = forme p + X / (forme p + X +
parolina p staccata seguita da X), su 3.311 righe non prime di paragrafo.

| segno | a inizio riga (attaccate/staccate) | in mezzo |
|---|---|---|
| *s* | **0,955** (337/16) | **0,535** (243/211) |
| *d* | 0,996 (554/2) | 0,982 (1.342/24) |
| *y* | 0,891 (418/51) | 0,817 (535/120) |
| *o* | 0,953 (325/16) | 0,970 (3.021/94) |
| *l* | 0,967 (59/2) | 0,839 (651/125) |
| tutti | 0,951 | 0,910 |

- Differenza complessiva +0,041 (IC 95% +0,029 – +0,054), z 6,7. **Esito preregistrato: a inizio riga la parolina si
  attacca di più.**
- **Lettura:**
  - *s* in mezzo alla riga si scrive staccata quasi una volta su due, all'inizio della riga quasi mai.
  - Lo stesso, più debole, per *l* e *y*; *d* e *o* sono quasi sempre attaccate dappertutto.
  - Una parte delle "parole lunghe" e delle forme nuove a inizio riga (e306, e365, e366) viene da questo modo di
    spaziare all'inizio della riga.
  - L'e367 misurava anche l'incertezza generale degli spazi; l'effetto specifico dell'inizio riga c'è, ma è più
    piccolo e concentrato su *s*.

## 3/10/2026 (notte) — e369: gli "errori" non sono specificamente errori di copiatura dalla riga sopra (incerto)

Preregistrato (`preregistrazioni/e369.md`).

| gruppo | occorrenze | madre/sorella nelle 2 righe sopra | nullo | eccesso | z |
|---|---|---|---|---|---|
| errori (1–5 occorrenze, a una modifica da una parola con almeno 20) | 2.321 | 0,173 | 0,153 | +0,020 | 4,1 |
| parole frequenti con una sorella frequente | 13.335 | 0,508 | 0,474 | +0,034 | 10,9 |

- Differenza degli eccessi −0,015, z −2,3. **Esito preregistrato: incerto.**
- **Lettura:**
  - La parola "giusta" sta nelle righe subito sopra un errore un po' più del caso, come per qualunque parola (è la
    ripresa dell'e340); in proporzione un poco di più (1,13 volte il caso contro 1,07), ma non abbastanza da parlare di
    errori di copiatura.
  - Con l'e357 (errori uniformi fra le sessioni): gli errori si comportano più come sbagli sparsi che come copie
    sbagliate della riga sopra.

## 3/10/2026 — vz: e407, tre pezzi per la pagella: unioni, legame fra ultimo e primo segno, verticale → 0,541 / 0,659, pagella 16,5/18

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e407.md`). Risultati in `risultati/e407_verso_pagella.md`.
Semi 1–4; ogni strato regola i suoi pesi sul pannello (seme 11).

- **Conteggio fatto prima (proprietà del testo).** Nel Voynich l'8,8% delle coppie di parole vicine dà, unita, una
  parola attestata; 2,7 punti vengono da parole **uniche** che sono due parole attaccate (la stessa coppia è scritta
  una volta unita e altre volte staccata), 6,1 da parole note. L'81% delle parole uniche si legge come due parole
  attestate unite. Nella v8 le unioni con parola unica erano 1,3 punti: per questo la regolazione dell'e406 non
  convergeva.

| strato | regolazione | AUC e231 | AUC e266 | pagella | estese | materia del pezzo |
|---|---|---|---|---|---|---|
| P3 dell'e406 (v8) | non converge (14%) | 0,558 | 0,703 | 13,8/18 | 4,0/8 | |
| U1, parole nuove come unioni | converge (7%) | 0,548 | 0,659 | 15,2/18 | 4,0/8 | unione = parola unica 3,4% (Voynich 2,7%); formule 4,3 (5,2) |
| U2, + legame fra ultimo e primo segno | converge (10%) | 0,559 | 0,673 | 16,0/18 | 3,0/8 | confine 0,177 (0,188): **legame preso in 4 semi** |
| U3, + verticale | converge (10%) | **0,541** | **0,659** | **16,5/18** | 3,2/8 | verticale 1,029 (1,028): **presa in 4 semi** |

- **Previsioni rispettate** per tutti e tre i pezzi: la regolazione converge, la materia del pezzo viene presa, i
  giudici non peggiorano (anzi: giudice forte da 0,703 a 0,659).
- **L'ipotesi sulle unioni era giusta:** con una parte delle parole nuove fatta di due parole note della pagina
  attaccate, il peso dell'unione torna normale (da 2,7 a 0,7–1,2) e la regolazione converge.
- **Pagella 16,5/18, come la v5** (16,5 sugli stessi semi), con i giudici a 0,54 / 0,66 contro 0,81 / 0,92.
- **Che cosa manca ancora** (U3, in 4 semi su 4): profilo pagina (V3_R 0,62 contro 1,02), prime righe come registro
  (z 2,3 contro 4,7), scelte di riga (3,5 classi contro 12), concordanza delle desinenze (0,12 contro 0,043: troppa);
  in 2–3 semi: dispersione delle lunghezze, gradiente, parole rare per pagina (R 4,9, fascia ≤ 5), coppie viste
  altrove (0,243 contro 0,221). Il cancello della riga resta perso in tutti i semi.
- **Effetto collaterale da tenere d'occhio:** con le unioni il solo sacco sale da 0,523 a 0,561 (JSD
  pagina-manoscritto 0,046 contro 0,040: le parole fatte di parole della pagina ne rafforzano il profilo).
- **Esito secondo la preregistrazione:** i tre pezzi si tengono; U3 diventa la **v9**
  (`voynichizzatore/pezzi_parametri_v9.json`) e va al banco.
- **Lettura per la ricerca sul Voynich.** Tre proprietà note (unioni e227, legame e22/e152, copia verticale e228) si
  riproducono ognuna con un termine solo, debole, e convivono: nel generatore vecchio si pestavano i piedi.

## 3/10/2026 (notte) — e370: la crescita di -ey scendendo nella pagina c'è sia nelle parole riprese sia nelle altre (incerto)

Preregistrato (`preregistrazioni/e370.md`).

| parole in -dy/-ey | pagine | quota di -ey, metà bassa − metà alta | z |
|---|---|---|---|
| riprese dalle 2 righe sopra | 53 | +0,146 | 3,5 |
| non riprese | 67 | +0,074 | 2,5 |

- **Esito preregistrato: incerto.**
- La crescita è più forte nelle parole riprese (che ereditano la scelta, e356), ma c'è anche nelle altre. La ripresa la
  amplifica, non la spiega da sola.

## 3/10/2026 (notte) — e371: l'inventiva delle sessioni regge anche senza i bordi della riga

Preregistrato (`preregistrazioni/e371.md`). 48 bifogli, 21.120 parole in mezzo alla riga (righe non prime di
paragrafo). Dispersione della quota di forme nuove fra i bifogli: **3,41 volte il nullo, z 9,1. Esito preregistrato:
l'inventiva regge senza i bordi.** Con e360 ed e364: la differenza fra sessioni nelle forme nuove non dipende dai
paragrafi, dalla spaziatura né dai segni di bordo.

## 3/10/2026 (notte) — e372: la ripresa copia pezzi di riga, anche a ordine invertito

Preregistrato (`preregistrazioni/e372.md`). Coppie di parole vicine entrambe con una fonte (uguale o a una modifica)
nella riga subito sopra; "in blocco" se le fonti sono anche loro vicine.

| testo | coppie | stesso ordine | nullo | z | ordine invertito | nullo | z |
|---|---|---|---|---|---|---|---|
| Voynich | 3.125 | 0,235 | 0,182 | **8,0** | 0,210 | 0,182 | **4,3** |
| Timm e Schinner, seme 1 | 6.690 | 0,314 | 0,294 | 4,6 | 0,302 | 0,294 | 1,7 |
| Timm e Schinner, seme 19 | 5.365 | 0,236 | 0,205 | 5,9 | 0,213 | 0,205 | 1,7 |

- **Esito preregistrato: copia a pezzi.**
- Lo scriba riprende anche **coppie** di parole vicine dalla riga sopra, di solito nello stesso ordine, ma più del caso
  anche invertite. Nel generatore di Timm e Schinner l'ordine invertito non c'è: un'altra differenza dalla loro teoria,
  oltre alla distanza (e347).

## 3/10/2026 — vz: e293, banco della v9: la pagella sale (44/54), ma con il nascondiglio vecchio il giudice dell'e231 risale a 0,668



Banco preregistrato dell'e293 (`esegui.py e293 -- --v8 --v9`): Isidoro XVII nascosto con la chiave "banco" nelle cinque scelte di grafia, semi 7, 8, 9. Decodifica esatta nei sei manoscritti. La v8 rifatta con il codice nuovo è identica al banco precedente (controllo).



| versione | pagella (3 semi) | pagella estesa | riga | AUC e231 | AUC e266 |

|---|---|---|---|---|---|

| v5 | 49/54 | 57/78 | 0 | 0,816 | 0,917 |

| v8 | 41/54 | 56/78 | 0 | 0,604 | 0,715 |

| v9 | 44/54 | 56/78 | 0 | 0,668 | 0,719 |



- **La v9 non migliora la v8 al banco:** la pagella sale di 3 punti, il giudice forte è uguale (0,719 contro 0,715), quello dell'e231 **peggiora** (0,668 contro 0,604). Per seme: 0,654 / 0,733; 0,681 / 0,729; 0,670 / 0,695.

- **Non è effetto vincitore, è il nascondiglio.** Senza messaggio, sui semi di ricerca, la v9 fa 0,541 / 0,659 e la v8 0,558 / 0,703: il messaggio costa alla v8 circa +0,05 / +0,01 e alla v9 circa **+0,13 / +0,06**. Il nascondiglio vecchio riscrive le cinque scelte di grafia (ch/sh, k/t, qo-/o- all'inizio; -l/-r, -dy/-ey alla fine): cambia proprio il primo e l'ultimo segno delle parole, cioè rompe il legame fra ultimo e primo segno e le unioni che la v9 ha appena imparato a fare. Più il corpo è fine, più questo nascondiglio lo rovina. (Ipotesi coerente con l'e400, dove il nascondiglio da solo sul Voynich vero costava 0,63; la verifica diretta è l'e409.)

- **Conseguenza:** il nascondiglio va cambiato prima di tutto il resto. Preregistrato l'e409: il messaggio nel sacco (nei conteggi delle parole note di ogni pagina), senza più riscrivere le scelte di grafia.

## 3/10/2026 (notte) — e373: le sessioni differiscono lungo dimensioni quasi tutte indipendenti

Preregistrato (`preregistrazioni/e373.md`). 48 bifogli, otto misure per bifoglio come scarti dal proprio strato
(sezione × lingua): asse -*edy*/-*aiin*, forme nuove, errori, ripresa, -*ey*, *qo*-, lunghezza media delle parole,
coppie identiche vicine. Correlazioni di Spearman con 1.000 permutazioni e soglia di Bonferroni su 28 coppie.

- **Esito preregistrato: più dimensioni.** La prima componente spiega il 28% (soglia per "un solo carattere": 40%), poi
  16%, 15%, 13%.
- **Una sola coppia legata:** forme nuove ~ lunghezza (+0,50, z 3,5). Quasi sotto soglia: forme nuove ~ coppie
  identiche (−0,40, z −2,7), asse ~ forme nuove (+0,34, z 2,3), *qo*- ~ lunghezza (+0,31, z 2,2).
- **Controllo non preregistrato** (scratchpad): la coppia legata è in buona parte meccanica, perché le forme nuove sono
  parole lunghe e alzano la media del loro bifoglio. Con la lunghezza delle sole parole non uniche la correlazione scende
  a +0,27; con le parole di frequenza almeno 5 a +0,20.
- **La ripresa non è legata a niente** (|ρ| ≤ 0,10 con tutte le altre misure): una sessione che inventa molte forme
  nuove non copia né di più né di meno dalle righe sopra. Inventiva e ripresa sono due abitudini separate.
- Lettura: le sessioni non hanno un unico "carattere"; ogni proprietà (lessico dell'asse, inventiva, grafia, ripresa)
  varia per conto suo. Per il voynichizzatore: queste manopole si possono girare in modo indipendente fra le sessioni.

## 3/10/2026 (notte) — e375: oltre la giuntura, le parole del Voynich quasi non scelgono le vicine

Preregistrato (`preregistrazioni/e375.md`). S = tipi di coppia di parole vicine (diverse e non varianti) presenti su
almeno 2 pagine. Nullo: scambi dentro la pagina fra parole con lo stesso primo segno, lo stesso ultimo segno e la stessa
posizione nella riga. Così restano intatti giunture, lessico di pagina e bordi; si perde solo la preferenza di una
parola per una vicina precisa. Codice provato prima solo sui controlli.

| testo | parole | S | nullo | R | z |
|---|---|---|---|---|---|
| Voynich | 34.863 | 2.060 | 2.008 | **1,03** | **2,0** |
| testi sensati: Historical | 34.626 | 2.219 | 1.614 | 1,38 | 29,9 |
| testi sensati: Modern | 34.995 | 1.935 | 1.488 | 1,30 | 26,4 |
| testi sensati: Conlangs | 30.023 | 1.987 | 1.755 | 1,13 | 12,9 |
| gibberish umano | 10.075 | 74 | 65 | 1,13 | 2,2 |
| Timm e Schinner, seme 1 | 37.224 | 2.340 | 2.374 | 0,99 | −1,1 |

Voynich a parità di parole col gibberish (mediana di 20 sottoinsiemi): R 1,08, z 2,2.

- **Controllo positivo superato:** nei testi sensati le coppie tornano su più pagine dal 13% al 38% più del nullo.
- **Esito preregistrato: incerto** (z 2,0, fra 2 e 3).
- **L'effetto, se c'è, è piccolo:** l'eccesso del Voynich (3%) è meno di un quarto di quello del gruppo di testi sensati
  più basso (le lingue artificiali, 13%). Quasi tutta la struttura fra parole vicine sta nella giuntura fra ultimo e
  primo segno. Una lingua con le sue locuzioni lascerebbe molto di più, a parità di parole.
- **Le coppie più in eccesso** sono quasi tutte una parolina più una parola: *or aiin*, *ol aiin*, *ol olaiin*,
  *or cheey*, *ol cheey*, *ol sheey*. Potrebbero essere parole spezzate dallo spazio (*oraiin*, *olaiin*), in linea con
  le giunture senza spazio dell'e361–e363: il confine fra parole nel Voynich non è netto.
- Il gibberish umano ha un eccesso simile o un po' maggiore (1,13), ma su un testo tre volte più piccolo il test è
  debole.

## 3/10/2026 (notte) — e374: i bordi della riga ci sono appena nel gibberish umano, fortissimi nel Voynich

Preregistrato (`preregistrazioni/e374.md`). Righe con almeno 3 parole. F1 = divergenza fra il primo segno della prima
parola e quello delle parole in mezzo; F2 = lo stesso per l'ultimo segno dell'ultima parola; L1, L2 = differenza di
lunghezza. Nullo: parole rimescolate dentro la riga.

| testo | righe | F1 | z | F2 | z | L1 | L2 | z a parità col gibberish (F1, F2) |
|---|---|---|---|---|---|---|---|---|
| Voynich | 4.045 | 0,140 | 367 | 0,057 | 211 | +0,49 | −0,07 | 172, 90 |
| gibberish umano | 1.505 | 0,006 | **3,2** | 0,006 | 2,0 | +0,59 | +0,51 | — |
| testi sensati | 3.972 | 0,027 | 13 | 0,026 | 11 | +1,21 | +0,63 | 6,7, 4,7 |
| Timm e Schinner, seme 1 | 3.973 | 0,039 | 152 | 0,099 | 410 | +0,23 | −0,44 | 62, 201 |

- **Esito preregistrato: i bordi della riga ci sono anche nel gibberish umano** (F1, z 3,2 > 3).
- **Ma la soglia era mal tarata**, perché guardava solo lo z e non la forza. A parità di righe il Voynich ha z 172
  contro 3,2, e la divergenza del primo segno è 24 volte quella del gibberish (0,140 contro 0,006). Nel gibberish
  l'effetto è appena percettibile; nel Voynich è una delle proprietà più forti del testo. Lo dichiaro come limite della
  preregistrazione, senza cambiare l'esito.
- Anche i testi sensati mostrano un po' di effetto (z 13), forse per le righe-versetto di alcuni testi. Comunque è molto
  sotto il Voynich a parità di righe (6,7 contro 172).
- Il generatore di Timm e Schinner ha bordi forti per costruzione: *p f k* all'inizio, *m g d* alla fine.
- **Lunghezza:** la prima parola della riga è più lunga in tutti i testi (+0,5–1,2 segni: a capo vanno le parole lunghe).
  L'ultima è un po' più corta solo nel Voynich e in Timm e Schinner; nel gibberish è più lunga (+0,51).
- Nota: dei 38 testi di gibberish, 1.397 righe su 1.505 vengono da file con la sigla "DC". Il confronto per autore è
  quindi poco informativo.
- Lettura: chi inventa parole a mano non marca da sé inizio e fine della riga con segni propri. Nel Voynich i segni di
  bordo (*p t s* all'inizio, *g m* alla fine) sono una regola del sistema, non un effetto del gesto di scrivere.

## 3/10/2026 (notte) — e376: l'inventiva è della sessione, non dello scriba

Preregistrato (`preregistrazioni/e376.md`). 48 bifogli; mani di Davis (la più frequente nel bifoglio): 1 = 26, 2 = 11,
3 = 8, 4 = 1, 5 = 2. Sovradispersione fra i bifogli della quota di forme nuove e, come controllo, di errori.

| parole | stratificazione | strati | bifogli | rapporto sul nullo | z |
|---|---|---|---|---|---|
| forme nuove | sezione × lingua | 6 | 46 | 3,97 | 11,9 |
| forme nuove | sezione × lingua × mano | 5 | 42 | **4,02** | **11,4** |
| forme nuove | solo mano | 4 | 47 | 4,61 | 15,3 |
| errori | sezione × lingua | 6 | 46 | 1,05 | 0,2 |
| errori | sezione × lingua × mano | 5 | 42 | 0,98 | −0,1 |
| errori | solo mano | 4 | 47 | 0,99 | 0,0 |

- **Esito preregistrato: l'inventiva è della sessione.** Dentro la stessa mano, sezione e lingua, i bifogli
  differiscono nelle forme nuove 4 volte il caso. La mano non spiega niente dell'eccesso (−2%).
- **Controllo superato:** gli errori restano uniformi in tutte le stratificazioni.
- Lettura: lo stesso scriba, in sessioni diverse, inventa forme nuove in quantità molto diverse. È una condizione della
  sessione (tempo, fretta, modello da cui copiava), non un'abitudine personale.

## 3/10/2026 (notte) — e377: la giuntura fra parole del Voynich è forte come in una lingua, quasi assente nel gibberish umano

Preregistrato (`preregistrazioni/e377.md`). I = informazione mutua (bit) fra l'ultimo segno di una parola e il primo
della seguente nella stessa riga; nullo con le parole rimescolate nella riga; E = I − nullo.

| testo | parole | E | z | E a parità col gibberish (z) |
|---|---|---|---|---|
| Voynich | 34.836 | **0,188** | 190 | 0,185 (77) |
| testi sensati: Historical | 34.483 | 0,090 | 33 | 0,066 (11) |
| testi sensati: Modern | 34.791 | 0,049 | 19 | 0,041 (7) |
| testi sensati: Conlangs | 29.866 | 0,042 | 18 | 0,040 (9) |
| gibberish umano | 10.017 | **0,014** | 3,7 | — |
| Timm e Schinner, seme 1 | 37.224 | 0,010 | 13 | 0,010 (5) |

- **Esito preregistrato: giuntura più debole nel gibberish umano** (z 3,7, ma E 13 volte sotto il Voynich).
- **Controllo esplorativo, non preregistrato** (scratchpad, 50 rimescolamenti, primi 10.000 parole di ogni testo). I
  gruppi di testi sensati mescolano lingue diverse, e la loro E è una media. Testo per testo:
  - sanscrito 0,46–0,47 e arabo del Corano 0,47 (lingue con il *sandhi* o con forti legami fonetici fra parole);
  - tagalog 0,20–0,25, slavo ecclesiastico 0,25, greco tecnico 0,20, klingon 0,19;
  - francese 0,15–0,17, inglese 0,10–0,15, italiano 0,07–0,11, spagnolo 0,09–0,10, tedesco 0,05–0,08;
  - latino 0,03–0,07.
  - Il Voynich su 10.000 parole: 0,18–0,20 (5 sottoinsiemi).
- **Lettura corretta:** la giuntura del Voynich sta dentro la gamma delle lingue vere, nella parte alta. È più forte
  che in latino, italiano e tedesco, simile a greco, klingon e francese, meno che in sanscrito e arabo. Il gibberish
  scritto a mano dai volontari e il generatore di Timm e Schinner ne hanno pochissima.
- **Insieme all'e375:** il Voynich ha una giuntura di segni forte come una lingua, ma quasi nessuna preferenza fra
  parole oltre la giuntura (le lingue sì, 13–38%). Il legame fra parole vicine sta tutto nei segni di confine, non
  nell'identità delle parole.

## 3/10/2026 (notte) — e379: lo spazio a volte spezza le parole (parolina + parola)

Preregistrato (`preregistrazioni/e379.md`). Coppie vicine (x, y) con x di al massimo 2 segni; "unione nel lessico" se
xy è una parola con almeno 2 occorrenze nella ZL. Nullo: y scambiata dentro la pagina con parole dello stesso primo e
ultimo segno e della stessa posizione (giuntura e lessico di pagina intatti).

| coppie | quante | quota con unione nel lessico | nullo | z |
|---|---|---|---|---|
| parolina, spazio sicuro | 2.412 | 0,275 | 0,239 | **6,9** |
| parolina, spazio incerto (virgola) | 1.073 | 0,562 | 0,500 | 5,9 |
| parola di 3+ segni, spazio sicuro | 25.770 | 0,015 | 0,014 | 2,0 |

- **Esito preregistrato (b): lo spazio a volte spezza le parole.** Dopo una parolina, la parola seguente è più spesso
  del caso proprio quella che, unita, dà una parola scritta altrove tutta attaccata:
  - *s aiin* → *saiin* (30 volte);
  - *or aiin* → *oraiin* (28);
  - *ar aiin* → *araiin* (16);
  - *ol chedy* → *olchedy* (16), *ol shedy* → *olshedy* (16);
  - *r aiin* → *raiin* (12), *ar al* → *aral* (12).
- Con le parole lunghe l'effetto non c'è (z 2,0).
- Con gli spazi incerti la quota è più alta (0,56), come ci si aspetta se la virgola segna proprio questi casi.
- **Parte (a), esito preregistrato: incerto.** Unendo le parti separate da virgola, la misura dell'e375 resta uguale
  (R 1,03, z 2,1): il piccolo eccesso dell'e375 non viene dagli spazi incerti.
- **Lettura:** nel Voynich lo spazio non è un confine di parola affidabile per gli elementi corti (*s*, *or*, *ol*,
  *ar*, *r*). Possono stare attaccati o staccati dalla parola seguente. Con l'e361–e363 (pezzi attaccati senza spazio)
  e l'e368 (*s* attaccata a inizio riga): lo spazio separa pezzi di una catena di segni più che parole fisse.

## 3/10/2026 — vz: e408, concordanza delle desinenze e scelte di riga: migliorano tutte e due, nessuna delle due passa la soglia

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e408.md`). Risultati in `risultati/e408_scelte_di_riga.md`.
Semi 1–4; riferimento U3 dell'e407 (v9): 0,541 / 0,659, pagella 16,5, estese 3,2.

| strato | regolazione | AUC e231 | AUC e266 | pagella | estese | concordanza per seme (Voynich 0,043 ± 0,012) | scelte di riga per seme (soglia 10 su 12) |
|---|---|---|---|---|---|---|---|
| U3 (v9) | converge | 0,541 | 0,659 | 16,5/18 | 3,2/8 | circa 0,12 | circa 3,5 |
| R1, peso proprio per il legame fra finali | scarto 13,7% (**non converge**) | 0,554 | 0,673 | **17,0/18** | 2,5/8 | 0,059, 0,063, 0,059, 0,056 | 4, 4, 2, 3 |
| R2, + scelte di riga | scarto 12,9% (**non converge**) | 0,582 | 0,671 | 16,0/18 | 2,8/8 | 0,057, 0,060, 0,058, 0,058 | 8, 11, 10, 8 |

- **Esito preregistrato: nessuno dei due pezzi è "preso"** (serviva la materia in almeno 3 semi su 4).
  - **Concordanza delle desinenze:** scende da 0,12 a 0,058, ma resta appena fuori dalla fascia (≤ 0,055) in tutti i
    semi. Il peso del legame fra finali va quasi a zero (0,05–0,07): **nel Voynich i finali di parole vicine si legano
    molto meno di quanto il modello facesse**, e la concordanza che resta nel testo generato viene da altri termini
    (ultimo segno → primo segno, unioni) o dal sacco. È il valore che tiene la regolazione sopra il 10%.
  - **Scelte di riga:** il termine di riga porta le classi concordi da 3,5 a 9,25 su 12 (8, 11, 10, 8): due semi su
    quattro passano. L'eccesso medio di accordo è quello del Voynich (0,0227 contro 0,0231), quindi **la concordanza
    del Voynich non è distribuita fra le 12 classi come la fa un peso unico**: alcune classi restano sotto z 3. Il
    termine costa la materia "gradiente" in 4 semi su 4 (alza la somiglianza dentro la riga) e 0,03 sul giudice
    dell'e231.
- **Pagella 17/18 con R1**, il valore più alto del generatore a pezzi (manca solo il profilo pagina fra le 18).
- **Coppie viste altrove** resta alta (0,249 contro 0,221) con il peso della coppia esatta già a zero: i legami di
  forma producono da soli troppe coppie ripetute.
- **Cancello della riga:** perso in tutti i semi. Valori (R1): S1 1,08 (soglia ≤ 0,7), A 0,98 (≥ 1,0), scelte per riga
  1,0 (≥ 3), r fra righe consecutive 0,11 (0,207 ± 0,07); R_riga a posto.
- **Che cosa si tiene:** R1 come corpo della versione seguente (pagella più alta, giudici entro 0,03 da U3), dichiarando
  che la concordanza delle desinenze non è in fascia. R2 no (costa il gradiente; due semi su quattro). Lacuna
  dichiarata per le scelte di riga con questo termine: un secondo tentativo dovrà avere un peso per classe.

## 3/10/2026 — vz: e409, il messaggio nel sacco: funziona, e batte il nascondiglio vecchio (0,560 / 0,697 contro 0,677 / 0,737)

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e409.md`). `voynichizzatore/canale_sacco.py`: il testo
cifrato sceglie, pagina per pagina, quante volte compare ogni parola nota (catena di binomiali, codifica aritmetica di
v1); pagina tipo, posti e forme delle parole nuove e disposizione vengono dalla chiave; le scelte di grafia non si
riscrivono più. Corpo di partenza: v9. Isidoro XVII, quattro chiavi. Risultati in
`risultati/e409_messaggio_nel_sacco.md`.

- **Andata e ritorno esatta 4 su 4; chiave sbagliata respinta 4 su 4.**
- **Capacità:** 80.300 bit per libro (servono 38.240; il messaggio occupa 131 pagine su 207). Previsione 100.000–
  250.000: **più bassa del previsto**, ma doppia del necessario e quasi doppia di quella del nascondiglio vecchio
  (38.000–46.000).

| caso | AUC e231 (per chiave) | AUC e266 (per chiave) | pagella | estese | materie perse rispetto ad (a) |
|---|---|---|---|---|---|
| (a) messaggio nel sacco | **0,560** (0,578, 0,559, 0,551, 0,552) | **0,697** (0,730, 0,702, 0,684, 0,671) | 16,2/18 | 4,0/8 | |
| (b) stesso canale, soli bit di riempimento | 0,523 (0,478, 0,527, 0,528, 0,560) | 0,655 (0,606, 0,654, 0,657, 0,704) | 16,0/18 | 3,8/8 | |
| (c) nascondiglio vecchio sul corpo v9 | 0,677 (0,658, 0,696, 0,671, 0,680) | 0,737 (0,740, 0,729, 0,725, 0,755) | 15,0/18 | 3,8/8 | legame (4 su 4) |

- **Il nuovo nascondiglio batte il vecchio** di 0,117 sul giudice dell'e231 e di 0,040 su quello dell'e266, con 1,2
  punti di pagella in più. Come ipotizzato al banco della v9, il nascondiglio vecchio fa perdere la materia "legame"
  in 4 casi su 4 e alza G2 (coppie di segni) a 0,64: riscrive il primo e l'ultimo segno delle parole.
- **(a) contro (b): previsione NON rispettata.** La differenza delle medie è 0,037 / 0,042, oltre lo 0,02 previsto.
  Per costruzione i bit del messaggio cifrato e quelli di riempimento hanno la stessa distribuzione; con quattro
  chiavi (b) va da 0,478 a 0,560, quindi può essere rumore, ma non lo do per scontato: integrazione e409b con altre
  8 chiavi (in corso). Fino ad allora il canale non si dichiara "indistinguibile per costruzione".
- **(a) contro il corpo senza messaggio** (v9 sui semi 1–4: 0,541 / 0,659): +0,019 / +0,038; la soglia di allarme
  (0,03) è superata di poco sul giudice forte: stessa verifica dell'e409b.
- Senza la ripetizione θ i valori di pagina restano a posto: tipi su parole 0,758 (Voynich 0,756); JSD
  pagina-manoscritto 0,0445 (0,0402: alta dell'11%, come già nella v9 per le parole nuove fatte di unioni).
- **Cancello della riga:** perso in tutti i casi. Con il nascondiglio vecchio le scelte per riga sono 5 e r fra righe
  consecutive 0,17 (il modello delle scelte ha la memoria di riga); con il nuovo 0,75 e 0,09: il corpo a pezzi non
  ha ancora le cinque scelte concordi nella riga. È il prossimo pezzo.

## 3/10/2026 (notte) — Errore: nei testi sensati di Gaskell e Bowern alcune parole erano spezzate

Trovato da me dopo l'e377. La regola usata per estrarre le parole dai testi di Gaskell e Bowern (`[^\W\d_]+`, in
e346, e374, e375, e377) tratta i segni diacritici combinanti come separatori. Contando le parole sulle prime 3.000
righe (scratchpad):
- **Corano** (arabo vocalizzato) ×3,59, **Mahabharata** ×3,51 e **Charaka Samhita** (sanscrito in devanagari) ×3,78:
  le "parole" sono pezzi di parola.
- **Klingon** (2 testi) e **lojban** (2 testi) ×1,18–1,23, perché l'apostrofo, che lì è una lettera, spezza la parola.
- Gli altri testi non sono toccati.

Conseguenze:
- **I numeri del Voynich, del gibberish e di Timm e Schinner non cambiano.**
- **e377, controllo per testo:** i valori di sanscrito e Corano (0,46–0,47) sono un artefatto, perché misurano
  passaggi dentro la parola. Il massimo fra i testi validi è circa 0,25 (tagalog, slavo ecclesiastico), poi maya
  yucateco 0,22, greco tecnico 0,20. La conclusione resta ("il Voynich, 0,19, sta nella parte alta della gamma delle
  lingue"), ma il paragone con sanscrito e arabo va tolto. Il valore del gruppo Historical (0,090) è gonfiato.
- **e375:** il controllo positivo regge anche col solo gruppo Modern, che non ha testi spezzati (R 1,30, z 26). I
  valori di Historical e Conlangs sono da rifare.
- **e374:** i valori dei testi sensati sono da rifare; il confronto Voynich–gibberish non cambia.
- **e346** (ancora in esecuzione): il gruppo dei testi sensati contiene i 6 testi spezzati; se ne terrà conto
  nella lettura.
- **Correzione:** l'e381 rifà le misure dei testi sensati di e374, e375 ed e377 con le parole intere: spazi come
  separatori, tenendo lettere, segni combinanti e apostrofi.

## 3/10/2026 (notte) — e378: la lingua B non è la lingua A con un'altra chiave

Preregistrato (`preregistrazioni/e378.md`). Solo l'erbario: B 3.462 parole; A diviso 10 volte in due parti di pari
dimensione. Sovrapposizione delle frequenze delle parole; ricerca della sostituzione dei segni migliore (ricerca locale,
6 partenze). Ricerca provata prima solo su un testo latino di controllo.

| | media su 10 divisioni |
|---|---|
| O(A1, A2), stessa lingua | 0,586 |
| O(A1, B) | 0,311 |
| O(chiave migliore(A1), B) | 0,313 |
| quota del divario chiusa dalla chiave, R | **0,01** |
| controllo: A2 cifrata a caso, R | **1,00** |

- **Esito preregistrato: B non è una sostituzione di A.** La ricerca ritrova sempre una chiave casuale (controllo
  1,00 in tutte le 10 divisioni), ma fra A e B la chiave migliore è quasi l'identità. Gli unici scambi riguardano segni
  rari (*p*↔*f* in 10 divisioni su 10, poi *cph*, *cfh*, *x*, *c*) e guadagnano lo 0,2%.
- Le parole B sono più lunghe (4,37 segni contro 4,04), cosa che una sostituzione non può fare.
- Lettura: A e B usano i segni con lo stesso valore. La differenza sta nel lessico e nella forma delle parole (famiglie
  -*edy*, *qok*-, e315–e325), non in una chiave diversa.

## 3/10/2026 (notte) — e346: la ripresa del Voynich sta fra il gibberish umano e i testi sensati, ma il confronto con i testi sensati è falsato

Preregistrato (`preregistrazioni/e346.md`). Prima esecuzione fermata perché troppo lenta, codice reso più veloce e
rilanciato (voce precedente). Ripresa dalle 2 righe sopra (parole di almeno 3 segni, uguali o a una modifica); nullo
con le righe dell'unità in ordine casuale; E = quota − nullo, R = quota / nullo.

| testo | unità | parole | E | R | IC 95% di E |
|---|---|---|---|---|---|
| Voynich (pagine) | 167 | 26.080 | **+0,034** | 1,09 | +0,029 – +0,039 |
| gibberish umano (documenti) | 38 | 7.965 | +0,007 | 1,08 | −0,006 – +0,019 |
| testi sensati (documenti) | 71 | 4.016.539 | +0,060 | 1,73 | +0,051 – +0,069 |
| Timm e Schinner, seme 1 | 138 | 28.677 | +0,022 | 1,05 | +0,017 – +0,028 |
| Timm e Schinner, seme 19 | 138 | 29.198 | +0,022 | 1,05 | +0,018 – +0,027 |

Per categoria: Historical +0,054, Modern +0,068, Conlangs +0,073. Per autore del gibberish: DA (2 testi) −0,011,
DC (36 testi) +0,008.

- **Esito preregistrato: fuori da tutti e due (in mezzo):** sopra l'intervallo del gibberish e sotto quello dei testi
  sensati.
- **Il confronto con i testi sensati è falsato dal disegno, e lo dichiaro.** Per loro l'unità era il documento intero:
  fino a 69.000 righe, contro le 25 circa di una pagina del Voynich. Rimescolare le righe di un libro intero porta via
  la continuità locale (le righe vicine parlano della stessa cosa), che nel Voynich resta dentro il nullo della pagina.
  Così l'E dei testi sensati è gonfiato. In più il gruppo contiene i 6 testi con le parole spezzate (voce
  sull'errore).
- **Gibberish:** in eccesso il Voynich riprende 5 volte di più (0,034 contro 0,007, e il gibberish non è
  significativo). In rapporto sono uguali (1,09 contro 1,08): il Voynich ha molte più parole simili fra loro di base.
  Con 38 testi il gibberish è un campione piccolo.
- **Correzione:** l'e382 rifà il confronto con unità uguali (pagine di 25 righe) e con le parole intere.

## 3/10/2026 (notte) — e381: con le parole intere i controlli reggono; la giuntura del Voynich è fra le più alte (6 lingue su 71 sopra)

Preregistrato (`preregistrazioni/e381.md`). Correzione dell'errore delle parole spezzate: le misure dei testi sensati di
e374, e375 ed e377 rifatte con le parole intere (spazi come separatori; lettere, segni combinanti e apostrofi tenuti;
segno = lettera + segni combinanti).

- **e374 (bordi della riga), testi sensati:** F1 0,021 (z 6,8), F2 0,023 (z 5,5), contro 0,027 e 0,026 di prima.
  **Esito invariato:** dipendeva solo dal gibberish, e il Voynich (0,140) resta molto sopra.
- **e375 (coppie oltre la giuntura):** R 1,38 / 1,29 / 1,16 (z 28 / 26 / 15) per Historical / Modern / Conlangs, contro
  1,38 / 1,30 / 1,13 di prima. **Controllo positivo confermato**; il Voynich (1,03) resta molto sotto.
- **e377 (giuntura), gruppi:** E 0,058 / 0,048 / 0,042 (prima 0,090 / 0,049 / 0,042). Il gruppo Historical era
  gonfiato dai testi spezzati. **Esito invariato.**
- **e377, per testo (prime 10.000 parole):** il Voynich vale 0,175–0,186 (mediana 0,182). Solo **6 testi su 71** hanno
  una giuntura più forte:
  - arabo del Corano (vocalizzato) 0,36;
  - sanscrito 0,24 (Mahabharata) e 0,21 (Charaka Samhita);
  - tagalog 0,21 (due testi);
  - greco tecnico 0,21.
  - Seguono cinese in pinyin 0,16, inglese tecnico 0,15, poi italiano 0,06–0,12, francese 0,11, inglese 0,10,
    spagnolo 0,07–0,10, tedesco 0,04–0,08, latino 0,03–0,06, fiammingo 0,03–0,04.
- **Lettura:** la giuntura del Voynich è fra le più forti, al livello delle lingue in cui la fine di una parola e
  l'inizio della seguente sono legati dalla fonetica o dalla grammatica. Fra queste c'è il sanscrito, con il *sandhi*
  scritto. È molto più forte che nelle lingue europee del Quattrocento (latino, italiano, tedesco), e 13 volte quella
  del gibberish umano. Questo non dice che lingua sia: dice solo che il confine fra parole nel Voynich è legato quanto
  nelle lingue più legate.

## 3/10/2026 (notte) — e382: a parità di unità, il gibberish umano non riprende dalle righe sopra; il Voynich sì, quanto o più dei testi sensati

Preregistrato (`preregistrazioni/e382.md`). Correzione dell'e346: stessa misura, ma pagine di 25 righe per testi
sensati (prime 500 righe, parole intere) e gibberish; pagine vere per il Voynich; pagine di 29 righe per Timm e
Schinner.

| testo | pagine | parole | E | IC 95% | R | IC 95% |
|---|---|---|---|---|---|---|
| Voynich | 167 | 26.080 | **+0,034** | +0,028 – +0,039 | **1,09** | 1,08 – 1,11 |
| gibberish umano | 67 | 7.270 | **−0,001** | −0,009 – +0,007 | **0,99** | 0,90 – 1,07 |
| testi sensati | 1.237 | 156.859 | +0,029 | +0,027 – +0,032 | 1,20 | 1,19 – 1,22 |
| — Historical | 530 | 68.215 | +0,028 | | 1,19 | |
| — Modern | 480 | 61.094 | +0,027 | | 1,20 | |
| — Conlangs | 227 | 27.550 | +0,038 | | 1,23 | |
| Timm e Schinner, seme 1 | 138 | 28.677 | +0,022 | +0,017 – +0,028 | 1,05 | 1,04 – 1,06 |

- **Esito preregistrato su E: più di tutti** (appena sopra i testi sensati: 0,034 contro un intervallo che arriva a
  0,032).
- **Esito su R: fuori da tutti e due** (1,09, fra il gibberish 0,99 e i testi sensati 1,20).
- **Il gibberish scritto a mano non riprende affatto dalle righe sopra.** Chi inventa parole non tende a ripetere o
  variare quelle appena scritte.
- **I testi sensati riprendono** per la continuità del discorso (le righe vicine parlano della stessa cosa).
- **Il Voynich:** in eccesso assoluto è al livello dei testi sensati o poco sopra, in proporzione sotto (ha molte più
  parole simili di base).
- **L'e346 era falsato:** con il libro intero come unità i testi sensati sembravano riprendere il doppio (0,060).
- Da verificare (e385): se la ripresa del Voynich ha la stessa forma di quella delle lingue. Nel Voynich si ferma dopo
  1–2 righe (e347); se nelle lingue cala piano, il meccanismo è diverso: copia contro argomento.

## 3/10/2026 — vz: e409b, messaggio e riempimento su 12 chiavi: indistinguibili fra loro (differenza 0,013 / 0,011); nasce la v10



Integrazione preregistrata dell'e409 (altre 8 chiavi, 5–12, per i casi (a) e (b); `CHIAVI=5,...,12 CASI=a,b`). Risultati in `risultati/e409b_messaggio_nel_sacco_chiavi_5_12.md`.



| 12 chiavi | AUC e231 (media, deviazione) | AUC e266 (media, deviazione) | pagella |

|---|---|---|---|

| (a) messaggio nel sacco | 0,560 (0,023) | 0,682 (0,026) | 16,5/18 |

| (b) soli bit di riempimento | 0,547 (0,026) | 0,671 (0,032) | 16,3/18 |

| differenza (errore standard) | +0,013 (0,010) | +0,011 (0,012) | |



- **La previsione dell'integrazione è rispettata:** sulle 12 chiavi la differenza è entro 0,02 su entrambi i giudici ed entro circa un errore standard. La differenza di 0,04 vista con quattro chiavi era rumore fra chiavi (l'AUC di una chiave varia di circa 0,025). Andata e ritorno esatta 12 su 12, chiave sbagliata respinta 12 su 12.

- **Il manoscritto con il messaggio non è più riconoscibile di quello senza**, come deve essere per costruzione: il testo cifrato fa da dado al modello.

- **Nasce la v10:** corpo R1 dell'e408 (`pezzi_parametri_v10.json`) con il messaggio nel sacco (`canale_sacco.py`). Nel registro `versioni.py` ogni versione ha ora `codifica` / `decodifica` proprie; lo strumento `voynichizzatore.py` usa la v10 come predefinita. Prova dallo strumento: Isidoro con la chiave "giardino", salvato su file e riletto: identico.

- Banco e293 della v10 in corso (chiavi "banco7", "banco8", "banco9": con questo nascondiglio il corpo dipende da messaggio e chiave, e il seme d'esame entra nella chiave; deviazione dichiarata).

## 3/10/2026 (notte) — e383: la giuntura sta fra parole vere, non solo nelle parole spezzate

Preregistrato (`preregistrazioni/e383.md`). Eccesso della giuntura (e377) in tre versioni: (1) tutte le coppie; (2)
senza le coppie la cui unione è una parola del testo; (3) solo coppie di parole di almeno 3 segni.

| testo | E1 | E2 | E3 | q2 = E2/E1 | q3 = E3/E1 |
|---|---|---|---|---|---|
| Voynich | 0,188 | 0,154 | 0,155 | 0,82 | **0,83** |
| gibberish umano | 0,013 | 0,013 | 0,013 | 1,01 | 1,02 |
| testi sensati (71, min / mediana / max) | | | | 0,79 / 1,00 / 1,04 | 0,26 / 0,86 / 1,78 |

- **Esito preregistrato: la giuntura sta fra parole vere** (q3 0,83 > 0,8).
- Togliere le coppie che unite fanno una parola porta via il 18% della giuntura del Voynich, più che in quasi tutte le
  lingue (mediana 0%, minimo 21%): le parole spezzate (e379) ne spiegano una parte, non il grosso.
- Fra parole lunghe la giuntura del Voynich (0,155) è superata da 10 testi su 71.

## 3/10/2026 (notte) — e384: la giuntura non passa a capo; il Voynich si comporta come i testi in cui la riga è un versetto

Preregistrato (`preregistrazioni/e384.md`). Giuntura fra l'ultima parola di una riga e la prima della riga sotto (stesso
paragrafo), con un nullo dello stesso tipo di quello dentro la riga; Q = E a capo / E nella riga.

| testo | coppie a capo | E a capo | z | E nella riga | z | Q |
|---|---|---|---|---|---|---|
| Voynich | 3.390 | **−0,003** | **−0,7** | 0,191 | 238 | **−0,02** |
| gibberish umano | 1.531 | 0,006 | 0,4 | 0,014 | 3,6 | 0,46 |
| testi sensati, tutti i 71 (min / mediana / max) | | | | | | −0,40 / 0,54 / 2,56 |
| testi sensati con almeno 1.000 coppie a capo (39) | | | | | | −0,10 / 0,53 / 1,06 |

- **Esito preregistrato: "passa a capo come nella prosa"**, perché Q del Voynich sta fra il minimo e il massimo dei
  testi sensati.
- **Il criterio era mal scelto e lo dichiaro.** Minimo e massimo vengono da testi piccoli e rumorosi (il minimo, −0,40,
  è un testo con 161 coppie). Inoltre l'intervallo include testi in cui la riga non è un a capo arbitrario.
- **Descrizione:** nel Voynich la giuntura a capo è zero (z −0,7 su 3.390 coppie), mentre nella riga è fra le più
  forti. Fra i 39 testi grandi, Q vicino a zero lo hanno solo 5 testi:
  - Corano (−0,10), Avicenna arabo (0,04), Vulgata latina abbreviata (0,03), Nuovo Testamento ebraico (−0,02),
    klingon (0,10);
  - sono testi in cui la riga corrisponde a un versetto o a una frase.
  - Nella prosa che va a capo dove capita Q sta intorno a 0,5–1.
- **Lettura:** la riga del Voynich non è un a capo arbitrario. Si comporta come un'unità chiusa, un versetto o una
  voce: la giuntura lega le parole dentro la riga e si interrompe alla fine. Va con i segni di bordo della riga (e366,
  e374), con *s* attaccata all'inizio (e368) e con la prima parola della riga più lunga (e374).

## 3/10/2026 (notte) — e380: qo-/o- e -l/-r dipendono dalla parola vicina, come una regola di raccordo

Preregistrato (`preregistrazioni/e380.md`, con il limite della misura dichiarato prima di eseguire). Informazione
mutua fra il segno di bordo e il segno della parola vicina, a parità del resto della parola (tronco o corpo), della
posizione e dello strato. Si tolgono le coppie copiate dalle 2 righe sopra.

**Parte 1** (E in bit oltre il nullo):

| testo | E destra | z | E sinistra | z |
|---|---|---|---|---|
| Voynich | 0,029 | 16,4 | 0,033 | 15,0 |
| gibberish umano | 0,021 | 9,2 | 0,027 | 10,1 |
| Timm e Schinner, seme 1 | 0,005 | 3,0 | 0,009 | 5,2 |
| sanscrito (controllo positivo), z a destra | | 13,1 e 8,5 | | |

- **Esito preregistrato:** a destra "il segno finale porta da solo un legame con la parola dopo, nella gamma delle
  lingue" (40 testi su 71 hanno E maggiore); a sinistra lo stesso per il primo segno (29 su 71). Come dichiarato prima,
  questa parte non isola il *sandhi*: anche nelle lingue europee parole con lo stesso tronco hanno vicine diverse.

**Parte 2** (scelte di grafia ai bordi):

| scelta | eventi | E | z |
|---|---|---|---|
| -*l*/-*r* finale, secondo la parola dopo | 9.458 | 0,044 | **12,7** |
| -*dy*/-*ey*, secondo la parola dopo | 8.958 | 0,007 | 2,6 |
| *qo*-/*o*- davanti a gallows, secondo la parola prima | 8.101 | 0,063 | **19,4** |
| *ch*-/*sh*- iniziale, secondo la parola prima | 8.285 | −0,004 | −1,2 |

- **Esito preregistrato: legate al vicino -*l*/-*r* e *qo*-/*o*-.**
- **Descrittivo, non preregistrato** (scratchpad):
  - **qo-/o- dopo:** -*y* 64% *qo* (4.661), -*o* 63%, -*d* 59%; -*l* 39%; -*n* 26%, -*m* 27%, -*r* 23%, -*s* 23%.
  - **-l/-r davanti a:** *a*- 15% -*l* (963); *o*- 43%; *y*- 37%; *ch*-/*sh*- 50–52%; *q*- 63%, *s*- 68%, *d*- 75%,
    *l*- 78%, *t*- 81%, *k*- 86%.
- **Lettura:** due classi di segni di confine. Dopo -*y*, -*o*, -*d* la parola seguente prende *qo*-; dopo -*n*, -*r*,
  -*s*, -*m* prende *o*-. Davanti ad *a*-, *o*-, *y*- la parola finisce in -*r*; davanti a *k*-, *t*-, *d*-, *l*-,
  *s*-, *q*- finisce in -*l*. È la forma di una regola di raccordo fra parole, come *a*/*an* in inglese o la liaison
  francese. Questo non dice quale suono abbiano i segni. Una parte di "-*r* *a*-" sono parole spezzate (*or aiin*,
  e379).
- Per il voynichizzatore: *qo*-/*o*- e -*l*/-*r* vanno scelti guardando la parola vicina, non solo la posizione.

## 3/10/2026 (notte) — e385: la ripresa del Voynich è copia dalla riga subito sopra, non continuità del discorso

Preregistrato (`preregistrazioni/e385.md`). Eccesso di parole (3+ segni) con una parola uguale o a una modifica nella
riga a distanza L, contro l'atteso esatto su tutte le altre righe dell'unità. C = media(e3..e6) / e1.

| testo | unità | e1 | e2 | e3 | e4 | e5 | e6 | C (IC 95%) |
|---|---|---|---|---|---|---|---|---|
| Voynich (paragrafi) | 740 | **+0,032** | +0,007 | +0,000 | −0,004 | −0,000 | −0,005 | **−0,07** (−0,27 – 0,10) |
| gibberish umano | 85 | +0,001 | +0,004 | +0,002 | +0,005 | +0,000 | +0,000 | 1,89 (0,87 – 2,57) |
| testi sensati | 1.243 | +0,017 | +0,019 | +0,012 | +0,008 | −0,000 | −0,000 | **0,28** (0,22 – 0,36) |

- **Esito preregistrato: il Voynich cala più in fretta delle lingue (copia a corto raggio).**
- Nelle lingue la ripresa è spalmata su 3–4 righe, con il massimo a distanza 2: è la continuità del discorso.
- Nel Voynich sta quasi tutta nella riga subito sopra, con un'eccedenza doppia di quella delle lingue (0,032 contro
  0,017), poco nella seconda e niente dopo. È copia di quanto appena scritto, non argomento.
- Il gibberish umano non ha ripresa a nessuna distanza.

## 3/10/2026 (notte) — e386: la giuntura si rompe anche al salto del disegno: vale solo fra segni scritti di seguito

Preregistrato (`preregistrazioni/e386.md`). Giuntura per tipo di separatore nella riga; nullo nello strato.

| coppie | quante | E | z |
|---|---|---|---|
| salto del disegno (`<->`) | 740 | **0,026** | **1,9** |
| spazio normale | 27.442 | 0,165 | 192 |
| spazio incerto (virgola) | 2.436 | 0,507 | 82 |
| a capo (stesso paragrafo) | 3.337 | −0,002 | −0,6 |

A parità di coppie (740): spazio normale 0,167, a capo −0,005; Q_salto = 0,16.

- **Esito preregistrato: si rompe anche al disegno.** Dove la riga salta un disegno, il legame fra la fine di una
  parola e l'inizio della seguente quasi sparisce, come all'a capo. Agli spazi incerti è tre volte più forte che agli
  spazi normali, come ci si aspetta se spesso sono dentro una parola.
- **Descrittivo, non preregistrato** (scratchpad): le parole dopo il salto iniziano spesso con *s* (9,5%), *d* (17%) e
  *y* (15%), come le prime parole della riga (10%, 16%, 15%) e non come quelle in mezzo (2%, 8%, 3%). Quasi mai con *q*
  (3% contro 17% in mezzo). Le gallows *p*/*t* di inizio riga non ci sono. Le parole prima del salto finiscono quasi
  come quelle in mezzo (-*m* 2,4% contro 0,9% in mezzo e 15% a fine riga). Il salto fa quindi in parte da inizio di un
  nuovo pezzo di riga.
- **Lettura:** in una lingua scritta intorno a un disegno la grammatica continuerebbe oltre il salto. Nel Voynich il
  legame vale solo fra segni scritti uno di seguito all'altro: è una proprietà della scrittura continua (o del pezzo di
  riga scritto di fila), non della sequenza del testo. Con l'e384: ogni tratto scritto senza interruzioni riparte da
  capo.

## 3/10/2026 — vz: e293, banco della v10: 0,550 / 0,662 con Isidoro nascosto, pagella 50/54: meglio della v5 su tutto



Banco preregistrato dell'e293 (`esegui.py e293 -- --v10`): Isidoro XVII nascosto con il messaggio nel sacco, chiavi "banco7", "banco8", "banco9" (con questo nascondiglio il seme d'esame entra nella chiave; deviazione dichiarata nella preregistrazione dell'e409). **Decodifica esatta nei tre manoscritti.**



| versione | nascondiglio | pagella (3 semi) | pagella estesa | riga | AUC e231 | AUC e266 |

|---|---|---|---|---|---|---|

| v5 (copia e modifica) | scelte di grafia | 49/54 | 57/78 | 0 | 0,816 | 0,917 |

| v8 (a pezzi) | scelte di grafia | 41/54 | 56/78 | 0 | 0,604 | 0,715 |

| v9 | scelte di grafia | 44/54 | 56/78 | 0 | 0,668 | 0,719 |

| **v10** | **nel sacco** | **50/54** | **63/78** | 0 | **0,550** | **0,662** |



- Per chiave (e231 / e266, pagella): banco7 0,553 / 0,661, 17; banco8 0,548 / 0,653, 16; banco9 0,550 / 0,672, 17.

- **Esito con il criterio dell'e293:** l'AUC dell'e266 scende di 0,255 rispetto alla v5 con pagella estesa superiore (63 contro 57): **la v10 migliora la v5**, ed è la prima versione che la supera su tutte le colonne.

- I numeri al banco coincidono con quelli dei semi di ricerca (corpo R1 senza messaggio: 0,554 / 0,673; messaggio nel sacco su 12 chiavi: 0,560 / 0,682): il messaggio non costa niente e non c'è effetto vincitore.

- Restano: il cancello della riga (perso in tutte le chiavi), il giudice forte a 0,66 contro l'obiettivo 0,6, e le materie aggiunte mancate (prime righe come registro, scelte di riga, concordanza delle desinenze, coppie viste altrove, a seconda della chiave).

## 3/10/2026 (notte) — Esplorativo: senza una parola accanto, *o*- e -*l* (una "forma di pausa"?)

Non preregistrato: conteggi fatti dopo l'e380 e l'e386 (scratchpad), da prendere come ipotesi. Quota di *qo*- fra le
parole *qo*-/*o*- davanti a gallows, e di -*l* fra le parole in -*l*/-*r*, per posto nella riga e strato:

| strato | *qo*- dopo il salto del disegno | *qo*- in mezzo | *qo*- a inizio riga | -*l* prima del salto | -*l* in mezzo | -*l* a fine riga |
|---|---|---|---|---|---|---|
| erbario A | **0,07** (74) | 0,44 (949) | 0,57 (268) | **0,63** (93) | 0,50 (2.099) | 0,51 (212) |
| erbario B | **0,19** (54) | 0,37 (724) | 0,58 (38) | **0,71** (31) | 0,33 (722) | 0,47 (45) |

- Dopo il salto del disegno, dove manca la parola prima (la giuntura si rompe, e386), si sceglie quasi sempre *o*-.
  Prima del salto, dove manca la parola dopo, più spesso -*l*.
- Sembra una **forma di pausa**: senza vicino, *o*- all'inizio e -*l* alla fine. Con un vicino la scelta segue la
  regola di raccordo dell'e380.
- A inizio riga invece *qo*- è frequente (57–87%): la riga ha regole sue (e374), diverse dal salto.
- Numeri piccoli (31–93 parole). **Previsione per un controllo su dati non ancora guardati (e387):** nelle etichette,
  parole isolate senza vicini, *qo*- davanti a gallows dovrebbe essere più raro e -*l* più frequente che in mezzo alle
  righe.

## 3/10/2026 (notte) — e387: nelle etichette qo- quasi non c'è: senza parola prima si scrive o-

Preregistrato (`preregistrazioni/e387.md`), con previsioni fatte dai conteggi esplorativi sul salto del disegno, prima
di guardare le etichette. Etichette (loci di tipo L) contro parole in mezzo alla riga, a parità di strato.

| strato | *qo*- nelle etichette | *qo*- in mezzo alla riga | -*l* nelle etichette | -*l* in mezzo alla riga |
|---|---|---|---|---|
| astronomia (senza lingua) | 0,02 (51) | 0,39 (28) | 0,38 (52) | 0,38 (37) |
| biologia B | 0,05 (56) | 0,68 (1.470) | 0,71 (45) | 0,66 (996) |
| cosmologia (senza lingua) | 0,00 (15) | 0,30 (23) | 0,36 (22) | 0,71 (62) |
| cosmologia B | 0,01 (80) | 0,58 (81) | 0,38 (34) | 0,37 (68) |
| farmacia A | 0,00 (92) | 0,46 (403) | 0,48 (65) | 0,63 (642) |

- **qo-: previsione confermata.** Differenza pesata −0,50, p < 0,0001. Nelle etichette, parole senza vicini, *qo*-
  davanti a gallows quasi non esiste (0–5%), mentre nelle righe sta fra il 30% e il 68%.
- **-l: non decisa** (−0,06, p 0,94 nella direzione prevista). La parte della "forma di pausa" sulla fine della
  parola non regge.
- **Lettura:** con il salto del disegno (7–19%) e con la regola dell'e380 (*qo*- dopo -*y*, -*o*, -*d*), il quadro è
  coerente. *o*- è la forma di base; *qo*- compare solo quando la parola segue, scritta di seguito, una parola con
  certe finali. Le etichette non hanno una parola prima, e quindi hanno *o*-.
- Cautela: le etichette potrebbero anche essere un lessico a parte (nomi). Ma il salto del disegno, dentro il testo
  corrente, dà lo stesso effetto.
- A inizio riga invece *qo*- è frequente (57–87%): lì vale un'altra regola (e374), ancora da capire.

## 3/10/2026 (notte) — e388: la regola di raccordo è la stessa per tutti gli scribi

Preregistrato (`preregistrazioni/e388.md`). Classi prese dai conteggi descrittivi dell'e380 (stessi dati); domanda nuova:
la regola vale per ogni mano di Davis? Δ_qo = P(*qo* | parola prima in -*y*/-*o*/-*d*) − P(*qo* | in -*n*/-*r*/-*s*/-*m*);
Δ_l = P(-*l* | parola dopo in *k*/*t*/*d*/*l*/*s*/*q*) − P(-*l* | parola dopo in *a*). Bootstrap sulle pagine.

| regola | mano (strati principali) | eventi | Δ | IC 95% |
|---|---|---|---|---|
| *qo*-/*o*- | 1 (erbario A, farmacia A) | 653 / 499 | +0,25 | +0,19 – +0,30 |
| *qo*-/*o*- | 2 (biologia B, erbario B) | 1.895 / 550 | +0,48 | +0,42 – +0,54 |
| *qo*-/*o*- | 3 (ricette B) | 1.984 / 1.084 | +0,38 | +0,34 – +0,42 |
| -*l*/-*r* | 1 | 816 / 50 | +0,47 | +0,34 – +0,58 |
| -*l*/-*r* | 2 | 501 / 214 | +0,64 | +0,57 – +0,72 |
| -*l*/-*r* | 3 | 639 / 375 | +0,57 | +0,52 – +0,61 |

Le mani 4 e 5 hanno troppi pochi eventi.

- **Esito preregistrato: regola condivisa da tutte le mani.** I tre scribi con abbastanza testo, in lingua A e in
  lingua B, seguono le stesse due regole di raccordo. È una regola del sistema di scrittura, non un'abitudine di mano.
- In lingua A (mano 1) la regola di *qo*- è più debole (+0,25 contro +0,38/+0,48).

## 3/10/2026 (notte) — e389: a fine riga -m prende il posto di -r; a inizio riga y- e s- prendono il posto di ch- e k-

Preregistrato (`preregistrazioni/e389.md`). A parità del resto della parola (tronco o corpo) e dello strato, quanto ogni
ultimo segno (fine riga) o primo segno (inizio riga, righe non d'inizio paragrafo) è più frequente al bordo che in
mezzo; nullo con le etichette bordo/mezzo rimescolate nel gruppo.

**Fine riga** (489 gruppi, 2.030 parole al bordo):

| segno | Δ | z |
|---|---|---|
| -*m* | **+0,151** | 26,7 |
| -*g* | +0,014 | 9,0 |
| -*y* | +0,019 | 3,4 |
| -*d* | +0,007 | 3,1 |
| -*o* | −0,020 | −5,1 |
| -*l* | −0,052 | −6,2 |
| -*r* | **−0,121** | −13,6 |

**Inizio riga** (410 gruppi, 2.017 parole al bordo):

| segno | Δ | z |
|---|---|---|
| *y*- | **+0,092** | 16,6 |
| *s*- | **+0,098** | 16,0 |
| *d*- | +0,040 | 4,8 |
| *t*- | +0,022 | 3,9 |
| *q*- | −0,016 | −3,1 |
| *a*- | −0,011 | −5,2 |
| *r*- | −0,031 | −8,2 |
| *l*- | −0,050 | −9,1 |
| *ch*- | **−0,073** | −11,1 |
| *k*- | **−0,065** | −11,2 |

- **Esito preregistrato:** a fine riga "-m/-g/-y/-d è la variante di bordo di -r"; a inizio riga "y/s/d/t è la
  variante di bordo di k". La regola nomina solo il segno che cala di più; a inizio riga *ch*- cala quasi quanto
  *k*-.
- **Lettura:**
  - **-*m* di fine riga è soprattutto la forma di bordo di -*r*** (e in parte di -*l*): lo stesso tronco che in mezzo
    alla riga finisce in -*r* (*dar*, *ar*, *sar*) a fine riga finisce in -*m* (*dam*, *am*, *sam*). Non è la forma
    di -*n*: -*n* non cala.
  - A inizio riga *y*- e *s*- prendono il posto soprattutto di *ch*- e *k*-. Una parte è il segno attaccato all'inizio
    della riga (e366, e368), che qui risulta come sostituzione perché il gruppo è la parola senza il primo segno.
- Per il voynichizzatore: a fine riga una parola in -*r* (meno in -*l*) diventa -*m* circa una volta su sette; a
  inizio riga *ch*-/*k*- diventano *y*-/*s*-.

## 3/10/2026 (notte) — e390: le due regole di raccordo sono il 39% della giuntura; il resto ha lo stesso stampo (-y con q-, le altre finali con ch-/sh-/o-/a-)

Preregistrato (`preregistrazioni/e390.md`). Giuntura fra parole separate da spazio normale, nullo nella pagina.

- Giuntura vera: E 0,164 (z 166, 27.442 coppie). Neutralizzata (*qo*- contato come *o*-, -*l* e -*r* fusi): E 0,100.
  **Quota spiegata dalle due regole: 0,39. Esito preregistrato: una parte importante.**
- **Coppie che contano di più** (contributo all'informazione oltre il nullo, bit):
  - **-*y* *q*- +0,087**, di gran lunga la prima;
  - -*r* *a*- +0,036; -*n* *ch*- +0,023; -*n* *o*- +0,019; -*s* *a*- +0,016; -*y* *l*- +0,013; -*n* *sh*- +0,012;
    -*r* *sh*- +0,012; -*r* *o*- +0,011; -*l* *ch*- +0,010; -*l* *d*- +0,010;
  - negative (evitate): -*y* *ch*- −0,026, -*y* *o*- −0,020, -*y* *sh*- −0,020, -*n* *q*- −0,016, -*l* *q*- −0,011,
    -*r* *q*- −0,011.
- **Lettura:** la giuntura ha uno stampo semplice. Dopo -*y* viene *q*- e si evitano *ch*-, *sh*-, *o*-; dopo -*n*,
  -*r*, -*l*, -*s* vengono *ch*-, *sh*-, *o*-, *a*- e si evita *q*-. È come una distribuzione complementare fra due
  classi di finali e due classi di inizi.

## 3/10/2026 (notte) — e391: nei testi in cerchio e lungo i raggi la giuntura c'è, forte come nei paragrafi

Preregistrato (`preregistrazioni/e391.md`). Loci di tipo cerchio e raggio: 2.185 coppie di parole vicine (cosmologia
1.038, zodiaco 792, astronomia 355).

- **Giuntura:** E 0,174 (z 24,9) contro 0,170 dei paragrafi a parità di coppie; Q 1,02. **Esito preregistrato: la
  giuntura c'è anche nei cerchi.** Dove la scrittura è continua, il legame c'è con la stessa forza, qualunque sia la
  forma del testo (riga, cerchio, raggio).
- **Regola di *qo*-:** 605 eventi; differenza +0,042, p 0,03. **Esito preregistrato: non dimostrata nei cerchi.** Nei
  testi circolari *qo*- dopo -*y*/-*o*/-*d* è solo un po' più frequente che dopo -*n*/-*r*/-*s*/-*m*, molto meno che
  nei paragrafi (Δ +0,25 – +0,48, e388). La giuntura dei cerchi è quindi fatta d'altro, o la regola di *qo*- è propria
  dei paragrafi: da guardare.

## 3/10/2026 (notte) — e392: la parola copiata dalla riga sopra prende la forma voluta dalla nuova vicina

Preregistrato (`preregistrazioni/e392.md`). Parole *qo*/*o* + gallows il cui nucleo (dalla gallows in poi) sta nella riga
subito sopra in una sola forma (la fonte), precedute da una parola in -*y*/-*o*/-*d* (V) o in -*n*/-*r*/-*s*/-*m* (C).

| fonte nella riga sopra | nuova vicina | eventi | P(*qo*) |
|---|---|---|---|
| *qo*- | V | 331 | 0,79 |
| *qo*- | C | 94 | **0,29** |
| *o*- | V | 183 | **0,62** |
| *o*- | C | 80 | 0,16 |

- Effetto della nuova vicina, a parità di fonte: **+0,49**, p < 0,0001. Effetto della fonte, a parità di vicina:
  +0,16, p < 0,0001.
- **Esito preregistrato: entrambe le cose**, ma la vicina pesa tre volte la fonte.
- **Lettura:** una parola ripresa dalla riga sopra non viene copiata così com'è. Se la fonte aveva *qo*- ma la nuova
  vicina finisce in -*n*/-*r*/-*s*/-*m*, la copia prende *o*- due volte su tre. Se la fonte aveva *o*- ma la nuova
  vicina finisce in -*y*/-*o*/-*d*, prende *qo*- quasi due volte su tre. La regola di raccordo si applica **nel momento
  in cui si scrive**, alla parola nel suo nuovo posto: è il comportamento di un raccordo fonetico o grafico fra parole,
  non di una forma fissa memorizzata. Va con l'e356 (la copia non eredita la grafia).

## 3/10/2026 (notte) — e393: qo- a inizio riga non guarda la riga sopra; la giuntura è il doppio in lingua B

Preregistrato (`preregistrazioni/e393.md`).

- **Parte 1.** 541 prime parole *qo*/*o* + gallows, in righe non d'inizio paragrafo. Differenza di *qo*- secondo la
  fine della riga sopra (-*y*/-*o*/-*d* contro -*n*/-*r*/-*s*/-*m*): Δ +0,013, p 0,37. **Esito preregistrato: non la
  segue.**
  - A inizio riga *qo*- è frequente di suo: biologia B 0,89, erbario A 0,57, erbario B 0,63, farmacia A 0,69,
    ricette B 0,44, solo testo B 0,78.
  - L'inizio riga ha quindi una regola propria: lì *qo*- è la forma normale. Al contrario, nelle etichette e dopo il
    salto del disegno la forma normale è *o*- (e387).
- **Parte 2.** Giuntura a parità di coppie (8.304), mediana di 20 campioni:

  | | lingua A | lingua B |
  |---|---|---|
  | giuntura | 0,104 (0,103 – 0,104) | **0,217** (0,195 – 0,229) |
  | neutralizzata (senza le due regole) | 0,076 | 0,132 |

  **Esito preregistrato: giuntura più forte in B**, circa il doppio, anche togliendo le due regole di raccordo. Va con
  l'e388 (regola di *qo*- più debole nella mano 1, che scrive in A).

## 3/10/2026 (notte) — e394: anche la fine di una parola copiata è coordinata con la parola dopo; limite di lettura per e392 ed e394

Preregistrato (`preregistrazioni/e394.md`). Parole in -*l*/-*r* il cui tronco sta nella riga sopra in una sola forma
(la fonte), seguite da una parola in *k*/*t*/*d*/*l*/*s*/*q* (K) o in *a*/*o*/*y* (A).

| fonte nella riga sopra | parola dopo | eventi | P(-*l*) |
|---|---|---|---|
| -*l* | K | 96 | 0,84 |
| -*l* | A | 111 | 0,47 |
| -*r* | K | 72 | **0,74** |
| -*r* | A | 121 | 0,31 |

- Effetto della parola dopo, a parità di fonte: **+0,40**, p < 0,0001. Effetto della fonte: +0,14, p 0,001.
- **Esito preregistrato: entrambe le cose**, con la parola dopo che pesa tre volte la fonte.
- **Limite di lettura, che vale anche per l'e392.** Queste tabelle mostrano che la forma della parola copiata è
  coordinata con la sua nuova vicina più che con la fonte. Non dicono **chi si adatta a chi**: nell'e394 la finale
  potrebbe adattarsi alla parola dopo (lo scriba sa già cosa scriverà), oppure la parola dopo potrebbe essere scelta
  per accordarsi con la finale appena scritta. Nell'e392, specularmente, vale lo stesso per *qo*-/*o*- e la parola
  prima. La lettura dell'e392 "prende la forma voluta dalla nuova vicina" va quindi presa così: **la forma è
  coordinata con la vicina nel momento in cui si scrive, non ereditata dalla fonte**. La direzione resta aperta.

## 3/10/2026 (notte) — e395: con la trascrizione di Takahashi tutte le prove sulla giuntura si ripetono

Preregistrato (`preregistrazioni/e395.md`). Sei prove della notte rifatte sulla trascrizione IT (Takahashi), che ha
scelte proprie di segni e spazi.

| prova | con IT | replicata |
|---|---|---|
| 1 giuntura nella riga | E 0,185, z 251 (29.477 coppie) | sì |
| 2 giuntura a capo | E −0,001, z −0,3 (3.330 coppie) | sì |
| 3 giuntura al salto del disegno | E 0,023, z 1,7 (767 coppie), contro 0,175 nella riga a parità di coppie | sì |
| 4 regola di *qo*- | differenza +0,39, p < 0,0001 (7.123 eventi) | sì |
| 5 regola di -*l*/-*r* | differenza +0,58, p < 0,0001 (3.319 eventi) | sì |
| 6 fine riga | -*m* +0,162 (z 27,3), -*r* −0,129 (z −15,2) | sì |

**Esito preregistrato: i risultati non dipendono dalla trascrizione.** I numeri sono quasi gli stessi della ZL.

## 3/10/2026 (notte) — e396: quando due parole copiate non si accordano, cambia la seconda

Preregistrato (`preregistrazioni/e396.md`). Coppie (a, b) nella riga con entrambe le parole riprese dalla riga sopra
(b = *qo*/*o* + gallows, a con finale in -*y*/-*o*/-*d* o -*n*/-*r*/-*s*/-*m*): 83, di cui 34 in cui le due fonti
violano la regola di *qo*-.

| misura | nei conflitti | negli accordi | differenza | p |
|---|---|---|---|---|
| cambia la finale di a (la parola prima) | 0,00 | 0,04 | −0,04 | 1,00 |
| cambia *qo*/*o* di b (la parola dopo) | **0,59** | 0,18 | **+0,41** | 0,0003 |

- **Esito preregistrato: si adatta la parola dopo.** Quando le due fonti insieme violerebbero la regola, lo scriba
  cambia la forma della seconda parola (*qo*- ↔ *o*-) quasi sei volte su dieci, e non tocca mai la finale della prima.
- **Cautela:** per adattarsi, la parola prima dovrebbe cambiare la classe della finale (per esempio -*n* → -*y*), un
  cambiamento più grosso di *qo*-/*o*-. L'asimmetria può dipendere in parte da questo. Per -*l*/-*r* (e394) la
  direzione resta aperta.
- **Lettura:** almeno per *qo*-/*o*-, la regola si applica scrivendo da sinistra a destra: la parola nuova si adegua a
  quella appena scritta.

## 3/10/2026 (notte) — e397: lo spazio del Voynich si prevede dai segni vicini per il 73%, più di quasi tutte le lingue

Preregistrato (`preregistrazioni/e397.md`). R = quota dell'incertezza sulla posizione degli spazi tolta da 2 segni a
sinistra e 2 a destra (modello a conteggi, due metà incrociate, 10.000 parole per testo).

- **Voynich:** R 0,727–0,740 (mediana **0,728**).
- **Testi sensati:** solo il cinese in pinyin lo supera (0,861: ogni "parola" è una sillaba di forma fissa). Poi greco
  tecnico 0,707, lojban 0,700, toki pona 0,699, pinyin tecnico 0,686, tagalog 0,605, greco del Nuovo Testamento 0,600,
  italiano tecnico 0,584, ... fino a 0,276 (anglosassone).
- **Esito preregistrato: nella gamma delle lingue** (1 testo su 71 con R maggiore).
- **Gibberish umano: 0,085.** Controllo (scratchpad): non è un errore di codice. I 38 testi sono di persone diverse,
  ciascuna con le sue parole inventate, e sono piccoli. Mescolati, i segni vicini dicono poco sugli spazi; testo per
  testo, con poco addestramento, si arriva a 0,13–0,22. Il confronto con il gibberish qui è debole.
- **Lettura:** gli spazi del Voynich cadono in posti molto prevedibili dai segni intorno, come nelle lingue a sillabe
  o a parole di forma regolare (pinyin, lojban, toki pona). Va con le parole di forma rigida del Voynich (e363).

## 3/10/2026 (notte) — Correzione: "DA" e "DC" nel gibberish non sono autori

Nell'e346 e nell'e374 ho riportato il gibberish "per autore" usando le sigle dei file (DA, DC). Il README di Gaskell e
Bowern dice che i volontari erano 42, e i file sono numerati DC_01 … DC_42 (più DA_01, DA_02): ogni file è
probabilmente una persona diversa, e le sigle sono raccolte, non autori. Le righe "per autore" di quegli esperimenti
vanno lette come "per raccolta". Le conclusioni sul gibberish nel complesso non cambiano. Il README nota anche che il
gibberish varia molto da persona a persona, e che ha "distorsioni nella posizione dei caratteri nella riga": va con
l'effetto debole ma presente dell'e374.

## 3/10/2026 — vz: e410, il cancello della riga: preso in 3 semi su 4; giudici a 0,552 / 0,616

Chat del voynichizzatore. Preregistrato (`preregistrazioni/e410.md`). Risultati in `risultati/e410_cancello_riga.md`.
Semi 1–4, corpo senza messaggio; riferimento R1 dell'e408 (corpo della v10): 0,554 / 0,673, pagella 17,0, cancello 0/4.

| strato | AUC e231 | AUC e266 (min–max) | pagella | estese | semi con il cancello |
|---|---|---|---|---|---|
| R1 (corpo della v10) | 0,554 | 0,673 | 17,0/18 | 2,5/8 | 0/4 |
| G1, prima lettera della riga + somiglianza a distanza 2 | 0,555 | 0,639 (0,619–0,657) | 16,0/18 | 3,8/8 | 0/4 |
| G2, + cinque scelte di grafia nella riga e fra righe | **0,552** | **0,616** (0,600–0,629) | 15,8/18 | 4,5/8 | **3/4** |

| condizione del cancello (soglia) | G1, per seme | G2, per seme |
|---|---|---|
| S1 (≤ 0,7) | 0,52, 0,55, 0,49, 0,50 | 0,53, 0,61, 0,59, 0,55 |
| A (≥ 1,0) | 1,02, 1,04, 1,02, 1,01 | 1,004, **0,997**, 1,022, 1,003 |
| scelte per riga (≥ 3) | 2, 3, 0, 2 | 5, 5, 5, 5 |
| r fra righe consecutive (0,207 ± 0,07) | 0,09, 0,09, 0,09, 0,08 | 0,20, 0,17, 0,18, 0,17 |

- **Previsioni rispettate.** G1: S1 e A a posto in 4 semi su 4. G2: scelte per riga e r a posto in 4 semi su 4;
  **cancello della riga preso in 3 semi su 4** (previsto: almeno 2). Nel quarto manca A per 0,003.
- **È la prima volta che il generatore a pezzi prende il cancello della riga**, e lo fa con il corpo soltanto: con il
  messaggio nel sacco le scelte di grafia non vengono riscritte.
- **Il giudice forte scende a 0,616** (da 0,673), come previsto: la somiglianza a distanza 2 era una delle sue
  caratteristiche più pesanti (0,2231 contro 0,2198 dopo la regolazione). È il valore più basso mai visto; l'e231 resta
  a 0,55.
- **Costo:** la materia "gradiente" si perde in 4 semi su 4 (già in G1): premiare la somiglianza dentro la riga
  abbassa il rapporto fra somiglianza a 6 righe e somiglianza nella riga. Pagella 15,8 contro 17,0. Resta perso il
  profilo pagina.
- **La regolazione non converge formalmente** (scarto 13%): resta fuori la concordanza delle desinenze (0,057 contro
  0,042, con il peso del legame fra finali già a zero), come nell'e408.
- **Pesi regolati:** prima lettera −0,80 (evitata), distanza 2 0,15, scelte nella riga 0,049, scelte fra righe 0,047.
  Bersagli del Voynich: S1 0,531; A 1,047; rapporto di varianza per riga 1,103; r 0,207.
- **Esito secondo la preregistrazione:** i termini si tengono (condizioni in almeno 3 semi, giudice forte non
  peggiore). G2 diventa il corpo della **v11**, con il messaggio nel sacco, e va al banco.
- **Che cosa resta per il giudice forte** (caratteristiche pesanti di G2): la differenza fra le due metà della pagina
  (JSD 0,038 contro 0,050), le coppie viste altrove (0,25 contro 0,22), alcune coppie di segni rare.

## 3/10/2026 (notte) — e398 abbandonato prima della preregistrazione: la misura non va bene per le sillabe

Idea: se le parole del Voynich fossero sillabe di una lingua (come nel pinyin), le coppie vicine che formano parole
tornerebbero insieme molto più del caso. Prove sui soli controlli, prima di fissare la preregistrazione (scratchpad):
- con il nullo dell'e375 il pinyin dà R 1,05 contro 1,27 dell'italiano. In una sillaba pinyin primo e ultimo segno
  quasi la individuano, e quel nullo non rompe niente;
- con un nullo libero (parole rimescolate nella pagina) il pinyin dà 1,19, contro 2,06 dell'italiano e 2,39 del
  latino. Con poche centinaia di sillabe anche le coppie casuali tornano spesso su più pagine, e la misura satura.

La misura "coppie su almeno 2 pagine" non confronta testi con inventari di dimensioni così diverse. Esperimento
abbandonato, niente esito. Nota: il Voynich ha migliaia di tipi di parola, non poche centinaia come un sillabario.
L'ipotesi "parola = sillaba" andrebbe quindi messa alla prova in altro modo (per esempio sulla dimensione e sulla forma
dell'inventario), non con questa misura.

## 4/10/2026 (notte) — e399: nessun generatore pubblicato ha una giuntura forte che si ferma all'a capo

Preregistrato (`preregistrazioni/e399.md`). Misura dell'e384 (giuntura nella riga e a capo).

| testo | E nella riga | z | E a capo | z | Q |
|---|---|---|---|---|---|
| Voynich | **0,191** | 222 | −0,003 | −0,8 | **−0,02** |
| Naibbe (Greshko 2025), a capo sulle righe del Voynich | 0,002 | 4,9 | −0,002 | −0,6 | — |
| U2 (Whitehatnetizen 2026) | −0,001 | −0,8 | −0,001 | −0,3 | — |
| U3 (Whitehatnetizen 2026) | 0,076 | 66,7 | 0,074 | 15,0 | 0,97 |
| Timm e Schinner, seme 1 | 0,012 | 16,2 | 0,003 | 1,1 | 0,26 |
| Timm e Schinner, seme 19 | 0,011 | 18,1 | 0,002 | 0,7 | 0,18 |

- **Esito preregistrato: nessun generatore la riproduce.**
- **La previsione per Naibbe (Q vicino a 1) non è valutabile:** il cifrario di Naibbe quasi non ha giuntura (0,002).
  Le sue parole vengono da tabelle scelte lettera per lettera, senza legame fra la fine di una e l'inizio della
  successiva.
- U3 ha una giuntura media (0,076) che però passa l'a capo (Q 0,97), al contrario del Voynich.
- Timm e Schinner ha una giuntura debole (0,011), un sedicesimo di quella del Voynich, che si ferma in parte a capo.
- Per tutti i generatori: la giuntura del Voynich (forte, con le regole di raccordo, chiusa nella riga) è una proprietà
  che nessuno ha ancora messo nel modello. Il voynichizzatore dell'altra chat usa già i legami ai bordi; va detto che
  devono fermarsi all'a capo e al salto del disegno.

## 4/10/2026 — vz: e293, banco della v11: cancello della riga preso in 3 chiavi su 3; 0,565 / 0,647; pagella 47/54



Banco preregistrato dell'e293 (`esegui.py e293 -- --v11`), Isidoro XVII nel sacco, chiavi "banco7", "banco8", "banco9". **Decodifica esatta nei tre manoscritti.**



| versione | pagella (3) | pagella estesa | cancello della riga | AUC e231 | AUC e266 |

|---|---|---|---|---|---|

| v5 | 49/54 | 57/78 | 0 | 0,816 | 0,917 |

| v10 | 50/54 | 63/78 | 0 | 0,550 | 0,662 |

| **v11** | 47/54 | 61/78 | **3 su 3** | 0,565 | **0,647** |



- **Il cancello della riga è preso con tutte e tre le chiavi**: prima volta dal passaggio alla pagella estesa (v4–v10 lo perdevano sempre). Per chiave: 0,572 / 0,646 (pagella 16); 0,564 / 0,634 (15); 0,559 / 0,662 (16).

- **Esito con il criterio dell'e293** rispetto alla v10: AUC dell'e266 −0,015 ma pagella estesa 61 contro 63: formalmente **non migliora** (perde materie). Le materie perse in tutte le chiavi sono **gradiente** e **profilo pagina** (omogeneità in una); fra le aggiunte mancano scelte di riga (3), coppie viste altrove (3), prime righe come registro (2). Parole rare per pagina: R 3,8, 1,7, 1,7 (presa).

- v10 e v11 sono quindi due compromessi diversi: la v10 ha più materie (50) senza il cancello; la v11 ha il cancello e il giudice forte più basso, con tre materie in meno. Il passo seguente deve dare il gradiente senza perdere il cancello.

- Valori grezzi del gradiente (corpo G2, semi 1–4): somiglianza nella riga 0,0457 (Voynich 0,0385), nella riga sotto 0,0390 (0,0399), a 6 righe 0,0266 (0,0335). Nel Voynich la somiglianza cala piano con la distanza fra righe; nel generatore le righe della pagina sono scambiabili fra loro.

## 4/10/2026 (notte) — e3a01: per -l/-r un segnale di "guardare avanti", ma con troppi pochi casi

Preregistrato (`preregistrazioni/e3a01.md`); primo esperimento della nuova serie di numeri della ricerca (e3a01, …),
perché da 400 in su i numeri sono dell'altra chat. Coppie (a, b) con a ripresa dalla riga sopra (tronco, finale -*l*/-*r*)
e b uguale a una parola della riga sopra.

- Coppie 49, conflitti 26. La finale di a cambia rispetto alla fonte nel **58%** dei conflitti contro il **13%** degli
  accordi: differenza +0,45, p 0,0015.
- **Esito preregistrato: non decidibile** (meno di 30 conflitti).
- La direzione è quella del "guardare avanti": quando la finale della fonte non va bene per la parola che verrà, lo
  scriba la cambia. Con 26 casi però non lo considero dimostrato. Estensione con più casi nell'e3a02 (fonti dalle 2
  righe sopra).

## 4/10/2026 (notte) — e3a02: lo scriba adatta la parola dopo per qo-/o-, e la fine della parola prima per -l/-r: guarda avanti

Preregistrato (`preregistrazioni/e3a02.md`). Estensione dell'e3a01 e dell'e396, decisa dopo quei risultati: fonti
cercate nelle 2 righe sopra (non indipendente da quelle prove, le allarga).

| regola | coppie | conflitti | che cosa cambia | nei conflitti | negli accordi | differenza | p |
|---|---|---|---|---|---|---|---|
| -*l*/-*r* | 94 | 37 | finale della parola prima | **0,59** | 0,21 | +0,38 | 0,0002 |
| *qo*-/*o*- | 189 | 60 | finale della parola prima | 0,08 | 0,02 | +0,07 | 0,03 |
| *qo*-/*o*- | | | *qo*/*o* della parola dopo | **0,60** | 0,18 | +0,42 | < 0,0001 |

- **Esito preregistrato, parte A: lo scriba guarda avanti.** Quando la finale della fonte (-*l* o -*r*) non va bene
  per la parola che verrà dopo, lo scriba la cambia sei volte su dieci: mentre finisce una parola sa già quale sarà la
  successiva.
- **Esito preregistrato, parte B: si adatta la parola dopo** (conferma l'e396 con 60 conflitti).
- **Lettura:** ogni regola agisce sul pezzo più facile da cambiare. Per *qo*-/*o*- cambia l'inizio della seconda
  parola, per -*l*/-*r* la fine della prima. Lo scriba scrive una sequenza che conosce almeno una parola in anticipo:
  la sta copiando, o la ha in mente prima di scriverla. Con le parole della parte A copiate dalla riga sopra, il "dopo"
  era già scritto lì: guardare avanti qui può voler dire sapere quale parola si sta per riprendere.

## 4/10/2026 (notte) — e3a04: giuntura e raccordo reggono in quattro sezioni su cinque; nel "solo testo" la giuntura sembra passare l'a capo

Preregistrato (`preregistrazioni/e3a04.md`).

| sezione | coppie | giuntura nella riga E (z) | a capo E (z) | regola *qo*- Δ (p) | regola -*l*/-*r* Δ (p) |
|---|---|---|---|---|---|
| ricette | 9.534 | 0,206 (143) | 0,000 (0,0) | +0,38 (< 0,0001) | +0,57 (< 0,0001) |
| erbario | 8.411 | 0,119 (54) | 0,004 (0,5) | +0,27 (< 0,0001) | +0,55 (< 0,0001) |
| biologia | 5.003 | 0,263 (118) | 0,014 (1,2) | +0,56 (< 0,0001) | +0,67 (< 0,0001) |
| solo testo | 1.879 | 0,172 (25,5) | **0,140 (3,6)** | +0,35 (< 0,0001) | +0,48 (< 0,0001) |
| farmacia | 1.867 | 0,112 (17,4) | −0,028 (−0,7) | +0,28 (< 0,0001) | pochi dati |

- **Esito preregistrato: non reggono ovunque.** Unica eccezione: nella sezione "solo testo" (f1r, f66r, f76r, f85r1,
  f86v5, f86v6; 193 coppie a capo) la giuntura sembra passare l'a capo.
- **Controllo esplorativo** (scratchpad): togliendo una pagina alla volta, z resta fra 1,9 (senza f85r1) e 3,6. Non
  dipende da una sola pagina. Con 193 coppie, però, lo z dell'informazione mutua può esagerare: verifica con un nullo
  esatto e una taratura sulle altre sezioni nell'e3a06.
- Le due regole di raccordo reggono in tutte le sezioni con dati sufficienti.

## 4/10/2026 (notte) — e3a05: la giuntura si ripete con la trascrizione di Glen Claston

Preregistrato (`preregistrazioni/e3a05.md`). Trascrizione GC, alfabeto v101 (un carattere = un segno), divisione dei
glifi diversa dall'EVA.

- Nella riga: E 0,233 (z 186, 31.892 coppie). A capo: E 0,003 (z 0,5, 3.176 coppie). Q = 0,02.
- **Esito preregistrato: la giuntura si ripete con Glen Claston.**
- Coppia più forte: "-9 4-" (+0,089 bit), cioè -*y* *q*- in EVA, come nella ZL (+0,087).
- Con ZL, IT (e395) e GC, la giuntura chiusa nella riga regge in tre trascrizioni fatte da persone diverse.

## 4/10/2026 (notte) — e3a03: a parità della parola in mezzo, nessun legame a distanza 2 (nelle lingue sempre)

Preregistrato (`preregistrazioni/e3a03.md`). Terne di parole nella riga (w1, w2, w3): informazione mutua fra l'ultimo
segno di w1 e il primo di w3, a parità di w2 intera (e dello strato), oltre il nullo.

- **Voynich:** E 0,0033, z 1,3 (26.630 terne). A 10.000 parole: 0,0019, 0,0018, 0,0015, 0,0025, −0,0007 (mediana
  0,0018).
- **Gibberish umano:** E 0,0068, z 2,7.
- **Testi sensati (10.000 parole):** da 0,18 (pinyin) e 0,16 (toki pona), inglese 0,12–0,13, francese 0,11, tedesco
  0,10–0,11, arabo 0,11, spagnolo 0,09, ... Fra i testi con almeno 5.000 terne il minimo è il sanscrito (0,013, z 5,9;
  0,019 il Mahabharata). Solo 4 testi piccoli (1.000–2.100 terne) stanno vicino a zero.
- **Esito preregistrato: nessun legame oltre la parola accanto.**
- **Lettura:** nelle lingue la grammatica lega anche parole non vicine (accordi, reggenze, ordine delle parole). Nel
  Voynich il legame fra parole sta tutto fra vicine immediate: una volta nota la parola in mezzo, la prima non dice
  niente sulla terza. Il sistema guarda una parola avanti (e3a02) e una indietro (e392), non di più. Una lingua scritta
  così, con grammatica a distanza, lascerebbe un segno che qui non c'è.

## 4/10/2026 (notte) — e3a06: nelle 6 pagine "solo testo" c'è davvero un legame a capo, ma non è la regola di raccordo

Preregistrato (`preregistrazioni/e3a06.md`). Pagine f1r, f66r, f76r, f85r1, f86v5, f86v6; 193 coppie a capo.

- E 0,144; **p esatto 0,0006** (10.000 rimescolamenti nella pagina). Taratura: 2.000 insiemi di 193 coppie a capo dalle
  altre sezioni danno E da −0,114 a 0,135 (mediana 0,000); nessuno arriva a 0,144.
- **Esito preregistrato: nel solo testo la giuntura passa l'a capo.**
- **Esplorativo** (scratchpad): il legame viene da poche coppie con pochi casi (-*r* *ch*- 5, -*m* *t*- 7, -*y* *y*- 16,
  -*l* *d*- 7). La regola di *qo*- non passa l'a capo nemmeno lì: *qo*- a inizio riga è 73% dopo -*y*/-*o*/-*d* e 67%
  dopo -*n*/-*r*/-*s*/-*m* (nelle altre sezioni 67% e 61%).
- **Lettura prudente:** in queste 6 pagine la fine di una riga e l'inizio della seguente non sono indipendenti, ma non
  per la regola di raccordo. Forse ci sono strutture che si ripetono a cavallo delle righe (per esempio coppie riprese
  insieme). Il quadro generale (riga chiusa) resta per le sezioni illustrate e per le ricette. Da guardare a mano su
  quelle pagine.

## 4/10/2026 (notte) — e3a07: il legame a distanza 2 delle lingue era in buona parte argomento; ne resta una parte, nel Voynich niente

Preregistrato (`preregistrazioni/e3a07.md`). Come l'e3a03, ma con il nullo dentro (pagina, parola in mezzo).

- **Voynich:** E 0,0013, z 0,9 (26.630 terne). **Gibberish umano:** E 0,0011, z 0,7.
- **Testi sensati con almeno 5.000 terne (42):** mediana di E **0,013**, contro 0,068 dell'e3a03. Il legame resta
  significativo (z > 3) in 34 testi su 42. Massimi: pinyin 0,042, inglese 0,030–0,038. Vicino a zero: Plinio in latino
  (due versioni) e Charaka Samhita.
- **Esito preregistrato: in buona parte argomento.** Nell'e3a03 il contrasto con le lingue era gonfiato dalle parole
  che tornano nella stessa pagina. Il risultato sul Voynich non cambia (nessun legame), ma il confronto giusto è con un
  legame piccolo: le lingue ce l'hanno quasi sempre (34 su 42), il Voynich no.
- Il dossier va corretto (fatto).

## 4/10/2026 (notte) — e3a09: la -m di fine riga è più rara nell'ultima riga del paragrafo: è legata al margine

Preregistrato (`preregistrazioni/e3a09.md`). Ultime parole della riga in -*m*/-*r*/-*l*.

| prova | eventi (sì / no) | P(-*m*) sì | P(-*m*) no | differenza pesata | p |
|---|---|---|---|---|---|
| A: terzo di righe più piene contro meno piene | 396 / 396 | 0,495 | 0,424 | +0,071 | 0,04 |
| B: ultima riga del paragrafo contro le altre | 199 / 1.233 | **0,342** | 0,453 | **−0,135** | 0,0006 |

- **Esito A: incerto.** Le righe più piene hanno un po' più -*m*, ma sotto la soglia.
- **Esito B: -m più rara a fine paragrafo (legata al margine).** Nell'ultima riga del paragrafo, che di solito si
  ferma prima del margine, la parola finale prende -*m* meno spesso.
- **Lettura:** -*m* non segna solo "fine della riga": è più frequente quando la riga arriva al margine. Va con l'idea
  di una forma finale usata per chiudere una riga piena. Cautela: l'ultima riga del paragrafo differisce anche in altro
  (meno *qo*-, e313).

## 4/10/2026 (notte) — e3a08: il legame con la parola vicina passa quasi tutto dal segno di bordo

Preregistrato (`preregistrazioni/e3a08.md`). A parità di ultimo segno (e di strato), quanto l'identità intera della
parola prima dice ancora sul primo segno della parola dopo ("avanti"); e simmetricamente ("indietro").

| testo | avanti E | z | indietro E | z |
|---|---|---|---|---|
| Voynich (tutto) | 0,080 | 21,4 | 0,038 | 10,5 |
| Voynich a 10.000 parole (mediana) | **0,059** | | **0,024** | |
| gibberish umano | 0,121 | 28,4 | 0,126 | 24,9 |
| testi sensati con almeno 5.000 coppie (mediana) | 0,328 | | 0,309 | |

Massimi fra le lingue: toki pona 0,65, lojban 0,53, pinyin 0,52 (avanti).

- **Esito preregistrato, avanti e indietro: il legame passa solo dal segno di bordo** (il Voynich è sotto un quarto
  della mediana delle lingue: 18% avanti, 8% indietro).
- Non è però zero: sul libro intero resta un piccolo legame dell'identità della parola (z 21 avanti, 10 indietro). In
  una lingua l'identità della parola conta molto (sintassi); nel Voynich poco, meno anche che nel gibberish umano.
- Dove sta il resto: da vedere se nel penultimo segno (per esempio -*dy*/-*ey*) o nelle parole spezzate (*or aiin*,
  e379). Prossimo: e3a10.

## 4/10/2026 (notte) — e3a11: le etichette finiscono come le righe (-m, -g, e anche -s, -d)

Preregistrato (`preregistrazioni/e3a11.md`). A parità del resto della parola e della sezione, etichette contro parole
in mezzo alla riga (metodo dell'e389). Pochi dati: 103 etichette in 71 gruppi per le finali, 104 in 67 per le iniziali.

- **Finali che crescono nelle etichette** (z > 3): -*g* (+0,009, z 3,9), -*m* (+0,061, z 3,7), -*s* (+0,051, z 3,6),
  -*d* (+0,026, z 3,3). Nessuna cala sotto z −3 (-*y* −0,030, z −2,1).
- **Iniziali:** cresce solo *i*- (z 5,2, su pochissime parole); *d*- +0,074 (z 2,8).
- **Esito preregistrato:** crescono -*g*, -*m*, -*s*, -*d* fra le finali, *i*- fra le iniziali.
- **Lettura:** la parola isolata finisce più spesso con i segni della fine della riga (-*m*, -*g*, e389). La "forma di
  pausa" a fine parola è quindi -*m*/-*g*, non -*l* come avevo ipotizzato (e387). Con l'e3a09 (-*m* più rara
  nell'ultima riga del paragrafo) il quadro non è ancora coerente: -*m* compare a fine riga piena e in parole isolate,
  meno a fine paragrafo. Numeri piccoli: da prendere come indizio.

## 4/10/2026 (notte) — e3a12: le parole uniche rispettano la giuntura per circa due terzi

Preregistrato (`preregistrazioni/e3a12.md`). Giuntura nelle coppie con una parola unica nel libro, confrontata con le
coppie di parole ripetute a parità di numero di coppie (21.091 coppie di parole ripetute).

| classe | coppie | E | z | E ripetute a parità | Q |
|---|---|---|---|---|---|
| destra forma nuova | 2.402 | 0,124 | 22,6 | 0,185 | 0,67 |
| sinistra forma nuova | 2.451 | 0,093 | 15,3 | 0,182 | **0,51** |
| destra errore | 1.049 | 0,116 | 10,6 | 0,174 | 0,67 |
| sinistra errore | 1.031 | 0,118 | 9,5 | 0,179 | 0,66 |

- **Esito preregistrato: in parte, per tutte e quattro le classi.**
- **Lettura:** le parole uniche, forme nuove ed errori, seguono la giuntura con le vicine con circa due terzi della forza
  delle parole ripetute. Escono dallo stesso processo di scrittura, solo meno regolari. La più debole è la fine delle
  forme nuove (Q 0,51): spesso finiscono con segni insoliti (e362, e403).

## 4/10/2026 (notte) — e3a13: inizio riga, dopo un disegno ed etichette non imitano nessuna finale (solo una tendenza)

Preregistrato (`preregistrazioni/e3a13.md`). Distribuzione del primo segno nei tre casi senza parola prima, confrontata
con quella che segue ciascuna finale (-*d*, -*l*, -*n*, -*o*, -*r*, -*s*, -*y*) e con quella generale del mezzo della
riga (divergenza di Jensen-Shannon).

| caso | parole | dal generale | finale più vicina | rapporto (IC 95%) | iniziali più frequenti |
|---|---|---|---|---|---|
| inizio riga | 3.370 | 0,122 | -*y* (0,107) | 0,88 (0,85 – 0,90) | *d*, *y*, *o*, *q*, *s*, *t* |
| dopo un disegno | 740 | 0,094 | -*n* (0,063) | 0,68 (0,62 – 0,76) | *o*, *d*, *ch*, *y*, *s*, *sh* |
| etichetta | 997 | 0,148 | -*n* (0,136) | 0,92 (0,88 – 0,96) | *o* (59%), *d*, *y*, *s*, *ch* |

- **Esito preregistrato, per tutti e tre: né come una finale né come il generale.**
- C'è solo una tendenza coerente con la regola di *qo*-: l'inizio riga somiglia di più a "dopo -*y*" (dove viene *qo*-),
  dopo un disegno e nelle etichette di più a "dopo -*n*" (dove viene *o*-). Ma ogni caso ha una sua distribuzione:
  l'inizio riga ha molti *d*-, *y*-, *s*- (i segni di bordo, e389), le etichette sono quasi tutte *o*-.
- Lettura: i posti senza parola prima non si spiegano come "una finale sottintesa"; hanno regole proprie.

## 4/10/2026 (notte) — e3a10: il piccolo legame oltre il segno di bordo è sparso nella parola

Preregistrato (`preregistrazioni/e3a10.md`). Legame dell'identità della parola con il segno della vicina, condizionando
su k segni di bordo.

| direzione | condizione | E | z |
|---|---|---|---|
| avanti | ultimo segno (k = 1) | 0,080 | 20,8 |
| avanti | ultimi 2 segni | 0,050 | 14,5 |
| avanti | ultimi 3 segni | 0,028 | 9,1 |
| avanti | k = 1, senza parole corte | 0,064 | 14,6 |
| indietro | primo segno | 0,038 | 10,3 |
| indietro | primi 2 segni | 0,021 | 6,0 |
| indietro | primi 3 segni | 0,011 | 4,3 |
| indietro | k = 1, senza parole corte | 0,037 | 8,9 |

- **Esito preregistrato, in tutte e due le direzioni: il resto è sparso nella parola.** Non sta nel penultimo segno
  (con 2 segni resta il 63%) né nelle parole corte (senza di esse resta l'80% avanti, il 97% indietro).
- **Ipotesi da verificare:** il resto viene dal lessico della pagina. Nella stessa pagina tornano le stesse famiglie di
  parole, e questo lega l'identità di una parola all'iniziale della vicina anche senza raccordo. Il nullo dell'e3a08 e
  dell'e3a10 rimescolava fra pagine diverse: prova con il nullo dentro la pagina nell'e3a14.

## 4/10/2026 (notte) — e3a15: -ey cresce scendendo nella pagina anche a parità di posizione e lunghezza della riga

Preregistrato (`preregistrazioni/e3a15.md`). Righe interne della pagina; celle (pagina × posizione della parola nella riga
× terzile di lunghezza della riga); quota di -*ey* fra -*dy*/-*ey*, metà bassa meno metà alta.

- 562 celle, 7.897 parole. Differenza **+0,057, z 4,8.**
- **Esito preregistrato: la crescita verticale resta.** Non è un effetto della posizione nella riga né della lunghezza
  delle righe in basso: scendendo nella stessa pagina, a parità di questi fattori, lo scriba usa di più -*ey*.
- Resta da capire perché. Ipotesi da provare: legata alla ripresa (e370: più forte nelle parole riprese) o alla
  distanza dalla prima riga del paragrafo invece che della pagina.

## 4/10/2026 (notte) — e3a16: la regola di raccordo ha la stessa forza in tutte le sessioni

Preregistrato (`preregistrazioni/e3a16.md`). Δ = P(*qo* | parola prima in -*y*/-*o*/-*d*) − P(*qo* | in -*n*/-*r*/-*s*/-*m*)
per bifoglio; dispersione degli scarti dallo strato contro un nullo che rimescola gli esiti fra bifogli dello stesso
strato e della stessa classe.

- 30 bifogli in 6 strati; Δ da +0,02 a +0,60 (mediana +0,32). Dispersione 0,0060 contro 0,0084 del nullo (rapporto
  0,72), z −0,8.
- **Esito preregistrato: uniforme fra le sessioni, come una regola fissa.** Le differenze fra bifogli sono quelle del
  caso. La regola si comporta come gli errori (uniformi, e357) e non come l'inventiva (che varia 4 volte il caso,
  e376): è una regola del sistema, non un'abitudine della sessione.

## 4/10/2026 (notte) — e3a14: due terzi del "resto" erano lessico della pagina; resta un legame fra vicine pari a un quarto di quello delle lingue

Preregistrato (`preregistrazioni/e3a14.md`). Come l'e3a08, con il nullo dentro (pagina, segno di bordo).

| | avanti E | z | indietro E | z |
|---|---|---|---|---|
| Voynich (tutto) | 0,027 | 9,9 | 0,017 | 5,8 |
| Voynich a 10.000 parole (mediana) | **0,026** | | **0,018** | |
| testi sensati con almeno 5.000 coppie (mediana), stesso nullo | 0,111 | | 0,096 | |

- **Esito preregistrato: resta un piccolo legame fra vicine** (z > 3 in tutte e due le direzioni).
- Con il nullo dentro la pagina il resto avanti scende da 0,080 (e3a10) a 0,027: **due terzi erano lessico della
  pagina**. Quello che resta, oltre il segno di bordo, è circa un quarto (avanti) e un quinto (indietro) di quello delle
  lingue con lo stesso nullo.
- **Quadro aggiornato:** fra parole vicine il Voynich ha un legame forte fra segni di bordo (la giuntura) e un legame
  debole fra parole intere, un quarto di quello di una lingua. Fra parole non vicine, niente (e3a07).

## 4/10/2026 (notte) — e3a17: -ey cresce sia con l'altezza nella pagina sia con la posizione nel paragrafo

Preregistrato (`preregistrazioni/e3a17.md`). 154 pagine con più paragrafi, 9.240 parole in -*dy*/-*ey*; regressione con
effetti fissi di pagina × posizione nella riga, bootstrap sulle pagine.

| fattore | coefficiente (da cima a fondo) | IC 95% |
|---|---|---|
| altezza nella pagina | +0,124 | +0,067 – +0,184 |
| posizione nel paragrafo | +0,099 | +0,061 – +0,133 |

- **Esito preregistrato: tutte e due.** La quota di -*ey* cresce scendendo nella pagina e, separatamente, scendendo nel
  paragrafo. All'inizio di un paragrafo -*ey* torna più raro anche se il paragrafo comincia in basso nella pagina.

## 4/10/2026 (notte) — Esplorativo: dove cadono gli spazi incerti

Non preregistrato (scratchpad). Quota di spazi incerti (virgola nella ZL) per coppia (ultimo segno, primo segno);
generale 8,2%.
- **-*y* *q*-**, la coppia più forte della giuntura, ha quasi sempre uno spazio netto: incerto solo nell'1,0% (3.448
  coppie). Così anche -*y* *o*- (0,6%), -*n* *ch*- (0,5%), -*n* *q*- (0%). Il raccordo -*y* → *qo*- lega due parole ben
  separate.
- Gli spazi incerti si concentrano in -*l* *k*- (43%), -*r* *a*- (28%), -*y* *t*- (19%), -*y* *k*- (18%), -*l* *sh*-
  (16%), -*l* *d*- (14%), -*l* *ch*- (12%): proprio i posti delle parole spezzate o attaccate (*ol kedy*, *or aiin*;
  e379).

## 4/10/2026 (notte) — e3a18: due famiglie di scelte di grafia: quelle di raccordo non derivano, quelle di "stato" sì

Preregistrato (`preregistrazioni/e3a18.md`). Regressione di ogni scelta su altezza nella pagina e posizione nel
paragrafo, con effetti fissi di pagina × posizione nella riga (× classe della vicina per *qo*-/*o*- e -*l*/-*r*);
intervalli al 99,5% (Bonferroni su 10 coefficienti).

| scelta | eventi | altezza nella pagina | esito | posizione nel paragrafo | esito |
|---|---|---|---|---|---|
| *sh* fra *ch*/*sh* | 7.700 | +0,009 | nessuna deriva | **−0,196** | cala |
| *t* fra *k*/*t* | 12.880 | **−0,077** | cala | **−0,090** | cala |
| *qo* fra *qo*/*o* | 8.069 | +0,004 | nessuna deriva | −0,024 | nessuna deriva |
| -*r* fra -*l*/-*r* | 9.109 | −0,046 | nessuna deriva | −0,038 | nessuna deriva |
| -*ey* fra -*dy*/-*ey* | 9.032 | **+0,125** | cresce | **+0,101** | cresce |

- **Esito preregistrato:** derivano *sh* (cala nel paragrafo), *t* (cala nella pagina e nel paragrafo), -*ey* (cresce
  nella pagina e nel paragrafo). *qo*-/*o*- e -*l*/-*r* non derivano. Controllo: -*ey* ripete l'e3a17.
- **Lettura:** le cinque scelte si dividono in due famiglie.
  - **Scelte di raccordo** (*qo*-/*o*-, -*l*/-*r*): dipendono dalla parola vicina (e380) e non da dove si è nella
    pagina.
  - **Scelte di stato** (*ch*/*sh*, *k*/*t*, -*dy*/-*ey*): non dipendono dalla vicina (e380) ma derivano con la
    posizione: *sh* e *t* più frequenti all'inizio del paragrafo, -*ey* verso la fine.
- Cautela: *sh* e *t* potrebbero dipendere soprattutto dalla prima riga del paragrafo (con le gallows d'apertura). Lo
  verifica l'e3a20, senza le prime righe.

## 4/10/2026 (notte) — e3a19: la copia dalla riga sopra cresce lungo il paragrafo

Preregistrato (`preregistrazioni/e3a19.md`). 499 paragrafi con almeno 4 righe; eccesso di parole (3+ segni) con una
parola uguale o a una modifica nella riga subito sopra, per terzo del paragrafo.

- Inizio **+0,005**, mezzo +0,036, fine **+0,047**. Fine − inizio +0,042 (IC 95% +0,026 – +0,058).
- **Esito preregistrato: la copia cresce lungo il paragrafo.**
- **Lettura:** il paragrafo comincia con parole nuove e diventa via via più ripetitivo. Va con la deriva delle scelte di
  stato (e3a18: -*ey* cresce, *sh* e *t* calano scendendo nel paragrafo).
- Cautela: nel primo terzo la "riga sopra" è spesso la prima riga del paragrafo, che è speciale (parole nuove, e344;
  gallows d'apertura). Verifica senza le righe d'apertura nell'e3a20.

## 4/10/2026 (notte) — e3a20: senza le righe d'apertura le derive lungo il paragrafo spariscono; resta solo -ey con l'altezza nella pagina

Preregistrato (`preregistrazioni/e3a20.md`). Verifica di e3a17, e3a18 ed e3a19 togliendo le righe d'apertura.

**Parte A** (senza la prima riga dei paragrafi e della pagina; IC 99,5%):

| scelta | altezza nella pagina | esito | posizione nel paragrafo | esito |
|---|---|---|---|---|
| *sh* fra *ch*/*sh* | +0,002 | nessuna deriva | −0,032 | nessuna deriva (era −0,196) |
| *t* fra *k*/*t* | −0,062 | nessuna deriva | −0,031 | nessuna deriva (era −0,090) |
| *qo* fra *qo*/*o* | −0,020 | nessuna deriva | −0,030 | nessuna deriva |
| -*r* fra -*l*/-*r* | −0,055 | nessuna deriva | +0,002 | nessuna deriva |
| -*ey* fra -*dy*/-*ey* | **+0,139** | **cresce** | +0,027 | nessuna deriva (era +0,101) |

**Parte B** (righe i ≥ 2, paragrafi di almeno 6 righe): eccesso di copia inizio +0,051, mezzo +0,041, fine +0,043;
fine − inizio −0,007 (IC −0,029 – +0,015). **Esito: costante.**

- **Correzione delle letture di e3a17, e3a18 ed e3a19:**
  - le derive di *sh* e *t* lungo il paragrafo venivano dalla **prima riga del paragrafo** (dove *sh* e *t* abbondano,
    con le gallows d'apertura), non da un cambiamento graduale;
  - la crescita della copia lungo il paragrafo veniva dall'apertura: la seconda riga copia poco dalla prima, perché la
    prima è fatta di parole nuove (e344). Dopo, la copia è costante;
  - -*ey* cresce davvero con l'altezza nella **pagina** (anche senza la prima riga), non con la posizione nel paragrafo.
- **Quadro corretto:** il paragrafo ha un'apertura speciale (prima riga: gallows, *sh*, *t*, parole nuove), poi è
  stabile. L'unica deriva vera è -*ey*, che cresce scendendo nella pagina indipendentemente dai paragrafi.

## 4/10/2026 (notte) — e3a21: la crescita di -ey scendendo nella pagina sta soprattutto nelle ricette

Preregistrato (`preregistrazioni/e3a21.md`). Misura dell'e3a15 per sezione.

| sezione | parole | metà bassa − metà alta | z | esito |
|---|---|---|---|---|
| erbario | 1.068 | +0,039 | 1,4 | non cresce |
| biologia | 2.304 | +0,039 | 1,8 | non cresce |
| **ricette** | 3.371 | **+0,108** | **5,7** | **cresce** |
| farmacia | 424 | +0,006 | 0,1 | non cresce |
| altre | 730 | −0,060 | −1,5 | non cresce |
| erbario senza righe con salto del disegno | 607 | +0,061 | 1,7 | non cresce |

- **Esito preregistrato: non dipende dai disegni** (cresce nelle ricette, dove il testo non gira intorno ai disegni).
- Ma la crescita sta soprattutto lì: nelle ricette (pagine fitte, paragrafi brevi segnati da stelle, mano 3) è forte;
  in erbario e biologia va nella stessa direzione sotto soglia; altrove no. La "deriva verticale" di -*ey* è quindi in
  gran parte una proprietà delle pagine delle ricette.
- Esplorativo a parte (scratchpad), sulle pagine "solo testo" dell'e3a06: le parole non si spezzano fra una riga e
  l'altra (l'unione fine riga + inizio riga è una parola nota solo nello 0,5% dei casi, contro l'1,3% altrove). Il legame
  a capo di quelle pagine resta da spiegare.

## 4/10/2026 (notte) — e3a22: la prima riga del paragrafo pende verso il lato "B" dell'asse, e la seconda un po' meno

Preregistrato (`preregistrazioni/e3a22.md`). Asse A/B semplice (quota di *e* + parole in -*y* − quota di *a* − quota di
*n* − parole in -*n*); positivo = verso B (-*edy*).

| confronto | paragrafi | differenza media | z |
|---|---|---|---|
| prima riga contro il resto del paragrafo | 667 | **+0,100** | 6,7 |
| prima riga senza la prima parola | 667 | +0,115 | 7,3 |
| seconda riga contro le righe dalla terza (controllo) | 667 | +0,049 | 3,0 |
| prima riga, lingua A | 232 | +0,054 | 2,0 |
| prima riga, lingua B | 417 | +0,128 | 6,9 |

- **Esito preregistrato: la prima riga è spostata verso B (-edy).** Non dipende dalla prima parola con la gallows.
- **Il controllo però non è zero:** anche la seconda riga pende verso B rispetto alle seguenti (z 3,0). Non è quindi
  "un'altra lingua" nella prima riga, ma una **pendenza** lungo l'inizio del paragrafo: le prime righe hanno più *e* e
  finali -*y*, meno *a* e -*n*; poi il paragrafo si assesta. Più forte nelle pagine in lingua B.
- Da collegare: nell'e3a20 *sh* e *t* stavano soprattutto nella prima riga. L'apertura del paragrafo è un registro un
  po' diverso, che sfuma nelle righe successive.

## 4/10/2026 (notte) — e3a23: la giuntura è piena anche ai bordi della riga

Preregistrato (`preregistrazioni/e3a23.md`). Righe di almeno 4 parole.

| coppia | quante | E | z | E in mezzo a parità | Q |
|---|---|---|---|---|---|
| prima coppia (parole 1–2) | 3.500 | 0,184 | 44,0 | 0,162 | **1,14** |
| ultima coppia | 3.254 | 0,158 | 34,7 | 0,168 | **0,94** |

- **Esito preregistrato, per tutti e due i bordi: giuntura piena anche al bordo.**
- Le forme di bordo (*s*-, *y*-, *d*- all'inizio; -*m*, -*g* alla fine) non tolgono forza al legame con la parola
  vicina: posizione nella riga e raccordo agiscono insieme.

## 4/10/2026 (notte) — e3a24: le righe non rimano; le prime parole di righe consecutive si evitano

Preregistrato (`preregistrazioni/e3a24.md`). 656 paragrafi; coppie di righe consecutive con almeno 3 parole ciascuna.

| confronto | osservata | nullo (righe rimescolate) | rapporto | z |
|---|---|---|---|---|
| rima: ultime parole, ultimi 2 segni uguali | 0,107 | 0,104 | 1,03 | 0,9 |
| ultima parola contro una parola in mezzo della riga sopra | 0,101 | 0,094 | 1,07 | 1,4 |
| allitterazione: prime parole, primi 2 segni uguali | **0,030** | 0,054 | **0,57** | **−6,8** |
| prima parola contro una parola in mezzo della riga sopra | 0,060 | 0,048 | 1,24 | 3,1 |

- **Esito preregistrato: nessuna rima** (R 0,96) **e nessuna allitterazione** (R 0,46).
- **Ma c'è il contrario dell'allitterazione:** le prime parole di due righe consecutive cominciano con gli stessi 2
  segni il 43% in meno del caso (z −6,8), mentre la prima parola riprende volentieri le parole in mezzo della riga sopra
  (+24%). Sembra che lo scriba eviti di cominciare una riga come la precedente.
- Da verificare (e3a25): può dipendere dalla prima riga del paragrafo, che comincia in modo speciale (gallows) e che il
  nullo sposta in mezzo al paragrafo.

## 4/10/2026 (notte) — Esplorativo: nei testi in cerchio qo- è raro come nelle etichette

Non preregistrato (scratchpad). Quota di *qo*- fra *qo*/*o* + gallows: paragrafi 0,51 (nei paragrafi della sezione
cosmologica 0,45); testi in cerchio 0,05 (zodiaco 0,03, cosmologia 0,07, astronomia 0,04); raggi 0,14; etichette 0,02.
I testi in cerchio hanno la giuntura (e391) ma quasi senza *qo*-. L'inserimento di *q* dopo -*y* è proprio del testo in
paragrafi; i cerchi usano la forma *o*- come le etichette. Questo spiega la regola debole dell'e391.

## 4/10/2026 (notte) — e3a25: due righe consecutive quasi mai cominciano entrambe con qo-

Preregistrato (`preregistrazioni/e3a25.md`). Senza le prime righe dei paragrafi; coppie di righe consecutive con almeno
3 parole.

| confronto | coppie | osservata | nullo | rapporto | z |
|---|---|---|---|---|---|
| stessi primi 2 segni | 2.267 | 0,035 | 0,069 | **0,50** | **−8,0** |
| stesso primo segno | 2.267 | 0,080 | 0,145 | 0,55 | −10,5 |

Testi sensati con almeno 300 coppie, rapporto (primi 2 segni): minimo 0,36, mediana 0,97, massimo 1,90.

- **Esito preregistrato: incerto.** L'effetto non dipendeva dalla prima riga del paragrafo (rapporto 0,50, z −8,0), ma
  alcuni testi sensati arrivano più in basso (minimo 0,36), e la regola chiedeva di stare sotto tutti.
- **Che cosa si evita:** quasi tutto l'effetto è *qo*-. Due righe consecutive che cominciano entrambe con *qo*- sono 17
  contro 66,9 attese (un quarto); *da*- 14 contro 20,8; gli altri inizi sono vicini all'atteso.
- **Lettura:** *qo*- è normale a inizio riga (e393), ma due *qo*- uno sotto l'altro sul margine sinistro quasi non ci
  sono. L'inizio della riga potrebbe dipendere dall'**inizio** della riga sopra (sul margine), mentre non dipende dalla
  sua fine (e393). Verifica nell'e3a26.

## 4/10/2026 (notte) — e3a26: a inizio riga qo- evita il qo- della riga subito sopra (margine sinistro)

Preregistrato (`preregistrazioni/e3a26.md`). Prime parole *qo*/*o* + gallows, righe dalla seconda del paragrafo in poi.

| condizione | eventi (sì / no) | Δ P(*qo*) | z |
|---|---|---|---|
| la riga subito sopra comincia con *qo*- | 57 / 482 | **−0,518** | **−6,7** |
| la riga 2 sopra comincia con *qo*- | 110 / 294 | +0,166 | 0,9 |
| la riga 3 sopra comincia con *qo*- | 63 / 239 | −0,004 | −0,8 |
| la riga subito sopra finisce in -*y*/-*o*/-*d* (contro -*n*/-*r*/-*s*/-*m*) | 284 / 269 | +0,059 | 1,2 |

- **Esito preregistrato: qo- a inizio riga evita il qo- subito sopra** (niente alternanza: a distanza 2, z 0,9).
- **Lettura:** a inizio riga lo scriba guarda il margine sinistro della riga sopra, non la sua fine. Se lì c'è *qo*-,
  scrive *o*-: due *qo*- uno sotto l'altro quasi non ci sono. A destra invece non c'è niente del genere (e3a24: nessuna
  rima e nessun evitamento fra le parole finali). È un legame **verticale**, solo sul margine sinistro e solo con la riga
  subito sopra, come un "non ripetere lo stesso inizio".

## 4/10/2026 (notte) — e3a27: il qo- evitato sul margine sinistro regge con Takahashi e in tutte e due le lingue

Preregistrato (`preregistrazioni/e3a27.md`). Misura dell'e3a26 (la riga subito sopra comincia con *qo*-).

| prova | eventi (sì / no) | Δ P(*qo*) | z | esito |
|---|---|---|---|---|
| trascrizione IT (Takahashi) | 57 / 472 | −0,499 | −6,8 | regge |
| ZL, lingua A | 28 / 230 | −0,620 | −5,0 | regge |
| ZL, lingua B | 26 / 250 | −0,405 | −4,7 | regge |

- **Esito preregistrato: regge in tutte e tre le prove.** Il legame verticale sul margine sinistro non dipende dalla
  trascrizione né dalla lingua.

## 4/10/2026 (notte) — e3a28: sul margine sinistro lo stesso inizio si evita; nelle colonne interne sembra ripetersi (nullo da rifare)

Preregistrato (`preregistrazioni/e3a28.md`). 2.200 coppie di righe consecutive con almeno 5 parole (dalla seconda riga
del paragrafo). Nullo: ordine delle parole rimescolato dentro le due righe.

| colonna | stessi primi 2 segni: osservata / nullo | rapporto | z | parola uguale: rapporto | z |
|---|---|---|---|---|---|
| 1 (margine sinistro) | 0,035 / 0,077 | **0,45** | **−7,7** | 0,62 | −1,9 |
| 2 | 0,112 / 0,077 | 1,44 | 6,3 | 1,75 | 3,7 |
| 3 | 0,100 / 0,077 | 1,29 | 4,0 | 1,06 | 0,3 |
| 4 | 0,100 / 0,077 | 1,29 | 4,0 | 1,70 | 3,4 |
| ultima | 0,078 / 0,077 | 1,01 | 0,2 | 1,02 | 0,1 |

- **Esito preregistrato:** colonna 1 "evita la stessa colonna"; colonne 2–4 "ripete nella stessa colonna"; ultima
  "indifferente". "Solo il margine sinistro" (fra le evitate): sì.
- **Cautela sul nullo per le colonne interne:** rimescolando tutta la riga, le parole di bordo (con i loro inizi
  speciali, *s*-, *y*-, *d*-) finiscono nelle colonne interne e abbassano la somiglianza attesa lì. L'eccesso delle
  colonne 2–4 può venire in parte da questo. Si rifà con un nullo che rimescola solo le parole interne (e3a29). Per la
  colonna 1 il dubbio va nell'altro verso: le prime parole condividono gli inizi speciali, quindi l'evitamento è
  prudente (e confermato dall'e3a25 con un nullo diverso).

## 4/10/2026 (notte) — e3a29: con i bordi fermi le colonne interne non ripetono; resta solo l'evitamento sul margine sinistro

Preregistrato (`preregistrazioni/e3a29.md`). Come l'e3a28, ma il nullo rimescola solo le parole interne (prima e ultima
ferme).

| colonna | stessi primi 2 segni: rapporto | z | esito | parola uguale: rapporto | z |
|---|---|---|---|---|---|
| 2 | 1,25 | 3,6 | ripete | 1,37 | 2,1 |
| 3 | 1,11 | 1,7 | indifferente | 0,83 | −0,9 |
| 4 | 1,11 | 1,7 | indifferente | 1,32 | 1,7 |
| penultima | 1,03 | 0,5 | indifferente | 0,99 | −0,1 |

- **Esito preregistrato:** colonna 2 "ripete" (di poco), colonne 3, 4 e penultima "indifferente".
- **Correzione della lettura dell'e3a28:** l'eccesso nelle colonne interne veniva in gran parte dal nullo. Con i bordi
  fermi resta solo un lieve eccesso in colonna 2, che può venire dalle forme di posizione della seconda parola (e337). La
  copia dalla riga sopra non segue la colonna, come diceva l'e345.
- **Resta l'unico effetto verticale vero:** sul margine sinistro due righe consecutive evitano di cominciare allo stesso
  modo, soprattutto con *qo*- (e3a25–e3a27).

## 4/10/2026 (notte) — e3a30: al confine fra parole le "vocali" e le "consonanti" di Sukhotin si alternano, come nelle lingue

Preregistrato (`preregistrazioni/e3a30.md`). Classi di Sukhotin ricavate dentro le parole; quota di coppie di parole
vicine con ultimo e primo segno di classe diversa, contro le parole rimescolate nella riga (A = osservata / nullo).

- **Voynich:** A **1,086** (z 20,8). "Vocali" di Sukhotin: *a*, *c*, *e*, *h*, *n*, *o*, *u*, *y* (*c* e *h* sono i
  segni isolati, rari).
- **Gibberish umano:** A 1,011 (z 1,3).
- **Testi sensati:** A da 0,935 a 1,158, mediana 1,018. Sopra il Voynich: inglese tecnico 1,158, volapük 1,110, greco
  tecnico 1,107, francese 1,089. Il francese moderno 1,079, l'inglese moderno 1,071.
- **Esito preregistrato: il confine alterna come le lingue** (4 testi su 71 con A maggiore).
- **Lettura:** l'alternanza "vocale/consonante" fra la fine di una parola e l'inizio della seguente, misurata con classi
  ricavate senza guardare il confine, è nel Voynich forte quanto nelle lingue che più la mostrano (francese, inglese), e
  assente nel gibberish umano. Va con le regole di raccordo (e380, e390). Non dice quali suoni siano.

## 4/10/2026 — vz: e411, profilo di pagina e gradiente: due pezzi che non passano, e un difetto del metro (il Voynich stesso perde il gradiente)



Chat del voynichizzatore. Preregistrato (`preregistrazioni/e411.md`). Risultati in `risultati/e411_profilo_gradiente.md`. Semi 1–4, corpo senza messaggio; riferimento G2 dell'e410 (corpo della v11): 0,552 / 0,616, pagella 15,8, cancello 3/4.



| strato | AUC e231 | AUC e266 | pagella | cancello | profilo pagina R per seme (fascia 0,8–1,25) | gradiente per seme (fascia 0,70–0,97) |

|---|---|---|---|---|---|---|

| H1, carattere di pagina per posizione nella parola (κ 0,606) | 0,591 | 0,644 | 16,2/18 | 3/4 | 0,79, 0,73, 0,83, 0,83 | 0,56, 0,58, 0,56, 0,60 |

| H2, + vicinato fra righe (peso 4) | 0,689 | 0,780 | 14,2/18 | 0/4 | 0,75, 0,73, 0,79, 0,84 | 0,20, 0,20, 0,21, 0,20 |



- **H1 non passa:** il profilo pagina migliora (R da 0,66 a 0,80 circa) ma è in fascia solo in 2 semi su 4 (ne servivano 3), e i giudici peggiorano di 0,039 / 0,028. Dividere il carattere per posizione rende la pagina tipo più rumorosa (un terzo dei conteggi per posizione).

- **H2 è sbagliato come pezzo, e la previsione era sbagliata:** premiare la somiglianza con le parole delle righe sopra e sotto ammucchia le parole simili nelle stesse righe (somiglianza nella riga da 0,046 a 0,09) e allontana le righe distanti (0,026 → 0,018): il gradiente crolla a 0,20, i giudici salgono a 0,69 / 0,78 e il cancello si perde. Scartato.

- **Difetto del metro (trovato regolando H2).** Misurato con `e251.pagella_grezza`, il Voynich vero ha somiglianza nella riga 0,0385 e a 6 righe 0,0262: gradiente **0,683, sotto la fascia (0,70)**. Il riferimento usato per fissare la fascia (0,0335 a 6 righe) viene da un'altra suddivisione in pagine. Con questo metro il Voynich prende **17 materie su 18** (lo mostrava già l'e400: V = 17/18): la materia "gradiente" è mal posta e il massimo per seme è 17. Il corpo della v11 ha 0,0457 nella riga e 0,0266 a 6 righe: le righe lontane sono a posto, è la somiglianza nella riga a essere alta del 19% (effetto dei termini del cancello); anche portandola a 0,0385 il gradiente resterebbe fuori fascia come nel Voynich.

- **Altri riferimenti che non coincidono con la misura diretta sul Voynich** (pagella → misurato): somiglianza nella riga sotto 0,0399 → 0,0387; profilo pagina R 1,017 → 1,059, quota 0,0605 → 0,0514; formule 5,20 → 6,39; verticale 1,028 → 1,026. Vanno ricordati quando si legge "materia persa per poco".

- **Esito secondo la preregistrazione:** nessuno dei due pezzi si tiene; la versione migliore con il cancello resta la **v11**. Lacuna dichiarata sul profilo pagina (secondo tentativo dopo il carattere senza posizione): R circa 0,7–0,8 contro la fascia 0,8–1,25.

## 4/10/2026 (notte) — e3a32: l'alternanza "vocale/consonante" si comporta come la giuntura

Preregistrato (`preregistrazioni/e3a32.md`). Classi di Sukhotin ricavate dentro le parole di ciascuna trascrizione
("vocali" IT: *a*, *c*, *e*, *n*, *o*, *y*; ZL: *a*, *c*, *e*, *h*, *n*, *o*, *u*, *y*).

| prova | coppie | A | z |
|---|---|---|---|
| IT (Takahashi), nella riga | 29.477 | 1,092 | 20,1 |
| ZL, a capo | 3.337 | 1,008 | 0,6 |
| ZL, al salto del disegno | 740 | 1,040 | 1,2 |

- **Esito preregistrato: l'alternanza si comporta come la giuntura.** Si ripete con un'altra trascrizione e sparisce
  all'a capo e al salto del disegno.

## 4/10/2026 (notte) — Esplorativo: di che cosa è fatta la giuntura nei testi in cerchio

Non preregistrato (scratchpad). Nei cerchi e raggi (E 0,173, z 24,5) le coppie che contano di più sono -*r* *a*-
(+0,052), -*s* *a*- (+0,033), -*y* *d*- (+0,023), -*n* *o*- (+0,021), -*y* *ch*- (+0,013), -*l* *ch*- (+0,008). Senza
*qo*-, dopo -*y* vengono *d*- e *ch*- (che nei paragrafi dopo -*y* sono evitati in favore di *q*-), e pesano di più i
raccordi delle parole spezzate (*or aiin*, *s aiin*). Stessa forza, composizione diversa.
