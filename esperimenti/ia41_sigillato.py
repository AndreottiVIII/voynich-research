# -*- coding: utf-8 -*-
"""Esperimento IA41 (ia41): l'esame sigillato su divisioni nuove dei fogli.

Domanda: il risultato di IA40 (riga `s100k30`: punto di IA35 sul Voynich con `a_sez` 1 e ripiego K 30; b piu' basso di `t100` e `sezione` entro 2σ) regge su pagine MAI viste, con strumenti nuovi?
Si rifa' la divisione dei fogli: 4 divisioni NUOVE (`SEME_FOGLI32` 4101-4104, scritti prima) piu' l'ORIGINALE (3232) con semi nuovi per i libri. Per ogni divisione si rifanno la rete `Cb` di IA35 (stesso seme
di rete, stessa taglia, stesso addestramento) e le tabelle per sezione SOLO sui fogli d'addestramento di quella divisione; manopole identiche. Le circa 30 pagine tenute fuori di ogni divisione nuova non sono mai
state viste da rete, tabelle e scelte. Nessuna regolazione nuova: si esamina quello che c'e'.
Righe fissate ora: `s100k30` (a_sez 1, K 30), `t100` (punto di IA35, il "prima"), `neu` (manopole neutre: validita' di b, deve dare almeno 0,70), `dif` (difetto piantato: meta' delle righe di `s100k30` sostituite
con quelle di `neu`) e i 10 libri v21 gia' scritti. 8 libri per riga e per divisione. Giudici, tutti con "vero" = le sole pagine tenute fuori: b (mediato su 8 divisioni dei fogli, `sezione_giudice`),
sorpresa in avanti, sorpresa al contrario, indovina-sezione (`sigillo_giudici`). Misure: le otto di struttura di IA35 piu' sei nuove (`sigillo_misure`), con `sezione` a parte. N, KN, D solo sulla divisione
originale, come informazione. Difetti piantati: pagine rimescolate (misure e indovina-sezione che dipendono dalla sezione) e meta' righe di `neu` (b e le due sorprese). Preregistrazione: preregistrazioni/ia41.md.

Struttura (un processo per divisione, perche' `SEME_FOGLI32` si legge all'avvio; il programma si rilancia da solo):
  fase R   (per divisione) cartella separata `dati/cache/ia41/div<k>/`, rete e tabelle solo sui fogli d'addestramento di quella divisione (la divisione 0 usa la rete di IA37 dopo aver controllato che i fogli siano gli stessi)
  fase E   (per divisione) libri, giudici, misure, difetti piantati -> `esito_div.json` (solo numeri)
  fase S   (una volta) criteri scritti prima, esiti, `risultati/ia41_sigillato.{md,json}`

    nohup bash strumenti/coda.sh ia41 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia41" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella nel repo> CACHE41=<cartella nel repo> python esperimenti/ia41_sigillato.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): CACHE41, N_LIBRI41 (8), DIVISIONI41 (cifre delle divisioni da fare, predefinito 01234), MONDO41 (2 = vero, 3 = mondo di sviluppo `struttura3`, solo con
SOLO_CONTROLLI=1), SEMI41 (etichetta dei semi dei libri), ESTRAZIONI41 (60: estrazioni di fogli per il rumore), DIV41 e FASE41 (interne: il programma le imposta rilanciandosi), GRU41 non c'e' (niente R_rel).
"""
import json
import math
import os
import shutil
import subprocess
import sys
import time
import zlib
from collections import Counter, OrderedDict
from multiprocessing import get_context

# la divisione dei fogli si legge all'avvio (`rifare_dati.SEME_FOGLI32`): per un processo di divisione il seme va messo PRIMA di ogni importazione
_SEMI_FOGLI = {0: 3232, 1: 4101, 2: 4102, 3: 4103, 4: 4104}
_DIV = os.environ.get('DIV41')
DIV = int(_DIV) if _DIV is not None else None
if DIV is not None:
    os.environ['SEME_FOGLI32'] = str(_SEMI_FOGLI[DIV])
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402

NOME = 'ia41_sigillato'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE41 = os.environ.get('CACHE41', os.path.join(USCITA, 'ia41_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia41'))
CACHE37_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia37')
CACHE35_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia35')
MONDI_ELENCO = ['struttura2', 'vero', 'struttura3']
MONDO = MONDI_ELENCO[int(os.environ.get('MONDO41', '2')) - 1]
if MONDO == 'struttura3' and not SOLO_CONTROLLI:
    raise SystemExit('struttura3 e\' solo per le prove (SOLO_CONTROLLI=1)')
os.environ['CACHE26'] = os.path.join(CACHE41, 'div%d' % (DIV if DIV is not None else 0), 'banco')     # il banco di IA26 scrive qui, per divisione: mai nelle cache di IA26-IA40
os.environ.setdefault('CHUNK26', '500')
os.environ.setdefault('S_GRU_MONDO26', '6')
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_misure as RM  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import sezione_mondo as SMO  # noqa: E402,F401  (registra `struttura2`)
import sezione_rete as SR  # noqa: E402
import prudente_scrittura as PW  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402
import freqsez_scrittura as FW  # noqa: E402
import freqsez_lavori as FL  # noqa: E402
import sigillo_misure as SMIS  # noqa: E402
import sigillo_giudici as SGIU  # noqa: E402
if os.environ.get('SOLO_CONTROLLI') == '1':
    import prudente_mondo  # noqa: E402,F401   (il mondo di sviluppo `struttura3`: solo prove)

_ATTIVO = {}
N_LIBRI = int(os.environ.get('N_LIBRI41', 8))
DIVISIONI = [int(x) for x in os.environ.get('DIVISIONI41', '01234') if x.isdigit() and int(x) in _SEMI_FOGLI]
SEMI = os.environ.get('SEMI41', '')
PIEGHE = I7.PIEGHE
V21_NOMI = ['V21:%d' % k for k in range(13, 23)]
GIUDICI3 = ('N', 'KN', 'b')
SEME_RETE = 35001                                   # lo stesso seme di rete di IA35 (`sezione_rete.SEME_RETE35`)

# ---- criteri e soglie scritti nella preregistrazione prima di ogni numero sul Voynich
B_MIN_NEU = 0.70                    # validita' di b: la rete sola deve essere vista
FASCIA = (0.40, 0.60)               # b e sorprese
FASCIA_V21 = 0.65                   # 0,60-0,65 = "pari col v21"
DELTA_B_MIN = 0.02                  # criterio 1: b(t100) - b(s100k30) in media almeno cosi', e s100k30 sotto t100 in almeno 3 divisioni su 4
SOGLIA_SIGMA = 2.0                  # misure entro 2 sigma (sigma = rumore di campionamento)
VECCHIE_ALTRE_MIN = 5               # criterio 4: almeno 5 delle altre 7 misure vecchie (la proporzione 6/8 delle sette disponibili: D e R_rel non ci sono)
NUOVE_QUOTA = 2.0 / 3.0             # criterio 6: almeno 2/3 delle misure nuove valide (4 su 6)
CROLLO_IND = 0.25                   # indovina-sezione "vede" il difetto delle pagine rimescolate se l'accuratezza cala di almeno cosi' (assoluto)


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def leggi_corse(percorso):
    if not os.path.exists(percorso):
        return []
    out = []
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            try:
                out.append(json.loads(l))
            except ValueError:
                pass
    return out


def fatte_di(mondo):
    if os.environ.get('RIPRENDI') == '1':
        return {c['lavoro'] for c in leggi_corse(percorso_corse(mondo)) if not c.get('errore')}
    return set()


def azzera_corse(mondo):
    if os.environ.get('RIPRENDI') != '1':
        os.makedirs(USCITA, exist_ok=True)
        open(percorso_corse(mondo), 'w').close()


def avvia(mondo, nomi):
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    RM.prepara(mondo, cart41(mondo), nomi)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia36_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro41, da_fare), 1):
            out.append(r)
            if scrivi:
                with open(percorso_corse(mondo), 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: (round(r[x], 3) if isinstance(r[x], float) else r[x]) for x in ('obiettivo', 'obiettivo_puro', 'penalita', 'AUC_e231', 'AUC_N', 'copia_netta', 'k90') if x in r}
                print('[%s %d/%d %.1f min] %s: %s (%.0f s)' % (mondo, k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def attiva_main(mondo, nomi=()):
    """Attiva il mondo nel processo principale UNA volta sola (come in IA35: un solo mondo per processo, gli altri in un processo figlio)."""
    if _ATTIVO.get('mondo') == mondo:
        B._S['nomi'] = [n for n in nomi if n != 'vero']
        return B._S
    if _ATTIVO:
        raise RuntimeError('un solo mondo per processo: %s e poi %s' % (_ATTIVO['mondo'], mondo))
    _ATTIVO['mondo'] = mondo
    return B.imposta_mondo(mondo, list(nomi))


def scrittore40(spec):
    """Lo scrittore di una riga: `['L', cubo a 15, K]` -> scrittore di IA37 (`ScrittoreFreq`; K = ripiego, None = quello del file o 20: non conta con `a_sez` = 0);
    `['M', cubo a 16]` -> lo scrittore di IA36 con la memoria di sezione (`ScrittoreSez`), da cui IA37 discende."""
    cart = os.path.join(RM._W['cart'], 'rete_C')
    if spec[0] == 'M':
        k = ('M',)
        if k not in RM._W:
            RM._W[k] = PW.ScrittoreSez(cart)
        return RM._W[k]
    K = spec[2]
    k = ('L', K)
    if k not in RM._W:
        S = FW.ScrittoreFreq(cart)
        if K:
            S.K = float(K)
            S.tab = FT.TabelleSezione(S, S.P.f_add, S.K)
            S._lex_sez = {}
        RM._W[k] = S
    return RM._W[k]


def scrivi_libro40(tipo, i, spec, seme):
    """Un libro intero della riga `tipo` (nel formato del banco). -> dict (come `prudente_lavori.scrivi_libro36`)."""
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    man = None
    if os.path.exists(p):
        t = I7.leggi_file(p)
    else:
        t, man = scrittore40(spec).libro33(np.asarray(spec[1], float), seme, None)
        I7.scrivi_file(t, p + '.tmp', 'ia41, libro %s %d, mondo %s' % (tipo, i, RM._W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def u_dose(u14, f):
    """Il termostato a forza `f`: moltiplica insieme `w_cont`, `w_tri`, `w_quad`, `w_uni`, `w_bi` (esatto, perche' il peso e' lineare sopra 0,2); il resto fermo."""
    u = np.array(u14, float)
    for i in IDX_CONTI:
        if u[i] > U_PIATTO:
            u[i] = U_PIATTO + f * (u[i] - U_PIATTO)
        else:
            u[i] = u[i]
    return u


def cubo15(u14, a_sez=0.0):
    return np.concatenate([np.asarray(u14, float), [U_PIATTO + 0.8 * a_sez]])


def nome_libro(tipo, i):
    return 'tar:%s:%d' % (tipo, i)


def punto_base(mondo):
    """Il punto di IA35 per il mondo (cubo a 14); nel mondo di sviluppo con PUNTO_BASE40=stress un punto moderato scritto a mano."""
    p = os.path.join(CACHE35_ORIG, mondo, 'ciclo_esito.json')
    if not SOLO_CONTROLLI and os.path.exists(p):
        return np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float)[:14]
    if SOLO_CONTROLLI and PUNTO_BASE == 'stress':
        return np.array(OS.cubo_da_valori(VALORI_STRESS2), float)
    raise RuntimeError('manca il punto di IA35 per il mondo %s (dati/cache/ia35/%s/ciclo_esito.json)' % (mondo, mondo))


IDX_CONTI = (6, 7, 8, 10, 11)
U_PIATTO = 0.2
PUNTO_BASE = os.environ.get('PUNTO_BASE41', 'ia35')
VALORI_STRESS2 = OrderedDict([('T_eol', 0.8), ('w_cont', 3.0), ('w_tri', 3.0), ('w_quad', 3.0), ('s', 0.8), ('w_uni', 1.0), ('w_bi', 1.0), ('b_nuove', -0.8), ('w_pag', 0.3)])


def cart41(mondo, *p):
    return os.path.join(CACHE41, 'div%d' % (DIV if DIV is not None else 0), mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia41_corse_div%d_%s.jsonl' % (DIV if DIV is not None else 0, mondo))


def ident(a):
    if a[0] == 'B35':
        return 'B35|%s' % a[1]
    if a[0] == 'libro41':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'dif41':
        return 'libro|dif|%s' % a[1]
    if a[0] == 'SIG':
        return 'SIG|%s' % a[1]
    return '|'.join(str(x) for x in a)


# ---------------------------------------------------------------- righe e difetti

def righe(u14):
    """Le righe fissate ora (non si cambiano dopo): spec = ['L', cubo a 15, K]."""
    R = OrderedDict()
    R['s100k30'] = dict(descr='punto di IA35 con a_sez 1, ripiego K 30 (riga d\'esame)', spec=['L', list(map(float, cubo15(u14, 1.0))), 30])
    R['t100'] = dict(descr='punto di IA35 (il "prima")', spec=['L', list(map(float, cubo15(u14, 0.0))), None])
    R['neu'] = dict(descr='manopole neutre (rete sola: validita\' di b)', spec=['L', list(map(float, FW.neutro_cubo37())), None])
    return R


def meta_righe_t(t_a, t_b):
    """Difetto piantato `dif`: una riga su due (le dispari di ogni pagina) del libro `t_a` sostituita dalla riga corrispondente di `t_b` (liste (pagina, inizio, parole))."""
    bp = {}
    for p, ini, ps in t_b:
        bp.setdefault(p, []).append(ps)
    cont = Counter()
    out = []
    for p, ini, ps in t_a:
        j = cont[p]
        cont[p] += 1
        alt = bp.get(p, [])
        out.append((p, ini, alt[j] if (j % 2 == 1 and j < len(alt)) else ps))
    return out


# ---------------------------------------------------------------- lavori

def _stato():
    """I giudici nuovi della divisione, costruiti una volta per processo (modello di sorpresa in avanti, classificatore)."""
    if 'giudici' not in RM._W:
        c = I7.contesto_A()
        f_add, f_val, f_fuori = RD.divisione_fogli()
        RM._W['giudici'] = SGIU.Giudici(c, f_add, f_val, f_fuori)
    return RM._W['giudici']


def lavoro_SIG(tipo, nomi):
    """Giudici nuovi e misure di un insieme di libri (nomi del banco): sorpresa in avanti per libro, sorpresa al contrario (modello addestrato sul primo libro, giudica gli altri), indovina-sezione e le
    quattordici misure sulle sole pagine tenute fuori."""
    inizio = time.time()
    G = _stato()
    libri = [B.rows_testo(n) for n in nomi]
    out = OrderedDict([('lavoro', 'SIG|%s' % tipo), ('tipo', tipo), ('nomi', nomi)])
    out['avanti'] = [G.auc_avanti(r) for r in libri]
    out['indietro'] = G.auc_indietro(G.modello_finto(libri[0]), libri[1:]) if len(libri) > 1 else []
    out['indovina'] = [G.acc_indovina(r) for r in libri]
    out['misure'] = [SMIS.misure(r, G.pag_ho) for r in libri]
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_RUM():
    """Il vero tenuto fuori: le quattordici misure, il rumore di campionamento, l'accuratezza di indovina-sezione, le pagine."""
    inizio = time.time()
    G = _stato()
    c = G.c
    out = OrderedDict([('lavoro', 'RUM')])
    out['vero'] = SMIS.misure(c['vere'], G.pag_ho)
    out['rumore'] = SMIS.rumore(c['vere'], list(c['ids']))
    out['indovina_vero'] = G.acc_indovina(c['vere'])
    out['pagine_tenute_fuori'] = len(G.pag_ho)
    out['pagine_indovinabili'] = len(G.pagine_indovinabili())
    out['ordine_kn'] = G.ordine
    out['sezioni_classi'] = G.classi
    out['fogli'] = [len(RD.divisione_fogli()[i]) for i in range(3)]
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_DEFA(nomi):
    """Difetto piantato `pagine_rimescolate` sui libri `nomi` (di `s100k30`): misure e indovina-sezione sulle sole pagine tenute fuori."""
    inizio = time.time()
    G = _stato()
    libri = [SMIS.pagine_rimescolate(B.rows_testo(n), seme=4141 + i) for i, n in enumerate(nomi)]
    out = OrderedDict([('lavoro', 'DEFA'), ('misure', [SMIS.misure(r, G.pag_ho) for r in libri]), ('indovina', [G.acc_indovina(r) for r in libri])])
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_dif(i):
    """Scrive il libro `dif` n. i: meta' righe di `s100k30` n. i sostituite con quelle di `neu` n. i (stesse pagine e righe)."""
    t = meta_righe_t(I7.leggi_file(B.percorso_libro_tar('s100k30', i)), I7.leggi_file(B.percorso_libro_tar('neu', i)))
    p = B.percorso_libro_tar('dif', i)
    I7.scrivi_file(t, p + '.tmp', 'ia41, libro dif %d (meta\' righe di neu), mondo %s' % (i, RM._W['mondo']), 0)
    os.replace(p + '.tmp', p)
    return OrderedDict([('lavoro', 'libro|dif|%d' % i), ('tipo', 'dif'), ('i', i), ('righe', len(t))])


def lavoro41(args):
    try:
        if args[0] == 'libro41':
            return scrivi_libro40(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'dif41':
            return lavoro_dif(int(args[1]))
        if args[0] == 'SIG':
            return lavoro_SIG(args[1], args[2])
        if args[0] == 'RUM':
            return lavoro_RUM()
        if args[0] == 'DEFA':
            return lavoro_DEFA(args[1])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3] if not isinstance(a, (list, dict)))), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = FL.lavoro_banco37(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


# ---------------------------------------------------------------- R: la divisione (rete e tabelle solo sui fogli d'addestramento di questa divisione)

def fase_R(mondo, processi):
    """Cartella separata per divisione. Riferimento e modelli di misura del banco dalla cache di IA37 (non dipendono dalla divisione dei fogli); la RETE e le TABELLE: divisione 0 = rete di IA37 (si controlla che i
    fogli siano quelli della divisione), divisioni nuove = si riaddestra la variante `Cb` (stesso seme di IA35) sui fogli d'addestramento di QUESTA divisione. Niente si legge dalle cache di altre divisioni."""
    os.makedirs(cart41(mondo), exist_ok=True)
    f_add, f_val, f_fuori = RD.divisione_fogli()
    d_banco = os.path.join(CACHE41, 'div%d' % DIV, 'banco', mondo)
    o_banco = os.path.join(CACHE37_ORIG, 'banco', mondo)
    if not SOLO_CONTROLLI and not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        os.makedirs(os.path.join(d_banco, 'modelli_misura'), exist_ok=True)
        for f in os.listdir(os.path.join(o_banco, 'modelli_misura')):
            shutil.copy(os.path.join(o_banco, 'modelli_misura', f), os.path.join(d_banco, 'modelli_misura', f))
        shutil.copy(os.path.join(o_banco, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
    if not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        raise RuntimeError('manca il riferimento del banco di %s (%s)' % (mondo, d_banco))
    pt = cart41(mondo, 'rete_C', 'pieno.pt')
    if not os.path.exists(pt):
        if DIV == 0 and not SOLO_CONTROLLI:
            shutil.copytree(os.path.join(CACHE37_ORIG, mondo, 'rete_C'), cart41(mondo, 'rete_C'), dirs_exist_ok=True)
            print('divisione 0: rete condizionata copiata da IA37', flush=True)
        else:
            print('divisione %d: addestro la rete Cb sui %d fogli d\'addestramento della divisione (validazione %d, tenuti fuori %d)' % (DIV, len(f_add), len(f_val), len(f_fuori)), flush=True)
            SR.addestra_pieno35(cart41(mondo, 'rete_C'), cond=True, var=SR.VARIANTI['Cb'], messaggi=lambda s: print('[addestra] %s' % s, flush=True))
    import torch
    d = torch.load(pt, weights_only=False)
    assert list(d['f_add']) == list(f_add) and list(d['f_val']) == list(f_val) and list(d['f_fuori']) == list(f_fuori), 'i fogli della rete non sono quelli della divisione %d' % DIV
    nat_p = cart41(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        attiva_main(mondo, [])
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    controllo = OrderedDict([('divisione', DIV), ('seme_fogli', RD.SEME_FOGLI32), ('fogli', [len(f_add), len(f_val), len(f_fuori)]), ('fogli_rete_uguali', True),
                             ('tenuti_fuori', list(f_fuori)), ('rete', os.path.abspath(pt))])
    json.dump(controllo, open(cart41(mondo, 'controllo_divisione.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('divisione %d: seme fogli %d, fogli %s; la rete ha esattamente questi fogli' % (DIV, RD.SEME_FOGLI32, controllo['fogli']), flush=True)


# ---------------------------------------------------------------- E: libri, giudici, misure

def v21_disponibili():
    out = []
    if SOLO_CONTROLLI:
        return out
    for n in V21_NOMI:
        try:
            if RT.rows_di(n) is not None:
                out.append(n)
        except Exception:                                                 # noqa: BLE001
            pass
    return out


def fase_E(mondo, processi):
    R = righe(punto_base(mondo))
    tipi = list(R) + ['dif']
    nomi = [nome_libro(t, i) for t in tipi for i in range(1, N_LIBRI + 1)]
    v21 = v21_disponibili()
    attiva_main(mondo, nomi + v21)
    fatte = fatte_di(mondo)
    libri = [('libro41', t, i, d['spec'], seme_str('ia41esame' + SEMI, DIV, t, i)) for t, d in R.items() for i in range(1, N_LIBRI + 1)]
    print('== divisione %d: %d libri da scrivere' % (DIV, len(libri)), flush=True)
    esegui(mondo, nomi + v21, libri, processi, fatte)
    esegui(mondo, nomi + v21, [('dif41', i) for i in range(1, N_LIBRI + 1)], processi, fatte)
    gruppi = [(t, [nome_libro(t, i) for i in range(1, N_LIBRI + 1)]) for t in tipi] + ([('v21', v21)] if len(v21) > 1 else [])
    lavori = [('B35', t, ns, seme_str('b35' + SEMI, DIV, t) % 1000) for t, ns in gruppi]
    lavori += [('SIG', t, ns) for t, ns in gruppi] + [('RUM',), ('DEFA', [nome_libro('s100k30', i) for i in range(1, min(4, N_LIBRI) + 1)])]
    if DIV == 0:                                                     # N, KN, D solo sulla divisione originale, come informazione
        base = [n for t in R for n in [nome_libro(t, i) for i in range(1, N_LIBRI + 1)]]
        lavori += [('M', n) for n in base] + [('J32', n) for n in base] + [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    lavori = sorted(lavori, key=lambda a: {'RUM': 0, 'SIG': 1, 'DEFA': 1, 'B35': 2}.get(a[0], 3))
    print('== divisione %d: %d lavori del banco' % (DIV, len(lavori)), flush=True)
    esegui(mondo, nomi + v21, lavori, processi, fatte)
    return riassunto_divisione(mondo, R, tipi, gruppi, nomi + v21)


def _errore_b(b):
    nb = len(b.get('per_libro') or [])
    s = b.get('sd_libri') or 0.0
    return math.sqrt(s * s / max(nb, 1) + (b.get('nullo_sd') or 0.0) ** 2)


def riassunto_divisione(mondo, R, tipi, gruppi, nomi):
    attiva_main(mondo, nomi)
    corse = leggi_corse(percorso_corse(mondo))
    ok = [r for r in corse if not r.get('errore')]
    sig = {r['tipo']: r for r in ok if str(r.get('lavoro', '')).startswith('SIG|')}
    bj = {r['lavoro'][4:]: r for r in ok if str(r.get('lavoro', '')).startswith('B35|')}
    rum = next((r for r in ok if r.get('lavoro') == 'RUM'), None)
    defa = next((r for r in ok if r.get('lavoro') == 'DEFA'), None)
    if rum is None:
        raise RuntimeError('manca il lavoro RUM (rumore e vero tenuto fuori)')
    sd = {n: (rum['rumore'][n] or {}).get('sd') for n in SMIS.TUTTE}

    def z_misure(lista):
        out = OrderedDict()
        for n in SMIS.TUTTE:
            v = [m.get(n) for m in lista if m.get(n) is not None]
            if v and rum['vero'].get(n) is not None and sd.get(n):
                out[n] = (float(np.mean(v)) - rum['vero'][n]) / sd[n]
        return out

    def media(x):
        x = [a for a in x if a is not None]
        return float(np.mean(x)) if x else None

    def sdv(x):
        x = [a for a in x if a is not None]
        return float(np.std(x, ddof=1)) if len(x) > 1 else None
    righe_out = OrderedDict()
    for t, _ns in gruppi:
        s, b = sig.get(t), bj.get(t)
        if s is None:
            continue
        righe_out[t] = OrderedDict([('n', len(s['nomi'])), ('b', (b or {}).get('auc')), ('b_errore', _errore_b(b) if b else None), ('avanti', media(s['avanti'])), ('avanti_sd', sdv(s['avanti'])),
                                    ('indietro', media(s['indietro'])), ('indietro_sd', sdv(s['indietro'])), ('indovina', media(s['indovina'])), ('indovina_sd', sdv(s['indovina'])),
                                    ('z', z_misure(s['misure']))])
    difetti = OrderedDict()
    if defa:
        difetti['pagine_rimescolate'] = OrderedDict([('z', z_misure(defa['misure'])), ('indovina', media(defa['indovina']))])
    out = OrderedDict([('divisione', DIV), ('seme_fogli', RD.SEME_FOGLI32), ('righe', righe_out), ('difetti', difetti), ('vero', OrderedDict([('indovina', rum['indovina_vero']), ('misure', rum['vero']),
                       ('rumore', OrderedDict((n, sd[n]) for n in SMIS.TUTTE)), ('pagine_tenute_fuori', rum['pagine_tenute_fuori']), ('pagine_indovinabili', rum['pagine_indovinabili']),
                       ('ordine_kn', rum['ordine_kn']), ('sezioni_classi', rum['sezioni_classi']), ('fogli', rum['fogli'])]))])
    if DIV == 0:                                                      # informazione: N, KN, D dei libri della divisione originale
        C = B.indice_corse(ok)
        pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
        n_pag = len(I7.contesto_A()['ids'])
        inf = OrderedDict()
        for t in R:
            v = [RM.valori_libro(nome_libro(t, i), C, pK, pKN, n_pag) for i in range(1, N_LIBRI + 1)]
            inf[t] = OrderedDict((k, media([x.get(k) for x in v])) for k in ('N', 'KN', 'D'))
        out['informazione_N_KN_D'] = inf
    json.dump(out, open(cart41(mondo, 'esito_div.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return out


# ---------------------------------------------------------------- S: criteri, esiti, sintesi

def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def _m(x):
    x = [a for a in x if a is not None]
    return float(np.mean(x)) if x else None


def valuta(divs):
    """Criteri e strumenti validi sulle divisioni NUOVE `divs` (lista di esito_div): tutti scritti prima. -> dict."""
    nd = len(divs)
    s = [d['righe']['s100k30'] for d in divs]
    t = [d['righe']['t100'] for d in divs]
    neu = [d['righe']['neu'] for d in divs]
    dif = [d['righe'].get('dif') for d in divs]
    v21 = [d['righe'].get('v21') for d in divs]
    out = OrderedDict()
    neu_b = _m([x['b'] for x in neu])
    out['valido'] = bool(neu_b is not None and neu_b >= B_MIN_NEU)
    out['neu_b'] = neu_b
    # ---- strumenti validi: un difetto piantato che lo strumento non vede lo fa uscire dal verdetto
    z_difA = OrderedDict((n, _m([d['difetti'].get('pagine_rimescolate', {}).get('z', {}).get(n) for d in divs])) for n in SMIS.TUTTE)
    ind_vero = _m([d['vero']['indovina'] for d in divs])
    ind_difA = _m([d['difetti'].get('pagine_rimescolate', {}).get('indovina') for d in divs])
    valido = OrderedDict()
    for n in ('sezione', 'lingua', 'vicine'):
        valido[n] = bool(z_difA.get(n) is not None and abs(z_difA[n]) >= SMIS.SOGLIA_DIFETTO)
    valido['indovina'] = bool(ind_vero is not None and ind_difA is not None and ind_difA <= ind_vero - CROLLO_IND)
    b_dif = _m([x['b'] for x in dif if x])
    av_dif, in_dif = _m([x['avanti'] for x in dif if x]), _m([x['indietro'] for x in dif if x])
    valido['b'] = bool(b_dif is not None and b_dif > FASCIA[1])
    valido['avanti'] = bool(av_dif is not None and not (FASCIA[0] <= av_dif <= FASCIA[1]))
    valido['indietro'] = bool(in_dif is not None and not (FASCIA[0] <= in_dif <= FASCIA[1]))
    out['strumenti_validi'] = valido
    out['difetti'] = OrderedDict([('pagine_rimescolate_z', z_difA), ('indovina_vero', ind_vero), ('indovina_pagine_rimescolate', ind_difA), ('meta_righe_b', b_dif), ('meta_righe_avanti', av_dif), ('meta_righe_indietro', in_dif)])
    # ---- criterio 1: b di s100k30 sotto t100
    sotto = sum(1 for a, b in zip(s, t) if a['b'] is not None and b['b'] is not None and a['b'] < b['b'])
    delta = _m([b['b'] - a['b'] for a, b in zip(s, t) if a['b'] is not None and b['b'] is not None])
    c1 = bool(valido['b'] and sotto >= max(1, nd - 1) and delta is not None and delta >= DELTA_B_MIN)
    out['c1'] = OrderedDict([('ok', c1), ('divisioni_con_s_sotto_t', sotto), ('di', nd), ('delta_medio', delta), ('b_s', [x['b'] for x in s]), ('b_t', [x['b'] for x in t])])
    # ---- criterio 2: b medio in fascia
    bm = _m([x['b'] for x in s])
    out['c2'] = OrderedDict([('ok', bool(valido['b'] and bm is not None and FASCIA[0] <= bm <= FASCIA[1])), ('b_medio', bm), ('pari_col_v21', bool(bm is not None and FASCIA[1] < bm <= FASCIA_V21)),
                             ('b_v21', _m([x['b'] for x in v21 if x]))])
    # ---- criteri 3 e 4: misure vecchie
    zs = OrderedDict((n, _m([x['z'].get(n) for x in s])) for n in SMIS.TUTTE)
    out['z_medi'] = zs
    zt = OrderedDict((n, _m([x['z'].get(n) for x in t])) for n in SMIS.TUTTE)
    out['z_medi_t100'] = zt
    out['z_medi_v21'] = OrderedDict((n, _m([x['z'].get(n) for x in v21 if x])) for n in SMIS.TUTTE)
    out['c3'] = OrderedDict([('ok', bool(valido['sezione'] and zs.get('sezione') is not None and abs(zs['sezione']) <= SOGLIA_SIGMA)), ('sezione_z', zs.get('sezione'))])
    altre = [n for n in SMIS.VECCHIE if n != 'sezione']
    dentro = [n for n in altre if zs.get(n) is not None and abs(zs[n]) <= SOGLIA_SIGMA]
    out['c4'] = OrderedDict([('ok', len(dentro) >= VECCHIE_ALTRE_MIN), ('dentro', dentro), ('fuori', [n for n in altre if n not in dentro]), ('su', len(altre)), ('minimo', VECCHIE_ALTRE_MIN)])
    # ---- criterio 5: sorprese e indovina-sezione
    av, ind = _m([x['avanti'] for x in s]), _m([x['indietro'] for x in s])
    ia = _m([x['indovina'] for x in s])
    diff_ind = [x['indovina'] - d['vero']['indovina'] for x, d in zip(s, divs) if x['indovina'] is not None and d['vero']['indovina'] is not None]
    err_ind = max(0.03, (float(np.std(diff_ind, ddof=1)) / math.sqrt(len(diff_ind))) if len(diff_ind) > 1 else 0.03)
    c5 = OrderedDict([('avanti', av), ('avanti_ok', bool(valido['avanti'] and av is not None and FASCIA[0] <= av <= FASCIA[1])), ('indietro', ind), ('indietro_ok', bool(valido['indietro'] and ind is not None and FASCIA[0] <= ind <= FASCIA[1])),
                      ('indovina_finto', ia), ('indovina_vero', ind_vero), ('differenza', _m(diff_ind)), ('errore', err_ind),
                      ('indovina_ok', bool(valido['indovina'] and diff_ind and abs(_m(diff_ind)) <= 2 * err_ind))])
    c5['ok'] = bool(c5['avanti_ok'] and c5['indietro_ok'] and c5['indovina_ok'])
    out['c5'] = c5
    # ---- criterio 6: misure nuove
    vn = [n for n in SMIS.NUOVE if valido.get(n, True)]
    din = [n for n in vn if zs.get(n) is not None and abs(zs[n]) <= SOGLIA_SIGMA]
    out['c6'] = OrderedDict([('ok', bool(vn and len(din) >= math.ceil(NUOVE_QUOTA * len(vn) - 1e-9))), ('dentro', din), ('fuori', [n for n in vn if n not in din]), ('validi', vn),
                             ('usciti_dal_verdetto', [n for n in SMIS.NUOVE if n not in vn]), ('lingua_z', zs.get('lingua')), ('previsione_lingua', 'fallisce')])
    if not out['valido']:
        esito = 'non valido: b non vede le manopole neutre'
    elif not (c1 and out['c3']['ok']):
        esito = 'IA40 legata alla prima divisione: il risultato non regge su pagine mai viste (criterio 1 o 3 caduto); il compromesso torna'
    elif out['c2']['ok'] and out['c4']['ok'] and c5['ok'] and out['c6']['ok']:
        esito = 'confermato su pagine mai viste, con strumenti nuovi'
    else:
        caduti = [k for k, v in (('2 b in fascia', out['c2']['ok']), ('4 altre misure', out['c4']['ok']), ('5 sorprese e indovina-sezione', c5['ok']), ('6 misure nuove', out['c6']['ok'])) if not v]
        esito = 'regge su b e sezione (criteri 1 e 3) ma cadono: ' + '; '.join(caduti) + ' (difetti con nome per la colonna "che cosa no")'
    out['esito'] = esito
    return out


def fase_S(mondo):
    os.makedirs(USCITA, exist_ok=True)
    div = OrderedDict()
    for k in DIVISIONI:
        p = os.path.join(CACHE41, 'div%d' % k, mondo, 'esito_div.json')
        if os.path.exists(p):
            div[k] = json.load(open(p, encoding='utf-8'), object_pairs_hook=OrderedDict)
    nuove = [div[k] for k in DIVISIONI if k != 0 and k in div]
    if len(nuove) < 2:
        raise SystemExit('servono almeno due divisioni nuove per la sintesi (trovate %d)' % len(nuove))
    ver = valuta(nuove)
    out = OrderedDict([('esperimento', NOME), ('mondo', mondo), ('divisioni_nuove', [d['divisione'] for d in nuove]), ('esito', ver['esito']), ('verdetto', ver), ('divisioni', div)])
    json.dump(out, open(os.path.join(USCITA, 'ia41_sigillato.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    sv = ver['strumenti_validi']
    md = ['# IA41 (ia41) — Esame sigillato su divisioni nuove dei fogli', '', 'Preregistrazione: `preregistrazioni/ia41.md`. Mondo `%s`. Solo numeri e aggregati.' % mondo, '',
          '**Esito: %s.** (media sulle divisioni nuove: %s; giudice b valido: %s, `neu` b %s)' % (ver['esito'], ', '.join('%d (seme %d)' % (d['divisione'], d['seme_fogli']) for d in nuove), ver['valido'], mf(ver['neu_b'])), '',
          '## Criteri (scritti prima)', '', '| criterio | esito | numeri |', '|---|---|---|',
          '| 1. b di `s100k30` sotto `t100` in almeno 3 divisioni su 4 e di almeno 0,02 in media | %s | sotto in %d su %d; differenza media %s; b `s100k30` %s; b `t100` %s |' % (
              'SI' if ver['c1']['ok'] else 'no', ver['c1']['divisioni_con_s_sotto_t'], ver['c1']['di'], mf(ver['c1']['delta_medio']), ', '.join(mf(x) for x in ver['c1']['b_s']), ', '.join(mf(x) for x in ver['c1']['b_t'])),
          '| 2. b medio fra 0,40 e 0,60 (0,60-0,65 = pari col v21) | %s | b medio %s; pari col v21: %s; b v21 %s |' % ('SI' if ver['c2']['ok'] else 'no', mf(ver['c2']['b_medio']), ver['c2']['pari_col_v21'], mf(ver['c2']['b_v21'])),
          '| 3. `sezione` entro 2σ (σ = rumore di campionamento) | %s | z medio %s (strumento valido: %s) |' % ('SI' if ver['c3']['ok'] else 'no', mf(ver['c3']['sezione_z'], 1), sv['sezione']),
          '| 4. almeno %d delle altre 7 misure vecchie entro 2σ | %s | dentro: %s; fuori: %s |' % (VECCHIE_ALTRE_MIN, 'SI' if ver['c4']['ok'] else 'no', ', '.join(ver['c4']['dentro']) or '-', ', '.join(ver['c4']['fuori']) or '-'),
          '| 5. sorprese fra 0,40 e 0,60 e indovina-sezione entro 2 errori | %s | avanti %s (%s), indietro %s (%s), indovina-sezione finto %s contro vero %s (differenza %s, errore %s, %s) |' % (
              'SI' if ver['c5']['ok'] else 'no', mf(ver['c5']['avanti']), 'valido' if sv['avanti'] else 'FUORI', mf(ver['c5']['indietro']), 'valido' if sv['indietro'] else 'FUORI', mf(ver['c5']['indovina_finto']),
              mf(ver['c5']['indovina_vero']), mf(ver['c5']['differenza']), mf(ver['c5']['errore']), 'valido' if sv['indovina'] else 'FUORI'),
          '| 6. almeno 2/3 delle misure nuove valide entro 2σ | %s | dentro: %s; fuori: %s; usciti dal verdetto: %s; `lingua` z %s (previsione scritta: fallisce) |' % (
              'SI' if ver['c6']['ok'] else 'no', ', '.join(ver['c6']['dentro']) or '-', ', '.join(ver['c6']['fuori']) or '-', ', '.join(ver['c6']['usciti_dal_verdetto']) or '-', mf(ver['c6']['lingua_z'], 1)), '',
          '## Strumenti e difetti piantati', '', 'Strumenti che vedono il loro difetto (gli altri escono dal verdetto): ' + ', '.join('%s %s' % (k, 'si' if v else 'NO') for k, v in sv.items()) + '.', '',
          'Pagine rimescolate (z medio, in unita\' di rumore): ' + ', '.join('%s %s' % (n, mf(v, 1)) for n, v in ver['difetti']['pagine_rimescolate_z'].items()) + '; indovina-sezione vero %s, pagine rimescolate %s.' % (
              mf(ver['difetti']['indovina_vero']), mf(ver['difetti']['indovina_pagine_rimescolate'])),
          'Meta\' righe di `neu` (riga `dif`): b %s, sorpresa in avanti %s, sorpresa al contrario %s.' % (mf(ver['difetti']['meta_righe_b']), mf(ver['difetti']['meta_righe_avanti']), mf(ver['difetti']['meta_righe_indietro'])), '',
          '## Per divisione', '', '| divisione | riga | b | avanti | indietro | indovina | `sezione` z | pagine tenute fuori |', '|---|---|---|---|---|---|---|---|']
    for k, d in div.items():
        for t, r in d['righe'].items():
            md.append('| %d | %s | %s (%s) | %s | %s | %s | %s | %d |' % (k, t, mf(r['b']), mf(r['b_errore']), mf(r['avanti']), mf(r['indietro']), mf(r['indovina']), mf(r['z'].get('sezione'), 1), d['vero']['pagine_tenute_fuori']))
    md += ['', 'Misure (z medio sulle divisioni nuove, in unita\' di rumore di campionamento) per `s100k30`, `t100` e v21:', '', '| misura | s100k30 | t100 | v21 |', '|---|---|---|---|']
    for n in SMIS.TUTTE:
        md.append('| %s%s | %s | %s | %s |' % (n, ' (nuova)' if n in SMIS.NUOVE else '', mf(ver['z_medi'].get(n), 1), mf(ver['z_medi_t100'].get(n), 1), mf(ver['z_medi_v21'].get(n), 1)))
    if 0 in div and div[0].get('informazione_N_KN_D'):
        md += ['', 'Informazione sulla divisione originale (N e KN usano anche pagine studiate: non vanno nel verdetto): ' + '; '.join(
            '%s N %s, KN %s, D %s' % (t, mf(v['N']), mf(v['KN']), mf(v['D'])) for t, v in div[0]['informazione_N_KN_D'].items()) + '.']
    open(os.path.join(USCITA, 'ia41_sigillato.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
    print('esito: %s' % ver['esito'], flush=True)


# ---------------------------------------------------------------- il programma

def processo_divisione():
    import numpy  # noqa: F401
    import torch  # noqa: F401
    processi = int(os.environ.get('PROCESSI', 2))
    fasi = os.environ.get('FASE41', 'RE')
    os.makedirs(USCITA, exist_ok=True)
    print('ia41, divisione %d: mondo %s, fasi %s, libro (%s)' % (DIV, MONDO, fasi, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    if os.environ.get('RIPRENDI') != '1' and 'E' in fasi:
        azzera_corse(MONDO)
    if 'R' in fasi:
        fase_R(MONDO, processi)
    if 'E' in fasi:
        fase_E(MONDO, processi)


def lancia(div, fase, processi):
    env = dict(os.environ, DIV41=str(div), FASE41=fase, PROCESSI=str(processi))
    return subprocess.Popen([sys.executable, os.path.abspath(__file__)], env=env)


def driver():
    """Un processo per divisione. Le reti delle divisioni nuove si riaddestrano IN PARALLELO (circa 13 minuti ciascuna, un processo ciascuna) mentre la divisione 0 fa i suoi libri con gli altri processi;
    poi le divisioni nuove fanno i loro libri e giudici una dopo l'altra, con tutti i processi."""
    totale = int(os.environ.get('PROCESSI', 8))
    fasi = os.environ.get('FASI', 'RES')
    print('ia41: divisioni %s, processi %d, libro (%s)' % (DIVISIONI, totale, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    nuove = [k for k in DIVISIONI if k != 0]
    if 'R' in fasi or 'E' in fasi:
        proc = []
        if 0 in DIVISIONI:
            proc.append((0, lancia(0, ''.join(f for f in 'RE' if f in fasi), max(1, totale - len(nuove)))))
        if 'R' in fasi:
            for k in nuove:
                proc.append((k, lancia(k, 'R', 1)))
        for k, p in proc:
            if p.wait() != 0:
                raise SystemExit('divisione %d: uscita %d' % (k, p.returncode))
        if 'E' in fasi:
            for k in nuove:
                p = lancia(k, 'E', totale)
                if p.wait() != 0:
                    raise SystemExit('divisione %d (E): uscita %d' % (k, p.returncode))
    if 'S' in fasi:
        fase_S(MONDO)


def main():
    if DIV is not None:
        processo_divisione()
    else:
        driver()


if __name__ == '__main__':
    main()
