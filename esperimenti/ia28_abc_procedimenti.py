# -*- coding: utf-8 -*-
"""Esperimento IA28 (ia28): l'inferenza per simulazione sui procedimenti. NON e' una decifrazione: si stima, famiglia per famiglia, con
quali parametri un procedimento "da scriba" riprodurrebbe le statistiche del Voynich, e si vede quale famiglia ci arriva piu' vicino.

Idea (proposta C3 di REVIEW_FABLE.md e proposta 3 di PROPOSTA_METODI_OPUS.md). In ia14 e ia19 i procedimenti si provavano con tre valori
fissi per parametro e una distanza unica; qui i parametri si STIMANO (ABC: si pescano parametri da distribuzioni fissate prima, si scrive
un testo, si tengono i parametri il cui testo ha statistiche vicine al vero) e si confrontano tre famiglie con pochi parametri
(`abc_famiglie.py`): CV copia e varia (autocitazione generalizzata), NB Naibbe vero piu' eco di pagina, VT verboso piu' eco piu' bordi a
parametri liberi. La stima usa 29 statistiche classiche su QUARTI di libro (`abc_statistiche.py`); poi si controlla su misure TENUTE
FUORI, su libri INTERI scritti dai parametri trovati (`abc_tenute_fuori.py`): statistiche non usate nella stima, giudici e231, e266, K e
A, misure di ia09/ia10/ia02/ia03; il v21 sta nella stessa tabella come riferimento (non e' una famiglia: i suoi parametri sono ricavati dal
Voynich e il voynichizzatore non si tocca).

Fasi (variabile FASI28, lettere; predefinito SCVTL; la fase P, prova del codice, gira sempre per prima):
  P prova del codice            tutte le prove interne (famiglie, statistiche, motore, logica delle letture)
  S simulazioni per la tabella  N_TABELLA28 testi per famiglia, in pezzi da 250, ognuno su uno dei 4 quarti del libro (pagine a giro)
  C controlli                   positivi (testi di ogni famiglia con parametri noti: recupero di famiglia e parametri, verifica
                                predittiva calibrata) e negativi (latino in chiaro nell'impaginazione e testo rimescolato)
  V il vero                     stime sul testo vero (quattro quarti, ognuno per conto suo), verifica predittiva
  T misure tenute fuori         libri interi scritti con parametri dalla posteriore; giudici e misure fuori dalla stima; il v21 accanto
  L letture                     letture preregistrate, scritte in risultati/ia28_abc_procedimenti.json e .md (solo numeri)

    nohup bash strumenti/coda.sh NOME "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia28" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 USCITA=<cartella fuori dal repo> N_TABELLA28=500 ... python esperimenti/ia28_abc_procedimenti.py   (prova sul latino)

Variabili d'ambiente nuove (da aggiungere a VARIABILI di esegui.py): FASI28, N_TABELLA28, N_CONTROLLO28, N_PPC28, N_PPC_CTRL28, N_LIBRI28,
NT28, CACHE28, COMPONENTI28, V21_28, PICCOLO28. Gia' presenti e usate: PROCESSI, RIPRENDI, SOLO_CONTROLLI, USCITA, FILTRO.
I valori predefiniti sono quelli preregistrati. Preregistrazione: preregistrazioni/ia28.md.
"""
import json
import math
import os
import pickle
import random
import sys
import time
import zlib
from collections import Counter, OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import abc_famiglie as F  # noqa: E402
import abc_inferenza as INF  # noqa: E402
import abc_statistiche as S  # noqa: E402

NOME = 'ia28_abc_procedimenti'
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
RISULTATI = os.path.join(QUI, '..', 'risultati')
USCITA = os.environ.get('USCITA', RISULTATI)
CACHE28 = os.environ.get('CACHE28', os.path.join(USCITA, 'ia28_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia28'))
FASI28 = os.environ.get('FASI28', 'SCVTL')
PROCESSI = int(os.environ.get('PROCESSI', 1))
RIPRENDI = os.environ.get('RIPRENDI', '1') == '1'
N_TABELLA = int(os.environ.get('N_TABELLA28', 20000))        # testi per famiglia nella tabella di stima
N_CONTROLLO = int(os.environ.get('N_CONTROLLO28', 100))      # testi per famiglia per il controllo positivo (semi diversi dalla tabella)
N_PPC = int(os.environ.get('N_PPC28', 200))                  # testi simulati per ogni verifica predittiva
N_PPC_CTRL = int(os.environ.get('N_PPC_CTRL28', 20))         # controlli positivi per famiglia con verifica predittiva
N_LIBRI = int(os.environ.get('N_LIBRI28', 8))                # libri interi per famiglia nelle misure tenute fuori
NT = int(os.environ.get('NT28', 300))                        # alberi della foresta
COMPONENTI = os.environ.get('COMPONENTI28', 'XGKSDR')        # X statistiche fuori sintesi, G giudici e231 e266 e A, K giudice K, S struttura, D ordine, R rete
USA_V21 = os.environ.get('V21_28', '1') == '1'
PICCOLO = os.environ.get('PICCOLO28') == '1'                 # solo prove: meno libri v21
PEZZO = 250                                                  # testi per pezzo di tabella
N_QUARTI = 4
PIEGHE_K = 5

# ---- soglie e definizioni (fissate nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_FAMIGLIA = 0.80          # C1: la famiglia giusta ritrovata in almeno questa quota dei controlli positivi
SOGLIA_COPERTURA = 0.80         # C2: copertura dell'intervallo al 90% dei parametri stimabili, almeno questa
SOGLIA_PPC_POS = 0.80           # C3: la verifica predittiva passa (p >= 0,05) in almeno questa quota dei controlli positivi
QUARTI_MIN = 3                  # una lettura vale se si ripete in almeno 3 quarti su 4
PROB_MIN = 0.50                 # famiglia "preferita": probabilita' media almeno 0,5
SOGLIA_AL_VERO_REL = 0.05       # misura "al vero": entro il 5% del valore vero, oppure dentro l'intervallo di previsione dei libri
SOGLIA_QUOTA_AL_VERO = 0.75     # famiglia "tenute fuori al vero": almeno questa quota delle misure al vero
GIUDICE_REGGE, GIUDICE_VEDE = 0.62, 0.65      # come ia01: sotto 0,62 il giudice non vede; sopra 0,65 vede
POS_GIUDICE = 0.95              # il controllo "parole rimescolate" deve essere riconosciuto almeno a questo (come ia16)
NEG_BANDA = (0.45, 0.55)        # il giudice K, con etichette a caso, deve stare qui (come ia16)
MISURE_FUORI = ['H4', 'H5', 'righe_sopra_uguali', 'righe_2sopra_uguali', 'in_riga_d1', 'in_riga_d2', 'in_riga_d3', 'heaps',
                'consecutive_meno_caso', 'righe4_ripetute', 'ripetute_riga_sopra',
                'k90', 'GL', 'GR', 'R_rel', 'Q', 'copia_netta', 'lam', 'rho', 'G9', 'D']
GIUDICI = ['AUC_e231', 'AUC_e266', 'AUC_A', 'AUC_K']
COLONNE = OrderedDict([('CV', 'CV copia e varia'), ('NB', 'NB Naibbe vero + eco (nomi riallineati)'), ('NBn', 'NB (nomi nativi)'),
                       ('VT', 'VT verboso + eco + bordi'), ('V21', 'v21')])

_C = {}
_LAY = None            # nei processi figli: le impaginazioni dei quattro quarti


# ---------------------------------------------------------------- il testo vero (solo qui si carica)

def vero():
    """Pagine del testo vero (con SOLO_CONTROLLI il latino di prova di ia01), gruppi (sezione, lingua), impaginazione e quarti.
    E' l'UNICO punto che legge il Voynich: la preregistrazione dice che non si chiama prima del suo commit."""
    if 'vero' not in _C:
        import sintassi_testi as TT
        v = TT.testo_vere()
        pag = v['pagine']
        lay = F.layout_di(pag)
        _C['vero'] = dict(pagine=pag, tipo=v['tipo'], layout=lay, lay_q=F.quarti(lay, N_QUARTI), pag_q=F.quarti_pagine(pag, N_QUARTI))
    return _C['vero']


def gruppi_di(pagine, tipo):
    return {p: tipo.get(p) for p in pagine}


def vettore_quarti(pagine, tipo, seme=1):
    """Le statistiche di sintesi dei quattro quarti di un testo (nelle pagine del testo vero), ognuno col riferimento d'eco del proprio gruppo."""
    out = []
    for q, pq in enumerate(F.quarti_pagine(pagine, N_QUARTI)):
        out.append(S.vettore(S.statistiche(pq, gruppi_di(pq, tipo), seme + q)))
    return np.array(out)


# ---------------------------------------------------------------- lavori della tabella (nei processi)

def avvia_lavoro(lay_q):
    global _LAY
    _LAY = lay_q


def lavoro_tabella(args):
    """Un pezzo di testi simulati: (spazio dei semi 'tab' o 'ctrl', famiglia, numero del pezzo). Per ogni testo: parametri dall'a priori,
    un quarto di libro (k modulo 4), le 29 statistiche. Un testo che non riesce a scriversi si riprova con un altro seme (al massimo 3 volte)."""
    ns, fam, pezzo, n_max = args
    out = []
    for k in range(pezzo * PEZZO, min((pezzo + 1) * PEZZO, n_max)):
        q = k % N_QUARTI
        rec = None
        for tent in range(3):
            try:
                rnd = random.Random(F.seme28('th', ns, fam, k, tent))
                th = F.campiona(fam, rnd)
                pag, _ = F.genera(fam, th, _LAY[q], F.seme28('x', ns, fam, k, tent))
                s = S.statistiche(pag, None, k)
                rec = dict(k=k, q=q, u=[round(x, 6) for x in F.a_unita(fam, th)], s=[round(float(s[n]), 6) for n in S.NOMI])
                break
            except Exception as e:                                       # noqa: BLE001
                rec = dict(k=k, q=q, errore='%s: %s' % (type(e).__name__, str(e)[:120]))
        out.append(rec)
    return args, out


def lavoro_ppc(args):
    """Verifica predittiva: per ogni riga di parametri (scala [0, 1]) un testo sul quarto q e le sue statistiche."""
    chiave, fam, q, righe, seme0 = args
    M = []
    for i, u in enumerate(righe):
        for tent in range(3):
            try:
                th = F.da_unita(fam, u)
                pag, _ = F.genera(fam, th, _LAY[q], F.seme28('ppc', fam, seme0, i, tent))
                s = S.statistiche(pag, None, seme0 + i)
                M.append([float(s[n]) for n in S.NOMI])
                break
            except Exception:                                            # noqa: BLE001
                continue
    return chiave, fam, np.array(M)


def pool_lavori(funzione, lavori, lay_q, processi=None, etichetta='', al_risultato=None):
    """Esegue i lavori in un pool (o in serie con un solo processo), restituisce i risultati nell'ordine di arrivo."""
    processi = processi or PROCESSI
    out = []
    inizio = time.time()
    if processi <= 1:
        avvia_lavoro(lay_q)
        for k, l in enumerate(lavori, 1):
            r = funzione(l)
            out.append(r)
            if al_risultato:
                al_risultato(r)
            if k % 10 == 0 or k == len(lavori):
                print('[%s %d/%d, %.1f min]' % (etichetta, k, len(lavori), (time.time() - inizio) / 60), flush=True)
        return out
    with get_context('spawn').Pool(min(processi, max(1, len(lavori))), initializer=avvia_lavoro, initargs=(lay_q,)) as pool:
        for k, r in enumerate(pool.imap_unordered(funzione, lavori), 1):
            out.append(r)
            if al_risultato:
                al_risultato(r)
            if k % 10 == 0 or k == len(lavori):
                print('[%s %d/%d, %.1f min]' % (etichetta, k, len(lavori), (time.time() - inizio) / 60), flush=True)
    return out


# ---------------------------------------------------------------- tabella

def cartella(nome):
    d = os.path.join(CACHE28, nome)
    os.makedirs(d, exist_ok=True)
    return d


def file_pezzo(ns, n, fam, pezzo):
    return os.path.join(cartella('sim_%s_%d' % (ns, n)), '%s_%05d.json' % (fam, pezzo))


def fase_simulazioni(ns, n_per_famiglia, lay_q):
    """Scrive i pezzi mancanti di ns ('tab' o 'ctrl'); i pezzi gia' fatti non si rifanno."""
    npz = int(math.ceil(n_per_famiglia / float(PEZZO)))
    lavori = [(ns, fam, p, n_per_famiglia) for fam in F.FAMIGLIE for p in range(npz) if not (RIPRENDI and os.path.exists(file_pezzo(ns, n_per_famiglia, fam, p)))]
    print('simulazioni %s: %d pezzi da fare su %d' % (ns, len(lavori), npz * len(F.FAMIGLIE)), flush=True)
    def scrivi(r):
        (_, fam, p, _), out = r
        percorso = file_pezzo(ns, n_per_famiglia, fam, p)
        with open(percorso + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(out, f)
        os.replace(percorso + '.tmp', percorso)
    pool_lavori(lavoro_tabella, lavori, lay_q, etichetta='sim ' + ns, al_risultato=scrivi)


def carica_tabella(ns, n_per_famiglia):
    """(S, fam, U per famiglia, q, errori) con esattamente le prime n_per_famiglia simulazioni di ogni famiglia (quelle senza errore)."""
    npz = int(math.ceil(n_per_famiglia / float(PEZZO)))
    righe_S, fam_idx, U, qs, errori = [], [], [], [], 0
    for fi, fam in enumerate(F.FAMIGLIE):
        Uf = []
        for p in range(npz):
            with open(file_pezzo(ns, n_per_famiglia, fam, p), encoding='utf-8') as f:
                for r in json.load(f):
                    if r['k'] >= n_per_famiglia:
                        continue
                    if 'errore' in r:
                        errori += 1
                        continue
                    righe_S.append(r['s'])
                    fam_idx.append(fi)
                    qs.append(r['q'])
                    Uf.append(r['u'])
        U.append(np.array(Uf))
    return np.array(righe_S), np.array(fam_idx), U, np.array(qs), errori


def motore():
    """Il motore addestrato sulla tabella (si riusa se c'e' gia' sul disco per la stessa tabella)."""
    if 'motore' in _C:
        return _C['motore']
    S_, fam, U, qs, errori = carica_tabella('tab', N_TABELLA)
    chiave = '%d_%d_%d_%s' % (N_TABELLA, NT, len(S_), zlib.crc32(S_.tobytes()) & 0xffffffff)
    percorso = os.path.join(cartella('modello'), 'motore_%s.pkl' % chiave)
    if RIPRENDI and os.path.exists(percorso):
        with open(percorso, 'rb') as f:
            M = pickle.load(f)
    else:
        t0 = time.time()
        M = INF.Motore(F.FAMIGLIE, S_, fam, U, n_alberi=NT, n_alberi_par=max(60, 2 * NT // 3), n_jobs=max(1, PROCESSI))
        print('motore addestrato in %.1f min (errore fuori sacco della famiglia %.3f)' % ((time.time() - t0) / 60, M.errore_oob), flush=True)
        with open(percorso, 'wb') as f:
            pickle.dump(M, f)
    M.n_errori_tabella = errori
    _C['motore'] = M
    return M


# ---------------------------------------------------------------- analisi di un testo (un quarto = una osservazione)

def analizza_osservazioni(M, osservazioni, lay_q, n_ppc, seme=1, etichetta='ppc'):
    """`osservazioni`: lista di (chiave, vettore di sintesi, quarto). Per ognuna: scelta di famiglia, posteriori per famiglia, distanza dal
    piu' vicino e verifica predittiva (n_ppc testi per famiglia). Restituisce chiave -> dizionario."""
    ris = OrderedDict()
    lavori = []
    for chiave, s, q in osservazioni:
        r = OrderedDict(q=q, scelta=M.scelta_famiglia(s), post=OrderedDict())
        for fi, fam in enumerate(F.FAMIGLIE):
            camp, dmin, k = M.posteriore(s, fi, seme=seme)
            dnn, pnn = M.distanza_dal_piu_vicino(s, fi, seme=seme)
            r['post'][fam] = dict(camp=camp, riass=M.riassunto(camp), dmin_proiezione=dmin, accettate=k, dist_piu_vicino=dnn, p_piu_vicino=pnn)
            if n_ppc > 0:
                rng = np.random.default_rng(F.seme28('sceltapp', chiave, fam) % (2 ** 32))
                righe = camp[rng.choice(len(camp), size=n_ppc, replace=len(camp) < n_ppc)]
                lavori.append((chiave, fam, q, righe.tolist(), F.seme28('pp', chiave, fam)))
        ris[chiave] = r
    if lavori:
        for chiave, fam, Mat in pool_lavori(lavoro_ppc, lavori, lay_q, etichetta=etichetta):
            s = next(s_ for c_, s_, _ in osservazioni if c_ == chiave)
            ris[chiave]['post'][fam]['ppc'] = INF.ppc(s, Mat, S.NOMI) if len(Mat) >= 20 else None
            ris[chiave]['post'][fam]['n_ppc'] = int(len(Mat))
    return ris


def verdetto(quarti, soglia_ppc=INF.SOGLIA_PPC):
    """Da piu' quarti (dizionari di `analizza_osservazioni`): per famiglia probabilita' media, quarti in cui e' la preferita, quarti in cui la
    verifica passa e il rms_z medio; la famiglia preferita (prob. media >= 0,5 e preferita in >= 3 quarti), se compatibile, e quale
    famiglia arriva piu' vicino (rms_z minimo)."""
    nq = len(quarti)
    d = OrderedDict()
    for fi, fam in enumerate(F.FAMIGLIE):
        probs = [q['scelta']['prob'][fi] for q in quarti]
        pp = [q['post'][fam].get('ppc') for q in quarti]
        d[fam] = OrderedDict(prob_media=float(np.mean(probs)), prob_per_quarto=[float(x) for x in probs],
                             quarti_preferita=int(sum(1 for q in quarti if q['scelta']['preferita'] == fi)),
                             quarti_ppc_ok=int(sum(1 for x in pp if x is not None and x['p'] >= soglia_ppc)),
                             p_ppc=[(x['p'] if x else None) for x in pp],
                             rms_z_medio=(float(np.mean([x['rms_z'] for x in pp if x])) if any(pp) else None),
                             mancate=OrderedDict(Counter(m for x in pp if x for m in x['mancate']).most_common()))
    cand = max(F.FAMIGLIE, key=lambda f: d[f]['prob_media'])
    preferita = d[cand]['prob_media'] >= PROB_MIN and d[cand]['quarti_preferita'] >= min(QUARTI_MIN, nq)
    compat = preferita and d[cand]['quarti_ppc_ok'] >= min(QUARTI_MIN, nq)
    vicine = [f for f in F.FAMIGLIE if d[f]['rms_z_medio'] is not None]
    piu_vicina = min(vicine, key=lambda f: d[f]['rms_z_medio']) if vicine else None
    if preferita and compat:
        esito = 'famiglia %s preferita e compatibile' % cand
    elif preferita:
        esito = 'famiglia %s preferita ma NON compatibile (verifica predittiva fallita)' % cand
    else:
        esito = 'nessuna famiglia preferita'
    return OrderedDict(per_famiglia=d, candidata=cand, preferita=bool(preferita), compatibile=bool(compat), vince=(cand if compat else None),
                       piu_vicina=piu_vicina, esito=esito)


def posteriore_misto(quarti, fam):
    """Campioni di parametri dei quattro quarti messi insieme (miscuglio)."""
    return np.vstack([q['post'][fam]['camp'] for q in quarti])


def parametri_stimati(M, quarti):
    """Per ogni famiglia e parametro: mediana e intervallo al 90% del miscuglio dei quarti, nella scala vera dei parametri, R^2, 'stimabile'
    e 'sui bordi dell'a priori' (intervallo piu' largo del 90% dell'a priori o mediana a meno del 5% da un bordo)."""
    out = OrderedDict()
    for fi, fam in enumerate(F.FAMIGLIE):
        camp = posteriore_misto(quarti, fam)
        nomi = F.nomi_parametri(fam)
        stima = M.stimabili(fi)
        par = OrderedDict()
        for j, nome in enumerate(nomi):
            lo, med, hi = (float(np.quantile(camp[:, j], p)) for p in (0.05, 0.5, 0.95))
            conv = [F.da_unita(fam, [x if i == j else 0.5 for i in range(len(nomi))])[nome] for x in (lo, med, hi)]
            per_q = [float(np.median(q['post'][fam]['camp'][:, j])) for q in quarti]
            par[nome] = OrderedDict(mediana=conv[1], q05=conv[0], q95=conv[2], R2=float(M.r2[fi][j]), stimabile=bool(stima[j]),
                                    largo=bool(hi - lo > 0.9), ai_bordi=bool(med < 0.05 or med > 0.95),
                                    mediane_quarti_unita=per_q)
        out[fam] = par
    return out


# ---------------------------------------------------------------- controlli

def controlli_positivi(M, lay_q):
    """Per ogni famiglia, N_CONTROLLO testi nuovi con parametri noti: la famiglia giusta e' ritrovata? i parametri stimabili sono dentro
    l'intervallo al 90%? Sui primi N_PPC_CTRL la verifica predittiva passa?"""
    S_, fam_idx, U, qs, errori = carica_tabella('ctrl', N_CONTROLLO)
    ris = OrderedDict()
    osservazioni, info = [], {}
    for fi, fam in enumerate(F.FAMIGLIE):
        Sf = S_[fam_idx == fi]
        Uf = U[fi]
        qf = qs[fam_idx == fi]
        for i in range(len(Sf)):
            info[(fam, i)] = (Uf[i], qf[i])
    scelte = {}
    cop = {fam: [[] for _ in F.nomi_parametri(fam)] for fam in F.FAMIGLIE}
    giuste = {fam: [] for fam in F.FAMIGLIE}
    conf = np.zeros((len(F.FAMIGLIE), len(F.FAMIGLIE)), dtype=int)
    errori_med = {fam: [[] for _ in F.nomi_parametri(fam)] for fam in F.FAMIGLIE}
    ppc_osserv = []
    for fi, fam in enumerate(F.FAMIGLIE):
        Sf = S_[fam_idx == fi]
        Uf = U[fi]
        qf = qs[fam_idx == fi]
        for i in range(len(Sf)):
            sc = M.scelta_famiglia(Sf[i])
            giuste[fam].append(sc['preferita'] == fi)
            conf[fi, sc['preferita']] += 1
            camp, _, _ = M.posteriore(Sf[i], fi, n=1000, seme=i)
            riass = M.riassunto(camp)
            for j in range(camp.shape[1]):
                cop[fam][j].append((riass[j][1], riass[j][2], Uf[i][j]))
                errori_med[fam][j].append(abs(riass[j][0] - Uf[i][j]))
            if i < N_PPC_CTRL:
                ppc_osserv.append((('ctrl', fam, i), Sf[i], int(qf[i]), fi, camp))
    # verifica predittiva dei primi N_PPC_CTRL controlli di ogni famiglia, solo sulla famiglia giusta
    lavori, ppc_ris = [], {}
    for chiave, s, q, fi, camp in ppc_osserv:
        rng = np.random.default_rng(F.seme28('cppc', *chiave) % (2 ** 32))
        righe = camp[rng.choice(len(camp), size=N_PPC, replace=len(camp) < N_PPC)]
        lavori.append((chiave, chiave[1], q, righe.tolist(), F.seme28('cpp', *chiave)))
    if lavori:
        for chiave, fam, Mat in pool_lavori(lavoro_ppc, lavori, lay_q, etichetta='ppc controlli'):
            s = next(s_ for c_, s_, _, _, _ in ppc_osserv if c_ == chiave)
            ppc_ris[chiave] = INF.ppc(s, Mat, S.NOMI) if len(Mat) >= 20 else None
    for fi, fam in enumerate(F.FAMIGLIE):
        par = OrderedDict()
        for j, nome in enumerate(F.nomi_parametri(fam)):
            v = cop[fam][j]
            par[nome] = OrderedDict(R2=float(M.r2[fi][j]), stimabile=bool(M.stimabili(fi)[j]),
                                    copertura=INF.copertura([x[2] for x in v], [(x[0], x[1]) for x in v]),
                                    errore_assoluto_mediano_unita=float(np.median(errori_med[fam][j])))
        pp = [ppc_ris[k] for k in ppc_ris if k[1] == fam and ppc_ris[k] is not None]
        ris[fam] = OrderedDict(testi=len(giuste[fam]), famiglia_ritrovata=float(np.mean(giuste[fam])), parametri=par,
                               ppc_testi=len(pp), ppc_passa=(float(np.mean([x['p'] >= INF.SOGLIA_PPC for x in pp])) if pp else None),
                               ppc_p_mediano=(float(np.median([x['p'] for x in pp])) if pp else None))
    esito = OrderedDict()
    for fam in F.FAMIGLIE:
        r = ris[fam]
        stim = [v for v in r['parametri'].values() if v['stimabile']]
        esito[fam] = OrderedDict(
            C1_famiglia=bool(r['famiglia_ritrovata'] >= SOGLIA_FAMIGLIA),
            C2_parametri=bool(stim and all(v['copertura'] >= SOGLIA_COPERTURA for v in stim)),
            parametri_stimabili=[n for n, v in r['parametri'].items() if v['stimabile']],
            C3_ppc_calibrata=bool(r['ppc_passa'] is not None and r['ppc_passa'] >= SOGLIA_PPC_POS))
    return OrderedDict(per_famiglia=ris, confusione=conf.tolist(), esito=esito, errori_tabella=int(errori))


def testi_negativi(seme=1):
    """Controlli negativi nell'impaginazione del vero: latino in chiaro (Plinio) e testo vero con le parole rimescolate fra tutte le pagine."""
    import cifrari_procedimenti as CP
    v = vero()
    lat = CP.testo_lingua_in_layout(CP.CHIAVI_CHIARO['latino'], v['layout'], seme)
    rim = CP.rimescola_tutto(v['pagine'], CP.seme_di('ia28neg', seme))
    return OrderedDict([('latino in chiaro', lat), ('testo rimescolato', rim)])


# ---------------------------------------------------------------- misure tenute fuori

def media_se(xs):
    xs = [x for x in xs if x is not None and x == x]
    if not xs:
        return None, None, 0
    m = float(np.mean(xs))
    se = float(np.std(xs, ddof=1) / math.sqrt(len(xs))) if len(xs) > 1 else None
    return m, se, len(xs)


def al_vero(valori, v_vero, tol_rel=SOGLIA_AL_VERO_REL):
    """Vero se il valore vero sta nell'intervallo di previsione dei libri (media +- t * sd * radice(1 + 1/B)) o entro `tol_rel` del vero."""
    xs = [x for x in valori if x is not None and x == x]
    if v_vero is None or len(xs) < 2:
        return None
    from scipy.stats import t as tdist
    B = len(xs)
    m, sd = float(np.mean(xs)), float(np.std(xs, ddof=1))
    prev = tdist.ppf(0.975, B - 1) * sd * math.sqrt(1.0 + 1.0 / B)
    return bool(abs(m - v_vero) <= max(prev, tol_rel * abs(v_vero)))


def quota_al_vero(misure_per_colonna, vero_val, quali):
    """Per una colonna (famiglia): quota delle misure `quali` al vero fra quelle calcolabili, e l'elenco delle mancate."""
    ok, mancate, tot = 0, [], 0
    for m in quali:
        r = al_vero(misure_per_colonna.get(m, []), vero_val.get(m))
        if r is None:
            continue
        tot += 1
        ok += int(r)
        if not r:
            mancate.append(m)
    return (ok / tot if tot else None), tot, mancate


def classe_giudice(auc):
    if auc is None:
        return 'non calcolabile'
    return 'regge' if auc <= GIUDICE_REGGE else 'grigia' if auc <= GIUDICE_VEDE else 'vede'


def confronta_con_v21(misure_f, misure_21, vero_val, quali):
    """Misura per misura: la famiglia e' piu' vicina al vero del v21? ('piu' vicina' / 'uguale' / 'piu' lontana' a 2 errori)."""
    out, cont = OrderedDict(), Counter()
    for m in quali:
        mf, sf, nf = media_se(misure_f.get(m, []))
        m2, s2, n2 = media_se(misure_21.get(m, []))
        v = vero_val.get(m)
        if mf is None or m2 is None or v is None:
            continue
        df, d2 = abs(mf - v), abs(m2 - v)
        e = math.sqrt((sf or 0.0) ** 2 + (s2 or 0.0) ** 2)
        lett = 'piu\' vicina' if df < d2 - 2.0 * e else 'piu\' lontana' if df > d2 + 2.0 * e else 'uguale entro l\'errore'
        out[m] = OrderedDict(famiglia=mf, v21=m2, vero=v, distanza_famiglia=df, distanza_v21=d2, lettura=lett)
        cont[lett] += 1
    return out, dict(cont)


def nome_libro(col, i, riallineato):
    return '%s_%d%s' % (col, i, '_al' if riallineato else '')


def fase_tenute_fuori(M, quarti_vero, lay_q):
    """Libri interi dalla posteriore di ogni famiglia + riferimenti, tutte le misure fuori stima; restituisce misure per colonna e vero."""
    import abc_tenute_fuori as TF
    import ia07_voynich_neurale as I7
    TF.LIBRI_DIR = cartella('libri')
    TF.MISURE_DIR = cartella('misure_fuori')
    os.environ['LIBRI_DIR28'], os.environ['MISURE_DIR28'] = TF.LIBRI_DIR, TF.MISURE_DIR
    c = I7.contesto_A()
    vere_pag = c['vere']
    lay_full = F.layout_di(vere_pag)
    ranghi = TF.ranghi_glifi(vere_pag)
    nomi_tutti = OrderedDict()                        # nome del libro -> (colonna, indice)
    for fam in F.FAMIGLIE:
        camp = posteriore_misto(quarti_vero, fam)
        rng = random.Random(F.seme28('libri', fam))
        for i in range(N_LIBRI):
            u = camp[rng.randrange(len(camp))]
            th = F.da_unita(fam, u.tolist())
            pag, _ = F.genera(fam, th, lay_full, F.seme28('libro', fam, i))
            TF.salva_libro(nome_libro(fam, i, False), pag)
            TF.salva_libro(nome_libro(fam, i, True), F.riallinea_glifi(pag, ranghi))
            nomi_tutti[nome_libro(fam, i, False)] = (fam, i)
    import cifrari_procedimenti as CP
    lat = CP.testo_lingua_in_layout(CP.CHIAVI_CHIARO['latino'], lay_full, 1)
    TF.salva_libro('ctrl_lat', lat)
    TF.salva_libro('ctrl_lat_al', F.riallinea_glifi(lat, ranghi))
    v21 = ['V21:%d' % k for k in (I7.CHIAVI_V21[:3] if PICCOLO else I7.CHIAVI_V21)] if USA_V21 else []
    nativi = [n for n in nomi_tutti] + ['ctrl_lat'] + v21 + ['vere']
    giudici = [nome_libro(f, i, True) for f in F.FAMIGLIE for i in range(N_LIBRI)] + [nome_libro('NB', i, False) for i in range(N_LIBRI)] \
        + ['ctrl_lat_al', 'ctrl:parole'] + v21
    struttura = giudici + ['vere']
    lavori = []
    if 'X' in COMPONENTI:
        lavori += [('X', n) for n in nativi]
    if 'R' in COMPONENTI:
        lavori += [('R', n, t, 1) for n in nativi for t in ('R', 'K')]
    if 'G' in COMPONENTI:
        lavori += [('G', n) for n in giudici]
    if 'S' in COMPONENTI:
        lavori += [('S', n) for n in struttura]
    if 'K' in COMPONENTI:
        lavori += [('K', f, giudici) for f in range(PIEGHE_K)]
    if 'D' in COMPONENTI:
        lavori += [('D', f, [n for n in struttura if n != 'vere']) for f in range(PIEGHE_K)]
    percorso = os.path.join(CACHE28, 'corse_fuori.jsonl')
    fatte = {}
    if RIPRENDI and os.path.exists(percorso):
        for riga in open(percorso, encoding='utf-8'):
            if riga.strip():
                r = json.loads(riga)
                if 'errore' not in r:
                    fatte[r['lavoro']] = r
    def ident(a):
        return '|'.join(str(x) if not isinstance(x, (list, tuple)) else '#%08x' % (zlib.crc32('|'.join(x).encode('utf-8')) & 0xffffffff) for x in a)
    da_fare = [a for a in lavori if ident(a) not in fatte]
    print('misure tenute fuori: %d lavori, %d da fare' % (len(lavori), len(da_fare)), flush=True)
    if da_fare:
        inizio = time.time()
        with get_context('spawn').Pool(min(PROCESSI, len(da_fare)), initializer=TF.avvia_processo) as pool:
            for k, r in enumerate(pool.imap_unordered(TF.lavoro, da_fare), 1):
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
                if 'errore' in r:
                    print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
                else:
                    fatte[r['lavoro']] = r
                if k % 5 == 0 or k == len(da_fare):
                    print('[tenute fuori %d/%d, %.1f min]' % (k, len(da_fare), (time.time() - inizio) / 60), flush=True)
    return dict(fatte=fatte, nomi=nomi_tutti, nativi=nativi, giudici=giudici, struttura=struttura, v21=v21, lavori=[ident(a) for a in lavori],
                pieghe=list(range(PIEGHE_K)))


def raccogli_misure(TFR):
    """Dai risultati dei lavori: per ogni libro un dizionario nome misura -> valore."""
    import abc_tenute_fuori as TF
    TF.LIBRI_DIR, TF.MISURE_DIR = cartella('libri'), cartella('misure_fuori')
    per_libro = {}
    for r in TFR['fatte'].values():
        t, n = r['tipo'], r.get('nome')
        if t in ('X', 'G', 'S'):
            per_libro.setdefault(n, {}).update({k: v for k, v in r.items() if k not in ('lavoro', 'tipo', 'nome', 'secondi', 'traccia')})
        elif t == 'R':
            per_libro.setdefault(n, {}).update({k: v for k, v in r.items() if k not in ('lavoro', 'tipo', 'nome', 'secondi', 'traccia')})
        elif t == 'D':
            f = r['lavoro']
            for k, a in r['D'].items():
                per_libro.setdefault(k, {}).setdefault('_D', {})[f] = a
    # D da piu' pieghe: somma delle pieghe diverse
    for n, d in per_libro.items():
        if '_D' in d:
            d['D'] = _D_da_pieghe(list(d['_D'].values()))
            del d['_D']
    k_ok = all(os.path.exists(os.path.join(TF.MISURE_DIR, 'K_f%d.pkl' % f)) for f in TFR['pieghe'])
    neg_K = None
    if 'K' in COMPONENTI and k_ok:
        aucs, neg_K = TF.auc_K(TFR['giudici'], TFR['pieghe'])
        for n, a in aucs.items():
            per_libro.setdefault(n, {})['AUC_K'] = a
    return per_libro, neg_K


def _D_da_pieghe(liste):
    a = sum(x[0] for x in liste)
    b = sum(x[1] for x in liste)
    c_ = sum(x[2] for x in liste)
    return float((a - c_) / b) if b > 0 else None


def tabella_per_colonna(TFR, per_libro):
    """colonna -> misura -> lista di valori (un valore per libro). NB: le misure che dipendono dai nomi dei glifi (giudici, struttura, D)
    stanno per NB (riallineati) e per NBn (nomi nativi); le altre solo per NB."""
    per_col = {c: {} for c in COLONNE}
    identita = set(GIUDICI) | {'copia_netta', 'lam', 'rho', 'G9', 'D'}
    for i in range(N_LIBRI):
        for fam in F.FAMIGLIE:
            nat, al = per_libro.get(nome_libro(fam, i, False), {}), per_libro.get(nome_libro(fam, i, True), {})
            for m in MISURE_FUORI + GIUDICI:
                v = al.get(m) if m in identita else nat.get(m)
                per_col[fam].setdefault(m, []).append(v)
            if fam == 'NB':
                for m in identita:
                    per_col['NBn'].setdefault(m, []).append(nat.get(m))
                for m in MISURE_FUORI:
                    if m not in identita:
                        per_col['NBn'].setdefault(m, []).append(nat.get(m))
    for n in TFR['v21']:
        b = per_libro.get(n, {})
        for m in MISURE_FUORI + GIUDICI:
            per_col['V21'].setdefault(m, []).append(b.get(m))
    return per_col


# ---------------------------------------------------------------- letture preregistrate

def letture(ver_v, par, ctrl, neg, tf):
    """Le letture L1-L6. Ognuna dichiara da quali controlli dipende; se non sono superati e' 'non leggibile' (i numeri restano)."""
    L = OrderedDict()
    es = ctrl['esito']
    neg_ok = all(not neg[t]['vince'] for t in neg) if neg else False
    L['controlli'] = OrderedDict(
        C1_famiglia_ritrovata={f: es[f]['C1_famiglia'] for f in F.FAMIGLIE},
        C2_parametri_ritrovati={f: es[f]['C2_parametri'] for f in F.FAMIGLIE},
        C3_ppc_calibrata={f: es[f]['C3_ppc_calibrata'] for f in F.FAMIGLIE},
        C4_negativi_nessuna_famiglia_vince={t: (not neg[t]['vince']) for t in neg} if neg else None,
        tutti_i_negativi=bool(neg_ok))
    base = neg_ok
    v = ver_v
    cand = v['candidata']
    leggibile_l1 = bool(base and es[cand]['C1_famiglia'] and es[cand]['C3_ppc_calibrata'])
    L['L1_famiglia_migliore'] = OrderedDict(
        esito=v['esito'], candidata=cand, preferita=v['preferita'], compatibile=v['compatibile'], piu_vicina_rms_z=v['piu_vicina'],
        leggibile=leggibile_l1, per_famiglia=v['per_famiglia'])
    L['L2_parametri'] = OrderedDict()
    for fam in F.FAMIGLIE:
        ok = bool(base and es[fam]['C2_parametri'])
        L['L2_parametri'][fam] = OrderedDict(
            leggibile=ok, parametri=OrderedDict((n, OrderedDict(mediana=p['mediana'], q05=p['q05'], q95=p['q95'], R2=p['R2'],
                                                                stimabile=p['stimabile'], largo=p['largo'], ai_bordi=p['ai_bordi']))
                                                for n, p in par[fam].items() if p['stimabile']),
            non_stimabili=[n for n, p in par[fam].items() if not p['stimabile']])
    nb = par['NB']['p_eco']
    L['L5_naibbe_senza_eco'] = OrderedDict(
        p_eco_stimabile=nb['stimabile'], p_eco_q05=nb['q05'], p_eco_q95=nb['q95'], p_eco_mediana=nb['mediana'],
        eco_necessaria=(bool(nb['q05'] > 0.05) if nb['stimabile'] else None),
        leggibile=bool(base and es['NB']['C2_parametri'] and nb['stimabile']))
    if tf:
        L['L3_tenute_fuori'] = tf['L3']
        L['L4_contro_v21'] = tf['L4']
        L['L6_giudici'] = tf['L6']
    return L


def esito_negativo(quarti):
    v = verdetto(quarti)
    return OrderedDict(vince=v['vince'], esito=v['esito'], candidata=v['candidata'], piu_vicina=v['piu_vicina'],
                       prob_media={f: v['per_famiglia'][f]['prob_media'] for f in F.FAMIGLIE},
                       quarti_ppc_ok={f: v['per_famiglia'][f]['quarti_ppc_ok'] for f in F.FAMIGLIE},
                       rms_z_medio={f: v['per_famiglia'][f]['rms_z_medio'] for f in F.FAMIGLIE})


def letture_fuori(per_libro, per_col, TFR, neg_K, vero_val):
    """L3 (quota delle misure al vero per famiglia), L4 (contro il v21), L6 (giudici) dalle misure tenute fuori."""
    L3 = OrderedDict()
    for col in ('CV', 'NB', 'NBn', 'VT'):
        quota, tot, mancate = quota_al_vero(per_col[col], vero_val, MISURE_FUORI)
        L3[col] = OrderedDict(quota_al_vero=quota, misure_confrontate=tot, mancate=mancate,
                              al_vero=(None if quota is None or tot < 8 else bool(quota >= SOGLIA_QUOTA_AL_VERO)),
                              per_misura=OrderedDict((m, OrderedDict(media=media_se(per_col[col].get(m, []))[0], vero=vero_val.get(m),
                                                                      al_vero=al_vero(per_col[col].get(m, []), vero_val.get(m))))
                                                     for m in MISURE_FUORI))
    L4 = OrderedDict()
    if TFR['v21']:
        for col in ('CV', 'NB', 'VT'):
            conf, cont = confronta_con_v21(per_col[col], per_col['V21'], vero_val, MISURE_FUORI + GIUDICI)
            L4[col] = OrderedDict(conteggio=cont, per_misura=conf)
    # giudici
    L6 = OrderedDict()
    cp = per_libro.get('ctrl:parole', {})
    valido = OrderedDict(
        parole_rimescolate_e231=(cp.get('AUC_e231') is not None and cp['AUC_e231'] >= POS_GIUDICE),
        parole_rimescolate_e266=(cp.get('AUC_e266') is not None and cp['AUC_e266'] >= POS_GIUDICE),
        negativo_K_in_banda=(neg_K is not None and NEG_BANDA[0] <= neg_K <= NEG_BANDA[1]), negativo_K=neg_K)
    L6['validita_giudici'] = valido
    for col in ('CV', 'NB', 'NBn', 'VT', 'V21'):
        riga = OrderedDict()
        for g in GIUDICI:
            m, se, n = media_se(per_col[col].get(g, []))
            riga[g] = OrderedDict(media=m, se=se, libri=n, classe=classe_giudice(m))
        L6[col] = riga
    return dict(L3=L3, L4=L4, L6=L6)


# ---------------------------------------------------------------- scrittura dei risultati

def fmt(x, d=3):
    if x is None:
        return '-'
    if isinstance(x, bool):
        return 'si' if x else 'no'
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return ('%.' + str(d) + 'f') % x


def scrivi_md(R, percorso):
    L = R['letture']
    o = ['# IA28 (ia28): l\'inferenza per simulazione sui procedimenti (solo numeri)', '',
         'Tre famiglie di procedimenti con parametri stimati (ABC) su 29 statistiche classiche di quarti di libro; controllo su misure tenute fuori su libri interi. '
         'Non e\' una decifrazione. Modalita: %s. Tabella: %d testi per famiglia.' % ('PROVA su testi non Voynich (SOLO_CONTROLLI)' if R['solo_controlli'] else 'testo vero', R['n_tabella']), '']
    c = L['controlli']
    o += ['## Controlli', '', '| famiglia | C1 famiglia ritrovata | C2 parametri nell\'intervallo | C3 verifica predittiva calibrata |', '|---|---|---|---|']
    for f in F.FAMIGLIE:
        r = R['controlli_positivi']['per_famiglia'][f]
        o.append('| %s | %s (%s) | %s | %s (%s) |' % (f, fmt(c['C1_famiglia_ritrovata'][f]), fmt(r['famiglia_ritrovata'], 2), fmt(c['C2_parametri_ritrovati'][f]),
                                                  fmt(c['C3_ppc_calibrata'][f]), fmt(r['ppc_passa'], 2)))
    o += ['', 'Controlli negativi (nessuna famiglia deve vincere): %s' % ', '.join('%s: %s (%s)' % (t, fmt(v), R['negativi'][t]['esito']) for t, v in (c['C4_negativi_nessuna_famiglia_vince'] or {}).items()), '']
    o += ['## Parametri stimabili e coperture (controlli positivi)', '', '| famiglia | parametro | R2 fuori sacco | stimabile | copertura 90% |', '|---|---|---|---|---|']
    for f in F.FAMIGLIE:
        for n, p in R['controlli_positivi']['per_famiglia'][f]['parametri'].items():
            o.append('| %s | %s | %s | %s | %s |' % (f, n, fmt(p['R2'], 2), fmt(p['stimabile']), fmt(p['copertura'], 2)))
    l1 = L['L1_famiglia_migliore']
    o += ['', '## L1 famiglia migliore', '', 'Esito: **%s** (leggibile: %s). Piu\' vicina per scarto medio (rms z): %s.' % (l1['esito'], fmt(l1['leggibile']), l1['piu_vicina_rms_z']), '',
          '| famiglia | prob. media | quarti preferita | quarti con verifica passata | rms z medio | statistiche mancate (n. quarti) |', '|---|---|---|---|---|---|']
    for f in F.FAMIGLIE:
        d = l1['per_famiglia'][f]
        o.append('| %s | %s | %d | %d | %s | %s |' % (f, fmt(d['prob_media'], 2), d['quarti_preferita'], d['quarti_ppc_ok'], fmt(d['rms_z_medio'], 2),
                                                    ', '.join('%s (%d)' % kv for kv in list(d['mancate'].items())[:8])))
    o += ['', '## L2 parametri (mediana e intervallo al 90%, solo parametri stimabili)', '']
    for f in F.FAMIGLIE:
        l2 = L['L2_parametri'][f]
        o += ['**%s** (leggibile: %s; non stimabili: %s)' % (f, fmt(l2['leggibile']), ', '.join(l2['non_stimabili']) or 'nessuno'), '',
              '| parametro | mediana | q05 | q95 | R2 | largo | ai bordi |', '|---|---|---|---|---|---|---|']
        for n, p in l2['parametri'].items():
            o.append('| %s | %s | %s | %s | %s | %s | %s |' % (n, fmt(p['mediana']), fmt(p['q05']), fmt(p['q95']), fmt(p['R2'], 2), fmt(p['largo']), fmt(p['ai_bordi'])))
        o.append('')
    l5 = L['L5_naibbe_senza_eco']
    o += ['## L5 Naibbe vero senza eco', '', 'p_eco: mediana %s, intervallo %s - %s; l\'eco e\' necessaria (limite basso sopra 0,05): %s (leggibile: %s)' % (
        fmt(l5['p_eco_mediana']), fmt(l5['p_eco_q05']), fmt(l5['p_eco_q95']), fmt(l5['eco_necessaria']), fmt(l5['leggibile'])), '']
    if 'L3_tenute_fuori' in L:
        o += ['## L3 misure tenute fuori al vero', '', '| famiglia | quota al vero | misure confrontate | al vero | mancate |', '|---|---|---|---|---|']
        for col, d in L['L3_tenute_fuori'].items():
            o.append('| %s | %s | %s | %s | %s |' % (COLONNE[col], fmt(d['quota_al_vero'], 2), fmt(d['misure_confrontate']), fmt(d['al_vero']), ', '.join(d['mancate'])))
        o += ['', '## L4 contro il v21 (misura per misura: famiglia piu\' vicina / uguale / piu\' lontana del v21)', '']
        for col, d in L['L4_contro_v21'].items():
            o.append('- %s: %s' % (COLONNE[col], d['conteggio']))
        o += ['', '## L6 giudici (AUC media sui libri; classe: regge <= 0,62, grigia <= 0,65, vede)', '',
              'Validita dei giudici: %s' % L['L6_giudici']['validita_giudici'], '', '| colonna | e231 | e266 | A | K |', '|---|---|---|---|---|']
        for col in ('CV', 'NB', 'NBn', 'VT', 'V21'):
            r = L['L6_giudici'][col]
            o.append('| %s | %s | %s | %s | %s |' % (COLONNE[col], *[('%s (%s)' % (fmt(r[g]['media'], 3), r[g]['classe'])) for g in GIUDICI]))
    o += ['', '## Dichiarato', '', *['- ' + x for x in R['dichiarazioni']]]
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(o) + '\n')


DICHIARAZIONI = [
    'Le statistiche di sintesi (29) sono classiche e a basso costo; le misure di rete, di struttura e i giudici stanno FUORI dalla stima. Le misure di '
    'copia netta, rho e Λ di ia09 sono parenti stretti delle statistiche d\'eco di sintesi: sono "fuori" nel senso che non sono usate, non che siano indipendenti.',
    'L\'osservazione e\' ognuno dei quattro quarti del testo (pagine a giro), analizzato per conto suo; le simulazioni sono quarti con la stessa impaginazione.',
    'I testi delle famiglie CV e VT hanno glifi con nomi tirati a caso: per i giudici i libri sono riallineati per rango di frequenza ai glifi del vero '
    '(non cambia nessuna struttura). Per NB si riportano anche i nomi nativi (colonna NBn).',
    'Il v21 non e\' una famiglia a parametri liberi (i suoi parametri vengono dal Voynich e il voynichizzatore non si tocca): e\' una colonna di riferimento.',
    'Il Voynich e\' eterogeneo (lingue A e B, sezioni, mani); le famiglie scrivono un testo omogeneo. Una verifica predittiva fallita puo\' dipendere anche da questo.',
]


# ---------------------------------------------------------------- prove del codice

def prova_codice():
    """Prove interne (tutte devono essere vere): famiglie, statistiche, motore e la logica delle letture."""
    ris = OrderedDict()
    for nome, f in (('famiglie', F.prova_famiglie), ('statistiche', S.prova_statistiche), ('motore', INF.prova_inferenza)):
        for k, v in f().items():
            ris['%s: %s' % (nome, k)] = bool(v)
    # logica di al_vero e delle classi dei giudici
    ris['al_vero: dentro l\'intervallo di previsione'] = al_vero([1.0, 1.1, 0.9, 1.05, 0.95, 1.02, 0.98, 1.0], 1.0) is True
    ris['al_vero: lontano dal vero'] = al_vero([1.0, 1.1, 0.9, 1.05, 0.95, 1.02, 0.98, 1.0], 2.0) is False
    ris['al_vero: entro il 5% anche con libri quasi uguali'] = al_vero([1.0, 1.0, 1.0001, 1.0], 1.04) is True
    ris['al_vero: senza libri None'] = al_vero([None], 1.0) is None
    ris['classe_giudice'] = (classe_giudice(0.55), classe_giudice(0.63), classe_giudice(0.9), classe_giudice(None)) == ('regge', 'grigia', 'vede', 'non calcolabile')
    # pezzi della tabella: stesso pezzo, stessi testi (determinismo del lavoro)
    lay = [[('P%03d' % (10 * q + i), [(j == 0, 6 + (i + j) % 4) for j in range(10)]) for i in range(6)] for q in range(N_QUARTI)]
    avvia_lavoro(lay)
    global PEZZO
    p0 = PEZZO
    PEZZO = 4
    try:
        a = lavoro_tabella(('prova', 'CV', 0, 100))
        b = lavoro_tabella(('prova', 'CV', 0, 100))
        c = lavoro_tabella(('prova', 'CV', 1, 100))
    finally:
        PEZZO = p0
    ris['tabella: pezzo deterministico'] = a == b
    ris['tabella: pezzi diversi, testi diversi'] = a[1][0]['s'] != c[1][0]['s']
    ris['tabella: 4 testi per pezzo, 29 statistiche, nessun errore'] = len(a[1]) == 4 and all('errore' not in r and len(r['s']) == 29 for r in a[1])
    # verdetto su dati finti: la famiglia 1 vince e passa
    def fq(prob, ppcp):
        post = {fam: dict(ppc=dict(p=ppcp[i], rms_z=1.0 + i, mancate=[]), camp=np.zeros((2, 2))) for i, fam in enumerate(F.FAMIGLIE)}
        return dict(scelta=dict(prob=prob, preferita=int(np.argmax(prob))), post=post)
    quarti = [fq([0.1, 0.8, 0.1], [0.01, 0.4, 0.2]) for _ in range(4)]
    v = verdetto(quarti)
    ris['verdetto: preferita e compatibile'] = v['vince'] == F.FAMIGLIE[1] and v['piu_vicina'] == F.FAMIGLIE[0]
    quarti = [fq([0.1, 0.8, 0.1], [0.01, 0.01, 0.2]) for _ in range(4)]
    v = verdetto(quarti)
    ris['verdetto: preferita ma non compatibile'] = v['vince'] is None and v['preferita'] and not v['compatibile']
    quarti = [fq([0.4, 0.3, 0.3], [0.5, 0.5, 0.5]) for _ in range(4)]
    ris['verdetto: nessuna preferenza'] = not verdetto(quarti)['preferita']
    # classi di nomi dei libri
    ris['nome_libro'] = nome_libro('CV', 3, True) == 'CV_3_al' and nome_libro('NB', 0, False) == 'NB_0'
    # il riallineamento dei nomi non rompe la divisione in glifi EVA
    import misure as MIS
    dividi = MIS.divisore(MIS.GLIFI_EVA)
    pag, _ = F.genera('CV', F.campiona('CV', random.Random(2)), lay[0], 1)
    al = F.riallinea_glifi(pag, ['o', 'a', 'e', 'y', 'd', 'ch', 'i', 'l', 'k', 't', 'r', 's', 'n', 'sh', 'q', 'p', 'f', 'm', 'cth', 'ckh'])
    ok = all(tuple(dividi(''.join(w))) == w for rows in al.values() for _, ws in rows for w in ws)
    ris['riallineamento: le parole si ridividono come prima (con i 20 glifi piu\' frequenti EVA)'] = ok
    return ris


# ---------------------------------------------------------------- principale

def main():
    inizio = time.time()
    os.makedirs(USCITA, exist_ok=True)
    os.makedirs(CACHE28, exist_ok=True)
    print('ia28: SOLO_CONTROLLI=%s FASI28=%s PROCESSI=%d N_TABELLA28=%d CACHE28=%s' % (SOLO_CONTROLLI, FASI28, PROCESSI, N_TABELLA, CACHE28), flush=True)
    prove = prova_codice()
    for k, v in prove.items():
        if not v:
            print('PROVA FALLITA: %s' % k, flush=True)
    if not all(prove.values()):
        raise SystemExit('FERMO: la prova del codice non e\' superata')
    print('prova del codice superata (%d voci)' % len(prove), flush=True)
    if not any(x in FASI28 for x in 'SCVTL'):
        return
    R = OrderedDict(solo_controlli=SOLO_CONTROLLI, n_tabella=N_TABELLA, prova_codice=prove, dichiarazioni=DICHIARAZIONI, famiglie=OrderedDict(
        (f, OrderedDict(nome=F.NOMI_FAMIGLIE[f], priori=OrderedDict((k, list(v)) for k, v in F.PRIORI[f].items()))) for f in F.FAMIGLIE),
        statistiche=S.NOMI, fasi=FASI28)
    v = vero()
    lay_q = v['lay_q']
    R['quarti'] = dict(pagine=[len(x) for x in v['pag_q']], parole=[F.parole_totali(x) for x in lay_q])
    if 'S' in FASI28:
        fase_simulazioni('tab', N_TABELLA, lay_q)
    M = motore() if any(x in FASI28 for x in 'CVTL') else None
    R['motore'] = OrderedDict(errore_fuori_sacco_famiglia=M.errore_oob, confusione_fuori_sacco=M.confusione_oob.tolist(),
                              r2_parametri={f: [float(x) for x in M.r2[i]] for i, f in enumerate(F.FAMIGLIE)}, errori_tabella=M.n_errori_tabella) if M else None
    ctrl = neg = None
    if 'C' in FASI28 and M:
        fase_simulazioni('ctrl', N_CONTROLLO, lay_q)
        ctrl = controlli_positivi(M, lay_q)
        R['controlli_positivi'] = ctrl
        negativi = testi_negativi()
        neg = OrderedDict()
        R['negativi'] = OrderedDict()
        for nome, pag in negativi.items():
            Sq = vettore_quarti(pag, v['tipo'])
            oss = [(('neg', nome, q), Sq[q], q) for q in range(N_QUARTI)]
            an = analizza_osservazioni(M, oss, lay_q, N_PPC, etichetta='ppc neg')
            quarti = [an[o[0]] for o in oss]
            neg[nome] = esito_negativo(quarti)
            R['negativi'][nome] = neg[nome]
    ver = par = None
    quarti_vero = None
    if 'V' in FASI28 and M:
        Sq = vettore_quarti(v['pagine'], v['tipo'])
        oss = [(('vero', q), Sq[q], q) for q in range(N_QUARTI)]
        an = analizza_osservazioni(M, oss, lay_q, N_PPC, etichetta='ppc vero')
        quarti_vero = [an[o[0]] for o in oss]
        ver = verdetto(quarti_vero)
        par = parametri_stimati(M, quarti_vero)
        R['vero'] = OrderedDict(statistiche_quarti=[[float(x) for x in r] for r in Sq], verdetto=ver, parametri=par,
                                piu_vicino_nella_tabella=[[q['post'][f]['dist_piu_vicino'] for f in F.FAMIGLIE] for q in quarti_vero],
                                p_piu_vicino=[[q['post'][f]['p_piu_vicino'] for f in F.FAMIGLIE] for q in quarti_vero])
        with open(os.path.join(cartella('modello'), 'posteriori_vero.pkl'), 'wb') as f:
            pickle.dump({fam: posteriore_misto(quarti_vero, fam) for fam in F.FAMIGLIE}, f)
    tf = None
    if 'T' in FASI28 and M:
        if quarti_vero is None:
            with open(os.path.join(cartella('modello'), 'posteriori_vero.pkl'), 'rb') as f:
                mix = pickle.load(f)
            quarti_vero = [dict(post={fam: dict(camp=mix[fam]) for fam in F.FAMIGLIE})]
        TFR = fase_tenute_fuori(M, quarti_vero, lay_q)
        per_libro, neg_K = raccogli_misure(TFR)
        per_col = tabella_per_colonna(TFR, per_libro)
        vero_val = {k: x for k, x in per_libro.get('vere', {}).items() if isinstance(x, (int, float))}
        tf = letture_fuori(per_libro, per_col, TFR, neg_K, vero_val)
        R['tenute_fuori'] = OrderedDict(vero=vero_val, per_libro={n: {k: x for k, x in d.items() if isinstance(x, (int, float)) or x is None}
                                                                 for n, d in per_libro.items()},
                                        lavori_con_errore=[r['lavoro'] for r in TFR['fatte'].values() if 'errore' in r], componenti=COMPONENTI)
    if 'L' in FASI28 and ctrl and ver and par:
        R['letture'] = letture(ver, par, ctrl, neg, tf)
        R['secondi'] = round(time.time() - inizio, 1)
        base = os.path.join(USCITA, NOME)
        with open(base + '.json', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(R, f, ensure_ascii=False, indent=1, default=float)
        scrivi_md(R, base + '.md')
        print('scritto %s.json e .md (%.1f min)' % (base, (time.time() - inizio) / 60), flush=True)
    else:
        print('fasi eseguite: %s (letture non scritte: servono C, V ed L)' % FASI28, flush=True)


if __name__ == '__main__':
    main()
