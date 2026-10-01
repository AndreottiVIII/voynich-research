# -*- coding: utf-8 -*-
"""Esperimento 70: copia esatta (o con ritocco leggero) di una parola vicina con probabilita' c alta,
altrimenti una forma nuova composta dai trigrammi del Voynich; giunture R^3. Pagella (e61).

Preregistrazione: preregistrazioni/e70.md. Scrive risultati/e70_copia_frequente.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
C = (0.80, 0.86, 0.90)
MU = (0.0, 0.2)
LAM, TAU, GAMMA, TENTATIVI = 0.7, 1.5, 3, 20
SEMI = (1, 2, 3)
D = misure.divisore(misure.GLIFI_EVA)
COSTRUZIONE = ('forma parole',)
FUORI = ('profilo pagina', 'lunghezze vicine', 'verticale', 'formule', 'deriva', 'Zipf', 'unioni', 'curva piatta')
BASE = ('h2', 'spazio', 'uniche', 'tipi', 'ripetizione', 'omogeneità', 'gradiente', 'legame')
_MOD = None


def scrivi(struttura, globale, giunture, modifiche, c, mu, seme):
    import e56_copia_o_componi as e56
    rnd = random.Random(seme)
    pagine, viste, precedente = [], set(), []
    for righe_pagina in struttura:
        recente = defaultdict(Counter)
        for u in precedente:
            e56.conta(recente, u, 0.5)
        pagina, scritte = [], []
        for n in righe_pagina:
            riga = []
            for _ in range(n):
                scelta = None
                for _t in range(TENTATIVI):
                    if (pagina or riga) and rnd.random() < c:
                        cand = [(0, riga)] if riga else []
                        cand += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                        _, fonte = rnd.choices(cand, weights=[math.exp(-d / TAU) for d, _ in cand])[0]
                        u = rnd.choice(fonte)
                        for _m in range(generatori.poisson(rnd, mu) if mu else 0):
                            prova = modifiche.modifica(u, rnd)
                            if modifiche.valida(prova):
                                u = tuple(prova)
                    else:
                        for _n in range(TENTATIVI):
                            u = e56.componi(globale, recente, LAM, rnd)
                            if u not in viste:
                                break
                    scelta = tuple(u)
                    if not riga:
                        break
                    r = giunture.get((riga[-1][-1], scelta[0]), e56.R_IGNOTA)
                    if rnd.random() < min(1.0, r ** GAMMA):
                        break
                riga.append(scelta)
                scritte.append(scelta)
                viste.add(scelta)
                e56.conta(recente, scelta)
            pagina.append(riga)
        precedente = scritte
        pagine.append([[''.join(u) for u in r] for r in pagina])
    return pagine


def una(args):
    global _MOD
    import e61_pagella as e61
    struttura, globale, giunture, voy, soglia_ab, c, mu, seme = args
    if _MOD is None:
        _MOD = generatori.Modifiche(voy, D)
    return (c, mu, seme), e61.scheda(scrivi(struttura, globale, giunture, _MOD, c, mu, seme), D, voy, soglia_ab)


def main():
    import e46_codice_accorto as e46
    import e55_forma_parole as e55
    import e56_copia_o_componi as e56
    import e61_pagella as e61
    from e07_codifiche import pagine_voynich
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    pv = pagine_voynich(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    globale = defaultdict(Counter)
    for w in voy:
        e56.conta(globale, D(w))
    globale = {k: dict(x) for k, x in globale.items()}
    giunture = e46.tabella_giunture([r for p in pv for r in p], D)
    struttura = [[len(r) for r in p] for p in pv]
    ris = OrderedDict()
    v = e61.scheda(pv, D, voy, soglia_ab)
    ris['Voynich'] = v
    per = defaultdict(list)
    lavori = [(struttura, globale, giunture, voy, soglia_ab, c, mu, s) for c in C for mu in MU for s in SEMI]
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for chiave, r in pool.imap(una, lavori):
            ris['c %.2f, mu %.1f, seme %d' % chiave] = r
            per[chiave[:2]].append(r)
    medie = OrderedDict()
    for (c, mu), gruppo in per.items():
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(m, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        m['esiti'] = esiti
        nome = 'c %.2f, mu %.1f' % (c, mu)
        medie[nome] = m
        print('%-16s %d/17 | base %d/8 | fuori %d/%d | h2 %.2f spazio %.2f uniche %.2f tipi %.3f rip %.2f omog %.3f/%.3f legame %.3f forma %.2f R %.2f lungh %.3f deriva %.3f' % (
            nome, sum(esiti.values()), sum(esiti[p] for p in BASE), sum(esiti[p] for p in FUORI), len(FUORI),
            m['h2'], m['spazio_spiegato'], m['hapax_34000'], m['tipi_su_parole'], m['identiche_vs_riga'],
            m['somiglianza_riga'], m['somiglianza_6_righe'], m['confine'], m.get('V8_forma', 0), m['V3_R'] or 0,
            m['V6_autocorrelazione_lunghezze'], m['V2_ricambio_k1_meno_k20']), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e70_copia_frequente.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE)
    out = ['# e70 — Copia esatta o forma nuova, alla quota giusta', '',
           'Copia di una parola vicina con probabilità c (ritocco leggero μ), altrimenti forma nuova dai trigrammi (λ %.1f); '
           'giunture γ %d. Medie su tre semi. Per costruzione: forma delle parole. Fuori campione: %s. Preregistrazione: '
           '`preregistrazioni/e70.md`.' % (LAM, GAMMA, ', '.join(FUORI)), '',
           '| combinazione | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %d/17 | %s |' % (nome, sum(m['esiti'].values()), ' | '.join(
            ('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e70_copia_frequente.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
