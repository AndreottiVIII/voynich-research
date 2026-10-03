# -*- coding: utf-8 -*-
"""Il corpo del voynichizzatore, giro 5 (v5): come corpo4.py, con i bordi legati dentro la riga (e294, e295, e285c): fra
le candidate per il posto seguente, il peso si moltiplica per (T_fin[finale precedente, finale candidata] ** lam_fin) *
(T_pre[prefisso precedente, prefisso candidata] ** lam_pre), dove T e' il rapporto fra la frequenza della coppia di parti
fra parole vicine nella stessa riga del Voynich e quella attesa con le parti indipendenti (parti dell'e285, segmentatore
dell'e249; coppie con meno di 5 occorrenze attese -> 1; T fra 0,2 e 5). Le parti delle parole nuove si calcolano con lo
stesso segmentatore. Con lam_fin 0 e lam_pre 0 coincide con corpo4.genera_v4. Da corpo4:
Il corpo del voynichizzatore, giro 4: come corpo3.py, con le coppie ripetute (omega: con questa probabilita' la prima
candidata riprende una parola che seguiva gia' la parola precedente altrove nel testo). Con omega 0 coincide con
corpo3.genera_v3. Da corpo3, giro 3 (v4): come corpo2.py, con il tema variato (tau: una candidata presa dal tema e
rimasta identica si modifica con probabilita' tau, come nell'e234/e242). Con tau 0 coincide con corpo2.genera_v2. Da corpo2: come corpo.py, con quattro meccanismi in piu' (lunghezza stabile nelle varianti,
concordanza delle desinenze, somiglianza con la parola di sopra, spezzature durante la scelta gia' presenti come sigma).
Con i nuovi parametri spenti coincide con corpo.genera_tutto. Dal corpo del 3/10: il generatore e241 con tutti i meccanismi provati il 3/10/2026, ciascuno regolabile
(tema e mazzo dell'e251b, prime righe dell'e268, penalita' per le ripetizioni e copia per indice dell'e288, interruttori
di riga dell'e252). Con i valori predefiniti coincide con e233.genera (e241); con i parametri di ciascun esperimento
coincide con il suo generatore (verificato).
"""
import os, random, sys
from collections import Counter, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import generatori, trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e251_lessico_sezione as e251


_LEN, _SIM, _BORDI = {}, {}, {}


def lunghezze_voynich(c):
    """Distribuzione delle lunghezze (in segni) delle parole del Voynich."""
    if not _LEN:
        cnt = Counter(len(c['D'](w)) for w in c['voy'])
        tot = sum(cnt.values())
        _LEN.update({L: n / tot for L, n in cnt.items()})
    return _LEN


def bordi():
    """(parti, T_fin, T_pre): parti(w) = (prefisso, centro, finale) dell'e285; le due tabelle dal Voynich."""
    if not _BORDI:
        import math
        import e249_pezzi_simboli as e249
        import e285_pezzi_contesto as e285
        voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
        taglia = e249.segmentatore([w for r in voy for w in r])
        cache = {}

        def parti(w):
            if w not in cache:
                cache[w] = e285.parti(taglia, w)
            return cache[w]
        tab = []
        for j in (0, 2):
            coppie = [(parti(a)[j], parti(b)[j]) for r in voy for a, b in zip(r, r[1:])]
            n = len(coppie)
            cxy, cx, cy = Counter(coppie), Counter(a for a, _ in coppie), Counter(b for _, b in coppie)
            t = {}
            for (a, b), o in cxy.items():
                e = cx[a] * cy[b] / n
                if e >= 5:
                    t[(a, b)] = min(5.0, max(0.2, o / e))
            for a in cx:
                for b in cy:
                    if (a, b) not in cxy and cx[a] * cy[b] / n >= 5:
                        t[(a, b)] = 0.2
            tab.append(t)
        _BORDI.update(parti=parti, pre=tab[0], fin=tab[1])
    return _BORDI['parti'], _BORDI['fin'], _BORDI['pre']


def variante_L(w, mu, mod, rnd, nu, att, Dv, beta, plen):
    """Come e224.variante, con un filtro alla Metropolis sulla lunghezza: un cambio da L a L' segni si tiene con probabilita'
    min(1, (P(L')/P(L))**beta), con P la distribuzione delle lunghezze del Voynich. Con beta 0 non si usa."""
    u = tuple(Dv(w))
    for _ in range(generatori.poisson(rnd, mu)):
        x = mod.modifica(u, rnd)
        if ''.join(x) in att or (mod.valida(x) and rnd.random() < nu):
            if len(x) != len(u) and rnd.random() >= min(1.0, (plen.get(len(x), 1e-4) / plen.get(len(u), 1e-4)) ** beta):
                continue
            u = x
    return ''.join(u)


def somiglianza(a, b, Dv):
    """1 - distanza di modifica normalizzata fra due parole, sui segni."""
    k = (a, b)
    if k not in _SIM:
        x, y = tuple(Dv(a)), tuple(Dv(b))
        prec = list(range(len(y) + 1))
        for i in range(1, len(x) + 1):
            cur = [i] + [0] * len(y)
            for j in range(1, len(y) + 1):
                cur[j] = min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (x[i - 1] != y[j - 1]))
            prec = cur
        _SIM[k] = 1.0 - prec[-1] / max(len(x), len(y), 1)
    return _SIM[k]


def genera_v6(c, prm, seme, inter=None, prime_per_pag=None):
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
    beta, eps, vsim = prm.get('beta', 0.0), prm.get('eps', 1.0), prm.get('vsim', 0.0)
    tau = prm.get('tau', 0.0)
    lam_fin, lam_pre = prm.get('lam_fin', 0.0), prm.get('lam_pre', 0.0)
    if lam_fin or lam_pre:
        parti, t_fin, t_pre = bordi()
    omega, seguenti = prm.get('omega', 0.0), defaultdict(list)
    plen = lunghezze_voynich(c) if beta else None
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
                    da_tema = False
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
                        if omega and j == 0 and seguenti.get(riga[-1]) and rnd.random() < omega:
                            base = rnd.choice(seguenti[riga[-1]])
                        elif rho and ini and pr_pag and rnd.random() < rho:
                            base = rnd.choice(pr_pag)
                        else:
                            da_tema = rnd.random() < theta and bool(tema)
                            base = rnd.choice(tema) if da_tema else estrai()
                    if beta:
                        cand.append(variante_L(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv, beta, plen))
                    else:
                        cand.append(e224.variante(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv))
                    if tau and da_tema and cand[-1] == base and rnd.random() < tau:
                        cand[-1] = e234.forza_variante(base, mod, rnd, prm['nu'], att, Dv)
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
                    if eps != 1.0 and x != riga[-1] and Dv(x)[-2:] == Dv(riga[-1])[-2:]:
                        p *= eps
                    if vsim and sopra and pos < len(sopra):
                        p *= 1.0 + vsim * somiglianza(x, sopra[pos], Dv)
                    if (lam_fin or lam_pre) and trascrizione.pulita(x) and trascrizione.pulita(riga[-1]):
                        pa, px = parti(riga[-1]), parti(x)
                        if lam_fin:
                            p *= t_fin.get((pa[2], px[2]), 1.0) ** lam_fin
                        if lam_pre:
                            p *= t_pre.get((pa[0], px[0]), 1.0) ** lam_pre
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
            if omega:
                for a, b in zip(riga, riga[1:]):
                    seguenti[a].append(b)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe
