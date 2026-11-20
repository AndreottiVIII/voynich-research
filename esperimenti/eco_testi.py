# -*- coding: utf-8 -*-
"""Metadati delle pagine per ia15 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- per ogni pagina del Voynich: sezione illustrata (erbario, astronomia, ...), lingua A/B, mano, quaderno, foglio, bifoglio,
  posto nell'ordine del manoscritto e "tipo di pagina" (solo testo, ricette, erbario con disegno, con testo circolare, con
  etichette, altro). Si leggono solo le INTESTAZIONI delle pagine e il TIPO di ogni riga di trascrizione (paragrafo, etichetta,
  cerchio, raggio): nessuna parola.
- per i testi che non sono il Voynich (lingue, generatori): metadati finti ma con la stessa forma (4 sezioni a blocchi, un
  "quaderno" ogni 16 pagine, un "foglio" ogni 2 pagine), cosi' le misure sulle pagine vicine si possono provare ovunque.
- la matrice delle "relazioni" fra pagine (stesso foglio, stesso bifoglio, pagine consecutive, stesso quaderno, stessa
  sezione ma lontane, altra sezione).
Non carica il testo del Voynich: per quello ci sono le funzioni di ia01 (`contesto`) e di `sintassi_testi`.
"""
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)

CLASSI_REL = ['foglio', 'bifoglio', 'consecutive', 'quaderno', 'sezione_lontana', 'altra_sezione']
TIPI_PAGINA = ['T solo testo', 'S ricette', 'H erbario', 'circolare o raggi', 'etichette', 'altro']
DISEGNI = os.path.join(QUI, '..', 'dati', 'cache', 'disegni_e190.json')


def tipo_pagina(sez, n_cerchi_raggi, n_etichette):
    """Il tipo di pagina, dal solo metadato: 'T' e 'S' sono sezioni a se' (solo testo; ricette con stelline); poi pagine con
    testo circolare o a raggi; poi l'erbario (disegno grande di una pianta); poi pagine con etichette; il resto."""
    if sez == 'T':
        return 'T solo testo'
    if sez == 'S':
        return 'S ricette'
    if n_cerchi_raggi:
        return 'circolare o raggi'
    if sez == 'H':
        return 'H erbario'
    if n_etichette:
        return 'etichette'
    return 'altro'


def meta_voynich():
    """pagina -> metadati, per tutte le intestazioni del file ZL (solo variabili di pagina e tipo di riga)."""
    import trascrizione
    var, ordine = {}, []
    with open(os.path.join(trascrizione.CARTELLA, trascrizione.FILE['ZL']), encoding='latin-1') as f:
        for linea in f:
            linea = linea.rstrip('\n')
            if not linea or linea[0] == '#':
                continue
            m = trascrizione._PAGINA.match(linea)
            if m and not trascrizione._LOCUS.match(linea):
                var[m.group(1)] = dict(trascrizione._VAR.findall(m.group(2) or ''))
                ordine.append(m.group(1))
    loc = defaultdict(Counter)
    for r in trascrizione.leggi('ZL'):
        if r.tipo:
            loc[r.pagina][r.tipo[0]] += 1
    area = {}
    if os.path.exists(DISEGNI):
        area = {p: float(v[0]) for p, v in json.load(open(DISEGNI, encoding='utf-8')).items()}
    out = OrderedDict()
    for i, p in enumerate(ordine):
        v = var[p]
        c = loc[p]
        out[p] = dict(sez=v.get('I') or '?', lingua=v.get('L') or '?', mano=v.get('H') or '?', Q=v.get('Q'), F=v.get('F'), B=v.get('B'),
                      ord=i, tipo=tipo_pagina(v.get('I'), c['C'] + c['R'], c['L']), area=area.get(p))
    return out


def meta_generica(nomi, sezioni=None):
    """Metadati finti per testi senza struttura di manoscritto: 4 sezioni a blocchi (o quelle date), un quaderno ogni 16
    pagine, un foglio ogni 2 pagine, nessun bifoglio. L'ordine e' quello dei nomi."""
    nomi = sorted(nomi)
    n = len(nomi)
    out = OrderedDict()
    for i, p in enumerate(nomi):
        out[p] = dict(sez=(sezioni or {}).get(p, 'S%d' % (i * 4 // max(n, 1))), lingua='-', mano='-', Q='Q%d' % (i // 16),
                      F='F%d' % (i // 2), B=None, ord=i, tipo='generico', area=None)
    return out


_META = {}


def meta_di(nomi, sezioni_prova=None, prova=False):
    """I metadati delle pagine `nomi`: quelli del manoscritto se tutte le pagine ne fanno parte (e non siamo in prova),
    altrimenti quelli finti. `sezioni_prova`: sezioni di ia01 per le pagine del latino di prova."""
    nomi = list(nomi)
    if not prova:
        if 'v' not in _META:
            _META['v'] = meta_voynich()
        mv = _META['v']
        if all(p in mv for p in nomi):
            return OrderedDict((p, mv[p]) for p in sorted(nomi))
    return meta_generica(nomi, sezioni_prova)


def relazioni(meta, nomi):
    """Matrice np x np di classi di relazione fra pagine (indice in CLASSI_REL; -1 se non e' nessuna delle sei, e sulla diagonale):
    0 stesso foglio (fronte e retro: stesso quaderno e stessa lettera di foglio); 1 stesso bifoglio (stesso quaderno e stesso
    numero di bifoglio, foglio diverso); 2 pagine consecutive nel manoscritto (fuori dalle due classi precedenti);
    3 stesso quaderno (le altre); 4 stessa sezione, quaderno diverso e stessa mano; 5 altra sezione."""
    n = len(nomi)
    K = np.full((n, n), -1, dtype=np.int8)
    for a in range(n):
        ma = meta[nomi[a]]
        for b in range(a + 1, n):
            mb = meta[nomi[b]]
            stessoQ = ma['Q'] is not None and ma['Q'] == mb['Q']
            if stessoQ and ma['F'] == mb['F']:
                k = 0
            elif stessoQ and ma['B'] is not None and ma['B'] == mb['B']:
                k = 1
            elif abs(ma['ord'] - mb['ord']) == 1:
                k = 2
            elif stessoQ:
                k = 3
            elif ma['sez'] == mb['sez']:
                k = 4 if ma['mano'] == mb['mano'] else -1
            else:
                k = 5
            K[a, b] = K[b, a] = k
    return K


def testo_in_disposizione(chiave, base):
    """Un testo di una lingua (Gaskell e Bowern, chiave del file) messo nella DISPOSIZIONE di `base` (pagine di righe con numero di parole e
    segni di paragrafo, vedi `sintassi_testi`): le stesse pagine, lo stesso numero di parole per riga, gli stessi inizi di paragrafo, ma
    parole di una lingua, scritte di seguito nell'ordine del manoscritto (pagine consecutive = testo consecutivo). Dalla base si prende solo la
    forma (numeri di parole e segni di paragrafo), non le parole."""
    import e3c95_imparabilita as e95
    tt, _ = e95.lingue()
    flusso = iter([w for r in tt[chiave] if r for w in r])
    meta = meta_di(list(base))
    out = {}
    for p in sorted(base, key=lambda q: meta[q]['ord']):
        out[p] = [(ini, [tuple(next(flusso)) for _ in ws]) for ini, ws in base[p]]
    return OrderedDict((p, out[p]) for p in sorted(out))

