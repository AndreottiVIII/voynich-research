# -*- coding: utf-8 -*-
"""Esperimento IA15 (ia15): da dove viene l'"eco" della pagina. Argomento (come in una lingua: una pagina che parla di una cosa
ripete le sue parole) o tecnica di scrittura (copiare e ritoccare parole scritte poco prima)?

Segue ia09 (preregistrazioni/ia09.md, risultati/ia09_dove_sta_sintassi.md): nel Voynich la parola si prevede piu' dall'eco della pagina
(parole uguali o a una modifica da parole gia' scritte sulla pagina) che dalla parola prima; un quarto dell'eco e' locale, il resto "tema".
Qui si smonta l'eco con cinque domande. Preregistrazione: preregistrazioni/ia15.md.

Che cosa fa il codice (in parole semplici)
- Per ogni testo (Voynich, libri v21, Timm e Schinner, tre lingue, controlli sintetici "solo argomento" e "sola copia", rimescolati) e
  per ogni parola di ogni pagina, si contano le parole gia' scritte (le righe sopra e le parole prima nella stessa riga) che sono uguali o a
  una modifica di distanza, divise per distanza in righe, per paragrafo (stesso o diverso), per posto della modifica (inizio, fine,
  dentro la parola). La stessa conta si fa su una pagina di riferimento (stessa sezione, e un'altra sezione) con la stessa geometria di
  righe: la differenza e' l'"eco" (eccesso di parole simili per ogni parola fonte), tolta la ripetizione generica.
- Misure: (a) dentro lo stesso paragrafo contro fra paragrafi, a parita' di distanza, con il controllo dei confini spostati; (b) per
  sezione e per tipo di pagina; (c) varianti contro uguali per distanza; (d) dove cadono le modifiche; (e) pagine vicine contro lontane.
- Nessuna rete neurale: solo conte. Tutti i controlli sono scritti nella preregistrazione prima di eseguire sul Voynich.

Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia15_da_dove_eco.json e .md e, una riga per testo,
risultati/ia15_corse.jsonl (solo numeri per pagina; con RIPRENDI=1 i testi fatti non si rifanno).

Variabili (oltre a quelle di ia01 e ia09: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, RIGHE_PAGINA_EN, CHIAVI, USCITA, LIBRI, BOOT,
GENERATORI, RIM_TESTO, FILTRO, RIPRENDI, PROCESSI, FASI): FASI (conteggi, analisi; predefinito tutte e due), e le NUOVE di ia15:
NRIF (pagine di riferimento per ogni pagina e tipo, 2), SPOSTAMENTI (confini di paragrafo spostati, 200), LIVELLI_ARG e LIVELLI_TEC
(forza dei generatori, es. "F=0.5,M=0.2,D=0.08"), SCALA_COPIA (media della distanza di copia, in parole, 10; ia09), MIN_PAGINE_GRUPPO (5).
"""
import json, math, os, random, sys, time, zlib
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import ia09_dove_sta_sintassi as I9  # noqa: E402
import sintassi_testi as TT  # noqa: E402
import sintassi_modelli as SM  # noqa: E402
import eco_modelli as EM  # noqa: E402
import eco_testi as ET  # noqa: E402

NOME = 'ia15_da_dove_eco'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NRIF = int(os.environ.get('NRIF', 2))
SPOSTAMENTI = int(os.environ.get('SPOSTAMENTI', 200))
GENERATORI = I9.GENERATORI
RIM_TESTO = I9.RIM_TESTO
SCALA_COPIA = float(os.environ.get('SCALA_COPIA', 10))
MIN_PAGINE_GRUPPO = int(os.environ.get('MIN_PAGINE_GRUPPO', 5))
MIN_ETEROG = 10                              # pagine minime di un gruppo per il confronto fra gruppi
LIBRI_V21 = I9.LIBRI_V21


def livelli(nome, default):
    d = dict(x.split('=') for x in default.split(','))
    for x in os.environ.get(nome, '').split(','):
        if '=' in x:
            k, v = x.split('=')
            d[k] = v
    return {k: float(v) for k, v in d.items()}


LAMBDA_ARG = livelli('LIVELLI_ARG', 'F=0.35,M=0.20,D=0.10')     # quota di parole pescate dal tema (argomento puro)
P_TEC = livelli('LIVELLI_TEC', 'F=0.15,M=0.06,D=0.02')          # probabilita' di copiare una parola vicina (sola copia)
seme_di = G.seme_di


# ---------------------------------------------------------------- i testi

_T = OrderedDict()


def nomi_testi():
    """Tutti i testi. 'X~t' = X con tutte le parole mescolate fra le pagine; 'X~p' = con le parole mescolate dentro ogni pagina.
    arg* = solo argomento (argP: un tema per pagina; argR: per paragrafo; argS: un tema che scorre fra righe e pagine);
    tec* = sola copia (tecM/tecF/tecD: forza; tecP: copia solo dal paragrafo in corso; tecCoda/tecTesta: la modifica tocca sempre
    l'ultimo / il primo glifo)."""
    G_ = GENERATORI
    base = ['vere'] + LIBRI_V21 + ([] if SOLO_CONTROLLI else ['ts1', 'ts2'])
    rif = ([] if SOLO_CONTROLLI else ['latino']) + ['inglese', 'italiano']
    arg = (['argP%d' % i for i in range(1, G_ + 1)] + ['argPF1', 'argPD1'] + ['argR%d' % i for i in range(1, G_ + 1)] + ['argRF1'] +
           ['argS1', 'argSF1'])
    tec = ['tecM%d' % i for i in range(1, G_ + 1)] + ['tecF1', 'tecD1', 'tecP1', 'tecPF1', 'tecCoda1', 'tecTesta1']
    nomi = base + rif + ['latGeom', 'ingGeom'] + arg + tec
    rim_t = (['vere~t%d' % i for i in range(1, RIM_TESTO + 1)] +
             [x + '~t' for x in [LIBRI_V21[0]] + ([] if SOLO_CONTROLLI else ['ts1']) + ['argP1', 'tecM1'] + rif])
    rim_p = [x + '~p' for x in ['vere', LIBRI_V21[0]] + ([] if SOLO_CONTROLLI else ['ts1']) + ['argP1', 'tecF1'] + rif]
    return nomi + rim_t + rim_p


def costruisci(nome):
    """Il testo `nome`: dict(pagine, fold, tipo). Uguale in ogni processo (semi fissi)."""
    if nome in _T:
        return _T[nome]
    if '~' in nome:
        base, modo = nome.split('~')
        T = costruisci(base)
        f = TT.rimescola_testo if modo.startswith('t') else TT.rimescola_pagina
        t = dict(pagine=f(T['pagine'], seme_di('ia15:rim:' + nome)), fold=T['fold'], tipo=T['tipo'])
    elif nome in ('latGeom', 'ingGeom'):
        base = I9.costruisci('vere')
        chiave = TT.CHIAVE_LATINO if nome == 'latGeom' else TT.CHIAVE_INGLESE
        t = dict(pagine=ET.testo_in_disposizione(chiave, base['pagine']), fold=base['fold'], tipo=base['tipo'])
    elif nome.startswith('arg') or nome.startswith('tec'):
        base = I9.costruisci('vere')
        Cb = SM.Corpus(base['pagine'])
        Cb.prepara()
        seme = seme_di('ia15:gen:' + nome)
        if nome.startswith('arg'):
            unita = dict(P='pagina', R='paragrafo', S='scorre')[nome[3]]
            liv = dict(P='M', R='M', S='M')[nome[3]]
            if len(nome) > 4 and nome[4] in 'FD':
                liv = nome[4]
            meta = ET.meta_di(list(Cb.pag), prova=SOLO_CONTROLLI)
            ordine = sorted(Cb.pag, key=lambda p: meta[p]['ord'])
            pagine = EM.genera_argomento(Cb, seme, LAMBDA_ARG[liv], unita, ordine)
        else:
            modo, solo_par, liv = 'misto', False, 'M'
            if nome.startswith('tecCoda'):
                modo = 'fine'
            elif nome.startswith('tecTesta'):
                modo = 'inizio'
            elif nome[3] == 'P':
                solo_par = True
                liv = nome[4] if nome[4] in 'FD' else 'M'
            elif nome[3] in 'FD':
                liv = nome[3]
            pagine = EM.genera_copia_eco(Cb, seme, P_TEC[liv], SCALA_COPIA, modo, solo_par)
        t = dict(pagine=pagine, fold=base['fold'], tipo=base['tipo'])
    else:
        t = I9.costruisci(nome)
    if len(_T) > 4:
        _T.clear()
    _T[nome] = t
    return t


# ---------------------------------------------------------------- lavoro di un testo

def lavoro(nome):
    inizio = time.time()
    T = costruisci(nome)
    nomi = sorted(T['pagine'])
    C = SM.Corpus(T['pagine'])
    C.prepara()
    A = EM.grafo_vicini(C)
    sez_prova = {p: T['tipo'][p][0] for p in nomi} if (SOLO_CONTROLLI and T.get('tipo') and all(p in T['tipo'] for p in nomi)) else None
    meta = ET.meta_di(nomi, sezioni_prova=sez_prova, prova=SOLO_CONTROLLI)
    nrighe = {p: len(C.pag[p].lstart) - 1 for p in nomi}
    rs, ra = EM.scegli_riferimenti(nomi, meta, nrighe, seme_di('ia15:rif'), NRIF)
    pagine, nulli = OrderedDict(), {}
    for p in nomi:
        st, nl = EM.stat_pagina(C, A, C.pag[p], [C.pag[q] for q in rs[p]], [C.pag[q] for q in ra[p]])
        m = meta[p]
        st['meta'] = [m['sez'], m['lingua'], m['mano'], m['tipo'], m['ord'], None if m['area'] is None else round(m['area'], 4)]
        pagine[p] = st
        nulli[p] = nl
    # confini di paragrafo spostati: Q per ogni spostamento
    qnull = []
    multi = [p for p in nomi if pagine[p]['npar'] >= 2]
    reali = {p: np.array(pagine[p]['E']['real']) for p in nomi}
    refs = {p: np.array(pagine[p]['E']['sez']) for p in nomi}
    for s in range(SPOSTAMENTI):
        rnd = random.Random(seme_di('ia15:sp:%d' % s))
        Er = np.zeros((len(nomi), 2, 2, EM.NB, 2))
        for i, p in enumerate(nomi):
            if p in multi:
                pid = nulli[p]['pid']
                nuovo, prima = EM.paragrafi_spostati(pid, rnd)
                r = EM.somme_E_con_paragrafi(nulli[p], nuovo, prima)
                Er[i, 0], Er[i, 1] = r['real'], r['sez']
            else:
                Er[i, 0], Er[i, 1] = reali[p], refs[p]
        qnull.append(q_par(Er, np.ones((1, len(nomi))))['Q'][0])
    K = ET.relazioni(meta, nomi)
    rel = EM.relazioni_pagine(C, A, nomi, K)
    for p in nomi:
        pagine[p]['rel'] = rel[p]
    info = OrderedDict(npagine=len(nomi), nparole=int(sum(pagine[p]['nparole'] for p in nomi)), npar_multi=len(multi),
                       tipi=int(C.nt), qnull=[None if not np.isfinite(x) else round(float(x), 4) for x in qnull])
    return dict(job=['C', nome], info=info, stat=pagine, tempo=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- l'eco per paragrafo (formula condivisa)

def q_par(Earr, W, d=2):
    """Earr (P, 2 fonti [real, sez], 2 [dentro, fra], NB, 2 [n, simile]). Confronto, a parita' di distanza, fra l'eco da righe dello stesso
    paragrafo ('dentro') e da righe di un paragrafo precedente della stessa pagina ('fra'), nella banda d (2 = D2, due-tre righe sopra;
    3 = D4). Per ogni pagina che ha fonti in tutti e quattro i modi (dentro e fra, vera e riferimento): tasso dentro e fra, vero meno
    riferimento; poi media delle pagine con PESI COMUNI a dentro e fra (il minimo fra le fonti dentro e le fonti fra della pagina): senza
    pesi comuni le pagine con paragrafi lunghi (le piu' ripetitive) pesano di piu' dentro che fra e Q esce meta' anche in un testo con le
    parole mescolate dentro la pagina. W: un ricampionamento per riga (o una riga di uno). Q = eco fra / eco dentro: 1 = il confine non
    cambia l'eco, 0 = fra paragrafi non c'e' eco."""
    n = Earr[:, :, :, d, 0]
    h = Earr[:, :, :, d, 1]
    ok = (n > 0).all(axis=(1, 2))
    om = np.minimum(n[:, 0, 0], n[:, 0, 1]) * ok
    r = np.where(n > 0, h / np.where(n > 0, n, 1.0), 0.0)
    Wo = W * om[None, :]
    den = Wo.sum(1)
    with np.errstate(divide='ignore', invalid='ignore'):
        ew = (Wo @ (r[:, 0, 0] - r[:, 1, 0])) / den
        eb = (Wo @ (r[:, 0, 1] - r[:, 1, 1])) / den
        Q = np.where(ew > 0, eb / np.where(ew > 0, ew, 1.0), np.nan)
    return {'Q': Q, 'e_dentro': ew, 'e_fra': eb, 'pagine': int(ok.sum()), 'fonti_fra': float((n[:, 0, 1] * ok).sum())}


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def lavori(fasi):
    L = [('C', n) for n in nomi_testi()] if 'conteggi' in fasi else []
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


def esegui_lavoro(job):
    return lavoro(job[1])


# ---------------------------------------------------------------- analisi: i numeri di un testo

V = I9.V
pesi_bootstrap = I9.pesi_bootstrap
stima = I9.stima
FONTI3 = ('real', 'sez', 'altro')
QI = dict(simile=[1, 2, 3, 4], x=[1], v=[2, 3, 4], vI=[2], vF=[3], vM=[4])      # colonne di QUANT (0 e' n)
VIC, LON = [0, 1, 2], [3, 4]           # bande vicine (stessa riga, 1 riga sopra, 2-3 righe sopra) e lontane (4-7, 8 o piu')


class Dati:
    """I numeri per pagina di un testo (lavoro 'C')."""

    def __init__(self, r):
        self.nome = r['job'][1]
        st = r['stat']
        self.pag = sorted(st)
        self.info = r['info']
        self.A = np.array([[st[p]['A'][f] for f in FONTI3] for p in self.pag], dtype=float)           # (P, 3, NB, 5)
        self.A4 = np.array([[st[p]['A4'][f] for f in FONTI3[:2]] for p in self.pag], dtype=float)     # (P, 2, NB, 5)
        self.E = np.array([[st[p]['E'][f] for f in FONTI3[:2]] for p in self.pag], dtype=float)       # (P, 2, 2, NB, 2)
        self.rel = np.array([st[p]['rel'] for p in self.pag], dtype=float)                           # (P, 6, 3)
        self.meta = [st[p]['meta'] for p in self.pag]
        self.npar = np.array([st[p]['npar'] for p in self.pag])
        self.nparole = np.array([st[p]['nparole'] for p in self.pag])
        self.nrighe = np.array([st[p]['nrighe'] for p in self.pag])

    def campo(self, k):
        i = dict(sez=0, lingua=1, mano=2, tipo=3, ord=4, area=5)[k]
        return np.array([m[i] for m in self.meta])


def tasso(arr, f, bande, q, W, sel=None):
    """Parole fonte simili (uguali / a una modifica / per posto) per parola fonte, nelle bande date, come rapporto di somme."""
    n = arr[:, f][:, bande][:, :, 0].sum(1)
    h = arr[:, f][:, bande][:, :, QI[q]].sum((1, 2))
    return stima(h, n, W, sel)


def eco(d, q, bande, rif='sez', gruppo='A', W=None, sel=None):
    """Eco = tasso reale meno tasso sul riferimento (eccesso di parole simili per parola fonte). gruppo 'A' = tutte le parole;
    'A4' = solo parole alla riga 4 o piu' (stesso gruppo di parole per bande vicine e lontane; solo rif 'sez')."""
    arr = d.A if gruppo == 'A' else d.A4
    fr = FONTI3.index(rif)
    return tasso(arr, 0, bande, q, W, sel) - tasso(arr, fr, bande, q, W, sel)


def quota(a, b):
    """a / (a + b), con a e b dei V."""
    return a.dividi(a + b)


def eco_comune(arr, W, sel=None):
    """Eco vicina (bande D0-D2) ed eco lontana (D4-D8), e H = lontana / vicina, con PESI COMUNI per pagina: per ogni pagina il tasso di parole
    simili (vero meno riferimento) nelle bande vicine e nelle lontane, poi la media delle pagine con peso uguale per le due (il minimo fra le
    fonti vicine e le fonti lontane della pagina). Senza pesi comuni le pagine lunghe, che hanno piu' fonti lontane e sono le piu' ripetitive,
    pesano di piu' nell'eco lontana e H esce sbagliato (nelle pagine con le parole mescolate non e' 1). `arr` = (P, 2 [vero, riferimento], NB, 5)."""
    if sel is not None:
        arr, W = arr[sel], W[:, sel]
    n_v, n_l = arr[:, :, VIC, 0].sum(2), arr[:, :, LON, 0].sum(2)
    h_v, h_l = arr[:, :, VIC][..., 1:5].sum((2, 3)), arr[:, :, LON][..., 1:5].sum((2, 3))
    ok = (n_v > 0).all(1) & (n_l > 0).all(1)
    om = np.minimum(n_v[:, 0], n_l[:, 0]) * ok
    rv = np.where(n_v > 0, h_v / np.where(n_v > 0, n_v, 1.0), 0.0)
    rl = np.where(n_l > 0, h_l / np.where(n_l > 0, n_l, 1.0), 0.0)
    ev, el = rv[:, 0] - rv[:, 1], rl[:, 0] - rl[:, 1]

    def media(W_):
        Wo = W_ * om[None, :]
        den = Wo.sum(1)
        with np.errstate(divide='ignore', invalid='ignore'):
            return (Wo @ ev) / den, (Wo @ el) / den
    p, b = media(np.ones((1, arr.shape[0]))), media(W)
    e_vic, e_lon = V(p[0][0], b[0]), V(p[1][0], b[1])
    return e_vic, e_lon, e_lon.dividi(e_vic)


def misure(d, W, sel=None):
    """Le misure di un testo (tutti V), per il riferimento di sezione ('sez', principale) e di un'altra sezione ('altro')."""
    r = OrderedDict()
    for rif in ('sez', 'altro'):
        x = OrderedDict()
        x['E_bande'] = [eco(d, 'simile', [b], rif, 'A', W, sel) for b in range(EM.NB)]
        x['Ex_bande'] = [eco(d, 'x', [b], rif, 'A', W, sel) for b in range(EM.NB)]
        x['Ev_bande'] = [eco(d, 'v', [b], rif, 'A', W, sel) for b in range(EM.NB)]
        x['E_tutto'] = eco(d, 'simile', list(range(EM.NB)), rif, 'A', W, sel)
        x['E_vic_tutti'] = eco(d, 'simile', VIC, rif, 'A', W, sel)
        x['E_lon_tutti'] = eco(d, 'simile', LON, rif, 'A', W, sel)
        r[rif] = x
    x = r['sez']
    # parole alla riga 4 o piu': stesse parole per vicino e lontano
    x['E_vic'] = eco(d, 'simile', VIC, 'sez', 'A4', W, sel)
    x['E_lon'] = eco(d, 'simile', LON, 'sez', 'A4', W, sel)
    x['E_vic_c'], x['E_lon_c'], x['H'] = eco_comune(d.A4, W, sel)
    # varianti contro uguali per gruppo di distanza (parole alla riga 4 o piu', per averle tutte e due)
    for nome, bb in (('vic', VIC), ('lon', LON)):
        ex = eco(d, 'x', bb, 'sez', 'A4', W, sel)
        ev = eco(d, 'v', bb, 'sez', 'A4', W, sel)
        x['Ex_' + nome], x['Ev_' + nome] = ex, ev
        x['QV_' + nome] = quota(ev, ex)
        cl = [eco(d, 'v' + c, bb, 'sez', 'A4', W, sel) for c in 'IFM']
        tot = cl[0] + cl[1] + cl[2]
        x['dir_' + nome] = OrderedDict((c, y.dividi(tot)) for c, y in zip('IFM', cl))
        ref = [tasso(d.A4, 1, bb, 'v' + c, W, sel) for c in 'IFM']
        rtot = ref[0] + ref[1] + ref[2]
        x['dir_caso_' + nome] = OrderedDict((c, y.dividi(rtot)) for c, y in zip('IFM', ref))
    # paragrafo
    E = d.E if sel is None else d.E[sel]
    Wq = W if sel is None else W[:, sel]
    uno = np.ones((1, E.shape[0]))
    for nome, dd in (('', 2), ('4', 3)):
        qb, qp = q_par(E, Wq, dd), q_par(E, uno, dd)
        x['Q' + nome] = V(qp['Q'][0], qb['Q'])
        x['e_dentro' + nome] = V(qp['e_dentro'][0], qb['e_dentro'])
        x['e_fra' + nome] = V(qp['e_fra'][0], qb['e_fra'])
        x['pagine_Q' + nome] = qp['pagine']
        x['fonti_fra' + nome] = qp['fonti_fra']
    return r


def relazioni_pagine(d, W, sel=None):
    """(e) Tasso medio di parole simili fra pagine intere, per classe di relazione, in rapporto alla classe 'stessa sezione, quaderno
    diverso, stessa mano' (classe 4). Restituisce, per ogni classe 0-3 e 5, il rapporto (V) e, per 0-3, anche il rapporto delle sole parole
    uguali e delle sole varianti."""
    base = {}
    out = OrderedDict()
    cols = dict(simile=[1, 2], x=[1], v=[2])
    for q, cs in cols.items():
        def media(k):
            return stima(d.rel[:, k][:, cs].sum(1), d.rel[:, k, 0], W, sel)
        b = media(4)
        out[q] = OrderedDict((ET.CLASSI_REL[k], media(k).dividi(b)) for k in (0, 1, 2, 3, 5))
        out[q]['gradiente'] = media(2).dividi(media(3))
        out[q]['base_tasso'] = b
        out[q]['coppie'] = OrderedDict((ET.CLASSI_REL[k], int(d.rel[:, k, 0].sum() if sel is None else d.rel[sel][:, k, 0].sum())) for k in range(6))
    return out




# ---------------------------------------------------------------- soglie delle letture (fissate nella preregistrazione, prima di eseguire sul Voynich)

SOGLIA_ECO = 0.001            # eco vicina minima (eccesso di parole simili per parola fonte, bande 0-3 righe) perche' l'eco sia "misurabile"
H_RIPIDO, H_RIPIDO_IC = 0.25, 0.45     # profilo ripido: H <= 0,25 e limite alto < 0,45
H_PIATTO, H_PIATTO_IC = 0.80, 0.60     # profilo piatto: H >= 0,80 e limite basso > 0,60
QV_ALTE, QV_ALTE_IC = 0.45, 0.30       # varianti alte: quota >= 0,45 e limite basso > 0,30
QV_BASSE, QV_BASSE_IC = 0.25, 0.40     # varianti basse: quota <= 0,25 e limite alto < 0,40
Q_CONTA, Q_CONTA_IC = 0.60, 0.85       # il paragrafo conta: Q <= 0,60, limite alto < 0,85 e sotto il 2,5% dei confini spostati
Q_NON, Q_NON_IC = 0.80, 0.50           # il paragrafo non conta: Q >= 0,80 e limite basso > 0,50
Q_PAGINE_MIN = 20                      # pagine con fonti dentro e fra nella banda D2, minimo per leggere Q
REL_SI, REL_SI_IC = 1.15, 1.05         # pagine vicine: rapporto >= 1,15 e limite basso > 1,05
REL_NO, REL_NO_IC = 1.05, 1.10         # no: rapporto <= 1,05 e limite alto < 1,10
GRAD_SI = 1.05                         # gradiente (consecutive / stesso quaderno): >= 1,05 e limite basso > 1,0, altrimenti "solo a livello di quaderno"
DIR_QUOTA, DIR_ECCESSO = 0.50, 0.15    # le modifiche cadono in X: quota >= 0,50, e >= quota del caso + 0,15 (limite basso sopra il caso + 0,05)


def _ic(v):
    return v.ic()


def lettura_eco(x):
    v = x['E_vic']
    return 'misurabile' if (v.p >= SOGLIA_ECO and _ic(v)[0] > 0) else 'debole'


def lettura_profilo(x):
    """H = eco lontana (4 o piu' righe) / eco vicina (0-3 righe), sulle stesse parole."""
    if lettura_eco(x) != 'misurabile':
        return 'non leggibile'
    h = x['H']
    lo, hi = _ic(h)
    if h.p <= H_RIPIDO and hi < H_RIPIDO_IC:
        return 'ripido'
    if h.p >= H_PIATTO and lo > H_PIATTO_IC:
        return 'piatto'
    return 'intermedio'


def lettura_varianti(x):
    """Quota delle varianti (a una modifica) sull'eco vicina: varianti / (varianti + uguali), come eccessi sul riferimento."""
    if lettura_eco(x) != 'misurabile':
        return 'non leggibile'
    q = x['QV_vic']
    lo, hi = _ic(q)
    if q.p >= QV_ALTE and lo > QV_ALTE_IC:
        return 'alte'
    if q.p <= QV_BASSE and hi < QV_BASSE_IC:
        return 'basse'
    return 'medie'


def lettura_paragrafo(x, qnull):
    """Il confine fra paragrafi cambia l'eco, a parita' di distanza? Q = eco fra paragrafi / eco dentro il paragrafo, a 2-3 righe di distanza."""
    if lettura_eco(x) != 'misurabile':
        return 'non leggibile'
    q = x['Q']
    if not np.isfinite(q.p) or x['pagine_Q'] < Q_PAGINE_MIN:
        return 'non leggibile'
    lo, hi = _ic(q)
    nul = [z for z in qnull if z is not None and np.isfinite(z)]
    sotto = bool(nul) and q.p < np.percentile(nul, 2.5)
    if q.p <= Q_CONTA and hi < Q_CONTA_IC and sotto:
        return 'conta'
    if q.p >= Q_NON and lo > Q_NON_IC:
        return 'non conta'
    return 'zona grigia'


def lettura_direzione(x):
    """Dove cadono le modifiche delle varianti vicine (inizio, fine, dentro la parola)? Solo se le varianti vicine sono in eccesso."""
    ev = x['Ev_vic']
    if not (ev.p > 0 and _ic(ev)[0] > 0):
        return 'non leggibile (varianti in eccesso non misurabili)'
    nomi = dict(I='inizio', F='fine', M='dentro la parola')
    for c in 'IFM':
        s, caso = x['dir_vic'][c], x['dir_caso_vic'][c]
        if s.p >= DIR_QUOTA and s.p >= caso.p + DIR_ECCESSO and _ic(s)[0] > caso.p + 0.05:
            return nomi[c]
    return 'nessun posto prevale'


def lettura_pagine(rel):
    """Le pagine vicine (consecutive) si assomigliano piu' delle lontane della stessa sezione e mano?"""
    r = rel['simile']['consecutive']
    lo, hi = _ic(r)
    if not np.isfinite(r.p):
        return 'non leggibile'
    if r.p >= REL_SI and lo > REL_SI_IC:
        g = rel['simile']['gradiente']
        return 'si' if (g.p >= GRAD_SI and _ic(g)[0] > 1.0) else 'solo a livello di quaderno'
    if r.p <= REL_NO and hi < REL_NO_IC:
        return 'no'
    return 'zona grigia'


def sintesi(profilo, varianti, paragrafo, pagine):
    """La regola finale, scritta prima: a quale dei due modelli puri somiglia l'eco. In ordine:
    1. se profilo o varianti non sono leggibili: "non leggibile";
    2. il paragrafo conta (l'eco si ferma al confine): con varianti alte e profilo ripido "tecnica che riparte a ogni paragrafo", con
       varianti alte e profilo non ripido "mista", altrimenti "argomento di paragrafo" (il profilo ripido e' spiegato dal paragrafo);
    3. profilo ripido e varianti alte (la copia-e-ritocco vive vicino e cambia le parole): "tecnica";
    4. varianti non alte, profilo non ripido: "argomento di pagina" se il profilo e' piatto e le pagine vicine non si assomigliano di piu';
       "argomento che scorre" se il profilo e' intermedio o le pagine vicine si assomigliano;
    5. segni dei due lati (ripido o varianti alte da una parte; piatto, intermedio o pagine vicine "si" dall'altra): "mista";
    6. altrimenti "zona grigia"."""
    if 'non leggibile' in (profilo, varianti):
        return 'non leggibile'
    if paragrafo == 'conta':
        if varianti == 'alte':
            return 'tecnica che riparte a ogni paragrafo' if profilo == 'ripido' else 'mista'
        return 'argomento di paragrafo'
    if profilo == 'ripido' and varianti == 'alte':
        return 'tecnica'
    if varianti != 'alte' and profilo != 'ripido':
        if profilo == 'piatto' and pagine != 'si':
            return 'argomento di pagina'
        return 'argomento che scorre'
    lato_tecnica = profilo == 'ripido' or varianti == 'alte'
    lato_argomento = profilo in ('piatto', 'intermedio') or pagine == 'si'
    if lato_tecnica and lato_argomento:
        return 'mista'
    return 'zona grigia'


# ---------------------------------------------------------------- l'analisi di tutti i testi

def tutte_le_letture(nome, m, rel, qnull):
    """Le letture di un testo dalle sue misure (m = misure(...), rel = relazioni_pagine(...))."""
    x = m['sez']
    pr, va, pa, pg = lettura_profilo(x), lettura_varianti(x), lettura_paragrafo(x, qnull), lettura_pagine(rel)
    return OrderedDict(eco=lettura_eco(x), profilo=pr, varianti=va, paragrafo=pa, direzione=lettura_direzione(x), pagine_vicine=pg,
                       sintesi=sintesi(pr, va, pa, pg))


def voce(m, rel, info, d):
    """Il dizionario di risultati di un testo."""
    x = m['sez']
    v = OrderedDict()
    v['pagine'] = len(d.pag)
    v['parole'] = info['nparole']
    v['pagine_con_2_paragrafi'] = info['npar_multi']
    for rif in ('sez', 'altro'):
        y = m[rif]
        v['eco_' + rif] = OrderedDict(tutto=y['E_tutto'], bande=OrderedDict(zip(EM.NOMI_BANDA, y['E_bande'])),
                                      uguali=OrderedDict(zip(EM.NOMI_BANDA, y['Ex_bande'])), varianti=OrderedDict(zip(EM.NOMI_BANDA, y['Ev_bande'])),
                                      vicine_tutte=y['E_vic_tutti'], lontane_tutte=y['E_lon_tutti'])
    v['E_vic'], v['E_lon'], v['E_vic_c'], v['E_lon_c'], v['H'] = x['E_vic'], x['E_lon'], x['E_vic_c'], x['E_lon_c'], x['H']
    v['Ex_vic'], v['Ev_vic'], v['QV_vic'] = x['Ex_vic'], x['Ev_vic'], x['QV_vic']
    v['Ex_lon'], v['Ev_lon'], v['QV_lon'] = x['Ex_lon'], x['Ev_lon'], x['QV_lon']
    v['direzione_vic'] = OrderedDict((c, x['dir_vic'][c]) for c in 'IFM')
    v['direzione_lon'] = OrderedDict((c, x['dir_lon'][c]) for c in 'IFM')
    v['direzione_caso_vic'] = OrderedDict((c, x['dir_caso_vic'][c]) for c in 'IFM')
    v['Q'], v['Q4'] = x['Q'], x['Q4']
    v['Q_nullo'] = info['qnull']
    v['e_dentro'] = OrderedDict(D2=x['e_dentro'], D4=x['e_dentro4'])
    v['e_fra'] = OrderedDict(D2=x['e_fra'], D4=x['e_fra4'])
    v['pagine_Q'] = OrderedDict(D2=x['pagine_Q'], D4=x['pagine_Q4'])
    v['fonti_fra'] = OrderedDict(D2=x['fonti_fra'], D4=x['fonti_fra4'])
    v['pagine_vicine'] = OrderedDict((q, OrderedDict((k, y) for k, y in z.items())) for q, z in rel.items())
    return v


def gruppi(d, W, campo, minimo):
    """(b) Eco vicina, lontana e profilo per gruppo di pagine (sezione, tipo di pagina, lingua A/B), solo gruppi con almeno `minimo` pagine."""
    out = OrderedDict()
    vals = d.campo(campo)
    for g in sorted(set(vals), key=str):
        sel = np.array([x == g for x in vals])
        n = int(sel.sum())
        if n < minimo:
            out[str(g)] = OrderedDict(pagine=n, nota='troppo poche pagine per la misura')
            continue
        m = misure(d, W, sel)['sez']
        out[str(g)] = OrderedDict(pagine=n, parole=int(d.nparole[sel].sum()), E_vic=m['E_vic_c'], E_lon=m['E_lon_c'], H=m['H'], QV_vic=m['QV_vic'],
                                  Q=m['Q'], profilo=lettura_profilo(m), varianti=lettura_varianti(m))
    return out


def per_area(d, W, minimo):
    """(b) Nell'erbario: pagine con il disegno piu' grande contro piu' piccolo (terzili dell'area del disegno, e190)."""
    ok = np.array([m[3] == 'H erbario' and m[5] is not None for m in d.meta])
    if ok.sum() < 3 * minimo:
        return OrderedDict(nota='dati dell\'area del disegno assenti o pochi')
    aree = np.array([m[5] if m[5] is not None else np.nan for m in d.meta])
    t1, t2 = np.nanpercentile(aree[ok], [100 / 3, 200 / 3])
    out = OrderedDict(terzili=[float(t1), float(t2)])
    for nome, sel in (('disegno piccolo', ok & (aree <= t1)), ('disegno medio', ok & (aree > t1) & (aree <= t2)), ('disegno grande', ok & (aree > t2))):
        m = misure(d, W, sel)['sez']
        out[nome] = OrderedDict(pagine=int(sel.sum()), E_vic=m['E_vic_c'], E_lon=m['E_lon_c'], H=m['H'], QV_vic=m['QV_vic'])
    return out


def eterogeneita(g, minimo):
    """Rapporto fra il massimo e il minimo dell'eco vicina fra i gruppi con abbastanza pagine, e se gli intervalli si separano."""
    ok = [(k, v) for k, v in g.items() if 'E_vic' in v and v['pagine'] >= minimo and v['E_vic'].p > 0]
    if len(ok) < 2:
        return OrderedDict(esito='non leggibile (meno di due gruppi)')
    ok.sort(key=lambda kv: kv[1]['E_vic'].p)
    lo, hi = ok[0], ok[-1]
    rapp = hi[1]['E_vic'].p / lo[1]['E_vic'].p
    sep = _ic(hi[1]['E_vic'])[0] > _ic(lo[1]['E_vic'])[1]
    return OrderedDict(gruppo_minimo=lo[0], gruppo_massimo=hi[0], rapporto=float(rapp), intervalli_separati=bool(sep),
                       esito='varia' if (rapp >= 1.5 and sep) else 'uniforme' if (rapp < 1.25 or not sep) else 'zona grigia')


def ponte_ia09(D):
    """Ponte descrittivo con ia09: la "copia netta" in bit per parola (modelli di ia09, un solo addestramento su tutte le pagine) divisa per
    sezione e per tipo di pagina, dai numeri per pagina di `risultati/ia09_corse.jsonl` (se c'e' e se le pagine sono le stesse)."""
    percorso = os.path.join(USCITA, 'ia09_corse.jsonl')
    if 'vere' not in D or not os.path.exists(percorso):
        return OrderedDict(nota='ia09_corse.jsonl non disponibile')
    r9 = None
    for riga in open(percorso, encoding='utf-8'):
        if riga.startswith('{"job": ["C", "vere"]'):
            r9 = json.loads(riga)
            break
    if r9 is None:
        return OrderedDict(nota='il lavoro "vere" di ia09 non c\'e\'')
    d9 = I9.Dati(r9)
    d = D['vere']
    if d9.pag != d.pag:
        return OrderedDict(nota='le pagine di ia09 non sono le stesse di ia15')
    W = pesi_bootstrap(len(d.pag))
    out = OrderedDict()
    for campo, chiave in (('sez', 'sezione'), ('tipo', 'tipo_di_pagina')):
        vals = d.campo(campo)
        g = OrderedDict()
        for v in sorted(set(vals), key=str):
            sel = np.array([x == v for x in vals])
            if sel.sum() < MIN_PAGINE_GRUPPO:
                continue
            mis = I9.misure(d9, W, sel=sel)['w']
            g[str(v)] = OrderedDict(pagine=int(sel.sum()), copia_netta_bit=mis['netto'], guadagno_g=mis['G']['g'], rho=mis['rho'])
        out[chiave] = g
    out['tutte'] = OrderedDict(copia_netta_bit=I9.misure(d9, W)['w']['netto'])
    return out


def sotto_dati(d, pag):
    """Lo stesso testo ristretto alle pagine `pag` (stesso ordine)."""
    ix = [d.pag.index(p) for p in pag]
    o = Dati.__new__(Dati)
    o.nome, o.info, o.pag = d.nome, d.info, list(pag)
    for k in ('A', 'A4', 'E', 'rel', 'npar', 'nparole', 'nrighe'):
        setattr(o, k, getattr(d, k)[ix])
    o.meta = [d.meta[i] for i in ix]
    return o


MISURE_V21 = ['E_vic_c', 'E_lon_c', 'H', 'QV_vic', 'Q']


def v21_contro_vere(D, W_cache):
    """v21 (media dei libri) meno vere sulle pagine che hanno tutte, per le misure principali: differenza con intervallo e rapporto."""
    libri = [b for b in LIBRI_V21 if b in D]
    if 'vere' not in D or not libri:
        return None
    pag = D['vere'].pag
    for b in libri:
        pag = [p for p in pag if p in D[b].pag]
    W = pesi_bootstrap(len(pag))
    dv = sotto_dati(D['vere'], pag)
    mv = misure(dv, W)['sez']
    ms = [misure(sotto_dati(D[b], pag), W)['sez'] for b in libri]
    out = OrderedDict(_pagine=len(pag))
    for k in MISURE_V21:
        m21 = V.media([x[k] for x in ms])
        diff = m21 - mv[k]
        out[k] = OrderedDict(vere=mv[k], v21=m21, differenza=diff, rapporto=(m21.p / mv[k].p if abs(mv[k].p) > 1e-9 else None))
    return out


N_ARG = ['argP%d' % i for i in range(1, GENERATORI + 1)] + ['argPF1']
N_TEC = ['tecM%d' % i for i in range(1, GENERATORI + 1)] + ['tecF1']
N_ARGR = ['argR%d' % i for i in range(1, GENERATORI + 1)] + ['argRF1']
# (nome del controllo, testi, che cosa deve venire, condizione su una lettura)
CONTROLLI = [
    ('negativo_rimescolato_fra_pagine', ['vere~t%d' % i for i in range(1, RIM_TESTO + 1)] + ['tecM1~t', 'argP1~t'],
     'eco debole (nessuna ripetizione sopra il caso)', lambda l: l['eco'] == 'debole'),
    ('negativo_parole_mescolate_nella_pagina', ['vere~p', 'tecF1~p', 'argP1~p'],
     'profilo piatto e il paragrafo non conta (l\'eco di pagina resta, perde la distanza)', lambda l: l['profilo'] == 'piatto' and l['paragrafo'] != 'conta'),
    ('positivo_tecnica', N_TEC, 'profilo ripido, varianti alte, il paragrafo non conta, sintesi "tecnica"',
     lambda l: l['profilo'] == 'ripido' and l['varianti'] == 'alte' and l['paragrafo'] != 'conta' and l['sintesi'] == 'tecnica'),
    ('positivo_argomento_pagina', N_ARG, 'profilo piatto, varianti basse, il paragrafo non conta, sintesi "argomento di pagina"',
     lambda l: l['profilo'] == 'piatto' and l['varianti'] == 'basse' and l['paragrafo'] != 'conta' and l['sintesi'] == 'argomento di pagina'),
    ('positivo_argomento_paragrafo', N_ARGR, 'il paragrafo conta, sintesi "argomento di paragrafo"',
     lambda l: l['paragrafo'] == 'conta' and l['sintesi'] == 'argomento di paragrafo'),
    ('positivo_tecnica_che_riparte', ['tecPF1'], 'il paragrafo conta, sintesi "tecnica che riparte a ogni paragrafo"',
     lambda l: l['paragrafo'] == 'conta' and l['sintesi'] == 'tecnica che riparte a ogni paragrafo'),
    ('positivo_argomento_che_scorre', ['argSF1'], 'pagine vicine "si", sintesi "argomento che scorre"',
     lambda l: l['pagine_vicine'] == 'si' and l['sintesi'] == 'argomento che scorre'),
    ('negativo_pagine_vicine', ['argP%d' % i for i in range(1, GENERATORI + 1)] + ['tecM%d' % i for i in range(1, GENERATORI + 1)],
     'pagine vicine non "si" (nessun falso "si": il tema e la copia di questi generatori sono indipendenti da una pagina alla successiva)',
     lambda l: l['pagine_vicine'] != 'si'),
    ('positivo_direzione_fine', ['tecCoda1'], 'direzione "fine"', lambda l: l['direzione'] == 'fine'),
    ('positivo_direzione_inizio', ['tecTesta1'], 'direzione "inizio"', lambda l: l['direzione'] == 'inizio'),
    ('negativo_direzione', ['tecM1'], 'direzione "dentro la parola" (le modifiche cadono a caso nella parola: dentro e\' la maggioranza)',
     lambda l: l['direzione'] == 'dentro la parola'),
]


def esegui_controlli(L, MIS):
    """I controlli preregistrati. L = letture di ogni testo, MIS = misure. Vedi la tabella dei controlli nella preregistrazione."""
    c = OrderedDict()

    def ha(n):
        return n in L
    for nome, testi, a_parole, cond in CONTROLLI:
        t = [n for n in testi if ha(n)]
        c[nome] = OrderedDict(testi=t, condizione=a_parole, esiti=OrderedDict((n, L[n]) for n in t), superato=bool(t and all(cond(L[n]) for n in t)))
    neg = c['negativo_rimescolato_fra_pagine']['superato']
    neg_p = c['negativo_parole_mescolate_nella_pagina']['superato']
    tec, arg = c['positivo_tecnica']['superato'], c['positivo_argomento_pagina']['superato']
    c['valida_profilo'] = bool(neg and neg_p and tec and arg)
    c['valida_varianti'] = bool(neg and tec and arg)
    c['valida_paragrafo'] = bool(neg and neg_p and tec and arg and c['positivo_argomento_paragrafo']['superato'] and c['positivo_tecnica_che_riparte']['superato'])
    c['valida_pagine'] = bool(neg and c['positivo_argomento_che_scorre']['superato'] and c['negativo_pagine_vicine']['superato'])
    c['valida_direzione'] = bool(neg and c['positivo_direzione_fine']['superato'] and c['positivo_direzione_inizio']['superato'] and c['negativo_direzione']['superato'])
    c['valida_sintesi'] = bool(c['valida_profilo'] and c['valida_varianti'] and c['valida_paragrafo'] and c['valida_pagine'])
    c['sensibilita_limite'] = OrderedDict((n, OrderedDict((k, L[n][k]) for k in ('eco', 'profilo', 'varianti', 'sintesi'))) for n in ('tecD1', 'argPD1') if ha(n))
    return c


def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((k, pulisci(v)) for k, v in x.items() if not str(k).startswith('_'))
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, V):
        return pulisci(x.d())
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def analisi(corse, versioni):
    D = OrderedDict((r['job'][1], Dati(r)) for r in corse)
    if not D:
        raise SystemExit('FERMO: nessun lavoro da analizzare')
    MIS, REL, T, L = {}, {}, OrderedDict(), OrderedDict()
    for nome, d in D.items():
        W = pesi_bootstrap(len(d.pag))
        MIS[nome] = misure(d, W)
        REL[nome] = relazioni_pagine(d, W)
        T[nome] = voce(MIS[nome], REL[nome], d.info, d)
        L[nome] = tutte_le_letture(nome, MIS[nome], REL[nome], d.info['qnull'])
    ctrl = esegui_controlli(L, MIS)
    ok = dict(profilo=ctrl['valida_profilo'], varianti=ctrl['valida_varianti'], paragrafo=ctrl['valida_paragrafo'], pagine_vicine=ctrl['valida_pagine'],
              direzione=ctrl['valida_direzione'], sintesi=ctrl['valida_sintesi'])
    NL = 'non leggibile (un controllo non e\' superato)'
    letture = OrderedDict()
    for nome, l in L.items():
        if '~' in nome:
            continue
        letture[nome] = OrderedDict((k, (l[k] if (k == 'eco' or ok.get(k, True)) else NL)) for k in l)
        if not ok['sintesi']:
            letture[nome]['sintesi'] = NL
    out = OrderedDict(esperimento='ia15', versioni=versioni, parametri=OrderedDict(
        NRIF=NRIF, SPOSTAMENTI=SPOSTAMENTI, SEMI_RIF=seme_di('ia15:rif'), GENERATORI=GENERATORI, RIM_TESTO=RIM_TESTO, SCALA_COPIA=SCALA_COPIA,
        LAMBDA_ARG=LAMBDA_ARG, P_TEC=P_TEC, MIN_PAGINE_GRUPPO=MIN_PAGINE_GRUPPO, SOLO_CONTROLLI=SOLO_CONTROLLI, BOOT=I9.BOOT,
        soglie=OrderedDict(SOGLIA_ECO=SOGLIA_ECO, H_RIPIDO=H_RIPIDO, H_RIPIDO_IC=H_RIPIDO_IC, H_PIATTO=H_PIATTO, H_PIATTO_IC=H_PIATTO_IC,
                           QV_ALTE=QV_ALTE, QV_ALTE_IC=QV_ALTE_IC, QV_BASSE=QV_BASSE, QV_BASSE_IC=QV_BASSE_IC, Q_CONTA=Q_CONTA, Q_CONTA_IC=Q_CONTA_IC,
                           Q_NON=Q_NON, Q_NON_IC=Q_NON_IC, REL_SI=REL_SI, REL_SI_IC=REL_SI_IC, REL_NO=REL_NO, REL_NO_IC=REL_NO_IC, GRAD_SI=GRAD_SI,
                           DIR_QUOTA=DIR_QUOTA, DIR_ECCESSO=DIR_ECCESSO)),
        controlli=ctrl, letture=letture, testi=T)
    if 'vere' in D:
        d, W = D['vere'], pesi_bootstrap(len(D['vere'].pag))
        out['vere_per_gruppo'] = OrderedDict(sezione=gruppi(d, W, 'sez', MIN_PAGINE_GRUPPO),
                                             tipo_di_pagina=gruppi(d, W, 'tipo', MIN_PAGINE_GRUPPO), lingua=gruppi(d, W, 'lingua', MIN_PAGINE_GRUPPO),
                                             mano=gruppi(d, W, 'mano', MIN_PAGINE_GRUPPO), area_disegno_erbario=per_area(d, W, MIN_PAGINE_GRUPPO))
        out['vere_per_gruppo']['eterogeneita_sezione'] = eterogeneita(out['vere_per_gruppo']['sezione'], MIN_ETEROG)
        out['vere_per_gruppo']['eterogeneita_tipo'] = eterogeneita(out['vere_per_gruppo']['tipo_di_pagina'], MIN_ETEROG)
        for campo, chiave, grp in (('sez', 'controlli_per_sezione', 'eterogeneita_sezione'), ('tipo', 'controlli_per_tipo', 'eterogeneita_tipo')):
            for nome in D:
                if (nome[:3] in ('arg', 'tec') and '~' not in nome and nome.endswith('1') and len(nome) <= 6) or nome in ('latGeom', 'ingGeom'):
                    dd, WW = D[nome], pesi_bootstrap(len(D[nome].pag))
                    out.setdefault(chiave, OrderedDict())[nome] = eterogeneita(gruppi(dd, WW, campo, MIN_PAGINE_GRUPPO), MIN_ETEROG)
            rif = [x['rapporto'] for n, x in out.get(chiave, {}).items() if 'rapporto' in x and L[n]['eco'] == 'misurabile']
            e = out['vere_per_gruppo'][grp]
            if 'rapporto' in e and rif:
                e['rapporto_massimo_dei_riferimenti'] = float(max(rif))
                e['esito_relativo'] = 'piu che i riferimenti' if (e['esito'] == 'varia' and e['rapporto'] >= 1.5 * max(rif)) else 'come i riferimenti'
    out['v21_contro_vere'] = v21_contro_vere(D, None)
    out['ponte_ia09'] = ponte_ia09(D)
    pulito = pulisci(out)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulito, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    righe = scrivi_md(pulito)
    print('\n'.join(righe[:40]), flush=True)
    return pulito


def f3(x, n=3):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%+.*f' % (n, x)


def f2(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%.2f' % x


def vv(d, n=3):
    """Un numero con intervallo, in una cella."""
    if d is None:
        return '-'
    return '%s (%s; %s)' % (f3(d['punto'], n), f3(d['ic'][0], n), f3(d['ic'][1], n))


def scrivi_md(out):
    T, L, c = out['testi'], out['letture'], out['controlli']
    r = ['# ia15 — da dove viene l\'eco della pagina', '',
         'Soglie nella preregistrazione `preregistrazioni/ia15.md`. "Eco" = eccesso di parole uguali o a una modifica da parole gia\' scritte (stessa riga '
         'prima, righe sopra), per parola fonte, rispetto a una pagina di riferimento della stessa sezione con la stessa geometria di righe. Intervalli al 95% '
         'col bootstrap sulle pagine. Nessuna parola nei risultati.', '', '## Letture', '']
    for n, x in L.items():
        r.append('- %s: eco %s; profilo **%s**; varianti **%s**; paragrafo **%s**; modifiche **%s**; pagine vicine **%s**; sintesi **%s**' % (
            n, x['eco'], x['profilo'], x['varianti'], x['paragrafo'], x['direzione'], x['pagine_vicine'], x['sintesi']))
    r += ['', '## Controlli', '']
    for k, v in c.items():
        if isinstance(v, dict) and 'superato' in v:
            r.append('- %s: %s (%s); testi %s' % (k, 'SUPERATO' if v['superato'] else 'NON SUPERATO', v['condizione'], ', '.join(v['testi'])))
        elif isinstance(v, bool):
            r.append('- %s: %s' % (k, v))
        else:
            r.append('- %s: %s' % (k, json.dumps(v, ensure_ascii=False)))
    chiave = [n for n in T if '~' not in n]
    r += ['', '## Eco per testo (eccesso di parole simili per parola fonte)', '',
          '| testo | pagine | eco tutta (rif. sezione) | eco tutta (rif. altra sezione) | eco vicina 0-3 righe (pesi comuni) | eco lontana 4+ (pesi comuni) | H = lontana / vicina | quota varianti vicina | quota varianti lontana |',
          '|---|---|---|---|---|---|---|---|---|']
    for n in T:
        x = T[n]
        r.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (
            n, x['pagine'], vv(x['eco_sez']['tutto'], 4), vv(x['eco_altro']['tutto'], 4), vv(x['E_vic_c'], 4), vv(x['E_lon_c'], 4), vv(x['H'], 2),
            vv(x['QV_vic'], 2), vv(x['QV_lon'], 2)))
    r += ['', '## Eco per banda di distanza (rif. sezione): tutti i simili / uguali / varianti', '',
          '| testo | ' + ' | '.join(EM.NOMI_BANDA) + ' |', '|---' * (EM.NB + 1) + '|']
    for n in T:
        x = T[n]['eco_sez']
        r.append('| %s | %s |' % (n, ' | '.join('%s / %s / %s' % (f3(x['bande'][b]['punto'], 4), f3(x['uguali'][b]['punto'], 4), f3(x['varianti'][b]['punto'], 4)) for b in EM.NOMI_BANDA)))
    r += ['', 'Bande: D0 stessa riga (parole prima), D1 una riga sopra, D2 due-tre righe sopra, D4 quattro-sette, D8 otto o piu\'.', '',
          '## Il paragrafo: eco dentro e fra paragrafi a 2-3 righe di distanza (senza le prime righe dei paragrafi; pagine con pesi comuni)', '',
          '| testo | Q a 2-3 righe (D2) = eco fra / eco dentro | confini spostati: 2,5% - 97,5% | eco dentro D2 | eco fra D2 | pagine usate | Q a 4-7 righe (D4) | pagine D4 | paragrafo |',
          '|---|---|---|---|---|---|---|---|---|']
    for n in T:
        x = T[n]
        nul = [z for z in x['Q_nullo'] if z is not None]
        lim = '%s - %s' % (f2(float(np.percentile(nul, 2.5))), f2(float(np.percentile(nul, 97.5)))) if nul else '-'
        r.append('| %s | %s | %s | %s | %s | %d | %s | %d | %s |' % (
            n, vv(x['Q'], 2), lim, vv(x['e_dentro']['D2'], 4), vv(x['e_fra']['D2'], 4), x['pagine_Q']['D2'], vv(x['Q4'], 2), x['pagine_Q']['D4'],
            (L.get(n) or {}).get('paragrafo', '')))
    r += ['', '## Dove cadono le modifiche delle varianti vicine (quota dell\'eccesso di varianti: inizio / fine / dentro; fra parentesi la quota nel riferimento)', '',
          '| testo | inizio | fine | dentro la parola | lettura |', '|---|---|---|---|---|']
    for n in T:
        x = T[n]
        r.append('| %s | %s | %s | %s | %s |' % (n, *[('%s (%s)' % (f2(x['direzione_vic'][k]['punto']), f2(x['direzione_caso_vic'][k]['punto']))) for k in 'IFM'],
                                                 (L.get(n) or {}).get('direzione', '')))
    r += ['', '## Pagine vicine contro lontane (tasso di parole simili fra pagine intere, in rapporto alla stessa sezione, quaderno diverso, stessa mano)', '',
          '| testo | stesso foglio | stesso bifoglio | consecutive | stesso quaderno | altra sezione | gradiente (consecutive / quaderno) | coppie foglio / bifoglio / consecutive | solo uguali, consecutive | solo varianti, consecutive |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for n in T:
        p = T[n]['pagine_vicine']
        s = p['simile']
        r.append('| %s | %s | %s | %s | %s | %s | %s | %d / %d / %d | %s | %s |' % (
            n, *[vv(s[k], 2) for k in ('foglio', 'bifoglio', 'consecutive', 'quaderno', 'altra_sezione', 'gradiente')], s['coppie']['foglio'], s['coppie']['bifoglio'],
            s['coppie']['consecutive'], vv(p['x']['consecutive'], 2), vv(p['v']['consecutive'], 2)))
    if 'vere_per_gruppo' in out:
        g = out['vere_per_gruppo']
        for chiave_g, titolo in (('sezione', 'sezione'), ('tipo_di_pagina', 'tipo di pagina'), ('lingua', 'lingua A/B'), ('mano', 'mano')):
            r += ['', '## Le pagine vere per %s' % titolo, '',
                  '| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina | profilo | varianti |', '|---|---|---|---|---|---|---|---|---|']
            for k, x in g[chiave_g].items():
                if 'E_vic' in x:
                    r.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s |' % (k, x['pagine'], x['parole'], vv(x['E_vic'], 4), vv(x['E_lon'], 4), vv(x['H'], 2),
                                                                                 vv(x['QV_vic'], 2), x['profilo'], x['varianti']))
                else:
                    r.append('| %s | %d | - | - | - | - | - | - | - |' % (k, x['pagine']))
            e = g.get('eterogeneita_sezione' if chiave_g == 'sezione' else 'eterogeneita_tipo' if chiave_g == 'tipo_di_pagina' else '')
            if e:
                r.append('')
                r.append('Eterogeneita\' dell\'eco vicina fra i gruppi: %s' % json.dumps(e, ensure_ascii=False))
        a = g['area_disegno_erbario']
        r += ['', '## Erbario: disegno piccolo, medio, grande (terzili dell\'area del disegno, e190)', '']
        for k, x in a.items():
            if isinstance(x, dict) and 'E_vic' in x:
                r.append('- %s (%d pagine): eco vicina %s; lontana %s; H %s' % (k, x['pagine'], vv(x['E_vic'], 4), vv(x['E_lon'], 4), vv(x['H'], 2)))
        if out.get('controlli_per_sezione'):
            r += ["", "## Eterogeneita' dell'eco vicina per sezione nei generatori sintetici (nessuna sezione nel testo) e nelle lingue nella disposizione del Voynich (latGeom, ingGeom): il Voynich si legge contro questi", ""]
            for k, x in out['controlli_per_sezione'].items():
                r.append('- per sezione, %s: %s' % (k, json.dumps(x, ensure_ascii=False)))
            for k, x in out.get('controlli_per_tipo', {}).items():
                r.append('- per tipo di pagina, %s: %s' % (k, json.dumps(x, ensure_ascii=False)))
    v = out.get('v21_contro_vere')
    if v:
        r += ['', '## v21 contro vere (media dei libri meno vere)', '', '| misura | vere | v21 | differenza | rapporto |', '|---|---|---|---|---|']
        for k, x in v.items():
            if isinstance(x, dict):
                r.append('| %s | %s | %s | %s | %s |' % (k, vv(x['vere'], 4), vv(x['v21'], 4), vv(x['differenza'], 4), f2(x['rapporto'])))
    p = out.get('ponte_ia09')
    if p and 'nota' not in p:
        r += ['', '## Ponte con ia09: copia netta in bit per parola (modelli di ia09) per sezione e tipo di pagina', '',
              '| gruppo | pagine | copia netta (bit) | guadagno g (bit) | quota di copia rho |', '|---|---|---|---|---|']
        r.append('| tutte | - | %s | - | - |' % vv(p['tutte']['copia_netta_bit'], 3))
        for chiave_g in ('sezione', 'tipo_di_pagina'):
            for k, x in p.get(chiave_g, {}).items():
                r.append('| %s %s | %d | %s | %s | %s |' % (chiave_g, k, x['pagine'], vv(x['copia_netta_bit'], 3), vv(x['guadagno_g'], 3), vv(x['rho'], 2)))
    elif p:
        r += ['', '## Ponte con ia09', '', p['nota']]
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def main():
    import scipy
    versioni = dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'conteggi,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d; libri %s; riferimenti %d; spostamenti %d' % (len(c['ids']), LIBRI_V21, NRIF, SPOSTAMENTI), flush=True)
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI_V21 if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01)' % (', '.join(mancano), G.LIBRI))
    percorso = os.path.join(USCITA, 'ia15_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = carica_corse(percorso)
    elif 'conteggi' in fasi:
        open(percorso, 'w').close()
    if 'conteggi' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        Lj = lavori(['conteggi'])
        da_fare = [j for j in Lj if json.dumps(list(j)) not in fatte]
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(Lj) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 4))

        def registra(i, r):
            corse.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
            print('[%d/%d %.0f min] %s (%.0f s)' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo']), flush=True)
        if processi <= 1:
            for i, j in enumerate(da_fare, 1):
                registra(i, esegui_lavoro(j))
        else:
            with get_context('spawn').Pool(processi) as pool:
                for i, r in enumerate(pool.imap_unordered(esegui_lavoro, da_fare), 1):
                    registra(i, r)
    elif os.path.exists(percorso):
        corse = carica_corse(percorso)
    if 'analisi' in fasi:
        analisi(corse, versioni)


if __name__ == '__main__':
    main()
