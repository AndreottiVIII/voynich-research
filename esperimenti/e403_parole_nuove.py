# -*- coding: utf-8 -*-
"""Esperimento 403: il sacco, primo pezzo: le parole nuove. Nel Voynich vero si sostituisce solo ogni parola unica nel
libro con una parola inventata (voynichizzatore/parole_nuove.py: variante-libro, variante-pagina, trigrammi, mista); tutto
il resto resta vero. Si misura il "solo sacco" (giudice dell'e266 su G1, G2, G3, JSD pagina-manoscritto) con i
sottogruppi, i giudici interi e un pannello sulla forma delle parole inventate.

    PROCESSI=8 python esegui.py e403
    python esperimenti/e403_parole_nuove.py --prova     (costruzione e pannello della forma, nessun giudice)

Preregistrazione: preregistrazioni/e403.md. Scrive risultati/e403_parole_nuove.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e400_scala_controlli as e400

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
MODI = ('variante-libro', 'variante-pagina', 'trigrammi', 'mista')
PREVISTE = {'variante-libro': (0.60, 0.72), 'variante-pagina': (0.56, 0.68), 'trigrammi': (0.58, 0.70), 'mista': (0.55, 0.65)}
SOTTO = OrderedDict([('G1', ('G1 ',)), ('G2', ('G2 ',)), ('G3', ('G3 ',)), ('JSD', ('G9 JSD pagina-manoscritto',))])
D = misure.divisore(misure.GLIFI_EVA)


def sostituisci(rr, modo, seme, mod):
    """Il testo con ogni parola unica nel libro sostituita da una inventata; restituisce anche le inventate."""
    import parole_nuove
    conta = Counter(w for _, _, ps in rr for w in ps)
    pn = parole_nuove.ParoleNuove(conta, mod)
    rnd = random.Random(403000 + 1000 * MODI.index(modo) + seme)
    tipi = OrderedDict()
    for p, _, ps in rr:
        tipi.setdefault(p, OrderedDict()).update((w, 1) for w in ps if conta[w] >= 2)
    out, inventate = [], []
    for p, ini, ps in rr:
        nuova = []
        for w in ps:
            if conta[w] == 1:
                w = pn.inventa(modo, list(tipi[p]), rnd)
                inventate.append(w)
            nuova.append(w)
        out.append((p, ini, nuova))
    return out, inventate, conta


def forma(parole, conta):
    """Lunghezza media e deviazione, quota a una modifica da una parola vista almeno due volte."""
    base = {tuple(D(w)) for w, n in conta.items() if n >= 2}
    alf = sorted({g for u in base for g in u})

    def vicina(u):
        for i in range(len(u)):
            if u[:i] + u[i + 1:] in base or any(u[:i] + (g,) + u[i + 1:] in base for g in alf if g != u[i]):
                return True
        return any(u[:i] + (g,) + u[i:] in base for i in range(len(u) + 1) for g in alf)
    U = [tuple(D(w)) for w in parole]
    return OrderedDict([('lunghezza media', statistics.mean(map(len, U))), ('lunghezza deviazione', statistics.pstdev(list(map(len, U)))),
                        ('a una modifica da una nota', statistics.mean(vicina(u) for u in U)),
                        ('unione di due note', statistics.mean(any(u[:i] in base and u[i:] in base for i in range(1, len(u))) for u in U))])


def sotto_auc(vt, gt):
    import e231_discriminatore as e231
    nv, Xv, nf = vt
    ng, Xg, _ = gt
    comuni = [p for p in nv if p in set(ng)]
    iv, ig = {p: i for i, p in enumerate(nv)}, {p: i for i, p in enumerate(ng)}
    X = np.vstack([Xv[[iv[p] for p in comuni]], Xg[[ig[p] for p in comuni]]])
    y = np.array([0] * len(comuni) + [1] * len(comuni))
    gruppi = np.array(comuni + comuni)
    out = OrderedDict()
    tutte = [i for i, n in enumerate(nf) if any(n.startswith(pre) for pres in SOTTO.values() for pre in pres)]
    out['solo sacco'] = e231.auc_cv(X[:, tutte], y, gruppi)
    for nome, pres in SOTTO.items():
        col = [i for i, n in enumerate(nf) if n.startswith(pres)]
        out[nome] = e231.auc_cv(X[:, col], y, gruppi)
    m = e231.modello().fit(X[:, tutte], y)
    coef = m[-1].coef_[0]
    out['pesanti'] = [(nf[tutte[i]], float(coef[i]), float(X[y == 0][:, tutte[i]].mean()), float(X[y == 1][:, tutte[i]].mean())) for i in np.argsort(-np.abs(coef))[:10]]
    return out


def lavoro(args):
    modo, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    rr, _ = e400.voynich()
    conta = Counter(w for _, _, ps in rr for w in ps)
    if modo == 'V':
        return args, OrderedDict([('forma', forma([w for w, n in conta.items() if n == 1], conta))])
    t, inventate, _ = sostituisci(rr, modo, seme, k['c2']['mod'])
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    s = sotto_auc(k['vt266'], tab)
    nf = tab[2]
    return args, OrderedDict([('solo_sacco', s['solo sacco']), ('sotto', OrderedDict((n, s[n]) for n in SOTTO)), ('pesanti', s['pesanti']),
                              ('AUC_e266', e266.confronto(k['vt266'], tab)['AUC']),
                              ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])['AUC']),
                              ('forma', forma(inventate, conta)),
                              ('pagina', OrderedDict((n, float(tab[1][:, nf.index(n)].mean())) for n in ('G3 lunghezza media', 'G3 lunghezza deviazione', 'G3 uniche nel testo',
                                                                                                         'G3 tipi su parole', 'G9 JSD pagina-manoscritto')))])


def prova():
    import e251_lessico_sezione as e251
    rr, _ = e400.voynich()
    mod = e251._prepara()['c2']['mod']
    conta = Counter(w for _, _, ps in rr for w in ps)
    print('Voynich, parole uniche: %s' % {n: round(x, 3) for n, x in forma([w for w, n in conta.items() if n == 1], conta).items()})
    for modo in MODI:
        t, inv, _ = sostituisci(rr, modo, 1, mod)
        assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in rr]
        assert len(inv) == len(set(inv)) == sum(n == 1 for n in conta.values()) and not set(inv) & set(conta)
        assert all(a == b or conta[a] == 1 for (_, _, x), (_, _, y) in zip(rr, t) for a, b in zip(x, y))
        print('%-16s %d inventate, esempi %s' % (modo, len(inv), inv[:6]))
    print('costruzione a posto')


def main():
    if '--prova' in sys.argv:
        return prova()
    lavori = [('V', 0)] + [(m, s) for m in MODI for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%-16s seme %d: solo sacco %.3f %s | e231 %.3f e266 %.3f | forma %s' % (
                    a[0], a[1], r['solo_sacco'], {n: round(x, 2) for n, x in r['sotto'].items()}, r['AUC_e231'], r['AUC_e266'],
                    {n: round(x, 2) for n, x in r['forma'].items()}), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for m in MODI:
        rs = [ris[(m, s)] for s in SEMI]
        media = lambda f: statistics.mean(f(r) for r in rs)
        sintesi[m] = OrderedDict([('solo_sacco', media(lambda r: r['solo_sacco'])), ('min_max', [min(r['solo_sacco'] for r in rs), max(r['solo_sacco'] for r in rs)]),
                                  ('prevista', PREVISTE[m]), ('sotto', OrderedDict((n, media(lambda r: r['sotto'][n])) for n in SOTTO)),
                                  ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
                                  ('forma', OrderedDict((n, media(lambda r: r['forma'][n])) for n in rs[0]['forma'])),
                                  ('pagina', OrderedDict((n, media(lambda r: r['pagina'][n])) for n in rs[0]['pagina'])), ('pesanti', rs[0]['pesanti'])])
    out = OrderedDict([('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in lavori if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e403_parole_nuove.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e403 — Il sacco, primo pezzo: le parole nuove', '',
          'Voynich vero con ogni parola unica nel libro (4.776) sostituita da una parola inventata; semi 1–4 (medie). "Solo sacco" = giudice dell\'e266 su G1, G2, G3 e JSD '
          'pagina-manoscritto; pavimento 0,50. Preregistrazione: `preregistrazioni/e403.md`.', '',
          '| generatore | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|---|---|']
    for m, x in sintesi.items():
        md.append('| %s | %.3f (%.3f–%.3f) | %.2f–%.2f | %s | %.3f | %.3f |' % (m, x['solo_sacco'], x['min_max'][0], x['min_max'][1], x['prevista'][0], x['prevista'][1],
                                                                             ' | '.join('%.2f' % v for v in x['sotto'].values()), x['AUC_e231'], x['AUC_e266']))
    md += ['', '## Forma delle parole inventate', '', '| | ' + ' | '.join(voy['forma']) + ' |', '|---|' + '---|' * len(voy['forma']),
           '| Voynich, parole uniche | ' + ' | '.join('%.3f' % v for v in voy['forma'].values()) + ' |']
    md += ['| %s | %s |' % (m, ' | '.join('%.3f' % v for v in x['forma'].values())) for m, x in sintesi.items()]
    md += ['', '## Valori di pagina (media delle pagine)', '', '| generatore | ' + ' | '.join(next(iter(sintesi.values()))['pagina']) + ' |',
           '|---|' + '---|' * len(next(iter(sintesi.values()))['pagina'])]
    md += ['| %s | %s |' % (m, ' | '.join('%.4f' % v for v in x['pagina'].values())) for m, x in sintesi.items()]
    md += ['', '## Caratteristiche più pesanti del solo sacco (seme 1)', '']
    for m, x in sintesi.items():
        md += ['**%s**' % m, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti']]
        md.append('')
    open(os.path.join(RISULTATI, 'e403_parole_nuove.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({m: round(x['solo_sacco'], 3) for m, x in sintesi.items()}))


if __name__ == '__main__':
    main()
