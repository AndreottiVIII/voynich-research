# -*- coding: utf-8 -*-
"""Esperimento 404: il sacco, secondo pezzo: le parole note della pagina (lessico di sezione e lingua, ripetizione con un
parametro theta regolato sul pannello), e il primo generatore intero a pezzi. Strati: K1 lessico di sezione senza
ripetizione; K2 con ripetizione; K4 anche le parole nuove inventate (T-LPS dell'e403b); K5 = K4 ridisposto dal modello
dell'e401b (giudici interi e pagelle).

    PROCESSI=10 python esegui.py e404
    python esperimenti/e404_parole_note.py --prova     (costruzione e due giri di regolazione, nessun giudice)

Preregistrazione: preregistrazioni/e404.md. Scrive risultati/e404_parole_note.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e400_scala_controlli as e400
import e401_disposizione as e401
import e402_sacco_generatori as e402
import e403_parole_nuove as e403

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('K1', 'lessico di sezione, senza ripetizione'), ('K2', 'lessico di sezione con ripetizione'),
                      ('K4', 'K2 e parole nuove inventate'), ('K5', 'K4 ridisposto (generatore intero a pezzi)')])
PREVISTE = {'K1': (0.80, 0.92), 'K2': (0.60, 0.75), 'K4': (0.68, 0.80)}
PREVISTE_K5 = {'AUC_e231': (0.72, 0.84), 'AUC_e266': (0.78, 0.90)}
SEME_REGOLAZIONE, GIRI, TOLLERANZA = 11, 12, 0.03
PAGINA = ('G3 tipi su parole', 'G3 uniche nella pagina', 'G3 uniche nel testo', 'G3 fra le 100 piu frequenti', 'G3 lunghezza media',
          'G3 lunghezza deviazione', 'G9 JSD pagina-manoscritto')
_S = {}


def sacco():
    if 's' not in _S:
        import sacco as modulo
        rr, tipo = e400.voynich()
        _S['s'] = modulo.Sacco(rr, tipo)
    return _S['s']


def tipi_su_parole(rr):
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).extend(ps)
    return statistics.mean(len(set(ws)) / len(ws) for ws in per.values() if len(ws) >= 40)


def regola(giri=GIRI, stampa=True):
    s = sacco()
    bersaglio = tipi_su_parole(s.rr)
    theta, traccia, migliore = 100.0, [], None
    for g in range(giri):
        val = tipi_su_parole(s.genera(SEME_REGOLAZIONE, theta=theta))
        scarto = val / bersaglio - 1
        traccia.append(OrderedDict([('giro', g), ('theta', theta), ('tipi su parole', val), ('scarto', scarto)]))
        if stampa:
            print('giro %2d: theta %.1f | tipi su parole %.4f (Voynich %.4f) | scarto %+.3f' % (g, theta, val, bersaglio, scarto), flush=True)
        if migliore is None or abs(scarto) < abs(migliore[0]):
            migliore = (scarto, theta, val)
        if abs(scarto) < 0.003:
            break
        theta *= math.exp(4.0 * math.log(bersaglio / val))
    return OrderedDict([('bersaglio', bersaglio), ('theta', migliore[1]), ('valore', migliore[2]), ('scarto', migliore[0]),
                        ('converge', abs(migliore[0]) <= TOLLERANZA), ('traccia', traccia)])


def testo(strato, seme, theta):
    s = sacco()
    base = 404000 + seme
    if strato == 'K1':
        return s.genera(base, theta=None)
    if strato == 'K2':
        return s.genera(base, theta=theta)
    t = s.genera(base, theta=theta, nuove='inventate')
    if strato == 'K5':
        t = e401.modello(s.rr).disponi(t, base + 500, 'D3', pesi=e402.pesi_e401b())
    return t


def lavoro(args):
    strato, seme, theta = args
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    if strato == 'V':
        return (strato, seme), OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(sacco().rr)),
                                            ('pagina', OrderedDict((n, float(k['vt266'][1][:, k['vt266'][2].index(n)].mean())) for n in PAGINA))])
    t = testo(strato, seme, theta)
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    s = e403.sotto_auc(k['vt266'], tab)
    nf = tab[2]
    out = OrderedDict([('solo_sacco', s['solo sacco']), ('sotto', OrderedDict((n, s[n]) for n in e403.SOTTO)), ('pesanti', s['pesanti']),
                       ('pagina', OrderedDict((n, float(tab[1][:, nf.index(n)].mean())) for n in PAGINA))])
    if strato == 'K5':
        out['intero'] = e402.misura(t, k)
    return (strato, seme), out


def prova():
    s = sacco()
    for strato in STRATI:
        t = testo(strato, 1, 150.0) if strato != 'K5' else None
        if t:
            assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in s.rr]
            uniche = sum(s.conta[a] == 1 for _, _, ps in s.rr for a in ps)
            stesse = sum(a == b for (_, _, x), (_, _, y) in zip(s.rr, t) for a, b in zip(x, y) if s.conta[a] == 1)
            print('%s: tipi su parole %.4f; parole uniche vere rimaste al loro posto %d su %d' % (strato, tipi_su_parole(t), stesse, uniche))
    r = regola(giri=2)
    print('regolazione a posto (due giri): theta %.1f' % r['theta'])


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    reg = regola()
    theta = reg['theta']
    print('theta scelto %.1f, scarto %+.3f, converge %s' % (theta, reg['scarto'], reg['converge']), flush=True)
    lavori = [('V', 0, None)] + [(s, seme, theta) for s in STRATI for seme in SEMI]
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
                         ('pagina', OrderedDict((n, media(lambda r: r['pagina'][n])) for n in PAGINA)), ('pesanti', rs[0]['pesanti'])])
        if s == 'K5':
            ii = [r['intero'] for r in rs]
            for r in ii:
                r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
            mi = lambda f: statistics.mean(f(r) for r in ii)
            x['intero'] = OrderedDict([
                ('AUC_e231', mi(lambda r: r['AUC_e231'])), ('AUC_e266', mi(lambda r: r['AUC_e266'])), ('previste', PREVISTE_K5),
                ('gruppi', OrderedDict((n, mi(lambda r: r['gruppi_e266'][n])) for n in ii[0]['gruppi_e266'] if ii[0]['gruppi_e266'][n] is not None)),
                ('pagella_media', mi(lambda r: r['pagella'])), ('estese_media', mi(lambda r: len(r['estese_passate']))),
                ('semi_con_riga', sum(bool(r['riga']) for r in ii)),
                ('materie_mancate', sorted({m for r in ii for m in r['mancano']} | {m for r in ii for m in e293.FASCE if m not in r['estese_passate']})),
                ('pannello', OrderedDict((n, mi(lambda r: r['pannello'][n])) for n in ii[0]['pannello'])),
                ('pesanti_e266', ii[0]['pesanti_e266'][:10]), ('pesanti_e231', ii[0]['pesanti_e231'][:6])])
        sintesi[s] = x
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('sintesi', sintesi),
                       ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e404_parole_note.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e404 — Il sacco, secondo pezzo: le parole note della pagina, e il primo generatore intero a pezzi', '',
          'Impaginazione vera; semi 1–4 (medie). Solo sacco: pavimento 0,50; v5 0,794; modello del Voynich 0,959; parole nuove da sole 0,644 (e403b). '
          'Preregistrazione: `preregistrazioni/e404.md`.', '',
          'Regolazione di θ sul pannello (seme %d): θ = %.1f, tipi su parole %.4f (Voynich %.4f), scarto %+.3f: %s.' % (
              SEME_REGOLAZIONE, reg['theta'], reg['valore'], reg['bersaglio'], reg['scarto'], 'converge' if reg['converge'] else '**non converge**'), '',
          '| strato | che cosa | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |', '|---|---|---|---|---|---|---|---|']
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f (%.3f–%.3f) | %s | %s |' % (s, x['che cosa'], x['solo_sacco'], x['min_max'][0], x['min_max'][1],
                                                              ('%.2f–%.2f' % x['prevista']) if x['prevista'] else '—', ' | '.join('%.2f' % v for v in x['sotto'].values())))
    md += ['', '## Valori di pagina (media delle pagine)', '', '| | ' + ' | '.join(PAGINA) + ' |', '|---|' + '---|' * len(PAGINA),
           '| Voynich | ' + ' | '.join('%.4f' % voy['pagina'][n] for n in PAGINA) + ' |']
    md += ['| %s | %s |' % (s, ' | '.join('%.4f' % x['pagina'][n] for n in PAGINA)) for s, x in sintesi.items()]
    i5 = sintesi['K5']['intero']
    md += ['', '## K5: il generatore intero a pezzi, giudici interi e pagelle', '',
           'Per confronto, sugli stessi semi: v5 0,812 / 0,918 (pagella 16,5/18); v5 ridisposta 0,797 / 0,842; sacco vero ridisposto 0,533 / 0,659.', '',
           '| AUC e231 (prevista) | AUC e266 (prevista) | pagella | estese | riga | ' + ' | '.join(i5['gruppi']) + ' |', '|---|---|---|---|---|' + '---|' * len(i5['gruppi']),
           '| %.3f (%.2f–%.2f) | %.3f (%.2f–%.2f) | %.1f/18 | %.1f/8 | %d/4 | %s |' % (
               i5['AUC_e231'], PREVISTE_K5['AUC_e231'][0], PREVISTE_K5['AUC_e231'][1], i5['AUC_e266'], PREVISTE_K5['AUC_e266'][0], PREVISTE_K5['AUC_e266'][1],
               i5['pagella_media'], i5['estese_media'], i5['semi_con_riga'], ' | '.join('%.2f' % v for v in i5['gruppi'].values())), '',
           'Materie mancate in almeno un seme: %s.' % (', '.join(i5['materie_mancate']) or 'nessuna'), '',
           '| giudice | caratteristica | coefficiente | Voynich | K5 |', '|---|---|---|---|---|']
    md += ['| e266 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in i5['pesanti_e266']]
    md += ['| e231 | %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in i5['pesanti_e231']]
    md += ['', '## Caratteristiche più pesanti del solo sacco (seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s — %s**' % (s, x['che cosa']), '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti']]
        md.append('')
    open(os.path.join(RISULTATI, 'e404_parole_note.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(dict({s: round(x['solo_sacco'], 3) for s, x in sintesi.items()}, K5_intero=[round(i5['AUC_e231'], 3), round(i5['AUC_e266'], 3)])))


if __name__ == '__main__':
    main()
