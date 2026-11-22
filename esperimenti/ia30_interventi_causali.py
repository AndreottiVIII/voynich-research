# -*- coding: utf-8 -*-
"""Esperimento IA30 (ia30): gli interventi causali dentro un imitatore.

Domanda: quale informazione dentro l'imitatore produce quale tratto? (il contatto fra parole; l'eco; i bordi della riga; l'ordine delle famiglie)
Realizza la proposta C5 della revisione (REVIEW_FABLE.md) e la proposta 2 di PROPOSTA_METODI_OPUS.md. Non si addestra niente di nuovo sul Voynich: si usano i
modelli gia' addestrati e salvati (M1 e M5 di ia20, E2 di ia22). Si addestrano solo modelli di CONTROLLO su testi sintetici con regole note.
Preregistrazione: preregistrazioni/ia30.md. Moduli: interventi_motore.py (foto della rete, interventi, scambio di stati), interventi_scrittura.py (scrivere
con un intervento, misure leggere), interventi_sintetici.py (testo sintetico a regole note e sua taratura), interventi_letture.py (analisi e letture).

Che cosa fa il codice (in parole semplici)
- Fase C: taratura delle regole piantate sul testo sintetico (contatto, eco, bordi) in modo che le misure diano i valori VERI del manoscritto.
- Fase Q: modelli di controllo addestrati su testi sintetici: `ec` (contatto + eco + bordi, 5 semi: M1 ed E2), `senza` (niente di piantato, 2 semi: M1 ed E2),
  `ord` (ordine delle famiglie piantato, 3 semi: M1).
- Fase A: interventi a livello di previsione (solo passate in avanti, senza scrivere): per ogni modello e ogni intervento, di quanto cambia la previsione delle
  parole che seguono; scambio parziale di stati (dove sta l'informazione); testa di pagina. Sui modelli veri (30) e sui modelli di controllo.
- Fase B: libri scritti con un intervento sulla "percezione" della rete e misure leggere (contatto, eco per distanza, bordi, aderenza della lunghezza di riga).
- Fase M: misure pesanti sui libri (copia netta, Λ, contatto, firma dei bordi); fase D: D di ia10 sui libri delle condizioni sulla parola prima.
- Fase S: sintesi: mappa "informazione -> tratto", controlli, letture preregistrate.
Uscite (solo numeri e aggregati): risultati/ia30_interventi_causali.json e .md e, una riga per lavoro, risultati/ia30_corse.jsonl. Misure, libri e modelli di controllo
in dati/cache/ia30 (protetti: non si committano).

    nohup bash strumenti/coda.sh ia30 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia30" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO22=1 PICCOLO30=1 USCITA=<cartella fuori dal repo> python esperimenti/ia30_interventi_causali.py     (prova sul latino)

Variabili (oltre a quelle di ia07, ia20 e ia22, che si importano): PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere C Q A B M D S; predefinito CQABMDS), FILTRO.
Nuove: CACHE30, PICCOLO30 (solo prove; deve coincidere con PICCOLO20 e PICCOLO22), TIPI30 (sigle separate da -, predefinito M1-E2-M5), NP30 (punti parola per pagina, 6),
NL30 (punti inizio riga per pagina, 3), NH30 (pagine per gli interventi sulla testa di pagina, 5), NPATCH30 (punti con scambio parziale di stati per pagina, 3),
N_LIBRI30 (libri per condizione, 4; 2 per M5), COND30 (solo prove: sottoinsieme delle condizioni, sigle separate da -), SEMI_Q30 (semi dei controlli, 5), EPOCHE_Q30 (60), TAGLIA_Q30 (per le prove: numero di semi dei controlli senza e ord). I valori
predefiniti sono quelli preregistrati. Nessun valore contiene virgole o due punti.
"""
import json, math, os, pickle, random, statistics, sys, time, zlib
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
import ia22_eco_e_legame as I22  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import aprire_parole as AP  # noqa: E402
import interventi_motore as IM  # noqa: E402
import interventi_scrittura as IW  # noqa: E402
import interventi_sintetici as IS  # noqa: E402
import interventi_letture as IL  # noqa: E402

NOME = 'ia30_interventi_causali'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE30 = os.environ.get('CACHE30', os.path.join(USCITA, 'ia30_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia30'))
MOD30, LIBRI30, MISURE30 = os.path.join(CACHE30, 'modelli'), os.path.join(CACHE30, 'libri'), os.path.join(CACHE30, 'misure')
PICCOLO = os.environ.get('PICCOLO30') == '1'
if PICCOLO != I20.PICCOLO or PICCOLO != I22.PICCOLO:
    raise SystemExit('PICCOLO30, PICCOLO20 e PICCOLO22 devono avere lo stesso valore (le prove del codice usano la taglia piccola in tutti e tre)')
TIPI30 = tuple(x for x in os.environ.get('TIPI30', 'M1-E2-M5').split('-') if x in ('M1', 'E2', 'M5'))
NP30 = int(os.environ.get('NP30', 6))
NL30 = int(os.environ.get('NL30', 3))
NH30 = int(os.environ.get('NH30', 5))
NPATCH30 = int(os.environ.get('NPATCH30', 3))
K30 = IM.K_PAROLE
N_LIBRI30 = int(os.environ.get('N_LIBRI30', 4))
SEMI_Q30 = int(os.environ.get('SEMI_Q30', 5))
TAGLIA_Q30 = int(os.environ.get('TAGLIA_Q30', 2))
COND30 = tuple(x for x in os.environ.get('COND30', '').split('-') if x)                       # solo prove: sottoinsieme delle condizioni dei libri
EPOCHE_Q30 = int(os.environ.get('EPOCHE_Q30', 60))
PAZIENZA_Q30 = 10
PIEGHE = I7.PIEGHE
PIEGHE30 = tuple(int(x) for x in os.environ.get('PIEGHE30', '01234') if x.isdigit())      # solo prove del codice: sottoinsieme delle pieghe
REPLICHE30 = tuple(int(x) for x in os.environ.get('REPL30', '01') if x.isdigit())            # solo prove: sottoinsieme delle repliche
CALIB30 = os.path.join(CACHE30, 'calib.json')

# condizioni dei libri (fissate nella preregistrazione)
COND_LIBRI = OrderedDict([
    ('M1', ['base', 'u2', 'p1', 'pw', 'rs_m', 'rs_a', 'hN', 'fill']),
    ('E2', ['base', 'u2', 'p1', 'pw', 'rs_m', 'rs_a', 'hN', 'ptr_off', 'ptr_sopra', 'ptr_d1']),
    ('M5', ['base', 'u2', 'pw', 'rs_a', 'hN', 'ptr_off', 'ptr_sopra'])])
COND_CTRL = OrderedDict([('M1', ['base', 'nul', 'u2', 'p1', 'pw', 'rs_a', 'hN']), ('E2', ['base', 'nul', 'u2', 'p1', 'pw', 'rs_a', 'hN', 'ptr_off'])])
COND_PESANTI = ('base', 'u2', 'p1', 'pw', 'rs_m', 'rs_a', 'hN', 'ptr_off', 'ptr_sopra', 'ptr_d1')    # misure pesanti (copia netta, Λ)
COND_D = ('base', 'u2', 'p1', 'pw')                                                                                  # D di ia10
TESTI_Q = OrderedDict([('ec', dict(tipi=('M1', 'E2'), semi=SEMI_Q30)), ('senza', dict(tipi=('M1', 'E2'), semi=TAGLIA_Q30 - 1)), ('ord', dict(tipi=('M1',), semi=TAGLIA_Q30))])
_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def seme_str(*a):
    return MS.seme_str(*a)


# ---------------------------------------------------------------- calibrazione e testi sintetici

def lavoro_calib():
    """Fase C: la probabilita' di ogni regola piantata tale che la misura sul testo sintetico dia il valore vero (contatto 0,188; copia netta 0,114; firme dei bordi)."""
    inizio = time.time()
    righe, D, voc = I7.libro_vero(), I7.divisore(), I7.vocabolario()
    c = I7.contesto_A()
    unita = voc['unita']
    rows_di = lambda **kw: IS.righe_a_rows(IS.sintetico_regole(righe, 30001, D, unita, **kw), D)
    cr = OrderedDict()
    p_c, v_c, cr['contatto'] = IS.proporzionale(lambda p: R.mi_contatto(rows_di(contatto=p)), IS.VERO_CONTATTO, 0.10, 5)
    p_bi, v_bi, cr['bordi_in'] = IS.bisezione(lambda p: AP.firma_bordi(rows_di(bordi_in=p))['inizio_primo'], IS.VERO_BORDI_INIZIO_PRIMO, 0.0, 1.0, 8)
    p_bf, v_bf, cr['bordi_fi'] = IS.bisezione(lambda p: AP.firma_bordi(rows_di(bordi_fi=p))['fine_ultimo'], IS.VERO_BORDI_FINE_ULTIMO, 0.0, 1.0, 8)

    def copia(p):
        rows = rows_di(eco=p, ritocco=0.5)
        pag = OrderedDict((q, rows[q]) for q in c['ids'] if q in rows)
        return MS.copia_netta_lambda(MS.lavoro_M('ia30calib', pag, {q: c['fold'][q] for q in pag}))['copia_netta']
    p_e, v_e, cr['eco'] = IS.proporzionale(copia, IS.VERO_COPIA_NETTA, 0.012, 5)
    out = OrderedDict([('contatto', p_c), ('eco', p_e), ('bordi_in', p_bi), ('bordi_fi', p_bf), ('ordine', 0.4),
                       ('misura_ottenuta', OrderedDict([('contatto', v_c), ('copia_netta', v_e), ('bordi_inizio_primo', v_bi), ('bordi_fine_ultimo', v_bf)])),
                       ('bersagli', OrderedDict([('contatto', IS.VERO_CONTATTO), ('copia_netta', IS.VERO_COPIA_NETTA), ('bordi_inizio_primo', IS.VERO_BORDI_INIZIO_PRIMO),
                                                 ('bordi_fine_ultimo', IS.VERO_BORDI_FINE_ULTIMO)])),
                       ('cronologia', cr), ('solo_prova', bool(SOLO_CONTROLLI))])
    os.makedirs(CACHE30, exist_ok=True)
    json.dump(out, open(CALIB30, 'w', encoding='utf-8', newline='\n'), indent=1, default=float)
    out['lavoro'] = 'calib'
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def parametri_testo(testo):
    if testo == 'senza':
        return {}
    cal = json.load(open(CALIB30, encoding='utf-8'))
    if testo == 'ec':
        return dict(contatto=cal['contatto'], eco=cal['eco'], ritocco=0.5, bordi_in=cal['bordi_in'], bordi_fi=cal['bordi_fi'])
    if testo == 'ord':
        return dict(ordine=cal['ordine'])
    raise ValueError(testo)


def testo_sintetico(testo, i):
    k = ('sint', testo, i)
    if k not in _C:
        D, voc = I7.divisore(), I7.vocabolario()
        _C[k] = IS.sintetico_regole(I7.libro_vero(), seme_str('ia30sint', testo, i), D, voc['unita'], **parametri_testo(testo))
    return _C[k]


# ---------------------------------------------------------------- modelli: veri (cache di ia20 e ia22) e di controllo

def carica_reale(tipo, k, r):
    kk = ('mod', tipo, k, r)
    if kk not in _C:
        _C[kk] = I22.carica('E2', k, r) if tipo == 'E2' else I20.carica(1 if tipo == 'M1' else 5, k, r)
    return _C[kk]


def percorso_q(testo, tipo, i, est):
    return os.path.join(MOD30, 'ia30_%s_%s_%d%s' % (testo, tipo, i, est))


def carica_q(testo, tipo, i):
    kk = ('modq', testo, tipo, i)
    if kk not in _C:
        voc = I7.vocabolario()
        _C[kk] = (EM if tipo == 'E2' else GM).carica_modello(percorso_q(testo, tipo, i, '.pt'), voc)
    return _C[kk]


def qaddestra(testo, tipo, i):
    """Fase Q: un modello di controllo (piega 0) addestrato su un testo sintetico (semi diversi del testo e del modello)."""
    inizio = time.time()
    voc = I7.vocabolario()
    dps = I20.pagine_sintetiche(testo_sintetico(testo, i))
    tag = 'ia30:%s:%d' % (testo, i)
    seme = 31000 + 100 * list(TESTI_Q).index(testo) + 10 * i + (1 if tipo == 'E2' else 0)

    def messaggio(s):
        try:
            print('[%s %s %d]%s' % (testo, tipo, i, s), flush=True)
        except OSError:
            pass
    if tipo == 'M1':
        ctx, add, val, fuori = I20.pagine_fold(0, 1, dps, tag=tag)
        cfg = GM.cfg_completa(1, voc, ctx, PICCOLO)
        m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_Q30, PAZIENZA_Q30, messaggi=messaggio)
        bv, bf = GM.bpc_pagine(m, ctx, val), GM.bpc_pagine(m, ctx, fuori)
        GM.salva_modello(m, percorso_q(testo, tipo, i, '.pt'), voc['segni'], ctx, dict(testo=testo, tipo=tipo, seme=i, epoca_scelta=scelta))
    else:
        ctx, add, val, fuori = I22.pagine_fold22(0, 'E2', dps, tag=tag)
        cfg = EM.cfg_completa('E2', voc, ctx, PICCOLO)
        m, cv, ca, scelta = EM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_Q30, PAZIENZA_Q30, messaggi=messaggio)
        bv, bf = EM.bpc_pagine(m, ctx, val), EM.bpc_pagine(m, ctx, fuori)
        EM.salva_modello(m, percorso_q(testo, tipo, i, '.pt'), voc['segni'], ctx, dict(testo=testo, tipo=tipo, seme=i, epoca_scelta=scelta))
    return OrderedDict([('lavoro', 'qaddestra|%s|%s|%d' % (testo, tipo, i)), ('testo', testo), ('tipo', tipo), ('seme', i), ('epoche', len(ca)), ('epoca_scelta', scelta),
                        ('arrivata_al_massimo', len(ca) >= EPOCHE_Q30 and scelta > EPOCHE_Q30 - PAZIENZA_Q30), ('bpc_validazione', round(bv, 5)), ('bpc_fuori', round(bf, 5)),
                        ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- sorgenti: modello e pagine

def sorgente(fonte, tipo, k, r):
    """-> (modello, ctx, pagine di addestramento, pagine tenute fuori, pagine tutte). fonte 'reale': k = piega, r = replica; controllo: k = seme (piega 0)."""
    if fonte == 'reale':
        m, ctx = carica_reale(tipo, k, r)
        dp = I16.dati_pagine()
        fold = k
    else:
        m, ctx = carica_q(fonte, tipo, k)
        dp = I20.pagine_sintetiche(testo_sintetico(fonte, k))
        fold = 0
    f_add, f_val, f_fuori = I7.fogli_della_piega(fold)
    add = [d for d in dp.values() if d['foglio'] in set(f_add)]
    fuori = [d for d in dp.values() if d['foglio'] in set(f_fuori)]
    return m, ctx, add, fuori, dp


def lettore(m, ctx, tipo, dp):
    cap = max(len(d['tok']) for d in dp.values()) + 1700
    return IM.Lettore(m, ctx, I7.vocabolario(), tipo, cap)


# ---------------------------------------------------------------- fase A: interventi a livello di previsione

def lavoro_A(fonte, tipo, k, r):
    inizio = time.time()
    m, ctx, add, fuori, dp = sorgente(fonte, tipo, k, r)
    L = lettore(m, ctx, tipo, dp)
    rng = random.Random(seme_str('ia30A', fonte, tipo, k, r))
    don = IM.Donatori(add, ctx)
    sub = list(add)
    rng.shuffle(sub)
    patch = {}
    for nome in IM.NOMI_PATCH:
        patch[nome] = IM.classifica_dimensioni(L, sub[:30], don, rng, nome, 150)
    H = m.cfg['nasc']
    patch['__rnd__'] = {nome: np.random.default_rng(seme_str('ia30rnd', fonte, tipo, k, r, nome)).permutation(H) for nome in IM.NOMI_PATCH}
    per_pagina, testa, patch_tot, npunti = OrderedDict(), OrderedDict(), {}, Counter()
    for d in fuori:
        acc, pc = IM.lavoro_pagina(L, d, don, rng, K30, NP30, NL30, IM.NOMI_PAROLA, IM.NOMI_RIGA, patch=patch, n_patch=NPATCH30)
        per_pagina[d['nome']] = {nome: IM.acc_a_lista(a) for nome, a in acc.items()}
        for kk, v in pc.items():
            t = patch_tot.setdefault('%s|%s' % kk, [0.0, 0.0, 0.0, 0.0, 0])
            for x in range(5):
                t[x] += v[x]
        for nome, a in acc.items():
            npunti[nome] += int(a['N'][:, 0].sum())
    for d in fuori[:NH30]:
        testa[d['nome']] = {nome: IM.acc_a_lista(a) for nome, a in IM.lavoro_testa_pagina(L, d).items()}
    os.makedirs(MISURE30, exist_ok=True)
    out = OrderedDict([('fonte', fonte), ('tipo', tipo), ('k', k), ('r', r), ('per_pagina', per_pagina), ('testa', testa), ('patch', patch_tot),
                       ('ranking_dims', OrderedDict((nome, [int(x) for x in patch[nome][:16]]) for nome in IM.NOMI_PATCH)), ('punti', dict(npunti))])
    json.dump(out, open(percorso_A(fonte, tipo, k, r), 'w', encoding='utf-8', newline='\n'), default=float)
    return OrderedDict([('lavoro', 'A|%s|%s|%d|%d' % (fonte, tipo, k, r)), ('fonte', fonte), ('tipo', tipo), ('k', k), ('r', r), ('pagine', len(fuori)), ('punti', dict(npunti)),
                        ('secondi', round(time.time() - inizio, 1))])


def percorso_A(fonte, tipo, k, r):
    return os.path.join(MISURE30, 'A_%s_%s_%d_%d.json' % (fonte, tipo, k, r))


# ---------------------------------------------------------------- fase B: libri scritti con un intervento

def percorso_libro(fonte, tipo, cond, i):
    return os.path.join(LIBRI30, 'ia30_libro_%s_%s_%s_%d.txt' % (fonte, tipo, cond, i))


def scrivi_libro30(fonte, tipo, cond, i):
    """-> (testo scritto, conta, layout delle righe scritte). Reale: tutto il libro, ogni pagina dal modello della piega che non l'ha vista (replica secondo i). Controllo:
    le sole pagine tenute fuori della piega 0 del testo sintetico."""
    voc, D = I7.vocabolario(), I7.divisore()
    regole = I20.RegoleScrittura(voc)
    rng = np.random.default_rng(seme_str('ia30', fonte, tipo, i))
    rng_h = random.Random(seme_str('ia30h', fonte, tipo, cond, i))
    conta = Counter()
    out, layout = [], []
    if fonte == 'reale':
        righe = I7.libro_vero()
        replica = I7.replica_del_libro(i, n_libri(tipo))
        pg = I7.pieghe()
        pp = I7.per_pagina(righe)
        dp = I16.dati_pagine()
        don = _donatori_reale()
        penne = {}
        for pag, rp in pp.items():
            k = pg[I7.foglio_di(pag)]
            if k not in PIEGHE30:
                continue
            if k not in penne:
                m, ctx = carica_reale(tipo, k, replica)
                penne[k] = lettore(m, ctx, tipo, dp)
            out += IW.scrivi_pagina30(penne[k], cond, regole, rp, voc, D, rng, conta, don, rng_h, pag)
            layout += rp
    else:
        sint = testo_sintetico(fonte, i)
        m, ctx, add, fuori, dp = sorgente(fonte, tipo, i, 0)
        L = lettore(m, ctx, tipo, dp)
        don = IM.Donatori(add, ctx)
        pp = I7.per_pagina(sint)
        nomi = {d['nome'] for d in fuori}
        for pag, rp in pp.items():
            if pag in nomi:
                out += IW.scrivi_pagina30(L, cond, regole, rp, voc, D, rng, conta, don, rng_h, pag)
                layout += rp
    return out, conta, layout


def _donatori_reale():
    if 'don_reale' not in _C:
        m, ctx = carica_reale('M1', 0, 0)
        _C['don_reale'] = IM.Donatori(list(I16.dati_pagine().values()), ctx)
    return _C['don_reale']


def lavoro_libro(fonte, tipo, cond, i):
    inizio = time.time()
    replica = I7.replica_del_libro(i, n_libri(tipo)) if fonte == 'reale' else 0
    os.makedirs(LIBRI30, exist_ok=True)
    percorso = percorso_libro(fonte, tipo, cond, i)
    t, conta, layout = scrivi_libro30(fonte, tipo, cond, i)
    I7.scrivi_file(t, percorso + '.tmp', 'ia30, libro %s %s %s %d' % (fonte, tipo, cond, i), replica)
    os.replace(percorso + '.tmp', percorso)
    assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    D, voc = I7.divisore(), I7.vocabolario()
    rows = IS.righe_a_rows([dict(pagina=p, ini=ini, parole=ps) for p, ini, ps in t], D)
    ris = OrderedDict([('lavoro', 'libro|%s|%s|%s|%d' % (fonte, tipo, cond, i)), ('fonte', fonte), ('tipo', tipo), ('cond', cond), ('i', i), ('replica', replica),
                       ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)), ('conta', OrderedDict(conta))])
    ris['misure'] = IW.misure_leggere(rows, layout, voc, D, t)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def n_libri(tipo):
    """Libri per condizione: 4 (2 per replica) per M1 ed E2, 2 (1 per replica) per M5, che e' il piu' lento."""
    return min(N_LIBRI30, 2) if tipo == 'M5' else N_LIBRI30


def libri_da_fare():
    """Elenco (fonte, tipo, cond, i) dei libri."""
    out = []
    ok = lambda c: not COND30 or c in COND30
    for tipo in TIPI30:
        for cond in COND_LIBRI[tipo]:
            if ok(cond):
                out += [('reale', tipo, cond, i) for i in range(1, n_libri(tipo) + 1)]
        if ok('nul'):
            out.append(('reale', tipo, 'nul', 1))
    for testo, spec in TESTI_Q.items():
        if testo == 'senza':
            continue
        for tipo in spec['tipi']:
            if tipo in TIPI30:
                for cond in (COND_CTRL[tipo] if testo == 'ec' else COND_D):
                    if ok(cond):
                        out += [(testo, tipo, cond, i) for i in range(1, min(3, spec['semi']) + 1)]
    return out


# ---------------------------------------------------------------- fasi M e D: misure pesanti sui libri reali

def nome_libro(fonte, tipo, cond, i):
    return '%s:%s:%s:%d' % (fonte, tipo, cond, i)


def rows_libro(nome):
    fonte, tipo, cond, i = nome.split(':')
    t = I7.leggi_file(percorso_libro(fonte, tipo, cond, int(i)))
    return I7.libro_A_da_righe(t)


def lavoro_M(nome):
    inizio = time.time()
    c = I7.contesto_A()
    if nome == 'vere':
        rows = c['vere']
    else:
        rows = rows_libro(nome)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'M|%s' % nome)])
    r = MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag})
    ris['sintesi'] = MS.copia_netta_lambda(r)
    cp = {p: AP.conti_bordi({p: rr}) for p, rr in pag.items()}
    ris['bordi'] = AP.firma_da_conti(I20.somma_conti(list(cp.values())))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_libri_reali(COND_D):
        testi[n] = rows_libro(n)
    out, info = MS.lavoro_D(f, c, testi)
    return OrderedDict([('lavoro', 'D|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('secondi', round(time.time() - inizio, 1))])


def lavoro_Dc(seme):
    """D di ia10 sul controllo `ord` (ordine delle famiglie piantato): le famiglie si imparano sul testo sintetico stesso (pagine non tenute fuori) e si misura sulle pagine tenute
    fuori della piega 0: il testo piantato e i libri scritti dai modelli di controllo."""
    inizio = time.time()
    D = I7.divisore()
    sint = testo_sintetico('ord', seme)
    rows = IS.righe_a_rows(sint, D)
    dp = I20.pagine_sintetiche(sint)
    f_add, f_val, f_fuori = I7.fogli_della_piega(0)
    fuori = {d['nome'] for d in dp.values() if d['foglio'] in set(f_fuori)}
    c = dict(ids=OrderedDict((p, None) for p in rows), fold={p: (0 if p in fuori else 1) for p in rows}, vere=rows)
    testi = OrderedDict([('vere', rows)])
    for (fonte, tipo, cond, i) in libri_da_fare():
        if fonte == 'ord' and i == seme and os.path.exists(percorso_libro(fonte, tipo, cond, i)):
            testi[nome_libro(fonte, tipo, cond, i)] = rows_libro(nome_libro(fonte, tipo, cond, i))
    out, info = MS.lavoro_D(0, c, testi)
    return OrderedDict([('lavoro', 'Dc|%d' % seme), ('seme', seme), ('famiglie', info), ('D', out), ('secondi', round(time.time() - inizio, 1))])


def nomi_libri_reali(conds=None):
    out = []
    for (fonte, tipo, cond, i) in libri_da_fare():
        if fonte == 'reale' and (conds is None or cond in conds) and os.path.exists(percorso_libro(fonte, tipo, cond, i)):
            out.append(nome_libro(fonte, tipo, cond, i))
    return out


# ---------------------------------------------------------------- esecuzione

def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        tipo = args[0]
        if tipo == 'calib':
            return lavoro_calib()
        if tipo == 'qaddestra':
            return qaddestra(args[1], args[2], int(args[3]))
        if tipo == 'A':
            return lavoro_A(args[1], args[2], int(args[3]), int(args[4]))
        if tipo == 'libro':
            return lavoro_libro(args[1], args[2], args[3], int(args[4]))
        if tipo == 'M':
            return lavoro_M(args[1])
        if tipo == 'D':
            return lavoro_D(int(args[1]))
        if tipo == 'Dc':
            return lavoro_Dc(int(args[1]))
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
                print('[%d/%d %.1f min] %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def lavori_fase(fase):
    if fase == 'C':
        return [('calib',)]
    if fase == 'Q':
        out = []
        for testo, spec in TESTI_Q.items():
            for tipo in spec['tipi']:
                if tipo in TIPI30:
                    out += [('qaddestra', testo, tipo, i) for i in range(1, spec['semi'] + 1)]
        return sorted(out, key=lambda a: (a[2] != 'E2', a[1] != 'ec'))
    if fase == 'A':
        out = [('A', 'reale', t, k, r) for t in ('E2', 'M5', 'M1') if t in TIPI30 for r in REPLICHE30 for k in PIEGHE30]
        for testo, spec in TESTI_Q.items():
            for tipo in spec['tipi']:
                if tipo in TIPI30:
                    out += [('A', testo, tipo, i, 0) for i in range(1, spec['semi'] + 1)]
        return out
    if fase == 'B':
        lst = libri_da_fare()
        ordine = {'M5': 0, 'E2': 1, 'M1': 2}
        lst.sort(key=lambda a: (a[0] != 'reale', ordine.get(a[1], 3), a[2] != 'base'))
        return [('libro',) + tuple(a) for a in lst]
    if fase == 'M':
        nomi = [n for n in nomi_libri_reali(COND_PESANTI)]
        return [('M', 'vere')] + [('M', n) for n in nomi]
    if fase == 'D':
        return [('D', f) for f in range(PIEGHE)] + ([('Dc', i) for i in range(1, TESTI_Q['ord']['semi'] + 1)] if 'M1' in TIPI30 else [])
    return []


def leggi_corse(percorso):
    return I16.leggi_corse(percorso)


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__), ('echi', EM.VERSIONE), ('gradini', GM.VERSIONE)])
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD30, LIBRI30, MISURE30):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni; modelli %s; PICCOLO %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), TIPI30, PICCOLO), flush=True)
    percorso = os.path.join(USCITA, 'ia30_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'CQABMDS')
    for fase in 'CQABMD':
        if fase in fasi:
            lavori = lavori_fase(fase)
            if fase == 'Q' and 'A' in fasi:                                # i modelli di controllo vanno prima: A li legge. Q gira da sola.
                pass
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = IL.analisi(sys.modules[__name__], leggi_corse(percorso), versioni)
        print('sintesi scritta: %s' % o.get('percorso'), flush=True)


if __name__ == '__main__':
    main()
