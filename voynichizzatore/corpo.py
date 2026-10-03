# -*- coding: utf-8 -*-
"""Il corpo del voynichizzatore: il generatore e241 con tutti i meccanismi provati il 3/10/2026, ciascuno regolabile
(tema e mazzo dell'e251b, prime righe dell'e268, penalita' per le ripetizioni e copia per indice dell'e288, interruttori
di riga dell'e252). Con i valori predefiniti coincide con e233.genera (e241); con i parametri di ciascun esperimento
coincide con il suo generatore (verificato).
"""
import os, random, sys
from collections import Counter, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e251_lessico_sezione as e251


def genera_tutto(c, prm, seme, inter=None, prime_per_pag=None):
    """Il generatore e241 con tutti i meccanismi del 3/10 come parametri (theta, k_tema, mazzo: e251b; rho: e268; rip: e288;
    phi con copia per indice: e233; inter: e252). Con i valori predefiniti coincide con e233.genera. Come e232.genera ('gamma', 'fisica', 'delta'), con in piu' 'kappa' (modifiche medie MU * (2 r)^kappa, r = rango
    percentile della parola di base) e 'chi' (con questa probabilita' la seconda candidata e' una variante della parola
    precedente della riga)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    theta, k_tema, mazzo = prm.get('theta', 0.3), prm.get('k_tema', e153.K), prm.get('mazzo', False)
    frequenti = {w for w, _ in Counter(c['voy']).most_common(200)} if mazzo else set()
    rip, rho = prm.get('rip', 1.0), prm.get('rho', 0.0)
    rango = e233.ranghi(c)
    fattore = (lambda w: (2 * rango.get(w, 1.0)) ** kappa) if kappa else (lambda w: 1.0)
    sez = e230.sezioni()
    lessico = defaultdict(list)
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    h = {f: 0.0 for f in e145.SCELTE}
    stato = {kk: 0.0 for kk in (inter[0] if inter else {})}
    righe, storia = [], []
    for pag, d in c['P'].items():
        s_pag = sez.get(pag)
        nuove_pag = []
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        if inter:
            for kk in stato:
                stato[kk] = (e152.RHO / 2) * stato[kk] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        cnt = Counter(pool)
        tipi = list(cnt)
        pesi_pool = [cnt[t] ** prm['alfa'] for t in tipi]
        lex = lessico[s_pag]
        pr_pag = prime_per_pag.get(pag, []) if rho else []
        gt, gp = e232.globali(c, lingua, prm['alfa'])

        mazzo_pag = list(pool) if mazzo else None

        def estrai():
            if gamma and lex and rnd.random() < gamma:
                return rnd.choice(lex)
            if delta and rnd.random() < delta:
                return rnd.choices(gt, gp)[0]
            if mazzo:
                if not mazzo_pag:
                    mazzo_pag.extend(pool)
                i = rnd.randrange(len(mazzo_pag))
                w = mazzo_pag[i]
                if w not in frequenti:
                    mazzo_pag[i] = mazzo_pag[-1]
                    mazzo_pag.pop()
                return w
            return rnd.choices(tipi, pesi_pool)[0]

        tema = [estrai() for _ in range(k_tema)] if k_tema else []
        prima_sopra, sopra = None, None
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            if inter:
                for kk in stato:
                    stato[kk] = e152.RHO * stato[kk] + rnd.gauss(0, e152.SIGMA)
            n = len(ps)
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or Dv(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            while len(riga) < n:
                pos = len(riga)
                if prm['psi'] and storia and 1 <= pos <= n - 3 and rnd.random() < prm['psi']:
                    src = rnd.choice(storia)
                    if len(src) >= 4:
                        a = rnd.randrange(1, len(src) - 2)
                        m = min(rnd.choice((2, 3)), n - pos, len(src) - a)
                        riga += [e224.variante(x, e153.MU / 2, mod, rnd, prm['nu'], att, Dv) for x in src[a:a + m]]
                        continue
                cand = []
                for j in range(k):
                    if fisica:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi']
                    else:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra)
                    if copia and fisica:
                        x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                        centri, acc = [], 0
                        for w in sopra:
                            centri.append(acc + len(Dv(w)) / 2)
                            acc += len(Dv(w)) + 1
                        base = sopra[min(range(len(sopra)), key=lambda t: abs(centri[t] - x0))]
                    elif copia:
                        base = sopra[pos]
                    elif chi and j == 1 and rnd.random() < chi:
                        base = riga[-1]
                    else:
                        if rho and ini and pr_pag and rnd.random() < rho:
                            base = rnd.choice(pr_pag)
                        else:
                            base = rnd.choice(tema) if rnd.random() < theta and tema else estrai()
                    cand.append(e224.variante(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv))
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    if rip != 1.0 and x == riga[-1]:
                        p *= rip
                    pesi.append(p)
                x = rnd.choices(cand, pesi)[0]
                if prm['sigma'] and pos < n - 1 and len(Dv(x)) >= 4 and rnd.random() < prm['sigma']:
                    s = e224.spezza(x, att, Dv, rnd)
                    if s:
                        riga += s
                        continue
                riga.append(x)
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if inter:
                riga = e251.applica_interruttori(riga, stato, inter, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe
