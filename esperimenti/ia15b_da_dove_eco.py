# -*- coding: utf-8 -*-
"""Esperimento IA15b (ia15b): da dove viene l'"eco" della pagina, seconda versione (nuovo esperimento preregistrato DOPO aver visto i
numeri descrittivi di ia15). Argomento (una pagina che parla di una cosa ripete le sue parole) o tecnica di scrittura (copiare e
ritoccare parole scritte poco prima)?

Perche' una seconda versione: in ia15 i controlli costruiti sul lessico del Voynich non hanno retto (generatori con troppo poca eco, misura
del paragrafo instabile, un solo "controllo tecnica" che teneva insieme profilo, varianti e paragrafo), quindi quasi tutte le letture sono
uscite "non leggibili". Preregistrazione: preregistrazioni/ia15b.md. Il codice di ia15 (ia15_da_dove_eco.py, eco_testi.py, eco_modelli.py)
si importa e non si modifica; le aggiunte stanno qui e in eco_modelli_b.py.

Che cosa cambia rispetto a ia15 (in parole semplici)
1. Controlli separati per lettura: profilo, varianti, paragrafo, modifiche, pagine vicine e sintesi valgono ciascuna se passano i SUOI
   controlli, non tutti.
2. Taratura dei generatori di controllo: la forza di ogni generatore (quota di parole del tema, probabilita' di copiare) si sceglie, con
   un programma, perche' l'eco vicina del generatore sul lessico del Voynich sia della stessa grandezza di quella del Voynich (la sola
   quantita' di eco; mai le misure di lettura). Livelli: V (come il Voynich), M (meta'), D (un quarto: descrittivo).
3. Varianti al netto del lessico: la quota di varianti si legge solo sulla PARTE LOCALE dell'eco (eco vicina meno eco lontana, le parole
   uguali e le varianti ciascuna), cioe' la parte che cala con la distanza; la parte che non cala (il lessico e il tema della pagina)
   si toglie. Se l'eco non cala con la distanza la lettura e' "nessuna parte locale". Nuovo controllo: "argomento di famiglie di parole".
   Descrittivo: la quota grezza di ia15 contro il testo rimescolato dentro la pagina e contro il v21.
4. Paragrafo: Q si legge solo se l'eco "dentro il paragrafo" a 2-3 righe ha limite basso > 0 (altrimenti il rapporto e' instabile).
5. Direzione: il controllo negativo chiede "ne' inizio ne' fine" (modifiche a caso nella parola).
6. Sintesi anche "senza il paragrafo", se solo le prove del paragrafo non reggono.

Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia15b_da_dove_eco.json e .md, risultati/ia15b_taratura.json,
e, una riga per testo, risultati/ia15b_corse.jsonl.

Variabili (oltre a quelle di ia01, ia09 e ia15: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, RIGHE_PAGINA_EN, CHIAVI, USCITA, LIBRI, BOOT, GENERATORI,
RIM_TESTO, SCALA_COPIA, FILTRO, RIPRENDI, PROCESSI, FASI, NRIF, SPOSTAMENTI, MIN_PAGINE_GRUPPO): FASI (taratura, conteggi, analisi;
predefinito tutte e tre) e le NUOVE di ia15b: ECO_FRAZIONI (livelli della taratura, es. "M=0.5,D=0.25"), ECO_BERSAGLIO (eco vicina da
raggiungere; predefinito: quella del testo `vere`, calcolata nella corsa), TARA_TOL (tolleranza relativa, 0.08), TARA_PASSI (valutazioni
massime per livello, 8), FAMIGLIA_PHI (quota di parole del tema sostituite da una parente nel generatore "famiglie", 0.6), LOC_MIN (parte
locale minima dell'eco vicina, 0.15), N_FAMIGLIE (istanze del generatore "famiglie", 2). LIVELLI_ARG e LIVELLI_TEC di ia15 non servono.
"""
import json, math, os, random, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia15_da_dove_eco as I15  # noqa: E402  (non si modifica; qui si importa)
import eco_modelli_b as EMB  # noqa: E402

G, I9, TT, SM, EM, ET = I15.G, I15.I9, I15.TT, I15.SM, I15.EM, I15.ET
V, pesi_bootstrap, stima, _ic = I15.V, I15.pesi_bootstrap, I15.stima, I15._ic
Dati, q_par = I15.Dati, I15.q_par

NOME = 'ia15b_da_dove_eco'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NRIF, SPOSTAMENTI, MIN_PAGINE_GRUPPO, MIN_ETEROG = I15.NRIF, I15.SPOSTAMENTI, I15.MIN_PAGINE_GRUPPO, I15.MIN_ETEROG
GENERATORI, RIM_TESTO, SCALA_COPIA, LIBRI_V21 = I15.GENERATORI, I15.RIM_TESTO, I15.SCALA_COPIA, I15.LIBRI_V21
seme_di = G.seme_di
TARA_TOL = float(os.environ.get('TARA_TOL', 0.08))
TARA_PASSI = int(os.environ.get('TARA_PASSI', 8))
FAMIGLIA_PHI = float(os.environ.get('FAMIGLIA_PHI', 0.6))
LOC_MIN = float(os.environ.get('LOC_MIN', 0.15))        # la parte locale dell'eco vicina deve essere almeno questa quota dell'eco vicina
N_FAMIGLIE = int(os.environ.get('N_FAMIGLIE', 2))
POTENZA_MIN = 0.70                                       # un controllo vale solo se il suo testo ha almeno il 70% dell'eco vicina bersaglio


def frazioni_eco():
    d = dict(V=1.0, M=0.5, D=0.25)
    for x in os.environ.get('ECO_FRAZIONI', '').split(','):
        if '=' in x:
            k, v = x.split('=')
            d[k.strip()] = float(v)
    return d


FRAZIONI_ECO = frazioni_eco()

# ---------------------------------------------------------------- i generatori di controllo (nome -> come si costruiscono)
# famiglia: argP (un tema per pagina), argR (per paragrafo), argS (un tema che scorre), argF (un tema per pagina fatto di famiglie di
# parole: la parola del tema esce con una parente), tecM (copia e ritocco, modo misto), tecP (copia solo dal paragrafo in corso).
# livello: V (eco vicina come quella del Voynich), M (meta'), D (un quarto). Il nome: famiglia + (m|d) + numero di istanza.
FAMIGLIE = OrderedDict([('argP', 'arg'), ('argR', 'arg'), ('argS', 'arg'), ('argF', 'arg'), ('tecM', 'tec'), ('tecP', 'tec')])
LIVELLI_FAM = OrderedDict([('argP', ['V', 'M', 'D']), ('argR', ['V', 'M']), ('argS', ['V']), ('argF', ['V', 'M']),
                           ('tecM', ['V', 'M', 'D']), ('tecP', ['V', 'M', 'D'])])
SUFFISSO = dict(V='', M='m', D='d')
PARTENZA = dict(argP=0.20, argR=0.30, argS=0.30, argF=0.30, tecM=0.10, tecP=0.10)      # livello iniziale della ricerca
TETTO = dict(arg=0.98, tec=0.95)
ESPONENTE0 = dict(arg=1.7, tec=1.0)                                                       # pendenza iniziale log(eco) / log(livello)


def nome_gen(fam, liv, i):
    return '%s%s%d' % (fam, SUFFISSO[liv], i)


def registro_generatori():
    R = OrderedDict()
    G_ = GENERATORI
    for fam, n in (('argP', G_), ('argR', G_), ('argS', 1), ('argF', N_FAMIGLIE), ('tecM', G_), ('tecP', 1)):
        for i in range(1, n + 1):
            R[nome_gen(fam, 'V', i)] = dict(fam=fam, liv='V', modo='misto')
    R['tecCoda1'] = dict(fam='tecM', liv='V', modo='fine')
    R['tecTesta1'] = dict(fam='tecM', liv='V', modo='inizio')
    for fam in ('argP', 'argR', 'argF', 'tecM', 'tecP'):
        R[nome_gen(fam, 'M', 1)] = dict(fam=fam, liv='M', modo='misto')
    for fam in ('argP', 'tecM', 'tecP'):
        R[nome_gen(fam, 'D', 1)] = dict(fam=fam, liv='D', modo='misto')
    return R


GEN_B = registro_generatori()
N_TEC = [nome_gen('tecM', 'V', i) for i in range(1, GENERATORI + 1)]
N_ARGP = [nome_gen('argP', 'V', i) for i in range(1, GENERATORI + 1)]
N_ARGR = [nome_gen('argR', 'V', i) for i in range(1, GENERATORI + 1)]
N_ARGF = [nome_gen('argF', 'V', i) for i in range(1, N_FAMIGLIE + 1)]


# ---------------------------------------------------------------- generare un testo di controllo

_BASE = {}


def base_gen():
    """Il lessico su cui si costruiscono i generatori (le pagine `vere`), con il grafo delle parole a una modifica e l'ordine delle pagine."""
    if not _BASE:
        base = I9.costruisci('vere')
        Cb = SM.Corpus(base['pagine'])
        Cb.prepara()
        meta = ET.meta_di(list(Cb.pag), prova=SOLO_CONTROLLI)
        _BASE.update(base=base, Cb=Cb, A=None, ordine=sorted(Cb.pag, key=lambda p: meta[p]['ord']))
    return _BASE


def genera_pagine(fam, modo, livello, nome_seme):
    """Le pagine di un generatore di controllo di famiglia `fam`, al livello numerico `livello`, col seme del nome `nome_seme`."""
    B = base_gen()
    Cb, seme = B['Cb'], seme_di('ia15b:gen:' + nome_seme)
    if fam == 'argF':
        if B['A'] is None:
            B['A'] = EM.grafo_vicini(Cb)
        return EMB.genera_argomento_famiglie(Cb, B['A'], seme, livello, FAMIGLIA_PHI)
    if FAMIGLIE[fam] == 'arg':
        unita = dict(argP='pagina', argR='paragrafo', argS='scorre')[fam]
        return EM.genera_argomento(Cb, seme, livello, unita, B['ordine'])
    return EM.genera_copia_eco(Cb, seme, livello, SCALA_COPIA, modo, fam == 'tecP')


# ---------------------------------------------------------------- la quantita' di eco (per la taratura) e la taratura

def eco_vicina_di(pagine, tipo=None):
    """La sola quantita' di eco, come in ia15: eco vicina (0-3 righe) e lontana (4 o piu'), parole alla riga 4 o piu', pesi comuni, riferimento
    della stessa sezione (stessi semi di ia15 per i riferimenti). Restituisce (vicina, lontana). Niente paragrafi, niente rimescolamenti."""
    C = SM.Corpus(pagine)
    C.prepara()
    A = EM.grafo_vicini(C)
    nomi = sorted(pagine)
    sez_prova = {p: tipo[p][0] for p in nomi} if (SOLO_CONTROLLI and tipo and all(p in tipo for p in nomi)) else None
    meta = ET.meta_di(nomi, sezioni_prova=sez_prova, prova=SOLO_CONTROLLI)
    nrighe = {p: len(C.pag[p].lstart) - 1 for p in nomi}
    rs, _ra = EM.scegli_riferimenti(nomi, meta, nrighe, seme_di('ia15:rif'), NRIF)
    arr = np.stack([EMB.conta_eco_rapida(C, A, C.pag[p], [C.pag[q] for q in rs[p]]) for p in nomi])
    ev, el, _h = I15.eco_comune(arr, np.ones((1, len(nomi))))
    return ev.p, el.p


def livello_successivo(coppie, bersaglio, tipo, lo, hi):
    """Il prossimo livello da provare, in scala logaritmica (eco contro livello): se ci sono due punti che chiudono il bersaglio (uno sotto, uno
    sopra) si interpola fra i piu' vicini; altrimenti si estrapola con la pendenza dei due punti piu' vicini (o quella iniziale se ce n'e' uno
    solo); con eco nulla si raddoppia."""
    pos = sorted([(l, e) for l, e in coppie if e > 0])
    if not pos:
        return min(hi, max(lo, 2 * max(l for l, _ in coppie)))
    sotto = [(l, e) for l, e in pos if e < bersaglio]
    sopra = [(l, e) for l, e in pos if e >= bersaglio]
    if sotto and sopra:
        (l1, e1), (l2, e2) = max(sotto, key=lambda le: le[1]), min(sopra, key=lambda le: le[1])
        if l2 != l1 and e2 != e1:
            b = max(0.3, min(4.0, math.log(e2 / e1) / math.log(l2 / l1)))
            return min(hi, max(lo, l1 * math.exp(math.log(bersaglio / e1) / b)))
    near = sorted(pos, key=lambda le: abs(math.log(le[1] / bersaglio)))
    l1, e1 = near[0]
    b = ESPONENTE0[tipo]
    if len(near) >= 2 and abs(math.log(near[1][0] / l1)) > 1e-9:
        b2 = math.log(near[1][1] / e1) / math.log(near[1][0] / l1)
        if b2 > 0.3:
            b = min(b2, 4.0)
    return min(hi, max(lo, l1 * math.exp(math.log(bersaglio / e1) / b)))


def tara_famiglia(arg):
    """Per una famiglia, i livelli numerici che danno l'eco vicina bersaglio (frazione del bersaglio per ogni livello V, M, D). Si valuta con il
    seme dell'istanza 1 di ogni livello (cosi' quel testo ha esattamente quell'eco)."""
    fam, bersaglio = arg
    tipo_fam = FAMIGLIE[fam]
    coppie, out = [], OrderedDict()
    for liv in LIVELLI_FAM[fam]:
        target = bersaglio * FRAZIONI_ECO[liv]
        nome1 = nome_gen(fam, liv, 1)
        modo = GEN_B[nome1]['modo']
        valutazioni, migliore, ok = [], None, False
        tutte = list(coppie)                                    # i punti dei livelli precedenti (stessa famiglia) aiutano la prima stima
        livello = None
        for it in range(TARA_PASSI):
            if livello is None:
                livello = livello_successivo(tutte, target, tipo_fam, 0.005, TETTO[tipo_fam]) if tutte else PARTENZA[fam]
            pagine = genera_pagine(fam, modo, livello, nome1)
            e, _ = eco_vicina_di(pagine)
            valutazioni.append([round(livello, 5), round(e, 6)])
            tutte.append((livello, e))
            coppie.append((livello, e))
            if migliore is None or abs(e - target) < abs(migliore[1] - target):
                migliore = (livello, e)
            if abs(e / target - 1) <= TARA_TOL:
                ok = True
                break
            nuovo = livello_successivo(tutte, target, tipo_fam, 0.005, TETTO[tipo_fam])
            if any(abs(nuovo - v[0]) < 1e-6 for v in valutazioni):
                break                                           # al tetto o fermo: il bersaglio non si raggiunge
            livello = nuovo
        out[liv] = OrderedDict(livello=round(float(migliore[0]), 5), eco_vicina=round(float(migliore[1]), 6), bersaglio=round(float(target), 6),
                               raggiunto=bool(ok), valutazioni=valutazioni)
    return fam, out


def percorso_taratura():
    return os.path.join(USCITA, 'ia15b_taratura.json')


def esegui_taratura(processi):
    """Fase 'taratura': l'eco vicina del testo `vere` (o ECO_BERSAGLIO) e, per ogni famiglia di controlli, i livelli che la riproducono."""
    inizio = time.time()
    if os.environ.get('ECO_BERSAGLIO'):
        bers, lon = float(os.environ['ECO_BERSAGLIO']), None
        da = 'ECO_BERSAGLIO'
    else:
        T = costruisci('vere')
        bers, lon = eco_vicina_di(T['pagine'], T.get('tipo'))
        da = 'eco vicina del testo vere'
    print('bersaglio: eco vicina %.5f (%s); lontana %s' % (bers, da, 'n.d.' if lon is None else '%.5f' % lon), flush=True)
    lavori_t = [(f, bers) for f in LIVELLI_FAM]
    risultati = OrderedDict()
    if processi <= 1:
        for a in lavori_t:
            fam, r = tara_famiglia(a)
            risultati[fam] = r
            print('taratura %s: %s (%.0f s)' % (fam, {k: (v['livello'], v['eco_vicina'], v['raggiunto']) for k, v in r.items()}, time.time() - inizio), flush=True)
    else:
        with get_context('spawn').Pool(min(processi, len(lavori_t))) as pool:
            for fam, r in pool.imap_unordered(tara_famiglia, lavori_t):
                risultati[fam] = r
                print('taratura %s: %s (%.0f s)' % (fam, {k: (v['livello'], v['eco_vicina'], v['raggiunto']) for k, v in r.items()}, time.time() - inizio), flush=True)
    out = OrderedDict(bersaglio=round(float(bers), 6), da=da, eco_lontana_vere=None if lon is None else round(float(lon), 6),
                      frazioni=FRAZIONI_ECO, tolleranza=TARA_TOL, passi_max=TARA_PASSI, famiglia_phi=FAMIGLIA_PHI, scala_copia=SCALA_COPIA,
                      famiglie=OrderedDict((f, risultati[f]) for f in LIVELLI_FAM if f in risultati), secondi=round(time.time() - inizio, 1))
    os.makedirs(USCITA, exist_ok=True)
    with open(percorso_taratura(), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return out


_TARA = {}


def taratura_letta():
    if not _TARA:
        p = percorso_taratura()
        if not os.path.exists(p):
            raise SystemExit('FERMO: manca %s (fase taratura)' % p)
        _TARA.update(json.load(open(p, encoding='utf-8')))
    return _TARA


# ---------------------------------------------------------------- i testi

_ORIG_COSTRUISCI = I15.costruisci
_TB = OrderedDict()


def nomi_testi():
    """Tutti i testi. 'X~t' = X con tutte le parole mescolate fra le pagine; 'X~p' = con le parole mescolate dentro ogni pagina."""
    base = ['vere'] + LIBRI_V21 + ([] if SOLO_CONTROLLI else ['ts1', 'ts2'])
    rif = ([] if SOLO_CONTROLLI else ['latino']) + ['inglese', 'italiano']
    nomi = base + rif + ['latGeom', 'ingGeom'] + list(GEN_B)
    rim_t = (['vere~t%d' % i for i in range(1, RIM_TESTO + 1)] +
             [x + '~t' for x in [LIBRI_V21[0]] + ([] if SOLO_CONTROLLI else ['ts1']) + [N_ARGP[0], N_TEC[0], N_ARGF[0]] + rif])
    rim_p = [x + '~p' for x in ['vere', LIBRI_V21[0]] + ([] if SOLO_CONTROLLI else ['ts1']) + [N_ARGP[0], N_TEC[0], N_ARGF[0]] + rif]
    return nomi + rim_t + rim_p


def costruisci(nome):
    """Il testo `nome`: dict(pagine, fold, tipo). Uguale in ogni processo (semi fissi). I generatori usano i livelli della taratura."""
    if nome in _TB:
        return _TB[nome]
    if '~' in nome:
        base, modo = nome.split('~')
        T = costruisci(base)
        f = TT.rimescola_testo if modo.startswith('t') else TT.rimescola_pagina
        t = dict(pagine=f(T['pagine'], seme_di('ia15b:rim:' + nome)), fold=T['fold'], tipo=T['tipo'])
    elif nome in GEN_B:
        g = GEN_B[nome]
        livello = taratura_letta()['famiglie'][g['fam']][g['liv']]['livello']
        B = base_gen()
        t = dict(pagine=genera_pagine(g['fam'], g['modo'], livello, nome), fold=B['base']['fold'], tipo=B['base']['tipo'])
    else:
        t = _ORIG_COSTRUISCI(nome)
    if len(_TB) > 4:
        _TB.clear()
    _TB[nome] = t
    return t


I15.costruisci = costruisci          # il lavoro di ia15 (`lavoro`) chiama `costruisci` per nome: qui usa quella di ia15b


def lavori(fasi):
    L = [('C', n) for n in nomi_testi()] if 'conteggi' in fasi else []
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


def esegui_lavoro(job):
    return I15.lavoro(job[1])


# ---------------------------------------------------------------- nuove misure (varianti al netto del lessico)

VIC, LON = I15.VIC, I15.LON
UGUALI, VARIANTI = [1], [2, 3, 4]


def eco_comune_colonne(arr, cols, W, sel=None):
    """Come `I15.eco_comune` (stessi pesi comuni per pagina) ma per le colonne `cols` di (n, uguali, vI, vF, vM): eco vicina ed eco lontana."""
    if sel is not None:
        arr, W = arr[sel], W[:, sel]
    n_v, n_l = arr[:, :, VIC, 0].sum(2), arr[:, :, LON, 0].sum(2)
    h_v, h_l = arr[:, :, VIC][..., cols].sum((2, 3)), arr[:, :, LON][..., cols].sum((2, 3))
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
    return V(p[0][0], b[0]), V(p[1][0], b[1])


def misure(d, W, sel=None):
    """Le misure di ia15 piu' la parte locale dell'eco: uguali e varianti, vicino meno lontano (stessi pesi comuni). QL = quota di varianti
    nella parte locale; loc_rel = parte locale / eco vicina (= 1 - H)."""
    r = I15.misure(d, W, sel)
    x = r['sez']
    exv, exl = eco_comune_colonne(d.A4, UGUALI, W, sel)
    evv, evl = eco_comune_colonne(d.A4, VARIANTI, W, sel)
    x['Ex_vic_c'], x['Ex_lon_c'], x['Ev_vic_c'], x['Ev_lon_c'] = exv, exl, evv, evl
    x['loc_x'], x['loc_v'] = exv - exl, evv - evl
    x['loc'] = x['loc_x'] + x['loc_v']
    x['QL'] = x['loc_v'].dividi(x['loc'])
    x['loc_rel'] = x['loc'].dividi(x['E_vic_c'])
    return r


# ---------------------------------------------------------------- letture (cambiate rispetto a ia15: varianti, paragrafo, sintesi)

lettura_eco, lettura_profilo, lettura_direzione, lettura_pagine = I15.lettura_eco, I15.lettura_profilo, I15.lettura_direzione, I15.lettura_pagine
QV_ALTE, QV_ALTE_IC, QV_BASSE, QV_BASSE_IC = I15.QV_ALTE, I15.QV_ALTE_IC, I15.QV_BASSE, I15.QV_BASSE_IC


def lettura_varianti(x):
    """Quota di varianti nella PARTE LOCALE dell'eco (varianti / (varianti + uguali), vicino meno lontano). Se la parte locale non e' almeno
    LOC_MIN dell'eco vicina, con limite basso > 0, l'eco non cala con la distanza: "nessuna parte locale" (la quota di varianti non si legge:
    sarebbe lessico e tema della pagina)."""
    if lettura_eco(x) != 'misurabile':
        return 'non leggibile'
    loc, rel = x['loc'], x['loc_rel']
    if not (loc.p > 0 and _ic(loc)[0] > 0 and rel.p >= LOC_MIN):
        return 'nessuna parte locale'
    q = x['QL']
    lo, hi = _ic(q)
    if not np.isfinite(q.p):
        return 'non leggibile'
    if q.p >= QV_ALTE and lo > QV_ALTE_IC:
        return 'alte'
    if q.p <= QV_BASSE and hi < QV_BASSE_IC:
        return 'basse'
    return 'medie'


def lettura_paragrafo(x, qnull):
    """Come ia15, con una condizione in piu': Q e' un rapporto con l'eco "dentro il paragrafo" a 2-3 righe al denominatore; se quell'eco non ha
    limite basso > 0 il rapporto e' instabile e la lettura e' "non leggibile"."""
    if lettura_eco(x) != 'misurabile':
        return 'non leggibile'
    if not (np.isfinite(x['e_dentro'].p) and _ic(x['e_dentro'])[0] > 0):
        return 'non leggibile'
    return I15.lettura_paragrafo(x, qnull)


def sintesi(profilo, varianti, paragrafo, pagine):
    """La regola di ia15 con le varianti sulla parte locale. In ordine: (1) profilo o varianti non leggibili: "non leggibile"; (2) il paragrafo
    conta: con varianti alte e profilo ripido "tecnica che riparte a ogni paragrafo", con varianti alte e profilo non ripido "mista", altrimenti
    "argomento di paragrafo"; (3) profilo ripido e varianti alte: "tecnica"; (4) varianti non alte (anche "nessuna parte locale") e profilo non
    ripido: "argomento di pagina" se il profilo e' piatto e le pagine vicine non sono "si", altrimenti "argomento che scorre"; (5) segni dei due
    lati: "mista"; (6) altrimenti "zona grigia"."""
    return I15.sintesi(profilo, varianti, paragrafo, pagine)


def tutte_le_letture(nome, m, rel, qnull):
    x = m['sez']
    pr, va, pa, pg = lettura_profilo(x), lettura_varianti(x), lettura_paragrafo(x, qnull), lettura_pagine(rel)
    return OrderedDict(eco=lettura_eco(x), profilo=pr, varianti=va, paragrafo=pa, direzione=lettura_direzione(x), pagine_vicine=pg,
                       sintesi=sintesi(pr, va, pa, pg), sintesi_senza_paragrafo=sintesi(pr, va, 'zona grigia', pg))


# ---------------------------------------------------------------- controlli (separati per lettura)

TUTTE = ['profilo', 'varianti', 'paragrafo', 'direzione', 'pagine_vicine', 'sintesi', 'sintesi_senza_paragrafo']
NEG_PAGINA = ['vere~p', N_TEC[0] + '~p', N_ARGP[0] + '~p', N_ARGF[0] + '~p']
NEG_FRA = ['vere~t%d' % i for i in range(1, RIM_TESTO + 1)] + [N_TEC[0] + '~t', N_ARGP[0] + '~t', N_ARGF[0] + '~t']
TEC_RIPARTE = [nome_gen('tecP', 'V', 1)]
ARG_SCORRE = [nome_gen('argS', 'V', 1)]


def _in(l, k, valori):
    return l[k] in valori


# (nome, testi, che cosa deve venire, condizione sulle letture, letture a cui serve, richiede potenza)
CONTROLLI = [
    ('negativo_rimescolato_fra_pagine', NEG_FRA, 'eco debole (nessuna ripetizione sopra il caso)', lambda l: l['eco'] == 'debole', TUTTE, False),
    ('negativo_nella_pagina_profilo', NEG_PAGINA, 'profilo piatto (l\'eco di pagina resta, perde la distanza)', lambda l: l['profilo'] == 'piatto', ['profilo'], False),
    ('negativo_nella_pagina_varianti', NEG_PAGINA, 'varianti non alte (nessuna parte locale da leggere)', lambda l: l['varianti'] != 'alte', ['varianti'], False),
    ('negativo_nella_pagina_paragrafo', NEG_PAGINA, 'il paragrafo non conta', lambda l: l['paragrafo'] != 'conta', ['paragrafo'], False),
    ('positivo_tecnica_profilo', N_TEC, 'profilo ripido', lambda l: l['profilo'] == 'ripido', ['profilo'], True),
    ('positivo_tecnica_varianti', N_TEC, 'varianti alte', lambda l: l['varianti'] == 'alte', ['varianti'], True),
    ('positivo_tecnica_paragrafo', N_TEC, 'il paragrafo non conta (zona grigia ammessa: la copia e\' per parole, non per paragrafi)', lambda l: l['paragrafo'] != 'conta', ['paragrafo'], True),
    ('positivo_argomento_pagina_profilo', N_ARGP, 'profilo piatto', lambda l: l['profilo'] == 'piatto', ['profilo'], True),
    ('positivo_argomento_pagina_varianti', N_ARGP, 'varianti basse o nessuna parte locale', lambda l: _in(l, 'varianti', ('basse', 'nessuna parte locale')), ['varianti'], True),
    ('positivo_argomento_pagina_paragrafo', N_ARGP, 'il paragrafo non conta', lambda l: l['paragrafo'] == 'non conta', ['paragrafo'], True),
    ('positivo_famiglie_profilo', N_ARGF, 'profilo piatto', lambda l: l['profilo'] == 'piatto', ['profilo'], True),
    ('positivo_famiglie_varianti', N_ARGF, 'varianti non alte (tante varianti nella pagina, nessuna copia: la parte locale non c\'e\')', lambda l: l['varianti'] != 'alte', ['varianti'], True),
    ('positivo_famiglie_paragrafo', N_ARGF, 'il paragrafo non conta', lambda l: l['paragrafo'] == 'non conta', ['paragrafo'], True),
    ('positivo_argomento_paragrafo_paragrafo', N_ARGR, 'il paragrafo conta', lambda l: l['paragrafo'] == 'conta', ['paragrafo'], True),
    ('positivo_argomento_paragrafo_varianti', N_ARGR, 'varianti basse (le parole del tema tornano uguali)', lambda l: l['varianti'] == 'basse', ['varianti'], True),
    ('positivo_tecnica_riparte_paragrafo', TEC_RIPARTE, 'il paragrafo conta', lambda l: l['paragrafo'] == 'conta', ['paragrafo'], True),
    ('positivo_tecnica_riparte_varianti', TEC_RIPARTE, 'varianti alte', lambda l: l['varianti'] == 'alte', ['varianti'], True),
    ('positivo_argomento_che_scorre_pagine', ARG_SCORRE, 'pagine vicine "si"', lambda l: l['pagine_vicine'] == 'si', ['pagine_vicine'], True),
    ('negativo_pagine_vicine', N_ARGP + N_ARGF + N_TEC, 'pagine vicine non "si" (temi e copie indipendenti da una pagina alla successiva)',
     lambda l: l['pagine_vicine'] != 'si', ['pagine_vicine'], True),
    ('positivo_direzione_fine', ['tecCoda1'], 'direzione "fine"', lambda l: l['direzione'] == 'fine', ['direzione'], True),
    ('positivo_direzione_inizio', ['tecTesta1'], 'direzione "inizio"', lambda l: l['direzione'] == 'inizio', ['direzione'], True),
    ('negativo_direzione', [N_TEC[0]], 'direzione ne\' "inizio" ne\' "fine" (modifiche a caso nella parola)',
     lambda l: l['direzione'] not in ('inizio', 'fine'), ['direzione'], True),
    ('sintesi_tecnica', N_TEC, 'sintesi "tecnica"', lambda l: l['sintesi'] == 'tecnica', ['sintesi'], True),
    ('sintesi_argomento_pagina', N_ARGP, 'sintesi "argomento di pagina"', lambda l: l['sintesi'] == 'argomento di pagina', ['sintesi'], True),
    ('sintesi_famiglie', N_ARGF, 'sintesi "argomento di pagina"', lambda l: l['sintesi'] == 'argomento di pagina', ['sintesi'], True),
    ('sintesi_argomento_paragrafo', N_ARGR, 'sintesi "argomento di paragrafo"', lambda l: l['sintesi'] == 'argomento di paragrafo', ['sintesi'], True),
    ('sintesi_tecnica_riparte', TEC_RIPARTE, 'sintesi "tecnica che riparte a ogni paragrafo"', lambda l: l['sintesi'] == 'tecnica che riparte a ogni paragrafo', ['sintesi'], True),
    ('sintesi_argomento_che_scorre', ARG_SCORRE, 'sintesi "argomento che scorre"', lambda l: l['sintesi'] == 'argomento che scorre', ['sintesi'], True),
    ('sintesi_senza_paragrafo_tecnica', N_TEC, 'sintesi senza il paragrafo "tecnica"', lambda l: l['sintesi_senza_paragrafo'] == 'tecnica', ['sintesi_senza_paragrafo'], True),
    ('sintesi_senza_paragrafo_argomento_pagina', N_ARGP + N_ARGF, 'sintesi senza il paragrafo "argomento di pagina"',
     lambda l: l['sintesi_senza_paragrafo'] == 'argomento di pagina', ['sintesi_senza_paragrafo'], True),
    ('sintesi_senza_paragrafo_argomento_che_scorre', ARG_SCORRE, 'sintesi senza il paragrafo "argomento che scorre"',
     lambda l: l['sintesi_senza_paragrafo'] == 'argomento che scorre', ['sintesi_senza_paragrafo'], True),
]
# la sintesi (con il paragrafo) richiede anche le letture di cui e' fatta; la sintesi senza il paragrafo, tutte tranne il paragrafo
DIPENDE = dict(sintesi=['profilo', 'varianti', 'paragrafo', 'pagine_vicine'], sintesi_senza_paragrafo=['profilo', 'varianti', 'pagine_vicine'])


def esegui_controlli(L, POT):
    """I controlli preregistrati. L = letture di ogni testo; POT = eco vicina / eco vicina bersaglio di ogni testo. Un controllo con generatori vale
    solo se ogni suo testo ha almeno POTENZA_MIN dell'eco bersaglio (altrimenti non ha forza)."""
    c = OrderedDict()
    for nome, testi, a_parole, cond, serve, serve_potenza in CONTROLLI:
        t = [n for n in testi if n in L]
        pot = [POT.get(n) for n in t]
        potente = (not serve_potenza) or (bool(t) and all(p is not None and p >= POTENZA_MIN for p in pot))
        sup = bool(t and all(cond(L[n]) for n in t))
        c[nome] = OrderedDict(testi=t, condizione=a_parole, serve_a=serve, esiti=OrderedDict((n, L[n]) for n in t),
                              potenza=OrderedDict((n, None if POT.get(n) is None else round(float(POT[n]), 3)) for n in t),
                              potenza_sufficiente=bool(potente), superato=bool(sup and potente))
    valida = OrderedDict()
    for k in TUTTE:
        cs = [v for v in c.values() if k in v['serve_a']]
        valida[k] = bool(cs and all(v['superato'] for v in cs))
    for k, dip in DIPENDE.items():
        valida[k] = bool(valida[k] and all(valida[j] for j in dip))
    c['valida'] = valida
    c['sensibilita_limite'] = OrderedDict((n, OrderedDict((k, L[n][k]) for k in ('eco', 'profilo', 'varianti', 'paragrafo', 'pagine_vicine', 'sintesi')) |
                                          OrderedDict(potenza=None if POT.get(n) is None else round(float(POT[n]), 3)))
                                          for n in GEN_B if GEN_B[n]['liv'] in ('M', 'D') and n in L)
    return c


# ---------------------------------------------------------------- l'analisi

def voce(m, rel, info, d):
    v = I15.voce(m, rel, info, d)
    x = m['sez']
    for k in ('Ex_vic_c', 'Ex_lon_c', 'Ev_vic_c', 'Ev_lon_c', 'loc_x', 'loc_v', 'loc', 'QL', 'loc_rel'):
        v[k] = x[k]
    return v


def gruppi(d, W, campo, minimo):
    """(b) Come ia15 ma con la lettura delle varianti sulla parte locale."""
    out = OrderedDict()
    vals = d.campo(campo)
    for g in sorted(set(vals), key=str):
        sel = np.array([x == g for x in vals])
        n = int(sel.sum())
        if n < minimo:
            out[str(g)] = OrderedDict(pagine=n, nota='troppo poche pagine per la misura')
            continue
        m = misure(d, W, sel)['sez']
        out[str(g)] = OrderedDict(pagine=n, parole=int(d.nparole[sel].sum()), E_vic=m['E_vic_c'], E_lon=m['E_lon_c'], H=m['H'], QV_vic=m['QV_vic'], QL=m['QL'],
                                  loc_rel=m['loc_rel'], Q=m['Q'], profilo=lettura_profilo(m), varianti=lettura_varianti(m))
    return out


MISURE_V21 = ['E_vic_c', 'E_lon_c', 'H', 'QV_vic', 'QL', 'loc_rel', 'Q']


def v21_contro_vere(D):
    """v21 (media dei libri) meno vere sulle pagine che hanno tutte, per le misure principali (anche la parte locale)."""
    libri = [b for b in LIBRI_V21 if b in D]
    if 'vere' not in D or not libri:
        return None
    pag = D['vere'].pag
    for b in libri:
        pag = [p for p in pag if p in D[b].pag]
    W = pesi_bootstrap(len(pag))
    mv = misure(I15.sotto_dati(D['vere'], pag), W)['sez']
    ms = [misure(I15.sotto_dati(D[b], pag), W)['sez'] for b in libri]
    out = OrderedDict(_pagine=len(pag))
    for k in MISURE_V21:
        m21 = V.media([x[k] for x in ms])
        out[k] = OrderedDict(vere=mv[k], v21=m21, differenza=m21 - mv[k], rapporto=(m21.p / mv[k].p if abs(mv[k].p) > 1e-9 else None))
    return out


def contro_rimescolato(MIS, D):
    """Descrittivo: la quota di varianti grezza (eco vicina) di un testo contro quella dello stesso testo con le parole mescolate dentro la pagina
    (che tiene il lessico e il tema della pagina e rompe la distanza): la differenza e' quanto, delle varianti, e' legato alla distanza."""
    out = OrderedDict()
    for n in MIS:
        if '~' in n or (n + '~p') not in MIS:
            continue
        a, b = MIS[n]['sez'], MIS[n + '~p']['sez']
        out[n] = OrderedDict(QV_testo=a['QV_vic'], QV_rimescolato_nella_pagina=b['QV_vic'], differenza=a['QV_vic'] - b['QV_vic'],
                             H_testo=a['H'], H_rimescolato=b['H'])
    return out


def analisi(corse, versioni):
    D = OrderedDict((r['job'][1], Dati(r)) for r in corse)
    if not D:
        raise SystemExit('FERMO: nessun lavoro da analizzare')
    tara = json.load(open(percorso_taratura(), encoding='utf-8')) if os.path.exists(percorso_taratura()) else None
    bers = tara['bersaglio'] if tara else None
    MIS, REL, T, L, POT = {}, {}, OrderedDict(), OrderedDict(), {}
    for nome, d in D.items():
        W = pesi_bootstrap(len(d.pag))
        MIS[nome] = misure(d, W)
        REL[nome] = I15.relazioni_pagine(d, W)
        T[nome] = voce(MIS[nome], REL[nome], d.info, d)
        L[nome] = tutte_le_letture(nome, MIS[nome], REL[nome], d.info['qnull'])
        POT[nome] = (MIS[nome]['sez']['E_vic_c'].p / bers) if bers else None
    ctrl = esegui_controlli(L, POT)
    ok = ctrl['valida']
    NL = 'non leggibile (i controlli di questa lettura non sono superati)'
    letture = OrderedDict()
    for nome, l in L.items():
        if '~' in nome:
            continue
        r = OrderedDict((k, (l[k] if (k == 'eco' or ok.get(k, True)) else NL)) for k in l if k != 'sintesi_senza_paragrafo')
        if not ok['sintesi']:
            r['sintesi'] = (l['sintesi_senza_paragrafo'] + ' (senza il paragrafo)') if ok['sintesi_senza_paragrafo'] else NL
        letture[nome] = r
    out = OrderedDict(esperimento='ia15b', versioni=versioni, parametri=OrderedDict(
        NRIF=NRIF, SPOSTAMENTI=SPOSTAMENTI, SEMI_RIF=seme_di('ia15:rif'), GENERATORI=GENERATORI, N_FAMIGLIE=N_FAMIGLIE, RIM_TESTO=RIM_TESTO, SCALA_COPIA=SCALA_COPIA,
        FRAZIONI_ECO=FRAZIONI_ECO, TARA_TOL=TARA_TOL, FAMIGLIA_PHI=FAMIGLIA_PHI, LOC_MIN=LOC_MIN, POTENZA_MIN=POTENZA_MIN, MIN_PAGINE_GRUPPO=MIN_PAGINE_GRUPPO,
        SOLO_CONTROLLI=SOLO_CONTROLLI, BOOT=I9.BOOT,
        soglie=OrderedDict((k, getattr(I15, k)) for k in ('SOGLIA_ECO', 'H_RIPIDO', 'H_RIPIDO_IC', 'H_PIATTO', 'H_PIATTO_IC', 'QV_ALTE', 'QV_ALTE_IC', 'QV_BASSE',
                                                         'QV_BASSE_IC', 'Q_CONTA', 'Q_CONTA_IC', 'Q_NON', 'Q_NON_IC', 'Q_PAGINE_MIN', 'REL_SI', 'REL_SI_IC',
                                                         'REL_NO', 'REL_NO_IC', 'GRAD_SI', 'DIR_QUOTA', 'DIR_ECCESSO'))),
        taratura=tara, controlli=ctrl, letture=letture, testi=T)
    if 'vere' in D:
        d, W = D['vere'], pesi_bootstrap(len(D['vere'].pag))
        out['vere_per_gruppo'] = OrderedDict(sezione=gruppi(d, W, 'sez', MIN_PAGINE_GRUPPO), tipo_di_pagina=gruppi(d, W, 'tipo', MIN_PAGINE_GRUPPO),
                                             lingua=gruppi(d, W, 'lingua', MIN_PAGINE_GRUPPO), mano=gruppi(d, W, 'mano', MIN_PAGINE_GRUPPO),
                                             area_disegno_erbario=I15.per_area(d, W, MIN_PAGINE_GRUPPO))
        out['vere_per_gruppo']['eterogeneita_sezione'] = I15.eterogeneita(out['vere_per_gruppo']['sezione'], MIN_ETEROG)
        out['vere_per_gruppo']['eterogeneita_tipo'] = I15.eterogeneita(out['vere_per_gruppo']['tipo_di_pagina'], MIN_ETEROG)
        for campo, chiave, grp in (('sez', 'controlli_per_sezione', 'eterogeneita_sezione'), ('tipo', 'controlli_per_tipo', 'eterogeneita_tipo')):
            for nome in D:
                if (nome in GEN_B and GEN_B[nome]['liv'] == 'V' and nome.endswith('1') and nome[:4] != 'tecC' and nome[:4] != 'tecT') or nome in ('latGeom', 'ingGeom'):
                    dd, WW = D[nome], pesi_bootstrap(len(D[nome].pag))
                    out.setdefault(chiave, OrderedDict())[nome] = I15.eterogeneita(gruppi(dd, WW, campo, MIN_PAGINE_GRUPPO), MIN_ETEROG)
            rif = [x['rapporto'] for n, x in out.get(chiave, {}).items() if 'rapporto' in x and L[n]['eco'] == 'misurabile']
            e = out['vere_per_gruppo'][grp]
            if 'rapporto' in e and rif:
                e['rapporto_massimo_dei_riferimenti'] = float(max(rif))
                e['esito_relativo'] = 'piu che i riferimenti' if (e['esito'] == 'varia' and e['rapporto'] >= 1.5 * max(rif)) else 'come i riferimenti'
    out['v21_contro_vere'] = v21_contro_vere(D)
    out['varianti_contro_rimescolato_nella_pagina'] = contro_rimescolato(MIS, D)
    out['ponte_ia09'] = I15.ponte_ia09(D)
    pulito = I15.pulisci(out)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulito, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    righe = scrivi_md(pulito)
    print('\n'.join(righe[:40]), flush=True)
    return pulito


# ---------------------------------------------------------------- il rapporto in .md

f3, f2, vv = I15.f3, I15.f2, I15.vv


def scrivi_md(out):
    T, L, c = out['testi'], out['letture'], out['controlli']
    tara = out.get('taratura')
    r = ['# ia15b — da dove viene l\'eco della pagina (seconda versione)', '',
         'Soglie nella preregistrazione `preregistrazioni/ia15b.md`. "Eco" = eccesso di parole uguali o a una modifica da parole gia\' scritte (stessa riga '
         'prima, righe sopra), per parola fonte, rispetto a una pagina di riferimento della stessa sezione con la stessa geometria di righe. Intervalli al 95% '
         'col bootstrap sulle pagine. Nessuna parola nei risultati. Nuovo rispetto a ia15: controlli separati per lettura, generatori tarati sull\'eco '
         'vicina del Voynich, varianti sulla sola parte locale dell\'eco.', '']
    if tara:
        r += ['## Taratura dei generatori (solo la quantita\' di eco vicina)', '',
              'Bersaglio: eco vicina %.5f (%s). Tolleranza %.0f%%. Livelli: %s.' % (tara['bersaglio'], tara['da'], 100 * tara['tolleranza'], json.dumps(tara['frazioni'])), '',
              '| famiglia | livello | quota del bersaglio | livello numerico (quota tema o prob. di copia) | eco vicina ottenuta | raggiunto | valutazioni |', '|---|---|---|---|---|---|---|']
        for fam, lv in tara['famiglie'].items():
            for liv, x in lv.items():
                r.append('| %s | %s | %s | %.4f | %.5f | %s | %d |' % (fam, liv, tara['frazioni'].get(liv), x['livello'], x['eco_vicina'], 'si' if x['raggiunto'] else 'NO', len(x['valutazioni'])))
        r.append('')
    r += ['## Letture', '']
    for n, x in L.items():
        r.append('- %s: eco %s; profilo **%s**; varianti **%s**; paragrafo **%s**; modifiche **%s**; pagine vicine **%s**; sintesi **%s**' % (
            n, x['eco'], x['profilo'], x['varianti'], x['paragrafo'], x['direzione'], x['pagine_vicine'], x['sintesi']))
    r += ['', '## Controlli', '']
    for k, v in c.items():
        if k == 'valida':
            r.append('- **lettura valida (i suoi controlli sono superati)**: ' + '; '.join('%s %s' % (a, 'SI' if b else 'NO') for a, b in v.items()))
        elif isinstance(v, dict) and 'superato' in v:
            r.append('- %s: %s (%s); letture %s; testi %s%s' % (k, 'SUPERATO' if v['superato'] else 'NON SUPERATO', v['condizione'], ', '.join(v['serve_a']), ', '.join(v['testi']),
                                                            '' if v['potenza_sufficiente'] else ' [eco sotto il %.0f%% del bersaglio: nessuna forza]' % (100 * POTENZA_MIN)))
        elif k == 'sensibilita_limite':
            r.append('- livelli M (meta\') e D (un quarto) dell\'eco del Voynich, descrittivi: ' + json.dumps(v, ensure_ascii=False))
    r += ['', '## Eco per testo (eccesso di parole simili per parola fonte)', '',
          '| testo | pagine | eco tutta (rif. sezione) | eco tutta (rif. altra sezione) | eco vicina 0-3 righe (pesi comuni) | eco lontana 4+ (pesi comuni) | H = lontana / vicina | parte locale / eco vicina | quota varianti vicina (grezza) | quota varianti nella parte locale |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for n, x in T.items():
        r.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            n, x['pagine'], vv(x['eco_sez']['tutto'], 4), vv(x['eco_altro']['tutto'], 4), vv(x['E_vic_c'], 4), vv(x['E_lon_c'], 4), vv(x['H'], 2), vv(x['loc_rel'], 2),
            vv(x['QV_vic'], 2), vv(x['QL'], 2)))
    r += ['', '## Parte locale dell\'eco: uguali e varianti (vicino meno lontano, pesi comuni)', '', '| testo | parte locale | di cui uguali | di cui varianti |', '|---|---|---|---|']
    for n, x in T.items():
        r.append('| %s | %s | %s | %s |' % (n, vv(x['loc'], 4), vv(x['loc_x'], 4), vv(x['loc_v'], 4)))
    r += ['', '## Eco per banda di distanza (rif. sezione): tutti i simili / uguali / varianti', '', '| testo | ' + ' | '.join(EM.NOMI_BANDA) + ' |', '|---' * (EM.NB + 1) + '|']
    for n, x in T.items():
        y = x['eco_sez']
        r.append('| %s | %s |' % (n, ' | '.join('%s / %s / %s' % (f3(y['bande'][b]['punto'], 4), f3(y['uguali'][b]['punto'], 4), f3(y['varianti'][b]['punto'], 4)) for b in EM.NOMI_BANDA)))
    r += ['', 'Bande: D0 stessa riga (parole prima), D1 una riga sopra, D2 due-tre righe sopra, D4 quattro-sette, D8 otto o piu\'.', '',
          '## Il paragrafo: eco dentro e fra paragrafi a 2-3 righe di distanza (senza le prime righe dei paragrafi; pagine con pesi comuni)', '',
          '| testo | Q a 2-3 righe (D2) = eco fra / eco dentro | confini spostati: 2,5% - 97,5% | eco dentro D2 | eco fra D2 | pagine usate | Q a 4-7 righe (D4) | pagine D4 | paragrafo |',
          '|---|---|---|---|---|---|---|---|---|']
    for n, x in T.items():
        nul = [z for z in x['Q_nullo'] if z is not None]
        lim = '%s - %s' % (f2(float(np.percentile(nul, 2.5))), f2(float(np.percentile(nul, 97.5)))) if nul else '-'
        r.append('| %s | %s | %s | %s | %s | %d | %s | %d | %s |' % (n, vv(x['Q'], 2), lim, vv(x['e_dentro']['D2'], 4), vv(x['e_fra']['D2'], 4), x['pagine_Q']['D2'],
                                                                   vv(x['Q4'], 2), x['pagine_Q']['D4'], (L.get(n) or {}).get('paragrafo', '')))
    r += ['', '## Dove cadono le modifiche delle varianti vicine (quota dell\'eccesso di varianti: inizio / fine / dentro; fra parentesi la quota nel riferimento)', '',
          '| testo | inizio | fine | dentro la parola | lettura |', '|---|---|---|---|---|']
    for n, x in T.items():
        r.append('| %s | %s | %s | %s | %s |' % (n, *[('%s (%s)' % (f2(x['direzione_vic'][k]['punto']), f2(x['direzione_caso_vic'][k]['punto']))) for k in 'IFM'], (L.get(n) or {}).get('direzione', '')))
    r += ['', '## Pagine vicine contro lontane (tasso di parole simili fra pagine intere, in rapporto alla stessa sezione, quaderno diverso, stessa mano)', '',
          '| testo | stesso foglio | stesso bifoglio | consecutive | stesso quaderno | altra sezione | gradiente (consecutive / quaderno) | coppie foglio / bifoglio / consecutive | solo uguali, consecutive | solo varianti, consecutive |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for n, x in T.items():
        p = x['pagine_vicine']
        s = p['simile']
        r.append('| %s | %s | %s | %s | %s | %s | %s | %d / %d / %d | %s | %s |' % (
            n, *[vv(s[k], 2) for k in ('foglio', 'bifoglio', 'consecutive', 'quaderno', 'altra_sezione', 'gradiente')], s['coppie']['foglio'], s['coppie']['bifoglio'],
            s['coppie']['consecutive'], vv(p['x']['consecutive'], 2), vv(p['v']['consecutive'], 2)))
    cr = out.get('varianti_contro_rimescolato_nella_pagina')
    if cr:
        r += ['', '## Descrittivo: quota di varianti grezza contro lo stesso testo con le parole mescolate dentro la pagina (tiene il lessico e il tema, rompe la distanza)', '',
              '| testo | quota varianti vicina | quota con le parole mescolate nella pagina | differenza | H testo | H rimescolato |', '|---|---|---|---|---|---|']
        for n, x in cr.items():
            r.append('| %s | %s | %s | %s | %s | %s |' % (n, vv(x['QV_testo'], 2), vv(x['QV_rimescolato_nella_pagina'], 2), vv(x['differenza'], 2), vv(x['H_testo'], 2), vv(x['H_rimescolato'], 2)))
    if 'vere_per_gruppo' in out:
        g = out['vere_per_gruppo']
        for chiave_g, titolo in (('sezione', 'sezione'), ('tipo_di_pagina', 'tipo di pagina'), ('lingua', 'lingua A/B'), ('mano', 'mano')):
            r += ['', '## Le pagine vere per %s' % titolo, '',
                  '| gruppo | pagine | parole | eco vicina | eco lontana | H | quota varianti vicina (grezza) | quota varianti parte locale | profilo | varianti |', '|---|---|---|---|---|---|---|---|---|---|']
            for k, x in g[chiave_g].items():
                if 'E_vic' in x:
                    r.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s |' % (k, x['pagine'], x['parole'], vv(x['E_vic'], 4), vv(x['E_lon'], 4), vv(x['H'], 2),
                                                                                   vv(x['QV_vic'], 2), vv(x['QL'], 2), x['profilo'], x['varianti']))
                else:
                    r.append('| %s | %d | - | - | - | - | - | - | - | - |' % (k, x['pagine']))
            e = g.get('eterogeneita_sezione' if chiave_g == 'sezione' else 'eterogeneita_tipo' if chiave_g == 'tipo_di_pagina' else '')
            if e:
                r += ['', 'Eterogeneita\' dell\'eco vicina fra i gruppi: %s' % json.dumps(e, ensure_ascii=False)]
        a = g['area_disegno_erbario']
        r += ['', '## Erbario: disegno piccolo, medio, grande (terzili dell\'area del disegno, e190)', '']
        for k, x in a.items():
            if isinstance(x, dict) and 'E_vic' in x:
                r.append('- %s (%d pagine): eco vicina %s; lontana %s; H %s' % (k, x['pagine'], vv(x['E_vic'], 4), vv(x['E_lon'], 4), vv(x['H'], 2)))
        if out.get('controlli_per_sezione'):
            r += ['', '## Eterogeneita\' dell\'eco vicina per sezione nei generatori (nessuna sezione nel testo) e nelle lingue nella disposizione del Voynich: il Voynich si legge contro questi', '']
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
              '| gruppo | pagine | copia netta (bit) | guadagno g (bit) | quota di copia rho |', '|---|---|---|---|---|', '| tutte | - | %s | - | - |' % vv(p['tutte']['copia_netta_bit'], 3)]
        for chiave_g in ('sezione', 'tipo_di_pagina'):
            for k, x in p.get(chiave_g, {}).items():
                r.append('| %s %s | %d | %s | %s | %s |' % (chiave_g, k, x['pagine'], vv(x['copia_netta_bit'], 3), vv(x['guadagno_g'], 3), vv(x['rho'], 2)))
    elif p:
        r += ['', '## Ponte con ia09', '', p['nota']]
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


# ---------------------------------------------------------------- l'esecuzione

def main():
    import scipy
    versioni = dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'taratura,conteggi,analisi').split(',')
    processi = int(os.environ.get('PROCESSI', 4))
    c = G.contesto()
    print('pagine vere: %d; libri %s; riferimenti %d; spostamenti %d; generatori %d' % (len(c['ids']), LIBRI_V21, NRIF, SPOSTAMENTI, len(GEN_B)), flush=True)
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI_V21 if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01)' % (', '.join(mancano), G.LIBRI))
    if 'taratura' in fasi:
        if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso_taratura()):
            print('taratura gia\' fatta: si riusa %s' % percorso_taratura(), flush=True)
        else:
            esegui_taratura(processi)
    percorso = os.path.join(USCITA, 'ia15b_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = I15.carica_corse(percorso)
    elif 'conteggi' in fasi:
        open(percorso, 'w').close()
    if 'conteggi' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        Lj = lavori(['conteggi'])
        da_fare = [j for j in Lj if json.dumps(list(j)) not in fatte]
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(Lj) - len(da_fare)), flush=True)
        inizio = time.time()

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
        corse = I15.carica_corse(percorso)
    if 'analisi' in fasi:
        analisi(corse, versioni)


if __name__ == '__main__':
    main()
