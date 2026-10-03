# -*- coding: utf-8 -*-
"""Esperimento 408: concordanza delle desinenze alla dose giusta e scelte di grafia concordi nella riga. Due pezzi aggiunti
alla disposizione della v9: R1 peso proprio del legame fra finali (regolato sulla concordanza delle desinenze); R2 anche il
termine delle scelte di riga (regolato sull'eccesso medio di accordo delle 12 classi dell'e206b). Ogni strato regola i
suoi pesi sul pannello (seme 11), poi si misura come nell'e407 (semi 1-4).

    PROCESSI=10 python esegui.py e408
    python esperimenti/e408_scelte_di_riga.py --prova     (costruzione e due giri di regolazione di R2, nessun giudice)

Preregistrazione: preregistrazioni/e408.md. Scrive risultati/e408_scelte_di_riga.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e401b_disposizione_regolata as e401b
import e406_generatore_pezzi as e406
import e407_verso_pagella as e407

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('R1', 'peso proprio del legame fra finali'), ('R2', 'R1 e scelte di riga')])
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI, RIMESCOLAMENTI = 11, 30, 15, 5
D = misure.divisore(misure.GLIFI_EVA)
_P = {}


def concordanza(rr):
    """Eccesso dei passaggi fra finali diversi di parole vicine non varianti (e285c), con pochi rimescolamenti."""
    import e285c_ripetizione_passaggi as e285c
    import modello
    if 'parti' not in _P:
        _P['parti'] = modello.legami()[0]
    parti = _P['parti']
    righe = [[(w, parti(w)) for w in ps] for _, _, ps in rr if len(ps) >= 2]
    rnd = random.Random(4081)
    vero = e285c.passaggi(e285c.coppie(righe))
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in righe:
            x = list(r)
            rnd.shuffle(x)
            mes.append(x)
        nulli.append(e285c.passaggi(e285c.coppie(mes)))
    return vero - statistics.mean(nulli)


def accordo_classi(rr):
    """Eccesso medio di accordo nella riga delle 12 classi dell'e206b (rimescolamenti stratificati come in e252.test_classi)."""
    import e206_segni_facoltativi as e206
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    rnd = random.Random(4082)
    cl = e206.classi_di(Counter(w for _, _, ps in rr for w in ps))
    occ = defaultdict(list)
    for k, (pag, ini, ps) in enumerate(rr):
        for j, w in enumerate(ps):
            pos = 0 if j == 0 else (2 if j == len(ps) - 1 else 1)
            for c, v in cl.get(w, {}).items():
                nome = '%s %s' % c
                if nome in classi:
                    occ[nome].append(((pag, ini, pos), k, v))
    eccessi = []
    for nome in classi:
        oo = occ.get(nome, [])
        if len(oo) < 100:
            continue
        per_riga = defaultdict(list)
        for _, k, v in oo:
            per_riga[k].append(v)
        strati = defaultdict(list)
        for i, (s, _, _) in enumerate(oo):
            strati[s].append(i)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            vals = [v for _, _, v in oo]
            for idx in strati.values():
                x = [vals[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vals[i] = y
            pr = defaultdict(list)
            for (_, k, _), v in zip(oo, vals):
                pr[k].append(v)
            nulli.append(e206.accordo(pr))
        eccessi.append(e206.accordo(per_riga) - statistics.mean(nulli))
    return statistics.mean(eccessi) if eccessi else 0.0


def statistiche(rr, strato):
    v = e407.statistiche(rr, 'U3')
    v['concordanza'] = concordanza(rr)
    if strato == 'R2':
        v['accordo classi'] = accordo_classi(rr)
    return v


def scarto(n, val, bersaglio):
    if n == 'verticale':
        return abs(val - bersaglio) / 0.06
    if n == 'concordanza':
        return abs(val - bersaglio) / 0.12       # 0,012 (la fascia della pagella estesa) vale 0,10
    return abs(val / bersaglio - 1)


def regola(strato, giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    import pezzi
    rr, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = statistiche(rr, strato)
    x = json.load(open(pezzi.PARAMETRI % 'v9', encoding='utf-8'), object_pairs_hook=OrderedDict)
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, x)
    pesi = OrderedDict(x['pesi_disposizione'])
    pesi['fin_fin'] = 0.4
    if strato == 'R2':
        pesi['classi'] = 0.1
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
        if 'accordo classi' in val:
            pesi['classi'] = min(3.0, max(0.0, pesi['classi'] * math.exp(0.8 * math.log(bersaglio['accordo classi'] / max(val['accordo classi'], bersaglio['accordo classi'] / 8)))))
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
    t = d.disponi(pezzi.sacco_di(408000 + seme, x), 408500 + seme, 'D3', pesi=x['pesi_disposizione'])
    return (strato, seme), e406.misura(t, k, voy)


def prova():
    import pezzi
    rr, _ = pezzi.voynich()
    print('Voynich: %s' % {k: round(v, 4) for k, v in statistiche(rr, 'R2').items()})
    _, r = regola('R2', giri=2, passate=5)
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
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | estesa %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                    {n: (round(v, 3) if isinstance(v, float) else v) for n, v in r['estesa'].items()}), flush=True)
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
            ('valori', OrderedDict((n, media(lambda r: r['valori'][n])) for n in rs[0]['valori'] if all(r['valori'].get(n) is not None for r in rs))),
            ('valori_Voynich', rs[0]['valori_Voynich']),
            ('estesa', OrderedDict((n, media(lambda r: float(r['estesa'][n]))) for n in e293.FASCE if all(r['estesa'][n] is not None for r in rs))),
            ('estesa_per_seme', OrderedDict((n, [r['estesa'][n] for r in rs]) for n in ('scelte di riga', 'concordanza delle desinenze'))),
            ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10]), ('pesanti_e231', rs[0]['pesanti_e231'][:6])])
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e408_scelte_di_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['R1']['gruppi'])
    md = ['# e408 — Concordanza delle desinenze e scelte di grafia concordi nella riga', '',
          'Semi 1–4 (medie). Riferimento: U3 dell\'e407 (v9) 0,541 / 0,659, pagella 16,5/18, estese 3,2/8. Preregistrazione: `preregistrazioni/e408.md`.', '',
          '## Regolazione sul pannello (seme %d)' % SEME_REGOLAZIONE, '']
    for s, r in reg.items():
        md.append('- **%s:** pesi %s; valori %s; Voynich %s; scarto massimo %.3f: %s.' % (
            s, ', '.join('%s %.3f' % (k, v) for k, v in r['pesi'].items() if k != 'vocabolario_testo'), ', '.join('%s %.4f' % kv for kv in r['valori'].items()),
            ', '.join('%.4f' % v for v in r['bersaglio'].values()), r['scarto_massimo'], 'converge' if r['converge'] else '**non converge**'))
    md += ['', '| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | riga | scelte di riga per seme | concordanza per seme | ' + ' | '.join(gr) + ' |',
           '|---|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %s | %s | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['AUC_solo_sacco'], x['pagella_media'],
            x['estese_media'], x['semi_con_riga'], ', '.join(str(v) for v in x['estesa_per_seme']['scelte di riga']),
            ', '.join('%.3f' % v for v in x['estesa_per_seme']['concordanza delle desinenze']), ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', '## Materie mancate (su 4 semi) e valori grezzi', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    nomi = [n for n in sintesi['R2']['valori'] if n in sintesi['R2']['valori_Voynich']]
    md += ['| valore grezzo | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, sintesi['R2']['valori_Voynich'][n], ' | '.join('%.4g' % x['valori'].get(n, float('nan')) for x in sintesi.values())) for n in nomi]
    md += ['', 'Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):', '',
           '| | ' + ' | '.join(sintesi) + ' |', '|---|' + '---|' * len(sintesi)]
    md += ['| %s | %s |' % (n, ' | '.join('%.3f' % x['valori'].get(n, float('nan')) for x in sintesi.values())) for n in ('S1', 'R_riga', 'A', 'scelte_per_riga', 'r_righe_consecutive')]
    md += ['', '| materia aggiunta | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, float(voy['estesa'][n]), ' | '.join('%.4g' % x['estesa'].get(n, float('nan')) for x in sintesi.values())) for n in e293.FASCE]
    md += ['', '## Caratteristiche più pesanti (seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s**' % s, '', '| giudice | caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|---|']
        md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e231']]
        md.append('')
    open(os.path.join(RISULTATI, 'e408_scelte_di_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media'], x['estese_media']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
