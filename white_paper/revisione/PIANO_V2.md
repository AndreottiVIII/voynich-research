# Piano della versione 2 del white paper

Punto di ripartenza per qualunque sessione. Verifica delle note del revisore: `VERIFICA_NOTE_REVISORE.md`.

## Decisioni di Davide (8/10/2026)

1. **Struttura B:** un paper unico centrato sul voynichizzatore. Spiega le misure, la pagella estratta dalle misure e il
   generatore. Il generatore va anticipato all'inizio, con risalto (titolo, abstract, introduzione).
2. **Autori:** Claude non è più autore. Il suo uso va descritto nel metodo, senza frasi su responsabilità o regole
   delle riviste.
3. **Repository:** si apre (pubblico).
4. **Codice:** è stato letto. Non aggiungere dichiarazioni sulla revisione del codice.
5. **Rianalisi:** fare tutte quelle proposte. Se finiscono i token, ricominciare la notte.
6. **Lingua:** solo inglese. La versione italiana è ferma.
7. "No fretta e lavora bene."

## Lavori

### 0. Apertura del repo
- [x] Controllo prima di aprire (9/10):
  - storia git (dati protetti mai committati, chiavi o password);
  - email negli autori dei commit;
  - note del revisore;
  - licenze dei file in `dati/`.
- [x] Decisione di Davide (9/10): il repo di lavoro resta privato, si pubblica una **copia** (`strumenti/copia_pubblica.sh`:
  email anonima di GitHub, senza le note del revisore, mappa degli hash in `risultati/provenienza/MAPPA_COMMIT_PUBBLICI.txt`).
- [ ] Davide crea il repo pubblico su GitHub e lo carica; poi aggiornare l'URL di `repository` in `references.bib`.

### 1. Rianalisi (esperimenti nuovi, ognuno con preregistrazione, codice, esecuzione, quaderno)
- [x] e3c84: percentili per lingua, senza lingue artificiali (C1.1): reggono quasi tutti; giuntura 2 lingue su 24, calo 2 su 20
- [x] e3c85 nullo con la grammatica della parola (A7): spazio prevedibile, tagli e riempimento spiegati dalla forma delle parole; giuntura e rispecchiamento no
- [x] e3c86 intervalli per bifoglio e fascicolo (A5): tutto regge per bifoglio; per fascicolo cede solo la deriva di k/t
- [x] e3c88 ripetizioni osservato/atteso (A8): O/E nella riga 1,04 (non evitata, non in eccesso); lingue ≤ 0,92, scribi ≤ 0,79
- [x] e3c89 riga chiusa e margine a 10.000 parole (A8): reggono
- [x] e3c87 raccordo a parità di posizione (Feaster 2022): non viene dalla posizione
- [x] e3c90 potenza per scriba e scelta (A9): deriva assente con potenza 20/29 (corretto: prima 28/29, errore di unità); finestra 14/29, 13 senza potenza, 2 presenti (e3c91: Holm A 10 incerto)
- [x] e3c92 confronti multipli (A3): Holm 23 su 23; Bonferroni su 715 esperimenti 15 su 23
- [x] registro completo degli esperimenti (A2, B12): `registro_esperimenti.csv`, 716 righe
- [x] e3c94 controllo a campione sulle immagini (A11): nessuna q nascosta dopo il disegno (0 su 16, 3 incerte); -m di fine riga 5 su 6 chiare
- [x] e3c93 voynich-fingerprint: giuntura sì, riga chiusa e margine no (anche il manuale a mano); nel §6.3

### 2. Materiale sul voynichizzatore (lavoro dell'altra chat: leggere, non modificare)
- [x] Scheda tecnica: `white_paper/revisione/scheda_voynichizzatore.md`.
- [x] e419 (chat del voynichizzatore): con contro senza messaggio sulla v21, differenze dentro l'errore, classificatore diretto AUC 0,506; nel paper (§9)
- [x] Precedenti (nel §2 del paper):
  - steganografia: Ziegler 2019, Meteor 2021, Cachin 1998, Hopper 2002;
  - Wayner 1992;
  - test a due campioni con classificatore (Lopez-Paz e Oquab 2017);
  - generatori: Timm e Schinner 2020, voynich-fingerprint 2026;
  - Naibbe.
- [ ] Alla fine: chiedere alla chat del voynichizzatore di rileggere la sezione sul generatore

### 3. Riscrittura (inglese, LaTeX, `white_paper/en/`)
- Titolo, abstract (200–250 parole) e introduzione con il generatore in primo piano.
- Struttura prevista:
  1. Introduzione;
  2. lavori precedenti;
  3. dati;
  4. metodi, con l'uso dell'IA generativa;
  5. le regole di scrittura misurate, con le priorità e la batteria dei 79 manoscritti;
  6. la pagella;
  7. il voynichizzatore;
  8. la valutazione;
  9. discussione, con gli scenari e anche "la riga come unità di contenuto";
  10. limiti;
  11. riproducibilità.
- Appendici: metodi in formule, registro degli esperimenti, verifiche interne, glossario, fonti.
- Figure: almeno 4 di misure + pagina generata accanto a pagina vera.
- Correzioni puntuali: tutte quelle di `VERIFICA_NOTE_REVISORE.md` (B, C, D).
- Sito e scheda Zenodo da allineare a fine lavoro (avvisare la chat del sito).

### 4. Dopo la revisione (9/10)
- [x] Controllo dei numeri del paper (due agenti): 13 numeri e 24 formulazioni corretti.
- [x] Abstract riscritto come chiesto da Davide: procedimento, esperimenti, pagella (noto e nuovo distinti), generatore,
  dimostrazione "può portare un messaggio" ripetuta dopo il Naibbe, senza prendersi meriti altrui.
- [x] Precedenti con messaggio (ricerca del 9/10, `precedenti_messaggio.md` nello scratch): Naibbe, Rugg 2004 (Scientific
  American), Feaster 2019 (Griffoynich), Matlach 2022, Rozanova e Temerev 2026, Parisel 2026, Gaskell e Bowern 2022.
