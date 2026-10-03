# -*- coding: utf-8 -*-
"""Ciclo avversario, giro 4, seconda prova: i cinque ritocchi della prova_v4 non migliorano l'e288; qui i due ritocchi
nuovi di corpo5 (scelte di grafia concordi nella riga, e206b; parole rare che girano fra le pagine, e296), da soli e
insieme, sopra il corpo dell'e288. Semi di ricerca 1 e 2: pagella, pagella estesa (e293), AUC.

    PROCESSI=8 python voynichizzatore/prova_v4b.py
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import versioni

SEMI = (1, 2)
BASE = versioni.E288
CONF = [('e288', {}), ('classi 0,4', {'classi': 0.4}), ('classi 0,7', {'classi': 0.7}), ('classi 1', {'classi': 1.0}),
        ('circola larga 1', {'circola': 1.0, 'chiave': 'larga'}), ('classi 0,4 + circola larga 1', {'classi': 0.4, 'circola': 1.0, 'chiave': 'larga'}),
        ('classi 0,7 + circola larga 1', {'classi': 0.7, 'circola': 1.0, 'chiave': 'larga'}),
        ('classi 0,7 + circola larga 1 + ω 0,3', {'classi': 0.7, 'circola': 1.0, 'chiave': 'larga', 'omega': 0.3})]
NOME = 'prova_v4b'


def configurazioni():
    out = []
    for n, d in CONF:
        x = OrderedDict(BASE)
        x.update(d)
        out.append((n, x))
    return out


def lavoro(args):
    nome, x, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()
    rr = versioni.corpo(x, seme)
    pg = e251.pagella_grezza(k['c'], rr)
    est = e293.pagella_estesa(rr)
    t266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    return nome, seme, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', est),
                                    ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                                    ('AUC_e266', t266['AUC']), ('gruppi_e266', t266['AUC_per_gruppo'])])


def main():
    import e293_banco as e293
    voy = json.load(open(os.path.join(QUI, '..', 'risultati', 'e293_banco.json'), encoding='utf-8'))['Voynich']
    confs = configurazioni()
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for n, s, r in pool.imap_unordered(lavoro, [(n, x, s) for n, x in confs for s in SEMI]):
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy)]
            ris[(n, s)] = r
            print('%-38s seme %d: pagella %d riga %s mancano %s | estese %d/8 %s | AUC e231 %.3f e266 %.3f %s | %s' % (
                n, s, r['pagella'], r['riga'], r['mancano'], len(r['estese_passate']), r['estese_passate'], r['AUC_e231'], r['AUC_e266'],
                {g: round(v, 3) for g, v in r['gruppi_e266'].items() if v is not None},
                {m: round(v, 3) if isinstance(v, float) else v for m, v in r['estesa'].items()}), flush=True)
    print('\nMEDIE SUI SEMI 1 E 2')
    out = OrderedDict()
    for n, x in confs:
        rs = [ris[(n, s)] for s in SEMI]
        out[n] = OrderedDict([('parametri', x), ('pagella', sum(r['pagella'] for r in rs)), ('estese', sum(len(r['estese_passate']) for r in rs)),
                              ('righe', sum(bool(r['riga']) for r in rs)), ('AUC_e231', statistics.mean(r['AUC_e231'] for r in rs)),
                              ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs)), ('per_seme', rs)])
        print('%-38s pagella %2d + estese %2d = %2d/52 | riga %d | AUC e231 %.3f e266 %.3f' % (n, out[n]['pagella'], out[n]['estese'], out[n]['pagella'] + out[n]['estese'],
                                                                                         out[n]['righe'], out[n]['AUC_e231'], out[n]['AUC_e266']))
    json.dump(out, open(os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', NOME + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
