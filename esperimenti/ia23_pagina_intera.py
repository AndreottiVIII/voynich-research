# -*- coding: utf-8 -*-
"""Esperimento IA23 (ia23): l'eco da tutta la pagina gia' scritta, con il legame fra parole e il vocabolario della pagina.

Domanda (scelta di Davide, 21/11/2026): un imitatore che riprende le parole da TUTTA la pagina gia' scritta, non solo dalle righe vicine, porta insieme al vero
l'eco (copia netta e quota locale Λ), il legame fra parole (contatto e D) e il vocabolario della pagina (G9)?
Punto di partenza (ia22): E2 ha copia netta, contatto e D al vero ma Λ 0,360 contro 0,207 (eco quasi il doppio troppo locale, perche' i candidati sono solo la riga
in corso e quella sopra); nessuno E arriva al G9 vero (0,040). Preregistrazione: preregistrazioni/ia23.md. I modelli stanno in pagina_modelli.py, la fase 0
descrittiva (profilo di distanza dell'eco) in pagina_fase0.py, le prove di unita' in pagina_prove.py.

Che cosa fa il codice (in parole semplici)
- Fase A: 30 addestramenti (3 imitatori P1-P3 x 5 pieghe per foglio x 2 repliche) + eventuali modelli del giudice A mancanti.
    P1 eco come spinta sui logit (come E1) con i candidati di tutta la pagina; P2 puntatore vincolato al contatto (come E2); P3 puntatore con inizio rigenerato (come E3).
- Fase Q: controlli di sensibilita' su testi sintetici (tema di pagina + eco locale + contatto piantati insieme; "senza niente").
- Fase C: libri onesti (N_LIBRI23 per tipo, meta' per replica) con giudici del paper, giudice A (riportato), copia a memoria e ripetizioni; e le stesse misure sui libri di
  riferimento letti dalle cache (M1, M5 di ia20; E1, E2, E3 di ia22; mai riaddestrati).
- Fase F: fase 0 (profilo di distanza dell'eco) sul testo vero, sul v21, sui riferimenti, con i controlli sintetici.
- Fase D: controlli dei giudici, giudice K, misure di struttura, fase 0 sui libri P.
- Fase S: sintesi e letture preregistrate (L1, L1b, L2, L3, L4).
Uscite (solo numeri e aggregati): risultati/ia23_pagina_intera.json e .md e, una riga per lavoro, risultati/ia23_corse.jsonl. Modelli, libri e profili in dati/cache/ia23
(CACHE23, protetti: non si committano).

    nohup bash strumenti/coda.sh ia23 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia23" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO23=1 RIF23=ricalcola USCITA=<cartella fuori dal repo> python esperimenti/ia23_pagina_intera.py   (prova sul latino)

Variabili (oltre a quelle di ia07, ia20 e ia22, che si importano): PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere A Q C F D S; predefinito AQCFDS), FILTRO.
Nuove: CACHE23, EPOCHE23 (150), PAZIENZA23 (10), N_LIBRI23 (10), PICCOLO23 (solo prove; deve coincidere con PICCOLO20), EPOCHE_SENS23 (60), TIPI23 (cifre, senza
virgole: 123 = P1 P2 P3), RIF23 ('cache' = riferimenti letti dalle cache di ia20 e ia22; 'ricalcola' = solo prove del codice). I valori predefiniti sono quelli
preregistrati. Nessun valore contiene virgole o due punti (la coda li dividerebbe).
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
# ia22 vuole PICCOLO22 == PICCOLO20 (le prove usano la taglia piccola in tutti e due): qui lo si fa coincidere
os.environ.setdefault('PICCOLO22', os.environ.get('PICCOLO20', '0'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import ia20_imitatore_gradini as I20  # noqa: E402
import ia22_eco_e_legame as I22  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import pagina_modelli as PM  # noqa: E402
import pagina_fase0 as PF  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NOME = 'ia23_pagina_intera'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE23 = os.environ.get('CACHE23', os.path.join(USCITA, 'ia23_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia23'))
MOD23, LIBRI23, MISURE23 = os.path.join(CACHE23, 'modelli'), os.path.join(CACHE23, 'libri'), os.path.join(CACHE23, 'misure')
PICCOLO = os.environ.get('PICCOLO23') == '1'
if PICCOLO != I20.PICCOLO:
    raise SystemExit('PICCOLO23 e PICCOLO20 devono avere lo stesso valore (le prove del codice usano la taglia piccola in tutti e due)')
IDX = OrderedDict((t, i) for i, t in enumerate(PM.TIPI))                       # P1..P3 -> 0..2
TIPI23 = tuple(PM.TIPI[int(x) - 1] for x in os.environ.get('TIPI23', '123') if x.isdigit())
REPLICHE23 = (0, 1)
EPOCHE23 = int(os.environ.get('EPOCHE23', 150))
PAZIENZA23 = int(os.environ.get('PAZIENZA23', 10))
N_LIBRI23 = int(os.environ.get('N_LIBRI23', 10))              # libri per tipo (meta' dalla replica 0, meta' dalla 1)
EPOCHE_SENS23 = int(os.environ.get('EPOCHE_SENS23', 60))
PAZIENZA_SENS23 = 10
RIF23 = os.environ.get('RIF23', 'cache')
PIEGHE = I7.PIEGHE
N_RIF = I20.N_LIBRI20                                          # libri di riferimento per tipo (10)
RIF_M = (1, 5)                                                 # M1 e M5 di ia20 (cache di ia20)
RIF_E = ('E1', 'E2', 'E3')                                     # i corrispondenti di P1-P3 (cache di ia22): giudici, struttura, fase 0
RIF_E0 = ('E0',)                                               # E0 di ia22: solo fase 0
CORRISP = OrderedDict([('P1', 'E1'), ('P2', 'E2'), ('P3', 'E3')])
ETICHETTE = ['M1', 'E1', 'E2', 'E3', 'M5', 'P1', 'P2', 'P3']  # ordine nelle tabelle
CHIAVI_V21 = I20.CHIAVI_V21

# ---- soglie (fissate nella preregistrazione; quelle dei controlli di sensibilita' dopo le prove su testi non Voynich: dichiarato)
SOGLIA_ERRORI = I20.SOGLIA_ERRORI                              # 2 errori
VERO_TOL = I20.VERO_TOL                                        # "al vero": entro 2 errori o 5% del vero
SENS23 = OrderedDict([('guadagno_su_M1', 0.10),                # tema+eco+contatto: validazione almeno cosi' sotto M1 (bit per segno)
                      ('eco_rapporto', 0.70),                  # tasso di eco locale dei fogli scritti almeno questa frazione di quello del testo piantato
                      ('tema_rapporto', 0.50),                 # eccesso di tema (tasso lontano condizionato meno quello delle righe rimescolate) scritto / piantato, almeno
                      ('tema_E_max', 0.30),                    # il controllo vede la differenza: E2 di ia22 sta sotto questa frazione
                      ('contatto_rapporto', 0.80),             # quota del glifo iniziale preferito e informazione mutua: almeno questa frazione
                      ('senza_guadagno_max', 0.03),            # senza niente: guadagno su M1 al massimo cosi' (era 0,02 in ia22: alzato dopo le prove, vedi la preregistrazione)
                      ('senza_massa_max', 0.10)])              # senza niente: massa di copia media del puntatore al massimo cosi'
SENS_TESTI = OrderedDict([('tec', dict(eco=0.25, ritocco=0.6, tema=0.3, n_tema=25, contatto=0.7)), ('senza', dict(eco=0.0, tema=0.0, contatto=0.0))])
SENS_MODELLI = OrderedDict([('tec', ('M1', 'E1', 'E2', 'E3', 'P1', 'P2', 'P3')), ('senza', ('M1', 'E2', 'P1', 'P2', 'P3'))])
F0C_TESTI = OrderedDict([('tema_eco', dict(eco=0.25, tema=0.3)), ('solo_eco', dict(eco=0.25, tema=0.0)), ('solo_tema', dict(eco=0.0, tema=0.3)), ('nulla', dict(eco=0.0, tema=0.0))])
F0C_ATTESO = OrderedDict([('tema_eco', ('presente', 'presente')), ('solo_eco', ('assente', 'presente')), ('solo_tema', ('presente', 'assente')), ('nulla', ('assente', 'assente'))])
MISURE_STR = I20.MISURE_STR
MISURE_ECO = ['copia_netta', 'lam']                            # l'eco
MISURE_LEGAME = ['contatto', 'D']                              # il legame fra parole
BERSAGLI_L2 = ['lam', 'G9']                                    # P contro E corrispondente: bersagli
MISURE_F0 = OrderedDict([('locale', 'profilo: quota di riprese a 0-1 righe'), ('lontana', 'profilo: quota di riprese a 2 righe o piu\''),
                         ('tema_cond', 'tasso lontano condizionato (tema)'), ('quota_tema', 'quota di riprese di tema'),
                         ('eccesso_tema', 'eccesso di tema sul caso'), ('eccesso_locale', 'eccesso locale sul caso')])
GIUDICI = I20.GIUDICI
_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def seme_str(*a):
    return MS.seme_str(*a)


def mes(xs):
    return MS.media_es(xs)


def etichetta(nome):
    return nome.split(':')[0]


def e_nuovo(nome):
    return nome[0] == 'P' and nome[1].isdigit()


def e_rifE(nome):
    return nome[0] == 'E' and nome[1].isdigit()


def e_rifM(nome):
    return nome[0] == 'M' and nome[1].isdigit()


# ---------------------------------------------------------------- pagine e modelli

def pagine_fold23(piega, tipo, dp=None, tag='reale'):
    """(ctx, add, val, fuori, fc): le pagine del modello della piega preparate per il tipo P; `ctx` ha le K parole piu' frequenti dell'addestramento, `fc` la classe di
    frequenza di ogni tipo di parola dell'addestramento."""
    k = (tag, piega, tipo, PICCOLO)
    if k in _C:
        return _C[k]
    for kk in [x for x in _C if isinstance(x, tuple) and x[0] == tag and x[1] == piega and x[2] != tipo]:
        del _C[kk]                                             # una sola preparazione alla volta per piega: la memoria
    voc = I7.vocabolario()
    dp = dp or I16.dati_pagine()
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    sel = lambda ff: [d for d in dp.values() if d['foglio'] in set(ff)]
    K, S = (40, 12) if PICCOLO else (GM.K_TIPI, GM.S_CAND)
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(sel(f_add), GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    fc = PM.tabella_freq(PM.conta_tipi(sel(f_add), ctx))
    add, val, fuori = PM.prepara_insiemi([sel(f_add), sel(f_val), sel(f_fuori)], ctx, tipo, fc)
    _C[k] = (ctx, add, val, fuori, fc)
    return _C[k]


def seme_modello(tipo, piega, replica):
    return 23000 + 1000 * IDX[tipo] + 100 * replica + piega


def percorso_modello(tipo, piega, replica, est):
    return os.path.join(MOD23, 'ia23_%s_%s_%d%s' % (tipo, piega, replica, est))


def addestra(tipo, piega, replica):
    inizio = time.time()
    voc = I7.vocabolario()
    ctx, add, val, fuori, fc = pagine_fold23(piega, tipo)
    cfg = PM.cfg_completa(tipo, voc, ctx, PICCOLO)
    nome = '%s p%s r%d' % (tipo, piega, replica)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = PM.addestra_modello(cfg, ctx, add, val, seme_modello(tipo, piega, replica), EPOCHE23, PAZIENZA23, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'addestra|%s|%s|%d' % (tipo, piega, replica)), ('tipo', tipo), ('piega', piega), ('replica', replica),
                       ('parametri', sum(p.numel() for p in m.parameters())), ('pagine', [len(add), len(val), len(fuori)]),
                       ('epoche', len(ca)), ('epoca_scelta', scelta), ('arrivata_al_massimo', len(ca) >= EPOCHE23 and scelta > EPOCHE23 - PAZIENZA23),
                       ('curva_validazione', cv), ('curva_addestramento', ca),
                       ('bpc_addestramento', round(PM.bpc_pagine(m, ctx, add), 5)), ('bpc_validazione', round(PM.bpc_pagine(m, ctx, val), 5)),
                       ('bpc_fuori', round(PM.bpc_pagine(m, ctx, fuori), 5))])
    ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    ris['appresi'] = PM.parametri_appresi(m)
    if tipo != 'P1':
        ris['puntatore'] = PM.massa_copia(m, ctx, fuori)
    ris['secondi'] = round(time.time() - inizio, 1)
    PM.salva_modello(m, percorso_modello(tipo, piega, replica, '.pt'), voc['segni'], ctx, fc,
                     dict(tipo=tipo, piega=piega, replica=replica, epoca_scelta=scelta, solo_prova=bool(SOLO_CONTROLLI)))
    json.dump(ris, open(percorso_modello(tipo, piega, replica, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def carica(tipo, piega, replica):
    k = ('modello', tipo, piega, replica)
    if k not in _C:
        _C[k] = PM.carica_modello(percorso_modello(tipo, piega, replica, '.pt'), I7.vocabolario())
    return _C[k]


# ---------------------------------------------------------------- scrivere

def scrivi_pagina23(m, ctx, pen, regole, rp, voc, D, rng, conta):
    """Una pagina con la disposizione `rp`. P1: segno per segno (la spinta e' nei logit). P2, P3: a inizio parola il puntatore sceglie fra libero e un tipo di parola
    gia' scritto nella pagina (e strada); le strade 0-3 come in M5 e E0-E3, le strade 4-6 (P3) con il primo (e il secondo) glifo scritti dalla GRU."""
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    nt = PM.NT_PUNT.get(m.tipo, 0)
    pen.apri()
    lg = None
    for t in I7.testa_pagina(rp, voc):
        lg = pen.dai(t)
    if nt:
        psub, pins = pen.tabelle_ritocco()
    out = []
    for j, x in enumerate(rp):
        for t in I7.testa_riga(x, j, voc, D):
            lg = pen.dai(t)
        parole, lung, prima, fine = [], 0, 'inizio', False
        while not fine:
            w2 = None
            if nt and pen.stato.K:
                pf, ppi = pen.puntatore_pagina()
                pr = np.concatenate([[pf], ppi.reshape(-1)])
                pr = pr / pr.sum()
                for _ in range(8):
                    idx = int(rng.choice(len(pr), p=pr))
                    if idx == 0:
                        break
                    k, tipo_r = divmod(idx - 1, nt)
                    c = pen.stato.tipi[k]
                    if tipo_r <= 3:
                        w2 = GM.campiona_ritocco(c, tipo_r, psub, pins, rng)
                    else:
                        w2 = I22.rigenera(pen, c, tipo_r, lg, regole, lung, prima, ctx, rng)
                    if w2 is not None and len(w2):
                        stringhe = [unita[u] for u in w2]
                        if D(''.join(stringhe)) == stringhe:
                            conta[('uguale', 'cambia', 'aggiunge', 'toglie', 'primo_riscritto', 'glifo_davanti', 'due_riscritti')[tipo_r]] += 1
                            break
                    w2 = None
                conta['libero' if w2 is None else 'copia'] += 1
            if w2 is not None:
                for u in w2:
                    lg = pen.dai(u0 + u)
                lung += len(w2)
                ammessi = [SP, EOL] if lung < voc['lmax'] else [EOL]
                z = np.array([lg[a] for a in ammessi])
                z = np.exp(z - z.max())
                s = ammessi[I20.campiona(z / z.sum(), rng)]
                lg = pen.dai(s)
                parole.append(''.join(unita[u] for u in w2))
                prima = 'spazio'
                if s == EOL:
                    fine = True
                else:
                    lung += 1
                continue
            parola = []
            while True:
                amm = regole.ammessi(parola, lung, prima)
                z = np.array([lg[a] for a in amm])
                z = np.exp(z - z.max())
                s = amm[I20.campiona(z / z.sum(), rng)]
                lg = pen.dai(s)
                if s == EOL:
                    parole.append(''.join(parola))
                    fine = True
                    break
                lung += 1
                if s == SP:
                    parole.append(''.join(parola))
                    prima = 'spazio'
                    break
                parola.append(regole.unita[s])
                prima = 'segno'
        out.append((x['pagina'], x['ini'], parole))
    return out


def scrivi_libro23(tipo, replica, seme):
    righe, voc, D = I7.libro_vero(), I7.vocabolario(), I7.divisore()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    pg = I7.pieghe()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())
    regole = I20.RegoleScrittura(voc)
    penne = {}
    conta = Counter()
    out = []
    for pag, rp in pp.items():
        k = pg[I7.foglio_di(pag)]
        if k not in penne:
            m, ctx, fc = carica(tipo, k, replica)
            penne[k] = (m, ctx, PM.Penna23(m, ctx, fc, cap + 8))
        m, ctx, pen = penne[k]
        out += scrivi_pagina23(m, ctx, pen, regole, rp, voc, D, rng, conta)
    return out, conta


def percorso_libro(tipo, i):
    return os.path.join(LIBRI23, 'ia23_libro_%s_%d.txt' % (tipo, i))


def lavoro_libro(tipo, i):
    inizio = time.time()
    replica = I7.replica_del_libro(i, N_LIBRI23)
    seme = 2300000 + 10000 * IDX[tipo] + i
    os.makedirs(LIBRI23, exist_ok=True)
    percorso = percorso_libro(tipo, i)
    conta = None
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t, conta = scrivi_libro23(tipo, replica, seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia23, libro %s %d' % (tipo, i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('replica', replica), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    if conta is not None and tipo != 'P1':
        ris['modi_scrittura'] = OrderedDict(conta)
    ris.update(I22.misura_libro(t, os.path.join(LIBRI23, 'ia23_tabella_%s_%d.npz' % (tipo, i))))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def percorso_riferimento(sigla, i):
    """Libro i di un riferimento: M1, M5 (cache di ia20), E0-E3 (cache di ia22)."""
    if sigla[0] == 'M':
        return I20.percorso_libro(int(sigla[1]), i)
    return I22.percorso_libro(sigla, i)


def crea_riferimento(sigla, i):
    """Solo con RIF23=ricalcola (prove del codice): scrive il libro del riferimento con il codice di ia20 o di ia22 nella cache di prova."""
    if sigla[0] == 'M':
        I20.lavoro_libro(int(sigla[1]), i)
    else:
        I22.lavoro_libro(sigla, i)


def lavoro_riflibro(sigla, i):
    """Misure dei giudici sul libro i di un riferimento (M1, M5, E1, E2, E3), letto dalla cache (RIF23=cache). Con RIF23=ricalcola (solo prove) prima si scrive."""
    inizio = time.time()
    percorso = percorso_riferimento(sigla, i)
    if not os.path.exists(percorso):
        if RIF23 != 'ricalcola':
            raise RuntimeError('manca il libro di riferimento %s (RIF23=cache): va fatto con ia20 o ia22' % percorso)
        crea_riferimento(sigla, i)
    t = I7.leggi_file(percorso)
    ris = OrderedDict([('lavoro', 'riflibro|%s|%d' % (sigla, i)), ('sigla', sigla), ('i', i), ('replica', I7.replica_del_libro(i, N_RIF)), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(I22.misura_libro(t, None))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_rifscrivi(sigla, i):
    """Solo prove: scrive il libro di un riferimento (E0, che serve alla sola fase 0) con il codice di ia22."""
    inizio = time.time()
    if not os.path.exists(percorso_riferimento(sigla, i)):
        crea_riferimento(sigla, i)
    return OrderedDict([('lavoro', 'rifscrivi|%s|%d' % (sigla, i)), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- controlli di sensibilita' (testi sintetici con tema, eco e contatto piantati)

def misure_sens23(rows, pref, D, seme):
    """Numeri del controllo su pagine (pagina -> righe): quelli di ia22 (tasso di eco locale = parole uguali o a una modifica da una delle ultime 28 parole, quota del
    glifo preferito, informazione mutua del contatto) piu' quelli del tema (profilo di distanza di pagina_fase0): quota locale e lontana, tasso lontano condizionato
    del testo e delle sue righe rimescolate, e l'eccesso di tema = la differenza (lo stesso numero della fase 0)."""
    base = I22.misure_sens(rows, pref, D)
    pr = PF.profilo_testo(rows, seme, per_pagina=False, nulli=True)
    m, mr = PF.misure(pr['testo']), PF.misure(pr['nullo_righe'])
    for k in ('locale', 'lontana', 'tema_cond', 'quota_tema', 'tema_lontano'):
        base[k] = m[k]
    base['tema_cond_righe_rimescolate'] = mr['tema_cond']
    base['eccesso_tema'] = (m['tema_cond'] - mr['tema_cond']) if m['tema_cond'] is not None and mr['tema_cond'] is not None else None
    return base


def lavoro_sens(testo, modello):
    """Un modello addestrato (piega 0) su un testo sintetico; validazione e fuori piega; per i modelli col puntatore la massa di copia; per `tec` si scrivono i fogli
    tenuti fuori e si misurano eco locale, tema e contatto, confrontati con gli stessi numeri del testo piantato."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    pref, temi = {}, {}
    sint = PM.sintetico_tema_eco_contatto(I7.libro_vero(), seme_str('ia23sint', testo), D, voc['unita'], pref_out=pref, temi_out=temi, **SENS_TESTI[testo])
    dps = I20.pagine_sintetiche(sint)
    nome = 'sens %s %s' % (testo, modello)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    ordine_m = ['M1', 'E1', 'E2', 'E3', 'P1', 'P2', 'P3']
    seme = 33000 + 10 * list(SENS_TESTI).index(testo) + ordine_m.index(modello)
    tag = 'sint23:' + testo
    if modello in ('M1', 'M5'):
        passo = 1 if modello == 'M1' else 5
        ctx, add, val, fuori = I20.pagine_fold(0, passo, dps, tag=tag)
        cfg = GM.cfg_completa(passo, voc, ctx, PICCOLO)
        m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS23, PAZIENZA_SENS23, messaggi=messaggio)
        bv, bf = round(GM.bpc_pagine(m, ctx, val), 5), round(GM.bpc_pagine(m, ctx, fuori), 5)
        punt = GM.massa_copia(m, ctx, fuori) if passo >= 5 else None
        penna = lambda: GM.Penna20(m, ctx, cap)
        scrivi = lambda pen, regole, rp, rng, conta: I20.scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta)
    elif modello[0] == 'E':
        ctx, add, val, fuori = I22.pagine_fold22(0, modello, dps, tag=tag)
        cfg = EM.cfg_completa(modello, voc, ctx, PICCOLO)
        m, cv, ca, scelta = EM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS23, PAZIENZA_SENS23, messaggi=messaggio)
        bv, bf = round(EM.bpc_pagine(m, ctx, val), 5), round(EM.bpc_pagine(m, ctx, fuori), 5)
        punt = EM.massa_copia(m, ctx, fuori) if modello != 'E1' else None
        penna = lambda: EM.Penna22(m, ctx, cap)
        scrivi = lambda pen, regole, rp, rng, conta: I22.scrivi_pagina22(m, ctx, pen, regole, rp, voc, D, rng, conta)
    else:
        ctx, add, val, fuori, fc = pagine_fold23(0, modello, dps, tag=tag)
        cfg = PM.cfg_completa(modello, voc, ctx, PICCOLO)
        m, cv, ca, scelta = PM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS23, PAZIENZA_SENS23, messaggi=messaggio)
        bv, bf = round(PM.bpc_pagine(m, ctx, val), 5), round(PM.bpc_pagine(m, ctx, fuori), 5)
        punt = PM.massa_copia(m, ctx, fuori) if modello != 'P1' else None
        penna = lambda: PM.Penna23(m, ctx, fc, cap)
        scrivi = lambda pen, regole, rp, rng, conta: scrivi_pagina23(m, ctx, pen, regole, rp, voc, D, rng, conta)
    ris = OrderedDict([('lavoro', 'sens|%s|%s' % (testo, modello)), ('testo', testo), ('modello', modello), ('epoche', len(ca)), ('epoca_scelta', scelta),
                       ('bpc_validazione', bv), ('bpc_fuori', bf), ('curva_validazione', cv)])
    if punt is not None:
        ris['puntatore'] = punt
    if modello[0] in 'EP':
        ris['appresi'] = EM.parametri_appresi(m) if modello[0] == 'E' else PM.parametri_appresi(m)
    if testo == 'tec':
        f_fuori = set(I7.fogli_della_piega(0)[2])
        pp = I7.per_pagina(sint)
        pag_fuori = [p for p in pp if I7.foglio_di(p) in f_fuori]
        rng = np.random.default_rng(seme_str('ia23scr', testo, modello))
        regole = I20.RegoleScrittura(voc)
        pen = penna()
        conta = Counter()
        t = []
        for p in pag_fuori:
            t += scrivi(pen, regole, pp[p], rng, conta)
        rows_gen = OrderedDict()
        for pag, ini, ps in t:
            rows_gen.setdefault(pag, []).append((bool(ini), [tuple(D(w)) for w in ps]))
        ris['scritto'] = misure_sens23(rows_gen, pref, D, seme_str('ia23sens', testo, modello, 'scritto'))
        ris['piantato'] = misure_sens23(I22.righe_a_rows(sint, D, set(pag_fuori)), pref, D, seme_str('ia23sens', testo, modello, 'piantato'))
        ris['modi_scrittura'] = OrderedDict(conta)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


cap = None                                                              # capacita' massima di una pagina (si fissa in avvia_processo)


def fissa_capacita():
    global cap
    voc = I7.vocabolario()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in I7.per_pagina(I7.libro_vero()).values()) + 8
    I22.fissa_capacita()


# ---------------------------------------------------------------- catalogo dei libri da misurare

def nomi_giudicati():
    """Nomi dei libri giudicati: P<k>:i (i nuovi), M1:i e M5:i (ia20), E1:i-E3:i (ia22), V21:k (v21 senza messaggio di ia01), ctrl:* (controlli)."""
    nomi = []
    for t in TIPI23:
        nomi += ['%s:%d' % (t, i) for i in range(1, N_LIBRI23 + 1) if os.path.exists(percorso_libro(t, i))]
    for p in RIF_M:
        nomi += ['M%d:%d' % (p, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento('M%d' % p, i))]
    for s in RIF_E:
        nomi += ['%s:%d' % (s, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento(s, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    """Per le misure di struttura: tutti i libri nuovi e di riferimento giudicati e i primi 10 V21."""
    out = [x for x in nomi if e_nuovo(x) or e_rifM(x) or e_rifE(x)]
    out += [x for x in nomi if x.startswith('V21:')][:10]
    return out


def nomi_f0_riferimenti():
    nomi = []
    for s in ['M%d' % p for p in RIF_M] + list(RIF_E) + list(RIF_E0):
        nomi += ['%s:%d' % (s, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento(s, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21][:10]
    return nomi


def t_di(nome):
    k = int(nome.split(':')[1]) if ':' in nome and nome.split(':')[1].isdigit() else None
    if e_nuovo(nome):
        return I7.leggi_file(percorso_libro(nome.split(':')[0], k))
    if e_rifM(nome) or e_rifE(nome):
        return I7.leggi_file(percorso_riferimento(nome.split(':')[0], k))
    return I16.t_di(nome)


def rows_di(nome):
    if e_nuovo(nome) or e_rifM(nome) or e_rifE(nome):
        return I7.libro_A_da_righe(t_di(nome))
    return I16.rows_di(nome)


# ---------------------------------------------------------------- lavori di misura (fasi D e F)

def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_giudicati():
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE23, exist_ok=True)
    with open(os.path.join(MISURE23, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome):
    """Come ia22.lavoro_M, ma i libri si leggono con `rows_di` e `t_di` di ia23."""
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
        rng = np.random.default_rng(200023)
        ps = list(cp)
        bs = [AP.firma_da_conti(I20.somma_conti([cp[ps[i]] for i in rng.integers(0, len(ps), len(ps))])) for _ in range(200)]
        ris['bordi_ic'] = OrderedDict((kk, [float(np.nanpercentile([b[kk] for b in bs if b[kk] is not None], q)) for q in (2.5, 97.5)]) for kk in ris['bordi'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_struttura(nomi_giudicati()):
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


def lavoro_F0(nome):
    """Fase 0 su un testo (`vere`, un libro): conti del profilo di distanza dell'eco (testo e due riferimenti a caso). Solo numeri."""
    inizio = time.time()
    c = I7.contesto_A()
    rows = c['vere'] if nome == 'vere' else rows_di(nome)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'F0|%s' % nome)])
    ris['profilo'] = PF.profilo_testo(pag, seme_str('ia23F0', nome), per_pagina=(nome == 'vere'))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_F0c(nome):
    """Controllo della fase 0 su un testo sintetico (disposizione e vocabolario del libro dato; nelle prove: latino) con tema e/o eco locale piantati o assenti."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    c = I7.contesto_A()
    sint = PM.sintetico_tema_eco_contatto(I7.libro_vero(), seme_str('ia23F0c', nome), D, voc['unita'], contatto=0.0, **F0C_TESTI[nome])
    rows = I22.righe_a_rows(sint, D)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'F0c|%s' % nome), ('piantato', F0C_TESTI[nome])])
    ris['profilo'] = PF.profilo_testo(pag, seme_str('ia23F0c', nome, 'p'), per_pagina=True)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        tipo = args[0]
        if tipo == 'addestra':
            return addestra(args[1], args[2], int(args[3]))
        if tipo == 'rifaddestra':
            r = I20.addestra(int(args[1]), args[2], int(args[3]))
            r['lavoro'] = ident
            return r
        if tipo == 'rifaddestraE':
            r = I22.addestra(args[1], args[2], int(args[3]))
            r['lavoro'] = ident
            return r
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
        if tipo == 'sens':
            return lavoro_sens(args[1], args[2])
        if tipo == 'libro':
            return lavoro_libro(args[1], int(args[2]))
        if tipo == 'riflibro':
            return lavoro_riflibro(args[1], int(args[2]))
        if tipo == 'rifscrivi':
            return lavoro_rifscrivi(args[1], int(args[2]))
        if tipo == 'K':
            return lavoro_K(int(args[1]))
        if tipo == 'M':
            return lavoro_M(args[1])
        if tipo == 'D':
            return lavoro_D(int(args[1]))
        if tipo == 'F0':
            return lavoro_F0(args[1])
        if tipo == 'F0c':
            return lavoro_F0c(args[1])
        if tipo in ('O', 'caso', 'ctrlA', 'casoA'):
            return I7.lavoro(tuple(args))
        raise ValueError(tipo)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    I7.avvia_processo()
    fissa_capacita()


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
                breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'bpc_fuori', 'AUC_e231', 'AUC_e266', 'AUC_A', 'AUC', 'G9') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


# ---------------------------------------------------------------- analisi e letture

def leggi_corse(percorso):
    return I16.leggi_corse(percorso)


def mf(x, d=3):
    return I20.mf(x, d)


def bpc_riferimento(sigla):
    """Bit per segno dei 10 modelli di un riferimento (M1, M5 di ia20; E1-E3 di ia22), dalle schede json delle cache (solo numeri)."""
    v, f = [], []
    for k in range(PIEGHE):
        for r in (0, 1):
            p = I20.percorso_modello(int(sigla[1]), k, r, '.json') if sigla[0] == 'M' else I22.percorso_modello(sigla, k, r, '.json')
            if os.path.exists(p):
                d = json.load(open(p, encoding='utf-8'))
                v.append(d['bpc_validazione'])
                f.append(d['bpc_fuori'])
    return OrderedDict(modelli=len(v), validazione=mes(v), fuori=mes(f))


def misure_f0_libro(profilo):
    """Dalle somme di un libro (`testo`, `nullo_righe`, `nullo_parole`) i numeri del profilo e gli eccessi sul caso."""
    mT, mR, mP = PF.misure(profilo['testo']), PF.misure(profilo['nullo_righe']), PF.misure(profilo['nullo_parole'])
    x = OrderedDict((k, mT[k]) for k in ['q_' + c for c in PF.CLASSI] + ['senza_ripresa', 'locale', 'lontana', 'ripresa', 'tema_cond', 'quota_tema', 'tema_lontano'])
    x['eccesso_tema'] = (mT['tema_cond'] - mR['tema_cond']) if mT['tema_cond'] is not None and mR['tema_cond'] is not None else None
    x['eccesso_locale'] = (mT['locale'] - mP['locale']) if mT['locale'] is not None and mP['locale'] is not None else None
    return x


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    c_ctx = I7.contesto_A()
    n_pag = len(c_ctx['ids'])
    out = OrderedDict(esperimento='ia23', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=errori, tipi=list(TIPI23))
    # ---- modelli
    modelli = [C[k] for k in sorted(C) if k.startswith('addestra|')]
    out['modelli'] = [OrderedDict((k, v) for k, v in m.items() if k not in ('curva_validazione', 'curva_addestramento')) for m in modelli]
    bpc = OrderedDict()
    for t in TIPI23:
        ms = [m for m in modelli if m['tipo'] == t]
        if ms:
            bpc[t] = OrderedDict(modelli=len(ms), parametri=ms[0]['parametri'], validazione=mes([x['bpc_validazione'] for x in ms]), fuori=mes([x['bpc_fuori'] for x in ms]),
                                 epoche_scelte=mes([x['epoca_scelta'] for x in ms])[0], al_massimo=sum(bool(x['arrivata_al_massimo']) for x in ms),
                                 secondi_medi=statistics.mean(x['secondi'] for x in ms))
            if t != 'P1':
                bpc[t]['massa_copia_media'] = mes([x['puntatore']['massa_media'] for x in ms if x.get('puntatore')])[0]
    out['bpc'] = bpc
    out['bpc_riferimenti'] = OrderedDict((s, bpc_riferimento(s)) for s in ['M%d' % p for p in RIF_M] + list(RIF_E))
    appresi = OrderedDict()
    for t in TIPI23:
        ap = [m['appresi'] for m in modelli if m['tipo'] == t and m.get('appresi')]
        if not ap:
            continue
        a = OrderedDict()
        for k in ('distanza', 'occorrenze', 'frequenza', 'beta'):
            a[k] = np.mean([x[k] for x in ap], axis=0).round(3).tolist()
        if t == 'P2':
            a['gamma'] = mes([x['gamma'] for x in ap])
        appresi[t] = a
    out['appresi'] = appresi
    # ---- controlli dei giudici (come ia20, ia22)
    ctr = OrderedDict()
    pos = [C['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in C]
    caso = C.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=mes(pos)[0], soglia=I20.POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= I20.POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=I20.NEG_BANDA,
                                        riuscito=bool(caso) and all(I20.NEG_BANDA[0] <= caso[k] <= I20.NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    pa = OrderedDict((n, C['ctrlA|%s' % n].get('AUC_A') if 'ctrlA|%s' % n in C else None) for n in I7.NOMI_CTRL_A if n != 'righe')
    na = C['casoA|0']['AUC_A'] if 'casoA|0' in C else None
    ctr['A_positivo'] = OrderedDict(AUC=pa, soglia=I7.SOGLIA_POSITIVO_A, riuscito=pa.get('parole') is not None and all(v >= I7.SOGLIA_POSITIVO_A for v in pa.values() if v is not None))
    ctr['A_negativo'] = OrderedDict(AUC=na, banda=I20.NEG_BANDA, riuscito=na is not None and I20.NEG_BANDA[0] <= na <= I20.NEG_BANDA[1])
    profs = []
    for f in range(PIEGHE):
        p = os.path.join(MISURE23, 'K_f%d.pkl' % f)
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
        ctr['K_positivo'] = OrderedDict(AUC=posK, soglia=I20.POS_K, riuscito=bool(posK) and all(v >= I20.POS_K for v in posK.values()))
        ctr['K_negativo'] = OrderedDict(AUC=statistics.mean(neg), valori=neg, banda=I20.NEG_BANDA, riuscito=I20.NEG_BANDA[0] <= statistics.mean(neg) <= I20.NEG_BANDA[1])
        ctr['K_vede_v21'] = OrderedDict(AUC=mes(v21K)[0], soglia=I20.K_VEDE_V21, riuscito=bool(v21K) and statistics.mean(v21K) >= I20.K_VEDE_V21)
    ok_paper = ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito']
    ok_K = bool(prof) and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito'] and ctr['K_vede_v21']['riuscito']
    ok_A = ctr['A_positivo']['riuscito'] and ctr['A_negativo']['riuscito']
    out['controlli'] = ctr
    # ---- controlli di sensibilita' (fase Q): eco locale, tema di pagina e contatto piantati insieme
    sens = OrderedDict()
    sv = lambda t, m: C.get('sens|%s|%s' % (t, m))
    base = sv('tec', 'M1')
    sc = OrderedDict()
    if base:
        ep, ct = base['piantato']['tasso_eco'], base['piantato']['quota_preferito']
        e_piantato = base['piantato']['eccesso_tema']
        sc['piantato'] = OrderedDict(tasso_eco=ep, quota_preferito=ct, contatto=base['piantato']['contatto'], tema_cond=base['piantato']['tema_cond'],
                                     tema_cond_righe_rimescolate=base['piantato']['tema_cond_righe_rimescolate'], eccesso_tema=e_piantato)
        for m in ('M1', 'E1', 'E2', 'E3', 'P1', 'P2', 'P3'):
            r = sv('tec', m)
            if not r:
                continue
            g = r['scritto']
            x = OrderedDict(bpc_validazione=r['bpc_validazione'], guadagno_su_M1=base['bpc_validazione'] - r['bpc_validazione'], epoca_scelta=r['epoca_scelta'],
                            tasso_eco=g['tasso_eco'], eco_rapporto=g['tasso_eco'] / ep if ep else None, eccesso_tema=g['eccesso_tema'],
                            tema_rapporto=g['eccesso_tema'] / e_piantato if e_piantato and e_piantato > 0 and g['eccesso_tema'] is not None else None,
                            quota_preferito=g['quota_preferito'], contatto_rapporto_pref=g['quota_preferito'] / ct if ct else None, contatto=g['contatto'],
                            contatto_rapporto=(g['contatto'] / base['piantato']['contatto']) if base['piantato']['contatto'] else None)
            x['eco_ok'] = bool(x['guadagno_su_M1'] >= SENS23['guadagno_su_M1'] and x['eco_rapporto'] is not None and x['eco_rapporto'] >= SENS23['eco_rapporto'])
            x['tema_ok'] = bool(x['tema_rapporto'] is not None and x['tema_rapporto'] >= SENS23['tema_rapporto'])
            x['legame_ok'] = bool(x['contatto_rapporto_pref'] is not None and x['contatto_rapporto_pref'] >= SENS23['contatto_rapporto'] and x['contatto_rapporto'] is not None
                                  and x['contatto_rapporto'] >= SENS23['contatto_rapporto'])
            x['riuscito'] = x['eco_ok'] and x['tema_ok'] and x['legame_ok']
            sc[m] = x
    sens['tec'] = sc
    sn = OrderedDict()
    b1 = sv('senza', 'M1')
    for m in ('E2', 'P1', 'P2', 'P3'):
        r = sv('senza', m)
        if not r or not b1:
            continue
        mass = (r.get('puntatore') or {}).get('massa_media')
        gu = b1['bpc_validazione'] - r['bpc_validazione']
        sn[m] = OrderedDict(guadagno_su_M1=gu, massa_media=mass, riuscito=bool(gu <= SENS23['senza_guadagno_max'] and (mass is None or mass <= SENS23['senza_massa_max'])))
    sens['senza'] = sn
    # il controllo "vede la differenza": i P imparano il tema e E2 di ia22 no
    vede = None
    if 'E2' in sc and 'P2' in sc and sc['E2']['tema_rapporto'] is not None and sc['P2']['tema_rapporto'] is not None:
        vede = bool(sc['P2']['tema_ok'] and sc['E2']['tema_rapporto'] < SENS23['tema_E_max'])
    sens['vede_la_differenza_sul_tema'] = vede
    out['sensibilita'] = sens
    # sensibilita' provata = impara l'eco e il tema e non inventa guadagni dal nulla; "legame ok" e' un esito (lo scambio), non una condizione
    sens_ok = {t: bool(sc.get(t, {}).get('eco_ok') and sc.get(t, {}).get('tema_ok') and sn.get(t, {}).get('riuscito')) for t in TIPI23}
    # ---- libri e giudici per etichetta
    lib = OrderedDict()
    for t in TIPI23:
        lib[t] = [C['libro|%s|%d' % (t, i)] for i in range(1, N_LIBRI23 + 1) if 'libro|%s|%d' % (t, i) in C]
    for s in ['M%d' % p for p in RIF_M] + list(RIF_E):
        lib[s] = [C['riflibro|%s|%d' % (s, i)] for i in range(1, N_RIF + 1) if 'riflibro|%s|%d' % (s, i) in C]
    giud, val = OrderedDict(), OrderedDict()
    for lab in ETICHETTE:
        rs = lib.get(lab) or []
        if not rs:
            continue
        v = OrderedDict()
        v['e231'], v['e266'] = mes([r['AUC_e231'] for r in rs]), mes([r['AUC_e266'] for r in rs])
        v['K'] = mes([aucK.get('%s:%d' % (lab, r['i'])) for r in rs])
        v['A'] = mes([r.get('AUC_A') for r in rs])
        g = OrderedDict(libri=len(rs), e231=v['e231'], e266=v['e266'], K=v['K'], A=v['A'])
        g['per_replica'] = OrderedDict((j, [mes([r[k] for r in rs if r['replica'] == rp]) for rp in (0, 1)]) for j, k in (('e231', 'AUC_e231'), ('e266', 'AUC_e266')))
        g['repliche_diverse'] = OrderedDict((j, bool(all(x[0] is not None and x[1] is not None for x in pr) and abs(pr[0][0] - pr[1][0]) > 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)))
                                            for j, pr in g['per_replica'].items())
        g['gruppi_e266'] = OrderedDict((n, statistics.mean(r['gruppi_e266'][n] for r in rs)) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)
        giud[lab] = g
        val[lab] = v
    R07 = OrderedDict(v21_A=[])
    C07 = {x['lavoro']: x for x in leggi_corse(I20.CORSE_IA07)}
    for k in CHIAVI_V21:
        r = C07.get('rifA|%d' % k)
        if r and r.get('AUC_A_b') is not None:
            R07['v21_A'].append(r['AUC_A_b'])
    v21 = OrderedDict(libri=len(CHIAVI_V21), e231=(I7.V21['AUC_e231'][0], I7.V21['AUC_e231'][1]), e266=(I7.V21['AUC_e266'][0], I7.V21['AUC_e266'][1]),
                      K=mes([aucK[n] for n in aucK if n.startswith('V21:')]), A=mes(R07['v21_A']))
    out['giudici'] = OrderedDict(tipi=giud, v21=v21)
    # ---- copia a memoria e ripetizioni
    rif_copia = I7.copia_riferimenti()
    nat = I7.quote(rif_copia['naturale'])
    rep_nat = MS.ripetizioni_interne(OrderedDict((p, [x['parole'] for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items()))
    k4 = 'righe uguali a una precedente nella pagina (>= 4 parole)'
    ks = 'righe uguali alla riga sopra (>= 2 parole)'
    kp = 'parole uguali alla parola prima'
    nat4 = rep_nat[k4][0] / rep_nat[k4][1] if rep_nat[k4][1] else 0.0
    natp = rep_nat[kp][0] / rep_nat[kp][1] if rep_nat[kp][1] else 0.0
    cop, rip, lett_copia = OrderedDict(), OrderedDict(), OrderedDict()
    for lab in ETICHETTE:
        rs = lib.get(lab) or []
        if not rs:
            continue
        qs = [I7.quote(r['copia']) for r in rs]
        cop[lab] = OrderedDict((k, mes([q[k] for q in qs])) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))
        rip[lab] = OrderedDict((k, mes([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else None for r in rs])) for k in rep_nat)
        m5, mr = cop[lab]['5-grammi'][0], cop[lab]['righe intere'][0]
        l5 = 'nessuna copia rilevante' if m5 is not None and m5 <= I20.COPIA_5GRAMMI[0] else 'copia' if m5 is not None and m5 > I20.COPIA_5GRAMMI[1] else 'zona grigia'
        lr = 'nessuna copia rilevante' if mr is not None and mr <= I20.COPIA_RIGHE[0] else 'copia' if mr is not None and mr > I20.COPIA_RIGHE[1] else 'zona grigia'
        r4, rsopra, rpp = rip[lab][k4][0], rip[lab][ks][0], rip[lab][kp][0]
        avvita = bool((r4 is not None and r4 > I20.AVVITA_MIN and r4 > I20.AVVITA_VOLTE * max(nat4, 1e-9)) or (rsopra is not None and rsopra > I20.RIGA_SOPRA_MAX))
        nuove, rn = cop[lab]['parole nuove'][0], nat['parole nuove']
        lett_copia[lab] = OrderedDict([('5-grammi', l5), ('righe', lr), ('copia', 'copia' in (l5, lr)), ('zona_grigia', 'zona grigia' in (l5, lr)), ('si_avvita', avvita),
                                       ('parola_prima_alta', bool(rpp is not None and natp and rpp > I20.PAROLA_PRIMA_VOLTE * natp)),
                                       ('parole_nuove_ok', bool(nuove is not None and rn and I20.NUOVE_FASCIA[0] * rn <= nuove <= I20.NUOVE_FASCIA[1] * rn))])
    modi = OrderedDict()
    for t in TIPI23:
        tot = Counter()
        for r in lib.get(t) or []:
            tot.update(r.get('modi_scrittura', {}))
        if tot:
            modi[t] = OrderedDict(tot)
    out['copia'] = OrderedDict(tipi=cop, naturale=nat, ripetizioni=rip, ripetizioni_naturali=OrderedDict((k, v[0] / v[1] if v[1] else None) for k, v in rep_nat.items()),
                               letture=lett_copia, modi_scrittura=modi)
    # ---- fase 0: profilo di distanza (vero con errore da ricampionamento delle pagine; libri con errore fra libri)
    f0 = OrderedDict()
    ctrl0 = OrderedDict()
    for nm in F0C_TESTI:
        r = C.get('F0c|%s' % nm)
        if r:
            s = PF.riassunto(r['profilo'])
            ctrl0[nm] = OrderedDict(piantato=r['piantato'], eccesso_tema=s['eccesso_tema'], eccesso_locale=s['eccesso_locale'], lettura_tema=PF.lettura(s['eccesso_tema']),
                                    lettura_locale=PF.lettura(s['eccesso_locale']), atteso=list(F0C_ATTESO[nm]),
                                    tema_cond=s['testo']['tema_cond'], locale=s['testo']['locale'])
    ok0 = bool(ctrl0) and all((x['lettura_tema'], x['lettura_locale']) == tuple(x['atteso']) for x in ctrl0.values()) and len(ctrl0) == len(F0C_TESTI)
    vero_f0 = None
    if 'F0|vere' in C:
        s = PF.riassunto(C['F0|vere']['profilo'])
        vero_f0 = OrderedDict(misure=s['testo'], nullo_righe=s['nullo_righe'], nullo_parole=s['nullo_parole'], eccesso_tema=s['eccesso_tema'], eccesso_locale=s['eccesso_locale'],
                              lettura_tema=PF.lettura(s['eccesso_tema']) if ok0 else 'lettura non valida (controllo della fase 0 fallito)',
                              lettura_locale=PF.lettura(s['eccesso_locale']) if ok0 else 'lettura non valida (controllo della fase 0 fallito)')
    f0['vero'] = vero_f0
    nomi_ins = OrderedDict([('V21', ['V21:%d' % k for k in CHIAVI_V21][:10])])
    for s in ['M%d' % p for p in RIF_M] + list(RIF_E0) + list(RIF_E):
        nomi_ins[s] = ['%s:%d' % (s, i) for i in range(1, N_RIF + 1)]
    for t in TIPI23:
        nomi_ins[t] = ['%s:%d' % (t, i) for i in range(1, N_LIBRI23 + 1)]
    ins = OrderedDict()
    for etich, nomi in nomi_ins.items():
        rs = [misure_f0_libro(C['F0|%s' % n]['profilo']) for n in nomi if 'F0|%s' % n in C]
        if rs:
            ins[etich] = OrderedDict((k, mes([x[k] for x in rs])) for k in rs[0])
            ins[etich]['libri'] = len(rs)
    f0['insiemi'] = ins
    vf = OrderedDict()
    if vero_f0:
        for k in list(vero_f0['misure']):
            if k != 'parole':
                vf[k] = vero_f0['misure'][k]
        vf['eccesso_tema'] = vero_f0['eccesso_tema']['differenza']
        vf['eccesso_locale'] = vero_f0['eccesso_locale']['differenza']
    f0['vero_valori'] = vf
    f0['al_vero'] = OrderedDict((etich, OrderedDict((k, I20.al_vero(x[k], vf.get(k))) for k in ('locale', 'lontana', 'tema_cond', 'quota_tema', 'eccesso_tema', 'eccesso_locale')
                                                      if k in x)) for etich, x in ins.items()) if vf else OrderedDict()
    f0['controlli'] = ctrl0
    f0['controlli_ok'] = ok0
    out['fase0'] = f0
    # ---- struttura
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
            s = etichetta(nome)
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
    out['vero'] = vero
    out['struttura'] = struttura
    # ---- letture: validita'
    letture = OrderedDict()
    letture['validita'] = OrderedDict(paper=ok_paper, K=ok_K, A=ok_A, sensibilita=OrderedDict((t, bool(o)) for t, o in sens_ok.items()), controllo_vede_la_differenza_sul_tema=vede,
                                      scambio_visto_nel_sintetico=OrderedDict((t, bool(sc.get(t, {}).get('eco_ok') and not sc.get(t, {}).get('legame_ok'))) for t in TIPI23),
                                      fase0=ok0)
    for lab in val:
        s = struttura.get(lab, {})
        for m_ in MISURE_STR:
            val[lab][m_] = s.get(m_, (None, None))
    # ---- L1 e L1b: eco, legame (e G9) al vero?
    L1 = OrderedDict()
    for lab in ETICHETTE:
        if lab not in val or not vero:
            continue
        fl = OrderedDict((m_, I20.al_vero(val[lab][m_], vero.get(m_))) for m_ in MISURE_ECO + MISURE_LEGAME + ['G9'])
        dist = OrderedDict((m_, (abs(val[lab][m_][0] - vero[m_]) / abs(vero[m_])) if val[lab][m_][0] is not None and vero.get(m_) else None) for m_ in MISURE_ECO + MISURE_LEGAME + ['G9'])
        quattro = bool(all(fl[m_] for m_ in MISURE_ECO + MISURE_LEGAME))
        L1[lab] = OrderedDict(al_vero=fl, distanza_relativa=dist, eco_al_vero=bool(all(fl[m_] for m_ in MISURE_ECO)), legame_al_vero=bool(all(fl[m_] for m_ in MISURE_LEGAME)),
                              tutti_al_vero=quattro, con_G9_al_vero=bool(quattro and fl['G9']), valori=OrderedDict((m_, val[lab][m_][0]) for m_ in MISURE_ECO + MISURE_LEGAME + ['G9']))
    letture['L1_eco_e_legame'] = OrderedDict(per_tipo=L1, esiste=[t for t in TIPI23 if t in L1 and L1[t]['tutti_al_vero']],
                                             esiste_con_G9=[t for t in TIPI23 if t in L1 and L1[t]['con_G9_al_vero']],
                                             vero=OrderedDict((m_, vero.get(m_)) for m_ in MISURE_ECO + MISURE_LEGAME + ['G9']))
    # ---- L2: ogni P contro l'E corrispondente di ia22 (bersagli: Λ e G9)
    L2 = OrderedDict()
    for t in TIPI23:
        rif = CORRISP[t]
        if t not in val or rif not in val or not vero:
            continue
        cl = OrderedDict()
        for m_ in MISURE_STR:
            cl[m_] = I20.classe_misura(val[rif][m_], val[t][m_], vero.get(m_))
        for j in GIUDICI:
            cl[j] = I20.classe_misura(val[rif][j], val[t][j], None)
        x = I20.lettura_ingrediente(0, cl, BERSAGLI_L2)
        x['classi'] = cl
        x['sensibilita'] = 'provata' if sens_ok.get(t) else 'NON provata (con riserva)'
        if not (ok_paper and ok_K):
            x['nota_giudici'] = 'giudici non validi: le colonne dei giudici non si leggono'
        L2['%s contro %s' % (t, rif)] = x
    letture['L2_contro_E'] = L2
    # ---- L3: contro il v21 (regola di ia16/ia20)
    L3 = OrderedDict()
    for lab in val:
        cl = I16.classe_giudici({j: val[lab][j] for j in ('e231', 'e266', 'K')}, v21)
        L3[lab] = OrderedDict(esito=I16.esito_v21(cl), giudici=cl, media_tre=statistics.mean(val[lab][j][0] for j in ('e231', 'e266', 'K') if val[lab][j][0] is not None)
                              if all(val[lab][j][0] is not None for j in ('e231', 'e266', 'K')) else None)
    if not (ok_paper and ok_K):
        for x in L3.values():
            x['esito'] = 'lettura non valida (controllo dei giudici fallito: ' + ', '.join(n for n, o in (('paper', ok_paper), ('K', ok_K)) if not o) + ')'
    else:
        for nm, x in L3.items():
            lc = lett_copia.get(nm)
            if lc and lc['copia']:
                x['esito'] += ' ma NON VALE: copia a memoria sopra la soglia'
            elif lc and (lc['zona_grigia'] or lc['si_avvita']):
                x['esito'] += ' (con riserva: copia in zona grigia o scrittura che si avvita)'
    mig = [(x['media_tre'], lab) for lab, x in L3.items() if x['media_tre'] is not None]
    letture['L3_contro_v21'] = OrderedDict(migliore=min(mig)[1] if mig else None, per_tipo=L3)
    letture['L4_profilo_di_distanza'] = f0
    out['valori'] = OrderedDict((lab, OrderedDict((k, x) for k, x in v.items())) for lab, v in val.items())
    out['letture'] = letture
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('addestra', 'sens', 'libro', 'riflibro', 'K', 'M', 'D', 'F0', 'F0c'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def scrivi_md(o):
    L = o['letture']
    md = ['# IA23 (ia23) — Eco da tutta la pagina, legame fra parole e vocabolario della pagina', '',
          'Preregistrazione: `preregistrazioni/ia23.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    c = o['controlli']
    md += ['## Controlli dei giudici', '']
    md.append('- Giudici del paper, positivo: AUC %s, soglia ≥ %s → %s. Negativo: giudice 1 %s, giudice 2 %s → %s.' % (
        nu(c['paper_positivo']['AUC']), nu(I20.POS_PAPER, 2), nu(c['paper_positivo']['riuscito']), nu(c['paper_negativo']['AUC_e231']), nu(c['paper_negativo']['AUC_e266']), nu(c['paper_negativo']['riuscito'])))
    if 'K_positivo' in c:
        md.append('- K, positivo: %s → %s. Negativo: %s → %s. K vede il v21 (AUC %s) → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['K_positivo']['AUC'].items()), nu(c['K_positivo']['riuscito']),
                                                                                              nu(c['K_negativo']['AUC']), nu(c['K_negativo']['riuscito']), nu(c['K_vede_v21']['AUC']), nu(c['K_vede_v21']['riuscito'])))
    md.append('- A (riportato, non decide), positivo: %s → %s. Negativo: %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['A_positivo']['AUC'].items()), nu(c['A_positivo']['riuscito']),
                                                                                   nu(c['A_negativo']['AUC']), nu(c['A_negativo']['riuscito'])))
    s = o['sensibilita']
    md += ['', '## Controlli di sensibilità (testi sintetici)', '']
    sc = s['tec']
    if sc.get('piantato'):
        p = sc['piantato']
        md.append('Testo con tema di pagina, eco locale e contatto piantati insieme (fogli tenuti fuori della piega 0): tasso di eco locale %s, quota del glifo iniziale preferito %s, contatto %s; '
                  'tasso lontano condizionato %s (con le righe rimescolate %s, eccesso di tema piantato %s).' % (nu(p['tasso_eco']), nu(p['quota_preferito']), nu(p['contatto']), nu(p['tema_cond']), nu(p['tema_cond_righe_rimescolate']), nu(p['eccesso_tema'])))
        md += ['', '| modello | guadagno su M1 (bit/segno) | eco locale scritta / piantata | tema scritto / piantato (eccesso) | glifo preferito scritto / piantato | contatto scritto / piantato | eco ok | tema ok | legame ok | riuscito |',
               '|---|---|---|---|---|---|---|---|---|---|']
        for m, x in sc.items():
            if m == 'piantato':
                continue
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (m, nu(x['guadagno_su_M1']), nu(x['eco_rapporto']), nu(x['tema_rapporto']), nu(x['contatto_rapporto_pref']), nu(x['contatto_rapporto']),
                                                                         nu(x['eco_ok']), nu(x['tema_ok']), nu(x['legame_ok']), nu(x['riuscito'])))
    md += ['', 'Il controllo vede la differenza sul tema (P2 impara il tema, E2 di ia22 no): %s.' % nu(s['vede_la_differenza_sul_tema'])]
    md += ['', 'Testo senza niente di piantato: ' + '; '.join('%s: guadagno su M1 %s, massa di copia %s → %s' % (m, nu(x['guadagno_su_M1']), nu(x['massa_media']), nu(x['riuscito'])) for m, x in s['senza'].items()) + '.']
    md += ['', '## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)', '', '| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa di copia | minuti per modello |', '|---|---|---|---|---|---|---|---|']
    for nm, x in o['bpc'].items():
        md.append('| %s | %d | %s | %s | %s | %d | %s | %.1f |' % (nm, x['parametri'], mf(x['validazione']), mf(x['fuori']), nu(x['epoche_scelte'], 1), x['al_massimo'], nu(x.get('massa_copia_media')), x['secondi_medi'] / 60))
    for nm, x in o['bpc_riferimenti'].items():
        md.append('| %s (cache) | — | %s | %s | — | — | — | — |' % (nm, mf(x['validazione']), mf(x['fuori'])))
    md += ['', 'Numeri imparati (medie): ' + '; '.join('%s %s' % (t, json.dumps(x, default=float)) for t, x in o['appresi'].items()) + '.']
    g = o['giudici']
    md += ['', '## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)', '', '| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |', '|---|---|---|---|---|---|']
    for nm, x in g['tipi'].items():
        md.append('| %s | %d | %s | %s | %s | %s |' % (nm, x['libri'], mf(x['e231']), mf(x['e266']), mf(x['K']), mf(x['A'])))
    md.append('| v21 | %d | %s (paper) | %s (paper) | %s | %s |' % (g['v21']['libri'], mf(g['v21']['e231']), mf(g['v21']['e266']), mf(g['v21']['K']), mf(g['v21']['A'])))
    md += ['', 'Repliche diverse (più di 2 errori): ' + '; '.join('%s: %s' % (nm, ', '.join('%s %s' % (j, nu(b)) for j, b in x['repliche_diverse'].items())) for nm, x in g['tipi'].items()) + '.']
    md += ['', '## Struttura (media ± errore standard sui libri)', '', '| testo | ' + ' | '.join(MISURE_STR.values()) + ' |', '|' + '---|' * (len(MISURE_STR) + 1)]
    v = o['vero']
    if v:
        md.append('| **vero** | ' + ' | '.join(nu(v.get(m_), 4) for m_ in MISURE_STR) + ' |')
        for nm in ETICHETTE + ['V21']:
            x = o['struttura'].get(nm)
            if x:
                md.append('| %s (%d libri) | ' % (nm, x['libri']) + ' | '.join(mf(x[m_], 4) for m_ in MISURE_STR) + ' |')
    md += ['', '## Letture preregistrate', '']
    va = L['validita']
    md.append('- Validità: giudici del paper %s, K %s, A %s; sensibilità: %s; il controllo vede la differenza sul tema: %s; controlli della fase 0: %s.' % (
        nu(va['paper']), nu(va['K']), nu(va['A']), ', '.join('%s %s' % (k, nu(b)) for k, b in va['sensibilita'].items()), nu(va['controllo_vede_la_differenza_sul_tema']), nu(va['fase0'])))
    md.append('- Scambio visto nel testo sintetico (eco imparata ma legame piantato perso): ' + (', '.join(k for k, b in va['scambio_visto_nel_sintetico'].items() if b) or 'nessun tipo') + '.')
    l1 = L['L1_eco_e_legame']
    md += ['', '### L1 e L1b: eco, legame e vocabolario della pagina "al vero"?', '', '**L1, imitatori con copia netta, Λ, contatto e D tutti al vero: %s.** **L1b, anche G9 al vero: %s.**' % (
        ', '.join(l1['esiste']) or 'nessuno', ', '.join(l1['esiste_con_G9']) or 'nessuno'), '',
           '| tipo | copia netta | Λ | contatto | D | G9 | eco al vero | legame al vero | L1 (4 misure) | L1b (+ G9) |', '|---|---|---|---|---|---|---|---|---|---|',
           '| vero | ' + ' | '.join(nu(l1['vero'][m_], 3) for m_ in MISURE_ECO + MISURE_LEGAME + ['G9']) + ' | | | | |']
    for t, x in l1['per_tipo'].items():
        md.append('| %s | ' % t + ' | '.join('%s%s' % (nu(x['valori'][m_], 3), ' ✓' if x['al_vero'][m_] else '') for m_ in MISURE_ECO + MISURE_LEGAME + ['G9']) + ' | %s | %s | %s | %s |' % (
            nu(x['eco_al_vero']), nu(x['legame_al_vero']), nu(x['tutti_al_vero']), nu(x['con_G9_al_vero'])))
    md += ['', '### L2: ogni P contro l\'E corrispondente di ia22 (bersagli: Λ e G9)', '', '| confronto | lettura | misure corrette | misure rotte | sensibilità |', '|---|---|---|---|---|']
    nomi_m = dict(MISURE_STR, **GIUDICI)
    for k, x in L['L2_contro_E'].items():
        md.append('| %s | **%s** | %s | %s | %s |' % (k, x['esito'], ', '.join(nomi_m[m_] for m_ in x['corrette']) or '—', ', '.join(nomi_m[m_] for m_ in x['rotte']) or '—', x['sensibilita']))
    l3 = L['L3_contro_v21']
    md += ['', '### L3: contro il v21', '', '- **Tipo migliore (AUC media di e231, e266, K): %s.**' % l3['migliore']]
    for nm, x in l3['per_tipo'].items():
        md.append('  - %s: %s (%s).' % (nm, x['esito'], '; '.join('%s %s (diff. %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items())))
    f4 = L['L4_profilo_di_distanza']
    md += ['', '### L4: profilo di distanza dell\'eco (descrittivo)', '']
    for nm, x in f4['controlli'].items():
        md.append('- Controllo %s (piantato %s): eccesso di tema %s ± %s → %s (atteso %s); eccesso locale %s ± %s → %s (atteso %s).' % (
            nm, json.dumps(x['piantato']), nu(x['eccesso_tema']['differenza']), nu(x['eccesso_tema']['errore']), x['lettura_tema'], x['atteso'][0],
            nu(x['eccesso_locale']['differenza']), nu(x['eccesso_locale']['errore']), x['lettura_locale'], x['atteso'][1]))
    vf0 = f4['vero']
    if vf0:
        md.append('- **Il vero:** eccesso di tema sul caso %s ± %s → **%s**; eccesso locale sul caso %s ± %s → **%s**.' % (
            nu(vf0['eccesso_tema']['differenza']), nu(vf0['eccesso_tema']['errore']), vf0['lettura_tema'], nu(vf0['eccesso_locale']['differenza']), nu(vf0['eccesso_locale']['errore']), vf0['lettura_locale']))
    cols = ['q_' + c for c in PF.CLASSI] + ['senza_ripresa'] + list(MISURE_F0)
    md += ['', '| testo | ' + ' | '.join(['distanza %s' % c for c in PF.CLASSI] + ['senza ripresa'] + list(MISURE_F0.values())) + ' |', '|' + '---|' * (len(cols) + 1)]
    if vf0:
        md.append('| **vero** | ' + ' | '.join(nu(f4['vero_valori'].get(k), 4) for k in cols) + ' |')
    for etich, x in f4['insiemi'].items():
        md.append('| %s (%d libri) | ' % (etich, x['libri']) + ' | '.join(mf(x.get(k), 4) for k in cols) + ' |')
    cp = o['copia']
    md += ['', '## Copia a memoria e ripetizioni (soglie severe di ia20)', '', '| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |', '|---|---|---|---|---|']
    for nm, q in cp['tipi'].items():
        md.append('| %s | %s |' % (nm, ' | '.join(mf(q[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    md.append('| naturale | %s |' % ' | '.join(nu(cp['naturale'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    for nm, x in cp['letture'].items():
        md.append('- %s: 5-grammi → %s, righe → %s; si avvita: %s; parola uguale alla prima alta: %s; parole nuove %s.' % (nm, x['5-grammi'], x['righe'], nu(x['si_avvita']), nu(x['parola_prima_alta']), 'nella fascia' if x['parole_nuove_ok'] else 'FUORI fascia'))
    if cp['modi_scrittura']:
        md.append('\nModi di scrittura delle parole (conti sui libri): ' + '; '.join('%s: %s' % (t, ', '.join('%s %d' % kv for kv in x.items())) for t, x in cp['modi_scrittura'].items()) + '.')
    md += ['', '## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def lavori_fase(fase):
    if fase == 'A':
        mancanti = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
        rif = []
        if RIF23 == 'ricalcola':
            rif = [('rifaddestra', p, k, r) for p in RIF_M for r in REPLICHE23 for k in range(PIEGHE)]
            rif += [('rifaddestraE', t, k, r) for t in list(RIF_E0) + list(RIF_E) for r in REPLICHE23 for k in range(PIEGHE)]
        # i piu' lenti per primi (P2, P3, P1), a pari tipo prima la replica 0
        ordine = [t for t in ('P2', 'P3', 'P1') if t in TIPI23]
        return mancanti + rif + [('addestra', t, k, r) for t in ordine for r in REPLICHE23 for k in range(PIEGHE)]
    if fase == 'Q':
        return [('sens', t, m) for t, ms in SENS_MODELLI.items() for m in ms if m[0] in 'ME' or m in TIPI23]
    if fase == 'C':
        rif = [('riflibro', 'M%d' % p, i) for p in RIF_M for i in range(1, N_RIF + 1)] + [('riflibro', s, i) for s in RIF_E for i in range(1, N_RIF + 1)]
        if RIF23 == 'ricalcola':
            rif += [('rifscrivi', s, i) for s in RIF_E0 for i in range(1, N_RIF + 1)]
        return rif + [('libro', t, i) for t in [x for x in ('P2', 'P3', 'P1') if x in TIPI23] for i in range(1, N_LIBRI23 + 1)]
    if fase == 'F':
        return [('F0c', n) for n in F0C_TESTI] + [('F0', 'vere')] + [('F0', n) for n in nomi_f0_riferimenti()]
    if fase == 'D':
        nomi = nomi_giudicati()
        return ([('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0), ('casoA', 0)] + [('ctrlA', n) for n in I7.NOMI_CTRL_A] + [('K', f) for f in range(PIEGHE)] +
                [('D', f) for f in range(PIEGHE)] + [('M', 'vere')] + [('M', n) for n in nomi_struttura(nomi)] + [('F0', n) for n in nomi if e_nuovo(n)])
    return []


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__), ('pagina', PM.VERSIONE), ('echi', EM.VERSIONE), ('gradini', GM.VERSIONE)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD23, LIBRI23, MISURE23):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni, riga massima %d; tipi %s; PICCOLO %s; riferimenti %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), voc['lmax'], TIPI23, PICCOLO, RIF23), flush=True)
    percorso = os.path.join(USCITA, 'ia23_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AQCFDS')
    for fase in 'AQCFD':
        if fase in fasi:
            lavori = lavori_fase(fase)
            if fase == 'A' and 'Q' in fasi:        # i controlli di sensibilita' girano insieme ai modelli (stesso gruppo di processi)
                lavori = lavori_fase('Q') + lavori
            if fase == 'Q' and 'A' in fasi:
                continue
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        l1 = o['letture']['L1_eco_e_legame']
        print('L1: eco e legame tutti al vero: %s; con G9: %s' % (', '.join(l1['esiste']) or 'nessuno', ', '.join(l1['esiste_con_G9']) or 'nessuno'), flush=True)


if __name__ == '__main__':
    main()
