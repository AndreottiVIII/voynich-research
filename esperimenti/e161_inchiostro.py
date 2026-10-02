# -*- coding: utf-8 -*-
"""Esperimento 161: colore/scuro dell'inchiostro (immagini IIIF) e passo di riga (riquadri di voynichese.com) sono piu'
graduali nell'ordine ricostruito dei bifogli che in quello di rilegatura?

Preregistrazione: preregistrazioni/e161.md. Scrive risultati/e161_inchiostro.json e .md.
"""
import json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154
import e154b_ordine_normalizzato as e154b
import e34_spazi_fisici as e34

RISULTATI = os.path.join(QUI, '..', 'risultati')
IMMAGINI = os.path.join(QUI, '..', 'dati', 'cache', 'immagini')
REGISTRO = os.path.join(QUI, '..', 'dati', 'immagini.json')
SEME, CASUALI, MIN_PIXEL = 161, 1000, 2000


def fogli_da_nome(etichetta):
    return sorted({int(x) for x in re.findall(r'(\d+)[rv]', etichetta)})


def misura_immagine(percorso):
    im = Image.open(percorso).convert('RGB')
    im = im.resize((750, int(im.height * 750 / im.width)))
    hsv = np.asarray(im.convert('HSV')).astype(float)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h, w = V.shape
    centro = V[h // 6: 5 * h // 6, w // 6: 5 * w // 6]
    perg = float(np.median(centro))
    inch = (V < 0.55 * perg) & ~((S > 60) & (H >= 40) & (H <= 200)) & ~(S > 150)
    n = int(inch.sum())
    if n < MIN_PIXEL:
        return None
    ang = H[inch] / 255 * 2 * math.pi
    tinta = math.atan2(float(np.sin(ang).mean()), float(np.cos(ang).mean())) % (2 * math.pi)
    return [tinta, float(S[inch].mean()), float(V[inch].mean()) / perg]


def inchiostro_per_foglio():
    reg = json.load(open(REGISTRO, encoding='utf-8'))
    acc = defaultdict(list)
    for etichetta, d in reg.items():
        if etichetta.startswith('_') or 'file' not in d:
            continue
        ff = fogli_da_nome(etichetta)
        p = os.path.join(IMMAGINI, d['file'])
        if not ff or not os.path.exists(p):
            continue
        m = misura_immagine(p)
        if m:
            for f in ff:
                acc[f].append(m)
    return {f: [statistics.mean(x[i] for x in v) for i in range(3)] for f, v in acc.items()}


def passo_per_foglio():
    acc = defaultdict(list)
    for fn in os.listdir(e34.RIQUADRI):
        if not fn.endswith('.js'):
            continue
        d = json.load(open(os.path.join(e34.RIQUADRI, fn), encoding='utf-8'))
        righe, riga, prima = defaultdict(list), 0, None
        for e in d[1]:
            if prima is not None and e[1] < prima - 3:
                riga += 1
            righe[riga].append(e)
            prima = e[1]
        ys = [statistics.median(e[2] for e in r) for k, r in sorted(righe.items()) if len(r) >= 3]
        alt = [e[4] for e in d[1] if len(e) > 4 and e[4] > 0]
        dd = [b - a for a, b in zip(ys, ys[1:]) if b > a]
        if len(dd) >= 5 and alt:
            for x in fogli_da_nome(fn[:-3]):
                acc[x].append(statistics.median(dd) / statistics.median(alt))
    return {f: [statistics.mean(v)] for f, v in acc.items()}


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    ink_f, passo_f = inchiostro_per_foglio(), passo_per_foglio()
    print('fogli con inchiostro misurato: %d; con passo di riga: %d' % (len(ink_f), len(passo_f)), flush=True)

    def per_unita(per_foglio):
        out = {}
        for n in U:
            ff = [int(x[1:]) for x in n.split('-')]
            vv = [per_foglio[f] for f in ff if f in per_foglio]
            if vv:
                out[n] = [statistics.mean(v[i] for v in vv) for i in range(len(vv[0]))]
        return out
    caratt = OrderedDict([('(III) inchiostro', per_unita(ink_f)), ('(IV) passo di riga', per_unita(passo_f))])
    ris = OrderedDict([('fogli_inchiostro', len(ink_f)), ('fogli_passo', len(passo_f))])
    for nome_c, C in caratt.items():
        gruppi = defaultdict(list)
        for n, u in U.items():
            if n in C:
                gruppi[(u['mano'], u['lingua'])].append(n)
        gruppi = {k: v for k, v in gruppi.items() if len(v) >= 6}
        tot_r = tot_l = 0.0
        pesi = 0
        casuali = [0.0] * CASUALI
        for k, nomi in gruppi.items():
            X = e154.standardizza({n: C[n] for n in nomi})
            vett = {n: Counter(e154b.normalizza(w) for ps in U[n]['righe'] for w in ps) for n in nomi}
            S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
            ric = [nomi[i] for i in e150.ricostruisci(S)]
            ril = sorted(nomi, key=lambda n: U[n]['primo'])
            w = len(nomi) - 1
            tot_r += w * e154.distanza(ric, X)
            tot_l += w * e154.distanza(ril, X)
            pesi += w
            for i in range(CASUALI):
                o = nomi[:]
                rnd.shuffle(o)
                casuali[i] += w * e154.distanza(o, X)
        if not pesi:
            ris[nome_c] = None
            continue
        r_r, r_l = tot_r / pesi, tot_l / pesi
        cas = [x / pesi for x in casuali]
        p = sum(x <= r_r for x in cas) / CASUALI
        p_ril = sum(x <= r_l for x in cas) / CASUALI
        ris[nome_c] = OrderedDict([('gruppi', {('%s/%s' % k): len(v) for k, v in gruppi.items()}), ('ricostruito', r_r), ('rilegatura', r_l),
                                   ('casuali_media', statistics.mean(cas)), ('p_ricostruito', p), ('p_rilegatura', p_ril)])
        print('%-20s ricostruito %.3f (p %.3f) | rilegatura %.3f (p %.3f) | casuali %.3f | gruppi %s' % (
            nome_c, r_r, p, r_l, p_ril, statistics.mean(cas), ris[nome_c]['gruppi']), flush=True)
    conferma = any(r and r['ricostruito'] < r['rilegatura'] and r['p_ricostruito'] < 0.05 for r in (ris.get('(III) inchiostro'), ris.get('(IV) passo di riga')))
    ris['conferma_fisica'] = conferma
    print('conferma fisica:', conferma)
    with open(os.path.join(RISULTATI, 'e161_inchiostro.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e161 — Inchiostro e passo di riga nell\'ordine ricostruito dei bifogli', '', 'Fogli con inchiostro misurato: %d; con passo di riga: %d. Preregistrazione: '
           '`preregistrazioni/e161.md`.' % (len(ink_f), len(passo_f)), '', '| caratteristiche | ricostruito (p) | rilegatura (p) | casuali |', '|---|---|---|---|']
    for c in caratt:
        r = ris.get(c)
        if r:
            out.append('| %s | %.3f (%.3f) | %.3f (%.3f) | %.3f |' % (c, r['ricostruito'], r['p_ricostruito'], r['rilegatura'], r['p_rilegatura'], r['casuali_media']))
    out += ['', 'Conferma fisica: **%s**. (p = quota di ordini casuali altrettanto o più graduali.)' % ('sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e161_inchiostro.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
