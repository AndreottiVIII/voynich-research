# -*- coding: utf-8 -*-
"""Ciclo avversario, verso la v4: meccanismi aggiunti uno alla volta (cumulativi) al corpo dell'e288, ciascuno mirato a una
materia della pagella estesa (e293) mancata. Semi di ricerca 1 e 2: pagella, pagella estesa, AUC. Corpo: corpo4.genera_v4
piu' gli errori sparsi dell'e297.

    PROCESSI=6 python voynichizzatore/prova_v4.py
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))

SEMI = (1, 2)
BASE = OrderedDict([('rip', 0.5), ('phi', 0.10), ('sigma_post', 0.04), ('errori', 0.0), ('beta', 0.0), ('eps', 1.0), ('omega', 0.0), ('rho', 0.0)])
PASSI = [('e288', {}), ('+ errori sparsi 0,02', {'errori': 0.02}), ('+ lunghezza stabile β 1', {'beta': 1.0}), ('+ rima delle desinenze ε 2', {'eps': 2.0}),
         ('+ successore già visto ω 0,1', {'omega': 0.1}), ('+ prime righe ρ 0,15', {'rho': 0.15}), ('variante: errori 0,04', {'errori': 0.04})]


def configurazioni():
    out, x = [], OrderedDict(BASE)
    for nome, d in PASSI:
        x = OrderedDict(x)
        x.update(d)
        out.append((nome, x))
    return out


def corpo(x, seme):
    import corpo4
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    import e268_prime_righe as e268
    import e297_errori_sparsi as e297
    k = e251._prepara()
    e233.SIGMA_POST = x['sigma_post']
    prm = dict(e251.CONF, gamma=0.0, rip=x['rip'], phi=x['phi'], beta=x['beta'], eps=x['eps'], omega=x['omega'], rho=x['rho'])
    rr = e236.dopo(corpo4.genera_v4(k['c2'], prm, seme, prime_per_pag=e268.prime_per_pagina(k['c']) if x['rho'] else None), k['freq'], 100 + seme)
    return e297.errori(k['c2'], rr, x['errori'], seme)


def lavoro(args):
    nome, x, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    rr = corpo(x, seme)
    pg = e251.pagella_grezza(k['c'], rr)
    est = e293.pagella_estesa(rr)
    return args[0], seme, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', est),
                                       ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                                       ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])


def main():
    import e293_banco as e293
    voy = json.load(open(os.path.join(QUI, '..', 'risultati', 'e293_banco.json'), encoding='utf-8'))['Voynich']
    confs = configurazioni()
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for n, s, r in pool.imap_unordered(lavoro, [(n, x, s) for n, x in confs for s in SEMI]):
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy)]
            ris[(n, s)] = r
            print('%-30s seme %d: pagella %d riga %s | estese %d/8 %s | AUC e231 %.3f e266 %.3f | %s' % (
                n, s, r['pagella'], r['riga'], len(r['estese_passate']), r['estese_passate'], r['AUC_e231'], r['AUC_e266'],
                {m: round(v, 3) if isinstance(v, float) else v for m, v in r['estesa'].items()}), flush=True)
    print('\nMEDIE SUI SEMI 1 E 2')
    out = OrderedDict()
    for n, x in confs:
        rs = [ris[(n, s)] for s in SEMI]
        out[n] = OrderedDict([('parametri', x), ('pagella', sum(r['pagella'] for r in rs)), ('estese', sum(len(r['estese_passate']) for r in rs)),
                              ('righe', sum(bool(r['riga']) for r in rs)), ('AUC_e231', statistics.mean(r['AUC_e231'] for r in rs)),
                              ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs)), ('per_seme', rs)])
        print('%-30s pagella %2d + estese %2d = %2d/52 | riga %d | AUC e231 %.3f e266 %.3f' % (n, out[n]['pagella'], out[n]['estese'], out[n]['pagella'] + out[n]['estese'],
                                                                                         out[n]['righe'], out[n]['AUC_e231'], out[n]['AUC_e266']))
    json.dump(out, open(os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'prova_v4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
