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

**21:31 — e401 rilanciato** (coda `vz-disp2`). Davide ha dato il permesso di chiudere i processi piantati: chiusi 14 processi dell'e401, nessun altro processo Python era in corso. Il primo lancio risulta nello stato delle code come "FINE e401 uscita 127" (interrotto, nessun risultato).

## 3/10/2026, 21:45 — e401 finito



Risultati nel QUADERNO (voce "vz: e401"). In breve, AUC dell'e266: D1 0,991, D2 **0,855**, D3 0,847 (e231: 0,985, 0,771, 0,729). Gli otto tipi di posto rimettono a posto i bordi della riga (G7 da 0,93 a 0,55). I legami fra vicine esagerano (unioni 11,8% contro 9,2%, coppie viste altrove 26,9% contro 22,1%, identiche 2,1% contro 0,97%): tre termini che dicono in parte la stessa cosa. Deciso l'e401b: quarto termine per le coppie identiche e pesi regolati sul pannello (non sui giudici), strato D4. Preregistrazione `preregistrazioni/e401b.md`.



### Dove siamo (3/10, 21:45)



- Fatti e pubblicati: e400, e401. In preparazione: e401b (codice da scrivere: regolazione dei pesi + strato D4).

- Dopo: ordine delle righe nella pagina (G9, differenza fra le due metà), sacco di pagina, nascondiglio (0,63), banco v5/v7.

**21:40 — e401b lanciato** (coda `vz-disp3`, 5 processi): prima la regolazione dei quattro pesi sul pannello (seme 11, fino a 15 giri), poi D4 sui semi 1–4. Previsione scritta: AUC dell'e266 0,68–0,78.

## 3/10/2026, 21:50 — e401b finito: la disposizione funziona



Risultati nel QUADERNO (voce "vz: e401b"). Regolazione convergita (pesi: bordi 0,71, unione 0,59, coppia 0,49, identica −0,55). **D4: AUC e231 0,533, e266 0,659** (previsto 0,68–0,78), con le parole vere di ogni pagina. Restano: G9 (differenza fra le due metà della pagina: ordine delle righe), G8 (prime righe un po' lunghe), somiglianza a distanza 2. **La pagella invece non è a posto** (14,8/18, 5,2/8, cancello della riga perso): mancano concordanza delle desinenze, formule, gradiente, legame, scelte di riga, verticale, ripetizione.



**Come riusarlo:** `disposizione.Disposizione(rr).disponi(rr, seme, 'D3', pesi={'bordi': 0.712, 'unione': 0.587, 'coppia': 0.493, 'identica': -0.552})`. I pesi esatti sono in `risultati/e401b_disposizione_regolata.json` (regolazione → pesi).



### Dove siamo (3/10, 21:50)



- Fatti e pubblicati: e400 (scala), e401 (disposizione, legami esagerati), e401b (disposizione regolata: 0,53 / 0,66 con il sacco vero).

- Il problema è ora diviso in due: la **disposizione** è capita per i giudici (non per la pagella); il **sacco di pagina** (quali parole in ogni pagina) è tutto da fare ed è il passo che trasforma il controllo in un generatore.

- Prossimi passi, in ordine: (1) e402: sacco di pagina fatto dal modello + questa disposizione, per vedere quanto costa il solo sacco; (2) ordine delle righe (G9) e materie di pagella perse; (3) nascondiglio (0,63 da solo); (4) banco e293 ai semi 7–9 quando c'è un generatore intero.

**21:48 — e402 lanciato** (coda `vz-sacco`, 9 processi; preregistrazione `preregistrazioni/e402.md`). Misura il sacco di pagina dei due generatori esistenti (v5 e `modello.genera`), originali e ridisposti con i pesi dell'e401b, più l'AUC del solo sacco (G1, G2, G3, JSD pagina-manoscritto). Previsioni: v5 ridisposta 0,84–0,92 (solo sacco 0,80–0,88); modello ridisposto 0,90–0,97 (solo sacco 0,88–0,95). `disposizione.py` ora dà l'affinità anche alle parole che non sono nel Voynich (`conosci`).

## 3/10/2026, 22:00 — e402 finito: il muro è il sacco



Risultati nel QUADERNO (voce "vz: e402"). Solo sacco: v5 **0,794**, modello **0,959** (sacco vero: 0,500). v5 ridisposta 0,797 / 0,842 (originale 0,812 / 0,918), ma la pagella scende da 16,5 a 13,5. Il sacco della v5 è troppo ripetitivo (tipi su parole 0,681 contro 0,756), con parole troppo corte e disperse; quello del modello ha pagine troppo medie (JSD 0,013 contro 0,040) e parole troppo lunghe.



**Decisione:** costruire il sacco un pezzo alla volta, misurando con il "solo sacco" (ciclo corto: non serve né disposizione né pagella). Pezzi previsti: (1) parole nuove, e403; (2) ripetizione nella pagina e famiglie di varianti; (3) carattere della pagina (profilo dei segni, pagine vicine); poi sacco intero + disposizione, e solo allora pagella e banco.



### Dove siamo (3/10, 22:00)



- Fatti e pubblicati: e400, e401, e401b, e402.

- In preparazione: e403 (parole nuove: sostituire solo le parole uniche nel libro con parole inventate da più generatori di forme).

- In sospeso: ordine delle righe (G9 metà pagina), materie di pagella perse dalla disposizione, nascondiglio (0,63), banco e293.

**22:00 — e403 lanciato** (coda `vz-nuove`, 10 processi; `voynichizzatore/parole_nuove.py`, `esperimenti/e403_parole_nuove.py`). Descrizione fatta prima: le 4.776 parole uniche sono lunghe (5,94 segni), il 72% è a una modifica da una parola nota, il 68% si legge come unione di due note; stanno ai bordi della riga (47,7% delle prime parole di paragrafo). Previsioni del solo sacco: variante-libro 0,60–0,72, variante-pagina 0,56–0,68, trigrammi 0,58–0,70, mista 0,55–0,65.

## 3/10/2026, 22:10 — e403 finito: le parole nuove sono un pezzo grosso del muro



Risultati nel QUADERNO (voce "vz: e403"). Solo sacco: variante-libro 0,795, variante-pagina 0,781, trigrammi 0,961, mista 0,774: tutti molto sopra le previsioni (0,55–0,72). Mi sono fermato a capire: le parole uniche del Voynich portano i segni rari e di posizione (x, c, g, h, f, p, s, m), che le varianti non hanno; i trigrammi hanno i segni più giusti (G1 0,62) ma lunghezze sbagliate. Secondo tentativo e403b: trigrammi con lunghezza controllata (T-L), per tipo di posto (T-LP), scelti secondo il profilo della pagina (T-LPS).

**22:04 — e403b lanciato** (coda `vz-nuove2`; `parole_nuove.FormeUniche`). Nella prova di costruzione la lunghezza torna (5,9 ± 1,56), ma le inventate sono meno vicine a parole note (0,55 contro 0,715). Previsioni: T-L 0,68–0,80, T-LP 0,62–0,74, T-LPS 0,55–0,68.

## 3/10/2026, 22:15 — e403b finito: parole nuove a 0,64 (pezzo provvisorio)



Risultati nel QUADERNO (voce "vz: e403b"). Solo sacco: T-L 0,690, T-LP 0,688, **T-LPS 0,644** (e403: 0,774). Il tipo di posto non cambia il solo sacco ma abbassa i giudici interi (0,843 → 0,751). Resta: le inventate somigliano meno a parole note (0,55 contro 0,715). Leva nota: modello dei segni più stretto.



**Come riusarlo:** `parole_nuove.FormeUniche(rr).inventa('T-LPS', classe, profilo, rnd)`, con `classe = 4*bool(inizio_paragrafo) + disposizione.posizione(j, n)` e `profilo = fu.profilo(parole_della_pagina)`.



### Dove siamo (3/10, 22:15)



- Fatti e pubblicati: e400, e401, e401b, e402, e403, e403b.

- Pezzi pronti: disposizione (0,53 / 0,66 con il sacco vero); parole nuove (0,64 di solo sacco, provvisorio).

- In preparazione: e404 (parole note: lessico di sezione + ripetizione con un parametro θ regolato sul pannello; K5 = primo generatore intero a pezzi).

- In sospeso: quali posti ricevono una parola nuova; ordine delle righe; materie di pagella; nascondiglio; banco e293.

**22:08 — e404 lanciato** (coda `vz-note`; `voynichizzatore/sacco.py`, `esperimenti/e404_parole_note.py`). Nella prova di costruzione: senza ripetizione i tipi su parole sono 0,783 (Voynich 0,756): serve poca ripetizione oltre al lessico di sezione. Previsioni del solo sacco: K1 0,80–0,92, K2 0,60–0,75, K4 0,68–0,80; K5 intero 0,72–0,84 / 0,78–0,90.

## 3/10/2026, 22:20 — e404 finito: manca il carattere della pagina; primo generatore intero a pezzi



Risultati nel QUADERNO (voce "vz: e404"). θ = 765 (ripetizione quasi spenta). Solo sacco: K1 0,786, K2 0,777, K4 0,756: una sola caratteristica pesa, la JSD pagina-manoscritto (0,023 contro 0,040). **K5 (generatore intero a pezzi): 0,716 / 0,857**, meglio della v5 (0,812 / 0,918) sui giudici, peggio sulla pagella (11,5 contro 16,5). Deciso l'e404b: carattere della pagina = scostamenti dei segni presi da un'altra pagina vera della stessa sezione e lingua, forza κ regolata sul pannello; parole nuove sul profilo generato.



### Dove siamo (3/10, 22:20)



- Fatti e pubblicati: e400–e404.

- Pezzi: disposizione (ok per i giudici), parole nuove (0,64, provvisorio), parole note (lessico di sezione + θ; manca il carattere).

- In preparazione: e404b (carattere della pagina).

- Dopo: regolare di nuovo i pesi della disposizione sul sacco generato; quali posti hanno una parola nuova; pagella (molte materie perse); nascondiglio; banco e293.

**22:15 — e404b lanciato** (coda `vz-car`). Nota: nella prova di costruzione il carattere abbassa i tipi su parole (0,727 con κ 0,75), quindi θ e κ si regolano insieme (integrazione alla preregistrazione, committata prima dell'esecuzione). Nota di riproducibilità: `sacco.genera` ora inventa le parole nuove dopo le parole note della pagina; l'e404 è stato eseguito con la versione precedente (commit nella sua provenienza). Indicazione di Davide (22:25): avere chiaro come fare, non girare a vuoto.

## 3/10/2026, 22:25 — e404b finito: le parole note sono a posto; mandato della notte



Risultati nel QUADERNO (voce "vz: e404b"). κ = 0,708, θ = 2280. **C2 0,482** (parole note con carattere: al pavimento), C4 0,645 (le parole nuove sono il costo che resta), **C5 intero 0,711 / 0,813, pagella 14,5/18**. Difetto mio capito: la scelta per profilo delle parole nuove penalizza i segni che la pagina non ha fra le parole note, cioè i segni rari.



**Mandato di Davide per la notte (22:20):** andare avanti in autonomia; per domattina vuole un generatore che funzioni. Gli ho detto che cosa prometto: un generatore intero testo → manoscritto → testo fatto con i pezzi nuovi, verificato al banco sui semi 7–9, con i numeri onesti; non prometto 0,6 su tutto.



**Come riusare il sacco:** `sacco.Sacco(rr, tipo).genera(seme, theta=2280, nuove='inventate', kappa=0.708)`, poi `disposizione.Disposizione(rr).disponi(testo, seme, 'D3', pesi=...)`.



### Dove siamo (3/10, 22:25)



- Fatti e pubblicati: e400–e404b.

- Pezzi: disposizione (ok per i giudici); parole note (ok: 0,48); parole nuove (0,64, da migliorare: prossimo passo e405); posti delle parole nuove (ancora veri).

- Piano della notte: e405 parole nuove (profilo solo sui segni comuni, modello a quattro segni, forza regolata sul pannello) → e406 posti delle parole nuove e pesi della disposizione regolati sul sacco generato → versione nel registro e banco e293 ai semi 7–9 con il messaggio → pagella (materie perse) → nascondiglio.

**22:22 — e405 lanciato** (coda `vz-nuove3`). Nella prova di costruzione: il modello a quattro segni non alza la quota di inventate vicine a parole note (0,545); quasi metà dei campioni del modello sono parole attestate (scartate). Previsioni del sacco intero: N1 0,58–0,65, N2 0,55–0,63, N3 0,53–0,62.

## 3/10/2026, 22:30 — e405 finito: il sacco intero è al pavimento



Risultati nel QUADERNO (voce "vz: e405"). Sacco intero: N1 0,582, N2 0,563, **N3 0,495** (forza 0,37). Parametri del sacco: θ 2280, κ 0,708, parole nuove `FormeUniche(rr, comuni=True, quattro=True, forza=0.37)`.



### Dove siamo (3/10, 22:30)



- Sacco di pagina: chiuso per i giudici (0,495). Disposizione: 0,533 / 0,659 con il sacco vero.

- In preparazione: e406 (posti delle parole nuove dal modello; pesi della disposizione regolati sul sacco generato; versione v8 nel registro; poi banco e293 ai semi 7–9).

- Dopo: materie di pagella mancate (con i valori grezzi dell'e406), ordine delle righe, nascondiglio.

**22:27 — e406 lanciato** (coda `vz-pezzi`; `voynichizzatore/pezzi.py`). Nella prova: i posti dal modello danno 4.829 parole nuove (vere 4.776) con le stesse quote per posto (prima di paragrafo 0,48). Previsioni: P1 0,62–0,70 / 0,72–0,80; P3 0,58–0,66 / 0,68–0,77, pagella 14–16.

## 3/10/2026, 22:45 — e406 finito: generatore a pezzi 0,558 / 0,703; v8 nel registro; banco lanciato



Risultati nel QUADERNO (voce "vz: e406"). P1 0,667 / 0,747; P2 0,670 / 0,744; **P3 0,558 / 0,703**, pagella 13,8. La regolazione dei legami sul sacco generato non converge (unione 2,7, coppia 0): ipotesi, le parole inventate sono meno spesso "due parole note unite" (48% contro 68%). Materie di pagella mancate in 4 semi su 4: legame (confine 0,057 contro 0,188), profilo pagina, verticale, scelte di riga (5 contro 12), concordanza delle desinenze (0,106 contro 0,043), coppie viste altrove.



**v8 = impianto a pezzi** (`versioni.V8`, `pezzi.corpo(seme)`, parametri in `voynichizzatore/pezzi_parametri.json`). Uso: `python voynichizzatore/voynichizzatore.py codifica testo.txt --chiave X --uscita m.txt --versione v8`. Banco: `PROCESSI=4 python esegui.py e293 -- --v8`.



### Dove siamo (3/10, 22:45)



- Generatore intero a pezzi: fatto (v8). In corso: banco e293 della v8 sui semi 7–9 con Isidoro nascosto.

- Elenco di lavoro dopo il banco: (1) legame/confine, verticale, scelte di riga, concordanza delle desinenze (pagella e cancello della riga); (2) parole nuove come unioni di parole note (unioni attestate, regolazione dei legami); (3) ordine delle righe (JSD fra le due metà); (4) nascondiglio (0,63 da solo).

## 3/10/2026, 22:50 — banco della v8: 0,604 / 0,715, decodifica esatta



Nel QUADERNO (voce "vz: e293, banco della v8"). v8: pagella 41/54, estesa 56/78, riga 0, AUC **0,604 / 0,715** con Isidoro nascosto (v5: 49, 57, 0, 0,816 / 0,917). I semi di verifica confermano i semi di ricerca.



### Dove siamo (3/10, 22:50)



- **C'è un generatore intero funzionante** (v8): testo + chiave → manoscritto → testo esatto; molto meno riconoscibile della v5 per i giudici, più debole sulla pagella.

- Prossimo: capire e recuperare le materie di pagella perse, una alla volta, come termini del modello della disposizione regolati sul pannello: prima il legame (confine), poi verticale, scelte di riga, concordanza delle desinenze.

**22:47 — e407 lanciato** (coda `vz-pag`). Conteggio fatto prima: nel Voynich 2,7 punti su 8,8 di unioni attestate vengono da parole uniche = due parole attaccate; nella v8 1,3. Nella prova di costruzione: con le unioni (probabilità 0,25 per le parole nuove di almeno 6 segni) le parole nuove leggibili come due note unite salgono a 0,78 (Voynich 0,81); il termine verticale ha sensibilità circa 0,18 per unità di peso (peso atteso circa 0,13).

## 3/10/2026, 23:05 — e407 finito: 0,541 / 0,659, pagella 16,5; v9 al banco



Nel QUADERNO (voce "vz: e407"). U1 0,548 / 0,659 (15,2); U2 0,559 / 0,673 (16,0); **U3 0,541 / 0,659 (16,5/18)**. Legame e verticale presi in 4 semi. I parametri sono ora separati per versione: `pezzi_parametri_v8.json` (e406), `pezzi_parametri_v9.json` (e407, U3); `pezzi.corpo(seme, 'v9')`.



### Dove siamo (3/10, 23:05)



- v9 = v8 + parole nuove come unioni + confine + verticale. In corso: banco e293 della v9.

- Mancano (4 semi su 4): profilo pagina, prime righe come registro, scelte di riga, concordanza delle desinenze; cancello della riga. Prossimo: e408 (scelte di riga e concordanza delle desinenze come termini di riga nella disposizione).

- Poi: prime righe come registro, profilo pagina, ordine delle righe (JSD fra le due metà), nascondiglio.

**23:04 — e408 lanciato** (coda `vz-riga`). Dal cancello della riga della v9 (valori grezzi dell'e407): S1 circa 1,05–1,13 (soglia ≤ 0,7), A circa 0,96 (≥ 1,0), scelte per riga 0–2 (≥ 3), r fra righe consecutive circa 0,10 (0,207 ± 0,07); R_riga a posto. Nota di progetto: il nascondiglio attuale riscrive le cinque scelte di grafia, quindi il cancello dopo il messaggio dipende dal modello delle scelte; l'alternativa pulita è nascondere il messaggio nel sacco (conteggi delle parole note per pagina: distribuzione multinomiale esplicita, codifica aritmetica su binomiali), lasciando il testo un campione puro del modello. Da fare dopo l'e408.

## 3/10/2026, 23:10 — banco della v9: pagella 44/54, ma 0,668 / 0,719 con il nascondiglio vecchio



Nel QUADERNO (voce "vz: e293, banco della v9"). La v9 senza messaggio fa 0,541 / 0,659 (semi 1–4); con Isidoro nascosto dal nascondiglio vecchio 0,668 / 0,719 (semi 7–9): il nascondiglio riscrive primo e ultimo segno delle parole e rompe confine e unioni. v8 rifatta identica (controllo del codice).



### Dove siamo (3/10, 23:10)



- In corso: e408 (concordanza delle desinenze, scelte di riga).

- In preparazione: e409, il messaggio nel sacco (`voynichizzatore/canale_sacco.py`; preregistrazione committata). È il passo più importante adesso: senza, ogni miglioramento del corpo viene rovinato dal nascondiglio vecchio.

- Dopo: cancello della riga (S1, A, cinque scelte per riga e fra righe), prime righe come registro, profilo pagina.

**23:09 — e409 lanciato** (coda `vz-canale`, corpo di partenza v9; `voynichizzatore/canale_sacco.py`). Prova del codice fatta prima (nessun giudice): Isidoro con la chiave "prova" torna esatto, la chiave sbagliata è respinta, capacità del libro 80.119 bit (servono 38.240; la previsione scritta era 100.000–250.000, quindi più bassa del previsto ma sufficiente), il messaggio occupa 131 pagine su 207; codifica 42 s, decodifica 1 s.

## 3/10/2026, 23:30 — e408 ed e409 finiti



Nel QUADERNO (voci "vz: e408" e "vz: e409").



- **e408:** R1 (peso proprio per il legame fra finali) 0,554 / 0,673, pagella **17,0/18**, concordanza 0,058 (fascia ≤ 0,055: fuori di poco); R2 (+ scelte di riga) 0,582 / 0,671, pagella 16, scelte di riga 8, 11, 10, 8 (soglia 10), perde il gradiente. Nessuno dei due "preso" secondo la preregistrazione. Si tiene R1 come corpo (pesi in `risultati/e408_scelte_di_riga.json`, regolazione → R1 → parametri).

- **e409:** il messaggio nel sacco funziona: andata e ritorno 4 su 4, capacità 80.300 bit, **0,560 / 0,697** contro 0,677 / 0,737 del nascondiglio vecchio sullo stesso corpo, pagella 16,2 contro 15,0. Ma (a) messaggio e (b) riempimento differiscono di 0,037 / 0,042 (previsto ≤ 0,02): in corso l'e409b con altre 8 chiavi (`CHIAVI=5,...,12 CASI=a,b`; nota: queste due variabili non sono fra quelle registrate nella provenienza da `esegui.py`, sono scritte qui).



### Dove siamo (3/10, 23:30)



- Corpo migliore: R1 dell'e408 (da registrare come v10 insieme al canale nuovo, se l'e409b non mostra errori).

- Nascondiglio nuovo: `canale_sacco.codifica(testo, chiave, versione)` / `decodifica(righe, chiave, versione)`.

- Poi: banco con le chiavi banco7–9; cancello della riga (S1, A, cinque scelte per riga e fra righe consecutive); prime righe come registro; profilo pagina; coppie viste altrove.

## 3/10/2026, 23:40 — e409b: canale confermato; v10 registrata; banco lanciato



Nel QUADERNO (voce "vz: e409b"). Su 12 chiavi messaggio e riempimento differiscono di 0,013 / 0,011 (rumore). **v10 = corpo R1 dell'e408 + messaggio nel sacco.** Interfaccia unica: `versioni.codifica(versione, testo, chiave, seme=None)`, `versioni.decodifica(versione, righe, chiave, seme=None)`, `versioni.senza_messaggio(versione, chiave)`. Lo strumento `voynichizzatore.py` prende la v10 come predefinita.



### Dove siamo (3/10, 23:40)



- In corso: banco e293 della v10.

- Poi, nell'ordine: cancello della riga (prima lettera della riga S1; somiglianza fra vicine oltre il caso A; cinque scelte per riga e fra righe consecutive); prime righe come registro; profilo pagina; coppie viste altrove; ordine delle righe (JSD fra le due metà).

## 3/10/2026, 23:45 — banco della v10: 0,550 / 0,662, pagella 50/54; e410 lanciato



Nel QUADERNO (voce "vz: e293, banco della v10"). **La v10 batte la v5 su tutte le colonne** (pagella 50 contro 49, estesa 63 contro 57, AUC 0,550 / 0,662 contro 0,816 / 0,917), con il testo che torna esatto.



e410 (cancello della riga) lanciato nella coda `vz-cancello`. Dalla prova: bersagli del Voynich S1 0,531, somiglianza a distanza 2 0,2198, A 1,047, varianza per riga 1,103, r 0,207; dopo due giri brevi S1 0,64, A 1,03, r 0,15.



### Dove siamo (3/10, 23:45)



- **Versione corrente: v10** (predefinita nello strumento). In corso: e410.

- Dopo: v11 con il cancello della riga, banco; poi prime righe come registro, profilo pagina, coppie viste altrove, ordine delle righe; aggiornare STATO_LAVORI.md e il passaggio di consegne.

## 4/10/2026, 00:00 — e410 finito: cancello della riga in 3 semi su 4; v11 al banco



Nel QUADERNO (voce "vz: e410"). G1 0,555 / 0,639, pagella 16; **G2 0,552 / 0,616, pagella 15,8, cancello 3/4**. Costo: gradiente perso. **v11 = corpo G2 dell'e410 + messaggio nel sacco** (`pezzi_parametri_v11.json`); predefinita nello strumento.



### Dove siamo (4/10, 00:00)



- In corso: banco e293 della v11 (chiavi banco7–9).

- Restano: gradiente e profilo pagina (pagella); differenza fra le due metà della pagina e coppie viste altrove (giudice forte); prime righe come registro, scelte di riga a 12 classi, concordanza delle desinenze, parole rare per pagina (pagella estesa).

## 4/10/2026, 00:05 — banco della v11: cancello 3 su 3; 0,565 / 0,647; pagella 47/54



Nel QUADERNO. v11 contro v10: cancello 3/3 contro 0/3, giudice forte 0,647 contro 0,662, pagella 47 contro 50 (persi gradiente e profilo pagina). Indicazioni di Davide (mezzanotte): andare avanti tutta la notte anche oltre la v11; domattina si pubblica con quello che c'è (repo pubblico separato, licenze da controllare: io preparo l'elenco, non pubblico da solo).



### Dove siamo (4/10, 00:05)



- Versioni verificate al banco: v10 (50/54, senza cancello, 0,550 / 0,662) e v11 (47/54, con il cancello, 0,565 / 0,647).

- Prossimo pezzo (e411): località verticale, cioè righe vicine più simili fra loro di righe lontane; deve dare il gradiente e la differenza fra le due metà della pagina. Poi profilo pagina.

**00:02 — e411 lanciato** (coda `vz-grad`): H1 carattere per posizione nella parola (κ e θ regolati di nuovo), H2 anche vicinato fra righe (peso regolato sul gradiente della pagella). Piano della notte, confermato a Davide: (1) e411 → v12 → banco; (2) coppie viste altrove e differenza fra le due metà della pagina (giudice forte); (3) prime righe come registro, scelte di riga a 12 classi, concordanza delle desinenze; (4) nota per la pubblicazione (che cosa va nel repo pubblico, quali file derivano dalla trascrizione, licenze da controllare) e aggiornamento del passaggio di consegne. Regole: una preregistrazione per passo, due tentativi per strada, un esperimento alla volta in misura (≤ 10 processi).

## 4/10/2026, 00:40 — e411: negativo; difetto del metro sul gradiente



Nel QUADERNO (voce "vz: e411"). H1 (carattere per posizione) non passa (profilo pagina in 2 semi su 4, giudici +0,04 / +0,03); H2 (vicinato) sbagliato e scartato. **Il Voynich vero, misurato dalla nostra pagella, perde il gradiente (0,683 < 0,70): il massimo per seme è 17/18.** Codice: `sacco.POSIZIONALE` e il peso `vicinato` restano nel codice, spenti in tutte le versioni.



### Dove siamo (4/10, 00:40)



- Versioni al banco: v10 (50/54 senza cancello; 0,550 / 0,662), v11 (47/54 con il cancello 3/3; 0,565 / 0,647). Leggere le pagelle su 51 (17 × 3), non su 54.

- Prossimo (e412): il giudice forte. Due caratteristiche lo tengono sopra 0,6: coppie viste altrove (0,246 contro 0,221) e differenza fra le due metà della pagina (JSD 0,038 contro 0,050).

**00:39 — e412 lanciato** (coda `vz-forte`). Dalla prova: con il peso delle metà circa 1,9 la JSD fra le due metà è 0,0497 (Voynich 0,0503); un peso di 20 era troppo (JSD 0,24) e sballava gli altri valori, quindi la regolazione parte da 2.

## 4/10/2026, 01:00 — e412: giudice forte a 0,604; v12 al banco



Nel QUADERNO (voce "vz: e412"). M1 (coppia negativa) non serve da solo; **M2 (+ metà della pagina) 0,566 / 0,604, G9 0,54, cancello 3/4, pagella 15,0** (persa l'omogeneità). **v12 = corpo M2 + messaggio nel sacco** (`pezzi_parametri_v12.json`).



### Dove siamo (4/10, 01:00)



- In corso: banco e293 della v12.

- Tre versioni a pezzi con compromessi diversi: v10 (più materie, senza cancello), v11 (cancello), v12 (cancello e giudice forte più basso, meno materie).

## 4/10/2026, 01:10 — banco della v12: 0,546 / 0,600; bilancio della notte

Nel QUADERNO (voce "vz: e293, banco della v12"). **v12: decodifica esatta, AUC 0,546 / 0,600, pagella 45/54 (massimo
raggiungibile 51), estesa 62/78, cancello 2 su 3.** I due giudici sono all'obiettivo di misura; la pagella no.

### Bilancio (dalle 19:45 del 3/10 all'1:10 del 4/10)

| passo | che cosa | esito |
|---|---|---|
| e400 | scala dei controlli | contano i bordi della riga; nascondiglio vecchio 0,63 da solo |
| e401, e401b | disposizione | con il sacco vero 0,53 / 0,66 |
| e402 | sacco dei generatori vecchi | il muro era il sacco |
| e403, e403b, e405 | parole nuove | forma imparata sulle parole uniche; sacco intero 0,495 |
| e404, e404b | parole note | lessico di sezione + carattere di pagina: 0,48 |
| e406 | generatore intero a pezzi (v8) | 0,604 / 0,715 al banco |
| e407 | unioni, confine, verticale (v9) | pagella 16,5; il nascondiglio vecchio la rovina al banco |
| e408 | concordanza, scelte di riga | migliorano senza passare; pagella 17 |
| e409, e409b | messaggio nel sacco (v10) | 0,550 / 0,662 al banco, pagella 50 |
| e410 | cancello della riga (v11) | cancello 3 su 3 al banco; 0,565 / 0,647 |
| e411 | profilo pagina, gradiente | negativo; difetto del metro: il Voynich perde il gradiente |
| e412 | metà della pagina (v12) | 0,546 / 0,600 al banco |

### Dove siamo (4/10, 01:10)

- **Versioni a pezzi, tutte con il messaggio nel sacco e il testo che torna esatto:** v10 (più materie: 50/54, senza
  cancello, 0,550 / 0,662), v11 (cancello 3/3, 47/54, 0,565 / 0,647), v12 (0,546 / 0,600, cancello 2/3, 45/54). Lo
  strumento usa l'ultima (v12); `--versione v10` o `v11` per le altre.
- **Lacune dichiarate:** profilo pagina (R 0,7–0,8 contro 0,8–1,25); coppie viste altrove (0,245 contro 0,221);
  scelte di riga a 12 classi (un peso unico non basta); concordanza delle desinenze (0,057 contro 0,043, fascia fino a
  0,055); omogeneità (persa nella v12); prime righe come registro (z 2–3 contro la soglia 3); gradiente (materia mal
  posta nel metro).
- **Idee per il seguito, non provate:** (1) abbassare la somiglianza nella riga regolando anche su quella (omogeneità);
  (2) un peso per classe nelle scelte di riga; (3) un registro delle prime righe nel sacco (lessico proprio delle
  prime righe); (4) un giudice indipendente, costruito dalla chat di ricerca; (5) cifratura robusta (scrypt, HMAC) e
  prova di andata e ritorno su un'altra macchina; (6) togliere dal generatore le dipendenze dagli esperimenti e
  preparare il repo pubblico secondo `voynichizzatore/PUBBLICAZIONE.md`.
- **Da decidere con Davide:** quale versione pubblicare (v10, v11 o v12) e per quale strada (solo codice, o anche le
  statistiche: vedi la nota per la pubblicazione).

## 4/10/2026, 01:20 — la v12 su 12 chiavi: 0,576 / 0,619

Nel QUADERNO. **Stima migliore della v12: e231 0,576 ± 0,007, e266 0,619 ± 0,009** (12 chiavi); cancello 11 su 12;
pagella 15/18 sempre. Lo 0,600 del banco era rumore favorevole: il giudice forte è circa 0,02 sopra l'obiettivo.
Corretto un errore in `e409_messaggio_nel_sacco.py` (la tabella .md falliva senza il caso (b)).

### Dove siamo (4/10, 01:20)

- v12: e231 sotto l'obiettivo, e266 a 0,62, pagella 15/18 (massimo 17), cancello quasi sempre. Per confrontare alla
  pari v10 e v11 servirebbe la stessa replica su 12 chiavi (`VERSIONE=v10 CHIAVI=1,...,12 CASI=a,b`).
- Prossimi passi possibili (nessuno iniziato): omogeneità (abbassare la somiglianza nella riga), scelte di riga per
  classe, registro delle prime righe, giudice indipendente, pubblicazione.

## 4/10/2026, 01:35 — v10, v11, v12 su 12 chiavi; fine del lavoro della notte

Nel QUADERNO (ultima voce). Stime a 12 chiavi (da usare al posto dei numeri del banco a tre chiavi):

| versione, 12 chiavi | AUC e231 | AUC e266 (min – max) | pagella (massimo 17) | materie aggiunte | cancello della riga | decodifica |
|---|---|---|---|---|---|---|
| v10 | 0,572 ± 0,006 | 0,690 ± 0,006 (0,663 – 0,724) | 16,7 | 4,1 su 8 | 0 su 12 | 12 su 12 |
| v11 | 0,579 ± 0,005 | 0,634 ± 0,007 (0,596 – 0,687) | 14,9 | 4,5 su 8 | 9 su 12 | 12 su 12 |
| **v12** | 0,576 ± 0,007 | **0,619 ± 0,009** (0,585 – 0,669) | 15,0 | 5,2 su 8 | **11 su 12** | 12 su 12 |

### Dove siamo (4/10, 01:35) — punto di ripartenza

- **Versione consigliata: v12** (predefinita nello strumento). Domina la v11. La v10 resta come alternativa se conta di
  più la pagella a 18 materie che il cancello della riga e il giudice forte.
- **Rispetto all'obiettivo:** giudice dell'e231 sotto 0,6 (0,576); giudice dell'e266 a 0,619, cioè 0,02 sopra;
  pagella 15 su 17 raggiungibili; cancello della riga 11 chiavi su 12; testo sempre esatto.
- **Lacune dichiarate, in ordine di peso:** profilo pagina (mai preso); scelte di riga a 12 classi (mai prese);
  omogeneità (persa nella v12); coppie viste altrove; prime righe come registro; concordanza delle desinenze;
  dispersione delle lunghezze. Il gradiente è mal posto nel metro.
- **Niente è in esecuzione.** Tutto è committato e sul remoto privato. Niente è stato pubblicato.
- **Per riprendere:** leggere questa sezione, la voce "Bilancio" delle 01:10 e `voynichizzatore/PUBBLICAZIONE.md`.
  Regola pratica imparata stanotte: vicino a una soglia servono 12 chiavi, non 3
  (`VERSIONE=vNN CHIAVI=1,...,12 CASI=a PROCESSI=9 python esegui.py e409`).

## 4/10/2026, 06:25 — ripresa: Davide rimanda le decisioni e chiede di migliorare la v12



Alle 6:00 Davide ha risposto a quattro domande (pubblicazione con la v12, codice più statistiche, cifratura robusta), poi ha cambiato idea: **continuare a migliorare la v12 fino al mattino dopo; le decisioni si prendono allora.** Annotato in `PUBBLICAZIONE.md` che il sito della trascrizione dichiara la licenza CC0 per le trascrizioni (letto da un riassunto automatico: da ricontrollare a mano).



Diagnosi della v12 su 12 chiavi (gruppi dell'e266: G8 0,67, G3 0,65, G4 0,58, G7 0,57). Caratteristiche pesanti con causa leggibile nel sacco: *y*+*o* dentro le parole (unioni non controllate alla giuntura), quota fra le 100 più frequenti (0,440 contro 0,424), JSD pagina-manoscritto (0,045 contro 0,040). **e413 lanciato** (coda `vz-ritocchi`): S1 unioni ben formate; S2 anche κ regolata sul sacco completo ed esponente γ sulla frequenza. Misura su 12 chiavi per strato. D'ora in poi ogni confronto si fa su 12 chiavi.

## 4/10/2026, 06:35 — e413: v13 a 0,582 / 0,605 su 12 chiavi

Nel QUADERNO (voce "vz: e413"). S1 (unioni ben formate) inutile: *y*+*o* non cala (88 nelle parole nuove contro 27 nel
Voynich; il filtro è troppo largo). **S2 → v13: 0,582 ± 0,006 / 0,605 ± 0,006**, coppie viste altrove a posto (0,226),
cancello 9 su 12, pagella 15,2. Costo: tipi su parole 0,771 (troppo vari).

### Dove siamo (4/10, 06:35)

- **v13 è la versione migliore per i giudici** (predefinita nello strumento); la v12 ha il cancello più spesso (11 su 12).
- Prossimo (e414): giuntura delle unioni giudicata per probabilità (soglia sulla probabilità condizionata delle due
  terne di giuntura), per togliere *y*+*o*; poi tipi su parole (0,771), prime righe (G8 0,65), inizio riga con *ch*.

**06:27 — e414 lanciato** (coda `vz-giuntura`). Dalla prova: con la soglia 0,05 sulla probabilità delle terne di giuntura, *y*+*o* nelle parole nuove scende da 88 a 41 (Voynich 27). Fra tipi su parole e quota fra le 100 più frequenti c'è un compromesso (due manopole, tre bersagli).

## 4/10/2026, 06:50 — e414: v14 a 0,566 / 0,591 su 12 chiavi

Nel QUADERNO (voce "vz: e414"). J1 (giuntura probabile, soglia 0,05) → **v14: 0,566 ± 0,010 / 0,591 ± 0,009**, pagella
15,2, estese 6,2, cancello 9 su 12, decodifica 12 su 12. J2 (tre bersagli) peggio: non tenuto.

### Dove siamo (4/10, 06:50)

- **v14 è la versione migliore** (predefinita nello strumento). In corso: conferma su 12 chiavi nuove
  (`VERSIONE=v14 CHIAVI=13,...,24 CASI=a`).
- Restano: profilo pagina, omogeneità, scelte di riga a 12 classi, tipi su parole (0,771), cancello (9 su 12),
  G8 prime righe (0,65), G3 (0,63).

## 4/10/2026, 07:00 — conferma della v14 su chiavi nuove: 0,584 / 0,609

Nel QUADERNO. Chiavi 13–24: **0,584 ± 0,007 / 0,609 ± 0,005**; su 24 chiavi 0,575 / 0,600; cancello 19 su 24; testo
esatto 24 su 24. Le chiavi 1–12 erano ottimiste (effetto della scelta fra J1 e J2).

### Dove siamo (4/10, 07:00) — punto di ripartenza

- **Versione migliore: v14** (predefinita nello strumento). Giudice dell'e231 a 0,58 (sotto l'obiettivo), dell'e266 a
  0,60–0,61 (sulla soglia), pagella 15,2 su 17 raggiungibili, materie aggiunte circa 6 su 8, cancello della riga in
  circa 4 chiavi su 5, testo sempre esatto, capacità circa 82.000 bit.
- **Catena delle versioni a pezzi:** v8 (e406) → v9 (e407: unioni, confine, verticale) → v10 (e408 R1 + messaggio nel
  sacco) → v11 (e410: cancello) → v12 (e412: metà della pagina) → v13 (e413: κ e γ sul sacco completo) → v14 (e414:
  giuntura delle unioni).
- **Regola pratica:** confronti su 12 chiavi; quando si sceglie fra varianti, conferma su 12 chiavi nuove.
- **Lacune dichiarate:** profilo pagina; scelte di riga a 12 classi; omogeneità; tipi su parole (0,771 contro 0,756);
  prime righe come registro (G8 0,65); cancello non sempre (A appena sotto 1,0 in alcune chiavi).
- **Niente è in esecuzione.** Tutto è committato e sul remoto privato. Niente è stato pubblicato. Le decisioni sulla
  pubblicazione sono rimandate da Davide al mattino (vedi `PUBBLICAZIONE.md`, con la nota sulla licenza CC0 da
  ricontrollare a mano).

## 4/10/2026, 09:00 — nota per il white paper (indicazione di Davide)



Davide, sentendo la spiegazione, ha chiesto di **dirlo molto bene nel white paper del generatore e anche nell'altro** (quello sul Voynich). Il punto, da scrivere con cura quando Davide dirà di scrivere i white paper:



- Un manoscritto del voynichizzatore **con** un testo nascosto e uno **senza** non si distinguono fra loro (e409b: su 12 chiavi i due giudici danno 0,560 / 0,682 con il messaggio e 0,547 / 0,671 senza, differenza entro l'errore), perché il messaggio cifrato fa da dado al modello invece di essere aggiunto sopra il testo.

- Senza la chiave il testo non si legge, e non c'è niente da tradurre parola per parola: le parole non corrispondono al messaggio, che sta in quante volte ogni parola compare in ogni pagina.

- **È la stessa situazione del Voynich vero:** un testo con queste statistiche può portare un messaggio oppure no, e dalle statistiche non si può dire quale delle due. Il voynichizzatore è la dimostrazione costruttiva che un testo "alla Voynich" con un contenuto recuperabile e uno senza contenuto sono indistinguibili per le misure note; quindi quelle misure, da sole, non possono decidere se il Voynich ha un significato.

- Cautele da scrivere insieme: vale per i due giudici e la pagella di questo progetto; il manoscritto generato si riconosce come generato (stessa impaginazione del Voynich, parole del suo lessico; giudice forte a 0,60–0,61; due materie mai prese); la capacità è circa 80.000 bit per libro, molto meno di un testo in chiaro della stessa lunghezza.



La chat di ricerca può riprendere questa nota per il dossier (`DOSSIER_WHITE_PAPER.md` è suo).

## 4/10/2026, 09:35 — v15 (cifratura), v16 e v17 (gabbie), pacchetto pubblico

Decisioni di Davide del mattino: si pubblica la v14 (poi le sue discendenti), codice più dati; cifratura robusta; il
giudice indipendente si valuta dopo. Licenza della trascrizione riletta sul sito: pubblico dominio, CC0, con richiesta
di citare la fonte (`PUBBLICAZIONE.md` §7). Idea di Davide: la gabbia delle pagine non deve essere quella della pagina
vera.

Nel QUADERNO (voce "vz: e415"). Su 12 chiavi: v15 0,570 / 0,601; v16 (gabbia di un'altra pagina) 0,564 / 0,598; **v17
(gabbia statistica) 0,563 / 0,601, cancello 11/12**. Le tre sono pari: la gabbia vera non serviva.

### Dove siamo (4/10, 09:35)

- Versioni: v15 = v14 + cifratura robusta; v16 = v15 + gabbia da un'altra pagina; v17 = v15 + gabbia statistica.
  Parametri `impaginazione` ("altra pagina" o "statistica") e `cifra` ("scrypt") nei file `pezzi_parametri_vNN.json`.
- Pacchetto pubblico: `python strumenti/costruisci_pubblico.py` (costante `VERSIONE` in testa allo script, ora v15) →
  `pubblico/voynichizzatore/`. Mancano: README con i numeri, scelta della versione (v15, v16 o v17), eventuale prova
  su un altro computer.
- Nota per i white paper nel diario (voce delle 09:00): con e senza messaggio indistinguibili, come per il Voynich.

## 4/10/2026, 09:50 — Davide sceglie la v17; pacchetto pubblico pronto (non pubblicato)

- **Decisione di Davide: si pubblica la v17** (v14 + cifratura robusta + gabbia statistica).
- `strumenti/costruisci_pubblico.py` (VERSIONE = 'v17') costruisce `pubblico/voynichizzatore/` (17 file): moduli del
  generatore, pezzi estratti dagli esperimenti, `voynich_zl3b.json` (testo corrente del Voynich ripulito, con la fonte),
  `voynichizzatore.py` (codifica, decodifica, vuoto), `LEGGIMI.md` con i numeri e i limiti, `requirements.txt`.
- Prove sul pacchetto, da solo (senza il resto del repo nel percorso): Isidoro con una chiave a frase torna esatto; la
  chiave sbagliata di una lettera è respinta; il manoscritto vuoto non restituisce niente; il manoscritto è identico
  byte per byte a quello prodotto dal repo con la v17 e la stessa chiave.

### Dove siamo (4/10, 09:50) — punto di ripartenza

- **Versione corrente e da pubblicare: v17.** Su 12 chiavi: e231 0,563 ± 0,008, e266 0,601 ± 0,006, pagella 15,0 su 17
  raggiungibili, materie aggiunte 5,8 su 8, cancello 11 su 12, testo esatto 12 su 12.
- **Niente è stato pubblicato.** Prima di pubblicare restano, e sono decisioni di Davide: (1) la licenza del programma;
  (2) dove (nome e proprietario del repo pubblico; eventuale sito); (3) se fare prima la prova su un secondo computer;
  (4) se aspettare un giudice indipendente; (5) il via esplicito.
- Miglioramenti possibili, non iniziati: omogeneità, scelte di riga per classe, profilo pagina, registro delle prime
  righe, tipi su parole; uscita come immagine.

## 4/10/2026, 10:15 — pacchetto con licenza MIT e prova di rilettura; repo locale pronto, pubblicazione in attesa



Decisioni di Davide: licenza MIT; GitHub suo (sito web più avanti); prova su un altro computer preparata da me e fatta da lui; giudice indipendente dopo; **via libera alla pubblicazione**.



- Il pacchetto (`strumenti/costruisci_pubblico.py`) ha ora `LICENSE` (MIT, Davide Caniatti 2026), `README.md`, `.gitignore`, `prova.py` e `prova/` (testo di prova e manoscritto scritto su questo computer con la chiave "prova di rilettura su un altro computer"). `python prova.py` qui: 1 SI, 2 SI, 3 SI (Python 3.12.10, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, Windows).

- **Repo locale da pubblicare:** `C:\Users\davide\voynichizzatore` (copia del pacchetto, un commit `86193ef`, autore con l'indirizzo anonimo di GitHub `AndreottiVIII@users.noreply.github.com` per non esporre l'email personale in un repo pubblico; fine riga LF).

- **Non ancora pubblicato:** su questa macchina non c'è lo strumento `gh` e l'estensione di Chrome non è collegata, quindi non posso creare il repo su GitHub. Serve che Davide crei il repo pubblico vuoto `AndreottiVIII/voynichizzatore` (senza README né licenza); poi: `git -C /c/Users/davide/voynichizzatore remote add origin https://github.com/AndreottiVIII/voynichizzatore.git` e `git -C /c/Users/davide/voynichizzatore push -u origin main`.

- Zip per la prova su un altro computer: `pubblico/voynichizzatore_v17.zip` (non committato). Sull'altro computer: Python 3.12, `pip install -r requirements.txt`, `python prova.py`; conta la riga 1.

## 4/10/2026, 10:45 — PUBBLICATO: github.com/AndreottiVIII/voynichizzatore

- Davide ha fatto l'accesso a GitHub nel browser interno dell'app; ho creato il repo pubblico vuoto
  `AndreottiVIII/voynichizzatore` e caricato il pacchetto da `C:\Users\davide\voynichizzatore` (commit `86193ef`, poi
  `7a802d3`).
- Su richiesta di Davide istruzioni, comandi e messaggi sono **in inglese**: i testi stanno in
  `strumenti/pubblico_testi.py` e li usa `strumenti/costruisci_pubblico.py`. Comandi `encode` / `decode` / `empty` con
  `--key` e `--out` (i nomi italiani restano come alias). I commenti nel codice restano in italiano.
- Autore dei commit pubblici: Davide Caniatti con l'indirizzo anonimo di GitHub. Licenza MIT.
- **Per aggiornare il repo pubblico:** `python strumenti/costruisci_pubblico.py`; copiare `pubblico/voynichizzatore/.` in
  `C:\Users\davide\voynichizzatore\` (che tiene il suo `.git`); commit e push da lì.
- Resta in italiano la descrizione breve del repo su GitHub (non sono riuscito ad aprire la finestra di modifica dal
  browser interno): la cambia Davide, o si riprova.
- Prova su un altro computer: `pubblico/voynichizzatore_v17.zip` oppure il repo pubblico; `python prova.py`; conta la
  riga 1. **Non ancora fatta.**

### Dove siamo (4/10, 10:45)

- **Pubblicata la v17.** In sospeso: esito della prova su un altro computer (poi aggiornare la frase nel README),
  descrizione del repo in inglese, giudice indipendente, sito web, uscita come immagine, miglioramenti (omogeneità,
  scelte di riga, profilo pagina).

## 4/10/2026, 11:30 — Dal testo EVA alle pagine: carattere nostro e PDF del libro

Richiesta di Davide: l'uscita non deve restare in lettere EVA, deve diventare una scrittura "come il Voynich". Scelte
sue: **carattere nostro, disegnato da noi** (non il font EVA Hand 1 di Landini, che non è per uso commerciale) e uscita
come **PDF del libro**.

- `voynichizzatore/carattere.py`: ogni segno EVA è descritto a tratti (linee e archi); il programma li ingrossa come
  una penna, ne ricava i contorni e scrive `voynichizzatore/VoynichizzatoreEVA.ttf` (fontTools). I segni composti
  (`ch sh cth ckh cph cfh`) sono segni a sé, in codici privati; `in_segni(parola)` fa la conversione. Per rifare il
  font servono pillow e scikit-image; per usarlo no (il file .ttf è nel repo e nel pacchetto).
- `voynichizzatore/pagine.py`: legge il file del manoscritto e scrive un PDF, una pagina per pagina, paragrafi staccati,
  carta color pergamena. Il corpo si adatta alla pagina; le poche righe molto più lunghe delle altre sono scritte più
  strette. Solo testo, niente disegni. Il libro intero (207 pagine) si fa in circa 10 secondi, 0,6 MB.
- Strumento: `python voynichizzatore/voynichizzatore.py pdf manoscritto.txt --uscita libro.pdf`; nel pacchetto pubblico
  `python voynichizzatore.py pdf manuscript.txt --out book.pdf` (aggiunti `matplotlib` e `fonttools` ai requisiti).
- Prova: `esecuzioni/voynichizzatore/libro_v17.pdf` (dal manoscritto di Isidoro v17). Il pacchetto pubblico ricostruito
  (24 file) fa il PDF e rilegge ancora il manoscritto di prova.
- **Cosa non è:** il carattere imita le forme, non è la mano dello scriba; ogni segno è sempre identico (nessuna
  variazione di penna), niente disegni, niente etichette o testo circolare. Non è passato da nessun giudice: è solo la
  veste grafica, le misure restano quelle sul testo EVA.
- **Difetto notato guardando le pagine:** nel manoscritto v17 ci sono più righe "troppo lunghe" che nel Voynich vero
  (righe oltre una volta e mezza la mediana della pagina: 5,3% contro 2,9%). Viene dall'impaginazione statistica della
  v17. Da correggere in una prossima versione (va preregistrato: cambia il manoscritto).

### Dove siamo (4/10, 11:30)

- Carattere e PDF fatti e committati nel repo privato. **Il repo pubblico non è ancora aggiornato** con questo passo:
  aspetto che Davide guardi il PDF e dica se va bene.
- In sospeso come prima: prova su un altro computer, giudice indipendente, sito web, miglioramenti (omogeneità, scelte
  di riga, profilo pagina, righe troppo lunghe).

## 4/10/2026, 12:00 — Repo pubblico aggiornato; scheda per il sito

- Repo pubblico aggiornato col comando `pdf`, il carattere e `pagine.py` (commit `c08394b`), su richiesta di Davide.
- Scritta `voynichizzatore/SITO_WEB.md`: scheda autosufficiente per la chat che costruirà il sito (comandi, tempi misurati, formati, scelte tecniche, cosa si può dire e cosa no, licenze). Il sito deve offrire tutte e due le vesti: EVA e voynichese in PDF. Attenzione: si rilegge solo dal file EVA, non dal PDF.
- Tempi misurati: encode 105 s, decode 5 s, pdf 9 s.

## 4/10/2026, 13:00 — Carattere ritoccato (versione 1.1)

- Davide ha visto il confronto (`esecuzioni/voynichizzatore/carattere_confronto.png`) e ha approvato: forche con gambe vicine e inclinate, cappi piccoli e tondi, barra curva; la "l" con occhiello in basso e due braccia. Font rifatto, PDF di prova rifatto, pacchetto pubblico aggiornato.
- Righe troppo lunghe: la causa è che la v17 fissa le *parole* per riga e non lo spazio (in parole 3,8% contro 3,2% del vero; in caratteri 5,3% contro 2,9%; soglia 1,25: 18% contro 6%). Davide ha approvato un esperimento (e416): nuova regola nella disposizione che pareggia la larghezza in caratteri. Se migliora diventa v18 e va online.

## 4/10/2026, 10:50 — Sito web: scelte di Davide e prova del browser (chat del sito)

- Scelte di Davide: GitHub Pages, indirizzo gratuito, codice in `docs/` del repo pubblico; pagine Write (con un
  amanuense che scrive durante l'attesa), Read (decifratore), How it works (procedimento passo per passo, rigoroso),
  spazio per le ricerche. Dettagli in `SITO_WEB.md`, §11.
- **Prova del browser (passo 0) riuscita:** il pacchetto v17 senza modifiche gira in Pyodide 314; manca solo
  `hashlib.scrypt`, fornito da JavaScript con risultato identico. Rilettura nei due sensi (PC → browser e browser → PC)
  riuscita; scrittura 214 s; memoria circa 480 MB; primo accesso circa 27 MB + 10 MB per il PDF.
- **Il manoscritto scritto nel browser è diverso da quello del PC** ma ha le stesse parole in ogni pagina (207 su 207):
  cambia solo l'ordine nelle righe, che non porta informazione. Sul PC il programma è deterministico anche con semi di
  hash diversi. Prima prova di rilettura in un ambiente diverso (§10 della scheda): passata, ma con una sola chiave.
  Numeri in `SITO_WEB.md`, §12.
- Per la v18 (e416): il sito terrà ogni versione in una cartella sua, così la v17 resta leggibile.

## 4/10/2026, pomeriggio — Sito web: prima versione funzionante (chat del sito)

- **Dove:** `C:\Users\davide\voynichizzatore_sito`, worktree del repo pubblico sul ramo locale `sito`, cartella `docs/`.
  Niente committato né pubblicato. La copia `C:\Users\davide\voynichizzatore` (quella dell'altra chat) non è toccata.
- **Com'è fatto:** cinque pagine statiche (Write, Read, How it works, Research vuota, About). Il programma v17 è
  copiato senza modifiche in `docs/engine/v17/` da `docs/engine/build_engine.py`, con le impronte SHA-256 e il
  commit (`182056e`). Gira in un web worker con Pyodide 314.0.7; `scrypt` viene da `@noble/hashes` 2.4.0, copiata in
  `docs/js/noble-hashes/`. L'avanzamento pagina per pagina si legge avvolgendo da fuori `canale_sacco.distribuzione` e
  `Disposizione.pagina`, senza cambiare il calcolo. Fasi misurate sul PC (107 s): modello 9 s, parole 7 s,
  disposizione 87 s, verifica 2 s.
- **Amanuense:** una penna d'oca scrive voynichese di fantasia su un foglio; l'angolo mostra il foglio vero in lavorazione.
- **Aspetto:** Davide ha bocciato la prima bozza ("libro miniato"). Ha chiesto di prendere l'aspetto dal Voynich vero:
  pergamena su nero come nelle foto della Beinecke, inchiostro bruno, e un disegno vero per pagina (f9v, f67r, f88r,
  f75r, f33v). I disegni sono tolti dallo sfondo e fusi sulla pergamena (`mix-blend-mode: multiply`). La pergamena è
  la grana del foglio di guardia tinta col colore dei fogli. Le immagini stanno in `docs/img/` e sono fatte dallo
  script della sessione dalle foto in `dati/cache/immagini`. **Da decidere con Davide prima di committarle:** Yale le
  dà in open access per le opere di pubblico dominio ("may be used by anyone for any purpose"), ma il manifesto IIIF
  riporta solo un avviso generico.
- **Prove fatte nel browser:** scrittura completa (207 fogli, 4.260 righe, 4 min 36 s con il PC carico), verifica
  interna passata, PDF 0,3 MB, anteprima pagina per pagina; Read: chiave sbagliata rifiutata, testo esatto con quella
  giusta; **il manoscritto fatto dal sito si rilegge col programma da riga di comando sul PC.**
- Da fare: How it works passo per passo; collaudo con più chiavi e testi; telefono; scelta definitiva dell'aspetto;
  pubblicazione solo col via di Davide.

## 4/10/2026, 13:50 — e416 / e416b: righe troppo larghe, due tentativi, resta la v17

- Voce completa nel QUADERNO ("vz: e416 ed e416b"). In breve: termine di larghezza nella disposizione
  (`pesi_disposizione`: `larghezza`, `larghezza_beta` oppure `larghezza_curva`); parametri in `pezzi_parametri_v18.json`
  e `pezzi_parametri_v19.json` (non nel registro `versioni.py`, non pubblicate).
- v19: righe oltre 1,5 volte come nel Voynich (2,8% contro 2,9%), oltre 1,25 da 16,7% a 11,4% (Voynich 6,0%), giudici
  0,551 / 0,596 (v17: 0,563 / 0,601), ma **cancello della riga 4 su 12** (v17: 11 su 12) per la soglia A ≥ 1,0
  (A media 0,999 contro 1,009). Per i criteri preregistrati non sostituisce la v17.
- Errore mio da ricordare: il font nel repo pubblico era stato rovinato dalla conversione dei fine riga
  (`.gitattributes` con `* text eol=lf`); corretto con `*.ttf binary`. Controllare sempre i file binari dopo il push
  (`git show HEAD:file | cmp - file`).
- Code lanciate con `esecuzioni/vz_v18.sh` e `vz_v19.sh` (e416/e416b, poi e409 con VERSIONE, CHIAVI=1..12, CASI=a).

### Dove siamo (4/10, 13:50)

- Online: v17 + comando `pdf` + carattere 1.1. La v19 è pronta ma non pubblicata: aspetta la decisione di Davide
  (seguito possibile: regolare di nuovo il peso `scelte` sulla v19 per riportare il cancello, esperimento nuovo).
- Scheda per il sito: `voynichizzatore/SITO_WEB.md` (il sito lo costruisce un'altra chat; il generatore resta qui).

## 4/10/2026, 16:00 — e417: la v20 passa i criteri ed è la versione pubblicata

- Voce completa nel QUADERNO ("vz: e417"). v20 = v17 + `larghezza` 0,01 con `larghezza_curva` (e416b) + `distanza2`
  0,30 (e417). Parametri: `voynichizzatore/pezzi_parametri_v20.json`; nel registro `versioni.py` (la v18 e la v19 no).
- 12 chiavi: giudici 0,554 / 0,599; pagella 15,6; estese 5,4; cancello 12 su 12; righe oltre 1,5 volte 2,8% (Voynich
  2,9%), oltre 1,25 volte 11,5% (Voynich 6,0%, v17 16,7%); rilettura 12 su 12.
- Correzione mia: A non è "l'accordo delle scelte di grafia" (come avevo detto a Davide) ma l'alternanza nella riga;
  il peso che la muove è `distanza2`. Scritto nella preregistrazione.
- Pacchetto pubblico ricostruito con `VERSIONE = 'v20'`; README aggiornato (numeri, larghezza delle righe, nota che i
  manoscritti v17 si leggono con la v20: verificato). Pubblicato su GitHub.
- Esempio: `esecuzioni/voynichizzatore/repo_isidoro_v20.txt` (chiave "e409-1") e `libro_v20.pdf`.

### Dove siamo (4/10, 16:00)

- Online: **v20** + comando `pdf` + carattere 1.1. Il sito lo costruisce un'altra chat con `SITO_WEB.md`.
- Lacune dichiarate: righe oltre 1,25 volte ancora 11,5% (per chiuderla va cambiata la gabbia: parole per riga decise
  dopo aver scelto le parole), profilo pagina, scelte di riga a 12 classi, omogeneità, prime righe, gradiente.
- In sospeso: prova su un altro computer, giudice indipendente.

## 4/10/2026, sera — Sito web: aspetto dal Voynich vero, v20, How it works tecnica (chat del sito)

- Aspetto rifatto dalle foto della Beinecke (Davide: "molto meglio"; immagini di Yale confermate, "usane di più"):
  disegni ripuliti dallo sfondo e foto dei 207 fogli accanto ai fogli generati.
- Sito portato alla **v20**. Capienza osservata 80.344–84.678 bit; controllo anticipato del testo troppo lungo nel
  motore del sito (stesso messaggio del programma, calcolo invariato).
- How it works riscritta, esauriente e tecnica (indicazione di Davide). Dettagli e difetto trovato in `disposizione.py`
  (conteggi delle scelte mai inizializzati, v17 e v20): `SITO_WEB.md`, §13.
- Collaudo v20 in corso: 5 casi (corto, italiano, misto Unicode, quasi pieno, senza messaggio) scritti sul PC e nel
  browser, letture incrociate, manoscritti v17 letti con la v20, chiave sbagliata, sacchi identici, ripetibilità.

## 4/10/2026, 16:30 — Conferma della v20 su chiavi nuove: i numeri da citare cambiano

- v20 su 24 chiavi: **0,560 ± 0,005 / 0,607 ± 0,005**, pagella 15,7, cancello 24 su 24, rilettura 24 su 24.
  v17 sulle stesse 24: 0,559 / 0,597, pagella 15,0, cancello 18 su 24. Differenza appaiata sul secondo giudice
  +0,010 ± 0,006 (v20 forse un filo peggiore; dentro la tolleranza di 0,015 scritta prima).
- Le prime 12 chiavi erano ottimiste (0,554 / 0,599). README pubblico corretto: 0,56 / 0,61 su 24 chiavi.
- Regola da tenere: ogni versione nuova va confermata su chiavi nuove **prima** di citarne i numeri.
- Sicurezza (domanda di Davide): la chiave passa per scrypt (n = 2^15) con sale fisso; regge solo se la chiave è lunga
  e casuale (consiglio: 6 parole a caso o 12 caratteri a caso). Possibile miglioria: alzare il costo di scrypt
  (versione nuova). Da dire nel sito.
- Collaudo v20 superato in tutti e cinque i casi e in tutti i sensi (tabella in `SITO_WEB.md`, §13, e in How it works);
  trovato e corretto un difetto del sito sul libro senza messaggio (`JsNull`). Il sito presenta il libro come "un
  secondo Voynich", come chiesto da Davide.

## 4/10/2026, 17:40 — e418: difetto nella disposizione corretto, v21 pronta (non ancora pubblicata)

- Voce completa nel QUADERNO ("vz: e418"). Difetto mio dell'e412, trovato dalla chat del sito: conteggi delle scelte
  di riga mai inizializzati da v12 a v20. Corretto dietro `conti_iniziali` nei pesi della disposizione.
- v21 = v20 + `conti_iniziali` (stessi pesi; la regolazione non li cambia). Parametri
  `voynichizzatore/pezzi_parametri_v21.json` (uguale a `_v21f1.json`), nel registro `versioni.py`.
- 24 chiavi: 0,554 ± 0,004 / 0,601 ± 0,005 (v20: 0,560 / 0,607), pagella 16,0, cancello 24 su 24, rilettura 24 su 24.
- Lezione: rileggere il diff quando si inserisce un blocco in mezzo a una funzione; un controllo semplice sarebbe
  bastato (stampare i conteggi iniziali). La revisione di un'altra chat sul codice pubblico l'ha trovato in un giorno.
- Dalla chat del sito: capienza con cinque chiavi 80.344–84.678 bit (non 81.000–83.000); collaudo v20 nel browser
  superato (rilettura incrociata PC ↔ browser esatta).

### Dove siamo (4/10, 17:40)

- Online: v20. **v21 pronta nel repo privato; va pubblicata solo quando Davide dice sì** (poi avvisare la chat del
  sito, che aggiunge `docs/engine/v21`). Da aggiornare alla pubblicazione: `VERSIONE` in
  `strumenti/costruisci_pubblico.py`, numeri del README (0,55 / 0,60, pagella 16), capienza "about 80,000–85,000 bits".

## 4/10/2026, 18:00 — v21 PUBBLICATA (Davide: "sì, pubblica la v21 e dì al sito di usare quella")

- Pacchetto pubblico ricostruito con `VERSIONE = v21`; README: giudici 0,55 / 0,60 su 24 chiavi, pagella 16, capienza 80.000-85.000 bit, nota sul difetto corretto e sulla lettura dei manoscritti v17 e v20 (verificata sul pacchetto: letti esatti).
- Avvisata la chat del sito.

### Dove siamo (4/10, 18:00)

- Online: **v21** + comando `pdf` + carattere 1.1. In sospeso: prova su un altro computer, giudice indipendente, righe oltre 1,25 volte (11,6% contro 6,0%), costo di scrypt.
- (sera) Sito: libro illustrato nel browser (disegni veri staccati dal Voynich, PDF con jsPDF, 8 MB); sito passato
  alla v21 dopo la correzione del difetto segnalato; testi con le misure della v21 su 24 chiavi. `SITO_WEB.md`, §13.
- (sera) **Sito pubblicato** su https://andreottiviii.github.io/voynichizzatore/ (richiesta di Davide): pagina Research
  col white paper scaricabile, Read con conferme passo per passo, didascalie col solo codice del foglio. Procedura di
  aggiornamento in `SITO_WEB.md`, §14.

## 4/10/2026, 18:40 — Il sito è online; attenzione al repo pubblico

- Sito pubblicato dalla chat del sito su richiesta di Davide: https://andreottiviii.github.io/voynichizzatore/ (ramo `gh-pages`; usa la v21 in `docs/engine/v21`).
- **Il ramo main del repo pubblico ora contiene anche `docs/` (il sito).** Prima di ogni push dalla copia `C:\Users\davideoynichizzatore`: `git pull`. La copia del pacchetto (`cp -r pubblico/voynichizzatore/. ...`) non tocca `docs/`; non cancellare mai quella cartella.
- A ogni versione nuova: avvisare la chat del sito (aggiunge la cartella del motore; se cambiano i conteggi delle parole tiene anche la vecchia per rileggere).
- Da proporre a Davide: link al sito nel README del programma.
