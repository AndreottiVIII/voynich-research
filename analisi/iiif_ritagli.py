# -*- coding: utf-8 -*-
"""Ritagli delle pagine del manoscritto per i controlli sulle immagini (e3c94).

    python analisi/iiif_ritagli.py griglia PAGINA [x0 y0 x1 y1]
        salva nello scratch un'immagine della pagina (o di una sua parte) a 1.500 pixel con una griglia ogni 50 pixel,
        per trovare a vista le coordinate di una parola;
    python analisi/iiif_ritagli.py scarica
        scarica alla risoluzione piena le regioni di risultati/e3c94_ritagli.json dal server IIIF di Yale
        (pct:x,y,w,h/full/0/default.jpg) in dati/cache/iiif_e3c94/; salta i file già presenti.

Le coordinate di risultati/e3c94_ritagli.json sono in pixel dell'immagine a 1.500 pixel di larghezza
(dati/cache/immagini/).
"""
import json, os, sys, time, urllib.request

from PIL import Image, ImageDraw

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, '..')
IMMAGINI = os.path.join(RADICE, 'dati', 'cache', 'immagini')
CACHE = os.path.join(RADICE, 'dati', 'cache', 'iiif_e3c94')
RITAGLI = os.path.join(RADICE, 'risultati', 'e3c94_ritagli.json')
SCRATCH = os.environ.get('SCRATCH', os.path.join(RADICE, 'esecuzioni'))


def griglia(pagina, box=None):
    im = Image.open(os.path.join(IMMAGINI, pagina + '.jpg')).convert('RGB')
    x0, y0, x1, y1 = box or (0, 0) + im.size
    c = im.crop((x0, y0, x1, y1))
    scala = 1 if box else 0.5
    if box:
        scala = min(3.0, 1400 / (x1 - x0))
    c = c.resize((int(c.width * scala), int(c.height * scala)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    passo = 50 if box else 100
    for x in range((x0 // passo + 1) * passo, x1, passo):
        X = int((x - x0) * scala)
        d.line([(X, 0), (X, c.height)], fill=(255, 0, 0) if x % 100 == 0 else (255, 160, 160), width=1)
        d.text((X + 2, 2), str(x), fill=(255, 0, 0))
    for y in range((y0 // passo + 1) * passo, y1, passo):
        Y = int((y - y0) * scala)
        d.line([(0, Y), (c.width, Y)], fill=(0, 0, 255) if y % 100 == 0 else (160, 160, 255), width=1)
        d.text((2, Y + 2), str(y), fill=(0, 0, 255))
    f = os.path.join(SCRATCH, 'griglia_%s_%d_%d.jpg' % (pagina, x0, y0))
    c.save(f, quality=90)
    print(f)


def scarica():
    os.makedirs(CACHE, exist_ok=True)
    rit = json.load(open(RITAGLI, encoding='utf-8'))
    for k, v in rit.items():
        f = os.path.join(CACHE, k + '.jpg')
        if os.path.exists(f):
            continue
        w, h = Image.open(os.path.join(IMMAGINI, v['immagine'])).size
        x0, y0, x1, y1 = v['box']
        pct = 'pct:%.3f,%.3f,%.3f,%.3f' % (100 * x0 / w, 100 * y0 / h, 100 * (x1 - x0) / w, 100 * (y1 - y0) / h)
        url = 'https://collections.library.yale.edu/iiif/2/%s/%s/full/0/default.jpg' % (v['iiif_id'], pct)
        req = urllib.request.Request(url, headers={'User-Agent': 'voynich-research (image spot check)'})
        with urllib.request.urlopen(req, timeout=60) as r, open(f, 'wb') as o:
            o.write(r.read())
        print(k, url, os.path.getsize(f), Image.open(f).size, flush=True)
        time.sleep(1)


if __name__ == '__main__':
    if sys.argv[1] == 'griglia':
        griglia(sys.argv[2], tuple(int(x) for x in sys.argv[3:7]) if len(sys.argv) > 3 else None)
    else:
        scarica()
