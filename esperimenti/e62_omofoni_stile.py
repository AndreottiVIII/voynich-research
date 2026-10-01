# -*- coding: utf-8 -*-
"""Esperimento 62: messaggio vero con omofoni del Voynich scelti secondo uno stile di pagina che
deriva da pagina a pagina (pesi per segno, AR(1) fra le pagine), piu' la regola delle giunture.

Preregistrazione: preregistrazioni/e62.md. Scrive risultati/e62_omofoni_stile.json e .md.
"""
import json, math, os, random, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SIGMA = (0.5, 1.0, 2.0)
RHO = (0.0, 0.8, 0.95)
GAMMA = (0, 1.5, 3)
D = misure.divisore(misure.GLIFI_EVA)
BASE = ('h2', 'spazio', 'uniche', 'tipi', 'ripetizione', 'omogeneità', 'gradiente', 'legame')


def scrivi(struttura, messaggio, forme, giunture, segni, sigma, rho, gamma, seme):
    rnd = random.Random(seme)
    pesi = {g: rnd.gauss(0, sigma) for g in segni}
    pos = 0
    pagine = []
    for np_, righe_pagina in enumerate(struttura):
        if np_ > 0:
            pesi = {g: rho * w + math.sqrt(1 - rho * rho) * rnd.gauss(0, sigma) for g, w in pesi.items()}
        pagina = []
        for n in righe_pagina:
            riga = []
            for _ in range(n):
                cand = forme[messaggio[pos % len(messaggio)]]
                pos += 1
                pp = []
                for u in cand:
                    s = sum(pesi.get(g, 0.0) for g in u) / math.sqrt(len(u))
                    g_ = 1.0
                    if gamma and riga:
                        g_ = giunture.get((riga[-1][-1], u[0]), 0.05) ** gamma
                    pp.append(math.exp(s) * g_)
                riga.append(rnd.choices(cand, weights=pp)[0])
            pagina.append(riga)
        pagine.append([[''.join(u) for u in r] for r in pagina])
    return pagine


def una(args):
    import e61_pagella as e61
    struttura, latino, forme, giunture, segni, voy, soglia_ab, sigma, rho, gamma = args
    pagine = scrivi(struttura, latino, forme, giunture, segni, sigma, rho, gamma, 62)
    return (sigma, rho, gamma), e61.scheda(pagine, D, voy, soglia_ab)


def main():
    import e46_codice_accorto as e46
    import e52_codice_accorto_vero as e52
    import e55_forma_parole as e55
    import e61_pagella as e61
    from e07_codifiche import pagine_voynich
    from e36_posizione_pagina import plinio
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    pv = pagine_voynich(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    latino = [w for _, ps in plinio() for w in ps]
    codice = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(52))
    base = {}
    for w, c in zip(latino, codice):
        base.setdefault(w, c)
    forme = e52.forme_vere(base, voy, D)
    giunture = e46.tabella_giunture([r for p in pv for r in p], D)
    segni = sorted({g for fs in forme.values() for u in fs for g in u})
    struttura = [[len(r) for r in p] for p in pv]
    ris = OrderedDict()
    v = e61.scheda(pv, D, voy, soglia_ab)
    ris['Voynich'] = v
    lavori = [(struttura, latino, forme, giunture, segni, voy, soglia_ab, s, r, g) for s in SIGMA for r in RHO for g in GAMMA]
    medie = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for (s, r, g), m in pool.imap(una, lavori):
            esiti = OrderedDict()
            for prop, f in e61.BANDE.items():
                try:
                    esiti[prop] = bool(f(m, v))
                except (KeyError, TypeError, ZeroDivisionError):
                    esiti[prop] = False
            m['esiti'] = esiti
            m['compatibile'] = all(esiti[p] for p in BASE)
            nome = 'sigma %.1f, rho %.2f, gamma %.1f' % (s, r, g)
            medie[nome] = m
            print('%-32s base %d/8 %s | fuori campione %d/9 | rip %.2f somigl %.1f%%/%.1f%% legame %.3f deriva %.3f R %.2f' % (
                nome, sum(esiti[p] for p in BASE), 'COMPATIBILE' if m['compatibile'] else '',
                sum(x for p, x in esiti.items() if p not in BASE), m['identiche_vs_riga'], 100 * m['somiglianza_riga'],
                100 * m['somiglianza_6_righe'], m['confine'], m['V2_ricambio_k1_meno_k20'], m['V3_R'] or 0), flush=True)
    ris['combinazioni'] = medie
    with open(os.path.join(RISULTATI, 'e62_omofoni_stile.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE)
    out = ['# e62 — Messaggio con omofoni e stile di pagina che deriva', '',
           'Bande della pagella (e61). Compatibile = tutte le proprietà di base (%s). Le altre sono validazione '
           'fuori campione. Preregistrazione: `preregistrazioni/e62.md`.' % ', '.join(BASE), '',
           '| combinazione | base | fuori campione | ' + ' | '.join(props) + ' |',
           '|---|---|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %d/8%s | %d/9 | %s |' % (
            nome, sum(m['esiti'][p] for p in BASE), ' **compatibile**' if m['compatibile'] else '',
            sum(x for p, x in m['esiti'].items() if p not in BASE), ' | '.join('✓' if m['esiti'][p] else '·' for p in props)))
    with open(os.path.join(RISULTATI, 'e62_omofoni_stile.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
