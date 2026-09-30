# -*- coding: utf-8 -*-
"""Esperimento 57: "copia o componi" (e56) con parole composte volutamente nuove.

La parola composta deve essere una forma mai scritta prima nel testo (fino a 20 tentativi); le
copie restano esatte. Griglia c x lambda x tau con gamma 3. Bande e validazione dell'e56.
Preregistrazione: preregistrazioni/e57.md. Scrive risultati/e57_copia_o_componi_nuove.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e56_copia_o_componi as e56

RISULTATI = os.path.join(QUI, '..', 'risultati')
C = (0.2, 0.35, 0.5)
LAMBDA = (0.7, 0.85, 0.95)
TAU = (1.5, 4.0)
GAMMA = 3
SEMI = (1, 2, 3)


def scrivi(struttura, globale, giunture, c, lam, tau, gamma, seme):
    rnd = random.Random(seme)
    pagine, precedente, viste = [], [], set()
    for righe_pagina in struttura:
        recente = defaultdict(Counter)
        for u in precedente:
            e56.conta(recente, u, 0.5)
        pagina, scritte_pagina = [], []
        for n in righe_pagina:
            riga = []
            for _ in range(n):
                scelta = None
                for _t in range(e56.TENTATIVI):
                    if (pagina or riga) and rnd.random() < c:
                        cand = [(0, riga)] if riga else []
                        cand += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                        _, fonte = rnd.choices(cand, weights=[math.exp(-d / tau) for d, _ in cand])[0]
                        u = rnd.choice(fonte)
                    else:
                        for _n in range(e56.TENTATIVI):
                            u = e56.componi(globale, recente, lam, rnd)
                            if u not in viste:
                                break
                    scelta = u
                    if not riga:
                        break
                    r = giunture.get((riga[-1][-1], u[0]), e56.R_IGNOTA)
                    if rnd.random() < min(1.0, r ** gamma):
                        break
                riga.append(scelta)
                scritte_pagina.append(scelta)
                viste.add(scelta)
                e56.conta(recente, scelta)
            pagina.append(riga)
        precedente = scritte_pagina
        pagine.append([[''.join(u) for u in r] for r in pagina])
    return pagine


def una(args):
    struttura, globale, giunture, c, lam, tau, gamma, seme = args
    return (c, lam, tau, gamma, seme), e56.misura(scrivi(struttura, globale, giunture, c, lam, tau, gamma, seme))


def main():
    from e07_codifiche import pagine_voynich
    import e46_codice_accorto as e46
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    pv = pagine_voynich(corrente)
    globale = defaultdict(Counter)
    for w in trascrizione.parole(corrente):
        e56.conta(globale, e56.D(w))
    globale = {k: dict(v) for k, v in globale.items()}
    giunture = e46.tabella_giunture([r for p in pv for r in p], e56.D)
    struttura = [[len(r) for r in p] for p in pv]
    ris = OrderedDict()
    v = e56.misura(pv)
    ris['Voynich'] = v
    lavori = [(struttura, globale, giunture, c, lam, tau, GAMMA, s) for c in C for lam in LAMBDA for tau in TAU for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for chiave, r in pool.imap(una, lavori):
            ris['c %.2f, lambda %.2f, tau %.1f, seme %d' % (chiave[0], chiave[1], chiave[2], chiave[4])] = r
            per[chiave[:3]].append(r)
    medie = OrderedDict()
    for chiave, gruppo in per.items():
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float))]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        m['bande'] = e56.bande(m)
        m['compatibile'] = all(m['bande'].values())
        m['validazione'] = e56.validazione(m, v)
        nome = 'c %.2f, lambda %.2f, tau %.1f' % chiave
        medie[nome] = m
        print('%-30s rip %.2f somigl %.1f%%/%.1f%% h2 %.2f legame %.3f uniche %.2f tipi %.3f | bande %d/7 %s %s | %s' % (
            nome, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
            m['confine'], m['hapax_34000'], m['tipi_su_parole'], sum(m['bande'].values()),
            ','.join(k for k, x in m['bande'].items() if not x), 'COMPATIBILE' if m['compatibile'] else '',
            ' '.join(k for k, x in m['validazione'].items() if x)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e57_copia_o_componi_nuove.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    out = ['# e57 — "Copia o componi" con parole composte nuove', '',
           'Come l\'e56, ma la parola composta dev\'essere una forma mai scritta; γ = 3. Medie su tre semi. Compatibile = '
           'tutte e sette le bande. Preregistrazione: `preregistrazioni/e57.md`.', '',
           '| combinazione | ripetizione | somigl. riga | 6 righe | h2 | legame | uniche | tipi | bande (fuori) | validazione |',
           '|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.1f%% | %.1f%% | %.2f | %.3f | %.2f | %.3f | | |' % (
               v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['h2'], v['confine'],
               v['hapax_34000'], v['tipi_su_parole'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.1f%% | %.1f%% | %.2f | %.3f | %.2f | %.3f | %d/7 (%s)%s | %s |' % (
            nome, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
            m['confine'], m['hapax_34000'], m['tipi_su_parole'], sum(m['bande'].values()),
            ', '.join(k for k, x in m['bande'].items() if not x), ' **compatibile**' if m['compatibile'] else '',
            ', '.join(k for k, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e57_copia_o_componi_nuove.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
