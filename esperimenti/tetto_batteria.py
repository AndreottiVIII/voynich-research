# -*- coding: utf-8 -*-
"""IA43, modulo di supporto: la batteria di misure e di giudici che deve "vedere" il messaggio piantato (tutto riusato, niente riscritto).

In parole semplici
- Un libro e' una lista `t` di (pagina, inizio di paragrafo, [parole come stringhe]), come lo scrive il v21. Le misure lo guardano tutto (207 pagine), non solo le pagine tenute fuori:
  il v21 ha visto l'intero Voynich, e le pagine tenute fuori non hanno senso per lui (IA42, nota 2).
- **Il "vero"** e' il libro di riferimento della batteria: nella corsa vera il Voynich (come in e409/e419 e in IA41), nelle prove un libro v21 diverso da quelli piantati (`imposta_vero_standin`).
  Il vero entra solo come riferimento dei giudici (e231, e266, N, b) e come riga "Voynich" delle misure: non e' mai un testo da leggere.
- **Famiglie di misure** (tutte funzioni gia' scritte, importate senza modifiche):
    S  le 14 misure di struttura di IA35-IA41 (`sigillo_misure.misure`: heaps, burst, riga_cv, sezione, lag23, ini_par, ttr_pagina, hapax, lingua, dispersione, vicine, lunghezza, doppie, testa);
    T  le quattro misure dell'e160 (T1 ordine delle parole frequenti, T2 accordo a distanza 2, T3 accordo nella composizione della riga, T4 informazione fra parole vicine; z contro i
       rimescolamenti), sul testo grezzo (`g`) e sul testo ripulito dall'involucro di riga (`r`, come in e160);
    P  le parole che si scelgono fra vicine e per pagina: coppie che tornano (e375, z), legame a distanza 2 (e3a07, z), parole rare chiuse nella pagina (e211, R, erbario) e nettezza degli
       argomenti (e334, z, erbario A);
    J  i giudici del banco di IA26 che non hanno bisogno di una rete addestrata per libro: e231 ed e266 (AUC; `ia07.giudica`) e N (conteggi di n-grammi dentro la riga; `righello_giudici`);
    b  il giudice b di IA35 (`sezione_giudice.esame_b_medio`) su un INSIEME di libri: AUC per libro (media sulle ripetizioni in cui il libro era di prova) e nullo.
- Le funzioni sono quelle degli esperimenti originali: con i loro parametri (rimescolamenti ridotti per le misure P: 100 invece di 200-1000, dichiarato in preregistrazione).
Nessun risultato e' scritto qui.
"""
import os
import random
import sys
import time
from collections import OrderedDict

import numpy as np

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia01_giudice_neurale as G  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402

PERM_P = int(os.environ.get('PERM_P43', 100))        # rimescolamenti delle misure e375 ed e3a07
MIN_PAROLE_H = 60

NOMI_S = ('heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par', 'ttr_pagina', 'hapax', 'lingua', 'dispersione', 'vicine', 'lunghezza', 'doppie', 'testa')
NOMI_T = tuple('T%d%s' % (i, v) for v in ('g', 'r') for i in (1, 2, 3, 4))
NOMI_P = ('e375', 'e3a07', 'e211', 'e334')
NOMI_J = ('e231', 'e266', 'N')
NOMI_M = NOMI_S + NOMI_T + NOMI_P                      # misure per libro, senza giudici
NOMI_TUTTE = NOMI_M + NOMI_J + ('b',)


# ---------------------------------------------------------------- il mondo: il "vero"

def righe_dizionario(t, attributi):
    """Il libro `t` come righe-dizionario nel formato di `ia07.libro_vero()`; foglio, sezione, lingua e mano di ogni pagina da `attributi` (pagina -> (foglio, sezione, lingua, mano))."""
    out = []
    for p, ini, ps in t:
        if not ps:
            continue
        fog, sez, lin, man = attributi[p]
        out.append(dict(pagina=p, foglio=fog, sezione=sez, lingua=lin, mano=man, ini=bool(ini), parole=list(ps)))
    for i, x in enumerate(out):
        dopo = out[i + 1] if i + 1 < len(out) else None
        x['fin'] = dopo is None or dopo['pagina'] != x['pagina'] or dopo['ini']
    return out


def imposta_vero_standin(t_vero):
    """PROVE: il libro `t_vero` (un v21 senza messaggio) prende il posto del Voynich come "vero" in tutto il codice di IA07 (pagine, giudici, misure di sezione). Va chiamata PRIMA di ogni
    altra cosa nel processo. Della trascrizione si prendono solo gli attributi delle pagine (foglio, sezione, lingua, mano): niente parole."""
    I7._C.pop('righe', None)
    attr = OrderedDict()
    for x in I7.libro_vero():
        attr.setdefault(x['pagina'], (x['foglio'], x['sezione'], x['lingua'], x['mano']))
    I7._C.clear()
    righe = righe_dizionario(t_vero, attr)
    I7._C['righe'] = righe
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    vpag, vi = OrderedDict(), OrderedDict()
    for x in righe:
        vpag.setdefault(x['pagina'], [x['lingua'], []])[1].append(list(x['parole']))
        vi.setdefault(x['pagina'], [x['lingua'], []])[1].append((x['ini'], list(x['parole'])))
    rif = e231.riferimenti(vpag)
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    I7._C['rif'] = dict(vpag=vpag, rif=rif, rif266=rif266, vt266=vt266)
    for modulo in ('piano_misure',):
        try:
            import importlib
            m = importlib.import_module(modulo)
            m._K.clear()
        except Exception:                                                   # noqa: BLE001
            pass
    _N.clear()


# ---------------------------------------------------------------- formati

def rows_di(t):
    """Il libro come pagine (pagina -> [(inizio, [parola come tupla di glifi])]), le parole non pulite (con ? o *) tolte, come ia01.pagine_da_righe."""
    import trascrizione
    return G.pagine_da_righe(t, I7.divisore(), trascrizione.pulita)


def pagine_e160(t):
    """Come `e160.pagine_voynich`: lista di pagine, ognuna lista di (inizio, [parole])."""
    import trascrizione
    per = OrderedDict()
    for p, ini, ps in t:
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            per.setdefault(p, []).append((bool(ini), ps))
    return list(per.values())


def pagine_e375(t):
    """Come `e375.voynich`: lista di pagine, ognuna lista di righe di parole come tuple di glifi."""
    import trascrizione
    D = I7.divisore()
    per = OrderedDict()
    for p, ini, ps in t:
        ws = [tuple(D(w)) for w in ps if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per.setdefault(p, []).append(ws)
    return list(per.items())


def pagine_e328(t):
    """Come `e328.carica`: pagina -> lista di paragrafi, ognuno lista di (tipo, parole)."""
    import trascrizione
    pag = OrderedDict()
    for p, ini, ps in t:
        ws = [w for w in ps if trascrizione.pulita(w)]
        if not ws:
            continue
        pars = pag.setdefault(p, [])
        if ini or not pars:
            pars.append([])
        pars[-1].append(('prima' if ini else 'interna', ws))
    for p, pars in pag.items():
        for par in pars:
            if len(par) > 1:
                par[-1] = ('ultima', par[-1][1])
    return pag


# ---------------------------------------------------------------- misure per libro

def misure_S(t):
    import sigillo_misure as SMIS
    rows = rows_di(t)
    ids = [p for p in I7.contesto_A()['ids']]
    m = SMIS.misure(rows, ids)
    return OrderedDict((n, m.get(n)) for n in NOMI_S)


def misure_T(t):
    import e160_testo_ripulito as e160
    pagine = pagine_e160(t)
    out = OrderedDict()
    for suff, pg in (('g', pagine), ('r', e160.ripulisci(pagine))):
        _, r = e160.una(('x', pg))
        for i, k in enumerate(('T1', 'T2', 'T3', 'T4'), 1):
            out['T%d%s' % (i, suff)] = r[k]['z']
    return out


def misure_P(t):
    import e211_parole_proprie as e211
    import e334_orologio as e334
    import e375_coppie as e375
    import e380_sandhi as e380
    import e381_parole_intere as e381                          # noqa: F401  (e380 la usa)
    out = OrderedDict()
    pg = pagine_e375(t)
    out['e375'] = e375.Corpo([r for _, r in pg]).prova(random.Random(375), perm=PERM_P)['z']
    import e3a07_distanza_due_pagina as e3a07
    out['e3a07'] = e380.prova(e3a07.terne(pg), random.Random(3107), PERM_P)['z']
    chiavi = {x['pagina']: x['sezione'] for x in I7.libro_vero()}
    per_h = OrderedDict()
    for p, ini, ps in t:
        if chiavi.get(p) == 'H':
            per_h.setdefault(p, []).extend(w for w in ps if '?' not in w and '*' not in w)
    unita = [ws for ws in per_h.values() if len(ws) >= MIN_PAROLE_H]
    out['e211'] = e211.prova(unita, random.Random(211))['R'] if len(unita) >= 10 else None
    try:
        out['e334'] = e334.e334(pagine_e328(t), random.Random(334))['z']
    except Exception:                                                       # noqa: BLE001
        out['e334'] = None
    return out


def misure_libro(t):
    """Le misure delle famiglie S, T, P di un libro. -> OrderedDict nome -> valore (None se non calcolabile)."""
    out = OrderedDict()
    for f in (misure_S, misure_T, misure_P):
        out.update(f(t))
    return out


_N = {}


def giudici_libro(t):
    """e231, e266 (AUC, `ia07.giudica`) e N (AUC) di un libro, contro il vero del mondo. -> OrderedDict."""
    import righello_giudici as RG
    g = I7.giudica(t)
    out = OrderedDict([('e231', g['AUC_e231']), ('e266', g['AUC_e266'])])
    if 'v' not in _N:
        c = I7.contesto_A()
        nomi = sorted(c['ids'])
        voc = RG.vocabolario_N(c['vere'])
        Xv, pv = RG.matrice_righe_N(c['vere'], nomi, voc)
        _N['v'] = dict(nomi=nomi, voc=voc, Xv=Xv, pv=pv)
    v = _N['v']
    rows = rows_di(t)
    Xt, pt = RG.matrice_righe_N(OrderedDict((p, rows.get(p, [])) for p in v['nomi']), v['nomi'], v['voc'])
    out['N'] = RG.auc_N(v['Xv'], v['pv'], Xt, pt, len(v['nomi']))
    return out


def giudice_b(libri, seme, rip=None, perm=None):
    """Il giudice b di IA35 (mediato) su un insieme di libri `libri` (liste `t`), contro il vero del mondo. Pagine di giudizio: le pagine del vero con almeno 40 parole presenti in tutti i libri.
    -> dict (`auc`, `per_libro`, ...; senza nullo)."""
    import righello_giudici as RG
    import sezione_giudice as SG
    c = I7.contesto_A()
    pagine = list(c['ids'])
    voc = RG.vocabolario_N(c['vere'])
    # il nullo (permutazioni delle etichette) non serve ai criteri di IA43 (la fascia dei libri senza messaggio fa da nullo) e costa 8 volte: si salta, `permutazioni=0`
    return SG.esame_b_medio(c['vere'], [rows_di(t) for t in libri], pagine, I7.foglio_di, voc, ripetizioni=rip, permutazioni=0 if perm is None else perm, seme=seme)


def valori_vero():
    """Le stesse misure M (S, T, P) e giudici sul "vero" del mondo: per i giudici non hanno senso (il vero contro se stesso): solo le misure."""
    t = [(x['pagina'], x['ini'], list(x['parole'])) for x in I7.libro_vero()]
    return misure_libro(t)


def valori_takahashi():
    """SOLO nella corsa vera: le stesse misure M sulla trascrizione di Takahashi (`IT`) invece che su quella di Zandbergen e Landini (`ZL`). Non provata prima della corsa (legge il Voynich)."""
    import trascrizione
    t = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            t.append((r.pagina, bool(r.inizio_par), ps))
    return misure_libro(t)


if __name__ == '__main__':
    pass
