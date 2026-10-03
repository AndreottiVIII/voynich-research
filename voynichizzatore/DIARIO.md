# Diario di lavoro del voynichizzatore

Diario della chat del voynichizzatore, tenuto in ordine di tempo e **solo in aggiunta**. Serve a chi riprende il lavoro
(Davide, questa chat dopo un'interruzione, o un altro modello): dice che cosa si stava facendo, perché, che cosa è
uscito e qual è il prossimo passo. I risultati ufficiali restano nel `QUADERNO.md`; qui ci sono anche i ragionamenti,
le cose a metà e gli errori.

**Per riprendere da zero:** leggere `PASSAGGIO_VOYNICHIZZATORE.md`, `CLAUDE.md`, poi questo diario dalla fine
all'indietro fino all'ultima sezione "Dove siamo". Le regole di convivenza con la chat di ricerca sono nel passaggio
(esperimenti e400–e499, al massimo 10 processi, righe `vz:` nella finestra di stato, `git pull --rebase` prima di
ogni commit).

---

## 3/10/2026, sera — Inizio della chat e cambio di metodo

**Letture fatte:** passaggio di consegne, CLAUDE.md, STATO_LAVORI.md, progetto del voynichizzatore, dossier §15,
QUADERNO dal 3/10, codice del banco (e293), dei giudici (e231, e266), di `versioni.py`, `modello.py`, `corpo5.py`.

**Primo passo tentato e fermato.** Avevo aggiunto al registro la versione **v7** (= v5 + *p*/*f* nelle prime righe,
`galli_su` 1, `galli_giu` 0,7; commit `f65a551`) e stavo per lanciare il banco e293 su v5 e v7. Davide ha fermato:
"prima di lanciare ripartiamo da zero a ragionare". **Il banco v5/v7 non è mai partito.**

**Indicazioni di Davide (valgono sempre):**
- capire che cosa dà un risultato e perché, altrimenti "siamo sempre alla cieca";
- autonomia piena, ma aggiornamenti semplici, spiegati, con progressi a piccoli passi;
- tenere questo diario, così il lavoro si può passare a un altro modello.

**Il ragionamento da zero (piano approvato da Davide):**
1. I giudici (e231, e266) **non confrontano la pagina generata con la gemella vera**. Trasformano ogni pagina in
   circa 220 numeri e separano l'insieme delle pagine vere da quello delle generate. Quindi non serve copiare
   l'identità della pagina vera: serve che le pagine generate siano diverse fra loro quanto lo sono quelle vere.
2. Non si è mai misurato quanto costa ogni livello di struttura (ordine delle righe, ordine nella riga, parole della
   pagina). Senza questo non si sa dove lavorare.
3. Il nascondiglio non è mai stato misurato da solo sul corpo migliore possibile (il Voynich vero).

**Da qui il metodo:** prima una **scala dei controlli**, poi si costruisce **un pezzo alla volta**, ognuno misurato
contro il suo gradino; il generatore completo è l'ultimo passo.

### e400 — la scala dei controlli

- Preregistrazione `preregistrazioni/e400.md` (commit `58c8cbb`), codice `esperimenti/e400_scala_controlli.py`
  (commit `0b516ea`). Prova rapida della sola costruzione dei testi: a posto (`--prova`).
- Gradini: V (Voynich tale e quale), O1 righe rimescolate, O2 parole rimescolate nella riga, O3 parole rimescolate
  nella pagina tenendo separate le prime righe, O4 parole rimescolate in tutta la pagina, L1 ripescate dalla pagina
  con reimmissione, L2 dalle pagine vicine (±2), L3 da sezione × lingua, L4 da tutto il libro, N1 Voynich vero con
  Isidoro nascosto nelle cinque scelte di grafia. Semi 1–4.
- Previsioni scritte prima (AUC dell'e266): O1 0,50–0,58; O2 0,60–0,72; O3 0,75–0,85; O4 0,80–0,90; L1 0,88–0,95;
  L2 0,90–0,97; L3 0,95–0,99; L4 ≥ 0,98; N1 0,50–0,60.
- Lanciata alle 19:47 nella coda staccata `vz-scala` con `PROCESSI=10`. Uscita in
  `risultati/provenienza/e400.log`, risultati in `risultati/e400_scala_controlli.md` e `.json`.

**Come si legge (deciso prima):** O4 ≥ 0,75 → il primo pezzo da costruire è l'ordine delle parole, tenendo le parole
vere; O4 < 0,65 e L3 ≥ 0,85 → il primo pezzo è il "carattere" della pagina; N1 > 0,60 → va rifatto prima il
nascondiglio.

### Dove siamo (3/10, 19:50)

- In corso: e400. Nessun risultato ancora.
- Non pubblicati sul remoto: i commit `f65a551`, `58c8cbb`, `0b516ea` (si pubblicano con i risultati dell'e400).
- Rimandato: banco e293 di v5 e v7 (dopo la scala; serve anche come controllo dell'ambiente: la v5 deve ridare
  AUC 0,816 / 0,917).
- Prossimo passo: leggere la scala, scrivere la voce nel QUADERNO, scegliere il primo pezzo da costruire.

## 3/10/2026, 20:10 — e400 finito: che cosa dice la scala

Finito alle 20:02 (15 minuti). Controlli del metro validi. Tabella e dettagli nel QUADERNO (voce "vz: e400") e in
`risultati/e400_scala_controlli.md`.

**In breve (AUC dell'e266):** righe rimescolate 0,60; parole rimescolate nella riga **0,99**; nella pagina 0,998;
ripescate con reimmissione 1,00; nascondiglio da solo sul Voynich vero **0,63**.

**Le mie previsioni erano sbagliate** per i gradini O2–L1 (avevo previsto 0,60–0,95, sono tutti ≥ 0,99). Mi sono
fermato a capire perché, guardando gruppi e caratteristiche:
- non è un difetto del metro (V dà 0,500 esatto; i gruppi G1–G3, che non dipendono dall'ordine, restano a 0,50);
- sono i **bordi della riga**: G4 0,98 e G7 0,93. Inizio riga con *p* 7,7% → 0,9%, con *ch* 3,6% → 16,7%, fine riga in
  *m* 13,9% → 2,9%, prima parola più lunga. Avevo messo in conto i bordi, ma non quanto sono netti;
- l'ordine **in mezzo** alla riga vale poco (G6 0,66).

**Che cosa cambia nel modo di vedere il problema:**
1. Il generatore vecchio a 0,82/0,92 non era "scarso": partiva da 0,99 (rimescolamento) e i suoi meccanismi di riga
   lo portavano a 0,82. Il modello nuovo stava a 0,93/0,99 perché non aveva i bordi di riga.
2. Il problema si divide in due parti quasi indipendenti: **quali parole stanno nella pagina** (il sacco) e **come
   sono disposte** (prime righe, inizio e fine riga, coppie). La disposizione si può studiare da sola, con il sacco
   vero: ha un pavimento noto (0,5–0,6) e un soffitto noto (0,998).
3. Il nascondiglio attuale costa 0,63 da solo: da rifare, ma dopo aver capito la disposizione (riguarda l'ultimo
   passo).

**Prossimo passo deciso: e401, la disposizione.** Dato il sacco vero di ogni pagina e l'impaginazione, un modello
imparato dal Voynich (senza la pagina in esame) decide dove va ogni parola: prime righe o altre, inizio, fine, mezzo,
e accanto a quale parola. Si misura a strati (solo prime righe; più bordi; più coppie) contro O4, O3, O2 e O1.
Obiettivo: arrivare vicino a O1 (0,60).

### Dove siamo (3/10, 20:10)

- Fatto: e400 (risultati, QUADERNO, pubblicato sul remoto).
- In preparazione: e401 (preregistrazione e codice).
- Da fare dopo: rifare il nascondiglio (N1 0,63); il sacco di pagina (varietà, G3, G9); banco e293 di v5/v7 come
  controllo dell'ambiente.

**20:08 — e401 lanciato** (coda `vz-disp`, 10 processi; preregistrazione `e108496`, codice `667df14`: `voynichizzatore/disposizione.py` + `esperimenti/e401_disposizione.py`). Previsioni scritte: D1 0,985–0,995; D2 0,70–0,85; D3 0,62–0,75. Se un gruppo resta sopra 0,70 si guarda il pannello e si aggiunge solo il fattore che manca (e401b).

## 3/10/2026, 20:55 — e401: il primo lancio si è piantato (problema di calcolo, non un risultato)

- **Che cosa è successo.** Lanciato alle 20:08 con 10 processi; alle 20:39 nessuno dei 13 lavori aveva scritto una
  riga. I 10 processi consumavano circa 1,6 core ciascuno.
- **Che cosa ho capito** (misure in un processo a parte, senza giudici):
  - gli scambi della disposizione costano pochissimo: circa 8 microsecondi di calcolo a proposta, cioè una
    ventina di secondi per tutto il libro a 60 passate;
  - i tre termini del legame costano 0,3–1,5 microsecondi l'uno;
  - quindi il tempo va nell'**addestramento dell'affinità**: la regressione logistica era su una matrice densa
    (35.000 parole × 578 tratti) e ognuno dei 10 processi la calcolava per conto suo usando tutti i core. Dieci
    processi che vogliono 16 core l'uno si pestano i piedi e non finiscono; rallentano anche tutto il resto della
    macchina (le mie misure andavano 50 volte più piano in tempo d'orologio che in tempo di calcolo).
- **Correzione** (stesso modello, stessa preregistrazione): la matrice dei tratti è ora sparsa (nove tratti per
  parola). L'addestramento prende circa un minuto e mezzo anche a macchina carica.
- **Bloccato:** non ho il permesso di chiudere i processi piantati del primo lancio. Finché girano occupano la CPU
  e il file di uscita `risultati/provenienza/e401.log`. Ho chiesto a Davide di chiuderli (o di darmi il permesso).
  Poi l'e401 si rilancia identico: `nohup bash strumenti/coda.sh vz-disp2 "PROCESSI=10:e401" > /dev/null 2>&1 &`.
- **Lezione:** prima di lanciare in 10 processi un codice nuovo che addestra qualcosa, misurare il tempo di un
  lavoro intero in un processo solo.

### Dove siamo (3/10, 20:55)

- e400 fatto e pubblicato. e401: preregistrazione e codice committati, primo lancio piantato, correzione pronta,
  **in attesa che i processi vecchi vengano chiusi** per rilanciare. Nessun risultato dell'e401 è stato visto.
- Dopo l'e401: nascondiglio (N1 0,63), sacco di pagina, banco v5/v7.
