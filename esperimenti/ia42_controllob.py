# -*- coding: utf-8 -*-
"""Esperimento IA42 (ia42): il controllo B, con un libro v21 come "vero". E' l'ULTIMO della serie.

Domanda: i voti dell'IA sul Voynich (IA41: b 0,66 su pagine mai viste; `dispersione` e `vicine` fuori da 2σ) sono un limite del metodo con cosi' poco testo, o qualcosa di proprio del Voynich? Il controllo positivo
che manca da IA33: lo stesso programma di IA41 su un testo di cui conosciamo la regola, un libro del v21 (il numero 13), fatto con parole e impaginazione del Voynich (limite dichiarato).
Il "mondo" `v21w`: il testo vero e' il libro v21 n. `V21_VERO42` (13); disposizione = quella del libro v21 stesso (le sue righe e i suoi inizi di paragrafo: il v21 rimette le righe da se', 180 pagine su 207 hanno un numero
di righe diverso dal Voynich), con foglio, sezione, lingua e mano di ogni pagina presi dal Voynich. Le stesse quattro divisioni nuove dei fogli (`SEME_FOGLI32` 4101-4104: i fogli sono gli stessi di IA41); per ognuna si
rifanno rete `Cb` (stesso seme, stessa taglia) e tabelle per sezione sui fogli d'addestramento di QUEL libro; manopole identiche (punto di IA35: `t100`; `s100k30` = `a_sez` 1, K 30). Righe: `t100`, `s100k30`, `neu` e
gli altri NOVE libri v21 come gemelli (`gem`: stessa regola, altri semi; il tetto di un imitatore perfetto). Strumenti: b, indovina-sezione, `sezione`, le 7 misure vecchie e le 5 nuove valide di IA41 (niente sorprese
ne' `lingua`: in IA41 non vedevano il loro difetto). Difetto piantato: pagine rimescolate. Riusa il codice di IA41 (`sigillo_*`, `freqsez_*`). Preregistrazione: preregistrazioni/ia42.md.

Struttura (un processo per divisione, `SEME_FOGLI32` si legge all'avvio; il programma si rilancia da solo):
  fase R   (per divisione) cartella separata `dati/cache/ia42/div<k>/`, rete e tabelle solo sui fogli d'addestramento del libro v21 in quella divisione (controllo dei fogli come in IA41)
  fase E   (per divisione) libri delle tre righe, b, indovina-sezione, misure, difetto piantato -> `esito_div.json` (solo numeri)
  fase G   (per divisione, SOLO PROVE e non in corsa) solo i gemelli: b, indovina-sezione, misure e difetto, senza reti ne' libri scritti
  fase S   (una volta) criteri scritti prima, esito, `risultati/ia42_controllob.{md,json}`

    nohup bash strumenti/coda.sh ia42 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia42" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella nel repo> CACHE42=<cartella nel repo> python esperimenti/ia42_controllob.py     (prova: i libri "v21" sono catene di Markov sul latino)

Variabili nuove (valori senza virgole e senza due punti): CACHE42, N_LIBRI42 (8), DIVISIONI42 (cifre, predefinito 1234), V21_VERO42 (13), SEMI42, ESTRAZIONI42 (60), PUNTO_BASE42 (ia35 o stress: stress solo con
SOLO_CONTROLLI=1), DIV42 e FASE42 (interne).
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
_SEMI_FOGLI = {1: 4101, 2: 4102, 3: 4103, 4: 4104}
_DIV = os.environ.get('DIV42')
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

NOME = 'ia42_controllob'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE42 = os.environ.get('CACHE42', os.path.join(USCITA, 'ia42_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia42'))
CACHE35_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia35')
MONDO = 'v21w'
V21_VERO = int(os.environ.get('V21_VERO42', 13))
os.environ['CACHE26'] = os.path.join(CACHE42, 'div%d' % (DIV if DIV is not None else 1), 'banco')     # il banco di IA26 scrive qui, per divisione: mai nelle cache di IA26-IA41
os.environ.setdefault('CHUNK26', '500')
os.environ.setdefault('S_GRU_MONDO26', '6')
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_misure as RM  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import sezione_rete as SR  # noqa: E402
import prudente_scrittura as PW  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402
import freqsez_scrittura as FW  # noqa: E402
import freqsez_lavori as FL  # noqa: E402
import sigillo_misure as SMIS  # noqa: E402
import sigillo_giudici as SGIU  # noqa: E402


# ---------------------------------------------------------------- il mondo `v21w`: un libro v21 come testo vero

def righe_v21w(base, k=None):
    """Le righe (dizionari come `ia07.libro_vero()`) del libro v21 n. `k`: le sue righe e i suoi inizi di paragrafo; foglio, sezione, lingua e mano di ogni pagina dal libro `base` (il Voynich: solo la disposizione per pagina)."""
    k = V21_VERO if k is None else k
    rows = I7.libro_riferimento_A('b', k)
    attr = OrderedDict()
    for x in base:
        attr.setdefault(x['pagina'], (x['foglio'], x['sezione'], x['lingua'], x['mano']))
    out = []
    for p, (fog, sez, lin, man) in attr.items():
        for ini, ws in rows.get(p, []):
            if ws:
                out.append(dict(pagina=p, foglio=fog, sezione=sez, lingua=lin, mano=man, ini=bool(ini), parole=[''.join(w) for w in ws]))
    for i, x in enumerate(out):
        dopo = out[i + 1] if i + 1 < len(out) else None
        x['fin'] = dopo is None or dopo['pagina'] != x['pagina'] or dopo['ini']
    return out


_precedente = RT.righe_sintetiche


def _righe_sintetiche(base, nome, gemello=False):
    if nome != MONDO:
        return _precedente(base, nome, gemello)
    return righe_v21w(base)


if MONDO not in RT.MONDI:
    RT.MONDI[MONDO] = dict(gen='v21w', par=dict(libro=V21_VERO))
RT.righe_sintetiche = _righe_sintetiche

_ATTIVO = {}
N_LIBRI = int(os.environ.get('N_LIBRI42', 8))
DIVISIONI = [int(x) for x in os.environ.get('DIVISIONI42', '1234') if x.isdigit() and int(x) in _SEMI_FOGLI]
SEMI = os.environ.get('SEMI42', '')
PUNTO_BASE = os.environ.get('PUNTO_BASE42', 'ia35')
V21_NOMI = ['V21:%d' % k for k in range(13, 23)]
GEMELLI = [n for n in V21_NOMI if n != 'V21:%d' % V21_VERO]
NOMI_GEM = [n for n in GEMELLI]

# ---- criteri e soglie scritti nella preregistrazione prima di ogni numero sul libro v21 scelto come vero e sul Voynich
FASCIA = (0.40, 0.60)               # validita': i gemelli (b medio sulle quattro divisioni)
STESSO_VOTO = (0.61, 0.71)          # b medio di t100 e s100k30 sulle quattro divisioni: "stesso voto" del Voynich (IA41: 0,66)
VOYNICH_PIU_DIFFICILE = 0.58        # 0,58 o meno: "Voynich piu' difficile"
SOGLIA_SIGMA = 2.0
CROLLO_IND = 0.25                   # come IA41: l'indovina-sezione "vede" le pagine rimescolate se l'accuratezza cala di almeno cosi' (assoluto)
PREVISIONE_B = (0.61, 0.68)         # previsione di Fable, scritta prima: "stesso voto" con b fra 0,61 e 0,68; dispersione fuori anche qui, vicine dentro
# lo stato delle tre misure di riferimento sul Voynich in IA41 (z medio di `s100k30` sulle quattro divisioni nuove): fuori da 2 sigma o no
VOYNICH_Z = OrderedDict([('sezione', -1.53), ('dispersione', -2.22), ('vicine', -2.17)])
MISURE_42 = tuple(n for n in SMIS.TUTTE if n != 'lingua')         # 7 vecchie + sezione + 5 nuove (lingua esce: in IA41 non vedeva il suo difetto)
VECCHIE_ALTRE = tuple(n for n in SMIS.VECCHIE if n != 'sezione')
NUOVE_VALIDE = tuple(n for n in SMIS.NUOVE if n != 'lingua')
# punto di sviluppo (solo con SOLO_CONTROLLI=1 e PUNTO_BASE42=stress): un punto moderato scritto a mano al posto del punto di IA35, che c'e' solo in `dati/cache`
VALORI_STRESS2 = OrderedDict([('T_eol', 0.8), ('w_cont', 3.0), ('w_tri', 3.0), ('w_quad', 3.0), ('s', 0.8), ('w_uni', 1.0), ('w_bi', 1.0), ('b_nuove', -0.8), ('w_pag', 0.3)])


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
    RM.prepara(mondo, cart42(mondo), nomi)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia36_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro42, da_fare), 1):
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
        I7.scrivi_file(t, p + '.tmp', 'ia42, libro %s %d, mondo %s' % (tipo, i, RM._W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def cubo15(u14, a_sez=0.0):
    return np.concatenate([np.asarray(u14, float), [U_PIATTO + 0.8 * a_sez]])


def nome_libro(tipo, i):
    return 'tar:%s:%d' % (tipo, i)


IDX_CONTI = (6, 7, 8, 10, 11)
U_PIATTO = 0.2


def cart42(mondo, *p):
    return os.path.join(CACHE42, 'div%d' % (DIV if DIV is not None else 1), mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia42_corse_div%d_%s.jsonl' % (DIV if DIV is not None else 1, mondo))


def ident(a):
    if a[0] == 'B35':
        return 'B35|%s' % a[1]
    if a[0] == 'libro42':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'SIG':
        return 'SIG|%s' % a[1]
    return '|'.join(str(x) for x in a)


def punto_base(mondo):
    """Il punto di IA35 sul Voynich (cubo a 14: solo i numeri delle manopole, `ciclo_esito.json`): le manopole sono identiche in tutti i mondi. Con SOLO_CONTROLLI=1 e PUNTO_BASE42=stress un punto moderato scritto a mano."""
    p = os.path.join(CACHE35_ORIG, 'vero', 'ciclo_esito.json')
    if not SOLO_CONTROLLI and os.path.exists(p):
        return np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float)[:14]
    if SOLO_CONTROLLI and PUNTO_BASE == 'stress':
        return np.array(OS.cubo_da_valori(VALORI_STRESS2), float)
    raise RuntimeError('manca il punto di IA35 (dati/cache/ia35/vero/ciclo_esito.json)')


def righe(u14):
    """Le tre righe scritte dall'imitatore (fissate prima): spec = ['L', cubo a 15, K]. I gemelli non si scrivono: sono gli altri libri v21."""
    R = OrderedDict()
    R['s100k30'] = dict(descr='punto di IA35 con a_sez 1, ripiego K 30', spec=['L', list(map(float, cubo15(u14, 1.0))), 30])
    R['t100'] = dict(descr='punto di IA35 (il "prima")', spec=['L', list(map(float, cubo15(u14, 0.0))), None])
    R['neu'] = dict(descr='manopole neutre (rete sola)', spec=['L', list(map(float, FW.neutro_cubo37())), None])
    return R


# ---------------------------------------------------------------- lavori

def _stato():
    """I giudici nuovi della divisione, costruiti una volta per processo (classificatore di sezione sulle pagine studiate; il modello di sorpresa non si usa)."""
    if 'giudici' not in RM._W:
        c = I7.contesto_A()
        f_add, f_val, f_fuori = RD.divisione_fogli()
        RM._W['giudici'] = SGIU.Giudici(c, f_add, f_val, f_fuori)
    return RM._W['giudici']


def lavoro_SIG(tipo, nomi):
    """Indovina-sezione e le misure (sulle sole pagine tenute fuori) di un insieme di libri (nomi del banco). Niente sorprese."""
    inizio = time.time()
    G = _stato()
    libri = [B.rows_testo(n) for n in nomi]
    out = OrderedDict([('lavoro', 'SIG|%s' % tipo), ('tipo', tipo), ('nomi', nomi)])
    out['indovina'] = [G.acc_indovina(r) for r in libri]
    out['misure'] = [SMIS.misure(r, G.pag_ho) for r in libri]
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_RUM():
    """Il vero tenuto fuori (il libro v21 scelto): misure, rumore di campionamento, accuratezza di indovina-sezione, pagine."""
    inizio = time.time()
    G = _stato()
    c = G.c
    out = OrderedDict([('lavoro', 'RUM')])
    out['vero'] = SMIS.misure(c['vere'], G.pag_ho)
    out['rumore'] = SMIS.rumore(c['vere'], list(c['ids']), estrazioni=int(os.environ.get('ESTRAZIONI42', 60)))
    out['indovina_vero'] = G.acc_indovina(c['vere'])
    out['pagine_tenute_fuori'] = len(G.pag_ho)
    out['pagine_indovinabili'] = len(G.pagine_indovinabili())
    out['sezioni_classi'] = G.classi
    out['fogli'] = [len(RD.divisione_fogli()[i]) for i in range(3)]
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_DEFA(nomi):
    """Difetto piantato `pagine_rimescolate` sui libri `nomi`: misure e indovina-sezione sulle sole pagine tenute fuori."""
    inizio = time.time()
    G = _stato()
    libri = [SMIS.pagine_rimescolate(B.rows_testo(n), seme=4141 + i) for i, n in enumerate(nomi)]
    out = OrderedDict([('lavoro', 'DEFA'), ('misure', [SMIS.misure(r, G.pag_ho) for r in libri]), ('indovina', [G.acc_indovina(r) for r in libri])])
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro42(args):
    try:
        if args[0] == 'libro42':
            return scrivi_libro40(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'SIG':
            return lavoro_SIG(args[1], args[2])
        if args[0] == 'RUM':
            return lavoro_RUM()
        if args[0] == 'DEFA':
            return lavoro_DEFA(args[1])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3] if not isinstance(a, (list, dict)))), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = FL.lavoro_banco37(args)                                           # B35 (giudice b mediato)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


def stub_riferimento(mondo):
    """`rifare_misure.prepara` cerca il riferimento del banco: il controllo B non lo usa (niente N, KN, D, R_rel, obiettivo), se ne scrive uno vuoto."""
    d_banco = os.path.join(CACHE42, 'div%d' % (DIV if DIV is not None else 1), 'banco', mondo)
    os.makedirs(d_banco, exist_ok=True)
    rp = os.path.join(d_banco, 'riferimento.json')
    if not os.path.exists(rp):
        json.dump(OrderedDict([('nota', 'vuoto: il controllo B non usa il riferimento del banco')]), open(rp, 'w', encoding='utf-8', newline='\n'))


# ---------------------------------------------------------------- R: la divisione (rete e tabelle solo sui fogli d'addestramento di questa divisione, sul libro v21)

def fase_R(mondo, processi):
    """Cartella separata per divisione. La rete `Cb` si riaddestra (stesso seme di IA35) sui fogli d'addestramento di QUESTA divisione, sul testo del libro v21; si controlla che `pieno.pt` abbia esattamente i fogli della divisione.
    Il riferimento del banco non serve (non ci sono N, KN, D, R_rel ne' l'obiettivo): se ne scrive uno vuoto perche' `rifare_misure.prepara` lo cerca."""
    os.makedirs(cart42(mondo), exist_ok=True)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    stub_riferimento(mondo)
    pt = cart42(mondo, 'rete_C', 'pieno.pt')
    if not os.path.exists(pt):
        print('divisione %d: addestro la rete Cb sui %d fogli d\'addestramento del libro v21 n. %d (validazione %d, tenuti fuori %d)' % (DIV, len(f_add), V21_VERO, len(f_val), len(f_fuori)), flush=True)
        SR.addestra_pieno35(cart42(mondo, 'rete_C'), cond=True, var=SR.VARIANTI['Cb'], messaggi=lambda s: print('[addestra] %s' % s, flush=True))
    import torch
    d = torch.load(pt, weights_only=False)
    assert list(d['f_add']) == list(f_add) and list(d['f_val']) == list(f_val) and list(d['f_fuori']) == list(f_fuori), 'i fogli della rete non sono quelli della divisione %d' % DIV
    nat_p = cart42(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    controllo = OrderedDict([('divisione', DIV), ('seme_fogli', RD.SEME_FOGLI32), ('libro_v21', V21_VERO), ('fogli', [len(f_add), len(f_val), len(f_fuori)]), ('fogli_rete_uguali', True), ('tenuti_fuori', list(f_fuori))])
    json.dump(controllo, open(cart42(mondo, 'controllo_divisione.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('divisione %d: seme fogli %d, fogli %s; la rete ha esattamente questi fogli' % (DIV, RD.SEME_FOGLI32, controllo['fogli']), flush=True)


# ---------------------------------------------------------------- E (e G): libri, b, giudice di sezione, misure, difetto

def fase_E(mondo, processi, solo_gemelli=False):
    stub_riferimento(mondo)
    os.makedirs(cart42(mondo), exist_ok=True)
    R = righe(punto_base(mondo)) if not solo_gemelli else OrderedDict()
    tipi = list(R)
    nomi = [nome_libro(t, i) for t in tipi for i in range(1, N_LIBRI + 1)]
    attiva_main(mondo, nomi + NOMI_GEM)
    fatte = fatte_di(mondo)
    if R:
        libri = [('libro42', t, i, d['spec'], seme_str('ia42esame' + SEMI, DIV, t, i)) for t, d in R.items() for i in range(1, N_LIBRI + 1)]
        print('== divisione %d: %d libri da scrivere' % (DIV, len(libri)), flush=True)
        esegui(mondo, nomi + NOMI_GEM, libri, processi, fatte)
    gruppi = [(t, [nome_libro(t, i) for i in range(1, N_LIBRI + 1)]) for t in tipi] + [('gem', NOMI_GEM)]
    lavori = [('B35', t, ns, seme_str('b35' + SEMI, DIV, t) % 1000) for t, ns in gruppi]
    lavori += [('SIG', t, ns) for t, ns in gruppi]
    difetto = [nome_libro('s100k30', i) for i in range(1, min(4, N_LIBRI) + 1)] if R else NOMI_GEM[:4]
    lavori += [('RUM',), ('DEFA', difetto)]
    lavori = sorted(lavori, key=lambda a: {'RUM': 0, 'SIG': 1, 'DEFA': 1, 'B35': 2}.get(a[0], 3))
    print('== divisione %d: %d lavori del banco' % (DIV, len(lavori)), flush=True)
    esegui(mondo, nomi + NOMI_GEM, lavori, processi, fatte)
    return riassunto_divisione(mondo, gruppi, nomi + NOMI_GEM, solo_gemelli)


def _errore_b(b):
    nb = len(b.get('per_libro') or [])
    s = b.get('sd_libri') or 0.0
    return math.sqrt(s * s / max(nb, 1) + (b.get('nullo_sd') or 0.0) ** 2)


def riassunto_divisione(mondo, gruppi, nomi, solo_gemelli=False):
    attiva_main(mondo, nomi)
    ok = [r for r in leggi_corse(percorso_corse(mondo)) if not r.get('errore')]
    sig = {r['tipo']: r for r in ok if str(r.get('lavoro', '')).startswith('SIG|')}
    bj = {r['lavoro'][4:]: r for r in ok if str(r.get('lavoro', '')).startswith('B35|')}
    rum = next((r for r in ok if r.get('lavoro') == 'RUM'), None)
    defa = next((r for r in ok if r.get('lavoro') == 'DEFA'), None)
    if rum is None:
        raise RuntimeError('manca il lavoro RUM (rumore e vero tenuto fuori)')
    sd = {n: (rum['rumore'][n] or {}).get('sd') for n in SMIS.TUTTE}

    def media(x):
        x = [a for a in x if a is not None]
        return float(np.mean(x)) if x else None

    def z_misure(lista):
        out = OrderedDict()
        for n in MISURE_42:
            v = [m.get(n) for m in lista if m.get(n) is not None]
            if v and rum['vero'].get(n) is not None and sd.get(n):
                out[n] = (float(np.mean(v)) - rum['vero'][n]) / sd[n]
        return out
    righe_out = OrderedDict()
    for t, _ns in gruppi:
        s, b = sig.get(t), bj.get(t)
        if s is None:
            continue
        sdb = float(np.std([a for a in (b or {}).get('per_libro', [])], ddof=1)) if b and len(b.get('per_libro') or []) > 1 else None
        righe_out[t] = OrderedDict([('n', len(s['nomi'])), ('b', (b or {}).get('auc')), ('b_errore', _errore_b(b) if b else None), ('b_sd_libri', sdb), ('indovina', media(s['indovina'])),
                                    ('z', z_misure(s['misure']))])
    difetti = OrderedDict()
    if defa:
        difetti['pagine_rimescolate'] = OrderedDict([('z', z_misure(defa['misure'])), ('indovina', media(defa['indovina']))])
    out = OrderedDict([('divisione', DIV), ('seme_fogli', RD.SEME_FOGLI32), ('libro_v21', V21_VERO), ('solo_gemelli', bool(solo_gemelli)), ('righe', righe_out), ('difetti', difetti),
                       ('vero', OrderedDict([('indovina', rum['indovina_vero']), ('misure', OrderedDict((n, rum['vero'].get(n)) for n in MISURE_42)), ('rumore', OrderedDict((n, sd[n]) for n in MISURE_42)),
                                             ('pagine_tenute_fuori', rum['pagine_tenute_fuori']), ('pagine_indovinabili', rum['pagine_indovinabili']), ('sezioni_classi', rum['sezioni_classi']), ('fogli', rum['fogli'])]))])
    json.dump(out, open(cart42(mondo, 'esito_div%s.json' % ('_gemelli' if solo_gemelli else '')), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return out


# ---------------------------------------------------------------- S: criteri, esito, sintesi

def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def _m(x):
    x = [a for a in x if a is not None]
    return float(np.mean(x)) if x else None


def valuta(divs):
    """Criteri scritti prima sulle divisioni `divs` (lista di esito_div). Gli strumenti che non vedono il loro difetto ESCONO dal verdetto: la loro riga dice "fuori dal verdetto" e non conta ne' come passata ne' come bocciata. -> dict."""
    out = OrderedDict()
    s = [d['righe']['s100k30'] for d in divs if 's100k30' in d['righe']]
    t = [d['righe']['t100'] for d in divs if 't100' in d['righe']]
    gem = [d['righe']['gem'] for d in divs]
    # ---- strumenti: il difetto piantato (pagine rimescolate) e' visto?
    z_dif = OrderedDict((n, _m([d['difetti'].get('pagine_rimescolate', {}).get('z', {}).get(n) for d in divs])) for n in MISURE_42)
    ind_vero = _m([d['vero']['indovina'] for d in divs])
    ind_dif = _m([d['difetti'].get('pagine_rimescolate', {}).get('indovina') for d in divs])
    visto = OrderedDict()
    for n in ('sezione', 'vicine'):
        visto[n] = bool(z_dif.get(n) is not None and abs(z_dif[n]) >= SMIS.SOGLIA_DIFETTO)
    visto['indovina'] = bool(ind_vero is not None and ind_dif is not None and ind_dif <= ind_vero - CROLLO_IND)
    out['strumenti_visti'] = visto
    out['difetto'] = OrderedDict([('z', z_dif), ('indovina_vero', ind_vero), ('indovina_rimescolate', ind_dif)])
    # ---- validita': i gemelli fra 0,40 e 0,60 e le pagine rimescolate viste da sezione e indovina-sezione
    bg = _m([x['b'] for x in gem])
    out['gemelli'] = OrderedDict([('b_medio', bg), ('b_per_divisione', [x['b'] for x in gem]), ('in_fascia', bool(bg is not None and FASCIA[0] <= bg <= FASCIA[1]))])
    out['valido'] = bool(out['gemelli']['in_fascia'] and visto['sezione'] and visto['indovina'])
    # ---- b dell'imitatore
    bs, bt = _m([x['b'] for x in s]), _m([x['b'] for x in t])
    bn = _m([d['righe']['neu']['b'] for d in divs if 'neu' in d['righe']])
    bm = _m([x['b'] for x in s + t])
    out['b'] = OrderedDict([('s100k30', bs), ('t100', bt), ('neu', bn), ('medio', bm), ('s100k30_per_divisione', [x['b'] for x in s]), ('t100_per_divisione', [x['b'] for x in t]),
                            ('previsione', 'stesso voto, b fra %.2f e %.2f' % PREVISIONE_B), ('previsione_ok', bool(bm is not None and PREVISIONE_B[0] <= bm <= PREVISIONE_B[1]))])
    if not out['valido']:
        esito = 'non valido (gemelli in fascia: %s; sezione vede il difetto: %s; indovina-sezione vede il difetto: %s): il controllo non si legge' % (out['gemelli']['in_fascia'], visto['sezione'], visto['indovina'])
    elif bm is None:
        esito = 'non deciso (nessuna riga scritta)'
    elif STESSO_VOTO[0] <= bm <= STESSO_VOTO[1]:
        esito = 'STESSO VOTO: sul libro v21 (regola nota) l\'imitatore prende lo stesso b che sul Voynich (0,66): limite del metodo con cosi\' poco testo, niente di proprio del Voynich'
    elif bm <= VOYNICH_PIU_DIFFICILE:
        esito = 'VOYNICH PIU\' DIFFICILE: sul libro v21 l\'imitatore prende un b molto piu\' basso che sul Voynich (0,66): il Voynich ha qualcosa che il testo a regole non ha e la rete non prende'
    else:
        esito = 'NON DECISO: b medio fra 0,58 e 0,61 o sopra 0,71'
    out['esito'] = esito
    # ---- le tre misure di riferimento: fuori da 2 sigma anche qui?
    zs = OrderedDict((n, _m([x['z'].get(n) for x in s])) for n in MISURE_42)
    zt = OrderedDict((n, _m([x['z'].get(n) for x in t])) for n in MISURE_42)
    zg = OrderedDict((n, _m([x['z'].get(n) for x in gem])) for n in MISURE_42)
    out['z_s100k30'], out['z_t100'], out['z_gemelli'] = zs, zt, zg
    mis = OrderedDict()
    for n in ('dispersione', 'vicine', 'sezione'):
        valido_m = visto.get(n, True)
        z = zs.get(n)
        qui_fuori = bool(z is not None and abs(z) > SOGLIA_SIGMA)
        voy_fuori = abs(VOYNICH_Z[n]) > SOGLIA_SIGMA
        if not valido_m:
            lettura = 'fuori dal verdetto (non vede il suo difetto)'
        elif z is None:
            lettura = 'non calcolabile'
        elif qui_fuori:
            lettura = 'fuori da 2σ anche qui: difetto del metodo'
        elif voy_fuori:
            lettura = 'dentro qui e fuori sul Voynich: proprio del Voynich'
        else:
            lettura = 'dentro qui e dentro sul Voynich'
        mis[n] = OrderedDict([('z_qui', z), ('z_voynich_ia41', VOYNICH_Z[n]), ('z_gemelli', zg.get(n)), ('valida', valido_m), ('lettura', lettura)])
    out['misure_riferimento'] = mis
    out['previsione_misure'] = OrderedDict([('dispersione_fuori_anche_qui', bool(zs.get('dispersione') is not None and abs(zs['dispersione']) > SOGLIA_SIGMA)),
                                            ('vicine_dentro', (bool(zs.get('vicine') is not None and abs(zs['vicine']) <= SOGLIA_SIGMA) if visto.get('vicine', True) else None))])
    fuori = [n for n in MISURE_42 if zs.get(n) is not None and abs(zs[n]) > SOGLIA_SIGMA and visto.get(n, True)]
    out['altre_misure_fuori_qui'] = [n for n in fuori if n not in ('dispersione', 'vicine', 'sezione')]
    return out


def fase_S(mondo):
    os.makedirs(USCITA, exist_ok=True)
    div = OrderedDict()
    for k in DIVISIONI:
        p = os.path.join(CACHE42, 'div%d' % k, mondo, 'esito_div.json')
        if os.path.exists(p):
            div[k] = json.load(open(p, encoding='utf-8'), object_pairs_hook=OrderedDict)
    if len(div) < 2:
        raise SystemExit('servono almeno due divisioni per la sintesi (trovate %d)' % len(div))
    ver = valuta(list(div.values()))
    out = OrderedDict([('esperimento', NOME), ('mondo', mondo), ('libro_v21', V21_VERO), ('divisioni', list(div)), ('esito', ver['esito']), ('verdetto', ver), ('per_divisione', div)])
    json.dump(out, open(os.path.join(USCITA, 'ia42_controllob.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    sv = ver['strumenti_visti']
    md = ['# IA42 (ia42) — Controllo B: un libro v21 come "vero"', '', 'Preregistrazione: `preregistrazioni/ia42.md`. Il "vero" e\' il libro v21 n. %d (con parole e impaginazione del Voynich: limite dichiarato); gemelli = gli altri nove. Solo numeri e aggregati.' % V21_VERO, '',
          '**Esito: %s.**' % ver['esito'], '',
          '## Validita\'', '', '- Gemelli (b medio sulle divisioni %s): %s, in fascia 0,40-0,60: %s; per divisione %s.' % (', '.join(map(str, div)), mf(ver['gemelli']['b_medio']), ver['gemelli']['in_fascia'], ', '.join(mf(x) for x in ver['gemelli']['b_per_divisione'])),
          '- Pagine rimescolate (difetto piantato): `sezione` z %s (vista: %s), `vicine` z %s (vista: %s); indovina-sezione vero %s, rimescolate %s (vista: %s).' % (
              mf(ver['difetto']['z'].get('sezione'), 1), sv['sezione'], mf(ver['difetto']['z'].get('vicine'), 1), sv['vicine'], mf(ver['difetto']['indovina_vero']), mf(ver['difetto']['indovina_rimescolate']), sv['indovina']),
          '- Controllo valido: %s.' % ver['valido'], '',
          '## b dell\'imitatore sul libro v21', '', '| riga | b medio | per divisione |', '|---|---|---|',
          '| s100k30 | %s | %s |' % (mf(ver['b']['s100k30']), ', '.join(mf(x) for x in ver['b']['s100k30_per_divisione'])), '| t100 | %s | %s |' % (mf(ver['b']['t100']), ', '.join(mf(x) for x in ver['b']['t100_per_divisione'])),
          '| neu | %s | |' % mf(ver['b']['neu']), '| gemelli (altri libri v21) | %s | %s |' % (mf(ver['gemelli']['b_medio']), ', '.join(mf(x) for x in ver['gemelli']['b_per_divisione'])), '',
          'b medio di `t100` e `s100k30`: **%s** (sul Voynich in IA41: 0,66). Previsione scritta (stesso voto, 0,61-0,68): %s.' % (mf(ver['b']['medio']), 'confermata' if ver['b']['previsione_ok'] else 'non confermata'), '',
          '## Le tre misure di riferimento (z medio di `s100k30`, in unita\' di rumore di campionamento)', '', '| misura | qui | Voynich (IA41) | gemelli | lettura |', '|---|---|---|---|---|']
    for n, v in ver['misure_riferimento'].items():
        md.append('| %s | %s | %s | %s | %s |' % (n, mf(v['z_qui'], 1), mf(v['z_voynich_ia41'], 1), mf(v['z_gemelli'], 1), v['lettura']))
    md += ['', 'Previsione scritta: `dispersione` fuori anche qui: %s; `vicine` dentro: %s.' % (ver['previsione_misure']['dispersione_fuori_anche_qui'], ver['previsione_misure']['vicine_dentro']), '',
           'Altre misure fuori da 2σ per `s100k30`: %s.' % (', '.join(ver['altre_misure_fuori_qui']) or 'nessuna'), '', '## Tutte le misure (z medio)', '', '| misura | s100k30 | t100 | gemelli |', '|---|---|---|---|']
    for n in MISURE_42:
        md.append('| %s%s | %s | %s | %s |' % (n, ' (nuova)' if n in SMIS.NUOVE else '', mf(ver['z_s100k30'].get(n), 1), mf(ver['z_t100'].get(n), 1), mf(ver['z_gemelli'].get(n), 1)))
    md += ['', '## Per divisione', '', '| divisione | riga | b | indovina-sezione | `sezione` z | pagine tenute fuori |', '|---|---|---|---|---|---|']
    for k, d in div.items():
        for t, r in d['righe'].items():
            md.append('| %d | %s | %s (%s) | %s | %s | %d |' % (k, t, mf(r['b']), mf(r['b_errore']), mf(r['indovina']), mf(r['z'].get('sezione'), 1), d['vero']['pagine_tenute_fuori']))
    open(os.path.join(USCITA, 'ia42_controllob.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
    print('esito: %s' % ver['esito'], flush=True)


# ---------------------------------------------------------------- il programma

def processo_divisione():
    import numpy  # noqa: F401
    import torch  # noqa: F401
    processi = int(os.environ.get('PROCESSI', 2))
    fasi = os.environ.get('FASE42', 'RE')
    os.makedirs(USCITA, exist_ok=True)
    print('ia42, divisione %d: mondo %s (libro v21 n. %d), fasi %s, libro (%s)' % (DIV, MONDO, V21_VERO, fasi, 'controlli: latino, libri "v21" = Markov' if SOLO_CONTROLLI else 'Voynich: layout; testo = v21'), flush=True)
    if os.environ.get('RIPRENDI') != '1' and ('E' in fasi or 'G' in fasi):
        azzera_corse(MONDO)
    if 'R' in fasi:
        fase_R(MONDO, processi)
    if 'E' in fasi:
        fase_E(MONDO, processi)
    if 'G' in fasi:
        fase_E(MONDO, processi, solo_gemelli=True)


def lancia(div, fase, processi):
    env = dict(os.environ, DIV42=str(div), FASE42=fase, PROCESSI=str(processi))
    return subprocess.Popen([sys.executable, os.path.abspath(__file__)], env=env)


def driver():
    """Un processo per divisione. Le reti delle quattro divisioni si riaddestrano IN PARALLELO (un processo ciascuna, circa 13 minuti); poi le divisioni fanno libri, giudici e misure una dopo l'altra con tutti i processi."""
    totale = int(os.environ.get('PROCESSI', 8))
    fasi = os.environ.get('FASI', 'RES')
    print('ia42: divisioni %s, processi %d, libro v21 n. %d' % (DIVISIONI, totale, V21_VERO), flush=True)
    if 'R' in fasi:
        proc = [(k, lancia(k, 'R', 1)) for k in DIVISIONI]
        for k, p in proc:
            if p.wait() != 0:
                raise SystemExit('divisione %d (R): uscita %d' % (k, p.returncode))
    if 'E' in fasi or 'G' in fasi:
        for k in DIVISIONI:
            p = lancia(k, ''.join(f for f in 'EG' if f in fasi), totale)
            if p.wait() != 0:
                raise SystemExit('divisione %d: uscita %d' % (k, p.returncode))
    if 'S' in fasi:
        fase_S(MONDO)


def main():
    if DIV is not None:
        processo_divisione()
    else:
        driver()


if __name__ == '__main__':
    main()
