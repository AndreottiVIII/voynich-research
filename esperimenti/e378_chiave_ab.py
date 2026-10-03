# -*- coding: utf-8 -*-
"""Esperimento 378: una sostituzione dei segni (una chiave) trasforma l'erbario in lingua A nell'erbario in lingua B?
Sovrapposizione delle frequenze delle parole, ricerca locale sulle permutazioni dei segni, controllo positivo con A
cifrata da una permutazione casuale.

Preregistrazione: preregistrazioni/e378.md. Scrive risultati/e378_chiave_ab.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
DIVISIONI = 10
CASUALI = 4


def frequenze(parole):
    c = Counter(parole)
    n = sum(c.values())
    return {w: k / n for w, k in c.items()}


def sovrapp(px, py):
    if len(px) > len(py):
        px, py = py, px
    return sum(min(p, py.get(w, 0.0)) for w, p in px.items())


class Ricerca:
    def __init__(self, sorgente, bersaglio, alfabeto):
        self.alf = alfabeto
        self.idx = {s: i for i, s in enumerate(alfabeto)}
        self.tipi = [(tuple(self.idx[s] for s in w), p) for w, p in frequenze(sorgente).items()]
        self.bers = {tuple(self.idx[s] for s in w): p for w, p in frequenze(bersaglio).items()}
        self.fs = Counter(s for w in sorgente for s in w)
        self.fb = Counter(s for w in bersaglio for s in w)

    def valore(self, sigma):
        acc = defaultdict(float)
        for w, p in self.tipi:
            acc[tuple(sigma[i] for i in w)] += p
        b = self.bers
        return sum(min(p, b.get(w, 0.0)) for w, p in acc.items())

    def locale(self, sigma):
        sigma = list(sigma)
        v = self.valore(sigma)
        n = len(sigma)
        migliorato = True
        while migliorato:
            migliorato = False
            for i in range(n):
                for j in range(i + 1, n):
                    sigma[i], sigma[j] = sigma[j], sigma[i]
                    v2 = self.valore(sigma)
                    if v2 > v + 1e-12:
                        v = v2
                        migliorato = True
                    else:
                        sigma[i], sigma[j] = sigma[j], sigma[i]
        return v, sigma

    def migliore(self, rnd):
        n = len(self.alf)
        partenze = [list(range(n))]
        rs = sorted(range(n), key=lambda i: -self.fs[self.alf[i]])
        rb = sorted(range(n), key=lambda i: -self.fb[self.alf[i]])
        rank = [0] * n
        for a, b in zip(rs, rb):
            rank[a] = b
        partenze.append(rank)
        partenze += [rnd.sample(range(n), n) for _ in range(CASUALI)]
        return max((self.locale(s) for s in partenze), key=lambda x: x[0])


def main():
    rnd = random.Random(378)
    per_pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.sezione == 'H' and r.lingua in ('A', 'B'):
            ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            per_pag.setdefault((r.lingua, r.pagina), []).extend(w for w in ws if w)
    B = [w for (l, p), ws in per_pag.items() if l == 'B' for w in ws]
    pag_A = [p for (l, p) in per_pag if l == 'A']
    alfabeto = sorted({s for ws in per_pag.values() for w in ws for s in w})
    nB = len(B)
    pB = frequenze(B)
    ris = []
    scambi = Counter()
    for d in range(DIVISIONI):
        ordine = rnd.sample(pag_A, len(pag_A))
        A1, A2 = [], []
        for p in ordine:
            if len(A1) < nB:
                A1 += per_pag[('A', p)]
            elif len(A2) < nB:
                A2 += per_pag[('A', p)]
        p1, p2 = frequenze(A1), frequenze(A2)
        O_stessa, O_id = sovrapp(p1, p2), sovrapp(p1, pB)
        O_chiave, sigma = Ricerca(A1, B, alfabeto).migliore(rnd)
        for i, j in enumerate(sigma):
            if i != j:
                scambi['%s→%s' % (alfabeto[i], alfabeto[j])] += 1
        pi = rnd.sample(alfabeto, len(alfabeto))
        cod = dict(zip(alfabeto, pi))
        A2pi = [tuple(cod[s] for s in w) for w in A2]
        O_id_c = sovrapp(p1, frequenze(A2pi))
        O_chiave_c, _ = Ricerca(A1, A2pi, alfabeto).migliore(rnd)
        x = OrderedDict([('parole_A1', len(A1)), ('parole_A2', len(A2)), ('O_stessa', O_stessa), ('O_id', O_id), ('O_chiave', O_chiave),
                         ('R', (O_chiave - O_id) / (O_stessa - O_id) if O_stessa > O_id else None),
                         ('controllo_O_id', O_id_c), ('controllo_O_chiave', O_chiave_c), ('R_controllo', (O_chiave_c - O_id_c) / (O_stessa - O_id_c))])
        ris.append(x)
        print(d, json.dumps(x, default=float), flush=True)
    R = statistics.mean(x['R'] for x in ris if x['R'] is not None)
    Rc = statistics.mean(x['R_controllo'] for x in ris)
    if Rc <= 0.8:
        esito = 'la ricerca non funziona (controllo positivo fallito)'
    elif R > 0.5:
        esito = 'B è A con un\'altra chiave'
    elif R < 0.2:
        esito = 'B non è una sostituzione di A'
    else:
        esito = 'incerto'
    lung = OrderedDict([('A', statistics.mean(len(w) for (l, p), ws in per_pag.items() if l == 'A' for w in ws)), ('B', statistics.mean(len(w) for w in B))])
    out = OrderedDict([('parole_B', nB), ('alfabeto', alfabeto), ('divisioni', ris), ('O_stessa', statistics.mean(x['O_stessa'] for x in ris)),
                       ('O_id', statistics.mean(x['O_id'] for x in ris)), ('O_chiave', statistics.mean(x['O_chiave'] for x in ris)),
                       ('R', R), ('R_controllo', Rc), ('scambi_frequenti', scambi.most_common(15)), ('lunghezza_media', lung), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e378_chiave_ab.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e378 — La lingua B è la lingua A con un\'altra chiave di sostituzione?', '', 'Preregistrazione: `preregistrazioni/e378.md`. Erbario: B %d parole; A diviso in due parti di pari dimensione, 10 volte.' % nB, '',
          '| divisione | O(A1, A2) | O(A1, B) | O con la chiave migliore | R | controllo: O(A1, A2π) | controllo: O con la chiave | R controllo |', '|---|---|---|---|---|---|---|---|']
    for d, x in enumerate(ris):
        md.append('| %d | %.3f | %.3f | %.3f | %.2f | %.3f | %.3f | %.2f |' % (d, x['O_stessa'], x['O_id'], x['O_chiave'], x['R'], x['controllo_O_id'], x['controllo_O_chiave'], x['R_controllo']))
    md += ['', 'Medie: O stessa lingua %.3f, O fra A e B %.3f, O con la chiave %.3f; R %.2f; R controllo %.2f.' % (out['O_stessa'], out['O_id'], out['O_chiave'], R, Rc),
           'Lunghezza media delle parole (segni): A %.2f, B %.2f.' % (lung['A'], lung['B']),
           'Scambi più frequenti nella chiave migliore (su %d divisioni): %s.' % (DIVISIONI, ', '.join('%s (%d)' % t for t in scambi.most_common(15))), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e378_chiave_ab.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
