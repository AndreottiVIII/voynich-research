# -*- coding: utf-8 -*-
"""Voynichizzatore, versione 3 (in costruzione, 3/10/2026): correzioni dal primo giro del ciclo avversario sulla v2.

- Canale: come la v1, ma nel modello delle scelte la scelta k/t conosce anche la posizione nella riga (nella v2 le righe
  iniziavano con k il doppio del Voynich e con t un terzo in meno). Modello in modello_scelte_v3.json.
- Corpo: parametri da `corpo2.genera_v2` (vedi CORPO_V3, scelti con prova_v3.py sui semi di ricerca 1 e 2).

    python voynichizzatore/v3.py addestra
    python voynichizzatore/v3.py codifica testo.txt --chiave PAROLA --uscita manoscritto.txt [--parametri file.json]
    python voynichizzatore/v3.py decodifica manoscritto.txt --chiave PAROLA [--uscita testo.txt]
    python voynichizzatore/v3.py valuta manoscritto.txt --chiave PAROLA [--parametri file.json]
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import v0, v1, v2

v1.MODELLO = os.path.join(QUI, 'modello_scelte_v3.json')
_posti_v1 = v1.posti_contesto


def posti_contesto_v3(w, pr):
    """Come nella v1; in piu' il contesto di k/t contiene la posizione nella riga."""
    out = []
    for t, v, ctx in _posti_v1(w, pr):
        if t == 'KT':
            ctx = '%s|%d' % (ctx, pr)
        out.append((t, v, ctx))
    return out


v1.posti_contesto = posti_contesto_v3
CORPO_V3 = None            # si fissa dopo prova_v3.py; finche' e' None si usa il corpo della v2


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'addestra':
        m = v1.addestra()
        print({t: (x['posti'], round(x['quota_lunghe'], 3)) for t, x in m.items()})
    else:
        if CORPO_V3 is not None and '--parametri' not in sys.argv:
            v2.CORPO_E288 = CORPO_V3
        v2.main()
