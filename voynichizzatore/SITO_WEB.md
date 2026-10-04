# Voynichizzatore: tutto quello che serve per costruire il sito

Scheda scritta il 4/10/2026 per la chat che costruirà il sito. È autosufficiente: non serve leggere altro.
Chi decide è Davide. Lingua di lavoro con Davide: italiano semplice. **Testi del sito: in inglese** (come il repo).

## 1. Che cosa fa il programma

- Prende **un testo qualsiasi** e **una chiave** (una frase lunga) e scrive un **manoscritto "alla Voynich"**: un libro
  intero di 207 pagine e circa 4.100–4.200 righe, in EVA (l'alfabeto latino con cui si trascrive il manoscritto Voynich,
  Beinecke MS 408).
- Con la **stessa chiave** il testo torna fuori **esatto**. Con una chiave sbagliata non esce niente.
- Il libro ha sempre la stessa lunghezza, qualunque sia il testo. Se il testo è corto il resto è riempito, e non si
  vede dove finisce il messaggio. Si può anche fare un libro **senza messaggio**.
- Il manoscritto si può avere in due vesti (**il sito deve offrirle tutte e due**, scelta di Davide):
  1. **testo EVA** (file `.txt`);
  2. **scrittura "voynichese"**, come **PDF del libro** (una pagina per pagina), con un carattere disegnato da noi.

## 2. Dove sta il codice

- Repo pubblico: **https://github.com/AndreottiVIII/voynichizzatore** (licenza MIT, versione v17, istruzioni in inglese).
- Il sito deve usare **quel repo così com'è**, senza cambiare gli algoritmi: ogni modifica al generatore rompe la
  rilettura dei manoscritti già fatti. Il generatore si sviluppa in un altro repo, privato, che il sito non deve toccare.
- Serve **Python 3.12** con `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `fonttools` (`pip install -r requirements.txt`).
  Il pacchetto pesa meno di 1 MB e contiene tutto, compreso il testo del Voynich (`voynich_zl3b.json`) e il carattere
  (`VoynichizzatoreEVA.ttf`). Non scarica niente da internet.

## 3. I quattro comandi

```
python voynichizzatore.py encode text.txt --key "a long passphrase" --out manuscript.txt
python voynichizzatore.py decode manuscript.txt --key "a long passphrase" --out text.txt
python voynichizzatore.py empty --key "a long passphrase" --out manuscript.txt
python voynichizzatore.py pdf manuscript.txt --out book.pdf
```

Si possono anche chiamare da Python, senza passare dalla riga di comando:

```python
import canale_sacco, v0, pagine
righe, info = canale_sacco.codifica(testo, chiave, 'v17')   # testo=None per il libro senza messaggio
v0.salva(righe, 'manuscript.txt')                            # info['bit_messaggio'], info['capacita_bit']
testo = canale_sacco.decodifica(v0.carica('manuscript.txt'), chiave, 'v17')   # ValueError se la chiave è sbagliata
pagine.pdf('manuscript.txt', 'book.pdf')                     # restituisce il numero di pagine
```

## 4. Numeri misurati (su un PC normale, 4/10/2026)

| operazione | tempo | uscita |
|---|---|---|
| `encode` (o `empty`) | **circa 2 minuti** (105 secondi) | file `.txt` di circa 260 KB |
| `decode` | circa 5 secondi | il testo |
| `pdf` | circa 10 secondi | PDF di 207 pagine, circa 0,6 MB |

- **Capienza:** circa 80.000 bit (cambia un po' con la chiave: 81.000–83.000), cioè più o meno **20.000 caratteri** di
  testo normale. Il testo viene compresso (zlib) prima, quindi il limite vero dipende dal testo. Se è troppo lungo il
  programma si ferma con `text too long for this book: it needs N bits, the book carries M`.
- La memoria usata non è stata misurata: va controllata prima di scegliere il server.
- Il risultato è **deterministico**: stesso testo e stessa chiave danno lo stesso manoscritto, su ogni computer
  (provato sullo stesso PC; la prova su un secondo PC è ancora da fare, vedi punto 9).

## 5. Formati

- **File del manoscritto (EVA):** UTF-8, righe di commento che iniziano con `#`, poi una riga per ogni riga del
  manoscritto: `<f1r.1> parola.parola.parola`. Le righe che aprono un paragrafo hanno `@` davanti: `@<f1r.1> ...`.
- **Il messaggio sta nel file EVA.** Per rileggere serve il file `.txt`. **Dal PDF non si può rileggere**: non esiste
  (ancora) un programma che torna dal PDF all'EVA. Quindi il sito, anche quando l'utente sceglie il PDF, deve sempre
  far scaricare anche il `.txt`, e dirlo chiaramente ("keep this file: it is the one you need to read the text back").
- **Il carattere** `VoynichizzatoreEVA.ttf`: i segni semplici stanno sulle lettere EVA minuscole; i segni composti
  `ch sh cth ckh cph cfh` sono segni a sé in codici privati (da U+E000). La conversione da parola EVA a segni la fa
  `carattere.in_segni(parola)`. Il font ha anche le legature automatiche, quindi usato come webfont dovrebbe mostrare
  bene il testo EVA scritto normalmente (da verificare nel browser). Così il sito può mostrare un'**anteprima in
  voynichese** direttamente nella pagina, con un pulsante "EVA / Voynichese".
- **Il PDF:** solo testo, fondo color pergamena, niente disegni. Ogni segno è sempre identico (non imita le variazioni
  della penna). Le poche righe molto lunghe sono scritte più strette.

## 6. Che cosa deve fare il sito (richiesta di Davide)

1. **Scrivere:** l'utente incolla un testo, dà una chiave, sceglie la veste (**EVA** oppure **voynichese in PDF**) e
   ottiene il manoscritto. Dare sempre anche il `.txt`.
2. **Leggere:** l'utente carica il `.txt`, dà la chiave e riottiene il testo.
3. (Facoltativo) libro senza messaggio; anteprima di una pagina in voynichese.

## 7. Scelte tecniche da fare (con consigli)

- **Scrivere dura 2 minuti:** non può essere una richiesta web normale. Serve un lavoro in coda (l'utente aspetta con
  una barra, o torna dopo), con un limite di lavori contemporanei e un limite per utente. Leggere e fare il PDF sono
  veloci e possono essere richieste normali.
- **Dove gira il calcolo.** Due strade:
  - **sul server** (Python vero): semplice e sicuro che funzioni; ma testo e chiave passano dal server. In quel caso:
    HTTPS, non salvare né scrivere nei log testo, chiave e manoscritti, cancellare i file appena consegnati, e dirlo
    nella pagina;
  - **nel browser** (Pyodide): testo e chiave non lasciano il computer dell'utente, che è la cosa migliore per la
    riservatezza; ma è più lento e **va provato**: il programma usa `hashlib.scrypt`, che in Pyodide potrebbe mancare,
    e il risultato deve essere identico bit per bit a quello del Python normale (provare con `python prova.py`).
  - Consiglio: partire dal server, e valutare il browser dopo.
- **Non cambiare versione delle librerie alla leggera:** la rilettura dipende dal fatto che il calcolo dia gli stessi
  numeri. `prova.py` nel repo serve proprio a controllarlo: va eseguito sul server prima di aprire il sito.
- **Limiti da mettere:** lunghezza del testo (circa 20.000 caratteri; mostrare il messaggio d'errore del programma),
  dimensione del file caricato (un manoscritto pesa circa 260 KB), chiave minima (consigliare una frase lunga).

## 8. Che cosa si può dire e che cosa NO (importante)

Si può dire:
- il testo torna esatto con la chiave; senza chiave non c'è niente da "tradurre" parola per parola (non c'è
  corrispondenza fra parole del manoscritto e parole del testo: il messaggio decide **quante volte** compare ogni parola
  in ogni pagina);
- un manoscritto con messaggio e uno senza **non si distinguono** con le nostre misure: è la stessa situazione del
  Voynich vero, per cui non si sa se un messaggio c'è;
- due "giudici" automatici che cercano di distinguere le pagine fatte da quelle vere danno 0,56 e 0,60 (0,5 = tirano a
  indovinare, 1 = non sbagliano mai), su 12 chiavi; pagella 15 su 17 proprietà note.

**Non** si può dire:
- **mai "indistinguibile dal Voynich"**: il secondo giudice lo riconosce ancora un po'; alcune proprietà non tornano;
  i giudici li abbiamo fatti noi e un giudice indipendente non è stato provato;
- **mai che il Voynich è stato decifrato**, né che è fatto così: il programma imita le statistiche, non spiega il
  manoscritto;
- non garantire la sicurezza come per un programma di cifratura vero: la cifratura è seria (scrypt, SHAKE-256, HMAC)
  ma non è stata verificata da esperti. Scrivere "do not use it for secrets that matter".
- La sezione del README "How close it is to the Voynich" contiene le frasi giuste, già in inglese: usare quelle.

## 9. Licenze e crediti da mettere nel sito

- Codice e carattere: **MIT**, autore Davide Caniatti.
- Testo del Voynich usato dal programma: trascrizione Zandbergen–Landini (ZL), di **pubblico dominio (CC0)**; si chiede
  di citarla: René Zandbergen, voynich.nu. La sezione "Sources" del README ha la dicitura completa.
- Il nostro carattere **non** è il font "EVA Hand 1" (che non è per uso commerciale): è disegnato da un programma nostro.
- **Non mettere immagini del manoscritto vero** nel sito senza controllare la licenza della fonte (Beinecke Library).
- L'email personale di Davide non va messa da nessuna parte; contatto: il repo GitHub.

## 10. Cose ancora aperte

- Prova di rilettura **su un altro computer** (`python prova.py`): non ancora fatta. Finché manca, non promettere che un
  manoscritto fatto sul sito si rilegge su qualunque PC.
- Difetto noto della v17: un po' troppe righe molto più lunghe delle altre (5,3% contro 2,9% del Voynich vero); nel PDF
  si vede. Verrà corretto in una versione futura.
- Versioni future: un manoscritto si rilegge **solo con la versione che l'ha scritto**. Il sito deve mostrare la
  versione (v17) e, quando ne arriverà una nuova, tenere la vecchia disponibile per leggere.

## 11. Scelte di Davide (4/10/2026, mattina)

- **Ospitare:** GitHub Pages, indirizzo gratuito `andreottiviii.github.io/voynichizzatore`; il dominio si compra dopo,
  se serve. Codice del sito nel repo pubblico `voynichizzatore`, cartella `docs/`; il programma non si tocca.
- **Calcolo:** prima la prova del browser (passo 0, fatta: §12). GitHub Pages non fa calcoli, quindi con il calcolo nel
  browser il sito costa zero.
- **Che cosa deve esserci:**
  - **Write**, semplice: si mette testo e chiave ed esce il manoscritto (EVA `.txt` sempre, PDF in voynichese);
    **mentre si aspetta, qualcosa di divertente**, tipo un amanuense che scrive;
  - **Read**, il decifratore: si carica il `.txt`, si dà la chiave, torna il testo;
  - **How it works**: il procedimento del generatore spiegato **passo per passo, in modo rigoroso ma comprensibile**, in
    una pagina a parte (non durante l'attesa);
  - **spazio per le ricerche** fatte sul Voynich (contenuto da decidere con Davide: il white paper si scrive solo
    quando lo dice lui).

## 12. Prova del browser (passo 0, 4/10/2026, 10:20–10:50)

Pacchetto v17 **senza modifiche** dentro Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0, scikit-learn
1.8.0, matplotlib 3.10.8), in un web worker, sul PC di Davide (i5-12600K, con l'e416 in esecuzione). Testo e chiave di
`prova.py`. File della prova nella cartella temporanea della sessione (non conservati).

| prova | esito |
|---|---|
| `hashlib.scrypt` | **manca** in Pyodide 314 (niente OpenSSL). Fornita da JavaScript (`@noble/hashes` 2.4.0) e messa in `hashlib` prima di caricare il programma: vettore di prova ufficiale giusto, valore con la chiave di prova identico al PC, 0,1 s |
| rilettura nel browser del manoscritto scritto sul PC | **sì**, 12 s (PC 5–6 s) |
| chiave sbagliata | rifiutata ("wrong key, or manuscript without a message") |
| scrittura nel browser | 214 s (PC 105 s da solo; 166 s con due scritture in parallelo e l'e416) |
| manoscritto del browser identico byte per byte a quello del PC | **no**: 4.047 righe su 4.050 diverse |
| rilettura nel browser del manoscritto scritto nel browser | sì |
| **rilettura sul PC del manoscritto scritto nel browser** | **sì**, 6,5 s |
| PDF nel browser | 207 pagine in 11,5 s; uguale a vista a quello del PC (285 KB contro 558: cambia solo la compressione di matplotlib 3.10 contro 3.11) |
| memoria massima | circa 480 MB (con il PDF; 400 MB per scrivere) |
| da scaricare al primo accesso | circa 27 MB (Python, numpy, scipy, scikit-learn) + 10 MB solo per il PDF (matplotlib) |

**Perché i manoscritti sono diversi ma si rileggono:**
- sul PC il programma è deterministico anche cambiando `PYTHONHASHSEED` (semi 0 e 12345: identici fra loro e al
  manoscritto del pacchetto);
- nel browser le **parole di ogni pagina** sono identiche a quelle del PC: 207 pagine su 207, 34.974 parole, stesso
  numero di righe per pagina;
- cambia solo **l'ordine delle parole nelle righe** (la disposizione, che usa calcoli in virgola mobile e
  scikit-learn), che non porta informazione: per rileggere servono solo le parole di ogni pagina e la chiave.

**Conseguenze per il sito:**
- il calcolo nel browser si può fare: niente server, costo zero, testo e chiave non lasciano il computer;
- `scrypt` va fornito da JavaScript (libreria da copiare nel sito, non presa da un CDN);
- non promettere "stesso testo e stessa chiave danno lo stesso manoscritto del programma": danno le stesse parole per
  pagina, in un ordine che può cambiare; si rilegge nei due sensi;
- è una prima prova di rilettura in un ambiente diverso (versioni di Python e librerie diverse, WebAssembly), ma con
  **una sola chiave**: nel collaudo ripeterla con più chiavi e testi, nei due sensi, prima di aprire il sito.

## 11. Aggiornamento del 4/10/2026 pomeriggio: la versione pubblicata è la v20

- Il repo pubblico ora contiene la **v20** (non più la v17). Per il sito non cambia niente: stessi comandi, stessi
  formati, stessi tempi. Dove questa scheda dice "v17" leggere "v20" (anche negli esempi Python: `'v20'`).
- Che cosa cambia: le parole sono disposte in modo che la larghezza delle righe in caratteri somigli a quella del
  Voynich (prima c'erano troppe righe molto più larghe delle altre; nel PDF si vedeva).
- **I manoscritti scritti con la v17 si leggono con la v20** (verificato): le due versioni differiscono solo nella
  disposizione delle parole, che non porta il messaggio.
- Numeri aggiornati (12 chiavi): giudici 0,55 e 0,60; pagella 15–16 su 17; righe oltre 1,5 volte la mediana 2,8%
  (Voynich 2,9%); oltre 1,25 volte 11,5% (Voynich 6,0%: difetto che resta, dichiarato nel README).
- Il carattere è alla versione 1.1 (forche e "l" ridisegnate).

## 13. Chat del sito, 4/10/2026 pomeriggio: decisioni di Davide e stato

- **Aspetto:** preso dal Voynich vero (pergamena su nero come nelle foto della Beinecke, inchiostro bruno, un disegno
  vero per pagina). Davide: "molto molto meglio". **Immagini di Yale: confermate da Davide, "usane anche di più"**
  (politica Open Access di Yale per le opere di pubblico dominio). Nel sito: 5 disegni ripuliti dallo sfondo
  (`docs/img/`) e le foto di tutti i 207 fogli (`docs/img/folios/`, 6,9 MB), mostrate accanto al foglio generato
  nell'anteprima e sul banco dell'amanuense durante l'attesa, con il link alla pagina di Yale.
- **Indirizzo di lavoro di Davide:** testi molto più esaurienti e tecnici ("non è solo un giocone"). How it works
  riscritta per intero (21 sezioni: principio, dati, chiave, cifratura, gabbia, codifica aritmetica, parole inventate,
  disposizione con tutti i pesi, rilettura, capienza, piattaforme, giudici G1–G9, pagella, cancello, sicurezza, limiti,
  storia, mappa del codice).
- **Il sito usa la v20** (commit `261e175`), copiata in `docs/engine/v20/`; resta `docs/engine/v17/` per ora.
- **Capienza:** con cinque chiavi di prova va da **80.344 a 84.678 bit** (la scheda diceva 81.000–83.000). Il sito
  rifiuta subito oltre 86.000; fra 80.000 e 86.000 controlla appena il programma conosce la capienza (fine della scelta
  delle parole, circa un decimo del tempo), con lo stesso messaggio del programma.
- **Difetto trovato nel programma (v17 e v20, da segnalare alla chat del voynichizzatore):** in
  `disposizione.Disposizione.pagina` le righe che inizializzano `conti` (il conteggio delle scelte di grafia di ogni riga
  per i pesi `scelte` e `scelte_sopra`) stanno dentro `cambio_meta`, dopo il suo `return`: non vengono mai eseguite e i
  conteggi partono da zero. Probabilmente spostate quando fu inserito il termine `meta` (e412). La rilettura non è
  toccata (la disposizione non porta il messaggio); correggerlo cambia i manoscritti, quindi è una versione nuova.
- **Sicurezza, osservazioni scritte in How it works:** sale di scrypt fisso (un dizionario preparato vale per tutti) e
  flusso che dipende solo dalla chiave (stessa chiave per due messaggi = stesso flusso): usare una chiave diversa per
  ogni messaggio.

- **Correzione dei numeri (conferma su 24 chiavi):** giudici **0,56 e 0,61** (non 0,55 e 0,60); pagella 15–16;
  cancello della riga 24 su 24; rilettura 24 su 24. Usare questi, che sono quelli del README pubblico.
- **Chiave:** il sito deve chiedere una chiave lunga e casuale (almeno 6 parole a caso o 12 caratteri a caso), o
  generarla lui e mostrarla all'utente. Con una parola comune un attacco a tentativi riesce in poco tempo.
- **Collaudo v20 (4/10 sera), tutto superato.** Cinque casi scritti sia dal programma sul PC sia dal sito nel
  browser: c1 inglese corto; c2 italiano con accenti, virgolette, righe vuote, chiave accentata; c3 greco, cirillico,
  cinese, giapponese, coreano, arabo, ebraico, emoji, tabulazioni, a capo Windows, chiave con emoji; c4 32.014
  caratteri, 76.888 bit (91% della capienza), chiave di 264 caratteri; c5 libro senza messaggio. In tutti: rilettura
  browser → PC e PC → browser esatta; manoscritti v17 letti con la v20, sul PC e nel browser, esatti; chiave sbagliata
  respinta dalle due parti; parole identiche in 207 pagine su 207; capienze uguali; c1 riscritto due volte nel browser
  identico byte per byte. Tempi nel browser 172–350 s (PC carico). Tabella pubblicata in How it works.
- **Difetto del sito trovato dal collaudo e corretto:** il libro senza messaggio falliva nel browser (il `null` di
  JavaScript arriva a Python come `JsNull`, non `None`). Ora il motore passa un segnale a parte. Rifatto c5: passa.
- `docs/engine/v17` tolto: la v20 legge i manoscritti v17.
- **Inquadramento chiesto da Davide:** il sito presenta il risultato come un "secondo Voynich" (Voynich II), fatto per
  essere indistinguibile; per ora si scrive "made to be indistinguishable" (obiettivo) e "le nostre misure quasi non lo
  distinguono" (risultato), non "indistinguishable" come fatto: decisione da confermare con Davide (vedi §8).
- **Email di Davide nel sito (sua decisione, 4/10 sera):** nel colophon di About, scritta in due metà e ricomposta da
  `js/top.js` (contro i raccoglitori di indirizzi). Sostituisce l'indicazione del §9 ("non va messa da nessuna parte").
- **Nuovo PDF (decisione di Davide):** non il libro identico all'originale, ma pagine composte: pergamena, disegni veri
  staccati dal Voynich (quello del foglio vero con lo stesso nome; scelta lasciata a Claude), testo generato intorno in
  inchiostro bruno. Il PDF attuale (matplotlib) si toglie quando il nuovo è pronto.
- **Libro illustrato fatto (4/10 sera):** `docs/js/book.js` compone ogni foglio su pergamena col disegno vero del
  foglio con lo stesso nome (153 disegni ripuliti dalla scrittura in `docs/book/`, ricavati dalle foto di Yale con lo
  script della sessione; ripieghi per sezione; stelline per le ricette), sceglie fra tre impaginazioni quella che unisce
  scrittura leggibile e disegno grande, e fa il PDF nel browser con jsPDF 4.2.1 (copiato in `docs/js/vendor/`, MIT):
  207 pagine, circa 8 MB, circa 25 s. L'anteprima della pagina Write usa la stessa impaginazione. Il vecchio PDF
  (matplotlib) è tolto dal sito; il comando `pdf` del programma resta com'è.
- **Il sito usa la v21** (commit `4b1383c`), su richiesta di Davide passata dalla chat del voynichizzatore; tolta la
  cartella v20. Prova nel browser: manoscritti v17 e v20 (c1, c3, c4) riletti esatti dalla v21; manoscritto scritto
  dalla v21 nel browser riletto dal programma v21; parole uguali alla v20 in 207 pagine su 207.

## 14. Sito pubblicato (4/10/2026 sera, su richiesta di Davide)

- **Indirizzo:** https://andreottiviii.github.io/voynichizzatore/ (GitHub Pages dal ramo `gh-pages`, attivato da GitHub
  al primo push). Il codice del sito sta anche in `docs/` del ramo `main` del repo pubblico.
- **Prova sul sito pubblico:** tutte le pagine e i file rispondono; la pagina Read ha riletto esatto il manoscritto di
  prova del repo (`prova/manoscritto_di_prova.txt`, chiave di `prova.py`) caricando Python, il programma v21 e scrypt
  dal sito.
- **Research:** contenuti del white paper (commit 955660e: titolo, autori e contributori, abstract, dieci scoperte,
  citazione) e il PDF `research/Caniatti_Claude_2026_Voynich_writing_system_v1.pdf`. Senza licenza (non ancora scelta),
  senza link al repo privato, senza note sui ruoli degli autori (indicazioni della chat della ricerca). Quando arriva il
  DOI di Zenodo: aggiungerlo nella citazione e sostituire il PDF.
- **Come si aggiorna il sito** (copia di lavoro `C:\Users\davide\voynichizzatore_sito`, ramo `sito`):
  1. modificare `docs/`, provare in locale (server della sessione o `python -m http.server` in `docs/`);
  2. `git commit`, poi `git push origin sito:main`;
  3. `git subtree push --prefix docs origin gh-pages` (pubblica la cartella `docs/`);
  4. **nuova versione del programma:** `git merge main` nel ramo `sito`, `python docs/engine/build_engine.py vNN`,
     aggiornare `VERSION` in `docs/js/engine.js` e `docs/js/worker.js` e i percorsi del carattere; tenere la cartella
     della versione vecchia solo se la nuova cambia i conteggi delle parole (allora la vecchia serve per rileggere).
- **Attenzione per chi pubblica il programma:** il ramo `main` del repo pubblico ora contiene `docs/`; prima di un push
  dalla copia `C:\Users\davide\voynichizzatore` fare `git pull`.
- **4/10 sera, aggiornamenti pubblicati:** favicon (il sole di f67r ridisegnato: aquiloni blu, punte rosse, disco con
  falce e volto; `favicon.svg`, `favicon.ico` 16/32/48, `apple-touch-icon.png`), immagine di anteprima per la
  condivisione dei link (`og-image.jpg`, 1200×630, pianta di f9v e titolo) con i tag Open Graph in ogni pagina;
  Research con la licenza CC BY 4.0 e il PDF nuovo (commit 1e3178c della ricerca), **senza la riga dei contributori**
  (richiesta di Davide, "per ora"). Didascalie dei fogli veri: solo il codice del foglio. `.gitattributes` del repo
  pubblico: aggiunti `*.ico` e `*.webp` come binari (il favicon era stato alterato dalla conversione degli a capo).
