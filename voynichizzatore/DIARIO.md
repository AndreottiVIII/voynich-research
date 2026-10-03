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
