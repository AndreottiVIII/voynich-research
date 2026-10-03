# -*- coding: utf-8 -*-
"""Esperimento 297: errori sparsi nel generatore (le parole frequenti, con probabilita' p, scritte con un segno cambiato in
punti qualsiasi del libro), sopra il corpo dell'e288. Ricerca sui semi 1 e 2, verifica sui semi 7-9.

Preregistrazione: preregistrazioni/e297.md. Scrive risultati/e297_errori_sparsi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import trascrizione
import corpo2
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
P, SEMI_RICERCA, SEMI_VERIFICA, SOGLIA = (0.0, 0.01, 0.02, 0.04, 0.08), (1, 2), (7, 8, 9), 20
_FREQ = {}


def errori(c2, rr, p, seme):
    """Le parole con almeno SOGLIA occorrenze nel Voynich, con probabilita' p, diventano una loro variante di una modifica."""
    if not p:
        return rr
    if not _FREQ:
        _FREQ['f'] = {w for w, n in Counter(c2['voy']).items() if n >= SOGLIA}
    rnd = random.Random(seme * 7919 + 13)
    out = []
    for pag, ini, ps in rr:
        out.append((pag, ini, [e234.forza_variante(w, c2['mod'], rnd, 0.4, c2['att'], c2['D']) if (w in _FREQ['f'] and rnd.random() < p) else w for w in ps]))
    return out


def corpo(k, seme, p):
    e233.SIGMA_POST = 0.04
    rr = e236.dopo(corpo2.genera_v2(k['c2'], dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), seme), k['freq'], 100 + seme)
    return errori(k['c2'], rr, p, seme)


def lavoro(args):
    tipo, p, seme = args
    k = e251._prepara()
    rr = corpo(k, seme, p)
    pg = e251.pagella_grezza(k['c'], rr)
    out = OrderedDict([('p', p), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('R_parole_rare', e251.R_completo(rr, controllo=False)['R']),
                       ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    if tipo == 'verifica':
        out['AUC_e231'] = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']
    return args, out


def tutti(lavori):
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, x in pool.imap_unordered(lavoro, lavori):
            ris[a] = x
            print('%s p %.2f seme %d: pagella %d riga %s mancano %s | R rare %.1f | AUC e266 %.3f%s' % (a[0], a[1], a[2], x['pagella'], x['riga'], x['mancano'],
                  x['R_parole_rare'] or 0, x['AUC_e266'], (' e231 %.3f' % x['AUC_e231']) if 'AUC_e231' in x else ''), flush=True)
    return ris


def main():
    k = e251._prepara()
    e233.SIGMA_POST = 0.04
    base = e236.dopo(corpo2.genera_v2(k['c2'], dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), 1), k['freq'], 101)
    identico = corpo(k, 1, 0.0) == base
    sc = tutti([('scelta', p, s) for p in P for s in SEMI_RICERCA])
    righe = []
    for p in P:
        rs = [sc[('scelta', p, s)] for s in SEMI_RICERCA]
        righe.append(OrderedDict([('p', p), ('pagella', sum(r['pagella'] for r in rs)), ('riga', all(r['riga'] for r in rs)),
                                  ('R', statistics.mean(r['R_parole_rare'] or 99 for r in rs)), ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs))]))
    cand = [r for r in righe if r['riga']] or righe
    scelta = min(cand, key=lambda r: (-r['pagella'], r['R'], r['p']))
    vv = tutti([('verifica', p, s) for s in SEMI_VERIFICA for p in (0.0, scelta['p'])])
    br = {n: [vv[('verifica', p, s)] for s in SEMI_VERIFICA] for n, p in (('e288', 0.0), ('scelta', scelta['p']))}
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('R_media', statistics.mean(x['R_parole_rare'] or 99 for x in xs)), ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in xs)),
                             ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in xs))]) for n, xs in br.items()}
    mb, ms = medie['e288'], medie['scelta']
    utile = ms['R_media'] <= mb['R_media'] / 2 and ms['pagella_somma'] >= mb['pagella_somma'] and ms['semi_con_riga'] >= mb['semi_con_riga']
    esito = 'non valido' if not identico else ('errori utili' if utile else 'non utili') + ('; R ≤ 5' if ms['R_media'] <= 5 else '')
    out = OrderedDict([('validita_identico_e288', identico), ('ricerca', righe), ('p_scelto', scelta['p']), ('verifica', br), ('medie', medie), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e297_errori_sparsi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e297 — Errori sparsi nel generatore', '', 'Corpo dell\'e288 più errori sparsi con probabilità p sulle parole frequenti. Validità (p 0 = e288): %s. '
          'Preregistrazione: `preregistrazioni/e297.md`.' % ('sì' if identico else 'NO'), '', '| p (semi 1–2) | pagella | riga | R parole rare | AUC e266 |', '|---|---|---|---|---|']
    for r in righe:
        md.append('| %.2f | %d | %s | %.1f | %.3f |' % (r['p'], r['pagella'], 'sì' if r['riga'] else 'no', r['R'], r['AUC_e266']))
    md += ['', 'Scelto p %.2f.' % scelta['p'], '', '| seme | braccio | pagella | riga | mancano | R rare | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('e288', 'scelta'):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.1f | %.3f | %.3f |' % (s, n if n == 'e288' else 'p %.2f' % scelta['p'], x['pagella'], 'sì' if x['riga'] else 'no',
                                                                       ', '.join(x['mancano']) or '—', x['R_parole_rare'] or 0, x['AUC_e231'], x['AUC_e266']))
    md += ['', 'Medie: ' + '; '.join('%s pagella %d, riga in %d semi, R %.1f, AUC %.3f / %.3f' % (n, m['pagella_somma'], m['semi_con_riga'], m['R_media'], m['AUC_e231_media'],
                                                                                       m['AUC_e266_media']) for n, m in medie.items()) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e297_errori_sparsi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
