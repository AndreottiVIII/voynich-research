# -*- coding: utf-8 -*-
"""Esperimento IA8 (ia08): perche' il giudice A "sorpresa" di ia01 se ne accorge?

ia01 ha mostrato che un modello del testo (GRU a caratteri, ~67.000 parametri) rende le pagine del voynichizzatore v21
(libri a13-a22) piu' sorprendenti delle pagine vere (differenza media +0,13 bit per segno, AUC 0,751). Qui si scompone
quella differenza. Tre ipotesi (preregistrazione: preregistrazioni/ia08.md):
  H1 legami fra parole: nel Voynich vero la fine di una parola rende prevedibile l'inizio della successiva; il v21 no.
  H2 parole nuove: il v21 inventa parole che non esistono nel manoscritto, e li' la rete si sorprende.
  H3 dove cadono i picchi: i segni piu' sorprendenti (sopra il 95o percentile delle pagine vere) in che parte del testo stanno.

Che cosa fa il codice
- Riusa ia01 (importato, non modificato): pagine, pieghe, vocabolario, modello del testo (addestra_lm), sorprese, libri
  (percorso_libro, libro), rimescolamento (rimescola_parole), semi (G.SEMI = 1, 2). Il modello di ogni piega e seme e' lo
  stesso di ia01: stessa divisione 10% / 90% e stesso seme. Sono copiate da ia01.lavoro_A solo le righe che dividono le
  pagine e chiamano addestra_lm (lavoro_A fa tutto in un pezzo e non si puo' importare a spezzoni).
- Per ogni segno delle pagine di prova (vere, libri a13-a22, controlli) si registra la sorpresa e la sua "casella":
  posizione (inizio riga, inizio parola, dentro la parola, spazio, a capo) per stato della parola (nota = compare nelle
  pagine di addestramento della piega; nuova = no). Per le parole note anche la frequenza (classi). Per le nuove, se
  sono assenti da tutte le altre pagine vere. Si registrano solo somme per pagina (numero di segni, bit, segni sopra la
  soglia dei picchi), mai parole.
- La soglia dei picchi e' il 95o percentile della sorpresa dei segni delle pagine vere della piega fuori, per modello.
- H1 senza rete: informazione mutua fra l'ultimo glifo di una parola e il primo della successiva (stessa riga), contata
  direttamente; riferimento = stesso testo con le parole rimescolate nella riga.
- Controlli: ctrl:parole (parole rimescolate nella riga, come ia01), ctrl:nuove (vere con il 15% di parole cambiate in
  parole che non esistono), latino con legami piantati per l'informazione mutua, null (pagine vere divise a caso in due).

Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia08_perche_rete.json e .md e, una riga
per lavoro, risultati/ia08_corse.jsonl (con RIPRENDI=1 i lavori fatti non si rifanno).

Variabili (oltre a quelle di ia01: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, CHIAVI, SEMI, PASSI, OGNI, PAZIENZA, NASCOSTO,
CADUTA, USCITA, LIBRI): PROCESSI, RIPRENDI, FASI (rete, analisi, mi: 'rete,analisi' e' il predefinito; 'mi' esegue solo
l'informazione mutua e i suoi controlli e stampa), NULLI (divisioni a caso, 200), BOOT (ricampionamenti, 1000),
FRAZ_NUOVE (0,15). I libri a13-a22 devono esistere gia' (li ha fatti ia01 in dati/cache/ia01_libri); con SOLO_CONTROLLI
si generano i libri di prova (catene di Markov sul latino), come in ia01.
"""
import json, math, os, random, sys, time, zlib
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402

NOME = 'ia08_perche_rete'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF, SEMI, CHIAVI = G.NF, G.SEMI, G.CHIAVI
NULLI = int(os.environ.get('NULLI', 200))
BOOT = int(os.environ.get('BOOT', 1000))
FRAZ_NUOVE = float(os.environ.get('FRAZ_NUOVE', 0.15))
N_RIM = 5                     # rimescolamenti per l'informazione mutua
N_PERM = 50                   # permutazioni per il riferimento a caso dell'informazione mutua (stima puntuale)
PERC_PICCO = 95

# ---- soglie delle letture (fissate nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_NUOVE_Q = 0.03         # H2: la quota di parole nuove nel v21 supera quella delle vere di almeno 3 punti
SOGLIA_NUOVE_SI = 0.40        # H2: la parte "nuove" porta almeno il 40% della differenza
SOGLIA_NUOVE_NO = 0.25        # H2: sotto il 25% (e quota non piu' alta) = no
SOGLIA_POS_NUOVE_QUOTA = 0.50  # controllo positivo ctrl:nuove: almeno il 50% della sua differenza e' nelle parole nuove
SOGLIA_POS_NUOVE_DQ = 0.06    # ... e la quota di parole nuove sale di almeno 6 punti
SOGLIA_G_MISURABILE = 0.02    # H1: informazione mutua dovuta all'ordine nelle vere almeno 0,02 bit
SOGLIA_R_SI, SOGLIA_R_NO = 0.50, 0.80
SOGLIA_INIZIO_NOTE = 0.05     # H1, rete: sorpresa all'inizio delle parole note dopo una parola nota, almeno +0,05 bit
SOGLIA_MI_PIANTATO = 0.10     # controllo positivo MI: latino con legami piantati almeno 0,10 bit
SOGLIA_MI_LATINO = 0.01       # controllo positivo MI: latino vero, limite basso dell'intervallo sopra zero e almeno 0,01
BANDA_MI_NEG = 0.01           # controllo negativo MI: due serie di rimescolamenti dello stesso testo, |differenza| <= 0,01
SOGLIA_SENS = 2.0             # la differenza totale deve essere almeno 2 volte il 97,5o percentile del nullo
PICCHI_ATTESI = (0.045, 0.055)  # la soglia e' il 95o percentile delle vere: la quota di picchi nelle vere deve starci
H3_SI, H3_GRIGIA = 0.50, 0.25

P_PAR, P_SP, P_NL, P_RIGA, P_INI, P_DENTRO = 0, 1, 2, 3, 4, 5      # posizione del segno
POS_NOMI = OrderedDict([('riga', P_RIGA), ('ini', P_INI), ('dentro', P_DENTRO), ('sp', P_SP), ('nl', P_NL)])
FREQ_ETICHETTE = ['1 volta', '2-4 volte', '5-19 volte', '20 o piu']
CELLE10 = ['%s|%s' % (p, s) for p in POS_NOMI for s in ('nota', 'nuova')]
PARTI = OrderedDict([
    ('nuove', ['riga|nuova', 'ini|nuova', 'dentro|nuova']),
    ('inizio_note', ['ini|nota']),
    ('riga_note', ['riga|nota']),
    ('interno_note', ['dentro|nota']),
    ('spazi_acapo', ['sp|nota', 'sp|nuova', 'nl|nota', 'nl|nuova'])])
PARTI_ETICHETTE = OrderedDict([
    ('nuove', 'glifi di parole nuove'),
    ('inizio_note', 'primo glifo di parole note (non a inizio riga)'),
    ('riga_note', 'primo glifo di parole note a inizio riga'),
    ('interno_note', 'glifi interni di parole note'),
    ('spazi_acapo', 'spazi e a capo')])
CAMPI = list(CELLE10) + ['ini|nota|dopo_nota', 'ini|nota|dopo_nuova', 'ass|ini', 'ass|dentro']
CAMPI += ['f%d|%s' % (c, d) for c in range(4) for d in ('ini', 'dentro')] + ['T|tutte', 'T|nuove', 'T|assenti']
IX = {n: i for i, n in enumerate(CAMPI)}
K = 3 * len(CAMPI)            # per campo: numero di segni, bit, segni sopra la soglia
INSIEMI = ['vere'] + ['a%d' % k for k in CHIAVI] + ['ctrl:parole', 'ctrl:nuove']
LIBRI_V21 = ['a%d' % k for k in CHIAVI]
SEME_NUOVE = 880001


def classe_freq(n):
    return 0 if n == 1 else 1 if n <= 4 else 2 if n <= 19 else 3


# ---------------------------------------------------------------- parole: stato e controlli

_C = {}


def pagine_con_parola():
    """parola -> insieme delle pagine vere che la contengono (uguale in ogni processo)."""
    if 'pc' not in _C:
        d = defaultdict(set)
        for p, rows in G.contesto()['vere'].items():
            for _, ws in rows:
                for w in ws:
                    d[w].add(p)
        _C['pc'] = d
    return _C['pc']


def muta_parole(vere, seme, frazione, glifi, esistenti):
    """Controllo positivo per H2: ogni parola, con probabilita' `frazione`, cambia un glifo (o ne prende uno in piu' se e'
    di un solo glifo) in modo da dare una parola che non compare in nessuna pagina vera. Stesse pagine, stessi a capo."""
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in vere.items():
        nr = []
        for ini, ws in rows:
            nw = []
            for w in ws:
                if rnd.random() < frazione:
                    nuova = None
                    for _ in range(30):
                        if len(w) == 1:
                            cand = w + (glifi[rnd.randrange(len(glifi))],)
                        else:
                            i = rnd.randrange(len(w))
                            g = glifi[rnd.randrange(len(glifi))]
                            if g == w[i]:
                                continue
                            cand = w[:i] + (g,) + w[i + 1:]
                        if cand not in esistenti:
                            nuova = cand
                            break
                    if nuova is None:
                        nuova = w + (glifi[rnd.randrange(len(glifi))],) * 2
                    w = nuova
                nw.append(w)
            nr.append((ini, nw))
        out[p] = nr
    return out


def rows_insieme(nome):
    c = G.contesto()
    if nome == 'vere':
        return c['vere']
    if nome == 'ctrl:nuove':
        if 'nuove' not in _C:
            _C['nuove'] = muta_parole(c['vere'], SEME_NUOVE, FRAZ_NUOVE, c['voc'][4:], pagine_con_parola())
        return _C['nuove']
    return G.libro(nome)


def etichette(rows, idx, stato):
    """Segni di una pagina (nello stesso ordine di G.codifica) con la loro casella: ids, posizione, parola nuova (0/1),
    classe di frequenza (0-3, -1 se nuova), assente da tutte le altre pagine vere (0/1), la parola precedente era nuova
    (solo per l'inizio di parola, altrimenti -1). Spazio e a capo prendono lo stato della parola che chiudono."""
    ids, pos, nuova, fc, ass, prev = [], [], [], [], [], []

    def agg(i, p, st=(0, -1, 0), pv=-1):
        ids.append(i)
        pos.append(p)
        nuova.append(st[0])
        fc.append(st[1])
        ass.append(st[2])
        prev.append(pv)

    for ini, ws in rows:
        if ini:
            agg(2, P_PAR)
        st_prec = (0, -1, 0)
        for j, w in enumerate(ws):
            st = stato(w)
            if j:
                agg(0, P_SP, st_prec)
            for k, s in enumerate(w):
                p = (P_RIGA if j == 0 else P_INI) if k == 0 else P_DENTRO
                agg(idx.get(s, 3), p, st, st_prec[0] if (k == 0 and j > 0) else -1)
            st_prec = st
        agg(1, P_NL, st_prec)
    return tuple(np.array(x, dtype=np.int64) for x in (ids, pos, nuova, fc, ass, prev))


def accumula(s, pos, nuova, fc, ass, prev, soglia):
    """Per una pagina: matrice (campi, 3) = numero di segni, bit, segni sopra la soglia."""
    out = np.zeros((len(CAMPI), 3))

    def metti(nome, mask):
        v = s[mask]
        out[IX[nome]] = (len(v), float(v.sum()), int((v > soglia).sum()))
    prima = (pos == P_RIGA) | (pos == P_INI)
    for p, cod in POS_NOMI.items():
        for st, v in (('nota', 0), ('nuova', 1)):
            metti('%s|%s' % (p, st), (pos == cod) & (nuova == v))
    metti('ini|nota|dopo_nota', (pos == P_INI) & (nuova == 0) & (prev == 0))
    metti('ini|nota|dopo_nuova', (pos == P_INI) & (nuova == 0) & (prev == 1))
    metti('ass|ini', prima & (ass == 1))
    metti('ass|dentro', (pos == P_DENTRO) & (ass == 1))
    for c in range(4):
        metti('f%d|ini' % c, prima & (nuova == 0) & (fc == c))
        metti('f%d|dentro' % c, (pos == P_DENTRO) & (nuova == 0) & (fc == c))
    metti('T|tutte', prima)
    metti('T|nuove', prima & (nuova == 1))
    metti('T|assenti', prima & (ass == 1))
    return out


# ---------------------------------------------------------------- lavoro di rete (uno per seme e piega)

def lavoro_N(seme, piega):
    """Il modello del testo di ia01 (stessa divisione, stesso seme), poi la sorpresa di ogni segno delle pagine di prova per
    tutti gli insiemi, ridotta alle somme per pagina."""
    inizio = time.time()
    c = G.contesto()
    pagine = list(c['ids'])
    test = [p for p in pagine if c['fold'][p] == piega]
    resto = [p for p in pagine if c['fold'][p] != piega]
    random.Random(3964 + 100 * seme + piega).shuffle(resto)          # (righe copiate da G.lavoro_A, fino alla chiamata di addestra_lm)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([c['ids'][p] for p in ps])
    m, info = G.addestra_lm(flusso(add), flusso(val), c['V'], 1000 * seme + piega)
    cont = Counter(w for p in add for _, ws in c['vere'][p] for w in ws)
    pc = pagine_con_parola()
    vuoto = frozenset()
    dati = OrderedDict()
    for nome in INSIEMI:
        rows = rows_insieme(nome)
        ps = [p for p in test if p in rows]
        lab = []
        for p in ps:
            def stato(w, p=p):
                n = cont.get(w, 0)
                if n:
                    return (0, classe_freq(n), 0)
                return (1, -1, 1 if pc.get(w, vuoto) <= {p} else 0)
            lab.append(etichette(rows[p], c['idx'], stato))
            if nome == 'vere':
                assert np.array_equal(lab[-1][0], c['ids'][p]), 'segni diversi da ia01'
            else:
                assert np.array_equal(lab[-1][0], G.codifica(rows[p], c['idx'])), 'segni diversi da ia01'
        dati[nome] = (ps, lab, G.sorprese(m, [l[0] for l in lab]))
    ps, lab, s = dati['vere']
    soglia = float(np.percentile(np.concatenate([x[l[1] != P_PAR] for l, x in zip(lab, s)]), PERC_PICCO))
    stat = OrderedDict()
    for nome, (ps, lab, s) in dati.items():
        stat[nome] = OrderedDict((p, np.round(accumula(x, *l[1:], soglia), 4).ravel().tolist()) for p, l, x in zip(ps, lab, s))
    info['bpc_vere_fuori'] = float(np.mean([np.mean(x) for x in dati['vere'][2]]))
    return dict(job=['N', seme, piega], tipo='N', info=info, soglia=soglia, stat=stat, tempo=round(time.time() - inizio, 1))


def lavoro(job):
    return lavoro_N(job[1], job[2])


def lavori_rete():
    L = [('N', s, f) for s in SEMI for f in range(NF)]
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


# ---------------------------------------------------------------- statistiche sulle somme per pagina

def col(Z, nomi, k):
    return sum(Z[..., 3 * IX[n] + k] for n in nomi)


def rapporto(a, b):
    return a / np.maximum(b, 1e-12)


def statistiche(Z):
    """Z (..., K) = somme dei campi su un gruppo di pagine -> dizionario di misure (stessa forma di Z senza l'ultimo asse)."""
    N = col(Z, CELLE10, 0)
    r = OrderedDict()
    r['bps'] = rapporto(col(Z, CELLE10, 1), N)
    r['picchi'] = rapporto(col(Z, CELLE10, 2), N)
    for parte, celle in PARTI.items():
        n, b, a = col(Z, celle, 0), col(Z, celle, 1), col(Z, celle, 2)
        r['f_' + parte] = rapporto(n, N)
        r['m_' + parte] = rapporto(b, n)
        r['c_' + parte] = rapporto(b, N)
        r['p_' + parte] = rapporto(a, N)
        r['pr_' + parte] = rapporto(a, n)
    T = col(Z, ['T|tutte'], 0)
    r['q_nuove'] = rapporto(col(Z, ['T|nuove'], 0), T)
    r['q_assenti'] = rapporto(col(Z, ['T|assenti'], 0), T)
    r['m_ass'] = rapporto(col(Z, ['ass|ini', 'ass|dentro'], 1), col(Z, ['ass|ini', 'ass|dentro'], 0))
    r['m_ini_dopo_nota'] = rapporto(col(Z, ['ini|nota|dopo_nota'], 1), col(Z, ['ini|nota|dopo_nota'], 0))
    r['m_ini_dopo_nuova'] = rapporto(col(Z, ['ini|nota|dopo_nuova'], 1), col(Z, ['ini|nota|dopo_nuova'], 0))
    Tn = col(Z, ['T|tutte'], 0) - col(Z, ['T|nuove'], 0)
    for c in range(4):
        r['qf%d' % c] = rapporto(col(Z, ['f%d|ini' % c], 0), Tn)
        r['mi_f%d' % c] = rapporto(col(Z, ['f%d|ini' % c], 1), col(Z, ['f%d|ini' % c], 0))
        r['md_f%d' % c] = rapporto(col(Z, ['f%d|dentro' % c], 1), col(Z, ['f%d|dentro' % c], 0))
    for cella in CELLE10:
        r['n_' + cella] = rapporto(col(Z, [cella], 0), N)
        r['b_' + cella] = rapporto(col(Z, [cella], 1), col(Z, [cella], 0))
    return r


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def matrici_pagine(corse):
    """insieme -> (pagine ordinate, matrice (pagine, K) media sui semi)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in corse:
        for nome, d in r['stat'].items():
            for p, v in d.items():
                acc[nome][p].append(v)
    X = OrderedDict()
    pag = None
    for nome in INSIEMI:
        if nome not in acc:
            continue
        ps = sorted(acc[nome])
        for p in ps:
            if len(acc[nome][p]) != len(SEMI):
                raise SystemExit('FERMO: la pagina %s dell\'insieme %s ha %d semi invece di %d' % (p, nome, len(acc[nome][p]), len(SEMI)))
        if pag is None:
            pag = ps
        if ps != pag:
            raise SystemExit('FERMO: l\'insieme %s non ha le stesse pagine delle vere' % nome)
        X[nome] = np.array([np.mean(acc[nome][p], axis=0) for p in pag])
    return pag, X


def divisioni_nulle(P):
    """Divisioni a caso delle pagine in due meta' (A e B), uguali per tutte le misure."""
    out = []
    for s in range(NULLI):
        ordine = list(range(P))
        random.Random(3980 + s).shuffle(ordine)
        a = np.zeros(P, dtype=bool)
        a[ordine[:P // 2]] = True
        out.append(a)
    return out


def pesi_bootstrap(P):
    rng = np.random.default_rng(880002)
    return np.stack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(BOOT)]).astype(float)


def ic(x):
    return [float(v) for v in np.percentile(x, [2.5, 97.5])]


def ic_base(punto, boot):
    """Intervallo "di base" del bootstrap: 2*punto meno i percentili. Serve per l'informazione mutua del plug-in, dove i
    ricampionamenti con pagine ripetute spostano la stima (e un intervallo a percentili non conterrebbe nemmeno la stima)."""
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return [float(2 * punto - hi), float(2 * punto - lo)]


def analisi_rete(pag, X, corse):
    """Scomposizione, H2, H3 e parte di rete di H1, con intervalli (bootstrap sulle pagine) e distribuzione nulla."""
    P = len(pag)
    W = pesi_bootstrap(P)
    split = divisioni_nulle(P)
    pt, bt = {}, {}
    for nome, M in X.items():
        pt[nome] = statistiche(M.sum(0))
        bt[nome] = statistiche(W @ M)
    nullo = defaultdict(list)
    for a in split:
        sa, sb = statistiche(X['vere'][a].sum(0)), statistiche(X['vere'][~a].sum(0))
        for k in sa:
            nullo[k].append(float(sb[k] - sa[k]))
    nullo = {k: np.array(v) for k, v in nullo.items()}
    null97 = {k: float(np.percentile(np.abs(v), 97.5)) for k, v in nullo.items()}

    def delta(insieme, chiave):
        """Differenza (insieme meno vere): puntuale, intervallo, e per il v21 media sui libri (errore standard fra i libri)."""
        if insieme == 'v21':
            d = [pt[b][chiave] - pt['vere'][chiave] for b in LIBRI_V21]
            db = np.mean([bt[b][chiave] - bt['vere'][chiave] for b in LIBRI_V21], axis=0)
            return dict(punto=float(np.mean(d)), ic=ic(db), se_libri=float(np.std(d, ddof=1) / len(d) ** 0.5) if len(d) > 1 else 0.0,
                        minimo=float(min(d)), massimo=float(max(d)), boot=db)
        db = bt[insieme][chiave] - bt['vere'][chiave]
        return dict(punto=float(pt[insieme][chiave] - pt['vere'][chiave]), ic=ic(db), boot=db)

    def media_v21(chiave):
        return float(np.mean([pt[b][chiave] for b in LIBRI_V21]))

    def media_v21_boot(chiave):
        return np.mean([bt[b][chiave] for b in LIBRI_V21], axis=0)

    ris = OrderedDict()
    chiavi = ['bps', 'picchi', 'q_nuove', 'q_assenti', 'm_ass', 'm_ini_dopo_nota', 'm_ini_dopo_nuova']
    chiavi += ['%s_%s' % (a, p) for p in PARTI for a in ('c', 'f', 'm', 'p', 'pr')]
    chiavi += ['qf%d' % c for c in range(4)] + ['mi_f%d' % c for c in range(4)] + ['md_f%d' % c for c in range(4)]
    chiavi += ['n_' + x for x in CELLE10] + ['b_' + x for x in CELLE10]
    for ins in ('v21', 'ctrl:parole', 'ctrl:nuove'):
        d = OrderedDict()
        for k in chiavi:
            x = delta(ins, k)
            d[k] = dict(punto=x['punto'], ic=x['ic'], null97=null97[k])
            if ins == 'v21':
                d[k].update(se_libri=x['se_libri'], minimo=x['minimo'], massimo=x['massimo'],
                            vere=float(pt['vere'][k]), v21=media_v21(k))
            else:
                d[k].update(vere=float(pt['vere'][k]), valore=float(pt[ins][k]))
        # quote della differenza e scomposizione quota/costo
        db = {k: delta(ins, k)['boot'] for k in ('bps', 'picchi')}
        tot = d['bps']['punto']
        tq, tc = [], []
        for p in PARTI:
            share = d['c_' + p]['punto'] / tot if tot else None
            sb = delta(ins, 'c_' + p)['boot'] / db['bps']
            d['c_' + p]['quota_della_differenza'] = share
            d['c_' + p]['quota_ic'] = ic(sb)
            # effetto quota / effetto costo (media sui libri per il v21)
            gruppo = LIBRI_V21 if ins == 'v21' else [ins]
            # punto medio: f_b*m_b - f_v*m_v = (f_b - f_v) * m_medio + f_medio * (m_b - m_v), esatto
            eq = lambda S: np.mean([(S[b]['f_' + p] - S['vere']['f_' + p]) * (S[b]['m_' + p] + S['vere']['m_' + p]) / 2 for b in gruppo], axis=0)
            ec = lambda S: np.mean([(S[b]['f_' + p] + S['vere']['f_' + p]) / 2 * (S[b]['m_' + p] - S['vere']['m_' + p]) for b in gruppo], axis=0)
            d['c_' + p]['effetto_quota'] = float(eq(pt))
            d['c_' + p]['effetto_costo'] = float(ec(pt))
            d['c_' + p]['effetto_quota_ic'] = ic(eq(bt))
            d['c_' + p]['effetto_costo_ic'] = ic(ec(bt))
            tq.append((eq(pt), eq(bt)))
            tc.append((ec(pt), ec(bt)))
            d['p_' + p]['quota_dell_eccesso'] = d['p_' + p]['punto'] / d['picchi']['punto'] if d['picchi']['punto'] else None
            d['p_' + p]['quota_ic'] = ic(delta(ins, 'p_' + p)['boot'] / db['picchi'])
        d['scomposizione_totale'] = OrderedDict(
            effetto_quota=float(sum(x[0] for x in tq)), effetto_quota_ic=ic(sum(x[1] for x in tq)),
            effetto_costo=float(sum(x[0] for x in tc)), effetto_costo_ic=ic(sum(x[1] for x in tc)))
        ris[ins] = d
    # distanza fra i profili della differenza (quote delle 5 parti)
    prof = {ins: np.array([ris[ins]['c_' + p]['quota_della_differenza'] for p in PARTI], dtype=float) for ins in ris}
    ris['distanza_profili'] = OrderedDict(
        v21_da_ctrl_parole=float(np.abs(prof['v21'] - prof['ctrl:parole']).sum()),
        v21_da_ctrl_nuove=float(np.abs(prof['v21'] - prof['ctrl:nuove']).sum()))
    # per libro: misure principali
    per_libro = OrderedDict()
    for b in LIBRI_V21:
        per_libro[b] = OrderedDict((k, float(pt[b][k] - pt['vere'][k])) for k in ('bps', 'picchi', 'q_nuove', 'm_ini_dopo_nota') +
                                   tuple('c_' + p for p in PARTI))
    ris['per_libro'] = per_libro
    ris['nullo'] = OrderedDict((k, dict(media=float(v.mean()), sd=float(v.std(ddof=1)), p97_5_assoluto=null97[k])) for k, v in nullo.items()
                               if k in chiavi)
    ris['assoluti'] = OrderedDict((ins, OrderedDict((k, float(pt[ins][k])) for k in chiavi)) for ins in pt if ins in ('vere', 'ctrl:parole', 'ctrl:nuove'))
    ris['assoluti']['v21'] = OrderedDict((k, media_v21(k)) for k in chiavi)
    ris['_null97'] = null97
    ris['_W'] = W
    ris['_split'] = split
    ris['_pt'], ris['_bt'] = pt, bt
    # media pagina per pagina dei bit per segno, per il confronto con ia01
    pagbit = lambda M: float(np.mean(rapporto(sum(M[:, 3 * IX[c] + 1] for c in CELLE10), sum(M[:, 3 * IX[c]] for c in CELLE10))))
    ris['bit_medi_per_pagina'] = OrderedDict(vere=pagbit(X['vere']), v21=float(np.mean([pagbit(X[b]) for b in LIBRI_V21])))
    ris['bit_medi_per_pagina']['differenza'] = ris['bit_medi_per_pagina']['v21'] - ris['bit_medi_per_pagina']['vere']
    return ris


def verifica_ia01(corse):
    """Confronta i modelli di questa corsa con quelli di ia01 (stesso seme, stessa piega): perdita di validazione e bit medi per
    pagina. Solo un controllo di riproduzione, non entra nelle letture."""
    percorso = os.path.join(USCITA, 'ia01_corse.jsonl')
    if not os.path.exists(percorso):
        return dict(disponibile=False)
    vecchie = {}
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            d = json.loads(l)
            if d.get('tipo') == 'A':
                vecchie[(d['job'][1], d['job'][2])] = d
    diff, bpc, passi = [], [], []
    for r in corse:
        v = vecchie.get((r['job'][1], r['job'][2]))
        if not v:
            continue
        bpc.append(abs(v['info']['bpc_validazione'] - r['info']['bpc_validazione']))
        passi.append(v['info']['passi'] - r['info']['passi'])
        for nome, d in r['stat'].items():
            if nome not in v['profili']:
                continue
            for p, vec in d.items():
                M = np.array(vec).reshape(len(CAMPI), 3)
                mio = sum(M[IX[c], 1] for c in CELLE10) / sum(M[IX[c], 0] for c in CELLE10)
                diff.append(abs(mio - v['profili'][nome][p][0]))
    if not diff:
        return dict(disponibile=False)
    return OrderedDict(disponibile=True, modelli=len(bpc), max_diff_perdita_validazione=float(max(bpc)), max_diff_passi=int(max(abs(x) for x in passi)),
                       pagine_confrontate=len(diff), max_diff_bit_pagina=float(max(diff)), media_diff_bit_pagina=float(np.mean(diff)))


# ---------------------------------------------------------------- H1 senza rete: informazione mutua

def mappa_glifi(vere):
    gl = sorted({s for rows in vere.values() for _, ws in rows for w in ws for s in w})
    return {s: i for i, s in enumerate(gl)}, len(gl) + 1


def coppie_riga(ws, mappa, V, variante):
    out = []
    for a, b in zip(ws[:-1], ws[1:]):
        x = a[0] if variante == 'pri_pri' else a[-1]
        y = b[-1] if variante == 'ult_ult' else b[0]
        out.append((mappa.get(x, V - 1), mappa.get(y, V - 1)))
    return out


def coppie_testo(libro, pagine, mappa, V, variante):
    """Per pagina: lista (ultimo glifo, primo glifo) di ogni coppia di parole vicine nella stessa riga."""
    out = []
    for p in pagine:
        pr = []
        for _, ws in libro.get(p, []):
            pr += coppie_riga(ws, mappa, V, variante)
        out.append(np.array(pr, dtype=np.int64).reshape(-1, 2))
    return out


def matrici_coppie(cp, V):
    return np.array([np.bincount(a[:, 0] * V + a[:, 1], minlength=V * V) for a in cp], dtype=np.float64)


def mi_bit(Z, V):
    """Informazione mutua (bit) di una o piu' tabelle di conteggi (..., V*V), stima diretta."""
    Z = np.asarray(Z, dtype=float)
    T = Z.reshape(Z.shape[:-1] + (V, V))
    N = T.sum((-1, -2))
    p = T / np.maximum(N, 1e-12)[..., None, None]
    pr, pc = p.sum(-1, keepdims=True), p.sum(-2, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = p * np.log2(p / (pr * pc))
    return np.nansum(t, axis=(-1, -2))


def rimescolamenti(libro, nome, n=N_RIM, base=None):
    out = []
    for i in range(n):
        seme = base if (base is not None and i == 0) else G.seme_di('ia08:rim:%s:%d' % (nome, i))
        out.append(G.rimescola_parole(libro, seme))
    return out


def piantato(vere, seme, prob=0.5):
    """Controllo positivo per l'informazione mutua: nel testo, con probabilita' `prob`, il primo glifo di ogni parola (non la
    prima della riga) e' sostituito da un glifo che dipende solo dall'ultimo glifo della parola prima."""
    rnd = random.Random(seme)
    gl = sorted({s for rows in vere.values() for _, ws in rows for w in ws for s in w})
    f = {g: gl[(5 * i + 2) % len(gl)] for i, g in enumerate(gl)}
    out = OrderedDict()
    for p, rows in vere.items():
        nr = []
        for ini, ws in rows:
            nw = [ws[0]] if ws else []
            for w in ws[1:]:
                if rnd.random() < prob:
                    w = (f[nw[-1][-1]],) + tuple(w[1:])
                nw.append(w)
            nr.append((ini, nw))
        out[p] = nr
    return out


def g_ordine(Mt, Ms, V, pesi=None, maschera=None):
    """Informazione mutua dovuta all'ordine = MI del testo meno MI media dei suoi rimescolamenti nella riga (stesse pagine).
    Mt (pagine, V*V); Ms lista di matrici dei rimescolamenti. Con `pesi` (B, pagine) restituisce un vettore (B,); con
    `maschera` usa solo quelle pagine."""
    if pesi is not None:
        return mi_bit(pesi @ Mt, V) - np.mean([mi_bit(pesi @ M, V) for M in Ms], axis=0)
    if maschera is not None:
        return float(mi_bit(Mt[maschera].sum(0), V) - np.mean([mi_bit(M[maschera].sum(0), V) for M in Ms]))
    return float(mi_bit(Mt.sum(0), V) - np.mean([mi_bit(M.sum(0), V) for M in Ms]))


def mi_caso(cp, V, n=N_PERM, seme=1):
    """MI grezza e media su n permutazioni della seconda colonna (riferimento a caso: bias da conteggi finiti)."""
    a = np.concatenate(cp)
    rng = np.random.default_rng(seme)
    grezza = float(mi_bit(np.bincount(a[:, 0] * V + a[:, 1], minlength=V * V), V))
    caso = [float(mi_bit(np.bincount(a[:, 0] * V + rng.permutation(a[:, 1]), minlength=V * V), V)) for _ in range(n)]
    return grezza, float(np.mean(caso))


def analisi_mi(pag, libri, vere, W, split, variante='ult_pri'):
    """libri: nome -> libro (pagina -> righe); 'vere' incluso. Restituisce per ogni testo: MI grezza, riferimento a caso, MI
    dovuta all'ordine (con intervallo), piu' nullo sulle divisioni delle vere."""
    mappa, V = mappa_glifi(vere)
    testi = OrderedDict()
    for nome, lib in libri.items():
        base = 396001 if nome == 'vere' else None
        rim = rimescolamenti(lib, nome, base=base)
        cp = coppie_testo(lib, pag, mappa, V, variante)
        testi[nome] = dict(cp=cp, M=matrici_coppie(cp, V), Ms=[matrici_coppie(coppie_testo(r, pag, mappa, V, variante), V) for r in rim])
    out = OrderedDict()
    for nome, t in testi.items():
        grezza, caso = mi_caso(t['cp'], V)
        g = g_ordine(t['M'], t['Ms'], V)
        gb = g_ordine(t['M'], t['Ms'], V, pesi=W)
        out[nome] = dict(coppie=int(sum(len(a) for a in t['cp'])), MI_grezza=grezza, MI_caso=caso, MI_corretta=grezza - caso, g=g, g_ic=ic_base(g, gb),
                         MI_rimescolato=float(np.mean([mi_bit(M.sum(0), V) for M in t['Ms']])))
        t['gb'] = gb
    nomi_v21 = [n for n in libri if n != 'vere']
    if nomi_v21:
        gv = np.mean([testi[n]['gb'] for n in nomi_v21], axis=0)
        gv0 = np.mean([out[n]['g'] for n in nomi_v21])
        ver = testi['vere']['gb']
        r0 = float(gv0 / out['vere']['g']) if out['vere']['g'] else None
        rb = gv / np.where(np.abs(ver) > 1e-9, ver, np.nan)
        out['v21_media'] = dict(g=float(gv0), g_ic=ic_base(gv0, gv), g_vere=out['vere']['g'], g_vere_ic=out['vere']['g_ic'],
                           differenza=float(out['vere']['g'] - gv0), differenza_ic=ic_base(out['vere']['g'] - gv0, ver - gv),
                           rapporto=r0, rapporto_ic=ic_base(r0, rb) if r0 is not None else None,
                           se_libri=float(np.std([out[n]['g'] for n in nomi_v21], ddof=1) / len(nomi_v21) ** 0.5) if len(nomi_v21) > 1 else 0.0)
        # nullo: divisioni a caso delle vere (g di una meta' meno g dell'altra)
        d = []
        for a in split:
            d.append(g_ordine(testi['vere']['M'], testi['vere']['Ms'], V, maschera=~a) - g_ordine(testi['vere']['M'], testi['vere']['Ms'], V, maschera=a))
        out['nullo_divisioni'] = dict(media=float(np.mean(d)), sd=float(np.std(d, ddof=1)), p97_5_assoluto=float(np.percentile(np.abs(d), 97.5)))
    return out


def controllo_mi_latino(variante='ult_pri'):
    """Controllo positivo e negativo per l'informazione mutua, su latino (mai sul Voynich): latino vero, latino con legami
    piantati, e due serie di rimescolamenti dello stesso testo."""
    vere, _ = G.carica_latino()
    pag = sorted(vere)
    mappa, V = mappa_glifi(vere)
    rng = np.random.default_rng(880003)
    W = np.stack([np.bincount(rng.integers(0, len(pag), len(pag)), minlength=len(pag)) for _ in range(BOOT)]).astype(float)
    out = OrderedDict()
    pian = piantato(vere, 880004)
    for nome, lib in (('latino', vere), ('latino_piantato', pian)):
        rim = rimescolamenti(lib, nome, n=5)
        M = matrici_coppie(coppie_testo(lib, pag, mappa, V, variante), V)
        Ms = [matrici_coppie(coppie_testo(r, pag, mappa, V, variante), V) for r in rim]
        out[nome] = dict(g=g_ordine(M, Ms, V), g_ic=ic_base(g_ordine(M, Ms, V), g_ordine(M, Ms, V, pesi=W)), MI_grezza=float(mi_bit(M.sum(0), V)),
                         MI_rimescolato=float(np.mean([mi_bit(m.sum(0), V) for m in Ms])))
        if nome == 'latino':
            mi_rim = [float(mi_bit(m.sum(0), V)) for m in Ms]
            out['negativo'] = dict(differenza_serie=float(np.mean(mi_rim[:2]) - np.mean(mi_rim[2:])), rimescolamenti=mi_rim)
    ok_pos = out['latino_piantato']['g'] >= SOGLIA_MI_PIANTATO and out['latino']['g_ic'][0] > 0 and out['latino']['g'] >= SOGLIA_MI_LATINO
    ok_neg = abs(out['negativo']['differenza_serie']) <= BANDA_MI_NEG
    out['positivo_superato'] = bool(ok_pos)
    out['negativo_superato'] = bool(ok_neg)
    return out


# ---------------------------------------------------------------- letture

def lettura_H2(R, ctrl):
    v = R['v21']
    dq, n97q = v['q_nuove']['punto'], v['q_nuove']['null97']
    s_new = v['c_nuove']['quota_della_differenza']
    if not ctrl['valida_H2']:
        return OrderedDict(esito='non leggibile', motivo='un controllo non e\' superato: %s' % '; '.join(ctrl['motivi_H2']))
    a = dq >= SOGLIA_NUOVE_Q and dq > n97q
    b = s_new is not None and s_new >= SOGLIA_NUOVE_SI
    if a and b:
        e = 'si'
    elif (not a) and s_new is not None and s_new < SOGLIA_NUOVE_NO:
        e = 'no'
    else:
        e = 'zona grigia'
    return OrderedDict(esito=e, quota_nuove_vere=v['q_nuove']['vere'], quota_nuove_v21=v['q_nuove']['v21'], differenza_quota=dq, null97_quota=n97q,
                       quota_differenza_nelle_nuove=s_new, quota_ic=v['c_nuove']['quota_ic'], criterio_a=bool(a), criterio_b=bool(b))


def lettura_H1(R, mi, ctrl):
    """Due bracci. Informazione mutua (senza rete): sì se i legami nelle vere sono misurabili e il v21 ne ha al massimo la meta';
    no se ne ha almeno l'80%. Rete: sì se all'inizio delle parole note dopo una parola nota il v21 e' piu' sorprendente di
    almeno 0,05 bit e sopra il nullo; no se non supera il nullo. Esito: sì se i due bracci dicono sì, no se dicono no; altrimenti
    zona grigia (anche se la rete non e' leggibile perche' il suo controllo positivo fallisce: allora resta il solo braccio MI)."""
    v = R['v21']
    pm = mi['v21_media']
    d_ini, n97 = v['m_ini_dopo_nota']['punto'], v['m_ini_dopo_nota']['null97']
    d_ctrl = R['ctrl:parole']['m_ini_dopo_nota']['punto']
    g_ver, g_lo = pm['g_vere'], pm['g_vere_ic'][0]
    r = pm['rapporto']
    misurabile = g_ver >= SOGLIA_G_MISURABILE and g_lo > 0
    out = OrderedDict(g_vere=g_ver, g_vere_ic=pm['g_vere_ic'], g_v21=pm['g'], g_v21_ic=pm['g_ic'], rapporto_MI=r, rapporto_ic=pm['rapporto_ic'],
                      inizio_note_dopo_nota=d_ini, null97=n97, inizio_note_ctrl_parole=d_ctrl, misurabile=bool(misurabile))
    if not ctrl['valida_H1']:
        out.update(esito='non leggibile', motivo='un controllo non è superato: %s' % '; '.join(ctrl['motivi_H1']))
        return out
    if not misurabile:
        out.update(esito='non leggibile', motivo='i legami nelle pagine vere non sono misurabili con questa statistica (g sotto %.2f bit o intervallo che include 0)' % SOGLIA_G_MISURABILE)
        return out
    e_mi = 'si' if (r is not None and r <= SOGLIA_R_SI) else 'no' if (r is not None and r >= SOGLIA_R_NO) else 'zona grigia'
    rete_ok = ctrl['rete_leggibile_H1']
    if rete_ok:
        e_rete = 'si' if (d_ini >= SOGLIA_INIZIO_NOTE and d_ini > n97) else 'no' if d_ini <= n97 else 'zona grigia'
    else:
        e_rete = 'non leggibile'
    if e_mi == e_rete and e_mi in ('si', 'no'):
        e = e_mi
    else:
        e = 'zona grigia'
    out.update(esito=e, esito_informazione_mutua=e_mi, esito_rete=e_rete)
    return out


def lettura_H3(R, ctrl):
    v = R['v21']
    E, n97 = v['picchi']['punto'], v['picchi']['null97']
    out = OrderedDict(picchi_vere=v['picchi']['vere'], picchi_v21=v['picchi']['v21'], eccesso=E, null97=n97)
    if not ctrl['valida_H3']:
        out.update(esito='non leggibile', motivo='un controllo non e\' superato: %s' % '; '.join(ctrl['motivi_H3']))
        return out
    if E <= n97:
        out.update(esito='nessun eccesso di picchi oltre il caso', gruppi={})
        return out
    gr = OrderedDict()
    for p in PARTI:
        s = v['p_' + p]['quota_dell_eccesso']
        gr[p] = OrderedDict(quota=s, ic=v['p_' + p]['quota_ic'], esito='si' if s >= H3_SI else 'zona grigia' if s >= H3_GRIGIA else 'no')
    out.update(esito='letto', gruppi=gr)
    return out


def controlli(R, mi, mi_lat, rip):
    v = R['v21']
    cn = R['ctrl:nuove']
    cp = R['ctrl:parole']
    c = OrderedDict()
    c['positivo_nuove'] = OrderedDict(
        quota_nelle_nuove=cn['c_nuove']['quota_della_differenza'], differenza_quota_token=cn['q_nuove']['punto'],
        superato=bool(cn['c_nuove']['quota_della_differenza'] is not None and cn['c_nuove']['quota_della_differenza'] >= SOGLIA_POS_NUOVE_QUOTA
                      and cn['q_nuove']['punto'] >= SOGLIA_POS_NUOVE_DQ))
    c['positivo_parole'] = OrderedDict(
        differenza_bit=cp['bps']['punto'], null97_bit=cp['bps']['null97'], inizio_note_dopo_nota=cp['m_ini_dopo_nota']['punto'],
        null97_inizio=cp['m_ini_dopo_nota']['null97'], superato=bool(cp['bps']['punto'] > cp['bps']['null97']),
        rete_all_inizio=bool(cp['m_ini_dopo_nota']['punto'] > cp['m_ini_dopo_nota']['null97']))
    c['sensibilita'] = OrderedDict(differenza_v21=v['bps']['punto'], null97=v['bps']['null97'], superato=bool(v['bps']['punto'] >= SOGLIA_SENS * v['bps']['null97']))
    c['picchi_vere'] = OrderedDict(quota=v['picchi']['vere'], banda=PICCHI_ATTESI, superato=bool(PICCHI_ATTESI[0] <= v['picchi']['vere'] <= PICCHI_ATTESI[1]))
    c['mi_latino'] = OrderedDict(positivo=mi_lat['positivo_superato'], negativo=mi_lat['negativo_superato'])
    c['riproduzione_ia01'] = rip
    mot = lambda cond, t: [t] if not cond else []
    c['motivi_H2'] = mot(c['positivo_nuove']['superato'], 'controllo positivo ctrl:nuove') + mot(c['sensibilita']['superato'], 'sensibilita')
    # H1: il braccio informazione mutua dipende solo dai controlli sul latino; il braccio rete anche da ctrl:parole e dalla sensibilita'
    c['motivi_H1'] = (mot(mi_lat['positivo_superato'], 'controllo positivo MI (latino)') + mot(mi_lat['negativo_superato'], 'controllo negativo MI (latino)'))
    c['rete_leggibile_H1'] = bool(c['positivo_parole']['rete_all_inizio'] and c['sensibilita']['superato'])
    c['motivi_H3'] = mot(c['sensibilita']['superato'], 'sensibilita') + mot(c['picchi_vere']['superato'], 'quota di picchi nelle vere')
    c['valida_H1'], c['valida_H2'], c['valida_H3'] = (not c['motivi_H1']), (not c['motivi_H2']), (not c['motivi_H3'])
    return c


# ---------------------------------------------------------------- scrittura

def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((k, pulisci(v)) for k, v in x.items() if not str(k).startswith('_') and k != 'boot')
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def f3(x):
    return '-' if x is None else '%.3f' % x


def f2(x):
    return '-' if x is None else '%.2f' % x


def pc(x):
    return '-' if x is None else '%.1f%%' % (100 * x)


def scrivi(ris, versioni):
    R, mi, mi_lat, ctrl, rip = ris['rete'], ris['mi'], ris['mi_latino'], ris['controlli'], ris['riproduzione_ia01']
    parametri = OrderedDict(NF=NF, SEMI=SEMI, CHIAVI=CHIAVI, NULLI=NULLI, BOOT=BOOT, FRAZ_NUOVE=FRAZ_NUOVE, PERC_PICCO=PERC_PICCO, N_RIM=N_RIM, N_PERM=N_PERM,
                            PASSI=G.PASSI, OGNI=G.OGNI, PAZIENZA=G.PAZIENZA, NASCOSTO=G.NASCOSTO, CADUTA=G.CADUTA, SOLO_CONTROLLI=SOLO_CONTROLLI,
                            soglie=OrderedDict(SOGLIA_NUOVE_Q=SOGLIA_NUOVE_Q, SOGLIA_NUOVE_SI=SOGLIA_NUOVE_SI, SOGLIA_NUOVE_NO=SOGLIA_NUOVE_NO,
                                               SOGLIA_POS_NUOVE_QUOTA=SOGLIA_POS_NUOVE_QUOTA, SOGLIA_POS_NUOVE_DQ=SOGLIA_POS_NUOVE_DQ,
                                               SOGLIA_G_MISURABILE=SOGLIA_G_MISURABILE, SOGLIA_R_SI=SOGLIA_R_SI, SOGLIA_R_NO=SOGLIA_R_NO,
                                               SOGLIA_INIZIO_NOTE=SOGLIA_INIZIO_NOTE, SOGLIA_MI_PIANTATO=SOGLIA_MI_PIANTATO,
                                               SOGLIA_MI_LATINO=SOGLIA_MI_LATINO, BANDA_MI_NEG=BANDA_MI_NEG, SOGLIA_SENS=SOGLIA_SENS,
                                               PICCHI_ATTESI=PICCHI_ATTESI, H3_SI=H3_SI, H3_GRIGIA=H3_GRIGIA))
    out = OrderedDict(esperimento='ia08', parametri=parametri, versioni=versioni, impronte_libri=ris.get('impronte_libri'),
                      letture=ris['letture'], controlli=ctrl, riproduzione_ia01=rip, rete=pulisci(R), informazione_mutua=pulisci(mi),
                      informazione_mutua_varianti=pulisci(ris.get('mi_varianti')), informazione_mutua_latino=pulisci(mi_lat),
                      modelli_del_testo=ris.get('modelli'))
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulisci(out), f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    L = ris['letture']
    r = ['# ia08 — perche\' la rete se ne accorge', '']
    r.append('Prima riga di lettura (soglie nella preregistrazione `preregistrazioni/ia08.md`). Le differenze sono "v21 meno vere" (media sui %d libri), '
             'in bit per segno salvo dove detto; intervalli al 95%% col bootstrap sulle pagine.' % len(LIBRI_V21))
    r.append('')
    r.append('**H2, parole nuove:** %s. Quota di parole nuove (per token): vere %s, v21 %s (differenza %+.3f, nullo 97,5%% %.3f); la parte "glifi di parole nuove" porta %s della '
             'differenza (intervallo %s-%s).' % (
                 L['H2']['esito'].upper(), pc(L['H2'].get('quota_nuove_vere')), pc(L['H2'].get('quota_nuove_v21')), L['H2'].get('differenza_quota', float('nan')),
                 L['H2'].get('null97_quota', float('nan')), pc(L['H2'].get('quota_differenza_nelle_nuove')),
                 pc((L['H2'].get('quota_ic') or [None, None])[0]), pc((L['H2'].get('quota_ic') or [None, None])[1])) + (' ' + L['H2']['motivo'] if 'motivo' in L['H2'] else ''))
    h1 = L['H1']
    r.append('**H1, legami fra parole:** %s. Informazione mutua (ultimo glifo, primo della parola dopo) dovuta all\'ordine: vere %s bit (%s-%s), v21 %s (%s-%s), rapporto %s; '
             'sorpresa all\'inizio delle parole note dopo una parola nota: %+.3f bit (nullo %.3f; ctrl:parole %+.3f).' % (
                 h1['esito'].upper(), f3(h1['g_vere']), f3(h1['g_vere_ic'][0]), f3(h1['g_vere_ic'][1]), f3(h1['g_v21']), f3(h1['g_v21_ic'][0]), f3(h1['g_v21_ic'][1]),
                 f2(h1['rapporto_MI']), h1['inizio_note_dopo_nota'], h1['null97'], h1['inizio_note_ctrl_parole']) +
             (' Braccio informazione mutua: %s; braccio rete: %s.' % (h1['esito_informazione_mutua'], h1['esito_rete']) if 'esito_rete' in h1 else '') +
             (' ' + h1['motivo'] if 'motivo' in h1 else ''))
    h3 = L['H3']
    r.append('**H3, dove cadono i picchi:** %s. Segni sopra la soglia: vere %s, v21 %s (eccesso %+.4f, nullo %.4f).' % (
        h3['esito'].upper(), pc(h3['picchi_vere']), pc(h3['picchi_v21']), h3['eccesso'], h3['null97']))
    for p, d in (h3.get('gruppi') or {}).items():
        r.append('  - %s: %s dell\'eccesso (%s-%s) -> %s' % (PARTI_ETICHETTE[p], pc(d['quota']), pc(d['ic'][0]), pc(d['ic'][1]), d['esito']))
    r += ['', '## Controlli', '']
    r.append('- positivo H2, ctrl:nuove (%d%% delle parole cambiate in parole che non esistono): quota della differenza nelle parole nuove %s (soglia %.2f), quota di parole nuove %+.3f (soglia %.2f): %s' % (
        round(100 * FRAZ_NUOVE), pc(ctrl['positivo_nuove']['quota_nelle_nuove']), SOGLIA_POS_NUOVE_QUOTA, ctrl['positivo_nuove']['differenza_quota_token'],
        SOGLIA_POS_NUOVE_DQ, 'SUPERATO' if ctrl['positivo_nuove']['superato'] else 'NON superato'))
    pp = ctrl['positivo_parole']
    r.append('- positivo H1, rete, ctrl:parole: sorpresa al primo glifo delle parole note dopo una nota %+.3f (97,5%% del nullo %.3f): %s (condizione per il braccio rete di H1); '
             'differenza totale %+.3f (nullo %.3f): %s (solo descrittivo)' % (
                 pp['inizio_note_dopo_nota'], pp['null97_inizio'], 'SUPERATO' if pp['rete_all_inizio'] else 'NON superato',
                 pp['differenza_bit'], pp['null97_bit'], 'sopra il nullo' if pp['superato'] else 'sotto il nullo'))
    r.append('- positivo e negativo H1 (informazione mutua) su latino: legami piantati %s bit (soglia %.2f), latino vero %s bit (intervallo %s-%s, soglia %.3f): %s; '
             'due serie di rimescolamenti dello stesso testo, differenza %+.4f (banda %.2f): %s' % (
                 f3(mi_lat['latino_piantato']['g']), SOGLIA_MI_PIANTATO, f3(mi_lat['latino']['g']), f3(mi_lat['latino']['g_ic'][0]), f3(mi_lat['latino']['g_ic'][1]),
                 SOGLIA_MI_LATINO, 'SUPERATO' if mi_lat['positivo_superato'] else 'NON superato', mi_lat['negativo']['differenza_serie'], BANDA_MI_NEG,
                 'SUPERATO' if mi_lat['negativo_superato'] else 'NON superato'))
    r.append('- sensibilita: differenza totale del v21 %+.3f bit per segno, 97,5%% del nullo (%d divisioni a caso delle pagine vere) %.3f, rapporto richiesto almeno %.0f: %s' % (
        ctrl['sensibilita']['differenza_v21'], NULLI, ctrl['sensibilita']['null97'], SOGLIA_SENS, 'SUPERATO' if ctrl['sensibilita']['superato'] else 'NON superato'))
    r.append('- quota di segni sopra la soglia nelle vere: %s (attesa %s-%s): %s' % (pc(ctrl['picchi_vere']['quota']), pc(PICCHI_ATTESI[0]), pc(PICCHI_ATTESI[1]),
                                                                              'SUPERATO' if ctrl['picchi_vere']['superato'] else 'NON superato'))
    if rip.get('disponibile'):
        r.append('- riproduzione di ia01 (non e\' una soglia): %d modelli confrontati, differenza massima della perdita di validazione %.5f, dei passi %d, dei bit medi per pagina %.4f '
                 '(media %.5f su %d pagine)' % (rip['modelli'], rip['max_diff_perdita_validazione'], rip['max_diff_passi'], rip['max_diff_bit_pagina'],
                                              rip['media_diff_bit_pagina'], rip['pagine_confrontate']))
    else:
        r.append('- riproduzione di ia01: file `ia01_corse.jsonl` non disponibile, non confrontato')
    bm = R['bit_medi_per_pagina']
    r.append('- bit medi per segno, media sulle pagine (come ia01): vere %.3f, v21 %.3f, differenza %+.4f (ia01: +0.1320)' % (bm['vere'], bm['v21'], bm['differenza']))
    v = R['v21']
    r += ['', '## Scomposizione della differenza v21 meno vere (bit per segno, tutti i segni insieme)', '',
          'Quota = peso della parte sui segni; costo = bit per segno nella parte. La differenza della parte e\' la somma di un effetto quota (cambia quanti segni '
          'ci sono in quella parte) e di un effetto costo (cambia quanto costano); i due effetti si calcolano col punto medio fra vere e v21 e sommano esattamente '
          'alla differenza. Le colonne ctrl: sono le stesse quote della differenza per i due controlli.', '',
          '| parte | quota segni vere | quota segni v21 | costo vere | costo v21 | differenza (IC 95%) | quota della differenza (IC) | effetto quota | effetto costo | ctrl:parole | ctrl:nuove |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for p in PARTI:
        d = v['c_' + p]
        r.append('| %s | %s | %s | %.3f | %.3f | %+.4f (%+.4f; %+.4f) | %s (%s-%s) | %+.4f | %+.4f | %s | %s |' % (
            PARTI_ETICHETTE[p], pc(v['f_' + p]['vere']), pc(v['f_' + p]['v21']), v['m_' + p]['vere'], v['m_' + p]['v21'], d['punto'], d['ic'][0], d['ic'][1],
            pc(d['quota_della_differenza']), pc(d['quota_ic'][0]), pc(d['quota_ic'][1]), d['effetto_quota'], d['effetto_costo'],
            pc(R['ctrl:parole']['c_' + p]['quota_della_differenza']), pc(R['ctrl:nuove']['c_' + p]['quota_della_differenza'])))
    st = v['scomposizione_totale']
    r.append('| totale | | | %.3f | %.3f | %+.4f (%+.4f; %+.4f) | 100%% | %+.4f (%+.4f; %+.4f) | %+.4f (%+.4f; %+.4f) | %+.4f | %+.4f |' % (
        R['assoluti']['vere']['bps'], R['assoluti']['v21']['bps'], v['bps']['punto'], v['bps']['ic'][0], v['bps']['ic'][1],
        st['effetto_quota'], st['effetto_quota_ic'][0], st['effetto_quota_ic'][1], st['effetto_costo'], st['effetto_costo_ic'][0], st['effetto_costo_ic'][1],
        R['ctrl:parole']['bps']['punto'], R['ctrl:nuove']['bps']['punto']))
    r.append('')
    r.append('Distanza fra i profili (somma delle differenze assolute fra le quote della differenza): v21 da ctrl:parole %.2f, v21 da ctrl:nuove %.2f (piu\' piccola = piu\' simile; descrittivo).' % (
        R['distanza_profili']['v21_da_ctrl_parole'], R['distanza_profili']['v21_da_ctrl_nuove']))
    r += ['', '## H2: parole nuove', '', '| misura | vere | v21 | differenza (IC 95%) | nullo 97,5% | ctrl:nuove |', '|---|---|---|---|---|---|']
    for k, t in (('q_nuove', 'quota di parole nuove (per token)'), ('q_assenti', 'quota di parole assenti da tutte le altre pagine vere'), ('m_ass', 'bit per segno nelle parole assenti')):
        d = v[k]
        r.append('| %s | %.4f | %.4f | %+.4f (%+.4f; %+.4f) | %.4f | %+.4f |' % (t, d['vere'], d['v21'], d['punto'], d['ic'][0], d['ic'][1], d['null97'], R['ctrl:nuove'][k]['punto']))
    r += ['', 'Costo per segno delle parole nuove: vere %.3f, v21 %.3f bit (differenza %+.3f).' % (v['m_nuove']['vere'], v['m_nuove']['v21'], v['m_nuove']['punto'])]
    r += ['', '## H3: segni sopra la soglia dei picchi (95o percentile delle vere, per modello)', '',
          '| parte | picchi nella parte vere | v21 | parte dei picchi vere | parte dei picchi v21 | eccesso (IC 95%) | quota dell\'eccesso (IC) |', '|---|---|---|---|---|---|---|']
    for p in PARTI:
        d = v['p_' + p]
        r.append('| %s | %s | %s | %s | %s | %+.4f (%+.4f; %+.4f) | %s (%s-%s) |' % (
            PARTI_ETICHETTE[p], pc(v['pr_' + p]['vere']), pc(v['pr_' + p]['v21']), pc(d['vere'] / v['picchi']['vere']), pc(d['v21'] / v['picchi']['v21']),
            d['punto'], d['ic'][0], d['ic'][1], pc(d['quota_dell_eccesso']), pc(d['quota_ic'][0]), pc(d['quota_ic'][1])))
    r += ['', '## H1: informazione mutua fra ultimo glifo di una parola e primo della successiva (stessa riga), in bit', '',
          '| testo | coppie | MI grezza | a caso (permutazioni) | corretta | rimescolato nella riga | dovuta all\'ordine g (IC 95%) |', '|---|---|---|---|---|---|---|']
    for n, d in mi.items():
        if n in ('v21_media', 'nullo_divisioni'):
            continue
        r.append('| %s | %d | %.4f | %.4f | %.4f | %.4f | %+.4f (%+.4f; %+.4f) |' % (n, d['coppie'], d['MI_grezza'], d['MI_caso'], d['MI_corretta'], d['MI_rimescolato'], d['g'], d['g_ic'][0], d['g_ic'][1]))
    p = mi['v21_media']
    r.append('')
    r.append('v21 (media dei libri): g %+.4f (%+.4f; %+.4f), errore standard fra i libri %.4f; vere meno v21 %+.4f (%+.4f; %+.4f); rapporto v21/vere %s (intervallo %s-%s). '
             'Nullo (vere divise a caso in due, differenza di g): sd %.4f, 97,5%% del valore assoluto %.4f.' % (
                 p['g'], p['g_ic'][0], p['g_ic'][1], p['se_libri'], p['differenza'], p['differenza_ic'][0], p['differenza_ic'][1], f2(p['rapporto']),
                 f2((p['rapporto_ic'] or [None, None])[0]), f2((p['rapporto_ic'] or [None, None])[1]), mi['nullo_divisioni']['sd'], mi['nullo_divisioni']['p97_5_assoluto']))
    if ris.get('mi_varianti'):
        r += ['', 'Altre coppie di glifi (descrittivo, nessuna soglia): g nelle vere, nel v21 e differenza.', '', '| coppia | g vere | g v21 | vere meno v21 (IC 95%) |', '|---|---|---|---|']
        for nome, d in ris['mi_varianti'].items():
            q = d['v21_media']
            r.append('| %s | %+.4f | %+.4f | %+.4f (%+.4f; %+.4f) |' % (nome, q['g_vere'], q['g'], q['differenza'], q['differenza_ic'][0], q['differenza_ic'][1]))
    r += ['', 'Latino (controllo): legami piantati g %+.4f, latino vero g %+.4f (%+.4f; %+.4f).' % (
        mi_lat['latino_piantato']['g'], mi_lat['latino']['g'], mi_lat['latino']['g_ic'][0], mi_lat['latino']['g_ic'][1])]
    r += ['', '## H1 con la rete: sorpresa all\'inizio delle parole note', '', '| misura | vere | v21 | differenza (IC 95%) | nullo 97,5% | ctrl:parole |', '|---|---|---|---|---|---|']
    for k, t in (('m_ini_dopo_nota', 'primo glifo di parola nota dopo una parola nota'), ('m_ini_dopo_nuova', 'primo glifo di parola nota dopo una parola nuova'),
                 ('m_inizio_note', 'primo glifo di parola nota, tutte (non a inizio riga)')):
        d = v[k]
        r.append('| %s | %.3f | %.3f | %+.4f (%+.4f; %+.4f) | %.4f | %+.4f |' % (t, d['vere'], d['v21'], d['punto'], d['ic'][0], d['ic'][1], d['null97'], R['ctrl:parole'][k]['punto']))
    r += ['', '## Parole note per frequenza (nelle pagine di addestramento della piega)', '',
          '| classe | quota delle parole note vere | v21 | bit al primo glifo vere | v21 | bit dentro la parola vere | v21 |', '|---|---|---|---|---|---|---|']
    for c in range(4):
        r.append('| %s | %s | %s | %.3f | %.3f | %.3f | %.3f |' % (FREQ_ETICHETTE[c], pc(v['qf%d' % c]['vere']), pc(v['qf%d' % c]['v21']), v['mi_f%d' % c]['vere'],
                                                                  v['mi_f%d' % c]['v21'], v['md_f%d' % c]['vere'], v['md_f%d' % c]['v21']))
    r += ['', '## Posizione e stato della parola: quota dei segni e bit per segno', '', '| casella | quota segni vere | v21 | bit vere | v21 | differenza dei bit |', '|---|---|---|---|---|---|']
    for cella in CELLE10:
        r.append('| %s | %s | %s | %.3f | %.3f | %+.3f |' % (cella, pc(v['n_' + cella]['vere']), pc(v['n_' + cella]['v21']), v['b_' + cella]['vere'], v['b_' + cella]['v21'], v['b_' + cella]['punto']))
    r += ['', '## Per libro (differenza v21 meno vere)', '', '| libro | bit per segno | picchi | quota di parole nuove | inizio note dopo nota | parti: ' + ' / '.join(PARTI) + ' |', '|---|---|---|---|---|---|']
    for b, d in R['per_libro'].items():
        r.append('| %s | %+.4f | %+.4f | %+.4f | %+.4f | %s |' % (b, d['bps'], d['picchi'], d['q_nuove'], d['m_ini_dopo_nota'], ' / '.join('%+.3f' % d['c_' + p] for p in PARTI)))
    if ris.get('modelli'):
        r += ['', 'Modelli del testo: bit per segno sulla validazione %.3f; passi medi %d.' % (
            float(np.mean([x['bpc_validazione'] for x in ris['modelli']])), int(np.mean([x['passi'] for x in ris['modelli']])))]
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def impronte(nomi):
    return OrderedDict((n, '%08x' % (zlib.crc32(open(G.percorso_libro(n), 'rb').read()) & 0xffffffff)) for n in nomi)


def esegui_analisi(corse, versioni, modelli):
    c = G.contesto()
    pag, X = matrici_pagine(corse)
    rip = verifica_ia01(corse)
    R = analisi_rete(pag, X, corse)
    W, split = R['_W'], R['_split']
    vere = c['vere']
    libri = OrderedDict([('vere', vere)] + [(b, G.libro(b)) for b in LIBRI_V21])
    mi = analisi_mi(pag, libri, vere, W, split)
    varianti = OrderedDict()
    for var in ('pri_pri', 'ult_ult'):
        varianti[var] = analisi_mi(pag, libri, vere, W, split, variante=var)
    lat = controllo_mi_latino()
    ctrl = controlli(R, mi, lat, rip)
    letture = OrderedDict(H1=lettura_H1(R, mi, ctrl), H2=lettura_H2(R, ctrl), H3=lettura_H3(R, ctrl))
    ris = dict(rete=R, mi=mi, mi_varianti=varianti, mi_latino=lat, controlli=ctrl, letture=letture, riproduzione_ia01=rip,
               impronte_libri=impronte(LIBRI_V21), modelli=modelli)
    return scrivi(ris, versioni), ris


def prepara_libri():
    """I libri a13-a22 devono esistere (li ha fatti ia01). Con SOLO_CONTROLLI si fanno quelli di prova (catene di Markov)."""
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI_V21 if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01: eseguire prima ia01)' % (', '.join(mancano), G.LIBRI))


def main():
    import torch
    import numpy
    import scipy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'rete,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d, segni %d, vocabolario %d; pieghe %s; semi %s; libri %s' % (
        len(c['ids']), sum(len(a) for a in c['ids'].values()), c['V'], NF, SEMI, LIBRI_V21), flush=True)
    prepara_libri()
    if fasi == ['mi']:
        pag = sorted(c['ids'])
        W, split = pesi_bootstrap(len(pag)), divisioni_nulle(len(pag))
        libri = OrderedDict([('vere', c['vere'])] + [(b, G.libro(b)) for b in LIBRI_V21])
        mi = analisi_mi(pag, libri, c['vere'], W, split)
        lat = controllo_mi_latino()
        print(json.dumps(pulisci(OrderedDict(mi=mi, latino=lat)), indent=1, default=float))
        return
    percorso = os.path.join(USCITA, 'ia08_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = carica_corse(percorso)
    elif 'rete' in fasi:
        open(percorso, 'w').close()
    if 'rete' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        da_fare = [j for j in lavori_rete() if json.dumps(list(j)) not in fatte]
        print('addestramento: %d da fare, %d gia fatti' % (len(da_fare), len(lavori_rete()) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 10))
        with get_context('spawn').Pool(processi, initializer=G.avvia_processo) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                corse.append(r)
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s) passi %d' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo'], r['info']['passi']), flush=True)
    elif os.path.exists(percorso):
        corse = carica_corse(percorso)
    if 'analisi' in fasi:
        modelli = [dict(x['info'], job=x['job']) for x in corse]
        righe, ris = esegui_analisi(corse, versioni, modelli)
        print('\n'.join(righe[:14]), flush=True)


if __name__ == '__main__':
    main()
