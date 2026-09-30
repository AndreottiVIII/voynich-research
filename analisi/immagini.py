# -*- coding: utf-8 -*-
"""Immagini della Beinecke e riquadri per parola di voynichese.com.

I riquadri (repository di Rozanova e Temerev, voynichese_boxes/*.js) stanno in un sistema
di coordinate largo circa 600 pixel; le immagini IIIF (e33) hanno 1.500 pixel e margini, e
i fogli pieghevoli sono accorpati in immagini composite. allinea() trova scala e
spostamento che portano i riquadri sull'immagine, massimizzando la correlazione fra la
maschera dei riquadri e la maschera dell'inchiostro (pixel scuri e poco saturi). Tutto e'
deterministico: griglia fissa di scale, correlazione con FFT.
"""
import json, os

import numpy as np
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
RIQUADRI = os.path.join(QUI, '..', 'dati', 'cache', 'sorgenti', 'voynich-units', 'morphometry_voynichese',
                        'voynichese_boxes')
IMMAGINI = os.path.join(QUI, '..', 'dati', 'cache', 'immagini')
RIDUZIONE = 4          # la correlazione si fa a 1/4 della risoluzione, per velocita'


def riquadri(foglio):
    """[(parola, x, y, w, h)] nell'ordine di lettura di voynichese.com."""
    d = json.load(open(os.path.join(RIQUADRI, foglio + '.js'), encoding='utf-8'))
    voc = [w[0] for w in d[0]]
    return [(voc[e[0]], e[1], e[2], e[3], e[4]) for e in d[1]]


def carica(nome_file):
    return np.asarray(Image.open(os.path.join(IMMAGINI, nome_file)).convert('RGB')).astype(np.float32)


def maschera_inchiostro(rgb):
    """Inchiostro della scrittura: scuro rispetto alla carta e poco saturo (esclude i colori
    dei disegni). Soglia relativa alla mediana dell'immagine, quindi senza parametri da tarare
    per foglio."""
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    carta = np.median(lum)
    return (lum < 0.72 * carta) & (sat < 0.35 * carta)


def _riduci(m, k):
    h, w = m.shape[0] // k * k, m.shape[1] // k * k
    return m[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def allinea(rgb, boxes, scale=np.arange(1.6, 3.61, 0.02), rapporti=(1.0,)):
    """Scala s, rapporto r e spostamento (dx, dy) tali che x_img = s * x_box + dx e
    y_img = s * r * y_box + dy. Restituisce anche il punteggio (correlazione normalizzata)
    della combinazione migliore e della migliore con scala lontana piu' di 0,1."""
    ink = _riduci(maschera_inchiostro(rgb).astype(np.float32), RIDUZIONE)
    ink = ink - ink.mean()
    H, W = ink.shape
    F_ink = np.fft.rfft2(ink, s=(2 * H, 2 * W))
    risultati = []
    for s, r in [(s, r) for s in scale for r in rapporti]:
        k = s / RIDUZIONE
        ky = k * r
        mh = int(max(y + h for _, _, y, _, h in boxes) * ky) + 2
        mw = int(max(x + w for _, x, _, w, _ in boxes) * k) + 2
        if mh >= H or mw >= W:
            continue
        m = np.zeros((mh, mw), np.float32)
        for _, x, y, w, h in boxes:
            m[int(y * ky):int((y + h) * ky) + 1, int(x * k):int((x + w) * k) + 1] = 1
        m -= m.mean()
        corr = np.fft.irfft2(F_ink * np.conj(np.fft.rfft2(m, s=(2 * H, 2 * W))), s=(2 * H, 2 * W))[:H - mh, :W - mw]
        i = np.unravel_index(np.argmax(corr), corr.shape)
        punteggio = corr[i] / (np.linalg.norm(m) * np.linalg.norm(ink) + 1e-9)
        risultati.append((float(punteggio), float(s), int(i[1]) * RIDUZIONE, int(i[0]) * RIDUZIONE, float(r)))
    risultati.sort(reverse=True)
    migliore = risultati[0]
    # la seconda scala "diversa" (oltre 0,1 dalla migliore): dice quanto e' netta la scelta
    altre = [r for r in risultati if abs(r[1] - migliore[1]) > 0.1]
    return {'scala': migliore[1], 'rapporto': migliore[4], 'dx': migliore[2], 'dy': migliore[3], 'punteggio': migliore[0],
            'seconda': altre[0][0] if altre else None}


def sull_immagine(box, al):
    _, x, y, w, h = box
    s, sy = al['scala'], al['scala'] * al.get('rapporto', 1.0)
    return (int(s * x + al['dx']), int(sy * y + al['dy']), int(s * (x + w) + al['dx']), int(sy * (y + h) + al['dy']))


def affina(ink, rett, raggio=12):
    """Sposta il riquadro di al massimo `raggio` pixel dove contiene piu' inchiostro."""
    x0, y0, x1, y1 = rett
    H, W = ink.shape
    migliore, spost = -1, (0, 0)
    for dy in range(-raggio, raggio + 1, 2):
        for dx in range(-raggio, raggio + 1, 2):
            a, b, c, d = max(0, y0 + dy), min(H, y1 + dy), max(0, x0 + dx), min(W, x1 + dx)
            if b <= a or d <= c:
                continue
            v = ink[a:b, c:d].sum()
            if v > migliore:
                migliore, spost = v, (dx, dy)
    return (x0 + spost[0], y0 + spost[1], x1 + spost[0], y1 + spost[1])
