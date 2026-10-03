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
