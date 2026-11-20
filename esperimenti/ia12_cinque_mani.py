# -*- coding: utf-8 -*-
"""Esperimento IA12 (ia12): le cinque mani. Le misure di "eco della pagina" (ia09), "grammatica delle famiglie" (ia10) e "contesto"
(ia03) cambiano da mano a mano, oltre la differenza fra lingua A e lingua B?

Preregistrazione: preregistrazioni/ia12.md. Codice di supporto: mani_testi.py (testi, mani, controlli) e mani_stat.py
(misure per gruppo, nulli per permutazione, letture). Riusa per import ia09 (lavoro dei conteggi e modelli di copia), ia10 (famiglie
di parole) e ia03 (GRU a caratteri, k90, GL, GR); nessuno e' modificato.

Che cosa fa il codice (in parole semplici)
- Le pagine vere stanno in gruppi (mano, lingua). Un gruppo e' "leggibile" se ha abbastanza parole e pagine (soglie nella
  preregistrazione); le mani troppo piccole si riportano come "non leggibili".
- Conteggi (ia09, ia10): per ogni coppia di mani della stessa lingua si fanno M SOTTO-TESTI: le pagine delle due mani si scelgono a caso
  fino a Q parole ciascuna (parita' di quantita'), si addestrano i modelli di ia09 e ia10 sulle sole pagine del sotto-testo (le due mani
  pesano uguale, i modelli non conoscono le etichette di mano), e si misurano per mano la copia netta, la quota di copia rho, la quota
  locale Lambda (ia09), g e D delle famiglie (ia10). La differenza fra le due mani si confronta con quella che si ottiene permutando le
  etichette di mano fra le pagine del sotto-testo, tutte insieme (N1) e dentro la stessa sezione (N2).
- Rete (ia03): per ogni gruppo una GRU a caratteri addestrata sul solo testo del gruppo (55.000 segni, sempre la stessa quantita'),
  misure k90, GL, GR; il confronto fra due mani si legge contro "mani finte" (gruppi a caso di pagine della stessa lingua e taglia).
- Controlli: testi con la forma delle vere e parole latine, con "mani" finte uguali (negativi) o con una mano fatta da un processo
  noto diverso (positivi). Le letture valgono solo se i controlli sono superati.

Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia12_cinque_mani.json e .md e, una riga per lavoro,
risultati/ia12_corse.jsonl (con RIPRENDI=1 i lavori fatti non si rifanno).

Variabili (oltre a FASI, FILTRO, RIPRENDI, PROCESSI, SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA e quelle di ia03: PASSI, OGNI, PAZIENZA,
NASCOSTO, CADUTA, LUNG, LOTTO): FASI = conteggi, rete, analisi (predefinito tutte e tre); le nuove, tutte con prefisso MANI_:
MANI_Q (quota di confronto, 0.8), MANI_M (sotto-testi per coppia, 5), MANI_R (permutazioni, 2000), MANI_RGRU (mani finte della rete,
12), MANI_SEMI_GRU (semi della rete per gruppo, 10), MANI_SEMI_GRU_CTRL (semi nei controlli, 5), MANI_RGRU_CTRL (mani finte nei
controlli, 8), MANI_MIN_PAROLE (7000), MANI_MIN_PAGINE (25), MANI_MIN_SEGNI (57000), USCITA_CACHE.
"""
import json, math, os, shutil, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import random
from collections import OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import mani_testi as MT  # noqa: E402
import mani_stat as MS  # noqa: E402
import ia09_dove_sta_sintassi as I9  # noqa: E402
import ia10_famiglie_parole as I10  # noqa: E402
import ia03_contesto as I3  # noqa: E402

NOME = 'ia12_cinque_mani'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF = G.NF
CACHE = os.environ.get('USCITA_CACHE', os.path.join(QUI, '..', 'dati', 'cache', 'ia12', 'uscite'))

Q_QUOTA = float(os.environ.get('MANI_Q', 0.8))
M_SEL = int(os.environ.get('MANI_M', 5))
R_PERM = int(os.environ.get('MANI_R', 2000))
R_GRU = int(os.environ.get('MANI_RGRU', 12))
R_GRU_CTRL = int(os.environ.get('MANI_RGRU_CTRL', 8))
SEMI_GRU = int(os.environ.get('MANI_SEMI_GRU', 10))
SEMI_GRU_CTRL = int(os.environ.get('MANI_SEMI_GRU_CTRL', 5))
MIN_PAROLE = int(os.environ.get('MANI_MIN_PAROLE', 7000))
MIN_PAGINE = int(os.environ.get('MANI_MIN_PAGINE', 25))
MIN_SEGNI = int(os.environ.get('MANI_MIN_SEGNI', 57000))     # la rete usa 55.000 segni (40.000 + 5.000 + 10.000) piu' un margine
SEZ_PAGINE_MIN = 6                                           # pagine per mano in strati con tutte e due le mani, per pareggiare la sezione

TESTI_CONTI = ['vere', 'neg1', 'neg2', 'pos_eco', 'pos_gram', 'pos_loc']
TESTI_GRU = ['vere', 'neg1', 'pos_ctx', 'pos_riga']
# controlli: quale testo valida quale misura (le letture sul Voynich valgono solo se superato)
POSITIVO_PER = OrderedDict([('netto', 'pos_eco'), ('rho', 'pos_eco'), ('lambda', 'pos_loc'), ('g10', 'pos_gram'), ('D10', 'pos_gram'),
                            ('k90', 'pos_ctx'), ('GR', 'pos_riga')])
SOGLIE_GRU = OrderedDict([('k90_interpolato', 1.0), ('GR_corte', 0.03), ('GL', 0.02)])   # differenza minima che conta (segni; bit)
PRIM_GRU = OrderedDict([('k90', 'k90_interpolato'), ('GR', 'GR_corte')])
MISURE_GRU = ['k90', 'k90_interpolato', 'GL', 'GR_corte', 'GR']
PRIM_TUTTE = MS.PRIMARIE + list(PRIM_GRU)


def seme_di(x):
    return G.seme_di(x)


# ---------------------------------------------------------------- gruppi

def gruppi_vere():
    """Gruppi (mano, lingua) della disposizione delle vere (uguale per tutti i testi): pagine, parole, leggibile (conteggi e rete)."""
    b = MT.bundle_vere()
    par = MT.parole_pagina(b)
    segni = {p: sum(len(w) + 1 for _, ws in rows for w in ws) for p, rows in b['pagine'].items()}
    out = OrderedDict()
    for (m, lg), ps in sorted(MT.gruppi(b).items()):
        w = sum(par[p] for p in ps)
        out[(m, lg)] = dict(pagine=ps, n_pagine=len(ps), parole=w, segni=sum(segni[p] for p in ps),
                            leggibile=bool(w >= MIN_PAROLE and len(ps) >= MIN_PAGINE),
                            leggibile_rete=bool(sum(segni[p] for p in ps) >= MIN_SEGNI and len(ps) >= MIN_PAGINE))
    return out


def coppie_di(gr, chiave='leggibile'):
    """Coppie di gruppi leggibili della stessa lingua (mani diverse)."""
    out = []
    for (m1, l1), g1 in gr.items():
        for (m2, l2), g2 in gr.items():
            if l1 == l2 and m1 < m2 and g1[chiave] and g2[chiave]:
                out.append(((m1, l1), (m2, l2)))
    return out


def quota_confronto(gr):
    """Quantita' Q (parole per mano in ogni sotto-testo): quota dell'80% delle parole del gruppo leggibile piu' piccolo, per difetto al centinaio."""
    w = [g['parole'] for g in gr.values() if g['leggibile']]
    return int(math.floor(Q_QUOTA * min(w) / 100.0) * 100) if w else 0


def specifiche_conti(gr, b, solo_primarie=False):
    """Confronti dei conti: id -> dict(lato x, lato y con le pagine, tipo). Primarie: coppie di gruppi leggibili della stessa lingua. Descrittive
    (solo se non solo_primarie): coppie di gruppi leggibili di lingue diverse e tutte le pagine A contro tutte le B."""
    sp = OrderedDict()
    leg = [g for g in gr if gr[g]['leggibile']]
    for i, g1 in enumerate(leg):
        for g2 in leg[i + 1:]:
            if g1[0] == g2[0]:
                continue
            primaria = g1[1] == g2[1]
            if not primaria and solo_primarie:
                continue
            a, c = (g1, g2) if (g1[1], g1[0]) <= (g2[1], g2[0]) else (g2, g1)
            sp['%s%s_%s%s' % (a[0], a[1], c[0], c[1])] = dict(
                tipo='primaria' if primaria else 'descrittiva', x='%s%s' % a, y='%s%s' % c, lingua=a[1] if primaria else None,
                px=list(gr[a]['pagine']), py=list(gr[c]['pagine']))
    if not solo_primarie:
        pa = [p for p in b['pagine'] if b['lingua'][p] == 'A']
        pb = [p for p in b['pagine'] if b['lingua'][p] == 'B']
        if pa and pb:
            sp['A_B'] = dict(tipo='descrittiva', x='tutte A', y='tutte B', lingua=None, px=pa, py=pb)
    return sp


def selezione(spec, pid, m, par, Q):
    """Il sotto-testo m di un confronto: per ogni lato pagine a caso (senza rimpiazzo) finche' si raggiungono Q parole, e pieghe (5, per
    lato, cosi' ogni piega ha pagine di tutte e due le mani). Uguale per tutti i testi (stesse pagine nei controlli)."""
    rnd = random.Random(seme_di('ia12:sel:%s:%d' % (pid, m)))
    sel = {}
    for lato in ('x', 'y'):
        ps = sorted(spec['p' + lato])
        rnd.shuffle(ps)
        out, tot = [], 0
        for p in ps:
            if tot >= Q:
                break
            out.append(p)
            tot += par[p]
        sel[lato] = out
    fold = {}
    for lato in ('x', 'y'):
        ps = sorted(sel[lato])
        random.Random(seme_di('ia12:fold:%s:%d:%s' % (pid, m, lato))).shuffle(ps)
        for i, p in enumerate(ps):
            fold[p] = i % NF
    return sel, fold


def pagine_gruppo(b_layout, gr, grp):
    """Le pagine di un gruppo di rete: 'g|mano|lingua' (gruppo vero) o 'p|k|x|lingua|hA|hB' (mano finta, della taglia di hA; y: di hB)."""
    t = grp.split('|')
    if t[0] == 'g':
        return list(gr[(t[1], t[2])]['pagine'])
    k, lato, lg, hA, hB = int(t[1]), t[2], t[3], t[4], t[5]
    pool = sorted(p for p in b_layout['pagine'] if b_layout['lingua'][p] == lg)
    random.Random(seme_di('ia12:pseudo:%d:%s' % (k, lg))).shuffle(pool)
    par = MT.parole_pagina(b_layout)
    wA, wB = gr[(hA, lg)]['parole'], gr[(hB, lg)]['parole']
    x, y, tot = [], [], 0
    for p in pool:
        if tot < wA:
            x.append(p)
            tot += par[p]
        elif sum(par[q] for q in y) < wB:
            y.append(p)
    return x if lato == 'x' else y


# ---------------------------------------------------------------- lavori

def sotto_testo(job):
    """Registra (in questo processo) il sotto-testo di un lavoro dei conti; restituisce il suo nome."""
    nome, pid, m = job[1], job[2], job[3]
    gr = gruppi_vere()
    b = MT.bundle_vere()
    spec = specifiche_conti(gr, b)[pid]
    sel, fold = selezione(spec, pid, m, MT.parole_pagina(b), quota_confronto(gr))
    return MT.registra_sotto(nome, pid, m, sel['x'] + sel['y'], fold)


def lavoro_conti(job):
    tipo, extra = job[0], job[4]
    inizio = time.time()
    nm = sotto_testo(job)
    if tipo == 'C':
        r = I9.lavoro_C(nm + extra)
        return dict(job=list(job), tipo='C', info=dict(classi=[p['classi'] for p in r['info']['pieghe']]), stat=r['stat'], tempo=round(time.time() - inizio, 1))
    I10.CACHE = os.path.join(CACHE, 'tmp_%d' % os.getpid())
    try:
        r = I10.lavoro_piega(nm, extra)
    finally:
        shutil.rmtree(I10.CACHE, ignore_errors=True)
    return dict(job=list(job), tipo='F', K=r['K'], prova=r['prova'], rim=r['rim'], nulli=[x['pagine'] for x in r['nulli']],
                tempo=round(time.time() - inizio, 1))


def lavoro_rete(job):
    _, nome, grp, seme = job
    inizio = time.time()
    b = MT.bundle(nome)
    gr = gruppi_vere()
    pag = pagine_gruppo(MT.bundle_vere(), gr, grp)
    blocchi = [[ws for _, ws in b['pagine'][p]] for p in pag]
    t = OrderedDict([(nome + '|' + grp, dict(blocchi=blocchi, ruolo='controllo', trasforma=None, speciali=None))])
    I3.SEMI = (seme,)
    lavori, scarti = I3.prepara(t)
    if not lavori:
        return dict(job=list(job), tipo='R', scartato=list(scarti.values())[0] if scarti else 'nessun lavoro', pagine=len(pag), tempo=round(time.time() - inizio, 1))
    c = I3.corsa(lavori[0])
    m = I3.misure_corsa(c, 'B')
    return dict(job=list(job), tipo='R', pagine=len(pag), segni=int(sum(len(I3.e95.flusso(x)) for x in blocchi)),
                misure={k: (None if m[k] is None else float(m[k])) for k in MISURE_GRU}, passi=int(c['passi']), tempo=round(time.time() - inizio, 1))


def lavoro(job):
    try:
        return lavoro_rete(job) if job[0] == 'R' else lavoro_conti(job)
    except Exception as e:  # noqa: BLE001
        return dict(job=list(job), tipo='errore', errore='%s: %s' % (type(e).__name__, str(e)[:300]), tempo=0.0)


def elenco_lavori(fasi):
    gr = gruppi_vere()
    L = []
    if 'rete' in fasi:
        for nome in TESTI_GRU:
            vero = nome == 'vere'
            ns = SEMI_GRU if vero else SEMI_GRU_CTRL
            nr = R_GRU if vero else R_GRU_CTRL
            cp = coppie_di(gr, 'leggibile_rete')
            gruppi_n = [g for g in gr if gr[g]['leggibile_rete']] if vero else sorted({g for c in cp for g in c})
            for g in gruppi_n:
                for s in range(1, ns + 1):
                    L.append(('R', nome, 'g|%s|%s' % g, s))
            for (gA, gB) in cp:
                for k in range(nr):
                    for lato in ('x', 'y'):
                        L.append(('R', nome, 'p|%d|%s|%s|%s|%s' % (k, lato, gA[1], gA[0], gB[0]), 100 + k))
    if 'conteggi' in fasi:
        b = MT.bundle_vere()
        for nome in TESTI_CONTI:
            for pid in specifiche_conti(gr, b, solo_primarie=(nome != 'vere')):
                for m in range(M_SEL):
                    for suff in ('', '~p'):
                        L.append(('C', nome, pid, m, suff))
                    for f in range(NF):
                        L.append(('F', nome, pid, m, f))
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


# ---------------------------------------------------------------- tabelle per pagina

def tabella_testo(per, nome, pid, m):
    """La tabella per pagina di un sotto-testo dai lavori C ('' e '~p') e F (5 pieghe). (None, mancanti) se mancano lavori."""
    chiavi = [('C', nome, pid, m, ''), ('C', nome, pid, m, '~p')] + [('F', nome, pid, m, f) for f in range(NF)]
    if any(k not in per for k in chiavi):
        return None, ['%s' % (k,) for k in chiavi if k not in per]
    d = I9.Dati(dict(job=['C', nome], stat=per[chiavi[0]]['stat'], info=per[chiavi[0]]['info']))
    dp = I9.Dati(dict(job=['C', nome], stat=per[chiavi[1]]['stat'], info=per[chiavi[1]]['info']))
    pag = d.pag
    assert dp.pag == pag, 'pagine diverse fra il testo e la sua versione rimescolata'
    X, R, Nn = {}, {}, defaultdict(list)
    for f in range(NF):
        r = per[('F', nome, pid, m, f)]
        X.update(r['prova'])
        R.update(r['rim'])
        for i, x in enumerate(r['nulli']):
            for p, v in x.items():
                Nn[p].append((i, v))
    nn = {p: np.mean([v for _, v in sorted(l)], axis=0) for p, l in Nn.items()}
    if any(p not in X for p in pag):
        return None, ['pagine senza lavoro di famiglie']
    num = np.zeros((len(pag), len(MS.COLONNE)))
    den = np.zeros((len(pag), 3))
    for c in ('gram', 'g', 'n', 'tutto', 'gram_n', 'b', 'c', 'd', 'e', 'i1', 'cd'):
        num[:, MS.IX[c]] = d.B['w']['U'][:, 0] - d.B['w'][c][:, 0]
    num[:, MS.IX['gp']] = dp.B['w']['U'][:, 0] - dp.B['w']['g'][:, 0]
    num[:, MS.IX['np']] = dp.B['w']['U'][:, 0] - dp.B['w']['n'][:, 0]
    num[:, MS.IX['G0']] = d.fb['w']['U'][:, 0] - d.fb['w']['gram'][:, 0]
    den[:, 0], den[:, 1] = d.n[:, 0], d.fn[:, 0]
    x = np.array([X[p] for p in pag])
    r = np.array([R[p] for p in pag])
    nl = np.array([nn[p] for p in pag])
    num[:, MS.IX['G10']] = x[:, 0]
    num[:, MS.IX['g10']] = x[:, 0] - nl[:, 0]
    num[:, MS.IX['D10']] = x[:, 0] - r[:, 0]
    den[:, 2] = x[:, 1]
    return MS.Tab(pag, num, den, d.n[:, 1]), []


# ---------------------------------------------------------------- analisi dei conti

def num(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


def ms(x):
    """Media e deviazione standard (sui sotto-testi) di una lista che puo' avere NaN."""
    x = np.array([v for v in x if v is not None and not math.isnan(v)], dtype=float)
    return OrderedDict(media=(float(x.mean()) if len(x) else None), ds=(float(x.std(ddof=1)) if len(x) > 1 else None), n=int(len(x)))


def confronta_coppia(per, nome, pid, spec, gr, b, Q):
    """Un confronto di due gruppi di pagine su M sotto-testi: differenza (x meno y), nulli (etichette permutate fra le pagine del sotto-testo;
    dentro la stessa sezione), p, letture, e le misure di ognuno dei due gruppi. Nulli solo per le coppie primarie."""
    par = MT.parole_pagina(MT.bundle_vere())
    obs_m, gx_m, gy_m, n1_m, n2_m, mancano = [], [], [], [], [], []
    primaria = spec['tipo'] == 'primaria'
    cella = defaultdict(lambda: [0, 0])
    for p in spec['px']:
        cella[b['sez'][p]][0] += 1
    for p in spec['py']:
        cella[b['sez'][p]][1] += 1
    mista = sum(min(a, c) for a, c in cella.values())            # pagine delle due mani negli stessi strati (dati completi)
    leggibile2 = bool(primaria and mista >= SEZ_PAGINE_MIN)
    for m in range(M_SEL):
        tab, manc = tabella_testo(per, nome, pid, m)
        if tab is None:
            mancano += manc
            continue
        sel, _ = selezione(spec, pid, m, par, Q)
        sx = set(sel['x'])
        lab = np.array(['x' if p in sx else 'y' for p in tab.nomi])
        v = MS.valori_gruppi(tab, lab, ['x', 'y'])
        gx_m.append(v['x'])
        gy_m.append(v['y'])
        obs_m.append({k: v['x'][k] - v['y'][k] for k in MS.TUTTE})
        if primaria:
            r1 = np.random.default_rng(seme_di('ia12:n1:%s:%s:%d' % (nome, pid, m)))
            n1_m.append(MS.nullo_sel(tab, lab, [np.arange(tab.P)], 'x', 'y', R_PERM, r1))
            if leggibile2:
                cl = defaultdict(list)
                for i, p in enumerate(tab.nomi):
                    cl[b['sez'][p]].append(i)
                r2 = np.random.default_rng(seme_di('ia12:n2:%s:%s:%d' % (nome, pid, m)))
                n2_m.append(MS.nullo_sel(tab, lab, [np.array(x) for x in cl.values()], 'x', 'y', R_PERM, r2))
    if not obs_m:
        return OrderedDict(coppia=pid, mancano=mancano)
    res = OrderedDict()
    for k in MS.TUTTE:
        o = float(MS.aggrega([d[k] for d in obs_m]))
        r = OrderedDict(differenza=num(o), per_sotto_testo=ms([d[k] for d in obs_m]), x=ms([d[k] for d in gx_m]), y=ms([d[k] for d in gy_m]))
        if primaria and k in MS.PRIMARIE:
            nu1 = MS.aggrega([n[k] for n in n1_m]) if len(n1_m) == len(obs_m) else None
            nu2 = MS.aggrega([n[k] for n in n2_m]) if (leggibile2 and len(n2_m) == len(obs_m)) else None
            p1 = MS.p_valore(num(o), nu1)
            p2 = MS.p_valore(num(o), nu2)
            r.update(p_lingua=p1, p_lingua_sezione=p2, minimo=MS.SOGLIE_MINIME[k], esito_grezzo=MS.lettura(num(o), p1, p2, MS.SOGLIE_MINIME[k]),
                     nullo_97=(num(np.nanpercentile(np.abs(nu1), 97.5)) if nu1 is not None and np.isfinite(nu1).any() else None))
        res[k] = r
    return OrderedDict(coppia=pid, tipo=spec['tipo'], x=spec['x'], y=spec['y'], pagine_x=len(spec['px']), pagine_y=len(spec['py']),
                       sotto_testi=len(obs_m), pagine_stesso_strato=int(mista), sezione_pareggiabile=leggibile2, permutazioni=R_PERM,
                       mancano=mancano, misure=res)


# ---------------------------------------------------------------- analisi della rete

def valori_rete(per, nome, grp):
    """Per un gruppo: dict misura -> lista dei valori sui semi (solo corse riuscite)."""
    out = defaultdict(list)
    scarti = []
    for k, r in per.items():
        if k[0] == 'R' and k[1] == nome and k[2] == grp:
            if r.get('scartato'):
                scarti.append(r['scartato'])
                continue
            for m in MISURE_GRU:
                if r['misure'][m] is not None:
                    out[m].append(r['misure'][m])
    return out, scarti


def msd(x):
    x = [v for v in x if v is not None]
    if not x:
        return dict(media=None, ds=None, n=0)
    return dict(media=float(np.mean(x)), ds=float(np.std(x, ddof=1)) if len(x) > 1 else None, n=len(x))


def confronta_rete(per, nome, coppia, nr):
    """Differenza fra due gruppi nelle misure della rete: media sui semi, errore standard, mani finte, esito."""
    (hA, lg), (hB, _) = coppia
    gA, gB = 'g|%s|%s' % coppia[0], 'g|%s|%s' % coppia[1]
    vA, sA = valori_rete(per, nome, gA)
    vB, sB = valori_rete(per, nome, gB)
    out = OrderedDict(coppia='%s%s contro %s%s' % (hA, lg, hB, lg), scarti=sA + sB)
    for m in MISURE_GRU:
        a, bb = msd(vA[m]), msd(vB[m])
        r = OrderedDict(A=a, B=bb)
        dif = None
        if a['n'] >= 2 and bb['n'] >= 2:
            dif = a['media'] - bb['media']
            se = math.sqrt(a['ds'] ** 2 / a['n'] + bb['ds'] ** 2 / bb['n'])
            nul = []
            for k in range(nr):
                x, _ = valori_rete(per, nome, 'p|%d|x|%s|%s|%s' % (k, lg, hA, hB))
                y, _ = valori_rete(per, nome, 'p|%d|y|%s|%s|%s' % (k, lg, hA, hB))
                if x[m] and y[m]:
                    nul.append(abs(x[m][0] - y[m][0]))
            r.update(differenza=dif, errore_standard=se, mani_finte=len(nul), mani_finte_max=(max(nul) if nul else None),
                     mani_finte_97=(float(np.percentile(nul, 97.5)) if nul else None))
        if m in SOGLIE_GRU:
            r['minimo'] = SOGLIE_GRU[m]
            if dif is None:
                r['esito'] = 'non leggibile (corse mancanti o gruppo troppo piccolo)'
            elif abs(dif) < SOGLIE_GRU[m]:
                r['esito'] = 'nessuna differenza misurabile'
            elif abs(dif) > 3 * r['errore_standard'] and r['mani_finte'] >= 5 and abs(dif) > r['mani_finte_max']:
                r['esito'] = 'differiscono'
            else:
                r['esito'] = 'zona grigia'
        out[m] = r
    return out


# ---------------------------------------------------------------- controlli e letture

def e_differiscono(x):
    return isinstance(x, str) and x.startswith('differiscono')


def primarie_di(cs):
    """Le coppie primarie di un testo (dict coppia -> confronto)."""
    return {k: v for k, v in (cs or {}).items() if v.get('tipo') == 'primaria'}


def controlli(conti, rete):
    """conti: testo -> {coppia -> confronto}; rete: testo -> {coppia -> confronto}. Restituisce i controlli e la validita' per misura."""
    c = OrderedDict()
    neg = []
    for t in ('neg1', 'neg2'):
        for cp, x in primarie_di(conti.get(t)).items():
            for k in MS.PRIMARIE:
                neg.append((t, cp, k, x['misure'][k]['esito_grezzo']))
    c['negativo_conti'] = OrderedDict(
        esiti=[list(n) for n in neg], superato=bool(neg and not any(e_differiscono(n[3]) for n in neg)),
        nota='nessuna delle misure dei conti deve dare "differiscono" nei testi latini con mani finte (stessa forma delle vere)')
    negr = []
    for cp, x in rete.get('neg1', {}).items():
        for k, m in PRIM_GRU.items():
            negr.append(('neg1', cp, k, x[m].get('esito')))
    # un controllo negativo con corse mancanti ("non leggibile") non e' superato: nessun esito vuol dire nessuna prova
    c['negativo_rete'] = OrderedDict(esiti=[list(n) for n in negr], superato=bool(negr and not any(e_differiscono(n[3]) or str(n[3]).startswith('non leggibile') for n in negr)))
    valida = OrderedDict()
    for k, t in POSITIVO_PER.items():
        if k in ('k90', 'GR'):
            es = [x[PRIM_GRU[k]].get('esito') for x in rete.get(t, {}).values()]
            neg_ok = c['negativo_rete']['superato']
        else:
            es = [x['misure'][k]['esito_grezzo'] for x in primarie_di(conti.get(t)).values()]
            neg_ok = c['negativo_conti']['superato']
        pos_ok = bool(es and all(e_differiscono(e) for e in es))
        c['positivo_' + k] = OrderedDict(testo=t, esiti=es, superato=pos_ok)
        valida[k] = bool(neg_ok and pos_ok)
    c['valida'] = valida
    return c


# ---------------------------------------------------------------- uscita

def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((str(k), pulisci(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if math.isnan(v) or math.isinf(v) else v
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def f3(x):
    return '-' if x is None else '%+.3f' % x


def scrivi_md(out):
    r = ['# ia12 — le cinque mani', '',
         'Soglie e regole nella preregistrazione `preregistrazioni/ia12.md`. Conti (ia09, ia10): per ogni coppia di mani %d sotto-testi con le stesse parole per mano, '
         'modelli addestrati sul solo sotto-testo; rete (ia03): una rete per gruppo. Solo numeri e aggregati.' % out['parametri']['M'], '']
    r += ['## Gruppi (mano, lingua)', '', '| gruppo | pagine | parole | segni | leggibile (conti) | leggibile (rete) |', '|---|---|---|---|---|---|']
    for g, v in out['gruppi'].items():
        r.append('| %s | %d | %d | %d | %s | %s |' % (g, v['n_pagine'], v['parole'], v['segni'], 'si' if v['leggibile'] else 'no', 'si' if v['leggibile_rete'] else 'no'))
    r += ['', "Pagine con piu' di una mano: %s. Parole per mano in ogni sotto-testo Q: %d; sotto-testi %d; permutazioni %d." % (
        out['disposizione'].get('pagine_miste'), out['parametri']['Q'], out['parametri']['M'], out['parametri']['R'])]
    r += ['', '## Controlli', '']
    for k, v in out['controlli'].items():
        if k == 'valida':
            r.append('- **validita per misura**: ' + ', '.join('%s %s' % (a, 'si' if b else 'NO') for a, b in v.items()))
        else:
            r.append('- %s: %s' % (k, 'superato' if v.get('superato') else 'NON superato'))
    for cp, x in out['conti'].get('vere', {}).items():
        if 'misure' not in x:
            r.append('- vere %s: lavori mancanti' % cp)
            continue
        if x['tipo'] == 'primaria':
            r += ['', '## Voynich, %s (conti, %d sotto-testi)' % (cp, x['sotto_testi']), '',
                  '| misura | %s | %s | differenza (x meno y) | p dentro la lingua | p dentro lingua e sezione | minimo | esito |' % (x['x'], x['y']), '|---|---|---|---|---|---|---|---|']
            for k in MS.PRIMARIE:
                y = x['misure'][k]
                r.append('| %s | %s | %s | %s | %s | %s | %.2f | %s |' % (k, f3(y['x']['media']), f3(y['y']['media']), f3(y['differenza']), '-' if y['p_lingua'] is None else '%.4f' % y['p_lingua'],
                                                                     '-' if y['p_lingua_sezione'] is None else '%.4f' % y['p_lingua_sezione'], y['minimo'], y['esito']))
        else:
            r += ['', '## Voynich, %s (conti, descrittivo: mano e lingua insieme)' % cp, '',
                  '| misura | %s | %s | differenza |' % (x['x'], x['y']), '|---|---|---|---|']
            for k in MS.PRIMARIE + ['A_gram', 'A_cn', 'G0']:
                y = x['misure'][k]
                r.append('| %s | %s | %s | %s |' % (k, f3(y['x']['media']), f3(y['y']['media']), f3(y['differenza'])))
    for cp, x in out['rete'].get('vere', {}).items():
        r += ['', '## Voynich, %s (rete)' % cp, '', '| misura | x | y | differenza | errore standard | mani finte (max) | esito |', '|---|---|---|---|---|---|---|']
        for m in MISURE_GRU:
            y = x[m]
            r.append('| %s | %s | %s | %s | %s | %s | %s |' % (m, f3(y['A']['media']), f3(y['B']['media']), f3(y.get('differenza')), f3(y.get('errore_standard')),
                                                              f3(y.get('mani_finte_max')), y.get('esito', 'descrittiva')))
    if out['rete_gruppi']:
        r += ['', '## Rete, ogni gruppo (media sui semi)', '', '| gruppo | semi | segni | ' + ' | '.join(MISURE_GRU) + ' |', '|---' * (len(MISURE_GRU) + 3) + '|']
        for g, v in out['rete_gruppi'].items():
            r.append('| %s | %d | %s | %s |' % (g, v['k90']['n'], v.get('segni'), ' | '.join(f3(v[m]['media']) for m in MISURE_GRU)))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def analisi(corse, versioni):
    per = {}
    for r in corse:
        if r.get('tipo') == 'errore':
            continue
        per[tuple(r['job'])] = r
    gr = gruppi_vere()
    b = MT.bundle_vere()
    Q = quota_confronto(gr)
    print('gruppi leggibili (conti): %s; Q = %d' % ([g for g in gr if gr[g]['leggibile']], Q), flush=True)
    conti = OrderedDict()
    for nome in TESTI_CONTI:
        conti[nome] = OrderedDict()
        for pid, spec in specifiche_conti(gr, b, solo_primarie=(nome != 'vere')).items():
            t0 = time.time()
            conti[nome][pid] = confronta_coppia(per, nome, pid, spec, gr, b, Q)
            print('conti %s %s: %.0f s' % (nome, pid, time.time() - t0), flush=True)
    rete, rete_gruppi = OrderedDict(), OrderedDict()
    for nome in TESTI_GRU:
        rete[nome] = OrderedDict()
        for cp in coppie_di(gr, 'leggibile_rete'):
            rete[nome]['%s%s_%s%s' % (cp[0][0], cp[0][1], cp[1][0], cp[1][1])] = confronta_rete(per, nome, cp, R_GRU if nome == 'vere' else R_GRU_CTRL)
    for g, v in gr.items():
        if v['leggibile_rete']:
            val, _ = valori_rete(per, 'vere', 'g|%s|%s' % g)
            rete_gruppi['%s%s' % g] = dict({m: msd(val[m]) for m in MISURE_GRU}, segni=v['segni'])
    ctrl = controlli(conti, rete)
    for cp, x in primarie_di(conti.get('vere')).items():
        if 'misure' not in x:
            continue
        for k in MS.PRIMARIE:
            y = x['misure'][k]
            y['esito'] = y['esito_grezzo'] if ctrl['valida'].get(k) else "non leggibile (un controllo non e' superato)"
    for cp, x in rete.get('vere', {}).items():
        for k, m in PRIM_GRU.items():
            if m in x and 'esito' in x[m]:
                x[m]['esito_grezzo'] = x[m]['esito']
                if not ctrl['valida'].get(k):
                    x[m]['esito'] = "non leggibile (un controllo non e' superato)"
    out = OrderedDict(esperimento='ia12', versioni=versioni,
                      parametri=OrderedDict(Q=Q, Q_QUOTA=Q_QUOTA, M=M_SEL, R=R_PERM, R_GRU=R_GRU, R_GRU_CTRL=R_GRU_CTRL, SEMI_GRU=SEMI_GRU, SEMI_GRU_CTRL=SEMI_GRU_CTRL,
                                            MIN_PAROLE=MIN_PAROLE, MIN_PAGINE=MIN_PAGINE, MIN_SEGNI=MIN_SEGNI, ALFA=MS.ALFA_FAM, SOLO_CONTROLLI=SOLO_CONTROLLI,
                                            soglie_minime=MS.SOGLIE_MINIME, soglie_rete=SOGLIE_GRU),
                      disposizione=OrderedDict(pagine_miste=b['miste'], pagine=len(b['pagine'])),
                      gruppi=OrderedDict(('%s%s' % g, OrderedDict((k, v[k]) for k in ('n_pagine', 'parole', 'segni', 'leggibile', 'leggibile_rete'))) for g, v in gr.items()),
                      controlli=ctrl, conti=conti, rete=rete, rete_gruppi=rete_gruppi)
    pulito = pulisci(out)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulito, f, ensure_ascii=False, indent=1)
        f.write('\n')
    righe = scrivi_md(pulito)
    print('\n'.join(righe[:40]), flush=True)
    return pulito


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def avvia_processo():
    I3.avvia_processo()


def main():
    import torch
    import numpy
    import scipy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    fasi = os.environ.get('FASI', 'conteggi,rete,analisi').split(',')
    gr = gruppi_vere()
    print('pagine vere: %d; gruppi: %s' % (len(MT.bundle_vere()['pagine']), ', '.join('%s%s:%dp/%dw%s' % (g[0], g[1], v['n_pagine'], v['parole'], '' if v['leggibile'] else '(no)') for g, v in gr.items())), flush=True)
    percorso = os.path.join(USCITA, 'ia12_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    elif 'conteggi' in fasi or 'rete' in fasi:
        open(percorso, 'w').close()
    if 'conteggi' in fasi or 'rete' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        L = elenco_lavori([f for f in fasi if f in ('conteggi', 'rete')])
        da_fare = [j for j in L if json.dumps(list(j)) not in fatte]
        da_fare.sort(key=lambda j: 0 if j[0] == 'R' else 1)           # prima le reti (le piu' lunghe)
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(L) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 10))
        with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                if r.get('tipo') != 'errore':
                    corse.append(r)
                    with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s)%s' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo'],
                                                          (' ERRORE ' + r['errore']) if r.get('tipo') == 'errore' else ''), flush=True)
    elif os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    if 'analisi' in fasi:
        analisi(corse, versioni)


if __name__ == '__main__':
    main()
