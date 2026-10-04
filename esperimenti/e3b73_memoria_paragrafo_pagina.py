# -*- coding: utf-8 -*-
"""Esperimento e3b73: la memoria delle scelte passa la fine del paragrafo e il cambio di pagina? Metodo dell'e3b66
(continuazione contro inizi vicini che non sono la continuazione).

Preregistrazione: preregistrazioni/e3b73.md. Scrive risultati/e3b73_memoria_paragrafo_pagina.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e395_takahashi as e395
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b66_a_capo_potenza as e3b66

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def strutture(righe):
    """{pagina: [paragrafi: [righe (ws, seps)]]} nell'ordine."""
    out = OrderedDict()
    for pg, npar, ws, seps in righe:
        pars = out.setdefault(pg, OrderedDict())
        pars.setdefault(npar, []).append((ws, seps))
    return OrderedDict((pg, list(p.values())) for pg, p in out.items())


def ultimo(riga):
    return e3b64.tratti(*riga)[-1]


def primo(riga):
    return e3b64.tratti(*riga)[0]


def casi_paragrafo(st):
    out = defaultdict(list)
    for pg, pars in st.items():
        for p in range(len(pars) - 1):
            altri = OrderedDict([('sotto', primo(pars[p + 1][0])),
                                 ('c1', primo(pars[p - 1][0]) if p > 0 else None),
                                 ('c2', primo(pars[p + 2][0]) if p + 2 < len(pars) else None)])
            out[pg].append((ultimo(pars[p][-1]), altri))
    return out


def casi_pagina(st):
    """Un 'caso' per cambio di pagina, con chiave = pagina di sinistra (unità del bootstrap)."""
    pagine = list(st)
    out = defaultdict(list)
    for k in range(len(pagine) - 1):
        a = st[pagine[k]]
        altri = OrderedDict([('sotto', primo(st[pagine[k + 1]][0][0])),
                             ('c1', primo(st[pagine[k - 1]][0][0]) if k > 0 else None),
                             ('c2', primo(st[pagine[k + 2]][0][0]) if k + 2 < len(pagine) else None)])
        out[pagine[k]].append((ultimo(a[-1][-1]), altri))
    return out


def analisi(casi, quote, rnd):
    sm = {k: e3b66.somme(casi, quote, k) for k in ('sotto', 'c1', 'c2')}
    unita = list(casi)

    def dd(pp):
        ks = {k: e3b64.kappa([sm[k][u] for u in pp])[0] for k in sm}
        if None in ks.values():
            return None
        return ks['sotto'] - (ks['c1'] + ks['c2']) / 2
    d = dd(unita)
    boot = sorted(x for x in (dd([rnd.choice(unita) for _ in unita]) for _ in range(BOOT)) if x is not None)
    ks = OrderedDict((k, OrderedDict([('K', e3b64.kappa([sm[k][u] for u in unita])[0]), ('coppie', int(sum(sm[k][u][2] for u in unita)))])) for k in sm)
    return OrderedDict([('unita', len(unita)), ('K', ks), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]] if boot else None)])


def main():
    rnd = random.Random(3273)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(q)]
        quote = e3b64.quote_pagine(righe, e3b62.CV)
        st = strutture(righe)
        ris['fine paragrafo, %s' % q] = analisi(casi_paragrafo(st), quote, rnd)
        ris['cambio di pagina, %s' % q] = analisi(casi_pagina(st), quote, rnd)
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    es = OrderedDict()
    for conf in ('fine paragrafo', 'cambio di pagina'):
        z, it = ris['%s, ZL' % conf], ris['%s, IT' % conf]
        es[conf] = 'la memoria passa il confine' if z['IC95'] and z['IC95'][0] > 0 and (it['D'] or 0) > 0 else 'non dimostrato'
    out = OrderedDict([('confini', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b73_memoria_paragrafo_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b73 — La memoria delle scelte passa la fine del paragrafo e il cambio di pagina?', '', 'Preregistrazione: `preregistrazioni/e3b73.md`. Metodo dell\'e3b66 (a capo: D +0,039 ZL, +0,041 IT).', '',
          '| confine | unità | K continuazione (coppie) | K controllo 1 (coppie) | K controllo 2 (coppie) | D (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        kk = x['K']
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) |' % (k, x['unita'], kk['sotto']['K'], kk['sotto']['coppie'], kk['c1']['K'], kk['c1']['coppie'], kk['c2']['K'], kk['c2']['coppie'],
                                                                                     x['D'], x['IC95'][0], x['IC95'][1]))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b73_memoria_paragrafo_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
