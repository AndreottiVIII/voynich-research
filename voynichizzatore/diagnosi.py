# -*- coding: utf-8 -*-
"""Ciclo avversario, passo di diagnosi: che cosa usano ancora i discriminatori dell'e231 e dell'e266 per riconoscere un
manoscritto prodotto dal voynichizzatore (AUC per gruppo e caratteristiche piu' pesanti, con i valori medi del Voynich e del
manoscritto).

    python voynichizzatore/diagnosi.py manoscritto.txt
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import v0


def main():
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    rr = v0.carica(sys.argv[1])
    d231 = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    out = OrderedDict([('e231', OrderedDict([('AUC', d231['AUC']), ('gruppi', d231['AUC_per_gruppo']), ('pesanti', d231['piu_pesanti'])])),
                       ('e266', OrderedDict([('AUC', d266['AUC']), ('gruppi', d266['AUC_per_gruppo']), ('pesanti', d266['piu_pesanti'])]))])
    for nome, d in out.items():
        print('== %s: AUC %.3f' % (nome, d['AUC']))
        print('   gruppi: ' + ', '.join('%s %.3f' % (g, v) for g, v in d['gruppi'].items() if v is not None))
        for n, cf, a, b in d['pesanti']:
            print('   %-40s coeff %+.2f  Voynich %.4f  manoscritto %.4f' % (n, cf, a, b))
    json.dump(out, open(os.path.splitext(sys.argv[1])[0] + '_diagnosi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
