# -*- coding: utf-8 -*-
"""Esperimento 409: il messaggio nel sacco (voynichizzatore/canale_sacco.py). Con quattro chiavi: (a) Isidoro XVII nascosto
nei conteggi delle parole note; (b) lo stesso canale con soli bit di riempimento; (c) il corpo della versione di partenza
con il nascondiglio vecchio (scelte di grafia riscritte). Andata e ritorno, chiave sbagliata, capacita', giudici, pagella
con il cancello della riga, pagella estesa.

    PROCESSI=10 python esegui.py e409
    VERSIONE=v9 (predefinita) sceglie il corpo di partenza.

Preregistrazione: preregistrazioni/e409.md. Scrive risultati/e409_messaggio_nel_sacco.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
VERSIONE = os.environ.get('VERSIONE', 'v9')
CHIAVI = (1, 2, 3, 4)
CASI = OrderedDict([('a', 'messaggio nel sacco'), ('b', 'stesso canale, soli bit di riempimento'), ('c', 'nascondiglio vecchio sul corpo della versione di partenza')])


def lavoro(args):
    caso, i = args
    import e251_lessico_sezione as e251
    import e293_banco as e293
    import e401_disposizione as e401
    import canale_sacco, pezzi, versioni
    k = e251._prepara()
    voy, _ = pezzi.voynich()
    if caso == 'V':
        return args, OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(voy)),
                                  ('tipi su parole', e404.tipi_su_parole(voy)), ('JSD', e404b.jsd_pagina(voy))])
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    chiave = 'e409-%d' % i
    extra = OrderedDict()
    if caso == 'a':
        t, info = canale_sacco.codifica(testo, chiave, VERSIONE, verifica=False)
        extra['decodifica_esatta'] = canale_sacco.decodifica(t, chiave, VERSIONE) == testo
        try:
            extra['chiave_sbagliata_respinta'] = canale_sacco.decodifica(t, chiave + 'x', VERSIONE) != testo
        except Exception:
            extra['chiave_sbagliata_respinta'] = True
        extra.update(info)
    elif caso == 'b':
        t, info = canale_sacco.codifica(None, chiave, VERSIONE)
        extra['capacita_bit'] = info['capacita_bit']
    else:
        v1 = versioni.canale('v3')
        t, _ = v1.codifica(testo, chiave, righe=versioni.corpo(versioni.VERSIONI[VERSIONE]['corpo'], 409 + i))
        extra['decodifica_esatta'] = v1.decodifica(t, chiave) == testo
    r = e406.misura(t, k, voy)
    r.update(extra)
    r['tipi su parole'], r['JSD'] = e404.tipi_su_parole(t), e404b.jsd_pagina(t)
    return args, r


def main():
    import e293_banco as e293
    lavori = [('V', 0)] + [(c, i) for c in CASI for i in CHIAVI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%s chiave %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | %s' % (
                    a[0], a[1], r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                    {n: r[n] for n in ('decodifica_esatta', 'chiave_sbagliata_respinta', 'capacita_bit', 'bit_messaggio', 'pagine_usate') if n in r}), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for c in CASI:
        rs = [ris[(c, i)] for i in CHIAVI]
        for r in rs:
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
        media = lambda f: statistics.mean(f(r) for r in rs)
        mancate = Counter(m for r in rs for m in r['mancano'])
        mancate.update(m for r in rs for m in e293.FASCE if m not in r['estese_passate'])
        x = OrderedDict([
            ('che cosa', CASI[c]), ('AUC_e231', media(lambda r: r['AUC_e231'])), ('AUC_e266', media(lambda r: r['AUC_e266'])),
            ('AUC_e231_per_chiave', [r['AUC_e231'] for r in rs]), ('AUC_e266_per_chiave', [r['AUC_e266'] for r in rs]),
            ('AUC_solo_sacco', media(lambda r: r['AUC_solo_sacco'])),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('semi_con_riga', sum(bool(r['riga']) for r in rs)), ('materie_mancate', OrderedDict(mancate.most_common())),
            ('tipi su parole', media(lambda r: r['tipi su parole'])), ('JSD', media(lambda r: r['JSD'])),
            ('cancello', OrderedDict((n, media(lambda r: r['valori'][n])) for n in ('S1', 'R_riga', 'A', 'scelte_per_riga', 'r_righe_consecutive')
                                     if all(r['valori'].get(n) is not None for r in rs))),
            ('pesanti_e266', rs[0]['pesanti_e266'][:8])])
        if c != 'b':
            x['decodifica_esatta'] = sum(bool(r['decodifica_esatta']) for r in rs)
        if c == 'a':
            x['chiave_sbagliata_respinta'] = sum(bool(r['chiave_sbagliata_respinta']) for r in rs)
            x['capacita_bit'] = media(lambda r: r['capacita_bit'])
            x['bit_messaggio'] = rs[0]['bit_messaggio']
            x['pagine_usate'] = media(lambda r: r['pagine_usate'])
        if c == 'b':
            x['capacita_bit'] = media(lambda r: r['capacita_bit'])
        sintesi[c] = x
    out = OrderedDict([('versione', VERSIONE), ('Voynich', voy), ('sintesi', sintesi), ('per_chiave', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e409_messaggio_nel_sacco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['a']['gruppi'])
    a = sintesi['a']
    md = ['# e409 — Il messaggio nel sacco', '',
          'Corpo di partenza: %s. Isidoro XVII (%d bit dopo compressione e cifratura), quattro chiavi. Preregistrazione: `preregistrazioni/e409.md`.' % (VERSIONE, a['bit_messaggio']), '',
          '- Andata e ritorno esatta: %d su 4; chiave sbagliata respinta: %d su 4.' % (a['decodifica_esatta'], a['chiave_sbagliata_respinta']),
          '- Capacità del libro: %.0f bit con il messaggio, %.0f con soli bit di riempimento (servono %d); pagine usate dal messaggio %.0f su 207.' % (
              a['capacita_bit'], sintesi['b']['capacita_bit'], a['bit_messaggio'], a['pagine_usate']),
          '- Nascondiglio vecchio (c): decodifica esatta %d su 4.' % sintesi['c']['decodifica_esatta'], '',
          '| caso | che cosa | AUC e231 (per chiave) | AUC e266 (per chiave) | solo sacco | pagella | estese | riga | tipi su parole (Voynich %.4f) | JSD (Voynich %.4f) | %s |' % (
              voy['tipi su parole'], voy['JSD'], ' | '.join(gr)), '|---|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for c, x in sintesi.items():
        md.append('| %s | %s | %.3f (%s) | %.3f (%s) | %.3f | %.1f/18 | %.1f/8 | %d/4 | %.4f | %.4f | %s |' % (
            c, x['che cosa'], x['AUC_e231'], ', '.join('%.3f' % v for v in x['AUC_e231_per_chiave']), x['AUC_e266'], ', '.join('%.3f' % v for v in x['AUC_e266_per_chiave']),
            x['AUC_solo_sacco'], x['pagella_media'], x['estese_media'], x['semi_con_riga'], x['tipi su parole'], x['JSD'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', 'Cancello della riga (soglie: S1 ≤ 0,7; R_riga < 0,1; A ≥ 1,0; scelte per riga ≥ 3; r fra righe consecutive entro 0,07 da 0,207):', '',
           '| caso | ' + ' | '.join(a['cancello']) + ' |', '|---|' + '---|' * len(a['cancello'])]
    md += ['| %s | %s |' % (c, ' | '.join('%.3f' % x['cancello'].get(n, float('nan')) for n in a['cancello'])) for c, x in sintesi.items()]
    md += ['', '## Materie mancate (su 4 chiavi)', '']
    for c, x in sintesi.items():
        md += ['**%s.** %s.' % (c, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    md += ['## Caratteristiche più pesanti (giudice e266, prima chiave)', '']
    for c, x in sintesi.items():
        md += ['**%s**' % c, '', '| caratteristica | coefficiente | Voynich | testo |', '|---|---|---|---|']
        md += ['| %s | %+.2f | %.4f | %.4f |' % tuple(z) for z in x['pesanti_e266']]
        md.append('')
    open(os.path.join(RISULTATI, 'e409_messaggio_nel_sacco.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({c: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media']] for c, x in sintesi.items()}))


if __name__ == '__main__':
    main()
