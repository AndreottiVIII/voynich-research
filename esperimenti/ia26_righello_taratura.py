# -*- coding: utf-8 -*-
"""Esperimento IA26 (ia26): il righello e la taratura.

Domanda (revisione di Fable, proposta C1, e proposta 1 del coordinatore): le frasi "nessun imitatore porta al vero..." di ia16 e ia20-ia24 parlano del Voynich
o del limite di ogni imitatore piccolo? Due parti.
  Parte 1, il banco ("il righello"): un'unica batteria di misure (undici) e di giudici (sei, due dei quali nuovi: N e KN) applicata a tutti i testi che il repo ha
  gia' (vero, v21, Timm e Schinner, Naibbe, libri degli imitatori di ia07/ia16/ia20/ia22/ia23/ia24, cifrari e lingue di ia14, controlli). Esce un profilo per testo e
  una distanza dal vero, con pesi uguali, standardizzata sulla variabilita' del vero. Il metro "vero contro vero": meta' dei fogli contro l'altra meta', molte volte,
  per ogni misura e per ogni giudice: l'intervallo entro cui un testo e' "indistinguibile dal vero".
  Parte 2, la taratura: M1 e M5 (ia20) ed E2 (ia22) si riaddestrano su testi di cui si conosce la regola (catena di Markov di ordine 2, eco e contatto di ia22, tema +
  eco + contatto di ia23, e uno con tema, eco e contatto portati ai valori del Voynich) e si misurano con lo stesso banco: su un processo noto e paragonabile al Voynich,
  quanto "lontani" restano gli imitatori?
Preregistrazione: preregistrazioni/ia26.md. Moduli di supporto: righello_banco.py (il banco, riusabile: `python esperimenti/righello_banco.py profilo FILE`),
righello_giudici.py (giudici N e KN), righello_testi.py (catalogo dei testi e mondi sintetici).
Importa, senza modificarli, ia07 (libro vero, pieghe per foglio, giudici del paper, giudice A), ia20 e ia22 (addestramento e scrittura di M1, M5, E2), imitatore_misure (K,
copia netta, Λ, D, contatto), aprire_parole (bordi), rifarlo_ritocchi (forma), ia02 e ia03 (R_rel e k90), cifrari_procedimenti (cifrari e lingue di ia14), echi_modelli e
pagina_modelli (testi sintetici).

Fasi (variabile FASI, predefinita BCTS):
  B  il banco sul vero: tutti i testi del catalogo (A: modelli del giudice A; B: misure e giudici; N: i nulli dei giudici) -> risultati/ia26_corse_vero.jsonl
  C  calibrazione del mondo "calibrato": 27 testi sintetici su una griglia di (eco, tema, contatto), una regressione quadratica, 3 testi di rifinitura; i parametri che
     portano copia netta, Λ, contatto e G9 ai valori del vero vanno in dati/cache/ia26/calibrazione.json
  T  la taratura, un mondo dopo l'altro: addestramento di M1, M5, E2 (5 pieghe, 1 replica), libri, banco nel mondo (con il gemello del mondo come riferimento
     "imitatore perfetto") -> risultati/ia26_corse_<mondo>.jsonl
  S  sintesi: riferimento, profili, distanze, controlli e letture preregistrate -> risultati/ia26_righello_taratura.json e .md (solo numeri e aggregati)

    nohup bash strumenti/coda.sh ia26 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia26" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO22=1 USCITA=<cartella fuori dal repo> python esperimenti/ia26_righello_taratura.py     (prova sul libro latino)

Variabili (oltre a quelle di ia07 che si importano: SOLO_CONTROLLI, USCITA, ...): PROCESSI (non cambia i risultati), RIPRENDI, FASI, FILTRO (sottostringhe, separate da |,
che il nome del lavoro deve contenere). Nuove: CACHE26, MONDI26 (cifre 1-5: markov2, ecocontatto, tec, calibrato, eco20; predefinito 1234), TIPI26 (cifre 1-3: M1, M5, E2; 123),
N_LIBRI26 (libri per imitatore e mondo, 4), MONDI_GRU26 (mondi in cui si misurano k90 e R_rel; predefinito 4 = calibrato), S_GRU_MONDO26 (3), S_META26 (200), S_NULLO26 (200), S_NULLO_N26 (60), S_GRU26 (6), SEMI_GRU_VERO26 (123), CHUNK26 (60), N_PER_SET26 (5), N_V21_26 (10),
ISTANZE_CIF26 (1), CACHE_LIBRI26 (solo prove), CAL26 (percorso del file di calibrazione, di norma automatico). Valori senza virgole e senza due punti (la coda divide le impostazioni).
Le variabili di ia20 e ia22 (EPOCHE20, PAZIENZA20, EPOCHE22, PAZIENZA22, PICCOLO20, PICCOLO22) valgono anche per l'addestramento della taratura.
"""
import json
import math
import os
import statistics
import sys
import time
from collections import Counter, OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402

NOME = 'ia26_righello_taratura'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE26 = B.CACHE26
CAL_FILE = os.path.join(CACHE26, 'calibrazione.json')
RT.CACHE26_CAL = CAL_FILE
os.environ['CAL26'] = CAL_FILE                                       # i processi figli leggono i parametri del mondo calibrato da qui

# ---- la taratura: mondi, imitatori
MONDI_ELENCO = list(RT.MONDI)                                        # markov2, ecocontatto, tec, calibrato
MONDI_TAR = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI26', '1234') if x.isdigit() and 1 <= int(x) <= len(MONDI_ELENCO)]
TIPI_TAR = OrderedDict([('M1', ('ia20', 1)), ('M5', ('ia20', 5)), ('E2', ('ia22', 'E2'))])
TIPI_USATI = [list(TIPI_TAR)[int(x) - 1] for x in os.environ.get('TIPI26', '123') if x.isdigit() and 1 <= int(x) <= len(TIPI_TAR)]
# quali imitatori in quale mondo (il controllo positivo costa solo M1)
MATRICE = OrderedDict([('markov2', ['M1']), ('ecocontatto', ['M1', 'M5', 'E2']), ('tec', ['M1', 'M5', 'E2']), ('calibrato', ['M1', 'M5', 'E2']), ('eco20', ['M1', 'M5', 'E2'])])
N_LIBRI_TAR = int(os.environ.get('N_LIBRI26', 4))
MONDI_GRU = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI_GRU26', '4') if x.isdigit() and 1 <= int(x) <= len(MONDI_ELENCO)]   # mondi in cui si misurano anche k90 e R_rel (le reti piccole costano)
ETICHETTE_VOYNICH = OrderedDict([('M1', 'ia20_M1'), ('M5', 'ia20_M5'), ('E2', 'ia22_E2')])     # le stesse famiglie nel catalogo del vero
PIEGHE = I7.PIEGHE

# ---- soglie e letture (fissate nella preregistrazione, prima di eseguire sul Voynich; quelle marcate sono state scritte dopo la prova su testi non Voynich)
CONTR_NEG_CATALOGO_FUORI = 0.50      # il controllo CTRL:tutto deve stare fuori fascia su almeno questa quota di misure e giudici (dopo la prova: la prima versione chiedeva lo stesso a CTRL:parole)
CONTR_POS_AUC = 0.60                 # imitatore su catena di Markov di ordine 2: e231, e266 e K al massimo cosi'
NON_PULITI_MAX = 3                   # giudici "non puliti" (gemello fuori dal nullo) al massimo
GEMELLO_FUORI_MAX = 0.20             # il gemello del mondo: fuori fascia al massimo su questa quota
GEMELLO_AUC = (0.45, 0.55)           # e231, e266, K del gemello
PRECISIONE_CAL = 0.15                # la calibrazione riesce se copia netta, Λ, contatto e G9 sono entro il 15% del vero
AL_VERO_VOLTE, AL_VERO_FUORI = 2.0, 0.25    # "al vero": distanza <= 2 volte quella del gemello e fuori fascia <= 25%
LONTANO_VOLTE, LONTANO_FUORI = 4.0, 0.50    # "lontano": distanza >= 4 volte quella del gemello o fuori fascia >= 50%
PAVIMENTO_GEMELLO = 0.5              # la distanza del gemello non si prende sotto questo valore (e' una sola copia)
RAPPORTO_STESSA_LONTANANZA = 0.75    # distanza nel mondo / distanza sul Voynich: da qui in su "lontani quanto sul Voynich"
FASCIA_POCO_INFORMATIVA = 0.5        # misura con scala >= 0,5 volte il valore del vero: segnalata come poco informativa
NULLO_POCO_INFORMATIVO = 0.06        # giudice con deviazione standard del nullo >= 0,06: segnalato come poco informativo
GRIGLIA_ECO, GRIGLIA_TEMA, GRIGLIA_CONT = (0.0, 0.04, 0.10), (0.0, 0.08, 0.18), (0.0, 0.30, 0.60)      # dopo la prova sul latino: lo zero in ogni asse (i valori piccoli non bastavano)
BOX_CAL = dict(eco=(0.0, 0.15), tema=(0.0, 0.30), contatto=(0.0, 0.75))
MISURE_CAL = ('copia_netta', 'lam', 'contatto', 'G9')
PUBBLICATI = OrderedDict([('copia_netta', 0.114), ('lam', 0.207), ('contatto', 0.188), ('D', 0.144), ('G9', 0.040), ('costo_forma', 3.48)])   # ia20-ia24 (solo per il confronto)

_T = {}


def nu(v, d=3):
    return I7.nu(v, d)


# ---------------------------------------------------------------- lavori della taratura

def _tar():
    """ia20 e ia22 (addestramento e scrittura di M1, M5 ed E2) con le cartelle dei modelli dentro la cartella del mondo corrente."""
    if 'm' not in _T:
        import ia20_imitatore_gradini as I20
        import ia22_eco_e_legame as I22
        I20.MOD20 = B.dir_mondo('tar_modelli_ia20')
        I22.MOD22 = B.dir_mondo('tar_modelli_ia22')
        os.makedirs(I20.MOD20, exist_ok=True)
        os.makedirs(I22.MOD22, exist_ok=True)
        _T['m'] = (I20, I22)
    return _T['m']


def lavoro_addestra(tipo, piega):
    I20, I22 = _tar()
    kind, k = TIPI_TAR[tipo]
    ris = I20.addestra(k, piega, 0) if kind == 'ia20' else I22.addestra(k, piega, 0)
    ris = OrderedDict((a, v) for a, v in ris.items() if not a.startswith('curva'))
    ris['lavoro'] = 'addestra|%s|%d' % (tipo, piega)
    ris['tipo'] = tipo
    return ris


def lavoro_libro(tipo, i):
    """Un libro dell'imitatore `tipo` nel mondo corrente (modelli della replica 0, ogni pagina dal modello della piega che non ha visto il suo foglio)."""
    inizio = time.time()
    I20, I22 = _tar()
    kind, k = TIPI_TAR[tipo]
    seme = B.seme_str('ia26libro', B._S['mondo'], tipo, i)
    t, conta = I20.scrivi_libro(k, 0, seme) if kind == 'ia20' else I22.scrivi_libro22(k, 0, seme)
    percorso = B.percorso_libro_tar(tipo, i)
    I7.scrivi_file(t, percorso + '.tmp', 'ia26, libro %s %d, mondo %s' % (tipo, i, B._S['mondo']), 0)
    os.replace(percorso + '.tmp', percorso)
    assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    return OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                        ('modi_scrittura', OrderedDict(conta)), ('secondi', round(time.time() - inizio, 1))])


def parametri_cal(args):
    """('cal', 'g' o 'r', eco, tema, contatto) -> dizionario dei parametri del generatore di ia23."""
    return dict(eco=float(args[2]), tema=float(args[3]), contatto=float(args[4]), ritocco=0.6, inizio=0.0, n_tema=25, freq_min_tema=3, pref_seed=B.seme_str('ia26', 'pref', 'calibrato'))


def lavoro_cal(args):
    """Un testo sintetico (tema, eco e contatto di ia23) con i parametri dati, sul libro vero, misurato come un testo del banco (copia netta, Λ, contatto, G9)."""
    inizio = time.time()
    par = parametri_cal(args)
    base = I7.libro_vero()
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    righe = RT.genera_sintetico('tec2', base, B.seme_str('ia26cal', *args[1:]), D, unita, par)
    rows = OrderedDict((p, [(bool(x['ini']), [tuple(D(w)) for w in x['parole']]) for x in rr]) for p, rr in I7.per_pagina(righe).items())
    ris = B.lavoro_M('cal', rows=rows)
    ris['lavoro'] = '|'.join(str(a) for a in args)
    ris['par'] = OrderedDict((k, v) for k, v in par.items() if k != 'pref_seed')
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_ia26(args):
    inizio = time.time()
    try:
        t = args[0]
        if t == 'addestra':
            return lavoro_addestra(args[1], int(args[2]))
        if t == 'libro':
            return lavoro_libro(args[1], int(args[2]))
        if t == 'cal':
            return lavoro_cal(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])
    r = B.lavoro(args)
    for k in ('pesanti_e231', 'pesanti_e266'):                           # nomi di caratteristiche: non servono ai risultati
        r.pop(k, None)
    return r


def avvia(mondo, nomi):
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    B.imposta_mondo(mondo, nomi)


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


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia26_corse_%s.jsonl' % mondo)


def esegui(mondo, nomi, lavori, processi, fatte):
    """Fa girare i lavori in un gruppo di processi che hanno attivato il mondo `mondo`. Scrive una riga per lavoro in ia26_corse_<mondo>.jsonl."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte and (not filtro or any(x in '|'.join(str(y) for y in a) for x in filtro))]
    if not da_fare:
        return []
    percorso = percorso_corse(mondo)
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro_ia26, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'AUC_e231', 'AUC_e266', 'AUC_A', 'AUC_N', 'copia_netta', 'k90', 'R_rel') if x in r}
                print('[%s %d/%d %.1f min] %s: %s (%.0f s)' % (mondo, k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def fatte_di(mondo):
    if os.environ.get('RIPRENDI') == '1':
        return {c['lavoro'] for c in leggi_corse(percorso_corse(mondo)) if not c.get('errore')}
    open(percorso_corse(mondo), 'w').close()
    return set()


# ---------------------------------------------------------------- fasi B, C, T

def fase_B(processi):
    """Il banco sul vero: tutti i testi del catalogo."""
    nomi = [n for n in RT.catalogo() if n != 'vero']
    B.punta_cartelle('vero')
    fatte = fatte_di('vero')
    fasi = B.fasi_banco(nomi, mondo='vero')
    for nome_fase in ('A', 'B', 'N'):
        print('== fase B/%s: %d lavori (%d testi)' % (nome_fase, len(fasi[nome_fase]), len(nomi)), flush=True)
        esegui('vero', nomi, fasi[nome_fase], processi, fatte)
    scrivi_riferimento('vero')
    return nomi


def griglia_cal():
    return [('cal', 'g', e, t, c) for e in GRIGLIA_ECO for t in GRIGLIA_TEMA for c in GRIGLIA_CONT]


def _feature(e, t, c):
    return [1.0, e, t, c, e * e, t * t, c * c, e * t, e * c, t * c]


def calibra(C, bersaglio, centro=None):
    """Dai testi gia' valutati (`C`: lavoro -> risultato; la griglia e le rifiniture) una regressione quadratica per ognuna delle quattro misure, e il punto della
    scatola (BOX_CAL) che le porta piu' vicino ai valori del vero (`bersaglio`). Con `centro` (eco, tema, contatto) la regressione pesa di piu' i testi vicini al
    centro (peso gaussiano, larghezza meta' della scatola): serve alle rifiniture. -> (punto, previsto)."""
    pts = [r for k, r in C.items() if k.startswith('cal|g|') or k.startswith('cal|r|')]
    X = np.array([_feature(r['par']['eco'], r['par']['tema'], r['par']['contatto']) for r in pts])
    w = np.ones(len(pts))
    if centro is not None:
        larg = [0.5 * (BOX_CAL[k][1] - BOX_CAL[k][0]) for k in ('eco', 'tema', 'contatto')]
        w = np.array([math.exp(-sum(((r['par'][k] - c) / l) ** 2 for k, c, l in zip(('eco', 'tema', 'contatto'), centro, larg))) for r in pts])
    sw = np.sqrt(w)[:, None]
    coef = {m: np.linalg.lstsq(X * sw, np.array([r[m] for r in pts]) * sw[:, 0], rcond=None)[0] for m in MISURE_CAL}
    e = np.linspace(BOX_CAL['eco'][0], BOX_CAL['eco'][1], 36)
    t = np.linspace(BOX_CAL['tema'][0], BOX_CAL['tema'][1], 36)
    c = np.linspace(BOX_CAL['contatto'][0], BOX_CAL['contatto'][1], 36)
    E, T, Cc = np.meshgrid(e, t, c, indexing='ij')
    F = np.stack([np.ones_like(E), E, T, Cc, E * E, T * T, Cc * Cc, E * T, E * Cc, T * Cc], axis=-1).reshape(-1, 10)
    err = np.zeros(len(F))
    previsto = {}
    for m in MISURE_CAL:
        pr = F @ coef[m]
        previsto[m] = pr
        err += np.abs(pr - bersaglio[m]) / max(abs(bersaglio[m]), 1e-3)
    i = int(np.argmin(err))
    return (float(E.reshape(-1)[i]), float(T.reshape(-1)[i]), float(Cc.reshape(-1)[i])), OrderedDict((m, float(previsto[m][i])) for m in MISURE_CAL)


def errore_cal(r, bersaglio):
    return OrderedDict((m, abs(r[m] - bersaglio[m]) / max(abs(bersaglio[m]), 1e-3)) for m in MISURE_CAL)


def fase_C(processi):
    """Calibrazione del mondo 'calibrato' (tema, eco e contatto di ia23 portati ai valori del libro vero)."""
    B.punta_cartelle('vero')
    fatte = fatte_di('calibrazione')
    lav = [('cal', 'v')] + griglia_cal()
    print('== fase C: griglia di %d testi sintetici + il vero' % (len(lav) - 1), flush=True)
    esegui_cal(lav, processi, fatte)
    C = {c['lavoro']: c for c in leggi_corse(percorso_corse('calibrazione')) if not c.get('errore')}
    bers = {m: C['cal|v'][m] for m in MISURE_CAL}
    punto, prev = calibra(C, bers)
    prev0 = prev
    for giro in (1, 2):                                                   # due giri di rifinitura: il punto previsto e due variazioni, poi la regressione si rifa' pesando i testi vicini
        lav2 = [('cal', 'r', punto[0], punto[1], punto[2]), ('cal', 'r', punto[0] * 1.15, punto[1] * 0.9, punto[2]), ('cal', 'r', punto[0] * 0.87, punto[1] * 1.1, punto[2])]
        lav2 = [tuple(round(x, 4) if isinstance(x, float) else x for x in a) for a in lav2]
        print('== fase C: rifinitura %d (%d testi)' % (giro, len(lav2)), flush=True)
        esegui_cal(lav2, processi, fatte)
        C = {c['lavoro']: c for c in leggi_corse(percorso_corse('calibrazione')) if not c.get('errore')}
        cand = [r for k, r in C.items() if k.startswith('cal|g|') or k.startswith('cal|r|')]
        best = min(cand, key=lambda r: float(np.mean(list(errore_cal(r, bers).values()))))
        punto, _ = calibra(C, bers, centro=(best['par']['eco'], best['par']['tema'], best['par']['contatto']))
    prev = prev0
    cand = [r for k, r in C.items() if k.startswith('cal|g|') or k.startswith('cal|r|')]
    scelta = min(cand, key=lambda r: float(np.mean(list(errore_cal(r, bers).values()))))
    err = errore_cal(scelta, bers)
    cal = OrderedDict(parametri=OrderedDict((k, scelta['par'][k]) for k in ('eco', 'tema', 'contatto', 'ritocco', 'inizio', 'n_tema', 'freq_min_tema')), bersaglio=bers, ottenuto=OrderedDict((m, scelta[m]) for m in MISURE_CAL),
                      errore_relativo=err, riuscita=bool(all(v <= PRECISIONE_CAL for v in err.values())), previsto_dal_primo_modello=prev, pubblicati=PUBBLICATI,
                      testi=len(cand), solo_controlli=SOLO_CONTROLLI)
    os.makedirs(CACHE26, exist_ok=True)
    json.dump(cal, open(CAL_FILE, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('calibrazione: %s' % json.dumps(cal['errore_relativo'], default=float), flush=True)
    return cal


def esegui_cal(lavori, processi, fatte):
    """Come `esegui` ma i lavori di calibrazione ('cal|v' = il vero) girano nel mondo vero e si scrivono in ia26_corse_calibrazione.jsonl."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte and (not filtro or any(x in '|'.join(str(y) for y in a) for x in filtro))]
    if not da_fare:
        return
    percorso = percorso_corse('calibrazione')
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=('vero', [])) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro_cal_o_vero, da_fare), 1):
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                print('[cal %d/%d] %s: %s' % (k, len(da_fare), r['lavoro'], {m: round(r[m], 4) for m in MISURE_CAL}), flush=True)
        pool.close()
        pool.join()


def lavoro_cal_o_vero(args):
    if args == ('cal', 'v'):
        try:
            r = B.lavoro_M('vero')
            r['lavoro'] = 'cal|v'
            return r
        except Exception as e:                                            # noqa: BLE001
            return OrderedDict([('lavoro', 'cal|v'), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300]))])
    return lavoro_ia26(args)


def tipi_del_mondo(mondo):
    return [t for t in MATRICE[mondo] if t in TIPI_USATI]


def nomi_mondo(mondo):
    return ['gem'] + ['tar:%s:%d' % (t, i) for t in tipi_del_mondo(mondo) for i in range(1, N_LIBRI_TAR + 1)]


def fase_T(processi):
    """La taratura: per ogni mondo, addestramento degli imitatori, libri e banco."""
    for mondo in MONDI_TAR:
        tipi = tipi_del_mondo(mondo)
        if not tipi:
            continue
        nomi = nomi_mondo(mondo)
        B.punta_cartelle(mondo)
        fatte = fatte_di(mondo)
        fasi = B.fasi_banco(nomi, con_gru=mondo in MONDI_GRU, mondo=mondo)
        addestra = [('addestra', t, k) for t in sorted(tipi, key=lambda x: -list(TIPI_TAR).index(x)) for k in range(PIEGHE)]
        print('== fase T/%s: addestramento (%d modelli) e giudice A' % (mondo, len(addestra)), flush=True)
        esegui(mondo, nomi, fasi['A'] + addestra, processi, fatte)
        libri = [('libro', t, i) for i in range(1, N_LIBRI_TAR + 1) for t in tipi]
        print('== fase T/%s: %d libri' % (mondo, len(libri)), flush=True)
        esegui(mondo, nomi, libri, processi, fatte)
        for nf in ('B', 'N'):
            print('== fase T/%s: banco %s (%d lavori)' % (mondo, nf, len(fasi[nf])), flush=True)
            esegui(mondo, nomi, fasi[nf], processi, fatte)
        scrivi_riferimento(mondo)


# ---------------------------------------------------------------- analisi

def carica_mondo(mondo, nomi):
    """Riferimento, profili e distanze dei testi `nomi` nel mondo `mondo`, dalle corse."""
    B.punta_cartelle(mondo)
    C = B.indice_corse(leggi_corse(percorso_corse(mondo)))
    rif = B.riferimento_da_corse(C)
    if 'M|vero' not in C:
        return None
    n_pag = C['M|vero']['pagine']
    nomi = [n for n in nomi if ('M|%s' % n) in C]                       # i libri che non esistono (o non sono stati misurati) non contano
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    profili, dist = OrderedDict(), OrderedDict()
    for n in nomi:
        profili[n] = B.valori_testo(n, C, pK, pKN, n_pag)
    centri, non_puliti = {}, []
    if 'gem' in profili:
        for j, x in rif['nullo'].items():
            a = profili['gem'].get(j)
            if a is not None and a > x['q'][1]:
                centri[j] = a
                non_puliti.append(j)
    for n in nomi:
        dist[n] = B.distanza(profili[n], rif, centri=centri)
    rif['giudici_non_puliti'] = non_puliti
    return dict(C=C, rif=rif, profili=profili, dist=dist, centri=centri)


def scrivi_riferimento(mondo):
    """Il riferimento del vero del mondo (valori, scale, fasce, nulli) in dati/cache/ia26/<mondo>/riferimento.json: serve al comando `righello_banco profilo`."""
    B.punta_cartelle(mondo)
    C = B.indice_corse(leggi_corse(percorso_corse(mondo)))
    rif = B.riferimento_da_corse(C)
    if rif['vero'] and rif['nullo']:
        os.makedirs(B.dir_mondo(), exist_ok=True)
        json.dump(rif, open(B.dir_mondo('riferimento.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return rif


def mes(xs):
    return MS_media_es(xs)


def MS_media_es(xs):
    import imitatore_misure as MS
    return MS.media_es(xs)


def famiglie_di(nomi):
    out = OrderedDict()
    for n in nomi:
        f = ('tar:' + n.split(':')[1]) if n.startswith('tar:') else ('gem' if n == 'gem' else RT.famiglia(n))
        out.setdefault(f, []).append(n)
    return out


def riassunto_famiglia(membri, M):
    """Per un gruppo di testi: distanza media (e errore), quota fuori fascia, valore medio e z medio di ogni misura e giudice."""
    ds = [M['dist'][n]['distanza'] for n in membri if M['dist'][n]['distanza'] is not None]
    fu = [M['dist'][n]['fuori'] for n in membri if M['dist'][n]['fuori'] is not None]
    out = OrderedDict(libri=len(membri), distanza=mes(ds), rms=mes([M['dist'][n]['rms'] for n in membri]), fuori=mes(fu), valori=OrderedDict(), z=OrderedDict())
    for m in list(B.MISURE) + list(B.GIUDICI) + list(B.EXTRA):
        out['valori'][m] = mes([M['profili'][n].get(m) for n in membri])
    for m in B.DISTANZA_SU:
        out['z'][m] = mes([M['dist'][n]['z'].get(m) for n in membri])
    return out


def classe_distanza(d, f, d_gem):
    """'al vero' / 'lontano' / 'intermedio' secondo le soglie preregistrate (distanza e quota fuori fascia, contro la distanza del gemello)."""
    if d is None or f is None:
        return None
    rif = max(d_gem if d_gem is not None else PAVIMENTO_GEMELLO, PAVIMENTO_GEMELLO)
    if d <= AL_VERO_VOLTE * rif and f <= AL_VERO_FUORI:
        return 'al vero'
    if d >= LONTANO_VOLTE * rif or f >= LONTANO_FUORI:
        return 'lontano'
    return 'intermedio'


def misure_poco_informative(rif):
    out = []
    for m, s in rif['scala'].items():
        v = rif['vero'].get(m)
        if s is not None and v not in (None, 0) and s >= FASCIA_POCO_INFORMATIVA * abs(v):
            out.append(m)
    for j, x in rif['nullo'].items():
        if x['sd'] is not None and x['sd'] >= NULLO_POCO_INFORMATIVO:
            out.append(j)
    return out


def classe_fascia(zs):
    """'fuori fascia' / 'dentro la fascia' / 'misto' per un gruppo di libri: media dei z e quota di libri oltre +-1,96 (soglia dell'80%)."""
    zs = [z for z in zs if z is not None]
    if not zs:
        return None
    m = float(np.mean(zs))
    fuori = float(np.mean([abs(z) > B.Z95 for z in zs]))
    if abs(m) > B.Z95 and fuori >= 0.8:
        return 'fuori fascia'
    if abs(m) <= B.Z95 and fuori <= 0.2:
        return 'dentro la fascia'
    return 'misto'


def e_imitatore(f):
    return f.split('_')[0] in ('ia07', 'ia16', 'ia20', 'ia22', 'ia23', 'ia24')


def letture_parte1(V):
    """B3 (affermazioni delle voci precedenti rilette con la fascia) e B4 (giudici nuovi contro vecchi)."""
    fam = famiglie_di([n for n in V['dist']])
    cls = OrderedDict()
    for f, membri in fam.items():
        cls[f] = OrderedDict((m, classe_fascia([V['dist'][n]['z'].get(m) for n in membri])) for m in B.DISTANZA_SU)
    imit = [f for f in fam if e_imitatore(f)]
    B3 = OrderedDict(classi=OrderedDict((f, cls[f]) for f in imit))
    B3['a_G9'] = OrderedDict(confermata=all(cls[f]['G9'] == 'fuori fascia' for f in imit), non_fuori=[f for f in imit if cls[f]['G9'] != 'fuori fascia'])
    B3['a_forma'] = OrderedDict(confermata=all(cls[f]['costo_forma'] == 'fuori fascia' for f in imit), non_fuori=[f for f in imit if cls[f]['costo_forma'] != 'fuori fascia'])
    con_eco = [f for f in imit if ('_' in f and f.split('_', 1)[1] in ('M2', 'M3', 'M4', 'M5', 'E0', 'E1', 'E2', 'E3', 'P1', 'P2', 'P3', 'R'))]
    B3['b_lam'] = OrderedDict(fuori=[f for f in con_eco if cls[f]['lam'] == 'fuori fascia'], non_fuori=[f for f in con_eco if cls[f]['lam'] != 'fuori fascia'])
    B3['c_contatto'] = OrderedDict((f, cls[f]['contatto']) for f in imit)
    B3['d_M1'] = OrderedDict(contatto=cls.get('ia20_M1', {}).get('contatto'), D=cls.get('ia20_M1', {}).get('D'))
    v21 = fam.get('V21', [])
    z21 = OrderedDict()
    for j in ('e231', 'e266'):
        xs = [V['dist'][n]['z'].get(j) for n in v21 if V['dist'][n]['z'].get(j) is not None]
        z21[j] = float(np.mean(xs)) if xs else None
    B3['e_v21'] = OrderedDict(z_v21=z21, imitatori_piu_vicini_del_v21=[f for f in imit if all(
        z21[j] is not None and abs(float(np.mean([V['dist'][n]['z'].get(j, 99.0) for n in fam[f]]))) < abs(z21[j]) for j in ('e231', 'e266'))] if v21 else None)
    # B4: correlazione di rango fra giudici sui gruppi
    from scipy.stats import spearmanr
    gruppi = [f for f in fam if f not in ('gem',)]
    medie = {j: [float(np.mean([V['profili'][n].get(j) for n in fam[f] if V['profili'][n].get(j) is not None] or [float('nan')])) for f in gruppi] for j in B.GIUDICI}
    B4 = OrderedDict()
    for a in B.GIUDICI:
        for b in B.GIUDICI:
            if a < b:
                x, y = np.array(medie[a]), np.array(medie[b])
                ok = ~(np.isnan(x) | np.isnan(y))
                B4['%s~%s' % (a, b)] = float(spearmanr(x[ok], y[ok])[0]) if ok.sum() > 3 else None
    nuovi = [B4.get('K~N'), B4.get('KN~K')]
    B4['concordano_con_K'] = bool(all(x is not None and x >= 0.7 for x in nuovi))
    B4['gruppi'] = len(gruppi)
    return OrderedDict(B3=B3, B4=B4)


def analisi(versioni):
    out = OrderedDict(esperimento='ia26', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=[], tempi_minuti=OrderedDict())
    # ---- il vero: riferimento, profili e distanze di tutti i testi del catalogo
    nomi_v = [n for n in RT.catalogo() if n != 'vero']
    V = carica_mondo('vero', nomi_v)
    out['catalogo'] = len(nomi_v)
    if V is None:
        out['errori'].append('manca M|vero nelle corse del vero')
        return out, None, {}
    rif = V['rif']
    out['riferimento'] = OrderedDict(vero=rif['vero'], scala=rif['scala'], fascia=rif['fascia'], nullo=rif['nullo'], divisioni=rif.get('divisioni'), divisioni_rete=rif.get('divisioni_rete'),
                                     seme_sd=rif.get('seme_sd'), poco_informative=misure_poco_informative(rif), pubblicati=PUBBLICATI)
    nomi_v = list(V['dist'])
    fam_v = famiglie_di(nomi_v)
    out['famiglie_vero'] = OrderedDict((f, riassunto_famiglia(m, V)) for f, m in fam_v.items())
    out['testi_vero'] = OrderedDict((n, OrderedDict(valori=V['profili'][n], distanza=V['dist'][n]['distanza'], rms=V['dist'][n]['rms'], fuori=V['dist'][n]['fuori'], z=V['dist'][n]['z'])) for n in nomi_v)
    # ---- i mondi della taratura
    mondi = OrderedDict()
    for mondo in MONDI_TAR:
        nm = nomi_mondo(mondo)
        M = carica_mondo(mondo, nm)
        if M is None:
            out['errori'].append('mancano le corse del mondo %s' % mondo)
            continue
        fam = famiglie_di(list(M['dist']))
        mondi[mondo] = OrderedDict(riferimento=OrderedDict(vero=M['rif']['vero'], scala=M['rif']['scala'], nullo=M['rif']['nullo'], poco_informative=misure_poco_informative(M['rif'])),
                                   famiglie=OrderedDict((f, riassunto_famiglia(m, M)) for f, m in fam.items()),
                                   gemello=OrderedDict(valori=M['profili'].get('gem'), distanza=M['dist'].get('gem', {}).get('distanza'), fuori=M['dist'].get('gem', {}).get('fuori'),
                                                       z=M['dist'].get('gem', {}).get('z')),
                                   parametri=RT.parametri_mondo(mondo), giudici_non_puliti=M['rif'].get('giudici_non_puliti', []))
        mondi[mondo]['_M'] = M
    out['mondi'] = OrderedDict((k, OrderedDict((a, b) for a, b in v.items() if a != '_M')) for k, v in mondi.items())
    cal = json.load(open(CAL_FILE, encoding='utf-8')) if os.path.exists(CAL_FILE) else None
    out['calibrazione'] = cal
    out['controlli'], out['letture'] = controlli_e_letture(out, V, mondi, cal)
    out['letture'].update(letture_parte1(V))
    for tipo in ('addestra', 'libro', 'K', 'KN', 'D', 'M', 'J', 'G', 'gm', 'lmA', 'metro', 'nullo', 'cal'):
        s = []
        for mondo in ['vero'] + MONDI_TAR + ['calibrazione']:
            s += [c['secondi'] for c in leggi_corse(percorso_corse(mondo)) if not c.get('errore') and c['lavoro'].split('|')[0] == tipo and c.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    out['errori'] += [c['lavoro'] for mondo in ['vero'] + MONDI_TAR + ['calibrazione'] for c in leggi_corse(percorso_corse(mondo)) if c.get('errore')]
    return out, V, mondi


def controlli_e_letture(out, V, mondi, cal):
    ctr, let = OrderedDict(), OrderedDict()
    fam = out['famiglie_vero']
    # --- controlli
    ct, cp = V['dist'].get('CTRL:tutto'), V['dist'].get('CTRL:parole')
    zp = cp['z'] if cp else {}
    ok_tutto = bool(ct and ct['fuori'] is not None and ct['fuori'] >= CONTR_NEG_CATALOGO_FUORI)
    ok_parole = bool(cp and abs(zp.get('contatto', 0.0)) > B.Z95 and abs(zp.get('D', 0.0)) > B.Z95 and any(abs(zp.get(j, 0.0)) > B.Z95 for j in ('K', 'A', 'N', 'KN')))
    ctr['catalogo_negativo'] = OrderedDict(tutto_fuori=ct['fuori'] if ct else None, soglia=CONTR_NEG_CATALOGO_FUORI, tutto_ok=ok_tutto,
                                           parole_z=OrderedDict((m, zp.get(m)) for m in ('contatto', 'D', 'K', 'A', 'N', 'KN')), parole_ok=ok_parole, riuscito=bool(ok_tutto and ok_parole),
                                           nota='parole rimescolate in tutto il libro: fuori fascia su almeno la metà delle misure; parole rimescolate dentro la riga: fuori fascia su contatto, D e almeno un giudice a sorpresa')
    ctr['metro'] = OrderedDict(riuscito=bool(out['riferimento']['vero'] and out['riferimento']['nullo']), poco_informative=out['riferimento']['poco_informative'])
    ctr['calibrazione'] = OrderedDict(riuscita=bool(cal and cal.get('riuscita')), errore_relativo=cal.get('errore_relativo') if cal else None, soglia=PRECISIONE_CAL)
    ctr['mondi'] = OrderedDict()
    for mondo, M in mondi.items():
        g = M['gemello']
        z = g.get('z') or {}
        vals = g.get('valori') or {}
        auc3 = [vals.get(j) for j in ('e231', 'e266', 'K')]
        ctr['mondi'][mondo] = OrderedDict(
            gemello_fuori=g.get('fuori'), gemello_distanza=g.get('distanza'), gemello_auc=OrderedDict((j, vals.get(j)) for j in ('e231', 'e266', 'K')),
            giudici_non_puliti=M['giudici_non_puliti'], gemello_ok=bool(g.get('fuori') is not None and g['fuori'] <= GEMELLO_FUORI_MAX and len(M['giudici_non_puliti']) <= NON_PULITI_MAX))
    pos = None
    if 'markov2' in mondi:
        f = mondi['markov2']['famiglie'].get('tar:M1')
        if f:
            auc = OrderedDict((j, f['valori'][j][0]) for j in ('e231', 'e266', 'K'))
            pos = OrderedDict(auc=auc, soglia=CONTR_POS_AUC, riuscito=bool(all(a is not None and a <= CONTR_POS_AUC for a in auc.values())))
    ctr['positivo_markov2'] = pos
    # --- L1: gli imitatori sul Voynich (descrittiva) e che cosa e' fuori fascia
    L1 = OrderedDict()
    for tipo, et in ETICHETTE_VOYNICH.items():
        f = fam.get(et)
        if f:
            L1[tipo] = OrderedDict(distanza=f['distanza'], fuori=f['fuori'], z=f['z'])
    let['L1_imitatori_sul_vero'] = L1
    # --- L2: gli imitatori nei mondi, classe e rapporto con la distanza sul Voynich
    L2 = OrderedDict()
    for mondo, M in mondi.items():
        d_gem = M['gemello']['distanza']
        r = OrderedDict()
        for tipo in tipi_del_mondo(mondo):
            f = M['famiglie'].get('tar:%s' % tipo)
            if not f:
                continue
            dm, fm = f['distanza'][0], f['fuori'][0]
            dv = L1.get(tipo, {}).get('distanza', (None,))[0] if L1.get(tipo) else None
            fv = L1.get(tipo, {}).get('fuori', (None,))[0] if L1.get(tipo) else None
            r[tipo] = OrderedDict(distanza=dm, fuori=fm, classe=classe_distanza(dm, fm, d_gem), distanza_voynich=dv, fuori_voynich=fv, classe_voynich=classe_distanza(dv, fv, d_gem),
                                  rapporto=(dm / dv if dm is not None and dv else None), gemello=d_gem)
        L2[mondo] = r
    let['L2_taratura'] = L2
    # --- L3: l'esito (mondo primario: calibrato se la calibrazione e' riuscita, altrimenti tec)
    valido = bool(ctr['catalogo_negativo']['riuscito'] and ctr['metro']['riuscito'] and (pos is None or pos['riuscito']))
    primario = 'calibrato' if ('calibrato' in mondi and ctr['calibrazione']['riuscita']) else ('tec' if 'tec' in mondi else ('calibrato' if 'calibrato' in mondi else None))
    L3 = OrderedDict(mondo_primario=primario, valido=valido, nota_primario=('calibrazione non riuscita: il mondo calibrato è usato lo stesso, con riserva' if primario == 'calibrato' and not ctr['calibrazione']['riuscita'] else None))
    if primario is None or primario not in L2:
        L3['esito'] = 'nessuna lettura: manca il mondo primario'
    else:
        gem_ok = ctr['mondi'][primario]['gemello_ok']
        rr = L2[primario]
        lontani = [t for t, x in rr.items() if x['classe'] == 'lontano' and x['rapporto'] is not None and x['rapporto'] >= RAPPORTO_STESSA_LONTANANZA]
        al_vero = [t for t, x in rr.items() if x['classe'] == 'al vero' and x['classe_voynich'] == 'lontano']
        n = len(rr)
        soglia = 2 if n >= 3 else n
        if not valido or not gem_ok:
            L3['esito'] = 'lettura non valida (controlli: %s)' % ', '.join(k for k, b in (('catalogo negativo', ctr['catalogo_negativo']['riuscito']), ('metro', ctr['metro']['riuscito']),
                                                                                       ('positivo markov2', pos is None or pos['riuscito']), ('gemello', gem_ok)) if not b)
        elif len(lontani) >= soglia:
            L3['esito'] = 'A: gli imitatori restano lontani sul processo noto quanto sul Voynich: i verdetti di ia16 e ia20-ia24 dicono dei limiti degli imitatori, non del Voynich'
        elif len(al_vero) >= soglia:
            L3['esito'] = 'B: gli imitatori arrivano al vero sul processo noto e non sul Voynich: i verdetti sul Voynich valgono; le misure che falliscono solo sul Voynich sono i bersagli'
        else:
            L3['esito'] = 'intermedio: ne\' A ne\' B; vale la tabella misura per misura (L4)'
        L3['imitatori_lontani_quanto_sul_voynich'] = lontani
        L3['imitatori_al_vero_nel_mondo_ma_non_sul_voynich'] = al_vero
    let['L3_esito'] = L3
    # --- L4: misura per misura, nel mondo primario: fuori fascia sul Voynich / nel mondo (z medio sui libri dell'imitatore)
    L4 = OrderedDict()
    if primario in mondi:
        M = mondi[primario]
        for tipo in tipi_del_mondo(primario):
            f_m = M['famiglie'].get('tar:%s' % tipo)
            f_v = fam.get(ETICHETTE_VOYNICH[tipo])
            if not f_m or not f_v:
                continue
            tab = OrderedDict()
            for m in B.DISTANZA_SU:
                zm, zv = f_m['z'][m][0], f_v['z'][m][0]
                if zm is None or zv is None:
                    continue
                fm_, fv_ = abs(zm) > B.Z95, abs(zv) > B.Z95
                tab[m] = OrderedDict(z_mondo=zm, z_voynich=zv, classe='fuori in tutti e due (limite degli imitatori)' if fm_ and fv_ else 'fuori solo sul Voynich (bersaglio)' if fv_ else
                                     'fuori solo nel mondo noto' if fm_ else 'dentro in tutti e due')
            L4[tipo] = tab
    let['L4_misura_per_misura'] = L4
    return ctr, let


# ---------------------------------------------------------------- scrittura

def mf(x, d=3):
    if x is None:
        return '—'
    if isinstance(x, (tuple, list)):
        return '%s ± %s' % (nu(x[0], d), nu(x[1], d)) if x[0] is not None else '—'
    return nu(x, d)


def scrivi_md(o):
    L = o['letture']
    md = ['# IA26 (ia26) — Il righello e la taratura', '', 'Preregistrazione: `preregistrazioni/ia26.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '- Testi del catalogo (senza il vero): %d.' % o.get('catalogo', 0)]
    if o['errori']:
        md += ['- **Lavori falliti o mancanti:** ' + '; '.join(str(e) for e in o['errori']) + '.']
    md.append('')
    if 'riferimento' not in o:
        open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
        return
    r = o['riferimento']
    md += ['## Il metro "vero contro vero"', '', 'Le pagine vere divise in due metà (per foglio, bilanciate per sezione e lingua): %s divisioni per le misure di conteggio, %s per k90 e R_rel; per i giudici, '
           'l\'AUC con etichette a caso fra pagine vere. Scala = deviazione standard della differenza fra metà (per i giudici, del nullo). Fascia = 2,5-97,5 percentile della differenza.' % (
               r.get('divisioni'), r.get('divisioni_rete')), '', '| misura | vero | scala | fascia | scala / vero |', '|---|---|---|---|---|']
    for m, nome in B.MISURE.items():
        v, s, fa = r['vero'].get(m), r['scala'].get(m), r['fascia'].get(m)
        md.append('| %s | %s | %s | %s | %s |' % (nome, nu(v, 4), nu(s, 4), '[%s, %s]' % (nu(fa[0], 4), nu(fa[1], 4)) if fa else '—', nu(s / abs(v), 2) if s is not None and v else '—'))
    md += ['', '| giudice | media del nullo | scala (deviazione standard) | fascia 2,5-97,5 | etichettature |', '|---|---|---|---|---|']
    for j, nome in B.GIUDICI.items():
        x = r['nullo'].get(j)
        md.append('| %s | %s | %s | %s | %s |' % (nome, nu(x['media'] if x else None), nu(x['sd'] if x else None), '[%s, %s]' % (nu(x['q'][0]), nu(x['q'][1])) if x else '—', x['n'] if x else '—'))
    md += ['', 'Misure poco informative (scala ≥ %s volte il valore del vero): %s.' % (nu(FASCIA_POCO_INFORMATIVA, 1), ', '.join(r['poco_informative']) or 'nessuna'), '']
    md += ['## Distanza dal vero dei testi del catalogo (media di min(|z|, 6) su 11 misure e 6 giudici; pesi uguali)', '',
           '| gruppo | libri | distanza | media quadratica | fuori fascia (|z| > 1,96) | ' + ' | '.join(B.GIUDICI) + ' |', '|---|---|---|---|---|' + '---|' * len(B.GIUDICI)]
    for f, x in o['famiglie_vero'].items():
        md.append('| %s | %d | %s | %s | %s | %s |' % (f, x['libri'], mf(x['distanza'], 2), mf(x['rms'], 2), mf(x['fuori'], 2), ' | '.join(mf(x['valori'][j]) for j in B.GIUDICI)))
    md += ['', '### z medio per misura (valore del gruppo meno il vero, in scale)', '', '| gruppo | ' + ' | '.join(B.MISURE) + ' |', '|---|' + '---|' * len(B.MISURE)]
    for f, x in o['famiglie_vero'].items():
        md.append('| %s | %s |' % (f, ' | '.join(nu(x['z'][m][0], 1) if x['z'][m][0] is not None else '—' for m in B.MISURE)))
    c = o['controlli']
    b3, b4 = L['B3'], L['B4']
    md += ['', '## Le affermazioni delle voci precedenti, rilette con la fascia (B3)', '',
           '- (a) G9 mai al vero: %s; non fuori fascia: %s.' % ('confermata' if b3['a_G9']['confermata'] else 'NON regge per tutti', ', '.join(b3['a_G9']['non_fuori']) or 'nessun gruppo'),
           '- (a) costo di forma delle parole nuove mai al vero: %s; non fuori fascia: %s.' % ('confermata' if b3['a_forma']['confermata'] else 'NON regge per tutti', ', '.join(b3['a_forma']['non_fuori']) or 'nessun gruppo'),
           '- (b) Λ fuori fascia nei gruppi con eco: %s; dentro o misti: %s.' % (', '.join(b3['b_lam']['fuori']) or 'nessuno', ', '.join(b3['b_lam']['non_fuori']) or 'nessuno'),
           '- (c) contatto per gruppo: %s.' % '; '.join('%s %s' % kv for kv in b3['c_contatto'].items()),
           '- (d) M1: contatto %s, D %s.' % (b3['d_M1']['contatto'], b3['d_M1']['D']),
           '- (e) v21: z di e231 e e266 %s; imitatori con z più piccolo del v21 su tutti e due: %s.' % (b3['e_v21']['z_v21'], b3['e_v21']['imitatori_piu_vicini_del_v21'] if b3['e_v21']['imitatori_piu_vicini_del_v21'] else 'nessuno'),
           '', '### Giudici nuovi contro vecchi (B4): correlazione di rango fra i %d gruppi' % b4['gruppi'], '', ', '.join('%s %s' % (k, nu(v, 2)) for k, v in b4.items() if '~' in k) + '.',
           'N e KN concordano con K (rho ≥ 0,7): %s.' % nu(b4['concordano_con_K']), '']
    md += ['', '## Controlli', '']
    cn = c['catalogo_negativo']
    md.append('- Controllo negativo del catalogo: parole rimescolate in tutto il libro fuori fascia su almeno %s di misure e giudici: %s → %s; parole rimescolate dentro la riga fuori fascia su contatto, D e almeno un giudice a sorpresa (z %s) → %s.' % (
        nu(CONTR_NEG_CATALOGO_FUORI, 2), nu(cn['tutto_fuori'], 2), nu(cn['tutto_ok']), ', '.join('%s %s' % (k, nu(v, 1)) for k, v in cn['parole_z'].items()), nu(cn['parole_ok'])))
    md.append('- Metro disponibile: %s.' % nu(c['metro']['riuscito']))
    if c['calibrazione']['errore_relativo']:
        md.append('- Calibrazione del mondo "calibrato" (entro %s): errori relativi %s → %s.' % (nu(PRECISIONE_CAL, 2), ', '.join('%s %s' % (k, nu(v, 3)) for k, v in c['calibrazione']['errore_relativo'].items()),
                                                                                         nu(c['calibrazione']['riuscita'])))
    if c['positivo_markov2']:
        md.append('- Positivo (M1 su catena di Markov di ordine 2: e231, e266, K al massimo %s): %s → %s.' % (nu(CONTR_POS_AUC, 2), ', '.join('%s %s' % kv for kv in c['positivo_markov2']['auc'].items()), nu(c['positivo_markov2']['riuscito'])))
    for mondo, x in c['mondi'].items():
        md.append('- Negativo, gemello del mondo %s (fuori fascia ≤ %s, con i giudici non puliti centrati sul gemello): fuori fascia %s, distanza %s, AUC %s; giudici non puliti (gemello fuori dal nullo): %s → %s.' % (
            mondo, nu(GEMELLO_FUORI_MAX, 2), nu(x['gemello_fuori'], 2), nu(x['gemello_distanza'], 2), ', '.join('%s %s' % (k, nu(v)) for k, v in x['gemello_auc'].items()),
            ', '.join(x['giudici_non_puliti']) or 'nessuno', nu(x['gemello_ok'])))
    md += ['', '## Taratura: gli imitatori su processi noti', '', '| mondo | imitatore | libri | distanza | fuori fascia | classe | sul Voynich: distanza | classe | rapporto mondo / Voynich | gemello |', '|---|---|---|---|---|---|---|---|---|---|']
    for mondo, rr in L['L2_taratura'].items():
        for tipo, x in rr.items():
            md.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (mondo, tipo, o['mondi'][mondo]['famiglie']['tar:%s' % tipo]['libri'], nu(x['distanza'], 2), nu(x['fuori'], 2), x['classe'],
                                                                              nu(x['distanza_voynich'], 2), x['classe_voynich'], nu(x['rapporto'], 2), nu(x['gemello'], 2)))
    md += ['', '## Letture preregistrate', '']
    l3 = L['L3_esito']
    md.append('- Mondo primario: %s; controlli validi: %s.' % (l3['mondo_primario'], nu(l3['valido'])))
    md.append('- **Esito: %s.**' % l3['esito'])
    if l3.get('imitatori_lontani_quanto_sul_voynich') is not None:
        md.append('- Imitatori lontani nel mondo noto quanto sul Voynich: %s. Imitatori al vero nel mondo noto e lontani sul Voynich: %s.' % (
            ', '.join(l3['imitatori_lontani_quanto_sul_voynich']) or 'nessuno', ', '.join(l3['imitatori_al_vero_nel_mondo_ma_non_sul_voynich']) or 'nessuno'))
    md += ['', '### Misura per misura (mondo primario; z medio sui libri dell\'imitatore)', '']
    for tipo, tab in L['L4_misura_per_misura'].items():
        md += ['**%s**' % tipo, '', '| misura | z nel mondo | z sul Voynich | classe |', '|---|---|---|---|']
        for m, x in tab.items():
            md.append('| %s | %s | %s | %s |' % ({**B.MISURE, **B.GIUDICI}[m], nu(x['z_mondo'], 1), nu(x['z_voynich'], 1), x['classe']))
        md.append('')
    if o['calibrazione']:
        cal = o['calibrazione']
        md += ['## Calibrazione', '', 'Parametri scelti: %s. Valori del vero (banco): %s. Ottenuti: %s. Errori relativi: %s. Valori pubblicati (ia20-ia24, solo confronto): %s.' % (
            ', '.join('%s %s' % (k, nu(v, 3)) for k, v in cal['parametri'].items()), ', '.join('%s %s' % (k, nu(v, 3)) for k, v in cal['bersaglio'].items()),
            ', '.join('%s %s' % (k, nu(v, 3)) for k, v in cal['ottenuto'].items()), ', '.join('%s %s' % (k, nu(v, 2)) for k, v in cal['errore_relativo'].items()),
            ', '.join('%s %s' % (k, nu(v, 3)) for k, v in cal['pubblicati'].items())), '']
    md += ['## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


def fase_S(versioni):
    o, V, mondi = analisi(versioni)
    json.dump(o, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(o)
    if 'letture' in o:
        print('esito: %s' % o['letture']['L3_esito']['esito'], flush=True)
    return o


# ---------------------------------------------------------------- principale

def main():
    import numpy
    import torch
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    os.makedirs(CACHE26, exist_ok=True)
    righe = I7.libro_vero()
    print('libro (%s): %d righe, %d pagine; mondi %s; imitatori %s' % ('controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), MONDI_TAR, TIPI_USATI), flush=True)
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'BCTS')
    if 'B' in fasi:
        fase_B(processi)
    if 'C' in fasi:
        fase_C(processi)
    if 'T' in fasi:
        fase_T(processi)
    if 'S' in fasi:
        fase_S(versioni)


if __name__ == '__main__':
    main()
