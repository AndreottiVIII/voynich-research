# -*- coding: utf-8 -*-
"""Dati di ia29 ("immagini e vocabolario della pagina"): inventario delle immagini del Voynich, riquadri delle parole,
metadati delle pagine (sezione, lingua A/B, mano, fascicolo, bifoglio, posizione) e parole di ogni pagina.

Inventario (verificato il 22/11/2026):
- `dati/cache/voynichese_immagini/<foglio>.jpg`: 223 immagini "large" di voynichese.com (circa 636 x 900 pixel, a colori), nella stessa cornice dei
  riquadri delle parole (`dati/cache/sorgenti/voynich-units/morphometry_voynichese/voynichese_boxes/<foglio>.js`, 223 file): sono LA fonte principale,
  perche' i riquadri combaciano esattamente e il testo si puo' cancellare. Derivano dalle riproduzioni della Beinecke (impronte in
  `dati/cache/voynichese_immagini.sha256`).
- `dati/cache/immagini/*.jpg`: 212 immagini IIIF della Beinecke (Yale, manifest 2002046, larghezza 1500; elenco e impronte in `dati/immagini.json`;
  alcune sono "aperture" a due pagine o pezzi di pagina). Sul manifest: "Access: Public"; "Rights: The use of this image may be subject to the
  copyright law of the United States ... The person using the image is liable for any infringement". Si usano per ricerca, mai ridistribuite.
- `dati/cache/registrazioni_iiif.json`: per 169 pagine, registrazione (correlazione, scala, dx, dy) dei riquadri sull'immagine IIIF da 1500 pixel
  (analisi/piena_risoluzione.py); `dati/cache/immagini_piene/`: 3 immagini a piena risoluzione (non servono).
- `dati/cache/disegni_e190.json`: 17 caratteristiche a mano dei disegni dell'erbario (e190). Non si usano qui.

Nessuna funzione di questo modulo scrive parole o immagini in `risultati/`.
"""
import json, os, random, re, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione  # noqa: E402

RADICE = os.path.join(QUI, '..')
CACHE = os.path.join(RADICE, 'dati', 'cache')
IMG_VOY = os.path.join(CACHE, 'voynichese_immagini')
RIQUADRI = os.path.join(CACHE, 'sorgenti', 'voynich-units', 'morphometry_voynichese', 'voynichese_boxes')
IMG_IIIF = os.path.join(CACHE, 'immagini')
REG_IMMAGINI = os.path.join(RADICE, 'dati', 'immagini.json')
REG_IIIF = os.path.join(CACHE, 'registrazioni_iiif.json')
ZL = os.path.join(RADICE, 'dati', 'trascrizioni', 'ZL3b-n.txt')
MIN_PAROLE = 60            # pagine con almeno 60 parole pulite entrano nel campione (preregistrato)
SEZIONI_SENZA_DISEGNO = ('T',)


def intestazioni():
    """Variabili IVTFF delle pagine, nell'ordine del file (= ordine di rilegatura): Q fascicolo, B bifoglio, I tipo di illustrazione,
    H mano, L lingua. Solo metadati: nessuna parola."""
    out = OrderedDict()
    for l in open(ZL, encoding='latin-1'):
        l = l.rstrip('\n')
        m = trascrizione._PAGINA.match(l)
        if m and not trascrizione._LOCUS.match(l):
            out[m.group(1)] = dict(trascrizione._VAR.findall(m.group(2) or ''))
    return out


def righe_voynich(solo_controlli):
    """Righe di testo corrente: dict(pagina, sezione, lingua, mano, n, parole). Con solo_controlli le parole sono None (si tiene la disposizione)."""
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            out.append(dict(pagina=r.pagina, sezione=r.sezione or '?', lingua=r.lingua or '?', mano=r.mano or '?', n=len(ps),
                            parole=None if solo_controlli else ps))
    return out


def latino_nel_layout(righe, seme, I7):
    """Parole latine (Macer, Plinio, Plinio abbreviato di Gaskell e Bowern) nella disposizione data, come ia07 in modalita' controlli, ma con
    punti di partenza casuali nei flussi (seme): ogni seme e' una "replica" senza alcun legame con i disegni."""
    from itertools import islice
    rnd = random.Random(seme)
    flussi = I7.latino()
    flussi = {k: islice(v, rnd.randrange(0, 40000), None) for k, v in flussi.items()}
    out = []
    for x in righe:
        f = 'erbario A' if (x['sezione'] == 'H' and x['lingua'] == 'A') else x['lingua'] if x['lingua'] in ('A', 'B') else '?'
        y = dict(x)
        y['parole'] = [next(flussi[f]) for _ in range(x['n'])]
        out.append(y)
    return out


def pagine_con_parole(righe):
    """pagina -> lista di parole (in ordine)."""
    out = OrderedDict()
    for x in righe:
        out.setdefault(x['pagina'], []).extend(x['parole'])
    return out


def riquadri_voynichese(pag):
    """Riquadri (x0, y0, x1, y1) nella cornice delle immagini di voynichese.com; None se non c'e' il file."""
    p = os.path.join(RIQUADRI, pag + '.js')
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    return [(e[1], e[2], e[1] + e[3], e[2] + e[4]) for e in d[1]]


def percorso_voynichese(pag):
    p = os.path.join(IMG_VOY, pag + '.jpg')
    return p if os.path.exists(p) else None


def registrazioni_iiif():
    return json.load(open(REG_IIIF, encoding='utf-8')) if os.path.exists(REG_IIIF) else {}


def percorso_iiif(pag):
    """Immagine IIIF da 1500 pixel della pagina (solo se la pagina ha una registrazione dei riquadri)."""
    reg = registrazioni_iiif()
    if pag not in reg:
        return None
    r = json.load(open(REG_IMMAGINI, encoding='utf-8')).get(pag[1:])
    if not r or 'file' not in r:
        return None
    p = os.path.join(IMG_IIIF, r['file'])
    return p if os.path.exists(p) else None


def riquadri_iiif(pag):
    """Riquadri nei pixel dell'immagine IIIF da 1500 (registrazione: x' = x * scala + dx)."""
    r = registrazioni_iiif().get(pag)
    bb = riquadri_voynichese(pag)
    if not r or bb is None:
        return None
    _, s, dx, dy = r
    return [(x0 * s + dx, y0 * s + dy, x1 * s + dx, y1 * s + dy) for x0, y0, x1, y1 in bb]


def mascherata(im, riquadri, margine=3, anello=8):
    """Immagine PIL RGB con i riquadri del testo coperti dal colore mediano della pergamena attorno (per canale)."""
    from PIL import Image
    a = np.asarray(im.convert('RGB')).copy()
    h, w, _ = a.shape
    for x0, y0, x1, y1 in riquadri:
        X0, Y0, X1, Y1 = int(max(0, x0 - margine)), int(max(0, y0 - margine)), int(min(w, x1 + margine + 1)), int(min(h, y1 + margine + 1))
        if X1 - X0 < 1 or Y1 - Y0 < 1:
            continue
        A0, B0, A1, B1 = max(0, X0 - anello), max(0, Y0 - anello), min(w, X1 + anello), min(h, Y1 + anello)
        fin = a[B0:B1, A0:A1].reshape(-1, 3)
        dentro = np.zeros((B1 - B0, A1 - A0), bool)
        dentro[Y0 - B0:Y1 - B0, X0 - A0:X1 - A0] = True
        fuori = fin[~dentro.reshape(-1)]
        if len(fuori) < 10:
            fuori = fin
        a[Y0:Y1, X0:X1] = np.median(fuori, axis=0).astype(np.uint8)
    return Image.fromarray(a)


def cornice_vuota(im, frazione=0.10):
    """Controllo "ambientale": la pagina (gia' mascherata) con tutto il centro coperto dal colore mediano della cornice. Il modello vede solo i margini
    (pergamena, macchie, bordo della scansione, qualche tratto che esce dal disegno): se il vocabolario "segue" anche questo, il legame passa dalla sessione o dalla
    conservazione e non dal disegno."""
    from PIL import Image
    a = np.asarray(im.convert('RGB')).copy()
    h, w, _ = a.shape
    y0, y1, x0, x1 = int(h * frazione), int(h * (1 - frazione)), int(w * frazione), int(w * (1 - frazione))
    fr = np.ones((h, w), bool)
    fr[y0:y1, x0:x1] = False
    a[y0:y1, x0:x1] = np.median(a[fr], axis=0).astype(np.uint8)
    return Image.fromarray(a)


def elenco_pagine(solo_controlli, righe=None):
    """Elenco ordinato delle pagine del campione principale con i loro attributi.
    Criteri (preregistrati): pagina con immagine e riquadri di voynichese.com, tipo di illustrazione diverso da T (solo testo), almeno MIN_PAROLE parole pulite.
    Restituisce lista di dict(pagina, pos, sezione, lingua, mano, fascicolo, bifoglio, n)."""
    hdr = intestazioni()
    righe = righe if righe is not None else righe_voynich(solo_controlli)
    n = OrderedDict()
    for x in righe:
        n[x['pagina']] = n.get(x['pagina'], 0) + x['n']
    out = []
    for pos, (pag, v) in enumerate(hdr.items()):
        if pag not in n or n[pag] < MIN_PAROLE or v.get('I') in SEZIONI_SENZA_DISEGNO:
            continue
        if percorso_voynichese(pag) is None or riquadri_voynichese(pag) is None:
            continue
        out.append(dict(pagina=pag, pos=pos, sezione=v.get('I', '?'), lingua=v.get('L') or '?', mano=v.get('H') or '?',
                        fascicolo=v.get('Q', '?'), bifoglio=v.get('Q', '?') + v.get('B', '?'), n=n[pag]))
    return out
