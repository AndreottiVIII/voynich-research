# -*- coding: utf-8 -*-
"""Esperimento 406: il generatore intero a pezzi (voynichizzatore/pezzi.py). Strati: P1 posti delle parole nuove veri e pesi
della disposizione dell'e401b; P2 posti dal modello; P3 anche i pesi dei legami regolati sul pannello sul sacco generato.
Giudici interi con gruppi, pagella con i valori grezzi, pagella estesa, pannello, trigrammi copiati dal Voynich. Scrive
anche voynichizzatore/pezzi_parametri.json con la configurazione scelta secondo la preregistrazione (versione v8).

    PROCESSI=10 python esegui.py e406
    python esperimenti/e406_generatore_pezzi.py --prova     (costruzione e due giri di regolazione, nessun giudice)

Preregistrazione: preregistrazioni/e406.md. Scrive risultati/e406_generatore_pezzi.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e401_disposizione as e401
import e401b_disposizione_regolata as e401b
import e402_sacco_generatori as e402

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (1, 2, 3, 4)
STRATI = OrderedDict([('P1', 'posti delle parole nuove veri; pesi della disposizione dell\'e401b'), ('P2', 'posti dal modello; pesi dell\'e401b'),
                      ('P3', 'posti dal modello; pesi regolati sul sacco generato')])
PREVISTE = {'P1': ((0.62, 0.70), (0.72, 0.80)), 'P2': ((0.59, 0.73), (0.69, 0.83)), 'P3': ((0.58, 0.66), (0.68, 0.77))}
SEME_REGOLAZIONE, PASSATE_REGOLAZIONE, GIRI, TOLLERANZA = 11, 30, 15, 0.10


def base():
    """Parametri del sacco: theta e kappa dell'e404b, parole nuove N3 dell'e405."""
    r = json.load(open(os.path.join(RISULTATI, 'e404b_carattere_pagina.json'), encoding='utf-8'))['regolazione']
    f = json.load(open(os.path.join(RISULTATI, 'e405_parole_nuove_strette.json'), encoding='utf-8'))['regolazione_forza']['forza']
    return OrderedDict([('theta', r['theta']), ('kappa', r['kappa']), ('forme', OrderedDict([('comuni', True), ('quattro', True), ('forza', f)]))])


def configurazione(strato, pesi_generato):
    x = base()
    x['posti'] = 'veri' if strato == 'P1' else 'modello'
    x['pesi_disposizione'] = dict(pesi_generato if strato == 'P3' else e402.pesi_e401b())
    return x


def regola(giri=GIRI, passate=PASSATE_REGOLAZIONE, stampa=True):
    """I quattro pesi dei legami, come nell'e401b, ma disponendo il sacco generato (posti dal modello)."""
    import pezzi
    rr, _ = pezzi.voynich()
    _, d = pezzi.pezzi()
    bersaglio = e401b.quattro(rr)
    sacco = pezzi.sacco_di(SEME_REGOLAZIONE, dict(base(), posti='modello'))
    pesi = OrderedDict((k, float(v)) for k, v in e402.pesi_e401b().items())
    traccia, migliore = [], None
    for g in range(giri):
        val = e401b.quattro(d.disponi(sacco, SEME_REGOLAZIONE, 'D3', pesi=pesi, passate=passate))
        peggio = max(abs(val[n] / bersaglio[n] - 1) for n in e401b.LEGA)
        traccia.append(OrderedDict([('giro', g), ('pesi', OrderedDict(pesi)), ('valori', val), ('scarto_massimo', peggio)]))
        if stampa:
            print('giro %2d: pesi %s | valori %s | scarto massimo %.3f' % (g, {k: round(x, 3) for k, x in pesi.items()},
                                                                        {k: round(x, 4) for k, x in val.items()}, peggio), flush=True)
        if migliore is None or peggio < migliore[0]:
            migliore = (peggio, OrderedDict(pesi), val)
        if peggio < 0.02:
            break
        for n, (peso, guadagno) in e401b.LEGA.items():
            pesi[peso] += guadagno * math.log(bersaglio[n] / max(val[n], 1e-4))
            if peso != 'identica':
                pesi[peso] = max(0.0, pesi[peso])
    return OrderedDict([('bersaglio', bersaglio), ('pesi', migliore[1]), ('valori', migliore[2]), ('scarto_massimo', migliore[0]),
                        ('converge', migliore[0] <= TOLLERANZA), ('traccia', traccia)])


def trigrammi(rr):
    return Counter(tuple(ws[i:i + 3]) for _, _, ws in rr for i in range(len(ws) - 2))


def misura(t, k, voy):
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    pg = e251.pagella_grezza(k['c'], t)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(t), k['rif'])
    tab = e266.tabella(e251.righe_ini(t), k['rif266'])
    d266 = e266.confronto(k['vt266'], tab)
    v3, g3 = trigrammi(voy), trigrammi(t)
    return OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('valori', pg['valori']), ('valori_Voynich', pg['valori_Voynich']),
                        ('estesa', e293.pagella_estesa(t)), ('AUC_e231', d231['AUC']), ('gruppi_e231', d231['AUC_per_gruppo']), ('AUC_e266', d266['AUC']),
                        ('gruppi_e266', d266['AUC_per_gruppo']), ('pesanti_e266', d266['piu_pesanti']), ('pesanti_e231', d231['piu_pesanti']),
                        ('AUC_solo_sacco', e402.solo_sacco(k['vt266'], tab)), ('pannello', e401.pannello(tab)),
                        ('trigrammi_dal_Voynich', sum(n for x, n in g3.items() if x in v3) / max(1, sum(g3.values())))])


def lavoro(args):
    strato, seme, pesi_generato = args
    import e251_lessico_sezione as e251
    import e293_banco as e293
    import pezzi
    k = e251._prepara()
    voy, _ = pezzi.voynich()
    if strato == 'V':
        return (strato, seme), OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(voy))])
    x = configurazione(strato, pesi_generato)
    _, d = pezzi.pezzi()
    t = d.disponi(pezzi.sacco_di(406000 + seme, x), 406500 + seme, 'D3', pesi=x['pesi_disposizione'])
    return (strato, seme), misura(t, k, voy)


def prova():
    import pezzi
    rr, _ = pezzi.voynich()
    s, _ = pezzi.pezzi()
    for posti in ('veri', 'modello'):
        t = pezzi.sacco_di(1, dict(base(), posti=posti))
        assert [(p, ini, len(ps)) for p, ini, ps in t] == [(p, ini, len(ps)) for p, ini, ps in rr]
        nuove = sum(w not in s.conta for _, _, ps in t for w in ps)
        per = Counter()
        tot = Counter()
        for (p, ini, ps) in t:
            for j, w in enumerate(ps):
                c = 'prima di paragrafo' if ini and j == 0 else 'ultima' if j == len(ps) - 1 else 'altro'
                tot[c] += 1
                per[c] += w not in s.conta
        print('posti %s: parole nuove %d (uniche vere %d); quota per posto %s' % (posti, nuove, sum(n == 1 for n in s.conta.values()),
                                                                              {c: round(per[c] / tot[c], 3) for c in tot}))
    r = regola(giri=2, passate=5)
    print('regolazione a posto (due giri): %s' % {k: round(v, 3) for k, v in r['pesi'].items()})


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    reg = regola()
    print('pesi sul sacco generato %s, scarto massimo %.3f, converge %s' % ({k: round(v, 3) for k, v in reg['pesi'].items()}, reg['scarto_massimo'], reg['converge']), flush=True)
    pesi_generato = dict(reg['pesi'])
    lavori = [('V', 0, None)] + [(s, seme, pesi_generato) for s in STRATI for seme in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f solo sacco %.3f | %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'], r['AUC_solo_sacco'],
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
            ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]), ('previste', PREVISTE[s]),
            ('AUC_solo_sacco', media(lambda r: r['AUC_solo_sacco'])),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)), ('materie_mancate', OrderedDict(mancate.most_common())),
            ('valori', OrderedDict((n, media(lambda r: r['valori'][n])) for n in rs[0]['valori'] if all(n in r['valori'] for r in rs))),
            ('valori_Voynich', rs[0]['valori_Voynich']),
            ('estesa', OrderedDict((n, media(lambda r: float(r['estesa'][n]))) for n in e293.FASCE if all(r['estesa'][n] is not None for r in rs))),
            ('pannello', OrderedDict((n, media(lambda r: r['pannello'][n])) for n in rs[0]['pannello'])),
            ('trigrammi_dal_Voynich', media(lambda r: r['trigrammi_dal_Voynich'])),
            ('pesanti_e266', rs[0]['pesanti_e266'][:10]), ('pesanti_e231', rs[0]['pesanti_e231'][:6])])
    scelta = 'P3' if sintesi['P3']['AUC_e266'] <= sintesi['P2']['AUC_e266'] - 0.02 else 'P2'
    parametri = configurazione(scelta, pesi_generato)
    parametri['origine'] = 'e406, strato %s' % scelta
    json.dump(parametri, open(os.path.join(QUI, '..', 'voynichizzatore', 'pezzi_parametri.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    out = OrderedDict([('regolazione', reg), ('Voynich', voy), ('scelta', scelta), ('parametri', parametri), ('sintesi', sintesi),
                       ('per_seme', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e406_generatore_pezzi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['P1']['gruppi'])
    md = ['# e406 — Il generatore intero a pezzi', '',
          'Semi 1–4 (medie). Riferimenti sugli stessi semi: v5 0,812 / 0,918 (pagella 16,5); C5 dell\'e404b 0,711 / 0,813 (14,5); sacco vero ridisposto 0,533 / 0,659 (14,8). '
          'Preregistrazione: `preregistrazioni/e406.md`.', '',
          'Pesi dei legami regolati sul sacco generato (seme %d): %s; scarto massimo %.3f: %s. Pesi dell\'e401b: %s.' % (
              SEME_REGOLAZIONE, ', '.join('%s %.3f' % kv for kv in reg['pesi'].items()), reg['scarto_massimo'], 'converge' if reg['converge'] else '**non converge**',
              ', '.join('%s %.3f' % kv for kv in e402.pesi_e401b().items())), '',
          '| strato | che cosa | AUC e231 (prevista) | AUC e266 (min–max; prevista) | solo sacco | pagella | estese | riga | trigrammi dal Voynich | ' + ' | '.join(gr) + ' |',
          '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f (%.2f–%.2f) | %.3f (%.3f–%.3f; %.2f–%.2f) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %.3f | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['previste'][0][0], x['previste'][0][1], x['AUC_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1],
            x['previste'][1][0], x['previste'][1][1], x['AUC_solo_sacco'], x['pagella_media'], x['estese_media'], x['semi_con_riga'], x['trigrammi_dal_Voynich'],
            ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', 'Configurazione scelta per la v8 secondo la preregistrazione: **%s**.' % scelta, '',
           '## Materie mancate (su 4 semi) e valori grezzi della pagella', '']
    for s, x in sintesi.items():
        md.append('**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'))
        md.append('')
    nomi = [n for n in sintesi['P3']['valori'] if n in sintesi['P3']['valori_Voynich']]
    md += ['| valore grezzo | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4g | %s |' % (n, sintesi['P3']['valori_Voynich'][n], ' | '.join('%.4g' % x['valori'].get(n, float('nan')) for x in sintesi.values())) for n in nomi]
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
    open(os.path.join(RISULTATI, 'e406_generatore_pezzi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(dict({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media']] for s, x in sintesi.items()}, scelta=scelta)))


if __name__ == '__main__':
    main()
