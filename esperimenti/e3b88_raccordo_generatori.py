# -*- coding: utf-8 -*-
"""Esperimento e3b88: forza del raccordo qo/o (metodo dell'e3b58) nei generatori pubblicati.

Preregistrazione: preregistrazioni/e3b88.md. Scrive risultati/e3b88_raccordo_generatori.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3b54_memoria_oltre_parole as e3b54
import e3b58_raccordo_scriba as e3b58
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
VOYNICH = 0.058


def main():
    rng = np.random.default_rng(3288)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            testi[k] = [r for r in ([w for w in (tuple(e3b62.D(x)) for x in ps) if w] for _, ps in v) if r]
    testi['Timm e Schinner, seme 1'] = [r for r in ([tuple(e3b62.D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r]
    ris, es = OrderedDict(), OrderedDict()
    for nome, righe in testi.items():
        uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
        ev = e3b58.eventi(uu, e3b54.v_qo)
        if len(ev[0]) < 50 or len(set(ev[0].tolist())) < 2:
            ris[nome] = OrderedDict([('occorrenze', int(len(ev[0])))])
            es[nome] = 'dati insufficienti'
            continue
        x = e3b58.prova(*ev, rng)
        ris[nome] = x
        r = x['effetto_su_entropia']
        if x['p'] < 0.01:
            es[nome] = 'raccordo come il Voynich' if r >= VOYNICH / 2 else 'raccordo debole'
        elif x['p'] > 0.05:
            es[nome] = 'nessun raccordo'
        else:
            es[nome] = 'incerto'
        print(nome, es[nome], json.dumps(x), flush=True)
    out = OrderedDict([('generatori', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b88_raccordo_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b88 — Quanto è forte il raccordo qo/o nei generatori?', '', 'Preregistrazione: `preregistrazioni/e3b88.md`. Voynich ZL (e3b58): effetto/entropia 0,058; scriba anglosassone 0,007.', '',
          '| generatore | occorrenze | quota qo | MI osservata | MI nullo | effetto | effetto / entropia | p | esito |', '|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if 'MI' not in x:
            md.append('| %s | %d | | | | | | | %s |' % (k, x['occorrenze'], es[k]))
            continue
        md.append('| %s | %d | %.3f | %.4f | %.4f | %+.4f | %+.3f | %.3f | %s |' % (k, x['occorrenze'], x['quota_1'], x['MI'], x['MI_nullo'], x['effetto'], x['effetto_su_entropia'], x['p'], es[k]))
    open(os.path.join(RISULTATI, 'e3b88_raccordo_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
