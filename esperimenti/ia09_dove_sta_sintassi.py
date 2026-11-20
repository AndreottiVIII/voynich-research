# -*- coding: utf-8 -*-
"""Esperimento IA9 (ia09): dove sta l'informazione che rende prevedibile la parola successiva, e se e' "grammatica"
(classi di parole in sequenza) o "auto-citazione" (somiglianza con parole scritte poco prima sulla stessa pagina).

Segue ia08 (perche' la rete se ne accorge): li' si e' visto che il Voynich ha una "sintassi" fra le parole che va oltre il
contatto fra glifi. Qui si prova a smontarla in pezzi interpretabili. Preregistrazione: preregistrazioni/ia09.md.

Che cosa fa il codice (in parole semplici)
- Per ogni testo (Voynich, libri v21, Timm e Schinner, due generatori sintetici costruiti apposta, latino, inglese e i controlli
  rimescolati) e per ogni piega di pagine, si addestrano sulle pagine di addestramento dello STESSO testo dei modelli che vedono
  solo un pezzo del contesto ("bende"), e si misura quanti bit costa ogni parola delle pagine di prova (la parola intera e il
  solo primo glifo). Il guadagno di una benda = bit risparmiati rispetto al modello che non vede nessun contesto.
  Modelli: base (a); parola prima (b); ultimo glifo della prima (c); primo glifo della prima (d); parola di due posti prima (e)
  e sua forma (e2); ultimo+primo glifo della prima (cd); classe della parola prima (i1) e delle due prima (i2); posto nella
  riga e nella pagina (f); la copia (g): somiglianza con le parole scritte prima sulla stessa pagina, per distanza (bande),
  uguali o a una modifica; il riferimento della copia con le parole di una pagina a caso; miscele "grammatica", "copia" e "tutto".
- Una rete GRU a caratteri (come ia01), addestrata dentro lo stesso testo: contesto completo, e quanto perde se si rompe l'ordine.
- Letture: quota di copia (rho), grammatica dove non c'e' una parola simile vicina, quota locale della copia, v21 contro vere.

Uscite (solo numeri e aggregati, nessuna parola ne' riga di testo): risultati/ia09_dove_sta_sintassi.json e .md e, una riga per
lavoro, risultati/ia09_corse.jsonl (con RIPRENDI=1 i lavori fatti non si rifanno).

Variabili (oltre a quelle di ia01: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, CHIAVI, SEMI, PASSI, OGNI, PAZIENZA, NASCOSTO, CADUTA,
USCITA, LIBRI): PROCESSI, RIPRENDI, FASI (conteggi, rete, analisi; predefinito tutte e tre), FILTRO (sottostringhe, separate da |,
che il nome del lavoro deve contenere), NULLI (200), BOOT (1000), GENERATORI (istanze di ogni generatore sintetico, 3), RIM_TESTO
(rimescolamenti di tutto il testo delle vere, 5), SCALA_COPIA (10), RIGHE_PAGINA_EN (righe per pagina dell'inglese, 14).
"""
import json, math, os, random, sys, time, zlib
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import sintassi_testi as TT  # noqa: E402
import sintassi_modelli as SM  # noqa: E402

NOME = 'ia09_dove_sta_sintassi'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF, SEMI, CHIAVI = G.NF, G.SEMI, G.CHIAVI
NULLI = int(os.environ.get('NULLI', 200))
BOOT = int(os.environ.get('BOOT', 1000))
GENERATORI = int(os.environ.get('GENERATORI', 3))
RIM_TESTO = int(os.environ.get('RIM_TESTO', 5))
SCALA_COPIA = float(os.environ.get('SCALA_COPIA', 10))
FORZA = dict(F=1.0, M=0.5, D=0.3)       # generatori "a sola grammatica" piantati: peso della catena a ciclo (naturale = N, dal testo)
P_COPIA = dict(F=0.5, M=0.04, D=0.01)     # generatori "a sola copia": probabilita' di copiare una parola scritta prima
LIBRI_V21 = ['a%d' % k for k in CHIAVI]

LISTA13 = ['U'] + SM.BENDE + ['gram', 'g', 'tutto']      # modelli di cui si salvano anche "tutte le parole" e "parole rimescolate"
FLAG4 = ['U', 'gram', 'g', 'tutto']                      # modelli di cui si salva la divisione "parola simile vicina si' / no"


def comp(pre, bande, quali='xm'):
    out = []
    for b in bande:
        if 'x' in quali:
            out.append('%sx_%s' % (pre, b))
        if 'm' in quali:
            out.append('%sm_%s' % (pre, b))
    return out


def specifiche():
    """Le miscele: nome -> colonne (oltre alla base U). g = copia dalla pagina stessa; n = riferimento (pagina a caso)."""
    sp = OrderedDict()
    for pre, nome in (('', 'g'), ('n', 'n')):
        sp[nome] = comp(pre, SM.BANDE)
        for b in SM.BANDE:
            sp['%s_%s' % (nome, b)] = comp(pre, [b])
        sp['%s_vic' % nome] = comp(pre, SM.VICINE)
        sp['%s_lont' % nome] = comp(pre, SM.LONTANE)
        sp['%s_x' % nome] = comp(pre, SM.BANDE, 'x')
        sp['%s_m' % nome] = comp(pre, SM.BANDE, 'm')
    sp['gram'] = list(SM.GRAM)
    sp['tutto'] = list(SM.GRAM) + sp['g']
    sp['gram_n'] = list(SM.GRAM) + sp['n']
    return sp


SPEC = specifiche()
MODELLI = ['U'] + SM.BENDE + list(SPEC)


def seme_di(nome):
    return G.seme_di(nome)


# ---------------------------------------------------------------- i testi

_T = OrderedDict()


def nomi_testi():
    """Tutti i testi dell'esperimento. 'X~t1' = X con tutte le parole mescolate fra le pagine; 'X~p' = X con le parole mescolate
    dentro ogni pagina."""
    base = ['vere'] + LIBRI_V21
    if not SOLO_CONTROLLI:
        base += ['ts1', 'ts2']
    gen = (['gramN1', 'gramF', 'gramD', 'copiaF', 'copiaD'] + ['gramM%d' % i for i in range(1, GENERATORI + 1)] +
           ['copiaM%d' % i for i in range(1, GENERATORI + 1)])
    rif = (['latino'] if not SOLO_CONTROLLI else []) + ['inglese', 'italiano']
    nomi = base + gen + rif
    rim_t = ['vere~t%d' % i for i in range(1, RIM_TESTO + 1)] + [x + '~t' for x in (LIBRI_V21[:1] + (['ts1'] if not SOLO_CONTROLLI else []) + ['gramM1', 'copiaM1'] + rif)]
    rim_p = [x + '~p' for x in (['vere'] + LIBRI_V21 + (['ts1'] if not SOLO_CONTROLLI else []) + ['gramM1', 'copiaM1'] + rif)]
    return nomi + rim_t + rim_p


def costruisci(nome):
    """Il testo `nome`: dict(pagine, fold, tipo). Uguale in ogni processo (semi fissi)."""
    if nome in _T:
        return _T[nome]
    if '~' in nome:
        base, modo = nome.split('~')
        T = costruisci(base)
        f = TT.rimescola_testo if modo.startswith('t') else TT.rimescola_pagina
        t = dict(pagine=f(T['pagine'], seme_di('ia09:rim:' + nome)), fold=T['fold'], tipo=T['tipo'])
    elif nome == 'vere':
        t = TT.testo_vere()
    elif nome in LIBRI_V21:
        t = TT.testo_libro(nome)
    elif nome.startswith('ts'):
        t = TT.testo_ts(int(nome[2:]))
    elif nome == 'latino':
        t = TT.testo_latino()
    elif nome == 'inglese':
        t = TT.testo_inglese()
    elif nome == 'italiano':
        t = TT.testo_italiano()
    elif nome.startswith('gram') or nome.startswith('copia'):
        base = costruisci('vere')
        Cb = SM.Corpus(base['pagine'])
        Cb.prepara()
        seme = seme_di('ia09:gen:' + nome)
        livello = nome[4] if nome.startswith('gram') else nome[5]
        meta = {}
        if nome.startswith('gram'):
            pagine, meta = SM.genera_grammatica(Cb, seme, None if livello == 'N' else FORZA[livello])
        else:
            pagine = SM.genera_copia(Cb, seme, P_COPIA[livello], SCALA_COPIA)
        t = dict(pagine=pagine, fold=base['fold'], tipo=None, meta=meta)
    else:
        raise ValueError(nome)
    if len(_T) > 4:
        _T.clear()
    _T[nome] = t
    return t


# ---------------------------------------------------------------- lavoro dei conteggi (un testo, tutte le pieghe)

def prob_colonne(gr, beta, cc, tg):
    """Tutte le colonne di probabilita' di una pagina (base, bende, copia, copia di riferimento)."""
    col = SM.prob_bende(gr[tg], beta)
    U = gr[tg]['U']
    col.update(SM.comp_cache(cc, tg, U, 'r'))
    col.update(SM.comp_cache(cc, tg, U, 'n'))
    return col


def bit_modello(col, nome, pesi):
    if nome in col:
        return -np.log2(col[nome])
    cols = ['U'] + SPEC[nome]
    return -np.log2(sum(w * col[c] for w, c in zip(pesi[nome], cols)))


def lavoro_C(nome):
    inizio = time.time()
    T = costruisci(nome)
    nomi = sorted(T['pagine'])
    fold = T['fold']
    C = SM.Corpus(T['pagine'])
    C.aggiungi('riga', G.rimescola_parole(T['pagine'], seme_di('ia09:riga:' + nome)))
    C.prepara()
    perm = SM.derangement(nomi, seme_di('ia09:altra:' + nome))
    cc = {}
    for var in ('reale', 'riga'):
        pv = C.varianti[var]
        fin = {p: SM.Finestre(C, pv[p]) for p in nomi}
        cc[var] = {p: SM.cache_pagina(C, pv[p], fin[p], fin[perm[p]]) for p in nomi}
    out = {}
    info = OrderedDict(pieghe=[])
    for piega in range(NF):
        test = [p for p in nomi if fold[p] == piega]
        resto = [p for p in nomi if fold[p] != piega]
        random.Random(3964 + 100 + piega).shuffle(resto)
        nval = max(1, round(0.10 * len(resto)))
        val, add = resto[:nval], resto[nval:]
        M = SM.Modello(C, add, seme=piega + 1)
        gr_v = [M.grezze(C.pag[p]) for p in val]
        mask_v = [C.pag[p].J >= 2 for p in val]
        gr_t = {var: [M.grezze(C.varianti[var][p]) for p in test] for var in ('reale', 'riga')}
        inf_p = OrderedDict(classi=M.K, tipi_visti=int((M.cw > 0).sum()))
        nbv = np.concatenate([cc['reale'][p]['r']['nb'][m] for p, m in zip(val, mask_v)])
        inf_p['nb_medio'] = [round(float(x), 2) for x in nbv.mean(0)]
        for tg in ('w', 'f'):
            beta = SM.scegli_beta([g[tg] for g in gr_v], mask_v)
            col_v = [prob_colonne(g, beta, cc['reale'][p], tg) for g, p in zip(gr_v, val)]
            pesi = {}
            for nm, cols in SPEC.items():
                cs = ['U'] + cols
                Mv = np.column_stack([np.concatenate([c[k][m] for c, m in zip(col_v, mask_v)]) for k in cs])
                pesi[nm] = np.maximum(SM.em(Mv), 1e-12)
            inf_p['beta_' + tg] = beta
            inf_p['pesi_g_' + tg] = [round(float(x), 4) for x in pesi['g']]
            inf_p['pesi_tutto_' + tg] = [round(float(x), 4) for x in pesi['tutto']]
            for var, pagine_t in (('reale', test), ('riga', test)):
                for i, p in enumerate(pagine_t):
                    P = C.varianti[var][p]
                    col = prob_colonne(gr_t[var][i], beta, cc[var][p], tg)
                    bits = {m: bit_modello(col, m, pesi) for m in (MODELLI if var == 'reale' else LISTA13)}
                    r = out.setdefault(p, dict(n=None, w={}, f={}, fl=None))
                    mp, ma = P.J >= 2, np.ones(P.n, dtype=bool)
                    if var == 'reale':
                        r['n'] = [int(mp.sum()), int(ma.sum())]
                        for m in MODELLI:
                            r[tg][m] = [round(float(bits[m][mp].sum()), 2)]
                        for m in LISTA13:
                            r[tg][m].append(round(float(bits[m][ma].sum()), 2))
                        simile = cc['reale'][p]['simile']
                        s1, s0 = mp & simile, mp & ~simile
                        r['fl'] = dict(n=[int(s0.sum()), int(s1.sum())]) if r['fl'] is None else r['fl']
                        r['fl'][tg] = {m: [round(float(bits[m][s0].sum()), 2), round(float(bits[m][s1].sum()), 2)] for m in FLAG4}
                    else:
                        for m in LISTA13:
                            r[tg][m].append(round(float(bits[m][ma].sum()), 2))
        info['pieghe'].append(inf_p)
    info['meta'] = T.get('meta') or {}
    if T.get('tipo'):
        info['lingua'] = {p: str(T['tipo'][p][1]) for p in nomi}
    return dict(job=['C', nome], tipo='C', info=info, stat=out, tempo=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- lavoro di rete (un testo, un seme, una piega)

def posizioni_parole(rows):
    """Per ogni parola di una pagina messa in segni (come G.codifica): (inizio, lunghezza, posto nella riga)."""
    pos, out = 0, []
    for ini, ws in rows:
        if ini:
            pos += 1
        for j, w in enumerate(ws):
            if j:
                pos += 1
            out.append((pos, len(w), j))
            pos += len(w)
        pos += 1
    return out


def lavoro_N(nome, seme, piega):
    """Il modello del testo di ia01 (GRU a caratteri), addestrato dentro lo stesso testo (pagine delle altre pieghe), poi i bit di
    ogni parola (intera e primo glifo) delle pagine di prova, nell'ordine vero e con le parole rimescolate nella riga."""
    inizio = time.time()
    T = costruisci(nome)
    nomi = sorted(T['pagine'])
    C = SM.Corpus(T['pagine'])
    idx = {g: i + 4 for i, g in enumerate(C.glifi[:-1])}
    V = 4 + len(C.glifi) - 1
    riga = G.rimescola_parole(T['pagine'], seme_di('ia09:riga:' + nome))
    ids = {p: G.codifica(T['pagine'][p], idx) for p in nomi}
    test = [p for p in nomi if T['fold'][p] == piega]
    resto = [p for p in nomi if T['fold'][p] != piega]
    random.Random(3964 + 100 * seme + piega).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([ids[p] for p in ps])
    m, info = G.addestra_lm(flusso(add), flusso(val), V, 1000 * seme + piega)
    out = OrderedDict()
    sv = G.sorprese(m, [ids[p] for p in test])
    ids_r = [G.codifica(riga[p], idx) for p in test]
    sr = G.sorprese(m, ids_r)
    for p, s, s2 in zip(test, sv, sr):
        r = []
        for rows, x in ((T['pagine'][p], s), (riga[p], s2)):
            ps = posizioni_parole(rows)
            bw = np.array([x[a:a + l + 1].sum() for a, l, _ in ps])
            bf = np.array([x[a] for a, l, _ in ps])
            J = np.array([j for _, _, j in ps])
            mp = J >= 2
            r.append(dict(a=[len(ps), round(float(bw.sum()), 2), round(float(bf.sum()), 2)],
                          p=[int(mp.sum()), round(float(bw[mp].sum()), 2), round(float(bf[mp].sum()), 2)]))
        out[p] = [r[0]['p'], r[0]['a'], r[1]['a']]
    info['bpc_vere_fuori'] = float(np.mean([np.mean(x) for x in sv]))
    return dict(job=['N', nome, seme, piega], tipo='N', info=info, stat=out, tempo=round(time.time() - inizio, 1))


def lavoro(job):
    if job[0] == 'C':
        return lavoro_C(job[1])
    return lavoro_N(job[1], job[2], job[3])


# ---------------------------------------------------------------- elenco dei lavori

SEMI_RETE_TESTI = ['vere'] + LIBRI_V21 + ['gramM1', 'copiaM1', 'inglese', 'vere~t1']


def lavori(fasi):
    L = []
    if 'rete' in fasi:
        testi = SEMI_RETE_TESTI + (['ts1'] if not SOLO_CONTROLLI else []) + (['latino'] if not SOLO_CONTROLLI else [])
        for nome in testi:
            for s in (SEMI if nome == 'vere' else SEMI[:1]):
                for f in range(NF):
                    L.append(('N', nome, s, f))
    if 'conteggi' in fasi:
        for nome in nomi_testi():
            L.append(('C', nome))
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


# ---------------------------------------------------------------- analisi

# soglie delle letture (fissate nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_W = 0.03          # bit per parola: guadagno piu' piccolo che si legge (parola intera)
SOGLIA_F = 0.01          # bit per primo glifo
RHO_GRAM, RHO_COPIA = 0.25, 0.75
LAMBDA_SI, LAMBDA_NO = 0.30, 0.10
CONTROLLI_PIANTATI = dict(grammatica=['gramM1', 'gramM2', 'gramM3', 'gramF'], copia=['copiaM1', 'copiaM2', 'copiaM3', 'copiaF'])
NEGATIVI = ['vere~t%d' % i for i in range(1, 6)]


class V:
    """Un numero con la sua distribuzione bootstrap (stesso ricampionamento di pagine per tutti)."""

    def __init__(self, p, b):
        self.p = float(p)
        self.b = np.asarray(b, dtype=float)

    def _o(self, o):
        return o if isinstance(o, V) else V(o, np.full_like(self.b, float(o)))

    def __add__(s, o):
        o = s._o(o)
        return V(s.p + o.p, s.b + o.b)

    def __sub__(s, o):
        o = s._o(o)
        return V(s.p - o.p, s.b - o.b)

    def pos(s):
        return V(max(s.p, 0.0), np.maximum(s.b, 0.0))

    def dividi(s, o):
        o = s._o(o)
        with np.errstate(divide='ignore', invalid='ignore'):
            p = s.p / o.p if o.p else float('nan')
            b = np.where(o.b != 0, s.b / np.where(o.b != 0, o.b, 1), np.nan)
        return V(p, b)

    @staticmethod
    def media(lista):
        return V(np.mean([x.p for x in lista]), np.mean([x.b for x in lista], axis=0))

    def ic(s):
        b = s.b[~np.isnan(s.b)]
        return [float(v) for v in np.percentile(b, [2.5, 97.5])] if len(b) > 20 else [float('nan')] * 2

    def d(s):
        return OrderedDict(punto=s.p, ic=s.ic())


_W = {}


def pesi_bootstrap(P):
    if P not in _W:
        rng = np.random.default_rng(880009 + P)
        _W[P] = np.stack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(BOOT)]).astype(float)
    return _W[P]


def stima(num, den, W, sel=None):
    if sel is not None:
        num, den, W = num[sel], den[sel], W[:, sel]
    return V(num.sum() / den.sum(), (W @ num) / (W @ den))


class Dati:
    """I numeri per pagina di un testo (lavoro 'C')."""

    def __init__(self, r):
        self.nome = r['job'][1]
        st = r['stat']
        self.pag = sorted(st)
        self.info = r['info']
        self.n = np.array([st[p]['n'] for p in self.pag], dtype=float)
        self.B = {tg: {m: np.array([st[p][tg][m] for p in self.pag], dtype=float) for m in MODELLI} for tg in ('w', 'f')}
        self.fn = np.array([st[p]['fl']['n'] for p in self.pag], dtype=float)
        self.fb = {tg: {m: np.array([st[p]['fl'][tg][m] for p in self.pag], dtype=float) for m in FLAG4} for tg in ('w', 'f')}

    def sotto(self, pag):
        """Lo stesso testo ristretto alle pagine `pag` (stesso ordine)."""
        ix = [self.pag.index(p) for p in pag]
        o = Dati.__new__(Dati)
        o.nome, o.info, o.pag = self.nome, self.info, list(pag)
        o.n = self.n[ix]
        o.B = {tg: {m: a[ix] for m, a in self.B[tg].items()} for tg in self.B}
        o.fn = self.fn[ix]
        o.fb = {tg: {m: a[ix] for m, a in self.fb[tg].items()} for tg in self.fb}
        return o

    def guad(self, tg, m, W, sel=None):
        return stima(self.B[tg]['U'][:, 0] - self.B[tg][m][:, 0], self.n[:, 0], W, sel)

    def ordine(self, tg, m, W, sel=None):
        return stima(self.B[tg][m][:, 2] - self.B[tg][m][:, 1], self.n[:, 1], W, sel)

    def g0(self, tg, W, quale=0, sel=None):
        """Guadagno della miscela 'gram' sulle parole senza (0) o con (1) una parola simile vicina."""
        return stima(self.fb[tg]['U'][:, quale] - self.fb[tg]['gram'][:, quale], self.fn[:, quale], W, sel)

    def costo_base(self, tg):
        return float(self.B[tg]['U'][:, 0].sum() / self.n[:, 0].sum())


def misure(d, W, sel=None):
    """Tutte le misure di un testo, per i due bersagli (dizionario di V)."""
    out = {}
    for tg in ('w', 'f'):
        G_ = {m: d.guad(tg, m, W, sel) for m in MODELLI}
        r = dict(G=G_)
        r['netto'] = G_['g'] - G_['n']
        r['netto_banda'] = {b: G_['g_' + b] - G_['n_' + b] for b in SM.BANDE}
        r['netto_vic'] = G_['g_vic'] - G_['n_vic']
        r['netto_lont'] = G_['g_lont'] - G_['n_lont']
        r['A_gram'] = G_['tutto'] - G_['g']
        r['A_copia'] = G_['tutto'] - G_['gram']
        r['A_cn'] = G_['tutto'] - G_['gram_n']
        r['rho'] = r['A_cn'].pos().dividi(r['A_cn'].pos() + r['A_gram'].pos())
        r['G0'] = d.g0(tg, W, 0, sel)
        r['G1'] = d.g0(tg, W, 1, sel)
        r['quota_simile'] = float(d.fn[:, 1].sum() / d.fn.sum())
        r['ordine'] = {m: d.ordine(tg, m, W, sel) for m in LISTA13[1:]}
        out[tg] = r
    return out


def soglia_di(tg):
    return SOGLIA_W if tg == 'w' else SOGLIA_F


def lettura_tipo(r, tg):
    """Quota di copia rho = A_cn / (A_cn + A_gram) (parti positive): 'grammatica' (rho <= 0,25), 'copia' (>= 0,75), 'mista'; 'nessuna
    sintassi misurabile' se nessuna delle due parti e' almeno la soglia con limite basso dell'intervallo sopra 0."""
    s = soglia_di(tg)
    ag, ac = r['A_gram'], r['A_cn']
    mg = ag.p >= s and ag.ic()[0] > 0
    mc = ac.p >= s and ac.ic()[0] > 0
    out = OrderedDict(A_gram=ag.d(), A_copia_netto=ac.d(), rho=r['rho'].d(), gram_misurabile=bool(mg), copia_misurabile=bool(mc))
    if not mg and not mc:
        out['esito'] = 'nessuna sintassi misurabile'
    else:
        rho = r['rho'].p
        out['esito'] = 'grammatica' if rho <= RHO_GRAM else 'copia' if rho >= RHO_COPIA else 'mista'
    return out


def lettura_g0(r, tg):
    """Grammatica dove non c'e' una parola simile vicina: si' se G0 >= soglia con limite basso > 0; no se il limite alto e' sotto la soglia."""
    s = soglia_di(tg)
    g0 = r['G0']
    ic = g0.ic()
    e = 'si' if (g0.p >= s and ic[0] > 0) else 'no' if ic[1] < s else 'zona grigia'
    return OrderedDict(G0=g0.d(), G1=r['G1'].d(), esito=e)


def lettura_locale(rt, rp, tg):
    """Quota locale della copia = 1 - (copia netta con le parole mescolate dentro la pagina) / (copia netta). 'locale' se >= 0,30 con
    limite basso dell'intervallo sopra 0,10, 'di pagina' se <= 0,10; vale solo se la copia netta e' almeno la soglia."""
    s = soglia_di(tg)
    gn, gp = rt['netto'], rp['netto']
    if gn.p < s or gn.ic()[0] <= 0:
        return OrderedDict(esito='non definita (copia netta sotto la soglia)', copia_netta=gn.d(), copia_netta_pagina_rimescolata=gp.d())
    lam = V(1.0, np.ones_like(gn.b)) - gp.dividi(gn)
    e = 'locale' if (lam.p >= LAMBDA_SI and lam.ic()[0] > LAMBDA_NO) else 'di pagina' if lam.p <= LAMBDA_NO else 'zona grigia'
    return OrderedDict(esito=e, quota_locale=lam.d(), copia_netta=gn.d(), copia_netta_pagina_rimescolata=gp.d())


def verifica_ia01(corse):
    """Controllo di riproduzione (non e' una soglia): il modello GRU di 'vere' (stesso seme, stessa piega) deve coincidere con quello di ia01."""
    percorso = os.path.join(USCITA, 'ia01_corse.jsonl')
    if not os.path.exists(percorso):
        return dict(disponibile=False)
    vecchie = {}
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            d = json.loads(l)
            if d.get('tipo') == 'A':
                vecchie[(d['job'][1], d['job'][2])] = d
    bpc, passi = [], []
    for r in corse:
        if r['tipo'] == 'N' and r['job'][1] == 'vere':
            v = vecchie.get((r['job'][2], r['job'][3]))
            if v:
                bpc.append(abs(v['info']['bpc_validazione'] - r['info']['bpc_validazione']))
                passi.append(abs(v['info']['passi'] - r['info']['passi']))
    if not bpc:
        return dict(disponibile=False)
    return OrderedDict(disponibile=True, modelli=len(bpc), max_diff_perdita_validazione=float(max(bpc)), max_diff_passi=int(max(passi)))


def rete_dati(corse):
    """Per testo: per pagina, media sui semi di [n, bit parola, bit primo glifo] per parole dopo le prime due (p), tutte (a), rimescolate (s)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in corse:
        if r['tipo'] != 'N':
            continue
        for p, v in r['stat'].items():
            acc[r['job'][1]][p].append(v)
    out = {}
    for nome, d in acc.items():
        pag = sorted(d)
        out[nome] = dict(pag=pag, X=np.array([np.mean(d[p], axis=0) for p in pag]), semi=len(next(iter(d.values()))))
    return out


def lettura_rete(RN, nome):
    """GRU nel testo: bit per parola (dopo le prime due della riga) e valore dell'ordine (parole rimescolate meno ordine vero)."""
    d = RN.get(nome)
    if d is None:
        return None
    X = d['X']
    out = OrderedDict()
    Wd = pesi_bootstrap(len(d['pag']))
    for k, tg in ((1, 'w'), (2, 'f')):
        out[tg] = OrderedDict(bit_per_parola=stima(X[:, 0, k], X[:, 0, 0], Wd).d(), ordine=stima(X[:, 2, k] - X[:, 1, k], X[:, 1, 0], Wd).d())
    out['pagine'] = len(d['pag'])
    return out


def nullo_meta(d, tg, modelli, seme=3980):
    """NULLI divisioni a caso delle pagine vere in due meta': 97,5% del valore assoluto della differenza dei guadagni fra le due meta'."""
    P = len(d.pag)
    num = {m: d.B[tg]['U'][:, 0] - d.B[tg][m][:, 0] for m in modelli}
    den = d.n[:, 0]
    diff = {m: [] for m in modelli}
    for s in range(NULLI):
        ordine = list(range(P))
        random.Random(seme + s).shuffle(ordine)
        a = np.zeros(P, dtype=bool)
        a[ordine[:P // 2]] = True
        for m in modelli:
            diff[m].append(num[m][a].sum() / den[a].sum() - num[m][~a].sum() / den[~a].sum())
    return {m: float(np.percentile(np.abs(diff[m]), 97.5)) for m in modelli}


def lettura_v21(D, tg):
    """v21 (media dei libri) meno vere, per ogni modello: differenza, intervallo, nullo (vere divise a caso), etichetta."""
    libri = [b for b in LIBRI_V21 if b in D]
    if 'vere' not in D or not libri:
        return None
    pag = D['vere'].pag
    for b in libri:
        pag = [p for p in pag if p in D[b].pag]
    dv = D['vere'].sotto(pag)
    Wp = pesi_bootstrap(len(pag))
    modelli = SM.BENDE + ['gram', 'g', 'n', 'tutto']
    nul = nullo_meta(dv, tg, modelli)
    out = OrderedDict()
    s = soglia_di(tg)
    for m in modelli:
        gv = dv.guad(tg, m, Wp)
        g21 = V.media([D[b].sotto(pag).guad(tg, m, Wp) for b in libri])
        diff = g21 - gv
        ic = diff.ic()
        lim = max(nul[m], s)
        e = ('meno' if (diff.p <= -lim and ic[1] < 0) else 'piu' if (diff.p >= lim and ic[0] > 0) else 'uguale' if abs(diff.p) < nul[m] else 'zona grigia')
        out[m] = OrderedDict(vere=gv.d(), v21=g21.d(), differenza=diff.d(), nullo97=nul[m], limite=lim, rapporto=(g21.p / gv.p if gv.p > 1e-9 else None), esito=e)
    out['_pagine'] = len(pag)
    return out


def pesi_copia(info):
    """Peso della copia (uguale + a una modifica) di ogni banda nella miscela 'g' trovata sulla validazione, parole medie per banda e
    densita' per parola fonte (peso / parole), media delle pieghe (bersaglio parola intera)."""
    peso, nb = np.zeros(7), np.zeros(7)
    for p in info['pieghe']:
        w = np.array(p['pesi_g_w'])
        peso += w[1::2] + w[2::2]
        nb += np.array(p['nb_medio'])
    peso /= len(info['pieghe'])
    nb /= len(info['pieghe'])
    return OrderedDict(peso_banda=[round(float(x), 4) for x in peso], parole_per_banda=[round(float(x), 2) for x in nb],
                       densita=[round(float(x), 5) if x == x else None for x in np.where(nb > 0, peso / np.maximum(nb, 1e-9), np.nan)],
                       peso_base=round(float(1 - peso.sum()), 4))


def esegui_controlli(R):
    """Controlli preregistrati; R = nome -> {tg -> letture}."""
    c = OrderedDict()

    def tipo(n, tg='w'):
        return R[n][tg]['tipo']['esito']

    def g0(n):
        return R[n]['w']['g0']['esito']
    neg = [n for n in NEGATIVI if n in R]
    mx = [max(abs(R[n]['w']['G'][m]['punto']) for m in SM.BENDE + ['g', 'gram', 'tutto']) for n in neg]
    c['negativo_rimescolato_fra_pagine'] = OrderedDict(
        testi=neg, esiti=[tipo(n) for n in neg], G0=[g0(n) for n in neg], massimo_guadagno=(max(mx) if mx else None),
        superato=bool(neg and all(tipo(n) == 'nessuna sintassi misurabile' for n in neg) and all(g0(n) != 'si' for n in neg)))
    neg2 = [n for n in ('gramM1~t', 'copiaM1~t', 'gramM1~p') if n in R]
    c['negativo_altri_rimescolati'] = OrderedDict(
        testi=neg2, esiti=[tipo(n) for n in neg2],
        nota='gramM1~t e copiaM1~t (tutto il testo mescolato) devono dare "nessuna sintassi misurabile"; gramM1~p (mescolato dentro la pagina) '
             'non deve dare grammatica ne\' mista',
        superato=bool(all(tipo(n) == 'nessuna sintassi misurabile' for n in ('gramM1~t', 'copiaM1~t') if n in R) and
                      (tipo('gramM1~p') not in ('grammatica', 'mista') if 'gramM1~p' in R else True)))
    pg = [n for n in CONTROLLI_PIANTATI['grammatica'] if n in R]
    c['positivo_grammatica'] = OrderedDict(
        testi=pg, esiti=[tipo(n) for n in pg], G0=[g0(n) for n in pg], rho=[R[n]['w']['tipo']['rho']['punto'] for n in pg],
        superato=bool(pg and all(tipo(n) == 'grammatica' and g0(n) == 'si' for n in pg)))
    pc = [n for n in CONTROLLI_PIANTATI['copia'] if n in R]
    loc = R['copiaM1']['w'].get('locale') if 'copiaM1' in R else None
    c['positivo_copia'] = OrderedDict(
        testi=pc, esiti=[tipo(n) for n in pc], G0=[g0(n) for n in pc], rho=[R[n]['w']['tipo']['rho']['punto'] for n in pc],
        locale=(loc or {}).get('esito'),
        superato=bool(pc and all(tipo(n) == 'copia' and g0(n) != 'si' for n in pc)),
        superato_locale=bool(loc and loc.get('esito') == 'locale'))
    sens = [n for n in ('gramD', 'copiaD') if n in R]
    c['sensibilita_limite'] = OrderedDict(testi=sens, esiti=[tipo(n) for n in sens],
                                          nota='descrittivo: dice se il livello piu\' debole dei generatori piantati si legge (non e\' una condizione)')
    n1 = c['negativo_rimescolato_fra_pagine']['superato']
    c['valida_tipo'] = bool(n1 and c['negativo_altri_rimescolati']['superato'] and c['positivo_grammatica']['superato'] and c['positivo_copia']['superato'])
    c['valida_g0'] = bool(n1 and c['positivo_grammatica']['superato'] and c['positivo_copia']['superato'])
    c['valida_locale'] = bool(n1 and c['positivo_copia']['superato_locale'])
    c['valida_v21'] = bool(n1)
    return c


def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((k, pulisci(v)) for k, v in x.items() if not str(k).startswith('_') and k != 'boot')
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, V):
        return pulisci(x.d())
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def media_misure(lista):
    """Media di piu' testi (i libri v21) di tutte le misure: stesso ricampionamento di pagine per tutti."""
    out = {}
    for tg in ('w', 'f'):
        ms = [m[tg] for m in lista]
        r = {}
        for k, v0 in ms[0].items():
            if isinstance(v0, V):
                r[k] = V.media([m[k] for m in ms])
            elif isinstance(v0, dict):
                r[k] = {kk: V.media([m[k][kk] for m in ms]) for kk in v0}
            else:
                r[k] = float(np.mean([m[k] for m in ms]))
        r['rho'] = r['A_cn'].pos().dividi(r['A_cn'].pos() + r['A_gram'].pos())
        out[tg] = r
    return out


def voce(mis, costo, info, pagine):
    """Il dizionario di risultati di un testo, dalle sue misure (dizionario di V)."""
    v = OrderedDict()
    for tg in ('w', 'f'):
        r = mis[tg]
        v[tg] = OrderedDict(
            costo_base=costo[tg], G=OrderedDict((m, x.d()) for m, x in r['G'].items()), netto=r['netto'].d(),
            netto_banda=OrderedDict((b, x.d()) for b, x in r['netto_banda'].items()), netto_vic=r['netto_vic'].d(), netto_lont=r['netto_lont'].d(),
            tipo=lettura_tipo(r, tg), g0=lettura_g0(r, tg), quota_simile=r['quota_simile'],
            ordine=OrderedDict((m, x.d()) for m, x in r['ordine'].items()), _r=r)
    v['copia_pesi'] = pesi_copia(info)
    v['meta'] = info.get('meta')
    v['pagine'] = pagine
    return v


def analisi(corse, versioni):
    D = OrderedDict((r['job'][1], Dati(r)) for r in corse if r['tipo'] == 'C')
    RN = rete_dati(corse)
    if not D:
        raise SystemExit('FERMO: nessun lavoro di conteggio da analizzare')
    R = OrderedDict()
    MIS = {}
    for nome, d in D.items():
        MIS[nome] = misure(d, pesi_bootstrap(len(d.pag)))
        R[nome] = voce(MIS[nome], {tg: d.costo_base(tg) for tg in ('w', 'f')}, d.info, len(d.pag))
    # il v21: media dei libri sulle pagine che hanno tutti
    libri = [b for b in LIBRI_V21 if b in D]
    if 'vere' in D and libri:
        pag = D['vere'].pag
        for b in libri:
            pag = [p for p in pag if p in D[b].pag]
        W21 = pesi_bootstrap(len(pag))
        for suff in ('', '~p'):
            if all(b + suff in D for b in libri):
                ds = [D[b + suff].sotto(pag) for b in libri]
                MIS['v21' + suff] = media_misure([misure(x, W21) for x in ds])
                R['v21' + suff] = voce(MIS['v21' + suff], {tg: float(np.mean([x.costo_base(tg) for x in ds])) for tg in ('w', 'f')},
                                       ds[0].info, len(pag))
    for nome in list(R):
        if nome + '~p' in R:
            for tg in ('w', 'f'):
                R[nome][tg]['locale'] = lettura_locale(MIS[nome][tg], MIS[nome + '~p'][tg], tg)
    ctrl = esegui_controlli(R)
    ok = dict(tipo=ctrl['valida_tipo'], g0=ctrl['valida_g0'], locale=ctrl['valida_locale'])
    NL = 'non leggibile (un controllo non e\' superato)'
    letture = OrderedDict()
    for nome in R:
        if '~' in nome:
            continue
        letture[nome] = OrderedDict((tg, OrderedDict(
            tipo=R[nome][tg]['tipo']['esito'] if ok['tipo'] else NL, g0=R[nome][tg]['g0']['esito'] if ok['g0'] else NL,
            locale=((R[nome][tg].get('locale') or {}).get('esito') if ok['locale'] else NL))) for tg in ('w', 'f'))
    v21 = OrderedDict((tg, lettura_v21(D, tg)) for tg in ('w', 'f'))
    for tg in v21:
        if v21[tg] is not None:
            v21[tg]['_valida'] = ctrl['valida_v21']
            if not ctrl['valida_v21']:
                for m, x in v21[tg].items():
                    if isinstance(x, dict):
                        x['esito'] = NL
    ab = OrderedDict()
    if 'vere' in D and D['vere'].info.get('lingua'):
        lin = D['vere'].info['lingua']
        for lg in sorted(set(lin.values())):
            sel = np.array([lin[p] == lg for p in D['vere'].pag])
            if sel.sum() < 10:
                continue
            mis = misure(D['vere'], pesi_bootstrap(len(D['vere'].pag)), sel=sel)
            ab[lg] = OrderedDict((tg, OrderedDict(
                pagine=int(sel.sum()), G=OrderedDict((m, mis[tg]['G'][m].d()) for m in SM.BENDE + ['gram', 'g', 'n', 'tutto']),
                tipo=lettura_tipo(mis[tg], tg), g0=lettura_g0(mis[tg], tg), netto=mis[tg]['netto'].d())) for tg in ('w', 'f'))
    rete = OrderedDict((n, lettura_rete(RN, n)) for n in RN)
    out = OrderedDict(esperimento='ia09', versioni=versioni, parametri=OrderedDict(
        NF=NF, SEMI=SEMI, CHIAVI=CHIAVI, NULLI=NULLI, BOOT=BOOT, GENERATORI=GENERATORI, RIM_TESTO=RIM_TESTO, SCALA_COPIA=SCALA_COPIA, FORZA=FORZA,
        P_COPIA=P_COPIA, SOLO_CONTROLLI=SOLO_CONTROLLI,
        soglie=OrderedDict(SOGLIA_W=SOGLIA_W, SOGLIA_F=SOGLIA_F, RHO_GRAM=RHO_GRAM, RHO_COPIA=RHO_COPIA, LAMBDA_SI=LAMBDA_SI, LAMBDA_NO=LAMBDA_NO)),
        controlli=ctrl, letture=letture, testi=R, v21_contro_vere=v21, voynich_A_B=ab, rete=rete, riproduzione_ia01=verifica_ia01(corse))
    pulito = pulisci(out)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulito, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    righe = scrivi_md(pulito)
    print('\n'.join(righe[:40]), flush=True)
    return pulito


def f3(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%+.3f' % x


def f2(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%.2f' % x


def vv(d):
    """Un numero con intervallo, in una cella."""
    if d is None:
        return '-'
    return '%s (%s; %s)' % (f3(d['punto']), f3(d['ic'][0]), f3(d['ic'][1]))


def scrivi_md(out):
    T, L, c = out['testi'], out['letture'], out['controlli']
    r = ['# ia09 — dove sta la sintassi', '',
         'Soglie nella preregistrazione `preregistrazioni/ia09.md`. Guadagni in bit risparmiati rispetto al modello senza contesto (per parola, o per '
         'primo glifo); intervalli al 95% col bootstrap sulle pagine; ogni testo e\' addestrato e provato dentro se stesso (pieghe per pagina).', '',
         '## Letture (parola intera)', '']
    for n, x in L.items():
        r.append('- %s: tipo **%s**; grammatica senza parola simile vicina: %s; copia %s' % (n, x['w']['tipo'], x['w']['g0'], x['w']['locale'] or 'n.d.'))
    r += ['', '## Controlli', '']
    for k, v in c.items():
        r.append('- %s: %s' % (k, json.dumps({a: b for a, b in v.items() if a != 'nota'}, ensure_ascii=False) if isinstance(v, dict) else v))
    chiave = [n for n in T if '~' not in n]
    for tg, titolo in (('w', 'parola intera'), ('f', 'primo glifo')):
        r += ['', '## Guadagni, %s' % titolo, '', '| testo | base | ' + ' | '.join(SM.BENDE) + ' | g | g-n | gram | tutto |', '|---' * (len(SM.BENDE) + 6) + '|']
        for n in chiave:
            x = T[n][tg]
            r.append('| %s | %.2f | %s | %s | %s | %s | %s |' % (
                n, x['costo_base'], ' | '.join(f3(x['G'][m]['punto']) for m in SM.BENDE), f3(x['G']['g']['punto']), f3(x['netto']['punto']),
                f3(x['G']['gram']['punto']), f3(x['G']['tutto']['punto'])))
        r += ['', '## Valore aggiunto e grammatica senza parola simile, %s' % titolo, '',
              '| testo | grammatica sopra la copia | copia netta sopra la grammatica | rho | G0 (senza parola simile vicina) | G1 (con) | quota con parola simile | tipo |',
              '|---|---|---|---|---|---|---|---|']
        for n in chiave:
            x = T[n][tg]
            r.append('| %s | %s | %s | %s | %s | %s | %.2f | %s |' % (n, vv(x['tipo']['A_gram']), vv(x['tipo']['A_copia_netto']), vv(x['tipo']['rho']),
                                                                vv(x['g0']['G0']), vv(x['g0']['G1']), x['quota_simile'], x['tipo']['esito']))
    r += ['', '## Copia per distanza (guadagno netto di ogni banda, parola intera) e densita\' per parola fonte', '',
          '| testo | ' + ' | '.join(SM.BANDE) + ' | vicine | lontane | densita\' per banda |', '|---' * (len(SM.BANDE) + 4) + '|']
    for n in chiave:
        x = T[n]['w']
        r.append('| %s | %s | %s | %s | %s |' % (n, ' | '.join(f3(x['netto_banda'][b]['punto']) for b in SM.BANDE), f3(x['netto_vic']['punto']), f3(x['netto_lont']['punto']),
                                                 ' / '.join('%.4f' % y if y is not None else '-' for y in T[n]['copia_pesi']['densita'])))
    r += ['', 'Bande: S1 parola subito prima, S2 la seconda prima, S3 le altre della riga; R1 riga sopra, R2 due-tre righe sopra, R4 quattro-sette, R8 otto o piu\'.']
    r += ['', '## Quota locale della copia (testo contro lo stesso testo con le parole mescolate dentro la pagina)', '',
          '| testo | copia netta | con le pagine rimescolate | quota locale | esito |', '|---|---|---|---|---|']
    for n in T:
        x = T[n]['w'].get('locale')
        if x:
            r.append('| %s | %s | %s | %s | %s |' % (n, vv(x['copia_netta']), vv(x['copia_netta_pagina_rimescolata']), vv(x.get('quota_locale')), x['esito']))
    for tg, titolo in (('w', 'parola intera'), ('f', 'primo glifo')):
        v = out['v21_contro_vere'].get(tg)
        if v:
            r += ['', '## v21 contro vere, %s (media dei libri meno vere, bit)' % titolo, '',
                  '| modello | vere | v21 | differenza | nullo 97,5% | rapporto | esito |', '|---|---|---|---|---|---|---|']
            for m, x in v.items():
                if isinstance(x, dict):
                    r.append('| %s | %s | %s | %s | %.3f | %s | %s |' % (m, f3(x['vere']['punto']), f3(x['v21']['punto']), vv(x['differenza']), x['nullo97'], f2(x['rapporto']), x['esito']))
    if out['voynich_A_B']:
        r += ['', '## Voynich, lingua A e lingua B (stessi modelli delle pagine vere, pagine separate per lingua)', '']
        for lg, x in out['voynich_A_B'].items():
            y = x['w']
            r.append('- %s (%d pagine): guadagni b %s, c %s, d %s, e %s, i1 %s; copia netta %s; tipo %s; G0 %s' % (
                lg, y['pagine'], f3(y['G']['b']['punto']), f3(y['G']['c']['punto']), f3(y['G']['d']['punto']), f3(y['G']['e']['punto']), f3(y['G']['i1']['punto']),
                f3(y['netto']['punto']), y['tipo']['esito'], y['g0']['esito']))
    r += ['', '## L\'ordine delle parole (bit per parola persi se le parole si rimescolano dentro la riga), parola intera', '',
          '| testo | rete GRU | ' + ' | '.join(LISTA13[1:]) + ' |', '|---' * (len(LISTA13) + 1) + '|']
    for n in chiave:
        g = (out['rete'].get(n) or {}).get('w', {}).get('ordine') if out['rete'].get(n) else None
        r.append('| %s | %s | %s |' % (n, f3(g['punto']) if g else '-', ' | '.join(f3(T[n]['w']['ordine'][m]['punto']) for m in LISTA13[1:])))
    r += ['', '## Rete GRU dentro il testo (parole dopo le prime due della riga)', '',
          '| testo | pagine | bit per parola | bit per primo glifo | ordine, parola | ordine, primo glifo |', '|---|---|---|---|---|---|']
    for n, x in out['rete'].items():
        if x:
            r.append('| %s | %d | %.2f | %.2f | %s | %s |' % (n, x['pagine'], x['w']['bit_per_parola']['punto'], x['f']['bit_per_parola']['punto'], vv(x['w']['ordine']), vv(x['f']['ordine'])))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def main():
    import torch
    import numpy
    import scipy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'conteggi,rete,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d; pieghe %d; semi %s; libri %s' % (len(c['ids']), NF, SEMI, LIBRI_V21), flush=True)
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI_V21 if not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01)' % (', '.join(mancano), G.LIBRI))
    percorso = os.path.join(USCITA, 'ia09_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = carica_corse(percorso)
    elif 'conteggi' in fasi or 'rete' in fasi:
        open(percorso, 'w').close()
    if 'conteggi' in fasi or 'rete' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        L = lavori([f for f in fasi if f in ('conteggi', 'rete')])
        da_fare = [j for j in L if json.dumps(list(j)) not in fatte]
        # prima i lavori piu' lunghi (le reti)
        da_fare.sort(key=lambda j: 0 if j[0] == 'N' else 1)
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(L) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 10))
        with get_context('spawn').Pool(processi, initializer=G.avvia_processo) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                corse.append(r)
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s)' % (i, len(da_fare), (time.time() - inizio) / 60, r['job'], r['tempo']), flush=True)
    elif os.path.exists(percorso):
        corse = carica_corse(percorso)
    if 'analisi' in fasi:
        analisi(corse, versioni)


if __name__ == '__main__':
    main()
