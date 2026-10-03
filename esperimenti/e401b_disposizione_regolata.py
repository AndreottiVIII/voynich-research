# -*- coding: utf-8 -*-
"""Esperimento 401b: la disposizione con la dose dei legami regolata sul pannello. Nell'e401 i legami fra vicine (bordi,
unione, coppia esatta) con peso 1 esageravano. Qui i loro pesi, piu' un termine per la coppia identica, si regolano con
correzioni successive finche' quattro valori del testo disposto coincidono con quelli del Voynich (unioni attestate, coppie
viste altrove, coppie identiche, somiglianza fra vicine); poi lo strato D4 si misura come nell'e401 (semi 1-4).

    PROCESSI=4 python esegui.py e401b
    python esperimenti/e401b_disposizione_regolata.py --prova     (due giri di regolazione su 12 pagine, nessun giudice)

Preregistrazione: preregistrazioni/e401b.md. Scrive risultati/e401b_disposizione_regolata.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e400_scala_controlli as e400
import e401_disposizione as e401

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI, TOLLERANZA = 11, 30, 15, 0.10
# valore del pannello -> peso che lo governa, guadagno della correzione (sul logaritmo del rapporto bersaglio/valore)
LEGA = OrderedDict([('unioni attestate', ('unione', 1.0)), ('coppie viste altrove', ('coppia', 1.5)),
                    ('coppie identiche', ('identica', 1.0)), ('somiglianza fra vicine', ('bordi', 3.0))])
PARTENZA = OrderedDict([('bordi', 0.5), ('unione', 0.5), ('coppia', 0.5), ('identica', 0.0)])
PREVISTA = (0.68, 0.78)
D = misure.divisore(misure.GLIFI_EVA)


def quattro(rr):
    """I quattro valori, media delle pagine con almeno 40 parole (definizioni dell'e231 e dell'e266)."""
    freq = Counter(w for _, _, ps in rr for w in ps)
    tot = Counter((a, b) for _, _, ps in rr for a, b in zip(ps, ps[1:]))
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).append(ps)
    v = OrderedDict((n, []) for n in LEGA)
    for p, righe in per.items():
        cp = [(a, b) for r in righe for a, b in zip(r, r[1:])]
        if sum(map(len, righe)) < 40 or not cp:
            continue
        v['unioni attestate'].append(sum(freq[a + b] > 0 for a, b in cp) / len(cp))
        v['coppie viste altrove'].append(sum(tot[x] >= 2 for x in cp) / len(cp))
        v['coppie identiche'].append(sum(a == b for a, b in cp) / len(cp))
        v['somiglianza fra vicine'].append(statistics.mean(1 - misure._dist_norm(tuple(D(a)), tuple(D(b))) for a, b in cp))
    return OrderedDict((n, statistics.mean(x)) for n, x in v.items())


def regola(rr, m, giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    bersaglio = quattro(rr)
    pesi = OrderedDict(PARTENZA)
    traccia, migliore = [], None
    for g in range(giri):
        val = quattro(m.disponi(rr, SEME_REGOLAZIONE, 'D3', pesi=pesi, passate=passate))
        scarti = OrderedDict((n, val[n] / bersaglio[n] - 1) for n in LEGA)
        peggio = max(abs(x) for x in scarti.values())
        traccia.append(OrderedDict([('giro', g), ('pesi', OrderedDict(pesi)), ('valori', val), ('scarto_massimo', peggio)]))
        if stampa:
            print('giro %2d: pesi %s | valori %s | scarto massimo %.3f' % (g, {k: round(x, 3) for k, x in pesi.items()},
                                                                        {k: round(x, 4) for k, x in val.items()}, peggio), flush=True)
        if migliore is None or peggio < migliore[0]:
            migliore = (peggio, OrderedDict(pesi), val)
        if peggio < 0.02:
            break
        for n, (peso, guadagno) in LEGA.items():
            pesi[peso] += guadagno * math.log(bersaglio[n] / max(val[n], 1e-4))
            if peso != 'identica':
                pesi[peso] = max(0.0, pesi[peso])
    return OrderedDict([('bersaglio', bersaglio), ('pesi', migliore[1]), ('valori', migliore[2]), ('scarto_massimo', migliore[0]),
                        ('converge', migliore[0] <= TOLLERANZA), ('traccia', traccia)])


def lavoro(args):
    seme, pesi = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    rr, _ = e400.voynich()
    if seme == 0:
        return seme, OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(rr))])
    t = e401.modello(rr).disponi(rr, 401000 + 3000 + seme, 'D3', pesi=pesi)
    pg = e251.pagella_grezza(k['c'], t)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    d266 = e266.confronto(k['vt266'], tab)
    return seme, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', e293.pagella_estesa(t)),
                              ('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('AUC_e266', d266['AUC']),
                              ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti']), ('pannello', e401.pannello(tab))])


def prova():
    rr, _ = e400.voynich()
    pagine = list(OrderedDict((p, 1) for p, _, _ in rr))[:12]
    sotto = [x for x in rr if x[0] in pagine]
    r = regola(sotto, e401.modello(rr), giri=2, passate=5)
    assert len(r['traccia']) == 2 and set(r['pesi']) == set(PARTENZA)
    print('regolazione a posto')


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    rr, _ = e400.voynich()
    reg = regola(rr, e401.modello(rr))
    print('pesi scelti %s, scarto massimo %.3f, converge %s' % (dict(reg['pesi']), reg['scarto_massimo'], reg['converge']), flush=True)
    pesi = dict(reg['pesi'])
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for seme, r in pool.imap_unordered(lavoro, [(0, None)] + [(s, pesi) for s in SEMI]):
            ris[seme] = r
            if seme:
                print('D4 seme %d: pagella %d riga %s | AUC e231 %.3f e266 %.3f | %s' % (
                    seme, r['pagella'], r['riga'], r['AUC_e231'], r['AUC_e266'], {g: round(v, 2) for g, v in r['gruppi_e266'].items() if v is not None}), flush=True)
    voy = ris[0]
    rs = [ris[s] for s in SEMI]
    for r in rs:
        r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
    media = lambda f: statistics.mean(f(r) for r in rs)
    x = OrderedDict([
        ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
        ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]), ('prevista_e266', PREVISTA),
        ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
        ('gruppi_e231', OrderedDict((n, media(lambda r: r['gruppi_e231'][n])) for n in rs[0]['gruppi_e231'] if rs[0]['gruppi_e231'][n] is not None)),
        ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
        ('semi_con_riga', sum(bool(r['riga']) for r in rs)),
        ('materie_mancate', sorted({m for r in rs for m in r['mancano']} | {m for r in rs for m in e293.FASCE if m not in r['estese_passate']})),
        ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])), ('pesanti_e266', rs[0]['pesanti_e266'][:8])])
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('D4', x), ('per_seme', OrderedDict((str(s), ris[s]) for s in SEMI))])
    json.dump(out, open(os.path.join(RISULTATI, 'e401b_disposizione_regolata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(x['gruppi'])
    md = ['# e401b — La disposizione con la dose dei legami regolata sul pannello', '',
          'Sacco di parole vero e impaginazione vera; posti (8 tipi) e legami fra vicine con i pesi regolati perché quattro valori tornino quelli del Voynich. '
          'Riferimenti: e401 D2 0,855 e D3 0,847 (e231: 0,771 e 0,729); solo righe rimescolate 0,595. Preregistrazione: `preregistrazioni/e401b.md`.', '',
          '## Regolazione (seme %d, %d passate)' % (SEME_REGOLAZIONE, PASSATE_REGOLAZIONE), '',
          '| giro | bordi | unione | coppia | identica | ' + ' | '.join(LEGA) + ' | scarto massimo |', '|---|---|---|---|---|' + '---|' * (len(LEGA) + 1)]
    for t in reg['traccia']:
        md.append('| %d | %.3f | %.3f | %.3f | %.3f | %s | %.3f |' % (t['giro'], t['pesi']['bordi'], t['pesi']['unione'], t['pesi']['coppia'], t['pesi']['identica'],
                                                                 ' | '.join('%.4f' % t['valori'][n] for n in LEGA), t['scarto_massimo']))
    md += ['| Voynich | | | | | %s | |' % ' | '.join('%.4f' % reg['bersaglio'][n] for n in LEGA), '',
           'Pesi scelti: %s. Scarto massimo %.3f: la regolazione %s.' % (', '.join('%s %.3f' % kv for kv in reg['pesi'].items()), reg['scarto_massimo'],
                                                                      'converge' if reg['converge'] else '**non converge**'), '',
           '## Strato D4 (semi 1–4, medie)', '',
           '| AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | ' + ' | '.join(gr) + ' |', '|---|---|---|---|---|---|' + '---|' * len(gr),
           '| %.3f | %.3f (%.3f–%.3f) | %.2f–%.2f | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
               x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], PREVISTA[0], PREVISTA[1], x['pagella_media'], x['estese_media'],
               x['semi_con_riga'], ' | '.join('%.2f' % v for v in x['gruppi'].values())), '',
           'Gruppi dell\'e231: ' + ', '.join('%s %.2f' % kv for kv in x['gruppi_e231'].items()) + '.', '',
           'Materie mancate in almeno un seme: %s.' % (', '.join(x['materie_mancate']) or 'nessuna'), '',
           '## Pannello (media delle pagine)', '', '| misura | Voynich | D4 |', '|---|---|---|']
    md += ['| %s | %.4f | %.4f |' % (n, voy['pannello'][n], x['pannello'][n]) for n in voy['pannello']]
    md += ['', '## Caratteristiche più pesanti (giudice e266, seme 1)', '', '| caratteristica | coefficiente | Voynich | disposizione |', '|---|---|---|---|']
    md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
    open(os.path.join(RISULTATI, 'e401b_disposizione_regolata.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({'D4': [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3)], 'converge': reg['converge']}))


if __name__ == '__main__':
    main()
