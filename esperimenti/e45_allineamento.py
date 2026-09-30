# -*- coding: utf-8 -*-
"""Esperimento 45 (tecnico): si possono portare i riquadri di voynichese.com sulle immagini IIIF?

Serviva per misurare l'inchiostro delle etichette della farmacia (chiudere l'e40: etichette
scritte in sedute diverse avrebbero inchiostro diverso). Per ogni pagina della farmacia con
etichette di recipienti e frammenti: allineamento globale (scala, rapporto verticale,
spostamento; analisi/immagini.py), poi affinamento locale delle sole etichette (+-30 pixel).
Si salvano parametri e punteggi e, nella cache, le sovrapposizioni da controllare a vista.
Risultato del controllo a vista su f99r (QUADERNO, 30/09/2026): meta' circa delle etichette
cade sull'inchiostro giusto; le altre su tratti dei disegni o su parole uguali nei paragrafi.
Vedi DECISIONI.md, D-010.

Scrive risultati/e45_allineamento.json e .md.
"""
import json, os, sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import immagini as im, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOVRAPPOSIZIONI = os.path.join(QUI, '..', 'dati', 'cache', 'sovrapposizioni')
REGISTRO = os.path.join(QUI, '..', 'dati', 'immagini.json')
# pagina della ZL -> immagine IIIF (etichetta della Beinecke); solo le pagine singole: i pannelli
# pieghevoli sono accorpati in immagini composite e andrebbero ritagliati a mano
PAGINE = {'f88r': '88r', 'f99r': '99r', 'f99v': '99v', 'f100r': '100r'}


def main():
    from PIL import Image, ImageDraw
    os.makedirs(SOVRAPPOSIZIONI, exist_ok=True)
    registro = json.load(open(REGISTRO, encoding='utf-8'))
    righe_zl = trascrizione.leggi('ZL')
    ris = {}
    for foglio, etichetta in PAGINE.items():
        nome_file = registro[etichetta]['file']
        rgb = im.carica(nome_file)
        boxes = im.riquadri(foglio)
        etich = {w for r in righe_zl if r.pagina == foglio and r.tipo[0] == 'L' for w in r.parole}
        testo = {w for r in righe_zl if r.pagina == foglio and r.tipo[0] == 'P' for w in r.parole}
        al = im.allinea(rgb, boxes)
        ink = im.maschera_inchiostro(rgb)
        img = Image.open(os.path.join(im.IMMAGINI, nome_file)).convert('RGB')
        d = ImageDraw.Draw(img)
        # solo le etichette che non compaiono anche nel testo della pagina: altrimenti non si sa quale
        usate = [b for b in boxes if b[0] in etich and b[0] not in testo]
        for b in usate:
            d.rectangle(im.affina(ink, im.sull_immagine(b, al), raggio=30), outline=(0, 0, 255), width=3)
        img.save(os.path.join(SOVRAPPOSIZIONI, foglio + '_etichette.jpg'))
        ris[foglio] = dict(al, etichette=len(usate), riquadri=len(boxes))
        print(foglio, ris[foglio], flush=True)
    with open(os.path.join(RISULTATI, 'e45_allineamento.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e45 — Riquadri di voynichese.com sulle immagini IIIF (prova tecnica)', '',
           'Allineamento globale scala + spostamento per massima correlazione fra riquadri e inchiostro; '
           '"seconda" = miglior punteggio con una scala lontana più di 0,1: se è vicino al primo, la scelta '
           'non è netta. Le sovrapposizioni sono in `dati/cache/sovrapposizioni/` (non nel repository).', '',
           '| foglio | scala | spostamento | punteggio | seconda | etichette sovrapposte |', '|---|---|---|---|---|---|']
    for f, r in ris.items():
        out.append('| %s | %.2f | (%d, %d) | %.4f | %.4f | %d |' % (f, r['scala'], r['dx'], r['dy'], r['punteggio'],
                                                                   r['seconda'] or 0, r['etichette']))
    with open(os.path.join(RISULTATI, 'e45_allineamento.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
