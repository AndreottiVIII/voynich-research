# -*- coding: utf-8 -*-
"""Esperimento IA16 (ia16): un imitatore che rilegge la pagina.

Domanda: una rete che, mentre scrive, puo' rileggere tutta la pagina scritta fin li' (e la coda della pagina precedente) impara da sola
l'eco locale, il vocabolario della pagina, l'ordine fra le parole e il contatto fra le parole, e batte il v21 davanti ai giudici che
non conosce? Preregistrazione: preregistrazioni/ia16.md. Parte da IA7 (ia07: GRU 2 x 256 che scrive un libro intero con la
disposizione del vero) e ne riusa la disposizione, il condizionamento, le pieghe per foglio, la generazione onesta e il controllo di copia;
i giudici sono quelli del paper (e231, e266), il giudice K di ia11 (n-grammi con memoria di pagina, qui sulle pieghe per foglio) e il
giudice A di ia01 (riportato, "amico": non decide da solo).

Che cosa fa il codice (in parole semplici)
- Modello (imitatore_modelli.py): piccolo transformer a segni con strati locali e globali; variante P2 (pagina in corso + coda della
  precedente), ablazioni P1 (solo la pagina in corso) e R (solo la riga corrente). Due taglie fissate prima (P piccola, S media); si
  sceglie con la validazione. Gira su processore, un thread per processo.
- Fase A: 10 addestramenti (P2, due taglie, 5 pieghe per foglio, replica 0) + eventuali modelli del giudice A mancanti.
  Fase B: con la taglia scelta, P2 replica 1, P1 e R (replica 0). Fase C: libri onesti (20 P2, 10 P1, 10 R) con i giudici del paper,
  A, la copia a memoria; fase V (opzionale): modello su tutto e libro vetrina (solo in dati/cache/ia16, mai in risultati).
  Fase D: controlli dei giudici, giudice K, misure di struttura (copia netta e Λ di ia09, D di ia10, contatto di ia08, G9 del giudice 2).
  Fase S: sintesi e letture preregistrate.
- Niente messaggio nascosto: la generazione e' un campionamento ordinario a temperatura 1.
Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia16_imitatore.json e .md e, una riga per lavoro,
risultati/ia16_corse.jsonl (con RIPRENDI=1 i lavori fatti non si rifanno). Modelli, libri e profili in dati/cache/ia16 (CACHE16).

    nohup bash strumenti/coda.sh ia16 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=10:ia16" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO16=1 USCITA=<cartella fuori dal repo> python esperimenti/ia16_imitatore.py     (prova sul libro latino;
    con SOLO_CONTROLLI CACHE16, LIBRI_IA07 e MODELLI_IA07 stanno sotto USCITA, cosi' non si toccano i dati veri)

Variabili (oltre a quelle di ia07 e ia01, che si importano: SOLO_CONTROLLI, USCITA, PASSI_A, OGNI_A, PAZIENZA_A, NASCOSTO_A, CADUTA_A,
BOOT, ...): PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere A B C V D S; predefinito tutte), FILTRO (sottostringhe, separate
da |, che il nome del lavoro deve contenere). Nuove: CACHE16 (cartella di modelli, libri, profili), TAGLIE16 (P,S), EPOCHE16 (60),
PAZIENZA16 (10), N_LIBRI16 (20), N_ABL16 (10), N_STRUTTURA16 (10), PICCOLO16 (solo prove), CORSE_IA07 (risultati/ia07_corse.jsonl),
LIBRI_IA07 (dati/cache/ia07_libri), MODELLI_A16 (modelli del giudice A; predefinito quelli di ia07).
"""
import json, math, os, pickle, random, statistics, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402  (disposizione, pieghe, generazione, giudici del paper, giudice A, copia)
import ia01_giudice_neurale as G  # noqa: E402
import imitatore_modelli as IM  # noqa: E402
import imitatore_misure as MS  # noqa: E402

NOME = 'ia16_imitatore'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
# In prova (SOLO_CONTROLLI) tutto sta sotto USCITA: nessuna lettura ne' scrittura nei dati veri (libri e modelli di ia07, cache di ia16).
CACHE16 = os.environ.get('CACHE16', os.path.join(USCITA, 'ia16_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia16'))
MOD16, LIBRI16 = os.path.join(CACHE16, 'modelli'), os.path.join(CACHE16, 'libri')
MISURE16, VETRINA16 = os.path.join(CACHE16, 'misure'), os.path.join(CACHE16, 'vetrina')
TAGLIE16 = tuple(x for x in os.environ.get('TAGLIE16', 'P,S').split(',') if x)
EPOCHE16 = int(os.environ.get('EPOCHE16', 60))
PAZIENZA16 = int(os.environ.get('PAZIENZA16', 10))
N_LIBRI16 = int(os.environ.get('N_LIBRI16', 20))          # libri P2 (meta' dalla replica 0, meta' dalla 1)
N_ABL16 = int(os.environ.get('N_ABL16', 10))              # libri per ogni ablazione (P1, R)
N_STR16 = int(os.environ.get('N_STRUTTURA16', 10))        # libri per set nelle misure di struttura
PICCOLO = os.environ.get('PICCOLO16') == '1'
CORSE_IA07 = os.environ.get('CORSE_IA07', os.path.join(USCITA, 'ia07_corse.jsonl'))
LIBRI_IA07 = os.environ.get('LIBRI_IA07', I7.LIBRI if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia07_libri'))
if os.environ.get('MODELLI_A16'):
    I7.MODELLI_A = os.environ['MODELLI_A16']
MODELLI_IA07 = os.environ.get('MODELLI_IA07', I7.MODELLI if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia07_modelli'))
BOOT = int(os.environ.get('BOOT', 1000))
PIEGHE = I7.PIEGHE
VARIANTI = IM.VARIANTI
CHIAVI_V21 = I7.CHIAVI_V21[:4] if PICCOLO else I7.CHIAVI_V21     # (PICCOLO16: solo prove del codice, meno libri di riferimento)
N_IA07 = 4 if PICCOLO else 20

# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
POS_PAPER, NEG_BANDA = 0.95, (0.45, 0.55)        # controlli dei giudici del paper
POS_K, K_VEDE_V21 = 0.85, 0.65                   # controlli di K
COPIA_5GRAMMI = (0.002, 0.01)                    # quota di 5-grammi del libro presenti nel testo d'addestramento: ok / zona grigia / copia
COPIA_RIGHE = (0.001, 0.005)                     # righe intere (>= 4 parole) identiche a una riga d'addestramento
DEGENERA_VOLTE, DEGENERA_MIN = 3.0, 0.02         # righe ripetute: oltre 3 volte il naturale e oltre 2% -> "si avvita"
NUOVE_FASCIA = (0.6, 1.4)                        # parole nuove: fra 0,6 e 1,4 volte il naturale (descrittivo)
SOGLIA_TAGLIA = 0.02                             # se le due taglie differiscono meno di cosi' (bit per segno) si sceglie la piccola
G9_NOME = 'G9 JSD pagina-manoscritto'

_C = {}


# ---------------------------------------------------------------- pagine come dati di addestramento

def linee_di(seq, T):
    out = np.empty(len(seq), dtype=np.int64)
    l = -1
    for i, t in enumerate(seq):
        if t in T:
            l += 1
        out[i] = l
    return out


def dati_pagine():
    """pagina -> dict(tok, cond, linea, foglio, prev) con le sequenze di ia07 (testa di pagina, teste di riga, segni, fine riga)."""
    if 'dp' in _C:
        return _C['dp']
    righe, voc, D = I7.libro_vero(), I7.vocabolario(), I7.divisore()
    pp = I7.per_pagina(righe)
    nomi = list(pp)
    T = {voc['idx']['T:' + t] for t in 'PMUS'}
    out = OrderedDict()
    for i, p in enumerate(nomi):
        s = np.array(I7.sequenza(pp[p], voc, D), dtype=np.int64)
        out[p] = dict(nome=p, foglio=I7.foglio_di(p), tok=s, cond=s[1:4].copy(), linea=linee_di(s, T), prev=nomi[i - 1] if i else None)
    _C['dp'] = out
    return out


def pagina_modello(p, ammessi, prec):
    """La pagina `p` per il modello: con la coda (ultimi `prec` segni) della pagina precedente VERA solo se il foglio di quella e'
    fra gli `ammessi` (None: sempre). Nell'addestramento solo i fogli di addestramento, cosi' il modello non legge testo di fogli tenuti fuori."""
    dp = dati_pagine()
    d = dict(dp[p])
    pr = dp[p]['prev']
    if pr is not None and (ammessi is None or dp[pr]['foglio'] in ammessi):
        d['prev_tok'], d['prev_cond'] = dp[pr]['tok'][-prec:], dp[pr]['cond']
    else:
        d['prev_tok'] = d['prev_cond'] = None
    return d


def insiemi(piega, prec):
    """(addestramento, validazione, tenute fuori) come liste di pagine del modello. 'tutto': tutti i fogli, nessuna validazione."""
    dp = dati_pagine()
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    sa = set(f_add)
    ins = lambda ff, amm: [pagina_modello(p, amm, prec) for p, d in dp.items() if d['foglio'] in set(ff)]
    return ins(f_add, sa if piega != 'tutto' else None), ins(f_val, None), ins(f_fuori, None)


# ---------------------------------------------------------------- modelli: addestramento, file, caricamento

def seme_modello(var, taglia, piega, replica):
    k = 9 if piega == 'tutto' else piega
    return 16000 + 1000 * VARIANTI.index(var) + 100 * TAGLIE16_ORDINE.index(taglia) + 10 * replica + k


TAGLIE16_ORDINE = ('P', 'S')


def percorso_modello(var, taglia, piega, replica, est):
    return os.path.join(MOD16, 'ia16_%s_%s_%s_%d%s' % (var, taglia, piega, replica, est))


def addestra(var, taglia, piega, replica):
    inizio = time.time()
    voc = I7.vocabolario()
    cfg = IM.configurazione(taglia, var, len(voc['segni']), finestra_riga=voc['lmax'] + 8, piccolo=PICCOLO)
    add, val, fuori = insiemi(piega, cfg['prec'])
    primo = voc['primo_contenuto']
    fisse = None
    if piega == 'tutto':
        ep = [json.load(open(percorso_modello(var, taglia, k, r, '.json'), encoding='utf-8'))['epoca_scelta']
              for k in range(PIEGHE) for r in (0, 1) if os.path.exists(percorso_modello(var, taglia, k, r, '.json'))]
        fisse = int(statistics.median(ep))
    nome = '%s %s %s r%d' % (var, taglia, piega, replica)

    def messaggio(s):
        try:
            print('[%s] %s' % (nome, s), flush=True)
        except OSError:                                                   # uscita non disponibile in un processo figlio: non e' un errore
            pass
    m, cv, ca, scelta = IM.addestra_modello(cfg, add, val, primo, seme_modello(var, taglia, piega, replica), EPOCHE16, PAZIENZA16,
                                            epoche_fisse=fisse, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'addestra|%s|%s|%s|%d' % (var, taglia, piega, replica)), ('var', var), ('taglia', taglia), ('piega', piega),
                       ('replica', replica), ('parametri', sum(p.numel() for p in m.parameters())),
                       ('pagine', [len(add), len(val), len(fuori)]), ('epoche', len(ca)), ('epoca_scelta', scelta),
                       ('arrivata_al_massimo', fisse is None and len(ca) >= EPOCHE16 and scelta > EPOCHE16 - PAZIENZA16),
                       ('curva_validazione', cv), ('curva_addestramento', ca),
                       ('bpc_addestramento', round(IM.bpc_pagine(m, add, primo), 5)),
                       ('bpc_validazione', round(IM.bpc_pagine(m, val, primo), 5) if val else None),
                       ('bpc_fuori', round(IM.bpc_pagine(m, fuori, primo), 5) if fuori else None)])
    if fuori:
        ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    ris['secondi'] = round(time.time() - inizio, 1)
    IM.salva_modello(m, percorso_modello(var, taglia, piega, replica, '.pt'), voc['segni'],
                     dict(var=var, taglia=taglia, piega=piega, replica=replica, epoca_scelta=scelta, solo_prova=bool(SOLO_CONTROLLI)))
    json.dump(ris, open(percorso_modello(var, taglia, piega, replica, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def carica(var, taglia, piega, replica):
    k = ('modello', var, taglia, piega, replica)
    if k not in _C:
        _C[k] = IM.carica_modello(percorso_modello(var, taglia, piega, replica, '.pt'), I7.vocabolario()['segni'])
    return _C[k]


def taglia_scelta():
    """La taglia scelta dalla validazione media del modello P2 (replica 0, 5 pieghe) fra le taglie provate; a parita' (meno di 0,02 bit per
    segno) la piccola. Scritta in CACHE16/taglia_scelta.json la prima volta che tutti i modelli della fase A sono pronti."""
    p = os.path.join(CACHE16, 'taglia_scelta.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    medie = OrderedDict()
    for t in TAGLIE16:
        v = []
        for k in range(PIEGHE):
            f = percorso_modello('P2', t, k, 0, '.json')
            if not os.path.exists(f):
                break
            v.append(json.load(open(f, encoding='utf-8'))['bpc_validazione'])
        if len(v) == PIEGHE:
            medie[t] = statistics.mean(v)
    if len(medie) < len(TAGLIE16):
        raise SystemExit('FERMO: la fase A non e\' finita (mancano modelli P2 di una taglia): non si puo\' scegliere la taglia')
    ordine = sorted(medie, key=lambda t: TAGLIE16_ORDINE.index(t))
    scelta = min(ordine, key=lambda t: medie[t])
    if len(ordine) > 1 and abs(medie[ordine[0]] - medie[ordine[-1]]) < SOGLIA_TAGLIA:
        scelta = ordine[0]
    out = OrderedDict([('taglia', scelta), ('validazione_media', medie), ('regola', 'validazione media piu\' bassa; se le taglie differiscono meno di %s bit per segno, la piu\' piccola' % nu(SOGLIA_TAGLIA, 2))])
    os.makedirs(CACHE16, exist_ok=True)
    json.dump(out, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return out


# ---------------------------------------------------------------- scrivere un libro

class Penna16(I7.Penna):
    """Come la Penna di ia07 (stesse regole di scrittura), ma con il transformer e la sua cache. Campionamento a temperatura 1."""

    def __init__(self, m, voc, cache):
        super().__init__(m, voc)
        self.cache = cache
        self.T = {voc['idx']['T:' + t] for t in 'PMUS'}

    def inizia(self):
        pass

    def apri(self, cond, mem):
        import torch
        self.cache.riparti(mem)
        with torch.inference_mode():
            self.cv = self.m.vettore_cond(cond)
        self.storia = []

    def dai(self, tok):
        import torch
        with torch.inference_mode():
            lg = self.m.passo(int(tok), self.cv, self.cache, inizio_riga=tok in self.T)
        self.ultimo = lg.tolist()
        self.storia.append(int(tok))

    def distribuzione(self, amm):
        z = [self.ultimo[t] for t in amm]
        mx = max(z)
        e = [math.exp(x - mx) for x in z]
        s = sum(e)
        return [x / s for x in e]


def campiona(pr, rng):
    u, c = rng.random(), 0.0
    for i, p in enumerate(pr):
        c += p
        if u < c:
            return i
    return len(pr) - 1


def scrivi_libro(var, modello_di, seme):
    """Il libro intero, pagina per pagina nell'ordine del manoscritto. Ogni pagina e' scritta dal modello della piega che non ha visto il
    suo foglio; per P2 la coda della pagina precedente e' quella SCRITTA dal modello (non il testo vero). -> lista (pagina, inizio, parole)."""
    righe, voc = I7.libro_vero(), I7.vocabolario()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    cap_pagina = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())
    cache, prev, out = None, None, []
    for pag, rp in pp.items():
        m = modello_di(pag)
        if cache is None:
            cache = m.nuova_cache(cap_pagina + m.cfg['prec'] + 8)
        penna = Penna16(m, voc, cache)
        cond = I7.testa_pagina(rp, voc)[1:4]
        mem = m.memoria(prev[0], prev[1]) if (var == 'P2' and prev is not None) else None
        penna.apri(cond, mem)
        out += I7.percorri_pagina(penna, rp, lambda j, amm, pr: amm[campiona(pr, rng)])
        prev = (np.array(penna.storia, dtype=np.int64)[-m.cfg['prec']:], np.array(cond, dtype=np.int64))
    return out


def modello_di_replica(var, taglia, replica):
    pg = I7.pieghe()
    return lambda pag: carica(var, taglia, pg[I7.foglio_di(pag)], replica)


def replica_del_libro(var, i):
    return I7.replica_del_libro(i, N_LIBRI16) if var == 'P2' else 0


def percorso_libro(var, taglia, i):
    return os.path.join(LIBRI16, 'ia16_libro_%s_%s_%d.txt' % (var, taglia, i))


def libro_catalogo_i07():
    return range(1, N_IA07 + 1)


def lavoro_libro(var, taglia, i):
    inizio = time.time()
    replica = replica_del_libro(var, i)
    seme = 1600000 + 10000 * VARIANTI.index(var) + i
    os.makedirs(LIBRI16, exist_ok=True)
    percorso = percorso_libro(var, taglia, i)
    if os.path.exists(percorso):                    # libro gia' scritto da una corsa interrotta (stessi semi: stesso libro): lo si rilegge
        t = I7.leggi_file(percorso)
    else:
        t = scrivi_libro(var, modello_di_replica(var, taglia, replica), seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia16, libro %s %s %d' % (var, taglia, i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%s|%s|%d' % (var, taglia, i)), ('var', var), ('taglia', taglia), ('i', i), ('replica', replica),
                       ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(I7.giudica(t, os.path.join(LIBRI16, 'ia16_tabella_%s_%s_%d.npz' % (var, taglia, i))))
    try:
        ris.update(I7.giudice_A(I7.libro_A_da_righe(t)))
    except Exception as e:                                                # noqa: BLE001
        ris['A_errore'] = repr(e)
    ris['copia'] = I7.copia_onesta(t)
    ris['ripetizioni'] = MS.ripetizioni_interne({p: [ps for _, ps in rr] for p, rr in _raggruppa(t).items()})
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def _raggruppa(t):
    out = OrderedDict()
    for p, ini, ps in t:
        out.setdefault(p, []).append((ini, ps))
    return out


def lavoro_vetrina(taglia):
    """Il modello P2 su tutti i fogli (numero di epoche mediano dei modelli delle pieghe) e il libro vetrina, scritto da lui. Testo e
    immagini restano in dati/cache/ia16/vetrina (mai in risultati): in risultati solo il controllo di copia (conti e nomi di pagina)."""
    inizio = time.time()
    ris = OrderedDict([('lavoro', 'vetrina|%s' % taglia)])
    if not os.path.exists(percorso_modello('P2', taglia, 'tutto', 0, '.pt')):
        ris['addestramento'] = addestra('P2', taglia, 'tutto', 0)
    t = scrivi_libro('P2', lambda pag: carica('P2', taglia, 'tutto', 0), 1600000 + 99)
    os.makedirs(VETRINA16, exist_ok=True)
    percorso = os.path.join(VETRINA16, 'ia16_libro_vetrina.txt')
    I7.scrivi_file(t, percorso, 'ia16, libro vetrina', None)
    ris['copia'] = I7.conti_copia([ps for _, _, ps in t], [x['parole'] for x in I7.libro_vero()])
    ris['controllo_copia'] = I7.controllo_copia_vetrina(t)
    try:
        ris['immagini'] = I7.immagini(percorso, os.path.join(VETRINA16, 'pagine'), ris['controllo_copia']['pagine_pulite'])
    except Exception as e:                                                # noqa: BLE001
        ris['immagini_errore'] = repr(e)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- il catalogo dei libri da misurare

def nomi_libri():
    """Nomi dei libri esistenti: P2:i, P1:i, R:i (imitatore), I07:i (ia07), V21:k (libri v21 senza messaggio di ia01), ctrl:* (controlli)."""
    ts = taglia_scelta()['taglia']
    nomi = []
    for var, n in (('P2', N_LIBRI16), ('P1', N_ABL16), ('R', N_ABL16)):
        nomi += ['%s:%d' % (var, i) for i in range(1, n + 1) if os.path.exists(percorso_libro(var, ts, i))]
    nomi += ['I07:%d' % i for i in libro_catalogo_i07() if SOLO_CONTROLLI or os.path.exists(os.path.join(LIBRI_IA07, 'ia07_libro_senza_%d.txt' % i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    """Sottoinsieme per le misure di struttura: P2 e I07 meta' dalla replica 0 e meta' dalla 1; P1, R, V21 i primi N_STR."""
    def meta(s, n_tot):
        a = [x for x in nomi if x.split(':')[0] == s]
        k = N_STR16 // 2
        return [x for x in a if int(x.split(':')[1]) <= k or n_tot // 2 < int(x.split(':')[1]) <= n_tot // 2 + k]
    out = meta('P2', N_LIBRI16) + meta('I07', N_IA07)
    for s in ('P1', 'R', 'V21'):
        out += [x for x in nomi if x.split(':')[0] == s][:N_STR16]
    return out


def t_di(nome):
    """Il libro come lista (pagina, inizio, parole) di stringhe."""
    s, k = nome.split(':')
    if s in ('P2', 'P1', 'R'):
        return I7.leggi_file(percorso_libro(s, taglia_scelta()['taglia'], int(k)))
    if s == 'I07':
        p = os.path.join(LIBRI_IA07, 'ia07_libro_senza_%s.txt' % k)
        if os.path.exists(p):
            return I7.leggi_file(p)
        if SOLO_CONTROLLI:                    # prova: al posto del libro di ia07 un libro che rimescola le parole della riga (non e' ia07)
            return _t_da_rows(G.rimescola_parole(I7.contesto_A()['vere'], 1700000 + int(k)))
        raise RuntimeError('manca il libro di ia07 %s' % p)
    return _t_da_rows(rows_di(nome))


def _t_da_rows(rows):
    return [(p, ini, [''.join(w) for w in ws]) for p, rr in rows.items() for ini, ws in rr]


def rows_di(nome):
    """Il libro nel formato di ia01 (pagina -> righe (inizio, [parola come tupla di glifi]))."""
    s, k = nome.split(':')
    if s == 'V21':
        return I7.libro_riferimento_A('b', int(k))
    if s == 'ctrl':
        return I7.libro_controllo_A(k)
    return I7.libro_A_da_righe(t_di(nome))


# ---------------------------------------------------------------- lavori di misura (fase D)

def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    nomi = nomi_libri()
    libri = OrderedDict()
    for n in nomi:
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE16, exist_ok=True)
    with open(os.path.join(MISURE16, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])),
                        ('secondi', round(time.time() - inizio, 1))])


def media_G9(tab):
    nomi, X, nf = tab
    j = next((i for i, n in enumerate(nf) if str(n).startswith(G9_NOME)), None)
    return None if j is None else float(np.mean(np.asarray(X)[:, j]))


def lavoro_M(nome):
    """Copia netta e Λ di ia09, contatto di ia08 e G9 del giudice 2 per un libro (o per `vere`)."""
    import e266_discriminatore_forte as e266
    inizio = time.time()
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows, t = c['vere'], None
        g9 = media_G9(k['vt266'])
    else:
        rows, t = rows_di(nome), t_di(nome)
        g9 = media_G9(e266.tabella(I7.righe_ini(t), k['rif266']))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'M|%s' % nome), ('G9', g9)])
    ris.update(MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag}))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_struttura(nomi_libri()):
        testi[n] = rows_di(n)
    out, info = MS.lavoro_D(f, c, testi)
    return OrderedDict([('lavoro', 'D|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('secondi', round(time.time() - inizio, 1))])


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        tipo = args[0]
        if tipo == 'addestra':
            return addestra(args[1], args[2], args[3], int(args[4]))
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
        if tipo == 'libro':
            return lavoro_libro(args[1], args[2], int(args[3]))
        if tipo == 'vetrina':
            return lavoro_vetrina(args[1])
        if tipo == 'K':
            return lavoro_K(int(args[1]))
        if tipo == 'M':
            return lavoro_M(args[1])
        if tipo == 'D':
            return lavoro_D(int(args[1]))
        if tipo in ('O', 'caso', 'ctrlA', 'casoA'):
            return I7.lavoro(tuple(args))
        raise ValueError(tipo)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    I7.avvia_processo()


def esegui(lavori, processi, percorso, fatte):
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte and (not filtro or any(x in '|'.join(str(y) for y in a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'bpc_fuori', 'AUC_e231', 'AUC_e266', 'AUC_A', 'AUC', 'passi', 'G9') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()                      # chiusura ordinata: evita che alla fine un operaio si riavvii mentre il gruppo viene fermato
        pool.join()
    return out


def leggi_corse(percorso):
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()] if os.path.exists(percorso) else []


# ---------------------------------------------------------------- analisi e letture

def nu(v, d=3):
    return I7.nu(v, d)


def quota_media(corse_libri, chiave):
    qs = [I7.quote(r['copia']) for r in corse_libri if r.get('copia')]
    return MS.media_es([q[chiave] for q in qs])


def ref_ia07(C07):
    """Numeri di ia07 (dal suo file di corse): per libro AUC dei giudici del paper e di A, e per modello i bit per segno."""
    out = OrderedDict(libri=[], v21_A=[], bpc=OrderedDict())
    for i in libro_catalogo_i07():
        r = C07.get('libro|senza|%d' % i)
        if r:
            out['libri'].append(r)
    for k in CHIAVI_V21:
        r = C07.get('rifA|%d' % k)
        if r and r.get('AUC_A_b') is not None:
            out['v21_A'].append(r['AUC_A_b'])
    for k in range(PIEGHE):
        for rp in (0, 1):
            p = os.path.join(MODELLI_IA07, 'ia07_modello_%d_%d.json' % (k, rp))
            if os.path.exists(p):
                d = json.load(open(p, encoding='utf-8'))
                out['bpc'][(k, rp)] = (d.get('bpc_validazione'), d.get('bpc_fuori'))
    return out


def classe_giudici(m_set, v_set, nomi=('e231', 'e266', 'K')):
    """Per ogni giudice la lettura (piu' vicino / uguale / piu' lontano) del set contro il riferimento; m_set, v_set: giudice -> (media, errore)."""
    out = OrderedDict()
    for j in nomi:
        a, b = m_set.get(j, (None, None)), v_set.get(j, (None, None))
        out[j] = MS.confronta(a[0], a[1], b[0], b[1])
    return out


def esito_v21(cl):
    L = [x['lettura'] for x in cl.values()]
    if any(l == 'non calcolabile' for l in L):
        return 'non leggibile (manca un giudice)'
    vic, lon = sum(l == 'più vicino' for l in L), sum(l == 'più lontano' for l in L)
    solo_vicini = {j for j, x in cl.items() if x['lettura'] == 'più vicino'}
    if vic == len(L):
        return 'migliore del v21'
    if solo_vicini == {'K'}:
        return ('solo K scende: possibile giudice amico (K ha una memoria di pagina come l\'imitatore), non vale come sì' +
                (' (e almeno due giudici su tre sono "più lontano")' if lon >= 2 else ''))
    if lon == 0:
        return 'alla pari del v21'
    if lon >= 2:
        return 'più lontano dal vero del v21'
    return 'zona grigia'


def esito_ia07(cl):
    L = [x['lettura'] for x in cl.values()]
    if any(l == 'non calcolabile' for l in L):
        return 'non leggibile (manca un giudice)'
    vic, lon = sum(l == 'più vicino' for l in L), sum(l == 'più lontano' for l in L)
    if vic >= 2 and lon == 0:
        return 'progresso su ia07'
    if lon >= 2:
        return 'peggio di ia07'
    if vic == 0 and lon == 0:
        return 'nessun progresso su ia07 (uguale entro l\'errore)'
    return 'zona grigia'


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    ts_info = taglia_scelta()
    ts = ts_info['taglia']
    c = I7.contesto_A()
    n_pag = len(c['ids'])
    C07 = {x['lavoro']: x for x in leggi_corse(CORSE_IA07)}
    R07 = ref_ia07(C07)
    out = OrderedDict(esperimento='ia16', solo_controlli=SOLO_CONTROLLI, versioni=versioni, taglia=ts_info, errori=errori)
    # ---- modelli
    modelli = [C[k] for k in sorted(C, key=lambda x: x) if k.startswith('addestra|') and '|tutto|' not in k]
    out['modelli'] = modelli
    # media dei bit per segno per variante e taglia (descrittivo, da confrontare con ia07)
    out['bpc_medie'] = OrderedDict()
    for m in modelli:
        out['bpc_medie'].setdefault('%s %s' % (m['var'], m['taglia']), []).append(m)
    out['bpc_medie'] = OrderedDict((k, OrderedDict(modelli=len(ms), validazione=MS.media_es([x['bpc_validazione'] for x in ms])[0],
                                                   fuori=MS.media_es([x['bpc_fuori'] for x in ms])[0], epoche_scelte=MS.media_es([x['epoca_scelta'] for x in ms])[0],
                                                   al_massimo=sum(bool(x['arrivata_al_massimo']) for x in ms))) for k, ms in out['bpc_medie'].items())
    out['modelli_ia07'] = OrderedDict(('%d_%d' % kk, v) for kk, v in R07['bpc'].items())
    # ---- controlli dei giudici
    ctr = OrderedDict()
    pos = [C['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in C]
    caso = C.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=MS.media_es(pos)[0], soglia=POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=NEG_BANDA,
                                        riuscito=bool(caso) and all(NEG_BANDA[0] <= caso[k] <= NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    pa = OrderedDict((n, C['ctrlA|%s' % n].get('AUC_A') if 'ctrlA|%s' % n in C else None) for n in I7.NOMI_CTRL_A if n != 'righe')
    na = C['casoA|0']['AUC_A'] if 'casoA|0' in C else None
    ctr['A_positivo'] = OrderedDict(AUC=pa, soglia=I7.SOGLIA_POSITIVO_A, riuscito=pa.get('parole') is not None and all(v >= I7.SOGLIA_POSITIVO_A for v in pa.values() if v is not None))
    ctr['A_negativo'] = OrderedDict(AUC=na, banda=NEG_BANDA, riuscito=na is not None and NEG_BANDA[0] <= na <= NEG_BANDA[1])
    # ---- giudice K
    profs = []
    for f in range(PIEGHE):
        p = os.path.join(MISURE16, 'K_f%d.pkl' % f)
        if os.path.exists(p):
            profs.append(pickle.load(open(p, 'rb')))
    prof = MS.unisci_profili(profs) if len(profs) == PIEGHE else None
    aucK = OrderedDict()
    if prof:
        for n in prof:
            if n != 'vere':
                a = MS.auc_da_profili(prof, n, n_pag)
                if a is not None:
                    aucK[n] = a
        neg = [MS.negativo_K(prof, s) for s in range(1, MS.NEG + 1)]
        v21K = [aucK[n] for n in aucK if n.startswith('V21:')]
        posK = OrderedDict((n[5:], aucK[n]) for n in aucK if n.startswith('ctrl:') and n != 'ctrl:righe')
        ctr['K_positivo'] = OrderedDict(AUC=posK, soglia=POS_K, riuscito=bool(posK) and all(v >= POS_K for v in posK.values()))
        ctr['K_negativo'] = OrderedDict(AUC=statistics.mean(neg), valori=neg, banda=NEG_BANDA, riuscito=NEG_BANDA[0] <= statistics.mean(neg) <= NEG_BANDA[1])
        ctr['K_vede_v21'] = OrderedDict(AUC=MS.media_es(v21K)[0], soglia=K_VEDE_V21, riuscito=bool(v21K) and statistics.mean(v21K) >= K_VEDE_V21)
        ctr['ctrl_righe_rimescolate_K'] = aucK.get('ctrl:righe')
    out['controlli'] = ctr
    ok_paper = ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito']
    ok_K = bool(prof) and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito'] and ctr['K_vede_v21']['riuscito']
    ok_A = ctr['A_positivo']['riuscito'] and ctr['A_negativo']['riuscito']
    # ---- giudici per set
    lib = {v: [C['libro|%s|%s|%d' % (v, ts, i)] for i in range(1, (N_LIBRI16 if v == 'P2' else N_ABL16) + 1) if 'libro|%s|%s|%d' % (v, ts, i) in C] for v in VARIANTI}
    sets = OrderedDict()
    for v in VARIANTI:
        rs = lib[v]
        if not rs:
            continue
        s = OrderedDict(libri=len(rs))
        s['e231'], s['e266'] = MS.media_es([r['AUC_e231'] for r in rs]), MS.media_es([r['AUC_e266'] for r in rs])
        s['A'] = MS.media_es([r.get('AUC_A') for r in rs])
        s['K'] = MS.media_es([aucK.get('%s:%d' % (v, r['i'])) for r in rs])
        s['min_max'] = OrderedDict((j, [min(r[k] for r in rs), max(r[k] for r in rs)]) for j, k in (('e231', 'AUC_e231'), ('e266', 'AUC_e266')))
        if v == 'P2':
            s['per_replica'] = OrderedDict((j, [MS.media_es([r[k] for r in rs if r['replica'] == rp]) for rp in (0, 1)]) for j, k in (('e231', 'AUC_e231'), ('e266', 'AUC_e266')))
            s['gruppi_e266'] = OrderedDict((n, statistics.mean(r['gruppi_e266'][n] for r in rs)) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)
            # "si dichiara se le due repliche P2 differiscono piu' di 2 errori" (preregistrazione)
            s['repliche_diverse'] = OrderedDict((j, bool(len(pr) == 2 and all(x[0] is not None and x[1] is not None for x in pr) and
                                                         abs(pr[0][0] - pr[1][0]) > 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)))
                                                for j, pr in s['per_replica'].items())
        sets[v] = s
    i07 = OrderedDict(libri=len(R07['libri']))
    if R07['libri']:
        i07['e231'], i07['e266'] = MS.media_es([r['AUC_e231'] for r in R07['libri']]), MS.media_es([r['AUC_e266'] for r in R07['libri']])
        i07['A'] = MS.media_es([r.get('AUC_A') for r in R07['libri']])
    i07['K'] = MS.media_es([aucK[n] for n in aucK if n.startswith('I07:')])
    v21 = OrderedDict(libri=len(CHIAVI_V21), e231=(I7.V21['AUC_e231'][0], I7.V21['AUC_e231'][1]), e266=(I7.V21['AUC_e266'][0], I7.V21['AUC_e266'][1]),
                      K=MS.media_es([aucK[n] for n in aucK if n.startswith('V21:')]), A=MS.media_es(R07['v21_A']))
    out['giudici'] = OrderedDict(imitatore=sets, ia07=i07, v21=v21)
    # ---- copia a memoria
    rif_copia = I7.copia_riferimenti()
    nat = I7.quote(rif_copia['naturale'])
    cop = OrderedDict()
    for v in VARIANTI:
        if lib[v]:
            cop[v] = OrderedDict((k, quota_media(lib[v], k)) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))
    rep_nat = MS.ripetizioni_interne(OrderedDict((p, [x['parole'] for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items()))
    rip = OrderedDict()
    for v in VARIANTI:
        if lib[v]:
            rip[v] = OrderedDict((k, MS.media_es([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else None for r in lib[v]])) for k in rep_nat)
    giud_copia = OrderedDict()
    for v, q in cop.items():
        m5, mr = q['5-grammi'][0], q['righe intere'][0]
        l5 = 'nessuna copia rilevante' if m5 is not None and m5 <= COPIA_5GRAMMI[0] else 'copia' if m5 is not None and m5 > COPIA_5GRAMMI[1] else 'zona grigia'
        lr = 'nessuna copia rilevante' if mr is not None and mr <= COPIA_RIGHE[0] else 'copia' if mr is not None and mr > COPIA_RIGHE[1] else 'zona grigia'
        nuove = q['parole nuove'][0]
        rn = nat['parole nuove']
        interne = rip.get(v, {})
        k4 = 'righe uguali a una precedente nella pagina (>= 4 parole)'
        nat4 = rep_nat[k4][0] / rep_nat[k4][1] if rep_nat[k4][1] else 0.0
        mm = interne.get(k4, (None, None))[0]
        avvita = bool(mm is not None and mm > DEGENERA_MIN and mm > DEGENERA_VOLTE * max(nat4, 1e-9))
        giud_copia[v] = OrderedDict([('5-grammi', l5), ('righe', lr), ('copia', 'copia' in (l5, lr)), ('zona_grigia', 'zona grigia' in (l5, lr)),
                                     ('parole_nuove_ok', bool(nuove is not None and rn and NUOVE_FASCIA[0] * rn <= nuove <= NUOVE_FASCIA[1] * rn)),
                                     ('si_avvita', avvita)])
    out['copia'] = OrderedDict(imitatore=cop, naturale=nat, v21_esempio=I7.quote(rif_copia['v21 (libro d\'esempio)']) if 'v21 (libro d\'esempio)' in rif_copia else None,
                               ripetizioni=rip, ripetizioni_naturali=OrderedDict((k, v[0] / v[1] if v[1] else None) for k, v in rep_nat.items()), letture=giud_copia)
    # ---- letture 1 e 2: contro il v21 e contro ia07
    letture = OrderedDict()
    validi = OrderedDict(paper=ok_paper, K=ok_K, A=ok_A, copia_ok=bool(giud_copia.get('P2')) and not giud_copia['P2']['copia'])
    letture['validita'] = validi
    if 'P2' in sets:
        P2 = sets['P2']
        mset = {j: P2[j] for j in ('e231', 'e266', 'K', 'A')}
        c21 = classe_giudici(mset, v21)
        c07 = classe_giudici(mset, i07)
        cA21 = classe_giudici(mset, v21, ('A',))
        cA07 = classe_giudici(mset, i07, ('A',))
        e1, e2 = esito_v21(c21), esito_ia07(c07)
        if not (ok_paper and ok_K):
            e1 = e2 = 'lettura non valida (controllo dei giudici fallito: ' + ', '.join(n for n, o in (('paper', ok_paper), ('K', ok_K)) if not o) + ')'
        elif giud_copia['P2']['copia']:
            e1 += ' ma NON VALE: copia a memoria sopra la soglia'
        elif giud_copia['P2']['zona_grigia'] or giud_copia['P2']['si_avvita']:
            e1 += ' (con riserva: copia in zona grigia o scrittura che si avvita)'
        letture['L1_contro_v21'] = OrderedDict(esito=e1, giudici=c21, A_riportato=cA21['A'], A_valido=ok_A)
        letture['L2_contro_ia07'] = OrderedDict(esito=e2, giudici=c07, A_riportato=cA07['A'], A_valido=ok_A)
        # ablazioni: la memoria della pagina conta?
        abl = OrderedDict()
        for v in ('P1', 'R'):
            if v in sets:
                cl = classe_giudici({j: P2[j] for j in ('e231', 'e266', 'K')}, {j: sets[v][j] for j in ('e231', 'e266', 'K')})
                abl['P2_contro_%s' % v] = OrderedDict(giudici=cl, piu_vicino=sum(x['lettura'] == 'più vicino' for x in cl.values()),
                                                      piu_lontano=sum(x['lettura'] == 'più lontano' for x in cl.values()))
        letture['L3_ablazioni_giudici'] = abl
    out['sets'] = sets
    # ---- struttura
    M = {k[2:]: v for k, v in C.items() if k.startswith('M|')}
    Dj = [C['D|%d' % f] for f in range(PIEGHE) if 'D|%d' % f in C]
    struttura = OrderedDict()
    if 'vere' in M:
        Mv = MS.copia_netta_lambda(M['vere'], con_intervallo=True)
        Dv = MS.D_da_pieghe([x['D']['vere'] for x in Dj]) if len(Dj) == PIEGHE else None
        struttura['vere'] = OrderedDict(copia_netta=Mv['copia_netta'], copia_netta_ic=Mv['copia_netta_ic'], lam=Mv['lam'], lam_ic=Mv['lam_ic'], rho=Mv['rho'],
                                        contatto=Mv['contatto'], D=Dv, G9=M['vere'].get('G9'))
        per_set = OrderedDict()
        for nome, r in M.items():
            if nome == 'vere':
                continue
            s = nome.split(':')[0]
            x = MS.copia_netta_lambda(r)
            x['D'] = MS.D_da_pieghe([d['D'][nome] for d in Dj]) if len(Dj) == PIEGHE and all(nome in d['D'] for d in Dj) else None
            x['G9'] = r.get('G9')
            per_set.setdefault(s, []).append(x)
        misure = ('copia_netta', 'lam', 'D', 'contatto', 'G9')
        for s, xs in per_set.items():
            struttura[s] = OrderedDict((m_, MS.media_es([x[m_] for x in xs])) for m_ in misure)
            struttura[s]['libri'] = len(xs)
        L4 = OrderedDict()
        if 'P2' in struttura and 'I07' in struttura:
            for m_ in misure:
                v = struttura['vere'][m_]
                a, b = struttura['P2'][m_], struttura['I07'][m_]
                if v is None or a[0] is None or b[0] is None:
                    L4[m_] = OrderedDict(lettura='non calcolabile')
                    continue
                dm, d7 = abs(a[0] - v), abs(b[0] - v)
                e = math.sqrt((a[1] or 0) ** 2 + (b[1] or 0) ** 2)
                # frazione di cammino solo se ia07 e' lontano dal vero di oltre 2 errori e di oltre il 5% del valore vero (altrimenti il rapporto non ha senso)
                phi = (a[0] - b[0]) / (v - b[0]) if abs(v - b[0]) > max(2 * (b[1] or 0.0), 0.05 * abs(v), 1e-9) else None
                L4[m_] = OrderedDict(vero=v, imitatore=a[0], ia07=b[0], distanza_imitatore=dm, distanza_ia07=d7, errore=e, frazione_di_cammino=phi,
                                     lettura='più vicino al vero di ia07' if dm < d7 - 2 * e else 'più lontano dal vero di ia07' if dm > d7 + 2 * e else 'come ia07')
            nv = sum(x.get('lettura') == 'più vicino al vero di ia07' for x in L4.values())
            nl = sum(x.get('lettura') == 'più lontano dal vero di ia07' for x in L4.values())
            letture['L4_struttura'] = OrderedDict(esito=('struttura più vicina al vero di ia07' if nv >= 3 and nl == 0 else 'struttura come ia07' if nv == 0 and nl == 0 else
                                                          'struttura peggiore di ia07' if nl >= 3 else 'zona grigia'), vicino=nv, lontano=nl, misure=L4)
        # R resta "media"?
        if 'R' in struttura and 'P2' in struttura and 'vere' in struttura:
            v = struttura['vere']
            r_, p_ = struttura['R'], struttura['P2']
            vicini = 0
            dett = OrderedDict()
            for m_ in misure:
                if v[m_] is None or r_[m_][0] is None or p_[m_][0] is None:
                    continue
                dr, dp_ = abs(r_[m_][0] - v[m_]), abs(p_[m_][0] - v[m_])
                e = math.sqrt((r_[m_][1] or 0) ** 2 + (p_[m_][1] or 0) ** 2)
                dett[m_] = 'P2 più vicino al vero di R' if dp_ < dr - 2 * e else 'R più vicino al vero di P2' if dr < dp_ - 2 * e else 'uguali'
                vicini += dp_ < dr - 2 * e
            cr = r_['copia_netta'][0]
            letture['L3_struttura_ablazione_R'] = OrderedDict(
                esito='la memoria della pagina avvicina al vero' if vicini >= 3 and cr is not None and cr < 0.5 * v['copia_netta'] else
                'R non resta "media" (da capire)' if cr is not None and cr >= 0.5 * v['copia_netta'] else 'zona grigia',
                misure=dett, copia_netta_R=cr, copia_netta_vero=v['copia_netta'])
    out['struttura'] = struttura
    out['letture'] = letture
    # ---- vetrina e tempi
    vet = [v for k, v in C.items() if k.startswith('vetrina|')]
    out['vetrina'] = vet[0] if vet else None
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('addestra', 'libro', 'K', 'M', 'D'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and '|tutto|' not in k and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def mf(x, d=3):
    if x is None:
        return '—'
    if isinstance(x, (tuple, list)):
        return '%s ± %s' % (nu(x[0], d), nu(x[1], d)) if x[0] is not None else '—'
    return nu(x, d)


def scrivi_md(o):
    L = o['letture']
    md = ['# IA16 (ia16) — Un imitatore che rilegge la pagina', '',
          'Preregistrazione: `preregistrazioni/ia16.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()),
          '- Taglia scelta: **%s** (validazione media P2: %s). Regola: %s.' % (o['taglia']['taglia'], ', '.join('%s %s' % (k, nu(v)) for k, v in o['taglia']['validazione_media'].items()), o['taglia']['regola']), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    c = o['controlli']
    md += ['## Controlli dei giudici', '']
    md.append('- Giudici del paper, positivo (giudice 2, parole rimescolate nella riga): AUC %s, soglia ≥ %s → %s.' % (nu(c['paper_positivo']['AUC']), nu(POS_PAPER, 2), nu(c['paper_positivo']['riuscito'])))
    md.append('- Giudici del paper, negativo (etichette a caso): giudice 1 %s, giudice 2 %s, banda 0,45–0,55 → %s.' % (nu(c['paper_negativo']['AUC_e231']), nu(c['paper_negativo']['AUC_e266']), nu(c['paper_negativo']['riuscito'])))
    if 'K_positivo' in c:
        md.append('- K, positivo: %s, soglia ≥ %s → %s. Negativo (media di %d etichette): %s → %s. K vede il v21 (AUC %s, soglia ≥ %s) → %s.' % (
            ', '.join('%s %s' % (k, nu(v)) for k, v in c['K_positivo']['AUC'].items()), nu(POS_K, 2), nu(c['K_positivo']['riuscito']), len(c['K_negativo']['valori']),
            nu(c['K_negativo']['AUC']), nu(c['K_negativo']['riuscito']), nu(c['K_vede_v21']['AUC']), nu(K_VEDE_V21, 2), nu(c['K_vede_v21']['riuscito'])))
    md.append('- A (riportato), positivo: %s, soglia ≥ %s → %s. Negativo: %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['A_positivo']['AUC'].items()),
                                                                                   nu(I7.SOGLIA_POSITIVO_A, 2), nu(c['A_positivo']['riuscito']), nu(c['A_negativo']['AUC']), nu(c['A_negativo']['riuscito'])))
    md += ['', '## Modelli (pieghe per foglio; bit per segno)', '', '| modello | parametri | epoca scelta (su) | BPC add. | BPC val. | BPC fuori | scarto | minuti |', '|---|---|---|---|---|---|---|---|']
    for m in o['modelli']:
        md.append('| %s %s piega %s r%s | %d | %d (%d) | %s | %s | %s | %s | %.1f |' % (m['var'], m['taglia'], m['piega'], m['replica'], m['parametri'], m['epoca_scelta'], m['epoche'],
                                                                                nu(m['bpc_addestramento']), nu(m['bpc_validazione']), nu(m['bpc_fuori']), nu(m.get('scarto')), m['secondi'] / 60))
    md += ['', 'Medie per variante e taglia (bit per segno; epoche scelte in media; modelli arrivati al massimo di epoche): ' +
           '; '.join('%s: %d modelli, validazione %s, fuori %s, epoche %s, al massimo %d' % (k, x['modelli'], nu(x['validazione']), nu(x['fuori']), nu(x['epoche_scelte'], 1), x['al_massimo'])
                     for k, x in o['bpc_medie'].items()) + '.']
    if o['modelli_ia07']:
        v = [x[0] for x in o['modelli_ia07'].values() if x[0] is not None]
        f = [x[1] for x in o['modelli_ia07'].values() if x[1] is not None]
        md += ['', 'ia07 (GRU 2 x 256, 665.481 parametri, stesse pieghe e repliche): validazione media %s, fuori media %s bit per segno.' % (nu(statistics.mean(v)), nu(statistics.mean(f)))]
    g = o['giudici']
    md += ['', '## Giudici: libri contro libro vero (un giudice per libro; AUC, più basso = più vicino al vero)', '',
           '| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |', '|---|---|---|---|---|---|']
    for v, s in g['imitatore'].items():
        md.append('| imitatore %s | %d | %s | %s | %s | %s |' % (v, s['libri'], mf(s['e231']), mf(s['e266']), mf(s['K']), mf(s['A'])))
    md.append('| ia07 (GRU) | %d | %s | %s | %s | %s |' % (g['ia07']['libri'], mf(g['ia07'].get('e231')), mf(g['ia07'].get('e266')), mf(g['ia07'].get('K')), mf(g['ia07'].get('A'))))
    md.append('| v21 | %d | %s (paper, 24 chiavi) | %s (paper) | %s | %s |' % (g['v21']['libri'], mf(g['v21']['e231']), mf(g['v21']['e266']), mf(g['v21']['K']), mf(g['v21']['A'])))
    if 'P2' in g['imitatore']:
        s = g['imitatore']['P2']
        md += ['', 'P2 per replica dei modelli: ' + '; '.join('%s: replica 0 %s, replica 1 %s' % (j, mf(r[0]), mf(r[1])) for j, r in s['per_replica'].items()) + '.',
               'Le due repliche P2 differiscono di più di 2 errori? ' + '; '.join('%s: %s' % (j, nu(b)) for j, b in s['repliche_diverse'].items()) + '.',
               'Gruppi del giudice 2 (P2): ' + '; '.join('%s %s' % (k, nu(v, 2)) for k, v in s['gruppi_e266'].items()) + '.']
    md += ['', '## Letture preregistrate', '']
    md.append('- Validità: giudici del paper %s, K %s, A %s, copia di P2 senza soglia di "copia" superata %s.' % (nu(L['validita']['paper']), nu(L['validita']['K']), nu(L['validita']['A']), nu(L['validita']['copia_ok'])))
    for chiave, titolo in (('L1_contro_v21', 'L1, contro il v21'), ('L2_contro_ia07', 'L2, contro ia07')):
        if chiave in L:
            x = L[chiave]
            md.append('- **%s: %s.** %s. A (riportato, %s): %s.' % (titolo, x['esito'], '; '.join('%s %s (differenza %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items()),
                                                                 'valido' if x['A_valido'] else 'controlli di A non riusciti', x['A_riportato']['lettura']))
    for chiave, x in L.get('L3_ablazioni_giudici', {}).items():
        md.append('- L3, giudici, %s: %s; più vicino su %d giudici, più lontano su %d.' % (chiave.replace('_', ' '), '; '.join('%s %s' % (j, y['lettura']) for j, y in x['giudici'].items()), x['piu_vicino'], x['piu_lontano']))
    if 'L3_struttura_ablazione_R' in L:
        x = L['L3_struttura_ablazione_R']
        md.append('- **L3, struttura, P2 contro R: %s.** %s; copia netta di R %s contro %s del vero.' % (x['esito'], '; '.join('%s: %s' % kv for kv in x['misure'].items()), nu(x['copia_netta_R']), nu(x['copia_netta_vero'])))
    if 'L4_struttura' in L:
        x = L['L4_struttura']
        md.append('- **L4, struttura contro ia07: %s** (più vicino su %d misure, più lontano su %d).' % (x['esito'], x['vicino'], x['lontano']))
    st = o['struttura']
    if st:
        md += ['', '## Struttura (media ± errore standard sui libri; vero con intervallo al 95% sulle pagine)', '',
               '| testo | copia netta (bit per parola) | quota locale Λ | D (ia10) | contatto g (ia08) | G9 JSD pagina-manoscritto |', '|---|---|---|---|---|---|']
        v = st['vere']
        md.append('| vero | %s %s | %s %s | %s | %s | %s |' % (nu(v['copia_netta']), [round(x, 3) for x in v['copia_netta_ic']], nu(v['lam']), [round(x, 3) for x in v['lam_ic']], nu(v['D']), nu(v['contatto']), nu(v['G9'], 4)))
        for s, x in st.items():
            if s != 'vere':
                md.append('| %s (%d libri) | %s | %s | %s | %s | %s |' % (s, x['libri'], mf(x['copia_netta']), mf(x['lam']), mf(x['D']), mf(x['contatto']), mf(x['G9'], 4)))
        if 'L4_struttura' in L:
            md += ['', '| misura | vero | imitatore P2 | ia07 | frazione di cammino da ia07 al vero | lettura |', '|---|---|---|---|---|---|']
            for m_, x in L['L4_struttura']['misure'].items():
                md.append('| %s | %s | %s | %s | %s | %s |' % (m_, nu(x.get('vero'), 4), nu(x.get('imitatore'), 4), nu(x.get('ia07'), 4), nu(x.get('frazione_di_cammino'), 2), x['lettura']))
    cp = o['copia']
    md += ['', '## Copia a memoria e ripetizioni', '', 'Quote rispetto al testo d\'addestramento del modello che ha scritto la pagina (naturale: pagine vere tenute fuori).', '',
           '| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |', '|---|---|---|---|---|']
    for v, q in cp['imitatore'].items():
        md.append('| imitatore %s | %s |' % (v, ' | '.join(mf(q[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    md.append('| naturale | %s |' % ' | '.join(nu(cp['naturale'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    if cp.get('v21_esempio'):
        md.append('| v21 (libro d\'esempio) | %s |' % ' | '.join(nu(cp['v21_esempio'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    for v, x in cp['letture'].items():
        md.append('- %s: 5-grammi → %s, righe → %s; parole nuove %s; scrittura che si avvita: %s.' % (v, x['5-grammi'], x['righe'], 'nella fascia' if x['parole_nuove_ok'] else 'FUORI fascia', nu(x['si_avvita'])))
    md += ['', 'Ripetizioni dentro la pagina (naturale: %s):' % '; '.join('%s %s' % (k, nu(v, 4)) for k, v in cp['ripetizioni_naturali'].items())]
    for v, r in cp['ripetizioni'].items():
        md.append('- %s: %s.' % (v, '; '.join('%s %s' % (k, mf(x, 4)) for k, x in r.items())))
    if o['vetrina']:
        vt = o['vetrina']
        t = vt['controllo_copia']['totali']
        md += ['', '## Libro vetrina (modello su tutto: non è una prova onesta; testo e immagini solo in `dati/cache/ia16/vetrina`)', '',
               '- righe di almeno 3 parole identiche a una riga vera: %d su %d; 5-grammi presenti nel libro vero: %d su %d; pagine identiche: %d su %d; pagine senza copia: %d.' % (
                   t['righe copiate'], t['righe'], t['5-grammi copiati'], t['5-grammi'], t['pagina intera identica'], vt['controllo_copia']['pagine'], len(vt['controllo_copia']['pagine_pulite']))]
    md += ['', '## Tempi (minuti per lavoro, macchina condivisa)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def lavori_fase(fase):
    if fase == 'A':
        mancanti = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
        return mancanti + [('addestra', 'P2', t, k, 0) for t in reversed(TAGLIE16) for k in range(PIEGHE)]
    ts = taglia_scelta()['taglia']
    if fase == 'B':
        return ([('addestra', 'P2', ts, k, 1) for k in range(PIEGHE)] + [('addestra', 'P1', ts, k, 0) for k in range(PIEGHE)] +
                [('addestra', 'R', ts, k, 0) for k in range(PIEGHE)])
    if fase == 'C':
        return ([('libro', 'P2', ts, i) for i in range(1, N_LIBRI16 + 1)] + [('libro', 'P1', ts, i) for i in range(1, N_ABL16 + 1)] +
                [('libro', 'R', ts, i) for i in range(1, N_ABL16 + 1)])
    if fase == 'V':
        return [('vetrina', ts)]
    if fase == 'D':
        nomi = nomi_libri()
        return ([('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0), ('casoA', 0)] + [('ctrlA', n) for n in I7.NOMI_CTRL_A] + [('K', f) for f in range(PIEGHE)] +
                [('D', f) for f in range(PIEGHE)] + [('M', 'vere')] + [('M', n) for n in nomi_struttura(nomi)])
    return []


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD16, LIBRI16, MISURE16):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni, riga massima %d; taglie %s; PICCOLO %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), voc['lmax'], TAGLIE16, PICCOLO), flush=True)
    percorso = os.path.join(USCITA, 'ia16_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'ABCVDS')
    for fase in 'ABCVD':
        if fase in fasi and not (fase == 'V' and 'C' in fasi):         # V gira insieme a C se ci sono tutte e due
            lavori = lavori_fase(fase)
            if fase == 'C' and 'V' in fasi:
                lavori = lavori_fase('V') + lavori
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        for k, x in o['letture'].items():
            if isinstance(x, dict) and 'esito' in x:
                print('%s: %s' % (k, x['esito']), flush=True)


if __name__ == '__main__':
    main()
