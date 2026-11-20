# -*- coding: utf-8 -*-
"""Esperimento IA11 (ia11): "rifarlo", la prova del nove. Se ai libri v21 si aggiunge cio' che IA8-IA10 dicono che gli manca (l'eco
della pagina, l'ordine delle famiglie di parole, la forma delle parole nuove), il giudice A di ia01 smette di riconoscerli (AUC da 0,75
verso 0,50) senza peggiorare sui giudici del paper e, soprattutto, davanti a un giudice indipendente che non ha servito a progettare i
ritocchi? Preregistrazione: preregistrazioni/ia11.md.

Che cosa fa il codice (in parole semplici)
- I libri sono quelli di ia01 gia' generati (cache), senza messaggio (b13-b22); non si tocca il voynichizzatore. Le "varianti" sono
  ritocchi del testo (rifarlo_ritocchi.py): V0 il libro com'e'; V1 + eco della pagina; V2 + ordine delle famiglie; V3 = V1 + V2;
  V4 = V3 + correzione della forma delle parole nuove; N1 ritocco a caso della stessa entita' (controllo negativo); VR pagine VERE con
  un ritocco leggero (controllo di artefatti); V0a i libri con messaggio a13-a22 senza ritocchi (riproduzione di ia01).
- Taratura (lavoro F, una per piega del giudice): pochi parametri (probabilita' e scala dell'eco, forza dell'ordine, quota di parole
  corrette) si cercano per far tornare le misure di ia09/ia10 sulle sole pagine di addestramento della piega, con libri mai giudicati
  (chiavi 23 e 24); le pagine di prova della piega non entrano mai. Per l'ordine e la forma si usano due meta' delle pagine di
  addestramento (famiglie imparate su una meta' e misurate sull'altra).
- Giudici: A (rete GRU di ia01: lo stesso modello del testo, stesse pieghe e semi, stessa regressione); K, INDIPENDENTE (modello a
  caratteri non neurale con memoria di pagina, stesso passaggio finale di profilo e regressione); e231 ed e266 del paper (devono non salire).
- Verifica di manipolazione: le misure di ia09 (copia netta, quota locale), di ia10 (D con il modello delle vere), di ia08 (contatto
  ultimo -> primo glifo) e la forma delle parole nuove sulle varianti si avvicinano davvero a quelle delle vere?
Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia11_rifarlo.json e .md, una riga per lavoro in
risultati/ia11_corse.jsonl (con RIPRENDI=1 i lavori fatti non si rifanno); i testi ritoccati e i modelli stanno in dati/cache/ia11 (CACHE11).

Variabili (oltre a quelle di ia01, ia09, ia10: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, CHIAVI, SEMI, PASSI, OGNI, PAZIENZA, NASCOSTO,
CADUTA, NEG, BOOT, S_RIM, GIRI, NV, KS, FILTRO, RIPRENDI, PROCESSI, FASI): CACHE11 (cartella dei testi ritoccati), LIBRI_TARA (chiavi dei
libri di taratura, 23,24), LIBRI_MANIP (quanti libri nella verifica di manipolazione, tutti), VARIANTI (elenco, tutte), NRIM_TARA.
FASI: taratura (lavori F e L), giudizio (lavori P, K, M, E), analisi.
"""
import json, math, os, pickle, random, sys, time, zlib
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import ia09_dove_sta_sintassi as A9  # noqa: E402
import ia10_famiglie_parole as I10  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import rifarlo_giudici as J  # noqa: E402

NOME = 'ia11_rifarlo'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF, SEMI, CHIAVI = G.NF, G.SEMI, G.CHIAVI
CACHE = os.environ.get('CACHE11', os.path.join(QUI, '..', 'dati', 'cache', 'ia11'))
LIBRI_TARA = G.lista('LIBRI_TARA', '23,24')
LIBRI_MANIP = int(os.environ.get('LIBRI_MANIP', len(CHIAVI)))
NRIM_TARA = int(os.environ.get('NRIM_TARA', 10))
BOOT = int(os.environ.get('BOOT', 1000))
VARIANTI_TUTTE = ['V0a', 'V0', 'V1', 'V2', 'V3', 'V4', 'N1']
VARIANTI = [v for v in os.environ.get('VARIANTI', ','.join(VARIANTI_TUTTE)).split(',') if v]
REP_VR = 3                                          # ripetizioni delle pagine vere ritoccate

# ---- parametri della taratura (fissati nella preregistrazione)
GRIGLIA_TAU = (4.0, 10.0, 25.0, 60.0)               # scala dell'eco, in parole
GRIGLIA_Q = (0.3, 0.7)                              # probabilita' che la copia sia cambiata di una modifica
GRIGLIA_GAMMA = (0.0, 0.5, 1.0)                     # preferenza per le fonti rare (peso (frequenza + 1)^-gamma)
P_RIF = 0.10                                        # probabilita' di eco con cui si misura l'effetto per grandezza
P_MAX = 0.5
GRIGLIA_LAM = (0.5, 1.0, 2.0, 4.0)                  # forza del riordino (per bit di guadagno di famiglia)
MARGINE_LAM = 0.25                                  # si sceglie la forza piu' piccola che arriva al bersaglio + 25% del dislivello
MU = 1.0                                            # peso del contatto ultimo -> primo glifo nel riordino
INTENSITA_VR = 0.5                                  # pagine vere ritoccate: meta' dell'intensita'

# ---- soglie delle letture (fissate nella preregistrazione, prima di eseguire sul Voynich)
RIPRODUZIONE_IA01 = 0.751
TOL_V0A, TOL_V0 = 0.01, 0.03                        # V0a entro 0,01 da ia01; V0 (libri senza messaggio) entro 0,03 da V0a
CTRL_POS, BANDA_NEG = 0.85, (0.45, 0.55)
K_VEDE_MIN = 0.65                                   # il giudice indipendente deve vedere V0 con almeno questa AUC
Q_SI_A, Q_SI_K, Q_NO = 0.40, 0.30, 0.15             # quota dell'eccesso sopra 0,5 che la variante toglie
DISCESA_MIN_CI = 0.03                               # limite basso dell'intervallo della discesa di A (V0 - V3)
PAPER_MAX = 0.03                                    # i giudici del paper non devono salire oltre
NEG_MAX = 0.02                                      # il ritocco a caso non deve far scendere l'AUC di piu'
VR_MAX = 0.60                                       # pagine vere ritoccate: AUC al massimo
MANIP_BASSO, MANIP_ALTO = 0.6, 1.4                  # frazione del cammino V0 -> vere
LAMBDA_FRAZ = 0.5                                   # la quota locale (ia09) deve fare almeno meta' strada
CONTATTO_TOL, NUOVE_TOL = 0.02, 0.02
FORMA_SI, FORMA_NO = 0.03, 0.01                     # discesa di V3 -> V4


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def nome_v(var, k):
    return 'V0a:a%d' % k if var == 'V0a' else '%s:b%d' % (var, k)


def percorso_var(f):
    return os.path.join(CACHE, 'var_f%d.pkl' % f)


def percorso_lm(seme, f):
    return os.path.join(CACHE, 'lm_s%d_f%d.pt' % (seme, f))


# ---------------------------------------------------------------- divisione di una piega (come ia10)

def divisione(f, seme=None):
    T = I10.testo('vere')
    pagine = list(T.pagine)
    test = [p for p in pagine if T.piega[p] == f]
    resto = [p for p in pagine if T.piega[p] != f]
    random.Random(3964 + 100 * (seme or I10.SEME_DIV) + f).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    return T, test, resto, resto[:nval], resto[nval:]


def genera(pagine, passi, ctx, tag):
    """Applica i passi (eco, poi ordine, poi forma) a ogni pagina, con un seme fisso per pagina."""
    out = OrderedDict()
    for p, rows in pagine.items():
        rnd = random.Random(seme_str('ia11', tag, p))
        if 'eco' in passi:
            rows = R.eco_pagina(rows, passi['eco'], ctx['forma'], ctx['ct'], rnd, ctx.get('freq'))
        if 'ord' in passi:
            rows = R.riordina_pagina(rows, passi['ord'], ctx['fam'], ctx['lr'], ctx['ct'], rnd)
        if 'forma' in passi:
            rows = R.correggi_pagina(rows, ctx['noti'], ctx['forma'], passi['forma']['r'], rnd)
        out[p] = rows
    return out


def sotto(pagine, ps):
    return OrderedDict((p, pagine[p]) for p in ps if p in pagine)


def parole_di(pagine):
    return Counter(w for rows in pagine.values() for _, ws in rows for w in ws)


def contesto_modello(VV, ps, K, seme=1, val=None):
    """Famiglie, forma e contatto imparati sulle pagine vere `ps`."""
    pv = VV(ps)
    M = R.FamiglieModello(I10, pv, VV(val) if val else None, K=K, seme=seme)
    return M, dict(forma=R.Forma(parole_di(pv)), ct=R.Contatto(pv), fam=M.fam, lr=M.tr.logratio, noti=M.noti, freq=parole_di(pv))


# ---------------------------------------------------------------- lavoro F: taratura e generazione per una piega

def lavoro_F(f):
    inizio = time.time()
    c = G.contesto()
    T, test, resto, val, add = divisione(f)
    VV = lambda ps: OrderedDict((p, T.pagine[p]) for p in ps)
    libro = lambda nome, ps: sotto(G.libro(nome), ps)
    # ---- modello "esterno": famiglie come ia10 (stesse pagine di addestramento e validazione, seme 1)
    Madd, ctx = contesto_modello(VV, add, None, val=val)
    K = Madd.K
    Madd2 = R.FamiglieModello(I10, VV(add), K=K, seme=2)
    cal = OrderedDict(K=K, copertura_famiglie=round(Madd.copertura, 4), pagine=OrderedDict(test=len(test), resto=len(resto), val=len(val), add=len(add)))
    # ---- (1) eco: forma delle fasce di distanza sulle pagine di addestramento (resto), con libri mai giudicati
    libri_t = OrderedDict((k, libro('b%d' % k, resto)) for k in LIBRI_TARA)
    Ev, _ = R.eco_testo(VV(resto), freq=ctx['freq'])
    E0 = np.mean([R.eco_testo(pg, freq=ctx['freq'])[0] for pg in libri_t.values()], axis=0)
    w = 1.0 / np.maximum(np.abs(Ev), 0.05)
    prove = []
    for tau in GRIGLIA_TAU:
        for q in GRIGLIA_Q:
            for gamma in GRIGLIA_GAMMA:
                par = dict(p=P_RIF, tau=tau, q=q, gamma=gamma)
                Es = np.mean([R.eco_testo(genera(pg, dict(eco=par), ctx, 'eco:%s:%s:%s:%s' % (tau, q, gamma, k)), freq=ctx['freq'])[0]
                              for k, pg in libri_t.items()], axis=0)
                dE = (Es - E0) / P_RIF
                den = float(np.sum((w * dE) ** 2))
                p = float(np.clip(np.sum((w * dE) * (w * (Ev - E0))) / den, 0, P_MAX)) if den > 0 else 0.0
                prove.append((float(np.sum((w * (Ev - E0 - p * dE)) ** 2)), tau, q, gamma, p))
    loss0, tau, q, gamma, p = min(prove)

    def eco_con(p_):
        par = dict(p=round(p_, 4), tau=tau, q=q, gamma=gamma)
        return np.mean([R.eco_testo(genera(pg, dict(eco=par), ctx, 'eco-verifica:%s' % k), freq=ctx['freq'])[0] for k, pg in libri_t.items()], axis=0)
    # l'effetto di p non e' lineare (l'eco si copia a sua volta): si raffina p con una ricerca a sezione aurea sulla perdita vera
    perdita = lambda E_: float(np.sum((w * (Ev - E_)) ** 2))
    visti = {}
    for p_ in [p]:
        visti[p_] = eco_con(p_)
    a_, b_ = 0.0, min(max(2 * p, 0.05), P_MAX)
    fi = (math.sqrt(5) - 1) / 2
    x1, x2 = b_ - fi * (b_ - a_), a_ + fi * (b_ - a_)
    for _ in range(5):
        for x in (x1, x2):
            if x not in visti:
                visti[x] = eco_con(x)
        if perdita(visti[x1]) < perdita(visti[x2]):
            b_, x2 = x2, x1
            x1 = b_ - fi * (b_ - a_)
        else:
            a_, x1 = x1, x2
            x2 = a_ + fi * (b_ - a_)
    p_forma = min(visti, key=lambda x: perdita(visti[x]))
    # seconda fase: la FORMA dell'eco (tau, q, gamma) viene dalle fasce di distanza; l'INTENSITA' p si rifinisce sulla copia netta di ia09
    # (guadagno della miscela di copia meno quello del riferimento, dentro il testo), misurata sulle sole pagine del resto, per bisezione
    fold_c = {p_: c['fold'][p_] for p_ in resto}

    def copia_netta(pg, tag, mescola=False):
        nt = 'ia11:cn:%s:%d' % (tag, f)
        A9._T[nt] = dict(pagine=A9.TT.rimescola_pagina(pg, seme_str('cnrim', tag, f)) if mescola else pg, fold=fold_c, tipo=None)
        st = A9.lavoro_C(nt)['stat']
        del A9._T[nt]
        den = sum(x['n'][0] for x in st.values())
        return float(sum(x['w']['n'][0] - x['w']['g'][0] for x in st.values()) / max(den, 1))

    def cn_con(p_, mescola=False):
        par = dict(p=round(p_, 4), tau=tau, q=q, gamma=gamma)
        return float(np.mean([copia_netta(genera(pg, dict(eco=par), ctx, 'eco-cn:%s' % k), 'V1:%s:%s' % (k, p_), mescola) for k, pg in libri_t.items()]))
    cn_v = copia_netta(VV(resto), 'vere')
    cn_0 = float(np.mean([copia_netta(pg, 'V0:%s' % k) for k, pg in libri_t.items()]))
    p_hi = min(max(2 * p_forma, 0.05), P_MAX)
    if cn_v <= cn_0 + 1e-6:
        p, cn_fin, raggiunto_cn = 0.0, cn_0, False
    else:
        cn_hi = cn_con(p_hi)
        if cn_hi < cn_v:
            p, cn_fin, raggiunto_cn = p_hi, cn_hi, False
        else:
            lo, hi, cn_lo, cn_hi_ = 0.0, p_hi, cn_0, cn_hi
            for _ in range(4):
                mid = (lo + hi) / 2
                cm = cn_con(mid)
                if cm < cn_v:
                    lo, cn_lo = mid, cm
                else:
                    hi, cn_hi_ = mid, cm
            p = lo + (cn_v - cn_lo) * (hi - lo) / max(cn_hi_ - cn_lo, 1e-9)       # interpolazione lineare nell'ultimo intervallo
            cn_fin, raggiunto_cn = cn_con(p), True
    par_eco = dict(p=round(p, 4), tau=tau, q=q, gamma=gamma)
    E1 = eco_con(p)
    lam_v = 1.0 - copia_netta(VV(resto), 'vere~', True) / cn_v if cn_v > 1e-6 else float('nan')
    lam_1 = 1.0 - cn_con(p, True) / cn_fin if cn_fin > 1e-6 else float('nan')
    cal['eco'] = OrderedDict(parametri=par_eco, p_dalle_fasce=round(float(p_forma), 4), vettore_vere=[round(float(x), 4) for x in Ev],
                             vettore_V0=[round(float(x), 4) for x in E0], vettore_V1=[round(float(x), 4) for x in E1],
                             residuo_relativo=round(float(np.linalg.norm(w * (Ev - E1)) / max(np.linalg.norm(w * (Ev - E0)), 1e-9)), 4),
                             copia_netta=OrderedDict(vere=round(cn_v, 4), V0=round(cn_0, 4), V1=round(float(cn_fin), 4), raggiunta=bool(raggiunto_cn)),
                             quota_locale=OrderedDict(vere=round(float(lam_v), 4), V1=round(float(lam_1), 4)))
    cal['eco']['raggiunto'] = bool(raggiunto_cn)
    # ---- (2) ordine: due meta' delle pagine di addestramento, famiglie imparate su una meta' e misurate sull'altra
    rr = list(resto)
    random.Random(3990 + f).shuffle(rr)
    meta = [set(rr[:len(rr) // 2]), set(rr[len(rr) // 2:])]
    interni = []
    for h in range(2):
        train = [p_ for p_ in resto if p_ not in meta[h]]
        Mh, ctxh = contesto_modello(VV, train, K)
        interni.append((meta[h], Mh, ctxh))
    spezza = lambda pg: [OrderedDict((p_, r_) for p_, r_ in pg.items() if p_ in m_) for m_, _, _ in interni]

    def D_testo(parti):
        s = np.zeros(3)
        for (_, Mh, _), pg in zip(interni, parti):
            P_, R_ = R.stat_D(I10, Mh, pg, seme_str('D', f), NRIM_TARA)
            s += [P_[:, 0].sum(), P_[:, 1].sum(), R_[:, 0].sum()]
        return float((s[0] - s[2]) / max(s[1], 1.0))

    def riordina_meta(pg, lam, s=1.0, tag='o'):
        parti = spezza(pg)
        return [genera(x, dict(ord=dict(s=s, lam=lam, mu=MU)), ctxh, tag) for x, (_, _, ctxh) in zip(parti, interni)]

    def tara_ordine(basi, tag):
        Dv = D_testo(spezza(VV(resto)))
        D0 = float(np.mean([D_testo(spezza(b)) for b in basi.values()]))
        out = OrderedDict(D_vere=round(Dv, 4), D_base=round(D0, 4), per_lam=OrderedDict())
        scelta = None
        for lam in GRIGLIA_LAM:
            D1 = float(np.mean([D_testo(riordina_meta(b, lam, 1.0, '%s:%s:%s' % (tag, lam, k))) for k, b in basi.items()]))
            out['per_lam'][str(lam)] = round(D1, 4)
            if scelta is None and D1 >= Dv + MARGINE_LAM * (Dv - D0):
                scelta = (lam, D1)
        raggiunto = scelta is not None
        lam, D1 = scelta if raggiunto else (GRIGLIA_LAM[-1], out['per_lam'][str(GRIGLIA_LAM[-1])])
        s = float(np.clip((Dv - D0) / (D1 - D0), 0, 1)) if D1 - D0 > 1e-9 and Dv > D0 else 0.0
        out.update(lam=lam, s=round(s, 4), raggiunto=bool(raggiunto and Dv > D0))
        return out, dict(s=round(s, 4), lam=lam, mu=MU)

    base_v2 = OrderedDict((k, libro('b%d' % k, resto)) for k in LIBRI_TARA)
    cal['ordine_V2'], par_ord2 = tara_ordine(base_v2, 'V2')
    base_v3 = OrderedDict((k, genera(pg, dict(eco=par_eco), ctx, 'eco3:%s' % k)) for k, pg in base_v2.items())
    cal['ordine_V3'], par_ord3 = tara_ordine(base_v3, 'V3')
    # ---- (3) forma delle parole nuove: sulla base V3 (eco + ordine), con le due meta'
    v3_tara = OrderedDict()
    for k, b in base_v3.items():
        parti = riordina_meta(b, par_ord3['lam'], par_ord3['s'], 'V3t:%s' % k)
        v3_tara[k] = parti
    forme = []
    for h in range(2):
        train = [p_ for p_ in resto if p_ not in interni[h][0]]
        forme.append((R.Forma(parole_di(VV(train))), interni[h][1].noti))

    def costo(r_, tag):
        bit = gl = nn = tot = 0.0
        for k, parti in v3_tara.items():
            for h in range(2):
                fm, noti = forme[h]
                pg = parti[h]
                if r_ > 0:
                    pg = genera(pg, dict(forma=dict(r=r_)), dict(forma=fm, noti=noti), '%s:%s:%d' % (tag, k, h))
                b_, g_, n_, t_ = R.costo_nuove(fm, pg, noti)
                bit, gl, nn, tot = bit + b_, gl + g_, nn + n_, tot + t_
        return bit / max(gl, 1), nn / max(tot, 1)
    cv = [0.0, 0.0, 0.0, 0.0]
    for h in range(2):
        fm, noti = forme[h]
        x = R.costo_nuove(fm, sotto(T.pagine, [p_ for p_ in resto if p_ in interni[h][0]]), noti)
        cv = [a + b for a, b in zip(cv, x)]
    c_vere, q_vere = cv[0] / max(cv[1], 1), cv[2] / max(cv[3], 1)
    c_base, q_base = costo(0.0, 'f0')
    c_corr, q_corr = costo(1.0, 'f1')
    r_ = float(np.clip((c_vere - c_base) / (c_corr - c_base), 0, 1)) if c_corr < c_base - 1e-9 and c_vere < c_base else 0.0
    c_ver, q_ver = costo(r_, 'fv') if r_ > 0 else (c_base, q_base)
    par_forma = dict(r=round(r_, 4))
    cal['forma'] = OrderedDict(r=par_forma['r'], bit_per_glifo_vere=round(c_vere, 4), bit_per_glifo_V3=round(c_base, 4),
                               bit_per_glifo_corretto_tutto=round(c_corr, 4), bit_per_glifo_V4=round(c_ver, 4),
                               quota_nuove_vere=round(q_vere, 4), quota_nuove_V3=round(q_base, 4), quota_nuove_V4=round(q_ver, 4),
                               raggiunto=bool(c_vere < c_base and c_corr < c_base - 1e-9 and abs(c_ver - c_vere) <= 0.25 * abs(c_base - c_vere) + 1e-9))
    cal['parametri'] = OrderedDict(eco=par_eco, ordine_V2=par_ord2, ordine_V3=par_ord3, forma=par_forma)
    # ---- (4) generazione delle pagine di prova (mai viste dalla taratura)
    test_v = VV(test)
    testi = OrderedDict()
    testi['vere'] = test_v
    mezzo = dict(eco=dict(par_eco, p=par_eco['p'] * INTENSITA_VR), ord=dict(par_ord3, s=par_ord3['s'] * INTENSITA_VR))
    for k in CHIAVI:
        b0 = libro('b%d' % k, test)
        testi['V0a:a%d' % k] = libro('a%d' % k, test)
        testi['V0:b%d' % k] = b0
        testi['V1:b%d' % k] = genera(b0, dict(eco=par_eco), ctx, 'V1:b%d' % k)
        testi['V2:b%d' % k] = genera(b0, dict(ord=par_ord2), ctx, 'V2:b%d' % k)
        v3 = genera(b0, dict(eco=par_eco, ord=par_ord3), ctx, 'V3:b%d' % k)
        testi['V3:b%d' % k] = v3
        testi['V4:b%d' % k] = genera(v3, dict(forma=par_forma), ctx, 'V4:b%d' % k)
        testi['N1:b%d' % k] = R.ritocco_casuale(b0, par_eco, par_ord3, ctx['forma'], random.Random(seme_str('ia11', 'N1', k, f)))
    for rep in range(1, REP_VR + 1):
        testi['VR:r%d' % rep] = genera(test_v, dict(eco=mezzo['eco'], ord=mezzo['ord']), ctx, 'VR:r%d' % rep)
    os.makedirs(CACHE, exist_ok=True)
    with open(percorso_var(f) + '.tmp', 'wb') as fh:
        pickle.dump(dict(testi), fh)
    os.replace(percorso_var(f) + '.tmp', percorso_var(f))
    # ---- (5) misure sulle pagine di prova (modello delle vere di questa piega, come ia10 "cross")
    stat = OrderedDict()
    for nome, pg in testi.items():
        P1, R1 = R.stat_D(I10, Madd, pg, seme_str('Dp', f, nome), I10.S_RIM)
        P2, R2 = R.stat_D(I10, Madd2, pg, seme_str('Dp2', f, nome), I10.S_RIM)
        fm = [R.costo_nuove(ctx['forma'], OrderedDict([(p_, rows)]), ctx['noti']) for p_, rows in pg.items()]
        _, S = R.eco_testo(pg, freq=ctx['freq'])
        stat[nome] = OrderedDict(
            pag=list(pg), D=[[round(float(P1[i, 0]), 3), round(float(P1[i, 1])), round(float(R1[i, 0]), 3), round(float(P2[i, 0]), 3),
                              round(float(P2[i, 1])), round(float(R2[i, 0]), 3)] for i in range(len(pg))],
            forma=[[round(x[0], 2), round(x[1]), int(x[2]), int(x[3])] for x in fm], eco=S.round(1).tolist())
    return dict(job=['F', f], calibrazione=cal, stat=stat, tempo=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- lavori L (modello del testo di A) e P (profili di A)

def lavoro_L(seme, f):
    import torch
    c = G.contesto()
    pagine = list(c['ids'])
    test = [p for p in pagine if c['fold'][p] == f]
    resto = [p for p in pagine if c['fold'][p] != f]
    random.Random(3964 + 100 * seme + f).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([c['ids'][p] for p in ps])
    m, info = G.addestra_lm(flusso(add), flusso(val), c['V'], 1000 * seme + f)
    os.makedirs(CACHE, exist_ok=True)
    torch.save(m.state_dict(), percorso_lm(seme, f) + '.tmp')
    os.replace(percorso_lm(seme, f) + '.tmp', percorso_lm(seme, f))
    info['bpc_vere_fuori'] = float(np.mean([np.mean(x) for x in G.sorprese(m, [c['ids'][p] for p in test])]))
    return dict(job=['L', seme, f], info=info, tempo=info.get('secondi', 0.0))


def nomi_libri_fold(f):
    """Tutti i libri (con le pagine di prova della piega f) da giudicare: vere, controlli di ia01, varianti."""
    c = G.contesto()
    test = [p for p in c['ids'] if c['fold'][p] == f]
    with open(percorso_var(f), 'rb') as fh:
        testi = pickle.load(fh)
    libri = OrderedDict()
    libri['vere'] = {p: c['ids'][p] for p in test}
    for nome in G.controlli_disponibili():
        g = G.ids_libro(nome)
        libri[nome] = {p: g[p] for p in test if p in g}
    for nome, pg in testi.items():
        if nome == 'vere':
            continue
        libri[nome] = {p: G.codifica(rows, c['idx']) for p, rows in pg.items()}
    return libri


def lavoro_P(seme, f):
    import torch
    inizio = time.time()
    c = G.contesto()
    m = G.moduli()['LM'](c['V'])
    m.load_state_dict(torch.load(percorso_lm(seme, f), weights_only=True))
    m.eval()
    prof = OrderedDict()
    for nome, g in nomi_libri_fold(f).items():
        ps = list(g)
        s = G.sorprese(m, [g[p] for p in ps])
        prof[nome] = OrderedDict((p, G.profilo(g[p], x)) for p, x in zip(ps, s))
    return dict(job=['P', seme, f], profili=prof, tempo=round(time.time() - inizio, 1))


def lavoro_K(f):
    inizio = time.time()
    c = G.contesto()
    _, test, resto, val, add = divisione(f)
    g, info = J.scegli_giudice_k([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V'])
    prof = OrderedDict()
    for nome, libro_ in nomi_libri_fold(f).items():
        prof[nome] = OrderedDict((p, G.profilo(a, g.sorpresa(a))) for p, a in libro_.items())
    return dict(job=['K', f], info=info, profili=prof, tempo=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- lavori M (misure ia09/ia08 sul testo intero) ed E (giudici del paper)

_VAR = {}


def testo_intero(nome):
    """Il testo `nome` con tutte le pagine (le pagine di prova di ogni piega messe insieme)."""
    out = OrderedDict()
    for f in range(NF):
        if f not in _VAR:
            with open(percorso_var(f), 'rb') as fh:
                _VAR[f] = pickle.load(fh)
        out.update(_VAR[f][nome])
    return OrderedDict((p, out[p]) for p in sorted(out))


MODELLI_M = ['g', 'n', 'gram', 'tutto', 'gram_n']


def lavoro_M(nome):
    inizio = time.time()
    c = G.contesto()
    pag = testo_intero(nome)
    fold = {p: c['fold'][p] for p in pag}
    nt = 'ia11:' + nome
    A9._T.clear()
    A9._T[nt] = dict(pagine=pag, fold=fold, tipo=None)
    A9._T[nt + '~p'] = dict(pagine=A9.TT.rimescola_pagina(pag, seme_str('ia11rim', nome)), fold=fold, tipo=None)
    out = OrderedDict(job=['M', nome], pag=sorted(pag), mi=R.mi_contatto(pag))
    for chiave, nm in (('t', nt), ('p', nt + '~p')):
        r = A9.lavoro_C(nm)
        st = r['stat']
        ps = sorted(st)
        out['den_' + chiave] = [st[p]['n'][0] for p in ps]
        U = np.array([st[p]['w']['U'][0] for p in ps])
        for m_ in MODELLI_M:
            out['num_%s_%s' % (chiave, m_)] = [round(float(x), 3) for x in U - np.array([st[p]['w'][m_][0] for p in ps])]
    out['tempo'] = round(time.time() - inizio, 1)
    return out


def lavoro_E(nome):
    inizio = time.time()
    c = G.contesto()
    r = J.giudici_paper(testo_intero(nome), c['vere'])
    return dict(job=['E', nome], tempo=round(time.time() - inizio, 1), **r)


def nomi_testi_misura():
    var = [v for v in ('V0', 'V1', 'V2', 'V3', 'V4', 'N1') if v in VARIANTI]
    return ['vere'] + ['%s:b%d' % (v, k) for v in var for k in CHIAVI[:LIBRI_MANIP]]


def nomi_testi_paper():
    var = [v for v in ('V0', 'V1', 'V2', 'V3', 'V4', 'N1') if v in VARIANTI]
    return ['%s:b%d' % (v, k) for v in var for k in CHIAVI[:LIBRI_MANIP]] + ['VR:r%d' % i for i in range(1, REP_VR + 1)]


def lavoro(job):
    try:
        if job[0] == 'F':
            return lavoro_F(job[1])
        if job[0] == 'L':
            return lavoro_L(job[1], job[2])
        if job[0] == 'P':
            return lavoro_P(job[1], job[2])
        if job[0] == 'K':
            return lavoro_K(job[1])
        if job[0] == 'M':
            return lavoro_M(job[1])
        return lavoro_E(job[1])
    except Exception as e:  # noqa: BLE001
        import traceback
        return dict(job=list(job), errore='%s: %s' % (type(e).__name__, str(e)[:300]), traccia=traceback.format_exc()[-1500:], tempo=0.0)


def lavori(fasi):
    L = []
    if 'taratura' in fasi:
        L += [('L', s, f) for s in SEMI for f in range(NF)] + [('F', f) for f in range(NF)]
    if 'giudizio' in fasi:
        L += [('P', s, f) for s in SEMI for f in range(NF)] + [('K', f) for f in range(NF)]
        L += [('M', n) for n in nomi_testi_misura()] + [('E', n) for n in nomi_testi_paper()]
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


# ---------------------------------------------------------------- analisi

def media(x):
    x = [v for v in x if v is not None and v == v]
    return float(np.mean(x)) if x else None


def ic(x):
    return [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]


def coppia_auc(prof, nome, c):
    """AUC di un giudice a profili (stessa procedura di ia01.analizza_A_coppia): vere contro il libro `nome`."""
    if nome not in prof or 'vere' not in prof:
        return None
    pag = sorted(p for p in prof['vere'] if p in prof[nome])
    if len(pag) < 10 or len(pag) < 0.99 * len(c['ids']):
        return None
    X = np.array([np.mean(prof['vere'][p], axis=0) for p in pag] + [np.mean(prof[nome][p], axis=0) for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    a, p = G.auc_logistico(X, y, pag + pag)
    n = len(pag)
    return dict(AUC=float(a), reali=np.array(p[:n]), generate=np.array(p[n:]))


def negativo(prof, c, s):
    pag = sorted(prof['vere'])
    random.Random(3970 + s).shuffle(pag)
    y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
    X = np.array([np.mean(prof['vere'][p], axis=0) for p in pag])
    return float(G.auc_logistico(X, y, pag)[0])


def giudizio_giudice(prof, c, nome_giudice):
    """AUC per variante e per libro di un giudice a profili, con controlli e intervalli."""
    out = OrderedDict(nome=nome_giudice)
    per = OrderedDict()
    coppie = OrderedDict()
    for var in VARIANTI:
        lib = [nome_v(var, k) for k in CHIAVI] if var != 'VR' else []
        r = [coppia_auc(prof, n, c) for n in lib]
        r = [x for x in r if x]
        if r:
            per[var] = [x['AUC'] for x in r]
            coppie[var] = [(x['reali'], x['generate']) for x in r]
    r = [coppia_auc(prof, 'VR:r%d' % i, c) for i in range(1, REP_VR + 1)]
    r = [x for x in r if x]
    if r:
        per['VR'] = [x['AUC'] for x in r]
        coppie['VR'] = [(x['reali'], x['generate']) for x in r]
    boot = J.bootstrap_auc(coppie, n=BOOT) if coppie else {}
    out['per_libro'] = per
    out['AUC'] = OrderedDict((v, OrderedDict(media=float(np.mean(a)), se=float(np.std(a, ddof=1) / len(a) ** 0.5) if len(a) > 1 else 0.0,
                                             ic=ic(boot[v]) if v in boot else None, minimo=float(min(a)), massimo=float(max(a))))
                             for v, a in per.items())
    ctrl = OrderedDict()
    for n in G.controlli_disponibili():
        x = coppia_auc(prof, n, c)
        if x:
            ctrl[n] = x['AUC']
    neg = [negativo(prof, c, s) for s in range(1, G.NEG + 1)]
    out['controlli'] = ctrl
    out['negativo'] = OrderedDict(media=float(np.mean(neg)), valori=[round(x, 4) for x in neg])
    pos = [v for n, v in ctrl.items() if n in ('ctrl:parole', 'ctrl:e192', 'ctrl:ordine1')]
    out['valido'] = bool(pos and all(v >= CTRL_POS for v in pos) and BANDA_NEG[0] <= out['negativo']['media'] <= BANDA_NEG[1])
    out['_boot'] = boot
    return out


def quota(m0, m):
    return (m0 - m) / (m0 - 0.5) if m0 - 0.5 > 1e-9 else float('nan')


def discese(gd):
    """Per un giudice: discesa (V0 - V) con intervallo appaiato e quota dell'eccesso tolta, per ogni variante."""
    b, a = gd['_boot'], gd['AUC']
    out = OrderedDict()
    if 'V0' not in a:
        return out
    for v in a:
        if v in ('V0', 'V0a'):
            continue
        base = 'V0' if v != 'VR' else None
        if base is None:
            continue
        d = b['V0'] - b[v]
        out[v] = OrderedDict(discesa=round(a['V0']['media'] - a[v]['media'], 4), ic=ic(d), quota=round(quota(a['V0']['media'], a[v]['media']), 4))
    return out


def manipolazione(corse, c):
    """Le misure delle varianti contro quelle delle vere: D (ia10), eco (ia09), contatto (ia08), forma delle parole nuove."""
    F = {r['job'][1]: r for r in corse if r['job'][0] == 'F' and 'stat' in r}
    out = OrderedDict()
    if len(F) < NF:
        return out
    pag_tot = sum(len(F[f]['stat']['vere']['pag']) for f in F)
    W = A9.pesi_bootstrap(pag_tot)

    def mat(nome, col):
        return np.array([x[col] for f in sorted(F) for x in F[f]['stat'][nome]['D']])
    # --- D di ia10 (famiglie dello stesso seme; famiglie di un altro seme) e forma delle parole nuove
    def Dboot(nome, secondo=False):
        a = mat(nome, 3 if secondo else 0), mat(nome, 4 if secondo else 1), mat(nome, 5 if secondo else 2)
        num, den = a[0] - a[2], a[1]
        return float(num.sum() / den.sum()), (W @ num) / (W @ den)

    def formaboot(nome):
        m = np.array([x for f in sorted(F) for x in F[f]['stat'][nome]['forma']])
        return (float(m[:, 0].sum() / max(m[:, 1].sum(), 1)), (W @ m[:, 0]) / np.maximum(W @ m[:, 1], 1),
                float(m[:, 2].sum() / m[:, 3].sum()))
    righe = OrderedDict()
    for var in ('vere',) + tuple(v for v in VARIANTI if v != 'V0a'):
        nomi = ['vere'] if var == 'vere' else ['VR:r%d' % i for i in range(1, REP_VR + 1)] if var == 'VR' else [nome_v(var, k) for k in CHIAVI]
        if not all(n in F[0]['stat'] for n in nomi):
            continue
        D = [Dboot(n) for n in nomi]
        D2 = [Dboot(n, True) for n in nomi]
        fo = [formaboot(n) for n in nomi]
        righe[var] = OrderedDict(
            D=float(np.mean([x[0] for x in D])), D_b=np.mean([x[1] for x in D], axis=0),
            D2=float(np.mean([x[0] for x in D2])), D2_b=np.mean([x[1] for x in D2], axis=0),
            forma=float(np.mean([x[0] for x in fo])), forma_b=np.mean([x[1] for x in fo], axis=0),
            quota_nuove=float(np.mean([x[2] for x in fo])))
    # --- eco per fascia (somme sui testi, pagine di prova di tutte le pieghe)
    eco = OrderedDict()
    for var in righe:
        nomi = ['vere'] if var == 'vere' else ['VR:r%d' % i for i in range(1, REP_VR + 1)] if var == 'VR' else [nome_v(var, k) for k in CHIAVI]
        S = np.mean([sum(np.array(F[f]['stat'][n]['eco']) for f in F) for n in nomi], axis=0)
        eco[var] = [round(float(x), 4) for x in R.vettore_eco(S)]
    out['righe'] = righe
    out['eco_per_fascia'] = eco
    out['taratura'] = OrderedDict((f, F[f]['calibrazione']) for f in sorted(F))
    # --- ia09 (copia netta, quota locale) e ia08 (contatto) dai lavori M
    M = {r['job'][1]: r for r in corse if r['job'][0] == 'M' and 'errore' not in r}
    if M:
        P = len(next(iter(M.values()))['pag'])
        Wm = A9.pesi_bootstrap(P)

        def gain(r, ch, m_):
            return A9.stima(np.array(r['num_%s_%s' % (ch, m_)]), np.array(r['den_' + ch]), Wm)
        mm = OrderedDict()
        for nome, r in M.items():
            netto_t = gain(r, 't', 'g') - gain(r, 't', 'n')
            netto_p = gain(r, 'p', 'g') - gain(r, 'p', 'n')
            lam = A9.V(1.0, np.ones_like(netto_t.b)) - netto_p.dividi(netto_t)
            a_cn = (gain(r, 't', 'tutto') - gain(r, 't', 'gram_n')).pos()
            a_gr = (gain(r, 't', 'tutto') - gain(r, 't', 'g')).pos()
            rho = a_cn.dividi(a_cn + a_gr)
            mm[nome] = dict(netto=netto_t, lam=lam, rho=rho, mi=r['mi'])
        gruppi = OrderedDict()
        for var in ['vere'] + [v for v in ('V0', 'V1', 'V2', 'V3', 'V4', 'N1') if v in VARIANTI]:
            nomi = ['vere'] if var == 'vere' else [n for n in mm if n.startswith(var + ':')]
            if not nomi:
                continue
            gruppi[var] = OrderedDict(
                libri=len(nomi), netto=A9.V.media([mm[n]['netto'] for n in nomi]), lam=A9.V.media([mm[n]['lam'] for n in nomi]),
                rho=A9.V.media([mm[n]['rho'] for n in nomi]), mi=float(np.mean([mm[n]['mi'] for n in nomi])))
        out['ia09'] = gruppi
    return out


def frazione(x_v, x_0, x_var):
    """Quanta strada (0 = come V0, 1 = come le vere) ha fatto la variante."""
    d = x_v - x_0
    return float((x_var - x_0) / d) if abs(d) > 1e-9 else float('nan')


def letture_manipolazione(man):
    """Per ogni variante: la manipolazione e' riuscita? (soglie nella preregistrazione)"""
    if not man or 'righe' not in man:
        return OrderedDict()
    r = man['righe']
    ia = man.get('ia09', {})
    out = OrderedDict()
    fo = lambda v, k: frazione(r['vere'][k], r['V0'][k], r[v][k])
    for v in ('V1', 'V2', 'V3', 'V4'):
        if v not in r or 'V0' not in r:
            continue
        d = OrderedDict()
        ok = True
        if v in ('V1', 'V3', 'V4') and 'V0' in ia and v in ia:
            fe = frazione(ia['vere']['netto'].p, ia['V0']['netto'].p, ia[v]['netto'].p)
            fl = frazione(ia['vere']['lam'].p, ia['V0']['lam'].p, ia[v]['lam'].p)
            d['eco_frazione_copia_netta'] = round(fe, 3)
            d['eco_frazione_quota_locale'] = round(fl, 3)
            ok &= bool(MANIP_BASSO <= fe <= MANIP_ALTO and fl >= LAMBDA_FRAZ)
        if v in ('V2', 'V3', 'V4'):
            fd = fo(v, 'D')
            d['ordine_frazione_D'] = round(fd, 3)
            d['ordine_frazione_D_altro_seme'] = round(fo(v, 'D2'), 3)
            ok &= bool(MANIP_BASSO <= fd <= MANIP_ALTO)
        if v in ('V2', 'V3', 'V4') and 'V0' in ia and v in ia:
            dm = ia[v]['mi'] - ia['V0']['mi']
            d['contatto_differenza_da_V0'] = round(dm, 4)
            ok &= bool(abs(dm) <= CONTATTO_TOL)
        if v == 'V4':
            ff = fo(v, 'forma')
            d['forma_frazione'] = round(ff, 3)
            dq = r['V4']['quota_nuove'] - r['V3']['quota_nuove']
            d['quota_nuove_differenza_da_V3'] = round(dq, 4)
            ok &= bool(MANIP_BASSO <= ff <= MANIP_ALTO and abs(dq) <= NUOVE_TOL)
        d['riuscita'] = bool(ok)
        out[v] = d
    return out


def letture(giud, man, paper, dis, c):
    """Letture preregistrate (vedi la preregistrazione)."""
    L = OrderedDict()
    A, K = giud.get('A'), giud.get('K')
    # ---- validita'
    val = OrderedDict()
    if A and 'V0a' in A['AUC']:
        v0a = A['AUC']['V0a']['media']
        val['riproduzione_ia01'] = OrderedDict(V0a=round(v0a, 4), atteso=RIPRODUZIONE_IA01, ok=bool(abs(v0a - RIPRODUZIONE_IA01) <= TOL_V0A))
        if 'V0' in A['AUC']:
            val['V0_contro_V0a'] = OrderedDict(differenza=round(A['AUC']['V0']['media'] - v0a, 4), ok=bool(abs(A['AUC']['V0']['media'] - v0a) <= TOL_V0))
    val['A_controlli'] = bool(A and A['valido'])
    val['K_controlli'] = bool(K and K['valido'])
    val['K_vede_V0'] = bool(K and 'V0' in K['AUC'] and K['AUC']['V0']['media'] >= K_VEDE_MIN)
    L['validita'] = val
    mi = letture_manipolazione(man)
    L['manipolazione'] = mi
    # ---- L1: V3
    da, dk = dis.get('A', {}), dis.get('K', {})
    if A and 'V3' in da:
        qa, qk = da['V3']['quota'], (dk['V3']['quota'] if 'V3' in dk else float('nan'))
        a_ok = bool(qa >= Q_SI_A and da['V3']['ic'][0] > DISCESA_MIN_CI)
        k_leggibile = bool(val['K_controlli'] and val['K_vede_V0'])
        k_ok = bool(k_leggibile and 'V3' in dk and qk >= Q_SI_K and dk['V3']['ic'][0] > 0)
        paper_ok = bool(paper.get('V3', {}).get('non_peggiora', False)) if paper else False
        neg_ok = bool(all(('N1' not in dis.get(j, {})) or dis[j]['N1']['discesa'] <= NEG_MAX for j in ('A', 'K') if j in dis))
        valido = bool(val.get('riproduzione_ia01', {}).get('ok', True) and val['A_controlli'] and mi.get('V3', {}).get('riuscita', False) and neg_ok)
        if not valido:
            esito = 'non leggibile'
        elif a_ok and k_ok and paper_ok:
            esito = 'si'
        elif a_ok and not k_ok:
            esito = ('solo A: possibile adattamento al giudice A (non vale come si)' if k_leggibile else
                     'solo A, e il giudice indipendente non vede il v21: non confermabile')
        elif a_ok and not paper_ok:
            esito = 'A scende ma i giudici del paper peggiorano: zona grigia'
        elif qa < Q_NO:
            esito = 'no'
        else:
            esito = 'zona grigia'
        L['L1_V3'] = OrderedDict(esito=esito, quota_A=round(qa, 4), quota_K=None if qk != qk else round(qk, 4), A_ok=a_ok, K_ok=k_ok,
                                 K_leggibile=k_leggibile, paper_ok=paper_ok, controllo_negativo_ok=neg_ok, manipolazione_V3=mi.get('V3', {}).get('riuscita'))
    # ---- L2: quote di V1 e V2 sulla discesa di V3 (media dei due ordini)
    for j, d in (('A', da), ('K', dk)):
        if 'V1' in d and 'V2' in d and 'V3' in d and d['V3']['discesa'] >= DISCESA_MIN_CI:
            d1, d2, d3 = d['V1']['discesa'], d['V2']['discesa'], d['V3']['discesa']
            q1 = (d1 + (d3 - d2)) / 2 / d3
            L['L2_%s' % j] = OrderedDict(V1=round(d1, 4), V2=round(d2, 4), V3=round(d3, 4), quota_V1=round(q1, 3), quota_V2=round(1 - q1, 3),
                                        interazione=round(d3 - d1 - d2, 4))
    # ---- L3: forma (V4 contro V3)
    if A and 'V3' in A['AUC'] and 'V4' in A['AUC']:
        b = A['_boot']
        dd = b['V3'] - b['V4']
        d34 = A['AUC']['V3']['media'] - A['AUC']['V4']['media']
        e = 'si' if (d34 >= FORMA_SI and ic(dd)[0] > 0) else 'no' if d34 <= FORMA_NO else 'zona grigia'
        L['L3_forma_A'] = OrderedDict(esito=e, discesa=round(d34, 4), ic=ic(dd), manipolazione_V4=mi.get('V4', {}).get('riuscita'))
        if K and 'V4' in K['AUC'] and 'V3' in K['AUC']:
            ddk = K['_boot']['V3'] - K['_boot']['V4']
            L['L3_forma_K'] = OrderedDict(discesa=round(K['AUC']['V3']['media'] - K['AUC']['V4']['media'], 4), ic=ic(ddk))
    # ---- L5/L6: controlli di ritocco
    ctrl = OrderedDict()
    for j, gd in giud.items():
        if gd and 'VR' in gd['AUC']:
            ctrl['vere_ritoccate_%s' % j] = OrderedDict(AUC=round(gd['AUC']['VR']['media'], 4), ok=bool(gd['AUC']['VR']['media'] <= VR_MAX))
    L['L6_vere_ritoccate'] = ctrl
    L['paper'] = paper
    return L


def giudici_paper_riassunto(corse):
    E = {r['job'][1]: r for r in corse if r['job'][0] == 'E' and 'errore' not in r}
    out = OrderedDict()
    if not E:
        return out
    for var in ('V0', 'V1', 'V2', 'V3', 'V4', 'N1'):
        n = [x for k, x in E.items() if k.startswith(var + ':')]
        if n:
            out[var] = OrderedDict(libri=len(n), e231=float(np.mean([x['AUC_e231'] for x in n])), e266=float(np.mean([x['AUC_e266'] for x in n])))
    n = [x for k, x in E.items() if k.startswith('VR:')]
    if n:
        out['VR'] = OrderedDict(libri=len(n), e231=float(np.mean([x['AUC_e231'] for x in n])), e266=float(np.mean([x['AUC_e266'] for x in n])))
    for v, d in out.items():
        if v in ('V0', 'VR') or 'V0' not in out:
            continue
        d['salita_e231'] = round(d['e231'] - out['V0']['e231'], 4)
        d['salita_e266'] = round(d['e266'] - out['V0']['e266'], 4)
        d['non_peggiora'] = bool(d['salita_e231'] <= PAPER_MAX and d['salita_e266'] <= PAPER_MAX)
    return out


def riproduzione_lm(corse, profA=None):
    """I modelli del testo di A rifatti qui contro quelli di ia01 (stessi semi e pieghe: devono coincidere)."""
    percorso = os.path.join(USCITA, 'ia01_corse.jsonl')
    mie = {(r['job'][1], r['job'][2]): r for r in corse if r['job'][0] == 'L' and 'errore' not in r}
    if not os.path.exists(percorso) or not mie:
        return dict(disponibile=False, modelli=len(mie))
    vecchie = {}
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            d = json.loads(l)
            if d.get('tipo') == 'A':
                vecchie[(d['job'][1], d['job'][2])] = d
    bpc, passi = [], []
    for k, r in mie.items():
        if k in vecchie:
            bpc.append(abs(vecchie[k]['info']['bpc_validazione'] - r['info']['bpc_validazione']))
            passi.append(abs(vecchie[k]['info']['passi'] - r['info']['passi']))
    if not bpc:
        return dict(disponibile=False, modelli=len(mie))
    out = OrderedDict(disponibile=True, modelli=len(bpc), max_diff_perdita_validazione=float(max(bpc)), max_diff_passi=int(max(passi)))
    # profili di sorpresa di 'vere' e del libro a13 (media sui semi) contro quelli di ia01 (arrotondati a 4 decimali)
    vecchi = defaultdict(lambda: defaultdict(list))
    for k, d in vecchie.items():
        for nome in ('vere', 'a13'):
            for p, pr in d['profili'].get(nome, {}).items():
                vecchi[nome][p].append(pr)
    if profA is not None:
        diff = []
        for nome, nuovo in (('vere', 'vere'), ('a13', 'V0a:a13')):
            for p, lst in vecchi[nome].items():
                if p in profA.get(nuovo, {}) and len(lst) == len(profA[nuovo][p]):
                    diff.append(float(np.max(np.abs(np.mean(lst, axis=0) - np.mean(profA[nuovo][p], axis=0)))))
        if diff:
            out['profili_confrontati'] = len(diff)
            out['profili_diff_massima'] = max(diff)
            out['profili_diff_media'] = float(np.mean(diff))
    return out


def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((k, pulisci(v)) for k, v in x.items() if not str(k).startswith('_'))
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, A9.V):
        return OrderedDict(punto=round(x.p, 4), ic=[round(v, 4) for v in x.ic()])
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return [round(float(v), 4) for v in x.ravel()]
    return x


def analisi(corse, versioni):
    c = G.contesto()
    profA, profK = defaultdict(lambda: defaultdict(list)), defaultdict(lambda: defaultdict(list))
    for r in corse:
        if r.get('errore'):
            continue
        if r['job'][0] == 'P':
            for n, d in r['profili'].items():
                for p, pr in d.items():
                    profA[n][p].append(pr)
        elif r['job'][0] == 'K':
            for n, d in r['profili'].items():
                for p, pr in d.items():
                    profK[n][p].append(pr)
    errori = [OrderedDict(job=r['job'], errore=r['errore']) for r in corse if r.get('errore')]
    giud = OrderedDict()
    if profA:
        giud['A'] = giudizio_giudice(profA, c, 'A (sorpresa, rete GRU di ia01)')
    if profK:
        giud['K'] = giudizio_giudice(profK, c, 'K (indipendente: n-grammi a caratteri con memoria di pagina)')
    dis = OrderedDict((j, discese(g)) for j, g in giud.items())
    man = manipolazione(corse, c)
    paper = giudici_paper_riassunto(corse)
    lett = letture(giud, man, paper, dis, c)
    info_k = [r['info'] for r in corse if r['job'][0] == 'K' and 'errore' not in r]
    ris = OrderedDict(esperimento=NOME, versioni=versioni, errori=errori, riproduzione_lm=riproduzione_lm(corse, profA), giudici=giud, discese=dis,
                      manipolazione=man, giudici_paper=paper, giudice_K_scelte=info_k, letture=lett)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulisci(ris), f, ensure_ascii=False, indent=1)
        f.write('\n')
    scrivi_md(ris)
    return ris


def f4(x):
    return '-' if x is None or x != x else '%.4f' % x


def scrivi_md(ris):
    r = ris
    L = r['letture']
    o = ['# ia11 - rifarlo (la prova del nove)', '',
         'Soglie nella preregistrazione `preregistrazioni/ia11.md`. AUC: media sui 10 libri v21 senza messaggio (b13-b22); intervalli al 95% col bootstrap '
         'sulle pagine (lo stesso ricampionamento per tutte le varianti); discesa = AUC di V0 meno AUC della variante.', '']
    v = L.get('validita', {})
    o.append('## Validita')
    for k, x in v.items():
        o.append('- %s: %s' % (k, json.dumps(pulisci(x), ensure_ascii=False)))
    if 'L1_V3' in L:
        o += ['', '## Lettura principale (V3 = eco + ordine)', '- **%s**' % L['L1_V3']['esito'], '- dettagli: %s' % json.dumps(pulisci(L['L1_V3']), ensure_ascii=False)]
    for j, gd in r['giudici'].items():
        o += ['', '## Giudice %s' % gd['nome'], '', 'Controlli: %s; negativo (media di %d etichette) %s; valido: %s' % (
            json.dumps(pulisci(gd['controlli']), ensure_ascii=False), len(gd['negativo']['valori']), f4(gd['negativo']['media']), gd['valido']), '',
            '| variante | AUC media (se) | IC 95% pagine | min-max | discesa da V0 (IC) | quota dell\'eccesso tolta |', '|---|---|---|---|---|---|']
        for var, a in gd['AUC'].items():
            d = r['discese'][j].get(var)
            o.append('| %s | %s (%s) | %s | %s-%s | %s | %s |' % (var, f4(a['media']), f4(a['se']), a['ic'] if a['ic'] else '-', f4(a['minimo']), f4(a['massimo']),
                                                                  ('%s (%s)' % (f4(d['discesa']), d['ic'])) if d else '-', f4(d['quota']) if d else '-'))
    o += ['', '## Giudici del paper (media sui libri; e231 e e266)', '', '| variante | e231 | e266 | salita e231 | salita e266 | non peggiora (soglia +%.2f) |' % PAPER_MAX, '|---|---|---|---|---|---|']
    for var, d in r['giudici_paper'].items():
        o.append('| %s | %s | %s | %s | %s | %s |' % (var, f4(d['e231']), f4(d['e266']), f4(d.get('salita_e231')), f4(d.get('salita_e266')), d.get('non_peggiora', '-')))
    o += ['', '## Verifica di manipolazione (le misure delle varianti contro quelle delle vere)', '']
    man = r['manipolazione']
    if man:
        o += ['| testo | D (ia10, stesse famiglie) | D (altro seme) | costo di forma delle parole nuove (bit per glifo) | quota di parole nuove |', '|---|---|---|---|---|']
        for var, x in man['righe'].items():
            o.append('| %s | %s | %s | %s | %s |' % (var, f4(x['D']), f4(x['D2']), f4(x['forma']), f4(x['quota_nuove'])))
        if 'ia09' in man:
            o += ['', '| testo | copia netta (ia09, bit per parola) | quota locale | rho | contatto ultimo -> primo glifo (g di ia08, bit) |', '|---|---|---|---|---|']
            for var, x in man['ia09'].items():
                o.append('| %s | %s | %s | %s | %s |' % (var, f4(x['netto'].p), f4(x['lam'].p), f4(x['rho'].p), f4(x['mi'])))
        o += ['', 'Letture di manipolazione: %s' % json.dumps(pulisci(L['manipolazione']), ensure_ascii=False)]
        o += ['', 'Eco per fascia (parole frequenti con parola uguale, rare con parola uguale, tutte con parola a una modifica, al netto del riferimento; fasce S1 S2 S3 R1 R2 R4 R8): %s' % json.dumps(pulisci(man['eco_per_fascia']), ensure_ascii=False)]
        o += ['', 'Taratura per piega (parametri): %s' % json.dumps(pulisci(OrderedDict((f, x['parametri']) for f, x in man['taratura'].items())), ensure_ascii=False)]
    for k in ('L2_A', 'L2_K', 'L3_forma_A', 'L3_forma_K', 'L6_vere_ritoccate'):
        if k in L:
            o += ['', '- %s: %s' % (k, json.dumps(pulisci(L[k]), ensure_ascii=False))]
    o += ['', 'Riproduzione dei modelli del testo di ia01: %s' % json.dumps(pulisci(r['riproduzione_lm']), ensure_ascii=False)]
    if r['errori']:
        o += ['', 'ERRORI: %s' % json.dumps(pulisci(r['errori']), ensure_ascii=False)]
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(o) + '\n')


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def main():
    import torch
    import numpy
    import scipy
    import sklearn
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__, scipy=scipy.__version__,
                    scikit_learn=sklearn.__version__)
    os.makedirs(USCITA, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    fasi = os.environ.get('FASI', 'taratura,giudizio,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d; pieghe %d; semi %s; libri giudicati %s; libri di taratura %s' % (len(c['ids']), NF, SEMI, CHIAVI, LIBRI_TARA), flush=True)
    os.makedirs(G.LIBRI, exist_ok=True)
    servono = ['a%d' % k for k in CHIAVI] + ['b%d' % k for k in list(CHIAVI) + list(LIBRI_TARA)]
    mancano = [n for n in servono if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01; non si rigenerano qui)' % (', '.join(mancano), G.LIBRI))
    percorso = os.path.join(USCITA, 'ia11_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if not x.get('errore')]
    elif 'taratura' in fasi or 'giudizio' in fasi:
        open(percorso, 'w').close()
    if 'taratura' in fasi or 'giudizio' in fasi:
        processi = int(os.environ.get('PROCESSI', 10))
        inizio = time.time()
        with get_context('spawn').Pool(processi, initializer=G.avvia_processo) as pool:
            for tappa in (['taratura'] if 'taratura' in fasi else []) + (['giudizio'] if 'giudizio' in fasi else []):
                fatte = {json.dumps(x['job']) for x in corse}
                L = lavori([tappa])
                da_fare = [j for j in L if json.dumps(list(j)) not in fatte]
                da_fare.sort(key=lambda j: {'L': 0, 'F': 1, 'P': 2, 'K': 3, 'M': 4, 'E': 5}[j[0]])
                print('%s: %d da fare, %d gia fatti' % (tappa, len(da_fare), len(L) - len(da_fare)), flush=True)
                for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                    if r.get('errore'):
                        print('ERRORE %s: %s\n%s' % (r['job'], r['errore'], r.get('traccia', '')), flush=True)
                    else:
                        corse.append(r)
                    with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')
                    print('[%d/%d %.0f min] %s (%.0f s)' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo']), flush=True)
    elif os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if not x.get('errore')]
    if 'analisi' in fasi:
        analisi(corse, versioni)


if __name__ == '__main__':
    main()
