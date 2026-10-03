# -*- coding: utf-8 -*-
"""Esperimento e3a72: legame dell'e3a14/e3a65 con il nullo dentro (paragrafo, bordo), paragrafi veri contro paragrafi
finti della stessa grandezza (righe ruotate nella pagina).

Preregistrazione: preregistrazioni/e3a72.md. Scrive risultati/e3a72_paragrafi_finti.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
VOLTE = 20


def eventi(gruppi):
    """gruppi: [(id, [righe])]."""
    av, ind = [], []
    for g, righe in gruppi:
        for r in righe:
            for a, b in zip(r, r[1:]):
                av.append(((g, a[-1]), a, b[0]))
                ind.append(((g, b[0]), b, a[-1]))
    return av, ind


def main():
    rnd = random.Random(3172)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pagine.append((pg, pp))
    veri = [((pg, i), par) for pg, pp in pagine for i, par in enumerate(pp)]
    av, ind = eventi(veri)
    ris = OrderedDict([('veri', OrderedDict([('avanti', e380.prova(av, rnd, 200)), ('indietro', e380.prova(ind, rnd, 200))]))])
    print('veri', json.dumps(ris['veri'], default=float), flush=True)
    finti = []
    for v in range(VOLTE):
        gruppi = []
        for pg, pp in pagine:
            righe = [r for par in pp for r in par]
            lung = [len(par) for par in pp]
            n = len(righe)
            k = rnd.randrange(1, n) if len(pp) > 1 and n > 1 else 0
            rr = righe[k:] + righe[:k]
            i = 0
            for j, L in enumerate(lung):
                gruppi.append(((pg, 'f', j), rr[i:i + L]))
                i += L
        a2, i2 = eventi(gruppi)
        finti.append(OrderedDict([('avanti', e380.prova(a2, rnd, 100)), ('indietro', e380.prova(i2, rnd, 100))]))
        print('finti', v, finti[-1]['avanti']['E'], finti[-1]['indietro']['E'], flush=True)
    ris['finti'] = finti
    esiti = OrderedDict()
    for lato in ('avanti', 'indietro'):
        ev = ris['veri'][lato]['E']
        ef = [f[lato]['E'] for f in finti]
        if ev < min(ef):
            es = 'il paragrafo conta davvero'
        elif ev <= max(ef):
            es = 'calo in gran parte meccanico'
        else:
            es = 'incerto'
        esiti[lato] = OrderedDict([('veri', ev), ('finti_min', min(ef)), ('finti_media', sum(ef) / len(ef)), ('finti_max', max(ef)), ('esito', es)])
    ris['esiti'] = esiti
    print(json.dumps(esiti, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a72_paragrafi_finti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a72 — Il calo del legame col nullo del paragrafo è vero o meccanico?', '', 'Preregistrazione: `preregistrazioni/e3a72.md`. Riferimento e3a65: nullo (pagina, bordo) 0,0271 avanti, 0,0167 indietro.', '',
          '| direzione | paragrafi veri | paragrafi finti: min – max (media) | esito |', '|---|---|---|---|']
    md += ['| %s | %.4f | %.4f – %.4f (%.4f) | %s |' % (lato, x['veri'], x['finti_min'], x['finti_max'], x['finti_media'], x['esito']) for lato, x in esiti.items()]
    open(os.path.join(RISULTATI, 'e3a72_paragrafi_finti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
