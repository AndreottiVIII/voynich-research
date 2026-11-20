# -*- coding: utf-8 -*-
"""Testi per ia09 (modulo di supporto, non e' un esperimento): caricamento dei testi in pagine, pieghe, rimescolamenti.

Una pagina e' una lista di righe (inizio_paragrafo, [parola, ...]); una parola e' una tupla di segni (stringhe). E' la stessa
forma di ia01 (`ia01_giudice_neurale`), che si importa e non si modifica. Questo modulo non genera nulla e non legge il
Voynich da se': per il Voynich e i libri v21 chiama le funzioni di ia01 (`contesto`, `libro`).
"""
import os
import random
import sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402

NF = G.NF
MIN_PAROLE = G.MIN_PAROLE


def pieghe(nomi, seme=3961):
    """Stesse pieghe di ia01: i nomi ordinati, mescolati con random.Random(3961), a giro in NF pieghe."""
    ordine = sorted(nomi)
    random.Random(seme).shuffle(ordine)
    return {p: i % NF for i, p in enumerate(ordine)}


def filtra(pagine):
    """Tiene le pagine con almeno MIN_PAROLE parole (come ia01.contesto)."""
    return OrderedDict((p, rows) for p, rows in sorted(pagine.items()) if sum(len(ws) for _, ws in rows) >= MIN_PAROLE)


def testo_vere():
    """Le pagine vere di ia01 (nel Voynich la trascrizione ZL; con SOLO_CONTROLLI il latino di prova), con pieghe e (sezione,
    lingua) di ogni pagina."""
    c = G.contesto()
    return dict(pagine=c['vere'], fold=dict(c['fold']), tipo=dict(c['tipo']))


def testo_libro(nome):
    """Un libro v21 (o di prova): le sue pagine che esistono anche fra le vere, con le pieghe delle vere."""
    c = G.contesto()
    lib = G.libro(nome)
    pagine = OrderedDict((p, lib[p]) for p in c['vere'] if p in lib)
    return dict(pagine=pagine, fold={p: c['fold'][p] for p in pagine}, tipo=None)


def testo_ts(seme):
    """Timm e Schinner (generatore esterno, nella cache dati): pagine di 29 righe, i glifi EVA fusi come in e3c95."""
    sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
    import misure
    import e337_posizione as e337
    dividi = misure.divisore(misure.GLIFI_EVA)
    pagine = OrderedDict()
    for i, righe in enumerate(e337.pagine_ts(seme)):
        pagine['T%d_%03d' % (seme, i)] = [(False, [tuple(dividi(w)) for w in r]) for r in righe if r]
    pagine = filtra(pagine)
    return dict(pagine=pagine, fold=pieghe(pagine), tipo=None)


def testo_lingua(chiave, righe_pagina, n_pagine, prefisso):
    """Una lingua di Gaskell e Bowern messa in pagine (come ia01.carica_latino): un paragrafo ogni 8 righe."""
    import e3c95_imparabilita as e95
    tt, _ = e95.lingue()
    righe = [r for r in tt[chiave] if r]
    pagine = OrderedDict()
    for i in range(n_pagine):
        rows = righe[i * righe_pagina:(i + 1) * righe_pagina]
        if not rows:
            break
        pagine['%s%03d' % (prefisso, i)] = [(j % 8 == 0, [tuple(w) for w in r]) for j, r in enumerate(rows)]
    pagine = filtra(pagine)
    return dict(pagine=pagine, fold=pieghe(pagine), tipo=None)


CHIAVE_INGLESE = 'Historical - English - Literary - NT (KJV).txt'
CHIAVE_ITALIANO = 'Historical - Italian - Literary - NT - Diodati.txt'
CHIAVE_LATINO = "Historical - Latin - Technical - Pliny's Natural History.txt"


def testo_latino():
    n = int(os.environ.get('PAGINE', 196))
    return testo_lingua(CHIAVE_LATINO, int(os.environ.get('RIGHE_PAGINA', 23)), n, 'L')


def testo_inglese():
    n = int(os.environ.get('PAGINE', 196))
    return testo_lingua(CHIAVE_INGLESE, int(os.environ.get('RIGHE_PAGINA_EN', 14)), n, 'E')


def testo_italiano():
    n = int(os.environ.get('PAGINE', 196))
    return testo_lingua(CHIAVE_ITALIANO, int(os.environ.get('RIGHE_PAGINA_EN', 14)), n, 'I')


def rimescola_testo(pagine, seme):
    """Controllo negativo: tutte le parole del testo mescolate fra tutte le pagine; stesse righe, stesse pagine, stesse lunghezze."""
    rnd = random.Random(seme)
    tutte = [w for rows in pagine.values() for _, ws in rows for w in ws]
    rnd.shuffle(tutte)
    out, k = OrderedDict(), 0
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            nr.append((ini, tutte[k:k + len(ws)]))
            k += len(ws)
        out[p] = nr
    return out


def rimescola_pagina(pagine, seme):
    """Le parole mescolate dentro ogni pagina (fra le righe), righe e lunghezze invariate: tiene la 'materia' della pagina
    (le parole che ci sono) e rompe l'ordine."""
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in pagine.items():
        tutte = [w for _, ws in rows for w in ws]
        rnd.shuffle(tutte)
        nr, k = [], 0
        for ini, ws in rows:
            nr.append((ini, tutte[k:k + len(ws)]))
            k += len(ws)
        out[p] = nr
    return out
