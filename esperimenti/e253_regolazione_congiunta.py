# -*- coding: utf-8 -*-
"""Esperimento 253 (passo 4 del piano 18/18): ricerca casuale e affinamento su 19 parametri del corpo con tutti i meccanismi
(voynichizzatore/corpo.genera_tutto), obiettivo l'AUC dell'e266 sul seme 1 a pagella non inferiore all'e241; verifica sui
semi 7, 8, 9. Stampa ogni risultato appena arriva.

Preregistrazione: preregistrazioni/e253.md. Scrive risultati/e253_regolazione_congiunta.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import corpo
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266
import e268_prime_righe as e268

RISULTATI = os.path.join(QUI, '..', 'risultati')
CASUALI, AFFINAMENTO, SEME_RICERCA, SEMI_VERIFICA = 128, 32, 1, (7, 8, 9)
CONTINUI = OrderedDict([('alfa', (0.8, 1.4)), ('kappa', (0.0, 2.0)), ('chi', (0.0, 0.4)), ('nu', (0.3, 0.7)), ('lam', (0.6, 2.0)), ('eta', (0.0, 2.0)),
                        ('gamma', (0.0, 0.3)), ('delta', (0.0, 0.3)), ('psi', (0.0, 0.06)), ('sigma_post', (0.03, 0.15)), ('pi_post', (0.15, 0.45)),
                        ('phi', (0.0, 0.2)), ('theta', (0.0, 0.4)), ('rho', (0.0, 0.5)), ('rip', (0.2, 1.0))])
DISCRETI = OrderedDict([('k', (4, 8, 12, 16)), ('k_tema', (1, 3, 6, 12)), ('mazzo', (False, True)), ('inter', (False, True))])
E241 = OrderedDict([('alfa', 1.0), ('kappa', 1.0), ('chi', 0.2), ('nu', 0.4), ('lam', 1.0), ('eta', 1.0), ('gamma', 0.0), ('delta', 0.0), ('psi', 0.0),
                    ('sigma_post', 0.09), ('pi_post', 0.30), ('phi', 0.0), ('theta', 0.3), ('rho', 0.0), ('rip', 1.0),
                    ('k', 8), ('k_tema', 3), ('mazzo', False), ('inter', False)])
_INT = {}


def interruttori():
    if not _INT:
        classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
        _INT['x'] = e251.interruttori_voynich(classi)
    return _INT['x']


def prm_di(x):
    return dict(e224.BASE, alfa=x['alfa'], kappa=x['kappa'], chi=x['chi'], nu=x['nu'], lam_k=(x['lam'], x['k']), eta=x['eta'], gamma=x['gamma'],
                delta=x['delta'], psi=x['psi'], phi=x['phi'], theta=x['theta'], k_tema=x['k_tema'], mazzo=x['mazzo'], rho=x['rho'], rip=x['rip'])


def genera(k, x, seme):
    e233.SIGMA_POST, e233.PI_POST = x['sigma_post'], x['pi_post']
    grezzo = corpo.genera_tutto(k['c2'], prm_di(x), seme, inter=interruttori() if x['inter'] else None,
                                prime_per_pag=e268.prime_per_pagina(k['c']) if x['rho'] else None)
    return e236.dopo(grezzo, k['freq'], 100 + seme)


def lavoro(args):
    nome, x, seme, completa = args
    k = e251._prepara()
    rr = genera(k, x, seme)
    pg = e251.pagella_grezza(k['c'], rr)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])
    out = OrderedDict([('nome', nome), ('seme', seme), ('parametri', x), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('AUC_e231', d231['AUC']), ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    if completa:
        out['piu_pesanti_e231'] = d231['piu_pesanti']
    return out


def tutti(lavori):
    ris = []
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for r in pool.imap(lavoro, lavori):
            ris.append(r)
            print('%s seme %d: pagella %d riga %s | AUC e266 %.3f e231 %.3f' % (r['nome'], r['seme'], r['pagella'], r['riga'], r['AUC_e266'], r['AUC_e231']), flush=True)
    return ris


def estrai(rnd):
    x = OrderedDict((p, rnd.uniform(a, b)) for p, (a, b) in CONTINUI.items())
    for p, vals in DISCRETI.items():
        x[p] = rnd.choice(vals)
    return x


def vicino(x, rnd):
    y = OrderedDict((p, min(b, max(a, x[p] + rnd.uniform(-0.15, 0.15) * (b - a)))) for p, (a, b) in CONTINUI.items())
    for p, vals in DISCRETI.items():
        y[p] = rnd.choice(vals) if rnd.random() < 0.2 else x[p]
    return y


def main():
    rnd = random.Random('e253')
    ris = tutti([('e241', E241, SEME_RICERCA, False)] + [('c%03d' % i, estrai(rnd), SEME_RICERCA, False) for i in range(1, CASUALI + 1)])
    base1 = ris[0]
    ammessa = lambda r: r['pagella'] >= base1['pagella'] and r['riga']
    amm = [r for r in ris if ammessa(r)]
    migliore = min(amm, key=lambda r: (r['AUC_e266'], r['nome']))
    rnd2 = random.Random('e253-affinamento')
    aff = tutti([('a%03d' % i, vicino(migliore['parametri'], rnd2), SEME_RICERCA, False) for i in range(1, AFFINAMENTO + 1)])
    tutte = ris + aff
    scelta = min([r for r in tutte if ammessa(r)], key=lambda r: (r['AUC_e266'], r['nome']))
    print('scelta %s: AUC e266 %.3f (e241 %.3f) | %s' % (scelta['nome'], scelta['AUC_e266'], base1['AUC_e266'], dict(scelta['parametri'])), flush=True)
    json.dump(scelta['parametri'], open(os.path.join(RISULTATI, 'e253_parametri_scelti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ver = tutti([(n, x, s, True) for s in SEMI_VERIFICA for n, x in (('e241', E241), (scelta['nome'], scelta['parametri']))])
    vb, vs = [v for v in ver if v['nome'] == 'e241'], [v for v in ver if v['nome'] != 'e241']
    m = lambda vv, kk: statistics.mean(v[kk] for v in vv)
    medie = OrderedDict([(n, OrderedDict([('pagella_somma', sum(v['pagella'] for v in vv)), ('semi_con_riga', sum(bool(v['riga']) for v in vv)),
                                          ('AUC_e231_media', m(vv, 'AUC_e231')), ('AUC_e266_media', m(vv, 'AUC_e266')),
                                          ('mancano', dict(Counter(x for v in vv for x in v['mancano'])))])) for n, vv in (('e241', vb), ('scelta', vs))])
    mb, ms = medie['e241'], medie['scelta']
    pieno = all(v['pagella'] == 18 and v['riga'] for v in vs)
    migliore_v = ms['AUC_e266_media'] <= mb['AUC_e266_media'] - 0.05 and ms['pagella_somma'] >= mb['pagella_somma'] and ms['semi_con_riga'] >= mb['semi_con_riga']
    esito = 'passo superato (18/18)' + (' e migliore' if migliore_v else '') if pieno else ('migliore' if migliore_v else 'non migliore')
    corr = OrderedDict()
    ys = [r['AUC_e266'] for r in tutte]
    for p in list(CONTINUI) + list(DISCRETI):
        xs = [float(r['parametri'][p]) for r in tutte]
        corr[p] = statistics.correlation(xs, ys) if len(set(xs)) > 1 else None
    out = OrderedDict([('seme_1', tutte), ('scelta', scelta['nome']), ('parametri_scelti', scelta['parametri']), ('verifica', ver), ('medie', medie),
                       ('correlazioni_AUC_e266', corr), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e253_regolazione_congiunta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e253 — Passo 4 del piano 18/18: regolazione congiunta con tutti i meccanismi', '',
          '128 configurazioni casuali più l\'e241 e 32 di affinamento sul seme 1 (obiettivo AUC dell\'e266, pagella non inferiore all\'e241 e riga); verifica sui '
          'semi 7, 8, 9. Preregistrazione: `preregistrazioni/e253.md`.', '',
          'e241 sul seme 1: pagella %d, AUC e266 %.3f. Scelta **%s**: pagella %d, AUC e266 %.3f, e231 %.3f.' % (
              base1['pagella'], base1['AUC_e266'], scelta['nome'], scelta['pagella'], scelta['AUC_e266'], scelta['AUC_e231']), '',
          'Parametri scelti: ' + ', '.join('%s %s' % (p, ('%.3f' % v) if isinstance(v, float) else v) for p, v in scelta['parametri'].items()) + '.', '',
          '| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|']
    for v in ver:
        md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f |' % (v['seme'], v['nome'], v['pagella'], 'sì' if v['riga'] else 'no', ', '.join(v['mancano']) or '—', v['AUC_e231'], v['AUC_e266']))
    md += ['', 'Medie: e241 pagella %d, riga in %d semi, AUC %.3f / %.3f; scelta pagella %d, riga in %d semi, AUC %.3f / %.3f.' % (
        mb['pagella_somma'], mb['semi_con_riga'], mb['AUC_e231_media'], mb['AUC_e266_media'], ms['pagella_somma'], ms['semi_con_riga'], ms['AUC_e231_media'], ms['AUC_e266_media']),
           '', 'Correlazione fra parametro e AUC dell\'e266 sul seme 1 (negativa = alzarlo aiuta): ' + ', '.join(
               '%s %s' % (p, '%+.2f' % c if c is not None else '—') for p, c in corr.items()) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e253_regolazione_congiunta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
