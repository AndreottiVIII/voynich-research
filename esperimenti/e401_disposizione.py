# -*- coding: utf-8 -*-
"""Esperimento 401: la disposizione. Per ogni pagina si tengono il sacco delle parole vere e l'impaginazione vera; il
modello di voynichizzatore/disposizione.py decide dove va ogni parola, a strati (D1 prime righe, D2 otto tipi di posto,
D3 piu' i legami fra vicine). Giudici e231 ed e266 con gruppi e caratteristiche pesanti, pagelle, pannello di valori grezzi.
Si confronta con la scala dell'e400 (O4 0,998, O3 0,993, O1 0,595).

    PROCESSI=10 python esegui.py e401
    python esperimenti/e401_disposizione.py --prova     (solo costruzione su poche pagine, nessuna misura)

Preregistrazione: preregistrazioni/e401.md. Scrive risultati/e401_disposizione.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e400_scala_controlli as e400

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('D1', 'solo prima riga di paragrafo o no'), ('D2', 'otto tipi di posto'), ('D3', 'otto tipi di posto e legami fra vicine')])
PREVISTE = {'D1': (0.985, 0.995), 'D2': (0.70, 0.85), 'D3': (0.62, 0.75)}
PANNELLO = ('G4 inizio p', 'G4 inizio t', 'G4 inizio ch', 'G4 fine m', 'G7 ultime in m', 'G7 lunghezza prima parola', 'G7 lunghezza ultima parola',
            'G4 unioni attestate', 'G4 somiglianza fra vicine', 'G6 coppie viste altrove', 'G6 coppie identiche', 'G8 p prime righe meno altre',
            'G8 lunghezza parole prime righe', 'G9 JSD prima-seconda meta')
_M = {}


def modello(rr):
    if 'm' not in _M:
        import disposizione
        _M['m'] = disposizione.Disposizione(rr)
    return _M['m']


def pannello(tab):
    _, X, nf = tab
    return OrderedDict((n, float(X[:, nf.index(n)].mean())) for n in PANNELLO if n in nf)


def lavoro(args):
    strato, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    rr, _ = e400.voynich()
    if strato == 'V':
        return args, OrderedDict([('pannello', pannello(k['vt266'])), ('estesa', e293.pagella_estesa(rr))])
    t = modello(rr).disponi(rr, 401000 + 1000 * list(STRATI).index(strato) + seme, strato)
    pg = e251.pagella_grezza(k['c'], t)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    d266 = e266.confronto(k['vt266'], tab)
    return args, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', e293.pagella_estesa(t)),
                              ('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('AUC_e266', d266['AUC']),
                              ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti']), ('pannello', pannello(tab))])


def prova():
    """Controllo della costruzione su 12 pagine, senza giudici: stessa impaginazione, stesso sacco, strati diversi fra loro."""
    rr, _ = e400.voynich()
    m = modello(rr)
    pagine = list(OrderedDict((p, 1) for p, _, _ in rr))[:12]
    sotto = [x for x in rr if x[0] in pagine]
    for s in STRATI:
        t = m.disponi(sotto, 1, s, passate=20)
        assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in sotto], s
        for p in pagine:
            assert sorted(w for q, _, ps in t if q == p for w in ps) == sorted(w for q, _, ps in sotto if q == p for w in ps), (s, p)
        assert t == m.disponi(sotto, 1, s, passate=20), s
        print('%s: %d righe, righe identiche al Voynich %.3f' % (s, len(t), sum(a == b for a, b in zip(t, sotto)) / len(t)))
    print('costruzione a posto; tratti %d' % len(m.indice))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    lavori = [('V', 0)] + [(s, seme) for s in STRATI for seme in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%-3s seme %d: pagella %d riga %s | AUC e231 %.3f e266 %.3f | %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['AUC_e231'], r['AUC_e266'],
                    {g: round(v, 2) for g, v in r['gruppi_e266'].items() if v is not None}), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for s in STRATI:
        rs = [ris[(s, seme)] for seme in SEMI]
        for r in rs:
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
        media = lambda f: statistics.mean(f(r) for r in rs)
        sintesi[s] = OrderedDict([
            ('che cosa', STRATI[s]), ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
            ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]), ('prevista_e266', PREVISTE[s]),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)),
            ('materie_mancate', sorted({m for r in rs for m in r['mancano']} | {m for r in rs for m in e293.FASCE if m not in r['estese_passate']})),
            ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])),
            ('pesanti_e266', rs[0]['pesanti_e266'][:8])])
    out = OrderedDict([('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in lavori if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e401_disposizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['D1']['gruppi'])
    md = ['# e401 — La disposizione delle parole della pagina', '',
          'Sacco di parole vero e impaginazione vera per ogni pagina; il modello decide i posti. Semi 1–4 (medie). Riferimenti dall\'e400: '
          'parole rimescolate nella pagina 0,998 (O4), con le prime righe a parte 0,993 (O3), solo righe rimescolate 0,595 (O1). '
          'Preregistrazione: `preregistrazioni/e401.md`.', '',
          '| strato | che cosa | AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | ' + ' | '.join(gr) + ' |',
          '|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %.2f–%.2f | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['prevista_e266'][0], x['prevista_e266'][1],
            x['pagella_media'], x['estese_media'], x['semi_con_riga'], ' | '.join('%.2f' % v for v in x['gruppi'].values())))
    md += ['', '## Pannello: valori grezzi (media delle pagine)', '', '| misura | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    for n in voy['pannello']:
        md.append('| %s | %.4f | %s |' % (n, voy['pannello'][n], ' | '.join('%.4f' % x['pannello'][n] for x in sintesi.values())))
    md += ['', '## Perché: materie mancate e caratteristiche più pesanti (giudice e266, primo seme)', '']
    for s, x in sintesi.items():
        md += ['**%s — %s.** Materie mancate in almeno un seme: %s.' % (s, x['che cosa'], ', '.join(x['materie_mancate']) or 'nessuna'), '',
               '| caratteristica | coefficiente | Voynich | disposizione |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md.append('')
    open(os.path.join(RISULTATI, 'e401_disposizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3)] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
