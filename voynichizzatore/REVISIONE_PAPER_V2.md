# Revisione tecnica del white paper v2: sezioni sul generatore e sulla valutazione

Chat del voynichizzatore, 9/10/2026, sul commit `38c514a` (file in `white_paper/en`). Controllo fatto contro il codice
di `voynichizzatore/` e i file in `risultati/`; ogni voce ha la fonte. Non ho toccato i file del paper.

Legenda: **C** = da correggere; **P** = precisazione consigliata; **V** = verificato, nessuna modifica.

## 06_generatore.tex

| # | riga | frase attuale | frase giusta / proposta | fonte | tipo |
|---|---|---|---|---|---|
| 1 | 5–6 | "about 4,050–4,260 lines" | Non ho il conteggio delle righe sulle 24 chiavi (l'e409 non lo salva). Esempi misurati: 4.048, 4.144, 4.165, 4.179 righe. Se l'intervallo viene da una vostra conta, va bene; altrimenti "about 4,100–4,200 lines". | `esecuzioni/voynichizzatore/*.txt`; prova della figura | P |
| 2 | 67 | "books come out about 5% longer than the manuscript" | "about 4% more words than the manuscript (36,300 on average against 34,863; the number of lines is about the same, 4,130 in the manuscript)" | `e409b_…_v21f1_chiavi_*.json`, `valori.parole`: media 36.346, min 35.369, max 38.617; Voynich 34.863 parole, 4.130 righe | C |
| 3 | 69 | "About 86% … 2,246 types … the rest occur once" | V: 86,3%; 2.246 tipi con almeno 2 occorrenze; 4.776 tipi con una. | conteggio su `pezzi.voynich()` | V |
| 4 | 73 | "learned on the 4,776 once-occurring words" | V (coincide con i 4.776 byte compressi di Isidoro: è vero, non è un refuso). Precisare che il modello è per classe di posto: "learned, for each place class, on the …" | `parole_nuove.py` 120–131 (`tri[cl]`, `qua[cl]`) | P |
| 5 | 72–73 | "each glyph predicted from the three before it, backing off to two" | V | `parole_nuove.py` 166–172 (`tab4.get((z, a, b)) or tab[(a, b)]`) | V |
| 6 | 74–75 | "an invented word of six glyphs or more is, with probability 0.25, replaced if possible by a join of two known words of the page whose junction is probable" | V. Se si vuole il numero: "whose junction is probable (each of the two glyph triples across the junction has conditional probability at least 0.05 in the glyph model) and whose every glyph triple occurs in once-occurring words" | `parole_nuove.py` 207–229; `pezzi_parametri_v21.json`: `unioni 0.25`, `giuntura 0.05`, `unioni_valide true` | P |
| 7 | 75–76 | "An invented word is never a Voynich word" | V (controllo diretto: 0 parole inventate presenti nel vocabolario del Voynich in un libro v20/v21) | `parole_nuove.py` 175, 213; conteggio su `repo_isidoro_v20.txt` | V |
| 8 | 78–82 | lessico dalle altre pagine della stessa sezione e lingua; pagina tipo scelta dalla chiave; peso c^γ · exp(κ Σ n_g δ_g); γ = 0,976, κ = 0,644 | V. Precisazione possibile: la pagina tipo è un'altra pagina dello stesso tipo **con almeno 40 parole note**. | `sacco.py` 30–34, 89–96, 100; `pezzi_parametri_v21.json` (kappa 0,6435, gamma 0,9758) | V/P |
| 9 | 86–90 | catena di binomiali, "stop at j copies" con P(X=j)/P(X≥j) a 16 bit, codificatore a 32 bit; pesi ordinati dal più pesante | V | `canale_sacco.py` 77–98, 104–123; `v1.py` 24 (`TOT = 1 << 16`, `PREC = 32`) | V |
| 10 | 92–93 | "the Isidore text fills about 130 of the 207 pages" | "fills 124–131 of the 207 pages (128 on average)" | `e409b_…_v21f1_chiavi_*.json`, `pagine_usate` | C |
| 11 | 95 | "81,100–85,900 bits (mean 83,400 over 24 keys), about 2.7 bits per known word" | V (81.116–85.905, media 83.440; 83.440 / (36.346 × 0,863) = 2,67) | stessi file, `capacita_bit` | V |
| 12 | 96–98 | cinque scelte, "about 0.8 bits per choice and 46,000 bits per book" | V | `QUADERNO.md` riga 6713 (v1); `e145_abitudini.SCELTE` = (0, 1, 2, 4, 6) dell'e135 | V |
| 13 | 103–105 | "a logistic model on the word's first and last glyphs, length, prefix and ending" | "a logistic model on the word's first glyph and first two, last glyph and last two, length, prefix, ending, and whether it contains p or f" | `disposizione.py` 38–42 (`tratti`) | P |
| 14 | 103–109 | "thirteen terms"; 60 scambi per parola; temperatura 1 | V (posto, bordi, unione, coppia, identica, confine, verticale, prima_lettera, distanza2, scelte, scelte_sopra, meta, larghezza; `fin_fin` è a 0) | `pezzi_parametri_v21.json`; `disposizione.py` 28 (`PASSATE = 60`), accettazione exp(d) | V |
| 15 | 119 | "about 85% of the running words of a book are Voynich words" | "about 86%" (86,3% nel libro v20/v21 di Isidoro, 85,7% in un libro v17; coincide con la quota di parole note, perché le inventate non sono mai parole del Voynich) | conteggio su `repo_isidoro_v20.txt` e `_v17.txt` | P |
| 16 | 125–126 | "From version 14 on, the numbers we cite come from keys never used for tuning; versions 17 and 20 were released on the development keys and confirmed on the other 12 later the same day, version 21 before release" | I pesi non sono mai stati regolati sulle chiavi di misura (si regolano sul pannello, con semi e chiavi di regolazione a parte). Ma le chiavi 1–12 sono servite a **scegliere fra versioni**; i numeri citati sono su tutte e 24. Proposta: "The weights were never tuned on the measurement keys. Keys 1–12 were used to choose between versions; from version 14 on each version was also measured on keys 13–24, never used for that choice, and the numbers we cite are on all 24 keys. Versions 17 and 20 were released on keys 1–12 and confirmed on 13–24 later the same day, version 21 before release." Così coincide con 07, righe 5–7. | `QUADERNO.md`, voci "vz: conferma14", "vz: conferma della v20", "vz: e418" | C |
| 17 | 137–138 | v0 0.958 / 0.980; v1 0.889 / 0.957 | Non li ho trovati in `risultati/e293_banco*.md` né nel QUADERNO con questi valori: indicare il file di origine (le righe v2 e v3 del banco e293 danno 0,845 / 0,948 e 0,817 / 0,934 su 3 semi). Se vengono da un altro file, aggiungere "(3 seeds)" come per v8. | `risultati/e293_banco.md` righe 18–28 | C |
| 18 | 139–143 | tabella delle versioni: dopo v15–v17 viene v21 "correction of an initialisation defect" | Manca il passo v18–v20, che cambia il metodo: "v20 & line widths in characters: the arrangement is pushed towards the width expected from the manuscript for each line's number of words; the alternation term re-tuned & 0.560 / 0.607 (24 keys)". La riga v21 va bene, ma è "v20 + correzione", non "v17 + correzione". | `QUADERNO.md`, voci "vz: e416 ed e416b", "vz: e417", "vz: conferma della v20"; `risultati/e409b_…_v20_chiavi_*.json` | C |
| 19 | 141 | v14 0.575 / 0.600 (24 keys) | V | `QUADERNO.md`, "vz: conferma14" (24 chiavi: 0,575 / 0,600) | V |
| 20 | 142 | v15–v17 0.559 / 0.597 (24 keys) | V | `e409b_…_v17_chiavi_1_12` e `_13_24` | V |
| 21 | 143 | v21 0.554 / 0.601 (24 keys) | V | `e409b_…_v21f1_chiavi_*` | V |
| 22 | 151–155 | figura: "The message uses 1,144 of the book's 83,480 bits" | Con la frase esattamente come stampata nella didascalia (senza a capo finale) e quella chiave ottengo **1.128 bit** di messaggio e capacità **83.690**, 4.179 righe. La differenza (16 bit = 2 byte compressi) viene quasi certamente da un a capo finale o da una virgoletta diversa nel file usato per la figura; la capacità cambia perché dipende dai bit. Allineare didascalia e file (o scrivere "about 1,100 of about 83,500"). | prova diretta con `canale_sacco.codifica(…, 'v21')` | C |
| 23 | 54–59 | cornice, flusso, scrypt, generatori per uso e pagina | V (lunghezza 4 byte, etichetta 8 byte HMAC-SHA256 troncata; SHAKE-256; scrypt n = 2^15, r = 8, p = 1; `generatore(chiave, pagina, uso)`; la disposizione ha un generatore unico per libro) | `canale_sacco.py` 29–72, 262 | V |
| 24 | 60 | 11,207 bytes → 4,776 → 38,304 bits | V ((4 + 8 + 4.776) × 8 = 38.304) | `e409b_…_v21f1`: `byte_testo`, `byte_compressi`, `bit_messaggio` | V |
| 25 | 64–67 | impaginazione statistica (righe per pagina, larghezza, paragrafi, rapporto per ruolo) | V | `canale_sacco.py`, `statistiche_gabbia` e `gabbia_statistica` | V |
| 26 | 115–118 | sale fisso; flusso che dipende solo dalla chiave | V (`SALE` costante; `shake_256(k + b'flusso')`) | `canale_sacco.py` 29, 50 | V |

## 07_valutazione.tex

| # | riga | frase attuale | frase giusta / proposta | fonte | tipo |
|---|---|---|---|---|---|
| 27 | 20–27 | tabella: 0.554 ± 0.006 / 0.554 ± 0.005 / 0.554 ± 0.004 (0.517–0.580); 0.596 ± 0.008 / 0.606 ± 0.006 / 0.601 ± 0.005 (0.551–0.632); 6, 8, 14; 16.0, 15.9, 16.0; 5.5, 5.2, 5.4; 12, 12, 24; capacità | V tutto, con una sola sfumatura: estese sulle chiavi 13–24 = 5,25 (arrotondabile a 5.3 come a 5.2); su 24 chiavi 5,38 → 5.4 | `e409b_…_v21f1_chiavi_1_12.json`, `_13_24.json` | V |
| 28 | 36–53 | valori della pagella (Voynich e generato) | V per le righe 1–6, 8–18: h2 2,236/2,284; spazio 0,664/0,639; uniche 0,678/0,738; tipi 0,210/0,205; identiche 1,009/0,943; omogeneità 0,0385/0,0414 (1 chiave); giuntura 0,188/0,180; unioni 1,96/2,13; curva piatta 0,057/−0,024; ricambio 0,106/0,095; profilo 1,02/0,66; autocorrelazione 0,150/0,142; Zipf −1,041/−1,005; forma 0/0,040; verticale 1,028/1,035; formule 5,20/4,58; bordi 23,6/54,5. **Riga 7 (gradiente 0,62 generato): non l'ho potuta verificare**, il valore non è fra i `valori` salvati dall'e409: indicare la fonte. | medie di `valori` e `valori_Voynich` nei due json | V/P |
| 29 | 69 | "lines shuffled within each page (0.595)" e "words shuffled within each line (0.99)" | V | `risultati/e400_scala_controlli.md` righe 10–11 (O1 0,595; O2 0,990) | V |
| 30 | 70–72 | "register of the first lines of paragraphs (AUC 0.61 … over the 24 keys; on the fresh keys the word statistics are as informative, 0.609 against 0.605)" | V (G8 0,610 su 24; chiavi 13–24: G3 0,609, G8 0,605). Su tutte e 24 G3 vale 0,605, quasi quanto G8: si può dire "the register of the first lines (G8, 0.61) and the word statistics (G3, 0.61) are the groups the second judge uses best". | medie di `gruppi_e266` | P |
| 31 | 74–76 | estese mancate: scelte di riga 23/24, prime righe 18/24, dispersione 20/24 | V | `estese_passate` nei due json | V |
| 32 | 76–77 | "11.6% … against 6.0%" | V (chiavi 1–12, e418 F1 = v21) | `risultati/e418_conti_scelte.md` | V |
| 33 | 77 | "About 0.4–0.5% of the word triples of a book also occur in the manuscript" | "About 0.3–0.5% (0.43% on average)" | `trigrammi_dal_Voynich`: min 0,0030, max 0,0051, media 0,0043 | C |
| 34 | 79–91 | e419: −0,009 ± 0,008; −0,007 ± 0,010; −0,04 ± 0,04; 48 su 48 al cancello; 228 caratteristiche; 9.420 pagine; 0,506; nessun gruppo oltre 0,51; negativo 0,511; capacità non uguale | V tutto (228 caratteristiche contate direttamente; gruppo massimo G2 0,509) | `risultati/e419_con_senza_messaggio.md`; conteggio di `e266.tabella` | V |
| 35 | 5–7 | protocollo: chiavi 1–12 usate per scegliere, 13–24 solo per conferma | V; va allineato il §8 (voce 16) | — | V |
| 36 | 95–96 | "It models copying from the line above by the index of the word in the line" | V (`sopra[t]` = stesso indice nella riga sopra) | `disposizione.py` 150–165 | V |

## Abstract (main.tex) e §1.3 (01_introduzione.tex)

| # | riga | frase attuale | frase giusta / proposta | fonte | tipo |
|---|---|---|---|---|---|
| 37 | main.tex 88–93 | "bits decide only how many times each recurring Voynich word appears on each page … AUC 0.55 and 0.60 … 16 of the 17" | V | §9 | V |
| 38 | main.tex 92 | "(the second gives 0.60 also to the real manuscript with its lines shuffled)" | V (0,595) | `e400` O1 | V |
| 39 | main.tex 98; 01 riga 52 | "a classifier trained to tell them apart scores AUC 0.51" | V (0,506 → 0,51) | `e419` | V |
| 40 | 01 righe 33–39 | punto 1: "turns any text into a 207-page Voynich-like book … recovers it exactly with the key … bits drive an arithmetic decoder that samples how many times each recurring Voynich word occurs on each page" | V. Una cautela: "any text" vale fino a circa 80.000 bit dopo compressione (circa 20.000 caratteri); se si vuole, "any text up to about 20,000 characters". | §8 capacità | P |
| 41 | 01 righe 48–53 | punto 3 | V (coerente con e419 e §9) | — | V |

## Due cose di metodo da dire nel paper, se non ci sono già altrove

- La soglia del criterio (a) dell'e417 (righe larghe) è stata fissata dopo aver visto la v19 (dichiarato in
  `preregistrazioni/e417.md`); e le prime 12 chiavi della v20 erano ottimiste rispetto alle 13–24 (0,554 / 0,599 contro
  0,567 / 0,615). Se il paper racconta la storia delle versioni, questi due fatti ci stanno bene nell'appendice dei
  controlli.
- Il difetto corretto nella v21 (voce 18 della tabella) è stato trovato da un'altra chat leggendo il codice pubblico, non
  da una misura: le misure di v12–v20 erano vere per quei programmi, era sbagliata la descrizione del termine.
