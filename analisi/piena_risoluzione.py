# -*- coding: utf-8 -*-
"""Riquadri delle parole di voynichese.com sulle immagini IIIF della Beinecke a piena risoluzione.

Registrazione (scala e spostamento) dei riquadri sulle immagini IIIF da 1500 pixel gia' in cache (e33), per
correlazione fra una maschera d'inchiostro e la maschera dei riquadri (sviluppata su f103r, f3r, f1r, f58r).
Poi scaricamento dell'immagine a piena risoluzione e ritaglio delle parole.

Cache: dati/cache/registrazioni_iiif.json (registrazioni), dati/cache/immagini_piene/ (immagini).
"""
import json, os, sys, time, urllib.request

import numpy as np
from PIL import Image, ImageFilter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import e34_spazi_fisici as e34

CACHE = os.path.join(QUI, '..', 'dati', 'cache')
REGISTRO = os.path.join(QUI, '..', 'dati', 'immagini.json')
REG = os.path.join(CACHE, 'registrazioni_iiif.json')
PIENE = os.path.join(CACHE, 'immagini_piene')
F = 4
SCALE = np.arange(1.5, 2.31, 0.025)


def etichetta(pag):
    return pag[1:]


def maschera_inchiostro(percorso):
    im = Image.open(percorso).convert('RGB')
    hsv = np.asarray(im.convert('HSV')).astype(float)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h, w = V.shape
    perg = float(np.median(V[h // 6:5 * h // 6, w // 6:5 * w // 6]))
    chiaro = V > 0.75 * perg
    righe = np.where(chiaro.mean(axis=1) > 0.5)[0]
    col = np.where(chiaro.mean(axis=0) > 0.5)[0]
    y0, y1, x0, x1 = righe[0], righe[-1], col[0], col[-1]
    dy, dx = (y1 - y0) // 50, (x1 - x0) // 50
    dentro = np.zeros_like(chiaro)
    dentro[y0 + dy:y1 - dy, x0 + dx:x1 - dx] = True
    fondo = np.asarray(im.convert('L').filter(ImageFilter.MedianFilter(31))).astype(float)
    ink = dentro & (V < 0.7 * fondo) & ~((S > 60) & (H >= 40) & (H <= 200)) & ~(S > 150)
    return ink[:h - h % F, :w - w % F].reshape(h // F, F, w // F, F).mean(axis=(1, 3))


def registra(pag):
    """(correlazione, scala, dx, dy) dalla cornice dei riquadri ai pixel dell'immagine IIIF da 1500."""
    reg = json.load(open(REGISTRO, encoding='utf-8'))
    p = os.path.join(CACHE, 'immagini', reg[etichetta(pag)]['file'])
    small = maschera_inchiostro(p)
    bb = json.load(open(os.path.join(e34.RIQUADRI, pag + '.js'), encoding='utf-8'))[1]
    h, w = small.shape
    A = small - small.mean()
    P = (2 * h, 2 * w)
    FA = np.fft.rfft2(A, s=P)
    nA = np.linalg.norm(A)
    best = None
    for s in SCALE:
        ex = max((e[1] + e[3]) * s / F for e in bb)
        ey = max((e[2] + e[4]) * s / F for e in bb)
        if ex >= w or ey >= h:
            continue
        M = np.zeros((h, w))
        for e in bb:
            M[int(e[2] * s / F):int((e[2] + e[4]) * s / F) + 1, int(e[1] * s / F):int((e[1] + e[3]) * s / F) + 1] = 1
        B = M - M.mean()
        c = np.fft.irfft2(FA * np.conj(np.fft.rfft2(B, s=P)), s=P)[:int(h - ey), :int(w - ex)]
        k = np.unravel_index(np.argmax(c), c.shape)
        val = float(c[k] / (nA * np.linalg.norm(B)))
        if best is None or val > best[0]:
            best = (val, float(s), int(k[1] * F), int(k[0] * F))
    return best


def registrazioni():
    return json.load(open(REG, encoding='utf-8')) if os.path.exists(REG) else {}


def salva_registrazione(pag, r):
    d = registrazioni()
    d[pag] = r
    json.dump(d, open(REG, 'w', encoding='utf-8'), indent=1)


def immagine_piena(pag):
    os.makedirs(PIENE, exist_ok=True)
    reg = json.load(open(REGISTRO, encoding='utf-8'))[etichetta(pag)]
    out = os.path.join(PIENE, etichetta(pag) + '.jpg')
    if not os.path.exists(out):
        url = reg['url'].replace('/full/1500,/', '/full/full/')
        req = urllib.request.Request(url, headers={'User-Agent': 'voynich-ricerca/0.1'})
        open(out, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
        time.sleep(1)
    return out


def riquadri_pieni(pag):
    """[(parola, x0, y0, x1, y1)] nei pixel dell'immagine piena; None se non registrata."""
    r = registrazioni().get(pag)
    if not r:
        return None
    _, s, dx, dy = r
    W = Image.open(immagine_piena(pag)).size[0]
    k = W / 1500
    d = json.load(open(os.path.join(e34.RIQUADRI, pag + '.js'), encoding='utf-8'))
    voc = [v[0] for v in d[0]]
    return [(voc[e[0]], (e[1] * s + dx) * k, (e[2] * s + dy) * k, ((e[1] + e[3]) * s + dx) * k, ((e[2] + e[4]) * s + dy) * k) for e in d[1]]


if __name__ == '__main__':
    # registra e scarica le pagine indicate (o tutte quelle con riquadri e immagine singola)
    reg = json.load(open(REGISTRO, encoding='utf-8'))
    pagine = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(e34.RIQUADRI) if f.endswith('.js') and f[1:-3] in reg and 'file' in reg[f[1:-3]])
    fatte = registrazioni()
    for pag in pagine:
        if pag in fatte:
            continue
        try:
            r = registra(pag)
        except Exception as e:
            print(pag, 'errore', e, flush=True)
            continue
        salva_registrazione(pag, r)
        print(pag, 'corr %.3f scala %.3f dx %d dy %d' % r, flush=True)
