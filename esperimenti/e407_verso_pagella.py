# -*- coding: utf-8 -*-
"""Esperimento 407: verso la pagella. Tre pezzi aggiunti al generatore a pezzi: U1 parole nuove come unioni di due parole
note della pagina (e unione giudicata sul vocabolario del testo); U2 anche il legame fra ultimo e primo segno ("confine");
U3 anche la somiglianza con la parola sopra ("verticale"). Ogni strato regola i suoi pesi sul pannello (seme 11), poi si
misura come nell'e406 (semi 1-4). Scrive i parametri di ogni strato in risultati/e407_verso_pagella.json.

    PROCESSI=10 python esegui.py e407
    python esperimenti/e407_verso_pagella.py --prova     (costruzione e due giri di regolazione di U3, nessun giudice)

Preregistrazione: preregistrazioni/e407.md. Scrive risultati/e407_verso_pagella.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('U1', 'parole nuove come unioni'), ('U2', 'U1 e legame fra ultimo e primo segno'), ('U3', 'U2 e verticale')])
UNIONI = 0.25
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI = 11, 30, 15
D = misure.divisore(misure.GLIFI_EVA)


def statistiche(rr, strato):
    """I valori su cui si regola: i quattro dell'e401b, piu' confine (U2, U3) e verticale (U3)."""
    v = OrderedDict(e401b.quattro(rr))
    if strato in ('U2', 'U3'):
        v['confine'] = misure.confine([ps for _, _, ps in rr], D, solo_interne=True)['im_confine_eccesso']
    if strato == 'U3':
        import e61_pagella as e61
        per = OrderedDict()
        for p, _, ps in rr:
            per.setdefault(p, []).append(ps)
        v['verticale'] = float(e61.verticale(list(per.values()), D))
    return v


def scarto(n, val, bersaglio):
    return abs(val - bersaglio) / 0.06 if n == 'verticale' else abs(val / bersaglio - 1)


def regola(strato, giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    import pezzi
    rr, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = statistiche(rr, strato)
    x = dict(e406.base(), posti='modello')
    x['forme'] = dict(x['forme'], unioni=UNIONI)
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, x)
    pesi = OrderedDict([('bordi', 0.7), ('unione', 0.6), ('coppia', 0.5), ('identica', -0.55), ('vocabolario_testo', True)])
    if strato in ('U2', 'U3'):
        pesi['confine'] = 0.5
    if strato == 'U3':
        pesi['verticale'] = 0.15
    traccia, migliore = [], None
    for g in range(giri):
        val = statistiche(d.disponi(sacco, SEME_REGOLAZIONE, 'D3', pesi=pesi, passate=passate), strato)
        peggio = max(scarto(n, val[n], bersaglio[n]) for n in val)
        traccia.append(OrderedDict([('giro', g), ('pesi', OrderedDict(pesi)), ('valori', val), ('scarto_massimo', peggio)]))
        if stampa:
            print('%s giro %2d: pesi %s | valori %s | scarto massimo %.3f' % (strato, g, {k: round(v, 3) for k, v in pesi.items() if k != 'vocabolario_testo'},
                                                                           {k: round(v, 4) for k, v in val.items()}, peggio), flush=True)
        if migliore is None or peggio < migliore[0]:
            migliore = (peggio, OrderedDict(pesi), val)
        if peggio < 0.02:
            break
        for n, (peso, guadagno) in e401b.LEGA.items():
            pesi[peso] += guadagno * math.log(bersaglio[n] / max(val[n], 1e-4))
            if peso != 'identica':
                pesi[peso] = max(0.0, pesi[peso])
        if 'confine' in val:
            pesi['confine'] = max(0.0, pesi['confine'] + 0.6 * math.log(bersaglio['confine'] / max(val['confine'], 1e-3)))
        if 'verticale' in val:
            pesi['verticale'] = min(10.0, max(0.0, pesi['verticale'] + 4.0 * (bersaglio['verticale'] - val['verticale'])))
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
    t = d.disponi(pezzi.sacco_di(407000 + seme, x), 407500 + seme, 'D3', pesi=x['pesi_disposizione'])
    r = e406.misura(t, k, voy)
    c = Counter(w for _, _, ps in t for w in ps)
    cp = [(a, b) for _, _, ps in t for a, b in zip(ps, ps[1:])]
    r['unione_parola_unica'] = sum(c[a + b] == 1 for a, b in cp) / len(cp)
    return (strato, seme), r


def prova():
    import pezzi
    rr, _ = pezzi.voynich()
    print('Voynich: %s' % {k: round(v, 4) for k, v in statistiche(rr, 'U3').items()})
    _, r = regola('U3', giri=2, passate=5)
    print('regolazione a posto (due giri): %s' % {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r['pesi'].items()})
    t = pezzi.sacco_di(1, r['parametri'])
    s, _ = pezzi.pezzi()
    nuove = [w for _, _, ps in t for w in ps if w not in s.conta]
    unite = sum(any(w[:i] in s.conta and w[i:] in s.conta for i in range(1, len(w))) for w in nuove) / len(nuove)
    print('parole nuove %d, di cui leggibili come due parole note unite %.3f (Voynich 0,809)' % (len(nuove), unite))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    with Pool(3) as pool:
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
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f' % (a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266']), flush=True)
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
            ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]), ('AUC_solo_sacco', media(lambda r: r['AUC_solo_sacco'])),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)), ('materie_mancate', OrderedDict(mancate.most_common())),
            ('valori', OrderedDict((n, media(lambda r: r['valori'][n])) for n in rs[0]['valori'] if all(n in r['valori'] for r in rs))),
            ('valori_Voynich', rs[0]['valori_Voynich']),
            ('estesa', OrderedDict((n, media(lambda r: float(r['estesa'][n]))) for n in e293.FASCE if all(r['estesa'][n] is not None for r in rs))),
            ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])),
            ('unione_parola_unica', media(lambda r: r['unione_parola_unica'])), ('trigrammi_dal_Voynich', media(lambda r: r['trigrammi_dal_Voynich'])),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10]), ('pesanti_e231', rs[0]['pesanti_e231'][:6])])
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e407_verso_pagella.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['U1']['gruppi'])
    md = ['# e407 — Verso la pagella: unioni, legame fra ultimo e primo segno, verticale', '',
          'Semi 1–4 (medie). Riferimento: P3 dell\'e406 (v8) 0,558 / 0,703, pagella 13,8/18, estese 4,0/8. Preregistrazione: `preregistrazioni/e407.md`.', '',
          '## Regolazione sul pannello (seme %d)' % SEME_REGOLAZIONE, '']
    for s, r in reg.items():
        md.append('- **%s:** pesi %s; valori %s (Voynich %s); scarto massimo %.3f: %s.' % (
            s, ', '.join('%s %.3f' % (k, v) for k, v in r['pesi'].items() if k != 'vocabolario_testo'), ', '.join('%s %.4f' % kv for kv in r['valori'].items()),
            ', '.join('%.4f' % v for v in r['bersaglio'].values()), r['scarto_massimo'], 'converge' if r['converge'] else '**non converge**'))
    md += ['', '| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | riga | unione = parola unica (Voynich 0,027) | ' + ' | '.join(gr) + ' |',
           '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %.4f | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['AUC_solo_sacco'], x['pagella_media'],
            x['estese_media'], x['semi_con_riga'], x['unione_parola_unica'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', '## Materie mancate (su 4 semi) e valori grezzi', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    nomi = [n for n in sintesi['U3']['valori'] if n in sintesi['U3']['valori_Voynich']]
    md += ['| valore grezzo | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, sintesi['U3']['valori_Voynich'][n], ' | '.join('%.4g' % x['valori'].get(n, float('nan')) for x in sintesi.values())) for n in nomi]
    md += ['', '| materia aggiunta | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, float(voy['estesa'][n]), ' | '.join('%.4g' % x['estesa'].get(n, float('nan')) for x in sintesi.values())) for n in e293.FASCE]
    md += ['', '## Pannello (media delle pagine)', '', '| misura | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4f | %s |' % (n, voy['pannello'][n], ' | '.join('%.4f' % x['pannello'][n] for x in sintesi.values())) for n in voy['pannello']]
    md += ['', '## Caratteristiche più pesanti (seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s**' % s, '', '| giudice | caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|---|']
        md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e231']]
        md.append('')
    open(os.path.join(RISULTATI, 'e407_verso_pagella.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
