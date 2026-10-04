# -*- coding: utf-8 -*-
"""Esperimento e3b44: memoria delle scelte a cavallo dell'a capo nelle pagine "solo testo" contro gruppi di pagine
normali estratti a caso (prova per pagina), e per lunghezza del paragrafo.

Preregistrazione: preregistrazioni/e3b44.md. Scrive risultati/e3b44_a_capo_pagine.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b10_scelte_a_capo as e3b10

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRUPPI = 10000
BOOT = 2000
MIN_COPPIE = 10
CLASSI = (('2-4 righe', 2, 4), ('5-7 righe', 5, 7), ('8+ righe', 8, 10 ** 6))


def somme_pagina(pars, pid):
    """{(paragrafo, tipo): [somma eccessi, coppie]} di una pagina."""
    acc = defaultdict(lambda: [0.0, 0])
    for key, tipo, ok, att in e3b10.coppie_pagina(pars, pid):
        acc[(key[1], tipo)][0] += ok - att
        acc[(key[1], tipo)][1] += 1
    return acc


def cavallo(acc):
    s = sum(v[0] for (j, t), v in acc.items() if t == 'a cavallo')
    n = sum(v[1] for (j, t), v in acc.items() if t == 'a cavallo')
    return s, n


def prova_pagine(gruppo, pool, rnd):
    s = sum(x[0] for x in gruppo)
    n = sum(x[1] for x in gruppo)
    oss = s / n
    k = len(gruppo)
    ge = 0
    vals = []
    for _ in range(GRUPPI):
        g = rnd.sample(pool, k)
        v = sum(x[0] for x in g) / sum(x[1] for x in g)
        vals.append(v)
        ge += v >= oss
    vals.sort()
    return OrderedDict([('pagine', k), ('eccesso', oss), ('coppie', n), ('pool', len(pool)), ('p', ge / GRUPPI),
                        ('mediana_gruppi', vals[GRUPPI // 2]), ('q975_gruppi', vals[int(0.975 * GRUPPI)])])


def esito1(p):
    return 'regge a livello di pagina' if p < 0.025 else ('non regge a livello di pagina' if p > 0.10 else 'debole')


def main():
    rnd = random.Random(3244)
    sezione, mano = {}, {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
        mano.setdefault(r.pagina, r.mano)
    somme, lung = OrderedDict(), {}
    for pid, (pg, pars) in enumerate(e341.pagine().items()):
        pp = [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if not pp:
            continue
        somme[pg] = somme_pagina(pp, pid)
        for j, par in enumerate(pp):
            lung[(pg, j)] = len(par)
    t = [pg for pg in somme if sezione.get(pg) == 'T']
    per_pag = {pg: cavallo(a) for pg, a in somme.items()}
    pool = [per_pag[pg] for pg in somme if sezione.get(pg) != 'T' and per_pag[pg][1] >= MIN_COPPIE]
    m1 = prova_pagine([per_pag[pg] for pg in t], pool, rnd)
    t2 = [pg for pg in t if mano.get(pg) == '2']
    pool2 = [per_pag[pg] for pg in somme if sezione.get(pg) != 'T' and mano.get(pg) == '2' and per_pag[pg][1] >= MIN_COPPIE]
    m1b = prova_pagine([per_pag[pg] for pg in t2], pool2, rnd)
    print('T', json.dumps(m1), flush=True)
    print('mano 2', json.dumps(m1b), flush=True)
    m2 = OrderedDict()
    for gruppo, cond in (('altre pagine', lambda pg: sezione.get(pg) != 'T'), ('solo testo (T)', lambda pg: sezione.get(pg) == 'T')):
        for nome, lo, hi in CLASSI:
            pars = [(pg, j, v) for pg, a in somme.items() if cond(pg) for (j, tp), v in a.items()
                    if tp == 'a cavallo' and lo <= lung[(pg, j)] <= hi]
            if not pars:
                continue
            s, n = sum(v[0] for _, _, v in pars), sum(v[1] for _, _, v in pars)
            boot = []
            for _ in range(BOOT):
                bb = [pars[rnd.randrange(len(pars))] for _ in pars]
                nb = sum(v[1] for _, _, v in bb)
                boot.append(sum(v[0] for _, _, v in bb) / nb)
            boot.sort()
            m2['%s, %s' % (gruppo, nome)] = OrderedDict([('paragrafi', len(pars)), ('coppie', n), ('eccesso', s / n),
                                                          ('IC95', [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]])])
            print(gruppo, nome, json.dumps(m2['%s, %s' % (gruppo, nome)]), flush=True)
    lunghi = m2['altre pagine, 8+ righe']
    es2 = 'conta anche la lunghezza' if lunghi['IC95'][0] > 0 else 'non è la lunghezza dei paragrafi'
    out = OrderedDict([('prova_pagine_T', m1), ('esito_1_T', esito1(m1['p'])), ('prova_pagine_mano2', m1b),
                       ('esito_1_mano2', esito1(m1b['p'])), ('per_lunghezza', m2), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b44_a_capo_pagine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b44 — La memoria che passa l\'a capo: prova per pagina e lunghezza dei paragrafi', '', 'Preregistrazione: `preregistrazioni/e3b44.md`.', '',
          '## Prova per pagina', '', '| gruppo | pagine | eccesso a cavallo (coppie) | gruppi a caso: mediana, 97,5° | pagine nel serbatoio | p |', '|---|---|---|---|---|---|']
    for k, x in (('6 pagine T contro pagine non T', m1), ('4 pagine T della mano 2 contro pagine non T della mano 2', m1b)):
        md.append('| %s | %d | %+.4f (%d) | %+.4f, %+.4f | %d | %.4f |' % (k, x['pagine'], x['eccesso'], x['coppie'], x['mediana_gruppi'], x['q975_gruppi'], x['pool'], x['p']))
    md += ['', 'Esito 1: T **%s**; mano 2 **%s**.' % (esito1(m1['p']), esito1(m1b['p'])), '', '## Lunghezza del paragrafo', '',
           '| gruppo | paragrafi | coppie a cavallo | eccesso (IC 95%) |', '|---|---|---|---|']
    md += ['| %s | %d | %d | %+.4f (%+.4f – %+.4f) |' % (k, x['paragrafi'], x['coppie'], x['eccesso'], x['IC95'][0], x['IC95'][1]) for k, x in m2.items()]
    md += ['', 'Esito 2: **%s**.' % es2]
    open(os.path.join(RISULTATI, 'e3b44_a_capo_pagine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
