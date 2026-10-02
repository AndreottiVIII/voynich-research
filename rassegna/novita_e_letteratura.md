# Che cosa è nuovo e che cosa era già noto — rassegna al 2/10/2026

Rassegna fatta con ricerche web mirate su ciascun punto (non sistematica: voynich.nu non è
raggiungibile da questo PC, e molti lavori stanno solo su voynich.ninja o nei blog). Da completare
prima del white paper, in particolare su voynich.ninja e negli atti di Malta 2022.

## Già noto, che qui è stato replicato o quantificato

| risultato | esperimenti | già in |
|---|---|---|
| La riga è un'"unità funzionale": segni diversi a inizio e fine riga, gallow nelle prime righe dei paragrafi, -m e -g a fine riga | e71, e73 | Currier 1976; D'Imperio 1978; Vogt 2012; Feaster 2022 |
| A inizio riga sono attratti y, d, s | e72, e73, e139 | Tavie, Voynich Day (voynich.ninja, thread 4343); Timm 2014 |
| Righe consecutive evitano lo stesso segno iniziale (o-o, q-q, ch-ch), con asimmetrie (o → q) | e83, e84, e105 | Tavie (thread 4343); Timm 2014 (sorgente della prima parola nelle righe sopra) |
| Gli stessi andamenti sono condivisi dalle mani | e130 | Tavie (tre scribi) |
| La seconda parola di riga preferisce ch/sh (+70%) | e94 | segnalato su voynich.nu / letteratura sulla posizione |
| Dipendenze fra fine e inizio di parole adiacenti dentro la riga | e12, e91 | Smith e Ponzi 2019 (Cryptologia) |
| Parole simili vicine; copia locale | e110 | Timm 2014; Timm e Schinner 2020 |
| Testi inventati a mano imitano il Voynich nelle parole | e128 | Gaskell e Bowern 2022 |
| Cifrario a mano che imita le statistiche delle parole | e134 | Greshko 2025 (Naibbe) |
| I bifogli sono stati rimescolati; l'ordine attuale non è quello originale | e148, e150 | codicologia: acqua fra f78v e f81r, farmacia divisa fra fascicoli; Davis (macchie d'acqua, "singulions") |
| Vocabolario diverso per sezione e deriva | e142, e144 | Montemurro e Zanette 2013; Currier A/B |

## Probabilmente nuovo (non trovato in letteratura con le ricerche fatte)

1. **Chiusura della riga misurata come assenza di legame all'a capo.** Il legame fra fine e inizio di
   parole adiacenti, forte dentro la riga, sparisce attraverso l'a capo (R ≈ 0; e74), e le fini di
   righe vicine sono indipendenti, senza rima (e136, contro Dante come controllo). Smith e Ponzi
   studiano le giunture dentro la riga, non attraverso l'a capo.
2. **L'evitamento dell'inizio è una catena del primo ordine** (guarda solo la riga sopra, e105),
   senza ciclo né numerazione (e137, e137b). Il fenomeno era noto; la caratterizzazione no.
3. **Cinque scelte di grafia decise riga per riga, indipendenti fra loro, con memoria di 3–5 righe e
   ripartenza a ogni pagina** (e123b, e135, e146). Feaster 2022 ipotizza "opzioni diverse in zone
   diverse della pagina" senza misurarlo.
4. **Le righe sono composte sul posto**: dopo una riga accorciata da un disegno le regole d'inizio
   valgono come altrove (e141). Contro l'idea di una bella copia da un modello con altri a capo.
5. **Le regole di riga non le producono** i testi inventati da persone (dati di Gaskell e Bowern),
   Timm e Schinner, Naibbe, né i generatori U2/U3 (e128, e134). Un generatore che compone le righe in
   ordine (tema, giunture, abitudini, regola d'inizio) le produce tutte insieme (e152).
6. **Nessuna grammatica nemmeno nella composizione della riga**, ignorando l'ordine (e126); con
   e114 ed e115.
7. **Nessuna struttura di elenco o di voce:** tipi di riga (e138), cornice inizio-fine (e143),
   ordine alfabetico nelle ricette (e151, contro l'*Alphita*), posizioni fisse nelle ruote
   zodiacali (e144), somiglianza fra i segni zodiacali doppi (e142).
8. **Il testo non si adatta allo spazio** (e147, sulle immagini): niente parole più corte o segni più
   stretti dove il disegno toglie spazio, e il margine destro è meno regolare di un riempimento
   meccanico.
9. **I fogli coniugati si somigliano molto più dei vicini a parità di mano e lingua** (e148), e un
   ordine dei bifogli ricostruito dal vocabolario, su dati non usati e senza le scelte di grafia, è
   confermato dalle abitudini di grafia (e150b, e154b). La codicologia sapeva dei rimescolamenti; una
   ricostruzione statistica validata così non l'ho trovata.
10. **Verifica sistematica con chiavi casuali delle letture di Bax e Vatne** (e133): la chiave di Bax
    non batte il caso fuori campione; le sue parole ricorrenti stanno dappertutto; i "nomi" di Vatne
    ricorrono come qualsiasi prima parola. Le critiche esistevano; il test quantitativo no.
11. **Le etichette sono un lessico a sé marcato da o-** (59% contro 21% nel testo; zodiaco 76%), non
    parole del testo con un prefisso (e149). Che le etichette comincino spesso con o- era noto
    informalmente.
12. **Limite di decifrabilità:** un codice per sillabe con grafia variabile non si risolve per sola
    statistica nemmeno col modello di lingua "barato" (e112b).

## Da verificare in modo più completo

- voynich.ninja (in particolare i lavori di Tavie, Koen Gheuens, Emma May Smith, Marco Ponzi) per i
  punti 1, 3, 9.
- Atti del convegno di Malta 2022 (CEUR 3313) e di Voynich Day.
- Davis, *The Materiality of the Voynich Manuscript* (2025), per il punto 9.

## Fonti consultate

- Currier, *Papers on the Voynich Manuscript* — https://www.voynich.nu/extra/curr_main.html
- Vogt 2012 — https://voynichthoughts.wordpress.com/wp-content/uploads/2012/11/the_voynich_line.pdf
- Feaster 2022 — https://ceur-ws.org/Vol-3313/paper12.pdf
- Tavie, Voynich Day, Line Patterns — https://www.voynich.ninja/thread-4343.html
- Smith e Ponzi 2019 — https://agnosticvoynich.wordpress.com/2019/06/04/new-article-glyph-combinations-across-word-breaks-in-the-voynich-manuscript/
- Timm 2014 — https://arxiv.org/pdf/1407.6639
- Pelling, bifogli rimescolati — https://ciphermysteries.com/2013/05/30/evidence-of-bifolio-reordering-in-the-voynich-manuscript
- Pelling su Davis 2025 — https://ciphermysteries.com/2025/10/11/lisa-fagin-davis-the-materiality-of-the-voynich-manuscript
- Montemurro e Zanette 2013 — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0066344
