# -*- coding: utf-8 -*-
"""Esperimento e3b83: memoria delle scelte nei testi in cerchio e nei raggi (ZL) con il metodo finale (e3b62 + e3b70).

Preregistrazione: preregistrazioni/e3b83.md. Scrive risultati/e3b83_memoria_cerchi_finale.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rng = np.random.default_rng(3283)
    per, mano = OrderedDict(), {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
        if r.tipo[0] in (trascrizione.CERCHIO, trascrizione.RAGGIO):
            ws = [w for w in (tuple(e3b62.D(x)) for x in r.parole if trascrizione.pulita(x)) if w]
            if ws:
                per.setdefault(r.pagina, []).append(ws)
    uu = list(per.values())
    ss = [mano.get(pg) or '?' for pg in per]
    classi = OrderedDict((k, e3b62.prepara(uu, ss, f)) for k, f in e3b62.CV.items())
    pr = e3b62.prova(classi, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in classi.values()], pr['nullo'], rng)
    ic = iv['IC95']
    esito = 'memoria anche nei cerchi' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'non dimostrata nei cerchi')
    out = OrderedDict([('pagine', len(uu)), ('righe', sum(len(x) for x in uu)), ('coppie_vicine', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']),
                       ('effetto', iv['effetto']), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b83_memoria_cerchi_finale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b83 — Memoria delle scelte nei testi in cerchio e nei raggi, con il metodo finale', '', 'Preregistrazione: `preregistrazioni/e3b83.md`. e3b37 (misura grezza): +0,041. Paragrafi (e3b70): +0,086.', '',
          '| pagine | righe | coppie vicine | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|',
          '| %d | %d | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (out['pagine'], out['righe'], out['coppie_vicine'], out['M'], out['nullo'], out['effetto'], ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b83_memoria_cerchi_finale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
