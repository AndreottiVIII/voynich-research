# -*- coding: utf-8 -*-
"""Supporto di ia16 (modulo, non e' un esperimento): le misure sui libri dell'imitatore.

Che cosa c'e' qui, in parole semplici
- Giudice K di ia11 (n-grammi con memoria di pagina, `rifarlo_giudici.GiudiceK`), ma addestrato e provato sulle pieghe PER FOGLIO di
  ia07 (le stesse dei generatori): `lavoro_K` dà i profili di sorpresa a 14 numeri di ogni pagina vera e di ogni libro, `auc_da_profili`
  l'AUC con la regressione logistica di ia01, `negativo_K` il controllo con etichette a caso.
- Misure di struttura, importate senza modifiche da ia09 (copia netta della pagina, quota locale Λ), ia10 (D, guadagno dell'ordine
  fra famiglie di parole) e dal modulo di ia11 (contatto ultimo -> primo glifo, g di ia08): `lavoro_M` (copia netta, Λ, contatto)
  e `lavoro_D` (D) calcolano i numeri per pagina; `copia_netta_lambda` li riassume.
- `ripetizioni_interne`: righe e parole che si ripetono dentro la pagina (sintomo di scrittura che si avvita).
- Piccole funzioni di statistica (media ed errore standard, lettura "piu' vicino / uguale / piu' lontano" a due errori).
Una pagina e' una lista di righe (inizio_paragrafo, [parola, ...]); una parola e' una tupla di glifi EVA fusi (come ia01).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import math
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import ia09_dove_sta_sintassi as A9  # noqa: E402
import ia10_famiglie_parole as I10  # noqa: E402
import rifarlo_giudici as J  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NEG = G.NEG


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def media_es(xs):
    xs = [x for x in xs if x is not None and x == x]
    if not xs:
        return None, None
    return float(np.mean(xs)), (float(np.std(xs, ddof=1) / len(xs) ** 0.5) if len(xs) > 1 else None)


def confronta(m, em, v, ev, soglia=2.0):
    """d = m - v, e = radice(em^2 + ev^2): 'piu' vicino' (m sotto v di oltre 2 e), 'piu' lontano' (sopra), 'uguale'. Per le AUC (piu' basso = meglio)."""
    if m is None or v is None:
        return OrderedDict([('differenza', None), ('errore', None), ('lettura', 'non calcolabile')])
    d = m - v
    e = math.sqrt((em or 0.0) ** 2 + (ev or 0.0) ** 2)
    lett = 'più vicino' if d < -soglia * e else 'più lontano' if d > soglia * e else 'uguale entro l\'errore'
    return OrderedDict([('differenza', d), ('errore', e), ('lettura', lett)])


# ---------------------------------------------------------------- giudice K sulle pieghe per foglio

def divisione_K(c, f):
    """(pagine di prova, di validazione, di addestramento) della piega f di K: le pagine vere (>= 40 parole) dei fogli delle altre
    pieghe, 10% per la validazione (come ia11)."""
    test = [p for p in c['ids'] if c['fold'][p] == f]
    resto = [p for p in c['ids'] if c['fold'][p] != f]
    random.Random(3964 + 100 * I10.SEME_DIV + f).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    return test, resto[:nval], resto[nval:]


def lavoro_K(f, c, libri):
    """Profili di sorpresa (14 numeri) delle pagine di prova della piega f: `vere` e ogni libro di `libri` (nome -> pagina -> righe)."""
    test, val, add = divisione_K(c, f)
    g, info = J.scegli_giudice_k([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V'])
    prof = OrderedDict()
    prof['vere'] = OrderedDict((p, G.profilo(c['ids'][p], g.sorpresa(c['ids'][p]))) for p in test)
    for nome, rows in libri.items():
        out = OrderedDict()
        for p in test:
            if p in rows:
                a = G.codifica(rows[p], c['idx'])
                out[p] = G.profilo(a, g.sorpresa(a))
        prof[nome] = out
    return info, prof


def unisci_profili(lista):
    """Profili di piu' pieghe (liste di dizionari nome -> pagina -> profilo) in uno solo."""
    out = OrderedDict()
    for prof in lista:
        for nome, d in prof.items():
            out.setdefault(nome, OrderedDict()).update(d)
    return out


def auc_da_profili(prof, nome, n_pagine):
    """AUC (regressione logistica come ia01/e231: 10 pieghe per pagina, 5 ripetizioni) fra le pagine vere e quelle del libro `nome`."""
    if nome not in prof or 'vere' not in prof:
        return None
    pag = sorted(p for p in prof['vere'] if p in prof[nome])
    if len(pag) < 10 or len(pag) < 0.99 * n_pagine:
        return None
    X = np.array([prof['vere'][p] for p in pag] + [prof[nome][p] for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    return float(G.auc_logistico(X, y, pag + pag)[0])


def negativo_K(prof, s):
    pag = sorted(prof['vere'])
    random.Random(3970 + s).shuffle(pag)
    y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
    X = np.array([prof['vere'][p] for p in pag])
    return float(G.auc_logistico(X, y, pag)[0])


# ---------------------------------------------------------------- struttura: copia netta e quota locale (ia09), contatto (ia08)

MODELLI_M = ['g', 'n', 'gram', 'tutto', 'gram_n']


def lavoro_M(nome, pag, fold):
    """Come `lavoro_M` di ia11: numeri per pagina di ia09 dentro il testo (pagine `pag` = pagina -> righe, pieghe `fold` = pagina ->
    piega), nell'ordine vero e con le parole rimescolate dentro la pagina, e il contatto ultimo -> primo glifo."""
    nt = 'ia16:' + nome
    A9._T.clear()
    A9._T[nt] = dict(pagine=pag, fold=fold, tipo=None)
    A9._T[nt + '~p'] = dict(pagine=A9.TT.rimescola_pagina(pag, seme_str('ia16rim', nome)), fold=fold, tipo=None)
    out = OrderedDict(pag=sorted(pag), mi=R.mi_contatto(pag))
    for chiave, nm in (('t', nt), ('p', nt + '~p')):
        st = A9.lavoro_C(nm)['stat']
        ps = sorted(st)
        out['den_' + chiave] = [st[p]['n'][0] for p in ps]
        U = np.array([st[p]['w']['U'][0] for p in ps])
        for m_ in MODELLI_M:
            out['num_%s_%s' % (chiave, m_)] = [round(float(x), 3) for x in U - np.array([st[p]['w'][m_][0] for p in ps])]
    A9._T.clear()
    return out


def copia_netta_lambda(r, con_intervallo=False):
    """Da un risultato di `lavoro_M`: copia netta (bit per parola), quota locale Λ e rho, e il contatto (g)."""
    P = len(r['pag'])
    W = A9.pesi_bootstrap(P)

    def gain(ch, m_):
        return A9.stima(np.array(r['num_%s_%s' % (ch, m_)]), np.array(r['den_' + ch]), W)
    netto_t = gain('t', 'g') - gain('t', 'n')
    netto_p = gain('p', 'g') - gain('p', 'n')
    lam = A9.V(1.0, np.ones_like(netto_t.b)) - netto_p.dividi(netto_t)
    a_cn = (gain('t', 'tutto') - gain('t', 'gram_n')).pos()
    a_gr = (gain('t', 'tutto') - gain('t', 'g')).pos()
    rho = a_cn.dividi(a_cn + a_gr)
    out = OrderedDict(copia_netta=netto_t.p, lam=lam.p, rho=rho.p, contatto=float(r['mi']))
    if con_intervallo:
        out['copia_netta_ic'] = netto_t.ic()
        out['lam_ic'] = lam.ic()
    return out


# ---------------------------------------------------------------- struttura: D (ia10)

def lavoro_D(f, c, testi):
    """Per la piega f: famiglie e tabella dei passaggi imparate sulle pagine vere delle altre pieghe (90% / validazione 10%, K scelto
    sulla validazione come ia10), applicate alle pagine di prova di ogni testo (nome -> pagina -> righe). Per testo:
    [somma dei guadagni nell'ordine vero, coppie, somma con le parole rimescolate nella riga, pagine]; D = (a - c) / b sulle pieghe."""
    resto = [p for p in c['ids'] if c['fold'][p] != f]
    random.Random(3964 + 100 * I10.SEME_DIV + f).shuffle(resto)
    nval = max(1, round(0.10 * len(resto)))
    VV = lambda ps: OrderedDict((p, c['vere'][p]) for p in ps)
    M = R.FamiglieModello(I10, VV(resto[nval:]), VV(resto[:nval]), K=None, seme=1)
    out = OrderedDict()
    for nome, rows in testi.items():
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        if not pg:
            out[nome] = [0.0, 0.0, 0.0, 0]
            continue
        P, Rm = R.stat_D(I10, M, pg, seme_str('D16', f, nome), I10.S_RIM)
        out[nome] = [float(P[:, 0].sum()), float(P[:, 1].sum()), float(Rm[:, 0].sum()), len(pg)]
    return out, OrderedDict(K=int(M.K), copertura=round(float(M.copertura), 4))


def D_da_pieghe(liste):
    """D da una lista di [a, b, c, n] (una per piega)."""
    a = sum(x[0] for x in liste)
    b = sum(x[1] for x in liste)
    c_ = sum(x[2] for x in liste)
    return float((a - c_) / b) if b > 0 else None


# ---------------------------------------------------------------- ripetizioni interne

def ripetizioni_interne(righe_parole_per_pagina):
    """`righe_parole_per_pagina`: pagina -> lista di righe (liste di parole, stringhe o tuple). Conti [numeratore, denominatore]:
    righe di almeno 4 parole uguali a una riga precedente della stessa pagina; righe di almeno 2 parole uguali alla riga sopra;
    parole uguali alla parola subito prima (nella riga)."""
    r4, r4n, rs, rsn, pp, ppn = 0, 0, 0, 0, 0, 0
    for righe in righe_parole_per_pagina.values():
        viste = set()
        prima = None
        for ws in righe:
            ws = tuple(ws)
            if len(ws) >= 4:
                r4n += 1
                r4 += ws in viste
                viste.add(ws)
            if len(ws) >= 2 and prima is not None:
                rsn += 1
                rs += ws == prima
            prima = ws
            for a, b in zip(ws, ws[1:]):
                ppn += 1
                pp += a == b
    return OrderedDict([('righe uguali a una precedente nella pagina (>= 4 parole)', [r4, r4n]),
                        ('righe uguali alla riga sopra (>= 2 parole)', [rs, rsn]),
                        ('parole uguali alla parola prima', [pp, ppn])])
