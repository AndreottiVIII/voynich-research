# -*- coding: utf-8 -*-
"""IA25, parte 5 (modulo di supporto): il metro "vero contro vero" (anticipo di C1, versione minima).

Domanda: quanto varia il libro vero da se' stesso, misura per misura (copia netta, Λ, contatto, D, G9, bordi, forma, quota di parole nuove)?
E se "al vero" (ia20-ia24) si legge con questo intervallo, quali verdetti cambiano?

Metodo
- `lavoro_pagine`: UNA volta, i numeri per pagina del libro vero (con le stesse funzioni di ia09, ia10, ia08, ia16, ia17 e gli stessi semi e pieghe di ia20):
  per ogni pagina i numeratori e i denominatori della copia netta e di Λ, le coppie ultimo->primo glifo (nell'ordine vero e con 5 rimescolamenti dentro la
  riga) per il contatto, i punteggi di D (ordine vero e rimescolato), G9, i conti dei bordi, i bit e i glifi delle parole nuove. Salvati in
  `dati/cache/ia25/misure` (protetti: solo numeri).
- `misure_da_pesi`: da quei numeri, le nove misure su QUALUNQUE sottoinsieme (o ricampionamento) delle pagine, senza riaddestrare niente.
- `analisi_vero_vero`: (a) 200 divisioni a caso dei fogli in due meta' (bilanciate per sezione e lingua A/B: ogni gruppo si divide a meta'), per ogni
  misura la differenza meta' A meno meta' B e la deviazione standard "del libro intero" = sd(A - B) / 2; (b) 1000 ricampionamenti delle pagine e 1000 dei
  fogli: deviazione standard e intervallo al 95%; (c) sigma del vero = il maggiore dei tre; (d) quante coppie di meta' sarebbero "al vero" fra loro con la
  regola del 5% di ia20; (e) il controllo: la differenza fra lingua A e lingua B (che sappiamo grande) contro l'intervallo.
- `rileggi`: i valori di ia20-ia24 (risultati/*.json, solo numeri) riletti con "al vero" = entro 2 sigma combinate (sigma del vero e errore dei libri):
  quali verdetti cambiano rispetto alla regola di ia20 (entro 2 errori dei libri o entro il 5%).
"""
import math
import os
import pickle
import random
import statistics
import time
from collections import Counter, OrderedDict, defaultdict

import numpy as np

import verifiche_comune as C
import rifarlo_ritocchi as R
import aprire_parole as AP

I7, I10, I16, I20, MS, A9 = C.I7, C.MS.I10, C.I16, C.I20, C.MS, C.A9

MISURE = ['copia_netta', 'lam', 'contatto', 'D', 'G9', 'bordi_inizio', 'bordi_fine', 'parole_nuove', 'costo_forma']
NSPLIT = int(os.environ.get('NSPLIT25', 200))
NBOOT = int(os.environ.get('NBOOT25', 1000))
SOGLIE = OrderedDict([
    ('sigma_vero', 'il maggiore fra: sd(meta\' A - meta\' B)/2 sulle divisioni, sd del ricampionamento delle pagine, sd del ricampionamento dei fogli'),
    ('al_vero_nuovo', 'distanza dal vero <= 2 * radice(sigma_vero^2 + errore dei libri^2)'),
    ('accordo_boot_split', (0.5, 2.0)),             # controllo: sd dei fogli ricampionati / sd dalle divisioni deve stare qui
    ('lingua_AB_misure_viste', 3),                  # controllo positivo: almeno 3 misure su 9 distano fra A e B oltre 3 sigma
    ('lingua_AB_sigma', 3.0),
    ('media_divisioni_su_sigma', 0.25),             # controllo negativo: la media di (A - B) sulle divisioni sta entro 0,25 deviazioni standard dallo zero
    ('contatto_per_pagina_tol', 0.005)])            # il contatto da conti per pagina coincide con mi_contatto sul testo intero entro questo
CONTI_BORDI = [('prima', 'inizio'), ('ultima', 'fine')]
FEAT = ('primo', 'ultimo', 'lung')


def percorso_pagine():
    return os.path.join(C.MISURE25, 'vero_pagine.pkl')


# ---------------------------------------------------------------- numeri per pagina del libro vero

def _coppie(rows, rnd=None):
    ws = [list(w) for _, w in rows]
    out = Counter()
    for w in ws:
        if rnd is not None:
            rnd.shuffle(w)
        for a, b in zip(w, w[1:]):
            out[(a[-1], b[0])] += 1
    return out


def lavoro_pagine():
    inizio = time.time()
    import e266_discriminatore_forte as e266
    C.crea_cartelle()
    c = I7.contesto_A()
    k = I7.riferimenti()
    pagine = sorted(c['ids'])
    rows = c['vere']
    # copia netta e Λ (ia09, riferimento pagina a caso: lo stesso di ia20 per 'vere')
    r = C.struttura_M('vere', rows, '0')
    assert list(r['pag']) == pagine
    num = {ch + '_' + m_: np.array(r['num_%s_%s' % (ch, m_)], dtype=float) for ch in ('t', 'p') for m_ in MS.MODELLI_M}
    den = {ch: np.array(r['den_' + ch], dtype=float) for ch in ('t', 'p')}
    # contatto: coppie per pagina, nell'ordine vero e con 5 rimescolamenti dentro la riga (semi fissi per pagina)
    base = {p: _coppie(rows[p]) for p in pagine}
    shuf = [{p: _coppie(rows[p], random.Random(C.seme_str('ia25mi', s, p))) for p in pagine} for s in range(5)]
    chiavi = sorted({kk for d in [base] + shuf for cn in d.values() for kk in cn}, key=str)
    ix = {kk: i for i, kk in enumerate(chiavi)}
    nb = np.zeros((len(pagine), len(chiavi)))
    ns = np.zeros((5, len(pagine), len(chiavi)))
    for j, p in enumerate(pagine):
        for kk, v in base[p].items():
            nb[j, ix[kk]] = v
        for s in range(5):
            for kk, v in shuf[s][p].items():
                ns[s, j, ix[kk]] = v
    ultimi = sorted({a for a, _ in chiavi}, key=str)
    primi = sorted({b for _, b in chiavi}, key=str)
    ia_, ib_ = {a: i for i, a in enumerate(ultimi)}, {b: i for i, b in enumerate(primi)}
    mappa = np.array([(ia_[a], ib_[b]) for a, b in chiavi])
    # D (ia10): punteggi per pagina, per piega (come imitatore_misure.lavoro_D per 'vere')
    P = np.zeros((len(pagine), 2))
    Rm = np.zeros((len(pagine), 2))
    forma_pp = np.zeros((len(pagine), 4))
    for f in range(I7.PIEGHE):
        resto = [p for p in c['ids'] if c['fold'][p] != f]
        random.Random(3964 + 100 * I10.SEME_DIV + f).shuffle(resto)
        nval = max(1, round(0.10 * len(resto)))
        VV = lambda ps: OrderedDict((p, c['vere'][p]) for p in ps)               # noqa: E731
        M = R.FamiglieModello(I10, VV(resto[nval:]), VV(resto[:nval]), K=None, seme=1)
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        Pf, Rf = R.stat_D(I10, M, pg, C.seme_str('D16', f, 'vere'), I10.S_RIM)
        for j, p in enumerate(pg):
            P[pagine.index(p)], Rm[pagine.index(p)] = Pf[j], Rf[j]
        # forma e parole nuove: parole note e forma dalle pagine delle altre pieghe
        pv = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] != f)
        cnt = Counter(w for rr in pv.values() for _, ws in rr for w in ws)
        forma, noti = R.Forma(cnt), set(cnt)
        for p in pg:
            forma_pp[pagine.index(p)] = R.costo_nuove(forma, {p: rows[p]}, noti)
    # G9 (giudice 2)
    nomi_t, X, nf = k['vt266']
    j9 = next(i for i, n in enumerate(nf) if str(n).startswith(I16.G9_NOME))
    g9 = {p: float(X[i, j9]) for i, p in enumerate(nomi_t)}
    g9v = np.array([g9.get(p, np.nan) for p in pagine])
    # bordi: conti per pagina, per gruppo e tratto
    cp = [AP.conti_bordi({p: rows[p]}) for p in pagine]
    bord = OrderedDict()
    for g in ('prima', 'ultima', 'interna'):
        for ft in FEAT:
            simboli = sorted({s for x in cp for s in x[g][ft]}, key=str)
            si = {s: i for i, s in enumerate(simboli)}
            m = np.zeros((len(pagine), len(simboli)))
            for j, x in enumerate(cp):
                for s, v in x[g][ft].items():
                    m[j, si[s]] = v
            bord['%s|%s' % (g, ft)] = (simboli, m)
    foglio = [I7.foglio_di(p) for p in pagine]
    meta = C.meta_pagine()
    Q = dict(pagine=pagine, foglio=foglio, sez=[meta[p]['sez'] for p in pagine], lingua=[meta[p]['lingua'] for p in pagine], num=num, den=den,
             contatto=dict(nb=nb, ns=ns, mappa=mappa, na=len(ultimi), nbn=len(primi)), P=P, R=Rm, g9=g9v, bordi=bord, forma=forma_pp, solo_prova=bool(C.SOLO_CONTROLLI))
    with open(percorso_pagine() + '.tmp', 'wb') as fh:
        pickle.dump(Q, fh)
    os.replace(percorso_pagine() + '.tmp', percorso_pagine())
    # controlli di coerenza: il tutto da questi numeri contro le funzioni dirette
    w = np.ones(len(pagine))
    mm = misure_da_pesi(Q, w)
    diretto = C.stime_M(r)
    mi_dir = R.mi_contatto(OrderedDict((p, rows[p]) for p in pagine))
    coer = OrderedDict(copia_netta=[mm['copia_netta'], diretto['netto'].p], lam=[mm['lam'], diretto['lam'].p], contatto=[mm['contatto'], mi_dir],
                       D=[mm['D'], None], forma=[mm['costo_forma'], None])
    return OrderedDict([('lavoro', 'vv|pagine'), ('pagine', len(pagine)), ('misure_intere', mm), ('coerenza', coer),
                        ('secondi', round(time.time() - inizio, 1))])


def carica_pagine():
    with open(percorso_pagine(), 'rb') as fh:
        return pickle.load(fh)


# ---------------------------------------------------------------- misure da pesi di pagina

def _mi(n):
    N = n.sum()
    if N <= 0:
        return 0.0
    px, py = n.sum(1, keepdims=True), n.sum(0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(n > 0, n / N * np.log2(n * N / (px * py)), 0.0)
    return float(np.nansum(t))


def _matrice(Q, v):
    m = np.zeros((Q['contatto']['na'], Q['contatto']['nbn']))
    np.add.at(m, (Q['contatto']['mappa'][:, 0], Q['contatto']['mappa'][:, 1]), v)
    return m


def misure_da_pesi(Q, w):
    """Le nove misure sulle pagine di `Q` con pesi `w` (1 = una volta; un ricampionamento = conteggi)."""
    w = np.asarray(w, dtype=float)
    out = OrderedDict()
    num, den = Q['num'], Q['den']

    def gain(ch, m_):
        return float(w @ num[ch + '_' + m_]) / float(w @ den[ch])
    nt = gain('t', 'g') - gain('t', 'n')
    npg = gain('p', 'g') - gain('p', 'n')
    out['copia_netta'] = nt
    out['lam'] = 1.0 - npg / nt if nt else float('nan')
    nb = _mi(_matrice(Q, w @ Q['contatto']['nb']))
    ns = float(np.mean([_mi(_matrice(Q, w @ Q['contatto']['ns'][s])) for s in range(Q['contatto']['ns'].shape[0])]))
    out['contatto'] = nb - ns
    out['D'] = float((w @ Q['P'][:, 0] - w @ Q['R'][:, 0]) / (w @ Q['P'][:, 1]))
    g = Q['g9']
    ok = ~np.isnan(g)
    out['G9'] = float((w[ok] @ g[ok]) / w[ok].sum())
    cont = {}
    for kk, (simboli, m) in Q['bordi'].items():
        v = w @ m
        cont[kk] = {s: x for s, x in zip(simboli, v) if x > 0}
    for g_, nome in CONTI_BORDI:
        vals = [AP._jsd(cont['%s|%s' % (g_, ft)], cont['interna|%s' % ft]) for ft in FEAT]
        vals = [x for x in vals if x is not None]
        out['bordi_' + nome] = float(statistics.mean(vals)) if vals else float('nan')
    fp = Q['forma']
    out['costo_forma'] = float(w @ fp[:, 0]) / float(w @ fp[:, 1])
    out['parole_nuove'] = float(w @ fp[:, 2]) / float(w @ fp[:, 3])
    return out


def pesi_meta(Q, s):
    """Una divisione dei fogli in due meta' (bilanciata: ogni gruppo sezione-lingua si divide a meta'). -> (pesi A, pesi B) sulle pagine."""
    rnd = random.Random(C.seme_str('ia25vv', s))
    gruppi = defaultdict(list)
    visti = set()
    for p, f, sz, lg in zip(Q['pagine'], Q['foglio'], Q['sez'], Q['lingua']):
        if f not in visti:
            visti.add(f)
            gruppi[(sz, lg)].append(f)
    meta_a = set()
    for kk in sorted(gruppi, key=str):
        ff = sorted(gruppi[kk])
        rnd.shuffle(ff)
        meta_a.update(ff[:(len(ff) + rnd.randint(0, 1)) // 2] if len(ff) % 2 else ff[:len(ff) // 2])
    a = np.array([1.0 if f in meta_a else 0.0 for f in Q['foglio']])
    return a, 1.0 - a


def _sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def analisi_vero_vero(Q):
    """Intervalli del vero per ogni misura (dai numeri per pagina), controlli e tolleranze."""
    P = len(Q['pagine'])
    intero = misure_da_pesi(Q, np.ones(P))
    out = OrderedDict(pagine=P, intero=intero, soglie=SOGLIE)
    # (a) divisioni a meta'
    dif = {m: [] for m in MISURE}
    mez = {m: [] for m in MISURE}
    for s in range(NSPLIT):
        a, b = pesi_meta(Q, s)
        ma, mb = misure_da_pesi(Q, a), misure_da_pesi(Q, b)
        for m in MISURE:
            dif[m].append(ma[m] - mb[m])
            mez[m] += [ma[m], mb[m]]
    # (b) ricampionamenti di pagine e di fogli
    rng = np.random.default_rng(250005)
    fogli = sorted(set(Q['foglio']))
    fi = {f: [i for i, x in enumerate(Q['foglio']) if x == f] for f in fogli}
    bp = {m: [] for m in MISURE}
    bf = {m: [] for m in MISURE}
    for _ in range(NBOOT):
        w = np.bincount(rng.integers(0, P, P), minlength=P).astype(float)
        mp = misure_da_pesi(Q, w)
        w2 = np.zeros(P)
        for f in rng.integers(0, len(fogli), len(fogli)):
            w2[fi[fogli[f]]] += 1
        mf = misure_da_pesi(Q, w2)
        for m in MISURE:
            bp[m].append(mp[m])
            bf[m].append(mf[m])
    tab = OrderedDict()
    for m in MISURE:
        d = [x for x in dif[m] if x == x]
        s_split = _sd(d) / 2.0 if len(d) > 1 else None
        s_bp, s_bf = _sd(bp[m]), _sd(bf[m])
        cand = [x for x in (s_split, s_bp, s_bf) if x is not None]
        sigma = max(cand) if cand else None
        v = intero[m]
        al5 = [abs(x) <= 0.05 * abs(v) for x in d]
        tab[m] = OrderedDict(
            vero=v, sigma_divisioni=s_split, sigma_pagine=s_bp, sigma_fogli=s_bf, sigma_vero=sigma,
            intervallo_2sigma=[v - 2 * sigma, v + 2 * sigma] if sigma is not None else None,
            ic95_pagine=[float(np.nanpercentile(bp[m], q)) for q in (2.5, 97.5)], ic95_fogli=[float(np.nanpercentile(bf[m], q)) for q in (2.5, 97.5)],
            fascia_meta_contro_meta=[float(np.nanpercentile(d, q)) for q in (2.5, 97.5)], media_differenza=float(np.nanmean(d)),
            accordo_fogli_su_divisioni=(s_bf / s_split) if s_split and s_bf else None,
            coppie_entro_5_per_cento=float(np.mean(al5)), meta_media=float(np.nanmean(mez[m])))
    out['misure'] = tab
    out['coppie_entro_5_per_cento_tutte_e_nove'] = float(np.mean([all(abs(dif[m][i]) <= 0.05 * abs(intero[m]) for m in MISURE if dif[m][i] == dif[m][i]) for i in range(NSPLIT)]))
    # controlli
    ctr = OrderedDict()
    ctr['negativo_media_zero'] = OrderedDict(dettaglio={m: (abs(tab[m]['media_differenza']) / (2 * tab[m]['sigma_divisioni']) if tab[m]['sigma_divisioni'] else None) for m in MISURE},
                                             soglia=SOGLIE['media_divisioni_su_sigma'])
    ctr['negativo_media_zero']['riuscito'] = all(x is not None and x <= SOGLIE['media_divisioni_su_sigma'] for x in ctr['negativo_media_zero']['dettaglio'].values())
    acc = [tab[m]['accordo_fogli_su_divisioni'] for m in MISURE if tab[m]['accordo_fogli_su_divisioni'] is not None]
    ctr['accordo_ricampionamento_divisioni'] = OrderedDict(
        rapporti={m: tab[m]['accordo_fogli_su_divisioni'] for m in MISURE}, banda=SOGLIE['accordo_boot_split'],
        riuscito=bool(acc) and sum(SOGLIE['accordo_boot_split'][0] <= x <= SOGLIE['accordo_boot_split'][1] for x in acc) >= 0.7 * len(acc))
    # positivo: lingua A contro lingua B (differenza vera, grande)
    A_ = np.array([1.0 if l == 'A' else 0.0 for l in Q['lingua']])
    B_ = np.array([1.0 if l == 'B' else 0.0 for l in Q['lingua']])
    if A_.sum() > 5 and B_.sum() > 5:
        ma, mb = misure_da_pesi(Q, A_), misure_da_pesi(Q, B_)
        vis = OrderedDict()
        for m in MISURE:
            s = tab[m]['sigma_divisioni']
            vis[m] = OrderedDict(A=ma[m], B=mb[m], differenza=ma[m] - mb[m], in_sigma=(abs(ma[m] - mb[m]) / (2 * s) if s else None))
        n_vis = sum(1 for x in vis.values() if x['in_sigma'] is not None and x['in_sigma'] >= SOGLIE['lingua_AB_sigma'])
        ctr['positivo_lingua_A_contro_B'] = OrderedDict(dettaglio=vis, misure_viste=n_vis, soglia=[SOGLIE['lingua_AB_misure_viste'], SOGLIE['lingua_AB_sigma']],
                                                        riuscito=n_vis >= SOGLIE['lingua_AB_misure_viste'])
    out['controlli'] = ctr
    return out


# ---------------------------------------------------------------- rilettura dei verdetti "al vero" di ia20-ia24

FILE = OrderedDict([('ia20', 'ia20_imitatore_gradini.json'), ('ia22', 'ia22_eco_e_legame.json'), ('ia23', 'ia23_pagina_intera.json'), ('ia24', 'ia24_parole_nuove.json')])


def _flag_salvati(nome, d):
    """Verdetti 'al vero' scritti in quel risultato (per il controllo di riproduzione): tipo -> misura -> bool."""
    out = {}
    L = d['letture']
    if nome == 'ia20':
        for m, x in L['L4_irriproducibile'].items():
            if 'al_vero' in x:
                for t, f in x['al_vero'].items():
                    out.setdefault(t, {})[m] = f
    else:
        k = {'ia22': 'L1_eco_e_legame', 'ia23': 'L1_eco_e_legame', 'ia24': 'L1_forma'}[nome]
        for t, x in L[k]['per_tipo'].items():
            for m, f in x['al_vero'].items():
                out.setdefault(t, {})[m] = f
    return out


def rileggi(tab, cartella):
    """tab: misura -> sigma_vero (da `analisi_vero_vero`). Legge i json di ia20-ia24 in `cartella`; per ogni (tipo, misura): regola vecchia (rifatta e confrontata
    con il verdetto salvato), regola nuova (<= 2 radice(sigma^2 + e^2)) e nuova-o-vecchia."""
    out = OrderedDict()
    tot = Counter()
    for nome, f in FILE.items():
        p = os.path.join(cartella, f)
        if not os.path.exists(p):
            continue
        import json
        d = json.load(open(p, encoding='utf-8'))
        salv = _flag_salvati(nome, d)
        righe = []
        for t, vals in d['valori'].items():
            for m in MISURE:
                if m not in vals or vals[m][0] is None or d['vero'].get(m) is None:
                    continue
                mu, e = vals[m]
                v = d['vero'][m]
                vecchio = C.classe_vero(mu, e, v)
                s = tab.get(m, {}).get('sigma_vero')
                nuovo = bool(abs(mu - v) <= 2 * math.sqrt((s or 0.0) ** 2 + (e or 0.0) ** 2)) if s is not None else None
                n_o_v = bool(nuovo or vecchio) if nuovo is not None else None
                sv = salv.get(t, {}).get(m)
                righe.append(OrderedDict(tipo=t, misura=m, valore=mu, errore=e, vero=v, vecchio=vecchio, salvato=sv, riproduce=(None if sv is None else bool(sv == vecchio)),
                                         nuovo=nuovo, nuovo_o_vecchio=n_o_v, cambia_nuovo=(None if nuovo is None else bool(nuovo != vecchio)),
                                         cambia_nuovo_o_vecchio=(None if n_o_v is None else bool(n_o_v != vecchio))))
        out[nome] = righe
        for r in righe:
            tot['celle'] += 1
            tot['con_salvato'] += r['salvato'] is not None
            tot['riprodotte'] += bool(r['riproduce'])
            tot['cambia_nuovo'] += bool(r['cambia_nuovo'])
            tot['cambia_nuovo_o_vecchio'] += bool(r['cambia_nuovo_o_vecchio'])
            tot['diventa_vero_nuovo'] += bool(r['cambia_nuovo'] and r['nuovo'])
            tot['smette_vero_nuovo'] += bool(r['cambia_nuovo'] and not r['nuovo'])
    out['_totali'] = OrderedDict(tot)
    return out


def scrivi_md(o, rl):
    r = ['## Parte 5: il metro "vero contro vero"', '',
         'Domanda: quanto varia il vero da se\' stesso, misura per misura, e quali verdetti "al vero" di ia20-ia24 cambiano leggendoli con questo intervallo? '
         '(%d divisioni dei fogli in due meta\', %d ricampionamenti di pagine e di fogli.)' % (NSPLIT, NBOOT), '',
         '| misura | vero | sigma (divisioni) | sigma (pagine) | sigma (fogli) | sigma del vero | vero ± 2 sigma | meta\' contro meta\' (95%) | coppie entro il 5% |',
         '|---|---|---|---|---|---|---|---|---|']
    for m, x in o['misure'].items():
        iv = x['intervallo_2sigma']
        r.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (m, C.fmt(x['vero'], 4), C.fmt(x['sigma_divisioni'], 4), C.fmt(x['sigma_pagine'], 4), C.fmt(x['sigma_fogli'], 4),
                                                                     C.fmt(x['sigma_vero'], 4), '%s – %s' % (C.fmt(iv[0], 4), C.fmt(iv[1], 4)) if iv else '—',
                                                                     '%s – %s' % (C.fmt(x['fascia_meta_contro_meta'][0], 4), C.fmt(x['fascia_meta_contro_meta'][1], 4)),
                                                                     C.fmt(x['coppie_entro_5_per_cento'], 2)))
    r += ['', 'Coppie di meta\' "al vero" fra loro su tutte e nove le misure insieme (regola del 5%%): %s' % C.fmt(o['coppie_entro_5_per_cento_tutte_e_nove'], 3), '',
          '### Controlli', ''] + ['- %s: %s' % (k, v) for k, v in o['controlli'].items()]
    r += ['', '### Verdetti rielaborati (ia20-ia24)', '', 'Totali: %s' % dict(rl.get('_totali', {})), '']
    for nome, righe in rl.items():
        if nome.startswith('_'):
            continue
        cambi = [x for x in righe if x['cambia_nuovo']]
        r.append('- %s: %d celle, %d cambiano con la regola nuova: %s' % (nome, len(righe), len(cambi),
                                                                         '; '.join('%s %s (%s -> %s)' % (x['tipo'], x['misura'], 'sì' if x['vecchio'] else 'no', 'sì' if x['nuovo'] else 'no') for x in cambi) or 'nessuna'))
    return r
