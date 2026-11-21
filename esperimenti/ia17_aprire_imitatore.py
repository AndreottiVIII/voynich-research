# -*- coding: utf-8 -*-
"""Esperimento IA17 (ia17): aprire l'imitatore. Dove guarda, che cosa succede se gli si toglie la memoria della pagina, quali regole contiene.

Segue ia16 (un transformer a segni che rilegge la pagina). Preregistrazione: preregistrazioni/ia17.md. Non si addestra l'imitatore di ia16:
si leggono i suoi modelli salvati (`dati/cache/ia16/modelli`), pagina per pagina sui fogli che ogni modello non ha mai visto.
Importa ia16, ia13, ia07, e (tramite imitatore_misure) ia09, ia10, ia08, senza modificarli.

Che cosa fa il codice (in parole semplici)
- Fase A, "leggi": per ogni modello P2 (replica 0 e 1, 5 pieghe) e P1 (replica 0): mappe di attenzione degli strati globali (quota per distanza
  in righe e per tipo di bersaglio; sollevamento sulle parole eco, cioe' uguali o a una modifica da quella che sta per essere scritta, contro
  parole non-eco alla stessa distanza); bit per segno e per parola con la memoria ridotta (senza la pagina precedente, solo le ultime k righe,
  senza le parole eco, con il controllo "altrettante parole non-eco"); e i bit di ogni parola con le righe rimescolate (come ia13) per le regole.
- Fase K, controlli: due testi sintetici sulla disposizione del libro (uno con un'eco piantata due righe sopra, uno senza eco) e per ognuno un
  imitatore addestrato qui (taglia scelta da ia16, 1 piega), letto con le stesse funzioni: l'attenzione deve vedere l'eco piantata a distanza 2,
  la maschera deve toglierla, il testo senza eco deve dare attenzione piatta; e libri scritti con e senza memoria.
- Fase B, libri: libri scritti dai modelli P2 con memoria ridotta (senza pagina precedente, solo la riga, riga piu' una sopra, riga piu' tre sopra).
- Fase M, misure: copia netta e quota locale (ia09), contatto (ia08), D (ia10) e firma dei bordi della riga sui libri e sul vero.
- Fase R, regole: tabelle di pezzi e alberi come ia13 sulla perdita dei rimescolamenti letta dall'imitatore, e regole di eco sul risparmio
  di bit dovuto alla memoria della pagina; R2 fuori campione a confronto con ia13.
- Fase S: sintesi e letture preregistrate. Se ia16 non ha dato un imitatore valido l'analisi si fa lo stesso, come descrizione dichiarata.
Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia17_aprire_imitatore.json e .md e, una riga per lavoro,
risultati/ia17_corse.jsonl. I file con parole e glifi veri (bit per parola, libri scritti, regole con glifi) stanno solo in dati/cache/ia17.

    nohup bash strumenti/coda.sh ia17 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia17" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO16=1 TAGLIE16=P USCITA=<cartella fuori dal repo> python esperimenti/ia17_aprire_imitatore.py   (prova sul libro latino)

Variabili (oltre a quelle di ia16 e ia07: SOLO_CONTROLLI, USCITA, PICCOLO16, TAGLIE16, CACHE16, BOOT, ...): PROCESSI (non cambia i risultati),
RIPRENDI, FASI (lettere A K B M R S; predefinito tutte), FILTRO (sottostringhe, separate da |, che il nome del lavoro deve contenere).
Le fasi A, K e B (indipendenti) girano in un solo gruppo di processi. Nuove: CACHE17 (cartella protetta: dati/cache/ia17), REPLICHE17 (0,1), PIEGHE17 (0,1,2,3,4: solo per le prove), N_ABL17 (libri per condizione, 5),
EPOCHE17C (epoche massime dei modelli di controllo, 20), PAZIENZA17C (8), COPIE_SINT17 (copie del testo sintetico per l'addestramento, 8), N_SEMI17 (rimescolamenti per parola, 3).
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
import imitatore_modelli as IM  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import ia13_cosa_vede_rete as I13  # noqa: E402
import vedere_permutazioni as VP  # noqa: E402
import aprire_parole as AP  # noqa: E402
import aprire_attenzione as AA  # noqa: E402
import aprire_scrittura as AS  # noqa: E402
import aprire_regole as AR  # noqa: E402

NOME = 'ia17_aprire_imitatore'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE17 = os.environ.get('CACHE17', os.path.join(USCITA, 'ia17_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia17'))
REPLICHE17 = tuple(int(x) for x in os.environ.get('REPLICHE17', '0,1').split(',') if x)
PIEGHE17 = tuple(int(x) for x in os.environ.get('PIEGHE17', '0,1,2,3,4').split(',') if x)
N_ABL17 = int(os.environ.get('N_ABL17', 5))
EPOCHE17C = int(os.environ.get('EPOCHE17C', 20))
PAZIENZA17C = int(os.environ.get('PAZIENZA17C', 8))
N_SEMI17 = int(os.environ.get('N_SEMI17', 3))
COPIE17 = int(os.environ.get('COPIE_SINT17', 8))      # copie del testo sintetico (altri semi) per l'addestramento dei controlli
BOOT = I16.BOOT
NF = I7.PIEGHE

# condizioni di lettura (a parole note) e libri con memoria ridotta
COND_P2 = ('pieno', 'senza_prec', 'k0', 'k1', 'k2', 'k4', 'k8', 'eco_via', 'ctrl_via', 'eco_uguale_via', 'ctrl_uguale_via')
COND_P1 = tuple(c for c in COND_P2 if c != 'senza_prec')
COND_K = ('pieno', 'k0', 'k1', 'k2', 'k3', 'eco_via', 'ctrl_via')                  # controlli sintetici
LIBRI17 = OrderedDict([('SP', 'SP'), ('K0', 0), ('K1', 1), ('K3', 3)])             # nome del libro -> regola di memoria
NOMI_COND = OrderedDict([('pieno', 'memoria piena'), ('senza_prec', 'senza la pagina precedente'), ('k0', 'solo la riga'),
                         ('k1', 'riga e 1 sopra'), ('k2', 'riga e 2 sopra'), ('k3', 'riga e 3 sopra'), ('k4', 'riga e 4 sopra'), ('k8', 'riga e 8 sopra'),
                         ('eco_via', 'senza le parole eco (uguali o a una modifica)'), ('ctrl_via', 'senza altrettante parole non-eco'),
                         ('eco_uguale_via', 'senza le parole uguali'), ('ctrl_uguale_via', 'senza altrettante parole non uguali')])
# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
LIFT_SI, LIFT_SI_BASSO = 1.5, 1.25               # sollevamento: "piu' del caso"
LIFT_NO, LIFT_NO_ALTO = 0.67, 0.80               # "meno del caso"
LIFT_BANDA = (0.80, 1.25)                        # "come il caso" (intervallo dentro la banda)
SOGLIA_BIT = 0.03                                # bit per parola: differenza che "conta" (come ia09 e ia13)
CT_LIFT_POS, CT_LIFT_POS_BASSO, CT_ALTRE_DISTANZE = 3.0, 2.0, 2.0     # controllo positivo, attenzione
CT_BIT_POS, CT_BIT_POS_BASSO, CT_BIT_STESSA = 0.30, 0.15, 0.10         # controllo positivo, maschere (bit per parola)
CT_BIT_STESSA_REL = 0.05                         # k3 meno k2 puo' arrivare al 5% di k1 meno k2 (con un'eco forte 0,10 bit sono rumore)
CT_LIBRO_POS, CT_LIBRO_MASCH, CT_LIBRO_ALTRE = 0.25, 0.05, 0.10        # controllo positivo, libri (quota di righe copiate)
CT_NEG_BANDA = (0.70, 1.43)                      # controllo negativo: sollevamento
CT_NEG_BIT, CT_NEG_CELLE = 0.05, 100             # controllo negativo: bit e numero minimo di celle per giudicare un sollevamento
CT_R2_POS, CT_R2_POS_BASSO, CT_R2_NEG = 0.30, 0.20, 0.03             # controllo delle regole: l'eco piantata si ritrova / non c'e' niente da ritrovare
CT_FALSO = (0.80, 1.25)                          # strumento: eco con la parola da scrivere sbagliata
CT_COERENZA = 1e-3                               # bit: scrittura a passi contro calcolo a pagina intera con maschera
R2_SI, R2_SI_BASSO, R2_NO = 0.30, 0.20, 0.10     # come ia13
R2_MARGINE = 0.05                                # confronto con ia13: differenza che conta
ECO_PRESENTE = 0.5                               # P2 "ha eco" se la sua copia netta e' almeno la meta' del vero
SOGLIA_MISURA = 2.0                              # errori per leggere una differenza fra libri
LAM_MIN = 0.03                                  # Λ si legge solo se la copia netta del libro e' almeno 0,03 bit per parola (come ia09)
CALO_ECO = 0.5                                   # senza memoria l'eco "si perde" se la copia netta e' sotto la meta' di P2
LIM_K_ECO = 0.2                                  # la memoria "sta entro k righe" se con k righe resta almeno l'80% del risparmio

_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


# ---------------------------------------------------------------- l'ingresso: le varianti di ia16 che hanno superato i loro controlli

def condizione_ingresso():
    """IA17 si legge solo per le varianti di ia16 che hanno superato i loro controlli (giudici del paper e K riusciti, nessuna copia a memoria
    sopra le soglie). Se ia16 non da' un imitatore valido l'analisi si fa lo stesso, come descrizione dichiarata."""
    p = os.path.join(USCITA, 'ia16_imitatore.json')
    out = OrderedDict(file=p, disponibile=os.path.exists(p), varianti=OrderedDict())
    if not out['disponibile']:
        for v in IM.VARIANTI:
            out['varianti'][v] = OrderedDict(stato='non verificabile (risultati di ia16 non trovati)', valida=None, riserva=False)
        out['solo_descrizione'] = True
        out['nota'] = 'risultati di ia16 non trovati: ' + ('prova sui soli controlli' if SOLO_CONTROLLI else 'ATTENZIONE, la corsa vera dovrebbe partire dopo ia16')
        return out
    o = json.load(open(p, encoding='utf-8'))
    val = o.get('letture', {}).get('validita', {})
    cop = o.get('copia', {}).get('letture', {})
    out['validita_ia16'] = OrderedDict((k, val.get(k)) for k in ('paper', 'K', 'A', 'copia_ok'))
    out['L1'] = o.get('letture', {}).get('L1_contro_v21', {}).get('esito')
    out['L2'] = o.get('letture', {}).get('L2_contro_ia07', {}).get('esito')
    for v in IM.VARIANTI:
        c = cop.get(v)
        if c is None:
            out['varianti'][v] = OrderedDict(stato='non valida (nessun libro scritto da ia16)', valida=False, riserva=False)
            continue
        controlli = bool(val.get('paper')) and bool(val.get('K'))
        ok = controlli and not c.get('copia')
        riserva = bool(c.get('zona_grigia') or c.get('si_avvita'))
        motivi = []
        if not val.get('paper'):
            motivi.append('controlli dei giudici del paper non riusciti')
        if not val.get('K'):
            motivi.append('controlli di K non riusciti')
        if c.get('copia'):
            motivi.append('copia a memoria sopra le soglie')
        out['varianti'][v] = OrderedDict(stato=('valida con riserva (copia in zona grigia o scrittura che si avvita)' if (ok and riserva) else 'valida' if ok else
                                                'non valida: ' + '; '.join(motivi)), valida=ok, riserva=riserva)
    out['solo_descrizione'] = not out['varianti'].get('P2', {}).get('valida')
    return out


# ---------------------------------------------------------------- una pagina letta dal modello

def leggi_pagina(m, stato, var, p, voc, D, righe_pag, cache_tipi, conds, R_rim, con_att):
    """Tutte le letture di una pagina (tenuta fuori dal modello): bit per segno e per parola in ogni condizione, rimescolamenti, attenzione.
    Restituisce un dizionario di array (parole della pagina nell'ordine di lettura)."""
    Tm, mem = 0, None
    tokc, lin = np.asarray(p['tok'], dtype=np.int64), np.asarray(p['linea'], dtype=np.int64)
    if var == 'P2' and p['prev_tok'] is not None:
        Tm = len(p['prev_tok'])
        mem = m.memoria(p['prev_tok'], p['prev_cond'])
        tokc = np.concatenate([np.asarray(p['prev_tok'], dtype=np.int64), tokc])
        lin = np.concatenate([np.full(Tm, AP.LINEA_MEM, dtype=np.int64), lin])
    S = AP.Struttura(tokc, lin, Tm, voc)
    T = len(p['tok']) - 1
    qinfo = AA.info_query(S, T, voc)
    seme_c = MS.seme_str('ia17ctrl', p['nome'])
    nll = OrderedDict()
    nll['pieno'] = AA.nll_pagina(m, p, mem, stato, None, Tm)
    for c in conds:
        if c == 'pieno':
            continue
        if c == 'senza_prec':
            nll[c] = nll['pieno'] if Tm == 0 else AA.nll_pagina(m, p, None, stato, None, 0)
        elif c[0] == 'k':
            nll[c] = AA.nll_pagina(m, p, None, stato, AA.maschera_righe(S, T, int(c[1:]), False), 0)
        else:
            ex = AA.maschera_eco(S, T, qinfo, 'uguale' in c, c.startswith('ctrl'), seme_c, cache_tipi)
            nll[c] = AA.nll_pagina(m, p, mem, stato, ex, Tm)
    cw = OrderedDict((c, AA.costi_parole(nll[c], S)) for c in conds)
    ok = ~np.isnan(nll['pieno'])
    assert abs(cw['pieno'].sum() - float(np.nansum(nll['pieno']))) < 1e-3 * max(1.0, cw['pieno'].sum()), 'i bit per parola non sommano ai bit della pagina'
    vp = np.nonzero(~S.w_mem)[0]
    out = dict(nome=p['nome'], n_seg=int(ok.sum()), bit={c: float(np.nansum(nll[c])) for c in conds}, cw=cw, J=S.w_J[vp], nl=S.w_nl[vp], riga=S.w_linea[vp],
               posto=AA.etichetta_posto(S), parole=[S.tipi_parola[v] for v in vp])
    out['dl_eq'], out['dl_mod'], out['mem_eq'], out['mem_mod'] = AA.info_eco_parole(S)
    # rimescolamenti (come ia13, `tutto`): bit in piu' per ogni parola quando le parole di ogni riga sono rimescolate
    nwp = len(vp)
    rim_g, rim_t, rim_s = np.zeros((nwp, R_rim)), np.zeros((nwp, R_rim)), np.zeros((nwp, R_rim))
    if R_rim and righe_pag is not None:
        Jv, lv = S.w_J[vp], S.w_linea[vp]
        for r in range(R_rim):
            rnd = random.Random(MS.seme_str('ia17rim', p['nome'], r))
            pis = [VP.p_tutto(len(x['parole']), rnd) for x in righe_pag]
            righe2 = [dict(x, parole=[x['parole'][i] for i in pi]) for x, pi in zip(righe_pag, pis)]
            seq2 = np.array(I7.sequenza(righe2, voc, D), dtype=np.int64)
            assert len(seq2) == len(p['tok'])
            p2 = dict(p)
            p2['tok'] = seq2
            nll2 = AA.nll_pagina(m, p2, mem, stato, None, Tm)
            S2 = AP.Struttura(np.concatenate([tokc[:Tm], seq2]), lin, Tm, voc)
            cw2 = AA.costi_parole(nll2, S2)
            vecchio = np.arange(nwp) - Jv + np.array([pis[l][j] for l, j in zip(lv, Jv)], dtype=np.int64)
            d = np.zeros((nwp, 4))
            d[vecchio] = cw2 - cw['pieno'][vecchio]
            rim_g[:, r], rim_t[:, r] = d[:, :3].sum(1), d.sum(1)
            rim_s[:, r] = (cw2 - cw['pieno'])[:, :3].sum(1)          # appaiata per POSTO nella riga (per i bordi, come ia13)
    out['rim_g'], out['rim_t'], out['rim_s'] = rim_g, rim_t, rim_s
    if con_att:
        out['att'] = AA.aggrega_attenzione(m, p, mem, S, T, qinfo, cache_tipi, MS.seme_str('ia17falso', p['nome']))
    return out


def leggi_modello(m, var, pagine, righe_per_pagina, conds, R_rim, con_att, messaggi=None):
    """Legge tutte le `pagine` (dizionari di pagina di ia16) con il modello `m`. Restituisce il dizionario da salvare (vedi `salva_leggi`)."""
    voc, D = I7.vocabolario(), I7.divisore()
    m.eval()
    stato = AA.installa_maschera(m, voc['primo_contenuto'])
    cache_tipi = {}
    pg = []
    inizio = time.time()
    for i, p in enumerate(pagine):
        pg.append(leggi_pagina(m, stato, var, p, voc, D, righe_per_pagina.get(p['nome']) if righe_per_pagina else None, cache_tipi, conds, R_rim, con_att))
        if messaggi and (i + 1) % 10 == 0:
            messaggi('  %d/%d pagine, %.0f s' % (i + 1, len(pagine), time.time() - inizio))
    L = OrderedDict(pagine=[x['nome'] for x in pg], conds=list(conds), n_seg=np.array([x['n_seg'] for x in pg]),
                    bit=OrderedDict((c, np.array([x['bit'][c] for x in pg])) for c in conds))
    L['w_pag'] = np.concatenate([np.full(len(x['J']), i, dtype=np.int64) for i, x in enumerate(pg)]) if pg else np.zeros(0, dtype=np.int64)
    for k in ('J', 'nl', 'riga', 'posto', 'dl_eq', 'dl_mod', 'mem_eq', 'mem_mod'):
        L['w_' + k] = np.concatenate([x[k] for x in pg])
    L['cost'] = OrderedDict((c, np.concatenate([x['cw'][c] for x in pg]).astype(np.float32)) for c in conds)
    L['rim_g'] = np.concatenate([x['rim_g'] for x in pg]).astype(np.float32)
    L['rim_t'] = np.concatenate([x['rim_t'] for x in pg]).astype(np.float32)
    L['rim_s'] = np.concatenate([x['rim_s'] for x in pg]).astype(np.float32)
    parole = [w for x in pg for w in x['parole']]
    L['w_off'] = np.concatenate([[0], np.cumsum([len(w) for w in parole])]).astype(np.int64)
    L['w_gl'] = np.array([g for w in parole for g in w], dtype=np.int32)
    if con_att:
        L['att'] = OrderedDict((k, np.stack([x['att'][k] for x in pg])) for k in pg[0]['att'])
    return L


def salva_leggi(percorso, L, meta):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    plat = dict(pagine=np.array(L['pagine']), conds=np.array(L['conds']), n_seg=L['n_seg'], w_off=L['w_off'], w_gl=L['w_gl'],
                rim_g=L['rim_g'], rim_t=L['rim_t'], rim_s=L['rim_s'], meta=np.array(json.dumps(meta)))
    for c in L['conds']:
        plat['bit__' + c] = L['bit'][c]
        plat['cost__' + c] = L['cost'][c]
    for k in ('pag', 'J', 'nl', 'riga', 'posto', 'dl_eq', 'dl_mod', 'mem_eq', 'mem_mod'):
        plat['w_' + k] = L['w_' + k]
    for k, v in L.get('att', {}).items():
        plat['att__' + k] = v
    np.savez_compressed(percorso + '.tmp.npz', **plat)
    os.replace(percorso + '.tmp.npz', percorso)


def carica_leggi(percorso):
    z = np.load(percorso, allow_pickle=False)
    L = OrderedDict(pagine=[str(x) for x in z['pagine']], conds=[str(x) for x in z['conds']], n_seg=z['n_seg'], w_off=z['w_off'], w_gl=z['w_gl'],
                    rim_g=z['rim_g'], rim_t=z['rim_t'], rim_s=z['rim_s'], meta=json.loads(str(z['meta'])))
    L['bit'] = OrderedDict((c, z['bit__' + c]) for c in L['conds'])
    L['cost'] = OrderedDict((c, z['cost__' + c]) for c in L['conds'])
    for k in ('pag', 'J', 'nl', 'riga', 'posto', 'dl_eq', 'dl_mod', 'mem_eq', 'mem_mod'):
        L['w_' + k] = z['w_' + k]
    att = OrderedDict((k[5:], z[k]) for k in z.files if k.startswith('att__'))
    if att:
        L['att'] = att
    L['piega'] = L['meta'].get('piega')
    L['parole'] = [tuple(int(x) for x in L['w_gl'][L['w_off'][i]:L['w_off'][i + 1]]) for i in range(len(L['w_pag']))]
    L['nomi_pagine_parola'] = [L['pagine'][i] for i in L['w_pag']]
    return L


# ---------------------------------------------------------------- lavori

def taglia17():
    return I16.taglia_scelta()['taglia']


def percorso_leggi(var, replica, piega):
    return os.path.join(CACHE17, 'leggi', 'leggi_%s_%s_%d_%d.npz' % (var, taglia17(), replica, piega))


def lavoro_leggi(var, replica, piega):
    """Un modello di ia16 (var, replica, piega) letto sulle pagine dei fogli che non ha mai visto."""
    inizio = time.time()
    ts = taglia17()
    percorso = percorso_leggi(var, replica, piega)
    if not os.path.exists(percorso):
        m = I16.carica(var, ts, piega, replica)
        _, _, f_fuori = I7.fogli_della_piega(piega)
        dp = I16.dati_pagine()
        pagine = [I16.pagina_modello(n, None, m.cfg['prec']) for n, d in dp.items() if d['foglio'] in set(f_fuori)]
        pp = I7.per_pagina(I7.libro_vero())
        conds = COND_P2 if var == 'P2' else COND_P1
        L = leggi_modello(m, var, pagine, pp, conds, N_SEMI17, True, messaggi=lambda s: _stampa('[leggi %s r%d p%d] %s' % (var, replica, piega, s)))
        salva_leggi(percorso, L, dict(var=var, replica=replica, piega=piega, taglia=ts, solo_prova=bool(SOLO_CONTROLLI)))
    else:
        L = carica_leggi(percorso)
    ris = OrderedDict([('lavoro', 'leggi|%s|%d|%d' % (var, replica, piega)), ('pagine', len(L['pagine'])), ('parole', int(len(L['w_pag']))),
                       ('segni', int(L['n_seg'].sum()))])
    ris['bit_per_segno'] = OrderedDict((c, round(float(L['bit'][c].sum() / L['n_seg'].sum()), 4)) for c in L['conds'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def _stampa(s):
    try:
        print(s, flush=True)
    except OSError:
        pass


def verifica_coerenza(var, replica, piega, n_pagine=2):
    """Controllo (uno per tipo di modello): la scrittura segno per segno con la regola di memoria (`passo17`) da' gli stessi bit del calcolo a
    pagina intera con la maschera, per le regole k = 0, 1, 3, 'SP' e senza regola (pagina in corso, senza coda); massima differenza in bit."""
    voc = I7.vocabolario()
    m = I16.carica(var, taglia17(), piega, replica)
    stato = AA.installa_maschera(m, voc['primo_contenuto'])
    dp = I16.dati_pagine()
    _, _, f_fuori = I7.fogli_della_piega(piega)
    nomi = [n for n, d in dp.items() if d['foglio'] in set(f_fuori)][:n_pagine]
    mx = OrderedDict()
    for n in nomi:
        p = I16.pagina_modello(n, None, m.cfg['prec'])
        p0 = dict(p, prev_tok=None, prev_cond=None)
        T = len(p['tok']) - 1
        S = AP.Struttura(p['tok'], p['linea'], 0, voc)
        for regola in (None, 'SP', 0, 1, 3):
            ex = AA.maschera_righe(S, T, regola, False) if isinstance(regola, int) else None
            a = AA.nll_pagina(m, p0, None, stato, ex, 0)
            b = AS.nll_a_passi(m, p0, regola)
            d = float(np.nanmax(np.abs(a - b)))
            mx['%s' % (regola,)] = max(mx.get('%s' % (regola,), 0.0), d)
    return mx


def lavoro_coerenza():
    inizio = time.time()
    ris = OrderedDict([('lavoro', 'coerenza')])
    piega = PIEGHE17[0]
    for var in ('P2', 'P1'):
        if os.path.exists(I16.percorso_modello(var, taglia17(), piega, 0, '.pt')):
            ris[var] = verifica_coerenza(var, 0, piega)
    ris['massimo'] = max([max(v.values()) for k, v in ris.items() if k in ('P2', 'P1')] or [None])
    ris['soglia'] = CT_COERENZA
    ris['riuscito'] = bool(ris['massimo'] is not None and ris['massimo'] <= CT_COERENZA)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---- controlli sintetici

SEMI_SINT = 17000


def pagine_sintetiche(righe_s):
    """Le pagine di un testo sintetico nel formato di ia16 (con il collegamento alla pagina precedente), come `ia16.dati_pagine`."""
    voc, D = I7.vocabolario(), I7.divisore()
    pp = I7.per_pagina(righe_s)
    nomi = list(pp)
    T = {voc['idx']['T:' + t] for t in 'PMUS'}
    out = OrderedDict()
    for i, p in enumerate(nomi):
        s = np.array(I7.sequenza(pp[p], voc, D), dtype=np.int64)
        out[p] = dict(nome=p, foglio=I7.foglio_di(p), tok=s, cond=s[1:4].copy(), linea=I16.linee_di(s, T), prev=nomi[i - 1] if i else None)
    return out


def pagina_sint(dp, p, ammessi, prec):
    d = dict(dp[p])
    pr = dp[p]['prev']
    if pr is not None and (ammessi is None or dp[pr]['foglio'] in ammessi):
        d['prev_tok'], d['prev_cond'] = dp[pr]['tok'][-prec:], dp[pr]['cond']
    else:
        d['prev_tok'] = d['prev_cond'] = None
    return d


def percorso_sint(tipo, estensione='.pt'):
    return os.path.join(CACHE17, 'controlli', 'ia17_sint_%s_%s%s' % (tipo, taglia17(), estensione))


def lavoro_sint(tipo):
    """Un controllo sintetico: testo ('eco_d2' o 'senza_eco'), modello addestrato qui (piega PIEGHE17[0], taglia scelta), lettura, libri."""
    inizio = time.time()
    ts = taglia17()
    voc, D = I7.vocabolario(), I7.divisore()
    righe = I7.libro_vero()
    piega = PIEGHE17[0]
    sint = AP.genera_sintetico(righe, tipo, MS.seme_str('ia17sint', tipo), D, voc['unita'])
    dp = pagine_sintetiche(sint)
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    cfg = IM.configurazione(ts, 'P2', len(voc['segni']), finestra_riga=voc['lmax'] + 8, piccolo=I16.PICCOLO)
    sa = set(f_add)
    ins = lambda ff, amm: [pagina_sint(dp, p, amm, cfg['prec']) for p, d in dp.items() if d['foglio'] in set(ff)]
    add, val, fuori = ins(f_add, sa), ins(f_val, None), ins(f_fuori, None)
    for k in range(1, COPIE17):           # altre copie del testo (altro seme, stessa disposizione) solo per l'addestramento: piu' passi per epoca
        sk = AP.genera_sintetico(righe, tipo, MS.seme_str('ia17sint', tipo, k), D, voc['unita'])
        sk = [dict(x, pagina=x['pagina'] + '#%d' % k) for x in sk]
        dk = pagine_sintetiche(sk)
        add += [pagina_sint(dk, p, sa, cfg['prec']) for p, d in dk.items() if d['foglio'] in sa]
    percorso = percorso_sint(tipo)
    ris = OrderedDict([('lavoro', 'sint|%s' % tipo), ('tipo', tipo), ('piega', piega), ('pagine', [len(add), len(val), len(fuori)])])
    if os.path.exists(percorso):
        m = IM.carica_modello(percorso, voc['segni'])
        info = json.load(open(percorso_sint(tipo, '.json'), encoding='utf-8'))
    else:
        nome = 'sint %s' % tipo
        m, cv, ca, scelta = IM.addestra_modello(cfg, add, val, voc['primo_contenuto'], SEMI_SINT + (1 if tipo == 'eco_d2' else 2), EPOCHE17C, PAZIENZA17C,
                                                messaggi=lambda s: _stampa('[%s] %s' % (nome, s)))
        info = OrderedDict([('epoche', len(ca)), ('epoca_scelta', scelta), ('bpc_validazione', round(IM.bpc_pagine(m, val, voc['primo_contenuto']), 4)),
                            ('bpc_fuori', round(IM.bpc_pagine(m, fuori, voc['primo_contenuto']), 4)), ('curva_validazione', cv)])
        IM.salva_modello(m, percorso, voc['segni'], dict(tipo=tipo, piega=piega, solo_prova=bool(SOLO_CONTROLLI)))
        json.dump(info, open(percorso_sint(tipo, '.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    ris['modello'] = info
    L = leggi_modello(m, 'P2', fuori, None, COND_K, 0, True, messaggi=lambda s: _stampa('[sint %s] %s' % (tipo, s)))
    ris['lettura'] = riassunto_lettura(L)
    # regole: le regole di eco distillate dal risparmio di bit della memoria (k1: senza le righe oltre la prima sopra) devono ritrovare l'eco piantata
    Dc = AR.D_semplice(L, 5, ['k1'])
    rc = AR.regole_da_D(Dc, 'k1', True)
    ris['regole'] = OrderedDict(righe=rc['righe'], delta_medio=rc['delta_medio'], migliore_eco=rc['migliore_eco'],
                                R2_migliore_eco=vd(rc['famiglie'][rc['migliore_eco']]['R2']), R2_albero16_eco=vd(rc['albero']['eco'][16]),
                                R2_albero16_pezzi=vd(rc['albero']['pezzi'][16]))
    # libri: scritti sulle pagine tenute fuori, con la memoria piena e con la memoria ridotta
    nomi_fuori = {p['nome'] for p in fuori}
    pp = I7.per_pagina(sint)
    rate = OrderedDict()
    rate['testo_sintetico'] = AP.righe_uguali_a_distanza(OrderedDict((p, [x['parole'] for x in pp[p]]) for p in pp if p in nomi_fuori))
    for nome, regola in (('pieno', None), ('K1', 1), ('K3', 3)):
        t = AS.scrivi_libro17(regola, lambda pag: m, MS.seme_str('ia17sintlibro', tipo, nome), pagine=nomi_fuori)
        per = OrderedDict()
        for pag, ini, ps in t:
            per.setdefault(pag, []).append(ps)
        rate[nome] = AP.righe_uguali_a_distanza(per)
    ris['righe_copiate'] = rate
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def percorso_libro17(nome, i):
    return os.path.join(CACHE17, 'libri', 'ia17_libro_%s_%d.txt' % (nome, i))


def lavoro_libro17(nome, i):
    """Un libro scritto dai modelli P2 (replica 0, taglia scelta; stessi semi del libro P2 numero i di ia16) con la memoria ridotta `nome`
    (SP, K0, K1, K3) o, per `RIPR`, senza riduzione (deve riprodurre il libro di ia16, parola per parola)."""
    inizio = time.time()
    ts = taglia17()
    regola = None if nome == 'RIPR' else LIBRI17[nome]
    seme = 1600000 + 10000 * IM.VARIANTI.index('P2') + i
    replica = I16.replica_del_libro('P2', i)
    os.makedirs(os.path.join(CACHE17, 'libri'), exist_ok=True)
    percorso = percorso_libro17(nome, i)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (nome, i)), ('nome', nome), ('i', i), ('replica', replica)])
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t = AS.scrivi_libro17(regola, I16.modello_di_replica('P2', ts, replica), seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia17, libro %s %d' % (nome, i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t]
    ris['righe'] = len(t)
    ris['parole'] = sum(len(ps) for _, _, ps in t)
    if nome == 'RIPR':
        ia16 = I16.percorso_libro('P2', ts, i)
        ris['ia16_presente'] = os.path.exists(ia16)
        ris['uguale_a_ia16'] = bool(os.path.exists(ia16) and I7.leggi_file(ia16) == t)
    else:
        ris['copia'] = I7.copia_onesta(t)
        per = OrderedDict()
        for pag, ini, ps in t:
            per.setdefault(pag, []).append(ps)
        ris['ripetizioni'] = MS.ripetizioni_interne(per)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def nomi_libri17():
    """Nomi dei libri da misurare: P2:i (ia16), SP:i, K0:i, K1:i, K3:i. Quelli di cui esiste il file."""
    ts = taglia17()
    nomi = ['P2:%d' % i for i in range(1, N_ABL17 + 1) if os.path.exists(I16.percorso_libro('P2', ts, i))]
    for n in LIBRI17:
        nomi += ['%s:%d' % (n, i) for i in range(1, N_ABL17 + 1) if os.path.exists(percorso_libro17(n, i))]
    return nomi


def rows_libro17(nome):
    s, k = nome.split(':')
    if s == 'P2':
        return I7.libro_A_da_righe(I7.leggi_file(I16.percorso_libro('P2', taglia17(), int(k))))
    return I7.libro_A_da_righe(I7.leggi_file(percorso_libro17(s, int(k))))


def bordi_conti_per_pagina(rows):
    return {p: AP.conti_bordi({p: r}) for p, r in rows.items()}


def somma_conti(lista):
    tot = {g: {f: Counter() for f in ('primo', 'ultimo', 'lung')} for g in ('prima', 'ultima', 'interna')}
    for c in lista:
        for g in tot:
            for f in tot[g]:
                tot[g][f].update(c[g][f])
    return tot


def lavoro_M17(nome):
    inizio = time.time()
    c = I7.contesto_A()
    rows = c['vere'] if nome == 'vere' else rows_libro17(nome)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'M|%s' % nome)])
    ris.update(MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag}))
    cp = bordi_conti_per_pagina(pag)
    ris['bordi'] = AP.firma_da_conti(somma_conti(list(cp.values())))
    if nome == 'vere':
        rng = np.random.default_rng(170017)
        ps = list(cp)
        bs = []
        for _ in range(200):
            f = AP.firma_da_conti(somma_conti([cp[ps[i]] for i in rng.integers(0, len(ps), len(ps))]))
            bs.append(f)
        ris['bordi_ic'] = OrderedDict((k, [float(np.nanpercentile([b[k] for b in bs if b[k] is not None], q)) for q in (2.5, 97.5)]) for k in ris['bordi'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D17(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_libri17():
        testi[n] = rows_libro17(n)
    out, info = MS.lavoro_D(f, c, testi)
    return OrderedDict([('lavoro', 'D|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('secondi', round(time.time() - inizio, 1))])


def lavoro_regole(var):
    """Regole distillate dall'imitatore `var` (P2): sulla perdita dei rimescolamenti (ordine) e sul risparmio dovuto alla memoria della pagina."""
    inizio = time.time()
    ts = taglia17()
    liste = []
    for rp in REPLICHE17 if var == 'P2' else (0,):
        ls = [carica_leggi(percorso_leggi(var, rp, f)) for f in PIEGHE17 if os.path.exists(percorso_leggi(var, rp, f))]
        if len(ls) != len(PIEGHE17):
            raise RuntimeError('mancano pieghe di %s replica %d' % (var, rp))
        liste.append(ls)
    bers = ['k0', 'k1', 'k2', 'senza_prec'] if var == 'P2' else ['k0', 'k1', 'k2']
    D = AR.costruisci_D(liste, bers)
    ris = OrderedDict([('lavoro', 'regole|%s' % var), ('righe_totali', int(len(D['J']))), ('repliche', D['n_repliche'])])
    segni = I7.vocabolario()['segni']
    os.makedirs(os.path.join(CACHE17, 'regole'), exist_ok=True)
    ris['ordine'] = AR.regole_da_D(D, 'ord', True, segni, os.path.join(CACHE17, 'regole', 'regole_%s_ordine.txt' % var), 'ordine, %s' % var)
    for b in bers:
        ris['mem_' + b] = AR.regole_da_D(D, b, True, segni, os.path.join(CACHE17, 'regole', 'regole_%s_%s.txt' % (var, b)), 'memoria %s, %s' % (b, var))
    for k in list(ris):
        if k == 'ordine' or k.startswith('mem_'):
            ris[k] = jsonifica_regole(ris[k])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def jsonifica_regole(r):
    if r is None:
        return None
    o = OrderedDict(r)
    o['famiglie'] = OrderedDict((k, dict(v, R2=v['R2'].d())) for k, v in r['famiglie'].items())
    o['albero'] = OrderedDict((g, OrderedDict((str(L), v.d()) for L, v in d.items())) for g, d in r['albero'].items())
    return o


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        t = args[0]
        if t == 'leggi':
            return lavoro_leggi(args[1], int(args[2]), int(args[3]))
        if t == 'coerenza':
            return lavoro_coerenza()
        if t == 'sint':
            return lavoro_sint(args[1])
        if t == 'libro':
            return lavoro_libro17(args[1], int(args[2]))
        if t == 'M':
            return lavoro_M17(args[1])
        if t == 'D':
            return lavoro_D17(int(args[1]))
        if t == 'regole':
            return lavoro_regole(args[1])
        raise ValueError(t)
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
    if processi <= 1:                                       # un solo processo: senza gruppo (prove)
        avvia_processo()
        risultati = (lavoro(a) for a in da_fare)
        pool = None
    else:
        pool = get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo)
        risultati = pool.imap_unordered(lavoro, da_fare)
    for k, r in enumerate(risultati, 1):
        out.append(r)
        with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
        if r.get('errore'):
            print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
        else:
            fatte.add(r['lavoro'])
            print('[%d/%d %.1f min] %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], r.get('secondi', 0)), flush=True)
    if pool is not None:
        pool.close()
        pool.join()
    return out


def leggi_corse(percorso):
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()] if os.path.exists(percorso) else []


def lavori_fase(fase):
    if fase == 'A':
        L = [('coerenza',)]
        L += [('leggi', 'P2', rp, f) for rp in REPLICHE17 for f in PIEGHE17]
        L += [('leggi', 'P1', 0, f) for f in PIEGHE17]
        return L
    if fase == 'K':
        return [('sint', 'eco_d2'), ('sint', 'senza_eco')]
    if fase == 'B':
        return [('libro', 'RIPR', 1)] + [('libro', n, i) for n in LIBRI17 for i in range(1, N_ABL17 + 1)]
    if fase == 'M':
        return [('M', 'vere')] + [('M', n) for n in nomi_libri17()] + [('D', f) for f in range(NF)]
    if fase == 'R':
        return [('regole', 'P2'), ('regole', 'P1')]
    return []


# ---------------------------------------------------------------- analisi: mettere insieme le pagine

def sposta_per_pagina(Ls):
    """Da una lista di letture (una per piega) a dizionari di array per pagina (P, ...) nell'ordine delle pagine."""
    pagine = [n for L in Ls for n in L['pagine']]
    P = len(pagine)
    conds = list(Ls[0]['conds'])
    off = np.cumsum([0] + [len(L['pagine']) for L in Ls])
    w_pag = np.concatenate([L['w_pag'] + off[i] for i, L in enumerate(Ls)])
    posto = np.concatenate([L['w_posto'] for L in Ls])
    out = OrderedDict(pagine=pagine, conds=conds, P=P)
    out['n_seg'] = np.concatenate([L['n_seg'] for L in Ls]).astype(float)
    out['bit'] = OrderedDict((c, np.concatenate([L['bit'][c] for L in Ls])) for c in conds)
    out['N_posto'] = np.zeros((P, 3))
    np.add.at(out['N_posto'], (w_pag, posto), 1.0)
    costo = OrderedDict((c, np.concatenate([L['cost'][c] for L in Ls]).astype(np.float64)) for c in conds)
    out['S_posto'] = OrderedDict()
    for c in conds:
        a = np.zeros((P, 3, 4))
        np.add.at(a, (w_pag, posto), costo[c])
        out['S_posto'][c] = a
    ha = np.concatenate([(L['w_dl_eq'] >= 0) | (L['w_dl_mod'] >= 0) | L['w_mem_eq'] | L['w_mem_mod'] for L in Ls]).astype(float)
    J = np.concatenate([L['w_J'] for L in Ls])
    nl = np.concatenate([L['w_nl'] for L in Ls])
    cl4 = np.where(J == 0, 0, np.where((nl >= 2) & (J == nl - 1), 3, np.where(J == 1, 1, 2)))
    rs = np.concatenate([L['rim_s'] for L in Ls]).astype(np.float64)
    rs = rs.mean(axis=1) if rs.shape[1] else np.zeros(len(w_pag))
    out['rim_posto'] = np.zeros((P, 4))
    out['rim_N'] = np.zeros((P, 4))
    np.add.at(out['rim_posto'], (w_pag, cl4), rs)
    np.add.at(out['rim_N'], (w_pag, cl4), 1.0)
    out['N_eco'] = np.bincount(w_pag, weights=ha, minlength=P)
    out['N_parole'] = np.bincount(w_pag, minlength=P).astype(float)
    out['D_eco'] = OrderedDict((c, np.bincount(w_pag, weights=ha * (costo[c].sum(1) - costo['pieno'].sum(1)), minlength=P)) for c in conds)
    out['D_tutte'] = OrderedDict((c, np.bincount(w_pag, weights=(costo[c].sum(1) - costo['pieno'].sum(1)), minlength=P)) for c in conds)
    out['D_primo'] = OrderedDict((c, np.bincount(w_pag, weights=(costo[c][:, 0] - costo['pieno'][:, 0]), minlength=P)) for c in conds)
    if 'att' in Ls[0]:
        out['att'] = OrderedDict((k, np.concatenate([L['att'][k] for L in Ls], axis=0)) for k in Ls[0]['att'])
    return out


def media_repliche(lista):
    """Media elemento per elemento di piu' repliche (stesse pagine nello stesso ordine)."""
    base = lista[0]
    if len(lista) == 1:
        return base
    for x in lista[1:]:
        assert x['pagine'] == base['pagine'], 'repliche con pagine diverse'
    out = OrderedDict(pagine=base['pagine'], conds=base['conds'], P=base['P'])
    for k, v in base.items():
        if k in out:
            continue
        if isinstance(v, np.ndarray):
            out[k] = np.mean([x[k] for x in lista], axis=0)
        elif isinstance(v, dict):
            out[k] = OrderedDict((kk, np.mean([x[k][kk] for x in lista], axis=0)) for kk in v)
    return out


def carica_stack(var):
    """Le letture di `var` (P2: tutte le repliche, P1: replica 0) su tutte le pieghe disponibili in tutte le repliche. Restituisce (stack medio, liste, pieghe)."""
    reps = REPLICHE17 if var == 'P2' else (0,)
    disponibili = [f for f in PIEGHE17 if all(os.path.exists(percorso_leggi(var, rp, f)) for rp in reps)]
    if not disponibili:
        return None, None, []
    liste = [[carica_leggi(percorso_leggi(var, rp, f)) for f in disponibili] for rp in reps]
    return media_repliche([sposta_per_pagina(ls) for ls in liste]), liste, disponibili


# ---------------------------------------------------------------- statistiche con bootstrap sulle pagine

def rap_boot(num, den):
    """Rapporto di somme sulle pagine (num, den: array (P,)): V con intervallo (bootstrap sulle pagine)."""
    num, den = np.asarray(num, dtype=float), np.asarray(den, dtype=float)
    return I13.val(lambda W: I13.div(W @ num, W @ den), len(num))


def diff_boot(n1, d1, n2, d2):
    n1, d1, n2, d2 = (np.asarray(x, dtype=float) for x in (n1, d1, n2, d2))
    return I13.val(lambda W: I13.div(W @ n1, W @ d1) - I13.div(W @ n2, W @ d2), len(n1))


def etichetta_lift(v):
    ic = v.ic()
    if v.p >= LIFT_SI and ic[0] >= LIFT_SI_BASSO:
        return 'piu\' del caso'
    if v.p <= LIFT_NO and ic[1] <= LIFT_NO_ALTO:
        return 'meno del caso'
    if ic[0] >= LIFT_BANDA[0] and ic[1] <= LIFT_BANDA[1]:
        return 'come il caso'
    return 'zona grigia'


def etichetta_bit(v, soglia=SOGLIA_BIT, base=0.0):
    """'conta' se la differenza (bit per parola) supera di `soglia` la `base` (la stessa differenza nel modello di controllo senza eco, dove la
    memoria non serve: e' l'effetto di un contesto mai visto) con limite basso oltre meta' della soglia; 'non conta' se il limite alto sta sotto."""
    ic = v.ic()
    if v.p >= base + soglia and ic[0] > base + soglia / 2:
        return 'conta'
    if ic[1] < base + soglia:
        return 'non conta'
    return 'zona grigia'


def etichetta_cond(c, v, base):
    """Etichetta di una condizione di lettura. Per le maschere sulle righe e sulla pagina precedente la crescita dei bit mescola 'la rete usava quel
    contesto' e 'la rete e' sorpresa da un contesto mai visto': si dice 'dipende' / 'non dipende', non 'conta'. Per le maschere sull'eco (con il controllo di
    altrettante parole non-eco) vale 'conta' / 'non conta'."""
    e = etichetta_bit(v, SOGLIA_BIT, base)
    if c.startswith(('k', 'senza_prec')):
        return {'conta': 'dipende', 'non conta': 'non dipende'}.get(e, e)
    return e


def con_validita(e, spec, sens, etichette_si, etichette_no):
    """Un'etichetta che dice "c'e' qualcosa" (`etichette_si`) vale se la specificita' dello strumento e' provata; una che dice "non c'e' niente"
    (`etichette_no`) vale se e' provata la sensibilita' (il controllo con l'eco piantata e' riuscito). Altrimenti si scrive perche' non vale."""
    if e in etichette_si and not spec:
        return e + ' (NON VALE: specificità dello strumento non provata)'
    if e in etichette_no and not sens:
        return e + ' (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)'
    return e


def vd(v):
    return None if v is None else v.d()


GRUPPI_DL = OrderedDict([('stessa riga', [0]), ('1-3 righe sopra', [1, 2, 3]), ('vicina (stessa riga e 1-3 sopra)', [0, 1, 2, 3]),
                         ('lontana (4 o piu\' righe sopra)', [4, 5, 6, 7]), ('pagina precedente', [8])])


def lift_eco(att, prefisso, dls, classi=(0, 1, 2), rels=(0, 1, 2)):
    """Sollevamento dell'attenzione sulle parole eco (osservato / atteso su parole non-eco alla stessa distanza), per le classi di distanza in righe
    `dls`, i segni che guardano `classi` e i tipi di eco `rels`, sommando le teste. `prefisso`: 'eco' (parola da scrivere vera) o 'falso'."""
    o = att[prefisso + '_obs'][:, list(classi)][:, :, list(dls)][:, :, :, list(rels)]
    e = att[prefisso + '_att'][:, list(classi)][:, :, list(dls)][:, :, :, list(rels)]
    return rap_boot(o.sum(axis=(1, 2, 3, 4)), e.sum(axis=(1, 2, 3, 4)))


def lift_per_dl(att, prefisso, classi=(0, 1, 2), rels=(0, 1, 2)):
    return OrderedDict((NOME_DL, lift_eco(att, prefisso, [i], classi, rels)) for i, NOME_DL in enumerate(AA.NOMI_DL))


def celle_eco(att, dl, classi=(0, 1, 2), rels=(0, 1, 2)):
    return float(att['eco_nq'][:, list(classi)][:, :, dl][:, :, list(rels)].sum())


def lift_categoria(att, c, cat):
    """Quota di attenzione sulla categoria `cat` per i segni che guardano di classe c, divisa per la quota di segni che sono di quella categoria."""
    massa = att['cat_massa'][:, c, cat].mean(axis=-1) if att['cat_massa'].ndim == 4 else att['cat_massa'][:, c, cat]
    chiavi = att['cat_chiavi'][:, c, cat]
    nq = att['nq'][:, c]
    return rap_boot(massa, nq), rap_boot(chiavi, nq), rap_boot(massa, chiavi)


def profilo_attenzione(att):
    """Quota di attenzione per categoria (media delle teste), con la quota di segni disponibili e il sollevamento, per ogni classe di segno che guarda."""
    out = OrderedDict()
    for c in range(3):
        riga = OrderedDict()
        for k, nome in enumerate(AA.NOMI_CAT):
            q, ks, lf = lift_categoria(att, c, k)
            riga[nome] = OrderedDict(quota_attenzione=vd(q), quota_segni=vd(ks), sollevamento=vd(lf), etichetta=etichetta_lift(lf))
        # prime due righe della pagina (da riga 4 in poi)
        m = att['ini_massa'][:, c].mean(axis=-1) if att['ini_massa'].ndim == 3 else att['ini_massa'][:, c]
        lf = rap_boot(m, att['ini_chiavi'][:, c])
        riga['prime due righe della pagina (da riga 4)'] = OrderedDict(quota_attenzione=vd(rap_boot(m, att['ini_nq'][:, c])), quota_segni=vd(rap_boot(att['ini_chiavi'][:, c], att['ini_nq'][:, c])),
                                                                        sollevamento=vd(lf), etichetta=etichetta_lift(lf))
        out[AA.NOMI_QC[c]] = OrderedDict(segni_che_guardano=float(att['nq'][:, c].sum()), categorie=riga)
    return out


def teste_eco(att):
    """Sollevamento dell'eco per testa (solo punto), per i segni che guardano di inizio parola e tutte le distanze vicine."""
    H = att['eco_obs'].shape[-1]
    out = []
    for h in range(H):
        o = att['eco_obs'][:, :, :4, :, h].sum(axis=(1, 2, 3))
        e = att['eco_att'][:, :, :4, :, h].sum(axis=(1, 2, 3))
        out.append(float(o.sum() / e.sum()) if e.sum() > 0 else None)
    return out


def analisi_attenzione(St):
    att = St['att']
    out = OrderedDict()
    out['profilo'] = profilo_attenzione(att)
    out['eco_per_distanza'] = OrderedDict()
    for nome, pre in (('eco', 'eco'), ('parola da scrivere sbagliata (controllo dello strumento)', 'falso')):
        out['eco_per_distanza'][nome] = OrderedDict((k, OrderedDict(sollevamento=vd(v), celle=celle_eco(att, i), etichetta=etichetta_lift(v)))
                                                    for i, (k, v) in enumerate(lift_per_dl(att, pre).items()))
    out['eco_per_classe'] = OrderedDict()
    for c in range(3):
        out['eco_per_classe'][AA.NOMI_QC[c]] = OrderedDict(
            (g, OrderedDict(sollevamento=vd(lift_eco(att, 'eco', d, (c,))), falso=vd(lift_eco(att, 'falso', d, (c,))))) for g, d in GRUPPI_DL.items())
    out['eco_per_tipo'] = OrderedDict()
    for r, nome in enumerate(AA.NOMI_REL):
        out['eco_per_tipo'][nome] = OrderedDict((g, vd(lift_eco(att, 'eco', d, (0, 1, 2), (r,)))) for g, d in GRUPPI_DL.items())
    out['letture'] = OrderedDict()
    for g, d in GRUPPI_DL.items():
        v = lift_eco(att, 'eco', d)
        vf = lift_eco(att, 'falso', d)
        out['letture'][g] = OrderedDict(sollevamento=vd(v), falso=vd(vf), etichetta=etichetta_lift(v), strumento_ok=bool(vf.ic()[0] >= CT_FALSO[0] and vf.ic()[1] <= CT_FALSO[1]))
    out['sollevamento_per_testa'] = teste_eco(att)
    return out


# ---------------------------------------------------------------- analisi: bit con la memoria ridotta

def analisi_bit(St, nullo=None):
    P = St['P']
    nullo = nullo or {}
    n_par = St['N_parole']
    n_seg = St['n_seg']
    tot = St['bit']
    out = OrderedDict()
    pieno = St['S_posto']['pieno'].sum(axis=(1, 2))
    out['bit_per_segno'] = OrderedDict((c, vd(rap_boot(St['bit'][c], n_seg))) for c in St['conds'])
    out['bit_per_parola'] = OrderedDict((c, vd(rap_boot(St['S_posto'][c].sum(axis=(1, 2)), n_par))) for c in St['conds'])
    out['differenze'] = OrderedDict()
    for c in St['conds']:
        if c == 'pieno':
            continue
        dpar = rap_boot(St['D_tutte'][c], n_par)
        dseg = rap_boot(St['D_tutte'][c], n_seg)
        dprimo = rap_boot(St['D_primo'][c], n_par)
        deco = rap_boot(St['D_eco'][c], St['N_eco'])
        out['differenze'][c] = OrderedDict(nome=NOMI_COND[c], per_parola=vd(dpar), per_segno=vd(dseg), solo_primo_glifo_per_parola=vd(dprimo), parole_con_eco=vd(deco),
                                           base_nulla=nullo.get(c, 0.0), etichetta=etichetta_cond(c, dpar, nullo.get(c, 0.0)))
    out['quota_parole_con_eco'] = float(St['N_eco'].sum() / n_par.sum())
    # caduta per l'eco: togliere le parole eco costa piu' che togliere altrettante parole non-eco (bit per parola, su tutte le parole)
    for nome, a, b in (('caduta_per_eco', 'eco_via', 'ctrl_via'), ('caduta_per_eco_uguale', 'eco_uguale_via', 'ctrl_uguale_via')):
        if a in St['conds']:
            v = diff_boot(St['D_tutte'][a], n_par, St['D_tutte'][b], n_par)
            out[nome] = OrderedDict(per_parola=vd(v), base_nulla=nullo.get(nome, 0.0), etichetta=etichetta_bit(v, SOGLIA_BIT, nullo.get(nome, 0.0)), eco_via=vd(rap_boot(St['D_tutte'][a], n_par)), ctrl_via=vd(rap_boot(St['D_tutte'][b], n_par)))
    # per posto nella riga e per pezzo (prima, interna, ultima parola; primo glifo, interno, ultimo glifo, spazio): bit per parola persi con k0 e senza eco
    out['per_posto_pezzo'] = OrderedDict()
    for c in ('k0', 'senza_prec', 'eco_via', 'ctrl_via'):
        if c not in St['conds']:
            continue
        tab = OrderedDict()
        for ip, np_ in enumerate(('prima parola', 'interne', 'ultima parola')):
            tab[np_] = OrderedDict((pz, vd(rap_boot(St['S_posto'][c][:, ip, jz] - St['S_posto']['pieno'][:, ip, jz], St['N_posto'][:, ip])))
                                   for jz, pz in enumerate(('primo glifo', 'glifi interni', 'ultimo glifo', 'spazio o a capo')))
        out['per_posto_pezzo'][c] = tab
    # i bordi, letti dai bit: quanto pesa la memoria ai bordi della riga (rapporto fra prima/ultima parola e interne)
    out['bordi_bit'] = OrderedDict()
    for c in ('k0', 'eco_via'):
        if c not in St['conds']:
            continue
        d_pos = [St['S_posto'][c][:, i].sum(1) - St['S_posto']['pieno'][:, i].sum(1) for i in range(3)]
        out['bordi_bit'][c] = OrderedDict((nome, vd(rap_boot(d_pos[i], St['N_posto'][:, i]))) for i, nome in enumerate(('prima parola', 'interne', 'ultima parola')))
    # i bordi della riga come in ia13: bit in piu' per parola (solo glifi, appaiati per posto) quando le parole della riga sono rimescolate
    if St['rim_N'].sum() > 0 and St['rim_posto'].any():
        nomi4 = ('prima parola', 'seconda parola', 'dal terzo posto al penultimo', 'ultima parola')
        b = OrderedDict((nomi4[i], vd(rap_boot(St['rim_posto'][:, i], St['rim_N'][:, i]))) for i in range(4))
        r1 = I13.val(lambda W: I13.div(I13.div(W @ St['rim_posto'][:, 0], W @ St['rim_N'][:, 0]), I13.div(W @ St['rim_posto'][:, 2], W @ St['rim_N'][:, 2])), P)
        r2 = I13.val(lambda W: I13.div(I13.div(W @ St['rim_posto'][:, 3], W @ St['rim_N'][:, 3]), I13.div(W @ St['rim_posto'][:, 2], W @ St['rim_N'][:, 2])), P)
        b['R_prima'], b['R_ultima'] = vd(r1), vd(r2)
        out['bordi_ordine'] = b
    # curva della memoria: quanto del risparmio di k0 resta con k righe
    if 'k0' in out['differenze']:
        d0 = out['differenze']['k0']['per_parola']['punto']
        curva = OrderedDict()
        if d0 >= SOGLIA_BIT:                                  # la curva ha senso solo se togliere la memoria costa qualcosa
            for c in ('k1', 'k2', 'k4', 'k8'):
                if c in out['differenze']:
                    curva[c] = out['differenze'][c]['per_parola']['punto'] / d0
        out['curva_memoria'] = OrderedDict(frazione_persa_con_k=curva)
        ent = next((int(c[1:]) for c, f in curva.items() if f <= LIM_K_ECO), None)
        out['curva_memoria']['memoria_entro_k_righe'] = ent if curva else 'non definita (solo la riga costa meno di %s bit per parola)' % nu(SOGLIA_BIT, 2)
    return out


# ---------------------------------------------------------------- analisi: libri con memoria ridotta

def valore_libro(nome, M, Dj):
    r = M.get(nome)
    if r is None:
        return None
    x = MS.copia_netta_lambda(r)
    x['D'] = MS.D_da_pieghe([d['D'][nome] for d in Dj]) if len(Dj) == NF and all(nome in d['D'] for d in Dj) else None
    if x['copia_netta'] is None or x['copia_netta'] < LAM_MIN:          # Λ = 1 - (copia netta mescolata / copia netta): senza eco non e' definita
        x['lam'] = None
    x['bordi'] = r.get('bordi')
    return x


def media_set(xs, chiave):
    return MS.media_es([x[chiave] for x in xs if x is not None])


def analisi_libri(C):
    M = {k[2:]: v for k, v in C.items() if k.startswith('M|')}
    Dj = [C['D|%d' % f] for f in range(NF) if 'D|%d' % f in C]
    out = OrderedDict()
    if 'vere' not in M:
        return out
    Mv = MS.copia_netta_lambda(M['vere'], con_intervallo=True)
    Dv = MS.D_da_pieghe([d['D']['vere'] for d in Dj]) if len(Dj) == NF else None
    vero = OrderedDict(copia_netta=Mv['copia_netta'], copia_netta_ic=Mv['copia_netta_ic'], lam=Mv['lam'], lam_ic=Mv['lam_ic'], contatto=Mv['contatto'], D=Dv,
                       bordi=M['vere'].get('bordi'), bordi_ic=M['vere'].get('bordi_ic'))
    out['vere'] = vero
    insiemi = OrderedDict()
    for s in ['P2'] + list(LIBRI17):
        xs = [valore_libro(n, M, Dj) for n in M if n.split(':')[0] == s]
        xs = [x for x in xs if x is not None]
        if not xs:
            continue
        ins = OrderedDict(libri=len(xs))
        for k in ('copia_netta', 'lam', 'D', 'contatto'):
            ins[k] = media_set(xs, k)
        ins['bordi'] = OrderedDict((b, MS.media_es([x['bordi'][b] for x in xs if x['bordi'] and x['bordi'].get(b) is not None])) for b in (xs[0]['bordi'] or {}))
        insiemi[s] = ins
    out['insiemi'] = insiemi
    # confronto di ogni libro con memoria ridotta con P2 (stesso numero di libri e stessi modelli)
    conf = OrderedDict()
    if 'P2' in insiemi:
        for s in LIBRI17:
            if s not in insiemi:
                continue
            riga = OrderedDict()
            for k in ('copia_netta', 'lam', 'D', 'contatto'):
                a, b = insiemi[s][k], insiemi['P2'][k]
                if a[0] is None or b[0] is None:
                    riga[k] = OrderedDict(lettura='non calcolabile')
                    continue
                d = a[0] - b[0]
                e = math.sqrt((a[1] or 0) ** 2 + (b[1] or 0) ** 2)
                riga[k] = OrderedDict(differenza=d, errore=e, lettura='cala' if d < -SOGLIA_MISURA * e else 'cresce' if d > SOGLIA_MISURA * e else 'uguale entro l\'errore')
            # distanza dei bordi dal vero (media delle sei distanze di JS in valore assoluto)
            if vero['bordi'] and insiemi[s]['bordi'] and insiemi['P2']['bordi']:
                def dist(ins):
                    v = [abs(ins['bordi'][b][0] - vero['bordi'][b]) for b in vero['bordi'] if ins['bordi'].get(b) and ins['bordi'][b][0] is not None and vero['bordi'][b] is not None]
                    return statistics.mean(v) if v else None
                riga['bordi_distanza_dal_vero'] = OrderedDict(imitatore_ablato=dist(insiemi[s]), P2=dist(insiemi['P2']))
            conf[s] = riga
    out['confronto_con_P2'] = conf
    # P2 ha un'eco da perdere?
    if 'P2' in insiemi and vero['copia_netta']:
        a = insiemi['P2']['copia_netta']
        out['P2_ha_eco'] = OrderedDict(copia_netta_P2=a[0], copia_netta_vero=vero['copia_netta'], soglia=ECO_PRESENTE * vero['copia_netta'],
                                       ha_eco=bool(a[0] is not None and a[0] >= ECO_PRESENTE * vero['copia_netta']))
    letture = OrderedDict()
    if conf and out.get('P2_ha_eco'):
        ha = out['P2_ha_eco']['ha_eco']
        for s, nome in (('K0', 'togliere tutto tranne la riga'), ('K1', 'tenere la riga e una sopra'), ('K3', 'tenere la riga e tre sopra'), ('SP', 'togliere la pagina precedente')):
            if s not in conf:
                continue
            r = conf[s]['copia_netta']
            if not ha:
                letture[s] = 'P2 non ha un\'eco da perdere (copia netta di P2 sotto la meta\' del vero): nessuna lettura'
            elif r.get('lettura') == 'non calcolabile':
                letture[s] = 'non calcolabile'
            else:
                a = insiemi[s]['copia_netta'][0]
                letture[s] = ('l\'eco si perde' if (r['lettura'] == 'cala' and a < CALO_ECO * insiemi['P2']['copia_netta'][0]) else
                              'l\'eco cala ma resta' if r['lettura'] == 'cala' else 'l\'eco non cambia' if r['lettura'] == 'uguale entro l\'errore' else 'l\'eco cresce')
    out['letture'] = letture
    return out


# ---------------------------------------------------------------- analisi: regole

def lettura_r2(v):
    ic = v.ic()
    if v.p >= R2_SI and ic[0] >= R2_SI_BASSO:
        return 'spiegano'
    if ic[1] <= R2_NO:
        return 'poco'
    return 'zona grigia'


def confronto_ia13(v, rif):
    ic = v.ic()
    if v.p - rif >= R2_MARGINE and ic[0] >= rif:
        return 'piu\' spiegabile di ia13'
    if v.p - rif <= -R2_MARGINE and ic[1] <= rif:
        return 'meno spiegabile di ia13'
    return 'come ia13 (entro %s)' % nu(R2_MARGINE, 2)


def rielabora_regole(r, rif):
    """Dal risultato di un lavoro `regole` (con oggetti V) a un dizionario di numeri e di letture."""
    if r is None:
        return None
    out = OrderedDict(righe=r['righe'], delta_medio=r['delta_medio'], deviazione=r['deviazione'], soffitto=r['soffitto'], albero8_codici=r['albero8_codici'],
                      domande_principali=r['domande_principali'], migliore_pezzi=r.get('migliore_pezzi'), migliore_eco=r.get('migliore_eco'))
    out['famiglie'] = OrderedDict((k, OrderedDict(gruppo=v['gruppo'], celle=v['celle'], R2=vd(v['R2']), lettura=lettura_r2(v['R2']))) for k, v in r['famiglie'].items())
    out['albero'] = OrderedDict((g, OrderedDict((L, vd(v)) for L, v in d.items())) for g, d in r['albero'].items())
    out['letture'] = OrderedDict()
    a16 = r['albero']['pezzi'][16]
    out['letture']['albero16_pezzi'] = lettura_r2(a16)
    out['letture']['albero16_pezzi_contro_ia13'] = confronto_ia13(a16, rif['albero16'])
    if 'eco' in r['albero']:
        out['letture']['albero16_eco'] = lettura_r2(r['albero']['eco'][16])
        out['letture']['albero16_pezzi_e_eco'] = lettura_r2(r['albero']['pezzi+eco'][16])
    mp = r['famiglie'][r['migliore_pezzi']]['R2']
    out['letture']['migliore_tabella_pezzi'] = lettura_r2(mp)
    out['letture']['migliore_tabella_pezzi_contro_ia13'] = confronto_ia13(mp, rif['migliore_tabella'])
    if r.get('migliore_eco'):
        out['letture']['migliore_tabella_eco'] = lettura_r2(r['famiglie'][r['migliore_eco']]['R2'])
    return out


# ---------------------------------------------------------------- analisi: controlli

def riassunto_lettura(L):
    """Numeri di una lettura (un modello di controllo): sollevamento dell'eco per distanza, bit con le maschere, per il file di corse."""
    St = sposta_per_pagina([L])
    att = St['att']
    out = OrderedDict()
    out['sollevamento'] = OrderedDict((k, OrderedDict(punto=vd(v), celle=celle_eco(att, i))) for i, (k, v) in enumerate(lift_per_dl(att, 'eco').items()))
    out['falso'] = OrderedDict((k, vd(v)) for k, v in lift_per_dl(att, 'falso').items())
    out['eco_massa_per_distanza'] = OrderedDict((k, float(att['eco_obs'][:, :, i].sum())) for i, k in enumerate(AA.NOMI_DL))
    out['bit'] = analisi_bit(St)
    out['pagine'] = St['P']
    return out


def lettura_controllo_positivo(ris):
    """Il controllo positivo: eco piantata a distanza 2, imitatore addestrato su di essa."""
    r = ris['lettura']
    sol = r['sollevamento']
    d2 = sol['2']['punto']
    altre = [sol[k]['punto']['punto'] for k in ('stessa riga', '1', '3') if sol[k]['celle'] >= CT_NEG_CELLE and sol[k]['punto'] is not None and sol[k]['punto']['punto'] == sol[k]['punto']['punto']]
    dif = r['bit']['differenze']
    k12 = dif['k1']['per_parola']['punto'] - dif['k2']['per_parola']['punto']
    k32 = dif['k3']['per_parola']['punto'] - dif['k2']['per_parola']['punto']
    ce = r['bit']['caduta_per_eco']['per_parola']
    rate = ris['righe_copiate']
    o = OrderedDict()
    o['attenzione'] = OrderedDict(sollevamento_a_2=d2, altre_distanze_massimo=max(altre) if altre else None,
                                  riuscito=bool(d2['punto'] >= CT_LIFT_POS and d2['ic'][0] >= CT_LIFT_POS_BASSO and (not altre or d2['punto'] >= CT_ALTRE_DISTANZE * max(altre))))
    o['maschere'] = OrderedDict(bit_k1_meno_k2=k12, bit_k3_meno_k2=k32, caduta_per_eco=ce,
                                riuscito=bool(k12 >= CT_BIT_POS and ce['punto'] >= CT_BIT_POS and ce['ic'][0] >= CT_BIT_POS_BASSO and k32 <= max(CT_BIT_STESSA, CT_BIT_STESSA_REL * k12)))
    p2, k1 = rate['pieno']['2'], rate['K1']['2']
    altre_r = [v for d, v in rate['pieno'].items() if d in ('1', '3', '5') and v is not None]
    rg = ris['regole']
    o['regole'] = OrderedDict(R2_migliore_eco=rg['R2_migliore_eco'], R2_albero16_eco=rg['R2_albero16_eco'], migliore_eco=rg['migliore_eco'],
                              riuscito=bool(rg['R2_migliore_eco']['punto'] >= CT_R2_POS and rg['R2_migliore_eco']['ic'][0] >= CT_R2_POS_BASSO))
    o['libri'] = OrderedDict(quota_righe_copiate_a_2=OrderedDict(pieno=p2, K1=k1, testo=rate['testo_sintetico']['2']), altre_distanze_massimo=max(altre_r) if altre_r else None,
                             riuscito=bool(p2 is not None and k1 is not None and p2 >= CT_LIBRO_POS and k1 <= CT_LIBRO_MASCH and (not altre_r or max(altre_r) <= CT_LIBRO_ALTRE)))
    return o


def lettura_controllo_negativo(ris):
    r = ris['lettura']
    sol = r['sollevamento']
    fuori = OrderedDict()
    ok_att = True
    for k, v in sol.items():
        if v['celle'] >= CT_NEG_CELLE and v['punto'] is not None:
            dentro = v['punto']['ic'][0] >= CT_NEG_BANDA[0] and v['punto']['ic'][1] <= CT_NEG_BANDA[1]
            fuori[k] = OrderedDict(sollevamento=v['punto'], celle=v['celle'], nella_banda=bool(dentro))
            ok_att = ok_att and dentro
    dif = r['bit']['differenze']
    ce = r['bit']['caduta_per_eco']['per_parola']
    k0 = dif['k0']['per_parola']['punto']
    rate = ris['righe_copiate']
    altre_r = [v for d, v in rate['pieno'].items() if v is not None]
    rg = ris['regole']
    r2 = max(rg['R2_migliore_eco']['punto'], rg['R2_albero16_eco']['punto'])
    o = OrderedDict(sollevamento=fuori, caduta_per_eco=ce, bit_k0_meno_pieno=k0, righe_copiate_massimo=max(altre_r) if altre_r else None, R2_regole_eco_massimo=r2)
    o['riuscito_attenzione'] = bool(ok_att and fuori)
    o['riuscito_maschere'] = bool(ce['punto'] <= CT_NEG_BIT)
    o['riuscito_libri'] = bool(not altre_r or max(altre_r) <= CT_LIBRO_ALTRE)
    o['riuscito_regole'] = bool(r2 <= CT_R2_NEG)
    o['riuscito'] = all(o[k] for k in ('riuscito_attenzione', 'riuscito_maschere', 'riuscito_libri', 'riuscito_regole'))
    return o


def controlli(C, att2):
    out = OrderedDict()
    s = C.get('sint|eco_d2')
    n = C.get('sint|senza_eco')
    out['positivo_eco_piantata'] = lettura_controllo_positivo(s) if s else None
    out['negativo_senza_eco'] = lettura_controllo_negativo(n) if n else None
    out['coerenza_scrittura_e_maschera'] = C.get('coerenza')
    rip = C.get('libro|RIPR|1')
    out['riproduzione_ia16'] = OrderedDict(uguale_a_ia16=rip.get('uguale_a_ia16') if rip else None, ia16_presente=rip.get('ia16_presente') if rip else None)
    if att2 is not None:
        L = att2['letture']
        out['strumento_sulle_pagine_vere'] = OrderedDict((g, OrderedDict(falso=x['falso'], riuscito=x['strumento_ok'])) for g, x in L.items())
    pos, neg = out['positivo_eco_piantata'], out['negativo_senza_eco']
    strumento = out.get('strumento_sulle_pagine_vere')
    val = OrderedDict()
    # specificita': lo strumento non vede un'eco dove non c'e'; sensibilita': vede quella piantata (il modello di controllo l'ha imparata)
    val['attenzione_specificita'] = bool(neg and neg['riuscito_attenzione'] and (strumento is None or all(x['riuscito'] for x in strumento.values())))
    val['attenzione_sensibilita'] = bool(pos and pos['attenzione']['riuscito'])
    val['maschere_specificita'] = bool(neg and neg['riuscito_maschere'])
    val['maschere_sensibilita'] = bool(pos and pos['maschere']['riuscito'])
    val['libri'] = bool(out['coerenza_scrittura_e_maschera'] and out['coerenza_scrittura_e_maschera'].get('riuscito') and out['riproduzione_ia16'].get('uguale_a_ia16') is not False)
    val['libri_sensibilita'] = bool(pos and pos['libri']['riuscito'])
    val['regole_specificita'] = bool(neg and neg['riuscito_regole'])
    val['regole_sensibilita'] = bool(pos and pos['regole']['riuscito'])
    out['validita'] = val
    return out


# ---------------------------------------------------------------- sintesi

def ing_ok(ingresso):
    return bool(ingresso.get('disponibile'))


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    ingresso = condizione_ingresso()
    rif = AR.riferimenti_ia13(os.path.join(USCITA, 'ia13_cosa_vede_rete.json'))
    out = OrderedDict(esperimento='ia17', solo_controlli=SOLO_CONTROLLI, versioni=versioni, ingresso=ingresso, errori=errori, taglia=I16.taglia_scelta())
    out['modo'] = 'DESCRIZIONE (ia16 non ha dato un imitatore valido: i numeri descrivono questo modello, non un imitatore che ha superato i controlli)' \
        if ingresso['solo_descrizione'] else 'imitatore valido (ia16)'
    St2, liste2, pieghe2 = carica_stack('P2')
    St1, liste1, pieghe1 = carica_stack('P1')
    out['pieghe_lette'] = OrderedDict(P2=pieghe2, P1=pieghe1)
    out['bit_ia16'] = None
    if ing_ok(ingresso):
        out['bit_ia16'] = json.load(open(ingresso['file'], encoding='utf-8')).get('bpc_medie')
    out['ia13_riferimento'] = rif
    nullo = None
    n_ = C.get('sint|senza_eco')
    if n_:
        nullo = OrderedDict((c, x['per_parola']['punto']) for c, x in n_['lettura']['bit']['differenze'].items())
        for nome_ in ('caduta_per_eco', 'caduta_per_eco_uguale'):
            if nome_ in n_['lettura']['bit']:
                nullo[nome_] = n_['lettura']['bit'][nome_]['per_parola']['punto']
    out['base_nulla'] = nullo
    att2 = analisi_attenzione(St2) if St2 is not None else None
    out['controlli'] = controlli(C, att2)
    val = out['controlli']['validita']
    letture = OrderedDict()
    if St2 is not None:
        out['P2'] = OrderedDict(pagine=St2['P'], attenzione=att2, bit=analisi_bit(St2, nullo))
        L = out['P2']['attenzione']['letture']
        letture['A_dove_guarda_eco'] = OrderedDict((g, con_validita(x['etichetta'], val['attenzione_specificita'], val['attenzione_sensibilita'], ("piu' del caso", 'meno del caso'), ('come il caso',)))
                                                   for g, x in L.items())
        letture['A_mappa'] = OrderedDict()
        for c in (0, 1, 2):
            cat = out['P2']['attenzione']['profilo'][AA.NOMI_QC[c]]['categorie']
            letture['A_mappa'][AA.NOMI_QC[c]] = OrderedDict((k, cat[k]['etichetta']) for k in cat)
        b = out['P2']['bit']
        b = out['P2']['bit']
        letture['B_bit'] = OrderedDict((c, (con_validita(x['etichetta'], val['maschere_specificita'], val['maschere_sensibilita'], ('conta',), ('non conta',))
                                            if not c.startswith(('k', 'senza_prec')) else x['etichetta'] + ' (maschera sulle righe: include l effetto di un contesto mai visto)'))
                                       for c, x in b['differenze'].items() if not c.startswith('ctrl'))
        if 'caduta_per_eco' in b:
            letture['B_caduta_per_eco'] = con_validita(b['caduta_per_eco']['etichetta'], val['maschere_specificita'], val['maschere_sensibilita'], ('conta',), ('non conta',))
        letture['B_memoria_entro_k_righe'] = b.get('curva_memoria', {}).get('memoria_entro_k_righe')
    if St1 is not None:
        out['P1'] = OrderedDict(pagine=St1['P'], attenzione=analisi_attenzione(St1), bit=analisi_bit(St1, nullo))
    libri = analisi_libri(C)
    out['libri'] = libri
    if libri:
        letture['B_libri'] = OrderedDict((s, (t if val['libri'] else 'lettura non valida (coerenza o riproduzione di ia16 non riuscite)')) for s, t in libri.get('letture', {}).items())
    out['regole'] = OrderedDict()
    for var in ('P2', 'P1'):
        r = C.get('regole|%s' % var)
        if r:
            out['regole'][var] = OrderedDict()
            for k, v in r.items():
                if k in ('ordine',) or k.startswith('mem_'):
                    out['regole'][var][k] = rielabora_regole_json(v, rif)
            out['regole'][var]['righe_totali'] = r['righe_totali']
    letture['C_regole'] = OrderedDict()
    for var, d in out['regole'].items():
        for k, v in d.items():
            if isinstance(v, dict) and v.get('letture'):
                letture['C_regole']['%s %s' % (var, k)] = OrderedDict((kk, con_validita(vv, val['regole_specificita'], val['regole_sensibilita'], ('spiegano', "piu' spiegabile di ia13"), ('poco', 'meno spiegabile di ia13')))
                                                                      for kk, vv in v['letture'].items())
    out['letture'] = letture
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('leggi', 'sint', 'libro', 'M', 'D', 'regole'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


class _VJ:
    """Un numero con intervallo letto da un dizionario salvato (punto, ic): stessa interfaccia di I13.V per le etichette."""

    def __init__(self, d):
        self.p, self._ic = d['punto'], d['ic']

    def ic(self):
        return self._ic

    def d(self):
        return OrderedDict(punto=self.p, ic=self._ic)


def rielabora_regole_json(r, rif):
    """Come `rielabora_regole`, ma partendo dalla riga del file di corse (dove i V sono gia' dizionari)."""
    if r is None:
        return None
    wrap = OrderedDict(r)
    wrap['famiglie'] = OrderedDict((k, dict(v, R2=_VJ(v['R2']))) for k, v in r['famiglie'].items())
    wrap['albero'] = OrderedDict((g, OrderedDict((int(L), _VJ(v)) for L, v in d.items())) for g, d in r['albero'].items())
    return rielabora_regole(wrap, rif)


# ---------------------------------------------------------------- il rapporto

def ff(v, d=3):
    if v is None or (isinstance(v, float) and v != v):
        return '—'
    if isinstance(v, (tuple, list)):
        return '%s ± %s' % (nu(v[0], d), nu(v[1], d)) if v[0] is not None else '—'
    if isinstance(v, dict) and 'punto' in v:
        if v['punto'] is None or v['punto'] != v['punto']:
            return '—'
        return '%s (%s; %s)' % (nu(v['punto'], d), nu(v['ic'][0], d), nu(v['ic'][1], d))
    return nu(v, d)


def scrivi_md(o):
    md = ['# IA17 (ia17) — Aprire l\'imitatore', '',
          'Preregistrazione: `preregistrazioni/ia17.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- **Modo: %s.**' % o['modo'],
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()),
          '- Taglia (scelta da ia16): **%s**. Pieghe lette: P2 %s, P1 %s.' % (o['taglia']['taglia'], o['pieghe_lette']['P2'], o['pieghe_lette']['P1']), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    ing = o['ingresso']
    md += ['## Condizione d\'ingresso (varianti di ia16 che hanno superato i loro controlli)', '']
    for v, x in ing['varianti'].items():
        md.append('- %s: %s.' % (v, x['stato']))
    if ing.get('nota'):
        md.append('- %s.' % ing['nota'])
    ct = o['controlli']
    md += ['', '## Controlli', '']
    p = ct['positivo_eco_piantata']
    if p:
        md.append('- **Positivo, eco piantata a 2 righe:** attenzione: sollevamento a 2 righe %s (soglia ≥ %s, limite basso ≥ %s), altre distanze al massimo %s → %s. Maschere: k1 meno k2 %s bit per parola, '
                  'caduta per eco %s (soglia ≥ %s) → %s. Libri: righe copiate a 2 righe %s con memoria piena, %s con k1 (altre distanze al massimo %s) → %s.' % (
                      ff(p['attenzione']['sollevamento_a_2'], 2), nu(CT_LIFT_POS, 1), nu(CT_LIFT_POS_BASSO, 1), nu(p['attenzione']['altre_distanze_massimo'], 2), nu(p['attenzione']['riuscito']),
                      nu(p['maschere']['bit_k1_meno_k2'], 3), ff(p['maschere']['caduta_per_eco']), nu(CT_BIT_POS, 2), nu(p['maschere']['riuscito']),
                      nu(p['libri']['quota_righe_copiate_a_2']['pieno'], 3), nu(p['libri']['quota_righe_copiate_a_2']['K1'], 3), nu(p['libri']['altre_distanze_massimo'], 3), nu(p['libri']['riuscito'])))
    if p:
        md.append('- **Positivo, regole di eco:** la migliore regola di eco (%s) spiega il risparmio di bit della memoria con R² %s (soglia ≥ %s, limite basso ≥ %s); albero a 16 foglie con le sole regole di eco %s → %s.' % (
            p['regole']['migliore_eco'], ff(p['regole']['R2_migliore_eco']), nu(CT_R2_POS, 2), nu(CT_R2_POS_BASSO, 2), ff(p['regole']['R2_albero16_eco']), nu(p['regole']['riuscito'])))
    n = ct['negativo_senza_eco']
    if n:
        md.append('- **Negativo, senza eco:** sollevamenti tutti nella banda %s–%s: %s; caduta per eco %s (soglia ≤ %s); k0 meno pieno %s (descrittivo: effetto di un contesto mai visto, base delle letture dei bit); righe copiate al massimo %s; R² delle regole di eco al massimo %s (soglia ≤ %s) → %s.' % (
            nu(CT_NEG_BANDA[0], 2), nu(CT_NEG_BANDA[1], 2), nu(all(x['nella_banda'] for x in n['sollevamento'].values())), ff(n['caduta_per_eco']), nu(CT_NEG_BIT, 2),
            nu(n['bit_k0_meno_pieno'], 3), nu(n['righe_copiate_massimo'], 3), nu(n['R2_regole_eco_massimo'], 3), nu(CT_R2_NEG, 2), nu(n['riuscito'])))
    if ct.get('strumento_sulle_pagine_vere'):
        md.append('- **Strumento sulle pagine vere (parola da scrivere sbagliata):** ' + '; '.join('%s %s → %s' % (g, ff(x['falso'], 2), nu(x['riuscito'])) for g, x in ct['strumento_sulle_pagine_vere'].items()) + '.')
    co = ct['coerenza_scrittura_e_maschera']
    if co:
        md.append('- **Coerenza scrittura/maschera:** massima differenza %s bit (soglia ≤ %s) → %s.' % (nu(co.get('massimo'), 6), nu(CT_COERENZA, 4), nu(co.get('riuscito'))))
    md.append('- **Riproduzione di ia16:** libro P2 numero 1 riscritto senza maschera: uguale a quello di ia16 → %s.' % nu(ct['riproduzione_ia16']['uguale_a_ia16']))
    v_ = ct['validita']
    md.append("- Validità. Specificità (lo strumento non vede ciò che non c'è; serve a leggere un sì): attenzione %s, maschere %s, regole %s. "
              "Sensibilità (vede l'eco piantata; serve a leggere un no): attenzione %s, maschere %s, regole %s. "
              "Libri (coerenza e riproduzione di ia16): %s; con l'eco piantata nei libri %s." % (
        nu(v_['attenzione_specificita']), nu(v_['maschere_specificita']), nu(v_['regole_specificita']), nu(v_['attenzione_sensibilita']), nu(v_['maschere_sensibilita']),
        nu(v_['regole_sensibilita']), nu(v_['libri']), nu(v_['libri_sensibilita'])))
    if o.get('bit_ia16'):
        md += ['', '## Riferimento: bit per segno dei modelli di ia16 (validazione / fuori piega)', '',
               '; '.join('%s: %s / %s' % (k, ff(v['validazione']), ff(v['fuori'])) for k, v in o['bit_ia16'].items()) + '. Per confronto: le letture sopra con "solo la riga" (k0) sono lo stesso modello P2 con la memoria tolta in lettura, non un modello addestrato senza memoria (R).']
    for var in ('P2', 'P1'):
        if var not in o:
            continue
        x = o[var]
        md += ['', '*%s: stato in ia16 = %s.*' % (var, o['ingresso']['varianti'].get(var, {}).get('stato', '?'))]
        md += ['', '## %s: dove guarda (strati globali; sollevamento = attenzione osservata / attesa su parole non-eco alla stessa distanza)' % var, '',
               '| distanza in righe | sollevamento sull\'eco | con la parola da scrivere sbagliata (controllo) | celle | lettura |', '|---|---|---|---|---|']
        for k, y in x['attenzione']['eco_per_distanza']['eco'].items():
            f = x['attenzione']['eco_per_distanza']['parola da scrivere sbagliata (controllo dello strumento)'][k]
            md.append('| %s | %s | %s | %d | %s |' % (k, ff(y['sollevamento'], 2), ff(f['sollevamento'], 2), y['celle'], y['etichetta']))
        md += ['', 'Per gruppo di distanze: ' + '; '.join('%s %s (%s)' % (g, ff(y['sollevamento'], 2), y['etichetta']) for g, y in x['attenzione']['letture'].items()) + '.',
               'Per testa (distanze vicine): ' + ', '.join(nu(h, 2) for h in x['attenzione']['sollevamento_per_testa']) + '.', '',
               'Per tipo di eco: ' + '; '.join('%s: %s' % (t, ', '.join('%s %s' % (g, ff(v, 2)) for g, v in d.items())) for t, d in x['attenzione']['eco_per_tipo'].items()) + '.', '']
        for qc, d in x['attenzione']['profilo'].items():
            md += ['**Quando indovina: %s** (%d segni che guardano)' % (qc, d['segni_che_guardano']), '', '| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |', '|---|---|---|---|---|']
            for k, y in d['categorie'].items():
                md.append('| %s | %s | %s | %s | %s |' % (k, ff(y['quota_attenzione']), ff(y['quota_segni']), ff(y['sollevamento'], 2), y['etichetta']))
            md.append('')
        b = x['bit']
        md += ['## %s: che cosa succede ai bit se si toglie la memoria (pagine tenute fuori)' % var, '', '| condizione | bit per segno | bit in piu\' per parola | base (controllo senza eco) | in piu\' per segno | solo primo glifo | parole con eco | lettura |', '|---|---|---|---|---|---|---|---|']
        for c, y in b['differenze'].items():
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (y['nome'], ff(b['bit_per_segno'][c]), ff(y['per_parola']), nu(y['base_nulla']), ff(y['per_segno']), ff(y['solo_primo_glifo_per_parola']), ff(y['parole_con_eco']), y['etichetta']))
        md.append('')
        md.append('Memoria piena: %s bit per segno. Quota di parole con un\'eco già scritta (nella pagina o nella coda): %s.' % (ff(b['bit_per_segno']['pieno']), nu(b['quota_parole_con_eco'], 3)))
        for k in ('caduta_per_eco', 'caduta_per_eco_uguale'):
            if k in b:
                md.append('- %s: %s bit per parola (togliere le parole eco meno togliere altrettante non-eco) → %s.' % (k.replace('_', ' '), ff(b[k]['per_parola']), b[k]['etichetta']))
        if 'curva_memoria' in b:
            md.append('- Quota del risparmio di "solo la riga" che si perde con k righe: %s; la memoria utile sta entro %s righe.' % (
                ', '.join('%s %s' % (c, nu(v, 2)) for c, v in b['curva_memoria']['frazione_persa_con_k'].items()), b['curva_memoria']['memoria_entro_k_righe']))
        md.append('')
        if 'bordi_ordine' in b:
            md.append("Bordi della riga letti dall'imitatore (bit in più per parola quando le parole di ogni riga sono rimescolate, solo glifi, appaiati per posto; ia13, GRU sul vero: prima 1,142, ultima -0,581, R_prima 1,28, R_ultima -0,47): " +
                      '; '.join('%s %s' % (k, ff(v, 2)) for k, v in b['bordi_ordine'].items()) + '.')
            md.append('')
        for c, tab in b['per_posto_pezzo'].items():
            md.append('Bit in più per parola con "%s", per posto nella riga e pezzo della parola: ' % NOMI_COND[c] + '; '.join(
                '%s: %s' % (np_, ', '.join('%s %s' % (pz, ff(v)) for pz, v in d.items())) for np_, d in tab.items()) + '.')
        md.append('')
    L = o['libri']
    if L:
        md += ['## Libri scritti con la memoria ridotta (stessi modelli e stessi semi di P2)', '']
        v = L['vere']
        md += ['| testo | n | copia netta | quota locale Λ | D | contatto | ' + ' | '.join(AP_BORDI) + ' |', '|---|---|---|---|---|---|' + '---|' * len(AP_BORDI),
               '| vero | — | %s | %s | %s | %s | %s |' % (nu(v['copia_netta']), nu(v['lam']), nu(v['D']), nu(v['contatto']), ' | '.join(nu(v['bordi'][b], 3) if v['bordi'] else '—' for b in AP_BORDI))]
        for s, ins in L['insiemi'].items():
            md.append('| %s | %d | %s | %s | %s | %s | %s |' % (s, ins['libri'], ff(ins['copia_netta']), ff(ins['lam']), ff(ins['D']), ff(ins['contatto']),
                                                              ' | '.join(ff(ins['bordi'].get(b)) for b in AP_BORDI)))
        md.append('')
        if 'P2_ha_eco' in L:
            md.append('- P2 ha un\'eco da perdere? copia netta di P2 %s contro %s del vero (soglia: metà del vero) → %s.' % (nu(L['P2_ha_eco']['copia_netta_P2']), nu(L['P2_ha_eco']['copia_netta_vero']), nu(L['P2_ha_eco']['ha_eco'])))
        for s, r in L.get('confronto_con_P2', {}).items():
            md.append('- %s contro P2: ' % s + '; '.join('%s %s' % (k, x['lettura']) if 'lettura' in x else '%s: %s' % (k, ', '.join('%s %s' % kv for kv in x.items()))
                                                       for k, x in r.items()) + '.')
        for s, t in L.get('letture', {}).items():
            md.append('- **Lettura %s: %s.**' % (s, t))
        md.append('')
    if o['regole']:
        md += ['## Regole distillate (R² fuori campione, intervallo col bootstrap sulle pagine; ia13: albero a 16 foglie %s, migliore tabella %s, soffitto %s)' % (
            nu(o['ia13_riferimento']['albero16']), nu(o['ia13_riferimento']['migliore_tabella']), nu(o['ia13_riferimento']['soffitto'])), '']
        for var, d in o['regole'].items():
            for k, r in d.items():
                if not isinstance(r, dict):
                    continue
                md.append('**%s, %s** (%d parole): variazione media %s, soffitto %s.' % (var, k, r['righe'], nu(r['delta_medio']), nu(r['soffitto'])))
                md.append('- alberi: ' + '; '.join('%s: %s' % (g, ', '.join('%d foglie %s' % (L_, ff(v)) for L_, v in dd.items())) for g, dd in r['albero'].items()) + '.')
                md.append('- migliore tabella di pezzi: %s (%s); migliore regola di eco: %s.' % (r['migliore_pezzi'], ff(r['famiglie'][r['migliore_pezzi']]['R2']),
                                                                                              (r['migliore_eco'] + ' (%s)' % ff(r['famiglie'][r['migliore_eco']]['R2'])) if r.get('migliore_eco') else '—'))
                md.append('- letture: ' + '; '.join('%s: %s' % kv for kv in r['letture'].items()) + '.')
                md.append('')
    md += ['## Letture preregistrate', '']
    for chiave, x in o['letture'].items():
        md.append('- **%s:** %s' % (chiave, json.dumps(x, ensure_ascii=False, default=str)))
    md += ['', '## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


AP_BORDI = ['inizio_primo', 'inizio_ultimo', 'inizio_lung', 'fine_primo', 'fine_ultimo', 'fine_lung']


# ---------------------------------------------------------------- principale

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
    os.makedirs(CACHE17, exist_ok=True)
    percorso = os.path.join(USCITA, 'ia17_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AKBMRS')
    ing = condizione_ingresso()
    print('ingresso: %s' % '; '.join('%s: %s' % (v, x['stato']) for v, x in ing['varianti'].items()), flush=True)
    if not SOLO_CONTROLLI and not ing['disponibile']:
        raise SystemExit('FERMO: mancano i risultati di ia16 (%s): IA17 parte dopo ia16' % ing['file'])
    indip = [f for f in 'KBA' if f in fasi]              # le fasi K, B e A non dipendono l'una dall'altra: un solo gruppo di processi, i lavori piu' lunghi per primi
    if indip:
        lavori = [a for f in indip for a in lavori_fase(f)]
        print('== fasi %s: %d lavori' % (''.join(indip), len(lavori)), flush=True)
        esegui(lavori, processi, percorso, fatte)
    for fase in 'MR':                                     # M ha bisogno dei libri di B, R delle letture di A
        if fase in fasi:
            lavori = lavori_fase(fase)
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        for k, x in o['letture'].items():
            print('%s: %s' % (k, json.dumps(x, ensure_ascii=False, default=str)[:600]), flush=True)


if __name__ == '__main__':
    main()
