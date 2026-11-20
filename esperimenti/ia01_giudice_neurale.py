# -*- coding: utf-8 -*-
"""Esperimento IA1 (ia01): un giudice fatto con reti neurali separa le pagine del voynichizzatore v21 da quelle vere
meglio dei due giudici del paper v2 (AUC 0,554 e 0,601)? E separa i libri v21 con messaggio da quelli senza (paper 0,506)?

Pagine: ogni pagina e' la sequenza dei segni (glifi EVA fusi come in e3c95; spazio, a capo e un segno di inizio
paragrafo '¶' all'inizio delle righe che aprono un paragrafo). Pagine con almeno 40 parole nel Voynich (come e231).
Si usano le pagine vere (Voynich ZL, testo corrente) e le pagine gemelle dei libri v21 (stessa impaginazione).

Due giudici, entrambi con 5 pieghe per pagina (la pagina vera e la sua gemella stanno nella stessa piega):
- A "sorpresa": per ogni piega un GRU a caratteri come in e3c95 (1 strato, 32 + 128, caduta 0,3) addestrato come modello
  del testo sulle pagine vere delle altre pieghe (10% delle pagine per l'arresto anticipato). Di ogni pagina della piega
  fuori (vera o generata) si misura il profilo di sorpresa (bit per segno: media, deviazione, 95o percentile, a inizio
  parola, a inizio riga, dentro la parola, sullo spazio, sull'a capo, righe di paragrafo e altre, quarti della pagina).
  Regressione logistica sui profili (come e231: standardizzazione, C=1, 10 pieghe per pagina, 5 ripetizioni) -> AUC.
  I modelli del testo non dipendono dal libro: si addestrano una volta per piega e seme e servono a tutti i libri.
- B "lettore": GRU (32 + 64) che legge finestre di 256 segni di una pagina; media degli stati e ultimo stato -> uscita;
  addestrato a dire vera / generata, un lettore per libro e per piega, arresto anticipato su 15% delle pagine di
  addestramento. Punteggio della pagina: media dei punteggi delle finestre (passo 128). AUC sulle pagine delle 5 pieghe.
- B_unico: un solo lettore addestrato su tutti i libri insieme (pagine delle pieghe di addestramento), provato su tutti.

Libri: chiavi 13-22 (default; 13-24 non usate per la messa a punto). Messaggio: chiavi 13-24, libro con messaggio (caso a
di e409/e419) contro libro senza (caso b), pieghe per chiave (4 pieghe di 3 chiavi); controllo negativo: chiavi dispari
contro pari fra i libri senza; scala di sensibilita': libro senza messaggio contro lo stesso con una frazione (3%, 10%, 30%, 100%)
delle parole sostituite da parole di altre posizioni del libro.
Controlli: positivi = Voynich con le parole rimescolate nella riga, generatore e192; riferimento = righe rimescolate nella
pagina; negativo = pagine vere con etichette a caso (5 etichette diverse).

Preregistrazione: preregistrazioni/ia01.md. Scrive risultati/ia01_giudice_neurale.json e .md e, una riga per lavoro,
risultati/ia01_corse.jsonl (con RIPRENDI=1 i lavori gia' fatti non si rifanno). I libri generati stanno in
dati/cache/ia01_libri (LIBRI).

SOLO_CONTROLLI=1: prova del codice su testo latino messo in pagine (pagine vere = Plinio; libro = catena di Markov di
caratteri di ordine 2 che copia le righe; nessun accesso al Voynich ne' ai suoi generatori). Altre variabili per le prove:
PAGINE, CHIAVI, CHIAVI_MSG, SEMI, SEMI_B, PASSI, PASSI_B, PAZIENZA, LUNG_B, FRAZIONI, NEG, USCITA, LIBRI, FILTRO (sottostringhe
separate da | che il nome del lavoro deve contenere), PROCESSI (non cambia i risultati).
"""
import json, math, os, pickle, random, statistics, sys, time, zlib
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)

NOME = 'ia01_giudice_neurale'
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
LIBRI = os.environ.get('LIBRI', os.path.join(USCITA, 'libri_prova') if SOLO_CONTROLLI else
                       os.path.join(QUI, '..', 'dati', 'cache', 'ia01_libri'))
TESTO_ISIDORO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')


def lista(nome, default):
    return tuple(int(x) for x in os.environ.get(nome, default).split(',') if x)


MIN_PAROLE = 40
NF = 5                                            # pieghe per pagina
CHIAVI = lista('CHIAVI', ','.join(str(i) for i in range(13, 23)))
CHIAVI_MSG = lista('CHIAVI_MSG', ','.join(str(i) for i in range(13, 25)))
FRAZIONI = tuple(float(x) for x in os.environ.get('FRAZIONI', '0.03,0.10,0.30,1.00').split(','))
NEG = int(os.environ.get('NEG', 5))               # etichette a caso diverse per il controllo negativo
SEMI = lista('SEMI', '1,2')                       # semi dei modelli del testo (giudice A)
SEMI_B = lista('SEMI_B', '1')                     # semi dei lettori (giudice B)
# giudice A: come e3c95
EMB, NASCOSTO, CADUTA = 32, int(os.environ.get('NASCOSTO', 128)), float(os.environ.get('CADUTA', 0.3))
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
LUNG, LOTTO = 64, 32
PASSI = int(os.environ.get('PASSI', 4000))
OGNI = int(os.environ.get('OGNI', 20))
PAZIENZA = int(os.environ.get('PAZIENZA', 10))
# giudice B
EMB_B, NASC_B, CADUTA_B = 32, int(os.environ.get('NASC_B', 64)), 0.3
LUNG_B = int(os.environ.get('LUNG_B', 256))
LOTTO_B = 32
PASSI_B = int(os.environ.get('PASSI_B', 1500))
PAZIENZA_B = int(os.environ.get('PAZIENZA_B', 10))
MAX_FINESTRE_VAL = 800
# soglie, fissate nella preregistrazione prima di eseguire
SOGLIA_POSITIVO = 0.85
BANDA = (0.45, 0.55)
LETTURA_BASSA, LETTURA_ALTA = 0.62, 0.65
POTENZA = 0.60                                    # AUC della scala alla frazione POT_FR
POT_FR = 0.30 if 0.30 in FRAZIONI else FRAZIONI[-1]
PAPER = dict(giudice1=0.554, giudice2=0.601, messaggio=0.506)

SP, NL, PAR, RARO = ' ', '\n', '¶', '¤'   # id 0, 1, 2, 3 (i segni veri hanno id >= 4)
CARATTERISTICHE = ['bit_medi', 'bit_sd', 'bit_p95', 'inizio_parola', 'inizio_riga', 'dentro_parola', 'spazio',
                   'fine_riga', 'riga_paragrafo', 'riga_altra', 'quarto1', 'quarto2', 'quarto3', 'quarto4']


# ---------------------------------------------------------------- pagine
# Una pagina e' una lista di righe (inizio_paragrafo, [parola, ...]); una parola e' una tupla di segni.

def pagine_da_righe(rr, dividi, pulita=None):
    out = OrderedDict()
    for p, ini, ps in rr:
        if pulita:
            ps = [w for w in ps if pulita(w)]
        if ps:
            out.setdefault(p, []).append((bool(ini), [tuple(dividi(w)) for w in ps]))
    return out


def carica_voynich():
    sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
    import misure, pezzi
    rr, tipo = pezzi.voynich()
    return pagine_da_righe(rr, misure.divisore(misure.GLIFI_EVA)), tipo


def carica_latino():
    """Prova del codice: Plinio messo in pagine di RIGHE_PAGINA righe; un paragrafo ogni 8 righe."""
    import e3c95_imparabilita as e95
    tt, per = e95.lingue()
    chiave = per['Latin'][('Historical', 'Technical')][0][1]
    righe = [r for r in tt[chiave] if r]
    np_, rp = int(os.environ.get('PAGINE', 196)), int(os.environ.get('RIGHE_PAGINA', 23))
    vere, tipo = OrderedDict(), OrderedDict()
    for i in range(np_):
        rows = righe[i * rp:(i + 1) * rp]
        nome = 'L%03d' % i
        vere[nome] = [(j % 8 == 0, [tuple(w) for w in r]) for j, r in enumerate(rows)]
        tipo[nome] = ('S%d' % (i * 4 // np_), 'L')
    return vere, tipo


_CTX = {}


def contesto():
    """Pagine vere, vocabolario, pieghe: uguali in ogni processo (nessun caso)."""
    if _CTX:
        return _CTX
    vere, tipo = carica_latino() if SOLO_CONTROLLI else carica_voynich()
    nomi = sorted(p for p, rows in vere.items() if sum(len(ws) for _, ws in rows) >= MIN_PAROLE)
    vere = OrderedDict((p, vere[p]) for p in nomi)
    conti = Counter(s for rows in vere.values() for _, ws in rows for w in ws for s in w)
    tot = sum(conti.values())
    voc = [SP, NL, PAR, RARO] + sorted(s for s, c in conti.items() if c / tot >= 0.001)
    idx = {s: i for i, s in enumerate(voc)}
    ordine = list(nomi)
    random.Random(3961).shuffle(ordine)
    fold = {p: i % NF for i, p in enumerate(ordine)}
    chiavi = sorted(set(CHIAVI) | set(CHIAVI_MSG))
    # pieghe per chiave: dispari e pari mescolati a parte e distribuiti a giro, cosi' ogni piega ha chiavi di tutte e due le
    # parita' (serve al controllo negativo dispari contro pari)
    dis = [k for k in sorted(CHIAVI_MSG) if k % 2]
    par = [k for k in sorted(CHIAVI_MSG) if not k % 2]
    random.Random(3962).shuffle(dis)
    random.Random(3963).shuffle(par)
    nfm = max(1, min(4, len(CHIAVI_MSG) // 2))
    fold_chiave = {k: i % nfm for i, k in enumerate(dis + par)}
    _CTX.update(vere=vere, tipo=tipo, voc=voc, idx=idx, V=len(voc), fold=fold, fold_chiave=fold_chiave, nfm=nfm,
                ids={p: codifica(rows, idx) for p, rows in vere.items()}, chiavi=chiavi)
    return _CTX


def codifica(rows, idx):
    out = []
    for ini, ws in rows:
        if ini:
            out.append(2)
        for j, w in enumerate(ws):
            if j:
                out.append(0)
            out.extend(idx.get(s, 3) for s in w)
        out.append(1)
    return np.array(out, dtype=np.int64)


# ---------------------------------------------------------------- libri e controlli

def markov(vere, ordine, seme):
    """Prova del codice: per ogni riga vera una riga con lo stesso numero di parole, scritta da una catena di Markov di
    caratteri di ordine `ordine` addestrata sul testo vero."""
    rnd = random.Random(seme)
    cont = defaultdict(Counter)
    for rows in vere.values():
        for _, ws in rows:
            seq = [NL] * ordine
            for w in ws:
                for s in list(w) + [SP]:
                    for k in range(0, ordine + 1):          # con tutte le lunghezze di contesto, per il ripiego
                        cont[tuple(seq[len(seq) - k:]) if k else ()][s] += 1
                    seq.append(s)
    out = OrderedDict()
    for p, rows in vere.items():
        nuove = []
        for ini, ws in rows:
            seq, parole, cur = [NL] * ordine, [], []
            while len(parole) < len(ws):
                s = None
                for k in range(ordine, -1, -1):
                    c = cont.get(tuple(seq[len(seq) - k:]) if k else ())
                    if c:
                        ch = list(c.items())
                        s = rnd.choices([a for a, _ in ch], [b for _, b in ch])[0]
                        if s == SP and not cur:
                            s = None
                            continue
                        break
                if s is None or len(cur) > 25:
                    s = SP if cur else 'e'
                seq.append(s)
                if s == SP:
                    parole.append(tuple(cur))
                    cur = []
                else:
                    cur.append(s)
            nuove.append((ini, parole))
        out[p] = nuove
    return out


def rimescola_parole(vere, seme):
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in vere.items():
        nr = []
        for ini, ws in rows:
            ws = list(ws)
            rnd.shuffle(ws)
            nr.append((ini, ws))
        out[p] = nr
    return out


def rimescola_righe(vere, seme):
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in vere.items():
        rows = list(rows)
        rnd.shuffle(rows)
        out[p] = rows
    return out


def sostituisci_parole(libro, frazione, seme):
    """Una frazione delle parole del libro e' sostituita da una parola presa a caso fra tutte quelle del libro."""
    rnd = random.Random(seme)
    tutte = [w for rows in libro.values() for _, ws in rows for w in ws]
    out = OrderedDict()
    for p, rows in libro.items():
        out[p] = [(ini, [tutte[rnd.randrange(len(tutte))] if rnd.random() < frazione else w for w in ws])
                  for ini, ws in rows]
    return out


def seme_di(nome):
    return zlib.crc32(nome.encode('utf-8')) % (1 << 31)


def percorso_libro(nome):
    return os.path.join(LIBRI, nome.replace(':', '_') + '.pkl')


def genera_libro(nome):
    """Libri generati: 'a13' (con messaggio), 'b13' (senza), 'e192'. Salvati in LIBRI."""
    p = percorso_libro(nome)
    if os.path.exists(p):
        return 'gia\' fatto'
    os.makedirs(LIBRI, exist_ok=True)
    c = contesto()
    if SOLO_CONTROLLI:
        if nome == 'e192':
            return 'non previsto nella prova'
        libro = markov(c['vere'], 2, seme_di(nome))
    else:
        sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
        import misure, trascrizione
        dividi = misure.divisore(misure.GLIFI_EVA)
        if nome == 'e192':
            rr = righe_e192()
        else:
            import canale_sacco
            testo = open(TESTO_ISIDORO, encoding='utf-8').read().replace('\r\n', '\n') if nome[0] == 'a' else None
            rr, _ = canale_sacco.codifica(testo, 'e409-%d' % int(nome[1:]), 'v21', verifica=False)
        libro = pagine_da_righe(rr, dividi, trascrizione.pulita)
    with open(p + '.tmp', 'wb') as f:
        pickle.dump(libro, f)
    os.replace(p + '.tmp', p)
    return 'fatto'


def righe_e192():
    """Il generatore vecchio e192, seme 1, come in e231.generatore_e192 ma tenendo l'inizio di paragrafo."""
    import generatori, trascrizione
    import e131_procedimento_riga as e131
    import e145_abitudini as e145
    import e152_righe_in_ordine as e152
    import e153_righe_rifinite as e153
    import e162_messaggio_nei_temi as e162
    import e192_generatore_misto as e192
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    return [(pag, ini, [w for w in ps if trascrizione.pulita(w)])
            for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), 1, None)]


_LIB = {}


def libro(nome):
    """Il libro (pagina -> righe) di un nome: a13, b13, p0.03:b13, ctrl:parole, ctrl:righe, ctrl:e192, ctrl:ordine1."""
    if nome in _LIB:
        return _LIB[nome]
    c = contesto()
    if nome == 'vere':
        r = c['vere']
    elif nome == 'ctrl:parole':
        r = rimescola_parole(c['vere'], 396001)
    elif nome == 'ctrl:righe':
        r = rimescola_righe(c['vere'], 396002)
    elif nome == 'ctrl:ordine1':
        r = markov(c['vere'], 1, 396003)
    elif nome == 'ctrl:e192':
        r = pickle.load(open(percorso_libro('e192'), 'rb'))
    elif nome.startswith('p'):
        f, base = nome[1:].split(':')
        r = sostituisci_parole(libro(base), float(f), seme_di(nome))
    else:
        r = pickle.load(open(percorso_libro(nome), 'rb'))
    if len(_LIB) > 6:
        _LIB.clear()
    _LIB[nome] = r
    return r


def ids_libro(nome):
    c = contesto()
    if nome == 'vere':
        return c['ids']
    return {p: codifica(rows, c['idx']) for p, rows in libro(nome).items() if p in c['ids']}


def controlli_disponibili():
    if SOLO_CONTROLLI:
        return ['ctrl:ordine1', 'ctrl:parole', 'ctrl:righe']
    out = ['ctrl:parole', 'ctrl:righe']
    if os.path.exists(percorso_libro('e192')):
        out.insert(1, 'ctrl:e192')
    return out


# ---------------------------------------------------------------- insiemi di campioni per il giudice B

def campioni(nome):
    """Campioni di un insieme: dict(id, y, fold, unita, ids). 'unita' e' l'unita' dell'arresto anticipato (pagina o chiave),
    'fold' la piega esterna."""
    c = contesto()
    fp = c['fold']
    out = []

    def aggiungi(lib_ids, y, etichetta, per_chiave=None):
        for p, a in lib_ids.items():
            if per_chiave is None:
                out.append(dict(id=[p, etichetta], y=y, fold=fp[p], unita=p, ids=a))
            else:
                out.append(dict(id=[p, etichetta], y=y, fold=c['fold_chiave'][per_chiave], unita=per_chiave, ids=a))

    if nome.startswith('libro:') or nome.startswith('ctrl:'):
        g = ids_libro(nome[6:] if nome.startswith('libro:') else nome)
        comuni = [p for p in c['ids'] if p in g]
        aggiungi({p: c['ids'][p] for p in comuni}, 0, 'vera')
        aggiungi({p: g[p] for p in comuni}, 1, 'generata')
    elif nome.startswith('neg:'):
        s = int(nome[4:])
        pag = list(c['ids'])
        random.Random(3970 + s).shuffle(pag)
        for i, p in enumerate(pag):
            out.append(dict(id=[p, 'neg'], y=int(i >= len(pag) // 2), fold=fp[p], unita=p, ids=c['ids'][p]))
    elif nome == 'unico':
        aggiungi(c['ids'], 0, 'vera')
        for k in CHIAVI:
            g = ids_libro('a%d' % k)
            for p, a in g.items():
                out.append(dict(id=[p, 'a%d' % k], y=1, fold=fp[p], unita=p, ids=a))
    elif nome.startswith('msg:'):
        for k in CHIAVI_MSG:
            b = ids_libro('b%d' % k)
            if nome == 'msg:ab':
                aggiungi(ids_libro('a%d' % k), 1, 'a%d' % k, k)
                aggiungi(b, 0, 'b%d' % k, k)
            elif nome == 'msg:neg':
                aggiungi(b, k % 2, 'b%d' % k, k)
            else:
                f = nome[4:]                                   # 'f0.03'
                aggiungi(b, 0, 'b%d' % k, k)
                aggiungi(ids_libro('p%s:b%d' % (f[1:], k)), 1, 'p%d' % k, k)
    else:
        raise ValueError(nome)
    return out


def pieghe_di(nome):
    return contesto()['nfm'] if nome.startswith('msg:') else NF


# ---------------------------------------------------------------- reti

_MOD = {}


def moduli():
    if _MOD:
        return _MOD
    import torch.nn as nn

    class LM(nn.Module):
        def __init__(self, V):
            super().__init__()
            self.emb = nn.Embedding(V, EMB)
            self.gru = nn.GRU(EMB, NASCOSTO, batch_first=True)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(NASCOSTO, V)

        def forward(self, x):
            y, _ = self.gru(self.emb(x))
            return self.out(self.caduta(y))

    class Lettore(nn.Module):
        def __init__(self, V):
            super().__init__()
            self.V = V
            self.emb = nn.Embedding(V + 1, EMB_B, padding_idx=V)
            self.gru = nn.GRU(EMB_B, NASC_B, batch_first=True)
            self.caduta = nn.Dropout(CADUTA_B)
            self.out = nn.Linear(2 * NASC_B, 1)

        def forward(self, x, lung):
            import torch
            h, _ = self.gru(self.emb(x))
            maschera = (torch.arange(x.shape[1])[None, :] < lung[:, None]).float()[:, :, None]
            media = (h * maschera).sum(1) / lung[:, None].float()
            ultimo = h[torch.arange(x.shape[0]), lung - 1]
            return self.out(self.caduta(torch.cat([media, ultimo], 1)))[:, 0]

    _MOD.update(LM=LM, Lettore=Lettore)
    return _MOD


def avvia_processo():
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def addestra_lm(add, val, V, seme):
    """Il modello del testo: come in e3c95 (finestre di 64, lotti di 32, AdamW), con arresto anticipato sulla validazione;
    si tiene il modello del punto migliore."""
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    inizio = time.time()
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = moduli()['LM'](V)
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    add_t, val_t = torch.tensor(add, dtype=torch.long), torch.tensor(val, dtype=torch.long)
    finestra = torch.arange(LUNG + 1)

    def valuta():
        m.eval()
        with torch.no_grad():
            bpc = F.cross_entropy(m(val_t[None, :-1])[0], val_t[1:]).item() / math.log(2)
        m.train()
        return bpc

    curva, migliore, stato = [], None, None
    for passo in range(1, PASSI + 1):
        partenze = torch.from_numpy(rng.integers(0, len(add_t) - LUNG - 1, size=LOTTO))
        xb = add_t[partenze[:, None] + finestra]
        loss = F.cross_entropy(m(xb[:, :-1]).reshape(-1, V), xb[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        if passo % OGNI == 0:
            curva.append(round(valuta(), 5))
            if migliore is None or curva[-1] < migliore:
                migliore, stato = curva[-1], {k: v.clone() for k, v in m.state_dict().items()}
            if len(curva) - 1 - curva.index(min(curva)) >= PAZIENZA:
                break
    m.load_state_dict(stato)
    m.eval()
    return m, dict(passi=passo, bpc_validazione=migliore, secondi=round(time.time() - inizio, 1),
                   segni_addestramento=len(add), segni_validazione=len(val))


def sorprese(m, liste, blocco=16):
    """Sorpresa (bit) di ogni segno di ogni pagina, dal modello del testo; la pagina parte da un a capo."""
    import torch
    import torch.nn.functional as F
    out = [None] * len(liste)
    ordine = sorted(range(len(liste)), key=lambda i: len(liste[i]))
    with torch.no_grad():
        for i in range(0, len(ordine), blocco):
            gruppo = ordine[i:i + blocco]
            L = max(len(liste[j]) for j in gruppo)
            x = np.zeros((len(gruppo), L), dtype=np.int64)
            y = np.zeros((len(gruppo), L), dtype=np.int64)
            for r, j in enumerate(gruppo):
                a = liste[j]
                x[r, 0] = 1
                x[r, 1:len(a)] = a[:-1]
                y[r, :len(a)] = a
            lp = F.log_softmax(m(torch.from_numpy(x)), dim=-1)
            s = (-lp.gather(2, torch.from_numpy(y)[:, :, None])[:, :, 0] / math.log(2)).numpy()
            for r, j in enumerate(gruppo):
                out[j] = s[r, :len(liste[j])]
    return out


def profilo(a, s):
    """Profilo di sorpresa di una pagina (vedi CARATTERISTICHE); i segni '¶' non contano."""
    T = len(a)
    prec = np.concatenate([[1], a[:-1]])
    valido = a != 2
    glifo = a >= 3
    ini_riga = glifo & ((prec == 1) | (prec == 2))
    ini_par = glifo & (prec == 0)
    dentro = glifo & ~ini_riga & ~ini_par
    nl = (a == 1)
    riga = np.cumsum(nl) - nl
    prima = np.where((np.arange(T) == 0) | (prec == 1))[0]
    riga_par = np.array([a[i] == 2 for i in prima])[np.minimum(riga, len(prima) - 1)]
    quarto = (np.arange(T) * 4) // T
    tutto = float(s[valido].mean())

    def media(maschera):
        mk = maschera & valido
        return float(s[mk].mean()) if mk.any() else tutto
    return [round(x, 4) for x in (tutto, float(s[valido].std()), float(np.percentile(s[valido], 95)), media(ini_par),
                                  media(ini_riga), media(dentro), media(a == 0), media(nl), media(riga_par),
                                  media(~riga_par), media(quarto == 0), media(quarto == 1), media(quarto == 2),
                                  media(quarto == 3))]


def libri_per_A():
    nomi = ['a%d' % k for k in sorted(set(CHIAVI) | set(CHIAVI_MSG))] + ['b%d' % k for k in CHIAVI_MSG]
    nomi += ['p%s:b%d' % (f, k) for f in FRAZIONI for k in CHIAVI_MSG]
    return nomi + controlli_disponibili()


def lavoro_A(seme, piega):
    c = contesto()
    pagine = list(c['ids'])
    test = [p for p in pagine if c['fold'][p] == piega]
    resto = [p for p in pagine if c['fold'][p] != piega]
    random.Random(3964 + 100 * seme + piega).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([c['ids'][p] for p in ps])
    m, info = addestra_lm(flusso(add), flusso(val), c['V'], 1000 * seme + piega)
    prof = OrderedDict()
    for nome in ['vere'] + libri_per_A():
        g = ids_libro(nome)
        ps = [p for p in test if p in g]
        s = sorprese(m, [g[p] for p in ps])
        prof[nome] = OrderedDict((p, profilo(g[p], x)) for p, x in zip(ps, s))
    info['bpc_vere_fuori'] = float(np.mean([np.mean(x) for x in sorprese(m, [c['ids'][p] for p in test])]))
    return dict(profili=prof, info=info)


def finestre(n, W=None, passo=None):
    W = W or LUNG_B
    passo = passo or W // 2
    if n <= W:
        return [(0, n)]
    st = list(range(0, n - W + 1, passo))
    if st[-1] != n - W:
        st.append(n - W)
    return [(a, a + W) for a in st]


def impacchetta(liste, pad):
    import torch
    L = max(len(a) for a in liste)
    x = np.full((len(liste), L), pad, dtype=np.int64)
    for i, a in enumerate(liste):
        x[i, :len(a)] = a
    return torch.from_numpy(x), torch.tensor([len(a) for a in liste], dtype=torch.long)


def logit_finestre(m, lista_finestre, pad):
    import torch
    out = []
    m.eval()
    with torch.no_grad():
        for i in range(0, len(lista_finestre), 256):
            x, l = impacchetta(lista_finestre[i:i + 256], pad)
            out.extend(m(x, l).tolist())
    return out


def addestra_B(train, val, V, seme):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    inizio = time.time()
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = moduli()['Lettore'](V)
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    per_classe = [[s for s in train if s['y'] == k] for k in (0, 1)]
    assert per_classe[0] and per_classe[1], 'una classe senza campioni'
    vf = [(s['ids'][a:b], s['y']) for s in val for a, b in finestre(len(s['ids']))]
    if len(vf) > MAX_FINESTRE_VAL:
        sel = np.random.default_rng(seme + 777).choice(len(vf), MAX_FINESTRE_VAL, replace=False)
        vf = [vf[i] for i in sorted(sel)]
    yv = torch.tensor([y for _, y in vf], dtype=torch.float)

    def perdita_val():
        z = torch.tensor(logit_finestre(m, [w for w, _ in vf], V))
        m.train()
        return F.binary_cross_entropy_with_logits(z, yv).item()

    curva, migliore, stato = [], None, None
    m.train()
    for passo in range(1, PASSI_B + 1):
        ws, ys = [], rng.integers(0, 2, LOTTO_B)
        for y in ys:
            cl = per_classe[y]
            a = cl[rng.integers(len(cl))]['ids']
            if len(a) > LUNG_B:
                i = rng.integers(0, len(a) - LUNG_B + 1)
                a = a[i:i + LUNG_B]
            ws.append(a)
        x, l = impacchetta(ws, V)
        loss = F.binary_cross_entropy_with_logits(m(x, l), torch.tensor(ys, dtype=torch.float))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        if passo % OGNI == 0:
            curva.append(round(perdita_val(), 5))
            if migliore is None or curva[-1] < migliore:
                migliore, stato = curva[-1], {k: v.clone() for k, v in m.state_dict().items()}
            if len(curva) - 1 - curva.index(min(curva)) >= PAZIENZA_B:
                break
    m.load_state_dict(stato)
    return m, dict(passi=passo, perdita_validazione=migliore, secondi=round(time.time() - inizio, 1),
                   campioni_addestramento=len(train))


def punteggi(m, test, V):
    win, chi = [], []
    for i, s in enumerate(test):
        for a, b in finestre(len(s['ids'])):
            win.append(s['ids'][a:b])
            chi.append(i)
    z = np.array(logit_finestre(m, win, V))
    chi = np.array(chi)
    return [float(z[chi == i].mean()) for i in range(len(test))]


def lavoro_B(nome, piega, seme):
    c = contesto()
    tutti = campioni(nome)
    test = [s for s in tutti if s['fold'] == piega]
    resto = [s for s in tutti if s['fold'] != piega]
    unita = sorted({s['unita'] for s in resto}, key=str)
    rnd = random.Random(3965 + 1000 * seme + 10 * piega + zlib.crc32(nome.encode()) % 997)
    nval = 1 if nome.startswith('msg:') else max(1, round(0.15 * len(unita)))
    for _ in range(50):            # l'addestramento deve restare con tutte e due le classi
        if nome == 'msg:neg':      # etichetta = parita' della chiave: la validazione ha una chiave dispari e una pari
            uval = {rnd.choice([u for u in unita if u % 2]), rnd.choice([u for u in unita if not u % 2])}
        else:
            uval = set(rnd.sample(unita, nval))
        val = [s for s in resto if s['unita'] in uval]
        add = [s for s in resto if s['unita'] not in uval]
        if len({s['y'] for s in add}) == 2 and len({s['y'] for s in val}) == 2:
            break
    m, info = addestra_B(add, val, c['V'], (seme * 100 + piega + zlib.crc32(nome.encode('utf-8'))) % (1 << 31))
    z = punteggi(m, test, c['V'])
    info['classi_validazione'] = [sum(s['y'] == 0 for s in val), sum(s['y'] == 1 for s in val)]
    info['test'] = [[s['id'], s['y'], round(x, 5)] for s, x in zip(test, z)]
    return info


def lavoro(job):
    inizio = time.time()
    if job[0] == 'G':
        try:
            r = dict(esito=genera_libro(job[1]))
        except Exception as e:       # il generatore vecchio e192 e' un controllo facoltativo
            r = dict(esito='errore: %r' % (e,))
            if job[1] != 'e192':
                print('ERRORE nella generazione del libro %s: %r' % (job[1], e), flush=True)
    elif job[0] == 'A':
        r = lavoro_A(job[1], job[2])
    else:
        r = lavoro_B(job[1], job[2], job[3])
    r.update(job=list(job), tipo=job[0], tempo=round(time.time() - inizio, 1))
    return r


def lavori_generazione():
    nomi = ['a%d' % k for k in sorted(set(CHIAVI) | set(CHIAVI_MSG))] + ['b%d' % k for k in CHIAVI_MSG]
    if not SOLO_CONTROLLI:
        nomi.append('e192')
    return [('G', n) for n in nomi]


def nomi_B():
    n = ['libro:a%d' % k for k in CHIAVI] + [x for x in controlli_disponibili()] + ['neg:%d' % s for s in range(1, NEG + 1)]
    return n + ['unico', 'msg:ab', 'msg:neg'] + ['msg:f%s' % f for f in FRAZIONI]


def lavori_addestramento():
    L = []
    for n in nomi_B():
        if n.startswith('msg:') or n == 'unico':
            L += [('B', n, f, s) for f in range(pieghe_di(n)) for s in SEMI_B]
    L += [('A', s, f) for s in SEMI for f in range(NF)]
    for n in nomi_B():
        if not (n.startswith('msg:') or n == 'unico'):
            L += [('B', n, f, s) for f in range(pieghe_di(n)) for s in SEMI_B]
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


# ---------------------------------------------------------------- analisi

def auc(y, p):
    from scipy.stats import rankdata
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return None
    r = rankdata(p)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def appaiata(reale, gen):
    """Frazione di coppie (stessa pagina) in cui la generata ha il punteggio piu' alto della vera."""
    reale, gen = np.asarray(reale), np.asarray(gen)
    return float(np.mean((gen > reale) + 0.5 * (gen == reale)))


def auc_logistico(X, y, gruppi, pieghe=10, semi=(231, 232, 233, 234, 235)):
    """Come e231.auc_cv: regressione logistica con standardizzazione, pieghe per gruppo, medie su 5 ripetizioni.
    Restituisce AUC media e le probabilita' medie sulle ripetizioni."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y = np.asarray(X), np.asarray(y)
    aucs, ps = [], []
    n_gr = len(set(gruppi))
    for s in semi:
        p = np.zeros(len(y))
        for tr, te in StratifiedGroupKFold(n_splits=min(pieghe, n_gr), shuffle=True, random_state=s).split(X, y, gruppi):
            mod = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X[tr], y[tr])
            p[te] = mod.predict_proba(X[te])[:, 1]
        aucs.append(auc(y, p))
        ps.append(p)
    return float(np.mean(aucs)), np.mean(ps, axis=0)


def coef_logistico(X, y):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    mod = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(np.asarray(X), np.asarray(y))
    return mod[-1].coef_[0]


def auc_coppie(r, g):
    return auc([0] * len(r) + [1] * len(g), np.concatenate([r, g]))


def auc_coppie_pieghe(r, g, fo):
    """Media delle AUC calcolate dentro ogni piega (pagine vere contro gemelle generate): i punteggi di reti diverse non
    si mescolano."""
    fo = np.asarray(fo)
    return float(np.mean([auc_coppie(r[fo == f], g[fo == f]) for f in sorted(set(fo.tolist()))]))


def ic_coppie(coppie, fo=None, n=1000, seme=1):
    """Intervallo al 95% (bootstrap sulle pagine) della media delle AUC di piu' libri; coppie = [(reali, generate)] con
    le stesse pagine nello stesso ordine. Con `fo` (piega di ogni pagina) le pagine si ricampionano dentro la piega e
    l'AUC e' la media per piega; senza, le pagine sono un solo gruppo."""
    rng = np.random.default_rng(seme)
    m = len(coppie[0][0])
    fo = np.zeros(m, dtype=int) if fo is None else np.asarray(fo)
    gruppi = [np.where(fo == f)[0] for f in sorted(set(fo.tolist()))]
    v = []
    for _ in range(n):
        I = [gr[rng.integers(0, len(gr), len(gr))] for gr in gruppi]
        v.append(np.mean([np.mean([auc_coppie(r[i], g[i]) for i in I]) for r, g in coppie]))
    return [float(x) for x in np.percentile(v, [2.5, 97.5])]


def logistico_pieghe(X, y, fold):
    """Regressione logistica con le pieghe date (stesse del giudice B): probabilita' fuori piega."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y, fold = np.asarray(X), np.asarray(y), np.asarray(fold)
    p = np.zeros(len(y))
    for f in sorted(set(fold.tolist())):
        te = fold == f
        mod = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X[~te], y[~te])
        p[te] = mod.predict_proba(X[te])[:, 1]
    return p


def auc_pieghe(y, p, fold):
    """Media delle AUC calcolate dentro ogni piega: toglie lo spostamento fra le pieghe (con pochi gruppi le probabilita'
    di pieghe diverse non sono confrontabili e l'AUC complessiva puo' scendere sotto 0,5 anche con etichette a caso)."""
    y, p, fold = np.asarray(y), np.asarray(p), np.asarray(fold)
    v = [auc(y[fold == f], p[fold == f]) for f in sorted(set(fold.tolist()))]
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def ic_pieghe(y, p, gruppi, fold, n=1000, seme=1):
    """Bootstrap sulle chiavi dentro ogni piega, per la media delle AUC per piega."""
    rng = np.random.default_rng(seme)
    y, p, gruppi, fold = np.asarray(y), np.asarray(p), np.asarray(gruppi), np.asarray(fold)
    per = {}
    for f in sorted(set(fold.tolist())):
        ks = sorted(set(gruppi[fold == f].tolist()))
        per[f] = [np.where((gruppi == k) & (fold == f))[0] for k in ks]
    v = []
    for _ in range(n):
        a = []
        for f, righe in per.items():
            I = np.concatenate([righe[i] for i in rng.integers(0, len(righe), len(righe))])
            x = auc(y[I], p[I])
            if x is not None:
                a.append(x)
        if a:
            v.append(np.mean(a))
    return [float(x) for x in np.percentile(v, [2.5, 97.5])]


def ic_gruppi(y, p, gruppi, n=1000, seme=1):
    rng = np.random.default_rng(seme)
    y, p, gruppi = np.asarray(y), np.asarray(p), np.asarray(gruppi)
    chiavi = sorted(set(gruppi.tolist()))
    righe = {k: np.where(gruppi == k)[0] for k in chiavi}
    v = []
    for _ in range(n):
        I = np.concatenate([righe[chiavi[i]] for i in rng.integers(0, len(chiavi), len(chiavi))])
        a = auc(y[I], p[I])
        if a is not None:
            v.append(a)
    return [float(x) for x in np.percentile(v, [2.5, 97.5])]


def media_se(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(media=float(np.mean(xs)), se=float(np.std(xs, ddof=1) / len(xs) ** 0.5) if len(xs) > 1 else 0.0, n=len(xs),
                min=float(min(xs)), max=float(max(xs)))


class Dati:
    """Tutti i risultati dei lavori, in forma comoda."""

    def __init__(self, corse):
        self.prof = defaultdict(lambda: defaultdict(list))      # libro -> pagina -> [profilo per seme]
        self.lm = []
        self.B = defaultdict(list)                              # insieme -> [(id, y, logit)]
        self.info_B = defaultdict(list)
        for c in corse:
            if c['tipo'] == 'A':
                self.lm.append(dict(c['info'], job=c['job']))
                for libro_, d in c['profili'].items():
                    for p, f in d.items():
                        self.prof[libro_][p].append(f)
            elif c['tipo'] == 'B':
                self.info_B[c['job'][1]].append(dict(job=c['job'], passi=c['passi'], perdita=c['perdita_validazione'],
                                                     secondi=c['secondi']))
                for i, y, z in c['test']:
                    self.B[c['job'][1]].append((tuple(i), y, z, c['job'][2]))

    def X(self, libro_, p):
        return np.mean(self.prof[libro_][p], axis=0)

    def completo(self, insieme):
        """Tutte le pieghe di un insieme sono state fatte (per tutti i semi)."""
        return len(self.info_B.get(insieme, [])) == pieghe_di(insieme) * len(SEMI_B)

    def B_coppie(self, insieme):
        """Punteggi sui semi: (pagine, reali, generate, piega di ogni pagina) se l'insieme e' appaiato."""
        z = defaultdict(list)
        for i, y, v, _ in self.B.get(insieme, []):
            z[i].append((y, v))
        reali = {i[0]: np.mean([v for _, v in x]) for i, x in z.items() if i[1] == 'vera'}
        gen = {i[0]: np.mean([v for _, v in x]) for i, x in z.items() if i[1] != 'vera'}
        pag = sorted(set(reali) & set(gen))
        fold = contesto()['fold']
        return pag, np.array([reali[p] for p in pag]), np.array([gen[p] for p in pag]), [fold[p] for p in pag]


def risultato_coppie(pag, r, g, fo=None):
    """Con `fo` (giudice B) l'AUC principale e' la media delle AUC per piega e l'AUC complessiva (punteggi di reti
    diverse messi insieme) e' secondaria; senza (giudice A, come e231) l'AUC e' quella delle previsioni messe insieme."""
    m = len(pag)
    if m == 0:
        return None
    pool = auc_coppie(r, g)
    if fo is None:
        return dict(AUC=pool, AUC_appaiata=appaiata(r, g), pagine=m)
    return dict(AUC=auc_coppie_pieghe(r, g, fo), AUC_complessiva=pool, AUC_appaiata=appaiata(r, g), pagine=m)


def analizza_A_coppia(dati, libro_):
    pag = [p for p in dati.prof['vere'] if p in dati.prof[libro_]]
    if len(pag) < 10 or len(pag) < 0.99 * len(contesto()['ids']):
        return None
    X = np.array([dati.X('vere', p) for p in pag] + [dati.X(libro_, p) for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    a, p = auc_logistico(X, y, pag + pag)
    n = len(pag)
    return dict(AUC=a, AUC_appaiata=appaiata(p[:n], p[n:]), pagine=n, coef=coef_logistico(X, y).tolist(), pag=pag,
                reali=p[:n].tolist(), generate=p[n:].tolist())


def analizza_A_negativo(dati, s):
    pag = list(dati.prof['vere'])
    if len(pag) < 10 or len(pag) < 0.99 * len(contesto()['ids']):
        return None
    random.Random(3970 + s).shuffle(pag)
    y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
    X = np.array([dati.X('vere', p) for p in pag])
    return dict(AUC=auc_logistico(X, y, pag)[0])


def c_ids():
    return contesto()['ids']


def analizza_A_chiavi(dati, nome, c):
    """Insiemi per chiave (messaggio): AUC con pieghe per chiave."""
    chiavi = list(CHIAVI_MSG)
    X, y, g, fo = [], [], [], []
    for k in chiavi:
        if nome == 'msg:ab':
            gruppi = [('a%d' % k, 1), ('b%d' % k, 0)]
        elif nome == 'msg:neg':
            gruppi = [('b%d' % k, k % 2)]
        else:
            gruppi = [('b%d' % k, 0), ('p%s:b%d' % (nome[5:], k), 1)]
        for lib_, lab in gruppi:
            if len(dati.prof[lib_]) < 0.99 * len(c_ids()):
                return None
            for p in dati.prof[lib_]:
                X.append(dati.X(lib_, p))
                y.append(lab)
                g.append(k)
                fo.append(c['fold_chiave'][k])
    if len(set(g)) < len(chiavi) or len(set(y)) < 2:
        return None
    p = logistico_pieghe(X, y, fo)
    return dict(AUC=auc_pieghe(y, p, fo), AUC_complessiva=auc(y, p), IC=ic_pieghe(y, p, g, fo), n=len(y))


def analizza(corse):
    c = contesto()
    dati = Dati(corse)
    ris = OrderedDict()
    ris['semi_A'] = len({x['job'][1] for x in dati.lm})
    ris['modelli_del_testo'] = dati.lm
    # ---- giudizio sui libri v21 (con messaggio, chiavi CHIAVI): A, B, B_unico
    libri = OrderedDict()
    for k in CHIAVI:
        nome = 'a%d' % k
        r = OrderedDict(chiave=k)
        a = analizza_A_coppia(dati, nome)
        if a:
            r['A'] = {x: a[x] for x in ('AUC', 'AUC_appaiata', 'pagine', 'coef')}
            r['_A'] = a
        pag, re_, ge, fo = dati.B_coppie('libro:' + nome)
        if pag and dati.completo('libro:' + nome):
            r['B'] = risultato_coppie(pag, re_, ge, fo)
            r['_B'] = (pag, re_, ge, fo)
        libri[nome] = r
    # B_unico: AUC per libro con le pagine vere pooled
    z = defaultdict(list)
    for i, y, v, _ in dati.B.get('unico', []):
        z[i].append(v)
    if z:
        reali = {i[0]: np.mean(v) for i, v in z.items() if i[1] == 'vera'}
        for k in CHIAVI:
            gen = {i[0]: np.mean(v) for i, v in z.items() if i[1] == 'a%d' % k}
            pag = sorted(set(reali) & set(gen))
            if pag and dati.completo('unico'):
                ra, ga = np.array([reali[p] for p in pag]), np.array([gen[p] for p in pag])
                fo = [c['fold'][p] for p in pag]
                libri['a%d' % k]['Bunico'] = risultato_coppie(pag, ra, ga, fo)
                libri['a%d' % k]['_U'] = (pag, ra, ga, fo)
    giud = OrderedDict()
    for g, ch, nome in (('A', '_A', 'sorpresa'), ('B', '_B', 'lettore'), ('Bunico', '_U', 'lettore unico')):
        auc_l = [libri[l][g]['AUC'] for l in libri if libri[l].get(g)]
        ap = [libri[l][g]['AUC_appaiata'] for l in libri if libri[l].get(g)]
        if not auc_l:
            continue
        if g == 'A':
            coppie = [(np.array(libri[l][ch]['reali']), np.array(libri[l][ch]['generate'])) for l in libri if libri[l].get(g)]
            pag_ok = all(libri[l][ch]['pag'] == libri[next(iter(libri))][ch]['pag'] for l in libri if libri[l].get(g))
        else:
            coppie = [(libri[l][ch][1], libri[l][ch][2]) for l in libri if libri[l].get(ch)]
            pag_ok = all(libri[l][ch][0] == libri[next(iter(libri))][ch][0] for l in libri if libri[l].get(ch))
        fo = None if g == 'A' else libri[next(l for l in libri if libri[l].get(ch))][ch][3]
        ic = ic_coppie(coppie, fo) if pag_ok and len(coppie) else None
        giud[g] = OrderedDict(nome=nome, libri=len(auc_l), AUC=media_se(auc_l), AUC_appaiata=media_se(ap),
                              AUC_complessiva=None if g == 'A' else media_se([libri[l][g]['AUC_complessiva'] for l in libri if libri[l].get(g)]),
                              IC_pagine=ic, IC_basso_sopra_soglia=None if ic is None else bool(ic[0] > LETTURA_BASSA))
    ris['giudizio'] = OrderedDict(giudici=giud, libri=OrderedDict(
        (n, OrderedDict((k, v) for k, v in r.items() if not k.startswith('_') and k != 'coef')) for n, r in libri.items()))
    ris['_libri'] = libri
    # riferimenti del paper per le stesse chiavi
    rif = riferimenti_paper()
    if rif:
        ris['riferimento_paper'] = rif
        for g in giud:
            diff = [libri['a%d' % k][g]['AUC'] - rif['a|%d' % k]['AUC_e266'] for k in CHIAVI
                    if libri['a%d' % k].get(g) and 'a|%d' % k in rif]
            giud[g]['meno_giudice2_paper'] = media_se(diff)
    # ---- controlli
    ctrl = OrderedDict()
    for nome in ('ctrl:parole', 'ctrl:e192', 'ctrl:ordine1', 'ctrl:righe'):
        r = OrderedDict()
        a = analizza_A_coppia(dati, nome)
        if a:
            r['A'] = dict(AUC=a['AUC'], AUC_appaiata=a['AUC_appaiata'])
        pag, re_, ge, fo = dati.B_coppie(nome)
        if pag and dati.completo(nome):
            r['B'] = risultato_coppie(pag, re_, ge, fo)
        if r:
            ctrl[nome] = r
    neg = OrderedDict(A=[], B=[])
    for s in range(1, NEG + 1):
        a = analizza_A_negativo(dati, s)
        if a:
            neg['A'].append(a['AUC'])
        z = dati.B.get('neg:%d' % s, [])
        if dati.completo('neg:%d' % s):
            neg['B'].append(auc_pieghe([x[1] for x in z], [x[2] for x in z], [x[3] for x in z]))
            neg.setdefault('B_complessiva', []).append(auc([x[1] for x in z], [x[2] for x in z]))
    ctrl['negativo'] = OrderedDict((g, dict(AUC_per_etichetta=v, media=float(np.mean(v)) if v else None)) for g, v in neg.items())
    ris['controlli'] = ctrl
    # ---- messaggio
    msg = OrderedDict()
    for nome in ['msg:ab', 'msg:neg'] + ['msg:f%s' % f for f in FRAZIONI]:
        r = OrderedDict()
        a = analizza_A_chiavi(dati, nome, c)
        if a:
            r['A'] = a
        z = dati.B.get(nome, [])
        if z and dati.completo(nome):
            ys = [x[1] for x in z]
            chiave_di = {}
            for k in CHIAVI_MSG:
                chiave_di['a%d' % k] = chiave_di['b%d' % k] = chiave_di['p%d' % k] = k
            gr = [chiave_di[x[0][1]] for x in z]
            vals = [x[2] for x in z]
            fo = [x[3] for x in z]
            r['B'] = dict(AUC=auc_pieghe(ys, vals, fo), AUC_complessiva=auc(ys, vals), IC=ic_pieghe(ys, vals, gr, fo), n=len(ys))
        if r:
            msg[nome] = r
    ris['messaggio'] = msg
    # ---- descrittivo del giudice A: dove sta la differenza (libri v21, media sui libri)
    ris['descrittivo_A'] = descrittivo(dati, c)
    ris['tempi_B'] = {k: dict(passi_medi=float(np.mean([x['passi'] for x in v])), secondi_medi=float(np.mean([x['secondi'] for x in v])))
                      for k, v in dati.info_B.items()}
    return ris


def riferimenti_paper():
    out = {}
    for lo, hi in ((1, 12), (13, 24)):
        p = os.path.join(QUI, '..', 'risultati', 'e409b_messaggio_nel_sacco_v21f1_chiavi_%d_%d.json' % (lo, hi))
        if os.path.exists(p):
            out.update({k: dict(AUC_e231=v['AUC_e231'], AUC_e266=v['AUC_e266'])
                        for k, v in json.load(open(p, encoding='utf-8'))['per_chiave'].items()})
    return out


def descrittivo(dati, c):
    """Differenza media di ogni misura di sorpresa (generata meno vera) sulle pagine, per libro, poi media e errore sui libri."""
    libri = ['a%d' % k for k in CHIAVI if 'a%d' % k in dati.prof]
    if not libri or 'vere' not in dati.prof:
        return None
    sez = lambda p: c['tipo'][p][0]
    lin = lambda p: c['tipo'][p][1]
    per_carat = defaultdict(list)
    per_sez = defaultdict(lambda: defaultdict(list))
    per_lin = defaultdict(lambda: defaultdict(list))
    auc1 = defaultdict(list)
    for l in libri:
        pag = [p for p in dati.prof['vere'] if p in dati.prof[l]]
        if not pag:
            continue
        R = np.array([dati.X('vere', p) for p in pag])
        G = np.array([dati.X(l, p) for p in pag])
        for j, nome in enumerate(CARATTERISTICHE):
            per_carat[nome].append(float(np.mean(G[:, j] - R[:, j])))
            auc1[nome].append(auc([0] * len(pag) + [1] * len(pag), np.concatenate([R[:, j], G[:, j]])))
        for dove, f, tab in (('sezione', sez, per_sez), ('lingua', lin, per_lin)):
            for v in sorted({f(p) for p in pag}, key=str):
                ix = [i for i, p in enumerate(pag) if f(p) == v]
                for nome in ('bit_medi', 'inizio_parola', 'inizio_riga', 'dentro_parola', 'spazio', 'fine_riga'):
                    j = CARATTERISTICHE.index(nome)
                    tab[str(v)][nome].append(float(np.mean(G[ix, j] - R[ix, j])))
                tab[str(v)]['pagine'] = [len(ix)]
    return OrderedDict(
        differenza_per_caratteristica=OrderedDict((k, dict(media_se(v), AUC_singola=float(np.mean(auc1[k])))) for k, v in per_carat.items()),
        differenza_per_sezione=OrderedDict((s, OrderedDict((k, media_se(v)['media'] if k != 'pagine' else v[0]) for k, v in d.items())) for s, d in per_sez.items()),
        differenza_per_lingua=OrderedDict((s, OrderedDict((k, media_se(v)['media'] if k != 'pagine' else v[0]) for k, v in d.items())) for s, d in per_lin.items()))


# ---------------------------------------------------------------- letture e scrittura

def validita(ris):
    """Controlli per ogni giudice: positivo (AUC >= soglia sui controlli che fanno da positivo) e negativo (media delle
    etichette a caso dentro la banda)."""
    ctrl = ris['controlli']
    positivi = ['ctrl:ordine1'] if SOLO_CONTROLLI else ['ctrl:parole', 'ctrl:e192']
    out = OrderedDict()
    for g in ('A', 'B'):
        valori = OrderedDict((n, ctrl[n][g]['AUC']) for n in positivi if n in ctrl and g in ctrl[n])
        mancano = [n for n in positivi if n not in valori]
        pos = bool(valori) and all(v >= SOGLIA_POSITIVO for v in valori.values()) and (SOLO_CONTROLLI or 'ctrl:parole' in valori)
        n_ = ctrl['negativo'].get(g, {}).get('media')
        neg = n_ is not None and BANDA[0] <= n_ <= BANDA[1]
        out[g] = OrderedDict(positivo=pos, valori_positivi=valori, positivi_mancanti=mancano, negativo=neg, AUC_negativo=n_,
                             valido=pos and neg)
    out['Bunico'] = dict(out['B'], nota='stessi controlli del lettore B (stessa rete e stesso addestramento)')
    return out


def lettura_giudizio(ris, val):
    giud = ris['giudizio']['giudici']
    validi = [g for g in giud if val.get(g, {}).get('valido')]
    if not validi:
        return 'nessun giudice ha superato i controlli: nessuna lettura'
    best = max(validi, key=lambda g: giud[g]['AUC']['media'])
    a = giud[best]['AUC']['media']
    if a <= LETTURA_BASSA:
        t = 'la v21 regge anche contro una rete (AUC <= %.2f)' % LETTURA_BASSA
    elif a > LETTURA_ALTA:
        t = 'la rete vede qualcosa che i giudici del paper non vedono (AUC > %.2f): vedi il descrittivo' % LETTURA_ALTA
    else:
        t = 'zona grigia (%.2f < AUC <= %.2f)' % (LETTURA_BASSA, LETTURA_ALTA)
    ic = giud[best].get('IC_pagine')
    t2 = '' if not ic else '; intervallo al 95%% sulle pagine %.3f-%.3f: il limite basso %s %.2f' % (
        ic[0], ic[1], 'supera' if ic[0] > LETTURA_BASSA else 'NON supera', LETTURA_BASSA)
    return 'giudice migliore fra i validi: %s, AUC media %.3f: %s%s' % (best, a, t, t2)


def piu_piccola(msg, g):
    """La frazione piu' piccola della scala che il giudice separa con AUC >= POTENZA."""
    visti = [f for f in FRAZIONI if msg.get('msg:f%s' % f, {}).get(g, {}).get('AUC', 0) >= POTENZA]
    return '; scala: ' + ('si vede dal %.0f%% di parole sostituite' % (100 * min(visti)) if visti else 'nessuna frazione arriva a %.2f' % POTENZA)


def lettura_messaggio(ris, val):
    out = OrderedDict()
    msg = ris['messaggio']
    for g in ('A', 'B'):
        if 'msg:ab' not in msg or g not in msg['msg:ab']:
            continue
        a = msg['msg:ab'][g]['AUC']
        neg = msg.get('msg:neg', {}).get(g, {}).get('AUC')
        pot = msg.get('msg:f%s' % POT_FR, {}).get(g, {}).get('AUC')
        dentro = BANDA[0] <= a <= BANDA[1]
        neg_ok = neg is not None and BANDA[0] <= neg <= BANDA[1]
        pot_ok = pot is not None and pot >= POTENZA
        if not neg_ok or not pot_ok:
            t = 'lettura non valida (controllo negativo %s, potenza %s)' % ('ok' if neg_ok else 'FALLITO', 'ok' if pot_ok else 'INSUFFICIENTE')
        elif dentro:
            t = 'nessuna traccia con questa sensibilita\''
        elif a < BANDA[0]:
            t = 'AUC sotto %.2f: da capire (non e\' una traccia; sotto il caso vuol dire un artefatto delle pieghe o un addestramento instabile)' % BANDA[0]
        else:
            t = 'possibile traccia (AUC fuori da %.2f-%.2f)' % BANDA
        out[g] = '%s: AUC %.3f; negativo %s; frazione %.0f%% -> %s: %s' % (
            g, a, '-' if neg is None else '%.3f' % neg, 100 * POT_FR, '-' if pot is None else '%.3f' % pot, t + piu_piccola(msg, g))
    return out


def scrivi(corse, versioni):
    ris = analizza(corse)
    val = validita(ris)
    ris['validita'] = val
    ris['lettura_giudizio'] = lettura_giudizio(ris, val)
    ris['lettura_messaggio'] = lettura_messaggio(ris, val)
    interno = ris.pop('_libri')
    ris_json = OrderedDict(esperimento='ia01', parametri=OrderedDict(
        PAGINE_MIN_PAROLE=MIN_PAROLE, NF=NF, CHIAVI=CHIAVI, CHIAVI_MSG=CHIAVI_MSG, FRAZIONI=FRAZIONI, NEG=NEG, SEMI=SEMI,
        SEMI_B=SEMI_B, EMB=EMB, NASCOSTO=NASCOSTO, CADUTA=CADUTA, LR=LR, DECADIMENTO=DECADIMENTO, TAGLIO=TAGLIO, LUNG=LUNG,
        LOTTO=LOTTO, PASSI=PASSI, OGNI=OGNI, PAZIENZA=PAZIENZA, EMB_B=EMB_B, NASC_B=NASC_B, CADUTA_B=CADUTA_B, LUNG_B=LUNG_B,
        LOTTO_B=LOTTO_B, PASSI_B=PASSI_B, PAZIENZA_B=PAZIENZA_B, SOGLIA_POSITIVO=SOGLIA_POSITIVO, BANDA=BANDA,
        LETTURA_BASSA=LETTURA_BASSA, LETTURA_ALTA=LETTURA_ALTA, POTENZA=POTENZA, SOLO_CONTROLLI=SOLO_CONTROLLI),
        versioni=versioni, **ris)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris_json, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    f3 = lambda x: '-' if x is None else '%.3f' % x
    ctrl = ris['controlli']
    r = ['# ia01 — giudice neurale', '']
    for g in ('A', 'B'):
        v = val[g]
        r.append('controllo positivo, giudice %s: %s (soglia %.2f): %s' % (
            g, ', '.join('%s %.3f' % (n, x) for n, x in v['valori_positivi'].items()) or 'nessun valore',
            SOGLIA_POSITIVO, 'SUPERATO' if v['positivo'] else 'NON superato'))
    for g in ('A', 'B'):
        v = val[g]
        r.append('controllo negativo, giudice %s: vere contro vere, etichette a caso, AUC media %s (%s), banda %.2f-%.2f: %s' % (
            g, f3(v['AUC_negativo']), ', '.join(f3(x) for x in ctrl['negativo'].get(g, {}).get('AUC_per_etichetta', [])),
            BANDA[0], BANDA[1], 'SUPERATO' if v['negativo'] else 'NON superato'))
    r += ['', 'Lettura sul giudizio: %s.' % ris['lettura_giudizio'], '']
    for g, t in ris['lettura_messaggio'].items():
        r.append('Lettura sul messaggio, giudice %s -> %s' % (g, t))
    r += ['', 'Semi dei modelli del testo: %d. Valori: AUC media sui libri (errore standard sui libri).' % ris['semi_A'], '',
          '## Libri v21 (con messaggio) contro il Voynich, chiavi %s' % ', '.join(map(str, CHIAVI)), '',
          'AUC di B e B unico = media delle AUC dentro ogni piega; AUC di A = previsioni delle pieghe messe insieme (come e231).', '',
          '| giudice | AUC media (se) | min-max | IC 95% pagine | limite basso > 0,62 | AUC complessiva (B) | AUC appaiata | meno giudice 2 del paper (se) |',
          '|---|---|---|---|---|---|---|---|']
    for g, d in ris['giudizio']['giudici'].items():
        dd = d.get('meno_giudice2_paper')
        r.append('| %s | %s (%s) | %s-%s | %s | %s | %s | %s | %s |' % (
            d['nome'], f3(d['AUC']['media']), f3(d['AUC']['se']), f3(d['AUC']['min']), f3(d['AUC']['max']),
            '-' if not d['IC_pagine'] else '%.3f-%.3f' % tuple(d['IC_pagine']),
            '-' if d['IC_basso_sopra_soglia'] is None else ('si' if d['IC_basso_sopra_soglia'] else 'no'),
            f3((d.get('AUC_complessiva') or {}).get('media')), f3(d['AUC_appaiata']['media']),
            '-' if not dd else '%+.3f (%.3f)' % (dd['media'], dd['se'])))
    r += ['', 'Paper v2, stesse chiavi: giudice 1 e giudice 2 per chiave in `risultati/e409b_*_v21f1_*.json` '
          '(media sulle 24 chiavi: %.3f e %.3f).' % (PAPER['giudice1'], PAPER['giudice2']), '',
          '| libro | A | B | B unico | giudice 2 del paper |', '|---|---|---|---|---|']
    rif = ris.get('riferimento_paper', {})
    for n, d in ris['giudizio']['libri'].items():
        k = n[1:]
        r.append('| %s | %s | %s | %s | %s |' % (n, f3(d.get('A', {}).get('AUC')), f3((d.get('B') or {}).get('AUC')),
                                                 f3((d.get('Bunico') or {}).get('AUC')), f3(rif.get('a|' + k, {}).get('AUC_e266'))))
    r += ['', '## Controlli', '', '| insieme | A | B |', '|---|---|---|']
    for n, d in ctrl.items():
        if n == 'negativo':
            continue
        r.append('| %s | %s | %s |' % (n, f3(d.get('A', {}).get('AUC')), f3(d.get('B', {}).get('AUC'))))
    r.append('| negativo (media di %d etichette) | %s | %s |' % (NEG, f3(ctrl['negativo'].get('A', {}).get('media')),
                                                              f3(ctrl['negativo'].get('B', {}).get('media'))))
    r += ['', 'Riferimenti del paper per il giudice 2: parole rimescolate nella riga 0,99; righe rimescolate nella pagina '
          '0,595; e192 0,97 (con il giudice vecchio).', '', '## Messaggio: libri con contro libri senza (chiavi %s); AUC = media delle AUC per piega, IC 95%% col bootstrap sulle chiavi' % ', '.join(map(str, CHIAVI_MSG)), '',
          '| insieme | A | B |', '|---|---|---|']
    for n, d in ris['messaggio'].items():
        r.append('| %s | %s | %s |' % (n, '-' if 'A' not in d else '%s (%s-%s)' % (f3(d['A']['AUC']), f3(d['A']['IC'][0]), f3(d['A']['IC'][1])),
                                       '-' if 'B' not in d else '%s (%s-%s)' % (f3(d['B']['AUC']), f3(d['B']['IC'][0]), f3(d['B']['IC'][1]))))
    r.append('Paper: AUC 0,506 con le caratteristiche del giudice 2.')
    de = ris.get('descrittivo_A')
    if de:
        r += ['', '## Dove il giudice A trova la differenza (generata meno vera, bit per segno; media sui libri)', '',
              '| misura | differenza (se) | AUC della sola misura |', '|---|---|---|']
        for k, d in de['differenza_per_caratteristica'].items():
            r.append('| %s | %+.4f (%.4f) | %s |' % (k, d['media'], d['se'], f3(d['AUC_singola'])))
        for nome, tab in (('sezione', de['differenza_per_sezione']), ('lingua', de['differenza_per_lingua'])):
            r += ['', 'Per %s (differenza in bit per segno; pagine):' % nome, '',
                  '| %s | pagine | media | inizio parola | inizio riga | dentro parola | spazio | a capo |' % nome, '|---|---|---|---|---|---|---|---|']
            for s, d in tab.items():
                r.append('| %s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f |' % (
                    s, d['pagine'], d['bit_medi'], d['inizio_parola'], d['inizio_riga'], d['dentro_parola'], d['spazio'], d['fine_riga']))
        cs = [interno[l]['_A']['coef'] for l in interno if '_A' in interno[l]]
        if cs:
            coef = np.mean(cs, axis=0)
            r += ['', 'Coefficienti medi della regressione (misure standardizzate; positivo = piu alto nella generata):', '',
                  ', '.join('%s %+.2f' % (n, x) for n, x in sorted(zip(CARATTERISTICHE, coef), key=lambda t: -abs(t[1])))]
    if ris['modelli_del_testo']:
        r += ['', 'Modelli del testo (giudice A): bit per segno sulla validazione %s; passi %s.' % (
            f3(float(np.mean([x['bpc_validazione'] for x in ris['modelli_del_testo']]))),
            int(np.mean([x['passi'] for x in ris['modelli_del_testo']])))]
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris, r


def main():
    import torch
    import numpy
    import scipy
    import sklearn
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__,
                    scipy=scipy.__version__, scikit_learn=sklearn.__version__)
    os.makedirs(USCITA, exist_ok=True)
    c = contesto()
    print('pagine vere: %d, segni %d, vocabolario %d; pieghe %s; chiavi giudizio %s, chiavi messaggio %s' % (
        len(c['ids']), sum(len(a) for a in c['ids'].values()), c['V'], NF, CHIAVI, CHIAVI_MSG), flush=True)
    percorso = os.path.join(USCITA, 'ia01_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    else:
        open(percorso, 'w').close()
        if os.path.isdir(LIBRI):
            for n in os.listdir(LIBRI):
                os.remove(os.path.join(LIBRI, n))
    fatte = {json.dumps(x['job']) for x in corse}
    processi = int(os.environ.get('PROCESSI', 8))
    inizio = time.time()
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        # fase 1: libri generati (con RIPRENDI quelli gia' salvati si saltano)
        for fase, lav in (('libri', lavori_generazione()), ('addestramento', None)):
            if lav is None:
                lav = lavori_addestramento()
            da_fare = [j for j in lav if json.dumps(list(j)) not in fatte]
            print('%s: %d da fare, %d gia fatti' % (fase, len(da_fare), len(lav) - len(da_fare)), flush=True)
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                if fase == 'libri':
                    print('  libro %s: %s (%.0f s)' % (r['job'][1], r['esito'], r['tempo']), flush=True)
                    if r['esito'] not in ('fatto', 'gia\' fatto'):
                        print('  ATTENZIONE: %s non disponibile (%s)' % (r['job'][1], r['esito']), flush=True)
                else:
                    corse.append(r)
                    with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')
                    extra = ' passi %d' % (r['info']['passi'] if 'info' in r else r['passi'])
                    print('[%d/%d %.0f min] %s (%.0f s)%s' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo'], extra), flush=True)
            if fase == 'libri':
                mancano = [n for _, n in lav if n != 'e192' and not os.path.exists(percorso_libro(n))]
                if mancano:
                    pool.terminate()
                    raise SystemExit("FERMO: mancano i libri %s (la generazione e' fallita: vedi gli ERRORE sopra). "
                                     "Solo e192 e' facoltativo." % ', '.join(mancano))
    ris, righe = scrivi(corse, versioni)
    print('\n'.join(righe[:14]), flush=True)


if __name__ == '__main__':
    main()
