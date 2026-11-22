# -*- coding: utf-8 -*-
"""Esperimento IA27 (ia27): il modello esplicito a sorgenti latenti, senza reti, stimato a massima verosimiglianza.

Domanda (revisione esterna del 22/11/2026, proposta C2; parte della proposta 3 del coordinatore): da dove viene ogni parola e in che dose? Un modello leggibile, con
pochi parametri, scritto in chiaro, tiene insieme l'eco (le parole ricopiate dalla riga e dalla pagina) e il contatto fra parole, dove gli imitatori neurali di ia20-ia24
non ci riescono? E che cosa non spiega? Il modello (cinque sorgenti: lessico generale L, lessico di sezione S, forma F, riga R, pagina P; contatto; ritocco) sta in
`sorgenti_modello.py`, il modo di scrivere testo in `sorgenti_genera.py`, i dati in `sorgenti_dati.py`. Preregistrazione: preregistrazioni/ia27.md.
Importa, senza modificarli, `ia07_voynich_neurale` (disposizione, pieghe per foglio, giudici del paper, giudice A, copia a memoria), `ia16_imitatore` (letture contro il
v21), `ia20_imitatore_gradini` (misure, regole "al vero", libri e modelli di M1 e M5 come riferimento), `imitatore_misure` (giudice K, copia netta e Λ di ia09, D di
ia10, contatto di ia08), `aprire_parole` (bordi) e `rifarlo_ritocchi` (forma delle parole nuove). Non tocca il voynichizzatore. Aggancio per il banco di IA26: vedi `righello`.

Che cosa fa il codice (in parole semplici)
- Fase A: stima (EM) di ogni versione del modello su ogni piega per foglio (addestramento: i 70 fogli di ia07; fuori: i 20 fogli tenuti fuori), piu' una stima su tutte le pagine
  ("tutto") per le quote; bit per segno e per parola fuori piega; confronto con un bigramma di parole (modello a conteggi); costo dei bit per tipo di parola.
- Fase Q: controlli. Positivo: testi scritti dal modello con parametri noti (tre forze), la stima deve ritrovarli entro tolleranze scritte prima. Negativo: parole
  rimescolate (fra pagine dello stesso gruppo: decisivo; dentro la pagina; righe fra pagine). Latino nella disposizione del Voynich.
- Fase B: intervalli delle quote per ricampionamento delle pagine (EM a caldo su ogni ricampionamento) per la versione piena e per quella senza sorgente di sezione.
- Fase C: libri scritti dal modello (onesti: ogni pagina e' scritta dal modello della piega che non ha visto il suo foglio), con i giudici del paper, A, la copia a memoria.
- Fase D: controlli dei giudici, giudice K e misure di struttura (copia netta, Λ, contatto, D, G9, bordi, parole nuove e forma) dei libri e dei riferimenti (M1 e M5 di ia20, v21).
- Fase S: sintesi e letture preregistrate (`risultati/ia27_modello_sorgenti.json` e `.md`).
Uscite (solo numeri e aggregati, nessuna parola ne' riga): risultati/ia27_*.json, .md, ia27_corse.jsonl (una riga per lavoro; con RIPRENDI=1 i fatti non si rifanno).
Modelli (parametri), libri e profili in dati/cache/ia27 (CACHE27, protetti).

    nohup bash strumenti/coda.sh ia27 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia27" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO27=1 USCITA=<cartella fuori dal repo> python esperimenti/ia27_modello_sorgenti.py     (prova sul libro latino)

Variabili (oltre a quelle di ia07, che si importano: SOLO_CONTROLLI, USCITA, PASSI_A, OGNI_A, PAZIENZA_A, NASCOSTO_A, CADUTA_A): PROCESSI, RIPRENDI, FASI (lettere A Q B C D S;
predefinito tutte), FILTRO. Nuove: CACHE27, N_LIBRI27 (10: libri della versione piena), N_LIBRI_VAR27 (5: libri delle altre versioni), VARIANTI27 (versioni, separate da +),
VAR_LIBRI27 (versioni che scrivono libri, separate da +), BOOT27 (200 ricampionamenti), MAXIT27 (60 passi EM), N_INNER27 (10 gruppi di fogli per i lessici a incrocio),
SEMI_CTRL27 (5), PICCOLO27 (solo prove: meno ricampionamenti e semi), RIF27 (cache: i riferimenti M1 e M5 si leggono dalla cache di ia20; no: non si usano), RIGHELLO27 (1: ogni libro e' profilato anche con `righello_banco.profila_testo` di IA26, se il suo riferimento esiste; facoltativo, nessuna lettura ne dipende). I valori predefiniti sono quelli preregistrati.
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
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import ia20_imitatore_gradini as I20  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import sorgenti_dati as SD  # noqa: E402
import sorgenti_modello as SM  # noqa: E402
import sorgenti_genera as SG  # noqa: E402

NOME = 'ia27_modello_sorgenti'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE27 = os.environ.get('CACHE27', os.path.join(USCITA, 'ia27_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia27'))
MOD27, LIBRI27, MISURE27 = os.path.join(CACHE27, 'modelli'), os.path.join(CACHE27, 'libri'), os.path.join(CACHE27, 'misure')
PICCOLO = os.environ.get('PICCOLO27') == '1'
PIEGHE = I7.PIEGHE
N_LIBRI27 = int(os.environ.get('N_LIBRI27', 10))
N_LIBRI_VAR27 = int(os.environ.get('N_LIBRI_VAR27', 5))
BOOT27 = int(os.environ.get('BOOT27', 20 if PICCOLO else 200))
CHUNK_BOOT = 20
BOOT_PASSI = 8
MAXIT27 = int(os.environ.get('MAXIT27', 60))
N_INNER27 = int(os.environ.get('N_INNER27', 10))
SEMI_CTRL27 = int(os.environ.get('SEMI_CTRL27', 2 if PICCOLO else 5))
RIF27 = os.environ.get('RIF27', 'cache')
VARIANTI27 = [x for x in os.environ.get('VARIANTI27', '+'.join(SM.varianti())).split('+') if x]
VAR_LIBRI27 = [x for x in os.environ.get('VAR_LIBRI27', 'pieno+copia_con_contatto+ritocco_con_contatto+senza_copia+nucleo_piatto').split('+') if x]
VARIANTI_BOOT = ('pieno', 'senza_S')
RIF_PASSI = (1, 5)
N_RIF = I20.N_LIBRI20
CHIAVI_V21 = I20.CHIAVI_V21
SOGLIA_ERRORI, VERO_TOL = I20.SOGLIA_ERRORI, I20.VERO_TOL
MISURE_STR, GIUDICI = I20.MISURE_STR, I20.GIUDICI
POS_PAPER, NEG_BANDA, POS_K, K_VEDE_V21 = I20.POS_PAPER, I20.NEG_BANDA, I20.POS_K, I20.K_VEDE_V21

# ---- soglie dei controlli (scritte nella preregistrazione; quelle marcate "dopo la prova" sono state fissate dopo prove sul latino e su testi sintetici, non sul Voynich)
FORZE = OrderedDict([('debole', (0.006, 0.004)), ('media', (0.012, 0.008)), ('forte', (0.03, 0.02))])    # quote vere di R e di P nei testi sintetici
TOL_QUOTA = (0.20, 0.012)                    # |stima - vero| <= max(20% del vero, 0,012) (dopo la prova: sotto circa 0,012 la quota di R e P non si distingue da zero)
TOL_RHO = 0.10                               # tipi di ritocco di R: ognuno entro 0,10
TOL_NUCLEO = 0.15                            # distanza fra le masse per classe (variazione totale) del nucleo di R
TOL_CONTATTO = 0.25                          # guadagno del contatto (bit per parola su pagine fuori) entro il 25% di quello vero, oppure entro TOL_CONTATTO_ASS
TOL_CONTATTO_ASS = 0.02
MIN_POS_SEMI = 4                             # il controllo positivo riesce se almeno 4 semi su 5 ritrovano tutto
GAIN_MIN_POS = 0.02                          # sul testo sintetico la copia deve valere almeno 0,02 bit per parola fuori piega
NEG_R, NEG_P, NEG_GAIN = 0.02, 0.05, 0.08    # rimescolamento fra pagine: quota di R, quota di P, guadagno di copia (bit per parola) al massimo (dopo la prova)
LATINO_GAIN, LATINO_QUOTE = 0.25, 0.08       # latino: guadagno di copia e quota R+P al massimo (dopo la prova)
AUTO_RAPPORTO = 1.5                          # autocoerenza: guadagno di copia del testo scritto / del testo vero al massimo
GRU_VICINO = 0.10                            # modello entro 0,10 bit per segno dalla GRU: "competitivo"

_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def mes(xs):
    return MS.media_es(xs)


def seme_str(*a):
    return MS.seme_str(*a)


# ---------------------------------------------------------------- dati

def dati():
    """(pagine, bordi, Voc) del libro vero (nelle prove: latino con la disposizione del Voynich)."""
    if 'dati' not in _C:
        pagine, bordi = SD.pagine_vere()
        _C['dati'] = (pagine, bordi, SM.Voc(I7.vocabolario()['unita']))
    return _C['dati']


def split(piega):
    pagine, bordi, voc = dati()
    return SD.dividi_pagine(pagine, piega), bordi, voc


def valida_parola(w):
    D = I7.divisore()
    return len(w) > 0 and D(''.join(w)) == list(w)


def percorso_par(var, piega):
    return os.path.join(MOD27, 'ia27_%s_%s.pkl' % (var, piega))


def seme_basi(piega):
    return 1 if piega == 'tutto' else int(piega) + 2


def costruisci_base(piega, pagine_add=None):
    """Lessici a incrocio e rischio di fine riga della piega (deterministici)."""
    (add, val, fuori), bordi, voc = split(piega)
    add = pagine_add if pagine_add is not None else add
    return add, val, fuori, bordi, voc, SM.Basi(add, voc, n_inner=N_INNER27, seme=seme_basi(piega)), SD.Rischio(add, bordi)


def pooled(par, calc_c):
    """Quote pooled sui gruppi di lingua (pesate con le parole di ognuno)."""
    n = np.array([float((calc_c.lg == g).sum()) for g in range(3)])
    return (par.pi * n[:, None]).sum(0) / max(n.sum(), 1.0)


def masse_nucleo(par, calc):
    """Quota delle scelte di ricopiatura per classe di distanza (R: 24 classi; P: 5), a parametri dati (passo E)."""
    ll, _ = calc.passo(par)
    post, E = calc._stat['post'], calc.E
    mR = np.bincount(E['k'][E['src'] == 0], weights=post[E['src'] == 0], minlength=SM.KR)
    mP = np.bincount(E['k'][E['src'] == 1], weights=post[E['src'] == 1], minlength=SM.KP)
    calc._masse_freq = (np.bincount(E['b'][E['src'] == 0], weights=post[E['src'] == 0], minlength=SM.NF), np.bincount(E['b'][E['src'] == 1], weights=post[E['src'] == 1], minlength=SM.NF))
    return mR / max(mR.sum(), 1e-12), mP / max(mP.sum(), 1e-12), float(mR.sum()), float(mP.sum())


def info_contatto(par, c):
    """Informazione mutua (bit) fra contesto e primo glifo secondo la tabella del contatto, con le frequenze dei contesti del corpus `c`."""
    ref = par.ref
    pc = ref[None, :] * par.g
    pc = pc / pc.sum(1, keepdims=True)                        # il primo glifo di una parola fresca dopo ogni contesto (con il fattore di contatto)
    pctx = np.bincount(c.ctx, minlength=c.voc.Cx).astype(float)
    pctx = pctx / pctx.sum()
    return float((pctx[:, None] * pc * np.log2(np.maximum(pc, 1e-12) / np.maximum(ref[None, :], 1e-12))).sum())


def riassunto(par, calc, var):
    mR, mP, nR, nP = masse_nucleo(par, calc)
    r = SM.riassunto_parametri(par)
    r['quota_pooled'] = [float(x) for x in pooled(par, calc.c)]
    r['massa_R'], r['massa_P'] = [float(x) for x in mR], [float(x) for x in mP]
    fr = calc._masse_freq
    r['massa_freq_R'], r['massa_freq_P'] = [float(x) for x in fr[0] / max(fr[0].sum(), 1e-12)], [float(x) for x in fr[1] / max(fr[1].sum(), 1e-12)]
    r['scelte_R'], r['scelte_P'] = nR, nP
    r['info_contatto'] = info_contatto(par, calc.c)
    d = np.diff(par.ll)
    r['iterazioni'] = len(par.ll)
    r['ll_media_finale'] = float(par.ll[-1] / max(calc.peso.sum(), 1.0))
    r['ll_non_decresce'] = bool(np.all(d >= -1e-7 * np.abs(np.array(par.ll[1:])))) if len(d) else True
    return r


def diagnosi(par, calc_f, basi):
    """Dove spende i bit il modello su pagine nuove: per tipo di parola (nuova, nota con possibile ripresa, nota senza ripresa) e il rischio di fine riga."""
    x = calc_f._componenti(par)
    P = np.maximum((x['comp'] * x['pis']).sum(1), SM.EPS_P)
    bit = -np.log2(P)
    c = calc_f.c
    nuova = np.array([basi.conteggio_L(w, basi.H) == 0 for w in c.parole])
    ev = np.bincount(calc_f.E['t'], minlength=c.T) > 0
    out = OrderedDict()
    for nome, m in (('parole nuove', nuova), ('note con una parola uguale o a un ritocco gia scritta in pagina', (~nuova) & ev), ('note senza', (~nuova) & ~ev)):
        out[nome] = [float(bit[m].sum()), int(m.sum())]
    out['fine parola (spazio o fine riga)'] = [float(c.bits_stop.sum()), int(c.T)]
    out['glifi'] = float((c.ln).sum())
    return out


# ---------------------------------------------------------------- lavori: stima

def lavoro_stima(nome, piega):
    inizio = time.time()
    piega = piega if piega == 'tutto' else int(piega)
    var = SM.varianti()[nome]
    add, val, fuori, bordi, voc, basi, rischio = costruisci_base(piega)
    par, basi, calc = SM.stima(add, voc, rischio, var, n_inner=N_INNER27, seme=seme_basi(piega), basi=basi, max_iter=MAXIT27)
    os.makedirs(MOD27, exist_ok=True)
    with open(percorso_par(nome, piega), 'wb') as fh:
        pickle.dump(par, fh)
    ris = OrderedDict([('lavoro', 'stima|%s|%s' % (nome, piega)), ('variante', nome), ('piega', piega), ('pagine', [len(add), len(val), len(fuori)])])
    bw, bs, ns, _ = calc.verosimiglianza(par)
    ris['addestramento'] = OrderedDict(bit_per_parola=bw / calc.c.T, bit_per_segno=(bw + bs) / ns, nota='lessici a incrocio')
    if piega != 'tutto':
        for et, pg in (('validazione', val), ('fuori', fuori)):
            r, per, cf = SM.valuta(par, pg, voc, rischio, basi, var)
            ris[et] = r
            if et == 'fuori' and nome in ('pieno', 'senza_copia', 'solo_lessico', 'senza_S'):
                ris['diagnosi'] = diagnosi(par, cf, basi)
    ris['parametri'] = riassunto(par, calc, var)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_bigramma(piega):
    """Modello a conteggi: bigramma di parole (Witten-Bell) sopra il modello `solo_lessico` (lessico + forma, senza contatto e senza copia)."""
    inizio = time.time()
    piega = int(piega)
    var = SM.varianti()['solo_lessico']
    add, val, fuori, bordi, voc, basi, rischio = costruisci_base(piega)
    par, basi, calc = SM.stima(add, voc, rischio, var, n_inner=N_INNER27, seme=seme_basi(piega), basi=basi, max_iter=MAXIT27)
    cnt, seg = {}, {}
    for p in add:
        for r in p.righe:
            prec = '^'
            for w in r.parole:
                cnt.setdefault(prec, Counter())[w] += 1
                prec = w
    out = OrderedDict([('lavoro', 'bigramma|%d' % piega), ('piega', piega)])
    for et, pg in (('validazione', val), ('fuori', fuori)):
        r, per, cf = SM.valuta(par, pg, voc, rischio, basi, var)
        Puni = 2.0 ** (-per)
        bit, t = 0.0, 0
        for p in pg:
            for rg in p.righe:
                prec = '^'
                for w in rg.parole:
                    c = cnt.get(prec)
                    if c:
                        tot, T = sum(c.values()), len(c)
                        P = (c.get(w, 0) + T * Puni[t]) / (tot + T)
                    else:
                        P = Puni[t]
                    bit -= math.log2(max(P, 1e-300))
                    t += 1
                    prec = w
        out[et] = OrderedDict(bit_per_parola=bit / t, bit_per_segno=(bit + r['bit_fine']) / r['segni'], parole=t)
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_boot(nome, chunk):
    """Ricampionamento delle pagine (con rimpiazzo) sul testo intero: per ogni estrazione, EM a caldo (BOOT_PASSI passi) dalla stima di massima verosimiglianza."""
    inizio = time.time()
    var = SM.varianti()[nome]
    (add, val, fuori), bordi, voc = split('tutto')
    basi = SM.Basi(add, voc, n_inner=N_INNER27, seme=seme_basi('tutto'))
    rischio = SD.Rischio(add, bordi)
    corpus = SM.Corpus(add, voc, rischio, basi.gruppi_sl, basi.hid_di_foglio)
    calc = SM.Calcolo(corpus, basi, var)
    par0 = SM.iniziale(SM.Par(voc, var), corpus, var)
    par0 = calc.adatta(par0, max_iter=MAXIT27)
    P = len(add)
    prima = chunk * CHUNK_BOOT
    righe = []
    for b in range(prima, min(prima + CHUNK_BOOT, BOOT27)):
        rng = np.random.default_rng(2700000 + b)
        w = np.bincount(rng.integers(0, P, P), minlength=P).astype(float)
        calc.peso = w[corpus.pag]
        par = calc.adatta(par0.copia(), max_iter=BOOT_PASSI, tol=-1.0)
        mR, mP, _, _ = masse_nucleo(par, calc)
        righe.append(OrderedDict(b=b, quota=[float(x) for x in pooled(par, corpus)], per_lingua=[[float(x) for x in r] for r in par.pi], rho=[[float(x) for x in r] for r in par.rho],
                                 massa_R=[float(x) for x in mR], massa_P=[float(x) for x in mP], kR=[float(x) for x in par.kR], kP=[float(x) for x in par.kP],
                                 phiR=[float(x) for x in par.phiR], phiP=[float(x) for x in par.phiP], info_contatto=info_contatto(par, corpus)))
    return OrderedDict([('lavoro', 'boot|%s|%d' % (nome, chunk)), ('variante', nome), ('chunk', chunk), ('estrazioni', righe), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- lavori: controlli

def parametri_noti(base, voc, forza, seme):
    """Parametri veri di un testo sintetico: quote di R e P date dalla forza, nucleo che cala con la distanza, ritocchi, posto e glifo scelti a priori; il
    contatto e' quello stimato sul testo vero (solo come forma)."""
    pr, pp = FORZE[forza]
    rng = np.random.default_rng(2700100 + seme)
    p = SM.Par(voc, SM.varianti()['pieno'])
    fr = np.array([0.45, 0.30, 0.25])
    p.pi = np.tile(np.concatenate([fr / fr.sum() * (1.0 - pr - pp), [pr, pp]]), (3, 1))
    d = SM.EDGES_D.astype(float)
    p.kR = np.concatenate([1.0 / (1.0 + d / 3.0), 0.5 / (1.0 + d / 6.0)])
    p.kR = p.kR / p.kR.mean()
    p.kP = np.array([1.0, 0.8, 0.6, 0.4, 0.3])
    p.kP = p.kP / p.kP.mean()
    p.rho = np.tile(np.array([0.55, 0.25, 0.10, 0.10]), (2, 1))
    p.omega = np.array([[3.0, 1.0, 2.0], [2.0, 1.0, 1.0], [1.0, 1.0, 2.0]])
    p.tau = rng.dirichlet(np.ones(voc.G) * 2.0, size=(2, 2, voc.Cx))
    p.ref, p.pc, p.g = base.ref, base.pc, base.g
    return p


def tv(a, b):
    return float(0.5 * np.abs(np.asarray(a) - np.asarray(b)).sum())


def guadagno_copia(pagine, piega=0, bordi=None, voc=None):
    """Stima la versione piena e quella senza copia; guadagno (bit per parola, fuori piega) della copia R+P e le due stime."""
    (add, val, fuori), bordi, voc = SD.dividi_pagine(pagine, piega), bordi or dati()[1], voc or dati()[2]
    rischio = SD.Rischio(add, bordi)
    out = {}
    for nome in ('pieno', 'senza_copia'):
        var = SM.varianti()[nome]
        par, basi, calc = SM.stima(add, voc, rischio, var, n_inner=N_INNER27, seme=7, max_iter=MAXIT27)
        r, per, _ = SM.valuta(par, fuori, voc, rischio, basi, var)
        out[nome] = (par, basi, calc, r)
    return out, rischio, bordi, voc, add, val, fuori


def lavoro_ctrl_pos(forza, seme):
    inizio = time.time()
    pagine, bordi, voc = dati()
    add, val, fuori, bordi, voc, basi, rischio = costruisci_base(0)
    var = SM.varianti()['pieno']
    par_vero0, basi0, calc0 = SM.stima(add, voc, rischio, var, n_inner=N_INNER27, seme=seme_basi(0), basi=basi, max_iter=min(MAXIT27, 25))
    p = parametri_noti(par_vero0, voc, forza, seme)
    sint = SG.Scrittore(p, basi0, rischio, voc, var, valida=None).scrivi(pagine, 2700200 + seme)
    o, rischio2, _, _, sa, sv, sf = guadagno_copia(sint, 0)
    par, basi2, calc2, r1 = o['pieno']
    r0 = o['senza_copia'][3]
    gain = r0['bit_per_parola'] - r1['bit_per_parola']
    # nucleo "vero" e stimato sulla stessa metrica: le masse per classe sullo stesso testo, con i parametri veri e con quelli stimati
    mR_v, mP_v, _, _ = masse_nucleo(p, calc2)
    mR_s, mP_s, _, _ = masse_nucleo(par, calc2)
    pv, ps = FORZE[forza], pooled(par, calc2.c)
    q_ok = [abs(ps[3] - pv[0]) <= max(TOL_QUOTA[0] * pv[0], TOL_QUOTA[1]), abs(ps[4] - pv[1]) <= max(TOL_QUOTA[0] * pv[1], TOL_QUOTA[1])]
    rho_err = [float(abs(par.rho[0, i] - p.rho[0, i])) for i in range(4)]
    nucleo_tv = tv(mR_v, mR_s)
    ic_v, ic_s = info_contatto(p, calc2.c), info_contatto(par, calc2.c)
    # il contatto si misura in bit per parola guadagnati su pagine tenute fuori (senza il bias del conteggio di una tabella con molte celle)
    cf = SM.Corpus(sf, voc, rischio2, basi2.gruppi_sl, None, hid_default=basi2.H)
    calcf = SM.Calcolo(cf, basi2, var)

    def bit_parola(pp, senza_contatto):
        q = pp.copia()
        if senza_contatto:
            q.g = np.ones_like(q.g)
        return calcf.verosimiglianza(q)[0] / cf.T
    gc_s, gc_v = bit_parola(par, True) - bit_parola(par, False), bit_parola(p, True) - bit_parola(p, False)
    cont_err = abs(gc_s - gc_v)
    ok = OrderedDict(quota_R=bool(q_ok[0]), quota_P=bool(q_ok[1]), ritocchi=bool(max(rho_err) <= TOL_RHO), nucleo=bool(nucleo_tv <= TOL_NUCLEO),
                     contatto=bool(cont_err <= max(TOL_CONTATTO * gc_v, TOL_CONTATTO_ASS)), guadagno_visto=bool(gain >= GAIN_MIN_POS))
    return OrderedDict([('lavoro', 'ctrl|pos|%s|%d' % (forza, seme)), ('forza', forza), ('seme', seme), ('veri', OrderedDict(quota_R=pv[0], quota_P=pv[1])),
                        ('stima', OrderedDict(quota_R=float(ps[3]), quota_P=float(ps[4]), quote_fresche=[float(x) for x in ps[:3]], rho_R=[float(x) for x in par.rho[0]])),
                        ('errore_rho', rho_err), ('distanza_nucleo_R', nucleo_tv), ('distanza_nucleo_P', tv(mP_v, mP_s)), ('info_contatto', [ic_v, ic_s]), ('guadagno_contatto', [float(gc_v), float(gc_s)]), ('guadagno_copia', gain),
                        ('riuscito', OrderedDict(ok)), ('tutto_ritrovato', bool(all(ok.values()))), ('secondi', round(time.time() - inizio, 1))])


def lavoro_ctrl_neg(modo, seme):
    inizio = time.time()
    pagine, bordi, voc = dati()
    sc = SD.rimescola(pagine, modo, 2700300 + seme)
    o, rischio, _, _, sa, sv, sf = guadagno_copia(sc, 0)
    par, basi, calc, r1 = o['pieno']
    gain = o['senza_copia'][3]['bit_per_parola'] - r1['bit_per_parola']
    q = pooled(par, calc.c)
    return OrderedDict([('lavoro', 'ctrl|neg|%s|%d' % (modo, seme)), ('modo', modo), ('seme', seme), ('quota_R', float(q[3])), ('quota_P', float(q[4])), ('quote', [float(x) for x in q]),
                        ('rho_R', [float(x) for x in par.rho[0]]), ('guadagno_copia', float(gain)), ('secondi', round(time.time() - inizio, 1))])


def lavoro_ctrl_auto(seme):
    """Autocoerenza: il modello stimato sul testo vero scrive un testo; lo stesso metodo lo rilegge. Le quote devono tornare e il guadagno di copia sul testo scritto deve
    somigliare a quello sul testo vero (rapporto al massimo AUTO_RAPPORTO): se il modello scrive molta piu' copia utile di quella che il vero ha, le quote reali
    sono un limite alto (il vocabolario di sezione spiega nel vero parte di cio' che nel modello e' ricopiatura)."""
    inizio = time.time()
    pagine, bordi, voc = dati()
    o0, rischio, _, _, _, _, _ = guadagno_copia(pagine, 0)
    par0, basi0, calc0, r0 = o0['pieno']
    gain0 = o0['senza_copia'][3]['bit_per_parola'] - r0['bit_per_parola']
    gen = SG.Scrittore(par0, basi0, rischio, voc, SM.varianti()['pieno']).scrivi(pagine, 2700400 + seme)
    o1, _, _, _, _, _, _ = guadagno_copia(gen, 0)
    par1, basi1, calc1, r1 = o1['pieno']
    gain1 = o1['senza_copia'][3]['bit_per_parola'] - r1['bit_per_parola']
    q0, q1 = pooled(par0, calc0.c), pooled(par1, calc1.c)
    return OrderedDict([('lavoro', 'ctrl|auto|%d' % seme), ('seme', seme), ('quote_vero', [float(x) for x in q0]), ('quote_scritto', [float(x) for x in q1]),
                        ('guadagno_vero', float(gain0)), ('guadagno_scritto', float(gain1)), ('rapporto', float(gain1 / max(gain0, 1e-9))),
                        ('phiR_vero', [float(x) for x in par0.phiR]), ('phiR_scritto', [float(x) for x in par1.phiR]), ('secondi', round(time.time() - inizio, 1))])


def lavoro_ctrl_latino():
    inizio = time.time()
    pagine, bordi = SD.latino_in_disposizione() if not SOLO_CONTROLLI else SD.pagine_vere()
    voc_l = SM.Voc(sorted({g for p in pagine for r in p.righe for w in r.parole for g in w}))      # i glifi del latino (non sono quelli del Voynich)
    o, rischio, _, _, sa, sv, sf = guadagno_copia(pagine, 0, bordi, voc_l)
    par, basi, calc, r1 = o['pieno']
    gain = o['senza_copia'][3]['bit_per_parola'] - r1['bit_per_parola']
    q = pooled(par, calc.c)
    return OrderedDict([('lavoro', 'ctrl|latino|0'), ('quota_R', float(q[3])), ('quota_P', float(q[4])), ('quote', [float(x) for x in q]), ('rho_R', [float(x) for x in par.rho[0]]),
                        ('guadagno_copia', float(gain)), ('bit_per_segno', r1['bit_per_segno']), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- lavori: libri scritti dal modello

def idx_var(nome):
    return list(SM.varianti()).index(nome)


def percorso_libro(nome, i):
    return os.path.join(LIBRI27, 'ia27_libro_%s_%d.txt' % (nome, i))


def scrivi_libro(nome, seme):
    """Il libro intero: ogni pagina e' scritta dal modello della piega che non ha visto il suo foglio, con la disposizione vera. -> lista (pagina, inizio, parole)."""
    pagine, bordi, voc = dati()
    var = SM.varianti()[nome]
    rng = np.random.default_rng(seme)
    scritt = {}
    for k in range(PIEGHE):
        add, val, fuori, _, _, basi, rischio = costruisci_base(k)
        par = pickle.load(open(percorso_par(nome, k), 'rb'))
        scritt[k] = (SG.Scrittore(par, basi, rischio, voc, var, valida=valida_parola), set(p.foglio for p in fuori))
    out = []
    for p in pagine:
        k = next(k for k, (s, ff) in scritt.items() if p.foglio in ff)
        q = scritt[k][0].scrivi_pagina(p, rng)
        out += [(q.nome, r.ini, [''.join(w) for w in r.parole]) for r in q.righe]
    return out


def misura_libro(t, tabella):
    ris = OrderedDict()
    ris.update(I7.giudica(t, tabella))
    try:
        ris.update(I7.giudice_A(I7.libro_A_da_righe(t)))
    except Exception as e:                                                # noqa: BLE001
        ris['A_errore'] = repr(e)
    ris['copia'] = I7.copia_onesta(t)
    ris['ripetizioni'] = MS.ripetizioni_interne({p: [ps for _, ps in rr] for p, rr in I16._raggruppa(t).items()})
    return ris


def righello(t, nome):
    """Aggancio dichiarato per il banco di IA26: con RIGHELLO27=1 ogni libro scritto dal modello e' profilato anche con `righello_banco.profila_testo` (modulo di IA26,
    importato senza modificarlo, dopo `imposta_mondo('vero')`; richiede il `riferimento.json` della corsa di IA26). Il risultato (numeri) va in `righello` del lavoro del libro; un
    errore non ferma il lavoro. Nessuna lettura preregistrata dipende da esso."""
    if os.environ.get('RIGHELLO27') != '1':
        return None
    try:
        import righello_banco as RB
        RB.imposta_mondo('vero')
        return RB.profila_testo(I7.libro_A_da_righe(t), 'ia27_%s' % nome)
    except Exception as e:                                                # noqa: BLE001
        return OrderedDict([('errore', repr(e)[:200])])


def lavoro_libro(nome, i):
    inizio = time.time()
    os.makedirs(LIBRI27, exist_ok=True)
    percorso = percorso_libro(nome, i)
    seme = 2700000 + 10000 * idx_var(nome) + i
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t = scrivi_libro(nome, seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia27, libro %s %d' % (nome, i), None)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (nome, i)), ('variante', nome), ('i', i), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(misura_libro(t, os.path.join(LIBRI27, 'ia27_tabella_%s_%d.npz' % (nome, i))))
    rg = righello(t, '%s_%d' % (nome, i))
    if rg is not None:
        ris['righello'] = rg
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def percorso_rif(passo, i):
    return I20.percorso_libro(passo, i)


def lavoro_riflibro(passo, i):
    """Misure dei giudici sul libro i di M1 (passo 1) o M5 (passo 5) di ia20, letto dalla cache di ia20 (solo lettura)."""
    inizio = time.time()
    t = I7.leggi_file(percorso_rif(passo, i))
    ris = OrderedDict([('lavoro', 'riflibro|%d|%d' % (passo, i)), ('passo', passo), ('i', i), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(misura_libro(t, None))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- catalogo dei libri da misurare (fasi D)

def tipo_nostro(nome):
    return nome.split(':')[0] in VAR_LIBRI27


def e_rif(nome):
    return nome[0] == 'M' and nome[1:2].isdigit() and int(nome[1]) in RIF_PASSI


def n_libri_di(nome):
    return N_LIBRI27 if nome == 'pieno' else N_LIBRI_VAR27


def usa_rif():
    return RIF27 == 'cache' and not SOLO_CONTROLLI


def nomi_libri():
    nomi = []
    for v in VAR_LIBRI27:
        nomi += ['%s:%d' % (v, i) for i in range(1, n_libri_di(v) + 1) if os.path.exists(percorso_libro(v, i))]
    if usa_rif():
        for p in RIF_PASSI:
            nomi += ['M%d:%d' % (p, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_rif(p, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    out = [x for x in nomi if tipo_nostro(x) or e_rif(x)]
    out += [x for x in nomi if x.startswith('V21:')][:10]
    return out


def t_di(nome):
    if tipo_nostro(nome):
        return I7.leggi_file(percorso_libro(nome.split(':')[0], int(nome.split(':')[1])))
    if e_rif(nome):
        return I7.leggi_file(percorso_rif(int(nome[1]), int(nome.split(':')[1])))
    return I16.t_di(nome)


def rows_di(nome):
    if tipo_nostro(nome) or e_rif(nome):
        return I7.libro_A_da_righe(t_di(nome))
    return I16.rows_di(nome)


def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_libri():
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE27, exist_ok=True)
    with open(os.path.join(MISURE27, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome):
    import e266_discriminatore_forte as e266
    inizio = time.time()
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows = c['vere']
        g9 = I16.media_G9(k['vt266'])
    else:
        rows = rows_di(nome)
        g9 = I16.media_G9(e266.tabella(I7.righe_ini(t_di(nome)), k['rif266']))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'M|%s' % nome), ('G9', g9)])
    ris.update(MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag}))
    cp = {p: AP.conti_bordi({p: r}) for p, r in pag.items()}
    ris['bordi'] = AP.firma_da_conti(I20.somma_conti(list(cp.values())))
    if nome == 'vere':
        rng = np.random.default_rng(200027)
        ps = list(cp)
        bs = [AP.firma_da_conti(I20.somma_conti([cp[ps[i]] for i in rng.integers(0, len(ps), len(ps))])) for _ in range(200)]
        ris['bordi_ic'] = OrderedDict((kk, [float(np.nanpercentile([b[kk] for b in bs if b[kk] is not None], q)) for q in (2.5, 97.5)]) for kk in ris['bordi'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_struttura(nomi_libri()):
        testi[n] = rows_di(n)
    out, info = MS.lavoro_D(f, c, testi)
    pv = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] != f)
    cnt = Counter(w for rows in pv.values() for _, ws in rows for w in ws)
    forma, noti = R.Forma(cnt), set(cnt)
    fm = OrderedDict()
    for nome, rows in testi.items():
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        fm[nome] = R.costo_nuove(forma, pg, noti) if pg else [0.0, 0.0, 0, 0]
    return OrderedDict([('lavoro', 'D|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('forma', fm), ('secondi', round(time.time() - inizio, 1))])


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        tipo = args[0]
        if tipo == 'stima':
            return lavoro_stima(args[1], args[2])
        if tipo == 'bigramma':
            return lavoro_bigramma(args[1])
        if tipo == 'boot':
            return lavoro_boot(args[1], int(args[2]))
        if tipo == 'ctrl':
            if args[1] == 'pos':
                return lavoro_ctrl_pos(args[2], int(args[3]))
            if args[1] == 'neg':
                return lavoro_ctrl_neg(args[2], int(args[3]))
            if args[1] == 'auto':
                return lavoro_ctrl_auto(int(args[2]))
            return lavoro_ctrl_latino()
        if tipo == 'libro':
            return lavoro_libro(args[1], int(args[2]))
        if tipo == 'riflibro':
            return lavoro_riflibro(int(args[1]), int(args[2]))
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
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
                breve = {x: r[x] for x in ('AUC_e231', 'AUC_e266', 'AUC_A', 'AUC', 'G9', 'guadagno_copia') if x in r}
                if 'fuori' in r:
                    breve['fuori_bit_per_segno'] = round(r['fuori']['bit_per_segno'], 4)
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def leggi_corse(percorso):
    return I16.leggi_corse(percorso)


# ---------------------------------------------------------------- analisi e letture

def pc(x, q):
    return float(np.percentile(x, q))


def intervallo(x):
    x = [v for v in x if v is not None]
    return [pc(x, 2.5), pc(x, 97.5)] if len(x) >= 20 else None


def riferimenti_gru():
    """Bit per segno fuori piega delle reti di riferimento (schede json: solo numeri): ia07 (GRU), M1-M5 di ia20, E0-E3 di ia22. -> nome -> piega -> media sulle repliche."""
    cart22 = os.path.join(QUI, '..', 'dati', 'cache', 'ia22', 'modelli')
    sorg = OrderedDict()
    sorg['ia07 (GRU)'] = lambda k, r: os.path.join(I20.MODELLI_IA07, 'ia07_modello_%d_%d.json' % (k, r))
    for p in (1, 2, 3, 4, 5):
        sorg['M%d (ia20)' % p] = (lambda p: lambda k, r: I20.percorso_modello(p, k, r, '.json'))(p)
    for t in ('E0', 'E1', 'E2', 'E3'):
        sorg['%s (ia22)' % t] = (lambda t: lambda k, r: os.path.join(cart22, 'ia22_%s_%d_%d.json' % (t, k, r)))(t)
    out = OrderedDict()
    if SOLO_CONTROLLI:
        return out
    for nome, f in sorg.items():
        v = OrderedDict()
        for k in range(PIEGHE):
            xs = []
            for r in (0, 1):
                p = f(k, r)
                if os.path.exists(p):
                    d = json.load(open(p, encoding='utf-8'))
                    if d.get('bpc_fuori') is not None:
                        xs.append(d['bpc_fuori'])
            if xs:
                v[k] = float(np.mean(xs))
        if len(v) == PIEGHE:
            out[nome] = v
    return out


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    out = OrderedDict(esperimento='ia27', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=errori)
    # ---- 1. bit per segno fuori piega, per versione, e contro le reti
    bit = OrderedDict()
    for v in VARIANTI27:
        xs = [C['stima|%s|%d' % (v, k)] for k in range(PIEGHE) if 'stima|%s|%d' % (v, k) in C]
        if len(xs) == PIEGHE:
            bit[v] = OrderedDict(fuori_bps=mes([x['fuori']['bit_per_segno'] for x in xs]), fuori_bpp=mes([x['fuori']['bit_per_parola'] for x in xs]),
                                 validazione_bps=mes([x['validazione']['bit_per_segno'] for x in xs]), per_piega=[x['fuori']['bit_per_segno'] for x in xs],
                                 iterazioni=mes([x['parametri']['iterazioni'] for x in xs])[0], ll_non_decresce=all(x['parametri']['ll_non_decresce'] for x in xs))
    bg = [C['bigramma|%d' % k] for k in range(PIEGHE) if 'bigramma|%d' % k in C]
    if len(bg) == PIEGHE:
        bit['bigramma di parole (conteggi)'] = OrderedDict(fuori_bps=mes([x['fuori']['bit_per_segno'] for x in bg]), fuori_bpp=mes([x['fuori']['bit_per_parola'] for x in bg]),
                                                          validazione_bps=mes([x['validazione']['bit_per_segno'] for x in bg]), per_piega=[x['fuori']['bit_per_segno'] for x in bg])
    out['bit'] = bit
    gru = riferimenti_gru()
    conf = OrderedDict()
    for nome_r, v in gru.items():
        riga = OrderedDict(media=mes(list(v.values())))
        if 'pieno' in bit:
            dif = [bit['pieno']['per_piega'][k] - v[k] for k in range(PIEGHE)]
            riga['pieno_meno_rete'] = mes(dif)
            riga['entro_0_10'] = bool(mes(dif)[0] <= GRU_VICINO)
            riga['sotto_la_rete'] = bool(mes(dif)[0] < 0)
        conf[nome_r] = riga
    out['contro_le_reti'] = conf
    ablaz = OrderedDict()
    if 'pieno' in bit:
        for v in bit:
            if v == 'pieno':
                continue
            d = [bit[v]['per_piega'][k] - bit['pieno']['per_piega'][k] for k in range(PIEGHE)]
            dpp = [C['stima|%s|%d' % (v, k)]['fuori']['bit_per_parola'] - C['stima|pieno|%d' % k]['fuori']['bit_per_parola'] for k in range(PIEGHE)] if v in VARIANTI27 else None
            ablaz[v] = OrderedDict(bit_per_segno_in_piu=mes(d), bit_per_parola_in_piu=mes(dpp) if dpp else None)
    out['ablazioni'] = ablaz
    # ---- 2. quote e nucleo dalla stima sul testo intero e dai ricampionamenti
    tutto = C.get('stima|pieno|tutto')
    quote = OrderedDict()
    if tutto:
        P = tutto['parametri']
        quote['stima'] = OrderedDict(pooled=P['quota_pooled'], per_lingua=P['quote'], rho=P['rho'], omega=P['omega'], massa_R=P['massa_R'], massa_P=P['massa_P'],
                                     info_contatto=P['info_contatto'], kR=P['kR'], kP=P['kP'], phiR=P['phiR'], phiP=P['phiP'], massa_freq_R=P['massa_freq_R'], massa_freq_P=P['massa_freq_P'],
                                     scelte=[P['scelte_R'], P['scelte_P']])
        quote['per_piega'] = [C['stima|pieno|%d' % k]['parametri']['quota_pooled'] for k in range(PIEGHE) if 'stima|pieno|%d' % k in C]
    cf = [C['stima|con_frequenza|%s' % k] for k in list(range(PIEGHE)) + ['tutto'] if 'stima|con_frequenza|%s' % k in C]
    if cf:
        quote['frequenza'] = OrderedDict(phiR=[x['parametri']['phiR'] for x in cf], phiP=[x['parametri']['phiP'] for x in cf],
                                         rapporto_R=[x['parametri']['phiR'][2] / max(x['parametri']['phiR'][0], 1e-9) for x in cf], rapporto_P=[x['parametri']['phiP'][2] / max(x['parametri']['phiP'][0], 1e-9) for x in cf])
    boot = OrderedDict()
    for v in VARIANTI_BOOT:
        es = [e for k in sorted(C) if k.startswith('boot|%s|' % v) for e in C[k]['estrazioni']]
        es.sort(key=lambda e: e['b'])
        if es:
            boot[v] = es
    for v, es in boot.items():
        qs = np.array([e['quota'] for e in es])
        quote['boot_' + v] = OrderedDict(n=len(es), quota=[intervallo(qs[:, s]) for s in range(5)], quota_copia=intervallo(qs[:, 3] + qs[:, 4]), rho_R=[intervallo([e['rho'][0][i] for e in es]) for i in range(4)],
                                         massa_R=[intervallo([e['massa_R'][k] for e in es]) for k in range(SM.KR)], massa_P=[intervallo([e['massa_P'][k] for e in es]) for k in range(SM.KP)],
                                         info_contatto=intervallo([e['info_contatto'] for e in es]),
                                         rapporto_vicino_lontano=intervallo([float(np.mean(e['kR'][0:3]) / max(np.mean(e['kR'][SM.NB + 8:SM.NB + 12]), 1e-9)) for e in es]))
    if len(boot) == 2 and 'pieno' in boot and 'senza_S' in boot:
        a, b = {e['b']: e for e in boot['pieno']}, {e['b']: e for e in boot['senza_S']}
        com = sorted(set(a) & set(b))
        if len(com) >= 20:
            dif = np.array([(b[i]['quota'][3] + b[i]['quota'][4]) - (a[i]['quota'][3] + a[i]['quota'][4]) for i in com])
            quote['senza_S_meno_pieno_copia'] = OrderedDict(n=len(com), media=float(dif.mean()), intervallo=intervallo(dif))
    out['quote'] = quote
    # ---- 3. controlli del modello
    ctr = OrderedDict()
    pos = OrderedDict()
    for forza in FORZE:
        rs = [C['ctrl|pos|%s|%d' % (forza, s)] for s in range(1, SEMI_CTRL27 + 1) if 'ctrl|pos|%s|%d' % (forza, s) in C]
        if rs:
            crit = OrderedDict((k, sum(bool(r['riuscito'][k]) for r in rs)) for k in rs[0]['riuscito'])
            pos[forza] = OrderedDict(semi=len(rs), per_criterio=crit, tutto_ritrovato=sum(bool(r['tutto_ritrovato']) for r in rs),
                                     soglia_semi=min(MIN_POS_SEMI, len(rs)), riuscito=bool(sum(bool(r['tutto_ritrovato']) for r in rs) >= min(MIN_POS_SEMI, len(rs))),
                                     quota_R=[r['stima']['quota_R'] for r in rs], vero_R=rs[0]['veri']['quota_R'], quota_P=[r['stima']['quota_P'] for r in rs], vero_P=rs[0]['veri']['quota_P'],
                                     errore_rho_max=[max(r['errore_rho']) for r in rs], distanza_nucleo_R=[r['distanza_nucleo_R'] for r in rs], distanza_nucleo_P=[r['distanza_nucleo_P'] for r in rs],
                                     guadagno=[r['guadagno_copia'] for r in rs], info_contatto=[r['info_contatto'] for r in rs])
    ctr['positivo'] = pos
    neg = OrderedDict()
    for modo in ('fra_pagine', 'dentro_pagina', 'righe_fra_pagine'):
        rs = [C['ctrl|neg|%s|%d' % (modo, s)] for s in range(1, 4) if 'ctrl|neg|%s|%d' % (modo, s) in C]
        if rs:
            neg[modo] = OrderedDict(semi=len(rs), quota_R=[r['quota_R'] for r in rs], quota_P=[r['quota_P'] for r in rs], guadagno=[r['guadagno_copia'] for r in rs])
    if 'fra_pagine' in neg:
        n = neg['fra_pagine']
        n['riuscito'] = bool(max(n['quota_R']) <= NEG_R and max(n['quota_P']) <= NEG_P and max(n['guadagno']) <= NEG_GAIN)
    ctr['negativo'] = neg
    au = [C['ctrl|auto|%d' % s] for s in range(1, 4) if 'ctrl|auto|%d' % s in C]
    if au:
        ctr['autocoerenza'] = OrderedDict(semi=len(au), quote_vero=au[0]['quote_vero'], quote_scritto=[a['quote_scritto'] for a in au], guadagno_vero=au[0]['guadagno_vero'],
                                          guadagno_scritto=[a['guadagno_scritto'] for a in au], rapporto=[a['rapporto'] for a in au], phiR_vero=au[0]['phiR_vero'],
                                          phiR_scritto=[a['phiR_scritto'] for a in au], riuscito=bool(max(a['rapporto'] for a in au) <= AUTO_RAPPORTO))
    if 'ctrl|latino|0' in C:
        L = C['ctrl|latino|0']
        ctr['latino'] = OrderedDict(quota_R=L['quota_R'], quota_P=L['quota_P'], guadagno=L['guadagno_copia'], rho_R=L['rho_R'],
                                    riuscito=bool(L['guadagno_copia'] <= LATINO_GAIN and L['quota_R'] + L['quota_P'] <= LATINO_QUOTE))
    out['controlli_modello'] = ctr
    # ---- letture del modello (regole scritte nella preregistrazione)
    LM = OrderedDict()
    n1 = ctr['negativo'].get('fra_pagine', {}).get('riuscito')
    pos_media = ctr['positivo'].get('media', {}).get('riuscito')
    pos_deb = ctr['positivo'].get('debole', {}).get('riuscito')
    LM['strumento_valido'] = OrderedDict(negativo_fra_pagine=n1, positivo_forza_media=pos_media, positivo_forza_debole=pos_deb,
                                         autocoerenza=ctr.get('autocoerenza', {}).get('riuscito'),
                                         nota='le quote si leggono come misure solo se il negativo e il positivo di forza media riescono; se la prova di autocoerenza fallisce sono limiti alti')
    bp = quote.get('boot_pieno')
    if bp:
        valido = bool(n1) and bool(pos_media)
        rR, rP = bp['quota'][3], bp['quota'][4]
        LM['R_riga'] = 'non letta (controlli non riusciti)' if not valido else 'presente' if rR and rR[0] > NEG_R else 'assente o sotto il pavimento (limite basso sotto %s)' % NEG_R
        LM['P_pagina'] = 'non letta (controlli non riusciti)' if not valido else 'presente' if rP and rP[0] > NEG_P else 'assente o sotto il pavimento (limite basso sotto %s)' % NEG_P
        nv = bp.get('rapporto_vicino_lontano')
        LM['nucleo_cala_con_la_distanza'] = 'si' if nv and nv[0] > 2.0 else 'no o non provato (rapporto vicino/lontano, limite basso <= 2)'
        if 'senza_S_meno_pieno_copia' in quote:
            d = quote['senza_S_meno_pieno_copia']
            tot = (quote['stima']['pooled'][3] + quote['stima']['pooled'][4]) if 'stima' in quote else None
            LM['eco_e_vocabolario_di_sezione'] = ('in parte era vocabolario di sezione' if d['intervallo'] and d['intervallo'][0] > 0 and tot and d['media'] > 0.25 * tot
                                                  else 'l eco regge alla sezione' if d['intervallo'] and tot and d['media'] <= 0.25 * tot else 'non decidibile')
    fq = quote.get('frequenza')
    if fq:
        rr = fq['rapporto_R']
        LM['si_ricopiano'] = 'soprattutto parole frequenti' if max(rr) < 1.0 else 'soprattutto parole rare' if min(rr) > 1.0 else 'senza preferenza netta per la frequenza (le pieghe non concordano)'
    sc_ = ablaz.get('senza_contatto')
    if sc_ and sc_['bit_per_segno_in_piu'][0] is not None and sc_['bit_per_segno_in_piu'][1] is not None:
        LM['contatto'] = 'il contatto serve (senza, piu bit)' if sc_['bit_per_segno_in_piu'][0] - 2 * sc_['bit_per_segno_in_piu'][1] > 0 else 'nessun guadagno misurabile dal contatto'
    LM['contro_le_reti'] = OrderedDict((n, 'sotto la rete' if x.get('sotto_la_rete') else 'entro 0,10 bit dalla rete' if x.get('entro_0_10') else 'oltre 0,10 bit dalla rete') for n, x in conf.items() if 'pieno_meno_rete' in x)
    out['letture_modello'] = LM
    # ---- 4. diagnosi: dove spende i bit
    dg = OrderedDict()
    for v in ('pieno', 'senza_copia', 'solo_lessico'):
        xs = [C['stima|%s|%d' % (v, k)].get('diagnosi') for k in range(PIEGHE) if 'stima|%s|%d' % (v, k) in C]
        xs = [x for x in xs if x]
        if xs:
            cat = [k for k in xs[0] if k != 'glifi']
            tot = sum(sum(x[c][0] for c in cat) for x in xs)
            dg[v] = OrderedDict((c, OrderedDict(bit_totali=sum(x[c][0] for x in xs), parole=sum(x[c][1] for x in xs), quota_dei_bit=sum(x[c][0] for x in xs) / tot,
                                                bit_per_parola=sum(x[c][0] for x in xs) / max(sum(x[c][1] for x in xs), 1))) for c in cat)
    out['diagnosi'] = dg
    # ---- 5. libri: giudici, struttura, contro v21
    out.update(analisi_libri(C))
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('stima', 'bigramma', 'boot', 'ctrl', 'libro', 'K', 'M', 'D'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 2), massimo=round(max(s) / 60, 2), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def analisi_libri(C):
    out = OrderedDict()
    c_ctx = I7.contesto_A()
    n_pag = len(c_ctx['ids'])
    ctr = OrderedDict()
    pos = [C['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in C]
    caso = C.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=mes(pos)[0], soglia=POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=NEG_BANDA,
                                        riuscito=bool(caso) and all(NEG_BANDA[0] <= caso[k] <= NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    profs = []
    for f in range(PIEGHE):
        p = os.path.join(MISURE27, 'K_f%d.pkl' % f)
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
        ctr['K_vede_v21'] = OrderedDict(AUC=mes(v21K)[0], soglia=K_VEDE_V21, riuscito=bool(v21K) and statistics.mean(v21K) >= K_VEDE_V21)
    ok_paper = ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito']
    ok_K = bool(prof) and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito'] and ctr['K_vede_v21']['riuscito']
    out['controlli_giudici'] = ctr
    # giudici per versione
    lib = OrderedDict((v, [C['libro|%s|%d' % (v, i)] for i in range(1, n_libri_di(v) + 1) if 'libro|%s|%d' % (v, i) in C]) for v in VAR_LIBRI27)
    rif = OrderedDict((p, [C['riflibro|%d|%d' % (p, i)] for i in range(1, N_RIF + 1) if 'riflibro|%d|%d' % (p, i) in C]) for p in RIF_PASSI)
    val, giud = OrderedDict(), OrderedDict()
    for v, rs in list(lib.items()) + [('M%d' % p, r) for p, r in rif.items()]:
        if not rs:
            continue
        kk = lambda r: ('%s:%d' % (v, r['i']))
        x = OrderedDict(e231=mes([r['AUC_e231'] for r in rs]), e266=mes([r['AUC_e266'] for r in rs]), K=mes([aucK.get(kk(r)) for r in rs]), A=mes([r.get('AUC_A') for r in rs]))
        giud[v] = OrderedDict(libri=len(rs), **x)
        val[v] = x
    I07 = None
    v21 = OrderedDict(libri=len(CHIAVI_V21), e231=(I7.V21['AUC_e231'][0], I7.V21['AUC_e231'][1]), e266=(I7.V21['AUC_e266'][0], I7.V21['AUC_e266'][1]),
                      K=mes([aucK[n] for n in aucK if n.startswith('V21:')]))
    out['giudici'] = OrderedDict(versioni=giud, v21=v21)
    # copia a memoria
    rif_copia = I7.copia_riferimenti()
    nat = I7.quote(rif_copia['naturale'])
    rep_nat = MS.ripetizioni_interne(OrderedDict((p, [x['parole'] for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items()))
    k4, ks, kp = 'righe uguali a una precedente nella pagina (>= 4 parole)', 'righe uguali alla riga sopra (>= 2 parole)', 'parole uguali alla parola prima'
    nat4 = rep_nat[k4][0] / rep_nat[k4][1] if rep_nat[k4][1] else 0.0
    natp = rep_nat[kp][0] / rep_nat[kp][1] if rep_nat[kp][1] else 0.0
    cop, lett_copia = OrderedDict(), OrderedDict()
    for v, rs in lib.items():
        if not rs:
            continue
        qs = [I7.quote(r['copia']) for r in rs]
        cop[v] = OrderedDict((k, mes([q[k] for q in qs])) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))
        rip = OrderedDict((k, mes([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else None for r in rs])) for k in rep_nat)
        m5, mr = cop[v]['5-grammi'][0], cop[v]['righe intere'][0]
        l5 = 'nessuna copia rilevante' if m5 is not None and m5 <= I20.COPIA_5GRAMMI[0] else 'copia' if m5 is not None and m5 > I20.COPIA_5GRAMMI[1] else 'zona grigia'
        lr = 'nessuna copia rilevante' if mr is not None and mr <= I20.COPIA_RIGHE[0] else 'copia' if mr is not None and mr > I20.COPIA_RIGHE[1] else 'zona grigia'
        r4, rsopra, rpp = rip[k4][0], rip[ks][0], rip[kp][0]
        avvita = bool((r4 is not None and r4 > I20.AVVITA_MIN and r4 > I20.AVVITA_VOLTE * max(nat4, 1e-9)) or (rsopra is not None and rsopra > I20.RIGA_SOPRA_MAX))
        lett_copia[v] = OrderedDict([('5-grammi', l5), ('righe', lr), ('copia', 'copia' in (l5, lr)), ('zona_grigia', 'zona grigia' in (l5, lr)), ('si_avvita', avvita),
                                     ('parola_prima_alta', bool(rpp is not None and natp and rpp > I20.PAROLA_PRIMA_VOLTE * natp))])
    out['copia'] = OrderedDict(versioni=cop, naturale=nat, letture=lett_copia)
    # struttura
    M = {k[2:]: v for k, v in C.items() if k.startswith('M|')}
    Dj = [C['D|%d' % f] for f in range(PIEGHE) if 'D|%d' % f in C]
    struttura, vero = OrderedDict(), OrderedDict()
    if 'vere' in M and len(Dj) == PIEGHE:
        Mv = MS.copia_netta_lambda(M['vere'], con_intervallo=True)
        b = M['vere']['bordi']
        vero = OrderedDict(copia_netta=Mv['copia_netta'], lam=Mv['lam'], contatto=Mv['contatto'], D=MS.D_da_pieghe([x['D']['vere'] for x in Dj]), G9=M['vere'].get('G9'),
                           bordi_inizio=statistics.mean(b['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung')), bordi_fine=statistics.mean(b['fine_%s' % f] for f in ('primo', 'ultimo', 'lung')),
                           parole_nuove=nat['parole nuove'])
        fv = [x['forma']['vere'] for x in Dj]
        vero['costo_forma'] = sum(x[0] for x in fv) / max(sum(x[1] for x in fv), 1)
        vero['intervalli'] = OrderedDict(copia_netta=Mv['copia_netta_ic'], lam=Mv['lam_ic'], bordi=M['vere'].get('bordi_ic'))
        per_set = OrderedDict()
        for nome, r in M.items():
            if nome == 'vere':
                continue
            s = nome.split(':')[0]
            x = MS.copia_netta_lambda(r)
            x['D'] = MS.D_da_pieghe([d['D'][nome] for d in Dj]) if all(nome in d['D'] for d in Dj) else None
            x['G9'] = r.get('G9')
            x['bordi_inizio'] = statistics.mean(r['bordi']['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung'))
            x['bordi_fine'] = statistics.mean(r['bordi']['fine_%s' % f] for f in ('primo', 'ultimo', 'lung'))
            fm = [d['forma'][nome] for d in Dj if nome in d['forma']]
            x['parole_nuove'] = sum(y[2] for y in fm) / max(sum(y[3] for y in fm), 1) if fm else None
            x['costo_forma'] = sum(y[0] for y in fm) / max(sum(y[1] for y in fm), 1) if fm else None
            per_set.setdefault(s, []).append(x)
        for s, xs in per_set.items():
            struttura[s] = OrderedDict((m_, mes([x[m_] for x in xs])) for m_ in MISURE_STR)
            struttura[s]['libri'] = len(xs)
            if s in val:
                for m_ in MISURE_STR:
                    val[s][m_] = struttura[s][m_]
    out['vero'] = vero
    out['struttura'] = struttura
    # letture
    letture = OrderedDict()
    letture['validita'] = OrderedDict(paper=ok_paper, K=ok_K)
    L1 = OrderedDict()
    for v in val:
        if v.startswith('M'):
            continue
        cl = I16.classe_giudici({j: val[v][j] for j in ('e231', 'e266', 'K')}, v21)
        esito = I16.esito_v21(cl)
        if not (ok_paper and ok_K):
            esito = 'lettura non valida (controllo dei giudici fallito)'
        else:
            lc = lett_copia.get(v)
            if lc and lc['copia']:
                esito += ' ma NON VALE: copia a memoria sopra la soglia'
            elif lc and (lc['zona_grigia'] or lc['si_avvita']):
                esito += ' (con riserva: copia in zona grigia o scrittura che si avvita)'
        L1[v] = OrderedDict(esito=esito, giudici=cl)
    letture['L_contro_v21'] = L1
    L3 = OrderedDict()
    for v in list(val) :
        if not vero:
            break
        quali = OrderedDict()
        for m_ in ('copia_netta', 'lam', 'contatto', 'D'):
            x = val[v].get(m_)
            quali[m_] = I20.al_vero(x, vero.get(m_)) if x else None
        eco = all(quali[m_] for m_ in ('copia_netta', 'lam') if quali[m_] is not None) and all(quali[m_] is not None for m_ in ('copia_netta', 'lam'))
        legame = all(quali[m_] for m_ in ('contatto', 'D') if quali[m_] is not None) and all(quali[m_] is not None for m_ in ('contatto', 'D'))
        L3[v] = OrderedDict(al_vero=quali, eco_al_vero=bool(eco), legame_al_vero=bool(legame), tutti_e_quattro=bool(eco and legame))
    letture['L_eco_e_legame'] = L3
    letture['tutti_e_quattro'] = [v for v, x in L3.items() if x['tutti_e_quattro']]
    irr = OrderedDict()
    for m_ in MISURE_STR:
        v_ = vero.get(m_)
        if v_ is None:
            continue
        fl = OrderedDict((v, I20.al_vero(val[v].get(m_), v_) if val[v].get(m_) else None) for v in val if not v.startswith('M'))
        irr[m_] = OrderedDict(vero=v_, valori=OrderedDict((v, val[v][m_][0] if val[v].get(m_) else None) for v in val), al_vero=fl,
                              nessuna_versione_al_vero=not any(f for f in fl.values() if f is not None))
    letture['non_spiega'] = irr
    letture['non_spiega_elenco'] = [m_ for m_, x in irr.items() if x['nessuna_versione_al_vero']]
    out['letture_libri'] = letture
    return out


def mf(x, d=3):
    if x is None:
        return '—'
    if isinstance(x, (tuple, list)):
        return '%s ± %s' % (nu(x[0], d), nu(x[1], d)) if x[0] is not None else '—'
    return nu(x, d)


def ic_txt(x, d=3):
    return '—' if not x else '[%s; %s]' % (nu(x[0], d), nu(x[1], d))


def scrivi_md(o):
    md = ['# IA27 (ia27) — Il modello a sorgenti latenti', '', 'Preregistrazione: `preregistrazioni/ia27.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    md += ['## Bit per segno fuori piega (media ± errore sulle 5 pieghe)', '', '| versione | fuori (bit/segno) | fuori (bit/parola) | validazione (bit/segno) | EM: passi, verosimiglianza sale |', '|---|---|---|---|---|']
    for v, x in o['bit'].items():
        md.append('| %s | %s | %s | %s | %s |' % (v, mf(x['fuori_bps']), mf(x['fuori_bpp'], 2), mf(x['validazione_bps']), '%s, %s' % (nu(x['iterazioni'], 1), nu(x['ll_non_decresce'])) if 'iterazioni' in x else '—'))
    md += ['', '### Contro le reti (stesse pieghe: differenza per piega, modello pieno meno rete)', '', '| rete | bit/segno fuori | pieno - rete | entro 0,10 | sotto la rete |', '|---|---|---|---|---|']
    for n, x in o['contro_le_reti'].items():
        md.append('| %s | %s | %s | %s | %s |' % (n, mf(x['media']), mf(x.get('pieno_meno_rete')), nu(x.get('entro_0_10')), nu(x.get('sotto_la_rete'))))
    md += ['', '### Ablazioni (versione meno pieno, stesse pieghe)', '', '| versione | bit/segno in piu\' | bit/parola in piu\' |', '|---|---|---|']
    for n, x in o['ablazioni'].items():
        md.append('| %s | %s | %s |' % (n, mf(x['bit_per_segno_in_piu']), mf(x['bit_per_parola_in_piu'])))
    q = o['quote']
    md += ['', '## Quote delle sorgenti (stima sul testo intero; intervalli al 95% sui ricampionamenti delle pagine)', '']
    if 'stima' in q:
        s = q['stima']
        bi = q.get('boot_pieno')
        md.append('| sorgente | quota (tutte le lingue) | intervallo | A | B |')
        md.append('|---|---|---|---|---|')
        for i, (k, nm) in enumerate(SM.NOMI_SORGENTI.items()):
            md.append('| %s %s | %s | %s | %s | %s |' % (k, nm, nu(s['pooled'][i], 4), ic_txt(bi['quota'][i], 4) if bi else '—', nu(s['per_lingua']['A'][i], 4), nu(s['per_lingua']['B'][i], 4)))
        if bi:
            md.append('\nR + P (ricopiatura): intervallo %s. Ritocchi di R (uguale, cambia, aggiunge, toglie): stima %s; intervalli %s.' % (ic_txt(bi['quota_copia'], 4), ', '.join(nu(x, 3) for x in s['rho']['R']),
                                                                                                                   ' '.join(ic_txt(x, 3) for x in bi['rho_R'])))
        md.append('\nNucleo di R (quota delle scelte di ricopiatura per classe di distanza):')
        for k in range(SM.KR):
            md.append('- %s: %s%s' % (SM.etichetta_classe_R(k), nu(s['massa_R'][k], 3), ' %s' % ic_txt(bi['massa_R'][k], 3) if bi else ''))
        md.append('\nNucleo di P: ' + '; '.join('%s %s' % (SM.ETICHETTE_P[k], nu(s['massa_P'][k], 3)) for k in range(SM.KP)) + '.')
        md.append('\nInformazione del contatto (bit), stima sul testo intero: %s. L\'intervallo dei ricampionamenti (%s) e\' spostato in alto dalle pagine ripetute e non si legge: il contatto si legge dai bit in piu\' della versione senza contatto.' % (nu(s['info_contatto'], 4), ic_txt(bi['info_contatto'], 4) if bi else '—'))
        if 'senza_S_meno_pieno_copia' in q:
            x = q['senza_S_meno_pieno_copia']
            md.append('\nCon o senza la sorgente di sezione S: la quota R+P cambia di %s %s (stesse estrazioni; %d).' % (nu(x['media'], 4), ic_txt(x['intervallo'], 4), x['n']))
    if 'frequenza' in q:
        f_ = q['frequenza']
        md.append("\nVersione con_frequenza: peso della classe di frequenza della parola ricopiata (20 piu frequenti, fino alla 200-esima, altre), stima sul testo intero: R %s, P %s; rapporto rare/frequenti di R nelle 5 pieghe e nel testo intero: %s." % (
            ' '.join(nu(x, 2) for x in f_['phiR'][-1]), ' '.join(nu(x, 2) for x in f_['phiP'][-1]), ' '.join(nu(x, 2) for x in f_['rapporto_R'])))
    if 'stima' in q:
        s = q['stima']
        bi = q.get('boot_pieno')
        if bi:
            md.append("Rapporto fra il peso di una parola vicina (riga in corso, 1-3 parole prima) e di una lontana (riga sopra, 13 parole o piu): %s." % ic_txt(bi['rapporto_vicino_lontano'], 2))
    LM = o['letture_modello']
    md += ['', '## Letture del modello', '']
    for k_, v_ in LM.items():
        md.append('- %s: %s' % (k_, ', '.join('%s %s' % kv for kv in v_.items()) if isinstance(v_, dict) else v_))
    c = o['controlli_modello']
    md += ['', '## Controlli del modello', '']
    for forza, x in c['positivo'].items():
        md.append('- Positivo, forza %s (R %s, P %s veri): R stimata %s, P stimata %s; ritrovato in %d semi su %d (soglia %d): %s. Per criterio: %s. Guadagno di copia %s bit per parola.' % (
            forza, nu(x['vero_R'], 3), nu(x['vero_P'], 3), ' '.join(nu(v, 4) for v in x['quota_R']), ' '.join(nu(v, 4) for v in x['quota_P']), x['tutto_ritrovato'], x['semi'], x['soglia_semi'], nu(x['riuscito']),
            ', '.join('%s %d' % kv for kv in x['per_criterio'].items()), ' '.join(nu(v, 3) for v in x['guadagno'])))
    for modo, x in c['negativo'].items():
        md.append('- Negativo %s: quota R %s, quota P %s, guadagno di copia %s bit per parola%s.' % (modo, ' '.join(nu(v, 4) for v in x['quota_R']), ' '.join(nu(v, 4) for v in x['quota_P']), ' '.join(nu(v, 3) for v in x['guadagno']),
                                                                                                 '; riuscito: %s (soglie R %s, P %s, guadagno %s)' % (nu(x['riuscito']), NEG_R, NEG_P, NEG_GAIN) if 'riuscito' in x else ' (descrittivo)'))
    if 'autocoerenza' in c:
        x = c['autocoerenza']
        md.append('- Autocoerenza (il modello scrive, lo stesso metodo rilegge): quote vere R %s P %s; sul testo scritto R %s P %s; guadagno di copia sul vero %s e sullo scritto %s bit per parola (rapporto %s, soglia %s) → %s.' % (
            nu(x['quote_vero'][3], 4), nu(x['quote_vero'][4], 4), ' '.join(nu(q[3], 4) for q in x['quote_scritto']), ' '.join(nu(q[4], 4) for q in x['quote_scritto']), nu(x['guadagno_vero'], 3),
            ' '.join(nu(v, 3) for v in x['guadagno_scritto']), ' '.join(nu(v, 2) for v in x['rapporto']), AUTO_RAPPORTO, nu(x['riuscito'])))
    if 'latino' in c:
        x = c['latino']
        md.append('- Latino nella disposizione: quota R %s, P %s, guadagno di copia %s bit per parola, ritocchi di R %s → %s.' % (nu(x['quota_R'], 4), nu(x['quota_P'], 4), nu(x['guadagno'], 3), ', '.join(nu(v, 3) for v in x['rho_R']), nu(x['riuscito'])))
    md += ['', '## Dove spende i bit (fuori piega, tutte le pieghe)', '']
    for v, d in o['diagnosi'].items():
        md.append('- %s: ' % v + '; '.join('%s: %s%% dei bit (%s bit per parola, %d parole)' % (k, nu(100 * x['quota_dei_bit'], 1), nu(x['bit_per_parola'], 2), x['parole']) for k, x in d.items()) + '.')
    cg = o['controlli_giudici']
    md += ['', '## Controlli dei giudici', '']
    md.append('- Giudici del paper, positivo: AUC %s → %s. Negativo: %s e %s → %s.' % (nu(cg['paper_positivo']['AUC']), nu(cg['paper_positivo']['riuscito']), nu(cg['paper_negativo']['AUC_e231']), nu(cg['paper_negativo']['AUC_e266']), nu(cg['paper_negativo']['riuscito'])))
    if 'K_positivo' in cg:
        md.append('- K: positivo %s → %s; negativo %s → %s; vede il v21 %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in cg['K_positivo']['AUC'].items()), nu(cg['K_positivo']['riuscito']), nu(cg['K_negativo']['AUC']),
                                                                               nu(cg['K_negativo']['riuscito']), nu(cg['K_vede_v21']['AUC']), nu(cg['K_vede_v21']['riuscito'])))
    g = o['giudici']
    md += ['', '## Libri scritti dal modello: giudici (AUC, piu\' basso = piu\' vicino al vero)', '', '| libri | n | e231 | e266 | K | A (riportato) |', '|---|---|---|---|---|---|']
    for nm, x in g['versioni'].items():
        md.append('| %s | %d | %s | %s | %s | %s |' % (nm, x['libri'], mf(x['e231']), mf(x['e266']), mf(x['K']), mf(x['A'])))
    md.append('| v21 | %d | %s (paper) | %s (paper) | %s | — |' % (g['v21']['libri'], mf(g['v21']['e231']), mf(g['v21']['e266']), mf(g['v21']['K'])))
    v = o['vero']
    md += ['', '## Struttura (media ± errore sui libri)', '', '| testo | ' + ' | '.join(MISURE_STR.values()) + ' |', '|' + '---|' * (len(MISURE_STR) + 1)]
    if v:
        md.append('| **vero** | ' + ' | '.join(nu(v.get(m_), 4) for m_ in MISURE_STR) + ' |')
        for nm, x in o['struttura'].items():
            md.append('| %s (%d libri) | ' % (nm, x['libri']) + ' | '.join(mf(x[m_], 4) for m_ in MISURE_STR) + ' |')
    L = o['letture_libri']
    md += ['', '## Letture preregistrate', '', '- Validita\' dei giudici: paper %s, K %s.' % (nu(L['validita']['paper']), nu(L['validita']['K']))]
    for nm, x in L['L_contro_v21'].items():
        md.append('  - %s contro il v21: %s (%s).' % (nm, x['esito'], '; '.join('%s %s' % (j, y['lettura']) for j, y in x['giudici'].items())))
    md.append('- **Eco e legame insieme (copia netta, Λ, contatto, D tutti "al vero"):** ' + (', '.join(L['tutti_e_quattro']) or 'nessuna versione') + '.')
    for nm, x in L['L_eco_e_legame'].items():
        md.append('  - %s: eco al vero %s, legame al vero %s (%s).' % (nm, nu(x['eco_al_vero']), nu(x['legame_al_vero']), ', '.join('%s %s' % (k, nu(b)) for k, b in x['al_vero'].items())))
    md.append('- **Che cosa nessuna versione porta al vero:** ' + (', '.join(MISURE_STR[m_] for m_ in L['non_spiega_elenco']) or 'nessuna') + '.')
    cp = o['copia']
    md += ['', '## Copia a memoria (soglie severe di ia20)', '', '| | 5-grammi | 3-grammi | righe intere | parole nuove |', '|---|---|---|---|---|']
    for nm, q_ in cp['versioni'].items():
        md.append('| %s | %s |' % (nm, ' | '.join(mf(q_[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    md.append('| naturale | %s |' % ' | '.join(nu(cp['naturale'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    for nm, x in cp['letture'].items():
        md.append('- %s: 5-grammi → %s, righe → %s; si avvita: %s; parola uguale alla prima alta: %s.' % (nm, x['5-grammi'], x['righe'], nu(x['si_avvita']), nu(x['parola_prima_alta'])))
    md += ['', '## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def lavori_fase(fase):
    if fase == 'A':
        mancanti = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
        stime = [('stima', v, k) for v in VARIANTI27 for k in list(range(PIEGHE)) + ['tutto']]
        return mancanti + stime + [('bigramma', k) for k in range(PIEGHE)]
    if fase == 'Q':
        pos = [('ctrl', 'pos', f, s) for f in FORZE for s in range(1, SEMI_CTRL27 + 1)]
        neg = [('ctrl', 'neg', m, s) for m in ('fra_pagine', 'dentro_pagina', 'righe_fra_pagine') for s in range(1, 4 if not PICCOLO else 2)]
        return pos + neg + [('ctrl', 'auto', s) for s in range(1, 3 if not PICCOLO else 2)] + [('ctrl', 'latino', 0)]
    if fase == 'B':
        n = int(math.ceil(BOOT27 / float(CHUNK_BOOT)))
        return [('boot', v, c) for v in VARIANTI_BOOT for c in range(n)]
    if fase == 'C':
        rif = [('riflibro', p, i) for p in RIF_PASSI for i in range(1, N_RIF + 1) if usa_rif() and os.path.exists(percorso_rif(p, i))]
        return rif + [('libro', v, i) for v in VAR_LIBRI27 for i in range(1, n_libri_di(v) + 1)]
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
    for d in (MOD27, LIBRI27, MISURE27):
        os.makedirs(d, exist_ok=True)
    pagine, bordi, voc = dati()
    print('libro (%s): %d pagine, %d parole, %d glifi, bordi %s; versioni %s; libri %s; PICCOLO %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(pagine), sum(p.n_parole() for p in pagine), voc.G, bordi, VARIANTI27, VAR_LIBRI27, PICCOLO), flush=True)
    percorso = os.path.join(USCITA, 'ia27_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AQBCDS')
    for fase in 'AQBCD':
        if fase in fasi:
            lavori = lavori_fase(fase)
            if fase == 'A' and 'Q' in fasi:        # i controlli girano insieme alle stime (stesso gruppo di processi)
                lavori = lavori_fase('Q') + lavori
            if fase == 'Q' and 'A' in fasi:
                continue
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        print('Eco e legame tutti al vero: %s' % (', '.join(o['letture_libri']['tutti_e_quattro']) or 'nessuna versione'), flush=True)


if __name__ == '__main__':
    main()
