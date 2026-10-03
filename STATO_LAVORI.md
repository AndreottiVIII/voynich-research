# Stato dei lavori

Fotografia aggiornata a mano a ogni cambio importante. I dettagli e i numeri sono nel `QUADERNO.md`.

## 3/10/2026 — trasloco su un PC più potente

Il vecchio PC (i5-7200U, 2 core, 8 GB) era saturo.

**Coordinamento fra i due PC:**
- **Vecchio PC:** finisce gli esperimenti già avviati e ne committa i risultati. Non avvia altro.
- **Nuovo PC:** prende tutto ciò che non è ancora partito.
- **Prima di ogni commit sul nuovo PC:** `git pull --rebase`. Il QUADERNO riceve aggiunte da entrambi
  finché il vecchio non ha finito.

**Ancora in corso sul vecchio PC al momento del trasloco:**

| esperimento | che cosa | note |
|---|---|---|
| e243 | piano 18/18, passo 1: riuso esplicito autoreferenziale | già fallito al seme 7 (8/18, AUC 0,975); finisce i semi |
| e249 | pezzi delle parole come simboli | — |
| e269 | decifrazione sulle sole parole non copiate | — |
| e270 | parole nuove delle piante (e190 con profili di bigrammi) | — |
| e275 | generatore appreso dalla mistura dell'e259b | — |

## Primo compito sul nuovo PC: verifica del trasloco

1. Rieseguire **e277** ed **e278**, che sono veloci.
2. Confrontare i `.json` con quelli committati. Devono essere identici, a parte il blocco di provenienza.
3. Scrivere l'esito nel QUADERNO (voce "trasloco"):
   - processore, Python e versioni dei pacchetti del nuovo PC;
   - il fatto che `dati/cache` è stato copiato dal vecchio PC.

## Da fare (in ordine)

1. **e257** (righe gemelle).
2. **Catena di decifrazione:** e222 → e219 → e223 → e216 → e212b. Con più core si può alzare `PROCESSI`.
3. **e276** (κ e χ per sezione).
   - Il codice è pronto e può partire subito.
   - L'e243b è chiuso (non superato, AUC e266 0,947), quindi la base sarà l'e241.
4. **Piano 18/18, passo 2 (e251).**
   - Il passo 1 è chiuso con la lacuna dichiarata (e243 ed e243b non superati).
   - Il codice attuale è costruito sul generatore dell'e243, che ha fallito.
   - Va rifatto sopra l'e241, con un'**integrazione alla preregistrazione**
     committata prima.
   - Poi **e252** (12 interruttori di riga).
5. **Da scrivere:**
   - **e267**, modulo etichette: le etichette sono un sistema a parte che copia le etichette vicine;
   - **e268**, registro delle prime righe: lessico d'apertura per sezione, *opch-*, *qopch-*, *pch-*
     (e273, e278).
6. **Poi:** e253 (taratura congiunta), e254 (ciclo avversario, obiettivo AUC ≤ 0,6), e225
   (voynichizzatore).
   - Da decidere fra la strada costruita a mano e quella appresa (e275).
7. **Piccoli:**
   - e278b: la stessa misura con gruppi di uguale grandezza;
   - semi in parallelo negli esperimenti sui generatori.
8. **Più avanti:** e194, ridisegno ch/sh ad alta risoluzione, insieme a Davide.

## Dove siamo, in breve

- **Generatore migliore:** e241 (pagella 16/18, AUC e231 0,874, AUC e266 0,937).
  - Mancano ancora: verticale, formule, R delle parole rare (Voynich 1,96, generatore ~50), registro delle
    prime righe, varietà di pagina, etichette.
  - Il discriminatore (e243b, e231) vede nel generatore:
    - lunghezze delle parole più disperse;
    - meno parole frequenti e meno parole diverse nella pagina;
    - parole vicine meno simili.
- **Decifrazione:** tutti gli attacchi danno "nessuna lettura". I candidati dell'e217 erano artefatti.
- **Procedimento accertato:**
  - copia "a vista" dalla riga sopra;
  - 12 scelte di grafia per riga;
  - parole spezzate e prefissi staccati;
  - registro d'apertura dei paragrafi, ma senza formule fisse (e278);
  - nessuna isola di testo diverso (e274);
  - ~11 bit per parola non spiegati dalla copia.
