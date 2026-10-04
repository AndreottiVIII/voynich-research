# -*- coding: utf-8 -*-
"""Esperimento e3b57: memoria delle scelte oltre le parole (metodo dell'e3b56) nei generatori pubblicati.

Preregistrazione: preregistrazioni/e3b57.md. Scrive risultati/e3b57_memoria_generatori.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3b54_memoria_oltre_parole as e3b54
import e3b56_memoria_oltre_parole_corretta as e3b56

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
VOYNICH_ZL = 0.0535
BLOCCO = 25


def unita(righe):
    return [righe[i:i + BLOCCO] for i in range(0, len(righe), BLOCCO)]


def main():
    rng = np.random.default_rng(3257)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            testi[k] = [r for r in ([w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v) if r]
    testi['Timm e Schinner, seme 1'] = [r for r in ([tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r]
    cv = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])
    ris, es = OrderedDict(), OrderedDict()
    for nome, righe in testi.items():
        uu = unita(righe)
        ris[nome] = e3b54.prova(OrderedDict((k, e3b56.prepara(uu, f)) for k, f in cv.items()), rng)
        x = ris[nome]['insieme']
        if x['M'] is None:
            es[nome] = 'n.d.'
        elif x['p'] < 0.01 and x['effetto'] >= VOYNICH_ZL / 2:
            es[nome] = 'memoria come il Voynich'
        elif x['p'] > 0.05:
            es[nome] = 'nessuna memoria'
        else:
            es[nome] = 'debole'
        print(nome, es[nome], json.dumps(ris[nome], ensure_ascii=False), flush=True)
    out = OrderedDict([('generatori', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b57_memoria_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b57 — I generatori hanno memoria delle scelte oltre le parole?', '', 'Preregistrazione: `preregistrazioni/e3b57.md`. Voynich (e3b56): ZL +0,054, IT +0,049.', '',
          '| generatore, classe | coppie vicine | M osservata | M nullo | effetto | z | p |', '|---|---|---|---|---|---|---|']
    for g, r in ris.items():
        for k, x in r.items():
            if x['M'] is None:
                md.append('| %s, %s | %d | n.d. | | | | |' % (g, k, x['coppie_vicine']))
                continue
            md.append('| %s, %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (g, k, x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['z'], x['p']))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b57_memoria_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
