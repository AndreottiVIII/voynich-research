# -*- coding: utf-8 -*-
"""Supporto di ia30 (modulo, non e' un esperimento): il motore degli interventi dentro un imitatore gia' addestrato.

Che cosa c'e' qui, in parole semplici
- Un "lettore" (`Lettore`) tiene un imitatore addestrato (M1 o M5 di ia20, E2 di ia22) e la sua "penna" (la rete che si fa avanzare un segno
  alla volta). Si puo' fare una FOTO dello stato della penna (stati delle due GRU, memoria della riga, parole gia' lette) e RIPRENDERLO dopo.
- Un INTERVENTO e' una piccola modifica a cio' che la rete "ha letto" prima di un punto: le ultime lettere della parola prima, la riga sopra
  rimescolata o presa altrove, la fascia di lunghezza della riga, un segno di riempimento. Da una foto prima della modifica si fanno leggere alla
  rete i segni modificati (ecco lo stato "donatore": quello calcolato su un contesto identico tranne per un dettaglio) e poi, da li', le parole vere
  che seguono. Si misura quanto cambia la previsione di ogni parola rispetto alla lettura senza intervento.
- Lo SCAMBIO DI STATI: lo stato donatore (o una parte: il solo secondo strato, il solo primo, le k dimensioni piu' importanti, k dimensioni a caso)
  viene messo al posto dello stato vero nel punto d'inizio parola; poi si leggono le stesse parole vere. Il rapporto fra l'effetto dello scambio
  parziale e quello totale dice DOVE la rete tiene l'informazione.
- Le uscite sono solo numeri (somme per pagina di cambi di probabilita'): nessuna parola del manoscritto compare qui.
La logica di lettura copia la miscela del puntatore di ia20/ia22 (`mix`), senza modificare nessun modulo esistente.
"""
import math
import os
import random
import sys
import zlib
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import echi_fase0 as F0  # noqa: E402

# ---------------------------------------------------------------- costanti (fissate nella preregistrazione)

K_PAROLE = 6                     # parole lette dopo il punto d'intervento (interventi sulla parola prima)
K_RIGA = 40                      # parole lette dopo il punto d'intervento (inizio riga: si legge tutta la riga, fine riga compreso)
NOMI_PAROLA = ('nul', 'u1', 'u2', 'p2', 'p3', 'pm', 'p1', 'pw', 'w2', 'rc', 'fill')          # punto = parola (non prima) della riga
NOMI_RIGA = ('lnul', 'rs_m', 'rs_p', 'rs_a', 'rl', 'hN', 'hT', 'hR', 'lfill')    # punto = inizio riga (dopo la testa)
NOMI_TESTA_PAGINA = ('hS', 'hL', 'hM')                                              # punto = inizio pagina
NOMI_PATCH = ('u2', 'pw', 'rs_a')                                                   # interventi per i quali si fa anche lo scambio parziale di stati
KS_DIM = (1, 2, 4, 8, 16, 32, 64, 128)
VARIANTI_PATCH = ['tutto', 'y2', 'y1'] + ['top%d' % k for k in KS_DIM] + ['rnd%d' % k for k in KS_DIM]
CLASSI = ('altra', 'eco_riga', 'eco_sopra')                                          # classe di una parola vera (dal testo vero)
CAMPI = ('kl', 'dlpw', 'dlpm', 'dpc', 'dterm')
MARGINE_KV = 1500                                                                    # righe della memoria di attenzione da salvare (M5)
LEN_MIN_PREC = 3                                                                     # la parola prima deve avere almeno 3 glifi
MINIME = ('u1', 'u2', 'p2', 'p3', 'pm', 'p1')                                        # interventi con coppia minima di parole vere


# ---------------------------------------------------------------- numeri

def lsm(lg):
    a = np.asarray(lg, dtype=np.float64)
    a = a - a.max()
    return a - math.log(float(np.exp(a).sum()))


def kl_bit(lp_o, lp_m):
    """KL(o || m) in bit fra due log-probabilita' (naturali) di una stessa distribuzione."""
    p = np.exp(lp_o)
    return float((p * (lp_o - lp_m)).sum() / math.log(2))


# ---------------------------------------------------------------- struttura di una pagina

def struttura(tok, ctx):
    """Righe di una pagina: lista di dict(h = posizione del primo segno di testa (T), w0 = prima parola, parole = [(s, e)], eol = posizione del fine riga).
    s = primo glifo, e = posizione del terminatore (spazio o fine riga)."""
    tk = [int(x) for x in tok]
    parole = GM.parole_di_tok(np.asarray(tok), ctx)
    hs = [i for i, x in enumerate(tk) if x in ctx.Tset]
    out = []
    for r, h in enumerate(hs):
        fine = hs[r + 1] if r + 1 < len(hs) else len(tk) + 1
        w = [(s, e) for (s, e) in parole if h + 3 <= s < fine]
        out.append(dict(h=h, w0=h + 3, parole=w, eol=(w[-1][1] if w else None)))
    return out


def unita_parola(tok, s, e, u0):
    return tuple(int(tok[x]) - u0 for x in range(s, e))


def classi_parole(tok, righe, ctx, S=F0.S_CAND):
    """Per ogni parola (r, i): 0 'altra', 1 'eco_riga' (uguale o a una modifica da una parola candidata della riga in corso, la piu' vicina vince),
    2 'eco_sopra' (la piu' vicina e' della riga sopra). Candidati come nei modelli: ultime S parole della riga in corso, poi quelle della riga sopra."""
    u0 = ctx.u0
    parole = [[unita_parola(tok, s, e, u0) for (s, e) in L['parole']] for L in righe]
    out = {}
    for r, ws in enumerate(parole):
        sopra = parole[r - 1][::-1] if r > 0 else []
        for i, w in enumerate(ws):
            cur = ws[:i][::-1]
            cand = (cur + sopra)[:S]
            cl = 0
            for rango, c in enumerate(cand):
                if c == w or F0.una_modifica(c, w) is not None:
                    cl = 1 if rango < len(cur[:S]) else 2
                    break
            out[(r, i)] = cl
    return out, parole


# ---------------------------------------------------------------- foto della penna

def foto(pen):
    """Copia dello stato della penna (le GRU sono tensori che non si cambiano in loco: bastano i riferimenti)."""
    f = dict(h1=pen.h1, h2=pen.h2, hd=pen.hd, n=pen.n, linea=pen.linea, inizi=dict(pen.inizi), nlin=len(pen.lin), somma=pen.somma.copy(),
             ncomp=pen.ncomp, w=pen.w, sofar=pen.sofar, bin=pen.bin, corrente=list(pen.corrente),
             rp={k: list(v) for k, v in pen.righe_parole.items() if k >= pen.linea - 1})
    if hasattr(pen, 'lg_ultimo'):
        f['lg'] = pen.lg_ultimo
    return f


def ripristina(pen, f):
    pen.h1, pen.h2, pen.hd = f['h1'], f['h2'], f['hd']
    pen.n, pen.linea, pen.w, pen.sofar, pen.bin, pen.ncomp = f['n'], f['linea'], f['w'], f['sofar'], f['bin'], f['ncomp']
    pen.inizi = dict(f['inizi'])
    del pen.lin[f['nlin']:]
    pen.somma = f['somma'].copy()
    pen.corrente = list(f['corrente'])
    pen.righe_parole = {k: list(v) for k, v in f['rp'].items()}
    if 'lg' in f:
        pen.lg_ultimo = f['lg']


# ---------------------------------------------------------------- donatori

class Donatori:
    """Parole e righe di pagine date (le pagine di addestramento della piega): fonte dei glifi e delle righe che si mettono al posto di quelli veri.
    Le sostituzioni sulla parola prima sono COPPIE MINIME DI PAROLE VERE: la parola percepita e' una parola del lessico che differisce dalla vera solo nel posto
    toccato (ultimo glifo, ultimi due, penultimo, primo), cosi' la rete non legge parole che non esistono (un contesto "rotto" disturba la rete in modo generico e
    non e' un'informazione cambiata)."""

    def __init__(self, pagine, ctx):
        self.parole, self.righe, self.per_lung = [], [], {}
        u0 = ctx.u0
        for d in pagine:
            tok = d['tok']
            for L in struttura(tok, ctx):
                ws = [unita_parola(tok, s, e, u0) for (s, e) in L['parole']]
                if ws:
                    self.righe.append((d['nome'], tuple(ws)))
                for w in ws:
                    if len(w) >= LEN_MIN_PREC:
                        self.parole.append(w)
        for w in self.parole:
            self.per_lung.setdefault(len(w), []).append(w)
        # indice delle coppie minime: per posto, chiave = la parola senza i glifi toccati
        conti = {}
        for w in self.parole:
            conti[w] = conti.get(w, 0) + 1
        self.minime = {'u1': {}, 'u2': {}, 'p2': {}, 'p3': {}, 'pm': {}, 'p1': {}}
        for w, c in conti.items():
            n = len(w)
            self.minime['u1'].setdefault(w[:-1], []).append((w, c))
            self.minime['u2'].setdefault(w[:-2], []).append((w, c))
            self.minime['p2'].setdefault(w[:-2] + w[-1:], []).append((w, c))
            self.minime['p1'].setdefault(w[1:], []).append((w, c))
            if n >= 4:
                self.minime['p3'].setdefault(w[:-3] + w[-2:], []).append((w, c))
            if n >= 5:
                m = n // 2
                self.minime['pm'].setdefault(w[:m] + w[m + 1:], []).append((w, c))

    def coppia_minima(self, nome, p, rng):
        """Una parola vera uguale a `p` tranne che nel posto di `nome` (scelta in proporzione alla frequenza), o None."""
        if (nome == 'p3' and len(p) < 4) or (nome == 'pm' and len(p) < 5):
            return None
        m = len(p) // 2
        chiave = {'u1': p[:-1], 'u2': p[:-2], 'p2': p[:-2] + p[-1:], 'p1': p[1:], 'p3': p[:-3] + p[-2:], 'pm': p[:m] + p[m + 1:]}[nome]
        lst = [(w, c) for (w, c) in self.minime[nome].get(chiave, []) if w != p]
        if not lst:
            return None
        return rng.choices([w for w, _ in lst], weights=[c for _, c in lst])[0]

    def parola(self, rng):
        return rng.choice(self.parole)

    def parola_lung(self, n, rng):
        lst = self.per_lung.get(n) or [w for w in self.parole if abs(len(w) - n) <= 1]
        return rng.choice(lst) if lst else None

    def riga_altrove(self, nome_pagina, n_parole, rng):
        """Una riga di un'altra pagina, con lo stesso numero di parole se c'e' (altrimenti la piu' vicina)."""
        lst = [w for (p, w) in self.righe if p != nome_pagina and len(w) == n_parole]
        if not lst:
            lst = [w for (p, w) in self.righe if p != nome_pagina]
            lst.sort(key=lambda w: abs(len(w) - n_parole))
            lst = lst[:50]
        return rng.choice(lst)


# ---------------------------------------------------------------- gli interventi: regioni percepite

def modifica_parola(nome, p, don, rng):
    """La parola prima `p` (tuple di indici di glifo) come la "vede" la rete: una parola VERA che differisce da `p` solo nel posto dell'intervento (coppia minima), o,
    per `pw`, una parola vera della stessa lunghezza. None se l'intervento non si puo' fare (nessuna coppia minima) o non cambia niente."""
    n = len(p)
    if nome == 'nul':
        return p
    if n < LEN_MIN_PREC:
        return None
    if nome == 'pw':
        for _ in range(12):
            d = don.parola_lung(n, rng)
            if d is not None and d != p and len(d) == n:
                return d
        return None
    if nome in MINIME:
        return don.coppia_minima(nome, p, rng)
    raise ValueError(nome)


def _tok_parole(parole, ctx, finale):
    """Segni di una riga fatta delle `parole` (tuple di glifi), separate da spazio e chiusa da `finale`."""
    out = []
    for k, w in enumerate(parole):
        if k:
            out.append(ctx.SP)
        out += [ctx.u0 + int(x) for x in w]
    out.append(finale)
    return out


def regione(nome, ctx, voc, tok, righe, parole, r, i, don, rng, nome_pagina):
    """L'intervento `nome` nel punto (riga r, parola i): (start, tokens, s_cur) con
    start = posizione da cui rileggere (foto prima), tokens = segni percepiti da `start` fino a `s_cur` escluso, s_cur = inizio della parola del punto.
    None se non applicabile. `parole`: parole vere (tuple) di ogni riga."""
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    tk = [int(x) for x in tok]
    L = righe[r]
    ws = L['parole']
    s_cur = ws[i][0] if i < len(ws) else None
    idx = voc['idx']
    if nome in NOMI_PAROLA:
        if i < 1:
            return None
        sp, ep = ws[i - 1]
        if nome == 'nul':
            return sp, tk[sp:s_cur], s_cur
        if nome == 'fill':
            return s_cur, [0], s_cur
        if nome in MINIME or nome == 'pw':
            q = modifica_parola(nome, parole[r][i - 1], don, rng)
            if q is None:
                return None
            return sp, [u0 + x for x in q] + [tk[ep]], s_cur
        if nome == 'w2':
            if i < 2 or len(parole[r][i - 2]) < LEN_MIN_PREC:
                return None
            s2, e2 = ws[i - 2]
            q = modifica_parola('pw', parole[r][i - 2], don, rng)
            if q is None:
                return None
            return s2, [u0 + x for x in q] + [tk[e2]] + tk[ws[i - 1][0]:s_cur], s_cur
        if nome == 'rc':
            if i < 3:
                return None
            prima = list(parole[r][:i - 1])
            if len(set(prima)) < 2:
                return None
            for _ in range(12):
                rng.shuffle(prima)
                if tuple(prima) != tuple(parole[r][:i - 1]):
                    break
            else:
                return None
            toks = []
            for w in prima:
                toks += [u0 + int(x) for x in w] + [SP]
            return ws[0][0], toks + tk[sp:s_cur], s_cur
    if nome in NOMI_RIGA:
        if i != 0:
            return None
        h = L['h']
        if nome == 'lnul':
            return h, tk[h:h + 3], s_cur
        if nome == 'lfill':
            return s_cur, [0], s_cur
        if nome in ('hN', 'hT', 'hR'):
            q = {'hN': (2, 'N:%d', 8), 'hR': (1, 'R:%d', 10)}.get(nome)
            kk = list(tk[h:h + 3])
            if nome == 'hT':
                alt = [t for t in sorted(ctx.Tset) if t != kk[0]]
                kk[0] = rng.choice(alt)
            else:
                pos, fmt, n = q
                alt = [idx[fmt % b] for b in range(n) if idx[fmt % b] != kk[pos]]
                kk[pos] = rng.choice(alt)
            return h, kk, s_cur
        if nome in ('rs_m', 'rs_p', 'rs_a'):
            if r < 1 or not parole[r - 1]:
                return None
            sopra = list(parole[r - 1])
            if nome == 'rs_m':
                if len(set(sopra)) < 2:
                    return None
                for _ in range(12):
                    rng.shuffle(sopra)
                    if tuple(sopra) != tuple(parole[r - 1]):
                        break
                else:
                    return None
                nuova = sopra
            elif nome == 'rs_p':
                lont = [q for q in range(len(righe)) if abs(q - (r - 1)) >= 3 and parole[q]]
                if not lont:
                    return None
                nuova = list(parole[rng.choice(lont)])
            else:
                nuova = list(don.riga_altrove(nome_pagina, len(sopra), rng))
            return righe[r - 1]['w0'], _tok_parole(nuova, ctx, EOL) + tk[h:s_cur], s_cur
        if nome == 'rl':
            if r < 3 or not parole[r - 3]:
                return None
            nuova = list(don.riga_altrove(nome_pagina, len(parole[r - 3]), rng))
            return righe[r - 3]['w0'], _tok_parole(nuova, ctx, EOL) + tk[righe[r - 3]['eol'] + 1:s_cur], s_cur
    raise ValueError(nome)


# ---------------------------------------------------------------- il lettore

class Lettore:
    """Un imitatore addestrato con la sua penna. `tipo`: 'M1', 'M5' o 'E2'."""

    def __init__(self, m, ctx, voc, tipo, capacita):
        self.m, self.ctx, self.voc, self.tipo = m, ctx, voc, tipo
        self.punt = tipo in ('M5', 'E2')
        self.pen = EM.Penna22(m, ctx, capacita) if tipo[0] == 'E' else GM.Penna20(m, ctx, capacita)
        self.tab = self.pen.tabelle_ritocco() if self.punt else None
        self.pen.apri()

    # ---- avanzare
    def nuova(self):
        self.pen.apri()

    def alimenta(self, tokens):
        lg = None
        for t in tokens:
            lg = self.pen.dai(int(t))
        return lg

    # ---- miscela del puntatore (come la perdita di ia20/ia22, per una parola)
    def mix(self, cand, pf, ppi, w, lpw, lg_fine, tok_term):
        ctx = self.ctx
        psub, pins = self.tab
        U = ctx.U
        A = 0.0
        for k, (c, _) in enumerate(cand):
            for (tp, cx, x, n) in GM.scripts(c, w, U):
                if tp == 0:
                    pr = 1.0
                elif tp == 1:
                    pr = float(psub[min(cx, U - 1), min(x, U - 1)]) / n
                elif tp == 2:
                    pr = float(pins[cx, min(x, U - 1)]) / n
                else:
                    pr = 1.0 / n
                A += float(ppi[k, tp]) * pr
        a = np.array([lg_fine[ctx.SP], lg_fine[ctx.EOL]], dtype=np.float64)
        a = a - a.max()
        r = math.exp(a[0 if tok_term == ctx.SP else 1]) / float(np.exp(a).sum())
        P = pf * math.exp(lpw) + A * r
        return math.log(max(P, 1e-300))

    def continua(self, tok, righe, r, i0, lg, K=K_PAROLE, mask_puntatore=None):
        """Dalla parola i0 della riga r (la penna e' a inizio parola, `lg` = logit del primo glifo) legge le parole vere fino a K parole o fino alla fine
        della riga (il fine riga compreso). -> lista di dict per parola: lp1 (log-probabilita' del primo glifo, tutti i segni), lpw (parola e terminatore,
        solo GRU), lpm (miscela col puntatore, se c'e'), pf (probabilita' di libero, nan senza puntatore), lpt (terminatore), eol (era l'ultima parola)."""
        ctx, pen = self.ctx, self.pen
        SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
        ws = righe[r]['parole']
        out = []
        for i in range(i0, min(len(ws), i0 + K)):
            s, e = ws[i]
            l1 = lsm(lg)
            pf, cand, ppi = float('nan'), None, None
            if self.punt:
                cand = pen.candidati()
                if cand:
                    pf, ppi = pen.puntatore(cand)
                    if mask_puntatore is not None:
                        pf, ppi = mask_puntatore(pf, ppi, len(cand))
                else:
                    pf = 1.0
            lpw, ll = 0.0, l1
            for t in range(s, e):
                lpw += ll[int(tok[t])]
                lg = pen.dai(int(tok[t]))
                ll = lsm(lg)
            lpt = float(ll[int(tok[e])])
            lpw += lpt
            lpm = lpw
            if self.punt and cand:
                w = unita_parola(tok, s, e, u0)
                lpm = self.mix(cand, pf, ppi, w, lpw, lg, int(tok[e]))
            out.append(dict(lp1=l1, lpw=lpw, lpm=lpm, pf=pf, lpt=lpt, eol=int(tok[e]) == EOL))
            lg = pen.dai(int(tok[e]))
        return out

    # ---- salvare/ripristinare anche la memoria di attenzione (M5): le righe sopra la foto si sovrascrivono
    def perturba(self, f, fn):
        pen = self.pen
        if pen.passo >= 2:
            a = f['n']
            b = min(a + MARGINE_KV, pen.K.shape[0])
            sK, sV = pen.K[a:b].clone(), pen.Vv[a:b].clone()
        try:
            return fn()
        finally:
            if pen.passo >= 2:
                pen.K[a:b] = sK
                pen.Vv[a:b] = sV

    # ---- stati
    def stato_patchato(self, f, don, quali, dims=None):
        """La foto `f` (stato vero) con parte dello stato preso dal donatore `don` (foto): quali = 'tutto', 'y2', 'y1' o 'dims' (le dimensioni
        `dims` del secondo strato). Rimette la penna in questo stato e restituisce i logit del primo glifo (output del secondo strato)."""
        import torch
        pen = self.pen
        ripristina(pen, f)
        with torch.inference_mode():
            if quali == 'tutto':
                h1, h2 = don['h1'], don['h2']
            elif quali == 'y2':
                h1, h2 = f['h1'], don['h2']
            elif quali == 'y1':
                h1, h2 = don['h1'], f['h2']
            else:
                msk = torch.zeros(1, 1, f['h2'].shape[-1], dtype=torch.bool)
                msk[..., list(dims)] = True
                h1, h2 = f['h1'], torch.where(msk, don['h2'], f['h2'])
            pen.h1, pen.h2 = h1, h2
            pen.hd = h2[0, 0]
            lg = self.m.out(pen.hd).tolist()
        if hasattr(pen, 'lg_ultimo'):
            pen.lg_ultimo = lg
        return lg


# ---------------------------------------------------------------- accumulo per pagina

def nuovo_acc(K):
    return dict(S=np.zeros((len(CLASSI), K, len(CAMPI))), N=np.zeros((len(CLASSI), K)), U=np.zeros(3))


def somma_diff(acc, rO, rM, classi_k):
    """Aggiunge a `acc` le differenze fra la lettura con intervento (rM) e senza (rO) per le parole lette; classi_k: classe di ogni parola."""
    for k, (o, m) in enumerate(zip(rO, rM)):
        c = classi_k[k]
        acc['N'][c, k] += 1
        S = acc['S'][c, k]
        S[0] += kl_bit(o['lp1'], m['lp1'])
        S[1] += (m['lpw'] - o['lpw']) / math.log(2)
        S[2] += (m['lpm'] - o['lpm']) / math.log(2)
        S[3] += (0.0 if o['pf'] != o['pf'] else ((1.0 - m['pf']) - (1.0 - o['pf'])))
        S[4] += (m['lpt'] - o['lpt']) / math.log(2)
        if o['eol']:
            acc['U'][0] += 1
            acc['U'][1] += (m['lpt'] - o['lpt']) / math.log(2)
            acc['U'][2] += (m['lpm'] - o['lpm']) / math.log(2)


def acc_a_lista(acc):
    return dict(S=acc['S'].round(6).tolist(), N=acc['N'].tolist(), U=acc['U'].round(6).tolist())


def somma_acc_liste(a, b):
    """Somma due accumuli in forma di liste (usata per sommare pagine o modelli)."""
    S = (np.array(a['S']) + np.array(b['S'])).tolist()
    return dict(S=S, N=(np.array(a['N']) + np.array(b['N'])).tolist(), U=(np.array(a['U']) + np.array(b['U'])).tolist())


# ---------------------------------------------------------------- lettura di una pagina con foto

def leggi_con_foto(L, tok, tagli):
    """Fa leggere la pagina vera alla penna e prende la foto prima di ogni posizione di `tagli`: dict posizione -> (foto, logit che predicono tok[pos])."""
    pen = L.pen
    pen.apri()
    snaps = {}
    lg = None
    for t in range(len(tok) - 1):
        if t in tagli:
            snaps[t] = (foto(pen), lg)
        lg = pen.dai(int(tok[t]))
    return snaps


def scegli_punti(righe, parole, n_P, n_L, rng, classi=None, K=K_PAROLE, K_L=K_RIGA):
    """Punti d'intervento di una pagina: P = (r, i) con i >= 1 e parola prima di almeno 3 glifi; L = (r, 0) con r >= 1. Con `classi` (classe di ogni parola vera) meta' dei
    punti si sceglie fra quelli che hanno almeno una parola d'eco nelle K parole seguenti (le parole d'eco sono poche e senza questo sovracampionamento ne cadrebbero
    troppo poche): le medie per classe non ne risentono."""
    P = [(r, i) for r, L in enumerate(righe) for i in range(1, len(L['parole'])) if len(parole[r][i - 1]) >= LEN_MIN_PREC]
    Lp = [(r, 0) for r in range(1, len(righe)) if righe[r]['parole']]
    rng.shuffle(P)
    rng.shuffle(Lp)

    def scelti(lst, n, kk):
        if classi is None:
            return lst[:n]
        eco = [(r, i) for (r, i) in lst if any(classi.get((r, i + k), 0) > 0 for k in range(kk))]
        primi = eco[:(n + 1) // 2]
        resto = [x for x in lst if x not in set(primi)]
        return primi + resto[:n - len(primi)]
    return scelti(P, n_P, K), scelti(Lp, n_L, K_L)


def lavoro_pagina(L, d, don, rng, K, n_P, n_L, nomi_P, nomi_L, patch=None, mask_lettura=None, n_patch=4, K_L=K_RIGA):
    """Tutti gli interventi su una pagina vera (d: dict con tok, nome). Restituisce (acc per intervento, conti di patch). `patch`: dict con le
    classifiche di dimensioni per 'u2' e 'pw' ({nome: array di indici ordinati}) oppure None."""
    ctx, voc = L.ctx, L.voc
    tok = d['tok']
    righe = struttura(tok, ctx)
    classi, parole = classi_parole(tok, righe, ctx)
    pP, pL = scegli_punti(righe, parole, n_P, n_L, rng, classi, K, K_L)
    piani = []                                                      # (punto, nome, (start, tokens, s_cur))
    for (r, i) in pP:
        for nome in nomi_P:
            reg = regione(nome, ctx, voc, tok, righe, parole, r, i, don, rng, d['nome'])
            if reg is not None:
                piani.append(((r, i), nome, reg))
    for (r, i) in pL:
        for nome in nomi_L:
            reg = regione(nome, ctx, voc, tok, righe, parole, r, i, don, rng, d['nome'])
            if reg is not None:
                piani.append(((r, i), nome, reg))
    tagli = set()
    for (r, i), nome, (start, toks, s_cur) in piani:
        tagli.add(start)
        tagli.add(s_cur)
    snaps = leggi_con_foto(L, tok, tagli)
    acc = {}
    patch_conti = {}
    orig = {}
    fatti_patch = {}
    pw_punto = {}                                                   # risultato di `pw` in ogni punto: l'ancora dei punti dove c'e' una coppia minima
    piani.sort(key=lambda x: (x[0], x[1] != 'pw'))                  # in ogni punto `pw` per primo
    for (r, i), nome, (start, toks, s_cur) in piani:
        Kp = K if nome in NOMI_PAROLA else K_L
        if (r, i, Kp) not in orig:
            f0, lg0 = snaps[s_cur]
            ripristina(L.pen, f0)
            orig[(r, i, Kp)] = L.perturba(f0, lambda: L.continua(tok, righe, r, i, lg0, Kp, mask_lettura))
            ripristina(L.pen, f0)
        rO = orig[(r, i, Kp)]
        f1, _ = snaps[start]
        f0, lg0 = snaps[s_cur]

        def corri():
            ripristina(L.pen, f1)
            lg = L.alimenta(toks)
            if nome in NOMI_PAROLA:                       # interventi sulla parola prima: i candidati del puntatore restano le parole vere (come nella scrittura)
                L.pen.righe_parole[L.pen.linea] = [(parole[r][k], GM.feat_parola(parole[r][k], ctx)) for k in range(i)]
            fd = foto(L.pen)
            rM = L.continua(tok, righe, r, i, lg, Kp, mask_lettura)
            return fd, rM
        fd, rM = L.perturba(f1, corri)
        ck = [classi[(r, i + k)] for k in range(len(rO))]
        a = acc.setdefault(nome, nuovo_acc(Kp))
        somma_diff(a, rO, rM[:len(rO)], ck)
        if nome == 'pw':
            pw_punto[(r, i)] = (rO, rM, ck)
        elif nome in MINIME and (r, i) in pw_punto:                 # `pw` sugli stessi punti di questo intervento: l'ancora abbinata
            rO2, rM2, ck2 = pw_punto[(r, i)]
            somma_diff(acc.setdefault('pw@' + nome, nuovo_acc(Kp)), rO2, rM2[:len(rO2)], ck2)
        if patch is not None and nome in NOMI_PATCH and fatti_patch.get(nome, 0) < n_patch:
            fatti_patch[nome] = fatti_patch.get(nome, 0) + 1
            _patch_punto(L, patch, nome, tok, righe, r, i, f0, lg0, fd, rO, rM, Kp, rng, patch_conti, mask_lettura)
    return acc, patch_conti


def _patch_punto(L, patch, nome, tok, righe, r, i, f0, lg0, fd, rO, rM, K, rng, conti, mask_lettura):
    """Scambio parziale di stati nel punto (r, i): `f0` = stato vero, `fd` = stato donatore (foto presa dopo aver letto il contesto modificato)."""
    import torch
    n = min(len(rO), len(rM))
    aM = [rM[k]['lp1'] - rO[k]['lp1'] for k in range(n)]
    dM = np.array([(rM[k]['lpm'] - rO[k]['lpm']) / math.log(2) for k in range(n)])
    pO = np.exp(rO[0]['lp1'])
    pM = np.exp(rM[0]['lp1'])
    w = (pO + pM) / 2
    a0 = aM[0]
    den0 = float((w * a0 * a0).sum())
    Hn = f0['h2'].shape[-1]
    for v in VARIANTI_PATCH:
        if v.startswith('top'):
            dims = patch[nome][:int(v[3:])]
            quali = 'dims'
        elif v.startswith('rnd'):
            k = int(v[3:])
            dims = patch['__rnd__'][nome][:k]
            quali = 'dims'
        else:
            dims, quali = None, v

        def corri():
            lg = L.stato_patchato(f0, fd, quali, dims)
            return L.continua(tok, righe, r, i, lg, K, mask_lettura)
        rV = L.perturba(f0, corri)
        b0 = rV[0]['lp1'] - rO[0]['lp1']
        num0 = float((w * a0 * b0).sum())
        dV = np.array([(rV[k]['lpm'] - rO[k]['lpm']) / math.log(2) for k in range(n)])
        c = conti.setdefault((nome, v), [0.0, 0.0, 0.0, 0.0, 0])
        c[0] += num0
        c[1] += den0
        c[2] += float((dV * dM).sum())
        c[3] += float((dM * dM).sum())
        c[4] += 1


def classifica_dimensioni(L, pagine, don, rng, nome, n_punti, K=2):
    """Su pagine date (di addestramento): per ogni punto dell'intervento `nome` la differenza fra lo stato donatore e quello vero del secondo strato;
    punteggio di ogni dimensione = media di |differenza| * norma della colonna d'uscita. -> array di indici dall'importanza maggiore alla minore."""
    import torch
    ctx, voc = L.ctx, L.voc
    W = L.m.out.weight.detach().numpy()
    norma = np.sqrt((W ** 2).sum(0))
    tot, n = None, 0
    per = max(1, n_punti // max(len(pagine), 1) + 1)
    for d in pagine:
        if n >= n_punti:
            break
        tok = d['tok']
        righe = struttura(tok, ctx)
        classi, parole = classi_parole(tok, righe, ctx)
        pP, pL = scegli_punti(righe, parole, per if nome in NOMI_PAROLA else 0, per if nome in NOMI_RIGA else 0, rng, classi)
        piani = []
        for (r, i) in (pP if nome in NOMI_PAROLA else pL):
            reg = regione(nome, ctx, voc, tok, righe, parole, r, i, don, rng, d['nome'])
            if reg is not None:
                piani.append(((r, i), reg))
        tagli = {x for _, (st, tt, sc) in piani for x in (st, sc)}
        snaps = leggi_con_foto(L, tok, tagli)
        for (r, i), (start, toks, s_cur) in piani:
            f1, _ = snaps[start]
            f0, _ = snaps[s_cur]

            def corri():
                ripristina(L.pen, f1)
                L.alimenta(toks)
                return foto(L.pen)
            fd = L.perturba(f1, corri)
            dif = np.abs((fd['h2'] - f0['h2']).numpy().reshape(-1))
            tot = dif if tot is None else tot + dif
            n += 1
    if tot is None:
        return np.arange(L.m.cfg['nasc'])
    punteggio = (tot / max(n, 1)) * norma
    return np.argsort(-punteggio)


# ---------------------------------------------------------------- interventi sulla testa di pagina (stato dall'inizio)

def lavoro_testa_pagina(L, d, K_BUCKET=(10, 40, 100)):
    """hS, hL, hM: la sezione, la lingua o la mano della testa della pagina scambiate con quelle di un'altra pagina (valore diverso preso a caso fra
    quelli dell'elenco); la pagina vera viene poi letta per intero. Restituisce per ogni intervento un accumulo con 'K' = classi di distanza dall'inizio
    della pagina (parole 0-9, 10-39, 40-99, 100 e oltre)."""
    ctx, voc = L.ctx, L.voc
    tok = d['tok']
    righe = struttura(tok, ctx)
    classi, parole = classi_parole(tok, righe, ctx)
    idx = voc['idx']
    segni = voc['segni']
    nb = len(K_BUCKET) + 1

    def leggi_pagina(tok_testa):
        pen = L.pen
        pen.apri()
        lg = L.alimenta(tok_testa)
        out = []
        for r, Ln in enumerate(righe):
            lg = L.alimenta(tok[Ln['h']:Ln['h'] + 3])
            out += [(r, i, x) for i, x in enumerate(L.continua(tok, righe, r, 0, lg, 10 ** 6))]
        return out
    rO = leggi_pagina(tok[:4])
    acc = {}
    rng = random.Random(zlib.crc32(('testa:' + d['nome']).encode('utf-8')))
    for nome, pref, pos in (('hS', 'S:', 1), ('hM', 'M:', 2), ('hL', 'L:', 3)):
        alt = [idx[s] for s in segni if s.startswith(pref) and idx[s] != int(tok[pos])]
        if not alt:
            continue
        nuova = list(tok[:4])
        nuova[pos] = rng.choice(alt)
        rM = leggi_pagina(nuova)
        a = nuovo_acc(nb)
        for k, ((r, i, o), (_, _, m)) in enumerate(zip(rO, rM)):
            b = sum(k >= x for x in K_BUCKET)
            somma_diff_uno(a, o, m, classi[(r, i)], b)
        acc[nome] = a
    return acc


def somma_diff_uno(acc, o, m, c, k):
    acc['N'][c, k] += 1
    S = acc['S'][c, k]
    S[0] += kl_bit(o['lp1'], m['lp1'])
    S[1] += (m['lpw'] - o['lpw']) / math.log(2)
    S[2] += (m['lpm'] - o['lpm']) / math.log(2)
    S[3] += (0.0 if o['pf'] != o['pf'] else ((1.0 - m['pf']) - (1.0 - o['pf'])))
    S[4] += (m['lpt'] - o['lpt']) / math.log(2)
    if o['eol']:
        acc['U'][0] += 1
        acc['U'][1] += (m['lpt'] - o['lpt']) / math.log(2)
        acc['U'][2] += (m['lpm'] - o['lpm']) / math.log(2)
