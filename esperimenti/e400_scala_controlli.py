# -*- coding: utf-8 -*-
"""Esperimento 400: la scala dei controlli. Dal Voynich vero si costruiscono testi con l'impaginazione vera e un solo
livello di struttura rotto (ordine delle righe, ordine nella riga, riga come unita', parole della pagina, nascondiglio) e
si passano ai giudici dell'e231 e dell'e266, alla pagella dell'e224 e alla pagella estesa dell'e293. Per ogni gradino si
riportano anche i gruppi e le caratteristiche piu' pesanti (il perche' del numero).

    PROCESSI=10 python esegui.py e400
    python esperimenti/e400_scala_controlli.py --prova     (solo costruzione dei testi, nessuna misura)

Preregistrazione: preregistrazioni/e400.md. Scrive risultati/e400_scala_controlli.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
SEMI = (1, 2, 3, 4)
GRADINI = OrderedDict([
    ('V', 'il Voynich tale e quale'),
    ('O1', 'righe rimescolate nella pagina'),
    ('O2', 'parole rimescolate dentro la riga'),
    ('O3', 'parole rimescolate nella pagina, prime righe e altre separate'),
    ('O4', 'parole rimescolate in tutta la pagina'),
    ('L1', 'parole ripescate dalla pagina con reimmissione'),
    ('L2', 'parole dalle due pagine prima e dalle due dopo'),
    ('L3', 'parole dalle altre pagine della stessa sezione e lingua'),
    ('L4', 'parole dalle altre pagine del libro'),
    ('N1', 'Voynich con Isidoro nascosto nelle cinque scelte di grafia'),
])
PREVISTE = {'O1': (0.50, 0.58), 'O2': (0.60, 0.72), 'O3': (0.75, 0.85), 'O4': (0.80, 0.90), 'L1': (0.88, 0.95), 'L2': (0.90, 0.97),
            'L3': (0.95, 0.99), 'L4': (0.98, 1.0), 'N1': (0.50, 0.60)}


def voynich():
    """Righe (pagina, inizio paragrafo, parole pulite) e, per pagina, (sezione, lingua)."""
    rr, tipo = [], OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            rr.append((r.pagina, bool(r.inizio_par), ps))
            tipo.setdefault(r.pagina, (r.sezione, r.lingua or '?'))
    return rr, tipo


def per_pagina(rr):
    out = OrderedDict()
    for i, (p, _, _) in enumerate(rr):
        out.setdefault(p, []).append(i)
    return out


def riempi(rr, idx, parole):
    """Rimette le parole date, nell'ordine, nei posti delle righe idx (stesse lunghezze)."""
    out, k = {}, 0
    for i in idx:
        p, ini, ps = rr[i]
        out[i] = (p, ini, parole[k:k + len(ps)])
        k += len(ps)
    return out


def costruisci(gradino, seme, rr, tipo):
    rnd = random.Random(400000 + 1000 * list(GRADINI).index(gradino) + seme)
    pp = per_pagina(rr)
    pagine = list(pp)
    parole_pag = OrderedDict((p, [w for i in idx for w in rr[i][2]]) for p, idx in pp.items())
    nuovo = {}
    for ip, (p, idx) in enumerate(pp.items()):
        if gradino == 'V':
            for i in idx:
                nuovo[i] = rr[i]
        elif gradino == 'O1':
            ordine = list(idx)
            rnd.shuffle(ordine)
            for i, j in zip(idx, ordine):
                nuovo[i] = rr[j]
        elif gradino == 'O2':
            for i in idx:
                ps = list(rr[i][2])
                rnd.shuffle(ps)
                nuovo[i] = (rr[i][0], rr[i][1], ps)
        elif gradino == 'O3':
            for sel in (True, False):
                sotto = [i for i in idx if rr[i][1] == sel]
                ws = [w for i in sotto for w in rr[i][2]]
                rnd.shuffle(ws)
                nuovo.update(riempi(rr, sotto, ws))
        elif gradino == 'O4':
            ws = list(parole_pag[p])
            rnd.shuffle(ws)
            nuovo.update(riempi(rr, idx, ws))
        else:
            if gradino == 'L1':
                serb = parole_pag[p]
            elif gradino == 'L2':
                serb = [w for q in pagine[max(0, ip - 2):ip] + pagine[ip + 1:ip + 3] for w in parole_pag[q]]
            elif gradino == 'L3':
                serb = [w for q in pagine if q != p and tipo[q] == tipo[p] for w in parole_pag[q]]
                serb = serb or [w for q in pagine if q != p and tipo[q][0] == tipo[p][0] for w in parole_pag[q]]
            else:
                serb = None
            if not serb:
                serb = [w for q in pagine if q != p for w in parole_pag[q]]
            nuovo.update(riempi(rr, idx, [serb[rnd.randrange(len(serb))] for _ in parole_pag[p]]))
    return [nuovo[i] for i in range(len(rr))]


def lavoro(args):
    gradino, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    rr, tipo = voynich()
    out = OrderedDict()
    if gradino == 'N1':
        import versioni
        v1 = versioni.canale('v3')
        testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
        chiave = 'scala%d' % seme
        t, info = v1.codifica(testo, chiave, righe=rr)
        out['decodifica_esatta'] = v1.decodifica(t, chiave) == testo
        out['parole_cambiate'] = sum(a != b for (_, _, x), (_, _, y) in zip(rr, t) for a, b in zip(x, y)) / sum(len(x) for _, _, x in rr)
    else:
        t = costruisci(gradino, seme, rr, tipo)
    pg = e251.pagella_grezza(k['c'], t)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(t), k['rif266']))
    out.update([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', e293.pagella_estesa(t)),
                ('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('pesanti_e231', d231['piu_pesanti']),
                ('AUC_e266', d266['AUC']), ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti'])])
    return args, out


def prova():
    """Controllo della costruzione, senza misure: impaginazione uguale, sacchi di parole come dichiarato."""
    rr, tipo = voynich()
    pp = per_pagina(rr)
    for g in GRADINI:
        if g == 'N1':
            continue
        t = costruisci(g, 1, rr, tipo)
        assert [(p, len(ps)) for p, _, ps in t] == [(p, len(ps)) for p, _, ps in rr] or g == 'O1', g
        assert len(t) == len(rr) and [p for p, _, _ in t] == [p for p, _, _ in rr], g
        stesso_sacco = all(sorted(w for i in idx for w in t[i][2]) == sorted(w for i in idx for w in rr[i][2]) for idx in pp.values())
        assert stesso_sacco == (g in ('V', 'O1', 'O2', 'O3', 'O4')), g
        assert sum(ini for _, ini, _ in t) == sum(ini for _, ini, _ in rr), g
        uguali = sum(a == b for a, b in zip(t, rr)) / len(rr)
        print('%-3s righe %d, righe identiche al Voynich %.3f, sacco di pagina conservato %s' % (g, len(t), uguali, stesso_sacco))
    assert costruisci('V', 1, rr, tipo) == rr
    assert costruisci('O4', 2, rr, tipo) == costruisci('O4', 2, rr, tipo)
    print('costruzione a posto')


def main():
    if '--prova' in sys.argv:
        return prova()
    lavori = [('V', 0)] + [(g, s) for g in GRADINI if g != 'V' for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            print('%-3s seme %d: pagella %d riga %s | AUC e231 %.3f e266 %.3f | %s' % (
                a[0], a[1], r['pagella'], r['riga'], r['AUC_e231'], r['AUC_e266'],
                {g: round(v, 2) for g, v in r['gruppi_e266'].items() if v is not None}), flush=True)
    voy = ris[('V', 0)]['estesa']
    import e293_banco as e293
    sintesi = OrderedDict()
    for g in GRADINI:
        rs = [ris[a] for a in lavori if a[0] == g]
        for r in rs:
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy)]
        media = lambda f: statistics.mean(f(r) for r in rs)
        sintesi[g] = OrderedDict([
            ('che cosa', GRADINI[g]), ('semi', len(rs)), ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
            ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)),
            ('materie_mancate', sorted({m for r in rs for m in r['mancano']} | {m for r in rs for m in e293.FASCE if m not in r['estese_passate']})),
            ('pesanti_e266', rs[0]['pesanti_e266'][:6]), ('prevista_e266', PREVISTE.get(g)),
        ])
        if g == 'N1':
            sintesi[g]['decodifica_esatta'] = all(r['decodifica_esatta'] for r in rs)
            sintesi[g]['parole_cambiate'] = media(lambda r: r['parole_cambiate'])
    metro = OrderedDict([('V AUC 0,5', abs(sintesi['V']['AUC_e231'] - 0.5) <= 0.05 and abs(sintesi['V']['AUC_e266'] - 0.5) <= 0.05),
                         ('L4 AUC >= 0,95', sintesi['L4']['AUC_e231'] >= 0.95 and sintesi['L4']['AUC_e266'] >= 0.95),
                         ('N1 decodifica', sintesi['N1']['decodifica_esatta'])])
    out = OrderedDict([('metro', metro), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in lavori))])
    json.dump(out, open(os.path.join(RISULTATI, 'e400_scala_controlli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e400 — La scala dei controlli', '',
          'Testi fatti dal Voynich vero, con l\'impaginazione vera e un solo livello rotto; semi 1–4 (medie). Preregistrazione: `preregistrazioni/e400.md`.', '',
          'Controlli del metro: ' + '; '.join('%s: %s' % (n, 'sì' if x else '**NO**') for n, x in metro.items()) + '.', '',
          '| gradino | che cosa | AUC e231 | AUC e266 (min–max) | prevista e266 | pagella | estese | riga | ' + ' | '.join(sintesi['V']['gruppi']) + ' |',
          '|---|---|---|---|---|---|---|---|' + '---|' * len(sintesi['V']['gruppi'])]
    for g, x in sintesi.items():
        pr = x['prevista_e266']
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %s | %.1f/18 | %.1f/8 | %d/%d | %s |' % (
            g, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1],
            ('%.2f–%.2f' % pr) if pr else '—', x['pagella_media'], x['estese_media'], x['semi_con_riga'], x['semi'],
            ' | '.join('%.2f' % v for v in x['gruppi'].values())))
    md += ['', '## Perché: materie perse e caratteristiche più pesanti per gradino (giudice e266, primo seme)', '']
    for g, x in sintesi.items():
        if g == 'V':
            continue
        md += ['**%s — %s.** Materie mancate in almeno un seme: %s.' % (g, x['che cosa'], ', '.join(x['materie_mancate']) or 'nessuna'), '',
               '| caratteristica | coefficiente | Voynich | controllo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md.append('')
    if 'parole_cambiate' in sintesi['N1']:
        md.append('N1: decodifica esatta %s; parole cambiate dal nascondiglio %.1f%%.' % ('sì' if sintesi['N1']['decodifica_esatta'] else 'NO', 100 * sintesi['N1']['parole_cambiate']))
    open(os.path.join(RISULTATI, 'e400_scala_controlli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({g: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3)] for g, x in sintesi.items()}))


if __name__ == '__main__':
    main()
