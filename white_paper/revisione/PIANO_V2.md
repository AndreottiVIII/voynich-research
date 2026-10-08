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
- [ ] e3c84: percentili per lingua, senza lingue artificiali (C1.1)
- [ ] nullo con la grammatica della parola per la catena di segni (A7)
- [ ] intervalli per bifoglio e fascicolo (A5)
- [ ] ripetizioni: rapporto osservato/atteso (A8)
- [ ] Voynich ridotto alla lunghezza dei testi di confronto (A8)
- [ ] raccordo a parità di posizione nella riga (Feaster 2022)
- [ ] confronti multipli (Holm) e potenza per scriba e scelta (A3, A9)
- [ ] registro completo degli esperimenti (A2, B12)
- [ ] controllo a campione sulle immagini (A11)
- [ ] (con download autorizzato) voynich-fingerprint e testo cifrato di Kinnison nelle nostre misure

### 2. Materiale sul voynichizzatore (lavoro dell'altra chat: leggere, non modificare)
- [ ] Scheda tecnica: modello del libro, canale (conteggi delle parole per pagina), decodificatore aritmetico,
  cifratura, impaginazione, capienza, giudici (e231, e266), pagella (18 proprietà), numeri della v21 su 24 chiavi, limiti
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
