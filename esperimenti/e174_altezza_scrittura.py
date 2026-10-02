# -*- coding: utf-8 -*-
"""Esperimento 174: replica dell'e173b con l'altezza dei riquadri delle parole basse (senza aste ne' code).

Preregistrazione: preregistrazioni/e174.md. Scrive risultati/e174_altezza_scrittura.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146
import e173_dimensione_scrittura as e173
import e173b_dimensione_per_lunghezza as e173b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 174
BASSI = {'a', 'e', 'i', 'n', 'o', 'r', 's', 'ch', 'sh', 'ee'}
D = misure.divisore(misure.GLIFI_EVA)


def bassa(w):
    u = D(w)
    return bool(u) and all(x in BASSI for x in u)


def altezze():
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
        vt = [(voc[e[0]], e[4] if len(e) > 4 else 0) for e in d[1]]
        zt = [(k, w) for k in ks for w in righe[k][2]]
        sm = SequenceMatcher(a=[e34.fondi(w) for w, _ in vt], b=[e34.fondi(w) for _, w in zt], autojunk=False)
        per_riga = defaultdict(list)
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                w, alt = vt[i0 + t]
                if alt > 0 and bassa(w):
                    per_riga[zt[j0 + t][0]].append(alt)
        mis = {k: statistics.median(v) for k, v in per_riga.items() if len(v) >= 2}
        if len(mis) >= e173.MIN_RIGHE:
            m = statistics.median(mis.values())
            out[pag] = [(k, mis[k] / m) for k in ks if k in mis]
    return righe, out


def main():
    rnd = random.Random(SEME)
    righe, P = altezze()
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
    esito = 'test non valido' if not valido else ('replicato' if vero > 0 and p < 0.01 else ('non replicato' if p > 0.05 else 'incerto'))
    ris = OrderedDict([('pagine', len(P)), ('righe', sum(map(len, P.values()))), ('V1', OrderedDict([('r', vero1), ('nullo', statistics.mean(nulli)), ('z', z1)])),
                       ('valido', valido), ('coppie', len(cc)), ('statistica', vero), ('p', p), ('esito', esito)])
    print('pagine %d righe %d | V1 r %.3f z %.1f | coppie %d | statistica %.3f p %.4f | %s' % (len(P), ris['righe'], vero1, z1, len(cc), vero, p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e174_altezza_scrittura.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e174 — Replica dell\'e173b con l\'altezza della scrittura', '', 'Altezza dei riquadri delle parole senza aste né code, mediana per riga, normalizzata sulla pagina. '
           'Preregistrazione: `preregistrazioni/e174.md`.', '', '| verifica | valore |', '|---|---|',
           '| V1 correlazione fra righe consecutive (z) | %.3f (%.1f) |' % (vero1, z1), '| statistica dentro le classi di lunghezza (p) | %.3f (%.4f), coppie %d |' % (vero, p, len(cc)),
           '', 'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e174_altezza_scrittura.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
