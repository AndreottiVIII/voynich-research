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
