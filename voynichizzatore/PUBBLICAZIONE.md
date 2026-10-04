# Nota per la pubblicazione del voynichizzatore

Scritta il 4/10/2026 dalla chat del voynichizzatore, per Davide. **Non è stato pubblicato niente.** Questa nota dice
che cosa servirebbe in un repo pubblico separato, quali pezzi derivano dalla trascrizione, e che cosa va controllato
prima. Le decisioni sono di Davide.

## 1. Che cosa si pubblicherebbe

Lo strumento, nella versione verificata al banco (oggi v10 o v11; vedi `STATO_LAVORI.md`):

- gli si dà un testo e una parola chiave; scrive un manoscritto intero in EVA con l'impaginazione del Voynich;
- con la chiave il testo torna esatto; con la chiave sbagliata non si legge niente;
- capacità circa 80.000 bit per libro (circa 20.000 caratteri di testo latino dopo la compressione).

## 2. I file che servono

| che cosa | file in questo repo |
|---|---|
| strumento da riga di comando | `voynichizzatore/voynichizzatore.py`, `versioni.py` |
| generatore a pezzi | `voynichizzatore/pezzi.py`, `sacco.py`, `parole_nuove.py`, `disposizione.py`, `pezzi_parametri_v10.json`, `pezzi_parametri_v11.json` |
| nascondiglio | `voynichizzatore/canale_sacco.py`, più da `v0.py` e `v1.py` solo: chiave → numero, flusso della chiave, bit, codifica aritmetica, salva/carica |
| pezzi di parola e legami | `voynichizzatore/modello.py` (solo `legami`), `esperimenti/e249_pezzi_simboli.py` (`segmentatore`), `esperimenti/e285_pezzi_contesto.py` (`parti`) |
| scelte di grafia nella riga | `esperimenti/e135_stato_riga.py` (`occorrenze`), `esperimenti/e145_abitudini.py` (`SCELTE`), `esperimenti/e206_segni_facoltativi.py` (`classi_di`), `risultati/e206b_facoltativi_strati.json` (i nomi delle 12 classi) |
| lettura della trascrizione | `analisi/trascrizione.py`, `analisi/misure.py` (divisore dei segni EVA, distanza fra parole) |
| dipendenze | Python 3.12, `numpy`, `scipy`, `scikit-learn` (per l'affinità parola-posto) |

Non servono, e non vanno portati: i giudici, la pagella, gli esperimenti, il QUADERNO, il dossier, `dati/cache`.

## 3. Il punto delicato: i dati che vengono dalla trascrizione

Oggi il programma **legge la trascrizione ZL a ogni avvio** (`dati/cache/trascrizioni/ZL3b-n.txt`) e ne ricava al volo
tutte le statistiche. Un repo pubblico ha due strade:

**Strada A — non ridistribuire niente.** Il repo pubblico contiene solo il codice; chi lo usa scarica da sé la
trascrizione dal sito di origine con uno script (come fa `prepara.py` qui). È la strada che non richiede nessun
permesso, ed è quella che consiglio se le licenze non sono chiare. Costo: il programma non funziona "da solo" e non
può diventare un sito senza che il sito stesso tenga una copia della trascrizione.

**Strada B — ridistribuire le statistiche già calcolate.** Il repo contiene un file di statistiche al posto della
trascrizione. Va saputo che cosa c'è dentro, perché **non sono numeri astratti**:

| statistica | che cosa contiene davvero | quanto è vicina al testo |
|---|---|---|
| impaginazione | per ogni pagina: sezione, lingua, numero di righe, parole per riga, inizi di paragrafo | struttura, niente parole |
| lessico per sezione e lingua | **l'elenco di tutte le parole viste almeno due volte, con quante volte compaiono in ogni sezione e lingua** (e, per escludere ogni pagina da sé stessa, i conteggi per pagina) | molto vicina: con i conteggi per pagina si ricostruisce il contenuto di ogni pagina senza l'ordine |
| caratteri di pagina | frequenze dei segni di ogni pagina, per posizione nella parola | derivata, non ricostruisce il testo |
| forme delle parole uniche | tabelle di tre e quattro segni di seguito, contate sulle parole che compaiono una volta sola, e le loro lunghezze | derivata; l'elenco delle parole uniche serve però per non ridarle (basta un'impronta, non le parole) |
| affinità parola-posto | pesi di una regressione sui tratti delle parole | derivata |
| legami fra vicine | tabelle di rapporti fra pezzi di parole; conteggi delle coppie di parole vicine per pagina | le coppie per pagina sono vicine al testo |

Per la strada B si può ridurre l'esposizione: conteggi per sezione e lingua invece che per pagina (va verificato
quanto costa in riconoscibilità: oggi ogni pagina esclude sé stessa), impronte al posto dell'elenco delle parole
uniche, niente conteggi delle coppie per pagina (il loro peso nel modello è già zero nelle v10 e v11).

## 4. Che cosa va controllato prima (non l'ho fatto io)

1. **La licenza della trascrizione ZL** (Zandbergen–Landini, versione 3b, dal sito di René Zandbergen): `dati/FONTI.md`
   registra da dove viene e l'impronta del file, e dice che le copie restano fuori dal repo "per rispetto dei
   diritti". Va letto sul sito che cosa è permesso (uso, ridistribuzione, opere derivate) o va chiesto all'autore.
   Finché non è chiaro vale la strada A.
2. **Il codice di terzi:** i moduli elencati sopra sono scritti in questo progetto; nessuno dei generatori esterni
   citati in `dati/FONTI.md` (Timm e Schinner, Gaskell e Bowern) entra nel voynichizzatore. Da ricontrollare al
   momento di copiare i file.
3. **Le immagini:** il voynichizzatore oggi produce solo testo EVA. L'uscita come immagine (prevista dal progetto)
   non esiste ancora; quando ci sarà andranno controllate le licenze del font o dei ritagli.
4. **Che cosa si dichiara.** Numeri verificati al banco e limiti, come sono nel `QUADERNO.md`: "indistinguibile" vale
   per i due giudici e la pagella di questo progetto, i pesi del modello sono regolati sulle statistiche che quei metri
   guardano, e un giudice indipendente non è ancora stato provato.
5. **La cifratura:** il messaggio è cifrato con un flusso derivato dalla chiave con SHA-256 e il generatore casuale di
   Python. Basta a non far vedere il messaggio ai nostri metri, **non è crittografia robusta**: il progetto prevedeva
   scrypt e un'etichetta di autenticazione, non ancora fatti. Va scritto chiaro, o va fatto prima di pubblicare.
6. **Riproducibilità fra macchine:** codifica e decodifica usano probabilità in virgola mobile; sono state provate
   solo su questa macchina. Prima di pubblicare va provato che un manoscritto scritto su un computer si rilegga su un
   altro.

## 5. Che cosa preparerei, se Davide dice di sì

- uno script che estrae le statistiche (strada B) o che scarica la trascrizione (strada A);
- un modulo unico senza dipendenze dagli esperimenti (oggi il generatore importa pezzi da `esperimenti/`);
- un README con i numeri del banco, i limiti del punto 4 e le istruzioni d'uso;
- la prova di andata e ritorno su una seconda macchina.

## 6. Aggiornamento del 4/10 mattina: che cosa dice il sito sulla licenza (da ricontrollare a mano)

Letto attraverso un riassunto automatico della pagina, non riga per riga:

- la pagina delle trascrizioni (voynich.nu/transcr.html) non dichiara condizioni, rimanda alla pagina sul diritto
  d'autore del sito (voynich.nu/roadmap.html, sezione "Copyright");
- quella sezione dice che il materiale del sito si puo' usare liberamente, chiede di citare la fonte, e che le
  trascrizioni del testo del Voynich sono messe a disposizione **secondo la licenza Creative Commons CC0** (pubblico
  dominio: copia e opere derivate senza limiti);
- eccezione: il font "Voynich Eva Hand 1" e' di Gabriel Landini e non si puo' usare a fini commerciali (riguarda la
  futura uscita come immagine, non il testo EVA);
- il repo da cui vengono le nostre copie (Krymorn/The-Voynich-Transliteration-Tool) e' sotto licenza MIT per il suo
  codice e dice che le trascrizioni restano dei loro autori.

Se la lettura a mano conferma il CC0, la strada B (codice piu' statistiche) e' aperta, citando Zandbergen e Landini.
Decisione di Davide del 4/10 (provvisoria, poi sospesa): pubblicare la v12 con codice piu' statistiche e cifratura
robusta; alle 6:10 ha rimandato le decisioni al mattino dopo e chiesto di continuare a migliorare la v12.

## 7. Licenza riletta a mano (4/10, 8:40) e decisione di Davide

Aperta la pagina https://www.voynich.nu/roadmap.html, sezione "Licences and copyright", e letto il testo (non un
riassunto). Dice, in sostanza:

- il materiale del sito si puo' usare liberamente; si chiede di citare la fonte e, se possibile, di mettere un
  collegamento al sito;
- le trascrizioni del testo del Voynich raccolte nelle tabelle del sito vengono da fonti diverse, sono sempre state di
  pubblico dominio e sono messe a disposizione sul sito secondo la licenza Creative Commons CC0;
- il font "Voynich Eva Hand 1" e' di Gabriel Landini e non va usato a fini commerciali (non ci riguarda finche' l'uscita
  e' solo testo EVA).

**Conferma: la strada "codice piu' statistiche" e' aperta.** Da fare comunque nel repo pubblico: citare Rene' Zandbergen
e Gabriel Landini e il sito voynich.nu come fonte della trascrizione ZL (versione 3b del 13/05/2025), con il collegamento.
Cautele: e' la dichiarazione del curatore del sito, non un parere legale; la nostra copia viene da un repo che la
ridistribuisce (stessa impronta SHA-256 dell'originale, vedi dati/FONTI.md).

**Decisione di Davide (4/10, 8:40): si pubblica la v14.**

## 8. Stato del pacchetto (4/10, 9:50)

- Versione scelta da Davide: **v17**. Il pacchetto si ricostruisce con `.venv/Scripts/python strumenti/costruisci_pubblico.py`
  e sta in `pubblico/voynichizzatore/` (17 file, circa 480 KB, quasi tutti nel file del testo).
- Fatto: dati al posto della trascrizione (§3: si è scelto di includere il testo corrente ripulito, visto il pubblico
  dominio, invece di statistiche astratte: garantisce gli stessi risultati del repo); cifratura robusta; programma che
  non dipende dal resto del repo; istruzioni con i numeri e i limiti (`LEGGIMI.md`).
- Non fatto: licenza del programma; prova di rilettura su un secondo computer; giudice indipendente; uscita come
  immagine; pagina web.
- **Niente è stato pubblicato:** creare il repo pubblico e caricarlo richiede il via esplicito di Davide.

## 9. Pubblicato (4/10, 10:45)

Repo pubblico: https://github.com/AndreottiVIII/voynichizzatore (v17, licenza MIT, istruzioni e messaggi in inglese).
Copia di lavoro locale: `C:\Users\davide\voynichizzatore`. Come aggiornarlo: vedi il diario, voce delle 10:45.
In sospeso: prova di rilettura su un altro computer; descrizione del repo in inglese; giudice indipendente; sito web.
