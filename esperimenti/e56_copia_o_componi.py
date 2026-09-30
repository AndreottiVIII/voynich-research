# -*- coding: utf-8 -*-
"""Esperimento 56: il modello senza messaggio "copia o componi".

A ogni posto: con probabilita' c si copia una parola vicina (riga fonte con peso exp(-d/tau)),
altrimenti si compone una parola segno per segno con trigrammi lambda * pagina recente +
(1 - lambda) * Voynich; la candidata si accetta con la regola delle giunture (R^gamma).
Bande a due lati per la compatibilita'; validazione fuori campione V1, V2, V3, V5, V6, V7.

Preregistrazione: preregistrazioni/e56.md. Scrive risultati/e56_copia_o_componi.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
C = (0.3, 0.5, 0.7)
LAMBDA = (0.5, 0.8, 0.95)
TAU = (1.5, 4.0)
GAMMA = (1, 3)
SEMI = (1, 2, 3)
MASSIMO, TENTATIVI, R_IGNOTA = 12, 20, 0.05
D = misure.divisore(misure.GLIFI_EVA)


def conta(tabella, u, peso=1.0):
    s = ('^', '^') + tuple(u) + ('$',)
    for i in range(2, len(s)):
        tabella[(s[i - 2], s[i - 1])][s[i]] += peso


def pesca(ctx, globale, recente, lam, rnd):
    g, p = globale.get(ctx), recente.get(ctx)
    if not g and not p:
        return '$'
    l = 0.0 if not p else (1.0 if not g else lam)
    tg = sum(g.values()) if g else 0
    tp = sum(p.values()) if p else 0
    chiavi = sorted(set(g or {}) | set(p or {}))
    pesi = [(l * (p.get(k, 0) / tp if p else 0)) + ((1 - l) * (g.get(k, 0) / tg if g else 0)) for k in chiavi]
    return rnd.choices(chiavi, weights=pesi)[0]


def componi(globale, recente, lam, rnd):
    a, b, u = '^', '^', []
    for _ in range(MASSIMO):
        c = pesca((a, b), globale, recente, lam, rnd)
        if c == '$':
            break
        u.append(c)
        a, b = b, c
    return tuple(u) if u else ('o',)


def scrivi(struttura, globale, giunture, c, lam, tau, gamma, seme):
    rnd = random.Random(seme)
    pagine = []
    precedente = []
    for righe_pagina in struttura:
        recente = defaultdict(Counter)
        for u in precedente:
            conta(recente, u, 0.5)
        pagina, scritte_pagina = [], []
        for n in righe_pagina:
            riga = []
            for _ in range(n):
                scelta = None
                for _t in range(TENTATIVI):
                    if (pagina or riga) and rnd.random() < c:
                        cand = [(0, riga)] if riga else []
                        cand += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                        _, fonte = rnd.choices(cand, weights=[math.exp(-d / tau) for d, _ in cand])[0]
                        u = rnd.choice(fonte)
                    else:
                        u = componi(globale, recente, lam, rnd)
                    scelta = u
                    if not riga:
                        break
                    r = giunture.get((riga[-1][-1], u[0]), R_IGNOTA)
                    if rnd.random() < min(1.0, r ** gamma):
                        break
                riga.append(scelta)
                scritte_pagina.append(scelta)
                conta(recente, scelta)
            pagina.append(riga)
        precedente = scritte_pagina
        pagine.append([[''.join(u) for u in r] for r in pagina])
    return pagine


def bande(m):
    return {'ripetizione': 0.8 <= m['identiche_vs_riga'] <= 1.2,
            'somiglianza': 0.030 <= m['somiglianza_riga'] <= 0.046,
            'gradiente': 0.70 <= m['somiglianza_6_righe'] / m['somiglianza_riga'] <= 0.97 if m['somiglianza_riga'] > 0 else False,
            'h2': 2.10 <= m['h2'] <= 2.40,
            'legame': 0.14 <= m['confine'] <= 0.24,
            'uniche': 0.60 <= m['hapax_34000'] <= 0.76,
            'tipi': 0.17 <= m['tipi_su_parole'] <= 0.25}


def validazione(m, v):
    return {'V1': m['hapax_1000'] - m['hapax_34000'] <= 0.10,
            'V2': m['V2_ricambio_k1_meno_k20'] >= 0.05,
            'V3': m['V3_R'] is not None and 0.8 <= m['V3_R'] <= 1.25
                  and 0.5 * v['V3_quota_media'] <= m['V3_quota_media'] <= 1.5 * v['V3_quota_media'],
            'V5': m['unione_attestata'] / m['unione_caso'] >= 1.5,
            'V6': m['V6_autocorrelazione_lunghezze'] >= 0.08,
            'V7': abs(m['V7_zipf'] - v['V7_zipf']) <= 0.10}


def misura(pagine):
    import e53_scissione as e53
    return e53.misura(pagine)


def una(args):
    struttura, globale, giunture, c, lam, tau, gamma, seme = args
    pagine = scrivi(struttura, globale, giunture, c, lam, tau, gamma, seme)
    return (c, lam, tau, gamma, seme), misura(pagine)


def main():
    from e07_codifiche import pagine_voynich
    import e46_codice_accorto as e46
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    pv = pagine_voynich(corrente)
    globale = defaultdict(Counter)
    for w in trascrizione.parole(corrente):
        conta(globale, D(w))
    globale = {k: dict(v) for k, v in globale.items()}
    giunture = e46.tabella_giunture([r for p in pv for r in p], D)
    struttura = [[len(r) for r in p] for p in pv]
    ris = OrderedDict()
    v = misura(pv)
    ris['Voynich'] = v
    lavori = [(struttura, globale, giunture, c, lam, tau, g, s)
              for c in C for lam in LAMBDA for tau in TAU for g in GAMMA for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for chiave, r in pool.imap(una, lavori):
            ris['c %.1f, lambda %.2f, tau %.1f, gamma %d, seme %d' % chiave] = r
            per[chiave[:4]].append(r)
    medie = OrderedDict()
    for chiave, gruppo in per.items():
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float))]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        m['bande'] = bande(m)
        m['compatibile'] = all(m['bande'].values())
        m['validazione'] = validazione(m, v)
        nome = 'c %.1f, lambda %.2f, tau %.1f, gamma %d' % chiave
        medie[nome] = m
        print('%-36s rip %.2f somigl %.1f%%/%.1f%% h2 %.2f legame %.3f uniche %.2f tipi %.3f | bande %d/7 %s | %s' % (
            nome, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
            m['confine'], m['hapax_34000'], m['tipi_su_parole'], sum(m['bande'].values()),
            'COMPATIBILE' if m['compatibile'] else '', ' '.join(k for k, x in m['validazione'].items() if x)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e56_copia_o_componi.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    out = ['# e56 — Il modello "copia o componi"', '',
           'c = probabilità di copiare una parola vicina (riga fonte con peso exp(−d/τ)); altrimenti si compone con '
           'trigrammi λ · pagina recente + (1 − λ) · Voynich; giunture R^γ. Medie su tre semi. Compatibile = tutte e '
           'sette le bande a due lati. Validazione fuori campione V1, V2, V3, V5, V6, V7 (V4 e V8 per costruzione). '
           'Preregistrazione: `preregistrazioni/e56.md`.', '',
           '| combinazione | ripetizione | somigl. riga | 6 righe | h2 | legame | uniche | tipi | bande | validazione |',
           '|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.1f%% | %.1f%% | %.2f | %.3f | %.2f | %.3f | | |' % (
               v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['h2'], v['confine'],
               v['hapax_34000'], v['tipi_su_parole'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.1f%% | %.1f%% | %.2f | %.3f | %.2f | %.3f | %d/7%s | %s |' % (
            nome, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
            m['confine'], m['hapax_34000'], m['tipi_su_parole'], sum(m['bande'].values()),
            ' **compatibile**' if m['compatibile'] else '', ', '.join(k for k, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e56_copia_o_componi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
