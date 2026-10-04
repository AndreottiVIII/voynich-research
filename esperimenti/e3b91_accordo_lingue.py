# -*- coding: utf-8 -*-
"""Esperimento e3b91: misura finale della memoria (e3b62 + e3b70) sulle desinenze -o/-a (italiano, spagnolo) e -us/-a
(latino) di testi veri, per vedere se l'accordo grammaticale sembra memoria corta.

Preregistrazione: preregistrazioni/e3b91.md. Scrive risultati/e3b91_accordo_lingue.json e .md.
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
VOYNICH = 0.086
TESTI = OrderedDict([
    ('italiano NT (Diodati)', ('Historical - Italian - Literary - NT - Diodati.txt', 'romanzo')),
    ('italiano, Della Pittura', ('Historical - Italian - Technical - Della Pittura.txt', 'romanzo')),
    ('spagnolo NT', ('Historical - Spanish - Literary - NT - Sagradas Escrituras.txt', 'romanzo')),
    ('latino NT (Vulgata)', ('Historical - Latin - Literary - NT (Vulgate).txt', 'latino')),
    ('latino, Plinio', ("Historical - Latin - Technical - Pliny's Natural History.txt", 'latino')),
])


def oa(w):
    if len(w) >= 3 and w[-1] in ('o', 'a'):
        return (1 if w[-1] == 'a' else 0, w[:-1] + ('*',))
    return None


def usa(w):
    if len(w) >= 4 and w[-2:] == ('u', 's'):
        return (0, w[:-2] + ('*',))
    if len(w) >= 3 and w[-1] == 'a':
        return (1, w[:-1] + ('*',))
    return None


def main():
    rng = np.random.default_rng(3291)
    tt = e381.testi()
    ris, es = OrderedDict(), OrderedDict()
    for nome, (chiave, tipo) in TESTI.items():
        righe = [r for r in tt[chiave] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        f = oa if tipo == 'romanzo' else usa
        c = e3b62.prepara(uu, [nome] * len(uu), f)
        pr = e3b62.prova(OrderedDict([('x', c)]), rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
        ris[nome] = OrderedDict([('blocchi', len(uu)), ('occorrenze', int(len(c['val']))), ('quota_1', float(c['val'].mean())), ('coppie_vicine', pr['coppie_vicine']),
                                 ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95']), ('rapporto_Voynich', iv['effetto'] / VOYNICH)])
        ic = iv['IC95']
        es[nome] = "l'accordo sembra memoria" if ic[0] > 0 else 'no'
        print(nome, es[nome], json.dumps(ris[nome], ensure_ascii=False), flush=True)
    out = OrderedDict([('testi', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b91_accordo_lingue.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b91 — L\'accordo grammaticale delle lingue sembra "memoria corta" con la stessa misura?', '', 'Preregistrazione: `preregistrazioni/e3b91.md`. Voynich ZL (e3b70): +0,086 (IC +0,060 – +0,113).', '',
          '| testo | occorrenze | quota -a | coppie vicine | M | M nullo | effetto (IC 95%) | rispetto al Voynich | esito |', '|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.2f | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) | %.2f | %s |' % (k, x['occorrenze'], x['quota_1'], x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1], x['rapporto_Voynich'], es[k]))
    open(os.path.join(RISULTATI, 'e3b91_accordo_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
