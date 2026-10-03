# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 1 sulla v2: correzioni aggiunte una alla volta (cumulative) al corpo della v2, valutate sui semi
di ricerca 1 e 2 (mai su quelli di verifica): pagella, riga, AUC dell'e231 e dell'e266 con i gruppi che contano.

    python voynichizzatore/prova_v3.py          (PROCESSI dalla variabile d'ambiente)
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))

SEMI = (1, 2)
BASE = OrderedDict([('alfa', 1.0), ('kappa', 1.0), ('chi', 0.2), ('nu', 0.4), ('lam', 1.0), ('eta', 1.0), ('gamma', 0.0), ('delta', 0.0), ('psi', 0.0),
                    ('sigma_post', 0.04), ('pi_post', 0.30), ('phi', 0.10), ('theta', 0.3), ('rho', 0.0), ('rip', 0.5),
                    ('k', 8), ('k_tema', 3), ('mazzo', False), ('inter', False), ('beta', 0.0), ('eps', 1.0), ('vsim', 0.0), ('sigma_in', 0.0)])
PASSI = [('v2 (corpo e288)', {}), ('+ niente tema (θ 0)', {'theta': 0.0}), ('+ basi dal Voynich intero (δ 0,2)', {'delta': 0.2}),
         ('+ prime righe (ρ 0,25)', {'rho': 0.25}), ('+ lunghezza stabile (β 1)', {'beta': 1.0}), ('+ pezzi di riga copiati (ψ 0,03)', {'psi': 0.03}),
         ('+ penalità ripetizioni 0,4', {'rip': 0.4})]


def configurazioni():
    out, x = [], OrderedDict(BASE)
    for nome, d in PASSI:
        x = OrderedDict(x)
        x.update(d)
        out.append((nome, x))
    return out


def lavoro(args):
    nome, x, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    import e253_regolazione_congiunta as e253
    import e266_discriminatore_forte as e266
    import e268_prime_righe as e268
    import corpo2
    k = e251._prepara()
    prm = e253.prm_di(x)
    prm.update(beta=x['beta'], eps=x['eps'], vsim=x['vsim'], sigma=x['sigma_in'])
    e233.SIGMA_POST, e233.PI_POST = x['sigma_post'], x['pi_post']
    rr = e236.dopo(corpo2.genera_v2(k['c2'], prm, seme, inter=None, prime_per_pag=e268.prime_per_pagina(k['c']) if x['rho'] else None), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(k['c'], rr)
    d231 = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    return args, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('AUC_e231', d231['AUC']),
                              ('AUC_e266', d266['AUC']), ('gruppi_e266', d266['AUC_per_gruppo'])])


def main():
    confs = configurazioni()
    lavori = [(n, x, s) for n, x in confs for s in SEMI]
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for (n, x, s), r in pool.imap_unordered(lavoro, lavori):
            ris[(n, s)] = r
            print('%-36s seme %d: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f | G3 %.3f G6 %.3f G8 %.3f G9 %.3f' % (
                n, s, r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'], r['gruppi_e266']['G3'], r['gruppi_e266']['G6'],
                r['gruppi_e266']['G8'], r['gruppi_e266']['G9']), flush=True)
    print('\nMEDIE SUI SEMI 1 E 2')
    out = OrderedDict()
    for n, x in confs:
        rs = [ris[(n, s)] for s in SEMI]
        out[n] = OrderedDict([('parametri', x), ('pagella_somma', sum(r['pagella'] for r in rs)), ('righe', sum(bool(r['riga']) for r in rs)),
                              ('AUC_e231', statistics.mean(r['AUC_e231'] for r in rs)), ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs)),
                              ('per_seme', rs)])
        print('%-36s pagella %2d (2 semi) riga %d | AUC e231 %.3f e266 %.3f' % (n, out[n]['pagella_somma'], out[n]['righe'], out[n]['AUC_e231'], out[n]['AUC_e266']))
    json.dump(out, open(os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'prova_v3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
