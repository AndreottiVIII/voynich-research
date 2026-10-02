# -*- coding: utf-8 -*-
"""Esperimento 206c: le classi di segni facoltativi decise per riga (e206b) sono correlate fra loro da riga a riga
(un'unica abitudine di lunghezza) o indipendenti? Correlazioni fra righe sui residui di strato, senza parole in comune,
contro permutazioni delle righe dentro la pagina, indipendenti per classe.

Preregistrazione: preregistrazioni/e206c.md. Scrive risultati/e206c_scelte_correlate.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict
from itertools import combinations

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e206_segni_facoltativi as e206

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 2063, 200


def main():
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if r.parole:
            righe.append((r.pagina, bool(r.inizio_par), ps))
    freq = Counter(w for _, _, ps in righe for w in ps)
    cl = e206.classi_di(freq)
    occ = defaultdict(list)          # nome -> [(riga, gettone, strato, valore)]
    for k, (pag, ini, ps) in enumerate(righe):
        for j, w in enumerate(ps):
            pos = 0 if j == 0 else (2 if j == len(ps) - 1 else 1)
            for c, v in cl.get(w, {}).items():
                n = '%s %s' % c
                if n in classi:
                    occ[n].append((k, (k, j), (pag, ini, pos), v))
    residui = {}
    for n, oo in occ.items():
        s = defaultdict(list)
        for _, _, st, v in oo:
            s[st].append(v)
        m = {st: sum(x) / len(x) for st, x in s.items()}
        residui[n] = [(k, t, v - m[st]) for k, t, st, v in oo]
    gettoni = {n: {t for _, t, _ in residui[n]} for n in classi}
    K = len(righe)
    # per ogni coppia: medie per riga dei residui di A senza i gettoni di B (e viceversa)
    medie = {}
    for a, b in combinations(classi, 2):
        for x, y in ((a, b), (b, a)):
            somma, conta = np.zeros(K), np.zeros(K)
            for k, t, r in residui[x]:
                if t not in gettoni[y]:
                    somma[k] += r
                    conta[k] += 1
            with np.errstate(invalid='ignore', divide='ignore'):
                medie[(x, y)] = np.where(conta > 0, somma / np.maximum(conta, 1), np.nan)

    def correlazioni(perm):
        R = np.eye(len(classi))
        rs = {}
        for i, j in combinations(range(len(classi)), 2):
            a, b = classi[i], classi[j]
            va, vb = medie[(a, b)], medie[(b, a)]
            if perm is not None:
                pa, pb = np.full(K, np.nan), np.full(K, np.nan)
                pa[perm[a]] = va
                pb[perm[b]] = vb
                va, vb = pa, pb
            ok = ~np.isnan(va) & ~np.isnan(vb)
            r = float(np.corrcoef(va[ok], vb[ok])[0, 1]) if ok.sum() > 10 else 0.0
            R[i, j] = R[j, i] = r
            rs[(a, b)] = r
        pc1 = float(np.linalg.eigvalsh(R)[-1] / len(classi))
        return float(np.mean(list(rs.values()))), pc1, rs

    media_vera, pc1_vero, rs_vere = correlazioni(None)
    per_pagina = defaultdict(list)
    for k, (pag, _, _) in enumerate(righe):
        per_pagina[pag].append(k)
    rng = np.random.default_rng(SEME)
    nulli_m, nulli_p = [], []
    for _ in range(PERMUTAZIONI):
        perm = {}
        for n in classi:
            p = np.arange(K)
            for ks in per_pagina.values():
                ks = np.array(ks)
                p[ks] = ks[rng.permutation(len(ks))]
            perm[n] = p
        m, pc, _ = correlazioni(perm)
        nulli_m.append(m)
        nulli_p.append(pc)
    z = lambda x, xs: (x - np.mean(xs)) / np.std(xs) if np.std(xs) else None
    zm, zp = z(media_vera, nulli_m), z(pc1_vero, nulli_p)
    pm = (1 + sum(x >= media_vera for x in nulli_m)) / (PERMUTAZIONI + 1)
    pp = (1 + sum(x >= pc1_vero for x in nulli_p)) / (PERMUTAZIONI + 1)
    alte = sorted(rs_vere.items(), key=lambda kv: -kv[1])[:5]
    esito = ('un\'abitudine comune' if zm > 3 and zp > 3 else 'scelte in gran parte indipendenti' if zm <= 2 else 'legame parziale')
    ris = OrderedDict([('classi', classi), ('media_r', media_vera), ('media_r_nulla', float(np.mean(nulli_m)), ), ('z_media', zm), ('p_media', pm),
                       ('pc1', pc1_vero), ('pc1_nulla', float(np.mean(nulli_p))), ('z_pc1', zp), ('p_pc1', pp),
                       ('coppie_piu_correlate', [('%s / %s' % k, v) for k, v in alte]), ('esito', esito)])
    print(dict(ris))
    json.dump(ris, open(os.path.join(RISULTATI, 'e206c_scelte_correlate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e206c — Le scelte di riga dell\'e206b: indipendenti o un\'unica abitudine?', '',
          'Correlazioni fra righe dei residui di strato (pagina × prima riga × posizione), senza parole in comune fra le due classi; nullo: '
          '%d permutazioni delle righe dentro la pagina, indipendenti per classe. Preregistrazione: `preregistrazioni/e206c.md`.' % PERMUTAZIONI, '',
          '| statistica | vera | nulla | z | p |', '|---|---|---|---|---|',
          '| media delle 66 correlazioni | %.4f | %.4f | %.1f | %.3f |' % (media_vera, np.mean(nulli_m), zm, pm),
          '| quota della prima componente | %.3f | %.3f | %.1f | %.3f |' % (pc1_vero, np.mean(nulli_p), zp, pp), '',
          'Coppie più correlate: %s.' % '; '.join('%s %.3f' % (k, v) for k, v in ris['coppie_piu_correlate']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e206c_scelte_correlate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
