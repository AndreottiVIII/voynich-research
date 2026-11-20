# -*- coding: utf-8 -*-
"""Esperimento IA4 (ia04): il cervello di una lingua.

Domanda: se una rete ha imparato una lingua e le si lascia imparare solo l'alfabeto di un testo nuovo (la parte interna
resta bloccata), torna al livello della lingua quando il testo nuovo è quella lingua cifrata segno per segno? E sul
Voynich, qualche lingua aiuta più delle altre? È la versione con controlli delle "decifrazioni con l'IA" (Hauer e
Kondrak 2016/2018: un programma sceglie la lingua che spiega meglio un testo cifrato).

Cervelli: per ciascuna delle 20 lingue di e3c95 (stesso testo, stesso taglio, stesso modello: GRU a caratteri, 1 strato,
immersione 32, 128 unità, caduta 0,3), addestrati da zero sui 40.000 segni di addestramento, con arresto anticipato sulla
validazione, per i semi 1-3. Si salvano i pesi (cartella CERVELLI).

Adattamento al testo T (seme s): il nucleo GRU del cervello della lingua M (stesso seme) si blocca; si addestrano solo un
nuovo strato d'ingresso (immersione, V_T x 32) e un nuovo strato d'uscita (128 -> V_T) per l'alfabeto di T, con la
stessa caduta, lo stesso AdamW, lo stesso taglio del gradiente e lo stesso arresto anticipato sulla validazione di T
(passo LR_AD, al massimo PASSI_AD passi, pazienza PAZIENZA_AD). Avvio per frequenza (AVVIO=frequenza): ogni segno
del bersaglio parte con l'immersione e l'uscita del segno del cervello che ha la stessa posizione nella classifica per
frequenza (solo frequenze). Misura: BPC sulla prova di T nel punto scelto.

Cifrati: C+ solo su quelli con passi nuovi dello stesso testo; quelli con l'altro testo della lingua (ruolo cifrato_altro) e la
sonda degradata (omofoni e digrafi) sono descrittivi. Famiglie di lingue per lo scarto del criterio; analisi anche con i soli
cervelli con almeno tanti segni del bersaglio; cancello contro i generatori nelle letture. NUOVA=1 per azzerare il file delle corse.
Riferimenti per ogni T e seme:
- casuale: nucleo GRU con la stessa inizializzazione del seme, mai addestrato, bloccato; stesso adattamento di
  immersione e uscita (quanto si ottiene con la sola parte nuova);
- casuale con avvio (CAS_AVVIO_SU): nucleo casuale bloccato con lo stesso avvio per frequenza del cervello M (eco delle frequenze);
- zero: la rete intera addestrata da zero su T come in e3c95 (tutto addestrabile, passo 2e-3).
Guadagno di trasferimento: TG(M -> T) = (BPC_casuale - BPC_M) / (BPC_casuale - BPC_zero), seme per seme poi media.
Se il denominatore (media dei semi) è sotto DEN_MIN bit, il TG non si calcola (testo senza struttura: resta il guadagno
in bit, g = BPC_casuale - BPC_M).

Bersagli (T):
- "Cifrato: L": il testo della lingua L cifrato con una sostituzione semplice casuale dei segni (lettera per lettera; spazi
  e a capo restano, come nel Voynich). Passi mai visti dal cervello: addestramento, validazione e prova del bersaglio sono
  blocchi del testo di L che il cervello non ha usato (si continua lo stesso ordine casuale dei blocchi, dopo i blocchi del
  cervello); se il testo non è abbastanza lungo si usa l'altro testo della stessa lingua (letterario/tecnico); se non c'è,
  la lingua non è bersaglio (resta cervello). Per il latino sono "giusti" sia il latino sia il latino abbreviato.
- Voynich intero, A, B, Voynich in lettere EVA non fuse; generatori (Timm e Schinner, voynichizzatore v21, Naibbe);
  gibberish; negativo: il Voynich con i segni rimescolati fra le parole; negativo di prova: il latino con i segni
  rimescolati.
Taglio come in e3c95: 40.000 + 5.000 + 10.000 segni, blocchi per pagina o per 29 righe, ordine casuale random.Random(1000+s).

Preregistrazione: preregistrazioni/ia04.md. Scrive risultati/ia04_cervello_lingua.json e .md e, una riga per corsa,
risultati/ia04_corse.jsonl (con RIPRENDI=1 le corse già fatte non si rifanno).
SOLO_CONTROLLI=1: nessun testo del Voynich né imitazioni in EVA (solo per provare il codice). Per le prove: PASSI,
PASSI_AD, PAZIENZA_AD, LR_AD, SEMI, TESTI (bersagli) e CERVELLI (cervelli): sottostringhe separate da |, "=Nome" per il
nome esatto; USCITA cambia la cartella d'uscita; CERVELLI_DIR la cartella dei pesi. PROCESSI: numero di processi in
parallelo (non cambia i risultati).
"""
import json, math, os, random, re, statistics, sys, time
from collections import OrderedDict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c95_imparabilita as e95   # noqa: E402  (funzioni di testo e di taglio, non modificate)

N_ADD, N_VAL, N_PROVA = e95.N_ADD, e95.N_VAL, e95.N_PROVA
SEMI = tuple(int(s) for s in os.environ.get('SEMI', '1,2,3').split(','))
# cervelli e rete da zero: come e3c95
PASSI = int(os.environ.get('PASSI', 2000))
OGNI = int(os.environ.get('OGNI', 20))
PAZIENZA = int(os.environ.get('PAZIENZA', 10))
LUNG, LOTTO = int(os.environ.get('LUNG', 64)), int(os.environ.get('LOTTO', 32))
EMB, NASCOSTO, CADUTA = 32, int(os.environ.get('NASCOSTO', 128)), float(os.environ.get('CADUTA', 0.3))
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
# adattamento (immersione e uscita nuove, nucleo bloccato) e rete casuale bloccata
PASSI_AD = int(os.environ.get('PASSI_AD', 3000))
PAZIENZA_AD = int(os.environ.get('PAZIENZA_AD', 15))
LR_AD = float(os.environ.get('LR_AD', 1e-2))
# avvio dell'adattamento: 'frequenza' = ogni segno del bersaglio parte con l'immersione e l'uscita del segno del cervello
# che ha la stessa posizione nella classifica per frequenza (solo frequenze, nessuna conoscenza della sostituzione);
# 'casuale' = immersione e uscita casuali
AVVIO = os.environ.get('AVVIO', 'frequenza')
DEN_MIN = 0.10          # bit: sotto questo, "casuale - da zero" è troppo piccolo per un rapporto
# soglie delle letture (fissate dopo le prove del codice sui controlli, prima di toccare il Voynich)
TG_ALTO = float(os.environ.get('TG_ALTO', 0.80))
MARGINE_TG = float(os.environ.get('MARGINE_TG', 0.10))
SOGLIA_NEG = float(os.environ.get('SOGLIA_NEG', 0.03))     # bit: guadagno massimo ammesso sul negativo
QUOTA_FALLITI = 0.10    # controlli positivi: al massimo il 10% (2 su 18) può non riuscire
SOLO_CONTROLLI = e95.SOLO_CONTROLLI
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
CERVELLI_DIR = os.environ.get('CERVELLI_DIR', os.path.join(QUI, '..', 'dati', 'cache', 'ia04_cervelli'))
NOME = 'ia04_cervello_lingua'
SEME_CIFRA = 9500
FAMIGLIE = ({'Latin', 'Latin (Abbreviated)'},)    # due varietà della stessa lingua: sono "giuste" entrambe
# famiglie di lingue (decise prima di vedere i risultati); le lingue non elencate sono una famiglia da sole
FAMIGLIA = {}
for _f, _ls in (('romanze', ('Latin', 'Latin (Abbreviated)', 'Italian', 'Spanish', 'French')),
                ('germaniche', ('English', 'German', 'Flemish', 'Anglo-Saxon')),
                ('semitiche', ('Arabic', 'Hebrew')),
                ('austronesiane', ('Maori', 'Tagalog'))):
    for _l in _ls:
        FAMIGLIA[_l] = _f


def famiglia(L):
    return FAMIGLIA.get(L, L)


DEN_ETICHETTA = 0.30    # bit, per ogni seme: sotto questo il TG non basta per dare un'etichetta o per contare un cifrato
MIN_VALUTABILI = int(os.environ.get('MIN_VALUTABILI', 12))   # cifrati valutabili necessari perché C+ possa riuscire
# bersagli per cui si fa anche il riferimento "nucleo casuale + avvio per frequenza dal cervello M"
CAS_AVVIO_SU = set(s for s in os.environ.get('CAS_AVVIO_SU', '|'.join((
    'Voynich', "Voynichizzatore v21 (libro d'esempio)", 'Timm e Schinner (seme 1)', 'Gibberish (Gaskell e Bowern)',
    'Voynich, segni rimescolati (controllo negativo)', 'Cifrato: Latin', 'Cifrato: Spanish'))).split('|') if s)
CFG = dict(EMB=EMB, NASCOSTO=NASCOSTO, CADUTA=CADUTA, LR=LR, DECADIMENTO=DECADIMENTO, TAGLIO=TAGLIO, LUNG=LUNG,
           LOTTO=LOTTO, PASSI=PASSI, OGNI=OGNI, PAZIENZA=PAZIENZA, N_ADD=N_ADD, N_VAL=N_VAL, N_PROVA=N_PROVA)

import numpy as np   # noqa: E402
import torch   # noqa: E402
import torch.nn as nn   # noqa: E402
import torch.nn.functional as F   # noqa: E402


# ---------------------------------------------------------------- testi e taglio

def riempi(blocchi, ordine, inizio):
    """Come e95.dividi_blocchi, ma parte dalla posizione `inizio` dell'ordine e dice dove si è fermato.
    Restituisce (parti, posizione del primo blocco non usato) oppure (None, posizione) se non bastano i blocchi."""
    parti, quote, k, n, pos = ([], [], []), (N_ADD, N_VAL, N_PROVA), 0, [0, 0, 0], inizio
    while pos < len(ordine):
        while k < 3 and n[k] >= quote[k]:
            k += 1
        if k == 3:
            break
        b = blocchi[ordine[pos]]
        parti[k].extend(b)
        n[k] += len(e95.flusso(b))
        pos += 1
    while k < 3 and n[k] >= quote[k]:
        k += 1
    return (parti if k == 3 else None), pos


def due_tagli(blocchi, seme):
    """Taglio del cervello (identico a e95.dividi_blocchi) e taglio del bersaglio, fatto con i blocchi che vengono dopo
    nello stesso ordine casuale: nessun blocco in comune. Il secondo è None se il testo non basta."""
    ordine = list(range(len(blocchi)))
    random.Random(1000 + seme).shuffle(ordine)
    cerv, pos = riempi(blocchi, ordine, 0)
    if cerv is None:
        return None, None
    return cerv, riempi(blocchi, ordine, pos)[0]


def nome_file(s):
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')


def filtra(nomi, variabile):
    filtro = [s for s in os.environ.get(variabile, '').split('|') if s]
    if not filtro:
        return list(nomi)
    return [k for k in nomi if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro)]


def catalogo_testi():
    """Il catalogo di e3c95, senza il filtro TESTI (qui TESTI filtra i bersagli)."""
    salvato = os.environ.pop('TESTI', None)
    try:
        return e95.catalogo()
    finally:
        if salvato is not None:
            os.environ['TESTI'] = salvato


def origine_cifrato(L, cat):
    """Da dove vengono i passi nuovi del bersaglio cifrato di L: 'stesso' (blocchi non usati dal cervello, stesso testo),
    ('altro', nome) (l'altro testo della lingua) o None. Si decide una volta per tutti i semi."""
    if all(due_tagli(cat[L]['blocchi'], s)[1] is not None for s in SEMI):
        return 'stesso'
    for n, v in cat.items():
        if v['ruolo'] == 'trasferimento' and v['gruppo'] == cat[L]['gruppo'] and \
                all(e95.dividi_blocchi(v['blocchi'], s) is not None for s in SEMI):
            return ('altro', n)
    return None


def giusti_di(L):
    for f in FAMIGLIE:
        if L in f:
            return sorted(f)
    return [L]


def bersagli(cat, lingue_n):
    """Elenco dei bersagli: nome -> dict(ruolo, ...)."""
    b = OrderedDict()
    for L in lingue_n:
        o = origine_cifrato(L, cat)
        if o is None:
            print('senza passi nuovi, non è bersaglio (resta cervello): %s' % L, flush=True)
            continue
        # C+ solo sui cifrati con passi nuovi dello stesso testo; gli altri (altro testo, genere diverso) sono descrittivi
        b['Cifrato: ' + L] = dict(ruolo='cifrato' if o == 'stesso' else 'cifrato_altro', lingua=L, origine=o,
                                  giusti=giusti_di(L), indice=lingue_n.index(L))
    if not SOLO_CONTROLLI:
        for n in ('Voynich', 'Voynich A', 'Voynich B', 'Voynich in lettere EVA non fuse (sensibilità)',
                  'Timm e Schinner (seme 1)', "Voynichizzatore v21 (libro d'esempio)", 'Naibbe'):
            b[n] = dict(ruolo='voynich' if n.startswith('Voynich') and 'zzatore' not in n else 'generatore',
                        blocchi=cat[n]['blocchi'])
    b['Gibberish (Gaskell e Bowern)'] = dict(ruolo='generatore', blocchi=cat['Gibberish (Gaskell e Bowern)']['blocchi'])
    if not SOLO_CONTROLLI:
        b['Voynich, segni rimescolati (controllo negativo)'] = dict(ruolo='negativo', blocchi=cat['Voynich']['blocchi'],
                                                                   trasforma='lettere')
    if 'Latin' in lingue_n and origine_cifrato('Latin', cat) == 'stesso':
        # sonda di sensibilità: latino con tre segni divisi in due omofoni e tre coppie fuse in un segno, poi cifrato
        b['Latin, cifrato degradato: omofoni e digrafi (sonda)'] = dict(
            ruolo='sonda', lingua='Latin', origine='stesso', giusti=giusti_di('Latin'), degrada=True,
            indice=len(lingue_n) + 1)
    if 'Latin' in lingue_n:
        o = origine_cifrato('Latin', cat)
        if o is not None:
            b['Latin, segni rimescolati (controllo negativo)'] = dict(ruolo='negativo', lingua='Latin', origine=o,
                                                                    trasforma='lettere')
    return b


def degrada(parti, n_omofoni=3, n_digrafi=3):
    """Cifrato degradato (sonda): i 3 segni più frequenti dell'addestramento diventano due segni (omofoni) a occorrenze
    alterne; le 3 coppie di segni vicini più frequenti (senza segni omofoni, da sinistra a destra) diventano un segno solo.
    Le tre parti usano le stesse scelte; il contatore degli omofoni corre in ordine sulle tre parti."""
    conti, coppie = {}, {}
    for r in parti[0]:
        for w in r:
            for x in w:
                conti[x] = conti.get(x, 0) + 1
            for c in zip(w, w[1:]):
                coppie[c] = coppie.get(c, 0) + 1
    omo = [x for x, _ in sorted(conti.items(), key=lambda t: (-t[1], t[0]))[:n_omofoni]]
    dig = [c for c, _ in sorted(coppie.items(), key=lambda t: (-t[1], t[0]))
           if c[0] not in omo and c[1] not in omo and c[0] != c[1]][:n_digrafi]
    omo_s, dig_s, cont = set(omo), set(dig), {x: 0 for x in omo}

    def parola(w):
        out, i = [], 0
        while i < len(w):
            if i + 1 < len(w) and (w[i], w[i + 1]) in dig_s:
                out.append(w[i] + w[i + 1])
                i += 2
                continue
            x = w[i]
            if x in omo_s:
                cont[x] += 1
                if cont[x] % 2 == 0:
                    x = x + '\u2032'
            out.append(x)
            i += 1
        return tuple(out)
    return [[[parola(w) for w in r] for r in p] for p in parti]


_CACHE = {}


def alfabeti_sorgente(k, blocchi):
    """(tutti i segni, segni frequenti) di un testo; calcolati una volta sola."""
    if k not in _CACHE:
        _CACHE[k] = (e95.segni(blocchi), e95.frequenti([blocchi]))
    return _CACHE[k]


def parti_bersaglio(nome, b, seme, cat):
    """(righe di addestramento, validazione, prova, alfabeto dei segni frequenti) del bersaglio per un seme."""
    if 'lingua' in b:
        L, o = b['lingua'], b['origine']
        if o == 'stesso':
            sorg, k = cat[L]['blocchi'], L
            parti = due_tagli(sorg, seme)[1]
        else:
            sorg, k = cat[o[1]]['blocchi'], o[1]
            parti = e95.dividi_blocchi(sorg, seme)
        tutti, alf = alfabeti_sorgente(k, sorg)
        if parti is not None and b.get('degrada'):
            parti = degrada(parti)
            tutti, alf = e95.segni(parti), e95.frequenti([parti])
        if parti is not None and b['ruolo'] in ('cifrato', 'cifrato_altro', 'sonda'):
            # sostituzione semplice casuale (diversa per lingua e per seme) di tutto l'alfabeto del testo
            cif = [e95.cifra([x], tutti, seme=SEME_CIFRA + 10 * b['indice'] + seme) for x in parti]
            mappa = cif[0][1]
            parti = [c[0][0] for c in cif]
            alf = {mappa[s] for s in alf}
    else:
        parti = e95.dividi_blocchi(b['blocchi'], seme)
        alf = e95.frequenti([b['blocchi']])
    if parti is None:
        return None
    if b.get('trasforma') == 'lettere':
        rnd = random.Random(7919 * seme + 1)
        parti = [e95.rimescola_lettere(x, rnd) for x in parti]
    return parti, alf


def codifica(parti, alf):
    voc = sorted(alf | {' ', '\n', e95.RARO})
    idx = {s: i for i, s in enumerate(voc)}
    flussi = [e95.flusso(x)[:q] for x, q in zip(parti, (N_ADD, N_VAL, N_PROVA))]
    cod = [[idx.get(s, idx[e95.RARO]) for s in f] for f in flussi]
    return dict(V=len(voc), add=cod[0], val=cod[1], prova=cod[2])


# ---------------------------------------------------------------- modello

class Modello(nn.Module):
    """Come in e3c95: immersione 32, GRU a 1 strato, caduta sull'uscita, strato lineare d'uscita."""

    def __init__(self, V):
        super().__init__()
        self.emb = nn.Embedding(V, EMB)
        self.gru = nn.GRU(EMB, NASCOSTO, batch_first=True)
        self.caduta = nn.Dropout(CADUTA)
        self.out = nn.Linear(NASCOSTO, V)

    def forward(self, x):
        y, _ = self.gru(self.emb(x))
        return self.out(self.caduta(y))


def avvia_processo():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def costruisci(V, seme, nucleo=None, blocca=False):
    """Modello con inizializzazione del seme; se `nucleo` (stato della GRU) c'è, lo carica; se `blocca`, la GRU non si
    addestra. Immersione e uscita hanno lo stesso valore iniziale con o senza nucleo caricato (stesso seme)."""
    torch.manual_seed(seme)
    m = Modello(V)
    if nucleo is not None:
        m.gru.load_state_dict(nucleo)
    if blocca:
        for p in m.gru.parameters():
            p.requires_grad_(False)
    return m


def costruisci_ad(V, seme, nucleo=None):
    """Modello con la GRU bloccata. Il nucleo (casuale o del cervello) e l'immersione/uscita nascono da due generatori
    separati: il nucleo casuale di un seme è lo stesso per ogni V; immersione e uscita nuove dipendono da seme e V."""
    torch.manual_seed(seme)
    gru = nn.GRU(EMB, NASCOSTO, batch_first=True)
    torch.manual_seed(seme + 5000)
    m = Modello(V)
    m.gru.load_state_dict(gru.state_dict() if nucleo is None else nucleo)
    for p in m.gru.parameters():
        p.requires_grad_(False)
    return m


def rango(flusso, V):
    """Indici dei segni in ordine di frequenza decrescente nel flusso (a pari frequenza, indice minore)."""
    conti = [0] * V
    for x in flusso:
        conti[x] += 1
    return sorted(range(V), key=lambda i: (-conti[i], i))


def avvio_per_frequenza(m, stato_cervello, rango_bersaglio, rango_cervello):
    """Copia nel nuovo modello immersione e uscita del cervello, segno per segno nell'ordine di frequenza."""
    with torch.no_grad():
        for t, c in zip(rango_bersaglio, rango_cervello):
            m.emb.weight[t] = stato_cervello['emb.weight'][c]
            m.out.weight[t] = stato_cervello['out.weight'][c]
            m.out.bias[t] = stato_cervello['out.bias'][c]


def valuta(m, p):
    m.eval()
    with torch.no_grad():
        logit = m(p[None, :-1])[0]
        bpc = F.cross_entropy(logit, p[1:]).item() / math.log(2)
    m.train()
    return round(bpc, 5)


def addestra(m, d, seme, lr, passi, pazienza, registra0=False):
    """Addestramento come e95.corsa: finestre casuali, AdamW, taglio del gradiente, validazione ogni OGNI passi,
    arresto quando la validazione non migliora da `pazienza` valutazioni. Restituisce BPC della prova nel punto scelto
    (validazione più bassa), con lo stato del modello in quel punto già ricaricato."""
    V = d['V']
    rng = np.random.default_rng(seme)
    ps = [p for p in m.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(ps, lr=lr, weight_decay=DECADIMENTO)
    add = torch.tensor(d['add'], dtype=torch.long)
    val = torch.tensor(d['val'], dtype=torch.long)
    prova = torch.tensor(d['prova'], dtype=torch.long)
    finestra = torch.arange(LUNG + 1)
    curva, migliore, stato = [], None, None
    passo = 0
    bpc0 = valuta(m, prova) if registra0 else None     # BPC della prova prima di addestrare (dopo l'avvio, se c'è)
    for passo in range(1, passi + 1):
        partenze = torch.from_numpy(rng.integers(0, len(add) - LUNG - 1, size=LOTTO))
        xb = add[partenze[:, None] + finestra]
        logit = m(xb[:, :-1])
        loss = F.cross_entropy(logit.reshape(-1, V), xb[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(ps, TAGLIO)
        opt.step()
        if passo % OGNI == 0:
            v = valuta(m, val)
            curva.append(v)
            if migliore is None or v < migliore:
                migliore = v
                stato = {k: x.clone() for k, x in m.state_dict().items()}
            if len(curva) - 1 - curva.index(min(curva)) >= pazienza:
                break
    if stato is None:   # nessuna valutazione (passi < OGNI): si usa lo stato finale
        curva.append(valuta(m, val))
    else:
        m.load_state_dict(stato)
    return dict(bpc=valuta(m, prova), bpc0=bpc0, val=min(curva), passi=passo, valutazioni=len(curva),
                curva_val=curva, al_limite=passo >= passi)


def percorso_cervello(L, seme):
    return os.path.join(CERVELLI_DIR, '%s_s%d.pt' % (nome_file(L), seme))


def corsa(l):
    inizio = time.time()
    tipo, seme = l['tipo'], l['seme']
    if tipo == 'cervello':
        m = costruisci(l['V'], seme)
        r = addestra(m, l, seme, LR, PASSI, PAZIENZA)
        os.makedirs(CERVELLI_DIR, exist_ok=True)
        p = percorso_cervello(l['cervello'], seme)
        torch.save(dict(cfg=CFG, V=l['V'], seme=seme, stato=m.state_dict()), p + '.tmp')
        os.replace(p + '.tmp', p)
    elif tipo == 'zero':
        m = costruisci(l['V'], seme)
        r = addestra(m, l, seme, LR, PASSI, PAZIENZA)
    elif tipo == 'casuale':
        m = costruisci_ad(l['V'], seme)
        r = addestra(m, l, seme, LR_AD, PASSI_AD, PAZIENZA_AD, registra0=True)
    else:   # 'ad' (nucleo del cervello) e 'casavvio' (nucleo casuale, stesso avvio per frequenza dal cervello)
        c = torch.load(percorso_cervello(l['cervello'], seme))
        if c['cfg'] != CFG:
            raise RuntimeError('il cervello %s seme %d è stato fatto con altri parametri' % (l['cervello'], seme))
        nucleo = {k[4:]: v for k, v in c['stato'].items() if k.startswith('gru.')} if tipo == 'ad' else None
        m = costruisci_ad(l['V'], seme, nucleo)
        if AVVIO == 'frequenza':
            avvio_per_frequenza(m, c['stato'], rango(l['add'], l['V']), l['rango_cervello'])
        r = addestra(m, l, seme, LR_AD, PASSI_AD, PAZIENZA_AD, registra0=True)
    r.update(tipo=tipo, seme=seme, V=l['V'], testo=l.get('testo', ''), cervello=l.get('cervello', ''),
             h1=round(e95.h1(l['add'], l['prova'], l['V']), 5), secondi=round(time.time() - inizio, 1))
    return r


# ---------------------------------------------------------------- analisi

def chiave(r):
    return (r['tipo'], r['testo'], r['cervello'], r['seme'])


def media(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def analizza(bers, cervelli, corse):
    zero, cas, ad, ad0, cav, cerv, v_bers = {}, {}, {}, {}, {}, {}, {}
    for r in corse:
        t = r['tipo']
        if t == 'zero':
            zero.setdefault(r['testo'], {})[r['seme']] = r['bpc']
            v_bers[r['testo']] = r['V']
        elif t == 'casuale':
            cas.setdefault(r['testo'], {})[r['seme']] = r['bpc']
        elif t == 'ad':
            ad.setdefault(r['testo'], {}).setdefault(r['cervello'], {})[r['seme']] = r['bpc']
            ad0.setdefault(r['testo'], {}).setdefault(r['cervello'], {})[r['seme']] = r.get('bpc0')
        elif t == 'casavvio':
            cav.setdefault(r['testo'], {}).setdefault(r['cervello'], {})[r['seme']] = r['bpc']
        else:
            cerv.setdefault(r['cervello'], {})[r['seme']] = r
    v_cerv = {M: list(cerv[M].values())[0]['V'] for M in cerv if cerv[M]}
    per = OrderedDict()
    for T, b in bers.items():
        semi = [s for s in SEMI if s in zero.get(T, {}) and s in cas.get(T, {})]
        if not semi:
            continue
        den = {s: cas[T][s] - zero[T][s] for s in semi}
        den_m = statistics.mean(den.values())
        con_tg = den_m >= DEN_MIN
        righe = OrderedDict()
        for M in cervelli:
            ss = [s for s in semi if s in ad.get(T, {}).get(M, {})]
            if len(ss) < len(semi):
                continue
            g = [cas[T][s] - ad[T][M][s] for s in ss]
            tg = [x / den[s] for x, s in zip(g, ss)] if con_tg else None
            riga = dict(V=v_cerv.get(M), bpc=statistics.mean(ad[T][M][s] for s in ss), g=e95.media_ds(g),
                        TG=e95.media_ds(tg) if tg else None, bpc_al_passo_0=media(ad0[T][M].get(s) for s in ss))
            if all(s in cav.get(T, {}).get(M, {}) for s in semi):
                # nucleo casuale con lo stesso avvio per frequenza: separa l'eco delle frequenze dal contributo del nucleo
                riga['bpc_casuale_con_avvio'] = statistics.mean(cav[T][M][s] for s in semi)
                riga['eco_dell_avvio_bit'] = e95.media_ds([cas[T][s] - cav[T][M][s] for s in semi])
                riga['contributo_del_nucleo_bit'] = e95.media_ds([cav[T][M][s] - ad[T][M][s] for s in semi])
                if con_tg:
                    riga['TG_del_nucleo'] = e95.media_ds([(cav[T][M][s] - ad[T][M][s]) / den[s] for s in semi])
            righe[M] = riga
        if not righe:
            continue
        ordine = sorted(righe, key=lambda M: righe[M]['bpc'])
        r = OrderedDict(ruolo=b['ruolo'], V=v_bers.get(T), semi=semi, bpc_zero=statistics.mean(zero[T][s] for s in semi),
                        bpc_casuale=statistics.mean(cas[T][s] for s in semi), denominatore=den_m,
                        denominatore_minimo_fra_semi=min(den.values()), con_TG=con_tg, cervelli=righe, ordine=ordine)
        if len(ordine) > 1:
            primo, secondo = ordine[0], ordine[1]
            d = [ad[T][secondo][s] - ad[T][primo][s] for s in semi]
            r['primo'], r['secondo'] = primo, secondo
            r['margine_bit'] = e95.media_ds(d)
            if con_tg:
                r['margine_TG'] = righe[primo]['TG']['media'] - righe[secondo]['TG']['media']
        per[T] = r
    return per, cerv


def info_tg(r, ammessi=None):
    """Il cervello con il TG più alto fra gli ammessi e i suoi scarti: da qualsiasi altro cervello e dal miglior cervello
    di un'altra famiglia."""
    tg = {M: v['TG']['media'] for M, v in r['cervelli'].items() if v['TG'] and (ammessi is None or M in ammessi)}
    if len(tg) < 2:
        return None
    ordine = sorted(tg, key=tg.get, reverse=True)
    p, s = ordine[0], ordine[1]
    altre = [tg[M] for M in ordine if famiglia(M) != famiglia(p)]
    return OrderedDict(migliore=p, famiglia=famiglia(p), TG=tg[p], TG_ds=r['cervelli'][p]['TG']['ds'], secondo=s,
                       TG_secondo=tg[s], scarto_qualsiasi=tg[p] - tg[s],
                       miglior_altra_famiglia=max(altre) if altre else None,
                       scarto_famiglia=(tg[p] - max(altre)) if altre else None,
                       TG_mediano=statistics.median(tg.values()), TG_minimo=min(tg.values()), n_cervelli=len(tg))


def criterio(i):
    """TG* alto e staccato dal miglior cervello di un'altra famiglia."""
    return bool(i is not None and i['TG'] >= TG_ALTO and i['scarto_famiglia'] is not None
                and i['scarto_famiglia'] >= MARGINE_TG)


def valuta_cifrato(r, C):
    """Esito di un cifrato per il cervello giusto (uno di C)."""
    giusti = [M for M in r['cervelli'] if M in C]
    if not giusti or not r['con_TG']:
        return dict(riuscito=False, motivo='manca il cervello giusto o il denominatore è piccolo')
    mg = min(giusti, key=lambda M: r['cervelli'][M]['bpc'])
    tg = {M: v['TG']['media'] for M, v in r['cervelli'].items()}
    tg_g = tg[mg]
    sbagliati = [tg[M] for M in tg if M not in C]
    altre = [tg[M] for M in tg if famiglia(M) != famiglia(mg)]
    vince = r['ordine'][0] in C
    scarto_fam = (tg_g - max(altre)) if altre else None
    riuscito = bool(vince and tg_g >= TG_ALTO and scarto_fam is not None and scarto_fam >= MARGINE_TG)
    return dict(riuscito=riuscito, cervello_migliore=r['ordine'][0], giusto_migliore=vince, TG_giusto=tg_g,
                TG_giusto_ds=r['cervelli'][mg]['TG']['ds'], TG_miglior_sbagliato=max(sbagliati) if sbagliati else None,
                scarto_qualsiasi=(tg_g - max(sbagliati)) if sbagliati else None, scarto_famiglia=scarto_fam,
                migliore_per_TG=max(tg, key=tg.get), V=r['V'])


def controlli(per, bers):
    out = OrderedDict()
    cif = [T for T in per if bers[T]['ruolo'] == 'cifrato']
    if cif:
        dett, ok, max_sbagliati, nonval = OrderedDict(), 0, [], []
        valutabili = [T for T in cif if per[T]['con_TG'] and per[T]['denominatore_minimo_fra_semi'] >= DEN_ETICHETTA]
        for T in cif:
            if T not in valutabili:
                dett[T] = dict(riuscito=None, motivo='la differenza casuale - da zero è sotto %.2f bit in almeno un seme: '
                               'non valutabile' % DEN_ETICHETTA)
                nonval.append(T)
                continue
            d = valuta_cifrato(per[T], bers[T]['giusti'])
            dett[T] = d
            ok += d['riuscito']
            if d.get('TG_miglior_sbagliato') is not None:
                max_sbagliati.append(d['TG_miglior_sbagliato'])
        su = len(valutabili)
        ammessi = int(round(QUOTA_FALLITI * su))
        gaps = [d['scarto_famiglia'] for d in dett.values() if d.get('riuscito')]
        out['positivo'] = OrderedDict(
            riusciti=ok, su=su, non_valutabili=nonval, massimo_falliti=ammessi,
            superato=(su - ok) <= ammessi and su >= min(MIN_VALUTABILI, len(cif)), soglia_TG=TG_ALTO,
            TG_giusto_minimo=min((d['TG_giusto'] for d in dett.values() if d.get('TG_giusto') is not None), default=None),
            TG_sbagliato_massimo=max(max_sbagliati, default=None),
            # distribuzione del massimo fra i cervelli sbagliati, un valore per cifrato: P95 di quella distribuzione
            TG_sbagliato_p95=(sorted(max_sbagliati)[int(0.95 * (len(max_sbagliati) - 1))] if max_sbagliati else None),
            scarto_famiglia_minimo=min(gaps, default=None),
            scarto_famiglia_mediano=statistics.median(gaps) if gaps else None, dettaglio=dett)
    desc = OrderedDict()
    for T in per:
        if bers[T]['ruolo'] in ('cifrato_altro', 'sonda'):
            desc[T] = valuta_cifrato(per[T], bers[T]['giusti'])
            desc[T]['ruolo'] = bers[T]['ruolo']
    if desc:
        out['descrittivo'] = desc
    neg = [T for T in per if bers[T]['ruolo'] == 'negativo']
    if neg:
        d = OrderedDict()
        for T in neg:
            gs = {M: v['g']['media'] for M, v in per[T]['cervelli'].items()}
            mx = max(gs, key=gs.get)
            d[T] = dict(guadagno_massimo=gs[mx], cervello=mx, denominatore=per[T]['denominatore'],
                        superato=gs[mx] <= SOGLIA_NEG)
        out['negativo'] = OrderedDict(superato=all(x['superato'] for x in d.values()), soglia_bit=SOGLIA_NEG,
                                      dettaglio=d)
    return out


def letture(per, bers, ctrl):
    """Lettura preregistrata per ogni bersaglio che non è un controllo (Voynich e generatori)."""
    pos = ctrl.get('positivo')
    controlli_ok = bool(pos and pos['superato'] and ctrl.get('negativo', {'superato': True})['superato'])
    basso = pos['TG_sbagliato_p95'] if pos else None
    info = OrderedDict()
    for T, r in per.items():
        if bers[T]['ruolo'] not in ('voynich', 'generatore'):
            continue
        i = info_tg(r)
        if i is None:
            continue
        i['denominatore_minimo_fra_semi'] = r['denominatore_minimo_fra_semi']
        i['ruolo'] = bers[T]['ruolo']
        i['criterio'] = criterio(i)
        # stessa analisi con i soli cervelli che hanno almeno tanti segni del bersaglio (gli altri lasciano segni casuali)
        grandi = {M for M, v in r['cervelli'].items() if v['V'] is not None and v['V'] >= r['V']}
        ir = info_tg(r, grandi)
        i['con_i_soli_cervelli_con_almeno_tanti_segni'] = None if ir is None else OrderedDict(
            migliore=ir['migliore'], TG=ir['TG'], scarto_famiglia=ir['scarto_famiglia'],
            scarto_qualsiasi=ir['scarto_qualsiasi'], criterio=criterio(ir), n_cervelli=ir['n_cervelli'])
        info[T] = i
    gen_crit = [T for T, i in info.items() if i['ruolo'] == 'generatore' and i['criterio']]
    out = OrderedDict()
    for T, i in info.items():
        if not controlli_ok:
            et = 'non leggibile: un controllo non è riuscito'
        elif i['denominatore_minimo_fra_semi'] < DEN_ETICHETTA:
            et = 'non leggibile: la differenza fra rete casuale e rete da zero è sotto %.2f bit in un seme (TG instabile)' \
                 % DEN_ETICHETTA
        elif i['criterio']:
            if gen_crit:
                et = 'il metodo non distingue: lo stesso criterio (TG >= %.2f e scarto >= %.2f) è raggiunto anche da %s' % (
                    TG_ALTO, MARGINE_TG, ', '.join(gen_crit))
            else:
                et = 'il cervello %s aiuta come aiuta sui cifrati di %s; non è una lettura del testo' % (
                    i['migliore'], i['migliore'])
                if i['scarto_qualsiasi'] < MARGINE_TG:
                    et += ' (non si distingue da un cervello della stessa famiglia: %s)' % i['famiglia']
        elif i['TG'] >= TG_ALTO:
            et = 'generico: più lingue aiutano quasi allo stesso modo, nessuna in particolare (migliore %s)' % i['migliore']
        elif basso is not None and i['TG'] <= basso:
            et = 'nessuna lingua lo spiega come sostituzione semplice segno per segno: ogni cervello aiuta al più quanto ' \
                 'il miglior cervello sbagliato aiuta su un cifrato vero'
        else:
            et = 'intermedio: aiuta più di una lingua sbagliata ma non al livello dei cifrati veri'
        i['lettura'] = et
        i['p95_massimo_sbagliati_nei_controlli'] = basso
        out[T] = i
    # lettura 1: il Voynich è coerente se A e B indicano lo stesso cervello; lettura 6: sensibilità alla trascrizione
    if 'Voynich' in out:
        v = out['Voynich']
        parti = [n for n in ('Voynich', 'Voynich A', 'Voynich B') if n in out]
        v['coerente_con_A_e_B'] = bool(len(parti) == 3 and all(out[n]['criterio'] for n in parti) and
                                       len({out[n]['migliore'] for n in parti}) == 1)
        sens = 'Voynich in lettere EVA non fuse (sensibilità)'
        if sens in out:
            v['stessa_lettura_con_lettere_non_fuse'] = bool(out[sens]['criterio'] == v['criterio'] and
                                                            out[sens]['migliore'] == v['migliore'])
        note = []
        if v['criterio'] and not gen_crit and controlli_ok:
            if not v['coerente_con_A_e_B']:
                note.append('A e B non indicano lo stesso cervello con lo stesso criterio: dipende dalla parte')
            if v.get('stessa_lettura_con_lettere_non_fuse') is False:
                note.append('con le lettere EVA non fuse la lettura cambia: dipende dalla trascrizione')
        rv = v['con_i_soli_cervelli_con_almeno_tanti_segni']
        if rv is not None and rv['criterio'] != v['criterio']:
            note.append('con i soli cervelli con almeno tanti segni il criterio cambia')
        if note:
            v['lettura'] += ' [' + '; '.join(note) + ']'
    return out


def correlazioni(per):
    """Spearman fra il vettore di TG sui cervelli del Voynich e quello degli altri bersagli."""
    out = OrderedDict()
    for ref in ('Voynich',):
        if ref not in per or not per[ref]['con_TG']:
            continue
        for T, r in per.items():
            if T == ref or not r['con_TG']:
                continue
            ms = [M for M in per[ref]['cervelli'] if M in r['cervelli']]
            if len(ms) < 5:
                continue
            out['%s ~ %s' % (ref, T)] = e95.spearman([per[ref]['cervelli'][M]['TG']['media'] for M in ms],
                                                    [r['cervelli'][M]['TG']['media'] for M in ms])
    return out


def eco_e_nucleo(per):
    """Per i bersagli con il riferimento "nucleo casuale + avvio per frequenza": media sui cervelli di quanto vale l'avvio
    da solo (casuale - casuale con avvio), di quanto aggiunge il nucleo addestrato (casuale con avvio - cervello) e, per il
    cervello migliore, gli stessi due numeri."""
    out = OrderedDict()
    for T, r in per.items():
        eco = {M: v['eco_dell_avvio_bit']['media'] for M, v in r['cervelli'].items() if 'eco_dell_avvio_bit' in v}
        if not eco:
            continue
        nuc = {M: r['cervelli'][M]['contributo_del_nucleo_bit']['media'] for M in eco}
        den = r['denominatore']
        out[T] = OrderedDict(
            n_cervelli=len(eco), eco_medio_bit=statistics.mean(eco.values()), nucleo_medio_bit=statistics.mean(nuc.values()),
            eco_massimo_bit=max(eco.values()), denominatore_bit=den,
            per_il_cervello_migliore=OrderedDict(cervello=r['ordine'][0], eco_bit=eco.get(r['ordine'][0]),
                                                 nucleo_bit=nuc.get(r['ordine'][0])),
            quota_eco_su_denominatore=statistics.mean(eco.values()) / den if den else None)
    return out


def scrivi(bers, cervelli, corse, versioni, origini):
    per, cerv = analizza(bers, cervelli, corse)
    ctrl = controlli(per, bers)
    lett = letture(per, bers, ctrl)
    corr = correlazioni(per)
    eco = eco_e_nucleo(per)
    ris = OrderedDict(
        esperimento='ia04',
        parametri=dict(CFG, SEMI=SEMI, PASSI_AD=PASSI_AD, PAZIENZA_AD=PAZIENZA_AD, LR_AD=LR_AD, AVVIO=AVVIO, DEN_MIN=DEN_MIN,
                       DEN_ETICHETTA=DEN_ETICHETTA, TG_ALTO=TG_ALTO, MARGINE_TG=MARGINE_TG, SOGLIA_NEG=SOGLIA_NEG,
                       QUOTA_FALLITI=QUOTA_FALLITI, MIN_VALUTABILI=MIN_VALUTABILI, SOLO_CONTROLLI=SOLO_CONTROLLI,
                       CAS_AVVIO_SU=sorted(CAS_AVVIO_SU), FAMIGLIE=FAMIGLIA),
        versioni=versioni, origine_dei_cifrati={k: v for k, v in origini.items()},
        cervelli={M: OrderedDict((s, dict(bpc=r['bpc'], passi=r['passi'], al_limite=r['al_limite'], V=r['V']))
                                 for s, r in sorted(cerv.get(M, {}).items())) for M in cervelli},
        controlli=ctrl, bersagli=per, letture=lett, eco_e_nucleo=eco, correlazioni_con_il_voynich=corr)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')

    def f3(x, n=3):
        return '–' if x is None else ('%.' + str(n) + 'f') % x

    sintesi = []
    if 'positivo' in ctrl:
        c = ctrl['positivo']
        sintesi.append('controllo positivo: %s (%d cifrati su %d con il cervello giusto migliore, TG >= %.2f e scarto dal '
                       'miglior cervello di un\'altra famiglia >= %.2f; ammessi %d falliti; non valutabili %d; TG giusto '
                       'minimo %s; massimo-fra-gli-sbagliati: massimo %s, 95° percentile %s)' % (
                           'riuscito' if c['superato'] else 'FALLITO', c['riusciti'], c['su'], c['soglia_TG'], MARGINE_TG,
                           c['massimo_falliti'], len(c['non_valutabili']), f3(c['TG_giusto_minimo']),
                           f3(c['TG_sbagliato_massimo']), f3(c['TG_sbagliato_p95'])))
    if 'negativo' in ctrl:
        c = ctrl['negativo']
        sintesi.append('controllo negativo: %s (guadagno massimo di un cervello sul testo rimescolato, soglia %.3f bit: %s)'
                       % ('riuscito' if c['superato'] else 'FALLITO', c['soglia_bit'],
                          '; '.join('%s %.4f (%s)' % (T, d['guadagno_massimo'], d['cervello'])
                                    for T, d in c['dettaglio'].items())))
    r = ['# ia04 — il cervello di una lingua', '']
    r += sintesi
    r += ['', 'Cervelli: GRU a caratteri (%d unità), addestrati come in e3c95 (%d segni, arresto sulla validazione), '
          'semi %s. Adattamento: immersione e uscita nuove, nucleo bloccato, avvio %s, passo %g, al massimo %d passi, '
          'pazienza %d.' % (NASCOSTO, N_ADD, ', '.join(map(str, SEMI)), AVVIO, LR_AD, PASSI_AD, PAZIENZA_AD),
          'Valori: media dei semi (deviazione standard). BPC in bit per segno; g = BPC_casuale - BPC_cervello; '
          'TG = g / (BPC_casuale - BPC_zero).', '']
    corse_lim = sum(1 for c in corse if c.get('al_limite'))
    r += ['Corse arrivate al massimo dei passi: %d su %d.' % (corse_lim, len(corse)), '']
    r += ['## Cervelli (BPC sulla prova; i segni sono il numero V dell\'alfabeto)', '',
          '| lingua | famiglia | segni | BPC | passi |', '|---|---|---|---|---|']
    for M in cervelli:
        cs = cerv.get(M, {})
        if cs:
            r.append('| %s | %s | %d | %s | %s |' % (M, famiglia(M), list(cs.values())[0]['V'],
                                                   f3(media(c['bpc'] for c in cs.values())),
                                                   f3(media(c['passi'] for c in cs.values()), 0)))
    r += ['', '## Bersagli: riferimenti e cervelli migliori (per BPC)', '',
          '| bersaglio | ruolo | segni | casuale | zero | den. min. | 1° (TG) | 2° (TG) | scarto TG | g del 1° |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for T, x in per.items():
        if len(x['ordine']) < 1:
            continue
        a = x['ordine'][0]
        b = x['ordine'][1] if len(x['ordine']) > 1 else None
        tga = x['cervelli'][a]['TG']
        tgb = x['cervelli'][b]['TG'] if b else None
        r.append('| %s | %s | %s | %s | %s | %s | %s (%s) | %s (%s) | %s | %s |' % (
            T, x['ruolo'], x['V'], f3(x['bpc_casuale']), f3(x['bpc_zero']), f3(x['denominatore_minimo_fra_semi']), a,
            f3(tga and tga['media']), b or '–', f3(tgb and tgb['media']), f3(x.get('margine_TG')),
            f3(x['cervelli'][a]['g']['media'])))
    if 'positivo' in ctrl:
        r += ['', '## Controllo positivo, cifrato per cifrato (stesso testo)', '',
              '| cifrato | riuscito | migliore | TG giusto (ds) | TG miglior sbagliato | scarto qualsiasi | scarto altra famiglia |',
              '|---|---|---|---|---|---|---|']
        for T, d in ctrl['positivo']['dettaglio'].items():
            r.append('| %s | %s | %s | %s (%s) | %s | %s | %s |' % (
                T, {True: 'sì', False: 'NO', None: 'non valutabile'}[d['riuscito']], d.get('cervello_migliore', '–'),
                f3(d.get('TG_giusto')), f3(d.get('TG_giusto_ds')), f3(d.get('TG_miglior_sbagliato')),
                f3(d.get('scarto_qualsiasi')), f3(d.get('scarto_famiglia'))))
    if 'descrittivo' in ctrl:
        r += ['', '## Cifrati descrittivi (altro testo della lingua) e sonda degradata: non contano nel controllo', '',
              '| bersaglio | tipo | migliore per BPC | TG giusto (ds) | TG miglior sbagliato | scarto qualsiasi | scarto altra famiglia |',
              '|---|---|---|---|---|---|---|']
        for T, d in ctrl['descrittivo'].items():
            r.append('| %s | %s | %s | %s (%s) | %s | %s | %s |' % (
                T, d['ruolo'], d.get('cervello_migliore', '–'), f3(d.get('TG_giusto')), f3(d.get('TG_giusto_ds')),
                f3(d.get('TG_miglior_sbagliato')), f3(d.get('scarto_qualsiasi')), f3(d.get('scarto_famiglia'))))
    r += ['', '## Letture preregistrate (Voynich, generatori, gibberish)', '']
    for T, d in lett.items():
        rr = d['con_i_soli_cervelli_con_almeno_tanti_segni']
        r.append('- %s: %s. Migliore %s (TG %.3f, ds %.3f), secondo %s (%.3f); scarto da qualsiasi altro %.3f, dal miglior '
                 'cervello di un\'altra famiglia %s; TG mediano %.3f, minimo %.3f; criterio %s%s' % (
                     T, d['lettura'], d['migliore'], d['TG'], d['TG_ds'], d['secondo'], d['TG_secondo'],
                     d['scarto_qualsiasi'], f3(d['scarto_famiglia']), d['TG_mediano'], d['TG_minimo'],
                     'raggiunto' if d['criterio'] else 'non raggiunto',
                     '' if rr is None else '; con i soli cervelli con almeno tanti segni (%d): migliore %s, TG %.3f, '
                                          'scarto altra famiglia %s, criterio %s' % (
                                              rr['n_cervelli'], rr['migliore'], rr['TG'], f3(rr['scarto_famiglia']),
                                              'raggiunto' if rr['criterio'] else 'non raggiunto')))
    if eco:
        r += ['', '## Eco delle frequenze e contributo del nucleo (nucleo casuale con lo stesso avvio per frequenza)', '',
              '| bersaglio | cervelli | eco medio (bit) | nucleo medio (bit) | casuale - zero (bit) | quota eco | '
              'cervello migliore: eco / nucleo |', '|---|---|---|---|---|---|---|']
        for T, d in eco.items():
            p = d['per_il_cervello_migliore']
            r.append('| %s | %d | %s | %s | %s | %s | %s: %s / %s |' % (
                T, d['n_cervelli'], f3(d['eco_medio_bit']), f3(d['nucleo_medio_bit']), f3(d['denominatore_bit']),
                f3(d['quota_eco_su_denominatore']), p['cervello'], f3(p['eco_bit']), f3(p['nucleo_bit'])))
    r += ['', '## Correlazione dei TG sui cervelli: Voynich contro gli altri bersagli (Spearman)', '']
    for k, v in corr.items():
        r.append('- %s: %s' % (k, f3(v)))
    r += ['', '## TG per cervello (righe: bersagli; colonne: cervelli)', '']
    ms = list(cervelli)
    r.append('| bersaglio | ' + ' | '.join(m[:8] for m in ms) + ' |')
    r.append('|---|' + '---|' * len(ms))
    for T, x in per.items():
        r.append('| %s | ' % T + ' | '.join(
            f3(x['cervelli'][m]['TG']['media'] if m in x['cervelli'] and x['cervelli'][m]['TG'] else
               (x['cervelli'][m]['g']['media'] if m in x['cervelli'] else None), 2) for m in ms) + ' |')
    r.append('')
    r.append('(Dove il denominatore è sotto %.2f bit la cella mostra g, in bit, non TG.)' % DEN_MIN)
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris, sintesi


# ---------------------------------------------------------------- esecuzione

def main():
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=np.__version__)
    os.makedirs(USCITA, exist_ok=True)
    cat = catalogo_testi()
    lingue_n = [n for n, v in cat.items() if v['ruolo'] == 'lingua']
    cervelli = filtra(lingue_n, 'CERVELLI')
    bers_tutti = bersagli(cat, lingue_n)
    bers = OrderedDict((k, bers_tutti[k]) for k in filtra(bers_tutti, 'TESTI'))
    origini = {k: v.get('origine') for k, v in bers.items() if v.get('origine')}
    print('cervelli: %d; bersagli: %d; semi %s' % (len(cervelli), len(bers), SEMI), flush=True)
    for k, v in bers.items():
        print('  %-62s %-10s %s' % (k, v['ruolo'], v.get('origine', '')), flush=True)

    # dati
    dati_cerv, dati_bers = {}, {}
    for M in cervelli:
        alf = e95.frequenti([cat[M]['blocchi']])
        for s in SEMI:
            dati_cerv[M, s] = codifica(e95.dividi_blocchi(cat[M]['blocchi'], s), alf)
    for T, b in bers.items():
        for s in SEMI:
            p = parti_bersaglio(T, b, s, cat)
            if p is None:
                raise RuntimeError('bersaglio %s seme %d: testo troppo corto' % (T, s))
            dati_bers[T, s] = codifica(*p)
    A = [dict(tipo='cervello', cervello=M, seme=s, **dati_cerv[M, s]) for M in cervelli for s in SEMI]
    A += [dict(tipo=t, testo=T, seme=s, **dati_bers[T, s]) for T in bers for s in SEMI for t in ('zero', 'casuale')]
    rangi = {(M, s): rango(dati_cerv[M, s]['add'], dati_cerv[M, s]['V']) for M in cervelli for s in SEMI}
    B = [dict(tipo=t, testo=T, cervello=M, seme=s, rango_cervello=rangi[M, s], **dati_bers[T, s])
         for T in bers for M in cervelli for s in SEMI for t in (('ad', 'casavvio') if T in CAS_AVVIO_SU else ('ad',))]

    percorso = os.path.join(USCITA, 'ia04_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    else:
        if os.path.exists(percorso) and os.path.getsize(percorso) > 0 and os.environ.get('NUOVA') != '1':
            raise SystemExit('%s ha già corse: usa RIPRENDI=1 per continuare, NUOVA=1 per ricominciare da capo' % percorso)
        open(percorso, 'w').close()
    fatte = {chiave(c) for c in corse}

    def chiave_lavoro(l):
        return (l['tipo'], l.get('testo', ''), l.get('cervello', ''), l['seme'])
    processi = int(os.environ.get('PROCESSI', 8))
    inizio = time.time()
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        for fase, lavori in (('cervelli e riferimenti', A), ('adattamenti', B)):
            # un cervello già fatto in una corsa precedente ma senza il suo file di pesi si rifà
            da_fare = [l for l in lavori if chiave_lavoro(l) not in fatte or
                       (l['tipo'] == 'cervello' and not os.path.exists(percorso_cervello(l['cervello'], l['seme'])))]
            print('%s: %d da fare, %d già fatte' % (fase, len(da_fare), len(lavori) - len(da_fare)), flush=True)
            for i, c in enumerate(pool.imap_unordered(corsa, da_fare), 1):
                corse = [x for x in corse if chiave(x) != chiave(c)] + [c]
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(c, ensure_ascii=False) + '\n')
                print('[%s %d/%d %.0f min] %s %s%s seme %d: BPC %.3f (%d passi, %.0f s)' % (
                    fase[:4], i, len(da_fare), (time.time() - inizio) / 60, c['tipo'], c['testo'],
                    (' <- ' + c['cervello']) if c['testo'] and c['cervello'] else c['cervello'], c['seme'], c['bpc'],
                    c['passi'], c['secondi']), flush=True)
    ris, sintesi = scrivi(bers, cervelli, corse, versioni, origini)
    for riga in sintesi:
        print(riga, flush=True)


if __name__ == '__main__':
    main()
