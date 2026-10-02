# -*- coding: utf-8 -*-
"""Esperimento 175: replica dell'e173b con l'altezza del corpo della scrittura (fascia densa del profilo verticale
d'inchiostro nel riquadro), dalle immagini di voynichese.com.

Preregistrazione: preregistrazioni/e175.md. Scrive risultati/e175_corpo_scrittura.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

import numpy as np
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146
import e166_intinte as e166
import e173_dimensione_scrittura as e173
import e173b_dimensione_per_lunghezza as e173b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 175


def corpi(foglio):
    d = json.load(open(os.path.join(e34.RIQUADRI, foglio + '.js'), encoding='utf-8'))
    im = Image.open(os.path.join(e166.IMMAGINI, foglio + '.jpg')).convert('RGB')
    hsv = np.asarray(im.convert('HSV')).astype(float)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h, w = V.shape
    colorato = ((S > 60) & (H >= 40) & (H <= 200)) | (S > 150)
    out = []
    for e in d[1]:
        x0, y0, x1, y1 = max(0, e[1]), max(0, e[2]), min(w, e[1] + e[3]), min(h, e[2] + e[4])
        if x1 - x0 < 3 or y1 - y0 < 3:
            out.append(None)
            continue
        X0, Y0, X1, Y1 = max(0, x0 - e166.CORNICE), max(0, y0 - e166.CORNICE), min(w, x1 + e166.CORNICE), min(h, y1 + e166.CORNICE)
        anello = np.ones((Y1 - Y0, X1 - X0), bool)
        anello[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = False
        fondo = float(np.median(V[Y0:Y1, X0:X1][anello])) if anello.any() else float(np.median(V))
        ink = (V[y0:y1, x0:x1] < 0.7 * fondo) & ~colorato[y0:y1, x0:x1]
        if ink.sum() < e166.MIN_PIXEL:
            out.append(None)
            continue
        prof = ink.mean(axis=1)
        out.append(int((prof >= 0.5 * prof.max()).sum()))
    return [v[0] for v in d[0]], [e[0] for e in d[1]], out


def misure_righe():
    righe = e146.righe_voynich()
    per = defaultdict(list)
    for k, (pag, _, _) in enumerate(righe):
        per[pag].append(k)
    out = OrderedDict()
    for pag, ks in per.items():
        if not os.path.exists(os.path.join(e34.RIQUADRI, pag + '.js')) or not os.path.exists(os.path.join(e166.IMMAGINI, pag + '.jpg')):
            continue
        voc, idx, cp = corpi(pag)
        vt = [voc[i] for i in idx]
        zt = [(k, w) for k in ks for w in righe[k][2]]
        sm = SequenceMatcher(a=[e34.fondi(w) for w in vt], b=[e34.fondi(w) for _, w in zt], autojunk=False)
        per_riga = defaultdict(list)
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                if cp[i0 + t]:
                    per_riga[zt[j0 + t][0]].append(cp[i0 + t])
        mis = {k: statistics.median(v) for k, v in per_riga.items() if len(v) >= e173.MIN_PAROLE}
        if len(mis) >= e173.MIN_RIGHE:
            m = statistics.median(mis.values())
            out[pag] = [(k, mis[k] / m) for k in ks if k in mis]
    return righe, out


def main():
    rnd = random.Random(SEME)
    righe, P = misure_righe()
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
    with open(os.path.join(RISULTATI, 'e175_corpo_scrittura.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e175 — Replica dell\'e173b con l\'altezza del corpo della scrittura', '', 'Fascia densa del profilo verticale d\'inchiostro nel riquadro (immagini di voynichese.com), '
           'mediana per riga, normalizzata sulla pagina. Preregistrazione: `preregistrazioni/e175.md`.', '', '| verifica | valore |', '|---|---|',
           '| V1 correlazione fra righe consecutive (z) | %.3f (%.1f) |' % (vero1, z1), '| statistica dentro le classi di lunghezza (p) | %.3f (%.4f), coppie %d |' % (vero, p, len(cc)),
           '', 'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e175_corpo_scrittura.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
