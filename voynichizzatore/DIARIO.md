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
