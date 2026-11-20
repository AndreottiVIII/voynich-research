# -*- coding: utf-8 -*-
"""Esperimento IA7 (ia07): il Voynich ricreato da una rete neurale locale, con e senza messaggio nascosto.

Una rete a segni (GRU) impara il testo corrente del Voynich pagina per pagina e poi scrive un libro intero con la stessa
disposizione del vero: stesse pagine, stesse righe, stesse sezioni, mani, lingue A/B e paragrafi. Ogni pagina è una
sequenza che comincia con una testa di pagina (sezione, mano, lingua) e, per ogni riga, una testa di riga (tipo di riga:
prima, interna, ultima o unica del paragrafo; posizione nella pagina a fasce; lunghezza della riga vera a fasce), poi i
segni della riga e il segno di fine riga. Lo stato della rete passa da una riga all'altra dentro la pagina.
Generazione onesta: 5 pieghe per foglio, per ciascuna 2 modelli (repliche con semi di addestramento diversi), addestrati sull'80% dei fogli (una parte
dei fogli di addestramento fa da validazione per l'arresto); ogni modello scrive le pagine dei fogli che non ha visto (i libri si dividono a metà fra le due repliche). Un
undicesimo modello, addestrato su tutti i fogli, scrive il libro "vetrina".

Il campionamento è a temperatura 1 quasi esatta (probabilità rese intere, minimo 2^-24 per segno) ed è pilotato da un flusso di bit con la codifica aritmetica
(stego_ia07.py): libri senza messaggio (bit di riempimento da un seme) e libri con il messaggio (Isidoro XVII, lo stesso
testo del v21) cifrato con una parola chiave.

Misure per libro: giudici 1 (e231) e 2 (e266) del paper con il loro protocollo (un giudice per libro, pagina vera e
generata nella stessa piega), giudice A "sorpresa" di IA1 (aggiunto il 20/11/2026: GRU a caratteri per piega addestrata
sulle pagine vere delle altre pieghe, profilo di sorpresa di 14 numeri, regressione logistica; funzioni importate da
ia01_giudice_neurale; le pieghe sono quelle dei generatori; v21 e controlli ricalcolati con lo stesso giudice),
pagella e pagella estesa (se PAGELLA=1), copia a memoria (5-grammi e 3-grammi di parole,
righe intere, parole nuove rispetto al testo d'addestramento del modello che ha scritto la pagina), capacità in bit,
recupero esatto del messaggio, chiave sbagliata respinta. Sintesi: con contro senza messaggio (giudice 2, pieghe per
libro, come e419), controlli.

    nohup bash strumenti/coda.sh voynich_neurale "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=10:ia07" ...
    SOLO_CONTROLLI=1 USCITA=... python esperimenti/ia07_voynich_neurale.py     (prova sul libro latino)
    python esperimenti/ia07_voynich_neurale.py --leggi LIBRO.txt CHIAVE         (rilegge un messaggio)

SOLO_CONTROLLI=1: il "libro vero" è un libro latino con la disposizione del Voynich (dai soli metadati: pagine, righe,
numero di parole per riga, sezioni, mani, lingue, paragrafi). Le righe di lingua A dell'erbario hanno il Macer Floridus,
le altre di lingua A Plinio, quelle di lingua B Plinio abbreviato (Gaskell e Bowern). Nessuna parola del Voynich.
Manopole per le prove: EPOCHE_MAX, PAZIENZA, STRATI, NASCOSTO, N_SENZA, N_CON, PAGELLA, FASI, e per il giudice A
PASSI_A, OGNI_A, PAZIENZA_A, NASCOSTO_A, CADUTA_A (nomi propri: ia01 legge PASSI, PAZIENZA, NASCOSTO dall'ambiente con altri
valori predefiniti, qui li si imposta esplicitamente dopo l'import). RIPRENDI=1 riprende. PROCESSI cambia solo il parallelismo.

Preregistrazione: preregistrazioni/ia07.md. Scrive risultati/ia07_voynich_neurale.json e .md,
risultati/ia07_corse.jsonl (una riga per lavoro) e il controllo di copia della vetrina. Il libro vetrina e le sue immagini
(dati/cache/ia07_vetrina, MAI in risultati/), i modelli e i libri addestrati sul Voynich vanno in dati/cache/ (non nel repo).
"""
import json, math, os, random, re, statistics, sys, time
from collections import Counter, OrderedDict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import stego_ia07 as st
import ia01_giudice_neurale as ia01      # giudice A "sorpresa" di IA1: funzioni importate, non copiate

NOME = 'ia07_voynich_neurale'
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
CACHE = os.path.join(QUI, '..', 'dati', 'cache')
MODELLI = os.environ.get('MODELLI', os.path.join(USCITA, 'ia07_modelli') if SOLO_CONTROLLI else os.path.join(CACHE, 'ia07_modelli'))
LIBRI = os.environ.get('LIBRI', os.path.join(USCITA, 'ia07_libri') if SOLO_CONTROLLI else os.path.join(CACHE, 'ia07_libri'))
# Il libro vetrina (testo e immagini) non va MAI in risultati/: può contenere righe copiate dalla trascrizione protetta.
# In risultati/ va solo il controllo di copia della vetrina; la pubblicazione di qualche pagina la decide Davide.
VETRINA = os.environ.get('VETRINA', os.path.join(USCITA, 'ia07_vetrina') if SOLO_CONTROLLI else os.path.join(CACHE, 'ia07_vetrina'))
MESSAGGIO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')

# rete e addestramento
EMB = 64
STRATI = int(os.environ.get('STRATI', 2))
NASCOSTO = int(os.environ.get('NASCOSTO', 256))
CADUTA = float(os.environ.get('CADUTA', 0.3))
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
LOTTO = int(os.environ.get('LOTTO', 8))   # pagine per lotto
TRONCO = 256                # segni per tratto di retropropagazione (lo stato passa da un tratto al successivo)
EPOCHE_MAX = int(os.environ.get('EPOCHE_MAX', 150))
PAZIENZA = int(os.environ.get('PAZIENZA', 10))
QUOTA_VAL = 0.125           # fogli di validazione fra quelli di addestramento
PIEGHE = 5
REPLICHE = 2                 # semi di addestramento per piega (i libri si dividono a metà fra le due repliche)
SEME_PIEGHE = 3003
# disposizione
POS_BORDI = (0, 1, 2, 3, 4, 6, 9, 13, 18, 26)   # indice della riga nella pagina, a fasce
N_FASCE = 8                                     # lunghezza della riga vera (segni e spazi), a fasce di uguale frequenza
# libri
N_SENZA = int(os.environ.get('N_SENZA', 20))
N_CON = int(os.environ.get('N_CON', 20))
SEMI_O = (1, 2)
SEMI_CASO = (1, 2, 3, 4, 5)
PAGELLA = os.environ.get('PAGELLA', '0' if SOLO_CONTROLLI else '1') == '1'
FASI = os.environ.get('FASI', 'ABCS')
# riferimenti del paper v2 (e409b, 24 chiavi; e400, semi 1-4)
V21 = OrderedDict([('AUC_e231', (0.554, 0.004)), ('AUC_e266', (0.601, 0.005)), ('capacita', (81100, 85900)), ('pagella', 16.0),
                   ('trigrammi_nel_Voynich', 0.0043)])
SCALA = OrderedDict([('O1 righe rimescolate nella pagina', (0.481, 0.595)), ('O2 parole rimescolate nella riga', (0.984, 0.990))])
SOGLIA_POSITIVO = 0.95
NEGATIVO = (0.45, 0.55)

# giudice A "sorpresa" (IA1), aggiunto il 20/11/2026. Il modello del testo è quello di ia01 (GRU a caratteri 1 x 128, immersione 32,
# finestre di 64, lotti di 32, AdamW 0,002, al massimo 4.000 passi, pazienza 10 valutazioni di 20 passi, 10% delle pagine per
# l'arresto). ia01 legge PASSI, OGNI, PAZIENZA, NASCOSTO, CADUTA dall'ambiente (variabili che qui servono ad altro, con altri
# valori): dopo l'import li si fissa esplicitamente, con nomi propri, così il giudice è lo stesso di ia01 qualunque cosa si
# imposti per i generatori.
SEMI_A = (1, 2)                                   # semi dei modelli del testo, come in ia01
CHIAVI_V21 = tuple(range(13, 23))                # chiavi dei libri v21 di ia01 (mai usate per scegliere le varianti)
SOGLIA_POSITIVO_A = 0.85                          # come in ia01
LETTURA_A = (0.62, 0.65)                          # come in ia01 (letture "regge" / "grigia" / "vede")
AUC_A_IA01 = 0.751                                # ia01: giudice A sui libri v21 con messaggio, chiavi 13-22, pieghe per pagina
CONTROLLI_A_IA01 = OrderedDict([('parole rimescolate', 0.985), ('e192', 0.957), ('negativo', 0.483), ('righe rimescolate', 0.576)])
SCARTO_IA01 = 0.03                                # tolleranza per dire che il ricalcolo del v21 è coerente con 0,751
NOMI_CTRL_A = ('parole', 'righe', 'ordine1') if SOLO_CONTROLLI else ('parole', 'righe', 'e192')
ia01.NASCOSTO = int(os.environ.get('NASCOSTO_A', 128))
ia01.CADUTA = float(os.environ.get('CADUTA_A', 0.3))
ia01.PASSI = int(os.environ.get('PASSI_A', 4000))
ia01.OGNI = int(os.environ.get('OGNI_A', 20))
ia01.PAZIENZA = int(os.environ.get('PAZIENZA_A', 10))
ia01.LIBRI = os.path.join(CACHE, 'ia01_libri')    # libri v21 di ia01 (chiavi 13-24) ed e192: li ha già fatti ia01
MODELLI_A = os.path.join(MODELLI, 'giudiceA')

_C = {}


# ---------------------------------------------------------------- il libro vero

def foglio_di(pagina):
    """f1r -> f1, f67r2 -> f67; i nomi senza numero (fRos, il pieghevole delle rosette) restano un foglio a sé."""
    m = re.match(r'f\d+', pagina)
    return m.group(0) if m else pagina


def latino():
    """Flussi di parole latine: Macer Floridus (erbario), Plinio, Plinio abbreviato (Gaskell e Bowern)."""
    import e381_parole_intere as e381
    import e99_macer as e99
    tt = e381.testi()
    plinio = [''.join(w) for r in tt["Historical - Latin - Technical - Pliny's Natural History.txt"] for w in r]
    abbr = [''.join(w) for r in tt["Historical - Latin (Abbreviated) - Technical - Pliny's Natural History.txt"] for w in r]
    macer = [w for c in e99.capitoli() for v in c for w in v]
    return OrderedDict([('erbario A', iter(macer + plinio[300000:])), ('A', iter(plinio[150000:])),
                        ('B', iter(abbr[200000:])), ('?', iter(plinio[100000:150000]))])


def libro_vero():
    """Righe del libro vero, in ordine: dict(pagina, foglio, sezione, lingua, mano, ini, fin, parole).
    Voynich: trascrizione ZL, testo corrente, parole senza ? e * (come pezzi.voynich ed e231.voynich).
    Controlli: la stessa disposizione con parole latine (dal Voynich si tiene solo il numero di parole per riga)."""
    if 'righe' in _C:
        return _C['righe']
    import trascrizione
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            righe.append(dict(pagina=r.pagina, foglio=foglio_di(r.pagina), sezione=r.sezione or '?', lingua=r.lingua or '?',
                              mano=r.mano or '?', ini=bool(r.inizio_par), n=len(ps), parole=None if SOLO_CONTROLLI else ps))
    if SOLO_CONTROLLI:
        flussi = latino()
        for x in righe:
            f = 'erbario A' if (x['sezione'] == 'H' and x['lingua'] == 'A') else x['lingua'] if x['lingua'] in ('A', 'B') else '?'
            x['parole'] = [next(flussi[f]) for _ in range(x['n'])]
    for i, x in enumerate(righe):
        dopo = righe[i + 1] if i + 1 < len(righe) else None
        x['fin'] = dopo is None or dopo['pagina'] != x['pagina'] or dopo['ini']
        del x['n']
    _C['righe'] = righe
    return righe


def per_pagina(righe):
    out = OrderedDict()
    for x in righe:
        out.setdefault(x['pagina'], []).append(x)
    return out


def come_rr(righe):
    """Nel formato dei giudici e del voynichizzatore: [(pagina, inizio paragrafo, parole)]."""
    return [(x['pagina'], x['ini'], list(x['parole'])) for x in righe]


def pieghe():
    """foglio -> piega (0-4). Fogli in ordine di comparsa; dentro ogni sezione (quella della prima riga) in ordine
    casuale, poi a giro sulle 5 pieghe."""
    righe = libro_vero()
    sez = OrderedDict()
    for x in righe:
        sez.setdefault(x['foglio'], x['sezione'])
    rnd = random.Random(SEME_PIEGHE)
    out, k = {}, 0
    for s in sorted(set(sez.values())):
        ff = [f for f in sez if sez[f] == s]
        rnd.shuffle(ff)
        for f in ff:
            out[f] = k % PIEGHE
            k += 1
    return out


def fogli_della_piega(piega):
    """(fogli di addestramento, fogli di validazione, fogli tenuti fuori) per la piega; 'tutto': tutti, nessuno, nessuno."""
    pg = pieghe()
    if piega == 'tutto':
        return sorted(pg), [], []
    fuori = sorted(f for f, k in pg.items() if k == piega)
    dentro = sorted(f for f, k in pg.items() if k != piega)
    rnd = random.Random(3100 + piega)
    rnd.shuffle(dentro)
    nv = int(math.ceil(QUOTA_VAL * len(dentro)))
    return sorted(dentro[nv:]), sorted(dentro[:nv]), fuori


# ---------------------------------------------------------------- segni e teste

def divisore():
    import misure
    return misure.divisore(misure.GLIFI_EVA)


def vocabolario():
    """Segni (glifi EVA fusi, come in e3c95; per il latino le lettere con ch e sh fusi), spazio, fine riga e teste.
    L'elenco dei segni viene da tutto il libro (solo l'elenco, nessuna frequenza)."""
    if 'voc' in _C:
        return _C['voc']
    righe, D = libro_vero(), divisore()
    unita = sorted({u for x in righe for w in x['parole'] for u in D(w)})
    # trascrizione.pulisci toglie i commenti <...>, i segni di paragrafo <%> <$>, le scelte [a:b], le graffe e gli
    # apostrofi, trasforma i segni rari @nnn; in '*' (parola poi scartata da trascrizione.pulita) e divide su . e ,;
    # qui si controlla che restino solo lettere, così i separatori del formato del libro non possono comparire.
    strani = sorted({c for u in unita for c in u if not c.isalpha()})
    if strani:
        raise SystemExit('segni non alfabetici nel libro vero (%s): il formato del libro non li può scrivere, fermo prima '
                         'dell\'addestramento' % ' '.join(repr(c) for c in strani))
    teste = ['<pad>', '<pag>']
    teste += ['S:' + s for s in sorted({x['sezione'] for x in righe})]
    teste += ['M:' + s for s in sorted({x['mano'] for x in righe})]
    teste += ['L:' + s for s in sorted({x['lingua'] for x in righe})]
    teste += ['T:' + t for t in 'PMUS'] + ['R:%d' % i for i in range(len(POS_BORDI))] + ['N:%d' % i for i in range(N_FASCE)]
    voc = teste + [' ', '\n'] + unita
    lung = sorted(lunghezza(x, D) for x in righe)
    bordi = [lung[int(len(lung) * i / N_FASCE)] for i in range(1, N_FASCE)]
    _C['voc'] = dict(segni=voc, idx={s: i for i, s in enumerate(voc)}, primo_contenuto=len(teste), bordi=bordi,
                     lmax=int(1.25 * lung[-1]), unita=unita)
    return _C['voc']


def lunghezza(x, D):
    return sum(len(D(w)) for w in x['parole']) + len(x['parole']) - 1


def testa_pagina(righe_pag, voc):
    x, i = righe_pag[0], voc['idx']
    return [i['<pag>'], i['S:' + x['sezione']], i['M:' + x['mano']], i['L:' + x['lingua']]]


def testa_riga(x, j, voc, D):
    i = voc['idx']
    tipo = 'S' if x['ini'] and x['fin'] else 'P' if x['ini'] else 'U' if x['fin'] else 'M'
    pos = max(k for k, b in enumerate(POS_BORDI) if j >= b)
    lu = lunghezza(x, D)
    fascia = sum(lu >= b for b in voc['bordi'])
    return [i['T:' + tipo], i['R:%d' % pos], i['N:%d' % fascia]]


def sequenza(righe_pag, voc, D):
    """Una pagina come sequenza di indici."""
    i = voc['idx']
    seq = testa_pagina(righe_pag, voc)
    for j, x in enumerate(righe_pag):
        seq += testa_riga(x, j, voc, D)
        for k, w in enumerate(x['parole']):
            if k:
                seq.append(i[' '])
            seq += [i[u] for u in D(w)]
        seq.append(i['\n'])
    return seq


# ---------------------------------------------------------------- rete

def avvia_processo():
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def costruisci_rete(V, strati=None, nascosto=None):
    import torch.nn as nn

    class Rete(nn.Module):
        def __init__(self):
            super().__init__()
            self.emb = nn.Embedding(V, EMB)
            self.gru = nn.GRU(EMB, nascosto or NASCOSTO, strati or STRATI, batch_first=True,
                              dropout=CADUTA if (strati or STRATI) > 1 else 0.0)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(nascosto or NASCOSTO, V)

        def forward(self, x, h=None):
            y, h = self.gru(self.emb(x), h)
            return self.out(self.caduta(y)), h

    return Rete()


def _tensori(seqs, primo):
    import torch
    L = max(len(s) for s in seqs)
    X = torch.zeros((len(seqs), L - 1), dtype=torch.long)
    Y = torch.zeros((len(seqs), L - 1), dtype=torch.long)
    for b, s in enumerate(seqs):
        X[b, :len(s) - 1] = torch.tensor(s[:-1])
        Y[b, :len(s) - 1] = torch.tensor(s[1:])
    M = (Y >= primo).float()          # perdita solo sui segni da indovinare (contenuto, spazio, fine riga)
    return X, Y, M


def bpc(m, seqs, primo):
    """Bit per segno (contenuto, spazi e fine riga) sulle pagine date, stato dall'inizio della pagina."""
    import torch
    import torch.nn.functional as F
    m.eval()
    tot, n = 0.0, 0.0
    ordine = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with torch.no_grad():
        for a in range(0, len(ordine), LOTTO):
            X, Y, M = _tensori([seqs[i] for i in ordine[a:a + LOTTO]], primo)
            logit, _ = m(X)
            ce = F.cross_entropy(logit.reshape(-1, logit.shape[-1]), Y.reshape(-1), reduction='none')
            tot += float((ce * M.reshape(-1)).sum())
            n += float(M.sum())
    m.train()
    return tot / n / math.log(2)


def nome_modello(piega, replica=0):
    """'tutto' oppure 'k_r': piega k (0-4), replica r (0-1: stesso taglio, seme di addestramento diverso)."""
    return 'tutto' if piega == 'tutto' else '%d_%d' % (piega, replica)


def replica_del_libro(i, n):
    """I libri 1..n/2 sono scritti dai modelli della replica 0, gli altri da quelli della replica 1 (a metà, non pari e
    dispari: il controllo negativo con/senza confronta i semi dispari con i pari)."""
    return 0 if i <= n // 2 else 1


def addestra(piega, replica=0):
    """Addestra il modello della piega (0-4) e replica (0-1) o 'tutto'; salva il migliore sulla validazione (per
    'tutto': dopo il numero di epoche mediano dei 10 modelli delle pieghe)."""
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    inizio = time.time()
    righe, voc, D = libro_vero(), vocabolario(), divisore()
    pp = per_pagina(righe)
    f_add, f_val, f_fuori = fogli_della_piega(piega)
    seq_di = lambda ff: [sequenza(r, voc, D) for p, r in pp.items() if r[0]['foglio'] in set(ff)]
    add, val, fuori = seq_di(f_add), seq_di(f_val), seq_di(f_fuori)
    primo, V = voc['primo_contenuto'], len(voc['segni'])
    nome = nome_modello(piega, replica)
    seme = 7099 if piega == 'tutto' else 7000 + 100 * replica + piega
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci_rete(V)
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    if piega == 'tutto':
        epoche_fisse = int(statistics.median(json.load(open(percorso_modello(nome_modello(k, r), '.json'), encoding='utf-8'))['epoca_scelta']
                                             for k in range(PIEGHE) for r in range(REPLICHE)))
        massimo = epoche_fisse
    else:
        epoche_fisse, massimo = None, EPOCHE_MAX
    curva_val, curva_add, migliore, stato_migliore = [], [], None, None
    for epoca in range(1, massimo + 1):
        chiavi = [len(s) * (1 + 0.3 * u) for s, u in zip(add, rng.uniform(size=len(add)))]
        ordine = sorted(range(len(add)), key=lambda i: chiavi[i])
        lotti = [ordine[a:a + LOTTO] for a in range(0, len(ordine), LOTTO)]
        rng.shuffle(lotti)
        perdita, conti = 0.0, 0.0
        for lotto in lotti:
            X, Y, M = _tensori([add[i] for i in lotto], primo)
            h = None
            for t0 in range(0, X.shape[1], TRONCO):
                x, y, mk = X[:, t0:t0 + TRONCO], Y[:, t0:t0 + TRONCO], M[:, t0:t0 + TRONCO]
                logit, h = m(x, h)
                h = h.detach()
                if float(mk.sum()) == 0:
                    continue
                ce = F.cross_entropy(logit.reshape(-1, V), y.reshape(-1), reduction='none')
                loss = (ce * mk.reshape(-1)).sum() / mk.sum()
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
                opt.step()
                perdita += loss.item() * float(mk.sum())
                conti += float(mk.sum())
        curva_add.append(round(perdita / conti / math.log(2), 5))
        if val:
            v = round(bpc(m, val, primo), 5)
            curva_val.append(v)
            if migliore is None or v < migliore:
                migliore = v
                stato_migliore = {k: t.detach().clone() for k, t in m.state_dict().items()}
            if epoca % 10 == 0:
                print('  piega %s, epoca %d: validazione %.4f (migliore %.4f), %.0f s' % (piega, epoca, v, migliore, time.time() - inizio), flush=True)
            if len(curva_val) - 1 - curva_val.index(min(curva_val)) >= PAZIENZA:
                break
    if stato_migliore is not None:
        m.load_state_dict(stato_migliore)
    scelta = (curva_val.index(min(curva_val)) + 1) if curva_val else massimo
    ris = OrderedDict([('lavoro', 'addestra|%s' % ('tutto' if piega == 'tutto' else '%d|%d' % (piega, replica))), ('piega', piega), ('replica', replica), ('seme', seme), ('fogli', [len(f_add), len(f_val), len(f_fuori)]),
                       ('pagine', [len(add), len(val), len(fuori)]), ('segni_addestramento', sum(len(s) for s in add)),
                       ('parametri', sum(p.numel() for p in m.parameters())), ('epoche', len(curva_add)), ('epoca_scelta', scelta),
                       ('arrivata_al_massimo', epoche_fisse is None and len(curva_add) == EPOCHE_MAX and scelta > EPOCHE_MAX - PAZIENZA),
                       ('curva_validazione', curva_val), ('curva_addestramento', curva_add),
                       ('bpc_addestramento', round(bpc(m, add, primo), 5)), ('bpc_validazione', round(bpc(m, val, primo), 5) if val else None),
                       ('bpc_fuori', round(bpc(m, fuori, primo), 5) if fuori else None), ('secondi', round(time.time() - inizio, 1))])
    if fuori:
        ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    os.makedirs(MODELLI, exist_ok=True)
    torch.save(dict(stato=m.state_dict(), segni=voc['segni'], strati=STRATI, nascosto=NASCOSTO), percorso_modello(nome, '.pt'))
    json.dump(ris, open(percorso_modello(nome, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def percorso_modello(nome, est):
    return os.path.join(MODELLI, 'ia07_modello_%s%s' % (nome, est))


def carica_modello(nome):
    """nome: 'k_r' o 'tutto' (nome_modello)."""
    if ('modello', nome) not in _C:
        import torch
        d = torch.load(percorso_modello(nome, '.pt'))
        voc = vocabolario()
        assert d['segni'] == voc['segni'], 'vocabolario diverso da quello del modello'
        m = costruisci_rete(len(voc['segni']), d['strati'], d['nascosto'])
        m.load_state_dict(d['stato'])
        m.eval()
        _C[('modello', nome)] = m
    return _C[('modello', nome)]


# ---------------------------------------------------------------- scrivere e leggere una pagina

class Penna:
    """La rete passo per passo, con le regole di scrittura. Chi scrive e chi legge usano questa stessa classe e le
    stesse chiamate: le probabilità intere sono identiche bit per bit (un thread, stesse operazioni)."""

    def __init__(self, m, voc):
        self.m, self.voc = m, voc
        self.D = divisore()
        i = voc['idx']
        self.SP, self.EOL = i[' '], i['\n']
        self.unita = OrderedDict((i[u], u) for u in voc['unita'])
        self.tutti = [self.SP, self.EOL] + list(self.unita)
        self.senza_sp = list(self.unita)
        multi = [u for u in voc['unita'] if len(u) > 1]
        self.continua = {c for u in multi for c in u[1:]}

    def inizia(self):
        self.h = None

    def dai(self, tok):
        import torch
        with torch.inference_mode():
            logit, self.h = self.m(torch.tensor([[tok]], dtype=torch.long), self.h)
        self.ultimo = logit[0, -1].tolist()

    def ammessi(self, parola, lung, prima):
        """Segni ammessi: niente spazio o fine riga a inizio riga e dopo uno spazio; riga troppo lunga: fine riga;
        niente segno che, attaccato alla parola, la farebbe ridividere in modo diverso (es. c + h = ch)."""
        if prima in ('inizio', 'spazio'):
            base = self.senza_sp
        elif lung >= self.voc['lmax']:
            return [self.EOL]
        else:
            base = self.tutti
        if not parola:
            return base
        w = ''.join(parola)
        return [t for t in base if t not in self.unita or self.unita[t][0] not in self.continua
                or self.D(w + self.unita[t]) == parola + [self.unita[t]]]

    def distribuzione(self, amm):
        return st.softmax_interi([self.ultimo[t] for t in amm])


def percorri_pagina(penna, righe_pag, scelta):
    """Scrive (o rilegge) una pagina con la disposizione di righe_pag. scelta(riga, amm, cum) -> segno."""
    voc, D = penna.voc, penna.D
    penna.inizia()
    for t in testa_pagina(righe_pag, voc):
        penna.dai(t)
    out = []
    for j, x in enumerate(righe_pag):
        for t in testa_riga(x, j, voc, D):
            penna.dai(t)
        parola, parole, lung, prima = [], [], 0, 'inizio'
        while True:
            amm = penna.ammessi(parola, lung, prima)
            s = scelta(j, amm, penna.distribuzione(amm))
            penna.dai(s)
            if s == penna.EOL:
                parole.append(''.join(parola))
                break
            lung += 1
            if s == penna.SP:
                parole.append(''.join(parola))
                parola, prima = [], 'spazio'
            else:
                parola.append(penna.unita[s])
                prima = 'segno'
        out.append((x['pagina'], x['ini'], parole))
    return out


def scrivi_libro(modello_di, fonte):
    """modello_di: pagina -> piega del modello che la scrive. -> (righe [(pagina, ini, parole)], bit letti)."""
    righe, voc = libro_vero(), vocabolario()
    sc = st.Scrittore(fonte)
    out = []
    for pag, rp in per_pagina(righe).items():
        penna = Penna(carica_modello(modello_di(pag)), voc)
        out += percorri_pagina(penna, rp, lambda j, amm, cum: amm[sc.scegli(cum)])
    return out, sc.letti


def leggi_libro(modello_di, testo_righe):
    """Dai segni del libro ai bit che li hanno scelti (codifica aritmetica). None se il libro non è scrivibile dal modello."""
    righe, voc = libro_vero(), vocabolario()
    le = st.Lettore()
    D = divisore()
    i = voc['idx']
    gen = OrderedDict()
    for pag, ini, ps in testo_righe:
        gen.setdefault(pag, []).append(ps)
    for pag, rp in per_pagina(righe).items():
        penna = Penna(carica_modello(modello_di(pag)), voc)
        segni = []
        for ps in gen[pag]:
            seq = []
            for k, w in enumerate(ps):
                if k:
                    seq.append(i[' '])
                seq += [i[u] for u in D(w)]
            seq.append(i['\n'])
            segni.append(iter(seq))

        def scelta(j, amm, cum):
            s = next(segni[j])
            if s not in amm:
                raise ValueError('segno non ammesso')
            le.codifica(cum, amm.index(s))
            return s
        try:
            percorri_pagina(penna, rp, scelta)
        except (ValueError, StopIteration):
            return None
    return le.bit


def modello_onesto(replica=0):
    pg = pieghe()
    return lambda pag: nome_modello(pg[foglio_di(pag)], replica)


def scrivi_file(t, percorso, titolo, replica=None):
    """Formato del voynichizzatore (letto anche da voynichizzatore/pagine.py): '@<pagina.riga> parola.parola'. I
    separatori (. @ < > e lo spazio) non possono comparire nelle parole: le parole sono fatte solo di lettere
    (controllo in vocabolario() all'avvio e qui, parola per parola)."""
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# %s\n# Una riga per riga del libro; le righe che iniziano un paragrafo hanno il segno @ prima della pagina.\n' % titolo)
        if replica is not None:
            f.write('# replica dei modelli: %d\n' % replica)
        num = Counter()
        for pag, ini, ps in t:
            num[pag] += 1
            if not all(w and w.isalpha() for w in ps):
                raise SystemExit('parola con segni non alfabetici in %s: il formato del libro non la può scrivere' % pag)
            f.write('%s<%s.%d> %s\n' % ('@' if ini else '', pag, num[pag], '.'.join(ps)))


def replica_del_file(percorso):
    for l in open(percorso, encoding='utf-8'):
        if l.startswith('# replica dei modelli:'):
            return int(l.split(':')[1])
    return 0


def leggi_file(percorso):
    out = []
    for l in open(percorso, encoding='utf-8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#'):
            continue
        ini = l.startswith('@')
        locus, _, corpo = l.lstrip('@').partition('> ')
        out.append((locus.strip('<').rsplit('.', 1)[0], ini, corpo.split('.') if corpo else []))
    return out


# ---------------------------------------------------------------- giudici e misure

def pagine_di(rr):
    """Come e232.pagine_di."""
    import trascrizione
    out = OrderedDict()
    for pag, _, ps in rr:
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            out.setdefault(pag, []).append(ps)
    return out


def righe_ini(rr):
    """Come e251.righe_ini."""
    out = OrderedDict()
    for pag, ini, ps in rr:
        out.setdefault(pag, []).append((bool(ini), ps))
    return out


def riferimenti():
    """Pagine vere e riferimenti dei due giudici, come in e251._prepara (Voynich) o dal libro latino (controlli)."""
    if 'rif' in _C:
        return _C['rif']
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    if SOLO_CONTROLLI:
        righe = libro_vero()
        vpag, vi = OrderedDict(), OrderedDict()
        for x in righe:
            vpag.setdefault(x['pagina'], [x['lingua'], []])[1].append(list(x['parole']))
            vi.setdefault(x['pagina'], [x['lingua'], []])[1].append((x['ini'], list(x['parole'])))
    else:
        vpag, vi = e231.voynich(), e266.voynich_ini()
    rif = e231.riferimenti(vpag)
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    _C['rif'] = dict(vpag=vpag, rif=rif, rif266=rif266, vt266=vt266)
    return _C['rif']


def giudica(t, nome_tabella=None):
    import numpy as np
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    k = riferimenti()
    d231 = e231.confronto(k['vpag'], pagine_di(t), k['rif'])
    tab = e266.tabella(righe_ini(t), k['rif266'])
    d266 = e266.confronto(k['vt266'], tab)
    if nome_tabella:
        np.savez(nome_tabella, nomi=np.array(tab[0]), X=tab[1], nf=np.array(tab[2]))
    return OrderedDict([('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('pesanti_e231', d231['piu_pesanti'][:6]),
                        ('AUC_e266', d266['AUC']), ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti'][:8]),
                        ('pagine_giudicate', d266['pagine'])])


def pagella(t):
    """Pagella dell'e224 (con il cancello della riga) e pagella estesa dell'e293, come in e409. Solo sul Voynich."""
    import e251_lessico_sezione as e251
    import e293_banco as e293
    k = e251._prepara()
    if 'estesa_V' not in _C:
        _C['estesa_V'] = e293.pagella_estesa(come_rr(libro_vero()))
    pg = e251.pagella_grezza(k['c'], t)
    est = e293.pagella_estesa(t)
    passate = [m for m in e293.FASCE if e293.passa(m, est[m], _C['estesa_V'])]
    return OrderedDict([('pagella', pg['pagella']), ('riga', bool(pg['riga'])), ('mancano', pg['mancano']),
                        ('estese_passate', len(passate)), ('estese_mancate', [m for m in e293.FASCE if m not in passate])])


def ngrammi(righe_parole, n):
    return [tuple(r[i:i + n]) for r in righe_parole for i in range(len(r) - n + 1)]


def conti_copia(gen, add):
    """Conti (numeratore, denominatore) della copia: gen e add sono liste di righe (liste di parole)."""
    out = OrderedDict()
    for n in (5, 3):
        visti = set(ngrammi(add, n))
        g = ngrammi(gen, n)
        out['%d-grammi' % n] = [sum(x in visti for x in g), len(g)]
    righe_add = {tuple(r) for r in add if len(r) >= 4}
    g = [tuple(r) for r in gen if len(r) >= 4]
    out['righe intere'] = [sum(r in righe_add for r in g), len(g)]
    voc = {w for r in add for w in r}
    g = [w for r in gen for w in r]
    out['parole nuove'] = [sum(w not in voc for w in g), len(g)]
    return out


def somma_conti(lista):
    out = OrderedDict()
    for c in lista:
        for k, (a, b) in c.items():
            out.setdefault(k, [0, 0])
            out[k][0] += a
            out[k][1] += b
    return out


def quote(c):
    return OrderedDict((k, a / b if b else None) for k, (a, b) in c.items())


def controllo_copia_vetrina(t):
    """Quanto del libro vetrina è copiato dal libro vero (che il modello 'tutto' ha letto). Solo conti e nomi di pagina,
    mai le parole: righe di almeno 3 parole identiche a una riga vera qualsiasi (e alla riga vera nello stesso posto),
    5-grammi di parole presenti nel libro vero, pagine intere identiche alla pagina vera; per pagina, righe copiate e
    5-grammi copiati, e l'elenco delle pagine senza nessuna riga e nessun 5-gramma copiato."""
    vere = libro_vero()
    righe_vere = {tuple(x['parole']) for x in vere if len(x['parole']) >= 3}
    cinque = set(ngrammi([x['parole'] for x in vere], 5))
    vp = OrderedDict()
    for x in vere:
        vp.setdefault(x['pagina'], []).append(tuple(x['parole']))
    gp = OrderedDict()
    for pag, _, ps in t:
        gp.setdefault(pag, []).append(tuple(ps))
    per_pagina_ = OrderedDict()
    tot = Counter()
    for pag, rr in gp.items():
        c = Counter()
        for j, r in enumerate(rr):
            if len(r) >= 3:
                c['righe'] += 1
                c['righe copiate'] += r in righe_vere
                c['righe copiate nello stesso posto'] += j < len(vp[pag]) and r == vp[pag][j]
            g = ngrammi([list(r)], 5)
            c['5-grammi'] += len(g)
            c['5-grammi copiati'] += sum(x in cinque for x in g)
        c['pagina intera identica'] = int(rr == vp[pag])
        per_pagina_[pag] = OrderedDict((k, c[k]) for k in ('righe', 'righe copiate', 'righe copiate nello stesso posto', '5-grammi',
                                                           '5-grammi copiati', 'pagina intera identica'))
        tot.update(c)
    pulite = [p for p, c in per_pagina_.items() if c['righe copiate'] == 0 and c['5-grammi copiati'] == 0]
    return OrderedDict([('totali', OrderedDict((k, tot[k]) for k in ('righe', 'righe copiate', 'righe copiate nello stesso posto', '5-grammi',
                                                                       '5-grammi copiati', 'pagina intera identica'))),
                        ('pagine', len(per_pagina_)), ('pagine_pulite', pulite),
                        ('pagine_con_copia', OrderedDict((p, c) for p, c in per_pagina_.items() if p not in set(pulite)))])


def copia_onesta(t):
    """Copia a memoria delle pagine t rispetto al testo d'addestramento del modello che le ha scritte (pieghe)."""
    righe = libro_vero()
    gen = OrderedDict()
    for pag, _, ps in t:
        gen.setdefault(foglio_di(pag), []).append(ps)
    conti = []
    for k in range(PIEGHE):
        f_add, _, f_fuori = fogli_della_piega(k)
        add = [x['parole'] for x in righe if x['foglio'] in set(f_add)]
        conti.append(conti_copia([r for f in f_fuori for r in gen.get(f, [])], add))
    return somma_conti(conti)


# ---------------------------------------------------------------- giudice A "sorpresa" (di IA1)
# Funzioni di ia01 importate (non copiate): codifica, pagine_da_righe, addestra_lm, sorprese, profilo, auc_logistico, appaiata,
# rimescola_parole, rimescola_righe, markov, seme_di, moduli. Qui solo la colla: contesto con le pieghe di IA7, modelli salvati,
# profili e AUC. Il contesto (pagine con almeno 40 parole, segni con frequenza almeno 0,1%) è quello di ia01.contesto(); le sole
# differenze sono le pieghe (vedi contesto_A) e la fonte delle pagine (libro_vero(), che in prova è il libro latino).

def contesto_A():
    """Pagine vere (almeno 40 parole), segni, sequenze e pieghe del giudice A. Le pieghe sono quelle dei generatori (per foglio,
    pieghe()): il modello del testo della piega k ha visto esattamente i fogli che il generatore della piega k ha visto (meno il
    10% di pagine per l'arresto) e non ha mai visto i fogli della piega k, dove si giudicano le pagine vere e quelle scritte da
    quel generatore. In ia01 le pieghe erano per pagina a caso (seme 3961)."""
    if 'ctxA' in _C:
        return _C['ctxA']
    D = divisore()
    vere = OrderedDict()
    for x in libro_vero():
        vere.setdefault(x['pagina'], []).append((bool(x['ini']), [tuple(D(w)) for w in x['parole']]))
    nomi = sorted(p for p, rows in vere.items() if sum(len(ws) for _, ws in rows) >= ia01.MIN_PAROLE)
    vere = OrderedDict((p, vere[p]) for p in nomi)
    conti = Counter(s for rows in vere.values() for _, ws in rows for w in ws for s in w)
    tot = sum(conti.values())
    voc = [ia01.SP, ia01.NL, ia01.PAR, ia01.RARO] + sorted(s for s, c in conti.items() if c / tot >= 0.001)
    idx = {s: i for i, s in enumerate(voc)}
    pg = pieghe()
    _C['ctxA'] = dict(vere=vere, voc=voc, idx=idx, V=len(voc), fold={p: pg[foglio_di(p)] for p in nomi},
                      ids={p: ia01.codifica(rows, idx) for p, rows in vere.items()})
    return _C['ctxA']


def coerenza_ia01():
    """Solo sul Voynich: pagine, segni e sequenze di contesto_A() sono quelli di ia01.contesto()? (Informativo: se fossero
    diversi il giudice A resterebbe valido, ma il ricalcolo del v21 non sarebbe sugli stessi testi di ia01.)"""
    if SOLO_CONTROLLI:
        return None
    import numpy as np
    try:
        a, b = contesto_A(), ia01.contesto()
        return OrderedDict([('pagine', [len(a['ids']), len(b['ids'])]), ('stesse_pagine', set(a['ids']) == set(b['ids'])),
                            ('stessi_segni', a['voc'] == b['voc']),
                            ('sequenze_uguali', sum(1 for p in a['ids'] if p in b['ids'] and np.array_equal(a['ids'][p], b['ids'][p])))])
    except Exception as e:
        return OrderedDict([('errore', repr(e))])


def percorso_lmA(seme, piega):
    return os.path.join(MODELLI_A, 'ia07_giudiceA_s%d_p%d.pt' % (seme, piega))


def lavoro_lmA(seme, piega):
    """Modello del testo del giudice A per piega e seme: addestrato sulle pagine vere delle altre pieghe (10% per l'arresto,
    come ia01.lavoro_A, stesso modo di scegliere la validazione e di fissare il seme, ma pieghe di IA7)."""
    import numpy as np
    import torch
    inizio = time.time()
    c = contesto_A()
    test = [p for p in c['ids'] if c['fold'][p] == piega]
    resto = [p for p in c['ids'] if c['fold'][p] != piega]
    random.Random(3964 + 100 * seme + piega).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([c['ids'][p] for p in ps])
    m, info = ia01.addestra_lm(flusso(add), flusso(val), c['V'], 1000 * seme + piega)
    os.makedirs(MODELLI_A, exist_ok=True)
    torch.save(dict(stato=m.state_dict(), V=c['V']), percorso_lmA(seme, piega))
    fuori = ia01.sorprese(m, [c['ids'][p] for p in test])
    ris = OrderedDict([('lavoro', 'lmA|%d|%d' % (seme, piega)), ('seme', seme), ('piega', piega), ('pagine', [len(add), len(val), len(test)])])
    ris.update(info)
    ris['bpc_vere_fuori'] = float(np.mean([np.mean(x) for x in fuori]))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def carica_lmA(seme, piega):
    if ('lmA', seme, piega) not in _C:
        import torch
        p = percorso_lmA(seme, piega)
        if not os.path.exists(p):
            raise RuntimeError('manca il modello del giudice A %s: va fatta prima la fase A' % p)
        d = torch.load(p)
        m = ia01.moduli()['LM'](d['V'])
        m.load_state_dict(d['stato'])
        m.eval()
        _C[('lmA', seme, piega)] = m
    return _C[('lmA', seme, piega)]


def profili_A(libro):
    """Profili di sorpresa (14 numeri, media sui semi) delle pagine di un libro (pagina -> righe, formato di ia01), ognuna dal
    modello della sua piega (che non ha visto il suo foglio)."""
    import numpy as np
    c = contesto_A()
    g = {p: ia01.codifica(rows, c['idx']) for p, rows in libro.items() if p in c['ids']}
    out = {}
    for piega in range(PIEGHE):
        ps = [p for p in g if c['fold'][p] == piega]
        if not ps:
            continue
        per_seme = []
        for seme in SEMI_A:
            s = ia01.sorprese(carica_lmA(seme, piega), [g[p] for p in ps])
            per_seme.append([ia01.profilo(g[p], x) for p, x in zip(ps, s)])
        for i, p in enumerate(ps):
            out[p] = np.mean([a[i] for a in per_seme], axis=0)
    return out


def profili_vere_A():
    if 'profA_vere' not in _C:
        _C['profA_vere'] = profili_A(contesto_A()['vere'])
    return _C['profA_vere']


def giudice_A(libro):
    """AUC del giudice A fra le pagine vere e quelle del libro (stesso nome di pagina), come ia01.analizza_A_coppia: regressione
    logistica sui profili, 10 pieghe per pagina, 5 ripetizioni, previsioni messe insieme. Più la differenza media del profilo
    (generato meno vero, 14 numeri, nell'ordine di ia01.CARATTERISTICHE). Solo numeri."""
    import numpy as np
    vp, gp = profili_vere_A(), profili_A(libro)
    pag = [p for p in vp if p in gp]
    if len(pag) < 10 or len(pag) < 0.99 * len(vp):
        return OrderedDict([('AUC_A', None), ('A_errore', 'pagine in comune: %d su %d' % (len(pag), len(vp)))])
    X = np.array([vp[p] for p in pag] + [gp[p] for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    a, pr = ia01.auc_logistico(X, y, pag + pag)
    n = len(pag)
    return OrderedDict([('AUC_A', float(a)), ('AUC_A_appaiata', float(ia01.appaiata(pr[:n], pr[n:]))), ('pagine_A', n),
                        ('diff_profilo_A', [float(v) for v in np.mean([gp[p] - vp[p] for p in pag], axis=0)])])


def libro_A_da_righe(t):
    """Libro scritto, [(pagina, inizio, parole)] -> formato di ia01 (come ia01.genera_libro per i libri v21)."""
    import trascrizione
    return ia01.pagine_da_righe(t, divisore(), trascrizione.pulita)


def libro_riferimento_A(lettera, k):
    """Libro v21 di ia01 con la chiave k ('a' con messaggio, 'b' senza), dalla cache di ia01 (gli stessi libri). Nelle prove (libro
    latino): una catena di Markov di caratteri di ordine 2, solo per far girare il percorso (non è il v21)."""
    if SOLO_CONTROLLI:
        return ia01.markov(contesto_A()['vere'], 2, ia01.seme_di('%s%d' % (lettera, k)))
    import pickle
    p = os.path.join(CACHE, 'ia01_libri', '%s%d.pkl' % (lettera, k))
    if not os.path.exists(p):
        raise RuntimeError('manca il libro v21 di ia01 %s: va fatto con ia01 (genera_libro)' % p)
    return pickle.load(open(p, 'rb'))


def libro_controllo_A(nome):
    """Controlli di ia01: parole rimescolate nella riga (seme 396001), righe rimescolate nella pagina (396002), generatore
    e192 (dalla cache di ia01; può mancare, come in ia01); nelle prove la catena di Markov di ordine 1 (come ia01)."""
    vere = contesto_A()['vere']
    if nome == 'parole':
        return ia01.rimescola_parole(vere, 396001)
    if nome == 'righe':
        return ia01.rimescola_righe(vere, 396002)
    if nome == 'ordine1':
        return ia01.markov(vere, 1, 396003)
    if nome == 'e192':
        import pickle
        p = os.path.join(CACHE, 'ia01_libri', 'e192.pkl')
        return pickle.load(open(p, 'rb')) if os.path.exists(p) else None
    raise ValueError(nome)


def negativo_A():
    """Pagine vere contro pagine vere con etichette a caso (5 etichette, come ia01.analizza_A_negativo)."""
    import numpy as np
    vp = profili_vere_A()
    aucs = []
    for s in SEMI_CASO:
        pag = list(vp)
        random.Random(3970 + s).shuffle(pag)
        y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
        aucs.append(float(ia01.auc_logistico(np.array([vp[p] for p in pag]), y, pag)[0]))
    return aucs


# ---------------------------------------------------------------- lavori

def lavoro(args):
    tipo = args[0]
    ident = '|'.join(str(a) for a in args)
    inizio = time.time()
    if tipo == 'addestra':
        return addestra(args[1], args[2] if len(args) > 2 else 0)
    if tipo == 'lmA':
        return lavoro_lmA(args[1], args[2])
    os.makedirs(LIBRI, exist_ok=True)
    if tipo == 'libro':
        caso, i = args[1], args[2]
        if caso == 'vetrina':
            replica = None
            modello_di, chiave = (lambda pag: 'tutto'), 'ia07-vetrina'
        else:
            replica = replica_del_libro(i, N_SENZA if caso == 'senza' else N_CON)
            modello_di, chiave = modello_onesto(replica), 'ia07-%d' % i
        messaggio = open(MESSAGGIO, encoding='utf-8').read().replace('\r\n', '\n')
        fonte = st.fonte_senza_messaggio(3003000 + i) if caso == 'senza' else st.fonte_con_messaggio(messaggio, chiave)
        t, letti = scrivi_libro(modello_di, fonte)
        cartella = VETRINA if caso == 'vetrina' else LIBRI
        os.makedirs(cartella, exist_ok=True)
        percorso = os.path.join(cartella, 'ia07_libro_%s_%d.txt' % (caso, i))
        scrivi_file(t, percorso, 'ia07, libro %s %d' % (caso, i), replica)
        t_file = leggi_file(percorso)
        assert t_file == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
        bit = leggi_libro(modello_di, t_file)
        ris = OrderedDict([('lavoro', ident), ('caso', caso), ('i', i), ('replica', replica), ('bit_usati', letti), ('capacita_bit', len(bit) if bit is not None else None),
                           ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                           ('segni_per_parola', statistics.mean(len(divisore()(w)) for _, _, ps in t for w in ps))])
        if caso != 'senza':
            ris['bit_messaggio'] = len(st.pacchetto(messaggio, chiave))
            ris['recupero_esatto'] = bit is not None and st.apri(bit, chiave) == messaggio
            ris['chiave_sbagliata_respinta'] = bit is None or st.apri(bit, chiave + 'x') is None
        ris.update(giudica(t, os.path.join(LIBRI, 'ia07_tabella_%s_%d.npz' % (caso, i))))
        if caso != 'vetrina':       # il modello "tutto" ha visto tutte le pagine: per il giudice A la vetrina non è una prova onesta
            try:
                ris.update(giudice_A(libro_A_da_righe(t)))
            except Exception as e:
                ris['A_errore'] = repr(e)
        if caso == 'vetrina':
            ris['copia'] = conti_copia([ps for _, _, ps in t], [x['parole'] for x in libro_vero()])
            ris['controllo_copia'] = controllo_copia_vetrina(t)
        else:
            ris['copia'] = copia_onesta(t)
        if PAGELLA:
            try:
                ris.update(pagella(t))
            except Exception as e:
                ris['pagella_errore'] = repr(e)
    elif tipo == 'O':
        import e400_scala_controlli as e400
        rr = come_rr(libro_vero())
        tipi = OrderedDict((x['pagina'], (x['sezione'], x['lingua'])) for x in libro_vero())
        t = e400.costruisci(args[1], args[2], rr, tipi)
        ris = OrderedDict([('lavoro', ident)])
        ris.update(giudica(t))
    elif tipo == 'rifA':
        # giudice A sui libri v21 di ia01 (chiave args[1]): senza messaggio (b, parallelo ai libri della rete) e con (a, quelli di ia01)
        ris = OrderedDict([('lavoro', ident), ('chiave', args[1])])
        for lettera in ('b', 'a'):
            r = giudice_A(libro_riferimento_A(lettera, args[1]))
            ris['AUC_A_' + lettera] = r['AUC_A']
            ris['AUC_A_appaiata_' + lettera] = r.get('AUC_A_appaiata')
            ris['diff_profilo_A_' + lettera] = r.get('diff_profilo_A')
    elif tipo == 'ctrlA':
        # controlli del giudice A, procedura di ia01: parole rimescolate nella riga, righe rimescolate nella pagina, e192 (o, nelle prove, Markov di ordine 1)
        libro = libro_controllo_A(args[1])
        ris = OrderedDict([('lavoro', ident), ('controllo', args[1])])
        if libro is None:
            ris.update(AUC_A=None, esito='libro del controllo non disponibile')
        else:
            ris.update(giudice_A(libro))
    elif tipo == 'casoA':
        aucs = negativo_A()
        ris = OrderedDict([('lavoro', ident), ('AUC_A', statistics.mean(aucs)), ('AUC_A_etichette', aucs), ('coerenza_ia01', coerenza_ia01())])
    elif tipo == 'caso':
        import numpy as np
        import e231_discriminatore as e231
        k = riferimenti()
        nv1, X1, _ = e231.caratteristiche(OrderedDict((p, rr) for p, (_, rr) in k['vpag'].items()), k['rif'])
        nv2, X2, _ = k['vt266']
        ris = OrderedDict([('lavoro', ident)])
        for nome, nv, X in (('e231', nv1, X1), ('e266', nv2, X2)):
            aucs = []
            for s in SEMI_CASO:
                y = np.array([1] * (len(nv) // 2) + [0] * (len(nv) - len(nv) // 2))
                random.Random(s).shuffle(y)
                aucs.append(e231.auc_cv(X, y, np.array([foglio_di(p) for p in nv]), semi=(s,)))
            ris['AUC_%s' % nome] = statistics.mean(aucs)
            ris['AUC_%s_semi' % nome] = aucs
    else:
        raise ValueError(tipo)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def esegui(lavori, processi, percorso, fatte):
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte]
    if not da_fare:
        return []
    out = []
    inizio = time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            fatte.add(r['lavoro'])
            breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'bpc_fuori', 'scarto', 'AUC_e231', 'AUC_e266', 'AUC_A', 'A_errore',
                                       'AUC_A_b', 'AUC_A_a', 'passi', 'bpc_vere_fuori', 'capacita_bit',
                                       'recupero_esatto', 'chiave_sbagliata_respinta', 'pagella', 'pagella_errore') if x in r}
            print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
    return out


# ---------------------------------------------------------------- immagini della vetrina

def immagini(percorso_libro, cartella, pulite, quante=4):
    """Alcune pagine del libro vetrina in PNG con il carattere del voynichizzatore (voynichizzatore/pagine.py, importato
    senza modifiche): la prima pagina di erbario, biologia, ricette e farmacia con almeno 10 righe fra quelle senza
    righe né 5-grammi copiati dal libro vero (pulite). Restano in dati/cache: la pubblicazione la decide Davide."""
    import pagine as vzp
    os.makedirs(cartella, exist_ok=True)
    righe = [l for l in open(percorso_libro, encoding='utf-8') if l.strip() and not l.startswith('#')]
    per = OrderedDict()
    for l in righe:
        per.setdefault(l.lstrip('@').split('>')[0].strip('<').rsplit('.', 1)[0], []).append(l)
    sez = OrderedDict((x['pagina'], x['sezione']) for x in libro_vero())
    scelte = []
    for s in ('H', 'B', 'S', 'P'):
        p = next((p for p in per if sez.get(p) == s and len(per[p]) >= 10 and p in set(pulite)), None)
        if p:
            scelte.append(p)
    out = []
    for p in scelte[:quante]:
        tmp = os.path.join(cartella, '_pagina.txt')
        open(tmp, 'w', encoding='utf-8', newline='\n').write(''.join(per[p]))
        png = os.path.join(cartella, 'ia07_vetrina_%s.png' % p)
        vzp.pdf(tmp, os.path.join(cartella, '_pagina.pdf'), quante=1, stampa=False, immagine=png)
        os.remove(tmp)
        os.remove(os.path.join(cartella, '_pagina.pdf'))
        out.append((os.path.basename(png), os.path.getsize(png)))
    return out


# ---------------------------------------------------------------- sintesi

def media_es(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None, None
    return statistics.mean(xs), (statistics.stdev(xs) / len(xs) ** 0.5 if len(xs) > 1 else None)


def confronto_v21(m, es, ref):
    v, ev = ref
    d = m - v
    ec = math.sqrt((es or 0) ** 2 + ev ** 2)
    lettura = 'più vicino al vero del v21' if d < -2 * ec else 'più lontano dal vero del v21' if d > 2 * ec else 'uguale al v21 entro l\'errore'
    return OrderedDict([('media', m), ('errore', es), ('v21', v), ('differenza', d), ('errore_differenza', ec), ('lettura', lettura)])


def con_senza(per_libro):
    """Pagine dei libri con messaggio contro quelle dei libri senza (giudice 2, pieghe per libro, come e419); controllo
    negativo: libri senza, semi dispari contro pari. per_libro: [(caso, i, replica)].
    Prima del classificatore a ogni caratteristica si toglie la media della replica dei modelli che ha scritto il libro
    (calcolata sui libri di quella replica nel confronto): le due repliche sono presenti in egual misura nelle due classi,
    ma le pieghe per libro le sbilanciano, e senza questa correzione il classificatore impara la replica e la sbaglia
    nella piega di prova (AUC sotto 0,5; visto nella prova sul latino)."""
    import numpy as np
    import e231_discriminatore as e231
    import e419_con_senza_messaggio as e419
    tab, rep = {}, {}
    for caso, i, r in per_libro:
        d = np.load(os.path.join(LIBRI, 'ia07_tabella_%s_%d.npz' % (caso, i)))
        tab[(caso, i)] = (d['X'], [str(x) for x in d['nf']])
        rep[(caso, i)] = r

    def centra(chiavi):
        X = np.vstack([tab[k][0] for k in chiavi])
        r = np.array([rep[k] for k in chiavi for _ in tab[k][0]])
        X = X.astype(float).copy()
        for v in set(r.tolist()):
            X[r == v] -= X[r == v].mean(axis=0)
        return X

    senza = sorted(i for c, i in tab if c == 'senza')
    con = sorted(i for c, i in tab if c == 'con')
    vecchie = e231.PIEGHE
    try:
        e231.PIEGHE = max(2, min(10, len(senza), len(con)))
        nf = next(iter(tab.values()))[1]
        chiavi = [('con', i) for i in con] + [('senza', i) for i in senza]
        X = centra(chiavi)
        y = np.array([1 if c == 'con' else 0 for c, i in chiavi for _ in tab[(c, i)][0]])
        g = np.array([(1000 + i if c == 'con' else i) for c, i in chiavi for _ in tab[(c, i)][0]])
        diretto, per_gruppo = e419.auc_gruppi(X, y, g, nf)
        neg = None
        if len(senza) >= 4:
            e231.PIEGHE = max(2, min(10, len(senza) // 2))
            cb = [('senza', i) for i in senza]
            Xb = centra(cb)
            yb = np.array([i % 2 for i in senza for _ in tab[('senza', i)][0]])
            gb = np.array([i for i in senza for _ in tab[('senza', i)][0]])
            neg = e419.auc_gruppi(Xb, yb, gb, nf)[0]
    finally:
        e231.PIEGHE = vecchie
    return OrderedDict([('AUC_diretta', diretto), ('per_gruppo', per_gruppo), ('pagine', int(len(y))),
                        ('controllo_negativo_dispari_pari', neg), ('centrato_per_replica', True)])


def copia_riferimenti():
    """Riferimento naturale: le pagine vere tenute fuori contro il testo d'addestramento della loro piega. Più il libro
    d'esempio del v21 (solo sul Voynich) con le stesse pieghe."""
    righe = libro_vero()
    out = OrderedDict([('naturale', copia_onesta(come_rr(righe)))])
    if not SOLO_CONTROLLI:
        try:
            percorso = os.path.join(QUI, '..', 'white_paper', 'en', 'figure', 'libro_esempio_v21.txt')
            v21 = [(l.lstrip('@').split('>')[0].strip('<').rsplit('.', 1)[0], l.startswith('@'), [w for w in l.split('>', 1)[1].strip().split('.') if w])
                   for l in open(percorso, encoding='utf-8') if l.strip() and not l.startswith('#') and '>' in l]
            out['v21 (libro d\'esempio)'] = copia_onesta(v21)
        except Exception as e:
            print('copia del v21 non calcolata: %r' % e, flush=True)
    return out


def leggi_corse(percorso):
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()] if os.path.exists(percorso) else []


def media_diff(liste):
    """Media, misura per misura, delle differenze di profilo (generato meno vero) di più libri."""
    liste = [l for l in liste if l]
    if not liste:
        return None
    return OrderedDict((n, statistics.mean(l[j] for l in liste)) for j, n in enumerate(ia01.CARATTERISTICHE))


def lettura_A(rs, lettera, rifA, invalida):
    """Giudice A sui libri della rete (rs) contro il v21 ricalcolato con lo stesso giudice (lettera 'b' senza messaggio, 'a' con).
    Stessa regola delle letture dei giudici 1 e 2 (2 errori); in più la lettura assoluta (soglie di ia01) e la nota sulla
    circolarità: un esito "più vicino al v21" non è conclusivo, gli altri reggono anche col vantaggio della rete."""
    ok = [r for r in rs if r.get('AUC_A') is not None]
    if not ok:
        return None
    m, es = media_es([r['AUC_A'] for r in ok])
    rif = [r['AUC_A_' + lettera] for r in rifA if r.get('AUC_A_' + lettera) is not None]
    g = OrderedDict([('libri', len(ok)), ('libri_senza_A', len(rs) - len(ok))])
    if rif:
        mv, ev = media_es(rif)
        g.update(confronto_v21(m, es, (mv, ev or 0.0)))
        g['v21_libri'] = len(rif)
    else:
        g.update(media=m, errore=es, lettura='v21 ricalcolato non disponibile')
    g['min_max'] = [min(r['AUC_A'] for r in ok), max(r['AUC_A'] for r in ok)]
    g['per_replica'] = OrderedDict((str(rp), media_es([r['AUC_A'] for r in ok if r.get('replica') == rp])) for rp in range(REPLICHE))
    pr = list(g['per_replica'].values())
    if len(pr) == 2 and all(x[0] is not None and x[1] is not None for x in pr):
        g['repliche_diverse'] = abs(pr[0][0] - pr[1][0]) > 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)
    g['lettura_assoluta'] = ('la rete regge (giudice A al di sotto di %s)' % nu(LETTURA_A[0], 2) if m <= LETTURA_A[0] else
                             'giudice A vede la differenza (sopra %s)' % nu(LETTURA_A[1], 2) if m > LETTURA_A[1] else 'zona grigia')
    g['nota_circolarita'] = ('NON conclusivo: un giudice che è una rete addestrata sullo stesso testo vede il testo della rete come atteso; '
                             'si legge solo insieme ai giudici 1 e 2' if g['lettura'].startswith('più vicino') else
                             'regge anche col vantaggio che la circolarità dà alla rete' if g['lettura'].startswith(('più lontano', 'uguale')) else None)
    if invalida:
        g['lettura'] = g['lettura_assoluta'] = invalida
        g['nota_circolarita'] = None
    g['diff_profilo'] = media_diff([r.get('diff_profilo_A') for r in ok])
    return g


def sintesi(versioni, immagini_fatte):
    corse = {c['lavoro']: c for c in leggi_corse(os.path.join(USCITA, 'ia07_corse.jsonl'))}
    modelli = [corse['addestra|%d|%d' % (k, r)] for r in range(REPLICHE) for k in range(PIEGHE) if 'addestra|%d|%d' % (k, r) in corse]
    senza = [corse['libro|senza|%d' % i] for i in range(1, N_SENZA + 1) if 'libro|senza|%d' % i in corse]
    con = [corse['libro|con|%d' % i] for i in range(1, N_CON + 1) if 'libro|con|%d' % i in corse]
    vetrina = corse.get('libro|vetrina|0')
    O = OrderedDict((g, [corse['O|%s|%d' % (g, s)] for s in SEMI_O if 'O|%s|%d' % (g, s) in corse]) for g in ('O1', 'O2'))
    caso = corse.get('caso|0')
    rifA = [corse['rifA|%d' % k] for k in CHIAVI_V21 if 'rifA|%d' % k in corse]
    ctrlA = {n: corse['ctrlA|%s' % n] for n in NOMI_CTRL_A if 'ctrlA|%s' % n in corse}
    casoA = corse.get('casoA|0')
    modelliA = [corse['lmA|%d|%d' % (s, k)] for s in SEMI_A for k in range(PIEGHE) if 'lmA|%d|%d' % (s, k) in corse]

    # controlli
    pos = statistics.mean(r['AUC_e266'] for r in O['O2']) if O['O2'] else None
    controlli = OrderedDict()
    controlli['positivo'] = OrderedDict([('che cosa', 'giudice 2 sul libro vero con le parole rimescolate nella riga (O2, semi %s)' % list(SEMI_O)),
                                         ('AUC', pos), ('soglia', SOGLIA_POSITIVO), ('riuscito', pos is not None and pos >= SOGLIA_POSITIVO)])
    controlli['negativo'] = OrderedDict([('che cosa', 'pagine vere con etichette a caso (pieghe per foglio, semi %s)' % list(SEMI_CASO)),
                                         ('AUC_e231', caso and caso['AUC_e231']), ('AUC_e266', caso and caso['AUC_e266']), ('intervallo', NEGATIVO),
                                         ('riuscito', bool(caso) and all(NEGATIVO[0] <= caso[k] <= NEGATIVO[1] for k in ('AUC_e231', 'AUC_e266')))])
    tutti_con = con + ([vetrina] if vetrina else [])
    controlli['recupero'] = OrderedDict([('che cosa', 'messaggio riletto esatto e chiave sbagliata respinta, libri con messaggio'),
                                         ('esatti', sum(bool(r['recupero_esatto']) for r in tutti_con)),
                                         ('respinti', sum(bool(r['chiave_sbagliata_respinta']) for r in tutti_con)), ('libri', len(tutti_con)),
                                         ('riuscito', bool(tutti_con) and all(r['recupero_esatto'] and r['chiave_sbagliata_respinta'] for r in tutti_con))])
    cs = con_senza([('senza', r['i'], r.get('replica', 0)) for r in senza] + [('con', r['i'], r.get('replica', 0)) for r in con]) if senza and con else None
    if cs:
        neg = cs['controllo_negativo_dispari_pari']
        controlli['negativo_con_senza'] = OrderedDict([('che cosa', 'libri senza messaggio, semi dispari contro pari (giudice 2, pieghe per libro)'),
                                                       ('AUC', neg), ('intervallo', NEGATIVO),
                                                       ('riuscito', neg is not None and NEGATIVO[0] <= neg <= NEGATIVO[1])])

    # controlli del giudice A (procedura di ia01, ricalcolata qui con le pieghe di IA7: i numeri di ia01 non valgono per questo giudice)
    pos_A = OrderedDict((n, ctrlA[n].get('AUC_A') if n in ctrlA else None) for n in NOMI_CTRL_A if n != 'righe')
    controlli['positivo_A'] = OrderedDict([('che cosa', 'giudice A: libro vero con le parole rimescolate nella riga (seme 396001) e %s' % (
        'catena di Markov di ordine 1 (prova)' if SOLO_CONTROLLI else 'generatore e192 (se manca, vale il primo, dichiarato)')),
        ('AUC', pos_A), ('soglia', SOGLIA_POSITIVO_A),
        ('riuscito', pos_A.get('parole') is not None and all(v >= SOGLIA_POSITIVO_A for v in pos_A.values() if v is not None))])
    nA = casoA['AUC_A'] if casoA else None
    controlli['negativo_A'] = OrderedDict([('che cosa', 'giudice A: pagine vere con etichette a caso (media di %d etichette)' % len(SEMI_CASO)),
                                           ('AUC', nA), ('AUC_etichette', casoA and casoA['AUC_A_etichette']), ('intervallo', NEGATIVO),
                                           ('riuscito', nA is not None and NEGATIVO[0] <= nA <= NEGATIVO[1])])

    # validità delle letture: se un controllo fallisce i numeri restano, la lettura no
    falliti = lambda nomi: [n for n in nomi if n in controlli and not controlli[n]['riuscito']] + [n for n in nomi if n not in controlli]
    non_valida = lambda nomi: ('lettura non valida (controllo %s fallito o mancante)' % ', '.join(falliti(nomi))) if falliti(nomi) else None

    # giudici
    giudici = OrderedDict()
    for nome, rs in (('senza messaggio', senza), ('con messaggio', con)):
        if not rs:
            continue
        g = OrderedDict([('libri', len(rs))])
        for k in ('AUC_e231', 'AUC_e266'):
            m, es = media_es([r[k] for r in rs])
            g[k] = confronto_v21(m, es, V21[k])
            g[k]['min_max'] = [min(r[k] for r in rs), max(r[k] for r in rs)]
            g[k]['per_replica'] = OrderedDict((str(rp), media_es([r[k] for r in rs if r.get('replica') == rp])) for rp in range(REPLICHE))
            pr = list(g[k]['per_replica'].values())
            if len(pr) == 2 and all(x[0] is not None and x[1] is not None for x in pr):
                lim = 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)
                g[k]['repliche_diverse'] = abs(pr[0][0] - pr[1][0]) > lim
                if g[k]['repliche_diverse']:
                    g[k]['lettura'] += ' (le due repliche dei modelli differiscono più di 2 errori)'
            if non_valida(('positivo', 'negativo')):
                g[k]['lettura'] = non_valida(('positivo', 'negativo'))
        g['A'] = lettura_A(rs, 'b' if nome == 'senza messaggio' else 'a', rifA, non_valida(('positivo_A', 'negativo_A')))
        g['gruppi_e266'] = OrderedDict((n, statistics.mean(r['gruppi_e266'][n] for r in rs)) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)
        g['pagine_giudicate'] = statistics.mean(r['pagine_giudicate'] for r in rs)
        if all('pagella' in r for r in rs):
            g['pagella'] = statistics.mean(r['pagella'] for r in rs)
            g['cancello_riga'] = sum(r['riga'] for r in rs)
            g['estese'] = statistics.mean(r['estese_passate'] for r in rs)
            g['materie_mancate'] = OrderedDict(Counter(m for r in rs for m in r['mancano'] + r['estese_mancate']).most_common())
        g['pesanti_e266'] = rs[0]['pesanti_e266']
        giudici[nome] = g
    differenze = OrderedDict()
    if senza and con:
        # libri con e senza non sono appaiati (semi di campionamento diversi): differenza delle medie, errori sommati in quadratura
        for k in ('AUC_e231', 'AUC_e266') + (('pagella',) if all('pagella' in r for r in con + senza) else ()):
            (mc, ec), (ms, es_) = media_es([r[k] for r in con]), media_es([r[k] for r in senza])
            differenze[k] = OrderedDict([('differenza', mc - ms), ('errore', math.sqrt((ec or 0) ** 2 + (es_ or 0) ** 2)),
                                         ('libri', [len(con), len(senza)])])

    # copia a memoria
    rif_copia = copia_riferimenti()
    copia = OrderedDict()
    for nome, rs in (('senza messaggio', senza), ('con messaggio', con)):
        if rs:
            qs = [quote(r['copia']) for r in rs]
            copia[nome] = OrderedDict((k, media_es([q[k] for q in qs])) for k in qs[0])
    letture_copia = OrderedDict()
    if senza:
        nat = quote(rif_copia['naturale'])
        for k in ('5-grammi', 'righe intere'):
            m, es = copia['senza messaggio'][k]
            if m is None or nat[k] is None:
                letture_copia[k] = OrderedDict([('generato', m), ('errore', es), ('naturale', nat[k]), ('differenza', None),
                                                ('lettura', 'non calcolabile (nessun n-gramma o riga da contare)')])
                continue
            d = m - nat[k]
            lettura = ('copia più del testo vero' if (es is not None and d > 3 * es and m > 2 * nat[k]) else
                       'copia meno del testo vero' if (es is not None and d < -3 * es and m < nat[k] / 2) else 'copia come il testo vero')
            letture_copia[k] = OrderedDict([('generato', m), ('errore', es), ('naturale', nat[k]), ('differenza', d), ('lettura', lettura)])

    # capacità
    cap = media_es([r['capacita_bit'] for r in con])
    capacita = OrderedDict([('con_messaggio', cap), ('senza_messaggio', media_es([r['capacita_bit'] for r in senza])),
                            ('bit_messaggio', con[0]['bit_messaggio'] if con else None), ('v21', V21['capacita'])])
    if cap[0] is not None:
        capacita['lettura'] = non_valida(('recupero',)) or (
            'più del v21' if cap[0] > V21['capacita'][1] else 'meno del v21' if cap[0] < V21['capacita'][0] else 'come il v21')
    traccia = OrderedDict()
    if cs:
        a = cs['AUC_diretta']
        traccia = OrderedDict(cs)
        traccia['lettura'] = non_valida(('recupero', 'negativo_con_senza')) or (
            'nessuna traccia' if NEGATIVO[0] <= a <= NEGATIVO[1] else 'traccia' if a > NEGATIVO[1] else 'sotto 0,45 (da capire)')

    # giudice A: riferimento v21 ricalcolato e coerenza con ia01
    va = media_es([r['AUC_A_a'] for r in rifA if r.get('AUC_A_a') is not None])
    vb = media_es([r['AUC_A_b'] for r in rifA if r.get('AUC_A_b') is not None])
    giudice_a = OrderedDict([('v21_senza_messaggio', vb), ('v21_con_messaggio', va), ('v21_libri', len(rifA)),
                             ('diff_profilo_v21_senza', media_diff([r.get('diff_profilo_A_b') for r in rifA])),
                             ('ia01_v21_con_messaggio', AUC_A_IA01), ('controlli_ia01', CONTROLLI_A_IA01),
                             ('scarto_ricalcolo_da_ia01', (va[0] - AUC_A_IA01) if va[0] is not None else None),
                             ('ricalcolo_coerente_con_ia01', (abs(va[0] - AUC_A_IA01) <= SCARTO_IA01) if va[0] is not None else None),
                             ('righe_rimescolate_nella_pagina', ctrlA.get('righe', {}).get('AUC_A')),
                             ('coerenza_contesto_ia01', casoA.get('coerenza_ia01') if casoA else None),
                             ('modelli_del_testo', modelliA)])
    out = OrderedDict([('esperimento', 'ia07'), ('solo_controlli', SOLO_CONTROLLI), ('versioni', versioni),
                       ('parametri', OrderedDict([('rete', 'GRU %d strati x %d, immersione %d, caduta %.2f' % (STRATI, NASCOSTO, EMB, CADUTA)),
                                                  ('addestramento', 'AdamW lr %g, decadimento %g, taglio %g, lotti di %d pagine, tratti di %d segni, al massimo %d epoche, pazienza %d' % (
                                                      LR, DECADIMENTO, TAGLIO, LOTTO, TRONCO, EPOCHE_MAX, PAZIENZA)),
                                                  ('pieghe', PIEGHE), ('quota_validazione', QUOTA_VAL), ('fasce_posizione', POS_BORDI), ('fasce_lunghezza', N_FASCE),
                                                  ('probabilita_intere', 'Q = 2^%d, precisione %d bit' % (st.Q_BIT, st.P)),
                                                  ('libri', [N_SENZA, N_CON]), ('pagella', PAGELLA),
                                                  ('giudice_A', 'GRU 1 x %d, immersione %d, caduta %.2f, al massimo %d passi (pazienza %d x %d passi), semi %s, pieghe di IA7' % (
                                                      ia01.NASCOSTO, ia01.EMB, ia01.CADUTA, ia01.PASSI, ia01.PAZIENZA, ia01.OGNI, list(SEMI_A)))])),
                       ('controlli', controlli), ('modelli', modelli), ('vetrina_modello', corse.get('addestra|tutto')),
                       ('giudici', giudici), ('giudice_A', giudice_a), ('differenze_con_meno_senza', differenze), ('scala', OrderedDict((g, OrderedDict([
                           ('AUC_e231', statistics.mean(r['AUC_e231'] for r in rs)), ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs))]))
                           for g, rs in O.items() if rs)), ('scala_paper', SCALA),
                       ('copia', copia), ('copia_riferimenti', OrderedDict((k, quote(v)) for k, v in rif_copia.items())), ('letture_copia', letture_copia),
                       ('capacita', capacita), ('traccia', traccia), ('vetrina', vetrina), ('immagini', immagini_fatte)])
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def nu(v, d=3):
    if v is None:
        return '—'
    if isinstance(v, bool):
        return 'sì' if v else 'NO'
    return ('%.*f' % (d, v)).replace('.', ',')


def scrivi_md(o):
    c = o['controlli']
    md = ['# IA7 (ia07) — Il Voynich ricreato da una rete neurale locale', '',
          'Preregistrazione: `preregistrazioni/ia07.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Rete: %s. Addestramento: %s.' % (o['parametri']['rete'], o['parametri']['addestramento']),
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '',
          '## Controlli', '',
          '- **Positivo** (%s): AUC %s, soglia ≥ %s → %s.' % (c['positivo']['che cosa'], nu(c['positivo']['AUC']), nu(SOGLIA_POSITIVO, 2), nu(c['positivo']['riuscito'])),
          '- **Negativo** (%s): giudice 1 %s, giudice 2 %s, intervallo 0,45–0,55 → %s.' % (c['negativo']['che cosa'], nu(c['negativo']['AUC_e231']), nu(c['negativo']['AUC_e266']), nu(c['negativo']['riuscito'])),
          '- **Recupero del messaggio**: esatto %d su %d, chiave sbagliata respinta %d su %d → %s.' % (c['recupero']['esatti'], c['recupero']['libri'], c['recupero']['respinti'], c['recupero']['libri'], nu(c['recupero']['riuscito']))]
    if 'negativo_con_senza' in c:
        md.append('- **Negativo con/senza** (%s): AUC %s → %s.' % (c['negativo_con_senza']['che cosa'], nu(c['negativo_con_senza']['AUC']), nu(c['negativo_con_senza']['riuscito'])))
    if 'positivo_A' in c:
        pa, na = c['positivo_A'], c['negativo_A']
        md.append('- **Positivo, giudice A** (%s): AUC %s, soglia ≥ %s → %s.' % (
            pa['che cosa'], ', '.join('%s %s' % (k, nu(v)) for k, v in pa['AUC'].items()), nu(pa['soglia'], 2), nu(pa['riuscito'])))
        md.append('- **Negativo, giudice A** (%s): AUC %s (%s), intervallo 0,45–0,55 → %s.' % (
            na['che cosa'], nu(na['AUC']), ', '.join(nu(v) for v in (na['AUC_etichette'] or [])), nu(na['riuscito'])))
    md += ['', '## Modelli (pieghe per foglio, due repliche con semi di addestramento diversi)', '', '| piega | replica | fogli add./val./fuori | parametri | epoca scelta (su) | BPC add. | BPC val. | BPC fuori | scarto | minuti |', '|---|---|---|---|---|---|---|---|---|---|']
    for m in o['modelli'] + ([o['vetrina_modello']] if o['vetrina_modello'] else []):
        md.append('| %s | %s | %s | %d | %d (%d) | %s | %s | %s | %s | %.1f |' % (m['piega'], m.get('replica', '—') if m['piega'] != 'tutto' else '—', '/'.join(map(str, m['fogli'])), m['parametri'], m['epoca_scelta'], m['epoche'],
                                                                     nu(m['bpc_addestramento']), nu(m['bpc_validazione']), nu(m['bpc_fuori']), nu(m.get('scarto')), m['secondi'] / 60))
    md += ['', '## Giudici: libri generati contro libro vero (un giudice per libro)', '',
           '| libri | n | giudice 1 (e231) | lettura | giudice 2 (e266) | lettura | pagine giudicate | pagella | cancello | estese |', '|---|---|---|---|---|---|---|---|---|---|']
    for nome, g in o['giudici'].items():
        a, b = g['AUC_e231'], g['AUC_e266']
        md.append('| %s | %d | %s ± %s (%s–%s) | %s | %s ± %s (%s–%s) | %s | %.0f | %s | %s | %s |' % (
            nome, g['libri'], nu(a['media']), nu(a['errore']), nu(a['min_max'][0]), nu(a['min_max'][1]), a['lettura'],
            nu(b['media']), nu(b['errore']), nu(b['min_max'][0]), nu(b['min_max'][1]), b['lettura'], g['pagine_giudicate'],
            nu(g.get('pagella'), 1), g.get('cancello_riga', '—'), nu(g.get('estese'), 1)))
    md += ['', 'Riferimenti del paper v2: v21 giudice 1 %s ± %s, giudice 2 %s ± %s (24 chiavi, pagella 16,0/17). Scala (e400): %s.' % (
        nu(V21['AUC_e231'][0]), nu(V21['AUC_e231'][1]), nu(V21['AUC_e266'][0]), nu(V21['AUC_e266'][1]),
        '; '.join('%s: %s e %s' % (k, nu(v[0]), nu(v[1])) for k, v in o['scala_paper'].items()))]
    if o['scala']:
        md.append('Scala ricalcolata qui sul libro vero: ' + '; '.join('%s: %s e %s' % (k, nu(v['AUC_e231']), nu(v['AUC_e266'])) for k, v in o['scala'].items()) + '.')
    for nome, g in o['giudici'].items():
        md += ['', '**Per replica dei modelli (%s):** ' % nome + '; '.join('giudice %s: %s' % (
            j, ', '.join('replica %s %s ± %s' % (rp, nu(me[0]), nu(me[1])) for rp, me in g[k]['per_replica'].items())) for j, k in (('1', 'AUC_e231'), ('2', 'AUC_e266'))) + '.']
        md += ['', '**Gruppi del giudice 2 (%s):** ' % nome + '; '.join('%s %s' % (k, nu(v, 2)) for k, v in g['gruppi_e266'].items()) + '.']
        if g.get('materie_mancate'):
            md.append('Materie mancate (somma sui libri): ' + ', '.join('%s (%d)' % kv for kv in g['materie_mancate'].items()) + '.')
        md += ['', '| caratteristica (primo libro) | coefficiente | vero | generato |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(z) for z in g['pesanti_e266']]
    ga = o['giudice_A']
    md += ['', '## Giudice A "sorpresa" (di IA1): libri generati contro libro vero', '',
           'Modello del testo per piega (le pieghe dei generatori) e seme addestrato sulle pagine vere delle altre pieghe; profilo di sorpresa di 14 numeri per pagina; '
           'regressione logistica come e231. **Limite di circolarità:** il generatore e il giudice sono reti addestrate sullo stesso testo; vedi la preregistrazione.', '',
           '| libri | n | AUC A | v21 ricalcolato (stesse pieghe) | lettura | lettura assoluta | nota |', '|---|---|---|---|---|---|---|']
    per_rep = []
    for nome, g in o['giudici'].items():
        a = g.get('A')
        if not a:
            continue
        md.append('| %s | %d | %s ± %s (%s–%s) | %s ± %s (%d libri) | %s | %s | %s |' % (
            nome, a['libri'], nu(a['media']), nu(a['errore']), nu(a['min_max'][0]), nu(a['min_max'][1]), nu(a.get('v21')), nu(ga[('v21_senza_messaggio' if nome == 'senza messaggio' else 'v21_con_messaggio')][1]),
            ga['v21_libri'], a['lettura'], a['lettura_assoluta'], a.get('nota_circolarita') or '—'))
        per_rep.append('Per replica dei modelli (%s): ' % nome + ', '.join('replica %s %s ± %s' % (rp, nu(me[0]), nu(me[1])) for rp, me in a['per_replica'].items()) + '.')
    for r in per_rep:
        md += ['', r]
    md += ['', 'v21 con messaggio (chiavi 13–22) ricalcolato qui: %s ± %s; ia01 (pieghe per pagina): %s → scarto %s (%s). v21 senza messaggio: %s ± %s. '
           'Righe rimescolate nella pagina: %s. Controlli di ia01 (pieghe diverse): %s.' % (
               nu(ga['v21_con_messaggio'][0]), nu(ga['v21_con_messaggio'][1]), nu(ga['ia01_v21_con_messaggio']), nu(ga['scarto_ricalcolo_da_ia01']),
               'coerente' if ga['ricalcolo_coerente_con_ia01'] else 'NON coerente entro 0,03' if ga['ricalcolo_coerente_con_ia01'] is not None else '—',
               nu(ga['v21_senza_messaggio'][0]), nu(ga['v21_senza_messaggio'][1]), nu(ga['righe_rimescolate_nella_pagina']),
               '; '.join('%s %s' % (k, nu(v)) for k, v in ga['controlli_ia01'].items()))]
    if ga['coerenza_contesto_ia01']:
        md.append('Coerenza del contesto con ia01.contesto(): %s.' % '; '.join('%s %s' % kv for kv in ga['coerenza_contesto_ia01'].items()))
    if ga['modelli_del_testo']:
        md += ['', 'Modelli del testo di A: ' + '; '.join('seme %d piega %d: %d passi, %s bit/segno in validazione, %s fuori' % (
            m['seme'], m['piega'], m['passi'], nu(m['bpc_validazione']), nu(m['bpc_vere_fuori'])) for m in ga['modelli_del_testo']) + '.']
    for nome, g in o['giudici'].items():
        a = g.get('A')
        if a and a.get('diff_profilo'):
            md += ['', 'Differenza di profilo, generato meno vero, bit per segno (%s): ' % nome + ', '.join('%s %+.3f' % kv for kv in a['diff_profilo'].items()) + '.']
    if ga['diff_profilo_v21_senza']:
        md += ['', 'Lo stesso per il v21 senza messaggio: ' + ', '.join('%s %+.3f' % kv for kv in ga['diff_profilo_v21_senza'].items()) + '.']
    if o['differenze_con_meno_senza']:
        md += ['', 'Con meno senza messaggio (differenza delle medie, libri non appaiati): ' + '; '.join('%s %s ± %s' % (k, nu(v['differenza'], 4), nu(v['errore'], 4)) for k, v in o['differenze_con_meno_senza'].items()) + '.']
    md += ['', '## Copia a memoria', '', 'Quote rispetto al testo d\'addestramento del modello che ha scritto la pagina (riferimento naturale: le pagine vere tenute fuori, stesse pieghe).', '',
           '| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |', '|---|---|---|---|---|']
    for nome, q in o['copia'].items():
        md.append('| %s | %s |' % (nome, ' | '.join('%s ± %s' % (nu(q[k][0], 4), nu(q[k][1], 4)) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    for nome, q in o['copia_riferimenti'].items():
        md.append('| %s | %s |' % (nome, ' | '.join(nu(q[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    for k, l in o['letture_copia'].items():
        md.append('- %s: generato %s ± %s, naturale %s → **%s**.' % (k, nu(l['generato'], 4), nu(l['errore'], 4), nu(l['naturale'], 4), l['lettura']))
    cp = o['capacita']
    md += ['', '## Messaggio', '', '- Capacità (bit determinati dal libro): con messaggio %s ± %s, senza %s ± %s; il messaggio ne usa %s; v21 %d–%d → **%s**.' % (
        nu(cp['con_messaggio'][0], 0), nu(cp['con_messaggio'][1], 0), nu(cp['senza_messaggio'][0], 0), nu(cp['senza_messaggio'][1], 0),
        cp['bit_messaggio'], cp['v21'][0], cp['v21'][1], cp.get('lettura', '—'))]
    if o['traccia']:
        t = o['traccia']
        md.append('- Con contro senza messaggio (giudice 2, pieghe per libro, %d pagine): AUC %s → **%s**. Per gruppo: %s.' % (
            t['pagine'], nu(t['AUC_diretta']), t['lettura'], '; '.join('%s %s' % (k, nu(v)) for k, v in t['per_gruppo'].items() if v is not None)))
    if o['vetrina']:
        v = o['vetrina']
        md += ['', '## Libro vetrina (modello addestrato su tutto: non è una prova onesta)', '',
               '- Giudice 1 %s, giudice 2 %s; recupero esatto %s; capacità %s bit; pagella %s.' % (nu(v['AUC_e231']), nu(v['AUC_e266']), nu(v['recupero_esatto']), v['capacita_bit'], v.get('pagella', '—')),
               '- Copia rispetto al libro intero: ' + '; '.join('%s %s' % (k, nu(a / b if b else None, 4)) for k, (a, b) in v['copia'].items()) + '.']
        cc = v.get('controllo_copia')
        if cc:
            t = cc['totali']
            md += ['', '**Controllo di copia della vetrina** (il testo e le immagini restano in `dati/cache/ia07_vetrina/`, non nel repo; '
                   'la pubblicazione di qualche pagina la decide Davide guardando questo controllo):', '',
                   '- righe di almeno 3 parole identiche a una riga del libro vero: **%d su %d** (nello stesso posto: %d);' % (
                       t['righe copiate'], t['righe'], t['righe copiate nello stesso posto']),
                   '- 5-grammi di parole presenti nel libro vero: **%d su %d** (%s);' % (t['5-grammi copiati'], t['5-grammi'], nu(t['5-grammi copiati'] / t['5-grammi'] if t['5-grammi'] else None, 4)),
                   '- pagine intere identiche alla pagina vera: **%d su %d**;' % (t['pagina intera identica'], cc['pagine']),
                   '- pagine senza nessuna riga e nessun 5-gramma copiato: %d su %d.' % (len(cc['pagine_pulite']), cc['pagine']), '']
            peggiori = sorted(cc['pagine_con_copia'].items(), key=lambda kv: (-kv[1]['righe copiate'], -kv[1]['5-grammi copiati']))[:30]
            if peggiori:
                md += ['Pagine con copia (le prime 30 per righe copiate):', '', '| pagina | righe copiate / righe | 5-grammi copiati / 5-grammi | pagina identica |', '|---|---|---|---|']
                md += ['| %s | %d / %d | %d / %d | %s |' % (p, c['righe copiate'], c['righe'], c['5-grammi copiati'], c['5-grammi'], 'sì' if c['pagina intera identica'] else 'no')
                       for p, c in peggiori]
                md.append('')
            else:
                md += ['Nessuna pagina con copia.', '']
    if o['immagini']:
        md.append('- Pagine in immagine (solo fra le pagine senza copia, in `dati/cache/ia07_vetrina/pagine/`): ' +
                  ', '.join('`%s` (%.0f kB)' % (n, s / 1024) for n, s in o['immagini']) + '.')
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:
        pass
    os.makedirs(USCITA, exist_ok=True)
    righe, voc = libro_vero(), vocabolario()
    pp = per_pagina(righe)
    print('libro vero: %d righe, %d pagine, %d parole, %d segni (%s), fasce di lunghezza %s, riga massima %d' % (
        len(righe), len(pp), sum(len(x['parole']) for x in righe), len(voc['unita']), 'controlli: latino' if SOLO_CONTROLLI else 'Voynich',
        voc['bordi'], voc['lmax']), flush=True)
    pg = pieghe()
    print('pieghe: %s fogli' % [sum(1 for k in pg.values() if k == j) for j in range(PIEGHE)], flush=True)
    percorso = os.path.join(USCITA, 'ia07_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso)}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    if 'A' in FASI:
        # prima i 10 modelli del testo del giudice A (brevi), poi i 10 generatori
        esegui([('lmA', s, k) for s in SEMI_A for k in range(PIEGHE)] + [('addestra', k, r) for r in range(REPLICHE) for k in range(PIEGHE)],
               processi, percorso, fatte)
    if 'B' in FASI:
        lavori = ([('addestra', 'tutto')] + [('libro', 'senza', i) for i in range(1, N_SENZA + 1)] + [('libro', 'con', i) for i in range(1, N_CON + 1)]
                  + [('O', g, s) for g in ('O1', 'O2') for s in SEMI_O] + [('caso', 0)]
                  + [('rifA', k) for k in CHIAVI_V21] + [('ctrlA', n) for n in NOMI_CTRL_A] + [('casoA', 0)])
        esegui(lavori, processi, percorso, fatte)
    fatte_img = []
    if 'C' in FASI:
        esegui([('libro', 'vetrina', 0)], 1, percorso, fatte)
        libro = os.path.join(VETRINA, 'ia07_libro_vetrina_0.txt')          # resta in dati/cache, mai in risultati/
        pulite = next((c['controllo_copia']['pagine_pulite'] for c in leggi_corse(percorso) if c['lavoro'] == 'libro|vetrina|0'), [])
        try:
            fatte_img = immagini(libro, os.path.join(VETRINA, 'pagine'), pulite)
        except Exception as e:
            print('immagini non fatte: %r' % e, flush=True)
    if 'S' in FASI:
        o = sintesi(versioni, fatte_img)
        c = o['controlli']
        print('controllo positivo: %s (AUC %s, soglia %s)' % ('riuscito' if c['positivo']['riuscito'] else 'FALLITO', nu(c['positivo']['AUC']), SOGLIA_POSITIVO), flush=True)
        print('controllo negativo: %s (giudice 1 %s, giudice 2 %s)' % ('riuscito' if c['negativo']['riuscito'] else 'FALLITO', nu(c['negativo']['AUC_e231']), nu(c['negativo']['AUC_e266'])), flush=True)
        print('controllo recupero: %s (%d/%d esatti, %d/%d chiave sbagliata respinta)' % ('riuscito' if c['recupero']['riuscito'] else 'FALLITO', c['recupero']['esatti'],
                                                                                         c['recupero']['libri'], c['recupero']['respinti'], c['recupero']['libri']), flush=True)
        if 'negativo_con_senza' in c:
            print('controllo negativo con/senza: %s (AUC %s)' % ('riuscito' if c['negativo_con_senza']['riuscito'] else 'FALLITO', nu(c['negativo_con_senza']['AUC'])), flush=True)
        print('controllo positivo giudice A: %s (AUC %s, soglia %s)' % ('riuscito' if c['positivo_A']['riuscito'] else 'FALLITO',
                                                                         ', '.join('%s %s' % (k, nu(v)) for k, v in c['positivo_A']['AUC'].items()), SOGLIA_POSITIVO_A), flush=True)
        print('controllo negativo giudice A: %s (AUC %s)' % ('riuscito' if c['negativo_A']['riuscito'] else 'FALLITO', nu(c['negativo_A']['AUC'])), flush=True)
        for nome, g in o['giudici'].items():
            print('%s: giudice 1 %s ± %s (%s), giudice 2 %s ± %s (%s)' % (nome, nu(g['AUC_e231']['media']), nu(g['AUC_e231']['errore']), g['AUC_e231']['lettura'],
                                                                     nu(g['AUC_e266']['media']), nu(g['AUC_e266']['errore']), g['AUC_e266']['lettura']), flush=True)
            if g.get('A'):
                print('%s: giudice A %s ± %s contro v21 %s (%s; %s)' % (nome, nu(g['A']['media']), nu(g['A']['errore']), nu(g['A'].get('v21')), g['A']['lettura'], g['A']['lettura_assoluta']), flush=True)
        for k, l in o['letture_copia'].items():
            print('copia %s: %s contro %s naturale (%s)' % (k, nu(l['generato'], 4), nu(l['naturale'], 4), l['lettura']), flush=True)
        if o['capacita'].get('lettura'):
            print('capacità: %s bit (%s); traccia: %s' % (nu(o['capacita']['con_messaggio'][0], 0), o['capacita']['lettura'], o['traccia'].get('lettura')), flush=True)


def rileggi(percorso, chiave):
    """Rilegge il messaggio da un libro scritto con i modelli onesti (o 'vetrina' nel nome del file: modello su tutto)."""
    avvia_processo()
    modello_di = (lambda pag: 'tutto') if 'vetrina' in os.path.basename(percorso) else modello_onesto(replica_del_file(percorso))
    bit = leggi_libro(modello_di, leggi_file(percorso))
    testo = st.apri(bit, chiave) if bit is not None else None
    print('bit letti: %s; messaggio: %s' % (len(bit) if bit is not None else None, 'nessuno (chiave sbagliata o libro senza messaggio)' if testo is None else '%d caratteri' % len(testo)))
    if testo is not None:
        atteso = open(MESSAGGIO, encoding='utf-8').read().replace('\r\n', '\n')
        print('uguale al messaggio di partenza: %s' % (testo == atteso))
    return testo


if __name__ == '__main__':
    if '--leggi' in sys.argv:
        k = sys.argv.index('--leggi')
        rileggi(sys.argv[k + 1], sys.argv[k + 2])
    else:
        main()
