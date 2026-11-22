# -*- coding: utf-8 -*-
"""Il banco di misure e di giudici di IA26 (modulo di supporto, riusabile): dato un testo, il suo profilo e la sua distanza dal vero.

Che cosa c'e' qui, in parole semplici
- **Le misure** (undici, tutte importate dal codice gia' eseguito, mai riscritte): copia netta e quota locale Λ (ia09), contatto (ia08), ordine delle
  famiglie D (ia10), G9 (giudice 2), firma dei bordi della riga (ia13/ia17: inizio e fine), parole nuove e costo di forma (ia08/ia11), k90 (ia03) e R_rel
  (ia02); in piu', solo descrittive, ρ, GL, GR, Q.
- **I giudici** (sei): e231 ed e266 del paper, K (n-grammi con memoria di pagina, ia11), A (rete GRU a sorpresa, ia01) e due NUOVI mai usati da nessun
  generatore: N (conteggi di n-grammi di glifi dentro la riga + regressione logistica) e KN (Markov di Kneser-Ney a sorpresa); vedi `righello_giudici`.
- **Il metro "vero contro vero"**: le pagine vere divise in due meta' (per foglio, bilanciate per sezione e lingua) molte volte. Per ogni misura la differenza
  fra le due meta' dice quanto due pezzi veri differiscono per puro caso; per ogni giudice l'AUC con etichette a caso fra pagine vere dice quanto un giudice
  "vede" fra due pezzi veri. Le fasce sono quelle di meta' libro (piu' larghe di quelle di un libro intero: la scelta e' prudente per "lontano").
- **La distanza**: per ogni misura z = (valore del testo - valore del vero) / scala, con la scala = deviazione standard della differenza fra meta' vere
  (per i giudici: (AUC - media del nullo) / deviazione standard del nullo); distanza = media di min(|z|, 6) su tutte le misure e i giudici, pesi uguali.
  Si riportano anche la media quadratica e la quota di misure fuori fascia (|z| > 1,96).
- I **lavori** (`lavoro(args)`): una funzione per tipo (M, D, K, KN, J, G, lmA, metro, gm, nullo) che l'orchestratore `ia26_righello_taratura` fa girare in
  parallelo; `profila_testo` li fa girare in fila per un testo solo (comando `python esperimenti/righello_banco.py profilo FILE`).
Un "mondo" e' il libro che fa da vero (di norma `vero`; nella taratura un testo sintetico): `imposta_mondo` lo attiva e va chiamata per prima in ogni
processo. Nessun risultato e' scritto qui, salvo la cache dei modelli di misura (dati/cache/ia26, protetta) e i pickle dei profili dei giudici.
"""
import json
import math
import os
import pickle
import random
import statistics
import sys
import time
from collections import Counter, OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia01_giudice_neurale as G  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import rifarlo_giudici as J  # noqa: E402
import righello_giudici as RG  # noqa: E402
import righello_testi as RT  # noqa: E402

SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE26 = os.environ.get('CACHE26', os.path.join(USCITA, 'ia26_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia26'))
PIEGHE = I7.PIEGHE
S_META = int(os.environ.get('S_META26', 200))              # divisioni a meta' delle pagine vere (misure di conteggio)
S_NULLO = int(os.environ.get('S_NULLO26', 200))            # etichettature a caso per i giudici a profili e per e231/e266
S_NULLO_N = int(os.environ.get('S_NULLO_N26', 60))         # idem per il giudice N (piu' lento)
S_GRU = int(os.environ.get('S_GRU26', 6))                  # divisioni a meta' per k90 e R_rel nel mondo vero (due corse a divisione)
S_GRU_MONDO = int(os.environ.get('S_GRU_MONDO26', 3))      # idem nei mondi della taratura
SEMI_GRU_VERO = tuple(int(x) for x in os.environ.get('SEMI_GRU_VERO26', '123') if x.isdigit())   # semi della rete sul vero (senza virgole: la coda divide le impostazioni sulle virgole)
SEME_GRU = 1                                               # seme della rete per ogni altro testo
CHUNK = int(os.environ.get('CHUNK26', 60))                 # testi per lavoro di D, K e KN
ZMAX, Z95 = 6.0, 1.96
K90_NON_DEFINITO = 255.0                                   # come ia14: il contesto non guadagna niente
BOOT = int(os.environ.get('BOOT', 1000))

MISURE = OrderedDict([('copia_netta', 'copia netta (bit per parola)'), ('lam', 'quota locale Λ'), ('contatto', 'contatto ultimo→primo glifo'),
                      ('D', 'ordine delle famiglie D'), ('G9', 'G9 vocabolario della pagina'), ('bordi_inizio', 'bordi: inizio riga'),
                      ('bordi_fine', 'bordi: fine riga'), ('parole_nuove', 'quota di parole nuove'), ('costo_forma', 'costo di forma delle parole nuove (bit per glifo)'),
                      ('k90', 'k90 (segni di contesto)'), ('R_rel', 'R_rel (mai viste / viste)')])
MISURE_CONTEGGIO = ['copia_netta', 'lam', 'contatto', 'D', 'G9', 'bordi_inizio', 'bordi_fine', 'parole_nuove', 'costo_forma']
MISURE_RETE = ['k90', 'R_rel']
GIUDICI = OrderedDict([('e231', 'giudice 1 (e231)'), ('e266', 'giudice 2 (e266)'), ('K', 'giudice K'), ('A', 'giudice A (rete)'),
                       ('N', 'giudice N (n-grammi, nuovo)'), ('KN', 'giudice KN (Kneser-Ney, nuovo)')])
EXTRA = OrderedDict([('rho', 'ρ quota di copia'), ('GL', 'GL guadagno lungo'), ('GR', 'GR riga sopra'), ('Q', 'Q parole inventate vere')])
DISTANZA_SU = list(MISURE) + list(GIUDICI)

_S = dict(mondo='vero', nomi=[], dir=CACHE26)
_N = {}
_G9 = {}


# ---------------------------------------------------------------- mondo, cartelle, testi

def imposta_mondo(mondo, nomi=None):
    """Da chiamare per prima in ogni processo: attiva il mondo (il libro che fa da vero), le cartelle e l'elenco dei testi (senza `vero`)."""
    RT.attiva_mondo(mondo)
    _S['mondo'] = mondo
    _S['nomi'] = [n for n in (nomi if nomi is not None else RT.catalogo()) if n != 'vero']
    _S['dir'] = os.path.join(CACHE26, mondo)
    for d in ('misure', 'modelli_misura', 'libri', 'giudiceA'):
        os.makedirs(os.path.join(_S['dir'], d), exist_ok=True)
    I7.MODELLI_A = os.path.join(_S['dir'], 'giudiceA')
    return _S


def dir_mondo(*parti):
    return os.path.join(_S['dir'], *parti)


def punta_cartelle(mondo):
    """Solo le cartelle (non attiva il mondo): per leggere in un processo di analisi i risultati e i pickle di un mondo."""
    _S['mondo'] = mondo
    _S['dir'] = os.path.join(CACHE26, mondo)
    return _S['dir']


def esiste_lmA(mondo, seme, piega):
    return os.path.exists(os.path.join(CACHE26, mondo, 'giudiceA', 'ia07_giudiceA_s%d_p%d.pt' % (seme, piega)))


def percorso_libro_tar(tipo, i):
    return dir_mondo('libri', 'tar_%s_%d.txt' % (tipo, i))


def rows_testo(nome):
    """Il testo `nome` del mondo corrente come pagine. `gem` = il gemello del mondo; `tar:TIPO:i` = libro di un imitatore addestrato nel mondo."""
    if nome == 'gem':
        return RT.rows_gemello(_S['mondo'])
    if nome.startswith('tar:'):
        _, tipo, i = nome.split(':')
        p = percorso_libro_tar(tipo, int(i))
        return RT.rows_da_t(I7.leggi_file(p)) if os.path.exists(p) else None
    return RT.rows_di(nome)


def chunk(k):
    nomi = _S['nomi']
    return nomi[k * CHUNK:(k + 1) * CHUNK]


def n_chunk():
    return max(1, -(-len(_S['nomi']) // CHUNK))


def seme_str(*a):
    return MS.seme_str(*a)


# ---------------------------------------------------------------- piccole funzioni

def media_G9(tab):
    nomi, X, nf = tab
    j = next((i for i, n in enumerate(nf) if str(n).startswith('G9 JSD pagina-manoscritto')), None)
    return None if j is None else float(np.mean(np.asarray(X)[:, j]))


def G9_per_pagina(tab):
    nomi, X, nf = tab
    j = next((i for i, n in enumerate(nf) if str(n).startswith('G9 JSD pagina-manoscritto')), None)
    return {} if j is None else {p: float(np.asarray(X)[i, j]) for i, p in enumerate(nomi)}


def somma_conti(lista):
    tot = {g: {f: Counter() for f in ('primo', 'ultimo', 'lung')} for g in ('prima', 'ultima', 'interna')}
    for c in lista:
        for g in tot:
            for f in tot[g]:
                tot[g][f].update(c[g][f])
    return tot


def bordi_da_conti(conti):
    b = AP.firma_da_conti(conti)
    return (statistics.mean(b['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung')), statistics.mean(b['fine_%s' % f] for f in ('primo', 'ultimo', 'lung')))


def pickle_cache(chiave, costruisci):
    """Un oggetto costoso (modello di una piega) dalla cache in dati/cache/ia26, o costruito e salvato (scrittura atomica); se non si puo' salvare, si ricalcola."""
    p = dir_mondo('modelli_misura', chiave + '.pkl')
    if os.path.exists(p):
        try:
            with open(p, 'rb') as f:
                return pickle.load(f)
        except Exception:                                      # noqa: BLE001
            pass
    obj = costruisci()
    try:
        tmp = p + '.%d.tmp' % os.getpid()
        with open(tmp, 'wb') as f:
            pickle.dump(obj, f, protocol=4)
        os.replace(tmp, p)
    except Exception:                                          # noqa: BLE001
        pass
    return obj


# ---------------------------------------------------------------- lavoro M: copia netta, Λ, contatto, G9, bordi

def lavoro_M(nome, rows=None):
    """`rows` (facoltativo): le pagine del testo, se non si leggono dal catalogo (per la calibrazione dei testi sintetici)."""
    inizio = time.time()
    import e266_discriminatore_forte as e266
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vero' and rows is None:
        rows = c['vere']
        g9 = media_G9(k['vt266'])
    else:
        rows = rows if rows is not None else rows_testo(nome)
        g9 = media_G9(e266.tabella(I7.righe_ini(RT.t_da_rows(rows)), k['rif266']))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    r = MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag})
    x = MS.copia_netta_lambda(r)
    bi, bf = bordi_da_conti(somma_conti([AP.conti_bordi({p: rr}) for p, rr in pag.items()]))
    return OrderedDict([('lavoro', 'M|%s' % nome), ('copia_netta', x['copia_netta']), ('lam', x['lam']), ('rho', x['rho']), ('contatto', x['contatto']),
                        ('G9', g9), ('bordi_inizio', bi), ('bordi_fine', bf), ('pagine', len(pag)), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- D e forma, K, KN (per piega e per gruppo di testi)

def modello_D(f, c):
    resto = [p for p in c['ids'] if c['fold'][p] != f]
    random.Random(3964 + 100 * MS.I10.SEME_DIV + f).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    VV = lambda ps: OrderedDict((p, c['vere'][p]) for p in ps)
    return R.FamiglieModello(MS.I10, VV(resto[nval:]), VV(resto[:nval]), K=None, seme=1)


def lavoro_D(f, k):
    """D (ia10) e forma delle parole nuove (ia08/ia11) per la piega f, per i testi del gruppo k (e per `vero` nel gruppo 0)."""
    inizio = time.time()
    c = I7.contesto_A()
    M = pickle_cache('D_f%d' % f, lambda: modello_D(f, c))
    nomi = (['vero'] if k == 0 else []) + chunk(k)
    pv = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] != f)
    cnt = Counter(w for rr in pv.values() for _, ws in rr for w in ws)
    forma, noti = R.Forma(cnt), set(cnt)
    D, fm = OrderedDict(), OrderedDict()
    for nome in nomi:
        rows = c['vere'] if nome == 'vero' else rows_testo(nome)
        if rows is None:
            continue
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        if not pg:
            D[nome], fm[nome] = [0.0, 0.0, 0.0, 0], [0.0, 0.0, 0, 0]
            continue
        P, Rm = R.stat_D(MS.I10, M, pg, seme_str('D16', f, nome), MS.I10.S_RIM)
        D[nome] = [float(P[:, 0].sum()), float(P[:, 1].sum()), float(Rm[:, 0].sum()), len(pg)]
        fm[nome] = R.costo_nuove(forma, pg, noti)
    return OrderedDict([('lavoro', 'D|%d|%d' % (f, k)), ('piega', f), ('D', D), ('forma', fm), ('secondi', round(time.time() - inizio, 1))])


def lavoro_K(f, k):
    """Profili di sorpresa del giudice K (ia11) per la piega f e i testi del gruppo k; salva un pickle in misure/."""
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in chunk(k):
        r = rows_testo(n)
        if r is not None:
            libri[n] = r
    test, val, add = MS.divisione_K(c, f)
    g, info = pickle_cache('K_f%d' % f, lambda: J.scegli_giudice_k([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V']))
    prof = OrderedDict()
    prof['vere'] = OrderedDict((p, G.profilo(c['ids'][p], g.sorpresa(c['ids'][p]))) for p in test)
    for nome, rows in libri.items():
        out = OrderedDict()
        for p in test:
            if p in rows:
                a = G.codifica(rows[p], c['idx'])
                out[p] = G.profilo(a, g.sorpresa(a))
        prof[nome] = out
    with open(dir_mondo('misure', 'K_f%d_c%d.pkl' % (f, k)), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d|%d' % (f, k)), ('scelte_K', info), ('libri', len(libri)), ('secondi', round(time.time() - inizio, 1))])


def lavoro_KN(f, k):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in chunk(k):
        r = rows_testo(n)
        if r is not None:
            libri[n] = r
    info, prof = RG.lavoro_KN(f, c, libri)
    with open(dir_mondo('misure', 'KN_f%d_c%d.pkl' % (f, k)), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'KN|%d|%d' % (f, k)), ('scelte_KN', info), ('libri', len(libri)), ('secondi', round(time.time() - inizio, 1))])


def profili_uniti(prefisso):
    """Profili di tutte le pieghe e di tutti i gruppi (pickle di K o di KN) in un solo dizionario nome -> pagina -> profilo."""
    cart = dir_mondo('misure')
    profs = [pickle.load(open(os.path.join(cart, f), 'rb')) for f in sorted(os.listdir(cart)) if f.startswith(prefisso + '_f') and f.endswith('.pkl')]
    return MS.unisci_profili(profs) if profs else None


# ---------------------------------------------------------------- giudici del paper, A e N (per testo)

def N_vero():
    if 'v' not in _N:
        c = I7.contesto_A()
        nomi = sorted(c['ids'])
        voc = RG.vocabolario_N(c['vere'])
        Xv, pv = RG.matrice_righe_N(c['vere'], nomi, voc)
        _N['v'] = dict(nomi=nomi, voc=voc, Xv=Xv, pv=pv)
    return _N['v']


def lavoro_J(nome):
    inizio = time.time()
    rows = rows_testo(nome)
    out = OrderedDict([('lavoro', 'J|%s' % nome)])
    out.update(I7.giudica(RT.t_da_rows(rows)))
    try:
        out.update(I7.giudice_A(rows))
    except Exception as e:                                     # noqa: BLE001
        out['A_errore'] = repr(e)
    try:
        v = N_vero()
        Xt, pt = RG.matrice_righe_N(OrderedDict((p, rows.get(p, [])) for p in v['nomi']), v['nomi'], v['voc'])
        out['AUC_N'] = RG.auc_N(v['Xv'], v['pv'], Xt, pt, len(v['nomi']))
    except Exception as e:                                     # noqa: BLE001
        out['N_errore'] = repr(e)
    out['secondi'] = round(time.time() - inizio, 1)
    return out


# ---------------------------------------------------------------- k90 e R_rel: reti piccole addestrate sul testo stesso (ia03 e ia02)

def blocchi_di(pagine):
    """Una pagina = un blocco (come in e3c95 e ia14), le righe sono liste di parole."""
    return [[list(ws) for _, ws in rr] for rr in pagine.values()]


def corse_gru(blocchi, nome, tipo, seme):
    import e3c95_imparabilita as e95
    import ia02_parole_mai_viste as I2
    import ia03_contesto as I3
    t = OrderedDict([(nome, dict(blocchi=blocchi, ruolo='generatore', gruppo=nome, trasforma=None, speciali=None))])
    if tipo == 'R':
        e95.SEMI = (seme,)
        lavori, scarti = I2.prepara(t, t)
    else:
        I3.SEMI = (seme,)
        lavori, scarti = I3.prepara(t)
    if scarti or len(lavori) != 1:
        raise RuntimeError('lavoro di rete non preparato: %s' % (scarti,))
    corsa = (I2 if tipo == 'R' else I3).corsa(lavori[0])
    if tipo == 'R':
        x = I2.misure_corsa(corsa)
        return OrderedDict([('R_rel', x['R_rel']), ('Q', x['Q_rete'])])
    x = I3.misure_corsa(corsa, 'B')
    return OrderedDict([('k90', x['k90_interpolato'] if x['k90_interpolato'] is not None else K90_NON_DEFINITO), ('GL', x['GL']), ('GR', x['GR_corte']),
                        ('k90_definito', x['k90_interpolato'] is not None)])


def lavoro_G(tipo, nome, seme):
    inizio = time.time()
    rows = rows_testo(nome)
    ris = OrderedDict([('lavoro', 'G|%s|%s|%d' % (tipo, nome, seme)), ('tipo', tipo), ('nome', nome), ('seme', seme)])
    ris.update(corse_gru(blocchi_di(rows), nome, tipo, seme))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_gm(tipo, s, mezzo):
    """k90 o R_rel su una meta' (mezzo 1 o 2) della divisione `s` delle pagine vere."""
    inizio = time.time()
    tutte = rows_testo('vero')
    h = set(dividi_meta(s, tutte=True)[mezzo - 1])
    pag = OrderedDict((p, rr) for p, rr in tutte.items() if p in h)
    ris = OrderedDict([('lavoro', 'gm|%s|%d|%d' % (tipo, s, mezzo)), ('tipo', tipo), ('s', s), ('mezzo', mezzo), ('pagine', len(pag))])
    ris.update(corse_gru(blocchi_di(pag), 'meta%d_%d' % (s, mezzo), tipo, SEME_GRU))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- metro "vero contro vero"

def pagine_info():
    out = {}
    for x in I7.libro_vero():
        out.setdefault(x['pagina'], (x['foglio'], x['sezione'], x['lingua']))
    return out


def dividi_meta(s, tutte=False):
    """Divisione `s` delle pagine vere (>= 40 parole) in due meta': i FOGLI interi, bilanciati dentro ogni (sezione, lingua), ordine casuale seminato da s.
    -> (pagine della meta' 1, pagine della meta' 2) nell'ordine di `contesto_A()['ids']`; con `tutte`, tutte le pagine del libro (anche quelle corte) dei
    fogli di ogni meta'."""
    c = I7.contesto_A()
    info = pagine_info()
    stratofoglio, pagine_foglio = {}, {}
    for p in c['ids']:
        f, sez, lin = info[p]
        stratofoglio.setdefault(f, (sez, lin))                  # lo strato di un foglio e' quello della sua prima pagina: un foglio sta tutto in una meta'
        pagine_foglio.setdefault(f, []).append(p)
    strati = {}
    for f, st in stratofoglio.items():
        strati.setdefault(st, []).append(f)
    rnd = random.Random(5000 + s)
    f1, f2 = set(), set()
    for st in sorted(strati):
        ff = sorted(strati[st])
        rnd.shuffle(ff)
        off = rnd.randrange(2)
        for i, f in enumerate(ff):
            (f1 if (i + off) % 2 == 0 else f2).add(f)
    if tutte:
        return [p for p in info if info[p][0] in f1], [p for p in info if info[p][0] in f2]
    return [p for p in c['ids'] if info[p][0] in f1], [p for p in c['ids'] if info[p][0] in f2]


def dati_per_pagina_vero():
    """Numeri per pagina del libro vero (copia netta, D, forma, G9, bordi) per le divisioni a meta'."""
    import e266_discriminatore_forte as e266
    c = I7.contesto_A()
    k = I7.riferimenti()
    pag = OrderedDict((p, c['vere'][p]) for p in c['ids'])
    M = MS.lavoro_M('vero', pag, {p: c['fold'][p] for p in pag})
    D, forma = {}, {}
    for f in range(PIEGHE):
        Mf = pickle_cache('D_f%d' % f, lambda f=f: modello_D(f, c))
        pg = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] == f)
        P, Rm = R.stat_D(MS.I10, Mf, pg, seme_str('D16', f, 'vero'), MS.I10.S_RIM)
        pv = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] != f)
        cnt = Counter(w for rr in pv.values() for _, ws in rr for w in ws)
        fo, noti = R.Forma(cnt), set(cnt)
        for i, p in enumerate(pg):
            D[p] = (float(P[i, 0]), float(P[i, 1]), float(Rm[i, 0]))
            forma[p] = R.costo_nuove(fo, OrderedDict([(p, pg[p])]), noti)
    return dict(c=c, pag=pag, M=M, D=D, forma=forma, g9=G9_per_pagina(k['vt266']),
                bordi={p: AP.conti_bordi({p: rr}) for p, rr in pag.items()})


def misure_su(dp, pagine):
    """Le nove misure di conteggio calcolate solo sulle pagine `pagine` (insieme di nomi), dai numeri per pagina."""
    s = set(pagine)
    M = dp['M']
    ix = [i for i, p in enumerate(M['pag']) if p in s]
    sub = {'pag': [M['pag'][i] for i in ix]}
    for kk, v in M.items():
        if kk.startswith('num_') or kk.startswith('den_'):
            sub[kk] = [v[i] for i in ix]
    sub['mi'] = R.mi_contatto(OrderedDict((p, dp['pag'][p]) for p in sub['pag']))
    x = MS.copia_netta_lambda(sub)
    d = [dp['D'][p] for p in sub['pag']]
    f = [dp['forma'][p] for p in sub['pag']]
    bi, bf = bordi_da_conti(somma_conti([dp['bordi'][p] for p in sub['pag']]))
    return OrderedDict([('copia_netta', x['copia_netta']), ('lam', x['lam']), ('contatto', x['contatto']),
                        ('D', (sum(a for a, _, _ in d) - sum(r for _, _, r in d)) / max(sum(b for _, b, _ in d), 1e-12)),
                        ('G9', float(np.mean([dp['g9'][p] for p in sub['pag'] if p in dp['g9']]))), ('bordi_inizio', bi), ('bordi_fine', bf),
                        ('parole_nuove', sum(y[2] for y in f) / max(sum(y[3] for y in f), 1)), ('costo_forma', sum(y[0] for y in f) / max(sum(y[1] for y in f), 1))])


def lavoro_metro():
    """Il valore delle nove misure di conteggio sul libro vero intero e le differenze fra meta' (S_META divisioni)."""
    inizio = time.time()
    dp = dati_per_pagina_vero()
    ids = list(dp['pag'])
    vero = misure_su(dp, ids)
    diffs = OrderedDict((m, []) for m in MISURE_CONTEGGIO)
    for s in range(1, S_META + 1):
        h1, h2 = dividi_meta(s)
        a, b = misure_su(dp, h1), misure_su(dp, h2)
        for m in MISURE_CONTEGGIO:
            diffs[m].append(a[m] - b[m])
    return OrderedDict([('lavoro', 'metro'), ('vero', vero), ('diffs', diffs), ('pagine', len(ids)), ('divisioni', S_META), ('secondi', round(time.time() - inizio, 1))])


def lavoro_nullo(giudice):
    """AUC del giudice con etichette a caso fra pagine vere (meta' e meta'): quanto "vede" un giudice fra due pezzi veri."""
    inizio = time.time()
    n = S_NULLO
    if giudice in ('e231', 'e266'):
        import e231_discriminatore as e231
        k = I7.riferimenti()
        if giudice == 'e266':
            nomi, X, nf = k['vt266']
        else:
            nomi, X, nf = e231.caratteristiche(OrderedDict((p, rr) for p, (_, rr) in k['vpag'].items()), k['rif'])
        prof = {p: X[i] for i, p in enumerate(nomi)}
        aucs = RG.auc_nullo_profili(prof, n, lambda X_, y_, g_: e231.auc_cv(X_, y_, np.array(g_)))
    elif giudice in ('K', 'KN'):
        prof = profili_uniti(giudice)['vere']
        aucs = RG.auc_nullo_profili(prof, n)
    elif giudice == 'A':
        aucs = RG.auc_nullo_profili(I7.profili_vere_A(), n)
    elif giudice == 'N':
        v = N_vero()
        n = S_NULLO_N
        aucs = RG.auc_nullo_N(v['Xv'], v['pv'], len(v['nomi']), n)
    else:
        raise ValueError(giudice)
    return OrderedDict([('lavoro', 'nullo|%s' % giudice), ('giudice', giudice), ('auc', aucs), ('n', n), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- dispatcher

def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        t = args[0]
        if t == 'M':
            return lavoro_M(args[1])
        if t == 'D':
            return lavoro_D(int(args[1]), int(args[2]))
        if t == 'K':
            return lavoro_K(int(args[1]), int(args[2]))
        if t == 'KN':
            return lavoro_KN(int(args[1]), int(args[2]))
        if t == 'J':
            return lavoro_J(args[1])
        if t == 'G':
            return lavoro_G(args[1], args[2], int(args[3]))
        if t == 'gm':
            return lavoro_gm(args[1], int(args[2]), int(args[3]))
        if t == 'lmA':
            r = I7.lavoro_lmA(int(args[1]), int(args[2]))
            return r
        if t == 'metro':
            return lavoro_metro()
        if t == 'nullo':
            return lavoro_nullo(args[1])
        raise ValueError(t)
    except Exception as e:                                     # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def fasi_banco(nomi_testi, con_gru=True, con_vero=True, mondo='vero'):
    """I lavori del banco per i testi `nomi_testi` (senza `vero`) nel mondo corrente, in fasi da far girare una dopo l'altra (dentro una fase l'ordine e'
    libero; i piu' lunghi stanno per primi): 'A' (modelli del testo del giudice A sulle pagine vere), 'B' (tutto il resto), 'N' (nulli dei giudici, che
    leggono i profili di K e KN e i modelli di A)."""
    nk = max(1, -(-len(nomi_testi) // CHUNK))
    fa = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not esiste_lmA(mondo, s, k)] if con_vero else []
    fb = []
    if con_gru:
        if con_vero:
            semi_v = SEMI_GRU_VERO if mondo == 'vero' else SEMI_GRU_VERO[:1]
            n_split = S_GRU if mondo == 'vero' else S_GRU_MONDO
            fb += [('G', tp, 'vero', s) for s in semi_v for tp in ('K', 'R')]
            fb += [('gm', tp, s, m) for s in range(1, n_split + 1) for m in (1, 2) for tp in ('K', 'R')]
        fb += [('G', tp, n, SEME_GRU) for n in nomi_testi for tp in ('K', 'R')]
    fb += [('K', f, k) for k in range(nk) for f in range(PIEGHE)]
    fb += [('KN', f, k) for k in range(nk) for f in range(PIEGHE)]
    fb += [('D', f, k) for k in range(nk) for f in range(PIEGHE)]
    if con_vero:
        fb += [('metro',), ('M', 'vero')]
    fb += [('J', n) for n in nomi_testi]
    fb += [('M', n) for n in nomi_testi]
    fn = [('nullo', j) for j in ('e231', 'e266', 'K', 'KN', 'A', 'N')] if con_vero else []
    return OrderedDict([('A', fa), ('B', fb), ('N', fn)])


# ---------------------------------------------------------------- assemblaggio: riferimento, profili, distanza

def indice_corse(corse):
    return {c['lavoro']: c for c in corse if not c.get('errore')}


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def riferimento_da_corse(C):
    """Il riferimento del vero: valori, scale (deviazione standard delle differenze fra meta'), fasce e nulli dei giudici. `C`: lavoro -> risultato."""
    rif = OrderedDict(vero=OrderedDict(), scala=OrderedDict(), fascia=OrderedDict(), nullo=OrderedDict(), note=[])
    me = C.get('metro')
    if me:
        for m in MISURE_CONTEGGIO:
            d = [x for x in me['diffs'][m] if x is not None and x == x]
            rif['vero'][m] = me['vero'][m]
            rif['scala'][m] = sd(d)
            rif['fascia'][m] = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
        rif['divisioni'] = me['divisioni']
    for m, campo, tipo in (('k90', 'k90', 'K'), ('R_rel', 'R_rel', 'R')):
        vs = [r[campo] for kk, r in C.items() if kk.startswith('G|%s|vero|' % tipo) and r.get(campo) is not None]
        if vs:
            rif['vero'][m] = media(vs)
            rif['seme_sd'] = rif.get('seme_sd', OrderedDict())
            rif['seme_sd'][m] = sd(vs)
        d = []
        for kk, r in C.items():
            if kk.startswith('gm|%s|' % tipo) and kk.endswith('|1'):
                r2 = C.get(kk[:-1] + '2')
                if r2 is not None and r.get(campo) is not None and r2.get(campo) is not None:
                    d.append(r[campo] - r2[campo])
        if len(d) > 1:
            rif['scala'][m] = sd(d)
            rif['fascia'][m] = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))] if len(d) >= 20 else [-Z95 * sd(d), Z95 * sd(d)]
            rif['divisioni_rete'] = len(d)
    for j in GIUDICI:
        x = C.get('nullo|%s' % j)
        if x:
            rif['nullo'][j] = OrderedDict(media=float(np.mean(x['auc'])), sd=float(np.std(x['auc'], ddof=1)), n=x['n'],
                                          q=[float(np.percentile(x['auc'], 2.5)), float(np.percentile(x['auc'], 97.5))])
    return rif


def valori_testo(nome, C, prof_K=None, prof_KN=None, n_pag=None):
    """Il profilo di un testo: misure e AUC dei giudici dai risultati `C` (lavoro -> risultato). Mancante = None."""
    v = OrderedDict((m, None) for m in list(MISURE) + list(GIUDICI) + list(EXTRA))
    x = C.get('M|%s' % nome)
    if x:
        for m in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine', 'rho'):
            v[m] = x[m]
    Ds, Fs = [], []
    for f in range(PIEGHE):
        for kk, d in C.items():
            if kk.startswith('D|%d|' % f) and nome in d['D']:
                Ds.append(d['D'][nome])
                Fs.append(d['forma'][nome])
                break
    if len(Ds) == PIEGHE:
        v['D'] = MS.D_da_pieghe(Ds)
        v['costo_forma'] = sum(y[0] for y in Fs) / max(sum(y[1] for y in Fs), 1)
        v['parole_nuove'] = sum(y[2] for y in Fs) / max(sum(y[3] for y in Fs), 1)
    for tipo, campi in (('K', ('k90', 'GL', 'GR')), ('R', ('R_rel', 'Q'))):
        rs = [r for k, r in C.items() if k.startswith('G|%s|%s|' % (tipo, nome))]
        for cp in campi:
            v[cp] = media([r.get(cp) for r in rs])
    j = C.get('J|%s' % nome)
    if j:
        v['e231'], v['e266'], v['A'], v['N'] = j.get('AUC_e231'), j.get('AUC_e266'), j.get('AUC_A'), j.get('AUC_N')
    if n_pag:
        if prof_K is not None:
            v['K'] = MS.auc_da_profili(prof_K, nome, n_pag)
        if prof_KN is not None:
            v['KN'] = MS.auc_da_profili(prof_KN, nome, n_pag)
    return v


def distanza(v, rif, misure=None, centri=None):
    """Distanza dal vero di un profilo `v`: z per misura (vedi la docstring), media di min(|z|, 6), media quadratica, quota fuori fascia e z per misura.
    `centri` (facoltativo): giudice -> valore dell'AUC da prendere come "uguale al vero" al posto della media del nullo (nei mondi sintetici: l'AUC del gemello,
    quando il gemello sta fuori dal nullo)."""
    zs = OrderedDict()
    for m in (misure or DISTANZA_SU):
        x = v.get(m)
        if x is None:
            continue
        if m in GIUDICI:
            nu = rif['nullo'].get(m)
            if not nu or not nu['sd']:
                continue
            zs[m] = (x - (centri or {}).get(m, nu['media'])) / nu['sd']
        else:
            if m not in rif['vero'] or not rif['scala'].get(m):
                continue
            zs[m] = (x - rif['vero'][m]) / rif['scala'][m]
    if not zs:
        return OrderedDict(distanza=None, rms=None, fuori=None, n=0, z=zs)
    a = [min(abs(z), ZMAX) for z in zs.values()]
    return OrderedDict(distanza=float(np.mean(a)), rms=float(math.sqrt(np.mean([z * z for z in zs.values()]))),
                       fuori=float(np.mean([abs(z) > Z95 for z in zs.values()])), n=len(zs), z=zs)


# ---------------------------------------------------------------- un testo solo: profilo e distanza

def profila_testo(rows, nome='nuovo', riferimento=None, con_gru=True, mondo='vero'):
    """Il profilo e la distanza di un testo nuovo (`rows`: pagine nel formato di ia01, nella disposizione del libro vero). Va chiamata dopo
    `imposta_mondo`; richiede il riferimento (`riferimento.json` scritto dalla corsa del banco) e, per il giudice A, i modelli del vero gia' fatti.
    Fa girare in fila i lavori del banco per questo testo (le pieghe di D e di K si prendono dalla cache dei modelli). -> dict(valori, distanza)."""
    RT._RC[nome] = rows
    _S['nomi'] = [nome]
    rif = riferimento
    if rif is None:
        rif = json.load(open(dir_mondo('riferimento.json'), encoding='utf-8'))
    C = {}
    lav = [('M', nome), ('J', nome)] + [('D', f, 0) for f in range(PIEGHE)] + [('K', f, 0) for f in range(PIEGHE)] + [('KN', f, 0) for f in range(PIEGHE)]
    if con_gru:
        lav += [('G', tp, nome, SEME_GRU) for tp in ('K', 'R')]
    for a in lav:
        r = lavoro(a)
        if r.get('errore'):
            raise RuntimeError('%s: %s' % (r['lavoro'], r['errore']))
        C[r['lavoro']] = r
    n_pag = len(I7.contesto_A()['ids'])
    v = valori_testo(nome, C, profili_uniti('K'), profili_uniti('KN'), n_pag)
    d = distanza(v, rif, [m for m in DISTANZA_SU if con_gru or m not in MISURE_RETE])
    return OrderedDict([('nome', nome), ('valori', v), ('distanza', d)])


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description='Banco di IA26: profilo e distanza dal vero di un testo (libro nel formato del voynichizzatore).')
    ap.add_argument('comando', choices=['profilo'])
    ap.add_argument('file', help='libro: righe "@<pagina.riga> parola.parola" (come i libri di ia07)')
    ap.add_argument('--nome', default='nuovo')
    ap.add_argument('--mondo', default='vero')
    ap.add_argument('--senza-gru', action='store_true', help='salta k90 e R_rel (le due misure con le reti piccole)')
    a = ap.parse_args(argv)
    imposta_mondo(a.mondo, [])
    rows = RT.rows_da_t(I7.leggi_file(a.file))
    r = profila_testo(rows, a.nome, con_gru=not a.senza_gru)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=float))


if __name__ == '__main__':
    main(sys.argv[1:])
