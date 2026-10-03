# -*- coding: utf-8 -*-
"""Esperimento 289: secondo giro della regolazione congiunta, attorno alla scelta dell'e253, con i quattro meccanismi della
v2 (beta, eps, vsim, sigma dentro la scelta) di voynichizzatore/corpo2.genera_v2. Stampa ogni risultato appena arriva.

Preregistrazione: preregistrazioni/e289.md. Scrive risultati/e289_giro_due.json e .md e risultati/e289_parametri_scelti.json.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import corpo2
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e253_regolazione_congiunta as e253
import e266_discriminatore_forte as e266
import e268_prime_righe as e268

RISULTATI = os.path.join(QUI, '..', 'risultati')
CASUALI, AFFINAMENTO, SEME_RICERCA, SEMI_VERIFICA = 64, 32, 1, (7, 8, 9)
NUOVI = OrderedDict([('beta', (0.0, 2.0)), ('eps', (1.0, 4.0)), ('vsim', (0.0, 2.0)), ('sigma_in', (0.0, 0.1))])
CONTINUI = OrderedDict(list(e253.CONTINUI.items()) + list(NUOVI.items()))
CONTINUI['sigma_post'] = (0.0, 0.15)
DISCRETI = e253.DISCRETI
SPENTI = OrderedDict([('beta', 0.0), ('eps', 1.0), ('vsim', 0.0), ('sigma_in', 0.0)])


def centro():
    p = os.path.join(RISULTATI, 'e253_parametri_scelti.json')
    x = OrderedDict(json.load(open(p, encoding='utf-8'))) if os.path.exists(p) else OrderedDict(e253.E241)
    x.update(SPENTI)
    return x


def prm_di(x):
    p = e253.prm_di(x)
    p.update(beta=x['beta'], eps=x['eps'], vsim=x['vsim'], sigma=x['sigma_in'])
    return p


def lavoro(args):
    nome, x, seme, completa = args
    k = e251._prepara()
    e233.SIGMA_POST, e233.PI_POST = x['sigma_post'], x['pi_post']
    grezzo = corpo2.genera_v2(k['c2'], prm_di(x), seme, inter=e253.interruttori() if x['inter'] else None,
                              prime_per_pag=e268.prime_per_pagina(k['c']) if x['rho'] else None)
    rr = e236.dopo(grezzo, k['freq'], 100 + seme)
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


def vicino(x, rnd, quota, p_discreti, nuovi_uniformi):
    y = OrderedDict()
    for p, (a, b) in CONTINUI.items():
        if nuovi_uniformi and (p in NUOVI or p == 'sigma_post'):
            y[p] = rnd.uniform(a, b)
        else:
            y[p] = min(b, max(a, x[p] + rnd.uniform(-quota, quota) * (b - a)))
    for p, vals in DISCRETI.items():
        y[p] = rnd.choice(vals) if rnd.random() < p_discreti else x[p]
    return y


def main():
    c0 = centro()
    rnd = random.Random('e289')
    ris = tutti([('centro', c0, SEME_RICERCA, False)] + [('c%03d' % i, vicino(c0, rnd, 0.10, 0.1, True), SEME_RICERCA, False) for i in range(1, CASUALI + 1)])
    base1 = ris[0]
    ammessa = lambda r: r['pagella'] >= base1['pagella'] and r['riga']
    migliore = min([r for r in ris if ammessa(r)] or [base1], key=lambda r: (r['AUC_e266'], r['nome']))
    rnd2 = random.Random('e289-affinamento')
    aff = tutti([('a%03d' % i, vicino(migliore['parametri'], rnd2, 0.15, 0.2, False), SEME_RICERCA, False) for i in range(1, AFFINAMENTO + 1)])
    tutte = ris + aff
    scelta = min([r for r in tutte if ammessa(r)] or [base1], key=lambda r: (r['AUC_e266'], r['nome']))
    print('scelta %s: AUC e266 %.3f (centro %.3f) | %s' % (scelta['nome'], scelta['AUC_e266'], base1['AUC_e266'], dict(scelta['parametri'])), flush=True)
    json.dump(scelta['parametri'], open(os.path.join(RISULTATI, 'e289_parametri_scelti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    e241 = OrderedDict(e253.E241)
    e241.update(SPENTI)
    ver = tutti([(n, x, s, True) for s in SEMI_VERIFICA for n, x in (('e241', e241), ('centro', c0), (scelta['nome'], scelta['parametri']))])
    bracci = OrderedDict([('e241', [v for v in ver if v['nome'] == 'e241']), ('centro', [v for v in ver if v['nome'] == 'centro']),
                          ('scelta', [v for v in ver if v['nome'] not in ('e241', 'centro')])])
    m = lambda vv, kk: statistics.mean(v[kk] for v in vv)
    medie = OrderedDict((n, OrderedDict([('pagella_somma', sum(v['pagella'] for v in vv)), ('semi_con_riga', sum(bool(v['riga']) for v in vv)),
                                         ('AUC_e231_media', m(vv, 'AUC_e231')), ('AUC_e266_media', m(vv, 'AUC_e266')),
                                         ('mancano', dict(Counter(x for v in vv for x in v['mancano'])))])) for n, vv in bracci.items())
    mc, ms = medie['centro'], medie['scelta']
    migliore_v = ms['AUC_e266_media'] <= mc['AUC_e266_media'] - 0.02 and ms['pagella_somma'] >= mc['pagella_somma'] and ms['semi_con_riga'] >= mc['semi_con_riga']
    pieno = migliore_v and all(v['pagella'] == 18 and v['riga'] for v in bracci['scelta'])
    esito = '18/18' if pieno else ('migliore del giro 1' if migliore_v else 'non migliore')
    corr = OrderedDict()
    ys = [r['AUC_e266'] for r in tutte]
    for p in list(CONTINUI) + list(DISCRETI):
        xs = [float(r['parametri'][p]) for r in tutte]
        corr[p] = statistics.correlation(xs, ys) if len(set(xs)) > 1 else None
    out = OrderedDict([('centro', c0), ('seme_1', tutte), ('scelta', scelta['nome']), ('parametri_scelti', scelta['parametri']), ('verifica', ver),
                       ('medie', medie), ('correlazioni_AUC_e266', corr), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e289_giro_due.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e289 — Regolazione congiunta, secondo giro: i quattro meccanismi della v2', '',
          'Centro: la scelta dell\'e253. 64 configurazioni attorno al centro con β, ε, v e σ dentro la scelta, più 32 di affinamento, sul seme 1; verifica '
          'sui semi 7, 8, 9. Preregistrazione: `preregistrazioni/e289.md`.', '',
          'Centro sul seme 1: pagella %d, AUC e266 %.3f. Scelta **%s**: pagella %d, AUC e266 %.3f, e231 %.3f.' % (
              base1['pagella'], base1['AUC_e266'], scelta['nome'], scelta['pagella'], scelta['AUC_e266'], scelta['AUC_e231']), '',
          'Parametri scelti: ' + ', '.join('%s %s' % (p, ('%.3f' % v) if isinstance(v, float) else v) for p, v in scelta['parametri'].items()) + '.', '',
          '| seme | braccio | pagella | riga | mancano | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|']
    for v in ver:
        md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f |' % (v['seme'], v['nome'], v['pagella'], 'sì' if v['riga'] else 'no', ', '.join(v['mancano']) or '—', v['AUC_e231'], v['AUC_e266']))
    md += [''] + ['Medie %s: pagella %d, riga in %d semi, AUC %.3f / %.3f.' % (n, x['pagella_somma'], x['semi_con_riga'], x['AUC_e231_media'], x['AUC_e266_media'])
                  for n, x in medie.items()]
    md += ['', 'Correlazione fra parametro e AUC dell\'e266 sul seme 1: ' + ', '.join('%s %s' % (p, '%+.2f' % c if c is not None else '—') for p, c in corr.items()) + '.',
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e289_giro_due.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
