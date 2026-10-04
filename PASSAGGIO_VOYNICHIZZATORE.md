# Passaggio di consegne: il voynichizzatore

Scritto il 3/10/2026 alle 19:45, alla consegna del voynichizzatore a una nuova chat. Da qui in poi la chat di ricerca fa
**solo ricerca sul Voynich**; il voynichizzatore è tutto della nuova chat. Questo file è il punto di partenza: dice che
cosa si vuole, dove siamo, che cosa si sa del testo, che cosa non ha funzionato e perché.

---

## 1. Che cosa vuole Davide

- **Il voynichizzatore:** gli si dà un testo normale (per esempio Isidoro, un brano in italiano). Restituisce un
  manoscritto **indistinguibile dal Voynich**. Con la chiave, il testo torna fuori **esatto**.
- **"Indistinguibile" in numeri:**
  - pagella 18/18 dell'e224 con il cancello della riga, più le 8 materie aggiunte della pagella estesa (e293);
  - AUC ≤ **0,6** per i due discriminatori: e231 (5 gruppi) ed e266 (9 gruppi, il più forte).
- **Scelte di Davide** (`rassegna/voynichizzatore_progetto.md`):
  - imitare tutto il manoscritto (sezioni, mani, lingue A e B);
  - uscita in EVA, poi un'immagine con etichette e testo circolare;
  - chiave fatta da una parola;
  - l'indistinguibilità prevale sulla compattezza.
- **Quando funziona:** Davide lo vuole pubblicare su GitHub o come sito. Va fatto in un **repo pubblico separato**,
  con solo il programma e le statistiche necessarie, dopo aver controllato le licenze della trascrizione. Questo repo
  resta privato.
- **Stile di lavoro chiesto da Davide:**
  - italiano semplice, senza gergo;
  - avvisarlo dei risultati importanti;
  - migliorare in autonomia, a giri successivi, senza chiedere il permesso a ogni passo;
  - tenere la CPU occupata e la finestra di stato vera;
  - **niente giri a vuoto:** se qualcosa non torna, è il segno che manca un pezzo di comprensione. Si capisce
    quello, invece di girare manopole.

## 2. Regole del repo (da `CLAUDE.md`, valgono anche per il voynichizzatore)

- **Dati e repo:** i dati in `dati/cache` sono protetti da diritto d'autore. Non si committano e non si
  ridistribuiscono. Il repo resta privato.
- **Ordine dei commit,** ogni passo in un commit a parte:
  1. preregistrazione `preregistrazioni/eNN.md`;
  2. codice;
  3. esecuzione con `esegui.py` (scrive la provenienza);
  4. risultati e voce nel QUADERNO;
  5. push.
- **QUADERNO.md:** si scrive solo in aggiunta. Gli esiti negativi si scrivono come gli altri.
- **Git:**
  - file aggiunti per nome, mai `git commit -a`;
  - comandi git uno alla volta;
  - i messaggi finiscono con `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`;
  - l'email di Davide serve solo come autore git.
- **Semi:** i semi di verifica **7, 8, 9** non si usano mai per scegliere.
- **Esecuzioni lunghe:**
  - si lanciano in code staccate: `nohup bash strumenti/coda.sh NOME "PROCESSI=n:eNNN" > /dev/null 2>&1 &`;
  - lo stato va in `esecuzioni/stato_code.txt`, che si segue con un Monitor;
  - la finestra di Davide (`strumenti/Stato esperimenti.bat`) legge `esecuzioni/in_coda.txt` ed
    `esecuzioni/in_preparazione.txt` (righe `voce|descrizione|stato`): vanno tenuti **sempre veri**.
- **Ambiente:**
  - `.venv`, Python 3.12, `PYTHONIOENCODING=utf-8` per le stampe;
  - script lunghi scritti con lo strumento Write, non con heredoc.

### Convivenza con la chat di ricerca (stesso repo, stessa macchina, 16 core)

| | chat del voynichizzatore | chat di ricerca |
|---|---|---|
| file | `voynichizzatore/`, `esperimenti/e293_banco.py`, file nuovi suoi | `esperimenti/` (escluso e293), `preregistrazioni/` dei suoi esperimenti, `DOSSIER_WHITE_PAPER.md` |
| numeri degli esperimenti | **e400–e499** | e307–e399 |
| processi | fino a 10 | fino a 6 |

Accordi:
- I file dell'altra chat si leggono, non si modificano.
- `QUADERNO.md`, `STATO_LAVORI.md` e i due file della finestra di stato li scrivono entrambe le chat, solo in
  aggiunta e con `git pull --rebase` prima di ogni commit.
- Nella finestra di stato ogni chat aggiorna solo le proprie righe. Quelle del voynichizzatore iniziano con `vz:`.
- Le scoperte sul Voynich che emergono lavorando al voynichizzatore vanno nel QUADERNO. La chat di ricerca le porterà
  nel dossier.

## 3. Dove siamo (numeri verificati)

**Banco preregistrato e293.** Si esegue con `esegui.py e293 -- --v3 --v5`. Isidoro XVII nascosto con la chiave
"banco", semi di verifica 7-9. Risultati in `risultati/e293_banco_v3_v4_v5.md` e `risultati/e293_banco_v6.md`.

| versione | corpo | pagella (18 × 3) | pagella estesa (26 × 3) | cancello riga | AUC e231 | AUC e266 | decodifica |
|---|---|---|---|---|---|---|---|
| v3 | e288 (rip 0,5, φ 0,10, σ 0,04) + modello delle scelte v3 | 52 | 52 | 2 semi | 0,817 | 0,934 | esatta |
| v4 | v3 + bordi legati (λ_fin 1, λ_pre 1) + classi di riga per selezione (λ_cl 0,3) | 50 | **59** | 0 | 0,843 | 0,931 | esatta |
| **v5** | v4 + δ 0,2 (1 parola di base su 5 dal lessico globale) | 49 | 57 | 0 | **0,816** | **0,917** | esatta |
| v6 | v5 + rip 0,4 | 46 | 55 | 0 | 0,827 | 0,936 | esatta, **non confermata** |

- **La migliore verificata è la v5.**
- **Promettente ma non verificato:** *p*/*f* nelle prime righe dei paragrafi (`corpo5.galli_prime`, su 1, giù 0,7).
  Sui semi di ricerca 1-2 sopra la v5 porta l'AUC dell'e266 da 0,923 a **0,861**, a pagella estesa uguale. Il
  gruppo G8 scende da 0,87 a 0,67. È il passo più grande del giorno sull'e266 ed è mirato a un difetto preciso,
  quindi è probabile che regga. Va verificato sui semi 7-9.
- **Difetti aperti di v4/v5:**
  - perdono il **cancello della riga** in tutti i semi: cade A (somiglianza fra parole vicine oltre il caso, soglia
    1,0; v5 0,983);
  - perdono la materia **"gradiente"**: somiglianza fra righe a distanza 6 diviso somiglianza nella riga, Voynich
    0,89, v5 0,56;
  - mancano ancora 5 materie aggiunte: parole rare per pagina, tipi e uniche nella pagina, dispersione delle
    lunghezze, prime righe come registro.
- **Diagnosi della v5** con Isidoro, AUC 0,810 / 0,915 (`voynichizzatore/diagnosi.py`). I difetti più pesanti:
  - G8, prime righe: *p* +0,0315 nel Voynich contro +0,012;
  - G3, varietà nella pagina e lunghezze;
  - G6, coppie identiche: il doppio del Voynich.

### Il nuovo impianto provato alla fine (`voynichizzatore/modello.py`)

Al posto di "copia e modifica la pagina vera", un **modello del Voynich**:
- **da dove vengono le parole:** una mescolanza di fonti, con pesi stimati per massima verosimiglianza senza la
  pagina in esame. Le fonti sono:
  - memoria delle righe precedenti della pagina;
  - due pagine precedenti;
  - coppia con la parola precedente;
  - sezione × tipo di riga × posizione;
  - libro;
  - parola nuova (variante di una parola frequente);
- **quale parola si sceglie:** fra 16 candidate, con un peso dato dai legami ai bordi (finale→finale,
  finale→prefisso, prefisso→prefisso).

Risultati sui semi 1-4 (`esecuzioni/voynichizzatore/prova_modello*.log`):

| | pagella (18 × 4) | estese | AUC e231 | AUC e266 |
|---|---|---|---|---|
| v5 | 66 | 12 | 0,812 | 0,918 |
| modello, prototipo 1 | 27 | 2 | 0,988 | 0,998 |
| modello, seconda forma tarata | 30 | 12 | 0,932 | 0,989 |

- **Le statistiche di libro della seconda forma tornano.** Pannello `controlla_modello.py`, seme 1, Voynich →
  modello:
  - varietà nella pagina 0,756 → 0,763;
  - hapax 0,137 → 0,130;
  - coppie riviste altrove 0,241 → 0,240;
  - legame fra finali 0,0237 → 0,0240.
- **Il modello non copia:** i trigrammi presi dal Voynich sono l'1,3%.
- **Manca l'identità di ogni pagina.**
  - Il gruppo più riconoscibile è G9 (0,93), il profilo dei segni della pagina rispetto al libro.
  - Si perdono profilo pagina, deriva, omogeneità, verticale, formule.
  - Il vecchio generatore quell'identità l'aveva gratis, perché pescava dalle parole della pagina vera.
- **Domanda aperta:** che cosa rende ogni pagina diversa dalle altre. La chat di ricerca può studiarla: tipi di pagina,
  ordine, mani, lingue.

## 4. Che cosa si sa del testo (quello che il voynichizzatore deve riprodurre)

Dettagli e numeri in `DOSSIER_WHITE_PAPER.md` §15 e nel QUADERNO del 3/10.

**Parole e pagine**
- **Varietà:** tipi su parole nella pagina 0,756; uniche nella pagina 0,636; hapax 13,7% dei token, circa 7.000 tipi.
- **Ripetizione nella pagina:** il Voynich ripete le parole nella pagina ma **le evita nella stessa riga** (e303).
  Nella riga le parole si somigliano meno che con la riga sotto (0,965 contro 1). La somiglianza scende lentamente
  fino a 8 righe e risale a 12-16. La memoria giusta è quella delle **righe sopra**.
- **Coppie identiche vicine:** 0,94%, soprattutto parole **lunghe** (*chol chol*, *qokeedy qokeedy*). Il
  generatore ne fa il doppio, e di parole corte (e305).
- **Parole rare** (e296, e304):
  - due terzi sono varianti di una lettera di parole frequenti;
  - sono sparse fra le pagine (R 0,57-1,96; generatore 40-56);
  - tornano in media 3 volte, su pagine **più vicine del caso** (z −5,4): la grafia cambia nel tempo.
- **Ordine delle pagine:** le pagine vicine nella rilegatura si somigliano (z 8,5; z 5,7 anche a parità di sezione e
  lingua; e300, e300b).

**Parole vicine**
- **Legame fra parole vicine:** passa per i **bordi**: finale→finale, finale→prefisso (0,112), prefisso→prefisso. I
  centri quasi non contano (e285, e294).
  - La forma del legame è quella di una lingua con concordanza, ma la forza è 3-10 volte minore di qualsiasi lingua.
  - La coppia esatta di parole conta poco: nel modello pesa 0,03-0,05.
  - La parola si prevede dalla sezione (peso 0,31-0,42) e dal segno finale della parola precedente.
- **Concordanza delle desinenze:** dentro la riga 0,050, attraverso l'a capo 0,007 (e295). È un'abitudine di riga.
- **Coppie riviste altrove:** 22-24% delle coppie vicine.
- **Riga sopra (CORRETTO il 3/10 alle 22:05):** nel primo prototipo del modello pesava ~0, ma era una misura debole:
  competeva con il lessico della pagina vera, che vedeva anche le parole dopo. La misura diretta dell'e338 dice il
  contrario. Una parola ha una parola uguale o a una modifica di distanza nelle 2 righe subito sopra più del caso (z 16,6,
  più che nel generatore di Timm e Schinner). Quando la fonte è nella riga sopra, sta nella stessa colonna ±1 più del caso
  (z 8,7). Due cautele: la prima misura può includere il lessico del paragrafo; la seconda gli effetti di posizione
  nella riga (prima/ultima parola). Vedi QUADERNO, voce e337–e339. **Verifica e340:** la ripresa dalle 2 righe sopra
  regge anche a parità di lessico del paragrafo (z 17,4, più del doppio del generatore di Timm e Schinner); la "stessa
  colonna" invece, senza prima e ultima parola, quasi sparisce (z 2,7). Il generatore deve riprendere parole dalle
  righe appena scritte, non dalla stessa posizione.

**Righe e paragrafi**
- **Scelte di grafia concordi nella riga:** 12 classi su 12 con z > 3 (e206b). Il generatore ne prende 2-3, la v4
  12. Ci sono la memoria di riga e quella della riga sopra (modello delle scelte della v1).
- **Prime righe dei paragrafi** (e273, e302): sono un **registro a parte**.
  - parole più lunghe di 0,42 segni;
  - più *sh* e meno *ch* all'inizio;
  - *p* 20 volte più frequente che nelle altre righe (3,3% contro 0,17% dei segni), *f* 14 volte;
  - più -*y* e meno -*n* in fine parola;
  - la prima parola del paragrafo è una parola nuova quasi una volta su due.
- **Inizio riga:** *t* 10,5%, *k* 3,2%.
- **Lunghezze** (e306): il generatore vecchio è troppo corto ovunque. Fa troppe parole di 1-2 segni (16% contro 12%),
  per colpa delle spezzature e dei prefissi staccati dell'e236.

## 5. Lezioni di metodo (pagate care il 3/10)

1. **Effetto vincitore.** Quattro scelte su due semi non hanno retto la verifica (e283, e253, e292, v6). L'AUC di un
   seme varia di circa 0,03. Quindi:
   - si sceglie su **almeno 4 semi di ricerca (1-4)**;
   - si accetta un ritocco solo se abbassa l'AUC di **almeno 0,03**, oppure se è mirato a un gruppo del
     discriminatore e lo abbassa nettamente;
   - si verifica sempre sul banco ai semi 7-9.
2. **Partire dalla diagnosi** (`diagnosi.py`: gruppo e caratteristica più pesanti), non da manopole a caso.
   L'unico ritocco nato dalla diagnosi (*p*/*f*) è stato il più forte.
3. **Ciclo corto:** prima si fanno tornare le statistiche semplici con il pannello veloce (`controlla_modello.py`,
   pochi secondi). Poi i discriminatori, che richiedono minuti.
4. **Strade provate e fallite** (con il motivo, nel QUADERNO):

   | strada | perché è fallita |
   |---|---|
   | classi di riga per **sostituzione** di parole (`corpo5.classi_riga`) | AUC fino a 0,99 |
   | parole rare fatte girare per **scambio** fra pagine (`corpo5.circola`) | rompe omogeneità e legame, anche fra pagine vicine |
   | tema variato τ (e291), coppie ripetute ω (e292) | — |
   | errori sparsi da soli (e297) | — |
   | lunghezza stabile β 1, ρ prime righe | — |
   | dodici interruttori di riga (e252) | — |
   | regolazione congiunta su 19 parametri (e253) | — |

   Inoltre i **bordi** alzano la somiglianza nella riga e fanno perdere il gradiente.
5. **Il nascondiglio funziona e non si vede.**
   - Codifica aritmetica (Witten-Neal-Cleary, 32 bit) nelle 5 scelte di grafia (ch/sh, k/t, -l/-r, qo-/o-,
     -dy/-ey), secondo un modello delle scelte imparato dal Voynich.
   - Il manoscritto con il messaggio ha la stessa AUC di quello senza (v1).
   - Capacità circa 0,8 bit per posto, circa 38.000-46.000 bit per un libro come il Voynich, cioè circa 11.000
     caratteri di testo compresso.
   - Con un modello di parole buono, il messaggio si potrebbe nascondere direttamente nella scelta delle parole:
     più capacità e indistinguibile per costruzione.

## 6. Mappa del codice

| file | che cosa fa |
|---|---|
| `voynichizzatore/voynichizzatore.py` | strumento unico: `codifica testo.txt --chiave X --uscita m.txt --versione v5`, `decodifica`, `valuta`, `versioni` |
| `voynichizzatore/versioni.py` | registro delle versioni (corpo + modello delle scelte); `corpo(parametri, seme)` mette insieme tutti i meccanismi |
| `voynichizzatore/v0.py` | formato del manoscritto (`@<pag.n> parole.separate.da.punti`), chiave → seme (`numero`), salva/carica |
| `voynichizzatore/v1.py` | nascondiglio: modello delle scelte, codifica aritmetica (Nasconditore = decodificatore aritmetico, Rilettore = codificatore), `codifica`/`decodifica` con verifica interna |
| `voynichizzatore/v3.py`, `modello_scelte_v3.json` | modello delle scelte con lo stato di riga nel contesto KT (quello usato da v3-v6) |
| `voynichizzatore/corpo.py` … `corpo4.py` | il generatore vecchio "copia e modifica" con tutti i meccanismi come parametri (identico a e233/e241/e288 a manopole spente) |
| `voynichizzatore/corpo5.py` | ritocchi dopo la generazione: `circola`, `classi_riga` (scartati), `galli_prime` (*p*/*f* nelle prime righe, promettente) |
| `voynichizzatore/corpo6.py` | generatore con i bordi legati (λ_fin, λ_pre) e le classi di riga per selezione (λ_cl) |
| `voynichizzatore/modello.py`, `modello_pesi.json` | il nuovo impianto (sezione 3) |
| `voynichizzatore/controlla_modello.py` | pannello veloce delle statistiche di base |
| `voynichizzatore/diagnosi.py` | AUC per gruppo e caratteristiche più pesanti di un manoscritto |
| `voynichizzatore/prova_v*.py`, `prova_modello.py` | prove di ricerca sui semi 1-2 (o 1-4); `prova_v4b.lavoro` misura un corpo con pagella, estesa e AUC |
| `esperimenti/e293_banco.py` | banco preregistrato (`preregistrazioni/e293.md`): pagella estesa e verifica sui semi 7-9 con decodifica |
| `esperimenti/e231_discriminatore.py`, `e266_discriminatore_forte.py` | i due discriminatori (`confronto`, `tabella`, gruppi G1-G9) |
| `esperimenti/e251_lessico_sezione.py` | `_prepara()` (contesto, riferimenti dei discriminatori), `pagella_grezza` (pagella con valori grezzi e cancello della riga), `R_completo` |
| `esperimenti/e224_generatore_completo.py`, `e61_pagella.py` | le 18 materie (`e224.valuta`, fasce in `e61.BANDE`) e il cancello della riga |

## 7. Materiale da leggere, in quest'ordine

1. Questo file.
2. `CLAUDE.md` e `STATO_LAVORI.md`.
3. `rassegna/voynichizzatore_progetto.md`: progetto, scelte di Davide, §7 e §11.
4. `DOSSIER_WHITE_PAPER.md` §15: le proprietà del testo trovate il 3/10.
5. `QUADERNO.md` dal 3/10 in poi: in particolare le voci da "e288" alla fine, cioè i giri del ciclo avversario, il
   banco e il cambio d'impianto.
6. `risultati/e293_banco_v3_v4_v5.md`, `risultati/e293_banco_v6.md`, `risultati/e302_cinque_misure.md`.
7. Il codice della sezione 6, partendo da `voynichizzatore/voynichizzatore.py`, `versioni.py`, `v1.py`,
   `modello.py`.

**Se la nuova chat non lavora su questa macchina:**
- le servono il repo (`git clone` del repo privato AndreottiVIII/voynich) e `dati/cache`;
- `dati/cache` sta nello zip `voynich_cache.zip` usato per il trasloco: protetto da diritto d'autore, solo per uso
  privato, da non caricare in posti pubblici;
- poi si esegue `strumenti/installa.ps1`.

## 8. Primo passo consigliato (la decisione resta della nuova chat e di Davide)

1. Rifare il banco della v5 per controllare l'ambiente: `esegui.py e293 -- --v5` deve ridare AUC 0,816 / 0,917.
2. Verificare sul banco la v5 con *p*/*f* nelle prime righe (`galli_su` 1, `galli_giu` 0,7): è il guadagno più
   probabile.
3. Scegliere l'impianto:
   - continuare il generatore vecchio, guidati dalla diagnosi;
   - oppure portare avanti il modello del Voynich, dandogli un'identità di pagina (per esempio il lessico e il profilo
     della pagina vera come "tema" della pagina, o tipi di pagina appresi).

   Il modello è più pulito e ha già le statistiche di libro giuste, ma oggi sta a 0,93/0,99. Il generatore vecchio sta
   a 0,82/0,92 ma è pieno di toppe che si pestano i piedi.

## 9. Novità dalla ricerca della notte 3–4/10 (utili al voynichizzatore)

Dettagli e numeri nel `QUADERNO.md` (e373–e3a02); tutto replicato con la trascrizione di Takahashi (e395).

- **Giuntura fra parole:** l'ultimo segno di una parola e il primo della seguente sono legati (0,19 bit oltre il caso;
  fra le lingue solo 6 su 71 fanno di più). Nessun generatore pubblicato la ha (e399).
  - **Si ferma all'a capo** (e384) e al **salto di un disegno** dentro la riga (e386); c'è nei testi in cerchio (e391).
    Nel generatore i legami ai bordi non devono passare da una riga all'altra né oltre un disegno.
  - È il doppio in lingua B rispetto ad A (e393).
- **Regole di raccordo** (e380, e388, e390):
  - *qo*-/*o*- davanti alle gallows: *qo*- dopo una parola in -*y*, -*o*, -*d* (59–64%), *o*- dopo -*n*, -*r*, -*s*,
    -*m* (23–27% di *qo*). Senza parola prima (etichette, dopo un disegno) quasi solo *o*- (e387). A inizio riga
    *qo*- è frequente e non guarda la riga sopra (e393).
  - -*l*/-*r* finale: -*r* davanti ad *a*- (85%), -*l* davanti a *k*-, *t*-, *d*-, *l*-, *s*-, *q*- (63–86%).
  - Lo stampo generale: dopo -*y* viene *q*- e si evitano *ch*-, *sh*-, *o*-; dopo -*n*, -*r*, -*l*, -*s* vengono *ch*-,
    *sh*-, *o*-, *a*- e si evita *q*-.
  - Le regole si applicano scrivendo: una parola copiata dalla riga sopra si accorda alla nuova vicina, non alla fonte
    (e392, e394). Per *qo*-/*o*- cambia la parola dopo; per -*l*/-*r* cambia la finale della parola prima (lo scriba
    guarda avanti di una parola) (e396, e3a02).
- **Bordi della riga** (e389): a fine riga -*m* prende il posto di -*r* (*dar* → *dam*) e un po' di -*l*; a inizio riga
  *y*-/*s*- prendono il posto di *ch*-/*k*-.
- **Ripresa:** è copia dalla riga subito sopra (poco dalla seconda, niente oltre), non continuità dell'argomento come
  nelle lingue (e385). Le copie vengono a pezzi, anche invertiti (e372).
- **Spazi:** dopo elementi corti lo spazio a volte spezza una parola (*s aiin* / *saiin*, *or aiin* / *oraiin*) (e379);
  la posizione degli spazi si prevede per il 73% dai segni vicini (e397).
- **Sessioni (bifogli):** l'inventiva (forme nuove) varia per sessione, non per scriba (e376); le proprietà delle
  sessioni variano indipendenti (e373).
- **Niente locuzioni:** oltre la giuntura le parole non preferiscono vicine precise (e375). Il generatore non deve
  avere coppie di parole fisse.
- **Margine sinistro** (e3a25–e3a33): una riga evita di cominciare come la riga subito sopra, soprattutto con *qo*- e
  *o*- (due *qo*- uno sotto l'altro: 17 contro 67 attese), meno con *d*-, *ch*-, *y*-. A inizio riga *qo*- è altrimenti
  la forma normale (e393). Al margine destro e nelle colonne interne niente del genere.
- **Testi in cerchio ed etichette** usano *o*-, quasi mai *qo*- (2–5%); la giuntura nei cerchi c'è ma è fatta d'altro
  (-*r* *a*-, -*s* *a*-, -*y* *d*-).
- **Quanto sono libere le scelte** (e3a36, e3a37): il contesto trovato più la parola tolgono solo il 18,5% dell'incertezza su *qo*-/*o*- e il 10,8% su -*l*/-*r*. Le regole di raccordo sono spinte, non obblighi: il resto della scelta è libero (spazio per un messaggio, se si rispettano le spinte).
- **Catena per riga** (e3a49–e3a52): nel Voynich le coppie di segni fra parole ricalcano quelle dentro le parole (lo spazio è un confine debole), e la catena riparte da capo a ogni riga. U3 ha la catena ma senza la chiusura della riga; gli altri generatori non hanno né l'una né l'altra.
- **Dove cade lo spazio** (descrittivo): dopo *n* (95%), *y* (82%), *m* (80%) quasi sempre; dopo *r* (69%), *l* (46%), *s* (36%) a scelta; dopo gli altri segni quasi mai (sotto il 3%). Nel generatore: catena di segni per riga, tagliata così.
  - Dopo *l*, *r*, *s* lo spazio dipende dal segno che segue: quasi sempre davanti a *q*, di solito davanti a *ch*/*sh*/*o*/*d*, di solito no davanti a *k*/*a*/*y*/*e* (*olkeedy*, *saiin*).
- **Vocabolario come insieme di forme** (e3a55–e3a57, e3a61): nel Voynich le parole frequenti sono le sequenze di segni
  più probabili per le regole di sequenza (ρ 0,58; lingue 0,11), e quasi metà delle forme più probabili sono parole
  usate (43%; lingue 4%). I quattro generatori fanno lo stesso (0,41–0,60 e 0,41–0,45): qui il voynichizzatore è già
  nel giusto se costruisce le parole da regole sui segni. Vale per tutte le mani, A e B, tre trascrizioni.
- **Spazi graduati** (e3a58, e3a60): la regola "probabilità di spazio data la coppia di segni" prevede lo spazio con F1
  0,86 (lingue 0,64). Gli spazi incerti dei trascrittori cadono dove la regola dà circa 0,5 (dopo -*r*, -*l*, -*s*
  davanti a certi segni), e Takahashi in quei punti mette lo spazio 2 volte su 3. Nel generatore conviene tagliare la
  catena con queste probabilità (non con soglie 0/1), e, se si produce un'immagine, disegnare spazi stretti nei punti
  con probabilità intermedia.
- **Che cosa basta e che cosa manca** (e3a78, e3a80, e3a81): una catena di segni di ordine 2 per riga (con stato di
  inizio e fine riga) riproduce giuntura, chiusura della riga, -*m* a fine riga, *y*/*s*/*d* a inizio riga, catena
  attraverso lo spazio, frequenza-forma. **Non** riproduce: copia dalla riga sopra, evitamento dell'inizio uguale alla
  riga sopra, *p*/*f* nella prima riga del paragrafo, crescita di -*ey* scendendo. Questi quattro vanno aggiunti a mano.
- **Memoria delle parole** (e3a76, e3a77): quasi ordine 1, con un po' di ordine 2 (i generatori pubblicati non hanno
  quel po'). Le caselle per posto spiegano poco.
- **Dettagli della copia** (e3a74, e3a79, e3a82, e3a83, e3a84): la copia prende da tutta la riga sopra ma un po' di più
  dalla fine (le parole appena scritte); la prima parola della riga copia quanto le altre (l'evitamento riguarda solo
  l'inizio uguale all'inizio della riga sopra); la copia porta un poco con sé gli spazi; la copia non cambia -*dy* in
  -*ey* (la deriva di -*ey* lungo la pagina è a parte).
- **Correzione (e3a85):** il "po' di ordine 2" che i generatori non hanno riguarda solo quali parole sono frequenti (e3a76). Misurata direttamente sulle sequenze, la memoria di due segni del Voynich (0,23 bit per terna) è come quella di Naibbe e di Timm e Schinner; U2/U3 ne hanno meno (0,04–0,06). Sta a inizio parola e nelle serie ee/ii e attorno a o.
- **Ripetizione di memoria corta nella riga** (e3a86–e3a90): nella stessa riga una parola si ripete (identica o quasi) circa il doppio di quanto faccia la catena, soprattutto entro 1–4 parole, e la cosa si spegne dopo 6–7 parole. Nelle lingue e in tutti i generatori pubblicati non c'è (Timm e Schinner ripete ma senza spegnersi). Nel generatore: dopo aver scritto una parola, per qualche parola c'è una probabilità in più di riscriverla o di scriverne una a una modifica.
- **Spazio = segni vicini + lunghezza della parola in corso** (e3a99, e3b01–e3b03): nei punti facoltativi lo spazio non segue l'identità della parola (preferenza lessicale quasi zero, contro +4/+7 nelle lingue) ma la lunghezza: si taglia di più quando il pezzo in corso ha 5+ segni (+11 punti) e si evita di staccare pezzi di 1–3 segni. Nel generatore: probabilità di spazio = f(segno prima, segno dopo) corretta con la lunghezza della parola in corso.
- **ATTENZIONE, correzione importante (e3b06):** le "12 scelte di riga" dell'e206b non sono interruttori validi per tutta la riga: l'accordo c'è solo fra parole vicine (2–3 di distanza, +0,031) e sparisce a 6–10 parole (−0,001). Nel generatore vanno sostituite da una memoria corta delle scelte di grafia (ripetere la scelta delle ultime 2–3 parole), insieme alla ripetizione di memoria corta delle parole.
  - (e3b08) La memoria corta vale anche per parole diverse: dopo una scelta di grafia (qo/o, -ey/-dy, sh/ch, ee/e) lo scriba tende a rifarla nelle 2–3 parole seguenti anche quando non ripete la parola.
  - (e3b18) La memoria è separata per ogni variante: un sh richiama sh, un qo richiama qo, ma una scelta non spinge le altre. Nel generatore: una memoria per ciascuna variante, non un unico stato.
  - (e3b19) Hanno memoria corta anche le gallows k/t; non ce l'ha il numero di i (ain/aiin/aiiin), che va lasciato senza memoria.
  - (e3b20) La memoria delle scelte si consuma con le lettere scritte, non solo con le parole: nel generatore, farla decadere col numero di segni scritti.
  - (e3b31) Le parole uniche nascono spesso come variazione (a una modifica) di una parola delle 4 precedenti nella stessa riga: nel generatore, le forme nuove vanno create soprattutto modificando una parola appena scritta.
  - **Correzione (e3b31):** le parole uniche con una "sorella" fra le 4 precedenti sono solo il 2,6% (contro 1,5% atteso): l'effetto c'è ma riguarda poche parole uniche; non usarlo come meccanismo principale per le forme nuove.
  - **Correzione (e3b34):** che la memoria duri di più in lingua B non è dimostrato; usare la stessa durata (circa 2–4 parole, qualche decina di lettere al massimo) in A e B.
  - (e3b35) La memoria è soprattutto per variante, con una piccola parte comune (circa un quarto): nel generatore si può aggiungere un debole stato comune.
  - (e3b38–e3b44) **Eccezione all'azzeramento all'a capo:** nelle 6 pagine "solo testo" (f1r, f66r, f76r, f85r1, f86v5, f86v6) la memoria delle scelte (e la giuntura, e3a06) passa da una riga all'altra (+0,075, contro −0,002 nelle altre pagine), con due trascrizioni, togliendo una pagina per volta e con la prova per pagina. La stessa mano 2 la azzera nelle sue pagine con disegni e non nelle sue pagine di solo testo, e le ricette (testo fitto, solo stelline) la azzerano. Lì restano invece forme di bordo, evitamento dell'inizio uguale e copia dalla riga sopra (e3b40, e3b43). Nel generatore: per le pagine di solo testo, non azzerare la memoria all'a capo (tutto il resto uguale).
  - **Correzione (e3b46):** "la copia porta un poco con sé gli spazi" (e3a74) non regge come meccanismo: la riga subito sopra non batte quella a due righe di distanza (con Takahashi differenza zero). Non serve copiare gli spazi insieme alle parole; e una deriva della spaziatura lungo la pagina non si vede (e3b47), quindi non serve nemmeno quella.
  - (e3b48) Fra etichette consecutive la memoria delle scelte si azzera (le etichette si copiano la forma, e263/e3a38, ma non le scelte): nel generatore, a ogni etichetta la memoria riparte da capo.
  - (e3b54) La memoria corta delle scelte grafiche c'è anche in uno scriba medievale vero (þ/ð nei Hatton Gospels, più forte che nel Voynich): è un tratto umano normale, quindi va messa nel generatore per imitare uno scriba, non come stranezza del Voynich. Circa metà della memoria grezza del Voynich viene da parole simili scritte vicine (copia locale con due o più modifiche); il resto, +0,045 in scala normalizzata, è memoria delle scelte fra parole diverse, più forte per -ey/-dy.
  - **Correzione (e3b55)** della nota e3b38–e3b44: nelle pagine di solo testo ciò che passa l'a capo sono le parole (che parola segue a fine riga, giuntura), non dimostrata la memoria delle scelte oltre le parole. Nel generatore, per quelle pagine: far continuare la catena di segni e la scelta delle parole da una riga all'altra (niente ripartenza della catena), la memoria delle scelte può ripartire come altrove.
  - (e3b59, e3b60) La memoria delle scelte oltre le parole è delle mani 2 e 3 (lingua B), soprattutto per -ey/-dy e qo/o; la mano 1 (lingua A, erbario) non la ha. Nel generatore: memoria delle scelte solo (o molto più forte) nelle pagine B; nelle pagine A basta la ripetizione di parole simili vicine.
  - **Correzione:** la differenza A/B dell'e3b59/e3b60 può venire dal metodo (nella mano 1 il nullo è poco sensibile); per ora usare la stessa memoria in A e B, in attesa dell'e3b62.
  - **e3b62 (sostituisce le note e3b54–e3b61 sulla memoria):** con un confronto più sensibile la memoria delle scelte oltre le parole è circa +0,08 (scala normalizzata) in tutte le quattro scelte (qo/o, k/t, sh/ch, -ey/-dy) e in tutte le mani, uguale in A e in B. Nel generatore: stessa memoria delle scelte in tutte le pagine e per tutte le scelte (non solo B). Nessun generatore pubblicato la ha.
  - **Correzione importante (e3b64–e3b66):** la memoria delle scelte **non si azzera all'a capo**: con l'atteso giusto (le forme di bordo cambiano le quote a fine e inizio riga) a cavallo dell'a capo resta circa metà della memoria nella riga (D +0,04 contro +0,088 dentro la riga, ZL e IT). All'a capo ripartono invece il raccordo e la giuntura (catena di segni). Nel generatore: all'a capo dimezzare la memoria delle scelte, non azzerarla; far ripartire la catena di segni.
  - (e3b67) Al salto di un disegno dentro la riga la memoria delle scelte **prosegue per intero** (mentre la catena di segni riparte: giuntura rotta, e386). Nel generatore: al salto far ripartire la catena di segni ma tenere la memoria delle scelte.
  - (e3b69, e3b70) Con intervalli onesti la memoria delle scelte del Voynich è solida (+0,086 ZL, +0,076 IT, scala normalizzata), uguale nelle mani; non è un effetto della catena (sul testo riscritto dalla catena vale circa 0). Se uno scriba vero la abbia non è dimostrato. Per il generatore non cambia nulla rispetto alle note e3b62–e3b67.
  - (e3b71) Pagine di solo testo: per la memoria delle scelte sono come le altre (passa l'a capo per circa metà). La loro particolarità è che la catena di segni non riparte all'a capo (giuntura che passa, e3a06). Nel generatore: in quelle pagine non far ripartire la catena all'a capo; la memoria delle scelte come altrove.
  - (e3b73) Alla fine del paragrafo la memoria delle scelte sembra ripartire (stima circa zero, intervallo largo); al cambio di pagina non si sa. Nel generatore: azzerare la memoria delle scelte a inizio paragrafo è compatibile con i dati.
