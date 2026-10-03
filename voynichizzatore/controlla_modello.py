# -*- coding: utf-8 -*-
"""Pannello veloce di statistiche di base (pochi secondi): Voynich contro un testo generato. Serve a far tornare le cose
semplici prima di misurare con i discriminatori.

    python voynichizzatore/controlla_modello.py [seme]
"""
import os, statistics, sys
from collections import Counter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure, trascrizione

D = misure.divisore(misure.GLIFI_EVA)


def pannello(rr):
    rr = [(p, ini, [w for w in ws if trascrizione.pulita(w)]) for p, ini, ws in rr]
    per = {}
    for p, _, ws in rr:
        per.setdefault(p, []).extend(ws)
    pagine = [v for v in per.values() if len(v) >= 40]
    glob = Counter(w for v in per.values() for w in v)
    n = sum(glob.values())
    cp = [(a, b) for _, _, ws in rr for a, b in zip(ws, ws[1:])]
    ccp = Counter(cp)
    L = [len(D(w)) for v in per.values() for w in v]
    fin = lambda w: D(w)[-1]
    ini_fin = Counter((fin(a), fin(b)) for a, b in cp)
    fa, fb = Counter(fin(a) for a, _ in cp), Counter(fin(b) for _, b in cp)
    mi = sum(c / len(cp) * __import__('math').log2(c * len(cp) / (fa[a] * fb[b])) for (a, b), c in ini_fin.items())
    prime = [len(D(w)) for _, ini, ws in rr if ini for w in ws]
    return {
        'tipi/parole pagina': statistics.mean(len(set(v)) / len(v) for v in pagine),
        'uniche pagina': statistics.mean(sum(c == 1 for c in Counter(v).values()) / len(v) for v in pagine),
        'hapax/token': sum(c == 1 for c in glob.values()) / n,
        'tipi': len(glob),
        'lunghezza': statistics.mean(L),
        'dev lunghezza': statistics.pstdev(L),
        'parole 1-2 segni': sum(x <= 2 for x in L) / len(L),
        'lunghezza prime righe': statistics.mean(prime) if prime else 0,
        'coppie identiche': sum(a == b for a, b in cp) / len(cp),
        'coppie viste 2+': sum(ccp[x] >= 2 for x in cp) / len(cp),
        'MI finale-finale': mi,
        'quota daiin': glob['daiin'] / n,
        'quota chedy': glob['chedy'] / n,
    }


def confronta(rr, nome='generato'):
    import e293_banco as e293
    v, g = pannello(e293.voynich_rr()), pannello(rr)
    for k in v:
        print('%-22s Voynich %8.4f   %s %8.4f' % (k, v[k], nome, g[k]))


if __name__ == '__main__':
    import modello
    confronta(modello.genera(int(sys.argv[1]) if len(sys.argv) > 1 else 1), 'modello')
