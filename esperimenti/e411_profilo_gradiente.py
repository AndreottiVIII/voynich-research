# -*- coding: utf-8 -*-
"""Esperimento 411: profilo di pagina e gradiente, sopra il corpo della v11. H1: carattere di pagina per posizione nella
parola (primo segno, ultimo, in mezzo), con kappa e theta regolati di nuovo sul pannello; H2: anche il vicinato nella
disposizione (somiglianza con le parole della riga sopra e della riga sotto), con il peso regolato sul rapporto del
gradiente (valori grezzi della pagella). Misure come nell'e410 (semi 1-4).

    PROCESSI=9 python esegui.py e411
    python esperimenti/e411_profilo_gradiente.py --prova     (costruzione, nessun giudice)

Preregistrazione: preregistrazioni/e411.md. Scrive risultati/e411_profilo_gradiente.json e .md.
"""
import json, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e404_parole_note as e404
import e404b_carattere_pagina as e404b
import e406_generatore_pezzi as e406
import e410_cancello_riga as e410

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('H1', 'carattere di pagina per posizione nella parola'), ('H2', 'H1 e vicinato fra righe')])
SEME_REGOLAZIONE, GIRI_VICINATO = 11, 7
PROFILO = ('V3_R', 'V3_quota_media', 'somiglianza_riga', 'somiglianza_riga_sotto', 'somiglianza_6_righe', 'verticale', 'confine')


def v11():
    import pezzi
    return json.load(open(pezzi.PARAMETRI % 'v11', encoding='utf-8'), object_pairs_hook=OrderedDict)


def regola_carattere(stampa=True):
    """kappa e theta con il carattere per posizione (stessa regolazione dell'e404b)."""
    x = v11()
    s = e404.sacco()
    s.POSIZIONALE = True
    s.FORME = dict(x['forme'])
    r = e404b.regola(x['theta'], stampa=stampa)
    x['carattere'], x['kappa'], x['theta'] = 'posizionale', r['kappa'], r['theta']
    return x, r


def gradiente(valori):
    return valori['somiglianza_6_righe'] / valori['somiglianza_riga'] if valori['somiglianza_riga'] > 0 else 0.0


def regola_vicinato(x, giri=GIRI_VICINATO, stampa=True):
    import e251_lessico_sezione as e251
    import pezzi
    k = e251._prepara()
    voy, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = gradiente(e251.pagella_grezza(k['c'], voy)['valori'])
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, x)
    w, traccia, migliore = 4.0, [], None
    for g in range(giri):
        pesi = dict(x['pesi_disposizione'], vicinato=w)
        val = e251.pagella_grezza(k['c'], d.disponi(sacco, SEME_REGOLAZIONE, 'D3', pesi=pesi))['valori']
        gr = gradiente(val)
        traccia.append(OrderedDict([('giro', g), ('vicinato', w), ('gradiente', gr)] + [(n, val[n]) for n in PROFILO if n in val]))
        if stampa:
            print('vicinato %.2f: gradiente %.3f (Voynich %.3f) | nella riga %.4f, riga sotto %.4f, a 6 righe %.4f | verticale %.3f' % (
                w, gr, bersaglio, val['somiglianza_riga'], val['somiglianza_riga_sotto'], val['somiglianza_6_righe'], val['verticale']), flush=True)
        if migliore is None or abs(gr - bersaglio) < abs(migliore[1] - bersaglio):
            migliore = (w, gr)
        if abs(gr - bersaglio) < 0.03:
            break
        w = min(40.0, max(0.0, w + 15.0 * (bersaglio - gr)))
    y = OrderedDict(x)
    y['pesi_disposizione'] = dict(x['pesi_disposizione'], vicinato=migliore[0])
    return y, OrderedDict([('bersaglio', bersaglio), ('vicinato', migliore[0]), ('gradiente', migliore[1]), ('traccia', traccia)])


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
    t = d.disponi(pezzi.sacco_di(411000 + seme, x), 411500 + seme, 'D3', pesi=x['pesi_disposizione'])
    return (strato, seme), e406.misura(t, k, voy)


def prova():
    import pezzi
    x = dict(v11(), carattere='posizionale')
    x['pesi_disposizione'] = dict(x['pesi_disposizione'], vicinato=4.0)
    rr, _ = pezzi.voynich()
    pagine = list(OrderedDict((p, 1) for p, _, _ in rr))[:10]
    sacco = [r for r in pezzi.sacco_di(1, x) if r[0] in pagine]
    _, d = pezzi.pezzi()
    t = d.disponi(sacco, 1, 'D3', pesi=x['pesi_disposizione'], passate=10)
    assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in sacco]
    assert sorted(w for _, _, ps in t for w in ps) == sorted(w for _, _, ps in sacco for w in ps)
    print('costruzione a posto: %d righe; JSD del sacco intero %.4f' % (len(t), e404b.jsd_pagina(pezzi.sacco_di(1, x))))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    x1, r1 = regola_carattere()
    print('carattere per posizione: kappa %.3f, theta %.0f, scarto massimo %.3f, converge %s' % (r1['kappa'], r1['theta'], r1['scarto'], r1['converge']), flush=True)
    x2, r2 = regola_vicinato(x1)
    print('vicinato scelto %.2f: gradiente %.3f (Voynich %.3f)' % (r2['vicinato'], r2['gradiente'], r2['bersaglio']), flush=True)
    par = {'H1': x1, 'H2': x2}
    lavori = [('V', 0, None)] + [(s, seme, par[s]) for s in STRATI for seme in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                    {n: round(r['valori'][n], 3) for n in ('V3_R', 'somiglianza_riga', 'somiglianza_6_righe') if r['valori'].get(n) is not None}), flush=True)
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
            ('cancello_per_seme', OrderedDict((n, [r['valori'].get(n) for r in rs]) for n in e410.CANCELLO)),
            ('profilo_per_seme', OrderedDict((n, [r['valori'].get(n) for r in rs]) for n in PROFILO)),
            ('gradiente_per_seme', [gradiente(r['valori']) for r in rs]),
            ('JSD_meta', media(lambda r: r['pannello']['G9 JSD prima-seconda meta'])),
            ('estesa', OrderedDict((n, media(lambda r: float(r['estesa'][n]))) for n in e293.FASCE if all(r['estesa'][n] is not None for r in rs))),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10])])
    out = OrderedDict([('regolazione_carattere', r1), ('regolazione_vicinato', r2), ('parametri', par), ('Voynich', voy), ('sintesi', sintesi),
                       ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e411_profilo_gradiente.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['H1']['gruppi'])
    md = ['# e411 — Profilo di pagina e gradiente', '',
          'Semi 1–4 (medie), corpo senza messaggio. Riferimento: G2 dell\'e410 (corpo della v11) 0,552 / 0,616, pagella 15,8/18, cancello 3/4. '
          'Preregistrazione: `preregistrazioni/e411.md`.', '',
          '- Carattere per posizione: κ = %.3f, θ = %.0f; JSD pagina-manoscritto %.4f (Voynich %.4f), tipi su parole %.4f; scarto massimo %.3f: %s.' % (
              r1['kappa'], r1['theta'], r1['valore'], r1['bersaglio'], r1['tipi su parole'], r1['scarto'], 'converge' if r1['converge'] else '**non converge**'),
          '- Vicinato: peso %.2f; gradiente %.3f (Voynich %.3f); giri: %s.' % (
              r2['vicinato'], r2['gradiente'], r2['bersaglio'], ', '.join('%.1f → %.3f' % (t['vicinato'], t['gradiente']) for t in r2['traccia'])), '',
          '| strato | che cosa | AUC e231 | AUC e266 (min–max) | solo sacco | pagella | estese | semi con il cancello | JSD fra le due metà (Voynich 0,0503) | ' + ' | '.join(gr) + ' |',
          '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f | %.3f (%.3f–%.3f) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %.4f | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['AUC_solo_sacco'], x['pagella_media'],
            x['estese_media'], x['semi_con_riga'], x['JSD_meta'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    fmt = lambda vs: ', '.join('%.3f' % v if v is not None else '—' for v in vs)
    md += ['', 'Valori per seme (profilo pagina: R fra 0,8 e 1,25; gradiente fra 0,70 e 0,97; cancello: S1 ≤ 0,7, A ≥ 1,0, scelte ≥ 3, r 0,207 ± 0,07):', '',
           '| | ' + ' | '.join(sintesi) + ' |', '|---|' + '---|' * len(sintesi),
           '| gradiente | ' + ' | '.join(fmt(x['gradiente_per_seme']) for x in sintesi.values()) + ' |']
    md += ['| %s | %s |' % (n, ' | '.join(fmt(x['profilo_per_seme'][n]) for x in sintesi.values())) for n in PROFILO]
    md += ['| %s | %s |' % (n, ' | '.join(fmt(x['cancello_per_seme'][n]) for x in sintesi.values())) for n in e410.CANCELLO]
    md += ['', '## Materie mancate (su 4 semi)', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    md += ['| materia aggiunta | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, float(voy['estesa'][n]), ' | '.join('%.4g' % x['estesa'].get(n, float('nan')) for x in sintesi.values())) for n in e293.FASCE]
    md += ['', '## Caratteristiche più pesanti (giudice e266, seme 1)', '']
    for s, x in sintesi.items():
        md += ['**%s**' % s, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(c) for c in x['pesanti_e266']]
        md.append('')
    open(os.path.join(RISULTATI, 'e411_profilo_gradiente.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media'], x['semi_con_riga']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
