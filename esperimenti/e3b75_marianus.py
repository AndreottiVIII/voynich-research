# -*- coding: utf-8 -*-
"""Esperimento e3b75: memoria corta della scelta fra и e ꙇ a inizio parola nel Codex Marianus (metodo finale: nullo
largo dell'e3b62, intervallo per blocchi dell'e3b70).

Preregistrazione: preregistrazioni/e3b75.md. Scrive risultati/e3b75_marianus.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70

RISULTATI = os.path.join(QUI, '..', 'risultati')
CHIAVE = 'Historical - Russian - Literary - NT - Codex Marianus.txt'
UNO = {'ꙇ', 'ꙇ҅', 'ꙇ꙯', 'і'}
ZERO = {'и', 'и꙯', 'и҅'}
VOYNICH_BASSO = 0.060


def i_iniziale(w):
    if w and w[0] in UNO:
        return (1, ('*',) + w[1:])
    if w and w[0] in ZERO:
        return (0, ('*',) + w[1:])
    return None


def main():
    rng = np.random.default_rng(3275)
    righe = [r for r in e381.testi()[CHIAVE] if r]
    uu = [[b] for b in e3b51.blocchi(righe)]
    c = e3b62.prepara(uu, ['Marianus'] * len(uu), i_iniziale)
    pr = e3b62.prova(OrderedDict([('i iniziale', c)]), rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
    val = c['val']
    out = OrderedDict([('blocchi', len(uu)), ('occorrenze', int(len(val))), ('quota_ꙇ', float(val.mean())), ('coppie_vicine', pr['coppie_vicine']),
                       ('quota_rimescolabile', pr['quota_rimescolabile']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
    ic = iv['IC95']
    if ic[0] > 0:
        esito = 'memoria anche in questo scriba'
    else:
        esito = 'non si vede' + ('; meno del Voynich' if ic[1] < VOYNICH_BASSO else '')
    out['esito'] = esito
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b75_marianus.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b75 — Codex Marianus: la scelta fra и e ꙇ a inizio parola ha memoria corta?', '', 'Preregistrazione: `preregistrazioni/e3b75.md`. Voynich ZL (e3b70): +0,086 (IC +0,060 – +0,113).', '',
          '| blocchi | occorrenze | quota ꙇ | coppie vicine | quota rimescolabile | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|---|---|']
    md.append('| %d | %d | %.3f | %d | %.2f | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (out['blocchi'], out['occorrenze'], out['quota_ꙇ'], out['coppie_vicine'], out['quota_rimescolabile'] or 0, out['M'], out['nullo'], out['effetto'], ic[0], ic[1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b75_marianus.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
