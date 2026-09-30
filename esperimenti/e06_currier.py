# -*- coding: utf-8 -*-
"""Esperimento 6: i nostri strumenti ritrovano da soli le lingue A e B di Currier?

Un controllo di taratura. Negli anni Settanta Prescott Currier noto' che le
pagine del Voynich si dividono in due "lingue", A e B, con statistiche diverse.
Se dividiamo le pagine in due gruppi guardando solo le frequenze delle parole,
senza dire all'algoritmo quale pagina e' di quale lingua, dobbiamo ritrovare
la sua divisione. Se non ci riuscissimo, i numeri degli altri esperimenti
sarebbero da prendere con le molle.

Scrive risultati/e06_currier.json e risultati/e06_currier.md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE = 40
VOCI = 300


def main():
    righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    pagine, lingua, sezione = OrderedDict(), {}, {}
    for r in righe:
        pagine.setdefault(r.pagina, []).extend(p for p in r.parole if trascrizione.pulita(p))
        lingua[r.pagina], sezione[r.pagina] = r.lingua, r.sezione
    scelte = [p for p, ws in pagine.items() if len(ws) >= MIN_PAROLE and lingua[p] in ('A', 'B')]
    tutte = Counter(w for p in scelte for w in pagine[p])
    voci = [w for w, _ in tutte.most_common(VOCI)]
    X = np.array([[Counter(pagine[p])[w] / len(pagine[p]) for w in voci] for p in scelte])
    X = np.sqrt(X)                      # smorza le parole molto frequenti
    gruppi = KMeans(n_clusters=2, n_init=20, random_state=0).fit_predict(X)
    vere = np.array([1 if lingua[p] == 'B' else 0 for p in scelte])
    accordo = max((gruppi == vere).mean(), (gruppi != vere).mean())
    coordinate = PCA(n_components=2, random_state=0).fit_transform(X)
    sbagliate = [p for p, g, v in zip(scelte, gruppi, vere)
                 if (g == v) != ((gruppi == vere).mean() >= 0.5)]
    ris = {'pagine': len(scelte), 'parole_frequenti': VOCI, 'accordo': accordo,
           'pagine_in_disaccordo': [{'pagina': p, 'lingua': lingua[p], 'sezione': sezione[p]}
                                    for p in sbagliate],
           'pca': {p: [float(c[0]), float(c[1])] for p, c in zip(scelte, coordinate)},
           'lingua': {p: lingua[p] for p in scelte}}
    print('pagine %d, accordo con Currier %.1f%%, in disaccordo: %s' % (
        len(scelte), 100 * accordo, ', '.join('%s (%s)' % (p, lingua[p]) for p in sbagliate)))
    with open(os.path.join(RISULTATI, 'e06_currier.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RISULTATI, 'e06_currier.md'), 'w', encoding='utf-8') as f:
        f.write('# Esperimento 6: le lingue A e B di Currier\n\n'
                'Pagine con almeno %d parole leggibili: %d. Ogni pagina è descritta dalla frequenza '
                'delle %d parole più comuni; l\'algoritmo (k-medie, due gruppi) non sa niente della '
                'lingua.\n\n**Accordo con la divisione di Currier: %.1f%%.**\n\n'
                'Pagine messe nel gruppo sbagliato: %s.\n' % (
                    MIN_PAROLE, len(scelte), VOCI, 100 * accordo,
                    ', '.join('%s (lingua %s, sezione %s)' % (p, lingua[p], trascrizione.SEZIONI.get(sezione[p], sezione[p]))
                              for p in sbagliate) or 'nessuna'))


if __name__ == '__main__':
    main()
