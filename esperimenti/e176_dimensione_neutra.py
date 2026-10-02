# -*- coding: utf-8 -*-
"""Esperimento 176: come l'e173b, ma la dimensione della scrittura si misura solo sulle parole senza occorrenze delle
cinque scelte di grafia (parole neutre).

Preregistrazione: preregistrazioni/e176.md. Scrive risultati/e176_dimensione_neutra.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e135_stato_riga as e135
import e146_deriva_preferenze as e146
import e173_dimensione_scrittura as e173
import e173b_dimensione_per_lunghezza as e173b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 176
_NEUTRE = {}


def neutra(w):
    if w not in _NEUTRE:
        _NEUTRE[w] = trascrizione.pulita(w) and not any(o[0] in e146.SCELTE for o in e135.occorrenze([('x', [w])]))
    return _NEUTRE[w]


def dimensioni():
    righe = e146.righe_voynich()
    per = defaultdict(list)
    for k, (pag, _, _) in enumerate(righe):
        per[pag].append(k)
    out = OrderedDict()
    for pag, ks in per.items():
        p = os.path.join(e34.RIQUADRI, pag + '.js')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        voc = [w[0] for w in d[0]]
        vt = [(voc[e[0]], e[3]) for e in d[1]]
        zt = [(k, w) for k in ks for w in righe[k][2]]
        sm = SequenceMatcher(a=[e34.fondi(w) for w, _ in vt], b=[e34.fondi(w) for _, w in zt], autojunk=False)
        per_riga = defaultdict(list)
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                w, larg = vt[i0 + t]
                u = len(e173.D(w))
                if u and larg > 0 and neutra(zt[j0 + t][1]):
                    per_riga[zt[j0 + t][0]].append(larg / u)
        mis = {k: statistics.median(v) for k, v in per_riga.items() if len(v) >= 2}
        if len(mis) >= e173.MIN_RIGHE:
            m = statistics.median(mis.values())
            out[pag] = [(k, mis[k] / m) for k in ks if k in mis]
    return righe, out


def main():
    rnd = random.Random(SEME)
    righe, P = dimensioni()
    seqs = [[x for _, x in v] for v in P.values()]

    def auto(ss):
        a, b = [], []
        for s in ss:
            a += s[:-1]
            b += s[1:]
        return e173.pearson(a, b)
    vero1 = auto(seqs)
    nulli = []
    for _ in range(200):
        mes = []
        for s in seqs:
            s = s[:]
            rnd.shuffle(s)
            mes.append(s)
        nulli.append(auto(mes))
    z1 = (vero1 - statistics.mean(nulli)) / statistics.pstdev(nulli)
    valido = z1 > 5
    res = e146.residui(righe)
    cc = []
    for pag, v in P.items():
        for (k1, s1), (k2, s2) in zip(v, v[1:]):
            if k2 != k1 + 1 or righe[k1][1] != righe[k2][1]:
                continue
            dif = [abs(res[(f, k2)] - res[(f, k1)]) for f in e146.SCELTE if (f, k1) in res and (f, k2) in res]
            if dif:
                cc.append({'pagina': pag, 'dim': abs(s2 - s1), 'scelta': statistics.mean(dif), 'classe': e173b.classe(min(len(righe[k1][2]), len(righe[k2][2])))})
    vero = e173b.statistica(cc, [c['dim'] for c in cc])
    e173b.RIMESCOLAMENTI = 2000
    n1 = e173b.nullo(cc, lambda c: c['classe'], rnd)
    p = (1 + sum(x >= vero for x in n1)) / 2001
    esito = ('test non valido' if not valido else ('legame non meccanico (e173b confermato)' if vero > 0 and p < 0.01 else
             ('legame meccanico (e173b spiegato dalla geometria delle scelte)' if p > 0.05 else 'incerto')))
    ris = OrderedDict([('pagine', len(P)), ('righe', sum(map(len, P.values()))), ('V1', OrderedDict([('r', vero1), ('nullo', statistics.mean(nulli)), ('z', z1)])),
                       ('valido', valido), ('coppie', len(cc)), ('statistica', vero), ('p', p), ('esito', esito)])
    print('pagine %d righe %d | V1 r %.3f z %.1f | coppie %d | statistica %.3f p %.4f | %s' % (len(P), ris['righe'], vero1, z1, len(cc), vero, p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e176_dimensione_neutra.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e176 — Dimensione della scrittura su parole neutre rispetto alle scelte', '', 'Larghezza per unità EVA sulle sole parole senza occorrenze delle cinque scelte. '
           'Preregistrazione: `preregistrazioni/e176.md`.', '', '| verifica | valore |', '|---|---|',
           '| V1 correlazione fra righe consecutive (z) | %.3f (%.1f) |' % (vero1, z1), '| statistica dentro le classi di lunghezza (p) | %.3f (%.4f), coppie %d |' % (vero, p, len(cc)),
           '', 'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e176_dimensione_neutra.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
