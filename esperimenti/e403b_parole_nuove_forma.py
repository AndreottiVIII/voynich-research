# -*- coding: utf-8 -*-
"""Esperimento 403b: le parole nuove, secondo tentativo. Stessa prova dell'e403 (nel Voynich vero si sostituiscono solo le
parole uniche nel libro), con la forma imparata sulle parole uniche (parole_nuove.FormeUniche): T-L trigrammi con la
lunghezza controllata, T-LP anche per tipo di posto nella riga, T-LPS anche scelti secondo il profilo dei segni della pagina.

    PROCESSI=10 python esegui.py e403b
    python esperimenti/e403b_parole_nuove_forma.py --prova     (costruzione e forma, nessun giudice)

Preregistrazione: preregistrazioni/e403b.md. Scrive risultati/e403b_parole_nuove_forma.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e400_scala_controlli as e400
import e403_parole_nuove as e403

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
MODI = ('T-L', 'T-LP', 'T-LPS')
PREVISTE = {'T-L': (0.68, 0.80), 'T-LP': (0.62, 0.74), 'T-LPS': (0.55, 0.68)}


def sostituisci(rr, modo, seme):
    import parole_nuove
    from disposizione import posizione
    fu = parole_nuove.FormeUniche(rr)
    conta = fu.conta
    rnd = random.Random(403500 + 1000 * MODI.index(modo) + seme)
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).extend(ps)
    profili = {p: fu.profilo(ws) for p, ws in per.items()}
    out, inventate = [], []
    for p, ini, ps in rr:
        nuova = []
        for j, w in enumerate(ps):
            if conta[w] == 1:
                w = fu.inventa(modo, 4 * bool(ini) + posizione(j, len(ps)), profili[p], rnd)
                inventate.append(w)
            nuova.append(w)
        out.append((p, ini, nuova))
    return out, inventate, conta


def lavoro(args):
    modo, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    rr, _ = e400.voynich()
    t, inventate, conta = sostituisci(rr, modo, seme)
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    s = e403.sotto_auc(k['vt266'], tab)
    nf = tab[2]
    return args, OrderedDict([('solo_sacco', s['solo sacco']), ('sotto', OrderedDict((n, s[n]) for n in e403.SOTTO)), ('pesanti', s['pesanti']),
                              ('AUC_e266', e266.confronto(k['vt266'], tab)['AUC']),
                              ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])['AUC']),
                              ('forma', e403.forma(inventate, conta)),
                              ('pagina', OrderedDict((n, float(tab[1][:, nf.index(n)].mean())) for n in ('G3 lunghezza media', 'G3 lunghezza deviazione', 'G1 p', 'G1 f', 'G1 m',
                                                                                                         'G1 s', 'G9 JSD pagina-manoscritto') if n in nf))])


def prova():
    rr, _ = e400.voynich()
    conta = Counter(w for _, _, ps in rr for w in ps)
    print('Voynich, parole uniche: %s' % {n: round(x, 3) for n, x in e403.forma([w for w, n in conta.items() if n == 1], conta).items()})
    for modo in MODI:
        t, inv, _ = sostituisci(rr, modo, 1)
        assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in rr]
        assert len(inv) == len(set(inv)) == sum(n == 1 for n in conta.values()) and not set(inv) & set(conta)
        print('%-6s %d inventate, forma %s, esempi %s' % (modo, len(inv), {n: round(x, 3) for n, x in e403.forma(inv, conta).items()}, inv[:8]))
    print('costruzione a posto')


def main():
    if '--prova' in sys.argv:
        return prova()
    lavori = [(m, s) for m in MODI for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            print('%-6s seme %d: solo sacco %.3f %s | e231 %.3f e266 %.3f | forma %s' % (
                a[0], a[1], r['solo_sacco'], {n: round(x, 2) for n, x in r['sotto'].items()}, r['AUC_e231'], r['AUC_e266'],
                {n: round(x, 2) for n, x in r['forma'].items()}), flush=True)
    sintesi = OrderedDict()
    for m in MODI:
        rs = [ris[(m, s)] for s in SEMI]
        media = lambda f: statistics.mean(f(r) for r in rs)
        sintesi[m] = OrderedDict([('solo_sacco', media(lambda r: r['solo_sacco'])), ('min_max', [min(r['solo_sacco'] for r in rs), max(r['solo_sacco'] for r in rs)]),
                                  ('prevista', PREVISTE[m]), ('sotto', OrderedDict((n, media(lambda r: r['sotto'][n])) for n in e403.SOTTO)),
                                  ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
                                  ('forma', OrderedDict((n, media(lambda r: r['forma'][n])) for n in rs[0]['forma'])),
                                  ('pagina', OrderedDict((n, media(lambda r: r['pagina'][n])) for n in rs[0]['pagina'])), ('pesanti', rs[0]['pesanti'])])
    out = OrderedDict([('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in lavori))])
    json.dump(out, open(os.path.join(RISULTATI, 'e403b_parole_nuove_forma.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e403b — Le parole nuove, secondo tentativo: forma imparata sulle parole uniche', '',
          'Voynich vero con ogni parola unica nel libro sostituita da una inventata; semi 1–4 (medie). Solo sacco: pavimento 0,50; nell\'e403 il migliore era 0,774. '
          'Parole uniche del Voynich: lunghezza 5,944 ± 1,570; a una modifica da una nota 0,715; unione di due note 0,678. Preregistrazione: `preregistrazioni/e403b.md`.', '',
          '| generatore | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD | AUC e231 | AUC e266 | lunghezza | deviazione | a una modifica | unione |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for m, x in sintesi.items():
        md.append('| %s | %.3f (%.3f–%.3f) | %.2f–%.2f | %s | %.3f | %.3f | %s |' % (
            m, x['solo_sacco'], x['min_max'][0], x['min_max'][1], x['prevista'][0], x['prevista'][1], ' | '.join('%.2f' % v for v in x['sotto'].values()),
            x['AUC_e231'], x['AUC_e266'], ' | '.join('%.3f' % v for v in x['forma'].values())))
    primo = next(iter(sintesi.values()))
    md += ['', '## Valori di pagina (media delle pagine)', '', '| generatore | ' + ' | '.join(primo['pagina']) + ' |', '|---|' + '---|' * len(primo['pagina'])]
    md += ['| %s | %s |' % (m, ' | '.join('%.4f' % v for v in x['pagina'].values())) for m, x in sintesi.items()]
    md += ['', '## Caratteristiche più pesanti del solo sacco (seme 1)', '']
    for m, x in sintesi.items():
        md += ['**%s**' % m, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti']]
        md.append('')
    open(os.path.join(RISULTATI, 'e403b_parole_nuove_forma.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({m: round(x['solo_sacco'], 3) for m, x in sintesi.items()}))


if __name__ == '__main__':
    main()
