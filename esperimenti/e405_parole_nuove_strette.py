# -*- coding: utf-8 -*-
"""Esperimento 405: le parole nuove, terzo passo. Tre generatori (parole_nuove.FormeUniche): N1 profilo della pagina solo
sui segni comuni; N2 anche modello a quattro segni con ripiego sui trigrammi; N3 anche forza della scelta regolata sul
pannello (JSD pagina-manoscritto del sacco intero). Due misure: prova isolata (nel Voynich vero si sostituiscono solo le
parole uniche) e sacco intero (parole note con carattere, e404b, piu' parole nuove inventate).

    PROCESSI=10 python esegui.py e405
    python esperimenti/e405_parole_nuove_strette.py --prova     (costruzione, forma e regolazione, nessun giudice)

Preregistrazione: preregistrazioni/e405.md. Scrive risultati/e405_parole_nuove_strette.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e403_parole_nuove as e403
import e404_parole_note as e404
import e404b_carattere_pagina as e404b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
MODI = OrderedDict([('N1', dict(comuni=True)), ('N2', dict(comuni=True, quattro=True)), ('N3', dict(comuni=True, quattro=True))])
PREVISTE = {'N1': ((0.60, 0.66), (0.58, 0.65)), 'N2': ((0.56, 0.64), (0.55, 0.63)), 'N3': (None, (0.53, 0.62))}
SEME_REGOLAZIONE = 11


def parametri_e404b():
    r = json.load(open(os.path.join(RISULTATI, 'e404b_carattere_pagina.json'), encoding='utf-8'))['regolazione']
    return r['theta'], r['kappa']


def isolata(rr, argomenti, seme):
    """Il Voynich con le sole parole uniche sostituite; anche le inventate e la quota di campioni attestati scartati."""
    import parole_nuove
    from disposizione import posizione
    fu = parole_nuove.FormeUniche(rr, **argomenti)
    rnd = random.Random(405000 + seme)
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).extend(ps)
    profili = {p: fu.profilo(ws) for p, ws in per.items()}
    out, inventate = [], []
    for p, ini, ps in rr:
        nuova = []
        for j, w in enumerate(ps):
            if fu.conta[w] == 1:
                w = fu.inventa('T-LPS', 4 * bool(ini) + posizione(j, len(ps)), profili[p], rnd)
                inventate.append(w)
            nuova.append(w)
        out.append((p, ini, nuova))
    return out, inventate, fu.scartate / max(1, fu.campioni)


def intero(argomenti, seme):
    s = e404.sacco()
    theta, kappa = parametri_e404b()
    s.FORME = dict(argomenti)
    return s.genera(405500 + seme, theta=theta, nuove='inventate', kappa=kappa)


def regola_forza(stampa=True):
    """Forza della scelta per profilo (N3): la JSD pagina-manoscritto del sacco intero uguale a quella del Voynich."""
    s = e404.sacco()
    bersaglio = e404b.jsd_pagina(s.rr)
    theta, kappa = parametri_e404b()
    punti = []

    def valuta(f):
        s.FORME = dict(MODI['N3'], forza=f)
        v = e404b.jsd_pagina(s.genera(SEME_REGOLAZIONE, theta=theta, nuove='inventate', kappa=kappa))
        punti.append((f, v))
        if stampa:
            print('forza %.3f: JSD pagina-manoscritto %.4f (Voynich %.4f)' % (f, v, bersaglio), flush=True)
        return v
    valuta(0.0)
    valuta(1.0)
    for _ in range(3):
        (f0, v0), (f1, v1) = sorted(punti, key=lambda x: abs(x[1] - bersaglio))[:2]
        if abs(v1 - v0) < 1e-6 or abs(v0 / bersaglio - 1) < 0.01:
            break
        valuta(min(2.0, max(0.0, f0 + (bersaglio - v0) * (f1 - f0) / (v1 - v0))))
    f, v = min(punti, key=lambda x: abs(x[1] - bersaglio))
    return OrderedDict([('bersaglio', bersaglio), ('forza', f), ('valore', v), ('scarto', v / bersaglio - 1), ('punti', punti)])


def lavoro(args):
    modo, seme, forza = args
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    rr = e404.sacco().rr
    argomenti = dict(MODI[modo])
    if modo == 'N3':
        argomenti['forza'] = forza
    out = OrderedDict()
    for nome in ('isolata', 'intero'):
        if nome == 'isolata':
            if modo == 'N3':
                continue
            t, inventate, scarti = isolata(rr, argomenti, seme)
        else:
            t = intero(argomenti, seme)
        tab = e266.tabella(e251.righe_ini(t), k['rif266'])
        s = e403.sotto_auc(k['vt266'], tab)
        nf = tab[2]
        x = OrderedDict([('solo_sacco', s['solo sacco']), ('sotto', OrderedDict((n, s[n]) for n in e403.SOTTO)), ('pesanti', s['pesanti']),
                         ('pagina', OrderedDict((n, float(tab[1][:, nf.index(n)].mean())) for n in e404.PAGINA + ('G1 f', 'G1 p', 'G1 m')))])
        if nome == 'isolata':
            x['forma'] = e403.forma(inventate, e404.sacco().conta)
            x['attestate_scartate'] = scarti
        out[nome] = x
    return (modo, seme), out


def prova():
    rr = e404.sacco().rr
    for modo, argomenti in MODI.items():
        if modo == 'N3':
            continue
        t, inv, scarti = isolata(rr, argomenti, 1)
        assert len(inv) == len(set(inv)) and not set(inv) & set(e404.sacco().conta)
        print('%s isolata: forma %s, attestate scartate %.3f, esempi %s' % (modo, {n: round(x, 3) for n, x in e403.forma(inv, e404.sacco().conta).items()}, scarti, inv[:8]))
        t = intero(argomenti, 1)
        print('%s sacco intero: JSD %.4f, tipi su parole %.4f' % (modo, e404b.jsd_pagina(t), e404.tipi_su_parole(t)))
    r = regola_forza()
    print('regolazione a posto: forza %.3f, JSD %.4f' % (r['forza'], r['valore']))


def main():
    if '--prova' in sys.argv:
        return prova()
    reg = regola_forza()
    print('forza scelta %.3f, JSD %.4f, scarto %+.3f' % (reg['forza'], reg['valore'], reg['scarto']), flush=True)
    lavori = [(m, s, reg['forza']) for m in MODI for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            print('%s seme %d: %s' % (a[0], a[1], ' | '.join('%s %.3f %s' % (n, x['solo_sacco'], {g: round(v, 2) for g, v in x['sotto'].items()}) for n, x in r.items())), flush=True)
    sintesi = OrderedDict()
    for m in MODI:
        sintesi[m] = OrderedDict()
        for nome in ('isolata', 'intero'):
            rs = [ris[(m, s)][nome] for s in SEMI if nome in ris[(m, s)]]
            if not rs:
                continue
            media = lambda f: statistics.mean(f(r) for r in rs)
            x = OrderedDict([('solo_sacco', media(lambda r: r['solo_sacco'])), ('min_max', [min(r['solo_sacco'] for r in rs), max(r['solo_sacco'] for r in rs)]),
                             ('prevista', PREVISTE[m][0 if nome == 'isolata' else 1]), ('sotto', OrderedDict((n, media(lambda r: r['sotto'][n])) for n in e403.SOTTO)),
                             ('pagina', OrderedDict((n, media(lambda r: r['pagina'][n])) for n in rs[0]['pagina'])), ('pesanti', rs[0]['pesanti'])])
            if nome == 'isolata':
                x['forma'] = OrderedDict((n, media(lambda r: r['forma'][n])) for n in rs[0]['forma'])
                x['attestate_scartate'] = media(lambda r: r['attestate_scartate'])
            sintesi[m][nome] = x
    out = OrderedDict([('regolazione_forza', reg), ('sintesi', sintesi), ('per_seme', OrderedDict(('%s|%d' % a, r) for a, r in ris.items()))])
    json.dump(out, open(os.path.join(RISULTATI, 'e405_parole_nuove_strette.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e405 — Le parole nuove, terzo passo', '',
          'Semi 1–4 (medie). Riferimenti: prova isolata T-LPS 0,644 (e403b); sacco intero C4 0,645, con le parole nuove vere C2 0,482 (e404b). '
          'Parole uniche del Voynich: lunghezza 5,944 ± 1,570; a una modifica da una nota 0,715. Preregistrazione: `preregistrazioni/e405.md`.', '',
          'Forza della scelta per profilo (N3), regolata sul pannello: %.3f (JSD pagina-manoscritto %.4f, Voynich %.4f); punti provati: %s.' % (
              reg['forza'], reg['valore'], reg['bersaglio'], ', '.join('%.2f → %.4f' % p for p in reg['punti'])), '',
          '| generatore | misura | solo sacco (min–max) | previsto | G1 | G2 | G3 | JSD |', '|---|---|---|---|---|---|---|---|']
    for m, y in sintesi.items():
        for nome, x in y.items():
            md.append('| %s | %s | %.3f (%.3f–%.3f) | %s | %s |' % (m, nome, x['solo_sacco'], x['min_max'][0], x['min_max'][1],
                                                                  ('%.2f–%.2f' % x['prevista']) if x['prevista'] else '—', ' | '.join('%.2f' % v for v in x['sotto'].values())))
    md += ['', '## Forma delle inventate (prova isolata)', '', '| generatore | lunghezza | deviazione | a una modifica da una nota | unione di due note | campioni attestati scartati |',
           '|---|---|---|---|---|---|']
    for m, y in sintesi.items():
        if 'isolata' in y:
            md.append('| %s | %s | %.3f |' % (m, ' | '.join('%.3f' % v for v in y['isolata']['forma'].values()), y['isolata']['attestate_scartate']))
    nomi = list(next(iter(sintesi.values()))['intero']['pagina'])
    md += ['', '## Valori di pagina del sacco intero (media delle pagine)', '', '| generatore | ' + ' | '.join(nomi) + ' |', '|---|' + '---|' * len(nomi)]
    md += ['| %s | %s |' % (m, ' | '.join('%.4f' % y['intero']['pagina'][n] for n in nomi)) for m, y in sintesi.items()]
    md += ['', '## Caratteristiche più pesanti del sacco intero (seme 1)', '']
    for m, y in sintesi.items():
        md += ['**%s**' % m, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in y['intero']['pesanti']]
        md.append('')
    open(os.path.join(RISULTATI, 'e405_parole_nuove_strette.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({m: {n: round(x['solo_sacco'], 3) for n, x in y.items()} for m, y in sintesi.items()}))


if __name__ == '__main__':
    main()
