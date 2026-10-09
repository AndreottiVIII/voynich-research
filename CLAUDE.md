# Istruzioni per Claude in questo repository

Ricerca statistica sul manoscritto Voynich (Beinecke MS 408) per un futuro white paper. Lavoro di Davide, in
**italiano**. Lo stato corrente del lavoro è in `STATO_LAVORI.md`: leggilo all'inizio di ogni sessione.

## Regole fisse

- **Mai dichiarare una decifrazione.** Ogni "lettura" passa dai controlli (positivo, negativo, testo
  rimescolato dentro il criterio).
- **Il repo di lavoro resta privato** (github.com/AndreottiVIII/voynich); se ne pubblica una **copia** fatta con
  `strumenti/copia_pubblica.sh` (email anonima, senza le note del revisore; decisione di Davide del 9/10/2026).
- I dati in `dati/cache` sono protetti da diritto d'autore: non vanno committati né ridistribuiti (sono in
  `.gitignore`).
- **Ordine di lavoro**, ogni passo in un commit a parte:
  1. preregistrazione `preregistrazioni/eNN.md`;
  2. codice `esperimenti/eNN_*.py`;
  3. esecuzione con `esegui.py eNN` (registra la provenienza in `risultati/provenienza/`);
  4. risultati e voce nel `QUADERNO.md`;
  5. push.
- **Prove rapide del codice:** solo sui controlli, mai sul Voynich, prima del commit della preregistrazione.
- **Il white paper** si scrive solo quando lo dice Davide.
- **QUADERNO.md:** voci datate, **solo aggiunte**, mai riscritte. Gli esiti negativi e gli errori si scrivono
  come gli altri. Le deviazioni dalla preregistrazione si dichiarano.
- **Git:**
  - aggiungere i file per nome, mai `git commit -a`;
  - comandi git uno dopo l'altro, mai in parallelo;
  - aspettare che sparisca `.git/index.lock` (lo tocca anche `esegui.py` all'avvio);
  - i messaggi di commit finiscono con `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **L'email di Davide** serve solo come autore git, mai in header o richieste web.
- **Semi deterministici**, `PYTHONHASHSEED=0` (lo imposta `esegui.py`), ambiente `.venv` con
  `requirements.txt` (Python 3.12.10).

## Come si eseguono gli esperimenti lunghi

- I processi lanciati in background dalla sessione vengono chiusi dopo circa 30 minuti. Gli esperimenti
  vanno quindi in **code staccate**:

  ```
  nohup bash strumenti/coda.sh NOME e257 "PROCESSI=4:e222" > /dev/null 2>&1 &
  nohup bash strumenti/coda.sh NOME --dopo e243b e276 > /dev/null 2>&1 &
  ```

- **Dove finiscono le cose:**
  - lo stato delle code in `esecuzioni/stato_code.txt` (righe "avvio eNN" e "FINE eNN uscita rc");
  - l'uscita di ogni esperimento in `risultati/provenienza/eNN.log`.
- **La finestra di stato** di Davide è `strumenti/Stato esperimenti.bat` (collegamento sul Desktop):
  - mostra esperimenti in esecuzione e in coda;
  - la coda si tiene aggiornata in `esecuzioni/in_coda.txt`, una riga per esperimento:
    `eNNN|descrizione|motivo`.
- **Avvisare Davide:** con un Monitor che segue `esecuzioni/stato_code.txt`, da riarmare quando scade, così
  si avvisa Davide a ogni esito.
- **`PROCESSI`** cambia solo il parallelismo, non i risultati.
- **Script lunghi:** scriverli con lo strumento Write e poi eseguirli. Gli heredoc bash con apici e
  backtick si rompono. Per le stampe usare `PYTHONIOENCODING=utf-8`.

## Documenti

- `QUADERNO.md`: quaderno di laboratorio.
- `DECISIONI.md`: decisioni di metodo, D-nnn.
- `rassegna/piano_18.md`: piano per il generatore "18/18".
  - Un passo fallito si rifà una volta, poi si dichiara la lacuna.
- `rassegna/voynichizzatore_progetto.md`: progetto del voynichizzatore. Scelte di Davide del 3/10/2026:
  - imita tutto il manoscritto (sezioni, mani, A/B);
  - uscita EVA più immagine, con etichette e testo circolare;
  - chiave a parola chiave;
  - l'indistinguibilità prevale sulla compattezza.
- `DOSSIER_WHITE_PAPER.md`: materiale per il white paper.
