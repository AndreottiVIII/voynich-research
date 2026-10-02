# -*- coding: utf-8 -*-
"""Esperimento 173: dimensione della scrittura per riga (larghezza del riquadro per unita' EVA, voynichese.com) e
cambio delle scelte di grafia fra righe consecutive.

Preregistrazione: preregistrazioni/e173.md. Scrive risultati/e173_dimensione_scrittura.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI_V1, RIMESCOLAMENTI = 173, 200, 2000
MIN_PAROLE, MIN_RIGHE = 3, 8
D = misure.divisore(misure.GLIFI_EVA)


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
                u = len(D(w))
                if u and larg > 0:
                    per_riga[zt[j0 + t][0]].append(larg / u)
        mis = {k: statistics.median(v) for k, v in per_riga.items() if len(v) >= MIN_PAROLE}
        if len(mis) >= MIN_RIGHE:
            m = statistics.median(mis.values())
            out[pag] = [(k, mis[k] / m) for k in ks if k in mis]
    return righe, out


def spearman(a, b):
    def ranghi(x):
        o = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        for pos, i in enumerate(o):
            r[i] = pos
        return r
    ra, rb = ranghi(a), ranghi(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def pearson(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else 0.0


def main():
    rnd = random.Random(SEME)
    righe, P = dimensioni()
    # V1
    def auto(seqs):
        a, b = [], []
        for s in seqs:
            a += s[:-1]
            b += s[1:]
        return pearson(a, b)
    seqs = [[x for _, x in v] for v in P.values()]
    vero = auto(seqs)
    nulli = []
    for _ in range(RIMESCOLAMENTI_V1):
        mes = []
        for s in seqs:
            s = s[:]
            rnd.shuffle(s)
            mes.append(s)
        nulli.append(auto(mes))
    z1 = (vero - statistics.mean(nulli)) / statistics.pstdev(nulli)
    valido = z1 > 5
    print('pagine %d, righe %d | V1 r %.3f (nullo %.3f, z %.1f) | valido %s' % (len(P), sum(map(len, P.values())), vero, statistics.mean(nulli), z1, valido), flush=True)
    res = e146.residui(righe)
    coppie = []
    for pag, v in P.items():
        for (k1, s1), (k2, s2) in zip(v, v[1:]):
            if k2 != k1 + 1 or righe[k1][1] != righe[k2][1]:
                continue
            dif = [abs(res[(f, k2)] - res[(f, k1)]) for f in e146.SCELTE if (f, k1) in res and (f, k2) in res]
            if dif:
                coppie.append((pag, abs(s2 - s1), statistics.mean(dif)))
    rho = spearman([c[1] for c in coppie], [c[2] for c in coppie])
    per_pag = defaultdict(list)
    for i, c in enumerate(coppie):
        per_pag[c[0]].append(i)
    nulli2 = []
    for _ in range(RIMESCOLAMENTI):
        dd = [c[1] for c in coppie]
        for idx in per_pag.values():
            vv = [dd[i] for i in idx]
            rnd.shuffle(vv)
            for i, x in zip(idx, vv):
                dd[i] = x
        nulli2.append(spearman(dd, [c[2] for c in coppie]))
    p = (1 + sum(n >= rho for n in nulli2)) / (1 + RIMESCOLAMENTI)
    esito = 'test non valido' if not valido else ('le scelte seguono la dimensione' if rho > 0 and p < 0.01 else ('nessun legame' if p > 0.05 else 'incerto'))
    ris = OrderedDict([('pagine', len(P)), ('righe', sum(map(len, P.values()))), ('V1', OrderedDict([('r', vero), ('nullo', statistics.mean(nulli)), ('z', z1)])),
                       ('valido', valido), ('coppie', len(coppie)), ('spearman', rho), ('p', p), ('esito', esito)])
    print('coppie %d | Spearman %.3f (p %.4f) | %s' % (len(coppie), rho, p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e173_dimensione_scrittura.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e173 — Scelte di grafia e dimensione della scrittura', '', 'Dimensione = larghezza del riquadro per unità EVA (voynichese.com), mediana per riga, '
           'normalizzata sulla pagina. Preregistrazione: `preregistrazioni/e173.md`.', '',
           '| verifica | valore |', '|---|---|', '| V1 correlazione fra righe consecutive (nullo; z) | %.3f (%.3f; %.1f) |' % (vero, statistics.mean(nulli), z1),
           '| Spearman fra cambio di dimensione e cambio di scelta (p) | %.3f (%.4f), coppie %d |' % (rho, p, len(coppie)), '',
           'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e173_dimensione_scrittura.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
