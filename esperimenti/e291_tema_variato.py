# -*- coding: utf-8 -*-
"""Esperimento 291: il tema variato (tau, voynichizzatore/corpo3.genera_v3) sopra la configurazione dell'e288, con rip e phi
attorno ai valori dell'e288; ricerca sui semi 1 e 2 (pagella, poi AUC dell'e266), verifica sui semi 7-9 contro l'e288.
Stampa ogni risultato appena arriva.

Preregistrazione: preregistrazioni/e291.md. Scrive risultati/e291_tema_variato.json e .md.
"""
import itertools, json, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import corpo2, corpo3
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRIGLIA = [OrderedDict([('tau', t), ('rip', r), ('phi', f)]) for t, r, f in itertools.product((0.0, 0.5, 1.0), (0.4, 0.5, 0.6), (0.10, 0.15))]
E288 = OrderedDict([('tau', 0.0), ('rip', 0.5), ('phi', 0.10)])
SIGMA_POST, SEMI_RICERCA, SEMI_VERIFICA = 0.04, (1, 2), (7, 8, 9)


def nome(x):
    return 'tau %.1f, rip %.1f, phi %.2f' % (x['tau'], x['rip'], x['phi'])


def prm_di(x):
    return dict(e251.CONF, gamma=0.0, tau=x['tau'], rip=x['rip'], phi=x['phi'])


def lavoro(args):
    tipo, x, seme = args
    k = e251._prepara()
    e233.SIGMA_POST = SIGMA_POST
    rr = e236.dopo(corpo3.genera_v3(k['c2'], prm_di(x), seme), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(k['c'], rr)
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    out = OrderedDict([('configurazione', nome(x)), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('AUC_e266', d266['AUC']), ('G3', d266['AUC_per_gruppo']['G3']), ('G6', d266['AUC_per_gruppo']['G6'])])
    if tipo == 'verifica':
        out['AUC_e231'] = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']
        out['gruppi_e266'] = d266['AUC_per_gruppo']
    return args[:1] + (nome(x), seme), out


def tutti(lavori):
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, x in pool.imap_unordered(lavoro, lavori):
            ris[a] = x
            print('%s %-28s seme %d: pagella %d riga %s mancano %s | AUC e266 %.3f G3 %.3f G6 %.3f%s' % (
                a[0], a[1], a[2], x['pagella'], x['riga'], x['mancano'], x['AUC_e266'], x['G3'], x['G6'],
                (' | e231 %.3f' % x['AUC_e231']) if 'AUC_e231' in x else ''), flush=True)
    return ris


def main():
    k = e251._prepara()
    e233.SIGMA_POST = SIGMA_POST
    identico = corpo3.genera_v3(k['c2'], prm_di(E288), 1) == corpo2.genera_v2(k['c2'], dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), 1)
    print("tau 0 identico a corpo2 (e288): %s" % identico, flush=True)
    sc = tutti([('scelta', x, s) for x in GRIGLIA for s in SEMI_RICERCA])
    righe = []
    for x in GRIGLIA:
        rs = [sc[('scelta', nome(x), s)] for s in SEMI_RICERCA]
        righe.append(OrderedDict([('configurazione', nome(x)), ('parametri', x), ('pagella', sum(r['pagella'] for r in rs)), ('riga', all(r['riga'] for r in rs)),
                                  ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs)), ('G3', statistics.mean(r['G3'] for r in rs)),
                                  ('G6', statistics.mean(r['G6'] for r in rs))]))
    cand = [r for r in righe if r['riga']] or righe
    scelta = min(cand, key=lambda r: (-r['pagella'], r['AUC_e266'], righe.index(r)))
    print('scelta: %s (pagella %d, AUC e266 %.3f)' % (scelta['configurazione'], scelta['pagella'], scelta['AUC_e266']), flush=True)
    vv = tutti([('verifica', x, s) for s in SEMI_VERIFICA for x in (E288, scelta['parametri'])])
    br = {'e288': [vv[('verifica', nome(E288), s)] for s in SEMI_VERIFICA], 'scelta': [vv[('verifica', scelta['configurazione'], s)] for s in SEMI_VERIFICA]}
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in xs)), ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in xs)),
                             ('G3', statistics.mean(x['G3'] for x in xs)), ('G6', statistics.mean(x['G6'] for x in xs))]) for n, xs in br.items()}
    mb, ms = medie['e288'], medie['scelta']
    migliore = ms['AUC_e266_media'] <= mb['AUC_e266_media'] - 0.02 and ms['pagella_somma'] >= mb['pagella_somma'] and ms['semi_con_riga'] >= mb['semi_con_riga']
    esito = 'non valido' if not identico else ('migliore dell\'e288' if migliore else 'non migliore')
    out = OrderedDict([('validita_identico', identico), ('ricerca', righe), ('scelta', scelta['configurazione']), ('parametri_scelti', scelta['parametri']),
                       ('verifica', br), ('medie', medie), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e291_tema_variato.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e291 — Il tema variato sopra l\'e288', '', 'Validità (τ 0 = corpo dell\'e288): %s. Preregistrazione: `preregistrazioni/e291.md`.' % ('sì' if identico else 'NO'), '',
          '| configurazione (semi 1–2) | pagella | riga | AUC e266 | G3 | G6 |', '|---|---|---|---|---|---|']
    for r in sorted(righe, key=lambda r: (-r['pagella'], r['AUC_e266'])):
        md.append('| %s | %d | %s | %.3f | %.3f | %.3f |' % (r['configurazione'], r['pagella'], 'sì' if r['riga'] else 'no', r['AUC_e266'], r['G3'], r['G6']))
    md += ['', 'Scelta: **%s**.' % scelta['configurazione'], '', '| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 | G3 | G6 |', '|---|---|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('e288', 'scelta'):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f | %.3f | %.3f |' % (s, x['configurazione'], x['pagella'], 'sì' if x['riga'] else 'no', ', '.join(x['mancano']) or '—',
                                                                         x['AUC_e231'], x['AUC_e266'], x['G3'], x['G6']))
    md += ['', 'Medie: ' + '; '.join('%s pagella %d, riga in %d semi, AUC %.3f / %.3f, G3 %.3f, G6 %.3f' % (n, m['pagella_somma'], m['semi_con_riga'], m['AUC_e231_media'],
                                                                                                     m['AUC_e266_media'], m['G3'], m['G6']) for n, m in medie.items()) + '.',
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e291_tema_variato.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
