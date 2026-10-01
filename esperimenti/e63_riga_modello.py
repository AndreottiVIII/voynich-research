# -*- coding: utf-8 -*-
"""Esperimento 63: la riga modello. Ogni riga ripercorre una riga sopra (scelta con peso
exp(-d/tau)): con probabilita' a la parola del modello nella stessa posizione, ritoccata (Poisson mu),
altrimenti una forma nuova composta nello stile della pagina; giunture R^3.

Preregistrazione: preregistrazioni/e63.md. Scrive risultati/e63_riga_modello.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
A = (0.6, 0.75, 0.9)
MU = (0.5, 1.0)
TAU = (1.5, 4.0)
SEMI = (1, 2, 3)
LAM_PAGINA, GAMMA, TENTATIVI = 0.75, 3, 20
D = misure.divisore(misure.GLIFI_EVA)
BASE = ('h2', 'spazio', 'uniche', 'tipi', 'ripetizione', 'omogeneità', 'gradiente', 'legame')
BERSAGLI = ('lunghezze vicine', 'verticale')


def scrivi(struttura, globale, giunture, modifiche, a, mu, tau, seme):
    import e56_copia_o_componi as e56
    rnd = random.Random(seme)
    pagine, viste, precedente = [], set(), []
    for righe_pagina in struttura:
        recente = defaultdict(Counter)
        for riga in precedente:
            for u in riga:
                e56.conta(recente, u, 0.5)
        pagina = []
        for n in righe_pagina:
            if pagina:
                cand = list(range(1, len(pagina) + 1))
                d = rnd.choices(cand, weights=[math.exp(-x / tau) for x in cand])[0]
                modello = pagina[-d]
            else:
                modello = precedente[-1] if precedente else None
            riga = []
            for i in range(n):
                scelta = None
                for _t in range(TENTATIVI):
                    if modello and rnd.random() < a:
                        u = modello[min(i, len(modello) - 1)]
                        for _m in range(generatori.poisson(rnd, mu)):
                            prova = modifiche.modifica(u, rnd)
                            if modifiche.valida(prova):
                                u = prova
                    else:
                        for _n in range(TENTATIVI):
                            u = e56.componi(globale, recente, LAM_PAGINA, rnd)
                            if u not in viste:
                                break
                    scelta = u
                    if not riga:
                        break
                    r = giunture.get((riga[-1][-1], u[0]), e56.R_IGNOTA)
                    if rnd.random() < min(1.0, r ** GAMMA):
                        break
                riga.append(tuple(scelta))
                viste.add(tuple(scelta))
                e56.conta(recente, scelta)
            pagina.append(riga)
        precedente = pagina
        pagine.append([[''.join(u) for u in r] for r in pagina])
    return pagine


_MODIFICHE = None


def una(args):
    """Un lavoro del Pool; le modifiche si costruiscono nel processo (non si possono passare:
    contengono una funzione locale)."""
    global _MODIFICHE
    import e61_pagella as e61
    struttura, globale, giunture, voy, soglia_ab, a, mu, tau, seme = args
    if _MODIFICHE is None:
        _MODIFICHE = generatori.Modifiche(voy, D)
    modifiche = _MODIFICHE
    return (a, mu, tau, seme), e61.scheda(scrivi(struttura, globale, giunture, modifiche, a, mu, tau, seme), D, voy, soglia_ab)


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
    lavori = [(struttura, globale, giunture, voy, soglia_ab, a, mu, tau, s) for a in A for mu in MU for tau in TAU for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for chiave, r in pool.imap(una, lavori):
            ris['a %.2f, mu %.1f, tau %.1f, seme %d' % chiave] = r
            per[chiave[:3]].append(r)
    medie = OrderedDict()
    for chiave, gruppo in per.items():
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(m, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        m['esiti'] = esiti
        m['compatibile'] = all(esiti[p] for p in BASE)
        nome = 'a %.2f, mu %.1f, tau %.1f' % chiave
        medie[nome] = m
        fuori = [p for p in esiti if p not in BASE and p not in BERSAGLI]
        print('%-26s base %d/8 %s | bersagli %s | fuori campione %d/%d | rip %.2f somigl %.1f%%/%.1f%% h2 %.2f legame %.3f uniche %.2f tipi %.3f lungh %.3f vert %.3f forma %.2f' % (
            nome, sum(esiti[p] for p in BASE), 'COMPATIBILE' if m['compatibile'] else '',
            ''.join('✓' if esiti[p] else '·' for p in BERSAGLI), sum(esiti[p] for p in fuori), len(fuori),
            m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'], m['confine'],
            m['hapax_34000'], m['tipi_su_parole'], m['V6_autocorrelazione_lunghezze'], m['verticale'], m.get('V8_forma', 0)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e63_riga_modello.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE)
    out = ['# e63 — La riga modello', '',
           'Bande della pagella (e61). Compatibile = le 8 proprietà di base; bersagli del meccanismo: %s; le altre '
           'fuori campione. Medie su tre semi. Preregistrazione: `preregistrazioni/e63.md`.' % ', '.join(BERSAGLI), '',
           '| combinazione | base | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %d/8%s | %s |' % (nome, sum(m['esiti'][p] for p in BASE),
                                             ' **compatibile**' if m['compatibile'] else '',
                                             ' | '.join('✓' if m['esiti'][p] else '·' for p in props)))
    with open(os.path.join(RISULTATI, 'e63_riga_modello.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
