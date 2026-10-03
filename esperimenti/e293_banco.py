# -*- coding: utf-8 -*-
"""Esperimento 293: pagella estesa (18 materie dell'e224 piu' otto) e banco di prova del voynichizzatore: ogni versione
nasconde lo stesso testo (Isidoro XVII, chiave "banco") in corpi con i semi d'esame 7, 8, 9; decodifica, pagella,
pagella estesa, AUC dell'e231 e dell'e266. Il Voynich fa da controllo del metro.

    python esegui.py e293                     (versioni v2 e v3)
    python esegui.py e293 -- v4 ...           (altre versioni registrate in VERSIONI)

Preregistrazione: preregistrazioni/e293.md. Scrive risultati/e293_banco.json e .md (e e293_banco_<versioni>.* se diverse).
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
CHIAVE, SEMI = 'banco', (7, 8, 9)
CORPI = {'e288': OrderedDict([('rip', 0.5), ('phi', 0.10), ('sigma_post', 0.04)])}
VERSIONI = OrderedDict([('v2', ('e288', 'v1')), ('v3', ('e288', 'v3'))])     # versione -> (corpo, modello delle scelte)
FASCE = OrderedDict([('parole rare per pagina', None), ('tipi su parole nella pagina', 0.03), ('uniche nella pagina', 0.04),
                     ('dispersione delle lunghezze', 0.04), ('prime righe come registro', None), ('scelte di riga', None),
                     ('concordanza delle desinenze', 0.012), ('coppie viste altrove', 0.02)])
_STATO = {}


def canale(modello):
    """Imposta nel processo il modello delle scelte della versione (v1 o v3)."""
    import v1
    if 'posti_v1' not in _STATO:
        _STATO['posti_v1'], _STATO['modello_v1'] = v1.posti_contesto, v1.MODELLO
    if modello == 'v3':
        import v3
        v1.posti_contesto, v1.MODELLO = v3.posti_contesto_v3, os.path.join(QUI, '..', 'voynichizzatore', 'modello_scelte_v3.json')
    else:
        v1.posti_contesto, v1.MODELLO = _STATO['posti_v1'], _STATO['modello_v1']
    return v1


def corpo(nome, seme):
    import corpo2
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    k = e251._prepara()
    x = CORPI[nome]
    e233.SIGMA_POST, e233.PI_POST = x.get('sigma_post', 0.09), x.get('pi_post', 0.30)
    prm = dict(e251.CONF, gamma=0.0, rip=x.get('rip', 1.0), phi=x.get('phi', 0.0))
    return e236.dopo(corpo2.genera_v2(k['c2'], prm, seme), k['freq'], 100 + seme)


def misure_pagina(rr):
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    import e251_lessico_sezione as e251
    D = e231.D if hasattr(e231, 'D') else None
    import misure
    D = misure.divisore(misure.GLIFI_EVA)
    per = OrderedDict()
    for pag, _, ps in rr:
        per.setdefault(pag, []).extend(w for w in ps if trascrizione.pulita(w))
    tipi, uniche, disp = [], [], []
    for pag, ws in per.items():
        if len(ws) < e231.MIN_PAROLE:
            continue
        cw = Counter(ws)
        tipi.append(len(cw) / len(ws))
        uniche.append(sum(cw[w] == 1 for w in ws) / len(ws))
        disp.append(statistics.pstdev([len(D(w)) for w in ws]))
    ex = e266.extra(e251.righe_ini(rr))
    coppie = [f['G6 coppie viste altrove'] for f in ex.values()]
    return statistics.mean(tipi), statistics.mean(uniche), statistics.mean(disp), statistics.mean(coppie)


def pagella_estesa(rr):
    import e251_lessico_sezione as e251
    import e252_interruttori_riga as e252
    import e268_prime_righe as e268
    import e285c_ripetizione_passaggi as e285c
    import e285_pezzi_contesto as e285
    import e249_pezzi_simboli as e249
    tipi, uniche, disp, coppie = misure_pagina(rr)
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    z = e252.test_classi(rr, classi)
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    taglia = e249.segmentatore([w for r in voy for w in r])
    cache = {}
    tp = lambda w: (w, cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w)))
    righe = [[tp(w) for w in ps if trascrizione.pulita(w)] for _, _, ps in rr]
    conc = e285c.misure([r for r in righe if len(r) >= 2], random.Random(2853))['passaggi']['eccesso']
    m273 = e268.misura_e273(rr)
    return OrderedDict([('parole rare per pagina', e251.R_completo(rr, controllo=False)['R']), ('tipi su parole nella pagina', tipi),
                        ('uniche nella pagina', uniche), ('dispersione delle lunghezze', disp), ('prime righe come registro', m273['z']),
                        ('scelte di riga', sum((v or 0) > 3 for v in z.values())), ('concordanza delle desinenze', conc), ('coppie viste altrove', coppie)])


def passa(nome, x, voy):
    if x is None:
        return False
    if nome == 'parole rare per pagina':
        return x <= 5
    if nome == 'prime righe come registro':
        return x > 3
    if nome == 'scelte di riga':
        return x >= 10
    return abs(x - voy[nome]) <= FASCE[nome]


def voynich_rr():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            out.append((r.pagina, bool(r.inizio_par), [w for w in r.parole if trascrizione.pulita(w)]))
    return [x for x in out if x[2]]


def lavoro(args):
    versione, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    if versione == 'Voynich':
        return args, OrderedDict([('estesa', pagella_estesa(voynich_rr()))])
    nome_corpo, modello = VERSIONI[versione]
    v1 = canale(modello)
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    rr, info = v1.codifica(testo, CHIAVE, righe=corpo(nome_corpo, seme))
    ok = v1.decodifica(rr, CHIAVE) == testo
    pg = e251.pagella_grezza(k['c'], rr)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    return args, OrderedDict([('decodifica_esatta', ok), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                              ('AUC_e231', d231['AUC']), ('AUC_e266', d266['AUC']), ('gruppi_e266', d266['AUC_per_gruppo']), ('estesa', pagella_estesa(rr))])


def main():
    versioni = [a for a in sys.argv[1:] if a in VERSIONI] or list(VERSIONI)
    lavori = [('Voynich', 0)] + [(v, s) for v in versioni for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] == 'Voynich':
                print('Voynich: %s' % {n: round(x, 4) if isinstance(x, float) else x for n, x in r['estesa'].items()}, flush=True)
            else:
                print('%s seme %d: decodifica %s | pagella %d riga %s | AUC e231 %.3f e266 %.3f | estesa %s' % (
                    a[0], a[1], r['decodifica_esatta'], r['pagella'], r['riga'], r['AUC_e231'], r['AUC_e266'],
                    {n: round(x, 4) if isinstance(x, float) else x for n, x in r['estesa'].items()}), flush=True)
    voy = ris[('Voynich', 0)]['estesa']
    metro = OrderedDict((n, passa(n, voy[n], voy)) for n in FASCE)
    contate = [n for n in FASCE if metro[n]]
    sintesi = OrderedDict()
    for v in versioni:
        rs = [ris[(v, s)] for s in SEMI]
        for r in rs:
            r['estesa_passate'] = [n for n in contate if passa(n, r['estesa'][n], voy)]
        sintesi[v] = OrderedDict([('decodifica_esatta', all(r['decodifica_esatta'] for r in rs)), ('pagella_somma', sum(r['pagella'] for r in rs)),
                                  ('estesa_somma', sum(r['pagella'] + len(r['estesa_passate']) for r in rs)), ('semi_con_riga', sum(bool(r['riga']) for r in rs)),
                                  ('AUC_e231_media', statistics.mean(r['AUC_e231'] for r in rs)), ('AUC_e266_media', statistics.mean(r['AUC_e266'] for r in rs)),
                                  ('materie_estese_mancate', dict(Counter(n for r in rs for n in contate if n not in r['estesa_passate'])))])
    nome_file = 'e293_banco' if versioni == list(VERSIONI)[:2] else 'e293_banco_' + '_'.join(versioni)
    out = OrderedDict([('Voynich', voy), ('metro_valido', metro), ('versioni', OrderedDict((v, [ris[(v, s)] for s in SEMI]) for v in versioni)), ('sintesi', sintesi)])
    json.dump(out, open(os.path.join(RISULTATI, nome_file + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e293 — Pagella estesa e banco di prova del voynichizzatore', '',
          'Testo nascosto: Isidoro XVII (inizio), chiave "banco"; corpi con i semi 7, 8, 9. Pagella estesa = 18 materie dell\'e224 + %d (su 8) con il metro valido. '
          'Preregistrazione: `preregistrazioni/e293.md`.' % len(contate), '', '| materia aggiunta | Voynich | fascia | metro valido |', '|---|---|---|---|']
    for n in FASCE:
        fascia = {'parole rare per pagina': 'R ≤ 5', 'prime righe come registro': 'z > 3', 'scelte di riga': '≥ 10 su 12'}.get(n, '±%s' % FASCE[n])
        md.append('| %s | %s | %s | %s |' % (n, ('%.4f' % voy[n]) if isinstance(voy[n], float) else voy[n], fascia, 'sì' if metro[n] else 'NO'))
    md += ['', '| versione | seme | decodifica | pagella | riga | materie aggiunte passate | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|---|']
    for v in versioni:
        for s in SEMI:
            r = ris[(v, s)]
            md.append('| %s | %d | %s | %d/18 | %s | %d/%d | %.3f | %.3f |' % (v, s, 'esatta' if r['decodifica_esatta'] else 'NO', r['pagella'], 'sì' if r['riga'] else 'no',
                                                                       len(r['estesa_passate']), len(contate), r['AUC_e231'], r['AUC_e266']))
    md += ['', '| versione | pagella (3 semi) | pagella estesa (3 semi) | riga | AUC e231 | AUC e266 | materie aggiunte mancate |', '|---|---|---|---|---|---|---|']
    for v, x in sintesi.items():
        md.append('| %s | %d/54 | %d/%d | %d | %.3f | %.3f | %s |' % (v, x['pagella_somma'], x['estesa_somma'], 3 * (18 + len(contate)), x['semi_con_riga'], x['AUC_e231_media'],
                                                             x['AUC_e266_media'], ', '.join('%s (%d)' % kv for kv in x['materie_estese_mancate'].items()) or '—'))
    open(os.path.join(RISULTATI, nome_file + '.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({v: {k2: x[k2] for k2 in ('pagella_somma', 'estesa_somma', 'AUC_e231_media', 'AUC_e266_media')} for v, x in sintesi.items()}, default=float))


if __name__ == '__main__':
    main()
