# -*- coding: utf-8 -*-
"""Esperimento 413: tre ritocchi al sacco della v12, con il messaggio nel sacco. S1: le parole nuove fatte di due parole
unite si accettano solo se ben formate (ogni terna di segni vista nelle parole uniche). S2: anche kappa regolata sul sacco
completo (JSD pagina-manoscritto) ed esponente gamma sulla frequenza (quota fra le 100 parole piu' frequenti), regolati sul
pannello (seme 11). Misura: 12 chiavi per strato, Isidoro nascosto, andata e ritorno, giudici, pagelle.

    PROCESSI=9 python esegui.py e413
    python esperimenti/e413_ritocchi_sacco.py --prova     (regolazione breve e un'andata e ritorno, nessun giudice)

Preregistrazione: preregistrazioni/e413.md. Scrive risultati/e413_ritocchi_sacco.json e .md.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e404b_carattere_pagina as e404b
import e406_generatore_pezzi as e406

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
CHIAVI = tuple(range(1, 13))
STRATI = OrderedDict([('S1', 'unioni ben formate'), ('S2', 'S1, kappa sul sacco completo ed esponente sulla frequenza')])
SEME_REGOLAZIONE, GIRI = 11, 10
CANCELLO = ('S1', 'R_riga', 'A', 'scelte_per_riga', 'r_righe_consecutive')
SEGUITE = ('G2 y+o', 'G3 fra le 100 piu frequenti', 'G9 JSD pagina-manoscritto', 'G6 coppie viste altrove', 'G4 inizio ch', 'G3 tipi su parole')


def v12():
    import pezzi
    return json.load(open(pezzi.PARAMETRI % 'v12', encoding='utf-8'), object_pairs_hook=OrderedDict)


def cento(rr):
    """Quota di parole fra le 100 piu' frequenti del testo, media delle pagine con almeno 40 parole (G3 dell'e231)."""
    freq = Counter(w for _, _, ps in rr for w in ps)
    top = {w for w, _ in freq.most_common(100)}
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).extend(ps)
    return statistics.mean(sum(w in top for w in ws) / len(ws) for ws in per.values() if len(ws) >= 40)


def regola(giri=GIRI, stampa=True):
    import pezzi
    voy, _ = pezzi.voynich()
    s, _ = pezzi.pezzi()
    x = v12()
    x['forme'] = OrderedDict(x['forme'], unioni_valide=True)
    b_jsd, b_cento = e404b.jsd_pagina(voy), cento(voy)
    kappa, gamma, traccia, migliore = x['kappa'], 1.0, [], None
    for g in range(giri):
        s.FORME, s.POSIZIONALE, s.GAMMA = dict(x['forme']), False, gamma
        t = s.genera(SEME_REGOLAZIONE, theta=None, nuove='inventate', kappa=kappa, posti='modello')
        jsd, cen = e404b.jsd_pagina(t), cento(t)
        scarto = max(abs(jsd / b_jsd - 1), abs(cen / b_cento - 1) * 3)
        traccia.append(OrderedDict([('giro', g), ('kappa', kappa), ('gamma', gamma), ('JSD', jsd), ('fra le 100', cen), ('scarto', scarto)]))
        if stampa:
            print('giro %2d: kappa %.3f gamma %.3f | JSD %.4f (Voynich %.4f) | fra le 100 %.4f (Voynich %.4f) | scarto %.3f' % (g, kappa, gamma, jsd, b_jsd, cen, b_cento, scarto), flush=True)
        if migliore is None or scarto < migliore[0]:
            migliore = (scarto, kappa, gamma, jsd, cen)
        if scarto < 0.02:
            break
        kappa *= math.exp(1.0 * math.log(b_jsd / jsd))
        gamma = min(1.5, max(0.5, gamma + 0.5 * math.log(b_cento / cen)))
    s.GAMMA = 1.0
    y = OrderedDict(x)
    y['kappa'], y['gamma'] = migliore[1], migliore[2]
    return x, y, OrderedDict([('JSD_Voynich', b_jsd), ('cento_Voynich', b_cento), ('kappa', migliore[1]), ('gamma', migliore[2]), ('JSD', migliore[3]),
                              ('fra le 100', migliore[4]), ('scarto', migliore[0]), ('traccia', traccia)])


def lavoro(args):
    strato, i, x = args
    import e251_lessico_sezione as e251
    import e293_banco as e293
    import e401_disposizione as e401
    import canale_sacco, pezzi
    k = e251._prepara()
    voy, _ = pezzi.voynich()
    if strato == 'V':
        return (strato, i), OrderedDict([('pannello', e401.pannello(k['vt266'])), ('estesa', e293.pagella_estesa(voy))])
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    chiave = 'e409-%d' % i
    t, info = canale_sacco.codifica(testo, chiave, parametri=x, verifica=False)
    r = e406.misura(t, k, voy)
    r['decodifica_esatta'] = canale_sacco.decodifica(t, chiave, parametri=x) == testo
    r['capacita_bit'] = info['capacita_bit']
    tab = __import__('e266_discriminatore_forte').tabella(e251.righe_ini(t), k['rif266'])
    r['seguite'] = OrderedDict((n, float(tab[1][:, tab[2].index(n)].mean())) for n in SEGUITE if n in tab[2])
    return (strato, i), r


def prova():
    import canale_sacco
    x1, x2, reg = regola(giri=2)
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    t, info = canale_sacco.codifica(testo, 'prova', parametri=x2, verifica=False)
    print('andata e ritorno con S2: %s; capacita %d' % (canale_sacco.decodifica(t, 'prova', parametri=x2) == testo, info['capacita_bit']))


def main():
    if '--prova' in sys.argv:
        return prova()
    import e293_banco as e293
    x1, x2, reg = regola()
    print('kappa %.3f, gamma %.3f: JSD %.4f, fra le 100 %.4f, scarto %.3f' % (reg['kappa'], reg['gamma'], reg['JSD'], reg['fra le 100'], reg['scarto']), flush=True)
    par = {'S1': x1, 'S2': x2}
    lavori = [('V', 0, None)] + [(s, i, par[s]) for s in STRATI for i in CHIAVI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, r in pool.imap_unordered(lavoro, lavori):
            ris[a] = r
            if a[0] != 'V':
                print('%s chiave %d: decodifica %s | pagella %d riga %s | AUC e231 %.3f e266 %.3f' % (a[0], a[1], r['decodifica_esatta'], r['pagella'], r['riga'], r['AUC_e231'], r['AUC_e266']), flush=True)
    voy = ris[('V', 0)]
    sintesi = OrderedDict()
    for s in STRATI:
        rs = [ris[(s, i)] for i in CHIAVI]
        for r in rs:
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy['estesa'])]
        media = lambda f: statistics.mean(f(r) for r in rs)
        es = lambda f: statistics.stdev([f(r) for r in rs]) / len(rs) ** 0.5
        mancate = Counter(m for r in rs for m in r['mancano'])
        mancate.update(m for r in rs for m in e293.FASCE if m not in r['estese_passate'])
        sintesi[s] = OrderedDict([
            ('che cosa', STRATI[s]), ('AUC_e231', media(lambda r: r['AUC_e231'])), ('es_e231', es(lambda r: r['AUC_e231'])),
            ('AUC_e266', media(lambda r: r['AUC_e266'])), ('es_e266', es(lambda r: r['AUC_e266'])),
            ('AUC_e266_min_max', [min(r['AUC_e266'] for r in rs), max(r['AUC_e266'] for r in rs)]),
            ('gruppi', OrderedDict((n, media(lambda r: r['gruppi_e266'][n])) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)),
            ('pagella_media', media(lambda r: r['pagella'])), ('estese_media', media(lambda r: len(r['estese_passate']))),
            ('chiavi_con_riga', sum(bool(r['riga']) for r in rs)), ('decodifica_esatta', sum(bool(r['decodifica_esatta']) for r in rs)),
            ('capacita_bit', media(lambda r: r['capacita_bit'])), ('materie_mancate', OrderedDict(mancate.most_common())),
            ('seguite', OrderedDict((n, media(lambda r: r['seguite'][n])) for n in rs[0]['seguite']))])
    out = OrderedDict([('regolazione', reg), ('parametri', par), ('Voynich', voy), ('sintesi', sintesi),
                       ('per_chiave', OrderedDict(('%s|%d' % a, ris[a]) for a in ris if a[0] != 'V'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e413_ritocchi_sacco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    gr = list(sintesi['S1']['gruppi'])
    md = ['# e413 — Tre ritocchi al sacco della v12', '',
          'Isidoro XVII nascosto nel sacco, 12 chiavi per strato (medie ± errore standard). Riferimento, v12 sulle stesse chiavi: 0,576 ± 0,007 / 0,619 ± 0,009, '
          'pagella 15,0, cancello 11 su 12; gruppi G3 0,65, G8 0,67. Preregistrazione: `preregistrazioni/e413.md`.', '',
          'Regolazione di S2 sul pannello: κ = %.3f, γ = %.3f; JSD pagina-manoscritto %.4f (Voynich %.4f); fra le 100 più frequenti %.4f (Voynich %.4f).' % (
              reg['kappa'], reg['gamma'], reg['JSD'], reg['JSD_Voynich'], reg['fra le 100'], reg['cento_Voynich']), '',
          '| strato | che cosa | AUC e231 | AUC e266 (min – max) | pagella | estese | cancello | decodifica | capacità | ' + ' | '.join(gr) + ' |',
          '|---|---|---|---|---|---|---|---|---|' + '---|' * len(gr)]
    for s, x in sintesi.items():
        md.append('| %s | %s | %.3f ± %.3f | %.3f ± %.3f (%.3f – %.3f) | %.1f/18 | %.1f/8 | %d/12 | %d/12 | %.0f | %s |' % (
            s, x['che cosa'], x['AUC_e231'], x['es_e231'], x['AUC_e266'], x['es_e266'], x['AUC_e266_min_max'][0], x['AUC_e266_min_max'][1], x['pagella_media'],
            x['estese_media'], x['chiavi_con_riga'], x['decodifica_esatta'], x['capacita_bit'], ' | '.join('%.2f' % z for z in x['gruppi'].values())))
    md += ['', '| caratteristica seguita | Voynich | ' + ' | '.join(sintesi) + ' |', '|---|---|' + '---|' * len(sintesi)]
    md += ['| %s | %.4f | %s |' % (n, voy['pannello'].get(n, float('nan')), ' | '.join('%.4f' % x['seguite'][n] for x in sintesi.values())) for n in sintesi['S1']['seguite']]
    md += ['', '## Materie mancate (su 12 chiavi)', '']
    for s, x in sintesi.items():
        md += ['**%s.** %s.' % (s, ', '.join('%s (%d)' % kv for kv in x['materie_mancate'].items()) or 'nessuna'), '']
    open(os.path.join(RISULTATI, 'e413_ritocchi_sacco.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({s: [round(x['AUC_e231'], 3), round(x['AUC_e266'], 3), x['pagella_media'], x['chiavi_con_riga']] for s, x in sintesi.items()}))


if __name__ == '__main__':
    main()
