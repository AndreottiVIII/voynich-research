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
- [ ] Controllo prima di aprire:
  - storia git (dati protetti mai committati, chiavi o password);
  - email negli autori dei commit;
  - note del revisore;
  - licenze dei file in `dati/`.
- [ ] Aprire il repo, aggiornare `CLAUDE.md` (regola "il repo resta privato") e il paper (§ Riproducibilità).

### 1. Rianalisi (esperimenti nuovi, ognuno con preregistrazione, codice, esecuzione, quaderno)
- [x] e3c84: percentili per lingua, senza lingue artificiali (C1.1): reggono quasi tutti; giuntura 2 lingue su 24, calo 2 su 20
- [x] e3c85 nullo con la grammatica della parola (A7): spazio prevedibile, tagli e riempimento spiegati dalla forma delle parole; giuntura e rispecchiamento no
- [x] e3c86 intervalli per bifoglio e fascicolo (A5): tutto regge per bifoglio; per fascicolo cede solo la deriva di k/t
- [x] e3c88 ripetizioni osservato/atteso (A8): O/E nella riga 1,04 (non evitata, non in eccesso); lingue ≤ 0,92, scribi ≤ 0,79
- [x] e3c89 riga chiusa e margine a 10.000 parole (A8): reggono
- [x] e3c87 raccordo a parità di posizione (Feaster 2022): non viene dalla posizione
- [x] e3c90 potenza per scriba e scelta (A9): deriva assente con potenza 28/29; finestra 14/29, 13 senza potenza, 2 presenti (e3c91: Holm A 10 incerto)
- [ ] confronti multipli (Holm) per famiglie di prove (A3)
- [ ] registro completo degli esperimenti (A2, B12) — agente in corso, da rivedere
- [ ] controllo a campione sulle immagini (A11) — servono ritagli IIIF (download: chiedere a Davide); per gli spazi incerti citare Rozanova e Temerev
- [ ] (con download autorizzato) voynich-fingerprint (271 KB, MIT) nelle nostre misure; Kinnison = Naibbe, già misurato: non serve

### 2. Materiale sul voynichizzatore (lavoro dell'altra chat: leggere, non modificare)
- [x] Scheda tecnica (scratchpad della sessione: `scheda_voynichizzatore.md`). Buco: con messaggio contro senza messaggio misurato solo sulla v9 → chiesto alla chat del voynichizzatore di rifarlo sulla v21 (8/10)
- [ ] Precedenti:
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
