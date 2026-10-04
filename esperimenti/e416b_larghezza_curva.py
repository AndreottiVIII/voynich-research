# -*- coding: utf-8 -*-
"""Esperimento 416b: come l'e416, ma la larghezza attesa di una riga non e' n ** beta: segue una curva misurata sul Voynich
(12 nodi: log parole su mediana di pagina -> log larghezza su mediana di pagina). Secondo e ultimo tentativo su questa
strada. Scrive i parametri della v19.

    PROCESSI=8 python esegui.py e416b
    python esperimenti/e416b_larghezza_curva.py --prova

Preregistrazione: preregistrazioni/e416.md, integrazione "e416b". Scrive risultati/e416b_larghezza_curva.json e .md e
voynichizzatore/pezzi_parametri_v19.json.
"""
import json, math, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import e416_larghezza_righe as e416

NODI = 12


def modello(voy):
    pt = sorted(e416.punti(voy))
    xs, ys = [], []
    for k in range(NODI):
        pezzo = pt[k * len(pt) // NODI:(k + 1) * len(pt) // NODI]
        x, y = sum(a for a, _ in pezzo) / len(pezzo), sum(b for _, b in pezzo) / len(pezzo)
        if xs and x <= xs[-1] + 1e-9:          # molte righe con lo stesso numero di parole: si fondono nel nodo precedente
            ys[-1] = (ys[-1] + y) / 2
            continue
        xs.append(x)
        ys.append(y)
    return (tuple(xs), tuple(ys))


def f(curva, x):
    xs, ys = curva
    if x <= xs[0]:
        return ys[0]
    for k in range(1, len(xs)):
        if x <= xs[k]:
            return ys[k - 1] + (ys[k] - ys[k - 1]) * (x - xs[k - 1]) / (xs[k] - xs[k - 1])
    return ys[-1]


def descrivi(curva):
    return 'curva a %d nodi: ' % len(curva[0]) + '; '.join('%.2f -> %.2f' % (math.exp(x), math.exp(y)) for x, y in zip(*curva))


def larghezze(rr, curva):
    pt = e416.punti(rr)
    res = [y - f(curva, x) for x, y in pt]
    m = sum(res) / len(res)
    return OrderedDict([('righe', len(pt)),
                        ('caratteri oltre 1,25', sum(y > math.log(1.25) for _, y in pt) / len(pt)),
                        ('caratteri oltre 1,5', sum(y > math.log(1.5) for _, y in pt) / len(pt)),
                        ('parole oltre 1,5', sum(x > math.log(1.5) for x, _ in pt) / len(pt)),
                        ('residui', math.sqrt(sum((r - m) ** 2 for r in res) / len(res))),
                        ('pendenza propria', e416.pendenza(rr))])


def parametri(w, curva):
    import pezzi
    x = json.load(open(pezzi.PARAMETRI % 'v17', encoding='utf-8'), object_pairs_hook=OrderedDict)
    if w:
        x['pesi_disposizione'] = OrderedDict(x['pesi_disposizione'], larghezza=w, larghezza_curva=[list(curva[0]), list(curva[1])])
        x['origine'] = 'v17 con la larghezza delle righe in caratteri nella disposizione, attesa da una curva (e416b)'
    return x


e416.modello, e416.descrivi, e416.larghezze, e416.parametri = modello, descrivi, larghezze, parametri
e416.NOME, e416.VERS, e416.TITOLO = 'e416b_larghezza_curva', 'v19', 'e416b — La larghezza delle righe: attesa da una curva'
e416.PREREG = 'preregistrazioni/e416.md` (integrazione e416b'

if __name__ == '__main__':
    e416.main(prova='--prova' in sys.argv)
