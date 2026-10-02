# -*- coding: utf-8 -*-
"""Esperimento 166: scuro dell'inchiostro parola per parola (immagini di voynichese.com, nella cornice dei riquadri);
validita' (struttura, dente di sega), intinte, e cambio delle scelte di grafia fra righe con e senza intinta.

Preregistrazione: preregistrazioni/e166.md. Scrive risultati/e166_intinte.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

import numpy as np
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146

RISULTATI = os.path.join(QUI, '..', 'risultati')
IMMAGINI = os.path.join(QUI, '..', 'dati', 'cache', 'voynichese_immagini')
SEME, RIMESCOLAMENTI_V1, INVERSIONI, RIMESCOLAMENTI_H2 = 166, 200, 2000, 2000
CORNICE, MIN_PIXEL, MIN_RIGHE, PERCENTILE, PRECEDENTI = 6, 15, 8, 85, 3


def scuri(foglio):
    """Scuro di ogni riquadro (None se non misurabile)."""
    d = json.load(open(os.path.join(e34.RIQUADRI, foglio + '.js'), encoding='utf-8'))
    im = Image.open(os.path.join(IMMAGINI, foglio + '.jpg')).convert('RGB')
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
        X0, Y0, X1, Y1 = max(0, x0 - CORNICE), max(0, y0 - CORNICE), min(w, x1 + CORNICE), min(h, y1 + CORNICE)
        anello = np.ones((Y1 - Y0, X1 - X0), bool)
        anello[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = False
        fondo = float(np.median(V[Y0:Y1, X0:X1][anello])) if anello.any() else float(np.median(V))
        box = V[y0:y1, x0:x1]
        ink = (box < 0.7 * fondo) & ~colorato[y0:y1, x0:x1]
        out.append(1 - float(box[ink].mean()) / fondo if ink.sum() >= MIN_PIXEL and fondo > 0 else None)
    return [voc[0] for voc in d[0]], [e[0] for e in d[1]], out


def pagine():
    """Per pagina: lista di righe (indice globale della riga, [scuro o None per parola])."""
    righe = e146.righe_voynich()
    per = defaultdict(list)
    for k, (pag, par, ps) in enumerate(righe):
        per[pag].append(k)
    out = OrderedDict()
    for pag, ks in per.items():
        if not os.path.exists(os.path.join(e34.RIQUADRI, pag + '.js')) or not os.path.exists(os.path.join(IMMAGINI, pag + '.jpg')):
            continue
        voc, idx, sc = scuri(pag)
        vt = [voc[i] for i in idx]
        zt = [(k, j, w) for k in ks for j, w in enumerate(righe[k][2])]
        sm = SequenceMatcher(a=[e34.fondi(w) for w in vt], b=[e34.fondi(w) for _, _, w in zt], autojunk=False)
        valori = {}
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                valori[(zt[j0 + t][0], zt[j0 + t][1])] = sc[i0 + t]
        rr = [(k, [valori.get((k, j)) for j in range(len(righe[k][2]))]) for k in ks]
        if sum(1 for _, v in rr if any(x is not None for x in v)) >= MIN_RIGHE:
            out[pag] = rr
    return righe, out


def sequenza(rr):
    """Parole misurate nell'ordine di scrittura: (riga, posizione, scuro)."""
    return [(k, j, x) for k, v in rr for j, x in enumerate(v) if x is not None]


def corr(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.corrcoef(a, b)[0, 1]) if len(a) > 2 and a.std() and b.std() else 0.0


def v1(P, rnd):
    def stat(seqs):
        a, b = [], []
        for s in seqs:
            a += s[:-1]
            b += s[1:]
        return corr(a, b)
    seqs = [[x for _, _, x in sequenza(rr)] for rr in P.values()]
    seqs = [[x - statistics.mean(s) for x in s] for s in seqs if len(s) > 3]   # toglie il livello della pagina
    vero = stat(seqs)
    nulli = []
    for _ in range(RIMESCOLAMENTI_V1):
        mes = []
        for s in seqs:
            s = s[:]
            rnd.shuffle(s)
            mes.append(s)
        nulli.append(stat(mes))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('r', vero), ('nullo', m), ('z', (vero - m) / sd if sd else None)])


def skew(x):
    x = np.array(x)
    s = x.std()
    return float(((x - x.mean()) ** 3).mean() / s ** 3) if s else 0.0


def v2(P, rnd):
    dd = []
    for rr in P.values():
        s = [x for _, _, x in sequenza(rr)]
        dd += [b - a for a, b in zip(s, s[1:])]
    vero = skew(dd)
    arr = np.array(dd)
    nrnd = np.random.default_rng(SEME)
    nulli = [skew(arr * nrnd.choice([-1, 1], size=len(arr))) for _ in range(INVERSIONI)]
    p = (1 + sum(n >= vero for n in nulli)) / (1 + INVERSIONI)
    return OrderedDict([('skewness', vero), ('p', p), ('n', len(dd))])


def intinte(P):
    """{(riga, posizione): True/False} per le parole con almeno 3 precedenti misurate."""
    out = {}
    for rr in P.values():
        s = sequenza(rr)
        diff = [(s[t][0], s[t][1], s[t][2] - statistics.mean(x for _, _, x in s[t - PRECEDENTI:t])) for t in range(PRECEDENTI, len(s))]
        if len(diff) < 10:
            continue
        soglia = float(np.percentile([d for _, _, d in diff], PERCENTILE))
        for k, j, d in diff:
            out[(k, j)] = d > soglia
    return out


def main():
    rnd = random.Random(SEME)
    righe, P = pagine()
    n_par = sum(len(sequenza(rr)) for rr in P.values())
    print('pagine %d, parole misurate %d' % (len(P), n_par), flush=True)
    ris = OrderedDict([('pagine', len(P)), ('parole_misurate', n_par)])
    ris['V1'] = v1(P, rnd)
    ris['V2'] = v2(P, rnd)
    valido = (ris['V1']['z'] or 0) > 5 and ris['V2']['skewness'] > 0 and ris['V2']['p'] < 0.01
    ris['valido'] = valido
    print('V1 r %.3f (nullo %.3f, z %.1f) | V2 skewness %.3f (p %.4f) | valido %s' % (ris['V1']['r'], ris['V1']['nullo'], ris['V1']['z'] or 0,
          ris['V2']['skewness'], ris['V2']['p'], valido), flush=True)
    I = intinte(P)
    # H1: prima parola misurata della riga contro le altre
    per_riga = defaultdict(list)
    for (k, j), v in I.items():
        per_riga[k].append((j, v))
    prime, altre = [], []
    for k, vv in per_riga.items():
        vv.sort()
        prime.append(vv[0][1])
        altre += [v for _, v in vv[1:]]
    ris['H1'] = OrderedDict([('quota_prima_parola', sum(prime) / len(prime) if prime else None), ('quota_altre', sum(altre) / len(altre) if altre else None),
                             ('righe', len(prime))])
    print('H1 intinte: prima parola della riga %.3f, altre %.3f' % (ris['H1']['quota_prima_parola'] or 0, ris['H1']['quota_altre'] or 0), flush=True)
    # H2
    res = e146.residui(righe)
    coppie = []
    for pag, rr in P.items():
        ks = [k for k, _ in rr]
        for k1, k2 in zip(ks, ks[1:]):
            if righe[k1][1] != righe[k2][1]:
                continue
            dif = [abs(res[(f, k2)] - res[(f, k1)]) for f in e146.SCELTE if (f, k1) in res and (f, k2) in res]
            mis = sorted(j for j, _ in per_riga.get(k2, []))[:2]
            if not dif or not mis:
                continue
            coppie.append((pag, statistics.mean(dif), any(I[(k2, j)] for j in mis)))
    def stat(cc, etichette):
        con = [c for (_, c, _), e in zip(cc, etichette) if e]
        senza = [c for (_, c, _), e in zip(cc, etichette) if not e]
        return statistics.mean(con) - statistics.mean(senza) if con and senza else 0.0
    vero = stat(coppie, [e for _, _, e in coppie])
    per_pag = defaultdict(list)
    for i, (pag, _, _) in enumerate(coppie):
        per_pag[pag].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI_H2):
        et = [e for _, _, e in coppie]
        for idx in per_pag.values():
            v = [et[i] for i in idx]
            rnd.shuffle(v)
            for i, x in zip(idx, v):
                et[i] = x
        nulli.append(stat(coppie, et))
    p = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI_H2)
    ris['H2'] = OrderedDict([('coppie', len(coppie)), ('con_intinta', sum(e for _, _, e in coppie)), ('differenza', vero),
                             ('nullo_media', statistics.mean(nulli)), ('p', p)])
    esito = ('test non valido' if not valido else ('le scelte si rinnovano con l\'inchiostro' if vero > 0 and p < 0.01 else
             ('nessun legame' if p > 0.05 else 'incerto')))
    ris['esito'] = esito
    print('H2 coppie %d (con intinta %d): differenza %.4f, p %.4f | esito: %s' % (len(coppie), ris['H2']['con_intinta'], vero, p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e166_intinte.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e166 — Le scelte di grafia cambiano quando lo scriba intinge la penna?', '',
           'Scuro dell\'inchiostro per parola dalle immagini di voynichese.com (cornice dei riquadri). Pagine %d, parole misurate %d. '
           'Preregistrazione: `preregistrazioni/e166.md`.' % (len(P), n_par), '',
           '| verifica | valore |', '|---|---|',
           '| V1 correlazione fra parole consecutive (nullo; z) | %.3f (%.3f; z %.1f) |' % (ris['V1']['r'], ris['V1']['nullo'], ris['V1']['z'] or 0),
           '| V2 skewness di Δscuro (p) | %.3f (%.4f) |' % (ris['V2']['skewness'], ris['V2']['p']),
           '| H1 intinte: prima parola della riga / altre | %.3f / %.3f |' % (ris['H1']['quota_prima_parola'] or 0, ris['H1']['quota_altre'] or 0),
           '| H2 cambio di scelta con intinta − senza (p) | %.4f (%.4f), coppie %d, con intinta %d |' % (vero, p, len(coppie), ris['H2']['con_intinta']), '',
           'Validità: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e166_intinte.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
