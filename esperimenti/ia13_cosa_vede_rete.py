# -*- coding: utf-8 -*-
"""Esperimento IA13 (ia13): che cosa vede la rete quando le parole di una riga vengono rimescolate?

Segue ia09: li' si e' visto che rimescolare le parole dentro la riga costa alla rete GRU 1,21 bit per parola nel Voynich, mentre i
modelli semplici (parola prima, primo/ultimo glifo, famiglie, eco della pagina) ne spiegano solo circa 0,16. Qui si cerca DOVE sta quella
perdita, senza decifrare niente. Preregistrazione: preregistrazioni/ia13.md.

Che cosa fa il codice (in parole semplici)
- Per ogni testo (Voynich, tre libri v21, latino, inglese, testi sintetici con regole d'ordine piantate o senza ordine, un testo
  mescolato) e ogni piega di pagine, si addestra la rete GRU di ia01/ia09 dentro lo stesso testo (stessi semi e stesse pagine di ia09), poi:
  1. Scomposizione: si rimescolano le righe delle pagine di prova in 13 modi (tutte le parole; solo coppie vicine; blocchi; mezze righe;
     prima/ultima; ...) e si guarda quanti bit in piu' paga OGNI parola (si segue la stessa parola da prima a dopo), divisi per posto nella riga,
     pezzo della parola (primo glifo, interno, ultimo glifo, spazio) e "quanto contesto le e' rimasto uguale".
  2. Ablazione: per 3.000 parole scelte a caso (dal terzo posto della riga in poi) si lascia alla rete il contesto della riga ma si cambiano
     le parole prima: rimescolate, tolta la parola prima, o sostituite da un'altra parola dell'addestramento che ha lo stesso pezzo (stesso
     ultimo glifo, stessa lunghezza, ...). Si vede quanta perdita resta.
  3. Regole: dai bit di ogni parola (media di piu' rimescolamenti) si cercano le coppie e terne di pezzi di parole con il maggiore
     contributo e un albero piccolo e una tabella di regole che imitano la rete, provati su pagine mai viste.
- Controlli: testi sintetici con regole piantate di forza nota (con l'"oracolo": la perdita di una rete perfetta), un testo senza ordine,
  il Voynich con le parole mescolate fra tutte le pagine.

Uscite (solo numeri e codici anonimi: nessuna parola, nessun glifo con il suo nome): risultati/ia13_cosa_vede_rete.json e .md e, una riga per
lavoro, risultati/ia13_corse.jsonl. Le regole leggibili (con parole e glifi) e i bit di ogni parola stanno solo in dati/cache/ia13/ (protetto).

Variabili (oltre a quelle di ia01: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, CHIAVI, SEMI, PASSI, OGNI, PAZIENZA, NASCOSTO, CADUTA, USCITA,
e a quelle di ia09: RIGHE_PAGINA_EN): PROCESSI, RIPRENDI, FASI (rete, analisi), FILTRO, NULLI (200), BOOT (1000) e le NUOVE
RIP_TUTTO (rimescolamenti completi per piega, 3), N_OBIETTIVI (parole dell'ablazione per lavoro, 3000), LIBRI13 (libri v21, a13,a14,a15),
CACHE13 (cartella protetta, dati/cache/ia13).
"""
import json, math, os, random, sys, time
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
import vedere_permutazioni as VP  # noqa: E402
import vedere_sintetici as VS  # noqa: E402
import vedere_regole as VR  # noqa: E402

NOME = 'ia13_cosa_vede_rete'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
NF, SEMI = G.NF, G.SEMI
NULLI = int(os.environ.get('NULLI', 200))
BOOT = int(os.environ.get('BOOT', 1000))
RIP_TUTTO = int(os.environ.get('RIP_TUTTO', 3))
N_OBIETTIVI = int(os.environ.get('N_OBIETTIVI', 3000))
LIBRI13 = [x for x in os.environ.get('LIBRI13', 'a13,a14,a15').split(',') if x]
CACHE13 = os.environ.get('CACHE13', os.path.join(QUI, '..', 'dati', 'cache', 'ia13'))

# condizioni dell'ablazione (per ogni parola scelta): contesto della riga prima della parola, cambiato cosi'
#   orig: com'e'; ordine: le stesse parole rimescolate; prec_via: tolta la parola prima;
#   p_X: la parola prima sostituita da una parola con lo stesso pezzo X; r_X: tutte le parole prima sostituite cosi'
COND = ['orig', 'ordine', 'prec_via'] + ['p_' + x for x in VP.PEZZI] + ['r_' + x for x in VP.PEZZI]
VARIANTI = VP.NOMI_VARIANTI


def seme_di(nome):
    return G.seme_di(nome)


# ---------------------------------------------------------------- i testi

_T = OrderedDict()


def nomi_testi():
    """Testi con la rete: 'vere' (2 semi), i libri v21 scelti, due riferimenti (latino solo fuori dalla prova), i sintetici e il
    controllo negativo 'vere~t1' (tutte le parole mescolate fra tutte le pagine)."""
    libri = [b for b in LIBRI13 if int(b[1:]) in G.CHIAVI]
    rif = ([] if SOLO_CONTROLLI else ['latino']) + ['inglese']
    return ['vere'] + libri + rif + ['pianta1', 'pianta2', 'pianta3', 'senzaord', 'vere~t1']


def costruisci(nome):
    """Il testo `nome`: dict(pagine, fold, tipo, [meta, orac]). Uguale in ogni processo (semi fissi)."""
    if nome in _T:
        return _T[nome]
    if '~' in nome:
        base, modo = nome.split('~')
        T = costruisci(base)
        f = TT.rimescola_testo if modo.startswith('t') else TT.rimescola_pagina
        t = dict(pagine=f(T['pagine'], seme_di('ia13:rim:' + nome)), fold=T['fold'], tipo=T['tipo'])
    elif nome == 'vere':
        t = TT.testo_vere()
    elif nome.startswith('a') and nome[1:].isdigit():
        t = TT.testo_libro(nome)
    elif nome == 'latino':
        t = TT.testo_latino()
    elif nome == 'inglese':
        t = TT.testo_inglese()
    elif nome in ('pianta1', 'pianta2', 'pianta3', 'senzaord'):
        base = costruisci('vere')
        Cb = SM.Corpus(base['pagine'])
        pagine, meta, orac = VS.genera_piantato(Cb, seme_di('ia13:gen:' + nome), dict(pianta1='F', pianta2='D', pianta3='R', senzaord='Z')[nome])
        t = dict(pagine=pagine, fold=base['fold'], tipo=None, meta=meta, orac=orac)
    else:
        raise ValueError(nome)
    if len(_T) > 4:
        _T.clear()
    _T[nome] = t
    return t


def seme_testo(nome):
    """Semi della rete per un testo: come ia09 ('vere' due semi, gli altri uno)."""
    return SEMI if nome == 'vere' else SEMI[:1]


# ---------------------------------------------------------------- aggregazione per pagina

def impacchetta(J, e, cat, d_id, d_sl):
    """Per una pagina: i numeri delle parole raggruppati. J posto nella riga, e posto dalla fine (posti della riga, uguali prima e dopo),
    cat categoria del contesto (per parola, indice vecchio), d_id (parole, 4) differenza di bit per pezzo (primo, interno, ultimo, spazio)
    appaiata per PAROLA (la stessa parola prima e dopo), d_sl lo stesso appaiato per POSTO (il posto k prima e dopo). I totali sono uguali;
    i posti si leggono col posto (altrimenti l'a capo, che sta sempre in fondo alla riga, si attribuirebbe alla parola che per caso era
    ultima), le categorie con la parola, e senza l'a capo/spazio (solo i glifi), perche' lo spazio dopo una parola cambia se questa diventa
    l'ultima della riga.
    base (33): n, D (tutti i pezzi), Dg (solo glifi), n per posto(7), Dg per posto(7), n per categoria(6), Dg per categoria(6), D per pezzo(4);
    ext (70): n per posto dalla fine(4), Dg per posto dalla fine(4), Dg per pezzo(3) e categoria(6)=18, D per pezzo(4) e posto(7)=28,
    D per pezzo(4) e posto dalla fine(4)=16."""
    ps, pe = np.minimum(J, 6), np.minimum(e, 3)
    Dg_sl, Dg_id = d_sl[:, :3].sum(1), d_id[:, :3].sum(1)
    base = [float(len(J)), float(d_sl.sum()), float(Dg_sl.sum())]
    base += np.bincount(ps, minlength=7).astype(float).tolist() + np.bincount(ps, weights=Dg_sl, minlength=7).tolist()
    base += np.bincount(cat, minlength=VP.NCAT).astype(float).tolist() + np.bincount(cat, weights=Dg_id, minlength=VP.NCAT).tolist()
    base += d_sl.sum(0).tolist()
    ext = np.bincount(pe, minlength=4).astype(float).tolist() + np.bincount(pe, weights=Dg_sl, minlength=4).tolist()
    for k in range(3):
        ext += np.bincount(cat, weights=d_id[:, k], minlength=VP.NCAT).tolist()
    for k in range(4):
        ext += np.bincount(ps, weights=d_sl[:, k], minlength=7).tolist()
    for k in range(4):
        ext += np.bincount(pe, weights=d_sl[:, k], minlength=4).tolist()
    return np.array(base), np.array(ext)


def arrotonda(v, k=3):
    return [round(float(x), k) for x in v]


# ---------------------------------------------------------------- lavoro di rete (un testo, un seme, una piega)

class Pagina:
    """Una pagina di prova in tipi di parola: righe, posti, e (per ogni parola) indice di riga e di parola."""

    def __init__(self, C, WS, nome, rows_tid):
        self.nome = nome
        self.righe = rows_tid                                 # lista di (inizio, [tipi])
        self.ws = [(ini, [WS[t] for t in ts]) for ini, ts in rows_tid]
        self.nl = [len(ts) for _, ts in rows_tid]
        self.n = sum(self.nl)
        self.J = np.array([j for n in self.nl for j in range(n)], dtype=np.int64)
        self.e = np.array([n - 1 - j for n in self.nl for j in range(n)], dtype=np.int64)
        self.riga = np.array([l for l, n in enumerate(self.nl) for _ in range(n)], dtype=np.int64)
        self.inizi = np.concatenate([[0], np.cumsum(self.nl)]).astype(np.int64)
        self.tok = np.array([t for _, ts in rows_tid for t in ts], dtype=np.int64)


def righe_tid(C, p):
    P = C.pag[p]
    return [(bool(P.ini[P.lstart[l]]), [int(t) for t in P.tok[P.lstart[l]:P.lstart[l + 1]]]) for l in range(len(P.lstart) - 1)]


def passata(m, idx, pagine, pis=None):
    """Costi in bit (parole, 4) di ogni parola di ogni pagina: rimessi nell'ordine VECCHIO delle parole (appaiati per parola), nell'ordine dei
    posti (appaiati per posto) e la categoria del contesto.
    `pis[nome pagina]` = permutazioni per riga (None = ordine vero). Stesso passo di ia09: la pagina e' un flusso unico, parte da un a capo."""
    righe_n, liste = [], []
    for pg in pagine:
        if pis is None:
            rows = pg.ws
        else:
            rows = [(ini, [ws[i] for i in pi]) for (ini, ws), pi in zip(pg.ws, pis[pg.nome])]
        righe_n.append(rows)
        liste.append(G.codifica(rows, idx))
    sv = G.sorprese(m, liste)
    out = []
    for pg, rows, x in zip(pagine, righe_n, sv):
        c4 = VP.costi_parola(x, VP.posizioni_parole(rows))
        if pis is None:
            out.append((c4, c4, None))
            continue
        vecchio = np.concatenate([pg.inizi[l] + np.array(pi, dtype=np.int64) for l, pi in enumerate(pis[pg.nome])]) if pg.n else np.zeros(0, dtype=np.int64)
        c_old = np.zeros_like(c4)
        c_old[vecchio] = c4
        cat = np.concatenate([np.array(VP.categorie(pi), dtype=np.int64) for pi in pis[pg.nome]]) if pg.n else np.zeros(0, dtype=np.int64)
        out.append((c_old, c4, cat))
    return out


def passata_oracolo(orac, pagine, pis=None):
    """Costi dell'oracolo (bit per parola): (ordine vecchio, ordine dei posti)."""
    out = []
    for pg in pagine:
        nuovo, slot = np.zeros(pg.n), np.zeros(pg.n)
        for l, (ini, ts) in enumerate(pg.righe):
            s = pg.inizi[l]
            if pis is None:
                nuovo[s:s + len(ts)] = slot[s:s + len(ts)] = orac.costi(ts)
            else:
                pi = pis[pg.nome][l]
                c = orac.costi([ts[i] for i in pi])
                slot[s:s + len(ts)] = c
                for k, i in enumerate(pi):
                    nuovo[s + i] = c[k]
        out.append((nuovo, slot))
    return out


def pesi_testo(C, add):
    cw = np.zeros(C.nt, dtype=np.int64)
    for p in add:
        cw += np.bincount(C.pag[p].tok, minlength=C.nt)
    return cw


def ablazione(m, idx, C, WS, pagine, cls, cw, nome, seme, piega, orac):
    """Per N_OBIETTIVI parole delle pagine di prova (dal terzo posto della riga) e ogni condizione di COND, i bit della parola.
    Restituisce, per pagina, [n parole, somma dei bit per ogni condizione] (e lo stesso con l'oracolo, se c'e')."""
    R = VP.Ricambi(C, cw, cls)
    cand = [(ip, l, i) for ip, pg in enumerate(pagine) for l, n in enumerate(pg.nl) for i in range(2, n)]
    rnd = random.Random(seme_di('ia13:obiettivi:%s:%d:%d' % (nome, seme, piega)))
    scelti = sorted(rnd.sample(range(len(cand)), N_OBIETTIVI)) if len(cand) > N_OBIETTIVI else list(range(len(cand)))
    obiettivi = [cand[k] for k in scelti]
    nc = len(COND)
    costi = np.zeros((len(obiettivi), nc))
    cor = np.zeros((len(obiettivi), nc)) if orac is not None else None
    for ci, cond in enumerate(COND):
        liste, pos, ctxs = [], [], []
        for ti, (ip, l, i) in enumerate(obiettivi):
            ini, ts = pagine[ip].righe[l]
            pref, tgt = ts[:i], ts[i]
            nxt = [ts[i + 1]] if i + 1 < len(ts) else []
            r = random.Random(seme_di('ia13:abl:%s:%d:%d:%d:%d' % (nome, seme, piega, ti, ci)))
            if cond == 'orig':
                ctx = pref
            elif cond == 'ordine':
                ctx = list(pref)
                r.shuffle(ctx)
            elif cond == 'prec_via':
                ctx = pref[:-1]
            elif cond.startswith('p_'):
                ctx = pref[:-1] + [R.estrai(cond[2:], pref[-1], r)]
            else:
                ctx = [R.estrai(cond[2:], t, r) for t in pref]
            rows = [(ini, [WS[t] for t in ctx + [tgt] + nxt])]
            liste.append(G.codifica(rows, idx))
            pos.append(VP.posizioni_parole(rows)[len(ctx)])
            if cor is not None:
                cor[ti, ci] = orac.costi(ctx + [tgt])[-1]
        sv = G.sorprese(m, liste, blocco=64)
        for ti, (x, (a, ln, _)) in enumerate(zip(sv, pos)):
            costi[ti, ci] = float(x[a:a + ln + 1].sum())
    per = {}
    for ti, (ip, l, i) in enumerate(obiettivi):
        v = per.setdefault(pagine[ip].nome, np.zeros(1 + nc))
        v[0] += 1
        v[1:] += costi[ti]
    per_o = None
    if cor is not None:
        per_o = {}
        for ti, (ip, l, i) in enumerate(obiettivi):
            v = per_o.setdefault(pagine[ip].nome, np.zeros(1 + nc))
            v[0] += 1
            v[1:] += cor[ti]
    return per, per_o, dict(obiettivi=len(obiettivi), candidati=len(cand), ricambi_senza_pezzo=round(R.fallite / max(R.richieste, 1), 4))


def salva_parole(nome, seme, piega, C, pagine, deltas, ctrue):
    """Bit di ogni parola di prova (per le regole): solo in cache protetta, mai nei risultati."""
    os.makedirs(os.path.join(CACHE13, 'parole'), exist_ok=True)
    pag, rig, J, nl, gl, off = [], [], [], [], [], [0]
    for ip, pg in enumerate(pagine):
        for t, r, j, n in zip(pg.tok, pg.riga, pg.J, np.repeat(pg.nl, pg.nl)):
            pag.append(ip)
            rig.append(r)
            J.append(j)
            nl.append(n)
            gl.extend(C.tipi[int(t)])
            off.append(len(gl))
    np.savez_compressed(os.path.join(CACHE13, 'parole', 'parole_%s_s%d_f%d.npz' % (nome, seme, piega)),
                        pagine=np.array([pg.nome for pg in pagine]), pag=np.array(pag, dtype=np.int32), riga=np.array(rig, dtype=np.int32),
                        J=np.array(J, dtype=np.int16), nl=np.array(nl, dtype=np.int16), gl=np.array(gl, dtype=np.int16),
                        off=np.array(off, dtype=np.int64), glifi=np.array(C.glifi), ctrue=np.concatenate(ctrue),
                        delta=np.concatenate(deltas, axis=0).astype(np.float32))


def lavoro_N(nome, seme, piega):
    """Un lavoro: la rete di (testo, seme, piega) come in ia09; scomposizione, ablazione, bit di ogni parola."""
    inizio = time.time()
    T = costruisci(nome)
    nomi = sorted(T['pagine'])
    C = SM.Corpus(T['pagine'])
    C.prepara()
    WS = [C.parole_in_glifi(t) for t in range(C.nt)]
    idx = {g: i + 4 for i, g in enumerate(C.glifi[:-1])}
    V = 4 + len(C.glifi) - 1
    ids = {p: G.codifica([(i0, [WS[t] for t in ts]) for i0, ts in righe_tid(C, p)], idx) for p in nomi}
    test = [p for p in nomi if T['fold'][p] == piega]
    resto = [p for p in nomi if T['fold'][p] != piega]
    random.Random(3964 + 100 * seme + piega).shuffle(resto)          # come ia09
    nval = max(1, round(0.10 * len(resto)))
    val, add = resto[:nval], resto[nval:]
    flusso = lambda ps: np.concatenate([ids[p] for p in ps])
    m, info = G.addestra_lm(flusso(add), flusso(val), V, 1000 * seme + piega)
    t_rete = time.time()
    cw = pesi_testo(C, add)
    cls, K = SM.classi(C, add, seme=piega + 1)
    info['classi'] = int(K)
    pagine = [Pagina(C, WS, p, righe_tid(C, p)) for p in test]
    orac = T.get('orac')
    if orac is not None:
        orac.prepara(C)
    # ordine vero
    vero = passata(m, idx, pagine)
    c_true = [c4 for c4, _, _ in vero]
    t_true = [c[:, :3].sum(1) for c in c_true]                     # per le regole: solo i glifi
    o_vero = passata_oracolo(orac, pagine) if orac is not None else None
    o_true = [x[0] for x in o_vero] if o_vero else None
    passata_oracolo_vero = [x[1] for x in o_vero] if o_vero else None
    stat = {pg.nome: dict(v={}, vo={}) for pg in pagine}
    deltas = [np.zeros((pg.n, RIP_TUTTO)) for pg in pagine]
    for var in VARIANTI:
        rip = RIP_TUTTO if var == 'tutto' else 1
        acc = {pg.nome: [0.0] * rip for pg in pagine}
        base_m = {pg.nome: 0.0 for pg in pagine}
        ext_m = {pg.nome: 0.0 for pg in pagine}
        orb_m = {pg.nome: 0.0 for pg in pagine}
        for r in range(rip):
            if var == 'tutto' and r == 0:
                seme_p = seme_di('ia09:riga:' + nome)          # lo stesso rimescolamento di ia09 (riproduzione)
            else:
                seme_p = seme_di('ia13:%s:%d:%s' % (var, r, nome))
            pis_tutti = VP.permutazioni(T['pagine'], var, seme_p)
            nuovo = passata(m, idx, pagine, pis_tutti)
            o_new = passata_oracolo(orac, pagine, pis_tutti) if orac is not None else None
            for k, (pg, (c_new, c_slot, cat)) in enumerate(zip(pagine, nuovo)):
                d4 = c_new - c_true[k]
                d_sl = c_slot - c_true[k]
                b, x = impacchetta(pg.J, pg.e, cat, d4, d_sl)
                base_m[pg.nome] = base_m[pg.nome] + b / rip
                if var == 'tutto':
                    ext_m[pg.nome] = ext_m[pg.nome] + x / rip
                    deltas[k][:, r] = d4[:, :3].sum(1)
                    acc[pg.nome][r] = float(d4.sum())
                if o_new is not None:
                    do, do_sl = o_new[k][0] - o_true[k], o_new[k][1] - passata_oracolo_vero[k]
                    z = np.zeros_like(do)
                    bo, _ = impacchetta(pg.J, pg.e, cat, np.stack([do, z, z, z], 1), np.stack([do_sl, z, z, z], 1))
                    orb_m[pg.nome] = orb_m[pg.nome] + bo / rip
        for pg in pagine:
            s = stat[pg.nome]
            s['v'][var] = arrotonda(base_m[pg.nome], 3)
            if var == 'tutto':
                s['e'] = arrotonda(ext_m[pg.nome], 3)
                s['tr'] = [len(pg.tok)] + [round(x, 3) for x in acc[pg.nome][:RIP_TUTTO]]
            if orac is not None:
                s['vo'][var] = arrotonda(orb_m[pg.nome], 3)
    salva_parole(nome, seme, piega, C, pagine, deltas, t_true)
    t_var = time.time()
    ab, ab_o, info_ab = ablazione(m, idx, C, WS, pagine, cls, cw, nome, seme, piega, orac)
    for pg in pagine:
        stat[pg.nome]['a'] = arrotonda(ab.get(pg.nome, np.zeros(1 + len(COND))), 2)
        if ab_o is not None:
            stat[pg.nome]['ao'] = arrotonda(ab_o.get(pg.nome, np.zeros(1 + len(COND))), 2)
        stat[pg.nome]['n'] = pg.n
    info.update(info_ab)
    info['tempi_s'] = dict(rete=round(t_rete - inizio, 1), rimescolamenti=round(t_var - t_rete, 1), ablazione=round(time.time() - t_var, 1))
    info['parole_prova'] = int(sum(pg.n for pg in pagine))
    if orac is not None:
        info['oracolo'] = dict(p1=orac.p1, p2=orac.p2, p3=orac.p3)
    return dict(job=['N', nome, seme, piega], tipo='N', info=info, stat=stat, tempo=round(time.time() - inizio, 1))


def lavoro(job):
    return lavoro_N(job[1], job[2], job[3])


def lavori(fasi):
    L = []
    if 'rete' in fasi:
        for nome in nomi_testi():
            for s in seme_testo(nome):
                for f in range(NF):
                    L.append(('N', nome, s, f))
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(j) for x in filtro)]
    return L


def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


# ---------------------------------------------------------------- analisi

# soglie e limiti delle letture e dei controlli (fissati nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_NEG = 0.03          # bit per parola: massimo "valore dell'ordine" in un testo senza ordine
SOGLIA_NEG_ABL = 0.05      # idem per le prove dell'ablazione (meno parole: piu' rumore)
SOGLIA_R2_NEG = 0.03       # R2 massimo di un albero su un testo senza ordine
RAPPORTO_ORACOLO = (0.5, 1.5)   # perdita della rete / perdita di una rete perfetta (testo con regole piantate forti)
RHO_VARIANTI, RHO_ABL = 0.85, 0.70    # correlazione di rango rete-oracolo
RANGO_CELLA = 3            # la cella piantata deve stare fra le prime 3
PRIMO_POSTO = (0.7, 2.0)   # perdita della rete nel primo posto / quella dell'oracolo (regola piantata a inizio riga)
CONTRASTO_CONTATTO = 1.0   # bit: parole che cominciano con Y dopo X meno altrove, limite basso dell'intervallo
CONTRASTO_DIST2 = 0.3      # bit: lo stesso per la regola a distanza 2 (sensibilita')
SOGLIA_BIT, SOGLIA_RAPP = 0.03, 0.05     # differenza minima v21-vere: bit per parola; rapporti e quote
BORDO_SI, BORDO_NO = 1.5, 0.67            # rapporto fra la perdita al bordo e all'interno
QUOTA_PEZZO_SI, QUOTA_PEZZO_NO = 0.5, 0.4  # quota della perdita sul primo glifo
VICINO_SI, VICINO_NO = 0.75, 0.35          # parola prima / tutta la riga
PEZZO_SUFF, PEZZO_INS = 0.80, 0.50         # quota che resta quando si lascia alla rete solo un pezzo
R2_SI, R2_NO = 0.30, 0.10                  # R2 fuori campione delle regole
PARZIALI = ['vicine', 'finestra3', 'blocchi2', 'blocchi3', 'mezze', 'bordi_fissi', 'solo_bordi', 'prima_sposta', 'ultima_sposta',
            'pari_mescolati', 'dispari_mescolati']
FAMIGLIE_TOP = ['contatto: ultimo(prec) -> primo', 'ultimo(prec2) -> primo (distanza 2)', 'terna: ultimo(prec2), ultimo(prec) -> primo']
FOGLIE = (4, 8, 16, 32)
NOMI_PEZZO_PAROLA = ['primo glifo', 'glifi interni', 'ultimo glifo', 'spazio o a capo']


class V:
    """Un numero con la sua distribuzione bootstrap (stesso ricampionamento di pagine per tutti). Copiato (semplificato) da ia09."""

    def __init__(self, p, b):
        self.p = float(p)
        self.b = np.asarray(b, dtype=float)

    def ic(self):
        b = self.b[~np.isnan(self.b)]
        return [float(v) for v in np.percentile(b, [2.5, 97.5])] if len(b) > 20 else [float('nan')] * 2

    def d(self):
        return OrderedDict(punto=self.p, ic=self.ic())


_W = {}


def pesi_bootstrap(P):
    if P not in _W:
        rng = np.random.default_rng(880009 + P)
        _W[P] = np.stack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(BOOT)]).astype(float)
    return _W[P]


def rap(num, den):
    """Rapporto di due somme su pagine: funzione dei pesi W (B, P) -> (B,)."""
    def f(W):
        with np.errstate(divide='ignore', invalid='ignore'):
            return (W @ num) / (W @ den)
    return f


def div(a, b):
    with np.errstate(divide='ignore', invalid='ignore'):
        return a / b


def val(f, P):
    W = pesi_bootstrap(P)
    return V(f(np.ones((1, P)))[0], f(W))


def f3(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%+.3f' % x


def f2(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%.2f' % x


def vv(d):
    if d is None:
        return '-'
    return '%s (%s; %s)' % (f3(d['punto']), f3(d['ic'][0]), f3(d['ic'][1]))


def ve(x):
    return vv(x.d()) if isinstance(x, V) else vv(x)


IB = dict(n=0, D=1, Dg=2, nps=3, dps=10, ncat=17, dcat=23, dcls=29)       # posizioni nel vettore "base" di ogni pagina
IE = dict(npe=0, dpe=4, dcc=8, dcp=26, dce=54)                             # e nel vettore "ext"


class Testo:
    """I numeri per pagina di un testo (media sui semi), dai lavori di rete."""

    def __init__(self, nome, corse):
        rc = [r for r in corse if r['job'][1] == nome]
        acc = defaultdict(list)
        for r in rc:
            for p, s in r['stat'].items():
                acc[p].append(s)
        self.nome = nome
        self.pag = sorted(acc)
        self.lavori = len(rc)
        self.semi = len({r['job'][2] for r in rc})
        self.completo = bool(rc) and len(rc) == self.semi * NF
        P = len(self.pag)

        def media(f):
            return np.array([np.mean([f(s) for s in acc[p]], axis=0) for p in self.pag], dtype=float)
        self.n = media(lambda s: s['n'])
        self.var = {v: media(lambda s, v=v: s['v'][v]) for v in VARIANTI}
        self.ext = media(lambda s: s['e'])
        self.tr = media(lambda s: s['tr'])
        self.abl = media(lambda s: s['a'])
        s0 = acc[self.pag[0]][0] if P else {}
        self.orac = bool(s0.get('vo'))
        if self.orac:
            self.var_o = {v: media(lambda s, v=v: s['vo'][v]) for v in VARIANTI}
            self.abl_o = media(lambda s: s['ao'])
        self.info = [r['info'] for r in rc]

    @property
    def P(self):
        return len(self.pag)

    def restringi(self, pag):
        """Lo stesso testo con le sole pagine date (nomi)."""
        ix = [self.pag.index(p) for p in pag]
        t = Testo.__new__(Testo)
        t.__dict__.update(self.__dict__)
        t.pag = list(pag)
        for k in ('n', 'ext', 'tr', 'abl'):
            setattr(t, k, getattr(self, k)[ix])
        t.var = {v: a[ix] for v, a in self.var.items()}
        if self.orac:
            t.var_o = {v: a[ix] for v, a in self.var_o.items()}
            t.abl_o = self.abl_o[ix]
        return t

    def catalogo(self, oracolo=False):
        """Tutte le misure di un testo, come funzioni dei pesi di pagina W."""
        c = OrderedDict()
        var = self.var_o if oracolo else self.var
        ab = self.abl_o if oracolo else self.abl
        v = var['tutto']
        c['dt'] = rap(v[:, IB['D']], v[:, IB['n']])                # tutti i pezzi (come ia09)
        c['dtg'] = rap(v[:, IB['Dg']], v[:, IB['n']])              # solo i glifi (senza lo spazio / a capo)
        for b in range(7):
            c['dt_j%d' % b] = rap(v[:, IB['dps'] + b], v[:, IB['nps'] + b])      # per posto, solo glifi
        c['dt_j2piu'] = rap(v[:, IB['dps'] + 2:IB['dps'] + 7].sum(1), v[:, IB['nps'] + 2:IB['nps'] + 7].sum(1))
        c['R_prima'] = lambda W: div(c['dt_j0'](W), c['dt_j2piu'](W))
        for k in range(VP.NCAT):
            c['cat_%d' % k] = rap(v[:, IB['dcat'] + k], v[:, IB['ncat'] + k])
            c['quota_parole_cat_%d' % k] = rap(v[:, IB['ncat'] + k], v[:, IB['n']])
        for var_n in VARIANTI:
            w = var[var_n]
            c['dv_' + var_n] = rap(w[:, IB['D']], w[:, IB['n']])
            c['rotte_' + var_n] = rap(w[:, IB['ncat']] + w[:, IB['ncat'] + 1], w[:, IB['n']])
        num_l = sum(var[x][:, IB['dcat'] + 2:IB['dcat'] + 5].sum(1) for x in PARZIALI)
        den_l = sum(var[x][:, IB['ncat'] + 2:IB['ncat'] + 5].sum(1) for x in PARZIALI)
        num_v = sum(var[x][:, IB['dcat']:IB['dcat'] + 2].sum(1) for x in PARZIALI)
        den_v = sum(var[x][:, IB['ncat']:IB['ncat'] + 2].sum(1) for x in PARZIALI)
        c['R_lont'] = lambda W: div(rap(num_l, den_l)(W), rap(num_v, den_v)(W))
        c['parz_lont'] = rap(num_l, den_l)
        c['parz_vic'] = rap(num_v, den_v)
        if not oracolo:
            e = self.ext
            for b in range(4):
                c['dt_e%d' % b] = rap(e[:, IE['dpe'] + b], e[:, IE['npe'] + b])
            c['dt_e2piu'] = rap(e[:, IE['dpe'] + 2:IE['dpe'] + 4].sum(1), e[:, IE['npe'] + 2:IE['npe'] + 4].sum(1))
            c['R_ultima'] = lambda W: div(c['dt_e0'](W), c['dt_e2piu'](W))
            for k, nm in enumerate(['primo', 'interno', 'ultimo', 'spazio']):
                c['quota_' + nm] = rap(v[:, IB['dcls'] + k], v[:, IB['D']])
                c['pc_j0_' + nm] = rap(e[:, IE['dcp'] + k * 7], v[:, IB['nps']])        # per pezzo, nel primo posto
                c['pc_e0_' + nm] = rap(e[:, IE['dce'] + k * 4], e[:, IE['npe']])        # per pezzo, nell'ultimo posto
        # ablazione: i bit in piu' rispetto alla parola con il suo contesto vero
        S0 = ab[:, 1]
        for i, cond in enumerate(COND):
            if cond != 'orig':
                c['A_' + cond] = rap(ab[:, 1 + i] - S0, ab[:, 0])
        for pz in VP.PEZZI:
            if pz != 'nessuno':
                c['Q_' + pz] = lambda W, pz=pz: div(c['A_p_nessuno'](W) - c['A_p_' + pz](W), c['A_p_nessuno'](W))
                c['QR_' + pz] = lambda W, pz=pz: div(c['A_r_nessuno'](W) - c['A_r_' + pz](W), c['A_r_nessuno'](W))
        c['vicino'] = lambda W: div(c['A_p_nessuno'](W), c['A_r_nessuno'](W))
        c['qord'] = lambda W: div(c['A_ordine'](W), c['A_r_nessuno'](W))
        return c


def etichetta_rapporto(v, si, no):
    ic = v.ic()
    if v.p >= si and ic[0] >= 1 + (si - 1) / 2:
        return 'piu\' alta'
    if v.p <= no and ic[1] <= 1 - (1 - no) / 2:
        return 'piu\' bassa'
    if ic[0] >= 0.8 and ic[1] <= 1.25:
        return 'come l\'interno'
    return 'zona grigia'


def lettura_quota(v, si, no):
    ic = v.ic()
    if v.p >= si and ic[0] >= no:
        return 'si'
    if ic[1] < no:
        return 'no'
    return 'zona grigia'


def lettura_vicino(v):
    ic = v.ic()
    if v.p >= VICINO_SI and ic[0] >= 0.6:
        return 'vicino'
    if v.p <= VICINO_NO and ic[1] <= 0.5:
        return 'lontano'
    return 'misto'


def lettura_pezzo(v):
    ic = v.ic()
    if v.p >= PEZZO_SUFF and ic[0] >= 0.7:
        return 'sufficiente'
    if v.p <= PEZZO_INS and ic[1] <= 0.6:
        return 'insufficiente'
    return 'zona grigia'


def lettura_r2(v):
    ic = v.ic()
    if v.p >= R2_SI and ic[0] >= 0.20:
        return 'spiegano'
    if ic[1] <= R2_NO:
        return 'poco'
    return 'zona grigia'


# ---------------------------------------------------------------- regole

def codici_glifi(D):
    """Codice anonimo di ogni glifo: rango di frequenza fra tutte le parole di prova (1 = il piu' frequente)."""
    c = Counter(g for w in D['parola'] for g in w)
    return {g: '#%d' % (i + 1) for i, (g, _) in enumerate(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))}


def cod_el(x, cod):
    if isinstance(x, str):
        return cod.get(x, '?')
    if isinstance(x, tuple):
        if x == VR.NA:
            return 'NA'
        return ''.join(cod_el(y, cod) for y in x)
    return str(x)


def r2v(sse, sst, P):
    W = pesi_bootstrap(P)
    with np.errstate(divide='ignore', invalid='ignore'):
        return V(1 - sse.sum() / sst.sum(), 1 - (W @ sse) / (W @ sst))


def regole_testo(nome, semi, meta=None, scrivi=True):
    """Estrazione di regole dai bit di ogni parola (cache protetta): R2 fuori campione di tabelle di pezzi e di alberi, celle principali,
    soffitto. `meta` = glifi piantati (solo per i controlli). Restituisce (dizionario di numeri e codici, dizionario con i controlli)."""
    D = VR.carica_parole(CACHE13, nome, semi)
    if D is None:
        return None, None
    R = VR.tabella_regole(D)
    P = len(D['pagine'])
    y = R['y']
    cod = codici_glifi(D)
    aux = dict(rango={})
    if meta:
        pl = np.array([x[-1] for x in R['p1']])
        fc = np.array([x[0] for x in R['w']])
        p2l = np.array([x[-1] if x else '' for x in R['p2']])

        def contrasto(m_in, m_out):
            pg = R['pag']
            s_i, n_i = np.bincount(pg[m_in], weights=y[m_in], minlength=P), np.bincount(pg[m_in], minlength=P).astype(float)
            s_o, n_o = np.bincount(pg[m_out], weights=y[m_out], minlength=P), np.bincount(pg[m_out], minlength=P).astype(float)
            return OrderedDict(differenza=val(lambda W: div(W @ s_i, W @ n_i) - div(W @ s_o, W @ n_o), P), parole_dentro=int(n_i.sum()), parole_fuori=int(n_o.sum()))
        mY = fc == meta['Y']
        aux['contrasto_contatto'] = contrasto(mY & (pl == meta['X']), mY & (pl != meta['X']))
        mW = (fc == meta['W']) & (pl != meta['X']) & (p2l != '')
        aux['contrasto_dist2'] = contrasto(mW & (p2l == meta['U']), mW & (p2l != meta['U']))
    if len(set(D['fold'].tolist())) < 2:
        return None, aux                                        # servono almeno due pieghe per provare fuori campione
    out = OrderedDict(righe=int(len(y)), semi=D['n_semi'], delta_medio=float(y.mean()), soffitto=VR.soffitto(R['yr']))
    fam = VR.chiavi_famiglie(R)
    out['famiglie'] = OrderedDict()
    testo_cache = []
    for k, chiavi in fam.items():
        codici, dic = VR.codifica(chiavi)
        sse, sst = VR.valuta_tabella(codici, y, R['fold'], R['pag'], P)
        voce = OrderedDict(celle=len(dic), R2=r2v(sse, sst, P))
        if k in FAMIGLIE_TOP:
            for top in (10, 30, 100):
                a, b = VR.valuta_tabella(codici, y, R['fold'], R['pag'], P, top=top)
                voce['R2_top%d' % top] = r2v(a, b, P)
            celle, mu = VR.celle_top(codici, dic, y, 10)
            voce['celle_top'] = [OrderedDict(chiave=cod_el(c[0], cod), parole=c[1], delta_medio=c[2], contributo=c[3], quota=c[4]) for c in celle]
            testo_cache.append('## %s (media generale %.3f)' % (k, mu))
            for c in celle:
                esempi = Counter(' '.join(w) for w, kk in zip(R['w'], chiavi) if kk == c[0]).most_common(5)
                testo_cache.append('  %s: n=%d media=%.3f contributo=%.1f  esempi: %s' % (c[0], c[1], c[2], c[3], '; '.join('%s x%d' % e for e in esempi)))
            if meta:
                if k == FAMIGLIE_TOP[0]:
                    aux['rango']['contatto'] = VR.rango_cella(codici, dic, y, (meta['X'], meta['Y']))
                if k == FAMIGLIE_TOP[1]:
                    aux['rango']['distanza2'] = VR.rango_cella(codici, dic, y, (meta['U'], meta['W']))
        out['famiglie'][k] = voce
    glifi = sorted({g for w in D['parola'] for g in w})
    X, nomi = VR.matrice_albero(R, glifi)
    lab = [('%s=%s' % (n[0], cod_el(n[1], cod)) if n[1] != 0 else n[0]) for n in nomi]
    reale = [('%s=%s' % (n[0], ' '.join(n[1]) if isinstance(n[1], tuple) else n[1]) if n[1] != 0 else n[0]) for n in nomi]
    out['albero'] = OrderedDict()
    for L in FOGLIE:
        sse, sst = VR.valuta_albero(X, y, R['fold'], R['pag'], P, L)
        out['albero'][L] = r2v(sse, sst, P)
    from sklearn.tree import export_text
    t8 = VR.albero_intero(X, y, 8)
    out['albero8_codici'] = export_text(t8, feature_names=lab, max_depth=4, decimals=2).splitlines()
    out['domande_principali'] = [lab[i] for i in VR.prime_domande(t8, nomi, 5)]
    if scrivi:
        os.makedirs(os.path.join(CACHE13, 'regole'), exist_ok=True)
        t16 = VR.albero_intero(X, y, 16)
        with open(os.path.join(CACHE13, 'regole', 'regole_%s.txt' % nome), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# regole leggibili di %s (con glifi e parole veri): SOLO in cache protetta\n' % nome)
            f.write('# codici: %s\n' % ', '.join('%s=%s' % (v, k) for k, v in cod.items()))
            f.write('\n'.join(testo_cache) + '\n\n## albero a 16 foglie\n')
            f.write(export_text(t16, feature_names=reale, decimals=2) + '\n')
    aux['albero16'] = out['albero'][16]
    out['migliore_famiglia'] = max(((k, v['R2']) for k, v in out['famiglie'].items() if k != 'la parola intera'), key=lambda kv: kv[1].p)[0]
    return out, aux


# ---------------------------------------------------------------- confronti, controlli, letture

def spearman(a, b):
    from scipy.stats import spearmanr
    r = spearmanr(a, b).correlation
    return float(r) if r == r else float('nan')


def nullo_meta(stat_funcs, P, seme=3980):
    """NULLI divisioni a caso delle pagine vere in due meta': 97,5% del valore assoluto della differenza fra le due meta' (come ia09)."""
    out = {}
    masks = []
    for s in range(NULLI):
        ordine = list(range(P))
        random.Random(seme + s).shuffle(ordine)
        a = np.zeros(P)
        a[ordine[:P // 2]] = 1.0
        masks.append(a)
    A = np.array(masks)
    for nome, f in stat_funcs.items():
        d = f(A) - f(1.0 - A)
        out[nome] = float(np.nanpercentile(np.abs(d), 97.5))
    return out


STAT_CONFRONTO = (['dt', 'dt_j0', 'dt_j2piu', 'R_prima', 'R_ultima', 'dt_e0', 'dt_e2piu', 'quota_primo', 'quota_interno', 'quota_ultimo', 'quota_spazio'] +
                  ['dv_' + v for v in VARIANTI[1:]] + ['A_ordine', 'A_prec_via', 'A_p_nessuno', 'A_r_nessuno', 'vicino', 'qord', 'R_lont'] +
                  ['Q_' + p for p in VP.PEZZI if p != 'nessuno'])


def e_in_bit(nome):
    return nome.startswith(('dt', 'dv_', 'A_')) and not nome.startswith('R_')


def confronto_v21(TT):
    """Per ogni misura: v21 (media dei libri) meno vere, intervallo, nullo (vere divise a caso), esito."""
    libri = [b for b in LIBRI13 if b in TT]
    if 'vere' not in TT or not libri:
        return None
    pag = TT['vere'].pag
    for b in libri:
        pag = [p for p in pag if p in TT[b].pag]
    tv = TT['vere'].restringi(pag)
    tl = [TT[b].restringi(pag) for b in libri]
    P = len(pag)
    cv = tv.catalogo()
    cl = [t.catalogo() for t in tl]
    nomi = [s for s in STAT_CONFRONTO if s in cv]
    nul = nullo_meta({s: cv[s] for s in nomi}, P)
    out = OrderedDict()
    for s in nomi:
        fv = cv[s]
        f21 = (lambda W, s=s: np.mean([c[s](W) for c in cl], axis=0))
        gv, g21 = val(fv, P), val(f21, P)
        dif = val(lambda W, s=s, f21=f21, fv=fv: f21(W) - fv(W), P)
        soglia = SOGLIA_BIT if e_in_bit(s) else SOGLIA_RAPP
        lim = max(nul[s], soglia)
        ic = dif.ic()
        e = ('meno' if (dif.p <= -lim and ic[1] < 0) else 'piu' if (dif.p >= lim and ic[0] > 0) else 'uguale' if abs(dif.p) < nul[s] else 'zona grigia')
        out[s] = OrderedDict(vere=gv.d(), v21=g21.d(), differenza=dif.d(), nullo97=nul[s], limite=lim, esito=e)
    out['_pagine'] = P
    out['_libri'] = libri
    return out


def riassunto(T, oracolo=False):
    """Il blocco di risultati di un testo (numeri; nessuna parola)."""
    P = T.P
    cat = T.catalogo(oracolo)
    o = OrderedDict()
    o['pagine'] = P
    o['parole'] = float(T.n.sum())
    o['semi'] = T.semi
    for k, f in cat.items():
        o[k] = val(f, P)
    return o


def riproduzione_ia09(T):
    """Il rimescolamento 'tutto' (primo) e' quello di ia09: la differenza per pagina deve essere minima (descrittivo)."""
    percorso = os.path.join(USCITA, 'ia09_corse.jsonl')
    if T.nome != 'vere' or not os.path.exists(percorso):
        return dict(disponibile=False)
    acc = defaultdict(list)
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            if r.get('tipo') == 'N' and r['job'][1] == 'vere':
                for p, s in r['stat'].items():
                    acc[p].append(s[2][1] - s[1][1])
    ix = [i for i, p in enumerate(T.pag) if p in acc]
    if not ix:
        return dict(disponibile=False)
    mio = np.array([T.tr[i, 1] for i in ix])
    vecchio = np.array([np.mean(acc[T.pag[i]]) for i in ix])
    n = np.array([T.n[i] for i in ix])
    return OrderedDict(disponibile=True, pagine=len(ix), mio_per_parola=float(mio.sum() / n.sum()), ia09_per_parola=float(vecchio.sum() / n.sum()),
                       max_diff_per_pagina=float(np.max(np.abs(mio - vecchio))))


def controlli(TT, RG, AUX, S):
    """Controlli preregistrati. TT testi, RG regole, AUX dati ausiliari, S riassunti (V)."""
    c = OrderedDict()
    # negativi: testo senza ordine e il Voynich mescolato fra tutte le pagine
    neg = OrderedDict()
    for nome in ('senzaord', 'vere~t1'):
        if nome not in S:
            continue
        s = S[nome]
        bit = {k: s[k].p for k in ['dt'] + ['dv_' + v for v in VARIANTI[1:]]}
        abl = {k: s[k].p for k in ['A_ordine', 'A_prec_via', 'A_p_nessuno', 'A_r_nessuno']}
        r2 = RG.get(nome) and RG[nome]['albero'][16].p
        ok = all(abs(x) <= SOGLIA_NEG for x in bit.values()) and all(abs(x) <= SOGLIA_NEG_ABL for x in abl.values())
        if r2 is not None:
            ok = ok and r2 <= SOGLIA_R2_NEG
        neg[nome] = OrderedDict(max_abs_bit=max(abs(x) for x in bit.values()), max_abs_ablazione=max(abs(x) for x in abl.values()), R2_albero16=r2, superato=bool(ok))
    if neg:
        c['negativo_senza_ordine'] = OrderedDict(testi=neg, superato=all(x['superato'] for x in neg.values()))
    # positivo: regole piantate forti, con l'oracolo
    if 'pianta1' in S and TT['pianta1'].orac:
        t = TT['pianta1']
        s, so = S['pianta1'], riassunto(t, oracolo=True)
        aux = AUX.get('pianta1') or {}
        rap_o = s['dt'].p / so['dt'].p
        rv = spearman([s['dv_' + v].p for v in VARIANTI], [so['dv_' + v].p for v in VARIANTI])
        conds = [x for x in COND if x != 'orig']
        ra = spearman([s['A_' + x].p for x in conds], [so['A_' + x].p for x in conds])
        j0 = s['dt_j0'].p / so['dt_j0'].p
        rango = aux.get('rango', {}).get('contatto')
        cc, c2 = aux.get('contrasto_contatto'), aux.get('contrasto_dist2')
        ok = (RAPPORTO_ORACOLO[0] <= rap_o <= RAPPORTO_ORACOLO[1] and rv >= RHO_VARIANTI and ra >= RHO_ABL and PRIMO_POSTO[0] <= j0 <= PRIMO_POSTO[1] and
              rango is not None and rango <= RANGO_CELLA and cc is not None and cc['differenza'].ic()[0] >= CONTRASTO_CONTATTO)
        c['positivo_piantato'] = OrderedDict(
            perdita_rete=s['dt'].d(), perdita_oracolo=so['dt'].d(), rapporto_rete_oracolo=rap_o, correlazione_varianti=rv, correlazione_ablazione=ra,
            primo_posto_rete_su_oracolo=j0, rango_cella_contatto=rango, contrasto_contatto=cc, contrasto_distanza2_descrittivo=c2,
            correlazione_posti_descrittivo=spearman([s['dt_j%d' % b].p for b in range(7)], [so['dt_j%d' % b].p for b in range(7)]),
            vicino_rete=s['vicino'].d(), vicino_oracolo=so['vicino'].d(),
            R2_albero16=(RG.get('pianta1') or {}).get('albero', {}).get(16).d() if RG.get('pianta1') else None, soffitto=(RG.get('pianta1') or {}).get('soffitto'),
            superato=bool(ok))
    # sensibilita': la rete vede una regola a distanza 2? (non e' una condizione: dice che cosa la rete puo' vedere)
    if 'pianta3' in S:
        aux = AUX.get('pianta3') or {}
        c2 = aux.get('contrasto_dist2')
        so = riassunto(TT['pianta3'], oracolo=True) if TT['pianta3'].orac else None
        vista = bool(c2 is not None and c2['differenza'].ic()[0] >= CONTRASTO_DIST2)
        c['sensibilita_distanza2'] = OrderedDict(
            perdita_rete=S['pianta3']['dt'].d(), perdita_oracolo=so['dt'].d() if so else None, contrasto_distanza2=c2,
            vicino_rete=S['pianta3']['vicino'].d(), vicino_oracolo=so['vicino'].d() if so else None,
            esito='la rete vede la regola a distanza 2' if vista else 'la rete NON vede la regola a distanza 2 (limite di sensibilita)')
    if 'pianta2' in S:
        t = TT['pianta2']
        s = S['pianta2']
        so = riassunto(t, oracolo=True) if t.orac else None
        c['piantato_debole_descrittivo'] = OrderedDict(
            perdita_rete=s['dt'].d(), perdita_oracolo=so['dt'].d() if so else None, rango=(AUX.get('pianta2') or {}).get('rango'),
            contrasto_contatto=(AUX.get('pianta2') or {}).get('contrasto_contatto'),
            R2_albero16=(RG.get('pianta2') or {}).get('albero', {}).get(16).d() if RG.get('pianta2') else None)
    for k in ('negativo_senza_ordine', 'positivo_piantato'):
        c['valido_' + k] = bool(c.get(k, {}).get('superato', False))
    return c


def etichette_letture(S, RG, V21):
    """Le letture preregistrate per ogni testo vero (vere, libri v21, lingue)."""
    L = OrderedDict()
    for nome, s in S.items():
        if nome in ('pianta1', 'pianta2', 'pianta3', 'senzaord') or '~' in nome:
            continue
        x = OrderedDict()
        x['posto_nella_riga'] = OrderedDict(prima=etichetta_rapporto(s['R_prima'], BORDO_SI, BORDO_NO), ultima=etichetta_rapporto(s['R_ultima'], BORDO_SI, BORDO_NO))
        x['dentro_la_parola'] = OrderedDict(inizio=lettura_quota(s['quota_primo'], QUOTA_PEZZO_SI, QUOTA_PEZZO_NO),
                                            quote={k: s['quota_' + k].p for k in ('primo', 'interno', 'ultimo', 'spazio')})
        x['vicino_lontano'] = OrderedDict(esito=lettura_vicino(s['vicino']), vicino=s['vicino'].p, R_lont=s['R_lont'].p)
        x['pezzi'] = OrderedDict((p, lettura_pezzo(s['Q_' + p])) for p in VP.PEZZI if p != 'nessuno')
        r = RG.get(nome)
        if r:
            best = r['famiglie'][r['migliore_famiglia']]['R2']
            x['regole'] = OrderedDict(albero16=lettura_r2(r['albero'][16]), migliore_famiglia=r['migliore_famiglia'], migliore=lettura_r2(best))
        L[nome] = x
    return L


def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((str(k), pulisci(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, V):
        return pulisci(x.d())
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def analisi(corse, versioni):
    nomi = [n for n in nomi_testi() if any(r['job'][1] == n for r in corse)]
    if not nomi:
        raise SystemExit('FERMO: nessun lavoro di rete da analizzare')
    TT = OrderedDict((n, Testo(n, corse)) for n in nomi)
    S = OrderedDict((n, riassunto(t)) for n, t in TT.items())
    RG, AUX = OrderedDict(), OrderedDict()
    for n, t in TT.items():
        meta = None
        if n in ('pianta1', 'pianta2', 'pianta3'):
            try:
                meta = costruisci(n)['meta']
            except Exception as ex:                              # noqa: BLE001
                print('meta non disponibile per %s: %s' % (n, ex), flush=True)
        seme_n = sorted({r['job'][2] for r in corse if r['job'][1] == n})
        r, a = regole_testo(n, seme_n, meta)
        if r:
            RG[n] = r
        if a:
            AUX[n] = a
    out = OrderedDict(versioni=versioni, esperimento='ia13', pagine={n: t.P for n, t in TT.items()},
                      completi={n: t.completo for n, t in TT.items()})
    out['testi'] = OrderedDict((n, OrderedDict(riassunto=S[n], regole=RG.get(n))) for n in TT)
    out['oracolo'] = OrderedDict((n, riassunto(t, oracolo=True)) for n, t in TT.items() if t.orac)
    out['controlli'] = controlli(TT, RG, AUX, S)
    out['letture'] = etichette_letture(S, RG, None)
    out['v21_contro_vere'] = confronto_v21(TT)
    out['riproduzione_ia09'] = riproduzione_ia09(TT['vere']) if 'vere' in TT else None
    out['varianti'] = OrderedDict((v, VP.VARIANTI[v][1]) for v in VARIANTI)
    out['pezzi'] = VP.NOMI_PEZZI
    out['info_reti'] = OrderedDict((n, OrderedDict(
        passi_medi=float(np.mean([i['passi'] for i in t.info])), perdita_validazione=float(np.mean([i['bpc_validazione'] for i in t.info])),
        obiettivi=float(np.mean([i['obiettivi'] for i in t.info])), ricambi_senza_pezzo=float(np.mean([i['ricambi_senza_pezzo'] for i in t.info])),
        tempo_medio_s=float(np.mean([sum(i.get('tempi_s', {'x': 0}).values()) for i in t.info])))) for n, t in TT.items())
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulisci(out), f, ensure_ascii=False, indent=1)
        f.write('\n')
    scrivi_md(pulisci(out), TT)
    print('analisi scritta: %s' % os.path.join(USCITA, NOME + '.md'), flush=True)
    return out


# ---------------------------------------------------------------- scrittura del .md

def tabella(titolo, nomi, colonne, S, nota=None):
    """Una tabella: una riga per testo, una colonna per misura (etichetta, chiave)."""
    r = ['', '## %s' % titolo, '']
    if nota:
        r += [nota, '']
    r += ['| testo | ' + ' | '.join(c[0] for c in colonne) + ' |', '|---' * (len(colonne) + 1) + '|']
    for n in nomi:
        if n in S:
            r.append('| %s | %s |' % (n, ' | '.join(vv(S[n].get(k)) if isinstance(S[n].get(k), dict) else '-' for _, k in colonne)))
    return r


def scrivi_md(o, TT):
    S = OrderedDict((n, x['riassunto']) for n, x in o['testi'].items())
    reali = [n for n in S if n not in ('pianta1', 'pianta2', 'pianta3', 'senzaord') and '~' not in n]
    ctrl = [n for n in S if n not in reali]
    r = ['# ia13 — che cosa vede la rete', '',
         'Soglie nella preregistrazione `preregistrazioni/ia13.md`. "Perdita" = bit in piu\' per parola che la rete GRU paga quando il contesto della riga e\' '
         'rimescolato (la stessa parola, prima e dopo); intervalli al 95% col bootstrap sulle pagine. Nessuna parola della trascrizione: i glifi sono '
         'codici anonimi (#1 = il piu\' frequente).', '']
    r += ['## Letture', '']
    for n, x in o['letture'].items():
        g = x.get('regole')
        r.append('- %s: prima parola della riga %s, ultima %s; inizio di parola %s; contesto: **%s** (parola prima / tutta la riga = %s; oltre la prima / sulla prima %s); '
                 'pezzi %s; regole %s' % (
                     n, x['posto_nella_riga']['prima'], x['posto_nella_riga']['ultima'], x['dentro_la_parola']['inizio'], x['vicino_lontano']['esito'],
                     f2(x['vicino_lontano']['vicino']), f2(x['vicino_lontano']['R_lont']),
                     ', '.join('%s %s' % (k, v) for k, v in x['pezzi'].items()),
                     ('albero a 16 foglie: %s; migliore tabella (%s): %s' % (g['albero16'], g['migliore_famiglia'], g['migliore'])) if g else 'n.d.'))
    r += ['', '## Controlli', '']
    for k, v in o['controlli'].items():
        r.append('- %s: %s' % (k, json.dumps(v, ensure_ascii=False)))
    pos = [('prima', 'dt_j0'), ('2a', 'dt_j1'), ('3a', 'dt_j2'), ('4a', 'dt_j3'), ('5a', 'dt_j4'), ('6a', 'dt_j5'), ('7a o oltre', 'dt_j6')]
    r += tabella('Dove, nella riga (bit per parola persi, tutte le parole rimescolate, solo i glifi; posto = posto della riga, prima e dopo)', reali + ctrl,
                 [('tutte (con lo spazio)', 'dt'), ('tutte, solo glifi', 'dtg')] + pos + [('ultimo posto', 'dt_e0'), ('penultimo', 'dt_e1'), ('primo / dal 3o in poi', 'R_prima'), ('ultimo / prima dell\'ultimo-1', 'R_ultima')], S)
    r += tabella('Bordi della riga, per pezzo della parola (bit per parola)', reali + ctrl,
                 [('primo posto, ' + n_, 'pc_j0_' + k_) for n_, k_ in zip(NOMI_PEZZO_PAROLA, ('primo', 'interno', 'ultimo', 'spazio'))] +
                 [('ultimo posto, ' + n_, 'pc_e0_' + k_) for n_, k_ in zip(NOMI_PEZZO_PAROLA, ('primo', 'interno', 'ultimo', 'spazio'))], S)
    r += tabella('Dove, nella parola (quota della perdita per pezzo della parola)', reali + ctrl,
                 [(NOMI_PEZZO_PAROLA[0], 'quota_primo'), (NOMI_PEZZO_PAROLA[1], 'quota_interno'), (NOMI_PEZZO_PAROLA[2], 'quota_ultimo'), (NOMI_PEZZO_PAROLA[3], 'quota_spazio')], S)
    r += tabella('Quanto contesto e\' rimasto (rimescolamento completo: bit persi per parola, solo glifi, per categoria)', reali + ctrl,
                 [(VP.NOMI_CAT[k], 'cat_%d' % k) for k in range(VP.NCAT)], S)
    r += ['', '## I tredici rimescolamenti', '']
    for v in VARIANTI:
        r.append('- `%s`: %s' % (v, VP.VARIANTI[v][1]))
    r += tabella('Rimescolamenti, perdita (bit per parola)', reali + ctrl, [(v, 'dv_' + v) for v in VARIANTI], S)
    r += tabella('Rimescolamenti, quota di parole con la parola prima cambiata o spostata a inizio riga', reali + ctrl, [(v, 'rotte_' + v) for v in VARIANTI], S)
    r += tabella('Vicino o lontano nei rimescolamenti parziali (parole con la parola prima uguale e il contesto piu\' lontano cambiato / parole con la parola prima cambiata)',
                 reali + ctrl, [('perdita con parola prima uguale', 'parz_lont'), ('perdita con parola prima cambiata', 'parz_vic'), ('rapporto', 'R_lont')], S)
    r += ['', '## Ablazione: bit persi per parola scelta (dal terzo posto della riga) se si cambia il contesto prima', '']
    for pz, sp in VP.NOMI_PEZZI.items():
        r.append('- pezzo `%s`: %s' % (pz, sp))
    r.append('- `ordine`: le stesse parole rimescolate; `prec_via`: tolta la parola prima; `p_X`: solo la parola prima e\' sostituita da una con il pezzo X; `r_X`: tutte le parole prima.')
    r += tabella('Ablazione, perdita per parola', reali + ctrl, [(c, 'A_' + c) for c in COND if c != 'orig'], S)
    r += tabella('Quota dell\'utilita\' della parola prima che resta quando alla rete si lascia solo un pezzo (1 = tutta; 0 = niente)', reali + ctrl,
                 [(p, 'Q_' + p) for p in VP.PEZZI if p != 'nessuno'], S)
    r += tabella('Idem, per tutte le parole della riga', reali + ctrl, [(p, 'QR_' + p) for p in VP.PEZZI if p != 'nessuno'], S)
    r += tabella('Parola prima contro tutta la riga; quota dovuta all\'ordine', reali + ctrl, [('parola prima / riga', 'vicino'), ('ordine / contenuto', 'qord')], S)
    if o['oracolo']:
        r += ['', '## Oracolo (perdita di una rete perfetta, solo testi sintetici)', '']
        S_o = OrderedDict((n, x) for n, x in o['oracolo'].items())
        r += tabella('Oracolo, perdita per parola e per posto', list(S_o), [('tutte', 'dt')] + pos, S_o)
        r += tabella('Oracolo, rimescolamenti', list(S_o), [(v, 'dv_' + v) for v in VARIANTI], S_o)
        r += tabella('Oracolo, ablazione', list(S_o), [(c, 'A_' + c) for c in COND if c != 'orig'], S_o)
    r += ['', '## Regole leggibili (R2 fuori campione = quota della variazione della perdita da parola a parola che la regola spiega su pagine mai viste)', '']
    for n, x in o['testi'].items():
        g = x.get('regole')
        if not g:
            continue
        r += ['', '### %s' % n, '', '%d parole, perdita media %.3f, soffitto di prevedibilita\' %s (quota della variazione che non e\' rumore del rimescolamento)' % (
            g['righe'], g['delta_medio'], f2(g['soffitto'])), '']
        r += ['| famiglia di pezzi | celle | R2 | R2 con le 10 celle migliori | 30 | 100 |', '|---|---|---|---|---|---|']
        for k, fm in g['famiglie'].items():
            r.append('| %s | %d | %s | %s | %s | %s |' % (k, fm['celle'], vv(fm['R2']), vv(fm.get('R2_top10')) if fm.get('R2_top10') else '-',
                                                          vv(fm.get('R2_top30')) if fm.get('R2_top30') else '-', vv(fm.get('R2_top100')) if fm.get('R2_top100') else '-'))
        r += ['', 'Albero (R2 per numero di foglie): ' + ', '.join('%s: %s' % (k, vv(v)) for k, v in g['albero'].items()),
              'Domande principali dell\'albero a 8 foglie: ' + '; '.join(g['domande_principali'])]
        for k in FAMIGLIE_TOP:
            celle = g['famiglie'][k].get('celle_top') or []
            r += ['', 'Celle principali, %s (codici: i pezzi sono glifi anonimi):' % k, '']
            for c in celle[:10]:
                r.append('- %s: %d parole, perdita media %s, contributo %+.1f (%.1f%% del contributo assoluto)' % (c['chiave'], c['parole'], f2(c['delta_medio']), c['contributo'], 100 * c['quota']))
        r += ['', 'Albero a 8 foglie (codici anonimi):', '', '```'] + g['albero8_codici'] + ['```']
    v = o['v21_contro_vere']
    if v:
        r += ['', '## v21 contro vere (media dei libri meno vere)', '', '(%d pagine; libri %s)' % (v['_pagine'], ', '.join(v['_libri'])), '',
              '| misura | vere | v21 | differenza | nullo 97,5% | esito |', '|---|---|---|---|---|---|']
        for k, x in v.items():
            if isinstance(x, dict):
                r.append('| %s | %s | %s | %s | %.3f | %s |' % (k, vv(x['vere']), vv(x['v21']), vv(x['differenza']), x['nullo97'], x['esito']))
    r += ['', '## Riproduzione di ia09 e reti', '', '- riproduzione di ia09 (rimescolamento completo, stesso seme): %s' % json.dumps(o['riproduzione_ia09'], ensure_ascii=False)]
    for n, x in o['info_reti'].items():
        r.append('- %s: passi medi %.0f, perdita di validazione %.3f, obiettivi dell\'ablazione %.0f, ricambi senza pezzo %.4f, tempo medio per lavoro %.0f s' % (
            n, x['passi_medi'], x['perdita_validazione'], x['obiettivi'], x['ricambi_senza_pezzo'], x['tempo_medio_s']))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return r


def main():
    import torch
    import numpy
    import scipy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'rete,analisi').split(',')
    c = G.contesto()
    print('pagine vere: %d; pieghe %d; semi %s; libri v21 %s' % (len(c['ids']), NF, SEMI, LIBRI13), flush=True)
    os.makedirs(G.LIBRI, exist_ok=True)
    mancano = [n for n in LIBRI13 if int(n[1:]) in G.CHIAVI and not os.path.exists(G.percorso_libro(n))]
    if mancano and SOLO_CONTROLLI:
        for n in mancano:
            G.genera_libro(n)
        mancano = []
    if mancano:
        raise SystemExit('FERMO: mancano i libri %s in %s (li genera ia01)' % (', '.join(mancano), G.LIBRI))
    percorso = os.path.join(USCITA, 'ia13_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = carica_corse(percorso)
    elif 'rete' in fasi:
        open(percorso, 'w').close()
    if 'rete' in fasi:
        fatte = {json.dumps(x['job']) for x in corse}
        L = lavori(['rete'])
        da_fare = [j for j in L if json.dumps(list(j)) not in fatte]
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
