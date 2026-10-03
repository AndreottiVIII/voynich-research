# -*- coding: utf-8 -*-
"""Esperimento 283: ricerca casuale congiunta (96 + e241, poi 24 di affinamento) su tredici parametri del generatore e241,
obiettivo l'AUC dell'e266 sul seme 1 con un vincolo di pagella; verifica della scelta e dell'e241 sui semi 7, 8, 9.

Preregistrazione: preregistrazioni/e283.md. Scrive risultati/e283_regolazione_casuale.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
CASUALI, AFFINAMENTO, SEME_RICERCA, SEMI_VERIFICA = 96, 24, 1, (7, 8, 9)
CONTINUI = OrderedDict([('alfa', (0.8, 1.4)), ('kappa', (0.0, 2.0)), ('chi', (0.0, 0.4)), ('nu', (0.3, 0.7)), ('lam', (0.6, 2.0)),
                        ('eta', (0.0, 2.0)), ('gamma', (0.0, 0.6)), ('delta', (0.0, 0.4)), ('psi', (0.0, 0.06)), ('phi', (0.0, 0.3)),
                        ('sigma_post', (0.03, 0.15)), ('pi_post', (0.15, 0.45))])
K = (4, 8, 12, 16)
E241 = OrderedDict([('alfa', 1.0), ('kappa', 1.0), ('chi', 0.2), ('nu', 0.4), ('lam', 1.0), ('eta', 1.0), ('gamma', 0.0), ('delta', 0.0),
                    ('psi', 0.0), ('phi', 0.0), ('sigma_post', 0.09), ('pi_post', 0.30), ('k', 8)])


def prm_di(x):
    """Dai parametri della ricerca a quelli di e233.genera (fisica solo se phi > 0)."""
    p = dict(e224.BASE, alfa=x['alfa'], kappa=x['kappa'], chi=x['chi'], nu=x['nu'], lam_k=(x['lam'], x['k']), eta=x['eta'],
             gamma=x['gamma'], delta=x['delta'], psi=x['psi'], phi=x['phi'])
    if x['phi'] > 0:
        p['fisica'] = True
    return p


def lavoro(args):
    nome, x, seme, completa = args
    k = e251._prepara()
    e233.SIGMA_POST, e233.PI_POST = x['sigma_post'], x['pi_post']
    rr = e236.dopo(e233.genera(k['c2'], prm_di(x), seme), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(k['c'], rr)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])
    out = OrderedDict([('nome', nome), ('seme', seme), ('parametri', x), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('AUC_e231', d231['AUC']), ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    if completa:
        out['piu_pesanti_e231'] = d231['piu_pesanti']
    return out


def tutti(lavori):
    n = int(os.environ.get('PROCESSI', '1'))
    if n <= 1:
        return [lavoro(a) for a in lavori]
    with Pool(n) as pool:
        return list(pool.imap(lavoro, lavori))


def estrai(rnd):
    x = OrderedDict((p, rnd.uniform(a, b)) for p, (a, b) in CONTINUI.items())
    x['k'] = rnd.choice(K)
    return x


def vicino(x, rnd):
    y = OrderedDict()
    for p, (a, b) in CONTINUI.items():
        y[p] = min(b, max(a, x[p] + rnd.uniform(-0.15, 0.15) * (b - a)))
    i = K.index(x['k']) + rnd.choice((-1, 0, 1))
    y['k'] = K[min(len(K) - 1, max(0, i))]
    return y


def main():
    rnd = random.Random('e283')
    confs = [('e241', E241)] + [('c%03d' % i, estrai(rnd)) for i in range(1, CASUALI + 1)]
    ris = tutti([(n, x, SEME_RICERCA, False) for n, x in confs])
    base1 = ris[0]
    ammessa = lambda r: r['pagella'] >= base1['pagella'] - 1 and (r['riga'] or not base1['riga'])
    for r in ris:
        print('%s: pagella %d riga %s | AUC e266 %.3f e231 %.3f' % (r['nome'], r['pagella'], r['riga'], r['AUC_e266'], r['AUC_e231']), flush=True)
    migliore = min([r for r in ris if ammessa(r)], key=lambda r: (r['AUC_e266'], r['nome']))
    rnd2 = random.Random('e283-affinamento')
    aff = tutti([('a%03d' % i, vicino(migliore['parametri'], rnd2), SEME_RICERCA, False) for i in range(1, AFFINAMENTO + 1)])
    for r in aff:
        print('%s: pagella %d riga %s | AUC e266 %.3f e231 %.3f' % (r['nome'], r['pagella'], r['riga'], r['AUC_e266'], r['AUC_e231']), flush=True)
    tutte = ris + aff
    scelta = min([r for r in tutte if ammessa(r)], key=lambda r: (r['AUC_e266'], r['nome']))
    print('scelta %s: AUC e266 %.3f (e241 %.3f) | %s' % (scelta['nome'], scelta['AUC_e266'], base1['AUC_e266'], dict(scelta['parametri'])), flush=True)
    ver = tutti([(n, x, s, True) for s in SEMI_VERIFICA for n, x in (('e241', E241), (scelta['nome'], scelta['parametri']))])
    vb = [v for v in ver if v['nome'] == 'e241']
    vs = [v for v in ver if v['nome'] != 'e241']
    for v in ver:
        print('verifica seme %d %s: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f' % (
            v['seme'], v['nome'], v['pagella'], v['riga'], v['mancano'], v['AUC_e231'], v['AUC_e266']), flush=True)
    m = lambda vv, k: statistics.mean(v[k] for v in vv)
    medie = OrderedDict([(n, OrderedDict([('pagella_somma', sum(v['pagella'] for v in vv)), ('semi_con_riga', sum(bool(v['riga']) for v in vv)),
                                          ('AUC_e231_media', m(vv, 'AUC_e231')), ('AUC_e266_media', m(vv, 'AUC_e266'))])) for n, vv in (('e241', vb), ('scelta', vs))])
    mb, ms = medie['e241'], medie['scelta']
    migliore_v = (ms['AUC_e266_media'] <= mb['AUC_e266_media'] - 0.03 and ms['pagella_somma'] >= mb['pagella_somma'] and ms['semi_con_riga'] >= mb['semi_con_riga'])
    esito = ('indistinguibile' if ms['AUC_e231_media'] <= 0.6 else 'migliore') if migliore_v else 'non migliore'
    # correlazioni parametro -> AUC e266 sul seme 1 (tutte le configurazioni)
    corr = OrderedDict()
    ys = [r['AUC_e266'] for r in tutte]
    for p in list(CONTINUI) + ['k']:
        xs = [r['parametri'][p] for r in tutte]
        corr[p] = statistics.correlation(xs, ys) if len(set(xs)) > 1 else None
    out = OrderedDict([('seme_1', tutte), ('scelta', scelta['nome']), ('parametri_scelti', scelta['parametri']), ('verifica', ver), ('medie', medie),
                       ('correlazioni_AUC_e266', corr), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e283_regolazione_casuale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e283 — Regolazione congiunta preliminare: ricerca casuale sui parametri dell\'e241', '',
          '96 configurazioni casuali più l\'e241 e 24 di affinamento sul seme 1 (obiettivo AUC dell\'e266, pagella non oltre 1 sotto l\'e241); '
          'verifica sui semi 7, 8, 9. Preregistrazione: `preregistrazioni/e283.md`.', '',
          'e241 sul seme 1: pagella %d, riga %s, AUC e266 %.3f, e231 %.3f. Scelta: **%s**, AUC e266 %.3f, e231 %.3f, pagella %d.' % (
              base1['pagella'], 'sì' if base1['riga'] else 'no', base1['AUC_e266'], base1['AUC_e231'], scelta['nome'], scelta['AUC_e266'], scelta['AUC_e231'], scelta['pagella']), '',
          'Parametri scelti: ' + ', '.join('%s %s' % (p, ('%.3f' % v) if isinstance(v, float) else v) for p, v in scelta['parametri'].items()) + '.', '',
          '| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|']
    for v in ver:
        md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f |' % (v['seme'], v['nome'], v['pagella'], 'sì' if v['riga'] else 'no', ', '.join(v['mancano']) or '—', v['AUC_e231'], v['AUC_e266']))
    md += ['', 'Medie: e241 pagella %d (somma), riga in %d semi, AUC %.3f / %.3f; scelta pagella %d, riga in %d semi, AUC %.3f / %.3f.' % (
        mb['pagella_somma'], mb['semi_con_riga'], mb['AUC_e231_media'], mb['AUC_e266_media'], ms['pagella_somma'], ms['semi_con_riga'], ms['AUC_e231_media'], ms['AUC_e266_media']),
           '', 'Correlazione fra parametro e AUC dell\'e266 sul seme 1 (negativa = alzarlo aiuta): ' + ', '.join(
               '%s %s' % (p, '%+.2f' % c if c is not None else '—') for p, c in corr.items()) + '.', '',
           'Le 10 migliori sul seme 1:', '', '| config. | pagella | riga | AUC e266 | AUC e231 |', '|---|---|---|---|---|']
    for r in sorted(tutte, key=lambda r: r['AUC_e266'])[:10]:
        md.append('| %s | %d | %s | %.3f | %.3f |' % (r['nome'], r['pagella'], 'sì' if r['riga'] else 'no', r['AUC_e266'], r['AUC_e231']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e283_regolazione_casuale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
