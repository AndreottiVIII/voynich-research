# -*- coding: utf-8 -*-
"""Esperimento IA10 (ia10): "famiglie di parole" -- una grammatica in miniatura senza conoscere la lingua.

Domanda: se si raggruppano le parole in K famiglie secondo i vicini che hanno (come le categorie grammaticali di una lingua),
le famiglie si susseguono con regole? Cioe' esiste una tabella leggibile di famiglie e passaggi? E il v21 ce l'ha uguale?
(Preregistrazione: preregistrazioni/ia10.md.)

Metodo (tutto in numpy, nessuna rete neurale):
- Famiglie: algoritmo di scambio (Martin, Liermann e Ney, 1998) per il modello a classi di Brown et al. (1992): K famiglie per le
  1.000 parole piu' frequenti delle pagine di addestramento (almeno 3 volte); le altre sono una classe "rara" fissa. K = 5, 10,
  20, scelto sulle pagine di validazione (10%), senza guardare la prova. Pieghe e divisioni come ia08 (stesse pagine di ia01).
- Guadagno: bit per coppia di parole vicine nella stessa riga, rispetto a un modello senza ordine (unigrammi): log2 P(famiglia
  dopo | famiglia prima) - log2 P(famiglia dopo), sulle pagine della piega fuori.
- Controlli: testo rimescolato dentro la riga (stesso modello e modello rifatto), inglese (Brown, categorie grammaticali),
  latino (UD Latin-PROIEL, categorie), tre testi sintetici con grammatica nota (con forma, senza forma, senza ordine).
- Forma: quanto della famiglia si indovina dalla forma della parola (regressione logistica su primo/ultimo glifo, primi/ultimi
  due, lunghezza e glifi presenti, con validazione incrociata sulle parole).
- Stabilita': indice di Rand corretto fra due semi e fra pieghe. Posizione nella riga, sezione, lingua A/B: informazione
  mutua con riferimento a caso.
- v21 (libri a13-a22 di ia01): modello del Voynich vero applicato alle sue pagine (cross) e famiglie imparate dal libro (own).

Riusa ia01 (importato, non modificato): pagine, pieghe, libri, semi. Supporto: famiglie_classi.py (raggruppamento e misure),
famiglie_testi.py (inglese, latino, sintetici). Uscite: solo numeri e aggregati in risultati/ia10_famiglie_parole.json e .md e,
una riga per lavoro, risultati/ia10_corse.jsonl; l'elenco delle parole di ogni famiglia sta solo in dati/cache/ia10/uscite/
(protetto, non pubblicato).

Variabili: quelle di ia01 (SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, CHIAVI, USCITA, LIBRI) piu' FASI (fit, analisi; predefinito
'fit,analisi'), RIPRENDI, PROCESSI (non cambia i risultati), FILTRO (sottostringhe, separate da |, che il nome del lavoro deve
contenere), TESTI (elenco di testi, separati da virgola), NV, KS, GIRI, S_RIM, NULL_REP, BOOT, PERM, USCITA_CACHE.
"""
import json, math, os, pickle, random, sys, time, warnings, zlib
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import famiglie_classi as FC  # noqa: E402
import famiglie_testi as FT  # noqa: E402

NOME = 'ia10_famiglie_parole'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF, CHIAVI = G.NF, G.CHIAVI
CACHE = os.environ.get('USCITA_CACHE', os.path.join(QUI, '..', 'dati', 'cache', 'ia10', 'uscite'))


def lista_int(nome, default):
    return tuple(int(x) for x in os.environ.get(nome, default).split(',') if x)


# ---- parametri (i valori predefiniti sono quelli preregistrati)
NV_MAX = int(os.environ.get('NV', 1000))         # parole raggruppate: le piu' frequenti delle pagine di addestramento
MIN_CONT = 3                                       # ... che compaiono almeno 3 volte
KS = lista_int('KS', '5,10,20')                    # numeri di famiglie provati
K_PARSIMONIA = 0.005                               # si sceglie il K piu' piccolo con guadagno di validazione entro 0,005 bit dal migliore
GIRI = int(os.environ.get('GIRI', 20))
SEME_DIV = 1                                       # divisione addestramento/validazione: come ia08, seme 1
S_RIM = int(os.environ.get('S_RIM', 20))           # rimescolamenti del testo di prova (modello vero)
NULL_REP = int(os.environ.get('NULL_REP', 2))      # rifacimenti dell'intera procedura sul testo rimescolato dentro la riga
BOOT = int(os.environ.get('BOOT', 1000))
PERM = int(os.environ.get('PERM', 100))            # permutazioni (etichette dei tipi, pagine, rimescolamenti per la posizione)
KF = 10                                            # famiglie della tabella "finale" descrittiva (tutte le pagine)
CV_FORMA = 5
LIBRI_V21 = ['a%d' % k for k in CHIAVI]

# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
S_G_SI, S_G_NO = 0.03, 0.01             # L1: guadagno per coppia (bit)
S_NMI = 0.35                            # controllo positivo inglese: informazione mutua normalizzata con le categorie
S_NMI_MARGINE = 0.25                    # ... e almeno cosi' sopra il riferimento a caso (etichette permutate fra i tipi)
S_NMI_LATINO_MARGINE = 0.08             # latino (UD): margine sul riferimento a caso (non blocca, serve per leggere i "no")
S_SINT_NMI, S_SINT_G = 0.60, 0.20       # sintetico senza forma: NMI con le classi vere e guadagno
S_CASO_G = 0.02                         # sintetico senza ordine: guadagno al massimo
S_FORMA_SI, S_FORMA_NO = 0.40, 0.15     # L4: quota della famiglia spiegata dalla forma
S_FORMA_CTRL_ALTO, S_FORMA_CTRL_BASSO = 0.50, 0.10
S_RAPP_CELLE_SI = 0.75                  # L3: rapporto "celle per meta' probabilita'" (tabella / indipendenza), al massimo
S_RAPP_CELLE_MARGINE = 0.20             # ... e almeno cosi' sotto lo stesso rapporto della tabella imparata sul testo rimescolato
S_RAPP_CELLE_NO = 0.05                  # L3: no se la differenza dal testo rimescolato e' sotto questo valore
S_ARI_SI, S_ARI_NO = 0.15, 0.05         # L5: stabilita' fra pieghe
S_ARI_SINT_ALTO, S_ARI_SINT_BASSO = 0.50, 0.10
S_POS_RIGA = 0.005                      # L6: eccesso di informazione mutua normalizzata (famiglia, posizione nella riga)
S_POS_PAG = 0.01                        # L6: idem per sezione e lingua A/B (con il riferimento delle etichette permutate)
S_D_SENS = 0.03                         # sensibilita': perdita da rimescolamento delle vere (D) almeno cosi'
C_FORMA = 0.3                           # regolarizzazione della regressione logistica sulla forma
S_R_SI, S_R_NO = 0.50, 0.80             # L7: rapporto fra il guadagno del v21 e quello delle vere

PAROLE_MIN_PAGINA = G.MIN_PAROLE
TESTI_BASE = ['vere'] if SOLO_CONTROLLI else ['vere', 'vereA', 'vereB', 'ts', 'naibbe', 'latino']
TESTI_POS = ['inglese', 'latino_ud', 'sint_noforma', 'sint_forma', 'sint_caso']


def testi_attivi():
    t = TESTI_BASE + TESTI_POS + LIBRI_V21
    sel = [x for x in os.environ.get('TESTI', '').split(',') if x]
    return [x for x in t if x in sel] if sel else t


# ---------------------------------------------------------------- testi

_T = {}


def _filtra(pagine):
    return OrderedDict((p, r) for p, r in pagine.items() if sum(len(ws) for _, ws in r) >= PAROLE_MIN_PAGINA)


def testo(nome):
    if nome in _T:
        return _T[nome]
    c = G.contesto()
    if nome == 'vere':
        T = FT.Testo('vere', c['vere'], tipo=c['tipo'], piega=c['fold'])
    elif nome in ('vereA', 'vereB'):
        L = nome[-1]
        ps = [p for p in c['vere'] if c['tipo'][p][1] == L]
        T = FT.Testo(nome, OrderedDict((p, c['vere'][p]) for p in ps), tipo={p: c['tipo'][p] for p in ps}, piega=c['fold'])
    elif nome in LIBRI_V21:
        lib = G.libro(nome)
        T = FT.Testo(nome, OrderedDict((p, lib[p]) for p in c['vere'] if p in lib), tipo=c['tipo'], piega=c['fold'])
    elif nome == 'latino':
        v, _ = G.carica_latino()
        T = FT.Testo(nome, _filtra(v))
    elif nome in ('ts', 'naibbe'):
        import e3c95_imparabilita as e95
        blocchi = e95.timm_schinner() if nome == 'ts' else e95.naibbe()
        T = FT.Testo(nome, FT._da_blocchi(blocchi, 'T' if nome == 'ts' else 'N'))
    elif nome == 'inglese':
        T = FT.carica_brown()
    elif nome == 'latino_ud':
        T = FT.carica_latino_ud()
    elif nome.startswith('sint_'):
        T = FT.sintetico(nome[5:])
    else:
        raise ValueError(nome)
    _T[nome] = T
    return T


class Seq:
    """Una lista di pagine messa in fila: parole, riga (numero progressivo), indice di pagina, posizione nella riga
    (0 prima, 1 in mezzo, 2 ultima), categoria (se nota)."""

    def __init__(self, T, pagine):
        self.pagine = list(pagine)
        w, linea, pag, pos, cat = [], [], [], [], []
        k = 0
        for i, p in enumerate(self.pagine):
            et = T.etichette[p] if T.etichette else None
            for j, (_, ws) in enumerate(T.pagine[p]):
                n = len(ws)
                for q, x in enumerate(ws):
                    w.append(x)
                    linea.append(k)
                    pag.append(i)
                    pos.append(0 if q == 0 else 2 if q == n - 1 else 1)
                    if et is not None:
                        cat.append(et[j][q])
                k += 1
        self.w = w
        self.linea = np.array(linea, dtype=np.int64)
        self.pag = np.array(pag, dtype=np.int64)
        self.pos = np.array(pos, dtype=np.int64)
        self.cat = np.array(cat) if cat else None

    def ids(self, ix, NV):
        return np.array([ix.get(x, NV) for x in self.w], dtype=np.int64)


def vocabolario(seq):
    cont = Counter(seq.w)
    voc = [w for w, n in sorted(cont.items(), key=lambda x: (-x[1], x[0])) if n >= MIN_CONT][:NV_MAX]
    return voc, cont


# ---------------------------------------------------------------- adattamento, scelta di K, punteggi

def punteggi(tr, cls, tok, linea, pag, npag, NV):
    """Per pagina: guadagno totale (bit), numero di coppie, guadagno e numero sulle coppie con tutte e due le parole nel
    vocabolario raggruppato."""
    p = FC.coppie_di(tok, linea)
    a, b = tok[p], tok[p + 1]
    g = tr.logratio[cls[a], cls[b]]
    kk = ((a < NV) & (b < NV)).astype(float)
    pg = pag[p]
    return np.stack([np.bincount(pg, g, npag), np.bincount(pg, minlength=npag).astype(float),
                     np.bincount(pg, g * kk, npag), np.bincount(pg, kk, npag)], 1)


def adatta_e_scegli(tokA, linA, tokV, linV, NV, seme):
    """Per ogni K in KS: famiglie sulle coppie di addestramento, tabella dei passaggi, guadagno medio per coppia sulla
    validazione. Sceglie il K piu' piccolo il cui guadagno di validazione sta entro K_PARSIMONIA dal migliore."""
    pa = FC.coppie_di(tokA, linA)
    a, b = tokA[pa], tokA[pa + 1]
    graf = FC.Grafo(a, b, NV)
    pv = FC.coppie_di(tokV, linV)
    va, vb = tokV[pv], tokV[pv + 1]
    out = OrderedDict()
    for K in KS:
        cls, info = FC.adatta_famiglie(a, b, NV, K, seme, giri=GIRI, grafo=graf)
        tr = FC.Transizioni(a, b, cls, K)
        gv = float(tr.guadagno_coppie(cls[va], cls[vb]).mean()) if len(va) else float('nan')
        out[K] = dict(cls=cls, tr=tr, info=info, gval=gv)
    migliore = max(v['gval'] for v in out.values())
    Kstar = min(K for K, v in out.items() if v['gval'] >= migliore - K_PARSIMONIA)
    return out, Kstar, (a, b)


def classi_forma(voc, cont_tokens, K, tipo):
    """Famiglie "di sola forma": le parole raggruppate prendono la classe del loro ultimo (o primo) glifo; i K-1 glifi piu'
    frequenti nei testi di addestramento hanno una classe ciascuno, gli altri insieme. NV = rara."""
    NV = len(voc)
    gl = Counter()
    for w, n in zip(voc, cont_tokens):
        gl[w[-1] if tipo == 'ultimo' else w[0]] += n
    primi = [g for g, _ in sorted(gl.items(), key=lambda x: (-x[1], x[0]))[:K - 1]]
    mappa = {g: i for i, g in enumerate(primi)}
    cls = np.full(NV + 1, K, dtype=np.int64)
    for i, w in enumerate(voc):
        cls[i] = mappa.get(w[-1] if tipo == 'ultimo' else w[0], K - 1)
    return cls


# ---------------------------------------------------------------- forma

def caratteristiche(w):
    f = ['i1:' + w[0], 'f1:' + w[-1], 'i2:' + ''.join(w[:2]), 'f2:' + ''.join(w[-2:]), 'L:%d' % min(len(w), 9)]
    f += ['g:' + g for g in sorted(set(w))]
    return f


def analisi_forma(voc, cls, K, seme, pesi_tipi):
    """Quanto della famiglia (K+... solo le K famiglie vere) si indovina dalla forma della parola: regressione logistica sulle
    caratteristiche, validazione incrociata a CV_FORMA gruppi sui tipi. F = 1 - CE/H (per tipo): H = entropia delle famiglie,
    CE = entropia incrociata fuori campione; riferimento = stesso calcolo con le famiglie permutate fra i tipi. Anche
    pesata per il numero di occorrenze (solo descrittiva)."""
    from scipy.sparse import csr_matrix
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold
    NV = len(voc)
    y = cls[:NV]
    ph = [caratteristiche(w) for w in voc]
    colonne = {}
    for fs in ph:
        for f in fs:
            colonne.setdefault(f, len(colonne))
    righe, cols = [], []
    for i, fs in enumerate(ph):
        for f in fs:
            righe.append(i)
            cols.append(colonne[f])
    X = csr_matrix((np.ones(len(righe)), (righe, cols)), shape=(NV, len(colonne)))
    pesi = np.asarray(pesi_tipi, dtype=float)

    def ce_oof(yy):
        P = np.full((NV, K), 1e-3)
        for tr_i, te_i in KFold(CV_FORMA, shuffle=True, random_state=seme).split(np.arange(NV)):
            classi = np.unique(yy[tr_i])
            if len(classi) < 2:
                P[te_i, classi[0]] = 1.0
                continue
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                m = LogisticRegression(C=C_FORMA, max_iter=500)
                m.fit(X[tr_i], yy[tr_i])
            pr = m.predict_proba(X[te_i])
            P[np.ix_(te_i, m.classes_)] = np.maximum(pr, 1e-3)
        P = P / P.sum(1, keepdims=True)
        lp = -np.log2(P[np.arange(NV), yy])
        return lp

    def H(yy, w=None):
        c = np.bincount(yy, weights=w, minlength=K).astype(float)
        p = c / c.sum()
        return float(-FC.xlogx(p).sum())

    lp = ce_oof(y)
    rng = np.random.default_rng(seme + 7)
    yp = y[rng.permutation(NV)]
    lpp = ce_oof(yp)
    h, hp = H(y), H(yp)
    hw, hpw = H(y, pesi), H(yp, pesi)
    F = 1 - lp.mean() / h if h > 0 else float('nan')
    Fp = 1 - lpp.mean() / hp if hp > 0 else float('nan')
    Fw = 1 - (lp * pesi).sum() / pesi.sum() / hw if hw > 0 else float('nan')
    Fpw = 1 - (lpp * pesi).sum() / pesi.sum() / hpw if hpw > 0 else float('nan')
    return dict(F=float(F), F_perm=float(Fp), F_spiegata=float(F - Fp), F_pesata=float(Fw), F_perm_pesata=float(Fpw), H_famiglie=h)


# ---------------------------------------------------------------- etichette, posizione, sezione

def analisi_etichette(cls, tok, cat, NV, seme):
    """Informazione mutua normalizzata e purezza fra le famiglie e le categorie grammaticali (token della prova nel vocabolario
    raggruppato); riferimento: famiglie permutate fra i tipi, PERM volte."""
    m = tok < NV
    x, y = cls[tok[m]], cat[m]
    n, pur = FC.nmi(x, y)
    rng = np.random.default_rng(seme)
    rn, rp = [], []
    for _ in range(PERM):
        c2 = cls.copy()
        c2[:NV] = cls[:NV][rng.permutation(NV)]
        a, b = FC.nmi(c2[tok[m]], y)
        rn.append(a)
        rp.append(b)
    return dict(nmi=n, purezza=pur, nmi_caso=float(np.mean(rn)), nmi_caso_p97_5=float(np.percentile(rn, 97.5)), purezza_caso=float(np.mean(rp)),
                n_token=int(m.sum()))


def mi_norm(x, y):
    mi, hx, hy = FC.info_mutua_tabella(FC.tabella_contingenza(x, y))
    return mi, hx


def analisi_posizione(cls, tok, linea, pos, NV, seme):
    """Informazione mutua fra famiglia e posizione nella riga (prima, in mezzo, ultima), normalizzata con l'entropia delle famiglie;
    riferimento: parole rimescolate dentro la riga (la posizione resta quella del testo vero)."""
    m = tok < NV
    mi, h = mi_norm(cls[tok[m]], pos[m])
    rng = np.random.default_rng(seme)
    rif = []
    for _ in range(max(10, PERM // 5)):
        t2 = FC.rimescola_in_riga(tok, linea, rng)
        m2 = t2 < NV
        rif.append(mi_norm(cls[t2[m2]], pos[m2])[0])
    return dict(MI_norm=float(mi / h) if h > 0 else float('nan'), riferimento=float(np.mean(rif) / h) if h > 0 else float('nan'),
                eccesso=float((mi - np.mean(rif)) / h) if h > 0 else float('nan'), sd_rif=float(np.std(rif) / h) if h > 0 else float('nan'))


def analisi_etichetta_pagina(cls, tok, pag, npag, etich_pagina, K, NV, seme):
    """Informazione mutua normalizzata fra famiglia e un'etichetta di pagina (sezione, lingua A/B), con il riferimento delle
    etichette permutate fra le pagine. Solo pagine con l'etichetta; serve almeno 2 valori."""
    ok = np.array([e is not None for e in etich_pagina])
    valori = sorted({e for e in etich_pagina if e is not None})
    if len(valori) < 2 or ok.sum() < 6:
        return None
    m = (tok < NV) & ok[pag]
    H = np.zeros((npag, K))
    np.add.at(H, (pag[m], cls[tok[m]]), 1.0)
    idx = {v: i for i, v in enumerate(valori)}
    L = np.array([idx[e] if e is not None else -1 for e in etich_pagina])
    pagine_ok = np.nonzero(ok)[0]

    def mi_di(lab):
        T = np.zeros((len(valori), K))
        for i in pagine_ok:
            T[lab[i]] += H[i]
        mi, hx, hy = FC.info_mutua_tabella(T)
        return mi, hy
    mi, h = mi_di(L)
    rng = np.random.default_rng(seme)
    rif = []
    for _ in range(PERM):
        L2 = L.copy()
        L2[pagine_ok] = L[pagine_ok][rng.permutation(len(pagine_ok))]
        rif.append(mi_di(L2)[0])
    return dict(MI_norm=float(mi / h) if h > 0 else float('nan'), riferimento=float(np.mean(rif) / h) if h > 0 else float('nan'),
                eccesso=float((mi - np.mean(rif)) / h) if h > 0 else float('nan'), p97_5_eccesso=float((np.percentile(rif, 97.5) - np.mean(rif)) / h) if h > 0 else float('nan'),
                valori=len(valori), pagine=int(ok.sum()))


# ---------------------------------------------------------------- lavori

def arr_pagine(M, pagine, cifre=4):
    return OrderedDict((p, [round(float(x), cifre) for x in M[i]]) for i, p in enumerate(pagine))


def rimescola_seq(tok, linea, rng):
    return FC.rimescola_in_riga(tok, linea, rng)


def lavoro_piega(nome, piega):
    inizio = time.time()
    T = testo(nome)
    pagine = list(T.pagine)
    test = [p for p in pagine if T.piega[p] == piega]
    resto = [p for p in pagine if T.piega[p] != piega]
    random.Random(3964 + 100 * SEME_DIV + piega).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    sA, sV, sT = Seq(T, add), Seq(T, val), Seq(T, test)
    voc, cont = vocabolario(sA)
    NV = len(voc)
    ix = {w: i for i, w in enumerate(voc)}
    tA, tV, tT = sA.ids(ix, NV), sV.ids(ix, NV), sT.ids(ix, NV)
    freq_voc = np.array([cont[w] for w in voc], dtype=float)
    npT = len(test)
    seme_job = G.seme_di('ia10:%s:%d' % (nome, piega))
    rng = np.random.default_rng(seme_job)
    # ---- procedura principale (seme 1)
    ris, K, (a, b) = adatta_e_scegli(tA, sA.linea, tV, sV.linea, NV, 1)
    cls, tr = ris[K]['cls'], ris[K]['tr']
    per_K = OrderedDict()
    for k, v in ris.items():
        P = punteggi(v['tr'], v['cls'], tT, sT.linea, sT.pag, npT, NV)
        per_K[str(k)] = dict(gval=v['gval'], gprova=float(P[:, 0].sum() / max(P[:, 1].sum(), 1)), giri=v['info']['giri'], MI_add=v['info']['MI_addestramento'])
    prova = punteggi(tr, cls, tT, sT.linea, sT.pag, npT, NV)
    rim = np.zeros((npT, 4))
    for _ in range(S_RIM):
        rim += punteggi(tr, cls, FC.rimescola_in_riga(tT, sT.linea, rng), sT.linea, sT.pag, npT, NV)
    rim /= S_RIM
    # ---- famiglie "di sola forma" (stesso K)
    forma = OrderedDict()
    for tipo in ('ultimo', 'primo'):
        cf = classi_forma(voc, freq_voc, K, tipo)
        trf = FC.Transizioni(a, b, cf, K)
        forma[tipo] = arr_pagine(punteggi(trf, cf, tT, sT.linea, sT.pag, npT, NV), test)
    # ---- secondo seme: stabilita' fra semi
    cls2, info2 = FC.adatta_famiglie(a, b, NV, K, 2, giri=GIRI)
    ari_semi = FC.indice_rand_corretto(cls[:NV], cls2[:NV])
    tr2 = FC.Transizioni(a, b, cls2, K)
    prova2 = punteggi(tr2, cls2, tT, sT.linea, sT.pag, npT, NV)
    # ---- modello "senza ordine": stessa procedura (scelta di K compresa, sulla validazione vera) su un addestramento con le parole
    # rimescolate dentro la riga; si valuta sulle STESSE coppie di prova vere. Cattura tutto cio' che le famiglie sanno della
    # composizione della riga (quali parole stanno insieme) ma non dell'ordine.
    nulli = []
    fam_nullo = None
    for r in range(NULL_REP):
        rr = np.random.default_rng(seme_job + 1000 + r)
        tAn = FC.rimescola_in_riga(tA, sA.linea, rr)
        rn, Kn, _ = adatta_e_scegli(tAn, sA.linea, tV, sV.linea, NV, 1)
        Pn = punteggi(rn[Kn]['tr'], rn[Kn]['cls'], tT, sT.linea, sT.pag, npT, NV)
        nulli.append(dict(K=Kn, pagine=arr_pagine(Pn, test), conc=FC.misure_tabella(rn[Kn]['tr'].C)))
        if r == 0:
            fam_nullo = {w: int(rn[Kn]['cls'][i]) for i, w in enumerate(voc)}
    # ---- forma
    forma_an = analisi_forma(voc, cls, K, 3000 + piega, freq_voc)
    # ---- etichette grammaticali (se note), posizione, sezione, lingua
    etich = analisi_etichette(cls, tT, sT.cat, NV, seme_job + 5) if sT.cat is not None else None
    posiz = analisi_posizione(cls, tT, sT.linea, sT.pos, NV, seme_job + 6)
    sez = lang = None
    if T.tipo:
        sez = analisi_etichetta_pagina(cls, tT, sT.pag, npT, [T.tipo[p][0] if T.tipo.get(p) else None for p in test], K, NV, seme_job + 7)
        lang = analisi_etichetta_pagina(cls, tT, sT.pag, npT, [T.tipo[p][1] if T.tipo.get(p) and T.tipo[p][1] in ('A', 'B') else None for p in test], K, NV, seme_job + 8)
    # ---- v21 con il modello delle vere (solo per le pagine vere)
    cross = None
    if nome == 'vere':
        cross = OrderedDict()
        for b_ in LIBRI_V21:
            lib = G.libro(b_)
            pb = [p for p in test if p in lib]
            if len(pb) != len(test):
                raise SystemExit('FERMO: il libro %s non ha tutte le pagine della piega %d' % (b_, piega))
            Tb = FT.Testo(b_, OrderedDict((p, lib[p]) for p in test), tipo=T.tipo, piega=T.piega)
            sB = Seq(Tb, test)
            tB = sB.ids(ix, NV)
            Pb = punteggi(tr, cls, tB, sB.linea, sB.pag, npT, NV)
            rb = np.zeros((npT, 4))
            for _ in range(S_RIM):
                rb += punteggi(tr, cls, FC.rimescola_in_riga(tB, sB.linea, rng), sB.linea, sB.pag, npT, NV)
            cross[b_] = dict(prova=arr_pagine(Pb, test), rim=arr_pagine(rb / S_RIM, test),
                             quota_nuove=float(np.mean(tB == NV)))
    # ---- famiglie delle parole: solo nella cartella protetta
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, 'fam_%s_%d.pkl' % (nome, piega)), 'wb') as f:
        pickle.dump(dict(K=K, seme1={w: int(cls[i]) for i, w in enumerate(voc)}, seme2={w: int(cls2[i]) for i, w in enumerate(voc)}, nullo=fam_nullo), f)
    return OrderedDict(
        job=[nome, piega], tipo='piega', K=K, NV=NV, n_pagine=OrderedDict(add=len(add), val=len(val), test=len(test)),
        copertura_addestramento=float(np.mean(tA < NV)), quota_rare_prova=float(np.mean(tT == NV)), per_K=per_K,
        giri=ris[K]['info']['giri'], MI_addestramento=ris[K]['info']['MI_addestramento'],
        concentrazione=FC.misure_tabella(tr.C), prova=arr_pagine(prova, test), rim=arr_pagine(rim, test),
        prova_seme2=float(prova2[:, 0].sum() / max(prova2[:, 1].sum(), 1)), ari_semi=float(ari_semi),
        forma_sola=forma, nulli=nulli, forma=forma_an, etichette=etich, posizione=posiz, sezione=sez, lingua=lang, cross=cross,
        tempo=round(time.time() - inizio, 1))


def lavoro_finale(nome):
    """Tabella descrittiva: famiglie sulle parole di tutte le pagine (nessuna pagina di prova), K = KF, seme 1."""
    inizio = time.time()
    T = testo(nome)
    pagine = list(T.pagine)
    s = Seq(T, pagine)
    voc, cont = vocabolario(s)
    NV = len(voc)
    ix = {w: i for i, w in enumerate(voc)}
    tok = s.ids(ix, NV)
    p = FC.coppie_di(tok, s.linea)
    a, b = tok[p], tok[p + 1]
    K = KF
    cls, info = FC.adatta_famiglie(a, b, NV, K, 1, giri=GIRI)
    tr = FC.Transizioni(a, b, cls, K)
    freq = np.array([cont[w] for w in voc], dtype=float)
    fam = OrderedDict()
    for f in range(K):
        idx = np.nonzero(cls[:NV] == f)[0]
        ws = [voc[i] for i in idx]
        lun = [len(w) for w in ws]
        ult, pri = Counter(w[-1] for w in ws), Counter(w[0] for w in ws)
        ent = lambda c: float(-sum(v / len(ws) * math.log2(v / len(ws)) for v in c.values())) if ws else float('nan')
        m = (tok < NV) & (cls[np.minimum(tok, NV)] == f)
        fam[str(f)] = OrderedDict(tipi=len(ws), occorrenze=int(freq[idx].sum()), lunghezza_media=float(np.mean(lun)) if lun else float('nan'),
                                  entropia_ultimo_glifo=ent(ult), entropia_primo_glifo=ent(pri),
                                  quota_prima_in_riga=float((s.pos[m] == 0).mean()) if m.any() else float('nan'),
                                  quota_ultima_in_riga=float((s.pos[m] == 2).mean()) if m.any() else float('nan'))
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, 'famiglie_%s.txt' % nome), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# ia10: famiglie di parole di "%s" (K=%d, %d parole, %d pagine). Solo uso locale: non pubblicare.\n' % (nome, K, NV, len(pagine)))
        for fm in range(K):
            idx = sorted(np.nonzero(cls[:NV] == fm)[0], key=lambda i: -freq[i])
            f.write('\n## famiglia %d (%d parole, %d occorrenze)\n' % (fm, len(idx), freq[idx].sum()))
            f.write(' '.join('%s(%d)' % (''.join(voc[i]), freq[i]) for i in idx) + '\n')
    mt = FC.misure_tabella(tr.C)
    return OrderedDict(job=[nome, 'F'], tipo='finale', K=K, NV=NV, giri=info['giri'], famiglie=fam,
                       classe_rara=OrderedDict(occorrenze=int((tok == NV).sum())), conteggi=tr.C.astype(int).tolist(),
                       passaggi=np.round(tr.P, 3).tolist(), concentrazione=mt, tempo=round(time.time() - inizio, 1))


def lavoro(job):
    """Un errore di un lavoro non ferma gli altri: si registra come 'errore' (RIPRENDI=1 lo rifa) e il testo, se incompleto, non entra
    nell'analisi (l'analisi dice quali testi mancano)."""
    nome, piega = job
    inizio = time.time()
    try:
        return lavoro_finale(nome) if piega == 'F' else lavoro_piega(nome, piega)
    except Exception as e:  # noqa: BLE001
        return OrderedDict(job=[nome, piega], tipo='errore', errore='%s: %s' % (type(e).__name__, str(e)[:300]), tempo=round(time.time() - inizio, 1))


def lavori_fit():
    L = []
    for t in testi_attivi():
        L += [(t, f) for f in range(NF)] + [(t, 'F')]
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


def avvia_processo():
    pass


# ---------------------------------------------------------------- analisi

def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def pesi_bootstrap(P):
    rng = np.random.default_rng(100010)
    return np.stack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(BOOT)]).astype(float)


def ic(x):
    return [float(v) for v in np.percentile(x, [2.5, 97.5])]


def media(x):
    x = [v for v in x if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return float(np.mean(x)) if x else None


def mat_pagine(corse_testo, pag, getter):
    """Matrice (pagine, 4) da un campo per pagina di ogni lavoro (getter(r) -> {pagina: [4 numeri]})."""
    ip = {p: i for i, p in enumerate(pag)}
    M = np.zeros((len(pag), 4))
    for r in corse_testo:
        for p, v in getter(r).items():
            M[ip[p]] = v
    return M


def lista_pagine(corse_testo):
    """Pagine in ordine alfabetico e matrici (P, 4) di prova e rim, (P, 4) di forma ultimo/primo."""
    pag = sorted(p for r in corse_testo for p in r['prova'])
    ip = {p: i for i, p in enumerate(pag)}
    def mat(chiave, sotto=None):
        M = np.zeros((len(pag), 4))
        for r in corse_testo:
            d = r[chiave] if sotto is None else r[chiave][sotto]
            for p, v in d.items():
                M[ip[p]] = v
        return M
    return pag, mat


def g_di(M, W=None, col=(0, 1)):
    if W is None:
        return float(M[:, col[0]].sum() / max(M[:, col[1]].sum(), 1e-12))
    return (W @ M[:, col[0]]) / np.maximum(W @ M[:, col[1]], 1e-12)


def riassunto_testo(nome, corse_t, W_cache):
    """Tutte le misure di un testo, dalle 5 pieghe."""
    pieghe = sorted(corse_t, key=lambda r: r['job'][1])
    pag, mat = lista_pagine(pieghe)
    P = len(pag)
    if P not in W_cache:
        W_cache[P] = pesi_bootstrap(P)
    W = W_cache[P]
    X, R = mat('prova'), mat('rim')
    Xk = {t: mat('forma_sola', t) for t in ('ultimo', 'primo')}
    gb = g_di(X, W)
    out = OrderedDict()
    out['pagine'] = P
    out['K_scelti'] = [r['K'] for r in pieghe]
    out['coppie'] = int(X[:, 1].sum())
    out['G'] = OrderedDict(punto=g_di(X), ic=ic(gb))
    out['G_kk'] = OrderedDict(punto=g_di(X, col=(2, 3)), ic=ic(g_di(X, W, col=(2, 3))))
    out['G_rim'] = OrderedDict(punto=g_di(R), ic=ic(g_di(R, W)))
    out['G_forma_ultimo'] = g_di(Xk['ultimo'])
    out['G_forma_primo'] = g_di(Xk['primo'])
    out['G_seme2'] = media([r['prova_seme2'] for r in pieghe])
    out['G_per_piega'] = [g_di(np.array(list(r['prova'].values()))) for r in pieghe]
    out['G_per_K'] = OrderedDict((k, media([r['per_K'][k]['gprova'] for r in pieghe if k in r['per_K']])) for k in pieghe[0]['per_K'])
    out['gval_per_K'] = OrderedDict((k, media([r['per_K'][k]['gval'] for r in pieghe if k in r['per_K']])) for k in pieghe[0]['per_K'])
    # modello senza ordine (media dei rifacimenti, pagina per pagina) e differenza g = G - G_senza_ordine (stesse coppie di prova)
    Nm = np.mean([mat_pagine(pieghe, pag, lambda r, i=i: r['nulli'][i]['pagine']) for i in range(len(pieghe[0]['nulli']))], axis=0)
    out['G_senza_ordine'] = OrderedDict(punto=g_di(Nm), ic=ic(g_di(Nm, W)), K=[[x['K'] for x in r['nulli']] for r in pieghe],
                                        rifacimenti=[g_di(mat_pagine(pieghe, pag, lambda r, i=i: r['nulli'][i]['pagine'])) for i in range(len(pieghe[0]['nulli']))])
    out['g'] = OrderedDict(punto=g_di(X) - g_di(Nm), ic=ic(g_di(X, W) - g_di(Nm, W)))
    out['g_kk'] = OrderedDict(punto=g_di(X, col=(2, 3)) - g_di(Nm, col=(2, 3)), ic=ic(g_di(X, W, col=(2, 3)) - g_di(Nm, W, col=(2, 3))))
    out['D'] = OrderedDict(punto=g_di(X) - g_di(R), ic=ic(g_di(X, W) - g_di(R, W)))
    cm = [r['concentrazione'] for r in pieghe]
    cn = [[x['conc'] for x in r['nulli']] for r in pieghe]
    out['concentrazione'] = OrderedDict((k, media([c[k] for c in cm])) for k in cm[0])
    out['concentrazione_nullo'] = OrderedDict((k, media([x[k] for c in cn for x in c])) for k in cm[0])
    out['ari_semi'] = media([r['ari_semi'] for r in pieghe])
    out['forma'] = OrderedDict((k, media([r['forma'][k] for r in pieghe])) for k in pieghe[0]['forma'])
    out['quota_rare_prova'] = media([r['quota_rare_prova'] for r in pieghe])
    out['copertura_addestramento'] = media([r['copertura_addestramento'] for r in pieghe])
    if pieghe[0]['etichette']:
        out['etichette'] = OrderedDict((k, media([r['etichette'][k] for r in pieghe])) for k in pieghe[0]['etichette'])
    out['posizione'] = OrderedDict((k, media([r['posizione'][k] for r in pieghe])) for k in pieghe[0]['posizione'])
    for chiave in ('sezione', 'lingua'):
        v = [r[chiave] for r in pieghe if r.get(chiave)]
        if v:
            out[chiave] = OrderedDict((k, media([x[k] for x in v])) for k in v[0])
            out[chiave]['pieghe_valide'] = len(v)
    out['_X'], out['_R'], out['_pag'] = X, R, pag
    return out


def ari_fra_pieghe(nome, chiave='seme1'):
    """Indice di Rand corretto fra le famiglie di due pieghe, sulle parole raggruppate in tutte e due (media delle 10 coppie)."""
    fam = []
    for f in range(NF):
        percorso = os.path.join(CACHE, 'fam_%s_%d.pkl' % (nome, f))
        if not os.path.exists(percorso):
            return None
        fam.append(pickle.load(open(percorso, 'rb'))[chiave])
    v, comuni = [], []
    for i in range(NF):
        for j in range(i + 1, NF):
            c = sorted(set(fam[i]) & set(fam[j]), key=lambda w: (len(w), w))
            if len(c) >= 50:
                v.append(FC.indice_rand_corretto([fam[i][w] for w in c], [fam[j][w] for w in c]))
                comuni.append(len(c))
    return OrderedDict(ari=float(np.mean(v)), min=float(min(v)), max=float(max(v)), parole_comuni=float(np.mean(comuni))) if v else None


def ari_fra_testi(n1, n2):
    """Indice di Rand corretto fra le famiglie di due testi nella stessa piega (stesse parole raggruppate in tutti e due)."""
    v = []
    for f in range(NF):
        p1, p2 = (os.path.join(CACHE, 'fam_%s_%d.pkl' % (n, f)) for n in (n1, n2))
        if not (os.path.exists(p1) and os.path.exists(p2)):
            return None
        a, b = pickle.load(open(p1, 'rb'))['seme1'], pickle.load(open(p2, 'rb'))['seme1']
        c = sorted(set(a) & set(b), key=lambda w: (len(w), w))
        if len(c) >= 50:
            v.append(FC.indice_rand_corretto([a[w] for w in c], [b[w] for w in c]))
    return float(np.mean(v)) if v else None


def analisi_cross(corse_vere, W_cache):
    """v21 con il modello delle vere (stesse famiglie e stessa tabella dei passaggi, imparate sulle pagine vere di addestramento).
    Per ogni libro: guadagno G sulle sue pagine di prova, guadagno G_rim sulle stesse pagine con le parole rimescolate dentro la
    riga, e perdita da rimescolamento D = G - G_rim (quanto il modello si affida all'ordine). Lo stesso per le vere. Misura
    principale: rapporto D(v21) / D(vere). D si calcola con lo stesso modello su due versioni delle stesse pagine: non dipende da
    quanto il modello sa della composizione delle righe, perche' il rimescolamento nella riga non la cambia."""
    pieghe = sorted(corse_vere, key=lambda r: r['job'][1])
    pag = sorted(p for r in pieghe for p in r['prova'])
    P = len(pag)
    if P not in W_cache:
        W_cache[P] = pesi_bootstrap(P)
    W = W_cache[P]
    mat = lambda getter: mat_pagine(pieghe, pag, getter)
    Xv, Rv = mat(lambda r: r['prova']), mat(lambda r: r['rim'])
    Dv, Dvb = g_di(Xv) - g_di(Rv), g_di(Xv, W) - g_di(Rv, W)
    libri = OrderedDict()
    for b in LIBRI_V21:
        if not all(r['cross'] and b in r['cross'] for r in pieghe):
            continue
        Xb, Rb = mat(lambda r: r['cross'][b]['prova']), mat(lambda r: r['cross'][b]['rim'])
        libri[b] = OrderedDict(G=g_di(Xb), G_rim=g_di(Rb), D=g_di(Xb) - g_di(Rb), rapporto=(g_di(Xb) - g_di(Rb)) / Dv if Dv else None,
                               quota_rare=media([r['cross'][b]['quota_nuove'] for r in pieghe]), _b=g_di(Xb, W) - g_di(Rb, W))
    out = OrderedDict(G_vere=g_di(Xv), G_vere_ic=ic(g_di(Xv, W)), G_rim_vere=g_di(Rv), D_vere=Dv, D_vere_ic=ic(Dvb),
                      libri=OrderedDict((b, OrderedDict((k, v) for k, v in d.items() if k != '_b')) for b, d in libri.items()))
    if libri:
        Dm = float(np.mean([d['D'] for d in libri.values()]))
        Dmb = np.mean([d['_b'] for d in libri.values()], axis=0)
        r = Dm / Dv if Dv else None
        rb = Dmb / np.where(np.abs(Dvb) > 1e-9, Dvb, np.nan)
        lo, hi = np.nanpercentile(rb, [2.5, 97.5])
        out.update(G_v21=float(np.mean([d['G'] for d in libri.values()])), G_rim_v21=float(np.mean([d['G_rim'] for d in libri.values()])),
                   D_v21=Dm, D_v21_ic=ic(Dmb), differenza=Dv - Dm, differenza_ic=ic(Dvb - Dmb), rapporto=r,
                   rapporto_ic=[float(2 * r - hi), float(2 * r - lo)] if r is not None else None,
                   se_libri=float(np.std([d['D'] for d in libri.values()], ddof=1) / len(libri) ** 0.5) if len(libri) > 1 else 0.0)
    return out


def controlli_e_letture(S, cross, own, stab, finali):
    """S: riassunti per testo. Restituisce (controlli, letture). I controlli che non sono superati rendono "non leggibile" le letture."""
    c = OrderedDict()
    mot = []

    def ok(cond, msg):
        if not cond:
            mot.append(msg)
        return bool(cond)
    ing, lat, sn, sf, sc = (S.get(k) for k in ('inglese', 'latino_ud', 'sint_noforma', 'sint_forma', 'sint_caso'))
    if ing and ing.get('etichette'):
        e = ing['etichette']
        c['positivo_inglese'] = OrderedDict(nmi=e['nmi'], nmi_caso=e['nmi_caso'], margine=e['nmi'] - e['nmi_caso'], g=ing['g']['punto'],
                                            superato=ok(e['nmi'] >= S_NMI and e['nmi'] - e['nmi_caso'] >= S_NMI_MARGINE, 'inglese: le famiglie non corrispondono alle categorie'))
    if lat and lat.get('etichette'):
        e = lat['etichette']
        c['positivo_latino_ud'] = OrderedDict(nmi=e['nmi'], nmi_caso=e['nmi_caso'], margine=e['nmi'] - e['nmi_caso'], g=lat['g']['punto'],
                                              superato=bool(e['nmi'] - e['nmi_caso'] >= S_NMI_LATINO_MARGINE))
    if sn and sn.get('etichette'):
        e = sn['etichette']
        c['positivo_sintetico'] = OrderedDict(nmi=e['nmi'], g=sn['g']['punto'], D=sn['D']['punto'],
                                              superato=ok(e['nmi'] >= S_SINT_NMI and sn['g']['punto'] >= S_SINT_G and sn['D']['punto'] >= S_D_SENS, 'sintetico senza forma: classi vere o ordine non ritrovati'))
    if sc:
        c['negativo_sintetico'] = OrderedDict(g=sc['g']['punto'], g_ic=sc['g']['ic'], D=sc['D']['punto'], D_ic=sc['D']['ic'],
                                              superato=ok(sc['g']['ic'][1] <= S_CASO_G and sc['D']['ic'][1] <= S_CASO_G, 'sintetico senza ordine: g o D sopra il nullo'))
    if sn and sf:
        c['forma_sintetici'] = OrderedDict(F_senza_forma=sn['forma']['F_spiegata'], F_con_forma=sf['forma']['F_spiegata'],
                                           superato=ok(sn['forma']['F_spiegata'] <= S_FORMA_CTRL_BASSO and sf['forma']['F_spiegata'] >= S_FORMA_CTRL_ALTO, 'misura della forma: sintetici non separati'))
    if sn and sc:
        c['stabilita_sintetici'] = OrderedDict(ari_senza_forma=(stab.get('sint_noforma') or {}).get('ari'), ari_senza_ordine=(stab.get('sint_caso') or {}).get('ari'))
        a1, a2 = c['stabilita_sintetici']['ari_senza_forma'], c['stabilita_sintetici']['ari_senza_ordine']
        c['stabilita_sintetici']['superato'] = ok(a1 is not None and a2 is not None and a1 >= S_ARI_SINT_ALTO and a2 <= S_ARI_SINT_BASSO, 'stabilita: sintetici non separati')
    v = S.get('vere')
    c['motivi'] = mot
    c['valido'] = len(mot) == 0
    L = OrderedDict()
    if not v:
        return c, L
    lat_ok = c.get('positivo_latino_ud', {}).get('superato', False)
    # L1: ordine fra le famiglie, oltre la composizione della riga
    lo, hi = v['g']['ic']
    nota = None
    if not c['valido']:
        e = 'non leggibile'
    elif lo >= S_G_SI:
        e = 'si'
    elif hi <= S_G_NO:
        e = 'no' if lat_ok else 'zona grigia'
        if not lat_ok:
            nota = 'un "no" richiede il controllo sul latino (UD) superato'
    else:
        e = 'zona grigia'
    L['L1'] = OrderedDict(esito=e, g=v['g']['punto'], g_ic=v['g']['ic'], G=v['G']['punto'], G_ic=v['G']['ic'], G_senza_ordine=v['G_senza_ordine']['punto'],
                          D=v['D']['punto'], D_ic=v['D']['ic'], K_scelti=v['K_scelti'], nota=nota)
    # L1b: adiacenza -- le coppie vicine si distinguono dalle coppie a caso nella stessa riga? (perdita da rimescolamento D)
    d_lo, d_hi = v['D']['ic']
    e1b = 'non leggibile' if not c['valido'] else 'si' if d_lo >= S_D_SENS else 'no' if d_hi <= S_G_NO else 'zona grigia'
    L['L1b'] = OrderedDict(esito=e1b, D=v['D']['punto'], D_ic=v['D']['ic'])
    # L2: confronto con le lingue (su g)
    rif = OrderedDict((k, S[k]['g']['punto']) for k in ('inglese', 'latino', 'latino_ud') if k in S)
    if rif:
        r_lat = [rif[k] for k in ('latino', 'latino_ud') if k in rif]
        g = v['g']['punto']
        if r_lat and g > max(r_lat):
            e2 = 'si'                      # piu' netto di tutti e due i testi latini
        elif r_lat and g < 0.5 * min(r_lat):
            e2 = 'no'
        else:
            e2 = 'zona grigia'
        L['L2'] = OrderedDict(esito=e2 if c['valido'] else 'non leggibile', g_vere=g, riferimenti=rif,
                              rapporti=OrderedDict((k, g / x if x else None) for k, x in rif.items()))
    # L3: tabella concentrata
    rc, rn = v['concentrazione']['rapporto_celle'], v['concentrazione_nullo']['rapporto_celle']
    cond = rc <= S_RAPP_CELLE_SI and rn - rc >= S_RAPP_CELLE_MARGINE
    e3 = 'non leggibile' if not c['valido'] else 'si' if cond else 'no' if rn - rc < S_RAPP_CELLE_NO else 'zona grigia'
    L['L3'] = OrderedDict(esito=e3, rapporto_celle=rc, rapporto_celle_nullo=rn, MI_norm=v['concentrazione']['MI_norm'], MI_norm_nullo=v['concentrazione_nullo']['MI_norm'],
                          dominante=v['concentrazione']['dominante'], dominante_nullo=v['concentrazione_nullo']['dominante'])
    # L4: forma
    F = v['forma']['F_spiegata']
    e4 = 'non leggibile' if not c['valido'] else 'si' if F >= S_FORMA_SI else 'no' if F <= S_FORMA_NO else 'zona grigia'
    L['L4'] = OrderedDict(esito=e4, F_spiegata=F, F=v['forma']['F'], F_perm=v['forma']['F_perm'], F_pesata=v['forma']['F_pesata'],
                          G=v['G']['punto'], G_forma_ultimo=v['G_forma_ultimo'], G_forma_primo=v['G_forma_primo'])
    # L5: stabilita'
    a = stab.get('vere')
    if a:
        e5 = 'non leggibile' if not c['valido'] else 'si' if a['ari'] >= S_ARI_SI else 'no' if a['ari'] < S_ARI_NO else 'zona grigia'
        L['L5'] = OrderedDict(esito=e5, ari_pieghe=a['ari'], ari_min=a['min'], ari_max=a['max'], ari_semi=v['ari_semi'], ari_nullo=a.get('ari_nullo'))
    # L6: posizione, sezione, lingua
    l6 = OrderedDict()
    for nome_, chiave in (('posizione', 'posizione'), ('sezione', 'sezione'), ('lingua_AB', 'lingua')):
        d = v.get(chiave)
        if d:
            if chiave == 'posizione':
                si = max(S_POS_RIGA, 3 * (d.get('sd_rif') or 0.0))
                no = max(0.5 * S_POS_RIGA, 2 * (d.get('sd_rif') or 0.0))
            else:
                si = max(S_POS_PAG, d.get('p97_5_eccesso') or 0.0)
                no = d.get('p97_5_eccesso') or 0.0
            l6[nome_] = OrderedDict(esito='non leggibile' if not c['valido'] else 'si' if d['eccesso'] >= si else 'no' if d['eccesso'] < no else 'zona grigia',
                                    eccesso=d['eccesso'], MI_norm=d['MI_norm'], riferimento=d['riferimento'], soglia_si=si, soglia_no=no)
    if l6:
        L['L6'] = l6
    # L7: v21 contro vere (valida solo se la lettura L1 e' "si": serve un ordine da copiare)
    l7 = OrderedDict()
    leggibile = c['valido'] and L['L1']['esito'] == 'si'
    leggibile_cross = c['valido'] and L['L1b']['esito'] == 'si'
    if cross and cross.get('rapporto') is not None:
        r = cross['rapporto']
        e = 'non leggibile' if not leggibile_cross else 'si' if r <= S_R_SI else 'no' if r >= S_R_NO else 'zona grigia'
        l7['cross'] = OrderedDict(esito=e, rapporto=r, rapporto_ic=cross['rapporto_ic'], D_vere=cross['D_vere'], D_vere_ic=cross['D_vere_ic'], D_v21=cross['D_v21'],
                                  D_v21_ic=cross['D_v21_ic'], G_vere=cross['G_vere'], G_v21=cross['G_v21'], differenza=cross['differenza'], differenza_ic=cross['differenza_ic'])
    if own and own.get('rapporti'):
        rs = own['rapporti']
        r = float(np.mean(rs))
        e = 'non leggibile' if not leggibile else 'si' if r <= S_R_SI else 'no' if r >= S_R_NO else 'zona grigia'
        l7['own'] = OrderedDict(esito=e, rapporto=r, rapporti_libri=rs, g_v21=own['g_v21'], g_vere=v['g']['punto'], rapporto_celle_v21=own.get('rapporto_celle'),
                                rapporto_celle_vere=v['concentrazione']['rapporto_celle'], ari_pieghe_v21=own.get('ari_pieghe'), ari_con_vere=own.get('ari_con_vere'))
    if l7:
        es = [x['esito'] for x in l7.values() if x['esito'] != 'non leggibile']
        l7['esito'] = 'non leggibile' if not es else 'si' if all(x == 'si' for x in es) else 'no' if all(x == 'no' for x in es) else 'zona grigia'
        L['L7'] = l7
    return c, L


# ---------------------------------------------------------------- scrittura

def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((k, pulisci(v)) for k, v in x.items() if not str(k).startswith('_'))
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, np.ndarray):
        return pulisci(x.tolist())
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def f3(x):
    return '-' if x is None else '%.3f' % x


def f2(x):
    return '-' if x is None else '%.2f' % x


def pc(x):
    return '-' if x is None else '%.1f%%' % (100 * x)


def ii(x):
    return '-' if not x else '%.3f-%.3f' % (x[0], x[1])


NOMI_TESTI = OrderedDict([('vere', 'Voynich (tutto)'), ('vereA', 'Voynich A'), ('vereB', 'Voynich B'), ('ts', 'Timm e Schinner'), ('naibbe', 'Naibbe'),
                          ('latino', 'latino (Plinio)'), ('inglese', 'inglese (Brown)'), ('latino_ud', 'latino (UD PROIEL)'),
                          ('sint_noforma', 'sintetico senza forma'), ('sint_forma', 'sintetico con forma'), ('sint_caso', 'sintetico senza ordine')])


def scrivi(ris, versioni):
    S, ctrl, L = ris['testi'], ris['controlli'], ris['letture']
    parametri = OrderedDict(NF=NF, CHIAVI=CHIAVI, NV=NV_MAX, MIN_CONT=MIN_CONT, KS=KS, K_PARSIMONIA=K_PARSIMONIA, GIRI=GIRI, S_RIM=S_RIM, NULL_REP=NULL_REP,
                            BOOT=BOOT, PERM=PERM, KF=KF, SOLO_CONTROLLI=SOLO_CONTROLLI,
                            soglie=OrderedDict((k, globals()[k]) for k in ('S_G_SI', 'S_G_NO', 'S_NMI', 'S_NMI_MARGINE', 'S_NMI_LATINO_MARGINE', 'S_SINT_NMI', 'S_SINT_G',
                                                                            'S_CASO_G', 'S_FORMA_SI', 'S_FORMA_NO', 'S_FORMA_CTRL_ALTO', 'S_FORMA_CTRL_BASSO',
                                                                            'S_RAPP_CELLE_SI', 'S_RAPP_CELLE_MARGINE', 'S_ARI_SI', 'S_ARI_NO', 'S_ARI_SINT_ALTO',
                                                                            'S_ARI_SINT_BASSO', 'S_POS_RIGA', 'S_POS_PAG', 'S_D_SENS', 'S_RAPP_CELLE_NO', 'C_FORMA', 'S_R_SI', 'S_R_NO')))
    out = OrderedDict(esperimento='ia10', parametri=parametri, versioni=versioni, impronte_libri=ris.get('impronte_libri'), letture=L, controlli=ctrl,
                      testi_mancanti=ris.get('mancanti'), testi=S, stabilita_pieghe=ris['stabilita'], cross_v21=ris.get('cross'), own_v21=ris.get('own'), tabelle_finali=ris['finali'])
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulisci(out), f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    r = ['# ia10 — famiglie di parole', '',
         'Prima riga di lettura (soglie nella preregistrazione `preregistrazioni/ia10.md`). G = bit per coppia di parole vicine nella stessa riga che il modello a famiglie '
         'guadagna sulle pagine di prova rispetto a un modello senza ordine (unigrammi di famiglie). G_c = lo stesso per un modello rifatto su un addestramento con le parole '
         'rimescolate dentro la riga (sa quali famiglie stanno nella stessa riga, non in che ordine). g = G - G_c: l\'ordine, oltre la composizione della riga. '
         'D = G meno G sulle stesse pagine con le parole rimescolate (modello invariato). Intervalli al 95%% col bootstrap sulle pagine. Nessuna parola nei risultati.', '']
    esiti = lambda d: d['esito'].upper() if d else '-'
    v = S.get('vere')
    if v and 'L1' in L:
        l1 = L['L1']
        r.append('**L1, le famiglie si susseguono con ordine (oltre la composizione della riga):** %s. g = %s bit per coppia (%s); G = %s (%s), G_c = %s, D = %s (%s); K scelti %s.%s' % (
            esiti(l1), f3(l1['g']), ii(l1['g_ic']), f3(l1['G']), ii(l1['G_ic']), f3(l1['G_senza_ordine']), f3(l1['D']), ii(l1['D_ic']), l1['K_scelti'], (' ' + l1['nota']) if l1.get('nota') else ''))
    if 'L1b' in L:
        l1b = L['L1b']
        r.append('**L1b, le coppie vicine si distinguono dalle coppie a caso nella stessa riga:** %s. D = %s (%s).' % (esiti(l1b), f3(l1b['D']), ii(l1b['D_ic'])))
    if 'L2' in L:
        l2 = L['L2']
        r.append('**L2, rispetto alle lingue:** %s. g delle vere %s; riferimenti %s.' % (esiti(l2), f3(l2['g_vere']), ', '.join('%s %s' % (NOMI_TESTI[k], f3(x)) for k, x in l2['riferimenti'].items())))
    if 'L3' in L:
        l3 = L['L3']
        r.append('**L3, tabella dei passaggi concentrata:** %s. Celle per mezza probabilita\' rispetto all\'indipendenza: %s (tabella imparata sul testo rimescolato %s); informazione mutua normalizzata %s (rimescolato %s).' % (
            esiti(l3), f3(l3['rapporto_celle']), f3(l3['rapporto_celle_nullo']), f3(l3['MI_norm']), f3(l3['MI_norm_nullo'])))
    if 'L4' in L:
        l4 = L['L4']
        r.append('**L4, la famiglia dipende dalla forma della parola:** %s. Quota spiegata dalla forma %s (famiglie a caso: %s); G con famiglie dal solo ultimo glifo %s, dal solo primo %s (famiglie dai vicini %s).' % (
            esiti(l4), f3(l4['F_spiegata']), f3(l4['F_perm']), f3(l4['G_forma_ultimo']), f3(l4['G_forma_primo']), f3(l4['G'])))
    if 'L5' in L:
        l5 = L['L5']
        r.append('**L5, famiglie stabili:** %s. Indice di Rand corretto fra pieghe %s (%s-%s; famiglie imparate su testo rimescolato %s), fra semi %s.' % (
            esiti(l5), f3(l5['ari_pieghe']), f3(l5['ari_min']), f3(l5['ari_max']), f3(l5.get('ari_nullo')), f3(l5['ari_semi'])))
    if 'L6' in L:
        for k, d in L['L6'].items():
            r.append('**L6, famiglie e %s:** %s. Eccesso di informazione mutua normalizzata %s (soglie: si da %s, no sotto %s).' % (k.replace('_', ' '), d['esito'].upper(), f3(d['eccesso']), f3(d['soglia_si']), f3(d['soglia_no'])))
    if 'L7' in L:
        l7 = L['L7']
        r.append('**L7, v21 contro vere:** %s.' % esiti(l7))
        if 'cross' in l7:
            d = l7['cross']
            r.append('  - modello delle vere applicato al v21: %s; perdita da rimescolamento D: vere %s, v21 %s, rapporto %s (%s).' % (esiti(d), f3(d['D_vere']), f3(d['D_v21']), f2(d['rapporto']), ii(d['rapporto_ic'])))
        if 'own' in l7:
            d = l7['own']
            r.append('  - famiglie imparate dal libro v21: %s; rapporto fra g del libro e g delle vere (media sui libri) %s.' % (esiti(d), f2(d['rapporto'])))
    r += ['', '## Controlli', '']
    if 'positivo_inglese' in ctrl:
        d = ctrl['positivo_inglese']
        r.append('- positivo, inglese (Brown, categorie grammaticali): informazione mutua normalizzata famiglie-categorie %s, a caso %s, margine %s (soglie %.2f e %.2f): %s' % (
            f3(d['nmi']), f3(d['nmi_caso']), f3(d['margine']), S_NMI, S_NMI_MARGINE, 'SUPERATO' if d['superato'] else 'NON superato'))
    if 'positivo_latino_ud' in ctrl:
        d = ctrl['positivo_latino_ud']
        r.append('- positivo, latino (UD Latin-PROIEL, categorie UPOS): %s, a caso %s, margine %s (soglia %.2f; serve a leggere i "no"): %s' % (
            f3(d['nmi']), f3(d['nmi_caso']), f3(d['margine']), S_NMI_LATINO_MARGINE, 'SUPERATO' if d['superato'] else 'NON superato'))
    if 'positivo_sintetico' in ctrl:
        d = ctrl['positivo_sintetico']
        r.append('- positivo, sintetico con grammatica nota e senza forma: classi vere ritrovate (informazione mutua normalizzata %s, soglia %.2f), g %s (soglia %.2f), D %s (soglia %.2f): %s' % (
            f3(d['nmi']), S_SINT_NMI, f3(d['g']), S_SINT_G, f3(d['D']), S_D_SENS, 'SUPERATO' if d['superato'] else 'NON superato'))
    if 'negativo_sintetico' in ctrl:
        d = ctrl['negativo_sintetico']
        r.append('- negativo, sintetico senza ordine: g %s (%s), D %s (%s), limiti alti sotto %.2f: %s' % (f3(d['g']), ii(d['g_ic']), f3(d['D']), ii(d['D_ic']), S_CASO_G, 'SUPERATO' if d['superato'] else 'NON superato'))
    if 'forma_sintetici' in ctrl:
        d = ctrl['forma_sintetici']
        r.append('- forma, sintetici: quota spiegata dalla forma %s senza forma (al massimo %.2f) e %s con forma (almeno %.2f): %s' % (
            f3(d['F_senza_forma']), S_FORMA_CTRL_BASSO, f3(d['F_con_forma']), S_FORMA_CTRL_ALTO, 'SUPERATO' if d['superato'] else 'NON superato'))
    if 'stabilita_sintetici' in ctrl:
        d = ctrl['stabilita_sintetici']
        r.append('- stabilita\', sintetici: indice di Rand corretto fra pieghe %s senza forma (almeno %.2f) e %s senza ordine (al massimo %.2f): %s' % (
            f3(d['ari_senza_forma']), S_ARI_SINT_ALTO, f3(d['ari_senza_ordine']), S_ARI_SINT_BASSO, 'SUPERATO' if d['superato'] else 'NON superato'))
    if ris.get('mancanti'):
        r.append('- testi non completati (errore o lavori mancanti): %s' % ', '.join(ris['mancanti']))
    r.append('- esito dei controlli: %s%s' % ('tutti superati' if ctrl['valido'] else 'NON superati', '' if ctrl['valido'] else ' (%s)' % '; '.join(ctrl['motivi'])))
    r += ['', '## Ordine per testo (bit per coppia di parole vicine, pagine di prova)', '',
          '| testo | pagine | coppie | K scelti | G (IC 95%) | G_c (senza ordine) | g = G - G_c (IC 95%) | D (IC 95%) | G solo coppie raggruppate | G con famiglie dall\'ultimo glifo | dal primo glifo | parole rare in prova |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k in list(NOMI_TESTI) + LIBRI_V21:
        d = S.get(k)
        if not d:
            continue
        r.append('| %s | %d | %d | %s | %s (%s) | %s | %s (%s) | %s (%s) | %s | %s | %s | %s |' % (
            NOMI_TESTI.get(k, k + ' (v21, famiglie proprie)'), d['pagine'], d['coppie'], ','.join(str(x) for x in d['K_scelti']), f3(d['G']['punto']), ii(d['G']['ic']),
            f3(d['G_senza_ordine']['punto']), f3(d['g']['punto']), ii(d['g']['ic']), f3(d['D']['punto']), ii(d['D']['ic']), f3(d['G_kk']['punto']),
            f3(d['G_forma_ultimo']), f3(d['G_forma_primo']), pc(d['quota_rare_prova'])))
    r += ['', '## Guadagno per numero di famiglie (media sulle pieghe: validazione e prova)', '', '| testo | ' + ' | '.join('K=%s val / prova' % k for k in KS) + ' |', '|---|' + '---|' * len(KS)]
    for k in list(NOMI_TESTI) + LIBRI_V21:
        d = S.get(k)
        if d:
            r.append('| %s | %s |' % (NOMI_TESTI.get(k, k), ' | '.join('%s / %s' % (f3(d['gval_per_K'].get(str(K))), f3(d['G_per_K'].get(str(K)))) for K in KS)))
    r += ['', '## Tabella dei passaggi: concentrazione (media sulle pieghe; fra parentesi il testo rimescolato dentro la riga, stessa procedura)', '',
          '| testo | informazione mutua normalizzata | entropia condizionata (bit) | celle per mezza probabilita\' / indipendenza | passaggio dominante oltre l\'indipendenza |', '|---|---|---|---|---|']
    for k in list(NOMI_TESTI) + LIBRI_V21:
        d = S.get(k)
        if d:
            a, b = d['concentrazione'], d['concentrazione_nullo']
            r.append('| %s | %s (%s) | %s (%s) | %s (%s) | %s (%s) |' % (NOMI_TESTI.get(k, k), f3(a['MI_norm']), f3(b['MI_norm']), f3(a['H_cond']), f3(b['H_cond']), f3(a['rapporto_celle']), f3(b['rapporto_celle']), f3(a['dominante']), f3(b['dominante'])))
    r += ['', '## Forma, stabilita\', categorie (media sulle pieghe)', '', '| testo | quota spiegata dalla forma | (con famiglie a caso) | stabilita\' fra semi | fra pieghe | informazione mutua con le categorie | a caso | purezza |', '|---|---|---|---|---|---|---|---|']
    for k in list(NOMI_TESTI) + LIBRI_V21:
        d = S.get(k)
        if d:
            e = d.get('etichette') or {}
            st = ris['stabilita'].get(k)
            r.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (NOMI_TESTI.get(k, k), f3(d['forma']['F_spiegata']), f3(d['forma']['F_perm']), f3(d['ari_semi']), f3(st['ari']) if st else '-',
                                                                  f3(e.get('nmi')), f3(e.get('nmi_caso')), f2(e.get('purezza'))))
    r += ['', '## Posizione nella riga, sezione, lingua A/B (eccesso di informazione mutua normalizzata sul riferimento a caso; media sulle pieghe)', '', '| testo | posizione nella riga | sezione | lingua A/B |', '|---|---|---|---|']
    for k in list(NOMI_TESTI):
        d = S.get(k)
        if d:
            r.append('| %s | %s | %s | %s |' % (NOMI_TESTI[k], f3(d['posizione']['eccesso']), f3(d['sezione']['eccesso']) if d.get('sezione') else '-', f3(d['lingua']['eccesso']) if d.get('lingua') else '-'))
    cr = ris.get('cross')
    if cr and cr.get('libri'):
        r += ['', '## v21 con il modello delle vere (stesse pagine, stesse famiglie, stessa tabella dei passaggi)', '',
              'Vere: G %s (%s), G sulle stesse pagine rimescolate %s, D %s (%s). Media dei libri: G %s, rimescolato %s, D %s (%s); differenza di D (vere meno v21) %s (%s); '
              'rapporto D(v21)/D(vere) %s (%s); errore standard fra i libri %s.' % (
                  f3(cr['G_vere']), ii(cr['G_vere_ic']), f3(cr['G_rim_vere']), f3(cr['D_vere']), ii(cr['D_vere_ic']), f3(cr.get('G_v21')), f3(cr.get('G_rim_v21')), f3(cr.get('D_v21')),
                  ii(cr.get('D_v21_ic')), f3(cr.get('differenza')), ii(cr.get('differenza_ic')), f2(cr.get('rapporto')), ii(cr.get('rapporto_ic')), f3(cr.get('se_libri'))),
              '', '| libro | G | G rimescolato | D | D(libro)/D(vere) | parole rare |', '|---|---|---|---|---|---|']
        for b_, d in cr['libri'].items():
            r.append('| %s | %s | %s | %s | %s | %s |' % (b_, f3(d['G']), f3(d['G_rim']), f3(d['D']), f2(d['rapporto']), pc(d['quota_rare'])))
    ow = ris.get('own')
    if ow:
        r += ['', '## v21 con famiglie imparate dal libro', '', 'Rapporto fra g del libro e g delle vere, per libro: %s. Celle per mezza probabilita\' (media sui libri) %s contro %s delle vere. '
              'Indice di Rand corretto fra le famiglie del libro e quelle delle vere nella stessa piega: %s; fra pieghe dello stesso libro: %s.' % (
                  ', '.join('%s %s' % (b_, f2(x)) for b_, x in zip(LIBRI_V21, ow['rapporti'])), f3(ow.get('rapporto_celle')), f3(S['vere']['concentrazione']['rapporto_celle']),
                  f3(ow.get('ari_con_vere')), f3(ow.get('ari_pieghe')))]
    fin = ris['finali']
    r += ['', '## Tabelle di famiglie e passaggi (descrittive, famiglie imparate su tutte le pagine, K = %d; la classe %d e\' "parola rara")' % (KF, KF), '',
          'Le famiglie sono numerate a caso e non si possono confrontare fra testi. Riga = famiglia di partenza, colonna = famiglia della parola dopo (stessa riga); probabilita\' del passaggio. '
          'L\'elenco delle parole di ogni famiglia sta in `dati/cache/ia10/uscite/famiglie_<testo>.txt` (solo uso locale).']
    for k in ('vere', 'vereA', 'vereB', 'inglese', 'latino_ud', 'sint_noforma', 'a13'):
        d = fin.get(k)
        if not d:
            continue
        r += ['', '### %s' % NOMI_TESTI.get(k, k + ' (v21, un libro)'), '',
              '| famiglia | tipi | occorrenze | lunghezza media | prima in riga | ultima in riga | ' + ' | '.join('->%d' % j for j in range(d['K'] + 1)) + ' |', '|---|---|---|---|---|---|' + '---|' * (d['K'] + 1)]
        for i in range(d['K']):
            f = d['famiglie'][str(i)]
            r.append('| %d | %d | %d | %s | %s | %s | %s |' % (i, f['tipi'], f['occorrenze'], f2(f['lunghezza_media']), pc(f['quota_prima_in_riga']), pc(f['quota_ultima_in_riga']), ' | '.join('%.2f' % x for x in d['passaggi'][i])))
        r.append('| rara | | %d | | | | %s |' % (d['classe_rara']['occorrenze'], ' | '.join('%.2f' % x for x in d['passaggi'][d['K']])))
        r.append('')
        r.append('Informazione mutua normalizzata della tabella %s; celle per mezza probabilita\' rispetto all\'indipendenza %s.' % (f3(d['concentrazione']['MI_norm']), f3(d['concentrazione']['rapporto_celle'])))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def impronte(nomi):
    out = OrderedDict()
    for n in nomi:
        p = G.percorso_libro(n)
        out[n] = '%08x' % (zlib.crc32(open(p, 'rb').read()) & 0xffffffff) if os.path.exists(p) else None
    return out


def esegui_analisi(corse, versioni):
    per = defaultdict(list)
    finali = OrderedDict()
    for r in corse:
        if r.get('tipo') == 'errore':
            continue
        nome, piega = r['job']
        if piega == 'F':
            finali[nome] = r
        else:
            per[nome].append(r)
    W_cache = {}
    S = OrderedDict()
    stab = OrderedDict()
    for nome in testi_attivi():
        if len(per.get(nome, [])) == NF:
            S[nome] = riassunto_testo(nome, per[nome], W_cache)
            stab[nome] = ari_fra_pieghe(nome)
            sn = ari_fra_pieghe(nome, 'nullo')
            if stab[nome] is not None and sn is not None:
                stab[nome]['ari_nullo'] = sn['ari']
    cross = analisi_cross(per['vere'], W_cache) if len(per.get('vere', [])) == NF else None
    own = None
    libri = [b for b in LIBRI_V21 if b in S]
    if 'vere' in S and libri:
        gv = S['vere']['g']['punto']
        own = OrderedDict(rapporti=[S[b]['g']['punto'] / gv if gv else None for b in libri], g_v21=float(np.mean([S[b]['g']['punto'] for b in libri])),
                          rapporto_celle=float(np.mean([S[b]['concentrazione']['rapporto_celle'] for b in libri])),
                          ari_pieghe=media([stab[b]['ari'] for b in libri if stab.get(b)]),
                          ari_con_vere=media([ari_fra_testi('vere', b) for b in libri]))
        own['rapporti'] = [x for x in own['rapporti'] if x is not None]
    ctrl, L = controlli_e_letture(S, cross, own, stab, finali)
    mancanti = [n for n in testi_attivi() if n not in S]
    ris = dict(mancanti=mancanti, testi=S, stabilita=stab, controlli=ctrl, letture=L, cross=cross, own=own, finali=finali, impronte_libri=impronte(LIBRI_V21))
    return scrivi(ris, versioni), ris


def prepara_libri():
    """I libri a13-a22 devono esistere (li ha fatti ia01). Con SOLO_CONTROLLI si fanno quelli di prova (catene di Markov)."""
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI_V21 if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01: eseguire prima ia01)' % (', '.join(mancano), G.LIBRI))


def main():
    import numpy
    import scipy
    import sklearn
    versioni = dict(python=sys.version.split()[0], numpy=numpy.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'fit,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d; testi %s; K %s; pieghe %d' % (len(c['ids']), testi_attivi(), KS, NF), flush=True)
    prepara_libri()
    percorso = os.path.join(USCITA, 'ia10_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    elif 'fit' in fasi:
        open(percorso, 'w').close()
    if 'fit' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        da_fare = [j for j in lavori_fit() if json.dumps(list(j)) not in fatte]
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(lavori_fit()) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 10))
        with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                corse.append(r)
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s)%s' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo'], (' ERRORE ' + r['errore']) if r.get('tipo') == 'errore' else ''), flush=True)
    elif os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    if 'fit' in fasi:
        corse = [x for x in corse if x.get('tipo') != 'errore']
    if 'analisi' in fasi:
        righe, ris = esegui_analisi(corse, versioni)
        print('\n'.join(righe[:24]), flush=True)


if __name__ == '__main__':
    main()
