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
