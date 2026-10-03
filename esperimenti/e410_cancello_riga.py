# -*- coding: utf-8 -*-
"""Esperimento 410: il cancello della riga. Termini nuovi nella disposizione, regolati sul pannello (seme 11): G1 prima
lettera della riga diversa da quella della riga sopra e somiglianza a distanza 2; G2 anche le cinque scelte di grafia
concordi nella riga e fra righe consecutive. Corpo di partenza: parametri della v10. Misure come nell'e408 (semi 1-4).

    PROCESSI=9 python esegui.py e410
    python esperimenti/e410_cancello_riga.py --prova     (statistiche del Voynich e due giri di regolazione di G2, nessun giudice)

Preregistrazione: preregistrazioni/e410.md. Scrive risultati/e410_cancello_riga.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e401b_disposizione_regolata as e401b
import e406_generatore_pezzi as e406
import e408_scelte_di_riga as e408

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('G1', 'prima lettera della riga e somiglianza a distanza 2'), ('G2', 'G1 e cinque scelte di grafia nella riga e fra righe')])
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI = 11, 30, 15
CANCELLO = ('S1', 'R_riga', 'A', 'scelte_per_riga', 'r_righe_consecutive')
D = misure.divisore(misure.GLIFI_EVA)


def di_riga(rr, strato):
    """Le statistiche nuove: S1 (e83), somiglianza a distanza 2 (come G6 dell'e266), A (e110); per G2 anche il rapporto di
    varianza per riga delle cinque scelte (e135) e la correlazione fra righe consecutive (e146)."""
    import e83_evitamento_inizi as e83
    import e106_procedimento_versi as e106
    import e110_alternanza as e110
    e83.PERMUTAZIONI, e110.RIMESCOLAMENTI = 30, 5
    v = OrderedDict()
    per, par = OrderedDict(), 0
    for i, (_, ini, ps) in enumerate(rr):
        par += ini
        per.setdefault(i // e106.RIGHE_PAGINA, []).append((par, ini, ps[0] if ps else None))
    v['S1'] = e83.misura(per, 1, e83.primo_eva, random.Random(106))['S']
    pag = OrderedDict()
    for p, _, ps in rr:
        pag.setdefault(p, []).append(ps)
    s2 = []
    for righe in pag.values():
        if sum(map(len, righe)) >= 40:
            x = [1 - misure._dist_norm(tuple(D(a)), tuple(D(b))) for r in righe for a, b in zip(r, r[2:])]
            if x:
                s2.append(statistics.mean(x))
    v['somiglianza a distanza 2'] = statistics.mean(s2)
    v['A'] = e110.una(('x', [ps for _, _, ps in rr], 'eva'))[1]['senza identiche']['A']
    if strato == 'G2':
        import e135_stato_riga as e135
        import e145_abitudini as e145
        import e146_deriva_preferenze as e146
        occ = e135.occorrenze([(p, ps) for p, _, ps in rr])
        valori = [o[-1] for o in occ]
        var, _, _ = e135.statistiche(occ, valori)
        gg = e135.gruppi(occ)
        rnd = random.Random(4101)
        nulli = [e135.statistiche(occ, e135.permuta(valori, gg, rnd))[0] for _ in range(5)]
        rap = [var[f] / statistics.mean(n[f] for n in nulli) for f in e145.SCELTE if var.get(f) and all(n.get(f) for n in nulli)]
        v['varianza per riga'] = statistics.mean(rap)
        par, kk = [], 0
        for p, ini, ps in rr:
            kk += ini
            par.append((p, kk, ps))
        v['r righe consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    return v


def statistiche(rr, strato):
    v = e408.statistiche(rr, 'R1')
    v.update(di_riga(rr, strato))
    return v


def scarto(n, val, bersaglio):
    if n == 'r righe consecutive':
        return abs(val - bersaglio) / 0.7
    if n == 'A':
        return 0.0                      # si riporta, non si regola
    if n in ('verticale', 'concordanza'):
        return e408.scarto(n, val, bersaglio)
    return abs(val / bersaglio - 1)


def regola(strato, giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    import pezzi
    rr, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = statistiche(rr, strato)
    x = json.load(open(pezzi.PARAMETRI % 'v10', encoding='utf-8'), object_pairs_hook=OrderedDict)
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, x)
    pesi = OrderedDict(x['pesi_disposizione'])
    pesi['prima_lettera'], pesi['distanza2'] = -0.5, 0.3
    if strato == 'G2':
        pesi['scelte'], pesi['scelte_sopra'] = 0.05, 0.02
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
        if peggio < 0.03:
            break
        for n, (peso, guadagno) in e401b.LEGA.items():
            pesi[peso] += guadagno * math.log(bersaglio[n] / max(val[n], 1e-4))
            if peso != 'identica':
                pesi[peso] = max(0.0, pesi[peso])
        pesi['confine'] = max(0.0, pesi['confine'] + 0.6 * math.log(bersaglio['confine'] / max(val['confine'], 1e-3)))
        pesi['verticale'] = min(10.0, max(0.0, pesi['verticale'] + 4.0 * (bersaglio['verticale'] - val['verticale'])))
        pesi['fin_fin'] = min(3.0, max(0.0, pesi['fin_fin'] + 4.0 * (bersaglio['concordanza'] - val['concordanza'])))
        pesi['prima_lettera'] = max(-6.0, min(0.0, pesi['prima_lettera'] + 1.0 * math.log(bersaglio['S1'] / max(val['S1'], 0.05))))
        pesi['distanza2'] = min(5.0, max(0.0, pesi['distanza2'] + 30.0 * (bersaglio['somiglianza a distanza 2'] - val['somiglianza a distanza 2'])))
        if strato == 'G2':
            pesi['scelte'] = min(2.0, max(0.0, pesi['scelte'] * math.exp(0.8 * math.log(bersaglio['varianza per riga'] / max(val['varianza per riga'], 0.2)))))
            pesi['scelte_sopra'] = min(2.0, max(0.0, pesi['scelte_sopra'] + 0.3 * (bersaglio['r righe consecutive'] - val['r righe consecutive'])))
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
    t = d.disponi(pezzi.sacco_di(410000 + seme, x), 410500 + seme, 'D3', pesi=x['pesi_disposizione'])
    return (strato, seme), e406.misura(t, k, voy)


def prova():
    import pezzi
    rr, _ = pezzi.voynich()
    print('Voynich: %s' % {k: round(v, 4) for k, v in statistiche(rr, 'G2').items()})
    _, r = regola('G2', giri=2, passate=5)
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
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | cancello %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                    {n: round(r['valori'][n], 3) for n in CANCELLO if r['valori'].get(n) is not None}), flush=True)
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
            ('cancello_per_seme', OrderedDict((n, [r['valori'].get(n) for r in rs]) for n in CANCELLO)),
            ('valori', OrderedDict((n, media(lambda r: r['valori'][n])) for n in rs[0]['valori'] if all(r['valori'].get(n) is not None for r in rs))),
            ('valori_Voynich', rs[0]['valori_Voynich']),
            ('estesa', OrderedDict((n, media(lambda r: float(r['estesa'][n]))) for n in e293.FASCE if all(r['estesa'][n] is not None for r in rs))),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10]), ('pesanti_e231', rs[0]['pesanti_e231'][:6])])
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e410_cancello_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['G1']['gruppi'])
    md = ['# e410 — Il cancello della riga', '',
          'Semi 1–4 (medie). Riferimento: R1 dell\'e408 (corpo della v10) 0,554 / 0,673, pagella 17,0/18, cancello perso in 4 semi. Preregistrazione: `preregistrazioni/e410.md`.', '',
          '## Regolazione sul pannello (seme %d)' % SEME_REGOLAZIONE, '']
    for s, r in reg.items():
        md.append('- **%s:** pesi %s; scarto massimo %.3f: %s.' % (s, ', '.join('%s %.3f' % (k, v) for k, v in r['pesi'].items() if k != 'vocabolario_testo'),
                                                                r['scarto_massimo'], 'converge' if r['converge'] else '**non converge**'))
        md.append('  - valori (Voynich): ' + '; '.join('%s %.4f (%.4f)' % (n, r['valori'][n], r['bersaglio'][n]) for n in r['valori']) + '.')
    md += ['', '| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | semi con il cancello | ' + ' | '.join(gr) + ' |',
           '|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['AUC_solo_sacco'], x['pagella_media'],
            x['estese_media'], x['semi_con_riga'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', 'Cancello della riga per seme (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):', '',
           '| | ' + ' | '.join(sintesi) + ' |', '|---|' + '---|' * len(sintesi)]
    md += ['| %s | %s |' % (n, ' | '.join(', '.join('%.3f' % v if v is not None else '—' for v in x['cancello_per_seme'][n]) for x in sintesi.values())) for n in CANCELLO]
    md += ['', '## Materie mancate (su 4 semi)', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    md += ['| materia aggiunta | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, float(voy['estesa'][n]), ' | '.join('%.4g' % x['estesa'].get(n, float('nan')) for x in sintesi.values())) for n in e293.FASCE]
    md += ['', '## Caratteristiche più pesanti (seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s**' % s, '', '| giudice | caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|---|']
        md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e231']]
        md.append('')
    open(os.path.join(RISULTATI, 'e410_cancello_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media'], x['semi_con_riga']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
