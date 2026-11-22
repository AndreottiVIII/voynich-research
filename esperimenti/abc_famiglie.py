# -*- coding: utf-8 -*-
"""Famiglie di procedimenti "da scriba" per ia28 (modulo di supporto, non e' un esperimento).

Tre famiglie, ognuna con pochi parametri, che l'inferenza per simulazione (ABC, `abc_inferenza.py`) stima sul testo. Ogni famiglia
e' una funzione `genera(famiglia, theta, layout, seme)` che scrive un testo nell'impaginazione data (solo lunghezze: righe per
pagina, parole per riga, inizio di paragrafo) e restituisce le pagine nel formato di ia01: pagina -> [(inizio_paragrafo, [parola])],
con la parola come tupla di glifi.

  CV  copia e varia (autocitazione alla Timm e Schinner, generalizzata, scritta qui da zero in Python). Ogni parola e' nuova
      (probabilita' nu) oppure e' la copia, ritoccata, di una parola gia' scritta: da quale riga (scala tau, in righe), se dalla
      stessa posizione della riga sopra (b_pos), se da un punto qualunque del testo gia' scritto (p_lontano), con che probabilita' e
      di che tipo e' il ritocco (p_mod, q_sost, p_sim) e quanto pesa il contatto con la parola prima (w_contatto: la copia si
      sceglie fra le parole della riga con un peso che dipende da ultimo glifo della parola prima e primo glifo della candidata).
  NB  Naibbe vero piu' eco di pagina. Il generatore del repo (`analisi/generatori.naibbe`, con le tavole di Greshko
      `naibbe_tables.csv`, il mazzo di 52 carte e la quota di pezzi di una lettera 17/36 cosi' come sono) cifra il latino di
      Plinio; i suoi unici parametri esposti sono la deriva di pagina (conc: concentrazione, piu' bassa = pagine piu' "di
      parte"); in piu' l'eco: p_eco = quota di posti con una parola d'eco (parola NULLA: non porta lettere), q_tema = quota
      d'eco ripresa dal tema della pagina (le altre sono varianti di una parola della riga corrente o della sopra).
  VT  verboso, eco e bordi di ia19 a parametri liberi: cifrario verboso omofonico a bigrammi con T tavole, A segni, tavole
      speciali per la prima e l'ultima parola di riga con probabilita' b, piu' l'eco (p_eco, q_tema) come in NB.

REGOLA (come ia14 e ia19): questo modulo non legge il Voynich e non importa i suoi caricatori. Del Voynich usa solo le cose
generiche gia' usate da ia14/ia19: i nomi dei 20 segni (non le frequenze: per ogni istanza si tirano a caso), la lunghezza
media di una parola (circa 5 segni) e l'impaginazione (solo lunghezze, passata dal chiamante). Le tavole di Naibbe sono dati
dell'autore del cifrario, non del Voynich. Le distribuzioni a priori dei parametri (PRIORI) sono fissate nella preregistrazione.
"""
import math
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import cifrari_procedimenti as CP  # noqa: E402
import combinati_procedimenti as CB  # noqa: E402
import generatori as GEN  # noqa: E402
import misure as MIS  # noqa: E402

FAMIGLIE = ('CV', 'NB', 'VT')
NOMI_FAMIGLIE = OrderedDict([
    ('CV', 'copia e varia (autocitazione generalizzata)'),
    ('NB', 'Naibbe vero piu\' eco di pagina'),
    ('VT', 'verboso piu\' eco piu\' bordi, parametri liberi')])

# Distribuzioni a priori (fissate nella preregistrazione, prima di qualunque simulazione sul testo):
#   'u' uniforme in [lo, hi]; 'lu' logaritmica uniforme; 'i' intero uniforme in [lo, hi].
PRIORI = OrderedDict([
    ('CV', OrderedDict([('nu', ('u', 0.02, 0.30)), ('tau', ('lu', 0.3, 8.0)), ('p_lontano', ('u', 0.0, 0.30)),
                        ('b_pos', ('u', 0.0, 8.0)), ('p_mod', ('u', 0.2, 1.0)), ('q_sost', ('u', 0.0, 1.0)),
                        ('p_sim', ('u', 0.0, 1.0)), ('w_contatto', ('u', 0.0, 3.0))])),
    ('NB', OrderedDict([('conc', ('lu', 0.3, 30.0)), ('p_eco', ('u', 0.0, 0.50)), ('q_tema', ('u', 0.0, 1.0))])),
    ('VT', OrderedDict([('T', ('i', 2, 6)), ('A', ('i', 8, 20)), ('b', ('u', 0.0, 1.0)), ('p_eco', ('u', 0.0, 0.50)),
                        ('q_tema', ('u', 0.0, 1.0))])),
])

K_TEMA = 10                    # parole del tema di pagina (come ia19)
FINESTRA_RIGHE = 12            # CV: al massimo tante righe sopra come sorgente della copia
LUNGHEZZE_NUOVE = ((2, 0.15), (3, 0.25), (4, 0.25), (5, 0.20), (6, 0.10), (7, 0.05))
LUNGH_CLASSE = 3               # CV: i 20 segni si dividono a caso in gruppi di 3 "simili" (per le sostituzioni vicine)
NAIBBE_CSV = os.path.join(QUI, '..', 'dati', 'cache', 'sorgenti', 'naibbe-cipher', 'references', 'naibbe_tables.csv')
NAIBBE_CSV = os.environ.get('NAIBBE_CSV28', NAIBBE_CSV)

_C = {}


class RndLimitato(random.Random):
    """Un `random.Random` (stesse sequenze) che dopo `limite` estrazioni solleva un errore: protegge da cicli senza fine (con una sola tavola
    del verboso certe coppie di lettere possono avere una sola forma, uguale a quella di una lettera sola, e il ciclo di rifiuto di ia19 non
    finisce; per questo T parte da 2). Il testo che solleva l'errore si riprova con un altro seme."""

    def __init__(self, seme, limite=20000000):
        super().__init__(seme)
        self.limite = limite
        self.n = 0

    def random(self):
        self.n += 1
        if self.n > self.limite:
            raise RuntimeError('troppe estrazioni: ciclo senza fine?')
        return super().random()

    def getrandbits(self, k):
        self.n += 1
        if self.n > self.limite:
            raise RuntimeError('troppe estrazioni: ciclo senza fine?')
        return super().getrandbits(k)


def seme28(*parti):
    return zlib.crc32('|'.join(str(p) for p in ('ia28',) + parti).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- parametri: priori, scala unitaria

def campiona(fam, rnd):
    """Un vettore di parametri dalla distribuzione a priori della famiglia (dizionario nome -> valore)."""
    th = OrderedDict()
    for k, (tipo, lo, hi) in PRIORI[fam].items():
        if tipo == 'u':
            th[k] = lo + (hi - lo) * rnd.random()
        elif tipo == 'lu':
            th[k] = math.exp(math.log(lo) + (math.log(hi) - math.log(lo)) * rnd.random())
        else:
            th[k] = rnd.randint(lo, hi)
    return th


def a_unita(fam, th):
    """Parametri riportati a [0, 1] (la scala della distribuzione a priori; i 'lu' in scala logaritmica)."""
    v = []
    for k, (tipo, lo, hi) in PRIORI[fam].items():
        x = th[k]
        if tipo == 'lu':
            v.append((math.log(x) - math.log(lo)) / (math.log(hi) - math.log(lo)))
        else:
            v.append((x - lo) / float(hi - lo))
    return v


def da_unita(fam, v):
    """Inverso di `a_unita` (con i valori riportati dentro l'intervallo dell'a priori; gli interi si arrotondano)."""
    th = OrderedDict()
    for (k, (tipo, lo, hi)), x in zip(PRIORI[fam].items(), v):
        x = min(1.0, max(0.0, float(x)))
        if tipo == 'lu':
            th[k] = math.exp(math.log(lo) + (math.log(hi) - math.log(lo)) * x)
        elif tipo == 'i':
            th[k] = int(round(lo + (hi - lo) * x))
        else:
            th[k] = lo + (hi - lo) * x
    return th


def nomi_parametri(fam):
    return list(PRIORI[fam])


# ---------------------------------------------------------------- impaginazione (solo lunghezze)

def layout_di(pagine):
    """[(nome pagina, [(inizio_paragrafo, numero di parole), ...]), ...] da pagine gia' scritte: solo le lunghezze."""
    return CP.layout_da_pagine(pagine)


def quarti(layout, n=4):
    """Divide l'impaginazione in n parti con le pagine a giro (pagina i -> parte i % n): ogni parte ha pagine di tutte le zone."""
    return [[p for i, p in enumerate(layout) if i % n == q] for q in range(n)]


def quarti_pagine(pagine, n=4):
    nomi = list(pagine)
    return [OrderedDict((p, pagine[p]) for i, p in enumerate(nomi) if i % n == q) for q in range(n)]


def parole_totali(layout):
    return sum(sum(k for _, k in rows) for _, rows in layout)


# ---------------------------------------------------------------- CV: copia e varia

def modifica_cv(rnd, sg, w, th, classe_di):
    """Una o due modifiche alla parola w (tupla di glifi): sostituzione con probabilita' q_sost (con p_sim da un glifo 'simile', cioe'
    dello stesso gruppo), altrimenti inserzione o cancellazione (a meta' ciascuna)."""
    n = 0
    if rnd.random() < th['p_mod']:
        n = 1
        if rnd.random() < 0.5 * th['p_mod']:
            n = 2
    w = list(w)
    for _ in range(n):
        if rnd.random() < th['q_sost'] or len(w) == 1:
            i = rnd.randrange(len(w))
            gruppo = [g for g in classe_di[w[i]] if g != w[i]] if w[i] in classe_di else []
            if gruppo and rnd.random() < th['p_sim']:
                w[i] = rnd.choice(gruppo)
            else:
                w[i] = sg.uno()
        elif rnd.random() < 0.5:
            if len(w) < 12:
                w.insert(rnd.randrange(len(w) + 1), sg.uno())
        elif len(w) > 1:
            del w[rnd.randrange(len(w))]
    return tuple(w)


def genera_cv(th, layout, rnd):
    sg = CP.Segni(rnd)
    ordine = list(CP.ALFABETO)
    rnd.shuffle(ordine)
    classe_di = {}
    for i in range(0, len(ordine), LUNGH_CLASSE):
        gr = ordine[i:i + LUNGH_CLASSE]
        for g in gr:
            classe_di[g] = gr
    w_c = th['w_contatto']
    if w_c > 0:
        aff = {(a, b): math.exp(w_c * rnd.gauss(0.0, 1.0)) for a in CP.ALFABETO for b in CP.ALFABETO}
    ls, ps = zip(*LUNGHEZZE_NUOVE)
    peso_riga = [math.exp(-d / th['tau']) for d in [0.5] + list(range(1, FINESTRA_RIGHE + 1))]
    out = OrderedDict()
    tutte = []
    for pag, rows in layout:
        righe, pagina = [], []
        for ini, n in rows:
            cur = []
            for j in range(n):
                if not righe and not cur:
                    nuova = True
                else:
                    nuova = rnd.random() < th['nu']
                if nuova:
                    w = sg.stringa(rnd.choices(ls, weights=ps, k=1)[0])
                elif tutte and rnd.random() < th['p_lontano']:
                    w = modifica_cv(rnd, sg, rnd.choice(tutte), th, classe_di)
                else:
                    # riga sorgente: la riga in corso (parole gia' scritte) con scala 0,5, poi le righe sopra a distanza 1, 2, ...
                    cand, pesi = [], []
                    if cur:
                        cand.append(cur)
                        pesi.append(peso_riga[0])
                    for d in range(1, min(FINESTRA_RIGHE, len(righe)) + 1):
                        cand.append(righe[-d])
                        pesi.append(peso_riga[d])
                    riga = rnd.choices(cand, weights=pesi, k=1)[0]
                    pw = []
                    prima = cur[-1] if cur else None
                    for i, x in enumerate(riga):
                        p = 1.0 + (th['b_pos'] if i == j else 0.0)
                        if w_c > 0 and prima is not None:
                            p *= aff[(prima[-1], x[0])]
                        pw.append(p)
                    src = rnd.choices(riga, weights=pw, k=1)[0]
                    w = modifica_cv(rnd, sg, src, th, classe_di)
                cur.append(w)
                tutte.append(w)
            righe.append(cur)
            pagina.append((bool(ini), cur))
        out[pag] = pagina
    return out


# ---------------------------------------------------------------- eco (per NB e VT)

def tessi_eco(rnd_eco, base, layout, flags, q_tema, k_tema=K_TEMA):
    """Mette le parole di base e quelle d'eco nell'impaginazione (come `combinati_procedimenti.tessi_eco`, ma con q_tema libero). Una
    posizione con flags e' una parola NULLA: con probabilita' q_tema e' ripresa dal tema della pagina (k_tema parole distinte scelte a caso
    fra le parole di base di quella pagina), altrimenti e' una variante a una modifica di una parola della riga in corso o della sopra
    (modifica come in ia14: uguale 20%, un segno cambiato 40%, uno in piu' 20%, uno in meno 20%). Restituisce (pagine, tipi)."""
    sgt = CB.SegniDaTesto(rnd_eco, base)
    out, tipi = OrderedDict(), []
    pos = ib = 0
    for p, rows in layout:
        npos = sum(n for _, n in rows)
        fl = flags[pos:pos + npos]
        nb = npos - sum(fl)
        pagina_base = base[ib:ib + nb]
        distinte = sorted(set(pagina_base))
        tema = rnd_eco.sample(distinte, min(k_tema, len(distinte))) if distinte else []
        prev, nr, j, kb = [], [], 0, 0
        for ini, n in rows:
            cur = []
            for _ in range(n):
                if fl[j]:
                    cand = prev + cur
                    if tema and (rnd_eco.random() < q_tema or not cand):
                        w, t = rnd_eco.choice(tema), 't'
                    elif cand:
                        w, t = CP.modifica(sgt, rnd_eco.choice(cand)), 'l'
                    else:
                        w, t = sgt.stringa(4), 'l'
                else:
                    w, t = pagina_base[kb], 'b'
                    kb += 1
                cur.append(w)
                tipi.append(t)
                j += 1
            nr.append((bool(ini), cur))
            prev = cur
        out[p] = nr
        pos += npos
        ib += nb
    return out, tipi


def flag_eco(rnd_eco, N, p):
    return [rnd_eco.random() < p for _ in range(N)] if p > 0 else [False] * N


# ---------------------------------------------------------------- NB: Naibbe vero + eco

def _naibbe_dati():
    if 'nb' not in _C:
        glifi = GEN.naibbe_tabelle(NAIBBE_CSV)
        lettere_ok = {c.split('_')[-1] for c in glifi if c.startswith('unigram_alpha_')}
        dividi = MIS.divisore(MIS.GLIFI_EVA)
        chiave = CP.CHIAVI_CHIARO['latino']
        parole = CP._testo(chiave).split()
        # il testo in chiaro e' pulito come fa Naibbe e tenuto alle lettere che le sue tavole conoscono
        testo = ''.join(c for c in ''.join(GEN.naibbe_pulisci(p) for p in parole) if c in lettere_ok)
        _C['nb'] = dict(glifi=glifi, dividi=dividi, testo=testo)
    return _C['nb']


def genera_nb(th, layout, rnd, rnd_eco):
    d = _naibbe_dati()
    N = parole_totali(layout)
    flags = flag_eco(rnd_eco, N, th['p_eco'])
    n_base = N - sum(flags)
    t = d['testo']
    necessarie = int(1.65 * n_base) + 60
    inizio = rnd.randrange(0, max(1, len(t) - necessarie))
    lettere = t[inizio:inizio + necessarie]
    pagine_n = max(1, len(layout))
    parole_pagina = max(5, int(round(n_base / pagine_n)))
    cifrato, _ = GEN.naibbe(lettere, d['glifi'], rnd, parole_pagina, th['conc'])
    if len(cifrato) < n_base:
        raise ValueError('testo in chiaro troppo corto per Naibbe: %d parole su %d' % (len(cifrato), n_base))
    base = [tuple(d['dividi'](w)) for w in cifrato[:n_base]]
    return tessi_eco(rnd_eco, base, layout, flags, th['q_tema'])


# ---------------------------------------------------------------- VT: verboso + eco + bordi

def genera_vt(th, layout, rnd, rnd_eco):
    N = parole_totali(layout)
    flags = flag_eco(rnd_eco, N, th['p_eco'])
    n_base = N - sum(flags)
    cfg = dict(T=int(th['T']), A=int(th['A']), b=float(th['b']), n=0, p=0.0)
    att = CB.attributi_posizione(layout)
    attrs = [a for a, f in zip(att, flags) if not f]
    pc = CP.parole_chiaro('latino')
    inizio = rnd.randrange(0, max(1, len(pc) - 3 * N // 2))
    lettere, _ = CP.lettere_da(pc, inizio, int(1.62 * n_base) + 50)
    base, info = CB.genera_base(rnd, n_base, attrs, cfg, lettere=lettere)
    pagine, tipi = tessi_eco(rnd_eco, base, layout, flags, th['q_tema'])
    return pagine, tipi


# ---------------------------------------------------------------- interfaccia

def genera(fam, th, layout, seme):
    """Un testo della famiglia `fam` con i parametri `th` nell'impaginazione `layout`, deterministico dal `seme`.
    Restituisce (pagine, meta); meta e' fatto solo di numeri."""
    rnd = RndLimitato(seme28('gen', fam, seme))
    rnd_eco = RndLimitato(seme28('eco', fam, seme))
    meta = dict(famiglia=fam, seme=seme)
    if fam == 'CV':
        pagine = genera_cv(th, layout, rnd)
    elif fam == 'NB':
        pagine, tipi = genera_nb(th, layout, rnd, rnd_eco)
        meta.update(quota_eco=1.0 - tipi.count('b') / max(len(tipi), 1))
    elif fam == 'VT':
        pagine, tipi = genera_vt(th, layout, rnd, rnd_eco)
        meta.update(quota_eco=1.0 - tipi.count('b') / max(len(tipi), 1))
    else:
        raise ValueError(fam)
    tutte = [w for rows in pagine.values() for _, ws in rows for w in ws]
    meta.update(parole=len(tutte), lunghezza_media=sum(len(w) for w in tutte) / max(len(tutte), 1), tipi_distinti=len(set(tutte)))
    return pagine, meta


def rimescola_parole(pagine, seme):
    """Controllo negativo: tutte le parole mescolate fra tutte le pagine (stessa impaginazione)."""
    return CP.rimescola_tutto(pagine, seme)


def riallinea_glifi(pagine, ranghi_riferimento):
    """Rietichetta i glifi di un testo per rango di frequenza: il glifo piu' frequente del testo prende il nome del piu' frequente del
    riferimento, e cosi' via (i glifi in piu' mantengono il nome e si saltano i nomi gia' presi). Non cambia nessuna struttura: serve solo
    perche' i giudici (che conoscono i glifi del Voynich) non separino un testo solo dal nome dei suoi segni. `ranghi_riferimento`: lista
    dei glifi del riferimento dal piu' al meno frequente."""
    c = Counter(g for rows in pagine.values() for _, ws in rows for w in ws for g in w)
    mio = [g for g, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))]
    mappa, presi = {}, set()
    for g, r in zip(mio, ranghi_riferimento):
        mappa[g] = r
        presi.add(r)
    resto = [g for g in mio if g not in mappa]
    for g in resto:
        mappa[g] = g if g not in presi else g + '′'
        presi.add(mappa[g])
    return OrderedDict((p, [(ini, [tuple(mappa[g] for g in w) for w in ws]) for ini, ws in rows]) for p, rows in pagine.items())


def prova_famiglie():
    """Prove interne, solo su impaginazioni inventate: determinismo, numero di parole, priori, inverso dei parametri, famiglie senza il
    Voynich. Restituisce un dizionario di booleani (tutto vero = superata)."""
    ris = OrderedDict()
    layout = [('P%03d' % i, [(j == 0, 7 + (i + j) % 3) for j in range(12)]) for i in range(20)]
    N = parole_totali(layout)
    rnd = random.Random(1)
    for fam in FAMIGLIE:
        th = campiona(fam, rnd)
        a, ma = genera(fam, th, layout, 3)
        b, _ = genera(fam, th, layout, 3)
        c, _ = genera(fam, th, layout, 4)
        ris[fam + ': deterministico'] = a == b
        ris[fam + ': semi diversi, testi diversi'] = a != c
        ris[fam + ': numero di parole'] = ma['parole'] == N
        ris[fam + ': pagine e righe come il layout'] = (list(a) == [p for p, _ in layout] and all(
            [len(ws) for _, ws in a[p]] == [k for _, k in rows] for p, rows in layout))
        ris[fam + ': parole non vuote'] = all(len(w) > 0 for rows in a.values() for _, ws in rows for w in ws)
        v = a_unita(fam, th)
        ris[fam + ': parametri in [0,1]'] = all(-1e-9 <= x <= 1 + 1e-9 for x in v)
        back = da_unita(fam, v)
        ris[fam + ': inverso dei parametri'] = all(abs(back[k] - th[k]) < 1e-6 * max(1.0, abs(th[k])) for k in th)
    # CV: con nu = 1 niente copia (tutte parole nuove); con p_mod = 0 e nu piccolo molte parole uguali
    th = OrderedDict(nu=0.02, tau=1.0, p_lontano=0.0, b_pos=0.0, p_mod=0.0, q_sost=0.5, p_sim=0.5, w_contatto=0.0)
    a, _ = genera('CV', th, layout, 5)
    tutte = [w for rows in a.values() for _, ws in rows for w in ws]
    ris['CV: senza ritocchi pochi tipi (copie esatte)'] = len(set(tutte)) < 0.25 * len(tutte)
    th = dict(th, nu=1.0)
    a, _ = genera('CV', th, layout, 5)
    tutte = [w for rows in a.values() for _, ws in rows for w in ws]
    ris['CV: con nu = 1 quasi tutte parole diverse'] = len(set(tutte)) > 0.8 * len(tutte)
    # NB e VT: senza eco la quota d'eco e' zero; con eco 0,3 e' vicina
    for fam, th0 in (('NB', OrderedDict(conc=5.0, p_eco=0.0, q_tema=0.5)), ('VT', OrderedDict(T=3, A=20, b=0.0, p_eco=0.0, q_tema=0.5))):
        _, m0 = genera(fam, th0, layout, 7)
        _, m1 = genera(fam, dict(th0, p_eco=0.3), layout, 7)
        ris[fam + ': senza eco quota 0'] = m0['quota_eco'] == 0.0
        ris[fam + ': quota d\'eco vicina a p_eco'] = abs(m1['quota_eco'] - 0.3) < 0.06
    # VT con p_eco = 0, T = 3, A = 20, b = 0: le stesse parole del verboso di ia14 (stesso procedimento, stesso flusso)
    th0 = OrderedDict(T=3, A=20, b=0.0, p_eco=0.0, q_tema=0.5)
    a, _ = genera('VT', th0, layout, 9)
    ris['VT: le parole stanno nelle tavole (lunghezza media sensata)'] = 2.0 < sum(len(w) for rows in a.values() for _, ws in rows for w in ws) / N < 9.0
    ris['RndLimitato: stesse sequenze di random.Random'] = [RndLimitato(5).random() for _ in range(3)] == [random.Random(5).random() for _ in range(3)]         and RndLimitato(5).randrange(1000) == random.Random(5).randrange(1000)
    try:
        r_ = RndLimitato(1, limite=10)
        for _ in range(20):
            r_.random()
        ris['RndLimitato: si ferma dopo il limite'] = False
    except RuntimeError:
        ris['RndLimitato: si ferma dopo il limite'] = True
    # il modulo non importa caricatori del Voynich
    sorgente = open(os.path.abspath(__file__), encoding='utf-8').read()
    righe_import = [l for l in sorgente.splitlines() if l.startswith(('import ', 'from '))]
    ris['niente caricatori del Voynich'] = not any(m in l for l in righe_import for m in ('trascrizione', 'pezzi', 'ia01', 'sintassi_testi', 'e3c95'))
    # riallineamento dei glifi: non cambia le lunghezze e conserva i conteggi (ordinati)
    a, _ = genera('CV', th, layout, 5)
    r = riallinea_glifi(a, ['x%d' % i for i in range(25)])
    ca = sorted(Counter(g for rows in a.values() for _, ws in rows for w in ws for g in w).values())
    cr = sorted(Counter(g for rows in r.values() for _, ws in rows for w in ws for g in w).values())
    ris['riallinea_glifi: stessi conteggi'] = ca == cr
    ris['riallinea_glifi: stesse lunghezze'] = all(len(w1) == len(w2) for (p1, r1), (p2, r2) in zip(a.items(), r.items())
                                                   for (_, x1), (_, x2) in zip(r1, r2) for w1, w2 in zip(x1, x2))
    return ris


if __name__ == '__main__':
    r = prova_famiglie()
    for k, v in r.items():
        print('%-60s %s' % (k, 'ok' if v else 'FALLITA'))
    sys.exit(0 if all(r.values()) else 1)
