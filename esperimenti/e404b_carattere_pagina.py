# -*- coding: utf-8 -*-
"""Esperimento 404b: il sacco, terzo pezzo: il carattere della pagina nei segni. Come l'e404, ma ogni pagina riceve gli
scostamenti dei segni di un'altra pagina vera della stessa sezione e lingua, e le parole note si pescano dal lessico di
sezione con peso exp(kappa * scostamenti). kappa si regola sul pannello (JSD pagina-manoscritto come nel Voynich).
Strati: C2 (parole nuove vere), C4 (inventate sul profilo generato), C5 (C4 ridisposto: giudici interi e pagelle).

    PROCESSI=10 python esegui.py e404b
    python esperimenti/e404b_carattere_pagina.py --prova     (costruzione e due giri di regolazione, nessun giudice)

Preregistrazione: preregistrazioni/e404b.md. Scrive risultati/e404b_carattere_pagina.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e401_disposizione as e401
import e402_sacco_generatori as e402
import e403_parole_nuove as e403
import e404_parole_note as e404

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('C2', 'lessico di sezione, ripetizione e carattere; parole nuove vere'), ('C4', 'C2 e parole nuove inventate sul profilo generato'),
                      ('C5', 'C4 ridisposto (generatore intero a pezzi)')])
PREVISTE = {'C2': (0.58, 0.70), 'C4': (0.64, 0.76)}
PREVISTE_C5 = {'AUC_e231': (0.62, 0.74), 'AUC_e266': (0.74, 0.85)}
SEME_REGOLAZIONE, GIRI, TOLLERANZA = 11, 14, 0.03
D = misure.divisore(misure.GLIFI_EVA)


def theta_e404():
    return json.load(open(os.path.join(RISULTATI, 'e404_parole_note.json'), encoding='utf-8'))['regolazione']['theta']


def jsd_pagina(rr):
    """Media delle pagine (almeno 40 parole) della JSD fra i segni della pagina e quelli del testo (come G9 dell'e266)."""
    import e266_discriminatore_forte as e266
    cache = {}
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).extend(ps)
    conti = {}
    for p, ws in per.items():
        c = Counter()
        for w in ws:
            if w not in cache:
                cache[w] = Counter(D(w))
            c.update(cache[w])
        conti[p] = c
    glob = Counter()
    for c in conti.values():
        glob.update(c)
    return statistics.mean(e266.jsd(conti[p], glob) for p, ws in per.items() if len(ws) >= 40)


def regola(theta, giri=GIRI, stampa=True):
    """theta e kappa insieme (integrazione della preregistrazione): kappa sulla JSD, theta su tipi su parole."""
    s = e404.sacco()
    b_jsd, b_tsp = jsd_pagina(s.rr), e404.tipi_su_parole(s.rr)
    kappa, traccia, migliore = 1.0, [], None
    for g in range(giri):
        t = s.genera(SEME_REGOLAZIONE, theta=theta, kappa=kappa)
        val, tsp = jsd_pagina(t), e404.tipi_su_parole(t)
        scarto = max(abs(val / b_jsd - 1), abs(tsp / b_tsp - 1))
        traccia.append(OrderedDict([('giro', g), ('kappa', kappa), ('theta', theta), ('JSD', val), ('tipi su parole', tsp), ('scarto', scarto)]))
        if stampa:
            print('giro %2d: kappa %.3f theta %.0f | JSD %.4f (Voynich %.4f) | tipi su parole %.4f (Voynich %.4f) | scarto massimo %.3f' % (
                g, kappa, theta, val, b_jsd, tsp, b_tsp, scarto), flush=True)
        if migliore is None or scarto < migliore[0]:
            migliore = (scarto, kappa, theta, val, tsp)
        if scarto < 0.005:
            break
        kappa *= math.exp(1.2 * math.log(b_jsd / val))
        theta = min(1e7, theta * math.exp(4.0 * math.log(b_tsp / tsp)))
    return OrderedDict([('bersaglio', b_jsd), ('bersaglio_tipi', b_tsp), ('kappa', migliore[1]), ('theta', migliore[2]), ('valore', migliore[3]),
                        ('scarto', migliore[0]), ('tipi su parole', migliore[4]), ('converge', migliore[0] <= TOLLERANZA), ('traccia', traccia)])


def testo(strato, seme, theta, kappa):
    s = e404.sacco()
    base = 404500 + seme
    if strato == 'C2':
        return s.genera(base, theta=theta, kappa=kappa)
    t = s.genera(base, theta=theta, nuove='inventate', kappa=kappa)
    if strato == 'C5':
        t = e401.modello(s.rr).disponi(t, base + 500, 'D3', pesi=e402.pesi_e401b())
    return t


def lavoro(args):
    strato, seme, theta, kappa = args
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    if strato == 'V':
        return (strato, seme), OrderedDict([('estesa', e293.pagella_estesa(e404.sacco().rr)),
                                            ('pagina', OrderedDict((n, float(k['vt266'][1][:, k['vt266'][2].index(n)].mean())) for n in e404.PAGINA))])
    t = testo(strato, seme, theta, kappa)
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    s = e403.sotto_auc(k['vt266'], tab)
    nf = tab[2]
    out = OrderedDict([('solo_sacco', s['solo sacco']), ('sotto', OrderedDict((n, s[n]) for n in e403.SOTTO)), ('pesanti', s['pesanti']),
                       ('pagina', OrderedDict((n, float(tab[1][:, nf.index(n)].mean())) for n in e404.PAGINA))])
    if strato == 'C5':
        out['intero'] = e402.misura(t, k)
    return (strato, seme), out


def prova():
    s = e404.sacco()
    theta = theta_e404()
    for strato in ('C2', 'C4'):
        t = testo(strato, 1, theta, 1.0)
        assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in s.rr]
        stesse = sum(a == b for (_, _, x), (_, _, y) in zip(s.rr, t) for a, b in zip(x, y) if s.conta[a] == 1)
        print('%s: tipi su parole %.4f, JSD %.4f; parole uniche vere rimaste %d' % (strato, e404.tipi_su_parole(t), jsd_pagina(t), stesse))
    r = regola(theta, giri=2)
    print('regolazione a posto (due giri): kappa %.3f; theta %.0f' % (r['kappa'], r['theta']))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    reg = regola(theta_e404())
    kappa, theta = reg['kappa'], reg['theta']
    print('kappa scelta %.3f, theta %.0f, scarto massimo %.3f, converge %s' % (kappa, theta, reg['scarto'], reg['converge']), flush=True)
    lavori = [('V', 0, None, None)] + [(s, seme, theta, kappa) for s in STRATI for seme in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                extra = ' | intero e231 %.3f e266 %.3f pagella %d' % (r['intero']['AUC_e231'], r['intero']['AUC_e266'], r['intero']['pagella']) if 'intero' in r else ''
                print('%s seme %d: solo sacco %.3f %s%s' % (a[0], a[1], r['solo_sacco'], {n: round(x, 2) for n, x in r['sotto'].items()}, extra), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for s in STRATI:
        rs = [ris[(s, seme)] for seme in SEMI]
        media = lambda f: statistics.mean(f(r) for r in rs)
        x = OrderedDict([('che cosa', STRATI[s]), ('solo_sacco', media(lambda r: r['solo_sacco'])),
                         ('min_max', [min(r['solo_sacco'] for r in rs), max(r['solo_sacco'] for r in rs)]), ('prevista', PREVISTE.get(s)),
                         ('sotto', OrderedDict((n, media(lambda r: r['sotto'][n])) for n in e403.SOTTO)),
                         ('pagina', OrderedDict((n, media(lambda r: r['pagina'][n])) for n in e404.PAGINA)), ('pesanti', rs[0]['pesanti'])])
        if s == 'C5':
            ii = [r['intero'] for r in rs]
            for r in ii:
                r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
            mi = lambda f: statistics.mean(f(r) for r in ii)
            x['intero'] = OrderedDict([
                ('AUC_e231', mi(lambda r: r['AUC_e231'])), ('AUC_e266', mi(lambda r: r['AUC_e266'])), ('previste', PREVISTE_C5),
                ('gruppi', OrderedDict((n, mi(lambda r: r['gruppi_e266'][n])) for n in ii[0]['gruppi_e266'] if ii[0]['gruppi_e266'][n] is not None)),
                ('pagella_media', mi(lambda r: r['pagella'])), ('estese_media', mi(lambda r: len(r['estese_passate']))),
                ('semi_con_riga', sum(bool(r['riga']) for r in ii)),
                ('materie_mancate', sorted({m for r in ii for m in r['mancano']} | {m for r in ii for m in e293.FASCE if m not in r['estese_passate']})),
                ('pannello', OrderedDict((n, mi(lambda r: r['pannello'][n])) for n in ii[0]['pannello'])),
                ('pesanti_e266', ii[0]['pesanti_e266'][:10]), ('pesanti_e231', ii[0]['pesanti_e231'][:6])])
        sintesi[s] = x
    out = OrderedDict([('regolazione', reg), ('theta', theta), ('Voynich', voy), ('sintesi', sintesi),
                       ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e404b_carattere_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e404b — Il sacco, terzo pezzo: il carattere della pagina nei segni', '',
          'Impaginazione vera; semi 1–4 (medie). Riferimenti (e404): K2 0,777, K4 0,756, K5 intero 0,716 / 0,857. Preregistrazione: `preregistrazioni/e404b.md`.', '',
          'Regolazione di κ e θ insieme sul pannello (seme %d): κ = %.3f, θ = %.0f; JSD pagina-manoscritto %.4f (Voynich %.4f), tipi su parole %.4f (Voynich %.4f); '
          'scarto massimo %.3f: %s.' % (SEME_REGOLAZIONE, reg['kappa'], theta, reg['valore'], reg['bersaglio'], reg['tipi su parole'], reg['bersaglio_tipi'], reg['scarto'],
                                        'converge' if reg['converge'] else '**non converge**'), '',
          '| strato | che cosa | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |', '|---|---|---|---|---|---|---|---|']
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f (%.3f–%.3f) | %s | %s |' % (s, x['che cosa'], x['solo_sacco'], x['min_max'][0], x['min_max'][1],
                                                              ('%.2f–%.2f' % x['prevista']) if x['prevista'] else '—', ' | '.join('%.2f' % v for v in x['sotto'].values())))
    md += ['', '## Valori di pagina (media delle pagine)', '', '| | ' + ' | '.join(e404.PAGINA) + ' |', '|---|' + '---|' * len(e404.PAGINA),
           '| Voynich | ' + ' | '.join('%.4f' % voy['pagina'][n] for n in e404.PAGINA) + ' |']
    md += ['| %s | %s |' % (s, ' | '.join('%.4f' % x['pagina'][n] for n in e404.PAGINA)) for s, x in sintesi.items()]
    i5 = sintesi['C5']['intero']
    md += ['', '## C5: il generatore intero a pezzi, giudici interi e pagelle', '',
           'Per confronto, sugli stessi semi: K5 (e404) 0,716 / 0,857 (pagella 11,5); v5 0,812 / 0,918 (16,5); sacco vero ridisposto 0,533 / 0,659 (14,8).', '',
           '| AUC e231 (prevista) | AUC e266 (prevista) | pagella | estese | riga | ' + ' | '.join(i5['gruppi']) + ' |', '|---|---|---|---|---|' + '---|' * len(i5['gruppi']),
           '| %.3f (%.2f–%.2f) | %.3f (%.2f–%.2f) | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
               i5['AUC_e231'], PREVISTE_C5['AUC_e231'][0], PREVISTE_C5['AUC_e231'][1], i5['AUC_e266'], PREVISTE_C5['AUC_e266'][0], PREVISTE_C5['AUC_e266'][1],
               i5['pagella_media'], i5['estese_media'], i5['semi_con_riga'], ' | '.join('%.2f' % v for v in i5['gruppi'].values())), '',
           'Materie mancate in almeno un seme: %s.' % (', '.join(i5['materie_mancate']) or 'nessuna'), '',
           '| misura del pannello | C5 |', '|---|---|']
    md += ['| %s | %.4f |' % kv for kv in i5['pannello'].items()]
    md += ['', '| giudice | caratteristica | coefficiente | Voynich | C5 |', '|---|---|---|---|---|']
    md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in i5['pesanti_e266']]
    md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in i5['pesanti_e231']]
    md += ['', '## Caratteristiche più pesanti del solo sacco (seme 1)', '']
    for s in ('C2', 'C4'):
        x = sintesi[s]
        md += ['**%s — %s**' % (s, x['che cosa']), '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti']]
        md.append('')
    open(os.path.join(RISULTATI, 'e404b_carattere_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(dict({s: round(x['solo_sacco'], 3) for s, x in sintesi.items()}, C5_intero=[round(i5['AUC_e231'], 3), round(i5['AUC_e266'], 3)])))


if __name__ == '__main__':
    main()
