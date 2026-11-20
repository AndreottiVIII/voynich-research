# -*- coding: utf-8 -*-
"""Esperimento ia03 (IA3): quanto contesto serve a un modello minuscolo per prevedere il segno successivo.

Stesso modello di e3c95 (GRU a caratteri, un solo strato, 32 di immersione, 128 unita', caduta 0,3 sull'uscita), ma
addestrato su finestre di 256 segni che partono da uno stato vuoto, in modo che impari a prevedere con ogni lunghezza
di contesto da 0 a 255 segni. Ogni finestra comincia con un segno speciale di inizio (BOS): il contesto "k = 0" e' il
solo BOS. Le finestre stanno dentro un blocco (una pagina o 29 righe): non passano da un blocco all'altro.

Per ogni testo e seme: stessi blocchi e stessa divisione di e3c95 (40.000 segni di addestramento, 5.000 di validazione,
10.000 di prova; `random.Random(1000 + seme)` sui blocchi). Differenza rispetto a e3c95: qui i blocchi si tengono
distinti, perche' un contesto non deve attraversare un confine di blocco.

Arresto anticipato: ogni OGNI passi si misura la BPC (bit per segno) sulla validazione "con contesto pieno", cioe' sui
segni che hanno 192-255 segni di contesto (finestre di 256 con passo 64, si contano gli ultimi 64 segni di ogni
finestra). Ci si ferma quando non migliora da PAZIENZA valutazioni; si ricaricano i pesi con la validazione piu' bassa.
La prova non serve mai a scegliere.

Due varianti con gli stessi pesi: A = solo GRU; B = GRU piu' cache neurale (Grave, Joulin e Usunier 2017, forma a
normalizzazione globale: p(v) = (p_GRU(v) + alfa * somma dei pesi delle coppie con segno v) / (1 + alfa * somma dei pesi),
con peso exp(theta * (q . y_j - q . q)) per le coppie (stato y_j, segno che seguiva j) dei soli k segni ammessi); alfa e
theta si scelgono sulla validazione con contesto pieno. Le letture si fanno sulla B; la A e' descrittiva.

Misure sulla prova, con i pesi scelti. I bersagli sono i segni con almeno 255 segni prima nello stesso blocco: gli
stessi per ogni k.
- BPC(k): per ogni bersaglio la rete legge BOS piu' i k segni subito prima, da stato vuoto (k = 0, 1, 2, 3, 4, 6, 8,
  12, 16, 24, 32, 48, 64, 96, 128, 192, 255);
- k90: il piu' piccolo k della griglia per cui BPC(0) - BPC(k) >= 90% di BPC(0) - BPC(255) (None se il guadagno
  totale e' sotto SOGLIA_GUADAGNO); k90 interpolato: lo stesso, con interpolazione lineare fra i punti della griglia;
- guadagno lungo GL = BPC(32) - BPC(255);
- guadagno dalla riga sopra GR: per i segni con almeno 64 segni prima nel blocco, perdita con il contesto di 64 segni
  tagliato all'inizio della riga corrente (BOS, il segno a capo che apre la riga e i segni della riga) meno perdita
  con 64 segni anche oltre l'a capo; media su tutti i bersagli (GR) e sui soli bersagli a meno di 64 segni dall'inizio della riga (GR_corte);
- per il solo Voynich intero, GR sulle 6 pagine di solo testo (f1r, f66r, f76r, f85r1, f86v5, f86v6) che non sono
  nell'addestramento ne' nella validazione di quel seme.

Preregistrazione: preregistrazioni/ia03.md. Scrive risultati/ia03_contesto.json e .md e, una riga per corsa,
risultati/ia03_corse.jsonl (con RIPRENDI=1 le corse gia' fatte non si rifanno).
SOLO_CONTROLLI=1: niente Voynich ne' generatori in EVA (per provare il codice). Per le prove: PASSI, OGNI, PAZIENZA,
SEMI, LUNG, LOTTO, NASCOSTO, CADUTA; TESTI (sottostringhe separate da |, "=Nome" per il nome esatto); USCITA cambia la
cartella d'uscita; PROVA_SPECIALI=1 usa i primi 6 blocchi delle lingue al posto delle 6 pagine del Voynich.
PROCESSI: numero di processi in parallelo (non cambia i risultati).
"""
import bisect, json, math, os, random, statistics, sys, time
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c95_imparabilita as e95

N_ADD, N_VAL, N_PROVA = e95.N_ADD, e95.N_VAL, e95.N_PROVA
PASSI = int(os.environ.get('PASSI', 2000))
OGNI = int(os.environ.get('OGNI', 20))
PAZIENZA = int(os.environ.get('PAZIENZA', 10))
SEMI = tuple(int(s) for s in os.environ.get('SEMI', '1,2,3,4,5,6,7,8,9,10').split(','))
LUNG = int(os.environ.get('LUNG', 256))          # segni per finestra di addestramento (bersagli)
LOTTO = int(os.environ.get('LOTTO', 8))          # finestre per passo
EMB, NASCOSTO, CADUTA = 32, int(os.environ.get('NASCOSTO', 128)), float(os.environ.get('CADUTA', 0.3))
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
# cache neurale (variante B): alfa e theta si scelgono sulla validazione con contesto pieno, in questa griglia
ALFE = (0.0, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0)
TETE = (0.1, 0.2, 0.4, 0.8, 1.6, 3.2)
KS = (0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 255)
K_MAX = 255
CONTESTO_RIGA = 64                               # contesto per la misura della riga sopra
FINESTRA_VAL = 64                                # segni contati in ogni finestra di validazione (gli ultimi)
PASSO_VAL = 64                                   # passo fra le finestre di validazione
SOGLIA_GUADAGNO = 0.25                           # bit per segno: sotto, k90 non e' definito
MAX_TOKEN = 300000                               # segni letti in un lotto di valutazione (memoria)
MIN_BERSAGLI = 2000                              # minimo di bersagli della prova (k) e della riga sopra
MIN_FINESTRE_ADD = 200                           # minimo di partenze possibili nell'addestramento
MIN_BERSAGLI_VAL = 500
MAX_BERSAGLI_VAL = 2000                          # bersagli di validazione per scegliere alfa e theta (per ogni k)
NL_STR = chr(10)                                 # il segno a capo
C1_NOME = 'C1 catena di Markov di ordine 3 (controllo negativo)'
C2_NOME = 'C2 latino con ogni riga ripetuta sotto (controllo positivo)'
C4_NOME = 'C4 latino con ogni riga ripetuta due righe piu avanti (ripetizione a circa 170 segni)'
C3_NOME = "C3 latino, ogni riga comincia con gli ultimi 3 segni della riga sopra (controllo positivo)"
SPECIALI_VOYNICH = ('f1r', 'f66r', 'f76r', 'f85r1', 'f86v5', 'f86v6')
RARO = e95.RARO
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
NOME = 'ia03_contesto'

# soglie dei controlli (fissate dopo le prove del codice sui controlli: vedi preregistrazioni/ia03.md)
SOGLIA_C1_K90 = 4            # catena di ordine 3: k90 al massimo 4
SOGLIA_NEG_GL = 0.02         # bit: C1, guadagno lungo al massimo questo
SOGLIA_RIMESC_GL = 0.10      # bit: testi rimescolati, guadagno lungo al massimo questo
SOGLIA_NEG_GR = 0.03         # bit: controlli negativi, guadagno dalla riga sopra al massimo questo
SOGLIA_PEGGIORAMENTO = 0.01     # bit: verifica, in nessun k la B e' peggiore della A di piu' di questo (sulla prova)
SOGLIA_POS_GR = 0.05         # bit: controllo positivo C3, GR(C3) - GR(C1) almeno questo (variante A e B)
SOGLIA_POS_C2 = 0.5          # bit: variante B, controllo positivo C2 (righe ripetute), GR(C2) - GR(C1) almeno questo
SOGLIA_POS_GL = 0.5          # bit: variante B, controllo positivo C4 (ripetizione a ~170 segni), GL(C4) - GL(C1)


# ---------------------------------------------------------------- testi

def nomi_pagine_voynich():
    """Nomi delle pagine nello stesso ordine di e95.voynich_pagine() (una pagina c'e' se ha almeno una parola pulita)."""
    import trascrizione
    nomi = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=None):
        if any(trascrizione.pulita(p) for p in r.parole):
            nomi.setdefault(r.pagina, 0)
    return list(nomi)


def tabelle_ordine3(blocchi_lingua):
    """Tabelle di una catena di Markov di ordine 3 sui segni di un testo (spazio e a capo inclusi): per ogni contesto
    di 3 segni, (segni possibili, frequenze cumulate, totale)."""
    seq = e95.flusso([r for b in blocchi_lingua for r in b])
    conti = defaultdict(Counter)
    for i in range(3, len(seq)):
        conti[tuple(seq[i - 3:i])][seq[i]] += 1
    tabelle = {}
    for c, cnt in conti.items():
        simboli = sorted(cnt)
        cum, tot = [], 0
        for s in simboli:
            tot += cnt[s]
            cum.append(tot)
        tabelle[c] = (simboli, cum, tot)
    return tabelle, seq


def genera_segni(tabelle, ctx, rnd, n):
    """n segni dalla catena, partendo dal contesto ctx (lista di 3 segni)."""
    out, ctx = [], list(ctx)
    while len(out) < n:
        t = tabelle.get(tuple(ctx))
        if t is None:                      # contesto senza seguito (solo la fine del testo): si riparte da uno a caso
            ctx = list(rnd.choice(sorted(tabelle)))
            continue
        simboli, cum, tot = t
        s = simboli[bisect.bisect_right(cum, rnd.random() * tot)]
        out.append(s)
        ctx = ctx[1:] + [s]
    return out


def in_righe(segni):
    righe = []
    for ch in ''.join(segni).split(NL_STR):
        ws = [tuple(w) for w in ch.split(' ') if w]
        if ws:
            righe.append(ws)
    return righe


def catena_ordine3(blocchi_latino, n_segni, seme=98):
    """C1: catena di Markov di ordine 3 sui segni del latino, stimata su tutto il testo; genera n_segni segni e li
    riporta in blocchi di 29 righe."""
    tabelle, seq = tabelle_ordine3(blocchi_latino)
    return e95.blocchi_di(in_righe(genera_segni(tabelle, seq[:3], random.Random(seme), n_segni)))


def ripresa_ultimi_segni(blocchi, n=3):
    """C3: ogni riga (tranne la prima di ogni blocco) comincia con gli ultimi n segni della riga sopra (spazi
    compresi, ricomposti in parole). L'informazione passa l'a capo, a distanza fissa di n + 1 segni: la rete la puo'
    prendere con la sua memoria corta (lo stesso tipo di dipendenza che impara in C1)."""
    out = []
    for b in blocchi:
        nb = [list(b[0])]
        for prec, r in zip(b, b[1:]):
            coda = e95.flusso([prec])[:-1][-n:]                 # senza il segno a capo
            prefisso = [tuple(w) for w in ''.join(coda).split(' ') if w]
            nb.append(prefisso + list(r))
        out.append(nb)
    return out


def ripetizione_a_distanza(righe, d=2):
    """C4: dopo la riga i compare di nuovo la riga i - d: ogni riga si ripete d righe piu' avanti (con d = 2 la copia
    sta a circa 4 righe, cioe' 150-200 segni, dall'originale: oltre il contesto di 32 e dentro quello di 255)."""
    out = []
    for i, r in enumerate(righe):
        out.append(r)
        if i >= d:
            out.append(righe[i - d])
    return out


def catalogo():
    """Testi dell'esperimento: nome -> dict(blocchi, ruolo, trasforma, speciali). Parte dal catalogo di e3c95 (senza i
    suoi rimescolati, trasferimenti e cifrati) e aggiunge i controlli C1 e C2 e il latino rimescolato."""
    filtro = [s for s in os.environ.get('TESTI', '').split('|') if s]
    salvato = os.environ.pop('TESTI', None)       # il filtro si applica alla fine, sul catalogo completo
    e95.SOLO_CONTROLLI = SOLO_CONTROLLI
    try:
        base = e95.catalogo()
    finally:
        if salvato is not None:
            os.environ['TESTI'] = salvato
    t = OrderedDict()
    for nome, v in base.items():
        if v['ruolo'] in ('voynich', 'generatore', 'lingua'):
            t[nome] = dict(blocchi=v['blocchi'], ruolo=v['ruolo'], trasforma=None, speciali=None,
                           sorgente=v.get('sorgente'))
        elif nome == 'Voynich, segni rimescolati (controllo negativo)':
            t['Voynich, segni rimescolati'] = dict(blocchi=v['blocchi'], ruolo='controllo', trasforma='lettere',
                                                   speciali=None)
    if 'Voynich' in t and not SOLO_CONTROLLI:
        nomi = nomi_pagine_voynich()
        if len(nomi) == len(t['Voynich']['blocchi']):
            t['Voynich']['speciali'] = {nomi.index(n): n for n in SPECIALI_VOYNICH if n in nomi}
            if len(t['Voynich']['speciali']) != len(SPECIALI_VOYNICH):
                print('ATTENZIONE: trovate %d pagine di solo testo su %d (mancano: %s)' % (
                    len(t['Voynich']['speciali']), len(SPECIALI_VOYNICH),
                    ', '.join(n for n in SPECIALI_VOYNICH if n not in nomi)), flush=True)
        else:
            print('ATTENZIONE: i nomi delle pagine (%d) non corrispondono alle pagine (%d): niente pagine di solo '
                  'testo' % (len(nomi), len(t['Voynich']['blocchi'])), flush=True)
    if os.environ.get('PROVA_SPECIALI') == '1':
        for nome, v in t.items():
            if v['ruolo'] == 'lingua':
                v['speciali'] = {i: 'blocco %d' % i for i in range(6)}
    if 'Latin' in t:
        lat = t['Latin']['blocchi']
        t['Latin, segni rimescolati'] = dict(blocchi=lat, ruolo='controllo', trasforma='lettere', speciali=None)
        t[C1_NOME] = dict(
            blocchi=catena_ordine3(lat, 150000), ruolo='controllo', trasforma=None, speciali=None)
        t[C2_NOME] = dict(
            blocchi=[[r for r in b for _ in (0, 1)] for b in lat], ruolo='controllo', trasforma=None, speciali=None)
        t[C4_NOME] = dict(blocchi=[ripetizione_a_distanza(b) for b in lat], ruolo='controllo', trasforma=None,
                          speciali=None)
        t[C3_NOME] = dict(blocchi=ripresa_ultimi_segni(lat), ruolo='controllo', trasforma=None, speciali=None)
    if filtro:
        t = OrderedDict((k, v) for k, v in t.items()
                        if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro))
    return t


def dividi(blocchi, seme):
    """Indici dei blocchi di addestramento, validazione e prova (la stessa regola di e95.dividi_blocchi); None se la
    prova resta corta."""
    ordine = list(range(len(blocchi)))
    random.Random(1000 + seme).shuffle(ordine)
    quote, parti, n, k = (N_ADD, N_VAL, N_PROVA), ([], [], []), [0, 0, 0], 0
    for i in ordine:
        while k < 3 and n[k] >= quote[k]:
            k += 1
        if k == 3:
            break
        parti[k].append(i)
        n[k] += len(e95.flusso(blocchi[i]))
    if n[2] < N_PROVA:
        return None
    return parti


def flussi(righe_per_blocco, quota):
    """Flusso di segni dei blocchi dati, tagliato esattamente a `quota` segni, con i confini dei blocchi."""
    seq, conf = [], []
    for righe in righe_per_blocco:
        f = e95.flusso(righe)
        s = len(seq)
        if s >= quota:
            break
        f = f[:quota - s]
        seq.extend(f)
        conf.append((s, s + len(f)))
    return seq, conf


def prepara(t):
    """Per ogni (testo, seme): flussi codificati con i confini dei blocchi. Esclude i testi senza abbastanza bersagli."""
    import numpy as np
    alfabeti = {nome: e95.frequenti([v['blocchi']]) for nome, v in t.items()}
    lavori, scarti = [], OrderedDict()
    for nome, v in t.items():
        voc = sorted(alfabeti[nome] | {' ', '\n', RARO})
        idx = {s: i for i, s in enumerate(voc)}
        V, NL = len(voc), idx['\n']

        def cod(seq):
            return [idx.get(s, idx[RARO]) for s in seq]
        proprio = []
        for seme in SEMI:
            d = dividi(v['blocchi'], seme)
            if d is None:
                scarti[nome] = 'prova troppo corta (seme %d)' % seme
                break
            righe = [[v['blocchi'][i] for i in ix] for ix in d]       # per parte: lista di blocchi (liste di righe)
            if v['trasforma']:
                rnd = random.Random(7919 * seme + 1)
                f = e95.rimescola_parole if v['trasforma'] == 'parole' else e95.rimescola_lettere
                nuove = []
                for parte in righe:
                    piatte = f([r for b in parte for r in b], rnd)
                    out, k = [], 0
                    for b in parte:
                        out.append(piatte[k:k + len(b)])
                        k += len(b)
                    nuove.append(out)
                righe = nuove
            (add, add_b), (val, val_b), (prova, prova_b) = [flussi(x, q) for x, q in
                                                              zip(righe, (N_ADD, N_VAL, N_PROVA))]
            # controlli sul numero di bersagli
            n_add = sum(max(0, e - s - LUNG + 1) for s, e in add_b)
            n_val = sum(max(0, (e - s - LUNG) // PASSO_VAL + 1) * FINESTRA_VAL for s, e in val_b if e - s >= LUNG)
            n_prova = sum(max(0, e - s - K_MAX) for s, e in prova_b)
            if n_add < MIN_FINESTRE_ADD or n_val < MIN_BERSAGLI_VAL or n_prova < MIN_BERSAGLI:
                scarti[nome] = 'pochi bersagli (seme %d: addestramento %d, validazione %d, prova %d)' % (
                    seme, n_add, n_val, n_prova)
                break
            speciali = []
            if v['speciali']:
                usati = set(d[0]) | set(d[1])
                for i, nm in v['speciali'].items():
                    if i not in usati:
                        speciali.append((nm, cod(e95.flusso(v['blocchi'][i]))))
            proprio.append(dict(testo=nome, seme=seme, V=V, NL=NL, add=cod(add), add_b=add_b, val=cod(val),
                                val_b=val_b, prova=cod(prova), prova_b=prova_b, speciali=speciali))
        else:
            lavori.extend(proprio)
    return lavori, scarti


# ---------------------------------------------------------------- modello

def avvia_processo():
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def corsa(lavoro):
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Modello(nn.Module):
        def __init__(self, V):
            super().__init__()
            self.emb = nn.Embedding(V + 1, EMB)         # l'ultimo segno e' BOS
            self.gru = nn.GRU(EMB, NASCOSTO, batch_first=True)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(NASCOSTO, V)

        def forward(self, x):
            y, _ = self.gru(self.emb(x))
            return self.out(self.caduta(y))

        def stati(self, x):
            y, _ = self.gru(self.emb(x))
            return y

    inizio = time.time()
    seme, V, NL = lavoro['seme'], lavoro['V'], lavoro['NL']
    BOS = V
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = Modello(V)
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    add = torch.tensor(lavoro['add'], dtype=torch.long)
    val = torch.tensor(lavoro['val'], dtype=torch.long)
    prova = torch.tensor(lavoro['prova'], dtype=torch.long)
    ar = torch.arange(LUNG)
    partenze = np.array([a for s, e in lavoro['add_b'] for a in range(s, e - LUNG + 1)], dtype=np.int64)
    ws = np.array([a for s, e in lavoro['val_b'] if e - s >= LUNG for a in range(s, e - LUNG + 1, PASSO_VAL)],
                  dtype=np.int64)
    finestre_val = val[torch.from_numpy(ws)[:, None] + ar]                       # (n, LUNG)
    ingresso_val = torch.cat([torch.full((len(ws), 1), BOS), finestre_val[:, :-1]], 1)
    bersagli_val = finestre_val[:, LUNG - FINESTRA_VAL:].reshape(-1)

    def valuta():
        m.eval()
        with torch.no_grad():
            logit = m(ingresso_val)[:, LUNG - FINESTRA_VAL:].reshape(-1, V)
            bpc = F.cross_entropy(logit, bersagli_val).item() / math.log(2)
        m.train()
        return round(bpc, 5)

    validazione, perdite, perdita = [], [], 0.0
    migliore, stato = None, None
    for passo in range(1, PASSI + 1):
        sc = torch.from_numpy(partenze[rng.integers(0, len(partenze), size=LOTTO)])
        xb = add[sc[:, None] + ar]                                               # (LOTTO, LUNG)
        ingresso = torch.cat([torch.full((LOTTO, 1), BOS), xb[:, :-1]], 1)
        logit = m(ingresso)
        loss = F.cross_entropy(logit.reshape(-1, V), xb.reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        perdita += loss.item()
        if passo % OGNI == 0:
            validazione.append(valuta())
            perdite.append(round(perdita / OGNI / math.log(2), 5))
            perdita = 0.0
            if migliore is None or validazione[-1] < migliore:
                migliore = validazione[-1]
                stato = {k: v.clone() for k, v in m.state_dict().items()}
            if len(validazione) - 1 - validazione.index(min(validazione)) >= PAZIENZA:
                break
    m.load_state_dict(stato)
    m.eval()
    scelta = validazione.index(min(validazione))

    ln2 = math.log(2)

    # variante B: GRU piu' cache neurale (Grave, Joulin e Usunier 2017), nella forma a normalizzazione globale. Dato lo
    # stato q che prevede il segno successivo, la cache ha le coppie (y_j, segno che seguiva j) per i segni j del
    # contesto ammesso, con peso w_j = exp(theta * (q . y_j - q . q)); poi
    #   p(v) = (p_GRU(v) + alfa * somma dei w_j delle coppie con segno v) / (1 + alfa * somma di tutti i w_j).
    # Con alfa = 0 la B e' la A. Senza coppie, o con coppie lontane da q, p = p_GRU. Alfa e theta si scelgono sulla
    # validazione per ogni lunghezza di contesto k (e per il contesto tagliato della riga sopra), nella griglia
    # ALFE x TETE che contiene alfa = 0: cosi' sulla validazione la B non e' mai peggiore della A. I pesi della GRU
    # sono gli stessi della variante A.

    def lotti(flusso, pos, lung):
        """Per gruppi di bersagli con lo stesso contesto: (indici, L, stati y, ingresso x, bersagli, log p_GRU)."""
        for L in np.unique(lung):
            L = int(L)
            sel = np.nonzero(lung == L)[0]
            blocco = max(256, min(8192, MAX_TOKEN // (L + 1)))
            for i in range(0, len(sel), blocco):
                ss = sel[i:i + blocco]
                p = torch.from_numpy(pos[ss])
                cols = [torch.full((len(ss), 1), BOS)]
                if L:
                    cols.append(flusso[p[:, None] - L + torch.arange(L)])
                with torch.no_grad():
                    x = torch.cat(cols, 1)
                    y = m.stati(x)
                    lp = torch.log_softmax(m.out(y[:, -1]), -1)
                    tgt = flusso[p]
                    yield ss, L, y, x, tgt, lp.gather(1, tgt[:, None])[:, 0]

    def punti_cache(y, x, tgt):
        """Prodotti q.y_j - q.q (b, L) e maschera delle coppie col segno uguale al bersaglio."""
        q = y[:, -1]
        return (torch.einsum('bh,blh->bl', q, y[:, :-1]) - (q * q).sum(1, keepdim=True),
                x[:, 1:] == tgt[:, None])

    def perdita_cache(punti, uguale, lpt, al, th):
        """Perdita (nat) dei bersagli con la cache (alfa, theta)."""
        if al == 0:
            return -lpt
        sc_ = th * punti
        ltot = torch.logsumexp(sc_, 1)
        lm = torch.logsumexp(sc_.masked_fill(~uguale, float('-inf')), 1)
        lnum = torch.logaddexp(lpt, math.log(al) + lm)
        lden = torch.logaddexp(torch.zeros_like(ltot), math.log(al) + ltot)
        return lden - lnum

    def seleziona(flusso, pos, lung):
        """(alfa, theta) con la perdita totale piu' bassa sui bersagli dati (la validazione). Parita': alfa = 0."""
        somma = np.zeros((len(TETE), len(ALFE)))
        for ss, L, y, x, tgt, lpt in lotti(flusso, pos, lung):
            if L == 0:
                continue
            punti, uguale = punti_cache(y, x, tgt)
            for ti, th in enumerate(TETE):
                for ai, al in enumerate(ALFE):
                    somma[ti, ai] += perdita_cache(punti, uguale, lpt, al, th).sum().item()
        ti, ai = np.unravel_index(np.argmin(somma), somma.shape)
        return (ALFE[ai], TETE[ti]) if ALFE[ai] > 0 else (0.0, TETE[0])

    def perdite_bersagli(flusso, pos, lung, par):
        """Perdite in bit di ogni bersaglio pos[i], con contesto di esattamente lung[i] segni (BOS piu' i segni):
        (variante A, variante B con i parametri par = (alfa, theta))."""
        out_a, out_b = np.zeros(len(pos)), np.zeros(len(pos))
        for ss, L, y, x, tgt, lpt in lotti(flusso, pos, lung):
            out_a[ss] = (-lpt / ln2).numpy()
            if L and par[0] > 0:
                punti, uguale = punti_cache(y, x, tgt)
                out_b[ss] = (perdita_cache(punti, uguale, lpt, par[0], par[1]) / ln2).numpy()
            else:
                out_b[ss] = out_a[ss]
        return out_a, out_b

    def posizioni(stream, conf):
        """Inizio del blocco e inizio della riga di ogni posizione."""
        n = len(stream)
        bs, rs = np.zeros(n, dtype=np.int64), np.zeros(n, dtype=np.int64)
        for s, e in conf:
            ls = s
            for j in range(s, e):
                bs[j], rs[j] = s, ls
                if stream[j] == NL:
                    ls = j + 1
        return bs, rs

    def campione(pos, massimo=MAX_BERSAGLI_VAL):
        passo = max(1, -(-len(pos) // massimo))
        return pos[::passo]

    def bersagli_riga(stream, conf):
        """Bersagli con almeno CONTESTO_RIGA segni prima nel blocco, e fra questi quelli a meno di CONTESTO_RIGA segni
        dall'inizio della riga (contesto tagliato di p + 1 segni: il segno a capo che apre la riga e i p della riga)."""
        bs, rs = posizioni(stream, conf)
        i = np.arange(len(stream))
        tutti = i[(i - bs) >= CONTESTO_RIGA]
        p = tutti - rs[tutti]
        corte = tutti[p < CONTESTO_RIGA]
        return tutti, corte, (corte - rs[corte] + 1).astype(np.int64)

    # scelta di alfa e theta sulla validazione: per ogni k, e per il contesto tagliato della riga sopra
    bsv, rsv = posizioni(lavoro['val'], lavoro['val_b'])
    iv = np.arange(len(lavoro['val']))
    val_k = campione(iv[(iv - bsv) >= K_MAX])
    par = OrderedDict()
    for k in KS:
        par[k] = seleziona(val, val_k, np.full(len(val_k), k, dtype=np.int64)) if k else (0.0, TETE[0])
    _, val_corte, val_lc = bersagli_riga(lavoro['val'], lavoro['val_b'])
    ss_ = np.arange(len(val_corte))[::max(1, -(-len(val_corte) // MAX_BERSAGLI_VAL))]
    par_taglio = seleziona(val, val_corte[ss_], val_lc[ss_]) if len(ss_) else (0.0, TETE[0])
    par_pieno = par[CONTESTO_RIGA]

    def riga_sopra(flusso, stream, conf):
        """Somme sui bersagli con almeno CONTESTO_RIGA segni prima nel blocco: n tutti, n corte, somma delle differenze
        (tagliato meno 64 segni), somma delle perdite; per la variante A e, con il suffisso _B, per la B."""
        tutti, corte, lc = bersagli_riga(stream, conf)
        r = dict(n_tutti=int(len(tutti)), n_corte=int(len(corte)))
        if len(corte) == 0:
            return dict(r, somma_diff=0.0, somma_taglio=0.0, somma_pieno=0.0, somma_diff_B=0.0, somma_taglio_B=0.0,
                        somma_pieno_B=0.0)
        ta, tb = perdite_bersagli(flusso, corte, lc, par_taglio)
        pa, pb = perdite_bersagli(flusso, corte, np.full(len(corte), CONTESTO_RIGA, dtype=np.int64), par_pieno)
        return dict(r, somma_diff=float((ta - pa).sum()), somma_taglio=float(ta.sum()), somma_pieno=float(pa.sum()),
                    somma_diff_B=float((tb - pb).sum()), somma_taglio_B=float(tb.sum()), somma_pieno_B=float(pb.sum()))

    # curva BPC(k) sulla prova
    bs, rs = posizioni(lavoro['prova'], lavoro['prova_b'])
    i = np.arange(len(lavoro['prova']))
    bersagli = i[(i - bs) >= K_MAX]
    curva, curva_b = OrderedDict(), OrderedDict()
    for k in KS:
        la, lb = perdite_bersagli(prova, bersagli, np.full(len(bersagli), k, dtype=np.int64), par[k])
        curva[str(k)], curva_b[str(k)] = round(float(la.mean()), 5), round(float(lb.mean()), 5)
    conti = [0.5] * V
    for s in lavoro['add']:
        conti[s] += 1
    tot = sum(conti)
    h1 = -sum(math.log2(conti[s] / tot) for s in prova[bersagli].tolist()) / len(bersagli)
    riga = riga_sopra(prova, lavoro['prova'], lavoro['prova_b'])
    speciali = []
    for nome, stream in lavoro['speciali']:
        r = riga_sopra(torch.tensor(stream, dtype=torch.long), stream, [(0, len(stream))])
        r['pagina'] = nome
        speciali.append(r)
    n_righe = max(1, sum(1 for s in lavoro['prova'] if s == NL))
    return dict(testo=lavoro['testo'], seme=seme, V=V, parametri=sum(p.numel() for p in m.parameters()),
                h1=round(h1, 5), curva=curva, curva_B=curva_b,
                cache_B={str(k): list(v) for k, v in par.items()}, cache_B_taglio=list(par_taglio),
                max_peggioramento_B=round(max(curva_b[str(k)] - curva[str(k)] for k in KS), 5),
                n_bersagli=int(len(bersagli)), n_bersagli_validazione=int(len(val_k)), riga=riga, speciali=speciali,
                lunghezza_riga=round(len(lavoro['prova']) / n_righe, 2),
                validazione=validazione, addestramento=perdite, scelta=scelta, bpc_validazione=min(validazione),
                passi=passo, segni_per_valutazione=OGNI * LOTTO * LUNG, segni_addestramento=len(lavoro['add']),
                finestre_addestramento=int(len(partenze)), finestre_validazione=int(len(ws)),
                secondi=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- misure

VARIANTI = ('B', 'A')       # la B (GRU piu' cache) e' quella delle letture; la A (solo GRU) e' descrittiva


def misure_corsa(c, v='A'):
    suf = '_B' if v == 'B' else ''
    cu = {int(k): x for k, x in c['curva' + suf].items()}
    b0, bmax = cu[0], cu[K_MAX]
    guad = b0 - bmax
    k90, k90i = None, None
    if guad >= SOGLIA_GUADAGNO:
        soglia = 0.9 * guad
        guadagni = [b0 - cu[k] for k in KS]
        j = next(j for j, g in enumerate(guadagni) if g >= soglia)
        k90 = KS[j]
        k90i = float(KS[0]) if j == 0 else KS[j - 1] + (KS[j] - KS[j - 1]) * (soglia - guadagni[j - 1]) / (
            guadagni[j] - guadagni[j - 1])
    r = c['riga']
    return dict(bpc0=b0, bpc32=cu[32], bpc255=bmax, h1=c['h1'], G255=1 - bmax / c['h1'], guadagno_totale=guad,
                k90=k90, k90_interpolato=k90i, GL=cu[32] - bmax,
                GR=(r['somma_diff' + suf] / r['n_tutti']) if r['n_tutti'] else None,
                GR_corte=(r['somma_diff' + suf] / r['n_corte']) if r['n_corte'] else None,
                bpc_validazione=c['bpc_validazione'], lunghezza_riga=c['lunghezza_riga'],
                max_peggioramento=c['max_peggioramento_B'] if v == 'B' else None,
                epoche_scelte=(c['scelta'] + 1) * c['segni_per_valutazione'] / c['segni_addestramento'])


def media_ds(xs):
    return e95.media_ds(xs)


def analizza(t, corse, v='A'):
    suf = '_B' if v == 'B' else ''
    per = OrderedDict()
    for nome in t:
        cs = sorted((c for c in corse if c['testo'] == nome), key=lambda c: c['seme'])
        if cs:
            per[nome] = cs
    tab = OrderedDict()
    for nome, cs in per.items():
        ms = [misure_corsa(c, v) for c in cs]
        tab[nome] = OrderedDict((k, media_ds([m[k] for m in ms])) for k in ms[0])
        tab[nome]['ruolo'] = t[nome]['ruolo']
        tab[nome]['V'] = cs[0]['V']
        tab[nome]['seme_k90_non_definito'] = sum(1 for m in ms if m['k90'] is None)
        tab[nome]['curva'] = OrderedDict((str(k), statistics.mean(c['curva' + suf][str(k)] for c in cs)) for k in KS)
        tab[nome]['secondi'] = statistics.mean(c['secondi'] for c in cs)
        tab[nome]['corse_al_limite'] = sum(1 for c in cs if c['passi'] >= PASSI)
        tab[nome]['alfa'] = media_ds([c['cache_B']['255'][0] for c in cs])
        tab[nome]['theta'] = media_ds([c['cache_B']['255'][1] for c in cs])
        # pagine di solo testo: media per seme sulle pagine usabili, e per pagina su tutti i semi
        if t[nome].get('speciali'):
            per_seme, per_pagina = [], defaultdict(lambda: [0, 0.0, 0])
            for c in cs:
                n = sum(x['n_corte'] for x in c['speciali'])
                if n:
                    per_seme.append(sum(x['somma_diff' + suf] for x in c['speciali']) / n)
                for x in c['speciali']:
                    pp = per_pagina[x['pagina']]
                    pp[0] += 1
                    pp[1] += x['somma_diff' + suf]
                    pp[2] += x['n_corte']
            tab[nome]['GR_speciali'] = media_ds(per_seme)
            tab[nome]['speciali_per_pagina'] = {p: dict(semi=x[0], n=x[2], GR=(x[1] / x[2] if x[2] else None))
                                                for p, x in per_pagina.items()}
    lingue_n = [n for n in tab if tab[n]['ruolo'] == 'lingua']
    confronti = OrderedDict()
    for k in ('k90', 'k90_interpolato', 'GL', 'GR', 'GR_corte', 'G255', 'bpc255', 'guadagno_totale'):
        valori = [tab[n][k]['media'] for n in lingue_n if tab[n].get(k)]
        confronti[k] = OrderedDict()
        for nome in tab:
            if tab[nome]['ruolo'] in ('voynich', 'generatore', 'controllo') and tab[nome].get(k):
                confronti[k][nome] = e95.posizione(tab[nome][k]['media'], valori)
    # lingua A contro lingua B del Voynich: sono testi diversi, quindi non appaiati (stesso numero di seme non vuol dire
    # stessi dati); differenza delle medie con errore standard sqrt(s_A^2/n_A + s_B^2/n_B)
    ab = OrderedDict()
    if 'Voynich A' in per and 'Voynich B' in per:
        for k in ('k90_interpolato', 'GL', 'GR_corte'):
            a_ = [misure_corsa(c, v)[k] for c in per['Voynich A']]
            b_ = [misure_corsa(c, v)[k] for c in per['Voynich B']]
            a_, b_ = [x for x in a_ if x is not None], [x for x in b_ if x is not None]
            if len(a_) > 1 and len(b_) > 1:
                ab[k] = dict(A_meno_B=statistics.mean(a_) - statistics.mean(b_),
                             errore_standard=math.sqrt(statistics.variance(a_) / len(a_) +
                                                       statistics.variance(b_) / len(b_)), n_A=len(a_), n_B=len(b_))
    # profilo (k90 interpolato, GL, GR_corte): ogni misura divisa per la sua deviazione standard fra le lingue
    profilo = ('k90_interpolato', 'GL', 'GR_corte')
    ds_l = {}
    for k in profilo:
        vs = [tab[n][k]['media'] for n in lingue_n if tab[n].get(k)]
        if len(vs) > 2:
            ds_l[k] = statistics.stdev(vs)
    vicini = OrderedDict()
    for x in ('Voynich', 'Voynich A', 'Voynich B'):
        if x not in tab or len(ds_l) < len(profilo) or not all(tab[x].get(k) for k in profilo):
            continue
        dist = []
        for n in tab:
            if tab[n]['ruolo'] == 'voynich' or not all(tab[n].get(k) for k in profilo):
                continue
            d = math.sqrt(sum(((tab[n][k]['media'] - tab[x][k]['media']) / ds_l[k]) ** 2 for k in profilo))
            dist.append((d, n))
        vicini[x] = [dict(testo=n, ruolo=tab[n]['ruolo'], distanza=d) for d, n in sorted(dist)]
    # generatori e controlli rispetto al Voynich intero: "vicino" se la differenza e' al massimo un decimo
    # dell'intervallo delle lingue (almeno SOGLIA_NEG_GL)
    rispetto = OrderedDict()
    if 'Voynich' in tab:
        for n in tab:
            if tab[n]['ruolo'] not in ('generatore', 'controllo'):
                continue
            rispetto[n] = OrderedDict()
            for k in profilo:
                vs = [tab[x][k]['media'] for x in lingue_n if tab[x].get(k)]
                if tab[n].get(k) and tab['Voynich'].get(k) and vs:
                    diff = tab[n][k]['media'] - tab['Voynich'][k]['media']
                    lim = 0.1 * (max(vs) - min(vs))
                    if k != 'k90_interpolato':
                        lim = max(lim, SOGLIA_NEG_GL)
                    rispetto[n][k] = dict(differenza=diff, vicino=abs(diff) <= lim)
    # letture con i criteri della preregistrazione
    letture = OrderedDict()
    for x in ('Voynich', 'Voynich A', 'Voynich B'):
        if x in tab:
            gl, gr = tab[x]['GL']['media'], tab[x]['GR_corte']['media']
            letture[x] = dict(GL_oltre_zero=gl > SOGLIA_NEG_GL, GR_azzerata=gr <= SOGLIA_NEG_GR,
                              k90_definito=tab[x]['k90'] is not None,
                              semi_con_k90_non_definito=tab[x]['seme_k90_non_definito'], semi=len(per[x]))
    for k, d in ab.items():
        letture.setdefault('A_contro_B', OrderedDict())[k] = dict(
            differiscono=abs(d['A_meno_B']) > 3 * d['errore_standard'] and
            (k == 'k90_interpolato' or abs(d['A_meno_B']) > SOGLIA_NEG_GL), A_meno_B=d['A_meno_B'])
    if 'Voynich' in tab and tab['Voynich'].get('GR_speciali'):
        sp, gr = tab['Voynich']['GR_speciali'], tab['Voynich']['GR_corte']
        dif = sp['media'] - gr['media']
        letture['pagine_di_solo_testo'] = dict(
            differenza=dif, piu_alta=dif > SOGLIA_NEG_GR and dif > 2 * max(sp['ds'], gr['ds']))
    return tab, confronti, dict(vicini=vicini, ds_lingue=ds_l, A_contro_B=ab, rispetto_al_voynich=rispetto,
                                letture=letture)


def controlli(tab, v='B'):
    """Controlli (soglie in cima al file, fissate dopo le prove del codice sui controlli).
    Negativo: C1 (catena di ordine 3). Negativi aggiuntivi: il latino e il Voynich con i segni rimescolati.
    Positivi: C3 (ogni riga riprende gli ultimi 3 segni della riga sopra: GR, entrambe le varianti);
    solo per la variante B: C2 (ogni riga ripetuta subito sotto: GR) e C4 (ogni riga ripetuta due righe piu' avanti,
    a circa 170 segni: GL). Per la variante A C2 e C4 sono sonde di portata: si riportano, non decidono."""
    out = OrderedDict()
    c1, c2, c3, c4 = C1_NOME, C2_NOME, C3_NOME, C4_NOME
    gr1 = tab[c1]['GR_corte']['media'] if c1 in tab else None
    gl1 = tab[c1]['GL']['media'] if c1 in tab else None
    pos = OrderedDict()
    if c3 in tab and c1 in tab:
        pos['C3_GR_meno_C1'] = tab[c3]['GR_corte']['media'] - gr1
        pos['C3_soglia'] = SOGLIA_POS_GR
    if v == 'B':
        if c2 in tab and c1 in tab:
            pos['C2_GR_meno_C1'] = tab[c2]['GR_corte']['media'] - gr1
            pos['C2_soglia'] = SOGLIA_POS_C2
        if c4 in tab and c1 in tab:
            pos['C4_GL_meno_C1'] = tab[c4]['GL']['media'] - gl1
            pos['C4_soglia'] = SOGLIA_POS_GL
    if pos:
        ok = all(pos[k.replace('_soglia', '') + '_' + ('GR' if k[1] in '23' else 'GL') + '_meno_C1'] >= pos[k]
                 for k in pos if k.endswith('_soglia'))
        out['positivo'] = dict(pos, superato=ok)
    if c1 in tab:
        k90 = tab[c1]['k90']
        gl, gr = tab[c1]['GL']['media'], tab[c1]['GR_corte']['media']
        out['negativo'] = dict(k90=k90['media'] if k90 else None, GL=gl, GR=gr, soglia_k90=SOGLIA_C1_K90,
                               soglia_GL=SOGLIA_NEG_GL, soglia_GR=SOGLIA_NEG_GR,
                               superato=(k90 is not None and k90['media'] <= SOGLIA_C1_K90) and gl <= SOGLIA_NEG_GL
                               and gr <= SOGLIA_NEG_GR)
    for nome in ('Latin, segni rimescolati', 'Voynich, segni rimescolati'):
        if nome in tab:
            gl, gr = tab[nome]['GL']['media'], tab[nome]['GR_corte']['media']
            out['negativo aggiuntivo: ' + nome] = dict(GL=gl, GR=gr, soglia_GL=SOGLIA_RIMESC_GL,
                                                       soglia_GR=SOGLIA_NEG_GR,
                                                       superato=gl <= SOGLIA_RIMESC_GL and gr <= SOGLIA_NEG_GR)
    if v == 'B':
        peggio = OrderedDict((n, x['max_peggioramento']['media']) for n, x in tab.items() if x.get('max_peggioramento'))
        if peggio:
            ctrl_n = [n for n, x in tab.items() if x['ruolo'] == 'controllo']
            out['verifica B non peggiore di A (max_k BPC_B(k) - BPC_A(k) sulla prova, media dei semi)'] = dict(
                massimo_controlli=max([peggio[n] for n in ctrl_n if n in peggio] or [0.0]),
                massimo_tutti=max(peggio.values()), soglia=SOGLIA_PEGGIORAMENTO,
                superato=max([peggio[n] for n in ctrl_n if n in peggio] or [0.0]) <= SOGLIA_PEGGIORAMENTO)
    if v == 'A':
        sonde = OrderedDict((n, dict(GR=tab[n]['GR_corte']['media'], GL=tab[n]['GL']['media'])) for n in (c2, c4) if n in tab)
        if sonde:
            out['sonda di portata (non decide)'] = sonde
    return out


def scrivi(t, corse, versioni):
    risultati = OrderedDict()
    for v in VARIANTI:
        tab, confronti, profili = analizza(t, corse, v)
        risultati[v] = OrderedDict(controlli=controlli(tab, v), testi=tab, confronti=confronti, profili=profili)
    ris = OrderedDict(
        esperimento='ia03',
        parametri=dict(N_ADD=N_ADD, N_VAL=N_VAL, N_PROVA=N_PROVA, PASSI=PASSI, OGNI=OGNI, PAZIENZA=PAZIENZA, SEMI=SEMI,
                       LUNG=LUNG, LOTTO=LOTTO, EMB=EMB, NASCOSTO=NASCOSTO, CADUTA=CADUTA, LR=LR,
                       DECADIMENTO=DECADIMENTO, TAGLIO=TAGLIO, KS=KS, ALFE=ALFE, TETE=TETE,
                       CONTESTO_RIGA=CONTESTO_RIGA, FINESTRA_VAL=FINESTRA_VAL, PASSO_VAL=PASSO_VAL,
                       SOGLIA_GUADAGNO=SOGLIA_GUADAGNO, SOGLIA_C1_K90=SOGLIA_C1_K90, SOGLIA_NEG_GL=SOGLIA_NEG_GL,
                       SOGLIA_RIMESC_GL=SOGLIA_RIMESC_GL, SOGLIA_NEG_GR=SOGLIA_NEG_GR, SOGLIA_POS_GR=SOGLIA_POS_GR,
                       SOGLIA_POS_C2=SOGLIA_POS_C2, SOGLIA_POS_GL=SOGLIA_POS_GL, SOGLIA_PEGGIORAMENTO=SOGLIA_PEGGIORAMENTO,
                       MAX_BERSAGLI_VAL=MAX_BERSAGLI_VAL, SOLO_CONTROLLI=SOLO_CONTROLLI,
                       PROVA_SPECIALI=os.environ.get('PROVA_SPECIALI', ''), TESTI=os.environ.get('TESTI', '')),
        versioni=versioni, sorgenti={k: x.get('sorgente') for k, x in t.items() if x.get('sorgente')},
        varianti=risultati)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')

    def f3(d, k='media'):
        return '–' if not d else '%.3f' % d[k]

    def f1(d, k='media'):
        return '–' if not d else '%.1f' % d[k]

    primo = risultati['B']['testi']
    r = ['# ia03 (IA3) — quanto contesto serve', '',
         'Modello a caratteri GRU (%d unità nascoste), finestre di %d segni da stato vuoto, %d finestre per passo, '
         '%d segni di addestramento, %d di validazione, %d di prova, al massimo %d passi, semi %s.' % (
             NASCOSTO, LUNG, LOTTO, N_ADD, N_VAL, N_PROVA, PASSI, ', '.join(map(str, SEMI))),
         'Variante B = GRU più cache neurale (le letture si fanno su questa); variante A = solo GRU (descrittiva). '
         'Stessi pesi, stesse corse.',
         'Corse arrivate al massimo dei passi: %d.' % sum(x['corse_al_limite'] for x in primo.values()),
         'Valori: media dei semi (deviazione standard fra i semi). BPC in bit per segno.']
    for v in VARIANTI:
        tab, confronti, profili, ctrl = (risultati[v][k] for k in ('testi', 'confronti', 'profili', 'controlli'))
        r += ['', '# Variante %s' % v, '', '## Controlli (%s)' % v, '']
        for k, d in ctrl.items():
            r.append('- %s: %s' % (k, ', '.join('%s %s' % (a, ('%.4f' % b) if isinstance(b, float) else b)
                                               for a, b in d.items())))
        r += ['', '## Misure per testo (%s)' % v, '',
              '| testo | ruolo | segni | riga (segni) | H1 | BPC(0) | BPC(32) | BPC(255) | k90 | semi k90 non def. | '
              'k90 interp. | GL | GR | GR corte | B peggio di A | alfa(255) | theta(255) | s/corsa |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for nome, x in tab.items():
            r.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s (%s) | %d | %s | %s (%s) | %s (%s) | %s | %s | %s | %s | '
                     '%.0f |' % (
                         nome, x['ruolo'], x['V'], f1(x['lunghezza_riga']), f3(x['h1']), f3(x['bpc0']), f3(x['bpc32']),
                         f3(x['bpc255']), f1(x['k90']), f1(x['k90'], 'ds'), x['seme_k90_non_definito'],
                         f1(x['k90_interpolato']), f3(x['GL']), f3(x['GL'], 'ds'), f3(x['GR']), f3(x['GR'], 'ds'),
                         f3(x['GR_corte']), f3(x.get('max_peggioramento')) if v == 'B' else '–',
                         f3(x['alfa']) if v == 'B' else '–', f3(x['theta']) if v == 'B' else '–', x['secondi']))
        r += ['', '## Curva BPC(k), media dei semi (%s)' % v, '',
              '| testo | ' + ' | '.join(str(k) for k in KS) + ' |', '|---|' + '---|' * len(KS)]
        for nome, x in tab.items():
            r.append('| %s | %s |' % (nome, ' | '.join('%.3f' % x['curva'][str(k)] for k in KS)))
        r += ['', '## Posizione rispetto alle lingue (%s)' % v, '']
        for k, d in confronti.items():
            for nome, p in d.items():
                if p:
                    r.append("- %s, %s: %.3f, %s l'intervallo delle lingue [%.3f, %.3f], lingue sotto: %.0f%%" % (
                        k, nome, tab[nome][k]['media'], p['dentro'], p['minimo'], p['massimo'],
                        100 * p['frazione_sotto']))
        r += ['', '## Voynich lingua A meno lingua B (differenza di medie) (%s)' % v, '']
        for k, d in profili['A_contro_B'].items():
            r.append('- %s: %+.3f (errore standard %.3f, non appaiato, %d e %d semi)' % (
                k, d['A_meno_B'], d['errore_standard'], d['n_A'], d['n_B']))
        r += ['', '## Pagine di solo testo (GR sui bersagli corti, bit per segno) (%s)' % v, '']
        for nome, x in tab.items():
            if x.get('GR_speciali'):
                r.append('- %s: GR sulle pagine usabili %s (ds %s, %d semi); GR sulla prova %s' % (
                    nome, f3(x['GR_speciali']), f3(x['GR_speciali'], 'ds'), x['GR_speciali']['n'], f3(x['GR_corte'])))
                for p, y in x['speciali_per_pagina'].items():
                    r.append('  - %s: %d semi, %d segni, GR %s' % (p, y['semi'], y['n'],
                                                                  '–' if y['GR'] is None else '%.3f' % y['GR']))
        r += ['', '## Testi più vicini al Voynich sul profilo (k90 interpolato, GL, GR corte) (%s)' % v, '',
              'Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea.', '']
        for x, lista in profili['vicini'].items():
            r.append('- %s: %s' % (x, '; '.join('%s (%s) %.2f' % (y['testo'], y['ruolo'], y['distanza'])
                                                for y in lista[:6])))
        r += ['', '## Generatori e controlli rispetto al Voynich (%s)' % v, '',
              '"vicino": differenza al massimo un decimo dell\'intervallo delle lingue (almeno %.2f per GL e GR).' %
              SOGLIA_NEG_GL, '']
        for n, d in profili['rispetto_al_voynich'].items():
            r.append('- %s: %s' % (n, ', '.join('%s %+.3f%s' % (k, y['differenza'], ' (vicino)' if y['vicino'] else '')
                                                for k, y in d.items())))
        r += ['', '## Letture (criteri della preregistrazione) (%s)' % v, '']
        for k, d in profili['letture'].items():
            r.append('- %s: %s' % (k, d))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris


def main():
    import torch
    import numpy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    prova = [k for k in ('PASSI', 'OGNI', 'PAZIENZA', 'SEMI', 'LUNG', 'LOTTO', 'NASCOSTO', 'CADUTA', 'TESTI', 'USCITA',
                         'SOLO_CONTROLLI', 'PROVA_SPECIALI') if k in os.environ]
    print("variabili d'ambiente di prova attive: %s" % (', '.join(prova) if prova else 'nessuna'), flush=True)
    t = catalogo()
    print('testi: %d' % len(t), flush=True)
    for nome, v in t.items():
        print('  %-70s %-13s blocchi %4d segni %7d' % (nome, v['ruolo'], len(v['blocchi']),
                                                     e95.lunghezza(v['blocchi'])), flush=True)
    lavori, scarti = prepara(t)
    if scarti:
        print('esclusi: %s' % '; '.join('%s (%s)' % kv for kv in scarti.items()), flush=True)
    percorso = os.path.join(USCITA, 'ia03_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    else:
        open(percorso, 'w').close()
    fatte = {(c['testo'], c['seme']) for c in corse}
    da_fare = [l for l in lavori if (l['testo'], l['seme']) not in fatte]
    print('corse: %d da fare, %d già fatte' % (len(da_fare), len(fatte)), flush=True)
    processi = int(os.environ.get('PROCESSI', 8))
    inizio = time.time()
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        for i, c in enumerate(pool.imap_unordered(corsa, da_fare), 1):
            corse.append(c)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
            a, b = misure_corsa(c, 'A'), misure_corsa(c, 'B')
            print('[%d/%d %.0f min] %s seme %d: A BPC(255) %.3f k90 %s GL %.3f GRc %s | B (alfa %.2f theta %.1f al k 255, max peggio %.3f) '
                  'BPC(255) %.3f k90 %s GL %.3f GRc %s (%d passi, %.0f s)' % (
                      i, len(da_fare), (time.time() - inizio) / 60, c['testo'], c['seme'], a['bpc255'], a['k90'],
                      a['GL'], '–' if a['GR_corte'] is None else '%.3f' % a['GR_corte'], c['cache_B']['255'][0],
                      c['cache_B']['255'][1], c['max_peggioramento_B'], b['bpc255'], b['k90'], b['GL'],
                      '–' if b['GR_corte'] is None else '%.3f' % b['GR_corte'], c['passi'], c['secondi']),
                  flush=True)
    ris = scrivi(t, [c for c in corse if c['testo'] in t], versioni)
    # le due righe principali sono quelle della variante B; la A segue con il suffisso
    for v in VARIANTI:
        for k, d in ris['varianti'][v]['controlli'].items():
            print('controllo %s%s: %s' % (k, '' if v == 'B' else ' (variante A)', d), flush=True)


if __name__ == '__main__':
    main()
