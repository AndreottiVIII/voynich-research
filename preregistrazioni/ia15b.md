# Preregistrazione ia15b — IA15b: da dove viene l'eco della pagina (seconda versione)

Scritta il 21/11/2026, prima di eseguire sul Voynich, sui libri v21, su Timm e Schinner e su ogni generatore costruito sul Voynich.
Codice: `esperimenti/ia15b_da_dove_eco.py` (l'unico file `ia15b_*.py`; `esegui.py ia15` continua a trovare solo `ia15_da_dove_eco.py`, perché il modello
di ricerca è `ia15_*.py` e `ia15b_...` non lo soddisfa) e il modulo di supporto nuovo `esperimenti/eco_modelli_b.py`. Importa da ia15 (non modificato)
`ia15_da_dove_eco.py`, `eco_testi.py`, `eco_modelli.py` e, tramite lui, da ia01, ia09 e `sintassi_*`. Nessuna rete neurale e nessun modello di probabilità: solo conte.
Filone "Voynich e IA". Segue ia15 (`preregistrazioni/ia15.md`, `risultati/ia15_da_dove_eco.md`).

## Perché (e che cosa è già stato visto)

**Questo è un nuovo esperimento, preregistrato DOPO aver visto i numeri di ia15.** In ia15 (20/11/2026) la corsa è uscita quasi tutta "non leggibile": i
controlli "tecnica", "argomento di paragrafo", "tecnica che riparte" e il negativo della direzione non hanno retto con i generatori costruiti sul lessico del
Voynich. Le cause viste: (1) con i livelli scelti allora l'eco dei generatori era molto più piccola di quella osservata nel Voynich (eco vicina di `tecM1` 0,0022
contro 0,0084 del latino nella stessa disposizione e 0,0116 del Voynich), (2) di conseguenza la misura del paragrafo Q era instabile (intervalli enormi), (3) il controllo
"tecnica" chiedeva anche "il paragrafo non conta" e quindi è caduto con Q, rendendo non leggibili anche profilo e varianti, (4) il controllo negativo della direzione chiedeva
"dentro la parola", che con i glifi del Voynich è solo una delle due risposte giuste ("nessun posto prevale" è l'altra).

**Numeri del Voynich già visti in ia15 (da dichiarare, perché orientano la domanda):** eco vicina 0,0116 e lontana 0,0057 (H = 0,49); quota di varianti nell'eco vicina 0,74, ma
0,75 nel v21 e 0,75 nel Voynich con le parole mescolate dentro la pagina (`vere~p`): con questo lessico la quota grezza di varianti non distingue una tecnica;
Q a 2–3 righe 0,88 (0,69–1,11); pagine consecutive "no" (0,89), cioè nessuna continuità fra pagine vicine (il latino nella stessa disposizione dà "sì").
Questi numeri **non** sono stati usati per scegliere nessuna soglia di lettura. **Non sono stati visti** i numeri del Voynich per le misure nuove (parte locale dell'eco, quota
di varianti nella parte locale).

**Come si evita di scegliere le soglie guardando il Voynich.**
1. Le soglie di lettura di ia15 (H, quota di varianti, Q, pagine vicine, direzione) restano **identiche**.
2. Le soglie e i parametri nuovi (`LOC_MIN` 0,15; `POTENZA_MIN` 0,70; `TARA_TOL` 0,08; la condizione sul denominatore di Q; la regola del controllo negativo della
   direzione) sono fissati qui, **dai soli controlli su testi non Voynich** (latino e inglese scritti nella disposizione del Voynich: vedi "Prova del codice") e dalla logica
   delle misure, e non si cambiano dopo la corsa. Il valore 0,15 sta nel vuoto fra i controlli senza parte locale (parte locale / eco vicina fra −0,07 e +0,12 nei testi con le parole mescolate dentro la pagina e nei generatori di argomento di pagina e di famiglie) e le lingue o i
   generatori con parte locale vera (0,35–0,99).
3. L'**unica** cosa che viene dal Voynich è il bersaglio della taratura: l'**eco vicina** (una sola quantità) del testo `vere`, calcolata dentro la corsa con lo stesso programma
   (già vista in ia15: 0,0116). I generatori di controllo sono costruiti sul lessico del Voynich e la loro forza è scelta, da un programma, perché la loro eco vicina sia uguale
   (V), la metà (M) o un quarto (D) di quel bersaglio. Mai si tarano profilo, quota di varianti, Q, direzione o pagine vicine.
4. I controlli decidono quali letture valgono; la lettura del Voynich si legge **solo dopo** e solo se i suoi controlli passano. Un controllo che fallisce si rifà una volta
   (`RIPRENDI=1`, con la taratura rifatta); poi si dichiara la lacuna.

## Cambi rispetto a ia15 (dichiarati)

1. **Controlli separati per lettura.** Ogni lettura (profilo, varianti, paragrafo, modifiche, pagine vicine, sintesi, sintesi senza paragrafo) vale se passano **i suoi** controlli
   (tabella sotto), più il negativo "rimescolato fra le pagine" che serve a tutte. Prima un controllo fallito rendeva non leggibili tutte le letture.
2. **Generatori di controllo tarati sull'eco.** La forza di ogni generatore (quota di parole del tema `λ`, probabilità di copiare `p`) si cerca con un programma (interpolazione
   in scala logaritmica, al massimo 8 valutazioni per livello, tolleranza dell'8%) perché la sua eco vicina (0–3 righe, parole alla riga 4 o più, pesi comuni, riferimento della
   stessa sezione, gli stessi semi di ia15) sia **uguale** a quella del Voynich (livello V, i controlli veri), alla **metà** (M) e a **un quarto** (D) (M e D descrittivi: dicono
   fin dove la misura vede). Una famiglia con eco sotto il 70% del bersaglio non ha forza: i suoi controlli non contano.
3. **Varianti al netto del lessico.** La quota di varianti si legge sulla **parte locale** dell'eco: eco vicina meno eco lontana, separatamente per le parole uguali e per le varianti
   (stessi pesi comuni per pagina). La parte che non cala con la distanza (il lessico, il tema della pagina, le famiglie di parole) si toglie. `QL = varianti locali / (varianti locali + uguali locali)`.
   Se la parte locale non è almeno il 15% dell'eco vicina (e con limite basso > 0) la lettura è **"nessuna parte locale"** (l'eco non cala con la distanza: la quota di varianti non si legge).
   Resta la quota grezza di ia15, **descrittiva**, con il confronto contro lo stesso testo con le parole mescolate dentro la pagina (tiene lessico e tema, rompe la distanza) e contro il v21.
4. **Nuovo controllo "argomento di famiglie di parole"** (`argF`): ogni pagina ha un tema di 30 parole; quando esce una parola del tema, con probabilità 0,6 esce invece una parola a una modifica
   da lei, scelta a caso fra quelle del testo. Nessuna copia di parole vicine, nessun legame con la distanza: è il modo in cui una lingua flessiva (o un lessico a famiglie) ripete varianti senza
   copiare. Deve dare profilo piatto e varianti **non alte**: dice se la misura delle varianti si fa ingannare dal lessico.
5. **Paragrafo.** Q (eco fra paragrafi / eco dentro il paragrafo, a 2–3 righe, soglie di ia15 invariate) si legge solo se l'eco "dentro" ha limite basso > 0; altrimenti "non leggibile" (un rapporto con un
   denominatore che può essere zero non è una misura).
6. **Direzione.** Il controllo negativo (`tecM1`) chiede "né inizio né fine" (modifiche a caso nella parola), non "dentro la parola".
7. **Sintesi senza paragrafo.** Se solo i controlli del paragrafo non passano, la sintesi si legge ignorando il paragrafo (regola identica, con il paragrafo "zona grigia"), dichiarandolo.
8. **Nuovi generatori e nomi.** `argP1`–`3`, `argR1`–`3`, `argS1`, `argF1`–`2`, `tecM1`–`3`, `tecP1` (copia solo dal paragrafo in corso), `tecCoda1`, `tecTesta1` al livello V;
   `argPm1`, `argRm1`, `argFm1`, `tecMm1`, `tecPm1` (M) e `argPd1`, `tecMd1`, `tecPd1` (D). I nomi coincidono con quelli di ia15 per le famiglie, ma i livelli sono altri.
   (`argS` ora è un solo generatore al livello V; i livelli F/M/D fissi di ia15 non esistono più.) Le misure di base (conte, pagine di riferimento, bande, pesi comuni, bootstrap,
   confini spostati) sono **le stesse** di ia15.

## Misure (invariate da ia15, salvo quanto sopra)

Eco, bande D0–D8, riferimenti, Q con i confini spostati, profilo H, quota di varianti, direzione, pagine vicine e gruppi (sezione, tipo di pagina, lingua, mano, terzili dell'area del
disegno nell'erbario): vedi `preregistrazioni/ia15.md`. Nuove, per ogni testo e gruppo: `loc` = eco vicina meno eco lontana (pesi comuni), `loc_x` e `loc_v` (uguali e varianti),
`loc_rel = loc / eco vicina` (= 1 − H), `QL = loc_v / loc`. Tutte con bootstrap sulle pagine (1.000, gli stessi per testi con le stesse pagine).

## Soglie (fissate qui)

Come ia15 (tabella nel file ia15.md) per eco "misurabile" (eco vicina ≥ 0,001 con limite basso > 0), profilo (ripido, piatto), pagine vicine, direzione e paragrafo (con la sola aggiunta del
denominatore). **Varianti** (nuove, sulla parte locale):

| lettura | etichetta | condizione |
|---|---|---|
| varianti | **nessuna parte locale** | parte locale con limite basso ≤ 0, o parte locale / eco vicina < 0,15 |
| | **alte** | QL ≥ 0,45 e limite basso > 0,30 |
| | **basse** | QL ≤ 0,25 e limite alto < 0,40 |
| | **medie** | il resto |
| | **non leggibile** | eco non misurabile |

**Sintesi** (regola di ia15 invariata, con queste varianti): (1) profilo o varianti non leggibili: "non leggibile"; (2) il paragrafo conta: varianti alte e profilo ripido "tecnica che riparte a ogni
paragrafo", varianti alte e profilo non ripido "mista", altrimenti "argomento di paragrafo"; (3) profilo ripido e varianti alte: "tecnica"; (4) varianti non alte (anche "nessuna parte locale") e profilo non
ripido: "argomento di pagina" se il profilo è piatto e le pagine vicine non sono "sì", altrimenti "argomento che scorre"; (5) un segno di tecnica (profilo ripido o varianti alte) insieme a uno di
argomento (profilo piatto o intermedio, o pagine vicine "sì"): "mista"; (6) altrimenti "zona grigia".

## Controlli (ognuno vale per le sue letture; con generatori vale solo se ogni suo testo ha ≥ 70% dell'eco vicina bersaglio)

| controllo | testi | deve venire | serve a |
|---|---|---|---|
| negativo fra pagine | `vere~t1`–`5`, `tecM1~t`, `argP1~t`, `argF1~t` | eco "debole" | tutte le letture |
| negativo nella pagina (parole mescolate dentro la pagina; senza condizione di potenza) | `vere~p`, `tecM1~p`, `argP1~p`, `argF1~p` | profilo piatto; varianti non alte; il paragrafo non "conta" | profilo; varianti; paragrafo |
| positivo tecnica | `tecM1`–`3` | profilo ripido; varianti alte; paragrafo non "conta"; sintesi "tecnica"; sintesi senza paragrafo "tecnica" | profilo; varianti; paragrafo; sintesi (e senza paragrafo) |
| positivo argomento di pagina | `argP1`–`3` | profilo piatto; varianti basse o nessuna parte locale; paragrafo "non conta"; sintesi "argomento di pagina" (anche senza paragrafo) | idem |
| positivo famiglie di parole | `argF1`–`2` | profilo piatto; varianti non alte; paragrafo "non conta"; sintesi "argomento di pagina" | idem |
| positivo argomento di paragrafo | `argR1`–`3` | paragrafo "conta"; varianti basse; sintesi "argomento di paragrafo" | paragrafo; varianti; sintesi |
| positivo tecnica che riparte | `tecP1` | paragrafo "conta"; varianti alte; sintesi "tecnica che riparte a ogni paragrafo" | paragrafo; varianti; sintesi |
| positivo argomento che scorre | `argS1` | pagine vicine "sì"; sintesi (e senza paragrafo) "argomento che scorre" | pagine vicine; sintesi |
| negativo pagine vicine | `argP1`–`3`, `argF1`–`2`, `tecM1`–`3` | pagine vicine non "sì" | pagine vicine |
| positivo direzione | `tecCoda1`, `tecTesta1` | "fine", "inizio" | modifiche |
| negativo direzione | `tecM1` | né "inizio" né "fine" | modifiche |
| limite (descrittivo) | `argPm1`, `argRm1`, `argFm1`, `tecMm1`, `tecPm1` (metà eco); `argPd1`, `tecMd1`, `tecPd1` (un quarto) | nessuna condizione: si riportano tutte le letture | tutte |

**Validità.** Una lettura vale se tutti i controlli che la servono sono superati (con potenza sufficiente). La sintesi vale se valgono anche profilo, varianti, paragrafo e pagine vicine; la sintesi senza
paragrafo, se valgono profilo, varianti e pagine vicine. Una lettura che non vale è "non leggibile (i controlli di questa lettura non sono superati)". Se la sintesi con paragrafo non vale ma quella senza
paragrafo sì, la sintesi riportata è quella senza paragrafo, scritta così.

## Letture preregistrate

Tutte per il testo `vere`, con gli intervalli al 95% sulle pagine, ciascuna solo se vale. 1. **Paragrafo** (conta / non conta / zona grigia / non leggibile). 2. **Sezioni e tipi di pagina**
(eco vicina, lontana, H, quota di varianti grezza e sulla parte locale, eterogeneità "varia / uniforme / come i riferimenti / più che i riferimenti", come in ia15; i generatori al livello V e le lingue
nella disposizione del Voynich danno il riferimento). 3. **Profilo** (ripido / intermedio / piatto) **e varianti sulla parte locale** (alte / medie / basse / nessuna parte locale), con le tabelle per
banda. 4. **Direzione** (inizio, fine, dentro la parola, nessun posto prevale). 5. **Pagine vicine** (sì / solo a livello di quaderno / no / zona grigia; in ia15 era già "no": si rifà con gli stessi
conti, e i controlli sono quelli di ia15 più i nuovi generatori). 6. **Sintesi** (argomento di pagina, di paragrafo, che scorre, tecnica, tecnica che riparte, mista, zona grigia, non leggibile).
Descrittive, senza soglia: v21 contro vere (anche la parte locale), Timm e Schinner (ci si aspetta "tecnica" dove i controlli valgono), latino, inglese, italiano e le lingue nella disposizione del Voynich,
lingua A e B, mano, eco con riferimento di un'altra sezione, la quota di varianti grezza contro il rimescolato nella pagina, il ponte con ia09.

## Lettura attesa (non vincolante)

Dai numeri già visti: profilo **intermedio** (H = 0,49), pagine vicine **no**, paragrafo **non conta** o zona grigia (Q 0,88 con intervallo largo). Per le varianti non c'è un'attesa: se la quota
di varianti nell'eco vicina fosse tutta "di pagina" (come nel rimescolato) la lettura sarebbe "nessuna parte locale" o varianti basse, e l'eco sarebbe un argomento con famiglie di parole; se fosse locale e
alta, una copia-e-ritocco o un meccanismo locale. La sintesi possibile va da "argomento che scorre" (ma le pagine vicine non si assomigliano, quindi "argomento di pagina" è più probabile) a "mista". Non è una
decifrazione e non dice che il testo è una lingua o non lo è.

## Limiti di principio (come ia15, più questi)

- **Eco non è causa.** L'eco dice dove sono le ripetizioni, non perché ci sono; "argomento" e "tecnica" sono due modelli puri.
- **La taratura mette l'eco al livello del Voynich, non la sua struttura.** Un generatore con la stessa eco vicina può avere altre cose diverse (famiglie, ordine, tipi di parole). I controlli dicono se la
  misura **vede** una tecnica o un argomento con queste forme; una tecnica vera (Timm e Schinner, il Voynich) può avere altro profilo.
- **La parte locale** dipende dal confronto vicino/lontano (0–3 contro 4 o più righe): se l'eco cala a distanze diverse la parte locale cambia; è la stessa partizione di H.
- **Generatori sul lessico del Voynich non provati prima.** Le prove sono su testi non Voynich (vedi sotto); i generatori costruiti sul lessico del Voynich (frequenze, parole a una modifica) possono
  comportarsi diversamente: se un controllo fallisce si riporta e la lettura resta non leggibile.
- **Paragrafo.** Q è debole per una tecnica locale (poca eco a 2–3 righe): anche con la taratura, a metà eco o meno il paragrafo cade in zona grigia (livelli M e D, descrittivi).
- **Una trascrizione sola; parole con ? e * tolte; pagine consecutive secondo l'ordine attuale** (rilegatura possibilmente alterata). Letteratura da ricontrollare: Timm e Schinner 2020 (*Cryptologia*),
  Montemurro e Zanette 2013 (*PLoS ONE*).
- Il v21 è costruito su tutto il manoscritto. Non è una decifrazione.

## Corse e tempo

| fase | lavoro |
|---|---|
| taratura | 6 famiglie (argP, argR, argS, argF, tecM, tecP), 1–3 livelli, ≤ 8 valutazioni ciascuna; ~2 minuti (1 processo, prova) |
| conteggi | 63 testi: `vere`, 10 libri v21, `ts1`, `ts2`, 3 lingue, 2 lingue nella disposizione, 23 generatori, 13 rimescolati fra pagine, 9 rimescolati dentro la pagina |
| analisi | bootstrap 1.000, gruppi, libri v21, ponte con ia09: 2–4 minuti |

Nella prova (disposizione del Voynich con parole latine, un processo, PC occupato, 100 confini spostati): circa 20–30 secondi per testo; stima per la corsa: **circa 30 minuti di un processore, 8–12 minuti con 4
processi** più la taratura. Uscita `risultati/ia15b_corse.jsonl` circa 19 MB (solo numeri).

## Esecuzione

`nohup bash strumenti/coda.sh ia_C "PROCESSI=4:ia15b" > /dev/null 2>&1 &` (con `RIPRENDI=1` si riprende; la fase `taratura` si rifà se manca `risultati/ia15b_taratura.json`). Scrive `risultati/ia15b_taratura.json`,
`risultati/ia15b_da_dove_eco.json` e `.md` e, una riga per testo, `risultati/ia15b_corse.jsonl` (**solo numeri**: nessuna parola, né del Voynich né delle lingue). `FASI=taratura`, `FASI=conteggi`,
`FASI=analisi` eseguono una parte. Variabili che cambiano che cosa fa il codice (da registrare nella provenienza): quelle di ia01, ia09 e ia15 (`CHIAVI`, `SOLO_CONTROLLI`, `PAGINE`, `RIGHE_PAGINA`,
`RIGHE_PAGINA_EN`, `USCITA`, `LIBRI`, `BOOT`, `GENERATORI`, `RIM_TESTO`, `SCALA_COPIA`, `FILTRO`, `RIPRENDI`, `PROCESSI`, `FASI`, `NRIF`, `SPOSTAMENTI`, `MIN_PAGINE_GRUPPO`) e le **nuove**
`ECO_FRAZIONI`, `ECO_BERSAGLIO`, `TARA_TOL`, `TARA_PASSI`, `FAMIGLIA_PHI`, `LOC_MIN`, `N_FAMIGLIE` (da aggiungere a `VARIABILI` di `esegui.py`, che non è stato toccato). I valori predefiniti sono quelli
preregistrati. `LIVELLI_ARG` e `LIVELLI_TEC` di ia15 non sono usate.

## Prova del codice (prima di questa preregistrazione)

Solo su testi non Voynich: Plinio (latino) e il Nuovo Testamento KJV (inglese) scritti **nella disposizione del Voynich** (nomi di pagina, quindi sezioni, mani, quaderni, fogli; numero di parole per riga e inizi
di paragrafo: dalla trascrizione si sono contati solo i numeri, come in ia07 con `SOLO_CONTROLLI`; nessuna parola del Voynich è stata tenuta o stampata), e i generatori sintetici costruiti **su quel lessico**
(latino o inglese), mai sul lessico del Voynich. Nessun libro v21, nessun Timm e Schinner, nessun generatore sul Voynich. Uscite in una cartella temporanea fuori dal repo. Un solo processo.

1. **Taratura (latino nella disposizione).** Bersaglio 0,00845 (eco vicina del testo). Tutti i livelli raggiunti entro l'8%: `argP` λ = 0,315 (V), 0,231 (M), 0,162 (D); `argR` 0,377 e 0,267; `argS` 0,339; `argF` 0,336 e 0,237;
   `tecM` p = 0,223, 0,128, 0,073; `tecP` 0,202, 0,119, 0,071. Da 2 a 4 valutazioni per livello, 2 minuti in tutto. Un primo errore (la ricerca si fermava se il livello nuovo coincideva con uno di un altro livello della
   stessa famiglia: `argP` D non raggiunto) è stato corretto prima della prova finale.
2. **Controlli (latino, 47 testi, 100 confini spostati, bootstrap 1.000):** **tutti superati**, valide tutte le letture (profilo, varianti, paragrafo, direzione, pagine vicine, sintesi, sintesi senza paragrafo).
   H: tecnica −0,01–0,05, argomento di pagina 0,99–1,06, famiglie 0,98–1,01, argomento di paragrafo 0,22, argomento che scorre 0,56, lingue 0,31–0,65; parte locale / eco vicina: argomento di pagina e famiglie −0,06–0,02,
   tecnica 0,95–0,99, argomento di paragrafo 0,78, lingue 0,35–0,69; **QL**: tecnica 0,61–0,64, argomento di paragrafo 0,00–0,02, argomento che scorre 0,01, latino 0,27, inglese 0,00 (famiglie e argomento di pagina: nessuna
   parte locale, QL non si legge); Q: argomento di pagina 0,88–1,13, famiglie 1,04–1,08, argomento di paragrafo −0,03–0,03, tecnica che riparte −0,19, tecnica 0,64–1,35 (zona grigia ammessa), lingue 0,94–1,03.
   Sintesi: tecnica "tecnica", argomento di pagina e famiglie "argomento di pagina", argomento di paragrafo "argomento di paragrafo", tecnica che riparte "tecnica che riparte a ogni paragrafo", argomento che scorre
   "argomento che scorre"; `latGeom`/`latino`/`vere` (latino nella disposizione) "argomento che scorre" con varianti medie. Direzione: `tecCoda1` "fine", `tecTesta1` "inizio", `tecM1` "dentro la parola".
   La quota di varianti **grezza** dell'argomento di famiglie è 0,29 con profilo piatto (con lessico a famiglie vere sarebbe più alta): la sola ragione per cui si legge sulla parte locale.
3. **Livelli M e D (descrittivi, latino):** a metà eco profilo, varianti e sintesi restano giuste per tutti; il paragrafo della tecnica (`tecMm1`, `tecPm1`) cade in zona grigia (la tecnica che riparte non si vede più);
   a un quarto della eco il paragrafo della tecnica è non leggibile e il resto resta giusto. Sono i limiti da ricordare se qualche gruppo del Voynich ha poca eco.
4. **Eco dei rimescolati** (nulli): `vere~t`, `tecM1~t`, `argP1~t`, `argF1~t` eco "debole"; `~p`: profilo piatto (0,94–1,07), nessuna parte locale.
5. **Seconda prova su un lessico diverso: inglese nella disposizione** (bersaglio molto più basso: eco vicina 0,0045, contro 0,0084 del latino e 0,0116 del Voynich in ia15; 47 testi). La taratura trova tutti i livelli
   entro il 13% (due livelli fuori dall'8%: `argP` D +12,5%, `argF` V +9,7%; i controlli valgono comunque, perché sopra il 70%). **Controlli superati** (dunque letture valide): varianti, paragrafo, direzione;
   **non superati** (letture non valide in questa prova): il profilo (il negativo `vere~p` ha H 0,85 con intervallo 0,58–1,15: con poca eco dopo il rimescolamento il limite basso non supera 0,60, quindi "intermedio" invece di "piatto")
   e le pagine vicine (`argS1` dà 1,10 contro la soglia 1,15), e quindi anche le due sintesi. Tutti i positivi sul profilo, le varianti (QL della tecnica 0,55–0,65, dell'argomento di paragrafo −0,10–0,03; famiglie e argomento di pagina "nessuna parte
   locale") e il paragrafo (tecnica che riparte "conta", argomento di paragrafo "conta" in tutte e tre le istanze) reggono. Lettura: la misura **perde forza sotto circa la metà dell'eco del latino**, e lo dichiara con un
   controllo che cade, non con un numero sbagliato; è il limite da ricordare se il Voynich (0,0116) o un suo gruppo avesse poca eco. Nessuna soglia è stata cambiata dopo questa prova.
6. **Il percorso intero** (`ia15b_da_dove_eco.main`: taratura, conteggi di un sottoinsieme di testi, analisi, scrittura di `.json` e `.md`) è stato provato in un processo solo sul latino nella disposizione (20 confini spostati,
   4 testi): nessun errore. Il pool di processi è quello di ia15 (stesse funzioni di livello superiore; la sostituzione di `costruisci` in ia15 è fatta a livello di modulo, quindi vale anche nei processi figli) e non è stato provato con
   più processi (regola della prova: un processo solo). `esegui.py ia15` e `esegui.py ia15b` trovano ciascuno un solo file.

**Non provato (non si può senza toccare il Voynich o i suoi libri):** il caricamento delle pagine vere (lo fa `ia01.contesto`, già usato da ia01, ia08–ia15), i libri `a13`–`a22` veri, Timm e Schinner,
i generatori con il lessico e la frequenza del Voynich (stessi programmi della prova; se un controllo fallisce si riporta e la lettura resta non leggibile), la taratura sul Voynich, il parallelismo con più processi,
il ponte con il vero `ia09_corse.jsonl`, e tutte le letture sul Voynich.
