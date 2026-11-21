# -*- coding: utf-8 -*-
"""Esperimento IA20 (ia20): l'imitatore a gradini.

Domanda (Davide, 21/11/2026): "vorrei che addestrassimo un'IA a rifarlo, cosi' capiamo cosa non riusciamo a fare". Una scala di cinque modelli,
fissata prima, in cui ogni gradino aggiunge UN ingrediente al precedente; tutti giudicati allo stesso modo, per vedere quale ingrediente corregge
quale difetto e che cosa resta irriproducibile.
    M1 GRU 2 x 256 (come ia07)        M2 = M1 + memoria locale (attenzione sulla riga in corso e su quella sopra)
    M3 = M2 + vocabolario della pagina  M4 = M3 + posizione nella riga     M5 = M4 + copia e ritocco (puntatore)
Preregistrazione: preregistrazioni/ia20.md. I modelli stanno in gradini_modelli.py. Importa, senza modificarli, ia07 (disposizione, pieghe per foglio,
giudici del paper, giudice A, copia a memoria), ia16 (pagine, letture), imitatore_misure (giudice K, copia netta e Λ di ia09, D di ia10, contatto di ia08),
aprire_parole (firma dei bordi della riga di ia17) e rifarlo_ritocchi (forma delle parole nuove di ia08/ia11).

Che cosa fa il codice (in parole semplici)
- Fase A: 50 addestramenti (5 gradini x 5 pieghe per foglio x 2 repliche) + eventuali modelli del giudice A mancanti.
- Fase Q: controlli di sensibilita' (solo testi sintetici con un ingrediente piantato): ogni ingrediente deve saper imparare cio' per cui e' fatto.
- Fase C: libri onesti (N_LIBRI20 per gradino, meta' per replica) con i giudici del paper, il giudice A (riportato), la copia a memoria e le ripetizioni.
- Fase V (facoltativa): modello "tutto" del gradino scelto e libro vetrina, solo in dati/cache/ia20/vetrina.
- Fase D: controlli dei giudici, giudice K, misure di struttura (copia netta, Λ, contatto, D, G9, bordi, parole nuove e forma).
- Fase S: sintesi e letture preregistrate ("ingrediente -> misure corrette / rotte").
Uscite (solo numeri e aggregati): risultati/ia20_imitatore_gradini.json e .md, risultati/ia20_corse.jsonl (una riga per lavoro; con RIPRENDI=1 i fatti non si
rifanno). Modelli, libri, profili e vetrina in dati/cache/ia20 (CACHE20, protetti: non si committano).

    nohup bash strumenti/coda.sh ia20 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=10:ia20" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 USCITA=<cartella fuori dal repo> python esperimenti/ia20_imitatore_gradini.py     (prova sul libro latino)

Variabili (oltre a quelle di ia07, che si importano: SOLO_CONTROLLI, USCITA, PASSI_A, OGNI_A, PAZIENZA_A, NASCOSTO_A, CADUTA_A, ...): PROCESSI (non cambia i
risultati), RIPRENDI, FASI (lettere A Q C V D S; predefinito AQCDS), FILTRO (sottostringhe, separate da |, che il nome del lavoro deve contenere).
Nuove: CACHE20, PASSI20 (12345, senza virgole), EPOCHE20 (150), PAZIENZA20 (10), N_LIBRI20 (10), PICCOLO20 (solo prove), EPOCHE_SENS20 (60), PASSO_VETRINA20 (solo fase V),
CORSE_IA07, LIBRI_IA07, MODELLI_IA07, MODELLI_A20. I valori predefiniti sono quelli preregistrati.
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
import gradini_modelli as GM  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NOME = 'ia20_imitatore_gradini'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE20 = os.environ.get('CACHE20', os.path.join(USCITA, 'ia20_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia20'))
MOD20, LIBRI20, MISURE20 = os.path.join(CACHE20, 'modelli'), os.path.join(CACHE20, 'libri'), os.path.join(CACHE20, 'misure')
VETRINA20 = os.path.join(CACHE20, 'vetrina')
PICCOLO = os.environ.get('PICCOLO20') == '1'
PASSI20 = tuple(int(x) for x in os.environ.get('PASSI20', '12345') if x.isdigit())     # senza virgole (la coda divide le impostazioni sulle virgole): 12345 oppure 45
REPLICHE20 = (0, 1)
EPOCHE20 = int(os.environ.get('EPOCHE20', 150))
PAZIENZA20 = int(os.environ.get('PAZIENZA20', 10))
N_LIBRI20 = int(os.environ.get('N_LIBRI20', 10))             # libri per gradino (meta' dalla replica 0, meta' dalla 1)
EPOCHE_SENS20 = int(os.environ.get('EPOCHE_SENS20', 60))
PAZIENZA_SENS20 = 10
CORSE_IA07 = os.environ.get('CORSE_IA07', os.path.join(USCITA, 'ia07_corse.jsonl'))
LIBRI_IA07 = os.environ.get('LIBRI_IA07', I7.LIBRI if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia07_libri'))
MODELLI_IA07 = os.environ.get('MODELLI_IA07', I7.MODELLI if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia07_modelli'))
if os.environ.get('MODELLI_A20'):
    I7.MODELLI_A = os.environ['MODELLI_A20']
BOOT = int(os.environ.get('BOOT', 1000))
PIEGHE = I7.PIEGHE
CHIAVI_V21 = I7.CHIAVI_V21[:4] if PICCOLO else I7.CHIAVI_V21
N_IA07 = 4 if PICCOLO else 20
# L'ia16 legge lo stesso ambiente: in prova i suoi libri di riferimento (I07, V21) sono quelli di PICCOLO16; qui si allineano
I16.CHIAVI_V21, I16.N_IA07, I16.LIBRI_IA07 = CHIAVI_V21, N_IA07, LIBRI_IA07

# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
POS_PAPER, NEG_BANDA = I16.POS_PAPER, I16.NEG_BANDA          # 0,95; 0,45-0,55
POS_K, K_VEDE_V21 = I16.POS_K, I16.K_VEDE_V21                # 0,85; 0,65
SOGLIA_ERRORI = 2.0                                          # differenze lette a due errori
VERO_TOL = 0.05                                              # "al vero": entro 2 errori o entro il 5% del valore vero
COPIA_5GRAMMI = (0.001, 0.003)                               # SEVERA (ia16: 0,002 / 0,01): nessuna copia / zona grigia / copia
COPIA_RIGHE = (0.0005, 0.002)                                # SEVERA (ia16: 0,001 / 0,005)
AVVITA_VOLTE, AVVITA_MIN = 3.0, 0.01                         # righe ripetute nella pagina: oltre 3 volte il naturale e oltre 1% (ia16: 2%)
RIGA_SOPRA_MAX = 0.01                                        # righe uguali alla riga sopra (>= 2 parole) oltre l'1%: "si avvita"
PAROLA_PRIMA_VOLTE = 2.0                                     # parole uguali alla parola prima: oltre 2 volte il naturale -> segnalato
NUOVE_FASCIA = (0.6, 1.4)
# controlli di sensibilita': fissati dopo la prova su testi non Voynich (vedi la preregistrazione, sezione "Prova del codice")
SENS = OrderedDict([('eco_M5_contro_M1', 0.10),         # M5 sul testo con eco piantata: validazione almeno cosi' sotto M1 (bit per segno)
                    ('eco_post_copiabili', 0.50),       # quota a posteriori della strada "copia" sulle parole copiabili, almeno
                    ('tema_M3_contro_M2', 0.03),        # M3 sul testo con tema di pagina piantato, sotto M2 di almeno
                    ('bordi_M4_contro_M3', -0.02),      # M4 sul testo con parole di bordo piantate: NON peggio di M3 di piu' di cosi' (la GRU sa gia' contare: il guadagno atteso e' ~0)
                    ('senza_M5_contro_M1', 0.02),       # sul testo senza niente di piantato: M5 non scende sotto M1 di piu' di cosi' (il puntatore non inventa guadagni)
                    ('senza_massa_max', 0.10)])         # e massa di copia media del puntatore di M5 al massimo cosi'
SENS_TESTI = OrderedDict([('eco', dict(eco=0.5, ritocco=0.6)), ('tema', dict(tema=0.6)), ('bordi', dict(bordi=0.9)), ('senza', dict())])
SENS_MODELLI = OrderedDict([('eco', (1, 2, 5)), ('tema', (2, 3)), ('bordi', (3, 4)), ('senza', (1, 5))])
# bersaglio di ogni ingrediente (le altre misure si guardano comunque: "rompe" se peggiorano)
BERSAGLI = OrderedDict([(2, ['copia_netta', 'lam']), (3, ['G9']), (4, ['bordi_inizio', 'bordi_fine']), (5, ['copia_netta', 'lam'])])
INGREDIENTI = OrderedDict([(2, 'memoria locale (attenzione sulla riga in corso e su quella sopra)'), (3, 'vocabolario della pagina'),
                           (4, 'posizione nella riga'), (5, 'copia e ritocco (puntatore)')])
MISURE_STR = OrderedDict([('copia_netta', 'copia netta (bit per parola)'), ('lam', 'quota locale Λ'), ('contatto', 'contatto ultimo→primo glifo'),
                          ('D', 'ordine delle famiglie D'), ('G9', 'G9 vocabolario della pagina'), ('bordi_inizio', 'bordi: inizio riga'),
                          ('bordi_fine', 'bordi: fine riga'), ('parole_nuove', 'quota di parole nuove'), ('costo_forma', 'costo di forma delle parole nuove (bit per glifo)')])
GIUDICI = OrderedDict([('e231', 'giudice 1 (e231)'), ('e266', 'giudice 2 (e266)'), ('K', 'giudice K')])

_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def seme_str(*a):
    return MS.seme_str(*a)


def nome_passo(p):
    return GM.NOME_PASSO[p]


# ---------------------------------------------------------------- pagine e modelli

def pagine_fold(piega, passo, dp=None, tag='reale'):
    """(ctx, add, val, fuori): le pagine del modello della piega (fogli di addestramento, validazione, tenuti fuori di ia07) preparate per `passo`;
    `ctx` ha le K parole piu' frequenti dell'addestramento. `dp`: pagine (ia16.dati_pagine) o di un testo sintetico."""
    k = (tag, piega, passo >= 5, PICCOLO)
    if k in _C:
        return _C[k]
    voc = I7.vocabolario()
    dp = dp or I16.dati_pagine()
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    sel = lambda ff: [d for d in dp.values() if d['foglio'] in set(ff)]
    K, S = (40, 12) if PICCOLO else (GM.K_TIPI, GM.S_CAND)
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(sel(f_add), GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    out = (ctx,) + tuple([GM.prepara_pagina(d, ctx, passo >= 5) for d in sel(ff)] for ff in (f_add, f_val, f_fuori))
    _C[k] = out
    return out


def seme_modello(passo, piega, replica):
    return 20000 + 1000 * passo + 100 * replica + piega


def percorso_modello(passo, piega, replica, est):
    return os.path.join(MOD20, 'ia20_%s_%s_%d%s' % (nome_passo(passo), piega, replica, est))


def addestra(passo, piega, replica):
    inizio = time.time()
    voc = I7.vocabolario()
    ctx, add, val, fuori = pagine_fold(piega, passo)
    cfg = GM.cfg_completa(passo, voc, ctx, PICCOLO)
    nome = '%s p%s r%d' % (nome_passo(passo), piega, replica)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, seme_modello(passo, piega, replica), EPOCHE20, PAZIENZA20, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'addestra|%d|%s|%d' % (passo, piega, replica)), ('passo', passo), ('piega', piega), ('replica', replica),
                       ('parametri', sum(p.numel() for p in m.parameters())), ('pagine', [len(add), len(val), len(fuori)]),
                       ('epoche', len(ca)), ('epoca_scelta', scelta), ('arrivata_al_massimo', len(ca) >= EPOCHE20 and scelta > EPOCHE20 - PAZIENZA20),
                       ('curva_validazione', cv), ('curva_addestramento', ca),
                       ('bpc_addestramento', round(GM.bpc_pagine(m, ctx, add), 5)), ('bpc_validazione', round(GM.bpc_pagine(m, ctx, val), 5)),
                       ('bpc_fuori', round(GM.bpc_pagine(m, ctx, fuori), 5))])
    ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    ris['secondi'] = round(time.time() - inizio, 1)
    GM.salva_modello(m, percorso_modello(passo, piega, replica, '.pt'), voc['segni'], ctx, dict(passo=passo, piega=piega, replica=replica, epoca_scelta=scelta, solo_prova=bool(SOLO_CONTROLLI)))
    json.dump(ris, open(percorso_modello(passo, piega, replica, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def carica(passo, piega, replica):
    k = ('modello', passo, piega, replica)
    if k not in _C:
        _C[k] = GM.carica_modello(percorso_modello(passo, piega, replica, '.pt'), I7.vocabolario())
    return _C[k]


# ---------------------------------------------------------------- controlli di sensibilita' (testi sintetici)

def pagine_sintetiche(righe_s):
    voc, D = I7.vocabolario(), I7.divisore()
    pp = I7.per_pagina(righe_s)
    T = {voc['idx']['T:' + t] for t in 'PMUS'}
    out = OrderedDict()
    for p in pp:
        s = np.array(I7.sequenza(pp[p], voc, D), dtype=np.int64)
        out[p] = dict(nome=p, foglio=I7.foglio_di(p), tok=s, cond=s[1:4].copy(), linea=I16.linee_di(s, T))
    return out


def lavoro_sens(testo, passo):
    """Un gradino addestrato su un testo sintetico con UN ingrediente piantato (piega 0): validazione e, per M5, la massa di copia del puntatore."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    sint = GM.sintetico(I7.libro_vero(), seme_str('ia20sint', testo), D, voc['unita'], **SENS_TESTI[testo])
    dps = pagine_sintetiche(sint)
    ctx, add, val, fuori = pagine_fold(0, passo, dps, tag='sint:' + testo)
    cfg = GM.cfg_completa(passo, voc, ctx, PICCOLO)
    nome = 'sens %s %s' % (testo, nome_passo(passo))

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, 30000 + 10 * passo + list(SENS_TESTI).index(testo), EPOCHE_SENS20, PAZIENZA_SENS20, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'sens|%s|%d' % (testo, passo)), ('testo', testo), ('passo', passo), ('epoche', len(ca)), ('epoca_scelta', scelta),
                       ('bpc_validazione', round(GM.bpc_pagine(m, ctx, val), 5)), ('bpc_fuori', round(GM.bpc_pagine(m, ctx, fuori), 5)),
                       ('curva_validazione', cv)])
    if passo >= 5:
        ris['puntatore'] = GM.massa_copia(m, ctx, fuori)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- scrivere un libro

class RegoleScrittura(I7.Penna):
    """Solo le regole di scrittura di ia07 (`ammessi`): niente spazio o fine riga a inizio riga o dopo uno spazio, riga massima, niente segno che
    ridivide la parola."""

    def __init__(self, voc):
        super().__init__(None, voc)


def campiona(pr, rng):
    return I16.campiona(pr, rng)


def scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta):
    """Scrive una pagina con la disposizione `rp`. M1-M4: segno per segno. M5: a inizio parola sceglie fra libero e candidato (e tipo di ritocco)."""
    passo = m.passo
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    pen.apri()
    lg = None
    for t in I7.testa_pagina(rp, voc):
        lg = pen.dai(t)
    if passo >= 5:
        psub, pins = pen.tabelle_ritocco()
    out = []
    for j, x in enumerate(rp):
        for t in I7.testa_riga(x, j, voc, D):
            lg = pen.dai(t)
        parole, lung, prima, fine = [], 0, 'inizio', False
        while not fine:
            w2 = None
            if passo >= 5:
                cand = pen.candidati()
                if cand:
                    pf, ppi = pen.puntatore(cand)
                    pr = np.concatenate([[pf], ppi[:len(cand)].reshape(-1)])
                    pr = pr / pr.sum()
                    for _ in range(8):
                        idx = int(rng.choice(len(pr), p=pr))
                        if idx == 0:
                            break
                        k, tipo = divmod(idx - 1, GM.NTIPI)
                        w2 = GM.campiona_ritocco(cand[k][0], tipo, psub, pins, rng)
                        if w2 is not None:
                            stringhe = [unita[u] for u in w2]
                            if D(''.join(stringhe)) == stringhe:
                                conta[('uguale', 'cambia', 'aggiunge', 'toglie')[tipo]] += 1
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
                s = ammessi[campiona(z / z.sum(), rng)]
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
                s = amm[campiona(z / z.sum(), rng)]
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


def scrivi_libro(passo, replica, seme, pagine=None):
    """Il libro intero (o le pagine `pagine`), pagina per pagina: ogni pagina e' scritta dal modello della piega che non ha visto il suo foglio.
    -> (lista (pagina, inizio, parole), conti dei modi di scrittura)."""
    righe, voc, D = I7.libro_vero(), I7.vocabolario(), I7.divisore()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    pg = I7.pieghe()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())
    regole = RegoleScrittura(voc)
    penne = {}
    conta = Counter()
    out = []
    for pag, rp in pp.items():
        if pagine is not None and pag not in pagine:
            continue
        k = pg[I7.foglio_di(pag)]
        if k not in penne:
            m, ctx = carica(passo, k, replica)
            penne[k] = (m, ctx, GM.Penna20(m, ctx, cap + 8))
        m, ctx, pen = penne[k]
        out += scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta)
    return out, conta


def percorso_libro(passo, i):
    return os.path.join(LIBRI20, 'ia20_libro_%s_%d.txt' % (nome_passo(passo), i))


def lavoro_libro(passo, i):
    inizio = time.time()
    replica = I7.replica_del_libro(i, N_LIBRI20)
    seme = 2000000 + 10000 * passo + i
    os.makedirs(LIBRI20, exist_ok=True)
    percorso = percorso_libro(passo, i)
    conta = None
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t, conta = scrivi_libro(passo, replica, seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia20, libro %s %d' % (nome_passo(passo), i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%d|%d' % (passo, i)), ('passo', passo), ('i', i), ('replica', replica), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    if conta is not None and passo >= 5:
        ris['modi_scrittura'] = OrderedDict(conta)
    ris.update(I7.giudica(t, os.path.join(LIBRI20, 'ia20_tabella_%s_%d.npz' % (nome_passo(passo), i))))
    try:
        ris.update(I7.giudice_A(I7.libro_A_da_righe(t)))
    except Exception as e:                                                # noqa: BLE001
        ris['A_errore'] = repr(e)
    ris['copia'] = I7.copia_onesta(t)
    ris['ripetizioni'] = MS.ripetizioni_interne({p: [ps for _, ps in rr] for p, rr in I16._raggruppa(t).items()})
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_vetrina(passo):
    """Modello "tutto" del gradino scelto (numero di epoche mediano dei 10 modelli delle pieghe) e libro vetrina. Testo e immagini restano in
    dati/cache/ia20/vetrina, mai in risultati; in risultati solo il controllo di copia (conti e nomi di pagina)."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    ep = [json.load(open(percorso_modello(passo, k, r, '.json'), encoding='utf-8'))['epoca_scelta'] for k in range(PIEGHE) for r in REPLICHE20
          if os.path.exists(percorso_modello(passo, k, r, '.json'))]
    fisse = int(statistics.median(ep))
    dp = I16.dati_pagine()
    K, S = (40, 12) if PICCOLO else (GM.K_TIPI, GM.S_CAND)
    tutte = list(dp.values())
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(tutte, GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    add = [GM.prepara_pagina(d, ctx, passo >= 5) for d in tutte]
    cfg = GM.cfg_completa(passo, voc, ctx, PICCOLO)
    m, _, ca, _ = GM.addestra_modello(cfg, ctx, add, [], 20099 + passo, EPOCHE20, PAZIENZA20, epoche_fisse=fisse)
    os.makedirs(VETRINA20, exist_ok=True)
    GM.salva_modello(m, os.path.join(VETRINA20, 'ia20_%s_tutto.pt' % nome_passo(passo)), voc['segni'], ctx, dict(passo=passo, epoche=fisse))
    righe, regole = I7.libro_vero(), RegoleScrittura(voc)
    rng = np.random.default_rng(2000000 + 99)
    pen = GM.Penna20(m, ctx, max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in I7.per_pagina(righe).values()) + 8)
    t, conta = [], Counter()
    for pag, rp in I7.per_pagina(righe).items():
        t += scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta)
    percorso = os.path.join(VETRINA20, 'ia20_libro_vetrina_%s.txt' % nome_passo(passo))
    I7.scrivi_file(t, percorso, 'ia20, libro vetrina %s' % nome_passo(passo), None)
    ris = OrderedDict([('lavoro', 'vetrina|%d' % passo), ('passo', passo), ('epoche', fisse)])
    ris['copia'] = I7.conti_copia([ps for _, _, ps in t], [x['parole'] for x in righe])
    ris['controllo_copia'] = I7.controllo_copia_vetrina(t)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- catalogo dei libri da misurare

def libro_esiste(passo, i):
    return os.path.exists(percorso_libro(passo, i))


def nomi_libri():
    """Nomi dei libri: M<p>:i (gradini), I07:i (ia07), V21:k (v21 senza messaggio di ia01), ctrl:* (controlli)."""
    nomi = []
    for p in PASSI20:
        nomi += ['M%d:%d' % (p, i) for i in range(1, N_LIBRI20 + 1) if libro_esiste(p, i)]
    nomi += ['I07:%d' % i for i in range(1, N_IA07 + 1) if SOLO_CONTROLLI or os.path.exists(os.path.join(LIBRI_IA07, 'ia07_libro_senza_%d.txt' % i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    """Per le misure di struttura: tutti i libri dei gradini; I07 (meta' per replica, 10 libri) e V21 (10)."""
    out = [x for x in nomi if x.startswith('M') and x[1].isdigit()]
    ia = [x for x in nomi if x.startswith('I07:')]
    k = 5
    out += [x for x in ia if int(x.split(':')[1]) <= k or N_IA07 // 2 < int(x.split(':')[1]) <= N_IA07 // 2 + k]
    out += [x for x in nomi if x.startswith('V21:')][:10]
    return out


def e_gradino(nome):
    return nome[0] == 'M' and nome[1].isdigit()


def t_di(nome):
    if e_gradino(nome):
        return I7.leggi_file(percorso_libro(int(nome[1]), int(nome.split(':')[1])))
    return I16.t_di(nome)


def rows_di(nome):
    if e_gradino(nome):
        return I7.libro_A_da_righe(t_di(nome))
    return I16.rows_di(nome)


# ---------------------------------------------------------------- lavori di misura (fase D)

def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_libri():
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE20, exist_ok=True)
    with open(os.path.join(MISURE20, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def somma_conti(lista):
    tot = {g: {f: Counter() for f in ('primo', 'ultimo', 'lung')} for g in ('prima', 'ultima', 'interna')}
    for c in lista:
        for g in tot:
            for f in tot[g]:
                tot[g][f].update(c[g][f])
    return tot


def lavoro_M(nome):
    """Copia netta e Λ (ia09), contatto (ia08), G9 del giudice 2 e firma dei bordi della riga (ia17) per un libro o per `vere`."""
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
    ris['bordi'] = AP.firma_da_conti(somma_conti(list(cp.values())))
    if nome == 'vere':
        rng = np.random.default_rng(200020)
        ps = list(cp)
        bs = [AP.firma_da_conti(somma_conti([cp[ps[i]] for i in rng.integers(0, len(ps), len(ps))])) for _ in range(200)]
        ris['bordi_ic'] = OrderedDict((kk, [float(np.nanpercentile([b[kk] for b in bs if b[kk] is not None], q)) for q in (2.5, 97.5)]) for kk in ris['bordi'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    """D di ia10 per piega e, per ogni testo, forma delle parole nuove (ia08/ia11): bit totali, glifi, parole nuove, parole totali, con forma e parole
    note delle pagine vere delle altre pieghe."""
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
        if tipo == 'addestra':
            return addestra(int(args[1]), args[2], int(args[3]))
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
        if tipo == 'sens':
            return lavoro_sens(args[1], int(args[2]))
        if tipo == 'libro':
            return lavoro_libro(int(args[1]), int(args[2]))
        if tipo == 'vetrina':
            return lavoro_vetrina(int(args[1]))
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
                breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'bpc_fuori', 'AUC_e231', 'AUC_e266', 'AUC_A', 'AUC', 'G9') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


# ---------------------------------------------------------------- analisi e letture

def mes(xs):
    return MS.media_es(xs)


def classe_misura(prec, succ, vero, soglia=SOGLIA_ERRORI):
    """prec, succ: (media, errore) di un gradino e del successivo; vero: valore del libro vero o None (giudici: piu' basso = meglio).
    'avvicina' / 'peggiora' / 'invariata' a due errori. Per le misure con vero la distanza e' |valore - vero|; per i giudici l'AUC."""
    if prec[0] is None or succ[0] is None:
        return 'non calcolabile'
    e = math.sqrt((prec[1] or 0.0) ** 2 + (succ[1] or 0.0) ** 2)
    dp = abs(prec[0] - vero) if vero is not None else prec[0]
    ds = abs(succ[0] - vero) if vero is not None else succ[0]
    return 'avvicina' if dp - ds > soglia * e else 'peggiora' if ds - dp > soglia * e else 'invariata'


def al_vero(x, vero):
    """Un valore (media, errore) sta 'al vero' se dista dal vero meno di due errori o meno del 5% del valore vero."""
    if x[0] is None or vero is None:
        return None
    return bool(abs(x[0] - vero) <= max(SOGLIA_ERRORI * (x[1] or 0.0), VERO_TOL * abs(vero)))


def lettura_ingrediente(passo, cl, bersagli):
    """cl: misura -> classe (gradino `passo` contro il precedente). 'corregge' se almeno un bersaglio si avvicina e niente peggiora; 'corregge ma rompe'
    se qualcosa peggiora; 'rompe' se nessun bersaglio si avvicina e qualcosa peggiora; altrimenti 'nessun effetto'."""
    av = [m for m, c in cl.items() if c == 'avvicina']
    pe = [m for m, c in cl.items() if c == 'peggiora']
    bers = [m for m in bersagli if cl.get(m) == 'avvicina']
    esito = ('corregge' if bers and not pe else 'corregge ma rompe' if bers and pe else 'rompe' if pe else 'nessun effetto')
    return OrderedDict(esito=esito, bersagli=bersagli, bersagli_corretti=bers, corrette=av, rotte=pe)


def leggi_corse(percorso):
    return I16.leggi_corse(percorso)


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    c_ctx = I7.contesto_A()
    n_pag = len(c_ctx['ids'])
    out = OrderedDict(esperimento='ia20', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=errori, passi=list(PASSI20))
    # ---- modelli
    modelli = [C[k] for k in sorted(C) if k.startswith('addestra|')]
    out['modelli'] = [OrderedDict((k, v) for k, v in m.items() if k not in ('curva_validazione', 'curva_addestramento')) for m in modelli]
    bpc = OrderedDict()
    for p in PASSI20:
        ms = [m for m in modelli if m['passo'] == p]
        if ms:
            bpc[nome_passo(p)] = OrderedDict(modelli=len(ms), parametri=ms[0]['parametri'], validazione=mes([x['bpc_validazione'] for x in ms]), fuori=mes([x['bpc_fuori'] for x in ms]),
                                             epoche_scelte=mes([x['epoca_scelta'] for x in ms])[0], al_massimo=sum(bool(x['arrivata_al_massimo']) for x in ms),
                                             secondi_medi=statistics.mean(x['secondi'] for x in ms))
    out['bpc'] = bpc
    C07 = {x['lavoro']: x for x in leggi_corse(CORSE_IA07)}
    R07 = I16.ref_ia07(C07)
    out['modelli_ia07'] = OrderedDict(('%d_%d' % kk, v) for kk, v in R07['bpc'].items())
    # ---- controlli dei giudici
    ctr = OrderedDict()
    pos = [C['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in C]
    caso = C.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=mes(pos)[0], soglia=POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=NEG_BANDA,
                                        riuscito=bool(caso) and all(NEG_BANDA[0] <= caso[k] <= NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    pa = OrderedDict((n, C['ctrlA|%s' % n].get('AUC_A') if 'ctrlA|%s' % n in C else None) for n in I7.NOMI_CTRL_A if n != 'righe')
    na = C['casoA|0']['AUC_A'] if 'casoA|0' in C else None
    ctr['A_positivo'] = OrderedDict(AUC=pa, soglia=I7.SOGLIA_POSITIVO_A, riuscito=pa.get('parole') is not None and all(v >= I7.SOGLIA_POSITIVO_A for v in pa.values() if v is not None))
    ctr['A_negativo'] = OrderedDict(AUC=na, banda=NEG_BANDA, riuscito=na is not None and NEG_BANDA[0] <= na <= NEG_BANDA[1])
    profs = []
    for f in range(PIEGHE):
        p = os.path.join(MISURE20, 'K_f%d.pkl' % f)
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
    ok_A = ctr['A_positivo']['riuscito'] and ctr['A_negativo']['riuscito']
    out['controlli'] = ctr
    # ---- controlli di sensibilita' degli ingredienti
    sens = OrderedDict()
    sv = lambda t, p: C.get('sens|%s|%d' % (t, p))
    def _bpc(t, p):
        r = sv(t, p)
        return r['bpc_validazione'] if r else None
    def _gap(a, b):
        return None if a is None or b is None else a - b
    s_eco, s_tema, s_bordi, s_sen = _gap(_bpc('eco', 1), _bpc('eco', 5)), _gap(_bpc('tema', 2), _bpc('tema', 3)), _gap(_bpc('bordi', 3), _bpc('bordi', 4)), _gap(_bpc('senza', 1), _bpc('senza', 5))
    punt_eco = (sv('eco', 5) or {}).get('puntatore')
    punt_sen = (sv('senza', 5) or {}).get('puntatore')
    sens['M2_memoria_locale'] = OrderedDict(guadagno_su_M1=_gap(_bpc('eco', 1), _bpc('eco', 2)), nota='descrittivo: l\'attenzione puo\' imparare da sola la copia dalla riga sopra')
    sens['M3_vocabolario_pagina'] = OrderedDict(guadagno_su_M2=s_tema, soglia=SENS['tema_M3_contro_M2'], riuscito=s_tema is not None and s_tema >= SENS['tema_M3_contro_M2'])
    sens['M4_posizione_riga'] = OrderedDict(guadagno_su_M3=s_bordi, soglia=SENS['bordi_M4_contro_M3'], riuscito=s_bordi is not None and s_bordi >= SENS['bordi_M4_contro_M3'])
    sens['M5_puntatore'] = OrderedDict(guadagno_su_M1=s_eco, guadagno_su_M2=_gap(_bpc('eco', 2), _bpc('eco', 5)), soglia_guadagno=SENS['eco_M5_contro_M1'],
                                       posteriori_copiabili=punt_eco and punt_eco['posteriori_copiabili'], soglia_posteriori=SENS['eco_post_copiabili'],
                                       riuscito=bool(s_eco is not None and s_eco >= SENS['eco_M5_contro_M1'] and punt_eco and punt_eco['posteriori_copiabili'] is not None
                                                     and punt_eco['posteriori_copiabili'] >= SENS['eco_post_copiabili']))
    sens['M5_negativo'] = OrderedDict(differenza_M1_M5=s_sen, massa_media=punt_sen and punt_sen['massa_media'], soglie=[SENS['senza_M5_contro_M1'], SENS['senza_massa_max']],
                                      riuscito=bool(s_sen is not None and s_sen <= SENS['senza_M5_contro_M1'] and punt_sen and punt_sen['massa_media'] is not None
                                                    and punt_sen['massa_media'] <= SENS['senza_massa_max']))
    out['sensibilita'] = sens
    sens_ok = {2: True, 3: sens['M3_vocabolario_pagina']['riuscito'], 4: sens['M4_posizione_riga']['riuscito'], 5: sens['M5_puntatore']['riuscito'] and sens['M5_negativo']['riuscito']}
    # ---- libri e giudici per gradino
    lib = OrderedDict((p, [C['libro|%d|%d' % (p, i)] for i in range(1, N_LIBRI20 + 1) if 'libro|%d|%d' % (p, i) in C]) for p in PASSI20)
    giud = OrderedDict()
    val = OrderedDict()                     # passo -> misura -> (media, errore)
    for p, rs in lib.items():
        if not rs:
            continue
        v = OrderedDict()
        v['e231'], v['e266'] = mes([r['AUC_e231'] for r in rs]), mes([r['AUC_e266'] for r in rs])
        v['K'] = mes([aucK.get('M%d:%d' % (p, r['i'])) for r in rs])
        v['A'] = mes([r.get('AUC_A') for r in rs])
        g = OrderedDict(libri=len(rs), e231=v['e231'], e266=v['e266'], K=v['K'], A=v['A'])
        g['per_replica'] = OrderedDict((j, [mes([r[k] for r in rs if r['replica'] == rp]) for rp in (0, 1)]) for j, k in (('e231', 'AUC_e231'), ('e266', 'AUC_e266')))
        g['repliche_diverse'] = OrderedDict((j, bool(all(x[0] is not None and x[1] is not None for x in pr) and abs(pr[0][0] - pr[1][0]) > 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)))
                                            for j, pr in g['per_replica'].items())
        g['gruppi_e266'] = OrderedDict((n, statistics.mean(r['gruppi_e266'][n] for r in rs)) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)
        giud[nome_passo(p)] = g
        val[p] = v
    i07 = OrderedDict(libri=len(R07['libri']))
    if R07['libri']:
        i07['e231'], i07['e266'] = mes([r['AUC_e231'] for r in R07['libri']]), mes([r['AUC_e266'] for r in R07['libri']])
        i07['A'] = mes([r.get('AUC_A') for r in R07['libri']])
    i07['K'] = mes([aucK[n] for n in aucK if n.startswith('I07:')])
    v21 = OrderedDict(libri=len(CHIAVI_V21), e231=(I7.V21['AUC_e231'][0], I7.V21['AUC_e231'][1]), e266=(I7.V21['AUC_e266'][0], I7.V21['AUC_e266'][1]),
                      K=mes([aucK[n] for n in aucK if n.startswith('V21:')]), A=mes(R07['v21_A']))
    out['giudici'] = OrderedDict(gradini=giud, ia07=i07, v21=v21)
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
    for p, rs in lib.items():
        if not rs:
            continue
        nm = nome_passo(p)
        qs = [I7.quote(r['copia']) for r in rs]
        cop[nm] = OrderedDict((k, mes([q[k] for q in qs])) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))
        rip[nm] = OrderedDict((k, mes([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else None for r in rs])) for k in rep_nat)
        m5, mr = cop[nm]['5-grammi'][0], cop[nm]['righe intere'][0]
        l5 = 'nessuna copia rilevante' if m5 is not None and m5 <= COPIA_5GRAMMI[0] else 'copia' if m5 is not None and m5 > COPIA_5GRAMMI[1] else 'zona grigia'
        lr = 'nessuna copia rilevante' if mr is not None and mr <= COPIA_RIGHE[0] else 'copia' if mr is not None and mr > COPIA_RIGHE[1] else 'zona grigia'
        r4, rsopra, rpp = rip[nm][k4][0], rip[nm][ks][0], rip[nm][kp][0]
        avvita = bool((r4 is not None and r4 > AVVITA_MIN and r4 > AVVITA_VOLTE * max(nat4, 1e-9)) or (rsopra is not None and rsopra > RIGA_SOPRA_MAX))
        nuove, rn = cop[nm]['parole nuove'][0], nat['parole nuove']
        lett_copia[nm] = OrderedDict([('5-grammi', l5), ('righe', lr), ('copia', 'copia' in (l5, lr)), ('zona_grigia', 'zona grigia' in (l5, lr)), ('si_avvita', avvita),
                                      ('parola_prima_alta', bool(rpp is not None and natp and rpp > PAROLA_PRIMA_VOLTE * natp)),
                                      ('parole_nuove_ok', bool(nuove is not None and rn and NUOVE_FASCIA[0] * rn <= nuove <= NUOVE_FASCIA[1] * rn))])
    modi = OrderedDict()
    if lib.get(5):
        tot = Counter()
        for r in lib[5]:
            tot.update(r.get('modi_scrittura', {}))
        modi = OrderedDict(tot)
    out['copia'] = OrderedDict(gradini=cop, naturale=nat, ripetizioni=rip, ripetizioni_naturali=OrderedDict((k, v[0] / v[1] if v[1] else None) for k, v in rep_nat.items()),
                               letture=lett_copia, modi_scrittura_M5=modi,
                               v21_esempio=I7.quote(rif_copia['v21 (libro d\'esempio)']) if 'v21 (libro d\'esempio)' in rif_copia else None)
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
    out['vero'] = vero
    out['struttura'] = struttura
    # ---- letture: validita'
    letture = OrderedDict()
    letture['validita'] = OrderedDict(paper=ok_paper, K=ok_K, A=ok_A, sensibilita=OrderedDict((nome_passo(p), bool(o)) for p, o in sens_ok.items()))
    # valori per passo di ogni misura (giudici e struttura)
    for p in val:
        s = struttura.get(nome_passo(p), {})
        for m_ in MISURE_STR:
            val[p][m_] = s.get(m_, (None, None))
    # ---- L1: ogni gradino contro il v21 sui tre giudici (regola di ia16); il gradino migliore = AUC media (e231, e266, K) piu' bassa
    L1 = OrderedDict()
    for p in val:
        cl = I16.classe_giudici({j: val[p][j] for j in ('e231', 'e266', 'K')}, v21)
        L1[nome_passo(p)] = OrderedDict(esito=I16.esito_v21(cl), giudici=cl, media_tre=statistics.mean(val[p][j][0] for j in ('e231', 'e266', 'K') if val[p][j][0] is not None)
                                        if all(val[p][j][0] is not None for j in ('e231', 'e266', 'K')) else None)
    migliori = [(L1[nome_passo(p)]['media_tre'], p) for p in val if L1[nome_passo(p)]['media_tre'] is not None]
    migliore = min(migliori)[1] if migliori else None
    if not (ok_paper and ok_K):
        for x in L1.values():
            x['esito'] = 'lettura non valida (controllo dei giudici fallito: ' + ', '.join(n for n, o in (('paper', ok_paper), ('K', ok_K)) if not o) + ')'
    else:
        for nm, x in L1.items():
            lc = lett_copia.get(nm)
            if lc and lc['copia']:
                x['esito'] += ' ma NON VALE: copia a memoria sopra la soglia'
            elif lc and (lc['zona_grigia'] or lc['si_avvita']):
                x['esito'] += ' (con riserva: copia in zona grigia o scrittura che si avvita)'
    letture['L1_contro_v21'] = OrderedDict(gradino_migliore=nome_passo(migliore) if migliore else None, esito_migliore=L1[nome_passo(migliore)]['esito'] if migliore else None, per_gradino=L1)
    # ---- L2: M1 riproduce ia07? (descrittivo)
    if 1 in val and i07.get('e231'):
        letture['M1_contro_ia07'] = classe_giudici_misure(val[1], i07)
    # ---- L3: ingrediente -> misure corrette / rotte
    tabella = OrderedDict()
    for p in PASSI20:
        if p < 2 or p not in val or (p - 1) not in val:
            continue
        cl = OrderedDict()
        for m_ in MISURE_STR:
            cl[m_] = classe_misura(val[p - 1][m_], val[p][m_], vero.get(m_))
        for j in GIUDICI:
            cl[j] = classe_misura(val[p - 1][j], val[p][j], None)
        x = lettura_ingrediente(p, cl, BERSAGLI[p])
        x['ingrediente'] = INGREDIENTI[p]
        x['classi'] = cl
        x['sensibilita'] = 'provata' if sens_ok.get(p) else 'NON provata (con riserva)'
        if not (ok_paper and ok_K):
            x['nota_giudici'] = 'giudici non validi: le colonne dei giudici non si leggono'
        tabella['%s (%s)' % (nome_passo(p), INGREDIENTI[p])] = x
    letture['L3_ingredienti'] = tabella
    # ---- L4: che cosa nessun gradino porta al vero
    irr = OrderedDict()
    for m_ in MISURE_STR:
        v = vero.get(m_)
        if v is None:
            continue
        righe = OrderedDict((nome_passo(p), val[p][m_]) for p in val)
        flags = OrderedDict((nm, al_vero(x, v)) for nm, x in righe.items())
        dist = OrderedDict((nm, abs(x[0] - v) if x[0] is not None else None) for nm, x in righe.items())
        d1 = dist.get('M1')
        migl = min((d, nm) for nm, d in dist.items() if d is not None) if any(d is not None for d in dist.values()) else None
        irr[m_] = OrderedDict(vero=v, valori={k: x[0] for k, x in righe.items()}, al_vero=flags, nessun_gradino_al_vero=not any(f for f in flags.values() if f is not None),
                              migliore=migl[1] if migl else None, distanza_migliore=migl[0] if migl else None, distanza_M1=d1,
                              frazione_del_cammino=(1 - migl[0] / d1) if migl and d1 else None)
    for j in GIUDICI:
        righe = OrderedDict((nome_passo(p), val[p][j]) for p in val)
        irr[j] = OrderedDict(v21=v21.get(j, (None, None))[0], valori={k: x[0] for k, x in righe.items()}, nessun_gradino_alla_pari_del_v21=None)
        mv = v21[j][0] if v21.get(j) else None
        if mv is not None:
            irr[j]['sotto_v21'] = OrderedDict((k, bool(x[0] is not None and x[0] < mv - SOGLIA_ERRORI * math.sqrt((x[1] or 0) ** 2 + (v21[j][1] or 0) ** 2))) for k, x in righe.items())
            irr[j]['nessun_gradino_alla_pari_del_v21'] = not any(irr[j]['sotto_v21'].values())
    letture['L4_irriproducibile'] = irr
    letture['L4_elenco'] = [m_ for m_, x in irr.items() if m_ in MISURE_STR and x['nessun_gradino_al_vero']]
    out['valori'] = OrderedDict((nome_passo(p), OrderedDict((k, x) for k, x in v.items())) for p, v in val.items())
    out['letture'] = letture
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('addestra', 'sens', 'libro', 'K', 'M', 'D'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    vet = [v for k, v in C.items() if k.startswith('vetrina|')]
    out['vetrina'] = vet or None
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def classe_giudici_misure(v1, i07):
    return OrderedDict((j, MS.confronta(v1[j][0], v1[j][1], i07[j][0], i07[j][1])) for j in ('e231', 'e266', 'K') if i07.get(j))


def mf(x, d=3):
    if x is None:
        return '—'
    if isinstance(x, (tuple, list)):
        return '%s ± %s' % (nu(x[0], d), nu(x[1], d)) if x[0] is not None else '—'
    return nu(x, d)


def scrivi_md(o):
    L = o['letture']
    md = ['# IA20 (ia20) — L\'imitatore a gradini', '', 'Preregistrazione: `preregistrazioni/ia20.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    c = o['controlli']
    md += ['## Controlli dei giudici', '']
    md.append('- Giudici del paper, positivo: AUC %s, soglia ≥ %s → %s. Negativo: giudice 1 %s, giudice 2 %s, banda 0,45–0,55 → %s.' % (
        nu(c['paper_positivo']['AUC']), nu(POS_PAPER, 2), nu(c['paper_positivo']['riuscito']), nu(c['paper_negativo']['AUC_e231']), nu(c['paper_negativo']['AUC_e266']), nu(c['paper_negativo']['riuscito'])))
    if 'K_positivo' in c:
        md.append('- K, positivo: %s, soglia ≥ %s → %s. Negativo (media di %d etichette): %s → %s. K vede il v21 (AUC %s, soglia ≥ %s) → %s.' % (
            ', '.join('%s %s' % (k, nu(v)) for k, v in c['K_positivo']['AUC'].items()), nu(POS_K, 2), nu(c['K_positivo']['riuscito']), len(c['K_negativo']['valori']),
            nu(c['K_negativo']['AUC']), nu(c['K_negativo']['riuscito']), nu(c['K_vede_v21']['AUC']), nu(K_VEDE_V21, 2), nu(c['K_vede_v21']['riuscito'])))
    md.append('- A (riportato, non decide), positivo: %s → %s. Negativo: %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['A_positivo']['AUC'].items()), nu(c['A_positivo']['riuscito']),
                                                                                   nu(c['A_negativo']['AUC']), nu(c['A_negativo']['riuscito'])))
    s = o['sensibilita']
    md += ['', '## Controlli di sensibilità degli ingredienti (testi sintetici con un ingrediente piantato)', '']
    md.append('- M3 (vocabolario della pagina), tema piantato: M3 sotto M2 di %s bit per segno (soglia ≥ %s) → %s.' % (nu(s['M3_vocabolario_pagina']['guadagno_su_M2']), nu(SENS['tema_M3_contro_M2']), nu(s['M3_vocabolario_pagina']['riuscito'])))
    md.append('- M4 (posizione nella riga), parole di bordo piantate: M4 sotto M3 di %s (soglia ≥ %s: non rovina; il guadagno atteso è piccolo, la GRU sa già contare) → %s.' % (nu(s['M4_posizione_riga']['guadagno_su_M3']), nu(SENS['bordi_M4_contro_M3']), nu(s['M4_posizione_riga']['riuscito'])))
    x = s['M5_puntatore']
    md.append('- M5 (puntatore), copia-e-ritocco piantata dalla riga sopra: M5 sotto M1 di %s (soglia ≥ %s), sotto M2 di %s; quota a posteriori della copia sulle parole copiabili %s (soglia ≥ %s) → %s.' % (
        nu(x['guadagno_su_M1']), nu(SENS['eco_M5_contro_M1']), nu(x['guadagno_su_M2']), nu(x['posteriori_copiabili']), nu(SENS['eco_post_copiabili']), nu(x['riuscito'])))
    x = s['M5_negativo']
    md.append('- M5, testo senza niente di piantato: M1 − M5 = %s (≤ %s: M5 non guadagna dal nulla) e massa di copia media %s (≤ %s) → %s. M2 su eco (descrittivo): guadagno su M1 %s.' % (
        nu(x['differenza_M1_M5']), nu(SENS['senza_M5_contro_M1']), nu(x['massa_media']), nu(SENS['senza_massa_max']), nu(x['riuscito']), nu(s['M2_memoria_locale']['guadagno_su_M1'])))
    md += ['', '## Modelli (bit per segno; medie sui 10 modelli di ogni gradino)', '', '| gradino | parametri | validazione | fuori piega | epoche scelte | al massimo | minuti per modello |', '|---|---|---|---|---|---|---|']
    for nm, x in o['bpc'].items():
        md.append('| %s | %d | %s | %s | %s | %d | %.1f |' % (nm, x['parametri'], mf(x['validazione']), mf(x['fuori']), nu(x['epoche_scelte'], 1), x['al_massimo'], x['secondi_medi'] / 60))
    if o['modelli_ia07']:
        v = [x[0] for x in o['modelli_ia07'].values() if x[0] is not None]
        f = [x[1] for x in o['modelli_ia07'].values() if x[1] is not None]
        md.append('\nia07 (GRU 2 × 256, stesse pieghe e repliche): validazione media %s, fuori media %s.' % (nu(statistics.mean(v)), nu(statistics.mean(f))))
    g = o['giudici']
    md += ['', '## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)', '', '| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |', '|---|---|---|---|---|---|']
    for nm, x in g['gradini'].items():
        md.append('| %s | %d | %s | %s | %s | %s |' % (nm, x['libri'], mf(x['e231']), mf(x['e266']), mf(x['K']), mf(x['A'])))
    md.append('| ia07 (GRU) | %d | %s | %s | %s | %s |' % (g['ia07']['libri'], mf(g['ia07'].get('e231')), mf(g['ia07'].get('e266')), mf(g['ia07'].get('K')), mf(g['ia07'].get('A'))))
    md.append('| v21 | %d | %s (paper) | %s (paper) | %s | %s |' % (g['v21']['libri'], mf(g['v21']['e231']), mf(g['v21']['e266']), mf(g['v21']['K']), mf(g['v21']['A'])))
    md += ['', 'Repliche diverse (più di 2 errori): ' + '; '.join('%s: %s' % (nm, ', '.join('%s %s' % (j, nu(b)) for j, b in x['repliche_diverse'].items())) for nm, x in g['gradini'].items()) + '.']
    md += ['', '## Struttura (media ± errore standard sui libri)', '', '| testo | ' + ' | '.join(MISURE_STR.values()) + ' |', '|' + '---|' * (len(MISURE_STR) + 1)]
    v = o['vero']
    if v:
        md.append('| **vero** | ' + ' | '.join(nu(v.get(m_), 4) for m_ in MISURE_STR) + ' |')
        for nm, x in o['struttura'].items():
            md.append('| %s (%d libri) | ' % (nm, x['libri']) + ' | '.join(mf(x[m_], 4) for m_ in MISURE_STR) + ' |')
    md += ['', '## Letture preregistrate', '']
    va = L['validita']
    md.append('- Validità: giudici del paper %s, K %s, A %s; sensibilità degli ingredienti: %s.' % (nu(va['paper']), nu(va['K']), nu(va['A']), ', '.join('%s %s' % (k, nu(b)) for k, b in va['sensibilita'].items())))
    l1 = L['L1_contro_v21']
    md.append('- **Esito finale: il gradino migliore (AUC media di e231, e266, K più bassa) è %s: %s.**' % (l1['gradino_migliore'], l1['esito_migliore']))
    for nm, x in l1['per_gradino'].items():
        md.append('  - %s contro il v21: %s (%s).' % (nm, x['esito'], '; '.join('%s %s (diff. %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items())))
    if 'M1_contro_ia07' in L:
        md.append('- M1 contro ia07 (stesso modello, tratti allineati alle righe: deve essere "uguale"): ' + '; '.join('%s %s' % (j, y['lettura']) for j, y in L['M1_contro_ia07'].items()) + '.')
    md += ['', '### Ingrediente → misure corrette / rotte', '', '| gradino | ingrediente | lettura | misure corrette | misure rotte | sensibilità |', '|---|---|---|---|---|---|']
    nomi_m = dict(MISURE_STR, **GIUDICI)
    for k, x in L['L3_ingredienti'].items():
        md.append('| %s | %s | **%s** | %s | %s | %s |' % (k.split(' ')[0], x['ingrediente'], x['esito'], ', '.join(nomi_m[m_] for m_ in x['corrette']) or '—', ', '.join(nomi_m[m_] for m_ in x['rotte']) or '—', x['sensibilita']))
    md += ['', '### Che cosa nessun gradino porta al vero', '', '| misura | vero | ' + ' | '.join('M%d' % p for p in o['passi']) + ' | al vero in qualche gradino | frazione del cammino del migliore |', '|---|---|' + '---|' * len(o['passi']) + '---|---|']
    for m_, x in L['L4_irriproducibile'].items():
        if m_ in MISURE_STR:
            md.append('| %s | %s | ' % (MISURE_STR[m_], nu(x['vero'], 4)) + ' | '.join('%s%s' % (nu(x['valori'].get('M%d' % p), 4), ' ✓' if x['al_vero'].get('M%d' % p) else '') for p in o['passi']) +
                      ' | %s | %s |' % ('no' if x['nessun_gradino_al_vero'] else 'sì', nu(x['frazione_del_cammino'], 2)))
    md += ['', '**Misure che nessun gradino porta al vero:** ' + (', '.join(MISURE_STR[m_] for m_ in L['L4_elenco']) or 'nessuna') + '.']
    for j in GIUDICI:
        x = L['L4_irriproducibile'].get(j)
        if x and x.get('sotto_v21') is not None:
            md.append('- %s: gradini che battono il v21 (%s): %s.' % (GIUDICI[j], nu(x['v21']), ', '.join(k for k, b in x['sotto_v21'].items() if b) or 'nessuno'))
    cp = o['copia']
    md += ['', '## Copia a memoria e ripetizioni (soglie severe)', '', '| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |', '|---|---|---|---|---|']
    for nm, q in cp['gradini'].items():
        md.append('| %s | %s |' % (nm, ' | '.join(mf(q[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    md.append('| naturale | %s |' % ' | '.join(nu(cp['naturale'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    for nm, x in cp['letture'].items():
        md.append('- %s: 5-grammi → %s, righe → %s; si avvita: %s; parola uguale alla prima alta: %s; parole nuove %s.' % (nm, x['5-grammi'], x['righe'], nu(x['si_avvita']), nu(x['parola_prima_alta']), 'nella fascia' if x['parole_nuove_ok'] else 'FUORI fascia'))
    md += ['', 'Ripetizioni dentro la pagina (naturale: %s):' % '; '.join('%s %s' % (k, nu(v, 4)) for k, v in cp['ripetizioni_naturali'].items())]
    for nm, r in cp['ripetizioni'].items():
        md.append('- %s: %s.' % (nm, '; '.join('%s %s' % (k, mf(x, 4)) for k, x in r.items())))
    if cp['modi_scrittura_M5']:
        md.append('\nM5, modi di scrittura delle parole (conti sui libri): ' + ', '.join('%s %d' % kv for kv in cp['modi_scrittura_M5'].items()) + '.')
    md += ['', '## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def lavori_fase(fase):
    if fase == 'A':
        mancanti = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
        # i gradini piu' lenti per primi (M5, M4, ...), a pari gradino prima la replica 0
        return mancanti + [('addestra', p, k, r) for p in sorted(PASSI20, reverse=True) for r in REPLICHE20 for k in range(PIEGHE)]
    if fase == 'Q':
        return [('sens', t, p) for t, ps in SENS_MODELLI.items() for p in sorted(ps, reverse=True) if p in PASSI20]
    if fase == 'C':
        return [('libro', p, i) for p in sorted(PASSI20, reverse=True) for i in range(1, N_LIBRI20 + 1)]
    if fase == 'V':
        return [('vetrina', int(os.environ.get('PASSO_VETRINA20', 5)))]
    if fase == 'D':
        nomi = nomi_libri()
        return ([('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0), ('casoA', 0)] + [('ctrlA', n) for n in I7.NOMI_CTRL_A] + [('K', f) for f in range(PIEGHE)] +
                [('D', f) for f in range(PIEGHE)] + [('M', 'vere')] + [('M', n) for n in nomi_struttura(nomi)])
    return []


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__), ('gradini', GM.VERSIONE)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD20, LIBRI20, MISURE20):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni, riga massima %d; gradini %s; PICCOLO %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), voc['lmax'], PASSI20, PICCOLO), flush=True)
    percorso = os.path.join(USCITA, 'ia20_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AQCDS')
    for fase in 'AQCVD':
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
        for k, x in o['letture'].items():
            if isinstance(x, dict) and 'esito_migliore' in x:
                print('%s: %s -> %s' % (k, x['gradino_migliore'], x['esito_migliore']), flush=True)


if __name__ == '__main__':
    main()
