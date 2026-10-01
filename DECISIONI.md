# Registro delle decisioni

Una voce per ogni scelta di metodo che può cambiare un risultato o il modo di leggerlo.
Formato: contesto, opzioni considerate, scelta, motivo. Le voci non si riscrivono: se una
decisione cambia, se ne aggiunge una nuova che rimanda alla vecchia.

Le decisioni prese nella fase precedente (settembre 2026, repo `duri-a-morire`) sono
riassunte nel `DOSSIER_WHITE_PAPER.md`, sezione 3.2; qui cominciano quelle della fase nuova.

---

## D-001 — Nessuna conversione dei fine riga (30/09/2026)

- **Contesto.** Il lavoro ora gira su Windows, dove git è configurato a livello di sistema con
  `core.autocrlf=true`. Il checkout del vecchio repository ha trasformato LF in CRLF in 66 file
  su 128. Le impronte SHA-256 delle trascrizioni non coincidevano più con quelle pubblicate, e
  le lunghezze dei testi (quindi i numeri) sarebbero cambiate.
- **Opzioni.**
  - Lasciare la conversione e ricalcolare le impronte.
  - Disattivarla nel repository (`.gitattributes: * -text`).
  - Disattivarla anche per i corpora scaricati da `prepara.py`.
- **Scelta.** Disattivarla ovunque:
  - `.gitattributes` con `* -text`;
  - `core.autocrlf=false` e `core.eol=lf` passati a git per ogni download (in `esegui.py` e a mano
    per `prepara.py`).
- **Motivo.** I dati devono essere gli stessi byte, su ogni sistema operativo. Verifica:
  - i 128 file importati coincidono con i blob originali (`git hash-object`);
  - le tre trascrizioni hanno le impronte di `dati/FONTI.md`.

## D-002 — Esecuzione a condizioni fissate (30/09/2026)

- **Contesto.** Alcuni risultati dipendono da dettagli dell'ambiente che non si vedono nel
  codice:
  - l'ordine di iterazione dei `set` di stringhe dipende dal seme di hash di Python, casuale a
    ogni avvio;
  - su Windows Python scrive i file di testo con CRLF e usa una codifica diversa da UTF-8.
- **Scelta.** Ogni esperimento si lancia con `esegui.py`, che:
  - fissa `PYTHONHASHSEED=0` e `PYTHONUTF8=1`;
  - riporta a LF i file scritti in `risultati/`;
  - mette il JDK nel `PATH`.
- **Motivo.** Due esecuzioni sullo stesso commit devono dare gli stessi byte. È la condizione
  perché un confronto fra versioni sia informativo.

## D-003 — La provenienza in un file a parte (30/09/2026)

- **Contesto.** Il piano prevedeva di aggiungere un blocco di provenienza dentro ogni
  `risultati/eNN.json`: commit, impronte dei dati, versioni.
- **Opzioni.**
  - Blocco dentro il `.json`.
  - File a parte in `risultati/provenienza/`.
- **Scelta.** File a parte: `risultati/provenienza/eNN.json`, più il log completo in `eNN.log`.
- **Motivo.** Così il `.json` dei risultati resta confrontabile byte per byte con quello della
  fase precedente, e `git diff risultati/` è già la prova della replica. Un blocco con data e
  durata renderebbe ogni file sempre "diverso".

## D-004 — Dipendenze: ultime versioni, fissate (30/09/2026)

- **Contesto.** Il vecchio `requirements.txt` non fissava le versioni, e il vecchio repository
  non registrava quelle usate.
- **Scelta.**
  - Ambiente virtuale `.venv` con Python 3.12.10.
  - Pacchetti alle ultime versioni del 30/09/2026, fissati in `requirements.txt`.
  - Aggiunti `scipy` e `scikit-image`, per le misure sulle immagini.
- **Motivo.** Non si può ricostruire l'ambiente originale. La replica dirà se le differenze di
  versione cambiano qualcosa; se sì, lo scarto si documenta nel quaderno.

## D-005 — e29 riformulato, e36–e38 anticipati (30/09/2026)

- **Contesto.** L'e29 del piano chiedeva se la somiglianza di vocabolario fra pagine dipende dal
  tipo di illustrazione oltre che da fascicolo, mano e lingua di Currier. Progettandolo nel
  dettaglio è emerso un difetto: nel manoscritto il tipo di illustrazione coincide quasi con la
  posizione (le sezioni stanno in fascicoli contigui). Uno scriba che produce testo senza
  messaggio per sessioni, una sezione dopo l'altra, darebbe anche lui un "effetto sezione". E
  l'ordine vero di scrittura non si conosce, perché la rilegatura ha mescolato i bifogli. Il test
  quindi non separa l'ipotesi 3 dalle altre.
- **Opzioni.**
  1. Eseguirlo comunque, dichiarandone il limite.
  2. Riformularlo su coppie di pagine legate dal **contenuto ma lontane** (la stessa pianta
     nell'erbario e nella farmacia; i due Ariete e i due Toro dello zodiaco), guardando le parole
     rare in comune. Un testo senza messaggio non ha motivo di ripetere parole rare proprio lì.
  3. Abbandonarlo.
- **Scelta.** La 2. Richiede però l'elenco delle corrispondenze fra disegni, quindi le immagini:
  si fa insieme all'e35. Nel frattempo si anticipano e36, e37 ed e38 (lingue filosofiche), che
  usano solo la trascrizione e hanno previsioni che separano le ipotesi.
- **Motivo.** Un test che dà lo stesso esito sotto tutte le ipotesi costa tempo e non informa.

## D-006 — Misura comune per e36–e38: l'informazione per posizione (30/09/2026)

- **Contesto.** Le tre prove chiedono **dove** sta, dentro la parola, l'informazione sul gruppo a
  cui la parola appartiene: la pagina (e36), la sezione (e37), la categoria del glossario (e38).
- **Scelta.** Per ogni posizione della parola (primo, secondo, penultimo e ultimo segno; parole di
  almeno 4 segni, segni composti fusi) si calcola:
  - l'informazione mutua fra il gruppo e il segno in quella posizione;
  - a cui si sottrae la media di 200 rimescolamenti delle parole fra i gruppi, a seme fisso,
    dentro lo stesso strato;
  - divisa per l'entropia del segno in quella posizione.
  - Il profilo si riassume in R = quota al primo segno / media delle quote al penultimo e
    all'ultimo.
- **Alternative scartate.** La distanza di edit per posizione, come nell'e04: dipende dalla
  lunghezza e mescola posizioni vicine. L'informazione mutua non corretta: è distorta verso
  l'alto con molti gruppi piccoli; il rimescolamento corregge questa distorsione e dà anche il
  livello del caso.
- **Esclusioni.** Si scartano la prima e l'ultima parola di ogni riga e le righe che aprono un
  paragrafo, perché hanno statistiche proprie (i gallows a inizio paragrafo, gli effetti di inizio
  e fine riga). Nei controlli si escludono le stesse posizioni.

## D-007 — Deviazione dalla preregistrazione di e36: il controllo positivo (30/09/2026)

- **Contesto.** Una prova del codice di e36 fatta prima della corsa ufficiale (i numeri sono nel
  quaderno) ha mostrato un difetto del controllo positivo così come l'avevo preregistrato.
  - Dentro ogni categoria le parole erano numerate nell'ordine in cui compaiono nel testo.
  - Così le parole viste per la prima volta sulla stessa pagina ricevono numeri vicini, e la prima
    cifra del numero (il secondo segno) porta informazione sulla pagina: quota 0,089 al secondo
    segno contro 0,051 al primo.
  - Per il criterio preregistrato ("quota_primo la più alta") il controllo fallisce, ma per una
    ragione che non riguarda il metodo.
- **Scelta.**
  - Nella corsa ufficiale si riportano **due** versioni del controllo: quella preregistrata
    (numerazione per prima comparsa) e una corretta, in cui la numerazione dentro la categoria
    segue l'ordine alfabetico della parola latina e non ha legami con la pagina.
  - Il criterio di validità si applica alla versione corretta; l'esito della preregistrata si
    riporta com'è.
  - Nella prova ho visto anche il profilo del Voynich; le soglie per il Voynich **non** cambiano.
- **Motivo.** Correggere un controllo difettoso è necessario. Farlo in silenzio dopo aver visto i
  dati no: per questo si dichiara e si riportano entrambe le versioni.

## D-008 — Il pinyin resta nel profilo dell'e13; la frase sull'isolamento si corregge (30/09/2026)

- **Contesto.** Nella replica l'e13 include una lingua in più, il cinese in pinyin scritto una
  sillaba per parola. Il vecchio e13 la escludeva solo perché il vecchio `e01_prevedibilita.json`
  era stato prodotto prima dell'aggiunta del pinyin al corpus: un'esclusione per caso, non una
  scelta. Il pinyin risulta la lingua più isolata (6,64 dalla sua vicina; tutte le altre ≤ 4,0,
  la seconda è il q'eqchi' con 4,0).
- **Opzioni.**
  1. Escluderlo, perché è la trascrizione di una scrittura logografica.
  2. Tenerlo, perché il corpus lo include di proposito dall'e19 e rappresenta una lingua isolante.
- **Scelta.** Tenerlo, e riportare anche la distanza della seconda lingua più isolata.
- **Motivo.** Una lingua monosillabica e isolante è proprio il tipo di confronto che serve per
  un testo con parole corte e ripetitive. Escluderla perché scomoda sarebbe una scelta fatta
  dopo aver visto il risultato.
- **Formulazione per il white paper** (sostituisce quella del dossier, sezione 4.1):
  - con tutte e nove le misure il Voynich dista 9,2 dalla lingua più vicina, più di qualsiasi
    lingua (massimo 6,6, il pinyin);
  - senza l'omogeneità di pagina dista 4,4: più di ogni lingua salvo il pinyin (6,6).

## D-009 — Replica parziale degli esperimenti di ore (30/09/2026)

- **Contesto.** e17, e19 ed e20 richiedono ore di calcolo con 4 processori.
- **Scelta.**
  - e17 si replica su latino, italiano ed ebraico (`LINGUE_SOLO=Latin,Italian,Hebrew`). Latino e
    italiano sono i riferimenti di tutto il lavoro; l'ebraico era il punto più alto del Voynich
    (0,42), cioè il caso in cui una differenza conterebbe di più.
  - e19 ed e20 per ora non si replicano. Usano lo stesso risolutore dell'e17: se l'e17 si replica,
    il risolutore è verificato.
- **Motivo.** Il tempo di calcolo va agli esperimenti nuovi. La replica parziale si dichiara come
  tale nel white paper.

## D-010 — Niente misura dell'inchiostro delle etichette, per ora (30/09/2026)

- **Contesto.** Per distinguere "classe marcata" da "lotti di scrittura" (e40, e42) avevo
  proposto di misurare l'inchiostro delle etichette sulle immagini: etichette scritte in sedute
  diverse dovrebbero avere tono e densità diversi. Serve sapere dove sta ogni etichetta sulle
  immagini IIIF.
- **Prova (e45).** I riquadri di voynichese.com non si portano sulle immagini con una
  trasformazione semplice:
  - nei paragrafi si sovrappongono fra righe diverse; sono una disposizione approssimata, adatta a
    confrontare spazi dentro la stessa riga, non a localizzare le parole;
  - per le etichette, con un affinamento locale di ±30 pixel, circa metà cade sull'inchiostro
    giusto e le altre su tratti dei disegni (controllo a vista su f99r).
- **Opzioni.**
  1. Procedere lo stesso.
  2. Segnare a mano i riquadri delle circa 190 etichette della farmacia.
  3. Rinviare.
- **Scelta.** Rinviare. Una misura con metà delle etichette nel posto sbagliato darebbe un
  risultato senza significato; la segnatura a mano è possibile, ma lunga e da fare con un
  protocollo cieco.
- **Motivo.** Meglio un vicolo cieco documentato che un numero sbagliato. Le 213 immagini restano
  scaricate e registrate (e33), e l'allineamento è in `analisi/immagini.py` per chi riprenderà.

## D-011 — e68: il filtro di forma non si applica alle parole d'inizio riga (1/10/2026)

- **Contesto.** Con η = 1 il generatore si bloccava: il filtro, tarato sui segni iniziali di tutte
  le parole, rifiutava quasi tutte le parole d'inizio paragrafo. Queste per convenzione cominciano
  con i gallows (p-, t-, k-, f-), rari altrove.
- **Scelta.** Il filtro non si applica alle parole d'inizio riga, che hanno una distribuzione
  propria, come già nelle esclusioni di D-006.
- **Motivo.** È una deviazione dalla preregistrazione nata da un blocco tecnico, non dai risultati.
  Si rieseguono tutti i valori di η con la correzione; con η = 0 il controllo di validità resta lo
  stesso.

## D-012 — Diciottesima proprietà della pagella: il bordo di riga (1/10/2026)

- **Contesto.** Nell'e71 la distinzione del bordo di riga separa bene i testi:
  - Voynich: 23 all'inizio, 55 alla fine (rapporti con il nullo);
  - prosa mandata a capo: 1–5;
  - generatori: 10–13 all'inizio e 129–188 alla fine.
  - La preregistrazione diceva di aggiungerla alla pagella se i generatori non la riproducono.
- **Scelta.** La proprietà "bordo di riga" si considera riprodotta se entrambi i rapporti
  (inizio e fine) stanno fra 0,5 e 2 volte quelli del Voynich. Le righe d'inizio paragrafo sono
  escluse come nell'e71.
- **Motivo.** La banda è decisa dopo aver visto i dati, come le altre della pagella (e61): vale
  per i confronti futuri, non come prova. Il fattore 2 è lo stesso margine usato per altre bande
  di rapporto.

## D-013 — e78: deriva sui testi corti (1/10/2026)

- **Contesto.** La deriva (V2) è il ricambio a distanza 1 meno quello a distanza 20 blocchi di
  1.000 parole. I testi sanscriti dell'e78 hanno meno di 21.000 parole e l'esecuzione si è
  fermata (KeyError).
- **Scelta.** Per i testi corti si usa la distanza massima disponibile (≤ 20) e la si registra
  (`V2_distanza`). Il Voynich resta a 20.
- **Motivo.** È un blocco tecnico, non dipende dai risultati. Con una distanza più corta la deriva
  è sottostimata, quindi il confronto è prudente per i testi corti.
