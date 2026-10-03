# -*- coding: utf-8 -*-
"""Esperimento 402: quanto costa il sacco di pagina dei due generatori esistenti. Per il corpo della v5 e per il modello del
Voynich (seconda forma tarata), semi 1-4: il testo originale e lo stesso testo con le parole di ogni pagina ridisposte dal
modello dell'e401b. Giudici e231 ed e266 con gruppi, pagelle, pannello, e l'AUC del solo sacco (giudice dell'e266 ristretto
alle caratteristiche che non dipendono dall'ordine: G1, G2, G3, JSD pagina-manoscritto).

    PROCESSI=8 python esegui.py e402
    python esperimenti/e402_sacco_generatori.py --prova     (disposizione con parole inventate su 12 pagine, nessun giudice)

Preregistrazione: preregistrazioni/e402.md. Scrive risultati/e402_sacco_generatori.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import trascrizione
import e400_scala_controlli as e400
import e401_disposizione as e401

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
GENERATORI = OrderedDict([('v5', 'corpo della v5 (copia e modifica)'), ('modello', 'modello del Voynich, seconda forma tarata')])
VARIANTI = ('originale', 'ridisposto')
PREVISTE = {('v5', 'originale'): (0.90, 0.94), ('v5', 'ridisposto'): (0.84, 0.92), ('modello', 'originale'): (0.97, 1.0), ('modello', 'ridisposto'): (0.90, 0.97)}
PREVISTE_SACCO = {'v5': (0.80, 0.88), 'modello': (0.88, 0.95)}


def pesi_e401b():
    return json.load(open(os.path.join(RISULTATI, 'e401b_disposizione_regolata.json'), encoding='utf-8'))['regolazione']['pesi']


def genera(gen, seme):
    if gen == 'v5':
        import versioni
        rr = versioni.corpo(versioni.V5, seme)
    else:
        import modello
        rr = modello.genera(seme, forza={'memoria': 2.0, 'coppia': 3.0}, beta=OrderedDict((x, 1.5) for x in modello.BETA))
    out = [(p, bool(ini), [w for w in ps if trascrizione.pulita(w)]) for p, ini, ps in rr]
    return [x for x in out if x[2]]


def solo_sacco(vt, gt):
    """AUC del giudice dell'e266 sulle sole caratteristiche che non dipendono dall'ordine delle parole."""
    import e231_discriminatore as e231
    nv, Xv, nf = vt
    ng, Xg, _ = gt
    col = [i for i, n in enumerate(nf) if n.startswith(('G1 ', 'G2 ', 'G3 ')) or n == 'G9 JSD pagina-manoscritto']
    comuni = [p for p in nv if p in set(ng)]
    iv, ig = {p: i for i, p in enumerate(nv)}, {p: i for i, p in enumerate(ng)}
    X = np.vstack([Xv[[iv[p] for p in comuni]], Xg[[ig[p] for p in comuni]]])[:, col]
    y = np.array([0] * len(comuni) + [1] * len(comuni))
    return e231.auc_cv(X, y, np.array(comuni + comuni))


def misura(t, k):
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    pg = e251.pagella_grezza(k['c'], t)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    d266 = e266.confronto(k['vt266'], tab)
    return OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', e293.pagella_estesa(t)),
                        ('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('AUC_e266', d266['AUC']),
                        ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti']), ('pesanti_e231', d231['piu_pesanti']),
                        ('AUC_solo_sacco', solo_sacco(k['vt266'], tab)), ('pannello', e401.pannello(tab))])


def lavoro(args):
    gen, seme = args
    import e251_lessico_sezione as e251
    import e293_banco as e293
    k = e251._prepara()
    voy, _ = e400.voynich()
    if gen == 'V':
        return args, OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(voy))])
    t = genera(gen, seme)
    r = e401.modello(voy).disponi(t, 402000 + 1000 * list(GENERATORI).index(gen) + seme, 'D3', pesi=pesi_e401b())
    return args, OrderedDict([('originale', misura(t, k)), ('ridisposto', misura(r, k))])


def prova():
    import random
    voy, _ = e400.voynich()
    pagine = list(OrderedDict((p, 1) for p, _, _ in voy))[:12]
    rnd = random.Random(1)
    sotto = [(p, ini, [w + 'o' if rnd.random() < 0.2 else w for w in ps]) for p, ini, ps in voy if p in pagine]
    m = e401.modello(voy)
    t = m.disponi(sotto, 1, 'D3', pesi=pesi_e401b(), passate=10)
    assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in sotto]
    assert sorted(w for _, _, ps in t for w in ps) == sorted(w for _, _, ps in sotto for w in ps)
    nuove = len({w for _, _, ps in sotto for w in ps} - m.att)
    print('disposizione con %d parole non del Voynich: a posto; pesi %s' % (nuove, pesi_e401b()))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    lavori = [('V', 0)] + [(g, s) for g in GENERATORI for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                for v in VARIANTI:
                    x = r[v]
                    print('%-8s seme %d %-10s: pagella %d riga %s | AUC e231 %.3f e266 %.3f solo sacco %.3f | %s' % (
                        a[0], a[1], v, x['pagella'], x['riga'], x['AUC_e231'], x['AUC_e266'], x['AUC_solo_sacco'],
                        {g: round(z, 2) for g, z in x['gruppi_e266'].items() if z is not None}), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for g in GENERATORI:
        for v in VARIANTI:
            rs = [ris[(g, s)][v] for s in SEMI]
            for r in rs:
                r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
            media = lambda f: statistics.mean(f(r) for r in rs)
            sintesi['%s %s' % (g, v)] = OrderedDict([
                ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
                ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]), ('prevista_e266', PREVISTE[(g, v)]),
                ('AUC_solo_sacco', media(lambda r: r['AUC_solo_sacco'])), ('prevista_solo_sacco', PREVISTE_SACCO[g]),
                ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
                ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
                ('semi_con_riga', sum(bool(r['riga']) for r in rs)),
                ('materie_mancate', sorted({m for r in rs for m in r['mancano']} | {m for r in rs for m in e293.FASCE if m not in r['estese_passate']})),
                ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])),
                ('pesanti_e266', rs[0]['pesanti_e266'][:10]), ('pesanti_e231', rs[0]['pesanti_e231'][:6])])
    out = OrderedDict([('Voynich', voy), ('pesi_disposizione', pesi_e401b()), ('sintesi', sintesi),
                       ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in lavori if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e402_sacco_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(next(iter(sintesi.values()))['gruppi'])
    md = ['# e402 — Quanto costa il sacco di pagina dei due generatori esistenti', '',
          'Corpo della v5 e modello del Voynich, semi 1–4 (medie): testo originale e lo stesso testo con le parole di ogni pagina ridisposte dal modello '
          'dell\'e401b. "Solo sacco" = giudice dell\'e266 sulle sole caratteristiche che non dipendono dall\'ordine (G1, G2, G3, JSD pagina-manoscritto). '
          'Riferimento: sacco vero ridisposto 0,533 / 0,659 (e401b). Preregistrazione: `preregistrazioni/e402.md`.', '',
          '| testo | AUC e231 | AUC e266 (min–max) | prevista e266 | solo sacco | previsto | pagella | estese | riga | ' + ' | '.join(gr) + ' |',
          '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for n, x in sintesi.items():
        md.append('| %s | %.3f | %.3f (%.3f–%.3f) | %.2f–%.2f | %.3f | %.2f–%.2f | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
            n, x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['prevista_e266'][0], x['prevista_e266'][1],
            x['AUC_solo_sacco'], x['prevista_solo_sacco'][0], x['prevista_solo_sacco'][1], x['pagella_media'], x['estese_media'], x['semi_con_riga'],
            ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', '## Pannello (media delle pagine)', '', '| misura | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    for n in voy['pannello']:
        md.append('| %s | %.4f | %s |' % (n, voy['pannello'][n], ' | '.join('%.4f' % x['pannello'][n] for x in sintesi.values())))
    md += ['', '## Perché: materie mancate e caratteristiche più pesanti (primo seme)', '']
    for n, x in sintesi.items():
        md += ['**%s.** Materie mancate in almeno un seme: %s.' % (n, ', '.join(x['materie_mancate']) or 'nessuna'), '',
               '| giudice | caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|---|']
        md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e231']]
        md.append('')
    open(os.path.join(RISULTATI, 'e402_sacco_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({n: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), round(x['AUC_solo_sacco'], 3)] for n, x in sintesi.items()}))


if __name__ == '__main__':
    main()
