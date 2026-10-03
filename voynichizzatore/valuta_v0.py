# -*- coding: utf-8 -*-
"""Valutazione descrittiva del voynichizzatore v0: pagella e discriminatori del manoscritto con il messaggio, contro lo
stesso corpo senza messaggio (stessa chiave, quindi stesso seme del generatore).

    python voynichizzatore/valuta_v0.py manoscritto.txt --chiave PAROLA
"""
import argparse, json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import v0
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266


def misura(k, rr):
    pg = e251.pagella_grezza(k['c'], rr)
    return OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                        ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                        ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manoscritto')
    ap.add_argument('--chiave', required=True)
    a = ap.parse_args()
    k = e251._prepara()
    ris = OrderedDict([('senza messaggio', misura(k, v0.corpo(a.chiave))), ('con il messaggio (v0)', misura(k, v0.carica(a.manoscritto)))])
    for n, r in ris.items():
        print('%-24s pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f' % (n, r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266']), flush=True)
    json.dump(ris, open(os.path.splitext(a.manoscritto)[0] + '_valutazione.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
