# -*- coding: utf-8 -*-
"""Prova del modello del Voynich (modello.py) come corpo del voynichizzatore, sui semi di ricerca 1-4: pagella, pagella
estesa (e293), AUC dell'e231 e dell'e266 con i gruppi, quota di trigrammi di parole presi tali e quali dal Voynich
(controllo della copia). Riferimento: la v5 sugli stessi semi.

    PROCESSI=8 python voynichizzatore/prova_modello.py [nome]
"""
import json, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))

SEMI = (1, 2, 3, 4)
NOME = sys.argv[1] if len(sys.argv) > 1 else 'prova_modello'
CONF = [('v5', None), ('modello', {})]


def trigrammi(rr):
    return Counter(tuple(ws[i:i + 3]) for _, _, ws in rr for i in range(len(ws) - 2))


def lavoro(args):
    nome, forza, seme = args
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    import modello, versioni
    k = e251._prepara()
    rr = versioni.corpo(versioni.V5, seme) if forza is None else modello.genera(seme, forza=forza)
    pg = e251.pagella_grezza(k['c'], rr)
    est = e293.pagella_estesa(rr)
    t266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    voy3 = trigrammi(e293.voynich_rr())
    g3 = trigrammi(rr)
    copia = sum(n for t, n in g3.items() if t in voy3) / max(1, sum(g3.values()))
    return nome, seme, OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', est),
                                    ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                                    ('AUC_e266', t266['AUC']), ('gruppi_e266', t266['AUC_per_gruppo']), ('trigrammi_dal_Voynich', copia)])


def main():
    import e293_banco as e293
    voy = json.load(open(os.path.join(QUI, '..', 'risultati', 'e293_banco.json'), encoding='utf-8'))['Voynich']
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for n, s, r in pool.imap_unordered(lavoro, [(n, f, s) for n, f in CONF for s in SEMI]):
            r['estese_passate'] = [m for m in e293.FASCE if e293.passa(m, r['estesa'][m], voy)]
            ris[(n, s)] = r
            print('%-24s seme %d: pagella %d riga %s mancano %s | estese %d/8 %s | AUC e231 %.3f e266 %.3f %s | trigrammi copiati %.3f | %s' % (
                n, s, r['pagella'], r['riga'], r['mancano'], len(r['estese_passate']), r['estese_passate'], r['AUC_e231'], r['AUC_e266'],
                {g: round(v, 3) for g, v in r['gruppi_e266'].items() if v is not None}, r['trigrammi_dal_Voynich'],
                {m: round(v, 3) if isinstance(v, float) else v for m, v in r['estesa'].items()}), flush=True)
    print('\nMEDIE SUI SEMI %s' % (SEMI,))
    out = OrderedDict()
    for n, _ in CONF:
        rs = [ris[(n, s)] for s in SEMI]
        out[n] = OrderedDict([('pagella', sum(r['pagella'] for r in rs)), ('estese', sum(len(r['estese_passate']) for r in rs)),
                              ('righe', sum(bool(r['riga']) for r in rs)), ('AUC_e231', statistics.mean(r['AUC_e231'] for r in rs)),
                              ('AUC_e266', statistics.mean(r['AUC_e266'] for r in rs)), ('per_seme', rs)])
        print('%-24s pagella %2d + estese %2d = %3d/104 | riga %d | AUC e231 %.3f e266 %.3f' % (n, out[n]['pagella'], out[n]['estese'], out[n]['pagella'] + out[n]['estese'],
                                                                                          out[n]['righe'], out[n]['AUC_e231'], out[n]['AUC_e266']))
    json.dump(out, open(os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', NOME + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
