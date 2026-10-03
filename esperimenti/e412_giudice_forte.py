# -*- coding: utf-8 -*-
"""Esperimento 412: il giudice forte. Sopra il corpo della v11: M1 il peso della coppia esatta puo' diventare negativo
(regolato su "coppie viste altrove"); M2 anche il termine sulle due meta' della pagina (regolato sulla JSD fra prima e
seconda meta', come G9 dell'e266). Tutti i pesi si regolano insieme sul pannello (seme 11); misure come nell'e410.

    PROCESSI=9 python esegui.py e412
    python esperimenti/e412_giudice_forte.py --prova     (due giri di regolazione di M2, nessun giudice)

Preregistrazione: preregistrazioni/e412.md. Scrive risultati/e412_giudice_forte.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e401b_disposizione_regolata as e401b
import e406_generatore_pezzi as e406
import e410_cancello_riga as e410

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('M1', 'peso della coppia esatta anche negativo'), ('M2', 'M1 e differenza fra le due meta\' della pagina')])
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI = 11, 30, 15
D = misure.divisore(misure.GLIFI_EVA)


def jsd_meta(rr):
    import e266_discriminatore_forte as e266
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).append(ps)
    out = []
    for righe in per.values():
        if sum(map(len, righe)) < 40:
            continue
        m = len(righe) // 2
        out.append(e266.jsd(Counter(x for r in righe[:m] for w in r for x in D(w)), Counter(x for r in righe[m:] for w in r for x in D(w))))
    return statistics.mean(out)


def statistiche(rr, strato):
    v = e410.statistiche(rr, 'G2')
    v['JSD fra le meta'] = jsd_meta(rr)
    return v


def scarto(n, val, bersaglio, strato):
    if n == 'JSD fra le meta':
        return abs(val / bersaglio - 1) if strato == 'M2' else 0.0
    return e410.scarto(n, val, bersaglio)


def regola(strato, giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    import pezzi
    rr, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = statistiche(rr, strato)
    x = json.load(open(pezzi.PARAMETRI % 'v11', encoding='utf-8'), object_pairs_hook=OrderedDict)
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, x)
    pesi = OrderedDict(x['pesi_disposizione'])
    if strato == 'M2':
        pesi['meta'] = 2.0
    traccia, migliore = [], None
    for g in range(giri):
        val = statistiche(d.disponi(sacco, SEME_REGOLAZIONE, 'D3', pesi=pesi, passate=passate), strato)
        peggio = max(scarto(n, val[n], bersaglio[n], strato) for n in val)
        traccia.append(OrderedDict([('giro', g), ('pesi', OrderedDict(pesi)), ('valori', val), ('scarto_massimo', peggio)]))
        if stampa:
            print('%s giro %2d: pesi %s | valori %s | scarto massimo %.3f' % (strato, g, {k: round(v, 3) for k, v in pesi.items() if k != 'vocabolario_testo'},
                                                                           {k: round(v, 4) for k, v in val.items()}, peggio), flush=True)
        if migliore is None or peggio < migliore[0]:
            migliore = (peggio, OrderedDict(pesi), val)
        if peggio < 0.03:
            break
        coppia = pesi['coppia']
        for n, (peso, guadagno) in e401b.LEGA.items():
            pesi[peso] += guadagno * math.log(bersaglio[n] / max(val[n], 1e-4))
            if peso != 'identica':
                pesi[peso] = max(0.0, pesi[peso])
        pesi['coppia'] = max(-3.0, coppia + 1.5 * math.log(bersaglio['coppie viste altrove'] / val['coppie viste altrove']))
        pesi['confine'] = max(0.0, pesi['confine'] + 0.6 * math.log(bersaglio['confine'] / max(val['confine'], 1e-3)))
        pesi['verticale'] = min(10.0, max(0.0, pesi['verticale'] + 4.0 * (bersaglio['verticale'] - val['verticale'])))
        pesi['fin_fin'] = min(3.0, max(0.0, pesi['fin_fin'] + 4.0 * (bersaglio['concordanza'] - val['concordanza'])))
        pesi['prima_lettera'] = max(-6.0, min(0.0, pesi['prima_lettera'] + 1.0 * math.log(bersaglio['S1'] / max(val['S1'], 0.05))))
        pesi['distanza2'] = min(5.0, max(0.0, pesi['distanza2'] + 30.0 * (bersaglio['somiglianza a distanza 2'] - val['somiglianza a distanza 2'])))
        pesi['scelte'] = min(2.0, max(0.0, pesi['scelte'] * math.exp(0.8 * math.log(bersaglio['varianza per riga'] / max(val['varianza per riga'], 0.2)))))
        pesi['scelte_sopra'] = min(2.0, max(0.0, pesi['scelte_sopra'] + 0.3 * (bersaglio['r righe consecutive'] - val['r righe consecutive'])))
        if strato == 'M2':
            pesi['meta'] = min(5000.0, max(0.0, pesi['meta'] * math.exp(1.5 * math.log(bersaglio['JSD fra le meta'] / val['JSD fra le meta']))))
    x['pesi_disposizione'] = dict(migliore[1])
    return strato, OrderedDict([('bersaglio', bersaglio), ('pesi', migliore[1]), ('valori', migliore[2]), ('scarto_massimo', migliore[0]),
                                ('converge', migliore[0] <= 0.10), ('parametri', x), ('traccia', traccia)])


def lavoro(args):
    strato, seme, x = args
    import e251_lessico_sezione as e251
    import e293_banco as e293
    import e401_disposizione as e401
    import pezzi
    k = e251._prepara()
    voy, _ = pezzi.voynich()
    if strato == 'V':
        return (strato, seme), OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(voy))])
    _, d = pezzi.pezzi()
    t = d.disponi(pezzi.sacco_di(412000 + seme, x), 412500 + seme, 'D3', pesi=x['pesi_disposizione'])
    return (strato, seme), e406.misura(t, k, voy)


def prova():
    _, r = regola('M2', giri=2, passate=5)
    print('regolazione a posto (due giri): %s' % {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r['pesi'].items()})


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    with Pool(2) as pool:
        reg = OrderedDict(sorted(pool.imap_unordered(regola, list(STRATI))))
    for s, r in reg.items():
        print('%s: pesi %s, scarto massimo %.3f, converge %s' % (s, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r['pesi'].items()},
                                                                r['scarto_massimo'], r['converge']), flush=True)
    lavori = [('V', 0, None)] + [(s, seme, reg[s]['parametri']) for s in STRATI for seme in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                    {g: round(z, 2) for g, z in r['gruppi_e266'].items() if z is not None}), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for s in STRATI:
        rs = [ris[(s, seme)] for seme in SEMI]
        for r in rs:
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
        media = lambda f: statistics.mean(f(r) for r in rs)
        mancate = Counter(m for r in rs for m in r['mancano'])
        mancate.update(m for r in rs for m in e293.FASCE if m not in r['estese_passate'])
        sintesi[s] = OrderedDict([
            ('che cosa', STRATI[s]), ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
            ('AUC_e266_per_seme', [r['AUC_e266'] for r in rs]), ('AUC_solo_sacco', media(lambda r: r['AUC_solo_sacco'])),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)), ('materie_mancate', OrderedDict(mancate.most_common())),
            ('cancello_per_seme', OrderedDict((n, [r['valori'].get(n) for r in rs]) for n in e410.CANCELLO)),
            ('coppie_viste_altrove', [r['estesa']['coppie viste altrove'] for r in rs]),
            ('JSD_meta', [r['pannello']['G9 JSD prima-seconda meta'] for r in rs]),
            ('trigrammi_dal_Voynich', media(lambda r: r['trigrammi_dal_Voynich'])),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10])])
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e412_giudice_forte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['M1']['gruppi'])
    fmt = lambda vs: ', '.join('%.3f' % v if v is not None else '—' for v in vs)
    md = ['# e412 — Il giudice forte: coppie viste altrove e differenza fra le due metà della pagina', '',
          'Semi 1–4 (medie), corpo senza messaggio. Riferimento: G2 dell\'e410 (corpo della v11) 0,552 / 0,616, pagella 15,8/18, cancello 3/4. '
          'Preregistrazione: `preregistrazioni/e412.md`.', '', '## Regolazione sul pannello (seme %d)' % SEME_REGOLAZIONE, '']
    for s, r in reg.items():
        md.append('- **%s:** pesi %s; scarto massimo %.3f: %s.' % (s, ', '.join('%s %.3f' % (k, v) for k, v in r['pesi'].items() if k != 'vocabolario_testo'),
                                                                r['scarto_massimo'], 'converge' if r['converge'] else '**non converge**'))
        md.append('  - valori (Voynich): ' + '; '.join('%s %.4f (%.4f)' % (n, r['valori'][n], r['bersaglio'][n]) for n in r['valori']) + '.')
    md += ['', '| strato | che cosa | AUC e231 | AUC e266 (per seme) | solo sacco | pagella | estese | semi con il cancello | trigrammi dal Voynich | ' + ' | '.join(gr) + ' |',
           '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%s) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %.3f | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], fmt(x['AUC_e266_per_seme']), x['AUC_solo_sacco'], x['pagella_media'], x['estese_media'],
            x['semi_con_riga'], x['trigrammi_dal_Voynich'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', '| per seme | ' + ' | '.join(sintesi) + ' |', '|---|' + '---|' * len(sintesi),
           '| coppie viste altrove (Voynich 0,221 ± 0,02) | ' + ' | '.join(fmt(x['coppie_viste_altrove']) for x in sintesi.values()) + ' |',
           '| JSD fra le due metà (Voynich 0,0503) | ' + ' | '.join(', '.join('%.4f' % v for v in x['JSD_meta']) for x in sintesi.values()) + ' |']
    md += ['| %s | %s |' % (n, ' | '.join(fmt(x['cancello_per_seme'][n]) for x in sintesi.values())) for n in e410.CANCELLO]
    md += ['', '## Materie mancate (su 4 semi)', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    md += ['## Caratteristiche più pesanti (giudice e266, seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s**' % s, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md.append('')
    open(os.path.join(RISULTATI, 'e412_giudice_forte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media'], x['semi_con_riga']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
