# -*- coding: utf-8 -*-
"""Esperimento IA22 (ia22): l'eco della pagina e il legame fra parole, insieme.

Domanda (scelta di Davide, 21/11/2026: "eco + legame insieme"): si puo' costruire un imitatore che abbia INSIEME l'eco della pagina (copia netta, quota
locale Λ) e il legame fra parole (contatto ultimo -> primo glifo, ordine delle famiglie D) al vero? E se no, che cosa li rende incompatibili?
Punto di partenza (ia20): M1 ha contatto e D al vero ma niente eco; ogni ingrediente che porta l'eco (memoria locale, puntatore) rompe contatto e D.
Preregistrazione: preregistrazioni/ia22.md. I modelli stanno in echi_modelli.py, la fase 0 descrittiva in echi_fase0.py.

Che cosa fa il codice (in parole semplici)
- Fase A: 40 addestramenti (4 imitatori E0-E3 x 5 pieghe per foglio x 2 repliche) + eventuali modelli del giudice A mancanti.
    E1 eco come spinta sui logit della GRU (prodotto di esperti a livello di segno); E0 puntatore di M5 su base M1 (riferimento);
    E2 puntatore vincolato al contatto; E3 puntatore con inizio della parola rigenerato dalla GRU.
- Fase Q: controlli di sensibilita' su testi sintetici (eco + contatto piantati insieme; "senza niente").
- Fase C: libri onesti (N_LIBRI22 per tipo, meta' per replica) con giudici del paper, giudice A (riportato), copia a memoria e ripetizioni; e le stesse misure
  sui libri di M1 e M5 di ia20 letti dalla cache (riferimenti; mai riaddestrati).
- Fase F: fase 0 descrittiva sul testo vero, sul v21, su M1 e M5 (dove cade la modifica delle varianti d'eco, e se si accorda col contatto), con i controlli.
- Fase D: controlli dei giudici, giudice K, misure di struttura (copia netta, Λ, contatto, D, G9, bordi, parole nuove, forma), fase 0 sui libri E.
- Fase S: sintesi e letture preregistrate (L1-L4).
Uscite (solo numeri e aggregati): risultati/ia22_eco_e_legame.json e .md e, una riga per lavoro, risultati/ia22_corse.jsonl. Modelli, libri e profili in
dati/cache/ia22 (CACHE22, protetti: non si committano).

    nohup bash strumenti/coda.sh ia22 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia22" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO22=1 RIF22=ricalcola USCITA=<cartella fuori dal repo> python esperimenti/ia22_eco_e_legame.py   (prova sul latino)

Variabili (oltre a quelle di ia07 e ia20, che si importano): PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere A Q C F D S; predefinito AQCFDS),
FILTRO (sottostringhe, separate da |, che il nome del lavoro deve contenere). Nuove: CACHE22, EPOCHE22 (150), PAZIENZA22 (10), N_LIBRI22 (10), PICCOLO22 (solo prove;
deve coincidere con PICCOLO20), EPOCHE_SENS22 (60), TIPI22 (cifre, senza virgole: 0123 = E0 E1 E2 E3), RIF22 ('cache' = riferimenti M1 e M5 letti dalla cache di
ia20; 'ricalcola' = solo prove del codice: li addestra e li scrive qui). I valori predefiniti sono quelli preregistrati. Nessun valore contiene virgole o due punti
(la coda li dividerebbe); i percorsi con due punti si danno solo nelle prove, non dalla coda.
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
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import echi_fase0 as F0  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NOME = 'ia22_eco_e_legame'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE22 = os.environ.get('CACHE22', os.path.join(USCITA, 'ia22_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia22'))
MOD22, LIBRI22, MISURE22 = os.path.join(CACHE22, 'modelli'), os.path.join(CACHE22, 'libri'), os.path.join(CACHE22, 'misure')
PICCOLO = os.environ.get('PICCOLO22') == '1'
if PICCOLO != I20.PICCOLO:
    raise SystemExit('PICCOLO22 e PICCOLO20 devono avere lo stesso valore (le prove del codice usano la taglia piccola in tutti e due)')
IDX = OrderedDict((t, i) for i, t in enumerate(EM.TIPI))                       # E0..E3 -> 0..3
TIPI22 = tuple(EM.TIPI[int(x)] for x in os.environ.get('TIPI22', '0123') if x.isdigit())
REPLICHE22 = (0, 1)
EPOCHE22 = int(os.environ.get('EPOCHE22', 150))
PAZIENZA22 = int(os.environ.get('PAZIENZA22', 10))
N_LIBRI22 = int(os.environ.get('N_LIBRI22', 10))              # libri per tipo (meta' dalla replica 0, meta' dalla 1)
EPOCHE_SENS22 = int(os.environ.get('EPOCHE_SENS22', 60))
PAZIENZA_SENS22 = 10
RIF22 = os.environ.get('RIF22', 'cache')
PIEGHE = I7.PIEGHE
N_RIF = I20.N_LIBRI20                                          # libri di M1 e M5 di ia20 (10)
RIF_PASSI = (1, 5)
ETICHETTE = ['M1', 'E0', 'E1', 'E2', 'E3', 'M5']               # ordine nelle tabelle
CHIAVI_V21 = I20.CHIAVI_V21

# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_ERRORI = I20.SOGLIA_ERRORI                              # 2 errori
VERO_TOL = I20.VERO_TOL                                        # "al vero": entro 2 errori o 5% del vero
# controlli di sensibilita': fissati dopo le prove su testi non Voynich (vedi la preregistrazione, sezione "Prova del codice")
SENS22 = OrderedDict([('guadagno_su_M1', 0.10),                # eco+contatto: validazione almeno cosi' sotto M1 (bit per segno)
                      ('eco_rapporto', 0.70),                  # tasso di eco dei fogli scritti almeno questa frazione di quello del testo piantato (M1 sta a 0,35)
                      ('contatto_rapporto', 0.80),             # "quota del glifo iniziale preferito" e informazione mutua: almeno questa frazione
                      ('senza_guadagno_max', 0.02),            # senza niente: guadagno su M1 al massimo cosi'
                      ('senza_massa_max', 0.10)])              # senza niente: massa di copia media del puntatore al massimo cosi'
SENS_TESTI = OrderedDict([('ecocontatto', dict(eco=0.5, ritocco=0.6, inizio=0.5, contatto=0.6)), ('senza', dict(eco=0.0, contatto=0.0))])
SENS_MODELLI = OrderedDict([('ecocontatto', ('M1', 'E0', 'E1', 'E2', 'E3', 'M5')), ('senza', ('M1', 'E0', 'E1', 'E2', 'E3'))])
F0_SOGLIE = OrderedDict([('regola_presente_errori', 3.0), ('regola_presente_bit', 0.25), ('regola_assente_errori', 2.0), ('posto_primo_errori', 3.0)])
MISURE_STR = I20.MISURE_STR
MISURE_ECO = ['copia_netta', 'lam']                            # l'eco
MISURE_LEGAME = ['contatto', 'D']                              # il legame fra parole
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


def e_tipo_E(nome):
    return nome[0] == 'E' and nome[1].isdigit()


def e_rif(nome):
    return nome[0] == 'M' and nome[1].isdigit()


# ---------------------------------------------------------------- pagine e modelli

def pagine_fold22(piega, tipo, dp=None, tag='reale'):
    """(ctx, add, val, fuori): le pagine del modello della piega preparate per il tipo E; `ctx` ha le K parole piu' frequenti dell'addestramento."""
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
    add, val, fuori = EM.prepara_insiemi([sel(f_add), sel(f_val), sel(f_fuori)], ctx, tipo)
    _C[k] = (ctx, add, val, fuori)
    return _C[k]


def seme_modello(tipo, piega, replica):
    return 22000 + 1000 * IDX[tipo] + 100 * replica + piega


def percorso_modello(tipo, piega, replica, est):
    return os.path.join(MOD22, 'ia22_%s_%s_%d%s' % (tipo, piega, replica, est))


def addestra(tipo, piega, replica):
    inizio = time.time()
    voc = I7.vocabolario()
    ctx, add, val, fuori = pagine_fold22(piega, tipo)
    cfg = EM.cfg_completa(tipo, voc, ctx, PICCOLO)
    nome = '%s p%s r%d' % (tipo, piega, replica)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = EM.addestra_modello(cfg, ctx, add, val, seme_modello(tipo, piega, replica), EPOCHE22, PAZIENZA22, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'addestra|%s|%s|%d' % (tipo, piega, replica)), ('tipo', tipo), ('piega', piega), ('replica', replica),
                       ('parametri', sum(p.numel() for p in m.parameters())), ('pagine', [len(add), len(val), len(fuori)]),
                       ('epoche', len(ca)), ('epoca_scelta', scelta), ('arrivata_al_massimo', len(ca) >= EPOCHE22 and scelta > EPOCHE22 - PAZIENZA22),
                       ('curva_validazione', cv), ('curva_addestramento', ca),
                       ('bpc_addestramento', round(EM.bpc_pagine(m, ctx, add), 5)), ('bpc_validazione', round(EM.bpc_pagine(m, ctx, val), 5)),
                       ('bpc_fuori', round(EM.bpc_pagine(m, ctx, fuori), 5))])
    ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    ris['appresi'] = EM.parametri_appresi(m)
    if tipo != 'E1':
        ris['puntatore'] = EM.massa_copia(m, ctx, fuori)
    ris['secondi'] = round(time.time() - inizio, 1)
    EM.salva_modello(m, percorso_modello(tipo, piega, replica, '.pt'), voc['segni'], ctx, dict(tipo=tipo, piega=piega, replica=replica, epoca_scelta=scelta, solo_prova=bool(SOLO_CONTROLLI)))
    json.dump(ris, open(percorso_modello(tipo, piega, replica, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def carica(tipo, piega, replica):
    k = ('modello', tipo, piega, replica)
    if k not in _C:
        _C[k] = EM.carica_modello(percorso_modello(tipo, piega, replica, '.pt'), I7.vocabolario())
    return _C[k]


# ---------------------------------------------------------------- scrivere

def rigenera(pen, c, tipo_r, lg, regole, lung, prima, ctx, rng):
    """Strade di E3 (4 primo glifo riscritto, 5 glifo nuovo davanti, 6 primi due riscritti): il primo glifo (e il secondo) li pesca la GRU; il resto e' la
    parola d'eco `c`. -> parola (tuple di indici di glifo)."""
    u0 = ctx.u0
    amm = [a for a in regole.ammessi([], lung, prima) if a in regole.unita]
    if not amm:
        return None
    z = np.array([lg[a] for a in amm])
    z = np.exp(z - z.max())
    x = amm[I20.campiona(z / z.sum(), rng)]
    xu = x - u0
    if tipo_r == 4:
        return (xu,) + tuple(c[1:])
    if tipo_r == 5:
        return (xu,) + tuple(c)
    lg2 = pen.avanti([xu])[0].tolist()
    amm2 = [a for a in regole.ammessi([regole.unita[x]], lung + 1, 'segno') if a in regole.unita]
    if not amm2:
        return None
    z = np.array([lg2[a] for a in amm2])
    z = np.exp(z - z.max())
    y = amm2[I20.campiona(z / z.sum(), rng)]
    return (xu, y - u0) + tuple(c[2:])


def scrivi_pagina22(m, ctx, pen, regole, rp, voc, D, rng, conta):
    """Una pagina con la disposizione `rp`. E1: segno per segno (la spinta e' nei logit). E0, E2, E3: a inizio parola il puntatore sceglie fra libero e candidato
    (e strada); le strade 0-3 come in M5, le strade 4-6 con il primo (e il secondo) glifo scritti dalla GRU."""
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    nt = EM.NT_PUNT.get(m.tipo, 0)
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
            if nt:
                cand = pen.candidati()
                if cand:
                    pf, ppi = pen.puntatore(cand)
                    pr = np.concatenate([[pf], ppi[:len(cand)].reshape(-1)])
                    pr = pr / pr.sum()
                    for _ in range(8):
                        idx = int(rng.choice(len(pr), p=pr))
                        if idx == 0:
                            break
                        k, tipo_r = divmod(idx - 1, nt)
                        if tipo_r <= 3:
                            w2 = GM.campiona_ritocco(cand[k][0], tipo_r, psub, pins, rng)
                        else:
                            w2 = rigenera(pen, cand[k][0], tipo_r, lg, regole, lung, prima, ctx, rng)
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


def scrivi_libro22(tipo, replica, seme):
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
            m, ctx = carica(tipo, k, replica)
            penne[k] = (m, ctx, EM.Penna22(m, ctx, cap + 8))
        m, ctx, pen = penne[k]
        out += scrivi_pagina22(m, ctx, pen, regole, rp, voc, D, rng, conta)
    return out, conta


def percorso_libro(tipo, i):
    return os.path.join(LIBRI22, 'ia22_libro_%s_%d.txt' % (tipo, i))


def misura_libro(t, tabella):
    """Giudici del paper, giudice A, copia a memoria e ripetizioni di un libro scritto (lista (pagina, inizio, parole))."""
    ris = OrderedDict()
    ris.update(I7.giudica(t, tabella))
    try:
        ris.update(I7.giudice_A(I7.libro_A_da_righe(t)))
    except Exception as e:                                                # noqa: BLE001
        ris['A_errore'] = repr(e)
    ris['copia'] = I7.copia_onesta(t)
    ris['ripetizioni'] = MS.ripetizioni_interne({p: [ps for _, ps in rr] for p, rr in I16._raggruppa(t).items()})
    return ris


def lavoro_libro(tipo, i):
    inizio = time.time()
    replica = I7.replica_del_libro(i, N_LIBRI22)
    seme = 2200000 + 10000 * IDX[tipo] + i
    os.makedirs(LIBRI22, exist_ok=True)
    percorso = percorso_libro(tipo, i)
    conta = None
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t, conta = scrivi_libro22(tipo, replica, seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia22, libro %s %d' % (tipo, i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('replica', replica), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    if conta is not None and tipo != 'E1':
        ris['modi_scrittura'] = OrderedDict(conta)
    ris.update(misura_libro(t, os.path.join(LIBRI22, 'ia22_tabella_%s_%d.npz' % (tipo, i))))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_riflibro(passo, i):
    """Misure dei giudici sul libro i di M1 (passo 1) o M5 (passo 5) di ia20, letto dalla cache di ia20 (RIF22=cache). Con RIF22=ricalcola (solo prove) prima
    si addestrano e si scrivono con il codice di ia20."""
    inizio = time.time()
    percorso = I20.percorso_libro(passo, i)
    if not os.path.exists(percorso):
        if RIF22 != 'ricalcola':
            raise RuntimeError('manca il libro di ia20 %s (RIF22=cache): va fatto con ia20' % percorso)
        I20.lavoro_libro(passo, i)
    t = I7.leggi_file(percorso)
    ris = OrderedDict([('lavoro', 'riflibro|%d|%d' % (passo, i)), ('passo', passo), ('i', i), ('replica', I7.replica_del_libro(i, N_RIF)), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(misura_libro(t, None))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- controlli di sensibilita' (testi sintetici con eco e contatto piantati)

def righe_a_rows(righe, D, solo_pagine=None):
    out = OrderedDict()
    for x in righe:
        if solo_pagine is None or x['pagina'] in solo_pagine:
            out.setdefault(x['pagina'], []).append((bool(x['ini']), [tuple(D(w)) for w in x['parole']]))
    return out


def misure_sens(rows, pref, D):
    """Numeri del controllo su pagine (pagina -> righe): tasso di eco (parole uguali o a una modifica da una parola candidata), quota di parole (non prime) che
    cominciano con il glifo preferito dopo l'ultimo glifo della parola prima, informazione mutua del contatto (g di ia08)."""
    parole = copie = var = pref_n = pref_ok = 0
    for p, rr in rows.items():
        for (r, i, cat, det) in F0.varianti_pagina(rr):
            parole += 1
            copie += cat == 'copia'
            var += cat == 'variante'
        for _, ws in rr:
            for a, b in zip(ws, ws[1:]):
                pref_n += 1
                pref_ok += pref[a[-1]] == b[0]
    return OrderedDict(parole=parole, tasso_eco=(copie + var) / max(parole, 1), tasso_copia=copie / max(parole, 1), quota_preferito=pref_ok / max(pref_n, 1),
                       contatto=R.mi_contatto(rows) if len(rows) else None)


def lavoro_sens(testo, modello):
    """Un modello addestrato (piega 0) su un testo sintetico; validazione e fuori piega; per i modelli col puntatore la massa di copia; per `ecocontatto` si
    scrivono i fogli tenuti fuori e si misurano eco e contatto, confrontati con gli stessi numeri del testo piantato."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    pref = {}
    sint = EM.sintetico_eco_contatto(I7.libro_vero(), seme_str('ia22sint', testo), D, voc['unita'], pref_out=pref, **SENS_TESTI[testo])
    dps = I20.pagine_sintetiche(sint)
    nome = 'sens %s %s' % (testo, modello)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    seme = 32000 + 10 * list(SENS_TESTI).index(testo) + (['M1', 'E0', 'E1', 'E2', 'E3', 'M5'].index(modello))
    if modello in ('M1', 'M5'):
        passo = 1 if modello == 'M1' else 5
        ctx, add, val, fuori = I20.pagine_fold(0, passo, dps, tag='sint22:' + testo)
        cfg = GM.cfg_completa(passo, voc, ctx, PICCOLO)
        m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS22, PAZIENZA_SENS22, messaggi=messaggio)
        bv, bf = round(GM.bpc_pagine(m, ctx, val), 5), round(GM.bpc_pagine(m, ctx, fuori), 5)
        punt = GM.massa_copia(m, ctx, fuori) if passo >= 5 else None
        penna = lambda: GM.Penna20(m, ctx, cap)
        scrivi = lambda pen, regole, rp, rng, conta: I20.scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta)
    else:
        ctx, add, val, fuori = pagine_fold22(0, modello, dps, tag='sint22:' + testo)
        cfg = EM.cfg_completa(modello, voc, ctx, PICCOLO)
        m, cv, ca, scelta = EM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS22, PAZIENZA_SENS22, messaggi=messaggio)
        bv, bf = round(EM.bpc_pagine(m, ctx, val), 5), round(EM.bpc_pagine(m, ctx, fuori), 5)
        punt = EM.massa_copia(m, ctx, fuori) if modello != 'E1' else None
        penna = lambda: EM.Penna22(m, ctx, cap)
        scrivi = lambda pen, regole, rp, rng, conta: scrivi_pagina22(m, ctx, pen, regole, rp, voc, D, rng, conta)
    ris = OrderedDict([('lavoro', 'sens|%s|%s' % (testo, modello)), ('testo', testo), ('modello', modello), ('epoche', len(ca)), ('epoca_scelta', scelta),
                       ('bpc_validazione', bv), ('bpc_fuori', bf), ('curva_validazione', cv)])
    if punt is not None:
        ris['puntatore'] = punt
    if modello not in ('M1', 'M5'):
        ris['appresi'] = EM.parametri_appresi(m)
    if testo == 'ecocontatto':
        f_fuori = set(I7.fogli_della_piega(0)[2])
        pp = I7.per_pagina(sint)
        pag_fuori = [p for p in pp if I7.foglio_di(p) in f_fuori]
        rng = np.random.default_rng(seme_str('ia22scr', testo, modello))
        regole = I20.RegoleScrittura(voc)
        pen = penna()
        conta = Counter()
        t = []
        for p in pag_fuori:
            t += scrivi(pen, regole, pp[p], rng, conta)
        rows_gen = OrderedDict()
        for pag, ini, ps in t:
            rows_gen.setdefault(pag, []).append((bool(ini), [tuple(D(w)) for w in ps]))
        ris['scritto'] = misure_sens(rows_gen, pref, D)
        ris['piantato'] = misure_sens(righe_a_rows(sint, D, set(pag_fuori)), pref, D)
        ris['modi_scrittura'] = OrderedDict(conta)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


cap = None                                                              # capacita' massima di una pagina (si fissa in avvia_processo)


def fissa_capacita():
    global cap
    voc = I7.vocabolario()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in I7.per_pagina(I7.libro_vero()).values()) + 8


# ---------------------------------------------------------------- catalogo dei libri da misurare

def nomi_libri():
    """Nomi dei libri: E<k>:i (gli imitatori), M1:i e M5:i (ia20, dalla cache), V21:k (v21 senza messaggio di ia01), ctrl:* (controlli)."""
    nomi = []
    for t in TIPI22:
        nomi += ['%s:%d' % (t, i) for i in range(1, N_LIBRI22 + 1) if os.path.exists(percorso_libro(t, i))]
    for p in RIF_PASSI:
        nomi += ['M%d:%d' % (p, i) for i in range(1, N_RIF + 1) if os.path.exists(I20.percorso_libro(p, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    """Per le misure di struttura: tutti i libri E e di riferimento (M1, M5) e i primi 10 V21."""
    out = [x for x in nomi if e_tipo_E(x) or e_rif(x)]
    out += [x for x in nomi if x.startswith('V21:')][:10]
    return out


def t_di(nome):
    k = int(nome.split(':')[1]) if ':' in nome and nome.split(':')[1].isdigit() else None
    if e_tipo_E(nome):
        return I7.leggi_file(percorso_libro(nome.split(':')[0], k))
    if e_rif(nome):
        return I7.leggi_file(I20.percorso_libro(int(nome[1]), k))
    return I16.t_di(nome)


def rows_di(nome):
    if e_tipo_E(nome) or e_rif(nome):
        return I7.libro_A_da_righe(t_di(nome))
    return I16.rows_di(nome)


# ---------------------------------------------------------------- lavori di misura (fasi D e F)

def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_libri():
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE22, exist_ok=True)
    with open(os.path.join(MISURE22, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome):
    """Come ia20.lavoro_M, ma i libri si leggono con `rows_di` e `t_di` di ia22."""
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
        rng = np.random.default_rng(200022)
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


def lavoro_F0(nome):
    """Fase 0 su un testo (`vere`, un libro): conti delle varianti d'eco, posto della modifica e accordo col contatto (numeri e aggregati)."""
    inizio = time.time()
    c = I7.contesto_A()
    tab = F0.tabelle_fuori_piega(c['vere'], c['fold'])
    rows = c['vere'] if nome == 'vere' else rows_di(nome)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'F0|%s' % nome)])
    ris['conti'] = F0.conta_testo(pag, c['fold'], tab, seme_str('ia22F0', nome))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_F0c(segno):
    """Controlli della fase 0 su un testo sintetico con la regola piantata ('pos': il ritocco del primo glifo lo porta al glifo preferito dal contatto, con
    probabilita' 0,8) o assente ('neg': ritocchi a caso). Il testo e' la disposizione e il vocabolario del libro dato (nelle prove: latino)."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    c = I7.contesto_A()
    inizio_p = 0.8 if segno == 'pos' else 0.0
    sint = EM.sintetico_eco_contatto(I7.libro_vero(), seme_str('ia22F0c', segno), D, voc['unita'], eco=0.5, ritocco=0.6, inizio=inizio_p, contatto=0.6)
    rows = righe_a_rows(sint, D)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    tab = F0.tabelle_fuori_piega(pag, c['fold'])
    ris = OrderedDict([('lavoro', 'F0c|%s' % segno), ('regola', inizio_p)])
    ris['conti'] = F0.conta_testo(pag, c['fold'], tab, seme_str('ia22F0c', segno, 'conta'))
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
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
        if tipo == 'sens':
            return lavoro_sens(args[1], args[2])
        if tipo == 'libro':
            return lavoro_libro(args[1], int(args[2]))
        if tipo == 'riflibro':
            return lavoro_riflibro(int(args[1]), int(args[2]))
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


def bpc_riferimento(passo):
    """Bit per segno dei 10 modelli di M1 o M5 di ia20 (dalle schede json della cache di ia20; solo numeri)."""
    v, f = [], []
    for k in range(PIEGHE):
        for r in (0, 1):
            p = I20.percorso_modello(passo, k, r, '.json')
            if os.path.exists(p):
                d = json.load(open(p, encoding='utf-8'))
                v.append(d['bpc_validazione'])
                f.append(d['bpc_fuori'])
    return OrderedDict(modelli=len(v), validazione=mes(v), fuori=mes(f))


def lettura_f0(c, nomi_insiemi):
    """Dai risultati F0 (`c`: lavoro -> risultato) le righe per insieme di testi: numeri letti (vicini e lontani)."""
    out = OrderedDict()
    for etich, nomi in nomi_insiemi.items():
        rs = [c['F0|%s' % n]['conti'] for n in nomi if 'F0|%s' % n in c]
        if not rs:
            continue
        S = F0.somma_risultati(rs)
        riga = OrderedDict(testi=len(rs))
        for modo in ('vicini', 'lontani'):
            riga[modo] = F0.riassunto(S[modo])
        v, l = riga['vicini'], riga['lontani']
        for k in ('uno', 'due'):
            a, b = v['differenza_' + k], l['differenza_' + k]
            ea, eb = v['errore_' + k], l['errore_' + k]
            e = math.sqrt((ea or 0) ** 2 + (eb or 0) ** 2) if ea is not None and eb is not None else None
            riga['dd_' + k] = OrderedDict(differenza=(a - b) if a is not None and b is not None else None, errore=e)
        if v['quota_primo'] is not None and v['varianti']:
            se = math.sqrt(max(v['attesa_primo'] * (1 - v['attesa_primo']), 1e-9) / v['varianti'])
            riga['primo_contro_attesa'] = OrderedDict(osservata=v['quota_primo'], attesa=v['attesa_primo'], differenza=v['quota_primo'] - v['attesa_primo'], errore=se,
                                                      lontani=l['quota_primo'])
        out[etich] = riga
    return out


def lettura_regola(riga):
    """'presente' / 'assente' / 'zona grigia' per la regola "la variante cambia il primo glifo per accordarsi al contatto": confronto fra le varianti vere (vicini) e le
    varianti per caso (lontani), a un glifo. Soglie scritte prima."""
    d = riga['dd_uno']
    if d['differenza'] is None or not d['errore']:
        return 'non calcolabile'
    if d['differenza'] > F0_SOGLIE['regola_presente_errori'] * d['errore'] and d['differenza'] > F0_SOGLIE['regola_presente_bit']:
        return 'presente'
    if d['differenza'] <= F0_SOGLIE['regola_assente_errori'] * d['errore']:
        return 'assente'
    return 'zona grigia'


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    c_ctx = I7.contesto_A()
    n_pag = len(c_ctx['ids'])
    out = OrderedDict(esperimento='ia22', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=errori, tipi=list(TIPI22))
    # ---- modelli
    modelli = [C[k] for k in sorted(C) if k.startswith('addestra|')]
    out['modelli'] = [OrderedDict((k, v) for k, v in m.items() if k not in ('curva_validazione', 'curva_addestramento')) for m in modelli]
    bpc = OrderedDict()
    for t in TIPI22:
        ms = [m for m in modelli if m['tipo'] == t]
        if ms:
            bpc[t] = OrderedDict(modelli=len(ms), parametri=ms[0]['parametri'], validazione=mes([x['bpc_validazione'] for x in ms]), fuori=mes([x['bpc_fuori'] for x in ms]),
                                 epoche_scelte=mes([x['epoca_scelta'] for x in ms])[0], al_massimo=sum(bool(x['arrivata_al_massimo']) for x in ms),
                                 secondi_medi=statistics.mean(x['secondi'] for x in ms))
            if t != 'E1':
                bpc[t]['massa_copia_media'] = mes([x['puntatore']['massa_media'] for x in ms if x.get('puntatore')])[0]
    out['bpc'] = bpc
    out['bpc_riferimenti'] = OrderedDict((('M%d' % p), bpc_riferimento(p)) for p in RIF_PASSI)
    appresi = OrderedDict()
    for t in TIPI22:
        ap = [m['appresi'] for m in modelli if m['tipo'] == t and m.get('appresi')]
        if not ap:
            continue
        if t == 'E1':
            appresi[t] = OrderedDict(beta=np.mean([a['beta'] for a in ap], axis=0).round(4).tolist(), peso_distanza=np.mean([a['peso_distanza'] for a in ap], axis=0).round(3).tolist())
        else:
            appresi[t] = OrderedDict(beta=np.mean([a['beta'] for a in ap], axis=0).round(3).tolist())
            if t == 'E2':
                appresi[t]['gamma'] = mes([a['gamma'] for a in ap])
    out['appresi'] = appresi
    # ---- controlli dei giudici (come ia20)
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
        p = os.path.join(MISURE22, 'K_f%d.pkl' % f)
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
    # ---- controlli di sensibilita' (fase Q)
    sens = OrderedDict()
    sv = lambda t, m: C.get('sens|%s|%s' % (t, m))
    base = sv('ecocontatto', 'M1')
    sc = OrderedDict()
    if base:
        ep, ct = base['piantato']['tasso_eco'], base['piantato']['quota_preferito']
        sc['piantato'] = OrderedDict(tasso_eco=ep, quota_preferito=ct, contatto=base['piantato']['contatto'])
        for m in ('M1', 'E0', 'E1', 'E2', 'E3', 'M5'):
            r = sv('ecocontatto', m)
            if not r:
                continue
            g = r['scritto']
            x = OrderedDict(bpc_validazione=r['bpc_validazione'], guadagno_su_M1=base['bpc_validazione'] - r['bpc_validazione'], epoca_scelta=r['epoca_scelta'],
                            tasso_eco=g['tasso_eco'], eco_rapporto=g['tasso_eco'] / ep if ep else None, quota_preferito=g['quota_preferito'],
                            contatto_rapporto_pref=g['quota_preferito'] / ct if ct else None, contatto=g['contatto'],
                            contatto_rapporto=(g['contatto'] / base['piantato']['contatto']) if base['piantato']['contatto'] else None)
            x['eco_ok'] = bool(x['guadagno_su_M1'] >= SENS22['guadagno_su_M1'] and x['eco_rapporto'] is not None and x['eco_rapporto'] >= SENS22['eco_rapporto'])
            x['legame_ok'] = bool(x['contatto_rapporto_pref'] is not None and x['contatto_rapporto_pref'] >= SENS22['contatto_rapporto'] and x['contatto_rapporto'] is not None
                                  and x['contatto_rapporto'] >= SENS22['contatto_rapporto'])
            x['riuscito'] = x['eco_ok'] and x['legame_ok']
            sc[m] = x
    sens['ecocontatto'] = sc
    sn = OrderedDict()
    b1 = sv('senza', 'M1')
    for m in ('E0', 'E1', 'E2', 'E3'):
        r = sv('senza', m)
        if not r or not b1:
            continue
        mass = (r.get('puntatore') or {}).get('massa_media')
        gu = b1['bpc_validazione'] - r['bpc_validazione']
        sn[m] = OrderedDict(guadagno_su_M1=gu, massa_media=mass, riuscito=bool(gu <= SENS22['senza_guadagno_max'] and (mass is None or mass <= SENS22['senza_massa_max'])))
    sens['senza'] = sn
    out['sensibilita'] = sens
    sens_ok = {t: bool(sc.get(t, {}).get('eco_ok') and sn.get(t, {}).get('riuscito')) for t in TIPI22}          # sensibilita' provata = impara l'eco e non inventa guadagni dal nulla; "legame ok" e' un esito (lo scambio), non una condizione
    # ---- libri e giudici per etichetta
    lib = OrderedDict()
    for t in TIPI22:
        lib[t] = [C['libro|%s|%d' % (t, i)] for i in range(1, N_LIBRI22 + 1) if 'libro|%s|%d' % (t, i) in C]
    for p in RIF_PASSI:
        lib['M%d' % p] = [C['riflibro|%d|%d' % (p, i)] for i in range(1, N_RIF + 1) if 'riflibro|%d|%d' % (p, i) in C]
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
    for t in TIPI22:
        tot = Counter()
        for r in lib.get(t) or []:
            tot.update(r.get('modi_scrittura', {}))
        if tot:
            modi[t] = OrderedDict(tot)
    out['copia'] = OrderedDict(tipi=cop, naturale=nat, ripetizioni=rip, ripetizioni_naturali=OrderedDict((k, v[0] / v[1] if v[1] else None) for k, v in rep_nat.items()),
                               letture=lett_copia, modi_scrittura=modi)
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
    letture['validita'] = OrderedDict(paper=ok_paper, K=ok_K, A=ok_A, sensibilita=OrderedDict((t, bool(o)) for t, o in sens_ok.items()),
                                      scambio_visto_nel_sintetico=OrderedDict((t, bool(sc.get(t, {}).get('eco_ok') and not sc.get(t, {}).get('legame_ok'))) for t in TIPI22))
    for lab in val:
        s = struttura.get(lab, {})
        for m_ in MISURE_STR:
            val[lab][m_] = s.get(m_, (None, None))
    # ---- L1: eco e legame insieme al vero?
    L1 = OrderedDict()
    for lab in ETICHETTE:
        if lab not in val or not vero:
            continue
        fl = OrderedDict((m_, I20.al_vero(val[lab][m_], vero.get(m_))) for m_ in MISURE_ECO + MISURE_LEGAME)
        dist = OrderedDict((m_, (abs(val[lab][m_][0] - vero[m_]) / abs(vero[m_])) if val[lab][m_][0] is not None and vero.get(m_) else None) for m_ in MISURE_ECO + MISURE_LEGAME)
        L1[lab] = OrderedDict(al_vero=fl, distanza_relativa=dist, eco_al_vero=bool(all(fl[m_] for m_ in MISURE_ECO)), legame_al_vero=bool(all(fl[m_] for m_ in MISURE_LEGAME)),
                              tutti_al_vero=bool(all(fl.values())), valori=OrderedDict((m_, val[lab][m_][0]) for m_ in MISURE_ECO + MISURE_LEGAME))
    letture['L1_eco_e_legame'] = OrderedDict(per_tipo=L1, esiste=[t for t in TIPI22 if t in L1 and L1[t]['tutti_al_vero']],
                                             vero=OrderedDict((m_, vero.get(m_)) for m_ in MISURE_ECO + MISURE_LEGAME))
    # ---- L2: ogni imitatore contro M1 (aggiunge l'eco?) e contro M5 (tiene il legame?)
    L2 = OrderedDict()
    for t in TIPI22:
        if t not in val:
            continue
        for rif, bers in (('M1', MISURE_ECO), ('M5', MISURE_LEGAME)):
            if rif not in val or not vero:
                continue
            cl = OrderedDict()
            for m_ in MISURE_STR:
                cl[m_] = I20.classe_misura(val[rif][m_], val[t][m_], vero.get(m_))
            for j in GIUDICI:
                cl[j] = I20.classe_misura(val[rif][j], val[t][j], None)
            x = I20.lettura_ingrediente(0, cl, bers)
            x['classi'] = cl
            x['sensibilita'] = 'provata' if sens_ok.get(t) else 'NON provata (con riserva)'
            if not (ok_paper and ok_K):
                x['nota_giudici'] = 'giudici non validi: le colonne dei giudici non si leggono'
            L2['%s contro %s' % (t, rif)] = x
    letture['L2_contro_M1_e_M5'] = L2
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
    # ---- L4: fase 0
    nomi_ins = OrderedDict([('vere', ['vere']), ('v21', ['V21:%d' % k for k in CHIAVI_V21][:10]), ('M1', ['M1:%d' % i for i in range(1, N_RIF + 1)]),
                            ('M5', ['M5:%d' % i for i in range(1, N_RIF + 1)])])
    for t in TIPI22:
        nomi_ins[t] = ['%s:%d' % (t, i) for i in range(1, N_LIBRI22 + 1)]
    f0 = lettura_f0(C, nomi_ins)
    ctrl0 = OrderedDict()
    for sg in ('pos', 'neg'):
        if 'F0c|%s' % sg in C:
            S = C['F0c|%s' % sg]['conti']
            riga = OrderedDict(regola=C['F0c|%s' % sg]['regola'])
            for modo in ('vicini', 'lontani'):
                riga[modo] = F0.riassunto(S[modo])
            v, l = riga['vicini'], riga['lontani']
            dd = (v['differenza_uno'] - l['differenza_uno']) if v['differenza_uno'] is not None and l['differenza_uno'] is not None else None
            e = math.sqrt((v['errore_uno'] or 0) ** 2 + (l['errore_uno'] or 0) ** 2)
            riga['dd_uno'] = OrderedDict(differenza=dd, errore=e)
            riga['lettura'] = lettura_regola(riga)
            ctrl0[sg] = riga
    ok0 = bool(ctrl0.get('pos', {}).get('lettura') == 'presente' and ctrl0.get('neg', {}).get('lettura') == 'assente')
    for etich, riga in f0.items():
        riga['regola'] = lettura_regola(riga) if ok0 else 'lettura non valida (controllo della fase 0 fallito)'
        pc = riga.get('primo_contro_attesa')
        if pc:
            pc['eccesso_sul_primo'] = bool(pc['differenza'] > F0_SOGLIE['posto_primo_errori'] * pc['errore'])
    letture['L4_fase0'] = OrderedDict(controlli=ctrl0, controlli_ok=ok0, insiemi=f0)
    out['valori'] = OrderedDict((lab, OrderedDict((k, x) for k, x in v.items())) for lab, v in val.items())
    out['letture'] = letture
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('addestra', 'sens', 'libro', 'riflibro', 'K', 'M', 'D', 'F0'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def scrivi_md(o):
    L = o['letture']
    md = ['# IA22 (ia22) — Eco e legame fra parole, insieme', '', 'Preregistrazione: `preregistrazioni/ia22.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
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
    sc = s['ecocontatto']
    if sc.get('piantato'):
        md.append('Testo con eco e contatto piantati insieme (fogli tenuti fuori della piega 0): tasso di eco %s, quota del glifo iniziale preferito %s, contatto %s.' % (
            nu(sc['piantato']['tasso_eco']), nu(sc['piantato']['quota_preferito']), nu(sc['piantato']['contatto'])))
        md += ['', '| modello | guadagno su M1 (bit/segno) | eco scritta / piantata | glifo preferito scritto / piantato | contatto scritto / piantato | eco ok | legame ok | riuscito |', '|---|---|---|---|---|---|---|---|']
        for m, x in sc.items():
            if m == 'piantato':
                continue
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (m, nu(x['guadagno_su_M1']), nu(x['eco_rapporto']), nu(x['contatto_rapporto_pref']), nu(x['contatto_rapporto']), nu(x['eco_ok']), nu(x['legame_ok']), nu(x['riuscito'])))
    md += ['', 'Testo senza niente di piantato: ' + '; '.join('%s: guadagno su M1 %s, massa di copia %s → %s' % (m, nu(x['guadagno_su_M1']), nu(x['massa_media']), nu(x['riuscito'])) for m, x in s['senza'].items()) + '.']
    md += ['', '## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)', '', '| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa di copia | minuti per modello |', '|---|---|---|---|---|---|---|---|']
    for nm, x in o['bpc'].items():
        md.append('| %s | %d | %s | %s | %s | %d | %s | %.1f |' % (nm, x['parametri'], mf(x['validazione']), mf(x['fuori']), nu(x['epoche_scelte'], 1), x['al_massimo'], nu(x.get('massa_copia_media')), x['secondi_medi'] / 60))
    for nm, x in o['bpc_riferimenti'].items():
        md.append('| %s (ia20) | — | %s | %s | — | — | — | — |' % (nm, mf(x['validazione']), mf(x['fuori'])))
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
    md.append('- Validità: giudici del paper %s, K %s, A %s; sensibilità: %s; controlli della fase 0 %s.' % (nu(va['paper']), nu(va['K']), nu(va['A']), ', '.join('%s %s' % (k, nu(b)) for k, b in va['sensibilita'].items()), nu(L['L4_fase0']['controlli_ok'])))
    md.append('- Scambio visto nel testo sintetico (eco imparata ma legame piantato perso): ' + (', '.join(k for k, b in va['scambio_visto_nel_sintetico'].items() if b) or 'nessun tipo') + '.')
    l1 = L['L1_eco_e_legame']
    md += ['', '### L1: eco e legame insieme "al vero"?', '', '**Imitatori con copia netta, Λ, contatto e D tutti al vero: %s.**' % (', '.join(l1['esiste']) or 'nessuno'), '',
           '| tipo | copia netta | Λ | contatto | D | eco al vero | legame al vero | tutti |', '|---|---|---|---|---|---|---|---|',
           '| vero | ' + ' | '.join(nu(l1['vero'][m_], 3) for m_ in MISURE_ECO + MISURE_LEGAME) + ' | | | |']
    for t, x in l1['per_tipo'].items():
        md.append('| %s | ' % t + ' | '.join('%s%s' % (nu(x['valori'][m_], 3), ' ✓' if x['al_vero'][m_] else '') for m_ in MISURE_ECO + MISURE_LEGAME) + ' | %s | %s | %s |' % (nu(x['eco_al_vero']), nu(x['legame_al_vero']), nu(x['tutti_al_vero'])))
    md += ['', '### L2: ogni imitatore contro M1 (eco aggiunta?) e contro M5 (legame tenuto?)', '', '| confronto | lettura | misure corrette | misure rotte | sensibilità |', '|---|---|---|---|---|']
    nomi_m = dict(MISURE_STR, **GIUDICI)
    for k, x in L['L2_contro_M1_e_M5'].items():
        md.append('| %s | **%s** | %s | %s | %s |' % (k, x['esito'], ', '.join(nomi_m[m_] for m_ in x['corrette']) or '—', ', '.join(nomi_m[m_] for m_ in x['rotte']) or '—', x['sensibilita']))
    l3 = L['L3_contro_v21']
    md += ['', '### L3: contro il v21', '', '- **Tipo migliore (AUC media di e231, e266, K): %s.**' % l3['migliore']]
    for nm, x in l3['per_tipo'].items():
        md.append('  - %s: %s (%s).' % (nm, x['esito'], '; '.join('%s %s (diff. %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items())))
    f4 = L['L4_fase0']
    md += ['', '### L4: fase 0 — dove cade la modifica delle varianti d\'eco e se si accorda col contatto', '']
    for sg, x in f4['controlli'].items():
        md.append('- Controllo %s (regola piantata = %s): a un glifo vicini %s, lontani %s, differenza %s ± %s → lettura **%s**.' % (
            sg, nu(x['regola'], 1), nu(x['vicini']['differenza_uno']), nu(x['lontani']['differenza_uno']), nu(x['dd_uno']['differenza']), nu(x['dd_uno']['errore']), x['lettura']))
    md += ['', '| testo | varianti | quota sul primo glifo (attesa a posto uniforme; lontani) | un glifo: vicini − rimescolata | lontani | vicini − lontani ± errore | regola |', '|---|---|---|---|---|---|---|']
    for etich, x in f4['insiemi'].items():
        pc = x.get('primo_contro_attesa') or {}
        md.append('| %s | %d | %s (%s; %s) | %s | %s | %s ± %s | **%s** |' % (etich, x['vicini']['varianti'], nu(pc.get('osservata')), nu(pc.get('attesa')), nu(pc.get('lontani')), nu(x['vicini']['differenza_uno']),
                                                                              nu(x['lontani']['differenza_uno']), nu(x['dd_uno']['differenza']), nu(x['dd_uno']['errore']), x['regola']))
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
        if RIF22 == 'ricalcola':
            rif = [('rifaddestra', p, k, r) for p in RIF_PASSI for r in REPLICHE22 for k in range(PIEGHE)]
        # i piu' lenti per primi (E2, E3, E0, E1), a pari tipo prima la replica 0
        ordine = [t for t in ('E2', 'E3', 'E0', 'E1') if t in TIPI22]
        return mancanti + rif + [('addestra', t, k, r) for t in ordine for r in REPLICHE22 for k in range(PIEGHE)]
    if fase == 'Q':
        return [('sens', t, m) for t, ms in SENS_MODELLI.items() for m in ms if m in TIPI22 or m in ('M1', 'M5')]
    if fase == 'C':
        return [('riflibro', p, i) for p in RIF_PASSI for i in range(1, N_RIF + 1)] + [('libro', t, i) for t in [x for x in ('E2', 'E3', 'E0', 'E1') if x in TIPI22] for i in range(1, N_LIBRI22 + 1)]
    if fase == 'F':
        nomi = nomi_libri()
        ref = [x for x in nomi if e_rif(x) or x.startswith('V21:')]
        return [('F0c', 'pos'), ('F0c', 'neg'), ('F0', 'vere')] + [('F0', n) for n in ref]
    if fase == 'D':
        nomi = nomi_libri()
        return ([('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0), ('casoA', 0)] + [('ctrlA', n) for n in I7.NOMI_CTRL_A] + [('K', f) for f in range(PIEGHE)] +
                [('D', f) for f in range(PIEGHE)] + [('M', 'vere')] + [('M', n) for n in nomi_struttura(nomi)] + [('F0', n) for n in nomi if e_tipo_E(n)])
    return []


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__), ('echi', EM.VERSIONE), ('gradini', GM.VERSIONE)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD22, LIBRI22, MISURE22):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni, riga massima %d; tipi %s; PICCOLO %s; riferimenti %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), voc['lmax'], TIPI22, PICCOLO, RIF22), flush=True)
    percorso = os.path.join(USCITA, 'ia22_corse.jsonl')
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
        print('L1: eco e legame tutti al vero: %s' % (', '.join(l1['esiste']) or 'nessuno'), flush=True)


if __name__ == '__main__':
    main()
