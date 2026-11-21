# -*- coding: utf-8 -*-
"""Esperimento IA21 (ia21): l'allievo e l'esaminatore.

Idea di Davide (21/11/2026): "un'IA che impari a farlo simile, che si alleni da sola a prove ed errori fino a che non riesce, e da
queste prove capiamo". Qui l'allievo e' il generatore di ia07 (GRU 2 x 256, pieghe per foglio; o un modello di ia20, vedi
`MODELLO_PARTENZA`) e a ogni giro:
  1. scrive un serbatoio di pagine candidate (C copie di ogni pagina dei fogli su cui si e' addestrato);
  2. si addestra un ESAMINATORE nuovo (esaminatore_rete.py: lettore di pagina, GRU nei due versi + attenzione) a distinguere le pagine
     vere dalle pagine scritte dall'allievo in tutti i giri fino a quello (meta' del giro in corso, meta' dei precedenti);
  3. dal serbatoio si tiene, per ogni pagina, la candidata che l'esaminatore trova piu' vera (la migliore di C) e l'allievo si rifinisce
     su pagine vere piu' queste (auto-distillazione, scelta per rigetto: peso 1 per le vere, PESO21 per le scelte);
  4. registro del giro: AUC dell'esaminatore sull'allievo prima e dopo (su pagine di fogli mai visti), che cosa smaschera, e i
     GIUDICI TENUTI DA PARTE (giudici del paper e231 ed e266, K, A: mai usati nell'allenamento ne' nella scelta delle pagine) sui libri
     dell'allievo, piu' le guardie (copia a memoria, parole nuove, varieta' fra pagine, ripetizioni, tenuta sulla validazione vera).
Arresto (preregistrazioni/ia21.md): N giri, oppure giudice 2 e K sotto 0,62, oppure 3 giri senza miglioramento, oppure una guardia
violata (allora vale l'ultimo giro valido). Alla fine: 20 libri nuovi giudicati dai giudici tenuti da parte, misure di struttura.
Controlli: lo stesso percorso su un testo non Voynich (latino o sintetico nella disposizione del Voynich, SOLO_CONTROLLI=1) deve
migliorare; il percorso con esaminatore CIECO (PERCORSO=cieco, etichette a caso) non deve migliorare.

    # fase 0 (basi, giro 0, controlli dei giudici; comune a vero e cieco), poi i giri:
    nohup bash strumenti/coda.sh ia21 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=6,FASI=0:ia21" > /dev/null 2>&1 &
    nohup bash strumenti/coda.sh ia21v --dopo ia21 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=6,RIPRENDI=1,FASI=GFS:ia21" ...
    SOLO_CONTROLLI=1 PICCOLO21=1 USCITA=<cartella fuori dal repo> python esperimenti/ia21_allievo_esaminatore.py   (prova su latino)

Variabili d'ambiente (nessuna contiene virgole ne' due punti, perche' strumenti/coda.sh divide le impostazioni su quelli):
  PERCORSO (vero | cieco; predefinito vero), TESTO_PROVA (latino | sintetico | locale, solo con SOLO_CONTROLLI), MODELLO_PARTENZA (gru, o
  modulo.funzione), REPLICA_PARTENZA (0), CACHE21 (cartella di modelli, pagine, registri), N_GIRI21 (12), C21 (8), CVAL21 (2), PESO21 (1.0),
  EPOCHE_AFFINA21 (1), LR_AFFINA21 (0,0005), L_MON21 (3), N_FIN21 (20), N_STR21 (6), EPOCHE_ES21 (25), PAZIENZA_ES21 (6), STRUTTURA21
  (1 solo per il percorso vero sul Voynich), PICCOLO21 (solo prove), RIFAI (cancella i risultati del percorso e rifa'), MODELLI_IA07
  (cartella dei modelli di ia07, per il Voynich), e quelle gia' note: PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere 0 G F S;
  predefinito 0GFS), SOLO_CONTROLLI, USCITA e quelle di ia07 per i modelli di base dei controlli (STRATI, NASCOSTO, EPOCHE_MAX, PASSI_A ...).

Uscite (solo numeri e nomi di pagina, mai parole): risultati/ia21_<testo>_<percorso>.json e .md e ia21_corse_<testo>_<percorso>.jsonl.
Modelli, pagine scritte, registri dei giri e libri finali in dati/cache/ia21 (protetti, non si committano).
"""
import json, math, os, pickle, random, re, shutil, statistics, sys, time, warnings
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402  (disposizione, pieghe, giudici del paper, giudice A, copia, modelli di base)
import imitatore_misure as MS  # noqa: E402  (K, copia netta, D, contatto, ripetizioni)
import rifarlo_ritocchi as R  # noqa: E402
import allievo_gru as AG  # noqa: E402
import esaminatore_rete as ES  # noqa: E402

G = I7.ia01
NOME = 'ia21_allievo_esaminatore'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
PICCOLO = os.environ.get('PICCOLO21') == '1'
TESTO = (os.environ.get('TESTO_PROVA') or 'latino') if SOLO_CONTROLLI else 'voynich'
if SOLO_CONTROLLI and TESTO in ('sintetico', 'locale'):
    import allievo_prove  # noqa: E402
    I7.latino = getattr(allievo_prove, TESTO)
elif SOLO_CONTROLLI and TESTO != 'latino':
    raise SystemExit('TESTO_PROVA: latino, sintetico o locale')
PERCORSO = os.environ.get('PERCORSO') or 'vero'
if PERCORSO not in ('vero', 'cieco'):
    raise SystemExit('PERCORSO: vero o cieco')
PARTENZA = os.environ.get('MODELLO_PARTENZA') or 'gru'
REPLICA_PARTENZA = int(os.environ.get('REPLICA_PARTENZA', 0))
_RADICE_STD = os.path.join(QUI, '..', 'dati', 'cache', 'ia21')
RADICE = os.environ.get('CACHE21') or (_RADICE_STD if os.path.abspath(USCITA) == os.path.abspath(os.path.join(QUI, '..', 'risultati'))
                                       else os.path.join(USCITA, 'ia21_cache'))
TESTO_DIR = os.path.join(RADICE, '%s_%s' % (TESTO, PARTENZA.replace('.', '_')))

# ---- parametri del disegno (fissati nella preregistrazione, prima di eseguire sul Voynich)
N_GIRI = int(os.environ.get('N_GIRI21', 12))
C_CAND = int(os.environ.get('C21', 3 if PICCOLO else 8))                 # candidate per pagina (migliore di C)
C_VAL = int(os.environ.get('CVAL21', 1 if PICCOLO else 2))               # candidate per pagina dei fogli di validazione (per l'esaminatore)
PESO = float(os.environ.get('PESO21', 1.0))                              # peso delle pagine scelte rispetto alle vere
EP_AFFINA = int(os.environ.get('EPOCHE_AFFINA21', 1))
LR_AFFINA = float(os.environ.get('LR_AFFINA21', 5e-4))
L_MON = int(os.environ.get('L_MON21', 1 if PICCOLO else 3))              # libri di monitoraggio per giro (e copie per l'AUC dell'esaminatore)
N_FIN = int(os.environ.get('N_FIN21', 3 if PICCOLO else 20))             # libri finali (e di partenza) per il confronto
N_STR = int(os.environ.get('N_STR21', 2 if PICCOLO else 6))              # libri per set nelle misure di struttura
EP_ES = int(os.environ.get('EPOCHE_ES21', 3 if PICCOLO else 25))
PAZ_ES = int(os.environ.get('PAZIENZA_ES21', 2 if PICCOLO else 6))
GUARDIE_FERMANO = os.environ.get('GUARDIE21', '1') == '1'                 # 0 solo per le prove del codice: le guardie si registrano ma non fermano
STRUTTURA = os.environ.get('STRUTTURA21', '1' if (PERCORSO == 'vero' and not SOLO_CONTROLLI) else '0') == '1'
PIEGHE = I7.PIEGHE
FASI = os.environ.get('FASI', '0GFS')
CHIAVI_V21 = I7.CHIAVI_V21[:2] if PICCOLO else I7.CHIAVI_V21

# ---- soglie (fissate nella preregistrazione)
POS_PAPER, NEG_BANDA = 0.95, (0.45, 0.55)           # controlli dei giudici del paper
POS_K, K_VEDE_V21 = 0.85, 0.65                       # controlli di K
SOGLIA_STOP = 0.62                                   # arresto: giudice 2 e K entrambi a o sotto questa soglia
PAZIENZA_GIRI, MIGLIORA_MIN = 3, 0.005               # arresto: 3 giri senza che la media dei tre giudici scenda di almeno 0,005
COPIA_5GRAMMI, COPIA_RIGHE = 0.002, 0.001            # guardia: copia a memoria (severa)
NUOVE_FASCIA = (0.6, 1.4)                            # guardia: parole nuove fra 0,6 e 1,4 volte il naturale
VARIETA_FASCIA, PEGGIORA_REL = (0.7, 1.4), 0.15      # guardia: varieta' fra pagine, rispetto al vero; vale solo se anche peggiorata del 15% sul giro 0
DEGENERA_VOLTE, DEGENERA_MIN = 3.0, 0.02             # guardia: si avvita
DEGRADO_BPC = 0.10                                   # guardia: bit per segno sulla validazione vera, al massimo +0,10 sul giro 0
ESAM_MIN = 0.65                                      # l'esaminatore e' valido se al giro 1 distingue l'allievo di partenza con AUC >= 0,65
MIN_EFFETTO = 0.01                                   # una differenza fra AUC di meno di 0,01 non conta, anche se oltre due errori
SOFFITTO, POS_CALO = 0.97, 0.03                      # controllo positivo: sotto il soffitto al giro 0; calo della media dei tre giudici >= 0,03
G9_NOME = 'G9 JSD pagina-manoscritto'

# ---- cartelle: i modelli di base di ia07 per il Voynich (sola lettura), i propri per i controlli
if TESTO == 'voynich':
    if os.environ.get('MODELLI_IA07'):
        I7.MODELLI = os.environ['MODELLI_IA07']
        I7.MODELLI_A = os.path.join(I7.MODELLI, 'giudiceA')
else:
    I7.MODELLI = os.path.join(TESTO_DIR, 'base')
    I7.MODELLI_A = os.path.join(TESTO_DIR, 'giudiceA')
if SOLO_CONTROLLI and 'ia07_modelli' in os.path.normpath(I7.MODELLI).split(os.sep)[-1] and not os.path.abspath(I7.MODELLI).startswith(os.path.abspath(USCITA)):
    raise SystemExit('in prova (SOLO_CONTROLLI) non si leggono i modelli di ia07 del Voynich')

_C = {}


# ---------------------------------------------------------------- cartelle, righe dei lavori, semi

def amb_dir(a):
    return os.path.join(TESTO_DIR, a)


def GD(t):
    """Cartella del giro t: il giro 0 (l'allievo di partenza) e' comune ai percorsi, gli altri sono del percorso."""
    return os.path.join(amb_dir('comuni' if t == 0 else PERCORSO), 'g%d' % t)


def ident(args):
    return '|'.join(str(a) for a in args)


def ambito(args):
    tipo = args[0]
    if tipo in ('lmA', 'base', 'scrivi0', 'ctrl', 'Kctrl', 'naturale'):
        return 'comuni'
    if tipo in ('misura', 'K', 'finale'):
        return 'comuni' if args[1] == 0 else PERCORSO
    if tipo == 'M':
        return PERCORSO if re.match(r'g[1-9]\d*fin:', args[1]) else 'comuni'
    if tipo == 'D':
        return 'comuni' if args[1] == 'comuni' else PERCORSO
    return PERCORSO


def file_riga(args):
    return os.path.join(amb_dir(ambito(args)), 'righe', ident(args).replace('|', '__').replace(':', '_') + '.json')


def riga(args):
    p = file_riga(args)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def scrivi_riga(args, r):
    p = file_riga(args)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + '.tmp', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(r, f, ensure_ascii=False, default=float)
    os.replace(p + '.tmp', p)


def seme(*a):
    return MS.seme_str('ia21', TESTO, *a)


def dump(percorso, obj):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso + '.tmp', 'wb') as f:
        pickle.dump(obj, f)
    os.replace(percorso + '.tmp', percorso)


# ---------------------------------------------------------------- pagine, fogli, ia01

def insiemi_piega(f):
    """(pagine dei fogli di addestramento, di validazione, tenuti fuori) della piega f, ciascuna come (tutte, con almeno 40 parole)."""
    c = I7.contesto_A()
    pagine = list(I7.per_pagina(I7.libro_vero()))
    f_add, f_val, f_fuori = I7.fogli_della_piega(f)
    out = []
    for ff in (f_add, f_val, f_fuori):
        s = set(ff)
        tutte = [p for p in pagine if I7.foglio_di(p) in s]
        out.append((tutte, [p for p in tutte if p in c['ids']]))
    return out


def ids_pagina(nome, righe):
    """Una pagina scritta [(inizio, [parole])] nei numeri del giudice A / dell'esaminatore (vettore di numeri a 8 bit)."""
    import trascrizione
    c = I7.contesto_A()
    d = G.pagine_da_righe([(nome, ini, ps) for ini, ps in righe], I7.divisore(), trascrizione.pulita)
    return G.codifica(d.get(nome, []), c['idx']).astype(np.int8)


def carica_allievo(t, f):
    """L'allievo del giro t (0 = di partenza) per la piega f."""
    if t == 0:
        if PARTENZA == 'gru':
            return AG.AllievoGRU.da_partenza(f, REPLICA_PARTENZA)
        mod, fun = PARTENZA.rsplit('.', 1)
        import importlib
        return getattr(importlib.import_module(mod), fun)(f, REPLICA_PARTENZA)
    p = os.path.join(GD(t), 'allievo_f%d.pt' % f)
    if PARTENZA == 'gru':
        return AG.AllievoGRU.da_file(p, f)
    return type(carica_allievo(0, f)).da_file(p, f)


def rows_libro(t, tipo, i):
    """Il libro i-esimo del giro t ('mon': monitoraggio, 'fin': libri finali) come lista (pagina, inizio, parole) nell'ordine del libro vero."""
    gd = GD(t)
    nome = 'pagine' if tipo == 'mon' else 'finale'
    per = {f: pickle.load(open(os.path.join(gd, '%s_f%d.pkl' % (nome, f)), 'rb')) for f in range(PIEGHE)}
    pg = I7.pieghe()
    out = []
    for pag in I7.per_pagina(I7.libro_vero()):
        for ini, ps in per[pg[I7.foglio_di(pag)]][pag][i - 1]:
            out.append((pag, ini, ps))
    return out


def rows_ia01(nome):
    """Un libro per nome nel formato di ia01 (pagina -> righe (inizio, [parola come tupla di glifi])). Nomi: g<t>mon:<i>, g<t>fin:<i>,
    V21:<k>, ctrl:<nome>."""
    s, k = nome.split(':')
    if s == 'V21':
        return I7.libro_riferimento_A('b', int(k))
    if s == 'ctrl':
        return I7.libro_controllo_A(k)
    m = re.match(r'g(\d+)(mon|fin)$', s)
    return I7.libro_A_da_righe(rows_libro(int(m.group(1)), m.group(2), int(k)))


def t_di(nome):
    """Il libro come lista (pagina, inizio, parole) di stringhe."""
    s, k = nome.split(':')
    m = re.match(r'g(\d+)(mon|fin)$', s)
    if m:
        return rows_libro(int(m.group(1)), m.group(2), int(k))
    rr = rows_ia01(nome)
    return [(p, ini, [''.join(w) for w in ws]) for p, rows in rr.items() for ini, ws in rows]


# ---------------------------------------------------------------- lavori: modelli di base, giro 0

def lavoro_base(f):
    """Controlli: addestra il generatore di partenza della piega f come in ia07 (stessa funzione, stesse pieghe, replica di partenza)."""
    assert TESTO != 'voynich', 'il modello di base del Voynich e\' quello gia\' fatto da ia07'
    return I7.addestra(f, REPLICA_PARTENZA)


def pagine_fuori(f):
    return insiemi_piega(f)[2][0]


def lavoro_scrivi0(f):
    """Giro 0: l'allievo di partenza scrive, con la disposizione dei fogli tenuti fuori della piega, L_MON copie (monitoraggio) e N_FIN copie (libri
    di confronto finale)."""
    inizio = time.time()
    al = carica_allievo(0, f)
    (add, _), (val, _), (fuori, _) = insiemi_piega(f)
    gd = GD(0)
    dump(os.path.join(gd, 'pagine_f%d.pkl' % f), al.scrivi_pagine(fuori, L_MON, seme('mon', 0, f)))
    dump(os.path.join(gd, 'finale_f%d.pkl' % f), al.scrivi_pagine(fuori, N_FIN, seme('fin', 0, f)))
    return OrderedDict([('lavoro', 'scrivi0|%d' % f), ('piega', f), ('parametri', al.parametri), ('bpc_validazione', al.bpc(val)),
                        ('bpc_fuori', al.bpc(fuori)), ('secondi', round(time.time() - inizio, 1))])


def lavoro_finale(t, f):
    """Libri finali: l'allievo del giro t scrive N_FIN copie nuove delle pagine dei fogli tenuti fuori."""
    inizio = time.time()
    al = carica_allievo(t, f)
    fuori = pagine_fuori(f)
    dump(os.path.join(GD(t), 'finale_f%d.pkl' % f), al.scrivi_pagine(fuori, N_FIN, seme('fin', t, f)))
    return OrderedDict([('lavoro', ident(('finale', t, f))), ('piega', f), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- lavoro: un giro per una piega

def carica_fake(t, f):
    """Le pagine scritte (numeri) di tutti i giri precedenti a t per la piega f: lista di vettori (serbatoi dei giri 1..t-1)."""
    out = []
    for s in range(1, t):
        d = np.load(os.path.join(GD(s), 'fake_f%d.npz' % f))
        out += [d[k] for k in d.files]
    return out


def lavoro_giro(t, f):
    """Giro t per la piega f: serbatoio dell'allievo del giro t-1, esaminatore nuovo, scelta delle migliori, rifinitura, pagine di
    monitoraggio dell'allievo del giro t, AUC dell'esaminatore sull'allievo prima (t-1) e dopo (t) su fogli mai visti."""
    inizio = time.time()
    c = I7.contesto_A()
    V = c['V']
    (add, add40), (val, val40), (fuori, fuori40) = insiemi_piega(f)
    al = carica_allievo(t - 1, f)
    gd = GD(t)
    os.makedirs(gd, exist_ok=True)
    bpc_prima = al.bpc(val)
    # 1. serbatoio (fogli di addestramento) e candidate per la validazione dell'esaminatore (fogli di validazione)
    sr = al.scrivi_pagine(add40, C_CAND, seme(PERCORSO, 'serbatoio', t, f))
    sv = al.scrivi_pagine(val40, C_VAL, seme(PERCORSO, 'serbatoio_val', t, f))
    ids_sr = OrderedDict((p, [ids_pagina(p, r) for r in sr[p]]) for p in add40)
    ids_sv = [ids_pagina(p, r) for p in val40 for r in sv[p]]
    t_serb = time.time() - inizio
    # 2. esaminatore nuovo
    vere = [c['ids'][p] for p in add40]
    cur = [a for p in add40 for a in ids_sr[p]]
    vecchie = carica_fake(t, f)
    vere_val = [c['ids'][p] for p in val40]
    ex, info_ex = ES.addestra(vere, cur, vecchie, vere_val, ids_sv, V, seme(PERCORSO, 'esaminatore', t, f), cieco=(PERCORSO == 'cieco'),
                              epoche_max=EP_ES, pazienza=PAZ_ES, messaggio=None)
    t_es = time.time() - inizio - t_serb
    # 3. scelta: per ogni pagina la candidata che l'esaminatore trova piu' vera (punteggio piu' basso)
    pun = ES.punteggi(ex, cur)
    scelte, k, medie_tutte, medie_scelte, indici = [], 0, [], [], OrderedDict()
    for p in add40:
        s = pun[k:k + C_CAND]
        k += C_CAND
        j = int(np.argmin(s))
        indici[p] = j
        scelte.append((p, sr[p][j]))
        medie_tutte.append(float(s.mean()))
        medie_scelte.append(float(s[j]))
    dump_fake = {'%s|%d' % (p, j): a for p in add40 for j, a in enumerate(ids_sr[p])}
    np.savez_compressed(os.path.join(gd, 'fake_f%d.npz' % f), **dump_fake)
    # 4. rifinitura dell'allievo
    t0 = time.time()
    info_af = al.affina(add, scelte, PESO, EP_AFFINA, LR_AFFINA, seme(PERCORSO, 'affina', t, f))
    bpc_dopo = al.bpc(val)
    al.salva(os.path.join(gd, 'allievo_f%d.pt' % f))
    # 5. pagine di monitoraggio dell'allievo del giro t
    mon = al.scrivi_pagine(fuori, L_MON, seme(PERCORSO, 'mon', t, f))
    dump(os.path.join(gd, 'pagine_f%d.pkl' % f), mon)
    # 6. l'esaminatore sull'allievo prima e dopo, su fogli mai visti (ne' dall'allievo ne' dall'esaminatore)
    prima = pickle.load(open(os.path.join(GD(t - 1), 'pagine_f%d.pkl' % f), 'rb'))
    v_ids = [c['ids'][p] for p in fuori40]
    pr_ids = [ids_pagina(p, r) for p in fuori40 for r in prima[p]]
    do_ids = [ids_pagina(p, r) for p in fuori40 for r in mon[p]]
    sv_ = ES.punteggi(ex, v_ids)
    sp_ = ES.punteggi(ex, pr_ids)
    sd_ = ES.punteggi(ex, do_ids)
    lp, ld = len(prima[fuori40[0]]), len(mon[fuori40[0]])
    auc = lambda a, b: float(ES.auc([0] * len(a) + [1] * len(b), np.concatenate([a, b])))
    ris = OrderedDict([('lavoro', ident(('giro', t, f))), ('t', t), ('piega', f), ('pagine', [len(add40), len(val40), len(fuori40)]),
                       ('esaminatore', info_ex), ('AUC_prima', auc(sv_, sp_)), ('AUC_dopo', auc(sv_, sd_)),
                       ('punteggio_medio', OrderedDict([('vere', float(sv_.mean())), ('prima', float(sp_.mean())), ('dopo', float(sd_.mean()))])),
                       ('scelta', OrderedDict([('punteggio_medio_candidate', float(np.mean(medie_tutte))), ('punteggio_medio_scelte', float(np.mean(medie_scelte))),
                                               ('indici_scelti', [indici[p] for p in add40])])),
                       ('affina', info_af), ('bpc_val_prima', bpc_prima), ('bpc_val_dopo', bpc_dopo),
                       ('pun_vere', OrderedDict((p, float(x)) for p, x in zip(fuori40, sv_))),
                       ('pun_prima', OrderedDict((p, [float(x) for x in sp_[i * lp:(i + 1) * lp]]) for i, p in enumerate(fuori40))),
                       ('pun_dopo', OrderedDict((p, [float(x) for x in sd_[i * ld:(i + 1) * ld]]) for i, p in enumerate(fuori40))),
                       ('minuti', OrderedDict([('serbatoio', round(t_serb / 60, 2)), ('esaminatore', round(t_es / 60, 2)),
                                               ('resto', round((time.time() - inizio - t_serb - t_es) / 60, 2))])),
                       ('secondi', round(time.time() - inizio, 1))])
    return ris


# ---------------------------------------------------------------- misure sui libri

def diversita(pagine_parole):
    """pagina -> lista di parole (stringhe). Varieta' del libro: somiglianza media (Jaccard) fra i vocabolari di coppie di pagine della stessa
    sezione (le stesse coppie per ogni libro: 3000 a caso, seme fisso), parole diverse su parole totali del libro, e la stessa per pagina."""
    c = I7.contesto_A()
    sez = {x['pagina']: x['sezione'] for x in I7.libro_vero()}
    nomi = sorted(p for p in c['ids'] if p in pagine_parole)
    insiemi = {p: set(pagine_parole[p]) for p in nomi}
    per_sez = {}
    for p in nomi:
        per_sez.setdefault(sez[p], []).append(p)
    coppie = []
    for s in sorted(per_sez):
        ps = per_sez[s]
        coppie += [(a, b) for i, a in enumerate(ps) for b in ps[i + 1:]]
    random.Random(2121).shuffle(coppie)
    coppie = coppie[:3000]
    jac = [len(insiemi[a] & insiemi[b]) / max(len(insiemi[a] | insiemi[b]), 1) for a, b in coppie]
    tutte = [w for p in nomi for w in pagine_parole[p]]
    return OrderedDict([('jaccard', float(np.mean(jac))), ('ttr', len(set(tutte)) / max(len(tutte), 1)),
                        ('ttr_pagina', float(np.mean([len(insiemi[p]) / max(len(pagine_parole[p]), 1) for p in nomi]))), ('coppie', len(coppie))])


def pagine_parole_da_t(t_):
    out = OrderedDict()
    for p, _, ps in t_:
        out.setdefault(p, []).extend(ps)
    return out


def media_G9(tab):
    nomi, X, nf = tab
    j = next((i for i, n in enumerate(nf) if str(n).startswith(G9_NOME)), None)
    return None if j is None else float(np.mean(np.asarray(X)[:, j]))


def giudice_A_completo(rows):
    """Come `I7.giudice_A` (stessa procedura), ma restituisce anche il profilo a 14 numeri di ogni pagina."""
    vp, gp = I7.profili_vere_A(), I7.profili_A(rows)
    pag = [p for p in vp if p in gp]
    if len(pag) < 10 or len(pag) < 0.99 * len(vp):
        return OrderedDict([('AUC_A', None), ('A_errore', 'pagine in comune: %d su %d' % (len(pag), len(vp)))]), None
    X = np.array([vp[p] for p in pag] + [gp[p] for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    a, pr = G.auc_logistico(X, y, pag + pag)
    n = len(pag)
    ris = OrderedDict([('AUC_A', float(a)), ('AUC_A_appaiata', float(G.appaiata(pr[:n], pr[n:]))), ('pagine_A', n),
                       ('diff_profilo_A', [float(v) for v in np.mean([gp[p] - vp[p] for p in pag], axis=0)])])
    return ris, (pag, np.array([gp[p] for p in pag]))


def lavoro_misura(t, tipo, i):
    """Giudici tenuti da parte (paper e231, e266; A) e misure veloci su un libro dell'allievo del giro t."""
    inizio = time.time()
    t_ = t_di('g%d%s:%d' % (t, tipo, i))
    rows = I7.libro_A_da_righe(t_)
    gd = GD(t)
    tab = os.path.join(gd, 'tab_%s_%d.npz' % (tipo, i))
    os.makedirs(gd, exist_ok=True)
    ris = OrderedDict([('lavoro', ident(('misura', t, tipo, i))), ('t', t), ('tipo', tipo), ('i', i)])
    ris.update(I7.giudica(t_, tab))
    try:
        a, prof = giudice_A_completo(rows)
        ris.update(a)
        if prof:
            np.savez(os.path.join(gd, 'prof_%s_%d.npz' % (tipo, i)), nomi=np.array(prof[0]), X=prof[1])
    except Exception as e:                                                # noqa: BLE001
        ris['A_errore'] = repr(e)
    d = np.load(tab)
    ris['G9'] = media_G9((d['nomi'], d['X'], d['nf']))
    ris['copia'] = I7.copia_onesta(t_)
    pp = pagine_parole_da_t(t_)
    righe_p = OrderedDict()
    for p, _, ps in t_:
        righe_p.setdefault(p, []).append(ps)
    ris['ripetizioni'] = MS.ripetizioni_interne(righe_p)
    ris['diversita'] = diversita(pp)
    c = I7.contesto_A()
    ris['contatto'] = float(R.mi_contatto(OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def nomi_K(t, tipo):
    return ['g%d%s:%d' % (t, tipo, i) for i in range(1, (L_MON if tipo == 'mon' else N_FIN) + 1)]


def lavoro_K(t, tipo, f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict((n, rows_ia01(n)) for n in nomi_K(t, tipo))
    info, prof = MS.lavoro_K(f, c, libri)
    dump(os.path.join(GD(t), 'K_%s_f%d.pkl' % (tipo, f)), prof)
    return OrderedDict([('lavoro', ident(('K', t, tipo, f))), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])),
                        ('secondi', round(time.time() - inizio, 1))])


def nomi_Kctrl():
    return ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe'] + ['V21:%d' % k for k in CHIAVI_V21]


def lavoro_Kctrl(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_Kctrl():
        r = rows_ia01(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    dump(os.path.join(amb_dir('comuni'), 'Kctrl_f%d.pkl' % f), prof)
    return OrderedDict([('lavoro', 'Kctrl|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('secondi', round(time.time() - inizio, 1))])


def auc_K(t, tipo, ambito_='auto'):
    """AUC del giudice K per i libri `tipo` del giro t (nome -> AUC), dalle previsioni delle 5 pieghe."""
    prof = []
    for f in range(PIEGHE):
        p = os.path.join(GD(t), 'K_%s_f%d.pkl' % (tipo, f))
        if not os.path.exists(p):
            return None
        prof.append(pickle.load(open(p, 'rb')))
    prof = MS.unisci_profili(prof)
    n_pag = len(I7.contesto_A()['ids'])
    return OrderedDict((n, MS.auc_da_profili(prof, n, n_pag)) for n in nomi_K(t, tipo))


def lavoro_ctrl(*a):
    """Controlli dei giudici del paper e di A (procedure di ia07): O2, etichette a caso, controlli di A, etichette a caso di A."""
    return I7.lavoro(tuple(a))


def lavoro_naturale():
    """Riferimenti naturali: copia a memoria, ripetizioni e varieta' del libro vero."""
    inizio = time.time()
    ref = I7.copia_riferimenti()
    pp = OrderedDict((p, [w for x in rr for w in x['parole']]) for p, rr in I7.per_pagina(I7.libro_vero()).items())
    rip = MS.ripetizioni_interne(OrderedDict((p, [x['parole'] for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items()))
    return OrderedDict([('lavoro', 'naturale|0'), ('copia', ref['naturale']), ('copia_v21', ref.get('v21 (libro d\'esempio)')), ('ripetizioni', rip),
                        ('diversita', diversita(pp)), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome):
    """Copia netta e Λ (ia09), contatto (ia08), G9 del giudice 2, per un libro o per `vere`."""
    import e266_discriminatore_forte as e266
    inizio = time.time()
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows, g9 = c['vere'], media_G9(k['vt266'])
    else:
        rows = rows_ia01(nome)
        g9 = media_G9(e266.tabella(I7.righe_ini(t_di(nome)), k['rif266']))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', ident(('M', nome))), ('G9', g9)])
    ris.update(MS.lavoro_M('ia21_' + nome, pag, {p: c['fold'][p] for p in pag}))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def nomi_struttura(T):
    """Testi per la struttura: vero, i primi N_STR libri di partenza, i primi N_STR libri finali del giro T, i libri v21."""
    return ['g0fin:%d' % i for i in range(1, N_STR + 1)] + ['g%dfin:%d' % (T, i) for i in range(1, N_STR + 1)] + ['V21:%d' % k for k in CHIAVI_V21[:N_STR]]


def lavoro_D(ambito_, T, f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict()
    if ambito_ == 'comuni':
        testi['vere'] = c['vere']
        for n in nomi_struttura(T):
            if n.startswith(('g0fin', 'V21')):
                testi[n] = rows_ia01(n)
    else:
        for n in nomi_struttura(T):
            if re.match(r'g[1-9]\d*fin', n):
                testi[n] = rows_ia01(n)
    out, info = MS.lavoro_D(f, c, testi)
    return OrderedDict([('lavoro', ident(('D', ambito_, f))), ('piega', f), ('famiglie', info), ('D', out), ('secondi', round(time.time() - inizio, 1))])


def lavoro(args):
    inizio = time.time()
    try:
        tipo = args[0]
        if tipo == 'lmA':
            r = I7.lavoro_lmA(args[1], args[2])
        elif tipo == 'base':
            r = lavoro_base(args[1])
        elif tipo == 'scrivi0':
            r = lavoro_scrivi0(args[1])
        elif tipo == 'finale':
            r = lavoro_finale(args[1], args[2])
        elif tipo == 'giro':
            r = lavoro_giro(args[1], args[2])
        elif tipo == 'misura':
            r = lavoro_misura(args[1], args[2], args[3])
        elif tipo == 'K':
            r = lavoro_K(args[1], args[2], args[3])
        elif tipo == 'Kctrl':
            r = lavoro_Kctrl(args[1])
        elif tipo == 'ctrl':
            r = lavoro_ctrl(*args[1:])
        elif tipo == 'naturale':
            r = lavoro_naturale()
        elif tipo == 'M':
            r = lavoro_M(args[1])
        elif tipo == 'D':
            r = lavoro_D(args[1], args[2], args[3])
        else:
            raise ValueError(tipo)
        r['lavoro'] = ident(args)
        scrivi_riga(args, r)
        return r
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident(args)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    I7.avvia_processo()


class Esecutore:
    def __init__(self, processi, log):
        self.pool = get_context('spawn').Pool(processi, initializer=avvia_processo)
        self.log = log

    def corri(self, lavori, nome=''):
        """Esegue i lavori non ancora fatti (con riga di risultato) e scrive il registro. Restituisce gli errori."""
        da_fare = [a for a in lavori if riga(a) is None]
        if not da_fare:
            return []
        print('== %s: %d lavori (su %d)' % (nome, len(da_fare), len(lavori)), flush=True)
        inizio, errori = time.time(), []
        for k, r in enumerate(self.pool.imap_unordered(lavoro, da_fare), 1):
            with open(self.log, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps({x: v for x, v in r.items() if x not in ('pun_vere', 'pun_prima', 'pun_dopo')}, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                errori.append(r)
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                breve = {x: r[x] for x in ('AUC_e231', 'AUC_e266', 'AUC_A', 'AUC_prima', 'AUC_dopo', 'bpc_validazione', 'bpc_val_dopo') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        return errori

    def chiudi(self):
        self.pool.close()
        self.pool.join()


# ---------------------------------------------------------------- elenchi di lavori per fase

def lavori_fase0():
    """Basi, giro 0 e controlli (comuni ai percorsi di uno stesso testo)."""
    pre = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
    if TESTO != 'voynich':
        pre += [('base', f) for f in range(PIEGHE) if not os.path.exists(I7.percorso_modello(I7.nome_modello(f, REPLICA_PARTENZA), '.pt'))]
    return pre


def lavori_giro0():
    return [('scrivi0', f) for f in range(PIEGHE)]


def lavori_misure(t, tipo):
    n = L_MON if tipo == 'mon' else N_FIN
    return [('misura', t, tipo, i) for i in range(1, n + 1)] + [('K', t, tipo, f) for f in range(PIEGHE)]


def lavori_controlli():
    return ([('ctrl', 'O', 'O2', s) for s in I7.SEMI_O] + [('ctrl', 'caso', 0), ('ctrl', 'casoA', 0)] + [('ctrl', 'ctrlA', n) for n in I7.NOMI_CTRL_A] +
            [('Kctrl', f) for f in range(PIEGHE)] + [('naturale', 0)])


# ---------------------------------------------------------------- registro del giro, guardie, arresto

K4 = 'righe uguali a una precedente nella pagina (>= 4 parole)'


def media_es(xs):
    return MS.media_es([x for x in xs if x is not None])


def misure_libri(t, tipo):
    """Giudici tenuti da parte e misure veloci, media (± errore standard) sui libri `tipo` ('mon' o 'fin') del giro t. None se mancano."""
    n = L_MON if tipo == 'mon' else N_FIN
    rs = [riga(('misura', t, tipo, i)) for i in range(1, n + 1)]
    if any(r is None for r in rs):
        return None
    aK = auc_K(t, tipo)
    out = OrderedDict([('t', t), ('tipo', tipo), ('libri', n)])
    out['e231'] = media_es([r['AUC_e231'] for r in rs])
    out['e266'] = media_es([r['AUC_e266'] for r in rs])
    out['A'] = media_es([r.get('AUC_A') for r in rs])
    out['K'] = media_es(list(aK.values())) if aK else (None, None)
    out['per_libro'] = OrderedDict([('e231', [r['AUC_e231'] for r in rs]), ('e266', [r['AUC_e266'] for r in rs]),
                                    ('A', [r.get('AUC_A') for r in rs]), ('K', list(aK.values()) if aK else None)])
    tre = [out[j][0] for j in ('e231', 'e266', 'K')]
    out['M3'] = float(np.mean(tre)) if all(x is not None for x in tre) else None
    qs = [I7.quote(r['copia']) for r in rs]
    out['copia'] = OrderedDict((k, float(np.mean([q[k] for q in qs if q[k] is not None])) if any(q[k] is not None for q in qs) else None) for k in qs[0])
    out['ripetizioni'] = OrderedDict((k, float(np.mean([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else 0.0 for r in rs])))
                                     for k in rs[0]['ripetizioni'])
    out['diversita'] = OrderedDict((k, float(np.mean([r['diversita'][k] for r in rs]))) for k in ('jaccard', 'ttr', 'ttr_pagina'))
    out['G9'] = media_es([r.get('G9') for r in rs])[0]
    out['contatto'] = media_es([r.get('contatto') for r in rs])[0]
    dA = [r['diff_profilo_A'] for r in rs if r.get('diff_profilo_A')]
    out['diff_profilo_A'] = OrderedDict((n, float(np.mean([d[j] for d in dA]))) for j, n in enumerate(G.CARATTERISTICHE)) if dA else None
    out['gruppi_e266'] = OrderedDict((g, float(np.mean([r['gruppi_e266'][g] for r in rs if r['gruppi_e266'].get(g) is not None])))
                                     for g in rs[0]['gruppi_e266'] if any(r['gruppi_e266'].get(g) is not None for r in rs))
    out['gruppi_e231'] = OrderedDict((g, float(np.mean([r['gruppi_e231'][g] for r in rs if r['gruppi_e231'].get(g) is not None])))
                                     for g in rs[0]['gruppi_e231'] if any(r['gruppi_e231'].get(g) is not None for r in rs))
    out['pesanti_e266'] = rs[0].get('pesanti_e266')
    return out


def esaminatore_giro(t):
    """Medie sulle pieghe dei risultati dei lavori `giro` del giro t."""
    rs = [riga(('giro', t, f)) for f in range(PIEGHE)]
    if any(r is None for r in rs):
        return None
    m = lambda xs: float(np.mean(xs))
    return OrderedDict([('t', t), ('AUC_prima', m([r['AUC_prima'] for r in rs])), ('AUC_dopo', m([r['AUC_dopo'] for r in rs])),
                        ('AUC_prima_pieghe', [r['AUC_prima'] for r in rs]), ('AUC_dopo_pieghe', [r['AUC_dopo'] for r in rs]),
                        ('AUC_validazione', m([r['esaminatore']['AUC_validazione'] for r in rs if r['esaminatore']['AUC_validazione'] is not None])
                         if any(r['esaminatore']['AUC_validazione'] is not None for r in rs) else None),
                        ('epoca_scelta', m([r['esaminatore']['epoca_scelta'] for r in rs])), ('epoche_max', max(r['esaminatore']['epoche'] for r in rs)),
                        ('bpc_val_prima', m([r['bpc_val_prima'] for r in rs])), ('bpc_val_dopo', m([r['bpc_val_dopo'] for r in rs])),
                        ('punteggio_candidate', m([r['scelta']['punteggio_medio_candidate'] for r in rs])),
                        ('punteggio_scelte', m([r['scelta']['punteggio_medio_scelte'] for r in rs])),
                        ('minuti_per_piega', OrderedDict((k, m([r['minuti'][k] for r in rs])) for k in rs[0]['minuti'])),
                        ('secondi_massimo', max(r['secondi'] for r in rs))])


def bpc_partenza():
    rs = [riga(('scrivi0', f)) for f in range(PIEGHE)]
    return float(np.mean([r['bpc_validazione'] for r in rs])) if all(rs) else None


def guardie(m_t, m_0, es_t, nat):
    """Guardie del giro (monitoraggio): ok / valore / soglia. `nat`: riga 'naturale|0' (copia, ripetizioni e varieta' del libro vero)."""
    g = OrderedDict()
    q = m_t['copia']
    g['copia 5-grammi'] = (q['5-grammi'] is not None and q['5-grammi'] <= COPIA_5GRAMMI, q['5-grammi'], COPIA_5GRAMMI)
    g['copia righe intere'] = (q['righe intere'] is not None and q['righe intere'] <= COPIA_RIGHE, q['righe intere'], COPIA_RIGHE)
    nn = nat['copia']['parole nuove']
    nn = nn[0] / nn[1] if isinstance(nn, (list, tuple)) else nn
    g['parole nuove nella fascia del vero'] = (NUOVE_FASCIA[0] * nn <= q['parole nuove'] <= NUOVE_FASCIA[1] * nn, q['parole nuove'], [NUOVE_FASCIA[0] * nn, NUOVE_FASCIA[1] * nn])
    for k, nome in (('jaccard', 'varieta fra pagine (somiglianza dei vocabolari)'), ('ttr', 'varieta del lessico (parole diverse su totali)')):
        v, ref, v0 = m_t['diversita'][k], nat['diversita'][k], m_0['diversita'][k]
        fuori = not (VARIETA_FASCIA[0] * ref <= v <= VARIETA_FASCIA[1] * ref)
        peggio = abs(v - v0) > PEGGIORA_REL * abs(v0)
        g[nome] = (not (fuori and peggio), v, [VARIETA_FASCIA[0] * ref, VARIETA_FASCIA[1] * ref])
    nat4 = nat['ripetizioni'][K4]
    nat4 = nat4[0] / nat4[1] if nat4[1] else 0.0
    v4 = m_t['ripetizioni'][K4]
    g['non si avvita'] = (not (v4 > DEGENERA_MIN and v4 > DEGENERA_VOLTE * max(nat4, 1e-9)), v4, [DEGENERA_MIN, DEGENERA_VOLTE * nat4])
    b0 = bpc_partenza()
    deg = es_t['bpc_val_dopo'] - b0 if b0 is not None else None
    g['tenuta sulla validazione vera (bit per segno)'] = (deg is not None and deg <= DEGRADO_BPC, deg, DEGRADO_BPC)
    return OrderedDict((k, OrderedDict([('ok', bool(v[0])), ('valore', v[1]), ('soglia', v[2])])) for k, v in g.items())


def percorso_stato():
    return os.path.join(amb_dir(PERCORSO), 'stato.json')


def esegui_giri(ex):
    """Fase G: giro per giro fino all'arresto. Rilegge tutto dai file: con RIPRENDI i giri fatti non si rifanno e la decisione e' la stessa."""
    nat = riga(('naturale', 0))
    m0 = misure_libri(0, 'mon')
    if nat is None or m0 is None:
        raise SystemExit('FERMO: la fase 0 non e\' finita (manca il giro 0 o il naturale)')
    stato = OrderedDict([('percorso', PERCORSO), ('testo', TESTO), ('partenza', PARTENZA), ('giri', []), ('fermo', None), ('motivo', None), ('ultimo_valido', 0)])
    migliore, senza = m0['M3'], 0
    for t in range(1, N_GIRI + 1):
        errori = ex.corri([('giro', t, f) for f in range(PIEGHE)], 'giro %d, esaminatore e rifinitura' % t)
        if errori:
            raise SystemExit('FERMO: lavori del giro %d falliti (rifare con RIPRENDI=1)' % t)
        errori = ex.corri(lavori_misure(t, 'mon'), 'giro %d, giudici tenuti da parte' % t)
        if errori:
            raise SystemExit('FERMO: misure del giro %d fallite (rifare con RIPRENDI=1)' % t)
        es_t, m_t = esaminatore_giro(t), misure_libri(t, 'mon')
        gu = guardie(m_t, m0, es_t, nat)
        viol = [k for k, x in gu.items() if not x['ok']]
        voce = OrderedDict([('t', t), ('esaminatore', es_t), ('giudici', OrderedDict((j, m_t[j]) for j in ('e231', 'e266', 'A', 'K'))), ('M3', m_t['M3']),
                            ('guardie', gu), ('guardie_violate', viol)])
        stato['giri'].append(voce)
        motivo = None
        if viol and GUARDIE_FERMANO:
            motivo = 'guardia violata: ' + '; '.join(viol)
        else:
            stato['ultimo_valido'] = t
            if m_t['M3'] < migliore - MIGLIORA_MIN:
                migliore, senza = m_t['M3'], 0
            else:
                senza += 1
            if m_t['e266'][0] <= SOGLIA_STOP and m_t['K'][0] <= SOGLIA_STOP:
                motivo = 'soglia raggiunta (giudice 2 e K a o sotto %s)' % SOGLIA_STOP
            elif senza >= PAZIENZA_GIRI:
                motivo = '%d giri senza miglioramento (media dei tre giudici)' % PAZIENZA_GIRI
            elif t == N_GIRI:
                motivo = '%d giri fatti' % N_GIRI
        print('giro %d: esaminatore AUC prima %.3f dopo %.3f; giudici 1 %.3f 2 %.3f K %.3f A %.3f; media dei tre %.3f%s' % (
            t, es_t['AUC_prima'], es_t['AUC_dopo'], m_t['e231'][0], m_t['e266'][0], m_t['K'][0], m_t['A'][0] or float('nan'), m_t['M3'],
            ('; ARRESTO: ' + motivo) if motivo else ''), flush=True)
        if motivo:
            stato['fermo'], stato['motivo'] = t, motivo
            break
    json.dump(stato, open(percorso_stato(), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return stato


def esegui_finale(ex, stato):
    """Fase F: libri nuovi dell'allievo dell'ultimo giro valido (e, se STRUTTURA, misure di struttura)."""
    T = stato['ultimo_valido']
    lavori = []
    if T > 0:
        lavori += [('finale', T, f) for f in range(PIEGHE)]
    ex_err = ex.corri(lavori, 'libri finali del giro %d' % T) if lavori else []
    ex_err += ex.corri(lavori_misure(T, 'fin') + lavori_misure(0, 'fin'), 'giudici sui libri finali (giro %d e giro 0)' % T)
    if STRUTTURA:
        nomi = list(dict.fromkeys(nomi_struttura(T)))
        ex_err += ex.corri([('M', 'vere')] + [('M', n) for n in nomi] + [('D', 'comuni', T, f) for f in range(PIEGHE)] +
                           ([('D', 'finale', T, f) for f in range(PIEGHE)] if T > 0 else []), 'struttura')
    if ex_err:
        raise SystemExit('FERMO: lavori finali falliti (rifare con RIPRENDI=1)')


def esegui_fase0(ex):
    e = ex.corri(lavori_fase0(), 'fase 0: modelli di base e del giudice A')
    e += ex.corri(lavori_giro0(), 'fase 0: l\'allievo di partenza scrive il giro 0')
    e += ex.corri(lavori_misure(0, 'mon') + lavori_misure(0, 'fin') + lavori_controlli(), 'fase 0: giudici sul giro 0 e controlli dei giudici')
    if e:
        raise SystemExit('FERMO: lavori della fase 0 falliti (rifare con RIPRENDI=1)')


# ---------------------------------------------------------------- sintesi e letture

import contextlib


@contextlib.contextmanager
def con_percorso(testo_dir, percorso):
    """Per leggere i risultati di un altro testo o percorso (stesse funzioni di lettura, altra cartella)."""
    g = globals()
    vecchio = (g['TESTO_DIR'], g['PERCORSO'])
    g['TESTO_DIR'], g['PERCORSO'] = testo_dir, percorso
    try:
        yield
    finally:
        g['TESTO_DIR'], g['PERCORSO'] = vecchio


def testo_dir_di(testo):
    return os.path.join(RADICE, '%s_%s' % (testo, PARTENZA.replace('.', '_')))


def riassunto(testo, percorso):
    """Il percorso (di un testo) gia' eseguito: stato, libri di partenza e libri finali dell'ultimo giro valido. None se non c'e'."""
    with con_percorso(testo_dir_di(testo), percorso):
        if not os.path.exists(percorso_stato()):
            return None
        st = json.load(open(percorso_stato(), encoding='utf-8'))
        T = st['ultimo_valido']
        g0 = misure_libri(0, 'fin')
        fin = misure_libri(T, 'fin') if T > 0 else g0
        if g0 is None or fin is None:
            return None
        return OrderedDict([('testo', testo), ('percorso', percorso), ('stato', st), ('T', T), ('g0', g0), ('finale', fin)])


def classe(a, b, nomi=('e231', 'e266', 'K')):
    """Per ogni giudice la lettura (piu' vicino / uguale / piu' lontano, a due errori) di `a` contro `b`; a, b: giudice -> (media, errore)."""
    out = OrderedDict()
    for j in nomi:
        x, y = a.get(j) or (None, None), b.get(j) or (None, None)
        c = MS.confronta(x[0], x[1], y[0], y[1])
        if c['lettura'] in ('più vicino', 'più lontano') and abs(c['differenza']) < MIN_EFFETTO:
            c['lettura'] = "uguale entro l'errore (differenza sotto %s)" % str(MIN_EFFETTO).replace('.', ',')
        out[j] = c
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
        return 'solo K scende: possibile giudice amico, non vale come sì' + (' (e almeno due giudici su tre sono "più lontano")' if lon >= 2 else '')
    if lon == 0:
        return 'alla pari del v21'
    if lon >= 2:
        return 'più lontano dal vero del v21'
    return 'zona grigia'


def esito_progresso(cl, di_cosa='giro 0'):
    L = [x['lettura'] for x in cl.values()]
    if any(l == 'non calcolabile' for l in L):
        return 'non leggibile (manca un giudice)'
    vic, lon = sum(l == 'più vicino' for l in L), sum(l == 'più lontano' for l in L)
    if vic >= 2 and lon == 0:
        return 'progresso sul %s' % di_cosa
    if lon >= 2:
        return 'peggio del %s' % di_cosa
    if vic == 0 and lon == 0:
        return 'nessun progresso sul %s (uguale entro l\'errore)' % di_cosa
    return 'zona grigia'


def media3(x):
    v = [x[j][0] for j in ('e231', 'e266', 'K')]
    return float(np.mean(v)) if all(a is not None for a in v) else None


def controllo_positivo(r):
    """Il metodo sa migliorare un imitatore? Su un testo non Voynich: partenza sotto il soffitto, almeno due giudici su tre 'piu' vicino' (2 errori),
    calo della media dei tre giudici di almeno POS_CALO."""
    if r is None:
        return OrderedDict([('esito', 'non eseguito')])
    g0, fin = r['g0'], r['finale']
    m0, m1 = media3(g0), media3(fin)
    cl = classe(fin, g0)
    vic = sum(x['lettura'] == 'più vicino' for x in cl.values())
    out = OrderedDict([('giro_ultimo_valido', r['T']), ('media_tre_giudici_partenza', m0), ('media_tre_giudici_finale', m1), ('calo', None if m0 is None or m1 is None else m0 - m1),
                       ('giudici', cl), ('piu_vicini', vic)])
    if m0 is None or m1 is None:
        out['esito'] = 'non leggibile (manca un giudice)'
    elif m0 > SOFFITTO:
        out['esito'] = 'non leggibile: la partenza e\' sopra il soffitto (%s): i giudici non distinguono i miglioramenti' % nu(SOFFITTO, 2)
    elif r['T'] == 0:
        out['esito'] = 'non riuscito (nessun giro valido)'
    else:
        out['esito'] = 'riuscito' if (vic >= 2 and m0 - m1 >= POS_CALO) else 'non riuscito'
    out['riuscito'] = out['esito'] == 'riuscito'
    return out


def controllo_negativo_cieco(r):
    """L'esaminatore cieco non deve migliorare: al piu' un giudice su tre 'piu' vicino' e calo della media dei tre sotto POS_CALO."""
    if r is None:
        return OrderedDict([('esito', 'non eseguito')])
    g0, fin = r['g0'], r['finale']
    m0, m1 = media3(g0), media3(fin)
    cl = classe(fin, g0)
    vic = sum(x['lettura'] == 'più vicino' for x in cl.values())
    out = OrderedDict([('giro_ultimo_valido', r['T']), ('media_tre_giudici_partenza', m0), ('media_tre_giudici_finale', m1), ('calo', None if m0 is None or m1 is None else m0 - m1),
                       ('giudici', cl), ('piu_vicini', vic)])
    out['riuscito'] = bool(m0 is not None and m1 is not None and vic <= 1 and m0 - m1 < POS_CALO)
    out['esito'] = ('riuscito: non migliora' if out['riuscito'] else 'NON riuscito: anche con l\'esaminatore cieco i giudici scendono (il miglioramento puo\' venire dal solo rifinire)')
    return out


def controlli_giudici():
    """Controlli dei giudici sul testo corrente (procedure di ia07 e ia16), dai risultati della fase 0."""
    ctr = OrderedDict()
    pos = [riga(('ctrl', 'O', 'O2', s)) for s in I7.SEMI_O]
    pos = [x['AUC_e266'] for x in pos if x]
    caso = riga(('ctrl', 'caso', 0))
    ctr['paper_positivo'] = OrderedDict(AUC=MS.media_es(pos)[0] if pos else None, soglia=POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=NEG_BANDA,
                                        riuscito=bool(caso) and all(NEG_BANDA[0] <= caso[k] <= NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    pa = OrderedDict((n, (riga(('ctrl', 'ctrlA', n)) or {}).get('AUC_A')) for n in I7.NOMI_CTRL_A if n != 'righe')
    na = riga(('ctrl', 'casoA', 0))
    na = na['AUC_A'] if na else None
    ctr['A_positivo'] = OrderedDict(AUC=pa, soglia=I7.SOGLIA_POSITIVO_A, riuscito=pa.get('parole') is not None and all(v >= I7.SOGLIA_POSITIVO_A for v in pa.values() if v is not None))
    ctr['A_negativo'] = OrderedDict(AUC=na, banda=NEG_BANDA, riuscito=na is not None and NEG_BANDA[0] <= na <= NEG_BANDA[1])
    prof = []
    for f in range(PIEGHE):
        p = os.path.join(amb_dir('comuni'), 'Kctrl_f%d.pkl' % f)
        if os.path.exists(p):
            prof.append(pickle.load(open(p, 'rb')))
    aucK = OrderedDict()
    if len(prof) == PIEGHE:
        prof = MS.unisci_profili(prof)
        n_pag = len(I7.contesto_A()['ids'])
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
    return ctr, aucK


def rif_v21(aucK):
    """v21 senza messaggio: giudici del paper (24 chiavi, dal paper), K ricalcolato qui sui 10 libri, A dai libri di ia07 (rifA)."""
    out = OrderedDict(e231=I7.V21['AUC_e231'], e266=I7.V21['AUC_e266'])
    out['K'] = MS.media_es([v for n, v in aucK.items() if n.startswith('V21:')]) if aucK else (None, None)
    p = os.environ.get('CORSE_IA07', os.path.join(QUI, '..', 'risultati', 'ia07_corse.jsonl'))
    A = []
    if os.path.exists(p) and not SOLO_CONTROLLI:
        for l in open(p, encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r.get('lavoro', '').startswith('rifA|') and r.get('AUC_A_b') is not None:
                    A.append(r['AUC_A_b'])
    out['A'] = MS.media_es(A) if A else (None, None)
    return out


def struttura(T):
    """Misure di struttura: vero, partenza (g0), finale (giro T) e v21, come in ia16. None se non sono state eseguite."""
    M = {}
    for n in ['vere'] + list(dict.fromkeys(nomi_struttura(T))):
        r = riga(('M', n))
        if r is None:
            return None
        M[n] = r
    Dc = [riga(('D', 'comuni', T, f)) for f in range(PIEGHE)]
    Df = [riga(('D', 'finale', T, f)) for f in range(PIEGHE)] if T > 0 else Dc
    if any(x is None for x in Dc + Df):
        return None
    mv = MS.copia_netta_lambda(M['vere'], con_intervallo=True)
    out = OrderedDict(vere=OrderedDict(copia_netta=mv['copia_netta'], copia_netta_ic=mv['copia_netta_ic'], lam=mv['lam'], lam_ic=mv['lam_ic'], contatto=mv['contatto'],
                                       D=MS.D_da_pieghe([d['D']['vere'] for d in Dc]), G9=M['vere'].get('G9')))
    insiemi = OrderedDict([('partenza', ['g0fin:%d' % i for i in range(1, N_STR + 1)]), ('finale', ['g%dfin:%d' % (T, i) for i in range(1, N_STR + 1)]),
                           ('v21', ['V21:%d' % k for k in CHIAVI_V21[:N_STR]])])
    misure = ('copia_netta', 'lam', 'D', 'contatto', 'G9')
    for s, nomi in insiemi.items():
        xs = []
        for n in nomi:
            x = MS.copia_netta_lambda(M[n])
            x['G9'] = M[n].get('G9')
            dd = Df if s == 'finale' else Dc
            x['D'] = MS.D_da_pieghe([d['D'][n] for d in dd])
            xs.append(x)
        out[s] = OrderedDict((m_, MS.media_es([x[m_] for x in xs])) for m_ in misure)
        out[s]['libri'] = len(xs)
    L3 = OrderedDict()
    for m_ in misure:
        v, a, b = out['vere'][m_], out['partenza'][m_], out['finale'][m_]
        if v is None or a[0] is None or b[0] is None:
            L3[m_] = OrderedDict(lettura='non calcolabile')
            continue
        phi = (b[0] - a[0]) / (v - a[0]) if abs(v - a[0]) > max(2 * (a[1] or 0.0), 0.05 * abs(v), 1e-9) else None
        L3[m_] = OrderedDict(vero=v, partenza=a[0], finale=b[0], v21=out['v21'][m_][0], frazione_di_cammino=phi,
                             lettura=('partenza gia\' al vero' if phi is None else 'chiuso almeno a meta\'' if phi >= 0.5 else 'resta lontano'))
    out['frazione_di_cammino'] = L3
    return out


def associazioni(t, quale):
    """Che cosa l'esaminatore del giro t sembra usare: correlazione di rango (Spearman), dentro ogni piega, fra il suo punteggio e le
    caratteristiche delle pagine (profilo di 14 numeri del giudice A e le 228 del giudice 2), su pagine vere e scritte di fogli mai visti.
    `quale`: 'prima' (pagine dell'allievo del giro t-1) o 'dopo' (del giro t). E' un'associazione, non una prova che ne dipenda."""
    from scipy.stats import rankdata
    rows = [riga(('giro', t, f)) for f in range(PIEGHE)]
    if any(r is None for r in rows):
        return None
    k = I7.riferimenti()
    nv, Xv, nf = k['vt266']
    iv = {p: i for i, p in enumerate(nv)}
    pav = I7.profili_vere_A()
    u = t - 1 if quale == 'prima' else t
    tabs, profs = [], []
    for i in range(1, L_MON + 1):
        a = os.path.join(GD(u), 'tab_mon_%d.npz' % i)
        b = os.path.join(GD(u), 'prof_mon_%d.npz' % i)
        if not (os.path.exists(a) and os.path.exists(b)):
            return None
        d, e = np.load(a), np.load(b)
        tabs.append(({str(n): j for j, n in enumerate(d['nomi'])}, d['X']))
        profs.append(({str(n): j for j, n in enumerate(e['nomi'])}, e['X']))
    nomi_e = [str(n) for n in nf]
    rhoE, rhoA = [], []
    for r in rows:
        y, fe, fa = [], [], []
        for p, s in r['pun_vere'].items():
            if p in iv and p in pav:
                y.append(s)
                fe.append(Xv[iv[p]])
                fa.append(pav[p])
        for p, ss in r['pun_' + quale].items():
            for b, s in enumerate(ss):
                if b < len(tabs) and p in tabs[b][0] and p in profs[b][0]:
                    y.append(s)
                    fe.append(tabs[b][1][tabs[b][0][p]])
                    fa.append(profs[b][1][profs[b][0][p]])
        if len(y) < 20:
            continue
        ry = rankdata(y)
        for F_, lista in ((np.array(fe, dtype=float), rhoE), (np.array(fa, dtype=float), rhoA)):
            rho = np.full(F_.shape[1], np.nan)
            for j in range(F_.shape[1]):
                if F_[:, j].std() > 0:
                    rho[j] = float(np.corrcoef(ry, rankdata(F_[:, j]))[0, 1])
            lista.append(rho)
    if not rhoE:
        return None
    with np.errstate(all='ignore'), warnings.catch_warnings():
        warnings.simplefilter('ignore')
        rE, rA = np.nanmean(np.array(rhoE), axis=0), np.nanmean(np.array(rhoA), axis=0)
    gruppi = OrderedDict()
    for j, n in enumerate(nomi_e):
        g = n.split()[0] if n[:1] == 'G' else '?'
        if not math.isnan(rE[j]):
            gruppi.setdefault(g, []).append(abs(rE[j]))
    top = sorted(((nomi_e[j], float(rE[j])) for j in range(len(nomi_e)) if not math.isnan(rE[j])), key=lambda x: -abs(x[1]))[:6]
    return OrderedDict([('t', t), ('quale', quale), ('gruppi_giudice2_rho_assoluto_medio', OrderedDict((g, float(np.mean(v))) for g, v in sorted(gruppi.items()))),
                        ('piu_associate_giudice2', top), ('profilo_A', OrderedDict((n, None if math.isnan(rA[j]) else float(rA[j])) for j, n in enumerate(G.CARATTERISTICHE)))])


def tempi_lavori():
    out = OrderedDict()
    for a in ('comuni', PERCORSO):
        d = os.path.join(amb_dir(a), 'righe')
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            r = json.load(open(os.path.join(d, fn), encoding='utf-8'))
            tipo = fn.split('__')[0]
            if r.get('secondi'):
                out.setdefault(tipo, []).append(r['secondi'])
    return OrderedDict((k, OrderedDict(lavori=len(v), media_minuti=round(statistics.mean(v) / 60, 1), massimo_minuti=round(max(v) / 60, 1), totale_minuti=round(sum(v) / 60, 1)))
                       for k, v in out.items())


def sintesi(versioni):
    st = json.load(open(percorso_stato(), encoding='utf-8')) if os.path.exists(percorso_stato()) else None
    ctr, aucK = controlli_giudici()
    o = OrderedDict([('esperimento', 'ia21'), ('testo', TESTO), ('percorso', PERCORSO), ('partenza', PARTENZA), ('solo_controlli', SOLO_CONTROLLI), ('versioni', versioni),
                     ('parametri', OrderedDict([('giri_max', N_GIRI), ('candidate', C_CAND), ('peso_scelte', PESO), ('epoche_affina', EP_AFFINA), ('lr_affina', LR_AFFINA),
                                                 ('libri_monitoraggio', L_MON), ('libri_finali', N_FIN), ('libri_struttura', N_STR), ('guardie_fermano', GUARDIE_FERMANO)])),
                     ('controlli_giudici', ctr), ('stato', st)])
    letture = OrderedDict()
    r = riassunto(TESTO, PERCORSO) if st is not None else None
    if r is None:
        o['letture'] = letture
        scrivi_json_md(o)
        return o
    T = st['ultimo_valido']
    m0 = misure_libri(0, 'mon')
    o['giro0'] = m0
    o['giri'] = st['giri']
    # ---- esaminatore: validita' e che cosa smaschera
    es1 = st['giri'][0]['esaminatore'] if st['giri'] else None
    esT = next((g['esaminatore'] for g in st['giri'] if g['t'] == T), None)
    letture['esaminatore_valido'] = OrderedDict([('AUC_giro_1_prima', es1 and es1['AUC_prima']), ('soglia', ESAM_MIN), ('valido', bool(es1) and es1['AUC_prima'] >= ESAM_MIN)])
    o['associazioni'] = OrderedDict()
    for t, quale in [(1, 'prima')] + ([(T, 'dopo')] if T >= 1 else []):
        try:
            o['associazioni']['giro %d, pagine %s' % (t, 'dell\'allievo di partenza' if quale == 'prima' else 'dell\'ultimo giro valido')] = associazioni(t, quale)
        except Exception as e:                                            # noqa: BLE001
            o['associazioni']['giro %d, %s (errore)' % (t, quale)] = OrderedDict([('errore', repr(e))])
    # ---- giudici sui libri finali
    o['partenza_libri'], o['finale_libri'] = r['g0'], r['finale']
    v21 = rif_v21(aucK)
    o['v21'] = v21
    ok_paper = ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito']
    ok_K = bool('K_positivo' in ctr and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito'] and ctr['K_vede_v21']['riuscito'])
    ok_A = ctr['A_positivo']['riuscito'] and ctr['A_negativo']['riuscito']
    letture['validita'] = OrderedDict([('giudici_paper', ok_paper), ('K', ok_K), ('A', ok_A), ('esaminatore', letture['esaminatore_valido']['valido'])])
    invalida = None
    if TESTO == 'voynich' and not (ok_paper and ok_K):
        invalida = 'lettura non valida (controllo dei giudici fallito: ' + ', '.join(n for n, b in (('paper', ok_paper), ('K', ok_K)) if not b) + ')'
    cl21, cl0 = classe(r['finale'], v21), classe(r['finale'], r['g0'])
    cA21, cA0 = classe(r['finale'], v21, ('A',)), classe(r['finale'], r['g0'], ('A',))
    e1, e2 = esito_v21(cl21), esito_progresso(cl0)
    if invalida:
        e1 = e2 = invalida
    elif not letture['esaminatore_valido']['valido']:
        e1 += ' (ma l\'esaminatore era debole al giro 1: non vale come merito dell\'esaminatore)'
        e2 += ' (ma l\'esaminatore era debole al giro 1)'
    letture['L1_contro_v21'] = OrderedDict([('esito', e1), ('giudici', cl21), ('A_riportato', cA21['A']), ('giro', T)])
    letture['L1b_contro_il_giro_0'] = OrderedDict([('esito', e2), ('giudici', cl0), ('A_riportato', cA0['A']), ('giro', T)])
    # ---- curva
    o['curva'] = [OrderedDict([('t', 0), ('M3', m0['M3']), ('e231', m0['e231'][0]), ('e266', m0['e266'][0]), ('K', m0['K'][0]), ('A', m0['A'][0])])] + [
        OrderedDict([('t', g['t']), ('M3', g['M3']), ('e231', g['giudici']['e231'][0]), ('e266', g['giudici']['e266'][0]), ('K', g['giudici']['K'][0]), ('A', g['giudici']['A'][0]),
                     ('esaminatore_prima', g['esaminatore']['AUC_prima']), ('esaminatore_dopo', g['esaminatore']['AUC_dopo']), ('guardie_violate', g['guardie_violate'])])
        for g in st['giri']]
    # ---- L4: l'allievo inganna l'esaminatore o scrive meglio?
    if es1 and esT:
        calo_es = es1['AUC_prima'] - esT['AUC_dopo']
        vic = sum(x['lettura'] == 'più vicino' for x in cl0.values())
        m_0, m_1 = media3(r['g0']), media3(r['finale'])
        letture['L4_giudice_amico'] = OrderedDict([('AUC_esaminatore_giro1_prima', es1['AUC_prima']), ('AUC_esaminatore_ultimo_dopo', esT['AUC_dopo']), ('calo_esaminatore', calo_es),
                                                   ('calo_media_tre_giudici', m_0 - m_1 if m_0 is not None and m_1 is not None else None), ('giudici_piu_vicini_al_giro_0', vic),
                                                   ('esito', 'migliora per davvero (almeno due giudici su tre tenuti da parte lo confermano)' if vic >= 2 and not any(x['lettura'] == 'più lontano' for x in cl0.values()) else
                                                    'impara a ingannare l\'esaminatore, non a scrivere il Voynich' if calo_es >= 0.10 and vic < 2 else
                                                    'fermo: ne\' l\'esaminatore ne\' i giudici tenuti da parte si muovono' if calo_es < 0.10 and vic < 2 else 'zona grigia')])
    # ---- L3: che cosa non riesce a imparare
    s3 = struttura(T) if STRUTTURA else None
    o['struttura'] = s3
    resta = OrderedDict()
    if s3:
        resta['struttura_che_resta_lontana'] = [m_ for m_, x in s3['frazione_di_cammino'].items() if x.get('lettura') == 'resta lontano']
        resta['struttura_chiusa_almeno_a_meta'] = [m_ for m_, x in s3['frazione_di_cammino'].items() if x.get('lettura') == 'chiuso almeno a meta\'']
    d0, d1 = r['g0'].get('diff_profilo_A'), r['finale'].get('diff_profilo_A')
    if d0 and d1:
        resta['profilo_A_residuo'] = OrderedDict((n, (d1[n] / d0[n] if abs(d0[n]) >= 0.02 else None)) for n in d0)
        resta['profilo_A_che_resta'] = [n for n, v in resta['profilo_A_residuo'].items() if v is not None and v >= 0.5]
    g1 = r['finale'].get('gruppi_e266') or {}
    resta['gruppi_giudice2_ancora_riconoscibili'] = sorted([(g, a) for g, a in g1.items() if a >= 0.65], key=lambda x: -x[1])
    letture['L3_cosa_non_impara'] = OrderedDict([('esito', 'vedi l\'elenco'), ('dettaglio', resta)])
    # ---- controlli del metodo: positivo (testi non Voynich) e negativo (cieco)
    if TESTO == 'voynich':
        pos = OrderedDict((t_, controllo_positivo(riassunto(t_, 'vero'))) for t_ in ('latino', 'sintetico', 'locale') if os.path.isdir(testo_dir_di(t_)))
        neg = controllo_negativo_cieco(riassunto('voynich', 'cieco'))
    else:
        pos = OrderedDict([(TESTO, controllo_positivo(r) if PERCORSO == 'vero' else OrderedDict([('esito', 'percorso cieco')]))])
        neg = controllo_negativo_cieco(r) if PERCORSO == 'cieco' else OrderedDict([('esito', 'non eseguito')])
    letture['C_positivo_non_Voynich'] = OrderedDict([('esito', 'riuscito' if any(x.get('riuscito') for x in pos.values()) else 'non riuscito o non leggibile' if pos else 'non eseguito'), ('per_testo', pos)])
    letture['C_negativo_cieco'] = neg
    if PERCORSO == 'vero' and TESTO == 'voynich':
        rc = riassunto('voynich', 'cieco')
        if rc:
            cl = classe(r['finale'], rc['finale'])
            vic, lon = sum(x['lettura'] == 'più vicino' for x in cl.values()), sum(x['lettura'] == 'più lontano' for x in cl.values())
            letture['L5_vero_contro_cieco'] = OrderedDict([('esito', 'l\'esaminatore vero fa meglio di quello cieco' if vic >= 2 and lon == 0 else
                                                           'non meglio del cieco: il miglioramento non viene dall\'esaminatore' if vic == 0 else 'zona grigia'),
                                                          ('giudici', cl), ('giro_vero', r['T']), ('giro_cieco', rc['T'])])
    o['letture'] = letture
    o['tempi'] = tempi_lavori()
    scrivi_json_md(o)
    return o


def nu(v, d=3):
    return I7.nu(v, d)


def mf(x, d=3):
    if x is None:
        return '—'
    if isinstance(x, (tuple, list)):
        return '%s ± %s' % (nu(x[0], d), nu(x[1], d)) if x[0] is not None else '—'
    return nu(x, d)


def scrivi_json_md(o):
    base = os.path.join(USCITA, 'ia21_%s_%s' % (o['testo'], o['percorso']))
    json.dump(o, open(base + '.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    L = o['letture']
    md = ['# IA21 (ia21) — L\'allievo e l\'esaminatore: testo %s, percorso %s' % (o['testo'], o['percorso']), '',
          'Preregistrazione: `preregistrazioni/ia21.md`.%s' % (' **Prova sui soli controlli (non Voynich).**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()),
          '- Parametri: %s.' % ', '.join('%s %s' % (k, v) for k, v in o['parametri'].items()), '']
    c = o['controlli_giudici']
    md += ['## Controlli dei giudici (sul testo %s)' % o['testo'], '']
    md.append('- Giudici del paper, positivo (giudice 2, parole rimescolate): AUC %s, soglia ≥ %s → %s.' % (nu(c['paper_positivo']['AUC']), nu(POS_PAPER, 2), nu(c['paper_positivo']['riuscito'])))
    md.append('- Giudici del paper, negativo (etichette a caso): giudice 1 %s, giudice 2 %s → %s.' % (nu(c['paper_negativo']['AUC_e231']), nu(c['paper_negativo']['AUC_e266']), nu(c['paper_negativo']['riuscito'])))
    if 'K_positivo' in c:
        md.append('- K: positivo %s → %s; negativo %s → %s; vede il v21 (AUC %s, soglia ≥ %s) → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['K_positivo']['AUC'].items()), nu(c['K_positivo']['riuscito']),
                                                                                                   nu(c['K_negativo']['AUC']), nu(c['K_negativo']['riuscito']), nu(c['K_vede_v21']['AUC']), nu(K_VEDE_V21, 2), nu(c['K_vede_v21']['riuscito'])))
    md.append('- A: positivo %s → %s; negativo %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['A_positivo']['AUC'].items()), nu(c['A_positivo']['riuscito']), nu(c['A_negativo']['AUC']), nu(c['A_negativo']['riuscito'])))
    if not L:
        md += ['', 'Nessun giro eseguito (o libri finali non ancora fatti).']
        open(base + '.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
        return
    st = o['stato']
    md += ['', '## I giri (AUC: più basso = più vicino al vero)', '',
           '| giro | esaminatore prima | esaminatore dopo | giudice 1 | giudice 2 | K | A (amico) | media dei tre | guardie violate |', '|---|---|---|---|---|---|---|---|---|']
    for x in o['curva']:
        md.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (x['t'], nu(x.get('esaminatore_prima')), nu(x.get('esaminatore_dopo')), nu(x['e231']), nu(x['e266']), nu(x['K']), nu(x['A']), nu(x['M3']),
                                                                      '; '.join(x.get('guardie_violate') or []) or '—'))
    md += ['', 'Arresto: **giro %s** (%s). Ultimo giro valido: %s.' % (st['fermo'], st['motivo'], st['ultimo_valido']), '']
    md += ['## Libri finali (%d libri nuovi, un giudice per libro)' % o['finale_libri']['libri'], '',
           '| | giudice 1 | giudice 2 | K | A (amico) | media dei tre |', '|---|---|---|---|---|---|']
    for nome, x in (('partenza (giro 0)', o['partenza_libri']), ('finale (giro %d)' % st['ultimo_valido'], o['finale_libri'])):
        md.append('| %s | %s | %s | %s | %s | %s |' % (nome, mf(x['e231']), mf(x['e266']), mf(x['K']), mf(x['A']), nu(x['M3'])))
    v = o['v21']
    md.append('| v21 (paper; K e A ricalcolati) | %s | %s | %s | %s | — |' % (mf(v['e231']), mf(v['e266']), mf(v['K']), mf(v['A'])))
    md += ['', '## Letture preregistrate', '']
    md.append('- Esaminatore valido (AUC al giro 1 sull\'allievo di partenza %s, soglia %s): %s.' % (nu(L['esaminatore_valido']['AUC_giro_1_prima']), nu(ESAM_MIN, 2), nu(L['esaminatore_valido']['valido'])))
    for chiave, titolo in (('L1_contro_v21', 'L1, finale contro il v21'), ('L1b_contro_il_giro_0', 'L1b, finale contro il giro 0')):
        if chiave in L:
            x = L[chiave]
            md.append('- **%s: %s.** %s. A (amico, riportato): %s.' % (titolo, x['esito'], '; '.join('%s %s (differenza %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items()),
                                                                  x['A_riportato']['lettura']))
    if 'L4_giudice_amico' in L:
        x = L['L4_giudice_amico']
        md.append('- **L4, giudice amico: %s.** Esaminatore: AUC %s al giro 1 (sull\'allievo di partenza) → %s sull\'ultimo allievo (calo %s); media dei tre giudici: calo %s; giudici "più vicino" al giro 0: %d su 3.' % (
            x['esito'], nu(x['AUC_esaminatore_giro1_prima']), nu(x['AUC_esaminatore_ultimo_dopo']), nu(x['calo_esaminatore']), nu(x['calo_media_tre_giudici']), x['giudici_piu_vicini_al_giro_0']))
    if 'L5_vero_contro_cieco' in L:
        x = L['L5_vero_contro_cieco']
        md.append('- **L5, esaminatore vero contro cieco: %s.** %s.' % (x['esito'], '; '.join('%s %s' % (j, y['lettura']) for j, y in x['giudici'].items())))
    cp = L['C_positivo_non_Voynich']
    md.append('- **Controllo positivo (testo non Voynich): %s.** %s' % (cp['esito'], '; '.join('%s: %s (calo %s)' % (t_, x['esito'], nu(x.get('calo'))) for t_, x in cp['per_testo'].items())))
    md.append('- **Controllo negativo (esaminatore cieco): %s.**' % L['C_negativo_cieco']['esito'])
    d = L['L3_cosa_non_impara']['dettaglio']
    md += ['', '## Che cosa resta lontano dal vero a fine percorso', '']
    if 'struttura_che_resta_lontana' in d:
        md.append('- Struttura che resta lontana (frazione di cammino sotto 0,5): %s. Chiusa almeno a metà: %s.' % (', '.join(d['struttura_che_resta_lontana']) or '—', ', '.join(d['struttura_chiusa_almeno_a_meta']) or '—'))
    if 'profilo_A_che_resta' in d:
        md.append('- Profilo di sorpresa del giudice A: differenze rimaste almeno a metà di quelle di partenza: %s.' % (', '.join(d['profilo_A_che_resta']) or '—'))
    md.append('- Gruppi del giudice 2 ancora riconoscibili (AUC ≥ 0,65): %s.' % (', '.join('%s %s' % (g, nu(a, 2)) for g, a in d['gruppi_giudice2_ancora_riconoscibili']) or '—'))
    if o.get('struttura'):
        s = o['struttura']
        md += ['', '| misura | vero | partenza | finale | v21 | frazione di cammino | lettura |', '|---|---|---|---|---|---|---|']
        for m_, x in s['frazione_di_cammino'].items():
            md.append('| %s | %s | %s | %s | %s | %s | %s |' % (m_, nu(x.get('vero'), 4), nu(x.get('partenza'), 4), nu(x.get('finale'), 4), nu(x.get('v21'), 4), nu(x.get('frazione_di_cammino'), 2), x['lettura']))
    md += ['', '## Che cosa l\'esaminatore sembra usare (associazione, non prova)', '']
    for nome, a in (o.get('associazioni') or {}).items():
        if not a or 'errore' in a:
            md.append('- %s: non calcolata (%s).' % (nome, (a or {}).get('errore', 'dati mancanti')))
            continue
        md.append('- %s: gruppi del giudice 2 (|ρ| medio): %s. Più associate: %s. Profilo di A (ρ): %s.' % (
            nome, ', '.join('%s %s' % (g, nu(x, 2)) for g, x in a['gruppi_giudice2_rho_assoluto_medio'].items()),
            '; '.join('%s %s' % (n, nu(x, 2)) for n, x in a['piu_associate_giudice2'][:4]), ', '.join('%s %s' % (n, nu(x, 2)) for n, x in a['profilo_A'].items())))
    md += ['', '## Tempi (minuti per lavoro, macchina condivisa)', '']
    for k, x in o['tempi'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media_minuti'], x['massimo_minuti'], x['totale_minuti']))
    open(base + '.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


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
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('testo: %s (%s), percorso %s, partenza %s; %d righe, %d pagine, %d segni; giri %d, candidate %d, peso %s' % (
        TESTO, 'prova sui controlli' if SOLO_CONTROLLI else 'Voynich', PERCORSO, PARTENZA, len(righe), len(I7.per_pagina(righe)), len(voc['unita']),
        N_GIRI, C_CAND, PESO), flush=True)
    esiste = os.path.isdir(amb_dir(PERCORSO)) and any(os.scandir(amb_dir(PERCORSO)))
    if esiste and os.environ.get('RIPRENDI') != '1' and os.environ.get('RIFAI') != '1' and ('G' in FASI or 'F' in FASI):
        raise SystemExit('ci sono gia\' risultati in %s: usa RIPRENDI=1 per riprendere o RIFAI=1 per cancellarli e rifare' % amb_dir(PERCORSO))
    if os.environ.get('RIFAI') == '1' and esiste:
        shutil.rmtree(amb_dir(PERCORSO))
    os.makedirs(amb_dir('comuni'), exist_ok=True)
    os.makedirs(amb_dir(PERCORSO), exist_ok=True)
    log = os.path.join(USCITA, 'ia21_corse_%s_%s.jsonl' % (TESTO, PERCORSO))
    ex = Esecutore(int(os.environ.get('PROCESSI', 4)), log)
    try:
        stato = None
        if '0' in FASI:
            esegui_fase0(ex)
        if 'G' in FASI:
            stato = esegui_giri(ex)
        elif os.path.exists(percorso_stato()):
            stato = json.load(open(percorso_stato(), encoding='utf-8'))
        if 'F' in FASI:
            if stato is None:
                raise SystemExit('FERMO: i giri non sono stati fatti')
            esegui_finale(ex, stato)
    finally:
        ex.chiudi()
    if 'S' in FASI:
        o = sintesi(versioni)
        for k, x in o.get('letture', {}).items():
            if isinstance(x, dict) and 'esito' in x:
                print('%s: %s' % (k, x['esito']), flush=True)


if __name__ == '__main__':
    main()
