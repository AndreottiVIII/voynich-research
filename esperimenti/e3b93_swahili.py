# -*- coding: utf-8 -*-
"""Esperimento e3b93: accordo di prefisso dello swahili (m-/wa-, ki-/vi-) con la misura finale della memoria (e3b62 +
e3b70) e con la misura del consumo con le lettere (e3b80).

Preregistrazione: preregistrazioni/e3b93.md. Scrive risultati/e3b93_swahili.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b80_memoria_lettere as e3b80

RISULTATI = os.path.join(QUI, '..', 'risultati')
CHIAVE = 'Modern - Swahili - Literary - NT.txt'
VOCALI = set('aeiou')


def classi(righe):
    c = Counter(w for r in righe for w in r)
    mw, kv = set(), set()
    for w in c:
        if len(w) >= 3 and w[0] == 'm' and w[1] not in VOCALI and (('w', 'a') + w[1:]) in c:
            mw.add(w[1:])
        if len(w) >= 4 and w[:2] == ('k', 'i') and (('v', 'i') + w[2:]) in c:
            kv.add(w[2:])

    def f_mw(w):
        if len(w) >= 3 and w[0] == 'm' and w[1:] in mw:
            return (0, w[1:])
        if len(w) >= 4 and w[:2] == ('w', 'a') and w[2:] in mw:
            return (1, w[2:])
        return None

    def f_kv(w):
        if len(w) >= 4 and w[:2] == ('k', 'i') and w[2:] in kv:
            return (0, w[2:])
        if len(w) >= 4 and w[:2] == ('v', 'i') and w[2:] in kv:
            return (1, w[2:])
        return None
    return OrderedDict([('m-/wa-', f_mw), ('ki-/vi-', f_kv)])


def main():
    rng = np.random.default_rng(3293)
    righe = [r for r in e381.testi()[CHIAVE] if r]
    uu = [[b] for b in e3b51.blocchi(righe)]
    ss = ['sw'] * len(uu)
    cl = classi(righe)
    ris = OrderedDict()
    for nome, prep in (('memoria', e3b62.prepara), ('consumo con le lettere', e3b80.prepara)):
        x = OrderedDict()
        for k, f in list(cl.items()) + [('insieme', None)]:
            if f is None:
                cc = OrderedDict((kk, prep(uu, ss, ff)) for kk, ff in cl.items())
            else:
                cc = OrderedDict([(k, prep(uu, ss, f))])
            pr = e3b62.prova(cc, rng)['insieme']
            iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
            x[k] = OrderedDict([('occorrenze', int(sum(len(c['val']) for c in cc.values()))), ('coppie', pr['coppie_vicine']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    m, l = ris['memoria']['insieme'], ris['consumo con le lettere']['insieme']
    es1 = "l'accordo di prefisso sembra memoria" if m['IC95'][0] > 0 else 'no'
    es2 = 'si consuma con le lettere anche lo swahili' if l['IC95'][0] > 0 else 'no'
    out = OrderedDict([('misure', ris), ('esito_memoria', es1), ('esito_lettere', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b93_swahili.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b93 — Lo swahili (accordo di prefisso) ha una "memoria" come qo/o, e si consuma con le lettere?', '', 'Preregistrazione: `preregistrazioni/e3b93.md`. Voynich: memoria qo/o +0,095, insieme +0,086 (e3b62, e3b70); consumo con le lettere +0,066 (e3b80).', '',
          '| misura | classe | occorrenze | coppie | effetto (IC 95%) |', '|---|---|---|---|---|']
    for nome, x in ris.items():
        for k, y in x.items():
            md.append('| %s | %s | %d | %d | %+.4f (%+.4f – %+.4f) |' % (nome, k, y['occorrenze'], y['coppie'], y['effetto'], y['IC95'][0], y['IC95'][1]))
    md += ['', 'Esito memoria: **%s**. Esito consumo con le lettere: **%s**.' % (es1, es2)]
    open(os.path.join(RISULTATI, 'e3b93_swahili.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
