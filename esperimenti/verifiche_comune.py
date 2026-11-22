# -*- coding: utf-8 -*-
"""Supporto di IA25, "le verifiche rapide" (modulo, non e' un esperimento): le cose che servono a piu' di una parte.

Che cosa c'e' qui, in parole semplici
- percorsi (cache di IA25, libri di ia20 e ia22 gia' scritti), caricamento di un libro per nome ('vere', 'V21:13', 'M1:3', 'M5:3', 'E2:3',
  e i libri scritti da IA25 a temperature diverse 'M1@090:3');
- i metadati di pagina (sezione, lingua A/B, mano, fascicolo, bifoglio) e il "riferimento" della copia netta di ia09 scelto in quattro modi
  (pagina a caso come in ia09; stessa sezione, lingua e mano; stessa sezione e fascicolo; stesso bifoglio);
- `con_riferimento`: sostituisce per un momento la funzione che in ia09 sceglie "l'altra pagina" (senza toccare ia09) e lascia
  `imitatore_misure.lavoro_M` calcolare copia netta, quota locale Λ, rho e contatto con il nuovo riferimento;
- le piccole funzioni di aggregazione e di scrittura dei risultati (solo numeri).
Nessun risultato e nessuna parola del manoscritto e' scritta qui. Con SOLO_CONTROLLI=1 il "libro vero" e' il latino nella
disposizione del Voynich (come in ia07, ia16, ia20): niente testo del Voynich.
"""
import contextlib
import json
import math
import os
import pickle
import random
import statistics
import sys
import time
import zlib
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import ia20_imitatore_gradini as I20  # noqa: E402
import ia22_eco_e_legame as I22  # noqa: E402
import ia09_dove_sta_sintassi as A9  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import eco_testi as ET  # noqa: E402

SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
PICCOLO = I20.PICCOLO
CACHE25 = os.environ.get('CACHE25', os.path.join(USCITA, 'ia25_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia25'))
LIBRI25 = os.path.join(CACHE25, 'libri')
MISURE25 = os.path.join(CACHE25, 'misure')
MODELLI25 = os.path.join(CACHE25, 'modelli')
RISULTATI = os.path.join(QUI, '..', 'risultati')

_DER0 = A9.SM.derangement                       # la scelta dell'"altra pagina" di ia09 (permutazione a caso senza punti fissi)
_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def mes(xs):
    return MS.media_es(xs)


def pulisci(x):
    """Per scrivere in json: numpy -> python, nan/inf -> None, chiavi -> stringhe."""
    if isinstance(x, dict):
        return OrderedDict((str(k), pulisci(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return pulisci(float(x)) if isinstance(x, np.floating) else int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return pulisci(x.tolist())
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return x


def leggi_corse(percorso):
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()] if os.path.exists(percorso) else []


def crea_cartelle():
    for d in (CACHE25, LIBRI25, MISURE25, MODELLI25):
        os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------- libri

TEMPERATURE = OrderedDict([('080', 0.8), ('090', 0.9), ('100', 1.0), ('110', 1.1)])      # fissate prima (preregistrazione IA25, parte 3)


def percorso_libro_T(tipo, tkey, i):
    return os.path.join(LIBRI25, 'ia25_libro_%s_T%s_%d.txt' % (tipo, tkey, i))


def t_libro(nome):
    """Il libro come lista (pagina, inizio, parole stringhe). Nomi: 'V21:k', 'M1:i', 'M5:i' (cache di ia20), 'E2:i' (cache di ia22),
    'M1@090:i' / 'E2@110:i' (scritti da IA25 a una temperatura; a T=1,00 sono i libri originali)."""
    tipo, k = nome.split(':')
    k = int(k) if k.isdigit() else k
    if '@' in tipo:
        t, tk = tipo.split('@')
        if tk == '100' and t in ('M1', 'E2'):
            return t_libro('%s:%d' % (t, k))
        return I7.leggi_file(percorso_libro_T(t, tk, k))
    if tipo in ('M1', 'M5'):
        return I7.leggi_file(I20.percorso_libro(int(tipo[1]), k))
    if tipo == 'E2':
        return I7.leggi_file(I22.percorso_libro('E2', k))
    if tipo in ('V21', 'ctrl', 'I07'):
        return I16.t_di(nome)
    raise ValueError(nome)


def rows_libro(nome):
    """Il libro nel formato di ia01 (pagina -> righe (inizio, [parola come tupla di glifi]))."""
    if nome == 'vere':
        return I7.contesto_A()['vere']
    tipo = nome.split(':')[0]
    if tipo in ('V21', 'ctrl'):
        return I16.rows_di(nome)
    return I7.libro_A_da_righe(t_libro(nome))


def t_da_rows(rows):
    return [(p, ini, [''.join(w) for w in ws]) for p, rr in rows.items() for ini, ws in rr]


# ---------------------------------------------------------------- metadati di pagina e riferimenti della copia netta

RIF_NOMI = OrderedDict([('0', 'pagina a caso (come ia09)'), ('1', 'stessa sezione, lingua e mano'), ('2', 'stessa sezione e fascicolo'),
                        ('3', 'stesso bifoglio')])


def meta_pagine():
    """pagina -> dict(sez, lingua, mano, Q, F, B). Sezione, lingua e mano dal libro vero (con SOLO_CONTROLLI le stesse intestazioni di pagina,
    parole latine); fascicolo (Q), foglio (F), bifoglio (B) da eco_testi (con SOLO_CONTROLLI quelli finti: un fascicolo ogni 16 pagine)."""
    if 'meta' in _C:
        return _C['meta']
    base = OrderedDict()
    for x in I7.libro_vero():
        base.setdefault(x['pagina'], (x['sezione'], x['lingua'], x['mano']))
    nomi = sorted(base)
    gen = ET.meta_di(nomi, prova=SOLO_CONTROLLI)
    out = OrderedDict()
    for p in nomi:
        s, l, m = base[p]
        g = gen.get(p, {})
        out[p] = dict(sez=s, lingua=l, mano=m, Q=g.get('Q'), F=g.get('F'), B=g.get('B'))
    _C['meta'] = out
    return out


def livelli_riferimento(rif, meta):
    """Funzioni chiave dal piu' fine al piu' grosso: la pagina di riferimento sta nel gruppo piu' fine che ha almeno due pagine."""
    sez = lambda p: meta[p]['sez']                                                       # noqa: E731
    sl = lambda p: (meta[p]['sez'], meta[p]['lingua'])                                    # noqa: E731
    sq = lambda p: (meta[p]['sez'], meta[p]['Q']) if meta[p]['Q'] is not None else ('?', p)      # noqa: E731
    qb = lambda p: (meta[p]['Q'], meta[p]['B']) if meta[p]['Q'] is not None and meta[p]['B'] is not None else ('?', p)    # noqa: E731
    slm = lambda p: (meta[p]['sez'], meta[p]['lingua'], meta[p]['mano'])                  # noqa: E731
    if rif == '1':
        return [slm, sl, sez]
    if rif == '2':
        return [sq, sez]
    if rif == '3':
        return [qb, sq, sez]
    raise ValueError(rif)


def riferimento_pagine(nomi, seme, rif, meta, info=None):
    """Per ogni pagina di `nomi` un'altra pagina di riferimento (mai se stessa), con il riferimento `rif`. rif '0' = ia09 (derangement a caso).
    Per rif diverso: la pagina e' scelta a caso (seme fisso) fra le altre del gruppo piu' fine con almeno due pagine; se serve un gruppo piu' grosso
    del primo livello e' un "ripiego" (si conta in `info`)."""
    nomi = sorted(nomi)
    if rif == '0':
        return _DER0(nomi, seme)
    rnd = random.Random(seme)
    livelli = livelli_riferimento(rif, meta)
    gruppi = []
    for f in livelli:
        g = defaultdict(list)
        for p in nomi:
            g[f(p)].append(p)
        gruppi.append((f, g))
    ref, ripiego, livello_ult = {}, 0, 0
    for p in nomi:
        for li, (f, g) in enumerate(gruppi):
            altri = [q for q in g[f(p)] if q != p]
            if altri:
                ref[p] = rnd.choice(altri)
                ripiego += li > 0
                livello_ult = max(livello_ult, li)
                break
        else:
            altri = [q for q in nomi if q != p]
            ref[p] = rnd.choice(altri)
            ripiego += 1
    if info is not None:
        info['ripiego'] = ripiego / max(len(nomi), 1)
    return ref


@contextlib.contextmanager
def con_riferimento(rif, info=None):
    """Mentre dura, `lavoro_C` di ia09 sceglie la pagina "altra" con il riferimento `rif` (ia09 non viene modificato: si sostituisce per un momento
    l'attributo `derangement` del modulo di sintassi che ia09 chiama)."""
    meta = meta_pagine()

    def der(nomi, seme):
        return riferimento_pagine(nomi, seme, rif, meta, info)
    A9.SM.derangement = der
    try:
        yield
    finally:
        A9.SM.derangement = _DER0


def struttura_M(nome, rows, rif='0', info=None):
    """`imitatore_misure.lavoro_M` (copia netta, Λ, rho, contatto, con le pagine di ia09 e il suo riferimento) sul libro `rows` con il riferimento `rif`.
    Il nome e' quello che usa ia20/ia22 ('M1:3', 'V21:13', 'vere'): cosi' con rif '0' si ritrovano gli stessi numeri."""
    c = I7.contesto_A()
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    with con_riferimento(rif, info):
        return MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag})


def stime_M(r):
    """Da un risultato di `lavoro_M`: copia netta, Λ, rho come numeri con bootstrap (A9.V) e il contatto."""
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
    return dict(netto=netto_t, lam=lam, rho=rho, contatto=float(r['mi']), pagine=P)


# ---------------------------------------------------------------- statistiche

def classe_vero(m, e, vero, soglia=I20.SOGLIA_ERRORI, tol=I20.VERO_TOL):
    """Regola "al vero" di ia20 (entro 2 errori dei libri o entro il 5% del valore vero)."""
    if m is None or vero is None:
        return None
    return bool(abs(m - vero) <= max(soglia * (e or 0.0), tol * abs(vero)))


def scrivi_json(percorso, o):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pulisci(o), f, ensure_ascii=False, indent=1)
        f.write('\n')


def tabella_md(intest, righe):
    out = ['| ' + ' | '.join(intest) + ' |', '|' + '---|' * len(intest)]
    for r in righe:
        out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return out


def fmt(v, d=3):
    return nu(v, d)


def fmt_mes(x, d=3):
    if x is None or x[0] is None:
        return '—'
    return '%s ± %s' % (nu(x[0], d), nu(x[1], d) if x[1] is not None else '—')
